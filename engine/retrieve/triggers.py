"""Active triggers (12.2.3; `get_active_triggers`, 00.14.2 tool 30).

    active = get_active_triggers(state, rules)               # ordered per 12.2.3
    active = get_active_triggers(state, rules, raised=["trg.lead_injection"])   # plus this turn's raises

Triggers are *raised* by engine handlers (harm, clocks, pacing, recognition, ...), never remembered by a model.
A raised trigger lives in the store as a current fact whose predicate is the trigger id (kind `flag`, any
subject; the value is `true` or a dict of parameters such as `{source, cause}`); writing a falsy value lowers
it. Handlers that raise a trigger only for this turn may pass it in `raised` instead.

`TRIGGERS` is the registry: every `trg.*` id the rules name, with its 12.2.3 handling group and the rule cards
to load when it is active. Groups (12.2.3): 1 safety flags, 2 interrupts from advance_time, 3 lethal warning
and harm states, 4 clock completions and stage changes, 5 lead injection, 6 recognition and standing offers,
7 pacing pushes, 8 every other chapter trigger (rule-id order). Groups 1, 2 and 4 have no `trg.` id in the
rules; the engine names them `trg.safety_flag`, `trg.interrupt` and `trg.clock_stage`.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict

from engine.retrieve.anchors import natural_key
from engine.store.projection import WorldState


class TriggerDef(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    group: int  # 12.2.3 handling order
    rule_id: str  # the rule that defines the trigger
    cards: tuple[str, ...]  # rule cards to load while it is active


class ActiveTrigger(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    group: int
    rule_id: str
    cards: tuple[str, ...]
    subject: str | None = None  # the fact's subject when raised in the store
    fact_id: str | None = None
    params: dict[str, Any] = {}

    def line(self) -> str:
        """The active-trigger list entry (00.15.4 core)."""
        extra = ", ".join(f"{k}={v}" for k, v in sorted(self.params.items()))
        about = f" on {self.subject}" if self.subject and self.subject != "world" else ""
        return f"{self.id}{about} ({self.rule_id}){': ' + extra if extra else ''}"


def _t(tid: str, group: int, rule_id: str, *cards: str) -> TriggerDef:
    return TriggerDef(id=tid, group=group, rule_id=rule_id, cards=cards or (rule_id,))


TRIGGERS: dict[str, TriggerDef] = {t.id: t for t in [
    _t("trg.safety_flag", 1, "12.5.6"),
    _t("trg.interrupt", 2, "00.7.8"),
    _t("trg.lethal_warning", 3, "07.3.3"),
    _t("trg.danger_notice", 3, "07.3.8"),
    _t("trg.exits", 3, "07.3.7", "07.3.7", "07.4.1", "07.4.3"),
    _t("trg.clock_stage", 4, "00.8.4"),
    _t("trg.lead_injection", 5, "12.8.2", "12.8.2", "PR-12-3"),
    _t("trg.04.crisis_offer", 6, "PR-04-2", "04.7.1"),
    _t("trg.04.offer_due", 6, "04.7.1"),
    _t("trg.04.pick_due", 6, "04.7.1"),
    _t("trg.04.lapse_warning", 6, "04.8.2"),
    _t("trg.pacing_push", 7, "12.7.4"),
    _t("trg.04.fraying", 8, "04.9.2", "04.9.2", "04.9.4"),
    _t("trg.11.flashpoint", 8, "11.5.4"),
    _t("trg.16.band_cap_changed", 8, "16.2.4"),
    _t("trg.16.betrayal", 8, "16.6.6", "16.6.6", "PR-16-7"),
    _t("trg.16.confrontation", 8, "PR-16-7"),
    _t("trg.16.departure", 8, "PR-16-7"),
]}

OTHER_GROUP = 8


def trigger_def(tid: str) -> TriggerDef:
    """The registry entry; an unregistered `trg.*` id is a chapter trigger of group 8 with no cards."""
    return TRIGGERS.get(tid) or TriggerDef(id=tid, group=OTHER_GROUP, rule_id=tid, cards=())


def _params(value: Any) -> dict[str, Any]:
    return {str(k): v for k, v in value.items()} if isinstance(value, dict) else {}


def get_active_triggers(  # rule: 12.2.3
    state: WorldState, rules: Any = None, *, raised: Iterable[str] = ()
) -> list[ActiveTrigger]:
    """Every trigger currently raised, in 12.2.3 handling order (group, then rule id, then subject).

    `rules` is accepted for the tool signature (00.14.2 tool 30); card ids come from the registry.
    """
    found: dict[tuple[str, str | None], ActiveTrigger] = {}
    for f in state.facts.values():
        if not f.predicate.startswith("trg.") or not f.value:
            continue
        d = trigger_def(f.predicate)
        found[(d.id, f.subject)] = ActiveTrigger(id=d.id, group=d.group, rule_id=d.rule_id, cards=d.cards,
                                                 subject=f.subject, fact_id=f.id, params=_params(f.value))
    for tid in raised:
        d = trigger_def(tid)
        if not any(k[0] == tid for k in found):
            found[(tid, None)] = ActiveTrigger(id=d.id, group=d.group, rule_id=d.rule_id, cards=d.cards)
    return sorted(found.values(), key=lambda t: (t.group, natural_key(t.rule_id), t.id, t.subject or ""))


def trigger_cards(active: Iterable[ActiveTrigger | str]) -> list[str]:
    """Card ids to load for the active triggers, in handling order, without repeats."""
    out: list[str] = []
    for t in active:
        cards = trigger_def(t).cards if isinstance(t, str) else t.cards
        out.extend(c for c in cards if c not in out)
    return out
