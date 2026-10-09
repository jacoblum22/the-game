"""Spec 016 / OEQ-12-27: how precise are the precision checks (12.3.2)? Runs `claims.precision_checks` offline over
recorded first drafts and lists every hit, with the hand verdict from `JUDGED` (real error / false hit).

    py -3.12 evals/precision_audit.py                         # the replay bench corpus (evals/corpus)
    py -3.12 evals/precision_audit.py saves/playtest-*.db     # plus recorded games (first drafts, final store)

Corpus packets: names and pronouns come from the recorded view (`narration_plug.Packet.index`), the season from its
time line. Saves: each turn's first draft (declared sentences, speakers included) against the final store's
pronouns and season (ponytail: the final store stands for the turn's; season and pronouns rarely move in a game).
A hit with no entry in `JUDGED` is reported as unjudged; judge it and add it before trusting the rate.

Spec 016's no-verdict guards were tuned on this corpus (the narration pronoun check went from 63 hits, mostly false,
to 4; season words from 3 to 1), so its rate here is a development figure: re-measure on the next round's runs.
Output: evals/baselines/precision_audit.txt.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.audit.claims import SEASONS, calendar_season, precision_checks  # noqa: E402
from engine.audit.declare import DeclaredSentence, SceneIndex, parse_output, voices  # noqa: E402
from engine.data.loader import load_rules  # noqa: E402

# (source, turn, check, word) -> "real" | "false": judged by reading the sentence, its neighbours and the record.
# Ysrion Leafward is stored she/her; the narrator never saw it (squeezed out of the view's profiles, so spec 016
# puts pronouns on the SCENE SETTING line) and said "he" all game: real errors against the store.
JUDGED: dict[tuple[str, str, str, str], str] = {
    ("playtest-20261008-145410-talker", "turn.2", "pronoun_certain_subject", "he"): "real",
    ("playtest-20261008-145410-talker", "turn.4", "pronoun_certain_subject", "him"): "real",
    ("playtest-20261008-145410-talker", "turn.4", "pronoun_certain_subject", "His"): "real",
    ("playtest-20261008-145410-talker", "turn.6", "pronoun_certain_subject", "him"): "real",
    # "hiring extra hands for the autumn harvest" on the spring quarter day (talker note 18)
    ("playtest-20261008-145410-talker", "turn.2", "season_words", "autumn"): "real",
}
# The Framer's cost forms and consequences (framer.pronoun_errors). "real": a pronoun flip against the store;
# "pc": the player's character spoken of as he/she (the OFFER must say "you"; the same re-ask fixes it).
_P = "pronoun_certain_subject"
JUDGED |= {(f"playtest-{k}:framer", t, _P, w): v for k, t, w, v in [
    ("20261007-161320-explorer", "turn.3", "her", "pc"), ("20261007-181158-breaker", "turn.9", "she", "pc"),
    ("20261007-183202-breaker", "turn.7", "he", "real"), ("20261007-183202-breaker", "turn.10", "she", "pc"),
    ("20261007-183858-fighter", "turn.5", "her", "pc"), ("20261007-183858-fighter", "turn.10", "her", "pc"),
    ("20261007-183858-fighter", "turn.13", "her", "pc"), ("20261007-185715-talker", "turn.5", "her", "pc"),
    ("20261007-190015-newcomer", "turn.8", "she", "real"), ("20261007-191540-breaker", "turn.4", "her", "pc"),
    ("20261007-192340-talker", "turn.11", "him", "real"), ("20261007-192340-talker", "turn.14", "him", "pc"),
    ("20261007-195445-breaker", "turn.4", "her", "pc"), ("20261007-195734-fighter", "turn.11", "her", "pc"),
    ("20261007-205857-newcomer", "turn.11", "him", "pc"), ("20261007-210953-talker", "turn.16", "him", "real"),
    ("20261007-213310-talker", "turn.8", "she", "pc"), ("20261007-220207-talker", "turn.9", "his", "pc"),
    ("20261008-135049-fighter", "turn.11", "his", "real"), ("20261008-135049-fighter", "turn.14", "his", "real"),
    ("20261008-135049-fighter", "turn.15", "him", "real"), ("20261008-135049-fighter", "turn.16", "his", "real"),
    ("20261008-145430-fighter", "turn.12", "his", "real")]}


def _run(src: str, turn: str, sents: list[DeclaredSentence], idx: SceneIndex, season: str | None,
         rules: Any) -> list[dict[str, Any]]:
    out = []
    before: list[str] = []
    for s in sents:
        narration, speech = voices(s)
        for h in precision_checks(narration, idx=idx, before=before, speech=speech, about=s.about, season=season,
                                  rules=rules):
            out.append({"source": src, "turn": turn, "check": h.check, "voice": h.voice, "word": h.words,
                        "store": h.store_value, "sentence": s.text, "prev": before[-1] if before else "",
                        "verdict": JUDGED.get((src, turn, h.check, h.words), "unjudged")})
        before.append(narration)
    return out


def corpus_hits(rules: Any) -> tuple[int, list[dict[str, Any]]]:
    from evals.narration_plug import Packet
    from evals.replay_bench import load, packet_items

    hits: list[dict[str, Any]] = []
    n = 0
    for item in packet_items(load()):
        p = Packet(item)
        rec = item["_recorded"]
        m = re.search(r"season (\d+)", p.view)
        season = SEASONS[(int(m.group(1)) - 1) % 4] if m else None
        draft = rec["draft"] or {}
        sents = parse_output(draft) if draft.get("sentences") is not None or draft.get("fiction") else []
        n += len(sents)
        hits += _run(f"corpus:{rec['save']}", rec["turn"], sents, p.index(), season, rules)
    return n, hits


def save_hits(path: Path, rules: Any) -> tuple[int, list[dict[str, Any]]]:
    from engine.store.db import Store

    tmp = Path(tempfile.mkdtemp()) / path.name
    for suf in ("", "-wal", "-shm"):
        if Path(f"{path}{suf}").exists():
            shutil.copy(f"{path}{suf}", f"{tmp}{suf}")
    state = Store.open(tmp).state
    idx, season = SceneIndex.of(state), calendar_season(state)
    con = sqlite3.connect(f"file:{tmp}?mode=ro", uri=True)
    hits: list[dict[str, Any]] = []
    n = 0
    for turn, rec in con.execute("select turn_id, record from turns"):
        dv = (json.loads(rec).get("draft_versions") or [{}])[0]
        sents = [DeclaredSentence.model_validate(s) for s in dv.get("sentences") or []]
        n += len(sents)
        hits += _run(path.stem, turn, sents, idx, season, rules)
    from engine.dm.roles.framer import frame_texts

    for turn, resp in con.execute("select turn_id, response from model_calls where role='framer'"):
        data = (json.loads(resp or "{}") or {}).get("data") or {}
        for t in frame_texts(data):  # the pronoun check only, each text on its own (as framer.check runs it)
            n += 1
            hits += _run(f"{path.stem}:framer", turn, [DeclaredSentence(text=t)], idx, None, rules)
    con.close()
    return n, hits


def main(argv: list[str]) -> int:
    rules = load_rules()
    n, hits = corpus_hits(rules)
    for a in argv:
        try:
            k, h = save_hits(Path(a), rules)
        except Exception as e:  # noqa: BLE001 - an old save the store cannot open: skipped, said so
            print(f"skipped {a}: {e.__class__.__name__}")
            continue
        n += k
        hits += h
    print(f"sentences checked: {n}")
    for where in ("narration", "framer"):
        for check in ("pronoun_certain_subject", "season_words"):
            mine = [h for h in hits if h["check"] == check and h["source"].endswith(":framer") == (where == "framer")]
            n_of = {v: sum(h["verdict"] == v for h in mine) for v in ("real", "pc", "false", "unjudged")}
            judged = n_of["real"] + n_of["pc"] + n_of["false"]
            rate = f"{(n_of['real'] + n_of['pc']) / judged:.2f}" if judged else "n/a"
            print(f"{where} {check}: {len(mine)} hits, {n_of['real']} real, {n_of['pc']} character as he/she, "
                  f"{n_of['false']} false, {n_of['unjudged']} unjudged; precision {rate}")
    for h in hits:
        print(f"- [{h['verdict']}] {h['check']} {h['voice']} {h['word']!r} (store: {h['store']}) "
              f"{h['source']} {h['turn']}: {h['sentence'][:220]!r}" + (f" | before: {h['prev'][:140]!r}"
                                                                    if h["check"].startswith("pronoun") else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
