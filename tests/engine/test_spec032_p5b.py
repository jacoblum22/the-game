"""Spec 032 P5b: records and context (lane C). The DM's `said` list becomes testimony (J), the situation shows what
people carry and who is not here (Q), and the turn record is no longer empty. [spec 033 P4] The log-only checks and
the leak audit left the engine (evals/turn_judge.py measures them); `said` is kept as the DM gave it."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from engine.dm import codex, dm_tools, testimony
from engine.dm.schemas import QUESTION_KINDS
from engine.game import Game
from engine.harm.state import DEAD
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.retrieve.scene import pc_id
from engine.store.views import display_name
from engine.world.common import fact
from engine.world.places import location
from engine.world.scenes import cast_present
from evals.feedback_corpus import CORPUS, open_at
from tests.engine.test_dm_tools import change, in_turn, npc_here, to_play
from tests.engine.test_spec032_cases import RULES
from tests.engine.test_spec032_p3 import run

DM = Role.DM


def passage_of(game: Game, npc: str, words: str) -> str:
    return f'{display_name(game.store.state, npc)} meets your eyes. "{words}" You wait.'


def told(game: Game, entries: list[Any], passage: str, *, clues: list[dict[str, Any]] | None = None,
         setup: Any = None) -> dict[str, Any]:
    """`_told` in one turn (optionally after `setup(ctx, t, tx)`); returns the turn's stats."""
    def go(ctx: Any, t: Any, tx: Any) -> dict[str, Any]:
        if setup:
            setup(ctx, t, tx)
        t.said_raw, t.stats["clues"] = entries, clues or []
        dm_tools._told(ctx, t)
        return t.stats

    return in_turn(game, go)


def records(game: Game) -> list[dict[str, Any]]:
    return testimony.records(game.store.state)


def journal(game: Game) -> str:
    return codex.journal(game.store.state, RULES).text


def play(game: Game, model: ScriptedModel, message: str, data: dict[str, Any]) -> Any:
    """One scripted DM turn through `Game.submit` (queued twice: a world fact re-asks the final passage)."""
    full = {"calls": [], "said": [], "asks": [], **data}
    model.push(DM, full, full)
    try:
        return game.submit(message)
    finally:
        model.queues[DM].clear()


# ------------------------------------------------------------------------------------------- J: told

KIND_MESSAGES = {"none": "I nod and wait.", "who_is": "Who is that by the door?", "where_is": "Where is the smith?",
                 "what_happened": "What happened here last night?", "what_like": "What is the road like?",
                 "what_want": "What do you want from me?", "who_knows": "Who knows about the ford?"}


@pytest.mark.parametrize("kind", QUESTION_KINDS)
def test_j1_j7_each_question_kind_is_filed_as_told(tmp_path: Path, kind: str) -> None:
    game, model = to_play(tmp_path)
    npc, st = npc_here(game), game.store.state
    words = f"The {kind.replace('_', ' ')} answer is that the ford runs shallow after the rain"
    r = play(game, model, KIND_MESSAGES[kind], {"passage": passage_of(game, npc, words),
                                                 "said": [{"npc": npc, "words": words}]})
    rec = records(game)[-1]
    assert (rec["speaker"], rec["words"], rec["place"]) == (npc, words, location(st))
    assert len(rec["day"]) == 3 and rec["settled"] is None and rec["fact"] is None  # testimony, never settled
    assert f'{display_name(game.store.state, npc)} told you: "{words}"' in journal(game)
    assert not any(words in str(f.value) for f in game.store.state.facts.values())  # never a world fact
    tr = game.store.turn(r.turn_id)
    assert tr.said[0]["speaker"] == npc and tr.said[0]["words"] == words  # the turn record is not empty
    assert tr.screen["dm_tools"]["said"][0]["speaker"] == npc and not tr.screen["dm_tools"]["told_dropped"]


@pytest.mark.parametrize("why", ["dead", "absent"])  # [P8a] an unknown speaker is a new walk-on (test_spec032_p8a)
def test_j8_a_speaker_who_is_dead_absent_or_unknown_is_dropped_and_logged(tmp_path: Path, why: str) -> None:
    game, _ = to_play(tmp_path)
    npc, st = npc_here(game), game.store.state
    away = next(i for i, e in st.entities.items() if e.kind == "npc" and i not in cast_present(st))
    who = {"dead": npc, "absent": away}[why]
    words = "I saw the smoke from the hill at dawn."

    def kill(ctx: Any, t: Any, tx: Any) -> None:
        if why == "dead":
            tx.add(fact(tx, npc, "harm_state", DEAD, rule_id="07.1.3"))

    stats = told(game, [{"npc": who, "words": words}], passage_of(game, npc, words), setup=kill)
    assert not records(game) and not stats["said"]
    assert len(stats["told_dropped"]) == 1 and stats["told_dropped"][0]["words"] == words
    assert {"dead": "dead", "absent": "not here"}[why] in stats["told_dropped"][0]["why"]


def test_j9_the_same_line_twice_is_two_records(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    words = "The levee will hold if the rain stops by the new moon."
    told(game, [{"npc": npc, "words": words}, {"npc": npc, "words": words}], passage_of(game, npc, words))
    assert len(records(game)) == 2  # [spec 033 R8] kept as given: no repeat settlement (the DM records facts)
    told(game, [{"npc": npc, "words": words}], passage_of(game, npc, words))  # and again next turn
    assert len(records(game)) == 3


def test_j10_an_omitted_said_writes_nothing_and_breaks_nothing(tmp_path: Path) -> None:
    game, model = to_play(tmp_path)
    r = play(game, model, "I look around.", {"passage": "The room is quiet. What do you do?"})
    assert r.fiction.startswith("The room is quiet") and not records(game)
    stats = game.store.turn(r.turn_id).screen["dm_tools"]
    assert stats["said"] == [] and stats["told_dropped"] == []


def test_j11_the_characters_own_words_are_never_a_told_record(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    pc = pc_id(game.store.state) or ""
    words = "I am only passing through."
    stats = told(game, [{"npc": w, "words": words} for w in (pc, "pc")], f'You say, "{words}"')
    assert not records(game) and not stats["told_dropped"]


def test_only_six_lines_are_read(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    lines = ["The miller grinds barley before dawn", "Rooks nest above the ruined chapel", "Salt arrives by cart each spring",
             "Lanterns hang along the east wall", "Wolves were heard beyond the quarry", "Pilgrims rest near the shrine",
             "Tanners dump their waste upstream"]
    told(game, [{"npc": npc, "words": x} for x in lines], " ".join(f'"{x}"' for x in lines))
    assert len(records(game)) == dm_tools.SAID_MAX


def test_j14_what_do_i_know_about_x_lists_three_told_lines_with_speaker_place_day(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    st = game.store.state
    people = cast_present(st)[:3]
    lines = ["The ford is shallow after the rain", "Nobody crosses the ford at night",
             "The ford keeper left a lantern on the ford"]
    for npc, words in zip(people, lines, strict=False):
        told(game, [{"npc": npc, "words": words}], passage_of(game, npc, words))
    text = codex.what_you_know(game.store.state, "the ford", RULES).text
    for npc, words in zip(people, lines, strict=False):
        assert f'{display_name(game.store.state, npc)} told you: "{words}"' in text
    assert text.count("told you") == len(people) and "day " in text and " at " in text


def test_j12_the_talker_save_lines_reach_the_journal_attributed(tmp_path: Path) -> None:
    """dmtools-152037-talker (turn 10's state): Kazain's and Valas's quoted lines, as the DM would list them."""
    store = open_at(CORPUS / "dmtools-152037-talker.db.gz", "turn.10", tmp_path)
    quotes = {"turn.9": "npc.kazain_ironhelm", "turn.6": "npc.valas_vasande"}
    passages = {t: store.turn(t).delivered_verbatim for t in quotes}  # type: ignore[union-attr]
    path = next(tmp_path.glob("*.db"))
    store.close()
    game, _ = Game.open(path, model=ScriptedModel())
    for turn, npc in quotes.items():
        lines = re.findall(r'"([^"]{25,})"', passages[turn])[:2]
        assert lines
        told(game, [{"npc": npc, "words": x} for x in lines], passages[turn])
    text = journal(game)
    for npc in quotes.values():  # attributed to the name as the character knows it
        assert f'{display_name(game.store.state, npc)} told you: "' in text
    assert len(records(game)) >= 3 and all(r["settled"] is None for r in records(game))


# ------------------------------------------------------------------------------------------- Q: presence


@pytest.mark.parametrize("pronouns", ["she/her", "he/him", "they/them", "it"])
def test_q1_q4_the_card_shows_each_pronoun_set(tmp_path: Path, pronouns: str) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    game.store.state.entities[npc].data["pronouns"] = pronouns
    sit = dm_tools.situation(game.ctx)
    head = next(x for x in sit.splitlines() if x.startswith(f"- {npc}:"))
    assert f"({pronouns}" in head


def test_each_person_here_shows_what_they_carry(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc, st = npc_here(game), game.store.state
    sword = next(i for i, e in st.entities.items() if e.kind == "item" and "sword" in i)
    assert "carries" not in dm_tools.situation(game.ctx).split(f"- {npc}:")[1].split(chr(10) + "- ")[0]
    outs, _ = run(game, change(kind="give_item", what=sword, to=npc))
    assert outs[0].startswith("done"), outs
    block = dm_tools.situation(game.ctx).split(f"- {npc}:")[1].split("\n- ")[0]
    assert "carries: " in block and f"({sword})" in block


def _not_here(game: Game) -> str:
    return next((x for x in dm_tools.situation(game.ctx).splitlines() if x.startswith("Not here:")), "")


@pytest.mark.parametrize("state", ["elsewhere", "dead", "gone", "left_this_turn"])
def test_q5_q8_not_here_lists_met_people_who_are_elsewhere_dead_or_gone(tmp_path: Path, state: str) -> None:
    game, _ = to_play(tmp_path)
    npc, st = npc_here(game), game.store.state
    assert _not_here(game) == "" and npc in dm_tools.situation(game.ctx)
    away = next(i for i, e in st.entities.items() if e.kind == "place" and i != location(st) and ".inn" not in i)
    if state in ("gone", "dead"):
        st.entities[npc].exists = "departed" if state == "gone" else "dead"
    elif state == "elsewhere":
        outs, _ = run(game, change(kind="npc_leaves", who=npc, to=away))
        assert outs[0].startswith("done"), outs
    else:  # inside the same turn that the person leaves
        line = in_turn(game, lambda ctx, t, tx: (dm_tools.tool(ctx, t, change(kind="npc_leaves", who=npc, to=away)),
                                                 dm_tools.situation(ctx))[1])
        assert f"{npc}): " in line.split("Not here:")[1].splitlines()[0]
        return
    line = _not_here(game)
    assert f"({npc}): " in line and line.split(f"({npc}): ")[1].split(";")[0] in (
        ("dead",) if state == "dead" else ("gone",) if state == "gone" else (f"at {display_name(st, away)}",))
    assert f"- {npc}:" not in dm_tools.situation(game.ctx)


def test_q8_a_person_never_met_is_not_listed_and_a_down_person_stays_here(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    st = game.store.state
    met = {c for card in st.scene_cards.values() for c in card.cast}
    stranger = next(i for i, e in st.entities.items() if e.kind == "npc" and i not in met and i not in cast_present(st))
    assert stranger not in dm_tools.situation(game.ctx)
    npc = npc_here(game)
    with game.store.transaction("turn.900") as tx:
        tx.add(fact(tx, npc, "defeated", {"manner": "unconscious"}, rule_id="06.1.1"))
    sit = dm_tools.situation(game.ctx)
    assert f"- {npc}:" in sit and npc not in _not_here(game)


def test_a_body_here_is_shown_as_dead_not_as_a_listener(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    with game.store.transaction("turn.900") as tx:
        tx.add(fact(tx, npc, "harm_state", DEAD, rule_id="07.1.3"))
    assert "  state: dead" in dm_tools.situation(game.ctx).split(f"- {npc}:")[1].split(chr(10) + "- ")[0]


def test_a_hurt_character_is_told_so_in_the_situation(tmp_path: Path) -> None:
    """The traced fighter save: a staggered character was a word inside the sheet line."""
    game, _ = to_play(tmp_path)
    assert "  hurt:" not in dm_tools.situation(game.ctx)
    pc = pc_id(game.store.state) or ""
    game.store.state.quantities[pc]["vitality"].current = 0
    assert "  hurt: staggered (0 Vitality: the next blow wounds)" in dm_tools.situation(game.ctx)


# ------------------------------------------------------------------------------------------- the turn record


def test_the_turn_record_carries_the_told_lines_and_the_passage(tmp_path: Path) -> None:
    game, model = to_play(tmp_path)
    npc, st = npc_here(game), game.store.state
    name = st.entities[npc].name
    words = "The mill wheel stopped at dusk and has not turned since."
    passage = f'{name} folds their arms. "{words}" You wait.'
    r = play(game, model, "What of the mill?", {"passage": passage, "said": [{"npc": npc, "words": words}]})
    tr = game.store.turn(r.turn_id)
    assert r.fiction == passage
    assert [x["words"] for x in tr.said] == [words] and tr.claim_log == []
    assert tr.draft_versions and tr.draft_versions[0]["text"] == passage
    assert "log_only" not in tr.screen["dm_tools"] and "leaks" not in tr.screen["dm_tools"]
