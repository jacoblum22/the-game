"""engine/dm/oof.py: the 12.15 OOF blocks, rendered from computed records (they DO carry numbers; fiction does not)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine import ids
from engine.dm.oof import (
    OofBlock,
    clarify_block,
    create_block,
    last_chance_block,
    near_miss_block,
    near_miss_choices,
    note_block,
    offer_block,
    offer_choices,
    offer_view,
    ordered,
    recap_block,
    redirect_block,
    seed_block,
    status_block,
    warning_block,
)
from engine.harm.lethal import LethalTrigger
from engine.harm.threshold import Menu, MenuOption, Situation
from engine.resolve.gate import GateDecision, Redirect, RedirectOption
from engine.resolve.types import Frame, RollResult
from engine.store.events import EntityRecord, Event
from tests.engine.test_resolve_frame import check
from tests.engine.test_resolve_scene import Scene

LEARN = {"change": {"kind": "learn", "what": None}}  # 01.4.7 (spec 023): a secret frame is keyed on a learn goal


@pytest.fixture
def s(tmp_path: Path) -> Scene:
    sc = Scene.new(tmp_path)
    sc.add("npc", "Guard", attributes={"wits": 1, "agility": 1, "might": 2})
    return sc


def _frame(s: Scene, **kw: Any) -> Frame:
    f = check(s, stakes_source="consumed_resource",
              threatened_cost={"menu_id": "cost.drain", "form_intent": "you tire"},
              alternate_cost={"menu_id": "cost.shortfall", "form_intent": "you get less far"}, **kw)
    assert isinstance(f, Frame)
    return f


def test_offer_block_is_the_12_15_2_template(s: Scene) -> None:
    f = _frame(s)
    blk = offer_block(f, rules=s.rules, fate=1)
    lines = [ln.strip() for ln in blk.text.splitlines()]
    assert blk.kind == "OFFER"
    assert lines[0] == "[OFFER] Do it."  # no slot and no player words: the intent (spec 020)
    assert lines[1] == "Chance: even — 50%   (Agility +3, experience +1)"
    assert lines[2] == "If it works: what you wanted.   Very well (5%): more than you asked."
    assert lines[3] == "If it fails: you tire — a setback.   Badly (5%): you tire — serious."
    assert lines[4] == "Close call (15%): get it anyway and pay (you get less far), or fail."
    assert lines[5] == "Fate: 1 (you may spend one to reroll the die once you see it)"
    assert lines[6].startswith("Another way: with ")
    assert "Commit" not in blk.text and "Do it" not in " ".join(lines[1:])  # the menu follows the block
    assert [c["id"] for c in offer_choices(f)] == ["commit", "go_big", "play_safe", "change", "withdraw"]
    assert [c["label"] for c in offer_choices(f)] == ["Do it", "Go big", "Play it safe", "Another way", "Back off"]


def test_offer_words_playtest_20261008(s: Scene) -> None:
    """Fighter 18-21, talker 24: "a help +2, a hindrance −2" named no fact; "Takes:" read as a price and listed
    "fate 1" as if spent; the PC's own name ("Eliius gets up and slashes") read as a typo for the NPC "Eliia"; the
    hidden Recall odds gave no reason."""
    held = s.fact("npc.guard", "detail.posture", "held fast by you")
    wary = s.fact("npc.guard", "detail.manner", "on guard against you")
    name = s.state.entities[s.pc].name.split()[0]
    f = _frame(s, levers=[held], snags=[wary], method_consequences=["the knife is out whatever the roll"],
               beat_kw={"restatement": f"{name} gets up and slashes at the Guard.", "method": "slash at the guard",
                        "how": "slash at the guard"})
    text = offer_block(f, rules=s.rules, fate=1, state=s.state).text
    assert "held fast by you +2" in text and "on guard against you −2" in text and "a help" not in text
    assert "Takes:" not in text and "fate 1" not in text
    assert "Whatever the roll: the knife is out whatever the roll" in text
    assert text.startswith("[OFFER] Slash at the guard.") and name not in text
    secret = offer_block(check(s, LEARN, secret=True), rules=s.rules, fate=1).text  # type: ignore[arg-type]
    assert "Chance: you can't judge how hard this is. (The odds would tell you what your character can't " in secret
    assert "Fate: 1 (no reroll: you won't see this die)" in secret


def test_near_miss_prices_name_their_kind(s: Scene) -> None:
    """Fighter 19: two prices of the same severity both read "a setback"; each names what it costs, as RESULT does."""
    labels = [c["label"] for c in near_miss_choices(_frame(s), s.rules)]
    assert labels == ["Succeed, and pay: you tire (drain, a setback)",
                      "Succeed, and pay: you get less far (shortfall, a setback)",
                      "Let it fail, and still pay: you tire (drain, a setback)"]


def test_an_auto_offer_sits_above_its_result() -> None:
    """Fighter 26-31 (01.7.4): `ordered` moved the auto OFFER below its RESULT, so it read as an open offer waiting
    for "d"; it is no pause, so it stays where the roll is (12.15.2: immediately above its RESULT)."""
    auto, res = OofBlock(kind="OFFER", text="[OFFER — auto] Slash."), OofBlock(kind="RESULT", text="[RESULT] d20 17")
    hit = OofBlock(kind="RESULT", text="[RESULT] Eliia strikes")
    note = OofBlock(kind="NOTE", text="[NOTE] n")
    assert ordered([auto, res, hit, note]) == [note, auto, res, hit]
    assert ordered([OofBlock(kind="OFFER", text="[OFFER] Go."), res])[-1].kind == "OFFER"  # a pause: still last


def test_offer_view_has_exactly_the_engine_api_fields(s: Scene) -> None:
    v = offer_view(_frame(s), s.rules)
    assert set(v.model_dump()) == {"restated_beat", "approach", "difficulty_words", "odds", "stakes", "lethal",
                                   "threatened_cost", "alternate_cost", "only_natural_20"}
    assert v.odds == {"success_or_better_pct": 50, "critical_success_pct": 5, "critical_failure_pct": 5,
                      "near_miss_pct": 15}
    assert v.threatened_cost == {"menu_id": "cost.drain", "form": "you tire", "severity_on_failure": "S2"}
    assert v.alternate_cost == {"menu_id": "cost.shortfall", "form": "you get less far"}


def test_offer_variants_secret_lethal_long_shot_auto(s: Scene) -> None:
    secret = offer_block(check(s, LEARN, secret=True), rules=s.rules)  # type: ignore[arg-type]
    assert "Chance: you can't judge how hard this is." in secret.text and "%" not in secret.text
    assert "Close call" not in secret.text  # I-143: the If lines stay, the odds and the close call do not
    lethal = _frame(s).model_copy(update={"lethal": True, "stakes": "dire"})
    lines = offer_block(lethal, rules=s.rules, lethal_line="THIS CAN KILL YOU — the Guard (warned this scene)").text
    rows = lines.splitlines()
    fails = next(i for i, ln in enumerate(rows) if "If it fails:" in ln)
    assert "If it fails: Danger: " in rows[fails]
    assert "THIS CAN KILL YOU — the Guard" in rows[fails + 1]  # directly under the price (12.15.2)
    auto = offer_block(_frame(s), rules=s.rules, auto=True)
    assert auto.text.startswith("[OFFER — auto]") and "Another way" not in auto.text
    f = _frame(s)
    n20 = f.model_copy(update={"odds": f.odds.model_copy(update={"only_natural_20": True})})
    assert "Chance: only by luck — 5%, and at best what you wanted" in offer_block(n20).text
    long = f.model_copy(update={"long_shot": True, "odds": f.odds.model_copy(
        update={"success_or_better": 10, "critical_failure": 45})})
    assert "Chance: long shot — 10% (failing badly is likelier: 45%)" in offer_block(long).text


def test_near_miss_block(s: Scene) -> None:
    f = _frame(s)
    roll = RollResult(frame_id=None, d20=9, total=13, margin=-2, base_degree="failure", degree="failure",
                      near_miss=True)
    blk = near_miss_block(f, roll, rules=s.rules)
    assert blk.kind == "NEAR_MISS"
    assert blk.text == "[NEAR MISS] 13 vs 15. So close: succeed and pay a price, or let it fail."
    picks = near_miss_choices(f, s.rules)
    assert [c["id"] for c in picks] == ["success_at_cost:cost.drain", "success_at_cost:cost.shortfall", "failure"]
    # P-076: a success and a failure with the same price still read differently; severities in words (12.15.2)
    assert [c["label"] for c in picks] == [
        "Succeed, and pay: you tire (drain, a setback)",
        "Succeed, and pay: you get less far (shortfall, a setback)",
        "Let it fail, and still pay: you tire (drain, a setback)"]


def test_result_block_states_the_outcome_once(s: Scene) -> None:
    from engine.dm.adjudication import CostEntry
    from engine.dm.oof import result_block

    f = _frame(s)
    roll = RollResult(frame_id=None, d20=9, total=13, margin=-2, base_degree="failure", degree="failure",
                      near_miss=True)
    assert result_block(f, roll, rules=s.rules).text == "[RESULT] d20 9 → 13 vs 15 · failure (near miss)"
    paid = result_block(f, roll, sac=True, costs=[CostEntry(menu_id="cost.drain", severity="S2", form="you tire")],
                        rules=s.rules).text.splitlines()
    assert paid[0] == "[RESULT] d20 9 → 13 vs 15 · success at a cost (near miss)"
    assert paid[1].strip() == "It cost you: you tire — a setback."  # spec 016: no "Paid:" bookkeeping
    bare = result_block(f, roll, costs=[CostEntry(menu_id="cost.closed_door", severity="S2", form="")]).text
    assert bare.splitlines()[1].strip() == "It cost you: a door closes to you — a setback."
    secret = check(s, LEARN, secret=True)
    assert result_block(secret, roll).text == "[RESULT] hidden check made."  # type: ignore[arg-type]


def test_a_cost_form_that_cites_ids_is_not_shown(s: Scene) -> None:
    """P-072 / breaker 183202: a Framer form citing "fact.144" or a "Source:" aside is bookkeeping; the OFFER says
    the price in the cost's own plain words instead (no string surgery on model text)."""
    f = check(s, stakes_source="consumed_resource",
              threatened_cost={"menu_id": "cost.drain", "form_intent": "you tire, citing fact.144"},
              alternate_cost={"menu_id": "cost.shortfall", "form_intent": "he stumbles (source: Falett)"})
    assert isinstance(f, Frame)
    text = offer_block(f, rules=s.rules).text
    assert "fact." not in text and "source" not in text.lower()
    assert "If it fails: something is used up — a setback." in text and "(you get less than you wanted)" in text


def test_cost_terms_and_several_questions_are_answered(s: Scene) -> None:
    """Breaker playtest inputs 19, 25-26 (P-028): cost names and severities, and several questions in one message,
    got the generic note."""
    from types import SimpleNamespace as NS

    from engine.dm.turn import OOF_HELP, SEVERITY_ANSWER, oof_answer

    ctx: Any = NS(state=s.state, rules=s.rules)
    a = oof_answer(ctx, 'what does "closed door, S2" and "exposure" mean? And can I spend my Fate point on this?')
    assert a != OOF_HELP and a.startswith("Closed door: a cost that fits ")
    assert "At S2: this approach closed until a new fact changes the situation." in a
    assert "Exposure: a cost that fits " in a and SEVERITY_ANSWER in a and "reroll" in a
    b = oof_answer(ctx, 'what does "near miss" mean here? Also, can I change approach to just asking nicely?')
    assert b.startswith("A near miss is a roll that fails by 3") and "Change approach:" in b


def test_redirect_g3_and_g4(s: Scene) -> None:
    g3 = GateDecision(gate="G3", proposed="G3", redirect=Redirect(
        intent="open the lock", missing="lic.training.lockwork", missing_kind="license",
        options=[RedirectOption(kind="basic_verb", verb="verb.force", method="break it"),
                 RedirectOption(kind="intent", method="find another way in")],
        acquisition_paths=[{"type": "mentor", "detail": "a locksmith could teach you"}]))
    lines = redirect_block(g3, rules=s.rules).text.splitlines()
    assert lines[0].startswith("[REDIRECT] Not as tried: that needs ") and "which you have not learned." in lines[0]
    assert [ln.strip() for ln in lines[1:4]] == ["You could instead:", "- Break it", "- Find another way in"]
    assert lines[4].strip() == "To learn it: train with someone who knows it."
    assert not any(x in "\n".join(lines) for x in ("G3", "lic.", "verb."))
    fid = s.fact("npc.guard", "siblings", "two brothers")
    g4 = GateDecision(gate="G4", proposed="G4", fact_cited=fid, redirect=Redirect(
        intent="greet his sister", missing=fid, missing_kind="fact",
        options=[RedirectOption(kind="intent", method="tell him the truth")]))
    text = redirect_block(g4, state=s.state).text
    assert text.startswith("[REDIRECT] Not as tried: Guard's siblings is two brothers, as already settled.")
    assert "- Tell him the truth" in text


def test_clarify_note_passthroughs_and_order() -> None:
    assert clarify_block("do you mean to climb the rope, or cut it?").text == \
        "[CLARIFY] One question: do you mean to climb the rope, or cut it?"
    assert clarify_block("You mean the merchant.", assuming=True).text.startswith("[ASSUMING] You mean the merchant.")
    assert note_block("01.4.2 — one beat settles one obstacle.", "RULES").text == \
        "[RULES] 01.4.2 — one beat settles one obstacle."
    assert note_block("hi", rest=["there"]).text == "[NOTE] hi\n       there"
    assert create_block("Pick an origin.", 2, 9).text == "[CREATE 2/9] Pick an origin."
    assert seed_block("[SEED 1/14] Mode: guided").text == "[SEED 1/14] Mode: guided"
    blocks = [OofBlock(kind="OFFER", text="o"), OofBlock(kind="WARNING", text="w"), OofBlock(kind="NOTE", text="n"), OofBlock(kind="REDIRECT", text="r")]
    assert [b.kind for b in ordered(blocks)] == ["NOTE", "REDIRECT", "WARNING", "OFFER"]
    assert OofBlock(kind="NOTE", text="x").model_dump() == {"kind": "NOTE", "text": "x"}


def test_warning_status_last_chance(s: Scene) -> None:
    w = warning_block(s.rules, LethalTrigger(pc=s.pc, source="npc.guard", cause="disposition"),
                      source_name="the Guard", fate=2)
    assert w.kind == "WARNING" and w.text.startswith("[WARNING] THIS CAN KILL YOU — the Guard. It means to kill.")
    assert "Fate: 2." in w.text and "Yield — ask what it would mean" in w.text
    assert status_block(s.rules, s.state, s.pc) is None  # fresh: no card
    s.apply([Event.of("quantity_changed", source="test", entity=s.pc, quantity="vitality", delta=-13, new_value=0,
                      reason="test")])
    st = status_block(s.rules, s.state, s.pc)
    assert st is not None and st.kind == "STATUS" and st.text.startswith("[STATUS] STAGGERED")
    menu = Menu(pc=s.pc, situation=Situation(), fate_cost=1, options=[
        MenuOption(id="lc.maimed", name="Maimed", order=2, available=True, price="lose 1 Might for life"),
        MenuOption(id="lc.last_stand", name="Last Stand", order=7, available=True, price="one last turn, then death"),
        MenuOption(id="lc.captured", name="Captured", order=1, available=False, struck_by="fact.9")])
    lc = last_chance_block(menu)
    assert lc.kind == "LAST_CHANCE" and "(2) Maimed — lose 1 Might for life" in lc.text
    assert "There is no default" in lc.text and "Captured — fact.9" in lc.text


def test_recap_from_state_only(s: Scene) -> None:
    with s.store.transaction() as tx:
        for name, vis in (("The missing ferryman", "shown"), ("The secret cult", "sealed")):
            eid = ids.entity_id("thread", name, tx.state.entities)
            tx.add(Event.of("entity_created", source="test", entity=EntityRecord(
                id=eid, kind="thread", name=name, visibility=vis, data={"status": "active"})))  # type: ignore[arg-type]
        tx.add(Event.of("fact_set", {"source": "narration"}, fact_id=tx.mint(ids.FACT), subject="world",
                        predicate="chronicle.chr.1", visibility="available",
                        value={"id": "chr.1", "time": "Y1", "text": "Wren reached Ashford.", "kind": "deed",
                               "source": "12.4.8"}))
    text = recap_block(s.state).text
    assert text.startswith("[RECAP] Where:")
    assert "The missing ferryman" in text and "The secret cult" not in text
    assert "• Wren reached Ashford." in text


# ------------------------------------------------------------------ OOF answers about the OFFER's words


def test_questions_about_offer_words_get_their_meaning(s: Scene) -> None:
    from types import SimpleNamespace as NS

    from engine.dm.turn import oof_answer

    ctx: Any = NS(state=s.state, rules=None)
    assert oof_answer(ctx, 'what does "Go big" mean here?').startswith("Go big: raise the stakes one step")
    assert oof_answer(ctx, 'what does "near miss" mean?').startswith("A near miss is a roll that fails by 3")
    assert "reroll" in oof_answer(ctx, "Can I spend my Luck on this first?")  # P-047 (01.16.3)
