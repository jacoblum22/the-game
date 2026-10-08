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
import zlib
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from engine.audit.claims import Claim, Verdict, beat_polarity, check_claims, owed_blocks
from engine.audit.declare import (
    DeclaredSentence,
    Failure,
    SceneIndex,
    coverage,
    known_as,
    mention_of,
    pc_quotes,
    scan_sentence,
    t2_delivered,
    tier_of,
    voices,
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
    claim_log: list[dict[str, Any]] = Field(default_factory=list)  # 12.3.1b: delivered but logged (TurnRecord)
    said: list[dict[str, Any]] = Field(default_factory=list)  # 12.3.1b item 1: speech as testimony (TurnRecord)


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
    cited_before: list[str] = Field(default_factory=list)  # handles the sentence it replaced cited (its place)
    used: list[str] = Field(default_factory=list)  # detail facts it states (written or restated): usage marks at T12

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
    log: list[dict[str, Any]] = Field(default_factory=list)  # the claim log (12.3.1b)


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


def _log(ctx: TurnContext, turn: _Turn, sentence: int, cls: str, verdict: str, store_value: Any = None,
         **extra: Any) -> None:  # rule: 12.3.1b
    """One claim-log record (12.3.1b): delivered as drafted, kept for review and disputes (12.3.6)."""
    turn.log.append({"turn": ctx.turn_id, "sentence": sentence, "class": cls, "verdict": verdict,
                     "store_value": None if store_value is None else str(store_value), **extra})


_COARSE_POSTURE = re.compile(r"\b(held|pinned|restrained|mounted|bound|grip)\b", re.I)


def _blocking_slot(slot: str, prior: Any) -> bool:  # rule: 12.3.1b
    """A detail clash that still redraws (12.3.1b item 2): a held weapon or tool, a coarse posture (DL-12-77)."""
    from engine.audit.claims import relevant_item

    return (slot == "held" and relevant_item(str(prior))) or (slot == "posture" and bool(
        _COARSE_POSTURE.search(str(prior))))


def _in_speech(name: str, s: DeclaredSentence) -> bool:  # rule: 12.3.1b
    """The element is named only inside the sentence's speech: testimony, never written (12.3.1b item 1)."""
    from engine.audit import text as atx

    narration, speech = voices(s)
    return bool(speech) and atx.covers(name, " ".join(speech), ratio=0.6) and not (
        narration and atx.covers(name, narration, ratio=0.6))


def _write_new(ctx: TurnContext, record: AdjudicationRecord, s: _Sent, idx: SceneIndex,
               out: NarrationResult, turn: _Turn, i: int) -> None:  # rule: PR-00-7
    # rule: 12.14.13
    # rule: 12.3.1b
    """PR-00-7 step 2: each declared new element by its tier. T1a is written on mention with the properties the
    sentence states (logged when it cannot be written); T1b is proposed and settled by the Oracle (Likely when a
    present NPC the sentence is about says it, else Unlikely; a "no" is a redraft); T2 in the narrator's voice
    passes only when a cited record line delivers it, else it is cut. Named only in speech, any tier is testimony:
    logged, never written (12.3.1b). A clash with a known person's stored detail is logged and the store keeps its
    value, unless the slot is on the blocking list."""
    from engine.dm.mentions import Mention, MentionResult, profile_diff
    from engine.dm.roles.world import present_npcs

    for el in s.decl.new:
        known = known_as(el, idx)
        if known is not None:  # one of the scene's own: spoken of, not new; what it states is diffed (PR-00-7)
            s.decl.about = list(dict.fromkeys([*s.decl.about, known]))
            if el.implied and known in ctx.need_tx().state.entities:
                # ponytail: a cited record line about them stands for "an event that explains the change"
                because = next((r for r in s.decl.refs if known in idx.handle_entities.get(r, ())), None)
                res = MentionResult()
                tx = ctx.need_tx()
                start = len(tx.events)
                m = Mention.model_validate({"kind": "npc", "name": el.name,
                                            "implied": [i.model_dump() for i in el.implied]})
                profile_diff(m, known, tx=tx, rules=ctx.rules, res=res, because=because)
                record.add_writes(tx.events[start:])
                s.used += res.details_used
                for name, slot, prior in res.contradictions:
                    if _blocking_slot(slot, prior):
                        s.failures.append(Failure(why=f"{name}'s {slot} is established otherwise", fix="redraft",
                                                  store_value=prior))
                    else:
                        _log(ctx, turn, i, "detail", "contradicted", prior, subject=known, slot=slot)
            continue
        tier = tier_of(el, ctx.rules)
        if _in_speech(el.name, s.decl):
            _log(ctx, turn, i, "speech", "testimony", None, element=el.name, tier=tier)
            continue
        if tier == "T1a":
            m = mention_of(el)
            res = _write_mentions(ctx, record, [m]) if m is not None else None
            if res is None or res.refused:
                _log(ctx, turn, i, "new_element", "unwritten", None, element=el.name)
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


def _polarity(text: str, s: DeclaredSentence, record: AdjudicationRecord,
              its: Mapping[str, RecordItem]) -> list[Failure]:  # rule: 12.3.1
    # rule: 12.3.1a
    """Outcome words against the frame's degree (P-112), on the narrator's words: each cited beat line; an
    uncited sentence against the turn's only rolled beat (a code scan, 12.3.1a)."""
    beats = [record.beats[it.beat] for r in s.refs if (it := its.get(r)) is not None and it.kind == "beat"
             and it.beat is not None]
    if not s.refs:
        rolled = [b for b in record.beats if b.rolled and b.degree]
        beats = rolled if len(rolled) == 1 else []
    out = []
    for b in beats:
        degree = beat_polarity(text, b, record.pause) if text else None
        if degree:
            out.append(Failure(why=f"contradicts the attempt's result ({degree})", fix="redraft", store_value=degree))
    return out


def _count(turn: _Turn, key: str, n: int = 1) -> None:
    turn.stats[key] = turn.stats.get(key, 0) + n


def audit_mode(ctx: TurnContext) -> str:  # rule: 12.3.1
    # rule: OEQ-12-23
    """'sampled' on 1 turn in `claim_check.audit.full_extraction_every`, picked by the turn id's crc32 (so it draws
    nothing from the game's dice), else 'off'. The sampled audit runs after delivery and only logs (DL-12-83)."""
    cfg = (ctx.rules.pacing.get("claim_check") or {}).get("audit") or {}
    every = int(cfg.get("full_extraction_every") or 0)
    return "sampled" if every and zlib.crc32((ctx.turn_id or "").encode()) % every == 0 else "off"


def _sample(ctx: TurnContext, record: AdjudicationRecord, turn: _Turn, final: Sequence[_Sent],
            out: NarrationResult) -> None:  # rule: 12.3.1
    # rule: 12.3.1b
    # rule: OEQ-12-23
    """The sampled audit (12.3.1 source 2, DL-12-83), after delivery: the diff and the full extraction on the
    delivered sentences; every full-extraction claim is judged (`check_claims(texts=)`, a certain subject only)
    and logged. A failing narrator-voice claim on the blocking list with a certain subject is a `blocking_miss`;
    nothing is cut, redrafted or written."""
    from engine.audit import text as atx
    from engine.audit.claims import blocking

    decls = [s.decl for s in final if s.decl.text]
    if audit_mode(ctx) != "sampled" or not decls:
        return
    kw: dict[str, Any] = {"player_message": turn.player_message, "created": out.created, "exchanges": turn.exchanges,
                          "sentences": [d.text for d in decls], "decls": decls, "items": turn.items}
    try:
        diff = checker_role.check_draft(ctx, "", **kw)
        full = checker_role.check_draft(ctx, "", full=True, **kw)
    except ModelInvalid:
        _count(turn, "sample_failed")
        return
    st = ctx.need_tx().state
    by_handle = {it.handle: it for it in turn.items}
    # what each sentence cites: its record lines, and its view facts as lines about their subject (12.2.10)
    cited = {g: [by_handle[r] if r in by_handle else
                 RecordItem(handle=r, kind="note", must_name=False, entities=[st.facts[r].subject],
                            text=f"{st.facts[r].predicate.replace('_', ' ')} {st.facts[r].value}")
                 for r in d.refs if r in by_handle or r in st.facts] for g, d in enumerate(decls)}
    verdicts = check_claims(full.claims, st, record, full.scene_ids, rules=ctx.rules, cited=cited,
                            texts={g: d.text for g, d in enumerate(decls)})
    _count(turn, "sample_turns")
    _count(turn, "sample_diff_findings", len(diff.claims) + len(diff.undeclared))
    for c, v in zip(full.claims, verdicts, strict=True):
        narration, speech = voices(decls[c.sentence])
        if speech and not (narration and atx.covers(c.text, narration, ratio=0.6)):
            _log(ctx, turn, c.sentence, c.cls, "testimony", None, source="sample")
            continue
        miss = v.disposition != "supported" and not v.uncertain and c.subject in st.entities \
            and blocking(c, v, ctx.rules)
        _count(turn, "sample_misses", int(miss))
        _log(ctx, turn, c.sentence, c.cls, v.disposition, v.store_value, source="sample", blocking_miss=miss)
        out.verdicts.append({**v.model_dump(mode="json"), "sentence": c.sentence, "class": c.cls})
    for u in diff.undeclared:
        _log(ctx, turn, int(u.get("sentence") or 0), "new_element", "undeclared", None, source="sample",
             element=str(u.get("name") or ""), element_kind=str(u.get("element_kind") or ""))
    out.draft_versions[-1]["sample"] = {"claims": _dump(full.claims), "verdicts": _dump(verdicts)}


def _speech(ctx: TurnContext, record: AdjudicationRecord, turn: _Turn, s: _Sent, i: int) -> None:  # rule: 12.3.1b
    """12.3.1b item 1's three checks, all code: the speaker is present, is not the PC, and no quoted words in the
    PC's mouth go beyond the player's message (`pc_agency`, a cut). Speech is never checked for truth."""
    from engine.audit import text as atx
    from engine.world.scenes import cast_present

    _, speech = voices(s.decl)
    if not speech:
        return
    sp = s.decl.speaker
    pc_words = speech if sp is not None and sp == record.pc else pc_quotes(s.decl)
    for q in pc_words:
        if not (turn.player_message and atx.covers(q, turn.player_message, ratio=0.8)):
            s.failures.append(Failure(why="puts words in the PC's mouth the player did not say (12.14.3)", fix="cut"))
            break
    if sp is not None and sp != record.pc and sp not in cast_present(ctx.need_tx().state):
        s.failures.append(Failure(why="the speaker is not here", fix="redraft",
                                  store_value="give the words to someone present"))
    elif sp is None and not pc_words:
        _log(ctx, turn, i, "speech", "no_speaker")


def _judge(ctx: TurnContext, record: AdjudicationRecord, turn: _Turn, sents: list[_Sent], todo: Sequence[int],
           out: NarrationResult, version: dict[str, Any]) -> None:  # rule: PR-12-2
    # rule: 12.3.1a
    # rule: 12.3.1b
    """PR-12-2 for the sentences in `todo`, by code only (no per-turn audit, DL-12-83): the code scans on the
    narrator's voice (names, numerals, sealed strings, outcome words; 12.3.1a), the speech checks, new elements by
    tier (T8), safety. Only blocking-list hits fail a sentence; the rest is logged (12.3.1b)."""
    tx = ctx.need_tx()
    rules = ctx.rules
    by_handle = {it.handle: it for it in turn.items}
    idx = SceneIndex.of(tx.state, turn.items)
    names = _names(ctx, list(tx.state.entities))
    for i in todo:
        s = sents[i]
        s.failures = []
        valid = set(by_handle) | set(idx.facts)
        s.decl.refs = [r for r in s.decl.refs if r in valid]
        s.decl.about = [a for a in s.decl.about if a in tx.state.entities]
        if s.decl.speaker is not None and s.decl.speaker not in tx.state.entities:
            s.decl.speaker = None
        scan = scan_sentence(s.decl, idx, rules=rules, names=names)
        if scan.added_about:
            s.decl.about += scan.added_about
            _count(turn, "added_about", len(scan.added_about))
            if s.decl.atmosphere:  # it names someone: declared now, not atmosphere (12.3.1a item 2)
                s.decl.atmosphere = False
                _count(turn, "atmosphere_named")
        _count(turn, "undeclared_new", scan.undeclared_new)
        s.failures += scan.failures
        for cls, why in scan.logged:
            _log(ctx, turn, i, cls, "logged", why)
        _speech(ctx, record, turn, s, i)
        _write_new(ctx, record, s, idx, out, turn, i)
        safe = screen_safety(s.decl.text, tx.state)
        if not safe.ok and safe.cuts:
            s.failures.append(Failure(why="crosses a line the player set (12.5.6)", fix="cut"))
        echoed = echoed_quotes(s.decl.text, [p.text for p in record.parts])
        if echoed and i > 0:
            _log(ctx, turn, i, "speech", "echoes the player's words", echoed[0])
        s.failures += _polarity(voices(s.decl)[0], s.decl, record, by_handle)
        if not s.decl.declared and not s.decl.atmosphere and not s.failures                 and not s.decl.text.rstrip("\"”’' ").endswith("?"):  # the open prompt is no claim (12.14.9)
            _log(ctx, turn, i, "undeclared", "delivered")  # 12.3.1a: no scan hit, delivered as drafted
    version["checks"] = {str(g): [f.model_dump() for f in sents[g].failures] for g in todo}


def _dump(items: Sequence[BaseModel]) -> list[dict[str, Any]]:
    return [x.model_dump(mode="json", by_alias=True) for x in items]


def _names(ctx: TurnContext, ids: Sequence[str]) -> list[str]:
    st = ctx.state
    return [st.entities[i].name for i in ids if i in st.entities]


def _unanswered(record: AdjudicationRecord, text: str) -> list[str]:  # rule: 12.2.7
    """Questions with no answer in the fiction, for the repair. Words said to someone the PC then left (a new scene
    opened this turn and no one answered them) are not owed: asking them again after arriving replays an old
    question as if just said."""
    from engine.audit.screen import _acknowledged

    left = {p.text for p in record.parts if p.cls == "SPEECH"} if record.scene.started and not record.npc_actions \
        else set()
    return [f"answer: {q}" for q in _acknowledged(record, text) if q not in left]


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
    _mark_used(ctx, final, record, turn.items)
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
    out.draft_versions[-1]["screen"] = res.reasons
    _said(ctx, record, final, out)
    _sample(ctx, record, turn, final, out)  # after delivery: it only logs (DL-12-83)
    out.claim_log = turn.log
    out.draft_versions[-1]["stats"] = dict(turn.stats, rounds=rounds)
    return out


def _said(ctx: TurnContext, record: AdjudicationRecord, final: Sequence[_Sent],
          out: NarrationResult) -> None:  # rule: 12.3.1b
    """Delivered speech as `said` records `{speaker, turn, words, about}`, never facts (12.3.1b item 1). A stored
    name the PC did not know, heard in an NPC's words, is known from now on (`how: heard`)."""
    from engine.audit import text as atx
    from engine.store.views import name_known
    from engine.world.social import learn_name

    st = ctx.need_tx().state
    for s in final:
        _, speech = voices(s.decl)
        if not speech or pc_quotes(s.decl) or (s.decl.speaker and s.decl.speaker == record.pc):
            continue
        words = " ".join(speech)
        if s.decl.speaker is None and atx.covers(words, " ".join(p.text for p in record.parts), ratio=0.8):
            continue  # the player's own words quoted back: not testimony
        out.said.append({"speaker": s.decl.speaker, "turn": ctx.turn_id, "words": words, "about": list(s.decl.about)})
        low = words.lower()
        for eid, e in list(st.entities.items()):
            if record.pc and e.kind in ("npc", "companion", "adversary") and e.name and not name_known(st, eid) \
                    and re.search(rf"\b{re.escape(e.name.lower())}\b", low):
                learn_name(ctx.time_ctx(), record.pc, eid, "heard")


def _mark_used(ctx: TurnContext, final: Sequence[_Sent], record: AdjudicationRecord | None = None,
               items: Sequence[RecordItem] = ()) -> None:  # rule: 00.6.6a
    # rule: 12.14.11
    """T12 usage marks (00.6.6a item 5, DL-12-76): each established detail a delivered sentence states (a cited
    `detail.*` fact, a cited scene-state line's slot, or one its words wrote or restated) gets `last_used` = this
    turn; freshness reads them."""
    from engine.store.details import used_event
    from engine.store.projection import DETAIL

    tx = ctx.need_tx()
    st = tx.state
    facts = st.facts
    used = [r for s in final for r in s.decl.refs if r in facts and facts[r].predicate.startswith(DETAIL)]
    used += [u for s in final for u in s.used if u in facts]
    lines = {it.handle: record.activities[it.index] for it in items if it.kind == "activity"} if record else {}
    for r in (r for s in final for r in s.decl.refs if r in lines):  # a scene-state line said (12.11.9, T-12-18)
        ref = st.details.get(lines[r].npc, {}).get(lines[r].slot)
        if ref is not None:
            used.append(ref.fact_id)
    if used:
        tx.add(used_event(list(dict.fromkeys(used))))


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
        "claim_log": narr.claim_log, "said": narr.said,
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
