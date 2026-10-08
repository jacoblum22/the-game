# Research: 008 part A

No open unknowns; each item is a decision with its reason.

**R1 Where packs run.** Decision: `WorldSeed.record()` calls `seed_packs(reg, seed)` after `assemble`. Rationale:
every engine world (game, `build_rolled`, `rebuild_seed`) is then packed, the check sees packs, and keyed
streams keep the 13 steps' draws unchanged (DL-12-61). The parity test compares with the reference's
`seed_packs(build_seed(seed), seed)`. Alternative: pack in `write_world` only (rejected: the seed check could not
check packs, and `build_rolled` would differ from the game).

**R2 Keyed dice.** Decision: `keyed(seed, *parts)` = `Dice(random.Random(int(sha256("|".join(...))[:15], 16)))`,
byte-identical to the reference. A seed of `None` (a `WorldSeed` built from bare streams) keys on `0`.

**R3 Store shape.** Decision: places keep look/furniture/exits in entity data (they already carry the whole
10.1.2 record); NPC `knowledge` is a sealed data field (`places.NPC_SEALED`), `stance` plain data; walk-ons are
NPC entities (`name_known: False`; a missing subject is not positioned); documents are `object` entities with a
`text` fact (`retrieve.scene.WRITTEN`, so reading delivers them, P-110); cases go to meta `world.cases`
(never rendered). Alternative: pack facts as store facts with knowledge records (rejected for part A: ~80 facts
would enter fact ranking and packets; part B's rung 2 reads the pack from data).

**R4 Casting.** Decision: `engine/gen/cast.py`; the base pool is the old `incident._people` filter (re-exported
for `world_step`); role gate by `role_key` (and role tags); scope = the settlement concerned; weights from
`social.yaml#cast.fill.weights`; the pick uses a keyed stream on (game seed, role, scope), so the same question
casts the same person while the pool is unchanged (the `recency` row). Empty pool -> `None`.

**R5 Reduced case on demand.** Decision: `case_for_question(tx, role_words, place)` maps the role to an inciting
option (missing, duel, dying_messenger, refugees, offer), builds a region-record view of the store
(`world_rec(state)`), runs the same `reduced_case`, and writes new walk-ons, documents and the record. Other story
roles return `None` (casting answers them). Alternative: a full PR-15-6 solution generator (rejected by D4).

**R6 Interim `settle_who`.** Decision: answer order = stored `who_is_*` fact -> a case whose subject role covers the
question (its subject; node 1 marked found) -> on-demand case -> casting -> "no one you know". Part B replaces the
caller side with the ladder; the pointer helper (`case.pointer`, core holder first) is exposed now.

**R7 Placement audit in M1.** Decision: move the id to milestone 1 in `MILESTONE_HANDLERS`; register in `h15.py`;
for each case in meta and each unfound necessary node, count live placements (person/document holder exists and
`exists == "exists"`; a place exists; an object is live unless `lost`); below `min_live` (2) place the reserve as a
walk-on witness in the haven, then a PR-15-7 generic placement (a walk-on "someone who heard"), logged in the
case record.

**R8 I-149.** Decision: `incident.start_knowledge(ctx, tx)` at every new PC's opening: when the PC's anchor bond
NPC lives in the haven settlement, write a `name` fact on each haven officer (role key in smith/crafter,
innkeeper, guard/captain, healer, wise, scribe) and each head of a faction seated in the haven, with a PC
knowledge record (`how: recalled`, the closest existing enum to 12.10.2's `common`). `name_known` already
honours such records.

**R9 Names.** Decision: when 40 draws find no unused given name, compose fresh given names from the people's
`given_start` x `given_end` syllables (`tbl.12.seed.names`) not yet used; only then reuse a given name. The
seed's own draws are untouched (the fallback runs only where the old code raised).

**R10 Packet measurement.** Decision: compare `evals/longhorizon.py --mode scripted` view tokens before/after
(same seed 7) and the e2e `Driver.packet_sizes()`; report the delta.
