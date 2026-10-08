"""check_claims beyond the seeded set: Store input, unknown subjects, mention-created subjects, owed blocks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from engine.audit.claims import Claim, check_claims, failing, owed_blocks
from engine.data.loader import load_rules
from engine.dm.adjudication import AdjudicationRecord, WriteRef
from engine.store.events import Event
from tests.fixtures.game import entity, new_store


@pytest.fixture(scope="module")
def rules() -> Any:
    return load_rules()


def _store(tmp_path: Path) -> Any:
    store = new_store(tmp_path)
    with store.transaction("turn.0") as tx:
        tx.add(entity("pc", "Wren", tx=tx, quantities={"coin": (5, 0, None)}))
        tx.add(entity("npc", "Mara Voss", tx=tx, data={"gender": "woman", "pronouns": "she/her"}))
    return store


def test_store_or_state_and_claim_alias(tmp_path: Path, rules: Any) -> None:
    store = _store(tmp_path)
    claim = {"sentence": "0", "subject": "pc.wren", "class": "quantity", "predicate": "coin", "value": "five coins",
             "asserts_change": False, "pc_words_or_feelings": False}
    assert Claim.model_validate(claim).sentence == 0
    for st in (store, store.state):
        [v] = check_claims([claim], st, AdjudicationRecord(), ["pc.wren"], rules=rules)
        assert v.verdict == "supported" and v.fix is None


def test_unknown_subject_is_written_on_mention_not_cut(tmp_path: Path, rules: Any) -> None:
    store = _store(tmp_path)
    before = store.state.model_copy(deep=True)
    claims = [Claim.model_validate({"subject": "unknown", "class": "identity", "predicate": "name", "value": "Bo"}),
              Claim.model_validate({"subject": "npc.nobody", "class": "existence", "predicate": "is", "value": "here"})]
    vs = check_claims(claims, store.state, AdjudicationRecord(), [], rules=rules)
    # [revision: I-127] an unknown subject is written on mention (by the narration pass), never cut for being new
    assert [(v.verdict, v.fix) for v in vs] == [("new_element", "write_on_mention")] * 2
    assert store.state == before  # check_claims itself writes nothing


def test_subject_created_on_mention_this_turn(tmp_path: Path, rules: Any) -> None:
    store = _store(tmp_path)
    with store.transaction("turn.1") as tx:
        seq = tx.add(entity("object", "Rope Ladder", tx=tx))
    rec = AdjudicationRecord(writes=[WriteRef.of(store.event(seq))])  # type: ignore[arg-type]
    claim = {"subject": "unknown", "class": "existence", "predicate": "hangs", "value": "a rope ladder hangs here"}
    [v] = check_claims([claim], store.state, rec, ["pc.wren"], rules=rules)
    assert v.verdict == "supported"


def test_change_needs_a_write_this_turn(tmp_path: Path, rules: Any) -> None:
    store = _store(tmp_path)
    claim = {"subject": "pc.wren", "class": "quantity", "predicate": "coin", "value": "four", "asserts_change": True}
    [v] = check_claims([claim], store.state, AdjudicationRecord(), [], rules=rules)
    assert v.verdict == "unsourced_change"
    with store.transaction("turn.1") as tx:
        seq = tx.add(Event.of("quantity_changed", entity="pc.wren", quantity="coin", delta=-1, new_value=4,
                              reason="paid"))
    rec = AdjudicationRecord()
    rec.add_writes([store.event(seq)])  # type: ignore[list-item]
    [v] = check_claims([claim], store.state, rec, [], rules=rules)
    assert v.verdict == "supported"
    [v] = check_claims([{**claim, "value": "three"}], store.state, rec, [], rules=rules)
    assert v.verdict == "contradicted" and v.store_value == "4"
    assert failing([v]) == [v]


def test_owed_blocks() -> None:
    assert owed_blocks(["trg.lethal_warning", "trg.exits"], "fiction only") == ["[WARNING]", "[STATUS]"]
    assert owed_blocks(["trg.lethal_warning"], "x\n[WARNING] THIS CAN KILL YOU") == []
    assert owed_blocks(["trg.pacing_push"], "") == []


def test_the_anchor_bond_settles_friend_claims(tmp_path: Path, rules: Any) -> None:
    """P-036: a friend anchor bond (02.9.2: standing +2) is never contradicted by "she is not your friend"."""
    store = _store(tmp_path)
    with store.transaction("turn.1") as tx:
        tx.add(Event.of("fact_set", {"source": "player_accepted"}, source="creation", rule_id="02.9.2",
                        fact_id=tx.mint("fact"), subject="pc.wren", predicate="bond.anchor",
                        value={"kind": "friend", "npc": "npc.mara_voss"}, visibility="shown"))
        tx.add(Event.of("relationship_set", source="creation", rule_id="02.9.2", a="npc.mara_voss", b="pc.wren",
                        kind="standing", value=2, new_value=2, reason="bond"))

    def verdict(cls: str, predicate: str, value: str) -> tuple[str, Any]:
        claim = {"subject": "npc.mara_voss", "class": cls, "predicate": predicate, "value": value}
        [v] = check_claims([claim], store.state, AdjudicationRecord(), ["npc.mara_voss"], rules=rules)
        return v.verdict, v.store_value

    assert verdict("identity", "relation to you", "friend") == ("supported", None)
    assert verdict("identity", "relation to you", "stranger") == ("contradicted", "friend")
    assert verdict("identity", "relation to you", "not a friend")[0] == "contradicted"
    assert verdict("attitude", "relation to PC", "not a friend")[0] == "contradicted"
    assert verdict("attitude", "toward you", "warm")[0] == "supported"


def _kit_store(tmp_path: Path, kit: bool) -> Any:
    store = _store(tmp_path)
    with store.transaction("turn.0") as tx:
        tx.add(entity("item", "rapier", tx=tx, data={"item_tag": "item.weapon.blade.rapier"}))
        tx.add(Event.of("fact_set", {"source": "player_accepted"}, source="pc.wren", rule_id="02.8.1",
                        fact_id=tx.mint("fact"), subject="pc.wren", predicate="carries",
                        value=["item.cloak", *(["item.rapier"] if kit else [])], visibility="shown",
                        supersedes=None, gate=None))
    return store


@pytest.mark.parametrize("words", ["my rapier", "my blade", "a weapon"])
def test_the_sheet_kit_counts_as_held(tmp_path: Path, rules: Any, words: str) -> None:
    """Playtest 20261007-193420 (P-090): the sheet's rapier was drawn and the hand "found no blade"."""
    claim = {"subject": "pc.wren", "class": "possession", "predicate": "carries", "value": words}
    [v] = check_claims([claim], _kit_store(tmp_path, True).state, AdjudicationRecord(), ["pc.wren"], rules=rules)
    assert v.verdict == "supported", v
    [v] = check_claims([{**claim, "value": f"no {words.split()[-1]}"}], _kit_store(tmp_path / "x", True).state,
                       AdjudicationRecord(), ["pc.wren"], rules=rules)
    assert v.verdict == "contradicted", v  # "no blade" against the sheet's rapier
    [v] = check_claims([claim], _kit_store(tmp_path / "y", False).state, AdjudicationRecord(), ["pc.wren"],
                       rules=rules)
    assert v.verdict != "supported", v  # without one, nothing on the sheet backs it


def test_the_oracle_never_settles_what_the_sheet_carries(tmp_path: Path, rules: Any) -> None:
    """P-090: the Reader's "carries a rapier?" rolled no against the sheet; with no rapier it is still asked."""
    from engine.resolve.oracle import OracleQuestion, ask_oracle
    from engine.rng import Rng

    for kit, want in ((True, ("read", True)), (False, ("answered", False))):
        store = _kit_store(tmp_path / str(kit), kit)
        for pred in ("carries_a_rapier", "has_a_blade"):
            with store.transaction() as tx:
                res = ask_oracle(OracleQuestion(subject="pc.wren", predicate=pred, odds="impossible"),
                                 state=tx.state, rules=rules, rng=Rng(1), mint=tx.mint, store=store,
                                 staged=tx.events)
                tx.add_all(res.events)
            assert (res.status, res.answer) == want, (kit, pred, res)
