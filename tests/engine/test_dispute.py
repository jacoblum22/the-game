"""engine/dm/dispute.py: 12.3.6 / PR-12-4 disputes answered from the turn log and the store (DL-12-04 scoping)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine import ids
from engine.dm.context import TurnContext
from engine.dm.dispute import DisputedClaim, default_identify, dispute, settle_dispute
from engine.dm.understand import understand_schema
from engine.llm.base import Role, validate
from engine.llm.offline import OfflineModel, ScriptedModel, _report_value
from engine.store.events import Event, Quantity
from engine.store.records import TurnRecord
from tests.engine.test_resolve_scene import Scene


class World:
    def __init__(self, tmp_path: Path) -> None:
        self.s = Scene.new(tmp_path)
        self.store = self.s.store
        self.gate = self.s.add("object", "Gate")
        with self.store.transaction("turn.1") as tx:
            self.gate_fact = self._fact(tx, self.gate, "state", "open")
            self.purse = self._fact(tx, self.s.pc, "purse", 12)
            self.secret = self._fact(tx, self.gate, "maker", "the cult", visibility="background")
            tx.add(Event.of("quantity_defined", source="test", entity=self.s.pc, quantity="arrows", reason="test",
                            value=Quantity(current=6, max=None)))
        self.store.save_turn(TurnRecord(turn_id="turn.1", input_verbatim="I look at the gate.",
                                        delivered_verbatim="The gate stands barred against you. Your purse holds "
                                                           "twenty coins."))
        with self.store.transaction("turn.2") as tx:
            self.frame_id = tx.mint(ids.FRAME)
            tx.add(Event.of("frame_committed", source=self.frame_id, frame_id=self.frame_id, frame={
                "beat": {"target": self.gate, "intent": "get over", "method": "climb the wall beside the gate"},
                "attribute": "agility", "tier": "hard", "dc": 15, "stakes": "risky", "reach": "standard",
                "levers": [], "snags": []}))
            self.writes = [
                tx.add(Event.of("quantity_changed", source=self.frame_id, entity=self.s.pc, quantity="vitality",
                                delta=-3, new_value=10, reason="fall", frame_id=self.frame_id)),
                tx.add(Event.of("fact_set", {"source": "ruling"}, source=self.frame_id, fact_id=tx.mint(ids.FACT),
                                subject=self.s.pc, predicate="perch", value="on the wall", visibility="shown")),
            ]
        self.store.save_turn(TurnRecord(turn_id="turn.2", input_verbatim="I climb the wall beside the gate.",
                                        delivered_verbatim="You haul yourself up, scraping a knee."))
        self.ctx = TurnContext.for_store(self.store, model=OfflineModel(), rules=self.s.rules)

    @staticmethod
    def _fact(tx: Any, subject: str, predicate: str, value: Any, visibility: str = "shown") -> str:
        fid = tx.mint(ids.FACT)
        tx.add(Event.of("fact_set", {"source": "narration"}, fact_id=fid, subject=subject, predicate=predicate,
                        value=value, visibility=visibility))
        return fid

    def claim(self, **kw: Any) -> Any:
        return lambda ctx, text: DisputedClaim(**kw)


@pytest.fixture
def w(tmp_path: Path) -> World:
    return World(tmp_path)


def _types(w: World, since: int) -> list[str]:
    return [e.type for e in w.store.events(since=since)]


def test_record_backs_the_player_and_the_beat_is_rewound(w: World) -> None:
    ident = w.claim(subject=w.gate, key="state", said="barred", quote="the gate stands barred")
    first = settle_dispute(w.ctx, "you said the gate was barred!", identify=ident)
    assert first.kind == "narration_error" and [e.type for e in first.events] == ["meta_set"]  # the record: pending
    assert first.record is not None and first.record["outcome"] == "pending" and first.record["id"] == "dsp.1"
    assert [c["id"] for c in first.choices] == ["accept_forward", "rewind"]
    assert first.text.startswith("[CORRECTION] Earlier I said Gate's state was barred; the record has open")
    assert "[CHOICE]" in first.text
    before = w.store.state.last_seq
    res = settle_dispute(w.ctx, "you said the gate was barred!", identify=ident, choice="rewind")
    assert res.kind == "narration_error" and sorted(res.reverted) == sorted(w.writes)
    st = w.store.state
    assert st.quantities[w.s.pc]["vitality"].current == 13 and st.current_fact_id(w.s.pc, "perch") is None
    assert st.fact_value(w.gate, "state") == "open"  # a narration error: the store stands
    assert _types(w, before) == ["writes_reverted", "meta_set", "meta_set", "ruling_logged", "meta_set"]
    ruling = next(w.store.events(since=before, types=["ruling_logged"])).payload.ruling  # type: ignore[attr-defined]
    assert ruling["review_flag"] is True and ruling["kind"] == "rule_conflict"
    assert st.meta["rolls_voided"] == [w.frame_id]
    corr = [r for r in st.meta["corrections"] if r.get("kind") == "narration_error"]
    assert corr[-1]["rewound_beats"] == [w.frame_id]
    disputes = [r for r in st.meta["corrections"] if r.get("type") == "dispute"]
    assert len(disputes) == 1 and disputes[0]["outcome"] == "take_back" and disputes[0]["upheld"]  # pending replaced
    assert "Rewound to before that beat" in res.text
    assert w.store.rebuild() == w.store.state


def test_rewind_never_reaches_before_the_scene(w: World) -> None:
    with w.store.transaction("turn.3") as tx:
        tx.add(Event.of("scene_ended", source="test", scene_id=tx.state.scene.scene_id, reason="test"))  # type: ignore[union-attr]
        sid = tx.mint(ids.SCENE)
        tx.add(Event.of("scene_started", source="test", scene_id=sid, scene={"scene_id": sid}))
    res = settle_dispute(w.ctx, "x", identify=w.claim(subject=w.gate, key="state", said="barred",
                                                      quote="the gate stands barred"), choice="rewind")
    # the relying frame was in the last scene: no rewind, a forward correction (DL-12-04)
    assert res.kind == "narration_error" and res.reverted == [] and "writes_reverted" not in [e.type for e in res.events]
    assert w.store.state.quantities[w.s.pc]["vitality"].current == 10


def test_record_error_gets_a_corrective_write(w: World) -> None:
    res = settle_dispute(w.ctx, "x", identify=w.claim(subject=w.s.pc, key="purse", said=20,
                                                      quote="purse holds twenty coins", source=w.frame_id))
    assert res.kind == "record_error"
    st = w.store.state
    fid = st.current_fact_id(w.s.pc, "purse")
    assert fid is not None and st.facts[fid].value == 20 and st.facts[fid].supersedes == w.purse
    assert st.facts[fid].pinned and st.facts[fid].source == "correction"  # never archived (12.3.6)
    assert res.text.startswith("[CORRECTION] You're right: your purse is 20; the record had slipped to 12.")
    assert [e.type for e in res.events] == ["fact_set", "meta_set", "ruling_logged", "meta_set"]
    assert res.events[0].source == "correction" and res.events[0].rule_id == "12.3.6"


def test_record_backs_the_player_or_the_dm_explains_with_the_evidence(w: World) -> None:
    w.store.save_turn(TurnRecord(turn_id="turn.3", input_verbatim="Is it open?", delivered_verbatim="It hangs open."))
    res = settle_dispute(w.ctx, "x", identify=w.claim(subject=w.gate, key="state", said="open",
                                                      quote="it hangs open"))
    assert res.kind == "store_agrees" and res.record is not None and res.record["outcome"] == "correct"
    assert res.text.startswith("[CORRECTION] You're right: Gate's state is open (turn 3: \"It hangs open.\").")
    facts = dict(w.store.state.facts)
    never = settle_dispute(w.ctx, "x", identify=w.claim(subject=w.gate, key="state", said="gold",
                                                        quote="the gate is made of gold"))
    assert never.kind == "mistaken" and w.store.state.facts == facts  # INV-9: nothing written
    assert never.text.startswith("[FIX] As recorded: Gate's state is open (on record since turn 1).")
    assert "gold was never said." in never.text and "Logged." not in never.text
    assert never.record is not None and never.record["outcome"] == "explain_with_quote"


def test_hidden_state_is_never_revealed(w: World) -> None:
    res = settle_dispute(w.ctx, "x", identify=w.claim(subject=w.gate, key="maker", said="the smith",
                                                      quote="gate stands"))
    assert res.kind == "hidden" and "the cult" not in res.text and res.text.startswith("[UNKNOWN]")
    unverified = [r for r in w.store.state.meta["corrections"] if r.get("kind") == "unverified"]
    assert unverified[-1]["store_value"] is None and "the cult" not in str(res.record)


# ---------------------------------------------------------------- spec 014: understand first, then verify


def understood(**kw: Any) -> dict[str, Any]:
    """One complaint as the understanding call returns it."""
    return {"believes": "", "happened": "", "category": "other", "turn": "none", "quote": "", "subject": "none",
            "about": "other", "key": "", "value": "", **kw}


def scripted(w: World, *complaints: dict[str, Any]) -> Any:
    model = ScriptedModel({Role.UNDERSTAND: [{"complaints": list(complaints)}]}, fallback=False)
    return TurnContext.for_store(w.store, model=model, rules=w.s.rules), model


def test_a_ruling_question_is_restated_and_explained_in_plain_words(w: World) -> None:
    ctx, model = scripted(w, understood(believes="The climb worked but you never got over the gate",
                                        category="ruling_question", turn="turn.2", about="roll_or_outcome"))
    res = settle_dispute(ctx, "why am I not over the gate?")
    packet = model.calls[0][1].message  # the WHOLE transcript, with the roll under its turn
    assert "turn.1 | player:" in packet and f"rolled: {w.frame_id}" in packet and "NOW: spring" in packet
    assert res.kind == "ruling_stands" and res.record is not None and res.record["outcome"] == "explain_with_quote"
    lines = res.text.splitlines()
    assert lines[0] == "[FIX] You're saying the climb worked but you never got over the gate."
    assert lines[1].strip().startswith("Here's why: turn 2 committed \"get over\"")
    assert "your perch: on the wall" in res.text and "agility, hard DC 15" in res.text
    assert res.record["believes"].startswith("The climb worked") and "Logged." not in res.text


def test_a_ruling_error_still_offers_the_choice(w: World) -> None:
    missed = settle_dispute(w.ctx, "x", identify=w.claim(kind="ruling", frame_id=w.frame_id, missed_fact=w.gate_fact))
    assert missed.kind == "ruling_error" and [c["id"] for c in missed.choices] == ["accept_forward", "rewind"]
    fwd = settle_dispute(w.ctx, "x", identify=w.claim(kind="ruling", frame_id=w.frame_id, missed_fact=w.gate_fact),
                         choice="accept_forward")
    assert fwd.reverted == [] and [e.type for e in fwd.events] == ["meta_set", "ruling_logged", "meta_set"]
    assert w.store.state.quantities[w.s.pc]["vitality"].current == 10


def test_nothing_fits_is_answered_with_a_did_you_mean(w: World) -> None:
    ctx, _ = scripted(w, understood(believes="the purse was stolen from you", category="contradiction"))
    res = settle_dispute(ctx, "my purse was stolen, you never said")
    assert res.kind == "not_found" and res.record is not None and res.record["outcome"] == "not_found"
    assert "I can't find that; did you mean turn 1: \"Your purse holds twenty coins.\"?" in res.text, res.text
    assert "Logged." not in res.text


def test_the_calendar_backs_the_player_and_two_complaints_get_two_answers(w: World) -> None:
    ctx, _ = scripted(w, understood(believes="it's spring, but the game spoke of autumn", category="contradiction",
                                    turn="turn.1", about="season_or_time", key="season", value="spring"),
                      understood(believes="nobody scraped a knee", category="contradiction", turn="turn.2",
                                 quote="scraping a knee", about="who_said_what"))
    facts = len(w.store.state.facts)
    res = settle_dispute(ctx, "it's spring not autumn, and I never scraped a knee")
    assert res.text.count("You're saying") == 2
    assert "You're right: it is spring (the morning of day 1); the narration slipped" in res.text
    assert "scraping a knee" in res.text and "it's taken as you say, and it stays" in res.text
    st = w.store.state
    disputes = [r for r in st.meta["corrections"] if r.get("type") == "dispute"]
    assert [r["outcome"] for r in disputes] == ["correct", "player_reading_wins"]
    fid = st.current_fact_id("world", "correction.1")  # incidental fiction: the player's reading, pinned
    assert fid is not None and st.facts[fid].pinned and len(st.facts) == facts + 1


def test_the_understanding_schema_and_the_offline_stand_in(w: World) -> None:
    assert validate(understood(), understand_schema()["properties"]["complaints"]["items"]) == []
    c = default_identify(w.ctx, "You told me I had 20 arrows")  # the offline double reads the report
    assert c is not None and (c.kind, c.subject, c.key, c.said) == ("quantity", w.s.pc, "arrows", 20)
    text = dispute(w.ctx, "that was wrong")  # engine/dm/context.py DisputeHandler: (ctx, text) -> str
    assert text.startswith("[FIX] You're saying that was wrong.") and "I can't find that; did you mean turn " in text
    assert _report_value("Nedwin's coat was grey before, now you say blue", "coat") == "grey"
    assert _report_value("her hair is iron-grey, you just said red", "hair") == "iron-grey"


