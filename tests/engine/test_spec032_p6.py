"""Spec 032 P6 (lane F): `/fix` on dm-tools turns. Cases X1-X22 of specs/032-dm-tools-mvp/cases.md, the condition
origin view and removing one (`remove_fact` with a `cinst.N`; the pinned trace), and the head-to-head saves' complaints, with a scripted Fixer
over the offline stand-in. The live k/8 run is `evals/feedback_corpus.py --set dmtools --model sonnet`."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.dm import dm_tools
from engine.dm.context import TurnContext
from engine.dm.dispute import play_dm_dispute
from engine.gen.case import about_line
from engine.llm.base import Role
from engine.llm.offline import ScriptedModel
from engine.retrieve.scene import pc_id
from evals.feedback_corpus import CORPUS, open_at
from tests.engine.test_dm_tools import DM, _holder_here, change, npc_here, to_play
from tests.engine.test_spec032_cases import RULES

FIX = Role.FIXER
ROLL = {"tool": "propose_roll", "goal": "slip past the guard unseen", "verb": "verb.sneak", "target": "",
        "how": "keeping to the shadows", "attribute": "agility", "difficulty": "moderate",
        "why_uncertain": "she is watching", "stakes": "risky", "nonlethal": False, "fail_cost": "none",
        "change_kind": "none", "change_what": "", "change_whom": ""}


def say(passage: str, *calls: dict[str, Any]) -> dict[str, Any]:
    return {"calls": list(calls), "passage": passage, "said": [], "asks": []}


def p(kind: str, **kw: Any) -> dict[str, Any]:
    return {"kind": kind, "turn": "", "subject": "", "key": "", "value": "", "quantity": "", "amount": "",
            "fact_id": "", "evidence": [], **kw}


def look(*calls: tuple[str, str | None]) -> dict[str, Any]:
    return {"calls": [{"tool": t, "arg": a or ""} for t, a in calls], "final": False, "complaints": []}


def decide(*props: dict[str, Any], turn: str | None = "", verdict: str = "player_right", found: str = "Found it.") -> dict:
    return {"calls": [], "final": True, "complaints": [{"believes": "", "category": "contradiction", "turn": turn or "",
                                                         "verdict": verdict, "found": found,
                                                         "proposals": list(props)}]}


def state(tmp: Path, x: str, **cfg: Any) -> tuple[Any, ScriptedModel, str]:
    """A dm-tools game whose last turn is in state X1-X5; returns (game, model, that turn's id)."""
    game, model = to_play(tmp, **cfg)
    npc = npc_here(game)
    if x == "X1":  # plain talk: a recall, no writes
        model.push(DM, say("She nods.", {"tool": "recall", "query": "the road"}), say("She nods."))
        r = game.submit("I say hello.")
    elif x == "X2":  # an OFFER open
        model.push(DM, say("You edge along.", {**ROLL, "target": npc}))
        r = game.submit("I sneak past her.")
    elif x == "X3":  # rolled and resolved
        model.push(DM, say("You edge along.", {**ROLL, "target": npc}))
        game.submit("I sneak past her.")
        model.push(DM, *[say("It is done.")] * 3)
        r = game.answer("commit")
        while r.pause is not None:
            r = game.answer(r.pause.choices[-1].id)
    elif x == "X4":  # a change call
        pc = pc_id(game.store.state)
        model.push(DM, say("She hands you coins.", change(kind="coin", who=npc, to=pc, amount=3, note="pay")),
                   say("She hands you coins."))
        r = game.submit("I ask for my pay.")
    else:  # X5: a clue revealed
        h, case, node = _holder_here(game)
        model.push(Role.CLUE, {"about": "1", "part": "none"})
        q = f"What do you know about {about_line(game.store.state, case, node).split(' (')[0]}?"
        model.push(DM, say("She tells you.", {"tool": "reveal_clue", "npc": h, "question": q}), say("She tells you."))
        r = game.submit("I ask her what she knows.")
    return game, model, r.turn_id or ""


def fixer_saw(model: ScriptedModel) -> str:
    return "\n".join(pk.message for r, pk in model.calls if r == FIX)


# ------------------------------------------------------------------------------- X1-X20: 5 states x 4 report kinds

KINDS = ("explained", "corrected", "taken_back", "not_found")
# what code honestly does per cell. Since P4 every exchange passes time (the world step), so even the talk turn (X1)
# and the unrolled OFFER turn (X2) wrote something and are taken back as such [merge P4+P6]
EXPECT: dict[tuple[str, str], str] = {}


@pytest.mark.parametrize("x", ["X1", "X2", "X3", "X4", "X5"])
@pytest.mark.parametrize("kind", KINDS)
def test_x1_x20_every_turn_state_and_report_kind(tmp_path: Path, x: str, kind: str) -> None:
    game, model, tid = state(tmp_path, x)
    coin0 = game.store.state.quantities[pc_id(game.store.state)]["coin"].current  # type: ignore[index]
    final = {"explained": decide(p("explain"), turn=tid),
             "corrected": decide(p("refund", quantity="coin", amount="2", evidence=[tid]), turn=tid),
             "taken_back": decide(p("take_back", turn=tid, evidence=[tid]), turn=tid),
             "not_found": decide(turn="", verdict="unclear", found="")}[kind]
    model.push(FIX, look(("turn", tid), ("calls", tid)), final, final)
    r = game.dispute("that was wrong")
    tr = game.store.turn(r.turn_id)
    assert tr is not None and tr.parts and tr.parts[0].cls == "DISPUTE"
    s = tr.screen["dm_tools"]
    assert s["fix"] is True and s["kind"] == EXPECT.get((x, kind), kind), (s["kind"], r.text())
    assert "Now:" in r.text() and tr.delivered_verbatim == r.text()
    assert "DM tool calls" in fixer_saw(model) and "returned:" in fixer_saw(model)  # the turn's tool log, its calls
    assert Role.NARRATOR not in [ro for ro, _ in model.calls[-6:]]  # the answer is its blocks: no Narrator call
    st = game.store.state
    coin = st.quantities[pc_id(st)]["coin"].current  # type: ignore[index]
    if kind == "corrected":
        assert coin == coin0 + 2
    if (x, kind) == ("X4", "taken_back"):
        assert coin == coin0 - 3  # the pay is undone
    if (x, kind) in (("X2", "taken_back"),):
        assert st.open_pause() is None  # the offer is withdrawn


def test_the_next_dm_turn_sees_the_correction(tmp_path: Path) -> None:
    game, model, tid = state(tmp_path, "X1")
    model.push(FIX, look(("turn", tid)), decide(p("explain"), found="The narration slipped: she never left."),
               decide(p("explain"), found="The narration slipped: she never left."))
    game.dispute("she left, then she was here")
    model.push(DM, say("Fine."))
    game.submit("I go on.")
    dm_packet = [pk.message for r, pk in model.calls if r == DM][-1]
    assert "she never left" in dm_packet and "Now:" in dm_packet


# ------------------------------------------------------------------------------- X21, X22, re-frame and dropping


def test_x21_a_reframe_plays_the_dm_turn_again_with_the_note_and_no_framer_call(tmp_path: Path) -> None:
    game, model, tid = state(tmp_path, "X2")
    npc = npc_here(game)
    reframe = decide(p("reframe", value="she is half asleep at her post"), turn=tid)
    model.push(FIX, look(("turn", tid)), reframe, reframe)
    model.push(DM, say("She dozes; you ease along the wall.",
                       {**ROLL, "target": npc, "goal": "ease past the dozing guard", "difficulty": "easy"}))
    n = len(model.calls)
    r = game.dispute("the offer ignores that she is half asleep")
    roles = [ro for ro, _ in model.calls[n:]]
    assert Role.FRAMER not in roles and Role.NARRATOR not in roles  # X21: the code framer; the DM's prose
    rerun = [pk.message for ro, pk in model.calls[n:] if ro == DM][0]
    assert "half asleep" in rerun and "withdrawn" in rerun and "I sneak past her." in rerun
    assert r.pause is not None and r.pause.kind == "offer"
    assert "Ease past the dozing guard" in r.text() and r.fiction == "She dozes; you ease along the wall."
    s = game.store.turn(r.turn_id).screen["dm_tools"]
    assert s["fix"] and [t["tool"] for t in s["tools"]] == ["propose_roll"]
    assert "Slip past the guard" not in game.store.state.open_pause().prompt  # type: ignore[union-attr]
    # the new OFFER is the dm engine's: answering it rolls and the DM narrates
    model.push(DM, *[say("You slip by.")] * 3)
    r2 = game.answer("commit")
    assert r2.pause is None or r2.pause.kind == "near_miss"


def test_x22_a_correction_never_delivers_a_clue(tmp_path: Path) -> None:
    game, model, tid = state(tmp_path, "X2")
    h, case, node = _holder_here(game)
    q = f"What do you know about {about_line(game.store.state, case, node).split(' (')[0]}?"
    pc = pc_id(game.store.state)
    known = dict(game.store.state.knowledge.get(pc) or {})
    reframe = decide(p("reframe", value="she would rather talk"), turn=tid)
    model.push(FIX, look(("turn", tid)), reframe, reframe)
    model.push(DM, say("She shrugs.", {"tool": "reveal_clue", "npc": h, "question": q}), say("She shrugs."))
    r = game.dispute("she wanted to talk, not be snuck past")
    events = [e for e in game.store.events() if e.turn_id == r.turn_id]
    assert not any(e.type == "knowledge_recorded" for e in events)
    assert dict(game.store.state.knowledge.get(pc) or {}) == known
    s = game.store.turn(r.turn_id).screen["dm_tools"]
    assert s["clues"] == [] and all(t["tool"] != "reveal_clue" for t in s["tools"])
    # and a set_fact on the clue trail stays refused (INV-10)
    model.push(FIX, look(("turn", tid)), *[decide(p("set_fact", subject=h, key="clue.x", value="the answer",
                                                    evidence=[tid]), turn=tid)] * 2)
    r = game.dispute("she knows more")
    assert "Not done" in r.text()


def test_dropped_and_made_entries_show_in_the_turn_view(tmp_path: Path) -> None:
    game, model = to_play(tmp_path)
    pc = pc_id(game.store.state)
    add = change(kind="condition_add", who=pc, what="cond.prone", note="falls")
    model.push(DM, say("", add, add), say("The beast circles.", {**ROLL, "verb": "verb.strike", "goal": "hit it",
                                                                 "target": "the pale beast"}))
    r = game.submit("I swing at the beast.")
    tid = r.turn_id
    model.push(FIX, look(("turn", tid)), *[decide(p("explain"), turn=tid)] * 2)
    game.dispute("what happened there")
    seen = fixer_saw(model)
    last = [pk.message for r, pk in model.calls if r == FIX][-1]
    assert last.count("[DROPPED: not done]") == 1  # the second breach only
    assert "new on record:" in seen and "beast" in seen


def test_the_secrets_arm_private_lines_never_reach_the_fixer(tmp_path: Path) -> None:
    game, model = to_play(tmp_path, dm_secrets="visible")
    _holder_here(game)
    model.push(DM, say("You look around.", {"tool": "state", "about": "here"}), say("You look around."))
    r = game.submit("I look around.")
    assert "PRIVATE" in [pk.message for ro, pk in model.calls if ro == DM][-1]  # the DM saw them
    model.push(FIX, look(("turn", r.turn_id), ("calls", r.turn_id)), *[decide(p("explain"))] * 2)
    game.dispute("who knows what")
    assert "PRIVATE" not in fixer_saw(model)


def test_replay_plays_the_dm_turn_again_on_a_copy(tmp_path: Path) -> None:
    game, model, tid = state(tmp_path, "X4")
    model.push(DM, say("Again she pays.", change(kind="coin", who=npc_here(game), to=pc_id(game.store.state),
                                                 amount=3, note="pay")), say("Again she pays."))
    n = len(model.calls)
    coin = game.store.state.quantities[pc_id(game.store.state)]["coin"].current  # type: ignore[index]
    model.push(FIX, look(("replay", tid)), *[decide(p("explain"))] * 2)
    game.dispute("did she pay")
    seen = fixer_saw(model)
    assert "played again by the DM on a copy" in seen and "Again she pays." in seen
    assert Role.READER not in [ro for ro, _ in model.calls[n:]]  # not the pipeline's Reader
    assert game.store.state.quantities[pc_id(game.store.state)]["coin"].current == coin  # type: ignore[index]


# ------------------------------------------------------------------------------- conditions: origin and removal


def _fix_on_save(tmp: Path, save: str, turn: str, report: str, script: list[dict[str, Any]]) -> tuple[Any, Any, Any]:
    store = open_at(CORPUS / save, turn, tmp)
    fixer = ScriptedModel({FIX: script})
    ctx = TurnContext.for_store(store, model=fixer, rules=RULES, config={"engine": dm_tools.ENGINE})
    return play_dm_dispute(ctx, report), store, fixer


def test_pinned_real_case_the_origin_is_shown_and_the_pin_removed(tmp_path: Path) -> None:
    """playtest-20261010-175211-fighter-dm-tools turn.16 (pinned-trace.md): a footing cost in turn.4 put cond.pinned
    on the PC with the PC as holder; the Fixer could not see where it came from or remove it."""
    report = ("The game says I'm \"pinned\" and must break free, but nobody has grabbed me. I'm behind the bar with "
              "the woman. Who is pinning me?")
    fix = decide(p("remove_fact", fact_id="cinst.1", evidence=["turn.4"]), turn="turn.4")
    out, store, fixer = _fix_on_save(tmp_path, "dmtools-175211-fighter.db.gz", "turn.16", report,
                                     [look(("entity", "pc")), fix, fix])
    try:
        first = fixer.calls[0][1].message
        assert "cinst.1: pinned" in first and "in turn.4" in first and "frame.1" in first  # the opening shows it
        seen = "\n".join(pk.message for _, pk in fixer.calls)
        assert "conditions on record (where each came from):" in seen
        st = store.state
        assert not any(c.condition_id == "cond.pinned" for c in st.conditions_on(pc_id(st) or ""))
        assert "no longer pinned" in out.response.text() and "Now:" in out.response.text()
        assert "was" in out.response.text().split("Now:")[1]  # the Now line shows the change
        assert out.turn_record.screen["dm_tools"]["kind"] == "corrected"
        # the same path as every proposal: the correction is ledgered and can be taken back like any write
        recs = [r for r in st.meta.get("corrections") or [] if isinstance(r, dict) and r.get("type") == "dispute"]
        assert recs and "remove_fact" in recs[-1].get("done_kinds", [])
    finally:
        store.close()


def test_removing_a_condition_guards(tmp_path: Path) -> None:
    game, model = to_play(tmp_path)
    model.push(DM, say("You fall.", change(kind="condition_add", who=npc_here(game), what="cond.prone")),
               say("She falls."))
    r = game.submit("I trip her.")
    tid = r.turn_id
    inst = next(c for c in game.store.state.conditions.values() if c.condition_id == "cond.prone")
    cases = [  # (proposal, looked at its holder, removed?)
        (p("remove_fact", fact_id=inst.instance_id, evidence=[tid]), False, False),  # its id never seen: INV-9
        (p("remove_fact", fact_id="cinst.999", evidence=[tid]), True, False),  # no such condition
        (p("remove_fact", fact_id=inst.instance_id, evidence=[tid]), True, True),  # seen: off, on whoever has it
    ]
    for prop, looked, removed in cases:
        calls = [("turn", tid), ("entity", inst.target)] if looked else [("turn", tid)]
        model.push(FIX, look(*calls), *[decide(prop, turn=tid)] * 2)
        out = game.dispute("she is not prone")
        assert (inst.instance_id not in game.store.state.conditions) is removed, (prop, out.text())


def test_removing_a_condition_refuses_a_wound(tmp_path: Path) -> None:
    from engine.dm.dispute import _remove_condition
    from engine.store.events import ConditionInstance

    game, _ = to_play(tmp_path)
    st = game.store.state
    pc = pc_id(st)
    inst = ConditionInstance(instance_id="cinst.77", condition_id="cond.wound_arm", target=pc or "", severity="S2",
                             remaining="until:treated")
    st.conditions["cinst.77"] = inst
    with game.store.transaction(None) as tx:
        status, words = _remove_condition(st, tx, p("remove_fact", fact_id="cinst.77"), "", RULES)
    assert status == "not" and "Vitality" in words


# ------------------------------------------------------------------------------- the head-to-head saves' complaints

SAVED = [  # (save, /fix turn, report, the turn the evidence is in, a word the tools must show from it)
    ("dmtools-152037-talker.db.gz", "turn.13", "Magby's last line says Kazain \"has not yet come down from the stairs\","
     " but he never went upstairs.", "turn.12", "stairs"),
    ("dmtools-152037-talker-secrets.db.gz", "turn.10", "Tobbo tells me to take the bowl up to Agnes, but I already "
     "brought her the bread and broth.", "turn.9", "bowl"),
    ("dmtools-153123-fighter-secrets.db.gz", "turn.9", "The result line says \"Changed: your opponent worn\" which is "
     "garbled.", "turn.8", "worn"),
    ("dmtools-153123-fighter.db.gz", "turn.5", "The passage says the afternoon light won't hold, but the clock says "
     "morning.", "turn.4", "afternoon"),
]


@pytest.mark.parametrize(("save", "turn", "report", "about", "word"), SAVED, ids=["kazain", "bowl", "worn", "afternoon"])
def test_saved_complaints_are_answered_from_the_dm_record(tmp_path: Path, save: str, turn: str, report: str,
                                                          about: str, word: str) -> None:
    fix = decide(p("explain"), turn=about, found=f"The record is right; the {word} line slipped.")
    out, store, fixer = _fix_on_save(tmp_path, save, turn, report, [look(("turn", about), ("calls", about)), fix, fix])
    try:
        seen = "\n".join(pk.message for _, pk in fixer.calls)
        assert word in seen.split("INVESTIGATION SO FAR:")[1]  # the evidence reached the Fixer through its tools
        assert "DM tool calls" in seen and "dm (" in seen  # the DM's tool log and its call
        assert "PRIVATE" not in seen
        text = out.response.text()
        assert "Now:" in text and out.turn_record.screen["dm_tools"]["fix"]
    finally:
        store.close()
