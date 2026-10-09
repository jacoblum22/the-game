"""Spec 013: dialogue and texture (R2-H checklist items 1-9; PR-12-10, PR-12-12, 12.10.8, 12.11.9, 12.14.12).

Characters speak freely from a speaker card and their own testimony; testimony is settled only when relied on;
only outcomes, changes, direct answers, clues and pauses are must-name; activities are rolled once per scene and end
on engagement; only an addressed or concerned NPC responds."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from engine.dm import testimony as tm
from engine.dm.adjudication import ActivityEntry, AdjudicationRecord, NpcActionEntry, PartEntry
from engine.dm.context import TurnContext
from engine.dm.handles import items
from engine.dm.packet import speaker_card
from engine.dm.roles.narrator import record_text
from engine.dm.turn import play_turn
from engine.gen.case import cases
from engine.llm.base import Role
from engine.llm.offline import OfflineModel, ScriptedModel
from tests.engine.test_answer import PC, ask, here, turn
from tests.engine.test_turn_adjudication import QUIET_WORLD, reader, setup
from tests.engine.test_turn_narration import chk
from tests.fixtures.seeded import seeded_store

NAMED = "Laendil learned their trade from Tibgit Lucky, down at the smithy."


def _said(store: Any, speaker: str, words: str, about: list[str] | None = None, question: str | None = None) -> str:
    with turn(store) as ctx:
        return tm.add_said(ctx, [{"speaker": speaker, "words": words, "about": about or [], "question": question}])[0]


def _speaks(speaker: str, *lines: str) -> Any:
    """A scripted draft in which `speaker` says each line (declared speech, citing every MUST line)."""
    def build(schema: Any, packet: Any) -> dict[str, Any]:
        must = re.findall(r"(?m)^- (R\d+) MUST:", packet.message)
        out = [{"text": f'"{x}"', "refs": list(must), "about": [speaker], "new": [], "atmosphere": False,
                "speaker": speaker} for x in lines]
        return {"sentences": [*out, {"text": "What do you do?", "refs": [], "about": [], "new": [],
                                     "atmosphere": False, "speaker": "none"}]}
    return build


# ------------------------------------------------------------------------------------------- 1. testimony fed back


def test_said_lines_feed_back_on_the_speaker_card(tmp_path: Path) -> None:
    """An NPC asked twice sees what they already said (so they neither deny the name they gave nor repeat it)."""
    store = seeded_store(tmp_path, 8)[0]
    npc = here(store)[0]
    _said(store, npc, NAMED, question=f"{npc}|what_like|folk")
    card = "\n".join(speaker_card(store.state, npc, topic="folk"))
    assert "SPEAKER CARD" in card and "Tibgit Lucky" in card and "never contradict or repeat" in card
    assert store.rebuild() == store.state


def test_a_repeated_line_is_redrafted(tmp_path: Path) -> None:
    """`not_a_repeat`: the second turn's draft repeats the speaker's own said line; the repair replaces it."""
    hello = 'I say to Tam Harlan, "Evening."'
    model = ScriptedModel({Role.READER: [reader("SPEECH", hello)] * 2, Role.WORLD: [QUIET_WORLD] * 2,
                           Role.CHECKER: [chk()] * 3})
    dock, ctx = setup(tmp_path, model)
    model.push(Role.NARRATOR, _speaks(dock.ferryman, "The last ferry crosses an hour before the dawn tide"))
    first = play_turn(ctx, hello)
    assert [r["words"] for r in tm.said_by(dock.state, dock.ferryman)] == [
        "The last ferry crosses an hour before the dawn tide"]
    model.push(Role.NARRATOR, _speaks(dock.ferryman, "The last ferry crosses an hour before the dawn tide, friend"))
    model.push(Role.NARRATOR, {"repairs": [{"replaces": "0", "text": '"Mind the fog on the stair."', "refs": [],
                                            "about": [dock.ferryman], "new": [], "atmosphere": False,
                                            "speaker": dock.ferryman}]})
    second = play_turn(ctx, hello)
    assert first.response.fiction.count("dawn tide") == 1
    assert "dawn tide" not in second.response.fiction and "fog on the stair" in second.response.fiction
    assert tm.is_repeat(dock.state, dock.rules, dock.ferryman, "the last ferry crosses before the dawn tide")


def test_a_runaround_cannot_come_from_code(tmp_path: Path) -> None:
    """No code pointer: an ordinary question never yields "does not know X, but Y would" (DL-12-90)."""
    store = seeded_store(tmp_path, 8)[0]
    for npc in here(store):
        a = ask(store, npc, "who_knows", "who would know about the chalk-marked door?")
        assert a.pointer is None and a.willingness is not None and "would" not in a.said.split(":")[-1]


# ------------------------------------------------------------------------------------------- 2. lazy settlement


def test_relied_on_testimony_is_settled_once_before_the_beat(tmp_path: Path) -> None:
    store = seeded_store(tmp_path, 8)[0]
    npc = here(store)[0]
    sid = _said(store, npc, "The ford below the mill is shallow this week.")

    class R:
        rests_on = sid
        beats: list[Any] = []

    with turn(store) as ctx:
        assert tm.settle_triggered(ctx, R()) == [sid]
    rec = tm.get(store.state, sid)
    assert rec is not None and rec["settled"] is True and rec["route"] == "accepted"
    assert store.state.facts[rec["fact"]].source == "testimony" and rec["fact"] in store.state.knowledge[PC]
    with turn(store) as ctx:
        assert tm.settle_triggered(ctx, R()) == []  # never settled twice; hearing or asking again settles nothing


def test_a_target_known_only_from_testimony_triggers_settlement(tmp_path: Path) -> None:
    from engine.store.events import EntityRecord, Event
    from engine.world.social import learn_name

    store = seeded_store(tmp_path, 8)[0]
    npc = here(store)[0]
    with turn(store) as ctx:
        ctx.need_tx().add(Event.of("entity_created", source="test", entity=EntityRecord(
            id="npc.garwen", kind="npc", name="Garwen Deepwell", data={"role": "sellsword", "name_known": False})))
        learn_name(ctx.time_ctx(), PC, "npc.garwen", "heard")
    sid = _said(store, npc, "Garwen Deepwell drinks at the Crooked Lantern most mornings.")
    assert tm.triggered(store.state, None, ["npc.garwen"]) == [sid]
    assert tm.triggered(store.state, None, [npc]) == []  # someone the PC met is not known only from testimony


def test_a_consequential_claim_is_settled_by_the_case_and_delivers_no_clue(tmp_path: Path) -> None:
    store = seeded_store(tmp_path, 8)[0]
    case = next(iter(cases(store.state).values()))
    sub = case["solution"]["subject"]
    npc = next(n for n in here(store) if n != sub["id"])
    sid = _said(store, npc, f"{sub['words']} was taken to the old quarry by the river.")
    known = dict(store.state.knowledge.get(PC, {}))
    with turn(store) as ctx:
        tm.settle(ctx, sid)
    rec = tm.get(store.state, sid)
    assert rec is not None and rec["route"] == "case"
    assert not any(n.get("found") for n in cases(store.state)[case["id"]]["nodes"])  # no clue delivered
    new = set(store.state.knowledge.get(PC, {})) - set(known)
    assert all(store.state.facts[f].predicate == "wrong_about" for f in new)


def test_a_consequential_question_still_goes_only_through_the_case(tmp_path: Path) -> None:
    store = seeded_store(tmp_path, 8)[0]
    case = next(c for c in cases(store.state).values() if c.get("trigger") == "incident")
    core = next(p["holder"] for p in case["nodes"][0]["placements"] if p.get("access") == "core")
    holders = {p["holder"] for n in case["nodes"] for p in n["placements"]}
    other = next(n for n in here(store) if n not in holders and n != case["solution"]["subject"]["id"])
    text = str(store.state.meta["world.opening"]["inciting"]["text"])
    a = ask(store, other, "what_happened", f"What do you know of it: {text}?")
    assert a.pointer == core and a.willingness is None  # the case names its holder; no willingness line
    b = ask(store, core, "what_happened", f"Tell me about it: {text}?")
    assert b.pointer is None and case["nodes"][0]["fact"] in b.line


def test_a_namesake_of_the_case_subject_is_not_the_case(tmp_path: Path) -> None:
    """Live run 20261008-173008: "where is Kerda Coldbrook?" went to Calda Coldbrook's case, so everyone answered
    "someone at the Barrow of Calton would know"."""
    from engine.dm.answer import case_about
    from engine.store.events import EntityRecord, Event

    store = seeded_store(tmp_path, 8)[0]
    case = next(iter(cases(store.state).values()))
    sub = store.state.entities.get(case["solution"]["subject"]["id"])
    last = (sub.name.split()[-1] if sub is not None else case["solution"]["subject"]["words"].split()[-1])
    with turn(store) as ctx:
        ctx.need_tx().add(Event.of("entity_created", source="test", entity=EntityRecord(
            id="npc.kerda_x", kind="npc", name=f"Kerda {last}", data={"role": "smith"})))
    st = store.state
    assert case_about(st, f"Where can I find Kerda {last}?", "npc.kerda_x") is None
    assert case_about(st, f"Where did {case['solution']['subject']['words']} go?", None) == case


# ------------------------------------------------------------------------------------------- 3. the must-name diet


def test_only_the_diet_is_must_name_and_optional_material_has_no_handle() -> None:
    rec = AdjudicationRecord(pc="pc.wren", parts=[PartEntry.model_validate({"text": "Evening.", "class": "SPEECH"})])
    rec.activities = [ActivityEntry(npc="npc.a", activity="beating a rug"),
                      ActivityEntry(npc="npc.b", slot="posture", activity="leaning on the wall")]
    rec.npc_actions = [NpcActionEntry(npc="npc.a", action="answers what you asked, willingly (x): ...",
                                      source="talk_outcome", source_ref="PR-12-10"),
                       NpcActionEntry(npc="npc.b", action="looks up", source="table_row",
                                      source_ref="tbl.npc_action:5", tags=["work", "optional"])]
    its = items(rec)
    assert [it.kind for it in its] == ["npc"] and its[0].must_name and its[0].entities == ["npc.a"]
    from engine.store.projection import WorldState

    text = record_text(WorldState(), rec)
    opt = text.split("OPTIONAL MATERIAL", 1)[1]
    assert "beating a rug" in opt and "looks up" in opt and not re.search(r"R\d+", opt)


# ------------------------------------------------------------------------------------------- 4. activities


def test_an_ended_activity_is_not_a_lever(tmp_path: Path) -> None:
    from engine.dm.schemas import schema_context
    from engine.store.details import current

    hello = 'I say to Tam Harlan, "Evening."'
    model = ScriptedModel({Role.READER: [reader("SPEECH", hello)] * 2, Role.WORLD: [QUIET_WORLD] * 2})
    dock, ctx = setup(tmp_path, model)
    play_turn(ctx, hello)
    st = dock.state
    assert current(st, dock.ferryman, "activity") is None  # engaged: ended, not re-rolled
    rolled = [f for f in st.facts.values() if f.subject == dock.ferryman and f.predicate == "detail.activity"]
    sctx = schema_context(st, dock.rules)
    assert not any(f.id in sctx.lever_fact_ids for f in rolled) and not any(f.id in sctx.fact_ids for f in rolled)
    play_turn(ctx, hello)
    assert current(dock.state, dock.ferryman, "activity") is None


def test_a_role_without_its_own_cell_never_borrows_anothers() -> None:
    from engine.data.loader import load_rules
    from engine.dm.npc_layer import role_key

    rules = load_rules()
    assert role_key(rules, "officer of The merchants' guild of Hollyhollow") == "merchant"  # not servant ("of")
    assert role_key(rules, "head of the merchants' guild") == "merchant"
    assert role_key(rules, "pilot of the harbour") == "other"


# ------------------------------------------------------------------------------------------- 5. who responds


def test_a_bystander_stays_silent_unless_the_event_concerns_them(tmp_path: Path) -> None:
    ask_ = 'I say to Tam Harlan, "Is the ferry running tonight?"'
    named = 'I say to Tam Harlan, "That watchwoman Sela Vey has been staring at me."'
    model = ScriptedModel({Role.READER: [reader("SPEECH", ask_), reader("SPEECH", named)],
                           Role.WORLD: [QUIET_WORLD] * 2})
    dock, ctx = setup(tmp_path, model, world_judge=False)
    first = play_turn(ctx, ask_).adjudication.record
    assert {a.npc for a in first.npc_actions} == {dock.ferryman}  # the watch is not addressed or concerned
    second = play_turn(ctx, named).adjudication.record
    watch = [a for a in second.npc_actions if a.npc == dock.watch]
    assert len(watch) == 1 and "optional" in watch[0].tags  # named: concerned (concerns_self), optional material
    assert dock.watch not in {e for it in items(second) for e in it.entities}  # never a must-name line


def test_the_addressee_is_the_one_turned_to_not_the_last_spoken_with(tmp_path: Path) -> None:
    """Live run 20261008-170802: "I turn to the old woman on the bench" was answered by the innkeeper (the last one
    spoken with), and "cross the floor to Zitok ... 'Zitok, isn't it?'" by the innkeeper named first."""
    from engine.dm.npc_layer import SPOKEN, addressed
    from engine.store.details import write_detail
    from engine.store.events import Event
    from tests.fixtures.game import entity, new_store

    store = new_store(tmp_path)
    with store.transaction() as tx:
        tx.add(entity("npc", "Kerric Thornby", tx=tx, data={"role": "innkeeper", "pronouns": "she/her"}))
        tx.add(entity("npc", "Zitok Rope-Dancer", tx=tx, data={"role": "elder", "pronouns": "she/her",
                                                                "detail": "a pipe never lit", "name_known": False}))
    kerric, zitok = "npc.kerric_thornby", "npc.zitok_rope_dancer"
    with store.transaction() as tx:
        tx.add_all(write_detail(tx.state, tx.mint, zitok, "activity", "sitting on a bench in the sun",
                                source="generation", because="12.11.9", visibility="shown").events)
        tx.add(Event.of("meta_set", source="test", rule_id="12.11.9", key=SPOKEN, value={"scene": None,
                                                                                       "npcs": [kerric]}))
    st = store.state
    present = [kerric, zitok]

    def to(msg: str) -> list[str]:
        rec = AdjudicationRecord(parts=[PartEntry.model_validate({"text": msg, "class": "SPEECH"})])
        return addressed(st, rec, present, msg)

    assert to('I turn to the old woman on the bench and sit down beside her. "That pipe\'s never been lit."') == [zitok]
    assert to('I nod my thanks to Kerric, cross the floor to Zitok Rope-Dancer, and sit beside her. '
              '"Zitok, isn\'t it? Kerric gave me your name."') == [zitok]
    assert to('"Kerric, another cup," I say.') == [kerric]
    # live run 20261008-175000: someone no one here matches is not answered by the last one spoken with
    assert to('I turn to the baker\'s queue and ask the nearest person in line, "Did you see the rider?"') == []
    assert to('"Did you see the rider?"') == [kerric]  # spoken to no one: the first present (no exchange yet)


def test_offline_turns_have_no_engine_error(tmp_path: Path) -> None:
    dock, _ = setup(tmp_path, OfflineModel())
    ctx = TurnContext(store=dock.store, rules=dock.rules, rng=dock.rng, model=OfflineModel())
    for msg in ('I say to Tam Harlan, "Evening."', "Tam, is the ferry running tonight?",
                "Tam, who would know about the night boat?", "I ask Sela Vey what she saw."):
        out = play_turn(ctx, msg)
        assert out.response.fiction or out.response.oof_blocks
    assert dock.store.rebuild() == dock.state
