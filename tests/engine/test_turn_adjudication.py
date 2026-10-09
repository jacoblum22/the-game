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


def beat(intent: str, verb: str, *, target: str = "none", g4_fact: str | None = None, verbs: tuple[str, ...] = (),
         against_will: bool = False, uses_power: bool = False, speech: bool = False,
         shape: str = "now") -> dict[str, Any]:
    """A Reader beat (12.2.2 decision 3, DL-12-50): the gate and the roll test are computed from it."""
    return {"intent": intent, "method": intent, "purpose": "own_change", "assertion": None, "shape": shape,
            "target": target, "verb": verb, "pressure": "request" if verb == "verb.talk" else "none",
            "against_will": against_will, "uses_power": uses_power, "speech": speech or verb == "verb.talk",
            "g4_fact": g4_fact, "intent_verbs": list(verbs)}


def reader(cls: str, text: str, *beats: dict[str, Any], questions: tuple[dict[str, Any], ...] = (),
           qk: str = "none") -> Fn:
    data = {"parts": [{"text": text, "class": cls, "question_kind": qk, "topic": None}], "pending_answer": None,
            "fact_questions": list(questions),
            "beats": list(beats), "clarifying_question": None, "restatement": text, "player_quantity": None}
    return lambda schema, packet: prune(data, schema)


def framer(**over: Any) -> Fn:
    def fill(schema: dict[str, Any], packet: Any) -> dict[str, Any]:
        d: dict[str, Any] = {
            "anchor": enum_at(schema, "anchor")[0], "deltas": [], "attribute": enum_at(schema, "attribute")[0],
            "deed_tag": enum_at(schema, "deed_tag")[0], "traits": [],
            "obstacle": {"kind": "tier", "obstacle_class": "other", "tier": "moderate", "entity": None},
            "nudge_why": None, "nudge": "0", "nudge_fact": None, "request_size": "R2", "levers": [], "snags": [],
            "stakes_source": "none", "stakes_heavy": False, "lethal": False, "reach_whole": True,
            "reach_one_factor": False, "reach_two_factors": False, "asks": "none",
            "threatened_cost": {"menu_id": "cost.time", "form_intent": "",
                                  "source_fact": None},
            "alternate_cost": None, "method_consequences": [], "secret": False}
        d.update(over)
        return prune(nest_stakes(d), schema)

    return fill


def nest_stakes(d: dict[str, Any]) -> dict[str, Any]:
    """A Framer answer written with the flat stakes fields, as the paired `stakes` choice the schema asks for."""
    out = {k: v for k, v in d.items() if k not in ("stakes_source", "threatened_cost", "alternate_cost")}
    out["stakes"] = {"source": d.get("stakes_source") or "none", "threatened_cost": d.get("threatened_cost"),
                     "alternate_cost": d.get("alternate_cost")}
    return out


RISKY = {"stakes_source": "aware_opponent_or_observer",
         "threatened_cost": {"menu_id": "cost.exposure", "form_intent": "the watch hears", "source_fact": None},
         "alternate_cost": {"menu_id": "cost.time", "form_intent": "you wait for the lantern", "source_fact": None}}
SNEAK = beat("slip past the watch to the ferry", "verb.sneak", target="npc.sela_vey", verbs=("sneak",))
QUIET_WORLD = {"responses": []}


def setup(tmp_path: Path, model: Any, **config: Any) -> tuple[DockScene, TurnContext]:
    dock = build_dock(tmp_path)
    rng = D20.of(dock.store)
    # these tests read the OFFER pause: auto-commit (on by default for Safe frames, DL-01-32) is opted out here
    ctx = TurnContext(store=dock.store, rules=dock.rules, rng=rng, model=model, config={"auto_commit": False, **config})
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
    ids_ = [c["id"] for c in res.pause.choices]
    assert ids_[0] == "commit" and ids_[-2:] == ["change", "withdraw"]  # 12.15.2: Do it … Another way, Back off
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
    # P-012: the committed roll states its outcome once (12.15.3)
    result = [o["text"] for o in res2.oof if o["kind"] == "RESULT"]
    assert len(result) == 1 and result[0].startswith("[RESULT] d20 18 → ") and result[0].endswith("· success")
    assert "evidence_recorded" in t and res2.turn_record.beats == [fid]
    assert dock.store.rebuild() == dock.state


def test_a_success_rides_and_the_same_ask_does_not_roll_again(tmp_path: Path) -> None:
    """P-075 (talker 185715 inputs 28-31): she had already agreed, and the same ask rolled again at 50% with a
    closed door at stake. A success this scene, same target, anchor and approach, rides (01.4.2)."""
    dock, ctx, model, res = offer_turn(tmp_path, **RISKY)
    model.push(Role.WORLD, QUIET_WORLD)
    ctx.rng.faces = [18]  # type: ignore[attr-defined]
    assert answer_pause(ctx, "commit").record.beats[0].degree == "success"
    model.push(Role.READER, reader("DECLARATION", "I slip past the watch again.", SNEAK))
    model.push(Role.FRAMER, framer(**RISKY))
    model.push(Role.WORLD, QUIET_WORLD)
    res2 = run_turn(ctx, "I slip past the watch again.")
    assert res2.pause is None and len(rolls(dock.store)) == 1
    assert res2.record.beats[0].gate_words == "no roll: riding"


def test_withdraw_spends_nothing(tmp_path: Path) -> None:
    dock, ctx, model, res = offer_turn(tmp_path, **RISKY)
    before = dock.state.model_copy(deep=True)
    res2 = answer_pause(ctx, "withdraw")
    st = dock.state
    assert res2.pause is None and not rolls(dock.store) and not st.frames
    assert st.time.now == before.time.now and st.quantities == before.quantities and st.clocks == before.clocks
    written = [e for e in dock.store.events() if e.turn_id == res2.turn_id]
    # 12.11.9: the present NPCs' activities (scene-state details, T-12-18, rolled once per scene: the meta marks
    # whose were rolled) are the only facts; nothing is spent
    assert all(e.payload.predicate == "detail.activity" for e in written if e.type == "fact_set")  # type: ignore[attr-defined]
    assert all(e.payload.key == "npc.activity_rolled" for e in written if e.type == "meta_set")  # type: ignore[attr-defined]
    assert set(types(dock.store, res2.turn_id)) <= {"pause_closed", "offer_logged", "fact_set", "meta_set"}


def test_change_asks_how_then_the_new_way_is_offered(tmp_path: Path) -> None:
    """P-057: Change approach re-showed the same beat ("offers three coins") with new odds and never asked how.
    It now asks; the player's words are the new declaration, framed on their own."""
    from engine.resolve.pipeline import CHANGE_ASK

    dock, ctx, model, res = offer_turn(tmp_path, **RISKY)
    assert res.pause is not None
    res2 = answer_pause(ctx, "change")
    assert res2.pause is not None and res2.pause.kind == "offer" and res2.offer["stakes"] == "risky"
    assert {"kind": "NOTE", "text": CHANGE_ASK} in res2.oof
    assert not rolls(dock.store) and sum(1 for r, _ in model.calls if r == Role.FRAMER) == 1
    # "change approach: I talk my way past instead" carries the new way: it is framed, not the old beat
    talk = beat("talk my way past the watch", "verb.talk", target="npc.sela_vey", verbs=("persuade",))
    data = {"parts": [{"text": "change approach: I talk my way past instead", "class": "PENDING_ANSWER", "question_kind": "none", "topic": None}],
            "pending_answer": "change", "fact_questions": [], "beats": [talk], "clarifying_question": None,
            "restatement": "Wren talks her way past the watch", "player_quantity": None}
    model.push(Role.READER, lambda schema, packet: prune(data, schema))
    model.push(Role.FRAMER, framer(obstacle={"kind": "opposed", "obstacle_class": None, "tier": None,
                                             "entity": "npc.sela_vey"}))  # talk to a person: her defense (01.6.4)
    res3 = run_turn(ctx, "change approach: I talk my way past instead")
    assert res3.pause is not None and res3.pause.kind == "offer"
    assert res3.pause.detail["plan"]["beat"]["intent"] == "talk my way past the watch"
    assert not rolls(dock.store) and sum(1 for r, _ in model.calls if r == Role.FRAMER) == 2


def test_restrained_redirect_names_the_way_out_and_breaking_free_clears_it(tmp_path: Path) -> None:
    """Fighter playtest 181737 inputs 20-31: Restrained refused every Move with "1 prevents it right now", twice per
    reply, and nothing could end it. The block names the condition and its cleanse; a won Grapple ends it."""
    from engine.store.conditions import apply_condition

    climb = beat("climb onto the well rim", "verb.move", verbs=("climb",))
    leap = beat("leap after the face", "verb.move", verbs=("chase",))
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I climb the rim and leap after it.", climb, leap)],
                           Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    with dock.store.transaction() as tx:
        tx.add_all(apply_condition(tx.state, tx.mint, dock.rules, dock.pc, "cond.restrained").events)
    from engine.dm.narration import turn_blocks

    res = run_turn(ctx, "I climb the rim and leap after it.")
    blocks, _ = turn_blocks(ctx, res.oof, res.record, None)
    red = [b.text for b in blocks if b.kind == "REDIRECT"]
    assert len(red) == 1, red  # two beats refused for the same reason: one block
    assert red[0].startswith("[REDIRECT] Not as tried: you are restrained right now, and that stops it; clear it")
    assert "- Break free (one action; a Grapple roll)" in red[0]
    free = beat("break free of the hold", "verb.grapple", verbs=("escape",), against_will=True)
    model.push(Role.READER, reader("DECLARATION", "I break free.", free))
    model.push(Role.FRAMER, framer())
    model.push(Role.WORLD, QUIET_WORLD)
    res2 = run_turn(ctx, "I break free.")
    assert res2.pause is not None and res2.pause.kind == "offer"
    ctx.rng.faces = [20]  # type: ignore[attr-defined]
    answer_pause(ctx, "commit")
    assert not [c for c in dock.state.conditions.values() if c.condition_id == "cond.restrained"]


def test_a_reframe_that_moves_the_odds_says_why(tmp_path: Path) -> None:
    from engine.resolve.pipeline import reframe_note
    from engine.resolve.types import Frame

    dock, ctx, model, res = offer_turn(tmp_path, **RISKY)
    old = Frame.model_validate(res.pause.detail["frame"])
    assert reframe_note(old, old, dock.rules) is None
    new = old.model_copy(update={"attribute": "intellect",
                                 "modifier": old.modifier.model_copy(update={"attribute": old.modifier.attribute - 1}),
                                 "odds": old.odds.model_copy(update={"success_or_better": 40})})
    note = reframe_note(old, new, dock.rules)
    assert note is not None and note.startswith(f"The odds moved from {old.odds.success_or_better}% to 40%: ")
    assert "uses Intellect" in note and "instead of" in note


def test_go_big_reframes_once(tmp_path: Path) -> None:
    dock, ctx, model, res = offer_turn(tmp_path, **RISKY)
    assert res.pause is not None and "go_big" in [c["id"] for c in res.pause.choices]
    res2 = answer_pause(ctx, "go_big")
    assert res2.offer is not None and res2.offer["stakes"] == "dire" and res2.offer["trades"] == []


def test_go_big_from_safe_keeps_an_offer(tmp_path: Path) -> None:
    """Fighter playtest inputs 19/23: Go big from Safe had no alternate cost, frame_check refused, the OFFER was
    lost ("You cannot do it that way"). The trade now takes the first fitting alternate, or the offer stands."""
    dock, ctx, model, res = offer_turn(tmp_path)
    assert res.offer is not None and res.offer["stakes"] == "safe"
    res2 = answer_pause(ctx, "go_big")
    assert res2.pause is not None and res2.pause.kind == "offer"
    assert res2.offer is not None and res2.offer["stakes"] == "risky" and res2.offer["alternate_cost"]


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
    assert any(o["kind"] == "OFFER" and o["text"].startswith("[OFFER — auto]") for o in res.oof)


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
    with dock.store.transaction() as tx:  # 01.6.11: harm from an aware party cites that they are armed and hostile
        knife = tx.mint("fact")
        tx.add(Event.of("fact_set", {"source": "oracle"}, source="dm", rule_id="01.15.5", fact_id=knife,
                        subject="foe.cutthroat", predicate="wields", value="a knife", visibility="shown"))
    lethal = {"stakes_source": "aware_opponent_or_observer", "stakes_heavy": True, "lethal": True,
              "obstacle": {"kind": "entity_defense", "obstacle_class": None, "tier": None, "entity": "foe.cutthroat"},
              "threatened_cost": {"menu_id": "cost.harm", "form_intent": "his knife", "source_fact": knife},
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
    fly = beat("spring the harbour master's strongbox with arcane force", "verb.handle", uses_power=True,
               verbs=("open",))
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
    walk = beat("walk across the water to the far shore", "verb.move", g4_fact=ferry)
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
    talk = beat("ask the ferryman the fare", "verb.talk", target="npc.tam_harlan")
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I ask the ferryman the fare.", talk, qk="what_like"),
                                         reader("SPEECH", '"Evening."')]})
    dock, ctx = setup(tmp_path, model)
    b = run_turn(ctx, "I ask the ferryman the fare.")  # a first question to a stranger: certain (T-15-3)
    a = run_turn(ctx, '"Evening."')
    assert not a.record.beats and a.record.parts[0].handled == "answered"
    assert b.record.beats[0].gate_words == "no roll: trivial" and not b.record.beats[0].rolled  # certain (15.3.10)
    assert Role.FRAMER not in [r for r, _ in model.calls]  # a certain beat skips the Framer
    assert not rolls(dock.store) and not dock.state.frames
    assert a.record.npc_actions  # spoken to the room: the first present NPC answers (12.11.9 default layer)


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


@pytest.mark.parametrize("method", ["press Sela gently to say what she is watching",
                                    "threaten Sela until she says what she is watching"])
def test_talk_is_never_redirected(tmp_path: Path, method: str) -> None:
    """Playtest 20261007-170200: "press him gently" was redirected to Stonesense; P-122 (-212725): a threat was
    redirected to Intimidation. The gate is computed (00.12.3): Talk needs no licence, a knack never gates."""
    talk = beat(method, "verb.talk", target="npc.sela_vey", verbs=("press", "draw out"))
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I press her gently.", talk, qk="what_like")],
                           Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    res = run_turn(ctx, "I press her gently.")
    b = res.record.beats[0]
    assert b.gate == "G1" and not any(o["kind"] == "REDIRECT" for o in res.oof) and res.pause is None
    assert "ruling_logged" not in types(dock.store, res.turn_id)  # no g3_redirect ruling


def test_move_toward_someone_writes_the_band(tmp_path: Path) -> None:
    """Playtest 20261007-170200 turns 5/6/12: a declared, resolved Move wrote no position, so every arrival in
    the narration was cut as unsourced. PR-06-4: the band closes one step, written both ways."""
    walk = beat("walk out along the quay toward the watchwoman", "verb.move", target="npc.sela_vey",
                verbs=("approach",))
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I walk over to her.", walk),
                                         reader("DECLARATION", "I go closer.", walk)],
                           Role.WORLD: [QUIET_WORLD, QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    res = run_turn(ctx, "I walk over to her.")
    b = res.record.beats[0]
    assert b.positions and b.positions[0].entity == dock.pc and "Sela Vey" in b.positions[0].words
    st = dock.state
    assert st.positions[dock.pc].band_to[dock.watch] == "close" == st.positions[dock.watch].band_to[dock.pc]
    assert st.positions[dock.pc].location == dock.place
    assert res.record.writes_for(dock.pc, "position_set")
    run_turn(ctx, "I go closer.")  # never engaged without an engagement link (06.3.5)
    assert dock.state.positions[dock.pc].band_to[dock.watch] == "close"


def test_move_to_an_object_reads_plainly_and_reader_notes_stay_out(tmp_path: Path) -> None:
    """P-108 (playtest 20261007-201412 talker, input 26): "You are a few strides from bench" and the Reader's own
    note "Spoken to Oggza, not a beat: ..." reached the player. The object keeps its article; the note is not
    the beat's line."""
    sit = beat("sit on the bench", "verb.move", target="obj.bench", verbs=("sit",))
    said = "I sit on the bench. \"Who are you?\""

    def read(schema: dict[str, Any], packet: Any) -> dict[str, Any]:
        data = {"parts": [{"text": "I sit on the bench.", "class": "DECLARATION", "question_kind": "none", "topic": None},
                          {"text": "\"Who are you?\"", "class": "SPEECH", "question_kind": "none", "topic": None}], "pending_answer": None,
                "fact_questions": [], "beats": [sit], "clarifying_question": None, "player_quantity": None,
                "restatement": "Wren sits on the bench. Spoken to Sela, not a beat: she asks who Sela is."}
        return prune(data, schema)

    model = ScriptedModel({Role.READER: [read], Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    with dock.store.transaction() as tx:
        tx.add(Event.of("entity_created", source="test", entity=EntityRecord(id="obj.bench", kind="object",
                                                                             name="bench")))
        tx.add(Event.of("position_set", source="test", rule_id="10.1.1", entity="obj.bench", location=dock.place))
    b = run_turn(ctx, said).record.beats[0]
    assert b.restatement == "Wren sits on the bench."
    assert [p.words for p in b.positions] == ["a few strides from the bench"], b


def test_move_to_another_place_cuts_the_scene_there(tmp_path: Path) -> None:
    """12.4.2 (2) / 10.1.3: a resolved Move to a reachable place is travel: the scene ends and the next one
    opens there, with the PC's position written."""
    from engine.store.events import EntityRecord as Rec
    model = ScriptedModel()
    dock, ctx = setup(tmp_path, model)
    with dock.store.transaction() as tx:
        office = "loc.the_ferry_office"
        tx.add(Event.of("entity_created", source="test", entity=Rec(
            id=office, kind="place", name="The Ferry Office", data={"place_kind": "building", "parent": dock.place})))
    go = beat("go into the ferry office", "verb.move", target=office, verbs=("go",))
    model.push(Role.READER, reader("DECLARATION", "I go into the office.", go))
    model.push(Role.WORLD, QUIET_WORLD)
    from tests.engine.test_director import answer
    model.push(Role.DIRECTOR, answer(dock.place))  # the Director did not cut: the place change does
    res = run_turn(ctx, "I go into the office.")
    st = dock.state
    assert st.positions[dock.pc].location == office
    assert st.scene is not None and st.scene.place_id == office and res.record.scene.cut


# ------------------------------------------------------------------------------------------- "what do I know?"


@pytest.mark.parametrize("cls", ["FICTION_QUESTION", "DECLARATION"])
def test_what_do_i_know_is_answered_plainly_never_rolled(tmp_path: Path, cls: str) -> None:
    # 14.6.3 / 12.10.5: whatever the Reader called it, the journal answers, out of fiction; no Recall roll, no
    # Oracle draw about the PC's own memory
    text = "And what do I know about the ferryman so far?"
    recall = beat("remember what Wren knows of the ferryman", "verb.recall")
    ask = {"subject": "pc.wren", "predicate": "Wren knows anything of the ferryman", "odds_rung": "unlikely"}
    model = ScriptedModel({Role.READER: [reader(cls, text, recall, questions=(ask,))], Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    res = run_turn(ctx, text)
    assert [p.cls for p in res.record.parts] == ["OOF_QUESTION"]
    assert res.pause is None and not res.record.beats and not res.record.oracle
    assert "oracle_answered" not in types(dock.store, res.turn_id)
    note = next(o["text"] for o in res.oof if o["text"].startswith("[JOURNAL]"))
    assert note.startswith("[JOURNAL] What you know about the ferryman:") and "Tam Harlan" in note
    assert "silver" not in note and "tide" not in note  # his sealed wants


def test_trying_to_remember_stays_in_fiction(tmp_path: Path) -> None:
    text = "I try to remember what I know about the ferryman."
    recall = beat("remember what Wren knows of the ferryman", "verb.recall")
    model = ScriptedModel({Role.READER: [reader("DECLARATION", text, recall)], Role.FRAMER: [framer()],
                           Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    res = run_turn(ctx, text)
    assert [p.cls for p in res.record.parts] == ["DECLARATION"]
    assert not any(o["text"].startswith("[JOURNAL]") for o in res.oof)
    assert res.pause is not None or res.record.beats


def test_nothing_known_says_so_and_how_to_find_out(tmp_path: Path) -> None:
    text = "what do I know about the dragon?"
    model = ScriptedModel({Role.READER: [reader("FICTION_QUESTION", text)], Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    note = " ".join(o["text"] for o in run_turn(ctx, text).oof)
    assert "Nothing on record about the dragon" in note and "ask someone" in note and "remember" in note


def test_one_beat_offers_only_its_own_line_not_the_queued_tail() -> None:
    """P-064: "a bribe and a question" read as one roll because the single beat took the whole restatement."""
    from engine.dm.roles.reader import ReaderBeat, ReaderResult

    res = ReaderResult(beats=[ReaderBeat(intent="the children say what is below", method="holds up a copper",
                                         verb="verb.talk")],
                       restatement="Lisius holds up a copper for whoever tells him. Then, asked aloud: what the "
                                   "children know about Falwen (no beat).")
    n = iter(range(9))
    [plan] = res.plans(actor="pc.x", declared_seq=0, mint=lambda p: f"{p}.{next(n)}")
    assert plan.beat.restatement == "Lisius holds up a copper for whoever tells him."


# ------------------------------------------------------------------------------------------- extended goals (P-082)


def _track(tmp_path: Path, *shapes: str, reach_whole: bool = True) -> tuple[DockScene, TurnContext, list[Any]]:
    """Fighter playtest 20261007-191941 inputs 22-31: follow a track again and again; each success got the same
    "the mist hides it, press on?". Each turn: declare, commit, a success on the die."""
    model = ScriptedModel()
    dock, ctx = setup(tmp_path, model)
    with dock.store.transaction() as tx:
        for oid, name in (("obj.track", "track"), ("obj.track_in_the_mud", "track in the mud")):
            tx.add(Event.of("entity_created", source="test", entity=EntityRecord(id=oid, kind="object", name=name)))
            tx.add(Event.of("position_set", source="test", entity=oid, location=dock.place))
    out = []
    for i, shape in enumerate(shapes):
        follow = beat("follow the track", "verb.move", target="obj.track_in_the_mud" if i == 0 else "obj.track",
                      verbs=("follow",), shape="now" if shape == "single" else shape)
        model.push(Role.READER, reader("DECLARATION", "I follow the track.", follow))
        model.push(Role.FRAMER, framer(stakes_source="none", reach_whole=reach_whole))
        model.push(Role.WORLD, QUIET_WORLD, QUIET_WORLD)
        run_turn(ctx, "I follow the track.")
        ctx.rng.faces = [18]  # type: ignore[attr-defined]
        out.append(answer_pause(ctx, "commit").record.beats[0])
    return dock, ctx, out


def test_an_extended_goal_shows_progress_each_stretch(tmp_path: Path) -> None:
    dock, ctx, (b1, b2) = _track(tmp_path, "extended", "single", reach_whole=False)  # limited: 1 tick each
    assert "a first stretch" in b1.progress and "never the same view" in b1.progress
    assert "more than halfway" in b2.progress  # the same goal, though the Reader said single
    [clock] = [c for c in dock.state.clocks.values() if c.kind == "progress"]
    assert clock.filled == 2 and clock.segments == 4 and clock.status == "active"


def test_repeated_successes_at_one_goal_end_in_arrival(tmp_path: Path) -> None:
    from engine.world.common import trigger_raised
    dock, ctx, (b1, b2) = _track(tmp_path, "single", "single")  # standard: 2 ticks each, the first counted late
    assert not b1.progress
    assert b2.progress.startswith("goal reached") and "do not ask whether to press on" in b2.progress
    [clock] = [c for c in dock.state.clocks.values() if c.kind == "progress"]
    assert clock.status == "completed"
    # what lies at the end is a lead from state (12.8.2): delivered by the Director's step, or still owed
    assert dock.state.meta.get("lead_injection") or trigger_raised(dock.state, "trg.lead_injection")


def test_go_big_from_safe_takes_the_framers_fitted_alternate(tmp_path: Path) -> None:
    """P-083: going big from Safe printed the menu's example list ("left on the far side, down the well, stuck in
    a beam") in a grassy field. The Framer names the alternate a go-big adds; a safe offer does not show it."""
    alt = {"menu_id": "cost.exposure", "form_intent": "the watch looks up at the splash", "source_fact": None}
    dock, ctx, model, res = offer_turn(tmp_path, alternate_cost=alt)
    assert res.offer is not None and res.offer["stakes"] == "safe" and not res.offer["alternate_cost"]
    res2 = answer_pause(ctx, "go_big")
    assert res2.offer is not None and res2.offer["alternate_cost"]["form"] == alt["form_intent"]


def test_a_form_that_only_copies_the_menu_examples_is_dropped(tmp_path: Path) -> None:
    from engine.resolve.frame import _fitted
    from engine.resolve.types import CostDecl
    dock = build_dock(tmp_path)
    copied = CostDecl(menu_id="cost.gear", form_intent="Left on the far side, down the well, stuck in a beam.")
    assert _fitted(copied, dock.rules).form_intent == ""
    own = CostDecl(menu_id="cost.gear", form_intent="the mace lost in the long grass")
    assert _fitted(own, dock.rules).form_intent == own.form_intent



STAB = beat("stab the watchwoman with a dagger", "verb.strike", target="npc.sela_vey", verbs=("stab",),
            against_will=True)
MELEE = {"traits": ["trait.action.attack", "trait.delivery.melee"], "stakes_source": "aware_opponent_or_observer",
         "stakes_heavy": True, "obstacle": {"kind": "opposed", "obstacle_class": None, "tier": None,
                                            "entity": "npc.sela_vey"},
         "threatened_cost": {"menu_id": "cost.footing", "form_intent": "her answering blow", "source_fact": None},
         "alternate_cost": {"menu_id": "cost.exposure", "form_intent": "the quay sees it", "source_fact": None}}


def test_strikes_never_ride_close_to_engaged_and_a_hurt_pc_sees_it(tmp_path: Path) -> None:
    """Playtest 20261007-195734 (fighter): after one hit, three later lunges rode as "it works" with no OFFER
    (P-100); no strike wrote a band, so every closing step was cut (P-099); a critical failure's harm showed no
    Vitality change and "how hurt am I?" got the generic help (P-101)."""
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I stab her.", STAB)],
                           Role.FRAMER: [framer(**MELEE)], Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    with dock.store.transaction() as tx:  # 01.6.11: her blow is a cost because she is armed (a cited fact)
        armed = tx.mint("fact")
        tx.add(Event.of("fact_set", {"source": "oracle"}, source="dm", rule_id="01.15.5", fact_id=armed,
                        subject=dock.watch, predicate="wields", value="a short spear", visibility="shown"))
    harm = {**MELEE, "threatened_cost": {"menu_id": "cost.harm", "form_intent": "her answering blow",
                                         "source_fact": armed}}
    assert run_turn(ctx, "I stab her.").pause is not None
    model.push(Role.WORLD, QUIET_WORLD)
    ctx.rng.faces = [19]  # type: ignore[attr-defined]
    res = answer_pause(ctx, "commit")
    b = res.record.beats[0]
    assert b.degree in ("success", "critical_success") and b.positions and "Sela Vey" in b.positions[0].words
    st = dock.state
    assert st.positions[dock.pc].band_to[dock.watch] == "engaged" == st.positions[dock.watch].band_to[dock.pc]
    # the same strike again: an attack rolls each time (06.1.6), so the OFFER is shown again
    model.push(Role.READER, reader("DECLARATION", "I stab her again.", STAB))
    model.push(Role.FRAMER, framer(**harm))
    res2 = run_turn(ctx, "I stab her again.")
    assert res2.pause is not None and res2.pause.kind == "offer" and any(o["kind"] == "OFFER" for o in res2.oof)
    model.push(Role.WORLD, QUIET_WORLD)
    ctx.rng.faces = [1]  # type: ignore[attr-defined]
    res3 = answer_pause(ctx, "commit")
    assert res3.record.beats[0].degree == "critical_failure"
    result = next(o["text"] for o in res3.oof if o["kind"] == "RESULT")
    assert "Changed: Vitality " in result, result
    # "what are my options?" read as a fiction question, "how hurt am I?" as OOF: both answered
    data = {"parts": [{"text": "What are my options?", "class": "FICTION_QUESTION", "question_kind": "none", "topic": None},
                      {"text": "And how hurt am I right now?", "class": "OOF_QUESTION", "question_kind": "none", "topic": None}],
            "pending_answer": None, "fact_questions": [], "beats": [], "clarifying_question": None,
            "restatement": "", "player_quantity": None}
    model.push(Role.READER, lambda schema, packet: prune(data, schema))
    model.push(Role.WORLD, QUIET_WORLD)
    res4 = run_turn(ctx, "What are my options? And how hurt am I right now?")
    notes = " ".join(o["text"] for o in res4.oof if o["kind"] == "NOTE")
    assert "Vitality " in notes and "[LEADS]" in notes, notes


def test_a_shove_that_lands_drives_the_target_back_a_band(tmp_path: Path) -> None:
    """06.5.3: a Force at reach 2 pushes the target one band away and breaks the engagement (P-099)."""
    shove = beat("shove the watchwoman back off the quay edge", "verb.force", target="npc.sela_vey",
                 verbs=("shove",), against_will=True)
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I shove her back.", shove)],
                           Role.FRAMER: [framer(**{**MELEE, "traits": ["trait.delivery.melee"]})],
                           Role.WORLD: [QUIET_WORLD, QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    run_turn(ctx, "I shove her back.")
    ctx.rng.faces = [17]  # type: ignore[attr-defined]
    res = answer_pause(ctx, "commit")
    b = res.record.beats[0]
    assert b.degree == "success" and b.reach == "standard" and b.positions[0].entity == dock.watch
    st = dock.state
    assert st.positions[dock.pc].band_to[dock.watch] == "close" == st.positions[dock.watch].band_to[dock.pc]


def test_a_strike_that_lands_hurts_the_target_starts_the_fight_and_the_foe_answers(tmp_path: Path) -> None:
    """Playtest 20261007-195734 (fighter), I-154 (a)(b): a successful lunge left Taman unhurt and no conflict
    ever started. 06.2.1: the committed attack starts conflict mode and seeds the band; 06.4.3: a landed dagger
    Strike deals S2 to the target, shown in words; 06.9.2: the foe answers by its behavior row."""
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I stab her.", STAB)],
                           Role.FRAMER: [framer(**MELEE)], Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    run_turn(ctx, "I stab her.")
    st = dock.state
    assert str(st.time.mode) != "conflict"  # an OFFER is not yet an attack
    model.push(Role.WORLD, QUIET_WORLD)
    ctx.rng.faces = [17]  # type: ignore[attr-defined]
    res = answer_pause(ctx, "commit")
    b = res.record.beats[0]
    assert b.degree == "success" and b.reach == "standard"
    assert str(st.time.mode) == "conflict" and "conflict_start" in st.time.last_boundary
    assert st.quantities[dock.watch]["vitality"].current == 2  # T-09-3 band 1: 5, less a light blade's S2 (3)
    assert b.harm and b.harm[0].target == dock.watch and b.harm[0].words == "bloodied"
    result = next(o["text"] for o in res.oof if o["kind"] == "RESULT")
    assert "Sela Vey bloodied" in result and "→ 2" not in result, result
    assert any(a.npc == dock.watch and a.source == "behavior" for a in res.record.npc_actions)
    # the second blow drops her: a walk-on struck to 0 is dead (07.2.10), and the fight is over (06.13.1)
    model.push(Role.READER, reader("DECLARATION", "I stab her again.", STAB))
    model.push(Role.FRAMER, framer(**MELEE))
    run_turn(ctx, "I stab her again.")
    model.push(Role.WORLD, QUIET_WORLD)
    ctx.rng.faces = [17]  # type: ignore[attr-defined]
    res2 = answer_pause(ctx, "commit")
    assert res2.record.beats[0].harm[0].words == "dead"
    assert st.fact_value(dock.watch, "defeated") == {"manner": "dead"}
    assert str(st.time.mode) != "conflict" and "conflict_end" in st.time.last_boundary
    assert not any(a.npc == dock.watch and a.source == "behavior" for a in res2.record.npc_actions)


def test_a_fight_seeds_bands_and_a_foe_closes_before_it_strikes(tmp_path: Path) -> None:
    """PR-06-1 step 2 / 06.3.9: a foe with no established band starts `near`; its default melee row (06.9.4)
    moves it toward the PC before it can strike."""
    from engine.resolve.conflict import foe_beat, start

    dock, ctx = setup(tmp_path, ScriptedModel({}))
    with dock.store.transaction("t.fight") as tx:
        ctx.tx = tx
        assert start(ctx.time_ctx(), dock.pc, [dock.watch], "test")
        st = tx.state
        assert str(st.time.mode) == "conflict"
        assert st.positions[dock.pc].band_to[dock.watch] == "near" == st.positions[dock.watch].band_to[dock.pc]
        assert foe_beat(ctx.time_ctx(), ctx.rng, dock.watch, dock.pc)[0] == "moves toward you"
        assert st.positions[dock.watch].band_to[dock.pc] == "close"
        said, _ = foe_beat(ctx.time_ctx(), ctx.rng, dock.watch, dock.pc)
        assert said.startswith("closes in") and st.positions[dock.pc].band_to[dock.watch] == "engaged"
        ctx.tx = None
