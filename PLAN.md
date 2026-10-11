# MVP plan: an AI DM for D&D 5e (draft for the owner to edit)

## Goal
A new player sits at a terminal, picks a character, and plays a whole session of about 60 turns with an AI DM.
The session is good enough to show someone.

## Decided (owner, 2026-10-11)
- **Rules:** D&D 5e, the 2014 rules. The model already knows them, so we don't paste in a rulebook.
- **DM model:** Sonnet (`claude-sonnet-5-5`). Test cheaper models later.
- **Interface:** a plain terminal chat.
- **Tools:** roll, a character sheet with a fight tracker, and a rules lookup.
- **Content:** SRD 5.1 only, so the product can be sold as is, credited under its licence.
- **Characters:** three ready-made level-1 characters: a fighter, a rogue and a wizard, each with its SRD subclass.
- **The adventure:** the DM improvises from a one-paragraph opening written for each character.
- **Paying for the model:** the same way as the old playtests, through the Claude Code CLI on the owner's
  subscription. The Claude Agent SDK runs the CLI with real tool calls. Switching to an API key later is a
  setting.

## How it works
- **One model runs the game.** It receives:
  - short DM instructions (a few pages at most);
  - the current character sheet and fight tracker;
  - the conversation so far.

  It writes all the story and decides when to call a tool.
- **`roll(dice, reason)`:** real dice, such as `1d20+5`, with advantage and disadvantage. The player sees every
  roll.
- **The character sheet and tracker** hold HP, spell slots, items, gold, conditions, XP, the initiative order and
  monster HP.
  - The DM states what changed. Code does the arithmetic and refuses impossible changes, such as spending a slot
    you don't have.
  - The current sheet is shown to the DM every turn.
- **`lookup(query)`:** searches the SRD 5.1 text for exact spells, monster stat blocks, conditions and rules.
- **Code never decides the story.** It never picks a monster's move and never infers anything from what the
  player typed. In a fight the DM runs each creature on its own turn, in initiative order, looking at the
  tracker as it is at that moment.
- **Saving:** each game saves its transcript and sheet to a file, so a game can be resumed.

## The DM instructions (a short text)
- How to run the table: offer choices, keep scenes moving, and call for checks the way 5e does.
- How to use the tools:
  - never invent a die result;
  - always record damage, healing, spent slots, items and conditions through the sheet;
  - look up anything exact instead of guessing.
- A short list of 5e rules that models get wrong. It starts empty and grows from what we see in play.

## Not in the MVP
- character creation;
- a memory system (60 turns should fit in context);
- a second model that checks the first;
- maps, images, web or multiplayer.

Each of these gets added only if play shows it's needed.

## How we test
- **One small automated test:** the dice and the sheet arithmetic.
- **Playtests:**
  - the owner plays a session;
  - an AI player (Sonnet) plays a few 60-turn runs and notes what bothered it;
  - we read the transcripts and fix only what actually went wrong.
- **Baseline:** the same runs with **no tools** (the "dad version"), to see what the tools add.
- **Counted in every run:**
  - die results the DM made up;
  - HP, slots or items that drifted from the sheet;
  - 5e rules applied wrongly;
  - dead ends and contradictions.

## Order of work
1. A terminal loop, the DM instructions, `roll`, the sheet and tracker, and three characters. Play it.
2. Add `lookup` with the SRD 5.1 text. Downloading the text needs the owner's OK.
3. Build the AI-player harness and run the no-tools comparison.
4. Fix what play showed. Repeat until a session is worth showing.

## Open questions
- None for step 1. Before selling: the model must run on an API key (subscription use covers our own
  development and playtests), and a lawyer should check the SRD credit and the "compatible with 5e" wording.
