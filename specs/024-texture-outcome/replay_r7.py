"""Spec 024: rebuild the round-7 narrator packets with the new builder, and compare them with the packets the round
played with (read-only on the saves: each turn works on a scratch copy cut at the end of that turn).

    py -3.12 specs/024-texture-outcome/replay_r7.py C:/Users/Nelly/Documents/the-game/saves/playtest-20261009-160602-talker.db ...

Per narrated turn: the old packet's VIEW + THIS MESSAGE (as recorded) and a new one built by `narrator.draft` on the
saved state at the end of that turn, with the turn's parts, its beats (rebuilt from the committed frame and its
`frame_resolved` event, or the open pause), and the NPC responses re-run by the new `npc_layer.respond`. The PR-12-10
answer and learned lines are not re-run (they need the Reader's questions), so the new packets carry the willingness
lines in their place. Counts per save: lines that push a habit (any habit text outside the person's background line),
"brought the word", freshness / quote-back blocks, "call them" / "every other screen", and pronoun-neutral template
words beside a person with he/she pronouns. Then the T4 turns (talker inputs 27-28) and P1 (explorer inputs 20-21).
"""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.audit.declare import Passage, sentences_of  # noqa: E402
from engine.dm import narration  # noqa: E402
from engine.dm.adjudication import AdjudicationRecord, BeatEntry, CostEntry, PartEntry, PauseEntry  # noqa: E402
from engine.dm.context import TurnContext  # noqa: E402
from engine.dm.npc_layer import respond  # noqa: E402
from engine.dm.roles import narrator as nr  # noqa: E402
from engine.dm.turn import recent_exchanges  # noqa: E402
from engine.llm.base import Role  # noqa: E402
from engine.llm.offline import ScriptedModel  # noqa: E402
from engine.resolve.pipeline import BeatOutcome  # noqa: E402
from engine.store.db import Store  # noqa: E402
from evals.replay_bench import sections  # noqa: E402

FRESH = ("FRESHNESS", "Details stated lately", "Lines these people")
CALL = ('call them "', "every other screen")  # a label to repeat word for word
NEUTRAL = re.compile(r"in their own (?:words|voice)|their (?:teens|station|morning work|own business|fingers|tongue)|"
                     r"move them|does not know their name|call them|of theirs|themselves by name")


class _Done(Exception):
    pass


def _cut(src: Path, turn: str, tmp: Path) -> Path:
    """A scratch copy of the save holding the events up to the end of `turn` (no snapshot after it)."""
    dst = tmp / f"{turn}.db"
    shutil.copy2(src, dst)
    con = sqlite3.connect(dst)
    try:  # a scratch copy only: its append-only triggers are dropped so the later events can go
        for (name,) in con.execute("select name from sqlite_master where type='trigger'").fetchall():
            con.execute(f"drop trigger {name}")
        last = con.execute("select max(seq) from events where turn_id=?", (turn,)).fetchone()[0]
        con.execute("delete from events where seq > ?", (last,))
        con.execute("delete from snapshots where seq > ?", (last,))
        con.commit()
    finally:
        con.close()
    return dst


def _frames(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    out = {}
    for (pl,) in con.execute("select payload from events where type='frame_committed'"):
        f = json.loads(pl)["frame"]
        out[f["id"]] = f
    return out


def _beats(con: sqlite3.Connection, frames: dict[str, Any], turn: str, rec: dict[str, Any]) -> list[BeatOutcome]:
    resolved = {json.loads(p)["frame_id"]: json.loads(p) for (p,) in con.execute(
        "select payload from events where turn_id=? and type='frame_resolved'", (turn,))}
    pause = rec.get("pause") or {}
    out = []
    for fid in rec.get("beats") or []:
        f = frames.get(fid)
        if f is None:
            continue
        b, gate = f["beat"], f.get("gate") or {}
        r = resolved.get(fid)
        near = pause.get("kind") == "near_miss" and pause.get("frame_id") == fid
        entry = BeatEntry(frame_id=fid, actor=b.get("actor"), targets=[b["target"]] if b.get("target") else [],
                          verb=b.get("verb"), restatement=b.get("restatement") or "",
                          approach_words=f"{gate.get('verb') or gate.get('license')}, {f.get('attribute')}",
                          difficulty_words=str(f.get("tier") or f.get("dc_source") or "").replace("_", " "),
                          rolled=bool(r) or near, degree=(r or {}).get("degree") or ("failure" if near else None),
                          near_miss=bool((r or {}).get("near_miss")) or near,
                          success_at_cost=bool((r or {}).get("success_at_cost_taken")),
                          reach=((r or {}).get("delivered") or {}).get("reach"),
                          costs=[CostEntry(menu_id=c["menu_id"], severity=c.get("severity"), form=c.get("form") or "")
                                 for c in (r or {}).get("costs") or []])
        out.append(BeatOutcome(status="resolved" if r else "paused", entry=entry, frame_id=fid))
    return out


def _purpose(old_msg: str) -> str:
    first = old_msg.strip().splitlines()[0] if old_msg.strip() else ""
    return ("scene_open" if first.startswith("Narrate this turn from the record, then frame")
            else "opening" if first.startswith("The first opening") else "turn")


def rebuild(save: Path, turn: str, tmp: Path) -> tuple[str, str, AdjudicationRecord]:
    """(old VIEW + THIS MESSAGE, new VIEW + THIS MESSAGE, the rebuilt record) for one narrated turn."""
    con = sqlite3.connect(f"file:{save.as_posix()}?mode=ro", uri=True)
    req = con.execute("select request from model_calls where turn_id=? and role='narrator' order by row_id limit 1",
                      (turn,)).fetchone()
    old = dict(sections(str(json.loads(req[0])["packet"])))
    rec_row = json.loads(con.execute("select record from turns where turn_id=?", (turn,)).fetchone()[0])
    frames = _frames(con)
    beats = _beats(con, frames, turn, rec_row)
    con.close()
    store = Store.open(_cut(save, turn, tmp))
    captured: list[Any] = []

    def capture(schema: Any, packet: Any) -> dict[str, Any]:
        captured.append(packet)
        raise _Done

    model = ScriptedModel({Role.NARRATOR: [capture]})
    ctx = TurnContext.for_store(store, model=model, config={"world_judge": False})
    pause = rec_row.get("pause")
    record = AdjudicationRecord(turn_id=turn, pc=next((i for i, e in store.state.entities.items() if e.kind == "pc"),
                                                      None),
                                parts=[PartEntry.model_validate(p) for p in rec_row.get("parts") or []],
                                beats=[b.entry for b in beats],
                                pause=PauseEntry(kind=pause["kind"], frame_id=pause.get("frame_id")) if pause else None)
    try:
        with store.transaction(turn) as tx:
            ctx.tx = tx
            respond(ctx, record, beats)
            nr.draft(ctx, record, player_message=str(rec_row.get("input_verbatim") or ""),
                     exchanges=recent_exchanges(store, turn), purpose=_purpose(old.get("THIS MESSAGE", "")))  # type: ignore[arg-type]
    except _Done:
        pass
    finally:
        ctx.tx = None
        store.close()
    new = captured[0]
    return (f"{old.get('NARRATOR VIEW', '')}\n{old.get('THIS MESSAGE', '')}", f"{new.view}\n{new.message}", record)


def _habits(save: Path) -> list[str]:
    con = sqlite3.connect(f"file:{save.as_posix()}?mode=ro", uri=True)
    out = set()
    for (pl,) in con.execute("select payload from events where type in ('entity_created','fact_set')"):
        for m in re.finditer(r'"habit":\s*"([^"]+)"', pl):
            out.add(re.sub(r"^now and then ", "", m.group(1)))
    con.close()
    return sorted(out)


def _gendered(lines: list[str]) -> list[bool]:
    """Per line: does it speak of a person with he/she pronouns (a `present:` line or record line saying so, or a
    line inside the view block of such a person)."""
    out, cur = [], False
    for ln in lines:
        if re.match(r"^[a-z]+\.[\w.]+: ", ln):  # a view entity block starts
            cur = False
        if re.match(r"^\s+pronouns: (?:he/him|she/her)", ln):
            cur = True
        out.append(cur or bool(re.search(r"\((?:he/him|she/her)", ln)) or " MUST:" in ln)
    return out


def counts(text: str, habits: list[str]) -> dict[str, int]:
    lines = text.splitlines()
    core = [re.sub(r"\b(their|them|themselves|his|her|him|himself|herself)\b", "X", h)[:24] for h in habits]
    norm = [re.sub(r"\b(their|them|themselves|his|her|him|himself|herself)\b", "X", ln) for ln in lines]
    return {"habit outside background": sum(1 for ln, n in zip(lines, norm, strict=True)
                                           if any(c in n for c in core) and not ln.startswith("  background (")),
            "brought the word": sum("brought the word" in ln for ln in lines),
            "freshness / quote-back": sum(any(f in ln for f in FRESH) for ln in lines),
            "call them \"…\" / every other screen": sum(any(c in ln for c in CALL) for ln in lines),
            "pronoun-neutral templates (he/she person)": sum(len(NEUTRAL.findall(ln)) for ln, g in
                                                             zip(lines, _gendered(lines), strict=True) if g)}


def main(argv: list[str]) -> int:
    with tempfile.TemporaryDirectory(prefix="r7replay-", ignore_cleanup_errors=True) as t:
        tmp = Path(t)
        for arg in argv:
            save = Path(arg)
            con = sqlite3.connect(f"file:{save.as_posix()}?mode=ro", uri=True)
            turns = [r[0] for r in con.execute("select distinct turn_id from model_calls where role='narrator' "
                                               "order by row_id")]
            con.close()
            habits = _habits(save)
            tot_old: dict[str, int] = {}
            tot_new: dict[str, int] = {}
            for turn in turns:
                old, new, _ = rebuild(save, turn, tmp)
                for k, v in counts(old, habits).items():
                    tot_old[k] = tot_old.get(k, 0) + v
                for k, v in counts(new, habits).items():
                    tot_new[k] = tot_new.get(k, 0) + v
            print(f"## {save.name}: {len(turns)} narrator packets (habits: {'; '.join(habits)})")
            print("| push (lines) | round 7 as played | rebuilt |\n|---|---|---|")
            for k in tot_old:
                print(f"| {k} | {tot_old[k]} | {tot_new[k]} |")
            print()
            if "talker" in save.name:
                for turn, label in (("turn.12", "input 27 (near-miss pause)"), ("turn.13", "input 28 (succeed and "
                                                                                          "pay taken)")):
                    old, new, rec = rebuild(save, turn, tmp)
                    print(f"### talker {turn}, {label}")
                    for tag, text in (("as played", old), ("rebuilt", new)):
                        must = [ln for ln in text.splitlines() if re.match(r"- R\d", ln) or "has not answered" in ln]
                        print(f"- {tag}:")
                        print("\n".join(f"  {ln[ln.index('Except'):] if 'Except' in ln else ln[:300]}"
                                        for ln in must))
                    print()
            if "explorer" in save.name:
                con = sqlite3.connect(f"file:{save.as_posix()}?mode=ro", uri=True)
                for turn in ("turn.4", "turn.5", "turn.6"):  # inputs 19-21 (input N is turn.(N-15))
                    resp, = con.execute("select response from model_calls where turn_id=? and role='narrator' "
                                        "order by row_id limit 1", (turn,)).fetchone()
                    passage = str(json.loads(resp)["data"]["passage"])
                    delivered, = con.execute("select delivered_verbatim from turns where turn_id=?", (turn,)).fetchone()
                    p = Passage(text=passage)
                    sents = [narration._Sent(decl=s, orig=s.text) for s in sentences_of(p)[0]]
                    now = narration._text(sents, passage)
                    fiction = str(delivered).split("\n\n[")[0]  # the OOF blocks follow the fiction
                    print(f"### explorer {turn} (input {int(turn[5:]) + 15}): paragraph breaks in the model's passage "
                          f"{passage.count(chr(10) * 2)}, delivered in round 7 {fiction.count(chr(10) * 2)}, "
                          f"delivered now {now.count(chr(10) * 2)}; identical to the passage: {now == passage}")
                con.close()
                print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
