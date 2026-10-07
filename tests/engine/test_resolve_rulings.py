"""engine/resolve/rulings.py: signatures (00.15.5), find_rulings / precedent (00.15.6), log_ruling."""

from __future__ import annotations

from pathlib import Path

from engine.resolve.rulings import (
    RulingRecord,
    find_rulings,
    gate_signature,
    log_ruling,
    oracle_signature,
    precedent_for,
    signature,
)
from tests.engine.test_resolve_scene import Scene


def test_signature_sorts_deltas() -> None:
    assert signature("verb.exert", ["stakes", "dc:tier_rederived"]) == "verb.exert+dc:tier_rederived+stakes"
    assert signature("anc.x", [{"knob": "dc", "delta": "vault"}]) == "anc.x+dc:vault"
    assert signature("anc.x") == "anc.x"
    assert gate_signature("g4", "fact.3") == "g4:fact.3" and oracle_signature("back_door", "inn") == (
        "oracle:back_door@inn")


def test_log_and_find_across_transactions(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    rec = RulingRecord(signature="anc.x+dc:vault", situation="vault the wall", kind="adaptation")
    ids_ = []
    for _ in range(2):
        with s.store.transaction() as tx:
            assert find_rulings(s.store, "anc.x+dc:vault", staged=tx.events) == [] or ids_
            ev = log_ruling(rec, tx.mint, store=s.store, staged=tx.events)
            tx.add(ev)
            assert [r.id for r in find_rulings(s.store, "anc.x+dc:vault", staged=tx.events)][-1] == \
                ev.payload.ruling["id"]  # type: ignore[attr-defined]
            ids_.append(ev.payload.ruling["id"])  # type: ignore[attr-defined]
    assert len(set(ids_)) == 2
    found = find_rulings(s.store, "anc.x+dc:vault")
    assert [r.id for r in found] == ids_
    p = precedent_for(found)
    assert (p.status, p.from_) == ("reused", ids_[-1])
    assert precedent_for(found, "fact.9").status == "departed" and precedent_for([]).status == "new"
    assert s.store.rebuild() == s.state
