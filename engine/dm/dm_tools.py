"""Spec 031 prototype: one DM model with tools over the mechanical spine (`GameConfig.engine = "dm-tools"`).

    out = play_turn(ctx, "I ask the smith about the road.")   # one DM role in a bounded tool loop, then the passage
    out = play_answer(ctx, "commit")                           # an OFFER answered: code rolls, the DM narrates it
    out.response                                               # the delivered Response (same shape as the pipeline)

Code keeps the spine: the dice and odds (`resolve/`: gate, necessity, frame, OFFER, roll, read, cost), state (coin,
items, conditions, positions, presence, time), memory, the case graph and clue delivery (spec 029), the mood and the
ceiling (T-12-19, given as facts, never enforced). The DM model owns language and judgment: who answers, how people
react, what needs a roll, the passage. Bypassed here (not deleted): the Reader, Framer, Director, World, Checker,
narrator record lines, `npc_layer` and the answer ladder. `/fix` stays the pipeline's (engine/dm/dispute.py).

Each turn: the DM sees the situation (who is here with their people card and mood, the place, the PC sheet, open
threads, the scene) and the recent conversation, calls up to MAX_TOOLS tools (PER_STEP per answer), then writes the
passage. A `propose_roll` that needs a roll pauses the turn on the code-rendered OFFER; the next `play_answer` rolls
and the DM narrates the result. Per-turn stats (tool calls, refusals, ceilings, secret leaks) go to
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
from engine.dm.schemas import STR, Schema, arr, enum, obj
from engine.llm.base import Packet, Role, call_role
from engine.store.events import EntityRecord, Event
from engine.store.records import TurnRecord

ENGINE = "dm-tools"
MAX_TOOLS, PER_STEP = 6, 3
TOOLS = ("propose_roll", "state", "change", "recall", "reveal_clue", "mood")
CHANGES = ("coin", "give_item", "new_item", "condition_add", "condition_remove", "npc_leaves", "new_npc", "travel",
           "rest", "fact")
COSTS = ("none", "small", "real", "big")
GRANTS = ("help", "price", "partial", "refuse")  # what the DM had the NPC do for an ask (for ceiling logging)
STAKES = ("safe", "risky", "dire")
DM_ROLE = Role.NARRATOR  # ponytail: the DM's calls are logged under the narrator role; a Role.DM needs a schema,
# prompt, packet and offline heuristic per role in the contract tests. Add it if the prototype is kept.
MOOD = {"willing": "open", "guarded": "guarded", "unwilling": "closed"}
OUT_CHARS = 1600

PROMPT = """You are the game master of a text tabletop RPG, played in a terminal by one player. You run the world:
the people, the places, what happens. Code keeps the mechanical spine (dice, odds, coin, items, conditions, who is
where, time, clues) and you reach it through tools. You own the words and the judgment.

Each turn, read the player's message and the recent conversation, decide what happens, call tools when the spine is
involved, then write the passage.

Tools (each call is one object in `calls`; leave `calls` empty when you are done and write `passage`):
- propose_roll: the player's character attempts something whose outcome is uncertain AND failure would cost
  something. Give the goal (what success achieves), the verb, the target id (or "none"), how they do it, why it is
  uncertain, and the stakes. Code computes the odds. If a roll is needed the turn pauses on the odds screen: write
  only the lead-up in `passage` (never the outcome); you narrate the result next turn. With nothing at stake or a
  certain outcome, don't propose a roll: just narrate it.
- state: read the sheet ("pc"), a person or thing (its id), "here" (place, people, exits), or "time".
- change: apply a state change the fiction makes: coin (who pays `who`, who receives `to`, `amount`), give_item
  (`what` item id to `to`), new_item (`what` a short name, held by `to`), condition_add / condition_remove (`who`,
  `what` condition id), npc_leaves (`who`, optional `to` place id), new_npc (`what` their role, e.g. "a ferryman"),
  travel (`to` a reachable place id), rest (`what`: breather, rest_short or rest_long), fact (`who` subject id,
  `what` a short predicate, `note` the value). Code refuses only what the game can't hold and tells you why.
- recall: search memory (past turns, what people said, what the character knows) for `query`.
- reveal_clue: the player asks `npc` (an id) a question that may touch a mystery. Code says whether that person
  holds a clue about it, and if so gives the exact clue to deliver. Deliver it in their voice. Never invent clues.
- mood: a person's mood toward the player's character (rolled by dice, held for the scene) and the most they will
  do for an ask of a given cost to them (`ask_cost`). These are facts about the person: their reaction is at or
  below that ceiling, in their own voice.

When someone grants or refuses an ask this turn, list it in `asks` (npc id, the ask's cost to them, what they did).

The passage: second person ("you"), present tense, 60-180 words. Answer what the player did or asked; people speak
in their own voices; end on something the player can act on, never a menu. Never decide the player character's
words, feelings or choices beyond what they declared. Use names the player knows. Never mention tools, ids, dice
or rules in the passage."""


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
    stats: dict[str, Any] = field(default_factory=lambda: {"tool_calls": 0, "steps": 0, "refusals": [],
                                                           "ceilings": [], "ceiling_violations": [], "leaks": [],
                                                           "clues": [], "rolls": []})
    paused: bool = False
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
    from engine.dm import oof as oofm
    from engine.dm.narration import shown_pause, turn_blocks
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
                _harm_followups(ctx, t.env, t.rec, t.oof)
                lead = f"The player picked: {label}.\n" + _outcomes_text(ctx, t.rec, t.oof)
            elif pause is not None and (pause.detail or {}).get("stage") in ("offer", "warning", "redirect",
                                                                                 "near_miss", "plan"):
                res = close_by_default(t.env, pause)  # new words with an offer open: it is withdrawn (12.2.6)
                _take(t.rec, res, t.oof, None)
                lead = "The roll offered last turn was not taken (withdrawn; nothing spent)."
            if tx.state.scene is None and tx.state.open_pause() is None:
                _open_scene(ctx)
            if tx.state.open_pause() is None:  # a near miss or last chance opened by the answer: the menu first
                passage = _dm_loop(ctx, t, message if choice is None else "", exchanges, lead)
            _sync_scene(ctx, t)
            if tx.state.open_pause() is None:
                _turn_end(ctx, t.rec, t.oof)
                _harm_followups(ctx, t.env, t.rec, t.oof)
            _audit(ctx, t, passage)
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
    calls = store.model_calls(turn_id)
    t.stats.update(model_calls=len(calls), tokens_in=sum(int(c.get("tokens_in") or 0) for c in calls),
                   tokens_out=sum(int(c.get("tokens_out") or 0) for c in calls),
                   latency_ms=sum(int(c.get("latency_ms") or 0) for c in calls),
                   tools=[{"tool": a, "args": b, "out": o[:300]} for a, b, o in t.log])
    tr = TurnRecord(turn_id=turn_id, input_verbatim=message, writes=t.rec.write_seqs,
                    beats=[b.frame_id for b in t.rec.beats if b.frame_id], delivered_verbatim=resp.text(),
                    model_calls=list(ctx.call_ids), screen={"dm_tools": t.stats},
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
    verbs = ctx.rules.ids("verb.")
    kinds = list(ctx.rules.resolution["intended_change"]["kinds"])
    calls = [
        obj({"tool": enum(["propose_roll"]), "goal": STR, "verb": enum(verbs), "target": STR, "how": STR,
             "attribute": STR, "difficulty": STR, "why_uncertain": STR, "stakes": enum(STAKES),
             "change_kind": enum(kinds), "change_what": STR, "change_whom": STR}),
        obj({"tool": enum(["state"]), "about": STR}),
        obj({"tool": enum(["change"]), "kind": enum(CHANGES), "who": STR, "what": STR, "to": STR,
             "amount": {"type": "integer"}, "note": STR}),
        obj({"tool": enum(["recall"]), "query": STR}),
        obj({"tool": enum(["reveal_clue"]), "npc": STR, "question": STR}),
        obj({"tool": enum(["mood"]), "npc": STR, "ask_cost": enum(COSTS)}),
    ]
    call = {"anyOf": calls}
    return obj({"calls": arr(call, max_items=0 if final else PER_STEP), "passage": STR,
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
        packet = Packet(instructions=PROMPT, message=_message(ctx, t, message, exchanges, lead, note))
        schema = step_schema(ctx, final=final)
        res = call_role(ctx.model, DM_ROLE, schema, packet, turn_id=ctx.turn_id, recorder=ctx.record_call,
                        default={"calls": [], "passage": str(data.get("passage") or ""), "asks": []})
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
    return str(data.get("passage") or "")


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
    from engine.dm.fixer import sheet_line
    from engine.dm.oof import when_words
    from engine.dm.packet import people_card
    from engine.resolve.change import holder_of
    from engine.retrieve.scene import pc_id
    from engine.world.places import location, reachable
    from engine.world.scenes import cast_present
    from engine.world.social import thread_list

    st, rules = ctx.state, ctx.rules
    pc = pc_id(st)
    here = location(st) if pc else None
    lines = [f"Now: {when_words(st.time.now)}; at {_name(st, here)} ({here})" if here else "Now: nowhere on record"]
    sc = st.scene
    if sc is not None and (sc.agenda or sc.hoped_answer):
        lines.append(f"Scene: {sc.agenda}" + (f" (hoped: {sc.hoped_answer})" if sc.hoped_answer else ""))
    if pc:
        card = people_card(st, pc, rules=rules)
        lines += ["The player's character (" + pc + "): " + (card[0] if card else _name(st, pc)), *card[1:],
                  f"  sheet: {sheet_line(st, rules, pc)}"]
        held = [i for i, e in st.entities.items() if e.kind in ("item", "object", "clue") and holder_of(st, i) == pc]
        lines.append("  carries: " + (", ".join(f"{_name(st, i)} ({i})" for i in held) or "nothing on record"))
    people = cast_present(st) if sc is not None else []
    lines.append("People here:" if people else "People here: no one")
    for eid in people:
        card = people_card(st, eid, rules=rules)
        lines += [f"- {eid}: {card[0] if card else _name(st, eid)}", *card[1:]]
        m = _held_mood(st, eid)
        lines.append(f"  mood toward you: {m}" if m else "  mood toward you: not yet rolled (use `mood`)")
        if secrets_visible(ctx):
            lines += [f"  PRIVATE (they know this; the player does not): {s}" for s in secrets(st, eid)]
    if here:
        exits = [f"{_name(st, x.to)} ({x.to})" for x in reachable(st, here) if x.to != here]
        lines.append("Exits: " + (", ".join(exits[:8]) or "none known"))
    threads = [x for x in thread_list(st) if x["status"] == "active"][:4]
    if threads:
        lines.append("Open threads: " + "; ".join(_flat(x["text"] or x["name"], 160) for x in threads))
    return "\n".join(lines)


def secrets_visible(ctx: Any) -> bool:
    return str((getattr(ctx, "config", None) or {}).get("dm_secrets") or "hidden") == "visible"


def secrets(st: Any, eid: str) -> list[str]:
    """What `eid` privately knows of the cases (spec 029's graph): the clues they hold (each node's full fact) and
    whether they are a case's subject. Never shown to the DM unless the secrets arm is on."""
    from engine.gen.case import cases

    out: list[str] = []
    for c in cases(st).values():
        if (c.get("solution") or {}).get("subject", {}).get("id") == eid:
            out.append(f"you are the one the matter turns on: {_flat(c.get('about') or c['nodes'][0]['fact'], 200)}")
        for n in c["nodes"]:
            if n.get("found"):
                continue
            if any(p.get("holder") == eid and p.get("status") not in ("lost", "found") for p in n["placements"]):
                out.append(str(n["fact"]))
    return out


def _held_mood(st: Any, eid: str) -> str | None:
    from engine.dm.answer import held

    h = held(st, eid)
    return f"{MOOD.get(str(h['band']), h['band'])} ({h['why']})" if h else None


# ------------------------------------------------------------------------------------------- tools


def tool(ctx: TurnContext, t: Turn, call: dict[str, Any]) -> str:
    name = str(call.get("tool") or "")
    fn = {"propose_roll": _propose_roll, "state": _state, "change": _change, "recall": _recall,
          "reveal_clue": _reveal_clue, "mood": _mood}.get(name)
    if fn is None:
        return f"no tool {name!r}"
    try:
        out = fn(ctx, t, call)
    except Exception as e:  # noqa: BLE001 - a tool that fails tells the DM so; it never fails the turn
        out = f"REFUSED: the {name} tool failed: {type(e).__name__}: {_flat(e, 200)}"
    if out.startswith("REFUSED"):
        t.stats["refusals"].append({"tool": name, "args": _args(call), "why": out[:200]})
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


def _acting(st: Any, eid: str | None, *, here: bool = True) -> str:
    """Why `eid` cannot act now (unknown, dead, down, gone or not here), or ""."""
    from engine.harm.state import DEAD, harm_state, is_down
    from engine.retrieve.scene import pc_id
    from engine.world.scenes import cast_present

    if eid is None or eid not in st.entities:
        return f"no one on record called {eid!r}"
    e = st.entities[eid]
    if e.exists != "exists" or harm_state(st, eid) == DEAD:
        return f"{_name(st, eid)} is dead or gone"
    if is_down(st, eid) or st.fact_value(eid, "defeated"):
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
    target = _id(st, c.get("target"))
    if target is not None and target not in st.entities:
        return f"REFUSED: no one or nothing on record called {target!r} (use an id from the situation, or none)"
    kind = str(c.get("change_kind") or "none")
    what, whom = _id(st, c.get("change_what")), _id(st, c.get("change_whom"))
    change = None
    if kind != "none":
        change = Change(kind=kind, what=what if what in st.entities else None,
                        whom=whom if whom in st.entities else None,
                        description=None if what in st.entities else (str(c.get("change_what") or "") or None))
    goal = str(c.get("goal") or "").strip() or "act"
    how = str(c.get("how") or "").strip() or None
    verb = str(c.get("verb") or "") or None
    beat = Beat(id=tx.mint(ids.BEAT), actor=pc, intent=goal, method=how or goal, how=how, target=target,
                restatement=goal[:1].upper() + goal[1:], verb=verb, speech=verb == "verb.talk",
                against_will=bool(target and st.entities[target].kind in ("npc", "adversary")
                                  and verb in ("verb.strike", "verb.grapple", "verb.force")),
                declared_seq=st.last_seq, change=change)
    t.env.proposal = c  # what the code framer reads (difficulty, attribute, stakes)
    res = run_beats(t.env, [BeatPlan(beat=beat, intent_verbs=[str(verb or "").removeprefix("verb.")])])
    _take(t.rec, res, t.oof, None)
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
        if stakes != "safe" and sctx.stakes_menus:  # the first stakes source the rules accept here (01.6.9)
            for src, m in sctx.stakes_menus.items():
                if src != "none" and m["threatened"] and m["alternate"]:
                    alt = next((x for x in m["alternate"] if x != m["threatened"][0]), m["alternate"][0])
                    cands.append({**d, "stakes_heavy": stakes == "dire", "stakes": {
                        "source": src, "threatened_cost": {"menu_id": m["threatened"][0], "form_intent": "",
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
    npc = _id(st, c.get("npc"))
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
    if a.ref:
        return f"POINTER: {_name(st, npc)} doesn't know, but points the player on. Deliver: {learned}"
    return f"CLUE (deliver it plainly, in their voice; the player now knows it): {learned}"


def _mood(ctx: TurnContext, t: Turn, c: dict[str, Any]) -> str:
    from engine.dm.answer import willingness

    st = ctx.state
    npc = _id(st, c.get("npc"))
    why = _acting(st, npc)
    if why:
        return f"REFUSED: {why}"
    assert npc is not None
    band, reason = willingness(ctx, npc)
    mood = MOOD.get(band, band)
    cost = str(c.get("ask_cost") or "none")
    cell = ceiling(ctx.rules, mood, cost)
    t.stats["ceilings"].append({"npc": npc, "mood": mood, "cost": cost, "ceiling": cell})
    return (f"{_name(st, npc)}: mood toward you {mood} ({reason}). For an ask that costs them {cost}: at most "
            f"'{_cell_words(ctx.rules, cell)}'. A fact about them, not an order: react at or below it, in their voice.")


def ceiling(rules: Any, mood: str, cost: str) -> str:
    """T-12-19: the cell for (mood, cost), a lookup in `oracles.yaml#tbl.npc_ceiling`."""
    tbl = rules.table("tbl.npc_ceiling")
    row = next((r for r in tbl["results"] if r["range"] == mood), None)
    return str((row or {}).get("by_cost", {}).get(cost, "partial"))


def _cell_words(rules: Any, cell: str) -> str:
    return str(rules.table("tbl.npc_ceiling").get("cells", {}).get(cell, cell))


_GRANT_RANK = {"help": 0, "price": 1, "partial": 2, "partial_or_refuse": 3, "refuse": 4, "refuse_may_escalate": 4}


def _asks(ctx: TurnContext, t: Turn, asks: list[Any]) -> None:
    """Log each ask the DM says it granted against the ceiling (never blocks): a grant above the cell is a
    violation. The cell comes from the mood held for the scene (rolled now if it was not)."""
    from engine.dm.answer import willingness

    st = ctx.state
    for a in asks:
        if not isinstance(a, dict):
            continue
        npc = _id(st, a.get("npc"))
        if npc not in st.entities or _acting(st, npc):
            continue
        band, _ = willingness(ctx, npc)
        cell = ceiling(ctx.rules, MOOD.get(band, band), str(a.get("cost") or "none"))
        granted = str(a.get("granted") or "refuse")
        row = {"npc": npc, "mood": MOOD.get(band, band), "cost": a.get("cost"), "ceiling": cell, "granted": granted}
        t.stats.setdefault("asks", []).append(row)
        if _GRANT_RANK.get(granted, 4) < _GRANT_RANK.get(cell, 4):
            t.stats["ceiling_violations"].append(row)


# ------------------------------------------------------------------------------------------- change


def _change(ctx: TurnContext, t: Turn, c: dict[str, Any]) -> str:
    tx = ctx.need_tx()
    st = tx.state
    kind = str(c.get("kind") or "")
    pc = t.rec.pc or ""
    who, what, to = _id(st, c.get("who")), _id(st, c.get("what")), _id(st, c.get("to"))
    amount = int(c.get("amount") or 0)
    if kind == "coin":
        return _coin(ctx, t, payer=who, payee=to, amount=amount)
    if kind == "give_item":
        return _give(ctx, item=what, to=to)
    if kind == "new_item":
        name = str(c.get("what") or "").strip()
        holder = to or pc
        why = _acting(st, holder)
        if why or not name:
            return f"REFUSED: {why or 'name the item'}"
        eid = ids.entity_id("item", name, st.entities)
        tx.add(Event.of("entity_created", source="engine", rule_id="00.6.6",
                        entity=EntityRecord(id=eid, kind="item", name=name, visibility="shown")))
        tx.add(_fact(tx, eid, "holder", holder))
        return f"done: {name} ({eid}) now held by {_name(tx.state, holder)}"
    if kind in ("condition_add", "condition_remove"):
        return _condition(ctx, who, str(c.get("what") or ""), add=kind == "condition_add")
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
        card = __import__("engine.dm.packet", fromlist=["people_card"]).people_card(ctx.state, eid, rules=ctx.rules)
        return f"done: someone new is here: {eid}: " + "; ".join(x.strip() for x in card[:3])
    if kind == "travel":
        return _travel(ctx, t, to)
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


def _give(ctx: TurnContext, *, item: str | None, to: str | None) -> str:
    from engine.resolve.change import THINGS, holder_of

    tx = ctx.need_tx()
    st = tx.state
    if item is None or item not in st.entities or st.entities[item].kind not in THINGS:
        return f"REFUSED: no item on record called {item!r} (use new_item for something new)"
    holder = holder_of(st, item)
    if holder is not None and holder in st.entities and st.entities[holder].kind in ("pc", "npc", "companion",
                                                                                       "adversary"):
        why = _acting(st, holder)
        if why:
            return f"REFUSED: {_name(st, item)} is held by {_name(st, holder)}, and {why}"
    why = _acting(st, to)
    if why:
        return f"REFUSED: {why}"
    assert to is not None
    tx.add(_fact(tx, item, "holder", to))
    return f"done: {_name(st, to)} now holds {_name(st, item)}"


def _condition(ctx: TurnContext, who: str | None, cid: str, *, add: bool) -> str:
    from engine.store.conditions import apply_condition, remove_condition

    tx = ctx.need_tx()
    st = tx.state
    if who is None or who not in st.entities:
        return f"REFUSED: no one on record called {who!r}"
    cid = cid if cid.startswith("cond.") else f"cond.{ids.slug(cid)}"
    if cid not in ctx.rules.ids("cond."):
        return f"REFUSED: no condition {cid!r} in the rules (e.g. {', '.join(ctx.rules.ids('cond.')[:8])})"
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


def _travel(ctx: TurnContext, t: Turn, to: str | None) -> str:
    from engine.world.places import location, move, reachable

    st = ctx.state
    here = location(st)
    ways = {x.to for x in reachable(st, here)} if here else set()
    if to not in ways:
        return f"REFUSED: {to!r} is not reachable from here (reachable: {', '.join(sorted(ways)) or 'none'})"
    assert to is not None
    arrival = move(ctx.time_ctx(), to, end_scene=True)
    _open_scene(ctx)
    return (f"done: the character travels to {_name(ctx.state, to)}" + ("" if arrival.arrived else
                                                                         " (interrupted on the way)")
            + "\n" + situation(ctx))


def _open_scene(ctx: TurnContext) -> None:
    """A scene at the PC's place when none is open (no Director: no agenda; the DM frames it in words)."""
    from engine.world.places import location
    from engine.world.scenes import end_scene, start_scene

    st = ctx.state
    place = location(st) or (st.last_scene.place_id if st.last_scene else None)
    from engine.time import clock

    if st.scene is not None:
        end_scene(ctx.time_ctx(), "player_cut")
    mode = clock.mode_of(ctx.state.time.mode)
    start_scene(ctx.time_ctx(), place=place, mode="free" if mode == "travel" else mode, agenda="")


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


def _content(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOPS}


def _audit(ctx: TurnContext, t: Turn, passage: str) -> None:
    """Secret leaks (measured, never blocked): a present person's private case fact whose content words mostly
    appear in the passage, when no clue tool delivered it this turn."""
    from engine.world.scenes import cast_present

    st = ctx.state
    said = _content(passage)
    delivered = " ".join(c["learned"] for c in t.stats["clues"]).lower()
    for eid in cast_present(st) if st.scene is not None else []:
        for s in secrets(st, eid):
            body = s.split(":", 1)[-1]
            words = _content(body)
            if len(words) >= 3 and len(words & said) / len(words) >= 0.6 and body.strip().lower()[:40] not in delivered:
                t.stats["leaks"].append({"npc": eid, "secret": s[:200]})


def _name(st: Any, eid: str | None) -> str:
    from engine.store.views import display_name

    return display_name(st, eid) if eid and eid in st.entities else str(eid)


def _flat(s: Any, n: int | None = None) -> str:
    x = " ".join(str(s).split())
    return x if n is None or len(x) <= n else x[:n] + "…"


__all__ = ["ENGINE", "MAX_TOOLS", "Outcome", "ceiling", "enabled", "play_answer", "play_turn", "secrets",
           "situation", "step_schema", "tool"]
