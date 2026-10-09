"""Spec 021 measurements on the round-6 saves (read-only; the saves are gitignored). Output: measure-output.txt.

    py -3.12 specs/021-testimony-answers/measure.py            # offline: settlement triggers, speaker cards
    py -3.12 specs/021-testimony-answers/measure.py --haiku    # also re-runs the claim call on Haiku (30 calls)

1. Settlement per turn: each recorded Reader call, state projected to just before its turn; before = the Reader
   named `rests_on` (the recorded response); after = `testimony.triggered` over the recorded beats, with every record
   open that this replay has not settled.
2. Claims: the 30 recorded testimony calls; before = the recorded response; after (--haiku) = the new claim call on
   the same record and state. Lost subject = the subject resolves to no entity ("world"); garbled = an id in the
   claim, a question stored as a claim, or a pronoun that contradicts the speaker's or subject's recorded one.
3. Speaker cards: absent people named on a card, with or without their pronouns (recorded packet vs rebuilt card);
   the bond on a bonded NPC's card.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.data.loader import load_rules  # noqa: E402
from engine.dm import testimony as tm  # noqa: E402
from engine.dm.packet import speaker_card  # noqa: E402
from engine.retrieve.scene import resolve_names  # noqa: E402
from engine.store.events import Event, Timestamp  # noqa: E402
from engine.store.projection import WorldState, project  # noqa: E402
from engine.store.views import display_name  # noqa: E402

SAVES = Path("C:/Users/Nelly/Documents/the-game/saves")
RUNS = ["192926-talker", "192946-fighter", "214013-talker", "214033-fighter", "232941-talker", "233000-fighter"]
OUT: list[str] = []


def say(*a: Any) -> None:
    OUT.append(" ".join(str(x) for x in a))
    print(*a)


def con(run: str) -> sqlite3.Connection:
    c = sqlite3.connect(f"file:{(SAVES / f'playtest-20261008-{run}.db').as_posix()}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    return c


def events(c: sqlite3.Connection) -> list[Event]:
    return [Event(seq=r["seq"], branch_id=r["branch_id"], turn_id=r["turn_id"], beat_id=r["beat_id"],
                  game_time=Timestamp.model_validate_json(r["game_time"]) if r["game_time"] else None,
                  type=r["type"], payload=json.loads(r["payload"]), source=r["source"], rule_id=r["rule_id"],
                  schema_ver=r["schema_ver"]) for r in c.execute("SELECT * FROM events ORDER BY seq")]


def before_turn(evs: list[Event], c: sqlite3.Connection, turn: str) -> WorldState:
    row = c.execute("SELECT MIN(seq) FROM events WHERE turn_id = ?", (turn,)).fetchone()[0]
    cut = row - 1 if row is not None else evs[-1].seq
    return project(e for e in evs if (e.seq or 0) <= cut)


def reopen(st: WorldState, settled: set[str]) -> None:
    cur = dict(st.meta.get(tm.SAID) or {})
    cur["records"] = [dict(r, settled=True if r["id"] in settled else None) for r in cur.get("records") or []]
    st.meta[tm.SAID] = cur


def _packet(request: str | None) -> str:
    req = json.loads(request or "{}") or {}
    return str(req.get("packet") or req.get("contents") or "")  # the Claude CLI's packet, or Gemini's contents


# ------------------------------------------------------------------------------------------- 1. settlement


def settlement() -> None:
    say("## 1. Settlement per turn (Reader calls with testimony open)")
    tot = {"offered": 0, "before": 0, "after": 0, "after_ids": 0}
    for run in RUNS:
        c = con(run)
        evs = events(c)
        done: set[str] = set()
        n = {"offered": 0, "before": 0, "after": 0}
        rows = c.execute("SELECT turn_id, request, response FROM model_calls WHERE role = 'reader' ORDER BY row_id")
        for r in rows:
            if not r["turn_id"] or not r["response"]:
                continue
            data = (json.loads(r["response"]) or {}).get("data") or {}
            st = before_turn(evs, c, r["turn_id"])
            reopen(st, done)
            if not [x for x in tm.records(st) if x.get("settled") is None and x.get("speaker")]:
                continue
            n["offered"] += 1
            n["before"] += data.get("rests_on") not in (None, "none")
            beats = [SimpleNamespace(target=b.get("target"), assertion=b.get("assertion")) for b in data.get("beats")
                     or []]
            fired = tm.triggered(st, beats)
            for sid in fired:
                rec = tm.get(st, sid) or {}
                via = [f"target {b.target}" for b in beats if tm.triggered(st, [SimpleNamespace(
                    target=b.target, assertion=None)]) == [sid]] or [f"premise \"{b.assertion}\"" for b in beats
                                                                       if b.assertion]
                say(f"    {run} {r['turn_id']}: settles {sid} \"{str(rec.get('words'))[:70]}\" via {via[:1]}")
            n["after"] += bool(fired)
            done |= set(fired)
            tot["after_ids"] += len(fired)
        say(f"  {run}: offered {n['offered']}, before (rests_on) {n['before']}, after {n['after']}")
        for k in n:
            tot[k] += n[k]
    say(f"  TOTAL: before {tot['before']}/{tot['offered']} ({100 * tot['before'] / max(1, tot['offered']):.0f}%), "
        f"after {tot['after']}/{tot['offered']} ({100 * tot['after'] / max(1, tot['offered']):.0f}%), "
        f"records settled after {tot['after_ids']}")


# ------------------------------------------------------------------------------------------- 2. claims

_ID = re.compile(r"\b(?:pc|npc|loc|obj|item|fact)\.[a-z_]")
_HE, _SHE = re.compile(r"\b(he|him|his|himself)\b", re.I), re.compile(r"\b(she|her|hers|herself)\b", re.I)


def _flip(st: WorldState, ids_: list[str], text: str) -> bool:
    for i in ids_:
        p = str((st.entities[i].data.get("pronouns") or "") if i in st.entities else "")
        if p.startswith("she") and _HE.search(text) and not _SHE.search(text):
            return True
        if p.startswith("he") and _SHE.search(text) and not _HE.search(text):
            return True
    return False


def judge(st: WorldState, rec: dict[str, Any], c: dict[str, str], new: bool) -> dict[str, bool]:
    kind = c.get("kind", "claim") if new else "claim"
    subject = tm._subject(st, c.get("subject") or "") if new else (c["subject"] if c["subject"] in st.entities
                                                                    else "world")
    own = subject == rec["speaker"] and bool(tm._OWN_WILL.match(c.get("predicate") or ""))
    written = kind == "claim" and bool(c.get("predicate")) and not (new and own)
    text = f"{c.get('subject')} {c.get('predicate')} {c.get('value')}"
    said = f"{c.get('predicate')} {c.get('value')}"  # the old prompt asked for an id as the subject: not garbled
    refusal = bool(re.match(r"^(will|won'?t|would|refuses?|shall)\b", c.get("predicate") or "", re.I)) and \
        subject == rec["speaker"]
    question = bool(re.match(r"^(asks|wonders|questions)\b", c.get("predicate") or "", re.I))
    return {"written": written, "lost": written and subject == "world",
            "garbled": written and (bool(_ID.search(said)) or question or _flip(st, [rec["speaker"], subject], text)),
            "refusal_stored": written and refusal, "guard": new and kind == "claim" and own}


def claims(haiku: bool) -> None:
    say("## 2. Claims (the recorded testimony calls)")
    model = None
    if haiku:
        sys.path.insert(0, str(ROOT / "evals"))
        from evals.playtest import ClaudeModel

        model = ClaudeModel("haiku")
    rules = load_rules()
    old = {"n": 0, "written": 0, "lost": 0, "garbled": 0, "refusal_stored": 0}
    new = {"n": 0, "written": 0, "lost": 0, "garbled": 0, "refusal_stored": 0, "guard": 0}
    kinds: dict[str, int] = {}
    for run in RUNS:
        c = con(run)
        evs = events(c)
        for r in c.execute("SELECT turn_id, request, response FROM model_calls WHERE role = 'testimony' ORDER BY row_id"):
            m = re.search(r'said: "(.*)"', _packet(r["request"]))
            st = before_turn(evs, c, r["turn_id"])
            rec = next((x for x in reversed(tm.records(st)) if m and x["words"].startswith(m.group(1)[:40])), None)
            if rec is None:
                say(f"  {run} {r['turn_id']}: no record for {m.group(1)[:40] if m else '?'}")
                continue
            got = (json.loads(r["response"]) or {}).get("data") or {}
            j = judge(st, rec, got, False)
            old["n"] += 1
            for k in j:
                if k in old:
                    old[k] += j[k]
            if model is None:
                say(f"  {run} {r['turn_id']} \"{rec['words'][:50]}\" -> {got}"
                    f"{' LOST' if j['lost'] else ''}{' GARBLED' if j['garbled'] else ''}"
                    f"{' REFUSAL' if j['refusal_stored'] else ''}")
                continue
            store = SimpleNamespace(turn=lambda tid, c=c: (lambda row: SimpleNamespace(
                input_verbatim=row[0], delivered_verbatim=row[1] or "") if row else None)(
                c.execute("SELECT input_verbatim, delivered_verbatim FROM turns WHERE turn_id = ?", (tid,)).fetchone()))
            ctx = SimpleNamespace(need_tx=lambda st=st: SimpleNamespace(state=st), rules=rules, model=model,
                                  store=store, turn_id=None, record_call=None)
            out = tm._claim(ctx, rec)
            kinds[out["kind"]] = kinds.get(out["kind"], 0) + 1
            jn = judge(st, rec, out, True)
            new["n"] += 1
            for k in jn:
                new[k] += jn[k]
            say(f"  {run} {r['turn_id']} \"{rec['words'][:60]}\"\n     old {got}\n     new {out} -> "
                f"{'written' if jn['written'] else 'nothing written'}{' LOST' if jn['lost'] else ''}"
                f"{' GARBLED' if jn['garbled'] else ''}")
    say(f"  BEFORE: {old}")
    if model is not None:
        say(f"  AFTER (Haiku): {new}; kinds {kinds}")


# ------------------------------------------------------------------------------------------- 3. cards


def cards() -> None:
    say("## 3. Speaker cards (absent people named on a card: pronouns shown; bond on a bonded NPC's card)")
    tot = {"named": 0, "old": 0, "new": 0, "bonded": 0, "bond_old": 0, "bond_new": 0}
    for run in RUNS:
        c = con(run)
        evs = events(c)
        for r in c.execute("SELECT turn_id, request FROM model_calls WHERE role = 'narrator' AND attempt = 0"):
            packet = _packet(r["request"])
            for m in re.finditer(r"SPEAKER CARD for ([^\n(]+?) \(", packet):
                st = before_turn(evs, c, r["turn_id"])
                npc = next((i for i, e in st.entities.items() if e.kind == "npc"
                            and display_name(st, i) == m.group(1).strip()), None)
                if npc is None:
                    continue
                old_card = packet[m.start():].split("\n\n")[0]
                new_card = "\n".join(speaker_card(st, npc))
                here = set(st.scene.cast_present if st.scene else [])
                pc = next((i for i, e in st.entities.items() if e.kind == "pc"), None)
                for p in resolve_names(st, old_card):
                    e = st.entities.get(p)
                    if p in (npc, pc) or p in here or e is None or e.kind not in ("npc", "companion"):
                        continue
                    pro, name = str(e.data.get("pronouns") or ""), display_name(st, p)
                    if not pro:
                        continue
                    tot["named"] += 1
                    tot["old"] += any(name in ln and pro in ln for ln in packet.splitlines())
                    tot["new"] += any(name in ln and pro in ln for ln in new_card.splitlines())
                bonded = any(f.predicate.startswith("bond.") and isinstance(f.value, dict) and f.value.get("npc") == npc
                             for f in st.facts.values())
                if bonded:
                    tot["bonded"] += 1
                    tot["bond_old"] += "your friend" in old_card or "your " in old_card.split("\n")[0]
                    tot["bond_new"] += "your " in new_card.split("\n")[0]
    say(f"  absent people named on cards: {tot['named']}; pronouns in the recorded packet {tot['old']}, on the new card"
        f" {tot['new']}")
    say(f"  bonded NPC cards: {tot['bonded']}; bond shown before {tot['bond_old']}, after {tot['bond_new']}")


if __name__ == "__main__":
    settlement()
    claims("--haiku" in sys.argv)
    cards()
    (Path(__file__).parent / ("measure-output-haiku.txt" if "--haiku" in sys.argv else "measure-output.txt")
     ).write_text("\n".join(OUT) + "\n", encoding="utf-8")
