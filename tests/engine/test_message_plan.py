"""Spec 017 (ROUND4-ANALYSIS R4): a message is a plan of beats that survives pauses. The real cases run on the
playtest saves cut back to just before the turn (tests/fixtures/plan_*.db.gz), with the Reader's own answer."""

from __future__ import annotations

import gzip
import shutil
from pathlib import Path
from typing import Any

from engine.data.loader import load_rules
from engine.dm.context import TurnContext
from engine.dm.turn import answer_pause, run_turn
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.store.db import Store
from engine.store.events import Event
from tests.engine.test_pipeline import env_for, plan, stub_framer
from tests.engine.test_pipeline import setup as dock_setup
from tests.engine.test_turn_adjudication import D20, framer

FIXTURES = Path(__file__).parents[1] / "fixtures"
RULES = load_rules()


def _beat(intent: str, method: str, verb: str, target: str, change: dict[str, str], *, shape: str = "now",
          purpose: str = "own_change", against_will: bool = False, verbs: tuple[str, ...] = (),
          pressure: str = "none") -> dict[str, Any]:
    return {"against_will": against_will, "assertion": None, "change": change, "g4_fact": None, "intent": intent,
            "intent_verbs": list(verbs), "method": method, "pressure": pressure, "purpose": purpose, "shape": shape,
            "speech": verb == "verb.talk", "target": target, "uses_power": False, "verb": verb}


def _part(text: str, cls: str = "DECLARATION", qk: str = "none", topic: str | None = None) -> dict[str, Any]:
    return {"class": cls, "question_kind": qk, "text": text, "topic": topic}


def _reader(parts: list[dict[str, Any]], beats: list[dict[str, Any]], restatement: str,
            questions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"beats": beats, "clarifying_question": None, "fact_questions": questions or [], "parts": parts,
            "player_quantity": None, "restatement": restatement, "rests_on": "none"}


NONE = {"kind": "none", "what": "none", "whom": "none"}
# fighter 20261008-192946 input 26 (turn.11), the Reader's answer as logged
FIGHTER_11 = _reader(
    [_part("I sheathe my sword, then head for the reeve's cell and try to force my way in to see the prisoner.")],
    [_beat("the sword is put away", "sheathe the sword", "verb.handle", "none", NONE, purpose="free_activity",
           verbs=("sheathe",)),
     _beat("the player is at the reeve's cell", "walk to the reeve's cell", "verb.move",
           "loc.windy_march_saltton.hall",
           {"kind": "move_to", "what": "loc.windy_march_saltton.hall", "whom": "pc.selwin_elderhill"},
           verbs=("go", "reach")),
     _beat("the player is inside the reeve's cell and sees the prisoner", "force a way in past whoever keeps the cell",
           "verb.force", "loc.windy_march_saltton.hall",
           {"kind": "open", "what": "loc.windy_march_saltton.hall", "whom": "none"}, against_will=True,
           verbs=("force", "see"))],
    "Sheathe the sword. Then: walk to the reeve's cell (taken as the hall). Then: force a way in past whoever holds "
    "the cell, to see the prisoner.",
    [{"odds_rung": "likely", "predicate": "the reeve's cell has guards posted at its door",
      "subject": "loc.windy_march_saltton"}])
# fighter input 19 (turn.4)
FIGHTER_4 = _reader(
    [_part("I round the bend and keep hunting for the refugees, hand on my sword."),
     _part("If I find them, I walk straight up and demand they tell me their story.")],
    [_beat("get past the bend and keep searching the lane for the refugees",
           "round the bend and keep searching the lane, hand on sword", "verb.move", "loc.windy_march_saltton",
           {"kind": "move_to", "what": "loc.windy_march_saltton", "whom": "pc.selwin_elderhill"},
           verbs=("search", "move")),
     _beat("make the refugees tell their story once found", "walk up to the refugees and demand they tell their story",
           "verb.talk", "none", {"kind": "persuade_to", "what": "none", "whom": "none"}, shape="conditional",
           verbs=("demand", "ask"), pressure="insistence")],
    "Move: round the bend and keep searching the lane for the refugees. Then: if found, walk up to them and demand "
    "they tell their story.")
# talker 20261008-192926 input 29 (turn.14)
TALKER_14 = _reader(
    [_part("I take my coin back"), _part("nod to her", "SPEECH"),
     _part("ask the other carters at the table if any of them have actually seen the barrels loaded", "SPEECH",
           "what_happened", "barrels loaded"),
     _part("head for the gate to find Ivas")],
    [_beat("the coin is back in my hand", "take my coin back from the board", "verb.handle", "item.coin",
           {"kind": "take", "what": "item.coin", "whom": "none"}, verbs=("take", "reclaim")),
     _beat("I am at the gate looking for Ivas Terier", "walk from the back table to the gate", "verb.move",
           "loc.long_reach_sandburn.gate",
           {"kind": "move_to", "what": "loc.long_reach_sandburn.gate", "whom": "pc.wila_bramblefoot"},
           verbs=("go", "find"))],
    "Take the coin back from the board.\nThen: go to the gate to look for Ivas Terier.")


def _game(tmp_path: Path, fixture: str, reader: dict[str, Any], faces: list[int]) -> TurnContext:
    path = tmp_path / fixture.removesuffix(".gz")
    with gzip.open(FIXTURES / fixture, "rb") as src, path.open("wb") as dst:
        shutil.copyfileobj(src, dst)
    store = Store.open(path)
    model = ScriptedModel({Role.READER: [lambda schema, packet: reader], Role.FRAMER: [framer() for _ in range(4)]})
    rng = D20.of(store)
    rng.faces = list(faces)
    return TurnContext(store=store, rules=RULES, rng=rng, model=model, config={"auto_commit": False})


def _blocks(res: Any, kind: str) -> list[str]:
    return [o["text"] for o in res.oof if o["kind"] == kind]


def test_fighter_turn_11_offer_is_titled_by_its_own_beat_and_resolves(tmp_path: Path) -> None:
    """"Sheathe the sword. Then walk to the reeve's cell. Then force a way in": the OFFER was titled "Sheathe the
    sword" while it framed the door. The sheathe is a free activity, the walk the Force's reach (one beat)."""
    ctx = _game(tmp_path, "plan_fighter_turn11.db.gz", FIGHTER_11, faces=[19])
    res = run_turn(ctx, FIGHTER_11["parts"][0]["text"])
    assert res.pause is not None and res.offer is not None
    title = res.offer["restated_beat"]
    assert "force a way in" in title.lower() and "sheathe" not in title.lower()
    assert res.pause.prompt == title and "Sheathe" not in _blocks(res, "OFFER")[0].split("\n")[0]
    done = answer_pause(ctx, "commit")
    assert done.pause is None
    [b] = [b for b in done.record.beats if b.rolled]
    assert b.verb == "verb.force" and b.degree in ("success", "critical_success") and "force" in b.restatement.lower()
    assert _blocks(done, "RESULT")
    ctx.store.close()


def test_own_line_takes_the_beats_own_sentence() -> None:
    """Live run 20261008-220608: a free act's sentence and the Reader's "Beat 1:" label titled the OFFER."""
    from engine.resolve.pipeline import own_line

    two = "Draw the dagger. Ask Aldwen to open the chain across the road. Then: walk out through the gate."
    assert own_line(two, "ask Aldwen to open the gate chain Aldwen opens the chain") == \
        "Ask Aldwen to open the chain across the road."
    assert own_line(two, "walk out through the gate the PC is outside") == "Walk out through the gate."
    beat1 = "Beat 1: go down into the ditch to the looted wagon. Then: check the wagon for anything left behind."
    assert own_line(beat1, "go down into the ditch to the wagon", alone=False) == \
        "Go down into the ditch to the looted wagon."
    assert own_line("Grab the purse and punch her.", "punch her", alone=False) == ""  # P-064: one line, two beats


def test_fighter_turn_4_demand_their_story_runs_after_the_offer(tmp_path: Path) -> None:
    """"... If I find them, I walk straight up and demand they tell me their story": the conditional Talk beat was a
    "queued" note and never ran. It is on the plan: the OFFER names it, and it runs once the move succeeds."""
    ctx = _game(tmp_path, "plan_fighter_turn4.db.gz", FIGHTER_4, faces=[19, 19, 19])
    res = run_turn(ctx, " ".join(p["text"] for p in FIGHTER_4["parts"]))
    assert res.pause is not None and res.pause.detail["stage"] == "offer"
    assert "Then: walk up to the refugees and demand they tell their story" in _blocks(res, "OFFER")[0]
    assert [q["when"] for q in res.pause.detail["queued"]] == ["conditional"]
    out = [answer_pause(ctx, "commit")]
    while out[-1].pause is not None and out[-1].pause.detail.get("stage") == "offer":
        out.append(answer_pause(ctx, "commit"))
    talk = [b for o in out for b in o.record.beats if b.verb == "verb.talk"]
    assert talk and "demand" in talk[0].restatement.lower()  # answered, not dropped
    assert not any("queued for the next" in n for o in out for n in o.record.notes)
    ctx.store.close()


def test_a_plan_stops_and_asks_when_the_pc_goes_down(tmp_path: Path, monkeypatch: Any) -> None:
    import engine.resolve.pipeline as pl

    dock, rng = dock_setup(tmp_path)
    real = pl.apply_change

    def falls(tx: Any, rules: Any, beat: Any, reach: int, pc: str | None = None) -> Any:
        if beat.id == "beat.1":  # the first beat's result puts the PC down (a cost, a blow: the cause is not tested)
            tx.add(Event.of("fact_set", {"source": "ruling"}, source="test", rule_id="07.2.1", fact_id=tx.mint("fact"),
                            subject=dock.pc, predicate="down", value=True, visibility="shown"))
        return real(tx, rules, beat, reach, pc=pc)

    monkeypatch.setattr(pl, "apply_change", falls)
    plans = [plan(dock, f"look around {i}", "verb.observe", n=i) for i in (1, 2)]
    fr = stub_framer(trivial=("verb.observe",))
    with dock.store.transaction("turn.1") as tx:
        res = pl.run_beats(env_for(dock, tx, rng, framer=fr), plans)
    assert [o.status for o in res.outcomes] == ["no_roll"]
    assert res.pause is not None and res.pause.detail["stage"] == "plan"
    assert res.pause.prompt == "You are down. Still go on to look around 2?"
    assert [c["id"] for c in res.pause.choices] == ["continue", "withdraw"]
    with dock.store.transaction("turn.2") as tx:  # stop: said, not run
        stop = pl.resume(env_for(dock, tx, rng, framer=fr), dock.state.open_pause(), "withdraw")  # type: ignore[arg-type]
    assert not stop.outcomes and stop.queued == ["look around 2"] and dock.state.open_pause() is None


def test_a_withdrawn_offer_asks_before_the_rest_and_go_on_runs_it(tmp_path: Path) -> None:
    dock, rng = dock_setup(tmp_path)
    import engine.resolve.pipeline as pl

    plans = [plan(dock, "sneak to the ferry", "verb.sneak", n=1), plan(dock, "look at the ferry", "verb.observe", n=2)]
    fr = stub_framer(trivial=("verb.observe",))
    with dock.store.transaction("turn.1") as tx:
        pl.run_beats(env_for(dock, tx, rng, framer=fr), plans)
    with dock.store.transaction("turn.2") as tx:
        res = pl.resume(env_for(dock, tx, rng, framer=fr), dock.state.open_pause(), "withdraw")  # type: ignore[arg-type]
    assert res.pause is not None and res.pause.prompt == "That did not happen. Still go on to look at the ferry?"
    with dock.store.transaction("turn.3") as tx:
        res = pl.resume(env_for(dock, tx, rng, framer=fr), dock.state.open_pause(), "continue")  # type: ignore[arg-type]
    assert [o.status for o in res.outcomes] == ["no_roll"] and res.pause is None


def test_talker_turn_14_the_carters_answer_before_the_move_to_the_gate(tmp_path: Path) -> None:
    """"... ask the other carters at the table if any of them have actually seen the barrels loaded. Then I head for
    the gate": the move resolved first and the NPC step ran at the gate, so no carter answered. The words said here
    are answered here; the move waits on a one-line "Still go on to ...?"."""
    ctx = _game(tmp_path, "plan_talker_turn14.db.gz", TALKER_14, faces=[19, 19])
    st = ctx.store.state
    inn = st.scene.place_id if st.scene else None
    res = run_turn(ctx, "I take my coin back, nod to her, and ask the other carters at the table if any of them have "
                        "actually seen the barrels loaded. Then I head for the gate to find Ivas.")
    assert res.pause is not None and res.pause.detail["stage"] == "offer"  # the coin's OFFER: the words wait
    assert res.pause.detail["said_first"][-1].startswith("ask the other carters")
    out = answer_pause(ctx, "commit")
    assert out.pause is not None and out.pause.detail["stage"] == "plan"
    assert out.pause.prompt == "Still go on to walk from the back table to the gate?"
    assert any(p.cls == "SPEECH" and p.text.startswith("ask the other carters") for p in out.record.parts)
    answered = [a for a in out.record.npc_actions if a.npc.startswith("npc.")]
    assert answered, "a carter at the table answers (T5 ran in the inn)"
    assert ctx.store.state.scene is not None and ctx.store.state.scene.place_id == inn  # still in the inn
    gone = answer_pause(ctx, "continue")  # the move's own OFFER, titled by its own clause
    assert gone.offer is not None and gone.offer["restated_beat"] == "Go to the gate to look for Ivas Terier."
    ctx.store.close()
