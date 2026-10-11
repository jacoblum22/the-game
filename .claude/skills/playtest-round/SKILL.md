---
name: "playtest-round"
description: "Run one improvement round on the AI Dungeon Master: playtest, trace root causes with investigators, synthesise structural fixes, get owner approval, run a rules wave, then engine specs, merge and gate. Use when asked to playtest, find what's wrong, analyse a round, or continue the redesign loop."
argument-hint: "Optional: personas, the focus of this round, or 'analysis only'"
user-invocable: true
disable-model-invocation: false
---

# One improvement round

Read `research_notes/Playtest round 2 solutions/HANDOFF-2026-10-09.md` first if you haven't this session. It holds
the state, the philosophy, the history and the details this skill summarises. The constitution's **Principle VIII**
governs every decision:
- code owns the spine, and the model owns language and judgment;
- check only by measured precision;
- truth only when it matters;
- whole over parts;
- remove friction before adding procedure;
- better context, not more rules;
- diagnose from evidence;
- the player is part of error correction.

**Worked examples for every step** are in `EXAMPLES.md`, next to this file. They are drawn from real rounds; match
their shape and tone.

## The one rule that shapes the loop
**Never state a cause for a problem from the surface.** Most first guesses have been wrong. Go straight to the
evidence with `root-cause-investigator` agents, then synthesise. No guess-then-check round-trips.

## Steps

### 1. Playtest
Run on Haiku, 15 turns each: **talker** and **fighter**, plus one more (explorer, newcomer or breaker) when you
need breadth.
```
py -3.12 evals/playtest.py --engine claude --player claude --engine-model haiku --persona <p> --turns 15 --quick-setup
```
- Also run `py -3.12 evals/longhorizon.py --mode scripted`, which is offline and free.
- Run Gemini only when the owner allows it.
- Run in the background. Don't merge while runs are going.

### 2. Collect symptoms. Don't diagnose.
- Read the `.findings.jsonl` player notes and stats, and list the symptoms.
- Record what the last fixes' targets did, with numbers.
- **Re-check every recorded "Revisit if" condition** (`grep -n "Revisit if" rules/appendix/fragments/DL-*.md` and the
  open items in `OVERNIGHT-LOG.md` and the handoff). List each one that has fired this round as a symptom. Round 7
  found two that had fired and were never acted on (DL-12-99, DL-01-36). Owner rule, 2026-10-09.
- Commit the transcripts.

### 3. Trace, with 3–4 `root-cause-investigator` agents in parallel
Split them by area: narration/text, NPCs/dialogue, mechanics/combat, feedback (`/fix`), context. Each brief gives:
- its symptoms, with run stamps and input numbers;
- any fix currently proposed, to be tested against;
- its report path.

The method is built into the agent type.

### 4. Synthesise
- Put the reports side by side and look for **cross-cutting causes**, where one cause sits behind several symptoms.
- Check them against the anti-pattern catalogue (handoff §3.3).
- Write `ROUNDn-ANALYSIS.md` (or `-PLAN.md`) in `research_notes/Playtest round 2 solutions/`. It covers:
  - the targets' results;
  - each symptom with its traced cause and evidence;
  - the cross-cutting causes;
  - **one structural fix per real problem, naming what it retires**;
  - small bugs listed separately as patches.
- Write each family in the **four-part plain format** first, then the traced evidence (see step 5 and
  `EXAMPLES.md`).
- Prefer deleting machinery over adding it.

### 5. Owner review, in the owner's style
- Plain words, no rules shorthand. Concrete examples ("vault the table and stab him: one roll or two?").
- Order the update:
  1. what the last fixes achieved, with numbers;
  2. **families T1, T2, T3…**, formed only *after* the investigators' traces;
  3. the recommended order;
  4. the decisions needed, each with 2–3 options and a recommendation.
- **A family is a traced root cause**, not a surface grouping of complaints. Give each family a plain-words title
  (what goes wrong in play, not the code's name for it: "The game flips a coin for things it already knows", not
  "Oracle pre-frame questions"), then four parts, in the owner's words, not the code's:
  1. **In plain words:** what goes wrong and why, in 2–4 sentences a player would follow. Name the mechanism
     ("a yes/no dice roll"), not the module (`ask_oracle`).
  2. **From the playtest:** the concrete instance that happened, with the run and input numbers: who, what the
     player did, what the game did wrong.
  3. **Another example (made up):** a *different* situation the same cause would break, chosen to show how far the
     problem reaches (another kind of person, action or scene). It is not a rewording of the playtest example. End
     on one line that generalises ("anything the game already knows about a person can be overwritten this way").
  4. **The fix, plainly:** what changes, in play terms, and in one line what it retires.

  The traced evidence (files, counts, code paths) follows in the analysis document, not in the phone summary.
  List small one-off bugs separately as patches.
- Keep each part short (the owner reads on a phone), but never drop a part: the two examples are what make a
  family understandable. Send documents with `SendUserFile`.
- Wait for approval of any principle or rules change.
- If the owner pushes back, take it seriously and re-trace.

### 6. Rules wave
Use `rules-worker` agents in a worktree, **one at a time, one fresh agent per slice** (Sonnet, a 100-turn cap; see
"Agents" below). A slice is 2–4 revisions or issues, one audit, or one sim. The wave report's `## Handoff` section
carries state between slices. Commit each slice's worktree before starting the next. Each slice's brief:
- start with `git reset --hard milestone-1-playable` (slice 1) or the previous slice's branch;
- which slice it is, and whether it is the **last** one (the last runs assemble, anchors and cards);
- revisions tagged `[revision: R2-x]`;
- DL entries quoting the owner, with a numbering range assigned so parallel agents don't collide;
- re-assemble the appendix, run the anchors, then compile `engine/build/compile_cards.py` **last**;
- the validator at 0/0;
- don't edit ch.13;
- report with an **engine checklist per spec**.

### 7. Engine specs
- One spec-kit feature per structural fix: specify → plan → tasks → analyze → implement. Skip clarify and record
  assumptions instead.
- **Split each spec into slices, one fresh `spec-implementer` agent per slice** (Sonnet, a 100-turn cap). One long
  agent re-reads its whole growing context on every turn; specs 020–029 averaged 270 turns, peaked at 400–710k
  context, and were about 70% of a week's usage.
  - Slice 1 is the design: specify → plan → tasks → analyze. Pass `model: opus` when the fix is design-heavy.
  - Then one slice per phase of `tasks.md` (merge small phases, so a slice is roughly 15–60 turns of work).
  - Run each slice with `isolation: worktree`. Slice 1 resets to `milestone-1-playable`; each later slice resets to
    the previous slice's branch. Merge the last slice's branch.
  - The handoff between slices is the ticked `tasks.md` plus `specs/<feature>/HANDOFF.md`. Don't paste earlier
    reports into the next brief.
  - Slices in parallel (separate file lanes) must say so in their briefs. Each then writes `HANDOFF-<slice>.md`,
    so the merge doesn't conflict. When merging, fold them into `HANDOFF.md` and delete the per-slice files.
  - If a slice stops at the turn cap (its output is marked partial), resume it with `SendMessage`. Don't restart it.
- Each runs in its own worktree with explicit **file lanes**.
- **At most 2 in parallel**, because of usage limits.
- Each brief includes:
  - reset to `milestone-1-playable`;
  - the evidence to test against;
  - real gates: tests built from real saves, live Haiku runs with a turn budget, and a held-out set labelled
    *before* looking at answers;
  - **made-up cases, including edge cases** (owner rule, 2026-10-09). Before implementing, the spec writes and labels
    situations it was *not* derived from:
    - the family's "another example";
    - other people, verbs and scenes the same cause would break;
    - deliberately hard edge cases (a smaller ask in other words, a folded method, an open OFFER, an absent person,
      a negated question);
    - **every kind the game's data has**, enumerated from the data, not imagined. For example, every lead and
      incident kind in `world_seed.yaml`, every verb, every gate reason. Round 8 found spec 025 had covered only the
      lead kinds round 7 happened to show.

    A fix is accepted only if it passes these as well as the save it came from. Round 7 traced T3, T6 and T7 to fixes
    each accepted on the one case that prompted them: one surface, one wording, a tuned scoring set;
  - "report real numbers, never fake a pass";
  - what to retire;
  - Edit/Write tools for code, never Git Bash heredocs;
  - re-record the replay if packets change;
  - commit on the worktree branch, with no push.

### 8. Merge and gate (the orchestrator, in the main checkout)
```bash
git merge --no-ff --no-commit <branch>
py -3.12 evals/orchestration/resolve_rules_merge.py   # prints MANUAL: for anything it can't resolve
bash evals/orchestration/regen_and_gate.sh            # assemble, anchors, cards last, validator, replay, full pytest
git commit -m "Merge … (gate numbers)\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
- Typical manual conflicts:
  - role lists: keep the new roles, drop the retired ones;
  - `CONVENTIONS.md` sections: keep both.
- If two specs pass separately but fail together, commit to an `integrate-x-y` branch, have a reconcile agent
  fix it, then fast-forward. Never commit a red merge to `milestone-1-playable`.
- Update `research_notes/Playtest round 2 solutions/OVERNIGHT-LOG.md` after each merge.
- Then go back to step 1.

## Agents (owner, 2026-10-10: the weekly usage limit is the binding constraint)
An agent's cost grows with the square of its length, because every turn re-reads the whole context. So use short
agents with a written handoff, and the cheapest model that can do the slice.

| Job | Agent type | Model |
|---|---|---|
| Trace causes (step 3) | `root-cause-investigator` | Opus (from its file) |
| Rules wave slice (step 6) | `rules-worker` | Sonnet; pass `model: opus` only for a design-heavy slice (a new mechanic, a principle or constitution change) |
| Spec design slice (step 7) | `spec-implementer` | Sonnet; pass `model: opus` when the fix is design-heavy |
| Spec implementation slice (step 7) | `spec-implementer` | Sonnet |
| Anything else (audits, prototypes, research) | the closest typed agent; `general-purpose` only as a last resort | Sonnet (the default, `CLAUDE_CODE_SUBAGENT_MODEL` in user settings); Opus only for design-heavy work |

- Prefer a typed agent over `general-purpose`. `general-purpose` starts at about 60k tokens per turn; the typed ones
  start at 12–27k.
- Auto-compaction triggers at about 380k tokens (`CLAUDE_CODE_AUTO_COMPACT_WINDOW=400000` in user settings). It is a
  safety net, not the plan; size slices so they finish well below it.
- A slice that stops at its turn cap returns partial output. Resume it with `SendMessage`; don't restart it.

## Standing constraints
- Don't push; the owner pushes.
- No Gemini until the owner says so.
- Use Haiku for the engine. Use Sonnet for the player persona and the `/fix` investigator.
- Run at most 2–3 agents at a time.
- Keep the spine:
  - structured state;
  - typed goals;
  - clue cases;
  - dice and the rubric;
  - the event store;
  - the feedback loop.
