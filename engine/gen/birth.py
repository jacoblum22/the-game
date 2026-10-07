"""The birth draw (PR-02-4) and the Bent (PR-02-5), from `data/gen_birth.yaml`.

    tags = source_tags("orig.people.human", "orig.up.wilds", "orig.life.soldier")
    draw = birth_draw(rng, tags, "unremarked")          # -> BirthDraw(entries, log); the caller applies the effects

    state = BentState()
    state, offer = bent_offer(rng, state, window_locked=True, frames_by_branch={"deed.martial": 4},
                              attributes={"might": 1, ...}, reflection=3, frames_total=12)
    state, effect = answer_bent(state, "accept", reflection=4, frames_total=12)

The draw order is `_process/simulation/02-gen_data02/draws02.py`'s (one `randint(1, total weight)` per slot,
gift then knack then quirk), so a `random.Random(seed)` reproduces its worked examples. Two parts of PR-02-4 the
reference leaves out are added without moving its draws: the successor weight (x1/2 for an entry among the
domain's last five draws: all weights doubled, recent ones not, only when there are recent draws) and the
spark's element (02.6.3: drawn after the slots, equal weights, unless the concept named it).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field

from engine.gen import _data
from engine.gen._rng import SeedRng

Circumstance = Literal["unremarked", "hard", "omened", "gifted", "bent_first", "bent_again"]
ELEMENTS = ("fire", "water", "earth", "air")


class DrawLog(BaseModel):
    """What PR-02-4 step 5 logs for one slot: pool size, total weight and the roll."""

    layer: str
    pool_size: int
    total_weight: int
    roll: int
    band: tuple[int, int]
    entry: str


class BirthEntry(BaseModel):
    id: str
    name: str
    layer: str
    text: str
    effects: list[dict[str, Any]]
    competence: dict[str, Any] | None = None
    gifted_ability: str | None = None
    attribute: str | None = None
    element: str | None = None


class BirthDraw(BaseModel):
    circumstance: Circumstance
    rung: str
    source_tags: list[str]
    bias: str | None
    entries: list[BirthEntry]
    log: list[DrawLog]


def _gb() -> dict[str, Any]:
    return _data.load("gen_birth.yaml")


def _origins() -> dict[str, dict[str, Any]]:
    o = _data.load("origins.yaml")
    out = {x["id"]: x for x in o["origins"]}
    out.update({e["id"]: e for b in o.get("blocks") or [] for e in b.get("entries") or []})
    return out


def matches(gate: Sequence[str], src: Sequence[str]) -> bool:
    """00.5.4 c: a gate tag equals a source tag or is its ancestor."""
    return any(s == g or s.startswith(g + ".") for g in gate for s in src)


def carries(entry: Mapping[str, Any], bias: str) -> bool:
    return any(t == bias or t.startswith(bias + ".") for t in entry["tags"])


def source_tags(people: str, upbringing: str, livelihood: str, *, school: str | None = None) -> list[str]:
    """# rule: PR-02-4 step 1 -- the people's, upbringing's and livelihood's birth pools; a Touched character adds
    the named primal school tag, or all seven primal school tags when the gift is left to birth."""
    o = _origins()
    tags: list[str] = []
    for oid in (people, upbringing, livelihood):
        for t in o[oid].get("birth_pool") or []:
            if t not in tags:
                tags.append(t)
    if o[livelihood].get("birth_circumstance") == "gifted":
        schools = [school] if school else [e["gate_tags"][0] for e in _gb()["pool"] if e["layer"] == "gift"]
        tags += [s for s in schools if s not in tags]
    return tags


def circumstance_for(livelihood: str, manner: Circumstance = "unremarked") -> Circumstance:
    """# rule: PR-02-4 step 2 -- the circumstance is the manner (02.6.4); a Touched livelihood is always gifted."""
    return "gifted" if _origins()[livelihood].get("birth_circumstance") == "gifted" else manner


def draw_slot(rng: SeedRng, layer: str, src: Sequence[str], bias: str | None = None, exclude: Sequence[str] = (),
              recent: Sequence[str] = ()) -> tuple[dict[str, Any], DrawLog]:
    """# rule: PR-02-4 step 3-5 -- pool gate, then one weighted draw (x3 biased, x1/2 recent)."""
    cands = [e for e in _gb()["pool"] if e["layer"] == layer and matches(e["gate_tags"], src) and e["id"] not in exclude
             and not matches(e.get("excluded_tags") or [], src)]
    if not cands:
        raise ValueError(f"gen.birth: empty {layer} pool for {list(src)}")
    w = [e["weight"] * (3 if bias and carries(e, bias) else 1) for e in cands]
    if any(e["id"] in recent for e in cands):
        w = [x if e["id"] in recent else 2 * x for e, x in zip(cands, w, strict=True)]
    tot = sum(w)
    r = rng.randint(1, tot)
    acc = 0
    for e, x in zip(cands, w, strict=True):
        acc += x
        if r <= acc:
            return e, DrawLog(layer=layer, pool_size=len(cands), total_weight=tot, roll=r, band=(acc - x + 1, acc),
                              entry=e["id"])
    raise AssertionError("unreachable")


def _entry(e: dict[str, Any], element: str | None = None) -> BirthEntry:
    gifted = e.get("gifted_ability")
    if gifted == "by_element" and element:
        gifted = e["gifted_ability_by_element"][element]
    return BirthEntry(id=e["id"], name=e["name"], layer=e["layer"], text=e["text"], effects=list(e["tiers"][0]["effects"]),
                      competence=e.get("competence"), gifted_ability=gifted, attribute=e.get("attribute"), element=element)


def birth_draw(rng: SeedRng, src: Sequence[str], circumstance: Circumstance = "unremarked", *,
               recent: Sequence[str] = (), element: str | None = None) -> BirthDraw:
    """# rule: PR-02-4 -- the creation draw: the rung's slots filled gift, knack, quirk; returns entries and log.

    Writing (step 6: `apply_effect`, grants for a gift) is the caller's; each entry carries its effects.
    """
    gb = _gb()
    fill = {f["circumstance"]: f for f in gb["fill_map"]}[circumstance]
    bias = fill.get("bias_tag")
    rung = {q["circumstance"]: q["quality_rung"] for q in gb["quality_map"]}[circumstance]
    rdef = next(q for q in gb["quality_rungs"] if q["id"] == rung)
    layers = ([rdef["signature_layer"]] if rdef["signature_slots"] else []) + list(rdef["magnitude_layers"])
    picked: list[dict[str, Any]] = []
    log: list[DrawLog] = []
    for layer in layers:
        e, lg = draw_slot(rng, layer, src, bias, recent=recent)
        picked.append(e)
        log.append(lg)
    entries = []
    for e in picked:
        el = None
        if "element" in e:
            el = element or ELEMENTS[rng.randint(1, len(ELEMENTS)) - 1]
        entries.append(_entry(e, el))
    return BirthDraw(circumstance=circumstance, rung=rung, source_tags=list(src), bias=bias, entries=entries, log=log)


# ------------------------------------------------------------------------------------------------- the Bent


class BentOffer(BaseModel):
    entry: BirthEntry
    draw: int                       # 1, 2 or 3: the third offers forgo instead of defer
    log: DrawLog
    text: str


class BentState(BaseModel):
    """pc.creation.bent and its bookkeeping (02.6.5-02.6.7)."""

    status: Literal["none", "offered", "accepted", "forgone"] = "none"
    deferrals: int = 0
    struck: list[str] = Field(default_factory=list)
    offer: BentOffer | None = None
    deferred_at_reflection: int | None = None
    deferred_at_frames: int | None = None


def bent_branches(frames_by_branch: Mapping[str, int]) -> list[str]:
    """# rule: 02.6.5 -- the deed branches with at least three resolved frames by the PC since creation."""
    return sorted(b for b, n in frames_by_branch.items() if n >= 3)


def bent_offer(rng: SeedRng, state: BentState, *, window_locked: bool, frames_by_branch: Mapping[str, int],
               attributes: Mapping[str, int], reflection: int, frames_total: int,
               first_reflection: int | None = None) -> tuple[BentState, BentOffer | None]:
    """# rule: PR-02-5 steps 1-6 -- at a reflection: draw and offer a Bent if one is due (no default; never applied).

    `reflection`: this reflection's ordinal; `frames_total`: the PC's resolved frames since creation;
    `first_reflection`: the earliest reflection a first offer may come (the one after the window closed).
    """
    bent = _gb()["bent"]
    if not window_locked or state.status in ("accepted", "forgone"):
        return state, None
    if state.offer is not None:                 # open and unanswered: re-shown at session start, never re-drawn
        return state, None
    if first_reflection is not None and reflection < first_reflection:
        return state, None
    if state.deferred_at_reflection is not None:                         # 02.6.7 spacing
        if reflection - state.deferred_at_reflection < 2 or frames_total - (state.deferred_at_frames or 0) < 10:
            return state, None
    src = bent_branches(frames_by_branch)
    if not src:
        return state, None
    cap = bent["attribute_cap"]
    exclude = list(state.struck) + [e["id"] for e in _gb()["pool"] if e["layer"] == "bent"
                                    and attributes.get(e["attribute"], 0) >= cap]
    try:
        e, lg = draw_slot(rng, "bent", src, None, exclude)
    except ValueError:                          # empty pool: try again at the next reflection
        return state, None
    n = state.deferrals + 1
    offer = BentOffer(entry=_entry(e), draw=n, log=lg, text=bent_offer_text(e, n, bent["deferrals_max"]))
    return state.model_copy(update={"status": "offered", "offer": offer}), offer


def bent_offer_text(e: Mapping[str, Any], draw: int, deferrals_max: int = 2) -> str:
    """# rule: PR-02-5 step 6 -- the [CHOICE] block (the caller may add the derived change, e.g. Vitality)."""
    attr = e["attribute"]
    if draw > deferrals_max:
        b = "(b) forgo: no Bent, ever"
    else:
        b = ("(b) defer: this one is gone for you; another comes later, from what you have been doing by then "
             "(you may defer twice in all; this is the %s time)" % ("first" if draw == 1 else "second"))
    return (f"[CHOICE] Your Bent: something in you has settled. {attr.capitalize()} +1, for good.\n         (a) accept · {b}\n"
            "         No default: nothing changes until you choose.")


def answer_bent(state: BentState, answer: Literal["accept", "defer", "forgo"], *, reflection: int,
                frames_total: int) -> tuple[BentState, dict[str, Any] | None]:
    """# rule: PR-02-5 step 7 -- accept (returns the eff.02.bent effect to apply), defer (strike it), or forgo."""
    if state.offer is None:
        raise ValueError("no Bent offer is open")
    offer = state.offer
    third = offer.draw > _gb()["bent"]["deferrals_max"]
    if answer == "accept":
        return state.model_copy(update={"status": "accepted", "offer": None}), dict(offer.entry.effects[0])
    if answer == "defer" and not third:
        return state.model_copy(update={"status": "none", "offer": None, "deferrals": state.deferrals + 1,
                                        "struck": state.struck + [offer.entry.id], "deferred_at_reflection": reflection,
                                        "deferred_at_frames": frames_total}), None
    if answer == "forgo" and third:
        return state.model_copy(update={"status": "forgone", "offer": None}), None
    raise ValueError(f"{answer} is not an answer to draw {offer.draw:d} of the Bent")
