# Feature spec 026: `/fix` works the way an investigating engineer does (T7), and one shared people card

**Input**: `rules/_process/reports/R2-K-report.md`, "Spec 026 (T7)"; ROUND7-PLAN T7 (owner-approved 2026-10-09: "the
goal was to make slash fix work just like you… you seem to figure out what the problem is, and it seems like you're
able to to potentially revert it if necessary"); ROUND7-ANALYSIS §2 T7 and §6; traces R7-I3 §3 and R7-H2 T7
("What a fix must do differently"). Rules cited: PR-12-11 steps 2-6 and its retires, 12.3.6 item 4 ("At an open
OFFER"), 12.5.8 item 1, 12.2.4 (Fixer row), OEQ-12-26. Decisions: DL-12-116, DL-12-117, DL-12-111. Data:
`pacing.yaml#feedback.investigate` (`proposals_added`, `dry_run`, `check_screen`, `sees`, `mechanics_digest`,
`open_offer`, `code_guards`, `scored_on`). Constitution VIII.1 (code owns the spine) and VIII.8 (the player is part
of error correction; quality measured on real complaints).
**Hand-offs taken**: spec 024 (the Fixer's turn listing printed the raw degree: use `effective_degree`); spec 023 (the
Framer packet lacks NPC licences: its `target's record` line is replaced by the shared people card).
**Parallel lane**: spec 025 owns `engine/gen/`, `answer.py`, `npc_layer.py`, `social.py`, `testimony.py`,
`director.py`. Anything needed there is a hand-off.

## User stories

### US1 - One people card, read by every role and by the Fixer (P1; DL-12-116; 12.2.4)
`packet.people_card(state, eid)` renders a person in plain words: name as the PC knows it, pronouns, people, role
(an NPC) or livelihood and upbringing (the PC), licences by name and grade ("Letters (reads and writes)", "Scribing
(trained)", "speaks the Common tongue"), competences ("lore +1"), stance, standing toward the PC, the PC's bond, and
facts about their station (a rank). Never a sealed field for a play role (refusals and other motives stay with the
roles that already read them); the Fixer's copy adds refusals, marked as hidden from the player. The Reader's and
Narrator's views print it for each person with a full profile; the Framer's view prints it for the beat's target
(replacing spec 023's `target's record` line). The Fixer's `entity` tool and its opening print the same card. A tool
can therefore never know less than a role did.
- **Accept**: Belie's card (round-7 fighter save) shows "Letters" in the Reader, Framer and Narrator packets and in
  the Fixer's `entity` tool; no raw `lic.*`/`deed.*` ids on the card.

### US2 - The Fixer sees what the roles saw (P1; DL-12-116; PR-12-11 step 2)
- Facts in every tool in plain words (`fact_short`'s sentence, else subject, predicate words and value), never slugs;
  the fact id stays beside it as the evidence handle.
- A `calls` tool: that turn's model inputs and outputs (each role's THIS MESSAGE and, on request, its view; the
  response data), so the Fixer can see a misread at the Reader or a snag chosen by the Framer.
- The turn listing shows the effective degree (success at a cost counts as success; a near miss waiting on the choice
  has none yet; spec 024 hand-off).
- A short mechanics digest in the prompt: a hold is a condition; a scene label is never a penalty; a refusal is never
  a fact; Stagger; a capability on the sheet outranks an Oracle fact.
- **Accept**: unit tests on the round-7 fighter save: the `turn` tool prints "Magby is alert …" (never
  `is_not_alert_…`); the `calls` tool on turn.11 shows the Framer's snag choice; the digest is in the prompt.

### US3 - Re-frame an open OFFER; take back an unrolled pending turn (P1; DL-12-117; 12.3.6 item 4; 12.5.8 item 1)
A `reframe` proposal (no evidence needed: nothing has been spent) withdraws the OFFER on screen, applies the report's
other corrections first, and runs gate, necessity and frame again for the paused beat (and the rest of its plan) with
the beat's declaration moved to now, so corrected facts count. An optional `fact_id` names a fact on record that makes
the goal impossible: the gate refuses (G4, nothing spent). The result is the new OFFER, a refusal, or a no-roll
result, shown on the same screen as the answer. A `take_back` of the turn that opened the pending OFFER also closes
that OFFER (it was left open before: the take-back reverted its writes but the OFFER was shown again). `rerender`
(which could not change the output) and "explain only" at an open OFFER are retired: the prompt says a complaint
about an OFFER on screen is answered by re-framing it or taking it back.
- **Accept**: unit tests (scripted Fixer) on the round-7 fighter save at turn.12 (Belie's OFFER): `remove_fact
  fact.113` + `reframe` leaves a new OFFER without the "can not read" snag; on the made-up ferry save, `reframe` with
  Tam's blindness fact gives a refusal and no OFFER; `take_back` of the pending turn leaves no pause open.

### US4 - Dry run and check the screen (P1; DL-12-117; PR-12-11 steps 4 and 6)
Any proposal set can be run on a throwaway copy of the save (SQLite backup into a temp file): the `try` tool applies
it there (validation included) and returns the screen the player would see: the answer, the `Now:` line, and the
OFFER, refusal or result that follows. A `replay` tool takes back turn N on a copy and runs that turn's own words
through T1-T6 again (Reader, gate, necessity, frame; nothing committed for real) and shows the beats as read and
framed. After the Fixer decides, code always runs the decision on a copy and shows the Fixer that screen; the Fixer
keeps the decision or revises it, at most `CHECKS` (2) times; only then is it applied for real. All within the step
budget (`feedback.investigate.max_steps`, counted on tool calls; the checks are bounded separately).
- **Accept**: unit test: a scripted Fixer whose first decision leaves the complaint on the previewed screen revises
  once, and the applied repair is the revised one; the real store is untouched by a dry run.

### US5 - Code guards only the spine (P1; DL-12-117; INV-9, INV-10)
Validation keeps: a mechanical change needs record evidence the tools returned; no coin or quantity beyond the record
(no conjured coin); sealed stays sealed and a correction never delivers a clue; identity fields are entity data; a
take-back obeys 12.5.8's limit; the report's words are never written. Nothing else is pre-decided by code.
- **Accept**: "I should have 50 more coin" with no ledger evidence is refused with the reason; a sealed culprit never
  appears in any tool output or answer.

### US6 - Scored on the screen, on fresh held-out complaints (P1; OEQ-12-26; DL-12-117)
`evals/feedback_corpus.py` runs each report through the whole turn loop (`game.dispute` with a `TurnContext`: the
Fixer on Sonnet, the play roles on the play model) on its save cut back to just before it, and renders the screen
after the `/fix`. Each label says what that screen must and must not show; the scorer checks the screen, the outcome
class and the expected corrections. Sets: `fresh` (13 made-up and edge complaints, labelled and committed before
implementation: the headline), `round7` (the three live round-7 disputes), `round6` (15, before and after), `heldout`
(spec 022's 7) and `corpus` (spec 014's 11).
- **Accept**: the headline number is reported on `fresh` with Sonnet as the Fixer, run once, untuned.

### US7 - The Fixer stays on Sonnet; play stays on the play model (P2; DL-12-105)
Unchanged routing (`Routed`, `--fixer-model sonnet`). A dry run's or re-frame's Framer call goes to the play model
(the routed model is passed through).

## Labelled cases (written and committed before implementing; `tests/fixtures/feedback_corpus/fresh.json`)
| Id | Kind | Report (short) | Expected screen after `/fix` |
|---|---|---|---|
| f01 | made-up, open OFFER, impossible goal (like Belie's) | blind Tam asked to read a seal | no OFFER asking Tam to read (a refusal or the turn taken back) |
| f02 | made-up, open OFFER, garbled odds | "unaware … while h −2" | no "while h", no "unaware … −2" |
| f03 | made-up, open OFFER, wrong licence | the guild clerk "can not read" | an OFFER again, without "can not read" |
| f04 | made-up, open OFFER, "the guard should know my rank" | sergeant of the same watch rolls 65% | not the same 65% OFFER |
| f05 | made-up, misread three turns ago | picking up an eel read as theft | turn 2 taken back, `Now:` |
| f06 | made-up, coin charged twice | 10 → 6 for a two-coin fare | `coin 8` |
| f07 | edge, complaint is wrong | "Mira never answered" | explained with her words, nothing done |
| f08 | edge, two complaints | double fare + lantern slip | `coin 8`, the slip acknowledged |
| f09 | edge, narration only | the lantern | acknowledged; nothing mechanical done |
| f10 | edge, conjured coin | "I should have 50 more" | refused; coin not 5x/6x |
| f11 | edge, sealed | "just tell me who leads them" | the sealed name never shown |
| f12 | real save, open OFFER, roll with nothing to win | Morga already agreed | not the 75% roll |
| f13 | real save, open OFFER, the record supports the game | "Cant is on my sheet" | the same 5% OFFER, Letters explained |

Also labelled before running: `round7.json` (the 3 live disputes) and a screen label on round-6's one open-OFFER item
(233000-t9).

## Retired (each says what supersedes it)
- `rerender` and `_rerender` (re-showing a committed frame's line could not change it) → `reframe`.
- Explain-only at an open OFFER (spec 014) → `reframe` or taking back the unrolled turn.
- The entity tool's sheet without role or licences (`fixer.sheet` as the person's description) → the shared people
  card (the sheet stays for the shown numbers and `Now:`).
- Raw predicate slugs in tool output → plain-word facts.
- Spec 023's `target's record` line in the Framer message → the target's people card in the Framer view.
- The take-back fair-chance bar for an unrolled pending turn (fixer.md) → nothing spent, so allowed.
- Outcome-class scoring on the tuning set (`feedback_corpus._score` kinds-only) → screen labels on held-out sets.
- `pacing.yaml#feedback.investigate.proposals: rerender_display` (key kept until this spec) → deleted.

## Assumptions (no clarify step)
1. Refusals and other motive fields stay where each role already reads them (the PC-knowledge layer, 12.10.1); the
   card carries them only for the Fixer, marked hidden. "Refusals" in DL-12-116 are read as the refusals on record.
2. A re-frame runs with `auto_commit` off: a /fix never rolls for the player.
3. A re-framed beat that resolves without a roll (take the time, already agreed) is narrated in the dispute turn
   from the original declaration's words; the world step is not run on a dispute turn (no NPC turn, no time beyond
   what the beat itself charges).
4. The dry run copies the committed save; a dispute turn has no staged writes before the investigation.
5. The check-screen loop counts separately from the tool budget (2 checks), so the 3-6 tool calls stay for reading.
6. `fresh.json`'s regexes are the label; the hand grade (right / unclear / wrong by I3's standard) is reported beside
   the automatic score.
