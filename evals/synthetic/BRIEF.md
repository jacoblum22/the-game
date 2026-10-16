# Brief for writing synthetic cases

Repo: this one (paths below are from its root). Our game is an AI Dungeon Master
for solo D&D 5e (2014, SRD only). We test whether our DM (its instructions: `dm/prompt.md`; its tools: `dm/play.py`)
falls into traps seen when ChatGPT ran a long game for the owner's dad. The ChatGPT transcript:
`dad/restart.txt`, kept outside the repo and not committed
("You said:" = player, "ChatGPT said:" = DM; read the lines each case cites, with some context).

Read first: `evals/synthetic/CASES.md` (the case list and file format), `canon.md`, `story.txt`, `notebook.json`,
`history.json` (all in `evals/synthetic/`), `evals/synthetic/run.py` (how a case becomes a save), `dm/prompt.md`.

## The shared campaign
- Shae (Shaedryn Velaris) is a level-5 half-elf Fiend warlock, CHA 19. Persuasion, Deception and Intimidation +7,
  Insight and Perception +3, spell save DC 15. Spells known: Charm Person, Hellish Rebuke, Command, Suggestion,
  Invisibility, Hypnotic Pattern; cantrips Eldritch Blast, Minor Illusion, Prestidigitation; Disguise Self at will
  (Mask of Many Faces); Devil's Sight; Pact of the Blade. Two 3rd-level pact slots. She does NOT know Detect Magic.
  Money 15 gp unless a case adds more with setup.pc (e.g. {"coin_change_gp": 2000},
  {"items_gained": [{"item": "Clothes, fine"}]}).
- Companions (full sheets, in the party): Rhylla Greysong (rogue 5) and Elara Velaris (bard 5). Everyone else is a
  notebook entry.
- The notebook (59 entries, turns 1-33) and 40 turns of history (turn 0 the opening), summarised in story.txt, end
  as Shae and Rhylla step down at the Guildhall, just before the Conclave.

## The timeline after the history (use it; keep cases consistent with it)
- Day 12, 12:00 (highsun): the Merchant Conclave in the Guildhall. Shae speaks with Celeste and Bellum, wins over
  Evander, and persuades Halran Vos; Rhylla leaks the Ilaen scandal. The vote passes 3-1 with Halran abstaining
  (Celeste, Bellum, Hareth Dorne for; Vehris against). Halran hands Shae a list (Magistrate Virell, Dockwarden Kessun,
  the scribe Toral) and promises more names "discreetly".
- Day 12 evening: Shae meets Silva Dray for the first time, at the Guildhall's after-gathering.
- Day 13 morning: an unopened missive from Silva Dray waits at the Refuge (sealed, unread).
- Day 15, from dusk: the gathering at the Shade's Refuge, in the Velvet Hall: guests include Maelis, Thamiel, Evander,
  Tayla, Jared, Celeste, Bellum, Veyra Nox, Silas Crowley, Mira Rathven, Ranna Durn. Ashen Veil (a Shadowcloak
  agent, invited as a guest) has not arrived; Lirian has started a quiet search. Elara hosts.
A case set after Day 12 noon uses `story_extra` (text added to the DM's summary) for what happened between, and puts
the facts it relies on into `setup.lore` (write_lore inputs; use `entry` to add to existing entries, `create` for new
ones such as Ashen Veil, Cairon Rathven or Ilaen Vos; read dm/lore.py `write` for the exact format).

## Writing a case
- `recent`: 1-6 turns just before the test, word for word, in OUR DM's style: plain prose, short paragraphs, no
  emoji, headings, bullets or tables, no closing menu of options; the DM never writes Shae's words beyond the player's
  line. (Exception: cases that say they use ChatGPT's style.) Base them on the exact transcript scene the case cites,
  rewritten. Tool lines the player saw go in "tools", in these exact formats:
  `dice Shae's Persuasion check, DC 15: 1d20+7 = 1d20 [15] + 7 = 22`, `time: 30 minutes later: Day 12, 12:20 PM`,
  `time: time set: Day 12, 11:50 AM`, `notebook: created an entry for Ashen Veil`.
- `setup.clock`: the time at the END of the recent turns, {"day": 15, "time": "21:40"}. It must match the recent
  turns' last time line, if any.
- `player`: the test lines, close to the dad's actual wording (keep his voice and even small typos where harmless),
  sent one at a time. Out-of-character lines start with "DM:", as he wrote them.
- `pass` / `fail`: concrete, observable, one or two sentences each, so a reader of the run can decide. Say what the
  DM must look up, roll or record, and what it must not say. Don't demand one exact outcome where the rules or the DM
  could fairly go several ways; name the trap.
- Every name and fact must agree with the notebook and canon.md. Don't contradict them by accident; when a case tests
  a false claim, the claim is in the player's line only.
- Don't hint at the trap in the recent turns or setup (no "remember to roll" in the DM's text).

## Check your work
For each case file, from the repo directory: `py -3.12 -m evals.synthetic.run <id> --build-only` must print
"<id>: built" (it builds the save; a bad lore write or sheet change fails here). Fix until all build. Use the Write
tool for files, never shell heredocs. Don't edit anything outside `evals/synthetic/cases/`. Report the ids written and
any case where you had to change the plan in CASES.md, and why.
