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
from engine.resolve.frame import offer_preview
from engine.resolve.gate import GateDecision, Redirect, RedirectOption
from engine.resolve.types import Frame, RollResult
from engine.store.events import EntityRecord, Event
from tests.engine.test_resolve_frame import check
from tests.engine.test_resolve_scene import Scene


@pytest.fixture
def s(tmp_path: Path) -> Scene:
    sc = Scene.new(tmp_path)
    sc.add("npc", "Guard", attributes={"wits": 1, "agility": 1, "might": 2})
    return sc


def _frame(s: Scene, **kw: Any) -> Frame:
    f = check(s, stakes_source="aware_opponent_or_observer",
              threatened_cost={"menu_id": "cost.drain", "form_intent": "you tire"},
              alternate_cost={"menu_id": "cost.footing", "form_intent": "you slip"}, **kw)
    assert isinstance(f, Frame)
    return f


def test_offer_block_matches_the_cli_layout(s: Scene) -> None:
    f = _frame(s)
    blk = offer_block(f, rules=s.rules, fate=1)
    lines = blk.text.splitlines()
    assert blk.kind == "OFFER"
    assert lines[0] == "[OFFER] do it — Move (Agility), a moderate obstacle."
    assert lines[1].strip() == "Success or better 50% · critical failure 5% · near miss 15% (need 11+ on the die)."
    assert lines[2].strip().startswith("Stakes: risky. If it goes wrong: you tire (drain, S2")
    assert "Or instead: you slip (footing)." in lines[2]
    assert "Reach: standard." in blk.text and "Fate: 1." in blk.text
    assert "1) Commit" not in blk.text  # the front end lists the pause's choices once, after the block
    assert [c["id"] for c in offer_choices(f)] == ["commit", "change", "withdraw", "go_big", "play_safe"]


def test_offer_view_has_exactly_the_engine_api_fields(s: Scene) -> None:
    v = offer_view(_frame(s), s.rules)
    assert set(v.model_dump()) == {"restated_beat", "approach", "difficulty_words", "odds", "stakes", "lethal",
                                   "threatened_cost", "alternate_cost", "only_natural_20"}
    assert v.odds == {"success_or_better_pct": 50, "critical_success_pct": 5, "critical_failure_pct": 5,
                      "near_miss_pct": 15}
    assert v.threatened_cost == {"menu_id": "cost.drain", "form": "you tire", "severity_on_failure": "S2"}
    assert v.alternate_cost == {"menu_id": "cost.footing", "form": "you slip"}


def test_offer_variants_secret_lethal_auto(s: Scene) -> None:
    secret = offer_block(check(s, secret=True), rules=s.rules)  # type: ignore[arg-type]
    assert "difficulty hidden" in secret.text and "The roll is hidden" in secret.text and "%" not in secret.text
    lethal = offer_preview(_frame(s)).model_copy(update={"lethal": True})
    text = offer_block(lethal, rules=s.rules, lethal_line="THIS CAN KILL YOU — the Guard (warned this scene)").text
    stakes_at = text.splitlines().index(next(ln for ln in text.splitlines() if "Stakes:" in ln))
    assert "THIS CAN KILL YOU — the Guard" in text.splitlines()[stakes_at + 1]  # directly under Stakes (12.15.2)
    auto = offer_block(_frame(s), rules=s.rules, auto=True)
    assert auto.text.startswith("[OFFER — auto]") and "1) Commit" not in auto.text
    n20 = offer_preview(_frame(s)).model_copy(update={"only_natural_20": True})
    assert "Only a natural 20, and at best a plain success." in offer_block(n20).text


def test_near_miss_block(s: Scene) -> None:
    f = _frame(s)
    roll = RollResult(frame_id=None, d20=9, total=13, margin=-2, base_degree="failure", degree="failure",
                      near_miss=True)
    blk = near_miss_block(f, roll, rules=s.rules)
    assert blk.kind == "NEAR_MISS"
    assert blk.text == "[NEAR MISS] 13 vs 15. So close: succeed and pay a price, or let it fail."
    picks = near_miss_choices(f, s.rules)
    assert [c["id"] for c in picks] == ["success_at_cost:cost.drain", "success_at_cost:cost.footing", "failure"]
    assert [c["label"] for c in picks] == ["Succeed, and pay: you tire (drain, S2)",
                                           "Succeed, and pay: you slip (footing, S2)",
                                           "Let it fail: you tire (drain, S2)"]


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
