# R2-J report: round-6 rules wave (F1-F7)

Revision R2-J. Rule edits tagged `[revision: R2-J]`. Source: HANDOFF-2026-10-09 §2, §3.3, §6; ROUND6-PLAN.md
(owner-approved 2026-10-09, F6 on Sonnet); constitution VIII. Appended after every step.

## Progress
- Setup: worktree reset to milestone-1-playable (1a1b982). Read handoff §2/§3.3/§6, ROUND6-PLAN, constitution VIII,
  R2-J0 report. Baseline validator 0 ERROR / 0 WARN.
- Survey: read by id 01.2.2, 01.2.6, 01.2.7, 01.6.8, 01.11.2, 06.5.2, 06.9.2, 12.2.2 (PARSE), 12.2.4, 12.2.7,
  12.3.1–12.3.6, 12.5.8, 12.10.8, 12.11.2, 12.14.2, 12.14.12, 12.15.2/3/9, 15.1.4, PR-12-2, PR-12-10, PR-12-11,
  PR-12-12, T-12-18, 00.15.4, `pacing.yaml` (claim_check, details.scene_writes, testimony); golden policy B5; I1 §7,
  I2 fix list, I3 coin dispute, I4 A5. The "write around names or kinship" line exists only in
  `engine/dm/roles/prompts/narrator.md`; its nearest rule is 12.14.2.
- Ch.01 and ch.06 (scratch `e01.py`, 12 asserted edits): 01.2.2 split by goal (F2; conflict clause provisional);
  01.2.6 OFFER title from the typed goal; 01.2.7 items 1 and 3 (two goals; the change shown in RESULT, never handed
  to the narrator as done); 01.6.8 mechanically relevant levers and snags only (F4); 01.11.2 a price paid is a write
  (F5 coin); 06.5.2 the hold is a condition and the held one's turn breaks free first (F5); 06 edge case "two beats
  in one sentence" tied to 01.2.2's conflict clause.
- Ch.12, 15, 00 (scratch `e12.py`, 48 asserted edits): 12.2.2 PARSE (one beat per goal; `rests_on` retired);
  12.2.4 items 1–3 and the role table (guidance digests, no core or id-sorted cards, identity lines for everyone
  named, lead line only when new or relevant, conversation for Director/World/Checker, a Fixer row); 12.2.7
  (answered check retired); 12.3.1, 12.3.1a, 12.3.1b, 12.3.3, PR-12-2 (passage + side list, quote-mark check, one
  revision that sees the draft); 12.3.6, PR-12-11 (the investigator); 12.5.8, 12.15.9 (`Now:` on every restore);
  12.10.8, PR-12-10, 12.14.12 item 3 (answer lines only with a fact or clue; no re-delivered clue); PR-12-12
  (triggers narrowed; refusals and opinions never facts; pronouns in scope); 12.11.2 and 15.1.4 (seeded stance
  bounds the reaction roll, provisional); 12.13.3 (split by goal); 12.14.2 (no "write around names or kinship");
  12.15.2 (OFFER title from the typed goal); T-12-18 (labels never levers; the hold's posture is the condition's
  face; "straining" removed); 00.15.4 (situation plus digest).
- Data (scratch `edata.py`, 9 edits): `pacing.yaml` claim_check (`max_revisions: 1`, `passage_side_list`,
  `speech_quoted`; `max_redrafts` and `sentence_declaration` marked retired but kept until spec 019), scene_writes
  grapple (no "straining" manner), testimony (triggers narrowed, `never_facts`, `state_claim_sees`), feedback
  (`investigate` block; `understand_call` and `outcomes` marked retired until spec 022), packet (`guidance_digest`,
  `situation_cards_by_tag: retired`, `identity_lines`, `lead_line`). OEQ-12-26 re-aimed at the investigator.
  YAML parses.
- Decisions and ledger (scratch `edl.py`): DL-01-37..40 (DL-01.md), DL-06-31 (DL-06.md), DL-12-101..107 (DL-12.md),
  DL-00-07 (decision-log.md's DL-00 head, after DL-00-06); ledger I-194..I-204 (status open: rules done, engine
  specs pending). Owner quotes taken only from constitution VIII's preamble and DL-00-06.
- Close: re-assembled the appendix (`integration-assemble-appendix.py`), compiled anchors (129; 0 errors, 0
  warnings), compiled cards last (2133 cards, core 6). Validator: **0 ERROR / 0 WARN** (INFO only: BASIS 1, POOLS 2,
  REFS-EX 9, REFS-MD-EX 70). Engine tests: 1473 passed, 2 skipped. No engine code was touched, and the data edits
  keep every key the current code reads.

## Ids touched
- Rules: 00.15.4; 01.2.2, 01.2.6, 01.2.7 (items 1, 3), 01.6.8, 01.11.2; 06.5.2, the 06 edge case "Two beats in one
  sentence"; 12.2.2 (PARSE decision 3), 12.2.4, 12.2.7, 12.3.1, 12.3.1a, 12.3.1b, 12.3.3, 12.3.6, 12.5.8, 12.10.8,
  12.11.2, 12.13.3, 12.14.2, 12.14.12, 12.15.2, 12.15.9, PR-12-2, PR-12-10, PR-12-11, PR-12-12, T-12-18, OEQ-12-26;
  15.1.4.
- Data: `pacing.yaml` (claim_check, details.scene_writes, testimony, feedback, packet); `anchors.yaml` and
  `engine/build/cards.json` regenerated.
- Decisions: DL-00-07; DL-01-37, DL-01-38, DL-01-39, DL-01-40; DL-06-31; DL-12-101 to DL-12-107. Ledger: I-194 to
  I-204.
- Unused from the allotted ranges: DL-01-41..45, DL-06-32..36, DL-12-108..120, DL-15-40..44, DL-00-08..09, I-205..210.

## What each change retires (each rule says it)
- F1: the sentence array, per-sentence judging and repair, two redrafts, coverage "add" calls, the answered-question
  check, and "every part answered" (12.3.1, 12.3.1a, 12.3.3, 12.2.7).
- F2: the act-by-act split test, and "two changes are two beats" read act by act (01.2.2, 12.2.2, 12.13.3); the raw
  `method` in the OFFER (01.2.6, 12.15.2).
- F3: the core and the id-sorted situation cards in model packets; the lead line in every packet; "write around
  names or kinship" (00.15.4, 12.2.4, 12.14.2).
- F4: `rests_on` and the "NPC's response source" trigger; refusals settled as facts; the testimony call with no
  pronouns (PR-12-12). Scene labels as levers or snags, and DL-12-93's activity-as-lever clause (01.6.8). Empty or
  wrong answer lines, and re-delivered clues (PR-12-10). The change line handed to the narrator as done (01.2.7).
  Complaint text stored as a fact (12.3.6, PR-12-11).
- F5: the hold as words; the "straining" manner (06.5.2, T-12-18); a coin paid only in words (01.11.2); silent
  restores (12.5.8).
- F6: the one-shot understanding call, its fixed outcome table, code deciding before any model sees the report, and
  complaints settled one at a time (PR-12-11).
- F7: the bare reaction roll for a cast NPC with a seeded stance (12.11.2; provisional).

## Engine checklist per spec
**Spec 019 (F1 + F4's narration side)**: `narration.py`, `narrator.py`, `claims.py`.
- Cite: 12.3.1, 12.3.1a, 12.3.1b (items 1, 2.7, 4), 12.3.3, PR-12-2, 12.2.7, 12.14.12, 01.2.7 item 3; DL-12-101,
  DL-01-39, DL-12-103; `pacing.yaml#claim_check` (`max_revisions`, `passage_side_list`, `speech_quoted`).
- Build:
  - one passage plus a side list `{speech[{speaker, words, direct|reported}], new[], covers[]}`;
  - code scans over the whole passage;
  - the quote-mark check: direct speech inside quotes, and no first-person sentence in the narrator's voice. If the
    revision misses it, code quotes the exact words;
  - one revision call that sees the whole draft;
  - `said` records that store whole speeches;
  - rendered lines only as the last fallback, and never as instructions.
- Retire:
  - the sentence-array schema and its declarations (`refs`, `about`, `atmosphere`, per-sentence `speaker`);
  - the per-sentence repair loop (`MAX_REDRAFTS`, `_max_redrafts`);
  - coverage "add" repair calls;
  - `screen._acknowledged` (the answered-question check);
  - record lines that carry "say it plainly; it is done" (`narrator.py` near line 294);
  - the `change.py` line "Agreed by X: <goal>" sent to the narrator.

  Then delete `claim_check.max_redrafts`, `sentence_declaration` and the per-sentence wording of `on_exhausted` from
  `pacing.yaml`.
- Measure:
  - give `precision_checks.season_words` a measured `precision` (I1 §7: its one hit was false), so it logs until it
    meets `min_precision`;
  - measure the pronoun check on speech before it blocks there.

**Spec 020 (F2 + F3)**: the Reader, `packet.py`, `cards.py`, prompts.
- Cite: 01.2.2, 01.2.6, 01.2.7 item 1, 12.2.2 decision 3, 12.13.3, 12.15.2 (*Title*), 12.2.4 items 1–3 and the role
  table, 00.15.4, 12.14.2; DL-01-37, DL-01-39, DL-12-104, DL-00-07; `pacing.yaml#packet` (`guidance_digest`,
  `situation_cards_by_tag`, `identity_lines`, `lead_line`).
- Build:
  - Reader output: goals per target (what, toward whom, how), plus out-of-character flags;
  - `normalise` folds an against-will act into the goal it serves;
  - the OFFER title and "Then:" are rendered from the typed goal;
  - a guidance digest for each role;
  - conversation for the Director (last two exchanges), the World and the Checker (last exchange);
  - identity lines (name, pronouns, `bond.`) for everyone named or mentioned, present or absent;
  - the lead line only when it is new or relevant.
- Retire:
  - the Reader prompt line "two changes are two beats";
  - `pipeline._then` printing `method`;
  - the core, and the situation-by-tag step of `load_cards_for`, in every packet;
  - the narrator prompt's "write around it" line (`engine/dm/roles/prompts/narrator.md`, "Write only from the record
    and the view").
- Evals:
  - relabel **B5** in `evals/reader_golden_POLICY.md`. An against-will touch that serves a goal is that goal's method
    (`against_will` is true on the goal beat); it is its own beat only when it is the goal;
  - review **D1**'s walk-first rows (g027, g029);
  - do both blind, by 01.2.2, before looking at answers (I-204);
  - add the goal-shape breadth set.

**Spec 021 (F4's testimony and answer lines + pronouns and bond)**: `answer.py`, `npc_layer.py`, testimony.
- Cite: PR-12-12, 12.3.1b item 1, 12.2.2 (`rests_on` retired), 01.6.8, T-12-18, PR-12-10, 12.10.8, 12.14.12 item 3,
  12.2.4 item 3, 12.11.2, 15.1.4; DL-12-102, DL-12-103, DL-01-38, DL-12-107; `pacing.yaml#testimony`.
- Build:
  - triggers: travel, cited in a roll, or a mechanical input (including a target known only through testimony);
  - the claim call sees the speaker, the exchange and the identity lines. It returns none for a refusal, an
    opinion, a want, a feeling or an intention;
  - answer lines only for a case's delivery, a pointer to the holder, or a cast person;
  - the seeded stance bounds the first-interaction roll.
- Retire:
  - settlement driven by `rests_on`;
  - `settle()` accepting the speaker's own refusal;
  - the "no one you know" fact and empty lines from `cast_who`;
  - `answer._from_case` delivering a clue the PC already found;
  - a speaker card that skips `bond.` and shows corrections or `agreed` facts as "knows:";
  - Framer candidate facts that include scene labels (posture, manner, activity) or unsettled `said.*`;
  - `first_interaction` in `world/social.py` ignoring stance.

**Spec 022 (F5 + F6)**: `resolve/`, `dispute.py`, `understand.py`, a fixer tool layer.
- Cite: 06.5.2, 06.9.4, T-06-10, T-12-18 (Grapple rows), 01.11.2, 12.5.8, 12.3.4, 12.15.9, PR-12-11, 12.3.6,
  12.2.4 (Fixer row); DL-06-31, DL-01-40, DL-12-105, DL-12-106; `pacing.yaml#details.scene_writes`,
  `pacing.yaml#feedback.investigate`.
- Build:
  - the hold applied as `cond.grabbed`, `cond.restrained` or `cond.pinned` (its source the holder), with the posture
    written from it;
  - `foe_beat` tries break-free first, and refuses what the condition forbids;
  - payments made as method consequences are quantity writes;
  - a `Now:` line on every restore;
  - the Fixer role:
    - read-only tools: turn record, entity state and provenance, transcript search, recompute a frame, the coin and
      inventory ledger, what was said versus the record;
    - 3–6 steps;
    - a broad set of proposals, validated by code (INV-9, INV-10, T-00-1, the limit in 12.5.8);
    - one snapshot per report;
    - the reply: found → did → Now:;
    - model: Sonnet for the Fixer, set in config (owner, 2026-10-09).
- Retire:
  - the hold kept as scene text (the `restrain` words in `change.py` as its only record);
  - the "straining" manner (already removed from the data);
  - coin spent only as text;
  - the silent take-back;
  - the one-shot `understand` call over player-visible text, and `_claim`'s fixed branches;
  - pinning complaint text;
  - settling complaints one by one.

  Then delete `feedback.understand_call` and `feedback.outcomes` from `pacing.yaml`.
- Test: `evals/feedback_corpus.py`, the 15 round-6 disputes (I3 §5), and held-out complaints (OEQ-12-26).

## Owner decisions needed
1. **Splitting by goal inside a conflict** (DL-01-37, provisional). Options:
   - (A) A move or leap that ch.06 gives its own roll ("vault the table and stab him"; T-06-9's "X, then Y" rows)
     stays a sequential beat before the goal's beat. The goal's beat is always framed.
   - (B) Fold the move into the goal's beat: one roll. The move's action is still paid, and its obstacle becomes the
     stakes or a snag.
   - (C) As B, and the method's lever (for example `plunging`) applies automatically on a success.

   **Recommendation: A** (taken provisionally). It fixes the traced failure, the goal never being rolled, without
   reopening ch.06's action economy and its sims. Revisit with the goal-shape set.
2. **How the seeded stance bounds the reaction roll** (DL-12-107, provisional). Options:
   - (A) A bound: `helps` never starts below Neutral, and `hinders` never above Wary. For `helps` that gives Neutral
     72.2%, Warm 19.4%, Friendly 8.3%.
   - (B) The stance as one more ±1 cited modifier. A `helps` NPC still starts Unfriendly or worse 8.3% of the time.
   - (C) The stance sets standing outright (helps +1, hinders −1).

   **Recommendation: A** (taken provisionally). It keeps the roll's variety and rules out the traced failure.
