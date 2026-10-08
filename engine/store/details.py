"""Established details (00.6.6a): the store half. Functions return events; the caller stages them.

    res = write_detail(tx.state, tx.mint, "npc.samkin", "worn", "iron rings")          # new | same | refused
    res = write_detail(tx.state, tx.mint, "npc.samkin", "worn", "no rings", because="frame.12")  # superseded
    tx.add_all(res.events); res.outcome            # "contradiction" writes nothing: the caller redrafts (12.3.1)
    active_details(state, eid)                     # scene details, then the capped lasting ones (the view's)
    tx.add_all(expire_events(tx.state, tx.mint))   # scene end (12.4.8 step 8; end_scene does it)

A detail is the fact `detail.<slot>`; the projection indexes them (`WorldState.details`: slot -> fact id and
`last_used`). Slots and their persistence are the closed list `pacing.yaml#details.slots`.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from engine import ids
from engine.data.loader import load_rules
from engine.store.events import Event
from engine.store.projection import DETAIL, FactRecord, WorldState

Outcome = Literal["new", "same", "superseded", "contradiction", "refused"]
SEEDED = ("generation", "data")  # a seeded or generated look: salience 2 (00.6.6a item 3)


@dataclass
class DetailWrite:
    outcome: Outcome
    events: list[Event] = field(default_factory=list)
    fact_id: str | None = None  # the written fact (new, superseded) or the stored one (same, contradiction)
    prior: Any = None  # the stored value a contradiction or a supersede met
    reason: str = ""


def slots(rules: Any = None) -> dict[str, str]:  # rule: 00.6.6a
    """slot -> persistence, the person and object lists merged (`pacing.yaml#details.slots`)."""
    rules = rules if rules is not None else load_rules()
    out: dict[str, str] = {}
    for group in rules.pacing["details"]["slots"].values():
        out.update({str(k): str(v) for k, v in group.items()})
    return out


# a stated property's words -> its slot (00.6.6a item 1; spec 009 part B). ponytail: a word list stands in for the
# declaration naming the slot; a property that maps to none is an identity field, consequential or atmosphere
_SLOT_WORDS: dict[str, tuple[str, ...]] = {
    "hair": ("hair", "beard", "braid", "braids", "moustache", "mustache", "bald", "locks"),
    "face": ("face", "eyes", "eye", "skin", "complexion", "nose", "jaw", "teeth", "features"),
    "mark": ("mark", "scar", "scars", "scarred", "tattoo", "brand", "birthmark", "hands"),
    "build": ("build", "height", "frame", "tall", "short", "stout", "broad", "lean", "thin", "heavy", "stature"),
    "clothing": ("clothing", "clothes", "dress", "coat", "cloak", "apron", "tunic", "robe", "robes", "boots",
                 "hat", "hood", "shirt", "jerkin", "garb", "attire"),
    "worn": ("worn", "wears", "jewelry", "jewellery", "ring", "rings", "torc", "necklace", "earring", "brooch",
             "amulet", "pendant", "belt"),
    "voice": ("voice", "accent"),
    "condition_visible": ("soaked", "muddy", "wet", "dusty", "filthy", "bloodstained"),
    "material": ("material", "made", "wood", "wooden", "stone", "iron", "oak", "brass", "leather"),
    "state": ("state", "dented", "faded", "cracked", "weathered", "rusted", "peeling", "condition"),
    "marking": ("marking", "markings", "lettering", "letters", "carving", "carved", "painted", "sign"),
}


def slot_of(predicate: str, rules: Any = None, kind: str | None = None) -> str | None:  # rule: 00.6.6a
    """The detail slot a stated property's predicate names (`detail.hair`, 'hair', 'scarred hands'), or None.
    `kind`: the entity's kind picks the person or the object list (both when None)."""
    p = re.sub(r"^detail\.", "", str(predicate).strip().lower())
    rules = rules if rules is not None else load_rules()
    groups = rules.pacing["details"]["slots"]
    group = None if kind is None else "object" if kind in ("object", "item", "place") else "person"
    known = {str(k) for g, v in groups.items() if group in (None, g) for k in v}
    if p in known:
        return p
    words = re.findall(r"[a-z]+", p)
    return next((s for s, ws in _SLOT_WORDS.items() if s in known and any(w in ws for w in words)), None)


def max_active(rules: Any = None) -> int:
    rules = rules if rules is not None else load_rules()
    return int(rules.pacing["details"]["max_active"])


def _same(a: Any, b: Any) -> bool:
    def norm(v: Any) -> str:
        return re.sub(r"\s+", " ", re.sub(r"^(?:a|an|the)\s+", "", str(v).strip().lower().rstrip(".")))
    return norm(a) == norm(b)


def current(state: WorldState, eid: str, slot: str) -> FactRecord | None:
    ref = state.details.get(eid, {}).get(slot)
    return state.facts.get(ref.fact_id) if ref is not None else None


def write_detail(state: WorldState, mint: Callable[[str], str], eid: str, slot: str, value: Any, *,
                 source: str = "narration", because: str | None = None, rules: Any = None,
                 visibility: str | None = None) -> DetailWrite:  # rule: 00.6.6a
    """One value per slot (00.6.6a item 2): empty -> write; the same value -> no-op; a different value supersedes
    only when `because` names this turn's explaining record entry (a frame, an event), else it is a contradiction
    and nothing is written. Refused: a slot off the closed list, a subject with no id, a `scene`/`beat` slot from
    narration (item 4: code writes those)."""
    persistence = slots(rules).get(slot)
    if persistence is None:
        return DetailWrite("refused", reason=f"{slot!r} is not a detail slot")
    if eid not in state.entities:
        return DetailWrite("refused", reason=f"{eid!r} is not an entity")
    if source == "narration" and persistence != "lasting":
        return DetailWrite("refused", reason=f"{slot} is {persistence} state, written by code only")
    old = current(state, eid, slot)
    if old is not None and _same(old.value, value):
        return DetailWrite("same", fact_id=old.id, prior=old.value)
    if old is not None and not because:
        return DetailWrite("contradiction", fact_id=old.id, prior=old.value,
                           reason=f"{slot} is {old.value!r}; nothing in this turn's record changes it")
    fid = mint(ids.FACT)
    ev = Event.of("fact_set", {"source": source}, source=because or "engine", rule_id="00.6.6a", fact_id=fid,
                  subject=eid, predicate=DETAIL + slot, value=value,
                  certainty="narrated" if source == "narration" else "established",
                  visibility=visibility or ("shown" if source == "narration" else "background"),
                  persistence=persistence, supersedes=old.id if old else None)
    return DetailWrite("superseded" if old else "new", [ev], fid, old.value if old else None)


def _salience(f: FactRecord) -> int:
    return 2 if f.source in SEEDED else 1


def _lasting(state: WorldState, eid: str) -> list[FactRecord]:
    refs = state.details.get(eid, {})
    rows = [(f, r.last_used) for r in refs.values() if (f := state.facts.get(r.fact_id)) is not None
            and f.persistence in (None, "lasting")]
    rows.sort(key=lambda x: (-_salience(x[0]), -x[1], -x[0].valid_from_seq))
    return [f for f, _ in rows]


def active_details(state: WorldState, eid: str, rules: Any = None) -> list[FactRecord]:  # rule: 00.6.6a
    """The entity's details a view may show: its `scene` details (pinned while the scene runs), then at most
    `details.max_active` lasting ones by salience, then last use. `beat` details are never retrieved."""
    scene = [f for r in state.details.get(eid, {}).values()
             if (f := state.facts.get(r.fact_id)) is not None and f.persistence == "scene"]
    return scene + _lasting(state, eid)[:max_active(rules)]


def archived_details(state: WorldState, eid: str, rules: Any = None) -> list[FactRecord]:  # rule: 00.6.6a
    """Lasting details beyond the cap: still current facts (and in the contradiction scope), never in a view."""
    return _lasting(state, eid)[max_active(rules):]


def expire_events(state: WorldState, mint: Callable[[str], str]) -> list[Event]:  # rule: 12.4.8
    """12.4.8 step 8: every current `scene` and `beat` detail is cleared (superseded by a `None` value; the log and
    the fact index keep the history)."""
    out: list[Event] = []
    for eid, refs in state.details.items():
        for slot, r in refs.items():
            f = state.facts.get(r.fact_id)
            if f is None or f.persistence not in ("scene", "beat"):
                continue
            out.append(Event.of("fact_set", {"source": "ruling"}, rule_id="12.4.8", fact_id=mint(ids.FACT),
                                subject=eid, predicate=DETAIL + slot, value=None, persistence=f.persistence,
                                visibility=f.visibility, supersedes=f.id))
    return out


def used_event(fact_ids: list[str]) -> Event:  # rule: 00.6.6a
    """Usage marks (00.6.6a item 5): the delivered sentences stated these details (part B emits it at RECORD)."""
    return Event.of("details_used", rule_id="12.14.11", fact_ids=list(fact_ids))
