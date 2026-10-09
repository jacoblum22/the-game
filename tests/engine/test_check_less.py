"""Spec 011, check less (R2-G checklist items 1-11; 12.3.1b, DL-12-80..83, DL-12-87, DL-01-29, DL-01-33).

Only narrator-voice claims on the blocking list with a certain subject block; speech is testimony; incidental
clashes are logged; I-159 (one model-chosen modifier per beat), I-160(a) (zero reach is G4), I-176 (tags match
wants and refusals; the crowd's response is the place's scene fact)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

from engine.audit.claims import Claim, Verdict, blocking, certain, check_claims
from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, PartEntry
from engine.dm.turn import play_turn
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.store.events import EntityRecord, Event
from engine.store.views import name_known
from tests.engine.test_rubric import frame, ok
from tests.engine.test_rubric import s as s  # noqa: F401  (the fixture)
from tests.engine.test_turn_adjudication import QUIET_WORLD, SNEAK, framer, reader, rolls, setup
from tests.engine.test_turn_narration import _decl, _must, calls, look_model

RULES = load_rules()
PROMPT = "What do you do?"


def _say(*sents: dict[str, Any]) -> Any:
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        out = [dict(x) for x in sents]
        out[0]["refs"] = _must(packet)
        return {"sentences": [*out, _decl(PROMPT)]}
    return draft


def _item(tx: Any, eid: str, name: str, place: str) -> None:
    tx.add(Event.of("entity_created", source="test", entity=EntityRecord(id=eid, kind="item", name=name)))
    tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity=eid, location=place))


# ------------------------------------------------------------------------------------------- item 4: certainty


def test_two_swords_get_no_verdict_in_either_direction(tmp_path: Path) -> None:
    """DL-12-82, the owner's example: a red and a green sword in scope; "the sword is green" names neither
    certainly, so the claim is neither contradicted (about the red one) nor supported (about the green one)."""
    dock, _ = setup(tmp_path, look_model())
    with dock.store.transaction() as tx:
        _item(tx, "item.red_sword", "red sword", dock.place)
        _item(tx, "item.green_sword", "green sword", dock.place)
    st = dock.store.state
    text = {0: "The sword is green."}
    scope = ["item.red_sword", "item.green_sword"]
    for sword in scope:
        c = Claim.model_validate({"subject": sword, "class": "identity", "predicate": "colour", "value": "green"})
        [v] = check_claims([c], st, AdjudicationRecord(), scope, rules=RULES, texts=text)
        assert v.uncertain and v.disposition == "no_verdict" and v.fix is None
    assert not certain(st, "item.red_sword", "The sword is green.", scope=scope)
    assert certain(st, "item.red_sword", "The red sword lies on the stair.", scope=scope)  # a whole name, unique
    assert certain(st, dock.pc, "You stand at the stair.", pc=dock.pc)  # the PC is always certain


# ------------------------------------------------------------------------------------------- item 3: blocking list


def test_blocking_list_classes_block_and_others_log_only() -> None:
    def blocks(cls: str, verdict: str = "contradicted", predicate: str = "is", value: str = "x") -> bool:
        c = Claim.model_validate({"subject": "npc.x", "class": cls, "predicate": predicate, "value": value})
        return blocking(c, Verdict(claim=0, verdict=verdict), RULES)  # type: ignore[arg-type]
    assert all(blocks(c) for c in ("outcome", "capability", "harm_condition", "quantity", "position", "existence",
                                    "sealed"))
    assert blocks("possession", value="a sword") and blocks("identity", predicate="name", value="Odo")
    assert blocks("attitude", "pc_agency") and blocks("attitude", "leak")
    assert not blocks("attitude") and not blocks("knowledge") and not blocks("action") and not blocks("clock")
    assert not blocks("possession", value="a clay cup")  # who holds a cup is not on the list
    assert not blocks("identity", predicate="gender", value="woman")  # identity blocks for a name only


def test_a_pronoun_clash_on_a_certain_subject_now_redrafts(tmp_path: Path) -> None:
    """Spec 011 logged a pronoun clash; spec 016 (12.3.2 "Precision, not class", DL-12-95) makes the pronoun of a
    certain subject a precision check: logged with its verdict (OEQ-12-27) and the sentence redrafted."""
    model = look_model(narrator=[_say(_decl("He leans on the pole by the stair.", about=["npc.sela_vey"]))])
    _, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert "He leans" not in out.response.fiction
    assert any(e.get("check") == "pronoun_certain_subject" and e["verdict"] == "contradicted" and e["blocks"]
               and e["store_value"] == "she/her" for e in out.turn_record.claim_log)


def test_a_detail_clash_is_logged_and_the_store_keeps_its_value(tmp_path: Path) -> None:
    """12.3.1b item 3 (checklist 7): a lasting detail that clashes with the store is logged, not redrafted."""
    from engine.store.details import write_detail

    dock, ctx = setup(tmp_path, look_model())
    with dock.store.transaction() as tx:
        tx.add_all(write_detail(tx.state, tx.mint, dock.ferryman, "hair", "grey and cropped", rules=dock.rules).events)
    new = [{"element_kind": "person", "name": "Tam Harlan", "ordinary": True,
            "implied": [{"predicate": "hair", "value": "long and black"}]}]
    ctx.model.push(Role.NARRATOR, _say(_decl("Tam Harlan pushes back his long black hair.", new=new)))  # type: ignore[attr-defined]
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction.startswith("Tam Harlan pushes back his long black hair.")
    assert dock.store.state.fact_value(dock.ferryman, "detail.hair") == "grey and cropped"
    assert any(e["class"] == "detail" and e["store_value"] == "grey and cropped" for e in out.turn_record.claim_log)


def test_t2_in_the_narrators_voice_is_cut_and_in_speech_is_testimony(tmp_path: Path) -> None:
    bandit = [{"element_kind": "adversary", "name": "a bandit", "ordinary": True, "implied": []}]
    model = look_model(narrator=[_say(_decl("The quay is quiet."), _decl("A bandit waits on the north road.", new=bandit),
                                      _decl('"A bandit waits on the north road," Tam Harlan says.', new=bandit,
                                            speaker="npc.tam_harlan"))])
    _, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == f'The quay is quiet. "A bandit waits on the north road," Tam Harlan says. {PROMPT}'
    assert "a bandit" not in {e.name for e in ctx.store.state.entities.values()}  # never written
    assert any(e["verdict"] == "testimony" for e in out.turn_record.claim_log)


# ------------------------------------------------------------------------------------------- item 2: speech


def test_speech_is_testimony_a_said_record_never_a_fact(tmp_path: Path) -> None:
    """An NPC may name someone unknown and state a number: speech is never checked for truth (12.3.1b item 1);
    it is kept as a said record and writes no fact."""
    words = '"Brannoc took five silver from the ferry box," Tam Harlan says.'
    model = look_model(narrator=[_say(_decl(words, speaker="npc.tam_harlan"))])
    dock, ctx = setup(tmp_path, model)
    before = set(dock.store.state.facts)
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == f"{words} {PROMPT}" and len(calls(model, Role.NARRATOR)) == 1
    [said] = out.turn_record.said
    assert said["speaker"] == dock.ferryman and "Brannoc took five silver" in said["words"]
    new = [dock.store.state.facts[f] for f in set(dock.store.state.facts) - before]
    assert not any("Brannoc" in str(f.value) or "silver" in str(f.value) for f in new)


def test_a_name_heard_in_speech_is_learned(tmp_path: Path) -> None:
    dock, ctx = setup(tmp_path, look_model())
    with dock.store.transaction() as tx:
        tx.add(Event.of("entity_created", source="test", entity=EntityRecord(
            id="npc.odo_brant", kind="npc", name="Odo Brant", data={"role": "boatman", "name_known": False})))
    assert not name_known(dock.store.state, "npc.odo_brant")
    ctx.model.push(Role.NARRATOR, _say(_decl('"Odo Brant will row you across," Tam Harlan says.',  # type: ignore[attr-defined]
                                             speaker="npc.tam_harlan")))
    play_turn(ctx, "I look over the quay.")
    st = dock.store.state
    assert name_known(st, "npc.odo_brant")
    assert any(k.how == "heard" for k in st.knowledge[dock.pc].values())


def test_words_put_in_the_pcs_mouth_are_caught(tmp_path: Path) -> None:
    model = look_model(narrator=[_say(_decl("You look over the quay."),
                                      _decl('You say, "I will pay you ten silver for the crossing."'))])
    _, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert "ten silver" not in out.response.fiction and len(calls(model, Role.NARRATOR)) == 1  # a cut is code's
    checks = out.turn_record.draft_versions[0]["checks"]["1"]
    assert checks and checks[0]["fix"] == "cut" and "PC's mouth" in checks[0]["why"]


# ------------------------------------------------------------------------------------------- item 9: I-159


def test_a_snag_on_a_nudged_or_class_other_beat_applies_as_protective(s: Any) -> None:  # noqa: F811
    """01.6.8 (DL-01-29): one model-chosen modifier per beat. The rung of class `other`, or a nudge, is that
    modifier, so a cited Precision snag is refused as such and applies as Protective (stakes +1)."""
    a = s.fact("world", "crowd.density", "packed")
    plain = ok(frame(s, snags=[a], alternate_cost={"menu_id": "cost.shortfall"}))
    assert [x.type for x in plain.snags] == ["precision"]  # a class base: the one snag stays Precision
    other = ok(frame(s, obstacle={"kind": "tier", "id": "x", "obstacle_class": "other", "tier": "easy"},
                     snags=[a], alternate_cost={"menu_id": "cost.shortfall"}))
    assert [x.type for x in other.snags] == ["protective"] and other.stakes == "risky"
    lock = s.fact("world", "gate.make", "iron-bound, guild-made")
    nudged = ok(frame(s, obstacle={"kind": "tier", "id": "x", "obstacle_class": "obstructed", "nudge": 1,
                                   "nudge_fact": lock, "nudge_why": "a guild-made barrier stays hard"},
                      snags=[a], alternate_cost={"menu_id": "cost.shortfall"}))
    assert [x.type for x in nudged.snags] == ["protective"] and nudged.modifier.circumstance == 0


# ------------------------------------------------------------------------------------------- item 10: I-160(a)


def test_two_unoffset_reach_factors_route_the_beat_to_g4_before_the_offer(tmp_path: Path) -> None:
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I slip past the watch.", SNEAK)],
                           Role.FRAMER: [framer(reach_two_factors=True)], Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I slip past the watch.")
    adj = out.adjudication
    assert adj.pause is None and adj.record.beats[0].gate == "G4"
    assert any(o["kind"] == "REDIRECT" for o in adj.oof)
    assert not list(dock.store.events(types=["frame_committed"])) and not rolls(dock.store)  # nothing spent
    rulings = [e.payload.ruling for e in dock.store.events(types=["ruling_logged"])]  # type: ignore[attr-defined]
    assert any(r["kind"] == "g4" for r in rulings)


# ------------------------------------------------------------------------------------------- item 11: I-176


def _motives(dock: Any, npc: str, wants: list[Any], refusals: list[Any]) -> None:
    from engine.world.common import fact

    with dock.store.transaction() as tx:
        tx.add(fact(tx, npc, "wants", wants, rule_id="test", visibility="sealed"))
        tx.add(fact(tx, npc, "refusals", refusals, rule_id="test", visibility="sealed"))


def test_tags_match_wants_and_refusals_and_set_the_row(tmp_path: Path) -> None:
    from engine.dm.npc_layer import event_tags, motive_tags, want_row

    dock, _ = setup(tmp_path, look_model())
    _motives(dock, dock.ferryman, [{"text": "keep safe passage"}, {"text": "make money"}],
             [{"kind": "refusal.lend", "text": "never lends coin"}])
    st = dock.store.state
    m = motive_tags(st, RULES, dock.ferryman)
    assert m[f"{dock.ferryman}/want.1"] == {"concerns_travel", "asks_travel"}
    assert m[f"{dock.ferryman}/refusal.1"] == {"asks_loan"}
    # a Talk request asking for a loan, offering nothing: the Framer's asks tag and the pressure mark
    fake = SimpleNamespace(frame={"asks": "asks_loan", "beat": {"verb": "verb.talk", "pressure": "request"}})
    st.frames["frame.t"] = fake  # type: ignore[assignment]
    talk = SimpleNamespace(entry=BeatEntry(restatement="ask Tam for a loan", verb="verb.talk",
                                           targets=[dock.ferryman]), frame_id="frame.t", status="resolved")
    rec = AdjudicationRecord(parts=[PartEntry.model_validate({"text": "Lend me coin for the crossing?",
                                                              "class": "DECLARATION"})])
    ev = event_tags(st, rec, [talk], dock.ferryman)
    assert {"asks_loan", "pc_request", "concerns_travel"} <= ev
    assert ev & m[f"{dock.ferryman}/refusal.1"]  # the refusal engages: it is spoken
    strike = SimpleNamespace(entry=BeatEntry(restatement="strike Tam", verb="verb.strike", targets=[dock.ferryman]),
                             frame_id=None, status="resolved")
    assert "harms" in event_tags(st, AdjudicationRecord(), [strike], dock.ferryman)
    assert want_row(RULES, {"offers_payment"}, request=True, hostile=False) == 9
    assert want_row(RULES, {"offers_help"}, request=False, hostile=False) == 8
    assert want_row(RULES, {"harms"}, request=False, hostile=False) == 2
    assert want_row(RULES, {"harms"}, request=False, hostile=True) == 1
    assert want_row(RULES, {"concerns_travel"}, request=False, hostile=False) == 6


def test_plain_speech_gets_willingness_only_without_a_world_call(tmp_path: Path) -> None:
    """12.11.9 step 3 [revision: R2-H]: plain speech to Tam touches his want (concerns_travel), but for speech the
    source gives willingness only (PR-12-10 step 2): one willingness line, no row wording, no World call."""
    say = "Tam Harlan, the river crossing must be hard these days."
    model = ScriptedModel({Role.READER: [reader("SPEECH", say)], Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    _motives(dock, dock.ferryman, [{"text": "keep safe passage"}], [{"kind": "refusal.lend", "text": "never lends"}])
    out = play_turn(ctx, say)
    acts = [a for a in out.adjudication.record.npc_actions if a.npc == dock.ferryman]
    assert [(a.source, a.source_ref) for a in acts] == [("talk_outcome", "PR-12-10")]
    assert any(t.startswith("willingness:") for t in acts[0].tags)
    assert not calls(model, Role.WORLD)


def test_the_crowds_response_is_a_scene_fact_on_the_place_with_a_record_line(tmp_path: Path) -> None:
    from engine.dm.npc_layer import CROWD, crowd_response
    from engine.store.details import expire_events

    dock, ctx = setup(tmp_path, look_model())
    rec = AdjudicationRecord()
    with dock.store.transaction("turn.1") as tx:
        ctx.tx = tx
        crowd_response(ctx, rec, [1])  # the practice allows row 1 only: calling for the watch
        ctx.tx = None
    st = dock.store.state
    assert st.fact_value(dock.place, CROWD) == "calling for the watch"
    [line] = rec.npc_actions
    assert (line.npc, line.source, line.source_ref, line.tags) == (dock.place, "table_row", "tbl.npc_action:1",
                                                                   ["crowd"])
    with dock.store.transaction("turn.2") as tx:
        tx.add_all(expire_events(tx.state, tx.mint))  # scene end (12.4.8 step 8)
    assert dock.store.state.fact_value(dock.place, CROWD) is None
