"""Spec 015: the typed intended change (01.2.7, DL-01-34), the lift attribute rubric (DL-01-35) and the knockout
status line (problem 13)."""

from __future__ import annotations

import gzip
import json
import shutil
from pathlib import Path
from typing import Any

from engine.dm.context import TurnContext
from engine.dm.handles import items
from engine.dm.turn import answer_pause, run_turn
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.resolve.change import apply_change, holder_of
from engine.resolve.frame import lift_attribute, lift_or_carry
from engine.resolve.types import Beat, Change
from engine.store.db import Store
from engine.store.events import EntityRecord, Event
from tests.engine.test_turn_adjudication import D20, QUIET_WORLD, beat, framer, reader, setup

FIXTURE = Path(__file__).parents[1] / "fixtures" / "fighter_purse_turn8.db.gz"


def _thing(tx: Any, eid: str, name: str, holder: str | None = None, kind: str = "item") -> None:
    tx.add(Event.of("entity_created", source="test", entity=EntityRecord(id=eid, kind=kind, name=name)))  # type: ignore[arg-type]
    if holder:
        tx.add(Event.of("fact_set", {"source": "narration"}, source="test", rule_id="00.6.6", fact_id=tx.mint("fact"),
                        subject=eid, predicate="carried_on", value=holder, visibility="shown"))


def _beat(dock: Any, kind: str, what: str | None = None, whom: str | None = None, intent: str = "x") -> Beat:
    return Beat(id="beat.t", actor=dock.pc, intent=intent, method=intent, change=Change(kind=kind, what=what,
                                                                                      whom=whom))


def test_each_kind_applies_on_success_scaled_by_reach(tmp_path: Path) -> None:
    dock, _ = setup(tmp_path, None)
    rules = dock.rules
    with dock.store.transaction("turn.t") as tx:
        _thing(tx, "item.lantern", "lantern", dock.ferryman)
        _thing(tx, "obj.gate", "gate", kind="object")
        st = tx.state
        assert apply_change(tx, rules, _beat(dock, "take", "item.lantern", dock.ferryman), 0).words == ""  # failure
        part = apply_change(tx, rules, _beat(dock, "take", "item.lantern", dock.ferryman), 1, pc=dock.pc)
        assert "a hand on the lantern, still contested" in part.words
        assert holder_of(st, "item.lantern") == dock.ferryman and st.fact_value("item.lantern", "contested_by") == dock.pc
        wrong = apply_change(tx, rules, _beat(dock, "take", "item.lantern", dock.watch), 2, pc=dock.pc)
        assert wrong.refused.startswith("the lantern is not with") and not wrong.events
        whole = apply_change(tx, rules, _beat(dock, "take", "item.lantern", dock.ferryman), 2, pc=dock.pc)
        assert holder_of(st, "item.lantern") == dock.pc and "you hold the lantern, taken from" in whole.words
        assert st.fact_value("item.lantern", "contested_by") is None
        mine = apply_change(tx, rules, _beat(dock, "take", "item.lantern"), 2, pc=dock.pc)  # already yours (DL-01-36)
        assert mine.words == "you already have the lantern" and not mine.refused and not mine.events
        apply_change(tx, rules, _beat(dock, "give", "item.lantern", dock.watch), 2, pc=dock.pc)
        assert holder_of(st, "item.lantern") == dock.watch
        assert apply_change(tx, rules, _beat(dock, "give", "item.lantern", dock.ferryman), 2, pc=dock.pc).refused
        apply_change(tx, rules, _beat(dock, "open", "obj.gate"), 2, pc=dock.pc)
        assert st.fact_value("obj.gate", "open") is True
        apply_change(tx, rules, _beat(dock, "close", "obj.gate"), 1, pc=dock.pc)  # no partial form: whole at 1
        assert st.fact_value("obj.gate", "open") is False
        apply_change(tx, rules, _beat(dock, "persuade_to", dock.ferryman, intent="take me across"), 1, pc=dock.pc)
        assert st.fact_value(dock.ferryman, "agreed").startswith("a smaller part")
        apply_change(tx, rules, _beat(dock, "persuade_to", dock.ferryman, intent="take me across"), 2, pc=dock.pc)
        assert st.fact_value(dock.ferryman, "agreed") == "take me across"
        apply_change(tx, rules, _beat(dock, "hide", None, dock.watch), 2, pc=dock.pc)
        assert st.fact_value(dock.pc, "hidden_from") == dock.watch
        grips = [apply_change(tx, rules, _beat(dock, "restrain", dock.ferryman), r, pc=dock.pc).words for r in (1, 3, 4)]
        assert [g.split(" by ")[0].split()[-1] for g in grips] == ["fast", "restrained", "pinned"]
        assert "not built" in apply_change(tx, rules, _beat(dock, "make", None), 2, pc=dock.pc).refused
        assert apply_change(tx, rules, _beat(dock, "harm", dock.ferryman), 2, pc=dock.pc).words == ""  # own writer


def _turn(tmp_path: Path, *beats: dict[str, Any], faces: list[int]) -> tuple[Any, TurnContext, list[Any]]:
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I lift the lantern off the ferryman's hook.", *beats)],
                           Role.FRAMER: [framer() for _ in beats], Role.WORLD: [QUIET_WORLD] * 3})
    dock, ctx = setup(tmp_path, model)
    with dock.store.transaction("turn.0") as tx:
        _thing(tx, "item.lantern", "lantern", dock.ferryman)
    assert isinstance(ctx.rng, D20)
    ctx.rng.faces = list(faces)
    out = [run_turn(ctx, "I lift the lantern off the ferryman's hook.")]
    while out[-1].pause is not None and out[-1].pause.kind == "offer":
        choice = "commit" if any(c["id"] == "commit" for c in out[-1].pause.choices) else "continue"
        out.append(answer_pause(ctx, choice))
    return dock, ctx, out


LIFT = beat("the lantern is in my hand", "verb.handle", target="npc.tam_harlan",
            change={"kind": "take", "what": "item.lantern", "whom": "npc.tam_harlan"})


def test_success_applies_the_change_offer_and_result_say_it_and_it_is_must_name(tmp_path: Path) -> None:
    dock, ctx, out = _turn(tmp_path, LIFT, faces=[19])
    offer = next(o["text"] for o in out[0].oof if o["kind"] == "OFFER")
    assert "Taking: the lantern" in offer
    assert "Agility" in offer.split("Chance:")[1].split("\n")[0]  # DL-01-35: the best of might/agility/endurance
    assert "with Might" in offer and "with Endurance" in offer  # the others listed with their odds
    st = dock.store.state
    assert holder_of(st, "item.lantern") == dock.pc
    b = out[-1].record.beats[-1]
    assert b.change_kind == "take" and b.changed.startswith("you hold the lantern")
    result = next(o["text"] for o in out[-1].oof if o["kind"] == "RESULT")
    assert "Now: You hold the lantern" in result
    assert any(i.kind == "change" and i.must_name for i in items(out[-1].record))
    from engine.dm.codex import codex

    assert "lantern" in codex(st, "sheet", ctx.rules).text  # the sheet lists it


def test_failure_applies_nothing(tmp_path: Path) -> None:
    dock, _, out = _turn(tmp_path, LIFT, faces=[1])
    b = out[-1].record.beats[-1]
    assert b.degree in ("failure", "critical_failure") and not b.changed
    assert holder_of(dock.store.state, "item.lantern") == dock.ferryman


def test_two_changes_are_two_beats_and_the_offer_names_the_second(tmp_path: Path) -> None:
    punch = beat("the ferryman is struck", "verb.strike", target="npc.tam_harlan", against_will=True,
                 change={"kind": "harm", "what": "npc.tam_harlan"})
    dock, _, out = _turn(tmp_path, LIFT, punch, faces=[19, 19, 19])
    first = next(o["text"] for o in out[0].oof if o["kind"] == "OFFER")
    assert "Then: the ferryman is struck" in first  # the act (the test beat's method is its intent)
    kinds = [b.change_kind for o in out for b in o.record.beats if b.degree]
    assert kinds == ["take", "harm"]
    assert holder_of(dock.store.state, "item.lantern") == dock.pc


def test_the_purse_from_the_fighter_save_is_taken(tmp_path: Path) -> None:
    """Playtest 20261008-145430, input 23 (turn 8): "I try to lift the purse from her belt while she's pinned, quick
    and quiet." The save's state before that turn, the Reader's own answer plus the typed change."""
    path = tmp_path / "fighter.db"
    with gzip.open(FIXTURE, "rb") as src, path.open("wb") as dst:
        shutil.copyfileobj(src, dst)
    store = Store.open(path)
    lift = {"against_will": True, "assertion": None, "g4_fact": None, "intent_verbs": ["lift", "take"],
            "intent": "The coin purse is in the PC's hands and off Murzak's belt.", "pressure": "none",
            "method": "lift the purse from her belt while she is pinned, quick and quiet", "purpose": "own_change",
            "shape": "now", "speech": False, "target": "npc.murzak_red_hand", "uses_power": False,
            "verb": "verb.grapple",
            "change": {"kind": "take", "what": "item.coin_purse", "whom": "npc.murzak_red_hand", "description": None}}
    text = "I try to lift the purse from her belt while she's pinned, quick and quiet."
    model = ScriptedModel({Role.READER: [reader("DECLARATION", text, lift)], Role.FRAMER: [framer()]})
    from engine.rng import Rng

    class Faces(D20):
        pass

    rng = Faces.of(store)
    rng.faces = [18]
    assert isinstance(rng, Rng)
    ctx = TurnContext(store=store, rules=__import__("engine.data.loader", fromlist=["load_rules"]).load_rules(),
                      rng=rng, model=model, config={"auto_commit": False})
    res = run_turn(ctx, text)
    while res.pause is not None and res.pause.kind == "offer":
        res = answer_pause(ctx, "commit" if any(c["id"] == "commit" for c in res.pause.choices) else "continue")
    st = store.state
    pc = next(e for e in st.entities if e.startswith("pc."))
    assert holder_of(st, "item.coin_purse") == pc
    b = next(b for b in res.record.beats if b.change_kind == "take")
    assert b.changed.startswith("you hold the coin purse")
    from engine.dm.codex import codex

    assert "coin purse" in codex(st, "sheet", ctx.rules).text
    log = path.with_name("fighter.changes.jsonl")  # the Laya log (01.2.7 design note)
    row = json.loads(log.read_text(encoding="utf-8").splitlines()[-1])
    assert row["kind"] == "take" and row["slots"]["what"] == "item.coin_purse" and "item.coin_purse" in row["ids_in_scope"]
    assert {"restatement", "verb", "ids_in_scope"} <= set(row)
    assert len(ctx.rules.resolution["intended_change"]["kinds"]) <= 20


def test_a_grapple_that_takes_holds_no_one(tmp_path: Path) -> None:
    """The playtest's "lift his purse" Grapple wrote "restrained" (T-12-18's hold is `restrain`'s face, 01.2.7 item 4)."""
    from types import SimpleNamespace

    from engine.dm.adjudication import AdjudicationRecord, BeatEntry
    from engine.dm.scene_state import beat_writes
    from engine.store.details import current

    dock, ctx = setup(tmp_path, None)
    with dock.store.transaction("turn.t") as tx:
        ctx.tx = tx
        rec = AdjudicationRecord(pc=dock.pc)
        entry = BeatEntry(frame_id="frame.9", actor=dock.pc, targets=[dock.ferryman], verb="verb.grapple",
                          restatement="lift his purse", degree="success", reach="great", change_kind="take")
        beat_writes(ctx, rec, [SimpleNamespace(status="resolved", entry=entry)])
        assert current(tx.state, dock.ferryman, "posture") is None and current(tx.state, dock.pc, "held") is None
        assert current(tx.state, dock.ferryman, "manner").value == "on guard against you"  # type: ignore[union-attr]
        held = entry.model_copy(update={"verb": "verb.force", "change_kind": "restrain"})  # restrain on any verb
        from engine.store.conditions import apply_condition

        tx.add_all(apply_condition(tx.state, tx.mint, ctx.rules, dock.ferryman, "cond.restrained",
                                   source={"entity": dock.pc}).events)  # RECORD's hold (06.5.2)
        beat_writes(ctx, rec, [SimpleNamespace(status="resolved", entry=held)])
        assert current(tx.state, dock.ferryman, "posture").value == "restrained by you"  # type: ignore[union-attr]
        freed = entry.model_copy(update={"change_kind": "free"})
        beat_writes(ctx, rec, [SimpleNamespace(status="resolved", entry=freed)])
        assert current(tx.state, dock.ferryman, "posture") is None
        assert not tx.state.conditions_on(dock.ferryman)  # the condition goes with its face
        ctx.tx = None


def test_lift_attribute_words_pick_else_best_odds(tmp_path: Path) -> None:
    dock, _ = setup(tmp_path, None)
    st, rules = dock.store.state, dock.rules
    actor = st.entities[dock.pc]  # Wren: Agility 3, Might 1, Endurance 1
    take = _beat(dock, "take", "item.x", intent="get the purse")
    spec = lift_or_carry(rules, take)
    assert spec is not None
    assert lift_attribute(spec, rules, st, take, actor, "might", 0) == "agility"
    heave = take.model_copy(update={"method": "heave the chest onto the cart"})
    assert lift_attribute(spec, rules, st, heave, actor, "agility", 0) == "might"
    quiet = take.model_copy(update={"method": "lift it quickly and quietly"})
    assert lift_attribute(spec, rules, st, quiet, actor, "might", 0) == "agility"
    strike = Beat(id="beat.s", actor=dock.pc, intent="hit him", method="lift my sword and strike", verb="verb.strike")
    assert lift_or_carry(rules, strike) is None  # a lift word on another verb is not a lift


def test_staggered_status_line_says_one_blow_can_end_it(tmp_path: Path) -> None:
    from engine.harm.apply import apply_harm, status_block
    from engine.harm.state import View
    from tests.engine.test_harm_support import RULES, make_game, run

    store = make_game(tmp_path, vitality=1)
    run(store, apply_harm, "pc.wren", dealt=5, source="x")
    block = status_block(RULES, View(store.state), "pc.wren") or ""
    assert "Load 0/3; a blow adds 1 to 4 by how hard it lands" in block
    res = run(store, apply_harm, "pc.wren", dealt=8, source="x")  # one heavy blow (S4: 3 load) at 0/3
    assert res.transition == "down" and res.load == 3 and (res.wound or {}).get("load") == 3
