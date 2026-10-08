"""The narration pass of the turn loop: PR-12-1 T7–T12 (draft, mention, check, screen, deliver, record).

    adj = run_turn(ctx, message)                    # T1–T6 (engine/dm/turn.py)
    out = narrate_turn(ctx, adj, message)           # T7–T12 → TurnOutcome(response, turn_record, narration)
    out.response.text()                             # fiction, then the 12.15 blocks (the pause block last)

`engine.dm.turn.play_turn(ctx, message)` / `play_answer(ctx, choice_id)` wrap both. `narrate_checked` is the
draft → mention → check → screen loop on its own, for any narration that must pass the checker (a recap, a scene
opening, the first opening; 12.5.3, 12.16.16).

T7–T12 run in one store transaction under the turn's id (T8's write-on-mention, the fallback's ruling, T12's
counters and scene cut); a model failure there writes nothing after T6 and raises, and the turn row keeps the
input; `engine.dm.turn.play_turn` / `play_answer` then keep the turn's record as meta `narration_pending` and
`engine.dm.turn.resume_narration` re-runs T7–T12 from the written state on the next call (engine-api.md Errors).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from engine.audit.claims import Claim, Verdict, check_claims, failing, owed_blocks
from engine.audit.fallback import plain_fallback
from engine.audit.safety import screen_safety
from engine.audit.screen import screen_draft
from engine.dm import oof
from engine.dm.adjudication import AdjudicationRecord
from engine.dm.context import TurnContext
from engine.dm.mentions import MentionResult, write_mentions
from engine.dm.response import Flags, OofBlock, Pause, Response
from engine.dm.roles import checker as checker_role
from engine.dm.roles import narrator as narrator_role
from engine.dm.roles.narrator import Purpose, Redraft
from engine.llm.base import ModelInvalid
from engine.resolve.rulings import log_ruling
from engine.store.events import WORLD, Event, PauseRecord
from engine.store.records import TurnRecord

MAX_REDRAFTS = 2  # fallback only; the rules value is pacing.yaml#claim_check.max_redrafts
FRAME_NEXT = "scene.frame_next"  # meta: a cut reached at T12; the next turn frames the next scene (PR-12-1 T12)
_CUT_FIXES = ("cut", "replace_with_slice")


class NarrationResult(BaseModel):
    """What T7–T10 produced: the fiction to deliver and its audit trail (TurnRecord fields)."""

    fiction: str = ""
    fallback_used: bool = False
    review_flag: bool = False
    skipped: bool = False  # an OFFER with nothing resolved before it: no draft, no check (research.md)
    draft_versions: list[dict[str, Any]] = Field(default_factory=list)
    verdicts: list[dict[str, Any]] = Field(default_factory=list)
    screen: dict[str, Any] = Field(default_factory=dict)
    created: list[str] = Field(default_factory=list)  # entity ids written on mention


class TurnOutcome(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    response: Response
    turn_record: TurnRecord
    narration: NarrationResult
    adjudication: Any = None  # engine.dm.turn.AdjudicationResult


# ------------------------------------------------------------------------------------------- T7–T10


class _Plan(BaseModel):
    cut: set[int] = Field(default_factory=set)
    lines: list[str] = Field(default_factory=list)
    settled: list[str] = Field(default_factory=list)
    needs_narrator: bool = False


def _max_redrafts(rules: Any) -> int:
    return int(rules.pacing.get("claim_check", {}).get("max_redrafts", MAX_REDRAFTS))


def _write_mentions(ctx: TurnContext, record: AdjudicationRecord, mentions: Sequence[Any]) -> MentionResult:
    # rule: PR-00-7
    """T8: write every mentioned element before the check; its writes join the record (12.3.2 sources)."""
    tx = ctx.need_tx()
    start = len(tx.events)
    res = write_mentions(mentions, tx=tx, rules=ctx.rules, rng=ctx.rng, turn_id=ctx.turn_id)
    record.add_writes(tx.events[start:])
    return res


def _settled_lines(ctx: TurnContext, res: MentionResult) -> list[str]:
    st = ctx.state
    return [f"{narrator_role.name_of(st, s.entity)} — {s.property}: {s.value}" for s in res.settled]


def _ask_oracle(ctx: TurnContext, record: AdjudicationRecord, c: Claim) -> str | None:  # rule: 12.3.2
    """An `undetermined` property: settle it with the Oracle (Even odds), write it, return the answer in words."""
    from engine import ids
    from engine.resolve.oracle import OracleQuestion, ask_oracle

    tx = ctx.need_tx()
    st = tx.state
    subject = c.subject if c.subject in st.entities else WORLD
    # the asked value is in the predicate, so the stored yes/no says what it answers ("shutters_closed": False);
    # engine/audit/claims.py `_oracle_settled` reads it back
    pred = ids.slug(" ".join(x for x in (c.predicate or c.cls, c.value) if x))[:60]
    start = len(tx.events)
    res = ask_oracle(OracleQuestion(subject=subject, predicate=pred, question=f"{c.predicate} {c.value}?".strip(),
                                    odds="even", asker="dm"),
                     state=st, rules=ctx.rules, rng=ctx.rng, mint=tx.mint, store=ctx.store, staged=tx.events)
    tx.add_all(res.events)
    if c.cls == "knowledge" and res.answer is True and res.fact_id and record.pc:  # rule: 12.10.5
        tx.add(Event.of("knowledge_recorded", rule_id="12.10.5", knower=record.pc, fact_id=res.fact_id, how="told"))
    record.add_writes(tx.events[start:])
    if res.status == "refused" or res.answer is None:
        return None
    return {True: "yes", False: "no"}.get(res.answer, str(res.answer)) if isinstance(res.answer, bool) \
        else str(res.answer)


def _settle(ctx: TurnContext, record: AdjudicationRecord, claims: Sequence[Claim],
            verdicts: Sequence[Verdict]) -> list[Verdict]:  # rule: 12.3.2
    """`undetermined` with fix `oracle`: ask the Oracle now. A yes is the draft's own value, so the claim is
    `supported` and nothing is redrafted; any other answer is the redraft's (`store_value`); no answer: cut."""
    out = []
    for v in verdicts:
        if v.verdict != "supported" and v.fix == "oracle":
            ans = _ask_oracle(ctx, record, claims[v.claim])
            if ans == "yes":
                v = Verdict(claim=v.claim, verdict="supported", reason="the Oracle settled it as drafted")
            elif ans is None:
                v = v.model_copy(update={"fix": "cut", "reason": "nothing settles it; cut"})
            else:
                v = v.model_copy(update={"store_value": ans, "reason": f"the Oracle settled it: {ans}"})
        out.append(v)
    return out


def _key(sentence: str) -> str:
    return " ".join(re.findall(r"\w+", sentence.lower()))


def _carry(claims: Sequence[Claim], verdicts: Sequence[Verdict], sents: Sequence[str],
           passed: set[str]) -> list[Verdict]:  # rule: 12.3.3
    """A redraft keeps every sentence that passed (12.3.3): a sentence unchanged from a check it passed keeps that
    pass, and fresh claims read from it are not judged again; only new or changed sentences are."""
    out = []
    for v in verdicts:
        n = claims[v.claim].sentence
        if v.verdict != "supported" and 0 <= n < len(sents) and _key(sents[n]) in passed:
            v = Verdict(claim=v.claim, verdict="supported", reason="unchanged since a check it passed (12.3.3)")
        out.append(v)
    return out


def _passed(claims: Sequence[Claim], verdicts: Sequence[Verdict], sents: Sequence[str]) -> set[str]:
    bad = {claims[v.claim].sentence for v in failing(verdicts)}
    return {_key(s) for n, s in enumerate(sents) if n not in bad}


def _plan(claims: Sequence[Claim], verdicts: Sequence[Verdict], sents: Sequence[str]) -> _Plan:  # rule: PR-12-2
    """PR-12-2 steps 3–6 for the failing verdicts: what to cut, what the redraft must change (with the store's
    values), what the Oracle settled (`_settle` asked it)."""
    plan = _Plan()
    for v in failing(verdicts):
        c = claims[v.claim]
        n = c.sentence
        s = sents[n] if 0 <= n < len(sents) else ""
        head = f'sentence {n} "{s}": {v.verdict} ({c.cls}: {c.predicate} {c.value})'.replace("  ", " ")
        if v.fix == "oracle":
            plan.needs_narrator = True
            plan.settled.append(f"{c.predicate}: {v.store_value}")
            plan.lines.append(f"{head}; the Oracle settled it: {v.store_value}. Redraft to that answer")
        elif v.fix == "redraft_to_store":
            plan.needs_narrator = True
            plan.lines.append(f"{head}; the truth is: {v.store_value or 'something else'}. Make the "
                              "fiction say that, in its own words")
        elif v.fix == "replace_with_slice" and v.store_value:
            plan.needs_narrator = True
            plan.cut.add(n)
            plan.lines.append(f"{head}; cut it; if the sentence is needed, use only: {v.store_value}")
        else:  # cut, write_on_mention not done, replace_with_slice without a slice
            plan.cut.add(n)
            plan.lines.append(f"{head}; cut it" + (f" ({v.reason})" if v.reason else ""))
    return plan


_GENERIC_PREDICATES = {"present", "presence", "exists", "exist", "is", "are", "has", "have", "there", "stands", "location"}


def _mention_name(c: Claim) -> str:
    """The new element's name: an existence claim's predicate when it is the noun ("woodsmoke" / "rises thin"), else
    its value ("present" / "a traveler near the post")."""
    pred, value = c.predicate.strip(), c.value.strip()
    name = pred if c.cls == "existence" and pred and pred.lower() not in _GENERIC_PREDICATES else (value or pred)
    return name[:60]


def _apply_writes(ctx: TurnContext, record: AdjudicationRecord, claims: Sequence[Claim],
                  verdicts: Sequence[Verdict]) -> list[Verdict]:  # rule: 00.6.6
    """`new_element` with fix `write_on_mention` (ordinary furniture, an unknown subject: 12.3.2): write it now, at
    check time too, and return the verdicts with each written claim `supported` and each refused one a `cut`
    [revision: I-127; DL-12-37]."""
    todo = {v.claim: _mention_name(claims[v.claim]) for v in failing(verdicts) if v.fix == "write_on_mention"}
    todo = {i: name for i, name in todo.items() if name}
    if not todo:
        return list(verdicts)
    res = _write_mentions(ctx, record, [{"kind": "object", "name": n, "implied": [], "unsettled": []}
                                        for n in dict.fromkeys(todo.values())])
    refused = set(res.refused)
    out = []
    for v in verdicts:
        name = todo.get(v.claim)
        if name is None:
            out.append(v)
        elif name in refused:
            out.append(v.model_copy(update={"fix": "cut", "reason": "a kind that is never created by mention; cut"}))
        else:
            out.append(Verdict(claim=v.claim, verdict="supported"))
    return out


def _renumber(claims: Sequence[Claim], sents: Sequence[str], cut: set[int]) -> tuple[list[str], list[Claim]]:
    keep = [i for i in range(len(sents)) if i not in cut]
    new_index = {old: new for new, old in enumerate(keep)}
    out = [c.model_copy(update={"sentence": new_index[c.sentence]}) for c in claims if c.sentence in new_index]
    return [sents[i] for i in keep], out


def _dump(items: Sequence[BaseModel]) -> list[dict[str, Any]]:
    return [x.model_dump(mode="json", by_alias=True) for x in items]


def _names(ctx: TurnContext, ids: Sequence[str]) -> list[str]:
    st = ctx.state
    return [st.entities[i].name for i in ids if i in st.entities]


def narrate_checked(ctx: TurnContext, record: AdjudicationRecord, *, player_message: str = "",
                    purpose: Purpose = "turn", exchanges: Sequence[str | tuple[str, str]] = (),
                    pause_blocks: Sequence[OofBlock] = (), extra: Sequence[str] = (),
                    fallback_text: str | None = None) -> NarrationResult:  # rule: PR-12-1
    # rule: PR-12-2
    # rule: 12.3.3
    """T7 draft → T8 write-on-mention (one redraft when an answer changes it) → T9 claims and verdicts, fixes, at
    most `max_redrafts` redrafts → T10 screen (any failure back to T7, same budget) → else the plain fallback
    (`review_flag`, its `rule_conflict` ruling logged). Needs the turn's open transaction (`ctx.tx`).
    `fallback_text` replaces the record-built fallback (a recap falls back to its RECAP block: empty fiction)."""
    tx = ctx.need_tx()
    rules = ctx.rules
    max_r = _max_redrafts(rules)
    out = NarrationResult()
    redrafts = 0
    redraft: Redraft | None = None
    mention_redraft_done = False
    text: str | None = None
    sents: list[str] = []
    claims: list[Claim] = []
    flags: dict[str, Any] = {}
    scene_ids: list[str] = []
    verdicts: list[Verdict] = []
    version: dict[str, Any] = {}
    reasons: list[str] = []
    passed: set[str] = set()  # sentences (normalised) that passed a check this call: 12.3.3 keeps them
    while True:
        try:
            if text is None:  # T7 (or D)
                nd = narrator_role.draft(ctx, record, player_message=player_message, exchanges=exchanges,
                                         purpose=purpose, redraft=redraft, extra=extra)
                text = nd.fiction
                version = {"kind": "redraft" if redraft else "draft", "text": text, "mentions": nd.mentions,
                           "claims": [], "verdicts": []}
                out.draft_versions.append(version)
                mres = _write_mentions(ctx, record, nd.mentions)  # T8
                out.created += [i for i in mres.created.values() if i not in out.created]
                if mres.settled and not mention_redraft_done:
                    mention_redraft_done = True  # PR-00-7 step 3: narrate the answer (not a T9 redraft)
                    redraft = Redraft(previous=checker_role.split_sentences(text), settled=_settled_lines(ctx, mres),
                                      failures=["properties the draft needed were settled now: write to them"])
                    text = None
                    continue
                chk = checker_role.check_draft(ctx, text, player_message=player_message, created=out.created,
                                               exchanges=exchanges)  # T9
                sents, claims, flags, scene_ids = chk.sentences, chk.claims, chk.screen, chk.scene_ids
        except ModelInvalid as exc:
            reasons = [f"{exc.__class__.__name__}: {exc}"]
            break
        verdicts = check_claims(claims, tx.state, record, scene_ids, rules=rules)
        verdicts = _carry(claims, verdicts, sents, passed)
        verdicts = _apply_writes(ctx, record, claims, verdicts)
        verdicts = _settle(ctx, record, claims, verdicts)
        passed |= _passed(claims, verdicts, sents)
        version["claims"], version["verdicts"] = _dump(claims), _dump(verdicts)
        bad = failing(verdicts)
        if bad:
            reasons = [f"{v.verdict}: {v.reason}" for v in bad]
            plan = _plan(claims, verdicts, sents)
            if redrafts >= max_r:
                # past the budget every failing sentence is cut, not redrafted: what is left was checked against the
                # store, so it is delivered (closed by the open prompt, 12.14.9) instead of the plain fallback when
                # a sentence of fiction is left [playtest 2026-10-07: a scene asked for came back "What do you do?"]
                cut = (plan.cut | {claims[v.claim].sentence for v in bad}) & set(range(len(sents)))
                body = range(len(sents) - (0 if record.pause else 1))  # without a pause the last is the prompt
                if not cut or not any(i not in cut for i in body):
                    break
                redrafts += 1
                sents, claims = _renumber(claims, sents, cut)
                if record.pause is None and not sents[-1].rstrip().endswith("?"):
                    sents.append("What do you do?")
                text = " ".join(sents)
                version = {"kind": "cut", "text": text, "mentions": [], "claims": [], "verdicts": [],
                           "fixes": plan.lines}
                out.draft_versions.append(version)
                continue
            keep_prompt = record.pause is not None or (len(sents) - 1) not in plan.cut
            pure_cut = not plan.needs_narrator and plan.cut and len(plan.cut) < len(sents) and keep_prompt
            redrafts += 1
            if pure_cut:
                sents, claims = _renumber(claims, sents, plan.cut)  # a pure cut: code removes the sentences
                text = " ".join(sents)
                version = {"kind": "cut", "text": text, "mentions": [], "claims": [], "verdicts": [],
                           "fixes": plan.lines}
                out.draft_versions.append(version)
                continue
            redraft = Redraft(previous=list(sents), failures=plan.lines, settled=plan.settled)
            text = None
            continue
        # T10
        names = _names(ctx, scene_ids)
        res = screen_draft(text, flags=flags, record=record, verdicts=verdicts,
                           safety=screen_safety(text, tx.state), pause_blocks_text=[b.text for b in pause_blocks],
                           rules=rules, names=names)
        out.screen = res.screen
        version["screen"] = res.reasons
        if res.passed:
            out.fiction = text
            out.verdicts = _dump(verdicts)
            return out
        reasons = res.reasons
        if redrafts >= max_r:
            break
        redrafts += 1
        redraft = Redraft(previous=list(sents), failures=[f"screen: {r}" for r in res.reasons])
        text = None
    return _fallback(ctx, record, out, verdicts, reasons, fallback_text)


def _fallback(ctx: TurnContext, record: AdjudicationRecord, out: NarrationResult, verdicts: Sequence[Verdict],
              reasons: Sequence[str], fallback_text: str | None) -> NarrationResult:  # rule: 12.3.3
    """The plain fallback (12.3.3): from the record only, `review_flag`, a `rule_conflict` ruling logged."""
    tx = ctx.need_tx()
    st = tx.state
    names = {eid: e.name for eid, e in st.entities.items() if eid not in st.seals}
    fb = plain_fallback(record, names=names, verdicts=verdicts)
    ruling = fb.ruling.model_copy(update={"result": {**fb.ruling.result, "reasons": list(reasons)}})
    tx.add(log_ruling(ruling, tx.mint, store=ctx.store, staged=tx.events, turn_id=ctx.turn_id, rule_id="12.3.3"))
    out.fiction = fb.fiction if fallback_text is None else fallback_text
    out.fallback_used = True
    out.review_flag = fb.review_flag
    out.verdicts = _dump(verdicts)
    out.draft_versions.append({"kind": "fallback", "text": out.fiction, "mentions": [], "claims": [],
                               "verdicts": [], "reasons": list(reasons)})
    if not out.screen:
        out.screen = {"intent_acknowledged": True, "intent_substituted": False, "next_step_exists": True,
                      "mechanics_in_fiction": [], "ends_on_prompt_or_one_pause": True, "pc_agency_ok": True,
                      "safety_ok": True}
    return out


# ------------------------------------------------------------------------------------------- T11 blocks


def _pc_fate(ctx: TurnContext) -> int | None:
    from engine.retrieve.scene import pc_id

    pc = pc_id(ctx.state)
    q = ctx.state.quantities.get(pc or "", {}).get("fate")
    return q.current if q is not None else None


def _labelled(kind: str, text: str) -> OofBlock:
    t = text.strip()
    if t.startswith("["):
        return OofBlock(kind=kind, text=t)  # type: ignore[arg-type]
    if kind == "NOTE":
        return oof.note_block(t)
    if kind == "OFFER":
        return OofBlock(kind="OFFER", text=f"[OFFER — auto] {t}")
    return OofBlock(kind=kind, text=f"[{kind.replace('_', ' ')}] {t}")  # type: ignore[arg-type]


def pause_blocks(ctx: TurnContext, pause: PauseRecord, items: Sequence[dict[str, str]] = ()) -> list[OofBlock]:
    # rule: 12.15
    """The open pause's block(s), rendered from the stored pause (so resume re-shows exactly this)."""
    from engine.resolve.types import Frame, RollResult

    d = pause.detail or {}
    stage = d.get("stage")
    rules = ctx.rules
    last = {i["kind"]: i["text"] for i in items}
    try:
        if stage == "offer":
            return [oof.offer_block(Frame.model_validate(d["frame"]), rules=rules, fate=_pc_fate(ctx))]
        if stage == "near_miss":
            return [oof.near_miss_block(Frame.model_validate(d["frame"]), RollResult.model_validate(d["roll"]),
                                        rules=rules)]
        if stage == "redirect" and d.get("decision"):
            return [_redirect(ctx, d["decision"])]
    except Exception:  # noqa: BLE001 - a stored frame this build cannot read: the stored prompt still shows
        pass
    # the pause's choices are not repeated here: the front end lists them, numbered, after the block
    if stage == "offer":
        return [_labelled("OFFER", f"[OFFER] {pause.prompt}")]
    if stage == "warning":
        warn = last.get("WARNING") or pause.prompt
        return [_labelled("WARNING", warn), oof.note_block("Go on, or back off (nothing is spent)?", "CHOICE")]
    if stage == "near_miss":
        return [_labelled("NEAR_MISS", f"[NEAR MISS] {pause.prompt}")]
    if stage == "redirect":
        return [_labelled("REDIRECT", f"[REDIRECT] {pause.prompt}")]
    if stage == "dispute":
        return [OofBlock(kind="CLARIFY", text=f"[CLARIFY] {pause.prompt}")]
    if pause.kind == "clarify":
        return [oof.clarify_block(pause.prompt)]
    if pause.kind == "last_chance":
        return [_labelled("LAST_CHANCE", last.get("LAST_CHANCE") or f"[CHOICE] {pause.prompt}")]
    return [oof.note_block(pause.prompt.strip() or "Choose one.", "CHOICE")]


def _redirect(ctx: TurnContext, decision: Any) -> OofBlock:  # rule: 12.15.5
    """The REDIRECT block from the stored GateDecision (a dict, or its JSON)."""
    from engine.resolve.gate import GateDecision

    dec = (GateDecision.model_validate_json(decision) if isinstance(decision, str)
           else GateDecision.model_validate(decision))
    return oof.redirect_block(dec, state=ctx.state, rules=ctx.rules)


def shown_pause(pause: PauseRecord, owned: Sequence[OofBlock]) -> Pause:  # rule: 12.15
    """The API Pause for an open pause whose own block is shown: the block carries the prompt (the OFFER, the
    near miss, the redirect, ...), so the pipeline's one-line summary is not delivered a second time."""
    p = Pause.of(pause)
    return p.model_copy(update={"prompt": ""}) if owned else p


_PAUSE_ITEM = {"offer": ("OFFER", "WARNING"), "near_miss": ("NEAR_MISS",), "redirect": ("REDIRECT",),
               "last_chance": ("LAST_CHANCE",), "clarify": ("CLARIFY",)}


def _item_block(ctx: TurnContext, item: dict[str, str]) -> OofBlock:
    """One owed block; a REDIRECT that carries its GateDecision is rendered in words from it."""
    if item["kind"] == "REDIRECT" and item.get("decision"):
        try:
            return _redirect(ctx, item["decision"])
        except Exception:  # noqa: BLE001 - an unreadable decision: the pipeline's words still show
            pass
    return _labelled(item["kind"], item["text"])


def turn_blocks(ctx: TurnContext, oof_items: Sequence[dict[str, str]], record: AdjudicationRecord,
                pause: PauseRecord | None) -> tuple[list[OofBlock], list[OofBlock]]:  # rule: 12.15
    """(all blocks in 12.15 order, the pause's own blocks). The items T4–T5 owed, the open pause's block rendered
    from state in place of its one-line summary, and any warning block the record carries."""
    items = list(oof_items)
    owned: list[OofBlock] = []
    if pause is not None:
        owned = pause_blocks(ctx, pause, items)
        for kind in _PAUSE_ITEM.get(str(pause.detail.get("stage") or pause.kind), ()):
            idx = max((i for i, it in enumerate(items) if it["kind"] == kind), default=None)
            if idx is not None:
                items.pop(idx)
    # two beats refused for the same reason owe one block, not two copies (12.15: each block once)
    blocks = list({b.text: b for b in (_item_block(ctx, i) for i in items)}.values())
    texts = {b.text for b in blocks} | {b.text for b in owned}
    for n in record.notes:
        if n.lstrip().startswith("[WARNING") and n.strip() not in texts:
            blocks.append(OofBlock(kind="WARNING", text=n.strip()))
    return oof.ordered([*blocks, *owned]), owned


def owed(ctx: TurnContext, record: AdjudicationRecord, text: str) -> list[OofBlock]:  # rule: 12.3.2
    """Blocks a trigger owes (12.3.2 owed blocks) that the response lacks, rendered from state."""
    out: list[OofBlock] = []
    missing = owed_blocks(record.triggers, text)
    if "[STATUS]" in missing and record.pc:
        blk = oof.status_block(ctx.rules, ctx.state, record.pc)
        if blk is not None:
            out.append(blk)
    return out


# ------------------------------------------------------------------------------------------- T12


_MOVE_ON = re.compile(r"\b(skip ahead|move on|moving on|next morning|next day|tomorrow|later that|i leave|we leave|"
                      r"let'?s go|head (?:to|for|out|back|off)|go to|go back|travel to|set out|leave for|walk to|"
                      r"ride to|return to|make for|on to the)\b", re.IGNORECASE)
_STAY = re.compile(r"\b(not done|stay|keep looking|wait here|remain here|i remain|one more)\b", re.IGNORECASE)


def moves_on(message: str) -> bool:  # rule: 12.4.2
    """12.4.2 (6): the player says to move on ("skip ahead", "I leave", "next morning")."""
    return bool(_MOVE_ON.search(message or ""))


def stays(message: str) -> bool:  # rule: 12.4.2
    """The player stays after an offered cut ("I'm not done here")."""
    return bool(_STAY.search(message or ""))


def record_turn_end(ctx: TurnContext, record: AdjudicationRecord, writes: Sequence[int]) -> list[OofBlock]:
    # rule: PR-12-1
    # rule: 12.4.2
    """T12 counters and the scene cut: dead air (`note_turn`), an interrupt noted, then `cut_due`; a cut ends the
    scene now (`end_scene`, which marks scene_end) and leaves `scene.frame_next` for the next turn to frame
    (the player's own cut was framed in this turn already, by the Director at T5). Returns blocks to add."""
    from engine.world.scenes import cut_due, end_scene, note_cut, note_turn, turn_is_quiet

    st = ctx.state
    if st.scene is None:
        return []
    tctx = ctx.time_ctx()
    evs = [e for e in (ctx.store.event(s) for s in writes) if e is not None]
    note_turn(tctx, quiet=turn_is_quiet([p.cls for p in record.parts], evs))
    if any(n.startswith("interrupted:") for n in record.notes):
        note_cut(tctx, "interrupt")
    if ctx.state.open_pause() is not None:
        return []  # 12.2.6: a pause holds the scene where it is
    reason = cut_due(ctx.state, ctx.rules)
    if reason is None:
        return []
    end = end_scene(tctx, reason)
    ctx.need_tx().add(Event.of("meta_set", source="engine", rule_id="PR-12-1", key=FRAME_NEXT,
                               value={"reason": reason, "scene_id": end.scene_id, "turn_id": ctx.turn_id}))
    record.scene.cut = True
    record.scene.ended = end.scene_id
    if reason == "dead_air":
        return [oof.note_block("Move on to what comes next? Or stay a while.", "CUT?")]
    return []


# ------------------------------------------------------------------------------------------- the turn


def skip_drafting(record: AdjudicationRecord, pause: PauseRecord | None) -> bool:  # rule: 12.2.6
    """An OFFER pause with nothing resolved before it: deliver the OFFER block only (it restates the beat)."""
    if pause is None or (pause.detail or {}).get("stage") != "offer":
        return False
    return (len(record.beats) <= 1 and not record.oracle and not record.npc_actions and not record.omens
            and not record.scene.started and not any(p.cls == "SPEECH" for p in record.parts))


OOF_CLASSES = frozenset({"SAFETY", "SESSION", "DISPUTE", "OOF_QUESTION"})


def pure_oof(record: AdjudicationRecord) -> bool:  # rule: 12.15
    """Only out-of-fiction parts and nothing happened in the fiction: the response is its blocks alone (fiction
    empty, engine-api.md `Response.fiction`)."""
    return (bool(record.parts) and all(p.cls in OOF_CLASSES for p in record.parts) and not record.beats
            and not record.oracle and not record.npc_actions and not record.omens and not record.scene.started
            and not record.scene.ended)


def narrate_turn(ctx: TurnContext, adj: Any, message: str) -> TurnOutcome:  # rule: PR-12-1
    """T7–T12 for an `AdjudicationResult` (engine/dm/turn.py): the delivered Response and the full TurnRecord."""
    from engine.dm.turn import recent_exchanges
    from engine.harm.threshold import ending_state

    store = ctx.store
    rec: AdjudicationRecord = adj.record
    pause = store.state.open_pause()
    blocks, owned = turn_blocks(ctx, adj.oof, rec, pause)
    exchanges = recent_exchanges(store, adj.turn_id)
    with store.transaction(adj.turn_id) as tx:
        ctx.tx = tx
        try:
            if pure_oof(rec):
                narr = NarrationResult(fiction="", skipped=True)
            elif skip_drafting(rec, pause):  # the OFFER block restates the beat (01.7.1): not said twice
                narr = NarrationResult(fiction="", skipped=True)
            else:  # the OOF parts are answered by their blocks: the fiction answers (and is screened on) the rest
                if any(p.cls in OOF_CLASSES for p in rec.parts):
                    message = " ".join(p.text for p in rec.parts if p.cls not in OOF_CLASSES) or message
                narr = narrate_checked(ctx, rec, player_message=message, exchanges=exchanges,
                                       pause_blocks=owned if pause is not None else ())
            blocks += record_turn_end(ctx, rec, adj.writes)  # T12
        finally:
            ctx.tx = None
        events = list(tx.events)
    rec.add_writes(events)
    st = store.state
    resp = Response(turn_id=adj.turn_id, phase="ending" if ending_state(st) else "play", fiction=narr.fiction,
                    oof_blocks=oof.ordered(blocks), pause=shown_pause(pause, owned) if pause is not None else None,
                    scene_ended=bool(rec.scene.ended) and st.scene is None,
                    flags=Flags(fallback_used=narr.fallback_used, review_flag=narr.review_flag))
    extra = owed(ctx, rec, resp.text())
    if extra:
        resp.oof_blocks = oof.ordered([*resp.oof_blocks, *extra])
    calls = store.model_calls(adj.turn_id)
    tr = adj.turn_record.model_copy(update={
        "writes": rec.write_seqs, "draft_versions": narr.draft_versions, "verdicts": narr.verdicts,
        "fallback_used": narr.fallback_used, "screen": narr.screen, "delivered_verbatim": resp.text(),
        "model_calls": list(dict.fromkeys([*adj.turn_record.model_calls, *ctx.call_ids])),
        "cost_usd": float(sum(c.get("cost_usd") or 0.0 for c in calls)),
        "latency_ms": int(sum(c.get("latency_ms") or 0 for c in calls)),
        "pause": ({"kind": pause.kind, "frame_id": pause.frame_id, "options": [c.get("id", "") for c in pause.choices]}
                  if pause is not None else None)})
    store.save_turn(tr)  # T12: the delivered response verbatim
    return TurnOutcome(response=resp, turn_record=tr, narration=narr, adjudication=adj)


__all__ = ["FRAME_NEXT", "NarrationResult", "TurnOutcome", "moves_on", "narrate_checked", "narrate_turn", "owed",
           "pause_blocks", "pure_oof", "record_turn_end", "shown_pause", "skip_drafting", "stays", "turn_blocks"]
