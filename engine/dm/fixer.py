"""PR-12-11 the Fixer: a player's report investigated like an engineer debugging the game: read the record, look at what
each role was given and returned, try a correction on a copy, check the screen, then propose (specs 022, 026).

    out = investigate(ctx, "the coin for the round was never taken")   # the bounded tool loop, then the screen check
    out.complaints   # [{believes, category, turn, verdict, found, proposals: [{kind, ...}]}], all from one snapshot
    out.calls        # [(tool, arg, output)]: what the Fixer looked at (the evidence a proposal may cite)
    out.checks       # the screens the Fixer was shown after its decision (dry runs on a copy)
    tool(ctx, "turn", "turn.14")                                      # one read-only tool, as text

The Fixer role (12.2.4; `pacing.yaml#feedback.investigate`) reads the report with the calendar, the PC's card, the
people in view (the same people card the Reader, Framer and Narrator read, DL-12-116) and the last turns, then calls
the tools: a turn's record (frames, rolls with the effective degree, cited facts and every write, in plain words), a
person or thing (the people card, the sheet, each fact with its provenance), a transcript search, a frame recomputed
from the rules, the PC's coin and inventory ledger, what a character said against the record, that turn's model inputs
and outputs (`calls`), a dry run of proposals on a copy (`try`) and a turn replayed on a copy (`replay`). Tools never
write the game and never show sealed content (INV-10). When it decides, code runs the decision on a copy and shows
the Fixer the screen the player would see; it keeps or revises the decision, at most CHECKS times (DL-12-117). Then
engine/dm/dispute.py validates and applies it (code owns the spine; the model owns the reading and the judgment).
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

from engine import ids
from engine.dm.schemas import STR, STRS, Schema, arr, enum, obj

TOOLS = ("turn", "entity", "search", "recompute", "ledger", "said", "calls", "try", "replay")
PROPOSALS = ("set_fact", "remove_fact", "restore", "refund", "deduct", "reframe", "take_back", "correct_testimony",
             "remove_condition", "explain")
CATEGORIES = ("remembered_wrong", "rule_wrong", "contradiction", "misread", "ruling_question", "other")  # 12.3.6 item 2
VERDICTS = ("player_right", "partly", "record_stands", "unclear")
PLAYER_FACING = ("shown", "available")
MAX_STEPS, MIN_STEPS = 6, 3  # pacing.yaml#feedback.investigate.steps (read from the rules when given)
PER_STEP = 3  # tool calls one answer may ask for
CHECKS = 2  # PR-12-11 step 6: the screen after the repair is checked, and the decision revised, at most this often
OUT_CHARS = 2400  # one tool output, at most
WIDE = {"calls": 3600, "try": 3000, "replay": 3000}  # tools that show a whole screen or packet
SKIP_PREDICATES = ("trg.", "log.", "closed.", "lethal", "dc.")
CALL_ROLES = ("reader", "framer", "narrator", "interpret", "testimony", "checker",  # the PC-knowledge roles (INV-10)
              "dm")  # spec 032: the DM, its PRIVATE lines (the secrets arm) never shown


@dataclass
class Investigation:
    complaints: list[dict[str, Any]] = field(default_factory=list)
    calls: list[tuple[str, str, str]] = field(default_factory=list)  # (tool, arg, output)
    checks: list[str] = field(default_factory=list)  # the screens shown after each decision (dry runs)
    previewed: list[dict[str, Any]] = field(default_factory=list)  # the decision the last screen showed
    tape: list[Any] = field(default_factory=list)  # that dry run's play-role answers, reused when it is applied

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


_ENTITY_ID = re.compile(r"\b(?:pc|npc|companion|adversary|item|object|loc|place|fac|doc|thread|clue)\.[a-z0-9_.]+\b")


def _names(state: Any, text: str) -> str:
    """Entity ids in a value as the names the player knows (a sealed one stays an id: never its name)."""
    return _ENTITY_ID.sub(lambda m: name(state, m.group(0)) if m.group(0) in state.entities
                          and m.group(0) not in state.seals else m.group(0), text)


def plain_fact(state: Any, f: Any) -> str:  # rule: PR-12-11
    """A fact in plain words (DL-12-116), never a slug: the Chance line's own sentence ("Magby is alert to …"),
    else who it is about, the predicate in words and the value with names for ids."""
    from engine.dm.oof import fact_short
    from engine.text.render import slug_words

    words = fact_short(state, f.id) if state.facts.get(f.id) is f else ""
    if words:
        return words
    who = "the world" if f.subject == "world" else name(state, f.subject)
    v = f.value
    val = ("yes" if v else "no") if isinstance(v, bool) else _flat(
        json.dumps(v, ensure_ascii=False) if isinstance(v, dict | list) else v, 160)
    return _names(state, f"{who}: {slug_words(f.predicate.removeprefix('detail.'))}: {val}")


def fact_line(store: Any, state: Any, f: Any) -> str:
    return f"{f.id}: {plain_fact(state, f)} (source {f.source}, {_turn_of(store, f.valid_from_seq)})"


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
    """The values a player sees about `eid`: shown quantities, the harm word, conditions, what it holds (the `Now:`
    line's source; who someone is lives on the people card)."""
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


def cond_origins(store: Any, state: Any, rules: Any, eid: str) -> list[str]:  # rule: PR-12-11
    """Each condition on `eid` with where it came from: the event, its turn, the roll or source and the rule (spec 032
    P6: a Fixer with no origin view made one up). `cinst.N` is what `remove_condition` takes."""
    first = {}
    for e in store.events(types=["condition_applied"]):
        first.setdefault(getattr(e.payload, "instance_id", ""), e)
    out = []
    for c in state.conditions_on(eid):
        e = first.get(c.instance_id)
        src = c.source or {}
        out.append(f"  {c.instance_id}: {_cond_name(rules, c.condition_id)} ({c.condition_id} {c.severity})"
                   + (f", put on at {e.seq} in {e.turn_id or 'setup'} (rule {e.rule_id})" if e is not None else "")
                   + (f" by {src['frame_id']}" if src.get("frame_id") else "")
                   + (f", source {name(state, str(src['entity']))}" if src.get("entity") else ""))
    return out


def _cond_name(rules: Any, cid: str) -> str:
    try:
        return str(rules.condition(cid).get("name") or cid).lower()
    except Exception:  # noqa: BLE001
        return cid.removeprefix("cond.")


def sheet_line(state: Any, rules: Any, eid: str | None) -> str:
    return " · ".join(f"{k} {v}" for k, v in sheet(state, rules, eid).items())


def card(state: Any, rules: Any, eid: str) -> list[str]:
    """The shared people card (engine/dm/packet.py, DL-12-116) as the Fixer reads it: refusals included, marked."""
    from engine.dm.packet import people_card

    return people_card(state, eid, rules=rules, hidden=True)


# ------------------------------------------------------------------------------------------- the tools


def _cites(state: Any, frame: dict[str, Any]) -> str:
    """A frame's cited facts in plain words: what moved the odds."""
    out = []
    for kind, cites in (("+2", frame.get("levers") or []), ("−2", frame.get("snags") or [])):
        for c in cites:
            fid = str(c.get("fact_id") if isinstance(c, dict) else c)
            if isinstance(c, dict) and c.get("engine"):
                out.append(f"tried before {kind}")
                continue
            f = state.facts.get(fid) or state.superseded_facts.get(fid)
            out.append(f"{fid} \"{plain_fact(state, f)}\" {kind}" if f is not None and fid not in state.seals else
                       f"{fid} {kind}")
    return "; ".join(out)


def _degree(state: Any, p: Any) -> str:
    """The effective degree (DL-01-48, spec 024 hand-off): success at a cost counts as success; a near miss waiting
    on the choice has none yet."""
    from engine.dm.adjudication import effective_degree

    b = SimpleNamespace(near_miss=p.near_miss, success_at_cost=p.success_at_cost_taken, degree=p.degree,
                        frame_id=p.frame_id)
    eff = effective_degree(b, state.open_pause())  # type: ignore[arg-type]
    if p.success_at_cost_taken:
        return "success at a cost (counts as a success)"
    if eff is None:
        return "a near miss, waiting on the player's choice" if p.near_miss else "no degree"
    return str(eff).replace("_", " ") + (" (a near miss)" if p.near_miss else "")


def _event_line(store: Any, state: Any, e: Any) -> str | None:  # noqa: PLR0911, PLR0912 - one line per event kind
    p: Any = e.payload
    t = e.type
    mark = " (REVERTED)" if e.seq in state.reverted else ""
    if t == "fact_set":
        f = state.facts.get(p.fact_id) or state.superseded_facts.get(p.fact_id)
        if p.visibility not in PLAYER_FACING or p.subject in state.seals or p.fact_id in state.seals \
                or p.predicate.startswith(SKIP_PREDICATES):
            return None
        words = plain_fact(state, f) if f is not None and p.value is not None else \
            f"{name(state, p.subject)}: {p.predicate.replace('_', ' ')} (removed)"
        src = getattr(f, "source", None) or e.source
        return f"  {e.seq} {p.fact_id}: {words} (source {src}){mark}"
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
        return (f"  {e.seq} {p.frame_id} committed: \"{_flat(b.get('restatement') or b.get('intent'), 120)}\", chance "
                f"{(p.frame.get('odds') or {}).get('success_or_better')}%" + (f" ({c})" if (c := _cites(state, p.frame))
                                                                              else "") + " (use recompute)")
    if t == "frame_resolved":
        r = p.roll or {}
        return (f"  {e.seq} {p.frame_id} rolled d20 {r.get('d20')} -> {r.get('total')}: {_degree(state, p)}, reach "
                f"{(p.delivered or {}).get('reach')}" + (f"; costs {p.costs}" if p.costs else "")
                + (f"; whatever the roll: {p.method_consequences}" if p.method_consequences else ""))
    if t == "ruling_logged":
        r = p.ruling or {}
        return f"  {e.seq} ruling {r.get('kind')}: {_flat((r.get('result') or {}).get('outcome'), 160)}"
    if t == "pause_opened":
        d = p.pause.detail or {}
        now = state.open_pause()
        here = " — OPEN NOW, on the player's screen; nothing spent yet" if now is not None and \
            now.pause_id == p.pause.pause_id else ""
        f = d.get("frame") or {}
        odds = f", chance {(f.get('odds') or {}).get('success_or_better')}%" if f else ""
        c = _cites(state, f) if f else ""
        return (f"  {e.seq} pause opened ({d.get('stage') or p.pause.kind}){here}: {_flat(p.pause.prompt, 120)}{odds}"
                + (f" ({c})" if c else ""))
    if t == "pause_closed":
        return f"  {e.seq} pause closed by {p.by}: {p.choice}"
    if t == "time_advanced":
        return f"  {e.seq} time passed ({', '.join(p.boundaries) or 'within the hour'}){mark}"
    if t == "position_set" and p.location:
        return f"  {e.seq} {name(state, p.entity)} now at {name(state, p.location)}{mark}"
    if t == "relationship_set" and p.kind == "standing":
        return f"  {e.seq} {name(state, p.a)}'s standing toward {name(state, p.b)} now {p.new_value} ({p.reason}){mark}"
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
    if t == "entity_created" and p.entity.kind in ("npc", "companion", "adversary", "item", "object") \
            and p.entity.id not in state.seals:  # spec 032 G11: someone or something made this turn (a DM's prose)
        return f"  {e.seq} new on record: {name(state, p.entity.id)} ({p.entity.id}){mark}"
    return None


def dm_log(tr: Any) -> list[str]:  # rule: PR-12-11
    """A dm-tools turn's tool log (spec 032 G11): each DM tool call, its arguments and what code answered; a call code
    refused twice is DROPPED (not done). The secrets arm's PRIVATE lines are never shown (INV-10)."""
    s = ((tr.screen or {}).get("dm_tools") or {}) if tr is not None else {}
    if not s:
        return []
    tools = list(s.get("tools") or [])
    drop = Counter((r.get("tool"), r.get("args")) for r in s.get("dropped") or [])
    marks = [""] * len(tools)
    for i in reversed(range(len(tools))):  # the last breach of a call is the one dropped
        k = (tools[i].get("tool"), tools[i].get("args"))
        if drop[k]:
            drop[k] -= 1
            marks[i] = " [DROPPED: not done]"
    out = [("the /fix re-run's " if s.get("fix") else "") + "DM tool calls (the DM model asked; code answered):"
           if tools else "DM tool calls: none (the DM wrote the passage alone)"]
    for i, c in enumerate(tools):
        said = " / ".join(x for x in str(c.get("out") or "").splitlines() if "PRIVATE" not in x)
        out.append(f"  [{i + 1}] {c.get('tool')} {c.get('args')} -> {_flat(said, 300)}{marks[i]}")
    return out


def _tid(arg: str) -> str:
    m = re.search(r"\d+", arg)
    return ids.counter_id(ids.TURN, int(m.group(0))) if m else ""


def _turn_tool(ctx: Any, arg: str) -> str:
    store, state = ctx.store, ctx.state
    tid = _tid(arg)
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
    lines += dm_log(tr)
    if tr.model_calls:
        lines.append(f"model calls this turn: {', '.join(sorted({c.split('.')[3] for c in tr.model_calls if c.count('.') >= 4}))}"
                     " (use `calls`)")
    return "\n".join(lines)


def _entity_tool(ctx: Any, arg: str) -> str:
    from engine.retrieve.scene import CAST_KINDS

    store, state, rules = ctx.store, ctx.state, ctx.rules
    eid = resolve(state, arg)
    if eid is None:
        return f"no one or nothing on record called {arg!r}"
    e = state.entities[eid]
    pos = state.positions.get(eid)
    bands = ", ".join(f"{name(state, k)} {str(v).removeprefix('band.')}" for k, v in (pos.band_to if pos else {}).items())
    lines = [f"{eid} ({e.kind})" + (f", at {name(state, pos.location)}" if pos and pos.location else "")
             + (f"; bands: {bands}" if bands else "")]
    if e.kind in (*CAST_KINDS, "pc"):
        lines += card(state, rules, eid)  # the people card every role reads (DL-12-116)
    else:
        lines.append(f"{name(state, eid)}" + (f": {_flat(e.data.get('desc'), 160)}" if e.data.get("desc") else ""))
    if (sl := sheet_line(state, rules, eid)):
        lines.append(f"sheet: {sl}")
    if (origins := cond_origins(store, state, rules, eid)):
        lines += ["conditions on record (where each came from):", *origins]
    lines.append("facts on record:")
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
    state = ctx.state  # the record too, not only what was said on screen (a standing order, a rank)
    hits = [(sum(1 for w in words if w in t.lower()), f, t) for f in state.facts.values()
            if visible(state, f) and f.value is not None and (t := plain_fact(state, f))]
    facts = [f"  {fact_line(ctx.store, state, f)}" for n, f, _ in sorted(hits, key=lambda h: -h[0]) if n][:6]
    if facts:
        out += ["facts on record holding them:", *facts]
    return "\n".join(out) or f"no turn or fact holds any of: {', '.join(words)}"


def _frames_for(store: Any, state: Any, arg: str) -> list[tuple[str, int, str | None, dict[str, Any]]]:
    """(label, seq, turn, frame) for the committed frames of a turn (or one frame), and the OFFER on screen."""
    a = arg.strip()
    tid = "" if a.startswith("frame.") else _tid(a)
    out = [(str(e.payload.frame_id), int(e.seq or 0), e.turn_id, e.payload.frame)  # type: ignore[attr-defined]
           for e in store.events(types=["frame_committed"])
           if (getattr(e.payload, "frame_id", None) == a if a.startswith("frame.") else e.turn_id == tid)]
    pause = state.open_pause()
    if pause is not None and (pause.detail or {}).get("frame") and not a.startswith("frame."):
        ev = next((e for e in store.events(types=["pause_opened"]) if e.payload.pause_id == pause.pause_id), None)  # type: ignore[attr-defined]
        if ev is not None and ev.turn_id == tid:
            out.append(("the OFFER on screen (not rolled)", int(ev.seq or 0), ev.turn_id, pause.detail["frame"]))
    return out


def _recompute_tool(ctx: Any, arg: str) -> str:
    from engine.dm.dispute import recompute

    store, state = ctx.store, ctx.state
    frames = _frames_for(store, state, arg)
    if not frames:
        return f"no roll was framed in {arg!r} (a refused or no-roll beat shows in `turn` as a ruling)"
    out = []
    for label, seq, turn, f in frames:
        b = f.get("beat") or {}
        mod = f.get("modifier") or {}
        ch = b.get("change") or {}
        out.append(f"{label} ({turn}): \"{_flat(b.get('restatement') or b.get('intent'), 140)}\" as "
                   f"{str(b.get('verb') or '').removeprefix('verb.')}, goal {ch.get('kind')} "
                   f"{_names(state, ' '.join(str(x) for x in (ch.get('what'), ch.get('whom')) if x and x != 'none'))}")
        out.append(f"  {f.get('attribute')}, DC {f.get('dc')} ({f.get('dc_source')} {f.get('tier') or ''}), modifier "
                   f"{int(mod.get('total') or 0):+d}, odds {(f.get('odds') or {}).get('success_or_better')}%, stakes "
                   f"{f.get('stakes')}, reach {f.get('reach')}")
        if (c := _cites(state, f)):
            out.append(f"  cited: {c}")
        if f.get("method_consequences"):
            out.append(f"  whatever the roll: {f.get('method_consequences')}")
        diffs = recompute(store, ctx.rules, f, seq)
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
            if re.search(r"\b(coins?|silver|pay|paid|price|bribe|fee|fare)\b", c, re.IGNORECASE)]
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


def _section(packet: str, title: str) -> str:
    m = re.search(rf"\[{re.escape(title)}\]\n(.*?)(?=\n\n\[[A-Z ]+\]\n|\Z)", packet, re.DOTALL)
    return m.group(1) if m else ""


def _calls_tool(ctx: Any, arg: str) -> str:  # rule: PR-12-11
    """That turn's model inputs and outputs (DL-12-116): each play role's THIS MESSAGE and what it returned; name a
    role ("turn.11 framer") for its view too. Only the PC-knowledge roles (no motives, no sealed content)."""
    tid = _tid(arg)
    want = next((w for w in re.findall(r"[a-z]+", arg.lower()) if w in CALL_ROLES), None)
    rows = [r for r in ctx.store.model_calls(tid) if str(r.get("role")) in CALL_ROLES
            and (want is None or r.get("role") == want)] if tid else []
    if not rows:
        return f"no model call on record for {arg!r} (roles shown: {', '.join(CALL_ROLES)})"
    out = []
    for r in rows:
        packet = str((r.get("request") or {}).get("packet") or "")
        data = (r.get("response") or {}).get("data")
        msg = _section(packet, "THIS MESSAGE") or packet
        if r.get("role") == "dm" or msg.startswith("SITUATION\n"):  # spec 032 G11 (before P2 the DM ran as narrator):
            # the DM's situation once (PRIVATE lines never), then each answer
            sit = msg.split("\n\nRECENT CONVERSATION")[0]
            given = "" if r is not rows[0] else " / ".join(x for x in sit.splitlines() if "PRIVATE" not in x)
            out.append(f"dm ({r.get('model_id')})" + (f" was shown: {_flat(given, 1400)}" if given else ", next step"))
            out.append(f"  returned: {_flat(json.dumps(data, ensure_ascii=False), 900)}")
            continue
        out.append(f"{r.get('role')} ({r.get('model_id')}) was given: "
                   f"{_flat(_section(packet, 'THIS MESSAGE') or packet[-600:], 700)}")
        if want:
            out.append(f"  its view: {_flat(_section(packet, 'NARRATOR VIEW'), 1400)}")
        out.append(f"  returned: {_flat(json.dumps(data, ensure_ascii=False), 900)}")
    return "\n".join(out)


def _try_tool(ctx: Any, arg: str, text: str = "", inv: Investigation | None = None) -> str:  # rule: PR-12-11
    """A dry run (DL-12-117): the proposals (a JSON list, as in a decision) applied to a copy of the game, validation
    included; the screen the player would see. Nothing changes in the game."""
    from engine.dm.dispute import preview

    try:
        got = json.loads(arg)
    except json.JSONDecodeError:
        return 'give the proposals as a JSON list, e.g. [{"kind": "remove_fact", "fact_id": "fact.12", ...}]'
    props = got.get("proposals") if isinstance(got, dict) else got
    if not isinstance(props, list) or not all(isinstance(p, dict) for p in props):
        return "give the proposals as a JSON list of objects"
    trial = [{"believes": "", "category": "other", "turn": "", "verdict": "partly", "found": "(dry run)",
              "proposals": props}]
    return "dry run on a copy (nothing applied):\n" + preview(ctx, text, trial, inv.calls if inv else [])


def _replay_tool(ctx: Any, arg: str) -> str:  # rule: PR-12-11
    """A turn played again on a copy (DL-12-117): turn N taken back there, then its own words run through the
    Reader, gate, necessity and frame; the beats as read and framed (a dm-tools game: the DM's turn again, its tool
    calls and passage). Nothing changes in the game."""
    from engine.dm import dm_tools
    from engine.dm.dispute import _take_back, sandbox
    from engine.dm.narration import pause_blocks
    from engine.dm.turn import run_turn

    tid = _tid(arg)
    tr = ctx.store.turn(tid) if tid else None
    if tr is None:
        return f"no turn {arg!r}"
    with sandbox(ctx) as sx:
        with sx.store.transaction(getattr(ctx, "turn_id", None)) as tx:
            sx.tx = tx
            why, _ = _take_back(sx, tx, tid, f"dry run: replay {tid}")
            sx.tx = None
        if why:
            return f"cannot replay {tid} on a copy: {why}"
        if dm_tools.enabled(sx):  # spec 032 G11: the DM plays it again (the pipeline's Reader would be another game)
            if any(e.turn_id == tid and e.type == "pause_closed" and getattr(e.payload, "by", "") == "option"
                   for e in ctx.store.events(types=["pause_closed"])):
                return f"{tid} answered an offer ({tr.input_verbatim!r}); replay the turn that opened it"
            out = dm_tools.play_turn(sx, tr.input_verbatim)
            return "\n".join([f"{tid} played again by the DM on a copy (nothing kept): \"{_flat(tr.input_verbatim, 300)}\"",
                              *dm_log(out.turn_record), f"  passage: \"{_flat(out.response.fiction, 900)}\"",
                              *(f"  {_flat(b.text, 600)}" for b in out.response.oof_blocks)])
        adj = run_turn(sx, tr.input_verbatim)
        lines = [f"{tid} replayed on a copy (nothing kept): \"{_flat(tr.input_verbatim, 300)}\""]
        lines += [f"  beat: \"{_flat(b.restatement, 140)}\" · {str(b.verb or '').removeprefix('verb.')} · gate {b.gate}"
                  + (f" ({_flat(b.gate_words, 140)})" if b.gate_words else "") + (f" · {b.degree}" if b.degree else "")
                  for b in adj.record.beats]
        lines += [f"  {_flat(o['text'], 600)}" for o in adj.oof if o.get("kind") in ("RESULT", "REDIRECT", "NOTE")]
        if adj.pause is not None:
            lines += [f"  {_flat(b.text, 700)}" for b in pause_blocks(sx, adj.pause)]
        return "\n".join(lines)


TOOL_FNS = {"turn": _turn_tool, "entity": _entity_tool, "search": _search_tool, "recompute": _recompute_tool,
            "ledger": _ledger_tool, "said": _said_tool, "calls": _calls_tool, "replay": _replay_tool}


def tool(ctx: Any, name_: str, arg: str, *, text: str = "", inv: Investigation | None = None) -> str:  # rule: PR-12-11
    """One read-only tool call (PR-12-11 step 2), as text, at most OUT_CHARS (wider for a screen or a packet)."""
    fn = TOOL_FNS.get(name_)
    if fn is None and name_ != "try":
        return f"no tool {name_!r}"
    try:
        out = _try_tool(ctx, str(arg or ""), text, inv) if name_ == "try" else fn(ctx, str(arg or ""))  # type: ignore[misc]
    except Exception as e:  # noqa: BLE001 - a tool that fails tells the Fixer so; it never fails the report
        out = f"the {name_} tool failed on {arg!r}: {type(e).__name__}: {_flat(e, 200)}"
    n = WIDE.get(name_, OUT_CHARS)
    return out if len(out) <= n else out[:n] + "\n…(cut)"


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
    """THIS MESSAGE's fixed part: the report, the calendar, the PC's card and sheet, the people in view (their
    people cards), the offer on screen, the last turns."""
    from engine.audit.claims import calendar_season as season_word
    from engine.dm.oof import when_words

    state = ctx.state
    pc = pc_of(state)
    here = list(state.scene.cast_present) if state.scene else []
    people: list[str] = []
    for eid in dict.fromkeys(str(x) for x in here):
        if eid in state.entities and eid not in state.seals:
            c = card(state, ctx.rules, eid)
            people += [f"- {eid}: {c[0]}", *c[1:]] if c else []
    me = card(state, ctx.rules, pc) if pc else []
    recent = list(reversed(play_turns(ctx.store, getattr(ctx, "turn_id", None))[:6]))
    place = name(state, state.scene.place_id) if state.scene and state.scene.place_id else "none"
    pause = state.open_pause()
    offer = (f"ON SCREEN NOW: an open {(pause.detail or {}).get('stage') or pause.kind} (nothing spent yet): "
             f"{_flat(pause.prompt, 200)}" if pause is not None else "ON SCREEN NOW: no open offer or choice")
    return "\n".join([
        f'THE PLAYER\'S REPORT: "{_flat(text)}"',
        f"NOW: {season_word(state)}, {when_words(state.time.now)}; scene at {place}; the report is "
        f"{getattr(ctx, 'turn_id', None) or 'now'}",
        "THE PLAYER'S CHARACTER:", *([f"- {pc}: {me[0]}", *me[1:]] if me else ["- none"]),
        f"  sheet: {sheet_line(state, ctx.rules, pc)}",
        *(cond_origins(ctx.store, state, ctx.rules, pc) if pc else []),
        "PEOPLE IN VIEW (the people card every role reads):", *(people or ["- no one"]),
        offer,
        "LAST TURNS (oldest first; use `turn` for the full record):",
        *(f'{t.turn_id} | player: "{_flat(t.input_verbatim, 240)}" | game: "{_flat(t.delivered_verbatim, 500)}"'
          for t in recent)])


def _budget(rules: Any) -> tuple[int, int]:
    try:
        s = rules.pacing["feedback"]["investigate"]["steps"]
        return int(s["max_steps"]), int(s["min"])
    except (AttributeError, KeyError, TypeError):
        return MAX_STEPS, MIN_STEPS


def _ask(ctx: Any, schema: Schema, message: str, default_: dict[str, Any]) -> dict[str, Any]:
    from engine.dm.roles.prompts import load_prompt
    from engine.llm.base import Packet, Role, call_role

    res = call_role(ctx.model, Role.FIXER, schema, Packet(instructions=load_prompt("fixer"), message=message),
                    turn_id=getattr(ctx, "turn_id", None), recorder=getattr(ctx, "record_call", None),
                    default=default_)
    return res.data or {}


def _complaints(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [c for c in data.get("complaints") or [] if isinstance(c, dict)]


def investigate(ctx: Any, text: str) -> Investigation:  # rule: PR-12-11
    # rule: 12.3.6
    """PR-12-11 steps 1-3 and 6 `[J:enum]`: the Fixer's bounded tool loop on one snapshot (nothing is written until
    it ends), its decision, then the screen check: the decision run on a copy, its screen shown, kept or revised (at
    most CHECKS times). Without a model: nothing understood."""
    out = Investigation()
    if getattr(ctx, "model", None) is None:
        out.complaints = default()["complaints"]
        return out
    max_steps, min_steps = _budget(getattr(ctx, "rules", None))
    head = opening(ctx, text)
    made = 0
    decided: list[dict[str, Any]] = []

    def log() -> list[str]:
        return [f"[{i + 1}] {t}({a!r}):\n{o}" for i, (t, a, o) in enumerate(out.calls)] or ["(nothing yet)"]

    for step in range(max_steps + 1):
        final = made >= max_steps
        left = max_steps - made
        note = ("Decide now: no tool calls are left; give the complaints with findings and proposals." if final else
                f"You have {left} tool call(s) left (up to {PER_STEP} per answer). "
                + (f"Make at least {min_steps - made} more before deciding." if made < min_steps else
                   "Decide when the record answers every complaint."))
        data = _ask(ctx, step_schema(final=final, first=step == 0), "\n".join([head, "INVESTIGATION SO FAR:", *log(),
                                                                                 note]),
                    default() if final else {"calls": [], "final": True, "complaints": []})
        calls = [c for c in data.get("calls") or [] if isinstance(c, dict)][:min(PER_STEP, max_steps - made)]
        if data.get("final") and (made >= min_steps or not calls) or final:
            decided = _complaints(data)
            break
        for c in calls:
            out.calls.append((str(c.get("tool")), str(c.get("arg") or ""),
                              tool(ctx, str(c.get("tool")), str(c.get("arg") or ""), text=text, inv=out)))
        made += len(calls)
        if not calls:  # neither a call nor a decision: one forced decision next
            made = max_steps
    if not decided:
        out.complaints = default()["complaints"]
        return out
    out.complaints = _check(ctx, text, head, log(), decided, out)
    return out


def _check(ctx: Any, text: str, head: str, log: list[str], decided: list[dict[str, Any]],
           out: Investigation) -> list[dict[str, Any]]:  # rule: PR-12-11
    """PR-12-11 step 6 (DL-12-117): before anything is applied, the decision runs on a copy and the Fixer sees the
    screen the player would see; the same decision ends it, a revised one is checked again, at most CHECKS times."""
    from engine.dm.dispute import preview

    for _ in range(CHECKS):
        tape: list[Any] = []
        try:
            screen = preview(ctx, text, decided, out.calls, tape)
        except Exception as e:  # noqa: BLE001 - a dry run that fails leaves the decision as it is
            out.checks.append(f"(the dry run failed: {type(e).__name__})")
            return decided
        out.checks.append(screen)
        out.previewed, out.tape = decided, tape
        keep = {"calls": [], "final": True, "complaints": decided}
        data = _ask(ctx, step_schema(final=True), "\n".join([
            head, "INVESTIGATION SO FAR:", *log, "YOUR DECISION:", json.dumps(decided, ensure_ascii=False, sort_keys=True),
            "THE SCREEN THE PLAYER WILL SEE AFTER YOUR REPAIR (a dry run on a copy; nothing is applied yet):", screen,
            "Check it against the report. If it answers every complaint plainly and the thing complained about is gone "
            "from the screen (or rightly stays, explained), give the same decision again. If not, revise the decision "
            "(other proposals, a re-frame, a take-back, plainer words)."]), keep)
        revised = _complaints(data)
        if not revised or revised == decided:
            return decided
        decided = revised
    return decided


__all__ = ["CATEGORIES", "CHECKS", "PROPOSALS", "TOOLS", "VERDICTS", "Investigation", "card", "default",
           "investigate", "opening", "pc_of", "plain_fact", "sheet", "sheet_line", "step_schema", "tool", "turn_no"]
