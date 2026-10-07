"""A scripted player for offline end-to-end games (T076, T077): it drives `engine.game.Game` the way a person at
the CLI would, through the public API only, so `Game.replay` can re-drive every step.

    d = Driver.start(tmp_path / "g.db", seed=11)      # mixed seed (some answers in words), quick start, the opening
    d.play(60)                                         # varied acts; every pause answered; resumes at new pause kinds
    d.retire_and_continue()                            # "I retire" -> epilogue -> ending menu -> a new character
    d.game.close()

Acts rotate through looking, questions to the Oracle and about the scene, talk and speech, risky acts (climb, sneak,
an attack, forcing a door) whose OFFER is committed, changed or withdrawn, a skill the character lacks (a redirect),
travel to a reachable place, rests, codex reads, out-of-fiction questions and one dispute. Player choices come from a
seeded `random.Random`, so a run is reproducible.
"""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from engine.dm.response import Response
from engine.game import Game, GameConfig
from engine.llm.base import StructuredModel
from engine.llm.offline import OfflineModel
from engine.world.places import location, reachable

OFFLINE = GameConfig(offline=True)

LOOKS = ["I look around.", "I study the faces here.", "I look for anything out of place."]
QUESTIONS = ["Who is here?", "Is anyone here armed?", "Is there a back way out of here?", "Where am I?",
             "Is it about to rain?", "Does anyone here look afraid?"]
TALK = ["I ask them what is going on.", '"Did anyone see what happened?" I ask them.',
        "I greet whoever is here and ask about the trouble.", '"I am looking for work," I say.',
        "I ask about the dead who do not stay buried."]
RISKY = ["I climb the wall to get a better look.", "I sneak past the people here.", "I climb onto the roof.",
         "I jump across the gap between the stalls.", "I attack the nearest person with my sword."]
LACKING = ["I pick the lock of the nearest door.", "I read the old inscription on the stone."]
RESTS = ["I rest for the night.", "I take a short rest.", "I catch my breath."]
OOF = ["What are my options?", "What do I know?"]
CODEX = ["sheet", "journal", "threads", "abilities", "conditions", "rules 01.6.9"]
DISPUTE = "My Vitality is wrong: I was not hurt."


@dataclass
class Step:
    """One API call the player made and what came back (for assertions and timings)."""

    kind: str
    arg: str
    turn_id: str | None
    phase: str
    pause: str | None
    seconds: float
    fallback: bool = False
    fiction: str = ""


@dataclass
class Driver:
    path: Path
    game: Game
    model: StructuredModel
    rng: random.Random
    last: Response
    steps: list[Step] = field(default_factory=list)
    resumed: dict[str, int] = field(default_factory=dict)  # pause kind (and stage) -> resumes checked
    seen: dict[str, int] = field(default_factory=dict)  # pause kind (and stage) -> times reached
    turns: int = 0  # play submissions (acts, questions, talk)
    disputed: bool = False
    on_resume: Callable[[Response, Response], None] | None = None
    sizes: dict[str, list[tuple[int, int]]] = field(default_factory=dict)  # packet_sizes(), kept past close()

    # ------------------------------------------------------------------------------- set-up

    @classmethod
    def start(cls, path: Path, seed: int = 11, *, model: StructuredModel | None = None, name: str = "Bram, he/him",
              player_seed: int | None = None) -> Driver:
        model = model or OfflineModel()
        game, r = Game.new(path, OFFLINE, seed=seed, model=model)
        d = cls(path=path, game=game, model=model, rng=random.Random(player_seed or seed), last=r)
        d._note(r)
        d.seed_world()
        d.create(name)
        return d

    def seed_world(self) -> None:
        """Mixed: answer two questions in words (by number from the pick list), the oracle rolls the rest; keep
        every step but veto once."""
        r = self.call("submit", "3")
        vetoed = False
        while r.phase == "seed":
            p = r.pause
            ids_ = [c.id for c in p.choices] if p else []
            if p is not None and "keep" in ids_:
                veto = next((c for c in ids_ if c.startswith("veto")), None)
                if veto and not vetoed:
                    vetoed = True
                    r = self.call("answer", veto)
                else:
                    r = self.call("answer", "keep")
            elif p is not None and "all" in ids_:  # the mixed-mode list of questions to answer
                r = self.call("submit", "1, 3")
            elif p is not None and any(c.id == "own_words" for c in p.choices) or "describe your own" in r.text():
                r = self.call("submit", self.rng.choice(["the dead do not stay buried", "magic is rare and feared",
                                                         ""]))
            else:
                r = self.call("submit", "")

    def create(self, name: str) -> None:
        r = self.last
        answers = ["fights and mysteries please, nothing ruled out, quick start", "an old soldier tired of war",
                   "I want to find out who killed my brother", "my sister Ada, who raised me", name, "begin"]
        for msg in answers:
            if r.phase != "creation":
                break
            r = self.call("submit", msg)
        while r.phase == "creation":  # anything the quick start still asks: take the default
            r = self.call("submit", "")
        assert r.phase == "play", r.text()

    # ------------------------------------------------------------------------------- the API

    def call(self, kind: str, arg: str = "") -> Response:
        t = time.perf_counter()
        if kind == "submit":
            r = self.game.submit(arg)
        elif kind == "answer":
            r = self.game.answer(arg)
        elif kind == "dispute":
            r = self.game.dispute(arg)
        elif kind == "new_character":
            r = self.game.new_character()
        else:
            raise ValueError(kind)
        self.steps.append(Step(kind, arg, r.turn_id, r.phase, r.pause.kind if r.pause else None,
                               time.perf_counter() - t, r.flags.fallback_used, r.fiction))
        self.last = r
        self._note(r)
        return r

    def _key(self, r: Response) -> str | None:
        if r.pause is None:
            return None
        rec = self.game.store.state.open_pause()
        stage = (rec.detail.get("stage") or rec.detail.get("flow")) if rec is not None else None
        return f"{r.pause.kind}:{stage}" if stage and stage != r.pause.kind else r.pause.kind

    def _note(self, r: Response) -> None:
        key = self._key(r)
        if key is None:
            return
        self.seen[key] = self.seen.get(key, 0) + 1
        if key not in self.resumed:
            self.resume_check(r, key)

    def resume_check(self, r: Response, key: str) -> None:
        """Quit at this pause and come back: the same pause must be presented again."""
        self.resumed[key] = self.resumed.get(key, 0) + 1
        self.game.close()
        self.game, back = Game.open(self.path, OFFLINE, model=self.model)
        assert back.pause == r.pause, f"resume at {key}: {back.pause!r} != {r.pause!r}"
        if self.on_resume is not None:
            self.on_resume(r, back)
        self.last = back

    # ------------------------------------------------------------------------------- play

    def settle(self, r: Response) -> Response:
        """Answer every pause a step opened, the way a player would (mostly committing)."""
        for _ in range(8):
            p = r.pause
            if p is None or r.phase != "play":
                return r
            ids_ = [c.id for c in p.choices]
            key = self._key(r) or p.kind
            if key == "offer:warning" or "continue" in ids_:
                r = self.call("answer", "continue" if self.rng.random() < 0.7 else "withdraw")
            elif p.kind == "offer":
                roll = self.rng.random()
                pick = "commit" if roll < 0.7 else "change" if roll < 0.85 else "withdraw"
                r = self.call("answer", pick if pick in ids_ else ids_[0])
            elif p.kind == "near_miss":
                r = self.call("answer", self.rng.choice(ids_))
            elif p.kind == "redirect":
                r = self.call("answer", next((c for c in ids_ if c.startswith("accept:")), ids_[-1])
                              if self.rng.random() < 0.5 else ids_[-1])
            elif p.kind == "clarify" and "retire" in ids_:
                r = self.call("answer", "keep_playing")
            elif ids_:
                r = self.call("answer", ids_[0])
            else:
                r = self.call("submit", "yes")
        return r

    def act(self, i: int) -> Response:
        """One player turn, chosen by the turn number and a seeded draw."""
        roll = self.rng.random()
        if i % 25 == 7:
            return self.travel()
        if i % 40 == 19:
            return self.settle(self.call("submit", self.rng.choice(RESTS)))
        if i % 30 == 11:
            self.game.codex(self.rng.choice(CODEX))
        if not self.disputed and i >= 15 and self.last.pause is None:
            self.disputed = True
            return self.settle(self.call("dispute", DISPUTE))
        if roll < 0.12:
            msg = self.rng.choice(LOOKS)
        elif roll < 0.24:
            msg = self.rng.choice(QUESTIONS)
        elif roll < 0.48:
            msg = self.rng.choice(TALK)
        elif roll < 0.82:
            msg = self.rng.choice(RISKY)
        elif roll < 0.9:
            msg = self.rng.choice(LACKING)
        else:
            msg = self.rng.choice(OOF)
        return self.settle(self.call("submit", msg))

    def travel(self) -> Response:
        st = self.game.store.state
        here = location(st)
        dests = [x.to for x in reachable(st, here) if x.to != here and x.to in st.entities]
        if not dests:
            return self.settle(self.call("submit", "I head out on the road."))
        dest = self.rng.choice(dests)
        return self.settle(self.call("submit", f"I head to {st.entities[dest].name}."))

    def play(self, n: int) -> None:
        for _ in range(n):
            r = self.act(self.turns)
            self.turns += 1
            assert r.phase in ("play", "ending"), r.phase
            if r.phase == "ending":
                return

    # ------------------------------------------------------------------------------- endings

    def retire_and_continue(self, name: str = "Ash, he/him") -> None:
        """Retire by choice: the confirmation (resumed), the epilogue and ending menu (resumed), then a new
        character in the same world (its creation step resumed) and the new opening."""
        r = self.settle(self.last) if self.last.pause is not None and self.last.phase == "play" else self.last
        r = self.call("submit", "I retire.")
        assert r.pause is not None and [c.id for c in r.pause.choices] == ["retire", "keep_playing"], r.text()
        r = self.call("answer", "retire")
        assert r.phase == "ending" and r.pause is not None and r.pause.kind == "ending", r.text()
        r = self.call("new_character")
        assert r.phase == "creation"
        for msg in ("", "a wanderer who has seen too much", "", "", name, "begin"):
            if r.phase != "creation":
                break
            r = self.call("submit", msg)
        while r.phase == "creation":
            r = self.call("submit", "")
        assert r.phase == "play" and r.fiction, r.text()

    # ------------------------------------------------------------------------------- measurements

    def packet_sizes(self) -> dict[str, list[tuple[int, int]]]:
        """{role: [(turn number, rendered packet length)]} over the play turns, from the stored model calls."""
        out: dict[str, list[tuple[int, int]]] = {}
        for row in self.game.store.model_calls():
            tid = str(row.get("turn_id") or "")
            if not tid.startswith("turn."):
                continue
            packet = (row.get("request") or {}).get("packet") or ""
            out.setdefault(str(row["role"]), []).append((int(tid.split(".")[1]), len(packet)))
        return out


def trend(points: list[tuple[int, int]]) -> tuple[float, float, float]:
    """(mean of the first quarter, mean of the last quarter, least-squares slope per turn)."""
    pts = sorted(points)
    q = max(1, len(pts) // 4)
    first = sum(v for _, v in pts[:q]) / q
    last = sum(v for _, v in pts[-q:]) / q
    n = len(pts)
    mx = sum(x for x, _ in pts) / n
    my = sum(v for _, v in pts) / n
    var = sum((x - mx) ** 2 for x, _ in pts) or 1.0
    slope = sum((x - mx) * (v - my) for x, v in pts) / var
    return first, last, slope


__all__ = ["CODEX", "DISPUTE", "Driver", "OFFLINE", "Step", "trend"]
