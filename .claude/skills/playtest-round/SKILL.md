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
Use **one** `rules-worker` agent in a worktree. Its brief:
- start with `git reset --hard milestone-1-playable`;
- revisions tagged `[revision: R2-x]`;
- DL entries quoting the owner, with a numbering range assigned so parallel agents don't collide;
- re-assemble the appendix, run the anchors, then compile `engine/build/compile_cards.py` **last**;
- the validator at 0/0;
- don't edit ch.13;
- report with an **engine checklist per spec**.

### 7. Engine specs
- One spec-kit feature per structural fix: specify → plan → tasks → analyze → implement. Skip clarify and record
  assumptions instead.
- Each runs in its own worktree with explicit **file lanes**.
- **At most 2 in parallel**, because of usage limits.
- Each brief includes:
  - reset to `milestone-1-playable`;
  - the evidence to test against;
  - real gates: tests built from real saves, live Haiku runs with a turn budget, and a held-out set labelled
    *before* looking at answers;
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
