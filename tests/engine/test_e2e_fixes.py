"""Engine bugs the offline end-to-end run (T076) found, one test each."""

from __future__ import annotations

from pathlib import Path

from engine.harm.apply import apply_harm, go_down
from engine.harm.ctx import HarmCtx, Writes
from engine.harm.state import is_down
from engine.llm.offline import OfflineModel
from engine.time.clock import to_rounds
from tests.engine.test_game import to_play


def test_a_down_pc_wakes_after_an_interval_and_can_be_hurt_again(tmp_path: Path) -> None:
    # 07.2.9: Down from a non-lethal fall; with no victor to take the PC it wakes after one interval, Staggered.
    # Before the fix `down` stayed true for good: the PC acted while unconscious and every later harm was discarded.
    game, _ = to_play(tmp_path, OfflineModel(), seed=11)
    store = game.store
    pc = store.state.meta["pc.active"]
    with store.transaction() as tx:  # test set-up: the fall that put the PC Down
        ctx = HarmCtx.of(tx, game.rules)
        w = Writes.of(ctx)
        go_down(ctx, w, pc, cause="a fall", source={"entity": None, "frame_id": None, "effect_id": None})
        tx.add_all(w.events)
    assert is_down(store.state, pc)
    before = to_rounds(store.state.time.now)
    r = game.submit("I look around.")
    st = store.state
    assert not is_down(st, pc) and "cond.unconscious" not in {c.condition_id for c in st.conditions_on(pc)}
    assert to_rounds(st.time.now) - before >= 100  # one interval out cold
    assert "come to" in r.fiction
    with store.transaction() as tx:
        res = apply_harm(HarmCtx.of(tx, game.rules), pc, severity="S1", source="test")
        tx.add_all(res.events)
    assert res.load == 1 and res.wound  # a wound counts again: not recorded-and-discarded as while Down
    assert store.rebuild() == store.state


def test_what_are_my_options_gets_the_stuck_answer(tmp_path: Path) -> None:
    # 12.5.10 / 12.8.5: "what can I do?" is out of fiction and answered with leads from state; the offline Reader
    # used to read it as a question about the scene ("Nothing here answers that yet.")
    game, _ = to_play(tmp_path, OfflineModel(), seed=11)
    r = game.submit("What are my options?")
    leads = next(b.text for b in r.oof_blocks if "[LEADS]" in b.text)
    assert "or anything else you have in mind" in leads and leads.count("•") >= 2
    assert "Nothing here answers" not in r.fiction
    r = game.submit("What do I know?")
    assert any("[JOURNAL]" in b.text for b in r.oof_blocks)


def test_session_close_and_dispute_quote_no_offer_mechanics(tmp_path: Path) -> None:
    from engine.dm.session import where_line
    from engine.game import Game, GameConfig

    game, _ = to_play(tmp_path, OfflineModel(), seed=11)
    r = game.submit("I climb the wall.")
    assert r.pause is not None and r.pause.kind == "offer"
    line = where_line(game.store.state)
    assert "your choice is still open: You climb the wall" in line and "%" not in line and "need" not in line
    game.close()
    game, _ = Game.open(tmp_path / "g.db", GameConfig(offline=True), model=OfflineModel())
    game.answer("withdraw")
    note = game.dispute("My Vitality is wrong: I was not hurt.").oof_blocks[0].text
    # spec 022: the Fixer's answer ends in Now: with the sheet as it stands (the record's value)
    assert "Now:" in note and "Vitality" in note and "focus on next time" not in note and "Where:" not in note
    assert "%" not in note  # spec 012: the answer is the record's value, never the OFFER's mechanics


def test_exposure_lands_on_someone_present_when_no_one_is_targeted(tmp_path: Path) -> None:
    # 01.13.6: exposure fits when an observer is established; "I sneak past the smith" names no entity, but the
    # people in the scene can notice. Before the fix the cost was refused and a failed sneak cost nothing.
    from types import SimpleNamespace

    from engine.resolve.pipeline import _cost_params

    game, _ = to_play(tmp_path, OfflineModel(), seed=11)
    st = game.store.state
    pc = st.meta["pc.active"]
    assert st.scene is not None
    present = [i for i in st.scene.cast_present if st.entities[i].kind == "npc"]
    frame = SimpleNamespace(beat=SimpleNamespace(actor=pc, target="none"), defender=None)
    assert _cost_params(SimpleNamespace(state=st), frame, "cost.exposure") == {"observer": present[0]}  # type: ignore[arg-type]
