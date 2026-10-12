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


def _names(indexes: list[str]) -> list[str]:
    return [srd.table("Spells")[i]["name"] for i in indexes]


def spell_fields(cls: str, level: int, sheet: dict[str, Any], rec: dict[str, Any]) -> dict[str, Any]:
    """The spell fields a level record needs: the first valid spells, highest spell level first. `sheet` is the
    character one level lower; a known caster also replaces its first spell on every even level."""
    need = create.level_spell_needs(cls, level)
    if not need:
        return {}
    sc, top, S = sheet.get("spellcasting") or {}, need["max_level"], srd.table("Spells")
    have = set(sc.get("cantrips", []) + sc.get("known", []) + sc.get("spellbook", []))

    def take(source: str, n: int, low: int, high: int, avoid: set[str]) -> list[str]:
        pool = _names(create.spell_pool(source, low, high))
        out = [x for x in sorted(pool, key=lambda x: -S[srd.spell(x)["index"]]["level"]) if x not in avoid][:n]
        assert len(out) == n, (cls, level, source)
        return out

    out: dict[str, Any] = {}
    if need["cantrips"]:
        out["cantrips"] = take(cls, need["cantrips"], 0, 0, have)
    if need["spells"]:
        out["spells"] = take(cls, need["spells"], 1, top, have)
    if need["first_list"]:
        out["prepared"] = take(cls, 1, 1, top, set())
    if need["secrets"]:  # Magical Secrets: spells of another class
        out["secrets"] = take("cleric", need["secrets"], 0, top, have | set(out.get("spells", [])))
    if need["replace"] and level % 2 == 0 and sc.get("known"):
        out["replace"] = {"from": sc["known"][0], "to": take(cls, 1, 1, top, have | set(out.get("spells", [])))[0]}
    if need["arcanum"]:
        out["arcanum"] = take(cls, 1, need["arcanum"], need["arcanum"], set())[0]
    choice = rec.get("choices", {}).get("feature.pact-boon")
    if choice and any(g.get("index") == "pact-of-the-tome" for g in srd.resolve(
            next(cs for cid, _, cs in create.level_sets(cls, level) if cid == "feature.pact-boon"), choice, "")):
        out["tome"] = take("wizard", create.TOME_CANTRIPS, 0, 0, set())
    if need["mastery"] or need["signature"]:
        book = sc["spellbook"] + out["spells"]
        by = lambda lv: [x for x in book if S[srd.spell(x)["index"]]["level"] == lv]
        if need["mastery"]:
            out["mastery"] = [by(1)[0], by(2)[0]]
        if need["signature"]:
            out["signature"] = by(3)[:2]
    return out


def auto_levels(ch: dict[str, Any], upto: int, rolled: list[int] | None = None) -> list[dict[str, Any]]:
    """Level records for levels 2..upto: fixed hit points, the two highest scores below 20 for each Ability Score
    Improvement, expertise in the first skills the character is proficient in, the first valid spells, other choices
    shifted until one builds."""
    cls = srd.find("Classes", ch["class"])["index"]
    levels: list[dict[str, Any]] = []
    for level in range(2, upto + 1):
        sheet, errs = create.build(ch, rolled, levels)
        assert sheet, errs
        rec: dict[str, Any] = {"hp": "fixed"}
        if create.has_asi(cls, level):
            low = sorted((a for a in create.ABILITIES if sheet["scores"][a] < 20), key=lambda a: -sheet["scores"][a])[:2]
            rec["asi"] = {a: 1 for a in low}
        sets = create.level_sets(cls, level)
        proficient = [x.rsplit(" ", 1)[0] for x in sheet["skills"].split(" (* proficient")[0].split(", ")
                      if x.endswith("*") and not x.endswith("**")]
        for shift in range(60):
            rec["choices"] = {cid: proficient[:cs["choose"]] if "expertise" in cid else pick(cs, shift + i)
                              for i, (cid, _, cs) in enumerate(sets)}
            rec = {k: v for k, v in rec.items() if k not in create.SPELL_KEYS} | spell_fields(cls, level, sheet, rec)
            built, errs = create.build(ch, rolled, levels + [rec])
            if built:
                break
        assert built, errs
        levels.append(rec)
    return levels


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
