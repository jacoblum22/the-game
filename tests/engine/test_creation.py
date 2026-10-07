"""Character creation (PR-02-7 quick start, PR-02-1 workshop, PR-02-3 ready-made, PR-02-4 birth, PR-02-6 finish;
T063, T109): defaults, the required name, lines and veils, the written PC, resume and a second character."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.abilities.focus import focus, spend_focus
from engine.audit.safety import safety_prefs
from engine.data.loader import load_rules
from engine.dm.context import TurnContext
from engine.dm.creation import CreationError, CreationFlow, new_character, parse_limits, parse_name
from engine.dm.response import Pause, Response
from engine.dm.seed_flow import SeedFlow
from engine.harm.apply import apply_harm
from engine.harm.ctx import HarmCtx
from engine.harm.state import descriptor
from engine.llm.base import Role
from engine.llm.offline import OfflineModel, ScriptedModel
from engine.store.db import Store
from tests.fixtures.game import new_store

RULES = load_rules()


def pz(r: Response) -> Pause:
    """The response's open pause (asserted)."""
    assert r.pause is not None
    return r.pause


def seeded(tmp_path: Path, model=None) -> tuple[Store, TurnContext, CreationFlow]:
    """An oracle-mode seed, every summary kept: creation's first block is open."""
    store = new_store(tmp_path)
    ctx = TurnContext.for_store(store, model=model or OfflineModel(), rules=RULES)
    flow = SeedFlow(ctx)
    r = flow.start()
    r = flow.answer("oracle")
    while r.phase == "seed":
        r = flow.submit("")
    assert r.pause is not None and pz(r).kind == "create_step"
    return store, ctx, CreationFlow(ctx)


def answers(store: Store) -> dict[str, dict]:
    return {a["block"]: a for a in store.state.creation_answers}


def test_parsers():
    assert parse_name("Wren, she/her") == ("Wren", "she/her")
    assert parse_name("Call me Tam Harlan. He.") == ("Tam Harlan", "he/him")
    assert parse_name("Ash") == ("Ash", None)
    assert parse_limits(["spiders", "torture only off-stage", "nothing"]) == (["spiders"], ["torture only off-stage"])


def test_quick_start_skipped_answers_take_the_defaults(tmp_path: Path):
    store, ctx, flow = seeded(tmp_path)
    r = flow.present()
    assert "[CREATE 1/5] Before we begin" in r.oof_blocks[-1].text and pz(r).default_choice == "fast"
    r = flow.submit("")
    assert "[CREATE 2/5] Who are you?" in r.oof_blocks[-1].text
    assert [c.id for c in pz(r).choices][:2] == ["orig.life.soldier", "orig.life.hunter"]
    r = flow.submit("skip")
    assert r.oof_blocks[0].text.startswith("Soldier, then")
    r = flow.submit("")
    r = flow.submit("")
    assert "[CREATE 5/5] What are you called?" in r.oof_blocks[-1].text and pz(r).default_choice is None
    r = flow.submit("Wren, she/her")
    assert any(b.kind == "SHEET" for b in r.oof_blocks) and pz(r).prompt == "Ready?"
    r = flow.submit("")
    assert r.phase == "play" and r.pause is None
    a = answers(store)
    assert (a["c1"]["choice"], a["c1"]["source"]) == ("orig.life.soldier", "default")
    soldier = RULES.origins["orig.life.soldier"]
    assert a["c8.drive"]["choice"] == soldier["drive_seeds"][0] and a["c8.drive"]["source"] == "default"
    st = store.state
    pc = st.meta["pc.active"]
    assert st.entities[pc].name == "Wren" and st.entities[pc].data["pronouns"] == "she/her"
    assert st.fact_value(pc, "drive") == soldier["drive_seeds"][0]
    assert st.fact_value(pc, "origin.livelihood") == "orig.life.soldier"
    assert st.meta["pc.creation"]["choices"]["c1"]["default"] is True and st.meta["pc.creation"]["window"] == "open"
    assert st.meta["game.phase"] == "play"
    assert store.rebuild() == store.state


def test_a_name_is_required(tmp_path: Path):
    store, ctx, flow = seeded(tmp_path)
    for msg in ("", "", "", ""):
        r = flow.submit(msg)
    assert pz(r).prompt == "What are you called?"
    r = flow.submit("")  # no name: three are offered and the block waits (no default)
    assert pz(r).prompt == "What are you called?" and pz(r).default_choice is None
    names = [c.id for c in pz(r).choices]
    assert len(names) == 3 and all(n.startswith("name:") for n in names)
    r = flow.submit("skip")
    assert pz(r).prompt == "What are you called?"
    r = flow.answer(pz(r).choices[0].id)
    assert pz(r).prompt == "What are you called?" and [c.id for c in pz(r).choices] == ["she/her", "he/him",
                                                                                            "they/them"]
    r = flow.submit("")  # pronouns are never guessed (02.9.6)
    assert [c.id for c in pz(r).choices] == ["she/her", "he/him", "they/them"]
    r = flow.answer("they/them")
    assert pz(r).prompt == "Ready?"
    r = flow.answer("begin")
    pc = store.state.meta["pc.active"]
    assert store.state.entities[pc].data["pronouns"] == "they/them"


def test_lines_and_veils_are_kept_verbatim(tmp_path: Path):
    model = ScriptedModel()
    store, ctx, flow = seeded(tmp_path, model)
    model.push(Role.INTERPRET, {"choice": "fast", "own_words_class": "mysteries",
                                "own_words_text": "Mysteries and journeys. No spiders; torture only off-stage.",
                                "lines_and_veils": ["spiders", "torture only off-stage"]})
    r = flow.submit("Quick start, please. Mysteries and journeys. No spiders; torture only off-stage.")
    assert "[CREATE 2/5]" in r.oof_blocks[-1].text
    prefs = {(e.kind, e.topic) for e in safety_prefs(store.state)}
    assert prefs == {("line", "spiders"), ("veil", "torture only off-stage")}
    a = answers(store)
    assert a["c0.taste"]["choice"] == ["mysteries", "journeys"]
    assert a["c0.limits"]["choice"] == {"lines": ["spiders"], "veils": ["torture only off-stage"]}


def finish_fast(flow: CreationFlow, life: str = "", name: str = "Wren, she/her") -> None:
    for msg in ("", life, "", "", name, "begin"):
        flow.submit(msg)


def test_the_pc_has_every_field_and_harm_and_focus_accept_it(tmp_path: Path):
    store, ctx, flow = seeded(tmp_path)
    flow.submit("")
    flow.answer("orig.life.apprentice")
    for msg in ("", "", "Mira, she/her", "begin"):
        flow.submit(msg)
    st = store.state
    pc = st.meta["pc.active"]
    e = st.entities[pc]
    assert e.kind == "pc" and set(e.data["attributes"]) == {"might", "agility", "endurance", "wits", "intellect",
                                                            "presence", "resolve"}
    assert e.data["abilities"] and all(RULES.has(a) for a in e.data["abilities"])
    qs = st.quantities[pc]
    end = e.data["attributes"]["endurance"]
    assert qs["vitality"].current == qs["vitality"].max == 12 + end
    assert (qs["fate"].current, qs["fate"].max) == (1, 3)
    assert qs["focus"].current == qs["focus"].max == RULES.origins[e.data["upbringing"]]["focus_base"]
    assert "dread" in qs
    lics = {x.license_id for x in st.licenses[pc]}
    assert "lic.focus.push" in lics and "lic.lang.common" in lics
    carried = st.fact_value(pc, "carries")
    assert carried and all(st.entities[i].kind == "item" for i in carried)
    assert st.positions.get(pc) is not None  # at the opening place
    # engine/harm and engine/abilities accept the created PC
    with store.transaction() as tx:
        res = apply_harm(HarmCtx.of(tx, RULES, ctx.rng), pc, dealt=3, harm_tags=["harm.physical.cut"], source="test")
        tx.add_all(res.events)
    assert store.state.quantities[pc]["vitality"].current == 12 + end - 3
    assert descriptor(store.state, pc) in ("worn", "fresh", "bloodied")
    with store.transaction() as tx:
        tx.add_all(spend_focus(HarmCtx.of(tx, RULES, ctx.rng), pc, 1, reason="test"))
    q = focus(store.state, pc)
    assert q is not None and q.current == q.max - 1  # type: ignore[operator]


def test_ready_made_character(tmp_path: Path):
    store, ctx, flow = seeded(tmp_path)
    pregens = store.state.meta["world.pregens"]
    r = flow.answer("ready_made")
    assert "[CREATE 2/3] A ready-made character" in r.oof_blocks[-1].text
    assert [c.id for c in pz(r).choices] == [p["id"] for p in pregens]
    r = flow.answer(pregens[1]["id"])
    assert "[CREATE 3/3]" in r.oof_blocks[-1].text and pz(r).default_choice == "keep"
    r = flow.submit("")
    assert any(b.kind == "SHEET" for b in r.oof_blocks)
    flow.answer("begin")
    st = store.state
    pc = st.meta["pc.active"]
    assert st.entities[pc].name == pregens[1]["name"]
    assert st.entities[pc].data["attributes"] == pregens[1]["attributes"]
    bond = pregens[1]["anchor_bond"]["npc"]
    assert any(r.a == pc and r.b == bond for r in st.relationships.values())


def test_workshop_all_defaults(tmp_path: Path):
    store, ctx, flow = seeded(tmp_path)
    r = flow.answer("full")
    titles = []
    while r.pause and pz(r).prompt != "Ready?":
        titles.append(r.oof_blocks[-1].text.splitlines()[0])
        r = flow.submit("Wren, she/her" if pz(r).prompt == "What are you called?" else "")
    assert titles[0].startswith("[CREATE 2/") and titles[-1].startswith("[CREATE ") and "What are you called?" in \
        titles[-1]
    n = int(titles[-1].split("/")[1].split("]")[0])
    assert n == len(titles) + 1
    flow.answer("begin")
    assert store.state.meta["pc.creation"]["path"] == "full"


def test_change_something_reopens_a_block(tmp_path: Path):
    store, ctx, flow = seeded(tmp_path)
    for msg in ("", "", "", "", "Wren, she/her"):
        r = flow.submit(msg)
    r = flow.answer("change")
    assert pz(r).prompt == "What would you like to change?"
    r = flow.answer("c1")
    assert "Who are you?" in r.oof_blocks[-1].text
    r = flow.answer("orig.life.thief")
    assert pz(r).prompt == "Ready?"
    flow.answer("begin")
    pc = store.state.meta["pc.active"]
    assert store.state.entities[pc].data["livelihood"] == "orig.life.thief"


def test_resume_mid_creation_and_a_second_character(tmp_path: Path):
    store, ctx, flow = seeded(tmp_path)
    flow.submit("")
    before = flow.submit("2")
    path = tmp_path / "game.db"
    store.close()
    store = Store.open(path)
    ctx2 = TurnContext.for_store(store, model=OfflineModel(), rules=RULES)
    flow2 = CreationFlow(ctx2)
    after = flow2.present()
    assert after.pause == before.pause and after.oof_blocks[-1] == before.oof_blocks[-1]
    for msg in ("", "", "Wren, she/her", "begin"):
        flow2.submit(msg)
    first = store.state.meta["pc.active"]
    r = new_character(ctx2)
    assert r.phase == "creation" and "[CREATE 1/5]" in r.oof_blocks[-1].text
    finish_fast(flow2, name="Ash, he/him")
    second = store.state.meta["pc.active"]
    assert second != first and store.state.entities[second].name == "Ash"
    assert store.rebuild() == store.state


def test_no_answer_without_an_open_block(tmp_path: Path):
    store = new_store(tmp_path)
    flow = CreationFlow(TurnContext.for_store(store, model=OfflineModel(), rules=RULES))
    with pytest.raises(CreationError):
        flow.submit("hello")


def test_new_character_closes_the_ending_menu(tmp_path: Path):
    from engine.dm.response import Choice
    from engine.dm.seed_flow import flow_tx, open_pause

    store, ctx, flow = seeded(tmp_path)
    finish_fast(flow)
    with flow_tx(ctx) as tx:
        open_pause(tx, "ending", "What now?", [Choice(id="new_character", label="a new character")], None,
                   {"flow": "ending"}, "PR-11-6")
    r = new_character(ctx)
    assert r.phase == "creation" and pz(r).kind == "create_step"
    assert [p.kind for p in store.state.pauses] == ["create_step"]
