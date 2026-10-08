# Research: memory infrastructure (009 part A)

Background is in `research_notes/Playtest round 2 solutions/A_memory_and_context.md` and the R2-E report; only
the engine decisions are recorded here.

## R1. Where scene cards live
- Decision: the projection folds each scene's card from its own events (`WorldState.scene_cards`, keyed by scene
  id) and closes it at `scene_ended`. `store.rebuild()` regenerates every card; no card event is written.
- Rationale: "computed from the log, regenerated at any time" (12.4.8 step 9) holds by construction; the rebuild
  equality check already in the test suite proves determinism. Older saves get cards by a rebuild (DL-12-73).
- Alternatives: a `meta_set` card at scene end (a stored derived value that could drift from the log); computing
  from `store.events()` on every call (a log scan per packet).

## R2. Archiving
- Decision: archived = not among the top `details.max_active` lasting details by (salience, last use), computed on
  read. The fact stays current, so it stays in the contradiction scope.
- Rationale: no stored flag to keep in sync; the rule only needs the active set to be bounded.
- Alternatives: an `archived` field set by events (needs a re-rank event on every write).

## R3. Scene-end expiry
- Decision: `end_scene` stages a `fact_set` with value `None` superseding each current `scene`/`beat` detail
  (source `ruling`, rule 12.4.8), before `scene_ended`. The details index drops `None` values.
- Rationale: `facts_idx` keeps bi-temporal history only for superseding fact events; a reducer-side removal would
  leave the index thinking the value is still valid.

## R4. Usage marks
- Decision: event `details_used {fact_ids}`; the reducer sets `last_used` to the event's turn number. Part B emits
  it at RECORD (T12) from declarations.

## R5. The explaining event
- Decision: `write_detail(..., because=<record ref>)`; a change is a supersede iff `because` is given. The writer
  does not judge the explanation (part B's diff does, against this turn's record).

## R6. Alias index and full-name preference
- Decision: keys are the PC-known display name, the full name when known, `data.aliases`, the unnamed label and
  role; given and family names are weak keys used only when exactly one entity carries them and the token is not
  inside a matched full name. Matching is whole-word, longest key first.
- Rationale: fixes the harness finding ("Joss Fenn" matched Joss Dunmere and Pell Fenn) and P-085 style lookups;
  true names of unintroduced people are not keys (12.10.2), so a match cannot leak a name.
- Reuse: `mentions.find_existing` keeps its own exact-match semantics (spec 006's file, read only); the index
  reuses `display_name`, `unnamed_label`, `name_known`.

## R7. Where per-role projection happens
- Decision: `build_packet(role, view=WorldState)` calls `view_for(role, state, ctx)` with ctx built from its own
  arguments (focus, message, the last exchange's DM text). Reader, Framer, Narrator and Director packets change
  with no call-site edit; World and Checker pass strings (spec 006 files), so their hookup is part B.
- Rationale: one selection, many projections; no edits in other lanes.

## R8. What the Narrator keeps
- Decision: the selection as today minus motive keys (`wants`, `refusals`, `fears`, `secrets`, `knowledge`,
  `beliefs`, `ties`) and facts with those predicates; plus spotlight (PC-known) and ≤ 2 cards. In-scene
  background facts stay (perceivable now).
- Alternatives: drop all `background` facts (would starve the narrator of seeded scene material in play).

## R9. Recency fix
- Decision: recency reads the started_seq of the current scene and the stored cards (newest two scene starts),
  replacing `state.scene` / `state.last_scene`, which lost the scene before last when no scene is open.
