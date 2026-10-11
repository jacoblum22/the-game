"""Pick valid choices automatically, for tests: every option set gets its options in turn, starting at `shift`."""
from typing import Any

from dm import create, srd


def pick(cs: dict[str, Any], shift: int) -> list[Any]:
    f, n = cs["from"], cs["choose"]
    if f["option_set_type"] == "options_array":
        opts = f["options"]
        out = []
        for k in range(n):
            o = opts[(shift + k) % len(opts)]
            letter = srd.LETTERS[(shift + k) % len(opts)]
            subs = _subchoices(o)
            label = o["item"]["name"] if isinstance(o, dict) and o["option_type"] == "reference" else letter
            out.append({"option": letter, "picks": [p for c in subs for p in pick(c, shift)]} if subs else label)
        return out
    if f["option_set_type"] == "equipment_category":
        eq = srd.table("Equipment-Categories")[f["equipment_category"]["index"]]["equipment"]
        return [eq[(shift + k) % len(eq)]["name"] for k in range(n)]
    langs = [x["name"] for x in srd.table("Languages").values()]
    return [langs[(2 + shift + k) % len(langs)] for k in range(n)]


def _subchoices(o: Any) -> list[dict[str, Any]]:
    if not isinstance(o, dict):
        return []
    if o["option_type"] == "choice":
        return [o["choice"]]
    if o["option_type"] == "multiple":
        return [c for i in o["items"] for c in _subchoices(i)]
    return []


def character(race: str, cls: str, shift: int = 0) -> dict[str, Any]:
    ch: dict[str, Any] = {"name": "Test", "race": race, "class": cls, "ability_method": "standard_array",
                          "base_scores": dict(zip(create.ABILITIES, [10, 14, 13, 12, 15, 8] if cls in ("cleric", "druid")
                                                  else [15, 14, 13, 8, 10, 12] if cls not in ("wizard",)
                                                  else [8, 14, 13, 15, 12, 10])),
                          "choices": {cid: pick(cs, shift + i) for i, (cid, _, cs) in enumerate(create.choices_for(race, cls))}}
    for cid in ch["choices"]:
        if "expertise" in cid:  # expertise must be in skills the character has: the class's first chosen two
            skills = [s for s in ch["choices"]["class.proficiencies.1"]]
            ch["choices"][cid] = [{"option": "a", "picks": skills[:2]}]
    sr = create.spell_rules(race, cls, None)
    if sr:
        ch["cantrips"] = [s["name"] for s in srd.class_spells(cls, 0)][:sr["cantrips"]]
        level1 = [s["name"] for s in srd.class_spells(cls, 1, sr["expanded"])]
        if "known" in sr:
            ch["spells"] = level1[:sr["known"]]
        if "spellbook" in sr:
            ch["spells"] = level1[:sr["spellbook"]]
        sheet_scores = {a: v for a, v in ch["base_scores"].items()}
        full = create.spell_rules(race, cls, sheet_scores)
        if full and "prepared" in full:
            # racial bonuses can raise the modifier: try counts until one fits
            pool = ch.get("spells") or level1
            ch["prepared"] = pool[:full["prepared"]]
    return ch


def build_any(race: str, cls: str) -> tuple[dict[str, Any] | None, list[str]]:
    """Try shifted choices until one set is valid (some first picks collide with background skills)."""
    errs: list[str] = []
    for shift in range(40):
        ch = character(race, cls, shift)
        for _ in range(3):
            sheet, errs = create.build(ch)
            if sheet:
                return sheet, []
            fix = [e for e in errs if e.startswith("prepared: choose exactly")]
            if not fix:
                break
            n = int(fix[0].rsplit(" ", 1)[1])
            pool = ch.get("spells") if (create.spell_rules(race, cls) or {}).get("how") == "spellbook" else \
                [s["name"] for s in srd.class_spells(cls, 1)]
            ch["prepared"] = pool[:n]
    return None, errs
