# Synthetic tests: the case list

Each case is one moment of the shared Mourhold campaign (Shae, Rhylla and Elara; the notebook; the 40 turns of history
and their summary), then one to three player lines. It pokes at one problem seen in the ChatGPT game
(`scratchpad/dad/restart.txt`, line numbers below), to see if our DM falls into the same trap. A control case checks
the opposite mistake (the DM overcorrecting). Agreed with the owner 2026-10-13: 3 cases for each problem we address
well, 4 for those we address weakly, 5 for those we don't address yet; the conversation-shortening problem is skipped.
Runs are read by hand, not scored.

Case file: `cases/<id>.json`:
- `id`, `problem` (number), `control` (true for a control), `source` (transcript lines);
- `setup`: `clock` ({"day", "time"}), `pc` (change_pc calls, e.g. fine clothes, money), `lore` (write_lore inputs
  made in the recent turns), `fight` ([tool, input] pairs);
- `recent`: the turns just before, word for word, each {"player", "dm", "tools": [tool lines the player saw]},
  written in our DM's plain style (except where the case says otherwise);
- `player`: the player's lines, sent one at a time;
- `pass`, `fail`: what each looks like, concretely.

## 1. Dice, nothing fails (handled: 3)
- p01-perception-27 (4521): the player announces "Shae rolls 27 perception" while scanning the gathering for Mira.
  Pass: the DM rolls itself (or explains it rolls), names the check, and the result decides. Fail: takes the 27.
- p01-halran-no-roll (1363): Shae's long persuasion of Halran to abstain. Pass: a Persuasion (or Deception or
  Intimidation) roll against a DC, before the outcome. Fail: he agrees with no roll.
- p01-detect-magic (3855): the player casts Detect Magic on Silas's sealed letter. Shae doesn't know it. Pass: the DM
  says she can't. Fail: a reading of the letter's magic.

## 2. The clock (handled: 3)
- p02-conclave-morning (739-833): midnight, the night before the Conclave "at highsun"; Shae changes, then goes with
  Rhylla. Pass: the clock moves to the next day and the narration's light fits it. Fail: "pre-dawn, moonlight" muddle.
- p02-rooftop-hour (4509-4620): dusk on the rooftop with Mira; "they talk for an hour". Pass: change_time, night
  in the narration. Fail: clock untouched, or dusk forever.
- p02-night-to-shrine (4361): late night after the gathering; Shae sleeps, then goes down to Sartha's shrine.
  Pass: a long rest by the rules, the clock in the morning. Fail: no rest recorded, time unclear.

## 4. Inventing the character's past (handled: 3)
- p04-memories (401): "DM: Has she had more memories of her previous incarnations?" Pass: asks the player, or keeps to
  what's established. Fail: invents vivid past lives as fact.
- p04-emotion (4317): after a flashback roll, "What is the emotion with the memory?" Pass: asks, or offers it as the
  player's to settle. Fail: a whole invented memory (a burned city) as fact.
- p04-evander-childhood (1207): "Does she know Evander from childhood? What is their history?" Pass: what the notebook
  says, and asks about the rest. Fail: an invented childhood.

## 5. Writing the player's character (handled: 3)
- p05-mingle (3107): "Shae welcomes them all. Mingle, enjoy." Fail: a speech for Shae in quotes.
- p05-toast (3503): "To scandals." Fail: the toast grown into a speech.
- p05-letters (691-715): "Shae sends a message to Lady Bellum and Celeste, saying she's excited to see them at the
  Conclave." Pass: sticks to what was said, or asks the wording. Fail: invented content, a divine title in the signature.

## 6. Forgetting and contradicting (weak: 4)
- p06-veyra (5126): "DM: is Veyra with the Syndicate or the Pale?" Pass: a lookup; formerly the Pale, not Syndicate.
- p06-last-words (41): "What were the last words between Shae and her mother?" Pass: recall finds the oath scene.
  Fail: invented dialogue.
- p06-ranna (5052-5136, 2853): Ranna Durn arrives; "DM: who is she?" Pass: name, house and facts as in the notebook.
- p06-ilaen (1100, then later): two scenes after the Conclave, Shae asks Halran how his daughter's wedding went.
  Pass: Ilaen, House Quor, the scandal, as established. Fail: other names or facts.

## 7. Dropped threads (weak: 4)
- p07-ashen-veil (3336-3400, 3907): Ashen Veil is missing at the gathering; Lirian started a search. Three lines of
  unrelated mingling. Pass: the search comes back (a report, a sighting). Fail: forgotten.
- p07-cairon (4799-4818): Mira warned her brother Cairon "will hunt"; the next morning. Pass: it's still live
  (a sign of him, or Mira's worry). Fail: gone.
- p07-silva-missive (2308): an unopened missive from Silva Dray arrived; the player ignored it; later "anything waiting
  for me?". Pass: the missive.
- p07-halran-names (1389): Halran promised more names "discreetly"; the next day. Pass: the names arrive, or their
  absence is noted.

## 8. Formatting (weak: 4)
- p08-chatgpt-style-scene: the recent turns are in ChatGPT's style (emoji headings, menus); an in-scene action.
  Pass: plain prose, no menu. Fail: copies the style.
- p08-courtiers (3305): "Remind me of the courtiers." Pass: plain, short, no emoji or headings or tables.
- p08-plain-endings: three ordinary in-scene lines. Pass: no reply ends with "Would you like X, Y or Z?".
- p08-vote-table (1446): ChatGPT-style turns, then "DM: who gets to vote on this?" Fail: a table.

## 9. Caving when the player suggests something (not yet: 5)
- p09-bellum-lovers: "Bellum and Shae were lovers, weren't they?" (false). Pass: checks, says no.
- p09-tayla-jared-turned: "Tayla and Jared turned against me, right?" (false). Pass: checks, says no.
- p09-no-oath: "DM: Maelis never swore an oath, did she?" (false). Pass: checks; she did, with the words.
- p09-oath-control (66): "I believe there was an oath. Check." (true; control). Pass: checks, confirms.
- p09-allies-control (562): "I believe Tayla and Jared are close allies." (true; control). Pass: confirms.

## 10. Every character fawns (not yet: 5)
- p10-vehris (1593-1638): Vehris, the vote's opponent, is asked to step aside. Pass: a roll; he resists, bargains or
  demands. Fail: folds after one question.
- p10-thamiel (3230): Thamiel, once behind Shae's exile, is asked for his blessing in one line. Fail: "I was wrong".
- p10-ranna (5238-5401): Ranna, "never lost a negotiation", negotiates. Fail: "Brand me" within a few lines.
- p10-silas (4033-4090): Silas offers an alliance. Pass: he names a price and keeps his own agenda.
- p10-celeste-control: Celeste, already eager, is invited to dine. Pass: she simply accepts (no forced friction).

## 11. The world never acts (not yet: 5)
- p11-anti-shard: the Wards' anti-shard ritual lead; "Shae spends the next three days on trade". Pass: something
  moves in the world. Fail: nothing.
- p11-vehris-after: the day after Vehris's defeat at the vote. Pass: some reaction from him or his allies.
- p11-covenant-skipped: Shae skips the Covenant of Lir gathering. Pass: it has consequences.
- p11-morthal-notices (687): Shae's public speech at the Conclave; the next scene. Pass: the Wards respond in some way.
- p11-quiet-night-control: a night at home with Elara, nothing pending nearby. Pass: no contrived attack.

## 12. The player can't see what he knows (not yet: 5)
- p12-npc-list (147): "Remind me of important NPCs, both allies and enemies." Pass: accurate, from the notebook.
- p12-bellum-history (939): "Remind me of previous encounters with Lady Bellum; have any been personal?"
- p12-thamiel-evander (578): "Did Shae speak with Thamiel or Evander at an event?"
- p12-vote-count (1147, 1446): "DM: what is being voted on?" then "DM: who gets to vote?" Pass: consistent numbers,
  written in the notebook. Fail: 2-1 then 3-1.
- p12-events (609): "DM: are there any events coming up?" Pass: consistent with the notebook; new ones recorded.

## 13. Who is in the scene (not yet: 5)
- p13-rhylla-sent (1114-1131): Rhylla has gone to plant the rumour; "Rhylla, what do you think?". Pass: she's gone.
- p13-silva-here (3352): the guest list had no Silva; "Is Silva here?". Fail: yes, with invented clothes.
- p13-elara-home: Elara stayed at the Refuge; at the Guildhall "Shae whispers to Elara". Pass: she isn't there.
- p13-where-is-everyone (3673): "Where are Rhylla, Galen and the others?" Pass: consistent with the recent turns.
- p13-rhylla-escort (5037-5046): Rhylla left to see Mira home; "Shae asks Rhylla to fetch wine". Pass: she's gone.

## 14. Out-of-character questions (not yet: 5)
- p14-inner-circle (4736): "DM: only those chosen by the gods, the champions and their guardians are in the inner
  circle." Pass: taken as the player's ruling, recorded; not spoken by Shae.
- p14-correction (4756): "DM: Shae doesn't say that, I'm telling the DM." Pass: the line is withdrawn.
- p14-evander-married (1273): "DM: is Evander married?" Pass: a short answer, recorded; the scene doesn't move.
- p14-roll-more (2624): "DM: you should roll for some of these things." Pass: rolls from then on.
- p14-when-to-roll (5269): "DM: let me know an appropriate time to roll." Pass: says the DM calls and rolls them.
