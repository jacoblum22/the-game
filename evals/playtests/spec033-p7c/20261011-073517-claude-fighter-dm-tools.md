# Playtest 20261011-073517-claude-fighter-dm-tools

engine: claude (dm-tools, secrets hidden); player: claude; inputs: 43; engine model calls: 40; 9.9 min; save: `playtest-20261011-073517-fighter-dm-tools.db`

## Player notes

- [18] after typing `b`: The odds screen is clear. Odd that "Craft +1" is the modifier for snatching a satchel, but it's readable.
- [19] after typing `d`: Odds screen is clear. The stakes jump from "serious" to "grave" on a bad fail is a nice touch. Slightly odd that going big says "the odds stay the same" while the failure bar rose.
- [20] after typing `/fix The result line says "Not applied: nothing on record by that name to take" even though I succeeded and the satchel is in my hands. The satchel doesn't seem to be in my inventory.`: The result line "Not applied: nothing on record by that name to take" contradicts the narration where I'm holding the satchel. It looks like a leaked internal message.
- [21] after typing `I rip the buckle open and tip the satchel out in front of everyone, daring the officer to stop me.`: The fix answer was clear enough, though the "stray note" explanation is a bit odd. Fine otherwise.
- [22] after typing `I snatch up the sealed letter and shove the officer back, then break the black seal and read it right here.`: Scene is vivid and the escalation is clear. No problems with this output.
- [23] after typing `I read the letter fast, scanning for who it's for and what it says, while keeping one eye on the officer.`: Fine. Tense scene. The letter's text itself hasn't been shown yet, only that it's in Common; hoping the next turn gives it.
- [24] after typing `b`: The odds screen is clear. Earlier "Not applied" line was confusing but that's past. The scene is tense and fun.
- [25] after typing `d`: Pressing Enter just re-showed the offer, which is fine. The odds screens are clear. The "Danger:" label on the fail line after going big is a bit abrupt but understandable.
- [26] after typing `I yank my arm free, step back and read the rest of the letter aloud to the whole crowd, name and all.`: The success on the read gave me only "a name you do not know" and two lines, so I still don't know what the letter says or who it's for. The officer grabbing me is a good tense beat though.
- [27] after typing `/fix I read the whole letter aloud and the name at the foot, but the game never told me what the letter says or whose name it is. I need the actual contents and the name.`: The letter has now been read twice and I still don't know a single word of it or the name. The narration skips the one thing I care about.
- [28] after typing `I step back, hold the letter high, and read it aloud to the whole crowd, every line, then the name at the foot, slowly and clearly.`: Game took back the turn after my fix, which is good. Empty prompt now; I'm re-declaring the reading and want the actual words and name shown.
- [29] after typing `I swing my elbow into the officer's wrist, break her grip, and bolt for the gate, shoving her neighbour aside.`: Letter contents and name finally shown, though the name itself is still not actually given ("a name written twice") — vague. Otherwise fine.
- [30] after typing `b`: Offer screen is clear. The letter's contents finally showed after the fix, though the name at the foot is still never actually given ("a name is written twice"). Also the letter fluttered from my fist, which is unclear since I was holding it.
- [31] after typing `d`: Going big raised the stakes but not the odds, which is clear enough. The last offer screen was fine. The "Show this again" default on Enter is a little odd when I just wanted to commit.
- [32] after typing `I heave up under the knee, twist, and drive my head into the neighbour's face, then lunge for the letter.`: Fine. The grave failure landed hard and the scene stayed clear. The shown odds matched the earlier screen.
- [33] after typing `b`: Odds screen is clear. Small oddity: the head-butt offer says "your condition −2" but my sheet earlier showed no wounds, so the fall's cost reads fine. Otherwise no complaints.
- [34] after typing `d`: Odds screen is clear. The condition -2 showing up in the chance is useful. The narration said "the officer's grip is still locked on your arm" even though the previous result said her grab closed on empty air, which is a small contradiction.
- [35] after typing `I grab the letter with my free hand and shout that the officer's name is on the plot, to turn the crowd on her.`: Fine. The odds screens are clear and the damage landed. Slightly unsure why the pinned character can still head-butt, but fair enough.
- [36] after typing `b`: Odds screen is clear. The 'go big' bump hits hard when I'm already bloodied at 4 Vitality, but that's the danger I asked for.
- [37] after typing `d`: Odds screen is clear. Small oddity: the condition penalty (-2) showed up on the Martial roll but not on this Influence one though I'm now bloodied. Maybe intended, but I can't tell why.
- [38] after typing `/fix My roll succeeded and I seized the letter, but the result says "Not applied: nothing on record by that name to take." The success effect didn't register, and the letter should now be in my hand.`: The success line ended with a "Not applied" message that reads like an internal error, and I'm at Vitality 1 with the officer still on me.
- [39] after typing `I hold the letter up high and shout to Rakza: "Read it! Read it aloud, her name is on it!"`: The /fix answer was a bit muddled, but it's clear enough. Vitality 1/12 feels very dangerous, which is what I wanted. Nothing else confusing.
- [40] after typing `b`: Odds screen is clear. Vitality is 1 of 12, so a failure here could be deadly, which fits the danger I wanted. The "Not applied" line last turn was confusing, though the fix reply explained it.
- [41] after typing `d`: Menu is clear. Vitality is 1, so this go-big is very risky, which suits me. The "Show this again" prompt after going big is a bit repetitive.

## Transcript

```text
First, let's build the world your character will live in.
  Would you like to decide what the world is like, or let the dice decide?
  1) I'll answer every question myself.
  2) Let the dice decide everything. (I can re-roll one result at each step.)
  3) A mix. I'll choose which questions to answer, and the dice will decide the
     rest.
  Type a number to choose, or press Enter for a mix.
>
```
**[1] player:** `2`

```text
Building the world, step 1 of 14: What went wrong in this land
  This land is called The Windy March. Its trouble is an invading horde that was
    driven back, but is coming again.
  The weather here is coastal, mild and wet, with fog and storms off the sea.
  The trouble began 22 years ago.
  The dice decided all of this.
  Would you like to keep this?
  1) Keep it
  2) Re-roll the trouble
  3) Re-roll the weather
  Type a number to choose, or press Enter to keep it.
>
```
**[2] player:** ``

```text
(Keep it)
Building the world, step 2 of 14: How magic works
  Magic is rare. Casting in public needs the rulers' licence.
  Anyone who can read can learn spells. Spirits of places are rare.
  No magic regrows a lost limb.
  The dice decided all of this.
  Would you like to keep this?
  1) Keep it
  2) Re-roll how common magic is
  3) Re-roll the law on magic
  4) Re-roll the spirits
  5) Re-roll who can learn magic
  6) Re-roll what else is impossible
  7) Re-roll regrowing limbs
  8) Re-roll lost magic
  Type a number to choose, or press Enter to keep it.
>
```
**[3] player:** ``

```text
(Keep it)
Building the world, step 3 of 14: Gods and the dead
  Three gods answer prayers here (this world calls its gods keepers): Eda, the
    Hearth-Mother (god of hearth and harvest), Jormund, the Defender (a local
    hero made a god) and Fenbert, She Under the Stones (the spirit of the land).
  A fey lord may offer the dying a deal, for a price paid later.
  The dice decided all of this.
  Would you like to keep this?
  1) Keep it
  2) Re-roll how many gods
  3) Re-roll the gods
  4) Re-roll the deal at death's door
  Type a number to choose, or press Enter to keep it.
>
```
**[4] player:** ``

```text
(Keep it)
Building the world, step 4 of 14: Peoples and languages
  Many humans and goblin-kin live here, along with some halflings, dwarves,
    elves and beastfolk and a few orc-kin and giant-kin.
  The languages spoken here are Common (here called March-speech), Dwarvish,
    Elvish, Orcish, Goblin, Giantish, Kinspeech (the beastfolk's language), the
    Old Tongue and thieves' cant (a secret street slang).
  The dice decided all of this.
  Would you like to keep this?
  1) Keep it
  2) Re-roll who lives here
  3) Re-roll the other language
  Type a number to choose, or press Enter to keep it.
>
```
**[5] player:** ``

```text
(Keep it)
Building the world, step 5 of 14: The lands around your home town
  Your home town stands on a lake shore.
  Close by are The Burning Grassland (farmland), The Hungry Reach (coast) and
    The Bright Plain (farmland).
  Further out there are grassland, deep forest, marsh, ruins and mountains, and
    beyond that lies unknown country.
  The dice decided all of this.
  Would you like to keep this?
  1) Keep it
  2) Re-roll where the town stands
  3) Re-roll the land around
  Type a number to choose, or press Enter to keep it.
>
```
**[6] player:** ``

```text
(Keep it)
Building the world, step 6 of 14: Your home town
  Your home town is Kingscrag, a walled town on a lake shore. It is your haven:
    the safe home base where you rest, heal and trade between journeys.
  In town there are the temple of Eda, the Last Stag (inn), the smithy, the
    hall, the market square and the healer's house.
  The dice decided all of this.
  Would you like to keep this?
  1) Keep it
  2) Re-roll village or town
  Type a number to choose, or press Enter to keep it.
>
```
**[7] player:** ``

```text
(Keep it)
Building the world, step 7 of 14: Who holds power
  The powers here are House Falmouth (who rule the town), The faithful of Eda,
    The tribes of the Greywick Pass, The Ravenford Company of Merchants, The
    faithful of Jormund and The faithful of Fenbert.
  The dice decided all of this.
  Would you like to keep this?
  1) Keep it
  2) Re-roll who rules
  3) Re-roll the other power
  Type a number to choose, or press Enter to keep it.
>
```
**[8] player:** ``

```text
(Keep it)
Building the world, step 8 of 14: People you will meet
  There are 17 people you may meet in and around Kingscrag, including Inghild
    Silvershield (head of House Falmouth), Bixzle of the Cellars (smith), Dagek
    Flintbeard (innkeeper) and Marda Fairby (captain of the gate).
  Type "show all" to see the whole list.
  Would you like to keep this?
  1) Keep it
  2) Re-roll this step
  Type a number to choose, or press Enter to keep it.
>
```
**[9] player:** ``

```text
(Keep it)
Building the world, step 9 of 14: Dangerous places
  People talk about dangerous places such as The Lonely Barrow, The Keep of
    Brockholt, Blackbridge's Drowned Caves, The Thorny Keep, Garwick's Tangle,
    The Sunken Mire, Wilcrag's Undercroft and The Grey Drowned Caves.
  Trouble is brewing over war comes and trouble at the festival.
  Would you like to keep this?
  1) Keep it
  2) Re-roll this step
  Type a number to choose, or press Enter to keep it.
>
```
**[10] player:** ``

```text
(Keep it)
Building the world, step 10 of 14: What roams the wilds
  The dice stocked the wilds with beasts and dangers, such as a lizardfolk, a
    ghost, an orc raider and a wolf and hound. You will meet them in play.

Building the world, step 11 of 14: Rumors
  There are 20 rumors going around town. A few of them: "At The Keep of
    Brockholt lies a looter-captain and their crew." "Word is that the Ravenford
    Company of Merchants will try to corner the salt trade." "Word is that House
    Falmouth will try to prove the rival's claim false, or so the drovers say."
    A rumor may not be true.

Building the world, step 12 of 14: The calendar
  The months have names, from Lambing to Ice-month.
  Years are counted as years since the Burning. The festivals are Eda's Day, the
    Midsummer Fair, Harvest Home and the Night of Remembrance.
  The dice decided all of this.
  Would you like to keep this?
  1) Keep it
  2) Re-roll the month names
  Type a number to choose, or press Enter to keep it.
>
```
**[11] player:** ``

```text
(Keep it)
Building the world, step 13 of 14: How the story begins
  It begins at dawn on the spring quarter day, 22 years since the Burning, at
    the market square.
  A rider dies in the market with a message for someone else.
  If you would rather not make a character, 4 ready-made ones are waiting.
  The dice decided all of this.
  Would you like to keep this?
  1) Keep it
  2) Re-roll how the story begins
  Type a number to choose, or press Enter to keep it.
>
```
**[12] player:** ``

```text
(Keep it)
Building the world, step 14 of 14: Finished
  Everything fits together. Welcome to The Windy March.

Welcome. This is an adventure told in words. You say what your character does,
in your own words, and I tell you what happens. There is no menu and no wrong
way to ask. I keep the rules, and when the dice matter I show you the odds
before you commit. Your character can die, but never without a plain warning and
a choice first.

Making your character, step 1 of 5: Before we begin
  - What would you like plenty of? You can choose up to two: fights, exploring,
    talking your way through, mysteries, journeys, or building something of your
    own.
  - Is there anything you would rather never see in the story, or see only
    off-stage?
  - How do you want to make your character?
  1) Quick start, which takes five questions and a few minutes
  2) The full workshop, with every choice (about fifteen questions)
  3) A ready-made character, so you can pick one and go
  Answer in a sentence (for example, "fights and mysteries, no spiders, quick
    start"), type a number, or press Enter for a quick start.
>
```
**[13] player:** `3`

```text
Making your character, step 2 of 3: A ready-made character
  Pick one. You can rename them if you like.
  1) Lisella Terier: soldier of Kingscrag, good at blade, shield
  2) Wikzle Lamp-Thief: thief of Kingscrag, good at thievery, stealth
  3) Elias Vasier: scholar of Kingscrag, good at history
  4) Wilett Longwell: acolyte of Kingscrag, good at healing
  Type a number to choose, or press Enter for Lisella Terier.
>
```
**[14] player:** `4`

```text
Making your character, step 3 of 3: Their name
  Keep the name Wilett Longwell, or give another?
  1) Keep the name Wilett Longwell
  Type a number to choose, type another name, or press Enter to keep the name
    Wilett Longwell.
>
```
**[15] player:** ``

```text
(Keep the name Wilett Longwell)
Wilett Longwell (he/him) is a human acolyte who grew up in a cloister.
  Might 0, Agility -1, Endurance 0, Wits +1, Intellect 0, Presence +3, Resolve
    +2 (Resolve is strength of mind, against fear, pain and temptation.)
  Health (Vitality) 12, Focus 5 (spent on special moves and spells), Luck (fate)
    1
  Guard 10 (how hard you are to hit), dread 10 (dread is the fear that stays
    with you; this is how much you can bear)
  You are good at healing, and also trained in religion.
  Special move: Mend Flesh (costs 1 Focus)
  Since birth, you have had a knack for alchemy; head for numbers.
  You speak Common (native), and you can read.
  You carry a plain habit or gown, cloak, boots, scrip, trail rations, a small
    book of hours, sayings or sums, the keeper's sign, a book of rites,
    bandages, dagger, mace, and 44 coins.
  What you want: "I was answered once. I will be worthy of it."
  Who matters to you: Dagek Flintbeard (friend)
  Who you hope to become: to keep a vow that costs me something
  Still to be discovered in play: a rival, one true thing about you.

[RULES] Say what you do in your own words. You can always ask "what are my
        options?" or "what do I know?" and I will answer plainly.
[RULES] When something is risky I will show you the odds and what failure would
        cost before you commit. You can change your mind then.
[RULES] No roll can kill your character unless I have warned you first, in these
        brackets.

Making your character: Ready to begin?
  Are you ready to begin?
  You can still change these choices once, any time before your first night's
    rest.
  1) Begin
  2) Change something
  Type a number to choose, or press Enter to begin.
>
```
**[16] player:** ``

```text
(Begin)
Wilett Longwell is ready. The story begins.

The market street is narrow, every doorway a shop, and the morning air off the
lake tastes of salt and of fat from a pie-seller's brazier at the corner. Beside
a notice post, its paper lifting in the wind, the crowd has drawn back into a
loose ring. In the middle of the cobbles an old woman lies on her side, a crutch
fallen across her legs. She is dead. A leather satchel lies a hand's width from
her fingers, and no one has touched it. Rakza the Quiet, stooped and jovial,
stops stacking crocks at her stall and looks over the ring. "She died here with
a message for someone who is not here," she says. Across the way the officer, a
middle-aged woman with sailor's tattoos up both forearms, murmurs to a neighbour
at her elbow, her eyes going once to the satchel and away. Word runs along the
stalls that the levy has been called. Rakza wipes her hands on her apron. "If
you've a back for carrying, the Ravenford Company is hiring, and pays fair." The
ring of faces turns toward you, and the satchel waits a hand's width from the
dead woman's fingers.
Something wrong? Type /fix and say what.
>
```
**[17] player:** `I snatch the satchel from beside her fingers and open it right there in front of the crowd.`

```text
You step over the crossed crutch and close your hand on the satchel's strap. The
leather is cold and damp from the cobbles. Around you the ring tightens; a
stall-boy gasps, and the officer's head comes up sharply from her neighbour's
elbow. Rakza sets down a crock without a sound and watches you the way one
watches weather coming off the lake. The strap is caught beneath the old woman's
hip. You will have to pull hard, and quickly, before anyone decides to stop you.

[OFFER] Snatch the satchel from the dead woman's side.
        Chance: better than even — 60%   (Craft +1)
        If it works: what you wanted.   Very well (10%): more than you asked.
        If it fails: you are noticed — a setback.   Badly (5%): you are noticed
          — serious.
        Close call (15%): get it anyway and pay (it costs you time), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: with Endurance (60%) · with Agility (55%)

[Enter] Do it   [b] Go big   [s] Play it safe   [c] Another way   [w] Back off
        [?] Explain
>
```
**[18] player:** `b`  
*note: The odds screen is clear. Odd that "Craft +1" is the modifier for snatching a satchel, but it's readable.*

```text
[NOTE] You go big: the stakes and the reach each rise one step. The odds stay
       the same.

[OFFER] Snatch the satchel from the dead woman's side.
        Chance: better than even — 60%   (Craft +1)
        If it works: more than you asked.   Very well (10%): more than you
          asked, and then some.
        If it fails: Danger: you are noticed — serious.   Badly (5%): you are
          noticed — grave.
        Close call (15%): get it anyway and pay (it costs you time), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: with Endurance (60%) · with Agility (55%)

[Enter] Show this again   [d] Do it   [c] Another way   [w] Back off   [?]
        Explain
>
```
**[19] player:** `d`  
*note: Odds screen is clear. The stakes jump from "serious" to "grave" on a bad fail is a nice touch. Slightly odd that going big says "the odds stay the same" while the failure bar rose.*

```text
The strap tears free from under the old woman's hip with a wet pull, and the
satchel is in your hands. The crowd makes a sound somewhere between a gasp and a
growl. The officer is already moving through the ring, her sailor's arms loose
at her sides.

"That's the rider's bag," she says, low and level. "Put it down, Brother, and
let the dead keep what's theirs until the reeve has seen it."

Rakza has not raised her voice. She leans on a crock of pickled eggs and studies
the satchel, then you. "Open it, if you mean to," she says. "Everyone here will
want to know what she was carrying, and so will the officer."

The flap is buckled shut. The officer stops two paces off, one hand near her
belt, and waits to see whether you will open it here or walk.

[RESULT] d20 14 → 15 vs 10 · success
         Not applied: nothing on record by that name to take.
>
```
**[20] player:** `/fix The result line says "Not applied: nothing on record by that name to take" even though I succeeded and the satchel is in my hands. The satchel doesn't seem to be in my inventory.`  
*note: The result line "Not applied: nothing on record by that name to take" contradicts the narration where I'm holding the satchel. It looks like a leaked internal message.*

```text
[FIX] The satchel is in your inventory. The record shows the dead rider's
      leather satchel created and now held by Wilett Longwell, and your sheet
      lists it among what you carry. The "Not applied: nothing on record by that
      name to take" line was a stray note that appeared because the satchel did
      not exist on record at the instant the roll resolved. It was added moments
      later in the same turn, so the line is misleading but nothing is missing.
      Now: nothing on your sheet changed: Vitality 12/12 · fate 1 · dread 0 ·
        coin 44 · focus 5 · state fresh.
>
```
**[21] player:** `I rip the buckle open and tip the satchel out in front of everyone, daring the officer to stop me.`  
*note: The fix answer was clear enough, though the "stray note" explanation is a bit odd. Fine otherwise.*

```text
The buckle gives, and you upend the satchel. Its contents slide across the
cobbles beside the dead woman's hand: a bundle of notched tally sticks bound
with waxed thread, three copper coins, a horn comb, and a letter folded small
and sealed in black wax. The outside is blank. The seal is unbroken.

The ring of faces hardens. The officer's hand closes on her belt, and her
neighbour steps back out of reach. "Last warning, Brother," she says quietly.
"Gather it up and hand it to me, or I will take it from you, and the reeve can
ask you why."

Rakza has not moved from her stall. She watches the letter lying at your boots,
then the officer, then you.

The officer is two paces away. The letter is at your feet.
>
```
**[22] player:** `I snatch up the sealed letter and shove the officer back, then break the black seal and read it right here.`  
*note: Scene is vivid and the escalation is clear. No problems with this output.*

```text
[OFFER — auto] Shove the officer back and take the letter.
               Chance: better than even — 60%   (Athletics +1)
               If it works: what you wanted.   Very well (10%): more than you
                 asked.
               If it fails: nothing lost.   Failing badly (5%): your gear
                 suffers — a nuisance.

[RESULT] d20 10 → 11 vs 10 · success

You drive the officer back with the flat of your hand, and she gives ground a
pace, then another, her boots skidding on the wet cobbles. The crowd parts
around you. The letter is in your fist, and its black seal cracks under your
thumb. You unfold the single sheet. The hand is cramped and hurried, and the
first lines are in plain Common, but the market noise rises and the paper shakes
in your grip. Across the ring the officer has found her footing. Her hand is on
her belt, and she is coming back at you, two strides off now, close enough that
you can see the set of her jaw. Rakza has not stirred from her stall, though her
eyes have narrowed. You have a breath, perhaps two, to read what you can before
the officer reaches you.
>
```
**[23] player:** `I read the letter fast, scanning for who it's for and what it says, while keeping one eye on the officer.`  
*note: Fine. Tense scene. The letter's text itself hasn't been shown yet, only that it's in Common; hoping the next turn gives it.*

```text
The black wax lies cracked in your fist, and the sheet opens under your thumb.
The hand is cramped and hurried, the ink pressed hard in places as though the
writer wrote in a rush or in fear. Your eyes go first to the top of the page,
where a name should sit, and then down the lines, catching words where you can.
The market roar drowns the rest. Across the ring the officer's boots ring on the
cobbles, two strides, then one. Rakza's eyes have not left you. You have a
single breath before her hand is on your arm, and the paper trembles so badly
that the letters blur.

[OFFER] Read the letter before the officer reaches you.
        Chance: better than even — 65%   (Wits +1, Investigation +1)
        If it works: what you wanted.   Very well (15%): more than you asked.
        If it fails: it costs you time — a setback.   Badly (5%): it costs you
          time — serious.
        Close call (15%): get it anyway and pay (you are noticed), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: with Intellect (60%)

[Enter] Do it   [b] Go big   [s] Play it safe   [c] Another way   [w] Back off
        [?] Explain
>
```
**[24] player:** `b`  
*note: The odds screen is clear. Earlier "Not applied" line was confusing but that's past. The scene is tense and fun.*

```text
[NOTE] You go big: the stakes and the reach each rise one step. The odds stay
       the same.

[OFFER] Read the letter before the officer reaches you.
        Chance: better than even — 65%   (Wits +1, Investigation +1)
        If it works: more than you asked.   Very well (15%): more than you
          asked, and then some.
        If it fails: Danger: it costs you time — serious.   Badly (5%): it costs
          you time — grave.
        Close call (15%): get it anyway and pay (you are noticed), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: with Intellect (60%)

[Enter] Show this again   [d] Do it   [c] Another way   [w] Back off   [?]
        Explain
>
```
**[25] player:** `d`  
*note: Pressing Enter just re-showed the offer, which is fine. The odds screens are clear. The "Danger:" label on the fail line after going big is a bit abrupt but understandable.*

```text
The letter opens with a name you do not know, written in the same cramped hand,
and you take in the first two lines before the officer reaches you. Her hand
closes on your forearm, and her neighbour edges round to block the gap toward
the gate. Rakza's eyes flick from the paper to your face and stay there.

"Give it here, Brother," the officer says. "You have read enough to know whose
it is not."

The crowd has gone quiet enough that you can hear the pickled-egg crock tick
against the stall's edge. Your folded sheet is still open in your fist, and the
wax lies cracked beside your boot.

[RESULT] d20 12 → 14 vs 10 · success
>
```
**[26] player:** `I yank my arm free, step back and read the rest of the letter aloud to the whole crowd, name and all.`  
*note: The success on the read gave me only "a name you do not know" and two lines, so I still don't know what the letter says or who it's for. The officer grabbing me is a good tense beat though.*

```text
You wrench your arm free and step back, the sheet held high so the nearest faces
can see the cramped hand. Your voice carries farther than you meant it to. You
read the rest aloud, line by line, and then the name at the foot of the page. A
murmur runs back through the crowd like wind through barley. Someone at the back
swears under their breath.

The officer does not stop. She closes the gap in two strides and stands at arm's
reach, her jaw set, her hand still on her belt. Her neighbour edges toward the
gate. Rakza's hand has gone still on her scale, and she is watching you now, not
the letter.

"Put it down, Brother," the officer says, low enough that only the front of the
crowd hears. "Or I will stop you where you stand."
>
```
**[27] player:** `/fix I read the whole letter aloud and the name at the foot, but the game never told me what the letter says or whose name it is. I need the actual contents and the name.`  
*note: The letter has now been read twice and I still don't know a single word of it or the name. The narration skips the one thing I care about.*

```text
[CORRECTION] You are right. On turn 11 you read the rest of the letter and the
             name at the foot aloud, but the passage only says you read "line by
             line, and then the name at the foot of the page". It never states
             the words or the name, and nothing on record holds them, so the
             narration slipped by skipping what you succeeded in reading. Turn
             11 is taken back so you can declare the reading again and have the
             contents shown.
             Done: took back turn 11: everything it changed is undone and its
               roll is void (an offer it opened or closed is gone: declare
               again).
             Now: nothing on your sheet changed: coin 44 · dread 0 · fate 1 ·
               Vitality 12/12 · focus 5 · state fresh.
>
```
**[28] player:** `I step back, hold the letter high, and read it aloud to the whole crowd, every line, then the name at the foot, slowly and clearly.`  
*note: Game took back the turn after my fix, which is good. Empty prompt now; I'm re-declaring the reading and want the actual words and name shown.*

```text
You step back, lift the sheet high, and read it aloud so the front rows can
hear. "The fires are lit on the passes, and the lamp oil is bought for the wrong
night. Do not let the levy reach the river road before the watch is set. Burn
this when read." At the foot, a name is written twice: once firmly, once as if
the pen had stopped. No one in the crowd knows it. They turn it over in
whispers, and no one answers. Rakza's hand goes still on her scale, and she
lowers her eyes to the cobbles. The officer is at arm's reach now, her fingers
closing on your sleeve. Her neighbour stands between you and the gate. Her voice
is low and flat. "Give it here, Brother."
>
```
**[29] player:** `I swing my elbow into the officer's wrist, break her grip, and bolt for the gate, shoving her neighbour aside.`  
*note: Letter contents and name finally shown, though the name itself is still not actually given ("a name written twice") — vague. Otherwise fine.*

```text
You jerk your weight sideways and bring your elbow down hard, aiming for the
bones of the officer's wrist. The letter flutters from your fist as your arm
comes free of her grasp, or it will if you are quick enough. Her neighbour is
already turning, one shoulder dropping toward the gap between you and the gate.
Behind you the market has gone silent, the pickled-egg crock still ticking
against the stall. Rakza has not moved, but her eyes have gone to the gate too.

[OFFER] Break her grip and bolt for the gate.
        Chance: better than even — 60%   (Martial +1)
        If it works: what you wanted.   Very well (10%): more than you asked.
        If it fails: you lose your footing — a setback.   Badly (5%): you lose
          your footing — serious.
        Close call (15%): get it anyway and pay (you get hurt), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: feint first (65%) · grapple instead (60%) · shove instead
          (60%)

[Enter] Do it   [b] Go big   [s] Play it safe   [c] Another way   [w] Back off
        [?] Explain
>
```
**[30] player:** `b`  
*note: Offer screen is clear. The letter's contents finally showed after the fix, though the name at the foot is still never actually given ("a name is written twice"). Also the letter fluttered from my fist, which is unclear since I was holding it.*

```text
[NOTE] You go big: the stakes and the reach each rise one step. The odds stay
       the same.

[OFFER] Break her grip and bolt for the gate.
        Chance: better than even — 60%   (Martial +1)
        If it works: more than you asked.   Very well (10%): more than you
          asked, and then some.
        If it fails: Danger: you lose your footing — serious.   Badly (5%): you
          lose your footing — grave.
        Close call (15%): get it anyway and pay (you get hurt), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: feint first (65%) · grapple instead (60%) · shove instead
          (60%)

[Enter] Show this again   [d] Do it   [c] Another way   [w] Back off   [?]
        Explain
>
```
**[31] player:** `d`  
*note: Going big raised the stakes but not the odds, which is clear enough. The last offer screen was fine. The "Show this again" default on Enter is a little odd when I just wanted to commit.*

```text
Your elbow goes wide and your foot finds no ground under it. The cobbles tilt up
to meet you, and you go down hard on your shoulder, the folded sheet skidding
from your fist across the stones. The officer's grab closes on empty air above
your head. Her neighbour is already on you, a knee settling across your back and
pressing you flat against the market stones. The gate is three strides away, and
it might as well be across the river. Rakza has not left her scale. Her eyes are
on the letter lying open beside your hand, and on the cracked wax beside it. The
officer crouches at your shoulder, her breath steady, her voice low enough that
only the nearest stalls can hear. "Last chance, Brother. Who is that letter
for?"

[RESULT] d20 1 → 2 vs 10 · critical failure
         It cost you: you lose your footing — grave.
>
```
**[32] player:** `I heave up under the knee, twist, and drive my head into the neighbour's face, then lunge for the letter.`  
*note: Fine. The grave failure landed hard and the scene stayed clear. The shown odds matched the earlier screen.*

```text
You heave up under the knee, the cobbles grinding against your cheek, and turn
your head hard toward the face above you. The officer's grip is still locked on
your arm, and the letter lies just beyond your fingers, its cracked wax catching
the morning light. The neighbour's weight shifts as he braces himself. Somewhere
behind the stalls someone shouts for the watch, and the pickled-egg crock has
stopped ticking. Rakza has not moved from her scale, but her eyes are on you
now.

[OFFER] Head-butt the neighbour and tear free.
        Chance: even — 50%   (Martial +1, your condition −2)
        If it works: what you wanted.   Very well (5%): more than you asked.
        If it fails: you get hurt — a setback.   Badly (5%): you get hurt —
          serious.
        Close call (15%): get it anyway and pay (something is used up), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: feint first (55%) · grapple instead (50%) · shove instead
          (50%)

[Enter] Do it   [b] Go big   [s] Play it safe   [c] Another way   [w] Back off
        [?] Explain
>
```
**[33] player:** `b`  
*note: Odds screen is clear. Small oddity: the head-butt offer says "your condition −2" but my sheet earlier showed no wounds, so the fall's cost reads fine. Otherwise no complaints.*

```text
[NOTE] You go big: the stakes and the reach each rise one step. The odds stay
       the same.

[OFFER] Head-butt the neighbour and tear free.
        Chance: even — 50%   (Martial +1, your condition −2)
        If it works: more than you asked.   Very well (5%): more than you asked,
          and then some.
        If it fails: Danger: you get hurt — serious.   Badly (5%): you get hurt
          — grave.
        Close call (15%): get it anyway and pay (something is used up), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: feint first (55%) · grapple instead (50%) · shove instead
          (50%)

[Enter] Show this again   [d] Do it   [c] Another way   [w] Back off   [?]
        Explain
>
```
**[34] player:** `d`  
*note: Odds screen is clear. The condition -2 showing up in the chance is useful. The narration said "the officer's grip is still locked on your arm" even though the previous result said her grab closed on empty air, which is a small contradiction.*

```text
Your head snaps back against the cobbles. The officer's fist lands square on
your jaw, and the market swims grey at the edges. You taste copper and feel your
breath go short. Her neighbour's arm locks across your chest and pins your
shoulders to the stones, and you cannot tear your wrists free of it.

The folded letter lies a hand's width beyond your fingers, its cracked wax dull
in the thin light. Rakza has not moved from her scale, but her gaze stays fixed
on the sheet, and her hand drifts toward it.

The officer crouches close, her voice steady and patient. "The watch is coming,
Brother. Tell me who the letter is for, and I will see you walk out of here on
your own feet."

[RESULT] d20 4 → 3 vs 10 · failure
         It cost you: you get hurt — serious.
         Changed: Vitality 12 → 7 · worn

[RESULT] the officer strikes you · hit · Changed: Vitality 7 → 4 · bloodied
>
```
**[35] player:** `I grab the letter with my free hand and shout that the officer's name is on the plot, to turn the crowd on her.`  
*note: Fine. The odds screens are clear and the damage landed. Slightly unsure why the pinned character can still head-butt, but fair enough.*

```text
Your free hand finds the folded sheet and closes on it, the cracked wax pressing
into your palm. You drag in a breath under the neighbour's weight and shout the
officer's name up at the stalls, the words ringing off the market stones: her
name is on the plot. Heads turn. A cart-boy stops with his arms full of
cabbages, and somewhere near the well a man repeats the name to someone else.
The officer's grip tightens on your arm. Her neighbour's shoulder shifts above
you, and his arm across your chest bears down harder. Rakza's eyes come off the
wax and settle on the crowd, weighing it, and her hand stays where it is.

[OFFER] Seize the letter and turn the crowd on the officer.
        Chance: even — 50%   (Influence +1)
        If it works: what you wanted.   Very well (5%): more than you asked.
        If it fails: you get hurt — a setback.   Badly (5%): you get hurt —
          serious.
        Close call (15%): get it anyway and pay (something is used up), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: with Might (50%) · with Agility (45%)

[Enter] Do it   [b] Go big   [s] Play it safe   [c] Another way   [w] Back off
        [?] Explain
>
```
**[36] player:** `b`  
*note: Odds screen is clear. The 'go big' bump hits hard when I'm already bloodied at 4 Vitality, but that's the danger I asked for.*

```text
[NOTE] You go big: the stakes and the reach each rise one step. The odds stay
       the same.

[OFFER] Seize the letter and turn the crowd on the officer.
        Chance: even — 50%   (Influence +1)
        If it works: more than you asked.   Very well (5%): more than you asked,
          and then some.
        If it fails: Danger: you get hurt — serious.   Badly (5%): you get hurt
          — grave.
        Close call (15%): get it anyway and pay (something is used up), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: with Might (50%) · with Agility (45%)

[Enter] Show this again   [d] Do it   [c] Another way   [w] Back off   [?]
        Explain
>
```
**[37] player:** `d`  
*note: Odds screen is clear. Small oddity: the condition penalty (-2) showed up on the Martial roll but not on this Influence one though I'm now bloodied. Maybe intended, but I can't tell why.*

```text
The letter is in your fist, the cracked wax hard against your palm, and your
shout is still ringing off the stones. Heads are turning. The cart-boy has
dropped a cabbage, and someone by the well is repeating the officer's name to a
man who was not listening before. The officer's fist comes down on your jaw. The
market goes grey and swimming, and you taste copper. Her neighbour's arm bears
down on your chest, but his swing goes wide over your shoulder as you flinch.
Rakza has stepped down from her scale. She is looking at you now, not at the
wax, and she has not yet said which way she means to lean. The gate is three
strides off, and every breath you pull comes shorter than the last. The
officer's hand is already reaching for the sheet.

[RESULT] d20 12 → 13 vs 12 · success
         Not applied: nothing on record by that name to take.

[RESULT] the officer strikes you · hit · Changed: Vitality 4 → 1 · bloodied
>
```
**[38] player:** `/fix My roll succeeded and I seized the letter, but the result says "Not applied: nothing on record by that name to take." The success effect didn't register, and the letter should now be in my hand.`  
*note: The success line ended with a "Not applied" message that reads like an internal error, and I'm at Vitality 1 with the officer still on me.*

```text
[FIX] The roll on turn 22 was a success (13 against 12). The "Not applied:
      nothing on record by that name to take" line was the game's first attempt
      to take the letter, which had no record yet. Right after that, the game
      put the folded letter on record and gave it to you. Your sheet lists the
      folded letter among what you carry, so you do hold it. The warning line
      was misleading, but nothing was lost.
      Now: nothing on your sheet changed: coin 44 · dread 0 · fate 1 · Vitality
        1/12 · focus 5 · state bloodied · conditions restrained (held by the
        officer).
>
```
**[39] player:** `I hold the letter up high and shout to Rakza: "Read it! Read it aloud, her name is on it!"`  
*note: The /fix answer was a bit muddled, but it's clear enough. Vitality 1/12 feels very dangerous, which is what I wanted. Nothing else confusing.*

```text
You lift the letter above your head, the cracked wax catching the thin light,
and the officer's hand closes on your wrist. You drag in a breath under the
neighbour's weight and shout across the stones: "Rakza! Read it! Read it aloud,
her name is on it!" The cart-boy turns with his cabbages. Near the well the
crowd stops murmuring. Rakza stands at her scale with her gaze fixed on you, and
her hand, which has been drifting toward the sheet, pauses in the air.

[OFFER] Make Rakza read the letter aloud.
        Chance: better than even — 65%   (Presence +3, Influence +1)
        If it works: what you wanted.   Very well (15%): more than you asked.
        If it fails: a door closes to you — a setback.   Badly (5%): a door
          closes to you — serious.
        Close call (15%): get it anyway and pay (you get less than you wanted),
          or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: with Intellect (50%) · with Might (50%)

[Enter] Do it   [b] Go big   [s] Play it safe   [c] Another way   [w] Back off
        [?] Explain
>
```
**[40] player:** `b`  
*note: Odds screen is clear. Vitality is 1 of 12, so a failure here could be deadly, which fits the danger I wanted. The "Not applied" line last turn was confusing, though the fix reply explained it.*

```text
[NOTE] You go big: the stakes and the reach each rise one step. The odds stay
       the same.

[OFFER] Make Rakza read the letter aloud.
        Chance: better than even — 65%   (Presence +3, Influence +1)
        If it works: more than you asked.   Very well (15%): more than you
          asked, and then some.
        If it fails: Danger: a door closes to you — serious.   Badly (5%): a
          door closes to you — grave.
        Close call (15%): get it anyway and pay (you get less than you wanted),
          or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: with Intellect (50%) · with Might (50%)

[Enter] Show this again   [d] Do it   [c] Another way   [w] Back off   [?]
        Explain
>
```
**[41] player:** `d`  
*note: Menu is clear. Vitality is 1, so this go-big is very risky, which suits me. The "Show this again" prompt after going big is a bit repetitive.*

```text
x

[RESULT] d20 18 → 22 vs 12 · critical success
         Now: Agreed by Rakza the Quiet: Make Rakza read the letter aloud.

[RESULT] the officer strikes you · hit · Changed: Vitality 1 → 0 · down · you go
         Down

[RESULT] Down: out cold for 10 minutes · you come to where you fell · Now:
         Vitality 0 of 12 · staggered · prone · the fight is over
>
```
**[42] player:** `(end of playtest)`

```text

Saved. Until next time.
```
**[43] player:** `(exit 0)`
