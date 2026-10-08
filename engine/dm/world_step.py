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
from engine.retrieve.triggers import get_active_triggers
from engine.time.clock import beat_cost
from engine.time.scheduler import advance_time
from engine.world.social import first_interaction, record_knowledge, standing

NPC_TABLE = "tbl.npc_action"
RESOLVED = ("resolved", "no_roll")


def happened_text(record: AdjudicationRecord) -> str:
    """THIS MESSAGE for the World role: what just happened this turn, in words."""
    lines = [f"player: {p.text} ({p.cls})" for p in record.parts]
    for b in record.beats:
        res = b.degree or b.gate_words or "no roll"
        lines.append(f"beat: {b.restatement} -> {res}" + (f"; target {', '.join(b.targets)}" if b.targets else ""))
    return "\n".join(lines)


def world_step(ctx: TurnContext, record: AdjudicationRecord, *, beats: Sequence[BeatOutcome]) -> None:
    # rule: 12.2.9
    # coarse: PR-06-6
    deliver_learning(ctx, record, beats)
    npcs_respond(ctx, record, beats)
    clock_omens(ctx, record)
    fired_triggers(ctx, record)
    beat_time(ctx, record, beats)


def npcs_respond(ctx: TurnContext, record: AdjudicationRecord, beats: Sequence[BeatOutcome]) -> None:
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
        elif r.npc in unresolved:
            continue
        else:  # (c) the action table, with standing as context (12.11.5)
            tctx = ctx.time_ctx()
            st_value = standing(ctx.state, r.npc)
            if st_value is None:  # PR-12-5 step 3: the first interaction's reaction roll
                st_value = first_interaction(tctx, r.npc)
            res = roll_table(NPC_TABLE, {"standing_modifier": int(st_value), "tags": r.tags}, rules=ctx.rules,
                             state=ctx.state, rng=ctx.rng, purpose=f"npc action {r.npc} (12.11.5)")
            tx.add_all(res.events)
            record.npc_actions.append(NpcActionEntry(npc=r.npc, action=str(res.entry), source="table_row",
                                                     source_ref=f"{NPC_TABLE}:{res.roll}", tags=r.tags))
    for npc in [n for n in talk if n in ctx.state.entities]:  # the one spoken to answers as the talk went, always
        talked(npc, [])


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
        n = len(ranked)
        reach = REACH_VALUE.get(e.reach or "standard", 2)
        count = {1: max(1, n // 3), 2: -(-n // 2)}.get(reach, n)  # T-01-6; ponytail: no Exceptional bonus item
        for fid in ranked[:count]:
            record_knowledge(ctx.time_ctx(), pc, fid, LEARN_VERBS[verb])
            e.learned.append(fact_sentence(st, st.facts[fid]))


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


def beat_time(ctx: TurnContext, record: AdjudicationRecord, beats: Sequence[BeatOutcome]) -> None:
    # rule: 00.7.3
    """Step 5: each resolved beat costs its mode's time; boundaries crossed run their handlers (INV-15)."""
    st = ctx.state
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
