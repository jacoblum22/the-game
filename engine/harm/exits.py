"""The two exits before the brink: Yield (07.4.1–07.4.2) and Retreat (07.4.3–07.4.4; PR-06-6's sibling PR-07-6).
Both are answered from state BEFORE the player commits, as data for a pause:

    ans = yield_answer(rules, state, "pc.wren", "foe.guild_rider")       # accepted? which terms?
    tx.add(yield_pause(tx.mint, ans))                                       # pause kind yield_terms
    tx.add_all(commit_yield(ctx, "pc.wren", ans, term="keep_one_thing"))

    off = retreat_offer(ctx.state, rules, "pc.wren", route=True, engaged=["foe.ghoul"])
    tx.add_all(commit_retreat(ctx, "pc.wren", off, choice="clean"))

Victor data read from the entity: `defeat_disposition` (T-07-11 row), `leader_want` (a want the PC can meet),
`attacks`/`max_severity` (the parting blow), `pace` (the pursuit test), `broken` fact (a broken side).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from engine import ids
from engine.harm import lethal as lethal_mod
from engine.harm.apply import apply_harm, shift, stabilize
from engine.harm.ctx import Writes
from engine.harm.state import DYING, defeated_manner, harm_state, is_down
from engine.store.clocks import create_clock, tick_clock
from engine.store.events import Event, PauseRecord
from engine.store.projection import WorldState

# What a disposition does to a PC who yields, in the words the answer uses (T-07-11, yielded column).
DISPOSITION_WORDS = {
    "capture": "take you prisoner", "ransom": "hold you for ransom",
    "rob": "take your coin and valuables and let you go", "drive_off": "let you walk out of here",
    "leave": "leave you be", "kill": "kill you", "drag_to_lair": "drag you to its lair"}
# A refusing foe's answer (07.4.1 example).
REFUSAL = "not accepted (it does not understand quarter, and would not give it)"


def disposition_of(state: WorldState, victor: str | None) -> str | None:
    e = state.entities.get(victor or "")
    return str(e.data.get("defeat_disposition")) if e is not None and e.data.get("defeat_disposition") else None


@dataclass
class YieldAnswer:
    pc: str
    victor: str | None
    disposition: str | None
    accepted: bool
    terms: list[dict[str, str]] = field(default_factory=list)  # [{id, label, text}], the player picks one
    default_term: str = "no_further_harm"
    words: str = ""  # the exits card's Yield words
    want: str | None = None  # the recorded want that turns a refusal into an acceptance


def yield_answer(rules: Any, state: WorldState, pc: str, victor: str | None) -> YieldAnswer:  # rule: 07.4.1
    """Accepted? A lookup by the victor's disposition (T-07-8), never a roll; the terms the player may choose."""
    disp = disposition_of(state, victor)
    y = rules.harm["yield"]
    want = None
    accepted = bool(y["accepted_by"].get(disp, False)) if disp else False
    if not accepted and victor in state.entities and state.entities[victor or ""].data.get("leader_want"):
        want = str(state.entities[victor or ""].data["leader_want"])
        accepted = True
    terms: list[dict[str, str]] = []
    if accepted:
        dying = harm_state(state, pc) == DYING
        for t in y["terms"]:  # rule: 07.4.2
            if t.get("always") or (not dying and disp in (t.get("allowed_for") or ())):
                terms.append({"id": str(t["id"]), "label": str(t["name"]), "text": str(t["text"])})
    if want:
        words = f"accepted: it would take {want} and go"
    elif accepted:
        words = f"accepted: they would {DISPOSITION_WORDS.get(disp or '', 'take your surrender')}"
    else:
        words = REFUSAL
    return YieldAnswer(pc, victor, disp, accepted, terms, "no_further_harm", words, want)


def yield_pause(mint: Any, ans: YieldAnswer) -> Event:  # rule: 07.4.1
    """The `yield_terms` pause: the allowed terms, default no_further_harm (the player names one or none)."""
    choices = [{"id": t["id"], "label": f"{t['label']} — {t['text']}"} for t in ans.terms]
    choices.append({"id": "withdraw", "label": "Do not yield"})
    pause = PauseRecord(pause_id=mint(ids.PAUSE), kind="yield_terms", prompt=f"Yield? {ans.words}.",
                        choices=choices, default_choice=ans.default_term,
                        detail={"pc": ans.pc, "victor": ans.victor, "disposition": ans.disposition})
    return Event.of("pause_opened", source="07.4.1", rule_id="07.4.1", pause=pause)


def commit_yield(ctx: Any, pc: str, ans: YieldAnswer, term: str = "no_further_harm",
                 writes: Writes | None = None) -> list[Event]:  # rule: 07.4.1
    """An accepted yield: defeated {yielded}, setback.yielded, the term as the victor's commitment, the Dying PC
    stabilized by the victors, then the disposition's yielded column (PR-07-7, coarse in M1)."""
    if not ans.accepted:
        raise ValueError("yield not accepted: nothing is spent (07.4.1)")
    if term not in {t["id"] for t in ans.terms}:
        raise ValueError(f"term {term!r} is not allowed by {ans.disposition}")
    w = writes or Writes.of(ctx, source="07.4.1")
    start = len(w.events)
    if harm_state(w, pc) == DYING:
        stabilize(ctx, pc, writes=w)
    w.fact(pc, "defeated", {"manner": "yielded", "victor": ans.victor}, rule_id="07.4.1")
    w.fact(pc, "setback.yielded", {"victor": ans.victor, "term": term}, rule_id="07.4.1")
    if ans.victor:
        w.fact(ans.victor, f"yield_term:{pc}", term, kind="commitment", rule_id="07.4.2")
    run_disposition(ctx, pc, ans.victor, column="yielded", term=term, writes=w)
    return w.events[start:]


def run_disposition(ctx: Any, pc: str, victor: str | None, *, column: str, term: str | None = None,
                    writes: Writes) -> None:  # rule: PR-07-7
    """PR-07-7, Milestone 1: the always-writes (`victory_over_pc`, the setback, the chronicle line) and the row's
    words as a fact; captivity places, caches and openings (07.6.3–07.6.4) are coarse until M6."""
    w = writes
    disp = disposition_of(ctx.state, victor) or "leave"
    row = next((d for d in ctx.rules.harm["dispositions"] if d["id"] == disp), None)
    lines = [str(x) for x in (row or {}).get(column) or ()]
    if victor:
        w.fact(victor, "victory_over_pc", pc, rule_id="07.6.2")
    w.fact(pc, "disposition", {"victor": victor, "row": disp, "column": column, "term": term, "writes": lines},
           rule_id="PR-07-7")
    # coarse: PR-07-7 steps 3-4 — holding place, journey, cache and openings are the DM's to frame in M1.
    w.coarse("PR-07-7", "disposition recorded; captivity, cache and openings framed by the DM", entity=pc,
             disposition=disp, column=column)


# ------------------------------------------------------------------------------------------- Retreat


@dataclass
class RetreatOffer:
    pc: str
    legal: bool
    refusal: str | None = None
    kind: str = "clean"  # clean | contested
    pursuers: list[str] = field(default_factory=list)  # willing and able
    parting_blow: dict[str, Any] | None = None  # {source, severity}
    left_behind: list[str] = field(default_factory=list)
    rout_clocks: list[str] = field(default_factory=list)  # candidates in 07.4.3 order; [] -> create clk.grudge
    rout_ticks: int = 2
    choices: list[dict[str, str]] = field(default_factory=list)
    words: str = ""


def _attack_severity(state: WorldState, eid: str) -> str | None:
    d = state.entities[eid].data
    sevs = [str(a.get("severity")) for a in d.get("attacks") or () if isinstance(a, dict)]
    if d.get("max_severity"):
        sevs.append(str(d["max_severity"]))
    sevs = [s for s in sevs if s in ("S1", "S2", "S3", "S4", "S5")]
    return max(sevs) if sevs else None


def _held(state: WorldState, eid: str) -> bool:
    return any(c.condition_id in ("cond.prone", "cond.restrained", "cond.pinned", "cond.grappled")
               for c in state.conditions_on(eid))


def pursuit_test(state: WorldState, pc: str, hostiles: Sequence[str], *,
                 barred: Sequence[str] = ()) -> list[str]:  # rule: 07.4.3
    """The pursuers both WILLING (objective kill, capture or rob; side not broken) and ABLE (pace at least the
    PC's, not held or prone, a way to follow: not in `barred`, the ones a shut barrier stops)."""
    pace = int(state.entities[pc].data.get("pace", 0))
    out = []
    for h in hostiles:
        e = state.entities.get(h)
        if e is None or e.exists != "exists" or defeated_manner(state, h):
            continue
        willing = (e.data.get("objective") or e.data.get("defeat_disposition")) in ("kill", "capture", "rob") \
            and not state.fact_value(h, "broken", False)
        able = int(e.data.get("pace", 0)) >= pace and not _held(state, h) and h not in barred
        if willing and able:
            out.append(h)
    return out


def rout_candidates(state: WorldState, victors: Sequence[str]) -> list[str]:  # rule: 07.4.3
    """Clocks a rout may tick, in 07.4.3's order (faction goal clock, the scene's danger or countdown clock of that
    side); at most four. Empty: the rout creates `clk.grudge`."""
    owners = set(victors) | {str(state.entities[v].data.get("faction")) for v in victors
                             if v in state.entities and state.entities[v].data.get("faction")}
    act = [c for c in state.clocks.values() if c.status == "active" and c.owner in owners]
    goal = [c.id for c in act if c.kind == "faction_goal"]
    danger = [c.id for c in act if c.kind in ("danger", "countdown")]
    return (goal + danger)[:4]


def retreat_offer(state: WorldState, rules: Any, pc: str, *, route: bool, engaged: Sequence[str] = (),
                  hostiles: Sequence[str] | None = None, barred: Sequence[str] = (),
                  left_behind: Sequence[str] = ()) -> RetreatOffer:  # rule: PR-07-6
    """PR-07-6 steps 1-3: legality, the pursuit test and the whole price, shown before the player commits.
    `route` is decision 1 (the DM's flag; the Oracle when unestablished); `engaged`: enemies engaged with the PC."""
    off = RetreatOffer(pc=pc, legal=True)
    flags = state.positions.get(pc)
    blocked = [c.condition_id for c in state.conditions_on(pc) if c.condition_id in ("cond.restrained", "cond.pinned")]
    if flags is not None and "flag.cornered" in flags.flags:
        off.legal, off.refusal = False, "you are cornered: get past it first (Force or Move through, 06.5.6)"
    elif blocked:
        off.legal, off.refusal = False, f"you are {blocked[0].removeprefix('cond.')}: break free first"
    elif harm_state(state, pc) == DYING or is_down(state, pc):
        off.legal, off.refusal = False, "you cannot leave under your own power: you must be carried"
    elif not route:
        off.legal, off.refusal = False, "there is no way out of here: you are cornered in fact"
    if not off.legal:
        off.words = off.refusal or ""
        return off
    hs = list(hostiles) if hostiles is not None else lethal_mod.scene_sources(state)
    off.pursuers = pursuit_test(state, pc, hs, barred=barred)
    heavy = [(s, e) for e in engaged if e in state.entities and (s := _attack_severity(state, e))]
    if heavy:
        sev, src = max(heavy)
        off.parting_blow = {"source": src, "severity": shift(sev, -1)}  # one rung lighter; None below S1
    off.left_behind = list(left_behind)
    off.rout_clocks = rout_candidates(state, hs)
    price = ("one parting blow" if off.parting_blow and off.parting_blow["severity"] else "nothing to pay") + \
        (f"; left behind: {', '.join(off.left_behind)}" if off.left_behind else "")
    if not off.pursuers:
        off.kind = "clean"
        off.choices = [{"id": "clean", "label": f"Clean retreat: {price}"}]
        off.words = f"clean: {price}"
    else:
        off.kind = "contested"
        clock = off.rout_clocks[0] if off.rout_clocks else "a grudge they will carry"
        off.choices = [{"id": "run_for_it", "label": "Run for it: a chase (06.12)"},
                       {"id": "rout", "label": f"Rout: certain; {price}; {clock} +{off.rout_ticks}"}]
        off.words = f"a chase, or a rout costing {clock} +{off.rout_ticks}"
    return off


def _tick_world_cost(state: WorldState, clock_id: str, n: int, on: str) -> list[Event]:  # rule: 07.4.3
    """Tick `n` as a world cost: the clock need not list the rout as a source (07.4.3 sets the amount)."""
    c = state.clocks[clock_id]
    tmp = state.model_copy()
    tmp.clocks = {**state.clocks, clock_id: c.model_copy(update={"tick_sources": [*c.tick_sources,
                                                                                  {"on": on, "ticks": n}]})}
    return tick_clock(tmp, clock_id, on, row="source", source_ref=on, rule_id="07.4.3").events


def world_cost(ctx: Any, w: Writes, victor: str | None, clock_id: str | None, ticks: int,
               candidates: Sequence[str] = ()) -> str:  # rule: 07.4.3
    """Tick the named clock (default: the first candidate), else create `clk.grudge` for the victor. Returns the
    clock id ticked."""
    st: WorldState = ctx.state
    cid = clock_id or (candidates[0] if candidates else None)
    if cid is None:
        tpl = next(c for c in ctx.rules.harm["clock_templates"] if c["id"] == "clk.grudge")
        filled = int(tpl.get("starts_filled", 0))
        ev = create_clock(st, {k: v for k, v in tpl.items() if k not in ("starts_filled", "owner")}, owner=victor or "",
                          rule_id="07.4.3", filled=filled)
        w.extend([ev])
        clock = ev.payload.clock  # type: ignore[attr-defined]
        tmp = st.model_copy()
        tmp.clocks = {**st.clocks, clock.id: clock}
        w.extend(_tick_world_cost(tmp, clock.id, ticks, "rout"))
        return str(clock.id)
    w.extend(_tick_world_cost(st, cid, ticks, "rout"))
    return cid


def commit_retreat(ctx: Any, pc: str, off: RetreatOffer, choice: str, *, clock_id: str | None = None,
                   destination: str | None = None, writes: Writes | None = None) -> list[Event]:  # rule: PR-07-6
    # rule: 07.4.4
    """PR-07-6 on commit, in order: the parting blow (lethal: false), what is left behind, the world cost of a
    rout; then the move and the PC's conflict_end. `run_for_it` returns no events: the chase is 06.12's (M2)."""
    if not off.legal:
        raise ValueError(off.refusal or "retreat is not legal")
    if choice not in {c["id"] for c in off.choices}:
        raise ValueError(f"{choice!r} is not on the retreat offer")
    w = writes or Writes.of(ctx, source="PR-07-6")
    start = len(w.events)
    if choice == "run_for_it":
        # coarse: 06.12 — a chase is M2; M1's pipeline frames it as one contested beat.
        w.coarse("06.12", "run for it: the chase is framed as an ordinary beat in M1", entity=pc)
        return w.events[start:]
    pb = off.parting_blow
    if pb and pb.get("severity"):
        apply_harm(ctx, pc, severity=pb["severity"], source=pb["source"], lethal=False, writes=w)
    for item in off.left_behind:
        w.fact(pc, f"left_behind:{item}", True, rule_id="07.4.4")
    if ctx.state.scene is not None and ctx.state.scene.agenda:
        w.fact(pc, "objective_lost", ctx.state.scene.agenda, rule_id="07.4.4")
    if choice == "rout":
        victor = off.pursuers[0] if off.pursuers else None
        cid = world_cost(ctx, w, victor, clock_id, off.rout_ticks, off.rout_clocks)
        w.fact(pc, "setback.retreated", {"severity": "S3", "clock": cid}, rule_id="07.4.3")
    if destination:
        w.extend([Event.of("position_set", source="PR-07-6", rule_id="PR-07-6", entity=pc, location=destination)])
    w.fact(pc, "conflict_end", True, rule_id="PR-07-6", only_if_changed=False)
    return w.events[start:]
