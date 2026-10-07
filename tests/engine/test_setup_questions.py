"""Questions asked at a setup step get a real answer, then the question once (playtest 20261007 breaker)."""

from __future__ import annotations

from pathlib import Path

from engine.data.loader import load_rules
from engine.dm.context import TurnContext
from engine.dm.creation import CreationFlow
from engine.dm.response import Response
from engine.dm.schemas import SchemaContext, build_schema
from engine.dm.seed_flow import SeedFlow
from engine.llm.base import Role
from engine.llm.offline import OfflineModel, ScriptedModel
from tests.fixtures.game import new_store

RULES = load_rules()
WELCOME_START = "Welcome. This is an adventure told in words."


def _oracle(tmp_path: Path, model=None) -> tuple[SeedFlow, Response]:
    store = new_store(tmp_path)
    flow = SeedFlow(TurnContext.for_store(store, model=model or OfflineModel(), rules=RULES))
    flow.start()
    return flow, flow.answer("oracle")


def _to_step(flow: SeedFlow, r: Response, n: int) -> Response:
    while flow.ctx.store.state.open_pause().detail.get("step") != n:
        r = flow.submit("")
    return r


def _text(r: Response) -> str:
    return "\n".join(b.text for b in r.oof_blocks)


def test_a_question_at_a_summary_is_answered_and_only_the_prompt_returns(tmp_path: Path):
    model = ScriptedModel()
    flow, r = _oracle(tmp_path, model)
    r = _to_step(flow, r, 4)
    assert "Kinspeech (the beastfolk's language)" in _text(r) or "Kinspeech" not in _text(r)
    for _ in range(2):  # asking twice does not loop the whole screen
        model.push(Role.INTERPRET, {"choice": "details", "own_words_text": None,
                                    "answer": "Both are peoples of this land."})
        r = flow.submit("what's the difference between orc-kin and beastfolk?")
        t = _text(r)
        assert len(r.oof_blocks) == 1 and t.startswith("Both are peoples of this land.")
        assert "Orc-kin, strong and stubborn" in t and "Beastfolk, quick" in t
        assert "Here is a little more" not in t and "step 4 of 14" not in t
        assert r.pause is not None and r.pause.prompt == "Would you like to keep this?"


def test_what_a_reroll_does_and_the_haven_gloss(tmp_path: Path):
    flow, r = _oracle(tmp_path)  # the offline model reads a question as "details"
    r = _to_step(flow, r, 5)
    r = flow.submit('what does "re-roll the land around" actually do?')
    t = _text(r)
    assert "Re-roll the land around: the dice roll the land around again" in t and "one re-roll per step" in t
    assert "Keep it:" not in t  # only the option asked about
    r = _to_step(flow, r, 6)
    assert "your haven" in _text(r) and "rest" in _text(r)
    r = flow.submit("what does haven mean here? Is it like a safe place to rest?")
    assert "Haven: your home base" in _text(r)


def test_lists_are_shown_in_full_or_on_request(tmp_path: Path):
    flow, r = _oracle(tmp_path)
    seen: dict[int, str] = {}
    while r.phase == "seed":
        st = flow.ctx.store.state.open_pause()
        n = st.detail.get("step") if st else None
        seen.update({int(b.text.split(" of 14")[0].rsplit(" ", 1)[-1]): b.text for b in r.oof_blocks
                     if b.text.startswith("Building the world, step")})
        if n == 8:
            r = flow.submit("show all")
            npcs = flow.seed().st["S"]["npcs"]
            assert all(p["name"] in _text(r) for p in npcs)
        r = flow.submit("")
    ws = flow.seed()
    assert " more" not in seen[7] and " more." not in seen[9]  # short lists in full
    assert all(f["name"] in seen[7] for f in ws.st["factions"])
    assert "such as" in seen[10]
    assert "rumor" in seen[11] and "Word is" in seen[11] and "may not be true" in seen[11]
    assert "keepers" in seen[3] and "calls its gods" in seen[3]


def test_mode_question_explains_the_modes(tmp_path: Path):
    store = new_store(tmp_path)
    flow = SeedFlow(TurnContext.for_store(store, model=OfflineModel(), rules=RULES))
    flow.start()
    r = flow.submit('what does "a mix" actually mean?')
    t = _text(r)
    assert "A mix:" in t and "the dice answer" in t and r.pause is not None
    assert len(r.oof_blocks) == 2 and t.count("First, let's build the world") == 1  # the answer, the question once


def _creation(tmp_path: Path, model=None) -> tuple[CreationFlow, Response]:
    flow, r = _oracle(tmp_path, model)
    while r.phase == "seed":
        r = flow.submit("")
    return CreationFlow(flow.ctx), r


def test_creation_question_answers_without_the_welcome_again(tmp_path: Path):
    flow, r = _creation(tmp_path)
    assert WELCOME_START in _text(r)
    r = flow.submit("what's the difference between quick start and the ready-made ones?")
    t = _text(r)
    assert WELCOME_START not in t and t.count("Before we begin") == 1
    assert "Quick start:" in t and "ready-made" in t.lower() and "Here is a little more" not in t
    r = flow.submit("")
    r = flow.submit("what's the difference between Thief and Wanderer?")
    t = _text(r)
    assert "Thief" in t and "Wanderer" in t and "thievery" in t


def test_pronoun_given_with_the_name_is_kept(tmp_path: Path):
    model = ScriptedModel()
    flow, r = _creation(tmp_path, model)
    for msg in ("", "", "", ""):
        r = flow.submit(msg)
    model.push(Role.INTERPRET, {"choice": "own_words", "own_words_text": "Branric Blackfield", "answer": None})
    r = flow.submit("Branric Blackfield, she")
    assert r.pause is not None and r.pause.prompt == "Are you ready to begin?"
    assert "Resolve is strength of mind" in _text(r)


def test_interpret_schema_offers_a_short_answer():
    s = build_schema(Role.INTERPRET, SchemaContext(options=["a"]))
    assert s["properties"]["answer"] == {"type": ["string", "null"]}
