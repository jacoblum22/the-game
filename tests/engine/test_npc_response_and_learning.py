"""An addressed NPC's answer is sourced by the record line its sentence cites (spec 006, 12.11.9); a successful learning beat delivers what the store holds
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


def _check(dock: Any, rec: AdjudicationRecord, *cs: dict[str, Any], cite: bool = False) -> list[tuple[str, str]]:
    """Each claim judged as from sentence 0; with `cite`, that sentence cites every line of the record."""
    from engine.dm.handles import items

    cited = {0: items(rec, names={})} if cite else None
    return [(v.verdict, v.reason) for v in check_claims(list(cs), dock.store.state, rec, [], rules=RULES, cited=cited)]


def _act(subject: str, predicate: str, value: str, change: bool = True) -> dict[str, Any]:
    return {"subject": subject, "class": "action", "predicate": predicate, "value": value, "asserts_change": change}


# ------------------------------------------------------------------------------------------- 1. NPC responses


def test_an_addressed_npc_answers_in_words_and_manner(tmp_path: Path) -> None:
    dock, _ = setup(tmp_path, ScriptedModel({}))
    rec = _talk_record(dock)
    vs = _check(dock, rec, _act(dock.ferryman, "says", "not before the tide turns"),
                _act(dock.ferryman, "glances", "at the stair, then back to you"),
                _act(dock.ferryman, "shakes head", "slowly"),
                _act(dock.ferryman, "takes a breath", "before he answers"), cite=True)
    assert [v for v, _ in vs] == ["supported"] * 4
    # the same words from an NPC no line names have no source; nor do his, from a sentence citing nothing
    assert _check(dock, rec, _act(dock.watch, "says", "the tide is turning"), cite=True)[0][0] == "unsourced_change"
    assert _check(dock, rec, _act(dock.ferryman, "says", "not before the tide turns"))[0][0] == "unsourced_change"


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
    from engine.dm.npc_layer import addressed

    assert addressed(dock.store.state, rec, [dock.ferryman, dock.watch]) == [dock.ferryman]  # 12.11.9: he answers
    rec.npc_actions.append(NpcActionEntry(npc=dock.ferryman, action="returns the greeting without stopping",
                                          source="table_row"))
    assert _check(dock, rec, _act(dock.ferryman, "answers", "with a grunt"), cite=True)[0][0] == "supported"


# ------------------------------------------------------------------------------------------- 2. background figures


def test_background_activity_that_changes_nothing_is_atmosphere(tmp_path: Path) -> None:
    """Spec 006: an unnamed figure's continuing business in a sentence that cites a record line is a reaction to
    it; a change is cut; and with nothing cited (an undeclared sentence) the audit's claim has no source. A sentence
    the narrator flags as atmosphere is never extracted at all (engine/dm/narration.py)."""
    dock, _ = setup(tmp_path, ScriptedModel({}))
    rec = _talk_record(dock)
    vs = _check(dock, rec, _act("unknown", "laughs", "too loudly at a far table", change=False),
                _act("unknown", "wipes", "the same ring of wood", change=False),
                _act("unknown", "laughs", "too loudly, then drinks", change=True), cite=True)  # a change: cut
    assert [v for v, _ in vs] == ["supported", "supported", "unsourced_change"]
    vs = _check(dock, rec, _act("unknown", "lurks", "in the shadows behind the shed", change=False))
    assert [v for v, _ in vs] == ["unsourced_change"]


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


def test_unknown_knowledge_on_a_successful_talk_is_not_settled_at_the_check(tmp_path: Path) -> None:
    """Spec 008 part B: the answer ladder answers before the draft (PR-12-10), so what the record does not declare is
    no longer settled by the Oracle at the check (`_learning_success` is retired)."""
    dock, _ = setup(tmp_path, ScriptedModel({}))
    k = {"subject": dock.ferryman, "class": "knowledge", "predicate": "knows", "value": "the night boat leaves from the "
         "north stair"}
    secret = {"subject": dock.ferryman, "class": "knowledge", "predicate": "knows", "value": "the secret of the "
              "smugglers' hidden cache"}
    assert _check(dock, _talk_record(dock), k)[0][0] == "contradicted"
    assert _check(dock, _talk_record(dock, degree="failure"), k)[0][0] == "contradicted"
    assert _check(dock, AdjudicationRecord(pc=dock.pc), k)[0][0] == "contradicted"
    # spec 006: no keyword proxy for "a secret" (I-129); undeclared, it is cut like any other knowledge claim
    assert _check(dock, _talk_record(dock), secret)[0][0] == "contradicted"


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
               face: int = 19, kind: str = "none") -> tuple[Any, Any, ScriptedModel, Any]:
    """The ferry Talk; with a `question_kind` it asks (PR-12-10), a plain question to a Neutral listener being
    certain (no roll, 15.3.10); else it is a request, committed at `face`."""
    model = ScriptedModel({Role.READER: [reader("DECLARATION", ASK, TALK, qk=kind)], Role.FRAMER: [framer()],
                           Role.WORLD: [world]})
    dock, ctx = setup(tmp_path, model)
    fid = _fact(dock, dock.ferryman, "last_ferry_crossing", "at the turn of the tide, an hour before dawn")
    _fact(dock, dock.ferryman, "boat", "a flat-bottomed ferry with a patched sail")
    model.push(Role.NARRATOR, *narrator)
    model.push(Role.CHECKER, *checker)
    ctx.rng.faces = [face]  # type: ignore[attr-defined]
    out = play_turn(ctx, ASK)
    if out.adjudication.pause is not None:
        assert out.adjudication.pause.kind == "offer"
        out = play_answer(ctx, "commit")
    return dock, ctx, model, (fid, out)


def test_a_successful_talk_delivers_what_the_npc_knows(tmp_path: Path) -> None:
    text = ('"At the turn of the tide," Tam Harlan says, and glances at the water. "An hour before dawn." '
            "What do you do?")
    dock, ctx, model, (fid, out) = _talk_turn(tmp_path, [narr(text)], [chk(
        claim(0, "npc.tam_harlan", "action", "says", "at the turn of the tide", change=True),
        claim(0, "npc.tam_harlan", "action", "glances", "at the water", change=True),
        claim(1, "pc.wren", "knowledge", "learns", "the last ferry crosses an hour before dawn", change=True))],
        kind="what_like")
    b = out.adjudication.record.beats[0]
    assert b.degree in ("success", "critical_success") or b.gate_words.startswith("no roll")
    assert len(b.learned) == 1 and "turn of the tide" in b.learned[0]  # the boat is not what was asked
    assert fid in ctx.store.state.knowledge[dock.pc]
    assert "the PC learns" in calls(model, Role.NARRATOR)[0].message
    assert out.response.fiction == text and not out.response.flags.fallback_used


def test_a_talk_target_gets_the_talk_outcome_not_a_table_row(tmp_path: Path) -> None:
    world = {"responses": [{"npc": "npc.tam_harlan", "want_engaged": "none", "refusal_engaged": "none",
                            "table_context": {"tags": []}}]}
    _, _, _, (_, out) = _talk_turn(tmp_path, [narr("Tam Harlan nods. What do you do?")], [chk()], world=world)
    rows = out.adjudication.record.npc_actions
    from engine.dm.npc_layer import talk_outcome

    assert [(a.source, a.action) for a in rows] == [("talk_outcome", talk_outcome(out.adjudication.record.beats[0]))]
    assert "responds as the talk went" not in rows[0].action  # T-15-5's yes, not a placeholder


def test_a_talk_aimed_at_a_thing_gets_no_answer_row(tmp_path: Path) -> None:
    """P-096 (194952-talker turn 20): the Talk's target was a mention minted as an object ('coming up the road');
    the fallback said 'Coming up the road agrees.' A thing has no one to answer as the talk went."""
    from engine.store.events import EntityRecord

    say = "I call to the people coming up the road."
    talk = beat("call to the people coming up the road", "verb.talk", target="obj.coming_up_the_road",
                verbs=("call",))
    model = ScriptedModel({Role.READER: [reader("DECLARATION", say, talk)], Role.FRAMER: [framer()],
                           Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    with dock.store.transaction() as tx:
        tx.add(Event.of("entity_created", source="test", entity=EntityRecord(
            id="obj.coming_up_the_road", kind="object", name="coming up the road")))
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity="obj.coming_up_the_road",
                        location=dock.place))
    assert play_turn(ctx, say).adjudication.pause.kind == "offer"
    ctx.rng.faces = [19]  # type: ignore[attr-defined]
    model.push(Role.NARRATOR, narr("You call out. What do you do?"))
    model.push(Role.CHECKER, chk())
    rec = play_answer(ctx, "commit").adjudication.record
    assert not any(a.npc == "obj.coming_up_the_road" for a in rec.npc_actions), rec.npc_actions


def test_a_failed_talk_delivers_nothing(tmp_path: Path) -> None:
    _, ctx, _, (fid, out) = _talk_turn(tmp_path, [narr("Tam Harlan shrugs. What do you do?")], [chk()], face=2)
    assert out.adjudication.record.beats[0].learned == [] and fid not in ctx.store.state.knowledge.get("pc.wren", {})


def test_what_the_store_lacks_is_answered_before_the_draft(tmp_path: Path) -> None:
    """PR-12-10: nothing stored on what was asked: the ladder answers at RECORD (pack, propose and ratify, else a
    pointer), so the narration says a declared answer and never settles one at the check."""
    text = '"The night boat leaves from the north stair," Tam Harlan says. What do you do?'
    dock, ctx, model, (_, out) = _talk_turn(tmp_path, [narr(text)], [chk(
        claim(0, "npc.tam_harlan", "knowledge", "knows", "the night boat leaves from the north stair"))],
        kind="where_is")
    learned = out.adjudication.record.beats[0].learned
    assert len(learned) == 1 and learned[0].startswith("Tam Harlan "), learned
    assert learned[0] not in text  # the ladder's answer is the record's; the NPC's words are their own
    # spec 011: speech is testimony (12.3.1b item 1): delivered, kept as a said record, never written or judged
    assert out.response.fiction == text and any("north stair" in s["words"] for s in out.turn_record.said)
    assert not any("north stair" in str(f.value) for f in ctx.store.state.facts.values())


# ------------------------------------------------------------------------------------------- P-120: success answers
# playtests 20261007-210627-explorer (critical success, "Who's behind the coin?", Aldmund still would not say) and
# 210953-talker (15 -> 17 vs 10, the bailiff "I'll not say"): a successful Talk is "yes, as asked" (T-15-5)


def _asked(tmp_path: Path, say: str, intent: str, world: Any = QUIET_WORLD, face: int = 19,
           kind: str = "none") -> tuple[Any, Any]:
    talk = beat(intent, "verb.talk", target="npc.tam_harlan", verbs=("ask",))
    model = ScriptedModel({Role.READER: [reader("DECLARATION", say, talk, qk=kind)], Role.FRAMER: [framer()],
                           Role.WORLD: [world]})
    dock, ctx = setup(tmp_path, model)
    model.push(Role.NARRATOR, narr("Tam Harlan answers. What do you do?"))
    model.push(Role.CHECKER, chk())
    ctx.rng.faces = [face]  # type: ignore[attr-defined]
    out = play_turn(ctx, say)
    if out.adjudication.pause is not None:
        out = play_answer(ctx, "commit")
    return dock, out.adjudication.record


def test_a_successful_who_question_names_an_existing_person(tmp_path: Path) -> None:
    dock, rec = _asked(tmp_path, "Who's behind the coin, Tam?", "ask Tam Harlan who is behind the coin",
                       kind="who_is")
    b = rec.beats[0]
    assert b.learned, b
    assert b.learned[0].startswith("Tam Harlan tells you who is behind the coin: ")
    assert "Tam Harlan" not in b.learned[0].split(": ", 1)[1]  # an existing person, never the one asked
    st = dock.store.state
    fid = next(f.id for f in st.facts.values() if f.predicate.startswith("who_is_behind"))
    assert st.facts[fid].value != dock.ferryman and fid in st.knowledge[dock.pc]


def test_a_failed_who_question_settles_nothing(tmp_path: Path) -> None:
    dock, rec = _asked(tmp_path, "Who's behind the coin, Tam?", "ask Tam Harlan who is behind the coin", face=2)
    assert rec.beats[0].learned == []
    assert not any(f.predicate.startswith("who_is_") for f in dock.store.state.facts.values())


def test_a_success_with_nothing_stored_still_gives_a_real_lead(tmp_path: Path, monkeypatch: Any) -> None:
    """DL-12-44: the Oracle says Tam does not know; the answer is "does not know" plus who would (never empty)."""
    from engine.resolve import oracle

    monkeypatch.setattr(oracle, "shape_for", lambda *a: "no")
    dock, rec = _asked(tmp_path, "Tam, what happened to the lighthouse keeper's lamp?",
                       "ask Tam Harlan what happened to the lighthouse keeper's lamp", kind="what_happened")
    learned = rec.beats[0].learned
    assert len(learned) == 1 and learned[0].startswith("Tam Harlan does not know"), learned
    assert not any("concrete" in n or "plainly" in n for n in rec.notes)  # the narrator notes are retired


def test_a_successful_what_question_is_proposed_and_ratified(tmp_path: Path, monkeypatch: Any) -> None:
    """212731-newcomer: Mauette 'knows what the shapes are' five times, every answer cut. Now the Proposer frames one
    ordinary candidate and the Oracle settles it before the draft (PR-12-10 rung 3)."""
    from engine.resolve import oracle

    monkeypatch.setattr(oracle, "shape_for", lambda *a: "yes")
    dock, rec = _asked(tmp_path, "Tam, what are those shapes out on the water?",
                       "ask Tam Harlan what the shapes on the water are", kind="what_like")
    learned = rec.beats[0].learned
    assert len(learned) == 1 and learned[0].startswith("Tam Harlan tells you: "), learned
    sealed = lambda v: {"subject": dock.ferryman, "class": "sealed", "predicate": "what the shapes are",  # noqa: E731
                        "value": v}
    assert _check(dock, _talk_record(dock, degree="failure"), sealed("driftwood"))[0][0] == "new_element"


def test_a_refusal_never_outranks_a_successful_talk(tmp_path: Path) -> None:
    world = {"responses": [{"npc": "npc.tam_harlan", "want_engaged": "none",
                            "refusal_engaged": "npc.tam_harlan/refusal.1", "table_context": {"tags": []}}]}
    dock, rec = _asked(tmp_path, "Tam, who came across on the last boat?", "ask Tam Harlan who came across on "
                       "the last boat", world=world)
    assert [a.source for a in rec.npc_actions if a.npc == dock.ferryman] == ["talk_outcome"]
    # the narration may not have them refuse either; after a failed Talk the same words stand
    refuse = _act(dock.ferryman, "says", "I'll not say who it was, not now")
    assert _check(dock, rec, refuse)[0] == ("contradicted", "a successful Talk is answered, never refused")
    assert _check(dock, _talk_record(dock, degree="failure"), refuse, cite=True)[0][0] == "supported"


LOOK = "I study the crate by the bollard to see what is inside it."


def _look_turns(tmp_path: Path, faces: list[int]) -> list[Any]:
    """P-086: Observe turns on an object the store holds nothing about, one per die face."""
    from engine.store.events import EntityRecord

    n = len(faces)
    look = beat("study the crate by the bollard to see what is inside it", "verb.observe", target="obj.crate")
    model = ScriptedModel({Role.READER: [reader("DECLARATION", LOOK, look)] * n, Role.FRAMER: [framer()] * n,
                           Role.WORLD: [QUIET_WORLD] * n})
    dock, ctx = setup(tmp_path, model)
    with dock.store.transaction() as tx:
        tx.add(Event.of("entity_created", source="test", entity=EntityRecord(id="obj.crate", kind="object",
                                                                             name="crate")))
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity="obj.crate", location=dock.place))
    outs = []
    for face in faces:
        assert play_turn(ctx, LOOK).adjudication.pause.kind == "offer"
        ctx.rng.faces = [face]  # type: ignore[attr-defined]
        model.push(Role.NARRATOR, narr("You look. What do you do?"))
        model.push(Role.CHECKER, chk())
        outs.append(play_answer(ctx, "commit"))
    return outs


def test_a_successful_look_names_something(tmp_path: Path) -> None:
    """Nothing stored on the crate: the look still ends in a real lead (PR-12-10 step 5), never a note to invent."""
    rec = _look_turns(tmp_path, [19])[0].adjudication.record
    assert rec.beats[0].degree in ("success", "critical_success"), (rec.beats[0], rec.notes)
    assert rec.beats[0].learned and not any("concrete thing" in n for n in rec.notes), rec.beats[0].learned


def test_repeated_failed_looks_say_it_cannot_be_made_out(tmp_path: Path) -> None:
    first, second = (o.adjudication.record for o in _look_turns(tmp_path, [2, 2]))
    assert second.beats[0].degree in ("failure", "critical_failure")
    assert not any(n.startswith("cannot make out:") for n in first.notes)
    said = [n for n in second.notes if n.startswith("cannot make out:")]
    assert said and "You cannot make out the crate from here" in said[0]
    assert "You cannot make out the crate" in plain_fallback(second).fiction


# ------------------------------------------------------------------------------------------- 3. silent NPCs, speech

PRAY = 'I kneel beside the attendant and say, "Brother, who took it?"'


def _attendant(dock: Any) -> None:
    """Met mid-scene: positioned at the scene's place, never framed in its cast (playtest 175928-talker)."""
    from engine.store.events import EntityRecord

    with dock.store.transaction() as tx:
        tx.add(Event.of("entity_created", source="test", entity=EntityRecord(
            id="npc.gilda", kind="npc", name="Gilda Underhill", data={
                "role": "shrine attendant", "demeanor": "grieving", "pronouns": "he/him",
                "refusals": ["will not break off his prayer for a stranger"],
                "wants": [{"text": "find whoever took the relic"}]})))  # untagged motives with opposite rows
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity="npc.gilda", location=dock.place))


def test_an_npc_met_mid_scene_answers_and_a_refusal_is_legible(tmp_path: Path) -> None:
    # P-056: the World role saw only the framed cast, so the attendant never answered and nothing said why.
    # Spec 011 (I-176): no tag matches and his motives point to opposite rows, so the World fallback decides
    world = {"responses": [{"npc": "npc.gilda", "want_engaged": "none", "refusal_engaged": "npc.gilda/refusal.1",
                            "table_context": {"tags": []}}]}
    model = ScriptedModel({Role.READER: [reader("SPEECH", PRAY)], Role.WORLD: [world],
                           Role.NARRATOR: [narr('Gilda keeps praying and lifts a hand: "Not now." What do you do?')],
                           Role.CHECKER: [chk()]})
    dock, ctx = setup(tmp_path, model)
    _attendant(dock)
    out = play_turn(ctx, PRAY)
    rows = out.adjudication.record.npc_actions
    assert [(a.npc, a.source) for a in rows] == [("npc.gilda", "refusal")] and "world_fallback" in rows[0].tags
    msg = calls(model, Role.NARRATOR)[0].message
    assert "Gilda Underhill acts: refuses, in their own voice (" in msg and "will not break off his prayer" in msg
    assert "show it plainly" in msg and "manner: grieving" in msg and "- present: Gilda Underhill" in msg
    fb = plain_fallback(out.adjudication.record, names={"npc.gilda": "Gilda Underhill"})
    assert "Gilda Underhill refuses" in fb.fiction


def test_a_conversation_is_not_dead_air(tmp_path: Path) -> None:
    # P-088: two speech-only turns with an NPC who answered offered [CUT?] mid-conversation (12.4.2 (7))
    hello = 'I say to Tam Harlan, "Evening."'
    model = ScriptedModel({Role.READER: [reader("SPEECH", hello)] * 3, Role.WORLD: [QUIET_WORLD] * 3,
                           Role.NARRATOR: [narr('"Evening," Tam Harlan says. What do you say?')] * 3,
                           Role.CHECKER: [chk()] * 3})
    dock, ctx = setup(tmp_path, model)
    outs = [play_turn(ctx, hello) for _ in range(3)]
    assert ctx.store.state.meta.get("dead_air") == 0
    assert not any(b.kind == "CUT?" or "Or stay a while" in b.text for o in outs for b in o.response.oof_blocks)


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
