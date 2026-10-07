"""Improvised adversaries (PR-09-2, 09.4.8): four classifications in, a full stat block (PR-09-1) out.

    adv = improvise("arch.herd_beast", band=2, role="brute", variant="elite", name="the one-eyed boar")
    adv.record          # the adversary record of T-09-14 (what adversaries.yaml holds for a bestiary entry)
    adv.ruling_signature  # "arch.herd_beast+2+brute+elite": PR-09-2 step 1 reuses an earlier ruling by it

The classifications (archetype, band, role, variant) are the model's (`[J]`); everything after is `[D]`. The
build is a port of `_process/simulation/09-gen_data09.py#build` reading `data/archetypes.yaml`, with one input
precomputed: the Vitality solve against PR-09-4's estimator and the advisories (09.4.4-09.4.5), read from
`data/adversary_solve.json` (`build_tables.py`). Milestone 2 (T085) ports the estimator and drops the table.
A single creature only: mobs and swarms of several members (09.4.7) come with conflict in Milestone 2.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from engine.gen import _data

Variant = Literal["minion", "standard", "elite", "solo"]
VARIANTS = ("minion", "standard", "elite", "solo")
ATTRS = ["might", "agility", "endurance", "wits", "intellect", "presence", "resolve"]
WORDS = ["trivial", "easy", "fair", "hard", "lethal"]
NERVES: dict[str, int | None] = {"skittish": 4, "steady": 6, "resolute": 8, "fearless": None}     # T-09-5 nerve clocks
TIER_LADDER = ["easy", "moderate", "hard", "very_hard", "legendary"]                              # T-09-16
RARITY_SHIFT = {"common": 0, "uncommon": 1, "rare": 2, "legendary": 3}                            # T-09-16
LINGERING_RIDERS = {"pow.bleed", "pow.burning_touch"}                                              # T-09-6 (I-090)
LESSER = {"pow.frenzy", "pow.shield_wall", "pow.pack_tactics", "pow.ambush_strike", "pow.mend_kin", "pow.blink",
          "pow.glamour", "pow.spell_turning", "pow.rally_cry", "pow.call_kin", "pow.drag_off", "pow.second_wind",
          "pow.shrug"}                                                                             # T-09-6
FREE = {"pow.flight", "pow.swimmer", "pow.climber", "pow.burrower", "pow.night_eyes", "pow.keen_scent",
        "pow.tremorsense", "pow.mindless", "pow.deathless", "pow.unliving", "pow.amorphous", "pow.incorporeal",
        "pow.regenerate"}                                                                          # T-09-6
AURAS = ("pow.heat_aura", "pow.cold_aura", "pow.unholy_aura")
OBJECTIVE = {"kill": "kill", "capture": "capture", "rob": "rob", "ransom": "capture", "drive_off": "drive_off",
             "drag_to_lair": "capture", "leave": "defeat"}


class ImprovisedAdversary(BaseModel):
    """An improvised creature: its four inputs, its headline numbers, and the full record."""

    id: str
    name: str
    archetype: str
    band: int
    role: str
    variant: Variant
    vitality: int
    guard: int
    tempo: int
    reduction: int
    focus: int
    attacks: list[dict[str, Any]]
    powers: list[str]
    morale: dict[str, Any]
    lethal_context: bool
    advisory_alone: dict[str, str]
    ruling_signature: str
    record: dict[str, Any]


@functools.lru_cache(maxsize=1)
def _doc() -> dict[str, Any]:
    return _data.load("archetypes.yaml")


@functools.lru_cache(maxsize=1)
def _arch() -> dict[str, dict[str, Any]]:
    return {a["id"]: a for a in _doc()["archetypes"]}


@functools.lru_cache(maxsize=1)
def _powers() -> dict[str, dict[str, Any]]:
    return {p["id"]: p for p in _doc()["powers"]}


@functools.lru_cache(maxsize=1)
def _solve() -> dict[str, list[Any]]:
    return json.loads((Path(__file__).resolve().parent / "data" / "adversary_solve.json").read_text(encoding="utf-8"))


def ruling_signature(archetype: str, band: int, role: str, variant: str) -> str:
    """# rule: PR-09-2 step 1 -- the ruling signature an earlier improvisation of this creature is found by."""
    return f"{archetype}+{band:d}+{role}+{variant}"


def validate(archetype: str, band: int, role: str, variant: str) -> dict[str, Any]:
    """# rule: PR-09-1 step 1 -- the band inside the archetype's bands, the role among its roles, a known variant."""
    if archetype not in _arch():
        raise ValueError(f"unknown archetype {archetype}")
    a = _arch()[archetype]
    if not a["bands"][0] <= band <= a["bands"][1]:
        raise ValueError("{} is fielded at bands {}, not {:d} (09.4.8: the archetype's bands are its nature)".format(archetype, a["bands"], band))
    if role not in a["roles"]:
        raise ValueError("{}'s roles are {}, not {} (09.4.8)".format(archetype, a["roles"], role))
    if variant not in VARIANTS:
        raise ValueError(f"variant {variant} is not one of {VARIANTS}")
    return a


def power_premium(powers: list[str], riders: list[str], abilities: list[str]) -> float:
    """# rule: 09.4.3 -- the power premium (T-09-6), capped at 0.4."""
    prem = _doc()["band_tables"]["power_premium"]
    p = 0.0
    for x in set(powers) | set(riders):
        if x in FREE:
            continue
        if x in riders:
            p += prem["lingering_rider" if x in LINGERING_RIDERS else "rider"]
        elif x in LESSER:
            p += prem["lesser"]
        elif x == "pow.summon_dead":
            p += prem["summon"]
        elif _powers()[x]["kind"] == "trigger" and x in AURAS:
            p += prem["aura"]
        else:
            p += prem["action"]
    p += prem["ability"] * len(abilities)
    return min(0.4, p)


def build(archetype: str, band: int, role: str, variant: Variant = "standard", *, adv_id: str | None = None,
          name: str | None = None, depth: str = "walk-on") -> dict[str, Any]:
    """# rule: PR-09-1 -- archetype + band + role + variant -> the adversary record (no overrides: 09.4.8)."""
    a = validate(archetype, band, role, variant)
    b = band
    bt = _doc()["band_tables"]
    c = bt["competence"][b]
    at = {x: bt["rungs"][a["attribute_rungs"][x]][b] for x in ATTRS}
    trained = set(a["trained_defenses"])
    gear = list(a["gear"])
    shield = 1 if any("shield" in g for g in gear) else 0
    defenses = {"guard": 10 + at["agility"] + c + shield}
    for x in ATTRS:
        defenses[x] = 10 + at[x] + (c if x in trained else 0)
    tempo = 10 + at["wits"]
    atks: list[dict[str, Any]] = []
    for k in a["attacks"]:
        heavy = bool(k["heavy"])
        sev = (bt["heavy_severity"][b] if heavy else bt["standard_severity"][b]) + k["off"]
        sev = max(1, min(5, sev))
        if sev >= 4 or k["shape"]:
            heavy = True
        atks.append(dict(id=k["id"], name=k["name"], verb=k["verb"], attribute=k["attr"], modifier=at[k["attr"]] + c,
                         harm={"severity": f"S{sev:d}", "harm_tags": list(k["harm"])}, bands=k["bands"], weight=k["weight"],
                         action_cost=1, shape=k["shape"], windup=heavy, site=k["site"], riders=list(k["riders"]),
                         primary=bool(k.get("primary"))))
    ranged = [x for x in atks if x["weight"] in ("bow", "crossbow")]
    working = [x for x in atks if x["weight"] == "working"]
    if role == "archer" and ranged:
        prim = ranged[0]
    elif role == "caster" and working:
        prim = working[0]
    else:
        prims = [x for x in atks if x["primary"] and not x["windup"]] or [x for x in atks if not x["windup"]] or atks
        prim = prims[0]
    for x in atks:
        x["primary"] = x is prim
    if variant == "solo" and not any(x["windup"] for x in atks):
        hv = dict(prim)
        hv.update(id=prim["id"] + "_full", name=prim["name"] + " (full force)", windup=True, primary=False,
                  harm={"severity": "S{:d}".format(bt["heavy_severity"][b]), "harm_tags": prim["harm"]["harm_tags"]})
        atks.append(hv)
    heavy_sev = max([int(x["harm"]["severity"][1]) for x in atks if x["windup"] and not x["shape"]] or [0]) or None
    arm = a["armor"]
    red = bt["armor"]["{}.{}".format(arm["kind"], arm["rung"])][b - 1]
    if arm["kind"] == "worn":
        g = " ".join(gear)
        red = 3 if "plate" in g else 2 if ("mail" in g or "scale" in g or "brigandine" in g) else \
            1 if any(x in g for x in ("leather", "hide", "padded")) else red
    powers = list(dict.fromkeys(a["powers"]))
    if variant == "solo":
        powers += ["pow.shrug", "pow.second_wind"]
    powers = [p for p in powers if not (_powers()[p].get("min_band") and b < _powers()[p]["min_band"])]   # step 7
    riders = sorted({r for x in atks for r in x["riders"]})
    taken = 1.0
    for e in a["traits"]:
        if e["effect_id"] == "eff.harm_resistance":
            ht = e["params"]["harm_tags"]
            if "harm.physical" in ht:
                taken = min(taken, 0.5)
            elif any(t.startswith("harm.physical.") for t in ht):
                taken = min(taken, 0.75)
    if "pow.incorporeal" in powers:
        taken = min(taken, 0.5)
    regen = 3 if "pow.regenerate" in powers else 0
    nerve = a["morale"]["nerve"]
    if variant == "minion" and nerve in ("steady", "resolute"):
        nerve = {"steady": "skittish", "resolute": "steady"}[nerve]
    if variant in ("elite", "solo") and nerve in ("skittish", "steady"):
        nerve = {"skittish": "steady", "steady": "resolute"}[nerve]
    eff_band = b + (1 if variant == "elite" else 0)
    if variant == "minion":
        reaction: list[str] = []
    elif variant == "solo":
        reaction = ["opportunity_strike", "fend"]
    else:
        reaction = [] if eff_band <= 1 else ["opportunity_strike"] if eff_band == 2 else ["opportunity_strike", "fend"]
    if a["reaction"] is False:
        reaction = []
    fend = "fend" in reaction
    prem = power_premium(powers, riders, [])
    base_vit, fidelity, comp, adv_alone, adv_noc, _errs = _solve()[f"{archetype}|{b:d}|{role}|{variant}"]
    line = dict(atk=prim["modifier"], guard=defenses["guard"], sev=int(prim["harm"]["severity"][1]), heavy=heavy_sev, red=red,
                fend=fend, morale=NERVES[nerve], tempo=tempo, taken=taken, regen=regen)
    if comp:                                                    # 09.4.5: severity compensation on the primary
        line["sev"] = max(1, min(5, line["sev"] + comp))
        if line.get("heavy"):
            line["heavy"] = max(1, min(5, line["heavy"] + comp))
        for x in atks:
            s0 = int(x["harm"]["severity"][1])
            if x["primary"] or (x["windup"] and not x["shape"]):
                x["harm"]["severity"] = f"S{max(1, min(5, s0 + comp)):d}"
        for x in atks:
            if int(x["harm"]["severity"][1]) >= 4 or x["shape"]:
                x["windup"] = True
    vv = bt["variant_vitality"]
    mult = vv[variant] if not isinstance(vv[variant], dict) else vv[variant][b]
    vit = max(1, int(round(base_vit * mult)))
    focus = 0 if variant == "minion" else bt["focus_base"][b] + (1 if variant == "elite" else 2 if variant == "solo" else 0) \
        + (1 if role == "caster" else 0)
    dc_attrs = {e["params"]["effect_dc_source"].split(".")[1] for p in powers + riders for e in _powers()[p]["effects"]
                if e["params"].get("effect_dc_source")}
    effect_dc = {x: 10 + at[x] + c for x in sorted(dc_attrs)}
    disp = a["defeat_disposition"]
    lethal = bool(a["lethal_context"] or disp == "kill")
    s4 = any(int(x["harm"]["severity"][1]) >= 4 for x in atks)
    ctags = list(a["creature_tags"])
    competence = [{"tag": t, "value": c} for t in a["evidence_tags"]] + [{"tag": "deed.martial.unarmed", "value": c}]
    beh = list(a["behaviors"])
    if variant == "solo":
        beh = ["beh.09.solo_overlay"] + beh
    lore_i = TIER_LADDER.index(bt["lore_base_tier"][b]) + RARITY_SHIFT[a["lore"]["rarity"]]
    resist_tags = sorted({t for e in a["traits"] if e["effect_id"] == "eff.harm_resistance" for t in e["params"]["harm_tags"]})
    counter = ("fire or acid (stops regeneration)" if regen else
               ("the harm or weapon its resistance does not cover (" + ", ".join(resist_tags) + ")") if taken < 1.0 else None)
    loot = a["loot"]
    return {
        "id": adv_id or "adv.improvised.{}_{:d}_{}_{}".format(archetype.split(".", 1)[1], b, role, variant), "name": name or a["name"],
        "archetype": archetype, "threat_band": b, "variant": variant, "role": role,
        "default_behavior_role": a["default_behavior_role"] or "melee",
        "tags": list(dict.fromkeys(ctags + a["harm_tags"])), "creature_tags": ctags, "size": a["size"], "members": 1,
        "swarm": False, "leader": False, "npc_depth": depth, "attributes": at, "competence": competence,
        "defenses": defenses, "tempo": tempo, "vitality": vit,
        "reduction": {"amount": red, "harm_tags": ["harm.physical"], "kind": arm["kind"],
                      "no_gaps": arm.get("no_gaps", False) if arm["kind"] == "natural" else False},
        "resistances": a["traits"], "attacks": atks, "abilities": [], "powers": powers, "focus": focus,
        "effect_dc": effect_dc, "reaction": {"count": 1 if reaction else 0, "kinds": reaction}, "behaviors": beh,
        "morale": {"nerve": nerve, "segments": NERVES[nerve], "break_then": None if nerve == "fearless" else a["morale"]["break_then"]},
        "pace": a["pace"], "tells": dict(a["tells"]), "weak_spot": a["weak_spot"], "lethal_context": lethal,
        "lethal_causes": sorted(set((["archetype"] if lethal else []) + (["severity"] if s4 else []))),
        "defeat_disposition": disp, "kill_when": a["kill_when"], "captive_fate": a["captive_fate"],
        "can_bargain": a["can_bargain"], "dread": a["dread"], "speaks": a["speaks"], "mind": a["mind"],
        "reaction_roll": a["reaction_roll"], "objective": (a.get("encounter") or {}).get("objective_default") or OBJECTIVE[disp],
        "lore": {"deed_tag": a["lore"]["deed_tag"], "rarity": a["lore"]["rarity"],
                 "dc_tier": TIER_LADDER[min(lore_i, len(TIER_LADDER) - 1)]},
        "loot": {"yield": "always" if depth == "principal" else loot.get("yield", "trophy"), "tier_cap": b,
                 "trophy_base": loot.get("trophy_base"), "flaw": loot.get("flaw"), "gear": gear, "purse": a["purse"]},
        "advisory_alone": {f"P{i + 1:d}": WORDS[int(ch)] for i, ch in enumerate(adv_alone)},
        "advisory_without_counter": {f"P{i + 1:d}": WORDS[int(ch)] for i, ch in enumerate(adv_noc)} if adv_noc else None,
        "counter": counter,
        "calibration": {"premium": round(prem, 2), "solved_vitality": base_vit, "fidelity": fidelity,
                        "severity_compensation": comp,
                        "line": {k: line[k] for k in ("atk", "guard", "sev", "heavy", "red", "fend", "morale", "tempo",
                                                      "taken", "regen")}},
        "template_id": "improvised", "lifecycle": "provisional", "basis": ["09.4 PR-09-1", "09.4.8 PR-09-2", archetype],
    }


def improvise(archetype: str, band: int, role: str, variant: Variant = "standard", *, name: str | None = None,
              adv_id: str | None = None) -> ImprovisedAdversary:
    """# rule: PR-09-2 -- the DM's four classifications -> the built creature, ready to write and log as a ruling."""
    rec = build(archetype, band, role, variant, adv_id=adv_id, name=name)
    return ImprovisedAdversary(
        id=rec["id"], name=rec["name"], archetype=archetype, band=band, role=role, variant=variant,
        vitality=rec["vitality"], guard=rec["defenses"]["guard"], tempo=rec["tempo"], reduction=rec["reduction"]["amount"],
        focus=rec["focus"], attacks=rec["attacks"], powers=rec["powers"], morale=rec["morale"],
        lethal_context=rec["lethal_context"], advisory_alone=rec["advisory_alone"],
        ruling_signature=ruling_signature(archetype, band, role, variant), record=rec)
