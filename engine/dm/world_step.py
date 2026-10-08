"""T5 WORLD of PR-12-1 (12.2.9): the world responds in a fixed order, each only from its closed source (01.11.3).

    world_step(ctx, record, beats=outcomes)      # fills record.npc_actions / omens / triggers / notes

1. Adversaries in conflict — Milestone 1 has no round-by-round conflict (coarse).
2. NPCs present: a resolved Talk frame's outcome, else a recorded want or refusal the World role names, else
   `tbl.npc_action` rolled with the NPC's standing as the modifier (a first meeting rolls the reaction first).
3. Clocks that ticked this turn render their omens (INV-14).
4. Fired triggers in 12.2.3's order (owed blocks for the narration; a due lethal warning is delivered).
5. Time: each resolved beat's cost by the scene's mode (00.7.3) through `advance_time` (boundaries run).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from engine.audit import text as words
from engine.audit.fallback import fact_sentence
from engine.dm.adjudication import AdjudicationRecord, NpcActionEntry, OmenEntry
from engine.dm.context import TurnContext
from engine.dm.roles.world import npc_motives, npc_responses, present_npcs
from engine.resolve.pipeline import BeatOutcome
from engine.resolve.tables import roll_table
from engine.resolve.types import REACH_VALUE
from engine.retrieve.scene import READING, WRITTEN, cannot_read
from engine.retrieve.triggers import get_active_triggers
from engine.time.clock import beat_cost
from engine.time.scheduler import advance_time
from engine.store.views import name_known
from engine.world.social import first_interaction, learn_name, record_knowledge, standing

NPC_TABLE = "tbl.npc_action"
RESOLVED = ("resolved", "no_roll")


def happened_text(record: AdjudicationRecord) -> str:
    """THIS MESSAGE for the World role: what just happened this turn, in words."""
    lines = [f"player: {p.text} ({p.cls})" for p in record.parts]
    for b in record.beats:
        res = b.degree or b.gate_words or "no roll"
        lines.append(f"beat: {b.restatement} -> {res}" + (f"; target {', '.join(b.targets)}" if b.targets else ""))
    return "\n".join(lines)


def world_step(ctx: TurnContext, record: AdjudicationRecord, *, beats: Sequence[BeatOutcome],
               oof: list[dict[str, str]] | None = None) -> None:
    # rule: 12.2.9
    # coarse: PR-06-6
    deliver_learning(ctx, record, beats)
    acted = foes_act(ctx, record, oof)
    npcs_respond(ctx, record, beats, skip=acted, oof=oof)
    learn_names(ctx, record, beats)
    clock_omens(ctx, record)
    fired_triggers(ctx, record)
    beat_time(ctx, record, beats, fought=bool(acted))


def _foe_turn(ctx: TurnContext, record: AdjudicationRecord, foe: str, oof: list[dict[str, str]] | None) -> None:
    # rule: 06.9.2
    """One foe's beat (engine/resolve/conflict.py), its act for the narration and its RESULT line for the player."""
    from engine.dm.oof import changed_line
    from engine.resolve.conflict import foe_beat

    tx = ctx.need_tx()
    start = len(tx.events)
    said, res = foe_beat(ctx.time_ctx(), ctx.rng, foe, record.pc or "")
    record.npc_actions.append(NpcActionEntry(npc=foe, action=said, source="behavior", source_ref="beh.default_melee"))
    if res is not None and oof is not None:
        changed = changed_line(ctx.state, record.pc or "", tx.events[start:])
        oof.append({"kind": "RESULT", "text": f"[RESULT] {_name(ctx.state, foe)} strikes · hit"
                                              + (f" · {changed}" if changed else "")})
    if res is not None and res.threshold and oof is not None:  # rule: PR-07-5
        from engine.dm.turn import _env, _harm_followups

        env = _env(ctx)
        env.threshold_due.append(record.pc or "")
        _harm_followups(ctx, env, record, oof)


def foes_act(ctx: TurnContext, record: AdjudicationRecord, oof: list[dict[str, str]] | None = None) -> list[str]:
    # rule: 06.9.2
    """Step 1: in conflict mode each foe still able answers by its behavior row (06.9.4), then the end test
    (06.13.1). Returns the foes that acted (they draw no social table row this turn)."""
    from engine.resolve.conflict import able, check_end, record as conflict

    rec = conflict(ctx.state)
    if not rec or not record.pc or ctx.state.open_pause() is not None:
        return []
    acted = []
    for foe in rec.get("foes", []):
        if able(ctx.state, foe) and conflict(ctx.state):
            _foe_turn(ctx, record, foe, oof)
            acted.append(foe)
    check_end(ctx.time_ctx(), record.pc)
    return acted


def npcs_respond(ctx: TurnContext, record: AdjudicationRecord, beats: Sequence[BeatOutcome], *,
                 skip: Sequence[str] = (), oof: list[dict[str, str]] | None = None) -> None:
    # rule: 12.2.9
    """Step 2: only when something happened that an NPC present could respond to (a beat or speech)."""
    if not beats and not any(p.cls in ("SPEECH", "DECLARATION") for p in record.parts):
        return
    tx = ctx.need_tx()
    present = present_npcs(ctx.state)
    # a Talk framed with no target speaks to the one NPC here, if there is only one (P-056)
    talk = {(b.entry.targets or present)[0]: b for b in beats
            if b.status in RESOLVED and (b.entry.targets or len(present) == 1)
            and "talk" in (b.entry.approach_words or "")}
    # 12.11.5: a row never resolves what a frame should; a beat on this NPC that did not resolve (refused, withdrawn,
    # paused) happened to no one, so it draws no table row either
    unresolved = {t for b in beats if b.status not in RESOLVED for t in b.entry.targets}

    def talked(npc: str, tags: list[str]) -> None:
        b = talk.pop(npc)
        record.npc_actions.append(NpcActionEntry(npc=npc, action=f"responds as the talk went: "
                                                 f"{b.entry.degree or 'success'}",
                                                 source="talk_outcome", source_ref=b.frame_id, tags=tags))

    for r in npc_responses(ctx, happened_text(record)):
        motives = npc_motives(ctx.state, r.npc)
        if r.npc in talk:  # (a) a resolved Talk frame's delivered outcome (a certain talk, no roll, is a yes)
            talked(r.npc, r.tags)
        elif r.refusal_engaged:  # (b) a recorded refusal outranks everything unresolved
            record.npc_actions.append(NpcActionEntry(npc=r.npc, action=f"refuses: {motives.get(r.refusal_engaged)}",
                                                     source="refusal", source_ref=r.refusal_engaged, tags=r.tags))
        elif r.want_engaged:
            record.npc_actions.append(NpcActionEntry(npc=r.npc, action=f"acts on a want: {motives.get(r.want_engaged)}",
                                                     source="want", source_ref=r.want_engaged, tags=r.tags))
        elif r.npc in unresolved or r.npc in skip:  # a foe in the fight acted by its behavior row (06.9.2)
            continue
        else:  # (c) the action table, with standing as context (12.11.5)
            tctx = ctx.time_ctx()
            st_value = standing(ctx.state, r.npc)
            if st_value is None:  # PR-12-5 step 3: the first interaction's reaction roll
                st_value = first_interaction(tctx, r.npc)
            res = roll_table(NPC_TABLE, {"standing_modifier": int(st_value), "tags": r.tags}, rules=ctx.rules,
                             state=ctx.state, rng=ctx.rng, purpose=f"npc action {r.npc} (12.11.5)")
            tx.add_all(res.events)
            if "attacks" in str(res.entry) and int(st_value) <= -3 and record.pc:  # rule: 06.2.1
                # a hostile NPC's row says "attacks": the fight starts and it strikes now
                from engine.resolve.conflict import start

                start(tctx, record.pc, [r.npc], "a hostile NPC attacks (06.2.1)")
                _foe_turn(ctx, record, r.npc, oof)
                continue
            record.npc_actions.append(NpcActionEntry(npc=r.npc, action=str(res.entry), source="table_row",
                                                     source_ref=f"{NPC_TABLE}:{res.roll}", tags=r.tags))
    # the one spoken to answers as the talk went, always; a Talk aimed at a thing ("coming up the road") has no
    # one to answer it (P-096)
    for npc in [n for n in talk if n in ctx.state.entities
                and ctx.state.entities[n].kind in ("npc", "adversary", "companion")]:
        talked(npc, [])


# the NPC's *own* name or identity only: "the thief's name" / "the name of the thief" asks about someone else, and
# answering it with the speaker's name made the officer the thief [P-113]; a third party's name goes through
# `settle_who` (a `who_is_*` fact) on the claim path instead
_OBJ = r"(?:him|her|them|the [\w' -]{1,40}?)"
_ASKS_NAME = re.compile(r"\byour (?:own )?name\b|\bwho (?:are|were) you\b|\bwho you are\b|\bintroduc"
                        rf"|\b(?:ask|asks|asking) {_OBJ} (?:for )?(?:his|her|their) (?:own )?name\b"
                        rf"|\b(?:ask|asks|asking) {_OBJ} who (?:he|she|they) (?:is|are)\b", re.IGNORECASE)


def learn_names(ctx: TurnContext, record: AdjudicationRecord, beats: Sequence[BeatOutcome]) -> None:
    # rule: 12.10.2
    """The PC asked who someone is (or gave their own name) and that NPC answers (a resolved Talk on them,
    else the one NPC whose response this turn is not a withholding one): they give their name, recorded for
    the PC (`learn_name`) and named in their act so the narration says it."""
    from engine.dm.roles.narrator import WITHHOLDING

    st = ctx.state
    if record.pc is None or not _ASKS_NAME.search(" ".join([p.text for p in record.parts]
                                                           + [b.entry.restatement for b in beats])):
        return
    answering = [a for a in record.npc_actions if a.npc in st.entities
                 and not a.action.startswith(WITHHOLDING) and not name_known(st, a.npc)]
    talked = {t for b in beats if "talk" in (b.entry.approach_words or "") for t in b.entry.targets}
    for a in [a for a in answering if a.npc in talked] or (answering if len(answering) == 1 else []):
        learn_name(ctx.time_ctx(), record.pc, a.npc, "told")
        a.action += f"; gives their name, in their own words: {st.entities[a.npc].name}"


LEARN_VERBS = {"verb.talk": "told", "verb.observe": "witnessed", "verb.recall": "recalled"}


def _fact_words(state: Any, f: Any) -> str:
    """A fact's words for relevance ranking only (what the player sees is `fact_sentence`)."""
    from engine.dm.roles.narrator import name_of

    who = name_of(state, f.subject) if f.subject in state.entities else ""
    value = {True: "yes", False: "no"}.get(f.value, f.value) if isinstance(f.value, bool) else f.value
    head = f"{who} — " if who else ""
    return f"{head}{f.predicate.replace('_', ' ')}: {value}"


def _learnable(state: Any, f: Any, pc: str) -> bool:
    return (isinstance(f.value, str | bool | int | float) and f.visibility != "sealed" and f.id not in state.seals
            and f.subject not in state.seals and f.subject != pc and f.id not in state.knowledge.get(pc, {})
            and f.predicate != "name" and not f.predicate.endswith((".but", ".and")))


def deliver_learning(ctx: TurnContext, record: AdjudicationRecord, beats: Sequence[BeatOutcome]) -> None:
    # rule: 12.10.5
    """A successful Talk, Observe or Recall delivers what the store holds on what was asked, ranked by the words it
    shares with the beat, `deliver_count`'s many at the delivered reach (01.10.4); each is `record_knowledge`d for the
    PC and named in the record (BeatEntry.learned) for the narration. Talk draws on what the listener knows (their
    knowledge and their own facts, 15.6.2: they tell what they know); Observe and Recall on what is here.
    Nothing relevant in the store: nothing is delivered here, and what the narration then says the PC learns is
    settled by the Oracle at the claim check (12.3.2)."""
    # ponytail: relevance is shared content words; no per-NPC belief model of the scene's public facts
    st = ctx.state
    pc = record.pc
    if pc is None:
        return
    for b in beats:
        e = b.entry
        verb = next((v for v in LEARN_VERBS if v in (e.approach_words or "")), None)
        ok = b.status == "no_roll" or (b.status == "resolved" and (e.degree in ("success", "critical_success")
                                                                     or e.success_at_cost))
        if b.status == "resolved" and not ok:
            _stalled(st, record, e, b.frame_id)
        if verb is None or not ok:
            continue
        place = st.scene.place_id if st.scene else None
        here = {*(st.scene.cast_present if st.scene else ()), place, *e.targets, "world"} | {
            i for i, p in st.positions.items() if place and p.location == place}
        if verb == "verb.talk" and e.targets:
            pool = set(st.knowledge.get(e.targets[0], {})) | {f.id for f in st.facts.values()
                                                               if f.subject == e.targets[0]}
        else:
            pool = {f.id for f in st.facts.values() if f.subject in here}
        names = " ".join(st.entities[i].name for i in [e.actor, *e.targets] if i and i in st.entities)
        asked = words.content(e.restatement) - words.content(names)
        ranked = sorted(((len(asked & words.content(_fact_words(st, st.facts[fid]))), fid) for fid in pool
                         if fid in st.facts and _learnable(st, st.facts[fid], pc)
                         and fact_sentence(st, st.facts[fid])), reverse=True)  # only what can be told plainly
        ranked = [fid for score, fid in ranked if score][:5]  # resolution.yaml delivery_rules.max_items
        said = next((f for k in WRITTEN if e.targets and (f := st.current_fact_id(e.targets[0], k))), None)
        if said in pool and READING.search(e.restatement) and not cannot_read(st, pc, e.targets[0]):  # reading it delivers its words first (P-110)
            ranked = [said] + [f for f in ranked if f != said][:4]
        n = len(ranked)
        reach = REACH_VALUE.get(e.reach or "standard", 2)
        count = {1: max(1, n // 3), 2: -(-n // 2)}.get(reach, n)  # T-01-6; ponytail: no Exceptional bonus item
        for fid in ranked[:count]:
            record_knowledge(ctx.time_ctx(), pc, fid, LEARN_VERBS[verb])
            e.learned.append(fact_sentence(st, st.facts[fid]))
        if verb == "verb.talk" and e.targets and e.targets[0] in st.entities \
                and st.entities[e.targets[0]].kind in ("npc", "companion", "adversary"):
            _talk_answers(ctx, record, e, pc)
        if not ranked and verb != "verb.talk" and e.targets and e.targets[0] in st.entities:
            # P-086: a success that names nothing reads as a failure; what the narration names is settled by the
            # Oracle at the claim check and written (12.3.2, write-on-mention)
            record.notes.append(f"the look at {_name(st, e.targets[0])} succeeded: name at least one concrete thing "
                                "the PC now makes out about it (what it is, what it is made of, a telling detail), "
                                "plainly, never a vague glimpse")


# "who ..." asked of someone: at a sentence start or after an asking verb ("asking who is behind the coin", "says who
# told him"), never a relative clause ("the man who sold me the horse"); "the name of/behind X" asks "who is X"
_WHO_ASKED = re.compile(r"(?:^|[.?!:;\"“]\s*|\b(?i:ask|asks|asked|asking|say|says|saying|tell|tells|telling|learn|"
                        r"learns|know|knows|reveal|reveals|names?|whether)\s+(?:(?i:him|her|them|me|us|again|politely|"
                        r"plainly|directly)\s+|[A-Z][\w'-]+\s+){0,3}?)([Ww]ho\b(?:(?! and | or | so )[^?.!;,\"”])+)")
_WHAT_ASKED = re.compile(r"\bwhat (?:is|are|was|were|they are|it is|you saw|did you see)\b[^?.!;,\"”]*", re.I)
_NAME_OF = re.compile(r"\bname (?:of|behind) ([^?.!;,\"”]+)", re.I)


def _who_questions(text: str) -> list[str]:
    return [re.sub(r"^who(?:'s|’s)", "who is", m.group(1).strip(), flags=re.I).replace("Who", "who", 1)
            for m in _WHO_ASKED.finditer(text)] + [
        f"who is {m.group(1).strip()}" for m in _NAME_OF.finditer(text)]


def _talk_answers(ctx: TurnContext, record: AdjudicationRecord, e: Any, pc: str) -> None:
    # rule: 12.3.2
    """P-120: a successful Talk is "yes, as asked" (T-15-5), never a refusal. A "who is X?" the store cannot answer
    is settled among existing people (`settle_who`, I-148) and told by the one asked; a Talk that delivers nothing
    still gives what the NPC can from state (12.8.2's sources, no new clue: 12.14.13): an open thread any local may
    know, else who else might know (an existing person)."""
    from engine.dm.incident import _people, settle_who
    from engine.dm.oof import short_text
    from engine.dm.player_text import second_person
    from engine.dm.roles.world import present_npcs
    from engine.world.social import thread_list

    st = ctx.state
    speaker = e.targets[0]
    if not _ASKS_NAME.search(" ".join([e.restatement, *(p.text for p in record.parts)])):  # their own name: 12.10.2
        for q in [q for t in [e.restatement, *(p.text for p in record.parts)] for q in _who_questions(t)]:
            who = settle_who(ctx, q, asked=True, exclude=(speaker,))
            if who is None:
                continue
            name, fid = who
            if fid not in st.knowledge.get(pc, {}):
                record_knowledge(ctx.time_ctx(), pc, fid, "told")
            e.learned.insert(0, f"{_name(st, speaker)} tells you {q}: {name}")
            return
    if e.learned:
        return
    what = next((m.group(0).rstrip() for t in [*(p.text for p in record.parts), e.restatement]
                 for m in _WHAT_ASKED.finditer(t)), None)
    if what:  # like a look that finds nothing stored (P-086): they name it, settled at the claim check (12.3.2)
        record.notes.append(f"the talk with {_name(st, speaker)} succeeded: they answer {what.lower()} plainly, in "
                            "their own words, naming one concrete, ordinary thing it is (never a hint toward anything "
                            "hidden; if they cannot know, they say who or where might)")
        return
    threads = sorted((t for t in thread_list(st) if t["status"] == "active" and t["id"] not in st.seals
                      and st.entities[t["id"]].visibility in ("shown", "available")), key=lambda t: -t["weight"])
    if threads:
        lead = second_person(short_text(str(threads[0]["text"]), 160)).rstrip(".")
        e.learned.append(f"{_name(st, speaker)} gives what they can: {lead}")
        return
    here = set(present_npcs(st))
    # ponytail: the pointer is the first present (else first known) person, not who would really know; a "who
    # would know" table belongs to the rules (I-153)
    others = sorted((n for n in _people(st, pc) if n != speaker), key=lambda n: (n not in here, n))
    if others:
        e.learned.append(f"{_name(st, speaker)} gives what they can: {_name(st, others[0])} might know more")


STALLED = "cannot make out: "
_FAILED = ("failure", "critical_failure")


def _name(st: Any, eid: str) -> str:
    from engine.dm.roles.narrator import name_of

    n = name_of(st, eid)
    return f"the {n}" if n[:1].islower() and not n.startswith(("the ", "a ", "an ", "your ")) else n


def _looked(f: dict[str, Any]) -> bool:
    """A frame that tried to learn something: a hidden roll, or an Observe or Recall."""
    return bool(f.get("secret")) or (f.get("gate") or {}).get("verb") in ("verb.observe", "verb.recall")


def _stalled(st: Any, record: AdjudicationRecord, e: Any, frame_id: str | None) -> None:
    # rule: 12.14.8
    """P-086: the second failed attempt in this scene to make out the same target says so plainly and points to
    another way, instead of a third vague glimpse (failure is the world's answer, not a loop)."""
    fs = st.frames.get(frame_id) if frame_id else None
    if fs is None or not e.targets or e.targets[0] not in st.entities or not _looked(fs.frame):
        return
    target = e.targets[0]
    failed = [x for x in st.frames.values() if x.resolved and x.resolved.get("degree") in _FAILED
              and (x.frame.get("beat") or {}).get("target") == target and _looked(x.frame)]
    if len(failed) >= 2:
        # said plainly, in player-facing words (the plain fallback prints it as is)
        record.notes.append(f"{STALLED}You cannot make out {_name(st, target)} from here, not this way. Another "
                            "approach might: ask someone who knows, get it out into the open, or come back with "
                            "better means.")


def clock_omens(ctx: TurnContext, record: AdjudicationRecord) -> None:  # rule: 00.8.4
    """Step 3: every clock that ticked this turn, with the omen the tick selected (INV-14)."""
    st = ctx.state
    for ev in ctx.need_tx().events:
        if ev.type != "clock_ticked":
            continue
        p: Any = ev.payload
        clock = st.clocks.get(p.clock_id)
        omen = ""
        if clock is not None and p.omen_key:
            stage, _, idx = str(p.omen_key).partition(":")
            texts = clock.omens.get(stage) or []
            if idx.isdigit() and int(idx) < len(texts):
                omen = texts[int(idx)]
        record.omens.append(OmenEntry(clock_id=p.clock_id, stage=p.stage, omen=omen, completed=p.completed))


def fired_triggers(ctx: TurnContext, record: AdjudicationRecord) -> None:  # rule: 12.2.3
    """Step 4: the raised triggers, in handling order, for the narration's owed blocks; a lethal warning that a
    boundary raised (`h.07.lethal_scan`) and no beat delivered is delivered now (PR-07-4)."""
    from engine.harm.ctx import HarmCtx
    from engine.harm.lethal import LethalTrigger, active_triggers, record_warning, warning_block

    st = ctx.state
    for t in active_triggers(st):
        trig = LethalTrigger(pc=str(t.get("pc")), source=str(t.get("source")), cause=str(t.get("cause")),
                             detail=dict(t.get("detail") or {}))
        if trig.pc not in st.entities:
            continue
        name = st.entities[trig.source].name if trig.source in st.entities else trig.source
        fate = st.quantities.get(trig.pc, {}).get("fate")
        record.notes.append(warning_block(ctx.rules, trig, source_name=name, fate=fate.current if fate else 0,
                                          yield_text="give up on terms they will take",
                                          retreat_text="break away and run"))
        ctx.need_tx().add_all(record_warning(HarmCtx(state=st, mint=ctx.mint, rules=ctx.rules, rng=ctx.rng), trig,
                                             sign=f"{name} could kill you"))
        record.triggers.append("trg.lethal_warning")
    for t in get_active_triggers(ctx.state, ctx.rules):
        if t.id not in record.triggers:
            record.triggers.append(t.id)


def beat_time(ctx: TurnContext, record: AdjudicationRecord, beats: Sequence[BeatOutcome], *,
              fought: bool = False) -> None:
    # rule: 00.7.3
    """Step 5: each resolved beat costs its mode's time; boundaries crossed run their handlers (INV-15). In
    conflict mode a beat costs nothing and the turn (the PC, then each foe) is one round (06.2.3)."""
    from engine.resolve.pipeline import _mode

    st = ctx.state
    if _mode(st) == "conflict":
        if fought or any(b.status in RESOLVED for b in beats):
            # ponytail: one PC turn + the foes' answers = one round; no tempo order (06.2.2) yet
            advance_time(ctx.time_ctx(), 1, "round", "round end (06.2.3)")
        return
    mode = st.scene.mode if st.scene else str(st.time.mode)
    for b in beats:
        if b.status not in RESOLVED:
            continue
        amount, unit = beat_cost(mode, significant=True)
        if amount <= 0:
            continue
        res = advance_time(ctx.time_ctx(), amount, unit, f"beat {b.entry.beat_id}")
        if res.interrupt:  # 00.7.8: halt and frame a new moment
            record.notes.append(f"interrupted: {res.interrupt}")
            break
