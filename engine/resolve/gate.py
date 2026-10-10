"""GATE (01.3; 00.12.3 `[D]`; PR-01-5): the gate class, computed from the beat's verb, facets and the actor's holdings.

    dec = check_gate(beat, state=tx.state, rules=rules, store=store, staged=tx.events, mint=tx.mint)
    tx.add_all(dec.events)        # the g3_redirect / g4 ruling (none for G1, G2)

No role proposes the class (00.12.3, DL-01-30). `compute_gate` is a pure function of the verb, the three method
facets (12.2.2: `against_will`, `uses_power`, `speech`), the method's words matched against the verbs' `excludes`,
the held licences and whether literacy is on record; `check_gate` adds what only state holds (an active condition
forbidding the method, a cited G4 fact, an accepted crude fallback) and the redirect. A sheet knack is an edge,
never a gate: it is not an input. G3 builds the four-part redirect from the license entry (crude fallback,
acquisition paths); at least one concrete option is always present (P16). `find_rulings` runs before every G3/G4
decision (FR-022).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Sequence
from typing import Any, Literal, NamedTuple

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
LETTERS = "lic.lang.letters"  # 02.4.6: reading needs it once literacy is on record
WRITING = re.compile(r"\b(notice|sign|letter|inscription|script|rune|book|ledger|writing|written|words|page|scroll"
                     r"|bill|placard|poster|note|label|list|map|tablet|plaque|carved name)s?\b", re.I)
_LIC = re.compile(r"\blic\.[a-z_]+\.[a-z_]+")


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
    proposed: GateClass | None = None  # no role proposes the class any more (00.12.3); kept for old records
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
    """The verb's `excludes` entry one of whose alternatives ("flying or teleporting") has every content word in
    the method (a literal mention)."""
    m = words(method)
    for e in verb.get("excludes") or ():
        for alt in str(e.get("what", "")).split(" or "):
            w = words(alt)
            if w and w <= m:
                return e
    return None


def excluded_anywhere(rules: Any, verb_id: str | None, method: str) -> Any | None:  # rule: 01.3.1
    """The beat's own verb's `excludes` first, then every other verb's: "pick the lock" read as Handle is still
    the method Force names as needing Thievery."""
    order = [verb_id, *[v for v in rules.basic_verbs if v != verb_id]] if verb_id else list(rules.basic_verbs)
    for v in order:
        entry = rules.basic_verbs.get(v or "")
        if entry is not None and (ex := excluded_by(entry, method)) is not None:
            return ex
    return None


def held_license(state: Any, actor: str, license_id: str) -> LicenseInstance | None:  # rule: 01.3.2
    """The actor's instance of `license_id`, unless retired or expired (00.6.1 license state)."""
    for lic in state.licenses.get(actor, []):
        if lic.license_id == license_id and lic.lifecycle != "retired" and not lic.expires:
            return lic
    return None


def _lic(rules: Any, lid: str | None) -> Any | None:
    """A license entry from `licenses.yaml` or another data file (the language licenses), else None."""
    if not lid:
        return None
    if lid in rules.licenses:
        return rules.license(lid)
    try:
        return rules.get(lid) if rules.has(lid) else None
    except (KeyError, AttributeError):
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


def forbidden_by_condition(beat: Beat, *, state: Any, rules: Any, verb: str | None = None,
                           license: str | None = None) -> tuple[str, str] | None:  # rule: 01.3.7
    """G4 test 4 from state: an active condition's restrict forbids the verb, a trait of the beat or the license.
    Returns (condition instance id, what is forbidden)."""
    verb = verb or beat.verb
    license = license or beat.license
    for inst_id, forbid in _restricts(rules, state, beat.actor):
        if verb and verb in (forbid.get("verbs") or ()):
            return inst_id, verb
        if license and license in (forbid.get("licenses") or ()):
            return inst_id, license
        for m in forbid.get("methods") or ():
            t = re.match(r"any beat with (trait\.[a-z_.]+)", str(m))
            if t and t.group(1) in beat.traits:
                return inst_id, t.group(1)
    return None


# ------------------------------------------------------------------------------------------- the computation


def covering_verb(verb: str | None, *, against_will: bool, speech: bool) -> str | None:  # rule: 00.12.3
    """The verb card the facets put the beat under: a hold or a blow that is not against anyone's will is not a
    Grapple or a Strike ("gently turn the child's face" is Handle; words said with a raised fist are Talk)."""
    if against_will:  # words are never against anyone's will: a Talk read so carries a hold (a hand over a mouth)
        return "verb.grapple" if verb == "verb.talk" else verb
    if verb == "verb.grapple":
        return "verb.talk" if speech else "verb.handle"
    if verb == "verb.strike" and speech:
        return "verb.talk"
    return verb


class Computed(NamedTuple):
    gate: GateClass
    verb: str | None
    license: str | None  # G2: the covering license; G3: the would-be license (None: a deed branch)
    reason: str


def _fallback_shift(rules: Any, lid: str) -> int:
    fb = (_lic(rules, lid) or {}).get("crude_fallback")
    return int(fb.get("dc_shift") or 0) if isinstance(fb, dict) else 99


def _plain_cover(rules: Any, verb: str | None, held: Sequence[str]) -> str | None:
    """A held training license whose untrained form (crude fallback) is this verb: the licensed way of the same
    act (persuasion for Talk, tracking for Observe). The lowest fallback price first.
    ponytail: the method's deed tag would pick between two such licenses better than the price does."""
    fits = [lid for lid in held if (e := _lic(rules, lid)) is not None and e.get("kind") == "training"
            and isinstance(e.get("crude_fallback"), dict) and e["crude_fallback"].get("verb") == verb]
    return min(fits, key=lambda x: (_fallback_shift(rules, x), fits.index(x))) if fits else None


def _power_cover(rules: Any, held: Sequence[str]) -> str | None:
    """A held technique license (no crude fallback: its methods have no untrained form)."""
    return next((lid for lid in held if (e := _lic(rules, lid)) is not None and e.get("kind") == "training"
                 and not isinstance(e.get("crude_fallback"), dict)), None)


def _tongue(rules: Any, method: str, needs: str) -> list[str]:  # rule: PR-01-5
    """A language exclude ("reading an unknown script" needs a language license): the tongue the method names.
    ponytail: matched on a name's first three letters ("elven" → Elvish); a script fact on the target is better."""
    if "language" not in needs:
        return []
    heads = {w[:3] for w in re.findall(r"[a-z]+", method.lower()) if len(w) >= 3}
    return [lid for lid in rules.ids("lic.lang.") if lid not in ("lic.lang.common", LETTERS)
            and any(w[:3] in heads for w in re.findall(r"[a-z]+", str(rules.get(lid).get("name", "")).lower())
                    if len(w) >= 4)]


def compute_gate(verb: str | None, *, against_will: bool = False, uses_power: bool = False, speech: bool = False,
                 method: str = "", held: Sequence[str] = (), rules: Any, reading: bool = False,
                 literacy_known: bool = False, deed_tag: str | None = None) -> Computed:  # rule: 00.12.3
    """00.12.3's computation, pure. A *need* is an excluded method (any verb's `excludes`, matched literally), a
    supernatural or licensed technique (`uses_power`), or reading writing once literacy is on record. With a need,
    a held covering license gives G2, else G3 naming the would-be license (PR-01-5 step 1, looked up by code).
    Without one, the act is the basic verb's (G1), or G2 when a held license is the trained form of that verb."""
    v = covering_verb(verb, against_will=against_will, speech=speech)
    if v is None or v not in rules.basic_verbs:
        if uses_power:
            v = None
        else:
            return Computed("G3", v, would_be_license(method, rules, deed_tag), f"no basic verb {verb!r} fits")
    ex = excluded_anywhere(rules, v, method)
    need: str | None = None
    wanted: str | None = None
    if ex is not None:
        need = f"{ex['what']} needs {ex.get('needs')}"
        named = _LIC.findall(str(ex.get("needs") or "")) or _tongue(rules, method, str(ex.get("needs") or ""))
        wanted = next((x for x in named if x in held), named[0] if named else None)
    elif reading and literacy_known and not uses_power:  # reading a mind is a power, not letters
        need, wanted = "reading writing needs letters", LETTERS
    elif uses_power:
        need = "a supernatural or licensed technique"
    if need is None:
        cover = _plain_cover(rules, v, held)
        if cover:
            return Computed("G2", v, cover, f"held license {cover} is the trained form of {v}")
        return Computed("G1", v, None, f"{v} covers it")
    wanted = wanted or would_be_license(method, rules, deed_tag)
    if wanted and wanted in held:
        return Computed("G2", v, wanted, f"held license {wanted} covers it ({need})")
    if wanted is None and uses_power and (cover := _power_cover(rules, held)) is not None:
        return Computed("G2", v, cover, f"held license {cover} covers it ({need})")
    return Computed("G3", v, wanted, f"no held license covers it ({need})")


# ------------------------------------------------------------------------------------------- redirect


def would_be_license(method: str, rules: Any, deed_tag: str | None = None) -> str | None:  # rule: PR-01-5
    """PR-01-5 step 1: the license whose name and scope share the most words with the method (at least two), by
    code; no role names it."""
    m = words(method)
    best, score = None, 1
    for lid, lic in rules.licenses.items():
        text = f"{lic.get('name', '')} {lic.get('scope', '')}"
        s = len(m & words(text))
        if deed_tag and deed_tag in (lic.get("tags") or ()):
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


def _nearest(beat: Beat, rules: Any, verb: str | None = None) -> RedirectOption:
    verb = verb or beat.verb
    if verb and verb in rules.basic_verbs:
        return RedirectOption(kind="basic_verb", verb=verb, method=f"another way to {beat.intent}")
    return RedirectOption(kind="intent", verb="verb.observe", method=f"look for what could serve: {beat.intent}")


def build_redirect(beat: Beat, rules: Any, alternatives: Iterable[RedirectOption] = (), *,
                   lid: str | None = None, verb: str | None = None) -> Redirect:  # rule: PR-01-5
    """PR-01-5 steps 1-3 (the four-part redirect of 01.3.6): nothing is spent."""
    lic = _lic(rules, lid)
    options: list[RedirectOption] = []
    if lid is not None and lic is not None:
        fb = _fallback_option(lid, lic)
        if fb is not None:
            options.append(fb)
        options += _valid_alternatives(alternatives, rules)
        if not options:
            options.append(_nearest(beat, rules, verb))
        return Redirect(intent=beat.intent, missing=lid, missing_kind="license", options=options,
                        acquisition_paths=_paths(lic))
    branch = beat.deed_tag or "deed"
    options = _valid_alternatives(alternatives, rules) or [_nearest(beat, rules, verb)]
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


def zero_reach(beat: Beat, *, rules: Any, verb: str | None = None, mint: Callable[[str], str] | None = None,
               store: Any = None, staged: Sequence[Event] = ()) -> GateDecision:  # rule: 01.3.7
    # rule: 01.6.10
    """I-160(a), DL-01-33: the Framer's reach factors (two unoffset, or a total potency) leave no reach: G4 before
    the OFFER, with 01.3.7's redirect, no roll and nothing spent."""
    from engine import ids

    why = "two effect factors stand against the method, unoffset: it cannot reach its intent (01.3.7, 01.6.10)"
    key = f"zero_reach.{beat.target if beat.target and beat.target != 'none' else ids.slug(beat.intent)[:40]}"
    found = find_rulings(store, gate_signature("g4", key), staged=staged)
    return GateDecision(gate="G4", verb=verb or beat.verb, reason=why, precedent=found,
                        redirect=Redirect(intent=beat.intent, missing=key, missing_kind="zero_reach",
                                          options=[_nearest(beat, rules, verb)]),
                        events=_ruling("g4", key, beat, why, [], precedent_for(found), mint, store, staged))


def held_ids(state: Any, actor: str) -> list[str]:
    return [x.license_id for x in state.licenses.get(actor, []) if held_license(state, actor, x.license_id)]


# a look at writing ("peek at the ledger", "glance over the notice") reads it as surely as "read" does
LOOKS_AT = re.compile(r"\b(?:look|looks|looking|peek|peeks|peeking|glance|glances|glancing|scan|scans|scanning|skim|"
                      r"skims|skimming|study|studies|studying|pore|pores|poring|check|checks|checking)\b"
                      r"(?:\s+\w+){0,2}?\s+(?:at|over|through|down)\b", re.I)


def reads_writing(beat: Beat, verb: str | None, state: Any = None) -> bool:  # rule: 02.4.6
    """The PC's own method reads writing, whatever the verb label (DL-01-43: reading folded into a Talk, "I read the
    list over his shoulder and ask the name", met no gate in round 7): a `learn` goal, or a look, whose method reads
    (the reading words, or a look at a thing with writing) a target with words on record or writing it names.
    Asking someone else to read (`persuade_to`) is their act, not the PC's; "read a person or a scene" is Observe's
    own act, never letters."""
    from engine.retrieve.scene import READING, written_words

    kind = beat.change.kind if beat.change is not None else "none"
    if kind != "learn" and not (verb == "verb.observe" and kind == "none"):
        return False
    text = f"{beat.method} {beat.intent} {beat.how or ''}"
    on_record = any(state is not None and x in getattr(state, "entities", {}) and written_words(state, str(x))
                    is not None for x in (beat.target, beat.change.what if beat.change else None) if x)
    # a look counts only when what it looks at is the writing (the next few words), or the target bears words
    looks = any(on_record or WRITING.search(text[m.end():m.end() + 40]) for m in LOOKS_AT.finditer(text))
    return looks or (bool(READING.search(text)) and (on_record or bool(WRITING.search(text))))


def check_gate(beat: Beat, *, state: Any, rules: Any, store: Any = None, staged: Sequence[Event] = (),
               mint: Callable[[str], str] | None = None, canon_impossible: Iterable[str] = (),
               alternatives: Iterable[RedirectOption] = ()) -> GateDecision:  # rule: 01.3.1
    # rule: 00.12.3
    """The engine's GATE: G4 from an active condition or a cited fact on record; an accepted crude fallback rolls;
    otherwise `compute_gate` from the beat's verb and facets and the actor's held licences."""
    alts = list(alternatives)
    held = [x for x in held_ids(state, beat.actor)
            if not any(x in (f.get("licenses") or ()) for _, f in _restricts(rules, state, beat.actor))]
    # an accepted crude fallback (01.3.5): a G3 that rolls, on the fallback's own verb
    if beat.mode == "fallback" and beat.fallback_license and (lic := _lic(rules, beat.fallback_license)) is not None:
        fb = _fallback_option(beat.fallback_license, lic)
        if fb is not None and fb.verb == beat.verb:
            return GateDecision(gate="G3", verb=beat.verb, license=beat.fallback_license, mode="fallback",
                                reason=f"crude fallback of {beat.fallback_license} accepted")
    # a stretched or emulated license the engine set (01.3.5): G2 under its price, when held and declared
    if beat.mode in ("stretch", "emulate") and beat.license:
        lic = _lic(rules, beat.license)
        if beat.license in held and lic is not None and lic.get(beat.mode):
            return GateDecision(gate="G2", verb=beat.verb, license=beat.license, mode=beat.mode,
                                reason=f"held license {beat.license} ({beat.mode})")
    langs = any(x.startswith("lic.lang.") for x in held_ids(state, beat.actor))
    c = compute_gate(beat.verb, against_will=beat.against_will, uses_power=beat.uses_power, speech=beat.speech,
                     method=f"{beat.method} {beat.intent}", held=held, rules=rules,
                     reading=reads_writing(beat, covering_verb(beat.verb, against_will=beat.against_will,
                                                               speech=beat.speech), state),
                     literacy_known=langs, deed_tag=beat.deed_tag)
    # G4 (01.3.7): a condition that forbids the method, or an established fact the Reader cites
    g4: tuple[str, str, Literal["fact", "condition"]] | None = None
    forbid = forbidden_by_condition(beat, state=state, rules=rules, verb=c.verb,
                                    license=c.license if c.gate == "G2" else None)
    if forbid is not None:
        g4 = (forbid[0], f"an active condition forbids {forbid[1]}", "condition")
    elif beat.g4_fact and beat.g4_fact in state.facts:
        g4 = (beat.g4_fact, "success requires an established fact to be false", "fact")
    elif beat.g4_fact and beat.g4_fact in set(canon_impossible):
        g4 = (beat.g4_fact, "impossible for anyone in the setting (canon)", "fact")
    if g4 is not None:
        key, why, kind = g4
        found = find_rulings(store, gate_signature("g4", key), staged=staged)
        options = _valid_alternatives(alts, rules) or [_nearest(beat, rules, c.verb)]
        if kind == "condition" and options[0].verb == c.verb:
            options = [RedirectOption(kind="intent", verb="verb.observe", method=f"another way to {beat.intent}")]
        return GateDecision(gate="G4", verb=c.verb, reason=why, fact_cited=key, precedent=found,
                            redirect=Redirect(intent=beat.intent, missing=key, missing_kind=kind, options=options),
                            events=_ruling("g4", key, beat, why, [key] if kind == "fact" else [],
                                           precedent_for(found), mint, store, staged))
    if c.gate in ("G1", "G2"):
        return GateDecision(gate=c.gate, verb=c.verb, license=c.license, reason=c.reason)
    red = build_redirect(beat, rules, alts, lid=c.license, verb=c.verb)
    found = find_rulings(store, gate_signature("g3_redirect", red.missing), staged=staged)
    d = GateDecision(gate="G3", verb=c.verb, redirect=red, precedent=found, reason=c.reason)
    d.events = _ruling("g3_redirect", red.missing, beat, d.reason, [], precedent_for(found), mint, store, staged)
    if red.missing_kind == "deed_branch" and mint is not None:  # no license in data covers it (01.3.5)
        rec = RulingRecord(signature=f"rule_conflict:{red.missing}", situation=beat.restatement or beat.intent,
                           kind="rule_conflict", review_flag=True,
                           result={"degree": None, "outcome": f"no license entry covers this method under "
                                                              f"{red.missing}; ch.05/13 to author one"})
        d.events.append(log_ruling(rec, mint, store=store, staged=[*staged, *d.events], rule_id="01.3.5"))
    return d
