# 08 — Loot, crafting and data-generation simulations

Scripts (all seeded, deterministic; Python 3 + PyYAML):
- `08-gen_data08.py` + `08-gen_data08_part2.py` — generates and validates `data/base_items.yaml` (185),
  `item_properties.yaml` (210 properties, 8 flaws, 45 default signatures), `materials.yaml` (59),
  `economy.yaml`, `gen_loot.yaml`, `gen_craft.yaml`, `gen_gift.yaml`, `gen_item_ability.yaml` (159 pool
  entries) and `contrib/{effects,licenses,boundaries,tags}.08.yaml`. Every tag, effect, condition, license and
  ability id is checked against the repo's canonical files; every one of the 45 level-2 creature tags has a
  signature; every kit tag of `kits.yaml` resolves.
- `08-loot-sim.py` → `08-loot-sim-output.txt` — PR-08-1 over 26 reference archetypes (T1 rabble to T5
  dragons) and eight place contexts: 1,000 property drops (3,042 defeat events), repeat-rate streams (200
  decisive drops per archetype), a 500-character attunement test, and a commissioned-craft check.
- `08-craft-sim.py` → `08-craft-sim-output.txt` — the crafting project race (progress vs spoilage), 20,000
  projects per row, by target rung and modifier, with and without a recipe.

## Results (copied into 08's T-08-14 and T-08-16)

| Measure | Result |
|---|---|
| Drop rate by band | 7.3 / 16.0 / 32.5 / 38.8 / 55.3% (targets 10/15/30/40/55 since revision B, I-018; were 10/20/35/50/70) |
| Rungs | masterwork 759, fine 134, common 107 |
| Properties per drop | 0: 107, 1: 156, 2: 737 |
| Relics | bound power 14.0%, any relic 15.5% |
| Gated pool per drop | min 3, median 9, max 18 |
| 09 contract (pool ≥ 3 at tier 1, every base) | 25 of 26 archetypes (exception: a T4 aberration's charm at tier 1) |
| Magnitude repeat vs previous drop | mean 13.5% (target ≤ 15%); worst clockwork 31.7%, slime 25.6% |
| Identical whole item vs previous | mean 3.9%, max 14.1% |
| Item-share compliance after generation | 1,000 / 1,000 (16 refills) |
| 5 attuned items exceeding a share pre-clamp | harm edge 19.4%, edge 18.4%, reduction 26.6% of characters |
| Masterwork craft completion | +7 47.5%, +9 73.8%, +11 87.5%, +13 95.2% (recipe: +7 61.6%) |
| Wondrous craft completion | +11 32.5%, +13 62.4%, +15 86.4% (recipe: +11 56.7%) |

## Tuning history (what the simulation changed)
1. First run: pools at tier 1 were 0–2 entries for 13 of 26 archetypes; repeat rate 25% (fire elemental 100%).
   Added hazard wards, retorts and condition wards per harm branch, physical resistances, wider base kinds
   for senses → 25 of 26 pass; mean repeat 12–14%.
2. Relics at 23% of drops (bound power min tier 2, decisive fallback could pick it) → min tier 3, decisive
   never falls back to a relic → 14–15%.
3. 43 decisive drops lost their signature (signature base kinds vs trophy lists) → signature-honoring base
   selection → 0 lost.
4. Skeleton pools of 2 → the made-by-hands rule (armaments from folk and undead open folk-made properties).
5. Crafting: Flawed on any critical failure gave 40% flawed masterworks at +7 → Flawed only when spoilage
   stands at its last-but-one segment; wondrous spoilage clock 6.

## Revision B (I-016, I-017, I-019)
- **The test now covers the real bestiary.** The repeat and contract checks ran only on 26 hand-written reference
  archetypes, which ignored 09's per-archetype `trophy_base` (08.3.6 step 1). `08-loot-sim.py` now also runs every
  archetype of `data/archetypes.yaml` that yields loot, at each band it can appear at (186 cases), with its own
  trophy base, gear, creature, harm, evidence and org tags. `hash()`-seeded streams (salted per process) became
  `zlib.crc32` seeds, so the output reproduces byte for byte.
- **What it found:** 75 of 186 cases repeated their magnitude property in more than 15% of consecutive decisive
  drops (four at 100%: the raptor's and earth elemental's amulets, the water elemental's), and 15 cases broke the
  09 contract (tier-1 pool < 3). A decisive drop's signature often fixes the base kind (a drake's Drakefire makes
  every decisive drake drop a weapon), so the effective pool is the signature's base kind minus its mod group.
- **Fix:** `08-gen_data08.py#EXTRA_GATES` adds 114 creature, org and deed tags to 58 existing properties' gates, each a kind
  the property's own fiction fits (a wolf-pelt cloak is Warm; acid that eats armor Exposes; arrows pass through a
  skeleton's ribs), and one new water-gated tier-1 property, `prop.tidesense` (I-019). Results: reference set mean
  9.6%, worst 14.6% (clockwork sentinel 31.7 → 5.5%, slime 25.6 → 11.6%); real bestiary mean 8.0%, worst 14.6%,
  none above 15%; 09 contract 186/186 (water elemental's tier-1 pool 1 → 8). Drop rates and rungs unchanged.
- **I-016:** six prostheses in `base_items.yaml` (`item.tool.kit.prosthesis`, a new level-3 tag; body slot
  `fitted`, 08.5.1), each with `offsets {maim, narrows, never}`; `trophy_eligible: false`, so loot is untouched.
- **I-018:** `08-campaign-sim.py` (300 campaigns × 70 sessions, bands 1–5, fights from the encounter tables,
  site treasures, purses and sales) showed property items running a full row ahead of 08.2.7 at P3 (22) and P4
  (45.5). Retuned: drop check 10/15/30/40/55 (was 10/20/35/50/70), hoards T3 one masterwork, T4 one wondrous, T5 one
  wondrous and one masterwork, and a hoard-keeper away from its lair rolls as a trophy (08.3.12). Re-run: P1 4, P2 6,
  P3 13, P4 24 (each within its row or one item above); this file's drop-rate row is the new rates. T-08-17.
