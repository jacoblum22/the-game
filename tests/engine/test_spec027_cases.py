"""Spec 027: the made-up and edge cases of specs/027-round7-cleanup/cases.md (committed before implementing).

B (DL-12-122): a person's look and a thing's description reach the narrator when they first appear in a scene or when
the player looks at or asks about them; no counting or tracking. C (DL-12-123): a /fix re-frame's note for the Framer,
never odds. Hand-offs: the auto roll above the passage (DL-12-124), slug-free labels and refusals, the gate's name
(DL-12-125), the retired `pay`, the narrator's testimony line, the dispute guard, READING and the numeral check."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from engine.audit.declare import Passage, SceneIndex, scan_sentence, sentences_of
from engine.data.loader import load_rules
from engine.dm import dispute
from engine.dm.adjudication import AdjudicationRecord, BeatEntry
from engine.dm.context import TurnContext
from engine.dm.oof import redirect_block
from engine.dm.response import OofBlock, Response
from engine.dm.roles import narrator as nr
from engine.dm.roles.prompts import load_prompt
from engine.dm.turn import play_dispute
from engine.llm.base import Role, Routed
from engine.llm.offline import OfflineModel, ScriptedModel
from engine.resolve import change
from engine.resolve.gate import GateDecision, Redirect, RedirectOption
from engine.retrieve.scene import READING
from engine.store.events import Event
from engine.text.render import slug_words
from evals.feedback_corpus import CORPUS, open_at
from tests.fixtures.scene_dock import _entity, _fact, build_dock

RULES = load_rules()
SCAR = "a long scar along the jaw"


class _Done(Exception):
    pass


def _packet(dock: Any, message: str = "", *, turn: str = "turn.5", purpose: str = "turn",
            beats: list[BeatEntry] | None = None) -> str:
    """The narrator's VIEW and THIS MESSAGE for one turn, captured before any model call (nothing is committed)."""
    got: list[Any] = []

    def capture(schema: Any, packet: Any) -> dict[str, Any]:
        got.append(packet)
        raise _Done

    ctx = TurnContext.for_store(dock.store, model=ScriptedModel({Role.NARRATOR: [capture]}), rules=RULES)
    rec = AdjudicationRecord(turn_id=turn, pc=dock.pc, beats=beats or [])
    try:
        with dock.store.transaction(turn) as tx:
            ctx.tx = tx
            nr.draft(ctx, rec, player_message=message, purpose=purpose)  # type: ignore[arg-type]
    except _Done:
        pass
    finally:
        ctx.tx = None
    return f"{got[0].view}\n{got[0].message}"


def _place(dock: Any, name: str) -> str:
    with dock.store.transaction() as tx:
        return _entity(tx, "place", name, data={"place_kind": "landmark"})


def _move(dock: Any, who: str, where: str, turn: str | None = None) -> None:
    with dock.store.transaction(turn) as tx:
        tx.add(Event.of("position_set", source="fixture", rule_id="10.1.1", entity=who, location=where))


def _person(dock: Any, name: str, where: str | None = None, **data: Any) -> str:
    with dock.store.transaction() as tx:
        eid = _entity(tx, "npc", name, data=data)
        tx.add(Event.of("position_set", source="fixture", rule_id="10.1.1", entity=eid, location=where or dock.place))
    return eid


def _grza(dock: Any, **kw: Any) -> str:
    return _person(dock, "Grza", role="scholar", pronouns="she/her", detail=SCAR, demeanor="weary",
                   voice={"register": "dry", "habit": "taps her ink-stained fingers"}, **kw)


def _thing(dock: Any, kind: str, name: str, facts: dict[str, Any], source: str = "narration") -> str:
    with dock.store.transaction() as tx:
        eid = _entity(tx, kind, name, data={})
        tx.add(Event.of("position_set", source="fixture", rule_id="10.1.1", entity=eid, location=dock.place))
        for k, v in facts.items():
            tx.add(Event.of("fact_set", {"source": source}, source="fixture", rule_id="00.6.6", fact_id=tx.mint("fact"),
                            subject=eid, predicate=k, value=v, visibility="shown"))
    return eid


# ------------------------------------------------------------------------------------------- B: setting once


def test_c1_the_look_at_the_opening_then_not_on_a_talk_turn(tmp_path: Path) -> None:
    dock = build_dock(tmp_path)
    _grza(dock)
    assert SCAR in _packet(dock, purpose="scene_open")
    talk = _packet(dock, "I ask Grza about the road north.")
    assert "scar" not in talk
    assert "Grza" in talk and "she/her" in talk and "weary" in talk and "ink-stained" in talk  # who, manner, voice
    dock.store.close()


def test_c2_appears_leaves_and_returns(tmp_path: Path) -> None:
    dock = build_dock(tmp_path)
    market = _place(dock, "The Fish Market")
    carter = _person(dock, "Odo Brant", market, role="carter", pronouns="he/him", detail="a split lip")
    _move(dock, carter, dock.place, "turn.5")
    assert "split lip" in _packet(dock, "I wait.", turn="turn.5")  # came in this turn
    assert "split lip" not in _packet(dock, "I wait.", turn="turn.6")
    _move(dock, carter, market, "turn.7")
    assert "Odo Brant" not in _packet(dock, "I wait.", turn="turn.7").split("SCENE SETTING")[-1]
    _move(dock, carter, dock.place, "turn.8")
    assert "split lip" in _packet(dock, "I wait.", turn="turn.8")  # a return is a new appearance (A2)
    assert "split lip" not in _packet(dock, "I wait.", turn="turn.9")
    dock.store.close()


@pytest.mark.parametrize("message, shown", [
    ("I study Grza's face.", True),                      # C3: a look mid-scene
    ("Who is Grza?", True),                              # C4: asks about her
    ("What does Grza look like?", True),
    ("I ask Grza about the road.", False),               # asks her, not about her (A3)
    ("I order a drink from the ferryman.", False),
])
def test_c3_c4_looked_at_or_asked_about(tmp_path: Path, message: str, shown: bool) -> None:
    dock = build_dock(tmp_path)
    _grza(dock)
    assert (SCAR in _packet(dock, message)) is shown
    dock.store.close()


def test_c5_c9_each_scene_opening_and_a_look_around_show_every_look(tmp_path: Path) -> None:
    dock = build_dock(tmp_path)
    _grza(dock)
    for purpose in ("scene_open", "opening"):
        assert SCAR in _packet(dock, purpose=purpose)
    assert SCAR not in _packet(dock, "I nod.")
    assert SCAR in _packet(dock, "I look around the dock.")  # as places (DL-12-99)
    dock.store.close()


def test_c6_c7_a_bill_read_twice_and_a_ruled_state(tmp_path: Path) -> None:
    dock = build_dock(tmp_path)
    bill = _thing(dock, "item", "hiring bill on the doorpost",
                  {"text": "the Moot is hiring", "location": "nailed to the doorpost at a slant"})
    chest = _thing(dock, "object", "iron chest", {"locked": "locked fast"}, source="ruling")
    with dock.store.transaction() as tx:
        _fact(tx, chest, "detail.material", "iron-bound oak")
    read = _packet(dock, "I read the bill.", beats=[BeatEntry(restatement="Read the bill", targets=[bill],
                                                               verb="verb.observe")])
    other = _packet(dock, "I nod to the ferryman.", turn="turn.6")
    again = _packet(dock, "I read the bill again.", turn="turn.7")
    assert "the Moot is hiring" in read and "at a slant" in read
    assert "hiring bill on the doorpost" in other and "at a slant" not in other and "the Moot is hiring" not in other
    assert "at a slant" in again
    assert "locked fast" in other and "iron-bound" not in other  # the ruled state stays; the look goes (A4)
    dock.store.close()


def test_c8_nothing_is_tracked(tmp_path: Path) -> None:
    dock = build_dock(tmp_path)
    _grza(dock)
    seq = dock.store.last_seq
    assert _packet(dock, "I nod.") == _packet(dock, "I nod.")
    assert dock.store.last_seq == seq
    dock.store.close()


def test_c10_c11_an_unnamed_person_by_label_and_pronouns_kept(tmp_path: Path) -> None:
    dock = build_dock(tmp_path)
    _person(dock, "Odo Grey", role="scholar", pronouns="she/her", name_known=False, detail=SCAR)
    assert SCAR in _packet(dock, "I study the scholar's face.")
    plain = _packet(dock, "I nod.")
    assert SCAR not in plain and re.search(r"present: the scholar.*she/her", plain)
    dock.store.close()


# ------------------------------------------------------------------------------------------- C: the /fix note


@pytest.mark.parametrize("value, note, left_out", [
    ("he outranks the guard; the guard should simply let him in", "he outranks the guard; the guard should simply "
     "let him in", False),
    ("make it 90%", None, True),                                     # C14: odds stay the Framer's
    ("no roll: it should just work", None, True),
    ("easy difficulty", None, True),
    ("first line\nsecond line", "first line", False),                # C15
    ("x" * 300, "x" * 199 + "…", False),
    ("", None, False),
])
def test_c14_c15_the_note_is_one_line_and_never_odds(value: str, note: str | None, left_out: bool) -> None:
    assert dispute.framer_note(value) == (note, left_out)


class _Spy:
    """The offline model, keeping every Framer packet."""

    provider = "offline"

    def __init__(self) -> None:
        self.model, self.framer = OfflineModel(), []

    def fill(self, role: Role, schema: Any, packet: Any, **kw: Any) -> Any:
        if role == Role.FRAMER:
            self.framer.append(packet.message)
        return self.model.fill(role, schema, packet, **kw)


def _reframe(tmp: Path, value: str) -> tuple[Any, _Spy]:
    decision = {"calls": [], "final": True, "complaints": [{
        "believes": "", "category": "rule_wrong", "turn": "turn.11", "verdict": "player_right", "found": "Found it.",
        "proposals": [{"kind": "reframe", "turn": "", "subject": "", "key": "", "value": value, "quantity": "",
                       "amount": "", "fact_id": "", "evidence": []}]}]}
    store = open_at(CORPUS / "20261009-160622-fighter.db.gz", "turn.12", tmp)
    spy = _Spy()
    fixer = ScriptedModel({Role.FIXER: [{"calls": [{"tool": "turn", "arg": "turn.11"}], "final": False,
                                         "complaints": []}, decision, decision]}, fallback=False)
    ctx = TurnContext.for_store(store, model=Routed(spy, {Role.FIXER: fixer}), rules=RULES)
    out = play_dispute(ctx, "Belie is a scribe; she reads")
    store.close()
    return out, spy


def test_c13_the_note_reaches_the_framer_as_context(tmp_path: Path) -> None:
    out, spy = _reframe(tmp_path, "Belie is a scribe; she reads her own lists")
    assert any("note from the review" in m and "Belie is a scribe; she reads her own lists" in m for m in spy.framer)
    assert "is framed again" in out.response.text()


def test_c14_a_note_with_odds_is_not_passed_and_the_reframe_runs(tmp_path: Path) -> None:
    out, spy = _reframe(tmp_path, "make it 90%: no roll")
    assert spy.framer and not any("note from the review" in m for m in spy.framer)
    text = out.response.text()
    assert "is framed again" in text and "odds and rolls are the Framer's" in text


def test_c16_value_keeps_its_meaning_on_other_kinds() -> None:
    assert dispute.framer_note(None) == (None, False)  # only `_reframe` reads a note; set_fact's value is untouched
    assert "framer_note" not in dispute._apply.__code__.co_names  # noqa: SLF001


# ------------------------------------------------------------------------------------------- hand-offs


def _blocks(*texts: tuple[str, str]) -> list[OofBlock]:
    return [OofBlock(kind=k, text=t) for k, t in texts]  # type: ignore[arg-type]


def test_c18_an_auto_roll_leads_the_passage() -> None:
    r = Response(phase="play", fiction="You find the bench rung and the faces part.", oof_blocks=_blocks(
        ("NOTE", "[JOURNAL] noted"), ("OFFER", "[OFFER — auto] Learn from Mago."),
        ("RESULT", "[RESULT] d20 20 → 24 vs 10 · critical success")))
    text = r.text()
    assert text.index("[OFFER — auto]") < text.index("[RESULT]") < text.index("You find") < text.index("[JOURNAL]")


def test_c19_an_explicit_commit_keeps_the_order() -> None:
    r = Response(phase="play", fiction="You shove.", oof_blocks=_blocks(("RESULT", "[RESULT] d20 20 · critical success")))
    assert r.text().index("You shove.") < r.text().index("[RESULT]")


def test_c20_no_index_digit_in_a_label(tmp_path: Path) -> None:
    from engine.audit.fallback import fact_sentence

    assert slug_words("furniture.0") == "furniture" and slug_words("wound.2.depth") == "wound depth"
    dock = build_dock(tmp_path)
    with dock.store.transaction() as tx:
        fid = _fact(tx, dock.place, "furniture.0", "a long trestle table")
    assert fact_sentence(dock.store.state, dock.store.state.facts[fid]) == \
        "The Night Dock's furniture: a long trestle table."
    dock.store.close()


SLUG = re.compile(r"_|\b\w+\.\w+\.|\bTrue\b|\bFalse\b|is False")


def test_c21_every_gate_reason_reads_without_slugs(tmp_path: Path) -> None:
    dock = build_dock(tmp_path)
    with dock.store.transaction() as tx:
        eyes = _fact(tx, dock.ferryman, "detail.eyes", "milk-white")
        reads = _fact(tx, dock.ferryman, "can_read_the_writing", False)
    st = dock.store.state
    opt = [RedirectOption(kind="intent", verb="verb.observe", method="look for another way")]
    lines = {}
    for kind, missing in (("license", "lic.lang.letters"), ("deed_branch", "deed.martial"),
                          ("condition", "cond.grabbed"), ("canon", "canon"), ("zero_reach", "zero"),
                          ("fact", eyes), ("fact", reads), ("fact", "fact.999")):
        dec = GateDecision(gate="G4", verb="verb.observe", fact_cited=missing if kind == "fact" else None,
                           redirect=Redirect(intent="read it", missing=missing, missing_kind=kind,  # type: ignore[arg-type]
                                             options=opt))
        lines[missing] = redirect_block(dec, state=st, rules=RULES).text.splitlines()[0]
    assert all(not SLUG.search(x) for x in lines.values()), lines
    assert "Tam Harlan's eyes: milk-white" in lines[eyes]
    assert "Tam Harlan cannot read the writing" in lines[reads]
    assert "something already settled" in lines["fact.999"]
    dock.store.close()


@pytest.mark.parametrize("site, name, desc", [("river_ford", "the gate", "the gate, by the ford"),
                                              ("hill", "the hill gate", "the hill gate")])
def test_c22_the_gate_is_called_the_gate(site: str, name: str, desc: str) -> None:
    from engine.gen.world_seed import build_answered

    gate = next(p for p in build_answered(3, {"ws.q.haven_site": site}).record["places"] if p["id"].endswith(".gate"))
    assert (gate["name"], gate["desc"]) == (name, desc)


def test_c23_pay_is_gone() -> None:
    assert not hasattr(change, "pay")
    src = (Path(__file__).parents[2] / "engine" / "resolve" / "pipeline.py").read_text(encoding="utf-8")
    assert not re.search(r"\bpay\(", src)


def test_c24_the_narrator_may_improvise_ordinary_knowledge_as_testimony() -> None:
    p = load_prompt("narrator")
    assert "what someone knows" not in p
    assert "Characters may say what they believe and what their trade\n  and town know (testimony)" in p
    assert "a hook's terms and mystery facts come only from the record and their SPEAKER CARD" in p


def test_c25_harmless_knowledge_facts_can_be_corrected() -> None:
    assert not "knows_your_rank".startswith(dispute.CASE_PREDICATES)
    assert all(p.startswith(dispute.CASE_PREDICATES) for p in ("points_to.case_1", "case.ewe", "clue.found"))


@pytest.mark.parametrize("text, hit", [("what did they say about the notice?", False),
                                       ("what did the ferry notice say?", True), ("I read the bill", True)])
def test_c26_reading_is_writing_not_people(text: str, hit: bool) -> None:
    assert bool(READING.search(text)) is hit


def test_c27_the_players_own_sum_is_not_a_numeral_failure(tmp_path: Path) -> None:
    dock = build_dock(tmp_path)
    st = dock.store.state

    def fails(sentence: str, said: str) -> bool:
        idx = SceneIndex.of(st, said=said)
        s = sentences_of(Passage(text=sentence))[0][0]
        return any("count" in f.why for f in scan_sentence(s, idx, rules=RULES).failures)

    assert not fails("You set ten silver on the table.", "I offer ten silver for the crossing.")
    assert fails("The fare is 12 silver.", "I offer ten silver for the crossing.")  # a count nobody gave still fails
    dock.store.close()
