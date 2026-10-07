
---

## Tables

`data/origins.yaml`, `data/gen_birth.yaml` and `data/kits.yaml` are canonical for every id and number
(00.1.4 item 5). The tables below are rendered from those files by the scratchpad script `tables02.py`
(T-02-2 to T-02-10, T-02-13) or computed by `gen02.py` (T-02-3, T-02-11, T-02-15), so they cannot drift
from the data. Tables embedded in Rules are indexed here: the arrays (02.3.1), the Typical placements
(02.3.2), the upbringing budget (02.4.4), the profiles (02.5.2), the magic livelihoods (02.5.5), the
layers of birth (02.6.1), bond kinds (02.9.2), faction-tie brackets (02.9.5), preferences (02.10.1).

**T-02-1 What a new character has: the numbers other chapters read.**

| Quantity | Value at creation | Rule | Read by |
|---|---|---|---|
| Attribute values; sum | each −1…+3; **+5** (Free) or **+7** (Typical); one −1 always; at most one +3 | 02.3.1 | 01, 06, 07, 09 |
| Competence floor | **+1** at `deed` (confirmed) | 02.5.1 | 01, 03, 04 |
| Origin competence | **+2**, on at most **two** level-2 deed tags | 02.5.2 | 01, 04 (tier 1 is +3 or +2) |
| Best check modifier | +5 (attribute +3, deep +2); **+6** only with a knack on that tag | 02.6.2 | 00.3.7 band 1 (+4…+6) |
| Training licenses held | 2 to 11, all at grade `trained` | 02.5.3 | 05, 12 (facets) |
| Abilities held | 0, or **1** at rank 1 in the acquired partition | 02.5.4 | 05 |
| Vitality | **12 + Endurance** = 11…15 (base; 10…16 over a lifetime) | 02.7.1 | 06, 07, 09 |
| Focus base | **3, 4 or 5** by upbringing; never changes | 02.7.2 | 05 |
| fate | **1** | 02.7.3 | 01, 07 |
| Power band | 1 | 04 | 09 |
| Dread; threshold | 0; 8 + Resolve = 7…11 | 07.11 | 07 |
| Guard | 10 + Agility + (1 or 2) + (1 with a shield) = **10…16** | 06.4.1 | 06, 09 |
| Edge from birth | +1 on one level-2 deed tag (the knack) | 02.6.2 | 01 (edge cap +2), 08 (item edges share the cap) |
| Bonds; faction ties | 1 or 2 NPCs at set standing; ties +1, or +2 and −2 | 02.9.2, 02.9.5 | 11, 12, 15 |
| Hooks seeded | 5 to 8 | 02.9.7 | 11 |
| Coin | 3 to 55 | 02.8.2 | 08 |
| The Bent | +1 to one attribute, offered after creation, never above +3 | 02.6.5 | 00.4.3 a, 07 (Vitality) |

**T-02-2 Peoples.** (`origins.yaml`, `kind: people`; gifts in `contrib/licenses.02.yaml`)

{{T-02-2}}

Every people also carries two hooks and its `creature.folk.*` tag. A non-human may take the Free rule
(02.3.4) and keeps everything in this table except the "must hold" and "fixed" columns.

**T-02-3 The quantity-against-freedom audit.** For sixteen classic concepts, the best weighted
attribute score attainable under the Free rule and under each people's Typical rule (any shape). The
weights model a solo character: every attribute is worth 1 (one person meets every kind of check); the
four that feed a defense or a pool (Agility, Endurance, Wits, Resolve) are worth 1 more; a concept adds
4, 3 and 2 to its first, second and third attribute. **Bold** beats Free; *italic* trails it.

{{T-02-3}}

Reading: every people's Typical rule is better than Free for some concepts and worse for others; none
is best everywhere; the mean premium for accepting three decided placements is about one point, which
is what the human's extra training is set against. Giant-kin are the extreme case: five points better
than Free as a warrior, brawler, smith or knight, and worse at everything that needs quick wits, so a
giant-kin with another calling in mind takes 02.3.4. The audit is a design check, not a rule: no
number in it is used in play.

**T-02-4 Upbringings.** (`origins.yaml`, `kind: upbringing`; packs in `kits.yaml`)

{{T-02-4}}

Each row spends exactly three units (02.4.4). Each also carries an anchor seed, a thorn seed and two
hooks.

**T-02-5 Livelihoods.** (`origins.yaml`, `kind: livelihood`; kits in `kits.yaml`)

{{T-02-5}}

Level-2 deed tags per branch, for reference: {{branch_counts}} (81 in all). Every one appears on at
least one livelihood list or upbringing; any may be the off-list pick (magic schools excepted).

**T-02-6 Default attribute placements** (02.3.5; Peaked shape; humans under the Free rule, the others
under their Typical rule). Each cell lists Might, Agility, Endurance, Wits, Intellect, Presence,
Resolve, in that order.

{{T-02-6}}

**T-02-7 The seven gifts of the Touched.** (`gen_birth.yaml`, layer `gift`)

{{T-02-7}}

**T-02-8 Birth quirks.** (`gen_birth.yaml`, layer `quirk`; total weight 40. A lever granted by a trait
is an ordinary lever: it cites the quirk as its fact, counts toward the two-lever limit, and applies
only when its stated circumstance is recorded in the scene.)

{{T-02-8}}

**T-02-9 Knack pools.** The knack is drawn among the level-2 deed tags of the branches in the
character's birth pool, each at weight 2.

{{T-02-9}}

Over all 1,512 combinations of people, upbringing and livelihood the pool holds 15 to 52 knacks (median
35): never so few that the result is predictable.

**T-02-10 The Bent's pool gate.** (`gen_birth.yaml`, layer `bent`)

{{T-02-10}}

{{T-02-10b}}

**T-02-11 The Bent: what deferring is worth.** `n` = attributes in the pool at the first draw
(equal weights; a declined attribute is struck; the pool is assumed not to grow between draws).

| n | The one you want comes on the first draw | You defer until it comes (at most twice): you get it | …and you end with no Bent | Either of two you would be glad of, by the same policy |
|---|---|---|---|---|
| 2 | 50% | 100% | 0% | 100% |
| 3 | 33% | 100% | 0% | 100% |
| 4 | 25% | 75% | 25% | 100% |
| 5 | 20% | 60% | 40% | 90% |
| 6 | 17% | 50% | 50% | 80% |

A character whose work is narrow (two or three attributes in the pool) can have the Bent they want for
the price of waiting; one whose work is wide is offered more and risks more. Working in a new branch
before the next draw adds its attributes to the pool: it widens the choice and lowers each chance.

**T-02-12 Archetype coverage.** Each of chapter 04's twenty-five iconic archetypes (04.2.7) as a
creation recipe that makes it pursuable from the first scene. A recipe is a suggestion; recognition
still comes only from deeds.

| Archetype (04's calling) | Livelihood; profile and picks | Notes |
|---|---|---|
| Fighter (Warrior) | Soldier; Focused: blade + shield | any people; Orc-kin and Giant-kin Typical excel |
| Ranger | Hunter; Focused: archery + tracking | Wren (WE-02-1) |
| Rogue (Thief, Shadow) | Thief; Focused: thievery + stealth | Street-raised adds streetwise and the Cant |
| Bard | Performer; Focused or Gifted (*Stirring Song*) | Road-raised |
| Cleric (Priest, Healer) | Acolyte; Gifted: healing + *Mend Flesh* | Cloister-raised: Focus 5 |
| Paladin | Acolyte; Gifted: smiting + *Smite*; off-list access pick blade or shield; or Rider with the aspiration [divine.oaths] | the oath itself is chapter 04's offer |
| Druid | Hedge-taught; Gifted: growth + *Root Snare* | Wilds-raised |
| Wizard | Apprentice; Gifted: a school + its spell | Cloister-raised |
| Sorcerer (Elementalist) | Touched, the spark (`birth.gift.elements`) | innate; no teacher needed |
| Warlock (Pactbound) | Acolyte; Gifted: pact + *Patron's Brand*; the keeper is a patron | the calling is offered by V13 in play |
| Monk | Laborer; Focused: unarmed + athletics; Cloister-raised; a creed on `conduct.restraint` | |
| Barbarian (Berserker) | Soldier or Laborer; Focused: axe + athletics; Wilds-raised | the primal half is found in play (a place's acceptance) |
| Necromancer | Apprentice; Gifted: necromancy + *Wither* | |
| Artificer | Tinker; Focused: artifice + alchemy | the arcane half is learned in play |
| Alchemist | Tinker; Gifted: alchemy + *Quick Tincture* | |
| Merchant-prince | Merchant; Focused: trade + persuasion | Guild-quarter raised; the *prince* is rank and holdings (11) |
| Scholar | Scholar; Rounded or Broad; lore picks from Intellect | |
| Knight (Cavalier) | Rider; Focused: mounted + blade; Court-raised | knighthood is a rank (11); an aspiration names it |
| Witch (Hexer) | Hedge-taught; Gifted: hexcraft + *Evil Eye*; or Touched (the eye) | |
| Shaman (Spirit-talker) | Hedge-taught or Touched; spirits + *Spirit Tongue* | |
| Assassin, Spy | Thief; Focused: stealth + ambush (off-list) / Charlatan; Focused: deception + disguise | |
| Healer, mundane (Physician) | Healer; Focused: medicine + foraging, or Gifted (*Field Surgeon*) | |
| Monster-hunter (Slayer) | Hunter; Rounded: tracking deep, archery and bestiary (off-list) as access | |
| Captain | Soldier; Focused: tactics + command | Road-raised |
| Smith and the trades (Artisan) | Artisan; Focused: the craft + trade, or Gifted (*Keen Edge* and its kin) | Village- or Guild-quarter raised |

**T-02-13 Fate's hand.** (`origins.yaml#tables`; rolled only when the player asks for chance, 02.2.2)

{{T-02-13}}

**T-02-14 Optional data fields this chapter adds** (allowed by `data/SCHEMAS.md`: owners may add
optional fields and document them here).

| File | Field | Type | Meaning |
|---|---|---|---|
| origins.yaml | `kind` | people \| upbringing \| livelihood | which of the three origins the entry is |
| | `attribute_rules.floors`, `.shapes`, `.uncommon_of_kind` | map; map; rule | Typical minimums; the arrays allowed; the Free rule a non-human may take (02.3.4) |
| | `extra_access_trainings`, `language_picks`, `license_choice` | rule; int; {pick, of} | the human's training; tongues to pick; a choice among licenses |
| | `focus_base`, `wealth`, `coin`, `budget_units` | int; enum; int; int | upbringing values (02.4.4) |
| | `kit_id` | kit id | the kit in kits.yaml that `kit` copies |
| | `trainings`, `magic`, `grants`, `defaults`, `technique_suggestions` | lists and maps | livelihood content (02.4.5, 02.5) |
| | `org_tags`, `bond_seeds`, `drive_seeds`, `aspiration_seeds` | lists | seeds for C8 |
| | `birth_circumstance` | circumstance id | forces the manner (Bound service: hard; Touched: gifted) |
| | `backstory` | [tag] | declared, always empty (02.11.1) |
| | top level: `profiles`, `creation_defaults`, `bond_kinds`, `faction_tie_brackets`, `tables`, `concept_branches`, `attribute_shapes`, `upbringing_budget` | | the closed lists of 02.5.2, 02.2.2, 02.9.2, 02.9.5, 02.2.2, 02.2.4, 02.3.1, 02.4.4 |
| gen_birth.yaml | `layer` (= `mod_group`) | knack \| trait \| gift \| bent | which slot kind an entry fills |
| | `quality_rungs[].magnitude_layers`, `.signature_layer` | lists | which layer each slot draws from |
| | `text`, `competence`, `gifted_ability`, `attribute`, `excluded_when` | | player-facing text; a gift's +2; a gift's working; a Bent's attribute; a Bent's exclusion |
| | top level: `bent`, `bias_rule`, `allows_degree_none` | | 02.6.5–02.6.7; 02.6.4; 00.11.2 |
| kits.yaml | `note`; `choices` | str; [{pick, options}] | narration seed for the resolved item; the kit choice |

**T-02-15 What the starting numbers mean** (success or better, exhaustive d20 with chapter 01's
one-step rule; reference ladder).

| A new character who is… | Modifier | Easy 10 | Moderate 15 | Hard 20 | Very hard 25 |
|---|---|---|---|---|---|
| at their forced low, untrained (attribute −1, floor) | 0 | 55% | 30% | 5% | 5% |
| ordinary and untrained (attribute 0, floor) | +1 | 60% | 35% | 10% | 5% |
| capable, holding the training as access (attribute +2, floor) | +3 | 70% | 45% | 20% | 5% |
| capable, holding it deep (attribute +2, +2) | +4 | 75% | 50% | 25% | 5% |
| a specialist (attribute +3, +2) | +5 | 80% | 55% | 30% | 5% |
| a specialist with a knack on the tag (+3, +2, +1) | +6 | 85% | 60% | 35% | 10% |

The +1 and +5 rows are 00.3.17's calibration lines CT-1 to CT-4 for an untrained PC and a band-1
specialist, unchanged: this chapter's numbers sit on the ladder chapter 00 calibrated. A training held
as access changes none of these numbers for its holder; it changes which attempts are legal at all
(a Hard lock is G2 for the access holder and G3 for everyone else).
