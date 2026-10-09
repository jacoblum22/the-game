"""PR-12-11 the Fixer: a player's report investigated with read-only tools, then corrections proposed (spec 022).

    out = investigate(ctx, "the coin for the round was never taken")   # the bounded tool loop (3-6 tool calls)
    out.complaints   # [{believes, category, turn, verdict, found, proposals: [{kind, ...}]}], all from one snapshot
    out.calls        # [(tool, arg, output)]: what the Fixer looked at (the evidence a proposal may cite)
    tool(ctx, "turn", "turn.14")                                      # one read-only tool, as text

The Fixer role (12.2.4; `pacing.yaml#feedback.investigate`) reads the report with the calendar, the PC's sheet, the
people in view and the last turns, then calls the tools: a turn's record (its frames, rolls, cited facts and every
write, reverted ones marked), an entity's state with each fact's provenance, a transcript search, a frame recomputed
from the rules, the PC's coin and inventory ledger, and what a character said against the record. Tools never write
and never show sealed content (INV-10). It then proposes corrections from PR-12-11's list; engine/dm/dispute.py
validates and applies them (code owns the spine; the model owns the reading and the judgment, VIII.1).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from engine import ids
from engine.dm.schemas import STR, STRS, Schema, arr, enum, obj

TOOLS = ("turn", "entity", "search", "recompute", "ledger", "said")
PROPOSALS = ("set_fact", "remove_fact", "restore", "refund", "deduct", "rerender", "take_back", "correct_testimony",
             "explain")
CATEGORIES = ("remembered_wrong", "rule_wrong", "contradiction", "misread", "ruling_question", "other")  # 12.3.6 item 2
VERDICTS = ("player_right", "partly", "record_stands", "unclear")
PLAYER_FACING = ("shown", "available")
MAX_STEPS, MIN_STEPS = 6, 3  # pacing.yaml#feedback.investigate.steps (read from the rules when given)
PER_STEP = 3  # tool calls one answer may ask for
OUT_CHARS = 2400  # one tool output, at most
SKIP_PREDICATES = ("trg.", "log.", "closed.", "lethal", "dc.")


@dataclass
class Investigation:
    complaints: list[dict[str, Any]] = field(default_factory=list)
    calls: list[tuple[str, str, str]] = field(default_factory=list)  # (tool, arg, output)

    @property
    def seen(self) -> str:
        return "\n".join(o for _, _, o in self.calls)


# ------------------------------------------------------------------------------------------- shared reads


def _flat(s: Any, n: int | None = None) -> str:
    t = " ".join(str(s).split())
    return t if n is None or len(t) <= n else t[:n] + "…"


def turn_no(turn_id: str | None) -> int:
    p = ids.parse_counter_id(turn_id) if turn_id else None
    return p[1] if p else 0


def pc_of(state: Any) -> str | None:
    return next((eid for eid, e in state.entities.items() if e.kind == "pc" and e.exists == "exists"), None)


def name(state: Any, eid: str) -> str:
    from engine.store.views import display_name

    return display_name(state, eid) if eid in state.entities else eid


def visible(state: Any, f: Any) -> bool:
    """A fact the player may be shown: player-facing, its fact and subject unsealed (INV-10)."""
    return (f.visibility in PLAYER_FACING and f.id not in state.seals and f.subject not in state.seals
            and not f.predicate.startswith(SKIP_PREDICATES))


def _turn_of(store: Any, seq: int) -> str:
    ev = store.event(seq)
    return str(ev.turn_id) if ev is not None and ev.turn_id else "setup"


def fact_line(store: Any, state: Any, f: Any) -> str:
    return (f"{f.id} {name(state, f.subject)} {f.predicate} = {_flat(json.dumps(f.value, ensure_ascii=False), 160)} "
            f"(source {f.source}, {_turn_of(store, f.valid_from_seq)})")


def play_turns(store: Any, before: str | None) -> list[Any]:
    """Every play turn before `before`, newest first (a dispute's own turn is not the transcript being checked)."""
    from engine.dm.dispute import _turns

    return _turns(store, before)


def resolve(state: Any, arg: str) -> str | None:
    """An entity id from an id, a name as the PC knows it, or "me"/"pc"; sealed entities never."""
    a = arg.strip().strip('"').lower()
    if a in ("", "me", "pc", "you", "my character", "i"):
        return pc_of(state)
    if arg.strip() in state.entities and arg.strip() not in state.seals:
        return arg.strip()
    hits = [eid for eid, e in state.entities.items() if eid not in state.seals and a and (
        a == name(state, eid).lower() or a == e.name.lower() or a in name(state, eid).lower())]
    return hits[0] if hits else None


def sheet(state: Any, rules: Any, eid: str | None) -> dict[str, str]:
    """The values a player sees about `eid`: shown quantities, the harm word, conditions, what it holds."""
    from engine.harm.state import descriptor
    from engine.resolve.change import things_held

    if eid is None or eid not in state.entities:
        return {}
    out: dict[str, str] = {}
    for k, q in (state.quantities.get(eid) or {}).items():
        if q.visibility in PLAYER_FACING:
            out[k.replace("_", " ").capitalize() if k == "vitality" else k.replace("_", " ")] = \
                f"{q.current}" + (f"/{q.max}" if k == "vitality" and q.max is not None else "")
    try:
        out["state"] = descriptor(state, eid)
    except Exception:  # noqa: BLE001 - a thing with no harm ladder has no harm word
        pass
    conds = sorted(f"{_cond_name(rules, c.condition_id)}" + (f" (held by {name(state, str(c.source['entity']))})"
                   if (c.source or {}).get("entity") and c.condition_id.startswith(("cond.grab", "cond.restr",
                                                                                    "cond.pinn")) else "")
                   for c in state.conditions_on(eid))
    out["conditions"] = ", ".join(conds) or "none"
    out["holding"] = ", ".join(name(state, i) for i in things_held(state, [eid])) or "nothing"
    return out


def _cond_name(rules: Any, cid: str) -> str:
    try:
        return str(rules.condition(cid).get("name") or cid).lower()
    except Exception:  # noqa: BLE001
        return cid.removeprefix("cond.")


def sheet_line(state: Any, rules: Any, eid: str | None) -> str:
    return " · ".join(f"{k} {v}" for k, v in sheet(state, rules, eid).items())


# ------------------------------------------------------------------------------------------- the tools


def _event_line(store: Any, state: Any, e: Any) -> str | None:  # noqa: PLR0911 - one line per event kind
    p: Any = e.payload
    t = e.type
    mark = " (REVERTED)" if e.seq in state.reverted else ""
    if t == "fact_set":
        f = state.facts.get(p.fact_id) or state.superseded_facts.get(p.fact_id)
        if p.visibility not in PLAYER_FACING or p.subject in state.seals or p.fact_id in state.seals \
                or p.predicate.startswith(SKIP_PREDICATES):
            return None
        value = "(removed)" if p.value is None else _flat(json.dumps(p.value, ensure_ascii=False), 160)
        src = getattr(f, "source", None) or e.source
        return f"  {e.seq} fact {p.fact_id}: {name(state, p.subject)} {p.predicate} = {value} (source {src}){mark}"
    if t == "quantity_changed":
        q = (state.quantities.get(p.entity) or {}).get(p.quantity)
        if q is not None and q.visibility not in PLAYER_FACING and p.entity != pc_of(state):
            return f"  {e.seq} {name(state, p.entity)} {p.quantity} changed (hidden number){mark}"
        return f"  {e.seq} {name(state, p.entity)} {p.quantity} {p.new_value - p.delta} -> {p.new_value} ({p.reason}){mark}"
    if t == "condition_applied":
        src = (p.instance.source or {}).get("entity")
        return (f"  {e.seq} condition {p.instance.condition_id} {p.instance.severity} on {name(state, p.target)}"
                + (f" from {name(state, str(src))}" if src else "") + mark)
    if t == "condition_removed":
        return f"  {e.seq} condition removed {p.instance_id} ({p.reason}){mark}"
    if t == "frame_committed":
        b = p.frame.get("beat") or {}
        return f"  {e.seq} {p.frame_id} committed: \"{_flat(b.get('restatement') or b.get('intent'), 120)}\" (use recompute)"
    if t == "frame_resolved":
        r = p.roll or {}
        return (f"  {e.seq} {p.frame_id} rolled d20 {r.get('d20')} -> {r.get('total')}: {p.degree}, reach "
                f"{(p.delivered or {}).get('reach')}" + (f"; costs {p.costs}" if p.costs else "")
                + (f"; whatever the roll: {p.method_consequences}" if p.method_consequences else ""))
    if t == "ruling_logged":
        r = p.ruling or {}
        return f"  {e.seq} ruling {r.get('kind')}: {_flat((r.get('result') or {}).get('outcome'), 160)}"
    if t == "pause_opened":
        return f"  {e.seq} pause opened ({p.pause.kind}): {_flat(p.pause.prompt, 120)}"
    if t == "pause_closed":
        return f"  {e.seq} pause closed by {p.by}: {p.choice}"
    if t == "time_advanced":
        return f"  {e.seq} time passed ({', '.join(p.boundaries) or 'within the hour'}){mark}"
    if t == "position_set" and p.location:
        return f"  {e.seq} {name(state, p.entity)} now at {name(state, p.location)}{mark}"
    if t == "scene_started":
        return f"  {e.seq} scene started at {name(state, getattr(p.scene, 'place_id', '') or '')}{mark}"
    if t == "meta_set" and p.key == "log.harm" and isinstance(p.value, dict):
        v = p.value
        amount = f", {v.get('amount')} after reductions {v.get('breakdown')}" if v.get("target") == pc_of(state) else ""
        return (f"  {e.seq} harm to {name(state, str(v.get('target')))}: a {v.get('severity')} blow{amount}, from "
                f"{name(state, str(v.get('source')))}{mark}")
    if t == "writes_reverted":
        return f"  {e.seq} reverted {len(p.reverted)} writes: {_flat(p.reason, 120)}"
    if t == "knowledge_recorded" and p.fact_id in state.facts:
        return f"  {e.seq} {name(state, p.knower)} learned {p.fact_id} ({p.how}){mark}"
    return None


def _turn_tool(ctx: Any, arg: str) -> str:
    store, state = ctx.store, ctx.state
    m = re.search(r"\d+", arg)
    tid = ids.counter_id(ids.TURN, int(m.group(0))) if m else ""
    tr = store.turn(tid) if tid else None
    if tr is None:
        return f"no turn {arg!r} (turns are turn.1 … {getattr(ctx, 'turn_id', '')})"
    lines = [f"{tid} player: \"{_flat(tr.input_verbatim, 400)}\"", f"game: \"{_flat(tr.delivered_verbatim, 1400)}\"",
             "record:"]
    for e in store.events():
        if e.turn_id == tid:
            line = _event_line(store, state, e)
            if line:
                lines.append(line)
    return "\n".join(lines)


def _entity_tool(ctx: Any, arg: str) -> str:
    store, state, rules = ctx.store, ctx.state, ctx.rules
    eid = resolve(state, arg)
    if eid is None:
        return f"no one or nothing on record called {arg!r}"
    e = state.entities[eid]
    pos = state.positions.get(eid)
    bands = ", ".join(f"{name(state, k)} {str(v).removeprefix('band.')}" for k, v in (pos.band_to if pos else {}).items())
    lines = [f"{eid}: {name(state, eid)} ({e.kind}" + (f", {e.data.get('pronouns')}" if e.data.get("pronouns") else "")
             + ")" + (f", at {name(state, pos.location)}" if pos and pos.location else "")
             + (f"; bands: {bands}" if bands else ""), f"sheet: {sheet_line(state, rules, eid)}", "facts on record:"]
    mine = [f for f in state.facts.values() if f.subject == eid and visible(state, f) and f.value is not None]
    lines += [f"  {fact_line(store, state, f)}" for f in mine[-30:]] or ["  (none)"]
    about = [f for f in state.facts.values() if f.subject != eid and visible(state, f) and eid in json.dumps(f.value)]
    if about:
        lines.append("facts elsewhere naming it:")
        lines += [f"  {fact_line(store, state, f)}" for f in about[-12:]]
    return "\n".join(lines)


_STOP = frozenset("that this with from have they them then into never were your there about what when which would "
                  "should could said says just only also again still been being because while game turn the and "
                  "but not you".split())


def _search_tool(ctx: Any, arg: str) -> str:
    words = [w for w in re.findall(r"[a-z0-9']{3,}", arg.lower()) if w not in _STOP]
    if not words:
        return "give some words to search for"
    scored = []
    for tr in play_turns(ctx.store, getattr(ctx, "turn_id", None)):
        hay = f"{tr.input_verbatim} {tr.delivered_verbatim}".lower()
        n = sum(1 for w in words if w in hay)
        if n:
            scored.append((n, turn_no(tr.turn_id), tr))
    scored.sort(key=lambda x: (-x[0], -x[1]))
    out = []
    for n, _, tr in scored[:6]:
        flat = _flat(tr.delivered_verbatim)
        sents = [s for s in re.split(r"(?<=[.!?\"”])\s+", flat) if any(w in s.lower() for w in words)][:2]
        out.append(f"{tr.turn_id} ({n}/{len(words)} words) player: \"{_flat(tr.input_verbatim, 160)}\" | "
                   + " … ".join(_flat(s, 220) for s in sents))
    return "\n".join(out) or f"no turn holds any of: {', '.join(words)}"


def _frames_for(store: Any, arg: str) -> list[Any]:
    a = arg.strip()
    evs = list(store.events(types=["frame_committed"]))
    if a.startswith("frame."):
        return [e for e in evs if getattr(e.payload, "frame_id", None) == a]
    m = re.search(r"\d+", a)
    tid = ids.counter_id(ids.TURN, int(m.group(0))) if m else ""
    return [e for e in evs if e.turn_id == tid]


def _recompute_tool(ctx: Any, arg: str) -> str:
    from engine.dm.dispute import recompute

    store, state = ctx.store, ctx.state
    frames = _frames_for(store, arg)
    if not frames:
        return f"no roll was committed in {arg!r} (a refused or no-roll beat shows in `turn` as a ruling)"
    out = []
    for ev in frames:
        f: dict[str, Any] = ev.payload.frame  # type: ignore[attr-defined]
        b = f.get("beat") or {}
        mod = f.get("modifier") or {}
        ch = b.get("change") or {}
        out.append(f"{ev.payload.frame_id} ({ev.turn_id}): \"{_flat(b.get('restatement') or b.get('intent'), 140)}\" as "  # type: ignore[attr-defined]
                   f"{str(b.get('verb') or '').removeprefix('verb.')}, typed change {ch.get('kind')} {ch.get('what') or ''}")
        out.append(f"  {f.get('attribute')}, DC {f.get('dc')} ({f.get('dc_source')} {f.get('tier') or ''}), modifier "
                   f"{int(mod.get('total') or 0):+d}, odds {(f.get('odds') or {}).get('success_or_better')}%, stakes "
                   f"{f.get('stakes')}, reach {f.get('reach')}")
        for kind, cites in (("lever +2", f.get("levers") or []), ("snag -2", f.get("snags") or [])):
            for c in cites:
                fid = str(c.get("fact_id") if isinstance(c, dict) else c)
                fact = state.facts.get(fid) or state.superseded_facts.get(fid)
                what = fact_line(store, state, fact) if fact is not None and fid not in state.seals else fid
                out.append(f"  {kind}: {'tried before (engine)' if isinstance(c, dict) and c.get('engine') else what}")
        if f.get("method_consequences"):
            out.append(f"  whatever the roll: {f.get('method_consequences')}")
        diffs = recompute(store, ctx.rules, f, int(ev.seq or 0))
        out.append("  recomputed from the rules: " + ("; ".join(diffs) if diffs else "the same numbers"))
    return "\n".join(out)


def _ledger_tool(ctx: Any, arg: str) -> str:
    from engine.resolve.change import holder_of

    store, state = ctx.store, ctx.state
    pc = resolve(state, arg) if arg.strip() else pc_of(state)
    if pc is None:
        return "no character"
    lines = [f"{name(state, pc)} now: {sheet_line(state, ctx.rules, pc)}", "quantity history (oldest first):"]
    for e in store.events(types=["quantity_changed", "quantity_defined"]):
        p: Any = e.payload
        if p.entity != pc:
            continue
        mark = " (REVERTED)" if e.seq in state.reverted else ""
        if e.type == "quantity_defined":
            lines.append(f"  {e.seq} {e.turn_id or 'setup'} {p.quantity} set to {p.value.current}{mark}")
        else:
            lines.append(f"  {e.seq} {e.turn_id} {p.quantity} {p.new_value - p.delta} -> {p.new_value} ({p.reason}){mark}")
    held = [i for i, x in state.entities.items() if x.kind in ("item", "object", "clue") and holder_of(state, i) == pc]
    lines.append("carries: " + (", ".join(f"{i} ({name(state, i)})" for i in held) or "nothing on record"))
    pays = [(e.turn_id, c) for e in store.events(types=["frame_committed"])
            for c in e.payload.frame.get("method_consequences") or []  # type: ignore[attr-defined]
            if re.search(r"\b(coins?|silver|pay|paid|price|bribe|fee)\b", c, re.IGNORECASE)]
    if pays:
        lines.append("method consequences naming coin: " + "; ".join(f"{t}: \"{_flat(c, 100)}\"" for t, c in pays))
    return "\n".join(lines[-45:])


def _said_tool(ctx: Any, arg: str) -> str:
    from engine.dm.testimony import records

    store, state = ctx.store, ctx.state
    who = resolve(state, arg) if arg.strip() else None
    recs = [r for r in records(state) if who is None or r.get("speaker") == who or who in (r.get("about") or [])]
    lines = []
    for r in recs[-12:]:
        fid = r.get("fact")
        f = state.facts.get(str(fid)) if fid else None
        settled = (f"settled as {fact_line(store, state, f)}" if f is not None and visible(state, f)
                   else "settled, since superseded" if fid else "testimony only (not a fact)")
        lines.append(f"{r.get('id')} {r.get('turn')} {name(state, str(r.get('speaker')))}: \"{_flat(r.get('words'), 220)}\""
                     f" -> {settled}")
    tf = [f for f in state.facts.values() if f.source == "testimony" and visible(state, f) and f.value is not None
          and (who is None or f.subject == who)]
    if tf:
        lines.append("facts settled from testimony:")
        lines += [f"  {fact_line(store, state, f)}" for f in tf[-10:]]
    return "\n".join(lines) or "nothing said on record" + (f" by {name(state, who)}" if who else "")


TOOL_FNS = {"turn": _turn_tool, "entity": _entity_tool, "search": _search_tool, "recompute": _recompute_tool,
            "ledger": _ledger_tool, "said": _said_tool}


def tool(ctx: Any, name_: str, arg: str) -> str:  # rule: PR-12-11
    """One read-only tool call (PR-12-11 step 2), as text, at most OUT_CHARS."""
    fn = TOOL_FNS.get(name_)
    if fn is None:
        return f"no tool {name_!r}"
    try:
        out = fn(ctx, str(arg or ""))
    except Exception as e:  # noqa: BLE001 - a tool that fails tells the Fixer so; it never fails the report
        out = f"the {name_} tool failed on {arg!r}: {type(e).__name__}"
    return out if len(out) <= OUT_CHARS else out[:OUT_CHARS] + "\n…(cut)"


# ------------------------------------------------------------------------------------------- the loop


def step_schema(final: bool = False, first: bool = False) -> Schema:  # rule: PR-12-11
    """One Fixer answer: tool calls to make next, or (final) the complaints with their findings and proposals."""
    call = obj({"tool": enum(TOOLS), "arg": STR})
    proposal = obj({"kind": enum(PROPOSALS), "turn": STR, "subject": STR, "key": STR, "value": STR,
                    "quantity": STR, "amount": STR, "fact_id": STR, "evidence": STRS})
    complaint = obj({"believes": STR, "category": enum(CATEGORIES), "turn": STR, "verdict": enum(VERDICTS),
                     "found": STR, "proposals": arr(proposal, max_items=4)})
    calls = arr(call, max_items=0 if final else PER_STEP)
    assert calls is not None
    if first:
        calls["minItems"] = 1
    return obj({"calls": calls, "final": {"type": "boolean", "const": True} if final else
                ({"type": "boolean", "const": False} if first else {"type": "boolean"}),
                "complaints": arr(complaint, max_items=4)})


def default() -> dict[str, Any]:
    """Nothing understood: one complaint, explained as not found (the reply asks for the turn)."""
    return {"calls": [], "final": True, "complaints": [{
        "believes": "", "category": "other", "turn": "", "verdict": "unclear",
        "found": "I couldn't pin down what went wrong from the record.", "proposals": []}]}


def opening(ctx: Any, text: str) -> str:
    """THIS MESSAGE's fixed part: the report, the calendar, the PC's sheet, the people in view, the last turns."""
    from engine.audit.claims import calendar_season as season_word
    from engine.dm.oof import when_words

    state = ctx.state
    pc = pc_of(state)
    here = list(state.scene.cast_present) if state.scene else []
    people = []
    for eid in dict.fromkeys([*([pc] if pc else []), *here]):
        e = state.entities.get(eid)
        if e is None or eid in state.seals:
            continue
        bond = [f"{f.predicate}={_flat(json.dumps(f.value), 60)}" for f in state.facts.values()
                if f.subject == pc and f.predicate.startswith("bond.") and eid in json.dumps(f.value)]
        people.append(f"{eid}: {name(state, eid)}" + (f" ({e.data.get('pronouns')})" if e.data.get("pronouns") else "")
                      + (" [the player's character]" if eid == pc else "") + (f" [{'; '.join(bond)}]" if bond else ""))
    recent = list(reversed(play_turns(ctx.store, getattr(ctx, "turn_id", None))[:6]))
    place = name(state, state.scene.place_id) if state.scene and state.scene.place_id else "none"
    return "\n".join([
        f'THE PLAYER\'S REPORT: "{_flat(text)}"',
        f"NOW: {season_word(state)}, {when_words(state.time.now)}; scene at {place}; the report is "
        f"{getattr(ctx, 'turn_id', None) or 'now'}",
        f"THE PLAYER'S CHARACTER NOW: {name(state, pc) if pc else 'none'}: {sheet_line(state, ctx.rules, pc)}",
        "PEOPLE IN VIEW (id: name (pronouns) [bond]):", *people,
        "LAST TURNS (oldest first; use `turn` for the full record):",
        *(f'{t.turn_id} | player: "{_flat(t.input_verbatim, 240)}" | game: "{_flat(t.delivered_verbatim, 500)}"'
          for t in recent)])


def _budget(rules: Any) -> tuple[int, int]:
    try:
        s = rules.pacing["feedback"]["investigate"]["steps"]
        return int(s["max_steps"]), int(s["min"])
    except (AttributeError, KeyError, TypeError):
        return MAX_STEPS, MIN_STEPS


def investigate(ctx: Any, text: str) -> Investigation:  # rule: PR-12-11
    # rule: 12.3.6
    """PR-12-11 steps 1-3 `[J:enum]`: the Fixer's bounded tool loop on one snapshot (nothing is written until the
    loop ends), then its complaints with findings and proposals. Without a model: nothing understood."""
    from engine.dm.roles.prompts import load_prompt
    from engine.llm.base import Packet, Role, call_role

    out = Investigation()
    if getattr(ctx, "model", None) is None:
        out.complaints = default()["complaints"]
        return out
    max_steps, min_steps = _budget(getattr(ctx, "rules", None))
    head = opening(ctx, text)
    made = 0
    for step in range(max_steps + 1):
        final = made >= max_steps
        log = [f"[{i + 1}] {t}({a!r}):\n{o}" for i, (t, a, o) in enumerate(out.calls)]
        left = max_steps - made
        note = ("Decide now: no tool calls are left; give the complaints with findings and proposals." if final else
                f"You have {left} tool call(s) left (up to {PER_STEP} per answer). "
                + (f"Make at least {min_steps - made} more before deciding." if made < min_steps else
                   "Decide when the record answers every complaint."))
        packet = Packet(instructions=load_prompt("fixer"), message="\n".join(
            [head, "INVESTIGATION SO FAR:", *(log or ["(nothing yet)"]), note]))
        res = call_role(ctx.model, Role.FIXER, step_schema(final=final, first=step == 0), packet,
                        turn_id=getattr(ctx, "turn_id", None), recorder=getattr(ctx, "record_call", None),
                        default=default() if final else {"calls": [], "final": True, "complaints": []})
        data = res.data or {}
        calls = [c for c in data.get("calls") or [] if isinstance(c, dict)][:min(PER_STEP, max_steps - made)]
        if data.get("final") and (made >= min_steps or not calls) or final:
            out.complaints = [c for c in data.get("complaints") or [] if isinstance(c, dict)] or default()["complaints"]
            return out
        for c in calls:
            out.calls.append((str(c.get("tool")), str(c.get("arg") or ""), tool(ctx, str(c.get("tool")),
                                                                                str(c.get("arg") or ""))))
        made += len(calls)
        if not calls:  # neither a call nor a decision: one forced decision next
            made = max_steps
    out.complaints = default()["complaints"]
    return out


__all__ = ["CATEGORIES", "PROPOSALS", "TOOLS", "VERDICTS", "Investigation", "default", "investigate", "opening",
           "pc_of", "sheet", "sheet_line", "step_schema", "tool", "turn_no"]
