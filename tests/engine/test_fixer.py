"""Spec 022 F6: `/fix` as an investigator (PR-12-11). The Fixer is scripted here; the tools, the validation, the joint
application on one snapshot and the found → did → Now: answer are code, tested on the round-6 saves (I3 §5)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.data.loader import load_rules
from engine.dm.dispute import settle_dispute
from engine.dm.fixer import MAX_STEPS, tool
from engine.llm.base import Role, Routed
from engine.llm.offline import OfflineModel, ScriptedModel
from evals.feedback_corpus import CORPUS, Ctx, open_at

RULES = load_rules()
FIGHTER = CORPUS / "20261008-233000-fighter.db.gz"
TALKER = CORPUS / "20261008-192926-talker.db.gz"
PC = "pc.evine_oakwell"


def _calls(*calls: tuple[str, str]) -> dict[str, Any]:
    return {"calls": [{"tool": t, "arg": a} for t, a in calls], "final": False, "complaints": []}


def _p(kind: str, **kw: Any) -> dict[str, Any]:
    return {"kind": kind, "turn": "", "subject": "", "key": "", "value": "", "quantity": "", "amount": "",
            "fact_id": "", "evidence": [], **kw}


def _final(*complaints: dict[str, Any]) -> dict[str, Any]:
    return {"calls": [], "final": True, "complaints": [
        {"believes": "", "category": "other", "turn": "", "verdict": "player_right", "found": "Found it.",
         "proposals": [], **c} for c in complaints]}


def _settle(save: Path, turn: str, report: str, script: list[dict[str, Any]], tmp: Path) -> tuple[Any, Any, Any]:
    store = open_at(save, turn, tmp)
    model = ScriptedModel({Role.FIXER: [*script, script[-1]]}, fallback=False)  # spec 026: the screen check keeps it
    ctx = Ctx(store, RULES, model, turn)
    return settle_dispute(ctx, report), store, model


def test_the_g4_turn_is_taken_back_and_both_complaints_answer_on_one_snapshot(tmp_path: Path) -> None:
    """233000 dsp.3 + dsp.4 (I3 §5): the refused threat still cost a strike (Vitality 1 → 0, staggered). The take-back
    is applied once, and the answer for both complaints ends in one `Now:` line with what came back (12.5.8)."""
    report = ("I chose Presence and the story played out my threat with no roll shown, then the game said \"Not as "
              "tried\" as if it never happened. Which is it? Did I speak or not?")
    res, store, model = _settle(FIGHTER, "turn.15", report, [
        _calls(("turn", "turn.14"), ("recompute", "turn.14"), ("ledger", "")),
        _final({"believes": "the refused threat still cost you a blow", "category": "contradiction", "turn": "turn.14",
                "found": "Turn 14's threat was refused before any roll, yet Dunwen still struck you.",
                "proposals": [_p("take_back", turn="turn.14", evidence=["turn.14"])]},
               {"believes": "you want to know why nothing was rolled", "category": "ruling_question",
                "turn": "turn.14", "verdict": "record_stands",
                "found": "Nothing was rolled: two refusals were counted against the threat.",
                "proposals": [_p("explain")]})], tmp_path)
    try:
        st = store.state
        assert res.kind == "taken_back" and res.reverted
        assert st.quantities[PC]["vitality"].current == 1  # the free strike is undone
        text = res.text
        assert text.startswith("[CORRECTION] Turn 14's threat") and "Done: took back turn 14" in text
        assert "Now: Vitality 1/12 (was 0/12)" in text and text.count("Now:") == 1
        assert len(res.records) == 2 and {r["report"] for r in res.records} == {"rep.1"}
        assert res.records[0]["evidence"] == ["turn('turn.14')", "recompute('turn.14')", "ledger('')"]
        assert [k for k in st.fact_keys if "|correction." in k] == ["npc.dunwen_redmore|correction.1"]  # the old
        # code's pin (dsp.1, turn 9) is all there is: no complaint text is pinned now
        assert len([c for c in model.calls if c[0] == Role.FIXER]) == 3  # look, decide, check the screen
    finally:
        store.close()


def test_a_mechanical_change_needs_evidence_the_tools_returned(tmp_path: Path) -> None:
    """INV-9: a deduction citing nothing, or a turn the Fixer never looked at, is refused and the answer says why;
    the same deduction citing the turn it read is applied (192926 dsp.3: the round's coin was never taken)."""
    report = "The coin for the round is also not accounted for."
    res, store, _ = _settle(TALKER, "turn.8", report, [
        _calls(("turn", "turn.7"), ("ledger", ""), ("search", "round coin")),
        _final({"turn": "turn.7", "found": "Turn 7 says the coin for the round is spent, but your purse never moved.",
                "proposals": [_p("deduct", quantity="coin", amount="1"),
                              _p("deduct", quantity="coin", amount="1", evidence=["frame.99"]),
                              _p("deduct", quantity="coin", amount="1", evidence=["turn.7"])]})], tmp_path)
    try:
        coin = store.state.quantities["pc.wila_bramblefoot"]["coin"].current
        assert "Not done: deduct: it cites no record" in res.text
        assert "Not done: deduct: frame.99 was not looked at" in res.text
        assert f"Done: your coin {coin + 1} → {coin}." in res.text and f"Now: coin {coin} (was {coin + 1})" in res.text
    finally:
        store.close()


def test_a_correction_writes_the_value_never_the_report(tmp_path: Path) -> None:
    """PR-12-11 step 5: the complaint's words are never a fact; testimony settled from a refusal goes back to words."""
    report = ("The Chance line for the threat is garbled: \"said will give no word out while you evine oakwell has a "
              "hand\". It should read plainly, and Dunwen is \"her\", not \"him\".")
    res, store, _ = _settle(FIGHTER, "turn.9", report, [
        _calls(("said", "Dunwen Redmore"), ("recompute", "turn.8")),
        _final({"turn": "turn.8", "found": "The garbled line is a refusal of Dunwen's settled as a fact.",
                "proposals": [_p("set_fact", subject="npc.dunwen_redmore", key="mood", value=report,
                                 evidence=["turn.8"]),
                              _p("correct_testimony", fact_id="fact.103")]})], tmp_path)
    try:
        st = store.state
        pred = "said.will_give_no_word_out_while_pc_evine_oakwell_has_a_hand"
        assert "Not done: set fact: the value must be the corrected value" in res.text
        assert st.fact_value("npc.dunwen_redmore", pred) is None
        assert "their words again, not a settled fact" in res.text and "Now:" in res.text
        assert not any(isinstance(f.value, str) and "garbled" in f.value for f in st.facts.values())
    finally:
        store.close()


def test_the_tools_never_write_and_never_show_sealed_content(tmp_path: Path) -> None:
    store = open_at(FIGHTER, "turn.15", tmp_path)
    try:
        ctx = Ctx(store, RULES, None, "turn.15")
        before = store.state.last_seq
        outs = [tool(ctx, t, a) for t, a in (("turn", "turn.14"), ("entity", "Dunwen Redmore"), ("entity", "me"),
                                             ("search", "word Dunwen"), ("recompute", "frame.4"), ("ledger", ""),
                                             ("said", ""))]
        assert store.state.last_seq == before and all(outs)
        assert "REVERTED" not in outs[0] and "584" in outs[0] and "g4" in outs[0]  # the G4 and the free strike
        sealed = [f for f in store.state.facts.values() if f.id in store.state.seals or f.visibility not in
                  ("shown", "available")]
        assert sealed and not any(f"{f.id} " in o for f in sealed for o in outs)
    finally:
        store.close()


def test_the_investigation_is_bounded(tmp_path: Path) -> None:
    """3-6 tool calls (feedback.investigate.steps): a Fixer that keeps asking is made to decide."""
    store = open_at(FIGHTER, "turn.9", tmp_path)
    greedy = _calls(("search", "word"), ("ledger", ""), ("said", ""))
    done = _final({"found": "Done looking."})
    model = ScriptedModel({Role.FIXER: [greedy, greedy, greedy, done, done]}, fallback=False)
    try:
        res = settle_dispute(Ctx(store, RULES, model, "turn.9"), "something is off")
        assert len(res.records[0]["evidence"]) == MAX_STEPS and res.text.startswith("[FIX] Done looking.")
        assert len(model.calls) == 5  # two answers of three calls, a third refused (no calls left), the decision,
        # and the screen check (spec 026), which keeps it
    finally:
        store.close()


def test_the_fixer_runs_on_its_own_model() -> None:
    """DL-12-105: which model plays the Fixer is configuration; play stays on the play model."""
    fixer = ScriptedModel({Role.FIXER: [_final({})]}, fallback=False)
    routed = Routed(OfflineModel(), {Role.FIXER: fixer})
    from engine.llm.base import Packet

    routed.fill(Role.FIXER, {}, Packet(message="x"), turn_id=None, attempt=0)
    routed.fill(Role.TESTIMONY, {"type": "object"}, Packet(message="x"), turn_id=None, attempt=0)
    assert [r for r, _ in fixer.calls] == [Role.FIXER] and routed.provider == "offline"
