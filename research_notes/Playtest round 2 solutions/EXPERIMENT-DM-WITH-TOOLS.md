# Experiment: one DM model with tools, versus the current pipeline

**Status:** approved by the owner on 2026-10-10. It starts after specs 028 and 029 merge. Spec 030 is on hold until
the result is in.

**The owner's framing:** "my original plan here was just to create the mechanical rules. The D&D style advancement
rules. And then I just wanted to have the LLM play with them. But I think the code might be holding us back. But
maybe I'm wrong." The owner chose the experiment over a rewrite or more incremental rounds. Gemini is not part of
the experiment yet.

## The question
Do we get better play, at similar or lower cost, if one model acts as the DM each turn and uses **tools** over a
mechanical spine kept in code? The alternative is today's pipeline: about 10 model roles glued together by code
heuristics.

## What code keeps (the spine)
- **Dice and odds.** A `roll` tool takes the DM's typed proposal (goal, approach, difficulty factors) and computes
  the odds from the rules: attributes, licences, the tier rubric and costs. Code rolls and reports the result.
- **State.** Health, conditions (holds included), coin, items, positions (place and range band), presence, time,
  clocks and advancement. These are read and written through tools. A write is refused only when the game can't hold
  it: someone dead acting, an item not owned, coin from no source, an unknown entity.
- **Memory.** The event log, scene cards, said and testimony records, and the journal, all reached through `recall` /
  `lookup` tools.
- **Mysteries.** The case graph stays in code. A `reveal_clue` tool hands over a clue held by someone the player is
  talking to.

  **The secrets variant (an arm of the test):** the DM sees each present NPC's private knowledge, so a culprit can
  act guilty. Leaks are measured, not prevented.
- **Character rules and advancement**, unchanged.

## What the DM model does
Each turn, the DM reads the player's message and the recent conversation. It decides what needs a roll and proposes
it through the tool, then reads the result. It decides who answers and how people react; each NPC's dice-set mood
and the "most they'll do" ceiling are given as facts. It writes the passage and updates state through tools.

The OFFER screen (odds shown before committing) stays a code-rendered pause when a roll is proposed.

## Build
- **Reuse, don't rewrite:**
  - the store and projection;
  - the dice and odds functions (`resolve/`);
  - the rules data;
  - seed packs, casting and case builders (spec 029's terms);
  - the people card renderer (spec 026);
  - the `/fix` tool layer (spec 026), which already reads the game state through tools.
- **New:**
  - a tool-calling loop for one DM role, on the Claude CLI (Haiku), bounded to a small number of tool calls per turn;
  - a short DM guidance prompt;
  - adapters so `evals/playtest.py` and `evals/longhorizon.py` can run either engine.
- **Scope:** a prototype behind a flag (`--engine dm-tools`). The current pipeline stays the default.

## Test
- **Arms:**
  - (1) the current pipeline, after specs 028 and 029;
  - (2) DM with tools, NPC secrets hidden;
  - (3) DM with tools, NPCs' private knowledge visible.
- **The same inputs:**
  - the scripted long-horizon lines;
  - the seeded NPC scenes from spec 028's `evals/npc_agency.py`;
  - talker, fighter and explorer persona runs on Haiku, 15 turns each, Sonnet as the player.
- **Measures:**
  - wrong speaker;
  - contradictions with the record;
  - pushover rate by mood and cost, and ceiling violations;
  - clues delivered;
  - secret leaks;
  - needless rolls;
  - state errors (coin, holds, dead acting);
  - repetition;
  - player-reported problems per run;
  - model calls and tokens per turn;
  - latency.
- **Decision rule.** The owner decides from the numbers. A clear win on play quality, at no more than about 1.5×
  today's cost per turn, is the signal to move to the new design.

## Owner rules that still apply
- Diagnose from evidence.
- Made-up and edge cases, plus a held-out set.
- Sonnet for well-defined agents.
- Haiku for the engine.
- No pushing.
