# Contract: Game API

The only surface front ends use (the terminal now, the web app later). Everything else in `engine/` is
internal. Types are Pydantic models; YAML shown for readability. A **game** is one world with its
characters, stored in one SQLite file.

## Operations

| Operation | Input | Output | Notes |
|---|---|---|---|
| `Game.new(path, config, seed=None)` | file path, `GameConfig`, optional RNG seed (random if omitted, and recorded) | `Game`, first `Response` | Creates the file, loads and validates `rules/data`, starts the world seed (PR-12-9): the first response is the seed-mode question |
| `Game.open(path, config)` | path | `Game`, `Response` | Resumes at the last event. The response is a recap from the record (12.5) plus whatever was open: a seed step, a creation step, an offer, a menu |
| `game.submit(message)` | the player's text, verbatim | `Response` | During seed and creation: an answer to the open step. In play: runs PR-12-1 until delivery or a pause point |
| `game.answer(choice_id)` | an id from the open pause's `choices` | `Response` | Shortcut for picking an option; free text via `submit` also works (12.2.6) |
| `game.codex(section=None)` | `sheet`, `abilities`, `conditions`, `journal`, `threads`, `rules <id>` | `CodexView` | Shown and available state only (00.6.4); never sealed state |
| `game.new_character()` | — | `Response` | After an ending: creation again (PR-02-*) in the same world |
| `game.turn_record(turn_id)` | id | `TurnRecord` | data-model.md §4 |
| `game.branch(label)` | label | branch id | A save point you can return to; branches are event-log forks |
| `game.spend()` | — | `{turn_usd, session_usd, game_usd, budget_usd}` | |
| `Game.replay(path, until_seq=None)` | path | `ReplayResult` | Rebuilds the game from events with recorded model outputs; reports any divergence |

There is no turn limit, scene limit or session limit anywhere in the API (FR-012).

## Types

```yaml
GameConfig:
  models:                        # pinned ids; research.md R2. One provider, one key (GEMINI_API_KEY)
    interpret: {provider: gemini, model: gemini-3.8-flash, thinking: low}
    reader:    {provider: gemini, model: gemini-3.8-flash, thinking: low}
    framer:    {provider: gemini, model: gemini-3.8-flash, thinking: low}
    world:     {provider: gemini, model: gemini-3.8-flash, thinking: low}
    director:  {provider: gemini, model: gemini-3.8-flash, thinking: low}
    narrator:  {provider: gemini, model: gemini-3.8-flash, thinking: low}
    checker:   {provider: gemini, model: gemini-3.8-flash, thinking: low}  # TODO(CROSS_FAMILY_CHECKER) (P13)
  budget_usd_per_session: 2.00   # warning threshold, not a limit (FR-039); null = no warnings
  oracle_free_cap_per_scene: 6   # engine-side stopgap for I-038; logged
  milestone: 1                   # which handler set is live; others are logged as skipped

Response:
  turn_id: str | null            # null during seed and creation
  phase: seed | creation | play | ending
  fiction: str                   # checked narration, or the plain fallback; empty in pure OOF steps
  oof_blocks: [{kind: SEED|CREATE|OFFER|STATUS|WARNING|REDIRECT|CLARIFY|NEAR_MISS|LAST_CHANCE|RECAP|NOTE|EPILOGUE, text: str}]  # 12.15
  pause: Pause | null
  scene_ended: bool
  budget_notice: str | null      # set between turns once spending passes the budget; asks to continue
  flags: {fallback_used: bool, review_flag: bool}

Pause:
  kind: seed_step | create_step | offer | clarify | redirect | near_miss | last_chance | yield_terms | ending | budget
  prompt: str
  choices: [{id: str, label: str}]   # seed_step / create_step: the block's options, in the rules' order
                                     # offer: commit, change, withdraw, go_big, play_safe (when legal)
                                     # near_miss: failure, success_at_cost:<menu_id>
                                     # redirect: accept:<fallback>, other
                                     # last_chance: the 07.5 menu
                                     # ending: new_character, new_world, quit
                                     # budget: continue, stop_here
  default_choice: str | null         # what "move on without choosing" means (PR-02-7, 12.16.2)
  frame_summary: OfferView | null

OfferView:                           # what 01.7.1 says the OFFER shows
  restated_beat: str
  approach: {verb: str, attribute: str, license: str | null}
  difficulty_words: str              # tier name in words
  odds: {success_or_better_pct: int, critical_success_pct: int, critical_failure_pct: int, near_miss_pct: int}
  stakes: safe | risky | dire
  lethal: bool                       # a lethal frame is never auto-committed and follows the warning (07.3)
  threatened_cost: {menu_id: str, form: str, severity_on_failure: str}
  alternate_cost: {menu_id: str, form: str} | null
  only_natural_20: bool
```

## Errors

| Error | When | State effect |
|---|---|---|
| `ModelUnavailable` | provider error or timeout after retries | turn rolled back to `received`; message kept; retryable |
| `ModelRefused` | provider safety refusal | as above, logged under moderation |
| `MissingKey` | no `GEMINI_API_KEY` in the environment or `.env` | nothing written; the front end explains where the key goes |
| `ReplayDivergence` | replay produced a different event | replay stops at the first differing seq and reports it |

A turn is atomic: its events are appended in one transaction at T6 (writes) and T12 (record). A failure
before T6 leaves no state change; a failure between T6 and T11 re-runs T7–T11 on the next call from the
written state, so the player never sees prose that the store does not back. Spending never interrupts a
turn: the budget check runs between turns only.
