"""Compile the rules chapters into rule cards (00.15.2) and the always-loaded core list (00.15.4).

Usage:
  python engine/build/compile_cards.py            # (re)write engine/build/cards.json, print a summary
  python engine/build/compile_cards.py --check    # exit 1 if the rules changed since cards.json was built
Options: --rules DIR (rules root, default rules/), --out FILE (default engine/build/cards.json).

Parsing reuses `rules/tools/rq.py`'s index (its id regexes and card/section spans); rules/ is read-only.
Chapters 00-12 and 14-16 are compiled; ch.13 (the optional example setting) is skipped.

Card kinds: `rule` (numbered rule), `section` (numbered heading; its body is only the text before its
first child), `table` (T-), `procedure` (PR-), `example` (WE-). Tags: the card's own `Loads in:` line
where present; otherwise derived from its anchors' situation tags, its chapter and keywords in its section
and card titles (`tags_derived` is then true). Tag values are `situation.*` ids from data/tags.yaml plus
`core`, `any` (every situation), `creation` and `reflection`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict

REPO = Path(__file__).resolve().parents[2]
RULES = REPO / "rules"
OUT = Path(__file__).resolve().parent / "cards.json"
FORMAT = 1  # bump when the card record changes, so --check forces a rebuild

CHAPTERS = [f"{n:02d}" for n in range(17) if n != 13]  # ch.13 is the optional example setting
DATA_INPUTS = ["data/tags.yaml", "data/anchors.yaml"]

# rule: 00.15.4 the always-loaded core: turn-loop checklist, invariants, gate classes, stakes/reach/levers
CORE_IDS = ["T-12-1", "T-00-1", "00.12.3", "00.3.9", "00.3.14", "00.3.15"]

CardKind = Literal["rule", "section", "table", "procedure", "example"]
PREFIX_KIND: dict[str, CardKind] = {"T-": "table", "PR-": "procedure", "WE-": "example"}
EXTRA_TAGS = ("core", "any", "creation", "reflection")

# Derived tags when a card has no `Loads in:` line.
CHAPTER_TAGS: dict[str, list[str]] = {
    "02": ["creation"],
    "06": ["situation.conflict"],
    "09": ["situation.conflict"],
    "10": ["situation.exploration", "situation.travel"],
}
KEYWORD_TAGS: dict[str, str] = {
    "situation.conflict": r"\b(conflicts?|combat|fight\w*|rounds?|tempo|melee)\b",
    "situation.conflict.chase": r"\b(chases?|pursuit)\b",
    "situation.conflict.skirmish": r"\b(mobs?|skirmish\w*|battles?)\b",
    "situation.conflict.duel": r"\bduels?\b",
    "situation.social": r"\b(social|persua\w*|deception|reputation)\b",
    "situation.social.parley": r"\b(parley|negotiat\w*)\b",
    "situation.social.interrogation": r"\binterrogat\w*",
    "situation.social.bargaining": r"\b(bargain\w*|buying|selling|markets?|hiring)\b",
    "situation.social.court": r"\b(courts?|council)\b",
    "situation.investigation": r"\b(investigat\w*|clues?|myster\w*)\b",
    "situation.investigation.research": r"\b(research|librar\w*)\b",
    "situation.exploration": r"\b(explor\w*|sites?|dungeons?|hazards?|traps?)\b",
    "situation.travel": r"\b(travel\w*|journey\w*|navigat\w*|weather)\b",
    "situation.travel.water": r"\b(vessels?|sailing|boats?)\b",
    "situation.downtime": r"\bdowntime\b",
    "situation.downtime.project": r"\b(craft\w*|projects?)\b",
    "situation.downtime.training": r"\b(training|teach\w*)\b",
    "situation.rest": r"\b(rests?|resting|camp\w*)\b",
}

FIELD_KEYS = {
    "Trigger [T]": "trigger",
    "Loads in": "loads_in",
    "License check": "license_check",
    "Decisions (J)": "decisions",
    "Computation [D]": "computation",
    "Stakes": "stakes",
    "State writes": "state_writes",
    "Narration may not imply": "narration_may_not_imply",
    "Worst case (J)": "worst_case",
    "Examples": "examples",
    "Anchor": "anchor",
    "Basis": "basis",
}
RE_FIELD = re.compile(r"^(" + "|".join(re.escape(k) for k in FIELD_KEYS) + r"):\s*(.*)$")
RE_MARK = re.compile(r"`(\[(?:D|N|T|S|J(?::[a-z_]+)?)\])`")
RE_MARK_RAW = re.compile(r"(\[(?:D|N|T|S|J(?::[a-z_]+)?)\])")
RE_BRACKET = re.compile(r"\[([^\]`]+)\]")
RE_TABLE = re.compile(r"\bT-\d{2}-\d+[a-z]?\b")
RE_WORST = re.compile(r"\*Worst case \(J[^*]*\*:?\s*(.+?)(?:\n\s*\n|\Z)", re.S)


class AnchorRef(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    intent_verbs: list[str] = []
    deed_tags: list[str] = []
    situation_tags: list[str] = []
    knobs: list[dict[str, Any]] = []


class RuleCard(BaseModel):
    """One retrievable card (00.15.2). Fields absent in the source keep their defaults."""

    model_config = ConfigDict(frozen=True)
    id: str
    kind: CardKind
    title: str
    chapter: str
    section: str | None = None
    file: str
    lines: tuple[int, int]
    kinds: list[str] = []
    loads_in: list[str] = []
    tags: list[str] = []
    tags_derived: bool = False
    trigger: str | None = None
    license_check: str | None = None
    decisions: list[str] = []
    computation: str | None = None
    stakes: str | None = None
    state_writes: list[str] = []
    narration_may_not_imply: list[str] = []
    worst_case: str | None = None
    examples: list[str] = []
    anchors: list[AnchorRef] = []
    tables: list[str] = []
    basis: list[str] = []
    tokens: int = 0
    body: str = ""

    @property
    def model_judged(self) -> bool:
        """True when every mark is a judgment or narration ([J*]/[N]) with no code-run part."""
        return bool(self.kinds) and all(k.startswith("[J") or k == "[N]" for k in self.kinds)


class CardIndex:
    """Read access to compiled cards: by id, by situation tag, and the always-loaded core."""

    def __init__(self, cards: list[RuleCard], core_ids: list[str], meta: dict[str, Any]) -> None:
        self._cards = {c.id: c for c in cards}
        self._order = [c.id for c in cards]
        self._core = list(core_ids)
        self.meta = meta

    def __len__(self) -> int:
        return len(self._order)

    def __contains__(self, card_id: object) -> bool:
        return card_id in self._cards

    def __iter__(self):
        return (self._cards[i] for i in self._order)

    def get(self, card_id: str) -> RuleCard:
        return self._cards[card_id]

    # rule: 00.15.4 cards load by situation.* tag; a card tagged with an ancestor (or `any`) also loads
    def by_tag(self, tag: str) -> list[RuleCard]:
        want = {tag, "any"}
        parts = tag.split(".")
        want.update(".".join(parts[:i]) for i in range(2, len(parts)))
        return [c for c in self if want.intersection(c.tags)]

    # rule: 00.15.4
    def core(self) -> list[RuleCard]:
        return [self._cards[i] for i in self._core]


def load_cards(path: Path | None = None) -> CardIndex:
    """Load cards.json (default engine/build/cards.json)."""
    return _load(str(path or OUT))


@lru_cache(maxsize=4)
def _load(path: str) -> CardIndex:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    cards = [RuleCard.model_validate(c) for c in doc["cards"]]
    return CardIndex(cards, doc["core"], doc["meta"])


# ---------------------------------------------------------------- compile


def _rq() -> Any:  # rules/tools/rq.py, loaded by path (rules/ is not a package)
    spec = importlib.util.spec_from_file_location("rq", RULES / "tools" / "rq.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def source_files(rules: Path) -> list[Path]:
    chapters = [p for p in sorted(rules.glob("[0-9][0-9]-*.md")) if p.name[:2] in CHAPTERS]
    return chapters + [rules / d for d in DATA_INPUTS]


def tree_hash(rules: Path) -> tuple[str, dict[str, str]]:
    """sha256 over every compiler input (chapters 00-12, 14-16, tags.yaml, anchors.yaml)."""
    per_file: dict[str, str] = {}
    h = hashlib.sha256(f"format={FORMAT}\n".encode())
    for p in source_files(rules):
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        rel = p.relative_to(rules).as_posix()
        per_file[rel] = digest[:16]
        h.update(f"{rel} {digest}\n".encode())
    return h.hexdigest(), per_file


def _build_index(rules: Path) -> dict[str, tuple[str, str, int, int, str]]:
    rq = _rq()
    saved = rq.ROOT
    rq.ROOT = str(rules)  # rq.py reads its module-level ROOT
    try:
        return rq.build_index()
    finally:
        rq.ROOT = saved


def _kind(card_id: str, rq_kind: str) -> CardKind | None:
    for prefix, kind in PREFIX_KIND.items():
        if card_id.startswith(prefix):
            return kind
    if re.match(r"^\d{2}(\.\d+[a-z]?)+$", card_id):
        return "section" if rq_kind == "heading" else "rule"
    return None  # OEQ rows, FN, DL


def _split_top(text: str, seps: str = ",;") -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in text:
        depth += ch in "([{"
        depth -= ch in ")]}"
        if ch in seps and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [s.strip() for s in out if s.strip() and s.strip().lower() != "none"]


def _fields(body_lines: list[str]) -> dict[str, str]:
    """Template-block fields (00.2.5): label line plus indented continuation lines."""
    fields: dict[str, list[str]] = {}
    key = None
    for line in body_lines:
        m = RE_FIELD.match(line)
        if m:
            key = FIELD_KEYS[m.group(1)]
            fields[key] = [m.group(2).strip()]
        elif key and line.startswith(" ") and line.strip():
            fields[key].append(line.strip())
        else:
            key = None
    return {k: " ".join(v).strip() for k, v in fields.items()}


def _parse_loads_in(text: str, vocab: set[str]) -> list[str]:
    tags: list[str] = []
    for m in re.finditer(r"situation(?:\.[a-z_]+)*(?:\.\*)?", text):
        t = m.group(0).removesuffix(".*")
        while t != "situation" and t not in vocab:
            t = t.rsplit(".", 1)[0]
        tags.append("any" if t == "situation" else t)
    if re.search(r"\bcore\b(?!\s*(\(when|while|at\b))", text):
        tags.append("core")
    if re.search(r"\bevery situation\b", text):
        tags.append("any")
    tags += [w for w in ("creation", "reflection") if re.search(rf"\b{w}\b", text)]
    return list(dict.fromkeys(tags))


def _derive_tags(chapter: str, titles: str, anchors: list[AnchorRef], vocab: set[str]) -> list[str]:
    tags = [t for a in anchors for t in a.situation_tags if t in vocab]
    tags += CHAPTER_TAGS.get(chapter, [])
    tags += [t for t, rx in KEYWORD_TAGS.items() if re.search(rx, titles, re.I)]
    return list(dict.fromkeys(tags))


def _anchor_map(rules: Path) -> dict[str, list[AnchorRef]]:
    doc = yaml.safe_load((rules / "data/anchors.yaml").read_text(encoding="utf-8"))
    out: dict[str, list[AnchorRef]] = {}
    for a in doc.get("anchors", []):
        ref = AnchorRef(
            id=a["id"],
            intent_verbs=a.get("intent_verbs") or [],
            deed_tags=a.get("deed_tags") or [],
            situation_tags=a.get("situation_tags") or [],
            knobs=a.get("knobs") or [],
        )
        out.setdefault(str(a["rule_id"]), []).append(ref)
    return out


def _situation_vocab(rules: Path) -> set[str]:
    doc = yaml.safe_load((rules / "data/tags.yaml").read_text(encoding="utf-8"))
    return {t["id"] for t in doc["tags"] if t["id"].startswith("situation.")}


# rule: 00.15.2 each numbered rule compiles to one card
def compile_cards(rules: Path = RULES) -> dict[str, Any]:
    """Build the cards.json document (meta, core, cards) from the rules tree at `rules`."""
    idx = _build_index(rules)
    anchors = _anchor_map(rules)
    vocab = _situation_vocab(rules)
    texts: dict[str, list[str]] = {}
    entries = [
        (k, v)
        for k, v in idx.items()
        if v[1][:2] in CHAPTERS and v[1][2:3] == "-" and "/" not in v[1] and _kind(k, v[0])
    ]
    # Section spans per file, to find each card's enclosing section and a section's own preamble.
    starts: dict[str, list[int]] = {}
    sections: dict[str, list[tuple[int, int, str, str]]] = {}
    for k, (rq_kind, f, s, e, title) in entries:
        starts.setdefault(f, []).append(s)
        if _kind(k, rq_kind) == "section":
            sections.setdefault(f, []).append((s, e, k, title))
    for f in starts:
        starts[f].sort()

    cards: list[RuleCard] = []
    for k, (rq_kind, f, s, e, title) in sorted(entries, key=lambda kv: (kv[1][1], kv[1][2])):
        kind = _kind(k, rq_kind)
        assert kind is not None
        if f not in texts:
            texts[f] = (rules / f).read_text(encoding="utf-8").split("\n")
        lines = texts[f]
        end = e
        if kind == "section":  # preamble only: child cards carry the rest
            end = min([x - 1 for x in starts[f] if x > s] + [e])
            while end > s and not lines[end - 1].strip():
                end -= 1
        body_lines = lines[s - 1 : end]
        body = "\n".join(body_lines)
        enclosing = [sec for sec in sections.get(f, []) if sec[0] < s <= sec[1] and sec[2] != k]
        section = max(enclosing)[2:] if enclosing else None
        fields = _fields(body_lines)
        head = body_lines[0]
        marks = RE_MARK.findall(head)
        if not marks:  # block form: kinds sit unquoted on the fenced "### <id>  <name>  [kinds]" line
            tpl = next((x for x in body_lines[:4] if x.startswith(f"### {k} ")), "")
            marks = RE_MARK_RAW.findall(tpl)
        marks = list(dict.fromkeys(marks))
        basis = [b.strip() for m in RE_BRACKET.findall(RE_MARK.sub("", head)) for b in m.split(";")]
        if fields.get("basis"):
            basis += RE_BRACKET.findall(fields["basis"])
        my_anchors = anchors.get(k, [])
        declared = "loads_in" in fields
        loads_in = _parse_loads_in(fields["loads_in"], vocab) if declared else []
        titles = f"{section[1] if section else ''} {title}"
        tags = loads_in if declared else _derive_tags(f[:2], titles, my_anchors, vocab)
        worst = fields.get("worst_case")
        if worst is None and (m := RE_WORST.search(body)):
            worst = " ".join(m.group(1).split())[:600]
        decisions = re.split(r"\s(?=\d+\.\s)", fields["decisions"]) if fields.get("decisions") else []
        cards.append(
            RuleCard(
                id=k,
                kind=kind,
                title=re.sub(r"[`*]", "", title).strip().rstrip("."),
                chapter=f[:2],
                section=section[0] if section else None,
                file=f,
                lines=(s, end),
                kinds=marks,
                loads_in=loads_in,
                tags=tags,
                tags_derived=not declared,
                trigger=fields.get("trigger"),
                license_check=fields.get("license_check"),
                decisions=[d.strip() for d in decisions if d.strip()],
                computation=fields.get("computation"),
                stakes=fields.get("stakes"),
                state_writes=_split_top(fields.get("state_writes", "")),
                narration_may_not_imply=_split_top(fields.get("narration_may_not_imply", ""), ";"),
                worst_case=worst,
                examples=[fields["examples"]] if fields.get("examples") else [],
                anchors=my_anchors,
                tables=[t for t in dict.fromkeys(RE_TABLE.findall(body)) if t != k],
                basis=list(dict.fromkeys(b for b in basis if b)),
                tokens=(len(body) + 3) // 4,
                body=body,
            )
        )
    ids = {c.id for c in cards}
    missing_core = [i for i in CORE_IDS if i not in ids]
    if missing_core:
        raise ValueError(f"core ids missing from the rules: {missing_core}")
    digest, per_file = tree_hash(rules)
    meta = {"format": FORMAT, "rules_tree_sha256": digest, "sources": per_file}
    return {"meta": meta, "core": CORE_IDS, "cards": [c.model_dump(exclude_defaults=True) for c in cards]}


def write_cards(doc: dict[str, Any], out: Path = OUT) -> None:
    """One card per line: compact and diff-friendly."""
    head = json.dumps({"meta": doc["meta"], "core": doc["core"]}, ensure_ascii=False)[:-1]
    rows = ",\n".join(json.dumps(c, ensure_ascii=False, separators=(",", ":")) for c in doc["cards"])
    out.write_text(f'{head},\n"cards":[\n{rows}\n]}}\n', encoding="utf-8")
    _load.cache_clear()


def is_stale(rules: Path = RULES, out: Path = OUT) -> bool:
    """True when cards.json is missing or was built from a different rules tree (or card format)."""
    if not out.exists():
        return True
    meta = json.loads(out.read_text(encoding="utf-8"))["meta"]
    return meta.get("format") != FORMAT or meta.get("rules_tree_sha256") != tree_hash(rules)[0]


def summary(doc: dict[str, Any], out: Path) -> str:
    cards = doc["cards"]
    kinds = Counter(c["kind"] for c in cards)
    rules = [c for c in cards if c["kind"] == "rule"]
    declared = sum(1 for c in rules if not c.get("tags_derived"))
    untagged = sum(1 for c in rules if not c.get("tags"))
    anchored = sum(1 for c in cards if c.get("anchors"))
    size = out.stat().st_size if out.exists() else 0
    return (
        f"cards: {len(cards)} ({', '.join(f'{k} {n}' for k, n in sorted(kinds.items()))})\n"
        f"rules: {declared} with Loads in, {len(rules) - declared - untagged} derived tags, "
        f"{untagged} untagged; {anchored} cards with anchors; core {len(doc['core'])}\n"
        f"tokens: {sum(c.get('tokens', 0) for c in cards)}; {out} {size / 1e6:.2f} MB; "
        f"tree {doc['meta']['rules_tree_sha256'][:16]}"
    )


def main(argv: list[str]) -> int:
    rules, out = RULES, OUT
    if "--rules" in argv:
        rules = Path(argv[argv.index("--rules") + 1])
    if "--out" in argv:
        out = Path(argv[argv.index("--out") + 1])
    if "--check" in argv:
        if is_stale(rules, out):
            print(f"STALE: {out} does not match the rules tree; run engine/build/compile_cards.py")
            return 1
        print(f"ok: {out} matches the rules tree")
        return 0
    doc = compile_cards(rules)
    write_cards(doc, out)
    print(summary(doc, out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
