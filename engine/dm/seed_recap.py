"""What a world-seed step made, told in a few plain lines (the player's recap; PR-12-9 step 3, 12.16.3).

`engine.gen.world_seed.summary` keeps the rules' own `[SEED n/14]` dump for the record; this is what the player
reads instead: at most a few sentences, the shown parts only, and who chose what.

    recap(step, st, words)   # -> ["The Cold Wolds — a frontier: ...", "...", "You chose the trouble; the dice ..."]
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from engine.dm import setup_text as T
from engine.gen._seed_steps import STEP_QUESTIONS
from engine.gen.world_seed import SeedAnswer, SeedStep

AUTO = ("ws.q.hybrid_none", "ws.q.relics_magic")  # taken by the dice, never asked (setup.yaml says why)
_TERRAIN = {"deepwood": "deep forest", "glacier": "glaciers", "ruin": "ruins", "mountains": "mountains",
            "settlement": "settled land"}
_ROLE = {"rulers": "who rule"}


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:]


def _low(s: str) -> str:
    return s if s[1:2].isupper() else s[:1].lower() + s[1:]


def _and(items: list[str]) -> str:
    items = [i for i in items if i]
    return items[0] if len(items) == 1 else (", ".join(items[:-1]) + " and " + items[-1] if items else "")


def _answer(step: SeedStep, qid: str) -> Any:
    return next((a.answer for a in reversed(step.answers) if a.question == qid), None)


def _label(qid: str, oid: Any, st: dict[str, Any]) -> str:
    return T.option_label(qid, str(oid), str(oid).replace("_", " "), st.get("tier"))


def _said(qid: str, st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> str:
    """The player's own words for a question in quotes, else the plain label of the option."""
    if words.get(qid):
        return f'"{words[qid]}"'
    return _label(qid, _answer(step, qid), st)


def _places(st: dict[str, Any]) -> dict[str, Any]:
    return dict(st["S"]["_places"])


def _terrain(tag: str) -> str:
    last = tag.rsplit(".", 1)[-1]
    return _TERRAIN.get(last, last.replace("_", " "))


# ------------------------------------------------------------------------------------------- steps


def _s1(st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> list[str]:
    return [f"{_cap(st['region_name'])} — {_low(_said('ws.q.wound', st, step, words))}.",
            f"Weather — {_said('ws.q.climate', st, step, words)}.",
            f"The trouble began {int(st['ctx']['era_age']):d} years ago."]


def _s2(st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> list[str]:
    def short(q: str) -> str:
        if words.get(q):
            return f'{_cap(T.question_what(q))}: "{words[q]}".'
        return T.option_short(q, str(_answer(step, q))) or ""

    extra = [e for e in (_answer(step, "ws.q.extra_impossible") or []) if e != "none"]
    lines = [" ".join(x for x in (short("ws.q.magic_level"), short("ws.q.magic_law")) if x),
             " ".join(x for x in (short("ws.q.arcane_source"), short("ws.q.spirits")) if x)]
    if extra:
        lines.append("Also impossible here: " + _and([_low(_label("ws.q.extra_impossible", e, st))
                                                       for e in extra]) + ".")
    lines.append(" ".join(x for x in (short("ws.q.regrowth"), short("ws.q.closed_school")) if x))
    return [x for x in lines if x]


def _s3(st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> list[str]:
    keepers = st["keepers"]
    named = [f"{k['name']} ({(T.question('ws.q.keepers').get('short') or {}).get(k.get('form'), k.get('kind', ''))})"
             for k in keepers]
    count = {2: "Two", 3: "Three", 4: "Four"}.get(len(keepers), str(len(keepers)))
    who = (st.get("bargainer") or {}).get("who")
    if not who:
        death = "No one bargains with the dying."
    elif str(who).startswith("arch.fey"):
        death = "A fey lord may offer the dying a deal, for a price paid later."
    elif str(who).startswith("arch."):
        death = "A tempter may offer the dying a deal, and always collects."
    else:
        k = next((k for k in keepers if k.get("id") == who), None)
        death = f"{k['name'] if k else 'The god of death'} meets the dying, and may bargain."
    return [f"{count} gods (keepers) answer prayers: {_and(named)}.", death]


def _s4(st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> list[str]:
    plural = T.seed("peoples") or {}
    levels = T.seed("presence") or {}
    groups = []
    for lvl in ("common", "uncommon", "rare"):
        who = [str(plural.get(p["origin"], p["origin"].rsplit(".", 1)[-1])) for p in st["peoples"]
               if p["present"] == lvl]
        if who:
            groups.append(f"{levels.get(lvl, lvl)} {_and(who)}")
    names = T.seed("tongues") or {}
    tongues = []
    for t in st["tongues"]["list"]:
        lic = str(t["license"])
        name = str(names.get(lic) or lic.rsplit(".", 1)[-1].replace("_", " ").capitalize())
        tongues.append(f"{name} (here called {t['region_name']})" if t.get("region_name") else name)
    return [f"Who lives here: {'; '.join(groups)}.", f"Languages: {_and(tongues)}."]


def _s5(st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> list[str]:
    P = _places(st)
    rings = {int(k): v for k, v in st["areas_by_ring"].items()}
    near = [f"{P[a]['name']} ({_terrain(P[a]['terrain'][0])})" for a in rings.get(1, []) if P[a]["known"]]
    far: list[str] = []
    for r in sorted(k for k in rings if k > 1):
        for a in rings[r]:
            t = _terrain(P[a]["terrain"][0])
            if P[a]["known"] and t not in far:
                far.append(t)
    site = _said("ws.q.haven_site", st, step, words)
    out = [f"Your home town stands {_low(site)}." if not words.get("ws.q.haven_site") else f"Your home town: {site}."]
    if near:
        out.append(f"Close by: {_and(near)}.")
    out.append(f"Further out: {_and(far)}; beyond that, unknown country." if far else "Beyond that, unknown country.")
    return out


def _s6(st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> list[str]:
    P = _places(st)
    hav = P[st["hid"]]
    desc = str(hav.get("desc", "")).split(", the haven of")[0]
    inside = []
    for kind, b in st["blds"].items():
        if kind == "gate":
            continue
        name = str(P[b]["name"])
        inside.append(name if kind in name.lower() or kind in ("hall", "market") else f"{name} ({kind})")
    return [f"{hav['name']}: {desc}. This is your home base (the haven).", f"In town: {_and(inside)}."]


def _s7(st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> list[str]:
    seat = "village" if st.get("tier") == "village" else "town"
    names = [f"{f['name']} ({_ROLE[f['role']]} the {seat})" if f.get("role") in _ROLE else str(f["name"])
             for f in st["factions"]]
    more = len(names) - 4
    return [f"Who holds power here: {_and(names[:4] + ([f'{more:d} more'] if more > 0 else []))}."]


def _s8(st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> list[str]:
    npcs = st["S"]["npcs"]
    rulers = next((f["name"] for f in st["factions"] if f.get("role") == "rulers"), None)
    picked = [n for n in npcs if rulers and n["role"] == f"head of {rulers}"]
    picked += [n for n in npcs if n["role"] in ("innkeeper", "smith", "captain of the gate", "healer")]
    shown = [f"{n['name']} ({n['role'].replace(' of The ', ' of the ')})" for n in picked[:4]]
    home = _places(st)[st["hid"]]["name"]
    return [f"{len(npcs):d} people you may meet in and beyond {home}, among them {_and(shown)}."]


def _s9(st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> list[str]:
    P = _places(st)
    known = [P[s]["name"] for s in st["sites"] if P[s]["known"]]
    head = _and(known[:3] + ([f"{len(known) - 3:d} more"] if len(known) > 3 else []))
    trouble = _and([_low(str(s["title"])) for s in st["situations"]])
    return [f"Dangerous places people talk about: {head}.", f"Trouble brewing: {trouble}."]


def _s10(st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> list[str]:
    return ["The dice stocked the wilds with beasts and dangers. You will meet them in play."]


def _s11(st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> list[str]:
    n = len(st["rumor_tables"][0]["results"])
    return [f"{n:d} rumors are going round town. Some of them are true."]


def _s12(st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> list[str]:
    c = st["calendar"]
    months = list(c["months"])
    if _answer(step, "ws.q.month_names") == "counted" or not months:
        first = 'The months are just counted ("the second month of spring").'
    else:
        first = f"The months have names, from {months[0]} to {months[-1]}."
    fest = _and([f["name"] for f in c.get("festivals", [])])
    return [first, f"Years are counted as {c['era']['name']}." + (f" Festivals: {fest}." if fest else "")]


def _s13(st: dict[str, Any], step: SeedStep, words: dict[str, str]) -> list[str]:
    o = st["opening"]
    P = _places(st)
    start = o["start"]
    what = _said("ws.q.inciting", st, step, words)
    what = f"In your words: {what}." if words.get("ws.q.inciting") else f"{_cap(what)}."
    out = [f"It begins at {start['watch']} on {start['date']}, at {P[start['place']]['name']}.", what]
    if st.get("pregens"):
        out.append(f"If you would rather not make a character, {len(st['pregens']):d} ready-made ones are waiting.")
    return out


_STEPS: dict[int, Callable[[dict[str, Any], SeedStep, dict[str, str]], list[str]]] = {
    1: _s1, 2: _s2, 3: _s3, 4: _s4, 5: _s5, 6: _s6, 7: _s7, 8: _s8, 9: _s9, 10: _s10, 11: _s11, 12: _s12, 13: _s13}


# ------------------------------------------------------------------------------------------- the recap


def who_chose(step: SeedStep) -> str:
    """'You chose the climate; the dice chose the trouble.' (or all one way); "" for a step that asks nothing."""
    if not STEP_QUESTIONS.get(step.n):
        return ""
    seen: dict[str, str] = {}
    for a in step.answers:
        if a.question not in AUTO:
            seen[a.question] = a.source
    mine = [T.question_what(q) for q, s in seen.items() if s != "oracle"]
    rolled = [T.question_what(q) for q, s in seen.items() if s == "oracle"]
    if mine and rolled:
        key = "rolled_some" if len(mine) <= 2 else "rolled_rest"
        return str(T.seed("summary", key)).format(mine=_and(mine), rolled=_and(rolled))
    return str(T.seed("summary", "rolled_all" if rolled else "chose_all")) if mine or rolled else ""


def recap(step: SeedStep, st: dict[str, Any], words: dict[str, str] | None = None) -> list[str]:  # rule: 12.16.3
    """A few plain lines: what the step made (shown parts only), then who chose what."""
    lines = _STEPS[step.n](st, step, dict(words or {}))
    tail = who_chose(step)
    return [x for x in lines if x] + ([tail] if tail else [])


def rolled(step: SeedStep) -> list[SeedAnswer]:
    """The answers the dice gave in this step that the player may re-roll (auto-taken ones excluded)."""
    return [a for a in step.answers if a.source == "oracle" and a.question not in AUTO]


__all__ = ["AUTO", "recap", "rolled", "who_chose"]
