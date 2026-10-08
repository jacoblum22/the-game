"""P-110: written words reach a PC who reads them, and never one who cannot (02.4.6, 12.14.13)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine import ids
from engine.audit.claims import check_claims
from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord, NpcActionEntry
from engine.dm.packet import render_view, scene_view
from engine.dm.roles.narrator import record_text
from engine.store.events import Event, LicenseInstance, SceneRecord
from tests.fixtures.game import entity, new_store

WORDS = "THE CIRCLE OF THE STANWICK STONES IS HIRING. ASKS NO QUESTIONS."


@pytest.fixture(scope="module")
def rules() -> Any:
    return load_rules()


def _game(tmp_path: Path, licences: list[tuple[str, str]], **bill: Any) -> Any:
    store = new_store(tmp_path)
    with store.transaction("turn.0") as tx:
        tx.add(entity("pc", "Wren", tx=tx))
        tx.add(entity("place", "Gate", tx=tx))
        for lic, grade in licences:
            tx.add(Event.of("license_granted", source="test", entity="pc.wren",
                            license=LicenseInstance(license_id=lic, grade=grade)))
        sid = tx.mint(ids.SCENE)
        tx.add(Event.of("scene_started", scene_id=sid, scene=SceneRecord(scene_id=sid, place_id="loc.gate")))
        tx.add(entity("object", "bill on the gatepost", tx=tx))
        tx.add(Event.of("position_set", source="test", entity="obj.bill_on_the_gatepost", location="loc.gate"))
        for k, v in bill.items():
            tx.add(Event.of("fact_set", {"source": "narration"}, source="test", fact_id=tx.mint(ids.FACT), subject="obj.bill_on_the_gatepost",
                            predicate=k, value=v, visibility="shown"))
    return store


READER = [("lic.lang.common", "native"), ("lic.lang.letters", "trained")]
UNLETTERED = [("lic.lang.common", "native")]


def _read(store: Any, msg: str = "read the bill", **kw: Any) -> str:
    return record_text(store.state, AdjudicationRecord(pc="pc.wren", **kw), player_message=msg)


def test_the_words_stay_in_view_however_much_is_said_since(tmp_path: Path) -> None:
    store = _game(tmp_path, READER, text=WORDS)
    with store.transaction("turn.1") as tx:  # the newcomer's bill: 60 appearance facts and 15 objects later
        for i in range(15):
            tx.add(entity("object", f"stone {i}", tx=tx))
            tx.add(Event.of("position_set", source="test", entity=f"obj.stone_{i}", location="loc.gate"))
        for i in range(60):
            tx.add(Event.of("fact_set", {"source": "narration"}, source="test", fact_id=tx.mint(ids.FACT), subject="obj.bill_on_the_gatepost",
                            predicate=f"look_{i}", value=True, visibility="shown"))
    assert f"text = {WORDS[:40]}" in render_view(scene_view(store.state))


def test_a_reader_is_given_the_words_to_quote(tmp_path: Path) -> None:
    store = _game(tmp_path, READER, text=WORDS)
    assert f'quote its words exactly, in quotation marks: "{WORDS}"' in _read(store, "read the upper lines of the bill")


def test_no_letters_is_said_plainly_and_the_words_withheld(tmp_path: Path, rules: Any) -> None:
    store = _game(tmp_path, UNLETTERED, text=WORDS)
    out = _read(store)
    assert "never learned their letters" in out and "Say so once" in out and "read it to them" in out
    assert WORDS not in out
    quiet = _read(store, "I watch the stranger")  # any other turn: still never shown
    assert "cannot read the bill on the gatepost" in quiet and WORDS not in quiet

    claim = {"subject": "obj.bill_on_the_gatepost", "class": "identity", "predicate": "reads",
             "value": "THE CIRCLE OF THE STANWICK STONES IS HIRING"}
    [v] = check_claims([claim], store.state, AdjudicationRecord(pc="pc.wren"), ["obj.bill_on_the_gatepost"],
                       rules=rules)
    assert v.verdict == "contradicted" and "cannot read" in v.reason
    aloud = AdjudicationRecord(pc="pc.wren", npc_actions=[NpcActionEntry(npc="npc.x", action="reads it aloud", source="behavior")])
    [v] = check_claims([claim], store.state, aloud, ["obj.bill_on_the_gatepost"], rules=rules)
    assert v.verdict == "supported"  # heard read aloud, it is speech


def test_a_tongue_not_held_is_named(tmp_path: Path) -> None:
    store = _game(tmp_path, READER, text="KEEP OUT", language="the Old Tongue")
    out = _read(store)
    assert "it is written in the Old Tongue, which they do not read" in out and "KEEP OUT" not in out
    store = _game(tmp_path / "b", READER + [("lic.lang.old_tongue", "accented")], text="KEEP OUT",
                  language="the Old Tongue")
    assert '"KEEP OUT"' in _read(store)


def test_unwritten_notice_carries_the_opening_lead(tmp_path: Path) -> None:
    store = _game(tmp_path, READER)
    with store.transaction("turn.1") as tx:
        tx.add(Event.of("meta_set", source="test", key="world.opening", value={
            "start": {"place": "loc.gate"}, "leads": [{"lead": "the incident itself: an alarm"},
                                                      {"lead": "The Circle is hiring, and asks no questions"}]}))
    out = _read(store)
    assert "The Circle is hiring, and asks no questions" in out and "implied `text`" in out
    assert "an alarm" not in out


def test_reading_words_on_record_needs_no_roll(tmp_path: Path) -> None:
    from engine.dm.roles.reader import ReaderBeat, ReaderResult, _plain_reading

    def necessity(store: Any) -> str:
        out = ReaderResult(beats=[ReaderBeat(intent="know what the bill says", method="read the bill",
                                             target="obj.bill_on_the_gatepost", verb="verb.observe", gate="G2")])
        _plain_reading(out, store.state, "pc.wren")
        return out.beats[0].necessity

    assert necessity(_game(tmp_path, READER, text=WORDS)) == "trivial"
    assert necessity(_game(tmp_path / "b", UNLETTERED, text=WORDS)) == "uncertain_and_costly"
