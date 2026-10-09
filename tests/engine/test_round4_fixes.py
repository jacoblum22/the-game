"""Spec 018: the round-4 engine fixes (DL-12-96..100, DL-01-36), mostly replayed from the two 20261008 saves.

The fixtures are those saves truncated before the turn under test (`tests/fixtures/*_turnN.db.gz`); they keep the
Reader's and Framer's own answers for the later turns, so the replay runs Haiku's readings through the new code."""

from __future__ import annotations

import gzip
import json
import shutil
import sqlite3
from pathlib import Path
from typing import Any

from engine.audit.declare import Sentence, pc_quotes
from engine.audit.text import covers
from engine.data.loader import load_rules
from engine.dm.context import TurnContext
from engine.dm.turn import play_answer, play_turn, run_turn
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.resolve.change import apply_change, plain
from engine.resolve.types import Beat, Change
from engine.store.db import Store
from tests.engine.test_turn_adjudication import D20, QUIET_WORLD, beat, reader, setup

FIXTURES = Path(__file__).parents[1] / "fixtures"


def _open(tmp_path: Path, name: str) -> tuple[Store, dict[str, dict[str, list[Any]]]]:
    """The truncated save, and the recorded reader/framer answers by turn id."""
    path = tmp_path / name.replace(".gz", "")
    with gzip.open(FIXTURES / name, "rb") as src, path.open("wb") as dst:
        shutil.copyfileobj(src, dst)
    con = sqlite3.connect(path)
    said: dict[str, dict[str, list[Any]]] = {}
    for tid, role, resp in con.execute("select turn_id, role, response from model_calls order by row_id"):
        data = json.loads(resp)["data"]
        for b in data.get("beats", []) if role == "reader" else ():
            b["change"].setdefault("description", None)  # the slot spec 018 added (null: an id fits, or none)
            b.setdefault("how", None)  # the method words spec 020 added (null: none verbatim)
        said.setdefault(tid, {}).setdefault(role, []).append(data)
    con.close()
    return Store.open(path), said


def _ctx(store: Store, model: Any, faces: list[int] = ()) -> TurnContext:  # type: ignore[assignment]
    rng = D20.of(store)
    rng.faces = list(faces)
    return TurnContext(store=store, rules=load_rules(), rng=rng, model=model, config={"auto_commit": False})


def _play(ctx: TurnContext, text: str) -> Any:
    """One message narrated, its OFFERs committed and its plan gone on with (spec 017's "Still go on to …?", asked
    when speech said here waits on a later move away); the first adjudication result with every beat it led to."""
    first = out = play_turn(ctx, text).adjudication
    while out.pause is not None and out.pause.kind == "offer":
        out = play_answer(ctx, "continue" if out.pause.detail.get("stage") == "plan" else "commit").adjudication
        first.record.beats += [b for b in out.record.beats if b not in first.record.beats]
    return first


def _narrator_packets(model: ScriptedModel) -> list[str]:
    return [p.message for r, p in model.calls if r == Role.NARRATOR]


def test_the_fighters_walking_in_place_is_one_approach_and_the_refugees_can_be_persuaded(tmp_path: Path) -> None:
    """Playtest 20261008-192946, inputs 20-22 (turns 5-7), after input 19's travel into Saltton: "toward the voices"
    twice (each "a few strides short" of the lane), then a Move to Saltton while in Saltton ("still in"), then
    "persuade the refugees" with no one named (a critical success: "no one named to persuade"). Now: the first
    approach ends beside the lane, the second stays beside it, the Move to here is a look with no roll, and the
    persuade on the description "the refugees" applies (DL-12-97, DL-12-98)."""
    store, said = _open(tmp_path, "fighter_lane_turn5.db.gz")
    r7 = json.loads(json.dumps(said["turn.7"]["reader"][0]))
    r7["beats"][1]["change"]["description"] = "the refugees"  # the new slot the Reader fills when no id fits
    framers = [*said["turn.5"]["framer"], *said["turn.6"]["framer"],
               said["turn.7"]["framer"][1]]  # turn 7's Move framer is never asked now: a look needs no frame
    model = ScriptedModel({Role.READER: [said[f"turn.{n}"]["reader"][0] for n in (5, 6)] + [r7],
                           Role.FRAMER: framers})
    ctx = _ctx(store, model, faces=[15])
    texts = ["I stride around the corner toward the voices, hand on my sword, ready for trouble.",
             "I step into the narrow lane and walk toward the voices, drawing my sword halfway.",
             "I round the bend and step out with my sword fully drawn, calling out to the refugees to show "
             "themselves."]
    outs = [_play(ctx, t) for t in texts]
    pc = outs[0].record.pc
    lane = "obj.narrow_lane_between_two_houses"
    # turns 5-6: one approach, ending beside the lane; never "a few strides" (T-12-11 "close")
    words = [p.words for o in outs[:2] for b in o.record.beats for p in b.positions]
    assert words[0] == "beside the narrow lane between two houses" and not any("strides" in w for w in words)
    assert str(store.state.positions[pc].band_to[lane]).removeprefix("band.") == "engaged"
    assert all(b.gate_words.startswith("no roll") for o in outs[:2] for b in o.record.beats if b.verb == "verb.move")
    # turn 7: the Move to the place here is a look (no roll, no "still in"); the persuade lands on the description
    look, ask = outs[2].record.beats[0], outs[2].record.beats[-1]  # the persuade as resolved after its OFFER
    assert look.gate_words == "no roll: trivial" and not look.positions
    assert ask.degree in ("success", "critical_success") and not ask.change_refused
    # the frame's reach is limited ("partly what you wanted", as in the run): a smaller part, still applied
    assert ask.changed == "Agreed by the refugees: a smaller part of it (the refugees come out and show themselves)"
    place = str(store.state.scene.place_id)  # type: ignore[union-attr]
    assert str(store.state.fact_value(place, "agreed.the_refugees")).startswith("the refugees: a smaller part")
    # setting once (DL-12-99): the later turns of the scene carry the "already described" line, not the look again
    drafts = [p for p in _narrator_packets(model) if "SCENE SETTING" in p]  # repairs carry no setting
    assert len(drafts) >= 3 and all("already described this scene" in p and "- look:" not in p for p in drafts)


def test_a_redundant_persuade_is_certain_and_the_result_reads_plainly(tmp_path: Path) -> None:
    """Playtest 20261008-192926, input 20 (turn 5): "Tell them I'm good with locks..." after Ivas had agreed to carry
    Wila's word (fact.113): a 60% OFFER that could make her take offence. Haiku put the PC in `what`, so the result
    read "You agrees to Ivas carries word...". Now: no roll, no OFFER, the record says it is already agreed
    (DL-01-36), and the plain words never make the PC the persuaded one. The message's second beat walks to the
    Sleeping Goose: travel, so the narration frames the arrival (P-098)."""
    store, said = _open(tmp_path, "talker_ivas_turn5.db.gz")
    model = ScriptedModel({Role.READER: said["turn.5"]["reader"]})
    ctx = _ctx(store, model, faces=[15])
    res = _play(ctx, "Nothing more for now. Tell them I'm good with locks and quiet work. Then I head to the "
                     "Sleeping Goose to talk to the carters.")
    ask = next(b for b in res.record.beats if b.change_kind == "persuade_to")
    assert ask.gate_words == "no roll: trivial" and ask.degree is None
    assert ask.changed.startswith("Agreed already by Ivas Terier: Ivas carries Wila's word")
    assert ask.change == "Persuading: Ivas Terier"  # was "Persuading: you"
    assert not any(o.get("kind") == "OFFER" and "Persuading" in o.get("text", "") for o in res.oof)
    # the walk to the inn is travel: the scene changes and the narration frames the arrival (12.4.3; P-098)
    assert store.state.scene is not None and store.state.scene.place_id == "loc.long_reach_sandburn.inn"
    draft = next(p for p in _narrator_packets(model) if "then frame the new scene it reaches" in p)  # not a repair
    assert "SCENE SETTING (what the character sees" in draft and "frame it as the arrival the beats above led to" in draft
    # setting once (DL-12-99): two more turns at the inn; its look line reached the narrator once, on arrival
    for text in ("I wait by the door and watch the room.", "I listen to the talk at the nearest table."):
        _play(ctx, text)
    drafts = [p for p in _narrator_packets(model) if "SCENE SETTING" in p]
    assert sum("- look:" in p for p in drafts) == 1 and "already described this scene" in drafts[-1]
    # a new request applies on the person, never on the PC, in words with no verb agreement to get wrong
    st = store.state
    pc = res.record.pc
    b = Beat(id="beat.t", actor=pc, intent="Ivas tells the Circle my name tonight", method="ask",
             target="npc.ivas_terier", change=Change(kind="persuade_to", what=pc, whom="npc.ivas_terier"))
    with store.transaction("turn.x") as tx:
        got = apply_change(tx, ctx.rules, b, 2, pc=pc)
    assert got.words == "Agreed by Ivas Terier: Ivas tells the Circle my name tonight"
    assert st.fact_value("npc.ivas_terier", "agreed") == "Ivas tells the Circle my name tonight"
    assert plain(st, b.change, actor=pc, pc=pc) == "Persuading: Ivas Terier"


def test_a_change_with_no_one_named_asks_who_before_framing(tmp_path: Path) -> None:
    """DL-01-36: a persuade with no id, no target and no description is a question, never a roll."""
    talk = beat("get them to open up", "verb.talk", change={"kind": "persuade_to"})
    model = ScriptedModel({Role.READER: [reader("DECLARATION", "I get them to open up.", talk)],
                           Role.WORLD: [QUIET_WORLD]})
    dock, ctx = setup(tmp_path, model)
    res = run_turn(ctx, "I get them to open up.")
    b = res.record.beats[0]
    assert b.gate == "G0" and b.gate_words.startswith("ask the player who they mean") and b.degree is None
    assert res.pause is None and not any(r == Role.FRAMER for r, _ in model.calls)


def test_the_speaker_card_and_speech_line_ask_for_plain_speech() -> None:
    """DL-12-96 / DL-12-100: no prompt line the engine builds asks NPCs to hedge; no self-introduction."""
    import inspect

    from engine.dm import answer, packet
    from engine.dm.roles import narrator

    src = inspect.getsource(packet.speaker_card) + inspect.getsource(narrator._speech_line) + str(answer.WILL_WORDS)
    assert "hedged" not in src and "hearsay or a guess" not in src
    assert "plainly" in inspect.getsource(packet.speaker_card) and "own name or title" in src


def test_pc_words_inside_a_speech_attribution_are_caught() -> None:
    """Playtest 20261008-192926, turn 26: '"Fair enough," you say' inside the carter's line. The sentence's speaker is
    the carter, so the quote beside "you say" was never checked (DL-12-100)."""
    s = Sentence(text='"Ivas Terier would know it, since he\'s the one who brought the word." "Fair enough," '
                              'you say, and the words sit on the board between the cups.', speaker="npc.carter")
    assert pc_quotes(s) == ["Fair enough,"]
    assert not covers("Fair enough,", "Then who would know? Who do the carters sell to?", ratio=0.8)  # → cut
    assert pc_quotes(Sentence(text='"Go on," she says, and you nod.', speaker="npc.carter")) == []
