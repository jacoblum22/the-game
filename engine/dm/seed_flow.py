"""The world seed as a conversation (PR-12-9, 12.16; T064): one `seed_step` pause at a time.

    flow = SeedFlow(ctx)                 # ctx: engine.dm.context.TurnContext (store, rules, rng, model)
    resp = flow.start()                  # the mode question: guided / oracle / mixed (default mixed)
    resp = flow.submit("mixed")          # or flow.answer("mixed"); then (mixed) which questions to answer
    resp = flow.submit("2, 5")           # ... each question, each step's [SEED n/14] summary with keep / veto
    ...                                  # after the seed check the world is written and creation begins
    resp = SeedFlow(ctx).present()       # after a restart: exactly the open question, the world rebuilt

Everything the player says is a `seed_answered` event, and every question a `pause_opened` / `pause_closed` pair, so
the `WorldSeed` is rebuilt from the game's seed number and those events alone (`rebuild_seed`). Event `step` keys:
`ws.mode` (the mode), `ws.pick` (mixed: the questions the player answers), `ws.q.*` (an answer; choice None = handed
to the oracle), `ws.step.<n>` (step n ran: its answers, for the record), `ws.veto.<n>` (choice: the question
re-rolled), `ws.check` (step 14). Generator randomness is the seed number's own streams (engine.gen.world_seed).
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from engine import ids
from engine.dm import setup_text as T
from engine.dm.context import TurnContext
from engine.dm.response import Choice, OofBlock, Pause, Response
from engine.dm.roles.interpret import DETAILS, MOVE_ON, OWN_WORDS, SUGGEST, InterpretResult
from engine.dm.seed_recap import AUTO, recap, rolled
from engine.gen import _seed_steps as steps
from engine.gen._seed_lib import data as seed_data
from engine.gen.world_seed import (
    CHECK_STEP,
    LAST_STEP,
    ORACLE,
    SeededWorld,
    SeedStep,
    WorldSeed,
    questions,
    step_info,
)
from engine.store.db import Transaction
from engine.store.events import Event, PauseRecord
from engine.store.projection import WorldState

MODE, PICK, STEP, VETO, CHECK = "ws.mode", "ws.pick", "ws.step.", "ws.veto.", "ws.check"
DEFAULT_MODE = "mixed"
FLOW = "seed"
KEEP = "keep"
ALL = "all"
NONE_OPT = "none"
MULTI = {"ws.q.extra_impossible": 2, "ws.q.keepers": 4}  # questions answered with a list (12.16.5, 12.16.6)
# No closed list of options: the oracle always rolls these (the player may veto them at the step's summary).
# AUTO: never asked either (one possible answer, or a rules setting a new player cannot weigh; never vetoed).
UNASKED = ("ws.q.presence", "ws.q.terrain", *AUTO)
NO_VETO_STEPS = (10, 11)  # what these steps made is not shown, so a re-roll would mean nothing to the player
CARDS = ("12.16.2", "PR-12-9")
PHASE_KEY = "game.phase"


class SeedFlowError(RuntimeError):
    """An answer arrived with no seed question open."""


# ------------------------------------------------------------------------------------------- the questions


def _label(row: Any) -> str:
    if isinstance(row, dict):
        return str(row.get("text") or row.get("what") or row.get("id") or row.get("option") or row.get("org"))
    return str(row)


def question_options(qid: str, ws: WorldSeed | None = None) -> list[Choice]:  # rule: 12.16.2
    """A question's closed options in the rules' order (T-12-15), labelled with their text."""
    D = seed_data()
    q = D.QS[qid]
    out: list[Choice] = []
    if "options" in q:
        out = [Choice(id=str(o["id"] if isinstance(o, dict) else o), label=_label(o)) for o in q["options"]]
    elif qid == "ws.q.rulers":
        tier = (ws.st.get("tier") if ws is not None else None) or "village"
        out = [Choice(id=r["org"], label=_label(r)) for r in D.TAB["tbl.12.seed.rulers"]["by"][tier]]
    elif qid == "ws.q.fourth_faction":
        seen: list[str] = []
        for r in D.FAC["tbl.11.faction_seed"]["results"]:
            org = str(r["org"]).split(" ")[0]
            if org not in seen:
                seen.append(org)
        out = [Choice(id=o, label=o.split(".", 1)[-1].replace(".", ", ").replace("_", " ")) for o in seen]
    elif q.get("options_from") in D.TAB:
        out = [Choice(id=str(r["option"]), label=_label(r)) for r in D.TAB[q["options_from"]].get("results", [])
               if "option" in r]
    if qid == "ws.q.extra_impossible":
        out = [Choice(id=NONE_OPT, label="nothing else")] + out
    return out


def plain_options(qid: str, ws: WorldSeed | None = None) -> list[Choice]:
    """A question's options as the player reads them (engine/dm/text/setup.yaml), same ids and order."""
    tier = (ws.st.get("tier") if ws is not None else None) or "village"
    return [Choice(id=c.id, label=T.option_label(qid, c.id, c.label, tier)) for c in question_options(qid, ws)]


def askable(n: int | None = None) -> list[str]:
    """The questions a player may answer (all of T-12-15 but the two without closed options), in step order."""
    ns = range(1, LAST_STEP + 1) if n is None else [n]
    return [q["id"] for k in ns for q in questions(k) if q["id"] not in UNASKED]


def step_of(qid: str) -> int:
    return next(k for k, qs in steps.STEP_QUESTIONS.items() if qid in qs)


# ------------------------------------------------------------------------------------------- rebuild


def seed_ops(state: WorldState) -> list[dict[str, Any]]:
    """The replayable seed ops, in order (`ws.ran.*` records what a step rolled and is not replayed)."""
    return [a for a in state.seed_answers if str(a.get("step", "")).startswith("ws.")
            and not str(a["step"]).startswith("ws.ran.")]


def rebuild_seed(state: WorldState) -> WorldSeed | None:  # rule: PR-12-9
    """The WorldSeed exactly as the recorded answers, step runs and vetoes left it (None before the mode)."""
    ws: WorldSeed | None = None
    seed = state.game.seed if state.game else 0
    for op in seed_ops(state):
        ws = _apply_op(ws, op, seed)
    return ws


def _apply_op(ws: WorldSeed | None, op: dict[str, Any], seed: int) -> WorldSeed | None:
    key, choice = str(op["step"]), op.get("choice")
    if key == MODE:
        return WorldSeed.from_seed(seed, mode=choice if choice in ("guided", "oracle", "mixed") else DEFAULT_MODE)
    if ws is None or key == PICK:
        return ws
    if key.startswith("ws.q."):
        if ws.mode != "oracle":
            if choice is None:
                ws.answer(key, ORACLE)
            else:
                ws.answer(key, choice, words=op.get("words") if op.get("source") == "player_words" else None)
    elif key.startswith(STEP):
        ws.run_step()
    elif key.startswith(VETO):
        ws.veto(choice)
    elif key == CHECK:
        ws.run_check()
    return ws


def mixed_picks(state: WorldState) -> list[str] | None:
    picks = [op["choice"] for op in seed_ops(state) if op["step"] == PICK]
    return list(picks[-1]) if picks else None


# ------------------------------------------------------------------------------------------- the flow


def _ev_answer(step: str, choice: Any, source: str, words: str | None = None, rule: str = "12.16.2") -> Event:
    return Event.of("seed_answered", {"source": source}, source="player" if source.startswith("player") else "engine",
                    rule_id=rule, step=step, choice=choice, words=words)


def _meta(key: str, value: Any, rule: str) -> Event:
    return Event.of("meta_set", source="seed", rule_id=rule, key=key, value=value)


@contextmanager
def flow_tx(ctx: TurnContext) -> Iterator[Transaction]:
    """One transaction for one player answer (seed and creation have no turn id); sets `ctx.tx` for its length."""
    with ctx.store.transaction(None) as tx:
        ctx.tx = tx
        try:
            yield tx
        finally:
            ctx.tx = None


def open_pause(tx: Transaction, kind: str, prompt: str, choices: list[Choice], default: str | None,
               detail: dict[str, Any], rule: str) -> PauseRecord:  # rule: 12.2.6
    """Persist a pause (T109): what resume re-presents."""
    rec = PauseRecord(pause_id=tx.mint(ids.PAUSE), kind=kind, prompt=prompt,  # type: ignore[arg-type]
                      choices=[c.model_dump() for c in choices], default_choice=default, detail=detail)
    tx.add(Event.of("pause_opened", source="engine", rule_id=rule, pause=rec))
    return rec


def close_pause(tx: Transaction, rec: PauseRecord, choice: str | None, by: str, words: str | None = None) -> None:
    tx.add(Event.of("pause_closed", source="player", rule_id="12.2.6", pause_id=rec.pause_id, choice=choice, by=by,
                    words=words))


def present_pause(rec: PauseRecord, phase: str, extra: list[OofBlock] | None = None) -> Response:
    """The open pause as a Response: its stored blocks (the pause block last)."""
    blocks = [OofBlock.model_validate(b) for b in rec.detail.get("blocks", [])]
    return Response(phase=phase, oof_blocks=[*(extra or []), *blocks], pause=Pause.of(rec))  # type: ignore[arg-type]


def flow_of(state: WorldState) -> str | None:
    """Which conversation the open pause belongs to: "seed", "creation", or None (play)."""
    p = state.open_pause()
    return p.detail.get("flow") if p is not None else None


class SeedFlow:
    """PR-12-9 driven one pause at a time. Keeps a WorldSeed in memory and rebuilds it from events when needed."""

    def __init__(self, ctx: TurnContext):
        self.ctx = ctx
        self._ws: WorldSeed | None = None
        self._applied = -1  # seed ops folded into self._ws (-1: not built)

    # ---------------------------------------------------------------- public

    def start(self) -> Response:  # rule: PR-12-9
        """Step 1 of PR-12-9: ask the mode (or re-present whatever seed question is open)."""
        if self.ctx.store.state.open_pause() is not None or seed_ops(self.ctx.store.state):
            return self.present()
        return self._step(lambda tx: [])

    def present(self) -> Response:
        """Resume: exactly the open pause, as stored."""
        rec = self.ctx.store.state.open_pause()
        if rec is None:
            return self._step(lambda tx: [])
        return present_pause(rec, "creation" if rec.detail.get("flow") == "creation" else "seed")

    def submit(self, message: str) -> Response:
        """The player's words, answering the open seed question."""
        return self._answer(message=message)

    def answer(self, choice_id: str) -> Response:
        """Pick an option of the open pause by id (also `move_on`, `details`, `suggest`)."""
        return self._answer(choice_id=choice_id)

    def seed(self) -> WorldSeed | None:
        """The WorldSeed as the record left it."""
        state = self.ctx.store.state
        ops = seed_ops(state)
        if self._applied != len(ops):
            self._ws = rebuild_seed(state)
            self._applied = len(ops)
        return self._ws

    # ---------------------------------------------------------------- internals

    def _op(self, tx: Transaction, ev: Event) -> None:
        """Record one seed op and fold it into the in-memory WorldSeed."""
        tx.add(ev)
        p = ev.payload
        op = {"step": p.step, "choice": p.choice, "source": p.source, "words": p.words}  # type: ignore[attr-defined]
        seed = tx.state.game.seed if tx.state.game else 0
        self._ws = _apply_op(self._ws, op, seed)
        self._applied += 1

    def _step(self, handle: Any) -> Response:
        self.seed()
        try:
            with flow_tx(self.ctx) as tx:
                blocks: list[OofBlock] = list(handle(tx) or [])
                return self._advance(tx, blocks)
        except BaseException:
            self._ws, self._applied = None, -1
            raise

    def _answer(self, *, message: str | None = None, choice_id: str | None = None) -> Response:
        rec = self.ctx.store.state.open_pause()
        if rec is None or rec.detail.get("flow") != FLOW:
            raise SeedFlowError("no seed question is open")
        stage = rec.detail.get("stage")
        choices = [Choice(id=c["id"], label=c.get("label", c["id"])) for c in rec.choices]
        self.seed()
        if choice_id is not None:
            res = InterpretResult(choice=choice_id, picks=[choice_id] if any(c.id == choice_id for c in choices) else [],
                                  direct=True)
        else:
            qid = rec.detail.get("question")
            classes = [c.id for c in choices] if stage == "question" else []
            res = T.read_answer(self.ctx, message or "", rec, tag="[SEED]", classes=classes, cards=CARDS,
                                multi=stage == "pick" or qid in MULTI)
        if res.choice == DETAILS:
            return present_pause(rec, "seed", [OofBlock(kind="NOTE", text=_details(rec))])
        words = res.own_words_text or (message if res.choice == OWN_WORDS else None)

        def handle(tx: Transaction) -> list[OofBlock]:
            if stage == "mode":
                return self._on_mode(tx, rec, res, words)
            if stage == "pick":
                return self._on_pick(tx, rec, res, words)
            if stage == "summary":
                return self._on_summary(tx, rec, res)
            return self._on_question(tx, rec, res, words, message)

        return self._step(handle)

    def _on_mode(self, tx: Transaction, rec: PauseRecord, res: InterpretResult, words: str | None) -> list[OofBlock]:
        modes = [c["id"] for c in rec.choices]
        mode = res.choice if res.choice in modes else (res.own_words_class if res.own_words_class in modes else None)
        src = "player_option" if mode else "default"
        mode = mode or DEFAULT_MODE
        close_pause(tx, rec, mode, "option" if src == "player_option" else "default", words)
        tx.add(_meta(PHASE_KEY, "seed", "PR-12-9"))
        self._op(tx, _ev_answer(MODE, mode, src, words, rule="PR-12-9"))
        return []

    def _on_pick(self, tx: Transaction, rec: PauseRecord, res: InterpretResult, words: str | None) -> list[OofBlock]:
        qids = [c["id"] for c in rec.choices if c["id"] != ALL]
        if ALL in res.picks or res.choice == ALL:
            picks = qids
        else:
            picks = [p for p in res.picks if p in qids]
        src = "player_option" if picks else "default"
        close_pause(tx, rec, ",".join(picks) or None, "option" if picks else "default", words)
        self._op(tx, _ev_answer(PICK, picks, src, words, rule="PR-12-9"))
        return []

    def _on_summary(self, tx: Transaction, rec: PauseRecord, res: InterpretResult) -> list[OofBlock]:
        n = int(rec.detail["step"])
        choice = res.choice if any(c["id"] == res.choice for c in rec.choices) else KEEP
        close_pause(tx, rec, choice, "option" if choice == res.choice else "default")
        if choice == KEEP:
            return []
        question = choice.split(":", 1)[1] if ":" in choice else None
        self._op(tx, _ev_answer(f"{VETO}{n:d}", question, "player_option"))
        assert self._ws is not None
        step = self._ws.history[-1]
        self._op_run_record(tx, step)
        return [OofBlock(kind="SEED", text=self._recap(step) + "\n  " + str(T.seed("summary", "rerolled")))]

    def _on_question(self, tx: Transaction, rec: PauseRecord, res: InterpretResult, words: str | None,
                     message: str | None) -> list[OofBlock]:  # rule: 12.16.2
        qid = str(rec.detail["question"])
        opts = [c["id"] for c in rec.choices]
        value: Any = None
        if res.choice in opts:
            value, src = (res.picks or [res.choice]), "player_option"
        elif res.choice == OWN_WORDS and res.own_words_class in opts:
            value, src = [res.own_words_class], "player_words"
        else:
            src = "oracle_roll" if res.choice == SUGGEST else "default"
        if value is not None and qid not in MULTI:
            value = value[0]
        notes: list[OofBlock] = []
        if value is not None and qid in MULTI:
            value = self._complete_multi(tx, qid, list(value))
        by = {"player_option": "option", "player_words": "own_words"}.get(src, "default")
        close_pause(tx, rec, value if isinstance(value, str) else (",".join(value) if value is not None else None),
                    by, words if src == "player_words" else None)
        self._op(tx, _ev_answer(qid, value, src, words if src == "player_words" else None))
        if value is None and res.choice == SUGGEST:
            notes.append(OofBlock(kind="NOTE", text=str(T.seed("suggest_note"))))
        return notes

    def _complete_multi(self, tx: Transaction, qid: str, picks: list[str]) -> list[str]:
        """# rule: 12.16.2 -- supplied content is written as given, then completed by the step's rules."""
        if qid == "ws.q.extra_impossible":
            return [] if NONE_OPT in picks else picks[: MULTI[qid]]
        ws = self._ws
        assert ws is not None
        nk_given = ws.given.get("ws.q.keeper_count")
        nk = int(nk_given) if nk_given is not None else max(2, min(4, len(picks)))
        if nk_given is None:
            self._op(tx, _ev_answer("ws.q.keeper_count", str(nk), "player_option",
                                    rule="12.16.6"))
        chosen = picks[:nk]
        bias = ws.st["wound"]["keeper_bias"]
        forms = [r["option"] for r in seed_data().TAB["tbl.12.seed.keeper_form"]["results"]]
        while len(chosen) < nk:
            left = {f: (3 if f in bias else 1) for f in forms if f not in chosen}
            chosen.append(str(self.ctx.rng.weighted(left, "seed.keepers.complete")))
        return chosen

    def _op_run_record(self, tx: Transaction, step: SeedStep) -> None:
        """A step ran (or re-ran after a veto): its answers go on the record (not replayed: re-derived)."""
        tx.add(Event.of("seed_answered", {"source": "oracle_roll"}, source="engine", rule_id=step.rule,
                        step=f"ws.ran.{step.n:d}", choice=[a.model_dump() for a in step.answers], words=None))

    # ---------------------------------------------------------------- what comes next

    def _advance(self, tx: Transaction, blocks: list[OofBlock]) -> Response:  # rule: PR-12-9
        while True:
            ws = self._ws
            if ws is None:
                return self._ask_mode(tx, blocks)
            if ws.mode == "mixed" and mixed_picks(tx.state) is None:
                return self._ask_pick(tx, blocks)
            if ws.next_step <= LAST_STEP:
                q = self._next_question(tx.state, ws)
                if q is not None:
                    return self._ask_question(tx, blocks, ws, q)
                if self._handed_unasked(tx, ws):
                    continue
                self._op(tx, _ev_answer(f"{STEP}{ws.next_step:d}", None, "oracle_roll", rule="PR-12-9"))
                step = ws.history[-1]
                self._op_run_record(tx, step)
                vetoes = self._veto_choices(ws, step)
                if vetoes:
                    return self._ask_summary(tx, blocks, step, vetoes)
                blocks.append(OofBlock(kind="SEED", text=self._recap(step)))
                continue
            return self._finish(tx, ws, blocks)

    def _handed_unasked(self, tx: Transaction, ws: WorldSeed) -> bool:
        """Guided mode: questions with no closed options are handed to the oracle (recorded)."""
        if ws.mode != "guided":
            return False
        left = [q for q in ws.missing() if q in UNASKED]
        for q in left:
            self._op(tx, _ev_answer(q, None, "oracle_roll"))
        return bool(left)

    def _next_question(self, state: WorldState, ws: WorldSeed) -> str | None:
        if ws.mode == "oracle":
            return None
        wanted = askable(ws.next_step)
        if ws.mode == "mixed":
            picks = mixed_picks(state) or []
            wanted = [q for q in wanted if q in picks]
        return next((q for q in wanted if q not in ws.given and q not in ws.sources), None)

    def _veto_choices(self, ws: WorldSeed, step: SeedStep) -> list[Choice]:  # rule: 12.16.2
        """keep, then one veto per rolled answer (or the whole step when it asks nothing); none once vetoed, none
        for an auto-taken answer, none for a step whose result is not shown."""
        if step.n in ws._vetoed or step.n in NO_VETO_STEPS:  # noqa: SLF001 -- no accessor for the veto set
            return []
        reroll = str(T.seed("summary", "reroll"))
        if steps.STEP_QUESTIONS.get(step.n):
            opts = [Choice(id=f"veto:{a.question}", label=reroll.format(what=T.question_what(a.question)))
                    for a in rolled(step)]
        else:
            opts = [Choice(id="veto", label=str(T.seed("summary", "reroll_step")))]
        return [Choice(id=KEEP, label=str(T.seed("summary", "keep"))), *opts] if opts else []

    def _recap(self, step: SeedStep) -> str:
        """The step's plain recap under its header (the rules' summary stays on SeedStep.summary)."""
        ws = self._ws
        assert ws is not None
        lines = recap(step, ws.st, ws.words)
        return "\n".join([T.seed_header(step.n, step.name), *(f"  {x}" for x in lines)])

    # ---------------------------------------------------------------- pauses

    def _pause(self, tx: Transaction, blocks: list[OofBlock], block: str, prompt: str, choices: list[Choice],
               default: str | None, detail: dict[str, Any], orig: dict[str, str] | None = None) -> Response:
        own = [OofBlock(kind="SEED", text=block)]
        if orig:
            detail = {**detail, "orig": T.originals(choices, orig)}
        detail = {"flow": FLOW, **detail, "blocks": [b.model_dump() for b in own]}
        rec = open_pause(tx, "seed_step", prompt, choices, default, detail, "PR-12-9")
        return Response(phase="seed", oof_blocks=[*blocks, *own], pause=Pause.of(rec))

    def _ask_mode(self, tx: Transaction, blocks: list[OofBlock]) -> Response:  # rule: 12.16.2
        rules_text = {str(m["id"]): str(m["text"]) for m in seed_data().WS["modes"]}
        modes = [Choice(id=i, label=str(T.seed("mode", "options", i) or t)) for i, t in rules_text.items()]
        prompt = str(T.seed("mode", "prompt"))
        block = T.pause_block(str(T.seed("mode", "header")), prompt, [], modes,
                              T.footer("number", str(T.seed("mode", "enter"))))
        return self._pause(tx, blocks, block, prompt, modes, DEFAULT_MODE, {"stage": "mode"}, rules_text)

    def _ask_pick(self, tx: Transaction, blocks: list[OofBlock]) -> Response:  # rule: PR-12-9
        asks = {q: str(seed_data().QS[q]["ask"]) for q in askable()}
        qs = [Choice(id=q, label=T.question_pick(q, a)) for q, a in asks.items()]
        qs.append(Choice(id=ALL, label=str(T.seed("pick", "all"))))
        prompt = str(T.seed("pick", "prompt"))
        block = T.pause_block(str(T.seed("pick", "header")), prompt, [], qs, str(T.seed("pick", "footer")))
        return self._pause(tx, blocks, block, prompt, qs, MOVE_ON, {"stage": "pick"}, asks)

    def _ask_question(self, tx: Transaction, blocks: list[OofBlock], ws: WorldSeed, qid: str) -> Response:
        q = seed_data().QS[qid]
        opts = plain_options(qid, ws)
        n = step_of(qid)
        prompt = T.question_prompt(qid, str(q["ask"]))
        block = T.pause_block(T.seed_header(n, step_info(n)["name"]), prompt, [], opts,
                              T.footer("pick_many" if qid in MULTI else "pick", T.dice()))
        orig = {c.id: c.label for c in question_options(qid, ws)}
        return self._pause(tx, blocks, block, prompt, opts, MOVE_ON, {"stage": "question", "question": qid,
                                                                      "step": n}, orig)

    def _ask_summary(self, tx: Transaction, blocks: list[OofBlock], step: SeedStep, vetoes: list[Choice]) -> Response:
        prompt = str(T.seed("summary", "prompt"))
        block = T.pause_block(self._recap(step), prompt, [], vetoes,
                              T.footer("number", str(T.seed("summary", "enter"))))
        return self._pause(tx, blocks, block, prompt, vetoes, KEEP, {"stage": "summary", "step": step.n})

    # ---------------------------------------------------------------- the end of the seed

    def _finish(self, tx: Transaction, ws: WorldSeed, blocks: list[OofBlock]) -> Response:  # rule: PR-12-9
        """Step 4 (the seed check) and step 5 (hand over to creation)."""
        self._op(tx, _ev_answer(CHECK, None, "oracle_roll", rule="12.16.17"))
        world = ws.world()
        reran = any(h.n == CHECK_STEP for h in ws.history)
        lines = ([str(T.seed("check", "rerun"))] if reran else []) + \
            [str(T.seed("check", "ok")).format(region=world.region.name)]
        head = str(T.seed("header")).format(n=CHECK_STEP, title=T.seed("check", "title"))
        blocks.append(OofBlock(kind="SEED", text="\n".join([head, *(f"  {x}" for x in lines)])))
        write_world(tx, world)
        from engine.dm.creation import open_creation  # creation reads the seeded world; imported late

        return open_creation(self.ctx, blocks)


def write_world(tx: Transaction, world: SeededWorld) -> None:  # rule: 12.16.1
    """The seeded world into the store (engine.world.places writes places, routes, factions, clocks, threads and the
    cast) plus what creation and the opening read: tongues, peoples, pregens, the opening, canon."""
    from engine.world.places import seed_world_into_store

    seed_world_into_store(tx, world)
    rec = world.record
    tx.add_all([
        _meta("world.seed", {"seed": world.seed, "mode": world.mode, "region": world.region.model_dump(),
                             "check": [c.model_dump() for c in world.check]}, "12.16.1"),
        _meta("world.tongues", rec.get("tongues", {}), "12.16.7"),
        _meta("world.pregens", rec.get("pregens", []), "12.16.16"),
        _meta("world.opening", rec.get("opening", {}), "12.16.16"),
        _meta("world.canon_impossible", rec.get("canon_impossible", []), "12.16.5"),
        _meta("world.keepers", [{k: v for k, v in kp.items() if k in ("id", "name", "title", "what", "nature")}
                                for kp in rec.get("keepers", [])], "12.16.6"),
        _meta(PHASE_KEY, "creation", "PR-12-9"),
    ])


# ------------------------------------------------------------------------------------------- rendering


def _details(rec: PauseRecord) -> str:
    """'details': each option with the rules' fuller wording beside it, and the question's note when the rules give
    one."""
    qid = rec.detail.get("question")
    orig = dict(rec.detail.get("orig") or {})
    lines = [str(T.seed("details_head"))]
    lines += [f"{i + 1}. {c['label']}" + (f" ({orig[c['id']]})" if orig.get(c["id"]) else "")
              for i, c in enumerate(rec.choices)]
    if qid:
        note = seed_data().QS[qid].get("note")
        if note:
            lines.append(f"Note: {note}")
    if rec.detail.get("stage") == "mode":
        lines.append("When the dice decide, you may re-roll one result per step, once.")
    return "\n".join(lines)
