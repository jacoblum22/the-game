"""Reader golden set scorer (spec 005, US2; research notes D P1 test and D P6).

    py -3.12 evals/reader_golden.py                       # today's recorded Reader answers (no model call)
    py -3.12 evals/reader_golden.py --reader pkg.mod:fn   # any Reader: fn(line, context) -> dict of label fields

`evals/reader_golden.jsonl` holds hand-labelled player lines. Label conventions (one labeller):
- `verb`, `gate`, `necessity` describe the first beat, as 12.2.2 / 01.3.1 / 01.4.1 read today. A message with no
  beat (plain SPEECH, a FICTION_QUESTION, an out-of-fiction question such as "what do I know?") has all three
  null. When unsure between SPEECH and DECLARATION the rule's default (DECLARATION) is used.
- `gate` follows D P1's computed gate: a held licence whose scope covers the act gives G2, a sheet knack never
  gates, so threats with no licence are G1 (P-122). `necessity` is null when the gate stops the beat (G3, G4).
- facets (`against_will`, `uses_power`, `speech`) and `question_kind` (C §3: who_is, where_is, what_happened,
  what_like, what_want, who_knows, none) are the proposed Reader fields.
A field the Reader does not return is "not scored". `necessity` is scored only where its label is set.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

GOLDEN = ROOT / "evals" / "reader_golden.jsonl"
FIELDS = ("verb", "gate", "necessity", "against_will", "uses_power", "speech", "question_kind")
GATES = (None, "G0", "G1", "G2", "G3", "G4")
QUESTION_KINDS = ("who_is", "where_is", "what_happened", "what_like", "what_want", "who_knows", "none")
NECESSITY = (None, "uncertain_and_costly", "riding", "trivial", "good_idea", "impossible", "take_the_time",
             "certain_with_cost")

Reader = Callable[[str, str], dict[str, Any] | None]


def load(path: Path = GOLDEN) -> list[dict[str, Any]]:
    return [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines() if s.strip()]


def score(lines: list[dict[str, Any]], reader: Reader | None) -> str:
    """Per-field accuracy of `reader` (None: the recorded answers frozen in each line)."""
    hits = {f: [0, 0] for f in (*FIELDS, "roll")}
    issue_hits = {f: [0, 0] for f in ("verb", "gate")}
    misses: list[str] = []
    skipped = 0
    for g in lines:
        out = g.get("recorded") if reader is None else reader(g["line"], g["context"])
        if out is None:
            skipped += 1
            continue
        lab = g["labels"]
        for f in FIELDS:
            if f not in out or (f == "necessity" and lab[f] is None):
                continue
            ok = out[f] == lab[f]
            hits[f][0] += ok
            hits[f][1] += 1
            if g.get("issue") and f in issue_hits:
                issue_hits[f][0] += ok
                issue_hits[f][1] += 1
            if not ok and f in ("verb", "gate"):
                misses.append(f"{g['id']} {f}: got {out[f]}, want {lab[f]}  ({g['line'][:60]})")
        if "necessity" in out and lab["necessity"] is not None:
            hits["roll"][0] += (out["necessity"] == "uncertain_and_costly") == (lab["necessity"] == "uncertain_and_costly")
            hits["roll"][1] += 1

    def acc(h: list[int]) -> str:
        return f"{100 * h[0] / h[1]:.1f}% ({h[0]}/{h[1]})" if h[1] else "not scored"

    rows = [f"# Reader golden set ({len(lines)} lines; {len(lines) - skipped} scored, {skipped} without an answer)", ""]
    rows += [f"- {f}: {acc(hits[f])}" for f in FIELDS]
    rows += [f"- necessity as roll / no roll: {acc(hits['roll'])}",
             f"- issue lines (P-004 … P-123) verb: {acc(issue_hits['verb'])}, gate: {acc(issue_hits['gate'])}",
             "", f"## Misses (verb, gate): {len(misses)}"]
    rows += [f"- {m}" for m in misses[:12]]
    if len(misses) > 12:
        rows.append(f"- … {len(misses) - 12} more")
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--reader", default="recorded", help="module:function, or 'recorded'")
    args = ap.parse_args(argv)
    reader = None
    if args.reader != "recorded":
        from evals.replay_bench import load_plug

        reader = load_plug(args.reader)
    print(score(load(), reader))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
