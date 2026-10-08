"""Spec 010: T1c scene state written by code (T-12-18): a resolved beat's slots, a response's manner, the citable
lines rebuilt for whoever is present, and scene end clearing slots and bands."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from engine.dm.adjudication import AdjudicationRecord, BeatEntry
from engine.dm.scene_state import beat_writes, lines, response_values, write
from engine.store.details import current, expire_events
from engine.store.events import Event
from tests.engine.test_turn_adjudication import setup


def _grapple(dock: object, reach: str, degree: str = "success") -> SimpleNamespace:
    return SimpleNamespace(status="resolved", entry=BeatEntry(
        frame_id="frame.9", actor=dock.pc, targets=[dock.ferryman], verb="verb.grapple",  # type: ignore[attr-defined]
        restatement="You grab Tam", degree=degree, reach=reach))


def test_responses_set_manner_and_physical_rows_set_activity(tmp_path: Path) -> None:
    dock, _ = setup(tmp_path, None)
    rules = dock.rules
    assert response_values(rules, "talk_outcome", degree="success") == {"manner": "willing"}
    assert response_values(rules, "table_row", practice="fight", row=2)["activity"] == "taking cover"
    assert response_values(rules, "table_row", practice="greeting", row=2) == {"manner": "curt"}  # replaces row 2
    assert response_values(rules, "table_row", practice="work", row=5) == {}  # the activity holds
    assert response_values(rules, "behavior") == {}


def test_a_beat_writes_slots_lines_show_them_and_scene_end_clears_them(tmp_path: Path) -> None:
    dock, ctx = setup(tmp_path, None)
    with dock.store.transaction("turn.t") as tx:
        ctx.tx = tx
        rec = AdjudicationRecord(pc=dock.pc)
        beat_writes(ctx, rec, [_grapple(dock, "standard")])
        assert current(tx.state, dock.ferryman, "posture").value.startswith("held fast by you")  # type: ignore[union-attr]
        assert "in a grip" in str(current(tx.state, dock.pc, "held").value)  # type: ignore[union-attr]
        beat_writes(ctx, rec, [_grapple(dock, "great")])  # reach 3 supersedes, citing its frame
        assert current(tx.state, dock.ferryman, "posture").value == "restrained by you"  # type: ignore[union-attr]
        assert rec.writes and all(w.type == "fact_set" for w in rec.writes)
        write(ctx, rec, dock.watch, response_values(ctx.rules, "table_row", practice="fight", row=2), because="r.1")
        tx.add(Event.of("position_set", rule_id="06.3.5", entity=dock.ferryman, band_to={dock.pc: "engaged"}))
        shown = {(a.npc, a.slot): a.activity for a in lines(tx.state, dock.pc, [dock.ferryman, dock.watch])}
        assert shown[(dock.watch, "activity")] == "taking cover" and shown[(dock.ferryman, "position")].endswith("you")
        assert (dock.pc, "held") in shown
        assert not any(a.npc == dock.watch for a in lines(tx.state, dock.pc, [dock.ferryman]))  # left: dropped
        tx.add_all(expire_events(tx.state, tx.mint))  # 12.4.8 step 8
        assert lines(tx.state, dock.pc, [dock.ferryman, dock.watch]) == []
        assert not tx.state.positions[dock.ferryman].band_to
        beat_writes(ctx, rec, [_grapple(dock, "standard", "failure")])  # an expired slot is written afresh
        assert current(tx.state, dock.ferryman, "manner").value == "on guard against you"  # type: ignore[union-attr]
        ctx.tx = None


def test_a_common_noun_place_or_a_direction_does_not_place_a_thing_elsewhere(tmp_path: Path) -> None:
    """Live run 010: "the fire at the far end of the hall" (in an inn) matched the town's separate `the hall`."""
    from engine.audit.claims import check_claims
    from engine.store.events import EntityRecord

    dock, _ = setup(tmp_path, None)
    with dock.store.transaction("turn.t") as tx:
        for pid, name in (("loc.hall", "the hall"), ("loc.temple", "the temple of Halwin")):
            tx.add(Event.of("entity_created", source="test", entity=EntityRecord(id=pid, kind="place", name=name)))
        tx.add(Event.of("entity_created", source="test", entity=EntityRecord(id="obj.fire", kind="object",
                                                                             name="fire")))
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity="obj.fire", location=dock.place))

    def verdict(value: str) -> str:
        return check_claims([{"class": "position", "subject": "obj.fire", "predicate": "is", "value": value}],
                            dock.store)[0].verdict

    assert verdict("at the far end of the hall") == "supported"  # a common noun: this place's own hall
    assert verdict("smoke drifting toward the temple of Halwin") == "supported"  # a direction, not a location
    assert verdict("in the temple of Halwin") == "contradicted"  # a proper name still binds

    def moved(who: str, value: str) -> str:  # a change this turn, nothing written for it
        return check_claims([{"class": "position", "subject": who, "predicate": "moves", "value": value,
                              "asserts_change": True}], dock.store)[0].verdict

    assert moved(dock.ferryman, "crosses to the window") == "supported"  # fine placement: atmosphere (T0)
    assert moved(dock.ferryman, "leaves the dock") == "unsourced_change"  # departing is coarse
    assert moved(dock.ferryman, "steps out of your reach") == "unsourced_change"  # a band to the PC is coarse
