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
         license: str = "none", g4_fact: str | None = None, verbs: tuple[str, ...] = (),
         would_be: str = "none") -> dict[str, Any]:
    return {"intent": intent, "method": intent, "assertion": None, "shape": "single", "target": target, "verb": verb,
            "license": license, "would_be_license": would_be, "gate": gate, "g4_fact": g4_fact, "necessity": necessity,
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
    # P-012: the committed roll states its outcome once (12.15.3)
    result = [o["text"] for o in res2.oof if o["kind"] == "RESULT"]
    assert len(result) == 1 and result[0].startswith("[RESULT] d20 18 → ") and result[0].endswith("· success")
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
    data = {"parts": [{"text": "change approach: I talk my way past instead", "class": "PENDING_ANSWER"}],
            "pending_answer": "change", "fact_questions": [], "beats": [talk], "clarifying_question": None,
            "restatement": "Wren talks her way past the watch", "player_quantity": None}
    model.push(Role.READER, lambda schema, packet: prune(data, schema))
    model.push(Role.FRAMER, framer())
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
    free = beat("break free of the hold", "verb.grapple", verbs=("escape",))
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
               verbs=("pick",), would_be="lic.training.arcane_alteration")
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


def test_talk_proposed_as_g3_without_a_licence_is_never_redirected(tmp_path: Path) -> None:
    """Playtest 20261007-170200: "talk to the person on the bridge" / "press him gently" came back G3 with
    verb.talk and no licence, and the gate's word match redirected them to Stonesense. Talk needs no licence."""
    talk = beat("press Sela gently to say what she is watching", "verb.talk", gate="G3", target="npc.sela_vey",
                necessity="take_the_time", verbs=("press", "draw out"))
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I press her gently.", talk)],
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
                necessity="trivial", verbs=("approach",))
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
    go = beat("go into the ferry office", "verb.move", target=office, necessity="trivial", verbs=("go",))
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
    recall = beat("remember what Wren knows of the ferryman", "verb.recall", gate="G3")
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
    recall = beat("remember what Wren knows of the ferryman", "verb.recall", gate="G1")
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
