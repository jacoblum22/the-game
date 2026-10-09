"""The spec-007 Reader on the golden set (D P1 test 2): the real Reader prompt and schema, the computed gate.

    py -3.12 evals/reader_live.py --model haiku        # 91 Claude CLI calls (owner's subscription), cached
    py -3.12 evals/reader_live.py --cached              # re-score the cached answers, no call

Each line's context string stands in for the store: licences "held" in it are the PC's (`holds lic.x`,
`holding lic.x`; "does not hold" is not), and a context naming any `lic.lang.*` puts literacy on record. The
packet is the Reader's own (instructions, core cards, the context as the view, the line as THIS MESSAGE). The first
beat's verb is the covering verb the gate computes from the Reader's verb and facets (00.12.3); its gate is
`compute_gate` over the context's holdings. `necessity` is not scored: it needs state a context string lacks.
Answers are cached in `evals/baselines/reader_golden_haiku.jsonl` (raw model output per line id).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.data.loader import load_rules  # noqa: E402
from engine.dm.packet import build_packet  # noqa: E402
from engine.dm.roles.prompts import load_prompt  # noqa: E402
from engine.dm.roles.reader import normalise, now_beats  # noqa: E402
from engine.dm.schemas import SchemaContext, build_schema  # noqa: E402
from engine.llm.base import Role  # noqa: E402
from engine.resolve.gate import WRITING, compute_gate, covering_verb  # noqa: E402
from engine.retrieve.cards import load_cards_for  # noqa: E402
from engine.retrieve.scene import READING  # noqa: E402
from evals import reader_golden as rg  # noqa: E402

CACHE = ROOT / "evals" / "baselines" / "reader_golden_haiku.jsonl"
# the held-out set (labelled by the same policy before the beat normalisation was written) is never tuned on
SETS = {"golden": (rg.GOLDEN, CACHE),
        "heldout": (ROOT / "evals" / "reader_heldout.jsonl", ROOT / "evals" / "baselines" / "reader_heldout_haiku.jsonl"),
        # spec 020's goal-shape breadth set (labelled by 01.2.2 before any run; never tuned on)
        "goalshape": (ROOT / "evals" / "reader_goalshape.jsonl",
                      ROOT / "evals" / "baselines" / "reader_goalshape_haiku.jsonl"),
        # 14 more, labelled after the first post-change run, before the prompt revision was run: never tuned on
        "goalshape_heldout": (ROOT / "evals" / "reader_goalshape_heldout.jsonl",
                              ROOT / "evals" / "baselines" / "reader_goalshape_heldout_haiku.jsonl")}
RULES = load_rules()
HELD = re.compile(r"(?<!not )\b(?:holds?|holding)\s+(lic\.[a-z_]+\.[a-z_]+)")


def schema() -> dict[str, Any]:
    res, pacing = RULES.resolution, RULES.pacing
    ctx = SchemaContext(input_classes=[c for c in pacing["input_classes"] if c != "PENDING_ANSWER"],
                        oracle_rungs=[r["id"] for r in res["oracle"]["rungs"]], verbs=list(RULES.basic_verbs),
                        change_kinds=list(res["intended_change"]["kinds"]))
    return build_schema(Role.READER, ctx)


def packet(line: str, context: str) -> Any:
    cards = load_cards_for(Role.READER, [], None, [], rules=RULES)
    return build_packet(Role.READER, instructions=load_prompt("reader"), cards=cards,
                        view=f"Scene (as described): {context}", exchanges=[], message=line, rules=RULES)


def ask(line: str, context: str, model: str) -> dict[str, Any]:
    """One Reader call, after the engine's code pre-router (reader.knowledge_parts: "what do I know?" never
    reaches the model; a message that is only that makes no call)."""
    from engine.dm.roles.reader import knowledge_parts
    from evals.playtest import ask_claude

    known, rest = knowledge_parts(line)
    if not rest:
        return {"parts": [{"text": p.text, "class": p.cls, "question_kind": "none", "topic": None} for p in known],
                "beats": [], "fact_questions": []}
    p = packet(rest, context)
    data, _ = ask_claude(p.instructions, p.render(include_instructions=False), schema(), model)
    return data


def labels_from(data: dict[str, Any], line: str, context: str) -> dict[str, Any]:
    """The scored fields from one Reader answer, after the engine's beat normalisation: the covering verb and the
    computed gate of the first beat."""
    data = normalise(data)
    kinds = [p.get("question_kind") for p in data.get("parts", []) if p.get("question_kind") not in (None, "none")]
    beats = now_beats(data.get("beats", []))
    out: dict[str, Any] = {"question_kind": kinds[0] if kinds else "none", "verb": None, "gate": None,
                           "goals": [(b.get("change") or {}).get("kind") or "none" for b in beats]}
    if not beats:
        return out
    b = beats[0]
    aw, up, sp = bool(b.get("against_will")), bool(b.get("uses_power")), bool(b.get("speech"))
    verb = covering_verb(b.get("verb"), against_will=aw, speech=sp)
    text = f"{b.get('method', '')} {b.get('intent', '')}"
    reading = verb == "verb.observe" and bool(READING.search(text)) and bool(WRITING.search(text))
    c = compute_gate(b.get("verb"), against_will=aw, uses_power=up, speech=sp, method=text,
                     held=HELD.findall(context), rules=RULES, reading=reading, literacy_known="lic.lang" in context)
    out.update(verb=c.verb, gate=c.gate, against_will=aw, uses_power=up, speech=sp, raw_verb=b.get("verb"),
               change_kind=(b.get("change") or {}).get("kind"))
    return out


def run(model: str, lines: list[dict[str, Any]], cache: Path = CACHE, workers: int = 4) -> dict[str, dict[str, Any]]:
    cached = load_cache(cache)
    todo = [g for g in lines if g["id"] not in cached]

    def one(g: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        return g["id"], ask(g["line"], g["context"], model)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for gid, data in ex.map(one, todo):
            cached[gid] = data
            with cache.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"id": gid, "answer": data}) + "\n")
    return cached


def load_cache(cache: Path = CACHE) -> dict[str, dict[str, Any]]:
    if not cache.exists():
        return {}
    rows = [json.loads(s) for s in cache.read_text(encoding="utf-8").splitlines() if s.strip()]
    return {r["id"]: r["answer"] for r in rows}


def report(answers: dict[str, dict[str, Any]], lines: list[dict[str, Any]] | None = None) -> str:
    lines = rg.load() if lines is None else lines
    by_id = {g["id"]: labels_from(answers[g["id"]], g["line"], g["context"]) for g in lines if g["id"] in answers}

    def reader(line: str, context: str) -> dict[str, Any] | None:
        g = next(x for x in lines if x["line"] == line and x["context"] == context)
        return by_id.get(g["id"])

    paired = [g for g in lines if g.get("pair")]
    out = [rg.score(lines, reader), "", f"## Negation pairs ({len({g['pair'] for g in paired})} pairs, {len(paired)} lines)",
           rg.score(paired, reader)]
    raw = [g for g in lines if g["id"] in by_id and by_id[g["id"]].get("raw_verb") is not None]
    raw_ok = sum(by_id[g["id"]]["raw_verb"] == g["labels"]["verb"] for g in raw)
    out += ["", f"Reader's own verb before the facets choose the card: {100 * raw_ok / max(1, len(raw)):.1f}% "
                f"({raw_ok}/{len(raw)})"]
    # the computed gate where the Reader and the label agree on the beat (both have one, same verb): the gate's own
    # error, apart from the Reader's beat and verb choice
    same = [g for g in lines if g["id"] in by_id and g["labels"]["verb"] and by_id[g["id"]]["verb"] == g["labels"]["verb"]]
    ok = sum(by_id[g["id"]]["gate"] == g["labels"]["gate"] for g in same)
    nobeat = sum(1 for g in lines if g["id"] in by_id and (by_id[g["id"]]["verb"] is None) != (g["labels"]["verb"] is None))
    out += [f"Computed gate where the beat and verb agree: {100 * ok / max(1, len(same)):.1f}% ({ok}/{len(same)}); "
            f"lines where only one side has a beat (SPEECH vs a beat): {nobeat}"]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--cached", action="store_true")
    ap.add_argument("--set", choices=sorted(SETS), default="golden")
    ap.add_argument("--cache", type=Path, help="answers file (default: the set's baseline); a new file is a fresh run")
    args = ap.parse_args(argv)
    path, cache = SETS[args.set]
    cache = args.cache or cache
    lines = rg.load(path)
    answers = load_cache(cache) if args.cached else run(args.model, lines, cache)
    print(report(answers, lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
