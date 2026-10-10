"""Spec 023's real-save gates, on the round-7 saves (`tests/fixtures/round7/`, copied read-only from
`saves/playtest-20261009-1606*`): each re-runs the failing turn's step on the save as it stood, with the recorded
Reader beat and Framer proposal, under the new code (I3 §1-2, §4-7; H2 T6)."""

from __future__ import annotations

import gzip
import json
import shutil
import sqlite3
from pathlib import Path
from typing import Any

from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord
from engine.dm.context import TurnContext
from engine.dm.oof import fact_short, near_miss_choices
from engine.dm.packet import people_card
from engine.dm.roles.framer import beat_message
from engine.dm.roles.reader import FactQuestion, ReaderResult, normalise
from engine.dm.turn import _fiction_questions, not_oracle
from engine.resolve.change import typed_goal
from engine.resolve.frame import frame_check
from engine.resolve.gate import GateDecision, check_gate
from engine.resolve.oracle import positive
from engine.resolve.pipeline import BeatPlan, PipelineEnv, resume, run_beats
from engine.resolve.types import Beat, CostDecl, Frame, Obstacle, ProposedFrame
from evals.feedback_corpus import open_at
from tests.engine.test_turn_adjudication import D20

RULES = load_rules()
R7 = Path(__file__).parents[1] / "fixtures" / "round7"
FIGHTER, EXPLORER, TALKER = (R7 / f"20261009-{n}.db.gz" for n in ("160622-fighter", "160642-explorer",
                                                                     "160602-talker"))


def raw(save: Path, tmp: Path) -> sqlite3.Connection:
    """The whole save, read-only (the record the cut copies are made from)."""
    path = tmp / f"raw-{save.stem}"
    with gzip.open(save, "rb") as src, path.open("wb") as dst:
        shutil.copyfileobj(src, dst)
    return sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)


def pause_detail(save: Path, tmp: Path, seq: int) -> dict[str, Any]:
    con = raw(save, tmp)
    (payload,) = con.execute("SELECT payload FROM events WHERE seq = ?", (seq,)).fetchone()
    con.close()
    return dict(json.loads(payload)["pause"]["detail"])


def stub(proposed: ProposedFrame, seen: list[tuple[Beat, GateDecision]] | None = None) -> Any:
    def propose(beat: Beat, candidates: list[str], *, gate: GateDecision, note: str | None = None) -> ProposedFrame:
        if seen is not None:
            seen.append((beat, gate))
        return proposed

    return propose


def env(store: Any, tx: Any, framer: Any) -> PipelineEnv:
    pc = next(e for e, x in store.state.entities.items() if x.kind == "pc")
    return PipelineEnv(tx=tx, rules=RULES, rng=D20.of(store), store=store, framer=framer, pc=pc)


def test_belies_reading_is_her_record_never_a_coin_flip(tmp_path: Path) -> None:
    """Fighter turn.11 (input 26): the Reader asked the Oracle whether Belie, a scribe holding Letters, "can read the
    writing on the delivery list"; a d100 of 08 wrote no (fact.113) and the OFFER asked to persuade her with
    "can not read … −2". Now no draw is made, nothing is written, and the Framer sees her Letters."""
    store = open_at(FIGHTER, "turn.11", tmp_path)
    belie = "npc.belie_greenwort"
    ctx = TurnContext.for_store(store, model=None, rules=RULES)  # type: ignore[arg-type]
    try:
        with store.transaction("turn.11") as tx:
            ctx.tx = tx
            rec = AdjudicationRecord(turn_id="turn.11")
            _fiction_questions(ctx, rec, [FactQuestion(subject=belie, odds_rung="likely",
                                                       predicate="can read the writing on the delivery list")],
                               targets=[belie])
            assert not any(e.type in ("oracle_answered", "fact_set") for e in tx.events), tx.events
            assert not rec.oracle and any("not asked of the Oracle" in n for n in rec.notes)
            assert "Letters (reads and writes)" in "\n".join(people_card(tx.state, belie))  # spec 026: the card
            ctx.tx = None
            raise _Rollback
    except _Rollback:
        pass
    finally:
        store.close()


class _Rollback(Exception):
    """Nothing a test does is kept."""


def test_the_not_not_alert_label_reads_once(tmp_path: Path) -> None:
    """Fighter turn.5 (input 20): fact.106 `is_not_alert_…_while_h` = False showed "is not not alert … while h −2".
    The old record now reads once, with who it is about; a new question is asked positive and whole."""
    store = open_at(FIGHTER, "turn.6", tmp_path)
    label = fact_short(store.state, "fact.106")
    store.close()
    assert "not not" not in label and label.startswith("Magby is alert to a hand"), label
    asked, flipped = positive("is not alert to a hand reaching into his coat pocket while he faces the fire")
    assert flipped and asked.endswith("while he faces the fire") and " not " not in f" {asked} "
    assert not_oracle(store.state, "npc.magby_applefoot", asked, ["npc.magby_applefoot"])  # his noticing: the roll


def test_reading_folded_into_talk_meets_letters(tmp_path: Path) -> None:
    """Fighter turn.4 (input 19): "I read the list over his shoulder. What's the name…" was one Talk/learn beat and
    met no gate, so the list was stolen before the "you can't read" moment. The recorded beat now meets Letters."""
    con = raw(FIGHTER, tmp_path)
    (resp,) = con.execute("SELECT response FROM model_calls WHERE turn_id = 'turn.4' AND role = 'reader'").fetchone()
    con.close()
    data = json.loads(resp)
    reader = ReaderResult.model_validate(normalise(dict(data.get("data", data))))
    store = open_at(FIGHTER, "turn.4", tmp_path)
    (plan,) = reader.plans(actor="pc.balak_deephelm", declared_seq=store.state.last_seq, mint=lambda p: f"{p}.x")
    g = check_gate(plan.beat, state=store.state, rules=RULES)
    store.close()
    assert plan.beat.verb == "verb.talk" and plan.beat.change and plan.beat.change.kind == "learn"
    assert g.gate == "G3" and g.redirect is not None and g.redirect.missing == "lic.lang.letters", g


def test_sitting_to_listen_takes_the_time(tmp_path: Path) -> None:
    """Explorer turn.12 (input 28): "sit and listen" was a Safe, sourceless, secret Observe: a full OFFER, a d20 of 1
    and "[RESULT] hidden check made". Re-run with the recorded beat and proposal: no OFFER, no roll, the time spent."""
    d = pause_detail(EXPLORER, tmp_path, 626)
    store = open_at(EXPLORER, "turn.12", tmp_path)
    plan = BeatPlan.model_validate(d["plan"])
    proposed = ProposedFrame.model_validate(d["proposed"])
    before = store.state.time.now
    try:
        with store.transaction("turn.12") as tx:
            res = run_beats(env(store, tx, stub(proposed)), [plan])
            out = res.outcomes[0]
            assert res.pause is None and out.status == "no_roll", (out.status, out.entry.gate_words)
            assert out.entry.gate_words == "no roll: take_the_time" and not tx.state.frames.get("frame.2")
            assert "take the time" in out.oof[0]["text"] and "hidden check" not in out.oof[0]["text"]
            assert tx.state.time.now != before
            raise _Rollback
    except _Rollback:
        pass
    finally:
        store.close()


def test_a_smaller_ask_of_someone_who_agreed_is_already_true(tmp_path: Path) -> None:
    """Explorer turn.10 (input 25): Morga had agreed (fact.106) to let Haley hear the refugees; the narrower ask
    rolled at 75% and its limited success replaced the agreement with "a smaller part of it". Now the Framer's
    judgment (`already_agreed`) is checked by code: no roll, and fact.106 stands. The turn.4 Oracle draw on Morga's
    willingness (fact.105) is never asked."""
    d = pause_detail(EXPLORER, tmp_path, 590)
    store = open_at(EXPLORER, "turn.10", tmp_path)
    plan = BeatPlan.model_validate(d["plan"])
    proposed = ProposedFrame.model_validate({**d["proposed"], "already_agreed": "fact.106"})
    try:
        with store.transaction("turn.10") as tx:
            res = run_beats(env(store, tx, stub(proposed)), [plan])
            assert res.pause is None and res.outcomes[0].status == "no_roll"
            assert tx.state.current_fact_id("npc.morga_embershield", "agreed") == "fact.106"
            assert "Agreed already" in res.outcomes[0].entry.changed
            raise _Rollback
    except _Rollback:
        pass
    finally:
        store.close()
    (tmp_path / "t4").mkdir()
    early = open_at(EXPLORER, "turn.4", tmp_path / "t4")
    assert not_oracle(early.state, "npc.morga_embershield",
                      "is willing to let Haley hear the refugees' story directly", ["npc.morga_embershield"])
    early.close()


def test_the_near_miss_never_prices_the_goals_reversal(tmp_path: Path) -> None:
    """Talker turn.12-13 (input 28): buying the sellsword a round, typed `change: none`, near-missed and was priced
    "he turns the round down": the player paid a coin and got a refusal. The beat is now typed `persuade_to` and the
    close call offers no closed door on him."""
    d = pause_detail(TALKER, tmp_path, 523)
    store = open_at(TALKER, "turn.12", tmp_path)
    plan = BeatPlan.model_validate(d["plan"])
    fr = d["frame"]
    beat = plan.beat
    typed_goal(store.state, beat)
    assert beat.change is not None and beat.change.kind == "persuade_to" and beat.change.what == beat.target
    tc = fr["threatened_cost"]
    proposed = ProposedFrame(anchor=fr["anchor"], attribute=fr["attribute"],
                             obstacle=Obstacle(kind="opposed", entity=beat.target), stakes_source="none",
                             threatened_cost=CostDecl(menu_id=tc["menu_id"], form_intent=tc["form_intent"]),
                             method_consequences=list(fr.get("method_consequences") or []))
    g = check_gate(beat, state=store.state, rules=RULES)
    f = frame_check(proposed, beat, state=store.state, rules=RULES, gate=g)
    store.close()
    assert isinstance(f, Frame) and f.threatened_cost.menu_id == "cost.closed_door"
    sac = [c for c in near_miss_choices(f, RULES) if c["id"].startswith("success_at_cost")]
    assert sac and all("closed_door" not in c["id"] and "turns the round down" not in c["label"] for c in sac), sac


def test_the_fallback_is_framed_on_its_own_scope(tmp_path: Path) -> None:
    """Fighter turns 8-9 (inputs 24-25): "Try it anyway" re-sent the whole intent, so the Framer rated the full
    reading "hard" and code added +5 on top: a 5% OFFER, "failing badly 55%" for a nuisance. Now the Framer sees only
    the fallback's scope, the shift is added once, and with nothing at stake below Very hard it takes the time."""
    d = pause_detail(FIGHTER, tmp_path, 447)  # the recorded OFFER: Framer said hard on the whole intent
    hard = ProposedFrame.model_validate(d["proposed"])
    for tier, want in (("hard", "offer"), ("moderate", "no_roll")):
        cut = tmp_path / tier
        cut.mkdir()
        store = open_at(FIGHTER, "turn.9", cut)
        seen: list[tuple[Beat, GateDecision]] = []
        proposed = hard.model_copy(update={"obstacle": hard.obstacle.model_copy(update={"tier": tier,
                                                                                       "obstacle_class": "other"})})
        try:
            with store.transaction("turn.9") as tx:
                res = resume(env(store, tx, stub(proposed, seen)), tx.state.open_pause(), "accept:lic.lang.letters")
                beat, gate = seen[-1]
                assert beat.intent.startswith("pick out numerals") and "most dangerous" not in beat_message(beat, gate)
                if want == "offer":
                    assert res.pause is not None and res.pause.detail["frame"]["dc"] == 25  # 20 + 5, once: it rolls
                else:
                    assert res.pause is None and res.outcomes[0].status == "no_roll"
                    assert res.outcomes[0].entry.reach == "limited"  # at the fallback's reach cap
                raise _Rollback
        except _Rollback:
            pass
        finally:
            store.close()
