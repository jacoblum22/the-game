"""The game API (contracts/engine-api.md; T072): the only surface a front end uses.

    game, resp = Game.new("saves/salt.db", GameConfig(offline=True))   # the world seed's first question
    resp = game.submit("mixed")                                        # seed -> creation -> play -> ending
    resp = game.answer("commit")                                       # a pick from the open pause
    game.codex("sheet"); game.spend(); game.turn_record("turn.3"); game.branch("before the bridge")
    game.set_pref("budget_usd", 5.0); game.set_pref("autocommit", True)
    game.close()                                                       # session close; nothing is ever lost
    game, resp = Game.open("saves/salt.db", GameConfig(offline=True))  # recap + whatever was open
    Game.replay("saves/salt.db")                                       # ReplayResult(identical, divergence)

Routing: `submit` / `answer` go to whichever flow owns the open pause (`engine.dm.seed_flow.flow_of`): the seed
(PR-12-9), creation (PR-02-7), the ending menu or the retirement question (engine/dm/ending.py); with none, play
(PR-12-1 via `engine.dm.turn.play_turn` / `play_answer`). Meta `game.phase` goes seed -> creation -> play ->
ending (-> creation for a new character). There is no turn, scene or session limit anywhere (FR-012).

Every API call is logged, before it runs, in the game file's `game_inputs` table (kind, argument, outcome), so
`Game.replay` can re-drive a fresh copy with the same seed and the recorded model outputs (`ReplayModel`) and
compare every event. Budget: after a play step, once the session's spending passes the budget,
`Response.budget_notice` is set (between turns only, never at a pause inside a turn; once per session).
"""

from __future__ import annotations

import json
import re
import secrets
import sqlite3
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from engine import ids
from engine.data.loader import Rules, load_rules
from engine.dm import oof
from engine.dm.context import TurnContext
from engine.dm.player_text import clean, clean_response, entity_names
from engine.dm.response import Flags, Response
from engine.dm.seed_flow import PHASE_KEY, SeedFlow, flow_of, present_pause
from engine.llm.base import ModelError, Role, RoleModel, StructuredModel
from engine.llm.budget import SpendTotals, SpendTracker
from engine.store.db import Store
from engine.store.events import Event
from engine.store.records import TurnRecord

ROLE_IDS = tuple(r.value for r in Role)
MID_TURN = frozenset({"offer", "clarify", "redirect", "near_miss", "last_chance", "yield_terms"})
TITLE = "title"
BUDGET_PREF = "pref.budget_usd"  # meta {usd: float | None}; overrides GameConfig.budget_usd_per_session
AUTOCOMMIT_PREF = "auto_commit"  # meta read by TurnContext.auto_commit (01.7.4)
INPUTS_SQL = ("CREATE TABLE IF NOT EXISTS game_inputs (n INTEGER PRIMARY KEY, kind TEXT NOT NULL, arg TEXT, "
              "seq_before INTEGER, outcome TEXT)")


def _default_models() -> dict[str, RoleModel]:
    return {r: RoleModel() for r in ROLE_IDS}  # research.md R2: one provider, one key; TODO(CROSS_FAMILY_CHECKER)


class GameConfig(BaseModel):
    """contracts/engine-api.md `GameConfig`, plus `offline` (contracts/cli.md `--offline`)."""

    models: dict[str, RoleModel] = Field(default_factory=_default_models)
    offline: bool = False  # every role -> engine.llm.offline.OfflineModel (free; template prose)
    budget_usd_per_session: float | None = 2.00  # a warning threshold, never a limit (FR-039)
    oracle_free_cap_per_scene: int | None = 6  # engine-side stopgap for I-038
    milestone: int = 1
    engine: str = "pipeline"  # "dm-tools": spec 031's prototype, one DM model with tools (engine/dm/dm_tools.py)
    dm_secrets: str = "hidden"  # "visible": the dm-tools DM sees each present NPC's private case knowledge

    def model(self) -> StructuredModel:
        """The model every role calls (raises MissingKey for Gemini without a key, before anything is written)."""
        if self.offline:
            from engine.llm.offline import OfflineModel

            return OfflineModel()
        from engine.llm.gemini import GeminiModel

        return GeminiModel({Role(k): v for k, v in self.models.items() if k in ROLE_IDS})


class ReplayResult(BaseModel):
    identical: bool
    divergence: str | None = None
    events: int = 0  # events compared
    inputs: int = 0  # API calls re-driven


def saved_engine(config: GameConfig, stored: Mapping[str, Any] | None) -> GameConfig:
    """The play engine and the secrets arm belong to the save (spec 032 FR-11): what `game_created` stored wins over
    the caller's config, and a save without the key is a pipeline save (A7). Never read the default of `GameConfig`
    here: it flips to dm-tools later and would silently turn old saves into dm-tools games."""
    stored = stored or {}
    return config.model_copy(update={"engine": str(stored.get("engine") or "pipeline"),
                                     "dm_secrets": str(stored.get("dm_secrets") or "hidden")})


class Game:
    """One world in one SQLite file, with its characters. Build with `Game.new` / `Game.open`."""

    def __init__(self, store: Store, config: GameConfig, model: StructuredModel, *, rules: Rules | None = None,
                 log_inputs: bool = True) -> None:
        self.store = store
        self.config = config
        self.model = model
        self.rules = rules or load_rules()
        self._log = log_inputs
        self.store.conn.execute(INPUTS_SQL)
        self.tracker = SpendTracker(config.budget_usd_per_session, game_usd=self._game_usd())
        pref = store.state.meta.get(BUDGET_PREF)
        if isinstance(pref, dict) and "usd" in pref:
            self.tracker.budget_usd = pref["usd"]
        self._noticed = False
        self.ctx = TurnContext.for_store(store, model=model, rules=self.rules, recorder=self._record,
                                         config={"oracle_free_cap_per_scene": config.oracle_free_cap_per_scene,
                                                 "engine": config.engine, "dm_secrets": config.dm_secrets})
        self._prime_call_seq()
        self._seed_flow: SeedFlow | None = None
        self.closed = False

    @property
    def seed_flow(self) -> SeedFlow:
        """One SeedFlow for the game's life: its WorldSeed stays built between answers."""
        if self._seed_flow is None:
            self._seed_flow = SeedFlow(self.ctx)
        return self._seed_flow

    # ------------------------------------------------------------------------------- construction

    @classmethod
    def new(cls, path: Path | str, config: GameConfig | None = None, seed: int | None = None, *,
            model: StructuredModel | None = None) -> tuple[Game, Response]:
        """A new game file: `game_created` (the seed recorded; random when omitted), then the world seed's first
        question (PR-12-9)."""
        config = config or GameConfig()
        model = model or config.model()  # MissingKey here: nothing written
        rules = load_rules()
        seed = int(seed) if seed is not None else secrets.randbelow(2**31 - 1) + 1
        store = Store.create(path, seed=seed, milestone=config.milestone, config=config.model_dump(mode="json"),
                             rules_hash=rules.hash)
        game = cls(store, config, model, rules=rules)
        return game, game._call("new", {"seed": seed}, game._start)

    @classmethod
    def open(cls, path: Path | str, config: GameConfig | None = None, *,
             model: StructuredModel | None = None) -> tuple[Game, Response]:
        """Resume at the last event: a recap (12.5) in play, then exactly what was open (a seed step, a creation
        step, an offer, the last-chance menu, the ending menu)."""
        config = config or GameConfig()
        model = model or config.model()
        store = Store.open(path)
        created: Any = next(store.events(types=["game_created"])).payload
        config = saved_engine(config, created.config)  # spec 032 FR-11
        game = cls(store, config, model)
        return game, game._call("open", None, game._resume)

    # ------------------------------------------------------------------------------- the player's input

    def submit(self, message: str) -> Response:
        """The player's text, verbatim: an answer to the open seed / creation step, or a turn of play."""
        return self._call("submit", message, lambda: self._submit(message))

    def answer(self, choice_id: str) -> Response:
        """A pick from the open pause's choices (free text via `submit` works too, 12.2.6)."""
        return self._call("answer", choice_id, lambda: self._answer(choice_id))

    def new_character(self) -> Response:
        """After an ending: creation again in this world (PR-02-*)."""
        return self._call("new_character", None, self._new_character)

    def dispute(self, text: str) -> Response:
        """/fix: the DM checks the record and corrects a seen error (PR-12-4, 12.3.6)."""
        return self._call("dispute", text, lambda: self._dispute(text))

    def set_pref(self, key: str, value: Any) -> None:
        """`budget_usd` (float | None: no warnings) or `autocommit` (bool; 01.7.4). Stored as meta."""
        if key not in ("budget_usd", "autocommit"):
            raise ValueError(f"unknown preference {key!r} (budget_usd, autocommit)")
        self._call("set_pref", {"key": key, "value": value}, lambda: self._set_pref(key, value))

    def close(self) -> None:
        """Session close (PR-12-8: the pause stays open, a where-you-stand line), then the file is closed."""
        if self.closed:
            return
        try:
            st = self.store.state
            if flow_of(st) not in ("seed", "creation") and self._pc() is not None and not self._pending_kind():
                self._call("close", None, self._close_session)
        finally:
            self.closed = True
            self.store.close()

    # ------------------------------------------------------------------------------- reading

    def codex(self, section: str | None = None) -> Any:
        """`sheet` (default), `abilities`, `conditions`, `journal`, `threads`, `rules <id>` (00.6.4)."""
        from engine.dm.codex import codex

        view = codex(self.store.state, section, self.rules)
        if view.section.startswith("rules"):
            return view  # the player asked for the rule card itself
        return view.model_copy(update={"text": clean(view.text, self.rules, entity_names(self.store.state))})

    def turn_record(self, turn_id: str) -> TurnRecord | None:
        return self.store.turn(turn_id)

    def spend(self) -> SpendTotals:
        return self.tracker.totals()

    def branch(self, label: str) -> str:
        """A save point to return to: an event-log fork (table `branches`) and a copy of the file next to it,
        `<name> @ <label>.db`, which the front end lists and continues like any game."""
        st = self.store.state
        taken = {r[0] for r in self.store.conn.execute("SELECT branch_id FROM branches")}
        base = f"br.{ids.slug(label) or 'save'}"
        bid, n = base, 1
        while bid in taken:
            n += 1
            bid = f"{base}_{n}"
        self.store.conn.execute("INSERT INTO branches(branch_id, parent_id, fork_seq) VALUES (?, ?, ?)",
                                (bid, "main", self.store.last_seq))
        stem = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", label.strip()) or bid
        dest = self.store.path.with_name(f"{self.store.path.stem} @ {stem}.db")
        k = 1
        while dest.exists():
            k += 1
            dest = self.store.path.with_name(f"{self.store.path.stem} @ {stem} ({k}).db")
        target = sqlite3.connect(str(dest))
        try:
            self.store.conn.backup(target)
        finally:
            target.close()
        copy = Game(Store.open(dest), self.config, self.model, rules=self.rules)
        try:
            title = str(st.meta.get(TITLE) or self.store.path.stem)
            copy._call("set_title", f"{title} @ {label.strip()}", lambda: copy._write_title(f"{title} @ {label.strip()}"))
        finally:
            copy.store.close()
        return bid

    # ------------------------------------------------------------------------------- replay

    @classmethod
    def replay(cls, path: Path | str, until_seq: int | None = None) -> ReplayResult:
        """Rebuild the game in a temporary copy from its recorded inputs, the stored seed and the recorded model
        outputs; compare every event (up to `until_seq`). Reports the first difference."""
        from engine.llm.replay import ReplayModel

        src = Store.open(path)
        try:
            src.conn.execute(INPUTS_SQL)
            original = [e.model_dump(mode="json") for e in src.events(until=until_seq)]
            calls = src.model_calls()
            inputs = [dict(r) for r in src.conn.execute("SELECT n, kind, arg, outcome FROM game_inputs ORDER BY n")]
            created = next(src.events(types=["game_created"]))
        finally:
            src.close()
        gc: Any = created.payload
        made = {"seed": gc.seed, "milestone": gc.milestone, "config": gc.config, "rules_hash": gc.rules_hash,
                "engine_version": gc.engine_version}
        replayed = cls._redrive(inputs, made, ReplayModel.from_rows(calls), until_seq=until_seq)
        if isinstance(replayed, ReplayResult):
            return replayed
        events, done = replayed
        for a, b in zip(original, events, strict=False):
            if a != b:
                diff = sorted(k for k in a if a.get(k) != b.get(k))
                return ReplayResult(identical=False, inputs=done, events=a["seq"], divergence=(
                    f"seq {a['seq']} ({a['type']}) differs in {', '.join(diff)}: recorded {_short(a)}, "
                    f"replay {_short(b)}"))
        if len(original) != len(events):
            return ReplayResult(identical=False, inputs=done, events=min(len(original), len(events)), divergence=(
                f"recorded {len(original)} events, replay {len(events)}"))
        return ReplayResult(identical=True, inputs=done, events=len(original))

    @classmethod
    def export_record(cls, path: Path | str) -> dict[str, Any]:
        """A compact, file-free record of a game for regression tests (T077): how it was created, every API input,
        every model call's response with a digest of the packet it was asked (`packet_digest`, not the text), and
        a digest per event. `Game.replay_record` re-drives it."""
        from engine.llm.replay import packet_digest

        src = Store.open(path)
        try:
            src.conn.execute(INPUTS_SQL)
            created: Any = next(src.events(types=["game_created"])).payload
            inputs = [dict(r) for r in src.conn.execute("SELECT n, kind, arg, outcome FROM game_inputs ORDER BY n")]
            calls = []
            for row in src.model_calls():
                req = row.get("request") or {}
                packet = str(req.get("packet") or "")
                keep = {k: row.get(k) for k in ("call_id", "turn_id", "role", "attempt", "provider", "model_id",
                                                "schema_hash", "response", "outcome")}
                keep["extra"] = row.get("extra") or {}
                keep["request"] = {"attempt": req.get("attempt"), **packet_digest(packet)}
                calls.append(keep)
            events = [{"seq": e.seq, "type": e.type, "turn_id": e.turn_id, "digest": _digest(e.model_dump(mode="json"))}
                      for e in src.events()]
        finally:
            src.close()
        return {"format": 1, "created": {"seed": created.seed, "milestone": created.milestone,
                                         "config": created.config, "rules_hash": created.rules_hash,
                                         "engine_version": created.engine_version},
                "inputs": inputs, "calls": calls, "events": events}

    @classmethod
    def replay_record(cls, record: dict[str, Any], *, check_packets: bool = True) -> ReplayResult:
        """Re-drive an `export_record` record with its recorded model responses; with `check_packets` a call whose
        packet now differs from the recorded digest diverges (the engine would ask the model something else).
        Then every event's digest is compared."""
        from engine.llm.replay import ReplayModel, record_from_row

        model = ReplayModel((record_from_row(c) for c in record["calls"]), check_packets=check_packets)
        replayed = cls._redrive(record["inputs"], record["created"], model)
        if isinstance(replayed, ReplayResult):
            return replayed
        events, done = replayed
        want = record["events"]
        for a, b in zip(want, events, strict=False):
            if a["digest"] != _digest(b):
                return ReplayResult(identical=False, inputs=done, events=a["seq"], divergence=(
                    f"seq {a['seq']} (recorded {a['type']} in {a['turn_id']}) differs: replay {_short(b)}"))
        if len(want) != len(events):
            return ReplayResult(identical=False, inputs=done, events=min(len(want), len(events)), divergence=(
                f"recorded {len(want)} events, replay {len(events)}"))
        return ReplayResult(identical=True, inputs=done, events=len(want))

    @classmethod
    def _redrive(cls, inputs: list[dict[str, Any]], made: dict[str, Any], model: StructuredModel, *,
                 until_seq: int | None = None) -> tuple[list[dict[str, Any]], int] | ReplayResult:
        """Re-run recorded inputs in a temporary game file: (its events as JSON, inputs run), or the first input
        whose outcome differs from the recorded one."""
        if not inputs or inputs[0]["kind"] != "new":
            return ReplayResult(identical=False, divergence="no recorded inputs: this game cannot be replayed")
        cfg = saved_engine(GameConfig.model_validate({k: v for k, v in (made["config"] or {}).items()
                                                      if k in GameConfig.model_fields}), made["config"])
        rules = load_rules()
        done = 0
        with tempfile.TemporaryDirectory(prefix="replay-") as tmp:
            dest = Path(tmp) / "replay.db"
            game: Game | None = None
            try:
                for inp in inputs:
                    kind, arg = inp["kind"], json.loads(inp["arg"]) if inp["arg"] is not None else None
                    if game is not None and until_seq is not None and game.store.last_seq >= until_seq:
                        break
                    try:
                        if kind == "new":
                            store = Store.create(dest, seed=made["seed"], milestone=made["milestone"],
                                                 config=made["config"], rules_hash=made["rules_hash"],
                                                 engine_version=made["engine_version"])
                            game = cls(store, cfg, model, rules=rules, log_inputs=False)
                            game._start()
                        else:
                            assert game is not None
                            if kind == "open":
                                game.store.close()
                                game = cls(Store.open(dest), cfg, model, rules=rules, log_inputs=False)
                            game._replay_input(kind, arg)
                        failed = None
                    except (ModelError, ValueError, RuntimeError) as exc:
                        failed = f"{exc.__class__.__name__}: {exc}"
                    done += 1
                    want = inp["outcome"] or "ok"
                    got = "ok" if failed is None else failed.split(":")[0]
                    if want != "ok" and want.split(":")[0] == got:
                        continue
                    if want != got:
                        return ReplayResult(identical=False, inputs=done, divergence=(
                            f"input {inp['n']} ({kind} {arg!r}): recorded {want}, replay {failed or 'ok'}"))
                assert game is not None
                return [e.model_dump(mode="json") for e in game.store.events(until=until_seq)], done
            finally:
                if game is not None and not game.closed:
                    game.store.close()

    def _replay_input(self, kind: str, arg: Any) -> None:
        if kind == "open":
            self._resume()
        elif kind == "submit":
            self._submit(str(arg))
        elif kind == "answer":
            self._answer(str(arg))
        elif kind == "new_character":
            self._new_character()
        elif kind == "dispute":
            self._dispute(str(arg))
        elif kind == "set_pref":
            self._set_pref(arg["key"], arg["value"])
        elif kind == "close":
            self._close_session()
        elif kind == "set_title":
            self._write_title(str(arg))
        else:
            raise ValueError(f"unknown recorded input {kind!r}")

    # ------------------------------------------------------------------------------- internals: calls

    def _call(self, kind: str, arg: Any, fn: Any) -> Any:
        """Log the call (before it runs, so a failed one is on record too), run it, record its outcome."""
        n = None
        if self._log:
            cur = self.store.conn.execute("INSERT INTO game_inputs(kind, arg, seq_before) VALUES (?, ?, ?)",
                                          (kind, json.dumps(arg) if arg is not None else None, self.store.last_seq))
            n = cur.lastrowid
        try:
            out = fn()
        except BaseException as exc:
            if n is not None:
                self.store.conn.execute("UPDATE game_inputs SET outcome=? WHERE n=?",
                                        (f"{exc.__class__.__name__}: {exc}"[:500], n))
            raise
        if n is not None:
            self.store.conn.execute("UPDATE game_inputs SET outcome='ok' WHERE n=?", (n,))
        if isinstance(out, Response):  # every engine-written player string, without rule refs or ids
            out = clean_response(out, self.rules, self.store.state)
        return out

    def _record(self, rec: Any) -> None:
        self.store.record_model_call(rec)
        self.tracker.add(rec)

    def _game_usd(self) -> float:
        row = self.store.conn.execute("SELECT SUM(cost_usd) FROM model_calls").fetchone()
        return float(row[0] or 0.0)

    def _prime_call_seq(self) -> None:
        """Continue each (turn, role) call numbering where the file left it, so a call after a reopen never reuses a
        recorded call id (the replay key)."""
        best: dict[tuple[str | None, str], int] = {}
        for turn_id, role, seq in self.store.conn.execute(
                "SELECT turn_id, role, json_extract(extra, '$.seq') FROM model_calls"):
            key = (turn_id, str(role))
            best[key] = max(best.get(key, -1), int(seq or 0))
        for (turn_id, role), top in best.items():
            for _ in range(top + 1):
                self.ctx.next_call_seq(turn_id, role)

    def _pc(self) -> str | None:
        from engine.world.common import active_pc

        return active_pc(self.store.state)

    # ------------------------------------------------------------------------------- internals: flows

    def _start(self) -> Response:
        return self._after_seed(self.seed_flow.start())

    def _resume(self) -> Response:  # rule: PR-12-8
        from engine.dm.creation import CreationFlow
        from engine.dm.ending import present_ending
        from engine.dm.session import open_session

        self.tracker.new_session()
        self._noticed = False
        st = self.store.state
        flow = flow_of(st)
        if flow == "seed":
            return self.seed_flow.present()
        if flow == "creation":
            return CreationFlow(self.ctx).present()
        if flow == "ending":
            return present_ending(self.ctx)
        if flow == "retire":
            rec = st.open_pause()
            assert rec is not None
            return present_pause(rec, "play")
        if self._pc() is None:
            return self._restart_flow()
        first = self._settle_pending()
        if first is not None and first.phase == "ending":
            return first
        resp = open_session(self.ctx)
        return self._merge(first, resp, keep_first_pause=False)

    def _restart_flow(self) -> Response:
        """No character and nothing open (a game whose first step never ran): the seed, or creation after it."""
        from engine.dm.creation import CreationFlow

        if self.store.state.meta.get(PHASE_KEY) == "creation":
            return CreationFlow(self.ctx).begin()
        return self._after_seed(self.seed_flow.start())

    def _submit(self, message: str) -> Response:
        from engine.dm.creation import CreationFlow
        from engine.dm.ending import (
            answer_ending,
            answer_retire,
            ask_retire,
            ending_choice,
            is_retire,
            present_ending,
            retire_choice,
        )
        first = self._settle_pending()
        if first is not None and first.phase == "ending":
            return first
        st = self.store.state
        flow = flow_of(st)
        if flow == "seed":
            return self._after_seed(self.seed_flow.submit(message))
        if flow == "creation":
            return self._after_creation(CreationFlow(self.ctx).submit(message))
        if flow == "ending":
            choice = ending_choice(message)
            if choice is None:
                menu = present_ending(self.ctx)
                hint = oof.note_block("Pick one: a new character in this world, a new world, or stop here.")
                return menu.model_copy(update={"oof_blocks": [hint, *menu.oof_blocks]})
            return self._after_creation(answer_ending(self.ctx, choice))
        if flow == "retire":
            return self._after_turn(answer_retire(self.ctx, retire_choice(message)))
        if self._pc() is None:
            return self._restart_flow()
        if is_retire(message) and st.open_pause() is None:
            return self._merge(first, ask_retire(self.ctx))
        out = self._engine().play_turn(self.ctx, message)
        return self._merge(first, self._after_turn(out.response))

    def _answer(self, choice_id: str) -> Response:
        from engine.dm import turn
        from engine.dm.creation import CreationFlow
        from engine.dm.ending import answer_ending, answer_retire

        first = self._settle_pending()
        if first is not None and first.phase == "ending":
            return first
        st = self.store.state
        pause = st.open_pause()
        if pause is None or not any(c.get("id") == choice_id for c in pause.choices):
            if not (pause is not None and choice_id == "move_on" and pause.detail.get("flow") in ("seed",
                                                                                                  "creation")):
                raise ValueError(f"{choice_id!r} is not a choice of the open pause")
        flow = flow_of(st)
        if flow == "seed":
            return self._after_seed(self.seed_flow.answer(choice_id))
        if flow == "creation":
            return self._after_creation(CreationFlow(self.ctx).answer(choice_id))
        if flow == "ending":
            return self._after_creation(answer_ending(self.ctx, choice_id))
        if flow == "retire":
            return self._after_turn(answer_retire(self.ctx, choice_id))
        dm = self._engine() if (pause.detail or {}).get("stage") != "dispute" else None  # /fix stays the pipeline's
        out = (dm or turn).play_answer(self.ctx, choice_id)
        return self._merge(first, self._after_turn(out.response), keep_first_pause=False)

    def _engine(self) -> Any:
        """The module whose `play_turn` / `play_answer` run play: the pipeline (engine/dm/turn.py) or spec 031's
        DM with tools (engine/dm/dm_tools.py, `GameConfig.engine == "dm-tools"`)."""
        from engine.dm import dm_tools, turn

        return dm_tools if dm_tools.enabled(self.ctx) else turn

    def _new_character(self) -> Response:
        from engine.dm.creation import new_character
        from engine.dm.ending import ending_due, run_epilogue
        from engine.harm.threshold import ending_state

        st = self.store.state
        if ending_due(st):
            run_epilogue(self.ctx)
            st = self.store.state
        pc = self._pc()
        if flow_of(st) != "ending" and (pc is None or ending_state(st, pc) is None):
            raise ValueError("a new character comes after an ending (death, retirement or career end)")
        return self._after_creation(new_character(self.ctx))

    def _dispute(self, text: str) -> Response:
        from engine.dm import dm_tools
        from engine.dm.dispute import play_dm_dispute
        from engine.dm.turn import play_dispute

        if flow_of(self.store.state) in ("seed", "creation") or self._pc() is None:
            raise ValueError("there is nothing in play to dispute yet")
        first = self._settle_pending()
        # spec 032 G11: the same Fixer; a dm-tools game's re-frame plays the DM's turn again (no Narrator call)
        out = (play_dm_dispute if dm_tools.enabled(self.ctx) else play_dispute)(self.ctx, text)
        return self._merge(first, self._after_turn(out.response))

    def _set_pref(self, key: str, value: Any) -> None:
        if key == "budget_usd":
            usd = None if value is None else float(value)
            self.tracker.budget_usd = usd
            self._noticed = False
            self.store.append([Event.of("meta_set", source="player", rule_id="FR-039", key=BUDGET_PREF,
                                        value={"usd": usd})])
        else:
            self.store.append([Event.of("meta_set", source="player", rule_id="01.7.4", key=AUTOCOMMIT_PREF,
                                        value=bool(value))])

    def _close_session(self) -> Response:
        from engine.dm.session import close_session

        return close_session(self.ctx)

    # ------------------------------------------------------------------------------- internals: hand-overs

    def _after_seed(self, resp: Response) -> Response:
        self._sync_title()
        return resp

    def _sync_title(self) -> None:
        """meta `title`: the region's name once the seed names it (kept in step with a vetoed step 1)."""
        st = self.store.state
        name = ((st.meta.get("world.seed") or {}).get("region") or {}).get("name")
        if not name:
            ws = self.seed_flow.seed()
            raw = ws.st.get("region_name") if ws is not None else None
            name = str(raw).title() if raw else None
        if name and st.meta.get(TITLE) != name:
            self._write_title(name)

    def _write_title(self, title: str) -> None:
        self.store.append([Event.of("meta_set", source="engine", rule_id="FR-040", key=TITLE, value=title)])

    def _after_creation(self, resp: Response) -> Response:
        """Creation wrote the character: play begins with the opening (12.16.16)."""
        from engine.dm.opening import begin_play, needs_opening

        if resp.phase == "play" and resp.pause is None and needs_opening(self.store.state):
            return begin_play(self.ctx, resp)
        return resp

    def _after_turn(self, resp: Response) -> Response:
        """After a play step: the ending, when the character has reached one (FR-009), else the budget check."""
        from engine.dm.ending import ending_due, run_epilogue

        if ending_due(self.store.state):
            return self._merge(resp, run_epilogue(self.ctx), keep_first_pause=False)
        return self._budget(resp)

    def _budget(self, resp: Response) -> Response:  # rule: FR-039
        if self._noticed or (resp.pause is not None and resp.pause.kind in MID_TURN):
            return resp
        note = self.tracker.warning()
        if note:
            self._noticed = True
            resp = resp.model_copy(update={"budget_notice": note})
        return resp

    def _pending_kind(self) -> str | None:
        from engine.dm.ending import ending_due
        from engine.dm.opening import needs_opening
        from engine.dm.turn import NARRATION_PENDING

        st = self.store.state
        if st.meta.get(NARRATION_PENDING):
            return "narration"
        if flow_of(st) is None and needs_opening(st):
            return "opening"
        if flow_of(st) is None and ending_due(st):
            return "ending"
        return None

    def _settle_pending(self) -> Response | None:
        """What a failed or interrupted step left owed, before any new input: the narration of a turn whose writes
        committed (engine-api.md Errors), the opening of a written character, an ending's epilogue."""
        from engine.dm.ending import run_epilogue
        from engine.dm.opening import begin_play
        from engine.dm.turn import resume_narration

        first: Response | None = None
        kind = self._pending_kind()
        if kind == "narration":
            out = resume_narration(self.ctx)
            first = out.response if out is not None else None
            kind = self._pending_kind()
        if kind == "opening":
            first = self._merge(first, begin_play(self.ctx), keep_first_pause=False)
        elif kind == "ending":
            first = self._merge(first, run_epilogue(self.ctx), keep_first_pause=False)
        return first

    @staticmethod
    def _merge(first: Response | None, then: Response, *, keep_first_pause: bool = False) -> Response:
        """`first` (owed from an earlier step) shown before `then`; the earlier pause block is dropped when the
        later step answered or replaced it."""
        if first is None:
            return then
        blocks = list(first.oof_blocks)
        if first.pause is not None and not keep_first_pause and blocks:
            blocks = blocks[:-1]
        fiction = "\n\n".join(x for x in (first.fiction, then.fiction) if x)
        flags = Flags(fallback_used=first.flags.fallback_used or then.flags.fallback_used,
                      review_flag=first.flags.review_flag or then.flags.review_flag)
        return then.model_copy(update={"fiction": fiction, "oof_blocks": oof.ordered([*blocks, *then.oof_blocks]),
                                       "flags": flags, "scene_ended": first.scene_ended or then.scene_ended})


def _digest(ev: dict[str, Any]) -> str:
    """A short, stable hash of one event's JSON (sorted keys)."""
    import hashlib

    return hashlib.sha256(json.dumps(ev, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:20]


def _short(ev: dict[str, Any]) -> str:
    text = json.dumps({k: ev.get(k) for k in ("type", "turn_id", "source", "payload")}, sort_keys=True)
    return text if len(text) <= 240 else text[:237] + "..."


__all__ = ["Game", "GameConfig", "ReplayResult"]
