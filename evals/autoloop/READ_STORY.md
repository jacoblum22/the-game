# How to read a whole story (for the fourth reader)

The three block readers (READ.md) each read one game's latest 60 rounds, so they can't see a fact from an earlier
block contradicted in this one, or a thread opened at round 10 and dropped at round 150. You read one game from its
opening to its latest round, for the story as a whole. Same file format as READ.md describes (`PLAYER:`, `[game]`,
hidden `[DM ...]` calls, `DM:` replies); the player sees only the `DM:` replies and the `[game]` lines.

You get two files:
- the story, `<game>-1-<last>.txt`: read all of it, in order, keeping your own notes of facts as they are established
  (who is where, who knows what, names, ages, counts, distances, travel times, what happened when, what each character
  wants and is like);
- the candidates, `<game>-1-<last>.facts.txt`: for each person, place or thing named in more than one round, the
  sentences about it with a number, a distance, a time or a relation in them. A script gathered these and judges
  nothing; most are consistent. Use them to check, never as findings by themselves: every finding must be confirmed
  in the story file itself.

Report only these, each with evidence from both places:
1. contradiction: a fact that conflicts with one established earlier, however far back.
2. lore: the world's own rules broken (a god, a custom, a magic, a history or a geography stated one way and later
   used another way), or a reveal that doesn't fit what came before it.
3. plot hole: an event that couldn't have happened as told given what was established (someone in two places, a
   message arriving before it was sent, an enemy knowing what they couldn't), or a cause that's never explained when
   the story said it would be.
4. character: someone acting or speaking against what was established about them (their wants, loyalties, manner,
   what they know) without a reason the story gives.
5. thread: a promise, debt, lead or person the story set up and then forgot when it came up again, or dropped for
   good without a word.

Do not report style, pacing, format or rules mechanics (the block readers do those), or things that are merely
possible. A good DM may invent, surprise and change things on purpose: a lie by a character, a twist that the story
marks as a twist, or a change the story explains is not a finding.

Output: one line per problem, as JSON: {"round": N, "earlier": [rounds], "category": "...", "severity": 1|2|3,
"quote": "...", "earlier_quote": "...", "why": "..."} (severity 3 = a player would clearly notice and be bothered;
2 = noticeable; 1 = minor). Quote exactly, short. Then "SUMMARY:" with the three biggest problems for the story as a
whole.
