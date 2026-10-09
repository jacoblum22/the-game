# Feature spec 022: mechanics as state (F5) and `/fix` as an investigator on Sonnet (F6)

**Input**: `rules/_process/reports/R2-J-report.md`, "Engine checklist: Spec 022"; rules 06.5.2, 06.9.4, T-06-10,
T-12-18 (Grapple rows), 01.11.2, 12.5.8, 12.3.4, 12.3.6, 12.15.9, PR-12-11, 12.2.4 (Fixer row); DL-06-31, DL-01-40,
DL-12-105, DL-12-106; `pacing.yaml#details.scene_writes`, `pacing.yaml#feedback.investigate`. Evidence:
`round6-investigation/I3-combat-feedback.md` §1-§5; ROUND6-PLAN F5/F6 (F6 owner-approved 2026-10-09: "/fix"
investigator, Sonnet for the Fixer).
**Owner direction** (constitution VIII, especially VIII.1 and VIII.8): code owns the spine, the model owns judgment;
the player is part of error correction, so `/fix` must investigate the record, repair visibly and answer plainly.
Prefer deleting machinery. No clarify step: assumptions are recorded below.
**Parallel lane**: spec 020 (Reader, packet, cards) ran beside this one and merged first; its hand-off (a folded grip
leaves no hold) is taken up in US1.

## User stories

### US1 - A hold is a condition, and the held foe tries to break free (P1; F5; 06.5.2, 06.9.4, T-06-10, DL-06-31)
A successful hold applies 06.5.2's ladder condition on the held one by the delivered reach (1 `cond.grabbed` S1,
2 S2, 3 `cond.restrained`, 4 `cond.pinned`; a further hold by the same holder tightens one rung), its source the
holder. T-12-18's posture is its face: written only while the condition stands, cleared with it. A hold ends by
breaking free, the holder letting go (`free`), or the holder down, stunned or moved away, and the condition goes
with its face. On its turn a held foe follows `beh.default_melee` row 2 first: break free (its line's attack against
the holder's Might defense; a critical leaves the holder off balance), so it never strikes while held. A grip folded
into the goal it serves (spec 020: "grab her and demand the word") is applied when that goal's beat succeeds.
- **Accept**: on the round-6 fighter saves, each of the 9 foe hits that landed while (or the turn) the PC held the
  foe, re-run with the hold RECORD now writes, is a break-free attempt and no blow.

### US2 - A refused turn costs nothing (P1; F5; 01.3.6-01.3.7; I3 §3)
A turn whose every beat was refused (G4, a question, withdrawn) gives no foe a beat and passes no round.
- **Accept**: 233000 turn 14 (the G4 threat) re-run: no foe action, Vitality and the round unchanged.

### US3 - A price the method pays is a write (P1; F5; 01.11.2, DL-01-40)
A method consequence that hands coin over ("the coin for the round is spent whatever the answer") deducts the coin
at RECORD whatever the degree, shown in the RESULT's `Changed:` line. An offer of coin is not a payment.
- **Accept**: 192926 turn 7's consequence deducts 1 coin; the four offers in the round-5/6 saves deduct nothing.

### US4 - The Fixer investigates, code validates, the answer reads found → did → Now: (P1; F6; PR-12-11, 12.3.6)
`/fix` runs the Fixer role: it reads the report with the calendar, the PC's sheet, the people in view and the last
turns, then calls read-only tools (a turn's record, an entity's state with each fact's provenance, a transcript
search, a frame recomputed from the rules, the PC's coin and inventory ledger, what a character said against the
record) for 3-6 calls, then returns every complaint with what it found, a verdict and proposals (set or remove a
fact, restore a quantity as of turn N, refund or deduct, re-render a display, take back to turn N, correct
testimony, explain). Code validates every proposal (a mechanical change cites record ids the tools returned, INV-9;
sealed stays sealed and a correction never delivers a clue, INV-10; quantities stay in bounds, T-00-1; a take-back
obeys 12.5.8's limit) and applies the valid ones together on one snapshot. The answer: what was found, what was done
and what was refused (with why), then one `Now:` line with each shown value that changed. Complaint text is never
written as a fact.
- **Accept**: the 15 round-6 disputes (I3 §5: 1 right, 6 unclear, 8 wrong), re-run on their saves with the Fixer
  on Sonnet, graded by I3's standard, are mostly right; 5-8 held-out complaints labelled before running score
  likewise; the spec-014 corpus is re-scored before and after.

### US5 - The Fixer runs on Sonnet; play stays on the play model (P1; F6; DL-12-105)
The Fixer's model is configuration: `GameConfig.models["fixer"]` for the Gemini provider (a slot, not run), and the
Claude CLI harness routes `Role.FIXER` to `--fixer-model` (default `sonnet`) while every other role stays on
`--engine-model`.
- **Accept**: the live fighter run's model calls show the Fixer on Sonnet and play on Haiku.

## Retired (each says what supersedes it)
- The hold as scene text (the `restrain` words as its only record) → the 06.5.2 condition; the posture is its face.
- `foe_beat`'s strike-regardless → `beh.default_melee` row 2 (break free first).
- Coin spent only as text → `change.pay` at RECORD.
- The silent take-back → every restore ends with `Now:` (12.5.8, DL-12-106).
- The one-shot understanding call over player-visible text (`engine/dm/understand.py`, `Role.UNDERSTAND`, its prompt)
  and `_claim`'s fixed branches and outcome table → the Fixer's investigation and validated proposals.
- Pinning complaint text (`correction.N`) → corrections write typed values only.
- Settling complaints one by one → one snapshot, all proposals validated and applied together, one answer.
- The reliance CHOICE pause after a report → a take-back is proposed by the Fixer and applied (the player can
  `/fix` again); `pacing.yaml#feedback.understand_call` and `feedback.outcomes` deleted.

## Assumptions (no clarify step)
1. The break-free roll uses the foe line's attack bonus (T-09-3 has no separate Grapple bonus) against the holder's
   Might defense (06.5.2).
2. A folded grip applies at the goal's delivered reach on success, none on failure (coordinator's hand-off).
3. A payment's amount is the number the consequence names, else 1 coin (the economy's smallest lot, 08 `lots`); the
   payment is read from the Framer's declared consequence words (precision checked on the saves: 3 of 3 payments,
   0 of 4 offers). A typed `price` field on the Framer is the upgrade when its schema is next opened.
4. Restores print `Now:` with the PC's shown values (quantities, harm word, conditions, what they hold); nothing
   changed prints the sheet as it stands.
5. Incidental look/activity/manner corrections need no evidence (12.3.6 item 4); every other key needs record ids.
