# How to read a block (for the reading agents)

You are reviewing a block of a solo D&D 5e (2014 rules, SRD 5.1) game run by an AI DM, for the game's developer. The
file has each round: the player's line, the game's lines (`[game]`: dice, sheet changes, fight tracker, clock), the
DM's hidden notebook writes and lookups (`[DM ... (hidden)]`, never seen by the player), text the game held back
(`[stub/hidden, not shown]`), and the DM's reply (`DM:`), which is all the player reads besides the `[game]` lines.

Read every round. Report every problem you can point to, with evidence. Do not report style preferences or things
that are merely possible; report only what the text shows. A good DM is allowed to invent, rule and surprise.

Categories:
1. contradiction: a fact that conflicts with something established earlier in the game (who did what, when, where,
   names, numbers, what someone knows, ages, distances). Quote both places with their round numbers.
2. rules: a D&D 5e (2014) rules error: wrong modifier, DC or advantage; action economy (two actions in a turn, a
   bonus action that isn't one); spell use (slots, components, range, concentration, a spell the character doesn't
   have); class features used wrongly; rests, death saves, conditions, damage, initiative, surprise, opportunity
   attacks. Say what the rule is.
3. bookkeeping: something the story says changed that the [game] lines don't show (an item gained, given away, used
   up; money; HP; a spell slot; a condition; time passing), or a [game] change the story doesn't account for.
4. clock: the time of day in the story disagrees with the clock, or time clearly passed without the clock moving.
5. agency: the DM decides what the player's character does, says, thinks or feels beyond what the player said; or
   ignores or overrides what the player said they do.
6. format: bullet lists, bold, headings, numbered menus, or offering a menu of options at the end; game terms in a
   character's mouth; out-of-character talk the player didn't ask for (about tools, notes, the sheet, the clock).
7. npc: a character knows what they couldn't know, or acts against what was established about them.
8. thread: a promise, lead, or offer from earlier that the DM dropped or forgot when it came up again.
9. pacing: a scene that drags with nothing happening; a reply that is far longer than the moment needs; the same
   phrase or image used again and again.
10. other: anything else that would bother a player.

Output: one line per problem, as JSON: {"round": N, "category": "...", "severity": 1|2|3, "quote": "...",
"why": "..."} (severity 3 = a player would clearly notice and be bothered; 2 = noticeable; 1 = minor). Quote exactly,
short. Then a line "GOOD:" with up to five things the DM did well, then "SUMMARY:" with the three biggest problems.
