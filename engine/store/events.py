"""Events: the source of truth (data-model.md §2, T011). One Pydantic payload model per event type.

    ev = Event.of("fact_set", source="oracle", rule_id="00.14.2",
                  fact_id="fact.3", subject="npc.tam", predicate="has_sister", value=False)

`Event.of(type, **payload)` (or `Event(type=..., payload={...})`) validates the payload against its model at
construction; an event that fails validation never exists, so it is never appended. Reference checks against
the projection (ids that must exist) happen in `check()` when the store stages the event.
"""

from __future__ import annotations

from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, SerializeAsAny, model_validator

SCHEMA_VER = 1

Visibility = Literal["shown", "available", "background", "sealed"]  # 00.6.4
EntityKind = Literal["pc", "npc", "adversary", "companion", "item", "place", "faction", "thread", "rumor", "clue",
                     "object"]  # 00.6.2
Exists = Literal["exists", "destroyed", "dead", "departed", "unknown"]
Severity = Literal["S1", "S2", "S3", "S4", "S5"]
Stakes = Literal["safe", "risky", "dire"]


class Rejected(ValueError):
    """An event refused by `check()` (a reference to an id that does not exist, an illegal transition)."""


class Timestamp(BaseModel):
    """The 00.7.1 timestamp plus the monotone beat counter. engine/time owns its arithmetic."""  # rule: 00.7.1

    model_config = ConfigDict(frozen=True)
    year: int = 1
    season: int = 1
    week: int = 1
    day: int = 1
    watch: int = 0  # 0 morning, 1 afternoon, 2 evening, 3 night
    hour: int = 0
    interval: int = 0
    round: int = 0
    beat: int = 0


# ------------------------------------------------------------------------------------------- shared records


class Quantity(BaseModel):
    current: int
    min: int = 0
    max: int | None = None
    visibility: Visibility = "shown"


class LicenseInstance(BaseModel):  # 00.6.2 LicenseInstance
    license_id: str
    grade: str = "trained"
    source: str = "creation"
    acquired_at: Timestamp | None = None
    lifecycle: str = "permanent"
    expires: str | None = None


class EntityRecord(BaseModel):
    """00.6.2 Entity. Kind-specific fields (attributes, wants, archetype, ...) go in `data`."""  # rule: 00.6.2

    id: str
    kind: EntityKind
    name: str
    tags: list[str] = Field(default_factory=list)
    exists: Exists = "exists"
    introduced_at: Timestamp | None = None
    visibility: Visibility = "shown"
    sealed_fields: list[str] = Field(default_factory=list)  # keys of `data` withheld from the narrator
    data: dict[str, Any] = Field(default_factory=dict)


class ConditionInstance(BaseModel):
    """00.9.1 ConditionInstance, plus the exclusion fields copied from the definition at application."""

    instance_id: str
    condition_id: str
    target: str
    severity: Severity
    stacks: int = 1
    remaining: str  # a duration expression (substrate.yaml#duration_forms)
    source: dict[str, Any] = Field(default_factory=dict)  # {entity, effect_id, frame_id}
    applied_at: Timestamp | None = None
    exclusion_group: str | None = None
    priority_rank: int = 0


class ClockRecord(BaseModel):
    """00.8.1 Clock (an instance). `omens_used` tracks the next unused omen per stage (00.8.4)."""

    id: str
    name: str
    kind: Literal["danger", "progress", "countdown", "faction_goal", "project", "tug"]
    owner: str = ""
    segments: int
    filled: int = 0
    visibility: Literal["public", "sensed", "hidden"] = "public"
    direction: Literal["fill", "tug"] = "fill"
    tick_sources: list[dict[str, Any]] = Field(default_factory=list)
    auto_ticks: list[dict[str, Any]] = Field(default_factory=list)
    decay: list[dict[str, Any]] = Field(default_factory=list)
    omens: dict[str, list[str]] = Field(default_factory=dict)
    on_complete: dict[str, Any] = Field(default_factory=dict)
    races_with: str | None = None
    links: list[dict[str, Any]] = Field(default_factory=list)
    status: Literal["active", "completed", "voided", "paused"] = "active"
    created: dict[str, Any] = Field(default_factory=dict)
    history: list[dict[str, Any]] = Field(default_factory=list)
    omens_used: dict[str, list[int]] = Field(default_factory=dict)
    lethal: bool = False  # completion would expose the PC to lethal harm (PR-00-3 step 3)


class SceneRecord(BaseModel):
    """data-model.md §4 Scene (PR-12-7 scene record)."""

    scene_id: str
    place_id: str | None = None
    mode: str = "free"
    agenda: str = ""
    hoped_answer: str = ""
    pillar: str | None = None
    challenge_type: str | None = None
    cast_present: list[str] = Field(default_factory=list)
    situation_tags: list[str] = Field(default_factory=list)
    question_answered: bool = False
    started_at: Timestamp | None = None
    ended_at: Timestamp | None = None
    started_seq: int = 0


class PauseRecord(BaseModel):
    """A pause shown to the player (contracts/engine-api.md Pause)."""

    pause_id: str
    kind: Literal["seed_step", "create_step", "offer", "clarify", "redirect", "near_miss", "last_chance",
                  "yield_terms", "ending", "budget"]
    prompt: str = ""
    frame_id: str | None = None
    choices: list[dict[str, str]] = Field(default_factory=list)  # [{id, label}]
    default_choice: str | None = None
    detail: dict[str, Any] = Field(default_factory=dict)  # e.g. the OfferView, the seed step id


# ------------------------------------------------------------------------------------------- payloads


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # fields that hold ids this event CREATES (they advance the projection's id counters)
    creates: ClassVar[tuple[str, ...]] = ()
    # fields that hold entity ids that must already exist (or be created earlier in the same transaction)
    entity_refs: ClassVar[tuple[str, ...]] = ()

    def check(self, state: Any) -> None:
        """Reference checks against the working projection (data-model.md §5). Raise `Rejected`."""
        for f in self.entity_refs:
            v = getattr(self, f)
            for i in v if isinstance(v, list) else [v]:
                if i is not None and i not in state.entities and i != WORLD:
                    raise Rejected(f"{type(self).__name__}.{f}: unknown entity {i!r}")


WORLD = "world"  # the subject of facts about the world at large (no entity)


class EntityCreated(Payload):
    entity: EntityRecord
    quantities: dict[str, Quantity] = Field(default_factory=dict)
    licenses: list[LicenseInstance] = Field(default_factory=list)
    slices: dict[str, str] = Field(default_factory=dict)  # permitted slice per sealed field ("*" = the entity)
    gate: str | None = None  # what unseals the sealed parts (00.6.5)

    def check(self, state: Any) -> None:
        if self.entity.id in state.entities:
            raise Rejected(f"entity {self.entity.id} already exists")


class FactSet(Payload):  # rule: 00.6.2
    creates = ("fact_id",)
    entity_refs = ("subject",)
    fact_id: str
    subject: str
    predicate: str
    value: Any
    kind: Literal["fact", "flag", "commitment"] = "fact"
    source: Literal["narration", "oracle", "generation", "ruling", "data", "player_accepted"]
    certainty: Literal["established", "rumored", "believed"] = "established"
    truth: Literal["true", "partial", "false", "outdated"] = "true"  # sealed (00.6.2)
    visibility: Visibility = "background"
    supersedes: str | None = None
    gate: str | None = None  # what unseals it, when visibility is sealed (00.6.5)

    def check(self, state: Any) -> None:
        super().check(state)
        if self.fact_id in state.facts:
            raise Rejected(f"fact {self.fact_id} already exists")
        cur = state.current_fact_id(self.subject, self.predicate)
        if cur != self.supersedes:
            raise Rejected(f"fact_set {self.subject}.{self.predicate}: supersedes {self.supersedes!r}, current {cur!r}")


class QuantityChanged(Payload):
    entity_refs = ("entity",)
    entity: str
    quantity: str
    delta: int
    new_value: int
    clamped: bool = False
    reason: str
    frame_id: str | None = None

    def check(self, state: Any) -> None:
        super().check(state)
        q = state.quantities.get(self.entity, {}).get(self.quantity)
        if q is None:
            raise Rejected(f"{self.entity} has no quantity {self.quantity}")
        if self.new_value < q.min or (q.max is not None and self.new_value > q.max):
            raise Rejected(f"{self.entity}.{self.quantity} = {self.new_value} outside {q.min}..{q.max}")


class QuantityDefined(Payload):
    """A new quantity on an existing entity (or a new max); values come from rules data (INV-3)."""

    entity_refs = ("entity",)
    entity: str
    quantity: str
    value: Quantity
    reason: str


class RelationshipSet(Payload):
    entity_refs = ("a", "b")
    a: str
    b: str
    kind: str
    value: int | None = None
    steps: int | None = None
    new_value: int
    reason: str


class PositionSet(Payload):
    entity_refs = ("entity",)
    entity: str
    location: str | None = None
    flags_add: list[str] = Field(default_factory=list)
    flags_remove: list[str] = Field(default_factory=list)
    band_to: dict[str, str] = Field(default_factory=dict)


class KnowledgeRecorded(Payload):
    entity_refs = ("knower",)
    knower: str
    fact_id: str
    how: Literal["witnessed", "told", "read", "overheard", "recalled", "inferred", "rumor", "confided"]  # 15.9.17

    def check(self, state: Any) -> None:
        super().check(state)
        if self.fact_id not in state.facts and self.fact_id not in state.superseded_facts:
            raise Rejected(f"knowledge of unknown fact {self.fact_id}")


class ClockCreated(Payload):
    clock: ClockRecord

    def check(self, state: Any) -> None:
        if self.clock.id in state.clocks:
            raise Rejected(f"clock {self.clock.id} already exists")


class ClockTicked(Payload):  # rule: PR-00-3
    clock_id: str
    source_ref: str
    amount: int
    filled: int  # after the tick (and after `then` on completion)
    stage: Literal["stirring", "building", "imminent"] | None = None
    omen_key: str | None = None  # "<stage>:<index>"
    completed: bool = False
    status: Literal["active", "completed", "voided", "paused"] = "active"
    voids: list[str] = Field(default_factory=list)  # racing clocks voided by this completion (00.8.5)

    def check(self, state: Any) -> None:
        c = state.clocks.get(self.clock_id)
        if c is None:
            raise Rejected(f"unknown clock {self.clock_id}")
        if c.status != "active":
            raise Rejected(f"clock {self.clock_id} is {c.status}")
        for v in self.voids:
            if v not in state.clocks:
                raise Rejected(f"voids unknown clock {v}")


class ConditionApplied(Payload):  # rule: PR-00-5
    creates = ("instance_id",)
    entity_refs = ("target",)
    instance_id: str
    target: str
    instance: ConditionInstance
    outcome: Literal["applied", "refreshed", "replaced", "intensified", "escalated", "added"] = "applied"
    diminishing_group: str | None = None  # counted for diminishing returns (00.9.3e)

    def check(self, state: Any) -> None:
        super().check(state)
        if self.instance.instance_id != self.instance_id or self.instance.target != self.target:
            raise Rejected("condition_applied: instance id/target mismatch")


class ConditionRemoved(Payload):
    instance_id: str
    reason: str

    def check(self, state: Any) -> None:
        if self.instance_id not in state.conditions:
            raise Rejected(f"no condition instance {self.instance_id}")


class Sealed(Payload):  # rule: 00.6.5
    ref: str  # "<entity>", "<entity>#<field>", "<fact_id>", "<clock_id>"
    gate: str
    slice: str | None = None  # the permitted slice the narrator gets instead

    def check(self, state: Any) -> None:
        if not state.sealable(self.ref):
            raise Rejected(f"cannot seal {self.ref!r}: not an entity, entity#field or fact")
        if self.ref in state.seals:
            raise Rejected(f"{self.ref} is already sealed")


class Unsealed(Payload):  # rule: 00.6.5
    ref: str
    via: str
    visibility: Visibility = "available"  # the item's visibility once unsealed

    def check(self, state: Any) -> None:
        if self.ref not in state.seals:
            raise Rejected(f"{self.ref} is not sealed")


class FrameCommitted(Payload):  # rule: 00.13.2
    creates = ("frame_id",)
    frame_id: str
    frame: dict[str, Any]  # the 00.13.1 frame up to OFFER; immutable afterwards

    def check(self, state: Any) -> None:
        if self.frame_id in state.frames:
            raise Rejected(f"frame {self.frame_id} already committed (immutable, 00.13.2)")


class FrameResolved(Payload):  # rule: 00.13.2
    frame_id: str
    roll: dict[str, int] | None = None  # {d20, total, margin}
    degree: Literal["critical_success", "success", "failure", "critical_failure"] | None = None
    near_miss: bool = False
    success_at_cost_taken: bool = False
    delivered: dict[str, Any] = Field(default_factory=dict)  # {reach, units, items}
    costs: list[dict[str, Any]] = Field(default_factory=list)  # [{menu_id, severity, form}]
    method_consequences: list[str] = Field(default_factory=list)
    state_writes: list[int] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    ruling: str | None = None

    def check(self, state: Any) -> None:
        f = state.frames.get(self.frame_id)
        if f is None:
            raise Rejected(f"frame {self.frame_id} was never committed")
        if f.resolved is not None:
            raise Rejected(f"frame {self.frame_id} already resolved")


class OfferLogged(Payload):
    frame_id: str | None = None
    shown_at: Timestamp | None = None
    choice: Literal["commit", "change", "withdraw", "trade", "auto"]


class EvidenceRecorded(Payload):
    """00.6.8 EvidenceEvent. Tallies are settled from Milestone 3."""

    creates = ("id",)
    entity_refs = ("actor",)
    id: str
    actor: str
    time: Timestamp | None = None
    deed: str
    tags: list[str]
    conduct_sign: dict[str, int] = Field(default_factory=dict)
    kind: Literal["judged", "counted"] = "judged"
    frame_id: str | None = None
    degree: str | None = None
    challenge_band: int = Field(ge=1, le=5)
    stakes: Stakes
    lethal_context: bool = False
    witnesses: list[str] = Field(default_factory=list)
    scope: str | None = None


class RulingLogged(Payload):
    """00.15.5 RulingRecord in `ruling`; `signature` and `id` are required for the precedent index."""

    ruling: dict[str, Any]

    @model_validator(mode="after")
    def _keys(self) -> RulingLogged:
        for k in ("id", "signature"):
            if not isinstance(self.ruling.get(k), str):
                raise ValueError(f"ruling needs a string {k!r}")
        return self


class OracleAnswered(Payload):
    question: str
    odds: str
    d100: int = Field(ge=1, le=100)
    answer: Literal["yes", "no"]
    extreme: bool = False
    twist: bool = False
    fact_id: str | None = None

    def check(self, state: Any) -> None:
        if self.fact_id is not None and self.fact_id not in state.facts:
            raise Rejected(f"oracle answer cites unknown fact {self.fact_id} (append its fact_set first)")


class TableRolled(Payload):
    table_id: str
    context: dict[str, Any] = Field(default_factory=dict)
    roll: int | None = None
    entry: Any
    recency: list[str] = Field(default_factory=list)  # the table's recent entries after this roll


class TimeAdvanced(Payload):
    from_: Timestamp = Field(alias="from")
    to: Timestamp
    boundaries: list[str] = Field(default_factory=list)
    interrupt: str | None = None
    remainder: dict[str, int] | None = None
    mode: str | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class BoundaryMarked(Payload):
    boundary: str
    payload: dict[str, Any] = Field(default_factory=dict)


class HandlerRan(Payload):
    handler_id: str
    boundary: str
    phase: int
    result: str = ""


class HandlerSkipped(Payload):
    handler_id: str
    boundary: str
    phase: int
    reason: str = "not yet built"
    milestone: int | None = None


class WritesReverted(Payload):
    reverted: list[int]
    compensating: dict[str, Any] = Field(default_factory=dict)  # informational: the values restored
    reason: str


class SceneStarted(Payload):
    creates = ("scene_id",)
    scene_id: str
    scene: SceneRecord

    def check(self, state: Any) -> None:
        if self.scene.scene_id != self.scene_id:
            raise Rejected("scene_started: scene_id differs from the scene record's")
        if state.scene is not None:
            raise Rejected(f"scene {state.scene.scene_id} has not ended")
        if self.scene.place_id is not None and self.scene.place_id not in state.entities:
            raise Rejected(f"scene place {self.scene.place_id} is not an entity")


class SceneEnded(Payload):
    scene_id: str
    reason: str

    def check(self, state: Any) -> None:
        if state.scene is None or state.scene.scene_id != self.scene_id:
            raise Rejected(f"scene {self.scene_id} is not the current scene")


class MetaSet(Payload):
    key: str
    value: Any


class PauseOpened(Payload):
    creates = ("pause_id",)
    pause: PauseRecord
    pause_id: str = ""

    @model_validator(mode="after")
    def _id(self) -> PauseOpened:
        self.pause_id = self.pause.pause_id
        return self


class PauseClosed(Payload):
    pause_id: str
    choice: str | None = None
    by: Literal["option", "own_words", "default", "withdrawn"] = "option"
    words: str | None = None

    def check(self, state: Any) -> None:
        if not any(p.pause_id == self.pause_id for p in state.pauses):
            raise Rejected(f"pause {self.pause_id} is not open")


class SeedAnswered(Payload):
    step: str
    choice: Any
    source: Literal["player_option", "player_words", "oracle_roll", "default"]
    words: str | None = None


class CreationAnswered(Payload):
    block: str
    choice: Any
    source: Literal["player_option", "player_words", "oracle_roll", "default"]
    words: str | None = None


class GameCreated(Payload):  # FR-040
    seed: int
    engine_version: str
    rules_hash: str
    milestone: int
    config: dict[str, Any] = Field(default_factory=dict)

    def check(self, state: Any) -> None:
        if state.game is not None:
            raise Rejected("game_created twice")


class LicenseGranted(Payload):
    """00.14.2 #28 `grant` (not in data-model.md §2's table; the license family needs a write path)."""

    entity_refs = ("entity",)
    entity: str
    license: LicenseInstance


class LicenseRevoked(Payload):
    entity_refs = ("entity",)
    entity: str
    license_id: str
    reason: str


class NotBuilt(Payload):
    """Families filled in later milestones (data-model.md §3): their events are reserved and refused."""

    model_config = ConfigDict(extra="allow")


PAYLOADS: dict[str, type[Payload]] = {
    "entity_created": EntityCreated,
    "fact_set": FactSet,
    "quantity_changed": QuantityChanged,
    "quantity_defined": QuantityDefined,
    "relationship_set": RelationshipSet,
    "position_set": PositionSet,
    "knowledge_recorded": KnowledgeRecorded,
    "clock_created": ClockCreated,
    "clock_ticked": ClockTicked,
    "condition_applied": ConditionApplied,
    "condition_removed": ConditionRemoved,
    "sealed": Sealed,
    "unsealed": Unsealed,
    "frame_committed": FrameCommitted,
    "frame_resolved": FrameResolved,
    "offer_logged": OfferLogged,
    "evidence_recorded": EvidenceRecorded,
    "ruling_logged": RulingLogged,
    "oracle_answered": OracleAnswered,
    "table_rolled": TableRolled,
    "time_advanced": TimeAdvanced,
    "boundary_marked": BoundaryMarked,
    "handler_ran": HandlerRan,
    "handler_skipped": HandlerSkipped,
    "writes_reverted": WritesReverted,
    "scene_started": SceneStarted,
    "scene_ended": SceneEnded,
    "meta_set": MetaSet,
    "pause_opened": PauseOpened,
    "pause_closed": PauseClosed,
    "seed_answered": SeedAnswered,
    "creation_answered": CreationAnswered,
    "game_created": GameCreated,
    "license_granted": LicenseGranted,
    "license_revoked": LicenseRevoked,
}

# Reserved for later milestones; the reducers raise NotBuiltYet (data-model.md §3).
NOT_BUILT: dict[str, tuple[str, int]] = {
    "tally_settled": ("tally", 3),
    "effect_applied": ("effect_instance", 2),
    "effect_expired": ("effect_instance", 2),
    "offer_created": ("offer", 3),
    "offer_resolved": ("offer", 3),
}
for _t in NOT_BUILT:
    PAYLOADS[_t] = NotBuilt

EventType = str


class Event(BaseModel):
    """One row of `events` (data-model.md §1). `seq` is None until the store appends it."""

    model_config = ConfigDict(frozen=True)

    seq: int | None = None
    branch_id: str = "main"
    turn_id: str | None = None
    beat_id: str | None = None
    game_time: Timestamp | None = None  # stamped from the projection when left None
    type: EventType
    payload: SerializeAsAny[Payload]
    source: str = "engine"  # frame id, handler id, oracle id, mention, player
    rule_id: str | None = None
    schema_ver: int = SCHEMA_VER

    @model_validator(mode="before")
    @classmethod
    def _payload(cls, data: Any) -> Any:
        if isinstance(data, dict):
            t = data.get("type")
            model = PAYLOADS.get(t) if isinstance(t, str) else None
            if model is None:
                raise ValueError(f"unknown event type {t!r}")
            p = data.get("payload")
            if not isinstance(p, model):
                p = model.model_validate(p.model_dump(by_alias=True) if isinstance(p, BaseModel) else (p or {}))
            data = {**data, "payload": p}
        return data

    @classmethod
    def of(cls, type: EventType, payload: dict[str, Any] | None = None, /, *, source: str = "engine",  # noqa: A002
           rule_id: str | None = None, turn_id: str | None = None, beat_id: str | None = None,
           **fields: Any) -> Event:
        """Build and validate an event. Payload fields go in `fields`; a payload field whose name is also an
        event column (`source` of fact_set, seed_answered, creation_answered) goes in the `payload` dict."""
        return cls(type=type, payload={**(payload or {}), **fields}, source=source,  # type: ignore[arg-type]
                   rule_id=rule_id, turn_id=turn_id, beat_id=beat_id)

    def payload_json(self) -> dict[str, Any]:
        return self.payload.model_dump(mode="json", by_alias=True)
