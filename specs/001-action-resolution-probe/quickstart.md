# Quickstart: Action Resolution Probe

Validation guide only — implementation details belong in `tasks.md` (from `/speckit-tasks`) and
the actual code, not here.

## Prerequisites

- Python 3.11+
- An Anthropic API key, set as `ANTHROPIC_API_KEY`
- `pip install anthropic pytest`

## Run an interactive session

```bash
python src/main.py
```

Starts one session with a fresh CharacterState (see [data-model.md](data-model.md)). Type
freeform actions at the prompt; the DM resolves them per [contracts/tools.md](contracts/tools.md)
and narrates. The session log is written to a JSON file on exit (path printed at startup).

## Run the scripted consistency check (replaces the earlier human relay)

```bash
python tests/probe/run_scripted_session.py
```

Drives at least 10 resolved actions plus a few stakes-free lines against the live API using a
fixed script (mirroring the kind of turns exercised in [probe-results.md](probe-results.md):
investigation, a compound question, a combat attempt, an edge-case time-pressure action). On
completion it prints:

- **SC-001**: % of intended-to-resolve actions that produced a computed degree.
- **SC-002**: count of turns where narration contradicted its own computed `degree` (target: 0;
  this is the number the earlier probe couldn't actually measure without a human reviewer).
- **SC-003**: whether every state change is traceable to a specific `update_state` call (pass/fail
  per turn).
- **SC-004**: whether every stakes-free line correctly skipped `roll_check`.

**Expected outcome**: this is a genuine test, not a foregone conclusion — per probe-results.md's
own scope caveat, the relayed-chat session never verified real tool-calling reliability. A
result here that's worse than the relayed session's 0-contradiction outcome would itself be a
valid, useful finding, not a bug to hide.

## Run unit tests

```bash
pytest tests/unit
```

Covers only `resolution.py`'s pure degree-of-success calculation — no network calls, no live
model involved. This should be fast and fully deterministic.
