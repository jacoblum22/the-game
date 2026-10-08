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

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

from engine import ids
from engine.dm.adjudication import BeatEntry, CostEntry, HarmEntry, PositionEntry
from engine.resolve.costs import HarmHook, apply_cost
from engine.resolve.frame import auto_commit_allowed, commit_events, frame_check, legal_trades, offer_preview
from engine.resolve.gate import GateDecision, check_gate, words
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
    queued: list[str] = Field(default_factory=list)  # beats beyond the third, restated (01.2.3)

    def extend(self, other: PipelineResult) -> PipelineResult:
        self.outcomes += other.outcomes
        self.pause = other.pause
        self.queued += other.queued
        return self


# ------------------------------------------------------------------------------------------- driver


def run_beats(env: PipelineEnv, plans: list[BeatPlan]) -> PipelineResult:  # rule: PR-01-1
    """Run up to three beats in the player's order; stop at the first pause (the rest wait in its detail)."""
    res = PipelineResult()
    todo = list(plans[:MAX_BEATS])
    res.queued = [p.beat.restatement or p.beat.intent for p in plans[MAX_BEATS:]]  # rule: 01.2.3
    while todo:
        plan = todo.pop(0)
        out = _start(env, plan, todo)
        res.outcomes.append(out)
        if out.status == "paused":
            res.pause = env.state.open_pause()
            return res
    return res


def resume(env: PipelineEnv, pause: PauseRecord, choice: str, *, by: str = "option",
           words: str | None = None) -> PipelineResult:  # rule: 12.2.6
    """Answer the open pause and continue the same beat from the stored frame, then the queued beats."""
    d = pause.detail
    env.add(Event.of("pause_closed", source="player", rule_id="12.2.6", pause_id=pause.pause_id, choice=choice,
                     by=by, words=words))
    stage = d.get("stage")
    if stage not in ("offer", "warning", "near_miss", "redirect"):  # clarify: the Reader re-reads the words
        return PipelineResult()
    plan = BeatPlan.model_validate(d["plan"])
    queued = [BeatPlan.model_validate(q) for q in d.get("queued", [])]
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
    res = PipelineResult(outcomes=[out])
    if out.status == "paused":
        res.pause = env.state.open_pause()
        return res
    if out.status == "withdrawn":  # the rest of that declaration depended on it: dropped, restated
        res.queued = [p.beat.restatement or p.beat.intent for p in queued]
        return res
    return res.extend(run_beats(env, queued))


def close_by_default(env: PipelineEnv, pause: PauseRecord) -> PipelineResult:  # rule: 12.2.6
    """A new declaration while a pause is open: OFFER withdrawn (nothing spent), near miss → failure, redirect →
    the player chose another way. Queued beats of the old declaration are dropped (the new one replaces them)."""
    stage = pause.detail.get("stage")
    if stage == "near_miss":
        pause.detail["queued"] = []
        return resume(env, pause, "failure", by="default")
    env.add(Event.of("pause_closed", source="engine", rule_id="12.2.6", pause_id=pause.pause_id,
                     choice=pause.default_choice, by="withdrawn" if stage in ("offer", "warning") else "default"))
    if stage in ("offer", "warning"):
        env.add(Event.of("offer_logged", source="engine", rule_id="01.7.1", frame_id=None,
                         shown_at=env.state.time.now, choice="withdraw"))
    return PipelineResult()


# ------------------------------------------------------------------------------------------- GATE … FRAME


def _entry(beat: Beat, **kw: Any) -> BeatEntry:
    targets = [beat.target] if beat.target and beat.target != "none" else []
    return BeatEntry(beat_id=beat.id, actor=beat.actor, targets=targets, restatement=beat.restatement or beat.intent,
                     license=beat.license, **kw)


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
    # 3. NECESSITY (01.4)
    if beat.necessity == "impossible":
        return BeatOutcome(status="refused", entry=_entry(beat, gate="G4", gate_words="impossible (01.4.1)"))
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
        said = f"{_BAND_WORDS[band]} {ent.name}"
    else:
        evs.append(Event.of("position_set", source=beat.id, rule_id="PR-06-4", entity=actor, location=here))
        place = st.entities.get(here) if here else None
        said = f"moved within {place.name}" if place else "moved"
    env.add(*evs)
    return [PositionEntry(entity=actor, words=said)]


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
    return _checked(env, plan, dec, proposed, cands, queued, warned=warned)


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
    view = offer_preview(frame)
    if env.auto_commit and not warned and _may_auto(env, frame):  # rule: 01.7.4
        env.add(*commit_events(frame, "auto", mint=env.tx.mint, state=env.state))
        env.add(Event.of("offer_logged", source=frame.id or "engine", rule_id="01.7.4", frame_id=frame.id,
                         shown_at=env.state.time.now, choice="auto"))
        out = _roll(env, plan, frame, queued)
        out.oof.insert(0, {"kind": "OFFER", "text": offer_text(view) + " (auto-committed)"})
        return out
    choices = [{"id": "commit", "label": "Commit"}, {"id": "change", "label": "Change approach"},
               {"id": "withdraw", "label": "Withdraw (nothing is spent)"}]
    choices += [{"id": TRADE_IDS[t], "label": t.replace("_", " ").capitalize()} for t in legal_trades(frame)]
    detail = {"stage": "offer", "plan": plan.model_dump(mode="json"), "queued": _dump(queued),
              "proposed": proposed.model_dump(mode="json"), "frame": frame.record(), "candidates": cands,
              "offer": view.model_dump(mode="json"), "warned": warned}
    _open(env, "offer", offer_text(view), choices, "withdraw", detail)
    entry = _frame_entry(plan.beat, frame)
    return BeatOutcome(status="paused", entry=entry, oof=[{"kind": "OFFER", "text": offer_text(view)}])


def _may_auto(env: PipelineEnv, frame: Frame) -> bool:  # rule: 07.3.6
    """01.7.4's conditions and never a lethal frame (harm's 07.3.6 scan too)."""
    if not auto_commit_allowed(frame):
        return False
    from engine.harm.lethal import may_auto_commit

    return may_auto_commit(env.state, {"kind": "pc", "source": frame.defender or frame.beat.target,
                                       "target": frame.beat.actor, "stakes": frame.stakes, "lethal": frame.lethal})


def offer_text(view: Any) -> str:  # rule: 01.7.1
    """A one-line OFFER summary from the computed frame (the full OfferView rides in the pause detail)."""
    o = view.odds
    need = f"need {view.need}+" if view.need is not None else "hidden odds"
    alt = f"; or {view.alternate_cost['menu_id']} on a near miss" if view.alternate_cost else ""
    lethal = "; THIS CAN KILL YOU" if view.lethal else ""
    return (f"{view.restated_beat.rstrip('.')}: {view.approach.get('verb') or view.approach.get('license')} with "
            f"{view.approach.get('attribute')}, {view.difficulty_words}; {need} "
            f"({o['success_or_better_pct']}%); stakes {view.stakes}, reach {view.reach}; on failure "
            f"{view.threatened_cost['menu_id']} {view.threatened_cost['severity_on_failure'] or 'none'}{alt}{lethal}")


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
        return _checked(env, plan, dec, proposed.model_copy(update={"trade": trade}), cands, queued, warned=warned)
    if choice == "change":  # back to PARSE/FRAME, free (01.7.1)
        env.add(Event.of("offer_logged", source="player", rule_id="01.7.1", shown_at=now, choice="change"))
        dec = _gate_again(env, plan.beat)
        return _frame(env, plan, dec, queued, warned=warned,
                      note="The player chose CHANGE at the OFFER: propose a different approach (another anchor, "
                           "attribute or cited lever) for the same intent.")
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
    beat = plan.beat.model_copy(update={"gate": "G3", "mode": "fallback", "fallback_license": choice.split(":", 1)[1],
                                        "verb": fb.get("verb"), "method": fb.get("method") or plan.beat.method,
                                        "license": None})
    return _start(env, plan.model_copy(update={"beat": beat}), queued)


# ------------------------------------------------------------------------------------------- ROLL … RECORD


def _roll(env: PipelineEnv, plan: BeatPlan, frame: Frame, queued: list[BeatPlan]) -> BeatOutcome:  # rule: PR-01-3
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
    moved = _moved(env, plan) if resolved and (frame.gate.verb or frame.beat.verb) == MOVE else []
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
    return BeatOutcome(status="resolved", entry=entry, frame_id=frame.id)


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
    rec = PauseRecord(pause_id=env.tx.mint(ids.PAUSE), kind=kind, prompt=prompt,  # type: ignore[arg-type]
                      frame_id=frame_id, choices=choices, default_choice=default, detail=detail)
    env.add(Event.of("pause_opened", source="engine", rule_id="12.2.6", pause=rec))
    return rec


def _mode(state: Any) -> str:
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

