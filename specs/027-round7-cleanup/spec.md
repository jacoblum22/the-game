# Spec 027: the round-7 cleanup pass

Branch: the worktree branch of this session, cut from `milestone-1-playable` at 0bdf2c2 (specs 023-026 merged).
Rules tag: `[revision: R2-K]`. Ids: DL-12-122..DL-12-128, ledger I-220..I-226.

## Owner decisions (2026-10-09/10): "I agree B, A, A, C"
1. **B (spec 024's question): a person's look works like a place's ("setting once").** A person's look, and an item's
   description, reach the narrator only when the person or item first appears in a scene, or when the player looks at
   them or asks about them. On other turns the people card carries no look line; the narrator still sees the
   conversation and may mention the look again if it chooses. No counting, tracking or gates (don't prevent, don't
   encourage). Items stay listed by name (the player can act on them); only their description follows the rule.
2. **A (DL-01-46): an accepted fallback with nothing at stake takes the time (no roll).** Already built; the DL entry
   becomes owner-confirmed.
3. **A (spec 025's question): willingness holds for the scene,** even when a wary group refuses four times. Kept as
   built; DL-12-118 records the confirmation and a "Revisit if": players report walls even with onward pointers.
4. **C (spec 026's question): `/fix` may pass a one-line note to the re-frame's Framer.** The note is context the
   Framer lacked ("he outranks the guard; the guard should simply let him in"); the Framer still owns the odds.

## Hand-offs (each verified present before it is fixed)
| # | From | Hand-off |
|---|---|---|
| H1 | 023 | No narration after a critical success (explorer [24]-[25]): the passage was written from the roll, but an auto-committed OFFER and its RESULT printed below it, so the roll read as coming after the fiction. |
| H2 | 023 | The journal's "The Golden Plough's furniture 0: …" label (`furniture.0` predicate as words). |
| H3 | 026 | A G4 refusal's words are slugs: "Tam Harlan's detail eyes is milk-white…, as already settled", "can read the writing… is False" (`oof._fact_line`). |
| H4 | 025 | The plan pause said "Still go on: go to the ford?" for a move to the gate: the seed names the haven's gate building after the site feature ("the ford"). |
| H5 | 025 | Dead `change.pay` calls (`pipeline.py:415`, `:846`). |
| H6 | 025 | The narrator prompt's "Do not invent … what someone knows", narrowed per R7-R1: characters may improvise ordinary knowledge as testimony; hook terms and case facts come from the record. |
| H7 | 026 | The dispute guard's `knows_` prefix blocks harmless knowledge facts ("Pell knows your rank"). |
| H8 | 024 → 023 | `READING` matches "what did they say" (people, not writing); the numeral check blocks the player's own sums ("ten silver"). |
| H9 | 023, 025 | Rules: WE-01-2 still shows an Oracle snag; WE-12-11 quotes the old lead sentence; `resolution.yaml`'s reach tie-break disagrees with 01.6.10 (follow the rule text). |

Not in scope (noted only): the Framer's "favour"-sized request offsetting a rank bonus (spec 026, f04): the Framer's
judgment.

## Requirements
- R1 (B): the narrator's packet shows a person's look (`detail`, and narrated `detail.*` facts) and a thing's
  description (`desc`/`look`/`detail` data; written words; `detail.*` and narration-sourced facts about it) only for
  entities that (a) every entity, on a scene opening, a first opening or a look-around turn; (b) came into the scene
  this turn (created, or positioned at the scene's place, by an event of this turn); (c) the player looks at or asks
  about this turn (a look/ask word followed, within a few words, by its name; or the target of an Observe beat or of a
  `learn` goal). Names, pronouns, role, manner, voice and mechanical facts stay every turn. Nothing is written to the
  store to decide it.
- R2 (C): a `reframe` proposal's `value` is a one-line note for the Framer. Code passes it to the re-frame's Framer as
  context (never a fact, never odds), cut to one line; a note that states odds, a number or a roll is not passed
  (the re-frame still runs, the answer says why). The Framer's typed frame decides the odds as always.
- R3 (H1): an auto-committed OFFER and its RESULT are shown above the passage (the roll came first).
- R4 (H2-H8): each hand-off fixed at its shared root (the slug renderer, the seed's gate name, the guard's prefixes,
  the READING regex, the numeral check's allowed set).
- R5 (rules): DL-12-122 (B), DL-01-46 confirmed, DL-12-118 confirmed, DL-12-123 + PR-12-11 (C), DL-12-124 (R3),
  DL-12-125 (H4's seed naming), worked examples and `resolution.yaml` (H9); ledger I-220..I-226; appendix
  re-assembled, anchors and cards compiled, validator 0/0.

## Assumptions (recorded; no clarify step)
- A1: "look" means the look (`detail`); manner and voice stay in the background line every turn (the owner's B names
  the look; the habit is already worded as occasional, DL-12-113).
- A2: a return after leaving is a new appearance (the look is shown again that turn).
- A3: "asks about them" is the player's words naming them after a look or ask word ("about", "who is", "what does …
  look like"); speaking *to* someone ("I ask Grza about the road") is not asking about her.
- A4: a thing's mechanical facts (holder, a ruled state) stay every turn; only how it looks and what it says follow B.
  A read of a written thing still gets its words through the reading lines (12.14.13) as before.
- A5: R3 moves only an auto-committed roll; an explicitly committed OFFER was on the previous screen, so its RESULT
  stays where 12.15 puts it.
- A6: H4 renames new seeds only; old saves keep their names. The reference seed script changes the same way (parity).
