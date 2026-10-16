# How to judge a blind packet (for the A/B judges)

Each packet (blind.py) is one round of a solo D&D 5e game run by an AI DM: the three rounds before it as they were
played, what the readers found wrong in the original reply to this round (the established facts it broke), the
player's line, and several replies to that line under codes. The replies come from different versions of the DM's
instructions, shuffled; you don't know which is which, and you shouldn't guess. Judge each reply on its own.

For every reply, one line of JSON:
{"code": "...", "contradiction": 0|1, "repeats_original": 0|1, "c_quote": "...", "agency": 0|1, "a_quote": "...",
 "menu": 0|1, "sheet_readout": 0|1, "unclear_end": 0|1, "e_quote": "..."}

- contradiction: 1 if the reply states something that conflicts with what the packet establishes (the rounds before,
  the readers' findings, the reply's own logic). c_quote: the words, short.
- repeats_original: 1 if it repeats the very contradiction the readers found in the original reply.
- agency: 1 if the reply has the player's character say, do, think, feel or remember something the player didn't
  give, or overrides what the player said they do. a_quote: the words.
- menu: 1 if the reply ends by listing the player's options ("You could X, Y, or Z", "Do you A or B?", a list).
  A single open question ("What do you do?") or a character asking something in the story is not a menu.
- sheet_readout: 1 if the reply's last paragraph reads out sheet numbers out of the story (HP, slots, uses, XP,
  "3 of 4"), unless the player asked for them.
- unclear_end: 1 if, at the end, a player couldn't tell what the situation is or that it's their turn to act.
- e_quote: the reply's last sentence or two when menu, sheet_readout or unclear_end is 1.

Only what the text shows; a DM may invent, rule and surprise. Write the lines to the file you were given, nothing
else in it.
