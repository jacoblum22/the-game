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
from engine.dm.schemas import BOOL, STR, Schema, arr, enum, obj
from engine.llm.base import Packet, Role, call_role
from engine.store.events import EntityRecord, Event
from engine.store.records import TurnRecord

ENGINE = "dm-tools"
MAX_TOOLS, PER_STEP = 6, 3
SAID_MAX = 6  # the lines a passage may list as said
TOOLS = ("propose_roll", "state", "change", "recall", "reveal_clue", "mood", "end_scene", "end_game")
CHANGES = ("coin", "give_item", "new_item", "condition_add", "condition_remove", "npc_leaves", "new_npc", "travel",
           "rest", "fact", "fight", "position")  # [spec 032 P3] fight: a person turns on the PC; [spec 033] position
AS_KINDS = ("he", "she", "they", "creature", "thing")  # [spec 033] what unrecorded words are: pronouns, or kind
FORCES = ("push", "prone")  # 06.5.3: Force's two options
FOE_ACTS = ("strike", "close_in", "withdraw", "stand", "break_free", "grapple", "flee", "yield", "wait")  # 06.9.4
FAIL_COSTS = ("cost.closed_door", "cost.drain", "cost.exposure", "cost.footing", "cost.gear", "cost.harm",
              "cost.shortfall", "cost.time", "cost.twist")  # the 9 cost ids (a test pins them to the rules)
PRONOUNS = {"he": "he/him", "she": "she/her", "they": "they/them"}  # `as` -> the stored pronouns (12.11.1)
OFF_SCENE = "elsewhere"  # where `npc_leaves` with no place puts someone: off the scene, a place nobody named (D3)
COSTS = ("none", "small", "real", "big")
GRANTS = ("help", "price", "partial", "refuse")  # what the DM had the NPC do for an ask (logged, never gated)
STAKES = ("safe", "risky", "dire")
DM_ROLE = Role.DM  # spec 032 FR-13: its own role (schema, prompt file dm.md, offline heuristic, per-role model)
MOOD = {"willing": "open", "guarded": "guarded", "unwilling": "closed"}  # the held band -> the DM's word
BAND = {v: k for k, v in MOOD.items()}
OUT_CHARS = 1600


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
        "tool_calls": 0, "steps": 0, "refusals": [], "moods": [], "clues": [], "rolls": [], "dropped": [],
        "scene_ends": [], "world": {"foe_turns": [], "facts": [], "reasked": 0, "foe_calls": 0},
        "said": [], "told_dropped": [],
        "defaults": []})  # [spec 033 D3] `not_chosen:{field}`: each detail the DM left out and code defaulted  # [spec 032 P5] the told records, what was dropped, the checks
    said_raw: list[Any] = field(default_factory=list)  # the DM's final-answer `said` list, as written
    told: list[dict[str, Any]] = field(default_factory=list)  # the said entries written (TurnRecord.said's shape)
    beats: list[Any] = field(default_factory=list)  # the BeatOutcomes of this turn (the world step reads their status)
    world_done: bool = False  # the world step runs once per exchange
    cost_form: str = ""  # [spec 033 P3] the footing option the DM picked in its last answer ("" = none)
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
    from engine.resolve import costs
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
                _drain(t)  # [spec 033 D3] what code defaulted while it rolled
                _harm_followups(ctx, t.env, t.rec, t.oof)
                lead = f"The player picked: {label}.\n" + _outcomes_text(ctx, t.rec, t.oof) + _cost_block(ctx.state)
                if costs.pending_footing(tx.state) is None:  # [spec 033 D2] else the foes wait for the DM's cost_form
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
            _footing(ctx, t)  # [spec 033 DL-01-60] a footing still pending (no world step ran) lands here
            _sync_scene(ctx, t)
            if tx.state.open_pause() is None:
                _turn_end(ctx, t.rec, t.oof)
                _harm_followups(ctx, t.env, t.rec, t.oof)
            _told(ctx, t)  # [spec 032 P5] what people said: testimony records
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
    return schema_for(ctx.rules.ids("verb."), list(ctx.rules.resolution["intended_change"]["kinds"]), final=final,
                      approaches=approaches(ctx.rules))


def approaches(rules: Any) -> list[str]:
    """The specialist methods a verb names as needing a licence (basic_verbs.yaml `excludes`, whole entries): the
    values of `propose_roll.approach` besides "plain" (00.12.3)."""
    return list(dict.fromkeys(str(e["what"]) for v in rules.basic_verbs.values() for e in v.get("excludes") or ()))


def schema_for(verbs: list[str], kinds: list[str], *, final: bool, approaches: list[str] | None = None) -> Schema:
    """The DM step's schema (`Role.DM`'s builder in engine/dm/schemas.py calls this with the SchemaContext's lists).
    Every property of an object is required (schemas.obj), so an omitted detail is written as "" / "none" / "plain" /
    false; code then holds the documented default and logs `not_chosen:{field}` [spec 033 D3]."""
    calls = [
        obj({"tool": enum(["propose_roll"]), "goal": STR, "verb": enum(verbs), "target": STR,
             "as": enum(AS_KINDS, first="none"), "how": STR, "attribute": STR, "difficulty": STR, "why_uncertain": STR,
             "stakes": enum(STAKES), "nonlethal": BOOL, "force": enum(FORCES, first="none"), "weapon": STR,
             "reads": BOOL, "approach": enum(approaches or (), first="plain"),
             "fail_cost": enum(["none", *FAIL_COSTS]), "fail_on": STR,
             "change_kind": enum(kinds), "change_what": STR, "change_whom": STR}),
        obj({"tool": enum(["state"]), "about": STR}),
        obj({"tool": enum(["change"]), "kind": enum(CHANGES), "who": STR, "what": STR, "to": STR, "name": STR,
             "as": enum(AS_KINDS, first="none"), "knows": STR, "amount": {"type": "integer"}, "note": STR}),
        obj({"tool": enum(["recall"]), "query": STR}),
        obj({"tool": enum(["reveal_clue"]), "npc": STR, "question": STR}),
        obj({"tool": enum(["mood"]), "npc": STR, "mood": enum(list(BAND)), "why": STR}),
        obj({"tool": enum(["end_scene"]), "why": STR}),
        obj({"tool": enum(["end_game"]), "why": STR}),
    ]
    call = {"anyOf": calls}
    return obj({"calls": arr(call, max_items=0 if final else PER_STEP), "passage": STR,
                "said": arr(obj({"npc": STR, "words": STR, "as": enum(AS_KINDS, first="none")}), max_items=SAID_MAX),
                "asks": arr(obj({"npc": STR, "cost": enum(COSTS), "granted": enum(GRANTS)}), max_items=4),
                "cost_form": STR})  # cost_form: one option id of a COST TO SHAPE line, on the answer turn (P3)


def foe_schema(legal: dict[str, list[str]]) -> Schema:
    """[spec 033 D2] The foe-act call: after the character's result is settled, the DM picks what each foe still able
    to act does. `legal` maps each foe id to the acts legal for it now (`FOE_ACTS` filtered by state, P3); a foe's
    `act` can be nothing else. `target` defaults to the character; `nonlethal` to false."""
    one = [obj({"foe": enum([f]), "act": enum(acts), "target": STR, "nonlethal": BOOL}) for f, acts in legal.items()]
    return obj({"foes": arr({"anyOf": one} if one else STR, max_items=len(one))})


def _paused_note(ctx: TurnContext) -> str:
    """What the DM is told once a tool paused the turn: the open pause is a roll offered, or the retire question."""
    p = ctx.state.open_pause()
    if p is not None and p.kind == "clarify":
        return "The player is asked whether to retire the character: write only a short closing line, never the ending."
    return ("A roll is now offered to the player: write only the lead-up to the attempt (or nothing), never its "
            "outcome.")


def _dm_loop(ctx: TurnContext, t: Turn, message: str, exchanges: list[tuple[str, str]], lead: str) -> str:
    """The bounded tool loop: at most MAX_TOOLS tool calls, PER_STEP per answer, then the passage."""
    made = 0
    data: dict[str, Any] = {}
    for _ in range(MAX_TOOLS + 1):
        final = made >= MAX_TOOLS or t.paused
        note = ("Write the passage now (no tool calls are left)." if final and not t.paused else
                _paused_note(ctx) if t.paused else
                f"You may make up to {MAX_TOOLS - made} more tool call(s), {PER_STEP} per answer; with no calls, "
                "`passage` is delivered.")
        packet = Packet(instructions=load_prompt("dm"), message=_message(ctx, t, message, exchanges, lead, note))
        schema = step_schema(ctx, final=final)
        res = call_role(ctx.model, DM_ROLE, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call,
                        default={"calls": [], "passage": str(data.get("passage") or ""), "said": [], "asks": [],
                                 "cost_form": ""})
        data = dict(res.data or {})
        t.cost_form = str(data.get("cost_form") or "")
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


def foe_message(ctx: TurnContext, t: Turn, legal: dict[str, list[str]]) -> str:
    """[spec 033 D2] The foe call's message: the situation, what just settled, and the FIGHT block with each able foe's
    legal acts."""
    pc = t.rec.pc
    lead = _outcomes_text(ctx, t.rec, t.oof) + "\n" + "\n".join(_fight_block(ctx.state, pc, legal))
    note = ("Choose what each foe listed does now: `act` from its own acts, `target` (an id; empty is the character) "
            "and `nonlethal`. Write no passage.")
    return _message(ctx, t, "", [], lead, note, fight=False)


def _reask(ctx: TurnContext, t: Turn, message: str, exchanges: list[tuple[str, str]], lead: str, passage: str,
           facts: list[str]) -> str:
    """One more DM call, no tools: the final passage, told what the world did after the draft (spec 032 P4)."""
    world = _world_text(facts).strip() + "\nYOUR DRAFT PASSAGE:\n" + passage
    note = ("Write the final passage now (no tool calls). It replaces your draft: keep what still holds and weave in "
            "what the world did, agreeing with it exactly.")
    packet = Packet(instructions=load_prompt("dm"),
                    message=_message(ctx, t, message, exchanges, "\n".join(x for x in (lead, world) if x), note))
    res = call_role(ctx.model, DM_ROLE, step_schema(ctx, final=True), packet, turn_id=ctx.turn_id,
                    recorder=ctx.record_call, default={"calls": [], "passage": passage, "said": t.said_raw, "asks": [],
                                                       "cost_form": ""})
    t.stats["steps"] += 1
    t.cost_form = str((res.data or {}).get("cost_form") or "") or t.cost_form
    t.stats["world"]["reasked"] += 1
    t.said_raw = list((res.data or {}).get("said") or [])  # the final passage replaces the draft, and its lines
    return str((res.data or {}).get("passage") or passage)


def _world(ctx: TurnContext, t: Turn) -> list[str]:
    """The world step once per exchange (engine/dm/dm_world.py); a time jump (a rest, a day) opens a new scene."""
    from engine.dm import dm_world

    if t.world_done or ctx.state.open_pause() is not None:
        return []
    t.world_done = True
    _footing(ctx, t)  # [spec 033 D2] the character's result includes the footing: the foes act on it
    facts = dm_world.world_step(ctx, t)
    if dm_world.time_jumped(ctx):
        _open_scene(ctx, "time_jump")
        facts.append("Time has jumped on; a new scene begins here.")
    return facts


def _drain(t: Turn) -> None:
    """[spec 033 D3] The `not_chosen:{field}` lines the resolver logged on `PipelineEnv.defaults` join the turn's stats."""
    t.stats["defaults"] += t.env.defaults
    t.env.defaults.clear()


def _cost_block(st: Any) -> str:
    """[spec 033 DL-01-60] COST TO SHAPE: the footing forms that can land, after a failed roll's severity is known. The
    DM picks one in `cost_form` (its answer); omitted or not listed, code takes the first and logs it."""
    from engine.resolve import costs

    pend = costs.pending_footing(st)
    if pend is None:
        return ""
    words = pend.get("words") or {}
    return (f"\nCOST TO SHAPE: the roll cost the character their footing (severity {pend['severity']}). Pick the form it "
            "takes in `cost_form`, one id below; the game writes exactly that:\n"
            + "\n".join(f"- {o}: {words.get(o, o)}" for o in pend["options"]))


def _footing(ctx: TurnContext, t: Turn) -> None:
    """[spec 033 DL-01-60] Write the footing form the DM picked (`apply_footing`); log `not_chosen:cost_form` when code
    took the default. Held back while a pause is open (the DM is shown the options on the answer that follows)."""
    from engine.resolve import costs

    tx = ctx.need_tx()
    pend = costs.pending_footing(tx.state)
    if pend is None or tx.state.open_pause() is not None:
        return
    _, defaulted = costs.apply_footing(tx, ctx.rules, pend, t.cost_form or None)
    if defaulted:
        _default(t, "cost_form")
    t.cost_form = ""


def _world_text(facts: list[str]) -> str:
    return ("\nWHAT THE WORLD DID (the game rolled and recorded these; the passage must agree with them):\n"
            + "\n".join(f"- {f}" for f in facts)) if facts else ""


def _args(c: dict[str, Any]) -> str:
    return json.dumps({k: v for k, v in c.items() if k != "tool" and v not in ("", None, "none", 0)},
                      ensure_ascii=False)


def _message(ctx: TurnContext, t: Turn, message: str, exchanges: list[tuple[str, str]], lead: str,
             note: str, *, fight: bool = True) -> str:
    convo = [f"PLAYER: {i}\nGAME: {_flat(o, 1200)}" for i, o in exchanges]
    done = [f"[{n + 1}] {a} {b}\n -> {o}" for n, (a, b, o) in enumerate(t.log)]
    return "\n\n".join(x for x in [
        "SITUATION\n" + situation(ctx, fight=fight),
        "RECENT CONVERSATION (oldest first)\n" + ("\n\n".join(convo) or "(the story has just begun)"),
        lead and "WHAT JUST HAPPENED\n" + lead,
        message and f"THE PLAYER'S MESSAGE\n{message}",
        "TOOL RESULTS THIS TURN\n" + ("\n".join(done) or "(none yet)"),
        note] if x)


def situation(ctx: TurnContext, *, fight: bool = True) -> str:
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
    lines += _fight_block(st, pc) if fight else []
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


def _fight_block(st: Any, pc: str | None, legal: dict[str, list[str]] | None = None) -> list[str]:
    """The fight, in words (spec 032 G7): each foe's state and band to the character, and the character's own state.
    [spec 033 D2] With `legal` (the foe call): only the foes able to act, each with its conditions and the acts legal
    for it now (T-06-16)."""
    from engine.resolve.conflict import record as conflict
    from engine.resolve.conflict import state_words

    rec = conflict(st)
    if not rec or not pc:
        return []
    pos = st.positions.get(pc)
    out = ["FIGHT: a fight is on. After each move of the character settles you are asked what each foe does, from the "
           "acts legal for it; the game rolls it and tells you the result, which is never yours to write. The "
           "character's attack is a `propose_roll`."]
    for f in rec.get("foes", []):
        if legal is not None and f not in legal:
            continue
        band = str((pos.band_to.get(f) if pos else None) or "near").removeprefix("band.")
        line = f"- {f}: {_name(st, f)}, {state_words(st, f)}; {band} to the character"
        if legal is not None:
            conds = ", ".join(c.condition_id.removeprefix("cond.") for c in st.conditions_on(f)) or "none"
            line += f"; conditions: {conds}; acts now: {', '.join(legal[f])}"
        out.append(line)
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
          "reveal_clue": _reveal_clue, "mood": _mood, "end_scene": _end_scene,
          "end_game": _end_game}.get(name)
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
    """An entity id from what the DM wrote: the id itself, else the exact recorded name when one entity bears it
    (case-folded equality; no partial or head-noun matching, 01.2.5)."""
    s = str(raw or "").strip()
    if not s or s.lower() in ("none", "null", "world", "-"):
        return None
    if s in st.entities:
        return s
    low = s.lower()
    hits = [i for i, e in st.entities.items() if e.name.lower() == low and i not in st.seals]
    return hits[0] if len(hits) == 1 else s


_ID_LIKE = re.compile(r"^[a-z_]+\.[a-z0-9_.]+$")
PC = "pc"  # the one literal the DM writes for the player character (contract: ids)


def target_kinds(rules: Any, verb: str | None) -> tuple[str, ...]:
    """What a verb's target can be: the `target_kinds` field of its entry in basic_verbs.yaml (DL-01-62), "person"
    and/or "object", the first listed first. A verb with no target slot gives ()."""
    entry = rules.basic_verbs.get(verb) if verb else None
    return tuple(entry.get("target_kinds") or ()) if isinstance(entry, dict) else ()


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


def _party(ctx: TurnContext, t: Turn, raw: Any, *, person: bool = False, as_: Any = None) -> str | None:
    """A person or creature from what the DM wrote [spec 033 R6, 01.2.5]. An id slot takes an exact id, `"pc"`, an
    exact recorded name, or the id the DM chose for a `new_npc` this turn. Anything else is the DM naming someone new:
    `as` (he, she, they, creature, thing) says what; a person-only slot with no `as` is `they` (logged
    `not_chosen:as`). A person or creature is made at the scene's place with the DM's words as its role, and `t.made`
    tells the DM its id; `thing` is returned as written. Nothing here reads the words."""
    from engine.retrieve.scene import pc_id

    tx = ctx.need_tx()
    st = tx.state
    s = str(raw or "").strip()
    if s == PC and pc_id(st):
        return pc_id(st)
    eid = _id(st, t.aliases.get(s, raw))
    if eid is None or eid in st.entities:
        return eid
    kind = str(as_ or "none")
    if kind == "none":
        if not person:
            return s
        _default(t, "as")
        kind = "they"
    place = st.scene.place_id if st.scene is not None else None
    if kind == "thing" or place not in st.entities:
        return s
    new = _walk_on(ctx, s, place, kind)  # type: ignore[arg-type]
    t.aliases[s] = new  # the same words again in this turn are the same person
    t.made.append(f"{s} ({new})")
    return new


def _walk_on(ctx: TurnContext, words: str, place: str | None, as_: str = "they", name: str | None = None) -> str:
    """A minimal walk-on at `place`, described by the DM's words (its role) and pronouns from `as`: a creature
    (`mind: animal`, no rolled person) or a person (`social.meet_npc`, PR-12-5; `name` as given, else rolled). Never
    reuses anyone. A made-up id (`npc.hal`) is not words: the role is then rolled."""
    from engine.world.social import meet_npc

    tx = ctx.need_tx()
    label = "" if _ID_LIKE.match(words) else words
    if as_ == "creature":
        eid = ids.entity_id("npc", label or "creature", tx.state.entities)
        tx.add(Event.of("entity_created", source="engine", rule_id="PR-00-7", entity=EntityRecord(
            id=eid, kind="npc", name=name or label or "creature", visibility="shown",
            data={"mind": "animal", "role": label or "creature", "name_known": False, "home": place})))
        if place is not None:
            tx.add(Event.of("position_set", source="engine", rule_id="PR-00-7", entity=eid, location=place))
        return eid
    return meet_npc(ctx.time_ctx(), label or None, place, alias=label or None, reuse=False, name=name,
                    pronouns=PRONOUNS.get(as_, "they/them"))


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
                    as_=c.get("as"))  # [spec 033 P4]
    words = str(c.get("target") or "").strip()
    if target is not None and target not in st.entities:
        if "person" in kinds and "object" not in kinds:  # a person the game could not put here (no place open)
            return (f"REFUSED: no one on record called {target!r} (use an id from the situation, or none)")
        # [spec 032 P8a] a feature or obstacle in words (the stuck hatch): the act is on it, never refused
        target = None
        if not str(c.get("change_what") or "").strip():
            c = {**c, "change_what": words}  # [spec 033 P4] the DM's words as written, never an id's tail
    if target is not None and st.entities[target].kind in ("npc", "companion", "adversary"):
        why = _acting(st, target, down=False)  # a downed foe can still be struck; the dead and the absent cannot
        if why:
            return f"REFUSED: {why}"
    stated = _stated(ctx, t, c, verb, target)
    if isinstance(stated, str):
        return stated
    if str(c.get("change_kind") or "") != "move_to":  # a move is the way to get in reach
        why = _reach(ctx, t, verb, target, stated)
        if why:
            return why
    kind = str(c.get("change_kind") or "none")
    raw_t = str(c.get("target") or "").strip()
    what, whom = (target if raw_t and str(c.get(k) or "").strip() == raw_t else _id(st, c.get(k))
                  for k in ("change_what", "change_whom"))
    goal = str(c.get("goal") or "").strip() or "act"
    how = str(c.get("how") or "").strip() or None
    phrase = str(c.get("change_what") or "").strip()
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
    beat = Beat(id=tx.mint(ids.BEAT), actor=pc, intent=goal, method=method, how=how, target=target,
                restatement=goal[:1].upper() + goal[1:], verb=verb,
                title=goal[:1].upper() + goal[1:] if str(c.get("goal") or "").strip() else None, speech=verb == "verb.talk",
                against_will=bool(target and st.entities[target].kind in ("npc", "adversary")
                                  and verb in ("verb.strike", "verb.grapple", "verb.force")),
                declared_seq=st.last_seq, change=change, stated=stated)
    t.env.proposal = c  # what the code framer reads (difficulty, attribute, stakes)
    res = run_beats(t.env, [BeatPlan(beat=beat, intent_verbs=[str(verb or "").removeprefix("verb.")])])
    _take(t.rec, res, t.oof, None)
    _drain(t)  # [spec 033 D3]
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
        return "ROLLED (a safe roll, made at once): " + _outcomes_text(ctx, t.rec, t.oof) + _cost_block(tx.state)
    return f"NOT POSSIBLE AS PROPOSED ({out.status}): {e.gate_words}"


def _reach(ctx: TurnContext, t: Turn, verb: str | None, target: str | None, stated: Any) -> str:
    """[spec 033 T032, 06.4.3] A melee Strike, a Grapple or a Force needs the target in reach: the recorded band
    (`conflict._band`) is one the weapon covers (engaged; a Strike's weapon bands and a thrown weapon's bands, T-06-6).
    A rule's arithmetic on recorded state, so it is refused, not defaulted. The message names the move to state first."""
    from engine.resolve import conflict

    st = ctx.state
    pc = t.rec.pc or ""
    if verb not in ("verb.strike", "verb.grapple", "verb.force") or target is None or target == pc             or st.entities[target].kind not in ("npc", "adversary", "companion"):
        return ""
    band = conflict._band(st, pc, target)
    ok = {"engaged"}
    if verb == "verb.strike":
        w = conflict.weapon_of(ctx.rules, st, stated.weapon)
        ok = {str(b).split()[0].removeprefix("band.") for b in [*(w.get("bands") or ()), *(w.get("thrown_bands") or ())]}
    if band in ok:
        return ""
    return (f"REFUSED: {_name(st, target)} is not in reach (" + (f"{band} to the character" if band else "no position is recorded")
            + "). State the move first: `change` position `to` engaged with `what` " + target + " when nothing stops it, or a "
            "`propose_roll` with change_kind move_to (change_what a band) when someone contests it; then make the attack.")


def _default(t: Turn, field_: str) -> None:
    """[spec 033 D3] The DM left a detail out and code holds its documented default: count it for the owner."""
    t.stats["defaults"].append(f"not_chosen:{field_}")


def _stated(ctx: TurnContext, t: Turn, c: dict[str, Any], verb: str | None, target: str | None) -> Any:
    """The DM's typed fields as `Stated` (resolve/types.py), or a REFUSED string for a value that is not one of the
    legal ones. Omitted details take the contract's default and are logged (D3); nothing here reads prose."""
    from engine.resolve import conflict
    from engine.resolve.change import holder_of
    from engine.resolve.types import Stated

    st = ctx.state
    pc = t.rec.pc or ""
    approach = str(c.get("approach") or "plain")
    approach = "plain" if approach == "none" else approach
    if approach != "plain" and approach not in approaches(ctx.rules):
        return f"REFUSED: approach {approach!r} is not one of: plain, " + "; ".join(approaches(ctx.rules))
    force = str(c.get("force") or "none")
    if verb == "verb.force":
        if force not in FORCES:
            _default(t, "force")
            force = "push"
    else:
        force = "none"
    weapon = None
    if verb == "verb.strike":
        w = str(c.get("weapon") or "").strip()
        wid = _id(st, w) if w else None
        if w and w.lower() != "unarmed" and holder_of(st, wid or "") != pc:
            held = [i for i, e in st.entities.items() if e.kind in ("item", "object") and holder_of(st, i) == pc]
            return f"REFUSED: the character does not hold {w!r} (hold: {', '.join(held) or 'nothing'}; or unarmed)"
        if w:
            weapon = "unarmed" if w.lower() == "unarmed" else wid
        else:
            _default(t, "weapon")
            wielded = st.fact_value(pc, "wields")
            weapon = wielded if isinstance(wielded, str) and wielded in st.entities else "unarmed"
    fail_on = _id(st, c.get("fail_on"))
    fail_on = fail_on if fail_on in st.entities else None
    if fail_on is None and str(c.get("fail_cost") or "") in ("cost.exposure", "cost.gear", "cost.closed_door"):
        _default(t, "fail_on")
    position = None
    if str(c.get("change_kind") or "") == "move_to":
        band = str(c.get("change_what") or "").strip().lower().removeprefix("band.")
        if _id(st, c.get("change_what")) in st.entities and st.entities[str(_id(st, c.get("change_what")))].kind == "place":
            return "REFUSED: move_to takes a band (" + ", ".join(conflict.BANDS) + "); to go to a place use travel"
        if band in conflict.BANDS and target in st.entities:
            mover = pc
            if str(c.get("change_whom") or "").strip():
                mover = _id(st, c.get("change_whom")) or pc
            else:
                _default(t, "change_whom")
            if mover in st.entities:
                position = (mover, band, target if mover == pc else pc)
    return Stated(reads=bool(c.get("reads")), approach=approach, force=force if force in FORCES else None,  # type: ignore[arg-type]
                  weapon=weapon, nonlethal=bool(c.get("nonlethal")), fail_on=fail_on, position=position)


def code_framer(ctx: TurnContext, t: Turn) -> Any:
    """The pipeline's FramerFn with no model call: the rule's default frame (engine/dm/roles/framer.py), adjusted by
    the DM's typed proposal (attribute, difficulty tier, stakes) where the rules accept it; else the plain default."""
    from engine.dm.roles.framer import default_frame, to_proposed
    from engine.dm.schemas import build_schema, schema_context
    from engine.resolve.costs import menu
    from engine.resolve.frame import frame_check
    from engine.retrieve.scene import focus_of

    def propose(beat: Any, candidates: list[str], *, gate: Any, note: str | None = None) -> Any:
        st = ctx.state
        # [spec 032 P8b] the whole cost menu, not "the entries with a scene fact to cite": the structural fits (01.13.1)
        # decide here. Left out, a scene with no scene facts offered the twist alone and every roll was refused
        # (held-out H07, H10, H11: no roll, so no foe turn).
        sctx = schema_context(st, ctx.rules, anchors=candidates, beat=beat, message=beat.intent,
                              focus=focus_of(beat),
                              cost_menu_ids=[k for k, c in menu(ctx.rules).items() if not c.get("alternate_only")])
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
        # the DM's own `fail_cost` first (when legal), then the verb's plain failures in the rules' order (spec 032 G8;
        # `cost_selection.verb_costs`: a look costs time or effort, never harm). [spec 032 P8b]
        plain = list((ctx.rules.resolution["cost_selection"].get("verb_costs") or {}).get(str(beat.verb), []))
        wants = [w for w in dict.fromkeys((fc, *plain)) if w]
        home = ctx.rules.resolution.get("stakes_cost_menus") or {}
        if stakes != "safe" and sctx.stakes_menus:
            usable = [(src, m) for src, m in sctx.stakes_menus.items() if src != "none" and m["threatened"] and m["alternate"]]
            for want in wants or [""]:
                fits = [(src, m) for src, m in usable if want in m["threatened"]]
                if not fits and not plain and not cands:  # a verb with no list: the first source's first cost, as before
                    fits = usable[:1]
                if fits:  # the source that lists the cost first is the one it most directly follows (01.13.1)
                    src, m = min(fits, key=lambda x: (home.get(x[0]) or []).index(want) if want in (home.get(x[0]) or []) else 99)
                    threat = want if want in m["threatened"] else m["threatened"][0]
                    alt = next((x for x in [*m["alternate"], "cost.shortfall"] if x != threat), None)  # the shortfall is open to every source
                    cands.append({**d, "stakes_heavy": stakes == "dire", "stakes": {
                        "source": src, "threatened_cost": {"menu_id": threat, "form_intent": "", "source_fact": None},
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


def _end_game(ctx: TurnContext, t: Turn, c: dict[str, Any]) -> str:
    """[spec 033 R9] The DM ends the character's story when the player asks in the fiction: code opens the same
    confirmation `/retire` does (11.13.1). The player answers it; nothing is retired until they do."""
    from engine.dm.ending import ending_due, open_retire

    st = ctx.state
    if not t.rec.pc or ending_due(st):
        return "REFUSED: the character's story has already ended"
    if st.open_pause() is not None:
        return "REFUSED: a question is open to the player; the story cannot end under it"
    open_retire(ctx.need_tx())
    t.paused = True
    t.stats.setdefault("end_game", []).append(str(c.get("why") or "")[:160])
    return ("ASKED: the player is asked to confirm retiring the character. The turn pauses here: write only a short "
            "closing line, never the ending itself.")


def _position(ctx: TurnContext, t: Turn, c: dict[str, Any]) -> str:
    """`change position` [spec 033 R1]: the DM puts someone at a band to another person, or an NPC at a place. Writes
    what it is told, nothing else (the reach refusal is P2a's). Omitted: `who` = the character, `what` = the other
    party (the one foe in a fight, or the one other person here; an NPC's is the character)."""
    from engine.resolve import conflict
    from engine.world.scenes import cast_present

    tx = ctx.need_tx()
    st = tx.state
    pc = t.rec.pc or ""
    if str(c.get("who") or "").strip():
        who = _party(ctx, t, c.get("who"), person=True)
    else:
        _default(t, "who")
        who = pc
    why = _acting(st, who, down=False)
    if why:
        return f"REFUSED: {why}"
    assert who is not None
    to = str(c.get("to") or "").strip()
    band = to.lower().removeprefix("band.")
    if band in conflict.BANDS:
        other = _id(st, c.get("what")) if str(c.get("what") or "").strip() else None
        if other is None:
            if who != pc:
                other = pc
            else:
                near = [x for x in (conflict.record(st).get("foes") or cast_present(st)) if x != pc]
                other = near[0] if len(near) == 1 else None
            if other is None:
                return "REFUSED: say who the band is to, in `what` (an id)"
            _default(t, "what")
        why = _acting(st, other, down=False)
        if why:
            return f"REFUSED: {why}"
        conflict._set_band(tx, who, other, band, "06.3.9")
        return f"done: {_name(st, who)} is now {band} to {_name(st, other)}"
    dest = _id(st, to)
    if dest in st.entities and st.entities[str(dest)].kind == "place":
        if who == pc:
            return "REFUSED: the character goes to another place by travel, not by position"
        tx.add(Event.of("position_set", source="engine", rule_id="12.4.1", entity=who, location=dest))
        return f"done: {_name(st, who)} is now at {_name(st, dest)}"
    return f"REFUSED: `to` is a band ({', '.join(conflict.BANDS)}) or a place id; got {to!r}"


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
        who = _party(ctx, t, c.get("who"), person=kind != "fact", as_=c.get("as"))  # a fact's subject may be a thing: not made
    if kind in ("coin", "give_item", "new_item"):
        to = _party(ctx, t, c.get("to"), person=True, as_=c.get("as"))
    amount = int(c.get("amount") or 0)
    if kind == "coin":
        return _coin(ctx, t, payer=who, payee=to, amount=amount)
    if kind == "give_item":
        return _give(ctx, item=what, giver=who or pc, to=to)
    if kind == "new_item":
        name = str(c.get("what") or "").strip()
        holder = to or pc
        why = _acting(st, holder)
        if why or not name:
            return f"REFUSED: {why or 'name the item'}"
        eid = ids.entity_id("item", name, st.entities)  # always a new record: a twin is the DM's to see in the situation
        tx.add(Event.of("entity_created", source="engine", rule_id="00.6.6",
                        entity=EntityRecord(id=eid, kind="item", name=name, visibility="shown")))
        tx.add(_fact(tx, eid, "holder", holder))
        return f"done: {name} ({eid}) now held by {_name(tx.state, holder)}" + _knows(tx, c, eid)
    if kind in ("condition_add", "condition_remove"):
        return _condition(ctx, who, str(c.get("what") or ""), add=kind == "condition_add", pc=pc)
    if kind == "position":
        return _position(ctx, t, c)
    if kind == "fight":
        if not str(c.get("to") or "").strip():
            _default(t, "fight.to")  # [spec 033 D3] near
        return _fight(ctx, who, pc, str(c.get("to") or ""))
    if kind == "npc_leaves":
        why = _acting(st, who)
        if why:
            return f"REFUSED: {why}"
        assert who is not None
        if to in st.entities and st.entities[to].kind == "place":
            dest = to
        else:  # [spec 033 A21, D3] no place named: off-scene, "elsewhere" (the situation lists them so); logged
            _default(t, "npc_leaves.to")
            dest = OFF_SCENE
        tx.add(Event.of("position_set", source="engine", rule_id="12.4.1", entity=who, location=dest))
        return f"done: {_name(st, who)} leaves for {_name(st, dest) if dest in st.entities else dest}"
    if kind == "new_npc":
        place = st.scene.place_id if st.scene else None
        as_ = str(c.get("as") or "none")
        if as_ == "none":
            _default(t, "as")
            as_ = "they"
        if as_ == "thing":
            return "REFUSED: a thing is not someone (new_item makes things)"
        role = str(c.get("what") or "").strip()
        eid = _walk_on(ctx, role, place, as_, str(c.get("name") or "").strip() or None)  # type: ignore[arg-type]
        if _ID_LIKE.match(str(c.get("who") or "").strip()):  # [spec 032 P8a] the DM's own id for them, used next call
            t.aliases[str(c["who"]).strip()] = eid
        card = __import__("engine.dm.packet", fromlist=["people_card"]).people_card(ctx.state, eid, rules=ctx.rules)
        return f"done: someone new is here: {eid}: " + "; ".join(x.strip() for x in card[:3]) + _knows(tx, c, eid)
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


def _knows(tx: Any, c: dict[str, Any], eid: str) -> str:
    """`knows` on a new person or item [spec 033 R4]: the clue node id of a WITNESS NEEDED line; the node's reserve (else
    a generic placement) is placed on `eid`. Nothing is guessed: an id that names no node is told, not placed."""
    from engine.gen import case

    node = str(c.get("knows") or "").strip()
    if not node:
        return ""
    if case.place_on(tx, node, eid) is None:
        return f"\nNOTE: knows {node!r} names no clue node on record; nothing was placed."
    return f"\n{_name(tx.state, eid)} now holds what {node} needs."


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


def _fight(ctx: TurnContext, who: str | None, pc: str, rng: str = "") -> str:
    """A person the DM has turn on the PC: the conflict starts (spec 032 G7). No foe action here (the world step runs
    it); nothing is done to the PC without a roll or the foe's own turn. `rng` is the starting range the scene has
    established, the DM's to set (06.3.9): a band id; empty or unknown starts at `near`, the rule's default."""
    from engine.resolve import conflict

    tx = ctx.need_tx()
    why = _acting(tx.state, who)
    if why:
        return f"REFUSED: {why}"
    assert who is not None
    band = rng.strip().lower().removeprefix("band.")
    given = band in conflict.BANDS
    # [spec 033 D3] the DM's `to`, else the band already recorded, else near (the caller logs `not_chosen:fight.to`)
    if who not in conflict.record(tx.state).get("foes", []) and (given or conflict._band(tx.state, pc, who) is None):
        conflict._set_band(tx, pc, who, band if given else "near", "06.3.9")
    if not conflict.start(ctx.time_ctx(), pc, [who], f"the DM: {_name(tx.state, who)} turns on the character"):
        return f"{_name(tx.state, who)} is already in the fight (or cannot be a foe)."
    at = conflict._band(tx.state, pc, who) or "near"
    ranged = "" if given or not rng.strip() else f" (`{rng}` is not a range: {', '.join(conflict.BANDS)})"
    return (f"done: a fight begins; {_name(tx.state, who)} turns on the character, at range {at}{ranged}. Blows are not struck by your words: "
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
        if not p or p == PC:
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


# ------------------------------------------------------------------------------------------- told


def _told(ctx: TurnContext, t: Turn) -> None:
    """What people said, as testimony (spec 032 G3, spec 033 R8): each `said` entry becomes a record on the speaker
    (place and day), shown in the journal as "what you were told"; never a world fact. The speaker is an id, `"pc"`
    or an exact recorded name; else the DM names a new walk-on with `as` (default they, logged). The line is kept as
    given: no check of the words against the passage, earlier lines or clues (the DM records facts). Dropped and
    logged (`told_dropped`): a speaker who is unknown, dead, gone or not here. The character's own words and an empty
    line are skipped without a log."""
    from engine.dm import testimony
    from engine.retrieve.scene import pc_id

    st = ctx.state
    keep: list[dict[str, Any]] = []
    for e in [x for x in t.said_raw if isinstance(x, dict)][:SAID_MAX]:
        words, raw = str(e.get("words") or "").strip(), str(e.get("npc") or "")
        if not words or raw.strip() == PC:
            continue
        who = _party(ctx, t, raw, person=True, as_=e.get("as"))
        if who == pc_id(st):
            continue
        why = _acting(st, who, down=False)
        if why:
            t.stats["told_dropped"].append({"npc": raw[:60], "why": why, "words": words[:80]})
        else:
            keep.append({"speaker": who, "turn": ctx.turn_id, "words": words, "about": [who], "question": None})
    for sid, k in zip(testimony.add_said(ctx, keep), keep, strict=True):
        t.stats["said"].append({"id": sid, "speaker": k["speaker"], "words": k["words"][:120]})
    t.told = keep


def _name(st: Any, eid: str | None) -> str:
    from engine.store.views import display_name

    return display_name(st, eid) if eid and eid in st.entities else str(eid)


def _flat(s: Any, n: int | None = None) -> str:
    x = " ".join(str(s).split())
    return x if n is None or len(x) <= n else x[:n] + "…"


__all__ = ["ENGINE", "MAX_TOOLS", "Outcome", "enabled", "play_answer", "play_turn", "secrets",
           "situation", "step_schema", "tool"]
