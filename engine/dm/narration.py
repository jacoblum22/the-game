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
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from engine.audit.claims import Claim, Verdict, beat_polarity, check_claims, failing, owed_blocks
from engine.audit.declare import (
    DeclaredSentence,
    Failure,
    SceneIndex,
    coverage,
    known_as,
    mention_of,
    scan_sentence,
    t2_delivered,
    tier_of,
)
from engine.audit.fallback import plain_fallback
from engine.audit.safety import screen_safety
from engine.audit.screen import echoed_quotes, screen_draft
from engine.dm import oof
from engine.dm.adjudication import AdjudicationRecord
from engine.dm.context import TurnContext
from engine.dm.handles import RecordItem
from engine.dm.mentions import MentionResult, write_mentions
from engine.dm.response import Flags, OofBlock, Pause, Response
from engine.dm.roles import checker as checker_role
from engine.dm.roles import narrator as narrator_role
from engine.dm.roles.narrator import Purpose, Repair
from engine.llm.base import ModelInvalid
from engine.resolve.rulings import RulingRecord, log_ruling
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


class _Sent(BaseModel):
    """One drafted sentence while it is judged and repaired (12.3.3)."""

    decl: DeclaredSentence
    failures: list[Failure] = Field(default_factory=list)
    dropped: bool = False
    replaced: int = 0  # repair rounds that rewrote it
    verdicts: list[dict[str, Any]] = Field(default_factory=list)  # its claims' verdicts (TurnRecord.verdicts)
    cited_before: list[str] = Field(default_factory=list)  # handles the sentence it replaced cited (its place)

    @property
    def ok(self) -> bool:
        return not self.failures

    @property
    def cut(self) -> bool:
        return any(f.fix == "cut" for f in self.failures)


class _Turn(BaseModel):
    """What one narrate_checked call carries between judging rounds."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: list[RecordItem] = Field(default_factory=list)
    player_message: str = ""
    exchanges: list[Any] = Field(default_factory=list)
    stats: dict[str, int] = Field(default_factory=dict)


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


def _ask_oracle(ctx: TurnContext, record: AdjudicationRecord, c: Claim, odds: str = "even") -> str | None:
    # rule: 12.3.2
    """A consequential `undetermined` property (or a T1b proposal): settle it with the Oracle, write it, return the
    answer in words."""
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
                                    odds=odds, asker="dm"),
                     state=st, rules=ctx.rules, rng=ctx.rng, mint=tx.mint, store=ctx.store, staged=tx.events)
    tx.add_all(res.events)
    if c.cls in ("knowledge", "sealed") and res.answer is True and res.fact_id and record.pc:  # rule: 12.10.5
        tx.add(Event.of("knowledge_recorded", rule_id="12.10.5", knower=record.pc, fact_id=res.fact_id, how="told"))
    record.add_writes(tx.events[start:])
    if res.status == "refused" or res.answer is None:
        return None
    return {True: "yes", False: "no"}.get(res.answer, str(res.answer)) if isinstance(res.answer, bool) \
        else str(res.answer)


def _settle(ctx: TurnContext, record: AdjudicationRecord, claims: Sequence[Claim],
            verdicts: Sequence[Verdict]) -> list[Verdict]:  # rule: 12.3.2
    """`undetermined` (12.3.2, split by tier): an incidental property is written as narrated and binds later turns
    (T1a, DL-12-40); a consequential one goes to the Oracle: a yes is the draft's own value (`supported`), any other
    answer is the redraft's (`store_value`), no answer: cut."""
    out = []
    tx = ctx.need_tx()
    for v in verdicts:
        c = claims[v.claim]
        if v.verdict == "undetermined" and v.incidental and c.subject in tx.state.entities:
            from engine import ids
            from engine.world.common import fact

            start = len(tx.events)
            tx.add(fact(tx, c.subject, ids.slug(c.predicate or "detail")[:60], c.value, rule_id="12.3.2",
                        source="narration", visibility="shown"))
            record.add_writes(tx.events[start:])
            v = Verdict(claim=v.claim, verdict="supported", reason="incidental: written as narrated (12.3.2; T1a)")
        elif v.verdict != "supported" and v.fix == "oracle":
            ans = _ask_oracle(ctx, record, c)
            if ans == "yes":
                v = Verdict(claim=v.claim, verdict="supported", reason="the Oracle settled it as drafted")
            elif ans is None:
                v = v.model_copy(update={"fix": "cut", "reason": "nothing settles it; cut"})
            else:
                v = v.model_copy(update={"store_value": ans, "reason": f"the Oracle settled it: {ans}"})
        out.append(v)
    return out


def _apply_writes(ctx: TurnContext, record: AdjudicationRecord, claims: Sequence[Claim],
                  verdicts: Sequence[Verdict]) -> list[Verdict]:  # rule: 00.6.6
    """The backstop for an element the narrator did not declare (12.3.2 `new_element`, fix `write_on_mention`):
    written as ordinary furniture, so it is never cut merely for being new [revision: I-127; DL-12-37]; declared
    `new` elements are the main path (`_write_new`)."""
    todo = {v.claim: (claims[v.claim].value or claims[v.claim].predicate).strip()[:60]
            for v in failing(verdicts) if v.fix == "write_on_mention"}
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
            out.append(Verdict(claim=v.claim, verdict="supported", reason="undeclared: written on mention (backstop)"))
    return out


def _write_new(ctx: TurnContext, record: AdjudicationRecord, s: _Sent, idx: SceneIndex,
               out: NarrationResult) -> None:  # rule: PR-00-7
    # rule: 12.14.13
    """PR-00-7 step 2: each declared new element by its tier. T1a is written on mention with the properties the
    sentence states; T1b is proposed and settled by the Oracle (Likely when a present NPC the sentence is about
    says it, else Unlikely; a "no" is a redraft); T2 passes only when a cited record line delivers it."""
    from engine.dm.roles.world import present_npcs

    for el in s.decl.new:
        known = known_as(el, idx)
        if known is not None:  # one of the scene's own: spoken of, not new
            s.decl.about = list(dict.fromkeys([*s.decl.about, known]))
            continue
        tier = tier_of(el, ctx.rules)
        if tier == "T1a":
            m = mention_of(el)
            res = _write_mentions(ctx, record, [m]) if m is not None else None
            if res is None or res.refused:
                s.failures.append(Failure(why=f"{el.name!r} cannot be created by mention", fix="cut"))
            else:
                out.created += [i for i in res.ids if i not in out.created]
        elif tier == "T1b":
            speaker = next((a for a in s.decl.about if a in present_npcs(ctx.state)), None)
            c = Claim.model_validate({"subject": speaker or WORLD, "class": "knowledge", "predicate": "knows",
                                      "value": el.name})
            ans = _ask_oracle(ctx, record, c, odds="likely" if speaker else "unlikely")
            if ans != "yes":
                s.failures.append(Failure(why=f"{el.name!r} is not so (the Oracle settled it)", fix="redraft",
                                          store_value=f"not so: {el.name}" if ans else "say they do not know"))
        elif not t2_delivered(el, s.decl, idx):
            s.failures.append(Failure(why=f"a new {el.element_kind or 'element'} ({el.name}) that no record line "
                                      "delivers (12.14.13)", fix="cut"))


def _subject_given(c: Claim, s: DeclaredSentence, idx: SceneIndex, pc: str | None) -> Claim:  # rule: 12.3.1
    """A claim in a declared sentence takes the declared subject when the sentence declares exactly one subject
    besides the PC and the audit read the claim as about someone else or no one (never guessed)."""
    declared = [e for e in idx.subjects(s) if e != pc]
    if len(declared) == 1 and c.subject != pc and c.subject not in declared and not s.new:
        return c.model_copy(update={"subject": declared[0]})
    return c


def _polarity(s: DeclaredSentence, record: AdjudicationRecord, its: Mapping[str, RecordItem]) -> list[Failure]:
    # rule: 12.3.1
    """Each cited beat line, judged with its subject given: the sentence must not plainly say the opposite of the
    beat's degree (P-112). Other refs are sources for the claims that cite them (`check_claims(cited=)`)."""
    out = []
    for r in s.refs:
        it = its.get(r)
        if it is not None and it.kind == "beat" and it.beat is not None:
            degree = beat_polarity(s.text, record.beats[it.beat])
            if degree:
                out.append(Failure(why=f"contradicts the attempt's result ({degree})", fix="redraft",
                                   store_value=degree))
    return out


def _judge(ctx: TurnContext, record: AdjudicationRecord, turn: _Turn, sents: list[_Sent], todo: Sequence[int],
           out: NarrationResult, version: dict[str, Any]) -> None:  # rule: PR-12-2
    # rule: 12.3.1a
    """PR-12-2 steps 1-6 for the sentences in `todo`: scan each (12.3.1a), write its new elements by tier (T8), run
    the audit (the Checker) on them, resolve every claim with its subject given, judge with `check_claims`, and
    turn each verdict into the sentence's failure and fix (12.3.3's table)."""
    tx = ctx.need_tx()
    rules = ctx.rules
    pc = record.pc
    by_handle = {it.handle: it for it in turn.items}
    idx = SceneIndex.of(tx.state, turn.items)
    names = _names(ctx, list(tx.state.entities))
    for i in todo:
        s = sents[i]
        s.failures = []
        valid = set(by_handle) | set(idx.facts)
        s.decl.refs = [r for r in s.decl.refs if r in valid]
        s.decl.about = [a for a in s.decl.about if a in tx.state.entities]
        scan = scan_sentence(s.decl, idx, rules=rules, names=names)
        if scan.added_about:
            s.decl.about += scan.added_about
            turn.stats["added_about"] = turn.stats.get("added_about", 0) + len(scan.added_about)
            if s.decl.atmosphere:  # it names someone: declared now, not atmosphere (12.3.1a item 2)
                s.decl.atmosphere = False
                turn.stats["atmosphere_named"] = turn.stats.get("atmosphere_named", 0) + 1
        turn.stats["undeclared_new"] = turn.stats.get("undeclared_new", 0) + scan.undeclared_new
        s.failures += scan.failures
        _write_new(ctx, record, s, idx, out)
        safe = screen_safety(s.decl.text, tx.state)
        if not safe.ok and safe.cuts:
            s.failures.append(Failure(why="crosses a line the player set (12.5.6)", fix="cut"))
        echoed = echoed_quotes(s.decl.text, [p.text for p in record.parts])
        if echoed and i > 0:
            s.failures.append(Failure(why=f"an NPC answers with the player's own words ({echoed[0]})",
                                      fix="redraft", store_value="write the NPC's own reply"))
    idx = SceneIndex.of(tx.state, turn.items)  # with this round's new elements
    chk = checker_role.check_draft(ctx, "", player_message=turn.player_message, created=out.created,
                                   exchanges=turn.exchanges, sentences=[sents[i].decl.text for i in todo])
    version["screen_flags"] = chk.screen
    claims: list[Claim] = []
    order = list(todo)
    for c in chk.claims:
        if not 0 <= c.sentence < len(order):
            continue
        g = order[c.sentence]
        s = sents[g].decl
        if s.atmosphere and not s.declared and c.cls != "location_time" and (
                (c.subject == "unknown" and c.cls == "action") or not c.asserts_change):
            continue  # 12.3.1, 12.11.9: atmosphere (an unnamed crowd's murmur, heads turning) is never a claim
        c = _subject_given(c.model_copy(update={"sentence": g}), s, idx, pc)
        if c.subject not in idx.subjects(s) and c.subject != pc:
            turn.stats["audit_undeclared"] = turn.stats.get("audit_undeclared", 0) + 1
        claims.append(c)
    for g in todo:
        sents[g].failures += _polarity(sents[g].decl, record, by_handle)
        sents[g].verdicts = []
    # what each sentence cites: its record lines, and its view facts as lines about their subject (12.2.10: a
    # stated value cites the view's id; a claim restating what it cites is covered by the declaration)
    facts = tx.state.facts
    cited = {g: [by_handle[r] if r in by_handle else
                 RecordItem(handle=r, kind="note", must_name=False, entities=[facts[r].subject],
                            text=f"{facts[r].predicate.replace('_', ' ')} {facts[r].value}")
                 for r in sents[g].decl.refs if r in by_handle or r in facts] for g in todo}
    verdicts = check_claims(claims, tx.state, record, chk.scene_ids, rules=rules, cited=cited)
    verdicts = _apply_writes(ctx, record, claims, verdicts)
    verdicts = _settle(ctx, record, claims, verdicts)
    for v in verdicts:
        c = claims[v.claim]
        sents[c.sentence].verdicts.append({**v.model_dump(mode="json"), "sentence": c.sentence, "class": c.cls})
        if v.verdict != "supported":
            fix = "cut" if v.fix in _CUT_FIXES else "redraft"
            sents[c.sentence].failures.append(Failure(why=f"{v.verdict} ({c.cls}: {c.predicate} {c.value})".strip(),
                                                      fix=fix, store_value=v.store_value))
    version["claims"] = _dump(claims)
    version["verdicts"] = _dump(verdicts)
    version["checks"] = {str(g): [f.model_dump() for f in sents[g].failures] for g in todo}


def _dump(items: Sequence[BaseModel]) -> list[dict[str, Any]]:
    return [x.model_dump(mode="json", by_alias=True) for x in items]


def _names(ctx: TurnContext, ids: Sequence[str]) -> list[str]:
    st = ctx.state
    return [st.entities[i].name for i in ids if i in st.entities]


def _unanswered(record: AdjudicationRecord, text: str) -> list[str]:  # rule: 12.2.7
    from engine.audit.screen import _acknowledged

    return [f"answer: {q}" for q in _acknowledged(record, text)]


def _text(sents: Sequence[_Sent]) -> str:
    return " ".join(s.decl.text for s in sents if not s.dropped and s.decl.text)


def _snapshot(kind: str, sents: Sequence[_Sent], **extra: Any) -> dict[str, Any]:
    return {"kind": kind, "text": _text(sents), "sentences": [s.decl.model_dump() for s in sents if not s.dropped],
            "mentions": [], "claims": [], "verdicts": [], **extra}


def narrate_checked(ctx: TurnContext, record: AdjudicationRecord, *, player_message: str = "",
                    purpose: Purpose = "turn", exchanges: Sequence[str | tuple[str, str]] = (),
                    pause_blocks: Sequence[OofBlock] = (), extra: Sequence[str] = (),
                    fallback_text: str | None = None) -> NarrationResult:  # rule: PR-12-1
    # rule: PR-12-2
    # rule: 12.3.3
    """T7 draft (declared sentences) → judge each sentence (scans, tiers, audit, verdicts, coverage) → cut what a
    cut fixes, repair the rest one narrow call per round (at most `max_redrafts`) → cut what still fails and state
    each uncited must-name item by its rendered line → the plain fallback when no sentence passed → T10 screen.
    Needs the turn's open transaction (`ctx.tx`). `fallback_text` replaces the record-built fallback (a recap falls
    back to its RECAP block: empty fiction)."""
    from engine.dm.npc_layer import ensure_activities

    tx = ctx.need_tx()
    rules = ctx.rules
    max_r = _max_redrafts(rules)
    out = NarrationResult()
    if purpose in ("turn", "scene_open", "opening"):
        ensure_activities(ctx, record)  # 12.11.9 step 1: every present NPC's activity is a record line
    turn = _Turn(items=narrator_role.record_items(tx.state, record), player_message=player_message,
                 exchanges=list(exchanges))
    must = [it.handle for it in turn.items if it.must_name]
    sents: list[_Sent] = []
    had_prompt = False
    try:
        nd = narrator_role.draft(ctx, record, player_message=player_message, exchanges=exchanges, purpose=purpose,
                                 extra=extra, items=turn.items)
        sents = [_Sent(decl=s) for s in nd.sentences]
        had_prompt = bool(sents) and sents[-1].decl.text.rstrip("\"”’' ").endswith("?")
        version = _snapshot("draft", sents)
        out.draft_versions.append(version)
        _judge(ctx, record, turn, sents, range(len(sents)), out, version)
    except ModelInvalid as exc:
        return _fallback(ctx, record, out, [], [f"{exc.__class__.__name__}: {exc}"], fallback_text)
    rounds = 0
    while True:
        for s in sents:  # a cut is done by code at once, never redrafted (12.3.3)
            s.dropped = s.dropped or s.cut
        live = [s for s in sents if not s.dropped]
        missing = coverage([s.decl for s in live], must) + _unanswered(record, _text(sents))
        redo = {str(i): s for i, s in enumerate(sents) if not s.dropped and not s.ok}
        if (not redo and not missing) or rounds >= max_r:
            break
        rounds += 1
        words = {it.handle: it.render or it.text for it in turn.items}
        repair = Repair(failing={i: s.decl.text for i, s in redo.items()},
                        reasons={i: [f"{f.why}" + (f"; use: {f.store_value}" if f.store_value else "")
                                     for f in s.failures] for i, s in redo.items()},
                        missing=[f"{h} ({words.get(h, '')})" if h in words else h for h in missing])
        try:
            nd = narrator_role.draft(ctx, record, player_message=player_message, exchanges=exchanges,
                                     purpose=purpose, repair=repair, items=turn.items)
        except ModelInvalid:
            break
        todo: list[int] = []
        for key, decl in nd.repairs:
            if key in redo and decl.text.strip():
                i = int(key)
                old = sents[i]
                if not decl.refs:  # a replacement keeps its place, so the lines the sentence narrated (12.3.3)
                    decl.refs = [r for r in old.decl.refs if r in {it.handle for it in turn.items}]
                sents[i] = _Sent(decl=decl, replaced=old.replaced + 1,
                                 cited_before=list(dict.fromkeys([*old.cited_before, *old.decl.refs])))
                todo.append(i)
            elif key in redo:
                sents[int(key)].dropped = True
            elif key == "add" and decl.text.strip():
                at = len(sents) - (1 if had_prompt and sents and not sents[-1].dropped else 0)
                sents.insert(at, _Sent(decl=decl))
                todo = [t + 1 if t >= at else t for t in todo] + [at]
        version = _snapshot("repair", sents, fixes=[f"[{i}] {'; '.join(r)}" for i, r in repair.reasons.items()],
                            missing=repair.missing)
        out.draft_versions.append(version)
        if todo:
            try:
                _judge(ctx, record, turn, sents, sorted(todo), out, version)
            except ModelInvalid:
                break
    return _deliver(ctx, record, turn, sents, must, out, had_prompt, pause_blocks, fallback_text, rounds)


def _deliver(ctx: TurnContext, record: AdjudicationRecord, turn: _Turn, sents: list[_Sent], must: Sequence[str],
             out: NarrationResult, had_prompt: bool, pause_blocks: Sequence[OofBlock], fallback_text: str | None,
             rounds: int) -> NarrationResult:  # rule: 12.3.3
    """After the repairs: cut what still fails; state each must-name item no remaining sentence cites by its rendered
    line, in the place of the sentence that cited it; restore the open prompt only if repair cut it; the plain
    fallback when no drafted sentence passed (12.3.3)."""
    tx = ctx.need_tx()
    reasons = [f"[{i}] {f.why}" for i, s in enumerate(sents) for f in s.failures if not s.dropped]
    cut_any = any(s.dropped or not s.ok for s in sents)
    cited_at: dict[str, int] = {}
    for i, s in enumerate(sents):
        for r in [*s.decl.refs, *s.cited_before]:
            cited_at.setdefault(r, i)
        if not s.ok:
            s.dropped = True
    kept = [s for s in sents if not s.dropped]
    prose = [s for s in kept if not (s.decl.text.rstrip().endswith("?") and not s.decl.declared)]
    if not prose:
        return _fallback(ctx, record, out, [], reasons or ["no drafted sentence passed"], fallback_text)
    by_handle = {it.handle: it for it in turn.items}
    rendered: list[str] = []
    for h in coverage([s.decl for s in kept], must):
        line = by_handle[h].render
        if not line:
            continue
        rendered.append(h)
        live = [i for i, s in enumerate(sents) if not s.dropped]
        end = live[-1] if live and sents[live[-1]].decl.text.rstrip().endswith("?") else len(sents)
        at = cited_at.get(h, end)  # where the sentence that cited it stood, else before the closing question
        sents.insert(min(at, len(sents)), _Sent(decl=DeclaredSentence(text=line, refs=[h])))
        cited_at = {k: (v + 1 if v >= at else v) for k, v in cited_at.items()}
    final = [s for s in sents if not s.dropped]
    text = " ".join(s.decl.text for s in final)
    if had_prompt and record.pause is None and not text.rstrip("\"”’' ").endswith("?"):
        text += " What do you do?"  # 12.3.3: the open prompt (12.14.9), restored by code because repair cut it
    if cut_any or rendered:
        out.draft_versions.append({"kind": "render" if rendered else "cut", "text": text, "mentions": [],
                                   "claims": [], "verdicts": [], "rendered": rendered, "reasons": reasons})
    if rendered:  # 12.3.3: a rendered line was needed
        ruling = RulingRecord(signature="claim_check.rendered_line", kind="rule_conflict", review_flag=True,
                              situation="a must-name item was stated by its rendered line (12.3.3)",
                              result={"outcome": "rendered_line", "handles": rendered, "reasons": reasons},
                              tags=["claim_check"])
        tx.add(log_ruling(ruling, tx.mint, store=ctx.store, staged=tx.events, turn_id=ctx.turn_id, rule_id="12.3.3"))
        out.review_flag = True
    names = _names(ctx, list(tx.state.entities))
    res = screen_draft(text, flags={"intent_acknowledged": True, "next_step_exists": True}, record=record,
                       safety=screen_safety(text, tx.state), pause_blocks_text=[b.text for b in pause_blocks],
                       rules=ctx.rules, names=names)
    out.screen = res.screen
    out.fiction = text
    out.verdicts = [v for s in final for v in s.verdicts]  # the delivered sentences' verdicts
    out.draft_versions[-1]["screen"] = res.reasons
    out.draft_versions[-1]["stats"] = dict(turn.stats, rounds=rounds)
    return out


def _fallback(ctx: TurnContext, record: AdjudicationRecord, out: NarrationResult, verdicts: Sequence[Verdict],
              reasons: Sequence[str], fallback_text: str | None) -> NarrationResult:  # rule: 12.3.3
    """The plain fallback (12.3.3): no drafted sentence passed, so every must-name item is rendered; `review_flag`,
    a `rule_conflict` ruling logged."""
    tx = ctx.need_tx()
    st = tx.state
    # the name as the PC knows it ("the wagon driver" until told), never an unlearned name (12.10.2, P-096)
    fb = plain_fallback(record, names=narrator_role.names_for(st), verdicts=verdicts)
    ruling = fb.ruling.model_copy(update={"result": {**fb.ruling.result, "reasons": list(reasons)}})
    tx.add(log_ruling(ruling, tx.mint, store=ctx.store, staged=tx.events, turn_id=ctx.turn_id, rule_id="12.3.3"))
    out.fiction = fb.fiction if fallback_text is None else fallback_text
    out.fallback_used = True
    out.review_flag = fb.review_flag
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


_PER_BEAT = ("RESULT", "REDIRECT", "NEAR_MISS")


def _for_beat(block: OofBlock, beat: str) -> OofBlock:
    """'[RESULT] Learn what was stolen: d20 12 → 16 vs 15 · success': the beat's restatement in a few words."""
    words = oof.short_text(re.sub(r"\s*\([^()]*\)", "", beat or ""), 48).strip()
    if not words or block.kind not in _PER_BEAT or "] " not in block.text:
        return block
    head, rest = block.text.split("] ", 1)
    return block.model_copy(update={"text": f"{head}] {words[:1].upper()}{words[1:]}: {rest}"})


def turn_blocks(ctx: TurnContext, oof_items: Sequence[dict[str, str]], record: AdjudicationRecord,
                pause: PauseRecord | None) -> tuple[list[OofBlock], list[OofBlock]]:  # rule: 12.15
    """(all blocks in 12.15 order, the pause's own blocks). The items T4–T5 owed, the open pause's block rendered
    from state in place of its one-line summary, and any warning block the record carries."""
    items = list(oof_items)
    owned: list[OofBlock] = []
    # with two or more beats, each RESULT / REDIRECT / NEAR MISS says which action it belongs to (P-104)
    multi = len(record.beats) > 1
    if pause is not None:
        owned = pause_blocks(ctx, pause, items)
        for kind in _PAUSE_ITEM.get(str(pause.detail.get("stage") or pause.kind), ()):
            idx = max((i for i, it in enumerate(items) if it["kind"] == kind), default=None)
            if idx is not None:
                it = items.pop(idx)
                if multi:
                    owned = [_for_beat(b, it.get("beat", "")) if b.kind == kind else b for b in owned]
    # two beats refused for the same reason owe one block, not two copies (12.15: each block once)
    rendered = [(_item_block(ctx, i), i.get("beat", "")) for i in items]
    twice = {b.text for b, _ in rendered if sum(c.text == b.text for c, _ in rendered) > 1}
    blocks = list({b.text: _for_beat(b, beat if multi and b.text not in twice else "")
                   for b, beat in rendered}.values())
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
    from engine.dm.roles.world import present_npcs
    from engine.world.scenes import cut_due, end_scene, note_cut, note_turn, turn_is_quiet

    st = ctx.state
    if st.scene is None:
        return []
    tctx = ctx.time_ctx()
    evs = [e for e in (ctx.store.event(s) for s in writes) if e is not None]
    # someone answered: an NPC's response row, or the PC spoke with someone here (the narrator gives their reply)
    answered = bool(record.npc_actions) or (any(p.cls == "SPEECH" for p in record.parts) and bool(present_npcs(st)))
    note_turn(tctx, quiet=turn_is_quiet([p.cls for p in record.parts], evs, answered=answered))
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
