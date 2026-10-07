"""T042: the adjudication pass (PR-12-1 T1–T6) on the dock fixture with the offline and scripted models."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from engine import ids
from engine.dm.context import TurnContext
from engine.dm.schemas import prune
from engine.dm.turn import answer_pause, run_turn
from engine.llm.base import ModelUnavailable, Role
from engine.llm.offline import OfflineModel, ScriptedModel, enum_at
from engine.rng import Rng
from engine.store.events import EntityRecord, Event, SceneRecord
from tests.fixtures.scene_dock import LICENCES, DockScene, build_dock

Fn = Callable[[dict[str, Any], Any], dict[str, Any]]


class D20(Rng):
    """The game's RNG with scripted faces for `roll_check` draws only (everything else stays seeded)."""

    faces: list[int]

    @classmethod
    def of(cls, store: Any) -> D20:
        rng = cls.for_store(store)
        assert isinstance(rng, D20)
        rng.faces = []
        return rng

    def draw(self, n: int, purpose: str, *, stream: str = "dice", table_id: str | None = None) -> int:
        if purpose.startswith("roll_check") and getattr(self, "faces", None):
            face = self.faces.pop(0)
            if self.log is not None:
                self.log.record_rng_draw(stream, purpose, face, sides=n, table_id=table_id)
            return face
        return super().draw(n, purpose, stream=stream, table_id=table_id)


def beat(intent: str, verb: str, *, gate: str = "G1", necessity: str = "uncertain_and_costly", target: str = "none",
         license: str = "none", g4_fact: str | None = None, verbs: tuple[str, ...] = ()) -> dict[str, Any]:
    return {"intent": intent, "method": intent, "assertion": None, "shape": "single", "target": target, "verb": verb,
            "license": license, "gate": gate, "g4_fact": g4_fact, "necessity": necessity,
            "intent_verbs": list(verbs)}


def reader(cls: str, text: str, *beats: dict[str, Any], questions: tuple[dict[str, Any], ...] = ()) -> Fn:
    data = {"parts": [{"text": text, "class": cls}], "pending_answer": None, "fact_questions": list(questions),
            "beats": list(beats), "clarifying_question": None, "restatement": text, "player_quantity": None}
    return lambda schema, packet: prune(data, schema)


def framer(**over: Any) -> Fn:
    def fill(schema: dict[str, Any], packet: Any) -> dict[str, Any]:
        d: dict[str, Any] = {
            "anchor": enum_at(schema, "anchor")[0], "deltas": [], "attribute": enum_at(schema, "attribute")[0],
            "deed_tag": enum_at(schema, "deed_tag")[0], "traits": [],
            "obstacle": {"kind": "tier", "tier": "moderate", "entity": None}, "levers": [], "snags": [],
            "stakes_source": "none", "stakes_heavy": False, "lethal": False, "reach_whole": True,
            "reach_one_factor": False, "threatened_cost": {"menu_id": "cost.time", "form_intent": "",
                                                           "source_fact": None},
            "alternate_cost": None, "method_consequences": [], "secret": False}
        d.update(over)
        return prune(d, schema)

    return fill


RISKY = {"stakes_source": "aware_opponent_or_observer",
         "threatened_cost": {"menu_id": "cost.exposure", "form_intent": "the watch hears", "source_fact": None},
         "alternate_cost": {"menu_id": "cost.time", "form_intent": "you wait for the lantern", "source_fact": None}}
SNEAK = beat("slip past the watch to the ferry", "verb.sneak", target="npc.sela_vey", verbs=("sneak",))
QUIET_WORLD = {"responses": []}


def setup(tmp_path: Path, model: Any, **config: Any) -> tuple[DockScene, TurnContext]:
    dock = build_dock(tmp_path)
    rng = D20.of(dock.store)
    ctx = TurnContext(store=dock.store, rules=dock.rules, rng=rng, model=model, config=config)
    return dock, ctx


def rolls(store: Any) -> list[dict[str, Any]]:
    return [d for d in store.rng_draws() if str(d["purpose"]).startswith("roll_check")]


def types(store: Any, turn_id: str) -> list[str]:
    return [e.type for e in store.events() if e.turn_id == turn_id]


def offer_turn(tmp_path: Path, **frame: Any) -> tuple[DockScene, TurnContext, ScriptedModel, Any]:
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I slip past the watch.", SNEAK)],
                           Role.FRAMER: [framer(**frame)], Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    res = run_turn(ctx, "I slip past the watch.")
    return dock, ctx, model, res


# ------------------------------------------------------------------------------------------- OFFER


def test_offer_before_roll_and_nothing_rolled_until_commit(tmp_path: Path) -> None:
    dock, ctx, model, res = offer_turn(tmp_path, **RISKY)
    assert res.pause is not None and res.pause.kind == "offer"
    assert [c["id"] for c in res.pause.choices][:3] == ["commit", "change", "withdraw"]
    assert res.offer is not None and res.offer["stakes"] == "risky"
    assert not rolls(dock.store) and not dock.state.frames
    assert "frame_committed" not in types(dock.store, res.turn_id)
    assert res.turn_record.pause and res.turn_record.pause["kind"] == "offer"
    beat_id = res.pause.detail["plan"]["beat"]["id"]
    model.push(Role.WORLD, QUIET_WORLD)
    ctx.rng.faces = [18]  # type: ignore[attr-defined]
    res2 = answer_pause(ctx, "commit")  # the same beat resumes from the stored frame
    assert res2.pause is None and len(rolls(dock.store)) == 1
    t = types(dock.store, res2.turn_id)
    assert t.index("frame_committed") < t.index("frame_resolved")
    fid = res2.record.beats[0].frame_id
    assert fid and dock.state.frames[fid].resolved is not None
    assert res2.record.beats[0].beat_id == beat_id and res2.record.beats[0].degree == "success"
    assert "evidence_recorded" in t and res2.turn_record.beats == [fid]
    assert dock.store.rebuild() == dock.state


def test_withdraw_spends_nothing(tmp_path: Path) -> None:
    dock, ctx, model, res = offer_turn(tmp_path, **RISKY)
    before = dock.state.model_copy(deep=True)
    res2 = answer_pause(ctx, "withdraw")
    st = dock.state
    assert res2.pause is None and not rolls(dock.store) and not st.frames
    assert st.time.now == before.time.now and st.quantities == before.quantities and st.clocks == before.clocks
    assert set(types(dock.store, res2.turn_id)) <= {"pause_closed", "offer_logged"}


def test_change_gives_a_fresh_offer(tmp_path: Path) -> None:
    dock, ctx, model, res = offer_turn(tmp_path, **RISKY)
    assert res.pause is not None
    model.push(Role.FRAMER, framer())  # the second framing: safe this time
    res2 = answer_pause(ctx, "change")
    assert res2.pause is not None and res2.pause.kind == "offer" and res2.pause.pause_id != res.pause.pause_id
    assert res2.offer is not None and res2.offer["stakes"] == "safe"
    assert not rolls(dock.store) and sum(1 for r, _ in model.calls if r == Role.FRAMER) == 2


def test_go_big_reframes_once(tmp_path: Path) -> None:
    dock, ctx, model, res = offer_turn(tmp_path, **RISKY)
    assert res.pause is not None and "go_big" in [c["id"] for c in res.pause.choices]
    res2 = answer_pause(ctx, "go_big")
    assert res2.offer is not None and res2.offer["stakes"] == "dire" and res2.offer["trades"] == []


def test_near_miss_pauses_then_success_at_a_cost(tmp_path: Path) -> None:
    dock, ctx, model, res = offer_turn(tmp_path, **RISKY)
    assert res.offer is not None
    ctx.rng.faces = [res.offer["need"] - 1]  # type: ignore[attr-defined]  # margin -1: a near miss
    res2 = answer_pause(ctx, "commit")
    assert res2.pause is not None and res2.pause.kind == "near_miss"
    assert res2.pause.default_choice == "failure"
    fid = res2.pause.detail["frame"]["id"]
    assert fid in dock.state.frames and dock.state.frames[fid].resolved is None
    model.push(Role.WORLD, QUIET_WORLD)
    res3 = answer_pause(ctx, "success_at_cost:cost.exposure")
    b = res3.record.beats[0]
    assert b.success_at_cost and b.costs and b.costs[0].menu_id == "cost.exposure"
    assert dock.state.frames[fid].resolved is not None and len(rolls(dock.store)) == 1


def test_auto_commit_rolls_without_waiting(tmp_path: Path) -> None:
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I slip past.", SNEAK)],
                           Role.FRAMER: [framer()], Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model, auto_commit=True)
    ctx.rng.faces = [19]  # type: ignore[attr-defined]
    res = run_turn(ctx, "I slip past.")
    assert res.pause is None and len(rolls(dock.store)) == 1
    assert any(o["kind"] == "OFFER" and "auto-committed" in o["text"] for o in res.oof)


def test_lethal_frame_warns_first_and_is_never_auto_committed(tmp_path: Path) -> None:
    cut = beat("knife the cutthroat", "verb.strike", verbs=("stab",))
    model = ScriptedModel({Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model, auto_commit=True)
    with dock.store.transaction() as tx:
        rec = EntityRecord(id="foe.cutthroat", kind="adversary", name="the cutthroat",
                           data={"threat_advisory": "lethal", "attributes": {"agility": 2}, "defenses": {"guard": 12},
                                 "attacks": [{"name": "knife", "severity": "S4"}]})
        tx.add(Event.of("entity_created", source="test", entity=rec))
        tx.add(Event.of("scene_ended", source="test", scene_id=dock.scene, reason="test"))
        sid = tx.mint(ids.SCENE)
        tx.add(Event.of("scene_started", source="test", scene_id=sid, scene=SceneRecord(
            scene_id=sid, place_id=dock.place, mode="site", cast_present=[dock.watch, "foe.cutthroat"],
            started_seq=tx.state.last_seq)))
    cut["target"] = "foe.cutthroat"
    model.push(Role.READER, reader("DECLARATION", "I knife the cutthroat.", cut))
    lethal = {"stakes_source": "aware_opponent_or_observer", "stakes_heavy": True, "lethal": True,
              "obstacle": {"kind": "entity_defense", "tier": None, "entity": "foe.cutthroat"},
              "threatened_cost": {"menu_id": "cost.harm", "form_intent": "his knife", "source_fact": None},
              "alternate_cost": {"menu_id": "cost.footing", "form_intent": "you slip", "source_fact": None}}
    model.push(Role.FRAMER, framer(**lethal))
    res = run_turn(ctx, "I knife the cutthroat.")
    assert res.pause is not None and res.pause.detail["stage"] == "warning"
    assert "[WARNING]" in res.pause.prompt and not rolls(dock.store)
    assert dock.state.fact_value("foe.cutthroat", "lethal_context")
    res2 = answer_pause(ctx, "continue")
    assert res2.pause is not None and res2.pause.kind == "offer" and res2.offer is not None
    assert res2.offer["lethal"] is True and not rolls(dock.store)  # auto_commit is on, yet it waits


def test_settled_fact_stays_settled(tmp_path: Path) -> None:
    q = {"subject": "loc.the_night_dock", "predicate": "is the ferry running tonight", "odds_rung": "even"}
    model = ScriptedModel({Role.READER: [reader("FICTION_QUESTION", "Is the ferry running tonight?", questions=(q,)),
                                         reader("FICTION_QUESTION", "Is the ferry running?", questions=(q,))],
                           Role.WORLD: [QUIET_WORLD, QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    a = run_turn(ctx, "Is the ferry running tonight?")
    draws = len(dock.store.rng_draws("oracle"))
    b = run_turn(ctx, "Is the ferry running?")
    assert a.record.oracle and b.record.oracle
    assert a.record.oracle[0].fact_id == b.record.oracle[0].fact_id
    assert a.record.oracle[0].answer.split(",")[0] == b.record.oracle[0].answer
    assert len(dock.store.rng_draws("oracle")) == draws and draws >= 1
    assert sum(1 for e in dock.store.events(types=["oracle_answered"])) == 1
    assert b.turn_record.oracle_calls == []


def test_g3_gives_an_alternative_and_spends_nothing(tmp_path: Path) -> None:
    fly = beat("pick the harbour master's strongbox lock with arcane force", "verb.handle", gate="G3",
               verbs=("pick",))
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I magic the lock open.", fly)],
                           Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    before = dock.state.model_copy(deep=True)
    res = run_turn(ctx, "I magic the lock open.")
    b = res.record.beats[0]
    assert b.gate == "G3" and ("Possible now" in b.gate_words or res.pause is not None)
    assert any(o["kind"] == "REDIRECT" for o in res.oof)
    st = dock.state
    assert not st.frames and not rolls(dock.store) and st.quantities == before.quantities
    assert st.time.now == before.time.now and st.clocks == before.clocks
    assert Role.FRAMER not in [r for r, _ in model.calls]


def test_g4_gives_an_alternative_and_spends_nothing(tmp_path: Path) -> None:
    dock = build_dock(tmp_path)
    ferry = dock.facts["ferry"]
    walk = beat("walk across the water to the far shore", "verb.move", gate="G4", g4_fact=ferry)
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I walk across the water.", walk)],
                           Role.WORLD: [QUIET_WORLD]})
    ctx = TurnContext(store=dock.store, rules=dock.rules, rng=dock.rng, model=model)
    before = dock.state.model_copy(deep=True)
    res = run_turn(ctx, "I walk across the water.")
    b = res.record.beats[0]
    assert b.gate == "G4" and "Possible now" in b.gate_words and res.pause is None
    assert not dock.state.frames and dock.state.time.now == before.time.now
    assert "ruling_logged" in types(dock.store, res.turn_id)


def test_talk_and_trivial_acts_roll_nothing(tmp_path: Path) -> None:
    talk = beat("ask the ferryman the fare", "verb.talk", necessity="trivial", target="npc.tam_harlan")
    model = ScriptedModel({Role.READER: [reader("SPEECH", '"Evening."'),
                                         reader("DECLARATION", "I ask the ferryman the fare.", talk)]})
    dock, ctx = setup(tmp_path, model)
    a = run_turn(ctx, '"Evening."')
    b = run_turn(ctx, "I ask the ferryman the fare.")
    assert not a.record.beats and a.record.parts[0].handled == "answered"
    assert b.record.beats[0].gate_words == "no roll: trivial" and not b.record.beats[0].rolled
    assert not rolls(dock.store) and not dock.state.frames
    assert a.record.npc_actions  # the NPCs present answer from their table (offline World role)


def test_offline_model_plays_a_turn(tmp_path: Path) -> None:
    dock, ctx = setup(tmp_path, OfflineModel())
    res = run_turn(ctx, "I sneak past the guard toward the ferry. Is the ferry running tonight?")
    assert [p.cls for p in res.record.parts] == ["DECLARATION", "FICTION_QUESTION"]
    assert res.record.oracle and res.pause is not None and res.pause.kind == "offer"
    assert dock.store.turn(res.turn_id) is not None and res.turn_record.model_calls
    assert dock.store.rebuild() == dock.state


def test_turn_rolls_back_cleanly_when_the_model_fails(tmp_path: Path) -> None:
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I slip past the watch.", SNEAK)],
                           Role.FRAMER: [ModelUnavailable("provider down")]})
    dock, ctx = setup(tmp_path, model)
    seq, state = dock.store.last_seq, dock.state.model_copy(deep=True)
    with pytest.raises(ModelUnavailable):
        run_turn(ctx, "I slip past the watch.")
    assert dock.store.last_seq == seq and dock.store.state == state and ctx.tx is None
    tid = ids.counter_id(ids.TURN, 1)
    rec = dock.store.turn(tid)
    assert rec is not None and rec.input_verbatim == "I slip past the watch."  # T1: kept, retryable
    assert dock.store.rebuild() == dock.state


def test_pc_holds_two_licences_and_an_ability(tmp_path: Path) -> None:
    dock = build_dock(tmp_path)
    st = dock.state
    assert [x.license_id for x in st.licenses[dock.pc]] == list(LICENCES)
    assert st.entities[dock.pc].data["abilities"] == ["ab.soft_step"]
    assert st.scene is not None and st.scene.cast_present == [dock.ferryman, dock.watch]
    assert st.entities[dock.watch].data["wants"] and "wants" in st.entities[dock.watch].sealed_fields
    assert dock.clock in st.clocks and st.time.now.watch == 3
