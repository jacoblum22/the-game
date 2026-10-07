"""T043: the seeded-error set. Each case's state is built from cases.yaml with tests/fixtures/game.py, and
`check_claims` must return the expected verdict for every extracted claim. A second test feeds the drafts of the
contradiction and unsourced-change cases to the OfflineModel's heuristic Checker and measures recall."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import pytest
import yaml

from engine.audit.claims import check_claims
from engine.data.loader import load_rules
from engine.dm.schemas import SchemaContext, checker_schema
from engine.llm.base import Packet, Role
from engine.llm.offline import OfflineModel, sentences
from engine.store.db import Store
from tests.fixtures.game import new_store
from tests.seeded_errors.world import build, turn

DATA = yaml.safe_load((Path(__file__).parent / "cases.yaml").read_text())
CASES: list[dict[str, Any]] = DATA["cases"]
VERDICTS = ("supported", "new_element", "undetermined", "contradicted", "unsourced_change", "overreach", "leak",
            "pc_agency")


@pytest.fixture(scope="module")
def rules() -> Any:
    return load_rules()


def _merge(base: dict[str, Any], extra: dict[str, Any] | None) -> dict[str, Any]:
    out = {k: list(v) if isinstance(v, list) else v for k, v in base.items()}
    for k, v in (extra or {}).items():
        out[k] = [*out.get(k, []), *v] if isinstance(v, list) else v
    return out


def _setup(tmp_path: Path, case: dict[str, Any]) -> tuple[Store, Any, list[str]]:
    store = new_store(tmp_path, name=f"{case['id']}.db")
    spec = _merge(DATA["fixtures"][case["fixture"]], case.get("extra"))
    build(store, spec)
    record = turn(store, case.get("turn", []), case.get("record"))
    sc = store.state.scene
    scene_ids = [i for i in ["pc.wren", *(sc.cast_present if sc else []), sc.place_id if sc else None] if i]
    return store, record, scene_ids


def test_counts() -> None:
    per = Counter(v for c in CASES for v in c["expect"])
    assert len(CASES) >= 40
    assert set(VERDICTS) <= set(per), per
    assert all(per[v] >= 3 for v in VERDICTS), per


def test_classes_and_verdicts_match_rules_data(rules: Any) -> None:
    from typing import get_args

    from engine.audit.claims import ClaimClass, VerdictName

    cc = rules.pacing["claim_check"]
    assert list(get_args(ClaimClass)) == list(cc["classes"])
    assert list(get_args(VerdictName)) == list(cc["verdicts"])


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_verdict(case: dict[str, Any], tmp_path: Path, rules: Any) -> None:
    store, record, scene_ids = _setup(tmp_path, case)
    got = check_claims(case["claims"], store.state, record, scene_ids, rules=rules)
    assert [v.verdict for v in got] == case["expect"], [v.model_dump() for v in got]
    if "fix" in case:
        assert [v.fix for v in got] == case["fix"]
    if "store_value" in case:
        assert [v.store_value for v in got] == case["store_value"]
    for v in got:  # the fix follows the verdict (12.3.2)
        assert (v.fix is None) == (v.verdict == "supported")
    assert store.rebuild() == store.state


def _offline_claims(store: Store, scene_ids: list[str], draft: str, rules: Any) -> list[dict[str, Any]]:
    s = store.state
    order = sorted(scene_ids, key=lambda e: s.entities[e].kind == "place")  # a place's words last (ties)
    ctx = SchemaContext(scene_ids=order, claim_classes=list(rules.pacing["claim_check"]["classes"]),
                        sentence_ids=[str(i) for i, _ in enumerate(sentences(draft))])
    view = "\n".join(f"{eid}: {s.entities[eid].name}" + (", you, your" if s.entities[eid].kind == "pc" else "")
                     for eid in order)
    packet = Packet(view=view, message=draft)
    return OfflineModel().fill(Role.CHECKER, checker_schema(ctx), packet, turn_id=None, attempt=1).data["claims"]


def test_offline_recall(tmp_path: Path, rules: Any) -> None:
    """The OfflineModel's heuristic extraction + check_claims over the contradiction and unsourced-change drafts.
    Caught = some claim of the draft gets a non-supported verdict. Recall is reported (10/21 when written, with
    1/13 false alarms on the supported drafts): the heuristic extracts nothing from a sentence naming no listed
    entity, defaults unknown classes to `action`, and sets `asserts_change` only for a few verbs, so most misses
    are extraction misses (check_claims gets every hand-extracted case right, test_verdict). This floor guards
    against regressions; the Gemini Checker's recall is measured in evals/."""
    targets = [c for c in CASES if set(c["expect"]) & {"contradicted", "unsourced_change"}]
    caught, exact = [], []
    for case in targets:
        store, record, scene_ids = _setup(tmp_path, case)
        scene_ids = list(dict.fromkeys([*scene_ids, *store.state.entities]))  # the packet lists every entity
        claims = _offline_claims(store, scene_ids, case["draft"], rules)
        verdicts = check_claims(claims, store.state, record, scene_ids, rules=rules)
        bad = {v.verdict for v in verdicts if v.verdict != "supported"}
        if bad:
            caught.append(case["id"])
        if bad & set(case["expect"]):
            exact.append(case["id"])
    clean = [c for c in CASES if set(c["expect"]) == {"supported"}]
    alarms = []
    for case in clean:
        store, record, scene_ids = _setup(tmp_path, case)
        scene_ids = list(dict.fromkeys([*scene_ids, *store.state.entities]))
        verdicts = check_claims(_offline_claims(store, scene_ids, case["draft"], rules), store.state, record,
                                scene_ids, rules=rules)
        if any(v.verdict != "supported" for v in verdicts):
            alarms.append(case["id"])
    print(f"\noffline false alarms: {len(alarms)}/{len(clean)} {alarms}")
    assert len(alarms) / len(clean) < 0.1
    recall = len(caught) / len(targets)
    print(f"\noffline recall: {len(caught)}/{len(targets)} = {recall:.2f}; "
          f"same verdict: {len(exact)}/{len(targets)}; missed: {sorted(set(c['id'] for c in targets) - set(caught))}")
    assert recall >= 0.45
