"""Spec 020: the goal-first Reader (01.2.2, 01.2.6, DL-01-37, DL-01-39) and context per role (12.2.4, DL-12-104)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.data.loader import load_rules
from engine.dm.oof import goal_line
from engine.dm.packet import build_packet, identity_lines, view_ctx, view_for
from engine.dm.roles.reader import normalise, verbatim
from engine.llm.base import Role
from engine.resolve.types import Beat, Change
from tests.engine.test_packet import fact, scene_store

RULES = load_rules()


def _beat(verb: str, kind: str | None = None, target: str = "npc.d", **kw: Any) -> dict[str, Any]:
    return {"verb": verb, "method": verb.removeprefix("verb."), "purpose": "own_change", "pressure": "none",
            "against_will": False, "uses_power": False, "target": target,
            "change": {"kind": kind} if kind else None, **kw}


def _talk(**kw: Any) -> dict[str, Any]:
    return _beat("verb.talk", "learn", pressure="insistence", speech=True, **kw)


def _kinds(data: dict[str, Any]) -> list[tuple[Any, bool]]:
    return [((b.get("change") or {}).get("kind"), bool(b.get("against_will"))) for b in normalise(data)["beats"]]


# ---------------------------------------------------------------- F2: one beat per goal


def test_a_hold_that_serves_a_demand_is_the_demands_method() -> None:
    """I3 §6's five coercion messages: "I twist her arm: the word, Dunwen" is one `learn` beat, against her will."""
    grip = _beat("verb.grapple", "restrain", against_will=True, how="twist her arm up behind her back")
    out = normalise({"parts": [], "beats": [grip, _talk()]})
    assert _kinds({"parts": [], "beats": [grip, _talk()]}) == [("learn", True)]
    assert out["beats"][0]["how"] == "twist her arm up behind her back"  # the method's words, for the title
    marked = _beat("verb.strike", "harm", against_will=True, purpose="serves_another_act")
    assert _kinds({"parts": [], "beats": [marked, _talk()]}) == [("learn", True)]  # a blow the Reader marks


def test_two_goals_stay_two_beats() -> None:
    """01.2.2: "grab the purse and punch her" is take, then harm; a wanted blow, or a grip toward someone else, or a
    hold before no words, is its own goal."""
    take = _beat("verb.grapple", "take", against_will=True)
    punch = _beat("verb.strike", "harm", against_will=True)
    assert _kinds({"parts": [], "beats": [take, punch]}) == [("take", True), ("harm", True)]
    other = _beat("verb.grapple", "restrain", against_will=True, target="npc.child")
    assert _kinds({"parts": [], "beats": [other, _talk(target="npc.kerwin")]}) == [("restrain", True),
                                                                                   ("learn", False)]
    hold = _beat("verb.grapple", "restrain", against_will=True)
    assert _kinds({"parts": [], "beats": [hold]}) == [("restrain", True)]


def test_how_is_kept_only_when_it_is_the_players_words() -> None:
    msg = 'I twist her arm up behind her back and hiss, "The word, Dunwen."'
    assert verbatim("twist her arm up behind her back", msg) == "twist her arm up behind her back"
    assert verbatim("Twist  her ARM up", msg) == "Twist  her ARM up"  # case and spacing aside
    assert verbatim("demand she tell the word, saying she will be pursued", msg) is None  # I1 §3's garble
    assert verbatim(None, msg) is None


def _goal(**kw: Any) -> Beat:
    return Beat(**{"id": "beat.1", "actor": "pc.wren", "intent": "x", "method": "internal words", **kw})


def test_the_title_and_then_lines_render_from_the_typed_goal(tmp_path: Path) -> None:
    st = scene_store(tmp_path).state
    learn = _goal(change=Change(kind="learn", whom="npc.mara_voss"), target="npc.mara_voss",
                  how="twist my grip on her arm")
    assert goal_line(learn, st) == "Learn from Mara Voss: twist your grip on her arm"
    assert "internal words" not in goal_line(learn, st)  # never the Reader's raw `method` (DL-01-39)
    take = _goal(change=Change(kind="take", what="npc.tam_harlan"), target="npc.tam_harlan")
    assert goal_line(take, st) == "Take Tam Harlan"
    assert goal_line(_goal(verb="verb.talk", target="npc.mara_voss"), st) == "Talk to Mara Voss"
    bandits = _goal(change=Change(kind="harm", description="the bandits"), how="charge in")  # live run 143824
    assert goal_line(bandits, st) == "Hurt the bandits: charge in"
    assert goal_line(_goal(verb="verb.observe", intent="look around the quay"), st) == "Look around the quay"
    from engine.resolve.pipeline import BeatPlan, _then

    assert _then(st, [BeatPlan(beat=learn)]) == ["Learn from Mara Voss: twist your grip on her arm"]


# ---------------------------------------------------------------- F3: context per role


def test_identity_lines_name_pronouns_and_bond_present_or_absent(tmp_path: Path) -> None:
    """12.2.4 item 3: the narrator sees who an absent person named in the message is (I2 §2, §4)."""
    from tests.fixtures.game import entity

    store = scene_store(tmp_path)
    with store.transaction("turn.2") as tx:
        tx.add(entity("npc", "Ilse Varn", tx=tx, data={"pronouns": "she/her"}))
        tx.add(fact(tx, "pc.wren", "bond.anchor", {"npc": "npc.ilse_varn", "kind": "sister"}))
    st = store.state
    assert identity_lines(st, [], "Have you seen Ilse Varn?") == ["  - Ilse Varn: she/her; your sister"]
    assert identity_lines(st, ["pc.wren"]) == []  # never the PC
    assert identity_lines(st, ["npc.tam_harlan"]) == ["  - Tam Harlan: pronouns not recorded"]
    view = view_for(Role.NARRATOR, st, view_ctx('THE PLAYER\'S MESSAGE: "Where is Ilse Varn?"', []))
    assert "  - Ilse Varn: she/her; your sister" in view and "people here or named" in view


def test_the_lead_line_only_when_new_or_touched(tmp_path: Path) -> None:
    from tests.fixtures.game import entity

    store = scene_store(tmp_path)
    with store.transaction("turn.2") as tx:
        tx.add(entity("thread", "The levy called; folk say it is only the beginning.", tx=tx,
                      data={"status": "active"}))
    st = store.state
    tid = next(i for i, e in st.entities.items() if e.kind == "thread")
    new = view_for(Role.NARRATOR, st, view_ctx("I look at the boats.", []))
    assert tid in new  # introduced now: new this turn
    later = store.state.model_copy(update={"time": st.time.model_copy(update={
        "now": st.time.now.model_copy(update={"day": st.time.now.day + 1})})})
    assert tid not in view_for(Role.NARRATOR, later, view_ctx("I look at the boats.", []))
    assert tid in view_for(Role.NARRATOR, later, view_ctx("What is this levy everyone talks about?", []))
    assert tid in view_for(Role.DIRECTOR, later, view_ctx("I look at the boats.", []))  # the Director keeps all


def test_director_and_world_get_their_exchanges(tmp_path: Path) -> None:
    store = scene_store(tmp_path)
    talk = [(f"p{i}", f"d{i}") for i in range(5)]
    for role, n in ((Role.DIRECTOR, 2), (Role.WORLD, 1), (Role.NARRATOR, 4)):
        p = build_packet(role, instructions="", cards=[], view=store.state, exchanges=talk, message="m", rules=RULES)
        assert len(p.exchanges) == n, role
