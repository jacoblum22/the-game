"""Spec 031 prototype: one DM model with tools over the mechanical spine (`GameConfig.engine = "dm-tools"`).

    out = play_turn(ctx, "I ask the smith about the road.")   # one DM role in a bounded tool loop, then the passage
    out = play_answer(ctx, "commit")                           # an OFFER answered: code rolls, the DM narrates it
    out.response                                               # the delivered Response (same shape as the pipeline)

Code keeps the spine: the dice and odds (`resolve/`: gate, necessity, frame, OFFER, roll, read, cost), state (coin,
items, conditions, positions, presence, time), memory, the case graph and clue delivery (spec 029), the world step
(foes, time, omens, leads: engine/dm/dm_world.py). The DM model owns language and judgment: who answers, how people
react and what mood they are in (the `mood` tool: a memory it may change), what needs a roll, when a scene ends
(`end_scene`), the passage. Bypassed here (not deleted): the Reader, Framer, Director, World, Checker,
narrator record lines, `npc_layer` and the answer ladder. `/fix` stays the pipeline's (engine/dm/dispute.py).

Each turn: the DM sees the situation (who is here with their people card and mood, the place, the PC sheet, open
threads, the scene) and the recent conversation, calls up to MAX_TOOLS tools (PER_STEP per answer), then writes the
passage. A `propose_roll` that needs a roll pauses the turn on the code-rendered OFFER; the next `play_answer` rolls
and the DM narrates the result. Per-turn stats (tool calls, refusals, moods, world, secret leaks) go to
`TurnRecord.screen["dm_tools"]`.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from engine import ids
from engine.dm.adjudication import AdjudicationRecord
from engine.dm.context import TurnContext
from engine.dm.response import Flags, Response
from engine.dm.roles.prompts import load_prompt
from engine.dm.schemas import STR, Schema, arr, enum, obj
from engine.llm.base import Packet, Role, call_role
from engine.store.events import EntityRecord, Event
from engine.store.records import TurnRecord

ENGINE = "dm-tools"
MAX_TOOLS, PER_STEP = 6, 3
SAID_MAX = 6  # the lines a passage may list as said
TOOLS = ("propose_roll", "state", "change", "recall", "reveal_clue", "mood", "end_scene")
CHANGES = ("coin", "give_item", "new_item", "condition_add", "condition_remove", "npc_leaves", "new_npc", "travel",
           "rest", "fact", "fight")  # [spec 032 P3] fight: a person turns on the PC
FAIL_COSTS = ("cost.closed_door", "cost.drain", "cost.exposure", "cost.footing", "cost.gear", "cost.harm",
              "cost.shortfall", "cost.time", "cost.twist")  # the 9 cost ids (a test pins them to the rules)
_PERSON_KIND = re.compile(r"listener|watcher|creature|animal|person|helper|character|target's|entity|observer", re.I)
_THING_KIND = re.compile(r"\bobjects?\b|obstacle|\bthing\b|environment|trail|terrain|hazard", re.I)
COSTS = ("none", "small", "real", "big")
GRANTS = ("help", "price", "partial", "refuse")  # what the DM had the NPC do for an ask (logged, never gated)
STAKES = ("safe", "risky", "dire")
DM_ROLE = Role.DM  # spec 032 FR-13: its own role (schema, prompt file dm.md, offline heuristic, per-role model)
MOOD = {"willing": "open", "guarded": "guarded", "unwilling": "closed"}  # the held band -> the DM's word
BAND = {v: k for k, v in MOOD.items()}
OUT_CHARS = 1600
PREFERRED_COST = {"verb.strike": "cost.harm", "verb.grapple": "cost.harm", "verb.force": "cost.harm",
                  "verb.exert": "cost.harm", "verb.sneak": "cost.exposure", "verb.talk": "cost.closed_door"}


@dataclass
class Outcome:
    response: Response
    turn_record: TurnRecord


@dataclass
class Turn:
    """One turn's working state: the record the shared helpers fill, the blocks owed, the stats logged."""

    rec: AdjudicationRecord
    oof: list[dict[str, str]] = field(default_factory=list)
    log: list[tuple[str, str, str]] = field(default_factory=list)  # (tool, args, output)
    stats: dict[str, Any] = field(default_factory=lambda: {
        "tool_calls": 0, "steps": 0, "refusals": [], "moods": [], "leaks": [], "clues": [], "rolls": [], "dropped": [],
        "scene_ends": [], "world": {"foe_turns": [], "facts": [], "reasked": 0},
        "said": [], "told_dropped": [], "log_only": []})  # [spec 032 P5] the told records, what was dropped, the checks
    said_raw: list[Any] = field(default_factory=list)  # the DM's final-answer `said` list, as written
    told: list[dict[str, Any]] = field(default_factory=list)  # the said entries written (TurnRecord.said's shape)
    beats: list[Any] = field(default_factory=list)  # the BeatOutcomes of this turn (the world step reads their status)
    world_done: bool = False  # the world step runs once per exchange
    paused: bool = False
    made: list[str] = field(default_factory=list)  # people/creatures the resolver made this turn (told to the DM)
    aliases: dict[str, str] = field(default_factory=dict)  # an id the DM chose for a `new_npc` -> the id the game gave
    env: Any = None


def enabled(ctx: Any) -> bool:
    return str((getattr(ctx, "config", None) or {}).get("engine") or "") == ENGINE


# ------------------------------------------------------------------------------------------- entry points


def play_turn(ctx: TurnContext, message: str) -> Outcome:
    return _run(ctx, message, choice=None)


def play_answer(ctx: TurnContext, choice_id: str) -> Outcome:
    pause = ctx.store.state.open_pause()
    if pause is None or not any(c.get("id") == choice_id for c in pause.choices):
        raise ValueError(f"{choice_id!r} is not a choice of the open pause")
    return _run(ctx, choice_id, choice=choice_id)


def _run(ctx: TurnContext, message: str, *, choice: str | None) -> Outcome:
    from engine.dm import dm_world
    from engine.dm import oof as oofm
    from engine.dm.narration import owed, shown_pause, turn_blocks
    from engine.dm.turn import _harm_followups, _resume, _take, _turn_end, recent_exchanges
    from engine.harm.threshold import ending_state
    from engine.resolve.pipeline import close_by_default
    from engine.retrieve.scene import pc_id

    store = ctx.store
    turn_id = store.new_turn_id()
    store.save_turn(TurnRecord(turn_id=turn_id, input_verbatim=message))
    exchanges = recent_exchanges(store, turn_id, n=6)
    ctx.call_ids = []
    passage = ""
    with store.transaction(turn_id) as tx:
        ctx.tx = tx
        try:
            t = Turn(rec=AdjudicationRecord(turn_id=turn_id, pc=pc_id(tx.state)))
            t.env = _env(ctx, t)
            pause = tx.state.open_pause()
            lead = ""
            if choice is not None:  # an OFFER (or near miss, redirect, last chance) answered: code resolves it
                assert pause is not None
                label = next((c.get("label", c["id"]) for c in pause.choices if c.get("id") == choice), choice)
                res = _resume(ctx, t.env, pause, choice, t.oof)
                _take(t.rec, res, t.oof, None)
                t.beats += res.outcomes
                _harm_followups(ctx, t.env, t.rec, t.oof)
                lead = f"The player picked: {label}.\n" + _outcomes_text(ctx, t.rec, t.oof)
                lead += _world_text(_world(ctx, t))  # [spec 032 P4] the foes answer and time passes before the DM writes
            elif pause is not None and (pause.detail or {}).get("stage") in ("offer", "warning", "redirect",
                                                                                 "near_miss", "plan"):
                res = close_by_default(t.env, pause)  # new words with an offer open: it is withdrawn (12.2.6)
                _take(t.rec, res, t.oof, None)
                lead = "The roll offered last turn was not taken (withdrawn; nothing spent)."
            if tx.state.scene is None and tx.state.open_pause() is None:
                _open_scene(ctx)
            if tx.state.scene is not None:
                dm_world.ensure_site(ctx)
            if tx.state.open_pause() is None:  # a near miss or last chance opened by the answer: the menu first
                passage = _dm_loop(ctx, t, message if choice is None else "", exchanges, lead)
                facts = _world(ctx, t)  # a no-op on an answer turn (it ran before the loop)
                if facts and tx.state.open_pause() is None:  # one more call, only when the world produced a fact (F20)
                    passage = _reask(ctx, t, message if choice is None else "", exchanges, lead, passage, facts)
            _sync_scene(ctx, t)
            if tx.state.open_pause() is None:
                _turn_end(ctx, t.rec, t.oof)
                _harm_followups(ctx, t.env, t.rec, t.oof)
            _told(ctx, t, passage)  # [spec 032 P5] what people said: testimony records
            _audit(ctx, t, passage)
            _log_only(ctx, t, passage, message, exchanges, lead)
            events = list(tx.events)
        finally:
            ctx.tx = None
    t.rec.add_writes(events)
    st = store.state
    pause = st.open_pause()
    blocks, owned = turn_blocks(ctx, t.oof, t.rec, pause)
    resp = Response(turn_id=turn_id, phase="ending" if ending_state(st) else "play", fiction=passage.strip(),
                    oof_blocks=oofm.ordered(blocks), pause=shown_pause(pause, owned) if pause is not None else None,
                    flags=Flags())
    extra = owed(ctx, t.rec, resp.text())  # [spec 032 P5b trace] a staggered PC is shown [STATUS], as in the pipeline
    if extra:
        resp.oof_blocks = oofm.ordered([*resp.oof_blocks, *extra])
    calls = store.model_calls(turn_id)
    t.stats.update(model_calls=len(calls), tokens_in=sum(int(c.get("tokens_in") or 0) for c in calls),
                   tokens_out=sum(int(c.get("tokens_out") or 0) for c in calls),
                   latency_ms=sum(int(c.get("latency_ms") or 0) for c in calls),
                   tools=[{"tool": a, "args": b, "out": o[:300]} for a, b, o in t.log])
    tr = TurnRecord(turn_id=turn_id, input_verbatim=message, writes=t.rec.write_seqs,
                    beats=[b.frame_id for b in t.rec.beats if b.frame_id], delivered_verbatim=resp.text(),
                    model_calls=list(ctx.call_ids), screen={"dm_tools": t.stats}, said=t.told,
                    claim_log=[{"turn": turn_id, "sentence": i, "class": h["kind"], "verdict": "logged",
                                "store_value": h["text"]} for i, h in enumerate(t.stats["log_only"])],
                    draft_versions=[{"kind": "dm_tools", "text": passage, "steps": t.stats["steps"],
                                     "tools": t.stats["tool_calls"]}],
                    cost_usd=float(sum(c.get("cost_usd") or 0.0 for c in calls)),
                    latency_ms=int(t.stats["latency_ms"]),
                    pause=({"kind": pause.kind, "frame_id": pause.frame_id,
                            "options": [c.get("id", "") for c in pause.choices]} if pause is not None else None))
    store.save_turn(tr)
    return Outcome(response=resp, turn_record=tr)


def _env(ctx: TurnContext, t: Turn) -> Any:
    from engine.dm.turn import _env as pipeline_env

    env = pipeline_env(ctx)
    env.framer = code_framer(ctx, t)
    return env


# ------------------------------------------------------------------------------------------- the DM loop


def step_schema(ctx: TurnContext, *, final: bool) -> Schema:
    return schema_for(ctx.rules.ids("verb."), list(ctx.rules.resolution["intended_change"]["kinds"]), final=final)


def schema_for(verbs: list[str], kinds: list[str], *, final: bool) -> Schema:
    """The DM step's schema (`Role.DM`'s builder in engine/dm/schemas.py calls this with the SchemaContext's lists)."""
    calls = [
        obj({"tool": enum(["propose_roll"]), "goal": STR, "verb": enum(verbs), "target": STR, "how": STR,
             "attribute": STR, "difficulty": STR, "why_uncertain": STR, "stakes": enum(STAKES),
             "nonlethal": {"type": "boolean"}, "fail_cost": enum(["none", *FAIL_COSTS]),
             "change_kind": enum(kinds), "change_what": STR, "change_whom": STR}),
        obj({"tool": enum(["state"]), "about": STR}),
        obj({"tool": enum(["change"]), "kind": enum(CHANGES), "who": STR, "what": STR, "to": STR,
             "amount": {"type": "integer"}, "note": STR}),
        obj({"tool": enum(["recall"]), "query": STR}),
        obj({"tool": enum(["reveal_clue"]), "npc": STR, "question": STR}),
        obj({"tool": enum(["mood"]), "npc": STR, "mood": enum(list(BAND)), "why": STR}),
        obj({"tool": enum(["end_scene"]), "why": STR}),
    ]
    call = {"anyOf": calls}
    return obj({"calls": arr(call, max_items=0 if final else PER_STEP), "passage": STR,
                "said": arr(obj({"npc": STR, "words": STR}), max_items=SAID_MAX),  # [spec 032 P5] G3; [] when none
                "asks": arr(obj({"npc": STR, "cost": enum(COSTS), "granted": enum(GRANTS)}), max_items=4)})


def _dm_loop(ctx: TurnContext, t: Turn, message: str, exchanges: list[tuple[str, str]], lead: str) -> str:
    """The bounded tool loop: at most MAX_TOOLS tool calls, PER_STEP per answer, then the passage."""
    made = 0
    data: dict[str, Any] = {}
    for _ in range(MAX_TOOLS + 1):
        final = made >= MAX_TOOLS or t.paused
        note = ("Write the passage now (no tool calls are left)." if final and not t.paused else
                "A roll is now offered to the player: write only the lead-up to the attempt (or nothing), never its "
                "outcome." if t.paused else
                f"You may make up to {MAX_TOOLS - made} more tool call(s), {PER_STEP} per answer; with no calls, "
                "`passage` is delivered.")
        packet = Packet(instructions=load_prompt("dm"), message=_message(ctx, t, message, exchanges, lead, note))
        schema = step_schema(ctx, final=final)
        res = call_role(ctx.model, DM_ROLE, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call,
                        default={"calls": [], "passage": str(data.get("passage") or ""), "said": [], "asks": []})
        data = dict(res.data or {})
        t.stats["steps"] += 1
        calls = [c for c in data.get("calls") or [] if isinstance(c, dict)][:PER_STEP]
        if final or not calls:
            break
        for c in calls[:MAX_TOOLS - made]:
            out = tool(ctx, t, c)
            t.log.append((str(c.get("tool")), _args(c), out))
            made += 1
            t.stats["tool_calls"] += 1
            if t.paused:
                break
        if t.paused and data.get("passage"):  # the lead-up came with the proposal: no second call
            break
    _asks(ctx, t, data.get("asks") or [])
    t.said_raw = list(data.get("said") or [])  # [spec 032 P5] the last answer is the delivered one
    return str(data.get("passage") or "")


def _reask(ctx: TurnContext, t: Turn, message: str, exchanges: list[tuple[str, str]], lead: str, passage: str,
           facts: list[str]) -> str:
    """One more DM call, no tools: the final passage, told what the world did after the draft (spec 032 P4)."""
    world = _world_text(facts).strip() + "\nYOUR DRAFT PASSAGE:\n" + passage
    note = ("Write the final passage now (no tool calls). It replaces your draft: keep what still holds and weave in "
            "what the world did, agreeing with it exactly.")
    packet = Packet(instructions=load_prompt("dm"),
                    message=_message(ctx, t, message, exchanges, "\n".join(x for x in (lead, world) if x), note))
    res = call_role(ctx.model, DM_ROLE, step_schema(ctx, final=True), packet, turn_id=ctx.turn_id,
                    recorder=ctx.record_call, default={"calls": [], "passage": passage, "said": t.said_raw, "asks": []})
    t.stats["steps"] += 1
    t.stats["world"]["reasked"] += 1
    t.said_raw = list((res.data or {}).get("said") or [])  # the final passage replaces the draft, and its lines
    return str((res.data or {}).get("passage") or passage)


def _world(ctx: TurnContext, t: Turn) -> list[str]:
    """The world step once per exchange (engine/dm/dm_world.py); a time jump (a rest, a day) opens a new scene."""
    from engine.dm import dm_world

    if t.world_done or ctx.state.open_pause() is not None:
        return []
    t.world_done = True
    facts = dm_world.world_step(ctx, t)
    if dm_world.time_jumped(ctx):
        _open_scene(ctx, "time_jump")
        facts.append("Time has jumped on; a new scene begins here.")
    return facts


def _world_text(facts: list[str]) -> str:
    return ("\nWHAT THE WORLD DID (the game rolled and recorded these; the passage must agree with them):\n"
            + "\n".join(f"- {f}" for f in facts)) if facts else ""


def _args(c: dict[str, Any]) -> str:
    return json.dumps({k: v for k, v in c.items() if k != "tool" and v not in ("", None, "none", 0)},
                      ensure_ascii=False)


def _message(ctx: TurnContext, t: Turn, message: str, exchanges: list[tuple[str, str]], lead: str,
             note: str) -> str:
    convo = [f"PLAYER: {i}\nGAME: {_flat(o, 1200)}" for i, o in exchanges]
    done = [f"[{n + 1}] {a} {b}\n -> {o}" for n, (a, b, o) in enumerate(t.log)]
    return "\n\n".join(x for x in [
        "SITUATION\n" + situation(ctx),
        "RECENT CONVERSATION (oldest first)\n" + ("\n\n".join(convo) or "(the story has just begun)"),
        lead and "WHAT JUST HAPPENED\n" + lead,
        message and f"THE PLAYER'S MESSAGE\n{message}",
        "TOOL RESULTS THIS TURN\n" + ("\n".join(done) or "(none yet)"),
        note] if x)


def situation(ctx: TurnContext) -> str:
    """The compact situation: place and time, the PC (card and sheet), who is here (people card and mood), exits,
    open threads, the scene, and (the secrets arm) each present person's private knowledge."""
    from engine.dm.answer import held as held_band
    from engine.dm.fixer import sheet_line
    from engine.dm.oof import when_words
    from engine.dm.packet import people_card
    from engine.harm.state import descriptor
    from engine.resolve.change import holder_of
    from engine.resolve.conflict import state_words
    from engine.retrieve.scene import pc_id
    from engine.world.places import location, reachable
    from engine.world.scenes import cast_present
    from engine.world.social import thread_list

    st, rules = ctx.state, ctx.rules
    pc = pc_id(st)
    here = location(st) if pc else None
    lines = [f"Now: {when_words(st.time.now)}; at {_name(st, here)} ({here})" if here else "Now: nowhere on record"]
    lines += _fight_block(st, pc)
    sc = st.scene
    if sc is not None and (sc.agenda or sc.hoped_answer):
        lines.append(f"Scene: {sc.agenda}" + (f" (hoped: {sc.hoped_answer})" if sc.hoped_answer else ""))
    if pc:
        card = people_card(st, pc, rules=rules)
        lines += ["The player's character (" + pc + "): " + (card[0] if card else _name(st, pc)), *card[1:],
                  f"  sheet: {sheet_line(st, rules, pc)}"]
        held = [i for i, e in st.entities.items() if e.kind in ("item", "object", "clue") and holder_of(st, i) == pc]
        lines.append("  carries: " + (", ".join(f"{_name(st, i)} ({i})" for i in held) or "nothing on record"))
        hurt = descriptor(st, pc)  # [spec 032 P5, traced: a staggered PC read only as a word inside the sheet line]
        if hurt != "fresh":
            lines.append(f"  hurt: {hurt}" + (" (0 Vitality: the next blow wounds)" if hurt == "staggered" else ""))
    people = cast_present(st) if sc is not None else []
    lines.append("People here:" if people else "People here: no one")
    carried = _carried(st, people)
    for eid in people:
        card = people_card(st, eid, rules=rules)
        lines += [f"- {eid}: {card[0] if card else _name(st, eid)}", *card[1:]]
        if carried.get(eid):
            lines.append("  carries: " + _list(st, carried[eid]))
        if (hurt_words := state_words(st, eid)) != "fresh":  # a body or a downed person here is not talking
            lines.append(f"  state: {hurt_words}")
        m = _held_mood(st, eid)
        lines.append(f"  mood toward you: {m} ({(held_band(st, eid) or {}).get('why')})" if m else
                     "  mood toward you: not set (decide it, record it with `mood`)")
        if secrets_visible(ctx):
            lines += [f"  PRIVATE (they know this; the player does not): {s}" for s in secrets(st, eid)]
    away = _not_here(st, people)
    if away:
        lines.append("Not here: " + "; ".join(away))
    if here:
        exits = [f"{_name(st, x.to)} ({x.to})" for x in reachable(st, here) if x.to != here]
        lines.append("Exits: " + (", ".join(exits[:8]) or "none known"))
    threads = [x for x in thread_list(st) if x["status"] == "active"][:4]
    if threads:
        lines.append("Open threads: " + "; ".join(_flat(x["text"] or x["name"], 160) for x in threads))
    return "\n".join(lines)


def _carried(st: Any, people: list[str]) -> dict[str, list[str]]:
    """What each person here carries (items and objects they hold; never a sealed thing), one pass over the things."""
    from engine.resolve.change import holder_of

    out: dict[str, list[str]] = {}
    for i, e in st.entities.items():
        if e.kind in ("item", "object") and i not in st.seals and (h := holder_of(st, i)) in people:
            out.setdefault(h, []).append(i)
    return out


def _list(st: Any, ids_: list[str], cap: int = 6) -> str:
    more = f", and {len(ids_) - cap} more" if len(ids_) > cap else ""
    return ", ".join(f"{_name(st, i)} ({i})" for i in ids_[:cap]) + more


def _not_here(st: Any, here: list[str], cap: int = 6) -> list[str]:
    """People the character has met (in any scene's cast, or a bond) who are not in this scene, with where or why:
    elsewhere, dead, gone. Never-met people are not listed [spec 032 G6]."""
    from engine.harm.state import DEAD, harm_state
    from engine.retrieve.scene import pc_id

    pc = pc_id(st)
    met = dict.fromkeys(c for card in st.scene_cards.values() for c in card.cast)
    out = []
    for eid in met:
        e = st.entities.get(eid)
        if e is None or eid == pc or eid in here or e.kind not in ("npc", "companion", "adversary"):
            continue
        pos = st.positions.get(eid)
        where = pos.location if pos is not None else None
        if e.exists == "dead" or harm_state(st, eid) == DEAD:
            why = "dead"
        elif e.exists != "exists":
            why = "gone"
        else:
            why = f"at {_name(st, where)}" if where in st.entities else "elsewhere"
        out.append(f"{_name(st, eid)} ({eid}): {why}")
    return out[-cap:]


def _fight_block(st: Any, pc: str | None) -> list[str]:
    """The fight, in words (spec 032 G7): each foe's state and band to the character, and the character's own state."""
    from engine.resolve.conflict import record as conflict
    from engine.resolve.conflict import state_words

    rec = conflict(st)
    if not rec or not pc:
        return []
    pos = st.positions.get(pc)
    out = ["FIGHT: a fight is on. After each move of the character the game has the foes act and tells you what they "
           "did; a blow's result is never yours to write. The character's attack is a `propose_roll`."]
    for f in rec.get("foes", []):
        band = str((pos.band_to.get(f) if pos else None) or "near").removeprefix("band.")
        out.append(f"- {f}: {_name(st, f)}, {state_words(st, f)}; {band} to the character")
    out.append(f"- the character is {state_words(st, pc)}")
    return out


def secrets_visible(ctx: Any) -> bool:
    return str((getattr(ctx, "config", None) or {}).get("dm_secrets") or "hidden") == "visible"


def secrets(st: Any, eid: str) -> list[str]:
    """What `eid` privately knows of the cases (spec 029's graph): the clues they hold (each node's full fact) and
    whether they are a case's subject. Never shown to the DM unless the secrets arm is on."""
    from engine.gen.case import cases

    out: list[str] = []
    for c in cases(st).values():
        if (c.get("solution") or {}).get("subject", {}).get("id") == eid and not c["nodes"][0].get("found"):
            out.append(f"they are the one the matter turns on: {_flat(c.get('about') or c['nodes'][0]['fact'], 200)}")
        for n in c["nodes"]:
            if n.get("found"):
                continue
            if any(p.get("holder") == eid and p.get("status") not in ("lost", "found") for p in n["placements"]):
                out.append(str(n["fact"]))
    return out


def _held_mood(st: Any, eid: str) -> str | None:
    from engine.dm.answer import held

    h = held(st, eid)
    return MOOD.get(str(h["band"]), h["band"]) if h else None


# ------------------------------------------------------------------------------------------- tools


def tool(ctx: TurnContext, t: Turn, call: dict[str, Any]) -> str:
    name = str(call.get("tool") or "")
    fn = {"propose_roll": _propose_roll, "state": _state, "change": _change, "recall": _recall,
          "reveal_clue": _reveal_clue, "mood": _mood, "end_scene": _end_scene}.get(name)
    if fn is None:
        return f"no tool {name!r}"
    made0 = len(t.made)
    try:
        out = fn(ctx, t, call)
    except Exception as e:  # noqa: BLE001 - a tool that fails tells the DM so; it never fails the turn
        out = f"REFUSED: the {name} tool failed: {type(e).__name__}: {_flat(e, 200)}"
    if len(t.made) > made0:
        out += "\n(New on record, here now: " + "; ".join(t.made[made0:]) + ". Use these ids from now on.)"
    if out.startswith("REFUSED"):
        row = {"tool": name, "kind": str(call.get("kind") or ""), "args": _args(call), "why": out[:200]}
        # [spec 032 P3] one revision, then drop: a second breach of the same tool (or one with no call left to revise
        # it in) is logged; the turn goes on without it
        if any((r["tool"], r["kind"]) == (name, row["kind"]) for r in t.stats["refusals"]) \
                or t.stats["tool_calls"] + 1 >= MAX_TOOLS:
            t.stats["dropped"].append(row)
            out += "\nDROPPED: this call is not done; carry on without it."
        t.stats["refusals"].append(row)
    return out if len(out) <= OUT_CHARS else out[:OUT_CHARS] + "…"


def _id(st: Any, raw: Any) -> str | None:
    """An entity id from what the DM wrote: the id itself, else a unique name match."""
    s = str(raw or "").strip()
    if not s or s.lower() in ("none", "null", "world", "-"):
        return None
    if s in st.entities:
        return s
    low = s.lower()
    hits = [i for i, e in st.entities.items() if e.name.lower() == low and i not in st.seals]
    return hits[0] if len(hits) == 1 else s


_ID_LIKE = re.compile(r"^[a-z_]+\.[a-z0-9_.]+$")
_NAME = re.compile(r"(?![Tt]he\s|[Aa]n?\s|[Ss]ome\s|[Oo]ne\s|[Tt]his\s|[Tt]hat\s)[A-Z]")  # a capitalised name, not an article
_PC_WORDS = re.compile(r"^(pc|the pc|you|the player|player)$")  # the DM's words for the player character


def _squash(raw: Any) -> str:
    return re.sub(r"\s+", " ", str(raw or "").strip().lower())


def target_kinds(rules: Any, verb: str | None) -> tuple[str, ...]:
    """What a verb's target can be, read from its rules entry (basic_verbs.yaml): "person" and/or "object", the kind
    named first in the `targets` knob, else in `against`/`eligibility`, first. A verb with no target slot gives ()."""
    entry = rules.basic_verbs.get(verb) if verb else None
    if not isinstance(entry, dict):
        return ()
    a = entry.get("anchor") or {}
    knob = next((k for k in a.get("knobs", []) if k.get("knob") == "targets"), {})
    kinds: list[str] = []
    for seg in (str(knob.get("default") or ""), str(a.get("against") or ""), str(a.get("eligibility") or "")):
        hits = sorted((m.start(), k) for k, rx in (("person", _PERSON_KIND), ("object", _THING_KIND))
                      if (m := rx.search(seg)))
        kinds += [k for _, k in hits if k not in kinds]
    return tuple(kinds)


def target_is_person(rules: Any, verb: str | None, change_kind: str | None) -> bool:
    """Is a target the DM names (and that is not on record) a person? From the verb's kinds; for a verb that takes
    both, the first slot of the DM's `change_kind` (resolution.yaml: `persuade_to`, `restrain`, `free` take a person;
    `open`, `close`, `take`, `give`, `make` a thing) decides, else the kind the verb names first."""
    kinds = target_kinds(rules, verb)
    if len(kinds) == 2:
        slots = ((rules.resolution["intended_change"]["kinds"].get(change_kind or "") or {}).get("slots") or [""])
        if slots[0] == "person" or slots[0].startswith(("thing", "item")):
            return slots[0] == "person"
    return kinds[:1] == ("person",)


def _party(ctx: TurnContext, t: Turn, raw: Any, *, person: bool = False, names_ok: bool = False) -> str | None:
    """A person or creature from what the DM wrote [spec 032 G4, P8a]. An exact id (or the exact name, or the id the DM
    chose for a `new_npc` this turn) is that entity. Anything else is the DM naming someone new: when the slot takes a
    person (`names_ok`: a capitalised name does too) or the words are a creature's, a walk-on is made at the scene's
    place with the DM's words as its description, and `t.made` tells the DM its id. No name, role or head-noun
    matching: the DM maps "the horseman" to an id from the situation. A thing in words is returned as written."""
    from engine.dm.mentions import bare
    from engine.dm.npc_layer import ANIMAL
    from engine.retrieve.scene import pc_id

    tx = ctx.need_tx()
    st = tx.state
    if _PC_WORDS.match(_squash(raw)) and pc_id(st):  # the DM's words for the player character
        return pc_id(st)
    s = str(raw or "").strip()
    eid = _id(st, t.aliases.get(s, raw))
    if eid is None or eid in st.entities:
        return eid
    words = s
    if _ID_LIKE.match(s):  # an id the DM made up: its words say who or what it is
        prefix, _, tail = s.partition(".")
        words, person = tail.replace("_", " ").replace(".", " "), prefix in ("npc", "companion", "adversary")
    place = st.scene.place_id if st.scene is not None else None
    creature = bool(ANIMAL.match(bare(words).lower()))
    if not (person or creature or (names_ok and _NAME.match(words))) or place not in st.entities:
        return words
    new = _walk_on(ctx, words, place)  # type: ignore[arg-type]
    t.aliases[s] = new  # the same words again in this turn are the same person
    t.made.append(f"{words} ({new})")
    return new


def _walk_on(ctx: TurnContext, words: str, place: str) -> str:
    """A minimal walk-on at `place` described by the DM's words: a creature (`mind: animal`, no rolled person), a named
    person (the name given), else a walk-on with that role (PR-12-5). Never reuses anyone."""
    from engine.dm.mentions import Mention, bare, write_mentions
    from engine.dm.npc_layer import ANIMAL
    from engine.world.social import meet_npc

    tx = ctx.need_tx()
    label = bare(words)
    if ANIMAL.match(label.lower()):
        eid = ids.entity_id("npc", label, tx.state.entities)
        tx.add(Event.of("entity_created", source="engine", rule_id="PR-00-7", entity=EntityRecord(
            id=eid, kind="npc", name=label, visibility="shown",
            data={"mind": "animal", "role": label, "name_known": False, "home": place})))
        tx.add(Event.of("position_set", source="engine", rule_id="PR-00-7", entity=eid, location=place))
        return eid
    if _NAME.match(words):
        res = write_mentions([Mention(kind="npc", name=words)], tx=tx, rules=ctx.rules, rng=ctx.rng, place=place)
        found = res.created.get(words) or res.reused.get(words)
        if found:
            return found
    return meet_npc(ctx.time_ctx(), label, place, alias=label, reuse=False)


def _acting(st: Any, eid: str | None, *, here: bool = True, down: bool = True) -> str:
    """Why `eid` cannot act now (unknown, dead, down, gone or not here), or ""."""
    from engine.harm.state import DEAD, harm_state, is_down
    from engine.retrieve.scene import pc_id
    from engine.world.scenes import cast_present

    if eid is None or eid not in st.entities:
        return f"no one on record called {eid!r}"
    e = st.entities[eid]
    if e.exists != "exists" or harm_state(st, eid) == DEAD:
        return f"{_name(st, eid)} is dead or gone"
    if down and (is_down(st, eid) or st.fact_value(eid, "defeated")):
        return f"{_name(st, eid)} is down and cannot act"
    if here and eid != pc_id(st) and st.scene is not None and eid not in cast_present(st):
        return f"{_name(st, eid)} is not here"
    return ""


def _propose_roll(ctx: TurnContext, t: Turn, c: dict[str, Any]) -> str:
    from engine.dm.turn import _take
    from engine.resolve.pipeline import BeatPlan, run_beats
    from engine.resolve.types import Beat, Change

    tx = ctx.need_tx()
    st = tx.state
    pc = t.rec.pc
    if not pc:
        return "REFUSED: no player character"
    if st.open_pause() is not None:
        return "REFUSED: a roll is already offered this turn"
    verb = str(c.get("verb") or "") or None
    kinds = target_kinds(ctx.rules, verb)
    target = _party(ctx, t, c.get("target"), person=target_is_person(ctx.rules, verb, str(c.get("change_kind") or "")),
                    names_ok="person" in kinds)
    stated = str(c.get("target") or "").strip()
    if target is not None and target not in st.entities:
        if "person" in kinds and "object" not in kinds:  # a person the game could not put here (no place open)
            return (f"REFUSED: no one on record called {target!r} (use an id from the situation, or none)")
        # [spec 032 P8a] a feature or obstacle in words (the stuck hatch): the act is on it, never refused
        target = None
        if not str(c.get("change_what") or "").strip():
            c = {**c, "change_what": stated if not _ID_LIKE.match(stated) else stated.partition(".")[2].replace("_", " ")}
    if target is not None and st.entities[target].kind in ("npc", "companion", "adversary"):
        why = _acting(st, target, down=False)  # a downed foe can still be struck; the dead and the absent cannot
        if why:
            return f"REFUSED: {why}"
    kind = str(c.get("change_kind") or "none")
    raw_t = str(c.get("target") or "").strip()
    what, whom = (target if raw_t and str(c.get(k) or "").strip() == raw_t else _id(st, c.get(k))
                  for k in ("change_what", "change_whom"))
    goal = str(c.get("goal") or "").strip() or "act"
    how = str(c.get("how") or "").strip() or None
    phrase = str(c.get("change_what") or "").strip()
    if kind == "none" and target is None and verb not in ("verb.sneak", "verb.talk"):
        # no slot named: the verb's plain goal toward the DM's words, never "here" by default (the OFFER's title
        # read "Learn about the gate" for tracks on the road past it: fighter smoke 145810)
        from engine.resolve.change import _VERB_GOAL

        kind = _VERB_GOAL.get(str(verb), "none")
    change = None
    if kind != "none":
        if kind in ("harm", "restrain") and what not in st.entities:
            what = target
        if what not in st.entities and target is None and not phrase:
            phrase = goal[:1].lower() + goal[1:]
        change = Change(kind=kind, what=what if what in st.entities else None,
                        whom=whom if whom in st.entities else None,
                        description=None if what in st.entities else (phrase or None))
    method = how or goal
    if c.get("nonlethal") and verb in ("verb.strike", "verb.grapple", "verb.force"):
        method += " (nonlethal)"  # the harm rules read the method's words (engine/resolve/conflict.py NONLETHAL)
    beat = Beat(id=tx.mint(ids.BEAT), actor=pc, intent=goal, method=method, how=how, target=target,
                restatement=goal[:1].upper() + goal[1:], verb=verb,
                title=goal[:1].upper() + goal[1:] if str(c.get("goal") or "").strip() else None, speech=verb == "verb.talk",
                against_will=bool(target and st.entities[target].kind in ("npc", "adversary")
                                  and verb in ("verb.strike", "verb.grapple", "verb.force")),
                declared_seq=st.last_seq, change=change)
    t.env.proposal = c  # what the code framer reads (difficulty, attribute, stakes)
    res = run_beats(t.env, [BeatPlan(beat=beat, intent_verbs=[str(verb or "").removeprefix("verb.")])])
    _take(t.rec, res, t.oof, None)
    t.beats += res.outcomes
    t.stats["rolls"].append({"goal": goal, "verb": verb, "status": [o.status for o in res.outcomes]})
    out = res.outcomes[-1] if res.outcomes else None
    if out is None:
        return "nothing happened (no beat ran)"
    e = out.entry
    if out.status == "paused":
        t.paused = True
        offer = (tx.state.open_pause().detail or {}).get("offer") or {}  # type: ignore[union-attr]
        odds = (offer.get("odds") or {}).get("success_or_better") if isinstance(offer, dict) else None
        return ("ROLL OFFERED to the player" + (f" (about {odds}% to succeed)" if odds is not None else "")
                + ". The turn pauses here: write only the lead-up, never the outcome.")
    if out.status == "no_roll":
        return f"NO ROLL NEEDED ({e.gate_words}): it happens." + (f" Recorded: {e.change}" if e.change else "")
    if out.status == "resolved":
        return "ROLLED (a safe roll, made at once): " + _outcomes_text(ctx, t.rec, t.oof)
    return f"NOT POSSIBLE AS PROPOSED ({out.status}): {e.gate_words}"


def code_framer(ctx: TurnContext, t: Turn) -> Any:
    """The pipeline's FramerFn with no model call: the rule's default frame (engine/dm/roles/framer.py), adjusted by
    the DM's typed proposal (attribute, difficulty tier, stakes) where the rules accept it; else the plain default."""
    from engine.dm.roles.framer import default_frame, to_proposed
    from engine.dm.schemas import build_schema, schema_context
    from engine.resolve.frame import frame_check
    from engine.retrieve.scene import focus_ids

    def propose(beat: Any, candidates: list[str], *, gate: Any, note: str | None = None) -> Any:
        st = ctx.state
        sctx = schema_context(st, ctx.rules, anchors=candidates, beat=beat, message=beat.intent,
                              focus=focus_ids(st, beat.intent, beat.target))
        schema = build_schema(Role.FRAMER, sctx)
        base = default_frame(sctx, schema, beat, st, ctx.rules)
        p = dict(getattr(t.env, "proposal", None) or {})
        d = json.loads(json.dumps(base))
        attrs = ((schema["properties"].get("attribute") or {}).get("enum")) or []
        a = str(p.get("attribute") or "").lower()
        hit = next((x for x in attrs if x.lower() == a or x.lower().endswith("." + a)), None)
        if hit:
            d["attribute"] = hit
        ob = d.get("obstacle") or {}
        tier = str(p.get("difficulty") or "").lower().replace(" ", "_")
        if ob.get("kind") == "tier" and ob.get("obstacle_class") == "other" and tier in sctx.dc_tiers:
            ob["tier"] = tier
        stakes = str(p.get("stakes") or "safe")
        cands = []
        fc = str(p.get("fail_cost") or "")
        fc = fc if fc.startswith("cost.") or not fc else f"cost.{fc}"
        # the DM's own `fail_cost` first (when the rules' menu has it), then the verb's plain risk (spec 032 G8)
        wants = [w for w in dict.fromkeys((fc, PREFERRED_COST.get(str(beat.verb), ""))) if w]
        if stakes != "safe" and sctx.stakes_menus:  # the first stakes source the rules accept here (01.6.9)
            for want in wants or [""]:
                for src, m in sctx.stakes_menus.items():
                    if src != "none" and m["threatened"] and m["alternate"] and (want in m["threatened"] or not cands):
                        # ponytail: the cost a verb most plainly risks (a fight risks harm, a sneak being noticed)
                        threat = want if want in m["threatened"] else m["threatened"][0]
                        alt = next((x for x in m["alternate"] if x != threat), m["alternate"][0])
                        cands.append({**d, "stakes_heavy": stakes == "dire", "stakes": {
                            "source": src, "threatened_cost": {"menu_id": threat, "form_intent": "",
                                                               "source_fact": None},
                            "alternate_cost": {"menu_id": alt, "form_intent": "", "source_fact": None}}})
        for cand in (*cands, d, base):
            try:
                prop = to_proposed(cand, beat, st)
            except (KeyError, ValueError):
                continue
            chk = frame_check(prop, beat, state=st, rules=ctx.rules, gate=gate, candidates=candidates,
                              store=ctx.store, staged=ctx.need_tx().events)
            if not hasattr(chk, "step") or cand is base:
                return prop
        return to_proposed(base, beat, st)

    return propose


def _state(ctx: TurnContext, t: Turn, c: dict[str, Any]) -> str:
    from engine.dm.fixer import _entity_tool, sheet_line
    from engine.dm.oof import when_words
    from engine.resolve.change import holder_of
    from engine.retrieve.scene import pc_id

    st = ctx.state
    about = str(c.get("about") or "pc").strip()
    pc = pc_id(st)
    if about.lower() in ("pc", "me", "sheet", "inventory", "coin", "conditions", "") or about == pc:
        held = [i for i, e in st.entities.items() if e.kind in ("item", "object", "clue") and holder_of(st, i) == pc]
        conds = [f"{x.condition_id}" + (f" {x.severity}" if getattr(x, "severity", None) else "")
                 for x in st.conditions_on(pc or "")]
        return "\n".join([f"{_name(st, pc)} ({pc}): {sheet_line(st, ctx.rules, pc)}",
                          "carries: " + (", ".join(f"{_name(st, i)} ({i})" for i in held) or "nothing"),
                          "conditions: " + (", ".join(conds) or "none")])
    if about.lower() in ("time", "now", "when"):
        return f"{when_words(st.time.now)}; mode {st.time.mode}"
    if about.lower() in ("here", "place", "scene"):
        return situation(ctx)
    return _entity_tool(ctx, _id(st, about) or about)


def _recall(ctx: TurnContext, t: Turn, c: dict[str, Any]) -> str:
    from engine.dm.codex import what_you_know
    from engine.dm.fixer import _said_tool, _search_tool

    q = str(c.get("query") or "")
    st = ctx.state
    known = what_you_know(st, q or None, ctx.rules).text
    who = _id(st, q)
    said = _said_tool(ctx, who) if who in st.entities else ""
    return "\n".join(x for x in ("PAST TURNS AND RECORD:\n" + _search_tool(ctx, q),
                                 said and "SAID:\n" + said, "THE CHARACTER KNOWS:\n" + _flat(known, 700)) if x)


def _reveal_clue(ctx: TurnContext, t: Turn, c: dict[str, Any]) -> str:
    from engine.dm.answer import _from_case, clue_judgment
    from engine.dm.player_text import clean

    st = ctx.state
    npc = _party(ctx, t, c.get("npc"), person=True)
    why = _acting(st, npc)
    if why:
        return f"REFUSED: {why}"
    assert npc is not None
    q = str(c.get("question") or "").strip()
    if not q:
        return "REFUSED: give the question as asked"
    case, _ = clue_judgment(ctx, npc, [q])
    if case is None:
        return "NO CLUE: the question touches no open clue. Answer in their own words, from what they would know."
    a = _from_case(ctx, npc, case, False, t.rec.pc or "", False)
    if a is None:
        return "NO CLUE TO GIVE: they have nothing more on it. Answer in their own words."
    learned = clean(a.learned or a.said, ctx.rules)
    t.stats["clues"].append({"npc": npc, "learned": learned[:200]})
    if a.pointer:
        return f"POINTER: {_name(st, npc)} doesn't know, but points the player on. Deliver: {learned}"
    return f"CLUE (deliver it plainly, in their voice; the player now knows it): {learned}"


def _mood(ctx: TurnContext, t: Turn, c: dict[str, Any]) -> str:
    """The DM decides a person's mood toward the character and the game remembers it for the scene (the held band,
    answers.willingness); it may change it when the fiction does. No roll, no ceiling [owner ruling 2026-10-10]."""
    from engine.dm.answer import _hold

    st = ctx.state
    npc = _party(ctx, t, c.get("npc"), person=True)
    why = _acting(st, npc)
    if why:
        return f"REFUSED: {why}"
    assert npc is not None
    word = str(c.get("mood") or "").strip().lower()
    if word not in BAND:
        return f"REFUSED: mood is one of {', '.join(BAND)}"
    reason = str(c.get("why") or "").strip() or "the DM's call"
    was = _held_mood(st, npc)
    _hold(ctx, npc, BAND[word], reason)
    t.stats["moods"].append({"npc": npc, "was": was, "mood": word, "why": reason[:160]})
    return f"done: {_name(st, npc)} is {word} toward the character for this scene (a memory; change it when the fiction does)."


def _end_scene(ctx: TurnContext, t: Turn, c: dict[str, Any]) -> str:
    """The DM ends the scene [owner ruling 2026-10-10]. Code does the bookkeeping only: the scene_end handlers (time,
    per-scene resets: held moods, dead air) and the new scene record here. No cut rule asks for it."""
    from engine.resolve.conflict import record as conflict

    st = ctx.state
    if st.scene is None:
        return "REFUSED: no scene is open"
    if st.open_pause() is not None:
        return "REFUSED: a roll is offered; the scene cannot end under it"
    if conflict(st):
        return "REFUSED: a fight is on; the scene ends when the fight does"
    _open_scene(ctx, "player_cut")
    t.stats["scene_ends"].append(str(c.get("why") or "")[:160])
    return "done: that scene ends and a new one opens here (moods you set last scene are cleared; set them again if they matter)."


def _asks(ctx: TurnContext, t: Turn, asks: list[Any]) -> None:
    """Log each ask the DM says it granted or refused, with the mood it holds for that person (an observation for the
    owner to read: costly asks granted; never a gate, never blocks) [owner ruling 2026-10-10]."""
    st = ctx.state
    for a in asks:
        if not isinstance(a, dict):
            continue
        npc = _id(st, a.get("npc"))
        if npc not in st.entities or _acting(st, npc):
            continue
        t.stats.setdefault("asks", []).append({"npc": npc, "mood": _held_mood(st, npc), "cost": a.get("cost"),
                                               "granted": str(a.get("granted") or "refuse")})


# ------------------------------------------------------------------------------------------- change


def _change(ctx: TurnContext, t: Turn, c: dict[str, Any]) -> str:
    tx = ctx.need_tx()
    st = tx.state
    kind = str(c.get("kind") or "")
    pc = t.rec.pc or ""
    who, what, to = _id(st, c.get("who")), _id(st, c.get("what")), _id(st, c.get("to"))
    if kind in ("coin", "give_item", "condition_add", "condition_remove", "npc_leaves", "fight", "fact"):
        who = _party(ctx, t, c.get("who"), person=kind != "fact")  # a fact's subject may be a thing: not made
    if kind in ("coin", "give_item", "new_item"):
        to = _party(ctx, t, c.get("to"), person=True)
    amount = int(c.get("amount") or 0)
    if kind == "coin":
        return _coin(ctx, t, payer=who, payee=to, amount=amount)
    if kind == "give_item":
        return _give(ctx, item=what, giver=who or pc, to=to)
    if kind == "new_item":
        from engine.dm.mentions import bare
        from engine.resolve.change import PEOPLE, holder_of

        name = str(c.get("what") or "").strip()
        holder = to or pc
        why = _acting(st, holder)
        if why or not name:
            return f"REFUSED: {why or 'name the item'}"
        twin = next((i for i, e in st.entities.items()
                     if e.kind in ("item", "object") and bare(e.name).lower() == bare(name).lower()
                     and st.entities.get(str(holder_of(st, i))) is not None
                     and st.entities[str(holder_of(st, i))].kind in PEOPLE), None)
        eid = ids.entity_id("item", name, st.entities)
        tx.add(Event.of("entity_created", source="engine", rule_id="00.6.6",
                        entity=EntityRecord(id=eid, kind="item", name=name, visibility="shown")))
        tx.add(_fact(tx, eid, "holder", holder))
        echo = (f"\nNOTE: {_name(st, holder_of(st, twin))} already holds {_name(st, twin)} ({twin}); if you meant "
                f"that one, use give_item with it instead of a second {name}.") if twin else ""
        return f"done: {name} ({eid}) now held by {_name(tx.state, holder)}" + echo
    if kind in ("condition_add", "condition_remove"):
        return _condition(ctx, who, str(c.get("what") or ""), add=kind == "condition_add", pc=pc)
    if kind == "fight":
        return _fight(ctx, who, pc)
    if kind == "npc_leaves":
        why = _acting(st, who)
        if why:
            return f"REFUSED: {why}"
        assert who is not None
        from engine.world.places import location, reachable

        here = location(st, who) or (st.scene.place_id if st.scene else None)
        dest = to if to in st.entities and st.entities[to].kind == "place" else next(
            (x.to for x in reachable(st, here) if x.to != here), None) if here else None
        if dest is None:
            return "REFUSED: nowhere on record for them to go (name a place id in `to`)"
        tx.add(Event.of("position_set", source="engine", rule_id="12.4.1", entity=who, location=dest))
        return f"done: {_name(st, who)} leaves for {_name(st, dest)}"
    if kind == "new_npc":
        from engine.world.social import meet_npc

        place = st.scene.place_id if st.scene else None
        role = str(c.get("what") or "").strip() or None
        eid = meet_npc(ctx.time_ctx(), role, place, reuse=False)
        if _ID_LIKE.match(str(c.get("who") or "").strip()):  # [spec 032 P8a] the DM's own id for them, used next call
            t.aliases[str(c["who"]).strip()] = eid
        card = __import__("engine.dm.packet", fromlist=["people_card"]).people_card(ctx.state, eid, rules=ctx.rules)
        return f"done: someone new is here: {eid}: " + "; ".join(x.strip() for x in card[:3])
    if kind == "travel":
        return _travel(ctx, t, to, str(c.get("who") or ""))
    if kind == "rest":
        from engine.dm.turn import REST_WORDS, _rest

        rk = str(c.get("what") or "rest_short")
        rk = rk if rk in REST_WORDS else "rest_short"
        before = len(t.oof)
        _rest(ctx, t.rec, rk, t.oof)
        refused = [o["text"] for o in t.oof[before:] if o.get("kind") == "NOTE"]
        return f"REFUSED: {refused[0]}" if refused else f"done: {t.rec.notes[-1] if t.rec.notes else rk}"
    if kind == "fact":
        subj = who if who in st.entities else "world"
        pred = ids.slug(str(c.get("what") or ""))[:50]
        if not pred:
            return "REFUSED: name the fact in `what`"
        if who is not None and who not in st.entities:
            return f"REFUSED: no one or nothing on record called {who!r}"
        tx.add(_fact(tx, subj, pred, str(c.get("note") or True), source="narration", visibility="shown"))
        return f"done: recorded {pred} for {_name(st, subj) if subj != 'world' else 'the world'}"
    return f"REFUSED: unknown change kind {kind!r} (one of {', '.join(CHANGES)})"


def _fact(tx: Any, subject: str, predicate: str, value: Any, *, source: str = "ruling",
          visibility: str = "shown") -> Event:
    from engine.world.common import fact

    return fact(tx, subject, predicate, value, rule_id="01.2.7", source=source, visibility=visibility)


def _coin(ctx: TurnContext, t: Turn, *, payer: str | None, payee: str | None, amount: int) -> str:
    """Coin moves from a payer to a payee (economy AI-6: coin never comes from nowhere). A purse on record is
    debited and never goes below 0; a person with no purse on record (an NPC) pays from their own means."""
    tx = ctx.need_tx()
    st = tx.state
    if amount <= 0:
        return "REFUSED: give a positive amount"
    if payer is None:
        return "REFUSED: coin from no source (name who pays in `who`)"
    why = _acting(st, payer)
    if why:
        return f"REFUSED: {why}"
    if payee is None or payee not in st.entities:
        return f"REFUSED: no one on record called {payee!r} to receive it"
    if _acting(st, payee, here=False).endswith("dead or gone"):
        return f"REFUSED: {_name(st, payee)} is dead or gone"
    evs = []
    for eid, delta in ((payer, -amount), (payee, amount)):
        q = st.quantities.get(eid, {}).get("coin")
        if q is None:
            if eid == t.rec.pc:
                return "REFUSED: the character has no purse on record"
            continue
        if q.current + delta < 0:
            return f"REFUSED: {_name(st, eid)} has only {q.current} coin"
        evs.append(Event.of("quantity_changed", source="engine", rule_id="01.11.2", entity=eid, quantity="coin",
                            delta=delta, new_value=q.current + delta, reason="coin changes hands (DM)"))
    tx.add_all(evs)
    left = tx.state.quantities.get(t.rec.pc or "", {}).get("coin")
    return f"done: {amount} coin from {_name(st, payer)} to {_name(st, payee)}" + (
        f"; the character now has {left.current}" if left is not None else "")


def _give(ctx: TurnContext, *, item: str | None, giver: str, to: str | None) -> str:
    """An item changes hands: the giver must hold it (or it lies loose here) and be able to act; the receiver must
    be alive and here."""
    from engine.resolve.change import PEOPLE, THINGS, holder_of

    tx = ctx.need_tx()
    st = tx.state
    if item is None or item not in st.entities or st.entities[item].kind not in THINGS:
        return f"REFUSED: no item on record called {item!r} (use new_item for something new)"
    holder = holder_of(st, item)
    if holder in st.entities and st.entities[holder].kind in PEOPLE and holder != giver:  # type: ignore[index]
        return f"REFUSED: {_name(st, item)} is not {_name(st, giver)}'s to give; {_name(st, holder)} has it"
    why = _acting(st, giver)
    if why:
        return f"REFUSED: {why}"
    why = _acting(st, to)
    if why:
        return f"REFUSED: {why}"
    assert to is not None
    tx.add(_fact(tx, item, "holder", to))
    return f"done: {_name(st, to)} now holds {_name(st, item)}"


HARM_OWNED = ("cond.wound_arm", "cond.wound_body", "cond.wound_head", "cond.wound_leg", "cond.unconscious")


def _fight(ctx: TurnContext, who: str | None, pc: str) -> str:
    """A person the DM has turn on the PC: the conflict starts (spec 032 G7). No foe action here (the world step runs
    it); nothing is done to the PC without a roll or the foe's own turn."""
    from engine.resolve import conflict

    tx = ctx.need_tx()
    why = _acting(tx.state, who)
    if why:
        return f"REFUSED: {why}"
    assert who is not None
    if not conflict.start(ctx.time_ctx(), pc, [who], f"the DM: {_name(tx.state, who)} turns on the character"):
        return f"{_name(tx.state, who)} is already in the fight (or cannot be a foe)."
    return (f"done: a fight begins; {_name(tx.state, who)} turns on the character. Blows are not struck by your words: "
            "the game has them act when your turn ends and tells you what lands. Write the lead-up only; the "
            "character's reply is a roll.")


def _condition(ctx: TurnContext, who: str | None, cid: str, *, add: bool, pc: str = "") -> str:
    from engine.store.conditions import apply_condition, remove_condition

    tx = ctx.need_tx()
    st = tx.state
    if who is None or who not in st.entities:
        return f"REFUSED: no one on record called {who!r}"
    cid = cid if cid.startswith("cond.") else f"cond.{ids.slug(cid)}"
    if cid not in ctx.rules.ids("cond."):
        return f"REFUSED: no condition {cid!r} in the rules (e.g. {', '.join(ctx.rules.ids('cond.')[:8])})"
    if cid in HARM_OWNED:
        return f"REFUSED: {cid} comes from harm (a blow or a roll sets it); the DM does not add or lift it"
    if add and who == pc:
        return "REFUSED: nothing is done to the character without a roll or a foe's turn (no condition from the DM)"
    if add:
        res = apply_condition(st, tx.mint, ctx.rules, who, cid, source={"kind": "dm"})
        tx.add_all(res.events)
        return f"done: {cid} on {_name(st, who)} ({res.outcome})"
    found = [i for i in st.conditions_on(who) if i.condition_id == cid]
    if not found:
        return f"REFUSED: {_name(st, who)} has no {cid}"
    for inst in found:
        tx.add_all(remove_condition(st, ctx.rules, inst.instance_id, "ended in the fiction (DM)").events)
    return f"done: {cid} ends on {_name(st, who)}"


def _along(st: Any, raw: str) -> tuple[list[str], list[str]]:
    """Who the DM says walks with the character [spec 032 P8a]: ids, one or a comma list. Returns the ones who can
    come (here, alive, up) and a line for each who cannot. Nobody is guessed: only those named, by id."""
    ok: list[str] = []
    stay: list[str] = []
    for p in (x.strip() for x in re.split(r"\s*[,;]\s*", raw)):
        if not p or _PC_WORDS.match(_squash(p)):
            continue
        eid = _id(st, p)
        why = _acting(st, eid)
        if why:
            stay.append(why)
        elif eid not in ok:
            ok.append(str(eid))
    return ok, stay


def _travel(ctx: TurnContext, t: Turn, to: str | None, along: str = "") -> str:
    from engine.world.places import location, move, reachable

    st = ctx.state
    here = location(st)
    ways = {x.to for x in reachable(st, here)} if here else set()
    if to not in ways:
        return f"REFUSED: {to!r} is not reachable from here (reachable: {', '.join(sorted(ways)) or 'none'})"
    assert to is not None
    who, stay = _along(st, along.strip())
    arrival = move(ctx.time_ctx(), to, end_scene=True)
    if arrival.arrived:  # the named walk with the character; the rest stay where they were
        for eid in who:
            ctx.need_tx().add(Event.of("position_set", source="engine", rule_id="10.1.1", entity=eid, location=to))
    _open_scene(ctx)
    return (f"done: the character travels to {_name(ctx.state, to)}" + ("" if arrival.arrived else
                                                                         " (interrupted on the way)")
            + (f"\nWith the character: {', '.join(_name(ctx.state, e) for e in who)}." if who and arrival.arrived else "")
            + "".join(f"\nDid not come: {why}." for why in stay)
            + "\n" + situation(ctx))


def _open_scene(ctx: TurnContext, reason: str = "player_cut") -> None:
    """A scene at the PC's place when none is open (no Director: no agenda; the DM frames it in words). Its time mode
    is `site` (a fight in progress keeps `conflict`): an exchange is an interval (spec 032 A1, dm_world.ensure_site)."""
    from engine.world.places import location
    from engine.world.scenes import end_scene, start_scene

    st = ctx.state
    place = location(st) or (st.last_scene.place_id if st.last_scene else None)
    from engine.time import clock

    if st.scene is not None:
        end_scene(ctx.time_ctx(), reason)
    start_scene(ctx.time_ctx(), place=place, agenda="",
                mode="conflict" if clock.mode_of(ctx.state.time.mode) == "conflict" else "site")


def _sync_scene(ctx: TurnContext, t: Turn) -> None:
    """The scene follows the PC: a PC whose place is not the scene's gets a new scene there (12.4.2 (2))."""
    from engine.world.places import location

    st = ctx.state
    here = location(st)
    if st.open_pause() is None and st.scene is not None and here and st.scene.place_id != here:
        _open_scene(ctx)


# ------------------------------------------------------------------------------------------- audit


def _outcomes_text(ctx: TurnContext, rec: AdjudicationRecord, oof: list[dict[str, str]]) -> str:
    lines = []
    for b in rec.beats:
        bits = [b.restatement or "", b.degree or b.gate_words or ""]
        if b.success_at_cost:
            bits.append("success at a cost")
        if b.change:
            bits.append(str(b.change))
        lines.append(" · ".join(x for x in bits if x))
    lines += [o["text"] for o in oof if o.get("kind") in ("RESULT", "LAST_CHANCE", "NOTE")]
    return "\n".join(lines) or "nothing resolved"


_WORD = re.compile(r"[a-z][a-z']{3,}")
_STOPS = frozenset("that this with from have they them then into were your there about what when which would "
                   "their been being because while where whom".split())


def _content(text: str, drop: frozenset[str] = frozenset()) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOPS and w not in drop}


def _name_tokens(st: Any) -> frozenset[str]:
    """Every word of every entity's name, display name and aliases: a name in the passage and in a secret is not a
    leak (spec 032 G9: the 10 false flags were a person's name plus "matter")."""
    toks: set[str] = set()
    for eid, e in st.entities.items():
        for n in (e.name, _name(st, eid), *[a for a in e.data.get("aliases", []) if isinstance(a, str)]):
            toks |= set(_WORD.findall(str(n or "").lower()))
    return frozenset(toks)


def _audit(ctx: TurnContext, t: Turn, passage: str) -> None:
    """Secret leaks (measured, never blocked): a present person's private case fact whose content words (names
    removed) mostly appear in the passage, when no clue tool delivered it this turn."""
    from engine.world.scenes import cast_present

    st = ctx.state
    names = _name_tokens(st)
    said = _content(passage, names)
    delivered = " ".join(c["learned"] for c in t.stats["clues"]).lower()
    for eid in cast_present(st) if st.scene is not None else []:
        for s in secrets(st, eid):
            body = s.split(":", 1)[-1]
            words = _content(body, names)
            if len(words) >= 3 and len(words & said) / len(words) >= 0.6 and body.strip().lower()[:40] not in delivered:
                t.stats["leaks"].append({"npc": eid, "secret": s[:200]})


# ------------------------------------------------------------------------------------------- told, and the log-only checks


def _told(ctx: TurnContext, t: Turn, passage: str) -> None:
    """What people said, as testimony (spec 032 G3): each `said` entry becomes a record on the speaker (place and day),
    shown in the journal as "what you were told"; never a world fact. Dropped and logged (`told_dropped`), never
    written: a speaker that is unknown, dead, gone or not here; words not in the passage; a line the speaker already
    said; a line that is the clue `reveal_clue` delivered (that is a learned fact). The character's own words, and an
    empty line, are skipped without a log."""
    from engine.audit import text as atx
    from engine.dm import testimony
    from engine.retrieve.scene import pc_id

    st, rules = ctx.state, ctx.rules
    limit = float((((rules.pacing.get("narration") or {}).get("freshness") or {}).get("said_overlap")) or 0.6)
    clues = " ".join(c["learned"] for c in t.stats["clues"])
    keep: list[dict[str, Any]] = []
    for e in [x for x in t.said_raw if isinstance(x, dict)][:SAID_MAX]:
        words, raw = str(e.get("words") or "").strip(), str(e.get("npc") or "")
        who = _id(st, t.aliases.get(raw.strip(), raw))
        if not words or who == pc_id(st) or _PC_WORDS.match(_squash(raw)):
            continue
        if who not in st.entities and atx.covers(words, passage, ratio=0.8):
            who = _party(ctx, t, raw, person=True)  # [spec 032 P8a] not an id on record: the DM names a new walk-on
        why = (_acting(st, who, down=False)
               or ("the words are not in the passage" if not atx.covers(words, passage, ratio=0.8) else "")
               or ("said before" if testimony.is_repeat(st, rules, who, words)
                   or any(k["speaker"] == who and testimony.overlap(words, k["words"]) > limit for k in keep) else "")
               or ("delivered as a clue" if clues and testimony.overlap(clues, words) > limit else ""))
        if why:
            t.stats["told_dropped"].append({"npc": raw[:60], "why": why, "words": words[:80]})
        else:
            keep.append({"speaker": who, "turn": ctx.turn_id, "words": words, "about": [who], "question": None})
    for sid, k in zip(testimony.add_said(ctx, keep), keep, strict=True):
        t.stats["said"].append({"id": sid, "speaker": k["speaker"], "words": k["words"][:120]})
    t.told = keep


_GIVEN = r"(?:hands|gives|passes|slides|tosses|throws|presses|pushes|presents)"
_GIVE = re.compile(rf"\b{_GIVEN}\s+you\s+(?:an?|the|some|two|three|his|her|their)\s+([a-z'-]+(?:\s[a-z'-]+)?)|"
                   rf"\b{_GIVEN}\s+(?:an?|the|some|two|three|his|her|their)\s+([a-z'-]+(?:\s[a-z'-]+)?)"
                   r"\s+(?:into|to|across|over)\s+your\b", re.IGNORECASE)
_MOVES = ("give_item", "new_item", "coin")


def _log_only(ctx: TurnContext, t: Turn, passage: str, message: str, exchanges: list[tuple[str, str]],
              lead: str) -> None:
    """The checks that only log (spec 032 FR-09, DL-12-138): none returns anything the turn uses, so none can change or
    block the passage. `pronoun` (a named person's sentence uses the other pronoun than the record's), `absent_named`
    (a person who is neither here nor in the recent talk, tools or this turn's lead), `item_unbacked` (a thing handed
    over with no give_item, new_item or coin call that worked this turn). Precision is measured by hand
    (evals/baselines/log_only_032.md); none is promoted here."""
    from engine.audit.claims import _QUOTE_RE, _pronoun_hit
    from engine.audit.declare import SceneIndex, name_spans
    from engine.world.scenes import cast_present

    out = t.stats["log_only"]
    try:
        st = ctx.state
        idx = SceneIndex.of(st)
        here = set(cast_present(st)) if st.scene is not None else set()
        talk = " ".join([message, lead, *(f"{i} {o}" for i, o in exchanges),
                         *(f"{a} {b} {o}" for a, b, o in t.log)]).lower()
        backed = any(a == "change" and any(f'"kind": "{k}"' in b for k in _MOVES) and o.startswith("done")
                     for a, b, o in t.log)
        before: list[str] = []
        named: set[str] = set()
        for sent in re.split(r"(?<=[.!?])\s+", passage.strip()):
            narr = _QUOTE_RE.sub(" ", sent)
            if hit := _pronoun_hit(narr, before, idx, ()):
                out.append({"kind": "pronoun", "text": sent[:160], "who": hit[1], "word": hit[0]})
            for _, _, eid in name_spans(narr, idx):
                e = st.entities.get(eid)
                if e is None or e.kind not in ("npc", "companion", "adversary") or eid in here or eid in named:
                    continue
                if not any(re.search(rf"\b{re.escape(n)}\b", talk) for n in idx.aliases.get(eid, [])):
                    named.add(eid)
                    out.append({"kind": "absent_named", "text": sent[:160], "who": eid})
            if not backed and (g := _GIVE.search(narr)):
                out.append({"kind": "item_unbacked", "text": sent[:160], "item": (g.group(1) or g.group(2)).strip()})
            before.append(narr)
    except Exception as e:  # noqa: BLE001 - a log-only check never fails the turn
        out.append({"kind": "check_failed", "text": f"{type(e).__name__}: {_flat(e, 120)}"})


def _name(st: Any, eid: str | None) -> str:
    from engine.store.views import display_name

    return display_name(st, eid) if eid and eid in st.entities else str(eid)


def _flat(s: Any, n: int | None = None) -> str:
    x = " ".join(str(s).split())
    return x if n is None or len(x) <= n else x[:n] + "…"


__all__ = ["ENGINE", "MAX_TOOLS", "Outcome", "enabled", "play_answer", "play_turn", "secrets",
           "situation", "step_schema", "tool"]
