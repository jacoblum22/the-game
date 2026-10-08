"""Out-of-fiction blocks (12.15), rendered from state and computed records only, never from model text.

Every number, odds line, choice and rules matter goes in one of these blocks (12.14.4); the fiction carries none.
Each builder returns an `engine.dm.response.OofBlock(kind, text)` (the engine-api `Response.oof_blocks[]` item).

    blk = offer_block(frame, rules=rules, fate=1)                    # the [OFFER] pause block (12.15.2 template)
    blk.model_dump()                                                  # {"kind": "OFFER", "text": "..."}
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from typing import Any, Literal

from pydantic import BaseModel

from engine.dm.response import OofBlock, OofKind
from engine.harm import apply as harm_apply
from engine.harm import lethal as harm_lethal
from engine.harm.threshold import Menu, menu_text
from engine.resolve.costs import cost_severity
from engine.resolve.frame import offer_preview
from engine.resolve.gate import GateDecision
from engine.resolve.types import Frame, OfferPreview, RollResult
from engine.store.projection import WorldState

PLAYER_FACING = ("shown", "available")


class OfferView(BaseModel):
    """contracts/engine-api.md OfferView: what 01.7.1 says the OFFER shows (the front end's frame summary)."""

    restated_beat: str
    approach: dict[str, str | None]  # {verb, attribute, license}
    difficulty_words: str
    odds: dict[str, int]  # success_or_better_pct, critical_success_pct, critical_failure_pct, near_miss_pct
    stakes: Literal["safe", "risky", "dire"]
    lethal: bool
    threatened_cost: dict[str, str | None]  # {menu_id, form, severity_on_failure}
    alternate_cost: dict[str, str | None] | None  # {menu_id, form}
    only_natural_20: bool


# ------------------------------------------------------------------------------------------- helpers


def _block(label: str, first: str, rest: Iterable[str] = ()) -> str:
    """`[LABEL] first` with continuation lines aligned under the first line's text."""
    pad = " " * (len(label) + 3)
    return "\n".join([f"[{label}] {first}", *(pad + r for r in rest if r)])


def name_of(rules: Any, data_id: str | None) -> str:
    """A data entry's display name (verbs, licences, attributes, cost menus, conditions, abilities)."""
    if not data_id:
        return ""
    if rules is not None:
        try:
            if rules.has(data_id):
                n = rules.get(data_id).get("name")
                if n:
                    return str(n)
        except (KeyError, AttributeError, TypeError):
            pass
    tail = data_id.rsplit(".", 1)[-1]
    return tail.replace("_", " ").capitalize()


def _menu_form(rules: Any, menu_id: str | None, severity: str | None) -> str:
    """The cost menu's own example words for a severity (resolution.yaml cost_menu `forms.<S>.text`): for answers
    about a cost term (engine/dm/turn.py), never as this scene's price (P-083)."""
    try:
        forms = rules.get(menu_id).get("forms") or {} if rules is not None and menu_id and rules.has(menu_id) else {}
        return str((forms.get(severity or "S1") or {}).get("text") or "")
    except (KeyError, AttributeError, TypeError):
        return ""


def _view(src: Frame | OfferPreview, rules: Any) -> OfferPreview:
    return offer_preview(src, rules) if isinstance(src, Frame) else src


# ------------------------------------------------------------------------------------------- OFFER words (14.2.7)

# rule: 12.15.2 (the fixed word maps; the glossary 14.2.7 explains them behind `?`)
CHANCE_WORDS = ((95, "almost certain"), (75, "likely"), (55, "better than even"), (45, "even"), (25, "unlikely"),
                (10, "long shot"), (5, "only by luck"), (0, "impossible as framed"))
SEVERITY_WORDS = {"S1": "a nuisance", "S2": "a setback", "S3": "serious", "S4": "grave", "S5": "ruinous"}
REACH_WORDS = {"limited": "partly what you wanted", "standard": "what you wanted", "great": "more than you asked"}
COST_WORDS = {  # the price in plain words when the frame names no form of its own (never the menu's example list)
    "cost.harm": "you get hurt", "cost.footing": "you lose your footing", "cost.gear": "your gear suffers",
    "cost.time": "it costs you time", "cost.exposure": "you are noticed", "cost.closed_door": "a door closes to you",
    "cost.drain": "something is used up", "cost.shortfall": "you get less than you wanted",
    "cost.twist": "something complicates things"}
MODE_WORDS = {"fallback": "You're improvising without training: harder (+{n}), and at best a partial result.",
              "stretch": "You're stretching what you know: harder (+{n}).",
              "emulate": "You're copying what you've seen done: harder (+{n})."}
GLOSSARY: dict[str, str] = {  # rule: 14.2.7
    "almost certain": "95% to succeed", "likely": "75–90% to succeed", "better than even": "55–70% to succeed",
    "even": "45–50% to succeed", "unlikely": "25–40% to succeed", "long shot": "10–20% to succeed; as a label: "
    "failing badly is likelier than succeeding, and the offer shows a better way first",
    "only by luck": "5%: only a natural 20", "a nuisance": "the mildest price of a failure",
    "a setback": "a failure's price that sets you back", "serious": "a heavy price", "grave": "a very heavy price",
    "this can kill you": "this roll can leave you dying; you were warned before, and may back off",
    "danger": "a failure here costs something serious, even before a bad roll",
    "partly": "a success gets you part of what you wanted", "what you wanted": "a success gets you what you asked",
    "more than you asked": "a success goes further than you asked", "very well": "a critical success",
    "badly": "a critical failure", "close call": "you just missed: take what you wanted and pay the price shown, "
    "or fail", "go big": "if it works you get more; if it fails it costs more; same chance",
    "play it safe": "if it works you get less; if it fails it costs less; same chance",
    "another way": "other approaches the game worked out for you, each with its chance",
    "you can't judge how hard this is": "the roll is hidden; you see only what your character perceives",
    "improvising without training": "harder, and at best a partial result (you lack the training)",
    "auto": "a safe, likely roll made without asking you (you can turn this off)",
}


def chance_word(pct: int) -> str:  # rule: 12.15.2
    return next(w for floor, w in CHANCE_WORDS if pct >= floor)


def glossary(word: str = "") -> str:  # rule: 14.2.7
    """`?` alone: every word; `? <word>`: that word's meaning."""
    w = word.strip().lower().strip("[]?' ")
    if w:
        hit = next((k for k in GLOSSARY if k == w or k.startswith(w)), None)
        return f"{hit}: {GLOSSARY[hit]}" if hit else f"No glossary word {word.strip()!r}. Type ? for the list."
    return "\n".join(f"{k}: {v}" for k, v in GLOSSARY.items())


def _signed(n: int) -> str:
    return f"+{n}" if n >= 0 else f"−{-n}"


_DATA_ID = re.compile(r"^[a-z_]+(?:\.[a-z0-9_]+)+$")  # a data id (trait.sense.loud): its name is shown
_BOOKKEEPING = re.compile(r"\b(?:fact|npc|pc|obj|loc|clk|cost|verb|lic)\.[a-z0-9_]+|\bsource:|\bS[1-5]\b", re.I)


def _cost_clause(cost: Any) -> str:  # rule: 12.15.2
    """The price as one clause: the Framer's own form for this scene, unless it carries ids or bookkeeping (then
    the cost's plain words; the text is never rewritten, P-072)."""
    form = (getattr(cost, "form_intent", "") or "").strip().rstrip(".")
    if not form or _BOOKKEEPING.search(form):
        return COST_WORDS.get(cost.menu_id, "it costs you")
    return form


def _breakdown(f: Frame, rules: Any) -> str:
    m = f.modifier
    parts = [f"{name_of(rules, f.attribute)} {_signed(m.attribute)}"]
    if m.competence:
        tag = m.competence_tag
        word = "practised" if tag in (None, "deed") else f"trained ({name_of(rules, tag).lower()})"
        parts.append(f"{word} {_signed(m.competence)}")
    if m.edge:
        parts.append(f"edge {_signed(m.edge)}")
    lv = [x for x in f.levers if x.type == "precision"]
    sn = [x for x in f.snags if x.type == "precision"]
    parts += ["a help +2"] * len(lv) + [("tried before " if x.engine else "a hindrance ") + "−2" for x in sn]
    if m.status:
        parts.append(f"your condition {_signed(m.status)}")
    return ", ".join(parts)


def _chance_line(f: Frame, rules: Any) -> str:
    o = f.odds
    if f.secret:
        return "Chance: you can't judge how hard this is."
    if f.long_shot:  # 01.6.13: the label wins; a natural-20-only chance says so too
        n20 = ", only on a natural 20" if o.only_natural_20 else ""
        return (f"Chance: long shot — {o.success_or_better}%{n20} (failing badly is likelier: "
                f"{o.critical_failure}%)")
    if o.only_natural_20:
        return "Chance: only by luck — 5%, and at best what you wanted"
    return f"Chance: {chance_word(o.success_or_better)} — {o.success_or_better}%   ({_breakdown(f, rules)})"


def offer_view(src: Frame | OfferPreview, rules: Any = None) -> OfferView:  # rule: 01.7.1
    """The engine-api OfferView fields, from the computed frame (or its OfferPreview)."""
    v = _view(src, rules)
    tc = v.threatened_cost
    ac = v.alternate_cost
    return OfferView(
        restated_beat=v.restated_beat, approach=dict(v.approach), difficulty_words=v.difficulty_words,
        odds={k: int(v.odds.get(k, 0)) for k in ("success_or_better_pct", "critical_success_pct",
                                                 "critical_failure_pct", "near_miss_pct")},
        stakes=v.stakes, lethal=v.lethal,
        threatened_cost={"menu_id": tc.get("menu_id"), "form": tc.get("form"),
                         "severity_on_failure": tc.get("severity_on_failure")},
        alternate_cost=({"menu_id": ac.get("menu_id"), "form": ac.get("form")} if ac else None),
        only_natural_20=v.only_natural_20)


# 12.15.2's menu: the labels; play/render.py gives each its key ([Enter], d, b, s, c, w)
OFFER_LABELS = {"commit": "Do it", "go_big": "Go big", "play_safe": "Play it safe", "change": "Another way",
                "withdraw": "Back off"}


def offer_choices(src: Frame | OfferPreview, rules: Any = None) -> list[dict[str, str]]:  # rule: 01.7.3
    """Pause choices for an offer: do it, the trades legal now, another way (asks how), back off."""
    v = _view(src, rules)
    ids = ["commit", *[t for t in ("go_big", "play_safe") if t in v.trades or (t == "play_safe" and
                                                                              "play_it_safe" in v.trades)],
           "change", "withdraw"]
    return [{"id": i, "label": OFFER_LABELS[i]} for i in ids]


def offer_block(f: Frame, *, rules: Any = None, fate: int | None = None, lethal_line: str | None = None,
                auto: bool = False) -> OofBlock:  # rule: 12.15.2
    # rule: 01.7.1
    """The `[OFFER]` block: 12.15.2's template over the frame's typed fields (contracts/offer.md). No rule id, DC,
    severity code or mode name reaches the player; the menu follows from the pause's choices (play/render.py).
    `lethal_line`: engine/harm's `lethal_scan(...).offer_line`. `auto`: the auto-commit variant."""
    o = f.odds
    rest: list[str] = []
    mp = f.mode_price
    if mp is not None and mp.mode in MODE_WORDS:
        line = MODE_WORDS[mp.mode].format(n=mp.dc_shift)
        rest.append(line.replace("harder (+0), and ", "") if not mp.dc_shift else line)
    rest.append(_chance_line(f, rules))
    reach = REACH_WORDS.get(f.reach, "what you wanted")
    works = f"If it works: {reach}."
    if o.critical_success and not f.secret:  # a critical success delivers one reach rung more (01.6.10)
        better = "more than you asked" if f.reach != "great" else "more than you asked, and then some"
        works += f"   Very well ({o.critical_success}%): {better}."
    rest.append(works)
    tc = f.threatened_cost
    if tc.on_failure:
        fails = f"If it fails: {'Danger: ' if f.stakes == 'dire' else ''}{_cost_clause(tc)} — " \
                f"{SEVERITY_WORDS.get(tc.on_failure, tc.on_failure)}."
    else:
        fails = "If it fails: it just doesn't work."
    if tc.on_critical_failure and (o.critical_failure or f.secret):
        bad = f" ({o.critical_failure}%)" if not f.secret else ""
        fails += f"   Badly{bad}: {_cost_clause(tc)} — {SEVERITY_WORDS.get(tc.on_critical_failure, '')}."
    rest.append(fails)
    if f.lethal:
        rest.append(lethal_line or "THIS CAN KILL YOU.")
    if f.alternate_cost is not None and o.near_miss and not f.secret:
        rest.append(f"Close call ({o.near_miss}%): get it anyway and pay ({_cost_clause(f.alternate_cost)}), "
                    "or fail.")
    takes = [name_of(rules, c).lower() if _DATA_ID.match(c.strip()) else c.strip().rstrip(".")
             for c in f.method_consequences if c.strip()]
    if fate is not None:
        takes.append(f"fate {fate}")
    if takes:
        rest.append("Takes: " + " · ".join(takes))
    if f.alternatives and not auto and not f.secret:
        rest.append("Another way: " + " · ".join(f"{a.label} ({a.chance}%)" for a in f.alternatives))
    title = (f.beat.restatement or f.beat.intent).strip().rstrip(".") + "."
    return OofBlock(kind="OFFER", text=_block("OFFER — auto" if auto else "OFFER", title, rest))


# ------------------------------------------------------------------------------------------- harm blocks


def warning_block(rules: Any, trig: harm_lethal.LethalTrigger, *, source_name: str, fate: int,
                  yield_text: str | None = None, retreat_text: str | None = None) -> OofBlock:  # rule: 07.3.4
    # rule: PR-07-4
    """The `[WARNING]` block (T-07-7), never softened or omitted; exits default to "ask" (asking is free, 07.4)."""
    return OofBlock(kind="WARNING", text=harm_lethal.warning_block(
        rules, trig, source_name=source_name, fate=fate,
        yield_text=yield_text or "ask what it would mean", retreat_text=retreat_text or "ask what it would cost"))


def status_block(rules: Any, state: WorldState, eid: str, exits: str | None = None) -> OofBlock | None:
    # rule: 07.3.7
    """The `[STATUS]` card for a Staggered or Dying PC; None when neither."""
    from engine.harm.state import View

    text = harm_apply.status_block(rules, View(state), eid, exits)
    return OofBlock(kind="STATUS", text=text) if text else None


def last_chance_block(menu: Menu) -> OofBlock:  # rule: 07.5.2
    """The last-chance menu (`[CHOICE]` THE THRESHOLD …): a pause with no default."""
    return OofBlock(kind="LAST_CHANCE", text=menu_text(menu))


# ------------------------------------------------------------------------------------------- REDIRECT


def _fact_line(state: WorldState | None, fact_id: str | None, rules: Any = None) -> str:
    """An established fact in words (`the Guard's siblings: two brothers`), or a plain phrase when unseen."""
    f = state.facts.get(fact_id) if state is not None and fact_id else None
    if f is None or f.visibility not in PLAYER_FACING:
        return "something already settled stands against it"
    who = _ent_name(state, f.subject) if state is not None else ""
    pred = f.predicate.replace("_", " ").replace(".", " ")
    return f"{who + chr(39) + 's ' if who else ''}{pred} is {f.value}, as already settled"


def _why(dec: GateDecision, state: WorldState | None, rules: Any) -> str:
    """One plain line: what stands in the way."""
    red = dec.redirect
    if red is None:
        return "that is not possible as tried"
    if red.missing_kind == "license":
        return f"that needs {name_of(rules, red.missing)}, which you have not learned"
    if red.missing_kind == "deed_branch":
        if "." in red.missing:
            return f"that needs training in {name_of(rules, red.missing).lower()}, which you do not have"
        return "nothing you know how to do covers it as tried"
    if red.missing_kind == "condition":
        cdef = _condition_def(state, rules, red.missing)
        name = str((cdef or {}).get("name") or "a condition").lower()
        return f"you are {name} right now, and that stops it" + ("; clear it first" if clear_options(cdef) else "")
    if red.missing_kind == "canon":
        return "no one in this world can do that"
    if red.missing_kind == "zero_reach":
        return "too much stands against that way of doing it to get anywhere"
    return _fact_line(state, dec.fact_cited or red.missing, rules)


_GENERIC = ("another way to ", "look for what could serve")
_LEARN = {"mentor": "train with someone who knows it", "project": "study it from a book that teaches it",
          "recognition": "earn it through a calling", "item": "find or make a thing that grants it",
          "institution": "join an order or guild that grants it", "bargain": "ask someone with the authority to grant it",
          "origin": "it can only come from where you were born and raised"}


def _condition_def(state: WorldState | None, rules: Any, missing: str) -> Any:
    """The condition entry behind a G4 condition redirect (`missing` is the instance id, or a condition id)."""
    inst = state.conditions.get(missing) if state is not None else None
    cid = getattr(inst, "condition_id", None) or missing
    try:
        return rules.condition(cid) if rules is not None else None
    except Exception:  # noqa: BLE001 - an unknown id: the plain fallback words show
        return None


def clear_options(cdef: Any, rules: Any = None) -> list[str]:  # rule: 00.9.1
    """How a condition ends, from its `cleanse` entries: "Break free: one action (a Grapple roll)"."""
    out = []
    for c in (cdef or {}).get("cleanse") or ():
        means = re.sub(r"\s*\((?:verb|cond|trait)\.[a-z_.]+\)", "", str(c.get("means") or "")).strip()
        verb = (c.get("check") or {}).get("verb")
        head, _, tail = means.partition(": ")
        extra = "; ".join(x for x in (tail, f"a {name_of(rules, verb)} roll" if verb else "") if x)
        if head:
            out.append(head[:1].upper() + head[1:] + (f" ({extra})" if extra else ""))
    return out


def redirect_options(dec: GateDecision, rules: Any = None, *, limit: int = 3,
                     state: WorldState | None = None) -> list[str]:  # rule: 01.3.6
    """1-3 concrete things the player could do instead, in words they can type (a condition's way out first)."""
    red = dec.redirect
    out: list[str] = []
    if red is not None and red.missing_kind == "condition":
        out += clear_options(_condition_def(state, rules, red.missing), rules)
    for o in red.options if red else []:
        if o.method.startswith(_GENERIC):
            continue
        bits = []
        if o.kind == "fallback":
            if o.dc_shift:
                bits.append(f"harder: difficulty +{o.dc_shift}")
            if o.reach_cap:
                bits.append(f"at most {o.reach_cap} effect")
            if o.consequence:
                bits.append(str(o.consequence))
        out.append(o.method[:1].upper() + o.method[1:] + (f" ({'; '.join(bits)})" if bits else ""))
    if len(out) < 2:
        out += ["Look around for something here that would help", "Ask someone nearby who could do it"]
    return list(dict.fromkeys(out))[:limit]


def redirect_block(dec: GateDecision, *, state: WorldState | None = None,
                   rules: Any = None) -> OofBlock:  # rule: 12.15.5
    # rule: PR-01-5
    # rule: 01.3.6
    """`[REDIRECT]` for a G3 or G4 decision in plain words: what cannot be done and why in one line, then 1-3
    things to do instead, then how it could be learned (a missing licence)."""
    red = dec.redirect
    rest = ["You could instead:", *(f"- {o}" for o in redirect_options(dec, rules, state=state))]
    if red is not None and red.missing_kind == "license":
        paths = []
        for p in red.acquisition_paths:
            kind = str(p.get("type") or "")
            detail = _LEARN.get(kind) or str(p.get("detail") or p.get("text") or kind).strip()
            if detail and detail not in paths:
                paths.append(detail)
        if paths:
            rest.append(f"To learn it: {'; '.join(paths[:3])}.")
    return OofBlock(kind="REDIRECT", text=_block("REDIRECT", f"Not as tried: {_why(dec, state, rules)}.", rest))


# ------------------------------------------------------------------------------------------- CLARIFY, NEAR MISS


def clarify_block(question: str, *, assuming: bool = False) -> OofBlock:  # rule: 12.15.7
    # rule: 01.2.4
    """`[CLARIFY] One question: …` or, when the DM proceeds on a reading, `[ASSUMING] … (Say so if not …)`."""
    q = question.strip()
    if assuming:
        return OofBlock(kind="CLARIFY", text=f"[ASSUMING] {q} (Say so if not — you can change it at the offer.)")
    return OofBlock(kind="CLARIFY", text=f"[CLARIFY] One question: {q}")


def _price(rules: Any, cost: Any, severity: str | None) -> str:  # rule: 12.15.2
    """A price in words: the cost's clause and its severity word (never an S-code)."""
    sev = f" — {SEVERITY_WORDS.get(severity, severity)}" if severity else ""
    return f"{_cost_clause(cost)}{sev}"


def near_miss_choices(frame: Frame, rules: Any = None) -> list[dict[str, str]]:  # rule: 01.9.3
    """Pause choices: success at a cost (threatened, then alternate), or take the failure, in words."""
    sac = cost_severity(frame.stakes, "failure", success_at_cost=True, rules=rules)
    fail = cost_severity(frame.stakes, "failure", rules=rules)
    costs = [frame.threatened_cost] + ([frame.alternate_cost] if frame.alternate_cost else [])
    # each label says whether the attempt lands, so a success and a failure with the same price differ (P-076)
    out = [{"id": f"success_at_cost:{c.menu_id}",
            "label": f"Succeed: you get what you tried for, at this price: {_price(rules, c, sac)}"} for c in costs]
    lose = f"and still pay: {_price(rules, frame.threatened_cost, fail)}" if fail else "and nothing more is lost"
    out.append({"id": "failure", "label": f"Let it fail: you do not get it, {lose}"})
    return out


DEGREE_NAMES = {"critical_success": "critical success", "success": "success", "failure": "failure",
                "critical_failure": "critical failure"}


_SHOWN_QTY = {"vitality": "Vitality", "focus": "Focus", "fate": "fate", "dread": "Dread"}


def changed_line(state: WorldState, pc: str, events: Sequence[Any]) -> str:  # rule: 12.15.3
    """`Changed: Vitality 12 → 4 · bloodied`: the PC's shown quantities this beat moved, then the harm descriptor
    when Vitality moved (07.1.1); "" when nothing shown changed."""
    from engine.harm.state import descriptor
    from engine.resolve.conflict import state_words

    first: dict[str, int] = {}
    last: dict[str, int] = {}
    others: list[str] = []  # someone else hurt this beat: their state in words only, never their numbers (06.4.3)
    for e in events:
        p = e.payload
        if e.type == "quantity_changed" and getattr(p, "entity", None) == pc and p.quantity in _SHOWN_QTY:
            first.setdefault(p.quantity, p.new_value - p.delta)
            last[p.quantity] = p.new_value
        elif e.type == "quantity_changed" and p.quantity == "vitality" and p.entity not in others:
            others.append(p.entity)
    parts = [f"{_SHOWN_QTY[q]} {first[q]} → {v}" for q, v in last.items() if first[q] != v]
    if "vitality" in last:
        parts.append(descriptor(state, pc))
    from engine.store.views import name_known

    for eid in others:
        name = _ent_name(state, eid) or (state.entities[eid].name if eid in state.entities and name_known(state, eid)
                                         else "your opponent")
        parts.append(f"{name} {state_words(state, eid)}")
    return "Changed: " + " · ".join(parts) if parts else ""


def result_block(frame: Frame, roll: RollResult, *, sac: bool = False, costs: Sequence[Any] = (),
                 rules: Any = None, changed: str = "") -> OofBlock:  # rule: 12.15.3
    """`[RESULT] d20 9 → 13 vs 15 · failure (near miss)`, then what was paid; a secret frame: `hidden check made.`"""
    if frame.secret:
        return OofBlock(kind="RESULT", text="[RESULT] hidden check made.")
    words = "success at a cost (near miss)" if sac else (
        DEGREE_NAMES.get(roll.degree, roll.degree.replace("_", " ")) + (" (near miss)" if roll.near_miss else ""))
    rest = []
    for c in costs:
        form = (getattr(c, "form", "") or "").strip()
        tag = ", ".join(x for x in (name_of(rules, c.menu_id).lower(), SEVERITY_WORDS.get(c.severity or "", ""))
                        if x)
        rest.append(f"Paid: {form} ({tag})." if form else f"Paid: {tag}.")
    if changed:
        rest.append(changed)
    return OofBlock(kind="RESULT", text=_block("RESULT", f"d20 {roll.d20} → {roll.total} vs {frame.dc} · {words}",
                                               rest))


def near_miss_block(frame: Frame, roll: RollResult, *, rules: Any = None) -> OofBlock:  # rule: 12.15.4
    # rule: 01.9.3
    """`[NEAR MISS] <total> vs <DC>. So close: succeed and pay a price, or let it fail.` (the choices follow)."""
    vs = "hidden" if frame.secret else f"{roll.total} vs {frame.dc}"
    return OofBlock(kind="NEAR_MISS", text=f"[NEAR MISS] {vs}. So close: succeed and pay a price, or let it fail.")


# ------------------------------------------------------------------------------------------- RECAP, NOTE, passthroughs


def _ent_name(state: WorldState, eid: str | None) -> str:
    e = state.entities.get(eid or "")
    if e is None or eid in state.seals or e.visibility not in PLAYER_FACING:
        return ""
    return e.name


def when_words(ts: Any) -> str:
    """'the morning of day 3': game time in words (no internal counters)."""
    from engine.time.clock import day_index

    watches = ("morning", "afternoon", "evening", "night")
    watch = watches[ts.watch] if 0 <= ts.watch < len(watches) else ""
    return f"the {watch} of day {day_index(ts) + 1}" if watch else f"day {day_index(ts) + 1}"


def short_text(text: str, limit: int = 80) -> str:
    """The first sentence of `text`; longer than `limit`, it ends at its last whole clause ('; ', ', and ', ' — ')
    within the limit, else at a word boundary with an ellipsis (never 'one of…')."""
    t = re.split(r"(?<=[.!?])\s", str(text).strip(), maxsplit=1)[0].rstrip(".")
    if len(t) <= limit:
        return t
    cuts = [m.start() for m in re.finditer(r";\s|\s—\s|,\s(?:and|but|or|so|while|though)\s", t[:limit + 1])]
    if cuts and cuts[-1] >= limit // 3:
        return t[:cuts[-1]].rstrip(",;: ")
    return t[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def recap_block(state: WorldState, *, since_seq: int = 0, pc: str | None = None,
                max_lines: int = 6) -> OofBlock:  # rule: 12.5.3
    # rule: 12.15.11
    """A recap from state only (never from narration): where and when, pressing clocks as shown, active threads,
    the chronicle since `since_seq`, and the last scene's agenda."""
    from engine.world.chronicle import chronicle
    from engine.world.common import active_pc
    from engine.world.places import location
    from engine.world.social import thread_list

    pc = pc or active_pc(state)
    where = _ent_name(state, location(state, pc)) if pc else ""
    first = "Where: " + ", ".join(x for x in (where, when_words(state.time.now)) if x)
    clocks = []
    for c in state.clocks.values():
        if c.status != "active" or c.visibility == "hidden":
            continue
        clocks.append(c.name if c.visibility == "sensed" else f"{c.name} {c.filled}/{c.segments}")
    rest = []
    if clocks:
        rest.append("Pressing: " + " · ".join(clocks[:4]))
    from engine.dm.player_text import second_person

    threads = [short_text(second_person(t["text"] or t["name"])) for t in thread_list(state)
               if t["status"] == "active" and _ent_name(state, t["id"])]
    if threads:
        rest += ["Open threads:", *(f"- {t}" for t in threads[:4])]
    facts = state.facts
    lines = [e.text for e in chronicle(state, since_seq=since_seq)
             if (fid := state.current_fact_id("world", f"chronicle.{e.id}")) and facts[fid].visibility in PLAYER_FACING
             and e.scope in ("public", pc or "")]
    rest += [f"• {t}" for t in lines[-max_lines:]]
    last = state.scene or state.last_scene
    if last is not None and last.agenda:
        rest.append(f"Scene: {last.agenda}" + (" (answered)" if last.question_answered else ""))
    return OofBlock(kind="RECAP", text=_block("RECAP", first, rest))


NoteLabel = Literal["NOTE", "CORRECTION", "RULES", "UNKNOWN", "RULING", "LEADS", "SESSION", "OK", "FLAG", "CUT?",
                    "CHOICE", "SITUATION", "CHECK-IN"]


def note_block(text: str, label: NoteLabel = "NOTE", rest: Sequence[str] = ()) -> OofBlock:  # rule: 12.15.14
    """Any short OOF answer (`[NOTE]`, `[CORRECTION]`, `[RULES]`, `[UNKNOWN]`, `[RULING]` …); kind NOTE."""
    return OofBlock(kind="NOTE", text=_block(label, text.strip(), rest))


def seed_block(step: Any) -> OofBlock:  # rule: 12.16.3
    """`[SEED n/14]`: the world-seed step's summary (engine.gen.world_seed.SeedStep, or its text)."""
    return OofBlock(kind="SEED", text=str(getattr(step, "summary", step)))


def create_block(text: str, n: int | None = None, total: int | None = None) -> OofBlock:  # rule: PR-02-7
    """`[CREATE n/N]`: a creation step's pause block (passed through; labelled when n and total are given)."""
    t = text.strip()
    if n is not None and total is not None and not t.startswith("[CREATE"):
        t = f"[CREATE {n}/{total}] {t}"
    return OofBlock(kind="CREATE", text=t)


_ORDER = {"NOTE": 0, "RECAP": 1, "RESULT": 2, "SEED": 5, "CREATE": 5, "STATUS": 2, "REDIRECT": 3, "WARNING": 4, "OFFER": 5,
          "NEAR_MISS": 5, "CLARIFY": 5, "LAST_CHANCE": 5, "EPILOGUE": 6}


def ordered(blocks: Iterable[OofBlock]) -> list[OofBlock]:  # rule: 12.15
    """12.15's order: acknowledgements and corrections, the status and redirect blocks, the warning, then the one
    pause block last (stable otherwise)."""
    return sorted(blocks, key=lambda b: _ORDER.get(b.kind, 3))


__all__ = ["OfferView", "OofBlock", "OofKind", "clarify_block", "create_block", "last_chance_block", "name_of",
           "near_miss_block", "near_miss_choices", "note_block", "offer_block", "offer_choices", "offer_view",
           "ordered", "recap_block", "redirect_block", "result_block", "seed_block", "status_block", "warning_block"]
