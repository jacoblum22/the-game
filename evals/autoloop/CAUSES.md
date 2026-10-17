# Why did the DM contradict itself? (reader instructions)

You get a batch of contradiction findings from one test game (a JSON line each: `id`, `game`, `round`, `quote`, `why`).
Another reader found them by reading the transcript. Your job is to find, for each one, **why** the DM said it: what
it had in front of it at that round, and what kind of slip it was. Work from the files; don't guess.

## What you have (run from the repo root)
- The transcript, round by round: `evals/autoloop/games/read/<game>-1-60.txt`, `-61-120.txt`, `-121-180.txt`. Each round
  has the player's line, the game's tool lines `[game]`, the DM's hidden notebook writes `[DM write_lore (hidden)]`,
  and the reply `DM:`. Search them with grep for the names and numbers in the finding.
- What the DM had in front of it at the start of a round:
  `PYTHONPATH=".;evals/autoloop" .venv/Scripts/python evals/autoloop/context.py <game> <round> [--summary] [--lore NAME ...] [--grep WORD]`
  It prints which earlier rounds the DM's conversation still held word for word, and which only through its own
  summary (the conversation is cut when it gets long; the DM writes a summary and keeps the last 20 rounds word for
  word); the notebook notes shown at the top of that round's player message; with `--summary`, the summary in force;
  with `--lore`, a notebook entry in full as it was then; with `--grep`, every notebook line holding a word, as the
  notebook was then.

## For each finding, check
1. **Valid?** Is it really a contradiction, from the transcript? `yes`, `no` (the reader was wrong; say why), or
   `doubtful`.
2. **The earlier fact:** the round where it was first said (`earlier_round`).
3. **Word for word:** was that earlier round still in the conversation word for word at this round? (`verbatim`: yes/no)
4. **Summary:** if not, did the summary in force carry it, and correctly? (`summary`: `right`, `wrong`, `missing`, or `na`)
5. **Notebook:** was it in the notebook at that round? (`notebook`: `right`, `wrong` (the notebook held the wrong
   version), `both` (it held both versions, such as an old fact and a later correction), `missing`)
6. **Shown:** was the entry holding it in that round's notes? (`shown`: yes/no/na)
7. **Kind** of slip, the main one (`kind`), one of:
   - `arithmetic`: a sum the DM worked out wrong from facts it had: days, hours, distances, travel times, counts of
     people or things, money.
   - `recount`: a number or detail of the scene restated differently (six guards, then eight) where no sum was needed.
   - `reverted`: it had corrected itself on this point, then went back to the old version.
   - `same_reply`: both sides are in the same reply.
   - `new_invention`: something new it made up (a cause, a backstory, a clue) that clashes with what was established.
   - `capability`: a claim about what the game or its tools can do.
   - `other`: say what.
8. **cause:** one sentence, plain words, on why it happened.

## Output
Write one JSON line per finding to your output file (the path you are given), in the same order:
`{"id": ..., "valid": ..., "earlier_round": ..., "verbatim": ..., "summary": ..., "notebook": ..., "shown": ...,
"kind": ..., "cause": "..."}`. Write nothing else to the repo, and don't change any file but your output.
