# Contract: Session API

The only surface front ends use (the CLI now, the web app later). Everything else in `engine/` is
internal. Types are Pydantic models; JSON shown for readability.

## Operations

| Operation | Input | Output | Notes |
|---|---|---|---|
| `Session.new(campaign_path, scene_fixture, pc_fixture, seed, config)` | paths, int seed, `SessionConfig` | `Session` | Creates the SQLite file, loads and validates `rules/data`, frames the scene (PR-12-7) |
| `Session.open(campaign_path, config)` | path | `Session` | Resumes at the last event, including an open pause (FR-025) |
| `session.opening()` | — | `Response` | The scene's framing narration (already checked) |
| `session.submit(message)` | the player's text, verbatim | `Response` | Runs PR-12-1 until delivery or a pause point |
| `session.answer(choice_id)` | an id from the open pause's `choices` | `Response` | Shortcut for a PENDING_ANSWER; free text via `submit` also works (12.2.6) |
| `session.codex(view="codex")` | `codex` | `CodexView` | Shown and available state only (00.6.4). Not rendered by the slice's CLI except `/sheet` |
| `session.turn_record(turn_id)` | id | `TurnRecord` | data-model.md §4 |
| `session.save(label)` / `session.branch(label)` | label | branch id | Copy-free: branches are event-log forks |
| `Session.replay(campaign_path, until_seq=None)` | path | `ReplayResult` | Rebuilds state from events with `ReplayAdapter`; reports any divergence (FR-026) |

## Types

```yaml
SessionConfig:
  models:                       # pinned ids; research.md R2
    reader:   {provider: gemini, model: gemini-3.8-flash, thinking: low}
    framer:   {provider: gemini, model: gemini-3.8-flash, thinking: low}
    world:    {provider: gemini, model: gemini-3.8-flash, thinking: low}
    narrator: {provider: gemini, model: gemini-3.8-flash, thinking: low}
    checker:  {provider: gemini, model: gemini-3.8-flash, thinking: low}   # TODO(CROSS_FAMILY_CHECKER): move to another family (P13)
  spend_cap_usd: 1.00            # per session (FR-027)
  oracle_free_cap_per_scene: 6   # engine-side stopgap for I-038; logged
  auto_commit: false             # 01.7.4 preference
  replay: false                  # true → ReplayAdapter for every role

Response:
  turn_id: str
  fiction: str                   # checked narration (or the plain fallback)
  oof_blocks: [{kind: OFFER|STATUS|WARNING|REDIRECT|CLARIFY|NEAR_MISS|ODDS|NOTE, text: str}]  # 12.15
  pause: Pause | null
  scene_ended: bool
  spend: {turn_usd: float, session_usd: float, cap_usd: float}
  flags: {fallback_used: bool, review_flag: bool}

Pause:
  kind: offer | clarify | redirect | near_miss
  prompt: str
  choices: [{id: str, label: str}]   # offer: commit, change, withdraw, go_big, play_safe (when legal)
                                     # near_miss: failure, success_at_cost:<menu_id>
                                     # redirect: accept:<fallback>, other
  frame_summary: OfferView | null

OfferView:                           # what 01.7.1 says the OFFER shows
  restated_beat: str
  approach: {verb: str, attribute: str, license: str|null}
  difficulty_words: str              # tier name, never the DC in fiction; the OOF block may show numbers
  odds: {success_or_better_pct: int, critical_success_pct: int, critical_failure_pct: int, near_miss_pct: int}
  stakes: safe | risky | dire
  lethal: bool
  threatened_cost: {menu_id: str, form: str, severity_on_failure: str}
  alternate_cost: {menu_id: str, form: str} | null
  only_natural_20: bool
```

## Errors

| Error | When | State effect |
|---|---|---|
| `SpendCapReached` | the next call would exceed `spend_cap_usd` | none; session saved; resumable with a higher cap |
| `ModelUnavailable` | provider error or timeout after retries | turn rolled back to `received`; message kept; retryable |
| `ModelRefused` | provider safety refusal | as above, logged under moderation |
| `ReplayDivergence` | replay produced a different event | replay stops at the first differing seq and reports it |

A turn is atomic: its events are appended in one transaction at T6 (writes) and T12 (record). A failure
before T6 leaves no state change; a failure between T6 and T11 re-runs T7–T11 on the next call from the
written state, so the player never sees prose that the store does not back.
