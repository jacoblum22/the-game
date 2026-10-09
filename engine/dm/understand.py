"""PR-12-11 step 1: understand the player's report first (12.3.6 item 3; DL-12-94; spec 014).

    complaints = understand(ctx, "I succeeded but never got the purse")
    # [{"believes": "the lift succeeded but you never got the purse", "happened": ..., "category": "ruling_question",
    #   "turn": "turn.5", "quote": "You have her restrained", "subject": "npc.murzak_red_hand",
    #   "about": "roll_or_outcome", "key": "purse", "value": ""}]

ONE `Role.UNDERSTAND` call per report reads the report with the WHOLE transcript (every play turn, oldest first,
each with the roll it committed), the people the player has seen and the calendar. Past
`pacing.yaml#feedback.understand_call.transcript_budget_tokens` it reads the current scene's turns plus the turns
holding the report's words, newest first, within the budget. It returns up to three complaints (real reports bundle
them), each `{believes, happened, category, turn, quote}` plus what it is about (`subject`, `about`, `key`,
`value`): reading the report, never judging it. Code verifies everything it returns (engine/dm/dispute.py).
"""

from __future__ import annotations

import re
from typing import Any

from engine import ids
from engine.dm.schemas import STR, Schema, arr, enum, obj

CATEGORIES = ("remembered_wrong", "rule_wrong", "contradiction", "misread", "ruling_question", "other")
# what a complaint is about: code maps each to what it checks (dispute.locate); the model never decides a write
ABOUT = ("fact", "quantity", "possession", "name", "pronoun", "season_or_time", "look_or_activity", "who_said_what",
         "roll_or_outcome", "action_reading", "other")
SEASONS = ("spring", "summer", "autumn", "winter")
MAX_COMPLAINTS = 3
BUDGET_TOKENS = 30000  # pacing.yaml#feedback.understand_call.transcript_budget_tokens (read from the rules when given)
_STOP = frozenset("that this with from have they them then into never were your there about what when which would "
                  "should could said says just only also again still been being because while game turn".split())


def understand_schema(turns: list[str] | None = None, subjects: list[str] | None = None) -> Schema:  # rule: PR-12-11
    """`{complaints: [1..3 × {believes, happened, category, turn, quote, subject, about, key, value}]}`; `turn` and
    `subject` are the transcript's turns and the people listed, or `none`."""
    turn = enum(turns or [], first="none") if turns is not None else STR
    subject = enum(subjects or [], first="none") if subjects is not None else STR
    one = obj({"believes": STR, "happened": STR, "category": enum(CATEGORIES), "turn": turn, "quote": STR,
               "subject": subject, "about": enum(ABOUT), "key": STR, "value": STR})
    out = arr(one, max_items=MAX_COMPLAINTS)
    assert out is not None
    return obj({"complaints": {**out, "minItems": 1}})


def default() -> dict[str, Any]:
    """Nothing understood: one complaint with no passage (answered "I can't find that; did you mean …?")."""
    return {"complaints": [{"believes": "", "happened": "", "category": "other", "turn": "none", "quote": "",
                            "subject": "none", "about": "other", "key": "", "value": ""}]}


def _flat(s: str, n: int | None = None) -> str:
    t = " ".join(str(s).split())
    return t if n is None or len(t) <= n else t[:n] + "…"


def season_word(state: Any) -> str:
    s = int(getattr(state.time.now, "season", 1) or 1)
    return SEASONS[(s - 1) % 4]


def play_turns(store: Any, before: str | None) -> list[Any]:
    """Every turn before `before`, oldest first (the opening and session turns too; dispute turns excluded)."""
    from engine.dm.dispute import _turns

    return list(reversed(_turns(store, before)))


def _frame_lines(store: Any) -> dict[str, list[str]]:
    """turn id -> `rolled: frame.K "<restatement>" (<verb>) -> <degree>, reach <r>` lines."""
    out: dict[str, list[str]] = {}
    degree = {getattr(e.payload, "frame_id", None): e.payload for e in store.events(types=["frame_resolved"])}
    for e in store.events(types=["frame_committed"]):
        f: dict[str, Any] = e.payload.frame  # type: ignore[attr-defined]
        b = f.get("beat") or {}
        r: Any = degree.get(e.payload.frame_id)  # type: ignore[attr-defined]
        res = f" -> {r.degree}, reach {(r.delivered or {}).get('reach') or f.get('reach')}" if r is not None else ""
        verb = str(b.get("verb") or "").removeprefix("verb.")
        out.setdefault(str(e.turn_id), []).append(
            f'  rolled: {e.payload.frame_id} "{_flat(b.get("restatement") or "", 140)}" ({verb}){res}')  # type: ignore[attr-defined]
    return out


def _block(t: Any, rolls: dict[str, list[str]]) -> str:
    return "\n".join([f'{t.turn_id} | player: "{_flat(t.input_verbatim, 300)}" | game: "{_flat(t.delivered_verbatim)}"',
                      *rolls.get(t.turn_id, [])])


def transcript(store: Any, current: str | None, words: str, budget: int = BUDGET_TOKENS) -> tuple[list[str], list[str]]:
    # rule: PR-12-11
    """(lines, turn ids): the whole transcript; past `budget` tokens (chars/4) the current scene's turns plus the
    turns holding the report's words, newest first, within the budget (12.3.6 item 3)."""
    turns = play_turns(store, current)
    rolls = _frame_lines(store)
    blocks = {t.turn_id: _block(t, rolls) for t in turns}
    if sum(len(b) for b in blocks.values()) // 4 <= budget:
        return list(blocks.values()), list(blocks)
    state = store.state
    start = state.scene.started_seq if state.scene else 0
    first_seq = {t: s for t, s in store.conn.execute("SELECT turn_id, MIN(seq) FROM events GROUP BY turn_id")}
    keys = {w for w in re.findall(r"[a-z]{4,}", words.lower()) if w not in _STOP}
    here = [t for t in turns if (first_seq.get(t.turn_id) or 0) > start]
    hits = [t for t in reversed(turns) if t not in here
            and keys & set(re.findall(r"[a-z]{4,}", (t.input_verbatim + " " + t.delivered_verbatim).lower()))]
    kept: list[Any] = []
    used = 0
    for t in [*reversed(here), *hits]:  # ponytail: newest first by word hits; rank by overlap if budgets bite
        cost = len(blocks[t.turn_id]) // 4
        if used + cost > budget and kept:
            break
        kept.append(t)
        used += cost
    kept.sort(key=lambda t: (ids.parse_counter_id(t.turn_id) or ("", 0))[1])
    return [blocks[t.turn_id] for t in kept], [t.turn_id for t in kept]


def people(state: Any, text: str) -> list[tuple[str, str]]:
    """(id, line) for the PC, the people here and every entity the player has seen named in `text` (names as the
    PC knows them, or as the narration showed them; sealed entities never)."""
    from engine.store.views import display_name

    here = set(state.scene.cast_present) if state.scene else set()
    low = text.lower()
    out = []
    for eid, e in state.entities.items():
        if eid in state.seals or e.kind in ("thread", "rumor", "clue", "faction"):
            continue
        name = e.name if len(e.name) >= 3 and e.name.lower() in low else display_name(state, eid)  # as the player saw it
        if e.kind != "pc" and eid not in here and not (len(name) >= 3 and name.lower() in low):
            continue
        pron = e.data.get("pronouns")
        out.append((eid, f"{eid}: {name}" + (f" ({pron})" if pron else "")
                    + (" [the player's character]" if e.kind == "pc" else "")))
    return out


def understand(ctx: Any, text: str) -> list[dict[str, Any]]:  # rule: PR-12-11
    # rule: 12.3.6
    """PR-12-11 step 1 `[J:enum]`: one call, the report with the whole transcript; the complaints as returned
    (validated against the schema; code verifies them)."""
    from engine.dm.oof import when_words
    from engine.dm.roles.prompts import load_prompt
    from engine.llm.base import Packet, Role, call_role

    rules = getattr(ctx, "rules", None)
    budget = BUDGET_TOKENS
    try:
        budget = int(rules.pacing["feedback"]["understand_call"]["transcript_budget_tokens"])  # type: ignore[union-attr]
    except (AttributeError, KeyError, TypeError):
        pass
    state = ctx.state
    lines, turn_ids = transcript(ctx.store, getattr(ctx, "turn_id", None), text, budget)
    who = people(state, "\n".join(lines) + " " + text)
    message = "\n".join([f'THE PLAYER\'S REPORT: "{_flat(text)}"',
                         f"NOW: {season_word(state)}, {when_words(state.time.now)}",
                         "PEOPLE (id: name, pronouns):", *(line for _, line in who),
                         "TRANSCRIPT (every turn, oldest first):", *lines])
    packet = Packet(instructions=load_prompt("understand"), core="", cards=[], view="", exchanges=[], message=message)
    res = call_role(ctx.model, Role.UNDERSTAND, understand_schema(turn_ids, [i for i, _ in who]), packet,
                    turn_id=getattr(ctx, "turn_id", None), recorder=getattr(ctx, "record_call", None),
                    default=default())
    return [dict(c) for c in (res.data.get("complaints") or [])][:MAX_COMPLAINTS] or default()["complaints"]


__all__ = ["ABOUT", "CATEGORIES", "SEASONS", "default", "people", "season_word", "transcript", "understand",
           "understand_schema"]
