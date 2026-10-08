"""The scene's slice of state, shared by the packet view and the schema enums (12.2.4 item 3; FR-029, SC-002).

    scope = scene_scope(state)            # the PC, the scene's cast, its place: the ids a call may name
    facts = scene_facts(state)            # narrator-visible current facts about them, newest MAX_SCENE_FACTS

Both are bounded so that a packet (and a schema) does not grow with the length of the game: everything older
lives in state and reaches a call only through these scene-scoped slices.
"""

from __future__ import annotations

import re
from typing import Any

from engine.store.projection import FactRecord, WorldState
from engine.store.views import display_name

MAX_SCENE_OBJECTS = 12  # newest things lying at the scene's place kept in scope (12.2.4: bounded)
MAX_SCENE_FACTS = 40 # newest facts shown per call (the scene's working memory; older ones stay in the store)
READING = re.compile(r"\b(read|reads|reading|wording|inscription|lettering|what (?:does|do|did) (?:it|the \w+|they) "
                     r"say|what it says|what's written|what is written)\b", re.I)  # the player reads something
WRITTEN = ("text", "inscription", "reads", "words", "says", "wording", "writing")  # a thing's written words (P-110)


def written_words(state: WorldState, eid: str) -> Any:
    """The words written on a thing, as stored (its `text` fact or a synonym), else None."""
    return next((v for k in WRITTEN if (v := state.fact_value(eid, k)) is not None), None)


def cannot_read(state: WorldState, pc: str | None, eid: str | None) -> str:  # rule: 02.4.6
    """Why the PC cannot read what is written on `eid` (plain words), or "" when they can. Letters lets a character
    read every tongue they hold at accented or native; writing with no recorded tongue is in the common speech.
    `eid` None asks only whether the PC reads at all."""
    held = {x.license_id: x.grade for x in state.licenses.get(pc or "", [])}
    if not any(k.startswith("lic.lang.") for k in held):
        return ""  # no tongues recorded (a bare test PC): literacy is not known to be lacking
    if "lic.lang.letters" not in held:
        return "they never learned their letters"
    lang = next((str(v) for k in ("language", "tongue", "script")
                 if eid and (v := state.fact_value(eid, k)) is not None), "")
    if not lang or re.search(r"\bcommon\b|-speech\b", lang, re.I):
        lic = "lic.lang.common"
    else:
        want = f" {re.sub(r'[^a-z]+', ' ', lang.lower())} "  # "the Old Tongue" -> lic.lang.old_tongue
        lic = next((k for k in held if k.startswith("lic.lang.") and f" {k[9:].replace('_', ' ')} " in want), "")
    return "" if held.get(lic) in ("accented", "native") else f"it is written in {lang or 'the common speech'}, which they do not read"


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
            # a thing with words on it stays in view however much else was mentioned since (P-110)
            ids.extend([i for i in here[:-MAX_SCENE_OBJECTS] if written_words(state, i) is not None]
                       + here[-MAX_SCENE_OBJECTS:])
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
    # written words are never crowded out by later appearance facts (P-110: the bill's text left the window)
    return [f for f in rows if f.predicate in WRITTEN] + [f for f in rows if f.predicate not in WRITTEN][:limit]


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
        out[i] = display_name(state, i)  # 12.10.2: as the PC knows them
    return out
