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

from engine.dm.adjudication import AdjudicationRecord, NpcActionEntry, OmenEntry
from engine.dm.context import TurnContext
from engine.dm.roles.world import npc_motives, npc_responses
from engine.resolve.pipeline import BeatOutcome
from engine.resolve.tables import roll_table
from engine.retrieve.triggers import get_active_triggers
from engine.time.clock import beat_cost
from engine.time.scheduler import advance_time
from engine.world.social import first_interaction, standing

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
    talk = {b.entry.targets[0]: b for b in beats
            if b.status == "resolved" and b.entry.targets and "talk" in (b.entry.approach_words or "")}
    for r in npc_responses(ctx, happened_text(record)):
        motives = npc_motives(ctx.state, r.npc)
        if r.npc in talk:  # (a) a resolved Talk frame's delivered outcome
            b = talk[r.npc]
            record.npc_actions.append(NpcActionEntry(npc=r.npc, action=f"responds as the talk went: {b.entry.degree}",
                                                     source="talk_outcome", source_ref=b.frame_id, tags=r.tags))
        elif r.refusal_engaged:  # (b) a recorded refusal outranks everything unresolved
            record.npc_actions.append(NpcActionEntry(npc=r.npc, action=f"refuses: {motives.get(r.refusal_engaged)}",
                                                     source="refusal", source_ref=r.refusal_engaged, tags=r.tags))
        elif r.want_engaged:
            record.npc_actions.append(NpcActionEntry(npc=r.npc, action=f"acts on a want: {motives.get(r.want_engaged)}",
                                                     source="want", source_ref=r.want_engaged, tags=r.tags))
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
