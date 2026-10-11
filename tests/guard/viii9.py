"""Spec 033 P0: the VIII.9 guard (constitution 3.1.0 VIII.9: code never deduces the story).

A denylist of engine functions and word patterns that decide the story from prose or guess story state. While a
dm-tools turn runs (`engine.dm.dm_tools.play_turn` / `play_answer`) each entry is patched in every engine module that
holds it: a hit is recorded, and in `raise` mode an entry whose own mode is `raise` also raises `Viii9Violation`.
Every entry starts as `log`; each spec 033 phase moves the entries it makes unreachable to `raise` (P6 asserts all are).

    with Guard() as g:           # mode from the VIII9_GUARD environment variable: "log" (default) or "raise"
        play the game
    g.hits, g.reach, g.edges     # what was reached (see `census.py`)

`WATCH` lists census-only names: reached or not, never denied (class S/F/P candidates and low-confidence items).
"""

from __future__ import annotations

import functools
import json
import os
import sys
import types
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from types import CodeType
from typing import Any

MESSAGE = "constitution VIII.9 (code never deduces the story): dm-tools reached {name} ({inv})"


class Viii9Violation(AssertionError):
    """A denylisted function or pattern was reached by a dm-tools turn."""


@dataclass(frozen=True)
class Entry:
    inv: str  # the inventory ids (fiction-inference A/B/C, word-matching D)
    phase: str  # the spec 033 phase that makes it unreachable (and flips `mode` to "raise")
    mode: str = "log"  # "log" | "raise"
    only_from: str | None = None  # the one caller allowed to reach it: "module.qualname"
    scope: str = "turn"  # "turn": inside a dm-tools turn; "shell": anywhere inside Game.submit/answer on dm-tools


def _e(inv: str, phase: str, **kw: Any) -> Entry:
    return Entry(inv, phase, **kw)


_P, _R, _S, _W = "engine.resolve.pipeline.", "engine.resolve.conflict.", "engine.resolve.gate.", "engine.retrieve.scene."
_F, _C, _M, _D = "engine.resolve.frame.", "engine.resolve.change.", "engine.dm.mentions.", "engine.dm.dm_tools."
_T, _N, _SO = "engine.dm.testimony.", "engine.dm.npc_layer.", "engine.world.social."

# qualified name -> Entry. Functions are wrapped; module-level patterns, tuples and dicts are proxied.
DENY: dict[str, Entry] = {
    # P2a: positions, contact, fight start, hold release, penalty details (R1 R2 R5)
    _P + "_AWAY": _e("D1", "P2a"), _P + "_moved": _e("D1 A3", "P2a"),
    _P + "_DOWN": _e("D2 A2", "P2a"), _P + "_contact": _e("D2 A1", "P2a"),
    _P + "_FREEING": _e("D3 A13", "P2a"), _P + "_cleanse": _e("D3 A13", "P2a"),
    _P + "_cost_params": _e("A15 A16", "P2a"),
    _R + "start": _e("A4 A5", "P2a", only_from="engine.dm.dm_tools._fight"),
    _R + "NONLETHAL": _e("D5", "P2a"), _R + "UNARMED": _e("D5", "P2a"), _R + "weapon": _e("D5", "P2a"),
    _C + "_VERB_GOAL": _e("A11 A12", "P2a"), _C + "_person": _e("D15 N4", "P2a"),
    # P3: the foe's choice (R3)
    _R + "foe_beat": _e("A7 A8 A9", "P3"), "engine.dm.world_step.foes_act": _e("A7 A8 A9", "P3"),
    # P5: leads and witnesses are told, never spawned (R4)
    "engine.world.pacing.inject_lead": _e("A19", "P5"), "engine.gen.case.audit_cases": _e("A20", "P5"),
    # P2b: beat-text decisions (R7), search by id (R10)
    # (`resolve_names` and `_PROPER_RUN` left the list: `recall`'s codex search still lists candidates with them, class S)
    _S + "_STOP": _e("D6", "P2b", mode="raise"), _S + "excluded_by": _e("D6", "P2b", mode="raise"),
    _S + "excluded_anywhere": _e("D6", "P2b", mode="raise"), _S + "would_be_license": _e("D6", "P2b", mode="raise"),
    _S + "_tongue": _e("D6", "P2b", mode="raise"), _S + "WRITING": _e("D7", "P2b", mode="raise"),
    _S + "LOOKS_AT": _e("D8", "P2b", mode="raise"), _S + "reads_writing": _e("D8", "P2b", mode="raise"),
    _W + "READING": _e("D10", "P2b", mode="raise"), _W + "focus_ids": _e("D18", "P2b", mode="raise"),
    "engine.retrieve.anchors._intent_hits": _e("D20", "P2b", mode="raise"),
    _F + "_LIFT": _e("D11", "P2b", mode="raise"), _F + "_UNDO": _e("D12", "P2b", mode="raise"),
    _F + "_REFUSE": _e("D12", "P2b", mode="raise"),
    # P4: identity, walk-ons, testimony, the measures that leave the engine (R6 R8 R11)
    _D + "_NAME": _e("D21", "P4"), _D + "_PC_WORDS": _e("D21", "P4"),
    _D + "_PERSON_KIND": _e("D24", "P4"), _D + "_THING_KIND": _e("D24", "P4"),
    _D + "_audit": _e("M", "P4"), _D + "_log_only": _e("M", "P4"), _D + "_content": _e("M", "P4"),
    _D + "_name_tokens": _e("M", "P4"),
    _M + "write_mentions": _e("D30 A22", "P4"), _M + "find_existing": _e("D30 A22", "P4"), _M + "bare": _e("D31", "P4"), _M + "_proper": _e("D31", "P4"),
    _M + "_slug": _e("D31", "P4"), _M + "_ARTICLE": _e("D31", "P4"), _M + "_HELD_BY": _e("D32", "P4"),
    _M + "_holder": _e("D32", "P4"), _M + "_NPC_KEYS": _e("D33", "P4"), _M + "_PRONOUNS": _e("D33", "P4"),
    _M + "_GENDERS": _e("D33", "P4"), _M + "_npc": _e("D33", "P4"),
    _N + "ANIMAL": _e("D34 N2", "P4"), _N + "is_animal": _e("D34 N2", "P4"), _N + "role_key": _e("D34", "P4"),
    "engine.gen.npc.role_implies": _e("D33 (census)", "P4"),  # the census found it: role words -> age and pronouns
    _SO + "find_npc": _e("D35", "P4"), _SO + "_GROUP": _e("D35", "P4"), _SO + "cast_described": _e("D35 A24", "P4"),
    _T + "overlap": _e("D36", "P4"), _T + "is_repeat": _e("D36", "P4"), _T + "_named": _e("D37", "P4"),
    _T + "_premise": _e("D37", "P4"), _T + "_BEYOND": _e("D38", "P4"), _T + "_OWN_WILL": _e("D38", "P4"),
    _T + "_case_route": _e("D38", "P4"), _T + "_FIGURE": _e("D39", "P4"), _T + "_place_there": _e("D39 A25", "P4"),
    # P5: retire by `/retire` or the DM (R9); runs in the game shell, so its scope is the whole submit
    "engine.dm.ending._RETIRE": _e("D43", "P5", scope="shell"),
    "engine.dm.ending.is_retire": _e("D43", "P5", scope="shell"),
}

# Census only: recorded when reached, never denied. value = what the census expects it to be (S search, F format,
# P code-made strings, ? undecided) and the inventory id.
WATCH: dict[str, str] = {
    "engine.retrieve.scene.scene_facts": "? D19",
    "engine.retrieve.scene.resolve_names": "S D17 (recall's search lists candidates; the DM judges)",
    "engine.retrieve.scene._PROPER_RUN": "S D17",
    "engine.resolve.frame._fitted": "P D13 (exact equality with the menu example)",
    "engine.resolve.frame.lift_or_carry": "P D11 (stated: the typed take only)",
    "engine.resolve.frame.reverses": "P D12 (stated: reverses_goal over cost ids)",
    "engine.resolve.necessity.plain_reading": "P D9 (stated: stated.reads)",
    "engine.resolve.necessity.certain_talk": "P D9 (typed fields and recorded standing; no words)",
    "engine.resolve.necessity.looks_here": "P D9 (ids: the target is the mover place)",
    "engine.resolve.oracle.positive": "? D14",
    "engine.resolve.oracle._POSSESS": "? D14", "engine.resolve.oracle._NEG": "? D14",
    "engine.resolve.pipeline._same_goal": "P D4",
    "engine.resolve.change.apply_change": "? D16 (startswith at line 366)",
    "engine.resolve.change.typed_goal": "? A11",
    "engine.dm.world_step.deliver_learning": "? A (learning delivery)",
    "engine.dm.world_step.npcs_respond": "N",
    "engine.dm.codex.what_you_know": "S D41", "engine.dm.codex.promise_subject": "S D41",
    "engine.dm.codex._stems": "S D41", "engine.dm.codex.PROMISE": "S D41",
    "engine.dm.ending.retire_choice": "S D43", "engine.dm.ending.ending_choice": "S D43",
    "engine.dm.dispute._names": "X D46",
    "engine.dm.incident.OFFICERS": "? D53", "engine.store.details.slot_of": "? D53",
    "engine.store.views.sheet_holds": "? D53", "engine.store.views.unnamed_label": "? D53",
    "engine.dm.packet.pronouns_of": "F D54", "engine.dm.packet.own_words": "F D54",
    "engine.dm.packet.background_line": "F D54", "engine.dm.packet.people_card": "F D54",
    "engine.gen._seed_packs.role_key": "? D55",
    "engine.dm.dm_tools._along": "? D27", "engine.dm.dm_tools._told": "? D28",
    "engine.dm.dm_tools._party": "? D22", "engine.dm.dm_tools._walk_on": "? D23",
    "engine.dm.dm_tools._state": "? D25",
}
AUDIT_TEXT = "engine.audit.text."  # D40: the primitives; every caller of them is recorded as an edge

_ENGINE = "engine."


def mode_from_env() -> str:
    return os.environ.get("VIII9_GUARD", "log")


class _Proxy:
    """Stands in for a module-level pattern, word list or table; every use is a hit, then delegates."""

    def __init__(self, real: Any, hit: Callable[[], None]) -> None:
        object.__setattr__(self, "_real", real)
        object.__setattr__(self, "_hit", hit)

    def __getattr__(self, name: str) -> Any:
        if not name.startswith("__"):
            object.__getattribute__(self, "_hit")()
        return getattr(object.__getattribute__(self, "_real"), name)

    def __getitem__(self, k: Any) -> Any:
        self._hit()  # type: ignore[attr-defined]
        return self._real[k]  # type: ignore[attr-defined]

    def __contains__(self, k: Any) -> bool:
        self._hit()  # type: ignore[attr-defined]
        return k in self._real  # type: ignore[attr-defined]

    def __iter__(self) -> Any:
        self._hit()  # type: ignore[attr-defined]
        return iter(self._real)  # type: ignore[attr-defined]

    def __len__(self) -> int:
        return len(self._real)  # type: ignore[attr-defined]


def _delegate(op: str) -> Callable[..., Any]:
    def method(self: _Proxy, *a: Any) -> Any:
        self._hit()  # type: ignore[attr-defined]
        a = tuple(x._real if isinstance(x, _Proxy) else x for x in a)  # type: ignore[attr-defined]
        return getattr(self._real, op)(*a)  # type: ignore[attr-defined]

    return method


for _op in ("__and__", "__or__", "__sub__", "__xor__", "__rand__", "__ror__", "__rsub__", "__rxor__", "__eq__",
            "__repr__", "__str__"):
    setattr(_Proxy, _op, _delegate(_op))
_Proxy.__hash__ = lambda self: id(self)  # type: ignore[method-assign,assignment]


def _resolve(name: str) -> tuple[Any, str, str | None]:
    """`engine.mod.sub.attr` -> (module, attr, None); `engine.mod.Class.method` -> (module, attr, class name)."""
    parts = name.split(".")
    for i in range(len(parts) - 1, 0, -1):
        mod = sys.modules.get(".".join(parts[:i]))
        if mod is None:
            try:
                mod = __import__(".".join(parts[:i]), fromlist=["_"])
            except ImportError:
                continue
        rest = parts[i:]
        if len(rest) == 1:
            return mod, rest[0], None
        return mod, rest[1], rest[0]
    raise KeyError(name)


class Guard:
    """Patches the denylist while active; collects hits, reached functions and caller edges."""

    def __init__(self, deny: dict[str, Entry] | None = None, watch: dict[str, str] | None = None, *,
                 mode: str | None = None, jsonl: Path | None = None, record_reach: bool = True) -> None:
        self.deny = DENY if deny is None else deny
        self.watch = WATCH if watch is None else watch
        self.mode = mode or mode_from_env()
        self.jsonl = jsonl
        self.record_reach = record_reach
        self.turn_depth = 0  # inside a dm-tools turn
        self.shell_depth = 0  # inside Game.submit / answer on the dm-tools engine
        self.hits: list[dict[str, Any]] = []
        self.trace: list[str] = []  # one line per submitted message (the census games fill it)
        self.reach: Counter[tuple[str, str]] = Counter()  # (scope, qualified name) -> calls
        self.edges: Counter[tuple[str, str, str]] = Counter()  # (scope, caller, callee) for tracked callees
        self._undo: list[Callable[[], None]] = []
        self._codes: dict[CodeType, tuple[str, str | None]] = {}
        self.parts: dict[str, tuple[str, str]] = {}  # reached name -> (module, qualname)
        self._track = set(self.deny) | set(self.watch)

    # ------------------------------------------------------------------------------------------ scope
    @property
    def scope(self) -> str | None:
        return "turn" if self.turn_depth else "shell" if self.shell_depth else None

    def _armed(self, entry: Entry) -> bool:
        return bool(self.turn_depth) if entry.scope == "turn" else bool(self.turn_depth or self.shell_depth)

    # ------------------------------------------------------------------------------------------ hits
    def _stack(self, depth: int) -> list[str]:
        """The dm-tools / dm-world functions on the stack, outermost first, with the tool call being run."""
        out: list[str] = []
        f: Any = sys._getframe(depth)
        while f is not None:
            mod = f.f_globals.get("__name__", "")
            if mod in ("engine.dm.dm_tools", "engine.dm.dm_world"):
                out.append(f.f_code.co_name)
                call = f.f_locals.get("call") or f.f_locals.get("c")
                if f.f_code.co_name in ("tool", "_propose_roll", "_change") and isinstance(call, dict):
                    out[-1] += f"[{call.get('tool') or ''}:{call.get('kind') or call.get('verb') or ''}]"
            f = f.f_back
        return out[::-1]

    def _caller(self, depth: int) -> str:
        f: Any = sys._getframe(depth)
        return f"{f.f_globals.get('__name__', '')}.{f.f_code.co_qualname}"

    def _hit(self, name: str, entry: Entry, skip: int) -> None:
        """`skip`: the frames between this call and the code that reached the entry (the wrapper, the proxy)."""
        if not self._armed(entry):
            return
        depth = skip + 2
        if entry.only_from is not None and self._caller(depth) == entry.only_from:
            return
        eff = "raise" if (self.mode == "raise" and entry.mode == "raise") else "log"
        rec = {"name": name, "inv": entry.inv, "phase": entry.phase, "mode": eff, "scope": self.scope,
               "caller": self._caller(depth), "path": self._stack(depth)}
        self.hits.append(rec)
        if self.jsonl is not None:
            with self.jsonl.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")
        if eff == "raise":
            raise Viii9Violation(MESSAGE.format(name=name.removeprefix(_ENGINE), inv=entry.inv))

    # ------------------------------------------------------------------------------------------ patching
    def _swap(self, owner: Any, attr: str, new: Any) -> None:
        old = getattr(owner, attr)
        setattr(owner, attr, new)
        self._undo.append(lambda: setattr(owner, attr, old))

    def _patch(self, name: str, entry: Entry) -> None:
        mod, attr, cls = _resolve(name)
        holder = mod if cls is None else getattr(mod, cls)
        old = getattr(holder, attr)
        is_fn = isinstance(old, types.FunctionType)
        if is_fn:
            @functools.wraps(old)
            def wrapper(*a: Any, **k: Any) -> Any:
                self._hit(name, entry, 1)
                return old(*a, **k)

            new: Any = wrapper
        else:
            new = _Proxy(old, lambda: self._hit(name, entry, 2))
        for m in list(sys.modules.values()):  # `from x import f` copies: swap every holder of the same object
            if m is not None and getattr(m, "__name__", "").startswith(_ENGINE):
                for k2, v in list(vars(m).items()):
                    if v is old and (is_fn or k2 == attr):
                        self._swap(m, k2, new)
        if cls is not None:
            self._swap(holder, attr, new)

    def _wrap_scopes(self) -> None:
        from engine.dm import dm_tools
        from engine.game import Game

        def around(depth_attr: str, fn: Callable[..., Any], only_dm_tools: bool) -> Callable[..., Any]:
            @functools.wraps(fn)
            def inner(*a: Any, **k: Any) -> Any:
                if only_dm_tools and not dm_tools.enabled(a[0].ctx):
                    return fn(*a, **k)
                setattr(self, depth_attr, getattr(self, depth_attr) + 1)
                try:
                    return fn(*a, **k)
                finally:
                    setattr(self, depth_attr, getattr(self, depth_attr) - 1)

            return inner

        for fname in ("play_turn", "play_answer"):
            fn = getattr(dm_tools, fname)

            @functools.wraps(fn)
            def turn_inner(*a: Any, _fn: Callable[..., Any] = fn, **k: Any) -> Any:
                self.turn_depth += 1
                try:
                    return _fn(*a, **k)
                finally:
                    self.turn_depth -= 1

            self._swap(dm_tools, fname, turn_inner)
        for fname in ("submit", "answer"):
            self._swap(Game, fname, around("shell_depth", getattr(Game, fname), True))

    # ------------------------------------------------------------------------------------------ profile
    def _key(self, code: CodeType, glb: dict[str, Any]) -> tuple[str, str | None]:
        got = self._codes.get(code)
        if got is None:
            mod = glb.get("__name__", "")
            got = (f"{mod}.{code.co_qualname}", None) if mod.startswith(_ENGINE) else ("", None)
            self._codes[code] = got
            if got[0]:
                self.parts[got[0]] = (mod, code.co_qualname)
        return got

    def _profile(self, frame: Any, event: str, arg: Any) -> None:
        if event != "call":
            return
        scope = "turn" if self.turn_depth else "shell" if self.shell_depth else None
        if scope is None:
            return
        name = self._key(frame.f_code, frame.f_globals)[0]
        if not name:
            return
        self.reach[(scope, name)] += 1
        if name in self._track or name.startswith(AUDIT_TEXT):
            back = frame.f_back
            if back is not None:
                self.edges[(scope, self._key(back.f_code, back.f_globals)[0] or back.f_code.co_qualname, name)] += 1

    # ------------------------------------------------------------------------------------------ context
    def __enter__(self) -> Guard:
        for name, entry in self.deny.items():
            self._patch(name, entry)
        self._wrap_scopes()
        if self.record_reach:
            sys.setprofile(self._profile)
        return self

    def __exit__(self, *exc: Any) -> None:
        sys.setprofile(None)
        for undo in reversed(self._undo):
            undo()
        self._undo.clear()

    # ------------------------------------------------------------------------------------------ results
    def reached(self, name: str) -> int:
        return sum(n for (_, q), n in self.reach.items() if q == name)

    def raised(self) -> list[dict[str, Any]]:
        return [h for h in self.hits if h["mode"] == "raise"]
