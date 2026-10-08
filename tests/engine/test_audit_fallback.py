"""The plain fallback (12.3.3): built from the adjudication record only, no invented content, no mechanics."""

from __future__ import annotations

import re

from engine.audit import text as tx
from engine.audit.claims import Verdict
from engine.audit.fallback import plain_fallback
from engine.audit.screen import mechanics_in_fiction
from engine.dm.adjudication import (
    AdjudicationRecord,
    BeatEntry,
    CostEntry,
    NpcActionEntry,
    OmenEntry,
    PartEntry,
    PauseEntry,
    PositionEntry,
    SceneEntry,
)

NAMES = {"pc.wren": "Wren", "npc.tam_harlan": "Tam"}


def _record(**kw: object) -> AdjudicationRecord:
    beat = BeatEntry(restatement="Wren forces the hasp with the iron bar (verb.force)", actor="pc.wren",
                     degree="success", near_miss=True, success_at_cost=True, rolled=True,
                     costs=[CostEntry(menu_id="cost.noise", severity="S2", form="the bar shrieks against the iron")],
                     positions=[PositionEntry(entity="pc.wren", words="inside the archive")])
    return AdjudicationRecord(
        turn_id="turn.4", pc="pc.wren", beats=[beat], scene=SceneEntry(header="The old archive, morning"),
        npc_actions=[NpcActionEntry(npc="npc.tam_harlan", action="turns toward the noise", source="table_row")],
        omens=[OmenEntry(clock_id="clk.alarm", omen="boots on the upper stairs")], **kw)  # type: ignore[arg-type]


def _vocab(rec: AdjudicationRecord) -> set[str]:
    allowed = tx.content(" ".join(map(str, rec.dump().values())) + " " + " ".join(NAMES.values()))
    return allowed | tx.content("it works at a cost what do you does not go goes better than hoped badly wrong "
                                "falls just short comes someone are is yes no")  # [verification: fallback text quality]


def test_built_only_from_the_record() -> None:
    rec = _record()
    fb = plain_fallback(rec, names=NAMES, verdicts=[Verdict(claim=0, verdict="contradicted", fix="redraft_to_store")])
    assert tx.content(fb.fiction) <= _vocab(rec), tx.content(fb.fiction) - _vocab(rec)
    for piece in ("You force the hasp", "It works, at a cost", "The bar shrieks", "Boots on the upper stairs",
                  "Tam turns toward the noise", "The old archive, morning."):
        assert piece in fb.fiction
    assert fb.fiction.endswith("What do you do?")
    assert not re.search(r"\d|verb\.", fb.fiction)
    assert mechanics_in_fiction(fb.fiction) == []
    assert fb.review_flag and fb.ruling.kind == "rule_conflict" and fb.ruling.review_flag
    assert fb.ruling.result["verdicts"][0]["verdict"] == "contradicted"


def test_pause_and_owed_warning() -> None:
    rec = _record(pause=PauseEntry(kind="offer"), triggers=["trg.lethal_warning"])
    fb = plain_fallback(rec, names=NAMES)
    assert not fb.fiction.endswith("?")  # the pause block follows instead (12.14.9)
    assert fb.owed_blocks == ["[WARNING]"]


def test_npc_action_rows_read_as_prose() -> None:
    """Playtest 2026-10-07: "Tikka Mud-Walker escalates: threatens, calls for others, attacks only if able and
    hostile" and "asks the PC something" reached the player verbatim."""
    rows = ["escalates: threatens, calls for others, attacks only if able and hostile", "asks the PC something",
            "responds as the talk went: success", "helps as asked"]
    rec = AdjudicationRecord(pc="pc.wren", npc_actions=[NpcActionEntry(npc="npc.tam_harlan", action=a,
                                                                       source="table_row") for a in rows])
    fb = plain_fallback(rec, names=NAMES).fiction
    assert fb == ("Tam grows threatening and calls for others. Tam has a question for you. Tam agrees. "
                  "Tam helps as asked. What do you do?")
    _clean(fb)


def test_empty_record_invents_nothing() -> None:
    fb = plain_fallback(AdjudicationRecord(pc="pc.wren"))
    assert fb.fiction == "What do you do?"


# --- the playtest's fallbacks (save playtest-20261007-155118): fiction, not forms [verification: fallback text quality]
_RULES_TALK = re.compile(r"\?\s*(?:yes|no)\b|\b(?:roll|trivial|reach|dc|success|failure|odds|possible now|without "
                         r"this|intervals?)\b|(?:^|\. )learn whether|\(\s*\)", re.IGNORECASE)


def _clean(fiction: str) -> None:
    assert not _RULES_TALK.search(fiction), _RULES_TALK.search(fiction)
    assert mechanics_in_fiction(fiction) == [], mechanics_in_fiction(fiction)


def test_oracle_answers_are_statements() -> None:
    from engine.dm.adjudication import OracleEntry
    rec = AdjudicationRecord(pc="pc.wren", oracle=[
        OracleEntry(question="Traders are already setting up stalls at dawn?", answer="yes"),
        OracleEntry(question="Townsfolk are already gathering in the square at dawn?", answer="no"),
        OracleEntry(question="Someone is watching the square who should not be there?", answer="no"),
        OracleEntry(question="Fresh tracks leading away from the square can still be read on the ground?", answer="no"),
        OracleEntry(question="The well is dry?", answer="yes, but the bucket is wet")])
    fb = plain_fallback(rec, names=NAMES).fiction
    _clean(fb)
    for piece in ("Traders are already setting up stalls at dawn.", "Townsfolk are not yet gathering",
                  "No one is watching the square", "can no longer be read", "The well is dry, but the bucket is wet."):
        assert piece in fb, fb


def test_a_compound_no_is_left_out_not_half_negated() -> None:
    """P-077 (talker 185715 input 18): "Calbert Oakward is not in Barrowburn and can be found in the village"."""
    from engine.dm.adjudication import OracleEntry
    rec = AdjudicationRecord(pc="pc.wren", oracle=[OracleEntry(
        question="Calbert Oakward is in Barrowburn and can be found in the village today", answer="no")])
    assert plain_fallback(rec, names=NAMES).fiction == "What do you do?"


def test_a_wh_question_is_never_echoed_back() -> None:
    """Playtest 2026-10-07: "What stands and moves around the crossroads ...? Yes." reached the player."""
    from engine.dm.adjudication import OracleEntry
    rec = AdjudicationRecord(pc="pc.wren", oracle=[
        OracleEntry(question="What stands and moves around the crossroads at morning?", answer="yes")])
    assert plain_fallback(rec, names=NAMES).fiction == "What do you do?"


def test_gated_and_failed_beats_read_as_fiction() -> None:
    from engine.resolve.pipeline import _span_words
    rec = AdjudicationRecord(pc="pc.wren", beats=[
        BeatEntry(restatement="Learn whether anyone is watching the square from its doorways", actor="pc.wren",
                  gate="G1", gate_words="no roll: trivial", reach="standard"),
        BeatEntry(restatement="Learn whether tracks lead away from the square", actor="pc.wren", gate="G3",
                  gate_words="Without Tracking this is beyond you as tried. Possible now: follow fresh, plain tracks "
                             "(harder, at most limited reach)"),
        BeatEntry(restatement="Learn whether tracks lead away from the square", actor="pc.wren", rolled=True,
                  degree="critical_failure", costs=[CostEntry(menu_id="cost.time", severity="S2",
                                                              form=_span_words(6, "intervals"))]),
        BeatEntry(restatement="Wren tries the door", actor="pc.wren", degree="failure", rolled=True)])
    fb = plain_fallback(rec, names=NAMES).fiction
    _clean(fb)
    for piece in ("You try to learn whether anyone is watching the square from its doorways. It works.",
                  "You cannot do it that way.", "It goes badly. About an hour passes.",
                  "You try the door. It doesn't work."):
        assert piece in fb, fb
    assert "Tracking" not in fb and "harder" not in fb


def test_playtest_172629_fallback_is_grammatical() -> None:
    """Playtests 20261007-172629/170318/170204: "You try to gerella is pinned against the gatepost. It works.",
    "Knows where ... hiring can not be found", "..., but lesser", "(Her claim about the ankle is context only.)"."""
    from engine.dm.adjudication import OracleEntry
    names = {"pc.geria": "Geria Salier", "npc.gerella": "Gerella Vasois"}
    rec = AdjudicationRecord(pc="pc.geria", pause=PauseEntry(kind="offer"), beats=[
        BeatEntry(restatement="Gerella is pinned against the gatepost", actor="pc.geria"),
        BeatEntry(restatement="Gerella names who is hiring for Larkgate and where to find them", actor="pc.geria"),
        BeatEntry(restatement="Geria pushes on toward the gate, sword raised. (Her claim about the ankle is context "
                              "only.)", actor="pc.geria", degree="success", rolled=True)],
        oracle=[OracleEntry(question="knows where the Larkgate grain-lords' hiring can be found in Redby", answer="no"),
                OracleEntry(question="Gerella knows where the hiring can be found?", answer="no"),
                OracleEntry(question="The people at the wall can say what is at the gate", answer="yes, but lesser")])
    fb = plain_fallback(rec, names=names).fiction
    assert fb == ("Gerella is pinned against the gatepost. Gerella names who is hiring for Larkgate and where to find "
                  "them. You push on toward the gate, sword raised. It works. "
                  "The people at the wall can say what is at the gate."), fb
    assert not re.search(r"try to [a-z]*(?:gerella|is)\b|\bto [a-z]+ is\b|[()]|can not|but lesser", fb, re.I)


def test_empty_brackets_never_survive() -> None:
    rec = AdjudicationRecord(pc="pc.wren", beats=[BeatEntry(restatement="x", actor="npc.tam_harlan", degree="failure",
                                                            costs=[CostEntry(menu_id="cost.time", severity="S1",
                                                                             form="time passes (6 intervals)")])])
    assert "()" not in plain_fallback(rec, names=NAMES).fiction.replace(" ", "")


def test_a_possessive_or_determiner_restatement_is_its_own_sentence() -> None:
    """Playtest 20261007-193420 (P-091): "You try to garett's grip on her arm loosens"."""
    for r in ("Garett's grip on her arm loosens", "Some of the crowd steps back", "Each guard turns away"):
        rec = AdjudicationRecord(pc="pc.belas", beats=[BeatEntry(restatement=r, actor="pc.belas", degree="failure",
                                                                 rolled=True)])
        fb = plain_fallback(rec, names={"pc.belas": "Belas Terent"}).fiction
        assert fb.startswith(r + ".") and "try to" not in fb, fb
    rec = AdjudicationRecord(pc="pc.belas", beats=[BeatEntry(restatement="Wrench free", actor="pc.belas")])
    assert "You try to wrench free." in plain_fallback(rec, names={"pc.belas": "Belas Terent"}).fiction


def test_a_spoken_line_with_no_beat_is_restated() -> None:
    """Playtest 20261007-201412 talker, input 31: two SPEECH parts, no beat, and the fallback said only "What do
    you do?". The player's own words come back, in order, around the beats; a NOTE-answered part does not."""
    rec = AdjudicationRecord(pc="pc.wren", parts=[
        PartEntry.model_validate({"text": "I sit on the bench.", "class": "DECLARATION"}),
        PartEntry.model_validate({"text": "\"That's all right, Oggza. Is Seley one of yours?\"", "class": "SPEECH",
                                  "handled": "answered"}),
        PartEntry.model_validate({"text": "what are my options?", "class": "FICTION_QUESTION", "handled": "noted"})],
        beats=[BeatEntry(restatement="Wren sits on the bench", actor="pc.wren", part=0,
                         positions=[PositionEntry(entity="pc.wren", words="a few strides from the bench")])],
        npc_actions=[NpcActionEntry(npc="npc.tam_harlan", action="offers partial help", source="table_row")])
    fb = plain_fallback(rec, names=NAMES).fiction
    assert fb == ("You sit on the bench. You are a few strides from the bench. "
                  "You ask, \"That's all right, Oggza. Is Seley one of yours?\" Tam offers some help. "
                  "What do you do?"), fb
    # playtest 20261007-203717 breaker, input 28: the Reader's queue note reached the player
    noted = AdjudicationRecord(pc="pc.wren", beats=[BeatEntry(
        restatement="Wren asks Tam what there is to discover. Queued: looking at Belia, pending clarification of "
                    "who is in the room. Spoken to Tam, not a beat: she thanks him.", actor="pc.wren",
        degree="success", rolled=True)])
    assert plain_fallback(noted, names=NAMES).fiction == ("You ask Tam what there is to discover. It works. "
                                                          "What do you do?")
    only = AdjudicationRecord(pc="pc.wren", parts=[PartEntry.model_validate(
        {"text": "I lean in and say, \"Who did you lose?\"", "class": "SPEECH"})])
    assert plain_fallback(only, names=NAMES).fiction == 'You ask, "Who did you lose?" What do you do?'
