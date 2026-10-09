"""What rule text one model call gets (00.15.4, 12.2.4 items 1-2; DL-12-104, DL-00-07; spec 020).

    digest = guidance_digest(Role.READER)        # the role's guidance: the packet's stable, cacheable prefix
    cards = load_cards_for(Role.FRAMER, (), None, active_triggers, extra_ids=anchor_card_ids(cands, rules))

**Guidance, not the core** (12.2.4 item 1, `pacing.yaml#packet.guidance_digest: per_role`): each role gets a short
digest for the judgment it makes, generated from its cards (`GUIDANCE`): a card's `Decisions (J):` block where it has
one, else its body (a table, a prose rule), with revision and source tags stripped; for the Reader also the change
kinds and the verb covers from data. It is identical from call to call. The 00.15.4 core is the specification the
pipeline implements and is never sent.

**Cards only where code knows they apply** (12.2.4 item 2): a fired trigger's card (scene roles) and `extra_ids`
(the anchor candidates' cards, a Talk frame's 15.3.2, an ability in use as its data entry), at most
`pacing.yaml#packet.max_loaded_cards` (12), stable to volatile (trigger, extra). Situation cards picked by tag and
sorted by id are retired (`situation_cards_by_tag: retired`): they filled 70-87% of each role's input with rules it
did not apply (round 6, I4 A).
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from functools import lru_cache
from typing import Any

from engine.build.compile_cards import CardIndex, RuleCard, load_cards
from engine.data.loader import load_rules
from engine.llm.base import Role
from engine.retrieve.triggers import ActiveTrigger, trigger_cards

MAX_LOADED_CARDS = 12  # fallback only; the cap is pacing.yaml#packet.max_loaded_cards

# 12.2.4 item 1: the cards each role's guidance digest is generated from (the judgment the call makes). The narrator's
# and the checker's are their pre-020 role cards: spec 019 is rewriting those roles.
GUIDANCE: dict[Role, tuple[str, ...]] = {
    Role.INTERPRET: ("12.16.2",),
    Role.READER: ("01.2.2",),  # plus the change kinds and verb covers from data (`_reader_data`)
    Role.FRAMER: ("01.5.1", "01.5.3", "01.6.1", "01.6.2", "01.6.3", "01.6.4", "01.6.5", "01.6.8", "01.6.9",
                  "01.6.10", "01.6.11", "01.13.1"),
    Role.WORLD: ("15.2.3",),
    Role.DIRECTOR: ("T-12-7",),
    Role.NARRATOR: ("12.14.2", "12.14.3", "12.14.4", "12.14.9", "12.14.12", "12.14.13", "00.6.6"),
    Role.CHECKER: ("12.3.1",),
    Role.TESTIMONY: (),  # PR-12-12 step 2: its prompt and the said words are the whole packet
}
TALK_CARD = "15.3.2"  # request size: a Talk frame's card (12.2.4 item 2)

# Which roles get trigger cards: the scene roles (the Checker and Interpret judge no scene trigger).
SCENE_ROLES = frozenset({Role.READER, Role.FRAMER, Role.WORLD, Role.DIRECTOR, Role.NARRATOR})

_TAGS = re.compile(r" ?\[(?:revision:|amended:|DL-|I-\d|R\d|R:|P-\d|C:|SG-|OEQ-)[^\]]*\]"
                   r"|\*(?:Retires|Evidence):\*(?:[^().]|\([^)]*\))*\.\s*")  # history, not guidance
_FIELD = re.compile(r"^[A-Z][A-Za-z ()\[\]/'-]{2,40}:\s{2,}", re.M)


@lru_cache(maxsize=1)
def _index() -> CardIndex:
    return load_cards()


def max_cards(rules: Any = None) -> int:  # rule: 00.15.4
    rules = rules if rules is not None else load_rules()
    return int(rules.pacing.get("packet", {}).get("max_loaded_cards", MAX_LOADED_CARDS))


def judged(card: RuleCard) -> bool:
    """True when the card has a model decision or narration in it (a `[J*]` or `[N]` mark, or no marks)."""
    return not card.kinds or any(k.startswith("[J") or k == "[N]" for k in card.kinds)


def decisions(card: RuleCard) -> str:  # rule: 12.2.4
    """The card as guidance: its title line and its `Decisions (J):` block when it has one (the judgment; the `[D]`
    computation, triggers and state writes are code's), else its whole body; source and revision tags stripped."""
    body = card.body.strip()
    m = re.search(r"^Decisions \(J\):", body, re.M)
    if m:
        rest = body[m.start():]
        nxt = next((f.start() for f in _FIELD.finditer(rest) if f.start() > 0), len(rest))
        body = body.splitlines()[0] + "\n" + rest[:nxt].rstrip()
    return _TAGS.sub("", body)


def _reader_data(rules: Any) -> str:  # rule: 01.2.7
    # rule: T-00-11
    """The Reader's two data lists: the change kinds with their slots, and each basic verb's covers."""
    kinds = rules.resolution["intended_change"]["kinds"]
    lines = ["Change kinds and their slots (01.2.7): " + "; ".join(
        f"{k} ({', '.join(v.get('slots') or []) or '-'})" for k, v in kinds.items())]
    lines.append("Verb covers (T-00-11):")
    lines += [f"- {v.get('name', vid)}: {', '.join(str(c) for c in v.get('covers') or [])}"
              for vid, v in rules.basic_verbs.items() if v.get("covers")]
    return "\n".join(lines)


@lru_cache(maxsize=16)
def _digest(role: Role, rules_hash: str) -> str:
    idx = _index()
    parts = [decisions(idx.get(i)) for i in GUIDANCE.get(role, ()) if i in idx and judged(idx.get(i))]
    if role == Role.READER:
        parts.append(_reader_data(load_rules()))
    return "\n\n".join(parts)


def guidance_digest(role: Role, rules: Any = None) -> str:  # rule: 12.2.4
    # rule: 00.15.4
    """The role's guidance digest (12.2.4 item 1): identical from call to call, so it is the cacheable prefix."""
    rules = rules if rules is not None else load_rules()
    return _digest(role, str(getattr(rules, "hash", "")))


def data_card(entry_id: str, rules: Any) -> RuleCard | None:
    """A data entry (an ability, a licence, ...) as a card: its card is its data entry (12.2.4, 05.3.6)."""
    if rules is None or not rules.has(entry_id):
        return None
    entry = rules.get(entry_id)
    body = "\n".join(f"{k}: {v}" for k, v in entry.items() if k not in ("basis", "lifecycle", "id"))
    return RuleCard(id=entry_id, kind="rule", title=str(entry.get("name", entry_id)), chapter="data",
                    file=str(rules.where(entry_id)), lines=(0, 0), body=body, tokens=len(body) // 4)


def load_cards_for(  # rule: 12.2.4
    role: Role,
    situation_tags: Iterable[str] = (),  # retired (DL-12-104); accepted so callers that still pass it work
    mode: str | None = None,  # retired with it
    triggers: Iterable[ActiveTrigger | str] = (),
    extra_ids: Iterable[str] = (),
    *,
    rules: Any = None,
    index: CardIndex | None = None,
    cap: int | None = None,
) -> list[RuleCard]:
    """At most `cap` (12) cards code knows apply (12.2.4 item 2): the fired triggers' cards (scene roles), then
    `extra_ids` (a data entry becomes a card), stable to volatile. The role's own guidance is `guidance_digest`."""
    idx = index or _index()
    rules = rules if rules is not None else load_rules()
    limit = cap if cap is not None else max_cards(rules)
    core_ids = {c.id for c in idx.core()}
    out: dict[str, RuleCard] = {}
    wanted: list[RuleCard | None] = []
    if role in SCENE_ROLES:
        wanted += [idx.get(i) for i in trigger_cards(triggers) if i in idx and i not in core_ids]
    wanted += [(idx.get(i) if i in idx else data_card(i, rules)) for i in extra_ids if i not in core_ids]
    for c in wanted:
        if c is not None and c.id not in out and len(out) < limit:
            out[c.id] = c
    return list(out.values())


def anchor_card_ids(anchor_ids: Iterable[str], rules: Any) -> list[str]:
    """The rule card ids behind anchor candidates (for `extra_ids`), in candidate order, without repeats."""
    out: list[str] = []
    for aid in anchor_ids:
        rid = rules.anchors.get(aid, {}).get("rule_id")
        if rid and rid not in out:
            out.append(str(rid))
    return out
