"""Spec 033 P5 (leads, witnesses, retire): cases C6, C7 and C10 of specs/033-dm-states-code-records/cases.md, on the
offline scripted DM. Code tells the DM a lead is due or a clue has too few sources; it never writes the person or the
document. Retiring is the exact command `/retire` or the DM's `end_game`; nothing reads the player's words."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.dm import dm_tools, dm_world
from engine.game import Game, GameConfig
from engine.gen import case
from engine.llm.offline import ScriptedModel
from engine.time import clock
from engine.world import pacing
from engine.world.common import meta, raise_trigger, trigger_raised
from tests.engine.test_dm_tools import DM, change, in_turn, to_play
from tests.engine.test_game import quick_start, seed_oracle
from tests.engine.test_spec032_p3 import roll
from tests.engine.test_spec032_p4 import play, stats_of, step
from tests.engine.test_spec033_p4 import NODE, go, holder_of

LEAD = pacing.LEAD_TRIGGER
EMPTY = {"calls": [], "passage": "It goes on.", "said": [], "asks": []}


# ------------------------------------------------------------------------------------------- C6: leads


def run_to_lead(game: Game) -> list[str]:
    for _ in range(12):
        facts, _ = step(game)
        if any(f.startswith("LEAD DUE") for f in facts):
            return facts
    raise AssertionError("no lead came due")


def test_c6_a_due_lead_is_told_and_nothing_is_spawned(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    before = set(game.store.state.entities)
    facts_before = len(game.store.state.facts)
    facts = run_to_lead(game)
    st = game.store.state
    (line,) = [f for f in facts if f.startswith("LEAD DUE")]
    assert "form:" in line and "Nothing was added to the world" in line and "knows" in line
    assert set(st.entities) == before  # no walk-on, no clue, no document
    assert not any(f.predicate.startswith("lead.") for f in st.facts.values()) and len(st.facts) >= facts_before
    assert not trigger_raised(st, LEAD) and (st.meta["inconclusive"] or {}).get("count") == 0  # lowered, streak reset
    assert st.meta["lead_injection"]["facts"] == []  # logged as told, not written
    # the only PR-12-3 writes are the log, the counter and the trigger (meta and flag events), never a fact or knowledge
    assert not [e for e in game.store.events() if e.rule_id == "PR-12-3" and e.type in ("knowledge_recorded", "entity_created")]


def test_c6_ignored_the_streak_counts_again_and_tells_again(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    run_to_lead(game)
    assert (game.store.state.meta["inconclusive"] or {}).get("count") == 0
    run_to_lead(game)  # nothing was done with the first: the streak builds again and it is told again


def test_c6_no_thread_or_source_on_record_is_told_so(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    game, _ = play(tmp_path)
    last = len(game.rules.pacing["lead_injection"]["source_ladder"]) - 1
    monkeypatch.setattr(pacing, "lead_candidates", lambda ctx, rng=None: (last, None, None))
    facts = run_to_lead(game)
    assert any("no open thread or source is on record" in f for f in facts)
    assert not trigger_raised(game.store.state, LEAD)


def test_c6_a_lead_due_while_a_roll_is_offered_is_told_after_it_resolves(tmp_path: Path) -> None:
    game, model = play(tmp_path)
    model.push(DM, {"calls": [roll(verb="verb.exert", goal="climb the wall", how="hand over hand")], "passage": "You reach.",
                    "said": [], "asks": []})
    r = game.submit("I climb the wall.")
    assert r.pause is not None
    in_turn(game, lambda ctx, t, tx: tx.add(raise_trigger(tx, LEAD, {"count": 9}, rule_id="12.8.1")))
    assert not any("LEAD DUE" in f for f in stats_of(game, r)["world"]["facts"])  # the offer turn told nothing
    assert trigger_raised(game.store.state, LEAD)  # held, not dropped
    model.push(DM, EMPTY, EMPTY, EMPTY)
    r = game.answer("commit")
    assert any(f.startswith("LEAD DUE") for f in stats_of(game, r)["world"]["facts"])
    assert not trigger_raised(game.store.state, LEAD)


def test_c6_the_dm_brings_it_in_with_an_ordinary_walk_on(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    run_to_lead(game)
    before = set(game.store.state.entities)
    go(game, change(kind="new_npc", what="a courier with a sealed letter", **{"as": "he"}))
    assert len(set(game.store.state.entities) - before) == 1


def test_c6_the_pipeline_still_writes_its_lead(tmp_path: Path) -> None:
    """The pipeline's `inject_lead` is unchanged: it writes the lead fact and knowledge, and tells the narrator."""
    model = ScriptedModel()
    game, r = Game.new(tmp_path / "p.db", GameConfig(offline=True), seed=7, model=model)
    quick_start(game, seed_oracle(game, r))

    def make(ctx: Any, t: Any, tx: Any) -> pacing.LeadInjection:
        return pacing.inject_lead(ctx.time_ctx())

    out = in_turn(game, make)
    assert out.facts or out.not_built  # a fact written (or the last rung, which has no source)


# ------------------------------------------------------------------------------------------- C7: witnesses


def make_short(game: Game, node_id: str = NODE, keep: int = 1) -> None:
    """Lose all but `keep` placements of the node (a fire, a death): fewer than two stay live."""
    def fn(ctx: Any, t: Any, tx: Any) -> None:
        allc = case.cases(tx.state)
        for c in allc.values():
            for n in c["nodes"]:
                if n["id"] == node_id:
                    for p in n["placements"][keep:]:
                        p["status"] = "lost"
        tx.add(meta(case.CASES, allc, "15.9.4"))

    in_turn(game, fn)


def short_ids(game: Game) -> list[str]:
    return [s[0] for s in case.short_of_sources(game.store.state)]


def end_scene_and_step(game: Game) -> list[str]:
    def fn(ctx: Any, t: Any, tx: Any) -> list[str]:
        assert dm_tools.tool(ctx, t, {"tool": "end_scene", "why": "x"}).startswith("done")
        return dm_world.world_step(ctx, t)

    return in_turn(game, fn)


def placements(game: Game, node_id: str = NODE) -> int:
    return sum(len(n["placements"]) for c in case.cases(game.store.state).values() for n in c["nodes"] if n["id"] == node_id)


def test_c7_told_once_per_shortfall_never_placed(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    assert short_ids(game) == []
    make_short(game)
    assert short_ids(game) == [NODE]
    ents, placed = set(game.store.state.entities), placements(game)
    facts = end_scene_and_step(game)  # the scene end runs h.15.placement_audit: under dm-tools it places nothing
    (line,) = [f for f in facts if f.startswith("WITNESS NEEDED")]
    assert NODE in line and f"knows: {NODE}" in line
    assert set(game.store.state.entities) == ents and placements(game) == placed  # nothing spawned, nothing placed
    assert not any(f.startswith("WITNESS NEEDED") for f in end_scene_and_step(game))  # still short, already told
    assert not any(f.startswith("WITNESS NEEDED") for f in step(game)[0])
    assert game.store.state.meta["told_short"] == [NODE]


def test_c7_told_again_only_after_a_new_shortfall(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    make_short(game)
    assert any(f.startswith("WITNESS NEEDED") for f in end_scene_and_step(game))
    go(game, change(kind="new_npc", what="a ferryman", knows=NODE, **{"as": "he"}))  # the DM answers it
    assert short_ids(game) == []
    assert not any(f.startswith("WITNESS NEEDED") for f in end_scene_and_step(game))
    assert game.store.state.meta["told_short"] == []  # recovered: forgotten
    make_short(game, keep=0)  # a fresh shortfall
    assert any(f.startswith("WITNESS NEEDED") for f in end_scene_and_step(game))


def test_c7_the_dm_places_a_witness_with_knows_end_to_end(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    make_short(game)
    assert any(f.startswith("WITNESS NEEDED") for f in end_scene_and_step(game))
    before = set(game.store.state.entities)
    held = holder_of(game, NODE)
    outs, _ = go(game, change(kind="new_npc", what="a ferryman who saw it", knows=NODE, **{"as": "he"}))
    (eid,) = set(game.store.state.entities) - before
    assert "now holds what" in outs[0] and holder_of(game, NODE) == [*held, eid]
    placed = next(p for c in case.cases(game.store.state).values() for n in c["nodes"] if n["id"] == NODE
                  for p in n["placements"] if p["holder"] == eid)
    assert placed["status"] == "unfound" and placed["id"].count(".") >= 1  # the reserve entry, now held by the new person
    assert short_ids(game) == [] and case.short_of_sources(game.store.state) == []
    # a later reveal_clue to them delivers it: the case now routes the question to the new holder
    node = next(n for c in case.cases(game.store.state).values() for n in c["nodes"] if n["id"] == NODE)
    outs, _ = go(game, {"tool": "reveal_clue", "npc": eid, "question": node["fact"]})
    assert outs[0].startswith("CLUE")


def test_c7_a_document_with_knows_also_answers_it(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    make_short(game)
    outs, _ = go(game, change(kind="new_item", what="a copied letter", to="pc", knows=NODE))
    assert "now holds what" in outs[0] and short_ids(game) == []


@pytest.mark.parametrize("knows", ["clu.nope.n9", "the duel"])
def test_c7_knows_an_unknown_node_places_nothing(tmp_path: Path, knows: str) -> None:
    game, _ = play(tmp_path)
    make_short(game)
    placed = placements(game)
    outs, _ = go(game, change(kind="new_npc", what="a ferryman", knows=knows, **{"as": "he"}))
    assert placements(game) == placed and short_ids(game) == [NODE]
    assert "names no clue node" in outs[0]


def test_c7_a_found_node_is_not_short_and_not_told(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    make_short(game)

    def fn(ctx: Any, t: Any, tx: Any) -> None:
        case.mark_found(tx, next(iter(case.cases(tx.state))), NODE)

    in_turn(game, fn)
    assert short_ids(game) == [] and not any(f.startswith("WITNESS NEEDED") for f in end_scene_and_step(game))


def test_c7_with_no_haven_on_record_it_is_still_told(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    make_short(game)
    in_turn(game, lambda ctx, t, tx: tx.add(meta("world.region", {}, "15.9.4")))
    assert any(f.startswith("WITNESS NEEDED") for f in end_scene_and_step(game))


def test_c7_travel_opens_a_scene_and_is_told_there(tmp_path: Path) -> None:
    game, _ = play(tmp_path)
    make_short(game)
    from engine.world.places import location, reachable

    st = game.store.state
    to = sorted(w.to for w in reachable(st, location(st)))[0]

    # the travel tool opens the scene the DM's way; the world step that follows is the one that tells
    def moved(ctx: Any, t: Any, tx: Any) -> list[str]:
        dm_tools._travel(ctx, t, to)
        return dm_world.world_step(ctx, t)

    assert any(f.startswith("WITNESS NEEDED") for f in in_turn(game, moved))


def test_c7_the_tools_path_audits_nothing_but_the_pipeline_still_does(tmp_path: Path) -> None:
    pipe = Game.new(tmp_path / "p.db", GameConfig(offline=True), seed=7, model=ScriptedModel())
    game, r = pipe
    quick_start(game, seed_oracle(game, r))
    make_short(game)
    assert short_ids(game) == [NODE]

    def end(ctx: Any, t: Any, tx: Any) -> None:
        from engine.world.scenes import end_scene

        end_scene(ctx.time_ctx(), "player_cut")

    in_turn(game, end)
    assert short_ids(game) == []  # the pipeline's audit placed a reserve witness (its path is unchanged)


# ------------------------------------------------------------------------------------------- 12.8.4


def test_1284_the_tools_path_fires_no_stalled_thread_fallback(tmp_path: Path) -> None:
    """`h.12.lead_audit` marks a thread stalled and queues its fallback; nothing in the tools path fires the queue
    (the only reader is `lead_candidates`, a told fact). A scene end leaves the world's people and clues as they were."""
    game, _ = play(tmp_path)
    ents = set(game.store.state.entities)
    for _ in range(3):
        end_scene_and_step(game)
    assert set(game.store.state.entities) == ents
    assert not [e for e in game.store.events() if getattr(e.payload, "rule_id", "") == "11.5.7"]


# ------------------------------------------------------------------------------------------- C10: retire


def pc_of(game: Game) -> str:
    from engine.retrieve.scene import pc_id

    return pc_id(game.store.state) or ""


def test_c10_retire_command_opens_the_confirmation(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    r = game.submit("/retire")
    assert r.pause is not None and [c.id for c in r.pause.choices] == ["retire", "keep_playing"]
    assert any("[RETIRE]" in b.text for b in r.oof_blocks)


@pytest.mark.parametrize("msg", ["I retire.", "retire my character", "OOC: I want to retire", "/retire now", "please /retire"])
def test_c10_other_words_go_to_the_dm(tmp_path: Path, msg: str) -> None:
    game, model = to_play(tmp_path)
    model.push(DM, {**EMPTY, "passage": "The DM answers in the fiction."})
    r = game.submit(msg)
    assert r.pause is None and "The DM answers" in r.text()


def test_c10_the_dm_end_game_opens_the_same_confirmation(tmp_path: Path) -> None:
    game, model = to_play(tmp_path)
    model.push(DM, {"calls": [{"tool": "end_game", "why": "the player asked to hang up the sword"}],
                    "passage": "You lay the sword down.", "said": [], "asks": []})
    r = game.submit("I think I am done with the road. Time to settle down.")
    assert r.pause is not None and [c.id for c in r.pause.choices] == ["retire", "keep_playing"]
    assert stats_of(game, r)["end_game"] == ["the player asked to hang up the sword"]
    r = game.answer("keep_playing")  # keep_playing closes it
    assert r.pause is None and game.store.state.open_pause() is None
    model.push(DM, {"calls": [{"tool": "end_game", "why": "again"}], "passage": "Again.", "said": [], "asks": []})
    r = game.submit("Actually, yes: retire.")
    r = game.answer("retire")
    assert r.phase == "ending" and r.pause is not None and r.pause.kind == "ending"


def test_c10_end_game_is_refused_under_an_open_question(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    game.submit("/retire")

    def fn(ctx: Any, t: Any, tx: Any) -> str:
        return dm_tools.tool(ctx, t, {"tool": "end_game", "why": "x"})

    assert in_turn(game, fn).startswith("REFUSED")


def test_c10_slash_retire_withdraws_an_offered_roll_first(tmp_path: Path) -> None:
    game, model = play(tmp_path)
    model.push(DM, {"calls": [roll(verb="verb.exert", goal="climb the wall", how="hand over hand")], "passage": "You reach.",
                    "said": [], "asks": []})
    r = game.submit("I climb the wall.")
    assert r.pause is not None and r.pause.kind != "clarify"
    t0 = clock.to_rounds(game.store.state.time.now)
    r = game.submit("/retire")
    assert r.pause is not None and [c.id for c in r.pause.choices] == ["retire", "keep_playing"]
    assert clock.to_rounds(game.store.state.time.now) == t0  # withdrawn: nothing spent
    assert [e for e in game.store.events() if e.type == "offer_logged"]


def test_c10_menu_answers_are_by_id_or_number_and_free_text_shows_it_again(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    game.submit("/retire")
    for text in ("sure, retire", "no thanks", "I retire", "keep playing please"):  # words are not answers
        r = game.submit(text)
        assert r.pause is not None and [c.id for c in r.pause.choices] == ["retire", "keep_playing"], text
    assert game.store.state.open_pause() is not None
    r = game.submit("2")  # a number
    assert r.pause is None and game.store.state.open_pause() is None
    game.submit("/retire")
    r = game.submit("retire")  # an id
    assert r.phase == "ending" and r.pause is not None and r.pause.kind == "ending"
    for text in ("a new character", "stop", "I would like a new world"):  # free text at the ending menu
        r = game.submit(text)
        assert r.pause is not None and r.pause.kind == "ending", text
    r = game.submit("1")  # number
    assert r.phase == "creation"


def test_c10_a_pipeline_game_keeps_its_words(tmp_path: Path) -> None:
    game, r = Game.new(tmp_path / "p.db", GameConfig(offline=True), seed=7, model=ScriptedModel())
    quick_start(game, seed_oracle(game, r))
    r = game.submit("I retire.")
    assert r.pause is not None and [c.id for c in r.pause.choices] == ["retire", "keep_playing"]
    r = game.submit("yes")
    assert r.phase == "ending"


def test_c10_the_guard_denies_the_regex_under_dm_tools() -> None:
    from tests.guard.viii9 import DENY

    for name in ("engine.dm.ending.is_retire", "engine.dm.ending._RETIRE", "engine.world.pacing.inject_lead",
                 "engine.gen.case.audit_cases"):
        assert DENY[name].mode == "raise", name
