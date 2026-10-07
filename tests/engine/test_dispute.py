"""engine/dm/dispute.py: 12.3.6 / PR-12-4 disputes answered from the turn log and the store (DL-12-04 scoping)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine import ids
from engine.dm.context import TurnContext
from engine.dm.dispute import DisputedClaim, default_identify, dispute, settle_dispute
from engine.llm.offline import OfflineModel
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
    assert first.kind == "narration_error" and not first.events
    assert [c["id"] for c in first.choices] == ["accept_forward", "rewind"]
    assert first.text.startswith("[CORRECTION] Earlier I said Gate state was barred; the record has open")
    assert "[CHOICE]" in first.text
    before = w.store.state.last_seq
    res = settle_dispute(w.ctx, "you said the gate was barred!", identify=ident, choice="rewind")
    assert res.kind == "narration_error" and sorted(res.reverted) == sorted(w.writes)
    st = w.store.state
    assert st.quantities[w.s.pc]["vitality"].current == 13 and st.current_fact_id(w.s.pc, "perch") is None
    assert st.fact_value(w.gate, "state") == "open"  # a narration error: the store stands
    assert _types(w, before) == ["writes_reverted", "meta_set", "meta_set", "ruling_logged"]
    ruling = next(w.store.events(since=before, types=["ruling_logged"])).payload.ruling  # type: ignore[attr-defined]
    assert ruling["review_flag"] is True and ruling["kind"] == "rule_conflict"
    assert st.meta["rolls_voided"] == [w.frame_id]
    assert st.meta["corrections"][-1]["kind"] == "narration_error"
    assert st.meta["corrections"][-1]["rewound_beats"] == [w.frame_id]
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
    assert res.text.startswith("[CORRECTION] The record was wrong: Wren purse is 20")
    assert [e.type for e in res.events] == ["fact_set", "meta_set", "ruling_logged"]
    assert res.events[0].source == "correction" and res.events[0].rule_id == "12.3.4"


def test_record_backs_the_dm_explains_with_the_evidence(w: World) -> None:
    w.store.save_turn(TurnRecord(turn_id="turn.3", input_verbatim="Is it open?", delivered_verbatim="It hangs open."))
    before = w.store.state.last_seq
    res = settle_dispute(w.ctx, "x", identify=w.claim(subject=w.gate, key="state", said="open",
                                                      quote="it hangs open"))
    assert res.kind == "stands" and not res.events and w.store.state.last_seq == before
    assert res.text == ('[NOTE] The record agrees: Gate state is open.\n'
                        '       As delivered — turn.3: "It hangs open."')
    never = settle_dispute(w.ctx, "x", identify=w.claim(subject=w.gate, key="state", said="gold",
                                                        quote="the gate is made of gold"))
    assert never.kind == "not_said" and not never.events and w.store.state.last_seq == before  # INV-9: no fact
    assert never.text.startswith("[NOTE] The record has Gate state: open. The narration never said otherwise.")
    assert "From the turn log — turn.2" in never.text  # the latest exchange that mentions the gate


def test_hidden_state_is_never_revealed(w: World) -> None:
    res = settle_dispute(w.ctx, "x", identify=w.claim(subject=w.gate, key="maker", said="the smith",
                                                      quote="gate stands"))
    assert res.kind == "hidden" and "the cult" not in res.text and res.text.startswith("[UNKNOWN]")
    assert w.store.state.meta["corrections"][-1]["store_value"] is None


def test_ruling_disputes(w: World) -> None:
    stands = settle_dispute(w.ctx, f"{w.frame_id} should have been Easy", identify=default_identify)
    assert stands.kind == "ruling_stands" and stands.text.startswith(f"[RULING] {w.frame_id}: agility, hard DC 15")
    missed = settle_dispute(w.ctx, "x", identify=w.claim(kind="ruling", frame_id=w.frame_id, missed_fact=w.gate_fact))
    assert missed.kind == "ruling_error" and [c["id"] for c in missed.choices] == ["accept_forward", "rewind"]
    fwd = settle_dispute(w.ctx, "x", identify=w.claim(kind="ruling", frame_id=w.frame_id, missed_fact=w.gate_fact),
                         choice="accept_forward")
    assert fwd.reverted == [] and [e.type for e in fwd.events] == ["meta_set", "ruling_logged"]
    assert w.store.state.quantities[w.s.pc]["vitality"].current == 10


def test_default_identify_and_the_handler_signature(w: World) -> None:
    c = default_identify(w.ctx, "You told me I had 20 arrows")
    assert c is not None and (c.kind, c.subject, c.key, c.said) == ("quantity", w.s.pc, "arrows", 20)
    f = default_identify(w.ctx, f'the narration said {w.gate}.state was "stands barred"')
    assert f is not None and (f.subject, f.key, f.quote) == (w.gate, "state", "stands barred")
    assert default_identify(w.ctx, "that was wrong") is None
    text = dispute(w.ctx, "that was wrong")  # engine/dm/context.py DisputeHandler: (ctx, text) -> str
    assert text.startswith("[NOTE] Which statement, and when?") and "turn.2" in text
