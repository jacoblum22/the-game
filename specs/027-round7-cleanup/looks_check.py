"""Spec 027's packet check (C12): rebuild each narrated turn's narrator packet with the new builder (spec 024's
`replay_r7.rebuild`, read-only on the saves: each turn works on a scratch copy cut at the end of that turn) and count
the turns whose packet carries a person's look or a thing's description, as played and rebuilt.

    py -3.12 specs/027-round7-cleanup/looks_check.py <save.db> [<save.db> ...]

A person's look: their `detail` and their look-slot `detail.*` facts; a thing's description: `packet.describes`
facts (and `desc`/`look`/`detail` data). Values shorter than 12 characters are not searched (too common to count).
Named lines: the scholar's scar and the doorpost bill (spec 024's live talker). Caveat: a cut save already holds the
entities the narrator itself introduced that turn (written after its call in play), so the rebuilt count can only be
high, never low."""

from __future__ import annotations

import importlib.util
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.dm.packet import CAST_KINDS, THINGS, describes  # noqa: E402
from engine.store.db import Store  # noqa: E402

_spec = importlib.util.spec_from_file_location("replay024", ROOT / "specs" / "024-texture-outcome" / "replay_r7.py")
assert _spec is not None and _spec.loader is not None
replay = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(replay)

NAMED = {"scar": "long scar along the jaw", "bill": ("nailed to the doorpost", "and it asks no questions")}


def _values(save: Path, tmp: Path) -> tuple[list[str], dict[str, list[str]], dict[str, str | None]]:
    """(people's look values, each thing's description values, the turn each thing was created in), from the save's
    final state; a value that is some entity's name (a faction's) is not a description."""
    dst = tmp / "final.db"
    shutil.copy2(save, dst)
    store = Store.open(dst)
    st = store.state
    people: list[str] = []
    things: dict[str, list[str]] = {}
    for e in st.entities.values():
        if e.kind in CAST_KINDS and e.data.get("detail"):
            people.append(str(e.data["detail"]))
        if e.kind in THINGS:
            things.setdefault(e.id, []).extend(str(e.data[k]) for k in ("desc", "look", "detail") if e.data.get(k))
    for f in st.facts.values():
        if isinstance(f.value, str) and describes(st, f.model_dump(mode="json")):
            ent = st.entities.get(f.subject)
            if ent is not None and ent.kind in CAST_KINDS:
                people.append(f.value)
            else:
                things.setdefault(f.subject, []).append(f.value)
    names = {e.name.lower() for e in st.entities.values() if e.name}
    born = {e.payload.entity.id: e.turn_id for e in store.events(types=["entity_created"])}  # type: ignore[attr-defined]
    store.close()
    return ([v for v in dict.fromkeys(people) if len(v) >= 12],
            {k: [v for v in dict.fromkeys(vs) if len(v) >= 12 and v.lower() not in names and " " in v] for k, vs in things.items()},
            born)


def _has(text: str, values: list[str]) -> bool:
    low = text.lower()
    return any(v.lower() in low for v in values)


def main(argv: list[str]) -> int:
    with tempfile.TemporaryDirectory(prefix="r027looks-", ignore_cleanup_errors=True) as t:
        tmp = Path(t)
        for arg in argv:
            save = Path(arg)
            con = sqlite3.connect(f"file:{save.as_posix()}?mode=ro", uri=True)
            turns = [r[0] for r in con.execute("select distinct turn_id from model_calls where role='narrator' "
                                               "order by row_id")]
            con.close()
            people, things, born = _values(save, tmp)
            rows: dict[str, list[int]] = {k: [0, 0] for k in ("a person's look", "a thing's description", *NAMED)}
            per: list[str] = []
            for turn in turns:
                old, new, _ = replay.rebuild(save, turn, tmp)
                # a thing written on mention this turn did not exist yet when play called the narrator
                tv = [v for k, vs in things.items() if born.get(k) != turn for v in vs]
                marks = []
                for i, text in enumerate((old, new)):
                    hits = {"a person's look": _has(text, people), "a thing's description": _has(text, tv),
                            "scar": NAMED["scar"] in text, "bill": any(x in text for x in NAMED["bill"])}
                    for k, v in hits.items():
                        rows[k][i] += int(v)
                    marks.append("".join(k[0] if v else "." for k, v in hits.items() if k in ("scar", "bill"))
                                 + ("P" if hits["a person's look"] else ".") + ("T" if hits["a thing's description"]
                                                                                 else "."))
                per.append(f"{turn} {marks[0]}→{marks[1]}")
            print(f"## {save.name}: {len(turns)} narrated turns")
            print("| turns carrying | as played | rebuilt (spec 027) |\n|---|---|---|")
            for k, (a, b) in rows.items():
                if k in NAMED and not a:
                    continue
                print(f"| {k} | {a}/{len(turns)} | {b}/{len(turns)} |")
            print("per turn (s scar, b bill, P a person's look, T a thing's description; as played → rebuilt):")
            print("  " + "; ".join(per))
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
