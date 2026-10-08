"""Offline replay bench over recorded narration (spec 005, US1; research notes B §1.2 and B P1 "Offline A/B").

    py -3.12 evals/replay_bench.py extract --saves ../saves      # saves -> evals/corpus/narration.json.gz
    py -3.12 evals/replay_bench.py run                           # the recorded baseline (B §1.2's table)
    py -3.12 evals/replay_bench.py run --narrator pkg.mod:fn --judge pkg.mod:fn [--limit 20]

`run` needs only the committed corpus: no saves, no network, no model. A plugged narrator gets one recorded
first-draft packet as `{section name: text}` (keys starting with `_` are harness metadata: `_recorded` is the
recorded draft and its checked version) and returns at least `{"fiction": str}`. A plugged judge returns one
`{"text", "ok", "cls", "undeclared_new"}` per sentence. Contract: specs/005-measurement-harness/contracts/cli.md.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib
import json
import random
import re
import shutil
import sqlite3
import sys
import tempfile
from collections import Counter
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CORPUS = ROOT / "evals" / "corpus" / "narration.json.gz"
MAX_BYTES = 3_000_000
LATE_FROM = ("20261007", "193000")  # B §1.2 read the 33 runs from 19:30 on (code close to final)
_SECTION = re.compile(r"(?m)^\[([A-Z][A-Z ]+)\]$")
_STAMP = re.compile(r"(\d{8})-(\d{6})")

Plug = Callable[..., Any]


def sentence_key(s: str) -> str:
    """As `engine.dm.narration._key`: an unchanged sentence has the same key."""
    return " ".join(re.findall(r"\w+", s.lower()))


def sections(packet: str) -> list[tuple[str, str]]:
    parts = _SECTION.split(packet)
    return [(parts[i], parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


def load_plug(spec: str) -> Plug:
    mod, _, fn = spec.partition(":")
    return getattr(importlib.import_module(mod), fn)


# ------------------------------------------------------------------------------------------------ extract


def _late(stem: str) -> bool:
    m = _STAMP.search(stem)
    return bool(m) and (m.group(1), m.group(2)) >= LATE_FROM


def _version(v: dict[str, Any], split: Callable[[str], list[str]]) -> dict[str, Any]:
    claims = v.get("claims") or []
    return {
        "kind": v.get("kind"),
        "sents": [sentence_key(s) for s in split(v.get("text") or "")],
        "mentions": [[m.get("name"), m.get("kind")] for m in v.get("mentions") or []],
        "claims": [[c.get("sentence"), c.get("class"), c.get("subject") == "unknown"] for c in claims],
        "verdicts": [[x.get("claim"), x.get("verdict"), x.get("fix"), (x.get("reason") or "")[:48]]
                     for x in v.get("verdicts") or []],
    }


def _read_save(path: Path, split: Callable[[str], list[str]]) -> tuple[dict[str, Any], list[dict[str, Any]],
                                                                       dict[str, Any]]:
    """(save summary, turns, {turn: (first narrator packet, first draft)}) from a copy of one save."""
    with tempfile.TemporaryDirectory() as tmp:
        for suffix in ("", "-wal"):
            src = Path(str(path) + suffix)
            if src.exists():
                shutil.copy(src, Path(tmp) / (path.name + suffix))
        db = sqlite3.connect(Path(tmp) / path.name)
        try:
            calls: dict[str, Counter[str]] = {}
            for tid, role in db.execute("SELECT turn_id, role FROM model_calls"):
                calls.setdefault(str(tid), Counter())[str(role)] += 1
            first: dict[str, str] = {}
            for tid, req in db.execute("SELECT turn_id, request FROM model_calls WHERE role='narrator' "
                                       "ORDER BY row_id"):
                if tid not in first:
                    first[tid] = (json.loads(req or "{}") or {}).get("packet") or ""
            turns, packets = [], {}
            n = 0
            for tid, fb, rec in db.execute("SELECT turn_id, fallback_used, record FROM turns"):
                n += 1
                r = json.loads(rec or "{}")
                dv = r.get("draft_versions") or []
                if not dv:
                    continue
                turns.append({"save": path.stem, "turn": tid, "fallback": bool(fb),
                              "calls": dict(calls.get(tid, {})), "versions": [_version(v, split) for v in dv]})
                if first.get(tid):
                    packets[tid] = (first[tid], {"fiction": dv[0].get("text") or "",
                                                 "mentions": dv[0].get("mentions") or []})
            total = Counter()
            turn_ids = {t for (t,) in db.execute("SELECT turn_id FROM turns")}
            for tid, c in calls.items():
                if tid in turn_ids:
                    total.update(c)
        finally:
            db.close()
    return {"late": _late(path.stem), "turns": n, "calls": dict(total)}, turns, packets


def extract(saves: Path, max_packets: int = 150, seed: int = 5, out: Path = CORPUS) -> dict[str, Any]:
    from engine.dm.roles.checker import split_sentences

    corpus: dict[str, Any] = {"format": 1, "saves": {}, "turns": [], "sections": {}, "packets": []}
    pool: list[tuple[str, str, str, dict[str, Any]]] = []
    for path in sorted(saves.glob("*.db")):
        try:
            summary, turns, packets = _read_save(path, split_sentences)
        except sqlite3.DatabaseError as e:  # an old or empty file: skipped, counted
            corpus["saves"][path.stem] = {"skipped": str(e)}
            continue
        if not summary["turns"]:
            continue
        corpus["saves"][path.stem] = summary
        corpus["turns"] += turns
        if summary["late"]:
            pool += [(path.stem, t["turn"], *packets[t["turn"]]) for t in turns
                     if t["turn"] in packets and _first_checked(t) is not None]
    for stem, tid, packet, draft in sorted(random.Random(seed).sample(pool, min(max_packets, len(pool)))):
        refs = []
        for name, text in sections(packet):
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            corpus["sections"][h] = text
            refs.append([name, h])
        corpus["packets"].append({"save": stem, "turn": tid, "sections": refs, "draft": draft})
    out.parent.mkdir(parents=True, exist_ok=True)
    data = gzip.compress(json.dumps(corpus, sort_keys=True, separators=(",", ":")).encode("utf-8"), mtime=0)
    if len(data) > MAX_BYTES:
        raise SystemExit(f"corpus is {len(data)} bytes, over {MAX_BYTES}: lower --max-packets")
    out.write_bytes(data)
    return corpus


def load(path: Path = CORPUS) -> dict[str, Any]:
    return json.loads(gzip.decompress(path.read_bytes()))


# ------------------------------------------------------------------------------------------------ measures


def _first_checked(t: dict[str, Any]) -> dict[str, Any] | None:
    """The first version the Checker read (a mention redraft comes before the check, PR-00-7)."""
    return next((v for v in t["versions"] if v["claims"]), None)


def _failing(v: dict[str, Any]) -> list[list[Any]]:
    return [x for x in v["verdicts"] if x[1] != "supported"]


def _pct(a: float, b: float) -> str:
    return f"{a}/{b} ({100 * a / b:.1f}%)" if b else f"{a}/0"


def instability(turns: Iterable[dict[str, Any]]) -> tuple[int, int]:
    """(identical sentences re-checked by the Checker in the next draft, of those whose claim classes differ).
    Cut versions reuse the old claims, so only drafts and redrafts count."""
    same = differ = 0
    for t in turns:
        checked = [v for v in t["versions"] if v["kind"] in ("draft", "redraft") and v["claims"]]
        for a, b in zip(checked, checked[1:], strict=False):
            ca: dict[str, set[str]] = {}
            cb: dict[str, set[str]] = {}
            for v, into in ((a, ca), (b, cb)):
                for n, cls, _ in v["claims"]:
                    if isinstance(n, int) and 0 <= n < len(v["sents"]):
                        into.setdefault(v["sents"][n], set()).add(cls)
            keys_b = {k: i for i, k in enumerate(b["sents"])}
            for k in dict.fromkeys(a["sents"]):
                if k and k in keys_b:
                    same += 1
                    differ += ca.get(k, set()) != cb.get(k, set())
    return same, differ


def recorded_measures(corpus: dict[str, Any], late_only: bool) -> dict[str, Any]:
    saves = {k: v for k, v in corpus["saves"].items() if "turns" in v and (v["late"] or not late_only)}
    turns = [t for t in corpus["turns"] if t["save"] in saves]
    n_turns = sum(s["turns"] for s in saves.values())
    calls: Counter[str] = Counter()
    for s in saves.values():
        calls.update(s["calls"])
    firsts = [(t, v) for t in turns if (v := _first_checked(t)) is not None]
    passed = sum(1 for _, v in firsts if not _failing(v))
    same, differ = instability(turns)
    reasons = Counter()
    pairs: Counter[str] = Counter()
    contra: Counter[str] = Counter()
    for t in turns:
        for v in t["versions"]:
            for *_, reason in v["verdicts"]:
                if reason.startswith("the Oracle settled it as drafted"):
                    reasons["yes"] += 1
                elif reason.startswith("the Oracle settled it:"):
                    reasons["no"] += 1
                elif reason.startswith("nothing settles it"):
                    reasons["cut"] += 1
    for _, v in firsts:
        for ci, verdict, _, _ in _failing(v):
            cls = v["claims"][ci][1] if isinstance(ci, int) and ci < len(v["claims"]) else "?"
            pairs[f"{verdict}/{cls}"] += 1
            if verdict == "contradicted":
                contra[cls] += 1
    declared = sum(len(t["versions"][0]["mentions"]) for t, _ in firsts)
    undeclared = sum(1 for _, v in firsts for c in v["claims"] if c[2])
    other = sum(calls.values()) - calls["narrator"] - calls["checker"]
    return {
        "population": f"{len(saves)} saves, {n_turns} turns, {len(turns)} narrated",
        "first-draft pass rate": _pct(passed, len(firsts)),
        "delivered as first drafted": _pct(sum(1 for t in turns if len(t["versions"]) == 1 and not t["fallback"]),
                                           len(turns)),
        "turns with cut sentences": _pct(sum(1 for t in turns if any(v["kind"] == "cut" for v in t["versions"])),
                                         len(turns)),
        "fallback turns": _pct(sum(1 for t in turns if t["fallback"]), len(turns)),
        "class instability, unchanged sentences": _pct(differ, same),
        "calls/turn narrator, checker, other": (f"{calls['narrator'] / n_turns:.2f}, {calls['checker'] / n_turns:.2f}, "
                                                f"{other / n_turns:.2f}") if n_turns else "n/a",
        "narrator calls/narrated turn": f"{sum(t['calls'].get('narrator', 0) for t in turns) / len(turns):.2f}"
                                        if turns else "n/a",
        "Oracle on drafted details: asked, no (redraft), cut": (f"{sum(reasons.values())}, {reasons['no']}, "
                                                                f"{reasons['cut']}"),
        "new elements per first draft: declared, undeclared": (f"{declared / len(firsts):.2f}, "
                                                               f"{undeclared / len(firsts):.2f}") if firsts else "n/a",
        "contradicted per first draft, by class": ", ".join(f"{k} {v}" for k, v in contra.most_common()),
        "top failing verdict/class (first drafts)": ", ".join(f"{k} {v}" for k, v in pairs.most_common(6)),
    }


# ------------------------------------------------------------------------------------------------ plugs


def packet_items(corpus: dict[str, Any], limit: int | None = None) -> list[dict[str, Any]]:
    """Each corpus packet as `{section: text, "_recorded": {...}}`."""
    by_turn = {(t["save"], t["turn"]): t for t in corpus["turns"]}
    out = []
    for p in corpus["packets"][:limit]:
        item: dict[str, Any] = {name: corpus["sections"][h] for name, h in p["sections"]}
        item["_recorded"] = {"save": p["save"], "turn": p["turn"], "draft": p["draft"],
                             "checked": _first_checked(by_turn[(p["save"], p["turn"])])}
        out.append(item)
    return out


def recorded_narrator(packet: dict[str, Any]) -> dict[str, Any]:
    return packet["_recorded"]["draft"]


def recorded_judge(packet: dict[str, Any], draft: dict[str, Any]) -> list[dict[str, Any]]:  # noqa: ARG001
    """The recorded Checker + code verdicts of the first checked version, per sentence."""
    v = packet["_recorded"]["checked"]
    out = [{"text": k, "ok": True, "cls": None, "undeclared_new": False} for k in v["sents"]]
    for ci, verdict, _, _ in v["verdicts"]:
        n, cls, unknown = v["claims"][ci] if isinstance(ci, int) and ci < len(v["claims"]) else (None, None, False)
        if not isinstance(n, int) or not 0 <= n < len(out):
            continue
        out[n]["undeclared_new"] |= bool(unknown)
        if verdict != "supported" and out[n]["ok"]:
            out[n].update(ok=False, cls=cls)
    return out


def _drafts(items: list[dict[str, Any]], narrator: Plug, workers: int) -> list[dict[str, Any] | None]:
    """Each item's draft (None for a plug failure), `workers` at a time (a model plug is I/O bound)."""
    def one(item: dict[str, Any]) -> dict[str, Any] | None:
        try:
            return narrator(item)
        except Exception as e:  # noqa: BLE001 - a plug failure is a failed draft, not a bench failure
            print(f"plug error: {e.__class__.__name__}: {str(e)[:200]}", file=sys.stderr)
            return None
    if workers <= 1:
        return [one(i) for i in items]
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(workers) as pool:
        return list(pool.map(one, items))


def plugged_measures(items: list[dict[str, Any]], narrator: Plug, judge: Plug, workers: int = 1) -> dict[str, Any]:
    passed = errors = sents = bad = undeclared = declared = 0
    classes: Counter[str] = Counter()
    loop: Counter[str] = Counter()  # spec 006 plugs report the whole narration loop (calls, cuts, renders)
    for item, draft in zip(items, _drafts(items, narrator, workers), strict=True):
        try:
            if draft is None:
                raise ValueError("no draft")
            verdicts = judge(item, draft)
        except Exception:  # noqa: BLE001 - a plug failure is a failed draft, not a bench failure
            errors += 1
            continue
        fails = [s for s in verdicts if not s["ok"]]
        if "_first_pass" in draft:  # coverage counts too (12.3.1a item 3)
            passed += bool(draft["_first_pass"])
            loop.update(turns=1, calls=draft["_calls"], cut=draft["_cut"], rendered=draft["_rendered"],
                        missing_first=bool(draft["_missing_first"]), sentences=len(verdicts),
                        added_about=sum(s.get("added_about", 0) for s in verdicts))
            loop.update(**{k: v for k, v in (draft.get("_audit") or {}).items()},
                        audited=bool(draft.get("_audit")))
            undeclared += sum(s.get("undeclared_new", 0) for s in verdicts)
            declared += sum(len(s.get("new") or []) for s in draft.get("_sentences") or [])
        else:
            passed += not fails
            undeclared += sum(1 for s in verdicts if s.get("undeclared_new"))
            declared += len(draft.get("mentions") or [])
        sents += len(verdicts)
        bad += len(fails)
        classes.update(str(s.get("cls")) for s in fails)
    n = len(items)
    out = {
        "packets": n,
        "first-draft pass rate": _pct(passed, n),
        "failing sentences": _pct(bad, sents),
        "new elements per draft: declared, undeclared": f"{declared / n:.2f}, {undeclared / n:.2f}" if n else "n/a",
        "plug errors": errors,
        "top failing classes": ", ".join(f"{k} {v}" for k, v in classes.most_common(5)),
    }
    if loop["turns"]:
        t = loop["turns"]
        out.update({
            "first drafts missing a must-name line": _pct(loop["missing_first"], t),
            "turns with cut sentences": _pct(loop["cut"], t),
            "turns with a rendered line": _pct(loop["rendered"], t),
            "narrator calls per turn": f"{loop['calls'] / t:.2f}",
            "names used but not declared (added to about) per draft": f"{loop['added_about'] / t:.2f}",
        })
        if loop["audited"]:
            a = loop["audited"]
            out["audit (Checker) per first draft: undeclared new elements, claims on undeclared subjects"] = (
                f"{loop['audit_unknown_new'] / a:.2f}, {loop['audit_undeclared_subject'] / a:.2f} ({a} drafts)")
    return out


def report(corpus: dict[str, Any], narrator: str | None = None, judge: str | None = None,
           limit: int | None = None, workers: int = 1) -> str:
    size = CORPUS.stat().st_size if CORPUS.exists() else 0
    lines = [f"# Replay bench (corpus {size // 1024} KB, {len(corpus['packets'])} packets)", ""]
    for label, late in (("all saves", False), ("late saves (B §1.2 population)", True)):
        lines.append(f"## Recorded, {label}")
        lines += [f"- {k}: {v}" for k, v in recorded_measures(corpus, late).items()]
        lines.append("")
    items = packet_items(corpus, limit)
    runs = [("recorded narrator + recorded judge", recorded_narrator, recorded_judge)]
    if narrator or judge:
        runs.append((f"{narrator or 'recorded'} + {judge or 'recorded'}",
                     load_plug(narrator) if narrator else recorded_narrator,
                     load_plug(judge) if judge else recorded_judge))
    for label, n, j in runs:
        lines.append(f"## Packets: {label}")
        lines += [f"- {k}: {v}" for k, v in plugged_measures(items, n, j, workers if n is not recorded_narrator
                                                                            else 1).items()]
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("extract")
    ex.add_argument("--saves", type=Path, default=ROOT / "saves")
    ex.add_argument("--max-packets", type=int, default=150)
    rn = sub.add_parser("run")
    rn.add_argument("--narrator")
    rn.add_argument("--judge")
    rn.add_argument("--limit", type=int)
    rn.add_argument("--workers", type=int, default=1, help="plugged narrator calls at a time")
    args = ap.parse_args(argv)
    if args.cmd == "extract":
        c = extract(args.saves, args.max_packets)
        print(f"corpus: {len(c['saves'])} saves, {len(c['turns'])} narrated turns, {len(c['packets'])} packets, "
              f"{len(c['sections'])} sections, {CORPUS.stat().st_size // 1024} KB")
        return 0
    print(report(load(), args.narrator, args.judge, args.limit, args.workers))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
