"""The claim check converges (12.3.3; spec 006): the evidence of playtest 20261007-155118, where 5 of 7 turns fell
back, and the per-sentence repair that replaces whole-draft redrafts.

- a repair re-sends only the failing sentence; the sentences that passed are neither re-sent nor re-checked;
- an Oracle answer that agrees with the draft forces no repair;
- "an hour goes by" was undetermined on a turn where time passed; place and outcome contradictions had no reason;
- after two repair rounds a still-failing sentence is cut and the passing ones are delivered.
Declared inventions (a clue, a hidden door with treasure, a person who knows of the cult) are still cut (T2).
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
from tests.engine.test_turn_narration import _decl, _must, calls, look_model, narr, rep

PROMPT = "What do you do?"


def test_a_repair_resends_only_the_failing_sentence(tmp_path: Path) -> None:
    """The turn-3 pattern: one sentence is wrong. Only it is sent back and re-checked; the others stand as written.
    Spec 011: the failure is a code-scan hit (an unknown name); a coat's colour or a gender is no longer judged."""
    draft = f"Tam Harlan nods to Brannoc. He mends a net by the post. Stallholders call their prices. {PROMPT}"
    model = look_model(narrator=[narr(draft), rep(0, "Tam Harlan nods to you.")])
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert not out.response.flags.fallback_used
    assert out.response.fiction == ("Tam Harlan nods to you. He mends a net by the post. "
                                    f"Stallholders call their prices. {PROMPT}")
    assert len(calls(model, Role.NARRATOR)) == 2  # one narrow repair
    repair = calls(model, Role.NARRATOR)[1].message.split("A REPAIR", 1)[1]
    assert "Brannoc" in repair and "mends a net" not in repair
    assert [v["kind"] for v in out.turn_record.draft_versions] == ["draft", "repair"]


def test_oracle_yes_needs_no_redraft(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A declared T1b element (knowledge) is settled by the Oracle; a yes is the draft's own value."""
    text = "The tide turns at dusk here."

    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        new = [{"element_kind": "knowledge", "name": "the tide turns at dusk", "ordinary": True, "implied": []}]
        return {"sentences": [_decl(text, _must(packet), new=new), _decl(PROMPT)]}
    model = look_model(narrator=[draft])
    dock, ctx = setup(tmp_path, model)
    monkeypatch.setattr(narration, "_ask_oracle", lambda *a, **k: "yes")
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == f"{text} {PROMPT}" and not out.response.flags.fallback_used
    assert len(calls(model, Role.NARRATOR)) == 1


def test_an_incidental_property_is_written_as_narrated(tmp_path: Path) -> None:
    """12.3.2 / DL-12-40 (B P5): a coat's look is T1a: written as drafted, no Oracle, no repair; it binds later."""
    text = "Tam Harlan's coat is patched at the elbows."

    def draft(schema: Any, packet: Any) -> dict[str, Any]:
        new = [{"element_kind": "person", "name": "Tam Harlan", "ordinary": True,
                "implied": [{"predicate": "clothing", "value": "coat patched at the elbows"}]}]
        return {"sentences": [_decl(text, _must(packet), new=new), _decl(PROMPT)]}
    model = look_model(narrator=[draft])
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == f"{text} {PROMPT}"
    ref = dock.state.details[dock.ferryman]["clothing"]  # a look goes in its detail slot (00.6.6a; spec 009 B)
    assert dock.state.facts[ref.fact_id].value == "coat patched at the elbows"
    assert not any(e.type == "oracle_answered" for e in dock.store.events(types=["oracle_answered"]))


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


def test_still_failing_after_two_repairs_is_cut_and_the_rest_delivered(tmp_path: Path) -> None:
    bad = "Tam Harlan nods to Brannoc."
    model = look_model(narrator=[narr(f"{bad} The fog lies low on the water. {PROMPT}"), rep(0, bad), rep(0, bad)])
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert not out.response.flags.fallback_used
    assert out.response.fiction == f"The fog lies low on the water. {PROMPT}"
    assert [v["kind"] for v in out.turn_record.draft_versions] == ["draft", "repair", "repair", "cut"]


def test_after_the_repairs_a_cut_leaving_only_the_prompt_falls_back(tmp_path: Path) -> None:
    bad = "Tam Harlan nods to Brannoc."
    model = look_model(narrator=[narr(f"{bad} {PROMPT}"), rep(0, bad), rep(0, bad)])
    dock, ctx = setup(tmp_path, model)
    assert play_turn(ctx, "I look over the quay.").response.flags.fallback_used


@pytest.mark.parametrize("new", [
    {"element_kind": "clue", "name": "a scrap of paper that points to the smugglers' cache", "ordinary": True},
    {"element_kind": "item", "name": "a hidden door with treasure behind it", "ordinary": False},
    {"element_kind": "person", "name": "an old man who knows about the cult", "ordinary": False},
])
def test_declared_inventions_in_a_repair_are_still_cut(tmp_path: Path, new: dict[str, Any]) -> None:
    """12.14.13: a T2 element no record line delivers is cut, also when a repair adds it."""
    bad = f"Tam Harlan nods to Brannoc. {PROMPT}"

    def repair(schema: Any, packet: Any) -> dict[str, Any]:
        return {"repairs": [{"replaces": "0", "text": "Tam Harlan nods to you.", "refs": _must(packet),
                             "about": [], "new": [], "atmosphere": False, "speaker": "none"},
                            {"replaces": "add", "text": "Something is waiting here.", "refs": [], "about": [],
                             "new": [{**new, "implied": []}], "atmosphere": False, "speaker": "none"}]}
    model = look_model(narrator=[narr(bad), repair])
    dock, ctx = setup(tmp_path, model)
    out = play_turn(ctx, "I look over the quay.")
    assert out.response.fiction == f"Tam Harlan nods to you. {PROMPT}"
    assert new["name"] not in {e.name for e in ctx.store.state.entities.values()}


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
