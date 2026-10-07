"""PR-10-10 (build an encounter table's threat sub-table) and PR-10-8 (its audit), for the world seed.

A port of `_process/simulation/10_table_builder.py` and `10-word-audit.py#audit_table`. The one input the
engine does not compute yet is PR-09-4's word for a row (it needs PR-09-1's estimator, Milestone 2): it is read
from `data/threat_words.json`, precomputed from the reference code by `build_tables.py`.
"""

from __future__ import annotations

import functools
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.gen import _data
from engine.gen._rng import SeedRng

WORDS = ["trivial", "easy", "fair", "hard", "lethal"]
SLOTS = [(3, -1), (3, -1), (3, 0), (3, 0), (3, 0), (2, 0), (2, 1), (1, 1)]
# T-10-25 start shapes: (count, variant) per home band, one per slot (same order as SLOTS)
START: dict[int, list[tuple[str, str]]] = {
    1: [("1-2", "standard"), ("1-2", "standard"), ("6-8", "minion"), ("6-8", "minion"), ("2", "standard"),
        ("1", "elite"), ("1", "standard"), ("2", "minion")],
    2: [("4-6", "minion"), ("2", "standard"), ("2", "standard"), ("1", "elite"), ("4-6", "minion"),
        ("2", "standard"), ("1", "minion"), ("1", "minion")],
    3: [("6-8", "minion"), ("2", "standard"), ("1", "elite"), ("2", "minion"), ("1", "elite"), ("1", "standard"),
        ("1", "minion"), ("1", "minion")],
    4: [("2", "standard"), ("1", "elite"), ("1", "standard"), ("1", "elite"), ("1", "standard"), ("1", "standard"),
        ("1", "minion"), ("1", "minion")],
    5: [("2", "standard"), ("1", "standard"), ("1", "standard"), ("1", "minion"), ("1", "minion"),
        ("1", "standard"), ("1", "solo"), ("1", "solo")],
}
LADDER = [("6-8", "minion"), ("4-6", "minion"), ("2", "standard"), ("1", "elite"), ("1-2", "standard"),
          ("1", "standard"), ("2", "minion"), ("1", "minion")]
SOLO_LADDER = [("1", "solo"), ("1", "elite"), ("1", "standard"), ("1", "minion")]
CEILING = {-1: "fair", 0: "fair", 1: "hard"}
LABEL = {-1: "home-1", 0: "home", 1: "home+1"}

Row = dict[str, Any]


@functools.lru_cache(maxsize=1)
def _words() -> dict[str, list[Any]]:
    return json.loads((Path(__file__).resolve().parent / "data" / "threat_words.json").read_text(encoding="utf-8"))


@functools.lru_cache(maxsize=1)
def archetypes() -> dict[str, dict[str, Any]]:
    return {a["id"]: a for a in _data.load("archetypes.yaml")["archetypes"]}


@functools.lru_cache(maxsize=1)
def adversaries() -> dict[str, dict[str, Any]]:
    doc = _data.load("adversaries.yaml")
    out = {e["id"]: e for e in doc["adversaries"]}
    for b in doc.get("blocks") or []:
        for e in b.get("entries") or []:
            out[e["id"]] = e
    return out


def _range(s: Any) -> tuple[int, int]:
    a, _, b = str(s).partition("-")
    return int(a), int(b or a)


def audit_row(row: Row, home: int) -> dict[str, Any]:
    """# rule: PR-10-8 step 2 -- one threat row's words at a home band (precomputed PR-09-4, see module doc)."""
    key = "{}|{}|{}|{}|{:d}|{:d}".format("+".join(row["ref"]), row["band"], row.get("count", "1"), row.get("variant") or "standard", int(bool(row.get("leader"))), home)
    try:
        enc = _words()[key]
    except KeyError:
        raise KeyError(f"no precomputed PR-10-8 word for {key}: rerun python -m engine.gen.build_tables") from None
    out: dict[str, Any] = {"problems": list(enc[5]) if len(enc) > 5 else [], "band": enc[0]}
    for i, k in ((1, "mid"), (2, "high"), (3, "light_mid"), (4, "light_high")):
        if enc[i] is not None:
            out[k] = (WORDS[enc[i]],)
    return out


def _slot_band(home: int, off: int) -> int:
    return max(1, min(5, home + off))


def _rungs(start: tuple[str, str]) -> list[tuple[str, str]]:
    lad = SOLO_LADDER if start[1] == "solo" else LADDER
    return lad[lad.index(start):]


def _weighted_pick(rng: SeedRng, items: Sequence[tuple[str, float]]) -> str:
    tot = sum(w for _, w in items)
    x = rng.random() * tot
    for k, w in items:
        x -= w
        if x < 0:
            return k
    return items[-1][0]


def _try_slot(arch: str, home: int, off: int, start: tuple[str, str]) -> tuple[Row | None, str | None]:
    for count, variant in _rungs(start):
        row = {"range": "1", "band": LABEL[off], "ref": [arch], "count": count, "variant": variant, "leader": False}
        r = audit_row(row, home)
        if r["problems"] or "mid" not in r:
            continue
        ok = WORDS.index(r["mid"][0]) <= WORDS.index(CEILING[off]) and r["high"][0] != "lethal"
        if ok and "light_mid" in r:
            ok = WORDS.index(r["light_mid"][0]) <= WORDS.index(CEILING[off]) and r["light_high"][0] != "lethal"
        if ok:
            return row, r["mid"][0]
    return None, None


def build_threat_table(pool: Mapping[str, float], home: int, rng: SeedRng,
                       fallback_pool: Mapping[str, float] | None = None) -> tuple[list[Row], list[tuple[Any, ...]]]:
    """# rule: PR-10-10 -- a d20 threat sub-table from a weighted archetype pool; returns (rows, log)."""
    arch = archetypes()
    rows: list[Row] = []
    log: list[tuple[Any, ...]] = []
    used: set[str] = set()
    face = 1
    for i, (w, off) in enumerate(SLOTS):
        b = _slot_band(home, off)
        chosen: tuple[Row, str, str] | None = None
        for which, src in (("pool", pool), ("fallback", fallback_pool or {})):
            cands = {a: wt for a, wt in src.items() if a in arch and arch[a]["bands"][0] <= b <= arch[a]["bands"][1]
                     and wt > 0}
            tried: set[str] = set()
            while cands.keys() - tried:
                fresh = [(a, wt) for a, wt in sorted(cands.items()) if a not in tried and a not in used]
                pick_from = fresh or [(a, wt) for a, wt in sorted(cands.items()) if a not in tried]
                a = _weighted_pick(rng, pick_from)
                tried.add(a)
                row, word = _try_slot(a, home, off, START[home][i])
                if row and word:
                    chosen = (row, word, which)
                    break
            if chosen:
                break
        if not chosen:
            allp = dict(fallback_pool or {})
            allp.update(pool)
            best = sorted((min(abs(b - arch[a]["bands"][0]), abs(b - arch[a]["bands"][1])), a) for a in allp if a in arch)
            for _, a in best:
                nb = max(arch[a]["bands"][0], min(arch[a]["bands"][1], b))
                row = {"range": "1", "band": nb, "ref": [a], "count": "1", "variant": "standard", "leader": False}
                r = audit_row(row, home)
                if "mid" in r and WORDS.index(r["mid"][0]) <= WORDS.index(CEILING[off]) and \
                        ("light_mid" not in r or WORDS.index(r["light_mid"][0]) <= WORDS.index(CEILING[off])):
                    chosen = (row, r["mid"][0], "nearest band")
                    break
        if not chosen:
            raise RuntimeError(f"PR-10-10: no archetype can fill slot {i + 1:d} at home {home:d}")
        row, word, which = chosen
        used.add(row["ref"][0])
        lo, hi = face, face + w - 1
        face = hi + 1
        out: Row = {"range": str(lo) if lo == hi else f"{lo:d}-{hi:d}", "kind": "adversary", "ref": row["ref"],
                    "band": row["band"], "count": row["count"]}
        if row["variant"] != "standard":
            out["variant"] = row["variant"]
        out.update({"threat": True, "ambush": "lurker" in arch[row["ref"][0]]["roles"], "complication": i == 3,
                    "when": "any"})
        rows.append(out)
        log.append((i + 1, row["ref"][0], row["band"], row["count"], row["variant"], word, which))
    return rows, log


def audit_table(threat_rows: list[Row], home: int, non_threat: list[Row] | None = None,
                deadly_only: bool = False) -> tuple[bool, dict[str, Any], list[str], list[Any]]:
    """# rule: PR-10-8 -- one threat sub-table at one home band: (ok, summary, failures, row results)."""
    fails: list[str] = []
    wsum: Counter[str] = Counter()
    lsum: Counter[str] = Counter()
    bands: Counter[str] = Counter()
    rows_out: list[Any] = []
    for row in threat_rows:
        lo, hi = _range(row["range"])
        w = hi - lo + 1
        r = audit_row(row, home)
        if "mid" not in r:
            fails.append("row {}: cannot be fielded ({})".format(row["range"], "; ".join(r["problems"])))
            continue
        rel = row["band"] if not isinstance(row["band"], int) else {-1: "home-1", 0: "home", 1: "home+1"}.get(
            row["band"] - home, "out of band {:+d}".format(row["band"] - home))
        bands[rel] += w
        wd = r["mid"][0]
        wsum[wd] += w
        refs = "+".join(row["ref"])
        for p in r["problems"]:
            fails.append("row {} ({}): {}".format(row["range"], refs, p))
        if wd == "lethal" or r["high"][0] == "lethal":
            fails.append("row {} ({}): lethal{}".format(row["range"], refs, "" if wd == "lethal" else " at the high face"))
        if wd == "hard" and row.get("complication"):
            fails.append("row {} ({}): hard and complication: true".format(row["range"], refs))
        if "light_mid" in r:
            lw = r["light_mid"][0]
            lsum[lw] += w
            if lw == "lethal" or r["light_high"][0] == "lethal":
                fails.append("row {} ({}): lethal for the light reference{}".format(row["range"], refs, "" if lw == "lethal" else " at the high face"))
            if lw == "hard" and row.get("complication"):
                fails.append("row {} ({}): hard for the light reference and complication: true".format(row["range"], refs))
        rows_out.append((row, r))
    total = sum(wsum.values())
    fair = sum(wsum[k] for k in ("trivial", "easy", "fair"))
    if fair * 3 < total * 2:
        fails.append(f"only {fair:d}/{total:d} threat faces fair or easier")
    lfair = sum(lsum[k] for k in ("trivial", "easy", "fair"))
    if lsum and lfair * 3 < total * 2:
        fails.append(f"only {lfair:d}/{total:d} threat faces fair or easier for the light reference")
    for k, want in (("home-1", 6), ("home", 11), ("home+1", 3)):
        if abs(bands.get(k, 0) - want) > 1:
            fails.append(f"band weights {dict(bands)} (want 6/11/3 +-1)")
            break
    if any(k.startswith("out of band") for k in bands):
        fails.append(f"rows outside home-1..home+1: {dict(bands)}")
    if non_threat is not None and not deadly_only:
        faces = sum(_range(r["range"])[1] - _range(r["range"])[0] + 1 for r in non_threat)
        if faces != 6:
            fails.append(f"non-threat sub-table has {faces:d} faces (want 6)")
    summary = {"words": dict(wsum), "fair_or_easier": fair, "total": total, "bands": dict(bands),
               "light_words": dict(lsum), "light_fair_or_easier": lfair if lsum else None}
    return (not fails), summary, fails, rows_out
