"""Spec 022 F5, from the round-6 saves (I3 §1-§3): the hold is a condition and the held foe tries to break free
instead of striking; a refused turn gives no free strike; a payment deducts coin; a take-back prints `Now:`."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord
from engine.dm.context import TurnContext
from engine.resolve.change import HOLDS, apply_change, current_hold, deal_price, pay_deal
from engine.resolve.types import Beat
from evals.feedback_corpus import CORPUS, open_at

RULES = load_rules()
# I3 §1: the foe hits that landed while the PC held the foe (and 233000 turn 4, the turn the grip was set)
HELD_HITS = [("20261008-135049-fighter.db.gz", 7), ("20261008-135049-fighter.db.gz", 10),
             ("20261008-145430-fighter.db.gz", 9), ("20261008-145430-fighter.db.gz", 11),
             ("20261008-145430-fighter.db.gz", 15), ("20261008-233000-fighter.db.gz", 4),
             ("20261008-233000-fighter.db.gz", 6), ("20261008-233000-fighter.db.gz", 10),
             ("20261008-233000-fighter.db.gz", 14)]


def _n(turn_id: str | None) -> int:
    return int(str(turn_id).rsplit(".", 1)[1]) if turn_id and str(turn_id).startswith("turn.") else 0


def _grips(store: Any, upto: int) -> list[tuple[dict[str, Any], int]]:
    """The save's Grapple or `restrain` beats that succeeded by turn `upto`, with their delivered reach."""
    resolved = {e.payload.frame_id: e for e in store.events(types=["frame_resolved"])}  # type: ignore[attr-defined]
    out = []
    for e in store.events(types=["frame_committed"]):
        b = e.payload.frame["beat"]  # type: ignore[attr-defined]
        r = resolved.get(e.payload.frame_id)  # type: ignore[attr-defined]
        kind = (b.get("change") or {}).get("kind")
        if r is None or _n(r.turn_id) > upto or not (r.payload.degree in ("success", "critical_success")
                                                      or r.payload.success_at_cost_taken):
            continue
        if str(b.get("target") or "").startswith("npc.") and (
                kind == "restrain" or (b.get("verb") == "verb.grapple" and kind in (None, "none"))):
            out.append((b, {"standard": 2, "partial": 1, "great": 3, "extraordinary": 4}.get(
                str(r.payload.delivered.get("reach")), 2)))
    return out


@pytest.mark.parametrize(("save", "turn"), HELD_HITS, ids=lambda x: str(x).split("-")[-1].split(".")[0])
def test_a_held_foe_tries_to_break_free_and_never_strikes(save: str, turn: int, tmp_path: Path) -> None:
    """Re-run the hit turn's foe beat on the save as it stood, with the hold RECORD now applies (06.5.2, DL-06-31):
    `beh.default_melee` row 2 comes first, so the foe strains against the hold (or breaks it) and lands no blow."""
    from engine.resolve.conflict import foe_beat
    from engine.store.db import Store

    full = Store.open(open_at(CORPUS / save, f"turn.{turn + 1}", tmp_path).path)
    grips = _grips(full, turn)
    full.close()
    assert grips, "the save holds a successful grip by this turn"
    (tmp_path / "cut").mkdir()
    store = open_at(CORPUS / save, f"turn.{turn}", tmp_path / "cut")
    ctx = TurnContext.for_store(store, model=None, rules=RULES)  # type: ignore[arg-type]
    try:
        with store.transaction(f"turn.{turn}") as tx:
            ctx.tx = tx
            beat, reach = grips[-1]
            res = apply_change(tx, RULES, Beat.model_validate(beat), reach, pc=beat["actor"])
            held = str(beat.get("target") or (beat.get("change") or {}).get("what"))
            assert current_hold(tx.state, held, beat["actor"]) >= 1, res
            pc = beat["actor"]
            before = tx.state.quantities[pc]["vitality"].current
            said, harm = foe_beat(ctx.time_ctx(), ctx.rng, held, pc)
            assert "hold" in said and "strikes" not in said and harm is None, said
            assert tx.state.quantities[pc]["vitality"].current == before
            ctx.tx = None
            raise _Rollback
    except _Rollback:
        pass
    finally:
        store.close()


class _Rollback(Exception):
    """Nothing the test does is kept."""


def test_breaking_free_ends_the_condition_and_its_face(tmp_path: Path) -> None:
    """A successful break-free ends the hold: the conditions and the posture/held slots go together (06.5.2)."""
    from engine.resolve.conflict import _break_free, holds
    from engine.store.details import current

    store = open_at(CORPUS / "20261008-233000-fighter.db.gz", "turn.5", tmp_path)
    ctx = TurnContext.for_store(store, model=None, rules=RULES)  # type: ignore[arg-type]
    try:
        with store.transaction("turn.5") as tx:
            ctx.tx = tx
            pc, foe = "pc.evine_oakwell", "npc.dunwen_redmore"
            from engine.resolve.change import hold

            tx.add_all(hold(tx, RULES, foe, pc, 2))
            assert (pc, foe) in holds(tx.state) and current(tx.state, foe, "posture") is not None
            rng = SimpleNamespace(d=lambda sides, why: 20)  # a natural 20: a critical break
            said = _break_free(ctx.time_ctx(), rng, foe, pc)
            assert "free" in said and (pc, foe) not in holds(tx.state)
            assert not [c for c in tx.state.conditions_on(foe) if c.condition_id in HOLDS]
            assert current(tx.state, foe, "posture") is None and current(tx.state, pc, "held") is None
            assert any(c.condition_id == "cond.off_balance" for c in tx.state.conditions_on(pc))
            ctx.tx = None
            raise _Rollback
    except _Rollback:
        pass
    finally:
        store.close()


def test_a_refused_turn_gives_the_foe_no_free_strike(tmp_path: Path) -> None:
    """I3 §3 (233000 turn 14): every beat refused (G4) spends nothing: no foe beat and no round (01.3.6-01.3.7)."""
    from engine.dm.adjudication import BeatEntry
    from engine.dm.world_step import world_step
    from engine.resolve.pipeline import BeatOutcome

    store = open_at(CORPUS / "20261008-233000-fighter.db.gz", "turn.14", tmp_path)
    ctx = TurnContext.for_store(store, model=None, rules=RULES)  # type: ignore[arg-type]
    try:
        with store.transaction("turn.14") as tx:
            ctx.tx = tx
            pc = "pc.evine_oakwell"
            vit, rnd = tx.state.quantities[pc]["vitality"].current, tx.state.time.now.round
            rec = AdjudicationRecord(pc=pc)
            refused = BeatOutcome(status="refused", entry=BeatEntry(beat_id="beat.9", actor=pc, gate="G4",
                                                                    restatement="threaten Dunwen"))
            world_step(ctx, rec, beats=[refused], oof=[])
            assert not rec.npc_actions and tx.state.quantities[pc]["vitality"].current == vit
            assert tx.state.time.now.round == rnd
            ctx.tx = None
            raise _Rollback
    except _Rollback:
        pass
    finally:
        store.close()


def test_a_deal_pays_its_typed_price_never_prose(tmp_path: Path) -> None:
    """Spec 025 (15.7.1 item 3, DL-15-42): Framer prose moves no coin (the regex price is retired); a deal's typed
    price, from the band of the request, is a quantity change with a price record."""
    rules = load_rules()
    assert deal_price(rules, None, None) == 1 and deal_price(rules, "R2", 10) == 5 and deal_price(rules, "R2", 3) == 3
    store = open_at(CORPUS / "20261008-192926-talker.db.gz", "turn.7", tmp_path)
    try:
        with store.transaction("turn.7") as tx:
            pc = "pc.wila_bramblefoot"
            coin = tx.state.quantities[pc]["coin"].current
            npc = next(i for i, e in tx.state.entities.items() if e.kind == "npc")
            evs = pay_deal(tx, pc, npc, 1)
            assert tx.state.quantities[pc]["coin"].current == coin - 1 and evs[0].payload.value["amount"] == 1  # type: ignore[attr-defined]
            raise _Rollback
    except _Rollback:
        pass
    finally:
        store.close()


def test_a_folded_grip_is_applied_when_its_goal_succeeds(tmp_path: Path) -> None:
    """Spec 020's goal-first Reader folds "grab her and demand the word" into one Talk beat; its grip is still real:
    the goal's success applies the hold (06.5.2), its failure applies none."""
    from engine.dm.roles.reader import _fold_methods
    from engine.resolve.pipeline import _folded_hold

    beats = _fold_methods([
        {"verb": "verb.grapple", "target": "npc.dunwen_redmore", "against_will": True, "method": "grab her arm",
         "change": {"kind": "restrain", "what": "npc.dunwen_redmore", "whom": "none"}, "shape": "now"},
        {"verb": "verb.talk", "target": "npc.dunwen_redmore", "method": "demand the word", "shape": "now",
         "change": {"kind": "learn", "what": "none", "whom": "none"}}])
    assert len(beats) == 1 and beats[0]["holds"] == "npc.dunwen_redmore"
    store = open_at(CORPUS / "20261008-233000-fighter.db.gz", "turn.3", tmp_path)
    try:
        with store.transaction("turn.3") as tx:
            beat = Beat(id="beat.99", actor="pc.evine_oakwell", intent="learn the word", method="grab, demand",
                        holds="npc.dunwen_redmore")
            env = SimpleNamespace(tx=tx, rules=RULES, state=tx.state, add=tx.add)
            _folded_hold(env, beat, 0)  # type: ignore[arg-type]
            assert current_hold(tx.state, "npc.dunwen_redmore") == 0
            _folded_hold(env, beat, 2)  # type: ignore[arg-type]
            assert current_hold(tx.state, "npc.dunwen_redmore", "pc.evine_oakwell") == 2
            raise _Rollback
    except _Rollback:
        pass
    finally:
        store.close()
