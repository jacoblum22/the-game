"""Spec 033 P8: the fixes from live check 1 [owner ruling 2026-10-11].

Attack rolls carry `starts_fight` / `fight_to`; an unrecorded band is an omitted detail (a recorded one out of reach is
still refused); `change position` refuses a swapped or self-referring call with one exact example; `new_npc` has a
`name` the DM calls them by. Cases are rebuilt from the saves in specs/033-dm-states-code-records/live-check-1.md.
Nothing here reads prose: the code keys on the DM's verb and ids."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from engine.dm import dm_tools
from engine.llm.base import Role
from engine.resolve import conflict
from engine.resolve import pipeline as pl
from engine.retrieve.scene import pc_id
from tests.engine.test_dm_tools import DM, in_turn, npc_here, to_play
from tests.engine.test_spec033_p1 import calls
from tests.engine.test_spec033_p2a import BASE, fixed

ROLL = {**BASE, "starts_fight": "", "fight_to": ""}  # the attack fields left blank


def chg(**kw: Any) -> dict[str, Any]:
    return {"tool": "change", "kind": "", "who": "", "what": "", "to": "", "name": "", "as": "none", "knows": "",
            "amount": 0, "note": "", **kw}


def stats(game: Any, r: Any) -> dict[str, Any]:
    tr = game.store.turn(str(r.turn_id))
    assert tr is not None
    return dict(tr.screen["dm_tools"])


def snap(game: Any, foe: str) -> tuple[Any, ...]:
    st = game.store.state
    pc = pc_id(st) or ""
    vit = st.quantities.get(foe, {}).get("vitality")
    return (conflict.record(st), conflict._band(st, pc, foe), conflict._band(st, foe, pc), vit.current if vit else None,
            st.time.mode, dict(st.meta))


# ------------------------------------------------------------------------------------------- the schema


def test_the_attack_fields_and_the_plain_position_descriptions_are_in_the_schema(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    tools = calls(dm_tools.step_schema(game.ctx, final=False))
    pr, ch = tools["propose_roll"], tools["change"]
    assert pr["starts_fight"]["enum"] == ["", "yes", "no"] and pr["fight_to"]["enum"] == ["", *conflict.BANDS]
    assert "the one who moves" in ch["who"]["description"] and "a band" in ch["to"]["description"]
    assert "other party" in ch["what"]["description"] and "short name" in ch["name"]["description"]


# ------------------------------------------------------------------------------------------- fix 1: fight start


def test_h05_a_grapple_with_no_band_on_record_starts_a_fight_at_engaged_and_logs_the_defaults(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""

    def go(ctx: Any, t: Any, tx: Any) -> tuple[str, list[str]]:
        out = dm_tools._propose_roll(ctx, t, {**ROLL, "verb": "verb.grapple", "target": npc, "change_kind": "restrain"})
        return out, t.stats["defaults"]

    out, defaults = in_turn(game, go)
    st = game.store.state
    assert out.startswith("A fight begins with") and "ROLL OFFERED" in out and "REFUSED" not in out
    assert conflict.active(st) and conflict.record(st)["foes"] == [npc]
    assert conflict._band(st, pc, npc) == "engaged" == conflict._band(st, npc, pc)
    assert "not_chosen:fight.starts" in defaults and "not_chosen:fight.to" in defaults
    assert "not_chosen:position" not in defaults  # the fight start wrote the band


@pytest.mark.parametrize(("verb", "extra"), [("verb.strike", {"change_kind": "harm"}), ("verb.force", {"force": "push"})])
def test_a_yes_starts_the_fight_at_the_stated_band_and_logs_nothing(tmp_path: Path, verb: str, extra: dict[str, Any]) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""

    def go(ctx: Any, t: Any, tx: Any) -> list[str]:
        dm_tools._propose_roll(ctx, t, {**ROLL, "verb": verb, "target": npc, "starts_fight": "yes", "fight_to": "close",
                                        "weapon": "unarmed", **extra})
        return t.stats["defaults"]

    defaults = in_turn(game, go)
    assert conflict.active(game.store.state) and conflict._band(game.store.state, pc, npc) == "close"
    assert not [d for d in defaults if d.startswith("not_chosen:fight") or d == "not_chosen:position"]


def test_no_is_a_single_blow_outside_a_fight_and_an_unrecorded_band_takes_engaged(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    out, defaults = in_turn(game, lambda ctx, t, tx: (dm_tools._propose_roll(
        ctx, t, {**ROLL, "verb": "verb.strike", "target": npc, "starts_fight": "no", "change_kind": "harm"}),
        t.stats["defaults"]))
    st = game.store.state
    assert out.startswith("ROLL OFFERED") and not conflict.active(st)
    assert conflict._band(st, pc, npc) == "engaged"  # fix 2: no band on record = an omitted detail
    assert "not_chosen:position" in defaults and not [d for d in defaults if d.startswith("not_chosen:fight")]


def test_a_ranged_strike_defaults_to_the_weapons_first_band_and_a_melee_one_to_engaged() -> None:
    from engine.data.loader import load_rules

    rules = load_rules()
    ctx: Any = SimpleNamespace(rules=rules, state=SimpleNamespace(entities={"item.bow": SimpleNamespace(tags=["item.weapon.bow.longbow"])}))
    assert dm_tools._reach_bands(ctx, "verb.strike", SimpleNamespace(weapon="item.bow")) == ["close", "near", "far"]
    assert dm_tools._reach_bands(ctx, "verb.strike", SimpleNamespace(weapon="unarmed")) == ["engaged"]
    assert dm_tools._reach_bands(ctx, "verb.grapple", SimpleNamespace(weapon=None)) == ["engaged"]


def test_other_verbs_and_things_start_no_fight(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)

    def go(ctx: Any, t: Any, tx: Any) -> None:
        dm_tools._propose_roll(ctx, t, {**ROLL, "verb": "verb.talk", "target": npc, "starts_fight": "yes"})

    in_turn(game, go)
    assert not conflict.active(game.store.state)


# ------------------------------------------------------------------------------------------- a fight that is already on


def test_attacks_in_a_live_fight_change_nothing_and_log_nothing(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    in_turn(game, lambda ctx, t, tx: dm_tools._fight(ctx, npc, pc, "engaged"))
    before = snap(game, npc)
    assert before[0] and before[1] == "engaged"
    for fields in ({"starts_fight": "yes", "fight_to": "far"}, {"starts_fight": ""}, {"starts_fight": "yes", "fight_to": "near"},
                   {"starts_fight": "no"}):
        def go(ctx: Any, t: Any, tx: Any, f: dict[str, Any] = fields) -> list[str]:
            note: list[str] = []
            dm_tools._attack_starts_fight(ctx, t, {**ROLL, **f}, "verb.strike", npc, SimpleNamespace(weapon="unarmed"), note)
            assert note == []
            return t.stats["defaults"]

        assert in_turn(game, go) == []
        assert snap(game, npc) == before  # no restart, no band reset, no Vitality reset, no new conflict


def test_a_newcomer_to_a_live_fight_joins_as_change_fight_joins_it(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    in_turn(game, lambda ctx, t, tx: dm_tools._fight(ctx, npc, pc, "engaged"))
    before = snap(game, npc)
    newcomer = in_turn(game, lambda ctx, t, tx: dm_tools._walk_on(ctx, "a guard", ctx.state.scene.place_id, "he", "the guard"))
    blow = {"starts_fight": "no"}  # one blow at the newcomer: he is not joined
    in_turn(game, lambda ctx, t, tx: dm_tools._attack_starts_fight(
        ctx, t, {**ROLL, **blow}, "verb.strike", newcomer, SimpleNamespace(weapon="unarmed"), []))
    assert conflict.record(game.store.state)["foes"] == [npc]
    note: list[str] = []
    in_turn(game, lambda ctx, t, tx: dm_tools._attack_starts_fight(
        ctx, t, {**ROLL, "starts_fight": "yes", "fight_to": "close"}, "verb.strike", newcomer,
        SimpleNamespace(weapon="unarmed"), note))
    st = game.store.state
    assert note == []  # no new fight begins; he joins the running one
    assert conflict.record(st)["foes"] == [npc, newcomer] and conflict._band(st, pc, newcomer) == "close"
    after = snap(game, npc)
    assert after[1:5] == before[1:5] and after[0]["previous"] == before[0]["previous"]  # the first foe and the mode untouched
    assert st.quantities[newcomer]["vitality"].current > 0  # joined with Vitality, as change fight gives it


def test_a_second_and_third_attack_across_turns_leave_the_fight_alone(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    game, model = to_play(tmp_path)
    npc = npc_here(game)
    monkeypatch.setattr(pl, "roll_check", fixed("failure"))
    seen: list[tuple[Any, ...]] = []
    for n, fields in enumerate(({"starts_fight": ""}, {"starts_fight": "yes", "fight_to": "far"}, {"starts_fight": "yes"})):
        model.push(DM, {"calls": [{**ROLL, "target": npc, "verb": "verb.strike", "change_kind": "harm", **fields}],
                        "passage": "Lead-up.", "said": [], "asks": []})
        r = game.submit(f"I strike {n}.")
        assert r.pause is not None and r.pause.kind == "offer"
        if n:
            assert not [d for d in stats(game, r)["defaults"] if d.startswith("not_chosen:fight")]
        else:
            assert "not_chosen:fight.starts" in stats(game, r)["defaults"]
        model.push(DM, {"calls": [], "passage": "Result.", "said": [], "asks": []},
                   {"foes": [{"foe": npc, "act": "wait", "target": "", "nonlethal": False}]},
                   {"calls": [], "passage": "Result.", "said": [], "asks": []})
        game.answer("commit")
        assert conflict.active(game.store.state)
        seen.append(snap(game, npc))
    assert seen[0][:3] == seen[1][:3] == seen[2][:3] and seen[0][4] == seen[2][4]  # record, both bands, mode
    assert seen[2][3] <= seen[0][3]  # Vitality never goes back up


# ------------------------------------------------------------------------------------------- fix 2: reach


def test_a_recorded_near_band_and_a_melee_strike_is_still_refused_with_the_one_call(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""

    def go(ctx: Any, t: Any, tx: Any) -> list[str]:
        conflict._set_band(tx, pc, npc, "near", "t")
        a = dm_tools._propose_roll(ctx, t, {**ROLL, "target": npc, "verb": "verb.strike", "starts_fight": "no"})
        b = dm_tools._propose_roll(ctx, t, {**ROLL, "target": npc, "verb": "verb.strike"})  # blank: the fight starts, near stays
        return [a, b]

    for out in in_turn(game, go):
        assert out.endswith("then make the attack.") and out.count("REFUSED: ") == 1
        assert f"`change kind=position who=pc to=engaged what={npc}`" in out and "near to the character" in out
    assert conflict._band(game.store.state, pc, npc) == "near"


def test_fight_to_near_then_a_melee_strike_is_refused(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    out = in_turn(game, lambda ctx, t, tx: dm_tools._propose_roll(
        ctx, t, {**ROLL, "target": npc, "verb": "verb.strike", "starts_fight": "yes", "fight_to": "near"}))
    assert "REFUSED" in out and "not in reach (near" in out and conflict.active(game.store.state)


# ------------------------------------------------------------------------------------------- fix 3: change position


EX = "For example: `change kind=position who=pc to=engaged what="


@pytest.mark.parametrize("call", [
    {"who": "pc", "what": "close", "to": "close"},                     # fighter25
    {"who": "@npc", "what": "engaged", "to": "engaged"},               # fighter25
    {"who": "", "what": "engaged", "to": "pc.calella_stoneby"},        # fighter25: `to` is neither a band nor a place
    {"who": "@npc", "what": "@npc", "to": "engaged"},                  # H01: a self-band
    {"who": "pc", "what": "pc", "to": "engaged"},
    {"who": "@npc", "what": "engaged", "to": "loc.the_tavern_yard"},   # H05: `what` is not a party
])
def test_swapped_or_self_referring_position_calls_are_refused_with_one_example(tmp_path: Path, call: dict[str, Any]) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    c = chg(kind="position", **{k: (npc if v == "@npc" else v) for k, v in call.items()})
    out = in_turn(game, lambda ctx, t, tx: dm_tools._change(ctx, t, c))
    assert out.startswith("REFUSED") and EX + npc in out, out
    st = game.store.state
    assert conflict._band(st, pc, npc) is None and conflict._band(st, npc, pc) is None  # nothing written


def test_the_example_call_is_accepted_and_pc_is_a_party(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)
    npc, pc = npc_here(game), pc_id(game.store.state) or ""
    outs = in_turn(game, lambda ctx, t, tx: [dm_tools._change(ctx, t, chg(kind="position", who="pc", to="engaged", what=npc)),
                                             dm_tools._change(ctx, t, chg(kind="position", who=npc, to="close", what="pc"))])
    assert all(o.startswith("done") for o in outs)
    assert conflict._band(game.store.state, pc, npc) == "close"


# ------------------------------------------------------------------------------------------- fix 3b: new_npc naming


def test_h01_the_wolfhound_lunges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The DM names the creature, then strikes it by that name: one creature, a fight at engaged, no refusal."""
    game, model = to_play(tmp_path)
    monkeypatch.setattr(pl, "roll_check", fixed("failure"))
    made = chg(kind="new_npc", what="a wolfhound, the size of a calf, lips pulled back", name="the wolfhound")
    made["as"] = "creature"
    hit = {**ROLL, "target": "the wolfhound", "verb": "verb.strike", "change_kind": "harm", "change_what": "the wolfhound"}
    model.push(DM, {"calls": [made, hit], "passage": "It lunges.", "said": [], "asks": []})
    r = game.submit("I wait.")
    st = game.store.state
    pc = pc_id(st) or ""
    hounds = [i for i, e in st.entities.items() if e.name == "the wolfhound"]
    assert len(hounds) == 1 and not [i for i, e in st.entities.items() if "wolfhound" in i and i not in hounds]
    assert r.pause is not None and r.pause.kind == "offer"  # not refused
    assert conflict.active(st) and conflict.record(st)["foes"] == hounds
    assert conflict._band(st, pc, hounds[0]) == "engaged"
    d = stats(game, r)["defaults"]
    assert "not_chosen:name" not in d and "not_chosen:position" not in d


def test_new_npc_tells_the_id_to_use_and_logs_a_missing_name(tmp_path: Path) -> None:
    game, _ = to_play(tmp_path)

    def go(ctx: Any, t: Any, tx: Any) -> tuple[str, str, list[str]]:
        a = dm_tools._change(ctx, t, {**chg(kind="new_npc", what="a ferryman", name="Odo"), "as": "he"})
        b = dm_tools._change(ctx, t, {**chg(kind="new_npc", what="a dog"), "as": "creature"})
        return a, b, t.stats["defaults"]

    a, b, d = in_turn(game, go)
    for out in (a, b):
        eid = out.split("someone new is here: ")[1].split(":")[0]
        assert out.endswith(f"Use {eid} for them from now on.")
    assert d.count("not_chosen:name") == 1
    st = game.store.state
    assert [e.name for e in st.entities.values() if e.name == "Odo"] == ["Odo"]
    assert len({i for i, e in st.entities.items() if e.name == "a dog"}) <= 1  # no fuzzy matching is added


# ------------------------------------------------------------------------------------------- fix 6: offline DM


def test_the_offline_dm_fills_the_attack_fields_and_states_no_move(tmp_path: Path) -> None:
    from engine.llm.base import Packet
    from engine.llm.offline import OfflineModel
    from tests.engine.test_spec033_p1 import validate

    game, _ = to_play(tmp_path)
    npc = npc_here(game)
    name = game.store.state.entities[npc].name
    schema = dm_tools.step_schema(game.ctx, final=False)
    msg = f"THE PLAYER'S MESSAGE\nI strike {name}.\n\nTOOL RESULTS THIS TURN\n(none yet)\n- {npc}: {name} (sly)"
    data = OfflineModel().fill(Role.DM, schema, Packet(instructions="", message=msg), turn_id=None, attempt=0).data
    assert validate(data, schema) == []
    (call,) = data["calls"]
    assert call["starts_fight"] == "yes" and call["fight_to"] == "engaged"
