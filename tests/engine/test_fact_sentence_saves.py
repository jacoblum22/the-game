"""P-097: `fact_sentence` over the fact shapes real games write: no doubled prepositions, no 'is said the',
no raw ids or snake_case. The saves sweep reads copies of the newest local saves (skipped when there are none)."""

from __future__ import annotations

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
SAVES = next((p / "saves" for p in Path(__file__).resolve().parents if (p / "saves").is_dir()), Path("saves"))
GARBLED = re.compile(r"\b(?:at|in|on|by|within) (?:within|in|at|on|by|beside|near|under|inside|behind|beyond|above|"
                     r"below|against|pinned|nailed)\b|\bis said\b|_|\b[a-z]+\.[a-z_]+\b|\bpc s\b")


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


def _recent_saves() -> list[Path]:
    if not SAVES.is_dir():
        return []
    dbs = sorted(SAVES.glob("*.db"), key=lambda p: p.stat().st_mtime)
    evidence = SAVES / "playtest-20261007-194952-talker.db"
    return dbs[-10:] + ([evidence] if evidence.exists() and evidence not in dbs[-10:] else [])


@pytest.mark.skipif(not _recent_saves(), reason="no local saves")
def test_saves_fact_shapes_read_plainly(tmp_path: Path) -> None:
    bad, shapes = [], set()
    for src in _recent_saves():
        copy = tmp_path / src.name
        shutil.copy(src, copy)  # the save itself is never opened for writing
        store = Store.open(copy)
        state = store.state
        for f in state.facts.values():
            e = state.entities.get(f.subject)
            if f.subject == "world" or (e is not None and e.kind == "pc"):  # the sheet's, not the journal's
                continue
            shapes.add(f.predicate)
            s = fact_sentence(state, f)
            if s and GARBLED.search(s):
                bad.append(f"{f.predicate}={f.value!r} -> {s}")
        store.close()
    assert shapes and not bad, "\n".join(bad[:20])
