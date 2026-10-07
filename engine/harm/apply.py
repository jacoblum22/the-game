"""`apply_harm` and the harm-state ladder (07.1–07.2; PR-07-1), restoring Vitality, stabilizing, the dying check.

    res = apply_harm(ctx, "pc.wren", severity="S3", harm_tags=["harm.frost"], source="foe.wight",
                     frame_id="frame.4", lethal=True)
    tx.add_all(res.events)
    res.transition     # None | staggered | down | dying | dying_step | threshold | defeated | dead | unconscious
    res.threshold      # True: open the Threshold now (threshold.open_threshold)
    res.obligations    # what the narration must carry (descriptor, the [STATUS] block, ...)

Milestone 1 runs wounds coarsely: while Staggered or Dying each harm event adds its wound load (07.2.4) and the
ladder moves exactly as 07.2.6–07.2.8 say, but no wound record is drawn from injuries.yaml (PR-07-2 is M2), so
no site, status penalty or maximum-Vitality penalty follows; each such wound is logged (`log.coarse`). A brink
wound is kept as the `brink` count and healed by the daily pass (engine/harm/rest.py).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.harm import lethal as lethal_mod
from engine.harm.ctx import Writes
from engine.harm.dice import dc_of, degree, distribution, pct, roll_d20
from engine.harm.state import (
    ACTIVE,
    DEAD,
    DYING,
    STAGGERED,
    VITALITY,
    brink,
    descriptor,
    descriptor_words,
    dying_step,
    endure_modifier,
    harm_state,
    is_down,
    on_ladder,
    wound_load,
)
from engine.store.conditions import apply_condition
from engine.store.events import Event

SEVERITIES = ("S1", "S2", "S3", "S4", "S5")
LOAD_LIMIT = 3  # harm.yaml#wounds.load_limit


@dataclass
class HarmResult:
    target: str
    events: list[Event] = field(default_factory=list)
    amount: int = 0
    breakdown: dict[str, Any] = field(default_factory=dict)
    wound: dict[str, Any] | None = None
    load: int = 0
    transition: str | None = None
    obligations: list[str] = field(default_factory=list)
    lethal: bool = False
    lethal_refused: str | None = None
    threshold: bool = False
    triggers: list[str] = field(default_factory=list)  # trg.exits
    hooks: list[str] = field(default_factory=list)  # hooks to fire (00.10), and morale ticks for the conflict


# ------------------------------------------------------------------------------------------- arithmetic


def severity_harm(rules: Any, severity: str) -> int:  # rule: 07.2.1
    """S1..S5 -> 1 / 3 / 5 / 8 / 12 (scales.yaml severity harm)."""
    for s in rules.scales["severity"]:
        if s["id"] == severity:
            return int(s["harm"])
    raise ValueError(f"unknown severity {severity!r}")


def bucket(amount: int) -> str:  # rule: 07.2.4
    """The wound severity of a final amount: 1–2 S1, 3–4 S2, 5–7 S3, 8–11 S4, 12+ S5."""
    return "S1" if amount <= 2 else "S2" if amount <= 4 else "S3" if amount <= 7 else "S4" if amount <= 11 else "S5"


def shift(severity: str, rungs: int) -> str | None:
    i = SEVERITIES.index(severity) + rungs
    return SEVERITIES[i] if 0 <= i < len(SEVERITIES) else None


def _tags_match(key: str, tags: Sequence[str]) -> bool:
    return any(t == key or t.startswith(key + ".") for t in tags)


def receiver_amount(rules: Any, data: dict[str, Any], base: int, tags: Sequence[str], *, no_reduction: bool,
                    reduction: int | None) -> tuple[int, dict[str, Any]]:  # rule: 07.2.2
    """The receiver's side (00.10.5): reduction by harm tag capped at 4, then at most one ×½ and one ×2, clamped
    at 0, rounded down. `data` is the target's entity data (`reduction`: int for worn armor against
    harm.physical, or {harm tag: n}; `resist` / `vulnerable`: harm tags)."""
    cap = int(rules.harm["reduction_cap"])
    red = 0
    if not no_reduction:
        if reduction is not None:
            red = reduction
        else:
            r = data.get("reduction", 0)
            if isinstance(r, dict):
                red = sum(int(n) for k, n in r.items() if _tags_match(str(k), tags))
            elif not tags or _tags_match("harm.physical", tags):
                red = int(r or 0)
        red = max(0, min(cap, red))
    half = any(_tags_match(str(k), tags) for k in data.get("resist") or ())
    double = any(_tags_match(str(k), tags) for k in data.get("vulnerable") or ())
    x = max(0, base - red)
    if half:
        x = x // 2
    if double:
        x = x * 2
    return x, {"base": base, "reduction": red, "half": half, "double": double, "final": x}


# ------------------------------------------------------------------------------------------- the ladder


def _state(w: Writes, eid: str, hs: str, rule_id: str) -> None:
    w.fact(eid, "harm_state", hs, rule_id=rule_id)


def _cond(ctx: Any, w: Writes, eid: str, cond: str, source: dict[str, Any], rule_id: str) -> None:
    w.extend(apply_condition(ctx.state, w.mint, ctx.rules, eid, cond, source=source, rule_id=rule_id).events)


def _dread(w: Writes, eid: str, n: int, rule_id: str) -> None:
    """Dread is M2 (07.11): applied when the character has a `dread` quantity, else logged as coarse."""
    if w.quantity(eid, "dread") is not None:
        w.add_quantity(eid, "dread", n, reason=f"dread +{n} ({rule_id})", rule_id=rule_id)
    else:
        w.coarse(rule_id, f"dread +{n} not tracked before M2", entity=eid)


def go_down(ctx: Any, w: Writes, eid: str, *, cause: str, source: dict[str, Any]) -> None:  # rule: 07.2.9
    """Down: `down`, defeated {manner: down}, unconscious and prone; Vitality 0, Staggered; the ladder frozen."""
    w.set_quantity(eid, VITALITY, 0, reason=f"down: {cause}", rule_id="07.2.9")
    _state(w, eid, STAGGERED, "07.2.9")
    w.fact(eid, "down", True, rule_id="07.2.9")
    w.fact(eid, "defeated", {"manner": "down"}, rule_id="07.2.9")
    w.fact(eid, "setback.defeated", {"cause": cause}, rule_id="07.2.9")
    _cond(ctx, w, eid, "cond.unconscious", source, "07.2.9")
    _cond(ctx, w, eid, "cond.prone", source, "07.2.9")


def _enter_dying(ctx: Any, w: Writes, eid: str, res: HarmResult, source: dict[str, Any], key1: str | None) -> None:
    step = min(3, 1 + brink(w, eid))  # rule: 07.2.6
    _state(w, eid, DYING, "07.2.6")
    w.fact(eid, "dying_step", step, rule_id="07.2.6")
    w.fact(eid, "lethal_key", key1, rule_id="07.3.1")  # Key 1 on record for this fall
    w.fact(eid, "setback.dying_entered", {"step": step}, rule_id="07.2.6")
    _cond(ctx, w, eid, "cond.prone", source, "07.2.7")
    _dread(w, eid, 1, "07.11.2")
    res.transition = "dying"
    res.hooks.append("on_dying")
    res.triggers.append("trg.exits")


def _coarse_wound(ctx: Any, w: Writes, eid: str, amount: int, periodic: bool, res: HarmResult) -> int:
    """07.2.4: the wound's severity and load U(severity); returns the load added."""
    sev = bucket(amount)
    units = int(ctx.rules.severity_units()[sev])
    res.wound = {"severity": sev, "load": units, "record": None}
    if not periodic:  # rule: PR-07-2
        # coarse: PR-07-2 — no injuries.yaml record before M2 (no site, status or max-Vitality penalty).
        w.coarse("PR-07-2", "wound load added, no wound record (M2)", entity=eid, severity=sev, amount=amount)
    return units


def apply_harm(ctx: Any, target: str, *, severity: str | None = None, dealt: int | None = None,
               harm_tags: Sequence[str] = (), source: str | None = None, frame_id: str | None = None,
               lethal: bool = False, mode: str = "lethal", no_reduction: bool = False, periodic: bool = False,
               reduction: int | None = None, writes: Writes | None = None) -> HarmResult:  # rule: PR-07-1
    # rule: 07.1.5
    # rule: 07.2.11
    # coarse: 07.2.5
    """PR-07-1. `lethal` is the caller's Key 1 claim for this event; it is kept only if 07.3.6 tests 1 and 3 hold
    (else refused and logged). `mode` is the attacker's intent at 0 Vitality (06.4.8)."""
    st = ctx.state
    w = writes or Writes.of(ctx, source=frame_id or "apply_harm")
    start = len(w.events)
    res = HarmResult(target=target)
    if target not in st.entities:
        raise ValueError(f"unknown target {target}")
    src = {"entity": source, "frame_id": frame_id, "effect_id": None}
    # 1. coarse: PR-07-1 step 1 — prevent/redirect subscribers are effect instances (M2); none exist in M1.
    # 2. lethal test (07.3.6 tests 1 and 3; test 2 is the caller's frame)
    if lethal:
        if not on_ladder(st, target):
            lethal = False  # others need no key (07.3.6 test 3)
        elif lethal_mod.effective(st, source) is None:
            lethal = False
            res.lethal_refused = "1: no effective lethal context for the source"  # rule: 07.3.6
            w.log("lethal_refused", {"target": target, "source": source, "frame_id": frame_id,
                                     "missing": res.lethal_refused}, rule_id="07.3.6")
    res.lethal = lethal
    # 3. amount
    if dealt is None:
        if severity is None:
            raise ValueError("apply_harm needs a severity or a dealt amount")
        base = severity_harm(ctx.rules, severity)
    else:
        base = dealt
    amount, res.breakdown = receiver_amount(ctx.rules, st.entities[target].data, base, harm_tags,
                                            no_reduction=no_reduction, reduction=reduction)
    res.amount = amount
    record = {"target": target, "source": source, "frame_id": frame_id, "severity": severity, "amount": amount,
              "breakdown": res.breakdown, "lethal": lethal, "mode": mode, "periodic": periodic,
              "harm_tags": list(harm_tags)}
    # 4. zero
    if amount == 0:
        w.log("harm", {**record, "transition": None}, rule_id="PR-07-1")
        res.events = w.events[start:]
        return res
    v = w.quantity(target, VITALITY)
    if v is None:
        raise ValueError(f"{target} has no Vitality")
    mx = v.max if v.max is not None else v.current
    reason = f"harm {amount} from {source or 'unknown'}"
    if not on_ladder(st, target):
        _others(ctx, w, target, v.current, amount, mode, reason, frame_id, src, res)  # 5.
    else:
        hs = harm_state(w, target)
        if hs == DEAD or is_down(w, target):  # 9. Down or dead: record and discard
            res.transition = None
        elif hs == ACTIVE and v.current > 0:  # 6. Active
            new = max(0, v.current - amount)
            w.set_quantity(target, VITALITY, new, reason=reason, rule_id="07.2.3", frame_id=frame_id)
            res.hooks.append("on_harm_taken")
            if v.current * 2 > mx >= new * 2:
                res.hooks.append("on_vitality_threshold:half")  # rule: 07.1.4
            if new == 0:  # rule: 07.2.3
                res.breakdown["discarded"] = amount - v.current
                res.hooks += ["on_vitality_threshold:zero", "morale:-2"]
                if mode == "nonlethal":
                    go_down(ctx, w, target, cause="a nonlethal blow at 0 Vitality (06.4.8)", source=src)
                    res.transition = "down"
                else:
                    _state(w, target, STAGGERED, "07.2.3")
                    res.transition = "staggered"
                    res.triggers.append("trg.exits")
        elif hs in (ACTIVE, STAGGERED):  # 7. Staggered
            res.hooks.append("on_harm_taken")
            load = wound_load(w, target) + _coarse_wound(ctx, w, target, amount, periodic, res)
            w.fact(target, "wound_load", load, rule_id="07.2.6")
            res.load = load
            _state(w, target, STAGGERED, "07.2.6")
            if load >= LOAD_LIMIT:  # rule: 07.2.6
                if lethal:
                    c = lethal_mod.effective(st, source)
                    _enter_dying(ctx, w, target, res, src, c["id"] if c else None)
                else:
                    go_down(ctx, w, target, cause="wound load 3 under a non-lethal event", source=src)
                    res.transition = "down"
        elif hs == DYING:  # 8. Dying
            if lethal:  # rule: 07.2.7
                _coarse_wound(ctx, w, target, amount, periodic, res)
                res.load = wound_load(w, target)
                step = dying_step(w, target) + (2 if bucket(amount) in ("S4", "S5") else 1)
                if step >= 4:  # rule: 07.5.1
                    w.fact(target, "dying_step", 3, rule_id="07.5.1")
                    res.threshold = True
                    res.transition = "threshold"
                    res.breakdown["held_at_threshold"] = True
                else:
                    w.fact(target, "dying_step", step, rule_id="07.2.7")
                    res.transition = "dying_step"
            # non-lethal harm to a Dying character: recorded and discarded (07.2.11)
    w.log("harm", {**record, "transition": res.transition}, rule_id="PR-07-1")
    res.obligations = obligations(ctx, w, target, res)
    res.events = w.events[start:]
    return res


def _others(ctx: Any, w: Writes, target: str, current: int, amount: int, mode: str, reason: str,
            frame_id: str | None, src: dict[str, Any], res: HarmResult) -> None:  # rule: 07.2.10
    """PR-07-1 step 5: an adversary or NPC. At 0: dead (lethal walk-on), Dying until scene_end (lethal recurring
    or principal), or unconscious for the scene (nonlethal)."""
    if current <= 0:
        return
    new = max(0, current - amount)
    w.set_quantity(target, VITALITY, new, reason=reason, rule_id="07.2.10", frame_id=frame_id)
    res.hooks.append("on_harm_taken")
    if new > 0:
        return
    depth = str(ctx.state.entities[target].data.get("depth", "walk-on"))
    if mode == "nonlethal":
        _cond(ctx, w, target, "cond.unconscious", src, "07.2.10")
        w.fact(target, "defeated", {"manner": "unconscious"}, rule_id="07.2.10")
        res.transition = "unconscious"
    elif depth in ("recurring", "principal"):
        _state(w, target, DYING, "07.2.10")
        w.fact(target, "defeated", {"manner": "dying"}, rule_id="07.2.10")
        res.transition = "defeated"
    else:
        _state(w, target, DEAD, "07.2.10")
        w.fact(target, "defeated", {"manner": "dead"}, rule_id="07.2.10")
        res.transition = "dead"
    lethal_mod.end_contexts(w, reason="source defeated", source=target)


# ------------------------------------------------------------------------------------------- what narration owes


def status_block(rules: Any, r: Any, eid: str, exits: str | None = None) -> str | None:  # rule: 07.3.7
    """The `[STATUS]` exits card for a Staggered or Dying PC (T-07-7). `exits`: the Yield/Retreat words computed
    by engine/harm/exits.py; without them the card says to ask (asking is free, 07.4)."""
    hs = harm_state(r, eid)
    ex = exits or "Yield — ask what it would mean · Retreat — ask what it would cost"
    if hs == STAGGERED and not is_down(r, eid):
        fall = "fall to Dying" if any(lethal_mod.effective(r.state, s) for s in lethal_mod.scene_sources(r.state)) \
            else "go Down"
        return (f"[STATUS] STAGGERED — blows now wound you; at wound load 3 you {fall}. "
                f"Load {wound_load(r, eid)}/3.\n         Exits: {ex} · or fight on.")
    if hs == DYING:
        step = dying_step(r, eid)
        dc = dc_of(rules, ("easy", "moderate", "hard")[max(1, step) - 1])
        mod = endure_modifier(r.state, eid)
        dist = distribution(mod, dc)
        need = max(1, min(20, dc - mod))
        odds = pct(dist["success"] + dist["critical_success"])
        return (f"[STATUS] DYING {step} of 3 — one action a turn; a check each turn (you need {need} or better; "
                f"{odds}%).\n         A blow adds a step. Past 3 you choose from the last-chance menu. "
                f"Exits: {ex.split(' · ')[0]}.")
    return None


def obligations(ctx: Any, r: Any, eid: str, res: HarmResult) -> list[str]:  # rule: PR-07-1
    out: list[str] = []
    word = descriptor(r, eid)
    out.append(f"descriptor: {word} ({', '.join(descriptor_words(ctx.rules, word))})")
    if res.wound is not None:
        out.append(f"wound: {res.wound['severity']} (load {res.load}/3)")
    if "trg.exits" in res.triggers:
        block = status_block(ctx.rules, r, eid)
        if block:
            out.append(block)
    if res.threshold:
        out.append("the Threshold: the moment holds; nothing may say or suggest death (07.5.1)")
    return out


# ------------------------------------------------------------------------------------------- back up the ladder


def stabilize(ctx: Any, target: str, *, brink_wound: bool = True, rule_id: str = "07.2.8",
              writes: Writes | None = None) -> list[Event]:  # rule: 07.2.8
    """Stabilized: step 0, Staggered (or active if Vitality is above 0), conscious and prone, `on_stabilize`, one
    brink wound unless a fate reprieve (07.5.8). Kept as the `brink` count in M1."""
    w = writes or Writes.of(ctx, source="stabilize")
    start = len(w.events)
    v = w.quantity(target, VITALITY)
    w.fact(target, "dying_step", 0, rule_id=rule_id)
    _state(w, target, ACTIVE if v is not None and v.current > 0 else STAGGERED, rule_id)
    if brink_wound:
        w.fact(target, "brink", brink(w, target) + 1, rule_id="07.2.8")
        # coarse: 07.2.8 — the brink wound's maximum-Vitality penalty (-2) waits for h.07.vitality_max (M3).
        w.coarse("07.2.8", "brink wound counted; its max-Vitality penalty is not applied before M3", entity=target)
    return w.events[start:]


def restore_vitality(ctx: Any, target: str, *, amount: int | None = None, to: int | None = None, reason: str,
                     rule_id: str, brink_wound: bool = True, frame_id: str | None = None,
                     writes: Writes | None = None) -> list[Event]:  # rule: 07.2.7
    """Raise Vitality by `amount` or to `to` (never lowering), clamped to the maximum. A Dying character is
    stabilized first (07.2.7); a Staggered one above 0 is active again, its wound load kept (07.1.3)."""
    w = writes or Writes.of(ctx, source="restore_vitality")
    start = len(w.events)
    v = w.quantity(target, VITALITY)
    if v is None:
        raise ValueError(f"{target} has no Vitality")
    hs = harm_state(w, target)
    if hs == DEAD:
        return []
    if hs == DYING:
        stabilize(ctx, target, brink_wound=brink_wound, writes=w)
    new = v.current + amount if amount is not None else max(v.current, to if to is not None else v.current)
    w.set_quantity(target, VITALITY, new, reason=reason, rule_id=rule_id, frame_id=frame_id)
    after = w.quantity(target, VITALITY)
    if after is not None and after.current > 0 and harm_state(w, target) == STAGGERED and not is_down(w, target):
        _state(w, target, ACTIVE, "07.1.3")
    return w.events[start:]


@dataclass
class DyingCheck:
    events: list[Event]
    natural: int
    modifier: int
    dc: int
    degree: str
    margin: int
    result: str  # stabilized | step_down | holds | step_up | threshold
    step: int
    threshold: bool = False


def dying_check(ctx: Any, target: str, *, natural: int | None = None,
                writes: Writes | None = None) -> DyingCheck:  # rule: 07.2.7
    """The dying check at the character's turn end: Endure with Endurance against the step's stabilize DC (10 /
    15 / 20). The handler `h.07.dying_check` is M2; Milestone 1's coarse fights call this at the PC's turn end."""
    w = writes or Writes.of(ctx, source="h.07.dying_check")
    start = len(w.events)
    step = dying_step(w, target)
    if harm_state(w, target) != DYING or step < 1:
        raise ValueError(f"{target} is not Dying")
    dc = dc_of(ctx.rules, ("easy", "moderate", "hard")[step - 1])
    mod = endure_modifier(ctx.state, target)
    nat = roll_d20(ctx, f"dying check {target} (step {step})", natural)
    deg, margin = degree(nat, mod, dc)
    out = DyingCheck([], nat, mod, dc, deg, margin, "holds", step)
    if deg == "critical_success" or (deg == "success" and step == 1):
        stabilize(ctx, target, writes=w)
        out.result, out.step = "stabilized", 0
    elif deg == "success":
        out.result, out.step = "step_down", step - 1
    elif deg == "failure" and margin >= -3:
        out.result = "holds"
    else:
        up = step + (2 if deg == "critical_failure" else 1)
        if up >= 4:
            out.result, out.step, out.threshold = "threshold", 3, True
        else:
            out.result, out.step = "step_up", up
    if out.result in ("step_down", "step_up", "threshold"):
        w.fact(target, "dying_step", out.step, rule_id="07.2.7")
    w.log("dying_check", {"target": target, "natural": nat, "modifier": mod, "dc": dc, "degree": deg,
                          "result": out.result}, rule_id="07.2.7")
    out.events = w.events[start:]
    return out


def heal(ctx: Any, target: str, amount: int, *, source: str, writes: Writes | None = None) -> list[Event]:
    """A Vitality-restoring effect (magic, or a mundane ability such as ab.field_surgeon): at most two per being
    between its long rests (`healings_since_long_rest`, reset by h.05.rest_recharge); stabilizes the Dying at once;
    never clears the wound load or heals a wound (07.8.9). Over the cap it restores nothing."""  # rule: 07.8.9
    w = writes or Writes.of(ctx, source=source)
    start = len(w.events)
    key = f"{target}.healings_since_long_rest"
    used = int(w.meta_value(key, 0) or 0)
    if used >= 2:
        w.log("healing_capped", {"target": target, "source": source}, rule_id="07.8.9")
        return w.events[start:]
    restore_vitality(ctx, target, amount=amount, reason=f"healing from {source}", rule_id="07.8.9", writes=w)
    w.meta(key, used + 1, rule_id="07.8.9")
    return w.events[start:]


def harm_hook(ctx: Any, source: str | None = None) -> Any:  # rule: PR-07-1
    """The `harm_hook` engine/resolve's `apply_cost` takes for `cost.harm`: `hook(target, severity, *, lethal,
    harm_tags, frame_id) -> list[Event]`, through apply_harm (lethal is re-tested there, 07.3.6)."""
    def hook(target: str, severity: str, *, lethal: bool = False, harm_tags: Sequence[str] = (),
             frame_id: str | None = None) -> list[Event]:
        return apply_harm(ctx, target, severity=severity, harm_tags=harm_tags, source=source, frame_id=frame_id,
                          lethal=lethal).events
    return hook
