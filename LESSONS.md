# Lessons from the first build (2026-09-28 → 2026-10-11)

**What we built.**
- A custom ruleset of 573,000 words.
- A Python engine that implemented part of it.
- First a pipeline of model roles, then one DM model with tools.
- About eight playtest rounds, with Haiku as the DM and Sonnet playing the player.

On 2026-10-11 we reset everything. The old work is archived under the git tags `archive/pre-reset/*`
(`milestone-1-playable` and `spec033-base` are the latest).

## The big lesson: the rules must be something the DM model reads and follows
- **Our ruleset was written as a spec for code.** It has 1,241 procedure and table cards, hundreds of handlers and
  trigger hooks, and lines like "default occupant of `slot.defense_reaction` at priority rank 0". That made the
  game an engine project that never ends.
- **The engine fell quietly behind the rules.** The final audit found these missing:
  - turn order;
  - reactions;
  - enemies' second action;
  - the fate reroll the game promised;
  - abilities;
  - 80 of 105 rule handlers.

  So no playtest ever tested our rules. It tested the engine as built.
- **A model already knows D&D from training. It knows nothing about our system.** Whatever it needs must fit in its
  context on every turn. 573k words is roughly 750k tokens, several times too big. Treat size as a design limit from
  day one.
- **Design the system for an AI DM.** Ask of every rule:
  - Can a model apply it consistently from a short text?
  - Or does it need a tool?

## The DM model and tools
- **One DM model with tools beat a pipeline of specialist roles** (experiment, 2026-10-10):
  - about a third of the tokens;
  - 0.4× the time per turn;
  - fewer contradictions (5 and 3, against 10);
  - fewer repairs.
- **Haiku is a workable DM** when its context is good: about 15–20 s and 15–30k tokens per turn. Most failures were
  ours (wrong context, too much machinery), not the model's.
- **Tools are for what must be exact:** dice, damage, coin, items, and state the model must not forget. The model
  owns language and judgment.
- **The model decides; code records and does the arithmetic.** Code must never work out story facts from words:
  positions, who is present, identity, an enemy's choice. Word matching over prose failed every time we tried it.
  When code and story disagree, give the DM a tool or a field. Never add a guess.
- **A logged default is fine for a detail the model left out.** It must never stand in for a decision someone is
  supposed to make, such as an enemy's move.
- **Decisions need the current state.** Picking every enemy's move at once broke as soon as the first move changed
  the field.
- **Whole over parts.** Models read whole messages and write whole passages. Splitting narration or dialogue into
  pieces made it choppy, and repairs made on pieces were blind to the whole.
- **Better context beats more rules.**
  - 70–87% of a role's input was rule text.
  - What helps is the situation: who is here, with pronouns and relationships, what just happened, and what is at
    stake.
  - Add only short guidance for the judgment being made.
- **Give the narrator facts, never orders.** Pushing details and reactions made it repeat them.
- **NPC speech is testimony, not fact.** It becomes true only when the player acts on it.
- **The player is part of error correction.** A real "/fix, that's wrong" channel lets the rest stay loose.

## Checks and measurement
- **Block only on checks that are right most of the time.** A "was the question answered?" check that was right
  about 6% of the time corrupted the prose.
- **Keep a held-out test set,** labelled before looking at the answers.
- **Test against the rules, not just the code.** Tests that prove the code matches its spec are worthless once the
  spec drifts from the rules.
- **An AI player persona with notes on what bothered it** worked well as a playtest harness.

## How we work
- **Agree on what we're making before building.** Don't run ahead.
- **Trace before diagnosing.** About 10 of 13 first guesses at a cause were wrong.
- **Observe before solving.** Let the model run, then fix what actually goes wrong in play.
- **Prefer deleting machinery to adding it.** Fixes aren't sacred.
- **Never quietly simplify the rules.** A deviation goes to the owner first. Never rewrite a rule to describe the
  code.
- **Updates for the owner:** plain words, examples, short enough for a phone.
- **Agents:** short slices on Sonnet with written handoffs. Context size is the cost.

## Ideas from the old ruleset that may still be worth reusing (ideas, not text)
- The player can try anything.
- Mechanics stay hidden.
- One way to resolve a check.
- Foes show tells instead of numbers.
- Death is real but always telegraphed.
