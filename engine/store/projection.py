"""The projection: `WorldState` (data-model.md §3), built from events by reducers (T012).

    state = project(events)            # from nothing; honours writes_reverted
    state2 = apply(state, event)       # pure: `state` is not modified
    state3 = fold(state, events)       # pure: one copy, then every event in order

Reducers are deterministic functions of (state, event); they never read rules data, the clock or the RNG, so
rebuilding from the log always equals the live projection. Each reducer mutates a private copy (`apply` and
`fold` copy first). Families filled in later milestones (tally, effect_instance, offer) have stub reducers that
raise `NotBuiltYet`.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from pydantic import BaseModel, Field

from engine import ids
from engine.store.events import (
    NOT_BUILT,
    ClockRecord,
    ConditionInstance,
    EntityRecord,
    Event,
    LicenseInstance,
    PauseRecord,
    Quantity,
    SceneRecord,
    Timestamp,
    Visibility,
)
from engine.store.events import (
    WritesReverted as _WritesReverted,
)


class NotBuiltYet(NotImplementedError):
    """An event of a state family that a later milestone builds (data-model.md §3)."""


class GameInfo(BaseModel):
    seed: int
    engine_version: str
    rules_hash: str
    milestone: int
    config: dict[str, Any] = Field(default_factory=dict)


class FactRecord(BaseModel):  # 00.6.2 Fact plus its bi-temporal start
    id: str
    subject: str
    predicate: str
    value: Any
    kind: str = "fact"
    source: str
    certainty: str
    truth: str = "true"
    visibility: Visibility
    established_at: Timestamp | None = None
    supersedes: str | None = None
    valid_from_seq: int
    persistence: str | None = None  # details only: lasting | scene | beat (00.6.6a)
    pinned: bool = False  # a correction (12.3.6): never archived, always in view with its subject


class DetailRef(BaseModel):  # 00.6.6a: the details index entry
    fact_id: str
    last_used: int = 0  # the turn number a delivered sentence (or the write) last stated it


class SceneCard(BaseModel):  # 12.4.8 step 9: a view over the scene's events, never prose
    scene: str
    place: str | None = None
    agenda: str = ""
    answer: str | None = None
    started_at: Timestamp | None = None
    ended_at: Timestamp | None = None
    started_seq: int = 0
    cast: list[str] = Field(default_factory=list)
    beats: list[dict[str, Any]] = Field(default_factory=list)  # {frame, actor, verb, target, degree}
    facts: list[str] = Field(default_factory=list)
    memories: list[str] = Field(default_factory=list)
    threads: list[str] = Field(default_factory=list)


class RelationshipRecord(BaseModel):
    a: str
    b: str
    kind: str
    value: int


class PositionRecord(BaseModel):
    location: str | None = None
    flags: list[str] = Field(default_factory=list)
    band_to: dict[str, str] = Field(default_factory=dict)


class KnowledgeEntry(BaseModel):
    how: str
    seq: int


class Seal(BaseModel):  # 00.6.5
    gate: str
    slice: str | None = None
    seq: int


class FrameState(BaseModel):
    frame: dict[str, Any]
    committed_seq: int
    resolved: dict[str, Any] | None = None


class Application(BaseModel):  # one condition application, for diminishing returns (00.9.3e)
    target: str
    condition_id: str
    group: str | None
    seq: int


class TimeState(BaseModel):
    now: Timestamp = Field(default_factory=Timestamp)
    mode: str = "free"
    last_boundary: dict[str, int] = Field(default_factory=dict)  # boundary id -> seq it was last marked


class WorldState(BaseModel):
    last_seq: int = 0
    game: GameInfo | None = None
    counters: dict[str, int] = Field(default_factory=dict)
    entities: dict[str, EntityRecord] = Field(default_factory=dict)
    quantities: dict[str, dict[str, Quantity]] = Field(default_factory=dict)  # entity -> name -> quantity
    facts: dict[str, FactRecord] = Field(default_factory=dict)  # current facts only
    fact_keys: dict[str, str] = Field(default_factory=dict)  # "subject|predicate" -> current fact id
    superseded_facts: dict[str, int] = Field(default_factory=dict)  # fact id -> seq it stopped being valid
    relationships: dict[str, RelationshipRecord] = Field(default_factory=dict)  # "a|b|kind"
    positions: dict[str, PositionRecord] = Field(default_factory=dict)
    knowledge: dict[str, dict[str, KnowledgeEntry]] = Field(default_factory=dict)  # knower -> fact -> how
    clocks: dict[str, ClockRecord] = Field(default_factory=dict)
    conditions: dict[str, ConditionInstance] = Field(default_factory=dict)  # instance id -> instance
    applications: list[Application] = Field(default_factory=list)  # this scene's condition applications
    licenses: dict[str, list[LicenseInstance]] = Field(default_factory=dict)
    ledger: dict[str, list[int]] = Field(default_factory=dict)  # this scene: oracle, offers, rulings, ...
    time: TimeState = Field(default_factory=TimeState)
    frames: dict[str, FrameState] = Field(default_factory=dict)  # this scene's frames
    scene: SceneRecord | None = None
    last_scene: SceneRecord | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    table_recency: dict[str, list[str]] = Field(default_factory=dict)
    seals: dict[str, Seal] = Field(default_factory=dict)  # ref -> seal
    pauses: list[PauseRecord] = Field(default_factory=list)  # open pauses, oldest first
    seed_answers: list[dict[str, Any]] = Field(default_factory=list)
    creation_answers: list[dict[str, Any]] = Field(default_factory=list)
    reverted: list[int] = Field(default_factory=list)
    details: dict[str, dict[str, DetailRef]] = Field(default_factory=dict)  # entity -> slot -> detail (00.6.6a)
    scene_cards: dict[str, SceneCard] = Field(default_factory=dict)  # scene id -> card (12.4.8 step 9)

    # -- queries the payload checks use
    def current_fact_id(self, subject: str, predicate: str) -> str | None:
        return self.fact_keys.get(f"{subject}|{predicate}")

    def fact_value(self, subject: str, predicate: str, default: Any = None) -> Any:
        fid = self.current_fact_id(subject, predicate)
        return self.facts[fid].value if fid else default

    def sealable(self, ref: str) -> bool:
        ent, _, field = ref.partition("#")
        if ent in self.entities:
            return not field or field in self.entities[ent].data
        return ref in self.facts

    def open_pause(self) -> PauseRecord | None:
        """The last unclosed pause: what resume re-presents (FR-010)."""
        return self.pauses[-1] if self.pauses else None

    def conditions_on(self, target: str) -> list[ConditionInstance]:
        return [c for c in self.conditions.values() if c.target == target]


# ------------------------------------------------------------------------------------------- reducers

Reducer = Callable[[WorldState, Event, Any], None]
REDUCERS: dict[str, Reducer] = {}


def reducer(*types: str) -> Callable[[Reducer], Reducer]:
    def deco(fn: Reducer) -> Reducer:
        for t in types:
            REDUCERS[t] = fn
        return fn

    return deco


def _seq(ev: Event) -> int:
    assert ev.seq is not None, "reducers need appended events (seq set)"
    return ev.seq


def _log(s: WorldState, kind: str, ev: Event) -> None:
    s.ledger.setdefault(kind, []).append(_seq(ev))


DETAIL = "detail."  # 00.6.6a: a detail is the fact `detail.<slot>`


def _turn_n(ev: Event) -> int:
    parsed = ids.parse_counter_id(ev.turn_id) if ev.turn_id else None
    return parsed[1] if parsed and parsed[0] == ids.TURN else 0


@reducer("details_used")
def _details_used(s: WorldState, ev: Event, p: Any) -> None:  # rule: 00.6.6a
    for fid in p.fact_ids:
        f = s.facts.get(fid)
        ref = s.details.get(f.subject, {}).get(f.predicate[len(DETAIL):]) if f is not None else None
        if ref is not None and ref.fact_id == fid:
            ref.last_used = _turn_n(ev)


@reducer("game_created")
def _game_created(s: WorldState, ev: Event, p: Any) -> None:
    s.game = GameInfo(seed=p.seed, engine_version=p.engine_version, rules_hash=p.rules_hash,
                      milestone=p.milestone, config=p.config)


@reducer("entity_created")
def _entity_created(s: WorldState, ev: Event, p: Any) -> None:  # rule: 00.6.2
    e = p.entity.model_copy(deep=True)
    if e.introduced_at is None:
        e.introduced_at = ev.game_time
    s.entities[e.id] = e
    if p.quantities:
        s.quantities[e.id] = {k: q.model_copy() for k, q in p.quantities.items()}
    if p.licenses:
        s.licenses[e.id] = [lic.model_copy() for lic in p.licenses]
    gate = p.gate or "unspecified"
    if e.visibility == "sealed":  # rule: 00.6.5
        s.seals[e.id] = Seal(gate=gate, slice=p.slices.get("*"), seq=_seq(ev))
    for f in e.sealed_fields:
        s.seals[f"{e.id}#{f}"] = Seal(gate=gate, slice=p.slices.get(f), seq=_seq(ev))


@reducer("quantity_defined")
def _quantity_defined(s: WorldState, ev: Event, p: Any) -> None:
    s.quantities.setdefault(p.entity, {})[p.quantity] = p.value.model_copy()


@reducer("quantity_changed")
def _quantity_changed(s: WorldState, ev: Event, p: Any) -> None:
    s.quantities[p.entity][p.quantity].current = p.new_value


@reducer("fact_set")
def _fact_set(s: WorldState, ev: Event, p: Any) -> None:  # rule: 00.6.2
    if p.supersedes:
        s.facts.pop(p.supersedes, None)
        s.superseded_facts[p.supersedes] = _seq(ev)
    s.facts[p.fact_id] = FactRecord(
        id=p.fact_id, subject=p.subject, predicate=p.predicate, value=p.value, kind=p.kind, source=p.source,
        certainty=p.certainty, truth=p.truth, visibility=p.visibility, established_at=ev.game_time,
        supersedes=p.supersedes, valid_from_seq=_seq(ev), persistence=p.persistence, pinned=p.pinned)
    s.fact_keys[f"{p.subject}|{p.predicate}"] = p.fact_id
    if p.predicate.startswith(DETAIL):  # rule: 00.6.6a
        slots = s.details.setdefault(p.subject, {})
        slot = p.predicate[len(DETAIL):]
        if p.value is None:  # cleared (a scene detail expiring, 12.4.8 step 8)
            slots.pop(slot, None)
        else:
            slots[slot] = DetailRef(fact_id=p.fact_id, last_used=_turn_n(ev))
    if p.visibility == "sealed":
        s.seals[p.fact_id] = Seal(gate=p.gate or "unspecified", slice=None, seq=_seq(ev))
    if p.supersedes:
        s.seals.pop(p.supersedes, None)


@reducer("relationship_set")
def _relationship_set(s: WorldState, ev: Event, p: Any) -> None:
    s.relationships[f"{p.a}|{p.b}|{p.kind}"] = RelationshipRecord(a=p.a, b=p.b, kind=p.kind, value=p.new_value)


@reducer("position_set")
def _position_set(s: WorldState, ev: Event, p: Any) -> None:
    pos = s.positions.setdefault(p.entity, PositionRecord())
    if p.location is not None:
        pos.location = p.location
    pos.flags = sorted((set(pos.flags) | set(p.flags_add)) - set(p.flags_remove))
    pos.band_to.update(p.band_to)
    for other in p.band_drop:
        pos.band_to.pop(other, None)
    sc, e = s.scene, s.entities.get(p.entity)
    if sc is not None and sc.place_id and e is not None and e.kind in _CAST_KINDS and p.location is not None:
        if p.location == sc.place_id and p.entity not in sc.cast_present:  # 12.4.1: whoever is here is in the scene
            sc.cast_present.append(p.entity)
        elif p.location != sc.place_id and p.entity in sc.cast_present:  # moved away: no longer present
            sc.cast_present.remove(p.entity)


_CAST_KINDS = ("npc", "companion", "adversary")  # as engine.world.places.cast_at


@reducer("knowledge_recorded")
def _knowledge(s: WorldState, ev: Event, p: Any) -> None:
    s.knowledge.setdefault(p.knower, {})[p.fact_id] = KnowledgeEntry(how=p.how, seq=_seq(ev))


@reducer("clock_created")
def _clock_created(s: WorldState, ev: Event, p: Any) -> None:  # rule: 00.8.1
    c = p.clock.model_copy(deep=True)
    if not c.created:
        c.created = {"seq": _seq(ev), "by": ev.rule_id}
    s.clocks[c.id] = c


@reducer("clock_ticked")
def _clock_ticked(s: WorldState, ev: Event, p: Any) -> None:  # rule: PR-00-3
    c = s.clocks[p.clock_id]
    c.filled = p.filled
    c.status = p.status
    c.history.append({"seq": _seq(ev), "delta": p.amount, "source": p.source_ref})
    if p.omen_key:
        stage, _, idx = p.omen_key.partition(":")
        used = c.omens_used.setdefault(stage, [])
        if len(used) >= len(c.omens.get(stage, [])):  # every omen used: start the list again (00.8.4)
            used.clear()
        used.append(int(idx))
    for v in p.voids:
        s.clocks[v].status = "voided"


@reducer("condition_applied")
def _condition_applied(s: WorldState, ev: Event, p: Any) -> None:  # rule: PR-00-5
    inst = p.instance.model_copy(deep=True)
    if inst.applied_at is None:
        inst.applied_at = ev.game_time
    s.conditions[p.instance_id] = inst
    s.applications.append(Application(target=p.target, condition_id=inst.condition_id,
                                      group=p.diminishing_group, seq=_seq(ev)))


@reducer("condition_removed")
def _condition_removed(s: WorldState, ev: Event, p: Any) -> None:
    del s.conditions[p.instance_id]


@reducer("sealed")
def _sealed(s: WorldState, ev: Event, p: Any) -> None:  # rule: 00.6.5
    s.seals[p.ref] = Seal(gate=p.gate, slice=p.slice, seq=_seq(ev))
    ent, _, field = p.ref.partition("#")
    if ent in s.entities:
        e = s.entities[ent]
        if field and field not in e.sealed_fields:
            e.sealed_fields.append(field)
        elif not field:
            e.visibility = "sealed"
    elif p.ref in s.facts:
        s.facts[p.ref].visibility = "sealed"


@reducer("unsealed")
def _unsealed(s: WorldState, ev: Event, p: Any) -> None:  # rule: 00.6.5
    s.seals.pop(p.ref, None)
    ent, _, field = p.ref.partition("#")
    if ent in s.entities:
        e = s.entities[ent]
        if field:
            e.sealed_fields = [f for f in e.sealed_fields if f != field]
        else:
            e.visibility = p.visibility
    elif p.ref in s.facts:
        s.facts[p.ref].visibility = p.visibility


@reducer("frame_committed")
def _frame_committed(s: WorldState, ev: Event, p: Any) -> None:  # rule: 00.13.2
    s.frames[p.frame_id] = FrameState(frame=dict(p.frame), committed_seq=_seq(ev))


@reducer("frame_resolved")
def _frame_resolved(s: WorldState, ev: Event, p: Any) -> None:  # rule: 00.13.2
    s.frames[p.frame_id].resolved = p.model_dump(mode="json", exclude={"frame_id"})


@reducer("offer_logged")
def _offer(s: WorldState, ev: Event, p: Any) -> None:
    _log(s, "offers", ev)


@reducer("evidence_recorded")
def _evidence(s: WorldState, ev: Event, p: Any) -> None:
    _log(s, "evidence", ev)


@reducer("ruling_logged")
def _ruling(s: WorldState, ev: Event, p: Any) -> None:
    _log(s, "rulings", ev)


@reducer("oracle_answered")
def _oracle(s: WorldState, ev: Event, p: Any) -> None:
    _log(s, "oracle", ev)


@reducer("table_rolled")
def _table(s: WorldState, ev: Event, p: Any) -> None:
    _log(s, "tables", ev)
    s.table_recency[p.table_id] = list(p.recency)


@reducer("time_advanced")
def _time(s: WorldState, ev: Event, p: Any) -> None:  # rule: 00.7.1
    s.time.now = p.to
    if p.mode:
        s.time.mode = p.mode


@reducer("boundary_marked")
def _boundary(s: WorldState, ev: Event, p: Any) -> None:
    s.time.last_boundary[p.boundary] = _seq(ev)


@reducer("handler_ran", "handler_skipped")
def _handler(s: WorldState, ev: Event, p: Any) -> None:
    return None  # the log is the record; nothing in the projection changes


@reducer("writes_reverted")
def _reverted(s: WorldState, ev: Event, p: Any) -> None:
    # The skipped events are handled by fold()/project(); here only the record of what was reverted.
    s.reverted = sorted(set(s.reverted) | set(p.reverted))


@reducer("scene_started")
def _scene_started(s: WorldState, ev: Event, p: Any) -> None:  # rule: PR-12-7
    sc = p.scene.model_copy(deep=True)
    sc.started_seq = _seq(ev)
    if sc.started_at is None:
        sc.started_at = ev.game_time
    if sc.place_id:  # 12.4.1: the cast is the framed cast plus everyone already positioned at the place (P-095)
        sc.cast_present += [eid for eid, pos in s.positions.items() if pos.location == sc.place_id
                            and eid not in sc.cast_present and eid in s.entities
                            and s.entities[eid].kind in _CAST_KINDS and s.entities[eid].exists == "exists"]
    s.scene = sc
    s.frames = {}
    s.ledger = {}
    s.applications = []


@reducer("scene_ended")
def _scene_ended(s: WorldState, ev: Event, p: Any) -> None:
    assert s.scene is not None
    s.scene.ended_at = ev.game_time
    s.last_scene = s.scene
    s.scene = None


@reducer("meta_set")
def _meta(s: WorldState, ev: Event, p: Any) -> None:
    s.meta[p.key] = p.value


@reducer("pause_opened")
def _pause_opened(s: WorldState, ev: Event, p: Any) -> None:
    s.pauses.append(p.pause.model_copy(deep=True))


@reducer("pause_closed")
def _pause_closed(s: WorldState, ev: Event, p: Any) -> None:
    s.pauses = [x for x in s.pauses if x.pause_id != p.pause_id]


@reducer("seed_answered")
def _seed(s: WorldState, ev: Event, p: Any) -> None:
    s.seed_answers.append({**p.model_dump(mode="json"), "seq": _seq(ev)})


@reducer("creation_answered")
def _creation(s: WorldState, ev: Event, p: Any) -> None:
    s.creation_answers.append({**p.model_dump(mode="json"), "seq": _seq(ev)})


@reducer("license_granted")
def _grant(s: WorldState, ev: Event, p: Any) -> None:
    held = [x for x in s.licenses.get(p.entity, []) if x.license_id != p.license.license_id]
    s.licenses[p.entity] = held + [p.license.model_copy()]


@reducer("license_revoked")
def _revoke(s: WorldState, ev: Event, p: Any) -> None:
    s.licenses[p.entity] = [x for x in s.licenses.get(p.entity, []) if x.license_id != p.license_id]


def _card(s: WorldState, ev: Event, p: Any) -> None:  # rule: 12.4.8
    """Fold one event into the open scene's card (12.4.8 step 9): a structured view over the scene's events, so a
    rebuild from the log regenerates every card (00.6.9d). Runs after the event's reducer."""
    t = ev.type
    if t == "scene_started":
        sc = s.scene
        assert sc is not None
        card = s.scene_cards.get(sc.scene_id)
        if card is None:
            s.scene_cards[sc.scene_id] = SceneCard(scene=sc.scene_id, place=sc.place_id, agenda=sc.agenda,
                                                   started_at=sc.started_at, started_seq=sc.started_seq,
                                                   cast=list(sc.cast_present))
        else:  # re-opened (12.4.2): the same scene goes on
            card.ended_at = None
        return
    if t == "scene_ended":
        last = s.last_scene
        card = s.scene_cards.get(last.scene_id) if last else None
        if last is not None and card is not None:
            card.ended_at = last.ended_at
            card.cast = list(dict.fromkeys([*card.cast, *last.cast_present]))
        return
    card = s.scene_cards.get(s.scene.scene_id) if s.scene else None
    if card is None:
        return
    if t == "frame_committed":
        beat = p.frame.get("beat") or {}
        card.beats.append({"frame": p.frame_id, "actor": beat.get("actor"), "verb": beat.get("verb"),
                           "target": beat.get("target"), "degree": None})
    elif t == "frame_resolved":
        for b in card.beats:
            if b["frame"] == p.frame_id:
                b["degree"] = p.degree
    elif t == "fact_set":
        if p.value is None or p.predicate.startswith(("trg.", "chronicle.")):
            return
        (card.memories if p.predicate.startswith("memory.") else card.facts).append(p.fact_id)
        if p.subject.startswith("thr.") and p.subject not in card.threads:
            card.threads.append(p.subject)
    elif t == "clock_ticked":
        owner = s.clocks[p.clock_id].owner if p.clock_id in s.clocks else ""
        if owner.startswith("thr.") and owner not in card.threads:
            card.threads.append(owner)
    elif t == "meta_set" and isinstance(p.value, dict) and p.value.get("scene_id") == card.scene:
        if p.key == "scene_agenda":
            card.answer = p.value.get("answered")
        elif p.key == "scene" and isinstance(p.value.get("thread"), str) and p.value["thread"] not in card.threads:
            card.threads.append(p.value["thread"])


_CARD_EVENTS = frozenset({"scene_started", "scene_ended", "frame_committed", "frame_resolved", "fact_set",
                          "clock_ticked", "meta_set"})


def _not_built(s: WorldState, ev: Event, p: Any) -> None:
    family, milestone = NOT_BUILT[ev.type]
    raise NotBuiltYet(f"{ev.type}: the {family} family is built in Milestone {milestone}")


for _t in NOT_BUILT:
    REDUCERS[_t] = _not_built


# ------------------------------------------------------------------------------------------- folding


def _bump_counters(s: WorldState, ev: Event) -> None:
    # A beat id is created by no payload; the events of a beat carry it in the `beat_id` column.
    for v in [*ev.payload.created_ids(), *([ev.beat_id] if ev.beat_id else [])]:
        parsed = ids.parse_counter_id(v)
        if parsed:
            prefix, n = parsed
            if n > s.counters.get(prefix, 0):
                s.counters[prefix] = n


def apply_inplace(s: WorldState, ev: Event, *, skip: bool = False) -> None:
    """Reduce one appended event into `s` (mutates `s`). A reverted event (`skip`) only advances the counters,
    so its ids are never minted again."""
    _bump_counters(s, ev)
    if not skip:
        REDUCERS[ev.type](s, ev, ev.payload)
        if ev.type in _CARD_EVENTS:
            _card(s, ev, ev.payload)
    s.last_seq = _seq(ev)


def apply(state: WorldState, ev: Event) -> WorldState:
    """Pure reducer: the state after `ev`. `state` is not modified."""
    s = state.model_copy(deep=True)
    apply_inplace(s, ev)
    return s


def fold(state: WorldState, events: Iterable[Event], *, skip: Iterable[int] = ()) -> WorldState:
    """Pure: `state` after every event in order, skipping the seqs in `skip` (reverted writes)."""
    s = state.model_copy(deep=True)
    skipped = set(skip)
    for ev in events:
        apply_inplace(s, ev, skip=ev.seq in skipped)
    return s


def reverted_seqs(events: Iterable[Event]) -> set[int]:
    out: set[int] = set()
    for ev in events:
        if isinstance(ev.payload, _WritesReverted):
            out |= set(ev.payload.reverted)
    return out


def project(events: Iterable[Event], start: WorldState | None = None) -> WorldState:
    """The projection of `events` (from `start`, default empty), honouring every writes_reverted among them."""
    evs = list(events)
    return fold(start or WorldState(), evs, skip=reverted_seqs(evs))
