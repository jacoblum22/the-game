"""Spec 026: small made-up games for the held-out `/fix` complaints (tests/fixtures/feedback_corpus/fresh.json).

    py -3.12 evals/fix_scenarios.py          # (re)writes tests/fixtures/feedback_corpus/fresh-*.db.gz

Each game is built from events through the engine's own pipeline (gate, necessity, frame with a fixed Framer
proposal, the OFFER pause and its block), with turn records holding what the player typed and what the screen
showed, so the Fixer reads them exactly as it reads a live save. Some states are deliberately wrong (a fare charged
twice, a reading taken as theft, a fact that should never have been a snag): those are the bugs the complaints report.
Deterministic: fixed seed, fixed dice faces.
"""

from __future__ import annotations

import gzip
import json
import shutil
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine import ids  # noqa: E402
from engine.data.loader import load_rules  # noqa: E402
from engine.llm.base import ModelCallRecord, Role  # noqa: E402
from engine.resolve import frame as frame_mod  # noqa: E402
from engine.resolve import pipeline  # noqa: E402
from engine.resolve.costs import first_fitting_cost  # noqa: E402
from engine.resolve.pipeline import BeatPlan, PipelineEnv, resume, run_beats  # noqa: E402
from engine.resolve.types import Beat, Change, Obstacle, ProposedFrame  # noqa: E402
from engine.rng import Rng  # noqa: E402
from engine.store.db import Store  # noqa: E402
from engine.store.events import EntityRecord, Event, LicenseInstance, Quantity, SceneRecord  # noqa: E402
from engine.store.records import TurnRecord  # noqa: E402
from engine.time.scheduler import TimeContext, set_mode  # noqa: E402

RULES = load_rules()
OUT = ROOT / "tests" / "fixtures" / "feedback_corpus"
ATTR = {"verb.talk": "presence", "verb.sneak": "agility", "verb.observe": "wits"}


class Dice(Rng):
    """The game's RNG with fixed faces for roll checks (everything else seeded)."""

    faces: list[int]

    def draw(self, n: int, purpose: str, *, stream: str = "dice", table_id: str | None = None) -> int:
        if purpose.startswith("roll_check") and getattr(self, "faces", None):
            face = self.faces.pop(0)
            if self.log is not None:
                self.log.record_rng_draw(stream, purpose, face, sides=n, table_id=table_id)
            return face
        return super().draw(n, purpose, stream=stream, table_id=table_id)


class Game:
    def __init__(self, path: Path, seed: int) -> None:
        self.store = Store.create(path, seed=seed, milestone=1, config={"fixture": "spec026"}, rules_hash="fixture")
        rng = Dice.for_store(self.store)
        assert isinstance(rng, Dice)
        rng.faces = []
        self.rng = rng
        self.n = 0
        self.pc = ""
        self.place = ""

    def ent(self, tx: Any, kind: str, name: str, data: dict[str, Any], *, licences: tuple[str, ...] = (),
            quantities: dict[str, tuple[int, int, int]] | None = None, sealed: dict[str, Any] | None = None) -> str:
        eid = ids.entity_id(kind, name, tx.state.entities)
        rec = EntityRecord(id=eid, kind=kind, name=name, data={**data, **(sealed or {})},  # type: ignore[arg-type]
                           sealed_fields=sorted(sealed or {}))
        qs = {k: Quantity(current=c, min=lo, max=hi) for k, (c, lo, hi) in (quantities or {}).items()}
        tx.add(Event.of("entity_created", source="seed", rule_id="12.11.1", entity=rec, quantities=qs,
                        licenses=[LicenseInstance(license_id=x, grade="native" if x == "lic.lang.common" else
                                                  "trained") for x in licences]))
        if kind in ("pc", "npc") and self.place:
            tx.add(Event.of("position_set", source="seed", rule_id="10.1.1", entity=eid, location=self.place))
        return eid

    @staticmethod
    def fact(tx: Any, subject: str, predicate: str, value: Any, source: str = "generation") -> str:
        fid = tx.mint(ids.FACT)
        tx.add(Event.of("fact_set", {"source": source}, source="engine", rule_id="00.6.6", fact_id=fid, subject=subject,
                        predicate=predicate, value=value, visibility="shown"))
        return fid

    def open_scene(self, tx: Any, cast: list[str], agenda: str) -> None:
        sid = tx.mint(ids.SCENE)
        tx.add(Event.of("scene_started", source="engine", rule_id="PR-12-7", scene_id=sid,
                        scene=SceneRecord(scene_id=sid, place_id=self.place, mode="free", agenda=agenda,
                                          cast_present=cast, started_seq=tx.state.last_seq)))
        set_mode(TimeContext(tx, RULES, self.rng), "free", "the scene opens")

    def turn(self, said: str, shown: str, build: Callable[[Any], Any] | None = None,
             calls: list[tuple[Role, str, dict[str, Any]]] = ()) -> Any:
        """One turn: `build(tx)` writes its events; the record keeps the words and the screen."""
        self.n += 1
        tid = f"turn.{self.n}"
        out = None
        with self.store.transaction(tid) as tx:
            out = build(tx) if build is not None else None
            writes = [e.seq for e in tx.events if e.seq is not None]
        for k, (role, message, data) in enumerate(calls):
            self.store.record_model_call(ModelCallRecord(
                call_id=f"call.{tid}.{role.value}.{k}.0", turn_id=tid, role=role, seq=k, provider="fixture",
                model_id="haiku", schema_hash="fixture", request={"packet": f"[THIS MESSAGE]\n{message}"},
                response={"data": data}))
        pause = self.store.state.open_pause()
        if isinstance(out, str):
            shown = f"{shown}\n\n{out}" if shown else out
        self.store.save_turn(TurnRecord(
            turn_id=tid, input_verbatim=said, delivered_verbatim=shown, writes=writes,
            model_calls=[f"call.{tid}.{r.value}.{k}.0" for k, (r, _, _) in enumerate(calls)],
            pause={"kind": pause.kind, "frame_id": pause.frame_id, "options": [c.get("id", "") for c in pause.choices]}
            if pause is not None else None))
        return out

    def beat(self, tx: Any, *, intent: str, verb: str, target: str, change: Change, faces: tuple[int, ...] = (),
             auto: bool = False, **over: Any) -> str:
        """Run one beat through gate, necessity and frame with a fixed Framer proposal; the OFFER block (or the
        RESULT) as the screen shows it."""
        self.rng.faces = list(faces)
        b = Beat(id=f"beat.{self.n}", actor=self.pc, intent=intent, method=over.pop("method", intent),
                 restatement=over.pop("restatement", intent), verb=verb, target=target, change=change,
                 declared_seq=tx.state.last_seq, speech=verb == "verb.talk", against_will=over.pop("against_will",
                                                                                                    False))
        snags = over.pop("snags", [])
        levers = over.pop("levers", [])

        def framer(beat: Beat, candidates: list[str], *, gate: Any, note: str | None = None) -> ProposedFrame:
            v = gate.verb or beat.verb or ""
            anchor = next((c for c in candidates if v.split(".")[-1] in c), candidates[0])
            src = over.get("stakes_source") or ("goodwill_or_trust" if v == "verb.talk" else "aware_opponent_or_observer")
            tc = first_fitting_cost(RULES, role="threatened", state=tx.state, actor=beat.actor, stakes_source=src,
                                    target=beat.target, declared_seq=beat.declared_seq or None)
            alt = first_fitting_cost(RULES, role="alternate", other=tc, state=tx.state, actor=beat.actor,
                                     stakes_source=src, target=beat.target, declared_seq=beat.declared_seq or None)
            person = tx.state.entities.get(over.get("against", beat.target) or "")
            ob = (Obstacle(kind="opposed", entity=person.id) if person is not None and person.kind == "npc" else
                  Obstacle(kind="tier", obstacle_class="other", tier=over.get("tier", "moderate"), id="obs.t"))
            return ProposedFrame(anchor=anchor, attribute=ATTR.get(v, "wits"), stakes_source=src, obstacle=ob,
                                 threatened_cost=tc, alternate_cost=alt, snags=snags, levers=levers,
                                 method_consequences=over.get("consequences", []))

        env = PipelineEnv(tx=tx, rules=RULES, rng=self.rng, store=self.store, framer=framer, pc=self.pc,
                          auto_commit=auto)
        may_auto, allowed = pipeline._may_auto, frame_mod.auto_commit_allowed
        if auto:  # committed with no OFFER shown, as an auto-commit records it (the misread case's buggy past)
            pipeline._may_auto = lambda env, frame: True  # type: ignore[assignment]  # noqa: ARG005
            frame_mod.auto_commit_allowed = lambda frame: True  # type: ignore[assignment]  # noqa: ARG005
        try:
            res = run_beats(env, [BeatPlan(beat=b, intent_verbs=[verb.split(".")[-1]])])
        finally:
            pipeline._may_auto, frame_mod.auto_commit_allowed = may_auto, allowed
        if auto and res.pause is not None and res.pause.detail.get("stage") == "near_miss":  # the failure taken
            res = resume(env, res.pause, "failure")
        kinds = ("RESULT", "REDIRECT") if auto else ("OFFER", "RESULT", "REDIRECT")
        blocks = [o["text"] for out in res.outcomes for o in out.oof if o["kind"] in kinds]
        assert blocks, f"no OFFER or RESULT for {intent!r}: {[(o.status, o.entry.gate_words) for o in res.outcomes]}"
        return "\n".join(blocks)


PEOPLE = {"attributes": {"wits": 1, "presence": 1, "resolve": 1, "agility": 1, "might": 1}, "defenses": {"notice": 11}}
PC_ATTR = {"might": 1, "agility": 2, "endurance": 1, "wits": 1, "intellect": 0, "presence": 2, "resolve": 0}


def heron_ferry(path: Path) -> dict[str, str]:
    """A ferry landing at dusk: Wren (she/her), Tam the blind ferryman, Mira the eel-seller. Turn 3 charges the
    fare twice (10 → 8 → 6); turn 2's narration puts Mira's lantern out and turn 3's lights the plank with it; turn 4
    opens an OFFER to persuade blind Tam to read a seal."""
    g = Game(path, 2601)
    out: dict[str, str] = {}
    with g.store.transaction("turn.0") as tx:
        g.place = g.ent(tx, "place", "The Heron Landing", {"place_kind": "landmark", "desc": "a ferry landing on the"
                                                           " river Wend, mud and planks under a toll lamp"})
        g.pc = g.ent(tx, "pc", "Wren Ashby", {"attributes": PC_ATTR, "competence": {}, "pronouns": "she/her",
                                               "livelihood": "orig.life.wanderer", "upbringing": "orig.up.road"},
                     licences=("lic.lang.common",), quantities={"vitality": (12, 0, 12), "coin": (10, 0, 999)})
        tam = out["tam"] = g.ent(tx, "npc", "Tam Harlan", {**PEOPLE, "role": "ferryman, blind since the river fever",
                                                          "pronouns": "he/him", "detail": "milk-white eyes",
                                                          "stance": {"stance": "helps", "toward": "pc",
                                                                     "why": "a fare is a fare"}})
        mira = out["mira"] = g.ent(tx, "npc", "Mira Sallow", {**PEOPLE, "role": "eel-seller", "pronouns": "she/her"},
                                   licences=("lic.lang.common",))
        out["letter"] = g.ent(tx, "item", "Sealed Letter", {"desc": "a letter closed with a wax seal"})
        g.fact(tx, tam, "detail.eyes", "milk-white: he has been blind since the river fever")
        g.fact(tx, "world", "weather", "a cold wind off the river")
        g.open_scene(tx, [tam, mira], "Will Wren get across the Wend tonight?")
    g.turn("(opening)", "Dusk settles over the Heron Landing. Mud and wet planks run down to the river Wend under a "
           "toll lamp that has not been lit. Tam Harlan sits on the gunwale of his flat ferry, his milk-white eyes "
           "turned toward the water, a coil of rope in his lap. A few strides up the bank Mira Sallow guts eels into a "
           "bucket by the light of a small tin lantern. The wind off the river is cold.")
    g.turn("I ask Tam what the crossing costs, and ask Mira whether the river has been quiet.",
           "Tam's head turns toward your voice before the rest of him does. \"Two coin, same as it's always been,\" he "
           "says. \"Pay when you're aboard.\" Mira wipes her knife on her apron. \"Quiet enough. Too quiet for eels, "
           "and the night boats went down early.\" The wind gusts, and her little tin lantern gutters and goes out; "
           "she curses and works on by the last of the dusk.")

    def pay(tx: Any) -> str:
        tx.add(Event.of("quantity_changed", source="engine", rule_id="01.11.2", entity=g.pc, quantity="coin", delta=-2,
                        new_value=8, reason="paid Tam the fare"))
        tx.add(Event.of("quantity_changed", source="engine", rule_id="01.11.2", entity=g.pc, quantity="coin", delta=-2,
                        new_value=6, reason="whatever the roll: the fare is handed over"))
        tx.add(Event.of("position_set", source="engine", rule_id="10.1.1", entity=g.pc, location=g.place))
        return "[RESULT] no roll · success\n         Changed: coin 10 → 6"

    g.turn("I pay Tam the two coin and step aboard.",
           "You count two coins into Tam's palm. He weighs them without looking, nods once, and pockets them. Mira "
           "lifts her lantern to light the plank for you, and you step down into the ferry; it rocks, then settles. "
           "Tam pushes off with his pole, and the landing slides away behind you.", pay)

    def ask(tx: Any) -> str:
        return g.beat(tx, intent="Tam reads the seal on the letter for Wren", verb="verb.talk", target=tam,
                      change=Change(kind="persuade_to", what=tam),
                      restatement="Hand Tam the letter and ask him to read you the seal.",
                      consequences=["Tam handles the letter, whatever he makes of it."])

    out["offer4"] = g.turn("Halfway across, I hand Tam the letter and ask him to read me the seal.",
                           "Halfway across, the far bank is a dark line. You hold the letter out, and Tam turns his "
                           "milk-white eyes toward the rustle of the paper. His hand finds it by touch.", ask)
    g.store.close()
    return out


def east_gate(path: Path) -> dict[str, str]:
    """The east gate of Hartwell at night: Sergeant Hale Brannock (he/him) of the Hartwell watch asks Pell, a gate
    guard of the same watch, to unbar the gate; the OFFER rolls as if Hale were a stranger."""
    g = Game(path, 2602)
    out: dict[str, str] = {}
    with g.store.transaction("turn.0") as tx:
        g.place = g.ent(tx, "place", "The East Gate of Hartwell", {"place_kind": "landmark",
                                                                   "desc": "the town's east gate, barred at night"})
        g.pc = g.ent(tx, "pc", "Hale Brannock", {"attributes": PC_ATTR, "competence": {}, "pronouns": "he/him",
                                                  "livelihood": "orig.life.watchman", "upbringing": "orig.up.town",
                                                  "member_of": ["the Hartwell watch"]},
                     licences=("lic.lang.common", "lic.lang.letters"),
                     quantities={"vitality": (12, 0, 12), "coin": (6, 0, 999)})
        pell = out["pell"] = g.ent(tx, "npc", "Pell Rudd", {**PEOPLE, "role": "gate guard of the Hartwell watch",
                                                           "pronouns": "he/him", "member_of": ["the Hartwell watch"]})
        g.fact(tx, g.pc, "rank", "sergeant of the Hartwell watch")
        g.fact(tx, "world", "gate_orders", "the east gate stays barred from dusk to dawn unless a sergeant or officer of the "
                                           "watch orders it opened")
        g.open_scene(tx, [pell], "Will the gate open tonight?")
    g.turn("(opening)", "Night at the east gate of Hartwell. The great bar sits in its brackets across the doors, and a "
           "brazier throws red light on the arch. Pell Rudd of the watch stamps his feet beside it, spear propped on "
           "his shoulder. Beyond the gate, the road runs dark toward the fields.")

    def ask(tx: Any) -> str:
        return g.beat(tx, intent="Pell unbars the east gate for Hale", verb="verb.talk", target=pell,
                      change=Change(kind="persuade_to", what=pell), tier="hard",
                      restatement="Tell Pell to unbar the gate: you are his sergeant, out on watch business.",
                      consequences=["Pell hears the order whatever the roll."])

    out["offer2"] = g.turn("I tell Pell to unbar the gate for me. I'm his sergeant, out on watch business.",
                           "Pell squints at you over the brazier. \"Gate stays barred till dawn,\" he says. "
                           "\"Orders.\"", ask)
    g.store.close()
    return out


def guild_hall(path: Path) -> dict[str, str]:
    """The river guild's counting room: Ada (she/her, no Letters) and Odo Penn, the guild's clerk, who holds
    Letters. Turn 2's OFFER counts "Odo can't read the ledger" as a −2 (a fact that should never have been written);
    turn 4's sneak OFFER carries a garbled snag."""
    g = Game(path, 2603)
    out: dict[str, str] = {}
    with g.store.transaction("turn.0") as tx:
        g.place = g.ent(tx, "place", "The Counting Room", {"place_kind": "building",
                                                           "desc": "the river guild's counting room"})
        g.pc = g.ent(tx, "pc", "Ada Penrose", {"attributes": PC_ATTR, "competence": {"deed.guile.thievery": 2},
                                                "pronouns": "she/her", "livelihood": "orig.life.thief"},
                     licences=("lic.lang.common", "lic.training.guile_thievery"),
                     quantities={"vitality": (12, 0, 12), "coin": (4, 0, 999)})
        odo = out["odo"] = g.ent(tx, "npc", "Odo Penn", {**PEOPLE, "role": "clerk of the river guild",
                                                        "pronouns": "he/him"},
                                 licences=("lic.lang.common", "lic.lang.letters", "lic.training.craft_scribing"))
        out["ledger"] = g.ent(tx, "item", "Guild Ledger", {"desc": "the guild's ledger of barges and cargoes"})
        out["no_read"] = g.fact(tx, odo, "can_read_the_ledger_s_cramped_hand", False, source="ruling")
        g.open_scene(tx, [odo], "What does the ledger say about the barge Heron?")
    g.turn("(opening)", "The counting room smells of tallow and damp paper. Odo Penn, the guild's clerk, sits behind "
           "a table stacked with tally sticks, the great ledger open under his hand. Shelves of rolled charters climb "
           "the wall behind him.")

    def ask(tx: Any) -> str:
        return g.beat(tx, intent="Odo reads Ada the ledger's entry for the barge Heron", verb="verb.talk", target=odo,
                      change=Change(kind="persuade_to", what=odo), snags=[out["no_read"]],
                      restatement="Ask Odo to read you the ledger's entry for the barge Heron.")

    out["offer2"] = g.turn("I ask Odo to read me the ledger's entry for the barge Heron.",
                           "Odo keeps his hand flat on the open page. \"Guild business,\" he says, \"and you're not "
                           "guild.\"", ask)

    def withdraw(tx: Any) -> None:
        p = tx.state.open_pause()
        tx.add(Event.of("pause_closed", source="player", rule_id="12.2.6", pause_id=p.pause_id, choice="withdraw"))
        tx.add(Event.of("offer_logged", source="engine", rule_id="01.7.1", frame_id=None, shown_at=tx.state.time.now,
                        choice="withdraw"))
        out["unaware"] = g.fact(tx, odo, "is_not_unaware_of_the_ledger_leaving_the_table_while_h", False, source="ruling")

    g.turn("withdraw", "You let it go. Odo turns a page, and after a while he gets up to search the shelves for a "
           "charter, his back to the table.", withdraw)

    def lift(tx: Any) -> str:
        return g.beat(tx, intent="Ada takes the guild ledger from Odo's table", verb="verb.sneak", target=odo,
                      change=Change(kind="take", what=out["ledger"], whom=odo), snags=[out["unaware"]], against=odo,
                      against_will=True,
                      restatement="Slide the ledger off Odo's table while his back is turned.")

    out["offer4"] = g.turn("While Odo's back is turned at the shelves, I slide the ledger off his table.",
                           "Odo runs a finger along the charters, muttering dates. The ledger lies open on the table "
                           "an arm's length from you.", lift)
    g.store.close()
    return out


def eel_market(path: Path) -> dict[str, str]:
    """A fish market: Corin (he/him) picks up an eel to see if it is fresh; the Reader read it as theft (its call is
    on record), the theft failed, and Hesk has treated him as a thief for three turns since. The first seed whose own
    dice fail the theft (fixed faces would break the RNG log the game replays on load)."""
    for seed in range(2604, 2704):
        path.unlink(missing_ok=True)
        out = _eel_market(path, seed)
        if out.pop("failed", ""):
            return out
    raise RuntimeError("no seed failed the theft")


def _eel_market(path: Path, seed: int) -> dict[str, str]:
    g = Game(path, seed)
    out: dict[str, str] = {}
    with g.store.transaction("turn.0") as tx:
        g.place = g.ent(tx, "place", "The Eel Market", {"place_kind": "market", "desc": "a fish market on the quay"})
        g.pc = g.ent(tx, "pc", "Corin Vale", {"attributes": PC_ATTR, "competence": {}, "pronouns": "he/him",
                                               "livelihood": "orig.life.sailor"},
                     licences=("lic.lang.common",), quantities={"vitality": (12, 0, 12), "coin": (7, 0, 999)})
        hesk = out["hesk"] = g.ent(tx, "npc", "Hesk Marrow", {**PEOPLE, "role": "fishwife", "pronouns": "she/her"})
        pim = out["pim"] = g.ent(tx, "npc", "Old Pim", {**PEOPLE, "role": "net-mender", "pronouns": "he/him"})
        out["eel"] = g.ent(tx, "item", "Silver Eel", {"desc": "a fat silver eel on Hesk's slab"})
        g.open_scene(tx, [hesk, pim], "Where do the eel-boats go at night?")
    g.turn("(opening)", "Morning on the quay. Hesk Marrow slaps eels onto her slab and calls the price of each. Old "
           "Pim sits on an upturned crate mending a net, his fingers quick and his eyes half shut.")
    reader = {"beats": [{"intent": "Corin steals a silver eel from Hesk's slab", "verb": "verb.sneak",
                         "target": out["eel"], "against_will": True,
                         "change": {"kind": "take", "what": out["eel"], "whom": hesk, "description": None},
                         "how": "pick up one of Hesk's eels"}]}

    def lift(tx: Any) -> str:
        res = g.beat(tx, intent="Corin steals a silver eel from Hesk's slab", verb="verb.sneak", target=out["eel"],
                     change=Change(kind="take", what=out["eel"], whom=hesk), against_will=True, auto=True, against=hesk,
                     stakes_source="aware_opponent_or_observer", restatement="Steal a silver eel from Hesk's slab.")
        tx.add(Event.of("relationship_set", source="engine", rule_id="15.1.5", a=hesk, b=g.pc, kind="standing",
                        steps=-2, new_value=-2, reason="caught stealing from her slab"))
        g.fact(tx, hesk, "detail.manner", "glaring at you as a thief", source="narration")
        out["failed"] = "failure" if "· failure" in res and "near miss" not in res else ""
        return res

    g.turn("I pick up one of Hesk's eels to see if it's fresh.",
           "You lift a silver eel from the slab, and it slides in your hand. Hesk's fist closes on your wrist. "
           "\"Thief!\" she shouts, loud enough to turn heads along the quay, and snatches the eel back.", lift,
           calls=[(Role.READER, "THE PLAYER'S MESSAGE: \"I pick up one of Hesk's eels to see if it's fresh.\"",
                   reader)])
    g.turn("I tell Hesk I was only looking, and put my hands up.",
           "\"Looking,\" Hesk says, and spits. \"I know looking. Hands where I can see them.\" She keeps one eye on "
           "you as she works.")
    g.turn("I ask Old Pim where the eel-boats go at night.",
           "Pim doesn't look up from his net. \"Down past the weir, where the water's slow. Don't tell Hesk I said "
           "so; she'll think you mean to rob her boats as well.\"")
    g.turn("I ask Hesk about the night catch.",
           "Hesk turns her back on you. \"Ask somewhere else, thief. I've nothing for you.\"")
    g.store.close()
    return out


SCENARIOS: dict[str, Callable[[Path], dict[str, str]]] = {"heron_ferry": heron_ferry, "east_gate": east_gate,
                                                           "guild_hall": guild_hall, "eel_market": eel_market}


def main() -> int:
    info: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        for name, build in SCENARIOS.items():
            db = Path(tmp) / f"{name}.db"
            info[name] = build(db)
            target = OUT / f"fresh-{name}.db.gz"
            with db.open("rb") as src, target.open("wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as dst:
                shutil.copyfileobj(src, dst)
            print(f"{target.name}: {json.dumps(info[name], ensure_ascii=False)[:600]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
