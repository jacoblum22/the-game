"""The scene's slice of state, shared by the packet view and the schema enums (12.2.4 item 3; FR-029, SC-002).

    scope = scene_scope(state)            # the PC, the scene's cast, its place: the ids a call may name
    facts = scene_facts(state)            # narrator-visible current facts about them, newest MAX_SCENE_FACTS

Both are bounded so that a packet (and a schema) does not grow with the length of the game: everything older
lives in state and reaches a call only through these scene-scoped slices.
"""

from __future__ import annotations

from typing import Any

from engine.store.projection import FactRecord, WorldState

MAX_SCENE_OBJECTS = 12  # newest things lying at the scene's place kept in scope (12.2.4: bounded)
MAX_SCENE_FACTS = 40 # newest facts shown per call (the scene's working memory; older ones stay in the store)


def pc_id(state: WorldState) -> str | None:
    """The player character's entity id (the first `pc` entity)."""
    return next((eid for eid, e in state.entities.items() if e.kind == "pc"), None)


def scene_scope(state: WorldState) -> list[str]:  # rule: 12.2.4
    """Entity ids in the current scene: the PC, the cast present, the place and the things lying there. Existing
    entities only."""
    ids: list[str] = []
    pc = pc_id(state)
    if pc:
        ids.append(pc)
    if state.scene is not None:
        ids.extend(state.scene.cast_present)
        if state.scene.place_id:
            ids.append(state.scene.place_id)
            # the things lying here (a notice, a well): what the narration said of them stays in view [P-041]
            here = [eid for eid, p in state.positions.items() if p.location == state.scene.place_id
                    and eid in state.entities and state.entities[eid].kind in ("object", "item")
                    and state.entities[eid].exists == "exists"]
            ids.extend(here[-MAX_SCENE_OBJECTS:])
    return [i for i in dict.fromkeys(ids) if i in state.entities]


def _sealed(state: WorldState, f: FactRecord) -> bool:
    if f.id in state.seals or f.visibility == "sealed":
        return True
    return f.subject in state.seals and not state.seals[f.subject].slice


def scene_facts(state: WorldState, scope: list[str] | None = None,  # rule: 12.2.4
                limit: int = MAX_SCENE_FACTS) -> list[FactRecord]:
    """Narrator-visible current facts about the scope's entities, newest first (at most `limit`).

    Trigger flags (`trg.*` predicates) are engine state, not fiction, and are left out.
    """
    keep = set(scope if scope is not None else scene_scope(state))
    rows = [f for f in state.facts.values()
            if f.subject in keep and not f.predicate.startswith("trg.") and not _sealed(state, f)]
    rows.sort(key=lambda f: (-f.valid_from_seq, f.id))
    return rows[:limit]


def entity_names(state: WorldState, ids: list[str]) -> dict[str, Any]:
    """id -> display name for the ids that exist (sealed entities show their slice or nothing)."""
    out: dict[str, Any] = {}
    for i in ids:
        e = state.entities.get(i)
        if e is None:
            continue
        seal = state.seals.get(i)
        if seal is not None:
            if seal.slice:
                out[i] = seal.slice
            continue
        out[i] = e.name
    return out
