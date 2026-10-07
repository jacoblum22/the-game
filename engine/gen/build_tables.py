"""Build-time only: precompute the deterministic numbers the generators read from the rules' reference code.

    python -m engine.gen.build_tables          # rewrites engine/gen/data/*.json (about 30 s)

Two outputs, both pure functions of `rules/data` and the reference code (no randomness):

- `threat_words.json`: PR-10-8's word for every encounter row PR-10-10 can write (every archetype, home band,
  relative band and shape it can field; every int band of the nearest-band fallback; every row of the generic
  tables in `travel.yaml`). The word is PR-09-4 against the reference PCs, computed by
  `_process/simulation/10-word-audit.py#audit_row`.
- `adversary_solve.json`: PR-09-1's Vitality solve (09.4.4-09.4.5) and the PR-09-4 advisories for every
  archetype x band x role x variant, single creature, computed by `09-gen_data09.py#build` (a power whose
  `min_band` exceeds the band is refused, PR-09-1 step 7, by building with it dropped).

The engine never imports `rules/_process`; it reads these files. Rerun this script whenever an input changes:
`sources.json` holds the inputs' hashes and `tests/engine/test_gen_adversary.py` fails while they are stale. When
PR-09-1's estimator is ported to the engine (T085, Milestone 2) these tables give way to the computation itself.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

from engine.gen import _data

REPO = Path(__file__).resolve().parents[2]
SIM = REPO / "rules" / "_process" / "simulation"
OUT = Path(__file__).resolve().parent / "data"
WORDS = ["trivial", "easy", "fair", "hard", "lethal"]
LADDER = [("6-8", "minion"), ("4-6", "minion"), ("2", "standard"), ("1", "elite"), ("1-2", "standard"),
          ("1", "standard"), ("2", "minion"), ("1", "minion"), ("1", "solo")]
LABELS = {"home-1": -1, "home": 0, "home+1": 1}


def _patched_yaml() -> None:
    """The reference scripts read data with yaml.safe_load; give them the same known-defect fix as _data."""
    orig = yaml.safe_load
    if getattr(orig, "_gen_patched", False):
        return

    def safe_load(stream: Any) -> Any:
        if hasattr(stream, "read"):
            name = os.path.basename(getattr(stream, "name", ""))
            return _data.parse(name, stream.read())
        return orig(stream)

    safe_load._gen_patched = True  # type: ignore[attr-defined]
    yaml.safe_load = safe_load


def load_module(name: str, file: str) -> ModuleType:
    _patched_yaml()
    spec = importlib.util.spec_from_file_location(name, SIM / file)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    argv, sys.argv = sys.argv, [str(SIM / file)]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    return mod


def gen09() -> dict[str, Any]:
    """09-gen_data09.py executed up to its write step (as 10-word-audit.py does)."""
    _patched_yaml()
    path = SIM / "09-gen_data09.py"
    src = path.read_text(encoding="utf-8")
    ns: dict[str, Any] = {"__file__": str(path), "__name__": "gen09_for_engine"}
    exec(compile(src[: src.index("\nADV = []")], str(path), "exec"), ns)
    return ns


def row_key(refs: list[str], band: Any, count: Any, variant: str | None, leader: bool, home: int) -> str:
    return "{}|{}|{}|{}|{:d}|{:d}".format("+".join(refs), band, count, variant or "standard", int(bool(leader)), home)


def _enc(r: dict[str, Any]) -> list[Any]:
    w = lambda k: WORDS.index(r[k][0]) if k in r else None  # noqa: E731
    out: list[Any] = [r["band"], w("mid"), w("high"), w("light_mid"), w("light_high")]
    if r["problems"]:
        out.append(r["problems"])
    return out


def threat_words(wa: ModuleType) -> dict[str, list[Any]]:
    out: dict[str, list[Any]] = {}
    arch = wa.ARCH
    for a in sorted(arch):
        lo, hi = arch[a]["bands"]
        for home in range(1, 6):
            for label, off in LABELS.items():
                if not lo <= max(1, min(5, home + off)) <= hi:
                    continue
                for count, variant in LADDER:
                    row = {"band": label, "ref": [a], "count": count, "variant": variant, "leader": False}
                    out[row_key([a], label, count, variant, False, home)] = _enc(wa.audit_row(row, home))
            for b in range(lo, hi + 1):
                row = {"band": b, "ref": [a], "count": "1", "variant": "standard", "leader": False}
                out[row_key([a], b, "1", "standard", False, home)] = _enc(wa.audit_row(row, home))
    travel = _data.load("travel.yaml")
    for t in travel["encounter_tables"]:
        for home, rows in t["threat_by_home"].items():
            for row in rows:
                k = row_key(row["ref"], row["band"], row.get("count", "1"), row.get("variant"),
                            row.get("leader", False), int(home))
                out[k] = _enc(wa.audit_row(row, int(home)))
    return out


def adversary_solve(ns: dict[str, Any]) -> dict[str, Any]:
    arch, build, V = ns["ARCH"], ns["build"], ns["RO"].V
    out: dict[str, Any] = {}
    for a in sorted(arch):
        lo, hi = arch[a]["bands"]
        for b in range(lo, hi + 1):
            for role in ns["ROLES"]:
                for variant in ns["VARIANTS"]:
                    before = len(ns["errors"])
                    # PR-09-1 step 7: a power whose min_band exceeds the band is refused (dropped), not built
                    drop = [p for p in arch[a]["powers"] if (ns["POWERS"][p].get("min_band") or 0) > b]
                    e = build(V("solve", "solve", a, b, role, variant, drop_powers=drop))
                    errs = ns["errors"][before:]
                    del ns["errors"][before:]
                    if e is None:
                        continue
                    cal = e["calibration"]
                    adv = "".join(str(WORDS.index(e["advisory_alone"][f"P{p:d}"])) for p in range(1, 6))
                    noc = e["advisory_without_counter"]
                    noc_s = "".join(str(WORDS.index(noc[f"P{p:d}"])) for p in range(1, 6)) if noc else None
                    out[f"{a}|{b:d}|{role}|{variant}"] = [cal["solved_vitality"], cal["fidelity"],
                                                                  cal["severity_compensation"], adv, noc_s,
                                                                  errs or None]
    return out


# the inputs the tables are computed from; `sources.json` records their hashes so a stale table is detected
SOURCES = ["rules/data/archetypes.yaml", "rules/data/adversaries.yaml", "rules/data/travel.yaml",
           "rules/_process/simulation/10-word-audit.py", "rules/_process/simulation/09-gen_data09.py",
           "rules/_process/simulation/09_core.py", "rules/_process/simulation/09_data_adv.py",
           "rules/_process/simulation/09_data_arch.py", "rules/_process/simulation/09_data_arch2.py",
           "rules/_process/simulation/09_data_powers.py", "rules/_process/simulation/09_data_beh.py"]


def source_hashes() -> dict[str, str]:
    return {p: hashlib.sha256((REPO / p).read_bytes()).hexdigest() for p in SOURCES}


def build_all() -> dict[str, Any]:
    wa = load_module("word_audit_10_engine", "10-word-audit.py")
    return {"threat_words.json": threat_words(wa), "adversary_solve.json": adversary_solve(gen09()),
            "sources.json": source_hashes()}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, data in build_all().items():
        (OUT / name).write_text(json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        print(f"{name}: {len(data):d} entries")


if __name__ == "__main__":
    main()
