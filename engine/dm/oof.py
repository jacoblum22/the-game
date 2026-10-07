"""Out-of-fiction blocks (12.15), rendered from state and computed records only, never from model text.

Every number, odds line, choice and rules matter goes in one of these blocks (12.14.4); the fiction carries none.
Each builder returns an `engine.dm.response.OofBlock(kind, text)` (the engine-api `Response.oof_blocks[]` item).

    blk = offer_block(offer_preview(frame), rules=rules, fate=1)     # the [OFFER] pause block
    blk.model_dump()                                                  # {"kind": "OFFER", "text": "..."}
"""

from __future__ import annotations

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
    if "go_big" in v.trades:
        out.append({"id": "go_big", "label": "Go big"})
    if "play_it_safe" in v.trades or "play_safe" in v.trades:
        out.append({"id": "play_safe", "label": "Play it safe"})
    return out


def _cost_words(rules: Any, cost: dict[str, Any] | None, *, with_severity: bool) -> str:
    if not cost or not cost.get("menu_id"):
        return ""
    menu = name_of(rules, cost.get("menu_id")).lower()
    form = (cost.get("form") or "").strip()
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
    first = f"{v.restated_beat} — {how}" + (f", {diff}" if diff else "") + "."
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
    text = _block(label, first, rest)
    if not auto:
        text += "\n  " + "   ".join(f"{i}) {c['label']}" for i, c in enumerate(offer_choices(v), 1))
    return OofBlock(kind="OFFER", text=text)


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


def _fact_line(state: WorldState | None, fact_id: str | None) -> str:
    if not fact_id:
        return "an established fact"
    f = state.facts.get(fact_id) if state is not None else None
    if f is None or f.visibility not in PLAYER_FACING:
        return f"an established fact ({fact_id})"
    return f"{f.subject}.{f.predicate} = {f.value} (established)"


def redirect_block(dec: GateDecision, *, state: WorldState | None = None,
                   rules: Any = None) -> OofBlock:  # rule: 12.15.5
    # rule: PR-01-5
    # rule: 01.3.6
    """`[REDIRECT]` for a G3 or G4 decision: what was checked, what is possible now, how to learn it."""
    red = dec.redirect
    if red is None:
        return OofBlock(kind="REDIRECT", text=_block("REDIRECT", f"{dec.gate} — {dec.reason or 'not possible as tried'}."))
    if red.missing_kind in ("license", "deed_branch"):
        first = f"{dec.gate} — checked {red.missing} (not held)."
    elif red.missing_kind == "condition":
        first = f"{dec.gate} — {red.missing} prevents it."
    else:
        first = f"{dec.gate} — " + _fact_line(state, dec.fact_cited or red.missing) + "."
    opts = []
    for o in red.options:
        bits = []
        if o.verb:
            bits.append(o.verb)
        if o.kind == "fallback":
            if o.dc_shift:
                bits.append(f"DC +{o.dc_shift}")
            if o.reach_cap:
                bits.append(f"reach capped at {o.reach_cap}")
            if o.consequence:
                bits.append(o.consequence)
        if o.verb:
            bits.append("ask for odds")
        opts.append(o.method + (f" ({'; '.join(bits)})" if bits else ""))
    rest = [f"Possible now: {' · '.join(opts)}" if opts else ""]
    paths = []
    for p in red.acquisition_paths:
        detail = str(p.get("detail") or p.get("text") or "").strip()
        kind = str(p.get("type") or "").strip()
        paths.append(f"{detail} ({kind})" if detail and kind else detail or kind)
    if paths:
        rest.append(f"Learn it: {' · '.join(x for x in paths if x)}")
    return OofBlock(kind="REDIRECT", text=_block("REDIRECT", first, rest))


# ------------------------------------------------------------------------------------------- CLARIFY, NEAR MISS


def clarify_block(question: str, *, assuming: bool = False) -> OofBlock:  # rule: 12.15.7
    # rule: 01.2.4
    """`[CLARIFY] One question: …` or, when the DM proceeds on a reading, `[ASSUMING] … (Say so if not …)`."""
    q = question.strip()
    if assuming:
        return OofBlock(kind="CLARIFY", text=f"[ASSUMING] {q} (Say so if not — you can change it at the offer.)")
    return OofBlock(kind="CLARIFY", text=f"[CLARIFY] One question: {q}")


def near_miss_choices(frame: Frame) -> list[dict[str, str]]:  # rule: 01.9.3
    """Pause choices: success at a cost (threatened, then alternate), or take the failure."""
    out = [{"id": f"success_at_cost:{frame.threatened_cost.menu_id}",
            "label": f"succeed and pay {frame.threatened_cost.menu_id}"}]
    if frame.alternate_cost is not None:
        out.append({"id": f"success_at_cost:{frame.alternate_cost.menu_id}",
                    "label": f"succeed and pay {frame.alternate_cost.menu_id}"})
    out.append({"id": "failure", "label": "let it fail"})
    return out


def near_miss_block(frame: Frame, roll: RollResult, *, rules: Any = None) -> OofBlock:  # rule: 12.15.4
    # rule: 01.9.3
    """`[NEAR MISS] <total> vs <DC>. Succeed and pay one — (a) … · (b) … — or (c) let it fail (…)`."""
    sac = cost_severity(frame.stakes, "failure", success_at_cost=True, rules=rules)
    fail = cost_severity(frame.stakes, "failure", rules=rules)
    costs = [frame.threatened_cost] + ([frame.alternate_cost] if frame.alternate_cost else [])
    letters = "abcdefg"
    paid = []
    for i, c in enumerate(costs):
        form = f": {c.form_intent}" if c.form_intent else ""
        paid.append(f"({letters[i]}) {name_of(rules, c.menu_id)} ({sac}){form}")
    fail_words = (f"{name_of(rules, frame.threatened_cost.menu_id)} {fail} applies" if fail else "nothing applies")
    vs = "hidden" if frame.secret else f"{roll.total} vs {frame.dc}"
    first = f"{vs}. Succeed and pay one — {' · '.join(paid)}"
    return OofBlock(kind="NEAR_MISS", text=_block("NEAR MISS", first, [f"— or ({letters[len(costs)]}) let it fail ({fail_words})."]))


# ------------------------------------------------------------------------------------------- RECAP, NOTE, passthroughs


def _ent_name(state: WorldState, eid: str | None) -> str:
    e = state.entities.get(eid or "")
    if e is None or eid in state.seals or e.visibility not in PLAYER_FACING:
        return ""
    return e.name


def recap_block(state: WorldState, *, since_seq: int = 0, pc: str | None = None,
                max_lines: int = 6) -> OofBlock:  # rule: 12.5.3
    # rule: 12.15.11
    """A recap from state only (never from narration): where and when, pressing clocks as shown, active threads,
    the chronicle since `since_seq`, and the last scene's agenda."""
    from engine.time.clock import fmt
    from engine.world.chronicle import chronicle
    from engine.world.common import active_pc
    from engine.world.places import location
    from engine.world.social import thread_list

    pc = pc or active_pc(state)
    where = _ent_name(state, location(state, pc)) if pc else ""
    first = "Where: " + ", ".join(x for x in (where, fmt(state.time.now)) if x)
    clocks = []
    for c in state.clocks.values():
        if c.status != "active" or c.visibility == "hidden":
            continue
        clocks.append(c.name if c.visibility == "sensed" else f"{c.name} {c.filled}/{c.segments}")
    rest = []
    if clocks:
        rest.append("Pressing: " + " · ".join(clocks[:4]))
    threads = [t["name"] for t in thread_list(state)
               if t["status"] == "active" and _ent_name(state, t["id"])]
    if threads:
        rest.append("Threads: " + " · ".join(threads[:5]))
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


_ORDER = {"NOTE": 0, "RECAP": 1, "SEED": 5, "CREATE": 5, "STATUS": 2, "REDIRECT": 3, "WARNING": 4, "OFFER": 5,
          "NEAR_MISS": 5, "CLARIFY": 5, "LAST_CHANCE": 5, "EPILOGUE": 6}


def ordered(blocks: Iterable[OofBlock]) -> list[OofBlock]:  # rule: 12.15
    """12.15's order: acknowledgements and corrections, the status and redirect blocks, the warning, then the one
    pause block last (stable otherwise)."""
    return sorted(blocks, key=lambda b: _ORDER.get(b.kind, 3))


__all__ = ["OfferView", "OofBlock", "OofKind", "clarify_block", "create_block", "last_chance_block", "name_of",
           "near_miss_block", "near_miss_choices", "note_block", "offer_block", "offer_choices", "offer_view",
           "ordered", "recap_block", "redirect_block", "seed_block", "status_block", "warning_block"]
