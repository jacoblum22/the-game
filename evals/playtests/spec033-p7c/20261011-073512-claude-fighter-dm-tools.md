# Playtest 20261011-073512-claude-fighter-dm-tools

engine: claude (dm-tools, secrets hidden); player: claude; inputs: 43; engine model calls: 25; 7.4 min; save: `playtest-20261011-073512-fighter-dm-tools.db`

## Player notes

- [18] after typing `b`: The odds screen is clear, but "Unarmed +1" on a cloistered scholar is a bit odd, and "Close call (15%)" is unclear on whether it's inside the 55%.
- [19] after typing `d`: Odds screen is clear. Going big just raised the failure stakes while the odds stayed at 55%, which is fine. "Unarmed +1" is a bit odd for a scholar, but not a problem.
- [20] after typing `I keep her where she is and tighten my grip. "Talk. Now. Everything, or I don't let go."`: The result line says 13 vs 10 success, but the odds screen said 55%, which is odd for a 10 target. Also the "Go big" promised "more than you asked," but I only got a stalemate. Otherwise vivid.
- [21] after typing `I keep my grip and shove her toward the gate wall. "Say what came home without the road-warden, or the captain can watch me break your arm."`: Scene is tense and vivid. Minor: the woman's line about "what came home" is a bit cryptic, but fine. Nothing wrong.
- [22] after typing `d`: The odds screen is clear. One small oddity: this was a threat, but the odds went up from 55% to 65% just because the skill changed to Athletics. That is fine, though a bit surprising.
- [23] after typing `I let go of the woman and swing a punch at Nedmund's black eye. "Stand aside, captain, I'm going to the ditch and nobody stops me."`: Fine. The woman's reveal was clear and the odds screens are readable. The "good hand" detail on the captain is a bit odd, but I'm not sure it's wrong.
- [24] after typing `b`: Odds screen is clear. The refugee woman called me "scholar" with no setup, which is a little odd. Otherwise fine.
- [25] after typing `d`: Fine. Odds screens are clear. Note the empty Enter just re-showed the offer, which is okay.
- [26] after typing `I slide down into the ditch toward the pale shape in the reeds, before the captain can catch me.`: Fine. Result line says "your opponent is worn" though the text never showed Nedmund getting hurt; slightly unclear.
- [27] after typing `I push through the reeds and kneel by the pale shape, pulling the rushes aside to see what it is.`: Last output was fine. The scene is vivid, though the previous action was read as already sliding into the ditch without an odds screen.
- [28] after typing `I search the body fast, checking the pockets and the green cord, while she's still above me.`: Description was good. Nedmund's hit came without an odds screen, which felt a bit abrupt. Also "your opponent is worn" appeared when I succeeded, which was slightly unclear.
- [29] after typing `d`: Odds screen is clear. Search offer reads fine, though it's odd that the guard's shield-bash landed as a narrated hit with no roll shown before I could act.
- [30] after typing `d`: The game hit an error ("something went wrong on our side") right after I chose to search the body. Input was kept, so I'm retrying.
- [31] after typing `d`: Twice in a row "Sorry, something went wrong on our side" when I tried to do the search roll. Input kept, but the action is stuck. Retrying once more.
- [32] after typing `d`: Pressing "d" on the search offer failed three times in a row with "Sorry, something went wrong on our side". The game is stuck on that action and I can't tell if retrying will ever work.
- [33] after typing `b`: The "Do it" key failed four times in a row with "something went wrong on our side", so I couldn't search the body. Nothing I did changed it, and there's no hint what's broken. Trying Go big instead to see if the game gets past it.
- [34] after typing `d`: Earlier "something went wrong on our side" errors repeated four times on the same input before going big worked; annoying. Now the go-big screen is showing again, fine.
- [35] after typing `d`: The game has now thrown "something went wrong on our side" five times in a row on the same search action, even though my input is kept. It blocks me from playing at all, and nothing says whether it will ever clear.
- [36] after typing `d`: Repeated "Sorry, something went wrong on our side" errors six times when I tried to do the search roll, even after choosing go big. The game is stuck on the same offer and I can't act.
- [37] after typing `d`: Repeated "something went wrong on our side" errors seven times in a row on the search action; the input is kept but retrying doesn't work. Only the "go big" screen gave any reaction. Stuck on this action.
- [38] after typing `d`: Repeated "something went wrong on our side" errors on every attempt to confirm the search roll (8 tries); I'm stuck and can't act on the offer.
- [39] after typing `/fix Pressing [d] to search the road-warden's body fails every time with "Sorry, something went wrong on our side" (tried about nine times, with and without Go big). I can't resolve the search.`: The Do it choice on the search offer errored nine times in a row and I'm stuck. The odds screen itself was clear, but I can't act on it.
- [40] after typing `/fix The replayed scene contradicts what I already saw: the warden was face-up with his face to the sky and a green cord at his shoulder, now he's face-down with a badge on a cord, and I'm at the lip of the ditch instead of kneeling in the reeds beside him. Also Nedmund already hit me and I'm hurt, which isn't mentioned.`: The fix got the search working again, but the replayed scene doesn't match the earlier one: body position, the cord and where I am all changed, and my wound is gone from the narration.
- [41] after typing `I search the body fast, checking the pockets and the green cord, while she's still above me.`: The fix replay finally went through. But the last correction didn't actually show me the scene again or the search offer, so I'm unsure whether I'm back at the offer. Had to wade through a lot of bookkeeping text.

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
  This land is called The Silver Marches. Its trouble is a cruel tyrant who
    rules the land beyond your town.
  The weather here is mild, with green summers, wet autumns and snow in some
    winters.
  The trouble began 18 years ago.
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
  Magic is common. Casting in public needs the rulers' licence.
  Anyone who can read can learn spells. Spirits of places turn up now and then.
  No magic regrows a lost limb. Summoning is lost.
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
  Three gods answer prayers here (this world calls its gods keepers): Ranine,
    the Even Hand (god of justice), Aldbert, the Hearth-Mother (god of hearth
    and harvest) and Isda, the High One (god of the sky and oaths).
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
  Many humans and halflings live here, along with some dwarves and a few elves,
    goblin-kin, giant-kin and beastfolk.
  The languages spoken here are Common (here called Marches-speech), Dwarvish,
    Elvish, Goblin, Giantish, Kinspeech (the beastfolk's language), the Old
    Tongue and thieves' cant (a secret street slang).
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
  Your home town stands at a river ford.
  Close by are The Old Meads (farmland), The Burning Holt (woodland) and The
    Grey Downs (farmland).
  Further out there are hills, moor, deep forest and woodland, and beyond that
    lies unknown country.
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
  Your home town is Goldford, a walled town at a ford of a river. It is your
    haven: the safe home base where you rest, heal and trade between journeys.
  In town there are the temple of Ranine, the Crooked Lantern (inn), the smithy,
    the hall, the market square and the healer's house.
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
  The powers here are The council of Goldford (who rule the town), The faithful
    of Ranine, The March-Wardens, The hunters of Ferngate, The faithful of
    Aldbert and The faithful of Isda.
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
  There are 18 people you may meet in and around Goldford, including Valian
    Terence (head of the council of Goldford), Willy Thistlebarrel (smith), Octo
    Vasier (innkeeper) and Nedmund Stonebrook (captain of the gate).
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
  People talk about dangerous places such as The Caves of Larkcrag, Redmere's
    Warren, The Crooked Sluices, Crowwick's Undercroft, The Undercroft of
    Silverby, The Long Tangle, Hawkford's Temple and Coldham's Drowned Caves.
  Trouble is brewing over the road of knives and the road of knives.
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
  The dice stocked the wilds with beasts and dangers, such as a ghost, a
    brigand, a wolf and hound and a raptor and great bird. You will meet them in
    play.

Building the world, step 11 of 14: Rumors
  There are 20 rumors going around town. A few of them: "At Redmere's Warren
    lies the warchest." "At The Undercroft of Silverby lies the engine or altar
    the place was built around (resonance: arcane), and no one has ever come
    back from it." "Ranine has been seen in a dream by three people this month."
    A rumor may not be true.

Building the world, step 12 of 14: The calendar
  The months have names, from Greening to Wolf.
  Years are counted as years of the Iron Peace. The festivals are Ranine's Day,
    the Midsummer Fair, Harvest Home and the Night of Remembrance.
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
  It begins at dawn on the spring quarter day, 18 years of the Iron Peace, at
    the gate.
  Refugees arrive with a story that nobody believes.
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
  Everything fits together. Welcome to The Silver Marches.

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
  1) Dunbert Ironwell: soldier of Goldford, good at blade, shield
  2) Bela Greenbottle: thief of Goldford, good at thievery, stealth
  3) Tammund Stonewell: scholar of Goldford, good at history
  4) Elio Terande: acolyte of Goldford, good at oaths
  Type a number to choose, or press Enter for Dunbert Ironwell.
>
```
**[14] player:** `3`

```text
Making your character, step 3 of 3: Their name
  Keep the name Tammund Stonewell, or give another?
  1) Keep the name Tammund Stonewell
  Type a number to choose, type another name, or press Enter to keep the name
    Tammund Stonewell.
>
```
**[15] player:** ``

```text
(Keep the name Tammund Stonewell)
Tammund Stonewell (she/her) is a human scholar who grew up in a cloister.
  Might -1, Agility 0, Endurance 0, Wits +2, Intellect +3, Presence +1, Resolve
    0 (Resolve is strength of mind, against fear, pain and temptation.)
  Health (Vitality) 12, Focus 5 (spent on special moves and spells), Luck (fate)
    1
  Guard 11 (how hard you are to hit), dread 8 (dread is the fear that stays with
    you; this is how much you can bear)
  You are good at history, and also trained in languages, investigation and law.
  Since birth, you have had a knack for history; fear arrives late in you.
  You speak Common (native), Old tongue (accented), and you can read.
  You carry a plain habit or gown, cloak, boots, scrip, trail rations, a small
    book of hours, sayings or sums, a penknife, books and notes of your subject,
    writing case: pens, ink, wax, parchment, a small lamp, lamp oil, and 88
    coins.
  What you want: "A thing is not true because it is written; I will see for
    myself."
  Who matters to you: Willy Thistlebarrel (friend)
  Who you hope to become: to read a tongue no living person reads
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
Tammund Stonewell is ready. The story begins.

Morning light lies flat and cold on the road to the ford, and the gate of
Goldford stands shut. Heavy doors are barred, the bar as thick as a man, and a
chain sags across the road in iron brackets. Above the gate a watch platform
looks down on the waiting road. Pinned to the gatepost, a hire notice offers
good coin to able hands for a matter best discussed in private, and it names the
hunters of Ferngate as the ones asking.

Nedmund Stonebrook, the captain of the gate, stands at the chain. She is young,
a fresh black eye darkening one side of her face, and she keeps glancing back at
the people in the road.

Those people are the refugees, a huddle of bundles and tired faces. At their
front a woman with a shaved head and an old tattoo on her scalp is packing a
blanket with hard, quick hands. She watches the captain the way one watches a
dog that might bite.

"They came in at first light with a story nobody in Goldford believes. Nobody.
And there's a wagon in the ditch past the ford, looted to the boards. So tell me
what I'm to make of that."

The woman lifts her chin. "Then go and look at the ditch. I have no need of your
belief."

Nedmund's eyes come to you, waiting.
Something wrong? Type /fix and say what.
>
```
**[17] player:** `I grab the refugee woman by the arm and demand she tell me the truth of her story, right here, in front of the captain.`

```text
You close your hand on the woman's forearm before you have quite decided to, and
the blanket she was folding slips half out of her grasp. Under your fingers her
arm is thin, all cords and bone, but it does not soften. Her eyes drop to your
hand, then rise to your face, cold and measuring. Behind her the refugees go
still, a child's voice cut off mid-word. Nedmund's head snaps around, one hand
moving toward the chain. Every eye on the road is on you now. The woman says
nothing yet. She is waiting to see which of you will speak first, and how hard
you mean to hold her.

[OFFER] Hold the refugee leader and demand the truth.
        Chance: better than even — 55%   (Might −1, Unarmed +1)
        If it works: what you wanted.   Very well (5%): more than you asked.
        If it fails: you lose your footing — a setback.   Badly (5%): you lose
          your footing — serious.
        Close call (15%): get it anyway and pay (you get hurt), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: feint first (70%) · with Agility (60%) · shove instead
          (55%)

[Enter] Do it   [b] Go big   [s] Play it safe   [c] Another way   [w] Back off
        [?] Explain
>
```
**[18] player:** `b`  
*note: The odds screen is clear, but "Unarmed +1" on a cloistered scholar is a bit odd, and "Close call (15%)" is unclear on whether it's inside the 55%.*

```text
[NOTE] You go big: the stakes and the reach each rise one step. The odds stay
       the same.

[OFFER] Hold the refugee leader and demand the truth.
        Chance: better than even — 55%   (Might −1, Unarmed +1)
        If it works: more than you asked.   Very well (5%): more than you asked,
          and then some.
        If it fails: Danger: you lose your footing — serious.   Badly (5%): you
          lose your footing — grave.
        Close call (15%): get it anyway and pay (you get hurt), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: feint first (70%) · with Agility (60%) · shove instead
          (55%)

[Enter] Show this again   [d] Do it   [c] Another way   [w] Back off   [?]
        Explain
>
```
**[19] player:** `d`  
*note: Odds screen is clear. Going big just raised the failure stakes while the odds stayed at 55%, which is fine. "Unarmed +1" is a bit odd for a scholar, but not a problem.*

```text
Your grip holds, and the woman does not struggle. She turns her head only enough
to look at the fingers biting into her arm, then back at your face. Behind her a
man steps forward and stops when Nedmund lifts her free hand from the chain. The
captain's eyes move from you to the refugees and back again, and she says
nothing yet.

"You want the truth," the woman says, low and steady. "Then take your hand off
me. I will not speak the worst of it with your fist in my flesh and my people
watching you do it."

Somewhere behind her the child starts crying again, quietly. The blanket lies
crumpled at your feet. You can loosen your grip and let her talk, or keep her
where she is and see whether fear will do what your question could not.

[RESULT] d20 13 → 13 vs 10 · success
         Now: The refugees' leader, the traveler restrained by you.
>
```
**[20] player:** `I keep her where she is and tighten my grip. "Talk. Now. Everything, or I don't let go."`  
*note: The result line says 13 vs 10 success, but the odds screen said 55%, which is odd for a 10 target. Also the "Go big" promised "more than you asked," but I only got a stalemate. Otherwise vivid.*

```text
The woman does not struggle. She looks at your hand, then at the captain, and
her voice stays level. "You will have it from me, scholar, and it will cost you
more than my arm." Her gaze flicks past you to the ditch road. "Ask Nedmund what
came home this morning without the road-warden. Then ask her why she is still
holding that chain."

Nedmund has stepped forward, her good hand close to her spear. "Let her go. Now.
I will not tell you twice, and I will not have my gate turned into a brawl over
a story I have not heard."

The child behind the refugees has stopped crying. The whole road is waiting to
see whether you loosen your grip, or whether you mean to make the captain choose
between you and her people.
>
```
**[21] player:** `I keep my grip and shove her toward the gate wall. "Say what came home without the road-warden, or the captain can watch me break your arm."`  
*note: Scene is tense and vivid. Minor: the woman's line about "what came home" is a bit cryptic, but fine. Nothing wrong.*

```text
You drive her back a step, and her shoulder meets the cold stone of the gate
wall with a dull thud. Your hand stays locked on her arm, and the threat is out
in the open air: name it, or lose the arm. Nedmund's spear comes up a hand's
width, her face gone hard, and she says your name once, sharp, as a warning.
Along the road the refugees have drawn together. A man shifts a child onto his
hip and steps back, eyes never leaving you. The woman does not cry out. She
looks at you the way one looks at a stranger who has shown their true face, and
waits to see whether you mean it.

[OFFER] Make the refugee leader say what came home.
        Chance: better than even — 65%   (Might −1, Athletics +1)
        If it works: what you wanted.   Very well (15%): more than you asked.
        If it fails: Danger: you are noticed — serious.   Badly (5%): you are
          noticed — grave.
        Close call (15%): get it anyway and pay (you lose your footing), or
          fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: feint first (80%) · grapple instead (65%) · strike instead
          (65%)

[Enter] Show this again   [d] Do it   [s] Play it safe   [c] Another way   [w]
        Back off   [?] Explain
>
```
**[22] player:** `d`  
*note: The odds screen is clear. One small oddity: this was a threat, but the odds went up from 55% to 65% just because the skill changed to Athletics. That is fine, though a bit surprising.*

```text
The woman's jaw works once, as if she is swallowing something bitter. "The
road-warden's horse came through the ford at first light," she says, very low,
so that only you and the captain can hear her. "No rider. Its saddle was turned,
and it would not go near the wagon. We saw the wagon on the way in. Its boards
were already bare when we passed it." Her eyes stay on yours. "The men who
stripped it did not leave in any hurry. They knew where the road ran and where
the watch would not be looking." Behind her, the man who stepped forward has not
moved. Nedmund's spear dips a hand's width, though her grip does not ease. The
woman glances at your fingers on her arm. "That is all I will give you while you
hold me. The rest is in the ditch, if you have the stomach to look."

[RESULT] d20 12 → 12 vs 8 · success
         Now: Agreed by the refugees' leader, the traveler: Make the refugee
           leader say what came home.
>
```
**[23] player:** `I let go of the woman and swing a punch at Nedmund's black eye. "Stand aside, captain, I'm going to the ditch and nobody stops me."`  
*note: Fine. The woman's reveal was clear and the odds screens are readable. The "good hand" detail on the captain is a bit odd, but I'm not sure it's wrong.*

```text
You open your hand, and the woman's arm slides free of your grip. The blanket
stays crumpled at your feet. Before the captain can bring her spear around, you
drive your fist toward the bruise under Nedmund's eye, your whole weight behind
it. Her shield-arm is already rising to meet you, and the chain at her hip
rattles as she shifts her stance. Behind her the refugees scatter back from the
wall, and somewhere a child screams the captain's name. The road to the ditch is
a few strides past her shoulder, if you can get past her.

[OFFER] Punch Nedmund and break past her to the ditch.
        Chance: better than even — 55%   (Might −1, Martial +1)
        If it works: what you wanted.   Very well (5%): more than you asked.
        If it fails: you get hurt — a setback.   Badly (5%): you get hurt —
          serious.
        Close call (15%): get it anyway and pay (something is used up), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: feint first (70%) · with Agility (60%) · grapple instead
          (55%)

[Enter] Do it   [b] Go big   [s] Play it safe   [c] Another way   [w] Back off
        [?] Explain
>
```
**[24] player:** `b`  
*note: Odds screen is clear. The refugee woman called me "scholar" with no setup, which is a little odd. Otherwise fine.*

```text
[NOTE] You go big: the stakes and the reach each rise one step. The odds stay
       the same.

[OFFER] Punch Nedmund and break past her to the ditch.
        Chance: better than even — 55%   (Might −1, Martial +1)
        If it works: more than you asked.   Very well (5%): more than you asked,
          and then some.
        If it fails: Danger: you get hurt — serious.   Badly (5%): you get hurt
          — grave.
        Close call (15%): get it anyway and pay (something is used up), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: feint first (70%) · with Agility (60%) · grapple instead
          (55%)

[Enter] Show this again   [d] Do it   [c] Another way   [w] Back off   [?]
        Explain
>
```
**[25] player:** `d`  
*note: Fine. Odds screens are clear. Note the empty Enter just re-showed the offer, which is okay.*

```text
Nedmund gives ground as your shoulder drives past her shield. Her spear comes
around too late, and you are through the gap and onto the ditch road with the
gate wall at your back. The mud is soft and churned, and the stink of wet timber
and old smoke rises from the ditch below. The wagon lies on its side in the
reeds. Its boards have been stripped to the frame, and the axle hangs broken.
Something pale shows among the rushes, too still and too straight to be sacking.

Behind you Nedmund calls your name, and the chain at her hip rattles as she
steps after you. She does not run. The refugees have gone quiet at the wall, and
the woman is watching you with her hand pressed to the child's head.

You can go down into the ditch now, while the captain is still deciding whether
to follow, or turn and try to make her hear you first.

[RESULT] d20 17 → 17 vs 10 · success
         Changed: your opponent is worn
>
```
**[26] player:** `I slide down into the ditch toward the pale shape in the reeds, before the captain can catch me.`  
*note: Fine. Result line says "your opponent is worn" though the text never showed Nedmund getting hurt; slightly unclear.*

```text
You slide down the bank and the mud takes your boots to the ankle, throwing cold
water up your habit. Above, Nedmund has come to the lip of the ditch, close
enough that her outstretched hand could catch your collar. The chain at her hip
swings as she leans over, and her spear stays low but ready. The stink of wet
timber and old smoke closes around you. The wagon lies on its side a few strides
off, its bare frame open to the sky, and the broken axle drips into the reeds.
The pale shape is closer now, half-hidden among the rushes, and a corner of
cloth or skin shows where the reeds part. At the wall the refugees have gone
silent. The woman has her hand pressed to the child's head and her eyes still on
you. The shape lies just beyond the reeds, and the captain is one reach away.
>
```
**[27] player:** `I push through the reeds and kneel by the pale shape, pulling the rushes aside to see what it is.`  
*note: Last output was fine. The scene is vivid, though the previous action was read as already sliding into the ditch without an odds screen.*

```text
The rushes part, and the man beneath them is a road-warden. His grey cloak is
sodden, a green cord knotted at his shoulder, and his boots are still laced,
which seems wrong for a man left in a ditch. His face is turned to the sky, too
pale to read.

Above, Nedmund does not wait for your answer. Her shield-rim catches you across
the shoulder as she leans over the lip of the bank, and the blow lands hard. The
breath leaves you in a rush and the ditch tilts for a heartbeat. You are still
on your knees and still thinking, but you are no longer unhurt.

At the wall the woman has not moved, her hand still pressed to the child's head.
The captain's spear tip hovers over you, close enough to read. You can search
the body now, quickly, while she is still above you, or you can look up and tell
her what you have found.

[RESULT] Nedmund Stonebrook strikes you · hit · Changed: Vitality 12 → 9 · worn
>
```
**[28] player:** `I search the body fast, checking the pockets and the green cord, while she's still above me.`  
*note: Description was good. Nedmund's hit came without an odds screen, which felt a bit abrupt. Also "your opponent is worn" appeared when I succeeded, which was slightly unclear.*

```text
Your fingers go to the grey cloak first, sodden and heavy, then to the pockets
beneath it. You move fast, while the captain's shadow lies across the reeds. The
green cord at his shoulder is knotted tight, the kind a warden ties to show
whose road he keeps. Above, Nedmund shifts her weight on the lip of the bank,
and her spear tip dips toward you. At the wall the woman has not made a sound.
The mud is already soaking through your habit at the knees, and you have only a
few heartbeats before the captain decides whether to strike again.

[OFFER] Search the road-warden's body.
        Chance: even — 45%   (Wits +2, Investigation +1)
        If it works: what you wanted.   Very well (5%): more than you asked.
        If it fails: it costs you time — a setback.   Badly (10%): it costs you
          time — serious.
        Close call (15%): get it anyway and pay (you are noticed), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: with Intellect (50%)

[Enter] Do it   [b] Go big   [s] Play it safe   [c] Another way   [w] Back off
        [?] Explain
>
```
**[29] player:** `d`  
*note: Odds screen is clear. Search offer reads fine, though it's odd that the guard's shield-bash landed as a narrated hit with no roll shown before I could act.*

```text
Sorry, something went wrong on our side. Your input is kept; try again.
>
```
**[30] player:** `d`  
*note: The game hit an error ("something went wrong on our side") right after I chose to search the body. Input was kept, so I'm retrying.*

```text
Sorry, something went wrong on our side. Your input is kept; try again.
>
```
**[31] player:** `d`  
*note: Twice in a row "Sorry, something went wrong on our side" when I tried to do the search roll. Input kept, but the action is stuck. Retrying once more.*

```text
Sorry, something went wrong on our side. Your input is kept; try again.
>
```
**[32] player:** `d`  
*note: Pressing "d" on the search offer failed three times in a row with "Sorry, something went wrong on our side". The game is stuck on that action and I can't tell if retrying will ever work.*

```text
Sorry, something went wrong on our side. Your input is kept; try again.
>
```
**[33] player:** `b`  
*note: The "Do it" key failed four times in a row with "something went wrong on our side", so I couldn't search the body. Nothing I did changed it, and there's no hint what's broken. Trying Go big instead to see if the game gets past it.*

```text
[NOTE] You go big: the stakes and the reach each rise one step. The odds stay
       the same.

[OFFER] Search the road-warden's body.
        Chance: even — 45%   (Wits +2, Investigation +1)
        If it works: more than you asked.   Very well (5%): more than you asked,
          and then some.
        If it fails: Danger: it costs you time — serious.   Badly (10%): it
          costs you time — grave.
        Close call (15%): get it anyway and pay (you are noticed), or fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: with Intellect (50%)

[Enter] Show this again   [d] Do it   [c] Another way   [w] Back off   [?]
        Explain
>
```
**[34] player:** `d`  
*note: Earlier "something went wrong on our side" errors repeated four times on the same input before going big worked; annoying. Now the go-big screen is showing again, fine.*

```text
Sorry, something went wrong on our side. Your input is kept; try again.
>
```
**[35] player:** `d`  
*note: The game has now thrown "something went wrong on our side" five times in a row on the same search action, even though my input is kept. It blocks me from playing at all, and nothing says whether it will ever clear.*

```text
Sorry, something went wrong on our side. Your input is kept; try again.
>
```
**[36] player:** `d`  
*note: Repeated "Sorry, something went wrong on our side" errors six times when I tried to do the search roll, even after choosing go big. The game is stuck on the same offer and I can't act.*

```text
Sorry, something went wrong on our side. Your input is kept; try again.
>
```
**[37] player:** `d`  
*note: Repeated "something went wrong on our side" errors seven times in a row on the search action; the input is kept but retrying doesn't work. Only the "go big" screen gave any reaction. Stuck on this action.*

```text
Sorry, something went wrong on our side. Your input is kept; try again.
>
```
**[38] player:** `d`  
*note: Repeated "something went wrong on our side" errors on every attempt to confirm the search roll (8 tries); I'm stuck and can't act on the offer.*

```text
Sorry, something went wrong on our side. Your input is kept; try again.
>
```
**[39] player:** `/fix Pressing [d] to search the road-warden's body fails every time with "Sorry, something went wrong on our side" (tried about nine times, with and without Go big). I can't resolve the search.`  
*note: The Do it choice on the search offer errored nine times in a row and I'm stuck. The odds screen itself was clear, but I can't act on it.*

```text
You go wide-eyed and keep your footing at the lip of the ditch. The road-warden
lies face-down in the cold, brown water, one arm flung out over the bank. His
cloak is soaked dark, and the warden's badge still hangs on its cord at his
neck. Nothing about him has been hidden or moved, and the reeds around him are
trampled only where he fell.

Behind you, Captain Nedmund has not lowered her spear. Her shield is set and her
eyes are on your hands, not on the body. "Step back from him, scholar," she
says. "Or tell me why you're down there."

You can kneel at the water's edge to look more closely, or answer her first.

[CORRECTION] The search offer is open and its numbers check out (Wits +2,
             Investigation +1, 45%, after your Go big at turn 18). But each
             commit (turns 19 to 23) wrote nothing and no model call was
             recorded, so the offer is stuck and never reaches a roll. Nothing
             has been spent. The stuck offer will be withdrawn and framed again
             fresh so you can resolve the search.
             Done: the offer for "Search the road-warden's body" is withdrawn
               (nothing was spent) and the turn played again (below).
             Now: nothing on your sheet changed: coin 88 · dread 0 · fate 1 ·
               Vitality 9/12 · focus 5 · state worn.
>
```
**[40] player:** `/fix The replayed scene contradicts what I already saw: the warden was face-up with his face to the sky and a green cord at his shoulder, now he's face-down with a badge on a cord, and I'm at the lip of the ditch instead of kneeling in the reeds beside him. Also Nedmund already hit me and I'm hurt, which isn't mentioned.`  
*note: The fix got the search working again, but the replayed scene doesn't match the earlier one: body position, the cord and where I am all changed, and my wound is gone from the narration.*

```text
[CORRECTION] At turn 12 you pushed through the reeds and knelt by him, and the
             text said "His face is turned to the sky" with "a green cord
             knotted at his shoulder". The replay at turn 24 described him
             "face-down" with a badge on a cord and put you at the lip of the
             ditch. That was the narration slipping, since nothing on record
             moved him or you. The scene stands as at turn 12: he lies face-up
             with the green cord at his shoulder, and you kneel in the reeds
             beside him.
             Done: the road-warden's body in the ditch's posture is face-up on
               record; the road-warden's body in the ditch's cord is green,
               knotted at the shoulder on record; your position is kneeling in
               the reeds beside the warden on record.
             At turn 12 Nedmund's shield-rim struck you for 3, taking Vitality
               from 12 to 9, and that is still on your sheet (9/12). The
               replayed text at turn 24 left the blow out and described you as
               keeping your footing, which was wrong. The injury is real and
               stays; nothing needs changing in the numbers.
             Now: nothing on your sheet changed: coin 88 · dread 0 · fate 1 ·
               Vitality 9/12 · focus 5 · state worn.
>
```
**[41] player:** `I search the body fast, checking the pockets and the green cord, while she's still above me.`  
*note: The fix replay finally went through. But the last correction didn't actually show me the scene again or the search offer, so I'm unsure whether I'm back at the offer. Had to wade through a lot of bookkeeping text.*

```text
x

[OFFER] Search the warden's pockets and the green cord, fast.
        Chance: even — 45%   (Wits +2, Investigation +1)
        If it works: what you wanted.   Very well (5%): more than you asked.
        If it fails: you are noticed — a setback.   Badly (10%): you are noticed
          — serious.
        Close call (15%): get it anyway and pay (you lose your footing), or
          fail.
        Fate: 1 (you may spend one to reroll the die once you see it)
        Another way: with Intellect (50%)

[Enter] Do it   [b] Go big   [s] Play it safe   [c] Another way   [w] Back off
        [?] Explain
>
```
**[42] player:** `(end of playtest)`

```text

Saved. Until next time.
```
**[43] player:** `(exit 0)`
