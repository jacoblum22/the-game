# Playtest issues

Triage list for the automated playtest loop (`evals/playtest.py`). One row per issue, deduplicated across runs.
Class: **bug** (engine, fix it) · **harness** (the test rig, not the game) · **rules** (logged to
`rules/_process/issue-ledger.md`, never edited here) · **claude-only** (may not happen with Gemini) · **polish**.
Status: open · fixing (round N) · fixed (commit) · logged (ledger id) · wontfix.

| ID | Class | Sev | Issue | Evidence | Status |
|---|---|---|---|---|---|
| P-001 | bug | high | Raw pydantic error "1 validation error for OracleResult … valid boolean, input_value=[items]" printed to the player as game text | run 20261007-155118 input 26 | fixing (r1) |
| P-002 | bug | high | Claim check doesn't converge: 5/7 turns fell back. Redrafts re-extract all sentences and fail ones that passed; unnamed background figures' ambient acts cut as unsourced_change; Oracle "yes" still forces a redraft; elapsed-time and empty-reason contradictions | 20261007-155118 turns 1,2,4,6,7 | fixing (r1) |
| P-003 | bug | high | Plain fallback text reads as debug output: "X? Yes. Y? No.", "No roll: trivial", "Possible now: …", "Time passes ( intervals)", infinitive restatements | 20261007-155118 turns 2,4,6,7 | fixing (r1) |
| P-004 | bug | high | Hunter's sheet says "good at tracking", then tracking is redirected: "needs Tracking, which you have not learned" | 20261007-155118 input 27–29 | fixing (r1) |
| P-005 | polish | med | OFFER block jargon: "Mode: fallback — DC +5, reach capped at limited", "time, S1", garbled stakes | 20261007-155118 input 28–29 | fixing (r1, with P-004) |
| P-006 | bug | low | Name step says "Add he, she or they", but "Branric Blackfield, she" then asks pronouns again | 20261007-155118 input 22 | open |
| P-007 | polish | low | "a hunter, half-elf" silently becomes human ("No elves live in this land" shown in passing only) | 20261007-155118 input 18–19 | open |
| P-008 | harness | — | Player never saw its own typed lines, so it reported "skipped" steps that weren't skipped; notes repeated old complaints | 20261007-155118 inputs 18–24 | fixed (harness echo, round 2 on) |
| P-009 | polish | med | World-seed summaries too vague to judge: "5 more" places, "the enemy and the prisoner", rumors/wilds as counts only; "3 more" powers unnamed | 20261007-155118 inputs 12–16 | open |
| P-010 | polish | low | Jargon in setup and sheet without explanation: keepers, haven, Kinspeech, dread, Resolve | 20261007-155118 inputs 8–13, 24 | open |
| P-011 | polish | low | Mixed setup: "step N of 14" titles don't match the question asked; 14 keep/re-roll screens feel long | 20261007-155118 inputs 5–10 | open |
| P-012 | bug | med | A critical failure is announced ("goes badly wrong") but the player never learns what happened | 20261007-155118 turn 6 | open (check after P-002/P-003) |
