"""Pacing (12.6-12.9; T062): the tension dial, the inconclusive streak and lead injection (P16), the pacing push,
random events, the rotation ledger and the live-lead audit.

    t = tension(state, rules)                         # 1..9, background (12.6.3)
    ev = random_event(ctx, source="oracle_doubles_lte_tension")      # PR-12-6 steps 1-3 (rolls, no writes)
    lead = inject_lead(ctx)                           # PR-12-3 when trg.lead_injection is raised

The handler bodies (`tension_update`, `inconclusive_streak`, `pacing_push`, `rotation_update`, `lead_audit`)
are registered by engine/world/handlers.py. Meta keys: `tension`, `pacing.phase` (build | peak | relax; the M2
intensity handler moves it), `inconclusive` {count, since}, `scene_push`, `rotation` {pillar, challenge_type},
`fallback_queue` [thread ids], `lead_tried` {thread: [ids]}, `lead_injection` (the last injection's log),
`last_event_target`, `control_streak`.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from engine.data.loader import Rules
from engine.resolve.tables import roll_table
from engine.store.clocks import stage as clock_stage
from engine.store.events import WORLD, Event
from engine.store.projection import WorldState
from engine.time.handlers import HandlerResult
from engine.time.scheduler import TimeContext
from engine.world.common import (
    WorldError,
    active_pc,
    fact,
    lower_trigger,
    meta,
    raise_trigger,
    scene_events,
    scene_number,
    severity_rank,
    stage,
    trigger_raised,
)

LEAD_TRIGGER = "trg.lead_injection"
PUSH_TRIGGER = "trg.pacing_push"
_HARM_CHAOS = ("harm_state.staggered", "harm_state.dying")
# How a lead's form reaches the PC (00.6 knowledge `how`), by tbl.lead_injection row.
_FORM_HOW = {1: "told", 2: "overheard", 3: "witnessed", 4: "witnessed", 5: "witnessed", 6: "told", 7: "told",
             8: "told", 9: "inferred", 10: "witnessed", 11: "told", 12: "rumor"}
_FALLBACK_HOW = {"sources_1_3_4": "inferred", "sources_2_5_6_7": "told"}


class RandomEvent(BaseModel):
    """PR-12-6 steps 1-3: what the World role interprets in one sentence (step 4) and writes (step 5)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    source: str
    focus: str
    focus_roll: int | None = None
    substituted: str | None = None  # why the rolled focus was replaced
    target: str | None = None
    target_list: str | None = None
    meaning: list[str] = Field(default_factory=list)  # verb, subject
    events: list[Event] = Field(default_factory=list)  # staged already


class LeadInjection(BaseModel):
    """PR-12-3: the source taken, the form, and the facts written (the narrator delivers it this turn)."""

    rung: int
    source_rung: str
    source_id: str | None
    thread: str | None
    form: str
    form_roll: int | None
    facts: list[str] = Field(default_factory=list)
    not_built: bool = False  # rung 7 (a new ch.11 hook) is Milestone 6


# ------------------------------------------------------------------------------------------- the dials


def tension(state: WorldState, rules: Rules) -> int:  # rule: 12.6.3
    t = rules.pacing["tension"]
    return int(state.meta.get("tension", t["start"]))


def phase(state: WorldState) -> str:  # rule: 12.7.2
    return str(state.meta.get("pacing.phase") or "build")


def tension_points(tx: Any, rules: Rules) -> tuple[list[str], list[str]]:  # rule: 12.6.3
    """The current scene's chaos and control items (one point each, each at most once), from the scene log."""
    from engine.world.scenes import agenda_answer, scene_info, scene_test_result
    state: WorldState = tx.state
    sc = state.scene
    if sc is None:
        return [], []
    names = rules.pacing["tension"]["rules"]
    ch, co = names["chaos_points"], names["control_points"]
    pc = active_pc(state)
    evs = scene_events(tx, sc.started_seq)
    info, test = scene_info(state), scene_test_result(state)
    answered = agenda_answer(state)
    hoped = bool(sc.hoped_answer)
    costs = [severity_rank(c.get("severity")) for e in evs if e.type == "frame_resolved"
             for c in e.payload.costs]  # type: ignore[attr-defined]
    chaos: list[str] = []
    control: list[str] = []
    if test.get("result") in ("altered", "interrupted") or info.get("interrupt"):
        chaos.append(ch[0])
    if hoped and answered == "against_hope":
        chaos.append(ch[1])
    if any(c >= 3 for c in costs):
        chaos.append(ch[2])
    if any(e.type == "fact_set" and e.payload.subject == pc  # type: ignore[attr-defined]
           and ((e.payload.predicate == "harm_state" and e.payload.value in _HARM_CHAOS)  # type: ignore[attr-defined]
                or (e.payload.predicate == "defeated" and e.payload.value)) for e in evs):  # type: ignore[attr-defined]
        chaos.append(ch[3])
    if any(e.type == "table_rolled" and _twist_rank(e.payload.table_id, e.payload.context) >= 3  # type: ignore[attr-defined]
           for e in evs):
        chaos.append(ch[4])
    ticks = [e.payload for e in evs if e.type == "clock_ticked"]
    if any(_opposition(state, p.clock_id, pc) and (p.stage == "imminent" or p.completed)  # type: ignore[attr-defined]
           for p in ticks):
        chaos.append(ch[5])
    if hoped and answered == "as_hoped":
        control.append(co[0])
    if any(p.completed and _is_progress(state, p.clock_id) for p in ticks):  # type: ignore[attr-defined]
        control.append(co[1])
    outcome = state.meta.get("scene_outcome") or {}
    if outcome.get("scene_id") == sc.scene_id and outcome.get("opposition_overcome") and max(costs, default=0) <= 2:
        control.append(co[2])
    if info.get("purpose_declared") and test.get("result") == "expected":
        control.append(co[3])
    if any(e.type == "relationship_set" and e.payload.kind == "standing" and e.payload.b == pc  # type: ignore[attr-defined]
           and (e.payload.steps or 0) > 0 for e in evs):  # type: ignore[attr-defined]
        control.append(co[4])
    if any(e.type == "unsealed" and _thread_secret(state, e.payload.ref) for e in evs):  # type: ignore[attr-defined]
        control.append(co[5])
    return chaos, control


def _twist_rank(table_id: str, context: dict[str, Any]) -> int:
    if table_id.startswith("tbl.twist_s"):
        return severity_rank("S" + table_id.rsplit("_s", 1)[-1])
    if table_id == "tbl.twist":
        return severity_rank(context.get("severity"))
    return 0


def _opposition(state: WorldState, clock_id: str, pc: str | None) -> bool:
    c = state.clocks.get(clock_id)
    return c is not None and c.kind != "progress" and (pc is None or c.owner != pc)


def _is_progress(state: WorldState, clock_id: str) -> bool:
    c = state.clocks.get(clock_id)
    return c is not None and c.kind == "progress"


def _thread_secret(state: WorldState, ref: str) -> bool:
    base = ref.partition("#")[0]
    f = state.facts.get(base)
    subject = f.subject if f else base
    e = state.entities.get(subject)
    return e is not None and e.kind == "thread" and e.data.get("status", "active") == "active"


def tension_update(ctx: TimeContext) -> HandlerResult:  # rule: 12.6.3
    # rule: 12.7.5
    """`h.12.tension_update` (scene_end, phase 9): +1 when chaos > control, -1 when control > chaos, clamp 1..9.
    Also counts the 12.7.5 streak of scenes with control > chaos (`control_streak`)."""
    tx, rules = ctx.tx, ctx.rules
    chaos, control = tension_points(tx, rules)
    cfg = rules.pacing["tension"]
    t0 = tension(tx.state, rules)
    delta = (len(chaos) > len(control)) - (len(control) > len(chaos))
    t1 = max(int(cfg["min"]), min(int(cfg["max"]), t0 + delta))
    streak = int(tx.state.meta.get("control_streak") or 0) + 1 if len(control) > len(chaos) else 0
    stage(ctx, meta("tension", t1, "12.6.3"), meta("control_streak", streak, "12.7.5"))
    return HandlerResult(summary=f"tension {t0}->{t1} (chaos {len(chaos)}, control {len(control)})")


# ------------------------------------------------------------------------------- inconclusive streak (P16)


def _reach_value(reach: Any) -> int:
    """A delivered reach as stored by the pipeline (its 00.3.15 name, e.g. "limited") or a number."""
    from engine.resolve.types import REACH_VALUE

    if isinstance(reach, int):
        return reach
    text = str(reach or "0")
    return REACH_VALUE.get(text, int(text) if text.isdigit() else 0)


def beat_conclusive(events: Sequence[Event], pc: str | None) -> bool:  # rule: 12.8.1
    """01.11.4: a beat is conclusive when it wrote a fact the PC learned, a clock change, a position change or a
    delivered reach >= 1."""
    for e in events:
        p: Any = e.payload
        if e.type == "knowledge_recorded" and p.knower == pc:
            return True
        if e.type in ("clock_created", "clock_ticked"):
            return True
        if e.type == "position_set" and p.entity == pc:
            return True
        if e.type == "frame_resolved" and _reach_value((p.delivered or {}).get("reach")) >= 1:
            return True
    return False


def inconclusive_streak(ctx: TimeContext) -> HandlerResult:  # rule: 12.8.1
    """`h.12.inconclusive_streak` (beat_end, phase 9): count consecutive inconclusive beats; at
    `lead_injection.threshold` raise `trg.lead_injection`."""
    tx, rules = ctx.tx, ctx.rules
    prev = tx.state.meta.get("inconclusive") or {}
    sc = tx.state.scene
    since = int(prev.get("since") or (sc.started_seq if sc else tx.peek_seq() - 1))  # the first beat: this scene
    evs = [e for e in scene_events(tx, since + 1) if e.type not in ("boundary_marked", "handler_ran")]
    pc = active_pc(tx.state)
    count = 0 if beat_conclusive(evs, pc) else int(prev.get("count") or 0) + 1
    stage(ctx, meta("inconclusive", {"count": count, "since": tx.peek_seq()}, "12.8.1"))
    threshold = int(rules.pacing["lead_injection"]["threshold"])
    if count >= threshold and not trigger_raised(tx.state, LEAD_TRIGGER):
        stage(ctx, raise_trigger(tx, LEAD_TRIGGER, {"count": count}, rule_id="12.8.1"))
        return HandlerResult(summary=f"inconclusive {count}: trg.lead_injection raised")
    return HandlerResult(summary=f"inconclusive {count}")


# ------------------------------------------------------------------------------------- lead injection


def inject_lead(ctx: TimeContext, *, form_misfit: bool = False) -> LeadInjection:  # rule: PR-12-3
    """PR-12-3: the first eligible source on the ladder, a form from `tbl.lead_injection` (threat forms excluded
    in PEAK and RELAX), then the writes: a fact naming the lead, `knowledge_recorded` for the PC, the counter
    reset, the trigger lowered and the injection logged. `form_misfit` (the DM's fit test said no twice) takes
    the fallback form."""
    from engine.world.scenes import scene_info
    from engine.world.social import cast_list, thread_list
    tx, rules, rng = ctx.tx, ctx.rules, ctx.rng
    if rng is None:
        raise WorldError("lead injection needs ctx.rng")
    state = tx.state
    pc = active_pc(state)
    if pc is None:
        raise WorldError("no PC")
    ladder = list(rules.pacing["lead_injection"]["source_ladder"])
    threads = {t["id"]: t for t in thread_list(state) if t["status"] == "active"}
    scene_thread = scene_info(state).get("thread")
    queue = list(state.meta.get("fallback_queue") or [])
    clues = _unfound_clues(state)

    def by_weight(items: list[tuple[str, int]]) -> str | None:
        if not items:
            return None
        top = max(w for _, w in items)
        tied = [i for i, w in items if w == top]
        return tied[0] if len(tied) == 1 else rng.choice(tied, "lead injection: tie at a rung")

    pick: tuple[int, str | None, str | None] | None = None  # (rung index, source id, thread)
    for i, rung in enumerate(ladder):
        src: str | None = None
        thr: str | None = scene_thread
        if rung == "unfound_clue_of_scene_thread" and scene_thread:
            src = next((c for c, t in clues if t == scene_thread), None)
        elif rung == "scene_thread_proactive_fallback" and scene_thread in queue:
            src = scene_thread
        elif rung == "unfound_clue_of_other_active_thread_by_weight":
            cands = [(c, threads[t]["weight"]) for c, t in clues if t != scene_thread and t in threads]
            # M1: the seed's lead threads (12.16.12 openings) are hooks with no clue entities yet; their
            # `points_to` node stands in for a placement.
            cands += [(t["id"], t["weight"]) for t in threads.values()
                      if t["id"] != scene_thread and t.get("thread_kind") == "lead" and _node_exists(state, t.get("points_to"))]
            src = by_weight(cands)
            thr = _clue_thread(state, src) or src
        elif rung == "most_advanced_opposition_clock_omen_as_trace":
            src = _most_advanced_clock(state, pc)
            thr = None
        elif rung == "cast_npc_with_unfulfilled_want_by_weight":
            src = by_weight([(n, w) for n, w in cast_list(state).items() if _open_want(state, n)])
            thr = None
        elif rung == "region_rumor_pointing_to_existing_node":
            src = next((eid for eid, e in state.entities.items() if e.kind == "rumor"
                        and _node_exists(state, e.data.get("points_to"))), None)
            thr = None
        elif rung == "new_hook_from_ch11":
            pick = (i, None, None)
            break
        if src is not None:
            pick = (i, src, thr)
            break
    assert pick is not None
    i, src, thr = pick
    form, form_roll, how = _lead_form(ctx, i + 1, form_misfit)
    facts: list[str] = []
    if src is not None:
        subject = src if src in state.entities else WORLD
        ev = fact(tx, subject, f"lead.{thr or src}", {"form": form, "thread": thr, "source_rung": ladder[i]},
                  rule_id="PR-12-3", source="generation", visibility="available")
        stage(ctx, ev)
        fid = ev.payload.fact_id  # type: ignore[attr-defined]
        stage(ctx, Event.of("knowledge_recorded", rule_id="PR-12-3", knower=pc, fact_id=fid, how=how))
        facts.append(fid)
    out = LeadInjection(rung=i + 1, source_rung=ladder[i], source_id=src, thread=thr, form=form, form_roll=form_roll,
                        facts=facts, not_built=src is None)
    stage(ctx, meta("inconclusive", {"count": 0, "since": tx.peek_seq()}, "PR-12-3"),
          *lower_trigger(tx, LEAD_TRIGGER, rule_id="PR-12-3"),
          meta("lead_injection", {"scene_id": state.scene.scene_id if state.scene else None,
                                  **out.model_dump(include={"source_rung", "source_id", "form_roll", "facts"})},
               "PR-12-3"))
    if src is not None or thr is not None:
        from engine.world.social import feature
        feature(ctx, [x for x in (src, thr) if x])
        # spec 029 (T2): the form's terms, like any hook's: who brings it, where, the words of what is found
        from engine.gen.hooks import write_injection
        omen = clock_trace(state, src) if src in state.clocks else None
        write_injection(tx, roll=out.form_roll, form=form, thread=thr, src=src, source_text=omen or "")
    return out


def _lead_form(ctx: TimeContext, rung: int, misfit: bool) -> tuple[str, int | None, str]:  # rule: 12.8.2
    tbl = ctx.rules.table("tbl.lead_injection")
    key = "sources_1_3_4" if rung in (1, 3, 4) else "sources_2_5_6_7"
    if misfit:
        return str(tbl["fallback_forms"][key]), None, _FALLBACK_HOW[key]
    ph = phase(ctx.tx.state)
    assert ctx.rng is not None
    for attempt in range(2):
        r = roll_table("tbl.lead_injection", {"phase": ph}, rules=ctx.rules, state=ctx.tx.state, rng=ctx.rng,
                       purpose="lead injection form" + (" (re-roll)" if attempt else ""))
        stage(ctx, *r.events)
        if not ("threat" in (r.row.get("tags") or ()) and ph in ("peak", "relax")):
            return str(r.entry), r.roll, _FORM_HOW.get(int(r.roll or 0), "told")
    return str(tbl["fallback_forms"][key]), None, _FALLBACK_HOW[key]


def _unfound_clues(state: WorldState) -> list[tuple[str, str]]:
    """(clue id, thread id) for clue entities not yet found."""
    return [(eid, str(e.data.get("thread"))) for eid, e in sorted(state.entities.items())
            if e.kind == "clue" and e.data.get("thread") and not e.data.get("found")
            and not state.fact_value(eid, "found")]


def _clue_thread(state: WorldState, src: str | None) -> str | None:
    e = state.entities.get(src) if src else None
    return str(e.data.get("thread")) if e is not None and e.kind == "clue" else None


def _node_exists(state: WorldState, node: Any) -> bool:
    return isinstance(node, str) and (node in state.entities or node in state.clocks)


def _most_advanced_clock(state: WorldState, pc: str) -> str | None:
    cands = [c for c in state.clocks.values() if c.status == "active" and c.visibility in ("sensed", "hidden")
             and c.kind != "progress" and c.owner != pc and c.omens]
    if not cands:
        return None
    return max(cands, key=lambda c: (c.filled / max(1, c.segments), c.id)).id


def clock_trace(state: WorldState, clock_id: str) -> str | None:  # rule: 12.8.2
    """Rung 4's lead: the clock's current omen, re-rendered by the narrator as a concrete trace (no tick)."""
    c = state.clocks[clock_id]
    omens = c.omens.get(clock_stage(c.filled, c.segments)) or []
    return omens[0] if omens else None


def _open_want(state: WorldState, npc: str) -> bool:
    from engine.world.social import npc_field
    wants = npc_field(state, npc, "wants")
    return bool(wants) and any(w.get("status", "open") == "open" for w in wants or [] if isinstance(w, dict))


# -------------------------------------------------------------------------------------- random events


def random_event(ctx: TimeContext, *, source: str) -> RandomEvent:  # rule: PR-12-6
    """PR-12-6 steps 1-3: focus (`tbl.event_focus`; threat foci read as omen in PEAK and RELAX), target from the
    weighted list (empty: the stated substitute focus; a protected thread never resolves off-screen), meaning
    (`tbl.meaning`, action). The table rolls are staged; interpretation and writes are the World role's."""
    from engine.world.social import cast_list, protected_threads, thread_list
    tx, rules, rng = ctx.tx, ctx.rules, ctx.rng
    if rng is None:
        raise WorldError("a random event needs ctx.rng")
    if source not in rules.pacing["events"]["sources"]:
        raise WorldError(f"{source!r} is not a random-event source (12.6.5)")
    ph = phase(tx.state)
    r = roll_table(rules.pacing["events"]["table"], {"phase": ph}, rules=rules, state=tx.state, rng=rng,
                   purpose="random event focus")
    stage(ctx, *r.events)
    focus, row, sub = str(r.entry), r.row, None
    lists: dict[str, dict[str, int]] = {
        "cast": cast_list(tx.state),
        "thread": {t["id"]: t["weight"] for t in thread_list(tx.state) if t["status"] == "active"},
        "faction": {eid: 1 for eid, e in tx.state.entities.items() if e.kind == "faction" and e.exists == "exists"},
    }
    target = None
    tl = row.get("target_list")
    if tl:
        weights = lists.get(str(tl), {})
        if not weights:
            sub = f"empty {tl} list"
            focus = "new NPC" if tl == "cast" else "rumor arrives"
            tl = None
        else:
            target = _draw(ctx, weights, f"random event target ({tl})")
            if focus == "thread resolves off-screen" and target in protected_threads(tx.state, rules):
                focus, sub = "thread complicates", "protected thread (12.6.5)"
    if ph in ("peak", "relax") and (("threat" in (row.get("tags") or ())) or focus == "thread complicates"):
        focus, sub = "omen", f"threat focus in {ph} (12.7.2)"
    m = roll_table("tbl.meaning", {"meaning_kind": "action"}, rules=rules, state=tx.state, rng=rng,
                   purpose="random event meaning")
    stage(ctx, *m.events)
    if target is not None:
        stage(ctx, meta("last_event_target", target, "12.6.6"))
    return RandomEvent(source=source, focus=focus, focus_roll=r.roll, substituted=sub, target=target,
                       target_list=str(tl) if tl else None, meaning=[str(w) for w in m.words],
                       events=[*r.events, *m.events])


def _draw(ctx: TimeContext, weights: dict[str, int], purpose: str) -> str:  # rule: 12.6.6
    """A weighted draw; an entry drawn twice in a row is re-drawn once."""
    assert ctx.rng is not None
    items = sorted(weights.items())
    pick = ctx.rng.weighted(items, purpose)
    if pick == ctx.tx.state.meta.get("last_event_target") and len(items) > 1:
        pick = ctx.rng.weighted(items, purpose + " (recency re-draw)")
    return pick


# ----------------------------------------------------------------------------------------- pacing push


def pacing_push(ctx: TimeContext) -> HandlerResult:  # rule: 12.7.4
    """`h.12.pacing_push` (scene_start, phase 7): when `trg.pacing_push` is raised and the director is in BUILD,
    choose one push for the scene being framed: a ch.11 bang (`bang_queue`, Milestone 6), else a
    `tbl.vignette` row (rooted in an existing thread, clock or NPC), else the most overdue rotation axis's
    opportunity; written to meta `scene_push`, trigger lowered. PEAK and RELAX hold the push."""
    tx, rules = ctx.tx, ctx.rules
    sc = tx.state.scene
    if sc is None or not trigger_raised(tx.state, PUSH_TRIGGER):
        return HandlerResult(summary="not raised")
    ph = phase(tx.state)
    if ph != "build":
        return HandlerResult(summary=f"held ({ph})")
    push: dict[str, Any] = {"scene_id": sc.scene_id}
    bangs = list(tx.state.meta.get("bang_queue") or [])
    stalest = (overdue(tx.state, rules) or [None])[0]
    if bangs:
        push.update(candidate="ch11_bang_queue", entry=bangs[0])
    else:
        if ctx.rng is None:
            raise WorldError("the pacing push needs ctx.rng")
        r = roll_table("tbl.vignette", {"phase": ph, "rotation_axis": stalest}, rules=rules, state=tx.state,
                       rng=ctx.rng, purpose="pacing push vignette")
        stage(ctx, *r.events)
        push.update(candidate="tbl.vignette", entry=r.entry, roll=r.roll, kind=r.row.get("kind"),
                    rooted_in=r.row.get("rooted_in"), stalest_axis=stalest)
    stage(ctx, meta("scene_push", push, "12.7.4"), *lower_trigger(tx, PUSH_TRIGGER, rule_id="12.7.4"))
    return HandlerResult(summary=f"push: {push['candidate']}")


def raise_push(ctx: TimeContext, reason: str) -> None:  # rule: 12.7.2
    """Raise `trg.pacing_push` for the next scene_start (flatline guard or end of recovery, 12.7.2/12.7.5)."""
    stage(ctx, raise_trigger(ctx.tx, PUSH_TRIGGER, {"reason": reason}, rule_id="12.7.2"))


# ---------------------------------------------------------------------------------------- rotation ledger


def rotation(state: WorldState, rules: Rules) -> dict[str, dict[str, int]]:  # rule: 12.9.1
    """Scenes since each pillar and challenge type was foregrounded (absent = never, counted from game start)."""
    rot = state.meta.get("rotation") or {}
    rcfg = rules.pacing["rotation"]
    n = int(state.counters.get("scn", 0))
    return {"pillar": {p: int((rot.get("pillar") or {}).get(p, n)) for p in rcfg["pillars"]},
            "challenge_type": {c["id"]: int((rot.get("challenge_type") or {}).get(c["id"], n))
                               for c in rcfg["challenge_types"]}}


def overdue(state: WorldState, rules: Rules) -> list[str]:  # rule: 12.9.2
    """Pillars at or past their overdue threshold (player weights applied), stalest first."""
    rot = rotation(state, rules)["pillar"]
    cfg = rules.pacing["rotation"]
    weights = state.meta.get("pillar_weights") or {}
    pw = cfg["player_weights"]
    limit = {p: cfg["overdue"]["pillar_scenes"] * float(pw.get(weights.get(p, "same"), 1)) for p in rot}
    due = [p for p, n in rot.items() if n >= limit[p]]
    return sorted(due, key=lambda p: (-rot[p], p))


def scene_pillar(state: WorldState, rules: Rules) -> str | None:  # rule: 12.9.1
    """The scene's pillar: the branch most of its frames' situation tags carry, else the record's."""
    sc = state.scene
    if sc is None:
        return None
    pillars = set(rules.pacing["rotation"]["pillars"])
    counts: dict[str, int] = {}
    for fs in state.frames.values():
        for tag in _strings(fs.frame):
            if tag.startswith("situation."):
                branch = tag.split(".")[1]
                if branch in pillars:
                    counts[branch] = counts.get(branch, 0) + 1
    if counts:
        return max(sorted(counts), key=lambda b: counts[b])
    return sc.pillar


def _strings(x: Any) -> list[str]:
    if isinstance(x, str):
        return [x]
    if isinstance(x, dict):
        return [s for v in x.values() for s in _strings(v)]
    if isinstance(x, (list, tuple)):
        return [s for v in x for s in _strings(v)]
    return []


def rotation_update(ctx: TimeContext) -> HandlerResult:  # rule: 12.9.1
    """`h.12.rotation_update` (scene_end, phase 9): +1 to every pillar and challenge type, reset the scene's.
    Facets (abilities, licences, hooks) are Milestone 3 (recognition); not tracked here."""
    tx, rules = ctx.tx, ctx.rules
    sc = tx.state.scene
    if sc is None:
        return HandlerResult(summary="no scene")
    rot = rotation(tx.state, rules)
    pillar = scene_pillar(tx.state, rules)
    for axis, key in (("pillar", pillar), ("challenge_type", sc.challenge_type)):
        for k in rot[axis]:
            rot[axis][k] = 0 if k == key else rot[axis][k] + 1
    stage(ctx, meta("rotation", rot, "12.9.1"))
    return HandlerResult(summary=f"pillar {pillar}, challenge {sc.challenge_type}")


# -------------------------------------------------------------------------------------- live-lead audit


def lead_audit(ctx: TimeContext) -> HandlerResult:  # rule: 12.8.4
    """`h.12.lead_audit` (scene_end, phase 7): every active thread needs one live lead (an unfound clue, a queued
    fallback, or a connected node not yet tried for it, `lead_tried`). A thread with none is marked `stalled`
    and its proactive fallback queued (`fallback_queue`). Fewer than three clue placements is reported as a
    content defect in the summary (ch.11/15's generators add placements; Milestone 6)."""
    from engine.world.social import thread_list
    tx = ctx.tx
    state = tx.state
    clues = _unfound_clues(state)
    queue = list(state.meta.get("fallback_queue") or [])
    tried = state.meta.get("lead_tried") or {}
    stalled, defects = [], 0
    for t in thread_list(state):
        if t["status"] != "active":
            continue
        tid = t["id"]
        placements = [c for c, th in clues if th == tid]
        defects += len([e for e in state.entities.values() if e.kind == "clue" and e.data.get("thread") == tid]) < 3
        node = t.get("points_to")
        live = bool(placements) or tid in queue or (_node_exists(state, node) and node not in tried.get(tid, []))
        if not live:
            stalled.append(tid)
            if not state.fact_value(tid, "stalled"):
                stage(ctx, fact(tx, tid, "stalled", True, rule_id="12.8.4", source="ruling", visibility="background"))
            queue.append(tid)
    if stalled:
        stage(ctx, meta("fallback_queue", list(dict.fromkeys(queue)), "12.8.4"))
    return HandlerResult(summary=f"stalled {len(stalled)}; under three placements {defects}")


def mark_tried(ctx: TimeContext, thread: str, node: str) -> None:  # rule: 12.8.4
    """A frame or scene targeted `node` for `thread` (12.8.4's [J:flag] answered true)."""
    tried = dict(ctx.tx.state.meta.get("lead_tried") or {})
    tried[thread] = list(dict.fromkeys([*tried.get(thread, []), node]))
    stage(ctx, meta("lead_tried", tried, "12.8.4"))


def scenes_so_far(state: WorldState) -> int:
    return scene_number(state.scene.scene_id) if state.scene else int(state.counters.get("scn", 0))
