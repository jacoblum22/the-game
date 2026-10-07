"""rules/data loads, validates and is read-only (T007)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from engine.data.loader import (
    KNOWN_DEFECTS,
    RULES_ROOT,
    FrozenDict,
    Rules,
    RulesDataError,
    freeze,
    load_rules,
    rules_hash,
    validate,
)


@pytest.fixture(scope="module")
def rules() -> Rules:
    return load_rules()


def test_every_data_file_loads(rules: Rules) -> None:
    on_disk = {p.name for p in (RULES_ROOT / "data").glob("*.yaml")}
    assert set(rules.files) == on_disk - set(KNOWN_DEFECTS)
    assert set(rules.broken) == set(KNOWN_DEFECTS) & on_disk


@pytest.mark.parametrize("name", sorted(KNOWN_DEFECTS))
def test_known_defects_still_broken(name: str) -> None:
    """When this fails the file was fixed in rules/: remove it from KNOWN_DEFECTS."""
    with pytest.raises(yaml.YAMLError):
        yaml.safe_load((RULES_ROOT / "data" / name).read_text(encoding="utf-8"))


def test_every_cross_reference_resolves(rules: Rules) -> None:
    assert validate(rules) == []


def test_accessors(rules: Rules) -> None:
    assert rules.anchor("anc.01_18_4")["verb"] == "verb.move"
    assert rules.anchors_for_rule("01.18.4")
    assert rules.table("tbl.npc_action")["die"]
    assert rules.table("tbl.twist")["id"] == "tbl.twist"
    hs = rules.boundary_handlers()
    assert len(hs) == len({h["id"] for h in hs}) and all("owner" in h for h in hs)
    assert {t["dc"] for t in rules.resolution["dc_tiers"]}
    assert "harm_states" in rules.harm and "steps" in rules.world_seed and "pool" in rules.gen_birth
    for coll in (rules.oracles, rules.origins, rules.kits, rules.licenses, rules.abilities, rules.conditions,
                 rules.basic_verbs, rules.attributes, rules.archetypes, rules.adversaries, rules.anchors):
        assert len(coll) > 0
    assert "tension" in rules.pacing and "standing_effects" in rules.social and "options" in rules.last_chance
    assert rules.condition("cond.prone")["stacking"] == "unique"
    assert rules.verb("verb.move") and rules.attribute("might")
    assert rules.severity_units() == {"S1": 1, "S2": 1, "S3": 2, "S4": 3, "S5": 4}
    assert rules.where("cond.prone").startswith("conditions.yaml")
    assert "cond.prone" in rules.ids("cond")
    # owner-block entries are part of their collection
    assert any(e for e in rules.licenses if rules.where(e).startswith("licenses.yaml:blocks/"))


def test_unknown_ids_fail_loudly(rules: Rules) -> None:
    with pytest.raises(RulesDataError):
        rules.condition("cond.nonexistent")
    with pytest.raises(RulesDataError):
        rules.get("tbl.nonexistent")
    with pytest.raises(RulesDataError):
        rules.table("cond.prone")
    with pytest.raises(RulesDataError):
        rules.doc("no_such_file")


def test_data_is_read_only(rules: Rules) -> None:
    c = rules.condition("cond.prone")
    with pytest.raises(TypeError):
        c["stacking"] = "refresh"  # type: ignore[index]
    with pytest.raises(TypeError):
        c.update({"x": 1})
    assert isinstance(c["neutralizes"], tuple)
    assert isinstance(c, dict)  # still JSON-shaped


def test_load_is_cached(rules: Rules) -> None:
    assert load_rules() is rules


def test_validation_catches_broken_references(rules: Rules) -> None:
    docs = dict(rules._docs)  # noqa: SLF001
    conds = dict(docs["conditions"])
    entries = list(conds["conditions"])
    entries[0] = freeze({**entries[0], "stacking": "sometimes", "neutralizes": ["cond.nope"]})
    entries.pop(1)  # a reserved id goes missing
    conds["conditions"] = tuple(entries)
    docs["conditions"] = FrozenDict(conds)
    bd = dict(docs["boundaries"])
    blk = dict(bd["blocks"][0])
    blk["handlers"] = (freeze({**blk["handlers"][0], "boundary": "teatime", "phase": 11}), *blk["handlers"][1:])
    bd["blocks"] = (FrozenDict(blk), *bd["blocks"][1:])
    docs["boundaries"] = FrozenDict(bd)
    broken = Rules(rules.root, "test", docs, {})
    problems = "\n".join(validate(broken))
    assert "stacking 'sometimes'" in problems and "neutralizes unknown cond.nope" in problems
    assert "reserved condition" in problems
    assert "unknown boundary teatime" in problems and "phase 11" in problems


def test_rules_hash_tracks_content(tmp_path: Path) -> None:
    root = tmp_path / "rules"
    (root / "data").mkdir(parents=True)
    (root / "00-a.md").write_text("one")
    (root / "data" / "x.yaml").write_text("schema_version: 1\n")
    (root / "data" / "SCHEMAS.md").write_text("s")
    h1 = rules_hash(root)
    assert rules_hash(root) == h1
    (root / "data" / "x.yaml").write_text("schema_version: 2\n")
    assert rules_hash(root) != h1
    assert len(rules_hash()) == 64
