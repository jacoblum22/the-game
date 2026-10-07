"""GATE (01.3; PR-01-5): verify the Reader's proposed gate class against the actor's holdings and the data.

    dec = check_gate(beat, state=tx.state, rules=rules, store=store, staged=tx.events, mint=tx.mint)
    tx.add_all(dec.events)        # the g3_redirect / g4 ruling (none for G0-G2)

The engine checks what state and data can settle: a cited verb exists and its `excludes` do not name the method;
a cited license is held (not retired or expired, not forbidden by an active condition); a G4 fact exists; an
active condition forbids the verb or a trait (G4 test 4, answered from state). Anything that fails falls to G3
(SG-05). G3 builds the four-part redirect from the license entry (crude fallback, acquisition paths); at least
one concrete option is always present (P16). `find_rulings` runs before every G3/G4 decision (FR-022).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from engine.resolve.rulings import (
    Precedent,
    RulingRecord,
    find_rulings,
    gate_signature,
    log_ruling,
    precedent_for,
)
from engine.resolve.types import Beat, GateClass, GateMode
from engine.store.events import Event, LicenseInstance

_STOP = {"the", "and", "with", "from", "into", "onto", "your", "you", "that", "this", "for", "not", "any", "a", "an",
         "its", "their", "own", "other", "than", "which"}


class RedirectOption(BaseModel):
    kind: Literal["fallback", "basic_verb", "intent"]
    verb: str | None = None
    method: str
    license: str | None = None  # whose crude_fallback this is
    dc_shift: int = 0
    reach_cap: str | None = None
    consequence: str | None = None


class Redirect(BaseModel):
    """01.3.6: acknowledge the intent; why (the id checked); what is possible now (>= 1 option); how to gain it."""

    intent: str
    missing: str  # the license id (G3) or fact / condition id (G4) checked
    missing_kind: Literal["license", "deed_branch", "fact", "canon", "zero_reach", "condition"]
    options: list[RedirectOption]
    acquisition_paths: list[dict[str, Any]] = Field(default_factory=list)


class GateDecision(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    gate: GateClass
    proposed: GateClass
    verb: str | None = None
    license: str | None = None
    mode: GateMode = "normal"
    reason: str = ""
    fact_cited: str | None = None
    redirect: Redirect | None = None
    precedent: list[RulingRecord] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)

    @property
    def rolls_possible(self) -> bool:
        return self.gate in ("G1", "G2") or (self.gate == "G3" and self.mode == "fallback")


# ------------------------------------------------------------------------------------------- holdings


def _stem(w: str) -> str:
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def words(text: str) -> set[str]:
    return {_stem(w) for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= 3 and w not in _STOP}


def excluded_by(verb: Any, method: str) -> Any | None:  # rule: 01.3.1
    """The verb's `excludes` entry whose every content word appears in the method (a literal mention)."""
    m = words(method)
    for e in verb.get("excludes") or ():
        w = words(str(e.get("what", "")))
        if w and w <= m:
            return e
    return None


def held_license(state: Any, actor: str, license_id: str) -> LicenseInstance | None:  # rule: 01.3.2
    """The actor's instance of `license_id`, unless retired or expired (00.6.1 license state)."""
    for lic in state.licenses.get(actor, []):
        if lic.license_id == license_id and lic.lifecycle != "retired" and not lic.expires:
            return lic
    return None


def _restricts(rules: Any, state: Any, actor: str) -> Iterable[tuple[str, Any]]:
    for inst in state.conditions_on(actor):
        try:
            cond = rules.condition(inst.condition_id)
        except Exception:  # noqa: BLE001 - an unknown condition id restricts nothing here
            continue
        for m in cond.get("modifies") or ():
            if m.get("effect_id") == "eff.restrict":
                yield inst.instance_id, (m.get("params") or {}).get("forbid") or {}


def forbidden_by_condition(beat: Beat, *, state: Any, rules: Any) -> tuple[str, str] | None:  # rule: 01.3.7
    """G4 test 4 from state: an active condition's restrict forbids the verb, a trait of the beat or the license.
    Returns (condition instance id, what is forbidden)."""
    for inst_id, forbid in _restricts(rules, state, beat.actor):
        if beat.verb and beat.verb in (forbid.get("verbs") or ()):
            return inst_id, beat.verb
        if beat.license and beat.license in (forbid.get("licenses") or ()):
            return inst_id, beat.license
        for m in forbid.get("methods") or ():
            t = re.match(r"any beat with (trait\.[a-z_.]+)", str(m))
            if t and t.group(1) in beat.traits:
                return inst_id, t.group(1)
    return None


# ------------------------------------------------------------------------------------------- redirect


def would_be_license(beat: Beat, rules: Any) -> str | None:  # rule: PR-01-5
    """PR-01-5 step 1: the license that would cover the method (named by the Reader, else the best word match
    over license names, scopes and fallbacks; at least two shared words)."""
    for cand in (beat.would_be_license, beat.license):
        if cand and cand in rules.licenses:
            return cand
    m = words(f"{beat.method} {beat.intent}")
    best, score = None, 1
    for lid, lic in rules.licenses.items():
        text = f"{lic.get('name', '')} {lic.get('scope', '')}"
        s = len(m & words(text))
        if beat.deed_tag and beat.deed_tag in (lic.get("tags") or ()):
            s += 2
        if s > score:
            best, score = lid, s
    return best


def _paths(lic: Any) -> list[dict[str, Any]]:
    return [dict(p) for p in lic.get("acquisition_paths") or () if p.get("type") != "origin"]


def _fallback_option(lid: str, lic: Any) -> RedirectOption | None:
    fb = lic.get("crude_fallback")
    if not fb or fb == "none" or not isinstance(fb, dict):
        return None
    return RedirectOption(kind="fallback", verb=fb.get("verb"), method=str(fb.get("method", "")), license=lid,
                          dc_shift=int(fb.get("dc_shift") or 0), reach_cap=fb.get("reach_cap"),
                          consequence=fb.get("consequence"))


def _valid_alternatives(alts: Iterable[RedirectOption], rules: Any) -> list[RedirectOption]:
    return [a for a in alts if a.verb is None or a.verb in rules.basic_verbs]


def _nearest(beat: Beat, rules: Any) -> RedirectOption:
    if beat.verb and beat.verb in rules.basic_verbs:
        return RedirectOption(kind="basic_verb", verb=beat.verb, method=f"another way to {beat.intent}")
    return RedirectOption(kind="intent", verb="verb.observe", method=f"look for what could serve: {beat.intent}")


def build_redirect(beat: Beat, rules: Any, alternatives: Iterable[RedirectOption] = ()) -> Redirect:
    # rule: PR-01-5
    """PR-01-5 steps 1-3 (the four-part redirect of 01.3.6): nothing is spent."""
    lid = would_be_license(beat, rules)
    options: list[RedirectOption] = []
    if lid is not None:
        lic = rules.license(lid)
        fb = _fallback_option(lid, lic)
        if fb is not None:
            options.append(fb)
        options += _valid_alternatives(alternatives, rules)
        if not options:
            options.append(_nearest(beat, rules))
        return Redirect(intent=beat.intent, missing=lid, missing_kind="license", options=options,
                        acquisition_paths=_paths(lic))
    branch = beat.deed_tag or "deed"
    options = _valid_alternatives(alternatives, rules) or [_nearest(beat, rules)]
    return Redirect(intent=beat.intent, missing=branch, missing_kind="deed_branch", options=options,
                    acquisition_paths=[{"type": "mentor", "detail": f"someone who holds a {branch} license"},
                                       {"type": "recognition", "detail": f"a calling keyed at or above {branch}"}])


# ------------------------------------------------------------------------------------------- the check


def _ruling(kind: Literal["g3_redirect", "g4"], key: str, beat: Beat, reason: str, facts: list[str],
            precedent: Precedent, mint: Callable[[str], str] | None, store: Any,
            staged: Sequence[Event]) -> list[Event]:
    if mint is None:
        return []
    rec = RulingRecord(signature=gate_signature(kind, key), situation=beat.restatement or beat.intent,
                       facts_cited=facts, kind=kind, precedent=precedent,
                       result={"degree": None, "outcome": reason}, tags=list(beat.traits))
    return [log_ruling(rec, mint, store=store, staged=staged, rule_id="01.3.6")]


def check_gate(beat: Beat, *, state: Any, rules: Any, store: Any = None, staged: Sequence[Event] = (),
               mint: Callable[[str], str] | None = None, canon_impossible: Iterable[str] = (),
               alternatives: Iterable[RedirectOption] = ()) -> GateDecision:  # rule: 01.3.1
    """The engine's GATE: G0 passes; G4 from state (condition) or a cited fact/canon; G1 verb covers and not
    excludes; G2 a held license; otherwise G3 with a redirect (or an accepted crude fallback, rollable)."""
    d = GateDecision(gate=beat.gate, proposed=beat.gate, verb=beat.verb, license=beat.license, mode=beat.mode)
    if beat.gate == "G0":
        d.reason = "a question about the world: state, knowledge, or the Oracle (01.3.8)"
        return d
    alts = list(alternatives)
    # G4 (01.3.7): test 4 answered from state, whatever was proposed
    g4: tuple[str, str, Literal["fact", "canon", "zero_reach", "condition"]] | None = None
    forbid = forbidden_by_condition(beat, state=state, rules=rules)
    if forbid is not None:
        g4 = (forbid[0], f"an active condition forbids {forbid[1]}", "condition")
    elif beat.gate == "G4":
        test = beat.g4_test or ("fact" if beat.g4_fact else "zero_reach")
        if test == "fact":
            if beat.g4_fact and beat.g4_fact in state.facts:
                g4 = (beat.g4_fact, "success requires an established fact to be false", "fact")
            else:
                d.reason = f"G4 cites no established fact ({beat.g4_fact!r}); default false (01.3.7)"
        elif test == "canon":
            if beat.g4_fact and (beat.g4_fact in set(canon_impossible) or beat.g4_fact in state.facts):
                g4 = (beat.g4_fact, "impossible for anyone in the setting (canon)", "canon")
            else:
                d.reason = f"G4 canon test cites nothing on record ({beat.g4_fact!r}); default false"
        else:
            g4 = (beat.g4_fact or "reach", "two effect factors stand against the method (zero reach)", "zero_reach")
    if g4 is not None:
        key, why, kind = g4
        found = find_rulings(store, gate_signature("g4", key), staged=staged)
        options = _valid_alternatives(alts, rules) or [_nearest(beat, rules)]
        if kind == "condition" and options[0].verb == beat.verb:
            options = [RedirectOption(kind="intent", verb="verb.observe", method=f"another way to {beat.intent}")]
        d.gate, d.reason, d.fact_cited, d.precedent = "G4", why, key, found
        d.redirect = Redirect(intent=beat.intent, missing=key, missing_kind=kind, options=options)
        d.events = _ruling("g4", key, beat, why, [key] if kind in ("fact", "canon") else [], precedent_for(found),
                           mint, store, staged)
        return d
    # a G4 that did not hold falls through to G1/G2 (01.3.7: default false)
    proposed = beat.gate if beat.gate != "G4" else ("G2" if beat.license else "G1")
    # G2: a held license (01.3.2)
    if beat.license and proposed in ("G1", "G2"):
        if held_license(state, beat.actor, beat.license) is not None and beat.license in rules.licenses:
            lic = rules.license(beat.license)
            if beat.mode in ("stretch", "emulate") and not lic.get(beat.mode):
                d.reason = f"{beat.license} declares no {beat.mode} (01.3.5)"
            else:
                d.gate, d.mode = "G2", beat.mode if beat.mode in ("stretch", "emulate") else "normal"
                d.reason = f"held license {beat.license}"
                return d
        else:
            d.reason = f"license {beat.license} is not held by {beat.actor}"
    # G1: the verb covers it and does not exclude it (01.3.1)
    elif proposed == "G1":
        verb = rules.basic_verbs.get(beat.verb or "")
        if verb is None:
            d.reason = f"unknown basic verb {beat.verb!r}"
        elif beat.method_class and beat.method_class.lower() not in {c.lower() for c in verb["covers"]}:
            d.reason = f"{beat.method_class!r} is not in {beat.verb}'s covers"
        elif (ex := excluded_by(verb, beat.method)) is not None:
            d.reason = f"{beat.verb} excludes {ex['what']!r} (needs {ex.get('needs')})"
        else:
            d.gate, d.mode, d.license = "G1", "normal", None
            d.reason = "; ".join(x for x in (d.reason, f"{beat.verb} covers it") if x)
            return d
    # G3: an accepted crude fallback rolls; otherwise the redirect
    if beat.mode == "fallback" and beat.fallback_license and beat.fallback_license in rules.licenses:
        fb = _fallback_option(beat.fallback_license, rules.license(beat.fallback_license))
        if fb is not None and fb.verb == beat.verb:
            d.gate, d.mode, d.license = "G3", "fallback", beat.fallback_license
            d.reason = f"crude fallback of {beat.fallback_license} accepted"
            return d
    red = build_redirect(beat, rules, alts)
    found = find_rulings(store, gate_signature("g3_redirect", red.missing), staged=staged)
    d.gate, d.mode, d.redirect, d.precedent = "G3", "normal", red, found
    d.reason = d.reason or "beyond the basic verbs and no held license covers it"
    d.events = _ruling("g3_redirect", red.missing, beat, d.reason, [], precedent_for(found), mint, store, staged)
    if red.missing_kind == "deed_branch" and mint is not None:  # no license in data covers it (01.3.5)
        rec = RulingRecord(signature=f"rule_conflict:{red.missing}", situation=beat.restatement or beat.intent,
                           kind="rule_conflict", review_flag=True,
                           result={"degree": None, "outcome": f"no license entry covers this method under "
                                                              f"{red.missing}; ch.05/13 to author one"})
        d.events.append(log_ruling(rec, mint, store=store, staged=[*staged, *d.events], rule_id="01.3.5"))
    return d
