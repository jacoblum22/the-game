# Implementation results: spec 010 (scene state written by code)

Branch `claude/nostalgic-dewdney-eb1cde`, base ffbede0 (milestone-1-playable). Outputs:
`evals/baselines/live_narration_010.txt`, `evals/baselines/longhorizon_010.txt`. Rules wave:
`rules/_process/reports/R2-F-report.md` (T-12-18, DL-12-77).

## Gate table

| Gate | Final overnight live (19 narrated) | **Spec 010 live (19 narrated, Haiku)** | Projection, post-run judge | Target |
|---|---|---|---|---|
| First draft delivered as drafted | 36.8% (7/19) | **42.1%** (8/19) | 63.2% (12/19) | > 50% |
| Turns with a contradicted position | 8 | **6**, none about a person | 0 | lower |
| Turns with a cut, rendered line or fallback | 10.5% (2/19) | **26.3%** (5/19) | 26.3% | < 15% |
| Narrator calls per narrated turn | 1.53 | **1.37** | n/a | ≤ 1.2 |
| Engine errors | 0 | 0 | n/a | 0 |

The live targets are **missed as measured**: the first-draft rate rose 5 points, short of 50%, and cut turns rose.
The projection re-judges the recorded first-draft verdicts with the post-run judge fix; it was **not** re-measured
live (19 of the 25 narrated turns were spent; the sample is ±10 points).

**Offline scripted, 300 lines:** 0 engine errors, 0 contradictions, first draft as drafted 86.1% (89.1% before),
cut turns 13.9% (10.9%), calls per turn 1.28 (1.22). All 43 failing drafts follow draft → repair → repair → render on
must-name lines the canned offline narrator never cites (lead notes, the beat's position line), as at baseline.
Scene-state lines are never must-name. The trajectory also changed (383 turns vs 388), because activity rolls now
come at different times on the NPC RNG stream.

**Suite:** see the final line in the commit message. ruff clean; pyright clean on touched files, except one existing
error in `tests/engine/test_turn_adjudication.py:176` (untouched code). Rules validator 0 ERROR / 0 WARN.

## What the live run showed

- **People no longer contradict.** Before this spec, offline inspection of the same seed showed the cause:
  - a scene change mid-turn kept the old scene's activity lines (in turn 15, Grak "sweeping out the common room"
    was shown in a Ravenford street; in turn 18, the child from Ravenford was listed in the Old Goose);
  - an NPC who answered or squared up kept a fixed activity with "say only this of it";
  - bands from a scuffle never cleared.

  Now each turn shows each present person's activity, posture, hold and manner, plus their band to the PC. In the
  live run, no contradicted position was about a person.
- **The 6 that remained were the judge.**
  - "The fire at the far end of the hall" (5 turns, all in the Old Goose) matched the town's separate place `the
    hall`. This is the place-name ambiguity spec 009-B named.
  - "The lane runs ... toward the temple of Halwin" read a direction as a location.

  Fixed after the run: `claims._not_located_at` and 12.3.1's position row. A common-noun place does not place
  something that is here elsewhere, and a place after a direction word is a direction. A proper name still binds.
- **Cuts not related to scene state:**
  - the audit typed a clue or a document (turns 8, 12);
  - an unratified knowledge claim (15);
  - a door that "closes behind you" (18);
  - "Where is Dunys Brightward?" had no record line to answer it (24). That is an answer-ladder gap: a whereabouts
    question addressed to no one.

## What landed

See [tasks.md](tasks.md). Summary:
- T-12-18 as data (`pacing.yaml#details.scene_writes`) and as a rules table.
- `engine/dm/scene_state.py`: beat writes, response writes, lines.
- `ActivityEntry.slot`.
- The rolled activity is the `activity` detail.
- `PositionSet.band_drop`; bands clear at scene end.
- `write_detail` supersedes an expired slot. This was a latent bug: a scene slot written again after a scene end
  was rejected.
- Freshness skips scene slots.
- The judge fix above.
- `evals/longhorizon.py --keep DIR` keeps the run's stores for diagnosis.

## Deferred

- A live re-measure of the judge fix (about 20 Haiku turns).
- The cut sources above, the whereabouts question in particular.
- A disarm clearing `held` (DL-12-77 "Revisit if").
- Bands between NPCs are cleared but never shown.
