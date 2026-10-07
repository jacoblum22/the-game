"""Scenes (12.4, PR-12-7; T060's deterministic half): the scene record, start and end, the scene test, cut
detection, dead air, and the closed lists the Director's schema needs.

    with store.transaction(turn) as tx:
        ctx = TimeContext(tx, rules, rng)
        st = start_scene(ctx, place="loc.x", mode="free", agenda="Does the ferryman talk?", hoped_answer="yes",
                         pillar="social", cast=["npc.tam"], expected="Wren finds the ferryman at the landing")
        st.test["result"]                     # expected | altered | interrupted | untested (h.12.scene_test)
        ...
        reason = cut_due(tx.state, rules)     # None, or a 12.4.2 cut trigger id
        end_scene(ctx, reason or "player_cut", answered="as_hoped")

The record (data-model.md §4) is the store's `SceneRecord`, written by `scene_started`; the facts the record
cannot change after its start live in meta, keyed to the scene id:
- `scene`          {scene_id, expected, purpose_declared, interrupt, thread, untested, tags}
- `scene_test`     {scene_id, result, roll, tension, adjustments, event}           (h.12.scene_test)
- `scene_agenda`   {scene_id, answered: as_hoped | against_hope | answered}       (12.4.2 (1), 12.6.3)
- `scene_cut`      {scene_id, reason}                                             (interrupt, player cut)
- `dead_air`       consecutive quiet DM turns in this scene                       (12.4.2 (7))
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field

from engine.data.loader import Rules
from engine.store.events import Event, SceneRecord
from engine.store.projection import WorldState
from engine.time import clock
from engine.time.handlers import HandlerResult
from engine.time.scheduler import BoundaryResult, TimeContext, mark_boundary, set_mode
from engine.world.common import WorldError, active_pc, meta, stage, trigger_raised

Answer = Literal["as_hoped", "against_hope", "answered"]
QUIET_CLASSES = frozenset({"SPEECH"})  # 12.4.2 (7): speech or free activities only
# Events that count as "something written" for dead air (time and bookkeeping events do not).
_NOT_WRITES = frozenset({"time_advanced", "boundary_marked", "handler_ran", "handler_skipped", "meta_set",
                         "table_rolled", "pause_opened", "pause_closed"})
_TIME_JUMP_BOUNDARIES = ("watch", "day", "week", "breather", "rest_short", "rest_long")


class SceneStart(BaseModel):
    scene_id: str
    record: SceneRecord
    test: dict[str, Any] = Field(default_factory=dict)
    push: dict[str, Any] | None = None
    narration: list[str] = Field(default_factory=list)


class SceneEnd(BaseModel):
    scene_id: str
    reason: str
    tension: int
    narration: list[str] = Field(default_factory=list)
    chronicle_offer: dict[str, Any] | None = None


# ------------------------------------------------------------------------------------------------ reading


def current_scene(state: WorldState) -> SceneRecord | None:
    return state.scene


def scene_info(state: WorldState) -> dict[str, Any]:
    """The current scene's meta record (`scene`), or {} outside a scene."""
    return _scoped(state, "scene")


def _scoped(state: WorldState, key: str, scene_id: str | None = None) -> dict[str, Any]:
    sid = scene_id or (state.scene.scene_id if state.scene else None)
    v = state.meta.get(key)
    return dict(v) if isinstance(v, dict) and sid and v.get("scene_id") == sid else {}


def cast_present(state: WorldState) -> list[str]:  # rule: 12.4.1
    """The scene's cast: those framed in it plus every NPC positioned at its place who still exists."""
    sc = state.scene
    if sc is None:
        return []
    from engine.world.places import cast_at
    here = cast_at(state, sc.place_id) if sc.place_id else []
    pc = active_pc(state)
    return [i for i in dict.fromkeys([*sc.cast_present, *here]) if i in state.entities and i != pc
            and state.entities[i].exists == "exists"]


def situation_tags(state: WorldState) -> list[str]:
    sc = state.scene
    if sc is None:
        return []
    return list(dict.fromkeys([*sc.situation_tags, *scene_info(state).get("tags", [])]))


def add_situation_tags(ctx: TimeContext, tags: Iterable[str]) -> None:
    info = scene_info(ctx.tx.state)
    if not info:
        raise WorldError("no current scene")
    info["tags"] = list(dict.fromkeys([*info.get("tags", []), *tags]))
    stage(ctx, meta("scene", info, "12.4.1"))


def scene_test_result(state: WorldState, scene_id: str | None = None) -> dict[str, Any]:
    return _scoped(state, "scene_test", scene_id)


def agenda_answer(state: WorldState, scene_id: str | None = None) -> str | None:
    return _scoped(state, "scene_agenda", scene_id).get("answered")


# ---------------------------------------------------------------------------------------- start and end


def untested_reason(state: WorldState, *, place: str | None, mode: str, interrupt: bool) -> str | None:
    """12.4.4: which `pacing.yaml#scenes.untested` case applies, if any."""  # rule: 12.4.4
    if mode == "conflict":
        return "conflict"
    if interrupt:
        return "interrupt_scene"
    pe = state.entities.get(place) if place else None
    if mode == "downtime" and pe is not None and pe.data.get("safe"):
        return "downtime_in_haven"
    last = state.last_scene
    if last is not None and last.place_id == place and last.ended_at is not None:
        if clock.to_rounds(state.time.now) - clock.to_rounds(last.ended_at) < clock.ROUNDS["interval"]:
            return "direct_continuation_under_one_interval"
    return None


def start_scene(ctx: TimeContext, *, place: str | None, mode: str, agenda: str, hoped_answer: str = "",
                pillar: str | None = None, challenge_type: str | None = None, cast: Sequence[str] = (),
                situation_tags: Sequence[str] = (), expected: str | None = None, purpose_declared: bool = False,
                interrupt: bool = False, thread: str | None = None) -> SceneStart:  # rule: PR-12-7
    """PR-12-7 at scene_start: (1) write the record; (2) `mark_boundary(scene_start)`, which runs
    `h.12.scene_test` (unless untested) and `h.12.pacing_push`. Applying an altered or interrupted result and
    framing the scene are the DM's (12.4.3)."""
    tx = ctx.tx
    if tx.state.scene is not None:
        raise WorldError(f"scene {tx.state.scene.scene_id} has not ended")
    if mode not in clock.MODES:
        raise WorldError(f"unknown mode {mode!r}")
    if clock.mode_of(tx.state.time.mode) != mode:
        set_mode(ctx, mode, "scene start")
    sid = tx.mint("scn")
    rec = SceneRecord(scene_id=sid, place_id=place, mode=mode, agenda=agenda, hoped_answer=hoped_answer,
                      pillar=pillar, challenge_type=challenge_type,
                      cast_present=[c for c in dict.fromkeys(cast) if c in tx.state.entities],
                      situation_tags=list(situation_tags))
    untested = untested_reason(tx.state, place=place, mode=mode, interrupt=interrupt)
    stage(ctx, Event.of("scene_started", rule_id="PR-12-7", scene_id=sid, scene=rec))
    stage(ctx, meta("scene", {"scene_id": sid, "expected": expected, "purpose_declared": purpose_declared,
                              "interrupt": interrupt, "thread": thread, "untested": untested, "tags": []}, "12.4.1"),
          meta("dead_air", 0, "12.4.2"))
    done = mark_boundary(ctx, "scene_start", {"scene_id": sid, "untested": untested})
    state = tx.state
    push = state.meta.get("scene_push")
    return SceneStart(scene_id=sid, record=state.scene or rec, test=scene_test_result(state, sid),
                      push=push if isinstance(push, dict) and push.get("scene_id") == sid else None,
                      narration=_narration(done))


def end_scene(ctx: TimeContext, reason: str, *, answered: Answer | None = None,
              opposition_overcome: bool = False) -> SceneEnd:  # rule: PR-12-7
    """PR-12-7 at scene_end: record how the agenda was answered (12.6.3's hope), `mark_boundary(scene_end)` (its
    handlers read the still-current scene: h.12.lead_audit, h.12.tension_update, h.12.rotation_update,
    h.12.npc_memory, h.12.bookkeeping, h.15.patience_reset, ...), then `scene_ended`."""
    tx = ctx.tx
    sc = tx.state.scene
    if sc is None:
        raise WorldError("no current scene to end")
    if answered is not None:
        mark_agenda_answered(ctx, answered)
    stage(ctx, meta("scene_outcome", {"scene_id": sc.scene_id, "opposition_overcome": opposition_overcome},
                    "12.6.3"))
    done = mark_boundary(ctx, "scene_end", {"scene_id": sc.scene_id, "reason": reason})
    offer = tx.state.meta.get("chronicle_offer")
    stage(ctx, Event.of("scene_ended", rule_id="PR-12-7", scene_id=sc.scene_id, reason=reason),
          meta("dead_air", 0, "12.4.2"))
    from engine.world.pacing import tension
    return SceneEnd(scene_id=sc.scene_id, reason=reason, tension=tension(tx.state, ctx.rules),
                    narration=_narration(done),
                    chronicle_offer=offer if isinstance(offer, dict) and offer.get("scene_id") == sc.scene_id
                    else None)


def reopen_scene(ctx: TimeContext) -> str:  # rule: 12.4.2
    """The player stays ("I'm not done here"): the last scene re-opens with the same id (12.4.2, class iv)."""
    tx = ctx.tx
    last = tx.state.last_scene
    if tx.state.scene is not None or last is None:
        raise WorldError("nothing to re-open")
    rec = last.model_copy(update={"ended_at": None})
    stage(ctx, Event.of("scene_started", rule_id="12.4.2", source="player_stays", scene_id=rec.scene_id, scene=rec),
          meta("dead_air", 0, "12.4.2"))
    return rec.scene_id


def mark_agenda_answered(ctx: TimeContext, answered: Answer) -> None:  # rule: 12.4.2
    """12.4.2 (1): a write this turn settled the scene's question; `as_hoped`/`against_hope` per 12.6.3."""
    sc = ctx.tx.state.scene
    if sc is None:
        raise WorldError("no current scene")
    stage(ctx, meta("scene_agenda", {"scene_id": sc.scene_id, "answered": answered}, "12.4.2"))


def note_cut(ctx: TimeContext, reason: Literal["interrupt", "player_cut"]) -> None:  # rule: 12.4.2
    """An interrupt halted `advance_time` (12.4.2 (4)) or the player said to move on (12.4.2 (6))."""
    sc = ctx.tx.state.scene
    if sc is None:
        raise WorldError("no current scene")
    stage(ctx, meta("scene_cut", {"scene_id": sc.scene_id, "reason": reason}, "12.4.2"))


def _narration(done: list[BoundaryResult]) -> list[str]:
    return [n for b in done for n in b.narration]


# --------------------------------------------------------------------------------------- dead air and cuts


def turn_is_quiet(input_classes: Iterable[str], events: Iterable[Event]) -> bool:  # rule: 12.4.2
    """12.4.2 (7): the message held only SPEECH (or free activities) and nothing was written except time."""
    if not set(input_classes) <= QUIET_CLASSES:
        return False
    return all(e.type in _NOT_WRITES for e in events)


def note_turn(ctx: TimeContext, *, quiet: bool) -> int:  # rule: 12.4.2
    """Count a DM turn for dead air: +1 when quiet, else back to 0. Returns the counter."""
    n = int(ctx.tx.state.meta.get("dead_air") or 0) + 1 if quiet else 0
    stage(ctx, meta("dead_air", n, "12.4.2"))
    return n


def cut_due(state: WorldState, rules: Rules) -> str | None:  # rule: 12.4.2
    """The first 12.4.2 cut trigger that is true now (`pacing.yaml#scenes.cut_triggers` order), else None.
    `dead_air` means the DM offers the cut in one line (the player may stay)."""
    sc = state.scene
    if sc is None:
        return None
    cfg = rules.pacing["scenes"]
    checks = {
        "agenda_answered": lambda: agenda_answer(state) is not None,
        "place_change": lambda: _place_changed(state, sc),
        "time_jump": lambda: _time_jumped(state, sc),
        "interrupt": lambda: _scoped(state, "scene_cut").get("reason") == "interrupt",
        "conflict_end": lambda: state.time.last_boundary.get("conflict_end", 0) > sc.started_seq,
        "player_cut": lambda: _scoped(state, "scene_cut").get("reason") == "player_cut",
        "dead_air": lambda: int(state.meta.get("dead_air") or 0) >= int(cfg["dead_air_turns"]),
    }
    return next((t for t in cfg["cut_triggers"] if t in checks and checks[t]()), None)


def _place_changed(state: WorldState, sc: SceneRecord) -> bool:
    pc = active_pc(state)
    pos = state.positions.get(pc) if pc else None
    return bool(sc.place_id and pos and pos.location and pos.location != sc.place_id)


def _time_jumped(state: WorldState, sc: SceneRecord) -> bool:
    if any(state.time.last_boundary.get(b, 0) > sc.started_seq for b in _TIME_JUMP_BOUNDARIES):
        return True
    start = sc.started_at
    return start is not None and clock.to_rounds(state.time.now) - clock.to_rounds(start) >= clock.ROUNDS["hour"]


# ------------------------------------------------------------------------------------------- scene test


def run_scene_test(ctx: TimeContext) -> HandlerResult:  # rule: 12.4.4
    # rule: T-12-9
    # rule: 12.6.4
    """`h.12.scene_test` (scene_start, phase 7): d10 against tension; roll <= T - 3 deviates (odd altered, even
    interrupted; interrupted reads as altered in PEAK and RELAX). Altered rolls `tbl.scene_adjustment`;
    interrupted rolls a random event (PR-12-6). The result is written to meta `scene_test`."""
    from engine.resolve.tables import roll_table
    from engine.world.pacing import phase, random_event, tension
    tx, rules = ctx.tx, ctx.rules
    sc = tx.state.scene
    if sc is None:
        return HandlerResult(summary="no scene")
    untested = ctx.payload.get("untested", scene_info(tx.state).get("untested"))
    out: dict[str, Any] = {"scene_id": sc.scene_id}
    if untested:
        out.update(result="untested", reason=untested)
        stage(ctx, meta("scene_test", out, "12.4.4"))
        return HandlerResult(summary=f"untested ({untested})")
    if ctx.rng is None:
        raise WorldError("the scene test needs ctx.rng")
    t = tension(tx.state, rules)
    cfg = rules.pacing["scene_test"]
    res = roll_table(cfg["table"], {"tension": t}, rules=rules, state=tx.state, rng=ctx.rng, purpose="scene test")
    stage(ctx, *res.events)
    roll = int(res.roll or 0)
    result = "expected"
    if roll <= t - 3:
        result = cfg["odd"] if roll % 2 else cfg["even"]
        if result == "interrupted" and phase(tx.state) in ("peak", "relax"):  # rule: 12.7.2
            result = "altered"
    out.update(result=result, roll=roll, tension=t)
    if result == "altered":
        out["adjustments"] = _adjustments(ctx)
    elif result == "interrupted":
        out["event"] = random_event(ctx, source="interrupted_scene").model_dump(exclude={"events"})
    stage(ctx, meta("scene_test", out, "12.4.4"))
    return HandlerResult(summary=f"{result} (d10 {roll}, tension {t})")


def _adjustments(ctx: TimeContext) -> list[str]:  # rule: 12.4.4
    """`tbl.scene_adjustment`; "two adjustments" rolls two more (a repeat of that row is dropped)."""
    from engine.resolve.tables import roll_table
    assert ctx.rng is not None
    out: list[str] = []
    todo, doubled = 1, False
    while todo:
        todo -= 1
        r = roll_table("tbl.scene_adjustment", rules=ctx.rules, state=ctx.tx.state, rng=ctx.rng,
                       purpose="scene adjustment")
        stage(ctx, *r.events)
        if str(r.entry) == "two adjustments":
            if not doubled:
                todo, doubled = todo + 2, True
            continue
        out.append(str(r.entry))
    return out


# ------------------------------------------------------------------------------------------- the Director


def director_enums(state: WorldState, rules: Rules) -> dict[str, Any]:  # rule: 12.4.2
    # rule: 12.9.1
    # rule: T-12-7
    """The closed lists the Director schema needs (contracts/model-calls.md S), keyed like
    `engine.dm.schemas.SchemaContext`'s Director fields, plus `push_raised` and `lead_fires` for
    `schema_context(..., places=, push_raised=, lead_fires=)`."""
    from engine.world.places import location, reachable
    from engine.world.social import thread_list
    pacing = rules.pacing
    here = location(state) or (state.scene.place_id if state.scene else None)
    places = [here, *(x.to for x in reachable(state, here))] if here else []
    push = trigger_raised(state, "trg.pacing_push")
    lead = trigger_raised(state, "trg.lead_injection")
    last = state.scene or state.last_scene

    def visible(eid: str) -> bool:
        seal = state.seals.get(eid)
        return seal is None or bool(seal.slice)

    return {
        "modes": [m["to"] for m in pacing.get("modes", []) if m.get("to") != "previous"],
        "previous_mode": last.mode if last else None,
        "places": list(dict.fromkeys(places)),
        "current_place": here,
        "pillars": list(pacing["rotation"]["pillars"]),
        "challenge_types": [c["id"] for c in pacing["rotation"]["challenge_types"]],
        "known_ids": [eid for eid, e in state.entities.items()
                      if e.kind in ("npc", "companion", "adversary", "faction") and e.exists == "exists" and visible(eid)],
        "push_options": list(pacing["push"]["candidates"]) if push else [],
        "thread_ids": [t["id"] for t in thread_list(state) if t["status"] == "active"],
        "lead_routes": list(pacing["lead_injection"]["source_ladder"]) if lead else [],
        "push_raised": push,
        "lead_fires": lead,
    }


__all__ = ["SceneStart", "SceneEnd", "current_scene", "scene_info", "cast_present", "situation_tags",
           "add_situation_tags", "scene_test_result", "agenda_answer", "untested_reason", "start_scene", "end_scene",
           "reopen_scene", "mark_agenda_answered", "note_cut", "turn_is_quiet", "note_turn", "cut_due",
           "run_scene_test", "director_enums"]
