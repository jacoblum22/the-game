"""The claim check converges (12.3.3): the evidence of playtest 20261007-155118, where 5 of 7 turns fell back.

- each redraft was re-extracted from scratch and the Checker found new failures in sentences that had passed;
- an Oracle answer that agreed with the draft still forced a redraft;
- "an hour goes by" was undetermined on a turn where time passed; place and outcome contradictions had no reason;
- after the budget, failures whose fix was a cut still fell back to the plain fallback.
Real inventions (a clue, a hidden door with treasure, a person who knows of the cult) are still cut.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.audit.claims import Claim, check_claims
from engine.data.loader import load_rules
from engine.dm import narration
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, WriteRef
from engine.dm.turn import play_turn
from engine.llm.base import Role
from tests.engine.test_turn_adjudication import setup
from tests.engine.test_turn_narration import calls, chk, claim, look_model, narr

PROMPT = "What do you do?"


def test_unchanged_passed_sentences_keep_their_pass(tmp_path: Path) -> None:
    """The turn-3 pattern: the redraft fixes one sentence; re-extraction finds fresh 'failures' in sentences that
    passed before. They are carried; the invented hidden door is cut by code. One redraft, no fallback."""
    draft = f"Tam Harlan, a woman, watches the water. He mends a net by the post. Stallholders call their prices. {PROMPT}"
    redraft = (f"Tam Harlan, a man, watches the water. He mends a net by the post. Stallholders call their prices. "
               f"Behind the shed a hidden door hides a chest of treasure. {PROMPT}")
    model = look_model(narrator=[narr(draft), narr(redraft)])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER,
               chk(claim(0, dock.ferryman, "identity", "gender", "woman"),
                   claim(1, dock.ferryman, "action", "mends", "a net")),
               chk(claim(0, dock.ferryman, "identity", "gender", "man"),
                   claim(1, dock.ferryman, "identity", "gender", "woman"),  # a fresh misreading of a passed sentence
                   claim(2, "unknown", "action", "call", "their prices", change=True),
                   claim(3, "unknown", "existence", "hidden door", "a hidden door hiding a chest of treasure")))
    out = play_turn(ctx, "I look over the quay.")
    assert not out.response.flags.fallback_used
    assert out.response.fiction == ("Tam Harlan, a man, watches the water. He mends a net by the post. "
                                    f"Stallholders call their prices. {PROMPT}")
    assert len(calls(model, Role.NARRATOR)) == 2  # one redraft
    assert [v["kind"] for v in out.turn_record.draft_versions] == ["draft", "redraft", "cut"]
    v2 = out.turn_record.draft_versions[1]["verdicts"]
    assert [v["verdict"] for v in v2[:3]] == ["supported"] * 3 and "12.3.3" in v2[1]["reason"]
    assert (v2[3]["verdict"], v2[3]["fix"]) == ("new_element", "cut")


def test_oracle_yes_needs_no_redraft(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    text = f"Tam Harlan's coat is patched at the elbows. {PROMPT}"
    model = look_model(narrator=[narr(text)])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk(claim(0, dock.ferryman, "identity", "appearance", "coat patched at the elbows")))
    monkeypatch.setattr(narration, "_ask_oracle", lambda *a: "yes")
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == text and not out.response.flags.fallback_used
    assert len(calls(model, Role.NARRATOR)) == 1 and len(calls(model, Role.CHECKER)) == 1


def test_oracle_no_is_redrafted_and_its_answer_is_readable(tmp_path: Path) -> None:
    """The Oracle's yes/no is stored under the asked value, so a later claim of that value is checked, with a
    reason (it was `contradicted` against a bare False before)."""
    model = look_model(narrator=[narr(f"The shed's shutters are closed. {PROMPT}")])
    dock, ctx = setup(tmp_path, model)
    from engine.store.events import Event

    with dock.store.transaction() as tx:
        tx.add(Event.of("fact_set", {"source": "oracle"}, source="dm", rule_id="01.15.5", fact_id="fact.t1",
                        subject=dock.ferryman, predicate="shutters_closed", value=False, visibility="shown"))
    c = Claim.model_validate({"subject": dock.ferryman, "class": "identity", "predicate": "shutters", "value": "closed"})
    v = check_claims([c], dock.store.state, AdjudicationRecord(), [], rules=dock.rules)[0]
    assert (v.verdict, v.store_value) == ("contradicted", "not closed") and v.reason


def test_cut_only_failures_after_the_budget_deliver_the_cut(tmp_path: Path) -> None:
    bad = f"Tam Harlan, a woman, watches you. The fog lies low on the water. {PROMPT}"
    last = f"Tam Harlan watches you. The fog lies low on the water. Someone spits into the dust. {PROMPT}"
    model = look_model(narrator=[narr(bad), narr(bad), narr(last)])
    dock, ctx = setup(tmp_path, model)
    woman = claim(0, dock.ferryman, "identity", "gender", "woman")
    model.push(Role.CHECKER, chk(woman), chk(woman), chk(claim(2, "unknown", "action", "spits", "into the dust")))
    out = play_turn(ctx, "I look over the quay.")
    assert not out.response.flags.fallback_used
    assert out.response.fiction == f"Tam Harlan watches you. The fog lies low on the water. {PROMPT}"
    assert [v["kind"] for v in out.turn_record.draft_versions] == ["draft", "redraft", "redraft", "cut"]


def test_after_the_budget_a_cut_leaving_only_the_prompt_falls_back(tmp_path: Path) -> None:
    bad = f"Tam Harlan, a woman, watches you. {PROMPT}"
    model = look_model(narrator=[narr(bad)] * 3)
    dock, ctx = setup(tmp_path, model)
    woman = claim(0, dock.ferryman, "identity", "gender", "woman")
    model.push(Role.CHECKER, chk(woman), chk(woman), chk(claim(0, "unknown", "action", "spits", "into the dust")))
    assert play_turn(ctx, "I look over the quay.").response.flags.fallback_used


@pytest.mark.parametrize("claim_args", [
    ("existence", "clue", "a scrap of paper that points to the smugglers' cache"),
    ("existence", "hidden door", "a hidden door behind the shelves with treasure behind it"),
    ("knowledge", "knows", "the old man knows about the cult"),
])
def test_inventions_in_a_redraft_are_still_cut(tmp_path: Path, claim_args: tuple[str, str, str]) -> None:
    cls, predicate, value = claim_args
    bad = f"Tam Harlan, a woman, watches you. {PROMPT}"
    redraft = f"Tam Harlan, a man, watches you. Something is waiting here. {PROMPT}"
    model = look_model(narrator=[narr(bad), narr(redraft)])
    dock, ctx = setup(tmp_path, model)
    model.push(Role.CHECKER, chk(claim(0, dock.ferryman, "identity", "gender", "woman")),
               chk(claim(0, dock.ferryman, "identity", "gender", "man"), claim(1, "unknown", cls, predicate, value)))
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == f"Tam Harlan, a man, watches you. {PROMPT}"
    assert value not in {e.name for e in ctx.store.state.entities.values()}


def _time_record(boundaries: str) -> AdjudicationRecord:
    rec = AdjudicationRecord()
    rec.writes.append(WriteRef(seq=1, type="time_advanced", key=boundaries))
    return rec


def test_elapsed_time_is_supported_when_time_passed() -> None:
    from engine.store.projection import WorldState

    c = [{"subject": "unknown", "class": "location_time", "predicate": "time elapsed", "value": "an hour goes by",
          "asserts_change": True}]
    rules = load_rules()
    assert check_claims(c, WorldState(), _time_record("interval"), [], rules=rules)[0].verdict == "supported"
    v = check_claims(c, WorldState(), _time_record("beat_end"), [], rules=rules)[0]
    assert (v.verdict, v.reason) == ("unsourced_change", "no time passed this turn")


def test_a_place_described_is_not_a_whereabouts() -> None:
    """Turn 1: "the bell of Alda's temple tolls" (about the market) and "Larkhollow" (the market's town) were
    contradicted with "the market square" and no reason."""
    from engine.store.events import EntityRecord, SceneRecord
    from engine.store.projection import WorldState

    ents = [EntityRecord(id="loc.town", kind="place", name="Larkhollow"),
            EntityRecord(id="loc.market", kind="place", name="market square", data={"parent": "loc.town"}),
            EntityRecord(id="loc.temple", kind="place", name="temple of Alda", data={"parent": "loc.town"}),
            EntityRecord(id="pc.x", kind="pc", name="Branric")]
    st = WorldState(entities={e.id: e for e in ents}, scene=SceneRecord(scene_id="scene.1", place_id="loc.market"))
    lt = lambda s, v: {"subject": s, "class": "location_time", "predicate": "where", "value": v}  # noqa: E731
    vs = check_claims([lt("loc.market", "the bell of the temple of Alda"), lt("loc.market", "Larkhollow"),
                       lt("pc.x", "in Larkhollow"), lt("pc.x", "inside the temple of Alda")],
                      st, AdjudicationRecord(pc="pc.x"), [], rules=load_rules())
    assert [v.verdict for v in vs] == ["supported", "supported", "supported", "contradicted"]
    assert vs[3].reason == "the store places them at market square"


def test_failed_outcome_words_and_reasons() -> None:
    from engine.store.projection import WorldState

    rec = AdjudicationRecord()
    rec.beats.append(BeatEntry.model_validate({"restatement": "follow the tracks", "degree": "critical_failure"}))
    cs: list[dict[str, Any]] = [
        {"subject": "unknown", "class": "outcome", "predicate": "trail", "value": "goes cold"},
        {"subject": "unknown", "class": "outcome", "predicate": "tracks", "value": "each line breaks off"},
        {"subject": "unknown", "class": "outcome", "predicate": "tracks", "value": "you follow them to the gate"}]
    vs = check_claims(cs, WorldState(), rec, [], rules=load_rules())
    assert [v.verdict for v in vs] == ["supported", "supported", "contradicted"]
    assert vs[2].reason == "the attempt's result was critical failure"
