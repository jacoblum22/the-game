"""The Threshold and the last-chance menu (07.5; PR-07-5), death under the Two-Key rule (07.3.1), and the ending
of a character's story (death, retirement, career end).

    if res.threshold:                                         # from apply_harm or dying_check
        op = open_threshold(ctx, "pc.wren", Situation(victor="foe.wight", bargainer="npc.barrow_king"))
        tx.add_all(op.events)                                 # dread +2, setback.threshold, the last_chance pause
    ...the player picks...
    ch = choose(ctx, "pc.wren", op.menu, "lc.bargain", pause_id=op.pause_id)
    tx.add_all(ch.events)
    ending_state(state)                                       # None | "death" | "retirement" | "career_end"

The menu is data for a `last_chance` pause (contracts/engine-api.md): choices are the surviving options in the
rules' order, there is no default, and each carries its full price computed from state. Death is written only
by `write_death`, which refuses unless Key 1 (a lethal context on record for the fall, or a confirmed chosen
death) and Key 2 (Last Stand, a failed Gamble, a confirmed voluntary last stand) both hold (INV-6).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from engine import ids
from engine.harm import lethal as lethal_mod
from engine.harm.apply import restore_vitality, stabilize
from engine.harm.ctx import Writes
from engine.harm.dice import dc_of, degree, distribution, pct, roll_d20
from engine.harm.exits import disposition_of, rout_candidates, run_disposition, world_cost
from engine.harm.state import (
    DEAD,
    DYING,
    VITALITY,
    attribute,
    defeated_manner,
    endure_modifier,
    fate,
    harm_state,
    pcs,
)
from engine.store.clocks import create_clock
from engine.store.events import Event, PauseRecord
from engine.store.projection import WorldState

DEATH_OPTIONS = ("lc.last_stand", "lc.gamble")


@dataclass
class Situation:
    """What the engine cannot read from M1 state at the Threshold; the pipeline fills it from the fight."""

    victor: str | None = None
    source_kind: str = "entity"  # entity | hazard | affliction (lc.left_for_dead with no victor)
    bargainer: str | None = None  # an entity with `can_bargain: true` (07.5.2 decision 2); else found in the scene
    bargain_ask: str | None = None
    route: bool = False  # 07.4.3 decision 1
    companion_can_carry: bool = False
    rout_clock: str | None = None  # 07.4.3 decision 2
    maim_entry: str | None = None  # fix the maim drawn (tests, replays); else tbl.wound_site and a d2
    strikes: dict[str, str] = field(default_factory=dict)  # option id -> the fact id that rules it out


@dataclass
class MenuOption:
    id: str
    name: str
    order: int
    available: bool
    reason: str = ""  # why it is not offered
    price: str = ""
    death: bool = False
    struck_by: str | None = None


@dataclass
class Menu:
    pc: str
    options: list[MenuOption]
    situation: Situation
    fate_cost: int
    maim: dict[str, Any] | None = None  # {entry, name, attribute, text}
    bargain: dict[str, Any] | None = None  # {bargainer, ask}
    gamble: dict[str, int] = field(default_factory=dict)  # percentages per result
    refused_strikes: list[str] = field(default_factory=list)

    def offered(self) -> list[MenuOption]:
        return [o for o in self.options if o.available]

    def choices(self) -> list[dict[str, str]]:
        return [{"id": o.id, "label": f"({o.order}) {o.name} — {o.price}"} for o in self.offered()]


def _option_data(rules: Any) -> list[dict[str, Any]]:
    return sorted(rules.last_chance["options"], key=lambda o: int(o["order"]))


def _present(state: WorldState, eid: str | None) -> bool:
    e = state.entities.get(eid or "")
    return e is not None and e.exists == "exists" and not defeated_manner(state, eid or "")


def fate_cost(state: WorldState, pc: str) -> int:  # rule: 07.5.8
    """min(3, 1 + reprieves already taken in this life)."""
    return min(3, 1 + int(state.fact_value(pc, "reprieves_taken", 0) or 0))


def _maims(state: WorldState, pc: str) -> list[dict[str, Any]]:
    return list(state.fact_value(pc, "maims", []) or [])


def _maim_attribute(state: WorldState, pc: str, order: list[str]) -> str | None:  # rule: 07.7.4
    taken = {m.get("attribute") for m in _maims(state, pc)}
    return next((a for a in order if a not in taken and attribute(state, pc, a) > -2), None)


def draw_maim(ctx: Any, pc: str, sit: Situation) -> dict[str, Any] | None:  # rule: 07.7.4
    """The maim the Maimed option would take. M1 has no wound sites, so the site is the engine's roll on
    `tbl.wound_site` (07.2.4's fallback) and a d2 between that site's maims (WE-07-1)."""
    st: WorldState = ctx.state
    entries = [e for e in ctx.rules.doc("injuries")["injuries"] if str(e["id"]).startswith("inj.maim.")]
    if sit.maim_entry:
        pool = [e for e in entries if e["id"] == sit.maim_entry]
    else:
        rng = getattr(ctx, "rng", None)
        site_tbl = next(t for t in ctx.rules.harm["tables"] if t["id"] == "tbl.wound_site")
        if rng is None:
            pool = entries
        else:
            # coarse: 07.7.4 — "the site of the worst fresh wound" has no wound record in M1: tbl.wound_site.
            _, row = rng.pick(site_tbl, f"maim site {pc}")
            site = [e for e in entries if e.get("site") == row["result"]]
            pool = site[rng.d(len(site), f"maim among {row['result']}") - 1:] if site else entries
    for e in pool:
        a = _maim_attribute(st, pc, list(e.get("attribute_order") or ()))
        if a:
            return {"entry": str(e["id"]), "name": str(e["name"]), "attribute": a, "text": str(e.get("text", ""))}
    return None


def _bargain(ctx: Any, pc: str, sit: Situation) -> dict[str, Any] | None:  # rule: 07.5.5
    st: WorldState = ctx.state
    b = sit.bargainer
    if b is None:
        cast = lethal_mod.scene_sources(st)
        b = next((i for i in cast if st.entities[i].data.get("can_bargain")), None)
    if b is None or b not in st.entities or st.fact_value(pc, "deaths_debt"):
        return None
    ask = sit.bargain_ask or st.entities[b].data.get("want")
    if not ask and st.entities[b].data.get("wants"):
        ask = st.entities[b].data["wants"][0]
    if not ask:
        rng = getattr(ctx, "rng", None)
        tbl = next(t for t in ctx.rules.harm["tables"] if t["id"] == "tbl.bargain_asks")
        ask = rng.pick(tbl, f"bargain ask {b}")[1]["result"] if rng is not None else tbl["results"][0]["result"]
    return {"bargainer": b, "ask": str(ask)}


def _cornered(state: WorldState, pc: str) -> bool:
    pos = state.positions.get(pc)
    held = any(c.condition_id in ("cond.restrained", "cond.pinned") for c in state.conditions_on(pc))
    return held or (pos is not None and "flag.cornered" in pos.flags)


def build_menu(ctx: Any, pc: str, sit: Situation) -> Menu:  # rule: PR-07-5
    # rule: T-07-10
    """PR-07-5 steps 2-4: evaluate each option's `requires` against state, price it, apply the DM's strikes
    (each citing a recorded fact; refused if it would leave < 3 options or none that is not death)."""
    st: WorldState = ctx.state
    victor = sit.victor if _present(st, sit.victor) else None
    disp = disposition_of(st, victor)
    objective = st.entities[victor].data.get("objective") if victor else None
    vname = st.entities[victor].name if victor else "no one"
    menu = Menu(pc=pc, options=[], situation=sit, fate_cost=fate_cost(st, pc))
    scene = lethal_mod.scene_id(st)
    maimed_here = st.fact_value(pc, "maimed_in_scene") == scene and scene is not None
    menu.maim = None if maimed_here else draw_maim(ctx, pc, sit)
    menu.bargain = _bargain(ctx, pc, sit)
    dist = distribution(endure_modifier(st, pc), dc_of(ctx.rules, "moderate"))
    menu.gamble = {"free": pct(dist["critical_success"]), "live": pct(dist["success"]),
                   "choose": pct(dist["failure_within_3"]), "death": pct(dist["failure"] + dist["critical_failure"])}
    v = st.quantities[pc][VITALITY]
    mx = v.max if v.max is not None else v.current
    quarter = math.ceil(mx / 4)
    for o in _option_data(ctx.rules):
        oid = str(o["id"])
        mo = MenuOption(oid, str(o["name"]), int(o["order"]), True, death=oid in DEATH_OPTIONS)
        if oid == "lc.captured":
            mo.available = victor is not None and (disp in ("capture", "ransom", "rob", "drag_to_lair")
                                                   or objective == "capture")
            mo.reason = "" if mo.available else ("no victor present" if victor is None else f"the victor's "
                                                 f"disposition is {disp}")
            mo.price = f"{vname} takes you, alive"
        elif oid == "lc.maimed":
            mo.available = menu.maim is not None
            mo.reason = "" if mo.available else "already chosen this scene, or no attribute left to maim"
            if menu.maim:
                mo.price = (f"{menu.maim['name']}: {menu.maim['attribute'].capitalize()} -1; "
                            f"you stand at Vitality {quarter}")
        elif oid == "lc.bargain":
            mo.available = menu.bargain is not None
            mo.reason = "" if mo.available else "no power here could take a debt"
            if menu.bargain:
                bn = st.entities[menu.bargain["bargainer"]].name
                mo.price = f"{bn} asks: {menu.bargain['ask']}"
        elif oid == "lc.left_for_dead":
            mo.available = (victor is not None and disp not in ("kill", "drag_to_lair")) or (
                victor is None and sit.source_kind in ("hazard", "affliction"))
            mo.reason = "" if mo.available else "kill makes sure" if disp == "kill" else "nothing would leave you"
            mo.price = "what they want is taken; you wake a watch later where you fell"
        elif oid == "lc.rout":
            mo.available = (sit.route and not _cornered(st, pc)) or sit.companion_can_carry
            mo.reason = "" if mo.available else "cornered, and no one to carry you"
            cands = rout_candidates(st, [victor] if victor else [])
            clock = sit.rout_clock or (cands[0] if cands else "a grudge they will carry")
            mo.price = f"{clock} +{int(ctx.rules.severity_units()['S4'])}"
        elif oid == "lc.reprieve":
            mo.available = fate(st, pc) >= menu.fate_cost
            mo.reason = "" if mo.available else f"fate {fate(st, pc)}, the cost is {menu.fate_cost}"
            mo.price = f"fate {menu.fate_cost} of {fate(st, pc)}; you stand at Vitality {quarter}"
        elif oid == "lc.last_stand":
            mo.price = "one turn in which nothing you attempt fails, then death"
        elif oid == "lc.gamble":
            g = menu.gamble
            mo.price = f"{g['free']}% free / {g['live']}% live / {g['choose']}% choose a price / {g['death']}% death"
        elif oid == "lc.road_ends":
            mo.price = "you live; your adventuring is over"
        menu.options.append(mo)
    _strike(ctx, menu)
    return menu


def valid(options: list[MenuOption]) -> bool:  # rule: 07.5.2
    live = [o for o in options if o.available]
    return len(live) >= 3 and any(not o.death for o in live)


def _strike(ctx: Any, menu: Menu) -> None:  # rule: 07.5.2
    data = {str(o["id"]): o for o in _option_data(ctx.rules)}
    for oid, fact_id in menu.situation.strikes.items():
        o = next((x for x in menu.options if x.id == oid), None)
        if o is None or not o.available or not data[oid].get("struck_when") or fact_id not in ctx.state.facts:
            menu.refused_strikes.append(oid)
            continue
        o.available, o.struck_by = False, fact_id
        if not valid(menu.options):
            o.available, o.struck_by = True, None
            menu.refused_strikes.append(oid)


def menu_text(menu: Menu) -> str:  # rule: 07.5.2
    """The `[CHOICE]` block (T-07-7)."""
    lines = ["[CHOICE]  THE THRESHOLD — you do not roll to die; you choose."]
    lines += [f"          ({o.order}) {o.name} — {o.price}" for o in menu.offered()]
    struck = [f"{o.name} — {o.struck_by}" for o in menu.options if o.struck_by]
    if struck:
        lines.append(f"          Struck: {'; '.join(struck)}.")
    lines.append("          There is no default: the moment holds.")
    return "\n".join(lines)


@dataclass
class ThresholdOpen:
    events: list[Event]
    menu: Menu
    pause_id: str
    text: str


def open_threshold(ctx: Any, pc: str, sit: Situation, *, writes: Writes | None = None) -> ThresholdOpen:
    """PR-07-5 steps 1, 5: the conflict pauses, dread +2, `setback.threshold`, and the menu as a `last_chance`
    pause with no default."""  # rule: PR-07-5
    w = writes or Writes.of(ctx, source="PR-07-5")
    start = len(w.events)
    if harm_state(ctx.state, pc) != DYING:
        raise ValueError(f"{pc} is not at the Threshold (not Dying)")
    if w.quantity(pc, "dread") is not None:
        w.add_quantity(pc, "dread", 2, reason="the Threshold", rule_id="07.11.2")
    else:
        w.coarse("07.11.2", "dread +2 at the Threshold not tracked before M2", entity=pc)
    w.fact(pc, "setback.threshold", {"scene": lethal_mod.scene_id(ctx.state)}, rule_id="07.5.1",
           only_if_changed=False)
    menu = build_menu(ctx, pc, sit)
    pid = w.mint(ids.PAUSE)
    text = menu_text(menu)
    pause = PauseRecord(pause_id=pid, kind="last_chance", prompt=text, choices=menu.choices(), default_choice=None,
                        detail={"pc": pc, "fate_cost": menu.fate_cost, "maim": menu.maim, "bargain": menu.bargain,
                                "gamble": menu.gamble, "victor": sit.victor,
                                "struck": {o.id: o.struck_by for o in menu.options if o.struck_by}})
    w.extend([Event.of("pause_opened", source="PR-07-5", rule_id="PR-07-5", pause=pause)])
    return ThresholdOpen(w.events[start:], menu, pid, text)


# ------------------------------------------------------------------------------------------- the choice


@dataclass
class Choice:
    events: list[Event]
    option: str
    stays_in_scene: bool = False
    gamble_offer: dict[str, Any] | None = None  # option 8: frame the Gamble as a lethal frame and OFFER it
    last_stand: bool = False  # option 7: run the final turn, then finish_last_stand
    advance_time: str | None = None  # e.g. "watches:1" for Left for Dead (the caller advances time)
    ending: str | None = None
    narration: list[str] = field(default_factory=list)


def _close(w: Writes, pause_id: str | None, choice: str) -> None:
    if pause_id and any(p.pause_id == pause_id for p in w.state.pauses):
        w.extend([Event.of("pause_closed", source="PR-07-5", rule_id="PR-07-5", pause_id=pause_id, choice=choice)])


def _after(w: Writes, pc: str, option: dict[str, Any], line: str) -> None:  # rule: 07.5.12
    w.fact(pc, "wound_load", 0, rule_id="07.5.12")
    w.fact(pc, "chronicle_line", line, rule_id="07.5.12", only_if_changed=False)
    if "brink mark" in " ".join(str(x) for x in option.get("world_writes") or ()) or \
            str(option.get("mark", "none")).startswith("chosen"):
        # coarse: 07.7.3 — brink marks (draw three, the player picks) are M2's marks; recorded as owed.
        w.coarse("07.7.3", "brink mark owed (marks are M2)", entity=pc, option=option["id"])


def choose(ctx: Any, pc: str, menu: Menu, option_id: str, *, pause_id: str | None = None,
           via_gamble: bool = False, writes: Writes | None = None) -> Choice:  # rule: PR-07-5
    """PR-07-5 steps 6-7: apply the chosen option's outcome and world writes."""
    st: WorldState = ctx.state
    o = next((x for x in menu.options if x.id == option_id), None)
    if o is None or not o.available:
        raise ValueError(f"{option_id} is not on the menu")
    if via_gamble and option_id not in ("lc.captured", "lc.maimed", "lc.bargain", "lc.left_for_dead", "lc.rout"):
        raise ValueError("a near-failed Gamble pays one of options 1-5")
    data = next(x for x in _option_data(ctx.rules) if x["id"] == option_id)
    w = writes or Writes.of(ctx, source="PR-07-5")
    start = len(w.events)
    _close(w, pause_id, option_id)
    ch = Choice([], option_id, stays_in_scene=bool(data.get("stays_in_scene") is True))
    v = w.quantity(pc, VITALITY)
    mx = (v.max if v is not None and v.max is not None else 0) or 0
    quarter = math.ceil(mx / 4)
    w.fact(pc, "threshold_choice", option_id, rule_id="PR-07-5", only_if_changed=False)
    victor = menu.situation.victor
    if option_id == "lc.captured":  # rule: 07.5.3
        stabilize(ctx, pc, writes=w)
        w.fact(pc, "defeated", {"manner": "captured", "victor": victor}, rule_id="07.5.3")
        w.fact(pc, "setback.captured", {"victor": victor}, rule_id="07.5.3")
        run_disposition(ctx, pc, victor, column="defeated", writes=w)
    elif option_id == "lc.maimed":  # rule: 07.5.4
        restore_vitality(ctx, pc, to=quarter, reason="maimed: you stand", rule_id="07.5.4", writes=w)
        m = menu.maim or {}
        w.fact(pc, "maims", [*_maims(st, pc), m], rule_id="07.7.4")
        a = str(m.get("attribute"))
        w.fact(pc, f"attribute_delta.{a}", int(st.fact_value(pc, f"attribute_delta.{a}", 0) or 0) - 1,
               rule_id="07.7.4")
        w.fact(pc, "maimed_in_scene", lethal_mod.scene_id(st), rule_id="07.5.4")
    elif option_id == "lc.bargain":  # rule: 07.5.5
        restore_vitality(ctx, pc, to=1, reason="Death's Bargain", rule_id="07.5.5", writes=w)
        b = menu.bargain or {}
        w.fact(pc, "deaths_debt", {**b, "stage": 1}, rule_id="07.5.5")
        tpl = next(c for c in ctx.rules.harm["clock_templates"] if c["id"] == "clk.deaths_debt")
        w.extend([create_clock(st, {k: v for k, v in tpl.items() if k != "owner"}, owner=pc, rule_id="07.5.5",
                               omens={})])
        # coarse: 07.5.5 — aff.deaths_debt (an affliction) and its vow thread are M2/M6; recorded as the fact.
        w.coarse("07.5.5", "aff.deaths_debt stage 1 and the vow thread recorded as the deaths_debt fact", entity=pc)
        ch.narration.append(f"{b.get('bargainer')} ends the danger in its own way")
    elif option_id == "lc.left_for_dead":  # rule: 07.5.6
        restore_vitality(ctx, pc, to=1, reason="left for dead", rule_id="07.5.6", writes=w)
        if victor:
            w.fact(victor, f"believes_dead:{pc}", True, truth="false", rule_id="07.5.6")
        w.fact(pc, "setback.defeated", {"victor": victor, "manner": "left_for_dead"}, rule_id="07.5.6")
        ch.advance_time = "watches:1"
        w.coarse("07.6.4", "what a folk victor takes goes to a cache the DM frames (M5 caches)", entity=pc)
    elif option_id == "lc.rout":  # rule: 07.5.7
        restore_vitality(ctx, pc, to=1, reason="rout", rule_id="07.5.7", writes=w)
        n = int(ctx.rules.severity_units()["S4"])
        cid = world_cost(ctx, w, victor, menu.situation.rout_clock, n,
                         rout_candidates(st, [victor] if victor else []))
        w.fact(pc, "setback.retreated", {"severity": "S4", "clock": cid}, rule_id="07.5.7")
    elif option_id == "lc.reprieve":  # rule: 07.5.8
        stabilize(ctx, pc, brink_wound=False, writes=w)
        restore_vitality(ctx, pc, to=quarter, reason="reprieve", rule_id="07.5.8", brink_wound=False, writes=w)
        w.add_quantity(pc, "fate", -menu.fate_cost, reason="reprieve", rule_id="01.16.4")
        w.fact(pc, "reprieves_taken", int(st.fact_value(pc, "reprieves_taken", 0) or 0) + 1, rule_id="07.5.8")
    elif option_id == "lc.last_stand":  # rule: 07.5.9
        w.fact(pc, "last_stand", {"actions": 3, "critical": True, "focus_free": True}, rule_id="07.5.9")
        ch.last_stand = True
        ch.stays_in_scene = True
    elif option_id == "lc.gamble":  # rule: 07.5.10
        ch.gamble_offer = {"verb": "verb.endure", "attribute": "endurance", "dc": dc_of(ctx.rules, "moderate"),
                           "modifier": endure_modifier(st, pc), "odds": dict(menu.gamble), "lethal": True,
                           "auto_commit": False}
    elif option_id == "lc.road_ends":  # rule: 07.5.11
        restore_vitality(ctx, pc, to=1, reason="the road ends", rule_id="07.5.11", writes=w)
        w.fact(pc, "career.ending", "retirement", rule_id="07.5.11")
        ch.ending = "retirement"
    if option_id not in ("lc.last_stand", "lc.gamble"):
        _after(w, pc, data, f"{data['name']}: {o.price}")
    ch.events = w.events[start:]
    return ch


@dataclass
class GambleResult:
    events: list[Event]
    natural: int
    degree: str
    margin: int
    result: str  # free | live | choose | death
    choices: list[dict[str, str]] = field(default_factory=list)  # for "choose": options 1-5 still available
    pause_id: str | None = None


def resolve_gamble(ctx: Any, pc: str, menu: Menu, *, natural: int | None = None,
                   writes: Writes | None = None) -> GambleResult:  # rule: 07.5.10
    """Roll the Gamble once the player confirmed its OFFER: Endure with Endurance against Moderate (15)."""
    st: WorldState = ctx.state
    w = writes or Writes.of(ctx, source="07.5.10")
    start = len(w.events)
    mod = endure_modifier(st, pc)
    nat = roll_d20(ctx, f"the Gamble {pc}", natural)
    deg, margin = degree(nat, mod, dc_of(ctx.rules, "moderate"))
    data = next(x for x in _option_data(ctx.rules) if x["id"] == "lc.gamble")
    out = GambleResult([], nat, deg, margin, "death")
    if deg == "critical_success":  # as a Reprieve at no cost
        stabilize(ctx, pc, brink_wound=False, writes=w)
        v = w.quantity(pc, VITALITY)
        mx = (v.max if v is not None and v.max is not None else 0) or 0
        restore_vitality(ctx, pc, to=math.ceil(mx / 4), reason="the Gamble: free", rule_id="07.5.10",
                         brink_wound=False, writes=w)
        out.result = "free"
        _after(w, pc, {**data, "mark": "none", "world_writes": []}, "The Gamble: walked away free")
    elif deg == "success":  # stabilized and overlooked, a brink wound, nothing taken, no mark
        restore_vitality(ctx, pc, to=1, reason="the Gamble: overlooked", rule_id="07.5.10", writes=w)
        out.result = "live"
        _after(w, pc, {**data, "mark": "none", "world_writes": []}, "The Gamble: overlooked, alive")
    elif deg == "failure" and margin >= -3:
        out.result = "choose"
        sub = [o for o in menu.offered() if o.order <= 5]
        out.choices = [{"id": o.id, "label": f"({o.order}) {o.name} — {o.price}"} for o in sub]
        pid = w.mint(ids.PAUSE)
        out.pause_id = pid
        w.extend([Event.of("pause_opened", source="07.5.10", rule_id="07.5.10", pause=PauseRecord(
            pause_id=pid, kind="last_chance", prompt="The Gamble nearly failed: choose a price and pay it in full.",
            choices=out.choices, default_choice=None, detail={"pc": pc, "via_gamble": True}))])
    else:
        w.fact(pc, "gamble_failed", True, rule_id="07.5.10")
        write_death(ctx, pc, key2="b", writes=w)
    w.log("gamble", {"pc": pc, "natural": nat, "modifier": mod, "degree": deg, "result": out.result},
          rule_id="07.5.10")
    out.events = w.events[start:]
    return out


# ------------------------------------------------------------------------------------------- death and endings


class DeathRefused(ValueError):
    """INV-6: the Two-Key rule refuses a death write that lacks a key."""


def keys(state: WorldState | Writes, pc: str) -> tuple[bool, bool]:  # rule: 07.3.1
    # rule: 07.3.9
    """(Key 1, Key 2) as the record holds them now."""
    key1 = bool(state.fact_value(pc, "lethal_key")) or bool(state.fact_value(pc, "voluntary_last_stand"))
    choice = state.fact_value(pc, "threshold_choice")
    key2 = (choice == "lc.last_stand" and bool(state.fact_value(pc, "last_stand"))) or (
        choice == "lc.gamble" and bool(state.fact_value(pc, "gamble_failed"))) or bool(
        state.fact_value(pc, "voluntary_last_stand"))
    return key1, key2


def write_death(ctx: Any, pc: str, *, key2: str, writes: Writes | None = None) -> list[Event]:  # rule: 07.3.1
    """The only write of `harm_state.dead` for a PC. Refused (DeathRefused) unless both keys hold. Under
    `pref.death.mode: retire` it resolves as The Road Ends instead (07.5.14)."""
    w = writes or Writes.of(ctx, source="07.3.1")
    start = len(w.events)
    k1, k2 = keys(w, pc)
    if not (k1 and k2):
        raise DeathRefused(f"{pc}: Key 1 {'holds' if k1 else 'missing'}, Key 2 {'holds' if k2 else 'missing'}")
    if ctx.state.meta.get("pref.death.mode") == "retire":  # rule: 07.5.14
        if harm_state(w, pc) == DYING:
            stabilize(ctx, pc, writes=w)
        w.fact(pc, "career.ending", "retirement", rule_id="07.5.14")
        return w.events[start:]
    w.fact(pc, "dying_step", 0, rule_id="07.3.1")
    w.fact(pc, "harm_state", DEAD, rule_id="07.3.1")
    w.fact(pc, "defeated", {"manner": "dead", "key2": key2}, rule_id="07.3.1")
    w.fact(pc, "career.ending", "death", rule_id="07.3.1")
    return w.events[start:]


def finish_last_stand(ctx: Any, pc: str, *, witnesses: list[str] | None = None,
                      writes: Writes | None = None) -> list[Event]:  # rule: 07.5.9
    """When the last stand's turn ends: dead, Key 1 on record and Key 2 (a); the legend line."""
    w = writes or Writes.of(ctx, source="07.5.9")
    start = len(w.events)
    w.fact(pc, "chronicle_line", {"legend": True, "witnesses": witnesses or []}, rule_id="07.5.9",
           only_if_changed=False)
    write_death(ctx, pc, key2="a" if not w.fact_value(pc, "voluntary_last_stand") else "c", writes=w)
    return w.events[start:]


def confirm_voluntary_last_stand(ctx: Any, pc: str, source: str, *, sign: str,
                                 writes: Writes | None = None) -> list[Event]:  # rule: 07.5.13
    """The player confirmed, out of fiction, an act whose stated outcome is the character's death: the `chosen`
    context is written if none holds (Key 1), and the last stand runs from the current harm state (Key 2 c)."""
    w = writes or Writes.of(ctx, source="07.5.13")
    start = len(w.events)
    if lethal_mod.context(w, source) is None:
        lethal_mod.record_warning(ctx, lethal_mod.chosen_trigger(pc, source), sign=sign, writes=w)
    w.fact(pc, "voluntary_last_stand", {"source": source}, rule_id="07.5.13")
    w.fact(pc, "last_stand", {"actions": 3, "critical": True, "focus_free": True}, rule_id="07.5.9")
    return w.events[start:]


def active_pc(state: WorldState) -> str | None:
    """The character whose story is being played: `meta['pc.active']`, else the most recently created PC."""
    p = state.meta.get("pc.active")
    if isinstance(p, str) and p in state.entities:
        return p
    found = pcs(state)
    return found[-1] if found else None


def ending_state(state: WorldState, pc: str | None = None) -> str | None:
    """None | "death" | "retirement" | "career_end" for the active PC (FR-009)."""  # rule: 07.3.1
    p = pc or active_pc(state)
    if p is None:
        return None
    if harm_state(state, p) == DEAD:
        return "death"
    e = state.fact_value(p, "career.ending")
    return str(e) if e in ("death", "retirement", "career_end") else None


def h_07_career_end(ctx: Any) -> list[Event]:  # rule: 07.11.6
    """`h.07.career_end` (scene_end, phase 8): a written `career_end` (the fourth break, M2) hands the character to
    ch.11's retirement procedure: the ending is recorded for the epilogue."""
    w = Writes.of(ctx, source="h.07.career_end")
    for p in pcs(ctx.state):
        if ctx.state.fact_value(p, "career_end") and not ctx.state.fact_value(p, "career.ending"):
            w.fact(p, "career.ending", "career_end", rule_id="07.11.6")
    return w.events
