"""Spec 032 P3 (lane T): the tools make the DM's words real. Cases R (prose-only people), O (OFFER words), I (items),
E (one revision, then drop), K (conditions) of specs/032-dm-tools-mvp/cases.md, on the offline scripted DM."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from engine.dm import dm_tools, oof
from engine.dm.npc_layer import is_animal
from engine.game import Game
from engine.harm.state import DEAD
from engine.resolve import conflict
from engine.resolve.types import Beat
from engine.retrieve.scene import pc_id
from engine.store.events import Event
from engine.world.common import fact
from engine.world.scenes import cast_present
from tests.engine.test_dm_tools import DM, change, in_turn, npc_here, to_play
from tests.engine.test_spec032_cases import FIX, RULES

BEAST = "npc.pale_beast"


def roll(**kw: Any) -> dict[str, Any]:
    base = {"tool": "propose_roll", "goal": "hit it", "verb": "verb.strike", "target": "", "how": "swing hard",
            "attribute": "might", "difficulty": "hard", "why_uncertain": "it is quick", "stakes": "risky",
            "nonlethal": False, "fail_cost": "none", "change_kind": "none", "change_what": "", "change_whom": ""}
    return {**base, **kw}


def run(game: Game, *calls: dict[str, Any]) -> tuple[list[str], Any]:
    """The calls in one turn; returns the outputs and the turn."""
    box: dict[str, Any] = {}

    def go(ctx: Any, t: Any, tx: Any) -> list[str]:
        box["t"] = t
        return [dm_tools.tool(ctx, t, c) for c in calls]

    return in_turn(game, go), box["t"]


def ent(game: Game, eid: str) -> Any:
    return game.store.state.entities[eid]


# ------------------------------------------------------------------------------------------- R: the resolver


def test_r1_to_r15_a_creature_in_prose_is_one_creature_here_for_every_verb(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    here = game.store.state.scene.place_id  # type: ignore[union-attr]
    seen = []
    for verb in RULES.ids("verb."):  # the 15 verbs
        def one(ctx: Any, t: Any, tx: Any, verb: str = verb) -> tuple[str | None, str | None]:
            # [P8a] nothing is matched: the same words in one turn are one creature (the code's own memo); the next
            # turn's words are a new one unless the DM uses the id
            first = dm_tools._party(ctx, t, "the pale beast", person=dm_tools.target_is_person(RULES, verb, None))
            return first, dm_tools._party(ctx, t, "the pale beast")

        a, b = in_turn(game, one)
        assert a == b and a is not None
        assert dm_tools._id(game.store.state, a) == a  # by its id it is found again
        seen.append(a)
    assert seen[0] == BEAST and len(set(seen)) == len(seen)
    e = ent(game, BEAST)
    assert e.data["mind"] == "animal" and is_animal(game.store.state, BEAST)
    assert game.store.state.positions[BEAST].location == here and BEAST in cast_present(game.store.state)


def test_r16_the_fighter_save_calls_are_accepted_and_the_beast_is_one_entity(tmp_path: Path) -> None:
    """Turn 9 and 12 of save playtest-20261010-153123-fighter-dm-tools: the calls that were REFUSED."""
    fx = json.loads(FIX.read_text(encoding="utf-8"))["turns"]
    game, _ = to_play(tmp_path)
    args9 = {"tool": "propose_roll", **json.loads(fx["turn.9"]["tools"][0]["args"])}
    outs, t = run(game, args9)
    assert outs[0].startswith("ROLL OFFERED") and t.stats["refusals"] == []
    beasts = [i for i, e in game.store.state.entities.items() if "beast" in i]
    assert len(beasts) == 1 and ent(game, beasts[0]).data["mind"] == "animal"
    # [P8a] the creature's id is what the DM uses next turn: found exactly
    assert in_turn(game, lambda ctx, t, tx: dm_tools._party(ctx, t, beasts[0])) == beasts[0]
    game2, _ = to_play(tmp_path / "b")
    args12 = {"tool": "propose_roll", **json.loads(fx["turn.12"]["tools"][0]["args"])}
    outs, t = run(game2, args12)
    assert outs[0].startswith("ROLL OFFERED") and t.stats["refusals"] == []


def test_r17_r18_r19_r23_described_people_are_walk_ons_groups_or_reused(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    box: dict[str, Any] = {}

    def go(ctx: Any, t: Any, tx: Any) -> None:
        for k, words in (("carter", "the carter at the well"), ("carter2", "the carter at the well"),
                         ("guard", "the lead guard"), ("none", ""), ("n2", "none"), ("n3", "world")):
            box[k] = dm_tools._party(ctx, t, words, person=True)
        box["existing"] = dm_tools._party(ctx, t, ctx.state.entities[npc_here(game)].name, person=True)

    in_turn(game, go)
    st = game.store.state
    assert box["carter"] == box["carter2"] and box["carter"] in cast_present(st)  # R23, R19
    assert st.entities[box["carter"]].data.get("name_known") is False  # R17: a walk-on with that role
    assert box["guard"] != box["carter"] and box["guard"] in st.entities
    assert box["none"] is None and box["n2"] is None and box["n3"] is None  # R21
    assert box["existing"] == npc_here(game)  # R19: an existing person is reused, no duplicate


def test_r20_r22_the_one_here_wins_and_the_absent_and_the_dead_are_refused(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    place = next(i for i, e in game.store.state.entities.items()
                 if e.kind == "place" and i != game.store.state.scene.place_id)  # type: ignore[union-attr]
    far = in_turn(game, lambda ctx, t, tx: dm_tools._party(ctx, t, "the beast", person=True))
    in_turn(game, lambda ctx, t, tx: tx.add(Event.of("position_set", source="engine", rule_id="x", entity=far,
                                                     location=place)))
    outs, _ = run(game, roll(target=far))
    assert outs[0].startswith("REFUSED") and "not here" in outs[0]  # a recorded creature elsewhere, by id: refused (spine)
    # [P8a] "the beast" in words is matched to no one: it is a new creature here
    here_one = in_turn(game, lambda ctx, t, tx: dm_tools._party(ctx, t, "a great beast", person=True))
    assert here_one != far and here_one in cast_present(game.store.state)
    # R22: dead or down
    npc = npc_here(game)
    in_turn(game, lambda ctx, t, tx: tx.add(fact(tx, npc, "harm_state", DEAD, rule_id="07.1.3")))
    outs, _ = run(game, roll(target=npc))
    assert outs[0].startswith("REFUSED") and "dead" in outs[0]


def test_a_thing_is_not_made_a_person_and_is_not_refused(tmp_path: Path) -> None:
    """[spec 032 P8a] supersedes the P3 refusal: an object named in words is the obstacle the act is on."""
    game, _ = to_play(tmp_path)
    before = set(game.store.state.entities)
    outs, t = run(game, roll(verb="verb.force", target="the locked door", change_kind="open", change_what="the door"))
    assert not outs[0].startswith("REFUSED: no one"), outs[0]
    assert set(game.store.state.entities) == before and t.made == []


def test_r24_to_r34_each_change_kind_with_a_person_in_prose(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    pc = pc_id(game.store.state)
    npc = npc_here(game)
    sword = next(i for i, e in game.store.state.entities.items() if e.kind == "item" and "sword" in i)
    place = next(i for i, e in game.store.state.entities.items()
                 if e.kind == "place" and i != game.store.state.scene.place_id)  # type: ignore[union-attr]
    kinds = {
        "coin": change(kind="coin", who="the carter", to=pc, amount=2),
        "give_item": change(kind="give_item", what=sword, to="the porter"),
        "new_item": change(kind="new_item", what="a tin whistle", to="the drover"),
        "condition_add": change(kind="condition_add", who="the cook", what="cond.dazed"),
        "condition_remove": change(kind="condition_remove", who=npc, what="cond.dazed"),
        "npc_leaves": change(kind="npc_leaves", who="the tinker", to=place),
        "new_npc": change(kind="new_npc", who="the ghost", what="a ferryman"),
        "travel": change(kind="travel", to="the old mill"),
        "rest": change(kind="rest", who="the ghost", what="breather"),
        "fact": change(kind="fact", who="the clerk", what="owes_money", note="three crowns"),
        "fight": change(kind="fight", who="the pale beast"),
        "position": change(kind="position", who="the sentry", to="far"),  # [spec 033]
    }
    assert set(kinds) == set(dm_tools.CHANGES) and len(kinds) == 12  # a new kind without a case fails
    in_turn(game, lambda ctx, t, tx: dm_tools.tool(ctx, t, change(kind="condition_add", who=npc, what="cond.dazed")))
    made = {}
    for k, c in kinds.items():
        before = set(game.store.state.entities)
        outs, t = run(game, c)
        made[k] = (outs[0], set(game.store.state.entities) - before)
    people = {"coin", "give_item", "new_item", "condition_add", "npc_leaves", "fight", "position"}
    for k in people:
        assert made[k][0].startswith("done") or made[k][0].startswith("REFUSED: "), (k, made[k][0])
        assert not made[k][0].startswith("REFUSED: no one or nothing on record"), (k, made[k][0])
        assert len(made[k][1]) >= 1, (k, "no one was made")
    # a coin source with no purse pays from their own means; a person who is given an item holds it
    assert made["coin"][0].startswith("done") and made["give_item"][0].startswith("done")
    assert made["new_item"][0].startswith("done") and made["condition_add"][0].startswith("done")
    assert made["npc_leaves"][0].startswith("done") and made["fight"][0].startswith("done")
    # not valid for a person in prose: the new_npc/rest/travel slots take none, a fact's subject is not made
    assert made["new_npc"][0].startswith("done") and len(made["new_npc"][1]) == 1  # only the new person
    assert made["rest"][1] == set() and made["travel"][0].startswith("REFUSED") and made["travel"][1] == set()
    assert made["fact"][0].startswith("REFUSED") and made["fact"][1] == set()
    assert made["condition_remove"][0].startswith("done") or made["condition_remove"][0].startswith("REFUSED")


def test_r_a_fact_about_a_creature_or_a_known_alias_is_accepted(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    outs, _ = run(game, change(kind="fact", who="the pale beast", what="limps", note="left foreleg"))
    assert outs[0].startswith("done: recorded limps")


# ------------------------------------------------------------------------------------------- change kind fight


def test_a_fight_change_starts_the_conflict_and_does_nothing_to_the_pc(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    pc = pc_id(game.store.state)
    npc = npc_here(game)
    vit0 = game.store.state.quantities.get(pc, {}).get("vitality")
    outs, _ = run(game, change(kind="fight", who=npc))
    st = game.store.state
    assert outs[0].startswith("done: a fight begins") and conflict.active(st)
    assert npc in conflict.record(st)["foes"] and st.time.last_boundary.get("conflict_start")
    assert st.quantities.get(pc, {}).get("vitality") == vit0  # no foe action here
    again, _ = run(game, change(kind="fight", who=npc))
    assert "already in the fight" in again[0]
    gone, _ = run(game, change(kind="fight", who="the pale beast"))  # made, and joins the running fight
    assert gone[0].startswith("done") or "already" in gone[0]


def test_a_fight_with_a_dead_or_absent_person_is_refused(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    in_turn(game, lambda ctx, t, tx: tx.add(fact(tx, npc, "harm_state", DEAD, rule_id="07.1.3")))
    outs, _ = run(game, change(kind="fight", who=npc))
    assert outs[0].startswith("REFUSED") and "dead" in outs[0] and not conflict.active(game.store.state)


# ------------------------------------------------------------------------------------------- O: OFFER words


def test_o_the_nine_cost_ids_are_the_schema_menu() -> None:
    assert sorted(dm_tools.FAIL_COSTS) == sorted(RULES.ids("cost."))
    props = dm_tools.step_schema.__globals__["schema_for"](["verb.strike"], ["harm"], final=False)
    enum_ = props["properties"]["calls"]["items"]["anyOf"][0]["properties"]["fail_cost"]["enum"]
    assert enum_ == ["none", *dm_tools.FAIL_COSTS]


def _offer_cost(tmp_path: Path, fail_cost: str) -> tuple[str, dict[str, Any]]:
    game, _ = to_play(tmp_path)
    outs, _ = run(game, roll(target="the pale beast", stakes="dire", fail_cost=fail_cost, change_kind="harm",
                             change_what="the pale beast", goal="Drive the beast off the cart"))
    p = game.store.state.open_pause()
    assert outs[0].startswith("ROLL OFFERED") and p is not None
    pr = p.detail["proposed"]
    return pr["threatened_cost"]["menu_id"], {"menu": pr["stakes_source"], "alt": pr["alternate_cost"]["menu_id"]}


@pytest.mark.parametrize("cost", sorted(RULES.ids("cost.")))
def test_o1_to_o9_fail_cost_is_honoured_when_the_menu_has_it_else_the_plain_fallback(tmp_path: Path, cost: str) -> None:
    got, _ = _offer_cost(tmp_path / "a", cost)
    base, _ = _offer_cost(tmp_path / "b", "none")
    assert got in RULES.ids("cost.")  # never raises, always a menu cost
    assert got == cost or got == base  # honoured, or exactly today's fallback


def test_o_at_least_one_cost_is_actually_chosen_by_the_dm(tmp_path: Path) -> None:
    base, _ = _offer_cost(tmp_path / "b", "none")
    others = [c for c in sorted(RULES.ids("cost.")) if c != base]
    assert any(_offer_cost(tmp_path / c, c)[0] == c for c in others)


def test_o10_o12_the_offer_title_is_the_dms_goal_words_else_the_default(tmp_path: Path) -> None:
    game, model = to_play(tmp_path)
    call = roll(target="the pale beast", stakes="dire", change_kind="harm", change_what="the pale beast",
                goal="Hurt the beast before its lunge lands")
    model.push(DM, {"calls": [call], "passage": "It gathers itself.", "said": [], "asks": []})
    r = game.submit("I charge the beast.")
    offer = next(b for b in r.oof_blocks if b.kind == "OFFER")
    assert "Hurt the beast before its lunge lands" in offer.text
    p = game.store.state.open_pause()
    assert p is not None
    beat = Beat.model_validate(p.detail["plan"]["beat"])
    assert beat.title == "Hurt the beast before its lunge lands"
    assert oof.goal_line(beat, game.store.state) == "Hurt the beast before its lunge lands"
    plain = beat.model_copy(update={"title": None})  # O12: no DM title -> the rendered default, as the pipeline's
    assert oof.goal_line(plain, game.store.state) != "Hurt the beast before its lunge lands"
    assert Beat.model_validate({**beat.model_dump(), "title": None}).title is None


# ------------------------------------------------------------------------------------------- I: items


def _two_people(game: Game) -> tuple[str, str, str]:
    """pc, an NPC here, and a second NPC here."""
    pc = pc_id(game.store.state)
    a = npc_here(game)
    b = in_turn(game, lambda ctx, t, tx: dm_tools._party(ctx, t, "the porter", person=True))
    assert b is not None
    return pc, a, b


def test_i1_to_i11_items_move_only_between_people_who_hold_and_are_here(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    pc, a, b = _two_people(game)
    sword = next(i for i, e in game.store.state.entities.items() if e.kind == "item" and "sword" in i)
    st = lambda: game.store.state  # noqa: E731
    out = lambda *c: run(game, *c)[0]  # noqa: E731
    from engine.resolve.change import holder_of

    assert out(change(kind="give_item", what=sword, to=a))[0].startswith("done") and holder_of(st(), sword) == a  # I1
    assert out(change(kind="give_item", what=sword, who=a, to=pc))[0].startswith("done")  # I2
    assert out(change(kind="give_item", what=sword, to=a))[0].startswith("done")
    assert out(change(kind="give_item", what=sword, who=a, to=b))[0].startswith("done") and holder_of(st(), sword) == b  # I3
    assert out(change(kind="give_item", what=sword, who=a, to=pc))[0].startswith("REFUSED")  # I4: a does not hold it
    far = next(i for i, e in st().entities.items() if e.kind == "npc" and i not in cast_present(st()))
    assert "not here" in out(change(kind="give_item", what=sword, who=b, to=far))[0]  # I5
    assert out(change(kind="coin", who="", to=pc, amount=3))[0].startswith("REFUSED: coin from no source")  # I7
    assert out(change(kind="coin", who=pc, to=a, amount=10 ** 6))[0].startswith("REFUSED")  # I8
    assert out(change(kind="coin", who=a, to=pc, amount=1))[0].startswith("done")  # I9
    loose = out(change(kind="new_item", what="a stray lantern", to=""))[0]  # held by the pc (default)
    assert loose.startswith("done")


def test_i6_i10_a_new_item_named_like_a_held_one_echoes_the_held_one(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    pc = pc_id(game.store.state)
    npc = npc_here(game)
    first, _ = run(game, change(kind="new_item", what="a bone knife", to=npc))
    assert first[0].startswith("done") and "NOTE" not in first[0]
    second, _ = run(game, change(kind="new_item", what="a bone knife", to=pc))
    assert second[0].startswith("done") and "NOTE" in second[0] and "item.a_bone_knife)" in second[0]
    assert "already holds" in second[0] and "give_item" in second[0]


def test_i11_a_loose_item_here_can_be_given_by_anyone(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    place = game.store.state.scene.place_id  # type: ignore[union-attr]

    def make(ctx: Any, t: Any, tx: Any) -> str:
        from engine.store.events import EntityRecord

        tx.add(Event.of("entity_created", source="engine", rule_id="00.6.6",
                        entity=EntityRecord(id="item.loose_rope", kind="item", name="loose rope", visibility="shown")))
        tx.add(fact(tx, "item.loose_rope", "holder", place, rule_id="01.2.7"))
        return dm_tools.tool(ctx, t, change(kind="give_item", what="item.loose_rope", who=npc, to=pc_id(tx.state)))

    assert in_turn(game, make).startswith("done")


# ------------------------------------------------------------------------------------------- E: one revision, then drop


def test_e1_to_e4_a_second_breach_is_dropped_and_logged_the_first_is_not(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    pc = pc_id(game.store.state)
    sword = next(i for i, e in game.store.state.entities.items() if e.kind == "item" and "sword" in i)
    cases = {
        "E4 no source": [change(kind="coin", who="", to=pc, amount=3)] * 2,
        "E3 not owned": [change(kind="give_item", what=sword, who=npc, to=pc)] * 2,
        "E1 unknown": [change(kind="npc_leaves", who="loc.nobody")] * 2,  # [P8a] an `npc.` id is a walk-on now
    }
    for name, calls in cases.items():
        outs, t = run(game, *calls)
        assert outs[0].startswith("REFUSED") and "DROPPED" not in outs[0], name  # the first breach: a revision is allowed
        assert outs[1].startswith("REFUSED") and "DROPPED" in outs[1], name
        assert len(t.stats["refusals"]) == 2 and len(t.stats["dropped"]) == 1, name
    # E1/E2 on the real spine: a dead person, then an absent one, are refused with the reason
    in_turn(game, lambda ctx, t, tx: tx.add(fact(tx, npc, "harm_state", DEAD, rule_id="07.1.3")))
    outs, t = run(game, change(kind="coin", who=npc, to=pc, amount=1), change(kind="coin", who=npc, to=pc, amount=1))
    assert "dead" in outs[0] and len(t.stats["dropped"]) == 1


def test_e2_an_absent_actor_is_refused(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    place = next(i for i, e in game.store.state.entities.items()
                 if e.kind == "place" and i != game.store.state.scene.place_id)  # type: ignore[union-attr]
    outs, _ = run(game, change(kind="npc_leaves", who=npc, to=place), change(kind="coin", who=npc, to="pc", amount=1))
    assert outs[0].startswith("done") and outs[1].startswith("REFUSED")


def test_e6_a_breach_in_the_last_tool_slot_is_dropped_at_once(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)

    def go(ctx: Any, t: Any, tx: Any) -> str:
        t.stats["tool_calls"] = dm_tools.MAX_TOOLS - 1  # the sixth call: no revision left
        return dm_tools.tool(ctx, t, change(kind="coin", who="", to=pc_id(tx.state), amount=3))

    out = in_turn(game, go)
    assert out.startswith("REFUSED") and "DROPPED" in out


def test_e7_e8_nothing_is_done_to_the_pc_without_a_roll_but_an_npc_may_be_conditioned(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    pc = pc_id(game.store.state)
    npc = npc_here(game)
    outs, _ = run(game, change(kind="condition_add", who=pc, what="cond.dazed"),
                  change(kind="condition_add", who=npc, what="cond.dazed"))
    assert outs[0].startswith("REFUSED") and "without a roll" in outs[0]
    assert outs[1].startswith("done")  # E8
    assert game.store.state.conditions_on(pc) == [] or all(i.condition_id != "cond.dazed"
                                                           for i in game.store.state.conditions_on(pc))


# ------------------------------------------------------------------------------------------- K: the 33 conditions


def test_k1_to_k33_each_condition_on_an_npc_and_on_the_pc(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    pc = pc_id(game.store.state)
    npc = npc_here(game)
    ids = RULES.ids("cond.")
    assert len(ids) == 33
    for cid in ids:
        outs, _ = run(game, change(kind="condition_add", who=npc, what=cid), change(kind="condition_add", who=pc, what=cid))
        if cid in dm_tools.HARM_OWNED:
            assert outs[0].startswith("REFUSED") and "harm" in outs[0], (cid, outs[0])
        else:
            assert outs[0].startswith("done"), (cid, outs[0])
            if any(i.condition_id == cid for i in game.store.state.conditions_on(npc)):
                rm, _ = run(game, change(kind="condition_remove", who=npc, what=cid))
                assert rm[0].startswith("done"), (cid, rm[0])
        assert outs[1].startswith("REFUSED"), (cid, outs[1])  # E7 on the PC, for every one of the 33
    bad, _ = run(game, change(kind="condition_add", who=npc, what="cond.no_such"))
    assert bad[0].startswith("REFUSED") and "cond.bleeding" in bad[0]  # an unknown id: refused with examples
    assert len(dm_tools.HARM_OWNED) == 5 and set(dm_tools.HARM_OWNED) <= set(ids)
