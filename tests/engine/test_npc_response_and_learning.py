"""An addressed NPC's answer is sourced by the PC's beat; a successful learning beat delivers what the store holds
(playtests 20261007-170157-breaker and 161323-talker: Bixok's reply was cut until he "repeated my question back"; a
successful Talk said "It works" next to "hinders quietly", and the PC never learned what was asked).

12.2.9: the source decides *what* an NPC does, the DM chooses the *words*; 12.10.5: what the PC learns is written.
Real inventions stay cut: a deed with no source, a secret the store does not hold."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.audit.claims import check_claims
from engine.audit.fallback import plain_fallback
from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, NpcActionEntry, PartEntry
from engine.dm.turn import play_answer, play_turn
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.store.events import Event
from tests.engine.test_turn_adjudication import QUIET_WORLD, beat, framer, reader, setup
from tests.engine.test_turn_narration import calls, chk, claim, narr

RULES = load_rules()
ASK = "I ask Tam Harlan when the last ferry crosses."
TALK = beat("ask Tam Harlan when the last ferry crosses tonight", "verb.talk", target="npc.tam_harlan",
            verbs=("ask",))


def _fact(dock: Any, subject: str, predicate: str, value: Any) -> str:
    with dock.store.transaction() as tx:
        fid = tx.mint("fact")
        tx.add(Event.of("fact_set", {"source": "oracle"}, source="dm", rule_id="01.15.5", fact_id=fid,
                        subject=subject, predicate=predicate, value=value, visibility="shown"))
    return fid


def _talk_record(dock: Any, *, degree: str | None = "success", gate_words: str = "") -> AdjudicationRecord:
    rec = AdjudicationRecord(pc=dock.pc)
    rec.parts.append(PartEntry.model_validate({"text": ASK, "class": "DECLARATION"}))
    rec.beats.append(BeatEntry(actor=dock.pc, targets=[dock.ferryman], restatement="Wren asks Tam Harlan when the "
                               "last ferry crosses", approach_words="verb.talk, presence", degree=degree,
                               rolled=degree is not None, gate_words=gate_words, gate="G1"))
    return rec


def _check(dock: Any, rec: AdjudicationRecord, *cs: dict[str, Any]) -> list[tuple[str, str]]:
    return [(v.verdict, v.reason) for v in check_claims(list(cs), dock.store.state, rec, [], rules=RULES)]


def _act(subject: str, predicate: str, value: str, change: bool = True) -> dict[str, Any]:
    return {"subject": subject, "class": "action", "predicate": predicate, "value": value, "asserts_change": change}


# ------------------------------------------------------------------------------------------- 1. NPC responses


def test_an_addressed_npc_answers_in_words_and_manner(tmp_path: Path) -> None:
    dock, _ = setup(tmp_path, ScriptedModel({}))
    rec = _talk_record(dock)
    vs = _check(dock, rec, _act(dock.ferryman, "says", "not before the tide turns"),
                _act(dock.ferryman, "glances", "at the stair, then back to you"),
                _act(dock.ferryman, "shakes head", "slowly"),
                _act(dock.ferryman, "takes a breath", "before he answers"))
    assert [v for v, _ in vs] == ["supported"] * 4
    # the same words from an NPC no one addressed have no source
    assert _check(dock, rec, _act(dock.watch, "says", "the tide is turning"))[0][0] == "unsourced_change"


def test_an_addressed_npcs_deed_still_needs_a_source(tmp_path: Path) -> None:
    dock, _ = setup(tmp_path, ScriptedModel({}))
    rec = _talk_record(dock)
    vs = _check(dock, rec, _act(dock.ferryman, "hands over", "a brass key to you"),
                _act(dock.ferryman, "walks away", "down the quay"),
                _act(dock.ferryman, "draws a knife", "from his belt"))
    assert [v for v, _ in vs] == ["unsourced_change"] * 3
    rec.npc_actions.append(NpcActionEntry(npc=dock.ferryman, action="hands over the brass key", source="want"))
    assert _check(dock, rec, _act(dock.ferryman, "hands over", "a brass key to you"))[0][0] == "supported"


def test_a_question_naming_the_npc_addresses_them(tmp_path: Path) -> None:
    dock, _ = setup(tmp_path, ScriptedModel({}))
    rec = AdjudicationRecord(pc=dock.pc)
    rec.parts.append(PartEntry.model_validate({"text": "Tam, is the ferry running?", "class": "FICTION_QUESTION"}))
    assert _check(dock, rec, _act(dock.ferryman, "answers", "with a grunt"))[0][0] == "supported"


# ------------------------------------------------------------------------------------------- 2. background figures


def test_background_activity_that_changes_nothing_is_atmosphere(tmp_path: Path) -> None:
    dock, _ = setup(tmp_path, ScriptedModel({}))
    rec = AdjudicationRecord(pc=dock.pc)
    vs = _check(dock, rec, _act("unknown", "laughs", "too loudly at a far table", change=False),
                _act("unknown", "wipes", "the same ring of wood", change=False),
                _act("unknown", "laughs", "too loudly, then drinks", change=True),  # a change: cut
                _act("unknown", "watches", "you from the door", change=False),  # involves the PC: cut
                _act("unknown", "grabs", "a lantern from the hook", change=False),  # a deed: cut
                _act("unknown", "lurks", "in the shadows behind the shed", change=False))  # an adversary: cut
    assert [v for v, _ in vs] == ["supported", "supported"] + ["unsourced_change"] * 4


# ------------------------------------------------------------------------------------------- 3. what is learned


def test_an_oracle_settled_no_supports_the_npcs_denial(tmp_path: Path) -> None:
    """Breaker turn 6: 'Bixok did not see who started it' was contradicted with 'not known' although the Oracle
    had settled saw_who_started_the_quarrel = no."""
    dock, _ = setup(tmp_path, ScriptedModel({}))
    _fact(dock, dock.ferryman, "saw_who_started_the_quarrel", False)
    rec = _talk_record(dock)
    k = lambda p, v: {"subject": dock.ferryman, "class": "knowledge", "predicate": p, "value": v}  # noqa: E731
    vs = _check(dock, rec, k("saw who started the quarrel", "no"), k("did not see", "who started the quarrel"),
                k("saw who started the quarrel", "yes, the tall one"))
    assert [v for v, _ in vs] == ["supported", "supported", "contradicted"]


def test_unknown_knowledge_on_a_successful_talk_is_settled_not_cut(tmp_path: Path) -> None:
    dock, _ = setup(tmp_path, ScriptedModel({}))
    k = {"subject": dock.ferryman, "class": "knowledge", "predicate": "knows", "value": "the night boat leaves from the "
         "north stair"}
    secret = {"subject": dock.ferryman, "class": "knowledge", "predicate": "knows", "value": "the secret of the "
              "smugglers' hidden cache"}
    assert _check(dock, _talk_record(dock), k)[0][0] == "undetermined"
    assert _check(dock, _talk_record(dock, degree="failure"), k)[0][0] == "contradicted"
    assert _check(dock, AdjudicationRecord(pc=dock.pc), k)[0][0] == "contradicted"
    assert _check(dock, _talk_record(dock), secret)[0][0] == "contradicted"  # a secret is never settled by asking


def test_a_refused_beat_is_not_it_works(tmp_path: Path) -> None:
    """Breaker turn 8: a go-big reframe the frame check refused printed 'It works.' beside the NPC's table row."""
    dock, _ = setup(tmp_path, ScriptedModel({}))
    rec = _talk_record(dock, degree=None, gate_words="PR-01-2 step 10 (alternate_cost): a risky frame needs an "
                                                     "alternate cost")
    out = {"subject": "unknown", "class": "outcome", "predicate": "it works", "value": "he tells you"}
    assert _check(dock, rec, out)[0][0] == "contradicted"
    fb = plain_fallback(rec, names={dock.pc: "Wren", dock.ferryman: "Tam Harlan"})
    assert "It works" not in fb.fiction


def _talk_turn(tmp_path: Path, narrator: list[Any], checker: list[Any], world: Any = QUIET_WORLD,
               face: int = 19) -> tuple[Any, Any, ScriptedModel, Any]:
    model = ScriptedModel({Role.READER: [reader("DECLARATION", ASK, TALK)], Role.FRAMER: [framer()],
                           Role.WORLD: [world]})
    dock, ctx = setup(tmp_path, model)
    fid = _fact(dock, dock.ferryman, "last_ferry_crossing", "at the turn of the tide, an hour before dawn")
    _fact(dock, dock.ferryman, "boat", "a flat-bottomed ferry with a patched sail")
    assert play_turn(ctx, ASK).adjudication.pause.kind == "offer"
    ctx.rng.faces = [face]  # type: ignore[attr-defined]
    model.push(Role.NARRATOR, *narrator)
    model.push(Role.CHECKER, *checker)
    return dock, ctx, model, (fid, play_answer(ctx, "commit"))


def test_a_successful_talk_delivers_what_the_npc_knows(tmp_path: Path) -> None:
    text = ('"At the turn of the tide," Tam Harlan says, and glances at the water. "An hour before dawn." '
            "What do you do?")
    dock, ctx, model, (fid, out) = _talk_turn(tmp_path, [narr(text)], [chk(
        claim(0, "npc.tam_harlan", "action", "says", "at the turn of the tide", change=True),
        claim(0, "npc.tam_harlan", "action", "glances", "at the water", change=True),
        claim(1, "pc.wren", "knowledge", "learns", "the last ferry crosses an hour before dawn", change=True))])
    b = out.adjudication.record.beats[0]
    assert b.degree in ("success", "critical_success")
    assert len(b.learned) == 1 and "turn of the tide" in b.learned[0]  # the boat is not what was asked
    assert fid in ctx.store.state.knowledge[dock.pc]
    assert "the PC learns" in calls(model, Role.NARRATOR)[0].message
    assert out.response.fiction == text and not out.response.flags.fallback_used


def test_a_talk_target_gets_the_talk_outcome_not_a_table_row(tmp_path: Path) -> None:
    world = {"responses": [{"npc": "npc.tam_harlan", "want_engaged": "none", "refusal_engaged": "none",
                            "table_context": {"tags": []}}]}
    _, _, _, (_, out) = _talk_turn(tmp_path, [narr("Tam Harlan nods. What do you do?")], [chk()], world=world)
    rows = out.adjudication.record.npc_actions
    assert [(a.source, a.action) for a in rows] == [("talk_outcome", f"responds as the talk went: "
                                                                     f"{out.adjudication.record.beats[0].degree}")]


def test_a_failed_talk_delivers_nothing(tmp_path: Path) -> None:
    _, ctx, _, (fid, out) = _talk_turn(tmp_path, [narr("Tam Harlan shrugs. What do you do?")], [chk()], face=2)
    assert out.adjudication.record.beats[0].learned == [] and fid not in ctx.store.state.knowledge.get("pc.wren", {})


def test_what_the_store_lacks_is_settled_by_the_oracle_and_learned(tmp_path: Path, monkeypatch: Any) -> None:
    """The store holds nothing on the north stair: the narration's answer is settled at the check (yes here), so it
    stands as drafted and the PC's knowledge of it is written (12.10.5)."""
    from engine.resolve import oracle

    monkeypatch.setattr(oracle, "shape_for", lambda *a: "yes")
    text = '"The night boat leaves from the north stair," Tam Harlan says. What do you do?'
    dock, ctx, model, (_, out) = _talk_turn(tmp_path, [narr(text)], [chk(
        claim(0, "npc.tam_harlan", "knowledge", "knows", "the night boat leaves from the north stair"))])
    assert out.response.fiction == text and not out.response.flags.fallback_used
    st = ctx.store.state
    asked = [f for f in st.facts.values() if f.subject == dock.ferryman and f.predicate.startswith("knows_the_night")]
    assert len(asked) == 1 and asked[0].value is True and asked[0].id in st.knowledge[dock.pc]


# ------------------------------------------------------------------------------------------- 3. silent NPCs, speech

PRAY = 'I kneel beside the attendant and say, "Brother, who took it?"'


def _attendant(dock: Any) -> None:
    """Met mid-scene: positioned at the scene's place, never framed in its cast (playtest 175928-talker)."""
    from engine.store.events import EntityRecord

    with dock.store.transaction() as tx:
        tx.add(Event.of("entity_created", source="test", entity=EntityRecord(
            id="npc.gilda", kind="npc", name="Gilda Underhill", data={
                "role": "shrine attendant", "demeanor": "grieving", "pronouns": "he/him",
                "refusals": ["will not break off his prayer for a stranger"]})))
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity="npc.gilda", location=dock.place))


def test_an_npc_met_mid_scene_answers_and_a_refusal_is_legible(tmp_path: Path) -> None:
    # P-056: the World role saw only the framed cast, so the attendant never answered and nothing said why
    world = {"responses": [{"npc": "npc.gilda", "want_engaged": "none", "refusal_engaged": "npc.gilda/refusal.1",
                            "table_context": {"tags": []}}]}
    model = ScriptedModel({Role.READER: [reader("SPEECH", PRAY)], Role.WORLD: [world],
                           Role.NARRATOR: [narr('Gilda keeps praying and lifts a hand: "Not now." What do you do?')],
                           Role.CHECKER: [chk()]})
    dock, ctx = setup(tmp_path, model)
    _attendant(dock)
    out = play_turn(ctx, PRAY)
    rows = out.adjudication.record.npc_actions
    assert [(a.npc, a.source) for a in rows] == [("npc.gilda", "refusal")]
    msg = calls(model, Role.NARRATOR)[0].message
    assert "Gilda Underhill acts: refuses: will not break off his prayer" in msg
    assert "show it plainly" in msg and "manner: grieving" in msg and "- present: Gilda Underhill" in msg
    fb = plain_fallback(out.adjudication.record, names={"npc.gilda": "Gilda Underhill"})
    assert "Gilda Underhill refuses" in fb.fiction


def test_an_npc_who_asks_is_quoted(tmp_path: Path) -> None:
    # P-061: "she asks something, pitched low" with no words; the narrator is told to quote, and an NPC's quoted
    # question passes the check as drafted
    world = {"responses": [{"npc": "npc.tam_harlan", "want_engaged": "none", "refusal_engaged": "none",
                            "table_context": {"tags": []}}]}
    hello = 'I say to Tam Harlan, "Evening."'
    text = 'Tam Harlan squints at you. "Who sent you down here at this hour?" he asks. What do you say?'
    model = ScriptedModel({Role.READER: [reader("SPEECH", hello)], Role.WORLD: [world],
                           Role.NARRATOR: [narr(text)], Role.CHECKER: [chk(
                               claim(1, "npc.tam_harlan", "action", "asks", "who sent you down here at this hour",
                                     change=True))]})
    dock, ctx = setup(tmp_path, model)
    ctx.rng.faces = [7]  # type: ignore[attr-defined]
    out = play_turn(ctx, hello)
    msg = calls(model, Role.NARRATOR)[0].message
    assert "speaks in quoted words" in msg and "Never write that their words are lost" in msg
    assert out.response.fiction == text and not out.response.flags.fallback_used
    assert '"Who sent you down here at this hour?"' in out.response.fiction
