# R2-A report: ranked, budgeted narrator view and cache-aware packet layout

Scope: playtest round 2, synthesis Phase 1, items A P3 and A P6 (`research_notes/Playtest round 2 solutions/`),
plus the 12.11.7 archived-memory leak. Rule edits are tagged `[revision: R2-A]`; decision DL-12-38. Appended
after every step.

## Step 0: baseline (2026-10-08)
- Validator: 0 ERROR / 0 WARN. Offline replay game (`offline_seed11`, 134 calls): median share of each packet
  byte-identical to the same role's previous packet: Director 25%, World 99.8% (mean 83%), Narrator 95%,
  Reader 97.5%, Framer 86.5%. The Director's first difference is always in the core (the trigger list).
  Median view about 1,094 tokens (Narrator, Reader).

## Step 1: engine
- `engine/retrieve/scene.py`: `scene_facts` returns pins (open commitments, written words, active NPC memories;
  archived memories excluded, 12.11.7) then facts ranked by salience + recency (per scene) + relevance +
  adjacency, each within a token budget; `scene_scope` pins things with written words and fills the rest of the
  place's things newest first within a budget; `focus_ids` gives the relevance ids. The `WRITTEN` exemptions
  and the `MAX_SCENE_OBJECTS` carve-out are gone (they are pins).
- `engine/dm/packet.py`: per-section token budgets; threads and the known cast by 12.6.6 weight; the
  active-trigger list moved from the core to the head of the view. `engine/retrieve/cards.py`: cards chosen by
  the same priority, returned stable to volatile.
- `rules/data/pacing.yaml#packet.view_budget` (hand-written file, no generator).

## Step 2: rules
- 12.2.4 items 1-3, 00.15.4, 12.11.7 revised; DL-12-38 in `appendix/fragments/DL-12.md`; appendix
  re-assembled; anchors compiled (0 errors); `engine/build/cards.json` rebuilt; validator 0 / 0.

## Step 3: measurement
- Replay game after: Director 78% median (from 25%), World mean 95% (from 83%); other roles unchanged; median
  view about 1,099 tokens (the trigger line moved into it). Seeded 300-scene store: 1,564 / 1,586 / 1,594 view
  tokens at scenes 50 / 200 / 300, all pins present.

## R2-A2 follow-up: the people present get a budget (2026-10-08)
- Cause: every NPC positioned at the scene's place joins `cast_present` at scene start (12.4.1), and `scene_view`
  rendered each as a full, unbudgeted profile (~80 tokens). Aged harness: six more residents at the home inn by
  scene 300 added ~460 tokens.
- Engine: `engine/retrieve/scene.py` `cast_order` (focus, then most recent dealings, then 12.6.6 weight) and
  `also_here`; `engine/dm/packet.py` `scene_view` keeps full profiles within `view_budget.cast` (320) and names the
  rest on one `also here:` line within `cast_line` (80, then "and N more"); `scene_setting` uses the same ranking
  and budgets. Pins were already hard-capped by `fit` (kind order, then newest); documented.
- Rules: 12.2.4 item 3 bullet "People present" `[revision: R2-A2]`; DL-12-39; appendix re-assembled; anchors 0 / 0.
- Measurement: unit 300-scene store with every walk-on kept at the place: 1,828 / 1,839 / 1,844 view tokens at
  scenes 50 / 200 / 300. `evals/longhorizon.py --mode aged`: Narrator view 1,337 / 1,612 / 1,952 before, 1,190 /
  1,261 / 1,357 after (remaining growth: facts filling to 500, the `also here:` line filling to 80; both capped).
  Replay game re-recorded.
