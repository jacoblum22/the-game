"""Turn judge (spec 033 R11, constitution VIII.9): measures about the story that a keyword match cannot make.

A Haiku judge reads sampled turns of a save, one call per turn and measure, against a fixed rubric. The engine writes
no `leaks`/`log_only` stats any more; this is where those counts come from. Every count is printed with its
precision, which is only known from hand verdicts: below 20 of them a measure prints "precision unmeasured".

    py -3.12 evals/turn_judge.py run <save.db> [...] [--n 30] [--seed 1] [--offline] [--template out.yaml]
    py -3.12 evals/turn_judge.py report <save.db> [...]        # from the cache only, no model call

Measures (MEASURES): leak (a secret given in the passage), ask (a costly ask: caved / priced / refused with a way
forward / refused), mood (a mood change and whether its cause is in the passage or the log), pronoun (a pronoun that
contradicts the record), absent (a person who is not here speaks or acts).

Verdicts are cached in `evals/baselines/turn_judge/<save>.json` (keyed by turn and measure; a changed rubric drops
the cache; `--offline` stand-ins go to `<save>.offline.json`, which no scorer reads). Hand verdicts: `evals/baselines/turn_judge_hand.yaml`, a list under `verdicts:` of
`{save, turn, measure, judge, hand}` where `judge` is the label the judge gave and `hand` the label you give it (same
labels). `--template` writes the flagged turns of a run in that shape, `hand: null`, for you to fill in.
--offline: the stand-in labels a turn from `fixture` in its packet (else `none`); no model, a harness check only."""

from __future__ import annotations

import hashlib
import json
import random
import sqlite3
import sys
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

HAIKU = "haiku"
MIN_HAND = 20  # hand verdicts a measure needs before its precision is printed
CACHE_DIR = ROOT / "evals" / "baselines" / "turn_judge"
HAND_FILE = ROOT / "evals" / "baselines" / "turn_judge_hand.yaml"
NOISE = {"handler_ran", "handler_skipped", "meta_set", "entity_created", "fact_set", "snapshot"}  # not log lines

# name -> (flagged label, all labels, packet parts it reads, rubric)
MEASURES: dict[str, tuple[str, tuple[str, ...], tuple[str, ...], str]] = {
    "leak": ("leaked", ("none", "leaked"), ("secrets", "passage"),
             "You are given SECRETS (things the player has not learned) and a PASSAGE of a tabletop RPG. Label "
             "`leaked` when the passage tells the player what a secret says: its substance, even in other words or "
             "in a hint that makes it plain. Label `none` when the passage only touches the same people or places, "
             "mentions that someone hides something, or shows nervousness without the content."),
    "ask": ("caved", ("none", "caved", "priced", "refused_way", "refused"), ("player", "log", "passage"),
            "A costly ask is a request that costs the asked person something real: danger, a lie, their standing, a "
            "loyalty, a risk to others. Small favours and questions are not costly. Judge the player's turn and the "
            "passage. Label `none` if there is no costly ask. Otherwise label how the asked person answers: `caved` "
            "(does it or agrees outright, with nothing asked in return and no real hesitation), `priced` (agrees "
            "only for a price or on a condition, which the passage states), `refused_way` (says no but offers "
            "another way forward, a lead, an alternative or a condition to come back with), `refused` (a flat no "
            "or a deflection). A priced deal is never a cave."),
    "mood": ("uncaused", ("none", "caused", "uncaused"), ("earlier", "log", "passage"),
             "Label whether a named person's attitude toward the player clearly changes in this passage (warmer, "
             "colder, trusting, hostile, afraid) compared with how EARLIER showed them. `none` if nobody's attitude "
             "changes. `caused` if it changes and the cause is something said or done in the PASSAGE or recorded in "
             "the LOG (a gift, a threat, a wound, news, an act of the player's). `uncaused` if it changes and "
             "neither the passage nor the log gives a cause."),
    "pronoun": ("slip", ("none", "slip"), ("cast", "passage"),
                "CAST lists each person's pronouns on record. Label `slip` if the passage refers to a person with a "
                "pronoun that differs from their record (or switches pronouns for one person within the passage). "
                "The player's own 'you' is never a slip. Label `none` otherwise, including people not on the cast."),
    "absent": ("absent_speaks", ("none", "absent_speaks"), ("cast", "player", "log", "passage"),
               "CAST says who is PRESENT in the scene and who is elsewhere. Label `absent_speaks` if the passage "
               "has someone listed as elsewhere speak, act in the scene or answer the player as though they were "
               "here (a person only remembered, quoted from the past or spoken about does not count; someone who "
               "arrives in the passage or the LOG does not count). Otherwise label `none`."),
}
PART_TITLES = {"secrets": "SECRETS", "passage": "THE PASSAGE", "player": "THE PLAYER'S TURN", "log": "THE LOG",
               "earlier": "EARLIER", "cast": "CAST"}
SYSTEM = ("You label one excerpt of a tabletop RPG session against a fixed rubric. Read only what is given. Answer "
          "with the label and a one-sentence reason. When unsure between a flagged label and `none`, choose `none`.\n\n")
Judge = Callable[[str, dict[str, Any]], dict[str, Any]]


def rubric_hash() -> str:
    return hashlib.sha1(json.dumps(MEASURES, sort_keys=True).encode()).hexdigest()[:10]


def render(measure: str, packet: dict[str, Any]) -> str:
    return "\n\n".join(f"{PART_TITLES[k]}:\n{packet.get(k) or '(none)'}" for k in MEASURES[measure][2])


def live_judge(measure: str, packet: dict[str, Any]) -> dict[str, Any]:
    from evals.playtest import ask_claude

    flagged, labels, _, rubric = MEASURES[measure]
    schema = {"type": "object", "properties": {"label": {"type": "string", "enum": list(labels)},
                                               "why": {"type": "string"}}, "required": ["label", "why"]}
    data, _ = ask_claude(SYSTEM + rubric, render(measure, packet), schema, HAIKU)
    return {"label": data["label"] if data.get("label") in labels else "none", "why": str(data.get("why", ""))}


def offline_judge(measure: str, packet: dict[str, Any]) -> dict[str, Any]:
    return {"label": (packet.get("fixture") or {}).get(measure, "none"), "why": "offline stand-in"}


def verdict(measure: str, packet: dict[str, Any], *, offline: bool = False) -> dict[str, Any]:
    """One verdict for a packet already built (npc_agency uses this directly)."""
    return (offline_judge if offline else live_judge)(measure, packet)


# ------------------------------------------------------------------------------------------------ a save to packets


def _clip(s: Any, n: int) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


class Save:
    """A save read once, read-only: its events, its engine turns, and the packet of any turn."""

    def __init__(self, path: Path):
        self.path = path
        db = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
        self.events = [(s, t, ty, json.loads(p)) for s, t, ty, p in db.execute(
            "select seq, turn_id, type, payload from events order by seq")]
        self.turns = [(t, inp or "", json.loads(rec or "{}"), out or "") for t, inp, rec, out in db.execute(
            "select turn_id, input_verbatim, record, delivered_verbatim from turns where turn_id like 'turn.%'")]
        db.close()

    def eligible(self) -> list[str]:  # the player's inputs, not the opening or the session close
        return [t for t, inp, _, out in self.turns if not inp.startswith("(") and out.strip()]

    def _upto(self, turn: str) -> list[tuple[int, str | None, str, dict[str, Any]]]:
        end = max((s for s, t, _, _ in self.events if t == turn), default=0)
        return [e for e in self.events if e[0] <= end]

    def packet(self, turn: str) -> dict[str, Any]:
        evs = self._upto(turn)
        ents: dict[str, dict[str, Any]] = {}
        where: dict[str, str] = {}
        cases: dict[str, Any] = {}
        for _, _, ty, p in evs:
            if ty == "entity_created" and p.get("entity"):
                e = p["entity"]
                ents[e["id"]] = {"name": e.get("name") or e["id"], "kind": e.get("kind"),
                                 "pr": (e.get("data") or {}).get("pronouns"), "secrets": (e.get("data") or {}).get("secrets") or []}
            elif ty == "position_set" and p.get("entity"):
                where[p["entity"]] = p.get("location") or ""
            elif ty == "meta_set" and p.get("key") == "world.cases":
                cases = p.get("value") or {}
        pc = next((i for i, e in ents.items() if e["kind"] == "pc"), None)
        here = where.get(pc or "", "?")
        people = {i: e for i, e in ents.items() if e["kind"] == "npc"}

        def line(i: str) -> str:
            return f"{people[i]['name']} ({people[i]['pr'] or 'pronouns not on record'})"

        present = [line(i) for i in people if where.get(i) == here]
        away = [line(i) for i in people if where.get(i) != here][:40]
        secrets = [f"{e['name']} {s.get('text', s) if isinstance(s, dict) else s}" for e in people.values()
                   for s in e["secrets"]]
        secrets += [str(p["value"]) for _, _, ty, p in evs if ty == "fact_set" and p.get("visibility") == "sealed"
                    and isinstance(p.get("value"), str) and len(p["value"]) > 20]
        secrets += [str(n["fact"]) for c in cases.values() for n in c.get("nodes", []) if not n.get("found")]
        i = next(k for k, t in enumerate(self.turns) if t[0] == turn)
        _, inp, rec, out = self.turns[i]
        log = [f"{ty}: {_clip(json.dumps(p, ensure_ascii=False), 160)}" for _, t, ty, p in self.events
               if t == turn and ty not in NOISE][:25]
        tools = ((rec.get("screen") or {}).get("dm_tools") or {}).get("tools") or []
        log += [f"tool {x.get('tool')}: {_clip(x.get('out', ''), 100)}" for x in tools][:15]
        return {"player": inp, "passage": out, "log": "\n".join(log),
                "earlier": "\n".join(_clip(o, 600) for _, _, _, o in self.turns[max(0, i - 2): i] if o),
                "cast": f"PRESENT: {', '.join(present) or 'nobody'}\nELSEWHERE: {', '.join(away) or 'nobody'}",
                "secrets": "\n".join(f"- {_clip(s, 240)}" for s in secrets[:30])}


# ------------------------------------------------------------------------------------------------ run, cache, report


def cache_path(save: Path, cache_dir: Path | None = None, offline: bool = False) -> Path:
    """Stand-in verdicts go to a separate `.offline.json` file, so they can never be read as the judge's."""
    return (cache_dir or CACHE_DIR) / f"{save.stem}{'.offline' if offline else ''}.json"


def cached(save: Path, cache_dir: Path | None = None, offline: bool = False) -> dict[str, dict[str, Any]]:
    """The save's cached verdicts, `"turn|measure" -> {label, why}`; empty if none or the rubric changed since."""
    p = cache_path(save, cache_dir, offline)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    return dict(data["verdicts"]) if data.get("rubric") == rubric_hash() else {}


def sample(turns: list[str], n: int, seed: int, save: str) -> list[str]:
    return sorted(random.Random(f"{seed}:{save}").sample(turns, min(n, len(turns))), key=turns.index)


def run_save(path: Path, *, n: int = 30, seed: int = 1, offline: bool = False, cache_dir: Path | None = None,
             fixtures: dict[str, dict[str, str]] | None = None) -> dict[str, dict[str, Any]]:
    """Judge a seeded sample of the save's turns on every measure (cached, so a re-run only fills gaps)."""
    save = Save(path)
    done = cached(path, cache_dir, offline)
    todo = [(t, m) for t in sample(save.eligible(), n, seed, path.stem) for m in MEASURES if f"{t}|{m}" not in done]
    packets = {t: save.packet(t) for t in {t for t, _ in todo}}
    for t, f in (fixtures or {}).items():
        if t in packets:
            packets[t]["fixture"] = f
    with ThreadPoolExecutor(1 if offline else 4) as pool:
        for (t, m), v in zip(todo, pool.map(lambda x: verdict(x[1], packets[x[0]], offline=offline), todo), strict=True):
            done[f"{t}|{m}"] = v
    p = cache_path(path, cache_dir, offline)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"rubric": rubric_hash(), "verdicts": done}, indent=1, ensure_ascii=False), encoding="utf-8")
    return done


def load_hand(path: Path | None = None) -> list[dict[str, Any]]:
    p = path or HAND_FILE
    rows = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("verdicts") if p.exists() else None
    return [r for r in rows or [] if r.get("hand") is not None]


def precision(measure: str, hand: list[dict[str, Any]]) -> str:
    """"precision 0.75 (n=22 hand-checked)", or "precision unmeasured" under MIN_HAND hand verdicts. Precision is the
    share of the judge's flagged turns among those verdicts that the hand agreed with."""
    mine = [r for r in hand if r.get("measure") == measure]
    flagged = [r for r in mine if r.get("judge") == MEASURES[measure][0]]
    if len(mine) < MIN_HAND:
        return f"precision unmeasured ({len(mine)} of {MIN_HAND} hand verdicts)"
    if not flagged:
        return f"precision unmeasured (no flagged turn among {len(mine)} hand verdicts)"
    ok = sum(r["hand"] == r["judge"] for r in flagged)
    return f"precision {ok / len(flagged):.2f} ({ok}/{len(flagged)} flagged confirmed, n={len(mine)} hand-checked)"


def count_line(measure: str, verdicts: list[dict[str, Any]], hand: list[dict[str, Any]]) -> str:
    labels = MEASURES[measure][1]
    by = {lab: sum(v["label"] == lab for v in verdicts) for lab in labels if lab != "none"}
    flagged = MEASURES[measure][0]
    return (f"{measure}: {by[flagged]} {flagged} of {len(verdicts)} judged "
            f"({', '.join(f'{k} {v}' for k, v in by.items())}); {precision(measure, hand)}")


def report(results: dict[str, dict[str, dict[str, Any]]], hand: list[dict[str, Any]] | None = None) -> str:
    """`results`: save stem -> cached verdicts. One line per measure over all saves."""
    hand = load_hand() if hand is None else hand
    allv = [v for r in results.values() for v in r.values()]
    out = []
    for m in MEASURES:
        vs = [v for r in results.values() for k, v in r.items() if k.endswith(f"|{m}")]
        out.append(count_line(m, vs, hand) if vs else f"{m}: not judged")
    return "\n".join(out) if allv else "\n".join(f"{m}: not judged" for m in MEASURES)


def template(results: dict[str, dict[str, dict[str, Any]]]) -> str:
    rows = [{"save": s, "turn": k.split("|")[0], "measure": k.split("|")[1], "judge": v["label"], "hand": None}
            for s, r in results.items() for k, v in r.items() if v["label"] == MEASURES[k.split("|")[1]][0]]
    return yaml.safe_dump({"verdicts": rows}, sort_keys=False)


def main(argv: list[str]) -> int:
    def opt(name: str, default: Any = None) -> Any:
        return argv[argv.index(name) + 1] if name in argv else default

    saves = [Path(a) for i, a in enumerate(argv[1:], 1) if not a.startswith("--")
             and argv[i - 1] not in ("--n", "--seed", "--template")]
    if not argv or argv[0] not in ("run", "report") or not saves:
        print(__doc__)
        return 2
    if argv[0] == "run":
        results = {p.stem: run_save(p, n=int(opt("--n", 30)), seed=int(opt("--seed", 1)), offline="--offline" in argv)
                   for p in saves}
    else:
        results = {p.stem: cached(p, offline="--offline" in argv) for p in saves}
    print(report(results))
    if opt("--template"):
        Path(opt("--template")).write_text(template(results), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
