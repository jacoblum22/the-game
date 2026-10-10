# R7-H2: history of T6 (rolls with nothing at stake) and T7 (`/fix` can't see enough)

Read-only trace. Code: `integrate-021` at 10a7b9f, the same as the round-7 build ed51aa7 for every file cited. Saves were opened with
`mode=ro`. The scratch scripts are outside the repo.

## Summary: where the history differs from "it was dealt with before"

1. **T6: the take-the-time path existed and spec 007 removed it.**
   - Before spec 007, the Reader proposed `necessity` and could choose `take_the_time`. The pipeline honoured it:
     `if beat.necessity != ROLLS: return _no_roll(...)` (`git show 144b2ff^:engine/resolve/pipeline.py:217`).
   - In the 75 saves from 2026-10-07, the Reader labelled `take_the_time` 71 times out of 605 necessity labels. The
     saves hold **65 frameless no-roll successes against 184 rolled frames**.
   - Spec 007 (144b2ff, merged 63801c8) deleted the Reader's `necessity` field (FR-001) and computed only "trivial or
     certain" in code (FR-004). Its research.md R2 explicitly rejected computing COSTLY: "a too-eager no-roll grants
     unearned successes".
   - Since spec 007 there are **0 frameless successes in the 13 saves**. This is a **regression (c)**, not a rule that
     was never built.
2. **P-024 was fixed at the screen, not at the roll.**
   - The fix for the "full odds screen for an unbarred wicket" was Safe auto-commit (DL-01-32). It still rolls.
   - It also excludes secret frames and frames below 50%. So the explorer's secret Observe got the full screen anyway.
   - `ISSUES.md` still lists P-024 as **open**.
3. **One of T6's two headline examples belongs to a different cause.**
   - Explorer turn.10 (the persuasion after a half-answer) was a **Risky** frame with a closed-door cost. 01.4.4 would
     not remove it.
   - The real miss is spec 018's "already true is certain" check (DL-01-36). An `agreed` fact covering a *larger* ask
     was on record and in the Framer's packet. `already_true`'s two-way word-overlap test at 60% missed it.
   - The roll then **shrank** the agreement: fact.118, "a smaller part of it", superseded fact.106.
4. **T7: the round-6 offline score hid the exact round-7 failure.**
   - Only 1 of the 15 round-6 disputes was raised at an open OFFER (233000-d1, pause 504).
   - On that one, `rerender turn.8` re-showed a *different, already-rolled* frame from the same turn: frame.3 at seq
     488, the arm-twist, not the disputed threat.
   - It was graded right, because the scorer checks only the outcome class and the kinds applied
     (`evals/feedback_corpus.py:124-138`).
   - The set was also the one the prompt was tuned on ("tuned on this set; not a clean number"). The untuned held-out
     set scored 4/1/2. Both of its misses were the missing mechanics digest, which was handed off and never built.

---

## T6. Rolls with nothing at stake

### Round-7 instances (re-verified)

Seven OFFERs over three runs. Each is shown with its frame (from `frame_committed` or the `pause_opened` detail) and
its classification.

| Run / turn | Act | Verb | Stakes / source | Threatened cost (`on_failure`) | Shown | 01.4.1 COSTLY? |
|---|---|---|---|---|---|---|
| talker t8 (seq 468) | steady the cask with Hssaoo | help | safe / none | cost.drain (None) | `OFFER — auto`, failed | **no**: take the time |
| talker t12 (seq 521) | buy the sellsword a round | — | safe / none | cost.closed_door (None) | `OFFER — auto`, near miss | **no** by the frame's own `on_failure: None`. The offer is the NPC's to accept, not a roll. |
| explorer t12 (seq 626/631) | sit and listen to the refugees | observe | safe / none, **secret** | cost.time on fact.116 (None) | full OFFER, "you can't judge how hard this is", then a d20 of 1 and `[RESULT] hidden check made.` | **no**: take the time |
| fighter t9 (seq 447) | read the list (G3 fallback, hard +5) | observe | safe / none | cost.drain (None) | full OFFER, 5% | arguable. 0c15da2 (P-087) forces every accepted fallback to roll. |
| fighter t5 | pick Magby's pocket | — | dire | exposure | full | yes |
| fighter t11 | persuade Belie to read | talk | risky | closed_door on fact.91 | full | yes; it is impossible (T1) |
| explorer t10 (seq 590) | persuade Morga to let Haley sit and listen | **help** | risky | closed_door on **fact.105** (Oracle: "not willing") | full, 75% | yes as framed. But it was **already agreed** (fact.106); see below. |

Take the time would have removed **3 clean cases of 7 OFFERs** (3 of the 5 committed rolls), plus 1 arguable case. In
every one of the 3 clean cases the frame itself carries the "not costly" signal: `stakes.source: none` and
`on_failure: None`. Code computes that signal and then rolls anyway.

**Explorer t10 in detail.** This is the case ROUND7-ANALYSIS cites as "persuading someone who has already half-agreed".
- **Turn.4:** a certain talk wrote fact.106: `npc.morga_embershield agreed = "Morga lets Haley hear the refugees' story
  from them directly"` (seq 497). In the same turn the Oracle wrote fact.105, `is_willing_to_let_haley_hear… = false`
  (seq 493, d100 42 on even).
- **Turn.10:** the Reader typed `persuade_to` with `verb.help`, `asks: false` and `pressure: request`. Two consequences:
  - `certain_talk` (necessity.py:66) would fail on `asks` even with `verb.talk`. The verb label is not the cause I3
    names.
  - `already_true` (change.py:153-160) runs `covers(done, act, 0.6) and covers(act, done, 0.6)`. Run on the two
    strings, both directions return `False`.
- **Framer (row 27):** the packet listed fact.106 *and* fact.105 one line apart. The Framer framed Risky on
  `goodwill_or_trust` with `closed_door` sourced to fact.105.
- **Result:** a limited success. fact.118, `agreed = "a smaller part of it (…sit near… and listen…)"`, superseded
  fact.106 at seq 596. **The needless roll took away part of an agreement the player already had.**

### Earlier, similar bugs

| # | Original symptom (id, round) | Diagnosed then | Built (commit / spec / DL) | Why it didn't hold in round 7 |
|---|---|---|---|---|
| 1 | **P-024** (round 1, fighter 161325 inputs 29–32): "Trivial acts get a full odds screen (opening an unbarred wicket 'easy obstacle'); a shout at 35% with 20% critical failure" | Lane D (`D_adjudication_difficulty.md` P3) and synthesis D7, three parts: (i) trivial means the class base is trivial; (ii) an observer is COSTLY only if it would act; (iii) "a quieter OFFER for safe beats", meaning auto-commit, which "answers P-024's full odds screen". | R2-C rules (91fc837). Spec 007 (144b2ff, merged 63801c8): `necessity()` with `plain_reading`, `certain_talk` and `trivial_class` after framing; `parties_who_would_act`, used **only to narrow the stakes source**; `auto_commit_allowed` (frame.py:878-882, DL-01-32). | **(d) plus (a).** The symptom was read as a *presentation* problem, so auto-commit still rolls the die, and a failure still costs. Auto-commit excludes secret frames and frames under 50%, which is why the explorer's listen got the full screen. Part (i) handles UNCERTAIN = false (anyone succeeds). Round 7's cases are UNCERTAIN = true but COSTLY = false: exactly 01.4.4, which no part addressed. P-024 is still "open" in `evals/playtests/ISSUES.md:33`. |
| 2 | **The Reader's own take-the-time** (rounds 1 to 3, pre-007) | Pre-007 `reader.md:48-50`: "`necessity`… Another reason only when its card plainly applies". The Reader chose `take_the_time` in 71 of 605 labels, and the pipeline skipped the roll. One misfire: **P-087** (192159-newcomer), take the time on an accepted fallback gave "You cannot do it that way". | 0c15da2 forced accepted fallbacks to roll (pipeline.py:726-733). Then spec 007 FR-001 **removed the Reader's necessity field**, and FR-004 computed only trivial and certain. research.md R2: "computing COSTLY fully before framing (rejected for now…)". The `take_the_time` tuple at pipeline.py:45 is all that survives. | **(c) regressed by spec 007.** The only producer of `take_the_time` was deleted and no code producer replaced it. `grep take_the_time engine/**/*.py` finds only the tuple and a comment. Measured: frameless no-roll evidence (basis `take_the_time`, `good_idea` or `certain_with_cost`) is 65 in the 2026-10-07 saves and 0 in all 13 saves since. |
| 3 | **P-075** (rolling run 185715-talker 28–31): "An NPC already agreed ('Yes' to meeting) yet the follow-up ask rolls at 50% with a closed-door risk" | 01.4.2 riding was never implemented. | 3c6cbbf: `_rides` (pipeline.py:526-544). The beat rides an earlier *rolled* success with the same actor, target, anchor, attribute and method class. | **(b) bypassed.** Morga's agreement came from a no-roll certain talk at turn.4, so there is no frame and `_rides` cannot see it. |
| 4 | **Round 4 R5** ("persuade Ivas", rolled at 60% after she had already agreed; ROUND4-ANALYSIS line 45) | "A change's applicability is checked only after the roll… a change already true is certain." | Spec 018 US4 (e783e76, merge 516af3f), DL-01-36: `already_true` (change.py:138-161). For `persuade_to` it requires two-way 60% content-stem overlap with the `agreed` text. The acceptance test was the single same-words case (talker t5). | **(a) built for a narrower surface:** a re-ask in nearly the same words. A *smaller* ask in other words fails both directions. DL-01-36's own "Revisit if: … an already-true change rolled" has now fired, and so has "…a rolled beat whose success applied nothing" (talker t8 and t12 typed `change: none`). |
| 5 | **Round 4 R3** (fighter: "two rolls were automatic for walking", four turns of looking for the refugees) | No find procedure; an approach rolled band by band. | Spec 018 US3, DL-12-98: `looks_here` (necessity.py:97-104) and approach as Move/open_ground with a `trivial` base. | **(a) a Move-only carve-out** of decision 1. Round 7's needless rolls were Help, Observe and an offer. |

### Is it the same root cause?

**Yes. It is the same as P-024 at the root:** code has never evaluated 01.4.1 decision 2 (COSTLY) as a no-roll test.
- Every fix since round 1 added a *verb- or case-specific carve-out of decision 1*: plain reading, plain question,
  open ground, a move to here, already true.
- The one general mechanism, the Reader's model-proposed `take_the_time`, was removed in spec 007 and not replaced.
- Safe auto-commit then hid the remaining Safe rolls behind a shorter screen. It still spends a die and can still fail.
- The share of Safe frames among committed rolls never fell: 80/186 (43%) on 10-07, 12/28 (43%) on 10-08, 3/5 (60%) in
  round 7.

### What a fix must do differently to hold

1. **Decide on the typed frame, after framing, in one place, for every verb.**
   - Condition: `stakes.source == none` and `on_failure is None` and no clock listening to the beat or to time and not
     a conflict and tier below Very hard. Then the reason is `take_the_time`: no OFFER, no roll, Standard reach, and
     `advance_time` for twice the mode's time (01.4.4).
   - The time cost must actually be written. Today `_no_roll` (pipeline.py:387-409) writes no time at all.
   - Do not key it on verb labels or text. The Framer already supplies the signal.
2. **Settle the fallback question explicitly** (rule owner): 0c15da2 forces rolls on all fallbacks, but 01.4.4 does
   not exempt them.
3. **Retire Safe auto-commit** for frames take the time now covers (DL-01-32 becomes nearly dead code). Keep it only if
   some Safe-but-costly class remains.
4. **Make "already agreed" typed, not textual.** An `agreed` record holds the request's target, act and size (R1–R5).
   A new `persuade_to` whose act is equal to or smaller than an agreement on record is `already_true`. This
   generalises to subset asks, and it must not let a later roll *replace* the larger agreement.
5. **Precision guard.** Before trusting `stakes.source: none`, have code check it against the frame's own costs. The
   talker t12 frame threatened closed_door with source none. A frame that names a door-closing cost on failure is
   COSTLY.
6. **Accept on breadth, not on the reported save.** Use a seeded sweep over the golden set and the round-1 to round-7
   saves: count Safe frames that still roll (target 0, except Very hard and above) and subset re-asks that roll. Spec
   018's single-case acceptance is why the 60% overlap shipped.

---

## T7. `/fix` can't see enough

### Round-7 instances (re-verified)

At **2 of the 3** `/fix` reports (both of the mechanical ones), an OFFER was open:

| Report | Input | Open pause at report |
|---|---|---|
| fighter dsp.1 | n=22 | pause 414, the pickpocket OFFER |
| fighter dsp.2 | n=28 | pause 456, the Belie OFFER |
| talker dsp.1 | n=30 | none (a pronoun complaint; graded right) |

**fighter dsp.2: the tools the Fixer used, and what was missing.**
- Tools used: `turn(turn.12)`, `turn(turn.11)` and `entity(npc.belie_greenwort)`.
- The entity tool returned "sheet: state fresh · conditions none · holding nothing" plus three facts, among them
  `fact.113 … can_read_the_writing… = false (source oracle)`. That comes from `fixer.py:_entity_tool` 218-240 and
  `sheet` 106-129.
- Belie's record has `role: "scribe and teacher of letters"` and `licenses: [lic.lang.letters, …]` (entity_created,
  seq 222). Neither appears anywhere in either Fixer request: "scribe" occurs 0 times in rows 26 and 27. PEOPLE IN
  VIEW gives only name and pronouns.

**fighter dsp.2: what the Fixer did.**
- The prompt says "Prefer the record over the narration" (`fixer.md:56`), so the Fixer took the Oracle fact as the
  record and answered `explain`.
- `take_back` is barred by `fixer.md:47-48` ("only for a turn the player never had a fair chance at").
- `PROPOSALS` (fixer.py:27) has no kind that re-frames or withdraws an open OFFER. `dispute.py` never touches the open
  pause, so the same OFFER is re-shown.

**fighter dsp.1: what the Fixer did.**
- It proposed `rerender`. `_rerender` (dispute.py:308-325) scans only `frame_committed`, and turn.5's frame was still
  a pause, so the call was a silent no-op.
- Even on a committed frame it would call the same `_breakdown → fact_short` on the same fact.
- The `turn` tool printed the raw negated slug `is_not_alert_…_while_h = false`, and Sonnet misread it as "Magby is
  not alert".

### Earlier, similar bugs

| # | Original symptom (round) | Diagnosed then | Built | Why it didn't hold |
|---|---|---|---|---|
| 1 | **Round 5 T4:** "a garbled OFFER line answered with 'it stays' and then reprinted unchanged" (ROUND5-ANALYSIS:93-114) | "No category for display errors… No visible repair." Proposed: `display_error`: acknowledge, re-render, log. | Spec 014 (40d4a4a), by design: "A complaint about an open OFFER (no committed frame yet): explained from the offer's levers and their facts" (spec.md:64). Explanation only, no repair. | **(e) never built.** The repair for an open OFFER was explicitly "explain" in 014 and stayed that way. |
| 2 | **Round 6, 233000 d1:** the garbled Chance line at an **open** threat OFFER (pause 504), pinned as a fact and "reprinted at turns 9, 12 and 13" (I3 §5) | I3 §5: `display_error` is only **partial**: "Re-rendering… prints the same garble, because the garble is the stored fact." The source fix belongs in `settle`/`fact_short`. | Spec 022 (aefbbfe, 636a9f1, d685518; merge e8768cd) built `rerender` anyway, over `frame_committed` only. Spec 021 fixed the *testimony* source of garbles. | **(d) plus (a).** The warning that a re-render cannot change anything was not acted on, and `rerender` covers only rolled frames. The round-7 garble's source is an **Oracle** fact (`turn.py:_fiction_questions` → `oof.fact_short`), a path 021 did not touch (I3 §1). |
| 3 | **Round 6, the whole set:** 1/6/8 of 15 (I3 §5): complaint text pinned, sequential settlement, subject-only lookups (bond on the PC, positions), branch order | Missing lookups and outcomes. All code, not the model (understood 14/15). | ROUND6-PLAN F6 → spec 022: six read-only tools, chosen for exactly those lookups (bond, position, ledger, said vs record). The plan's "an entity's state and the provenance of each fact" became `sheet()`: quantities, harm word, conditions, held items. | **(a) fitted to round 6's complaint types.** No round-6 complaint needed an NPC's role or licences, so the entity card never got them. |
| 4 | **Spec 022's held-out set:** 4/1/2. The misses h1 (a held foe's crutch blow) and h7 (the "straining against you" self-snag) were "rule knowledge the Fixer is not given" | Hand-off: "a short mechanics digest (holds, scene labels never snags, refusals never facts, Stagger)". | Nothing. `OVERNIGHT-LOG.md:338` lists it as "Open after the four specs". `fixer.md` has one Stagger line (59). | **(e) never built.** |

### Why spec 022's 10/3/2 did not carry over to round 7's 1/0/2

1. **It was the tuning set.**
   - implementation-results: "with the fix: 10 / 4 / 1 (tuned on this set; not a clean number)".
   - The untuned held-out set (7 complaints, labelled first) scored **4 right, 1 unclear, 2 wrong**. That is 57% right,
     closer to round 7 than to 10/15.
   - The same pattern appeared before: spec 014 reached 11/11 on its tuned corpus, and then round 6 went 1/6/8 live.
2. **The set was different in kind.**
   - Round 6: 14 of the 15 complaints were about the record *after* the fact: pronouns, positions, a bond, coin, a
     testimony line, a take-back. 1 of 15 was raised at an open OFFER.
   - Round 7: 2 of 3 were raised at an open OFFER. A live player disputes the OFFER *before* committing, so this
     share will stay high.
   - Round 6's bad facts were testimony (`said.*`), which has its own repair (`correct_testimony`). Round 7's were
     Oracle facts about an NPC's capability. Refuting those needs the licence, which the entity tool hides.
3. **The scorer passed the one open-OFFER case, and that pass was wrong.**
   - In `evals/baselines/fixer_round6_sonnet.json`, 233000-t9 shows `done: … "turn 8 shown again: \"Twist Dunwen's
     arm up behind her back\": Chance 50% (…Dunwen is straining against you −2)"`.
   - That line is frame.3, committed at seq 488 in turn.8. The complaint was about the *threat* OFFER, pause 504, which
     was still open at seq 506.
   - The label (`tests/fixtures/feedback_corpus/round6.json`) expected only `class: upheld` and `done:
     [correct_testimony]`.
   - `feedback_corpus.py:_score` checks the class and whether any expected kind was applied. It never checks which
     frame was shown or what the player would see next.
4. **The replay stops at the answer.** The harness cuts the save at `open_at` and runs `settle_dispute`. It never
   renders the next screen, so "re-shows the same broken OFFER" cannot be observed offline.
5. **Tools exercised offline but not live, and the reverse.**
   - Offline, `rerender` was used once, and on the wrong frame.
   - `entity` was called on Dunwen, Branwen, Lilett and Sevella. Every complaint about them was settled by pronouns
     or facts, never by role or licences.
   - Live, the one complaint that needed `entity` to show licences hit the gap at once.

### Is it the same root cause?

**Partly the same, partly new.**
- **Same since spec 014:** `/fix` has no repair for an **open OFFER**, only an explanation. This is the third round
  running in which a disputed OFFER line was re-shown unchanged: round 5 T4, round 6 233000-d1, round 7 dsp.1 and
  dsp.2.
- **New with spec 022:** the tools are narrower than the record. The entity card has no role, licences or competence,
  and the turn tool prints raw negated slugs.
- **Upstream (shared with T1):** both round-7 mechanical complaints were caused by blind Oracle facts. The Fixer is
  being asked to repair a defect the pipeline keeps producing.

### What a fix must do differently to hold

1. **Add a `reframe` proposal for an open pause.**
   - Withdraw the open OFFER for free (nothing is spent) and apply the fact corrections.
   - Re-run gate, necessity and frame. Show the new OFFER, or a G4 when the goal is impossible.
   - Allow `take_back` of an unrolled pending turn without the "fair chance" bar.
   - Retire `rerender`: it cannot change output, by construction.
2. **Show the people card from one shared renderer.** The tools should render each person through the same function
   that builds the people card for the Reader, Framer and Narrator: role, licences, competence, stance and refusals.
   Then a tool cannot know less than a role did, and the round-to-round "add the field the last complaint needed"
   cycle stops.
3. **Print facts in plain words.** The tools should print facts as the narrator reads them, de-negated: the same
   `fact_short` fix as T1. Raw predicate slugs should never appear.
4. **Add the mechanics digest that 022 handed off.** It covers holds, scene labels never being snags, refusals never
   being facts, Stagger, and "a capability on the sheet outranks an Oracle fact". Also qualify `fixer.md:56`: when the
   record contradicts itself, the typed sheet wins over an Oracle fact.
5. **Change the acceptance test.**
   - Replay must render the screen after the `/fix`, and the label must say what that screen should show.
   - Score on complaints from a *different* round than the one the prompt was tuned on: the 3 round-7 disputes plus
     synthetic open-OFFER complaints (an impossible goal, a garbled snag, a wrong licence).
   - Report the held-out number as the headline.

---

## Shared causes across T6 and T7

| Shared cause | T6 | T7 |
|---|---|---|
| **Fixes fitted to the last round's surface** (anti-pattern: test traps) | carve-outs for doors and open ground, plain reading, same-words agreement | tools for bond, position, pronoun and testimony; `rerender` for rolled frames |
| **Acceptance on the reported case or the tuning set** | spec 018 US4 accepted on one same-words save turn | spec 022 scored on the tuned round-6 set. Its one open-OFFER item was mis-graded right by a kinds-only scorer. |
| **A general mechanism removed or deferred, then patched piecemeal** | spec 007 removed the Reader's `take_the_time` and rejected computing COSTLY | spec 014 decided that open-OFFER complaints get "explained", and spec 022 kept it |
| **Blind Oracle facts (T1)** | fact.105 ("not willing") was the closed-door source for the needless persuade roll | fact.106 and fact.113 caused both mechanical disputes |

**Anti-pattern catalogue.**
- **Low-precision check:** `already_true`'s word overlap; in practice it is low-*recall*.
- **Test traps:** spec 018's single-case acceptance; spec 022's tuned set and kinds-only scorer.
- **Blind model call:** the Fixer's entity tool.
- **Wrong context:** raw negated slugs in the `turn` tool.
- **Instruction that forces the behaviour:** `fixer.md:56`, "Prefer the record", when the record is an Oracle guess.
- **Over-triggering:** Safe frames always roll.

## Evidence index
- **Saves:**
  - `saves/playtest-20261009-160642-explorer.db`: seq 493, 497, 585-596, 626-643; model_calls rows 27 and 31.
  - `saves/playtest-20261009-160622-fighter.db`: seq 222, 414, 447, 456; model_calls rows 16, 17, 26 and 27; and its
    `.disputes.md`.
  - `saves/playtest-20261008-233000-fighter.db`: seq 485-516, game_inputs n=25.
- **Baselines:** `evals/baselines/fixer_round6_sonnet.json` (233000-t9) and
  `tests/fixtures/feedback_corpus/round6.json`.
- **Code:**
  - `engine/resolve/necessity.py` 59-104;
  - `engine/resolve/pipeline.py` 45, 387-409, 510-524, 726-733;
  - `engine/resolve/frame.py` 878-882;
  - `engine/resolve/change.py` 138-161;
  - `engine/dm/fixer.py` 27, 106-129, 218-240;
  - `engine/dm/dispute.py` 308-325;
  - `engine/dm/roles/prompts/fixer.md` 47-49, 56;
  - `evals/feedback_corpus.py` 124-138.
- **Commits:**
  - 0c15da2 (P-087 fallback rolls);
  - 3c6cbbf (P-075 riding);
  - 144b2ff and 63801c8 (spec 007);
  - e783e76 and 516af3f (spec 018);
  - 40d4a4a (spec 014);
  - aefbbfe, 636a9f1, d685518 and e8768cd (spec 022).
- **Decisions:** DL-01-09, DL-01-32, DL-01-36, DL-12-98. **Specs:** spec 007 research.md R2, spec 014 spec.md:64.
