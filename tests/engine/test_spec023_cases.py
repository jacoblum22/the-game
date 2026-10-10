"""Spec 023's labelled made-up and edge cases (C1-C29, specs/023-question-owners-goal-time/spec.md), each against a
small scene built from events, with a stub Framer (no model): one owner per question (T1), the goal flows through
(T5), take the time (T6), OFFER wording (P2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from engine import ids
from engine.data.loader import load_rules
from engine.dm.oof import fact_short, near_miss_choices, offer_block
from engine.dm.roles.framer import beat_message
from engine.dm.turn import not_oracle
from engine.resolve.change import apply_change, typed_goal
from engine.resolve.costs import first_fitting_cost
from engine.resolve.frame import frame_check
from engine.resolve.gate import GateDecision, check_gate
from engine.resolve.necessity import certain_talk, costly
from engine.resolve.oracle import MIRROR, positive
from engine.resolve.pipeline import BeatPlan, PipelineEnv, resume, run_beats
from engine.resolve.types import Beat, Change, CostDecl, Frame, Obstacle, ProposedFrame
from engine.store.clocks import create_clock
from engine.store.events import Event, SceneRecord
from engine.time.clock import ROUNDS, to_rounds
from engine.time.scheduler import TimeContext, set_mode
from tests.engine.test_turn_adjudication import D20
from tests.fixtures.game import new_store
from tests.fixtures.scene_dock import WATCH_CLOCK, _entity, _fact

RULES = load_rules()
ATTR = {"verb.talk": "presence", "verb.observe": "wits", "verb.move": "agility", "verb.strike": "might",
        "verb.handle": "agility", "verb.sneak": "agility", "verb.help": "presence", "verb.exert": "might",
        "verb.recall": "intellect"}


@dataclass
class Room:
    store: Any
    rng: D20
    pc: str = ""
    ids: dict[str, str] = field(default_factory=dict)

    @property
    def state(self) -> Any:
        return self.store.state

    def __getitem__(self, k: str) -> str:
        return self.ids[k]


def room(tmp_path: Path, *, letters: bool = False, clock: bool = False, unfriendly: bool = False) -> Room:
    """Ada's lodging-house: a clerk at a ledger, a smith, an old friend, Belie the scribe, a guard by the door."""
    store = new_store(tmp_path)
    r = Room(store=store, rng=D20.of(store))
    STATE[:] = [r]
    with store.transaction("turn.0") as tx:
        tctx = TimeContext(tx, RULES, r.rng)
        place = r.ids["place"] = _entity(tx, "place", "The Lodging House", data={"place_kind": "inn"})
        lic = ("lic.lang.common", "lic.lang.letters") if letters else ("lic.lang.common",)
        r.pc = _entity(tx, "pc", "Ada", data={"attributes": {"might": 1, "agility": 1, "endurance": 1, "wits": 0,
                                                              "intellect": 1, "presence": 2, "resolve": 0},
                                               "competence": {}, "pronouns": "she/her"},
                       quantities={"vitality": (12, 0, 12), "coin": (10, 0, 999)}, licences=lic)
        people = {"clerk": ("Odo Penn", "clerk of the river guild", ("lic.lang.common", "lic.lang.letters")),
                  "smith": ("Bram Hollis", "blacksmith", ("lic.training.craft_smithing",)),
                  "friend": ("Wynn Dale", "carter, an old friend you saved last week", ()),
                  "belie": ("Belie Greenwort", "scribe and teacher of letters", ("lic.lang.letters",)),
                  "guard": ("Tolly Marsh", "door guard", ())}
        for k, (name, role, held) in people.items():
            r.ids[k] = _entity(tx, "npc", name, data={"role": role, "pronouns": "he/him",
                                                      "attributes": {"wits": 1, "presence": 1, "resolve": 1},
                                                      "defenses": {"notice": 11}}, licences=held)
        for k, name in (("ledger", "Ledger"), ("book", "Book of Hours"), ("dummy", "Straw Dummy"),
                        ("strongbox", "Strongbox"), ("list", "Delivery List")):
            r.ids[k] = _entity(tx, "item", name, data={})
        r.ids["door"] = _entity(tx, "object", "Back Door", data={})
        _fact(tx, r["ledger"], "text", "debts owed to the river guild")
        r.ids["suspicious"] = _fact(tx, r["clerk"], "suspicious_of", "strangers asking about the guild")
        r.ids["rope"] = _fact(tx, "world", "rope_in_the_loft", True)
        for e in (r.pc, *[r[k] for k in people]):
            tx.add(Event.of("position_set", source="fixture", rule_id="10.1.1", entity=e, location=place))
        sid = tx.mint(ids.SCENE)
        tx.add(Event.of("scene_started", source="fixture", rule_id="PR-12-7", scene_id=sid,
                        scene=SceneRecord(scene_id=sid, place_id=place, mode="site", agenda="What is in the ledger?",
                                          hoped_answer="yes", cast_present=[r[k] for k in people],
                                          started_seq=tx.state.last_seq)))
        set_mode(tctx, "site", "a lodging house is a site")
        if clock:
            tx.add(create_clock(tx.state, WATCH_CLOCK, name="The watch makes its round", owner="12",
                                rule_id="PR-12-7"))
        if unfriendly:
            tx.add(Event.of("relationship_set", source="fixture", rule_id="15.1.1", a=r["guard"], b=r.pc,
                            kind="standing", steps=-2, new_value=-2, reason="fixture"))
    return r


SEEN: list[tuple[Beat, GateDecision]] = []
STATE: list[Room] = []  # the room the stub Framer reads (for the rule's first fitting cost)


def framer(**over: Any) -> Any:
    """A fixed proposal (Safe, sourceless, Moderate, a time cost unless `over` says otherwise); records what it saw."""
    def propose(beat: Beat, candidates: list[str], *, gate: GateDecision, note: str | None = None) -> ProposedFrame:
        SEEN.append((beat, gate))
        verb = gate.verb or beat.verb or ""
        anchor = next((c for c in candidates if verb.split(".")[-1] in c), candidates[0])
        src = over.get("stakes_source", "none")
        tc = first_fitting_cost(RULES, role="threatened", state=STATE[0].state, actor=beat.actor, stakes_source=src,
                                target=beat.target, declared_seq=beat.declared_seq or None)
        base: dict[str, Any] = {"anchor": anchor, "attribute": ATTR.get(verb, "wits"),
                                "obstacle": Obstacle(kind="tier", obstacle_class="other", tier="moderate", id="obs.t"),
                                "stakes_source": "none", "threatened_cost": tc}
        if src != "none":
            base["alternate_cost"] = first_fitting_cost(RULES, role="alternate", other=over.get("threatened_cost", tc),
                                                        state=STATE[0].state, actor=beat.actor, stakes_source=src,
                                                        target=beat.target, declared_seq=beat.declared_seq or None)
        return ProposedFrame(**{**base, **over})

    return propose


def mk(r: Room, intent: str, verb: str, *, target: str | None = None, change: Change | None = None,
       **kw: Any) -> Beat:
    return Beat(id=f"beat.{len(SEEN)}{intent[:3]}", actor=r.pc, intent=intent, method=kw.pop("method", intent),
                verb=verb, target=target, change=change, declared_seq=r.state.last_seq, **kw)


def run(r: Room, b: Beat, fr: Any = None, turn: str = "turn.1", **env: Any) -> Any:
    with r.store.transaction(turn) as tx:
        e = PipelineEnv(tx=tx, rules=RULES, rng=r.rng, store=r.store, framer=fr or framer(), pc=r.pc, **env)
        return run_beats(e, [BeatPlan(beat=b, intent_verbs=[intent_verb(b)])])


def intent_verb(b: Beat) -> str:
    return (b.verb or "verb.observe").split(".")[-1]


def frame_of(r: Room, b: Beat, **over: Any) -> Frame:
    typed_goal(r.state, b)
    g = check_gate(b, state=r.state, rules=RULES)
    from engine.retrieve.anchors import anchor_candidates

    cands = anchor_candidates({**b.model_dump(), "intent_verbs": [intent_verb(b)]}, r.state, RULES)
    out = frame_check(framer(**over)(b, cands, gate=g), b, state=r.state, rules=RULES, gate=g, candidates=cands)
    assert isinstance(out, Frame), out
    return out


# ------------------------------------------------------------------------------------------- T1: one owner


def test_c1_the_smiths_ability_is_his_record_never_a_coin_flip(tmp_path: Path) -> None:
    """C1 made-up: "mend my sword" with the Reader's "can the smith work iron?": no draw; an Oracle fact on record
    about him is never offered as a snag, and frame_check refuses one."""
    r = room(tmp_path)
    smith = r["smith"]
    assert not_oracle(r.state, smith, "can work iron", [smith])
    with r.store.transaction("turn.1") as tx:
        fid = tx.mint(ids.FACT)
        tx.add(Event.of("fact_set", {"source": "oracle"}, source="dm", rule_id="01.15.5", fact_id=fid, subject=smith,
                        predicate="can_work_iron", value=False, visibility="shown"))
    b = mk(r, "Bram mends my sword", "verb.talk", target=smith, speech=True,
           change=Change(kind="persuade_to", what=smith))
    from engine.dm.schemas import schema_context

    assert fid not in (schema_context(r.state, RULES, beat=b).snag_fact_ids or [])
    with pytest.raises(AssertionError, match="never a snag"):
        frame_of(r, b, snags=[fid], obstacle=Obstacle(kind="opposed", entity=smith))
    from engine.dm.packet import view_ctx, view_for
    from engine.llm.base import Role

    framer_view = view_for(Role.FRAMER, r.state, view_ctx(b.intent, (), [smith], b))  # spec 026: the people card
    assert "Smithing" in framer_view and "can:" in framer_view


def test_c2_an_old_friends_will_is_willingness(tmp_path: Path) -> None:
    """C2 made-up: "is she willing to help?" about the friend present is never drawn."""
    r = room(tmp_path)
    assert not_oracle(r.state, r["friend"], "is willing to help", [r["friend"]])
    assert not_oracle(r.state, r["friend"], "is willing to help", [])  # present, even when not the target


@pytest.mark.parametrize("phrasing", ["sweet-talk the clerk and sneak a look at the ledger",
                                      "sweet-talk the clerk and peek at the ledger"])
def test_c3_c11_reading_folded_into_talk_meets_letters(tmp_path: Path, phrasing: str) -> None:
    """C3, C11 made-up: the reading is gated (G3, Letters) folded into a Talk beat or as its own look."""
    r = room(tmp_path)
    folded = mk(r, "learn what the ledger says", "verb.talk", target=r["clerk"], speech=True, method=phrasing,
                change=Change(kind="learn", what=r["ledger"], whom=r["clerk"]))
    split = mk(r, "learn what the ledger says", "verb.observe", target=r["ledger"], method=phrasing.split(" and ")[1],
               change=Change(kind="learn", what=r["ledger"]))
    for b in (folded, split):
        g = check_gate(b, state=r.state, rules=RULES)
        assert g.gate == "G3" and g.redirect is not None and g.redirect.missing == "lic.lang.letters", (b.verb, g)


def test_c14_asking_someone_else_to_read_is_their_act(tmp_path: Path) -> None:
    """C14 made-up: "ask Belie to read the list for me" (her act): no Letters gate on Ada."""
    r = room(tmp_path)
    b = mk(r, "Belie reads the delivery list for Ada", "verb.talk", target=r["belie"], speech=True,
           method="ask her to read the list for me", change=Change(kind="persuade_to", what=r["belie"]))
    assert check_gate(b, state=r.state, rules=RULES).gate == "G1"


def test_c4_shouldering_past_the_guard_moves_you(tmp_path: Path) -> None:
    """C4 made-up: a Move left `none` is typed `move_to` the door; with the guard hostile it rolls, and success puts Ada
    beside the door."""
    r = room(tmp_path, unfriendly=True)
    b = mk(r, "reach the back door", "verb.move", target=r["door"], method="shoulder past the guard")
    res = run(r, b, framer(obstacle=Obstacle(kind="tier", obstacle_class="obstructed", id="obs.door"),
                           stakes_source="aware_opponent_or_observer"))  # the Framer names the hostile guard
    assert b.change is not None and b.change.kind == "move_to" and b.change.what == r["door"]
    assert res.pause is not None and res.pause.detail["stage"] == "offer"
    r.rng.faces = [20]
    with r.store.transaction("turn.2") as tx:
        e = PipelineEnv(tx=tx, rules=RULES, rng=r.rng, store=r.store, framer=framer(), pc=r.pc)
        out = resume(e, r.state.open_pause(), "commit")
    assert out.outcomes[0].entry.positions and "Back Door" in out.outcomes[0].entry.positions[0].words


def test_live_a_move_within_the_place_here_is_titled_by_its_spot(tmp_path: Path) -> None:
    """Live run 20261009-204702 turn 9 (found after implementing): "edge closer to the quarrel" typed `move_to` the
    inn the PC was in, with the spot as its description; the OFFER read "Go to the Golden Plough"."""
    from engine.dm.oof import goal_line

    r = room(tmp_path)
    b = mk(r, "be at the back of the crowd", "verb.move", method="edge closer",
           change=Change(kind="move_to", what=r["place"], description="the back of the crowd around the quarrel"))
    assert goal_line(b, r.state).startswith("Go to the back of the crowd around the quarrel")


def test_c12_a_joke_and_a_slip_past_is_typed(tmp_path: Path) -> None:
    """C12 made-up: "I tell the guard a joke and slip past": the Sneak is typed `hide` from the guard, never `none`."""
    r = room(tmp_path)
    b = mk(r, "slip past the guard", "verb.sneak", target=r["guard"], method="tell the guard a joke and slip past")
    typed_goal(r.state, b)
    assert b.change is not None and (b.change.kind, b.change.what, b.change.whom) == ("hide", r.pc, r["guard"])


def test_c13_a_question_about_someone_here_is_theirs(tmp_path: Path) -> None:
    """C13 made-up: the player's own "Can the smith work iron?" with him present: no draw (his record answers)."""
    r = room(tmp_path)
    assert not_oracle(r.state, r["smith"], "can work iron", [])
    assert not_oracle(r.state, r.pc, "can read the ledger")  # the PC's own ability: the sheet
    assert not not_oracle(r.state, r.pc, "is there a well here")  # a world question filed under the PC


def test_c9_c20_a_world_question_is_the_oracles_and_never_a_snag(tmp_path: Path) -> None:
    """C9, C20 edge: "is there a rope in the loft?" may be drawn; its answer is never a snag (refused) but may be a
    lever on a later beat."""
    r = room(tmp_path)
    assert not not_oracle(r.state, "world", "is there a rope in the loft")
    with r.store.transaction("turn.1") as tx:
        fid = tx.mint(ids.FACT)
        tx.add(Event.of("fact_set", {"source": "oracle"}, source=r.pc, rule_id="01.15.5", fact_id=fid,
                        subject="world", predicate="is_there_a_rope_in_the_loft", value=True, visibility="shown"))
    b = mk(r, "climb up to the loft", "verb.exert", target=r["place"], method="climb the beam with the rope")
    with pytest.raises(AssertionError, match="never a snag"):
        frame_of(r, b, snags=[fid])
    assert frame_of(r, b, levers=[fid]).levers[0].fact_id == fid


def test_c16_a_negated_question_is_asked_and_labelled_positive(tmp_path: Path) -> None:
    """C16 edge: "is the gate not barred?" is asked as "is the gate barred" at the mirrored odds; an old negated
    record reads once ("is alert", never "is not not alert")."""
    assert positive("is the gate not barred") == ("is the gate barred", True)
    assert positive("can't read the writing") == ("can read the writing", True)
    assert positive("is alert") == ("is alert", False)
    assert MIRROR["unlikely"] == "likely" and MIRROR["likely"] == "unlikely"
    r = room(tmp_path)
    with r.store.transaction("turn.1") as tx:
        old, new = tx.mint(ids.FACT), tx.mint(ids.FACT)
        tx.add(Event.of("fact_set", {"source": "oracle"}, source="dm", rule_id="01.15.5", fact_id=old,
                        subject=r["guard"], predicate="is_not_alert_to_a_hand_in_his_pocket", value=False,
                        visibility="shown"))
        tx.add(Event.of("fact_set", {"source": "oracle"}, source="dm", rule_id="01.15.5", fact_id=new,
                        subject=r["door"], predicate="is_barred", value=False, visibility="shown"))
    assert fact_short(r.state, old) == "Tolly is alert to a hand in his pocket"
    assert fact_short(r.state, new).endswith("Back Door is not barred")


def test_c19_content_is_never_a_yes_no(tmp_path: Path) -> None:
    """C19 edge (adversarial): "how much does the job pay" sent to the Oracle is dropped: answered in words."""
    r = room(tmp_path)
    assert "content" in not_oracle(r.state, "world", "how much the job pays")
    assert not_oracle(r.state, "world", "where the ferryman was last seen")


# ------------------------------------------------------------------------------------------- T5: the goal


def test_c18_a_secret_frame_needs_a_learn_goal(tmp_path: Path) -> None:
    """C18 edge (adversarial): the Framer marks a persuade frame secret: it is not."""
    r = room(tmp_path)
    b = mk(r, "Odo opens the strongbox for me", "verb.talk", target=r["clerk"], speech=True,
           change=Change(kind="persuade_to", what=r["clerk"]))
    f = frame_of(r, b, secret=True, obstacle=Obstacle(kind="opposed", entity=r["clerk"]))
    assert not f.secret
    look = mk(r, "find a hidden catch on the strongbox", "verb.observe", target=r["strongbox"])
    assert frame_of(r, look, secret=True).secret


def test_c21_certain_talk_keys_on_the_words_not_the_verb(tmp_path: Path) -> None:
    """C21 edge: a plain question to a Neutral NPC labelled Help, with words, is certain; a Talk label without words
    is not."""
    r = room(tmp_path)
    helped = mk(r, "learn where the guild meets", "verb.help", target=r["clerk"], speech=True, asks=True,
                change=Change(kind="learn", what=r["clerk"]))
    assert certain_talk(helped, "verb.help", r.state)
    mute = mk(r, "learn where the guild meets", "verb.talk", target=r["clerk"], asks=True,
              change=Change(kind="learn", what=r["clerk"]))
    assert not certain_talk(mute, "verb.talk", r.state)


def test_c10_a_price_that_undoes_the_goal_is_never_the_close_call(tmp_path: Path) -> None:
    """C10 edge: picking the strongbox open: "the guard hears you" is a close-call price; "the lock jams shut again"
    is not offered as one (another price is named)."""
    r = room(tmp_path, clock=True)
    b = mk(r, "open the strongbox", "verb.handle", target=r["strongbox"], method="work the lock with a pin",
           change=Change(kind="open", what=r["strongbox"]))
    f = frame_of(r, b, stakes_source="listening_clock",
                 threatened_cost=CostDecl(menu_id="cost.exposure", form_intent="the guard hears you"),
                 alternate_cost=CostDecl(menu_id="cost.time", form_intent="the lock jams shut again"))
    labels = [c["label"] for c in near_miss_choices(f, RULES)]
    assert any("the guard hears you" in x for x in labels if x.startswith("Succeed"))
    assert not any("jams shut" in x for x in labels if x.startswith("Succeed"))


def test_c10b_a_closed_door_on_the_person_persuaded_is_never_the_close_call(tmp_path: Path) -> None:
    """Talker t12's shape, made up: buying the clerk a drink, the close call never prices "he turns you down"."""
    r = room(tmp_path)
    b = mk(r, "Odo takes the drink and talks", "verb.talk", target=r["clerk"], speech=True,
           change=Change(kind="persuade_to", what=r["clerk"]))
    f = frame_of(r, b, obstacle=Obstacle(kind="opposed", entity=r["clerk"]),
                 threatened_cost=CostDecl(menu_id="cost.closed_door", form_intent="he turns the round down"))
    sac = [c for c in near_miss_choices(f, RULES) if c["id"].startswith("success_at_cost")]
    assert sac and all("closed_door" not in c["id"] for c in sac), sac


def test_c17_a_fallback_is_framed_on_its_own_scope_and_takes_the_time(tmp_path: Path) -> None:
    """C17 edge: Ada (no Letters) accepts the crude fallback; the Framer rates the fallback's own scope; at Moderate
    + 5 with nothing at stake it takes the time, at its reach cap (DL-01-46, provisional)."""
    r = room(tmp_path)
    SEEN.clear()
    b = mk(r, "learn what the ledger says", "verb.observe", target=r["ledger"], method="read the ledger",
           change=Change(kind="learn", what=r["ledger"]))
    res = run(r, b)
    assert res.pause is not None and res.pause.detail["stage"] == "redirect"
    with r.store.transaction("turn.2") as tx:
        e = PipelineEnv(tx=tx, rules=RULES, rng=r.rng, store=r.store, framer=framer(), pc=r.pc)
        out = resume(e, r.state.open_pause(), "accept:lic.lang.letters")
    seen, gate = SEEN[-1]
    assert seen.intent.startswith("pick out numerals") and "learn what the ledger says" not in beat_message(seen, gate)
    o = out.outcomes[0]
    assert o.status == "no_roll" and o.entry.reach == "limited" and r.state.open_pause() is None
    assert "take the time" in o.oof[0]["text"]


def test_c7_very_hard_rolls_even_with_nothing_at_stake(tmp_path: Path) -> None:
    """C7 edge: a sourceless Safe frame at Very hard, and a fallback whose shift lands at Very hard, both roll."""
    r = room(tmp_path)
    b = mk(r, "find the ring in my room", "verb.observe", target=r["place"])
    res = run(r, b, framer(obstacle=Obstacle(kind="tier", obstacle_class="other", tier="very_hard", id="obs.v")))
    assert res.pause is not None and res.pause.detail["stage"] == "offer"
    r2 = room(tmp_path / "b")
    ledger = mk(r2, "learn what the ledger says", "verb.observe", target=r2["ledger"], method="read the ledger",
                change=Change(kind="learn", what=r2["ledger"]))
    run(r2, ledger)
    with r2.store.transaction("turn.2") as tx:
        e = PipelineEnv(tx=tx, rules=RULES, rng=r2.rng, store=r2.store, pc=r2.pc,
                        framer=framer(obstacle=Obstacle(kind="tier", obstacle_class="other", tier="hard", id="o.h")))
        out = resume(e, r2.state.open_pause(), "accept:lic.lang.letters")
    assert out.pause is not None and out.pause.detail["stage"] == "offer"  # hard 20 + 5 = 25: it rolls
    assert out.pause.detail["frame"]["dc"] == 25  # the shift is counted once


# ------------------------------------------------------------------------------------------- T6: take the time


@pytest.mark.parametrize(("intent", "verb", "key", "method"), [
    ("find my dropped ring", "verb.observe", "place", "search my room for the ring"),
    ("practise my cuts", "verb.strike", "dummy", "hack at the straw dummy"),
    ("learn what the book says", "verb.observe", "book", "read my own book by the fire"),
])
def test_c5_nothing_at_stake_takes_the_time(tmp_path: Path, intent: str, verb: str, key: str, method: str) -> None:
    """C5 made-up: searching your own room, practising on a dummy, reading your own book: no OFFER, no roll, two
    intervals spent, and the RESULT says so (never "hidden check made")."""
    r = room(tmp_path, letters=True)
    before = r.state.time.now
    b = mk(r, intent, verb, target=r[key], method=method)
    res = run(r, b)
    o = res.outcomes[0]
    assert res.pause is None and o.status == "no_roll" and o.entry.gate_words == "no roll: take_the_time"
    assert not r.state.frames  # nothing committed, nothing rolled
    assert to_rounds(r.state.time.now) - to_rounds(before) == 2 * ROUNDS["interval"]  # 01.4.4: twice the site time
    assert o.oof and "take the time" in o.oof[0]["text"] and "hidden" not in o.oof[0]["text"]


def test_c26_a_secret_frame_with_nothing_at_stake_takes_the_time(tmp_path: Path) -> None:
    """C26 edge: a secret look with nothing at stake takes the time; no "hidden check made"."""
    r = room(tmp_path)
    o = run(r, mk(r, "find a hidden catch", "verb.observe", target=r["strongbox"]), framer(secret=True)).outcomes[0]
    assert o.status == "no_roll" and "hidden check made" not in o.oof[0]["text"]


def test_c28_a_time_cost_cited_to_an_unrelated_fact_still_takes_the_time(tmp_path: Path) -> None:
    """C28 edge (explorer t12): `cost.time` cited to a place fact is no stakes source; time is what taking it pays."""
    r = room(tmp_path)
    fr = framer(threatened_cost=CostDecl(menu_id="cost.time", source_fact=r["rope"]))
    assert run(r, mk(r, "listen to the room", "verb.observe", target=r["place"]), fr).outcomes[0].status == "no_roll"


def test_c6_a_sourced_cost_with_source_none_is_costly_and_noted(tmp_path: Path) -> None:
    """C6 edge: stakes.source none but a closed door cited to the clerk's suspicion: costly, an OFFER, the
    disagreement noted on the frame."""
    r = room(tmp_path)
    b = mk(r, "open the strongbox", "verb.handle", target=r["strongbox"], change=Change(kind="open", what=r["strongbox"]))
    fr = framer(threatened_cost=CostDecl(menu_id="cost.closed_door", source_fact=r["suspicious"]))
    res = run(r, b, fr)
    assert res.pause is not None and res.pause.detail["stage"] == "offer"
    assert any("stakes.source none, but costly" in n for n in res.pause.detail["frame"]["notes"])


@pytest.mark.parametrize("case", ["c22_conflict", "c23_unfriendly_watcher", "c27_clock"])
def test_c22_c23_c27_costly_frames_roll(tmp_path: Path, case: str) -> None:
    """C22, C23, C27 edge: in a conflict, with an Unfriendly watcher the Framer names as the source, or with a clock
    listening: costly. (C23 as amended: whether a bystander would act on this failure is the Framer's stakes source,
    01.6.9; an Unfriendly bystander it does not name leaves the frame to take the time, as explorer t12 shows.)"""
    r = room(tmp_path, clock=case.endswith("clock"), unfriendly=case.endswith("watcher"))
    if case.endswith("conflict"):
        with r.store.transaction("turn.0b") as tx:
            set_mode(TimeContext(tx, RULES, r.rng), "conflict", "a fight")
    src = {"stakes_source": "aware_opponent_or_observer"} if case.endswith("watcher") else {}
    f = frame_of(r, mk(r, "search the room", "verb.observe", target=r["place"]), **src)
    assert costly(f, state=r.state, rules=RULES, source=src.get("stakes_source", "none"))
    if case.endswith("watcher"):  # not named by the Framer: the bystander alone does not make it costly
        assert not costly(frame_of(r, mk(r, "search the room", "verb.observe", target=r["place"])), state=r.state,
                          rules=RULES)


def test_c8_c15_an_agreement_on_record_covers_a_smaller_ask_and_is_never_shrunk(tmp_path: Path) -> None:
    """C8, C15 edge: the friend agreed to more; a smaller ask (the Framer cites the agreement) takes no roll and
    leaves the agreement as it was; a larger ask's limited success is added, never replacing it."""
    r = room(tmp_path)
    friend = r["friend"]
    with r.store.transaction("turn.0c") as tx:
        agreed = tx.mint(ids.FACT)
        tx.add(Event.of("fact_set", {"source": "ruling"}, source="beat.0", rule_id="01.2.7", fact_id=agreed,
                        subject=friend, predicate="agreed", value="Wynn lets Ada hear the refugees' story from them",
                        visibility="shown"))
    small = mk(r, "Wynn lets Ada sit near the refugees and listen", "verb.help", target=friend, speech=True,
               change=Change(kind="persuade_to", what=friend))
    res = run(r, small, framer(already_agreed=agreed, obstacle=Obstacle(kind="opposed", entity=friend)))
    assert res.outcomes[0].status == "no_roll" and res.pause is None
    assert r.state.current_fact_id(friend, "agreed") == agreed
    bigger = mk(r, "Wynn takes Ada to the refugees tonight", "verb.talk", target=friend, speech=True,
                change=Change(kind="persuade_to", what=friend))
    with r.store.transaction("turn.2") as tx:
        apply_change(tx, RULES, bigger, 1, pc=r.pc, limit="tonight")
    now = r.state.fact_value(friend, "agreed")
    assert "hear the refugees' story" in now and "takes Ada to the refugees tonight, but not tonight" in now
    assert "a smaller part" not in now


def test_c29_a_safe_frame_that_stays_costly_still_auto_commits(tmp_path: Path) -> None:
    """C29 edge: a Safe frame that is a contest (the clerk can refuse) stays costly: with auto-commit on it rolls at
    once, labelled auto (01.7.4)."""
    r = room(tmp_path)
    b = mk(r, "Odo shows me the guild's rota", "verb.talk", target=r["clerk"], speech=True,
           change=Change(kind="persuade_to", what=r["clerk"]))
    r.rng.faces = [15]
    res = run(r, b, framer(obstacle=Obstacle(kind="opposed", entity=r["clerk"])), auto_commit=True)
    assert res.outcomes[0].status == "resolved" and "OFFER — auto" in res.outcomes[0].oof[0]["text"]


# ------------------------------------------------------------------------------------------- P2: wording


def test_c24_limited_reach_needs_a_cited_factor_and_the_offer_names_it(tmp_path: Path) -> None:
    """C24 edge: no cited factor: Standard; with one: Limited, and the OFFER names it."""
    r = room(tmp_path, clock=True)
    b = mk(r, "search the room", "verb.observe", target=r["place"])
    assert frame_of(r, b, stakes_source="listening_clock").reach == "standard"
    f = frame_of(r, b, stakes_source="listening_clock", reach_limit="the cellar below: one lamp")
    assert f.reach == "limited" and "the cellar below: one lamp" in offer_block(f, rules=RULES, state=r.state).text


def test_c25_no_zero_terms_and_no_generic_practised(tmp_path: Path) -> None:
    """C25 edge: Wits 0 and the PC's floor competence: no "+0", no "practised"; a Safe frame says a plain failure
    loses nothing and names failing badly's price."""
    r = room(tmp_path, clock=True)
    f = frame_of(r, mk(r, "search the room", "verb.observe", target=r["place"]), stakes_source="listening_clock",
                 deed_tag="deed.lore")
    text = offer_block(f, rules=RULES, state=r.state).text
    assert "+0" not in text and "practised" not in text and "Wits" not in text, text
    safe = frame_of(r, mk(r, "search the room", "verb.observe", target=r["place"]))
    assert "If it fails: nothing lost." in offer_block(safe, rules=RULES, state=r.state).text
