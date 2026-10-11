"""Spec 033 P2a: positions, contact, fight start and costs on the dm-tools path (cases C1.d-g, C2, C3, C5).

With `Beat.stated` set every guessing helper is skipped: a band is written only from `stated.position` or Force's
stated ladder, a Strike or Grapple writes no band, no fight starts from code, the weapon and lethality are the DM's,
an untyped Grapple holds nothing, and a footing cost defers its options to the DM's pick."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from engine.llm.base import Role
from engine.resolve import change, conflict, costs
from engine.resolve import pipeline as pl
from engine.resolve.types import Beat, RollResult, Stated
from engine.retrieve.scene import pc_id
from tests.engine.test_dm_tools import in_turn, npc_here, to_play

BASE = {"tool": "propose_roll", "goal": "Do it", "verb": "verb.strike", "target": "", "as": "none", "how": "",
        "attribute": "", "difficulty": "", "why_uncertain": "", "stakes": "risky", "nonlethal": False, "force": "none",
        "weapon": "", "reads": False, "approach": "plain", "fail_cost": "none", "fail_on": "", "change_kind": "none",
        "change_what": "", "change_whom": ""}


def fixed(degree: str) -> Callable[..., RollResult]:
    def roll(frame: Any, rng: Any) -> RollResult:
        return RollResult(frame_id=frame.id, d20=15, total=20, margin=5, base_degree=degree, degree=degree,  # type: ignore[arg-type]
                          near_miss=False)

    return roll


def play(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, over: dict[str, Any], degree: str = "success",
         setup: Callable[[Any, str, str], None] | None = None, engaged: bool = True) -> tuple[Any, str, str]:
    """One proposed roll whose die is fixed at `degree`, offered then committed. Returns (game, npc, pc)."""
    game, model = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    if setup is not None:
        setup(game, npc, pc)
    monkeypatch.setattr(pl, "roll_check", fixed(degree))
    call = {**BASE, "target": npc, **{k: (npc if v == "@npc" else pc if v == "@pc" else v) for k, v in over.items()}}
    if call["verb"] in ("verb.strike", "verb.grapple", "verb.force") and engaged:  # 06.4.3: in reach first (P3)
        with game.store.transaction("turn.900") as tx:
            conflict._set_band(tx, pc, npc, "engaged", "06.3.9")
    model.push(Role.DM, {"calls": [call], "passage": "Lead-up.", "said": [], "asks": []})
    r = game.submit("I act.")
    assert r.pause is not None and r.pause.kind == "offer"
    game.first_turn = r.turn_id  # type: ignore[attr-defined]
    model.push(Role.DM, {"calls": [], "passage": "Result.", "said": [], "asks": []},
               {"calls": [], "passage": "Result.", "said": [], "asks": []})
    r = game.answer("commit")
    assert r.pause is None
    return game, npc, pc


def conds(game: Any, who: str) -> list[str]:
    return [c.condition_id for c in game.store.state.conditions_on(who)]


def hold_on(game: Any, held: str, holder: str, reach: int = 2) -> None:
    with game.store.transaction("turn.901") as tx:
        tx.add_all(change.hold(tx, game.ctx.rules, held, holder, reach, "beat.x"))


# ------------------------------------------------------------------------------------------- C1.d positions


@pytest.mark.parametrize("band", list(conflict.BANDS))
def test_a_stated_move_to_writes_its_band_both_ways_on_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                                band: str) -> None:
    game, npc, pc = play(tmp_path, monkeypatch, {"verb": "verb.move", "change_kind": "move_to", "change_what": band})
    st = game.store.state
    assert conflict._band(st, pc, npc) == band and conflict._band(st, npc, pc) == band


def test_a_failed_move_writes_no_band_and_the_other_party_can_be_the_mover(tmp_path: Path,
                                                                           monkeypatch: pytest.MonkeyPatch) -> None:
    game, npc, pc = play(tmp_path, monkeypatch, {"verb": "verb.move", "change_kind": "move_to", "change_what": "far"},
                         "failure")
    assert conflict._band(game.store.state, pc, npc) is None
    game, npc, pc = play(tmp_path / "b", monkeypatch, {"verb": "verb.move", "change_kind": "move_to",
                                                       "change_what": "engaged", "change_whom": "@npc"})
    assert conflict._band(game.store.state, npc, pc) == "engaged"


def test_no_band_is_guessed_from_the_words_of_a_move(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """"retreat" and "flee" moved a mover one band away (`_AWAY`); with the DM stating nothing, nothing is written."""
    game, npc, pc = play(tmp_path, monkeypatch, {"verb": "verb.move", "goal": "Retreat and flee back",
                                                 "change_kind": "none"})
    assert conflict._band(game.store.state, pc, npc) is None


# ------------------------------------------------------------------------------------------- contact and fight start


@pytest.mark.parametrize("verb", ["verb.strike", "verb.grapple"])
def test_a_strike_or_grapple_writes_no_band_and_starts_no_fight(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                                 verb: str) -> None:
    game, npc, pc = play(tmp_path, monkeypatch, {"verb": verb, "change_kind": "harm" if verb == "verb.strike" else "none"})
    st = game.store.state
    assert conflict._band(st, pc, npc) == "engaged" == conflict._band(st, npc, pc)  # as the DM left it: nothing written
    assert not conflict.record(st) and not conflict.active(st)  # only the DM's `change fight` starts one


def test_the_dm_fight_start_is_unchanged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    from engine.dm import dm_tools

    out = in_turn(game, lambda ctx, t, tx: dm_tools._fight(ctx, npc, pc, "far"))
    assert "range far" in out


# ------------------------------------------------------------------------------------------- C1.e C1.f weapon, lethality


def seen_harm(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, str]]:
    seen: list[tuple[str, str]] = []
    real = conflict.strike_harm

    def spy(tx: Any, rules: Any, rng: Any, frame: Any, delivered: int, *, w: dict[str, Any], mode: str) -> Any:
        seen.append((w["id"], mode))
        return real(tx, rules, rng, frame, delivered, w=w, mode=mode)

    monkeypatch.setattr(conflict, "strike_harm", spy)
    return seen


def test_the_strike_uses_the_stated_weapon_and_lethality_never_the_words(tmp_path: Path,
                                                                         monkeypatch: pytest.MonkeyPatch) -> None:
    seen = seen_harm(monkeypatch)
    # words that the old regexes read: "knock him out" (nonlethal), "punch" (unarmed), "sword" (a weapon)
    play(tmp_path, monkeypatch, {"change_kind": "harm", "goal": "Knock him out with a punch", "how": "my sword"})
    assert seen == [("unarmed", "lethal")]  # nothing wielded on record, nonlethal not stated
    seen.clear()
    play(tmp_path / "b", monkeypatch, {"change_kind": "harm", "nonlethal": True, "weapon": "unarmed",
                                       "goal": "Cut him down"})
    assert seen == [("unarmed", "nonlethal")]


def test_a_held_weapon_item_gives_its_weight() -> None:
    from engine.data.loader import load_rules

    rules = load_rules()
    st = SimpleNamespace(entities={"item.a": SimpleNamespace(tags=["item.weapon.blade.dagger"]),
                                   "item.b": SimpleNamespace(tags=["item.junk"])})
    assert conflict.weapon_of(rules, st, "item.a")["id"] == "light"
    assert conflict.weapon_of(rules, st, "item.b")["id"] == "unarmed"  # ponytail: an improvised weapon is unarmed
    assert conflict.weapon_of(rules, st, "unarmed")["id"] == "unarmed" == conflict.weapon_of(rules, st, None)["id"]


def test_the_method_text_is_unchanged_by_nonlethal(tmp_path: Path) -> None:
    from engine.dm import dm_tools

    game, _ = to_play(tmp_path)
    npc = npc_here(game)

    def run(ctx: Any, t: Any, tx: Any) -> str:
        conflict._set_band(tx, t.rec.pc, npc, "engaged", "06.3.9")
        dm_tools._propose_roll(ctx, t, {**BASE, "target": npc, "nonlethal": True, "how": "with the flat of the blade",
                                        "change_kind": "harm"})
        return str(Beat.model_validate(tx.state.open_pause().detail["frame"]["beat"]).method)

    assert in_turn(game, run) == "with the flat of the blade"


# ------------------------------------------------------------------------------------------- C1.g holds


def test_an_untyped_grapple_holds_nothing_but_a_stated_restrain_climbs_the_ladder(tmp_path: Path,
                                                                                   monkeypatch: pytest.MonkeyPatch) -> None:
    game, npc, pc = play(tmp_path, monkeypatch, {"verb": "verb.grapple", "change_kind": "none"})
    assert conds(game, npc) == []
    game, npc, pc = play(tmp_path / "b", monkeypatch, {"verb": "verb.grapple", "change_kind": "restrain",
                                                       "change_what": "@npc"})
    assert conds(game, npc) == ["cond.grabbed"]
    game, npc, pc = play(tmp_path / "c", monkeypatch, {"verb": "verb.grapple", "change_kind": "restrain",
                                                       "change_what": "@npc"}, "critical_success")
    assert conds(game, npc) == ["cond.restrained"]


def test_free_ends_the_actors_hold_and_a_grapple_without_free_does_not(tmp_path: Path,
                                                                       monkeypatch: pytest.MonkeyPatch) -> None:
    game, npc, pc = play(tmp_path, monkeypatch, {"verb": "verb.grapple", "change_kind": "free", "change_what": "@pc"},
                         setup=lambda g, n, p: hold_on(g, p, n))
    assert conds(game, pc) == []


def test_cleanse_reads_no_freeing_words_for_a_stated_beat(tmp_path: Path) -> None:
    """The held PC grapples something else with "break free" words: only the pipeline's `_FREEING` guess frees it."""

    def run(stated: Stated | None, kind: str) -> list[str]:
        g, _ = to_play(tmp_path / f"{kind}{stated is None}")
        npc, pc = npc_here(g), pc_id(g.store.state) or ""
        other = next(i for i, e in g.store.state.entities.items() if e.kind == "object")
        hold_on(g, pc, npc)
        beat = Beat(id="beat.1", actor=pc, intent="Break free", method="wrench loose", target=other, stated=stated,
                    change=change.Change(kind=kind, what=pc) if kind != "none" else None)
        frame = SimpleNamespace(beat=beat, gate=SimpleNamespace(verb="verb.grapple"))
        with g.store.transaction("turn.902") as tx:
            env = pl.PipelineEnv(tx=tx, rules=g.ctx.rules, rng=None, store=g.store, framer=None, pc=pc)  # type: ignore[arg-type]
            pl._cleanse(env, frame)  # type: ignore[arg-type]
        return conds(g, pc)

    assert run(None, "none") == []  # the pipeline: the words free it
    assert run(Stated(), "none") == ["cond.grabbed"]  # stated: no word test
    assert run(Stated(), "free") == []  # the DM's `free` aims it


# ------------------------------------------------------------------------------------------- C2 force


def test_force_push_moves_the_target_by_reach_from_the_stated_force(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    over = {"verb": "verb.force", "force": "push", "change_kind": "harm", "goal": "Trip him onto the floor"}
    game, npc, pc = play(tmp_path, monkeypatch, over)  # reach 2: one band, whatever the words say
    assert conflict._band(game.store.state, pc, npc) == "close" == conflict._band(game.store.state, npc, pc)
    assert conds(game, npc) == []
    game, npc, pc = play(tmp_path / "b", monkeypatch, over, "critical_success")  # reach 3: two bands
    assert conflict._band(game.store.state, pc, npc) == "near"
    game, npc, pc = play(tmp_path / "c", monkeypatch, over, "failure")
    assert conflict._band(game.store.state, pc, npc) == "engaged" and conds(game, npc) == []


def test_force_prone_knocks_down_without_moving(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    over = {"verb": "verb.force", "force": "prone", "change_kind": "harm", "goal": "Shove him back"}
    game, npc, pc = play(tmp_path, monkeypatch, over)
    assert conds(game, npc) == ["cond.prone"] and conflict._band(game.store.state, pc, npc) == "engaged"
    game, npc, pc = play(tmp_path / "b", monkeypatch, over, "critical_success")
    assert conds(game, npc) == ["cond.prone"]  # prone and off balance: the condition rules fold off balance into prone


def test_force_omitted_defaults_to_push_and_is_logged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    game, npc, pc = play(tmp_path, monkeypatch, {"verb": "verb.force", "force": "none", "change_kind": "harm"})
    assert conflict._band(game.store.state, pc, npc) == "close"
    assert game.store.turn(game.first_turn).screen["dm_tools"]["defaults"] == ["not_chosen:force"]


# ------------------------------------------------------------------------------------------- C3 pipeline unchanged


def test_the_pipeline_keeps_its_guessing_helpers() -> None:
    assert Beat(id="b", actor="a", intent="i", method="m").stated is None
    assert pl._same_goal("obj.track", "obj.track_in_the_damp_earth")
    assert not pl._same_goal("obj.track", "obj.track_in_the_damp_earth", exact=True)
    assert pl._same_goal("obj.track", "obj.track", exact=True)


# ------------------------------------------------------------------------------------------- C5 costs


def frame_of(actor: str, target: str | None, **stated: Any) -> Any:
    return SimpleNamespace(beat=Beat(id="beat.1", actor=actor, intent="i", method="m", target=target,
                                     stated=Stated(**stated)), defender=None)


def test_fail_on_names_who_notices_which_item_and_who_refuses(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    item = next(i for i, e in game.store.state.entities.items() if e.kind == "item" and change.holder_of(
        game.store.state, i) == pc)

    def run(ctx: Any, t: Any, tx: Any) -> dict[str, Any]:
        env = t.env
        out: dict[str, Any] = {}
        out["exp"] = pl._stated_cost_params(env, frame_of(pc, None, fail_on=npc), "cost.exposure")
        out["exp_none"] = pl._stated_cost_params(env, frame_of(pc, None), "cost.exposure")
        out["gear"] = pl._stated_cost_params(env, frame_of(pc, npc, fail_on=item), "cost.gear")
        out["gear_not_held"] = pl._stated_cost_params(env, frame_of(pc, npc, fail_on=npc), "cost.gear")
        out["door"] = pl._stated_cost_params(env, frame_of(pc, None, fail_on=npc), "cost.closed_door")
        out["door_default"] = pl._stated_cost_params(env, frame_of(pc, npc), "cost.closed_door")
        out["harm"] = pl._stated_cost_params(env, frame_of(pc, npc), "cost.harm")
        out["defaults"] = list(env.defaults)
        return out

    got = in_turn(game, run)
    assert got["exp"]["observer"] == npc and "observer" not in got["exp_none"]  # no scene-cast guess
    assert got["gear"]["item"] == item and got["gear_not_held"].get("item") != npc
    assert got["door"]["target"] == npc and got["door_default"]["target"] == npc
    assert got["harm"] == {"stated": True}
    assert got["defaults"].count("not_chosen:fail_on") == 3  # exp_none, gear_not_held (not the actor's), door_default


def test_a_failed_stated_exposure_cost_alerts_the_one_stated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    game, npc, pc = play(tmp_path, monkeypatch, {"change_kind": "harm", "fail_cost": "cost.exposure", "fail_on": "@npc"},
                         "failure")
    assert game.store.state.fact_value(npc, "alertness") == "alert"


def test_footing_options_are_only_those_that_can_land(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    st = game.store.state
    npc, pc = npc_here(game), pc_id(st) or ""
    f = frame_of(pc, npc)

    def ids_of(sev: str, state: Any = st) -> list[str]:
        return [o.id for o in costs.footing_options(state, f, sev)]

    s1, s2 = ids_of("S1"), ids_of("S2")
    assert s1[0] == "off_balance" and not any(x.startswith("lose:") for x in s1)  # no flag held
    assert s2[0] == "prone" and "grabbed" not in s2 and "band_back" not in s2  # no band recorded, not engaged
    assert all(x.startswith("slide:") for x in s2[1:])  # an exit on record
    assert ids_of("S3") == ["restrained", "cornered", "slowed"]  # separated needs a band
    assert ids_of("S4") == ["pinned", "controlled"] and ids_of("S5")[0] == "trapped"

    with game.store.transaction("turn.901") as tx:
        conflict._set_band(tx, pc, npc, "engaged", "06.3.9")
        tx.add(change_event_flag(pc))
        s1b, s2b, s3b = (ids_of(s, tx.state) for s in ("S1", "S2", "S3"))
    assert "lose:flag.hidden" in s1b
    assert {"grabbed", "band_back"} <= set(s2b) and "separated" in s3b
    nobody = frame_of(pc, None)
    assert [o.id for o in costs.footing_options(st, nobody, "S4")] == ["pinned"]  # no opponent: no control


def change_event_flag(pc: str) -> Any:
    from engine.store.events import Event

    return Event.of("position_set", source="engine", rule_id="t", entity=pc, flags_add=["flag.hidden"])


def test_a_failed_stated_footing_defers_its_options_and_apply_footing_writes_exactly_the_pick(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from engine.dm import dm_tools

    monkeypatch.setattr(dm_tools, "_footing", lambda ctx, t: None)  # hold the deferral: the flow (P3) is tested elsewhere
    game, npc, pc = play(tmp_path, monkeypatch, {"change_kind": "harm", "fail_cost": "cost.footing"}, "failure")
    pend = costs.pending_footing(game.store.state)
    assert pend is not None and pend["severity"] == "S2" and pend["options"][0] == "prone"
    assert conds(game, pc) == []  # nothing written until the DM picks
    with game.store.transaction("turn.902") as tx:
        pick, defaulted = costs.apply_footing(tx, game.ctx.rules, pend, pend["options"][-1])
    assert pick == pend["options"][-1] and not defaulted and costs.pending_footing(game.store.state) is None
    assert conds(game, pc) == []  # a slide is a fact, not a condition
    assert game.store.state.fact_value(pc, "footing") is not None


def test_apply_footing_defaults_to_the_first_option_that_can_land(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from engine.dm import dm_tools

    monkeypatch.setattr(dm_tools, "_footing", lambda ctx, t: None)
    game, npc, pc = play(tmp_path, monkeypatch, {"change_kind": "harm", "fail_cost": "cost.footing"}, "failure")
    pend = costs.pending_footing(game.store.state)
    assert pend is not None
    with game.store.transaction("turn.902") as tx:
        pick, defaulted = costs.apply_footing(tx, game.ctx.rules, pend, "restrained")  # not among those shown
    assert pick == "prone" and defaulted
    assert conds(game, pc) == ["cond.prone"]
