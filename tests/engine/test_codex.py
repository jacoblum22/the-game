"""engine/dm/codex.py: the codex shows shown and available state only (00.6.4); nothing sealed or background."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine import ids
from engine.data.loader import Rules, load_rules
from engine.dm.codex import codex
from engine.store.db import Store
from engine.store.events import ConditionInstance, EntityRecord, Event, LicenseInstance, Quantity
from tests.fixtures.game import new_store

SECRET = "ZZSEALEDZZ"  # appears only in sealed or background state


@pytest.fixture(scope="module")
def rules() -> Rules:
    return load_rules()


def _fact(tx: object, subject: str, predicate: str, value: object, visibility: str) -> str:
    fid = tx.mint(ids.FACT)  # type: ignore[attr-defined]
    tx.add(Event.of("fact_set", {"source": "narration"}, fact_id=fid, subject=subject,  # type: ignore[attr-defined]
                    predicate=predicate, value=value, visibility=visibility))
    return fid


@pytest.fixture
def store(tmp_path: Path) -> Store:
    st = new_store(tmp_path)
    with st.transaction() as tx:
        pc = EntityRecord(id="pc.wren", kind="pc", name="Wren", sealed_fields=["true_name"],
                          data={"attributes": {"might": 1, "agility": 3}, "abilities": ["ab.riposte"],
                                "true_name": SECRET})
        tx.add(Event.of("entity_created", source="test", entity=pc, licenses=[
            LicenseInstance(license_id="lic.training.martial_blade")], quantities={
            "vitality": Quantity(current=10, max=13), "focus": Quantity(current=3, max=4),
            "fate": Quantity(current=1, max=None), "uses.ab.riposte": Quantity(current=1, max=2),
            "arrows": Quantity(current=6, max=None),
            "doom": Quantity(current=77, max=None, visibility="background")}))
        tx.add(Event.of("entity_created", source="test", entity=EntityRecord(
            id="item.iron_bar", kind="item", name="Iron bar", data={"holder": "pc.wren"})))
        tx.add(Event.of("entity_created", source="test", entity=EntityRecord(
            id="npc.cultist", kind="npc", name=SECRET, visibility="sealed")))
        for name, vis in (("The missing ferryman", "shown"), (SECRET, "sealed")):
            eid = ids.entity_id("thread", name, tx.state.entities)
            tx.add(Event.of("entity_created", source="test", entity=EntityRecord(
                id=eid, kind="thread", name=name, visibility=vis, data={"status": "active"})))  # type: ignore[arg-type]
        iid = tx.mint(ids.CONDITION_INSTANCE)
        tx.add(Event.of("condition_applied", source="test", instance_id=iid, target="pc.wren", instance=ConditionInstance(
            instance_id=iid, condition_id="cond.off_balance", target="pc.wren", severity="S1", remaining="rounds:1")))
        _fact(tx, "world", "chronicle.chr.1", {"id": "chr.1", "time": "Y1 S1 W1 D1", "text": "Wren reached Ashford.",
                                               "kind": "deed", "source": "12.4.8"}, "available")
        _fact(tx, "world", "chronicle.chr.2", {"id": "chr.2", "time": "Y1 S1 W1 D1", "text": SECRET, "kind": "deed",
                                               "source": "12.4.8"}, "background")
        known = _fact(tx, "item.iron_bar", "condition", "bent", "shown")
        hidden = _fact(tx, "pc.wren", "cursed_by", SECRET, "sealed")
        bg = _fact(tx, "item.iron_bar", "maker", SECRET, "background")
        for f in (known, hidden, bg):
            tx.add(Event.of("knowledge_recorded", source="test", knower="pc.wren", fact_id=f, how="witnessed"))
    return st


def test_sheet_shows_the_pcs_shown_state(store: Store, rules: Rules) -> None:
    v = codex(store.state, rules=rules)
    assert v.section == "sheet"
    t = v.text
    assert t.startswith("[SHEET] Wren — ")
    assert "Might +1" in t and "Agility +3" in t
    assert "Vitality 10/13" in t and "Focus 3/4" in t and "fate 1" in t and "arrows 6" in t
    assert "Off-balance (S1)" in t and "Bladework (trained)" in t and "Riposte (uses 1/2)" in t
    assert "Carrying: Iron bar" in t


def test_no_sealed_or_background_field_appears_anywhere(store: Store, rules: Rules) -> None:
    for section in ("sheet", "abilities", "conditions", "journal", "threads", None):
        v = codex(store.state, section, rules)
        blob = v.text + json.dumps(v.data, default=str)
        assert SECRET not in blob, section
        assert "77" not in blob and "doom" not in blob and "true_name" not in blob, section


def test_sections(store: Store, rules: Rules) -> None:
    ab = codex(store.state, "abilities", rules).text
    assert ab.startswith("[ABILITIES] Focus 3/4") and "Riposte (Focus 1 · uses 1/2" in ab
    cond = codex(store.state, "/conditions", rules).text
    assert "Off-balance (S1; rounds:1)" in cond
    j = codex(store.state, "journal", rules)
    assert "Wren reached Ashford." in j.text and "Iron bar: condition — bent (witnessed)" in j.text
    assert [k["fact_id"] for k in j.data["known"]] == ["fact.3"]
    th = codex(store.state, "threads", rules).text
    assert "The missing ferryman [active]" in th
    assert codex(store.state, "nonsense", rules).text.startswith("[NOTE] Codex sections:")


def test_rules_card_by_id(store: Store) -> None:
    v = codex(store.state, "rules 01.7.1")
    assert v.text.startswith("[RULES] 01.7.1 What the OFFER shows") and "commit" in v.text
    assert codex(store.state, "rules 99.99.99").text == "[RULES] No rule card 99.99.99."


def test_no_character_yet(tmp_path: Path) -> None:
    assert codex(new_store(tmp_path).state).text == "[SHEET] No character yet."
