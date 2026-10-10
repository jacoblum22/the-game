# Spec 027 implementation results: the round-7 cleanup pass

Cases committed before any code (5869180); rules wave and engine after. Real numbers below; nothing faked.

## Gates
| Gate | Result |
|---|---|
| Full suite | **1942 passed, 4 skipped, 0 failed** (spec 026 merged: 1908) |
| Replay | re-recorded (`offline_seed11`) |
| ruff / pyright (touched files) | 0 / 0 |
| Validator | 0 ERROR / 0 WARN (INFO: BASIS 1, POOLS 2, REFS-EX 9, REFS-MD-EX 70); anchors 0/0; cards compiled last |
| `longhorizon --mode scripted` | 0 engine errors (`longhorizon_scripted.txt`) |
| Made-up and edge cases | C1-C16, C18-C27: 34 tests pass (`tests/engine/test_spec027_cases.py`); C12 and C17 below; C28 by the rules worker (validator, by hand) |

## Packet check (C12; `looks_check.py`, `looks_check.txt`; narrated turns, rebuilt from the saves, read-only)
| Save | turns with a person's look: as played → rebuilt | a thing's description |
|---|---|---|
| 024 live talker (201430) | 16/16 → 1/16 (the scar: 16/16 → 1/16, the scene opening) | 15/16 → 0/16 (the bill's own text and place: 11/16 → 1/16) |
| round-7 talker (160602) | 15/15 → 2/15 | 15/15 → 8/15 |
| round-7 explorer (160642) | 15/15 → 4/15 | 14/15 → 8/15 |

Counts are per narrated turn (the brief's 19/19 and 14/19 counted narrator calls, revisions included). The bill's 1/16
is turn 5, the turn the narrator itself wrote it on mention: a cut save already holds it, so the rebuilt count can only
be high. The things left in the round-7 saves are scene openings, turns that look at them, and the "earlier scenes"
cards (12.4.8), whose `noted:` lines quote narrated details of past scenes; those cards were not in scope.

## /fix note (C17: spec 026's two repeats, Sonnet Fixer, Haiku play roles; `fixer_fresh_027_f04_f12.json`)
- **f12 (nothing at stake): right.** The Fixer's note ("Morga is friendly… she has no reason to refuse") reached the
  Framer; the re-frame needed no roll and Morga agreed (026 run 2: framed 75% again).
- **f04 (the guard should know my rank): still 65% (auto wrong).** The note reached the Framer; the OFFER now counts
  "rank: sergeant +2", but the Framer again framed it as a request to persuade, at 65%. This is the out-of-scope item
  (the Framer's request size offsetting the rank bonus): the Framer's judgment.
- The taped spec-026 fresh run was re-scored on this code (`fixer_fresh_026.json`): f01's screen now reads "Tam
  Harlan's eyes: milk-white…" (no slug); f04's `knows_` correction now applies (H7), and the taped Framer answer
  still says 65%, so f04 is scored wrong instead of unclear (11/0/3).

## Hand-offs
| # | Status | What changed |
|---|---|---|
| H1 no narration after a critical success | fixed | The passage did narrate it; an auto-committed OFFER and its RESULT printed below it. `Response.split`: they now lead the passage (engine text and both CLI renderers); DL-12-124. |
| H2 "furniture 0" | fixed | `slug_words` drops index segments and the `detail.` namespace; the codex label uses it. |
| H3 gate refusal slugs | fixed | `oof._fact_line` uses `fact_sentence` (a narrated detail as "X's eyes: milk-white"), else the plain phrase. |
| H4 "go to the ford" | fixed | The seed names the gate building "the gate" (described "the gate, by the ford"); the reference script and its example regenerated (parity 13/13); DL-12-125. |
| H5 dead `change.pay` | fixed | Both calls and the function removed. |
| H6 narrator "what someone knows" | fixed | Characters may say what they believe and what their trade and town know (testimony); hook terms and mystery facts only from the record and speaker card. |
| H7 `knows_` guard | fixed | Removed from `CASE_PREDICATES` (no case writes it). |
| H8 READING / numerals | fixed | READING no longer matches "what did they say"; takes two-word noun phrases. The player's own numbers are allowed for the PC. |
| H9 WE-01-2, WE-12-11, reach tie-break | fixed (rules worker) | WE-01-2 has no Oracle snag; WE-12-11 uses the lead as data; `reach_flags.whole.tie_break: true` per 01.6.10. |

## Rules (R2-K, `rules/_process/reports/R2-K-027-report.md`)
DL-12-122 (B), DL-12-123 (C, PR-12-11 one line), DL-12-124 (auto roll order), DL-12-125 (gate name); DL-01-46 and
DL-12-118 owner-confirmed with the quote; revisit lines on DL-12-113 and DL-12-99. Ledger I-220..I-226. DL-12-126..128
unused.

## Assumptions
As `spec.md` A1-A6. Also: "about" counts as asking about someone only after an ask/know/tell/hear/say word ("sorry
about the cask" does not); a thing's `holder` stays every turn.

## Not in scope (noted)
The Framer's "favour"-sized request offsetting a cited rank (f04). The "earlier scenes" cards still quote narrated
details of past scenes. The Fixer's free-form `set_fact` key can still read awkwardly ("Pell Rudd's knows rank of hale
brannock") now that `knows_` corrections apply.
