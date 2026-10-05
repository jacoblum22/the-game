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
| Drop rate by band | 8.1 / 21.6 / 35.1 / 51.3 / 75.9% (targets 10/20/35/50/70) |
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
