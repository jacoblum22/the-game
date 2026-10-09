"""T038: the PR-01-1 driver on the dock fixture, with a stub Framer (no model)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.resolve.gate import GateDecision
from engine.resolve.pipeline import BeatPlan, PipelineEnv, challenge_band, close_by_default, resume, run_beats
from engine.resolve.types import Beat, CostDecl, Obstacle, ProposedFrame
from tests.engine.test_turn_adjudication import D20
from tests.fixtures.scene_dock import DockScene, build_dock


def stub_framer(attribute: str = "agility", trivial: tuple[str, ...] = (), **over: Any) -> Any:
    """A fixed proposal; for a verb in `trivial`, that verb's trivial rubric class (no roll, 01.4.1)."""
    def propose(beat: Beat, candidates: list[str], *, gate: GateDecision, note: str | None = None) -> ProposedFrame:
        if beat.verb in trivial:
            cls = {"verb.observe": "in_plain_view", "verb.move": "open_ground", "verb.handle": "ordinary_use"}
            return ProposedFrame(anchor=candidates[0], attribute=attribute,
                                 obstacle=Obstacle(kind="tier", obstacle_class=cls[beat.verb or ""], id="obs.test"),
                                 threatened_cost=CostDecl(menu_id="cost.time"))
        base: dict[str, Any] = {
            "anchor": candidates[0], "attribute": attribute,
            "obstacle": Obstacle(kind="tier", tier="moderate", id="obs.test"),
            "stakes_source": "listening_clock",
            "threatened_cost": CostDecl(menu_id="cost.exposure"), "alternate_cost": CostDecl(menu_id="cost.time")}
        return ProposedFrame(**{**base, **over})

    return propose


def plan(dock: DockScene, intent: str, verb: str, *, n: int = 1, **kw: Any) -> BeatPlan:
    beat = Beat(id=f"beat.{n}", actor=dock.pc, intent=intent, method=intent, verb=verb,
                declared_seq=dock.state.last_seq, **kw)
    return BeatPlan(beat=beat, intent_verbs=[intent.split()[0]])


def env_for(dock: DockScene, tx: Any, rng: Any = None, **kw: Any) -> PipelineEnv:
    return PipelineEnv(tx=tx, rules=dock.rules, rng=rng or dock.rng, store=dock.store,
                       framer=kw.pop("framer", stub_framer()), pc=dock.pc, **kw)


def setup(tmp_path: Path) -> tuple[DockScene, D20]:
    dock = build_dock(tmp_path)
    rng = D20.of(dock.store)
    return dock, rng


def test_at_most_three_beats_the_rest_queued(tmp_path: Path) -> None:
    dock, rng = setup(tmp_path)
    plans = [plan(dock, f"look around {i}", "verb.observe", n=i) for i in range(4)]
    with dock.store.transaction("turn.1") as tx:
        res = run_beats(env_for(dock, tx, rng, framer=stub_framer(trivial=("verb.observe",))), plans)
    assert [o.status for o in res.outcomes] == ["no_roll"] * 3 and dock.state.time.now.beat == 3  # three beat_ends
    # 01.2.3: the fourth is confirmed, not run and not dropped (spec 017: the plan waits in the pause)
    assert res.pause is not None and res.pause.detail["stage"] == "plan"
    assert res.pause.prompt == "That is three actions this turn. Still go on: look around 3?"
    assert [q["beat"]["intent"] for q in res.pause.detail["queued"]] == ["look around 3"]


def test_resume_continues_the_beat_then_the_queue(tmp_path: Path) -> None:
    dock, rng = setup(tmp_path)
    plans = [plan(dock, "sneak to the ferry", "verb.sneak", n=1),
             plan(dock, "look at the ferry", "verb.observe", n=2)]
    fr = stub_framer(trivial=("verb.observe",))
    with dock.store.transaction("turn.1") as tx:
        res = run_beats(env_for(dock, tx, rng, framer=fr), plans)
    assert res.pause is not None and [o.status for o in res.outcomes] == ["paused"]
    assert len(res.pause.detail["queued"]) == 1
    rng.faces = [20]
    with dock.store.transaction("turn.2") as tx:
        res2 = resume(env_for(dock, tx, rng, framer=fr), dock.state.open_pause(), "commit")  # type: ignore[arg-type]
    assert [o.status for o in res2.outcomes] == ["resolved", "no_roll"]
    assert res2.outcomes[0].entry.degree == "critical_success" and dock.state.open_pause() is None
    assert dock.store.rebuild() == dock.state


def test_new_declaration_withdraws_an_open_offer(tmp_path: Path) -> None:
    dock, rng = setup(tmp_path)
    with dock.store.transaction("turn.1") as tx:
        run_beats(env_for(dock, tx, rng), [plan(dock, "sneak to the ferry", "verb.sneak")])
    before = dock.state.model_copy(deep=True)
    with dock.store.transaction("turn.2") as tx:
        close_by_default(env_for(dock, tx, rng), dock.state.open_pause())  # type: ignore[arg-type]
        added = [e.type for e in tx.events]
    assert added == ["pause_closed", "offer_logged"] and dock.state.open_pause() is None
    assert dock.state.time.now == before.time.now and not dock.state.frames


def test_open_near_miss_defaults_to_failure(tmp_path: Path) -> None:
    dock, rng = setup(tmp_path)
    with dock.store.transaction("turn.1") as tx:
        res = run_beats(env_for(dock, tx, rng), [plan(dock, "sneak to the ferry", "verb.sneak")])
    assert res.pause is not None
    rng.faces = [int(res.pause.detail["offer"]["need"]) - 2]
    with dock.store.transaction("turn.2") as tx:
        res2 = resume(env_for(dock, tx, rng), dock.state.open_pause(), "commit")  # type: ignore[arg-type]
    assert res2.pause is not None and res2.pause.kind == "near_miss"
    with dock.store.transaction("turn.3") as tx:
        res3 = close_by_default(env_for(dock, tx, rng), dock.state.open_pause())  # type: ignore[arg-type]
    out = res3.outcomes[0]
    assert out.status == "resolved" and out.entry.degree == "failure" and not out.entry.success_at_cost
    assert out.entry.costs and out.entry.costs[0].menu_id == "cost.exposure"  # risky failure: the threatened cost


def test_redirect_offers_the_crude_fallback(tmp_path: Path) -> None:
    dock, rng = setup(tmp_path)
    axe = plan(dock, "hew the mooring rope with the axe like a trained axeman", "verb.strike", uses_power=True)
    with dock.store.transaction("turn.1") as tx:
        res = run_beats(env_for(dock, tx, rng, framer=stub_framer("might")), [axe])
    assert res.pause is not None and res.pause.kind == "redirect"
    ids_ = [c["id"] for c in res.pause.choices]
    assert ids_ == ["accept:lic.training.martial_axe", "other"] and not dock.state.frames
    with dock.store.transaction("turn.2") as tx:
        res2 = resume(env_for(dock, tx, rng, framer=stub_framer("might")), dock.state.open_pause(),  # type: ignore[arg-type]
                      "accept:lic.training.martial_axe")
    assert res2.pause is not None and res2.pause.kind == "offer"
    assert res2.pause.detail["frame"]["gate"]["mode"] == "fallback"


def test_accepted_fallback_rolls_even_from_a_no_roll_class(tmp_path: Path) -> None:
    """P-087: "Try it anyway" on a take-the-time beat was an unrolled success the narration then refused."""
    dock, rng = setup(tmp_path)
    axe = plan(dock, "hew the mooring rope with the axe like a trained axeman", "verb.strike", uses_power=True)
    with dock.store.transaction("turn.1") as tx:
        run_beats(env_for(dock, tx, rng, framer=stub_framer("might")), [axe])
    with dock.store.transaction("turn.2") as tx:
        res2 = resume(env_for(dock, tx, rng, framer=stub_framer("might")), dock.state.open_pause(),  # type: ignore[arg-type]
                      "accept:lic.training.martial_axe")
    assert res2.pause is not None and res2.pause.kind == "offer"
    assert res2.pause.detail["frame"]["gate"]["mode"] == "fallback"


def test_challenge_band() -> None:
    assert [challenge_band(x) for x in (None, 10, 15, 20, 25, 30)] == [1, 1, 2, 3, 4, 5]
