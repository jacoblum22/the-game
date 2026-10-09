"""The resolution pipeline driver (PR-01-1): PARSE → GATE → NECESSITY → ANCHOR → FRAME → OFFER → ROLL → READ →
DELIVER → CONSEQUENCE → RECORD, per beat, at most three beats per declaration, stopping at the first pause.

    env = PipelineEnv(tx=tx, rules=rules, rng=rng, store=store, framer=framer, pc="pc.wren", auto_commit=False)
    res = run_beats(env, [BeatPlan(beat=beat, intent_verbs=["sneak"])])     # the Reader's beats (PARSE done)
    res.pause                              # the open pause (stored with `pause_opened`), or None
    res = resume(env, state.open_pause(), "commit")           # PENDING_ANSWER: continue the same beat
    res = close_by_default(env, state.open_pause())           # a new declaration arrived (12.2.6 defaults)

PARSE is the Reader's (engine/dm/roles/reader.py); FRAME's proposal is the Framer's, injected as `framer` (the dm
side re-asks once naming a `frame_check` refusal, then uses the rule's default frame). Everything else is code:
the gate, the frame, the OFFER, the roll, the read, the cost, the records. A pause stores everything the beat needs
to continue in `PauseRecord.detail`, so a resumed game (a new process) continues the same beat exactly.

Pause stages (`detail["stage"]`): `offer` (commit / change / withdraw / go_big / play_safe), `warning` (an OFFER
pause carrying the lethal warning before a lethal frame: continue / withdraw), `near_miss` (failure /
success_at_cost:<menu>), `redirect` (accept:<license> / other), `clarify` (free words only).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

from engine import ids
from engine.dm.adjudication import BeatEntry, CostEntry, HarmEntry, PositionEntry
from engine.resolve.change import ChangeResult, apply_change, plain
from engine.resolve.costs import HarmHook, apply_cost, check_cost_decl, first_fitting_cost
from engine.resolve.frame import auto_commit_allowed, commit_events, frame_check, offer_preview
from engine.resolve.gate import GateDecision, check_gate, words, zero_reach
from engine.resolve.necessity import necessity, trivial_class
from engine.resolve.roll import read_result, roll_check
from engine.resolve.rulings import RulingRecord, log_ruling
from engine.resolve.types import REACH_VALUE, Beat, Frame, FrameRefusal, ProposedFrame, ReadResult, RollResult
from engine.retrieve.anchors import anchor_candidates, verb_anchor
from engine.store.events import Event, PauseRecord
from engine.time.scheduler import TimeContext, advance_time, mark_boundary

MAX_BEATS = 3  # 01.2.3
ROLLS = "uncertain_and_costly"
MOVE = "verb.move"
NO_ROLL_EVIDENCE = ("good_idea", "take_the_time", "certain_with_cost")  # 03.3.1 bases without a degree
TRADE_IDS = {"go_big": "go_big", "play_it_safe": "play_safe"}  # Frame trade -> Pause choice id
REACH_NAME = {v: k for k, v in REACH_VALUE.items()}
Status = Literal["resolved", "no_roll", "redirected", "refused", "paused", "withdrawn", "question", "queued"]


class BeatPlan(BaseModel):
    """One parsed beat (PARSE done by the Reader) and its anchor lookup keys."""

    beat: Beat
    intent_verbs: list[str] = Field(default_factory=list)
    when: str = "now"  # 12.2.2 shape: now, conditional (on an earlier result) or queued (a Ready beat) (spec 017)

    def lookup(self) -> dict[str, Any]:
        return {**self.beat.model_dump(), "intent_verbs": self.intent_verbs}


class FramerFn(Protocol):
    """The Framer role (engine/dm/roles/framer.py): a proposal `frame_check` accepts, or the rule's default."""

    def __call__(self, beat: Beat, candidates: list[str], *, gate: GateDecision,
                 note: str | None = None) -> ProposedFrame: ...


@dataclass
class LethalWarning:
    source: str
    block: str  # the [WARNING] block (T-07-7)
    events: list[Event]


class LethalCheck(Protocol):
    """07.3.3 / PR-07-4: the warning due before this beat's frame, with its writes, or None."""

    def __call__(self, env: PipelineEnv, beat: Beat, frame: Frame | None) -> LethalWarning | None: ...


@dataclass
class PipelineEnv:
    tx: Any  # engine.store.db.Transaction
    rules: Any
    rng: Any
    store: Any
    framer: FramerFn
    pc: str
    auto_commit: bool = False
    harm_hook: HarmHook | None = None
    lethal: LethalCheck | None = None  # default: harm_lethal_warning (engine/harm/lethal.py)
    milestone: int = 0
    harm_log: list[HarmEntry] = field(default_factory=list)  # filled by the harm hook for the record
    threshold_due: list[str] = field(default_factory=list)  # PCs whose harm opened the Threshold (07.5)
    said: list[str] = field(default_factory=list)  # the message's SPEECH parts, carried by a pause (spec 017)
    said_first: list[str] = field(default_factory=list)  # those said before a later declaration: answered here

    @property
    def state(self) -> Any:
        return self.tx.state

    def time_ctx(self) -> TimeContext:
        return TimeContext(self.tx, self.rules, self.rng, milestone=self.milestone)

    def add(self, *events: Event) -> list[int]:
        return self.tx.add_all(events)


class BeatOutcome(BaseModel):
    status: Status
    entry: BeatEntry
    frame_id: str | None = None
    oof: list[dict[str, str]] = Field(default_factory=list)  # {kind, text} (12.15 blocks the record owes)


class PipelineResult(BaseModel):
    outcomes: list[BeatOutcome] = Field(default_factory=list)
    pause: PauseRecord | None = None
    queued: list[str] = Field(default_factory=list)  # beats not attempted, restated (a Threshold voids the rest)
    said: list[str] = Field(default_factory=list)  # SPEECH a closed pause carried: the record answers it (spec 017)

    def extend(self, other: PipelineResult) -> PipelineResult:
        self.outcomes += other.outcomes
        self.pause = other.pause
        self.queued += other.queued
        return self


# ------------------------------------------------------------------------------------------- driver


def run_beats(env: PipelineEnv, plans: list[BeatPlan], *, prev: BeatOutcome | None = None,
              ran: int = 0, here: set[str] | None = None) -> PipelineResult:
    # rule: PR-01-1
    """Run the message's plan in the player's order; stop at the first pause (the rest of the plan waits in its
    detail). Before each beat `_recheck` may ask "Still go on to …?" instead (01.2.3, 01.14.4; spec 017). `prev`:
    the beat a resumed pause just resolved; `ran`: beats already resolved this turn; `here`: the plan's targets
    able before it (`_able`)."""
    res = PipelineResult()
    todo = list(plans)
    here = _able(env, todo) if here is None else here
    while todo:
        why = _recheck(env, todo[0], prev, ran, here)
        if why == VOID:  # 07.5: the last-chance menu is the question; the rest is said, not attempted
            res.queued = [p.beat.method or p.beat.restatement for p in todo]
            return res
        if why is not None:
            _ask(env, why, todo)
            res.pause = env.state.open_pause()
            return res
        plan = todo.pop(0)
        out = _start(env, plan, todo)
        res.outcomes.append(out)
        prev, ran = out, ran + 1
        if out.status == "paused":
            res.pause = env.state.open_pause()
            return res
    return res


VOID = "void"
SUCCESS = ("success", "critical_success")


def _able(env: PipelineEnv, plans: list[BeatPlan]) -> set[str]:
    """The plan's targets that are creatures able to act and here now (06.13.1's `able`)."""
    from engine.resolve.conflict import able

    st = env.state
    out = set()
    for p in plans:
        ent = st.entities.get(p.beat.target or "")
        if ent is not None and ent.kind in _CREATURES and able(st, ent.id):
            out.add(ent.id)
    return out


def _recheck(env: PipelineEnv, plan: BeatPlan, prev: BeatOutcome | None, ran: int, here: set[str]) -> str | None:
    # rule: 01.2.3, 01.14.4
    """Whether the next beat of the plan still runs as declared: None (run it), the line said before "Still go on
    to …?" ("" for none), or VOID (a Threshold opened)."""
    from engine.harm.state import is_down
    from engine.resolve.conflict import able

    st, beat = env.state, plan.beat
    if env.pc in env.threshold_due:
        return VOID
    if ran >= MAX_BEATS:  # 01.2.3: the rest is confirmed, never run past a decision point
        return "That is three actions this turn."
    if env.said_first and _leaves(env, beat):  # the words said here are answered here first
        return ""
    if prev is None:
        return None
    if env.pc and is_down(st, env.pc):
        return "You are down."
    if beat.target in here and not able(st, str(beat.target)):
        from engine.store.views import display_name

        return f"{display_name(st, str(beat.target))} is down or gone."
    if prev.status in ("withdrawn", "refused"):
        return "That did not happen."
    done = prev.status == "no_roll" or (prev.status == "resolved" and (prev.entry.degree in SUCCESS
                                                                         or prev.entry.success_at_cost))
    if plan.when == "conditional" and not done:  # 01.14.4: what it waited on may not be true
        return "That did not work."
    return None


def _leaves(env: PipelineEnv, beat: Beat) -> bool:  # rule: PR-06-4
    """A beat that takes its actor to a place that is not here (travel: the scene cuts to it)."""
    st = env.state
    pos = st.positions.get(beat.actor)
    here = (pos.location if pos else None) or (st.scene.place_id if st.scene else None)
    c = beat.change
    to = c.what if c is not None and c.kind == "move_to" else beat.target if beat.verb == MOVE else None
    ent = st.entities.get(to or "")
    return ent is not None and ent.kind == "place" and to != here


def _ask(env: PipelineEnv, why: str, todo: list[BeatPlan]) -> PauseRecord:  # rule: 01.2.3
    """The plan pause: one line, "Still go on to <act>?", before the next beat (kind offer: a new declaration
    withdraws it, 12.2.6). It falls between beats, so T5 still runs for what resolved (spec 017)."""
    act = todo[0].beat.method or todo[0].beat.restatement or todo[0].beat.intent
    act = act[:1].lower() + act[1:]
    prompt = f"{why} Still go on to {act.rstrip('.')}?".strip()
    choices = [{"id": "continue", "label": f"Go on: {act}"}, {"id": "withdraw", "label": "Stop here"}]
    return _open(env, "offer", prompt, choices, "withdraw", {"stage": "plan", "queued": _dump(todo)})


def own_line(restatement: str, act: str, *, alone: bool = True) -> str:  # rule: 01.2.2
    """The restatement's clause for one beat ("A. Then: B. Then: C"): the clause sharing the most content words with
    the beat's own act (its method and intent); a tie goes to the first; "" when none shares a word, or when the
    restatement is one clause and the beat is not `alone` (it speaks for every beat: P-064). Fighter turn 11:
    "Sheathe the sword." titled a Force on the door. Spec 017."""
    clauses = [c.strip(" ,:\n") for c in _THEN.split(restatement or "") if c.strip(" ,:\n")]
    if len(clauses) <= 1:
        return clauses[0] if clauses and alone else ""
    want = words(act)
    best = max(range(len(clauses)), key=lambda i: (len(words(clauses[i]) & want), -i))
    if not words(clauses[best]) & want:
        return ""
    line = clauses[best]
    return line[:1].upper() + line[1:]


_THEN = re.compile(r"(?:(?<=[.!?;])\s+|\n\s*)Then\b:?")


def resume(env: PipelineEnv, pause: PauseRecord, choice: str, *, by: str = "option",
           words: str | None = None) -> PipelineResult:  # rule: 12.2.6
    """Answer the open pause and continue the same beat from the stored frame, then the rest of the plan."""
    d = pause.detail
    env.add(Event.of("pause_closed", source="player", rule_id="12.2.6", pause_id=pause.pause_id, choice=choice,
                     by=by, words=words))
    stage = d.get("stage")
    env.said, env.said_first = list(d.get("said") or []), list(d.get("said_first") or [])
    carried = PipelineResult(said=list(env.said))
    if stage not in ("offer", "warning", "near_miss", "redirect", "plan"):  # clarify: the Reader re-reads the words
        return carried
    queued = [BeatPlan.model_validate(q) for q in d.get("queued", [])]
    here = _able(env, queued)  # before the paused beat lands: a target it downs is then "down or gone"
    if stage == "plan":  # rule: 01.2.3
        return carried.extend(_plan_answer(env, choice, queued, here))
    plan = BeatPlan.model_validate(d["plan"])
    if stage == "offer":
        out = _answer_offer(env, plan, d, choice, queued)
    elif stage == "warning":
        out = _answer_warning(env, plan, d, choice, queued)
    elif stage == "near_miss":
        frame = Frame.model_validate(d["frame"])
        roll = RollResult.model_validate(d["roll"])
        sac = choice.startswith("success_at_cost")
        menu = choice.split(":", 1)[1] if ":" in choice else None
        out = _finish(env, plan, frame, roll, take_sac=sac, menu=menu)
    else:
        out = _answer_redirect(env, plan, d, choice, queued)
    carried.outcomes = [out]
    if out.status == "paused":
        carried.pause = env.state.open_pause()
        return carried
    # the plan goes on with its next beat (a withdrawn one asks first: `_recheck`)
    return carried.extend(run_beats(env, queued, prev=out, ran=1, here=here))


def _plan_answer(env: PipelineEnv, choice: str, queued: list[BeatPlan], here: set[str]) -> PipelineResult:
    # rule: 01.2.3
    """The plan pause answered: go on with the next beat (the player confirmed it), or stop (said, not run)."""
    if choice != "continue" or not queued:
        return PipelineResult(queued=[p.beat.method or p.beat.restatement for p in queued])
    first = _start(env, queued[0], queued[1:])
    res = PipelineResult(outcomes=[first])
    if first.status == "paused":
        res.pause = env.state.open_pause()
        return res
    return res.extend(run_beats(env, queued[1:], prev=first, ran=1, here=here))


def close_by_default(env: PipelineEnv, pause: PauseRecord) -> PipelineResult:  # rule: 12.2.6
    """A new declaration while a pause is open: OFFER withdrawn (nothing spent), near miss → failure, redirect →
    the player chose another way. Queued beats of the old declaration are dropped (the new one replaces them); the
    words it carried are still answered (`said`, spec 017)."""
    stage = pause.detail.get("stage")
    if stage == "near_miss":
        pause.detail["queued"] = []
        return resume(env, pause, "failure", by="default")
    env.add(Event.of("pause_closed", source="engine", rule_id="12.2.6", pause_id=pause.pause_id,
                     choice=pause.default_choice, by="withdrawn" if stage in ("offer", "warning") else "default"))
    if stage in ("offer", "warning"):
        env.add(Event.of("offer_logged", source="engine", rule_id="01.7.1", frame_id=None,
                         shown_at=env.state.time.now, choice="withdraw"))
    return PipelineResult(said=list(pause.detail.get("said") or []))


# ------------------------------------------------------------------------------------------- GATE … FRAME


def _entry(beat: Beat, **kw: Any) -> BeatEntry:
    targets = [beat.target] if beat.target and beat.target != "none" else []
    return BeatEntry(beat_id=beat.id, actor=beat.actor, targets=targets, verb=beat.verb,
                     restatement=beat.restatement or beat.intent, license=beat.license, **kw)


def _start(env: PipelineEnv, plan: BeatPlan, queued: list[BeatPlan]) -> BeatOutcome:  # rule: PR-01-1
    beat = plan.beat
    tx = env.tx
    # 2. GATE (01.3)
    dec = check_gate(beat, state=env.state, rules=env.rules, store=env.store, staged=tx.events, mint=tx.mint)
    env.add(*dec.events)
    if dec.gate == "G0":
        return BeatOutcome(status="question", entry=_entry(beat, gate="G0", gate_words=dec.reason))
    if dec.gate == "G4":  # refused with an alternative; nothing spent (01.3.7)
        return _refused(beat, dec, "G4")
    if dec.gate == "G3" and not dec.rolls_possible:
        return _redirect(env, plan, dec, queued)
    # 3. NECESSITY (01.4.1, computed): a certain or plainly trivial beat skips the Framer
    beat.necessity = necessity(beat, dec, state=env.state, rules=env.rules)
    if beat.necessity != ROLLS:
        return _no_roll(env, plan, dec)
    # 4-5. ANCHOR and FRAME
    return _frame(env, plan, dec, queued)


def decision_json(dec: GateDecision) -> str:
    """The GateDecision the REDIRECT block is rendered from (engine.dm.oof.redirect_block), JSON."""
    return dec.model_dump_json(exclude={"events", "precedent"})


def _refused(beat: Beat, dec: GateDecision, gate: str) -> BeatOutcome:  # rule: 01.3.6
    red = dec.redirect
    options = [o.method for o in red.options] if red else []
    words = f"{dec.reason}. Possible now: {'; '.join(options)}" if options else dec.reason
    if red and red.acquisition_paths:
        words += ". To gain it: " + "; ".join(str(p.get("detail") or p.get("type")) for p in red.acquisition_paths)
    return BeatOutcome(status="refused", entry=_entry(beat, gate=gate, gate_words=words),
                       oof=[{"kind": "REDIRECT", "text": words, "decision": decision_json(dec)}])


def _redirect(env: PipelineEnv, plan: BeatPlan, dec: GateDecision, queued: list[BeatPlan]) -> BeatOutcome:
    # rule: 01.3.6
    """G3: a crude fallback is a pause (accept it or choose another way); with none, a refusal with options."""
    red = dec.redirect
    fallback = next((o for o in red.options if o.kind == "fallback" and o.license), None) if red else None
    if fallback is None:
        return _refused(plan.beat, dec, "G3")
    assert red is not None
    words = (f"Without {red.missing} this is beyond you as tried. Possible now: {fallback.method}"
             + (f" (harder, at most {fallback.reach_cap} reach)" if fallback.reach_cap else ""))
    choices = [{"id": f"accept:{fallback.license}", "label": f"Try it anyway: {fallback.method}"},
               {"id": "other", "label": "Do something else"}]
    detail = {"stage": "redirect", "plan": plan.model_dump(mode="json"), "queued": _dump(queued),
              "fallback": fallback.model_dump(mode="json"), "missing": red.missing,
              "decision": dec.model_dump(mode="json", exclude={"events", "precedent"})}
    _open(env, "redirect", words, choices, "other", detail)
    return BeatOutcome(status="paused", entry=_entry(plan.beat, gate="G3", gate_words=words),
                       oof=[{"kind": "REDIRECT", "text": words, "decision": decision_json(dec)}])


def _no_roll(env: PipelineEnv, plan: BeatPlan, dec: GateDecision) -> BeatOutcome:  # rule: 01.4.1
    """A no-roll class: the beat succeeds at Standard reach (never Great, never lethal), recorded; evidence only
    for resolved bases (good idea, take the time, certain with cost; 03.3.1)."""
    beat = plan.beat
    entry = _entry(beat, gate=dec.gate, gate_words=f"no roll: {beat.necessity}", reach="standard",
                   approach_words=(dec.verb or beat.verb or "") if dec.gate != "G2" else (dec.license or ""))
    evs: list[Event] = []
    if beat.necessity in NO_ROLL_EVIDENCE:
        tag = beat.deed_tag or _verb_deed(env.rules, beat.verb)
        if tag:
            evs.append(evidence_event(env, beat, tag, frame=None, degree="success"))
        if beat.necessity == "good_idea":  # rule: 01.5.4
            evs.append(log_ruling(RulingRecord(signature=f"good_idea:{beat.verb or beat.license}",
                                               situation=beat.restatement or beat.intent, kind="good_idea",
                                               result={"degree": None, "outcome": "success (good idea)"}),
                                  env.tx.mint, store=env.store, staged=env.tx.events, rule_id="01.5.4"))
    env.add(*evs)
    if (dec.verb or beat.verb) == MOVE:
        entry.positions = _moved(env, plan)
    _change_entry(env, beat, entry, apply_change(env.tx, env.rules, beat, 2, pc=env.pc))  # rule: 01.2.7
    mark_boundary(env.time_ctx(), "beat_end", {"beat": beat.id})
    return BeatOutcome(status="no_roll", entry=entry)


BANDS = ("engaged", "close", "near", "far", "distant")  # 06.3.2, nearest first
_BAND_WORDS = {"engaged": "at arm's reach of", "close": "a few strides from", "near": "a stone's throw from",
               "far": "a long bowshot from", "distant": "at the edge of sight of"}  # T-12-11
_AWAY = {"withdraw", "retreat", "flee", "away", "back", "leave"}


def _moved(env: PipelineEnv, plan: BeatPlan) -> list[PositionEntry]:  # rule: PR-06-4
    """A resolved Move writes where it took the mover: one band step toward (or away from) its target in the
    scene, in both directions, at the mover's place. A place that is not here is travel: the scene cut moves the
    PC there (12.4.2, 10.1.3), so nothing is written here."""
    # ponytail: one band step per resolved Move, whatever the reach; engaged only through an existing link (06.3.5)
    beat = plan.beat
    st = env.state
    actor = beat.actor
    pos = st.positions.get(actor)
    here = (pos.location if pos else None) or (st.scene.place_id if st.scene else None)
    tgt = beat.target if beat.target not in (None, "none", actor) else None
    ent = st.entities.get(tgt) if tgt else None
    if ent is not None and ent.kind == "place":
        if tgt != here:
            return []
        tgt, ent = None, None
    evs = []
    if ent is not None and tgt is not None:
        cur = str((pos.band_to.get(tgt) if pos else None) or "near").removeprefix("band.")
        i = BANDS.index(cur) if cur in BANDS else 2
        away = bool(_AWAY & words(" ".join([beat.method, beat.intent, *plan.intent_verbs])))
        band = BANDS[min(i + 1, 4)] if away else BANDS[i if i == 0 else max(i - 1, 1)]
        evs.append(Event.of("position_set", source=beat.id, rule_id="PR-06-4", entity=actor, location=here,
                            band_to={tgt: band}))
        evs.append(Event.of("position_set", source=beat.id, rule_id="PR-06-4", entity=tgt, band_to={actor: band}))
        from engine.audit.fallback import the_name
        from engine.store.views import display_name

        said = f"{_BAND_WORDS[band]} {the_name(display_name(st, tgt))}"  # "the bench", as the PC knows it (P-108)
    else:
        evs.append(Event.of("position_set", source=beat.id, rule_id="PR-06-4", entity=actor, location=here))
        place = st.entities.get(here) if here else None
        said = f"still in {place.name}" if place else "on the move"  # "you are still in X" (P-077)
    env.add(*evs)
    return [PositionEntry(entity=actor, words=said)]


CONTACT = ("verb.strike", "verb.grapple", "verb.force")
_CREATURES = ("pc", "npc", "adversary", "companion")
_DOWN = re.compile(r"\b(?:trip\w*|prone|floor|sweep\w*|down)\b", re.IGNORECASE)  # knocked down, not pushed


def _contact(env: PipelineEnv, frame: Frame, verb: str | None, delivered: int) -> list[PositionEntry]:
    # rule: 06.3.5
    """A melee Strike, a Grapple or a Force is made at arm's reach (06.4.3 IN REACH, 06.5.2 needs engaged), so
    the attempt writes actor and target engaged, whatever the degree; a Force that lands pushes the target one
    band away at reach 2 and two at reach 3+, breaking the link (06.5.3), unless the beat knocks it down instead
    (prone: the band stays). `delivered` is 0 for a beat that did not resolve."""
    # ponytail: engaged is written even when the weapon has reach (06.4.3 allows close); T-06-6 bands when weapons land
    beat = frame.beat
    st = env.state
    actor, tgt = beat.actor, beat.target
    ent = st.entities.get(tgt or "") if tgt != actor else None
    if ent is None or ent.kind not in _CREATURES or (verb == "verb.strike"
                                                     and "trait.delivery.melee" not in frame.traits):
        return []
    band = "engaged"
    if verb == "verb.force" and delivered >= 2 and not _DOWN.search(f"{beat.method} {beat.intent}"):
        band = BANDS[min(delivered, 3) - 1]  # 2 -> close (one band), 3+ -> near (two bands)
    pos = st.positions.get(actor)
    here = (pos.location if pos else None) or (st.scene.place_id if st.scene else None)
    env.add(Event.of("position_set", source=beat.id, rule_id="06.3.5", entity=actor, location=here,
                     band_to={tgt: band}),
            Event.of("position_set", source=beat.id, rule_id="06.3.5", entity=tgt, band_to={actor: band}))
    if band == "engaged":
        return [PositionEntry(entity=actor, words=f"{_BAND_WORDS[band]} {ent.name}")]
    return [PositionEntry(entity=str(tgt), words=f"driven back, {_BAND_WORDS[band]} you")]


def _verb_deed(rules: Any, verb: str | None) -> str | None:
    aid = verb_anchor(verb, rules)
    tags = rules.anchors.get(aid, {}).get("deed_tags", ()) if aid else ()
    return str(tags[0]) if tags else None


def _gate_again(env: PipelineEnv, beat: Beat) -> GateDecision:
    return check_gate(beat, state=env.state, rules=env.rules, store=env.store, staged=env.tx.events)


def _frame(env: PipelineEnv, plan: BeatPlan, dec: GateDecision, queued: list[BeatPlan], *,
           note: str | None = None, warned: bool = False) -> BeatOutcome:  # rule: PR-01-2
    """ANCHOR (≤8 candidates) and FRAME (the Framer's proposal through `frame_check`), then the lethal check."""
    beat = plan.beat
    cands = anchor_candidates(plan.lookup(), env.state, env.rules)
    if not cands:
        return BeatOutcome(status="refused", entry=_entry(beat, gate=dec.gate, gate_words="no anchor fits (00.15.3)"))
    proposed = env.framer(beat, cands, gate=dec, note=note)
    if proposed.reach_two_factors:  # rule: 01.6.10 (I-160a): zero reach is G4 before the OFFER, nothing spent
        g4 = zero_reach(beat, rules=env.rules, verb=dec.verb, mint=env.tx.mint, store=env.store,
                        staged=env.tx.events)
        env.add(*g4.events)
        return _refused(beat, g4, "G4")
    if trivial_class(proposed, env.rules, dec.verb or beat.verb):  # rule: 01.4.1
        beat.necessity = "trivial"  # the class's base is trivial: anyone, in these conditions, succeeds
        return _no_roll(env, plan, dec)
    # an attack never rides: each Strike or Grapple is its own action and rolls against the same defense
    # (06.1.3, 06.1.6 (f)); P-100: a hit let three later lunges pass as "it works" with no OFFER
    if not proposed.lethal and not _attack(env, beat, proposed) \
            and _rides(env.state, beat, proposed.anchor, proposed.attribute):
        beat.necessity = "riding"  # the success this scene stands; no new roll (01.4.2; P-075)
        return _no_roll(env, plan, dec)
    return _checked(env, plan, dec, proposed, cands, queued, warned=warned)


def _attack(env: PipelineEnv, beat: Beat, proposed: ProposedFrame) -> bool:  # rule: 06.1.6
    verb_traits = (env.rules.basic_verbs.get(beat.verb or "") or {}).get("traits") or ()
    return "trait.action.attack" in {*proposed.traits, *beat.traits, *verb_traits}


def _rides(state: Any, beat: Beat, anchor: str, attribute: str) -> bool:  # rule: 01.4.2
    """A frame resolved this scene as a success (or success at a cost) by the same actor against the same target,
    with the same anchor, attribute and method class: the ride is active and the new beat does not roll.
    ponytail: success rides only, ended by the scene's end or a changed approach; a failure ride (the failure
    stands) needs the lever/superseded-fact end conditions (01.4.2 items 2, 3, 5) before it can block a retry."""
    if beat.target in (None, "none", beat.actor):
        return False
    since = state.scene.started_seq if state.scene is not None else 0
    for fs in state.frames.values():
        r, f = fs.resolved, fs.frame
        b = f.get("beat") or {}
        if (r and fs.committed_seq >= since
                and (r.get("degree") in ("success", "critical_success") or r.get("success_at_cost_taken"))
                and (b.get("actor"), b.get("target"), b.get("method_class"), f.get("anchor"), f.get("attribute"))
                == (beat.actor, beat.target, beat.method_class, anchor, attribute)):
            return True
    return False


def _checked(env: PipelineEnv, plan: BeatPlan, dec: GateDecision, proposed: ProposedFrame, cands: list[str] | None,
             queued: list[BeatPlan], *, warned: bool) -> BeatOutcome:
    beat = plan.beat
    out = frame_check(proposed, beat, state=env.state, rules=env.rules, gate=dec, candidates=cands, store=env.store,
                      staged=env.tx.events)
    lethal_refused = isinstance(out, FrameRefusal) and out.field == "lethal"
    if not warned and (lethal_refused or (isinstance(out, Frame) and (out.stakes == "dire" or out.lethal))):
        warning = (env.lethal or harm_lethal_warning)(env, beat, out if isinstance(out, Frame) else None)
        if warning is not None:  # rule: PR-07-4
            return _warn(env, plan, proposed, cands, queued, warning)
    if lethal_refused:  # 07.3.6 test 1 fails: the frame is not lethal
        proposed = proposed.model_copy(update={"lethal": False})
        out = frame_check(proposed, beat, state=env.state, rules=env.rules, gate=dec, candidates=cands,
                          store=env.store, staged=env.tx.events)
    if isinstance(out, FrameRefusal):  # the Framer's default failed too: a data gap, logged for review
        env.add(log_ruling(RulingRecord(signature=f"rule_conflict:frame:{beat.verb or beat.license}",
                                        situation=beat.restatement or beat.intent, kind="rule_conflict",
                                        review_flag=True, result={"degree": None, "outcome": out.message}),
                           env.tx.mint, store=env.store, staged=env.tx.events, rule_id="01.5.4"))
        return BeatOutcome(status="refused", entry=_entry(beat, gate=dec.gate, gate_words=out.message))
    return _offer(env, plan, proposed, out, cands, queued, warned=warned)


def _warn(env: PipelineEnv, plan: BeatPlan, proposed: ProposedFrame, cands: list[str] | None,
          queued: list[BeatPlan], warning: LethalWarning) -> BeatOutcome:  # rule: 07.3.4
    """The lethal warning comes before a lethal frame, with a choice (07.3.4; PR-07-4; SC-006)."""
    env.add(*warning.events)
    choices = [{"id": "continue", "label": "Go on (you will see the offer)"}, {"id": "withdraw", "label": "Back off"}]
    detail = {"stage": "warning", "plan": plan.model_dump(mode="json"), "queued": _dump(queued),
              "proposed": proposed.model_dump(mode="json"), "candidates": cands, "source": warning.source}
    _open(env, "offer", warning.block, choices, "withdraw", detail)
    return BeatOutcome(status="paused", entry=_entry(plan.beat, gate_words="lethal warning"),
                       oof=[{"kind": "WARNING", "text": warning.block}])


# ------------------------------------------------------------------------------------------- OFFER


def _offer(env: PipelineEnv, plan: BeatPlan, proposed: ProposedFrame, frame: Frame, cands: list[str] | None,
           queued: list[BeatPlan], *, warned: bool) -> BeatOutcome:  # rule: 01.7.1
    from engine.dm.oof import offer_block, offer_choices  # the 12.15.2 template (the dm layer renders)

    view = offer_preview(frame)
    if env.auto_commit and not warned and _may_auto(env, frame):  # rule: 01.7.4
        env.add(*commit_events(frame, "auto", mint=env.tx.mint, state=env.state))
        env.add(Event.of("offer_logged", source=frame.id or "engine", rule_id="01.7.4", frame_id=frame.id,
                         shown_at=env.state.time.now, choice="auto"))
        out = _roll(env, plan, frame, queued)
        out.oof.insert(0, {"kind": "OFFER", "text": offer_block(frame, rules=env.rules, auto=True, state=env.state,
                                                                then=_then(queued)).text})
        return out
    text = offer_block(frame, rules=env.rules, state=env.state, then=_then(queued)).text
    detail = {"stage": "offer", "plan": plan.model_dump(mode="json"), "queued": _dump(queued),
              "proposed": proposed.model_dump(mode="json"), "frame": frame.record(), "candidates": cands,
              "offer": view.model_dump(mode="json"), "warned": warned}
    # the pause's prompt is the beat as restated (its block carries the rest; a session close quotes the prompt)
    _open(env, "offer", view.restated_beat, offer_choices(frame), "withdraw", detail)
    entry = _frame_entry(plan.beat, frame)
    return BeatOutcome(status="paused", entry=entry, oof=[{"kind": "OFFER", "text": text}])


def _then(queued: list[BeatPlan]) -> list[str]:  # rule: 01.2.2
    """The beats of the same message still to come, for the OFFER's "Then:" line (playtest: the punch read as dropped):
    each one's act, never its intent (an intent reads as an outcome promised, live run 015)."""
    return [q.beat.method or q.beat.restatement for q in queued]


def _may_auto(env: PipelineEnv, frame: Frame) -> bool:  # rule: 07.3.6
    """01.7.4's conditions and never a lethal frame (harm's 07.3.6 scan too)."""
    if not auto_commit_allowed(frame):
        return False
    from engine.harm.lethal import may_auto_commit

    return may_auto_commit(env.state, {"kind": "pc", "source": frame.defender or frame.beat.target,
                                       "target": frame.beat.actor, "stakes": frame.stakes, "lethal": frame.lethal})


CHANGE_ASK = ("How do you go about it instead? Say what your character does: another way, or something here you "
              "use. Nothing is spent, and this offer stays open until you do.")


def reframe_note(old: Frame, new: Frame, rules: Any = None) -> str | None:  # rule: 01.7.1
    """One line saying why the odds moved when a new approach replaces an open OFFER on the same target."""
    if old.secret or new.secret or old.odds.success_or_better == new.odds.success_or_better:
        return None
    from engine.dm.oof import name_of

    def signed(n: int) -> str:
        return f"{n:+d}"

    why = []
    om, nm = old.modifier, new.modifier
    if old.attribute != new.attribute:
        why.append(f"it uses {name_of(rules, new.attribute)} ({signed(nm.attribute)}) instead of "
                   f"{name_of(rules, old.attribute)} ({signed(om.attribute)})")
    for part, label in (("competence", "training"), ("circumstance", "help and hindrances"), ("edge", "edge"),
                        ("status", "your condition")):
        a, b = getattr(om, part), getattr(nm, part)
        if a != b:
            why.append(f"{label} {signed(b)} instead of {signed(a)}")
    if old.dc != new.dc:
        why.append(f"the difficulty is {new.dc} instead of {old.dc}")
    return (f"The odds moved from {old.odds.success_or_better}% to {new.odds.success_or_better}%: "
            f"{'; '.join(why) or 'the new approach is framed differently'}.")


def _answer_offer(env: PipelineEnv, plan: BeatPlan, d: dict[str, Any], choice: str,
                  queued: list[BeatPlan]) -> BeatOutcome:  # rule: 01.7.1
    frame = Frame.model_validate(d["frame"])
    proposed = ProposedFrame.model_validate(d["proposed"])
    cands = d.get("candidates")
    warned = bool(d.get("warned"))
    now = env.state.time.now
    if choice == "commit":
        env.add(*commit_events(frame, "commit", mint=env.tx.mint, state=env.state))
        env.add(Event.of("offer_logged", source=frame.id or "player", rule_id="01.7.1", frame_id=frame.id,
                         shown_at=now, choice="commit"))
        return _roll(env, plan, frame, queued)
    if choice in ("go_big", "play_safe"):  # rule: 01.7.3
        trade = "go_big" if choice == "go_big" else "play_it_safe"
        env.add(Event.of("offer_logged", source="player", rule_id="01.7.3", shown_at=now, choice="trade"))
        dec = _gate_again(env, plan.beat)
        traded = proposed.model_copy(update={"trade": trade})
        # Safe -> Risky needs an alternate (01.6.11): the Framer's own (its form fits the scene, P-083) when legal,
        # else the first that fits uncited
        kw = dict(role="alternate", other=traded.threatened_cost, state=env.state, actor=plan.beat.actor,
                  stakes_source=traded.stakes_source, declared_seq=plan.beat.declared_seq or env.state.last_seq,
                  target=plan.beat.target if plan.beat.target != "none" else None)
        if traded.alternate_cost is None or check_cost_decl(traded.alternate_cost, rules=env.rules, **kw):  # type: ignore[arg-type]
            traded.alternate_cost = first_fitting_cost(env.rules, **kw)  # type: ignore[arg-type]
        check = frame_check(traded, plan.beat, state=env.state, rules=env.rules, gate=dec, candidates=cands,
                            store=env.store, staged=env.tx.events)
        if isinstance(check, FrameRefusal) and check.field != "lethal":  # the trade is illegal: the OFFER stays
            out = _offer(env, plan, proposed, frame, cands, queued, warned=warned)
            out.oof.insert(0, {"kind": "NOTE", "text": "That trade is not possible on this attempt; the offer stands "
                                                       "as it was."})
            return out
        out = _checked(env, plan, dec, traded, cands, queued, warned=warned)
        said =("You go big: the stakes and the reach each rise one step." if trade == "go_big" else
                "You play it safe: the stakes and the reach each drop one step.")
        out.oof.insert(0, {"kind": "NOTE", "text": f"{said} The odds stay the same."})
        return out
    if choice == "change":  # rule: 01.7.1
        # change is "a new method or a new lever citation: back to PARSE": the method is the player's to say, so
        # the offer stays open and asks; their words are a new declaration, which replaces it free (12.2.6)
        out = _offer(env, plan, proposed, frame, cands, queued, warned=warned)
        out.oof.insert(0, {"kind": "NOTE", "text": CHANGE_ASK})
        return out
    env.add(Event.of("offer_logged", source="player", rule_id="01.7.1", shown_at=now, choice="withdraw"))
    return BeatOutcome(status="withdrawn", entry=_entry(plan.beat, gate_words="withdrawn at the OFFER"))


def _answer_warning(env: PipelineEnv, plan: BeatPlan, d: dict[str, Any], choice: str,
                    queued: list[BeatPlan]) -> BeatOutcome:  # rule: 07.3.5
    if choice != "continue":
        env.add(Event.of("offer_logged", source="player", rule_id="07.3.4", shown_at=env.state.time.now,
                         choice="withdraw"))
        return BeatOutcome(status="withdrawn", entry=_entry(plan.beat, gate_words="withdrawn after the warning"))
    # going on is the player's next declaration: the context recorded at the warning now stands behind the frame
    beat = plan.beat.model_copy(update={"declared_seq": env.state.last_seq})
    plan = plan.model_copy(update={"beat": beat})
    proposed = ProposedFrame.model_validate(d["proposed"])
    return _checked(env, plan, _gate_again(env, beat), proposed, d.get("candidates"), queued, warned=True)


def _answer_redirect(env: PipelineEnv, plan: BeatPlan, d: dict[str, Any], choice: str,
                     queued: list[BeatPlan]) -> BeatOutcome:  # rule: 01.3.6
    if not choice.startswith("accept:"):
        return BeatOutcome(status="withdrawn", entry=_entry(plan.beat, gate="G3", gate_words="another way chosen"))
    fb = d["fallback"]
    # an accepted crude fallback is "a new frame on the fallback verb" with its DC shift and reach cap (01.3.5):
    # it always rolls through an OFFER, never a no-roll class (playtest 20261007-192159: "take the time" made it
    # an unrolled success the narration could not support, so the player got "You cannot do it that way")
    beat = plan.beat.model_copy(update={"mode": "fallback", "fallback_license": choice.split(":", 1)[1],
                                        "verb": fb.get("verb"), "method": fb.get("method") or plan.beat.method,
                                        "license": None, "necessity": ROLLS, "uses_power": False})
    return _start(env, plan.model_copy(update={"beat": beat}), queued)


# ------------------------------------------------------------------------------------------- ROLL … RECORD


def _attacks(env: PipelineEnv, frame: Frame) -> bool:  # rule: 06.2.1
    """A committed attack-trait beat by the PC on a creature that will resist (an NPC or adversary)."""
    from engine.resolve.conflict import FOES

    beat = frame.beat
    ent = env.state.entities.get(beat.target or "")
    verb_traits = (env.rules.basic_verbs.get(frame.gate.verb or beat.verb or "") or {}).get("traits") or ()
    return (beat.actor == env.pc and ent is not None and ent.kind in FOES
            and "trait.action.attack" in {*frame.traits, *beat.traits, *verb_traits})


def _roll(env: PipelineEnv, plan: BeatPlan, frame: Frame, queued: list[BeatPlan]) -> BeatOutcome:  # rule: PR-01-3
    if _attacks(env, frame):  # 06.2.1: the attack is committed, so the fight starts (or the target joins it)
        from engine.resolve.conflict import start

        start(env.time_ctx(), env.pc, [str(frame.beat.target)], "the PC attacks (06.2.1)")
    roll = roll_check(frame, env.rng)
    if roll.near_miss:  # rule: 01.9.3
        from engine.dm.oof import near_miss_choices  # the labels in words (12.15.4)

        choices = near_miss_choices(frame, env.rules)
        prompt = f"So close: {frame.beat.restatement or frame.beat.intent}. Take the failure, or succeed at a cost?"
        detail = {"stage": "near_miss", "plan": plan.model_dump(mode="json"), "queued": _dump(queued),
                  "frame": frame.record(), "roll": roll.model_dump(mode="json")}
        _open(env, "near_miss", prompt, choices, "failure", detail, frame_id=frame.id)
        entry = _frame_entry(frame.beat, frame, rolled=True, degree=roll.degree, near_miss=True)
        return BeatOutcome(status="paused", entry=entry, frame_id=frame.id, oof=[{"kind": "NEAR_MISS", "text": prompt}])
    return _finish(env, plan, frame, roll, take_sac=False, menu=None)


def _finish(env: PipelineEnv, plan: BeatPlan, frame: Frame, roll: RollResult, *, take_sac: bool,
            menu: str | None) -> BeatOutcome:  # rule: 01.12.1
    """READ → DELIVER → CONSEQUENCE → RECORD, in 01.12.1's order, then `beat_end`."""
    read = read_result(frame, roll, take_success_at_cost=take_sac if roll.near_miss else None)
    start = len(env.tx.events)
    harm_from = len(env.harm_log)
    costs, reach_delta, notes = _consequence(env, frame, read, menu)
    delivered = max(0, read.delivered_reach + reach_delta) if read.delivered_reach else 0
    resolved = roll.degree in ("success", "critical_success") or read.success_at_cost_taken
    verb = frame.gate.verb or frame.beat.verb
    moved = (_moved(env, plan) if resolved and verb == MOVE
             else _contact(env, frame, verb, delivered if resolved else 0) if verb in CONTACT else [])
    if resolved and verb not in ("verb.grapple", "verb.force") and _attacks(env, frame):  # rule: 06.4.3
        from engine.resolve.conflict import check_end, strike_harm

        hurt, said = strike_harm(env.tx, env.rules, env.rng, frame, delivered)
        if hurt.amount or hurt.transition:
            env.harm_log.append(HarmEntry(target=str(frame.beat.target), words=said))
        check_end(env.time_ctx(), env.pc)  # 06.13.1: the last foe down ends the fight
    chg = apply_change(env.tx, env.rules, frame.beat, delivered if resolved else 0, pc=env.pc)  # rule: 01.2.7
    progress = _progress(env, frame, delivered if resolved else 0)
    writes = [e.seq for e in env.tx.events[start:] if e.seq is not None]
    ev_ids: list[str] = []
    if frame.deed_tag:  # PR-03-1 for every resolved beat (a degree is a resolved basis)
        ev = evidence_event(env, frame.beat, frame.deed_tag, frame=frame, degree=roll.degree,
                            sac=read.success_at_cost_taken)
        env.add(ev)
        ev_ids.append(ev.payload.id)  # type: ignore[attr-defined]
    ruling_id = None
    if frame.deltas:  # rule: 01.5.4
        rec = RulingRecord(frame_id=frame.id, signature=frame.signature, situation=frame.beat.restatement or
                           frame.beat.intent, facts_cited=[c.fact_id for c in [*frame.levers, *frame.snags]],
                           frame_summary={"attribute": frame.attribute, "dc_source": frame.dc_source, "dc": frame.dc},
                           kind="adaptation", review_flag=len(frame.deltas) >= 2,
                           result={"degree": roll.degree, "outcome": "success" if resolved else "failure"})
        rev = log_ruling(rec, env.tx.mint, store=env.store, staged=env.tx.events, rule_id="01.5.4")
        env.add(rev)
        ruling_id = rev.payload.ruling["id"]  # type: ignore[attr-defined]
    assert frame.id is not None
    env.add(Event.of("frame_resolved", source=frame.id, rule_id="00.13.2", beat_id=frame.beat.id, frame_id=frame.id,
                     roll={"d20": roll.d20, "total": roll.total, "margin": roll.margin}, degree=roll.degree,
                     near_miss=roll.near_miss, success_at_cost_taken=read.success_at_cost_taken,
                     delivered={"reach": REACH_NAME.get(delivered, str(delivered))},
                     costs=[c.model_dump() for c in costs], method_consequences=list(frame.method_consequences),
                     state_writes=writes, evidence=ev_ids, ruling=ruling_id))
    mark_boundary(env.time_ctx(), "beat_end", {"beat": frame.beat.id, "frame": frame.id})  # rule: 00.7.1
    entry = _frame_entry(frame.beat, frame, rolled=True, degree=roll.degree, near_miss=roll.near_miss,
                         sac=read.success_at_cost_taken, reach=REACH_NAME.get(delivered, str(delivered)))
    entry.costs = costs
    entry.positions = moved
    entry.harm = env.harm_log[harm_from:]
    entry.reach_words = _reach_words(env.rules, frame, delivered, notes)
    entry.progress = progress
    _change_entry(env, frame.beat, entry, chg)
    if resolved:
        _cleanse(env, frame)
    from engine.dm.oof import (  # 12.15.3: the outcome stated once, after the fiction
        change_result_line,
        changed_line,
        result_block,
    )

    blk = result_block(frame, roll, sac=read.success_at_cost_taken, costs=costs, rules=env.rules,
                       changed=changed_line(env.state, env.pc, env.tx.events[start:]) if env.pc else "",
                       change=change_result_line(entry))
    return BeatOutcome(status="resolved", entry=entry, frame_id=frame.id, oof=[{"kind": "RESULT", "text": blk.text}])


def _change_entry(env: PipelineEnv, beat: Beat, entry: BeatEntry, res: ChangeResult) -> None:  # rule: 01.2.7
    """The typed change on the record: its kind, its plain words, and what RECORD applied or why not."""
    c = beat.change
    entry.change_kind = c.kind if c is not None else None
    entry.change = plain(env.state, c, actor=beat.actor, pc=env.pc)
    entry.changed, entry.change_refused = res.words, res.refused


_FREEING = re.compile(r"\b(free|loose|escape|break|slip|wriggle|wrench|pull away|get up|stand)\b", re.IGNORECASE)


PROGRESS_SEGMENTS = 4  # 00.8.3 "a scene's worth"


def _same_goal(a: str | None, b: str | None) -> bool:
    # ponytail: id-prefix match ("obj.track" ~ "obj.track_in_the_damp_earth"); a named-goal key if it misfires
    return bool(a and b) and (a == b or a.startswith(f"{b}_") or b.startswith(f"{a}_"))  # type: ignore[union-attr]


def _progress(env: PipelineEnv, frame: Frame, delivered: int) -> str:  # rule: 01.14.6
    # rule: PR-01-6
    """An `extended` beat, or (outside a conflict) the same verb at the same goal as an earlier success this scene,
    advances a progress clock named for the obstacle: ticks = delivered reach, earlier successes counted when it
    is first made. Returns the words the narration needs: a stretch gained, or the goal reached (P-082). Reaching
    it raises a lead (12.8.2), so what lies at the end is a real thing from state, not an invention."""
    from engine.store.clocks import create_clock, tick_clock
    from engine.world.common import raise_trigger

    beat, st = frame.beat, env.state
    tgt = beat.target if beat.target and beat.target != "none" else None
    if tgt is None or delivered < 1:
        return ""
    verb = frame.gate.verb or beat.verb
    clock = next((c for c in st.clocks.values() if c.kind == "progress" and c.status == "active"
                  and _same_goal(c.owner, tgt)), None)
    if clock is None:
        earlier = [x.resolved for x in st.frames.values() if x.resolved and (
            x.resolved.get("degree") in ("success", "critical_success") or x.resolved.get("success_at_cost_taken"))
            and (x.frame.get("gate") or {}).get("verb") == verb
            and _same_goal((x.frame.get("beat") or {}).get("target"), tgt)]
        if beat.shape != "extended" and not (earlier and _mode(st) != "conflict"):
            return ""
        before = sum(REACH_VALUE.get(str((r.get("delivered") or {}).get("reach")), 0) for r in earlier)
        name = st.entities[tgt].name if tgt in st.entities else tgt.split(".", 1)[-1].replace("_", " ")
        ev = create_clock(st, {"kind": "progress", "segments": PROGRESS_SEGMENTS,
                               "tick_sources": [{"on": "delivered_reach", "ticks": "delivered_reach"}]},
                          name=f"The {name}", owner=tgt, rule_id="01.14.6",
                          filled=min(before, PROGRESS_SEGMENTS - 1))
        env.add(ev)
        clock = st.clocks[ev.payload.clock.id]  # type: ignore[attr-defined]
    res = tick_clock(st, clock.id, "delivered_reach", reach=min(delivered, 4), rule_id="PR-01-6")
    env.add(*res.events)
    if res.completed:
        env.add(raise_trigger(env.tx, "trg.lead_injection", {"progress": clock.id}, rule_id="01.14.6"))
        return ("goal reached: this stretch ends it; show the arrival plainly (where it ends, what is there) "
                "and do not ask whether to press on")
    gained = "more than halfway" if res.filled * 2 >= clock.segments else "a first stretch"
    return (f"progress toward the goal: {gained}; show something concrete and new this stretch gained (the ground "
            "changes, it turns, narrows or nears something), never the same view again")


def _cleanse(env: PipelineEnv, frame: Frame) -> None:  # rule: 00.9.1
    """A resolved beat whose verb is an active condition's cleanse check ("break free: one action", Grapple) ends
    that condition on the actor, when it was aimed at the condition (no other target, the holder, or freeing words)."""
    from engine.store.conditions import remove_condition

    beat = frame.beat
    verb = frame.gate.verb or beat.verb
    for inst in list(env.state.conditions_on(beat.actor)):
        try:
            cdef = env.rules.condition(inst.condition_id)
        except Exception:  # noqa: BLE001 - an unknown condition id has no cleanse here
            continue
        checks = [c for c in cdef.get("cleanse") or () if (c.get("check") or {}).get("verb") == verb]
        holder = (inst.source or {}).get("entity")
        aimed = beat.target in (None, "", "none", beat.actor, holder) or bool(
            _FREEING.search(f"{beat.intent} {beat.method}"))
        # ponytail: "aimed at the condition" is a target/word heuristic; a beat field naming the condition would be exact
        if checks and aimed:
            env.add(*remove_condition(env.state, env.rules, inst.instance_id, checks[0].get("means") or "cleansed",
                                      rule_id="00.9.1").events)


def _consequence(env: PipelineEnv, frame: Frame, read: ReadResult,
                 menu: str | None) -> tuple[list[CostEntry], int, list[str]]:  # rule: 01.11.1
    """The one cost due, at its READ severity: the chosen (or threatened) entry, then the next candidate when it
    cannot land in full (01.13.1)."""
    if read.cost_severity is None:
        return [], 0, []
    order = [m for m in dict.fromkeys([menu, *read.cost_choices]) if m]
    notes: list[str] = []
    for m in order:
        app = apply_cost(frame, read, m, state=env.state, rules=env.rules, mint=env.tx.mint,
                         params=_cost_params(env, frame, m), harm_hook=env.harm_hook, rng=env.rng,
                         mode=_mode(env.state))
        if app.refused:
            notes.append(f"{m}: {app.refused}")
            continue
        env.add(*app.events)
        form = _deferred(env, app.deferred, frame) if app.deferred else ""
        decl = frame.threatened_cost if m == frame.threatened_cost.menu_id else frame.alternate_cost
        return [CostEntry(menu_id=m, severity=app.severity, form=form or (decl.form_intent if decl else ""))], \
            app.reach_delta, notes
    return [], 0, notes  # no candidate could land (01.13.1): nothing is paid, and none is narrated as paid


def _cost_params(env: PipelineEnv, frame: Frame, menu: str) -> dict[str, Any]:
    st = env.state
    actor = frame.beat.actor
    target = frame.beat.target if frame.beat.target and frame.beat.target != "none" else None
    p: dict[str, Any] = {}
    other = frame.defender or target
    people = ("npc", "adversary", "companion")
    if menu == "cost.exposure":  # rule: 01.13.6
        # the observer: the one acted against, else someone present to notice (01.13.6 "false for a scene with no
        # one to notice": the frame check accepted the cost through the scene's people)
        cast = [i for i in (st.scene.cast_present if st.scene else []) if i != actor]
        seen = [i for i in [other, *cast] if i and st.entities.get(i) and st.entities[i].kind in people]
        if seen:
            p["observer"] = seen[0]
    if menu == "cost.gear":
        held = [f.value for f in st.facts.values() if f.subject == actor and f.predicate in ("holds", "carries",
                                                                                              "wields")]
        item = next((v for v in held if isinstance(v, str) and v in st.entities), None)
        if item:
            p["item"] = item
    if menu == "cost.closed_door" and target:
        p["target"] = target
    return p


_SPANS = ((100, "a few minutes pass"), (300, "a good while passes"), (900, "about an hour passes"),
          (3_000, "a few hours pass"), (14_400, "much of the day passes"))


def _span_words(amount: int, unit: str) -> str:  # rule: 12.14.4
    """A time cost's form in plain words: the cost form is read into the fiction, so no digits or rules units
    ("intervals", "watches") — "about an hour passes" [verification: fallback text quality]."""
    from engine.time.clock import ROUNDS, unit_of

    rounds = amount * ROUNDS[unit_of(unit)]
    return next((w for cap, w in _SPANS if rounds <= cap), "days pass")


def _deferred(env: PipelineEnv, deferred: dict[str, Any], frame: Frame) -> str:
    if "advance_time" in deferred:  # rule: 01.13.5
        (unit, amount), = dict(deferred["advance_time"]).items()
        advance_time(env.time_ctx(), int(amount), str(unit), f"cost.time {frame.id}")
        return _span_words(int(amount), str(unit))
    if "footing" in deferred:  # a non-condition footing form: written as a fact on the actor
        env.add(Event.of("fact_set", {"source": "ruling"}, source=frame.id or "cost", rule_id="01.13.7",
                         fact_id=env.tx.mint(ids.FACT), subject=frame.beat.actor, predicate="footing",
                         value=str(deferred["footing"]), visibility="shown",
                         supersedes=env.state.current_fact_id(frame.beat.actor, "footing")))
        return str(deferred["footing"])
    if "twist" in deferred:
        return ", ".join(str(w) for w in deferred["twist"])
    return ""


def _reach_words(rules: Any, frame: Frame, delivered: int, notes: list[str]) -> list[str]:
    """DELIVER (01.10): the anchor's reach ladder line for the delivered reach (coarse: no bundle ranking)."""
    # coarse: 01.10.4
    verb = rules.basic_verbs.get(frame.gate.verb or "") if frame.gate.verb else None
    ladder = ((verb or {}).get("anchor") or {}).get("reach_ladder") or {}
    line = ladder.get(delivered) if delivered else None
    return [str(line)] if line else []


def _frame_entry(beat: Beat, frame: Frame, *, rolled: bool = False, degree: str | None = None, near_miss: bool = False,
                 sac: bool = False, reach: str | None = None) -> BeatEntry:
    return _entry(beat, frame_id=frame.id, gate=frame.gate.class_, approach_words=(
        f"{frame.gate.verb or frame.gate.license}, {frame.attribute}"),
                  difficulty_words=(frame.tier or frame.dc_source).replace("_", " "), stakes=frame.stakes,
                  rolled=rolled, degree=degree, near_miss=near_miss, success_at_cost=sac, reach=reach)


# ------------------------------------------------------------------------------------------- RECORD helpers


def challenge_band(dc: int | None) -> int:  # rule: 03.4.3
    """The absolute band from the final DC: ≤12 → 1, 13–17 → 2, 18–22 → 3, 23–27 → 4, ≥28 → 5 (no DC → 1)."""
    if dc is None:
        return 1
    return 1 if dc <= 12 else 2 if dc <= 17 else 3 if dc <= 22 else 4 if dc <= 27 else 5


def evidence_event(env: PipelineEnv, beat: Beat, tag: str, *, frame: Frame | None, degree: str | None,
                   sac: bool = False) -> Event:  # rule: PR-03-1
    """PR-03-1 steps 2, 3, 6, 8: the deed line, the frame's primary tag (never re-classified), the default witness
    list (NPCs present), recorded with `record_evidence`. Tallies are settled from Milestone 3."""
    st = env.state
    cast = st.scene.cast_present if st.scene else []
    witnesses = [i for i in cast if i in st.entities and st.entities[i].kind in ("npc", "companion", "adversary")]
    result = "succeeds at a cost" if sac else (degree or "succeeds").replace("_", " ")
    return Event.of("evidence_recorded", source=frame.id if frame and frame.id else "engine", rule_id="PR-03-1",
                    beat_id=beat.id, id=env.tx.mint(ids.EVIDENCE), actor=beat.actor, time=st.time.now,
                    deed=f"{beat.restatement or beat.intent} — {result}", tags=[tag], kind="judged",
                    frame_id=frame.id if frame else None, degree=degree,
                    challenge_band=challenge_band(frame.dc if frame else None),
                    stakes=frame.stakes if frame else "safe", lethal_context=bool(frame and frame.lethal),
                    witnesses=witnesses)


# ------------------------------------------------------------------------------------------- pauses, lethal


def _dump(plans: list[BeatPlan]) -> list[dict[str, Any]]:
    return [p.model_dump(mode="json") for p in plans]


def _open(env: PipelineEnv, kind: str, prompt: str, choices: list[dict[str, str]], default: str | None,
          detail: dict[str, Any], *, frame_id: str | None = None) -> PauseRecord:  # rule: 12.2.6
    if detail.get("stage") != "plan" and (env.said or env.said_first):  # T5 is skipped: the words wait (spec 017)
        detail = {**detail, "said": list(env.said), "said_first": list(env.said_first)}
    rec = PauseRecord(pause_id=env.tx.mint(ids.PAUSE), kind=kind, prompt=prompt,  # type: ignore[arg-type]
                      frame_id=frame_id, choices=choices, default_choice=default, detail=detail)
    env.add(Event.of("pause_opened", source="engine", rule_id="12.2.6", pause=rec))
    return rec


def _mode(state: Any) -> str:
    if str(state.time.mode) == "conflict":  # 06.2.1: a fight inside a scene runs in conflict mode
        return "conflict"
    return state.scene.mode if state.scene is not None else str(state.time.mode)


def harm_lethal_warning(env: PipelineEnv, beat: Beat, frame: Frame | None) -> LethalWarning | None:
    # rule: PR-07-4
    """The default LethalCheck, from engine/harm/lethal.py: a 07.3.3 row true for this beat's opponent (or any
    scene source) with no context yet → the [WARNING] block and its writes (`record_warning`: the
    `<source>.lethal_context` fact `frame_check` reads, 00.3.14)."""
    from engine.harm.ctx import HarmCtx
    from engine.harm.lethal import record_warning, warning_block, warning_needed

    st = env.state
    sources = [x for x in (frame.defender if frame else None, beat.target) if x and x != "none"]
    needs = warning_needed(st, env.pc, sources=sources or None)
    if not needs:
        return None
    trig = needs[0]
    name = st.entities[trig.source].name if trig.source in st.entities else trig.source
    fate_q = st.quantities.get(env.pc, {}).get("fate")
    block = warning_block(env.rules, trig, source_name=name, fate=fate_q.current if fate_q else 0,
                          yield_text="give up on terms they will take", retreat_text="break away and run")
    hctx = HarmCtx(state=st, mint=env.tx.mint, rules=env.rules, rng=env.rng)
    events = record_warning(hctx, trig, sign=f"{name} could kill you")
    return LethalWarning(source=trig.source, block=block, events=events)


def _harm_source(env: PipelineEnv, frame_id: str | None, target: str) -> str | None:  # rule: 07.3.2
    """Who deals a cost's harm: the frame's opposing entity (its obstacle's entity, else its first target other than
    the one hurt), so the lethal re-test (07.3.6) finds that source's lethal context; else the frame itself."""
    fs = env.state.frames.get(frame_id or "")
    frame: dict[str, Any] = dict(fs.frame) if fs is not None else {}
    obstacle = frame.get("obstacle") or {}
    beat = frame.get("beat") or {}
    candidates = [obstacle.get("entity"), *list(obstacle.get("entities") or []), *list(beat.get("targets") or []),
                  beat.get("target")]
    for c in candidates:
        if isinstance(c, str) and c != target and c in env.state.entities:
            return c
    return frame_id


def harm_hook_for(env: PipelineEnv, rng: Any = None) -> HarmHook:
    """The CONSEQUENCE harm hook over engine/harm/apply.py's `apply_harm` (PR-07-1; as `apply.harm_hook`, plus a
    HarmEntry for the record). A fall to the Threshold is flagged in `env.threshold_due` for the turn loop."""
    from engine.harm.apply import apply_harm
    from engine.harm.ctx import HarmCtx

    def hook(target: str, severity: str, *, lethal: bool, harm_tags: list[str], frame_id: str | None) -> list[Event]:
        ctx = HarmCtx(state=env.state, mint=env.tx.mint, rules=env.rules, rng=rng or env.rng)
        res = apply_harm(ctx, target, severity=severity, harm_tags=harm_tags, frame_id=frame_id, lethal=lethal,
                         source=_harm_source(env, frame_id, target))
        words = res.transition or ("hurt" if res.amount else "shaken but unhurt")
        env.harm_log.append(HarmEntry(target=target, words=words))
        if res.threshold:
            env.threshold_due.append(target)
        return res.events

    return hook

