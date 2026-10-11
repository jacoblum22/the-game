"""Spec 032 P4 (lane W): the world step of a dm-tools exchange. Code runs what the spine owns and hands the DM the
outcomes as plain words; it gives no orders and calls no model.

    facts = world_step(ctx, t)    # t: the dm_tools Turn (rec, oof, beats, stats); [] when a pause is open

In the pipeline's order (engine/dm/world_step.py, reused, not rebuilt): the foes answer (`foes_act`: the conflict's
own foe turn, harm by code), the exchange costs its mode's time (`beat_time`, or one `beat_cost` for an exchange with
no beat), the beat counter and dead air move, clocks that ticked give their omens, raised triggers give their warnings,
and a raised lead injection is written (`inject_lead`). Scene ends are the DM's call (the `end_scene` tool): nothing
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
from engine.world.common import trigger_raised
from engine.world.pacing import inject_lead
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
    picked = _foes(ctx, t, rec, oof) if spent else {}  # [spec 033 D2] the DM picks each foe's act; code rolls it
    acted = list(picked)
    ws.release_holds(ctx, rec)  # 06.5.2
    _time(ctx, t, spent, acted)  # before the omens: the interval it crosses is what ticks a clock
    ws.clock_omens(ctx, rec)
    ws.fired_triggers(ctx, rec)
    note_turn(tctx, quiet=turn_is_quiet(["DECLARATION" if t.beats else "SPEECH"], ctx.need_tx().events))
    facts = _foe_facts(ctx, rec, n_act, oof[n_oof:])
    t.stats["world"]["foe_turns"] += [{"foe": a.npc, "did": a.action, "act": picked[a.npc][0], "picked_by": picked[a.npc][1]}
                                      for a in rec.npc_actions[n_act:] if a.npc in picked]
    facts += [f"An omen: {o.omen}" + (" (it has come to a head)" if o.completed else "")
              for o in rec.omens[n_om:] if o.omen]
    if trigger_raised(ctx.state, LEAD):  # raised at beat_end by the inconclusive streak (12.8.1)
        facts += _lead(ctx, rec)
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


def _foes(ctx: TurnContext, t: Any, rec: Any, oof: list[dict[str, str]]) -> dict[str, tuple[str, str]]:
    # rule: 06.9.1
    """[spec 033 D2, DL-06-40] The foe call: with a fight on and a foe able, the DM picks each able foe's act from the
    acts legal now (T-06-16) and its target. Code checks legality, rolls the act (06.9.2) and applies it. A foe the DM
    left out, or whose pick is outside its list, takes the first legal row of its behavior list (else `wait`), the PC as
    target, logged `not_chosen:foes.<id>`; no re-ask. Returns {foe: (act, "dm" | "default")} in act order."""
    from engine.dm import dm_tools
    from engine.llm.base import Packet, call_role
    from engine.resolve import foe_act
    from engine.resolve.conflict import able, check_end
    from engine.resolve.conflict import record as conflict

    st, pc = ctx.state, rec.pc or ""
    crec = conflict(st)
    if not crec or not pc or st.open_pause() is not None:
        return {}
    legal = {f: foe_act.legal_acts(st, f, pc) for f in crec.get("foes", []) if able(st, f)}
    picks: dict[str, dict[str, Any]] = {}
    if legal:
        packet = Packet(instructions=dm_tools.load_prompt("dm"), message=dm_tools.foe_message(ctx, t, legal))
        res = call_role(ctx.model, dm_tools.DM_ROLE, dm_tools.foe_schema(legal), packet, turn_id=ctx.turn_id,
                        recorder=ctx.record_call, default={"foes": []})
        t.stats["world"]["foe_calls"] += 1
        for p in (res.data or {}).get("foes") or []:
            if isinstance(p, dict) and p.get("foe") in legal:
                picks.setdefault(str(p["foe"]), p)
    done: dict[str, tuple[str, str]] = {}
    for foe in legal:
        if not (able(ctx.state, foe) and conflict(ctx.state)):
            continue
        now = foe_act.legal_acts(ctx.state, foe, pc)
        p = picks.get(foe) or {}
        by = "dm" if p.get("act") in now else "default"
        pick = str(p["act"]) if by == "dm" else foe_act.default_act(ctx.rules, ctx.state, foe, now)
        if by == "default":
            dm_tools._default(t, f"foes.{foe}")
        target = pc
        raw = str(p.get("target") or "").strip()
        if by == "dm" and raw and raw.lower() != "pc":
            other = dm_tools._id(ctx.state, raw)
            if other in ctx.state.entities and ctx.state.entities[other].kind == "companion" \
                    and not dm_tools._acting(ctx.state, other, here=False):
                target = str(other)  # ponytail: a companion is a legal target without a band check (06.9.3)
            elif other != pc:
                dm_tools._default(t, f"foes.{foe}.target")
        nonlethal = bool(p.get("nonlethal"))
        ws._foe_turn(ctx, rec, foe, oof, target=target, ref=f"{by}:{pick}",
                     do=lambda tc, rng, f, who: foe_act.act(tc, rng, f, pick, who, nonlethal))
        done[foe] = (pick, by)
    check_end(ctx.time_ctx(), pc)
    return done


def _up(s: str) -> str:
    return s[:1].upper() + s[1:]


def _lead(ctx: TurnContext, rec: Any) -> list[str]:
    try:
        inj = inject_lead(ctx.time_ctx())
    except Exception as exc:  # noqa: BLE001 - no eligible source: logged, the counter stays for next time
        rec.notes.append(f"lead injection held: {exc}")
        return []
    st = ctx.state
    names = list(dict.fromkeys(_name(st, i) for i in (inj.thread, inj.source_id) if i in st.entities))  # one line once
    return [f"A lead arrives, in the form: {inj.form}." + (f" On record with it: {', '.join(names)}." if names else "")
            + " It is now known to the character; work it into the scene."]


def time_jumped(ctx: TurnContext) -> bool:
    """A rest or a day boundary passed since this scene began: a spine fact, so a new scene opens (12.4.2 (3))."""
    st = ctx.state
    return st.scene is not None and any(st.time.last_boundary.get(b, 0) > st.scene.started_seq for b in JUMPS)
