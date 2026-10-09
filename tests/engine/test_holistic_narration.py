"""Spec 019 (F1 + F4's narration side) on real round-6 turns: the talker save 20261008-232941, cut into
tests/fixtures/round6_narration.json by specs/019-holistic-narration/extract_fixture.py (the saves are gitignored).

Each turn's first draft is given to today's passage judge as the passage a holistic narrator would send with the
same words (the draft's text, its speech in the side list, every MUST line covered). Offline, no model call: what
the test shows is what code now does with those words. Recorded then: blind add-repairs stacked quotes (turn.2),
repeated "Mark me ... a child gone" (turn.13) and ended a passage on the player's own line (turn.14); speech went out
unquoted (turn.16)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from engine.audit.declare import Passage, Speech, coverage, quote, unquoted
from engine.dm.adjudication import AdjudicationRecord, BeatEntry
from engine.dm.handles import items
from engine.dm.roles.narrator import record_text
from engine.dm.turn import play_turn
from engine.store.projection import WorldState
from evals.narration_plug import Packet, judge_passage
from tests.engine.test_turn_adjudication import setup
from tests.engine.test_turn_narration import _must, chk, look_model, passage

TURNS = {t["turn"]: t for t in json.loads((Path(__file__).parents[1] / "fixtures" / "round6_narration.json")
                                           .read_text(encoding="utf-8"))}
_Q = re.compile(r'"([^"]*)"')


def _passage(t: dict[str, Any]) -> Passage:
    """The first draft's words as one passage; each speaker's quoted words (or, unquoted, the sentence) as speech."""
    speech = []
    for s in t["first_draft"]:
        if s["speaker"] in (None, "none"):
            continue
        spans = _Q.findall(s["text"]) or [s["text"]]
        speech += [Speech(speaker=s["speaker"], words=w) for w in spans]
    return Passage(text=" ".join(s["text"] for s in t["first_draft"]), speech=speech,
                   covers=re.findall(r"(?m)^- (R\d+) MUST:", t["THIS MESSAGE"]))


def _judge(t: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    item = {"NARRATOR VIEW": t["NARRATOR VIEW"], "THIS MESSAGE": t["THIS MESSAGE"],
            "_recorded": {"save": t["save"], "turn": t["turn"]}}
    p = Packet(item)
    _, checks, _, unq = judge_passage(p, p.index(), _passage(t))
    must = re.findall(r"(?m)^- (R\d+) MUST:", t["THIS MESSAGE"])
    return checks, coverage(_passage(t), must), unq


def _fiction(text: str) -> str:
    return " ".join(ln for ln in text.splitlines() if not ln.lstrip().startswith(("[", ">")) and ln[:1] != " ")


def _stacked(text: str) -> int:
    spans = list(re.finditer(r'"[^"]*"', text))
    return sum(1 for a, b in zip(spans, spans[1:], strict=False) if not text[a.end():b.start()].strip())


@pytest.mark.parametrize("turn", ["turn.2", "turn.13", "turn.14"])
def test_a_round6_first_draft_needs_no_revision(turn: str) -> None:
    """The repairs those turns got came from the retired answered check (I1 §2, §7): judged as a passage, the same
    first draft has no failure, no uncovered line and no unquoted speech, so it is delivered as written (one call)."""
    t = TURNS[turn]
    assert t["versions"][1:] and set(t["versions"][1:]) == {"repair"}  # recorded: one or two blind repairs
    checks, missing, unq = _judge(t)
    assert all(c["ok"] for c in checks) and not missing and not unq, (checks, missing, unq)


def test_what_the_blind_repairs_added_is_gone() -> None:
    """Delivered then vs the passage now (the first draft): turn.2's stacked quotes from two add-repairs, turn.13's
    duplicated "Mark me ... gone since last night", turn.14's closing echo of the player's statement."""
    t2, t13, t14 = TURNS["turn.2"], TURNS["turn.13"], TURNS["turn.14"]
    now = {k: _passage(t).text for k, t in TURNS.items()}
    assert _stacked(now["turn.2"]) < _stacked(_fiction(t2["delivered"]))
    added = "Plain enough for any eye to follow"  # the add that contradicted "the word came off the lanes" (note 18)
    assert added in _fiction(t2["delivered"]) and added not in now["turn.2"]
    assert _fiction(t13["delivered"]).count("Mark me") == 3 and now["turn.13"].count("Mark me") == 1
    echo = "Captain, I'll be plain. The trail stops on the road past the last house."
    assert echo in _fiction(t14["delivered"]) and echo not in now["turn.14"]


def test_turn16s_unquoted_speech_is_found_and_quoted_by_code() -> None:
    """I1 §7: three speech sentences went out as bare narration. The quote-mark check finds them (as declared speech
    standing outside quote marks); left so after the revision, code quotes the exact words."""
    t = TURNS["turn.16"]
    _, _, unq = _judge(t)
    bare = [s["text"] for s in t["first_draft"] if s["speaker"] not in (None, "none")]
    assert unq == bare
    text = _passage(t).text
    for w in unq:
        text = quote(text, w)
    assert all(f'"{w}"' in text for w in bare) and _stacked(text) == 2  # one speech of three sentences, as drafted
    assert not unquoted(Passage(text=text, speech=_passage(t).speech))


def test_the_change_line_is_never_handed_to_the_narrator_as_done() -> None:
    """F4 (01.2.7 item 3, DL-01-39): turn.14's record told the narrator "what changed (say it plainly; it is done):
    Agreed by Sevella de Belac: Get Sevella to lift the chain ...". Now the narrator gets who agreed; the goal
    restated as an agreement stays in the RESULT block, and no record line says "it is done"."""
    assert "say it plainly; it is done" in TURNS["turn.14"]["THIS MESSAGE"]
    changed = "Agreed by Sevella de Belac: Get Sevella to lift the chain so the PC can pass through the gate"
    beat = BeatEntry(restatement="Ask Captain Sevella to let you through the chain", degree=None,
                     gate_words="no roll: trivial", targets=["npc.sevella"], change_kind="persuade_to", changed=changed)
    rec = AdjudicationRecord(pc="pc.ysndil", beats=[beat])
    text = record_text(WorldState(), rec)
    assert "Sevella de Belac agrees to what was asked" in text
    assert "it is done" not in text and "say it plainly" not in text and "Get Sevella" not in text
    its = items(rec, names={"npc.sevella": "Sevella de Belac"})
    change = next(it for it in its if it.kind == "change")
    assert change.must_name and change.render == "Sevella de Belac agrees."
    refused = AdjudicationRecord(pc="pc.ysndil", beats=[beat.model_copy(update={
        "changed": "", "change_refused": "no one named to persuade"})])
    assert not next(it for it in items(refused) if it.kind == "change").must_name  # the RESULT explains it
    assert "say why plainly" not in record_text(WorldState(), refused)


def test_a_speech_broken_by_its_tag_is_one_said_record(tmp_path: Path) -> None:
    """12.3.1b item 1 (spec 019): `said` stores whole speeches. Turn.2's '"Rrakaa Mud-Walker," he says. "Missing
    since last night..."' was two records joined with a comma; a speech in the side list is one record, whole."""
    words = "Evening. The last ferry left an hour ago, and the next goes at dawn."
    model = look_model(checker=[chk()] * 2)
    dock, ctx = setup(tmp_path, model)
    model.push("narrator", lambda schema, packet: passage(  # type: ignore[arg-type]
        '"Evening," Tam Harlan says. "The last ferry left an hour ago, and the next goes at dawn." What do you do?',
        _must(packet), speech=[{"speaker": dock.ferryman, "words": words, "form": "direct"}]))
    out = play_turn(ctx, "I look over the quay.")
    assert [s["words"] for s in out.turn_record.said] == [words]
    assert len(out.turn_record.draft_versions) == 1
