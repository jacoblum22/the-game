"""RC-DATA: load every `rules/data/*.yaml` once into read-only structures keyed by id (T006).

    rules = load_rules()                 # cached per process (lru_cache) and on disk (pickle keyed by rules_hash)
    rules.condition("cond.prone")        # one entry, by id (KeyError -> RulesDataError on an unknown id)
    rules.conditions                     # {id: entry} for the whole collection (main list + owner-blocks)
    rules.resolution["dc_tiers"]         # a whole file as a read-only mapping
    rules.get("tbl.npc_action")          # any id defined in data, whatever file defines it

Entries are `FrozenDict` / tuples: plain JSON-shaped data that cannot be mutated. The YAML files are the schema
(rules/data/SCHEMAS.md); this module checks the cross-references the engine relies on and fails loudly
(`RulesDataError`) on any that do not resolve. The ruleset's own validator
(`rules/_process/validate_ruleset.py`) remains the authority for prose-level references.
"""

from __future__ import annotations

import functools
import hashlib
import os
import pickle
import re
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, NoReturn

import yaml

REPO = Path(__file__).resolve().parents[2]
RULES_ROOT = REPO / "rules"
CACHE_DIR = Path(os.environ.get("THE_GAME_RULES_CACHE", Path(__file__).resolve().parent / "_cache"))
CACHE_FORMAT = 1

# Files that do not parse in the current rules tree and that no Milestone-1 code reads. Each is reported, not
# loaded: `rules.doc(name)` raises for it. Remove an entry once the file is fixed in rules/ (the test
# `test_known_defects_still_broken` fails when one parses again).
KNOWN_DEFECTS: Mapping[str, str] = {}  # e.g. {"world_turn.yaml": "line 1543: unquoted ': ' (owner 11, M6)"}

FACETS = ("deed", "conduct", "creature", "harm", "material", "item", "terrain", "situation", "trait", "org")
LIFECYCLES = ("provisional", "permanent", "retired")
_ID = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)+$|^veh\.V\d+$")
_KEY_ID = re.compile(r"^[a-z_]+\.[a-z0-9_.]+$")
_TAG_FIELDS = ("tags", "deed_tags", "situation_tags", "gate_tags", "excluded_tags", "key_tags", "terrain_tags")


class RulesDataError(ValueError):
    """The rules data is broken: a file does not parse, an id is unknown, or a cross-reference fails."""


# ------------------------------------------------------------------------------------------- read-only data


class FrozenDict(dict[str, Any]):
    """A dict that refuses mutation. Still a dict, so json.dumps and isinstance(x, dict) work."""

    def _ro(self, *_: object, **__: object) -> NoReturn:
        raise TypeError("rules data is read-only")

    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = _ro  # type: ignore[assignment]

    def __ior__(self, other: object) -> NoReturn:  # type: ignore[override]
        self._ro()

    def __reduce__(self) -> tuple[Any, ...]:
        return (FrozenDict, (dict(self),))

    def __hash__(self) -> int:  # type: ignore[override]
        return id(self)


def freeze(x: Any) -> Any:
    if isinstance(x, dict):
        return FrozenDict({(k if isinstance(k, str) else k): freeze(v) for k, v in x.items()})
    if isinstance(x, list):
        return tuple(freeze(v) for v in x)
    return x


# ------------------------------------------------------------------------------------------- hashing


def rules_files(root: Path) -> list[Path]:
    """What the rules hash covers: the chapter files, rules/README.md, and data/ (YAML plus SCHEMAS.md)."""
    data = root / "data"
    return sorted(root.glob("*.md")) + sorted(data.glob("*.yaml")) + [data / "SCHEMAS.md"]


def rules_hash(root: Path | None = None) -> str:
    """sha256 of the rules tree (rules_files). Stamped on every save by `game_created` (FR-040)."""
    root = root or RULES_ROOT
    h = hashlib.sha256()
    for p in rules_files(root):
        if p.exists():
            h.update(f"{p.relative_to(root).as_posix()}\n".encode())
            h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


# ------------------------------------------------------------------------------------------- the Rules object


class Rules:
    """Read-only view of rules/data. Build it with `load_rules()`; never construct one per call."""

    def __init__(self, root: Path, digest: str, docs: Mapping[str, Any], broken: Mapping[str, str]) -> None:
        self.root = root
        self.hash = digest
        self._docs = docs  # file stem -> frozen document
        self.broken = dict(broken)  # file name -> parse error, for KNOWN_DEFECTS only
        self._index: dict[str, tuple[str, Any]] = {}  # id -> (where, entry)
        self._collections: dict[tuple[str, str], FrozenDict] = {}
        self._build_index()

    # -- whole files
    def doc(self, name: str) -> Any:
        """A whole data file by stem ('resolution') or file name ('resolution.yaml')."""
        stem = name.removesuffix(".yaml")
        if stem in self._docs:
            return self._docs[stem]
        if f"{stem}.yaml" in self.broken:
            raise RulesDataError(f"{stem}.yaml did not load: {self.broken[stem + '.yaml']}")
        raise RulesDataError(f"no data file {stem}.yaml")

    @property
    def files(self) -> list[str]:
        return sorted(f"{s}.yaml" for s in self._docs)

    resolution = property(lambda self: self.doc("resolution"))
    harm = property(lambda self: self.doc("harm"))
    world_seed = property(lambda self: self.doc("world_seed"))
    gen_birth = property(lambda self: self.doc("gen_birth"))
    pacing = property(lambda self: self.doc("pacing"))
    social = property(lambda self: self.doc("social"))
    scales = property(lambda self: self.doc("scales"))
    substrate = property(lambda self: self.doc("substrate"))
    boundaries = property(lambda self: self.doc("boundaries"))
    last_chance = property(lambda self: self.doc("last_chance"))

    # -- collections ({id: entry}, main list plus owner-blocks)
    def collection(self, file: str, key: str) -> FrozenDict:
        """{id: entry} for `file`'s list under `key`, merged with its owner-blocks' entries."""
        ck = (file, key)
        if ck not in self._collections:
            doc = self.doc(file)
            out: dict[str, Any] = {}
            for e in doc.get(key, ()) or ():
                out[e["id"]] = e
            if key == _MAIN_KEY.get(file):
                for blk in doc.get("blocks", ()) or ():
                    for e in blk.get("entries", ()) or ():
                        out[e["id"]] = e
            self._collections[ck] = FrozenDict(out)
        return self._collections[ck]

    oracles = property(lambda self: self.collection("oracles", "tables"))
    origins = property(lambda self: self.collection("origins", "origins"))
    kits = property(lambda self: self.collection("kits", "kits"))
    licenses = property(lambda self: self.collection("licenses", "licenses"))
    abilities = property(lambda self: self.collection("abilities", "abilities"))
    conditions = property(lambda self: self.collection("conditions", "conditions"))
    basic_verbs = property(lambda self: self.collection("basic_verbs", "verbs"))
    attributes = property(lambda self: FrozenDict({a["id"]: a for a in self.doc("attributes")["attributes"]}))
    archetypes = property(lambda self: self.collection("archetypes", "archetypes"))
    adversaries = property(lambda self: self.collection("adversaries", "adversaries"))
    anchors = property(lambda self: self.collection("anchors", "anchors"))
    effects = property(lambda self: self.collection("effects", "core"))
    tags = property(lambda self: FrozenDict({t["id"]: t for t in self.doc("tags")["tags"]}))

    # -- single entries
    def get(self, id_: str) -> Any:
        """Any id defined in data (entries of every file's collections, and id-shaped mapping keys)."""
        try:
            return self._index[id_][1]
        except KeyError:
            raise RulesDataError(f"unknown id {id_!r}") from None

    def has(self, id_: str) -> bool:
        return id_ in self._index

    def where(self, id_: str) -> str:
        """'file.yaml:collection' that defines `id_`."""
        self.get(id_)
        return self._index[id_][0]

    def ids(self, prefix: str) -> list[str]:
        """Every data id with this prefix ('cond' or 'cond.'), sorted."""
        p = prefix.rstrip(".") + "."
        return sorted(i for i in self._index if i.startswith(p))

    def _one(self, coll: Mapping[str, Any], id_: str, what: str) -> Any:
        try:
            return coll[id_]
        except KeyError:
            raise RulesDataError(f"unknown {what} id {id_!r}") from None

    def anchor(self, id_: str) -> Any:
        """An anchor card by `anc.*` id."""
        return self._one(self.anchors, id_, "anchor")

    def anchors_for_rule(self, rule_id: str) -> list[Any]:
        return [a for a in self.anchors.values() if a["rule_id"] == rule_id]

    def table(self, id_: str) -> Any:
        """A `tbl.*` table from any file (oracles.yaml, world_seed.yaml, weather.yaml, ...)."""
        if not id_.startswith("tbl."):
            raise RulesDataError(f"not a table id: {id_!r}")
        return self.get(id_)

    def condition(self, id_: str) -> Any:
        return self._one(self.conditions, id_, "condition")

    def license(self, id_: str) -> Any:
        return self._one(self.licenses, id_, "license")

    def ability(self, id_: str) -> Any:
        return self._one(self.abilities, id_, "ability")

    def origin(self, id_: str) -> Any:
        return self._one(self.origins, id_, "origin")

    def kit(self, id_: str) -> Any:
        return self._one(self.kits, id_, "kit")

    def verb(self, id_: str) -> Any:
        return self._one(self.basic_verbs, id_, "verb")

    def attribute(self, id_: str) -> Any:
        return self._one(self.attributes, id_, "attribute")

    def archetype(self, id_: str) -> Any:
        return self._one(self.archetypes, id_, "archetype")

    def adversary(self, id_: str) -> Any:
        return self._one(self.adversaries, id_, "adversary")

    def effect(self, id_: str) -> Any:
        if not id_.startswith("eff."):
            raise RulesDataError(f"not an effect id: {id_!r}")
        return self.get(id_)

    def boundary_handlers(self) -> list[Any]:
        """Every handler of boundaries.yaml in owner order, each with its block's `owner` added."""
        out = []
        for blk in self.boundaries.get("blocks", ()):
            for h in blk.get("handlers", ()):
                out.append(FrozenDict({**h, "owner": blk["owner"]}))
        return out

    def severity_units(self) -> dict[str, int]:
        """U(severity) per 00.3.11 from scales.yaml: {'S1': 1, ..., 'S5': 4}."""  # rule: 00.8.2
        return {s["id"]: int(s["units"]) for s in self.scales["severity"]}

    # -- index
    def _build_index(self) -> None:
        for stem, doc in self._docs.items():
            if stem == "tags" or not isinstance(doc, Mapping):
                continue
            for where, entry in _entries(stem, doc):
                i = entry.get("id")
                if not isinstance(i, str) or "." not in i or "mirror_of" in entry:
                    continue
                prev = self._index.get(i)
                # a generator pool entry naming content defined elsewhere is a reference, not a definition
                if prev is not None and where.endswith(":pool") and stem.startswith("gen_"):
                    continue
                if prev is None or (prev[0].endswith(":pool") and prev[0].startswith("gen_")):
                    self._index[i] = (where, entry)
            for k, v in doc.items():  # ids defined as mapping keys (e.g. factions.yaml tbl.11.*)
                if isinstance(k, str) and _KEY_ID.match(k) and k.split(".")[0] not in FACETS:
                    self._index.setdefault(k, (f"{stem}.yaml:{k}", v))


_MAIN_KEY = {
    "oracles": "tables", "origins": "origins", "kits": "kits", "licenses": "licenses", "abilities": "abilities",
    "conditions": "conditions", "basic_verbs": "verbs", "archetypes": "archetypes", "adversaries": "adversaries",
    "anchors": "anchors", "effects": "core",
}


def _entries(stem: str, doc: Mapping[str, Any]) -> Iterator[tuple[str, Any]]:
    """(where, entry) for each entry of a file's main collections: lists under a top-level key or one level down,
    owner-block entries/handlers, and top-level mappings with an id. A region's `region` record is not one."""
    for k, v in doc.items():
        if k == "blocks" and isinstance(v, (list, tuple)):
            for blk in v:
                for e in (blk.get("entries") or blk.get("handlers") or ()):
                    if isinstance(e, Mapping):
                        yield f"{stem}.yaml:blocks/{blk.get('owner')}", e
        elif isinstance(v, (list, tuple)):
            for e in v:
                if isinstance(e, Mapping):
                    yield f"{stem}.yaml:{k}", e
        elif isinstance(v, Mapping):
            if isinstance(v.get("id"), str) and not (stem.startswith("region_") and k == "region"):
                yield f"{stem}.yaml:{k}", v
            for k2, v2 in v.items():
                if isinstance(v2, (list, tuple)):
                    for e in v2:
                        if isinstance(e, Mapping):
                            yield f"{stem}.yaml:{k}/{k2}", e


# ------------------------------------------------------------------------------------------- validation


def validate(rules: Rules) -> list[str]:
    """Every problem with the data, as one line each. Empty when the data is sound. Checks (SCHEMAS.md):
    envelope, id spelling and uniqueness, lifecycle and superseded_by, tag references, effect references,
    conditions (reserved ids, stacking, category, severity, escalation, neutralizes), handlers (boundary, phase,
    before), anchors (verb, tags), origins (licenses), adversaries (archetype, abilities), table dice."""
    errs: list[str] = []
    docs = rules._docs  # noqa: SLF001
    tags = set(rules.tags) | set(FACETS)

    for stem, doc in docs.items():
        if not isinstance(doc, Mapping) or not isinstance(doc.get("schema_version"), int):
            errs.append(f"{stem}.yaml: missing integer schema_version")

    # ids: spelling, primary uniqueness, lifecycle
    seen: dict[str, str] = {}
    for stem, doc in docs.items():
        if stem == "tags" or not isinstance(doc, Mapping):
            continue
        for where, e in _entries(stem, doc):
            i = e.get("id")
            if not isinstance(i, str) or "." not in i or "mirror_of" in e:
                continue
            if "<" not in i and not _ID.match(i):
                errs.append(f"{where}: id {i!r} is not snake_case dot segments (00.16.1)")
            pool_ref = stem.startswith("gen_") and where.endswith(":pool")
            if i in seen and not pool_ref and not seen[i].endswith(":pool"):
                errs.append(f"{where}: id {i} also defined in {seen[i]}")
            seen.setdefault(i, where)
            lc = e.get("lifecycle")
            if lc is not None and lc not in LIFECYCLES:
                errs.append(f"{where}: {i} lifecycle {lc!r}")
            sup = e.get("superseded_by")
            if isinstance(sup, str) and not rules.has(sup):
                errs.append(f"{where}: {i} superseded_by {sup} does not resolve")

    # tag and effect references anywhere
    def walk(x: Any, path: str) -> None:
        if isinstance(x, Mapping):
            for k, v in x.items():
                if k in _TAG_FIELDS and isinstance(v, (list, tuple)):
                    for t in v:
                        if isinstance(t, str) and t.split(".")[0] in FACETS and t not in tags:
                            errs.append(f"{path}/{k}: unknown tag {t}")
                if k == "effect_id" and isinstance(v, str) and not v.startswith("<") and not rules.has(v):
                    errs.append(f"{path}: unknown effect {v}")
                walk(v, f"{path}/{k}")
        elif isinstance(x, (list, tuple)):
            for n, v in enumerate(x):
                walk(v, f"{path}[{n}]")

    for stem, doc in docs.items():
        if stem != "tags":
            walk(doc, f"{stem}.yaml")

    errs += _check_conditions(rules)
    errs += _check_handlers(rules)
    errs += _check_refs(rules)
    return errs


def _check_conditions(rules: Rules) -> list[str]:
    errs: list[str] = []
    sub = rules.substrate
    stacking = {s["id"] for s in sub["condition_stacking"]}
    cats = {c if isinstance(c, str) else c["id"] for c in sub["condition_categories"]}
    sev = {s["id"] for s in rules.scales["severity"]}
    conds = rules.conditions
    for rid in sub["reserved_ids"]["conditions"]:
        if rid not in conds:
            errs.append(f"conditions.yaml: reserved condition {rid} is not defined (00.9.4)")
    for cid, c in conds.items():
        if c["stacking"] not in stacking:
            errs.append(f"{cid}: stacking {c['stacking']!r} not in substrate.condition_stacking")
        if c["category"] not in cats:
            errs.append(f"{cid}: category {c['category']!r} not in substrate.condition_categories")
        if c["severity"] not in sev:
            errs.append(f"{cid}: severity {c['severity']!r}")
        esc = c.get("escalates_to")
        if c["stacking"] == "escalate" and not (esc and esc.get("condition") in conds):
            errs.append(f"{cid}: escalate without a resolvable escalates_to")
        for n in c.get("neutralizes") or ():
            if n not in conds:
                errs.append(f"{cid}: neutralizes unknown {n}")
    return errs


def _check_handlers(rules: Rules) -> list[str]:
    errs: list[str] = []
    b = rules.boundaries
    bounds = set(b["boundaries"]["time"]) | set(b["boundaries"]["event"]) | {"*"}
    hs = {h["id"]: h for h in rules.boundary_handlers()}
    if len(hs) != len(rules.boundary_handlers()):
        errs.append("boundaries.yaml: duplicate handler id")
    for hid, h in hs.items():
        if not hid.startswith(f"h.{h['owner']}."):
            errs.append(f"{hid}: in owner-block {h['owner']} but not prefixed h.{h['owner']}.")
        bl = h["boundary"] if isinstance(h["boundary"], (list, tuple)) else [h["boundary"]]
        for x in bl:
            if x not in bounds:
                errs.append(f"{hid}: unknown boundary {x}")
        if not (isinstance(h.get("phase"), int) and 1 <= h["phase"] <= 9):
            errs.append(f"{hid}: phase {h.get('phase')!r} not in 1..9")
        for t in h.get("before") or ():
            if t not in hs:
                errs.append(f"{hid}: before: unknown handler {t}")
            elif hs[t]["phase"] != h["phase"]:
                errs.append(f"{hid}: before: {t} is in another phase")
    return errs


def _check_refs(rules: Rules) -> list[str]:
    errs: list[str] = []
    for aid, a in rules.anchors.items():
        v = a.get("verb")
        if v and v not in rules.basic_verbs:
            errs.append(f"{aid}: unknown verb {v}")
    lic_like = set(rules.licenses) | set(rules.abilities)
    for oid, o in rules.origins.items():
        for lic in list(o.get("licenses") or ()) + list(o.get("languages") or ()):
            if isinstance(lic, str) and lic.startswith("lic.") and lic not in lic_like:
                errs.append(f"{oid}: unknown license {lic}")
    for aid, a in rules.adversaries.items():
        arch = a.get("archetype")
        if isinstance(arch, str) and arch not in rules.archetypes:
            errs.append(f"{aid}: unknown archetype {arch}")
        for ab in a.get("abilities") or ():
            if isinstance(ab, str) and ab.startswith("ab.") and ab not in rules.abilities:
                errs.append(f"{aid}: unknown ability {ab}")
    for tid, t in rules.oracles.items():
        if not re.match(r"^(\d*d\d+|none)$", str(t.get("die", ""))):  # 'none': a dispatcher (tbl.twist)
            errs.append(f"{tid}: die {t.get('die')!r}")
    return errs


# ------------------------------------------------------------------------------------------- loading


def _parse_all(root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    loader: Any = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    docs: dict[str, Any] = {}
    broken: dict[str, str] = {}
    errors: list[str] = []
    for p in sorted((root / "data").glob("*.yaml")):
        try:
            docs[p.stem] = freeze(yaml.load(p.read_text(encoding="utf-8"), Loader=loader))
        except yaml.YAMLError as e:
            msg = str(e).split("\n")[0]
            if p.name in KNOWN_DEFECTS:
                broken[p.name] = f"{msg} ({KNOWN_DEFECTS[p.name]})"
            else:
                errors.append(f"{p.name} does not parse: {e}")
    if errors:
        raise RulesDataError("\n".join(errors))
    return docs, broken


def _cache_path(digest: str) -> Path:
    return CACHE_DIR / f"rules-{CACHE_FORMAT}-{digest[:24]}.pickle"


@functools.lru_cache(maxsize=4)
def _load(root: Path) -> Rules:
    digest = rules_hash(root)
    cache = _cache_path(digest)
    if cache.exists():
        try:
            with cache.open("rb") as f:
                stored = pickle.load(f)
            if stored.get("hash") == digest and stored.get("root") == str(root):
                return Rules(root, digest, stored["docs"], stored["broken"])
        except Exception:  # noqa: BLE001 - a bad cache is rebuilt, never trusted
            pass
    docs, broken = _parse_all(root)
    rules = Rules(root, digest, docs, broken)
    problems = validate(rules)
    if problems:
        head = "\n".join(problems[:40])
        raise RulesDataError(f"{len(problems)} problem(s) in {root / 'data'}:\n{head}")
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = cache.with_suffix(".tmp")
        with tmp.open("wb") as f:
            pickle.dump({"hash": digest, "root": str(root), "docs": docs, "broken": broken}, f, protocol=5)
        tmp.replace(cache)
        for stale in CACHE_DIR.glob("rules-*.pickle"):
            if stale != cache:
                stale.unlink(missing_ok=True)
    except OSError:
        pass
    return rules


def load_rules(root: Path | None = None) -> Rules:
    """The validated rules data for `root` (default: the repo's rules/). Loaded once per process; parsed YAML is
    cached on disk under engine/data/_cache keyed by `rules_hash`, so a rules change forces a reparse."""
    return _load((root or RULES_ROOT).resolve())
