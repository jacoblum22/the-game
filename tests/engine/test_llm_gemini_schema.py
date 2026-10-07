"""engine/llm/gemini_schema.py: the engine's schemas -> the JSON Schema subset Gemini accepts.

The fixtures are the schemas a real offline game sent to the model (tests/engine/fixtures_gemini_schemas/,
one per role at its largest seen, plus `largest.json`).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from engine.llm import gemini_schema as gs
from engine.llm.base import Packet, Role, validate
from engine.llm.gemini_schema import convert, problems, to_gemini
from engine.llm.offline import OfflineModel, conform

FIXTURES = Path(__file__).parent / "fixtures_gemini_schemas"
ROLES = [r for r in Role if (FIXTURES / f"{r.value}.json").is_file()]


def fixture(name: str) -> dict[str, Any]:
    data = json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
    return data["schema"] if name == "largest" else data


def keywords(node: Any) -> set[str]:
    """Every schema keyword used (property names are not keywords)."""
    out: set[str] = set()
    if isinstance(node, dict):
        for k, v in node.items():
            out.add(k)
            if k in ("properties", "$defs"):
                for sub in v.values():
                    out |= keywords(sub)
            elif k in ("items", "additionalProperties"):
                out |= keywords(v)
            elif k in ("anyOf", "prefixItems"):
                for sub in v:
                    out |= keywords(sub)
    return out


def test_every_role_has_a_fixture() -> None:
    assert set(ROLES) == set(Role)
    assert fixture("largest")["type"] == "object"


@pytest.mark.parametrize("name", [*[r.value for r in Role], "largest"])
@pytest.mark.parametrize("level", [0, 1])
def test_fixtures_convert_to_supported_subset(name: str, level: int) -> None:
    original = fixture(name)
    before = copy.deepcopy(original)
    out = to_gemini(original, level=level)
    assert problems(out) == []
    assert keywords(out) <= gs.SUPPORTED
    assert original == before  # the engine's schema is never mutated
    if level == 1:
        assert "enum" not in keywords(out) and "maxItems" not in keywords(out)
    assert len(json.dumps(out)) < gs.MAX_BYTES


@pytest.mark.parametrize("role", ROLES)
def test_values_valid_for_the_original_stay_valid(role: Role) -> None:
    """The conversion only loosens: an offline answer valid against the original passes the converted one."""
    schema = fixture(role.value)
    packet = Packet(instructions="x", message="I look around. quiet_turns: 1", view="pc.wren: Wren\n  name: Wren")
    samples = [OfflineModel().fill(role, schema, packet, turn_id=None, attempt=0).data, conform(None, schema, schema)]
    for value in samples:
        assert validate(value, schema) == []
        for level in (0, 1):
            assert validate(value, to_gemini(schema, level=level)) == []


def test_property_ordering_follows_the_engine_order() -> None:
    out = to_gemini(fixture("narrator"))
    assert out["propertyOrdering"] == ["fiction", "mentions"]
    item = out["properties"]["mentions"]["items"]
    assert item["propertyOrdering"] == list(item["properties"])


def test_nullable_enum_becomes_anyof_without_null_in_enum() -> None:
    out = to_gemini({"type": ["string", "null"], "enum": ["a", "b", None]})
    assert out == {"anyOf": [{"type": "string", "enum": ["a", "b"]}, {"type": "null"}]}
    assert to_gemini({"type": ["string", "null"]}) == {"anyOf": [{"type": "string"}, {"type": "null"}]}
    # null in the type list but not in the enum: null is not allowed after all
    assert to_gemini({"type": ["string", "null"], "enum": ["a"]}) == {"type": "string", "enum": ["a"]}


def test_unsupported_keywords() -> None:
    conv = convert({
        "type": "object", "properties": {
            "a": {"const": "x"},
            "b": {"oneOf": [{"type": "string"}, {"type": "integer"}]},
            "c": {"type": "string", "minLength": 2, "maxLength": 9, "default": "zz"},
            "d": {"allOf": [{"type": "boolean"}]},
        }, "required": ["a", "b", "c", "d", "ghost"], "additionalProperties": False,
    })
    p = conv.schema["properties"]
    assert p["a"] == {"enum": ["x"], "type": "string"}
    assert p["b"] == {"anyOf": [{"type": "string"}, {"type": "integer"}]}
    assert p["c"]["type"] == "string" and "minLength" not in p["c"] and "default" not in p["c"]
    assert p["c"]["description"] == "At least 2 characters. At most 9 characters."
    assert p["d"] == {"type": "boolean"}
    assert conv.schema["required"] == ["a", "b", "c", "d"]
    assert conv.schema["additionalProperties"] is False
    assert any("minLength" in n for n in conv.relaxed) and problems(conv.schema) == []


def test_refs_are_inlined_and_recursion_kept() -> None:
    flat = to_gemini({"$defs": {"N": {"type": "string", "enum": ["x"]}},
                      "type": "object", "properties": {"n": {"$ref": "#/$defs/N"}}})
    assert flat["properties"]["n"] == {"type": "string", "enum": ["x"]} and "$defs" not in flat
    tree = to_gemini({"$defs": {"T": {"type": "object", "properties": {"kids": {"type": "array",
                                                                               "items": {"$ref": "#/$defs/T"}}}}},
                      "$ref": "#/$defs/T"})
    assert tree["properties"]["kids"]["items"] == {"$ref": "#/$defs/T"} and "T" in tree["$defs"]
    assert problems(tree) == []


def test_large_enum_becomes_described_string_and_original_still_checks() -> None:
    ids = [f"npc.n{i:03d}" for i in range(gs.MAX_ENUM + 40)]
    schema = {"type": "object", "properties": {"cast": {"type": "array", "items": {"type": "string", "enum": ids}}},
              "required": ["cast"], "additionalProperties": False}
    conv = convert(schema)
    item = conv.schema["properties"]["cast"]["items"]
    assert "enum" not in item and item["type"] == "string" and "npc.n000" in item["description"]
    assert len(item["description"]) <= gs.MAX_DESCRIPTION + 100
    assert conv.relaxed and "$.cast.items" in conv.relaxed[0] and problems(conv.schema) == []
    assert validate({"cast": ["npc.bogus"]}, conv.schema) == []  # Gemini may now say anything ...
    assert validate({"cast": ["npc.bogus"]}, schema) != []  # ... and the engine's own check still catches it


def test_total_enum_budget_relaxes_largest_first() -> None:
    small = [f"s{i}" for i in range(10)]
    props = {f"f{i}": {"type": "string", "enum": [f"v{i}.{j}" for j in range(90)]} for i in range(6)}
    props["small"] = {"type": "string", "enum": small}
    conv = convert({"type": "object", "properties": props, "required": list(props)})
    left = [k for k, v in conv.schema["properties"].items() if "enum" in v]
    assert "small" in left and len(left) < len(props)
    assert problems(conv.schema) == []


def test_problems_flags_raw_engine_shapes() -> None:
    raw = {"type": "object", "properties": {"x": {"type": ["string", "null"], "enum": ["a", None]},
                                            "y": {"type": "string", "maxLength": 3}}}
    errs = problems(raw)
    assert any("enum holds" in e for e in errs) and any("maxLength" in e for e in errs)
