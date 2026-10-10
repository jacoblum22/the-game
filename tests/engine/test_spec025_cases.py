"""Spec 025: the made-up and edge cases of `specs/025-hooks-clues-willingness/cases.md` (labelled there, committed
before implementing). T2 hook terms and guards; D2 A clue judgment; D3 A willingness held for the scene; the typed
deal price; P3. The clue judgment's model is scripted here; its live precision and recall are measured on Haiku by
`specs/025-hooks-clues-willingness/clue_eval.py`."""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from engine.data.loader import load_rules
from engine.dm import answer as ans
from engine.dm import testimony as tm
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, PartEntry
from engine.dm.npc_layer import respond
from engine.dm.roles.director import DirectorDecision, NextScene, frame_scene
from engine.dm.roles.narrator import speaker_cards
from engine.gen.case import about_line, cases
from engine.gen.hooks import hook_terms, job_fee
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.resolve.change import DEAL, deal_price, pay_deal
from engine.store.events import Event
from engine.world.common import fact, meta
from engine.world.places import location, move, reachable
from engine.world.scenes import end_scene, start_scene
from tests.engine.test_answer import PC, here, turn
from tests.fixtures.seeded import seeded_store

RULES = load_rules()
OFFER, REFUGEES, MISSING = 6, 10, 21  # rolled seeds whose incident is an offer, refugees, a missing person


def _case(store: Any) -> dict[str, Any]:
    return next(c for c in cases(store.state).values() if c.get("trigger") == "incident")


def _core(case: dict[str, Any]) -> str:
    return next(p["holder"] for p in case["nodes"][0]["placements"] if p["access"] == "core")


def _card(store: Any, npc: str, key: str | None = None) -> str:
    rec = AdjudicationRecord(pc=PC)
    rec.npc_actions.append(_line(npc, key or f"{npc}|what_happened|local_news"))
    return "\n".join(speaker_cards(store.state, rec, RULES))


def _line(npc: str, key: str) -> Any:
    from engine.dm.adjudication import NpcActionEntry

    return NpcActionEntry(npc=npc, action="answers", source="talk_outcome", source_ref="PR-12-10", tags=[f"ask:{key}"])


def _standing(store: Any, npc: str, value: int) -> None:
    with turn(store) as ctx:
        ctx.need_tx().add(Event.of("relationship_set", source="test", rule_id="12.11.2", a=npc, b=PC, kind="standing",
                                   value=value, new_value=value, reason="test"))


def _scene(store: Any) -> None:
    with turn(store) as ctx:
        if ctx.state.scene is not None:
            end_scene(ctx.time_ctx(), "test")
        start_scene(ctx.time_ctx(), place=location(ctx.state, PC), mode="free", agenda="test")


def _ask(store: Any, npc: str, text: str, clue: Any = "none", kind: str = "what_happened",
         topic: str | None = None, record: Any = None, beats: Any = ()) -> tuple[ans.Answer, ScriptedModel]:
    model = ScriptedModel({Role.CLUE: [{"about": clue}] * 4})
    with turn(store, model) as ctx:
        a = ans.ask(ctx, npc, kind, topic, text, pc=PC, record=record, beats=beats)
    return a, model


def _clue_calls(model: ScriptedModel) -> list[str]:
    return [p.message for r, p in model.calls if r == Role.CLUE]


# ------------------------------------------------------------------------------------------- T2: hook terms


def test_c1_bounty_terms_are_written_and_last_seen_is_improvised(tmp_path: Path) -> None:
    """made-up C1: the missing person's bounty: pay (a job fee), issuer and contact written as the reporter's
    knowledge; "where was he last seen" has no term (the reporter answers in words)."""
    store = seeded_store(tmp_path, MISSING)[0]
    case = _case(store)
    t = hook_terms(store.state)["thr.lead_1"]
    assert t["kind"] == "missing" and t["pay"] == job_fee(1) and t["issuer"].endswith(".rulers")
    card = _card(store, _core(case))
    assert f"pay: {job_fee(1)} coins" in card and "posted by:" in card and "last seen" not in card
    notice = next(p["holder"] for p in case["nodes"][0]["placements"] if p["holder_kind"] == "document")
    text = str(store.state.fact_value(notice, "text"))
    assert not re.search(r"\d|silver|gold", text), text  # the notice names no figure the purse could disagree with


def test_c1_a_seeded_bounty_notice_has_a_typed_reward(tmp_path: Path) -> None:
    """made-up C1 (a posted notice, no case behind it): "a fair reward in coin" on the notice; the contact it names
    holds the figure (a job fee), the same for anyone who asks him."""
    store = seeded_store(tmp_path, 8)[0]
    t = hook_terms(store.state)["doc.notice"]
    assert t["kind"] == "bounty" and t["pay"] == job_fee(1) and t["contact"] in t["know"]
    assert f"pay: {job_fee(1)} coins" in _card(store, t["contact"])


def test_c12_a_hire_with_no_stated_pay_has_a_typed_fee(tmp_path: Path) -> None:
    """made-up C12: the hire notice says only "Good coin"; the contact's card holds the job fee and the place; every
    knower holds the same figure."""
    store = seeded_store(tmp_path, OFFER)[0]
    t = next(x for x in hook_terms(store.state).values() if x["kind"] == "hire")
    assert t["pay"] == job_fee(t["band"]) and t["destination"] in store.state.entities
    for k in t["know"]:
        card = _card(store, k)
        assert f"pay: {t['pay']} coins" in card and store.state.entities[t["destination"]].name in card
    leads = [str(x["lead"]) for x in store.state.meta["world.opening"]["leads"]]
    assert not any("asks no questions" in x or "only the beginning" in x for x in leads)  # data, not sentences


def test_c17_c20_the_offers_reporter_has_pay_and_place_never_the_issuer(tmp_path: Path) -> None:
    """playtest C17 / edge C20 (fighter, Magby): the offer's reporter knows the work, the pay and the place; the
    issuer is the case's sealed answer and is on no card; "who is paying?" is judged about the held clue and the
    case delivers it."""
    store = seeded_store(tmp_path, OFFER)[0]
    case = _case(store)
    core = _core(case)
    t = hook_terms(store.state)["thr.lead_1"]
    card = _card(store, core)
    assert f"pay: {t['pay']} coins" in card and "where:" in card and "work:" in card
    issuer = store.state.entities[case["solution"]["subject"]["id"]].name
    assert issuer not in card
    a, model = _ask(store, core, "Who is really paying for this?", clue="1")
    assert a.fact_id and issuer in a.line and "1*:" in _clue_calls(model)[0]
    assert cases(store.state)[case["id"]]["nodes"][0].get("found")


def test_officer_role_is_data(tmp_path: Path) -> None:
    store = seeded_store(tmp_path, OFFER)[0]
    roles = [str(e.data.get("role")) for e in store.state.entities.values() if e.kind == "npc"]
    assert "officer" in roles and not any(r.startswith("officer of") for r in roles)


# ------------------------------------------------------------------------------------------- D2 A: clues


def test_c2_c9_a_question_judged_about_a_held_clue_is_delivered(tmp_path: Path) -> None:
    """made-up C2 / edge C9: the holder (here Guarded by standing) is asked a question that shares no word with the
    clue; judged yes; delivered, with no willingness line; the authored about line is what the judge reads."""
    store = seeded_store(tmp_path, MISSING)[0]
    case = _case(store)
    core = _core(case)
    _standing(store, core, -1)
    with turn(store) as ctx:  # the widow's clue, authored: what a question must be about to reach it
        c = dict(cases(store.state))
        c[case["id"]]["nodes"][0]["placements"][0]["about"] = "who had cause to want him gone (his debts and quarrels)"
        ctx.need_tx().add(meta("world.cases", c, "test"))
    a, model = _ask(store, core, "Did he have enemies?", clue="1")
    sent = _clue_calls(model)[0]
    assert "1*: who had cause to want him gone" in sent and case["solution"]["subject"]["words"] not in sent
    assert a.fact_id and a.willingness is None and cases(store.state)[case["id"]]["nodes"][0].get("found")


def test_c4_c14_judged_no_nothing_leaks(tmp_path: Path) -> None:
    """edge C4 / C14: a question about the weather, and one that sounds like the clue but is not: judged none; no
    delivery, no pointer; an ordinary willingness line."""
    store = seeded_store(tmp_path, REFUGEES)[0]
    case = _case(store)
    core = _core(case)
    for q in ("Is the river high at the ferry this week?", "Who leads the evening prayers at the temple?"):
        a, _ = _ask(store, core, q, clue="none")
        assert a.willingness and a.fact_id is None and a.pointer is None
        assert case["nodes"][0]["fact"].split(":", 1)[1].strip() not in a.line
    assert not cases(store.state)[case["id"]]["nodes"][0].get("found")


def test_c15_an_unfriendly_holder_still_delivers(tmp_path: Path) -> None:
    """edge C15: standing -2 does not block a core clue (willingness never overrides the clue rules)."""
    store = seeded_store(tmp_path, REFUGEES)[0]
    case = _case(store)
    core = _core(case)
    _standing(store, core, -2)
    a, _ = _ask(store, core, "Who speaks for the people who came in?", clue="1")
    assert a.fact_id and a.willingness is None


def test_c16_signed_is_not_the_sign(tmp_path: Path) -> None:
    """playtest C16 (talker turn.9): a non-holder asked "Have you signed with Morri's Wolves?": judged none, so no
    case pointer line."""
    store = seeded_store(tmp_path, 25)[0]  # an omen: the subject is "a sign of ..."
    case = _case(store)
    holders = {p["holder"] for n in case["nodes"] for p in n["placements"]}
    other = next(i for i, e in sorted(store.state.entities.items()) if e.kind == "npc" and i not in holders
                 and not e.data.get("power") and not e.data.get("group"))
    a, model = _ask(store, other, "Have you signed with Morri's Wolves, or are you still looking for work?")
    assert a.fact_id is None and a.willingness and "does not know" not in a.line  # no case pointer line
    assert _clue_calls(model) and "*" not in _clue_calls(model)[0].split("\n", 2)[2]  # not a holder


def test_about_line_never_names_the_answer(tmp_path: Path) -> None:
    store = seeded_store(tmp_path, REFUGEES)[0]
    case = _case(store)
    for n in case["nodes"]:
        line = about_line(store.state, case, n)
        assert n["fact"].split(":", 1)[1].strip() not in line and "the matter:" in line


# ------------------------------------------------------------------------------------------- D3 A: willingness


def _rolls(store: Any) -> int:
    return len([e for e in store.events(types=["table_rolled"])])  # type: ignore[attr-defined]


def test_c22_the_band_holds_for_the_scene_and_a_new_scene_decides_afresh(tmp_path: Path) -> None:
    """edge C22: an Unfriendly NPC asked two questions in one scene: one decision (one table roll), the same band;
    a new scene decides again."""
    store = seeded_store(tmp_path, REFUGEES)[0]
    case = _case(store)
    holders = {p["holder"] for n in case["nodes"] for p in n["placements"]}
    npc = next(n for n in here(store) if n not in holders)
    _scene(store)
    _standing(store, npc, -2)
    before = _rolls(store)
    a1, _ = _ask(store, npc, "Where can I get a meal?", topic="goods")
    a2, _ = _ask(store, npc, "What's the weather doing?", topic="weather")
    assert a1.willingness == a2.willingness and _rolls(store) == before + 1
    _scene(store)
    _ask(store, npc, "Where can I get a meal?", topic="goods")
    assert _rolls(store) == before + 2


def _talk(npc: str, degree: str = "success", pressure: str = "none", status: str = "resolved") -> Any:
    entry = BeatEntry(restatement="talk them round", verb="verb.talk", targets=[npc], approach_words="verb.talk",
                      degree=degree if status == "resolved" else None, rolled=status == "resolved")
    return SimpleNamespace(entry=entry, frame_id=None, status=status)


def test_c23_a_won_persuasion_holds_willing(tmp_path: Path) -> None:
    """edge C23: unwilling, then a won persuasion (success at a cost counts): willing for the rest of the scene."""
    store = seeded_store(tmp_path, REFUGEES)[0]
    npc = here(store)[-1]
    _scene(store)
    with turn(store) as ctx:
        ans._hold(ctx, npc, "unwilling", "unfriendly toward you")
    beat = _talk(npc)
    beat.entry.degree, beat.entry.success_at_cost = "failure", True
    with turn(store) as ctx:
        assert ans.willingness(ctx, npc, AdjudicationRecord(pc=PC), [beat])[0] == "willing"
    with turn(store) as ctx:
        assert ans.willingness(ctx, npc)[0] == "willing"  # held, no talk this turn


def test_c7_payment_moves_the_band_a_refusal_stays_on_its_topic(tmp_path: Path) -> None:
    """edge C7: Guarded; a payment moves the band up; a new topic does not re-roll; a recorded refusal (here: never
    lends coin) still refuses that topic only."""
    from engine.dm.npc_layer import motive_tags  # noqa: F401  (the tags the refusal is matched by)

    store = seeded_store(tmp_path, REFUGEES)[0]
    npc = here(store)[-1]
    _scene(store)
    with turn(store) as ctx:
        ans._hold(ctx, npc, "guarded", "wary toward you")
        assert ans.step_band(ctx, npc, 1, "paid")[0] == "willing"
    before = _rolls(store)
    a, _ = _ask(store, npc, "What's the price of salt?", topic="prices")
    assert a.willingness == "willing" and _rolls(store) == before
    with turn(store) as ctx:
        ctx.need_tx().add(fact(ctx.need_tx(), npc, "refusals", [{"kind": "refusal.lend", "text": "never lends coin"}],
                               rule_id="test", visibility="sealed"))
    store.state.frames["frame.t"] = SimpleNamespace(frame={"asks": "asks_loan", "beat": {  # type: ignore[assignment]
        "verb": "verb.talk", "pressure": "request"}})
    loan = SimpleNamespace(entry=BeatEntry(restatement="ask for a loan", verb="verb.talk", targets=[npc]),
                           frame_id="frame.t", status="unresolved")
    rec = AdjudicationRecord(pc=PC, parts=[PartEntry.model_validate({"text": "Lend me coin?", "class": "SPEECH"})])
    with turn(store) as ctx:
        assert ans.willingness(ctx, npc, rec, [loan])[0] == "unwilling"
        assert ans.willingness(ctx, npc)[0] == "willing"  # the band itself is untouched


def test_c5_c11_c18_a_refusal_points_to_someone_new_never_back(tmp_path: Path) -> None:
    """edge C5 / C11 / playtest C18: an unwilling answer names one new person who would know; never the asked, never
    anyone who refused on the topic; when everyone has refused, no pointer at all."""
    store = seeded_store(tmp_path, REFUGEES)[0]
    _scene(store)
    people = here(store)
    first, second = people[0], people[1]
    for n in (first, second):
        with turn(store) as ctx:
            ans._hold(ctx, n, "unwilling", "unfriendly toward you")
    a1, _ = _ask(store, first, "Which road is safest?", topic="roads")
    assert a1.willingness == "unwilling"
    a2, _ = _ask(store, second, "Which road is safest?", topic="roads")
    assert a2.pointer not in (first, second) and (a2.pointer is None or "names one person" in a2.line)
    with turn(store) as ctx:  # everyone who would know has refused
        idx = dict(ctx.state.meta.get(ans.INDEX) or {})
        for n in [i for i, e in ctx.state.entities.items() if e.kind == "npc"]:
            idx[f"{n}|where_is|roads"] = {"willingness": "unwilling", "reason": "x", "said": []}
        ctx.need_tx().add(meta(ans.INDEX, idx, "test"))
        assert ans.refusal_pointer(ctx, second, "roads", None) is None


def test_c8_thanks_gets_no_willingness_line(tmp_path: Path) -> None:
    """edge C8 (P3): "Thanks, friend." to the one present: no willingness line, no refusal voicing."""
    store = seeded_store(tmp_path, REFUGEES)[0]
    npc = here(store)[0]
    rec = AdjudicationRecord(pc=PC, parts=[PartEntry.model_validate({"text": "Thanks, friend.", "class": "SPEECH"})])
    with turn(store) as ctx:
        respond(ctx, rec, [])
    assert not [a for a in rec.npc_actions if a.npc == npc and a.source_ref == "PR-12-10"]
    assert not any(a.action.startswith("refuses") for a in rec.npc_actions)


# ------------------------------------------------------------------------------------------- deals and guards


def test_c6_c21_a_spoken_price_settles_from_the_band() -> None:
    """edge C6 / C21: "ten silver for the map" (an R2 ask) pays the band's ceiling 5; 3 inside the band stays 3;
    nothing stated: the floor."""
    assert deal_price(RULES, "R2", 10) == 5 and deal_price(RULES, "R2", 3) == 3 and deal_price(RULES, "R2", None) == 2


def test_c19_buying_a_cup_is_a_typed_deal(tmp_path: Path) -> None:
    """made-up C19: "Let me buy you a cup" (offer, no amount, no roll) accepted: 1 coin leaves the purse with a price
    record; the talk moved them."""
    store = seeded_store(tmp_path, REFUGEES)[0]
    npc = here(store)[0]
    with turn(store) as ctx:
        ctx.need_tx().add(Event.of("quantity_defined", source="test", rule_id="08.8.1", entity=PC, quantity="coin",
                                   value={"current": 10}, reason="test purse"))
    beat = _talk(npc, status="no_roll")
    beat.entry.restatement = "offer to buy them a cup"
    rec = AdjudicationRecord(pc=PC, parts=[PartEntry.model_validate({"text": "Let me buy you a cup.",
                                                                     "class": "SPEECH"})])
    with turn(store) as ctx:
        respond(ctx, rec, [beat])
        assert ans.willingness(ctx, npc, rec, [beat])[0] == "willing"
    st = store.state
    assert st.quantities[PC]["coin"].current == 9
    assert st.fact_value(npc, DEAL) == {"payer": PC, "payee": npc, "kind": "coin", "amount": 1, "due": "now",
                                        "paid": 1}


def test_pay_deal_never_below_zero(tmp_path: Path) -> None:
    store = seeded_store(tmp_path, REFUGEES)[0]
    npc = here(store)[0]
    with turn(store) as ctx:
        evs = pay_deal(ctx.need_tx(), PC, npc, 5)  # no purse: the record says nothing was paid
    assert len(evs) == 1 and evs[0].payload.value["paid"] == 0  # type: ignore[attr-defined]


def test_c10_a_speaker_sees_what_others_said_on_the_topic(tmp_path: Path) -> None:
    """made-up C10: the keeper said where he was last seen; the widow, asked the same, sees it on her card."""
    store = seeded_store(tmp_path, REFUGEES)[0]
    keeper, widow = here(store)[0], here(store)[1]
    with turn(store) as ctx:
        tm.add_said(ctx, [{"speaker": keeper, "words": "Last I saw him he was taking a fare across at dusk.",
                           "question": f"{keeper}|where_is|travellers"}])
    card = _card(store, widow, f"{widow}|where_is|travellers")
    assert "others have said on this" in card and "taking a fare across at dusk" in card
    assert "others have said" not in _card(store, keeper, f"{keeper}|where_is|travellers")


def test_c3_the_director_casts_the_refugees(tmp_path: Path) -> None:
    """made-up C3: the refugees are a group from the seed on; a scene at the temple with `cast_described: ["the
    refugees"]` has them present (never a random walk-on)."""
    store = seeded_store(tmp_path, REFUGEES)[0]
    group = next(i for i, e in store.state.entities.items() if e.data.get("group"))
    temple = next(i for i, e in store.state.entities.items() if e.kind == "place" and i.endswith((".temple", ".shrine")))
    before = {i for i, e in store.state.entities.items() if e.kind == "npc"}
    with turn(store) as ctx:
        ctx.need_tx().add(Event.of("position_set", source="test", rule_id="10.1.1", entity=PC, location=temple))
        d = DirectorDecision(next_scene=NextScene(place=temple, agenda="hear the refugees' story",
                                                  cast=["new_npc"], cast_described=["the refugees"]))
        frame_scene(ctx, d, reason="test")
    sc = store.state.scene
    assert store.state.positions[group].location == temple and sc is not None and group in sc.cast_present
    assert {i for i, e in store.state.entities.items() if e.kind == "npc"} == before  # no walk-on made
    with turn(store) as ctx:  # a description nobody fits: a new group, by that label
        d = DirectorDecision(next_scene=NextScene(place=temple, agenda="the carters", cast_described=["the carters"]))
        end_scene(ctx.time_ctx(), "test")
        frame_scene(ctx, d, reason="test")
    carters = [i for i, e in store.state.entities.items() if e.data.get("group") and e.data.get("role") == "carters"]
    assert carters and store.state.positions[carters[0]].location == temple


def test_c13_a_place_heard_in_speech_becomes_a_site_on_travel(tmp_path: Path) -> None:
    """made-up C13: "up at the healer's croft", known only by name: reachable from town; on arrival a building of
    the settlement; a true settled claim that the refugees are there puts them there."""
    from engine.dm.mentions import write_mentions

    store = seeded_store(tmp_path, REFUGEES)[0]
    with turn(store) as ctx:
        write_mentions([{"kind": "place", "name": "the healer's croft"}], tx=ctx.need_tx(), rules=RULES, rng=ctx.rng)
    croft = next(i for i, e in store.state.entities.items() if e.name == "healer's croft")
    here_ = location(store.state, PC)
    assert croft in {x.to for x in reachable(store.state, here_)}
    with turn(store) as ctx:
        arrival = move(ctx.time_ctx(), croft)
    assert arrival.arrived and store.state.fact_value(croft, "place.place_kind") == "building"
    assert location(store.state, PC) == croft and here_ in {x.to for x in reachable(store.state, croft)}
    group = next(i for i, e in store.state.entities.items() if e.data.get("group"))
    with turn(store) as ctx:
        tm._place_there(ctx.need_tx(), group, "up at the healer's croft")
    assert store.state.positions[group].location == croft


def test_a_price_claim_never_settles_as_a_figure(tmp_path: Path) -> None:
    store = seeded_store(tmp_path, REFUGEES)[0]
    npc = here(store)[0]
    with turn(store) as ctx:
        sid = tm.add_said(ctx, [{"speaker": npc, "words": "The map is ten silver, no less."}])[0]
    model = ScriptedModel({Role.TESTIMONY: [{"kind": "claim", "subject": "the map", "predicate": "costs",
                                             "value": "ten silver"}]})
    with turn(store, model) as ctx:
        assert tm.settle(ctx, sid) is None
    assert tm.get(store.state, sid)["route"] == "price_band"  # type: ignore[index]
