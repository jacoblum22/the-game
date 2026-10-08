"""Spec 009 part B: the diff-mode Checker (12.3.1 source 2, DL-12-71), the audit's undeclared elements written by
tier (12.14.13; I-175), the profile diff on reuse (PR-00-7 step 2, 00.6.6a) and the Checker's spotlight scope."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.dm.turn import play_turn
from engine.llm.base import Role
from engine.store.events import EntityRecord, Event
from tests.engine.test_turn_adjudication import setup
from tests.engine.test_turn_narration import _decl, _must, calls, chk, claim, look_model, rep
from tests.fixtures.scene_dock import build_dock


def _names(ctx: Any) -> set[str]:
    return {e.name for e in ctx.store.state.entities.values()}


def test_the_audit_reads_declarations_in_words_and_judges_what_goes_beyond(tmp_path: Path) -> None:
    """The Checker sees each sentence's declarations rendered in words; a claim beyond them is judged against the
    store (a contradicted pronoun is redrafted to the store's value)."""
    holder: dict[str, Any] = {}

    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        return {"sentences": [_decl("Tam Harlan, a woman, watches you.", _must(packet),
                                    about=[holder["dock"].ferryman]), _decl("What do you do?")]}
    model = look_model(narrator=[draft, lambda s, p: rep(0, "Tam Harlan watches you.", _must(p))])
    dock, ctx = setup(tmp_path, model)
    holder["dock"] = dock
    model.push(Role.CHECKER, chk(claim(0, dock.ferryman, "identity", "gender", "woman")), chk())
    out = play_turn(ctx, "I look over the quay.")
    msg = calls(model, Role.CHECKER)[0].message
    assert "[0] Tam Harlan, a woman, watches you.\n    declares: R1 (" in msg
    assert f"about Tam Harlan ({dock.ferryman})" in msg and "    declares: nothing" in msg
    assert out.response.fiction == "Tam Harlan watches you. What do you do?"


def test_an_unexpressed_declaration_is_dropped_and_the_line_is_owed_again(tmp_path: Path) -> None:
    """(ii): a declared handle the sentence never says no longer covers its must-name line (12.3.1a), so the repair
    adds a sentence for it; the sentence itself stands."""
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        return {"sentences": [_decl("The fog lies thick on the water.", _must(packet)), _decl("What do you do?")]}
    model = look_model(narrator=[draft, lambda s, p: rep("add", "You look over the quay.", _must(p))])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk(unexpressed=[{"sentence": "0", "ref": "R1", "says_otherwise": False}]), chk())
    out = play_turn(ctx, "I look over the quay.")
    repair = calls(model, Role.NARRATOR)[1].message
    assert "MISSING" in repair and "R1" in repair.split("MISSING", 1)[1]
    assert out.response.fiction == "The fog lies thick on the water. You look over the quay. What do you do?"
    stats = out.turn_record.draft_versions[-1]["stats"]
    assert stats["audit_unexpressed"] == 1


def test_a_figure_of_speech_is_atmosphere_not_a_claim(tmp_path: Path) -> None:
    """12.3.1 as revised: a claim needs a literal assertion about an addressable id. A clock or sealed label on a
    metaphor, or an existence claim with no id, passes as atmosphere and writes nothing."""
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        return {"sentences": [_decl("You look over the quay, and it is only the beginning.", _must(packet)),
                              _decl("The silence presses, more than it seems."), _decl("What do you do?")]}
    model = look_model(narrator=[draft])
    dock, ctx = setup(tmp_path, model)
    before = _names(ctx)
    model.push(Role.CHECKER, chk(claim(0, "unknown", "clock", "is", "only the beginning"),
                                 claim(1, "unknown", "sealed", "is", "more than it seems"),
                                 claim(1, "unknown", "existence", "the silence", "presses")))
    out = play_turn(ctx, "I look over the quay.")
    assert [v["kind"] for v in out.turn_record.draft_versions] == ["draft"]  # delivered as drafted
    assert out.response.fiction.startswith("You look over the quay, and it is only the beginning.")
    assert _names(ctx) == before  # no "only the beginning" or "silence" furniture


def test_undeclared_elements_are_written_by_tier(tmp_path: Path) -> None:
    """I-175: what the audit finds undeclared is folded back as the sentence's declaration and written by its tier:
    ordinary furniture is written (T1a), an adversary no record line delivers is cut (T2)."""
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        return {"sentences": [_decl("You look over the quay; a coil of rope lies by the stair.", _must(packet)),
                              _decl("A cutthroat waits in the dark."), _decl("What do you do?")]}
    model = look_model(narrator=[draft])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk(undeclared=[
        {"sentence": "0", "element_kind": "furniture", "name": "coil of rope", "ordinary": True},
        {"sentence": "1", "element_kind": "adversary", "name": "cutthroat", "ordinary": False}]))
    out = play_turn(ctx, "I look over the quay.")
    assert "coil of rope" in _names(ctx) and "cutthroat" not in _names(ctx)
    assert "cutthroat" not in out.response.fiction and "coil of rope" in out.response.fiction
    assert out.turn_record.draft_versions[-1]["stats"]["audit_new"] == 2


def test_profile_diff_on_reuse(tmp_path: Path) -> None:
    """PR-00-7 step 2 for an existing entity: an empty slot is written (`narrated`), the same value is a no-op, a
    different one is a contradiction unless this turn's record explains it (then it supersedes)."""
    from engine.dm.mentions import write_mentions

    dock = build_dock(tmp_path)

    def say(value: str, because: str | None = None) -> Any:
        with dock.store.transaction("turn.1") as tx:
            return write_mentions([{"kind": "npc", "name": "Tam Harlan",
                                    "implied": [{"predicate": "hair", "value": value}]}],
                                  tx=tx, rules=dock.rules, because=because), len(tx.events)
    res, n = say("grey and cropped")
    st = dock.store.state
    f = st.facts[st.details[dock.ferryman]["hair"].fact_id]
    assert res.reused == {"Tam Harlan": dock.ferryman} and n == 1 and f.certainty == "narrated"
    res, n = say("grey and cropped")
    assert n == 0 and res.details_used == [f.id] and not res.contradictions  # same: a no-op, but stated
    res, n = say("long and black")
    assert n == 0 and res.contradictions == [("Tam Harlan", "hair", "grey and cropped")]
    res, n = say("shaved", because="R2")
    assert n == 1 and dock.store.state.facts[dock.store.state.details[dock.ferryman]["hair"].fact_id].value == "shaved"


def test_the_checker_may_name_absent_people_the_turn_speaks_of(tmp_path: Path) -> None:
    """12.2.4 item 3 (P-085): the spotlight joins the Checker's ids, marked `not here`; a label someone here also
    carries stays theirs."""
    from engine.dm.roles.checker import checker_ids, entity_lines

    dock = build_dock(tmp_path)
    with dock.store.transaction("turn.1") as tx:
        tx.add(Event.of("entity_created", source="fixture", rule_id="00.6.6", entity=EntityRecord(
            id="npc.odo_brant", kind="npc", name="Odo Brant", visibility="shown", data={"role": "ferryman"})))
    st = dock.store.state
    ids = checker_ids(st, message="Where is Odo Brant?", rules=dock.rules)
    assert "npc.odo_brant" in ids and "npc.odo_brant" not in checker_ids(st, rules=dock.rules)
    lines = {ln.split(":", 1)[0]: ln for ln in entity_lines(st, ids)}
    assert lines["npc.odo_brant"].endswith("; not here") and "ferryman" not in lines["npc.odo_brant"]
    assert lines[dock.ferryman].endswith("; here") and "ferryman" in lines[dock.ferryman]


def test_restating_a_known_lead_is_supported(tmp_path: Path) -> None:
    """Live loop 009 B: the narrator retells an opening lead ("a quarrel in the inn turns to a challenge"); the audit
    labelled it a clock tick or a position here. A claim that restates a lead the character knows is supported."""
    from engine.audit.claims import check_claims

    dock = build_dock(tmp_path)
    with dock.store.transaction("turn.1") as tx:
        tx.add(Event.of("entity_created", source="fixture", rule_id="12.16.16", entity=EntityRecord(
            id="thr.lead_1", kind="thread", name="lead", visibility="available",
            data={"status": "active", "text": "a quarrel in the inn turns to a challenge"})))
    claims = [{"sentence": 0, "subject": dock.place, "class": "clock", "predicate": "quarrel progress",
               "value": "turning toward a challenge", "asserts_change": True},
              {"sentence": 0, "subject": dock.place, "class": "clock", "predicate": "the tide",
               "value": "turning toward a flood", "asserts_change": True},
              {"sentence": 1, "subject": "unknown", "class": "action", "predicate": "no one",
               "value": "names him", "asserts_change": False}]
    got = [v.verdict for v in check_claims(claims, dock.store.state, None, [], rules=dock.rules)]
    assert got == ["supported", "unsourced_change", "supported"]
    from engine.dm.narration import _in_lead  # an "undeclared" element the lead names is spoken of, not new

    assert _in_lead(dock.store.state, "the quarrel") and not _in_lead(dock.store.state, "a cutthroat")


def test_the_audit_skip_stays_off_until_the_gate_is_met(tmp_path: Path) -> None:
    """OEQ-12-23: with `skip_enabled` false the diff runs every turn; once enabled, a fully declared turn with no
    SPEECH part skips it, and 1 turn in `full_extraction_every` is sampled for a full extraction."""
    from types import SimpleNamespace

    from engine.audit.declare import DeclaredSentence
    from engine.data.loader import load_rules
    from engine.dm.adjudication import AdjudicationRecord
    from engine.dm.narration import audit_mode

    audit = dict(load_rules().pacing["claim_check"]["audit"])
    assert audit["skip_enabled"] is False and audit["full_extraction_every"] == 10
    decl = [DeclaredSentence(text="You look.", refs=["R1"])]
    bare = [DeclaredSentence(text="A man waits.")]

    def ctx(turn: str, **cfg: Any) -> Any:
        return SimpleNamespace(rules=SimpleNamespace(pacing={"claim_check": {"audit": {**audit, **cfg}}}),
                               turn_id=turn)
    rec = AdjudicationRecord()
    assert audit_mode(ctx("turn.3"), rec, decl) == "diff"
    turns = [f"turn.{n}" for n in range(1, 41)]
    modes = [audit_mode(ctx(t, skip_enabled=True), rec, decl) for t in turns]
    assert 1 <= modes.count("sample") <= 10 and set(modes) == {"sample", "skip"}  # about 1 in 10 sampled
    assert {audit_mode(ctx(t, skip_enabled=True), rec, bare) for t in turns} == {"sample", "diff"}
