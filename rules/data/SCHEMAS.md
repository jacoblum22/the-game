# data/SCHEMAS.md — Schemas of every data file

Owner: 00-architecture (00.16). This file fixes the **required** fields of every `data/*.yaml` file
listed in T-00-19, so that sixteen chapters written in parallel produce compatible data. Owning
chapters may add **optional** fields (document them in their chapter's Tables section); removing or
renaming a required field, or changing its type, is an amendment to 00. Section names are the file
names so rules can cite `data/SCHEMAS.md#<file>`.

## Notation

- `str`, `int`, `bool`, `any`; `[T]` = list of T; `{k: T}` = mapping; `A|B` = either; `?` = optional.
- `tag` = an id in `data/tags.yaml`; `S1..S5` = severity id; `band` = 1..5; `duration` = a form in
  `substrate.yaml#duration_forms`; `limits` = `{per: <boundary id>, uses: int}`;
  `effect_ref` = `{effect_id: eff.*, params: {…}}`; `expr` = a state expression over the documented
  context keys; `clock_template` = a Clock (00.8.1) without `id`, `filled`, `status`, `history`.
- Ids use the prefixes of 00.16.2 and are globally unique and never reused.

## Common envelope (every file)

```yaml
# <file> — purpose / owner / schema: data/SCHEMAS.md#<file> / basis
schema_version: int            # required, starts at 1
<collection_key>: [Entry]      # the file's main list (named per section below)
blocks: [{owner: "NN", entries: [Entry]}]   # only where T-00-19 allows owner-blocks
```

Every **Entry** has, in addition to its file-specific fields:

| Field | Type | Req | Meaning |
|---|---|---|---|
| `id` | str | yes | prefixed, snake_case, unique |
| `name` | str | yes | human name |
| `tags` | [tag] | yes (may be empty) | from tags.yaml |
| `lifecycle` | provisional\|permanent\|retired | yes | default provisional (00.16.3) |
| `superseded_by` | id | when retired | successor |
| `basis` | [str] | yes | citations per 00.1.6 |
| `notes` | str | ? | non-binding commentary (never mechanics) |

Mechanics are never prose-only: every mechanical consequence is an `effect_ref`, a number on a named
scale, a clock, or a table reference (00.16.4).

**Owner-blocks** (amended at integration). Where T-00-19 allows them, a file's `blocks:` list holds one
`{owner: "NN", entries: [...]}` per chapter, ordered by owner number; `boundaries.yaml` names the list
`handlers` instead of `entries`. Fragments written in parallel (`data/contrib/<file>.NN.yaml`) are merged into
these blocks at integration and kept in `_process/merged-contrib/` as the record.

**Optional fields** (amended at integration). Owning chapters document their optional fields in the data file's
header comment and in their chapter's Tables section; every key not listed as required below is optional and
is read only by the rules that name it. Any file whose chapter owns clock templates may carry an optional
top-level `clock_templates` key (IR ch.12). The documented optional keys, by file:

| File | Optional keys documented in |
|---|---|
| abilities.yaml | header; T-05-2 |
| afflictions.yaml, injuries.yaml, last_chance.yaml, harm.yaml | headers; ch.07 Tables (harm.yaml holds many keyed sections beside its seven required keys) |
| archetypes.yaml, adversaries.yaml, behaviors.yaml | T-09-14 (archetypes.yaml also holds `powers`: the `pow.*` adversary-only mechanics) |
| base_items.yaml, item_properties.yaml, materials.yaml, economy.yaml, gen_loot/craft/gift/item_ability.yaml | T-08-1 |
| basic_verbs.yaml (anchor fields) | T-01-11 |
| callings.yaml, hybrids.yaml, vehicles.yaml, gen_absorb.yaml | T-04-2, T-04-3, T-04-5, T-04-9 |
| composites.yaml, rituals.yaml | headers; ch.05 Tables |
| conditions.yaml, conflict.yaml | headers; ch.06 Tables (`reserved_by_00`, `intent`, `diminishing.group`, `diminishing.counter_decay`) |
| evidence.yaml | T-03-2 … T-03-11 (`quality`, `quality_by_basis`, `flags`, `blast_radius`, `counted_rules`, `conduct`, `conduct_tests`, `witness`, `verb_default_tag`, `item_grounding`, `functions`, `ledger_view`, `calibration`, `backstory`) |
| factions.yaml, world_turn.yaml, calendar.yaml, legacy.yaml | T-11-1 |
| hazards.yaml, travel.yaml, sites.yaml, traps.yaml, weather.yaml | headers; ch.10 Tables (band-indexed tiers `dc_tier_by_band`, `severity_by_band`; sub-tables; `archetype_signs`; `terrain_defaults`; `states`; `climates`) |
| oracles.yaml, pacing.yaml, anchors.yaml | headers; ch.12 Tables (row fields `writes`, `tags`, `phase_substitute`, `fallback`, `recency_window` …; pacing extensions incl. `packet`) |
| world_seed.yaml | header; ch.12 T-12-15, T-12-16 [revision: I-028] |
| origins.yaml, gen_birth.yaml, kits.yaml | T-02-14 |
| region_*.yaml | T-13-16; 12.16 (`seed`, `calendar`, a site record's `denizen_table`) [revision: I-028] |
| resolution.yaml | header; ch.01 Tables |
| social.yaml, investigation.yaml, downtime.yaml | headers; ch.15 Tables |
| companions.yaml | T-16-1 … T-16-22 |

---

## tags.yaml
Owner 00 (levels 0–2) / 03. Keys: `facets`, `tags`.
- **Facet**: `id` (one of the ten), `name`, `steward` ("NN"), `domain` [str], `signed`? bool, `definition`.
- **Tag**: `id` (dot path), `name`, `parent` (facet or tag id), `level` int (1..4), `definition` ("True
  only when… False for…"), `distinguish`? str, `lifecycle`; conduct axes also `positive_pole`,
  `negative_pole`; `aliases`? [str] (natural-language synonyms for retrieval); `domain`? (narrowing).

## attributes.yaml
Owner 00. Keys: `ranges`, `tie_break`, `attributes`, `defense_formula`, `effect_dc_formula`.
- **Attribute**: `id` (might|agility|endurance|wits|intellect|presence|resolve), `name`, `governs`,
  `distinguish` [{vs, test}], `derived` {value, owner}.

## scales.yaml
Owner 00; values under `owner_of_values: "NN"` are set by that chapter within the stated envelope.
Keys: `dice`, `check_modifier`, `degrees`, `obstacle_tiers`, `severity`, `stakes`, `reach`, `levers`,
`standing`, `bands`, `resources`, `ability_slots`, `clock_sizes`, `clock_omen_stages`, `oracle_odds`,
`time`, `visibility_classes`, `lifecycle`, `gate_classes`. Shapes as in the file; a chapter changing
an `owner_of_values` number records the old and new value and the recomputed calibration table in its DL.

## substrate.yaml
Owner 00; every list closed. Keys: `hooks` [{id, group, fires, params?}], `operations` [{id,
params}], `quantities` [str], `modifier_families` [{id, applies_to, stacking, cap…}],
`stacking_families`, `same_effect_rule`, `evaluation_pass`, `regimes`, `trigger_order`,
`trigger_order_within_group`, `behavioral_slots` [{id, meaning}], `recursion`, `condition_stacking`,
`condition_categories`, `duration_forms`, `limits_form`, `reserved_ids` {range_bands,
positional_flags, harm_states, cost_menu, conditions, generator_domains, fill_methods,
degree_effects, clock_kinds, license_kinds, acquisition_path_types}.

## effects.yaml
Owner 00 (core); owner-blocks 02, 04–11, 15, 16 (02 amended at integration). Keys: `core`, `blocks`.
- **EffectDefinition** (00.10.1): `id` eff.*, `op` (substrate.operations), `quantity`? (substrate
  quantities; required for modify/multiply), `family`? (required for modify/multiply), `regime`
  (substrate.regimes), `hook`? (required for independent_trigger), `slot`? (required for
  priority_exclusive), `params` {name: type or range}, `applies_when`? expr (context keys per 00.10.1),
  `limits`? limits,
  `player_only`? bool, `adversary_only`? bool, `text` (positive, literal template rendered verbatim
  into narration packets), `lifecycle`.

## basic_verbs.yaml
Owner 00 (listed fields) / 01 (`anchor`). Keys: `verbs`, `free_activities`.
- **Verb**: `id` verb.*, `name`, `covers` [str], `excludes` [{what, needs}], `attribute`
  (attr|by_method|none), `alt_attributes` [{attribute, when}], `reach_unit`, `traits` [tag], `anchor`
  (01: {rule_id, knobs [{knob (T-00-20), default, allowed_deltas}], degree_table, obstacle_classes? [{id, base
  (a tier id or by_hazard), examples}] (01.6.5, at most six) [revision: R2-C]}), `lifecycle`.

## boundaries.yaml
Owner 00; owner-blocks for every chapter's own handlers. Keys: `phases`, `boundaries`, `blocks`.
- **Handler**: `id` h.NN.*, `boundary` (id, list, or "*"), `phase` 1..9, `interrupting` bool (or a
  rule), `effect` (one line; the chapter rule defines behavior), `rule_id`? (the chapter rule), `before`?
  [handler ids of the same phase it runs ahead of] (00.7.5, amended), `status`?, `lifecycle`?.

## resolution.yaml
Owner 01. Keys: `dc_tiers` [{id, dc}] (must satisfy CT-1..6), `degree_rule` {critical_band,
natural_20, natural_1}, `near_miss` {min, max}, `read_delivery` [{degree, near_miss_taken?,
reach_delta}], `read_costs` [{stakes, degree, severities [S1..S5]}], `cost_menu` [{id (cost.*),
standard_form, heavy_form, fits_when, effect_refs}], `delivery_counts` [{reach, formula}],
`oracle` {rungs [{id, yes_on?, roll}], doubles}, `fate` {max, start, earn [str], spend [{use, cost}]},
`auto_commit` {default, allowed_when, never}; optional `frame_guards` (00.3.9(b), 01.6.13) and `stakes_cost_menus`
{source: [cost.*]} (01.6.11) [revision: R2-C].

## origins.yaml
Owner 02 (owner-block 13; setting origins pass PR-02-9). Key `origins`. **Origin**: `id` orig.*, `name`, `tags`, `attribute_rules`
{fixed?: {attr: int}, free_points: int, sum}, `licenses` [license_id], `competence` [{tag, value}],
`languages` [lic.lang.*], `kit` [{item_tag, quality, quantity}], `hooks` [str], `birth_pool` (gen.birth
source tags), `tradeoff` str (P4), `lifecycle`, `basis`.

## gen_birth.yaml, gen_loot.yaml, gen_craft.yaml, gen_gift.yaml, gen_item_ability.yaml, gen_absorb.yaml
Owners 02 (birth), 08 (loot, craft, gift, item_ability), 04 (absorb). One file per domain. Keys:
`domain` (gen.*), `output_kind` (item|property|ability|license|attribute_variance), `circumstances`
[{id, true_only_when, false_for, default?: bool}], `fill_map` [{circumstance, fill_method
(signature|biased|chosen|weighted|recipe), bias_tag?}], `quality_map` [{circumstance, degree,
quality_rung}], `quality_rungs` [{id, signature_slots 0|1, magnitude_slots int}], `degree_effects`
{critical_success: greater|none, critical_failure: flawed|none}, `tier_rule` {signature, magnitude},
`recency_window` int (default 5), `slot_cap` int, `pool` [PoolEntry]. `gen.birth` (02) uses three declared
extensions: `quality_rungs[].magnitude_layers` (slots drawn by layer; `mod_group` = layer), `degree: none` on every
draw, and an entry-level `excluded_when` (the cap check moved before the draw) (00.11.1, amended). `gen.pick`
(04) is registered with no file of its own: it is PR-04-5 over `abilities.yaml` (00.11.1, amended).
- **PoolEntry**: `id` prop.*|ab.*|…, `gate_tags` [tag], `excluded_tags` [tag], `base_kinds`? [tag],
  `mod_group` str, `weight` int ≥ 1, `signature_of`? [arch_id], `signature_eligible`? bool,
  `min_tier` int, `tiers` [{tier, effects [effect_ref]}], `flaw`? effect_ref, `player_only`?,
  `adversary_only`?, `cannot_absorb`?, `lifecycle`, `basis`.

## kits.yaml
Owner 02 (owner-block 13: the setting origins' kits). Key `kits`. **Kit**: `id`, `name`, `items` [{item_tag,
quality, quantity}], `coin` int.

## evidence.yaml
Owner 03. Keys: `weights` {challenge_band [..], stakes {..}, witnessed, lethal_context},
`antigrind` {repeat_factor [..], reset_boundary}, `recency` {window, weight}, `counted` [{id,
hook, filter, tags [tag], weight}], `significance_criteria` [str], `exclusions` [str],
`tag_event_fields` (extensions to 00.6.8). A counter's `tags` may be empty when it carries a `tag_source`
(the tag is read from the event) (amended at integration: IR ch.03 #2).

## callings.yaml
Owner 04. Key `callings`. **Calling**: `id` call.*, `name`, `kind` specialist|hybrid, `key_tags`
[tag] (specialist: one tag; hybrid: via hybrids.yaml), `thresholds` {primary, secondary},
`confidence` (04's definition inputs), `tiers` [{tier, competence [{tag, value}], capabilities
[license_id], synergy [comp_id], attribute_increase?: attr, crystallization {vehicles [veh_id],
requirement}}], `max_tier` int, `shadow` {conduct tags, forbidden_acts [str]}, `oath`?,
`focus_generation`? [effect_ref], `vehicles_default` [veh_id], `lifecycle`, `basis`. A calling's `tiers` may be
given fully expanded (as the file ships) or as a reference to a shared ladder that the loader expands, provided
the expanded record is identical (amended at integration: IR ch.04, "ladder references").

## hybrids.yaml
Owner 04. Key `hybrids`. **Hybrid**: `id` hyb.*, `branches` [deed branch, deed branch] (distinct),
`calling` call.* | `none` (explicit "no hybrid" entries allowed), `prerequisites`, `lifecycle`.

## vehicles.yaml
Owner 04. Key `vehicles`. **Vehicle**: `id` veh.V1..V14, `name`, `maps_to` [grant|offer|abstain|
revocation], `recognizer`, `staging`, `offer_form` {accept, decline, defer}, `witness_required` bool,
`scope`, `rules` [str], `org_tags`? [tag].

## abilities.yaml
Owner 05. Key `abilities`. **Ability** = License (00.12.1) with `kind: ability|spell`, plus required:
`activation` active|passive, `regime`, `effects` [effect_ref], `cost` {focus}, `limits`, `slot_class`
calling|acquired|equipped|license (`license`: a branch working held through a magic training license, no slot,
with `granted_by`, `deed_tag_rule`, `rank_rule`; 05.7.11, revision I-009), `limitation` str, `weakness`? str, `cost_text`? str (P12 separate fields),
`narration_may_not_imply` [str], `principle`, `stretch`, `emulate`?. The top-level `scope`, `effects`, `cost` and
`limits` are rank 1; a file may instead let the loader read them from `ranks[0]`, provided the expanded record is
identical (amended at integration: IR ch.05).

## rituals.yaml
Owner 05. Key `rituals`. **Ritual**: License fields + `clock` clock_template, `components` [str],
`time_per_tick` duration, `failure_costs` [cost ids], `effects` [effect_ref].

## composites.yaml
Owner 05 (owner-block 04 for calling synergies). Key `composites`. **Composite**: `id` comp.*,
`keys` [exactly two], `key_kind` (deed_branch|conduct_axis|harm_branch|composite_key_license),
`active_when` expr (both keys present and not suppressed), `effects` [effect_ref], `suppresses`
[effect_id], `lifecycle`.

## licenses.yaml
Owner 05 (owner-blocks 02, 04, 08, 13, 15; 04 and 15 amended at integration). Key `licenses`. Every entry conforms to License (00.12.1): `id`
lic.*, `name`, `kind`, `tags`, `principle`, `scope`, `excludes`, `grades`?, `attribute`,
`grants_competence`?, `crude_fallback`, `stretch`, `emulate`, `acquisition_paths`, `effects`?,
`cost`?, `limits`?, `source`?, `feeds_evidence`? (default true; false for relic-granted licenses, 00.12.1),
`lifecycle`, `basis`. `kind` includes `universal` (held by every character, e.g. `lic.focus.push`).

## conditions.yaml
Owner 06 (owner-block 07 for affliction carriers). Key `conditions`. Every entry conforms to Condition
(00.9.1), whose `diminishing` may carry `group` (one shared counter per target, 06.7.4; amended). All reserved
ids (T-00-15, including the four ch.06 added) must be present.

## conflict.yaml
Owner 06. Keys: `economy` {actions_per_turn, reactions_per_round, action_costs [{what, cost}]},
`range_bands` [{id band.*, meaning, move_cost}], `positional_flags` [{id flag.*, meaning,
effect_refs}], `repeated_attack` {penalties [int]}, `multi_target` [{shape, selection_rule, cap}],
`morale` {thresholds}, `companion_command` {cost, rules}.

## harm.yaml
Owner 07. Keys: `harm_states` [{id harm_state.*, entry, exit}], `dying` {steps 2..4, check},
`wounds` {severity_track}, `reduction_cap` (0..4), `rests` [{id breather|rest_short|rest_long,
restores, interrupted_by, quality_rules}], `lethal_warning` {trigger, writes}, `two_key` {keys}.

## afflictions.yaml
Owner 07 (owner-block 13: regional afflictions; amended at integration). Key `afflictions`. **Affliction**: `id` aff.*, `harm_tags`, `stages` [{stage, condition
cond.*, severity, duration, check {verb, dc_tier}, on_fail, on_success}], `onset`, `cure` [str].

## injuries.yaml
Owner 07. Key `injuries`. **Injury** (wound or mark): `id` inj.*, `severity`, `harm_tags`,
`effects` [effect_ref], `recovery` duration|permanent, `evidence_tags`? [tag].

## last_chance.yaml
Owner 07. Key `options`. **Option**: `id`, `name`, `requires` expr, `outcome` [effect_ref],
`world_writes` [str], `fate_cost`? int, `always_available`? bool.

## base_items.yaml
Owner 08. Key `base_items`. **BaseItem**: `id` bi.*, `item_tags` [item.*], `material_tags`,
`harm` {severity, harm_tags, band_reach [band.*]}? (weapons), `reduction`? {amount, harm_tags}
(armor), `slot_cap` int, `price` int, `weight` int, `lifecycle`.

## item_properties.yaml
Owner 08. Key `properties`. PoolEntry schema (see gen_*.yaml) used by any domain that references it.

## materials.yaml
Owner 08. Key `materials`. **Material**: `id` mat.*, `material_tags`, `source_tags` (creature etc.),
`gates` [tag] (which property families it unlocks in gen.craft), `price`, `rarity_band` band.

## economy.yaml
Owner 08. Keys: `currency` {units}, `price_bands` [..], `lifestyles` [{id, weekly_cost, effects}],
`wages` [..], `carry` {formula from might}, `supply` {units, cost}.

## archetypes.yaml
Owner 09. Key `archetypes`. **Archetype**: `id` arch.*, `creature_tags` [creature.*], `harm_tags`,
`evidence_tags` [tag], `loot` {domain, trophy_base?: item tag, pool_gate_tags [tag]}, `absorbable`
{pool_gate_tags, cannot_absorb [id]}, `behaviors` [behavior id], `lethal_context` bool,
`defeat_disposition` enum, `tells` [str], `signature_property` prop.*. Top-level `powers` [{id `pow.*`, …}]
holds the adversary-only mechanics (09; `pow.` prefix amended at integration).

## adversaries.yaml
Owner 09 (owner-block 13). Key `adversaries`. **Adversary**: `id` adv.*, `archetype`, `threat_band`,
`attributes`, `competence` [{tag, value}], `defenses` (computed or override), `vitality`, `attacks`
[{name, verb, harm {severity, harm_tags}, bands, effects}], `abilities` [ab.*], `reduction`,
`resistances` [effect_ref], `behaviors`, `morale`, `tells`, `lethal_context`, `defeat_disposition`. The 00.3.7
Vitality envelope binds `standard` (and, from below, `minion`) entries; `elite`, `solo` and mob entries exceed it
by 09's multipliers (amended at integration).

## behaviors.yaml
Owner 09. Key `behaviors`. **Behavior**: `id`, `priority_list` [{when expr, do}], `morale_break`
{threshold, then}.

## hazards.yaml
Owner 10 (owner-block 13). Key `hazards`. **Hazard**: `id` haz.*, `terrain_tags`, `harm_tags`,
`severity`, `resist` {verb, dc_tier|effect_dc}, `cadence` (boundary), `conditions` [effect_ref],
`omens` [str], `lethal_context` bool.

## travel.yaml
Owner 10. Keys: `pace` [..], `activities` [{id, duration, verb?, effects}], `watch_check` {die,
results [{range, result}]}, `navigation` {..}, `supply` {..}, `exploration_activities` [{id, duration}].
`encounter_tables` [{id tbl.10.enc.*, terrain, threat_die d20, `threat_by_home` {1..5: [EncounterRow]},
non_threat_die d6, non_threat [EncounterRow]}]; EncounterRow (10.10.1) gains optional `variant`
(minion|standard|elite|solo) and `leader` bool [revision: I-029].

## sites.yaml
Owner 10. Key `site_themes`, `site_domains`. **Theme/Domain**: `id` site.*, `terrain_tags`,
`creature_gate_tags`, `loot_gate_tags`, `features` [..], `dangers` [..], `clock_templates`.
`denizen_pools` [{theme, domain, archetypes [{ref arch.*, weight}], fielded_by_band {1..5: int}}], one per
theme × domain pair, read by PR-10-10 [revision: I-022].

## traps.yaml
Owner 10. Key `traps`. **Trap**: `id` trap.*, `detect` {verb, dc_tier}, `disarm` {license, dc_tier},
`trigger`, `harm` {severity, harm_tags}, `effects`.

## weather.yaml
Owner 10. Keys `regimes` (by season and terrain), `tables` [{id tbl.*, die, results}].

## factions.yaml
Owner 11 (owner-block 13). Key `factions`. **Faction**: `id` fac.*, `org_tags` [org.*], `tier` int,
`hold` enum, `ratings` {..}, `goal` {text, clock clock_template}, `lifecycle_stage`, `linchpins`
[{npc, consequence}], `status_to_pc` −3..+3, `tags`.

## world_turn.yaml
Owner 11. Keys: `steps` [{n, name, handler, rule_id}], `event_tables` [tbl.*], `attention` {..}.

## calendar.yaml
Owner 11 (engine) / owner-block 13 (names). Keys: `year_days: 364`, `seasons` [{id, name}],
`weeks_per_season: 13`, `day_names` [7], `festivals` [{name, season, week, day}]. An owner-block entry is a
**name overlay** (`cal.*`): its nested `seasons`, `quarter_days`, `months` … carry the engine's ids as references
and replace only the names and notes (the engine's ids are never redefined).

## legacy.yaml
Owner 11. Keys: `endings` [..], `settlement` {..}, `inheritance` {..}, `timeskip_options` [..].

## oracles.yaml
Owner 12. Key `tables`. **Table**: `id` tbl.*, `die`, `results` [{range, result, effects?, sub_table?}],
`recency` bool, `context_filters` [tag].

## anchors.yaml
Owner 12 (compiled from every chapter's anchor cards). Key `anchors`. **Anchor**: `rule_id`,
`intent_verbs` [str], `deed_tags` [tag], `situation_tags` [tag], `knobs` [{knob, default,
allowed_deltas}], `degree_table` ref.

## pacing.yaml
Owner 12. Keys: `tension` {min 1, max 9, start 5, rules}, `intensity` {phases}, `lead_injection`
{threshold 3, table}.

## region_*.yaml
Owner 12 (the world seed's output, 12.16) / 13 (`region_thallen.yaml`, an optional pre-made seed) [revision: I-028].
One file per region; the world seed writes one (example: `_process/simulation/12-world-seed-example.yaml`). Keys: `places` [Place], `npcs` [NPC], `factions` (refs or instances),
`clocks` [Clock], `encounter_tables`, `rumor_tables`, `names`, `canon_impossible` [str]. Entities use
00.6.2 shapes. Optional keys (T-13-16; amended at integration): `region`, `canon`, `keepers` (`keeper.*`),
`tongues`, `peoples`, `absent_origins`, `places_of_acceptance`, `fight_locations`, `objects` (`obj.*`),
`bond_placement`, `values`, `situations`, `encounter_table_audit`, `tables`, `terrain_by_ring`, `cases`,
`bestiary`, `storied_items`, `storied_sets`, `stock`, `pregens`, `opening`, `interface_checklist`; and, from the
world seed (12.16): `seed` {procedure, seed, mode, answers [{question, answer, source}], uses_generic},
`calendar` {months, day_names, era, festivals, opening_date}, and a site record's `denizen_table` (PR-10-10).
A region is complete when it passes the seed check (12.16.17, T-12-16) [revision: I-028].

## world_seed.yaml
Owner 12 (12.16). Keys: `modes` [{id, text}], `steps` [{id `ws.step.*`, n, name, rule, questions, writes}],
`questions` [{id `ws.q.*`, step, ask, options [{id, text, …}] | options_from, oracle {die, table | results |
from/map, by?}}], `tables` [{id `tbl.12.seed.*`, die?, results | by_people | by | climates …}], `defaults`
{canon_impossible [{key, text, scope}], sources, components_by_band, rare_metals, haven_by_tier, market_by_terrain,
sentry_floors, areas_per_ring, watches_between, uses_generic}, `requirements` [{id `ws.req.*`, from, need, rules,
key (a path, `/`-separated), check, generic?}] [revision: I-028].

## codex.yaml
Owner 14. Keys: `views` [{id, shows [state family], class_filter [visibility class], layout}],
`offer_marker` {text}, `preferences` {the closed `pref.*` keys of T-14-1: tone, lethality.acknowledged, death.mode,
safety.lines, safety.veils, safety.flags, pacing.profile, auto_commit, pillars, player.new_to_this, creation.path,
shown_notes} [editor: E2-057].

## social.yaml
Owner 15. Keys: `standing_effects` [{standing, dc_mod, behavior}], `claim_plausibility` [..],
`refusal_rules` [..], `negotiation` {..}.

## investigation.yaml
Owner 15. Keys: `clue_graph_template` {nodes [{id, sealed_fact, placements (≥3), prerequisites}]},
`delivery` {..}. Optional `cases` [{id `case.*`, …}]: concrete case graphs (15's and a region's; chapter 13's
Thallen Vale's three were moved here at integration).

## downtime.yaml
Owner 15. Key `activities`. **Activity**: `id` (`dt.*`), `duration`, `verb`?, `clock`? clock_template,
`costs`, `effects`.

## companions.yaml
Owner 16. Key `companions`. **Companion**: `id` (`cmp.*`), `template` (adversary-like stat block at band),
`loyalty` {standing, clock}, `command_actions` [..], `journey_roles` [..], `harm_rules` (07 variant),
`wage`. These required keys are kept; every other top-level key (knacks `kn.*`, loyalty tables, record fields …)
is optional and documented in T-16-1 … T-16-22 (amended at integration).
