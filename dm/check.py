"""The continuity checker (Jake, 2026-10-18; built into the game 2026-10-19). After the DM's reply is written and before
the player sees it, a second Sonnet call reads the reply, the last CHECK_WINDOW turns word for word and the notebook
entries the reply names, and lists what clashes (the offline tests: evals/autoloop on the autoloop branch,
haiku_check.py `quote` and quote_cutoffs.py). Each problem has a score from 1 to 5, topics, the reply's words, the
earlier line it clashes with (copied word for word, and code checks the line is really there), and a fix.

What the game does with a problem is decided here, by topic: a per-topic score cutoff says whether to act; time,
items and mechanics (and the number of enemies in a fight) go back to the DM, who writes the reply again; the rest are
fixed in the text with the checker's replacement sentence. Nothing here infers a story fact: only the DM's tool calls
set them."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Any

from dm import lore as notebook
from dm import model

ENABLED = True
CHECK_MODEL = "claude-sonnet-5-5"
CHECK_WINDOW = 5  # turns before the reply, word for word (10 caught fewer and cost 40% more)
MAX_ENTRIES, MAX_CHARS = 12, 100_000
# Act at this score or higher, by topic (leave-one-out on 165 rounds: 71 of 105 contradictions caught, 19 of 60 clean
# rounds flagged). A problem with several topics is acted on at the lowest of its topics' cutoffs.
CUTOFF = {"count": 2, "place": 2, "items": 2, "status": 2, "mechanics": 2,
          "distance": 3, "deeds": 3, "identity": 3, "time": 4}
TOPICS = list(CUTOFF)
BACK_TO_DM = {"time", "items", "mechanics"}  # the fix also touches the clock, sheet or notebook: the DM writes again

SYSTEM = (
    "You check a solo D&D game run by an AI DM for continuity errors. You get the DM's notebook entries, the "
    "turns before, and the DM's NEW REPLY. Find any statement in the NEW REPLY that contradicts EARLIER PLAY or "
    "the NOTEBOOK, or contradicts another statement in the same reply: numbers and counts, times, dates and ages, "
    "distances and travel times, places, who did or said what, who has what. Something that changed because of "
    "events in play is not a contradiction; neither is something new that clashes with nothing; neither is a "
    "character lying or being wrong, if the story shows that. Only flag what the text shows plainly."
    " List each problem with a severity from 1 to 5. 1: a nitpick no player would notice (the clock a few minutes off, "
    "loose wording). 2: a careful player might notice but wouldn't mind (a crowd of 'about twenty' becomes 'thirty'). "
    "3: a player paying attention would notice (a named NPC's title or terms change; a distance or travel time shrinks). "
    "4: it changes something the player relied on (a promised payment, an item they hold, how many enemies remain). "
    "5: it breaks the story (a dead character acting, a place in two directions, a count that can't be). Quote the NEW "
    "REPLY's exact words: in quote, the whole sentence (or sentences) that has to change, from its first word to its "
    "final punctuation, never a part of a sentence, and replacement is the whole sentence written again to take its "
    "place; and in clashes_with name the earlier line it clashes with. Then say how to fix it: fix 'text' "
    "with a replacement for the quoted words when changing the words alone fixes it, or fix 'dm' with an empty "
    "replacement when the fix also needs a change to the character sheet, fight, clock or notebook (hit points, "
    "items, gold, enemy numbers, time passing). Return an empty list if none."
    " For every problem, copy the earlier line it clashes with into earlier_quote, word for word from the "
    "NOTEBOOK, EARLIER PLAY or the NEW REPLY itself, and say in earlier_where which (notebook, earlier play, or same "
    "reply). If you can't point to such a line, it is not a contradiction: something not mentioned before, or a "
    "character guessing or lying, is not a clash. Check in particular: dice, hit point and spell lines against what "
    "the narration says happened; counts and times within the same reply; deals, orders and plans already made or "
    "cancelled. Score by what it does to the player: anything that would change what the player decides, or makes "
    "a plan impossible (a travel time, a deadline, a count of enemies), is at least 3. Give the problem's topics: "
    "count (how many people or things), time (clock, dates, days passed, ages, how long ago), distance (how far, "
    "travel time), place (where things are, directions), deeds (who did or said what), items (who has what, money, "
    "gear, deals), identity (names, roles, relationships, backstory, looks), status (alive, wounded, bound, where "
    "someone is now), mechanics (hit points, dice, spells, rules); one or two.")
SCHEMA: dict[str, Any] = {
    "type": "object", "additionalProperties": False, "required": ["problems"],
    "properties": {"problems": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["quote", "clashes_with", "severity", "fix", "replacement", "earlier_quote", "earlier_where",
                     "topics"],
        "properties": {"quote": {"type": "string"}, "clashes_with": {"type": "string"},
                       "severity": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
                       "fix": {"type": "string", "enum": ["text", "dm"]},
                       "replacement": {"type": "string"},
                       "earlier_quote": {"type": "string"},
                       "earlier_where": {"type": "string", "enum": ["notebook", "earlier play", "same reply"]},
                       "topics": {"type": "array", "items": {"type": "string", "enum": TOPICS}}}}}}}

HAND_BACK = (
    "[Not from the player: a check of your reply before it was shown] Your reply this turn was NOT shown to the "
    "player. A checker found {what}:\n{problems}\n\nWrite the reply again with `reply`, whole, so that none of this "
    "clashes. What you already recorded this turn stays recorded: call a tool only for what the fix changes. If the "
    "checker is wrong (the story shows the change, or the line it quotes was a lie or a guess), write the reply as it "
    "was.")

# One structured call to the checker model: (backend, system, user text) -> the parsed answer, or raises model.Failed.
Ask = Callable[[str, str, str], Awaitable[dict[str, Any]]]


def norm(s: str) -> str:
    return " ".join(s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
                    .replace("*", "").split()).lower()


def context(lore: dict[str, Any], transcript: list[dict[str, Any]], reply: str) -> str:
    """What the checker reads: the notebook entries the reply names (as the notebook was before this turn), the last
    CHECK_WINDOW turns word for word, and the reply. `transcript` ends with the player's line of this turn."""
    turn = notebook.now(transcript)
    before = transcript[:max((i for i, e in enumerate(transcript) if e["kind"] == "player"), default=0)]
    earlier = "\n\n".join(x for n in range(max(turn - CHECK_WINDOW, 0), turn) if (x := notebook.turn_text(transcript, n)))
    entries = []
    for n in notebook.mentioned(lore, reply)[:MAX_ENTRIES]:
        try:
            entries.append(notebook.look(lore, [n], before))
        except Exception:  # noqa: BLE001 - an entry that can't be shown is left out
            pass
    s = ("NOTEBOOK (the DM's notes, as they were before the new reply)\n" + "\n\n".join(entries)
         + f"\n\nEARLIER PLAY (the last {CHECK_WINDOW} turns, word for word)\n{earlier}\n\nNEW REPLY\n{reply}")
    return s if len(s) <= MAX_CHARS else s[:MAX_CHARS // 3] + "\n[...]\n" + s[-2 * MAX_CHARS // 3:]


def found(p: dict[str, Any], text: str) -> bool:
    """The earlier line is really there: in the reply for 'same reply', otherwise before it."""
    before, _, reply = text.rpartition("\nNEW REPLY\n")
    q = norm(p.get("earlier_quote") or "")
    return bool(q) and q in norm(reply if p.get("earlier_where") == "same reply" else before)


def acts(p: dict[str, Any]) -> bool:
    topics = [t for t in p.get("topics") or [] if t in CUTOFF]
    return bool(topics) and p["severity"] >= min(CUTOFF[t] for t in topics)


def sort(problems: list[dict[str, Any]], reply: str, in_fight: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """(problems for the DM, problems fixed in the text). A text fix needs the quoted words to be in the reply, and a
    replacement; anything else that was kept goes back to the DM."""
    back, text = [], []
    for p in problems:
        topics = set(p["topics"])
        if (topics & BACK_TO_DM or (in_fight and "count" in topics) or p["fix"] == "dm"
                or not p["replacement"].strip() or p["quote"] not in reply):
            back.append(p)
        else:
            text.append(p)
    return back, text


def kept(answer: dict[str, Any], state: str) -> list[dict[str, Any]]:
    return [p for p in answer.get("problems", []) if found(p, state) and acts(p)]


def describe(problems: list[dict[str, Any]]) -> str:
    return "\n".join(f"- You wrote \"{p['quote']}\" but earlier: \"{p['earlier_quote']}\" ({p['clashes_with']})."
                     + (f" Suggested wording: \"{p['replacement']}\"." if p["replacement"].strip() else "")
                     for p in problems)


async def ask_model(backend: str, system: str, text: str) -> dict[str, Any]:
    """One call to the checker model, on the way the game is played: the API (the browser too), or Claude Code."""
    if backend == "sdk":
        from dm import sdk  # here: the browser has no Agent SDK
        return await sdk.structured(CHECK_MODEL, system, text, SCHEMA)
    r = await model.send({
        "model": CHECK_MODEL, "max_tokens": 6000, "system": system, "messages": [{"role": "user", "content": text}],
        "output_config": {"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}}})
    return json.loads(next(b["text"] for b in r["content"] if b["type"] == "text"))


async def check(backend: str, lore: dict[str, Any], transcript: list[dict[str, Any]], reply: str,
                ask: Ask | None = None) -> tuple[list[dict[str, Any]], str]:
    """The problems to act on in `reply`, and the state the checker read. Raises model.Failed or ValueError if the
    call or its answer is no good (the caller shows the reply as it is)."""
    state = context(lore, transcript, reply)
    answer = await (ask or ask_model)(backend, SYSTEM, state)
    return kept(answer, state), state
