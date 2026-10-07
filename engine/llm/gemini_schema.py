"""Convert the engine's JSON Schemas into the subset Gemini's `response_json_schema` accepts.

What the API accepts (google-genai 2.25.0 `GenerateContentConfig.response_json_schema` docstring and
ai.google.dev/gemini-api/docs/structured-output, read 2026-10-07): `$id`, `$defs`, `$ref`, `$anchor`, `type`
(a single type, or a list with "null"), `format`, `title`, `description`, `enum` (strings and numbers only),
`items`, `prefixItems`, `minItems`, `maxItems`, `minimum`, `maximum`, `anyOf`, `oneOf` (read as `anyOf`),
`properties`, `additionalProperties`, `required`, and the non-standard `propertyOrdering`. A `$ref` may have
no sibling keyword except `$`-prefixed ones. "Very large or deeply nested schemas may be rejected"; no
number is published, so the caps below are our own conservative guesses.

The conversion only ever loosens: the engine still validates every response against the ORIGINAL schema
(`call_role`), so a relaxed field (an enum turned into a described string, a dropped `maxLength`) is checked
there and re-asked on failure. `convert` returns the notes naming every relaxation so the call record shows
them.

Levels: 0 = faithful (unsupported keywords dropped, large enums relaxed); 1 = loose (every enum becomes a
described string and item counts are dropped), the fallback when the server rejects level 0.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

SUPPORTED = frozenset({
    "$id", "$defs", "$ref", "$anchor", "type", "format", "title", "description", "enum", "items",
    "prefixItems", "minItems", "maxItems", "minimum", "maximum", "anyOf", "properties",
    "additionalProperties", "required", "propertyOrdering",
})
TYPES = frozenset({"string", "number", "integer", "boolean", "object", "array", "null"})

MAX_ENUM = 100  # values in one enum before it becomes a described string (our cap; none is published)
MAX_ENUM_TOTAL = 400  # enum values across the whole schema; the largest enums are relaxed first past this
MAX_ENUM_CHARS = 12_000  # characters of enum values across the schema (same rule)
MAX_DESCRIPTION = 2_000  # characters listed in a relaxed enum's description
MAX_DEPTH = 12  # nesting checked by `problems` (ours reach 5)
MAX_BYTES = 60_000  # serialised size checked by `problems` (ours reach about 6 KB)

# Unsupported constraints that are worth telling the model about in words.
_HINTS = {
    "minLength": "at least {} characters",
    "maxLength": "at most {} characters",
    "pattern": "matching the pattern {}",
    "exclusiveMinimum": "greater than {}",
    "exclusiveMaximum": "less than {}",
    "multipleOf": "a multiple of {}",
    "uniqueItems": "no repeated items",
}


@dataclass
class Converted:
    schema: dict[str, Any]
    level: int = 0
    relaxed: list[str] = field(default_factory=list)  # one note per loosened path: "$.cast.items: enum(140) …"


def to_gemini(schema: Mapping[str, Any], *, level: int = 0) -> dict[str, Any]:
    """The schema Gemini is sent (see `convert` for the notes)."""
    return convert(schema, level=level).schema


def convert(schema: Mapping[str, Any], *, level: int = 0) -> Converted:
    notes: list[str] = []
    root = dict(schema)
    out = _node(root, root, "$", notes, level, frozenset())
    defs = root.get("$defs")
    if isinstance(defs, Mapping) and _has_ref(out):  # a recursive ref was kept: keep its targets
        out["$defs"] = {k: _node(v, root, f"$.$defs.{k}", notes, level, frozenset()) for k, v in defs.items()}
    if level == 0:
        _cap_enums(out, notes)
    return Converted(schema=out, level=level, relaxed=notes)


# ---------------------------------------------------------------- the walk


def _node(
    node: Any, root: Mapping[str, Any], path: str, notes: list[str], level: int, refs: frozenset[str],
) -> dict[str, Any]:
    if not isinstance(node, Mapping):
        return {}
    node = dict(node)
    if "$ref" in node:
        ref = node["$ref"]
        target = _deref(ref, root)
        if target is None or ref in refs:  # unknown or recursive: keep the bare ref (Gemini unrolls a little)
            return {"$ref": ref}
        extra = {k: v for k, v in node.items() if k != "$ref"}
        return _node({**target, **extra}, root, path, notes, level, refs | {ref})
    if "const" in node:
        c = node.pop("const")
        if isinstance(c, str | int | float) and not isinstance(c, bool):
            node["enum"] = [c]
        else:
            notes.append(f"{path}: const dropped")
    if "oneOf" in node:
        node["anyOf"] = [*node.pop("oneOf"), *node.get("anyOf", [])]
    if "allOf" in node:
        parts = node.pop("allOf")
        if isinstance(parts, list) and len(parts) == 1 and isinstance(parts[0], Mapping):
            node = {**parts[0], **node}
        else:
            notes.append(f"{path}: allOf dropped")

    t = node.get("type")
    if isinstance(t, list):
        kinds = [x for x in dict.fromkeys(t) if x in TYPES]
        if len(kinds) == 1:
            node["type"] = kinds[0]
        elif kinds:
            # A type union becomes anyOf, one branch per type; enum values go to the branch of their type.
            return _union(node, kinds, root, path, notes, level, refs)

    out: dict[str, Any] = {}
    hints: list[str] = []  # sentences appended to the description
    for key, value in node.items():
        if key == "properties" and isinstance(value, Mapping):
            out["properties"] = {
                k: _node(v, root, f"{path}.{k}", notes, level, refs) for k, v in value.items()
            }
            out["propertyOrdering"] = list(value)
        elif key in ("items", "additionalProperties") and isinstance(value, Mapping):
            out[key] = _node(value, root, f"{path}.{key}", notes, level, refs)
        elif key == "prefixItems" and isinstance(value, list):
            out[key] = [_node(v, root, f"{path}[{i}]", notes, level, refs) for i, v in enumerate(value)]
        elif key == "anyOf" and isinstance(value, list):
            out[key] = [_node(v, root, f"{path}|{i}", notes, level, refs) for i, v in enumerate(value)]
        elif key == "$defs":
            continue  # refs are inlined; `convert` re-adds $defs only when a recursive ref survives
        elif key == "enum":
            vals = [v for v in value if isinstance(v, str | int | float) and not isinstance(v, bool)]
            if len(vals) != len(value):
                notes.append(f"{path}: non-string enum values dropped")
            if level >= 1:
                hints.append(_listing(vals))
                out["type"] = _scalar_type(vals)
                notes.append(f"{path}: enum({len(vals)}) as string (loose)")
            elif vals:
                out["enum"] = vals
        elif key in ("minItems", "maxItems") and level >= 1:
            notes.append(f"{path}: {key} dropped (loose)")
        elif key == "propertyOrdering":
            continue  # rebuilt from properties
        elif key == "type" and "type" in out:
            continue  # already set by a loose enum
        elif key in SUPPORTED:
            out[key] = value
        elif key in _HINTS:
            hints.append(_HINTS[key].format(value).capitalize() + ".")
            notes.append(f"{path}: {key} dropped")
        elif key not in ("$schema", "default", "examples", "$comment", "readOnly", "writeOnly", "deprecated"):
            notes.append(f"{path}: {key} dropped")
    if "enum" in out and "type" not in out:
        out["type"] = _scalar_type(out["enum"])
    if "required" in out and "properties" in out:
        out["required"] = [k for k in out["required"] if k in out["properties"]]
    if hints:
        out["description"] = _join(out.get("description"), " ".join(hints))
    return out


def _union(
    node: dict[str, Any], kinds: list[str], root: Mapping[str, Any], path: str, notes: list[str], level: int,
    refs: frozenset[str],
) -> dict[str, Any]:
    enum = node.get("enum")
    shared = {k: v for k, v in node.items() if k in ("description", "title")}
    rest = {k: v for k, v in node.items() if k not in ("type", "enum", "description", "title")}
    branches = []
    for kind in kinds:
        branch: dict[str, Any] = {"type": kind}
        if kind != "null":
            branch.update(rest)
        if isinstance(enum, list):
            vals = [v for v in enum if _is_type(v, kind)]
            if kind == "null":
                if None not in enum:
                    continue  # null is in the type list but not the enum: not allowed after all
            elif not vals:
                continue
            else:
                branch["enum"] = vals
        branches.append(_node(branch, root, path, notes, level, refs))
    if len(branches) == 1:
        return {**branches[0], **shared}
    return {**shared, "anyOf": branches}


def _is_type(v: Any, kind: str) -> bool:
    return {
        "string": isinstance(v, str), "null": v is None, "boolean": isinstance(v, bool),
        "integer": isinstance(v, int) and not isinstance(v, bool),
        "number": isinstance(v, int | float) and not isinstance(v, bool),
    }.get(kind, False)


def _deref(ref: Any, root: Mapping[str, Any]) -> Mapping[str, Any] | None:
    if not isinstance(ref, str) or not ref.startswith("#"):
        return None
    target: Any = root
    for part in [p for p in ref[1:].split("/") if p]:
        if not isinstance(target, Mapping) or part not in target:
            return None
        target = target[part.replace("~1", "/").replace("~0", "~")]
    return target if isinstance(target, Mapping) else None


def _has_ref(node: Any) -> bool:
    if isinstance(node, Mapping):
        return "$ref" in node or any(_has_ref(v) for v in node.values())
    if isinstance(node, list):
        return any(_has_ref(v) for v in node)
    return False


def _join(a: Any, b: str) -> str:
    return f"{a} {b}" if a else b


def _scalar_type(vals: list[Any]) -> str:
    return "string" if all(isinstance(v, str) for v in vals) else "number"


def _listing(vals: list[Any]) -> str:
    """'Exactly one of: "a", "b", ….' listing as many values as fit in MAX_DESCRIPTION characters."""
    listed: list[str] = []
    size = 0
    for v in vals:
        s = json.dumps(v, ensure_ascii=False)
        if size + len(s) > MAX_DESCRIPTION:
            listed.append("…")
            break
        listed.append(s)
        size += len(s) + 2
    return f"Exactly one of: {', '.join(listed)}."


def _describe(node: dict[str, Any]) -> None:
    """Replace the node's enum (in place) by a string whose description lists the allowed values."""
    vals = node.pop("enum")
    node["type"] = _scalar_type(vals)
    node["description"] = _join(node.get("description"), _listing(vals))


# ---------------------------------------------------------------- enum caps (level 0)


def _enums(node: Any, path: str = "$") -> list[tuple[str, dict[str, Any]]]:
    found: list[tuple[str, dict[str, Any]]] = []
    if isinstance(node, dict):
        if isinstance(node.get("enum"), list):
            found.append((path, node))
        for k, v in node.items():
            if k in ("properties", "$defs") and isinstance(v, dict):
                for name, sub in v.items():
                    found += _enums(sub, f"{path}.{name}")
            elif k in ("items", "additionalProperties"):
                found += _enums(v, f"{path}.{k}")
            elif k in ("anyOf", "prefixItems") and isinstance(v, list):
                for i, sub in enumerate(v):
                    found += _enums(sub, f"{path}|{i}")
    return found


def _cap_enums(schema: dict[str, Any], notes: list[str]) -> None:
    enums = _enums(schema)
    for path, node in enums:
        if len(node["enum"]) > MAX_ENUM:
            notes.append(f"{path}: enum({len(node['enum'])}) as string (over {MAX_ENUM})")
            _describe(node)
    live = sorted((e for e in _enums(schema)), key=lambda e: -len(e[1]["enum"]))

    def totals() -> tuple[int, int]:
        n = sum(len(nd["enum"]) for _, nd in live)
        c = sum(len(str(v)) for _, nd in live for v in nd["enum"])
        return n, c

    while live and (totals()[0] > MAX_ENUM_TOTAL or totals()[1] > MAX_ENUM_CHARS):
        path, node = live.pop(0)
        notes.append(f"{path}: enum({len(node['enum'])}) as string (schema total over cap)")
        _describe(node)


# ---------------------------------------------------------------- checks (tests and the smoke script)


def problems(schema: Mapping[str, Any]) -> list[str]:
    """Everything in `schema` outside what Gemini documents or our caps; [] for a converted schema."""
    errs: list[str] = []
    total = 0

    def walk(node: Any, path: str, depth: int) -> None:
        nonlocal total
        if not isinstance(node, Mapping):
            errs.append(f"{path}: not an object")
            return
        if depth > MAX_DEPTH:
            errs.append(f"{path}: nested deeper than {MAX_DEPTH}")
        for k in node:
            if k not in SUPPORTED:
                errs.append(f"{path}: unsupported keyword {k}")
        if "$ref" in node and any(not k.startswith("$") for k in node):
            errs.append(f"{path}: $ref with sibling keywords")
        t = node.get("type")
        for x in t if isinstance(t, list) else [t] if t is not None else []:
            if x not in TYPES:
                errs.append(f"{path}: unknown type {x!r}")
        if isinstance(t, list) and len([x for x in t if x != "null"]) > 1:
            errs.append(f"{path}: type union {t}")
        if "enum" in node:
            vals = node["enum"]
            total += len(vals)
            if len(vals) > MAX_ENUM:
                errs.append(f"{path}: enum of {len(vals)} (cap {MAX_ENUM})")
            if any(v is None or isinstance(v, bool) or not isinstance(v, str | int | float) for v in vals):
                errs.append(f"{path}: enum holds a value that is not a string or number")
        props = node.get("properties")
        if isinstance(props, Mapping):
            order = node.get("propertyOrdering")
            if order is not None and list(order) != list(props):
                errs.append(f"{path}: propertyOrdering does not match properties")
            missing = [r for r in node.get("required", []) if r not in props]
            if missing:
                errs.append(f"{path}: required names unknown properties {missing}")
            for k, v in props.items():
                walk(v, f"{path}.{k}", depth + 1)
        for key in ("items", "additionalProperties"):
            if isinstance(node.get(key), Mapping):
                walk(node[key], f"{path}.{key}", depth + 1)
        for key in ("anyOf", "prefixItems"):
            for i, v in enumerate(node.get(key) or []):
                walk(v, f"{path}|{i}", depth + 1)
        for k, v in (node.get("$defs") or {}).items():
            walk(v, f"{path}.$defs.{k}", depth + 1)

    walk(schema, "$", 0)
    if total > MAX_ENUM_TOTAL:
        errs.append(f"$: {total} enum values in all (cap {MAX_ENUM_TOTAL})")
    size = len(json.dumps(schema, ensure_ascii=False))
    if size > MAX_BYTES:
        errs.append(f"$: {size} bytes (cap {MAX_BYTES})")
    return errs
