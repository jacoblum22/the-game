"""The adjudication record: what T1–T6 produced, and all that T7–T10 may narrate from (PR-12-1; 12.3.3).

The turn loop fills it as the turn runs; the Narrator's packet carries it (contracts/model-calls.md B), the claim
check reads it for sources (12.3.2: a change needs a write this turn; an act needs a source in this record), and
the plain fallback (12.3.3) is built from it alone. Everything here is plain words and ids, JSON-serializable.

    rec = AdjudicationRecord(turn_id="turn.3", pc="pc.wren")
    rec.parts.append(PartEntry(text="I pick the lock.", cls="DECLARATION"))
    rec.beats.append(BeatEntry(restatement="Wren picks the archive lock", degree="success", ...))
    rec.add_writes(events)                       # appended events (seq set); entities touched are derived
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from engine.store.events import Event

NpcSource = Literal["talk_outcome", "want", "refusal", "table_row", "behavior", "clock", "trigger", "ally_reason",
                    "frame"]  # 12.2.9's closed sources (+ an ally's 16.13.3 reasons, + a resolved frame)


class PartEntry(BaseModel):
    """One part of the player's message (12.2.2) and how this turn answered it (12.2.7 acknowledged)."""

    model_config = ConfigDict(populate_by_name=True)

    text: str
    cls: str = Field(alias="class")  # SAFETY|SESSION|DISPUTE|PENDING_ANSWER|OOF_QUESTION|FICTION_QUESTION|...
    handled: str = ""  # resolved | queued | paused | redirected | answered | refused (01.2.3)
    question_kind: str = "none"  # 12.2.2 (DL-12-50); read by the answer ladder (spec 008)
    topic: str | None = None
    beat_id: str | None = None


class CostEntry(BaseModel):
    menu_id: str
    severity: str | None = None
    form: str = ""  # the chosen form, in words ("your footing goes: you slide to one knee")


class HarmEntry(BaseModel):
    target: str
    words: str  # in fiction words (T-12-10): "bloodied", "staggered", "a deep cut on the arm"
    condition_ids: list[str] = Field(default_factory=list)


class PositionEntry(BaseModel):
    entity: str
    words: str  # "at the far door", "behind the cart"


class BeatEntry(BaseModel):
    """One resolved (or redirected, or paused) beat: its frame summary and what it delivered."""

    beat_id: str | None = None
    frame_id: str | None = None
    part: int | None = None  # index into `parts`
    actor: str | None = None
    targets: list[str] = Field(default_factory=list)  # entity ids the beat acts on
    verb: str | None = None  # the Reader's basic verb id ("verb.force"): the plain fallback's beat line (B P4)
    restatement: str  # the neutral restatement (01.2.6)
    gate: str | None = None  # gate result id or words (G0..G4, "no roll: necessity")
    gate_words: str = ""  # a redirect's or refusal's words
    approach_words: str = ""  # "force, with the iron bar"
    difficulty_words: str = ""  # tier name in words ("hard")
    stakes: str | None = None
    rolled: bool = False
    degree: str | None = None  # critical_success | success | failure | critical_failure | None (no roll)
    near_miss: bool = False
    success_at_cost: bool = False
    reach: str | None = None  # delivered reach id (limited | standard | ...)
    reach_words: list[str] = Field(default_factory=list)  # what was delivered, in words
    costs: list[CostEntry] = Field(default_factory=list)
    harm: list[HarmEntry] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)  # visible conditions applied, in words
    positions: list[PositionEntry] = Field(default_factory=list)
    license: str | None = None  # the licence or ability used, if any
    learned: list[str] = Field(default_factory=list)  # what a successful learning beat delivered, in words (12.10.5)
    progress: str = ""  # an extended goal's progress clock, in words (01.14.6; P-082)
    # 01.2.7: the typed intended change (kind; its plain words), what RECORD applied, or why it could not
    change_kind: str | None = None  # None: untyped (T-12-18 reads the verb alone)
    change: str = ""  # "take the coin purse from Murzak Red-Hand"
    changed: str = ""  # "you have the coin purse" (applied, at the delivered reach)
    change_refused: str = ""  # "the coin purse is not on Feney" (not applied; the RESULT says it)


class OracleEntry(BaseModel):
    question: str
    answer: str  # "yes" | "no" | "yes, but ..." in words
    fact_id: str | None = None
    subject: str | None = None
    predicate: str | None = None


class NpcActionEntry(BaseModel):
    """An NPC's (or foe's, or ally's) act this turn and its closed source (12.2.9)."""

    npc: str
    action: str  # in words: "steps aside and lets you pass"
    source: NpcSource
    source_ref: str | None = None  # frame id, want id, table id + row, clock id, trigger id
    tags: list[str] = Field(default_factory=list)


class ActivityEntry(BaseModel):
    """A present person's scene state (T1c, 12.11.9 step 1; T-12-18): their activity, or with `slot` their posture,
    hold, manner or range band to the PC. Citable, not owed."""

    npc: str
    activity: str  # the slot's value
    slot: str = "activity"  # activity | posture | held | manner | position
    hidden: str = ""  # why the narration is not shown it this turn: "stale" (12.14.11) | "engaged" (12.11.9)


class OmenEntry(BaseModel):
    clock_id: str
    stage: str | None = None
    omen: str = ""  # the omen the engine selected (00.8.4)
    completed: bool = False
    ticked: bool = True


class SceneEntry(BaseModel):
    cut: bool = False
    ended: str | None = None  # scene id
    started: str | None = None  # scene id
    header: str = ""  # the new scene's header line, in words (place, time)


class WriteRef(BaseModel):
    """One event written this turn and what it touched (the claim check's "a write this turn backs it")."""

    seq: int
    type: str
    entities: list[str] = Field(default_factory=list)
    key: str | None = None  # quantity name, fact predicate, condition id, relationship kind, clock id

    @classmethod
    def of(cls, ev: Event) -> WriteRef:
        assert ev.seq is not None, "WriteRef.of needs an appended event"
        p = ev.payload
        ents: list[str] = []
        for f in ("entity", "subject", "target", "knower", "a", "b"):
            v = getattr(p, f, None)
            vid = getattr(v, "id", None)  # entity_created's EntityRecord
            if isinstance(v, str):
                ents.append(v)
            elif isinstance(vid, str):
                ents.append(vid)
        key = None
        for f in ("quantity", "predicate", "kind", "clock_id"):
            v = getattr(p, f, None)
            if isinstance(v, str):
                key = v
                break
        if ev.type == "time_advanced":
            key = " ".join(p.boundaries)  # type: ignore[attr-defined]  # what passed: "beat_end", "interval", ...
        inst = getattr(p, "instance", None)
        if inst is not None and getattr(inst, "condition_id", None):
            key = inst.condition_id
            ents.append(inst.target)
        if ev.type == "condition_removed":
            key = key or p.instance_id  # type: ignore[attr-defined]
        if ev.type == "position_set" and getattr(p, "location", None):
            ents.append(p.location)  # type: ignore[attr-defined]
        return cls(seq=ev.seq, type=ev.type, entities=list(dict.fromkeys(ents)), key=key)


class PauseEntry(BaseModel):
    kind: str
    frame_id: str | None = None
    prompt: str = ""
    options: list[str] = Field(default_factory=list)


class AdjudicationRecord(BaseModel):
    """What T1–T6 produced this turn. Generic and serializable: the turn loop fills it."""

    turn_id: str | None = None
    pc: str | None = None
    parts: list[PartEntry] = Field(default_factory=list)
    beats: list[BeatEntry] = Field(default_factory=list)
    oracle: list[OracleEntry] = Field(default_factory=list)
    npc_actions: list[NpcActionEntry] = Field(default_factory=list)
    activities: list[ActivityEntry] = Field(default_factory=list)  # 12.11.9 step 1 (spec 006)
    omens: list[OmenEntry] = Field(default_factory=list)
    scene: SceneEntry = Field(default_factory=SceneEntry)
    writes: list[WriteRef] = Field(default_factory=list)
    triggers: list[str] = Field(default_factory=list)  # active trigger ids this turn (owed blocks, 12.3.2)
    pause: PauseEntry | None = None
    notes: list[str] = Field(default_factory=list)  # anything else the narration must carry, in words
    player_quantity: int | None = None  # the Reader's typed number (01.1.4): a deal's stated amount (15.7.1)

    def add_writes(self, events: Iterable[Event]) -> None:
        """Record appended events as this turn's writes (skips ones already recorded)."""
        have = {w.seq for w in self.writes}
        for ev in events:
            if ev.seq is not None and ev.seq not in have:
                self.writes.append(WriteRef.of(ev))
                have.add(ev.seq)

    @property
    def write_seqs(self) -> list[int]:
        return [w.seq for w in self.writes]

    def touched(self) -> set[str]:
        """Every entity id a write this turn touched."""
        return {e for w in self.writes for e in w.entities}

    def writes_for(self, entity: str, *types: str) -> list[WriteRef]:
        return [w for w in self.writes if entity in w.entities and (not types or w.type in types)]

    def dump(self) -> dict[str, Any]:
        return self.model_dump(mode="json", by_alias=True)


def undecided(b: BeatEntry, pause: Any = None) -> bool:  # rule: 01.9.3
    """The beat waits on the near-miss choice (01.9.3): its recorded degree is `failure`, but whether it lands is
    the player's pick, so neither result may be narrated yet (12.2.6; DL-12-115)."""
    return bool(b.near_miss and not b.success_at_cost and pause is not None
                and getattr(pause, "kind", None) == "near_miss" and getattr(pause, "frame_id", None) == b.frame_id)


def effective_degree(b: BeatEntry, pause: Any = None) -> str | None:  # rule: 01.9.3
    """DL-01-48: the one outcome every reader uses. A success at a cost taken is `success`; a beat waiting on its
    near-miss choice (`pause`, the turn's open pause) has none yet; else the rolled degree (None: no roll)."""
    if undecided(b, pause):
        return None
    return "success" if b.success_at_cost else b.degree


def paused_beat(record: AdjudicationRecord, n: int) -> bool:  # rule: 12.2.6
    """Beat `n` is the one the open pause holds before its outcome (an OFFER, a redirect, a warning, a near-miss
    choice): unresolved in the narrator's record, no result words and not owed (DL-12-115)."""
    if record.pause is None or n != len(record.beats) - 1:
        return False
    b = record.beats[n]
    return (b.degree is None and not b.gate_words.startswith("no roll")) or undecided(b, record.pause)
