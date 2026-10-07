"""Event store, projection, views, clocks and conditions (T018, store half)."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import ValidationError

from engine.data.loader import load_rules
from engine.rng import Rng
from engine.store import views
from engine.store.clocks import ClockError, create_clock, stage, tick_clock
from engine.store.conditions import active_conditions, apply_condition, remove_condition
from engine.store.db import ENGINE_VERSION, Store
from engine.store.events import Event, PauseRecord, Rejected
from engine.store.projection import NotBuiltYet, apply, project
from engine.store.records import Part, TurnRecord
from tests.fixtures.game import TEST_RULES_HASH, entity, new_store


def fact(tx, subject: str, predicate: str, value, **kw) -> Event:
    return Event.of("fact_set", {"source": kw.pop("source", "narration")}, fact_id=tx.mint("fact"), subject=subject,
                    predicate=predicate, value=value, supersedes=tx.state.current_fact_id(subject, predicate), **kw)


def scene(tx, place: str | None = None) -> Event:
    sid = tx.mint("scn")
    return Event.of("scene_started", scene_id=sid, scene={"scene_id": sid, "place_id": place})


@pytest.fixture
def store(tmp_path: Path) -> Iterator[Store]:
    s = new_store(tmp_path)
    yield s
    s.close()


@pytest.fixture
def cast(store: Store) -> Store:
    """A PC, a place, an NPC with a sealed secret, a sealed NPC, and an open scene."""
    with store.transaction("turn.1") as tx:
        tx.add(entity("place", "Grey Keep", tx=tx))
        tx.add(entity("pc", "Wren", tx=tx, quantities={"vitality": (10, 0, 10), "coin": (5, 0, None)}))
        tx.add(entity("npc", "Tam Harlan", tx=tx, data={"pronouns": "he"}, sealed={"secret": "killed the miller"},
                      slices={"secret": "theme: guilt"}, gate="Tam confides"))
        tx.add(entity("npc", "The Hooded Man", tx=tx, visibility="sealed", slices={"*": "someone watches"}))
        tx.add(scene(tx, "loc.grey_keep"))
    return store


# ------------------------------------------------------------------------------ creation and append-only


def test_game_created_stamps_version_rules_hash_and_milestone(store: Store) -> None:
    first = next(store.events())
    assert first.type == "game_created" and first.seq == 1
    g = store.state.game
    assert g is not None
    assert (g.seed, g.engine_version, g.rules_hash, g.milestone) == (1234, ENGINE_VERSION, TEST_RULES_HASH, 1)


def test_create_refuses_existing_file(store: Store) -> None:
    with pytest.raises(RuntimeError):
        Store.create(store.path, seed=1, rules_hash="x")


def test_events_table_is_append_only(cast: Store) -> None:
    for sql in ("UPDATE events SET type='x' WHERE seq=1", "DELETE FROM events WHERE seq=1",
                "UPDATE rng_draws SET result=1", "DELETE FROM rng_draws"):
        if "rng" in sql:
            cast.record_rng_draw("dice", "test", 3, sides=6)
        with pytest.raises(sqlite3.DatabaseError, match="append-only"):
            cast.conn.execute(sql)


def test_invalid_payload_never_becomes_an_event() -> None:
    with pytest.raises(ValidationError):
        Event.of("quantity_changed", entity="pc.wren")  # missing fields
    with pytest.raises(ValidationError):
        Event.of("no_such_event")
    with pytest.raises(ValidationError):
        Event.of("knowledge_recorded", knower="pc.wren", fact_id="fact.1", how="telepathy")  # closed enum


def test_reference_to_unknown_id_is_rejected_and_nothing_written(cast: Store) -> None:
    before = cast.last_seq
    with pytest.raises(Rejected):
        with cast.transaction() as tx:
            tx.add(fact(tx, "npc.nobody", "mood", "sour"))
    assert cast.last_seq == before and cast.event(before + 1) is None


def test_id_created_earlier_in_same_transaction_may_be_referenced(store: Store) -> None:
    with store.transaction() as tx:
        tx.add(entity("pc", "Wren", tx=tx))
        tx.add(fact(tx, "pc.wren", "has_sister", False))
    assert store.state.fact_value("pc.wren", "has_sister") is False


def test_quantity_out_of_bounds_rejected(cast: Store) -> None:
    with pytest.raises(Rejected):
        cast.append([Event.of("quantity_changed", entity="pc.wren", quantity="vitality", delta=5, new_value=15,
                              reason="x")])


# ------------------------------------------------------------------------------ transactions


def test_transaction_rollback_writes_nothing_and_restores_rng(cast: Store) -> None:
    rng = Rng.for_store(cast)
    state_before, seq_before = cast.state.model_copy(deep=True), cast.last_seq
    with pytest.raises(RuntimeError, match="model down"):
        with cast.transaction("turn.2") as tx:
            rng.d(20, "roll inside the failed turn")
            tx.add(fact(tx, "pc.wren", "mood", "grim"))
            raise RuntimeError("model down")
    assert cast.state == state_before and cast.last_seq == seq_before
    assert cast.rng_draws() == []
    # the stream was restored: the next draw is the one the failed turn made
    fresh = Rng(1234)
    assert rng.d(20, "after rollback") == fresh.d(20, "x")


def test_turn_commits_in_one_transaction(cast: Store) -> None:
    with cast.transaction("turn.2") as tx:
        a = tx.add(fact(tx, "pc.wren", "mood", "grim"))
        b = tx.add(fact(tx, "pc.wren", "mood", "hopeful"))
        assert cast.last_seq < a  # nothing committed yet
    assert [e.turn_id for e in cast.events(since=a - 1)] == ["turn.2", "turn.2"]
    assert b == a + 1 == cast.last_seq


def test_not_built_families_raise(cast: Store) -> None:
    with pytest.raises(NotBuiltYet, match="Milestone 3"):
        cast.append([Event.of("tally_settled", tag="deed.martial")])
    assert all(e.type != "tally_settled" for e in cast.events())


# ------------------------------------------------------------------------------ projection


def _busy_game(store: Store, rules) -> None:
    """Touch every Milestone-1 family, end a scene (snapshot), revert a write."""
    with store.transaction("turn.2") as tx:
        tx.add(fact(tx, "world", "weather", "rain", visibility="shown"))
        tx.add(fact(tx, "world", "weather", "snow", visibility="shown"))
        f = tx.mint("fact")
        tx.add(Event.of("fact_set", {"source": "oracle"}, fact_id=f, subject="npc.tam_harlan", predicate="owes",
                        value="the guild", visibility="sealed", gate="ledger found"))
        tx.add(Event.of("knowledge_recorded", knower="pc.wren", fact_id=f, how="overheard"))
        tx.add(Event.of("relationship_set", a="npc.tam_harlan", b="pc.wren", kind="standing", steps=1, new_value=1,
                        reason="helped"))
        tx.add(Event.of("position_set", entity="pc.wren", location="loc.grey_keep", flags_add=["flag.hidden"]))
        tx.add(Event.of("quantity_changed", entity="pc.wren", quantity="coin", delta=-2, new_value=3, reason="bribe"))
        tx.add(Event.of("meta_set", key="tension", value=6))
        tx.add(create_clock(tx.state, rules.get("clk.twist_word_reaches"), name="Word reaches the guild"))
        tx.add(Event.of("license_granted", entity="pc.wren", license={"license_id": "lic.lang.common"}))
        tx.add(Event.of("pause_opened", pause=PauseRecord(pause_id=tx.mint("pause"), kind="offer",
                                                         choices=[{"id": "commit", "label": "Commit"}])))
        tx.add(Event.of("frame_committed", frame_id=tx.mint("frame"), frame={"beat": {"intent": "sneak"}}))
    with store.transaction("turn.3") as tx:
        tx.add(Event.of("pause_closed", pause_id="pause.1", choice="commit"))
        tx.add(Event.of("frame_resolved", frame_id="frame.1", degree="success", roll={"d20": 14, "total": 17,
                                                                                       "margin": 3}))
        res = tick_clock(tx.state, "clk.word_reaches_the_guild", "cost.exposure", severity="S3",
                         units=rules.severity_units())
        tx.add_all(res.events)
        tx.add_all(apply_condition(tx.state, tx.mint, rules, "pc.wren", "cond.bleeding").events)
        tx.add_all(apply_condition(tx.state, tx.mint, rules, "pc.wren", "cond.bleeding").events)
        hit = tx.add(Event.of("quantity_changed", entity="pc.wren", quantity="vitality", delta=-4, new_value=6,
                              reason="cut"))
    with store.transaction("turn.4") as tx:
        tx.add(Event.of("writes_reverted", reverted=[hit], compensating={"pc.wren.vitality": 10}, reason="error"))
        tx.add(Event.of("scene_ended", scene_id="scn.1", reason="question answered"))
        tx.add(scene(tx))
        tx.add(Event.of("unsealed", ref="npc.tam_harlan#secret", via="Tam confides"))


def test_rebuild_from_events_equals_live_projection(cast: Store) -> None:
    rules = load_rules()
    _busy_game(cast, rules)
    s = cast.state
    assert s.quantities["pc.wren"]["vitality"].current == 10  # reverted
    assert s.quantities["pc.wren"]["coin"].current == 3
    assert s.conditions_on("pc.wren")[0].stacks == 2
    assert s.clocks["clk.word_reaches_the_guild"].filled == 2
    assert s.open_pause() is None and s.frames == {}  # new scene clears this scene's frames
    assert cast.rebuild() == s
    assert project(cast.events()) == s
    reopened = Store.open(cast.path)
    assert reopened.state == s  # from the scene_end snapshot plus later events
    assert cast.conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0] == 1


def test_apply_is_pure(cast: Store) -> None:
    before = cast.state.model_copy(deep=True)
    ev = Event.of("meta_set", key="tension", value=7).model_copy(update={"seq": cast.last_seq + 1})
    after = apply(cast.state, ev)
    assert cast.state == before and after.meta["tension"] == 7


def test_counter_ids_are_deterministic_and_never_reused_after_revert(cast: Store) -> None:
    with cast.transaction() as tx:
        e = tx.add(fact(tx, "pc.wren", "mood", "grim"))
    assert cast.state.facts["fact.1"].value == "grim"
    with cast.transaction() as tx:
        tx.add(Event.of("writes_reverted", reverted=[e], reason="wrong"))
    assert "fact.1" not in cast.state.facts
    with cast.transaction() as tx:
        assert tx.mint("fact") == "fact.2"


def test_revert_outside_current_scene_is_rejected(cast: Store) -> None:
    with pytest.raises(Rejected, match="DL-12-04"):
        cast.append([Event.of("writes_reverted", reverted=[2], reason="too old")])


def test_resume_reopens_the_last_unclosed_pause(cast: Store) -> None:
    with cast.transaction() as tx:
        tx.add(Event.of("pause_opened", pause=PauseRecord(pause_id=tx.mint("pause"), kind="seed_step",
                                                         prompt="Which mode?", default_choice="quick")))
    p = Store.open(cast.path).state.open_pause()
    assert p is not None and p.kind == "seed_step" and p.prompt == "Which mode?"


def test_frame_committed_is_immutable(cast: Store) -> None:
    cast.append([Event.of("frame_committed", frame_id="frame.1", frame={"x": 1})])
    with pytest.raises(Rejected, match="immutable"):
        cast.append([Event.of("frame_committed", frame_id="frame.1", frame={"x": 2})])


# ------------------------------------------------------------------------------ views


def test_narrator_view_has_no_sealed_field(cast: Store) -> None:
    with cast.transaction() as tx:
        f = tx.mint("fact")
        tx.add(Event.of("fact_set", {"source": "generation"}, fact_id=f, subject="npc.tam_harlan",
                        predicate="debt", value="owes the Salt Guild 40 crowns", visibility="sealed", gate="ledger"))
        tx.add(fact(tx, "npc.tam_harlan", "trade", "miller's hand", truth="false"))
    nv = views.narrator_view(cast.state)
    text = json.dumps(nv)
    assert "killed the miller" not in text and "40 crowns" not in text
    assert "The Hooded Man" not in text and '"truth"' not in text
    assert nv["entities"]["npc.tam_harlan"]["data"]["secret"] == {"slice": "theme: guilt"}
    assert nv["entities"]["npc.the_hooded_man"] == {"id": "npc.the_hooded_man", "kind": "npc",
                                                    "slice": "someone watches"}
    assert "killed the miller" in json.dumps(views.audit_view(cast.state))
    cast.append([Event.of("unsealed", ref="npc.tam_harlan#secret", via="Tam confides")])
    assert views.narrator_view(cast.state)["entities"]["npc.tam_harlan"]["data"]["secret"] == "killed the miller"


def test_codex_view_shows_only_shown_and_available(cast: Store) -> None:
    with cast.transaction() as tx:
        tx.add(fact(tx, "pc.wren", "oath", "find the crown", visibility="shown"))
        tx.add(fact(tx, "pc.wren", "hunted_by", "the guild", visibility="background"))
    cv = views.codex_view(cast.state)
    preds = {f["predicate"] for f in cv["facts"].values()}
    assert preds == {"oath"}
    assert "npc.the_hooded_man" not in cv["entities"] and "secret" not in cv["entities"]["npc.tam_harlan"]["data"]
    scoped = views.view(cast.state, "codex", scope=["pc.wren"])
    assert set(scoped["entities"]) == {"pc.wren"}


def test_hidden_clock_fill_never_reaches_the_narrator(cast: Store) -> None:
    rules = load_rules()
    with cast.transaction() as tx:
        tx.add(create_clock(tx.state, rules.get("clk.twist_word_reaches"), name="Word reaches the guild"))
    nv = views.narrator_view(cast.state)
    assert "clk.word_reaches_the_guild" not in nv["clocks"]


def test_facts_are_bitemporal(cast: Store) -> None:
    with cast.transaction() as tx:
        a = tx.add(fact(tx, "world", "weather", "rain"))
    with cast.transaction() as tx:
        b = tx.add(fact(tx, "world", "weather", "snow"))
    assert cast.fact("world", "weather", at_seq=a - 1) is None
    assert (cast.fact("world", "weather", at_seq=a) or {})["value"] == "rain"
    assert (cast.fact("world", "weather", at_seq=b) or {})["value"] == "snow"
    assert (cast.fact("world", "weather") or {})["value"] == "snow"
    assert [r["value"] for r in cast.fact_history("world", "weather")] == ["rain", "snow"]
    assert views.fact(cast.state, "world", "weather") == "snow"
    with pytest.raises(Rejected, match="supersedes"):  # a write must name the value it replaces
        cast.append([Event.of("fact_set", {"source": "narration"}, fact_id="fact.9", subject="world",
                              predicate="weather", value="sun")])


# ------------------------------------------------------------------------------ side tables


class _Rec:
    def __init__(self, **kw) -> None:
        self.kw = kw

    def model_dump(self, mode: str = "python") -> dict:
        return dict(self.kw)


def test_model_calls_keep_retries_and_extra_fields(store: Store) -> None:
    base = dict(call_id="call.turn.1.narrator.0", turn_id="turn.1", role="narrator", attempt=0, provider="offline",
                model_id="m", schema_hash="h", request={"p": 1}, response={"data": None, "text": "x", "error": None},
                tokens_in=10, tokens_out=5, cost_usd=0.0, latency_ms=3, outcome="ok", note="extra field")
    store.record_model_call(_Rec(**base))
    store.record_model_call(_Rec(**{**base, "outcome": "error", "response": {"error": "boom"}}))
    rows = store.model_calls("turn.1")
    assert len(rows) == 1 and rows[0]["outcome"] == "error" and rows[0]["extra"] == {"note": "extra field"}
    assert store.conn.execute("SELECT COUNT(*) FROM model_calls").fetchone()[0] == 2


def test_turn_records_round_trip(store: Store) -> None:
    tid = store.new_turn_id()
    rec = TurnRecord(turn_id=tid, input_verbatim="I knock.", parts=[Part.model_validate({"text": "I knock.", "class": "DECLARATION"})])
    store.save_turn(rec)
    store.save_turn(rec.model_copy(update={"delivered_verbatim": "The door opens."}))
    got = store.turn(tid)
    assert got is not None and got.delivered_verbatim == "The door opens."
    assert Store.open(store.path).new_turn_id() == "turn.2"


# ------------------------------------------------------------------------------ clocks (PR-00-3)


def test_clock_ticks_omens_and_completion(cast: Store) -> None:
    rules = load_rules()
    units = rules.severity_units()
    with cast.transaction() as tx:
        tx.add(create_clock(tx.state, rules.get("clk.twist_word_reaches"), name="Word"))
        tx.add(create_clock(tx.state, {"kind": "progress", "segments": 4, "tick_sources": [{"on": "frame",
                                       "ticks": "delivered_reach"}]}, name="Escape", races_with="clk.word"))
    with pytest.raises(ClockError, match="does not list"):
        tick_clock(cast.state, "clk.word", "cost.harm")
    omens = []
    res = None
    for _ in range(3):
        with cast.transaction() as tx:
            res = tick_clock(tx.state, "clk.word", "cost.exposure", severity="S3", units=units)
            tx.add_all(res.events)
            omens.append((res.stage, res.omen))
    assert [o[0] for o in omens] == ["stirring", "building", "imminent"]
    assert len({o[1] for o in omens}) == 3 and cast.state.clocks["clk.word"].filled == 6
    assert cast.state.clocks["clk.word"].status == "completed"
    assert res is not None and res.completed and res.completion_effects and not res.interrupt
    assert cast.state.clocks["clk.escape"].status == "active"  # Escape races Word only one way here
    with pytest.raises(ClockError):
        tick_clock(cast.state, "clk.word", "cost.twist")


def test_racing_clock_is_voided(cast: Store) -> None:
    with cast.transaction() as tx:
        tx.add(create_clock(tx.state, {"kind": "danger", "segments": 4, "tick_sources": [{"on": "x", "ticks": 4}]},
                            name="A"))
        tx.add(create_clock(tx.state, {"kind": "progress", "segments": 4, "tick_sources": [{"on": "x", "ticks": 1}]},
                            name="B", races_with="clk.a"))
        tx.add_all(tick_clock(tx.state, "clk.b", "x").events)
    with cast.transaction() as tx:
        tx.add_all(tick_clock(tx.state, "clk.b", "x").events)
        tx.add_all(tick_clock(tx.state, "clk.b", "x").events)
        tx.add_all(tick_clock(tx.state, "clk.b", "x").events)
    assert cast.state.clocks["clk.b"].status == "completed" and cast.state.clocks["clk.a"].status == "voided"


def test_clock_stage_boundaries() -> None:
    assert [stage(f, 8) for f in range(9)] == ["stirring"] * 4 + ["building"] * 2 + ["imminent"] * 3
    assert [stage(f, 4) for f in range(5)] == ["stirring", "stirring", "building", "imminent", "imminent"]


# ------------------------------------------------------------------------------ conditions (PR-00-5)


def _apply(store: Store, cid: str, target: str = "pc.wren", **kw):
    rules = load_rules()
    with store.transaction() as tx:
        res = apply_condition(tx.state, tx.mint, rules, target, cid, **kw)
        tx.add_all(res.events)
    return res


def test_condition_stacking_rules(cast: Store) -> None:
    assert _apply(cast, "cond.prone").outcome == "applied"
    assert _apply(cast, "cond.prone").outcome == "ignored"  # unique
    assert [_apply(cast, "cond.exhausted").outcome for _ in range(4)] == ["applied"] + ["intensified"] * 3
    assert next(c for c in cast.state.conditions_on("pc.wren") if c.condition_id == "cond.exhausted").stacks == 3
    assert _apply(cast, "cond.frightened", severity="S2").outcome == "applied"
    assert _apply(cast, "cond.frightened", severity="S1").outcome == "ignored"  # replace_stronger
    assert _apply(cast, "cond.frightened", severity="S3").outcome == "replaced"
    assert [_apply(cast, "cond.cursed", severity="S1").outcome for _ in range(4)] == ["applied", "added", "added",
                                                                                     "ignored"]  # independent, 3
    res = _apply(cast, "cond.off_balance")
    assert res.must_narrate and res.hooks == ["on_condition_applied"]
    assert cast.rebuild() == cast.state


def test_condition_escalates_and_neutralizes(cast: Store) -> None:
    assert _apply(cast, "cond.chilled").outcome == "applied"
    res = _apply(cast, "cond.chilled")
    assert res.outcome == "escalated"
    assert {c.condition_id for c in cast.state.conditions_on("pc.wren")} == {"cond.frozen"}
    res = _apply(cast, "cond.burning")  # burning neutralizes frozen: both gone
    assert res.outcome == "neutralized" and cast.state.conditions_on("pc.wren") == []


def test_condition_diminishing_returns(cast: Store) -> None:
    assert _apply(cast, "cond.restrained").outcome == "applied"
    rules = load_rules()
    rid = cast.state.conditions_on("pc.wren")[0].instance_id
    with cast.transaction() as tx:
        tx.add_all(remove_condition(tx.state, rules, rid, "escaped").events)
    assert _apply(cast, "cond.dazed").outcome == "applied"  # same control group: 2nd application
    assert _apply(cast, "cond.stunned").outcome == "immune"  # immune_after 2


def test_exclusion_group_keeps_highest_priority(cast: Store) -> None:
    _apply(cast, "cond.grabbed")
    _apply(cast, "cond.pinned")
    act = {c.condition_id for c in active_conditions(cast.state, "pc.wren")}
    assert act == {"cond.pinned"} and len(cast.state.conditions_on("pc.wren")) == 2
