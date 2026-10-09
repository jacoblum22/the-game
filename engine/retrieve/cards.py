"""Rule cards for one model call (00.15.4, 12.2.4; FR-029, FR-030).

    cards = load_cards_for(Role.READER, scene.situation_tags, scene.mode, active_triggers, extra_ids=[])
    core = core_cards()                         # the always-loaded core; travels with every call, uncapped

The always-loaded core is exactly 00.15.4's list (`CardIndex.core()`: T-12-1, T-00-1, 00.12.3, 00.3.9,
00.3.14, 00.3.15); the active-trigger list heads the view (the packet builder renders it). The ch.01 cards whose
`Loads in:` line says `core` are NOT core here: 00.15.4 says "only these travel with every turn", and those
cards matter only to the calls that make their decisions. They are this call's **role cards** (the role's
pipeline steps, contracts/model-calls.md), and they count toward the twelve-card cap.

Selection under the cap (`pacing.yaml#packet.max_loaded_cards`, 12), in order:
1. role cards (`ROLE_CARDS`), keeping only cards with a judgment or narration mark: `[D]`-only rules are run
   by code and never need to be in a prompt (research.md R5);
2. the active triggers' cards (12.2.4: "triggers first");
3. `extra_ids`: the anchor candidates' cards, precedent rulings, the PC's held abilities (data entries);
4. situation cards for the scene's tags and its time mode, most specific first: a deeper tag match before a
   shallower one, an explicit `Loads in:` line before a derived tag, then rule-id order. Only rules and
   procedures that carry a `[J*]` or `[N]` mark are eligible.
Triggers and situation cards go only to the scene roles (`SCENE_ROLES`); the Checker and Interpret get their
role cards and `extra_ids`.
Every step is deterministic; duplicates are dropped. The chosen cards are returned stable to volatile (role,
situation, trigger, extra), so a role's packet prefix repeats across calls for prompt caching (DL-12-38).
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from functools import lru_cache
from typing import Any

from engine.build.compile_cards import CardIndex, RuleCard, load_cards
from engine.data.loader import load_rules
from engine.llm.base import Role
from engine.retrieve.anchors import mode_tags, natural_key
from engine.retrieve.triggers import ActiveTrigger, trigger_cards

MAX_LOADED_CARDS = 12  # fallback only; the cap is pacing.yaml#packet.max_loaded_cards

# The cards each role's decisions need (contracts/model-calls.md lists the Reader's and the Framer's).
ROLE_CARDS: dict[Role, tuple[str, ...]] = {
    Role.INTERPRET: ("12.16.2",),
    Role.READER: ("12.2.2", "01.2.1", "01.2.2", "01.2.3", "01.2.4", "01.2.5", "01.2.6", "01.3.1", "01.3.8",
                  "01.4.1", "01.15.2"),
    # 01.6.6 (who rolls) and 01.6.7 (fortune checks) are decided by code, not by a FramerOutput field.
    Role.FRAMER: ("01.5.1", "01.5.3", "01.6.1", "01.6.2", "01.6.3", "01.6.4", "01.6.5", "01.6.8", "01.6.9",
                  "01.6.10", "01.6.11", "01.13.1"),
    Role.WORLD: ("12.11.4", "12.11.5", "12.2.9"),
    Role.DIRECTOR: ("12.4.2", "12.4.3", "12.9.1", "T-12-7"),
    Role.NARRATOR: ("12.14.2", "12.14.3", "12.14.4", "12.14.9", "12.14.12", "12.14.13", "00.6.6"),
    Role.CHECKER: ("12.3.1",),
    Role.TESTIMONY: (),  # PR-12-12 step 2: its prompt and the said words are the whole packet
}

# Which roles get trigger and situation cards. The Checker sees only its own instructions and the draft
# (contracts/model-calls.md C); Interpret maps a fixed block's answer and needs no scene rules.
SCENE_ROLES = frozenset({Role.READER, Role.FRAMER, Role.WORLD, Role.DIRECTOR, Role.NARRATOR})

SITUATION_KINDS = ("rule", "procedure")
NEVER_SITUATION = frozenset({"00.2.5"})  # the card template itself (its placeholder says "Loads in: any")


@lru_cache(maxsize=1)
def _index() -> CardIndex:
    return load_cards()


def max_cards(rules: Any = None) -> int:  # rule: 00.15.4
    rules = rules if rules is not None else load_rules()
    return int(rules.pacing.get("packet", {}).get("max_loaded_cards", MAX_LOADED_CARDS))


def core_cards(index: CardIndex | None = None) -> list[RuleCard]:  # rule: 00.15.4
    """The always-loaded core cards (without the active-trigger list, which the packet renders)."""
    return (index or _index()).core()


def judged(card: RuleCard) -> bool:
    """True when the card has a model decision or narration in it (a `[J*]` or `[N]` mark, or no marks)."""
    return not card.kinds or any(k.startswith("[J") or k == "[N]" for k in card.kinds)


def role_cards(role: Role, index: CardIndex | None = None) -> list[RuleCard]:  # rule: 00.15.4
    idx = index or _index()
    return [idx.get(i) for i in ROLE_CARDS.get(role, ()) if i in idx and judged(idx.get(i))]


def _depth(card: RuleCard, tags: Sequence[str]) -> int:
    """How specific the best match between the card's tags and the wanted tags is (0 = `any` only)."""
    best = 0
    for want in tags:
        for have in card.tags:
            if have == want or want.startswith(have + "."):
                best = max(best, have.count(".") + 1)
    return best


def situation_cards(tags: Iterable[str], index: CardIndex | None = None) -> list[RuleCard]:  # rule: 12.2.4
    """Eligible situation cards for these tags, most specific first."""
    idx = index or _index()
    want = list(dict.fromkeys(tags))
    seen: dict[str, RuleCard] = {}
    for tag in want:
        for c in idx.by_tag(tag):
            if c.kind in SITUATION_KINDS and judged(c) and "core" not in c.tags and c.id not in NEVER_SITUATION:
                seen.setdefault(c.id, c)
    return sorted(seen.values(), key=lambda c: (-_depth(c, want), c.tags_derived, natural_key(c.id)))


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
    situation_tags: Iterable[str] = (),
    mode: str | None = None,
    triggers: Iterable[ActiveTrigger | str] = (),
    extra_ids: Iterable[str] = (),
    *,
    rules: Any = None,
    index: CardIndex | None = None,
    cap: int | None = None,
) -> list[RuleCard]:
    """At most `cap` (12) cards for one call: chosen role, trigger, extra, then situation cards (module
    docstring), returned stable to volatile for prompt caching: role, situation, trigger, extra (DL-12-38)."""
    idx = index or _index()
    rules = rules if rules is not None else load_rules()
    limit = cap if cap is not None else max_cards(rules)
    out: dict[str, tuple[int, RuleCard]] = {}

    def take(cards: Iterable[RuleCard | None], place: int) -> None:
        for c in cards:
            if len(out) >= limit:
                return
            if c is not None and c.id not in out:
                out[c.id] = (place, c)

    core_ids = {c.id for c in idx.core()}
    scene_role = role in SCENE_ROLES
    take(role_cards(role, idx), 0)
    if scene_role:
        take((idx.get(i) for i in trigger_cards(triggers) if i in idx and i not in core_ids), 2)
    take(((idx.get(i) if i in idx else data_card(i, rules)) for i in extra_ids if i not in core_ids), 3)
    if scene_role:
        tags = list(situation_tags) + mode_tags(mode, rules)
        take((c for c in situation_cards(tags, idx) if c.id not in core_ids), 1)
    return [c for _, c in sorted(out.values(), key=lambda pc: pc[0])]


def anchor_card_ids(anchor_ids: Iterable[str], rules: Any) -> list[str]:
    """The rule card ids behind anchor candidates (for `extra_ids`), in candidate order, without repeats."""
    out: list[str] = []
    for aid in anchor_ids:
        rid = rules.anchors.get(aid, {}).get("rule_id")
        if rid and rid not in out:
            out.append(str(rid))
    return out
