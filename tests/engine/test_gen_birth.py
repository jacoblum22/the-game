"""PR-02-4 and PR-02-5 beyond the reference draws: the gift, recency, the Bent's gates and answers."""

from __future__ import annotations

import random
from typing import Any

import pytest

from engine.gen.birth import (
    BentState,
    answer_bent,
    bent_offer,
    birth_draw,
    circumstance_for,
    draw_slot,
    source_tags,
)

ATTRS = {"might": 1, "agility": 3, "endurance": 0, "wits": 1, "intellect": 0, "presence": 0, "resolve": 0}
FRAMES = {"deed.martial": 3}


def test_touched_gets_a_gift_and_an_element() -> None:
    src = source_tags("orig.people.human", "orig.up.wilds", "orig.life.touched", school="deed.primal.elements")
    circ = circumstance_for("orig.life.touched")
    assert circ == "gifted"
    d = birth_draw(random.Random(1), src, circ)
    assert [e.layer for e in d.entries] == ["gift", "knack", "quirk"] and d.rung == "marked"
    gift = d.entries[0]
    assert gift.id == "birth.gift.elements" and gift.element in ("fire", "water", "earth", "air")
    assert gift.gifted_ability and gift.gifted_ability.startswith("ab.") and gift.competence == {
        "tag": "deed.primal.elements", "value": 2}
    named = birth_draw(random.Random(1), src, circ, element="water")
    assert named.entries[0].gifted_ability == "ab.undertow"


def test_hard_childhood_biases_survival() -> None:
    src = source_tags("orig.people.human", "orig.up.wilds", "orig.life.soldier")
    plain = birth_draw(random.Random(5), src, "unremarked").log[1]
    hard = birth_draw(random.Random(5), src, "hard")
    assert hard.bias == "deed.wilds.survival" and hard.log[1].total_weight > plain.total_weight


def test_recent_entries_weigh_half() -> None:
    src = ["creature.folk.human"]
    _, base = draw_slot(random.Random(1), "quirk", src)
    _, recent = draw_slot(random.Random(1), "quirk", src, recent=["birth.quirk.iron_stomach"])
    assert recent.total_weight == 2 * base.total_weight - 2          # iron stomach (weight 2) counts 2, not 4


def test_bent_gates() -> None:
    rng = random.Random(7)
    kw: dict[str, Any] = dict(frames_by_branch=FRAMES, attributes=ATTRS, reflection=5, frames_total=20)
    assert bent_offer(rng, BentState(), window_locked=False, **kw)[1] is None          # window still open
    assert bent_offer(rng, BentState(status="accepted"), window_locked=True, **kw)[1] is None
    assert bent_offer(rng, BentState(), window_locked=True, first_reflection=6, **kw)[1] is None
    no_frames: dict[str, Any] = dict(kw, frames_by_branch={"deed.martial": 2})
    assert bent_offer(rng, BentState(), window_locked=True, **no_frames)[1] is None
    st, offer = bent_offer(rng, BentState(), window_locked=True, **kw)
    assert offer and offer.entry.attribute in ("might", "endurance") and "[CHOICE] Your Bent" in offer.text
    assert offer.entry.attribute != "agility"                                       # +3 is excluded
    assert bent_offer(rng, st, window_locked=True, **kw)[1] is None                    # an open offer is never re-drawn


def test_bent_accept_and_spacing() -> None:
    kw: dict[str, Any] = dict(frames_by_branch=FRAMES, attributes=ATTRS)
    st, offer = bent_offer(random.Random(2), BentState(), window_locked=True, reflection=3, frames_total=12, **kw)
    assert offer
    st2, eff = answer_bent(st, "accept", reflection=3, frames_total=12)
    assert st2.status == "accepted" and eff == {"effect_id": "eff.02.bent",
                                                "params": {"attribute": offer.entry.attribute, "amount": 1}}
    st3, eff = answer_bent(st, "defer", reflection=3, frames_total=12)
    assert eff is None and st3.struck == [offer.entry.id] and st3.deferrals == 1
    with pytest.raises(ValueError):
        answer_bent(st, "forgo", reflection=3, frames_total=12)                        # forgo only on the third draw
    r = random.Random(3)
    assert bent_offer(r, st3, window_locked=True, reflection=4, frames_total=40, **kw)[1] is None   # one reflection
    assert bent_offer(r, st3, window_locked=True, reflection=5, frames_total=21, **kw)[1] is None   # nine frames
    _, again = bent_offer(r, st3, window_locked=True, reflection=5, frames_total=22, **kw)
    assert again and again.entry.id != offer.entry.id and again.draw == 2
