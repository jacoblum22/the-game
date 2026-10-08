"""The two keys' first half: lethal contexts, the lethal-warning trigger, the warning block and the lethal frame
(07.3; PR-07-4; SC-006).

    for trig in warning_needed(state, rules, "pc.wren"):         # 07.3.3 rows true, no context yet
        text = warning_block(rules, trig, source_name="the barrow-wight", fate=1, yield_text=..., retreat_text=...)
        tx.add_all(record_warning(ctx, trig, sign="frost creeps across the grave-goods"))   # PR-07-4 step 4
    verdict = lethal_scan(state, frame)        # 07.3.6: is this frame lethal? (never auto-committed if so)

A lethal context is the fact `<source>.lethal_context` (a non-entity source: `world.lethal_context:<source>`), value
`{id, source, pc, cause, sign, warned_at, effective_from, shown, ends, scene_id, active}`. It is effective from
the beat after the warning (the player's next declaration, 07.3.5) until scene_end or the source's defeat.

Source data the rows read (an adversary/NPC/object entity's `data`): `hostile` (default true for adversaries),
`lethal_context` (bool, 09), `defeat_disposition`, `threat_advisory` ("lethal" | "hard" | ...),
`attacks` ([{name, severity}]) or `max_severity`, `windup` (the attack named), `hazard`
({severity, lethal_context}). Clocks: `ClockRecord.lethal` at the imminent stage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from engine import ids
from engine.harm.ctx import Writes
from engine.harm.state import LADDER_KINDS, defeated_manner
from engine.store.clocks import stage
from engine.store.events import WORLD, Event
from engine.store.projection import WorldState

CAUSES = ("advisory", "archetype", "disposition", "severity", "windup", "clock", "hazard", "affliction",
          "deprivation", "chosen")  # harm.yaml#lethal_warning.trigger, in table order
HEAVY = ("S4", "S5")
SEV_NAMES = {"S4": "Grievous", "S5": "Catastrophic"}


@dataclass
class LethalTrigger:
    """`trg.lethal_warning {source, cause}` for one PC (07.3.3)."""

    pc: str
    source: str
    cause: str
    detail: dict[str, Any] = field(default_factory=dict)  # severity, attack, affliction named in the cause line


@dataclass
class LethalVerdict:
    lethal: bool
    missing: str | None = None  # the 07.3.6 test that failed
    context_id: str | None = None
    offer_line: str | None = None  # 12.15.2: THIS CAN KILL YOU — <source> (warned <when>)


def key(state: WorldState, source: str) -> tuple[str, str]:
    """Where a source's context lives: `<source>.lethal_context` for an entity (engine/resolve reads that
    predicate), else `world.lethal_context:<source>` (a hazard or clock id)."""
    return (source, "lethal_context") if source in state.entities else (WORLD, f"lethal_context:{source}")


def scene_id(state: WorldState) -> str | None:
    return state.scene.scene_id if state.scene is not None else None


def context(state: WorldState | Writes, source: str) -> dict[str, Any] | None:  # rule: 07.3.2
    """The source's lethal context in the current scene, if one is recorded and not ended."""
    st = state.state if isinstance(state, Writes) else state
    v = state.fact_value(*key(st, source))
    if not isinstance(v, dict) or not v.get("active") or v.get("scene_id") != scene_id(st):
        return None
    return v


def effective(state: WorldState, source: str | None) -> dict[str, Any] | None:  # rule: 07.3.5
    """The context if it has taken effect: shown, the player has declared since, the source not defeated."""
    if not source:
        return None
    c = context(state, source)
    if c is None or not c.get("shown"):
        return None
    if state.time.now.beat < int(c.get("effective_from", 0)):
        return None
    if source in state.entities and defeated_manner(state, source):
        return None
    return c


# ------------------------------------------------------------------------------------------- the trigger rows


def _max_severity(data: dict[str, Any]) -> str | None:
    sevs = [str(a.get("severity")) for a in data.get("attacks") or () if isinstance(a, dict)]
    if data.get("max_severity"):
        sevs.append(str(data["max_severity"]))
    sevs = [s for s in sevs if s in ("S1", "S2", "S3", "S4", "S5")]
    return max(sevs) if sevs else None


def _fight_severity(state: WorldState, eid: str) -> str | None:  # rule: 06.2.1
    """A foe of the running fight: the heaviest harm its line lists (recorded by `conflict.start`), else None."""
    from engine.resolve.conflict import record

    rec = record(state)
    return str((rec.get("severity") or {}).get(eid) or "S1") if eid in rec.get("foes", ()) else None


def _rows_for_entity(state: WorldState, pc: str, eid: str) -> LethalTrigger | None:  # rule: 07.3.3
    e = state.entities[eid]
    d = e.data
    if e.exists != "exists" or defeated_manner(state, eid):
        return None
    fight = _fight_severity(state, eid)  # a person fighting the PC is hostile, whatever its record says
    hostile = bool(d.get("hostile", e.kind == "adversary")) or fight is not None
    hazard = d.get("hazard") if isinstance(d.get("hazard"), dict) else None
    sev = _max_severity(d) or fight
    if hostile and d.get("threat_advisory") == "lethal":
        return LethalTrigger(pc, eid, "advisory")
    if hostile and d.get("lethal_context"):
        return LethalTrigger(pc, eid, "archetype")
    if hostile and d.get("defeat_disposition") == "kill":
        return LethalTrigger(pc, eid, "disposition")
    hsev = str(hazard.get("severity")) if hazard else None
    if (hostile and sev in HEAVY) or hsev in HEAVY:
        return LethalTrigger(pc, eid, "severity", {"severity": sev if sev in HEAVY else hsev})
    if hostile and d.get("windup"):
        return LethalTrigger(pc, eid, "windup", {"attack": str(d["windup"])})
    if hazard and hazard.get("lethal_context"):
        return LethalTrigger(pc, eid, "hazard", {"severity": hsev or "S4"})
    return None


def scene_sources(state: WorldState) -> list[str]:
    """Entities the PC perceives in the framed scene: the scene's cast, else every adversary that exists."""
    if state.scene is not None and state.scene.cast_present:
        return [i for i in state.scene.cast_present if i in state.entities]
    return [i for i, e in state.entities.items() if e.kind == "adversary"]


def lethal_rows(state: WorldState, pc: str, *, sources: list[str] | None = None) -> list[LethalTrigger]:
    """07.3.3 against tracked state: one trigger per source, with the first true cause (WE-07-1)."""  # rule: 07.3.3
    out: list[LethalTrigger] = []
    for eid in sources if sources is not None else scene_sources(state):
        if eid == pc or eid not in state.entities:
            continue
        t = _rows_for_entity(state, pc, eid)
        if t is not None:
            out.append(t)
    for c in state.clocks.values():  # the clock row (PR-00-3 step 3)
        if c.status == "active" and c.lethal and c.visibility != "public" \
                and stage(c.filled, c.segments) == "imminent":
            out.append(LethalTrigger(pc, c.id, "clock"))
    return out


def warning_needed(state: WorldState, pc: str, *, sources: list[str] | None = None) -> list[LethalTrigger]:
    """Rows true for a source with no lethal context in this scene: the warning is due this turn (PR-07-4)."""
    return [t for t in lethal_rows(state, pc, sources=sources) if context(state, t.source) is None]  # rule: PR-07-4


def chosen_trigger(pc: str, source: str) -> LethalTrigger:  # rule: 07.5.13
    """A voluntary last stand raises the `chosen` warning for the player to confirm out of fiction."""
    return LethalTrigger(pc, source, "chosen")


def danger_notice(state: WorldState, pc: str, source: str, disposition_words: str) -> str | None:  # rule: 07.3.8
    """`threat_advisory` hard and no row true: one plain line; it writes no context."""
    e = state.entities.get(source)
    if e is None or e.data.get("threat_advisory") != "hard" or _rows_for_entity(state, pc, source):
        return None
    return f"[WARNING] A hard fight — you may well lose this. Losing here means {disposition_words}."


# ------------------------------------------------------------------------------------------- the warning


def cause_line(rules: Any, trig: LethalTrigger) -> str:  # rule: 07.3.4
    line = str(rules.harm["lethal_warning"]["cause_lines"][trig.cause])
    sev = SEV_NAMES.get(str(trig.detail.get("severity")), "Grievous")
    return (line.replace("<Grievous | Catastrophic>", sev)
            .replace("<the attack named>", str(trig.detail.get("attack", "a heavy blow")))
            .replace("<affliction>", str(trig.detail.get("affliction", "it"))))


def warning_block(rules: Any, trig: LethalTrigger, *, source_name: str, fate: int, yield_text: str,
                  retreat_text: str) -> str:  # rule: 07.3.4
    """The `[WARNING]` block (T-07-7): never softened, never omitted."""
    return (f"[WARNING] THIS CAN KILL YOU — {source_name}. {cause_line(rules, trig)}\n"
            f"          From your next action on, falling here can mean Dying. Fate: {fate}.\n"
            f"          Exits now: Yield — {yield_text} · Retreat — {retreat_text}")


def context_id(state: WorldState, source: str) -> str:
    return f"lc.{ids.slug(scene_id(state) or 'none')}.{ids.slug(source)}"


def record_warning(ctx: Any, trig: LethalTrigger, *, sign: str, ends: str = "scene_end",
                   writes: Writes | None = None) -> list[Event]:  # rule: PR-07-4
    """PR-07-4 step 4, once the sign and the block are in this turn's delivery: the context, shown, effective
    from the beat after the player's next declaration (07.3.5)."""
    w = writes or Writes.of(ctx, source="h.07.lethal_scan")
    start = len(w.events)
    st: WorldState = ctx.state
    now = st.time.now
    w.fact(*key(st, trig.source), {
        "id": context_id(st, trig.source), "source": trig.source, "pc": trig.pc, "cause": trig.cause,
        "sign": sign, "warned_at": now.model_dump(), "effective_from": now.beat + 1, "shown": True,
        "ends": ends, "scene_id": scene_id(st), "active": True}, rule_id="07.3.2", visibility="shown")
    pending = [t for t in (w.meta_value("trg.lethal_warning") or []) if t.get("source") != trig.source]
    if pending != (w.meta_value("trg.lethal_warning") or []):
        w.meta("trg.lethal_warning", pending, rule_id="PR-07-4")
    return w.events[start:]


def end_contexts(w: Writes, *, reason: str, source: str | None = None) -> None:  # rule: 07.3.5
    """End the scene's contexts (h.07.load_clear at scene_end), or one source's (defeated, gone, cured)."""
    for f in list(w.state.facts.values()):
        if not f.predicate.startswith("lethal_context"):
            continue
        v = w.fact_value(f.subject, f.predicate)
        if not isinstance(v, dict) or not v.get("active"):
            continue
        if source is not None and v.get("source") != source:
            continue
        # ended: the value becomes None (falsy for readers of `lethal_context`); the history keeps the record
        w.fact(f.subject, f.predicate, None, rule_id="07.3.5")


def active_triggers(state: WorldState) -> list[dict[str, Any]]:
    """`get_active_triggers`' lethal part: warnings raised and not yet delivered (07.3.3: until `shown`)."""
    return [t for t in state.meta.get("trg.lethal_warning") or [] if context(state, str(t.get("source"))) is None]


# ------------------------------------------------------------------------------------------- the lethal frame


def lethal_scan(state: WorldState, frame: dict[str, Any]) -> LethalVerdict:  # rule: 07.3.6
    """Is this frame lethal? All three tests of 07.3.6. `frame`: {kind: pc|adversary|hazard|affliction,
    source, target, stakes, lethal (the DM's flag on a PC frame), mode (an adversary's harm mode),
    entry_lethal (a hazard or affliction stage)}."""
    target = str(frame.get("target") or "")
    if state.entities.get(target) is None or state.entities[target].kind not in LADDER_KINDS:
        return LethalVerdict(False, "3: the target is not a PC or companion")
    source = str(frame.get("source") or "")
    c = effective(state, source)
    if c is None:
        return LethalVerdict(False, "1: no effective lethal context for the source")
    kind = frame.get("kind", "pc")
    if kind == "pc":
        ok = frame.get("stakes") == "dire" and bool(frame.get("lethal"))
        missing = "2: a PC frame must be Dire and flagged lethal"
    elif kind == "adversary":
        ok = frame.get("mode", "lethal") == "lethal"
        missing = "2: the adversary's harm mode is not lethal"
    else:
        ok = bool(frame.get("entry_lethal", frame.get("lethal")))
        missing = "2: the exposure's entry is not lethal"
    if not ok:
        return LethalVerdict(False, missing, c["id"])
    return LethalVerdict(True, None, c["id"], offer_line(state, c))


def offer_line(state: WorldState, c: dict[str, Any]) -> str:  # rule: 07.3.4
    """12.15.2's OFFER line for a lethal frame."""
    e = state.entities.get(str(c.get("source")))
    name = e.name if e is not None else str(c.get("source"))
    return f"THIS CAN KILL YOU — {name} (warned this scene, beat {c.get('warned_at', {}).get('beat', '?')})"


def may_auto_commit(state: WorldState, frame: dict[str, Any]) -> bool:  # rule: 07.3.6
    """A lethal frame is never auto-committed: it goes to the OFFER (07.3.4, 00.13.2; SC-006)."""
    return not lethal_scan(state, frame).lethal
