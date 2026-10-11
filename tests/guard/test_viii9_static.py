"""Spec 033 R12, the static half: no function of `dm_tools.py`, `dm_world.py`, or reached from a dm-tools turn reads
text with words unless the allow-list (`viii9_allow.py`) says why (class P, F or S), or names the phase that removes
it (`pending:<phase>`, which fails from P6). A planted `re.search` fails with the constitution's VIII.9."""

from __future__ import annotations

import pytest

from tests.guard import viii9_allow as allow
from tests.guard.scan import Hit, Module, load_modules, reached_functions, scan

MESSAGE = "constitution VIII.9 (code never deduces the story): {what}"
CLASSES = ("P", "F", "S")


def judge(hits: list[Hit], listed: dict[str, tuple[str, str]], *, strict: bool) -> list[str]:
    """Problems: hits nobody listed, listed entries no longer found, bad classes, `pending` under `strict`."""
    keys = {h.key for h in hits}
    out = [MESSAGE.format(what=f"{k} reads text with words; list it in tests/guard/viii9_allow.py with a class "
                               f"(P, F or S) and a reason, or remove it") for k in sorted(keys - set(listed))]
    out += [MESSAGE.format(what=f"{k} is listed but no longer found; remove the stale entry") for k in
            sorted(set(listed) - keys)]
    for k, (cls, why) in listed.items():
        phase = cls.removeprefix("pending:")
        if cls not in CLASSES and not (cls.startswith("pending:") and phase in allow.PHASES):
            out.append(MESSAGE.format(what=f"{k} has class {cls!r}; use P, F, S or pending:<phase>"))
        elif not why.strip():
            out.append(MESSAGE.format(what=f"{k} has no reason"))
        elif strict and cls.startswith("pending:"):
            out.append(MESSAGE.format(what=f"{k} is still {cls}: phase {phase} did not remove it"))
    return out


def test_the_scan_finds_the_known_matchers() -> None:
    """The scanner is alive: it reads the files and the reached list (a stale reached.txt would hide hits)."""
    reached = reached_functions()
    assert sum(len(v) for v in reached.values()) > 500
    keys = {h.key for h in scan()}
    assert "engine.dm.dm_tools:_party:pattern:_NAME" in keys
    assert "engine.resolve.gate:forbidden_by_condition:re:match" in keys


def test_every_word_reading_function_is_listed_with_a_class() -> None:
    problems = judge(scan(), allow.flat(), strict=allow.STRICT)
    assert not problems, "\n".join(problems[:30]) + (f"\n... {len(problems)} in all" if len(problems) > 30 else "")


def test_the_allow_list_is_pending_until_p6_then_strict() -> None:
    pending = [k for k, (cls, _) in allow.flat().items() if cls.startswith("pending:")]
    assert allow.STRICT or pending, "STRICT is off but nothing is pending: set STRICT = True"
    assert not (allow.STRICT and pending), f"{len(pending)} entries still pending"


# ---------------------------------------------------------------------------------------------- C12: planted code

PLANTED = '''
import re
_NAMES = {"alice", "bob", "carol"}
_RX = re.compile(r"edda")

def decide(text):
    if re.search(r"sword", text):
        return 1

def by_pattern(text):
    return _RX.search(text)

def by_list(text):
    return text in _NAMES

def clean(text):
    return text.strip()
'''


def planted(source: str = PLANTED) -> list[Hit]:
    mods = {"engine.dm.dm_tools": Module("engine.dm.dm_tools", source)}
    return scan(mods, {})


def test_a_planted_re_call_a_pattern_and_a_word_list_each_fail_citing_viii9() -> None:
    hits = planted()
    assert {h.key for h in hits} == {
        "engine.dm.dm_tools:decide:re:search", "engine.dm.dm_tools:by_pattern:pattern:_RX",
        "engine.dm.dm_tools:by_list:words:_NAMES"}  # `clean` is not a hit
    problems = judge(hits, {}, strict=False)
    assert len(problems) == 3 and all("constitution VIII.9" in p for p in problems)


def test_the_same_lines_listed_as_p_pass_and_a_stale_entry_fails() -> None:
    hits = planted()
    listed = {h.key: ("P", "planted for the test") for h in hits}
    assert judge(hits, listed, strict=True) == []
    problems = judge(hits, {**listed, "engine.dm.dm_tools:gone:re:sub": ("P", "x")}, strict=True)
    assert len(problems) == 1 and "stale" in problems[0]


def test_pending_passes_until_strict_and_an_unknown_class_fails() -> None:
    hits = planted()
    listed = {h.key: ("pending:P4", "removed by P4") for h in hits}
    assert judge(hits, listed, strict=False) == []
    assert all("still pending:P4" in p for p in judge(hits, listed, strict=True))
    bad = {h.key: ("X", "no such class") for h in hits}
    assert all("class 'X'" in p for p in judge(hits, bad, strict=False))


@pytest.mark.parametrize("mod", ["engine.dm.dm_tools", "engine.dm.dm_world"])
def test_the_two_dm_files_are_scanned_whole(mod: str) -> None:
    mods = load_modules()
    funcs = set(mods[mod].functions())
    scanned = {h.func for h in scan(mods, {}) if h.module == mod}
    assert scanned and scanned <= funcs and len(funcs) > 5
