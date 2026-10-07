"""The world seed as a conversation (PR-12-9, 12.16.2; T064, T109): modes, picks, own words, rolls, one veto per
step, the seed check, the world written, and resume from the record."""

from __future__ import annotations

from pathlib import Path

from engine.dm.context import TurnContext
from engine.dm.response import Choice, Pause, Response
from engine.dm.roles.interpret import direct_choice
from engine.dm.seed_flow import SeedFlow, askable, flow_of, question_options, rebuild_seed
from engine.llm.base import Role
from engine.llm.offline import OfflineModel, ScriptedModel
from engine.store.db import Store
from tests.fixtures.game import new_store


def pz(r: Response) -> Pause:
    """The response's open pause (asserted)."""
    assert r.pause is not None
    return r.pause


def _flow(store: Store, model=None) -> SeedFlow:
    return SeedFlow(TurnContext.for_store(store, model=model or OfflineModel()))


def _drain(flow: SeedFlow, resp, answer: str = ""):
    """Keep every summary (move on) until creation begins."""
    while resp.phase == "seed":
        resp = flow.submit(answer)
    return resp


def test_direct_choice_numbers_letters_and_skip():
    cs = [Choice(id="a1", label="first"), Choice(id="b2", label="second"), Choice(id="c3", label="third")]
    assert direct_choice("2", cs) == ["b2"]
    assert direct_choice("(c)", cs) == ["c3"]
    assert direct_choice("first", cs) == ["a1"]
    assert direct_choice("1, 3", cs) is None
    assert direct_choice("1, 3", cs, multi=True) == ["a1", "c3"]
    assert direct_choice("skip", cs) == ["move_on"]
    assert direct_choice("the second one please", cs) is None


def test_mixed_seed_answers_rolls_and_one_veto(tmp_path: Path):
    store = new_store(tmp_path)
    model = ScriptedModel()
    flow = _flow(store, model)
    r = flow.start()
    assert r.phase == "seed" and r.pause and pz(r).kind == "seed_step"
    assert [c.id for c in pz(r).choices] == ["guided", "oracle", "mixed"] and pz(r).default_choice == "mixed"
    r = flow.answer("mixed")
    qs = askable()
    assert [c.id for c in pz(r).choices][:-1] == qs  # the questions in T-12-15 order, then "all"
    r = flow.submit(f"{qs.index('ws.q.wound') + 1}, {qs.index('ws.q.magic_level') + 1}")  # numbers: no model call
    assert not model.calls
    assert pz(r).prompt.startswith("What went wrong in this land")
    wounds = [c.id for c in question_options("ws.q.wound")]
    r = flow.submit("2")  # the second wound, by number
    wound = [a for a in store.state.seed_answers if a["step"] == "ws.q.wound"]
    assert [(a["choice"], a["source"]) for a in wound] == [(wounds[1], "player_option")]
    # step 1 ran: the climate was rolled, so a veto is offered
    assert pz(r).prompt == "Would you like to keep this?" and r.oof_blocks[-1].text.startswith("Building the world, step 1 of 14: ")
    assert [c.id for c in pz(r).choices] == ["keep", "veto:ws.q.climate"]
    first = store.state.seed_answers[-1]["choice"]  # ws.ran.1: what step 1 rolled
    r = flow.answer("veto:ws.q.climate")
    assert any("That was re-rolled, so this result is final." in b.text for b in r.oof_blocks)
    # step 2: magic level in the player's own words, classified to the nearest option (12.16.2)
    assert pz(r).prompt == "How common is magic?"
    model.push(Role.INTERPRET, {"choice": "own_words", "own_words_class": "common",
                                "own_words_text": "every village has its witch", "answer": None})
    r = flow.submit("every village has its witch")
    ans = [a for a in store.state.seed_answers if a["step"] == "ws.q.magic_level"][0]
    assert (ans["choice"], ans["source"], ans["words"]) == ("common", "player_words", "every village has its witch")
    r = _drain(flow, r)
    assert r.phase == "creation" and r.pause and pz(r).kind == "create_step"
    assert any(b.text.startswith("Building the world, step 14 of 14: Finished") for b in r.oof_blocks)
    st = store.state
    vetoes = [a for a in st.seed_answers if a["step"].startswith("ws.veto.")]
    assert [(a["step"], a["choice"]) for a in vetoes] == [("ws.veto.1", "ws.q.climate")]
    assert first is not None
    # the world is in the store
    assert st.meta["world.region"]["name"] and st.meta["world.pregens"] and st.meta["game.phase"] == "creation"
    assert any(e.kind == "place" for e in st.entities.values()) and any(e.kind == "npc" for e in st.entities.values())
    # every pause was closed except the creation block now open
    opened = [e for e in store.events(types=["pause_opened"])]
    closed = [e for e in store.events(types=["pause_closed"])]
    assert len(opened) == len(closed) + 1 and flow_of(st) == "creation"
    # the WorldSeed is rebuilt from the seed number and the answers alone
    rebuilt = rebuild_seed(st)
    assert rebuilt is not None and rebuilt.world().record == flow.seed().world().record  # type: ignore[union-attr]
    assert store.rebuild() == store.state


def test_guided_mode_details_and_suggest(tmp_path: Path):
    store = new_store(tmp_path)
    flow = _flow(store)
    flow.start()
    r = flow.answer("guided")
    assert pz(r).prompt.startswith("What went wrong")  # guided: no pick list, straight to the questions
    before = len(list(store.events()))
    r2 = flow.submit("details")
    assert r2.oof_blocks[0].kind == "NOTE" and r2.pause == r.pause and len(list(store.events())) == before
    r3 = flow.submit("suggest")  # handed to the oracle
    a = store.state.seed_answers[-1]
    assert (a["step"], a["choice"], a["source"]) == ("ws.q.wound", None, "oracle_roll")
    assert any("The dice will decide" in b.text for b in r3.oof_blocks)


def _run(store: Store, inputs: list[str], *, reopen_at: int | None = None, path: Path | None = None):
    flow = _flow(store)
    resp = flow.start()
    seen = None
    for i, msg in enumerate(inputs):
        if reopen_at is not None and i == reopen_at:
            assert path is not None
            store.close()
            store = Store.open(path)
            flow = _flow(store)
            seen = (resp, flow.present())
        if resp.phase != "seed":
            break
        resp = flow.submit(msg)
    return store, _drain(flow, resp), seen


def test_quit_mid_step_and_reopen_same_question_same_world(tmp_path: Path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    inputs = ["mixed", "1, 2, 12", "3", "", "keep", "2", "", "", "", "", "", "", "", "", "", "", "", "", ""]
    a, ra, _ = _run(new_store(tmp_path / "a"), inputs)
    b, rb, seen = _run(new_store(tmp_path / "b"), inputs, reopen_at=4, path=tmp_path / "b" / "game.db")
    assert seen is not None
    before, after = seen
    assert after.pause == before.pause and after.oof_blocks[-1] == before.oof_blocks[-1]
    assert a.state.seed_answers == b.state.seed_answers
    assert a.state.meta.get("world.region") == b.state.meta.get("world.region")
    assert sorted(a.state.entities) == sorted(b.state.entities)
    assert ra.phase == rb.phase
    w1, w2 = rebuild_seed(a.state), rebuild_seed(b.state)
    assert w1 is not None and w2 is not None and w1.record() == w2.record()
