"""What the DM had in front of it at the start of a round, for finding why it said something: the round's turn number,
the cuts so far (which turns its conversation still held word for word, and which only as its own summary), the
notebook notes shown at the top of the player's message, and, if asked, notebook entries in full as they were then
or the summary in force.
    PYTHONPATH=. .venv/Scripts/python evals/autoloop/context.py <name> <round> [--summary] [--lore NAME ...] [--grep WORD]
--grep: every notebook line (descriptions and relationships) holding WORD, as the notebook was at that round."""
import argparse
import sys
import json
from pathlib import Path

from metrics import GAMES

from dm import lore as notebook

p = argparse.ArgumentParser()
p.add_argument("name")
p.add_argument("round", type=int)
p.add_argument("--summary", action="store_true")
p.add_argument("--lore", nargs="*", default=[])
p.add_argument("--grep")
a = p.parse_args()
sys.stdout.reconfigure(encoding="utf-8")

meta = json.loads((GAMES / f"{a.name}.meta.json").read_text(encoding="utf-8"))
save = json.loads((GAMES / Path(meta["save"]).name).read_text(encoding="utf-8"))
t = save["transcript"]
idx = [i for i, e in enumerate(t) if e["kind"] == "player" and i >= meta["play_starts"]][a.round - 1]
before = t[:idx]
turn = notebook.now(before) + 1
state = next(json.loads(x) for x in open(GAMES / f"{a.name}.states.jsonl", encoding="utf-8")
             if json.loads(x)["round"] == a.round)
lore = state["lore"]
start = notebook.now(t[:meta["play_starts"]])  # turn of round 1, so turn = round + start - 1


def rnd(turn_no: int) -> int:
    return turn_no - start + 1


cuts = [s for s in save["story"] if s["turn"] + 20 < turn]  # a cut at turn last summarises to last - 20
print(f"ROUND {a.round} = turn {turn} (round r is turn r + {start - 1})")
if cuts:
    s = cuts[-1]
    print(f"Conversation: the DM's own summary of rounds up to {rnd(s['turn'])}, then rounds {rnd(s['turn']) + 1} "
          f"to {a.round - 1} word for word (cuts so far end at rounds {', '.join(str(rnd(c['turn'])) for c in cuts)}).")
else:
    print("Conversation: every round so far word for word (no cut yet).")
party = (state["sheet"]["name"], *(c["name"] for c in state["companions"]))
_, notes = notebook.notes(lore, t[:idx + 1], party)  # the player's line is logged before the notes are made
print("\n--- notes shown at the top of the player's message ---\n" + notes.split("\n" + notebook.REMINDER)[0])
if a.summary and cuts:
    print("\n--- the summary in force ---\n" + cuts[-1]["text"])
for n in a.lore:
    try:
        print("\n--- notebook entry, as it was ---\n" + notebook.look(lore, [n], before))
    except Exception as e:  # noqa: BLE001
        print(f"\n--- {n}: {e}")
if a.grep:
    w = a.grep.casefold()
    print(f"\n--- notebook lines with {a.grep!r}, as it was ---")
    for n, e in lore["entries"].items():
        for d in e["description"]:
            if w in d["text"].casefold():
                print(f"{n}: (t{d['turn']}) {d['text']}")
    for f in notebook._facts(lore):
        if w in f["text"].casefold():
            print(f"• {f['text']} (t{f['turn']})")
