"""Endings (FR-009; 11.13; PR-11-6 in its simple Milestone-1 form; T070).

    due = ending_due(state)                 # "death" | "retirement" | "career_end" | None (no epilogue yet)
    resp = run_epilogue(ctx)                # the epilogue (narrated + checked) and the `ending` pause
    resp = answer_ending(ctx, "new_character")   # creation again in this world (engine.dm.creation)
    resp = ask_retire(ctx)                  # "I retire": a confirmation pause (flow "retire", 11.13.1 "always")
    resp = answer_retire(ctx, "retire")     # writes career.ending = retirement, then the epilogue

Death is only ever written by engine/harm (both keys of 07.3.1, after the warning and the Threshold); this module
reads `engine.harm.threshold.ending_state` after a turn and runs the epilogue once per character.

The epilogue (11.13.3 steps, coarse in M1): 1 the ending (death -> `remembered`, a retirement or career end ->
`retire_to_a_life`); 3 the legend rank from the chronicle (renown is not tracked in M1: rank 1 "a local name" when
the chronicle names the character, else 0) and the period's events (up to five chronicle lines naming the
character, in time order); 4 every open thread is left to the world; 6 the character becomes an NPC at home (or
lies dead): fact `exists`; 10 the chronicle's retirement/death entry and the legacy record (meta `legacy.<pc>`).
Settlement, bequests, the timeskip, successors and inheritance (steps 2, 5, 7-9) are not built in M1 (logged as
`log.coarse`). The DM words only the epilogue prose, through the narrator and the checker like any narration.
"""

from __future__ import annotations

import re
from typing import Any

from engine.dm import oof
from engine.dm.adjudication import AdjudicationRecord
from engine.dm.context import TurnContext
from engine.dm.response import Choice, Flags, OofBlock, Pause, Response
from engine.dm.seed_flow import PHASE_KEY, close_pause, open_pause, present_pause
from engine.store.events import PauseRecord
from engine.store.projection import WorldState
from engine.store.records import TurnRecord

FLOW = "ending"
RETIRE_FLOW = "retire"
DONE = "ending.done"  # meta {pc: turn_id}: the epilogue ran for that character
ENDINGS = {"death": "remembered", "retirement": "retire_to_a_life", "career_end": "retire_to_a_life"}  # 11.13.2
MENU = [Choice(id="new_character", label="a new character in this world"),
        Choice(id="new_world", label="a new world (start a new game)"),
        Choice(id="quit", label="stop here for now")]
RETIRE_CHOICES = [Choice(id="retire", label="yes: retire this character (the story ends for them)"),
                  Choice(id="keep_playing", label="no: keep playing")]
_RETIRE = re.compile(r"^\W*(?:ooc:?\s*)?(?:/retire\b|i(?:\s+want\s+to|\s+would\s+like\s+to|['’]d\s+like\s+to)?\s+"
                     r"retire\b|retire\s+(?:my|this)\s+character\b)", re.IGNORECASE)


def is_retire(message: str) -> bool:  # rule: 11.13.1
    """The player's out-of-fiction request to retire the character ("I retire", "retire my character")."""
    return bool(_RETIRE.search(message or ""))


def _pc(state: WorldState) -> str | None:
    from engine.harm.threshold import active_pc

    return active_pc(state)


def ending_due(state: WorldState) -> str | None:  # rule: 11.13.1
    """The active character's ending (death, retirement, career end) when its epilogue has not run yet."""
    from engine.harm.threshold import ending_state

    pc = _pc(state)
    if pc is None:
        return None
    end = ending_state(state, pc)
    if end is None or pc in (state.meta.get(DONE) or {}):
        return None
    return end


# ------------------------------------------------------------------------------------------- the epilogue


def legend(state: WorldState, pc: str) -> tuple[int, str, list[str]]:  # rule: 11.13.3
    # coarse: 11.13.3 (renown and T-11-20 are not tracked in M1)
    """(legend rank, its words, the period's event lines): the chronicle lines naming the character, oldest first
    (at most five); rank 1 when there are any, else 0."""
    from engine.world.chronicle import chronicle

    lines = [e.text for e in chronicle(state, entity=pc) if e.kind != "retirement"][-5:]
    rank = 1 if lines else 0
    return rank, ("a local name" if rank else "unremembered"), lines


def summary(state: WorldState, pc: str, end: str) -> list[str]:  # rule: PR-11-6
    """The epilogue's only source (state, never earlier prose): the ending, the period, the threads left open."""
    from engine.world.places import location
    from engine.world.social import thread_list

    e = state.entities[pc]
    rank, words, events = legend(state, pc)
    where = location(state, pc)
    place = state.entities[where].name if where in state.entities else ""
    out = ["EPILOGUE SUMMARY (the epilogue's only source):",
           f"- {e.name}'s story ends: " + {"death": "dead", "retirement": "retired from the road",
                                          "career_end": "the career is over"}.get(end, end)
           + (f", at {place}" if place else ""),
           f"- remembered as: {words}"]
    out += [f"- from the chronicle: {t}" for t in events]
    out += [f"- left to the world: {t['name']}" for t in thread_list(state)
            if t.get("status") == "active" and t.get("name") and _shown(state, t["id"])]
    return out


def run_epilogue(ctx: TurnContext) -> Response:  # rule: PR-11-6
    # rule: 11.13.3
    """PR-11-6 (simple): write the ending's records, narrate the epilogue through the checker, open the `ending`
    pause (new_character / new_world / quit). One transaction under its own turn id, saved as `(epilogue)`."""
    from engine.dm.narration import narrate_checked
    from engine.world.chronicle import chronicle_append
    from engine.world.common import fact, meta

    store = ctx.store
    st = store.state
    pc = _pc(st)
    end = ending_due(st)
    if pc is None or end is None:
        raise ValueError("no character has reached an ending")
    turn_id = store.new_turn_id()
    ctx.call_ids = []
    with store.transaction(turn_id) as tx:
        ctx.tx = tx
        try:
            st = tx.state
            name = st.entities[pc].name
            ending = ENDINGS[end]
            rank, words, events = legend(st, pc)
            lines = summary(st, pc, end)
            exists = "dead" if end == "death" else "exists"
            if st.fact_value(pc, "exists") != exists:
                tx.add(fact(tx, pc, "exists", exists, rule_id="11.13.2", visibility="shown"))
            text = f"{name}'s road ended: " + ("dead, and remembered." if end == "death"
                                               else "retired to a life away from the road.")
            chronicle_append(ctx.time_ctx(), text, kind="death" if end == "death" else "retirement",
                             entities=[pc], source="11.13.3")
            threads = [t["id"] for t in _active_threads(st)]
            tx.add_all([
                meta(f"legacy.{pc}", {"ending": ending, "cause": end, "legend_rank": rank, "legend": words,
                                      "events": events, "threads_left_to_world": threads}, "11.13.3"),
                meta("log.coarse", {"rule": "PR-11-6", "what": "M1 epilogue: settlement, bequests, timeskip, "
                                    "successors and inheritance (11.13.3 steps 2, 5, 7-9) not built"}, "PR-11-6"),
            ])
            rec = AdjudicationRecord(turn_id=turn_id, pc=pc)
            narr = narrate_checked(ctx, rec, purpose="epilogue", extra=lines, fallback_text=_plain(lines))
            block = _epilogue_block(name, end, words, events)
            p = open_pause(tx, "ending", "What now?", MENU, None,
                           {"flow": FLOW, "pc": pc, "ending": ending, "blocks": [block.model_dump()]}, "PR-11-6")
            done = dict(st.meta.get(DONE) or {})
            tx.add_all([meta(DONE, {**done, pc: turn_id}, "PR-11-6"), meta(PHASE_KEY, "ending", "PR-11-6")])
        finally:
            ctx.tx = None
    resp = Response(turn_id=turn_id, phase="ending", fiction=narr.fiction, oof_blocks=[block], pause=Pause.of(p),
                    flags=Flags(fallback_used=narr.fallback_used, review_flag=narr.review_flag))
    store.save_turn(TurnRecord(turn_id=turn_id, input_verbatim="(epilogue)", delivered_verbatim=resp.text(),
                               model_calls=list(ctx.call_ids), draft_versions=narr.draft_versions,
                               verdicts=narr.verdicts, fallback_used=narr.fallback_used, screen=narr.screen))
    return resp


def _shown(state: WorldState, eid: str) -> bool:
    e = state.entities.get(eid)
    return e is not None and eid not in state.seals and e.visibility in ("shown", "available")


def _active_threads(state: WorldState) -> list[dict[str, Any]]:
    from engine.world.social import thread_list

    return [t for t in thread_list(state) if t.get("status") == "active"]


def _plain(lines: list[str]) -> str:
    """The fallback epilogue: the summary's lines as plain sentences."""
    return " ".join(x[2:].rstrip(".") + "." for x in lines[1:] if x.startswith("- "))


def _epilogue_block(name: str, end: str, words: str, events: list[str]) -> OofBlock:  # rule: 12.15
    head = {"death": f"{name} is dead.", "retirement": f"{name} retires from the road.",
            "career_end": f"{name}'s career is over."}.get(end, f"{name}'s story ends.")
    rest = [f"Legend: {words}."] + [f"  - {t}" for t in events] + ["What now?"]
    rest += [f"  {i}) {c.label}" for i, c in enumerate(MENU, 1)]
    return OofBlock(kind="EPILOGUE", text="\n".join([f"[EPILOGUE] {head}", *("          " + r for r in rest)]))


def present_ending(ctx: TurnContext) -> Response:
    """Resume at the ending menu: exactly the stored epilogue block and pause."""
    rec = ctx.store.state.open_pause()
    if rec is None or rec.detail.get("flow") != FLOW:
        raise ValueError("no ending menu is open")
    return present_pause(rec, "ending")


def answer_ending(ctx: TurnContext, choice_id: str) -> Response:  # rule: 11.13.1
    """The ending menu: `new_character` starts creation in this world; `new_world` and `quit` leave the menu open
    (a new world is a new game, the front end's job; quitting needs nothing: the game is saved)."""
    from engine.dm.creation import new_character

    rec = ctx.store.state.open_pause()
    if rec is None or rec.detail.get("flow") != FLOW:
        raise ValueError("no ending menu is open")
    if choice_id == "new_character":
        return new_character(ctx)
    if choice_id not in {c.id for c in MENU}:
        raise ValueError(f"{choice_id!r} is not a choice of the open pause")
    note = ("A new world is a new game: start one from the menu." if choice_id == "new_world"
            else "Saved. The menu will be here when you come back.")
    return present_pause(rec, "ending", [oof.note_block(note)])


# ------------------------------------------------------------------------------------------- retiring


def ask_retire(ctx: TurnContext) -> Response:  # rule: 11.13.1
    """11.13.1 "always": the player may retire the character, out of fiction. Confirmed first (it cannot be
    undone); a pause of flow `retire` (kind clarify) holds the question."""
    from engine.dm.seed_flow import flow_tx

    name = ctx.store.state.entities[_pc(ctx.store.state) or ""].name
    text = (f"[RETIRE] Retire {name}? Their story ends here and the epilogue is told; you can then make a new "
            "character in this world.\n" + "\n".join(f"  {i}) {c.label}" for i, c in enumerate(RETIRE_CHOICES, 1)))
    block = OofBlock(kind="CLARIFY", text=text)
    with flow_tx(ctx) as tx:
        p = open_pause(tx, "clarify", f"Retire {name}?", RETIRE_CHOICES, "keep_playing",
                       {"flow": RETIRE_FLOW, "blocks": [block.model_dump()]}, "11.13.1")
    return Response(phase="play", oof_blocks=[block], pause=Pause.of(p))


def answer_retire(ctx: TurnContext, choice_id: str) -> Response:  # rule: 11.13.1
    """`retire`: write `career.ending = retirement` and run the epilogue; anything else closes the question."""
    from engine.dm.seed_flow import flow_tx
    from engine.world.common import fact

    rec: PauseRecord | None = ctx.store.state.open_pause()
    if rec is None or rec.detail.get("flow") != RETIRE_FLOW:
        raise ValueError("no retirement question is open")
    pc = _pc(ctx.store.state)
    retire = choice_id == "retire"
    with flow_tx(ctx) as tx:
        close_pause(tx, rec, "retire" if retire else "keep_playing", "option" if choice_id in ("retire",
                                                                                            "keep_playing") else
                    "default")
        if retire and pc is not None:
            tx.add(fact(tx, pc, "career.ending", "retirement", rule_id="11.13.1", visibility="shown",
                        event_source="player"))
    if retire:
        return run_epilogue(ctx)
    return Response(phase="play", oof_blocks=[oof.note_block("Then the story goes on. What do you do?")])


def retire_choice(message: str) -> str:
    """A typed answer to the retirement question: a number, an id, or yes/no words."""
    from engine.dm.roles.interpret import direct_choice

    hit = direct_choice(message, RETIRE_CHOICES)
    if hit and hit[0] in ("retire", "keep_playing"):
        return hit[0]
    low = message.strip().lower()
    return "retire" if low.startswith(("y", "retire", "i retire")) else "keep_playing"


def ending_choice(message: str) -> str | None:
    """A typed answer to the ending menu: a number, an id, a label, or plain words."""
    from engine.dm.roles.interpret import direct_choice

    hit = direct_choice(message, MENU)
    if hit and hit[0] in {c.id for c in MENU}:
        return hit[0]
    low = message.lower()
    if "character" in low or "someone" in low:
        return "new_character"
    if "world" in low or "new game" in low:
        return "new_world"
    if any(w in low for w in ("quit", "stop", "exit", "done")):
        return "quit"
    return None


__all__ = ["DONE", "ENDINGS", "FLOW", "MENU", "RETIRE_FLOW", "answer_ending", "answer_retire", "ask_retire",
           "ending_choice", "ending_due", "is_retire", "legend", "present_ending", "retire_choice", "run_epilogue",
           "summary"]
