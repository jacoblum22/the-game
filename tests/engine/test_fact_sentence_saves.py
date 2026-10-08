"""P-097: `fact_sentence` over the fact shapes real games write: no doubled prepositions, no 'is said the',
no raw ids or snake_case (a proper name capitalised mid-sentence is fine). The suite checks a committed snapshot
of those shapes; the live saves sweep runs only when FACT_SWEEP_SAVES is set."""

from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

import pytest

from engine import ids
from engine.audit.fallback import fact_sentence
from engine.store.db import Store
from engine.store.events import EntityRecord, Event
from tests.fixtures.game import new_store

# the repo's saves/, or the main checkout's when this runs in a worktree under .claude/worktrees/
SHAPES = Path(__file__).resolve().parents[1] / "fixtures" / "fact_shapes.json"
SAVES = next((p / "saves" for p in Path(__file__).resolve().parents if (p / "saves").is_dir()), Path("saves"))
GARBLED = re.compile(r"^Who is |\b(?:at|in|on|by|within) (?:within|in|at|on|beside|near|under|inside|behind|beyond|above|"
                     r"below|against|pinned|nailed)\b|\bis said (?!to\b)|_|\b[a-z]+\.[a-z_]+\b|\bpc s\b")


def test_evidence_facts_read_plainly(tmp_path: Path) -> None:
    st = new_store(tmp_path)
    with st.transaction() as tx:
        for eid, kind, name in (("loc.poor_quarter", "place", "poor quarter"), ("npc.driver", "npc", "wagon driver"),
                                ("obj.bill", "object", "hiring bill"), ("pc.wren", "pc", "Wren")):
            tx.add(Event.of("entity_created", source="test", entity=EntityRecord(id=eid, kind=kind, name=name)))
        fids = {}
        for s, p, v in (("loc.poor_quarter", "location", "within Cornburn"),
                        ("loc.poor_quarter", "condition", "a cough is spreading there"),
                        ("npc.driver", "speech", "said the journey's origin is their own affair; said a cough is "
                                                 "spreading in the poor quarter"),
                        ("obj.bill", "location", "nailed to the gatepost"),
                        ("obj.bill", "text", "the Wolves are hiring"),
                        ("pc.wren", "origin.livelihood", "orig.life.soldier")):
            fids[(s, p)] = fid = tx.mint(ids.FACT)
            tx.add(Event.of("fact_set", {"source": "narration"}, fact_id=fid, subject=s, predicate=p, value=v,
                            visibility="shown"))
    said = {k: fact_sentence(st.state, st.state.facts[f]) for k, f in fids.items()}
    assert list(said.values()) == [
        "The poor quarter is within Cornburn.", "A cough is spreading in the poor quarter.",
        "The wagon driver said that the journey's origin is their own affair, and that a cough is spreading in the "
        "poor quarter.", "The hiring bill is nailed to the gatepost.", "The hiring bill reads: the Wolves are hiring.",
        ""]


def test_opening_incident_facts_read_plainly(tmp_path: Path) -> None:
    """Playtest 20261007-201748 explorer, input 22: the journal showed "Who is missing person: Betey Woodhill"."""
    st = new_store(tmp_path)
    with st.transaction() as tx:
        for eid, kind, name in (("npc.betey", "npc", "Betey Woodhill"), ("loc.mill", "place", "the mill"),
                                ("loc.north_road", "place", "the north road")):
            tx.add(Event.of("entity_created", source="test", entity=EntityRecord(id=eid, kind=kind, name=name)))
        fids = []
        for s, p, v in (("world", "who_is_missing_person", "npc.betey"), ("npc.betey", "is_missing", True),
                        ("npc.betey", "was_last_seen_at", "loc.mill"),
                        ("npc.betey", "was_seen_heading_toward", "loc.north_road"),
                        ("npc.betey", "is_the_challenger", True), ("world", "who_is_challenger", "npc.betey")):
            fids.append(fid := tx.mint(ids.FACT))
            tx.add(Event.of("fact_set", {"source": "generation"}, fact_id=fid, subject=s, predicate=p, value=v,
                            visibility="shown"))
    assert [fact_sentence(st.state, st.state.facts[f]) for f in fids] == [
        "Betey Woodhill is the missing person.", "Betey Woodhill is missing.", "Betey Woodhill was last seen at the mill.",
        "Betey Woodhill was seen heading toward the north road.", "Betey Woodhill is the challenger.",
        "Betey Woodhill is the challenger."]


def test_recorded_fact_shapes_read_plainly(tmp_path: Path) -> None:
    """The fact shapes real games wrote (tests/fixtures/fact_shapes.json: one sample per predicate head and value
    kind, plus the opening incident's predicates and the P-097 cases), snapshot from playtest saves 2026-10-07."""
    shapes = json.loads(SHAPES.read_text(encoding="utf-8"))
    st = new_store(tmp_path)
    with st.transaction() as tx:
        made: set[str] = set()
        for s in shapes:
            for e in [s["subject"], *s["refs"]]:
                if e and e["id"] not in made:
                    made.add(e["id"])
                    tx.add(Event.of("entity_created", source="test", entity=EntityRecord(**e)))
        fids, seen = [], set()
        for s in shapes:
            subject = s["subject"]["id"] if s["subject"] else "world"
            if (subject, s["predicate"]) in seen:
                continue
            seen.add((subject, s["predicate"]))
            fids.append(fid := tx.mint(ids.FACT))
            tx.add(Event.of("fact_set", {"source": "generation"}, fact_id=fid, subject=subject,
                            predicate=s["predicate"], value=s["value"], visibility="shown"))
    said = [(f, fact_sentence(st.state, st.state.facts[f])) for f in fids]
    bad = [f"{st.state.facts[f].predicate}={st.state.facts[f].value!r} -> {s}" for f, s in said
           if s and GARBLED.search(s)]
    assert len(said) > 100 and not bad, "\n".join(bad[:20])


def _recent_saves() -> list[Path]:
    if not SAVES.is_dir() or not os.environ.get("FACT_SWEEP_SAVES"):
        return []
    return sorted(SAVES.glob("*.db"), key=lambda p: p.stat().st_mtime)[-10:]


@pytest.mark.skipif(not _recent_saves(), reason="opt-in: set FACT_SWEEP_SAVES=1 to sweep the newest local saves")
def test_saves_fact_shapes_read_plainly(tmp_path: Path) -> None:
    """Opt-in sweep of the live saves/ folder (it changes with every playtest, so it is never part of the suite);
    a new garbled shape it finds belongs in tests/fixtures/fact_shapes.json."""
    bad, shapes = [], set()
    for src in _recent_saves():
        copy = tmp_path / src.name
        shutil.copy(src, copy)  # the save itself is never opened for writing
        store = Store.open(copy)
        state = store.state
        for f in state.facts.values():
            e = state.entities.get(f.subject)
            # the sheet's, not the journal's; the opening incident's "who is" facts are the journal's (12.16.16)
            if (f.subject == "world" and not f.predicate.startswith("who_is_")) or (e is not None and e.kind == "pc"):
                continue
            shapes.add(f.predicate)
            s = fact_sentence(state, f)
            if s and GARBLED.search(s):
                bad.append(f"{f.predicate}={f.value!r} -> {s}")
        store.close()
    assert shapes and not bad, "\n".join(bad[:20])
