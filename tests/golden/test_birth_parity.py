"""T053: the birth draw and the Bent reproduce chapter 02's reference draws.

Reference: `rules/_process/simulation/02-gen_data02/draws02.py` (the draws behind the chapter's worked examples)
and its committed output `draws02-output.txt`. The same cases are run through `engine.gen.birth` with the same
seeds; pool size, total weight, roll, band and entry must match line for line.
"""

from __future__ import annotations

import contextlib
import io
import random
import re
from types import ModuleType

import pytest

from engine.gen.birth import (
    BentState,
    Circumstance,
    answer_bent,
    bent_offer,
    birth_draw,
    draw_slot,
    source_tags,
)
from engine.gen.build_tables import SIM, load_module

REF_DIR = SIM / "02-gen_data02"
# draws02.py's cases: (name, source tags, circumstance, seed)
Case = tuple[str, list[str], Circumstance, int]
PRIMAL = ["deed.primal." + s for s in ("growth", "beastkin", "weather", "shapeshifting", "spirits", "elements", "hexcraft")]
CASES: list[Case] = [
    ("Wren", ["creature.folk.human", "deed.wilds", "deed.martial", "terrain.forest", "terrain.highland"], "unremarked", 2001),
    ("Bram", ["creature.folk.human", "deed.wilds", "deed.influence", "terrain.road", "terrain.settlement.camp", "deed.martial"],
     "unremarked", 2002),
    ("Thessaly", ["creature.folk.goblin", "deed.guile", "deed.lore", "deed.craft", "terrain.settlement.hold",
                  "terrain.ruin.temple", "deed.divine"], "hard", 2003),
    ("Odo", ["creature.folk.human", "deed.wilds", "deed.martial", "terrain.forest", "terrain.highland"], "unremarked", 2004),
    ("Touched, named", ["creature.folk.human", "deed.craft", "deed.wilds", "deed.primal", "deed.guile",
                        "deed.primal.elements"], "gifted", 2005),
    ("Touched, left to birth", ["creature.folk.human", "deed.craft", "deed.wilds", "deed.primal", "deed.guile"] + PRIMAL,
     "gifted", 2006),
]


@pytest.fixture(scope="module")
def ref() -> ModuleType:
    with contextlib.redirect_stdout(io.StringIO()):
        return load_module("draws02_reference", "02-gen_data02/draws02.py")


def committed() -> list[tuple[str, int, int, int, str]]:
    """(layer, pool, total, roll, entry) per slot line of the committed output."""
    text = (REF_DIR / "draws02-output.txt").read_text(encoding="utf-8")
    pat = re.compile(r"^\s+(gift|knack|quirk)\s+pool\s+(\d+) entries, total weight\s+(\d+), roll\s+(\d+) in band .* -> (\S+)",
                     re.M)
    return [(m[1], int(m[2]), int(m[3]), int(m[4]), m[5]) for m in pat.finditer(text)]


@pytest.mark.parametrize("name,src,circ,seed", CASES)
def test_creation_draw_matches_reference(ref: ModuleType, name: str, src: list[str], circ: Circumstance, seed: int) -> None:
    rng = random.Random(seed)
    bias = {f["circumstance"]: f.get("bias_tag") for f in ref.B["fill_map"]}[circ]
    want = []
    for layer in (["gift"] if circ == "gifted" else []) + ["knack", "quirk"]:
        e, n, tot, r, band = ref.draw(layer, src, bias, rng)
        want.append((layer, n, tot, r, band, e["id"]))
    got = birth_draw(random.Random(seed), src, circ, element="fire")    # a named element draws nothing more
    assert [(x.layer, x.pool_size, x.total_weight, x.roll, x.band, x.entry) for x in got.log] == want


def test_committed_output_is_reproduced() -> None:
    got = []
    for _, src, circ, seed in CASES:
        d = birth_draw(random.Random(seed), src, circ, element="fire")
        got += [(x.layer, x.pool_size, x.total_weight, x.roll, x.entry) for x in d.log]
    assert got == committed()


def test_bent_draws_match_reference(ref: ModuleType) -> None:
    """Wren's Bent: branches martial and wilds, Agility +3 excluded, three draws each striking the last."""
    rng_ref, rng = random.Random(3001), random.Random(3001)
    excl = {"birth.bent.agility"}
    for _ in range(3):
        e, cnt, tot, r, band = ref.draw("bent", ["deed.martial", "deed.wilds"], None, rng_ref, excl)
        mine, lg = draw_slot(rng, "bent", ["deed.martial", "deed.wilds"], None, sorted(excl))
        assert (mine["id"], lg.pool_size, lg.total_weight, lg.roll) == (e["id"], cnt, tot, r)
        excl.add(e["id"])
    text = (REF_DIR / "draws02-output.txt").read_text(encoding="utf-8")
    assert re.findall(r"-> (\w+)\n", text.split("Bent")[-1]) == ["endurance", "wits", "might"]


def test_bent_through_the_procedure_matches_reference() -> None:
    """The same three draws through PR-02-5: offer, defer, (spacing), offer, defer, offer, forgo."""
    rng = random.Random(3001)
    attrs = {"might": 1, "agility": 3, "endurance": 0, "wits": 1, "intellect": 0, "presence": 0, "resolve": 0}
    frames = {"deed.martial": 5, "deed.wilds": 3, "deed.lore": 2}
    st = BentState()
    got = []
    refl, total = 2, 10
    for answer in ("defer", "defer", "forgo"):
        st, offer = bent_offer(rng, st, window_locked=True, frames_by_branch=frames, attributes=attrs, reflection=refl,
                               frames_total=total)
        assert offer is not None
        got.append(offer.entry.attribute)
        st, eff = answer_bent(st, answer, reflection=refl, frames_total=total)  # type: ignore[arg-type]
        assert eff is None
        refl, total = refl + 2, total + 10
    assert got == ["endurance", "wits", "might"] and st.status == "forgone"


def test_source_tags_from_origins() -> None:
    assert source_tags("orig.people.human", "orig.up.wilds", "orig.life.soldier")[:5] == CASES[0][1]
    touched = source_tags("orig.people.human", "orig.up.wilds", "orig.life.touched")
    assert set(PRIMAL) <= set(touched)
