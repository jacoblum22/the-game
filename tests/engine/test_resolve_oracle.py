"""engine/resolve/oracle.py and tables.py: PR-01-4 in a store, the free-question cap (I-038), roll_table recency."""

from __future__ import annotations

from pathlib import Path

from engine.resolve.oracle import FREE_FACTS_KEY, OracleQuestion, ask_oracle, free_count
from engine.resolve.tables import TableError, roll_table
from engine.rng import Rng
from tests.engine.test_resolve_scene import FixedRng, Scene


def _ask(s: Scene, q: OracleQuestion, faces: list[int] | None = None, cap: int | None = None,
         rng: Rng | None = None):  # type: ignore[no-untyped-def]
    with s.store.transaction() as tx:
        res = ask_oracle(q, state=tx.state, rules=s.rules, rng=rng or FixedRng(faces or []), mint=tx.mint,
                         store=s.store, staged=tx.events, free_cap=cap)
        tx.add_all(res.events)
    return res


def test_answer_is_a_fact_then_a_log_entry(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    res = _ask(s, OracleQuestion(subject="world", predicate="inn.back_door", odds="likely", asker=s.pc), [34])
    assert (res.status, res.shape, res.answer, res.d100) == ("answered", "yes", True, 34)
    f = s.state.facts[res.fact_id]  # type: ignore[index]
    assert (f.source, f.value, f.visibility) == ("oracle", True, "shown")
    seqs = s.state.ledger["oracle"]
    ev = s.store.event(seqs[-1])
    assert ev is not None and ev.source == s.pc and ev.payload.fact_id == res.fact_id  # type: ignore[attr-defined]
    assert s.state.meta[FREE_FACTS_KEY] == [res.fact_id] and free_count(s.state) == 1
    assert s.store.rebuild() == s.state


def test_never_reask_reads_the_fact(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    first = _ask(s, OracleQuestion(subject="world", predicate="ford", odds="even", asker="dm"), [10])
    again = _ask(s, OracleQuestion(subject="world", predicate="ford", odds="likely", asker="dm"), [])
    assert (again.status, again.fact_id, again.answer) == ("read", first.fact_id, False)
    assert free_count(s.state) == 0  # the DM's own questions are not free facts


def test_reading_a_list_valued_fact_returns_it(tmp_path: Path) -> None:
    """Playtest 20261007-155118: the PC's `carries` fact is a list; reading it crashed OracleResult(answer: bool)."""
    from engine.store.events import Event

    s = Scene.new(tmp_path)
    kit = ["item.plain_clothes", "item.cloak", "item.skinning_knife", "item.spear"]
    with s.store.transaction() as tx:
        tx.add_all([Event.of("fact_set", {"source": "player_accepted"}, source=s.pc, rule_id="test",
                             fact_id=tx.mint("fact"), subject=s.pc, predicate="carries", value=kit,
                             visibility="shown", supersedes=None, gate=None)])
    res = _ask(s, OracleQuestion(subject=s.pc, predicate="carries", odds="even"), [])
    assert (res.status, res.answer) == ("read", kit)


def test_but_qualifier_and_extreme_and(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    but = _ask(s, OracleQuestion(subject="world", predicate="rope", odds="even", qualifier="elsewhere"), [52])
    assert (but.shape, but.twist, but.qualifier) == ("yes_but", True, "elsewhere")
    assert s.state.fact_value("world", "rope.but") == "elsewhere"
    nob = _ask(s, OracleQuestion(subject="world", predicate="lamp", odds="even", qualifier="bogus"), [47])
    assert (nob.shape, nob.qualifier) == ("no_but", "trace")  # unknown qualifier -> the data default
    ext = _ask(s, OracleQuestion(subject="world", predicate="dog", odds="even"), [66, 1, 2])
    assert ext.shape == "yes_and" and len(ext.meaning) == 2
    assert [e.payload.table_id for e in s.store.events(types=["table_rolled"])] == [  # type: ignore[attr-defined]
        "tbl.meaning", "tbl.meaning_verb", "tbl.meaning_subject"]


def test_certain_and_impossible_do_not_roll(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    yes = _ask(s, OracleQuestion(subject="world", predicate="stable.straw", odds="certain"), [])
    no = _ask(s, OracleQuestion(subject="world", predicate="stable.dragon", odds="impossible"), [])
    assert (yes.answer, yes.d100, no.answer) == (True, None, False)


def test_free_question_cap_refuses_and_logs(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    for i in range(2):
        _ask(s, OracleQuestion(subject="world", predicate=f"q{i}", odds="even", asker=s.pc), [40], cap=2)
    refused = _ask(s, OracleQuestion(subject="world", predicate="q2", odds="even", asker=s.pc), [40], cap=2)
    assert refused.status == "refused" and "cap" in refused.reason
    scene = s.state.scene.scene_id  # type: ignore[union-attr]
    assert s.state.meta[f"oracle.free_cap_hit.{scene}"]["cap"] == 2
    dm = _ask(s, OracleQuestion(subject="world", predicate="q3", odds="even"), [40], cap=2)
    assert dm.status == "answered"  # the cap is on the player's free questions only


def test_seeded_oracle_uses_the_oracle_stream(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    rng = Rng.for_store(s.store)
    res = _ask(s, OracleQuestion(subject="world", predicate="x", odds="even"), rng=rng)
    draws = s.store.rng_draws()
    assert draws[-1]["stream"] == "oracle" and draws[-1]["result"] == res.d100


def test_roll_table_recency_redraws_once(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    a = roll_table("tbl.meaning_verb", {}, rules=s.rules, state=s.state, rng=FixedRng([1]))
    s.apply(a.events)
    b = roll_table("tbl.meaning_verb", {}, rules=s.rules, state=s.state, rng=FixedRng([1, 2]))
    assert b.redrawn and b.roll == 2 and b.entry != a.entry
    s.apply(b.events)
    c = roll_table("tbl.meaning_verb", {}, rules=s.rules, state=s.state, rng=FixedRng([1, 2]))
    assert c.redrawn and c.entry == b.entry  # the second draw stands
    assert s.state.table_recency["tbl.meaning_verb"] == [a.entry, b.entry]


def test_roll_table_clamps_the_modified_total_to_a_row(tmp_path: Path) -> None:
    """12.11.5: d10 + standing (-3..+3), clamped 1-10 (`modifier.clamp`), always lands on a row."""
    s = Scene.new(tmp_path)

    def roll(face: int, standing: int) -> int | None:
        return roll_table("tbl.npc_action", {"standing_modifier": standing}, rules=s.rules, state=s.state,
                          rng=FixedRng([face])).roll

    assert roll(1, -3) == 1 and roll(2, -1) == 1 and roll(10, 3) == 10 and roll(9, 3) == 10 and roll(5, 2) == 7
    assert roll(4, -3) == 1 and roll(8, 0) == 8


def test_roll_table_dispatchers(tmp_path: Path) -> None:
    s = Scene.new(tmp_path)
    desc = roll_table("tbl.meaning", {"meaning_kind": "description"}, rules=s.rules, state=s.state,
                      rng=FixedRng([3, 4]))
    assert desc.roll is None and [x.table_id for x in desc.sub] == ["tbl.meaning_descriptor", "tbl.meaning_focus"]
    tw = roll_table("tbl.twist", {"severity": "S2"}, rules=s.rules, state=s.state, rng=FixedRng([5]))
    assert tw.sub[0].table_id == "tbl.twist_s2" and len(tw.events) == 2
    try:
        roll_table("tbl.twist", {"severity": "S5", "pc_frame": True}, rules=s.rules, state=s.state, rng=FixedRng([]))
        raise AssertionError("S5 twist on a PC frame must be refused")
    except TableError:
        pass
    react = roll_table("tbl.npc_reaction", {}, rules=s.rules, state=s.state, rng=FixedRng([3, 4]))
    assert react.roll == 7  # 2d6
