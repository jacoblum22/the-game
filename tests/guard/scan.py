"""Spec 033 P0: the static half of the VIII.9 guard (plan 3, R12).

`scan(functions)` parses the engine source and reports, per function, the places that read natural-language text with
words: a call into `re`, a use of a module-level compiled pattern, a use of a module-level collection of three or more
string literals (a word list). A hit is keyed `module:function:rule:name` (no line numbers, so edits elsewhere do not
move it). The functions scanned are every function of `engine/dm/dm_tools.py` and `engine/dm/dm_world.py`, plus every
function named in `tests/guard/reached.txt` (the functions the census games reach during a dm-tools turn; regenerate
with `PYTHONUTF8=1 py -3.12 -m tests.guard.census reached`).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "engine"
REACHED = Path(__file__).with_name("reached.txt")
ALWAYS = ("engine.dm.dm_tools", "engine.dm.dm_world")  # every function in these is scanned
EXCLUDED = ("engine.llm.offline",)  # the offline model stand-in (a test double, never the game's own reading)
MIN_WORDS = 3  # a module-level collection of this many string literals is a word list


def module_name(path: Path) -> str:
    return ".".join(path.relative_to(ROOT).with_suffix("").parts).removesuffix(".__init__")


def toplevel(qualname: str) -> str:
    """`f.<locals>.g`, `f.<locals>.<genexpr>` -> `f`: the def a profile frame belongs to."""
    return qualname.split(".<locals>.")[0]


@dataclass(frozen=True)
class Hit:
    module: str
    func: str
    rule: str  # "re" | "pattern" | "words"
    name: str

    @property
    def key(self) -> str:
        return f"{self.module}:{self.func}:{self.rule}:{self.name}"


def _is_re_compile(node: ast.AST | None) -> bool:
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "compile"
            and isinstance(node.func.value, ast.Name) and node.func.value.id == "re")


def _strings(node: ast.AST | None) -> int:
    """How many string literals a set/tuple/list/dict display (or `frozenset(...)`) holds."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("frozenset", "set", "tuple") \
            and len(node.args) == 1:
        node = node.args[0]
    if isinstance(node, ast.Dict):
        elts: list[ast.AST | None] = list(node.keys)
    elif isinstance(node, (ast.Set, ast.Tuple, ast.List)):
        elts = list(node.elts)
    else:
        return 0
    return sum(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in elts)


class Module:
    """One parsed engine module: its module-level patterns and word lists, its imports of such, its functions."""

    def __init__(self, path: Path | str, source: str | None = None) -> None:
        """`path`: an engine file; or, with `source`, a module name for source text (the planted-call tests)."""
        self.name = path if isinstance(path, str) else module_name(path)
        self.tree = ast.parse(source if source is not None else Path(path).read_text(encoding="utf-8"))
        self.patterns: set[str] = set()
        self.words: set[str] = set()
        self.imports: list[tuple[str, str, str]] = []  # (local name, source module, source name)
        for node in self.tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in targets:
                    if isinstance(t, ast.Name):
                        if _is_re_compile(value):
                            self.patterns.add(t.id)
                        elif _strings(value) >= MIN_WORDS:
                            self.words.add(t.id)
        self.has_re = any(isinstance(n, ast.Import) and any(a.name == "re" for a in n.names)
                          for n in ast.walk(self.tree))
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("engine"):
                self.imports += [(a.asname or a.name, node.module, a.name) for a in node.names]

    def functions(self) -> dict[str, ast.AST]:
        """Top-level defs and methods (nested defs belong to their enclosing def)."""
        out: dict[str, ast.AST] = {}

        def walk(body: list[ast.stmt], prefix: str) -> None:
            for n in body:
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out[prefix + n.name] = n
                elif isinstance(n, ast.ClassDef):
                    walk(n.body, prefix + n.name + ".")

        walk(self.tree.body, "")
        return out


def load_modules() -> dict[str, Module]:
    return {m.name: m for m in (Module(p) for p in sorted(ENGINE.rglob("*.py")))}


def reached_functions() -> dict[str, set[str]]:
    """module -> top-level function names, from `reached.txt` ("engine.mod.func" or "engine.mod.Class.method")."""
    out: dict[str, set[str]] = {}
    if REACHED.exists():
        for line in REACHED.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                mod, _, func = line.partition(" ")
                out.setdefault(mod, set()).add(func)
    return out


def scan(mods: dict[str, Module] | None = None, reached: dict[str, set[str]] | None = None) -> list[Hit]:
    mods = mods or load_modules()
    reached = reached_functions() if reached is None else reached
    hits: list[Hit] = []
    for name, mod in mods.items():
        if name in EXCLUDED:
            continue
        funcs = mod.functions()
        wanted = set(funcs) if name in ALWAYS else reached.get(name, set())
        for fname in sorted(wanted & set(funcs)):
            hits += _scan_function(mod, fname, funcs[fname], mods)
    return hits


def _scan_function(mod: Module, fname: str, fn: ast.AST, mods: dict[str, Module]) -> list[Hit]:
    imports = {local: (src, orig) for local, src, orig in mod.imports}  # whole-module scan: function-level ones too
    found: dict[tuple[str, str], None] = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) \
                and node.func.value.id == "re" and mod.has_re:
            found[("re", node.func.attr)] = None
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id in mod.patterns:
                found[("pattern", node.id)] = None
            elif node.id in mod.words:
                found[("words", node.id)] = None
            elif node.id in imports:
                src, orig = imports[node.id]
                other = mods.get(src)
                if other is not None and orig in other.patterns:
                    found[("pattern", f"{src.removeprefix('engine.')}.{orig}")] = None
                elif other is not None and orig in other.words:
                    found[("words", f"{src.removeprefix('engine.')}.{orig}")] = None
    return [Hit(mod.name, fname, rule, name) for rule, name in found]


if __name__ == "__main__":  # python -m tests.guard.scan: the hits, one per line
    for h in scan():
        print(h.key)
