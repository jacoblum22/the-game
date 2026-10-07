# Editor pass E1: ch.04 and ch.05 (fresh-reader)

Scope: I read ch.04 and ch.05 section by section, as a reader new to the project. No mechanic, number, threshold or outcome was changed, and no basis or revision tag was removed. All 34 edits were scripted with exact-match, single-occurrence replacements. Each text edit carries `[editor: E1-NNN]`. Validator: 0 ERROR / 0 WARN. Anchors were recompiled (`data/anchors.yaml`: two ch.04/05 hashes changed).

## Fixes by category (34)

| Category | Count | Ids |
|---|---|---|
| Stale "pending / until" notes and requests already met | 11 | E1-013 to E1-020 (04 Interface requests: `gen.pick`, T-00-9, the glossary, relic evidence, `success_by_band`, `opponent_kinds`; OEQ-04-10 quoting the ladder from before I-089); E1-021, E1-030 (05's "chapters not yet written"); E1-031, E1-032 (05 glossary request and the `composites.04.yaml` merge) |
| Sentences broken or garbled by layered edits | 4 | E1-002 (04.2.7 missing verb), E1-006 (04.3.5 fragment "On the current ladder…"), E1-028 (WE-05-3 "harm edge +2 → the harm event deals…"), E1-029 (WE-05-5 comma splice) |
| Abbreviations and undefined symbols | 5 | E1-003 HWFWM, E1-004 PoE / DCC, E1-007 `W(tier)` in K5, E1-009 OOF, E1-025 EU first used before 05.11 |
| Unclear antecedents | 2 | E1-001 ("its owner-blocks"), E1-014 ("the six `lic.call.*`" against the "five universal" licenses) |
| Card against intro, and cross-references | 3 | E1-008, E1-024 (the primal Focus trigger was worded three ways: 04.5.4, 05.7.2 and 05.6.10. All now match 05.6.10 and `callings.yaml`: "dawn under open sky or in wild country"); E1-010 (04.10.1 cited 04.10.4 for the library, which is defined in 04.10.3) |
| Numbering and table formatting | 5 | T-04-8 rows put back in order (R10 and R12 were out of sequence); E1-005 (key to 04.3.5's mixed-format rolled-encounters row); T-05-13 moved before T-05-14; the `influence.teaching` row moved from among the craft rows to the influence rows in T-05-14; a blank line added before the `---` that followed T-05-13's last row; a stray space removed before a colon in 05.7.3 (left untagged because it is whitespace only) |
| Wording that could be read two ways | 4 | E1-011 (PR-04-5 "fewer than one"), E1-022 ("at least four each" with three named), E1-026 (05.9.4 "a month with a teacher or two alone"), E1-027 (05.11.5 "three abilities at tier 1" with five rows) |

## Issue-ledger rows opened (status open)

- **I-108** (04): stale simulation figures in prose. 04.2.3, 04.4.3, 04.8.2 and WE-04-8 disagree with T-04-8 R3, R7 and R8 and with `04-recog04-output.txt`. Fixing them means changing numbers, so it is left for the owner.
- **I-109** (04): the worked examples' numbers disagree with each other. WE-04-2's thin-stealth row conflicts with WE-04-1 (scene 95 against scene 97). WE-04-3 and WE-04-5 use weighted 85, but WE-04-1 has 84.
- **I-110** (05): 05.3.2 allows a Working only at `beat`, but 31 Working-form abilities in the data are riders (`ab.aimed_shot` among them). Settling it is a rule decision.

## Not changed

These were noticed and judged acceptable, or outside an editor's remit: references to historical passes ("the sixth pass", 04.4.1), "four play styles" in R1, and `trg.04.offer_due` / `trg.04.pick_due` being listed but never raised.
