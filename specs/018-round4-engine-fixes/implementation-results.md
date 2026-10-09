# Implementation results: spec 018 (round-4 engine fixes)

Scope: `rules/_process/reports/R2-I-report.md`, "Engine checklist: spec 018 (items 1-6)"; DL-12-96..100, DL-01-36.
Spec-kit lean: [spec.md](spec.md), [plan.md](plan.md), [tasks.md](tasks.md) (with a lean analyze table; no
clarify). Engine API: `engine/CONVENTIONS.md`, last section. Lane 017's files were touched only in small
separate places: `pipeline._start` (3 lines, the "who?" check), `pipeline._moved` / new `band_words`; `oof.py` and
`turn.py` were not touched.

## What was built, by item
1. **Plain speech (DL-12-96)**: the speaker card, the narrator's speech line and `guarded` willingness no longer ask
   for "hearsay or a guess, hedged"; NPCs answer plainly, a hedge only for a cautious or gossipy character.
2. **A target can be a description (DL-12-97)**: `Change.description` (Reader `change.description`, string or null;
   in the Laya log). `persuade_to`/`open`/`close` on a description write a scene fact on the scene's place
   (`agreed.<slug>`, persistence `scene`), cleared at scene end. If the description names exactly one person in
   scope, that person is the slot. No group entity, no spokesperson, no casting call (the clue-bearing `learn` already
   routes through the case).
3. **Movement (DL-12-98)**: outside a conflict an approach ends **beside** the target in one beat (reach 2+); the band
   step stays for a conflict and a partial. A Move to the place the PC is in is `trivial` (a look) and, like a Move
   with no target, writes no "still in X" line. A turn whose record starts a scene narrates with purpose `scene_open`
   ("narrate this turn, then frame the new scene it reaches"), and a travel cut's scene line is must-name and comes
   after the beats. No approach code was needed in `necessity`: the Framer's Move rubric already gives open ground a
   `trivial` base and an obstacle (the bakery queue) a rolled class.
4. **Already true; no target (DL-01-36)**: `change.already_true` (the actor holds the item; the person's `agreed`
   covers the same act both ways at 0.6; the thing is already open/closed) → `trivial`, no OFFER, the record says it
   ("Agreed already by Ivas Terier: ..."). `change.needs_target`: a persuade/take/give/restrain/open/close with no
   id, target or description is a G0 question ("ask the player who they mean"), never a roll.
5. **Setting once (DL-12-99)**: `scene_setting(full=False)` on later turns of a scene: the place's description, look,
   furniture, landmarks, "within" and "nearby" are dropped for "already described this scene"; people present
   (pronouns), exits and time stay. Full again when the player looks around.
6. **Patches (DL-12-100)**: no self-introduction (prompt lines); `pc_quotes` catches the quote beside a "you say"
   clause even under an NPC speaker (and `_said` keeps the NPC's own line); `persuade_to` never picks the actor and
   words its result "Agreed by X: <act>" (the "You agrees to Ivas carries word" bug was the PC in `what`).

**Deleted or simplified**: the three hedging instructions; band-by-band approach outside a conflict (its `close`
floor never reached engaged); the "still in X" position line (both branches); `crowd_response`'s special case in
`expire_events` (now every scene-persistence fact); look/furniture in every turn's packet; `take`'s "already have"
refusal; `_moved`'s dead else-branch. Not added: group entities, a find procedure, a new necessity reason, an
optional self-introduction scan (analyze A3).

## Gates
- **Full suite**: 1773 passed, 4 skipped (was 1765 + replay). New `tests/engine/test_round4_fixes.py` (5 tests) from
  two truncated saves (`tests/fixtures/fighter_lane_turn5.db.gz`, `talker_ivas_turn5.db.gz`, which keep Haiku's own
  Reader/Framer answers for the replayed turns): the fighter's walking-in-place loop (inputs 20-22) is one approach
  ending beside the lane and a no-roll look; "persuade the refugees" applies on the description; the talker's
  redundant persuade is certain (no roll, no OFFER) and reads "Persuading: Ivas Terier"; the plain-words grammar;
  the walk to the inn narrates as a scene opening with a must-name arrival; the look line reaches the narrator once
  across three turns at the inn; "who?" before framing; "Fair enough," caught. Updated: two band tests (now "beside"),
  the take-already test. Replay re-recorded. ruff clean; pyright 0 errors on every touched file.
- **Offline long-horizon (scripted, seed 7)**: 0 engine errors (baseline 0). Novelty-4 **0.65** (baseline 0.70 on the
  same seed). It fell, and the cause is identified: the scripted player re-asks the same NPC the same thing ~70
  times; each re-ask used to roll and print a fresh garbled "The healer agrees to I ask Rakak the Mender", and now
  prints the same "Agreed already by the healer: ..." (DL-01-36 working as intended on a degenerate script). The 16
  "You are still in Ravenford" lines are gone. First draft delivered as drafted 64.3% (baseline 59.5%); narrator
  calls per narrated turn 1.71 (1.81).

## Live (Haiku through the Claude CLI; Sonnet persona player; 15 turns each)
| Run | Hedged NPC lines | Walking-in-place lines | Wasted successes | Repeated 5-grams (3+ turns, setup excluded) |
|---|---|---|---|---|
| talker before (20261008-192926) | 19/60 (32%) | 2 | 0 | 2 |
| talker after (20261008-224203) | 3/37 (8%) | 0 | 0 | 3 |
| fighter before (20261008-192946) | 3/9 (33%) | 3 | 4 ("no one named" etc.) | 15 |
| fighter after (20261008-224208) | 0/4 | 2 ("still at the crossroads cross") | 0 | 2 |
| fighter after the fix below (20261008-225808) | 0/10 | 0 | 0 | 27 (cloak/watch descriptions) |

The first fighter run found the "still in X" line still causing walking in place for a Move with no target
(following tracks); that line was then deleted and the fighter re-run. The persuade there reads "Now: Agreed by
Tamwen Greenley: Tamwen opens the chain a crack." No "You agrees", no "a few strides short", no "Not applied".

**Main player complaints (after)**: talker: pronoun flips (Tibo, Osa), NPCs stonewalling or contradicting themselves,
/fix replies that "keep it" with nothing visibly repaired, time of day jumping, repeated well/lane scenery. Fighter:
a modifier reason that doesn't fit ("talking with a neighbour −2"), a misreading /fix that didn't change the OFFER,
"[NEAR MISS] hidden." lines, standing on the ledge after a fall, the d20 display. Scenery repetition now comes from
people's descriptions ("his cloak of foreign cut" ×5), which stay in the setting every turn for pronouns: R6's
phrase feedback (DL-12-99's revisit condition) is the next step.

## Notes
- Analyze A2: the look is not re-listed as optional material on later turns; a one-line "already described" note
  replaces it, because listing it every turn is what repeated.
- Lane 017 merge: `pipeline.py` touches are `_start` (the "who?" check before NECESSITY), `band_words`, `_moved`
  (signature `reach`), and `_finish`'s `_moved(env, plan, delivered)` call.
