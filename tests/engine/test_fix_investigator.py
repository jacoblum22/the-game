"""Spec 026 (T7; DL-12-116, DL-12-117): `/fix` works the way an investigating engineer does.

One people card for every role and the Fixer; facts in plain words; that turn's model inputs and outputs; a re-frame of
the OFFER on screen; a take-back of the unrolled pending turn; dry runs on a copy; the screen checked before anything
is applied; code guards only the spine. The Fixer is scripted here; the play roles are the offline model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.data.loader import load_rules
from engine.dm.context import TurnContext
from engine.dm.dispute import preview
from engine.dm.fixer import PROPOSALS, Investigation, tool
from engine.dm.packet import people_card, view_ctx, view_for
from engine.dm.turn import play_dispute
from engine.llm.base import Role, Routed
from engine.llm.offline import OfflineModel, ScriptedModel
from engine.resolve.types import Beat, Change
from evals.feedback_corpus import CORPUS, open_at

RULES = load_rules()
FIGHTER7 = CORPUS / "20261009-160622-fighter.db.gz"
TALKER7 = CORPUS / "20261009-160602-talker.db.gz"
EXPLORER7 = CORPUS / "20261009-160642-explorer.db.gz"
FERRY = CORPUS / "fresh-heron_ferry.db.gz"
BELIE = "npc.belie_greenwort"


def _p(kind: str, **kw: Any) -> dict[str, Any]:
    return {"kind": kind, "turn": "", "subject": "", "key": "", "value": "", "quantity": "", "amount": "",
            "fact_id": "", "evidence": [], **kw}


def _look(*calls: tuple[str, str]) -> dict[str, Any]:
    return {"calls": [{"tool": t, "arg": a} for t, a in calls], "final": False, "complaints": []}


def _decide(*proposals: dict[str, Any], found: str = "Found it.", turn: str = "") -> dict[str, Any]:
    return {"calls": [], "final": True, "complaints": [{"believes": "", "category": "rule_wrong", "turn": turn,
                                                         "verdict": "player_right", "found": found,
                                                         "proposals": list(proposals)}]}


def _dispute(save: Path, turn: str, report: str, script: list[dict[str, Any]], tmp: Path) -> tuple[Any, Any, Any]:
    store = open_at(save, turn, tmp)
    fixer = ScriptedModel({Role.FIXER: script}, fallback=False)
    ctx = TurnContext.for_store(store, model=Routed(OfflineModel(), {Role.FIXER: fixer}), rules=RULES)
    return play_dispute(ctx, report), store, fixer


# ------------------------------------------------------------------------------------------- US1, US2: what it sees


def test_one_people_card_for_every_role_and_the_fixer(tmp_path: Path) -> None:
    """DL-12-116: Belie's Letters are on the card the Reader, the Framer and the Narrator read, and on the Fixer's
    `entity` tool (round 7: the entity tool hid them, so /fix could not see she reads). No ids, no slugs."""
    store = open_at(FIGHTER7, "turn.12", tmp_path)
    try:
        st = store.state
        card = people_card(st, BELIE)
        assert card[0].startswith("Belie Greenwort (she/her; halfling): scribe and teacher of letters")
        assert "Letters (reads and writes)" in card[1] and "lic." not in "\n".join(card)
        assert not any("refusals" in ln for ln in card)  # a motive: the play roles never see it (12.10.1)
        beat = Beat(id="b", actor="pc.balak_deephelm", intent="Belie reads the list", method="ask", verb="verb.talk",
                    target=BELIE, change=Change(kind="persuade_to", what=BELIE))
        for role in (Role.READER, Role.FRAMER, Role.NARRATOR):
            view = view_for(role, st, view_ctx("I ask Belie to read it", (), [BELIE], beat))
            assert "Letters (reads and writes)" in view, role
        ent = tool(TurnContext.for_store(store, model=OfflineModel(), rules=RULES), "entity", "Belie")
        assert "Letters (reads and writes)" in ent and "refusals (hidden from the player" in ent
    finally:
        store.close()


def test_facts_in_plain_words_and_the_turns_model_calls(tmp_path: Path) -> None:
    """Round 7 dsp.1: the `turn` tool printed `is_not_alert_…_while_h = false` and Sonnet read it backwards. Now the
    fact reads as the Chance line does; `calls` shows what the Framer was given and returned (its snag)."""
    store = open_at(FIGHTER7, "turn.12", tmp_path)
    try:
        ctx = TurnContext.for_store(store, model=OfflineModel(), rules=RULES)
        t5 = tool(ctx, "turn", "turn.5")
        assert "Magby is alert to a hand" in t5 and "is_not_alert" not in t5
        t11 = tool(ctx, "turn", "turn.11")
        assert "OPEN NOW" in t11 and "fact.113 \"Belie can not read" in t11
        calls = tool(ctx, "calls", "turn.11 framer")
        assert calls.startswith("framer (haiku) was given:") and '"snags": ["fact.113"]' in calls
        assert "its view:" in calls
        assert "world (" not in tool(ctx, "calls", "turn.11")  # only the PC-knowledge roles (INV-10)
    finally:
        store.close()


def test_the_turn_listing_shows_the_effective_degree(tmp_path: Path) -> None:
    """Spec 024 hand-off: success at a cost counts as a success in the Fixer's listing (DL-01-48)."""
    store = open_at(TALKER7, "turn.14", tmp_path)
    try:
        out = tool(TurnContext.for_store(store, model=OfflineModel(), rules=RULES), "turn", "turn.12") + tool(
            TurnContext.for_store(store, model=OfflineModel(), rules=RULES), "turn", "turn.13")
        assert "success at a cost (counts as a success)" in out or "a near miss" in out
    finally:
        store.close()


# ------------------------------------------------------------------------------------------- US3: re-frame, take back


def test_belies_offer_is_reframed_with_her_letters(tmp_path: Path) -> None:
    """R2-K case: "Belie can't read, but you want me to persuade her to read", at the open OFFER. The Oracle fact is
    removed and the OFFER framed again: the new screen no longer counts "can not read"."""
    decision = _decide(_p("remove_fact", fact_id="fact.113", evidence=["fact.113"]), _p("reframe"), turn="turn.11",
                       found="Belie is a scribe and holds Letters; the 'can not read' was a coin flip.")
    out, store, _ = _dispute(FIGHTER7, "turn.12", "Belie can read; the offer says she can't",
                             [_look(("turn", "turn.11"), ("entity", "Belie"), ("recompute", "turn.11")), decision,
                              decision], tmp_path)
    try:
        text = out.response.text()
        assert "[OFFER] Persuade Belie Greenwort." in text and "can not read" not in text.split("Now:")[1]
        assert "is framed again" in text and store.state.fact_value(BELIE, "can_read_the_writing_on_the_delivery_list") \
            is None
        pause = store.state.open_pause()
        assert pause is not None and pause.pause_id != "pause.20" and pause.detail["stage"] == "offer"
    finally:
        store.close()


def test_an_impossible_goal_is_refused_by_the_gate(tmp_path: Path) -> None:
    """Fresh f01's mechanism: blind Tam asked to read a seal. `reframe` with the blindness fact: the gate refuses
    (G4, nothing spent) and no OFFER is left on screen."""
    g4 = _decide(_p("reframe", fact_id="fact.1"), turn="turn.4")
    out, store, _ = _dispute(FERRY, "turn.5", "Tam is blind", [
        _look(("entity", "Tam"), ("turn", "turn.4"), ("calls", "turn.4")), g4, g4], tmp_path)
    try:
        text = out.response.text()
        assert "[REDIRECT] Not as tried" in text and "[OFFER]" not in text and store.state.open_pause() is None
    finally:
        store.close()


def test_the_unrolled_pending_turn_is_taken_back_and_its_offer_goes(tmp_path: Path) -> None:
    """12.5.8 item 1: nothing was spent, so no evidence is needed; before spec 026 a take-back left the OFFER open
    (a `pause_opened` is not a revertible write)."""
    tb = _decide(_p("take_back", turn="turn.4"), turn="turn.4")
    out, store, _ = _dispute(FERRY, "turn.5", "Tam is blind", [_look(("entity", "Tam"), ("ledger", ""), ("said", "")),
                                                                tb, tb], tmp_path)
    try:
        text = out.response.text()
        assert "took back turn 4: its offer is withdrawn and nothing was spent" in text
        assert store.state.open_pause() is None and "[OFFER]" not in text
    finally:
        store.close()


def test_rerender_is_retired() -> None:
    assert "rerender" not in PROPOSALS and "reframe" in PROPOSALS


# ------------------------------------------------------------------------------------------- US4: dry run and check


def test_a_dry_run_shows_the_screen_and_leaves_the_game_untouched(tmp_path: Path) -> None:
    """DL-12-117: proposals run on a copy (validation included); the real save is unchanged."""
    store = open_at(FERRY, "turn.4", tmp_path)
    try:
        ctx = TurnContext.for_store(store, model=OfflineModel(), rules=RULES)
        before = (store.last_seq, sorted(t for (t,) in store.conn.execute("SELECT turn_id FROM turns")))
        inv = Investigation(calls=[("ledger", "", tool(ctx, "ledger", ""))])
        shown = tool(ctx, "try", json.dumps([_p("refund", quantity="coin", amount="2", evidence=["turn.3"])]),
                     text="charged twice", inv=inv)
        assert shown.startswith("dry run on a copy") and "Now: coin 8 (was 6)" in shown
        blind = tool(ctx, "try", json.dumps([_p("refund", quantity="coin", amount="2")]), text="x", inv=inv)
        assert "it cites no record" in blind  # validation runs in the dry run too
        replay = tool(ctx, "replay", "turn.3")
        assert replay.startswith("turn.3 replayed on a copy")
        assert (store.last_seq, sorted(t for (t,) in store.conn.execute("SELECT turn_id FROM turns"))) == before
        assert store.state.quantities["pc.wren_ashby"]["coin"].current == 6
    finally:
        store.close()


def test_the_screen_check_revises_a_decision_that_leaves_the_complaint_up(tmp_path: Path) -> None:
    """PR-12-11 step 6: an explain-only answer at Belie's open OFFER is previewed; the Fixer sees "can not read"
    still on the screen, revises to remove the fact and re-frame, that screen is checked and kept, and only the
    revised decision is applied."""
    explain = _decide(_p("explain"), turn="turn.11", found="The record has her unable to read.")
    fixed = _decide(_p("remove_fact", fact_id="fact.113", evidence=["fact.113"]), _p("reframe"), turn="turn.11",
                    found="Belie holds Letters; the 'can not read' was a coin flip.")
    out, store, fixer = _dispute(FIGHTER7, "turn.12", "Belie can read", [
        _look(("turn", "turn.11"), ("entity", "Belie"), ("recompute", "turn.11")), explain, fixed, fixed], tmp_path)
    try:
        msgs = [p.message for r, p in fixer.calls if r == Role.FIXER]
        assert len(msgs) == 4
        first_check = msgs[2].split("THE SCREEN THE PLAYER WILL SEE AFTER YOUR REPAIR")[1]
        assert "can not read the writing on the delivery list −2" in first_check  # the explain left it up
        assert "can not read" not in msgs[3].split("THE SCREEN THE PLAYER WILL SEE AFTER YOUR REPAIR")[1].split(
            "Now:")[1]
        text = out.response.text()
        assert "Belie holds Letters" in text and "can not read" not in text.split("Now:")[1]
    finally:
        store.close()


# ------------------------------------------------------------------------------------------- US5: the spine


def test_code_guards_the_spine(tmp_path: Path) -> None:
    """"I should have 50 more coin" with nothing on record: refused, plainly; a sealed name never shows in a tool."""
    store = open_at(FERRY, "turn.4", tmp_path)
    try:
        ctx = TurnContext.for_store(store, model=OfflineModel(), rules=RULES)
        inv = Investigation(calls=[("ledger", "", tool(ctx, "ledger", ""))])
        shown = preview(ctx, "I sold salt for 50", [{"believes": "", "category": "other", "turn": "",
                                                     "verdict": "player_right", "found": "x", "proposals": [
                                                         _p("refund", quantity="coin", amount="50",
                                                            evidence=["turn.9"])]}], inv.calls)
        assert "Not done: refund: turn.9 was not looked at" in shown and "coin 56" not in shown
    finally:
        store.close()
    store = open_at(EXPLORER7, "turn.9", tmp_path)
    try:
        ctx = TurnContext.for_store(store, model=OfflineModel(), rules=RULES)
        outs = [tool(ctx, t, a) for t, a in (("entity", "Vorri Stonebeard"), ("search", "who leads the refugees"),
                                             ("turn", "turn.5"), ("calls", "turn.5"), ("entity", "Morga"))]
        assert not any("Vorri" in o or "Stonebeard" in o for o in outs)
    finally:
        store.close()
