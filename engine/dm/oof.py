"""Out-of-fiction blocks (12.15), rendered from state and computed records only, never from model text.

Every number, odds line, choice and rules matter goes in one of these blocks (12.14.4); the fiction carries none.
Each builder returns an `engine.dm.response.OofBlock(kind, text)` (the engine-api `Response.oof_blocks[]` item).

    blk = offer_block(offer_preview(frame), rules=rules, fate=1)     # the [OFFER] pause block
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
    """The cost menu's own example words for a severity (resolution.yaml cost_menu `forms.<S>.text`)."""
    try:
        forms = rules.get(menu_id).get("forms") or {} if rules is not None and menu_id and rules.has(menu_id) else {}
        return str((forms.get(severity or "S1") or {}).get("text") or "")
    except (KeyError, AttributeError, TypeError):
        return ""


def _difficulty_phrase(words: str) -> str:
    w = (words or "").strip()
    phrases = {"stored": "a difficulty already set", "their defense": "against their defense",
               "the effect's strength": "against the effect's strength", "hidden": "difficulty hidden", "": ""}
    if w in phrases:
        return phrases[w]
    return f"{'an' if w[:1].lower() in 'aeiou' else 'a'} {w.lower()} obstacle"


def _view(src: Frame | OfferPreview, rules: Any) -> OfferPreview:
    return offer_preview(src, rules) if isinstance(src, Frame) else src


# ------------------------------------------------------------------------------------------- OFFER


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


def offer_choices(src: Frame | OfferPreview, rules: Any = None) -> list[dict[str, str]]:  # rule: 01.7.3
    """Pause choices for an offer: commit, change, withdraw, and the trades legal now (go big / play it safe)."""
    v = _view(src, rules)
    out = [{"id": "commit", "label": "Commit"}, {"id": "change", "label": "Change approach"},
           {"id": "withdraw", "label": "Withdraw"}]
    from engine.resolve.pipeline import TRADE_LABELS

    if "go_big" in v.trades:
        out.append({"id": "go_big", "label": TRADE_LABELS["go_big"]})
    if "play_it_safe" in v.trades or "play_safe" in v.trades:
        out.append({"id": "play_safe", "label": TRADE_LABELS["play_it_safe"]})
    return out


def _cost_words(rules: Any, cost: dict[str, Any] | None, *, with_severity: bool) -> str:
    if not cost or not cost.get("menu_id"):
        return ""
    menu = name_of(rules, cost.get("menu_id")).lower()
    form = (cost.get("form") or "").strip() or _menu_form(rules, cost.get("menu_id"), cost.get("severity_on_failure"))
    sev = ""
    if with_severity and cost.get("severity_on_failure"):
        sev = f", {cost['severity_on_failure']}"
        if cost.get("severity_on_critical_failure"):
            sev += f"; {cost['severity_on_critical_failure']} on a critical failure"
    return f"{form} ({menu}{sev})" if form else menu + (f" ({sev[2:]})" if sev else "")


def offer_block(src: Frame | OfferPreview, *, rules: Any = None, fate: int | None = None,
                lethal_line: str | None = None, auto: bool = False,
                costs_line: str | None = None) -> OofBlock:  # rule: 12.15.2
    # rule: 01.7.1
    """The `[OFFER]` block in contracts/cli.md's layout: approach and difficulty in words, the odds line, stakes
    with the threatened and alternate cost in words, the lethal line, reach, fate, and the numbered choices.
    `lethal_line`: engine/harm's `lethal_scan(...).offer_line` (THIS CAN KILL YOU — <source> (warned <when>)).
    `costs_line`: the action, time and Focus prices when the caller has them (12.15.2 Costs). `auto`: the
    auto-commit variant (labelled `OFFER — auto`, no choices)."""
    v = _view(src, rules)
    ap = v.approach
    verb = name_of(rules, ap.get("verb")) if ap.get("verb") else name_of(rules, ap.get("license"))
    attr = name_of(rules, ap.get("attribute"))
    how = verb + (f" ({attr})" if attr and attr != verb else "")
    lic = ap.get("license")
    if lic and ap.get("verb"):
        how += f", {name_of(rules, lic)}"
    diff = _difficulty_phrase(v.difficulty_words)
    first = f"{v.restated_beat.rstrip(' .')} — {how}" + (f", {diff}" if diff else "") + "."
    rest: list[str] = []
    mp = v.mode_price
    if mp and mp.get("mode") and mp.get("mode") != "normal":
        price = []
        if mp.get("dc_shift"):
            price.append(f"DC +{mp['dc_shift']}")
        if mp.get("focus_add"):
            price.append(f"Focus +{mp['focus_add']}")
        if mp.get("reach_cap"):
            price.append(f"reach capped at {mp['reach_cap']}")
        if mp.get("consequence"):
            price.append(str(mp["consequence"]))
        rest.append(f"Mode: {mp['mode']}" + (f" — {', '.join(price)}" if price else "") + ".")
    if v.alternative_attribute:
        rest.append(f"(A method using {name_of(rules, v.alternative_attribute)} would use a higher attribute.)")
    o = v.odds
    if v.dc_source == "hidden":
        rest.append("The roll is hidden; you'll see only what you perceive.")
    elif v.only_natural_20:
        rest.append("Only a natural 20, and at best a plain success.")
    else:
        need = f" (need {v.need}+ on the die)" if v.need is not None else ""
        rest.append(f"Success or better {o.get('success_or_better_pct', 0)}% · critical failure "
                    f"{o.get('critical_failure_pct', 0)}% · near miss {o.get('near_miss_pct', 0)}%{need}.")
    stakes = f"Stakes: {v.stakes}."
    threat = _cost_words(rules, v.threatened_cost, with_severity=True)
    if threat and v.threatened_cost.get("severity_on_failure"):
        stakes += f" If it goes wrong: {threat}."
    elif threat and v.threatened_cost.get("severity_on_critical_failure"):
        crit = dict(v.threatened_cost, severity_on_failure=v.threatened_cost["severity_on_critical_failure"],
                    severity_on_critical_failure=None)
        stakes += (" If it goes wrong: it just doesn't work, at no other cost; on a critical failure, "
                   f"{_cost_words(rules, crit, with_severity=True)}.")
    elif v.threatened_cost.get("menu_id"):
        stakes += " If it goes wrong: it just doesn't work, at no other cost."
    alt = _cost_words(rules, v.alternate_cost, with_severity=False)
    if alt:
        stakes += f" Or instead: {alt}."
    rest.append(stakes)
    if v.lethal:
        rest.append(lethal_line or "THIS CAN KILL YOU.")
    rest.append(f"Reach: {v.reach}.")
    if costs_line:
        rest.append(costs_line)
    if fate is not None:
        rest.append(f"Fate: {fate}.")
    label = "OFFER — auto" if auto else "OFFER"
    return OofBlock(kind="OFFER", text=_block(label, first, rest))  # the pause's choices follow it, numbered


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


def _price(rules: Any, cost: Any, severity: str | None) -> str:
    form = (getattr(cost, "form_intent", None) or "").strip() or _menu_form(rules, cost.menu_id, severity)
    menu = name_of(rules, cost.menu_id).lower()
    sev = f", {severity}" if severity else ""
    return f"{form} ({menu}{sev})" if form else f"{menu}{sev}"


def near_miss_choices(frame: Frame, rules: Any = None) -> list[dict[str, str]]:  # rule: 01.9.3
    """Pause choices: success at a cost (threatened, then alternate), or take the failure, in words."""
    sac = cost_severity(frame.stakes, "failure", success_at_cost=True, rules=rules)
    fail = cost_severity(frame.stakes, "failure", rules=rules)
    costs = [frame.threatened_cost] + ([frame.alternate_cost] if frame.alternate_cost else [])
    out = [{"id": f"success_at_cost:{c.menu_id}", "label": f"Succeed, and pay: {_price(rules, c, sac)}"}
           for c in costs]
    lose = f": {_price(rules, frame.threatened_cost, fail)}" if fail else " (nothing more is lost)"
    out.append({"id": "failure", "label": f"Let it fail{lose}"})
    return out


DEGREE_NAMES = {"critical_success": "critical success", "success": "success", "failure": "failure",
                "critical_failure": "critical failure"}


def result_block(frame: Frame, roll: RollResult, *, sac: bool = False, costs: Sequence[Any] = (),
                 rules: Any = None) -> OofBlock:  # rule: 12.15.3
    """`[RESULT] d20 9 → 13 vs 15 · failure (near miss)`, then what was paid; a secret frame: `hidden check made.`"""
    if frame.secret:
        return OofBlock(kind="RESULT", text="[RESULT] hidden check made.")
    words = "success at a cost (near miss)" if sac else (
        DEGREE_NAMES.get(roll.degree, roll.degree.replace("_", " ")) + (" (near miss)" if roll.near_miss else ""))
    rest = []
    for c in costs:
        form = (getattr(c, "form", "") or "").strip() or _menu_form(rules, c.menu_id, c.severity)
        tag = ", ".join(x for x in (name_of(rules, c.menu_id).lower(), c.severity or "") if x)
        rest.append(f"Paid: {form} ({tag})." if form else f"Paid: {tag}.")
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
