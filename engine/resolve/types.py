"""Shared records of the resolution pipeline's deterministic steps (ch.01; the 00.13.1 frame).

The model roles PROPOSE (`Beat` from the Reader, `ProposedFrame` from the Framer); the engine computes
(`Frame`, `RollResult`, `ReadResult`) or refuses (`FrameRefusal`). Numbers on computed records come only from
code and rules data (INV-3).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Degree = Literal["critical_success", "success", "failure", "critical_failure"]
DEGREES: tuple[Degree, ...] = ("critical_success", "success", "failure", "critical_failure")  # best first
GateClass = Literal["G0", "G1", "G2", "G3", "G4"]
GateMode = Literal["normal", "stretch", "emulate", "fallback"]
StakesRung = Literal["safe", "risky", "dire"]
ReachRung = Literal["limited", "standard", "great"]
LeverType = Literal["precision", "protective", "amplifying"]
Shape = Literal["single", "sequential", "repeated", "bundled", "conditional", "extended"]
Trade = Literal["none", "go_big", "play_it_safe"]
OfferChoice = Literal["commit", "change", "withdraw", "auto"]
Severity = Literal["S1", "S2", "S3", "S4", "S5"]

STAKES_LADDER: tuple[StakesRung, ...] = ("safe", "risky", "dire")
REACH_LADDER: tuple[ReachRung, ...] = ("limited", "standard", "great")
REACH_VALUE: dict[str, int] = {"zero": 0, "limited": 1, "standard": 2, "great": 3, "exceptional": 4}  # 00.3.15


class Change(BaseModel):
    """The beat's typed intended change (01.2.7; `resolution.yaml#intended_change`): one kind and its two slot ids,
    `what` the kind's first data slot (item, place, thing, person, target), `whom` its second (from, to, who)."""

    kind: str = "none"
    what: str | None = None
    whom: str | None = None
    description: str | None = None  # people or things present with no id ("the refugees"; DL-12-97)


class Beat(BaseModel):
    """One beat after PARSE and the Reader's GATE proposal (00.13.1 `beat` + `gate` candidates)."""

    id: str
    actor: str
    intent: str
    method: str
    how: str | None = None  # 01.2.6: the method in the player's own words, verbatim from the message (DL-01-39)
    assertion: str | None = None  # context only, never a fact (INV-9)
    shape: Shape = "single"
    target: str | None = None
    parent_beat: str | None = None
    declared: bool = True
    restatement: str = ""
    # PARSE (12.2.2 decision 3): the verb and three method facets; the gate is computed from them (00.12.3)
    verb: str | None = None
    against_will: bool = False  # acts on a person's body or property against their will
    holds: str | None = None  # a hold folded into this goal's method (01.2.2): applied on a success (06.5.2; spec 022)
    uses_power: bool = False  # needs a supernatural or licensed technique
    speech: bool = False  # mainly words
    pressure: str = "none"  # 12.2.2: a Talk's pressure mark (request, threat, offer, plea, insistence); event tags
    asks: bool = False  # a Talk beat that asks a plain question (a part with a question_kind): R1 (15.3.2)
    license: str | None = None  # engine-set: a stretched or emulated license (01.3.5)
    mode: GateMode = "normal"
    method_class: str | None = None  # the verb's `covers` entry the method falls under, when named
    g4_fact: str | None = None  # the established fact the Reader cites as ruling the method out (G4)
    fallback_license: str | None = None  # an accepted crude fallback: the license whose fallback it is
    traits: list[str] = Field(default_factory=list)
    deed_tag: str | None = None
    necessity: str = "uncertain_and_costly"
    declared_seq: int = 0  # the last event seq before the declaration: levers and snags must be older
    change: Change | None = None  # 01.2.7 (PARSE); None: untyped (a beat from before spec 015)


class LeverCite(BaseModel):
    """A lever or snag citing a fact (00.3.9). A bare fact id reads as a Precision lever."""

    fact_id: str
    type: LeverType = "precision"
    engine: bool = False  # an engine-applied snag (repetition, 01.14.3): outside the two-snag count

    @model_validator(mode="before")
    @classmethod
    def _bare(cls, v: Any) -> Any:
        return {"fact_id": v} if isinstance(v, str) else v


class Delta(BaseModel):
    knob: str
    delta: str
    cites_fact: str | None = None


class Obstacle(BaseModel):
    """FramerOutput.obstacle plus what the engine needs to compute a defense or an effect DC (01.6.4)."""

    kind: Literal["tier", "opposed", "entity_defense", "effect", "stored"] = "tier"
    id: str | None = None  # the obstacle's identity (a stored DC is keyed on it)
    tier: str | None = None  # dc tier id
    entity: str | None = None  # defender, or an effect's source
    entities: list[str] = Field(default_factory=list)  # several aware defenders: the highest defense
    defense: str | None = None  # attribute id (opposed/effect) or a named defense in entity.data.defenses
    defense_tag: str | None = None  # the defender's competence tag, when the anchor lists one
    severity: Severity | None = None  # a hazard's severity (effect DC by tier)
    # the rubric (00.3.8 source 3, 01.6.5): the verb's obstacle class (`other`: `tier` is the model's rung),
    # at most one rung of nudge citing an intrinsic fact, with its why
    obstacle_class: str | None = None
    nudge: int = 0
    nudge_fact: str | None = None
    nudge_why: str | None = None
    request_size: str | None = None  # a social DC's request size, R1..R5 (15.3.2)


class CostDecl(BaseModel):
    menu_id: str
    form_intent: str = ""
    source_fact: str | None = None  # the fact id of the cost's source (01.13.1 candidates)


class ProposedFrame(BaseModel):
    """The Framer's output (contracts/model-calls.md FramerOutput) plus the OFFER trade and engine inputs."""

    anchor: str
    deltas: list[Delta] = Field(default_factory=list)
    attribute: str
    attribute_tie: str | None = None  # a second allowed attribute the method fits equally (01.6.1)
    deed_tag: str | None = None
    traits: list[str] = Field(default_factory=list)
    obstacle: Obstacle = Field(default_factory=Obstacle)
    levers: list[LeverCite] = Field(default_factory=list)
    snags: list[LeverCite] = Field(default_factory=list)
    stakes_source: str = "none"
    stakes_heavy: bool = False
    lethal: bool = False
    reach_limit: str | None = None  # 01.6.10 (DL-12-121): the cited factor that makes reach Limited, in plain words
    reach_two_factors: bool = False  # 01.6.10: two effect factors unoffset, or a total potency: G4 (I-160a)
    already_agreed: str | None = None  # 01.4.1 (DL-01-45): an `agreed` fact that covers this whole ask: no roll
    asks: str = "none"  # social.yaml#event_tags.asks: what a Talk request asks for, or none (12.11.9; I-176)
    threatened_cost: CostDecl | None = None
    alternate_cost: CostDecl | None = None
    method_consequences: list[str] = Field(default_factory=list)
    secret: bool = False
    trade: Trade = "none"
    repetition_instance: int = Field(default=1, ge=1)  # k-th instance in a repetition window (01.14.3)


class FrameRefusal(BaseModel):
    """frame_check's refusal: the PR-01-2 step that failed and why (re-asked once, naming it)."""

    step: int
    field: str
    reason: str

    @property
    def message(self) -> str:
        return f"PR-01-2 step {self.step} ({self.field}): {self.reason}"


class Modifier(BaseModel):
    attribute: int = 0
    competence: int = 0
    competence_tag: str | None = None
    edge: int = 0
    circumstance: int = 0
    status: int = 0
    total: int = 0


class Odds(BaseModel):
    """Exhaustive d20 enumeration under the degree rule (T-01-3); whole percentages."""

    success_or_better: int
    critical_success: int
    success: int
    failure: int
    critical_failure: int
    near_miss: int
    need: int | None  # "N or better on the die"; None when no face succeeds
    only_natural_20: bool


class CostPreview(BaseModel):
    menu_id: str
    form_intent: str = ""
    source_fact: str | None = None
    on_failure: Severity | None = None
    on_critical_failure: Severity | None = None
    on_success_at_cost: Severity | None = None


class GateRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    class_: GateClass = Field(alias="class")
    verb: str | None = None
    license: str | None = None
    mode: GateMode = "normal"


class ModePrice(BaseModel):
    """stretch / emulate / crude fallback price, shown as its own OFFER line (01.3.5)."""

    mode: GateMode
    dc_shift: int = 0
    focus_add: int = 0
    focus_mult: int = 1
    reach_cap: ReachRung | None = None
    consequence: str | None = None
    source: str = ""  # the license id the price is read from


class Alternative(BaseModel):
    """Another approach the engine computed with no model call (12.15.2): same obstacle, another attribute or
    sibling verb."""

    label: str  # plain words: "with Might", "grapple instead"
    verb: str | None = None
    attribute: str
    chance: int  # success-or-better %
    critical_failure: int = 0


class Frame(BaseModel):
    """A computed frame (00.13.1), up to OFFER. `record()` is the `frame_committed` payload."""

    id: str | None = None
    beat: Beat
    gate: GateRecord
    secret: bool = False
    anchor: str
    deltas: list[str] = Field(default_factory=list)
    signature: str = ""
    precedent: str | None = None
    attribute: str
    alternative_attribute: str | None = None  # the higher attribute's method, named in the OFFER (01.6.1)
    deed_tag: str | None = None
    traits: list[str] = Field(default_factory=list)
    obstacle_id: str | None = None
    dc_source: Literal["stored", "opposed", "tier", "effect"]
    tier: str | None = None
    defender: str | None = None
    dc: int
    mode_price: ModePrice | None = None
    levers: list[LeverCite] = Field(default_factory=list)
    snags: list[LeverCite] = Field(default_factory=list)
    stakes: StakesRung
    lethal: bool = False
    reach: ReachRung
    reach_factors: list[str] = Field(default_factory=list)
    reach_limit: str | None = None  # the cited factor a Limited reach names in the OFFER (01.6.10, DL-12-121)
    asks: str = "none"  # the Framer's event tag on a Talk request (social.yaml#event_tags.asks)
    trade: Trade = "none"
    threatened_cost: CostPreview
    alternate_cost: CostPreview | None = None
    method_consequences: list[str] = Field(default_factory=list)
    modifier: Modifier
    odds: Odds
    base_odds: int
    stored_dc_write: dict[str, Any] | None = None  # {subject, predicate, value}: written at commit (01.6.5)
    notes: list[str] = Field(default_factory=list)
    offer_choice: OfferChoice | None = None
    obstacle_class: str | None = None  # the rubric class the tier came from (01.6.5)
    nudge: int = 0
    long_shot: bool = False  # 01.6.13: critical failure above success after the guard
    guard: str | None = None  # what the critical-failure guard changed, when it changed something
    alternatives: list[Alternative] = Field(default_factory=list)  # "Another way" (12.15.2), best first

    def record(self) -> dict[str, Any]:
        return self.model_dump(mode="json", by_alias=True)


class OfferPreview(BaseModel):
    """contracts/engine-api.md OfferView: what 01.7.1 says the OFFER shows, built from the computed frame."""

    restated_beat: str
    approach: dict[str, str | None]  # {verb, attribute, license}
    difficulty_words: str
    dc_source: str
    need: int | None
    odds: dict[str, int]  # success_or_better_pct, critical_success_pct, critical_failure_pct, near_miss_pct
    stakes: StakesRung
    lethal: bool
    threatened_cost: dict[str, str | None]  # {menu_id, form, severity_on_failure, severity_on_critical_failure}
    alternate_cost: dict[str, str | None] | None
    reach: ReachRung
    mode_price: dict[str, Any] | None
    alternative_attribute: str | None
    only_natural_20: bool
    trades: list[str]  # the trades legal now (01.7.3)
    long_shot: bool = False  # 01.6.13


class RollResult(BaseModel):
    frame_id: str | None
    d20: int
    total: int
    margin: int
    base_degree: Degree
    degree: Degree
    near_miss: bool
    rerolled_from: list[int] = Field(default_factory=list)  # faces replaced by an on_roll reroll


class ReadResult(BaseModel):
    """01.9 READ: delivered reach and the one cost due (T-01-4, T-01-5)."""

    degree: Degree
    near_miss: bool
    success_at_cost_taken: bool
    delivered_reach: int
    cost_severity: Severity | None
    cost_choices: list[str] = Field(default_factory=list)  # menu ids the due cost may come from
