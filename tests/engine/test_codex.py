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
    assert "Wren reached Ashford." in j.text and "Iron bar is bent (witnessed)." in j.text
    assert [k["fact_id"] for k in j.data["known"]] == ["fact.3"]
    th = codex(store.state, "threads", rules).text
    assert "The missing ferryman [active]" in th
    assert codex(store.state, "nonsense", rules).text.startswith("[NOTE] Codex sections:")


def test_what_you_know_reads_what_was_seen_and_heard(store: Store, rules: Rules) -> None:
    # 12.10.5 / 15.9.16: facts shown in play are known even without a knowledge record; rumours say so
    with store.transaction() as tx:
        _fact(tx, "item.iron_bar", "weight", "heavier than it looks", "shown")
        _fact(tx, "pc.wren", "drive", "I will find the ferryman", "shown")
        rumour = _fact(tx, "item.iron_bar", "forged_by", "the smiths of Ashford", "available")
        tx.add(Event.of("knowledge_recorded", source="test", knower="pc.wren", fact_id=rumour, how="rumor"))
    j = codex(store.state, "journal", rules).text
    assert "Iron bar's weight is heavier than it looks." in j and "nothing yet" not in j
    from engine.dm.codex import what_you_know

    bar = what_you_know(store.state, "the iron bar", rules).text
    assert bar.startswith("[JOURNAL] What you know about the iron bar:")
    assert "weight is heavier than it looks" in bar and "Iron bar is forged by the smiths of Ashford (a rumour" in bar
    summary = what_you_know(store.state, None, rules).text
    assert "What drives you: I will find the ferryman" in summary
    for about in (None, "the iron bar", "Wren", "cultist"):
        assert SECRET not in what_you_know(store.state, about, rules).text
    assert "Nothing on record about the moon" in what_you_know(store.state, "the moon", rules).text


def test_fact_sentence_reads_plainly(store: Store, rules: Rules) -> None:
    # P-058 / P-042: a learned fact is a short plain sentence; a settled question that reads as no statement is
    # left out, and yes/no never prints as ": yes"
    from engine.audit.fallback import fact_sentence
    from engine.dm.oof import short_text

    with store.transaction() as tx:
        tx.add(Event.of("entity_created", source="test", entity=EntityRecord(
            id="npc.bixok", kind="npc", name="Bixok Lucky")))
        tx.add(Event.of("entity_created", source="test", entity=EntityRecord(id="obj.pack", kind="object", name="pack")))
        fids = {p: _fact(tx, s, p, v, "shown") for s, p, v in (
            ("npc.bixok", "coin_named_none_yet", True), ("npc.bixok", "carries_a_pack", False),
            ("obj.pack", "whether_it_is_closed", True), ("obj.pack", "held_by", "npc.bixok"),
            ("obj.pack", "size", True), ("obj.pack", "whether_it_is_closed.but", "lesser"),
            ("npc.bixok", "agreed_to_tell_calmund_about_the_night_once_the_shrine_door_", False))}
        tx.add(Event.of("knowledge_recorded", source="test", knower="pc.wren", fact_id=fids["coin_named_none_yet"],
                        how="told"))
    st = store.state
    said = {p: fact_sentence(st, st.facts[f]) for p, f in fids.items()}
    assert said == {"coin_named_none_yet": "", "carries_a_pack": "Bixok Lucky does not carry a pack.",
                    "whether_it_is_closed": "The pack is closed.", "held_by": "The pack is held by Bixok Lucky.",
                    "size": "", "whether_it_is_closed.but": "",
                    "agreed_to_tell_calmund_about_the_night_once_the_shrine_door_": ""}
    j = codex(st, "journal", rules).text
    assert "coin named" not in j and ": yes" not in j and "— yes" not in j and "The pack is closed." in j
    hook = "a countryman of yours lives in most settlements of any size; one of them will ask a favor before you ask"
    assert short_text(hook) == "a countryman of yours lives in most settlements of any size"
    assert short_text("one book, door or grave in the cloister was forbidden to you, and you never learned why "
                      "though you asked") == "one book, door or grave in the cloister was forbidden to you"


def test_rules_card_by_id(store: Store) -> None:
    v = codex(store.state, "rules 01.7.1")
    assert v.text.startswith("[RULES] 01.7.1 What the OFFER shows") and "commit" in v.text
    assert codex(store.state, "rules 99.99.99").text == "[RULES] No rule card 99.99.99."


def test_no_character_yet(tmp_path: Path) -> None:
    assert codex(new_store(tmp_path).state).text == "[SHEET] No character yet."
