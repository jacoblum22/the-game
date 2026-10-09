"""Replay-bench plugs for the narration contract (spec 006; spec 019's passage): recorded first-draft packets in
today's contract.

    py -3.12 evals/replay_bench.py run --narrator evals.narration_plug:haiku --judge evals.narration_plug:judge \
        --limit 80 --workers 4
    py -3.12 evals/replay_bench.py run --narrator evals.narration_plug:offline --judge evals.narration_plug:judge

Each recorded packet (spec 005's corpus) is rebuilt in the new contract: its record lines get handles (`R1`, …,
must-name by kind, the beat's costs, harm, conditions, positions and delivered items split into lines of their
own, 12.14.12), the instructions are today's narrator prompt, and the schema's enums come from the packet (record
handles; the view's people as speakers). The narrator plug then runs the turn's narration loop against the
packet: the first draft (one passage and its side list), the passage judge (engine.audit.declare: 12.3.1a scans,
tiers, coverage, the quote-mark check), and at most one revision that sees the whole draft (12.3.3), counting calls,
revisions, cuts and rendered lines.

What the replay cannot judge: the store. Support is the packet's (DL-12-42); a contradiction with a stored value,
an Oracle answer and the Checker's verdicts need the game's state, which the corpus does not hold. With `audit`
on, the Checker (same model) reads each first draft so undeclared assertions can be counted like spec 005's
baseline (unknown-subject claims no new element in the side list covers).
"""

from __future__ import annotations

import json
import os
import re
import sys
import threading
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.audit import text as tx  # noqa: E402
from engine.audit.claims import beat_polarity, passage_beat  # noqa: E402
from engine.audit.declare import (  # noqa: E402
    Passage,
    SceneIndex,
    Sentence,
    coverage,
    known_as,
    parse_output,
    scan_sentence,
    sentences_of,
    t2_delivered,
    tier_of,
    unquoted,
    voices,
)
from engine.dm.adjudication import BeatEntry  # noqa: E402
from engine.dm.handles import MUST_NOTES  # noqa: E402
from engine.dm.roles.narrator import Revision, revision_text  # noqa: E402
from engine.dm.roles.prompts import load_prompt  # noqa: E402
from engine.dm.schemas import SchemaContext, checker_schema, narrator_schema  # noqa: E402

HAIKU = "haiku"
_LOCK = threading.Lock()
MAX_REVISIONS = 1
AUDIT = True
_HEADER = "ADJUDICATION RECORD"
_GUIDE = ("- part [", "- whoever answers", "- the character ", "- the turn stops at a pause", "- end by handing",
          "- the scene ends here", "- the engine shows a lethal warning")
_SUB = {"cost paid": "cost", "harm to": "harm", "visible conditions": "condition", "position": "position",
        "the PC learns": "learned"}


def _rules() -> Any:
    from engine.data.loader import load_rules

    return load_rules()


# ------------------------------------------------------------------------------------------- the packet


def _bits(line: str) -> list[str]:
    """A beat line's '; '-joined bits; a piece with no 'key: ' continues the bit before it."""
    out: list[str] = []
    for piece in line.split("; "):
        if out and not re.match(r"^[A-Za-z][\w ()]*?: |^[a-z]+ [a-z ]+ [A-Z]", piece) and not piece.startswith(
                ("not resolved yet", "no roll", "acting on")):
            out[-1] += "; " + piece
        else:
            out.append(piece)
    return out


def _entities(view: str) -> dict[str, str]:
    """{id: name} from the view's top-level `<id>: <name>` lines."""
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"(?m)^([a-z]+\.[\w.]+): (.+)$", view)}


def _ids_named(text: str, names: dict[str, str]) -> list[str]:
    low = text.lower()
    return [i for i, n in names.items() if n and n.lower() in low]


class Packet:
    """One recorded packet in the new contract."""

    def __init__(self, item: dict[str, Any]) -> None:
        self.item = item
        self.view = item.get("NARRATOR VIEW", "")
        self.names = _entities(self.view)
        self.items: list[dict[str, Any]] = []  # {handle, kind, must, words, entities, degree, gate_words}
        msg = item.get("THIS MESSAGE", "")
        head, _, rest = msg.partition(_HEADER)
        rest = rest.split("\n", 1)[1] if "\n" in rest else ""
        lines = rest.split("\n")
        record, tail = [], []
        for i, ln in enumerate(lines):
            if ln.startswith("- "):
                record.append(ln)
            else:
                tail = lines[i:]
                break
        out = []
        for ln in record:
            out += self._convert(ln)
        self.message = (head + _HEADER + " (narrate exactly this, no better and no worse; list each line you narrate "
                        "by its handle in `covers`; narrate every line marked MUST):\n"
                        + "\n".join(out) + ("\n" + "\n".join(tail) if tail else ""))
        self.player = (re.search(r'THE PLAYER\'S MESSAGE: "(.*)"', msg) or [None, ""])[1]
        self.facts = {m.group(1): m.group(2) for m in re.finditer(r"(?m)^\s*(fact\.\d+) about (.+)$", self.view)}

    def _add(self, kind: str, must: bool, words: str, **kw: Any) -> str:
        h = f"R{len(self.items) + 1}"
        self.items.append({"handle": h, "kind": kind, "must": must, "words": words, **kw})
        return f"- {h}{' MUST' if must else ''}: {words}"

    def _convert(self, ln: str) -> list[str]:
        if ln.startswith(_GUIDE):
            return [ln]
        body = ln[2:]
        if body.startswith("beat:"):
            keep, subs = [], []
            for b in _bits(body):
                key = next((k for k in _SUB if b.startswith(k)), None)
                if key is None:
                    keep.append(b)
                elif key in ("visible conditions", "the PC learns"):
                    subs += [(_SUB[key], x) for x in b.split(": ", 1)[1].split("; ") if x]
                else:
                    subs.append((_SUB[key], b))
            beat = "; ".join(keep)
            degree = (re.search(r"result: ([a-z_ ]+)", beat) or [None, None])[1]
            degree = {"critical success": "critical_success", "critical failure": "critical_failure",
                      "success at cost": "success"}.get((degree or "").split(" (")[0].strip(), (degree or "").split(" (")[0].strip() or None)
            no_roll = "no roll" in beat
            owed = bool(degree) or no_roll or ("not done" not in beat and "not resolved yet" not in beat)
            acting = re.search(r"acting on: ([^;]+)", beat)
            ents = _ids_named(acting.group(1), self.names) if acting else []
            out = [self._add("beat", owed, beat, entities=ents, degree=degree,
                             gate_words="no roll" if no_roll and not degree else "")]
            for kind, words in subs:
                words = f"the PC learns: {words}" if kind == "learned" else words
                out.append(self._add(kind, True, words, entities=_ids_named(words, self.names)))
            return out
        if body.startswith("question "):
            return [self._add("oracle", True, body)]
        if " acts: " in body:
            who = body.split(" acts: ", 1)[0]
            return [self._add("npc", True, body, entities=_ids_named(who, self.names))]
        if body.startswith("an omen"):
            return [self._add("omen", True, body)]
        if body.startswith("note: "):
            note = body[6:]
            return [self._add("note", note.startswith(MUST_NOTES), body)]
        if body.startswith("a new scene opens"):
            return [self._add("scene", False, body)]
        return [ln]

    @property
    def handles(self) -> list[str]:
        return [x["handle"] for x in self.items]

    @property
    def must(self) -> list[str]:
        return [x["handle"] for x in self.items if x["must"]]

    def ctx(self) -> SchemaContext:
        rules = _rules()
        return SchemaContext(scene_ids=list(self.names), narrator_refs=self.handles,
                             speaker_ids=[i for i in self.names if not i.startswith("pc.")],
                             element_kinds=list(rules.pacing["claim_check"]["element_tiers"]))

    def render(self, message: str | None = None) -> str:
        order = ["CORE RULES", "RULE CARDS", "NARRATOR VIEW", "RECENT EXCHANGES"]
        parts = [f"[{k}]\n{self.item[k]}" for k in order if self.item.get(k) is not None]
        parts.append(f"[THIS MESSAGE]\n{message if message is not None else self.message}")
        return "\n\n".join(parts)

    def index(self) -> SceneIndex:
        """12.3.1a's comparison set, from the packet: names, pronouns, counts, facts, the record's lines."""
        aliases: dict[str, list[str]] = {}
        pronouns: dict[str, str] = {}
        numbers: dict[str, list[int]] = {}
        blocks = re.split(r"(?m)^(?=[a-z]+\.[\w.]+: )", self.view)
        for b in blocks:
            m = re.match(r"([a-z]+\.[\w.]+): (.+)", b)
            if not m:
                continue
            eid, name = m.group(1), m.group(2).strip()
            names = [name, *(name.split()[:1] if len(name.split()) > 1 else [])]
            role = re.search(r"(?m)^  role: (.+)$", b)
            if role:
                names.append(role.group(1).split(" of ")[0].strip())
            aliases[eid] = [n.lower() for n in names if n and len(n) > 2]
            pr = re.search(r"(?m)^  pronouns: (\w+)", b)
            if pr:
                pronouns[eid] = {"she": "f", "he": "m", "they": "x"}.get(pr.group(1), "x")
            q = re.search(r"(?m)^  quantities: (.+)$", b)
            if q:
                numbers[eid] = [int(x) for x in re.findall(r"\b(\d+)\b", q.group(1))]
        # the people SCENE SETTING says are present (the old view's budget dropped some of them): names to scan
        for n, m in enumerate(re.finditer(r"(?m)^- present: ([^,(\n]+)", self.message)):
            name = m.group(1).strip()
            if not any(name.lower() in a for a in aliases.values()):
                aliases[f"present.{n}"] = [x.lower() for x in (name, name.split()[0]) if len(x) > 2]
        everything = " ".join(str(v) for k, v in self.item.items() if not k.startswith("_")) + self.message
        known = set(re.findall(r"\b[A-Z][\w'-]+", everything))
        return SceneIndex(pc=next((i for i in aliases if i.startswith("pc.")), None), aliases=aliases,
                          pronouns=pronouns, numbers=numbers, facts=self.facts,
                          fact_subject={f: v.split(":", 1)[0].strip() for f, v in self.facts.items()},
                          handles={x["handle"]: x["words"] for x in self.items},
                          handle_entities={x["handle"]: x.get("entities", []) for x in self.items},
                          known_words=known)


# ------------------------------------------------------------------------------------------- judging


def judge_sentence(p: Packet, idx: SceneIndex, s: Sentence, beat: BeatEntry | None) -> dict[str, Any]:
    # rule: 12.3.1a
    """One sentence of a passage in packet mode: scans, tiers, plain result words. Returns {ok, fix, why, ...}."""
    rules = _rules()
    known = {el.name: known_as(el, idx) for el in s.new}
    s.about += [k for k in known.values() if k]
    s.new = [el for el in s.new if not known[el.name]]  # one of the scene's own, spoken of: not new
    scan = scan_sentence(s, idx, rules=rules, names=list(p.names.values()))
    fails = [(f.fix, f.why) for f in scan.failures]
    for el in s.new:
        if tier_of(el, rules) == "T2" and not t2_delivered(el, s, idx):
            fails.append(("cut", f"a new {el.element_kind} no record line delivers"))
    deg = beat_polarity(voices(s)[0], beat) if beat is not None else None
    cut = any(f == "cut" for f, _ in fails)
    return {"text": s.text, "ok": not fails, "fix": "cut" if cut else ("redraft" if fails else None),
            "why": [w for _, w in fails], "cls": fails[0][1].split(" (")[0] if fails else None,
            "outcome_words": deg, "undeclared_new": scan.undeclared_new, "added_about": len(scan.added_about)}


def judge_passage(p: Packet, idx: SceneIndex, passage: Passage) -> tuple[list[Sentence], list[dict[str, Any]],
                                                                         list[str], list[str]]:  # rule: PR-12-2
    """The passage judge in packet mode: (sentences, their checks, uncovered must-name handles, unquoted words).
    Plain result words are logged, never failed (measured 1 real of 10; pacing.yaml outcome_words)."""
    sents, _ = sentences_of(passage)
    beat = passage_beat([BeatEntry(restatement="", degree=x.get("degree"), gate_words=x.get("gate_words", ""))
                         for x in p.items if x["kind"] == "beat"])
    return sents, [judge_sentence(p, idx, s, beat) for s in sents], coverage(passage, p.must), unquoted(passage)


def _audit(p: Packet, passage: Passage, sents: list[Sentence], model: str) -> dict[str, int]:
    """The Checker on the first draft (12.3.1 source 2): claims on subjects the side list and names do not cover."""
    from evals.playtest import ask_claude

    rules = _rules()
    ctx = SchemaContext(scene_ids=list(p.names), claim_classes=list(rules.pacing["claim_check"]["classes"]),
                        sentence_ids=[str(i) for i in range(len(sents))])
    view = "\n".join(f"{i}: {n}" for i, n in p.names.items())
    msg = "\n".join(f"[{i}] {s.text}" for i, s in enumerate(sents)) + f'\n\nTHE PLAYER\'S MESSAGE: "{p.player}"'
    data, _ = ask_claude(load_prompt("checker"), f"[ENTITIES]\n{view}\n\n[THIS MESSAGE]\n{msg}",
                         checker_schema(ctx), model)
    unknown = undeclared = 0
    idx = p.index()
    for c in data.get("claims") or []:
        try:
            s = sents[int(c.get("sentence", 0))]
        except (ValueError, IndexError):
            continue
        if c.get("subject") == "unknown":
            text = f"{c.get('predicate', '')} {c.get('value', '')}"
            if not any(tx.overlap(text, el.name) for el in passage.new):
                unknown += 1
        elif c.get("subject") not in idx.subjects(s) and c.get("subject") != idx.pc:
            undeclared += 1
    return {"audit_unknown_new": unknown, "audit_undeclared_subject": undeclared}


# ------------------------------------------------------------------------------------------- narrators


def _failed(sents: list[Sentence], checks: list[dict[str, Any]], missing: list[str], quote: list[str]) -> list[str]:
    """What the one revision is told (engine.dm.narration._Draft.failed's words)."""
    out = []
    if any(c["fix"] == "redraft" for c in checks):
        for s, c in zip(sents, checks, strict=True):
            out += [f'remove "{s.text}": {w}' if c["fix"] == "cut" else f'"{s.text}": {w}' for w in c["why"]]
    out += [f"not narrated: {h} (narrate it and list it in `covers`)" for h in missing]
    out += [f'speech outside quote marks: "{w}" (put the spoken words inside quote marks)' for w in quote]
    return out


def _run(item: dict[str, Any], call: Any, audit: Any = None) -> dict[str, Any]:
    """The narration loop on one packet: draft, judge the passage, at most one revision, then cut and render."""
    p = Packet(item)
    instructions = load_prompt("narrator")
    data = call(instructions, p.render(), narrator_schema(p.ctx()))
    calls = 1
    passage = parse_output(data)
    idx = p.index()
    sents, first, missing0, quote0 = judge_passage(p, idx, passage)
    result: dict[str, Any] = {"fiction": passage.text, "mentions": [], "_first": first, "_missing_first": missing0,
                              "_unquoted_first": quote0, "_side_list": passage.model_dump(exclude={"text"}),
                              "_declared_new": len(passage.new)}
    if audit is not None:
        result["_audit"] = audit(p, passage, sents)
    checks, missing, quote = first, missing0, quote0
    revised = False
    failed = _failed(sents, checks, missing, quote)
    if failed and MAX_REVISIONS:
        rev = Revision(draft=passage.text, failed=failed)
        data = call(instructions, p.render(p.message + "\n" + revision_text(rev)), narrator_schema(p.ctx()))
        calls += 1
        revised = True
        if str(data.get("passage") or "").strip():
            passage = parse_output(data)
            sents, checks, missing, quote = judge_passage(p, idx, passage)
            result["_revision"] = passage.text
    kept = [s for s, c in zip(sents, checks, strict=True) if c["ok"]]
    result.update(_calls=calls, _cut=len(kept) < len(sents), _rendered=bool(missing), _revised=revised,
                  _quoted_by_code=len(quote), _first_pass=not failed, _rounds=int(revised),
                  _turn=f"{item['_recorded']['save']}/{item['_recorded']['turn']}",
                  _final=" ".join(s.text for s in kept))
    dump = os.environ.get("NARRATION_PLUG_DUMP")
    if dump:  # per-packet detail, for reading what drives a miss
        with _LOCK, open(dump, "a", encoding="utf-8") as f:
            f.write(json.dumps({k: v for k, v in result.items()}, default=str) + "\n")
    return result


def haiku(item: dict[str, Any]) -> dict[str, Any]:
    from evals.playtest import ask_claude

    def call(system: str, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        return ask_claude(system, prompt, schema, HAIKU)[0]
    return _run(item, call, (lambda p, ps, s: _audit(p, ps, s, HAIKU)) if AUDIT else None)


def offline(item: dict[str, Any]) -> dict[str, Any]:
    """The free offline narrator, for a smoke of the plug path (it cites every line it renders)."""
    from engine.llm.base import Packet as LlmPacket
    from engine.llm.offline import OfflineModel, conform

    def call(system: str, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        msg = prompt.split("[THIS MESSAGE]\n", 1)[1]
        view = prompt.split("[NARRATOR VIEW]\n", 1)[1].split("\n\n[", 1)[0] if "[NARRATOR VIEW]" in prompt else ""
        return conform(OfflineModel().propose(_role(), schema, LlmPacket(message=msg, view=view)), schema, schema)
    return _run(item, call)


def _role() -> Any:
    from engine.llm.base import Role

    return Role.NARRATOR


def judge(item: dict[str, Any], draft: dict[str, Any]) -> list[dict[str, Any]]:  # noqa: ARG001
    """The first draft's per-sentence checks (computed by the narrator plug, which needs them to revise)."""
    return draft.get("_first") or []
