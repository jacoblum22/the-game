"""Pair each NPC 'don't know' sentence with the player's line and the player's next note. Usage: dunno_pairs.py <transcript.md>"""
import re
import sys

t = open(sys.argv[1], encoding="utf-8").read()
notes = dict(re.findall(r"^- \[(\d+)\] after typing `.*?`: (.*)$", t, re.M))
body = t[t.index("## Transcript"):]
DUNNO = re.compile(r"[^.\"]*\b(?:do not know|don't know|not mine to give|wouldn't know|cannot say|can't say)\b[^.\"]*[.\"]", re.I)
for m in re.finditer(r"\*\*\[(\d+)\] player:\*\* `(.*?)`[^\n]*\n(?:\*note:[^\n]*\n)?\s*```text\n(.*?)```", body, re.S):
    n, said, out = m.group(1), m.group(2), " ".join(m.group(3).split())
    hits = DUNNO.findall(out)
    if not hits:
        continue
    print(f"[{n}] PLAYER: {said[:170]}")
    for h in hits:
        print(f"     NPC: {h.strip()[:170]}")
    note = notes.get(str(int(n) + 1)) or notes.get(n)
    if note:
        print(f"     NOTE: {note[:170]}")
