"""The narration pass of the turn loop: PR-12-1 T7–T12 (draft, mention, check, screen, deliver, record).

    adj = run_turn(ctx, message)                    # T1–T6 (engine/dm/turn.py)
    out = narrate_turn(ctx, adj, message)           # T7–T12 → TurnOutcome(response, turn_record, narration)
    out.response.text()                             # fiction, then the 12.15 blocks (the pause block last)

`engine.dm.turn.play_turn(ctx, message)` / `play_answer(ctx, choice_id)` wrap both. `narrate_checked` is the
draft → check → (one revision) → deliver loop on its own, for any narration that must pass the checks (a recap, a
scene opening, the first opening; 12.5.3, 12.16.16). The narrator writes one passage and a side list (12.3.1); code
checks the whole passage and cuts or revises at most once (12.3.3; spec 019).

T7–T12 run in one store transaction under the turn's id (T8's write-on-mention, the fallback's ruling, T12's
counters and scene cut); a model failure there writes nothing after T6 and raises, and the turn row keeps the
input; `engine.dm.turn.play_turn` / `play_answer` then keep the turn's record as meta `narration_pending` and
`engine.dm.turn.resume_narration` re-runs T7–T12 from the written state on the next call (engine-api.md Errors).
"""

from __future__ import annotations

import re
import zlib
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from engine.audit.claims import Claim, Verdict, check_claims, owed_blocks, passage_beat
from engine.audit.declare import (
    Failure,
    NewElement,
    Passage,
    SceneIndex,
    Sentence,
    coverage,
    known_as,
    mention_of,
    pc_quotes,
    quote,
    scan_sentence,
    sentences_of,
    t2_delivered,
    tier_of,
    unquoted,
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
from engine.dm.roles.narrator import Purpose, Revision
from engine.llm.base import ModelInvalid
from engine.resolve.rulings import RulingRecord, log_ruling
from engine.store.events import WORLD, Event, PauseRecord
from engine.store.records import TurnRecord

MAX_REVISIONS = 1  # fallback only; the rules value is pacing.yaml#claim_check.max_revisions (12.3.3)
FRAME_NEXT = "scene.frame_next"  # meta: a cut reached at T12; the next turn frames the next scene (PR-12-1 T12)


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
    """One sentence of the passage while it is judged (12.3.1b): code's split, so a failure has a place and a cut
    removes just it (12.3.3)."""

    decl: Sentence
    failures: list[Failure] = Field(default_factory=list)
    dropped: bool = False
    orig: str = ""  # the sentence as it stands in the passage: where it is, so delivery keeps the passage (P1)

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
    heard: str = ""  # the player's words this turn, with the parts a pause carried (`pc_agency` compares with them)
    exchanges: list[Any] = Field(default_factory=list)
    stats: dict[str, int] = Field(default_factory=dict)
    log: list[dict[str, Any]] = Field(default_factory=list)  # the claim log (12.3.1b)


class _Draft(BaseModel):
    """One passage as judged: its sentences, the must-name handles its side list leaves out (12.3.1a item 1), and the
    words standing outside quote marks (item 2)."""

    passage: Passage
    sents: list[_Sent] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    unquoted: list[str] = Field(default_factory=list)

    def failed(self) -> list[str]:
        """What the one revision is told (12.3.3), in words; empty when nothing needs it (a cut alone does not)."""
        out = []
        if any(not s.cut and not s.ok for s in self.sents):
            for s in self.sents:
                for f in s.failures:
                    out.append(f'remove "{s.decl.text}": {f.why}' if s.cut else
                               f'"{s.decl.text}": {f.why}' + (f"; use: {f.store_value}" if f.store_value else ""))
        out += [f"not narrated: {h} (narrate it and list it in `covers`)" for h in self.missing]
        out += [f'speech outside quote marks: "{w}" (put the spoken words inside quote marks)' for w in self.unquoted]
        return list(dict.fromkeys(out))


def _max_revisions(rules: Any) -> int:
    return int(rules.pacing.get("claim_check", {}).get("max_revisions", MAX_REVISIONS))


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


def _in_speech(name: str, s: Sentence) -> bool:  # rule: 12.3.1b
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


def _count(turn: _Turn, key: str, n: int = 1) -> None:
    turn.stats[key] = turn.stats.get(key, 0) + n


def audit_mode(ctx: TurnContext) -> str:  # rule: 12.3.1
    # rule: OEQ-12-23
    """'sampled' on 1 turn in `claim_check.audit.full_extraction_every`, picked by the turn id's crc32 (so it draws
    nothing from the game's dice), else 'off'. The sampled audit runs after delivery and only logs (DL-12-83)."""
    cfg = (ctx.rules.pacing.get("claim_check") or {}).get("audit") or {}
    every = int(cfg.get("full_extraction_every") or 0)
    return "sampled" if every and zlib.crc32((ctx.turn_id or "").encode()) % every == 0 else "off"


def _sample(ctx: TurnContext, record: AdjudicationRecord, turn: _Turn, final: Sequence[_Sent], passage: Passage,
            out: NarrationResult) -> None:  # rule: 12.3.1
    # rule: 12.3.1b
    # rule: OEQ-12-23
    """The sampled audit (12.3.1 source 2, DL-12-83), after delivery: the diff (beyond the side list) and the full
    extraction on the delivered passage; every full-extraction claim is judged (`check_claims(texts=)`, a certain
    subject only) and logged. A failing narrator-voice claim on the blocking list with a certain subject is a
    `blocking_miss`; nothing is cut, revised or written."""
    from engine.audit import text as atx
    from engine.audit.claims import blocking

    decls = [s.decl for s in final if s.decl.text]
    if audit_mode(ctx) != "sampled" or not decls:
        return
    kw: dict[str, Any] = {"player_message": turn.player_message, "created": out.created, "exchanges": turn.exchanges,
                          "sentences": [d.text for d in decls], "passage": passage, "items": turn.items}
    try:
        diff = checker_role.check_draft(ctx, "", **kw)
        full = checker_role.check_draft(ctx, "", full=True, **kw)
    except ModelInvalid:
        _count(turn, "sample_failed")
        return
    st = ctx.need_tx().state
    covered = [it for it in turn.items if it.handle in passage.covers]
    verdicts = check_claims(full.claims, st, record, full.scene_ids, rules=ctx.rules,
                            cited={g: covered for g in range(len(decls))},
                            texts={g: d.text for g, d in enumerate(decls)})
    _count(turn, "sample_turns")
    _count(turn, "sample_diff_findings", len(diff.claims) + len(diff.undeclared) + len(diff.unexpressed))
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
    for u in diff.unexpressed:
        _log(ctx, turn, -1, "coverage", "unexpressed", None, source="sample", ref=str(u.get("ref") or ""),
             says_otherwise=bool(u.get("says_otherwise")))
    out.draft_versions[-1]["sample"] = {"claims": _dump(full.claims), "verdicts": _dump(verdicts)}


def _speech(ctx: TurnContext, record: AdjudicationRecord, turn: _Turn, s: _Sent, i: int,
            earlier: Sequence[str] = ()) -> None:  # rule: 12.3.1b
    """12.3.1b item 1's checks, all code: the speaker is present, is not the PC, no quoted words in the PC's mouth
    go beyond the player's message (`pc_agency`, a cut), and `not_a_repeat` (12.14.11; DL-12-90): words that repeat
    one of the speaker's own `said` records, or their earlier line in this draft, are redrafted. Speech is never
    checked for truth."""
    from engine.audit import text as atx
    from engine.world.scenes import cast_present

    _, speech = voices(s.decl)
    if not speech:
        return
    sp = s.decl.speaker
    pc_words = speech if sp is not None and sp == record.pc else pc_quotes(s.decl)
    speech = [q for q in speech if q not in pc_words] or speech  # the NPC's own words (DL-12-100)
    for q in pc_words:  # the player's words, or those a pause carried into this turn (spec 017)
        if not (turn.heard and atx.covers(q, turn.heard, ratio=0.8)):
            s.failures.append(Failure(why="puts words in the PC's mouth the player did not say (12.14.3)", fix="cut"))
            break
    if sp is not None and sp != record.pc and sp not in cast_present(ctx.need_tx().state):
        s.failures.append(Failure(why="the speaker is not here", fix="redraft",
                                  store_value="give the words to someone present"))
    elif sp is None and not pc_words:
        _log(ctx, turn, i, "speech", "no_speaker")
    if sp is not None and sp != record.pc:
        from engine.dm.testimony import is_repeat, overlap

        said = " ".join(speech)
        limit = float(((ctx.rules.pacing.get("narration") or {}).get("freshness") or {}).get("said_overlap") or 0.6)
        again = is_repeat(ctx.need_tx().state, ctx.rules, sp, said) or next(
            (e for e in earlier if overlap(said, e) > limit), None)
        if again:
            s.failures.append(Failure(why="repeats a line this speaker already said (not_a_repeat, 12.14.11)",
                                      fix="redraft",
                                      store_value=f'{narrator_role.name_of(ctx.need_tx().state, sp, record.pc)} '
                                                  f'already said "{again[:120]}": new words, or drop the line'))


def _precision(ctx: TurnContext, record: AdjudicationRecord, turn: _Turn, sents: list[_Sent], i: int,
               idx: SceneIndex) -> None:  # rule: 12.3.2
    # rule: OEQ-12-27
    """12.3.2's precision checks on sentence `i` (the pronoun of a certain subject, season words against the calendar
    line, plain result words against the turn's beat): every hit is logged with whether it blocked, so each check's
    precision can be measured (OEQ-12-27); a blocking hit goes to the revision."""
    from engine.audit.claims import calendar_season, precision_checks

    s = sents[i]
    narration, speech = voices(s.decl)
    before = [voices(sents[j].decl)[0] for j in range(i) if not sents[j].dropped]
    for h in precision_checks(narration, idx=idx, before=before, speech=speech, about=s.decl.about,
                              season=calendar_season(ctx.need_tx().state), rules=ctx.rules,
                              beat=passage_beat(record.beats), pause=record.pause, speaker=s.decl.speaker):
        _log(ctx, turn, i, h.cls, "contradicted" if h.blocks else "logged", h.store_value, check=h.check,
             voice=h.voice, words=h.words, subject=h.subject, blocks=h.blocks, source="precision")
        _count(turn, f"precision.{h.check}")
        if h.blocks:
            s.failures.append(Failure(why=h.why, fix="redraft", store_value=h.store_value))


def _judge(ctx: TurnContext, record: AdjudicationRecord, turn: _Turn, d: _Draft, out: NarrationResult,
           version: dict[str, Any], unplaced: Sequence[NewElement] = ()) -> None:  # rule: PR-12-2
    # rule: 12.3.1a
    # rule: 12.3.1b
    """PR-12-2 over the whole passage, by code only (no per-turn audit, DL-12-83): coverage and the quote-mark check
    (12.3.1a); per sentence of code's split, the code scans on the narrator's voice (names, numerals, sealed strings,
    mechanics; 12.3.1a), the precision checks, the speech checks, new elements by tier (T8), safety. Only
    blocking-list hits fail a sentence; the rest is logged (12.3.1b)."""
    tx = ctx.need_tx()
    rules = ctx.rules
    idx = SceneIndex.of(tx.state, turn.items, said=turn.heard)
    names = _names(ctx, list(tx.state.entities))
    must = [it.handle for it in turn.items if it.must_name]
    d.missing = coverage(d.passage, must)
    d.unquoted = unquoted(d.passage)
    for el in unplaced:  # a side-list element the passage never names: nothing to write or cut
        _log(ctx, turn, -1, "new_element", "not_in_passage", None, element=el.name)
    for i, s in enumerate(d.sents):
        s.failures = []
        if s.decl.speaker is not None and s.decl.speaker not in tx.state.entities:
            s.decl.speaker = None
        scan = scan_sentence(s.decl, idx, rules=rules, names=names)
        s.decl.about += scan.added_about
        _count(turn, "undeclared_new", scan.undeclared_new)
        s.failures += scan.failures
        for cls, why in scan.logged:
            _log(ctx, turn, i, cls, "logged", why)
        _precision(ctx, record, turn, d.sents, i, idx)
        earlier = [" ".join(voices(d.sents[j].decl)[1]) for j in range(i)
                   if d.sents[j].decl.speaker == s.decl.speaker]
        _speech(ctx, record, turn, s, i, earlier)
        _write_new(ctx, record, s, idx, out, turn, i)
        safe = screen_safety(s.decl.text, tx.state)
        if not safe.ok and safe.cuts:
            s.failures.append(Failure(why="crosses a line the player set (12.5.6)", fix="cut"))
        echoed = echoed_quotes(s.decl.text, [p.text for p in record.parts])
        if echoed and i > 0:
            _log(ctx, turn, i, "speech", "echoes the player's words", echoed[0])
    version["checks"] = {str(g): [f.model_dump() for f in s.failures] for g, s in enumerate(d.sents) if s.failures}
    version["missing"] = list(d.missing)
    version["unquoted"] = list(d.unquoted)


def _dump(items: Sequence[BaseModel]) -> list[dict[str, Any]]:
    return [x.model_dump(mode="json", by_alias=True) for x in items]


def _names(ctx: TurnContext, ids: Sequence[str]) -> list[str]:
    st = ctx.state
    return [st.entities[i].name for i in ids if i in st.entities]


def _text(sents: Sequence[_Sent], source: str = "") -> str:  # rule: 12.3.3
    """P1: the passage as written. Each kept sentence stands where it stood in `source` (the model's passage), with
    the whitespace before it, so paragraphs survive (round 7: 21 of 43 drafts had paragraph breaks, 0 of 43
    deliveries); code's edits to a sentence (quoting) are applied in place; a cut sentence goes with the space before
    it, and a paragraph break it opened passes to the next kept sentence; a line code adds (a rendered must-name
    item, which has no place in the passage) joins with a space. The split is only an index into the passage."""
    out: list[str] = []
    at, carry = 0, ""
    for s in sents:
        i = source.find(s.orig, at) if s.orig and source else -1
        gap = (source[at:i] or " ") if i >= 0 else " "
        if i >= 0:
            at = i + len(s.orig)
        if s.dropped or not s.decl.text:
            carry = carry or (gap if "\n" in gap else "")
            continue
        if carry and "\n" not in gap:
            gap = carry
        carry = ""
        out.append((gap if out else "") + s.decl.text)
    return "".join(out).strip()


def _draft(ctx: TurnContext, record: AdjudicationRecord, turn: _Turn, passage: Passage, out: NarrationResult,
           kind: str) -> _Draft:  # rule: PR-12-2
    """One passage parsed into code's sentences, judged, and recorded as a draft version."""
    sents, unplaced = sentences_of(passage)
    d = _Draft(passage=passage, sents=[_Sent(decl=x, orig=x.text) for x in sents])
    version: dict[str, Any] = {"kind": kind, "text": passage.text, "side_list": passage.model_dump(exclude={"text"}),
                               "mentions": [], "claims": [], "verdicts": []}
    out.draft_versions.append(version)
    _judge(ctx, record, turn, d, out, version, unplaced)
    return d


def narrate_checked(ctx: TurnContext, record: AdjudicationRecord, *, player_message: str = "",
                    purpose: Purpose = "turn", exchanges: Sequence[str | tuple[str, str]] = (),
                    pause_blocks: Sequence[OofBlock] = (), extra: Sequence[str] = (),
                    fallback_text: str | None = None) -> NarrationResult:  # rule: PR-12-1
    # rule: PR-12-2
    # rule: 12.3.3
    """T7 draft (one passage and its side list) → judge the whole passage (scans, tiers, coverage, quote marks) →
    at most `max_revisions` revision calls that see the whole draft and what failed → cut what still fails, quote
    what is still unquoted, state each uncovered must-name item by its rendered line → the plain fallback when nothing
    survives → T10 screen. Needs the turn's open transaction (`ctx.tx`). `fallback_text` replaces the record-built
    fallback (a recap falls back to its RECAP block: empty fiction)."""
    from engine.dm.npc_layer import ensure_activities

    rules = ctx.rules
    out = NarrationResult()
    if purpose in ("turn", "scene_open", "opening"):
        ensure_activities(ctx, record)  # 12.11.9 step 1: once per scene; optional material, never a record line
    turn = _Turn(items=narrator_role.record_items(ctx.need_tx().state, record), player_message=player_message,
                 heard=" ".join([player_message, *(p.text for p in record.parts)]), exchanges=list(exchanges))
    kw: dict[str, Any] = {"player_message": player_message, "exchanges": exchanges, "purpose": purpose,
                          "extra": extra, "items": turn.items}
    try:
        d = _draft(ctx, record, turn, narrator_role.draft(ctx, record, **kw).passage, out, "draft")
    except ModelInvalid as exc:
        return _fallback(ctx, record, out, [], [f"{exc.__class__.__name__}: {exc}"], fallback_text)
    revisions = 0
    while revisions < _max_revisions(rules) and (failed := d.failed()):
        revisions += 1
        try:
            nd = narrator_role.draft(ctx, record, revision=Revision(draft=d.passage.text, failed=failed), **kw)
            if not nd.passage.text:
                break  # an empty revision: the draft stands, and what still fails is cut below
            d = _draft(ctx, record, turn, nd.passage, out, "revision")
        except ModelInvalid:
            break
    return _deliver(ctx, record, turn, d, out, pause_blocks, fallback_text, revisions)


_CLOSE = "\"”’' "


def _deliver(ctx: TurnContext, record: AdjudicationRecord, turn: _Turn, d: _Draft, out: NarrationResult,
             pause_blocks: Sequence[OofBlock], fallback_text: str | None, revisions: int) -> NarrationResult:
    # rule: 12.3.3
    # rule: 12.3.1a
    """After the revision: cut each sentence that still fails; quote what still stands outside quote marks (12.3.1a
    item 2); state each must-name item the side list still leaves out by its rendered line, before the closing
    question; restore the open prompt only if a cut removed it; the plain fallback when nothing drafted survives."""
    tx = ctx.need_tx()
    sents = d.sents
    reasons = [f"[{i}] {f.why}" for i, s in enumerate(sents) for f in s.failures]
    cut_any = any(not s.ok for s in sents)
    for s in sents:
        s.dropped = s.dropped or not s.ok
    kept = [s for s in sents if not s.dropped]
    if not [s for s in kept if s.decl.speaker or not s.decl.text.rstrip(_CLOSE).endswith("?")]:
        return _fallback(ctx, record, out, [], reasons or ["no drafted sentence passed"], fallback_text)
    quoted = []
    for w in d.unquoted:  # 12.3.1a item 2: code quotes the exact words the revision left outside quote marks
        for s in kept:
            q = quote(s.decl.text, w)
            if q != s.decl.text:
                s.decl.text = q
                quoted.append(w)
                break
    by_handle = {it.handle: it for it in turn.items}
    rendered = [h for h in d.missing if by_handle[h].render]
    lines = [_Sent(decl=Sentence(text=by_handle[h].render, refs=[h])) for h in rendered]
    at = len(kept) - (1 if kept[-1].decl.text.rstrip(_CLOSE).endswith("?") else 0)
    final = [*kept[:at], *lines, *kept[at:]]
    # every sentence, cut ones too, in passage order, the rendered lines before the closing question: the cuts close
    # their gaps and the paragraphs stay (P1). No usage marks are set (12.14.11; PR-12-1 T12).
    close = kept[at] if at < len(kept) else None
    ordered = [x for s in sents for x in ([*lines, s] if s is close else [s])] + (lines if close is None else [])
    text = _text(ordered, d.passage.text)
    had_prompt = sents[-1].decl.text.rstrip(_CLOSE).endswith("?")
    if had_prompt and record.pause is None and not text.rstrip(_CLOSE).endswith("?"):
        text += " What do you do?"  # 12.3.3: the open prompt (12.14.9), restored by code because a cut removed it
    if cut_any or rendered or quoted:
        out.draft_versions.append({"kind": "render" if rendered else "cut", "text": text, "mentions": [],
                                   "claims": [], "verdicts": [], "rendered": rendered, "quoted": quoted,
                                   "reasons": reasons})
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
    _said(ctx, record, d.passage, kept, text, out)
    _sample(ctx, record, turn, final, d.passage, out)  # after delivery: it only logs (DL-12-83)
    out.claim_log = turn.log
    out.draft_versions[-1]["stats"] = dict(turn.stats, revisions=revisions)
    return out


def _said(ctx: TurnContext, record: AdjudicationRecord, passage: Passage, kept: Sequence[_Sent], text: str,
          out: NarrationResult) -> None:  # rule: 12.3.1b
    """Delivered speech as `said` records `{speaker, turn, words, about, question}`, never facts (12.3.1b item 1;
    PR-12-10 step 5): one record per speech of the side list, whole (its words as the narrator gave them), when it
    was delivered; kept in state (`engine.dm.testimony`), fed back on the speaker's card, filed under the index key
    of the question they answered this turn. A stored name the PC did not know, heard in an NPC's words, is known
    from now on (`how: heard`)."""
    from engine.audit import text as atx
    from engine.dm.testimony import add_said
    from engine.store.views import name_known
    from engine.world.social import learn_name

    st = ctx.need_tx().state
    asked = {a.npc: t.removeprefix("ask:") for a in record.npc_actions for t in a.tags if t.startswith("ask:")}
    player = " ".join(p.text for p in record.parts)
    start = len(out.said)
    for sp in passage.speech:
        if not sp.speaker or sp.speaker == record.pc or sp.speaker not in st.entities:
            continue
        if not atx.covers(sp.words, text, ratio=0.8) or (player and atx.covers(sp.words, player, ratio=0.8)):
            continue  # cut, never in the passage, or the player's own words quoted back: not testimony
        about = [a for s in kept if s.decl.speaker == sp.speaker for a in s.decl.about]
        out.said.append({"speaker": sp.speaker, "turn": ctx.turn_id, "words": sp.words,
                         "about": list(dict.fromkeys([sp.speaker, *about])), "question": asked.get(sp.speaker)})
        low = sp.words.lower()
        for eid, e in list(st.entities.items()):
            if record.pc and e.kind in ("npc", "companion", "adversary") and e.name and not name_known(st, eid) \
                    and re.search(rf"\b{re.escape(e.name.lower())}\b", low):
                learn_name(ctx.time_ctx(), record.pc, eid, "heard")
    add_said(ctx, out.said[start:])


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
    from engine.resolve.types import Beat, Frame, RollResult

    d = pause.detail or {}
    stage = d.get("stage")
    rules = ctx.rules
    last = {i["kind"]: i["text"] for i in items}
    try:
        if stage == "offer":  # "Then:" from each queued goal, never the Reader's `method` (DL-01-39, as `_then`)
            then = [oof.goal_line(Beat.model_validate(q["beat"]), ctx.state) for q in d.get("queued") or ()]
            return [oof.offer_block(Frame.model_validate(d["frame"]), rules=rules, fate=_pc_fate(ctx), state=ctx.state,
                                    then=then)]
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
                                       purpose="scene_open" if rec.scene.started else "turn",  # 12.4.3; P-098
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
