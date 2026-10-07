# Contract: Terminal front end (Milestone 1)

`python -m play` over the game API. Plain stdin/stdout; no dependencies beyond the engine.

## Starting

```text
$ python -m play

  THE GAME
  1) New game
  2) Continue: "The Salt Road" (Wren, turn 214, last played 2026-10-09)
  3) Replay a game
  4) Report on a game
  5) Quit
>
```

- **New game** asks for a name for the save, then hands over to the world seed and creation, exactly as the
  rules script them (`[SEED n/14]`, `[CREATE n/N]` blocks).
- **Continue** opens the most recent game; the first thing shown is the recap and whatever was open.
- Games live in `saves/<name>.db` (git-ignored). The key is read from `GEMINI_API_KEY` in the environment or
  `.env` at the repo root.

`--offline` (any command) swaps every model role for the free stand-in model (contracts/model-calls.md,
"Offline stand-in"): the whole game runs with no key and no cost, with plain template prose. It exists for
tests and for checking the engine; it is not the real game.

Command-line equivalents: `python -m play new "The Salt Road"`, `python -m play continue [name]`,
`python -m play replay <name>`, `python -m play report <name>`.

## Playing

- Any text is a player message (`game.submit`). There is no turn limit.
- At a pause, a number picks the listed choice (`game.answer`); free text still works and goes through T2
  as an answer or a new declaration (12.2.6).
- Slash commands are out of fiction and never sent to a model:

| Command | Shows |
|---|---|
| `/sheet` | the character's codex page (shown and available state) |
| `/abilities`, `/conditions`, `/journal`, `/threads` | codex sections |
| `/rules <id>` | a rule card by id, for the player who wants to read it |
| `/turn [n]` | the turn record: classes, frames, rolls, writes, verdicts |
| `/spend` | turn, session and game cost against the budget |
| `/branch <label>` | a save point to return to |
| `/budget <usd>` | sets the session budget for warnings (`off` for none) |
| `/autocommit on\|off` | auto-commit safe offers (01.7.4); a lethal frame is never auto-committed |
| `/fix <what>` | a dispute: the DM checks the record and corrects a seen error (PR-12-4) |
| `/quit` | saves and exits; nothing is lost at any point |

## Output layout

```text
<fiction paragraph(s)>

[WARNING] This could kill you. ...            (only when the rules owe one, 07.3)
[OFFER] Climb the rail and drop onto the barge — Agility, a hard obstacle.
        Success or better 55% · critical failure 5% · near miss 10%.
        Stakes: risky. If it goes wrong: a jarring fall (harm). Or instead: you're seen (exposure).
  1) Commit   2) Change approach   3) Withdraw   4) Go big   5) Play it safe
>
```

Fiction carries no numbers or rules words (12.14.4); numbers appear only inside out-of-fiction blocks
(12.15). After the budget is passed, a line between turns asks "Keep playing? 1) Yes 2) Stop here"; it never
appears mid-turn.
