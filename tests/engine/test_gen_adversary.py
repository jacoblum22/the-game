"""PR-09-2 improvised adversaries (T058): the PR-09-1 port against the reference build, the bestiary, validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from engine.gen import _data
from engine.gen.adversary import build, improvise
from engine.gen.build_tables import gen09, source_hashes

DATA = Path(__file__).resolve().parents[2] / "engine" / "gen" / "data"


@pytest.fixture(scope="module")
def ref() -> dict[str, Any]:
    return gen09()


def test_tables_are_fresh() -> None:
    stored = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
    assert stored == source_hashes(), "rerun: python -m engine.gen.build_tables"


def test_build_matches_reference_for_every_combination(ref: dict[str, Any]) -> None:
    """Every archetype x band x own role x variant: the record equals 09-gen_data09.py#build's, field for field."""
    arch, rbuild, V = ref["ARCH"], ref["build"], ref["RO"].V
    n, bad = 0, []
    for a in sorted(arch):
        lo, hi = arch[a]["bands"]
        for b in range(lo, hi + 1):
            drop = [p for p in arch[a]["powers"] if (ref["POWERS"][p].get("min_band") or 0) > b]
            for role in arch[a]["roles"]:
                for var in ("minion", "standard", "elite", "solo"):
                    want = rbuild(V("x", "x", a, b, role, var, drop_powers=drop))
                    got = build(a, b, role, var)  # type: ignore[arg-type]
                    n += 1
                    bad += [(a, b, role, var, k) for k in want if k not in ("id", "name", "basis") and want[k] != got[k]]
    assert n > 1500 and not bad, bad[:5]


def test_plain_bestiary_entries_are_rebuilt() -> None:
    """Bestiary entries written with no overrides come out of the improvised build with the same numbers."""
    adv = {e["id"]: e for e in _data.load("adversaries.yaml")["adversaries"]}
    for aid in ("adv.panther", "adv.black_bear", "adv.cave_bear"):
        e = adv[aid]
        got = build(e["archetype"], e["threat_band"], e["role"], e["variant"])
        for k in ("vitality", "defenses", "tempo", "attacks", "powers", "focus", "morale", "reduction", "calibration",
                  "advisory_alone"):
            assert got[k] == e[k], (aid, k)


def test_improvise_record_and_signature() -> None:
    a = improvise("arch.herd_beast", 2, "brute", "elite", name="the one-eyed boar")
    assert a.ruling_signature == "arch.herd_beast+2+brute+elite"
    assert a.record["template_id"] == "improvised" and a.name == "the one-eyed boar"
    assert a.vitality == a.record["vitality"] > 0 and a.guard == a.record["defenses"]["guard"]
    assert set(a.advisory_alone) == {"P1", "P2", "P3", "P4", "P5"}
    assert improvise("arch.herd_beast", 2, "brute", "elite").record == improvise("arch.herd_beast", 2, "brute",
                                                                                  "elite").record


def test_classification_bounds() -> None:
    with pytest.raises(ValueError, match="bands"):
        improvise("arch.wolf", 5, "skirmisher")              # 09.4.8: a weak dragon is a drake, not a low band
    with pytest.raises(ValueError, match="roles"):
        improvise("arch.wolf", 1, "caster")
    with pytest.raises(ValueError, match="variant"):
        improvise("arch.wolf", 1, "skirmisher", "boss")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="unknown"):
        improvise("arch.nothing", 1, "soldier")


def test_a_power_above_the_band_is_refused() -> None:
    lich = {a["id"]: a for a in _data.load("archetypes.yaml")["archetypes"]}["arch.lich"]
    assert "pow.null_field" in lich["powers"]
    assert "pow.null_field" not in improvise("arch.lich", 4, lich["roles"][0]).powers
    assert "pow.null_field" in improvise("arch.lich", 5, lich["roles"][0]).powers
