"""Anchor candidates for the ANCHOR step (00.15.3; anchors.yaml `compile.retrieval`).

    ids = anchor_candidates(beat, state, rules)     # ≤ 8 anchor ids, best first, deterministic
    lines = anchor_menu(ids, rules)                  # one compact line per candidate, for the Framer packet

A beat is the Reader's beat (a dict or an object with `verb`, `intent_verbs`, `intent`, `method`, `license`,
`gate`). Scores follow `anchors.yaml#compile.retrieval.score`: intent verb match 3 (per matched verb), deed tag
equal or ancestor 2, situation tag match 1. The beat's basic-verb anchor is always included first (the
default, 00.15.3). An anchor needs an intent-verb or deed-tag match to be a candidate: a situation tag alone
would let every T-06-9 ruling into every conflict beat. Ties: specificity order, then rule id, then anchor id.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

from engine.store.projection import WorldState

MAX_CANDIDATES = 8  # fallback when anchors.yaml has no retrieval block


def _get(beat: Any, key: str, default: Any = None) -> Any:
    if isinstance(beat, Mapping):
        return beat.get(key, default)
    return getattr(beat, key, default)


def _norm(s: str) -> str:
    return re.sub(r"[\s_\-]+", " ", str(s).strip().lower())


def natural_key(s: str) -> tuple[Any, ...]:
    """Sort key that orders ids naturally (01.6.10 after 01.6.9, T-06-10 after T-06-9)."""
    return tuple((0, int(p)) if p.isdigit() else (1, p) for p in re.split(r"(\d+)", s) if p)


def _is_prefix(parent: str, child: str) -> bool:
    """True when `parent` equals `child` or is its ancestor in the dotted tag tree."""
    return parent == child or child.startswith(parent + ".")


def _retrieval(rules: Any) -> Mapping[str, Any]:
    return rules.doc("anchors").get("compile", {}).get("retrieval", {})


def scene_situation_tags(state: WorldState, rules: Any) -> list[str]:  # rule: 12.4.5
    """The scene's situation tags plus the tags its time mode loads (pacing.yaml#modes)."""
    tags: list[str] = []
    scene = state.scene
    if scene is not None:
        tags.extend(scene.situation_tags)
        tags.extend(mode_tags(scene.mode, rules))
    return list(dict.fromkeys(tags))


def mode_tags(mode: str | None, rules: Any) -> list[str]:  # rule: 12.4.5
    """Situation tags a time mode loads (`pacing.yaml#modes[].cards`); [] for an unknown mode."""
    if not mode:
        return []
    for row in rules.pacing.get("modes", []):
        cards = row.get("cards")
        if row.get("to") == mode and isinstance(cards, list | tuple):
            return [str(c) for c in cards]
    return []


def beat_deed_tags(beat: Any, rules: Any) -> list[str]:
    """Deed tags implied by the beat: its verb's (anchors.yaml verb_tag_map) and its licence's tags."""
    tags: list[str] = []
    verb = _get(beat, "verb")
    vmap = rules.doc("anchors").get("compile", {}).get("verb_tag_map", {})
    if verb and verb in vmap:
        tags.extend(vmap[verb].get("deed_tags", []))
    lic = _get(beat, "license")
    if lic and lic != "none" and rules.has(lic):
        tags.extend(t for t in rules.get(lic).get("tags", []) if str(t).startswith("deed."))
    return list(dict.fromkeys(tags))


def verb_anchor(verb: str | None, rules: Any) -> str | None:
    """The anchor id of a basic verb's card (the ANCHOR default, 00.15.3)."""
    if not verb:
        return None
    for aid, a in rules.anchors.items():
        if a.get("verb") == verb and a.get("specificity") == "verb_card":
            return aid
    return None


def _intent_phrases(beat: Any) -> tuple[set[str], str]:
    verbs = {_norm(v) for v in _get(beat, "intent_verbs", []) or [] if str(v).strip()}
    text = " ".join(str(_get(beat, k) or "") for k in ("intent", "method"))
    return verbs, _norm(text)


def _intent_hits(anchor: Mapping[str, Any], verbs: set[str], text: str) -> int:
    hits = 0
    for phrase in anchor.get("intent_verbs", []):
        p = _norm(phrase)
        if not p:
            continue
        if p in verbs or any(len(v) >= 3 and (re.search(rf"\b{re.escape(v)}\b", p)) for v in verbs) or (
            text and re.search(rf"\b{re.escape(p)}\b", text)
        ):
            hits += 1
    return hits


def score_anchor(anchor: Mapping[str, Any], beat: Any, deed_tags: Iterable[str], situation_tags: Iterable[str],
                 weights: Mapping[str, int]) -> tuple[int, bool]:  # rule: 00.15.3
    """(score, keyed): `keyed` is true when an intent verb or deed tag matched (situation alone is not enough)."""
    verbs, text = _intent_phrases(beat)
    intent = _intent_hits(anchor, verbs, text)
    deeds = list(deed_tags)
    deed = any(_is_prefix(a, b) for a in anchor.get("deed_tags", []) for b in deeds)
    sit = any(_is_prefix(a, s) for a in anchor.get("situation_tags", []) for s in situation_tags)
    score = (intent * weights.get("intent_verb_match", 3) + (weights.get("deed_tag_equal_or_ancestor", 2) if deed else 0)
             + (weights.get("situation_tag_match", 1) if sit else 0))
    return score, bool(intent or deed)


def verb_family(verb: str | None, rules: Any) -> set[str] | None:  # rule: 01.5.1
    """The beat's verb and the basic verbs its card is told apart from (either card's `distinguish`): the
    anchors a re-anchor may move to. None (no verb): any. A Talk beat never re-anchors to a Strike."""
    if not verb or verb not in rules.basic_verbs:
        return None

    def vs(v: str) -> set[str]:
        return {str(d.get("vs")) for d in (rules.basic_verbs[v].get("anchor") or {}).get("distinguish") or ()}

    return {verb, *(vs(verb) & set(rules.basic_verbs)), *(v for v in rules.basic_verbs if verb in vs(v))}


def anchor_candidates(beat: Any, state: WorldState, rules: Any) -> list[str]:  # rule: 00.15.3
    """At most eight anchor ids for this beat, the basic verb's anchor first, then best score; an anchor tied to
    a basic verb outside the beat's verb family is not a candidate (01.5.1: anchors for the beat's verb)."""
    retrieval = _retrieval(rules)
    cap = int(retrieval.get("max_candidates", MAX_CANDIDATES))
    weights = retrieval.get("score", {})
    spec_order = list(rules.doc("anchors").get("compile", {}).get("specificity_order", []))
    deed_tags = beat_deed_tags(beat, rules)
    situation = scene_situation_tags(state, rules)
    default = verb_anchor(_get(beat, "verb"), rules)
    family = verb_family(_get(beat, "verb"), rules)
    scored: list[tuple[int, int, tuple[Any, ...], str]] = []
    for aid, a in rules.anchors.items():
        if aid == default or (family is not None and a.get("verb") and a.get("verb") not in family):
            continue
        score, keyed = score_anchor(a, beat, deed_tags, situation, weights)
        if not keyed:
            continue
        spec = a.get("specificity", "")
        rank = spec_order.index(spec) if spec in spec_order else len(spec_order)
        scored.append((-score, rank, natural_key(str(a.get("rule_id", ""))), aid))
    scored.sort(key=lambda t: (t[0], t[1], t[2], natural_key(t[3])))
    out = [default] if default else []
    out.extend(aid for *_, aid in scored)
    return out[:cap]


def anchor_menu(anchor_ids: Iterable[str], rules: Any) -> list[str]:
    """One compact line per anchor (id, name, rule, intent verbs, knobs) for the Framer's packet."""
    lines = []
    for aid in anchor_ids:
        a = rules.anchors.get(aid)
        if a is None:
            continue
        knobs = "; ".join(
            f"{k.get('knob')}={k.get('default')}" + (f" (or {', '.join(map(str, k['allowed_deltas']))})"
                                                     if k.get("allowed_deltas") else "")
            for k in a.get("knobs", [])
        )
        verbs = ", ".join(map(str, a.get("intent_verbs", [])[:6]))
        lines.append(f"{aid}: {a.get('name', '')} [{a.get('rule_id', '')}] intent: {verbs}. knobs: {knobs}")
    return lines
