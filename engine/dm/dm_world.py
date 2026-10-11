"""Spec 032 P4 (lane W): the world step of a dm-tools exchange. Code runs what the spine owns and hands the DM the
outcomes as plain words; it gives no orders and calls no model.

    facts = world_step(ctx, t)    # t: the dm_tools Turn (rec, oof, beats, stats); [] when a pause is open

In the pipeline's order (engine/dm/world_step.py, reused, not rebuilt): the foes answer (`foes_act`: the conflict's
own foe turn, harm by code), the exchange costs its mode's time (`beat_time`, or one `beat_cost` for an exchange with
no beat), the beat counter and dead air move, clocks that ticked give their omens, raised triggers give their warnings,
a raised lead injection is told (LEAD DUE; code writes none, spec 033 P5), and a shortfall of clue sources is told
once per node (WITNESS NEEDED). Scene ends are the DM's call (the `end_scene` tool): nothing
here cuts a scene. [owner ruling 2026-10-10]
"""

from __future__ import annotations

from typing import Any

from engine.dm import world_step as ws
from engine.dm.answer import name as _name
from engine.dm.context import TurnContext
from engine.time import clock
from engine.time.clock import beat_cost
from engine.time.scheduler import advance_time, mark_boundary, set_mode
from engine.world.common import meta, trigger_raised
from engine.world.pacing import clock_trace, lead_due
from engine.world.scenes import note_turn, turn_is_quiet

IDLE = ("refused", "question", "withdrawn")  # 01.3.6: a beat that spends nothing, so no foe answers it and no time passes
LEAD = "trg.lead_injection"
JUMPS = ("breather", "rest_short", "rest_long", "day", "week")  # a time jump opens a new scene (12.4.2 (3))


def world_step(ctx: TurnContext, t: Any) -> list[str]:
    """One exchange's world, once. Returns what the DM must be told (foe blows, omens, warnings, an interruption, a
    lead), as plain sentences; time passing alone is not a fact (the situation's `Now:` line shows it)."""
    rec, oof, st = t.rec, t.oof, ctx.state
    if not rec.pc or st.open_pause() is not None:
        return []
    tctx = ctx.time_ctx()
    n_act, n_oof, n_om, n_notes = len(rec.npc_actions), len(oof), len(rec.omens), len(rec.notes)
    spent = not t.beats or any(b.status not in IDLE for b in t.beats)
    if not t.beats:  # a plain exchange marks its own beat end (a rolled beat already did): the streak counts it once
        mark_boundary(tctx, "beat_end", {"exchange": t.rec.turn_id})
    acted = ws.foes_act(ctx, rec, oof) if spent else []
    ws.release_holds(ctx, rec)  # 06.5.2
    _time(ctx, t, spent, acted)  # before the omens: the interval it crosses is what ticks a clock
    ws.clock_omens(ctx, rec)
    ws.fired_triggers(ctx, rec)
    note_turn(tctx, quiet=turn_is_quiet(["DECLARATION" if t.beats else "SPEECH"], ctx.need_tx().events))
    facts = _foe_facts(ctx, rec, n_act, oof[n_oof:])
    t.stats["world"]["foe_turns"] += [{"foe": a.npc, "did": a.action} for a in rec.npc_actions[n_act:]]
    facts += [f"An omen: {o.omen}" + (" (it has come to a head)" if o.completed else "")
              for o in rec.omens[n_om:] if o.omen]
    if trigger_raised(ctx.state, LEAD):  # raised at beat_end by the inconclusive streak (12.8.1)
        facts += _lead(ctx, rec)
    facts += _witness(ctx)
    facts += [n.strip() for n in rec.notes[n_notes:]]
    t.stats["world"]["facts"] += facts
    return facts


def ensure_site(ctx: TurnContext) -> None:
    """Assumption A1 (traced, implementation-results-P4.md): the opening scene's time mode is the store's `free`, whose
    beat cost is 0, so the clock would never move. A dm-tools place scene runs in `site` (an exchange = 1 interval,
    00.7.3). Travel, rest and a fight set their own modes and put `site` back (a fight's `previous` is read here)."""
    if clock.mode_of(ctx.state.time.mode) == "free" and ctx.state.scene is not None:
        set_mode(ctx.time_ctx(), "site", "a dm-tools place scene")


def _time(ctx: TurnContext, t: Any, spent: bool, acted: list[str]) -> None:
    """Conflict: a round (06.2.3). Else each resolved beat costs the mode's time, a plain exchange costs one."""
    mode = clock.mode_of(ctx.state.time.mode)
    if mode == "conflict":
        ws.beat_time(ctx, t.rec, t.beats, fought=bool(acted))
    elif spent:
        amount, unit = beat_cost(mode, significant=True)
        if amount > 0:
            n = max(1, sum(b.status in ws.RESOLVED for b in t.beats))
            res = advance_time(ctx.time_ctx(), amount * n, unit, "an exchange (dm-tools)")
            if res.interrupt:  # 00.7.8: the DM is told; it decides whether the scene ends
                t.rec.notes.append(f"interrupted: {res.interrupt}")


def _foe_facts(ctx: TurnContext, rec: Any, n_act: int, results: list[dict[str, str]]) -> list[str]:
    """Each foe's act in words, then what its blow changed (the RESULT line's numbers, which the player sees too)."""
    out = [f"{_up(_name(ctx.state, a.npc))} {a.action}." for a in rec.npc_actions[n_act:]]
    for r in results:
        if r.get("kind") == "RESULT":
            parts = r["text"].removeprefix("[RESULT] ").split(" · ")
            if len(parts) > 2:
                out.append("What that changed: " + " · ".join(parts[2:]))
    return out


def _up(s: str) -> str:
    return s[:1].upper() + s[1:]


def _lead(ctx: TurnContext, rec: Any) -> list[str]:
    """12.8.2 / PR-12-3 on the dm-tools path: the DM is told one lead (thread, source id, form) and the counter resets.
    Code writes no fact, person or document; the DM brings it in with its tools or lets it go. With no thread or source
    on record it is told so. A pending roll holds it (the world step does not run under an open pause)."""
    try:
        out = lead_due(ctx.time_ctx())
    except Exception as exc:  # noqa: BLE001 - no PC or no rng: logged, the counter stays for next time
        rec.notes.append(f"lead injection held: {exc}")
        return []
    st = ctx.state
    if out.source_id is None and out.thread is None:
        return ["LEAD DUE: the story has stalled, but no open thread or source is on record to build a lead from. "
                "Bring in a way forward of your own, or hold it."]

    def ref(i: str) -> str:
        return f"{_name(st, i)} ({i})" if i in st.entities else str(i)

    trace = clock_trace(st, out.source_id) if out.source_id in st.clocks else None
    return ["LEAD DUE: " + "; ".join(x for x in (f"thread {ref(out.thread)}" if out.thread else "",
                                                 f"source {ref(out.source_id)}" if out.source_id else "",
                                                 f"form: {out.form}", f"its omen now: {trace}" if trace else "") if x)
            + ". Nothing was added to the world. Bring it in with your own tools (a walk-on with `knows`, "
            "`reveal_clue`, a fact), or hold it."]


def _witness(ctx: TurnContext) -> list[str]:
    """15.9.4 on the dm-tools path: a necessary clue node with fewer than two live sources is told to the DM once per
    shortfall, when a scene opens (a scene end or travel). Code places nothing: the DM puts a witness or document on
    it with `new_npc` / `new_item` `knows: <node id>` (which takes the node's reserve)."""
    from engine.gen.case import short_of_sources

    tx, st = ctx.need_tx(), ctx.state
    scene = st.scene.scene_id if st.scene else None
    seen = st.meta.get("witness_scene")
    if scene is None or scene == seen:
        return []
    short = short_of_sources(st)
    told = [n for n in (st.meta.get("told_short") or []) if n in {s[0] for s in short}]  # a node that recovered resets
    new = [s for s in short if s[0] not in told]
    tx.add(meta("witness_scene", scene, "15.9.4"))
    tx.add(meta("told_short", told + [s[0] for s in new], "15.9.4"))
    return [f"WITNESS NEEDED: the answer '{fact}' (clue node {nid}) has {live} live source(s), fewer than 2. Nothing was "
            f"added to the world. Bring in a witness or a document of your own with `new_npc` / `new_item` and "
            f"`knows: {nid}`, or hold it." for nid, live, fact in new]


def time_jumped(ctx: TurnContext) -> bool:
    """A rest or a day boundary passed since this scene began: a spine fact, so a new scene opens (12.4.2 (3))."""
    st = ctx.state
    return st.scene is not None and any(st.time.last_boundary.get(b, 0) > st.scene.started_seq for b in JUMPS)
