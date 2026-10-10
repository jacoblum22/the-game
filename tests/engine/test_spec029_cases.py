"""Spec 029: the made-up, edge and data-enumerated cases of `specs/029-lead-terms-clues/cases.md` (written and
committed before implementing). T2: every lead and incident kind gets its terms when it is made, walked from the
game's own tables (a kind added to any table without terms fails); the incident's actor is the person on stage; the
journal shows what you were told. P9: one clue judgment per message, before the cap, delivered as a learned fact.
The clue judgment's model is scripted here; its live precision and recall are measured on Haiku by
`specs/029-lead-terms-clues/clue_eval_multi.py`."""

from __future__ import annotations

import copy
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from engine.data.loader import load_rules
from engine.dm import answer as ans
from engine.dm import testimony as tm
from engine.dm import world_step
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, NpcActionEntry, PartEntry
from engine.dm.codex import what_you_know
from engine.dm.context import TurnContext
from engine.dm.handles import items as record_items
from engine.dm.incident import incident_line, stage_actor, stage_info
from engine.dm.roles.narrator import speaker_cards
from engine.dm.session import opening
from engine.gen import _data
from engine.gen._seed_lib import data as seed_data
from engine.gen._seed_packs import make_document
from engine.gen._seed_steps import _instantiate
from engine.gen.case import cases
from engine.gen.hooks import (
    CARD,
    _Builder,
    card_lines,
    creation_kinds,
    hook_terms,
    job_fee,
    kinds,
    terms_data,
    write_creation,
    write_injection,
    write_terms,
)
from engine.llm.base import Role
from engine.llm.offline import OfflineModel, ScriptedModel
from engine.retrieve.scene import written_words
from engine.store.events import Event
from tests.engine.test_answer import PC, turn
from tests.fixtures.game import entity, new_store
from tests.fixtures.seeded import store_for_world, world, world_with

RULES = load_rules()
SEED = 3
INCIDENTS = kinds()["incident"]


def _card(store: Any, npc: str) -> str:
    rec = AdjudicationRecord(pc=PC)
    rec.npc_actions.append(NpcActionEntry(npc=npc, action="answers", source="talk_outcome", source_ref="PR-12-10",
                                          tags=[f"ask:{npc}|what_happened|local_news"]))
    return "\n".join(speaker_cards(store.state, rec, RULES))


def _lines(state: Any, npc: str, hook: str | None = None) -> list[str]:
    """The term lines `npc` knows (optionally one hook's), as facts."""
    out = []
    for fid in state.knowledge.get(npc, {}):
        f = state.facts.get(fid)
        if f is not None and f.predicate.startswith(CARD) and (hook is None or f".{hook}." in f.predicate + "."):
            out.append(str(f.value))
    return out


def _case(store: Any) -> dict[str, Any]:
    return next(c for c in cases(store.state).values() if c.get("trigger") == "incident")


def _core(case: dict[str, Any]) -> str:
    return next(p["holder"] for p in case["nodes"][0]["placements"] if p["access"] == "core")


def _store(tmp_path: Path, option: str) -> Any:
    return store_for_world(tmp_path, world_with(SEED, option))


# ------------------------------------------------------------------------------------------- the enumeration


def test_the_kinds_are_the_52_the_data_has() -> None:
    """Every family of lead and incident kind, read from the tables themselves, has an entry in
    `world_seed.yaml#terms` and the entry has a kind in the table (both ways)."""
    k, t = kinds(), terms_data()
    assert {f: len(v) for f, v in k.items()} == {"incident": 8, "situation": 16, "lead": 1, "document": 4,
                                                  "lead_form": 12, "rumor": 4, "creation": 7}
    assert sum(len(v) for v in k.values()) == 52
    assert set(k["incident"]) == set(t["incident"]) and set(k["situation"]) == set(t["situation"])
    assert set(k["document"]) == set(t["document"]) and set(k["lead_form"]) == set(t["lead_form"])
    assert set(k["creation"]) == set(t["creation"]) and set(k["rumor"]) == set(t["rumor"])
    assert "hire" in t and t["hire"]["fields"]


def test_every_entry_fills_with_no_token_left_over() -> None:
    """A template that names a token nothing supplies fails loudly (KeyError), so no `{...}` reaches a card."""
    for fam in ("incident", "situation", "document", "lead_form", "rumor", "creation"):
        for kind, ent in terms_data()[fam].items():
            for v in (ent.get("fields") or {}).values():
                assert "{" not in re.sub(r"\{\w+\}", "", str(v)), (fam, kind, v)


# ------------------------------------------------------------------------------------------- K1-K8: incidents


@pytest.mark.parametrize("option", INCIDENTS)
def test_k_incident_kind_has_its_terms(tmp_path: Path, option: str) -> None:
    """data-enumerated K1-K8: each incident kind is written with who, what and where as unsealed knowledge of the
    people who would know, and no node answer is on any of their lines (S1)."""
    store = _store(tmp_path, option)
    st = store.state
    case = _case(store)
    t = hook_terms(st)["thr.lead_1"]
    assert t["kind"] == option and t["family"] == "incident" and t["case"] == case["id"]
    assert t["what"] and t["where"] in st.entities and t["fields"] and t["know"]
    core = _core(case)
    assert core in t["know"]
    sub = case["solution"]["subject"]
    secret = [sub["words"], st.entities[sub["id"]].name if sub["id"] in st.entities else sub["words"]]
    for k in t["know"]:
        lines = _lines(st, k, "thr_lead_1")
        assert lines, (option, k)
        assert not any(s and s in ln for s in secret for ln in lines), (option, k, lines)  # S1: nothing sealed
        assert all(len(ln) <= 150 for ln in lines)  # a card shows a line whole
        assert any(t["what"].split(" ")[0] in ln for ln in lines)
    # the card the reporter's speaker shows has it (the first five lines are the knowledge a card shows)
    assert t["label"] in _card(store, core)


def test_k_dying_messenger_has_the_riders_words_and_a_body(tmp_path: Path) -> None:
    store = _store(tmp_path, "dying_messenger")
    st = store.state
    t = hook_terms(st)["thr.lead_1"]
    assert any(k.startswith("the rider's last words") and '"' in v for k, v in t["fields"])
    rider = st.entities[t["stage"]["actor"]]
    assert rider.exists == "dead" and st.positions[rider.id].location == t["where"]
    sub = _case(store)["solution"]["subject"]["id"]
    assert sub not in t["know"]  # the person the message was for is the sealed subject, off stage


def test_k_missing_has_since_last_seen_the_reward_and_a_notice(tmp_path: Path) -> None:
    store = _store(tmp_path, "missing")
    st = store.state
    t = hook_terms(st)["thr.lead_1"]
    got = dict(t["fields"])
    assert "last seen" in got and "since last night" in got["what"] and t["pay"] == job_fee(1)
    assert "pay: 40 coins" in " ".join(_lines(st, _core(_case(store)))) or f"pay: {job_fee(1)} coins" in " ".join(
        _lines(st, _core(_case(store))))
    notice = next(p["holder"] for p in _case(store)["nodes"][0]["placements"] if p["holder_kind"] == "document")
    assert written_words(st, notice)  # the notice's words exist (it was made with the case)


@pytest.mark.parametrize("option,label", [("duel", "the challenger"), ("offer", "the one making the offer"),
                                         ("refugees", "the refugees' leader")])
def test_k_the_actor_on_stage_is_the_case_subject_and_knows_the_terms(tmp_path: Path, option: str, label: str) -> None:
    store = _store(tmp_path, option)
    st = store.state
    sub = _case(store)["solution"]["subject"]["id"]
    t = hook_terms(st)["thr.lead_1"]
    assert t["stage"] == {"subject": sub, "label": label, "dead": False}
    assert sub in t["know"] and _lines(st, sub, "thr_lead_1")


# ------------------------------------------------------------------------------------------- K9-K24: situations


def _situation_rec(kind: str) -> tuple[dict[str, Any], dict[str, Any]]:
    rec = world(SEED).record
    fids = [f["id"] for f in rec["factions"]["instances"]]
    area = next(p["id"] for p in rec["places"] if p["place_kind"] == "area" and p.get("ring") == 1)
    tid = f"sit_t.{kind}"
    roles = {r: fids[i % len(fids)] for i, r in enumerate(seed_data().SITT[tid]["roles"])}
    sit = _instantiate("rs", tid, area, roles, "what", "k")
    return {**rec, "situations": [sit], "opening": {**rec["opening"], "leads": []}, "seed_cases": [],
            "documents": []}, sit


@pytest.mark.parametrize("kind", kinds()["situation"])
def test_k_situation_trace_has_its_terms(kind: str) -> None:
    """data-enumerated K9-K24: every situation template's step-1 trace (a lead) has who saw it, what, where, and,
    where a document holds the words, a document with its text; never the sealed timeline."""
    rec, sit = _situation_rec(kind)
    t = _Builder(rec, SEED)._situations({})[0]
    ent = terms_data()["situation"][kind]
    assert t["kind"] == kind and t["family"] == "situation" and t["what"] and t["know"] and t["where"]
    assert len(t["who"]) >= 1
    assert bool(t["doc"]) == bool(ent.get("doc"))
    for _k, v in t["fields"]:
        assert "{" not in v
    later = " ".join(str(s["trace"]) for s in sit["timeline"][1:])
    assert not any(step in " ".join(v for _, v in t["fields"]) for step in later.split("; ") if step)


def _with_situation(tmp_path: Path, kind: str) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    store = store_for_world(tmp_path, world(SEED))
    rec, sit = _situation_rec(kind)
    with store.transaction() as tx:
        write_terms(tx, rec)
    return store, hook_terms(store.state)[sit["id"]], sit


def test_p1_the_gate_log_has_the_cart_entry_and_reading_it_delivers_the_words(tmp_path: Path) -> None:
    """playtest P1 (talker [19]-[23]): "what does the entry say about the cart?" The gate log is a document at the gate,
    made with the cart lead; its text is the entry; the read is a fact; the question is marked answered."""
    store, t, _ = _with_situation(tmp_path, "the_prisoner")
    st = store.state
    log = st.entities[t["doc"]]
    assert log.name == "gate log" and "closed cart" in str(written_words(st, log.id))
    assert st.positions[log.id].location.endswith(".gate")
    pc = "pc.wren"
    st.positions[pc]  # the PC is at the opening place; move to the gate
    with store.transaction() as tx:
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity=pc, location=st.positions[log.id].location))
    part = PartEntry.model_validate({"text": "What does the entry say about the cart?", "class": "SPEECH",
                                     "question_kind": "what_is", "topic": log.id})
    beat = BeatEntry(restatement="read what the entry says about the cart", targets=[log.id], approach_words="observe",
                     verb="verb.observe")
    ctx = TurnContext.for_store(store, model=OfflineModel())
    with store.transaction() as tx:
        ctx.tx = tx
        try:
            out = world_step._look(ctx, beat, "verb.observe", 2, pc, [part])
            rec = AdjudicationRecord(pc=pc)
            world_step._give(rec, beat, None, out, [part], look=True)
        finally:
            ctx.tx = None
    assert out and out[0].fact_id and "closed cart" in out[0].line
    assert part.handled == "answered" and beat.learned and "closed cart" in beat.learned[0]


def test_two_entries_for_one_gate_are_one_gate_log() -> None:
    """Both opening situations may leave an entry at the gate: one document, both entries (a name is one thing)."""
    rec1, s1 = _situation_rec("the_prisoner")
    rec2, s2 = _situation_rec("road_of_knives")
    s2 = {**s2, "id": "sit.rs.other"}
    rec = {**rec1, "situations": [s1, s2]}
    b = _Builder(rec, SEED)
    ts = b._situations({})
    assert len(b.docs) == 1 and b.docs[0]["text"].count("Entry, ") == 2
    assert ts[0]["doc"] == ts[1]["doc"] == b.docs[0]["id"]


def test_p2_the_gate_watch_knows_whose_cart_who_drove_and_where_it_went(tmp_path: Path) -> None:
    """playtest P2 (talker): the watch's lines hold what, whose, the driver and where it went."""
    store, t, _ = _with_situation(tmp_path, "the_prisoner")
    watch = t["who"]["watch"]
    text = " ".join(_lines(store.state, watch))
    assert "closed cart" in text and "whose" in text and "the driver" in text
    driver = t["who"]["driver"]
    assert driver in store.state.entities and "route" not in text
    assert driver not in store.state.positions  # gone with the cart: a person who exists, not one standing at the gate


def test_p3_the_hall_clerk_knows_whose_banners(tmp_path: Path) -> None:
    """playtest P3 (explorer): the clerk's lines hold whose two banners they are and where."""
    store, t, _ = _with_situation(tmp_path, "succession")
    clerk = t["who"]["clerk"]
    text = " ".join(_lines(store.state, clerk))
    assert "two banners" in text and "banner of" in text and "hall" in text


def test_k_hire_lead_terms(tmp_path: Path) -> None:
    """data-enumerated K25 (kept from spec 025): task, pay, destination, the contact; every member knows."""
    store = store_for_world(tmp_path, world(SEED))
    t = next(x for x in hook_terms(store.state).values() if x["kind"] == "hire")
    assert t["pay"] == job_fee(t["band"]) and t["destination"] and t["contact"] in t["know"]
    assert "ask for" in dict(t["fields"])


# ------------------------------------------------------------------------------------------- K26-K29: documents


@pytest.mark.parametrize("option", kinds()["document"])
def test_k_document_kind_has_text_and_terms(option: str) -> None:
    """data-enumerated K26-K29: a document's text exists when it is made; a notice that stands alone (warning,
    charter, bounty) also has terms: why, where it points, who to report to; a bounty's reward is a job fee."""
    rec = copy.copy(world(SEED).record)
    rec["documents"] = []
    rec["seed_cases"] = []
    hav = rec["region"]["haven"]
    doc = make_document(rec, SEED, "notice", option, hav + ".gate", "The kin of Swancrag",
                        ("Kera Faircote", "the gate"), "The Black Fields")
    assert doc["text"] and "{" not in doc["text"]
    if option == "hire":
        return  # the hire notice's terms are the hire lead's (K25)
    t = _Builder(rec, SEED)._documents()[0]
    assert t["kind"] == option and t["family"] == "document" and t["fields"] and t["know"]
    assert (t["pay"] == job_fee(1)) == (option == "bounty")


# ------------------------------------------------------------------------------------------- K30-K41: lead forms


def _inject(store: Any, roll: int, thread: str = "thr.lead_2") -> dict[str, Any]:
    form = next(r["result"] for t in _data.load("oracles.yaml")["tables"] if t["id"] == "tbl.lead_injection"
                for r in t["results"] if str(r["range"]) == str(roll))
    with store.transaction() as tx:
        t = write_injection(tx, roll=roll, form=form, thread=thread, src=None)
    assert t is not None
    return t


@pytest.mark.parametrize("roll", range(1, 13))
def test_k_lead_form_has_its_terms(tmp_path: Path, roll: int) -> None:
    """data-enumerated K30-K41: each of the d12 forms, written when the lead is injected: who (made if no one fits),
    what, where the PC is, the words of anything found (a document made now), held by those who would know."""
    store = store_for_world(tmp_path, world(SEED))
    t = _inject(store, roll)
    st = store.state
    assert t["kind"] == str(roll) and t["family"] == "lead_form" and t["what"] and t["know"]
    assert t["where"] == st.positions["pc.wren"].location
    assert all(k in st.entities for k in t["know"])
    ent = terms_data()["lead_form"][str(roll)]
    if ent.get("doc"):
        assert written_words(st, t["doc"]) and st.positions[t["doc"]].location == t["where"]
    if ent.get("people"):
        assert all(st.entities[t["who"][p]].kind == "npc" for p in ent["people"])
    assert hook_terms(st)[t["hook"]]["fields"]
    assert any(_lines(st, k) for k in t["know"])


def test_lead_injection_through_the_pacing_writes_its_terms(tmp_path: Path) -> None:
    """The injection a turn raises (PR-12-3) writes the form's terms through `pacing.inject_lead` (one call)."""
    from engine.world.pacing import inject_lead

    store = store_for_world(tmp_path, world(SEED))
    ctx = TurnContext.for_store(store, model=OfflineModel())
    with store.transaction() as tx:
        ctx.tx = tx
        try:
            out = inject_lead(ctx.time_ctx())
        finally:
            ctx.tx = None
    got = [t for t in hook_terms(store.state).values() if t["family"] == "lead_form"]
    assert out.form and len(got) == 1 and got[0]["what"] and got[0]["thread"] == out.thread


# ------------------------------------------------------------------------------------------- K42-K45: rumors


def test_k_rumor_kinds_have_terms() -> None:
    """data-enumerated K42-K45: a faction's goal, a situation's trace, a site (its wording whatever its truth), the
    keeper's dream: each held by the people who carry it, saying what it says and where it points."""
    rec = copy.copy(world(SEED).record)
    npcs = [dict(n) for n in rec["npcs"]]
    rows = {t["id"]: t["results"] for t in rec["rumor_tables"]}
    tbl = rec["rumor_tables"][0]["id"]
    pick = {"faction_goal": lambda r: str(r["points_to"]).startswith("clk."),
            "situation": lambda r: str(r["points_to"]).startswith("sit."),
            "site": lambda r: str(r["points_to"]).startswith("loc.") and r.get("source") != "legend",
            "dream": lambda r: str(r["points_to"]).startswith("fac.")}
    holders = [n for n in npcs if n.get("depth") != "walk_on"][:4]
    for h, test in zip(holders, pick.values(), strict=True):
        row = next(r for r in rows[tbl] if test(r))
        h["knowledge"] = [{"slot": "rumor", "topic": "local_news", "rumor": {"table": tbl, "range": row["range"]}}]
    rec["npcs"] = npcs
    got = {t["kind"]: t for t in _Builder(rec, SEED)._rumors()}
    assert set(got) == set(kinds()["rumor"])
    for kind, t in got.items():
        flds = dict(t["fields"])
        assert t["family"] == "rumor" and flds["says"] and flds["points toward"] and t["know"], kind


# ------------------------------------------------------------------------------------------- K46-K52: creation hooks


def test_k_creation_hook_kinds_have_terms(tmp_path: Path) -> None:
    """data-enumerated K46-K52: the seven creation-hook kinds (02.9.7): the text as data, the person it binds (the
    anchor bond for `npc`, else a cast person), held by who would know."""
    assert creation_kinds() == sorted(kinds()["creation"])
    store = store_for_world(tmp_path, world(SEED))
    st = store.state
    anchor_npc = next(i for i, e in st.entities.items() if e.kind == "npc" and e.data.get("depth") != "walk_on")
    hooks = [f"{k}: something about {k} that is yours" for k in kinds()["creation"]]
    with store.transaction() as tx:
        got = write_creation(tx, "pc.wren", hooks, {"kind": "friend", "npc": anchor_npc})
    assert {t["kind"] for t in got} == set(kinds()["creation"])
    by = {t["kind"]: t for t in got}
    assert by["npc"]["who"]["bond"] == anchor_npc and anchor_npc in by["npc"]["know"]
    for t in got:
        assert t["family"] == "creation" and dict(t["fields"])["what"].startswith("something about") and t["know"]


# ------------------------------------------------------------------------------------------- P4: the actor on stage


def test_p4_the_challenger_on_stage_is_the_case_subject(tmp_path: Path) -> None:
    """playtest P4 (fighter): the duel's challenger is the sealed case's subject, cast into the opening by id; the
    note names the role with the person's label; their name stays sealed; the narrator is not left to invent one."""
    store = _store(tmp_path, "duel")
    st = store.state
    sub = _case(store)["solution"]["subject"]["id"]
    assert stage_info(st)["subject"] == sub and "the challenger: " in incident_line(st)
    resp = opening(TurnContext.for_store(store, model=OfflineModel()))
    st = store.state
    assert resp.fiction and st.scene is not None and sub in st.scene.cast_present
    assert st.positions[sub].location == st.scene.place_id
    note = next(str(r["request"]) for r in store.model_calls() if r["role"] == "narrator")
    assert "the challenger: " in note
    from engine.store.views import name_known

    assert not name_known(st, sub)  # the identity stays sealed until the node is told (12.10.2)
    assert store.rebuild() == store.state


@pytest.mark.parametrize("option", ["offer", "refugees"])
def test_the_offerer_and_the_refugees_leader_are_staged_where_the_scene_is(tmp_path: Path, option: str) -> None:
    store = _store(tmp_path, option)
    sub = _case(store)["solution"]["subject"]["id"]
    opening(TurnContext.for_store(store, model=OfflineModel()))
    st = store.state
    assert sub in st.scene.cast_present and st.positions[sub].location == st.scene.place_id


@pytest.mark.parametrize("option", ["alarm", "dying_messenger", "missing", "theft", "omen"])
def test_other_incidents_stage_no_living_actor(tmp_path: Path, option: str) -> None:
    store = _store(tmp_path, option)
    with turn(store) as ctx:
        assert stage_actor(ctx, ctx.need_tx()) == []


# ------------------------------------------------------------------------------------------- P9


def _duel(tmp_path: Path) -> tuple[Any, str, str]:
    store = _store(tmp_path, "duel")
    case = _case(store)
    return store, _core(case), case["solution"]["subject"]["id"]


def _part(text: str, kind: str = "what_is", topic: str | None = None) -> Any:
    return SimpleNamespace(question_kind=kind, topic=topic, text=text)


def _msg(store: Any, npc: str, parts: list[Any], reach: int, judgments: list[dict[str, str]], *, record: Any = None
         ) -> tuple[list[ans.Answer], ScriptedModel]:
    model = ScriptedModel({Role.CLUE: judgments})
    with turn(store, model) as ctx:
        out = ans.ask_message(ctx, npc, parts, reach, pc=PC, record=record)
    return out, model


def _clue_calls(model: ScriptedModel) -> list[str]:
    return [p.message for r, p in model.calls if r == Role.CLUE]


def _standing(store: Any, npc: str, value: int) -> None:
    with turn(store) as ctx:
        ctx.need_tx().add(Event.of("relationship_set", source="test", rule_id="12.11.2", a=npc, b=PC, kind="standing",
                                   value=value, new_value=value, reason="test"))


def test_p6_c1_the_clue_in_the_second_part_is_delivered_outside_the_cap(tmp_path: Path) -> None:
    """playtest P6 / made-up C1 (explorer [18]): "What are the banners, and who is the young man really?" to the core
    holder at Standard reach: both parts reach the one judgment; the clue is a fact with no speaker; the banners are
    answered ordinarily; the node is found."""
    store, core, sub = _duel(tmp_path)
    parts = [_part("What are the banners?"), _part("And who is the young man really?", "who_is")]
    out, model = _msg(store, core, parts, 2, [{"about": "1", "part": "2"}])
    assert len(_clue_calls(model)) == 1 and "Q1:" in _clue_calls(model)[0] and "Q2:" in _clue_calls(model)[0]
    clue = next(a for a in out if a.willingness is None)
    name = store.state.entities[sub].name
    assert clue.part == 1 and clue.fact_id and name in clue.line and "Mauo" not in clue.line.split(name)[0]
    assert clue.line == clue.learned and not clue.line.startswith(store.state.entities[core].name)  # no speaker
    ordinary = [a for a in out if a.willingness]
    assert [a.part for a in ordinary] == [0]
    assert cases(store.state)[_case(store)["id"]]["nodes"][0].get("found")


def test_c2_three_questions_at_limited_reach_clue_third_is_delivered(tmp_path: Path) -> None:
    """edge C2: deliver_count(3, 1) = 1, which used to drop the third part before the clue check saw it."""
    store, core, sub = _duel(tmp_path)
    parts = [_part("When does the kitchen close?"), _part("How much for a bed?"),
             _part("Who is the stranger that started the fight?", "who_is")]
    out, _ = _msg(store, core, parts, 1, [{"about": "1", "part": "3"}])
    assert sum(a.willingness is None for a in out) == 1 and sum(a.willingness is not None for a in out) == 1
    assert [a.part for a in out if a.willingness] == [0]
    assert ans.deliver_count(2, 1) == 1


def test_c3_one_clue_call_per_message_whatever_the_parts(tmp_path: Path) -> None:
    store, core, _ = _duel(tmp_path)
    parts = [_part(f"Question number {i}?") for i in range(4)]
    out, model = _msg(store, core, parts, 3, [{"about": "none", "part": "none"}])
    assert len(_clue_calls(model)) == 1 and all(a.willingness for a in out)
    # an ask() of one question is a one-part message: still one call
    model2 = ScriptedModel({Role.CLUE: [{"about": "none", "part": "none"}]})
    with turn(store, model2) as ctx:
        ans.ask(ctx, core, "what_is", None, "Is the soup good?", pc=PC)
    assert len(_clue_calls(model2)) == 1


def test_c4_a_question_that_sounds_like_the_clue_but_is_not(tmp_path: Path) -> None:
    store, core, sub = _duel(tmp_path)
    parts = [_part("Who has the evening prayers at the shrine?"), _part("Where is the privy?")]
    out, _ = _msg(store, core, parts, 2, [{"about": "none", "part": "none"}])
    assert all(a.willingness and a.fact_id is None and a.pointer is None for a in out)
    assert not _case(store)["nodes"][0].get("found")
    assert not cases(store.state)[_case(store)["id"]]["nodes"][0].get("found")


def test_c5_an_unfriendly_holder_delivers_the_clue_as_the_second_part(tmp_path: Path) -> None:
    store, core, sub = _duel(tmp_path)
    _standing(store, core, -2)
    parts = [_part("Is the ale watered?"), _part("Who is that swordsman really?", "who_is")]
    out, _ = _msg(store, core, parts, 1, [{"about": "1", "part": "2"}])
    assert any(a.willingness is None and a.fact_id for a in out)


def test_c6_a_clue_already_found_is_not_delivered_again(tmp_path: Path) -> None:
    """edge C6: once a case is wholly found there is no open clue: no judgment call, no learned line."""
    from engine.gen.case import mark_found

    store, core, sub = _duel(tmp_path)
    out, _ = _msg(store, core, [_part("Who is the challenger?", "who_is")], 2, [{"about": "1", "part": "1"}])
    assert any(a.learned for a in out)
    case = _case(store)
    with turn(store) as ctx:
        mark_found(ctx.need_tx(), case["id"], case["nodes"][1]["id"])
    out, model = _msg(store, core, [_part("Is the roast good?"), _part("And who is the challenger again?", "who_is")],
                      2, [{"about": "1", "part": "2"}])
    assert not _clue_calls(model)
    assert not any(a.learned for a in out)


def test_c7_a_non_holder_points_to_the_holder_as_a_fact(tmp_path: Path) -> None:
    store, core, sub = _duel(tmp_path)
    other = next(i for i in sorted(store.state.entities) if i.startswith("npc.") and i not in (core, sub)
                 and store.state.entities[i].data.get("depth") != "walk_on")
    out, _ = _msg(store, other, [_part("Who is the challenger?", "who_is")], 2, [{"about": "1", "part": "1"}])
    a = out[0]
    assert a.willingness is None and a.pointer and "would" in a.learned and a.fact_id
    assert not cases(store.state)[_case(store)["id"]]["nodes"][0].get("found")


def _record(parts: list[PartEntry]) -> AdjudicationRecord:
    return AdjudicationRecord(pc=PC, parts=parts)


def _speech(text: str, kind: str = "what_is", topic: str | None = None) -> PartEntry:
    return PartEntry.model_validate({"text": text, "class": "SPEECH", "question_kind": kind, "topic": topic})


def test_c8_c9_plain_speech_delivers_a_learned_fact_and_stamps_only_what_it_delivered(tmp_path: Path) -> None:
    """made-up C8 / edge C9: no Talk beat; the clue is on `record.learned` (the handle renders it as a learned item);
    no NPC "acts:" entry names a speaker for it; only the part that delivered a fact is answered."""
    store, core, sub = _duel(tmp_path)
    parts = [_speech("What are the banners?"), _speech("And who is the young man really?", "who_is")]
    rec = _record(parts)
    model = ScriptedModel({Role.CLUE: [{"about": "1", "part": "2"}]})
    with turn(store, model) as ctx:
        out = world_step._speech_answers(ctx, rec, [], parts, [core], PC)
    name = store.state.entities[sub].name
    assert out and rec.learned and name in rec.learned[0]
    assert not any(name in a.action for a in rec.npc_actions)  # the clue is not an NPC act
    assert [a.tags for a in rec.npc_actions if any(t.startswith("willingness") for t in a.tags)]  # the banners part
    assert parts[1].handled == "answered" and parts[0].handled != "answered"
    its = record_items(rec)
    assert any(i.kind == "learned" and i.must_name and name in i.text for i in its)


def test_c9_a_talk_beat_carries_the_clue_in_its_learned_line(tmp_path: Path) -> None:
    store, core, sub = _duel(tmp_path)
    parts = [_speech("Is the ale watered?"), _speech("And who is that swordsman really?", "who_is")]
    rec = _record(parts)
    e = BeatEntry(restatement="ask the innkeeper", targets=[core], approach_words="verb.talk", verb="verb.talk",
                  reach="standard")
    b = SimpleNamespace(entry=e, status="no_roll", frame_id=None)
    model = ScriptedModel({Role.CLUE: [{"about": "1", "part": "2"}]})
    with turn(store, model) as ctx:
        world_step.deliver_learning(ctx, rec, [b])
    name = store.state.entities[sub].name
    assert e.learned and name in e.learned[0] and not rec.learned
    assert parts[1].handled == "answered" and parts[0].handled != "answered"


def test_c10_a_typed_who_part_and_an_ordinary_part(tmp_path: Path) -> None:
    """edge C10: "who are you?" is answered by name with no judgment of its own; the cap counts the ordinary parts."""
    store, core, _ = _duel(tmp_path)
    parts = [_part("Who are you?", "who_is"), _part("Is the ale watered?"), _part("Is the roast good?")]
    out, model = _msg(store, core, parts, 1, [{"about": "none", "part": "none"}])
    assert out[0].part == 0 and store.state.entities[core].name in out[0].line and out[0].willingness is None
    assert sum(a.willingness is not None for a in out) == 1  # deliver_count(2, Limited) = 1 ordinary answer
    assert len(_clue_calls(model)) == 1 and "Who are you" not in _clue_calls(model)[0]


def test_the_offline_clue_stub_names_the_part() -> None:
    """The offline double reads a multi-question message: the clue and the question that asks it."""
    from engine.dm.roles.clue import message
    from engine.llm.base import Packet
    from engine.llm.offline import _clue

    pk = Packet(instructions="", core="", cards=[], view="", exchanges=[], message=message(
        ["Is the bread fresh?", "Whose child is gone missing?"], [("who is missing (the matter: a child is missing)", True)]))
    assert _clue({}, pk) == {"about": "1", "part": "2"}


# ------------------------------------------------------------------------------------------- the journal


def _journal_world(tmp_path: Path) -> tuple[Any, str]:
    store = new_store(tmp_path)
    with store.transaction() as tx:
        tx.add(entity("place", "Longfield", tx=tx, data={"place_kind": "settlement"}))
        tx.add(entity("pc", "Wren", tx=tx, quantities={"vitality": (10, 0, 10)}))
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity="pc.wren", location="loc.longfield"))
        tx.add(entity("place", "The Long Downs", tx=tx, data={"place_kind": "region", "desc": "a fallen realm: a kingdom broke "
                                                              "two generations ago"}))
        tx.add(entity("thread", "The wound", tx=tx, data={"thread_kind": "situation", "status": "active", "text":
                      "a realm that fell in a single bad winter, and the roads, keeps and heirs remain"}))
        tx.add(entity("npc", "Betric Marsh", tx=tx, data={"role": "innkeeper"}))
        tx.add(entity("npc", "Baker Haldor", tx=tx, data={"role": "baker"}))
        tx.add(entity("npc", "Anwen", tx=tx, data={"role": "miller's daughter"}))
    return store, "pc.wren"


def _say(store: Any, speaker: str, words: str, about: list[str] | None = None) -> None:
    ctx = TurnContext.for_store(store, model=OfflineModel())
    with store.transaction() as tx:
        ctx.tx = tx
        try:
            tm.add_said(ctx, [{"speaker": speaker, "words": words, "about": about or [], "question": None}])
        finally:
            ctx.tx = None


def test_p5_what_do_i_know_about_the_winter_and_the_banners(tmp_path: Path) -> None:
    """playtest P5 (explorer [19]-[21]): the compound is split; the thread is found by its text; Betric's words are
    under "what you were told", attributed; no "Nothing on record"."""
    store, _ = _journal_world(tmp_path)
    _say(store, "npc.betric_marsh", "The banners are the old colours of the Long Downs, from before the winter that "
         "brought the realm down.")
    text = what_you_know(store.state, "the Long Downs and the winter that brought the realm down").text
    assert "Nothing on record" not in text
    assert "single bad winter" in text  # the thread, matched by its text and not its cut name
    assert "What you were told" in text and 'Betric Marsh told you: "The banners are the old colours' in text
    assert "a fallen realm" in text  # the place by its alias still shows


def test_j1_the_bakers_word_is_under_the_millers_daughter(tmp_path: Path) -> None:
    store, _ = _journal_world(tmp_path)
    _say(store, "npc.baker_haldor", "I saw the miller's daughter leave with a tinker at dusk.", ["npc.anwen"])
    for q in ("Anwen", "the miller's daughter"):
        text = what_you_know(store.state, q).text
        assert 'Baker Haldor told you: "I saw the miller' in text and "tinker" in text, q


def test_j2_x_and_y_are_split_and_each_piece_is_searched(tmp_path: Path) -> None:
    store, _ = _journal_world(tmp_path)
    _say(store, "npc.baker_haldor", "The mill has stood idle since the autumn.", [])
    _say(store, "npc.betric_marsh", "The wound in the realm is why the roads are bad.", [])
    text = what_you_know(store.state, "the mill and the wound").text
    assert "idle since the autumn" in text and "single bad winter" in text and "roads are bad" not in text.split(
        "What you were told")[0]


def test_j3_two_speakers_who_contradict_are_both_shown_attributed(tmp_path: Path) -> None:
    store, _ = _journal_world(tmp_path)
    _say(store, "npc.baker_haldor", "The miller's daughter left with a tinker.", [])
    _say(store, "npc.betric_marsh", "The miller's daughter never left; she is in the loft.", [])
    text = what_you_know(store.state, "the miller's daughter").text
    assert "Baker Haldor told you" in text and "Betric Marsh told you" in text
    assert "you cannot say" in text  # testimony, never a verdict


def test_j4_nothing_known_nothing_told_keeps_the_old_answer(tmp_path: Path) -> None:
    store, _ = _journal_world(tmp_path)
    text = what_you_know(store.state, "the sunken bell").text
    assert text.startswith("[JOURNAL] Nothing on record about the sunken bell")


def test_j5_a_name_that_contains_and_is_not_split(tmp_path: Path) -> None:
    store = new_store(tmp_path)
    with store.transaction() as tx:
        tx.add(entity("pc", "Wren", tx=tx, quantities={"vitality": (10, 0, 10)}))
        tx.add(entity("place", "Hall and Keep", tx=tx, data={"place_kind": "building", "desc": "an old strong hall"}))
    text = what_you_know(store.state, "Hall and Keep").text
    assert "Hall and Keep" in text and "Nothing on record" not in text


def test_the_general_journal_lists_what_you_were_told(tmp_path: Path) -> None:
    from engine.dm.codex import journal

    store, _ = _journal_world(tmp_path)
    _say(store, "npc.betric_marsh", "The ford floods after rain.", [])
    assert "Betric Marsh told you" in journal(store.state).text
    assert "Betric Marsh told you" in what_you_know(store.state).text


# ------------------------------------------------------------------------------------------- misc


def test_a_term_card_line_is_never_cut_by_the_card() -> None:
    rec = world(SEED).record
    t = {"kind": "x", "label": "a very long label for a card heading that goes on", "fields": [["what", "w" * 400]],
         "task": None, "pay": None}
    assert all(len(ln) <= 150 for ln in card_lines(rec, t))


def test_a_found_letter_is_a_document_at_the_pcs_place_whose_words_are_its_text(tmp_path: Path) -> None:
    store = store_for_world(tmp_path, world(SEED))
    t = _inject(store, 3)
    st = store.state
    assert t["where"] == st.positions["pc.wren"].location and st.positions[t["doc"]].location == t["where"]
    assert "It concerns" in str(written_words(st, t["doc"]))
