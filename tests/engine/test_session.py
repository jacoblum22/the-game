"""PR-12-8: session open (recap from state through the checker, the open pause re-shown) and close, the first
opening (12.16.16), and the h.12 session / mode handlers."""

from __future__ import annotations

from pathlib import Path

from engine.dm.context import TurnContext
from engine.dm.session import NEXT_TIME, REVIEW, close_session, open_session, opening
from engine.dm.turn import play_turn
from engine.llm.base import Role
from engine.llm.offline import OfflineModel, ScriptedModel
from engine.store.events import Event
from engine.time.scheduler import TimeContext, set_mode
from tests.engine.test_turn_adjudication import QUIET_WORLD, RISKY, SNEAK, framer, reader, setup
from tests.fixtures.game import entity, new_store


def test_open_session_recaps_from_state(tmp_path: Path) -> None:
    model = ScriptedModel()
    dock, ctx = setup(tmp_path, model)
    play_turn(ctx, "I look over the quay.")
    resp = open_session(ctx)
    narrator = [p for r, p in model.calls if r == Role.NARRATOR][-1]
    assert "STATE SUMMARY" in narrator.message and "recap" in narrator.message.lower()
    assert resp.fiction and resp.oof_blocks[0].kind == "RECAP" and resp.pause is None
    st = dock.state
    assert st.meta["session"]["n"] == 1 and st.meta["recap.last_seq"] > 0
    tr = dock.store.turn(resp.turn_id or "")
    assert tr is not None and tr.input_verbatim == "(session open)" and tr.delivered_verbatim == resp.text()
    assert any(e.type == "handler_ran" for e in dock.store.events() if e.turn_id == resp.turn_id)


def test_open_session_reshows_the_open_offer(tmp_path: Path) -> None:
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I slip past the watch.", SNEAK)],
                           Role.FRAMER: [framer(**RISKY)], Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    first = play_turn(ctx, "I slip past the watch.").response
    resp = open_session(ctx)
    assert resp.pause is not None and first.pause is not None and resp.pause.pause_id == first.pause.pause_id
    assert resp.oof_blocks[-1].kind == "OFFER" and resp.oof_blocks[-1].text == first.oof_blocks[-1].text


def test_close_session_keeps_the_pause_and_stores_next_time(tmp_path: Path) -> None:
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I slip past the watch.", SNEAK)],
                           Role.FRAMER: [framer(**RISKY)], Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    play_turn(ctx, "I slip past the watch.")
    open_session(ctx)
    before = dock.state.time.now
    resp = close_session(ctx, next_time="the smugglers")
    st = dock.state
    assert st.time.now == before and st.open_pause() is not None and resp.pause is not None
    assert st.meta[NEXT_TIME] == "the smugglers" and isinstance(st.meta[REVIEW], list)
    assert st.meta["session"]["closed_seq"] is not None
    assert any("next time" in b.text for b in resp.oof_blocks) and "Wren" in resp.text()
    assert "the smugglers" in open_session(ctx).text()


def test_mode_change_loads_the_mode(tmp_path: Path) -> None:
    dock, ctx = setup(tmp_path, OfflineModel())
    with dock.store.transaction() as tx:
        set_mode(TimeContext(tx, dock.rules, ctx.rng), "free", "test")
    loaded = dock.state.meta["mode.loaded"]
    assert loaded["mode"] == "free" and loaded["beat_cost"][1]


def test_first_opening_frames_the_first_scene(tmp_path: Path) -> None:
    store = new_store(tmp_path)
    with store.transaction() as tx:
        tx.add(entity("place", "Ashford Green", tx=tx, data={"place_kind": "settlement"}))
        pc = entity("pc", "Wren", tx=tx, quantities={"vitality": (10, 0, 10)})
        tx.add(pc)
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity="pc.wren", location="loc.ashford_green"))
        tx.add(Event.of("meta_set", source="test", rule_id="12.16.16", key="world.opening",
                        value={"inciting": {"text": "the mill burns at dawn"}, "leads": ["smoke over the ford"]}))
    ctx = TurnContext.for_store(store, model=OfflineModel())
    resp = opening(ctx)
    st = store.state
    assert st.scene is not None and st.scene.place_id == "loc.ashford_green" and resp.fiction
    assert st.meta.get("game.opened") == resp.turn_id
    assert store.rebuild() == store.state
