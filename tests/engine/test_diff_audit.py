"""Spec 009 part B, as spec 011 left it: the diff-mode Checker (12.3.1 source 2) runs on a sampled turn (1 in 10
by the turn id; turn.1 is one), after delivery, and only logs (DL-12-83); the profile diff on reuse (PR-00-7 step
2, 00.6.6a) and the Checker's spotlight scope."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.dm.turn import play_turn
from engine.llm.base import Role
from engine.store.events import EntityRecord, Event
from tests.engine.test_turn_adjudication import setup
from tests.engine.test_turn_narration import _must, calls, chk, claim, look_model, passage
from tests.fixtures.scene_dock import build_dock


def _names(ctx: Any) -> set[str]:
    return {e.name for e in ctx.store.state.entities.values()}


def test_the_audit_reads_the_side_list_in_words_after_delivery(tmp_path: Path) -> None:
    """The sampled diff sees the delivered passage's sentences and its side list rendered in words; what it finds is
    logged and changes nothing (a gender is off the blocking list, DL-12-80)."""
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        return passage("Tam Harlan, a woman, watches you. What do you do?", _must(packet))
    model = look_model(narrator=[draft])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk(), chk(claim(0, dock.ferryman, "identity", "gender", "woman")))
    out = play_turn(ctx, "I look over the quay.")
    msg = calls(model, Role.CHECKER)[0].message
    assert "[0] Tam Harlan, a woman, watches you.\n[1] What do you do?" in msg
    assert "THE SIDE LIST:\n- covers R1: " in msg
    assert out.response.fiction == "Tam Harlan, a woman, watches you. What do you do?"
    [e] = [e for e in out.turn_record.claim_log if e.get("source") == "sample"]
    assert (e["class"], e["verdict"], e["blocking_miss"]) == ("identity", "contradicted", False)


def test_a_figure_of_speech_is_atmosphere_not_a_claim(tmp_path: Path) -> None:
    """12.3.1 as revised: a claim needs a literal assertion about an addressable id. A clock or sealed label on a
    metaphor, or an existence claim with no id, passes as atmosphere and writes nothing."""
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        return passage("You look over the quay, and it is only the beginning. The silence presses, more than it "
                       "seems. What do you do?", _must(packet))
    model = look_model(narrator=[draft])
    dock, ctx = setup(tmp_path, model)
    before = _names(ctx)
    model.push(Role.CHECKER, chk(), chk(claim(0, "unknown", "clock", "is", "only the beginning"),
                                 claim(1, "unknown", "sealed", "is", "more than it seems"),
                                 claim(1, "unknown", "existence", "the silence", "presses")))
    out = play_turn(ctx, "I look over the quay.")
    assert [v["kind"] for v in out.turn_record.draft_versions] == ["draft"]  # delivered as drafted
    assert out.response.fiction.startswith("You look over the quay, and it is only the beginning.")
    assert _names(ctx) == before  # no "only the beginning" or "silence" furniture


def test_undeclared_elements_the_audit_finds_are_logged_only(tmp_path: Path) -> None:
    """Spec 011 (DL-12-80, DL-12-83): what the sampled audit finds undeclared is logged; audit-typed T2 never cuts
    and nothing is written after delivery."""
    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        return passage("You look over the quay; a coil of rope lies by the stair. A cutthroat waits in the dark. "
                       "What do you do?", _must(packet))
    model = look_model(narrator=[draft])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk(undeclared=[
        {"sentence": "0", "element_kind": "furniture", "name": "coil of rope", "ordinary": True},
        {"sentence": "1", "element_kind": "adversary", "name": "cutthroat", "ordinary": False}]), chk())
    before = _names(ctx)
    out = play_turn(ctx, "I look over the quay.")
    assert _names(ctx) == before
    assert "cutthroat" in out.response.fiction and "coil of rope" in out.response.fiction
    logged = [e["element"] for e in out.turn_record.claim_log if e["verdict"] == "undeclared"]
    assert logged == ["coil of rope", "cutthroat"]


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


def test_the_audit_is_sampled_by_the_turn_id() -> None:
    """Spec 011 item 1 (DL-12-83, OEQ-12-23): the skip gate is retired; 1 turn in `full_extraction_every` is
    sampled by the turn id's crc32, every other turn runs no audit."""
    from types import SimpleNamespace

    from engine.data.loader import load_rules
    from engine.dm.narration import audit_mode

    audit = dict(load_rules().pacing["claim_check"]["audit"])
    assert "skip_enabled" not in audit and audit["full_extraction_every"] == 10 and audit["mode"] == "sampled"
    assert "max_active" not in load_rules().pacing["details"]

    def ctx(turn: str) -> Any:
        return SimpleNamespace(rules=SimpleNamespace(pacing={"claim_check": {"audit": audit}}), turn_id=turn)
    modes = [audit_mode(ctx(f"turn.{n}")) for n in range(1, 101)]
    assert set(modes) == {"sampled", "off"} and 5 <= modes.count("sampled") <= 15
    assert audit_mode(ctx("turn.1")) == "sampled" and audit_mode(ctx("turn.2")) == "off"
