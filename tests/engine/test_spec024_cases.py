"""Spec 024: the made-up and edge cases of specs/024-texture-outcome/cases.md (written before implementing).

T3 (DL-12-113, DL-12-114): nothing in the narrator packet pushes a look, a habit or a code sentence; no usage tracking.
T4 (DL-01-48, DL-12-115): one effective degree; a paused beat is unresolved. P1: the passage as written. P4, P5."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from engine.audit.claims import _beat_success, precision_checks
from engine.audit.declare import Passage, SceneIndex, sentences_of
from engine.data.loader import load_rules
from engine.dm import answer as ans
from engine.dm import narration
from engine.dm.adjudication import (
    AdjudicationRecord,
    BeatEntry,
    NpcActionEntry,
    PartEntry,
    PauseEntry,
    effective_degree,
    paused_beat,
)
from engine.dm.handles import items
from engine.dm.npc_layer import respond, voiced_refusal
from engine.dm.packet import own_words, pronoun_words, scene_setting, view_ctx, view_for
from engine.dm.roles import narrator as nr
from engine.dm.scene_state import _band, write
from engine.dm.turn import play_turn
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.resolve.pipeline import BeatOutcome
from engine.store.events import Event
from tests.engine.test_answer import turn
from tests.engine.test_turn_adjudication import QUIET_WORLD, reader, setup
from tests.fixtures.scene_dock import _entity, _fact, build_dock

RULES = load_rules()
HABIT = "wipes the bar with a rag"
PUSHES = ("FRESHNESS", "Details stated lately", "Lines these people", "brought the word", "matter at hand",
          "call them", "every other screen", "as every other")


def _person(dock: Any, name: str, **data: Any) -> str:
    with dock.store.transaction() as tx:
        eid = _entity(tx, "npc", name, data=data)
        tx.add(Event.of("position_set", source="fixture", rule_id="10.1.1", entity=eid, location=dock.place))
    return eid


def _innkeeper(dock: Any) -> str:
    return _person(dock, "Marra Holt", role="innkeeper", pronouns="she/her", detail="a stained apron",
                   demeanor="busy", voice={"register": "plain", "habit": HABIT})


def _unnamed(dock: Any, role: str, pronouns: str, **data: Any) -> str:
    """A person whose name the PC does not know (created unintroduced, 12.10.2)."""
    return _person(dock, "Odo Grey", role=role, pronouns=pronouns, name_known=False, **data)


def _packet(st: Any, rec: AdjudicationRecord, *, full: bool = False, message: str = "") -> str:
    return "\n".join([view_for(Role.NARRATOR, st, view_ctx(message, [], plain=False)),
                      nr.record_text(st, rec, player_message=message, rules=RULES), scene_setting(st, full=full)])


def _part(text: str, cls: str, **kw: Any) -> PartEntry:
    return PartEntry.model_validate({"text": text, "class": cls, **kw})


def _talk(npc: str, **kw: Any) -> BeatEntry:
    return BeatEntry(restatement="Offer the sellsword a round", approach_words="verb.talk, presence",
                     targets=[npc], verb="verb.talk", rolled=True, frame_id="frame.9", **kw)


# ------------------------------------------------------------------------------------------- C1, C7, C8 (live loop)


def test_c1_c7_c8_innkeeper_habit_over_ten_turns_is_never_pushed(tmp_path: Path) -> None:
    """made-up C1/C8 + edge C7: ten turns of talk with the innkeeper, the tenth while the inn burns; the narrator
    uses her habit every turn, knowingly. No packet requires, counts or quotes back the habit; no draft is redrafted
    for it; it reaches the narrator only as her background line, worded as occasional, in her pronouns."""
    model = ScriptedModel({Role.WORLD: [QUIET_WORLD] * 10})
    dock, ctx = setup(tmp_path, model)
    inn = _innkeeper(dock)
    lines = [f"Marra, what news tonight? ({n})" for n in range(9)] + ["Marra, the inn is on fire! Help me carry water!"]
    seen: list[str] = []
    said = iter(["Quiet as a grave.", "Carters came through at dusk.", "The ferry's late again.", "Ale's gone sour.",
                 "A stranger asked for you.", "The watch walked by twice.", "Rain by morning, I'd say.",
                 "Mind the loose board.", "Two rooms left upstairs.", "Grab a bucket, quick!"])

    def narrate(schema: dict[str, Any], packet: Any) -> dict[str, Any]:
        seen.append(f"{packet.view}\n{packet.message}")
        must = re.findall(r"(?m)^- (R\d+) MUST:", packet.message)
        words = next(said)  # her own words are new each turn (an NPC never repeats a said line, 12.14.11)
        return {"passage": f"Marra {HABIT} again. \"{words}\" What do you do?",
                "speech": [{"speaker": inn, "words": words, "form": "direct"}], "new": [], "covers": must}

    for text in lines:
        model.push(Role.READER, reader("SPEECH", text))
        model.push(Role.NARRATOR, narrate)
        out = play_turn(ctx, text)
        assert [v["kind"] for v in out.narration.draft_versions] == ["draft"]  # C7: delivered as drafted
        assert HABIT in out.response.fiction
    assert len(seen) == 10
    for pkt in seen:
        habit = [ln for ln in pkt.splitlines() if "wipes the bar" in ln]
        assert len(habit) == 1 and habit[0].startswith("  background (") and "now and then wipes the bar" in habit[0]
        assert not any(p in pkt for p in PUSHES), [p for p in PUSHES if p in pkt]
        assert not [ln for ln in pkt.splitlines() if " MUST:" in ln and ("rag" in ln or "apron" in ln)]


# ------------------------------------------------------------------------------------------- C2, C4, C9, C13


def test_c2_guild_label_is_data_never_a_verbatim_label(tmp_path: Path) -> None:
    """made-up C2: an unnamed officer of The Order of the Grey Hand; the packet gives role and faction as data and
    says only that the name is unknown, never a label to repeat."""
    dock = build_dock(tmp_path)
    off = _unnamed(dock, "officer of The Order of the Grey Hand", "he/him")
    st = dock.state
    rec = AdjudicationRecord(pc=dock.pc, parts=[_part("Officer, a word.", "SPEECH")])
    for full in (True, False, False):
        pkt = _packet(st, rec, full=full)
        assert not any(p in pkt for p in PUSHES)
        assert "(he/him): officer of The Order of the Grey Hand" in pkt  # spec 026: the people card's head line
        assert "does not know his name: never call him by a name" in pkt
        assert "name not known to the character" in pkt
    assert off in st.entities


@pytest.mark.parametrize("pron,poss,obj", [("he/him", "his", "him"), ("she/her", "her", "her")])
def test_c4_c9_unnamed_person_every_template_uses_their_pronouns(tmp_path: Path, pron: str, poss: str,
                                                                obj: str) -> None:
    """edge C4 (he/him walk-on) and C9 (she/her, no name): the view, age, activity, refusal, willingness and the
    name-unknown line all use the stored pronouns; never "call them"."""
    dock = build_dock(tmp_path)
    who = _unnamed(dock, "sellsword between contracts", pron, age="young (in their teens)",
                   detail="jewelry too fine for their station", voice={"register": "jovial",
                                                                        "habit": "clicks their tongue"})
    st = dock.state
    pkt = _packet(st, AdjudicationRecord(pc=dock.pc), full=True)
    assert f"young (in {poss} teens)" in pkt and f"too fine for {poss} station" in pkt
    assert f"now and then clicks {poss} tongue" in pkt
    assert f"does not know {poss} name: never call {obj} by a name" in pkt
    assert not re.search(r"\b(their|them|themselves)\b", "\n".join(ln for ln in pkt.splitlines() if "teens" in ln
                                                                  or "background" in ln or "know" in ln))
    rec = AdjudicationRecord(pc=dock.pc)
    with turn(dock.store) as ctx:
        refusal = voiced_refusal(ctx, who, "the talk did not move them")
        write(ctx, rec, who, {"activity": "going about their morning work"}, because="test")
        willing = ans.will_words(ctx.state, who, "willing", "a plain question")
    assert refusal == f"refuses, in {poss} own voice (jovial): the talk did not move {obj}"
    assert "clicks" not in refusal  # the habit is never required in a refusal (12.11.9 step 4)
    assert f"in {poss} own words" in willing
    from engine.dm.npc_layer import current_activity

    assert current_activity(dock.state, who) == f"going about {poss} morning work"


def test_c13_habit_across_three_scenes_only_background(tmp_path: Path) -> None:
    """made-up C13: the same NPC in three scenes: the look only when each scene is framed; the habit only in the
    view's background line; never a MUST line."""
    dock = build_dock(tmp_path)
    inn = _innkeeper(dock)
    st = dock.state
    rec = AdjudicationRecord(pc=dock.pc, parts=[_part("Marra?", "SPEECH")],
                             npc_actions=[NpcActionEntry(npc=inn, action="carries on with their own business",
                                                         source="table_row")])
    for _scene in range(3):
        for full in (True, False, False):
            setting = scene_setting(st, full=full)
            present = next(ln for ln in setting.splitlines() if "Marra Holt" in ln)
            assert ("a stained apron" in present) is full and "rag" not in present
            pkt = _packet(st, rec, full=full)
            assert [ln for ln in pkt.splitlines() if "wipes" in ln][0].startswith("  background (")
            assert not [ln for ln in pkt.splitlines() if "MUST" in ln and "wipes" in ln]
            assert "carries on with her own business" in pkt  # C18's row, in her pronouns


# ------------------------------------------------------------------------------------------- T4: C3, C5, C10, C11, C21


def test_c3_c21_effective_degree_everywhere() -> None:
    """made-up C3 (a lock barely missed, "succeed, but the guard hears you") and edge C21 (each degree)."""
    lock = BeatEntry(restatement="Pick the lock", degree="failure", near_miss=True, success_at_cost=True, rolled=True)
    assert effective_degree(lock) == "success" and _band(lock) == "success" and _beat_success(lock)
    line = nr._beat_line(None, lock, None)  # type: ignore[arg-type]
    assert "success at cost" in line and "near miss" not in line
    for deg in ("critical_failure", "critical_success"):
        assert effective_degree(BeatEntry(restatement="x", degree=deg)) == deg
    defaulted = BeatEntry(restatement="x", degree="failure", near_miss=True)  # the default, pause gone
    assert effective_degree(defaulted) == "failure" and _band(defaulted) == "failure"
    assert effective_degree(BeatEntry(restatement="x")) is None and _band(BeatEntry(restatement="x")) == "no_roll"


def test_c5_c11_paused_beat_is_unresolved_until_the_choice(tmp_path: Path) -> None:
    """edge C5 and C11: at a near-miss pause and at an OFFER the beat carries no degree, no near miss and no result
    words, is not owed, and its target has not answered the paused ask; once the default failure applies it does."""
    dock = build_dock(tmp_path)
    st = dock.state
    ferry = dock.ferryman
    parts = [_part("I set a coin down and offer a round.", "DECLARATION", handled="paused"),
             _part("Why won't you cross tonight?", "SPEECH", handled="answered")]
    near = _talk(ferry, degree="failure", near_miss=True)
    rec = AdjudicationRecord(pc=dock.pc, parts=parts, beats=[near],
                             pause=PauseEntry(kind="near_miss", frame_id="frame.9"))
    text = nr.record_text(st, rec, rules=RULES)
    beat = next(ln for ln in text.splitlines() if ln.startswith("- R1"))
    assert "not resolved yet" in beat and not re.search(r"failure|near miss|result:|it worked", beat)
    assert "R1 MUST" not in beat and paused_beat(rec, 0) and effective_degree(near, rec.pause) is None
    assert "Tam Harlan has not answered what the paused beat asks" in text
    assert "never end on waiting" not in text
    [it] = [i for i in items(rec, names=nr.names_for(st)) if i.kind == "beat"]
    assert not it.must_name and not re.search(r"short|fails|works", it.render)
    offer = AdjudicationRecord(pc=dock.pc, parts=parts[:1], beats=[_talk(ferry)], pause=PauseEntry(kind="offer"))
    text = nr.record_text(st, offer, rules=RULES)
    assert "not resolved yet" in text and "has not answered" in text and "answers in quoted words" not in text
    # the player declares something new: the default failure applies, no pause is open
    after = AdjudicationRecord(pc=dock.pc, beats=[near])
    assert "result: failure (the world answers), a near miss" in nr.record_text(st, after, rules=RULES)


def test_c10_accepted_near_miss_then_willingness(tmp_path: Path) -> None:
    """playtest C10 (talker inputs 27-28): the round offered, a near miss, "succeed and pay" taken: the sellsword's
    response is no refusal, his willingness is willing, his scene state takes the talk-success row."""
    dock = build_dock(tmp_path)
    ferry = dock.ferryman
    beat = BeatOutcome(status="resolved", entry=_talk(ferry, degree="failure", near_miss=True, success_at_cost=True))
    rec = AdjudicationRecord(pc=dock.pc, parts=[_part("A round, then?", "SPEECH")], beats=[beat.entry])
    with turn(dock.store) as ctx:
        respond(ctx, rec, [beat])
        band, why = ans.willingness(ctx, ferry, rec, [beat])
    [act] = rec.npc_actions
    assert not act.action.startswith("refuses") and "agrees" in act.action
    assert (band, why) == ("willing", "the talk moved them")
    assert ans.will_words(dock.state, ferry, band, why).endswith("in his own words, from what they know or have heard")


# ------------------------------------------------------------------------------------------- P1: C12, C20, C24


def _deliver(text: str, speech: list[dict[str, str]], drop: tuple[int, ...] = (), edit: dict[int, str] | None = None
             ) -> str:
    p = Passage.model_validate({"text": text, "speech": speech})
    sents = [narration._Sent(decl=s, orig=s.text) for s in sentences_of(p)[0]]
    for i in drop:
        sents[i].dropped = True
    for i, t in (edit or {}).items():
        sents[i].decl.text = t
    return narration._text(sents, text)


def test_c12_c20_two_paragraphs_two_speakers_kept() -> None:
    """made-up C12 and edge C20: two paragraphs, two speakers; a cut in paragraph 2, a code quote in place; a cut
    sentence that opens a paragraph passes its break to the next kept sentence."""
    text = ('Marra sets the jug down. "Smoke, out back," she says.\n\n'
            'The guard pushes in. "Everyone out," he says. The beams groan. What do you do?')
    speech = [{"speaker": "npc.marra", "words": "Smoke, out back,", "form": "direct"},
              {"speaker": "npc.guard", "words": "Everyone out,", "form": "direct"}]
    assert _deliver(text, speech) == text
    out = _deliver(text, speech, drop=(4,), edit={0: 'Marra sets the jug down, "carefully".'})
    assert out == ('Marra sets the jug down, "carefully". "Smoke, out back," she says.\n\n'
                   'The guard pushes in. "Everyone out," he says. What do you do?')
    out = _deliver(text, speech, drop=(2,))  # "The guard pushes in." opened paragraph 2
    assert '"Smoke, out back," she says.\n\n"Everyone out," he says.' in out


# ------------------------------------------------------------------------------------------- C6, C14, C17 (reading)


def _notice(dock: Any, name: str, words: str) -> str:
    with dock.store.transaction() as tx:
        eid = _entity(tx, "object", name, data={})
        _fact(tx, eid, "text", words)
        tx.add(Event.of("position_set", source="fixture", rule_id="10.1.1", entity=eid, location=dock.place))
    return eid


def test_c6_c17_reading_needs_a_named_or_acted_on_thing(tmp_path: Path) -> None:
    """edge C6 ("what did the notice say again?" is honoured) and C17 ("what did they say?" with two notices in
    view is not reading)."""
    dock = build_dock(tmp_path)
    _notice(dock, "ferry notice", "No crossings after dark. Posted by the harbour master.")
    _notice(dock, "bounty notice", "Ten silver for the smuggler. Posted by the watch.")
    st = dock.state
    rec = AdjudicationRecord(pc=dock.pc)
    again = nr._reading_lines(st, rec, "What did the ferry notice say again?")
    assert len(again) == 1 and "reads the ferry notice: quote its words exactly" in again[0]
    assert nr._reading_lines(st, rec, "Who did you ask, and what did they say?") == []


def test_c14_any_posted_notice_grammar() -> None:
    """edge C14: never "the any posted notice"."""
    assert nr._either(["any posted notice"]) == "any posted notice"
    assert nr._either(["the hire notice", "any posted notice"]) == "the hire notice or any posted notice"


def test_c15_notice_signature_separated() -> None:
    """edge C15: a hire or bounty notice ends "Posted by <issuer>."."""
    rows = {r["option"]: r["text"] for r in RULES.table("tbl.12.seed.document")["results"]}
    assert rows["hire"].endswith("Posted by {issuer}.") and rows["bounty"].endswith("Posted by {issuer}.")


# ------------------------------------------------------------------------------------------- C16 (pronoun tags)


IDX = SceneIndex(pc="pc.x", aliases={"npc.magby": ["magby applefoot", "magby"], "npc.soldier": ["the soldier"]},
                 pronouns={"npc.magby": "m", "npc.soldier": "f"})


def test_c16_speech_tag_is_judged_against_its_speaker() -> None:
    """edge C16: round 7's one blocking pronoun hit took Magby for the subject of "she says"."""
    before = ["Magby's back is still turned."]
    said = "\"That one's the worst of the lot,\" she says."
    assert not precision_checks(said, idx=IDX, before=before, speech=["That one's the worst of the lot,"],
                                speaker="npc.soldier", rules=RULES)
    assert not precision_checks(said, idx=IDX, before=before, speech=["That one's the worst of the lot,"],
                                rules=RULES)  # no declared speaker: no verdict
    [h] = precision_checks("\"Go,\" he says.", idx=IDX, speech=["Go,"], speaker="npc.soldier", rules=RULES)
    assert (h.words, h.subject) == ("he", "npc.soldier")


# ------------------------------------------------------------------------------------------- C18, C19, C22, C23


def test_c18_withheld_suffix_only_on_refusals(tmp_path: Path) -> None:
    """edge C18 (P4)."""
    dock = build_dock(tmp_path)
    st = dock.state
    assert nr._withheld(st, dock.ferryman, "carries on with their own business", dock.pc) == ""
    assert nr._withheld(st, dock.ferryman, "wants something first", dock.pc) == ""
    assert "does not get what was asked" in nr._withheld(st, dock.ferryman, "refuses, in his own voice: no", dock.pc)


def test_c19_no_incident_sentence_in_any_scene_setting(tmp_path: Path) -> None:
    """made-up C19: the opening's incident note carries the reporter as a field; no scene setting has a code
    sentence about it (the round-7 seeded opening is test_incident's)."""
    dock = build_dock(tmp_path)
    for full in (True, False):
        assert "brought the word" not in scene_setting(dock.state, full=full)
        assert "matter at hand" not in scene_setting(dock.state, full=full)


def test_c22_c23_pronoun_fill_is_only_for_known_pronouns_and_templates(tmp_path: Path) -> None:
    """edge C22 (they/them, unrecorded: the template stays) and C23 (free text is never filled)."""
    dock = build_dock(tmp_path)
    them = _person(dock, "Ash", role="drover", pronouns="they/them")
    nobody = _person(dock, "Kell", role="drover")
    st = dock.state
    for eid in (them, nobody):
        assert own_words("going about their morning work", pronoun_words(st, eid)) == "going about their morning work"
    assert own_words("Their hands shake", pronoun_words(st, dock.ferryman)) == "His hands shake"
    assert (pronoun_words(st, dock.pc) or ("",))[1:2] == ("your",)  # the PC is "you"
    # free text (a knowledge line about others) goes through no fill: speaker cards are not templated
    from engine.dm.packet import speaker_card

    with dock.store.transaction() as tx:
        _fact(tx, dock.ferryman, "topic.wolves", "the Wolves pay their men on the day")
        tx.add(Event.of("knowledge_recorded", source="fixture", rule_id="12.10.6", knower=dock.ferryman,
                        fact_id=tx.state.current_fact_id(dock.ferryman, "topic.wolves") or "", how="recalled"))
    assert any("pay their men" in ln for ln in speaker_card(dock.state, dock.ferryman))
