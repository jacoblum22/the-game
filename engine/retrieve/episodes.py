"""Scene cards (12.4.8 step 9): episodic recall computed from events, never from prose (00.6.9d).

    cards = cards_for(state, present_and_spotlight_ids, k=2)   # ended scenes, by entity overlap, then recency
    lines = card_lines(state, cards[0])                         # one line, as the PC knows it

The projection folds each card from its scene's events (`WorldState.scene_cards`), so `store.rebuild()` regenerates
them all. A card names people as the PC knows them (12.10.2) and shows only facts the narrator view may hold.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from engine.store.projection import SceneCard, WorldState
from engine.store.views import display_name
from engine.time.clock import day_index

DEGREE = {"critical_success": "a great success", "success": "a success", "failure": "a failure",
          "critical_failure": "a bad failure", None: "unresolved"}
MAX_ITEMS = 3  # facts and beats per card line (a card is ~150 tokens, view_budget.scene_cards / 2)


def card_entities(state: WorldState, card: SceneCard) -> set[str]:
    """Everyone and everything the card involves: cast, place, beat actors and targets, the subjects of its facts."""
    ids = {*card.cast, *([card.place] if card.place else [])}
    ids |= {str(b[k]) for b in card.beats for k in ("actor", "target") if b.get(k)}
    ids |= {f.subject for fid in [*card.facts, *card.memories] if (f := state.facts.get(fid)) is not None}
    return {i for i in ids if i in state.entities}


def cards_for(state: WorldState, ids: Iterable[str], k: int = 2) -> list[SceneCard]:  # rule: 12.2.4
    """At most `k` ended scenes' cards involving any of `ids`: most shared entities first, then the most recent.
    The scene still running has no card in the view (its exchanges are the verbatim window)."""
    want = {i for i in ids if i in state.entities and state.entities[i].kind != "pc"}
    if not want or k <= 0:
        return []
    scored = [(len(card_entities(state, c) & want), c) for c in state.scene_cards.values() if c.ended_at is not None]
    scored = [x for x in scored if x[0]]
    scored.sort(key=lambda x: (-x[0], -x[1].started_seq))
    return [c for _, c in scored[:k]]


def _name(state: WorldState, eid: Any) -> str:
    if not isinstance(eid, str) or eid not in state.entities:
        return ""
    seal = state.seals.get(eid)
    if seal is not None:
        return seal.slice or ""
    return "you" if state.entities[eid].kind == "pc" else display_name(state, eid)


def card_lines(state: WorldState, card: SceneCard) -> list[str]:  # rule: 12.4.8
    """The card in words, as the PC knows it: when and where, who was there, the agenda and its answer, the beats,
    and up to three facts written (never sealed ones, never a fact's `truth`)."""
    when = f"day {day_index(card.started_at) + 1}" if card.started_at else ""
    where = _name(state, card.place)
    cast = [n for n in (_name(state, i) for i in card.cast) if n]
    head = f"{card.scene} ({', '.join(x for x in (when, where) if x)})"
    bits = [f"with {', '.join(cast[:4])}" if cast else ""]
    if card.agenda:
        bits.append(f"asked: {card.agenda}" + (f" -> {card.answer.replace('_', ' ')}" if card.answer else ""))
    beats = [f"{_name(state, b['actor']) or 'someone'} {str(b.get('verb') or 'acted').rsplit('.', 1)[-1]}"
             + (f" {t}" if (t := _name(state, b.get("target"))) else "") + f" ({DEGREE.get(b.get('degree'), '')})"
             for b in card.beats[:MAX_ITEMS]]
    if beats:
        bits.append("beats: " + "; ".join(beats))
    facts = []
    pc = next((i for i, e in state.entities.items() if e.kind == "pc"), "")
    known = state.knowledge.get(pc, {})
    for fid in card.facts:
        f = state.facts.get(fid)
        if f is None or fid in state.seals or f.subject in state.seals or f.predicate.startswith("detail.") \
                or not (f.visibility in ("shown", "available") or fid in known):  # as the PC knows it
            continue
        facts.append(f"{_name(state, f.subject) or f.subject} {f.predicate.replace('_', ' ')}: {str(f.value)[:60]}")
        if len(facts) == MAX_ITEMS:
            break
    if facts:
        bits.append("noted: " + "; ".join(facts))
    if card.memories:
        bits.append(f"{len(card.memories)} memories kept")
    threads = [n for n in (_name(state, t) for t in card.threads) if n]
    if threads:
        bits.append("threads: " + ", ".join(threads[:2]))
    return [f"{head}: " + "; ".join(b for b in bits if b)]
