"""Casting: the 00.11.1 `cast` domain (`social.yaml#cast`; DL-12-60). "Who is <role>?" and "who would know <topic>?"
are answered with a person who already exists, never one the narration made up.

    npc = cast(state, "smith", scope="loc.merestead")              # an existing NPC id, or None (empty pool)
    kind, ref = pointer_target(state, "roads", scope=..., asker=npc)  # rung 4: ("person"|"place"|"walk_on", id or role)

The pool gate is the store's existing NPCs minus the PC, the anchor bond, anyone sealed and the far powers
(`base_pool`, formerly `incident._people`), then the role (or topic) and the scope. The fill is weighted by fit
(`#cast.fill.weights`) on a stream keyed by the game's seed and the question, so the same question casts the same
person while the pool is unchanged (`#cast.fill.recency`). An empty pool is the caller's: 12.11.1 generation or
"no one you know" (`#cast.empty_pool`).
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any, Literal

from engine.gen import _data
from engine.gen._seed_packs import keyed, pack_data, role_key


def _weights() -> dict[str, float]:
    return dict(_data.load("social.yaml")["cast"]["fill"]["weights"])


def home_of(state: Any, npc: str | None) -> str | None:
    """Where an NPC is found: their position, else their recorded home."""
    if npc is None or npc not in state.entities:
        return None
    pos = state.positions.get(npc)
    return (pos.location if pos else None) or state.entities[npc].data.get("home")


def settlement_of(state: Any, place: str | None) -> str | None:
    """The settlement a place lies in (itself, or the nearest settlement up its parents)."""
    seen: set[str] = set()
    while place and place in state.entities and place not in seen:
        seen.add(place)
        d = state.entities[place].data
        if d.get("place_kind") == "settlement":
            return place
        place = d.get("parent")
    return None


def alive(state: Any, eid: str) -> bool:
    """The entity exists and is not dead, destroyed or departed (its `exists` fact, else its record; harm state)."""
    e = state.entities.get(eid)
    if e is None:
        return False
    return (state.fact_value(eid, "exists") or e.exists) == "exists" \
        and state.fact_value(eid, "harm_state") != "harm_state.dead"


def base_pool(state: Any, pc: str | None) -> list[str]:  # rule: 00.11.1
    """The gate's exclusions (`#cast.pool_gate.excludes`): existing NPCs, not the PC, not the anchor bond (02.9.2),
    nothing sealed, no far power, not dead or departed. Sorted by id."""
    bond = state.fact_value(pc, "bond.anchor") if pc else None
    anchor = bond.get("npc") if isinstance(bond, dict) else None
    return sorted(i for i, e in state.entities.items()
                  if e.kind == "npc" and alive(state, i) and i != anchor and i not in state.seals
                  and not e.data.get("power"))


def _role_matches(state: Any, npc: str, key: str, role: str) -> bool:
    e = state.entities[npc]
    rk = role_key({"role": e.data.get("role")})
    tags = " ".join(str(t) for t in e.data.get("role_tags") or [])
    return (key != "other" and rk == key) or (bool(role) and role.lower() in str(e.data.get("role") or "").lower()) \
        or (key != "other" and key in tags)


def _knows_topic(state: Any, npc: str, topic: str) -> bool:
    e = state.entities[npc]
    rk = role_key({"role": e.data.get("role")})
    pack = e.data.get("knowledge") or []
    return topic in pack_data().CK["by_role"].get(rk, []) or any(k.get("topic") == topic for k in pack)


def cast(state: Any, role: str | None = None, *, scope: str | None, topic: str | None = None, asker: str | None = None,
         exclude: Iterable[str] = (), faction: str | None = None, gate: bool = True) -> str | None:  # rule: 00.11.1
    """One existing NPC for "who is <role>" (`role`) or "who would know <topic>" (`topic`), gated and weighted per
    `social.yaml#cast`; `scope` is a place (its settlement is the scope; None = anywhere). None when the pool is
    empty. The role gate is the role key (`common_knowledge.rule`), role tags, or the role's words in the NPC's
    role; `gate=False` (a story role no case covers: "who is the old enemy") gates nobody out by role, and the fit
    weights decide (the role's words still key the pick)."""
    from engine.store.views import name_known
    from engine.world.common import active_pc

    pc = active_pc(state)
    skip = {asker, *exclude}
    where = settlement_of(state, scope) or scope
    pool = [n for n in base_pool(state, pc) if n not in skip]
    if where is not None:
        near = [n for n in pool if settlement_of(state, home_of(state, n)) == where or home_of(state, n) == where]
        pool = near or pool  # else within reach of where it is asked: the region's people
    role = re.sub(r"^(?:the|a|an)\s+", "", (role or "").strip(), flags=re.I) or None
    key = role_key({"role": role}) if role else "other"
    if topic is not None:
        pool = [n for n in pool if _knows_topic(state, n, topic)]
    elif role and gate:
        pool = [n for n in pool if _role_matches(state, n, key, role)]
    if not pool:
        return None
    w = _weights()
    held = {p["holder"] for c in (state.meta.get("world.cases") or {}).values() for nd in c["nodes"]
            for p in nd["placements"]}
    asker_home = home_of(state, asker) if asker in state.entities else None

    def fit(n: str) -> float:
        d = state.entities[n].data
        x = 1.0
        if (gate and role and _role_matches(state, n, key, role)) or (topic and _knows_topic(state, n, topic)):
            x += w["role_or_topic_match"]
        if asker_home and home_of(state, n) == asker_home:
            x += w["same_place_as_asker"]
        if faction and faction in (d.get("member_of") or []):
            x += w["member_of_the_faction_named"]
        if name_known(state, n):
            x += w["known_to_pc"]
        if n in held and topic is not None:
            x += w["holds_a_case_placement_on_it"]
        return x

    seed = (state.meta.get("world.seed") or {}).get("seed")
    d = keyed(seed, "cast", role or "", topic or "", where or "")
    return d.weighted([(n, fit(n)) for n in pool])


def pointer_target(state: Any, topic: str, *, scope: str | None, asker: str | None = None,
                   exclude: Iterable[str] = ()) -> tuple[Literal["person", "place", "walk_on"], str]:  # rule: PR-12-10
    """Rung 4's "who would know <topic>": a person by casting (never `exclude`); else the topic's `kept_at` place in
    the settlement (`common_knowledge.topics`); else a walk-on to generate there (the role to give them)."""
    who = cast(state, None, scope=scope, topic=topic, asker=asker, exclude=exclude)
    if who is not None:
        return "person", who
    CK = pack_data().CK
    kept = str((CK["topics"].get(topic) or {}).get("kept_at") or "none")
    where = settlement_of(state, scope) or (state.meta.get("world.region") or {}).get("haven")
    pid = f"{where}.{kept}"
    if kept != "none" and pid in state.entities:
        return "place", pid
    role = next((r for r, ts in CK["by_role"].items() if topic in ts), "traveler")
    return "walk_on", role


__all__ = ["base_pool", "cast", "home_of", "pointer_target", "settlement_of"]
