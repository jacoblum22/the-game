"""Spec 024's measures over recorded games (read-only); also the repetition scan 12.14.11 logs (a measure run on
saves, never a gate; `pacing.yaml#narration.freshness.repetition_scan: log_only`).

    py -3.12 specs/024-texture-outcome/measure.py <save.db> [<save.db> ...]

Per save:
- **habit / look per NPC**: of the turns in which a person speaks (their `said` records), how many deliveries show
  their recorded habit or look (any of its distinctive word stems, listed). Round 7: the habit in 16 of 21.
- **image carry-over** (R7-I1's measure): deliveries sharing 2+ content bigrams with the one before, quotes and names
  removed. Round 7: 57%.
- **repetition scan**: openings and closings (first and last sentence's first four content words) repeated within the
  last 10 deliveries.
- **code sentences leaked**: deliveries holding a code-written sentence or label.
- **pronoun drift**: the claim log's pronoun-check hits, and candidate sentences that name exactly one he/she person
  and call them "they" (for review by hand: plural "they" is common).
- **speech attribution**: candidate quotes whose own sentence names someone other than the side list's speaker, or
  an untagged quote right after a sentence about someone else (for review by hand).
- **first draft, calls**: spec 019's measures (first draft delivered, narrator calls per narrated turn) and all model
  calls per narrated turn.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.audit import text as atx  # noqa: E402

_Q = re.compile(r"[\"“]([^\"”“]*)[\"”]")
_STOP = {"while", "when", "before", "anything", "everything", "important", "everyone", "about", "their", "theirs",
         "themselves", "always", "across", "under", "hand", "hands", "head", "eyes", "face", "with", "from", "into",
         "every", "never", "outright", "slightly", "constantly", "then", "now", "says", "calls", "speaks", "brings",
         "gets", "name", "uses", "tells", "thinking"}  # words any delivery has: never a habit's mark
CODE = ("brought the word", "the matter at hand", "officer of The", "folk say it is only the beginning",
        "asks no questions", "as every other screen")
SPEECH_VERB = re.compile(r"\b(says|said|asks|asked|adds|answers|replies|mutters|murmurs|whispers|calls|snaps|"
                         r"growls|grunts|sighs|shouts|laughs)\b", re.I)


def _fiction(text: str) -> str:
    """The delivered fiction (the OOF blocks follow it)."""
    return (text or "").split("\n\n[")[0].strip()


def stems(text: str) -> list[str]:
    return sorted({w[:4] for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= 4 and w not in _STOP})


def _sents(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?”\"])\s+", text) if s.strip()]


def _bigrams(text: str, names: list[str]) -> set[tuple[str, str]]:
    t = _Q.sub(" ", text)
    for n in names:
        t = re.sub(re.escape(n), " ", t, flags=re.I)
    ws = [w for w in re.findall(r"[a-z']+", t.lower()) if w in atx.content(w) or len(w) > 3]
    ws = [w for w in ws if atx.content(w)]
    return set(zip(ws, ws[1:], strict=False))


def _people(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    """npc id -> {name, label, pronouns, habit, look} from the event log (seeded and generated)."""
    out: dict[str, dict[str, Any]] = {}
    for typ, pl in con.execute("select type, payload from events where type in ('entity_created','fact_set')"):
        p = json.loads(pl)
        if typ == "entity_created":
            e = p.get("entity") or {}
            if e.get("kind") not in ("npc", "companion"):
                continue
            d = e.get("data") or {}
            v = d.get("voice") or {}
            out[e["id"]] = {"name": e.get("name") or "", "role": str(d.get("role") or ""),
                            "pronouns": str(d.get("pronouns") or ""),
                            "habit": str(v.get("habit") or "") if isinstance(v, dict) else "",
                            "look": str(d.get("detail") or "")}
        elif p.get("predicate") == "voice" and p.get("subject") in out and isinstance(p.get("value"), dict):
            out[p["subject"]]["habit"] = str(p["value"].get("habit") or "")
    return out


def measures(path: Path) -> list[str]:
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    people = _people(con)
    names = [n for p in people.values() for n in (p["name"], p["name"].split()[0] if p["name"] else "") if len(n) > 2]
    rows = []
    for tid, rec_json in con.execute("select turn_id, record from turns order by rowid"):
        rec = json.loads(rec_json or "{}")
        versions = rec.get("draft_versions") or []
        if versions and versions[0].get("kind") == "draft":
            rows.append((tid, rec))
    calls = Counter(r[0] for r in con.execute("select turn_id from model_calls"))
    ncalls = {t: n for t, n in con.execute("select turn_id, count(distinct call_id) from model_calls "
                                           "where role='narrator' group by turn_id")}
    con.close()
    out = [f"## {path.name}: {len(rows)} narrated turns"]
    # habit / look per NPC
    for pid, p in people.items():
        speaking = [(tid, _fiction(r.get("delivered_verbatim") or "")) for tid, r in rows
                    if any(s.get("speaker") == pid for s in r.get("said") or [])]
        if not speaking:
            continue
        for kind in ("habit", "look"):
            st = stems(re.sub(r"^now and then ", "", p[kind]))
            if not st:
                continue
            hit = [tid for tid, f in speaking if any(re.search(rf"\b{s}", f.lower()) for s in st)]
            out.append(f"- {p['name']} ({p['pronouns'] or 'no pronouns'}) {kind} \"{p[kind]}\" [stems {', '.join(st)}]: "
                       f"in {len(hit)} of {len(speaking)} speaking turns" + (f" ({', '.join(hit)})" if hit else ""))
    # image carry-over, repetition scan
    fic = [_fiction(r.get("delivered_verbatim") or "") for _, r in rows]
    carry = sum(1 for a, b in zip(fic, fic[1:], strict=False) if len(_bigrams(a, names) & _bigrams(b, names)) >= 2)
    out.append(f"- image carry-over (2+ shared content bigrams with the delivery before): {carry} of "
               f"{max(len(fic) - 1, 0)}")
    opens, closes = [], []
    for f in fic:
        ss = _sents(_Q.sub("Q", f))
        opens.append(" ".join(list(atx.content(ss[0]))[:4]) if ss else "")
        closes.append(" ".join(sorted(atx.content(ss[-1]))[:4]) if ss else "")
    rep_o = sum(1 for i, o in enumerate(opens) if o and o in opens[max(0, i - 10):i])
    rep_c = sum(1 for i, c in enumerate(closes) if c and c in closes[max(0, i - 10):i])
    out.append(f"- repetition scan (logged only): repeated openings {rep_o}, repeated closings {rep_c}")
    # code sentences
    leaks = [(tid, c) for (tid, _), f in zip(rows, fic, strict=True) for c in CODE if c.lower() in f.lower()]
    out.append(f"- code sentences leaked: {len(leaks)}" + (f" {leaks}" if leaks else ""))
    # pronoun drift
    hits = [(tid, e.get("words"), e.get("subject")) for tid, r in rows for e in r.get("claim_log") or []
            if e.get("check") == "pronoun_certain_subject"]
    out.append(f"- pronoun check hits (claim log): {len(hits)}" + (f" {hits}" if hits else ""))
    drift = []
    for (tid, _), f in zip(rows, fic, strict=True):
        for s in _sents(f):
            n = _Q.sub(" ", s)
            who = [p for p in people.values() if p["pronouns"][:2] in ("he", "sh") and p["name"]
                   and (re.search(rf"\b{re.escape(p['name'].split()[0])}\b", n)
                        or (p["role"] and re.search(rf"\bthe {re.escape(p['role'].split()[0])}\b", n, re.I)))]
            if len(who) == 1 and re.search(r"\b(they|their|them|themselves)\b", n, re.I):
                drift.append((tid, s[:140]))
    out.append(f"- 'they' beside one he/she person (candidates, review by hand): {len(drift)}")
    out += [f"  - {t}: {s}" for t, s in drift]
    # speech attribution
    mis = []
    for tid, r in rows:
        f = _fiction(r.get("delivered_verbatim") or "")
        ss = _sents(f)
        speech = (r.get("draft_versions") or [{}])[-1].get("side_list", {}).get("speech") or \
            (r.get("draft_versions") or [{}])[0].get("side_list", {}).get("speech") or []
        for sp in speech:
            pid, words = sp.get("speaker"), str(sp.get("words") or "")[:30]
            if pid not in people or not words:
                continue
            i = next((k for k, s in enumerate(ss) if words[:20] in s), None)
            if i is None:
                continue
            outside = _Q.sub(" ", ss[i])
            first = people[pid]["name"].split()[0] if people[pid]["name"] else ""
            others = [p["name"] for q, p in people.items() if q != pid and p["name"]
                      and re.search(rf"\b{re.escape(p['name'].split()[0])}\b", outside)]
            if others and SPEECH_VERB.search(outside) and not (first and first in outside):
                mis.append((tid, words, "tagged to " + others[0]))
            elif not outside.strip() and i > 0:
                prev = _Q.sub(" ", ss[i - 1])
                pnames = [p["name"] for q, p in people.items() if q != pid and p["name"]
                          and re.search(rf"\b{re.escape(p['name'].split()[0])}\b", prev)]
                if pnames and not (first and first in prev):
                    mis.append((tid, words, f"untagged after a sentence about {pnames[0]}"))
    out.append(f"- speech attribution candidates (review by hand): {len(mis)}")
    out += [f"  - {t}: \"{w}…\" {why}" for t, w, why in mis]
    # first draft, calls
    first = sum(1 for _, r in rows if [v.get("kind") for v in r["draft_versions"]] == ["draft"])
    n = len(rows) or 1
    out.append(f"- first draft delivered {first}/{len(rows)} ({100 * first / n:.0f}%); narrator calls per narrated turn "
               f"{sum(ncalls.get(t, 0) for t, _ in rows) / n:.2f}; all model calls per narrated turn "
               f"{sum(calls.get(t, 0) for t, _ in rows) / n:.2f}")
    return out


def main(argv: list[str]) -> int:
    for a in argv:
        print("\n".join(measures(Path(a))))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
