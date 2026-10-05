# 08 — Items, Loot, and Crafting

> This chapter governs every thing a character can own: what an item is in state, the base items of every
> `item.*` branch, what properties items may carry and what they may never do, how a defeated foe, a found
> cache or a patron produces an item (the loot and gift domains of 00.11's one generator), how a character
> makes, mends, breaks down and enchants things (the craft domain), which active abilities items hold and
> how relics lend off-identity capability, how items are identified, equipped and attuned, and the whole
> economy around them: coin, prices, haggling, selling, lifestyles, services, wages, holdings, carrying
> capacity, supply, light, mounts and vessels. It is shaped by one decision the constitution left open and
> two dangers the research names. The decision: *what does a dropped item grant?* (P5) — answered here as
> exactly four kinds of property (mundane, passive, license, item-bound active), at most one active per
> item, relics that license off-identity capability at a Focus surcharge and never feed calling tiers. The
> dangers: gear that out-scales who a character is (the Mythcreants "gear balance" antipattern, R1 08) and
> magic that mints wealth (5e's *Fabricate*, R2 08). Both are closed by numbers, not exhortation: every
> capped modifier family has an **item share** smaller than its cap, so callings always own the larger part
> of a character's power, and every coin enters the world through a table, never through a spell or a
> narrator's generosity. The DM's part is classification — the circumstance of a win, the resemblance of an
> improvised weapon, whether a gift is earned — and the engine computes everything else.

---

## Design intent

**Goals served.** Goal 1 (the player feels free to try any idea): any object can be a weapon, a lever, a
material or a trade good; any monster's body can become gear; any relic can lend a capability the
character's calling does not have; any found thing can be identified, sold, broken down or made into
something else. Goal 2 (the AI responds correctly): every item number lives in `data/`; every drop is
`generate()`'s output, which the DM names and never embellishes; every price is a table lookup; every
property is an effect reference that composes through 00.10's substrate at zero authoring cost
[BRIEF §3; C:P5; 00.11].

**What this chapter adopts, and from where.**
- **One generator, three configurations** (`gen.loot`, `gen.craft`, `gen.gift`) plus `gen.item_ability`
  for the ability an item holds. The source (a creature's nature, a material, a giver) gates a bounded
  pool; the manner (decisive, costly, merciful, scavenged; crafted, commissioned, improvised; earned,
  favored, bargained) picks the fill; the band sets the tier cap [C:P5 sixth pass; R3 08.1–08.3, 08.11;
  00.11; R: src/ability_pool.py (shape kept, content replaced)].
- **Identity separated from magnitude** (Diablo III's reserved Legendary slot, Borderlands' manufacturer
  pools): every item rung has a fixed number of **signature** and **magnitude** slots; the signature is
  what makes a drop recognizably "troll-work" [R3 08.2, 08.7, A-4, A-24].
- **Bound the count, not the table**: 210 properties in `data/item_properties.yaml`, but never more than
  three on one item, and fixed counts per rung (PoE2's fixed four) [R3 08.9, 08.13, A-21].
- **The source's band plays item level** (Diablo II's affix-level gate): a T2 wolf cannot drop a tier-4
  property [R3 08.4, A-2].
- **Crafting is the second pool-gate domain**: the material gates (troll hide gates regeneration and
  crush-proofing), the maker's manner fills, and type-tier × quality-tier comes from The Land's alchemy
  ladders [R2 #13; R3 08.11; C:P5 "crafting MUST NOT be assumed to need its own bespoke two-axis design"].
- **Kills feed crafts** (Monster Hunter's carve-and-craft loop): every resolved defeat yields materials
  even when no property item drops, and a harvested part carries its source's signature into whatever is
  made from it [R: https://en.wikipedia.org/wiki/Monster_Hunter_Wilds].
- **Relics license off-identity capability at a premium** (Stormlight's Honorblades): borrowed power costs
  +1 Focus and never grows [R2 #9; 05.6.3].
- **An explicit item budget** (the Alexandrian's Iron Man Principle: if magic items exist and matter,
  there must be rules for how many) [R2 08; R1 08 "item density is a balance assumption"].
- **Inventory as a small, legible budget** (Mausritter's paw/body/pack slots and usage, Cairn's ten
  slots): load units against a capacity derived from Might, the one value 00.4.4 lets Might feed
  [R: https://en.wikipedia.org/wiki/Mausritter; R: https://loottheroom.uk/the-long-read-mausritter;
  R: https://cairnrpg.com/; R5 EQ-02].
- **Lifestyle as an upkeep that matters** (Blades' stash-to-lifestyle quality; Torchbearer's lifestyle
  cost in town) [R: https://bladesinthedark.com/coin-stash; R5 EQ-05; R5 P-13].
- **Making is materials + tools + time + license** (Forbidden Lands: crafting needs raw materials, usually
  tools and often considerable time) [R: http://forbiddenlandswiki.com/index.php?title=Trade_Goods;
  R: https://forbiddenlandsopentable.obsidianportal.com/wikis/gear].

**What this chapter deliberately avoids.**
- *The DM deciding what drops.* Diablo III's "completely random" launch loot and Borderlands' cross-mixed
  parts were both corrected toward gated structure; this chapter starts there [R3 08.8, A-7].
- *Smart loot.* The generator never looks at the recipient's callings (00.11.4). Relevance comes from
  where the player hunts, what they make, and the `chosen` fills of mercy, commissions and gifts [R3 T-9].
- *Items that change who a character is.* Items never change attributes, competence, maxima of Vitality or
  Focus, actions per turn, or ability slots (08.2.1). Those are 02's, 04's and 05's.
- *Percentages and rolled ranges.* Every property value is fixed per tier; every price is an integer from a
  band table; anything cheaper than one coin is sold by the lot (SG-23).
- *Deleting what players love.* An item with a signature or a bound ability is never destroyed by a cost;
  lost gear goes to a cache somewhere the player can go (07.6.4).

---

## Rules

Rule ids are `08.S.R`. Kinds per 00.2.2. Data files are canonical for every id and number (00.1.4 item 5):
`data/base_items.yaml`, `data/item_properties.yaml`, `data/materials.yaml`, `data/economy.yaml`,
`data/gen_loot.yaml`, `data/gen_craft.yaml`, `data/gen_gift.yaml`, `data/gen_item_ability.yaml`, and the
fragments `data/contrib/{effects,licenses,boundaries,tags}.08.yaml`. All are generated and validated by
`rules/_process/simulation/08-gen_data08.py`.

### 08.1 Items: the schema, base items and quality

**08.1.1 The item record.** `[D]` Every item is an entity (00.6.1) whose record extends 00.6.2's `Item`.
The fields below are the complete shape; 00.6.2's six fields keep their names and meanings.

```yaml
Item (extends Entity; owner 08):
  base: bi.*                     # base item (data/base_items.yaml)
  quality: worn | common | fine | masterwork | wondrous | storied     # 08.1.4
  quality_index: 1..6            # the rung's index; 03's cnt.made reads it (lowest = 1)
  material: [mat.* | material.* tag]          # primary first; harvested parts keep their provenance
  signature: [Property]          # 0..1, the identity layer (00.11)
  properties: [Property]         # magnitude layer, 0..2
  worked: Property | null        # the ONE property added after making (enchanting, a crafter's addition; 08.6.10)
  flaw: Flaw | null              # from item_properties.yaml#flaws (Flawed results, cursed finds)
  sealed_properties: [prop_id]   # unidentified; sealed state (00.6.5), unsealed by 08.5.3
  bound_ability: {ability_id: ab.*, rank: 1..3} | null    # at most one (00.11.5; 05.2.8)
  relic: bool                    # derived: true when bound_ability or a license property is present
  feeds_evidence: bool           # false whenever relic is true (00.11.5; 04 request 11)
  cost_immune: bool              # true while a relic or storied item is attuned (01.13.4; 06.5.4)
  equipped: bool                 # 00.6.2
  slot: body slot id | null      # where it is worn or held (08.5.1)
  attuned: bool                  # 08.5.2
  condition: intact | damaged | broken | serviceable_until_rest_long     # 08.1.9
  uses: {current: int, max: int} | null         # kits, consumables, charges
  quantity: int | null           # stacked goods: arrows, torches, supply lots
  loaded: bool | null            # loading weapons (06.4.9)
  load: int                      # load units (08.9.1), computed from base and properties
  provenance: {domain: gen.loot | gen.craft | gen.gift | kit | bought | found,
               source_id: id | null, source_tags: [tag], circumstance: str | null, degree: str | null,
               rung: str, maker: id | null, made_at: time | null, place: place_id | null, tier_cap: int}
  facts: [fact_id]               # teaches:, kept_since:, made_by_holder:, gifted_by:, conjured:, recognizable_as:
  price: int                     # list price, computed (08.8.3)
Property: {prop_id: prop.*, tier: 1..6, effects: [effect_ref]}    # 00.6.2, unchanged
```

`provenance.maker` and `provenance.domain: gen.craft` are what 03's `cnt.made` counter reads; the quality
index is its weight (03 Interface request). Every field is written by a tool; narration restates only
what the record holds (INV-2) [R1 08 "items with states carry explicit state fields"; 00.6.2].

**08.1.2 Base items.** `[D]` A base item (`bi.*`, `data/base_items.yaml`) fixes everything about an item
that does not come from its quality or properties: its `item_tags` (the most specific level-3 tag first,
per 03's request, so 03.1.6 can ground evidence in it), its `material_tags`, its kind, its **price** in
coins at quality `common`, its **load** (`weight` in the schema) in load units, its `slot_cap` (the most
properties it can hold), its body slot, its `make` (the training license, deed tag and time per tick that
crafting it uses), and the kind-specific fields of 08.1.5–08.1.8. There are **185** base items covering
every level-2 branch of `item.*`. Base items are content; adding one is a data entry with a DL line, never
a rule change [R3 00.1; 00.16.4].

**08.1.3 The four kinds of property.** `[D]` Every property in `data/item_properties.yaml` declares
`kind`, and the kind fixes when it works:

| Kind | What it is | Works when | Takes an ability slot? | Examples |
|---|---|---|---|---|
| **mundane** | a property of make: magnitude only (an edge, a harm edge, a reduction, carry, a snag waived, durability) | the item is **equipped** (worn, wielded or in hand); no attunement | no | Keen, Balanced, Sturdy, Quiet, Warm |
| **passive** | a magical effect: additive or triggered | the item is **equipped and attuned** (08.5.2) | no | Ember-warded, Rending, Darksight, Hunter's sense |
| **license** | lets the bearer attempt what a named license permits, with no competence | equipped and attuned | no | Lock-whisper (thievery at trained), Stone-sense |
| **item_ability** | one active ability (`ab.*`) the item holds | equipped, attuned and **bound** to an equipped slot (05.2.8) | yes: one `equipped` slot | a fang that lets the bearer Pounce |

This is the whole answer to "what does an item grant" at the level of kind; 08.4 is the rest
[00.11.5; C:P5 "passive ... or active"; R3 08.10].

**08.1.4 The quality ladder.** `[D]` Every item has exactly one quality rung. The rung fixes its slot
counts (00.11.3 step 3), its price multiplier, and its index for 03's `cnt.made`.

| Index | Rung | Signature slots | Magnitude slots | Price (× base) | Meaning |
|---|---|---|---|---|---|
| 1 | **worn** | 0 | 0 | ×½ (minimum 1) | below standard; **fragile**: a `cost.gear` against it is taken one severity rung heavier |
| 2 | **common** | 0 | 0 | ×1 | standard, serviceable work |
| 3 | **fine** | 0 | 1 | ×3 | better make; its one magnitude slot is **open** (empty) unless a generator or a crafter fills it; a fine garment or jewel is a citable status fact |
| 4 | **masterwork** | 1 | 1 | ×10 | a master's work or a true trophy: the identity layer opens |
| 5 | **wondrous** | 1 | 2 | ×30 | the best that hands, hoards and powers produce |
| 6 | **storied** | 1 | 2 | authored | a named, hand-authored item: a fixed property set, exempt from mod groups, never exempt from the item share (08.2) or the slot cap; never generated |

Slot counts are clamped to the base item's `slot_cap` (a garment's cap is 2, so a wondrous cloak has one
signature and one magnitude slot). Chapter 02's assumed names map exactly: `worn` < `common` < `fine` are
rungs 1–3 of this ladder; 02.8.2's "nothing above fine, nothing from a generator pool" means a kit's `fine`
item arrives with its slot **open** (02 Interface request; DL-08-03) [R3 08.9; R2 08 "rarity specializes";
00.11.3].

**08.1.5 Weapons.** `[D]` Every weapon is built on chapter 06's **T-06-6** (weight → base severity,
Strike cost, hands, bands) and **T-06-7** (at most two of twelve properties). This chapter's assumed table,
stated so the interface is checkable, is 06's exactly: unarmed S1 (1 action); light and one-handed S2 (1
action); heavy S3 (2 actions); bows S2 (1 action; longbow reaches `band.far` with no snag); light crossbow
S2 (reload 1), heavy crossbow S3 (reload 2). Base severity is raised by the wielder's **mastery** (06.4.5:
expert +1 rung, master +2), which lives at E1 outside the ±2 effect-step cap; item harm edge sits inside
the +2 harm-edge cap and inside the item share of +1 (08.2.2). The roster:

| Weight | Base items (weapon properties) |
|---|---|
| light | knife (close_quarters, concealable) · dagger (finesse, thrown) · short sword (finesse, parrying) · hand axe (thrown) · club · sap (concealable, close_quarters) · whip (reach, entangling) · darts ×5 (thrown, concealable) · throwing knives ×3 (thrown, concealable) · net, bolas (thrown, entangling) |
| one-handed | arming sword (versatile, parrying) · rapier (finesse, parrying) · battle axe (versatile) · mace (armor_breaking) · war hammer (armor_breaking, versatile) · flail (armor_breaking, close_quarters) · spear (reach, thrown) · quarterstaff (versatile, parrying) · javelin (thrown) |
| heavy | greatsword (parrying) · great axe (reach) · maul (armor_breaking) · pike (reach) · halberd (reach, armor_breaking) · lance (reach; 1 action from the saddle with `lic.training.martial_mounted`) |
| bow | shortbow · longbow · sling (one hand) |
| crossbow | light crossbow (loading) · heavy crossbow (loading, armor_breaking) |

Each weapon names its **deed tag** (the primary tag of its Strike, 00.5.6) and the **training license**
whose grade sets mastery (`lic.training.martial_<child>`). Ammunition (arrows, bolts, sling bullets) is a
quantity of 20 per lot; half of what is spent is recovered after a conflict (06.4.9). *Interface flag:* if
06 retunes T-06-6 or T-06-7, `base_items.yaml` is regenerated from the same script; no rule text here
changes [06 Interface request to 08; DL-08-04].

**08.1.6 Armor.** `[D]` Worn armor reduces `harm.physical` from attacks and shaped effects by **light 1,
medium 2, heavy 3** (07.2.2; T-06-11); total reduction from all sources is capped at 4 by chapter 07, and
items' share of it is 3 (08.2.2). Armor pays for its reduction in the other pillars, each a data field:

| Armor | Kind | Price | Load worn / carried | Snags (engine-cited Precision snags) | Don | Sleeping in it |
|---|---|---|---|---|---|---|
| padded jack | light | 5 | 1 / 2 | — | 1 interval | no effect |
| leather | light | 10 | 1 / 2 | — | 1 interval | no effect |
| hide coat | light | 8 | 1 / 2 | Swim | 1 interval | no effect |
| brigandine | medium | 60 | 2 / 4 | Swim | 1 interval | long rest at best partial (07.8) |
| mail hauberk | medium | 50 | 2 / 4 | Sneak, Swim | 1 interval | partial |
| scale coat | medium | 45 | 2 / 4 | Sneak, Swim | 1 interval | partial |
| splint | heavy | 200 | 3 / 6 | Sneak, Swim, Exert | 2 intervals | partial |
| plate | heavy | 400 | 3 / 6 | Sneak, Swim | 3 intervals alone, 1 with help | partial |

The snags are the armor's **intrinsic** costs, cited by the engine as the fact `armor.<item>` (outside
the two-cited count, inside the ±4 cap, like 06's repetition snags); the mundane properties *Quiet* and
*Supple* waive them (`eff.05.waive`). A helm is a garment, not armor: it carries no reduction and is the
base for head-slot properties [07 Interface request to 08; 06 "armor carries its costs in other pillars"].

**08.1.7 Shields.** `[D]` A shield gives **+1 edge to Guard** (T-06-7 `shield_light` / `shield_heavy`) and
**reduces nothing** (07.2.2). Four base items: **buckler** (light; load 0; does not grant Full defense's
cover; the shield hand may also hold a lit torch or a light item, not a weapon), **round shield** (light;
grants Full defense's cover), **kite shield** (heavy; usable mounted; Exert and Sneak take a snag),
**tower shield** (heavy; not usable mounted; while its bearer Defends and does not Move it is a cover
feature for one ally engaged with the bearer). A shield bash is an unarmed-weight Strike (S1) under
`deed.martial.shield.bash`. Because a shield already fills the item share of Guard edge (+1), a Guarding
property never generates on a shield or alongside a parrying weapon (08.2.4).

**08.1.8 The other branches.** `[D]` (Every entry in `base_items.yaml`; the table is the summary.)

| Branch | Base items | What the base does on its own |
|---|---|---|
| `item.garment` | plain, working, fine and courtly clothes; winter furs; desert robes; cloak; oilskin cloak; boots; soft shoes; gloves; riding gauntlets; hood; hat; helm | clothes carry a **status** (plain / fine / noble) that is a citable fact where station matters; winter furs and desert robes carry an **intrinsic** hazard step (cold / heat one rung lower); the oilskin waives the rain snag |
| `item.jewelry` | ring, signet ring, amulet, torc, charm, circlet | nothing mundane but status; a signet is a citable seal; charms are the default trophy base (a fang, a scale, a feather on a thong) |
| `item.tool.kit` | thieves' tools, healer's kit (10 uses), climbing kit, rope, disguise kit (5), forgery kit (5) | each grants a **Precision lever** for its named beats, and its absence makes some licensed beats improvised (+5 DC) |
| `item.tool.instrument` | lute, flute, drum, horn | required for an instrumental performance |
| `item.tool.implement` | wand, casting staff (also a quarterstaff), orb, holy symbol, totem | the **sign** of 05.7.4 when it bears the keeper's mark; the **vessel** of 05.6.12 when kept a season or made by the holder (08.4.7) |
| `item.tool.trade` | smith's, woodworker's, leatherworker's, weaver's, alchemist's, cook's, mason's, tinker's, jeweler's, enchanter's tools; writing case; tools of the work; crowbar, grappling hook, shovel, manacles, spyglass, mirror, tent, fishing gear | trade tools give the Precision lever every licensed crafting beat needs (08.6.4); the others each name their lever |
| `item.tool.light` | torches ×5, lantern, candles ×10, tinderbox | light and burn time (08.9.5) |
| `item.tool.container` | backpack, belt pouch, satchel, sack, waterskin, strongbox, scroll case, bedroll and cook-pot | holds; a bedroll makes a camp a camp rest site, not rough (07.8) |
| `item.consumable` | healing draughts, clarity draught (Focus), elixirs, toxins, trail rations, scrolls, lamp oil, firepot, smoke pot, weapon oils (rime, ember, silvering, holy water), whetstone, bandages, antidotes and four specific remedies, salve | their `effects`, used up per use; oils claim `slot.strike_delivery` at rank **20** (05.10.3's 20–24 band) |
| `item.goods` | trade goods (salt, grain, cloth, ore, timber, spices, wine, furs, dyes, working stock), treasure (gems at 10 / 100 / 1,000, art objects at 50 / 500, a silver trade bar of 50), documents (letter, map, ledger, book, spellbook, manual, pattern book, charter) | value, and for documents the facts they carry (`teaches:`, title) |
| `item.conveyance` | donkey, pony, mule, riding horse, draft horse, courser, destrier; saddle and tack; light and heavy barding; handcart, cart, wagon, sledge, carriage; raft, rowboat, keelboat, river barge, sailing cog | carry capacity, pace, upkeep, crew (08.10) |

**08.1.9 Condition: intact, damaged, broken, destroyed.** `[D]` Chapter 01's `cost.gear` writes an item's
`condition` (01.13.4); this rule fixes what each value means (01 and 05 Interface requests):

| Condition | Written by | What still works | What stops | Mended by |
|---|---|---|---|---|
| **intact** | default | everything | — | — |
| **damaged** | `cost.gear` S3; `ab.sunder` rank 1; a failed crafting step on the item | the base item's weight, severity, bands and Strike; its signature, passive, license and bound ability | its **edge, harm-edge and reduction** — the mundane magnitude properties, the T-06-7 edge and harm-edge properties (versatile, parrying, shield), and **one point** of a worn armor's base reduction (heavy 3 → 2 …) | a crude repair (`verb.handle`, Easy, 1 interval: *serviceable until the next* `rest_long`, then damaged again) or a lasting repair (08.6.7) |
| **broken** | `cost.gear` S4; `ab.sunder` rank 2 | nothing but its value as salvage | the item does not function at all; a bound ability unbinds; a relic's license and passives are dormant | a licensed repair only (08.6.7); never by Handle |
| **destroyed** | `cost.gear` S5 | — | it is gone (`exists = destroyed`) | — |

An item that carries a **signature or a bound ability is never destroyed** by a cost: an S5 `cost.gear`
against it takes 01.13.4's other S5 form, *location sealed as unknown* (swept away, lost in the flood),
and the engine writes a rumor of where it fetched up (11), so it can be found again (07.6.4's principle).
A **worn** item takes every `cost.gear` one rung heavier (S2 → damaged); a **Sturdy** or dwarf-made item
one rung lighter (08.2.3) [01.13.4; 07.6.4; R1 08 object state].

**08.1.10 `cost_immune`.** `[D]` An item is `cost_immune: true` while it is a **relic or a storied item
and attuned** to its bearer. `cost.gear` may not target it (01.13.4), no ability breaks it (`ab.sunder`'s
excludes), and it cannot be disarmed (06.5.4). It can still be taken from a defeated, robbed or captured
bearer (07.6.4's caches): immunity protects against attrition, not theft. *Why:* a bound relic is a
character's identity piece; losing it to a near-miss die roll is the "losing gear hurts more than the
numbers suggest" failure (R1 07), while losing it to a captor is a story with a way back [01 Interface
request; DL-08-05].

**08.1.11 Improvised weapons and objects.**

```
### 08.1.11  Improvised weapon: strike with what is at hand        [J:enum] [D]
Trigger [T]:        a Strike, throw or block declared with an object that is not a weapon base item
Loads in:           situation.conflict
License check:      basic verb: verb.strike (G1); an improvised weapon is always legal
Decisions (J):      1. RESEMBLANCE [J:enum] Which weapon does the object most resemble in how it is used?
                       options: a base weapon of 08.1.5 (true only when the object is used the same way
                       and is about that weapon's size: a chair leg -> club; a pitchfork -> spear; a
                       wood-axe -> battle axe; a smith's hammer -> war hammer; a broken bottle -> knife) |
                       none (false for every object with no weapon of similar use and size: a lantern,
                       a book, a cooking pot) | default when uncertain: none
                    2. SIZE RUNG (only when resemblance is none) [J:rung] 06's improvised ladder:
                       hand (one hand lifts and throws it) | body (about a person's weight) |
                       heavy / massive (dropped or toppled only)
Computation [D]:    resembles W -> W's weight, base severity, bands and Strike cost, with NO weapon
                    properties, NO mastery (its deed tag is deed.martial.thrown.improvised for throws,
                    else the resembled weapon's), and the frame carries the engine-cited Precision snag
                    "improvised" unless the wielder holds the resembled weapon's training license.
                    none -> 06's improvised table: hand S1 (S2 if it resembles a light weapon), body S3
                    for two actions with one Precision snag, heavy S3 / massive S4 dropped or toppled.
                    On a critical failure the object takes cost.gear S4 (broken) in addition to any cost.
Stakes:             as the Strike's frame (06.4.3)
State writes:       frame fields; the object's condition on a critical failure
Narration may not imply: weapon properties the object does not have (reach, parrying); harm above the
                    computed severity
Worst case (J):     the neighboring weapon is chosen: at most one severity rung (S2 vs S3) or one
                    action of cost; shown in the OFFER before commitment (class i)
Examples:           inside: a smith's hammer swung at a thief -> war hammer: S2, 1 action, snag
                    "improvised" (no armor_breaking: properties do not carry over).
                    inside (boundary): a pitchfork -> spear: S2 with reach? No: reach is a property and
                    does not carry; it Strikes at band.engaged only.
                    outside: a lantern thrown -> none, hand rung S1, plus whatever the lantern's fire
                    does as an environment use (06.5.10).
                    tempting non-example: "my iron frying pan is basically a mace, so it ignores armor"
                    -> resemblance mace gives S2; armor_breaking is a property and is not inherited.
Anchor:             yes. Intent verbs: hit with, swing, bash, throw, block with. Knobs: harm_severity
                    (resembled weapon -> size rung), action_cost, dc (unchanged), targets (one).
Basis:              [01 Interface request: "improvised weapons use the resembled weapon's stats"]
                    [06.5.8 improvised ladder] [R7 §4.4 crude fallbacks] [DL-08-06]
```

**08.1.12 Resolving item tags to base items.** `[D]` Wherever a rule names an item by **tag** (02's kits,
00.17.1 Q17; 09's trophy bases; 13's regional stock), the engine resolves it in this first-match order:
(1) a base item whose `default_for` is that tag; (2) for a level-3 tag, the first base item carrying it;
(3) for a level-2 tag with no default, the first base item carrying it or a descendant. Two tags resolve
with an extra field: `item.tool.trade` resolves to **tools of the work** (`bi.work_tools`), which carries
the fact `serves: <deed tag>` set from the livelihood's first craft, trade or work deed tag (02's kit
note), so a herder's shears serve `deed.wilds.animals` and a scribe's case serves `deed.craft.scribing`;
`item.goods.document` with a `teaches:` note resolves to `bi.spellbook` (or `bi.manual` /
`bi.pattern_book` by the taught id's prefix: `ab.*`/`rit.*`, `lic.training.*`, `prop.*`). Kit quantities
of food are **supply** (1 per day, 08.9.4); a kit's riding horse is `bi.riding_horse` at `worn`. The full
mapping for all 39 tags 02's kits use is `base_items.yaml#kit_resolution` [02 Interface request;
00.17.1 Q17].

**08.1.13 Every item has an id from its first mention.** `[D]` + `[J:flag]` A found, bought, made, given
or narrated object that could later be used, sold, lost or cited is created as an item entity before the
narration that introduces it (00.6.6; INV-16). *Flag:* "Could the player cite this object later as a
weapon, a tool, a lever, a valuable or a material?" True for a sword on a rack, a coin purse, a strange
gem, a body that could be harvested; false for the clutter of a room described as clutter. Uncertain →
true. Coin is never an item: it is the `coin` quantity, and every change is `update_quantity` with a
reason; narration never states a post-transaction total the tool did not return (the gold-hallucination
failure) [R1 08 "wealth, counts and inventories are the most fragile state"; R4 §9 08 #4]. *Worst case:*
an inert object is recorded needlessly (harmless) or a relevant one is not (12's claim-vs-state check
catches the unrecorded mention; class iv).

### 08.2 The item-layer power budget

**08.2.1 What items never do.** `[D]` No item, property, consumable, relic or storied item: (a) changes an
attribute (00.4.3); (b) grants competence (00.3.6; a relic's license carries none, 08.4.4); (c) raises the
maximum of Vitality or Focus (those grow with power band and callings: 07, 05); (d) adds an action (INV-11)
or a reaction (06 alone grants those); (e) adds or moves an ability slot (05.2.2); (f) restores Focus
except as a consumable under 05.6.11's cap of 4 per long rest; (g) feeds a calling tier (00.11.5). These
seven are where a character's identity lives; items act only through edge, harm edge, reduction,
resistance, levers, triggered effects, licenses without competence, movement modes, hazard steps, and
`adjust`-family quantities [C:P2; C:P5; R1 08 "gear must not outclass innate abilities"; DL-08-07].

**08.2.2 The item share.** `[D]` In every capped family, the contributions that come **from items** (base
item properties such as `versatile` and `shield`, mundane and passive properties, worked properties,
consumables) are summed and clamped to the **item share** before they join the family at evaluation-pass
step E4 (00.10.4). The item share is always smaller than the family's cap, so the rest of the cap belongs to
abilities, callings and composites:

| Family (00.10.6) | Family cap | **Item share** | What fills the rest |
|---|---|---|---|
| edge (per quantity: a check of a given scope, one defense, an effect DC) | +2 | **+1** | abilities, calling capabilities |
| harm_edge (per harm event) | +2 | **+1** | abilities (Cinder Stride's +1), composites |
| reduction (per harm tag, worn armor included) | 4 (07) | **3** | abilities (Thick Hide, Stone-Flesh), wards |
| multiplier (resistance ×½) | one ×½ | **one ×½, only from a signature at tier 4+** | abilities, rites |
| step (severity, reach, stakes, hazard steps) | ±2 from effects | **±1** | abilities, rites |
| circumstance (levers) | ±4, ≤ 2 levers | **at most one item-granted lever per roll** | facts of the scene, Setup, abilities |
| adjust: carry | the quantity's envelope | **+4** | — |
| adjust: supply use | — | **−1 per day** | foraging (10) |
| adjust: Focus cost | 05.6.3: −1 per activation | **−1, once per scene, only an implement's signature** | abilities |

Example: a weapon with `versatile` (+1 harm edge in two hands) gains nothing from a Keen property (the item
share of harm edge is already full), and the generator will not place Keen on it (08.2.4); a character
whose cloak is Ember-warded (reduce fire 2) and whose amulet is too (2) has an item fire reduction of 3, not
4. *Implementation:* every modifier the engine collects at E0 already knows its source entity; the sub-cap
is one sum-and-clamp per family before E4's family stacking (Interface request to 00) [R3 00.13 "a per-layer
power budget"; R3 #11; PG5's jewel-socket meta; DL-08-07].

**08.2.3 Per-item caps.** `[D]` One item holds at most its rung's slots (08.1.4), clamped to its base
`slot_cap` (weapons, armor, shields, jewelry, implements 3; garments, tools, mounts 2; consumables and
goods 0), plus its one `worked` property only if a magnitude slot is open for it (08.6.10). At most one
property per `mod_group` (00.11.3 step 6), at most one **on-hit** trigger (mod group `on_hit`), at most one
**retort** trigger, at most one **item-bound ability** (it may sit only in the signature slot), at most one
**license** property (mod group `relic_license`, also signature-only). These make every item readable in
one line of the codex.

**08.2.4 Saturation at generation.** `[D]` When the generator (00.11.3 step 1) gates a pool, it drops every
entry whose family the **base item already fills to the item share**: harm-edge properties on a versatile
weapon; Guarding on a shield or beside a parrying weapon; Reinforced on heavy armor (3 of 3). At step 9 it
checks the item's whole contribution against the item share and, on a breach, drops that pick and refills
once (00.11.3 step 9). The simulation counts 16 such refills in 1,000 drops and **1,000 of 1,000 items
compliant** after generation (T-08-16).

**08.2.5 Attunement limit.** `[D]` A character may have at most **five** items attuned at once (08.5.2).
Mundane properties need no attunement; passive, license and item-ability properties do. Five sits between
D&D 5e's three attuned items and Pathfinder 2e's ten invested items, and it is the number at which the item
shares bind for about one character in five (T-08-16: with five attuned items drawn from a realistic haul,
18.4% would exceed an edge share, 19.4% the harm-edge share and 26.6% a reduction share without the
clamp) — so the choice of *which* five is a real choice, which is the point of a budget [R2 08 Iron Man
Principle; DL-08-14].

**08.2.6 The math: gear never out-scales callings.** `[N]` The numbers below use 00.3.7's envelope, 06.4.5's
mastery and 07.2.2's armor; "items" means the item share at its maximum.

| | P1 novice | P3 elite | P5 legend |
|---|---|---|---|
| Best-domain base modifier (attribute + competence + edge) | +3 + 2 + **1 (item)** = +6 | +3 + 5 + 1 (ability) + **1 (item)** = +10 | +4 + 6 + 1 + **1** = +12 (cap) |
| Items' part of the check modifier | 1 of 6 (17%) | 1 of 10 (10%) | 1 of 12 (8%) |
| Strike harm, one-handed weapon, unarmored foe, Standard reach | S2 3 + **1** = 4 | expert S3 5 + **1** = 6 | master S4 8 + 1 (ability) + **1** = 10 |
| Items' part of harm | 1 of 4 (25%) | 1 of 6 (17%) | 1 of 10 (10%) |
| Physical reduction (armor + items / cap 4) | light 1 + **1** = 2 | medium 2 + **1** = 3 | heavy 3 + 1 (ability) = 4 |
| Growth from P1 to P5 owed to callings | — | — | check +6 of +6; harm +5 of +6; Vitality +8 of +8 |

Against a Guard-13 foe the P1's item edge moves success from 65% to 70% (T-00-6); at P5 the same +1 is the
difference between 40% and 45% against a Very hard target. Items never stop mattering — they are the
specialization a character *chooses* — but at every band the calling owns at least 75% of the check
modifier's growth and all of the maxima. The two edge caps of 00.3.5 (+2 edge, +2 harm edge) are therefore
never filled by gear alone, which is 00.17.1 Q2's demand ("passive and mundane properties … count against
08's item-layer budget") stated as numbers [R1 08; R3 00.13; DL-08-07].

**08.2.7 Item density by band.** `[N]` + `[D]` Encounter tuning (09) and pacing (12) may rely on this
assumption, which follows from the drop check (08.3.3), two fights per session and 04's tier pacing (tiers
at sessions ~4/9/19/34/56):

| Power band | Sessions in band (focused) | Property items won (typical) | Attuned (of 5) | Bound abilities (of 4 equipped slots) | Highest signature tier usual |
|---|---|---|---|---|---|
| P1 | 1–9 | 2–4 | 0–2 | 0 | 2 |
| P2 | 9–19 | 4–6 | 2–4 | 0–1 | 3 |
| P3 | 19–34 | 8–12 | 4–5 | 1–2 | 3–4 |
| P4 | 34–56 | 15–25 | 5 | 2–3 | 4–5 |
| P5 | 56+ | 25+ | 5 | 2–4 | 5–6 |

Items won past five are traded, salvaged into materials and recipes (08.6.8), given away or kept for
their mundane use; nothing past the attunement limit adds power. A campaign whose actual density runs more
than one row ahead of this table is the VI revisit trigger for the drop check (OEQ-08-2) [R1 08 "item
density is a balance assumption"; R2 08 HWFWM's loot system retired for over-generating].

### 08.3 Loot: what a defeat or a find yields

**08.3.1 When loot generates.** `[T]` + `[D]` `generate(gen.loot, source, circumstance, degree, options)`
(tool #24) is called by PR-08-1 in exactly these cases:
1. **A side is defeated.** On `conflict_end` (or when the last member of a side is defeated, yields or
   breaks), once **per defeated side**, with source = the side's highest-band member that was defeated or
   yielded (a mob, a pack or a warband is one side, 06.10.2). Members that fled (`drive_off`) take their
   gear and purses with them.
2. **A body or a yielded creature is searched outside a conflict** (a sentry knocked out, a duel won):
   once, with that creature as source.
3. **A found thing is searched**: a cache, a corpse found dead, a chest, a lair's hoard, a site's treasure
   (source = the hoard's keeper if known, else the place, 08.3.12), with the degree of the resolved search
   beat (Observe or Handle).

Only resolved outcomes generate (00.11.2): a defeat must carry the frame id of the beat that caused it
(06.13.3's `on_defeat` payload); a narrated kill that was never resolved yields nothing. Independently of
any property item, every **body** may be harvested (08.3.10) and every carrier of coin or gear yields its
purse and gear (08.3.11) — so every resolved defeat yields *something*, which is constitution P5's "a
defeated source drops an item generated from its gated pool" [C:P5 sixth pass; R3 #8; 06.13.3].

**08.3.2 The loot circumstance.**

```
### 08.3.2  Loot circumstance: how was it won?                      [J:enum] [D]
Trigger [T]:        PR-08-1 step 2 (a generate(gen.loot) call is due)
Loads in:           situation.conflict, situation.exploration, situation.downtime
License check:      none (classification of a resolved outcome)
Decisions (J):      1. CIRCUMSTANCE [J:enum] (gen_loot.yaml#circumstances; cites frame and fact ids)
                       decisive - true only when the source was defeated by the PC's own resolved beat
                         (its frame id is on on_defeat) in a conflict in which the PC was never Staggered
                         or Dying and no frame against the PC was lethal. False for a foe finished by an
                         ally, a companion or a hazard; a fight in which the PC was Staggered; a foe that
                         yielded and was spared.
                       costly - true only when the source was defeated by the PC's own resolved beat AND
                         during that conflict the PC was Staggered or Dying, or a frame against the PC was
                         lethal. False for a hard fight the PC came through above 0 Vitality with no
                         lethal frame. (This is gen_absorb's narrow_survival: one classification serves
                         both domains, 04.10.)
                       merciful - true only when the source yielded, was subdued nonlethally, or broke and
                         was let go, by the PC's own resolved beat, AND a mercy fact is written (it is
                         spared alive). False for a creature bound and then killed; for a mindless
                         creature (creature.undead.mindless, creature.construct, creature.horror.ooze),
                         which cannot yield.
                       scavenged - none of the above: found dead, killed by another or by a hazard, or a
                         thing found rather than won; the degree is the SEARCH beat's. DEFAULT when
                         uncertain.
Computation [D]:    fill method: decisive -> signature; costly -> biased (bias tag ward);
                    merciful -> chosen; scavenged -> weighted (gen_loot.yaml#fill_map)
                    quality rung: decisive, costly, merciful (success or critical success) -> masterwork;
                    scavenged: critical success or success -> fine; failure or critical failure -> common
Stakes:             none (no roll; the degree comes from the frame that produced the defeat or the find)
State writes:       the generated item(s) and the generation log (PR-08-1)
Narration may not imply: any property, tier or rung the output does not hold; that the foe "dropped" a
                    thing it never carried (a wolf carries no coin)
Worst case (J):     decisive vs costly: the signature is the source's own instead of a ward-biased
                    draw, same rung (class i); merciful vs decisive: the player chooses among three
                    instead of receiving the signature, same rung (class i); scavenged vs a won
                    circumstance: fine instead of masterwork, one rung (class i). Errs toward the
                    default (scavenged) when uncertain, which errs low (SG-05 tie-break "does this
                    grant something?" -> no).
Examples:           inside decisive: Wren shoots the spider dead with her own arrow, never below half
                      Vitality -> decisive.
                    boundary costly: the same fight, but the spider's bite took her to 0 and she shot it
                      while Staggered -> costly.
                    boundary merciful: the bandit captain yields at 2 Vitality and Wren lets him go with
                      his life (fact mercy.bandit_captain) -> merciful; he gives up his sword.
                    tempting non-example: "I killed it cleanly while my hound held it" -> the killing
                      frame is Wren's, so decisive; but if the hound's bite was the defeating frame, the
                      circumstance is scavenged (the PC's own beat did not defeat it).
Anchor:             no
Basis:              [C:P5 "decisive vs. costly vs. merciful"] [00.11.2] [R: src/ability_pool.py
                    decisive_kill / narrow_survival / non_lethal_subdual] [04.10 gen_absorb] [DL-08-09]
```

Mercy is never worse than a kill: a spared source gives the same rung as a decisive kill and lets the
player choose. This is deliberate: the conduct axes (03) must not pay cruelty in loot [C:P5 "values-
expressive"; 03 conduct.mercy; DL-08-09].

**08.3.3 The drop check.** `[D]` Before the rung is looked up, the engine rolls d100 against the source's
**yield** (`gen_loot.yaml#drop_check`):

| Yield | Property item drops on d100 ≤ | Use for |
|---|---|---|
| `none` | never | vermin, swarms, mindless things with nothing worth keeping (they still yield materials) |
| `trophy` (default for anything with a body) | T1 **10** · T2 **20** · T3 **35** · T4 **50** · T5 **70** | ordinary foes |
| `hoard` | always, by the hoard table (08.3.12) | lairs, treasuries, sites |
| `always` | always, by the circumstance | principal NPCs (12.11.1), named foes, an archetype 09 marks |

A miss is not nothing: harvest, purse and gear still come (08.3.10–08.3.11). The chance rises with the
source's band and never reads the PC (no smart loot, 00.11.4): rabble rarely carry anything worth an
identity, and grinding them at P5 yields tier-1 trinkets one fight in ten. *Why a chance at all:* with one
generation per side and two fights a session, an unconditional drop would put 50–110 property items into a
campaign by P4 — the shape of HWFWM's retired over-generating loot system (R2 08). The check holds the haul
near 08.2.7's density (simulated rates 8 / 22 / 35 / 51 / 76%, T-08-16) [R3 A-1 (Diablo II's treasure-table
"NoDrop" weight); DL-08-08].

**08.3.4 The pool gate: nature and place (the contract with chapter 09).** `[D]` The gated pool for a loot
call is every entry of `item_properties.yaml` whose `domains` include `loot` and whose `gate_tags` match
(00.5.4c: an entry gated on G matches a source tag S when G = S or G is an ancestor of S) one of:
1. the source archetype's **`creature_tags`** (09: most specific first), **`harm_tags`**, **`evidence_tags`**
   (its `deed.*` tags) and **`org_tags`** (folk), plus any **`loot.pool_gate_tags`** 09 adds;
2. the generated base item's **`material_tags`**;
3. **`creature.folk`**, when the base item is an armament (weapon, armor or shield) taken from a folk or an
   undead source (made by hands: the folk-made mundane properties open to it);
4. the **place's terrain tags**, but only for entries flagged `place_gated: true` (a frost-shod boot can come
   from any foe killed on the high ice; a wolf in a forest never drops it).

Then entries are dropped when: an `excluded_tag` matches the source; no `base_kinds` entry is an
ancestor-or-equal of a base item tag; the base saturates its family (08.2.4); `min_tier` exceeds the tier
cap (08.3.5); the entry is `player_only`/`adversary_only` against this use. This is a hard zero-weight
exclusion (R3 08.1). The place axis is R2 #13's "gate by nature *and* place" (HWFWM's stones manifest
where their theme lives) — it widens the gate, it never adds a third fill axis.

*What 09 must give each archetype* (`gen_loot.yaml#contract_09`): `creature_tags`; `harm_tags`;
`evidence_tags`; `org_tags` for folk; `threat_band`; `loot.yield` (default `trophy`; `none` for mindless
vermin and swarms); optionally `loot.trophy_base` (an item tag or `bi.*` id), `loot.pool_gate_tags`,
`signature_property` (a `signature_eligible` entry whose gate tags match; default:
`item_properties.yaml#default_signatures`, which names a designed signature for **every one of the 45
level-2 creature tags**), `gear` (folk: the base items it carries, mundane, `worn` or `common`), `purse` (a
coin table, 08.3.11), `harvest` (a `mat.*` override). *Validation 09 must run:* for every archetype and each
base it can drop, the gated pool at tier cap 1 holds at least **3** entries; the reference set of 26
archetypes in `08-loot-sim.py` passes for all but one (an aberration's charm at tier 1, which is moot: the
aberration is T4), and 09 re-runs the same check on its own bestiary (T-08-16).

**08.3.5 The tier cap.** `[D]` The source's threat band is its **tier cap** (T1 → 1 … T5 → 5); a place's is
its site band (10/13). Signature properties take the tier cap; magnitude properties take tier cap − 1,
minimum 1; a property at tier *t* uses its highest authored tier row ≤ *t* (values are fixed per tier, never
rolled: 00.11.3 step 8). A **Greater** result adds +1 to the signature's tier and may exceed the cap by 1
(a tier-6 signature exists only this way, and uses its tier-5 row plus 08.3.9's Greater mark). This is
Diablo II's affix-level gate with the threat band as item level: a T2 wolf can never yield a tier-4
property [R3 08.4, A-2].

**08.3.6 The base item.** `[D]` First match:
1. 09's `loot.trophy_base` for the archetype (a tag resolves per 08.1.12 among bases with
   `trophy_eligible` not false; a `bi.*` id is used as is);
2. for folk and other armed sources, one item of its **gear**;
3. the trophy default for its creature branch (`gen_loot.yaml#base_selection`): beasts — charm, cloak,
   leather armor; undead — ring, amulet, weapon; spirits — charm, amulet; fiends — weapon, ring; constructs —
   shield, amulet, medium armor; elementals — charm, amulet; dragons — armor, shield, charm; horrors — charm,
   weapon. The engine draws with a d6 over the list (1–2 first, 3–4 second, 5–6 third).

**Signature-honoring:** when the fill is `signature`, the draw is made only among listed bases whose kind
the signature property accepts; if none does, the base is the default base of the signature's first base
kind (a wyvern's sting needs a weapon: a wyvern-fang dagger, not a scale shield). **Redraw:** if the drawn
base's gated pool holds fewer entries than the rung has slots, the base is redrawn once from the same list
(the simulation needed 0 redraws and 49 signature-driven overrides in 1,000 drops) [DL-08-10].

**08.3.7 Quality rung and slots.** `[D]` From the circumstance and degree (08.3.2's table): decisive,
costly and merciful wins give **masterwork** (one signature slot, one magnitude slot); a scavenged find
gives **fine** (one magnitude slot) on a success or critical success and **common** (no property) on a
failure. Hoards give their table's rungs (08.3.12). Slots are clamped to the base's `slot_cap` (08.1.4).
Wondrous items come only from hoards of T4–T5, from bargained gifts (08.7) and from expert or master
crafting (08.6) — never from an ordinary kill, which keeps the rung legible: a masterwork trophy is what a
fair fight is worth.

**08.3.8 Fill, slot by slot.** `[D]` (00.11.3 steps 4 and 6; PR-08-1.)
- **Signature slot first.** `signature`: the archetype's signature property (09's, else
  `default_signatures` of its most specific creature tag) if it survived the pool gate; if it did not, a
  weighted draw among `signature_eligible` entries **excluding relics** (a decisive win never falls back to a
  relic: relics come from costly, merciful and scavenged fills, gifts, crafting and archetypes that name
  `prop.bound_power` as their signature). `biased`: a weighted draw among `signature_eligible` entries with
  weight ×3 for entries whose `bias` equals the bias tag. `chosen`: the tool shows up to three
  `signature_eligible` entries (drawn by weight without replacement) and the player picks one. `weighted`:
  a plain weighted draw among `signature_eligible` entries.
- **Magnitude slots next**, from entries not marked `signature_only`, by the same method (chosen shows three
  per slot; biased ×3).
- After each pick, every entry sharing its `mod_group` is removed (hard mutual exclusion, R3 08.5).
- **Recency:** entries produced in the last 5 draws of the loot domain (in this campaign) have their weight
  halved; to keep integers the engine doubles every weight first, so recent entries count ×1 and the rest ×2
  (00.11.3 step 7; OEQ-00-5).
- An empty pool leaves a slot empty (the item keeps its rung; its price counts only filled slots).

**08.3.9 Degree effects, caps and output.** `[D]`
- **Greater** (critical success): the signature, or the first magnitude property if there is no signature,
  gains +1 tier (00.11.3 step 5); the item record marks it `greater: true`.
- **Flawed** (critical failure, possible only on a scavenged search): the find's magnitude slot is removed
  (a fine find becomes common) and the item is created `damaged`.
- **Caps** (step 9): the item share and per-item caps (08.2.2–08.2.4); a breaching pick is dropped and the
  slot refilled once; if it fails again, the slot stays empty.
- **Bound power:** when `prop.bound_power` fills the signature slot, the tool calls
  `generate(gen.item_ability, …)` with the same source, circumstance and tier (08.4.3); if that pool is
  empty, the signature is redrawn once among non-ability entries.
- **Output** (step 10): the item entity with base, rung, signature, properties, sealed flags (08.5.3),
  provenance and the generation log (pool size after each gate, weights, draws). The DM names it and
  narrates only what it holds; it never adds a property (INV-2).

**08.3.10 Harvest: a body's materials.**

```
### 08.3.10  Harvest: take what the body is made of                 [J:flag] [D]
Trigger [T]:        a body (dead, or of a creature that cannot object) is at band.engaged with the PC
                    after a resolved defeat, and harvest.done is not set on it
Loads in:           situation.exploration, situation.downtime
License check:      basic verb: verb.handle (G1) for hides, bones, horn, fangs, feathers and sinew;
                    essences (glands, hearts, blood, ichor, residue, cores) need a held license whose
                    scope covers dissection: lic.training.wilds_foraging, lic.training.lore_bestiary or
                    lic.training.craft_alchemy; without one, an essence is G3 with crude_fallback
                    "cut it out anyway": dc_shift +5, reach capped Limited, and the part's harvested
                    rarity band falls by 1
Decisions (J):      1. FRESH [J:flag] "Is the body fit to harvest?" True only when it was killed within
                       the last day and has not been burned, dissolved, eaten or sealed in a way a fact
                       records; false for a body found days dead (only bones and horn remain) or a
                       spectral or elemental foe that left no body (their residue or core is the body).
                       Uncertain -> true for bones, horn and fangs; false for soft parts.
Computation [D]:    the parts: every materials.yaml entry whose source_tags match the body's
                    creature_tags (most specific first), or 09's harvest override.
                    frame: verb.handle, primary tag deed.wilds.foraging.harvest, DC = the rarest part's
                    harvest dc_tier (band 0-1 Easy, 2 Moderate, 3 Hard, 4 Very hard), stakes Safe
                    (Risky if the body is in a hazard or the scene is hostile), time 1 interval (load-1
                    parts) or 1 hour (a large body).
                    delivered reach 1 -> the common parts (rarity band <= 1), one unit each;
                    2 -> plus ONE special part (engine-drawn among band 2+); 3 -> every part;
                    4 -> every part, and one special part counts one rarity band higher (pristine).
                    failure -> common parts only, and soft parts are spoiled; critical failure -> nothing.
                    Each harvested part is an item with provenance {source_id, source_tags, archetype,
                    band} and rarity band max(the material's band, the source's threat band - 1); it
                    carries the source archetype's signature into crafting (08.6.2).
Stakes:             safe (or risky, per Computation)
State writes:       material items created; harvest.done on the body; evidence on the primary tag (03)
Narration may not imply: parts not on the material list (a wolf has no fire gland); a part's properties
                    (a material has no properties until made into something, 08.6)
Worst case (J):     FRESH wrongly true: soft parts harvested from a body that should have spoiled -> at
                    most one special part (class i); wrongly false -> the player can cite the time of
                    death fact (class iv)
Examples:           inside: Wren skins the giant spider within the hour: chitin, silk, a venom sac.
                    boundary: the same spider found three days dead in a web -> FRESH false: chitin and
                      fangs only.
                    outside: a wraith leaves no body; its ectoplasm IS the harvestable remains (residue
                      gates as the body).
                    tempting non-example: "I harvest the dragon's fire breath" -> no material is a
                      breath; the fire gland is the part (and its power is the Taking's, 04.10, not a
                      harvest's).
Anchor:             yes. Intent verbs: skin, butcher, carve, harvest, take a trophy, cut out, collect.
                    Knobs: dc (by the rarest part), time_cost (interval -> hour), reach_unit (parts).
Basis:              [04.10.1 "the Taking's crude fallback is to harvest the body for materials"]
                    [R: https://en.wikipedia.org/wiki/Monster_Hunter_Wilds (carving)] [R2 #13] [DL-08-12]
```

**08.3.11 Coin, gear and goods.** `[D]` A defeated, yielded or robbed carrier gives: (a) its **purse**, one
roll on `economy.yaml#purses` by band (T1 1d4−1 coins; T2 2d6; T3 4d6+5; T4 6d10+20; T5 10d10+80), only for
carriers of coin (09 marks beasts `purse: none`); (b) its **gear**: every base item it carried, at `worn`
(T1–T2) or `common` (T3+) unless 09 says otherwise, with no properties; (c) goods 09 lists. Gear and coin
are generated by tables, never chosen (INV-3).

**08.3.12 Hoards and places.** `[D]` A hoard (`yield: hoard`, a lair, a vault, a site's treasure keyed by
10/13) generates by its band (`gen_loot.yaml#hoard_map`): T1 one fine item; T2 one masterwork; T3 one
masterwork and one fine; T4 one wondrous and one masterwork; T5 one wondrous and two masterworks; plus
`hoard_coin` (T1 3d6×3 … T5 10d10×150) and `hoard_goods` (gems, art, trade goods by band). The source is the
hoard's keeper if known (a dragon's hoard is gated by the dragon), else the **place**: the place's terrain
tags and site theme (10) act as the source tags, so a barrow's treasure is tomb-warded and whispering. The
circumstance is decisive if its keeper was defeated by the PC, else scavenged with the search beat's degree.

**08.3.13 Telling the player.** `[N]` The DM names what was found in fiction ("a fang on a thong, still
warm", "the captain's sword, notched near the hilt") and nothing more; the codex shows the item's rung,
known properties, sealed slots and price. A drop is narrated in one line unless the player asks, because
The Land's ten-minute loot readouts are the genre's documented failure (R2 08). *Narration may not imply:*
a property not in the output, a sealed property's nature, a price the tool did not compute.

### 08.4 What items grant

**08.4.1 The answer to constitution P5's deferred question.** `[D]` "Whether a dropped item itself grants an
ability, a passive bonus, or nothing beyond mundane value" is answered by the same pool-gate/fill-quality
shape that produced the item, slot by slot:

| An item's… | can hold | which means |
|---|---|---|
| magnitude slots (0–2) | mundane or passive properties | numbers and triggered effects inside the item share (08.2.2) |
| signature slot (0–1) | a signature property (passive or mundane), **or** a license property, **or** the bound power | its identity: what the source was |
| base item | its own numbers (severity, reduction, Guard edge, a kit's lever) | what any such object does |

So a dropped item grants exactly one of: **nothing beyond its base** (common, worn, or a fine item with an
open slot); **mundane value** (a mundane property: Keen, Sturdy); **passive bonuses** (passive properties);
**an off-identity license** (a license property: a relic); or **one item-bound active ability** (the bound
power: a relic) — the last two only in the signature slot, so **at most one** license or active per item,
and at most one item-bound active per item as 00.17.1 Q2 requires. The kind follows from where the
generator puts things, not from the DM's sense of what would be nice [C:P5; 00.11.5; R3 08.10].

**08.4.2 Passive properties: how they fire.** `[D]` A passive property is a set of effect references (00.10),
active while its item is equipped and attuned. Additive ones join the evaluation pass in their family,
under the item share (08.2.2). Triggered ones subscribe to one hook (00.10.2) with a **chance** expressed as
a natural d20 range on the triggering roll's own die (00.10.7): tier 1 "20", tier 2 "19–20", tier 3 "18–20",
tier 4 "17–20", tier 5 "16–20" (`item_properties.yaml#chance_rule`). An item's triggers are subscribers like
any effect: they fire only on depth-0 events, so an item's proc never procs another (INV-12). An item's
claim on a behavioral slot (an elemental strike, a movement mode) carries `priority_rank` **15–19** (14 +
tier), above abilities (10–12) and below applied consumables (20–24), per 05.10.3. Uses-limited properties
count their uses on the engine (00.10.9).

**08.4.3 Item-bound active abilities (`gen.item_ability`).** `[D]` When the bound power fills a signature
slot (only at tier 3+; its `min_tier` is 3), the tool calls `generate(gen.item_ability, source,
circumstance, degree)` with the parent call's source and circumstance:
- **The pool is not authored anew.** It is ch.04's **absorbed natural powers** (the active entries of
  `gen_absorb.yaml`, gated on creature tags: a beast's trophy holds a beast's power) and ch.05's **calling
  techniques** (every active `calling` ability without a conduct requirement, gated on its first deed tag);
  162 entries in `gen_item_ability.yaml#pool` (159 before revision A added three primal element workings). A source with no deed tags of its own reaches techniques
  through `source_to_deed` (a fire elemental → `deed.arcane.fire`, `deed.primal.elements`; an order of
  hunters → `deed.wilds`, `deed.martial.archery`). Never in the pool: oath-gated or conduct-gated
  abilities, `adversary_only` entries, passive abilities (an item passive is a property), and any ability
  the bearer already holds (05.2.9: it stays dormant).
- **Fill** follows the parent circumstance: decisive → the archetype's `signature_of` absorbed power if it
  passes the gate, else weighted; costly → biased toward ward; merciful, earned, bargained and crafted →
  chosen; commissioned → biased toward the named tag; scavenged and improvised → weighted; favored →
  signature (`gen_item_ability.yaml#fill_map`).
- **Rank** is the item's, fixed at generation: tier 3 → rank 1, tier 4 → rank 2, tier 5+ → rank 3, capped at
  the ability's authored ranks; an absorbed power uses its highest authored tier row ≤ the item's tier.
  The rank never rises: a relic does not grow (R2 #9).
- **Binding** (05.2.8): while the item is equipped **and attuned**, the ability binds to a free slot of the
  `equipped` partition (4 slots); with all four in use it is dormant and the codex says so. It is used at the
  item's rank, never a calling's, at its listed Focus **+1 relic surcharge** when the bearer holds no
  training license at or above its first tag (05.6.3); its uses are its own `limits`.
- **Evidence:** deeds done through it write **no deed evidence** (`feeds_evidence: false`; 04's request 11;
  05.2.8). Conduct evidence still records (a cruel act is cruel whoever's power did it).

**08.4.4 Relics: borrowed capability at a premium.** `[D]` A **relic** is any item holding a bound power or
a license property. Relics are how a character tries something their calling does not license (goal 1)
without that becoming who they are (VII; P5):
1. **License properties** (18 entries, `prop.lic_*`, signature-only, tier 2+) grant a named license while
   equipped and attuned, through `lic.08.relic_grant`: a tongue at grade `broken` (an Elvish torc), a
   people's sense (Stone-sense, Starsight, Cave-eyes, Hound's nose), or a training license at grade
   **trained** (Lock-whisper → `lic.training.guile_thievery`; Beast-friend → `wilds_animals`; Sea-legs;
   Spirit-speech → `primal_spirits`; Ward-mark → `arcane_warding`; Captain's token → `influence_command`;
   Leech's gift → `lore_medicine`).
2. **No competence:** a license from an item carries **no competence** (00.3.6: items never grant it). The
   bearer rolls with attribute + their own competence (often only the +1 floor) + edge, and the trained
   grade caps the obstacle tier at **Hard** (`licenses.yaml#grades`). A relic makes the attempt *legal*; it
   does not make the bearer good at it.
3. **No growth:** `feeds_evidence: false` — nothing done under a relic's license or through its bound
   ability counts toward any calling (00.11.5). The relic's grade and rank are fixed. A character who wants
   to *become* a lockpick learns from a mentor (05.9) — and may use the relic meanwhile.
4. **The surcharge:** an ability used through a relic costs +1 Focus unless the bearer holds the training
   license of its first tag (05.6.3). A license property has no Focus cost of its own; its price is the
   attunement slot and the absence of competence.
5. **Protection:** while attuned, a relic is `cost_immune` (08.1.10).
6. **Spare, not double:** a relic granting a license or ability the bearer already holds grants nothing
   (INV-13; 05.2.9): it is a spare.

*Why this shape:* Stormlight's Honorblades let anyone bind their Surges "without regard for oaths", at far
higher Stormlight cost and with none of the bond's growth (R2 #9). The surcharge, the missing competence
and the missing growth are three independent levers (P12: cost, limitation, weakness), each a number in data
[R2 #9; C:P12; 04.11.3 "lend an item that licenses a capability while carried"; DL-08-11].

**08.4.5 Consumables.** `[D]` A consumable's `effects` apply when it is used, and its `uses` fall by one.
Using one is a beat or a free activity as 06 classes it (drinking a draught, applying an oil and throwing a
firepot are actions in a conflict; eating is a free activity outside one, 00.12.6). Caps that bind them:
healing draughts count toward 05's two healing effects per recipient per long rest; Focus draughts toward
05.6.11's 4 Focus between long rests (the codex warns before one is wasted); weapon oils claim
`slot.strike_delivery` at rank **20** for 3 Strikes (a newer oil replaces an older one; an item's intrinsic
elemental strike at 15–19 is suppressed while the oil lasts and resumes after); a whetstone's harm edge is an
item contribution and adds nothing to a weapon already carrying an item harm edge; a remedy shifts an
affliction per 07.9.6 (specific remedies two stages, general one); a firepot is a shaped attack (`burst`,
06.8) whose harm is its listed severity; blade venom writes conduct evidence per 03 when used on the
unwilling. A **scroll** holds one ability (inscribed by `deed.craft.enchanting.inscription`, 08.6.11):
reading it activates that ability once at rank 1, needing no equipped slot, at its Focus (+1 relic
surcharge without the training license), and is consumed.

**08.4.6 Teaching texts and recipes.** `[D]` A document item may carry the fact `teaches: <id>` (02's
spellbook; 05.8.5; 05.8.7; 05.9):
- `teaches: ab.*` or `rit.*` (a **spellbook**, `bi.spellbook`): each downtime week of study ticks the
  learning clock **2** (05.8.5) or the rite clock (05.8.7); reading needs `lic.lang.letters` and the text's
  language;
- `teaches: lic.training.*` (a **manual**): a week of study ticks `clk.train` **1** (05.9);
- `teaches: prop.*` (a **pattern book**): a week of study with the property's craft license writes
  `knows_recipe: prop.*` (08.6.9).
A text is an item: it can be copied (craft.scribing, 08.6.11), stolen, burned and sold. A text found as
loot is generated as a `bi.spellbook`/`bi.manual`/`bi.pattern_book` whose taught id is drawn from the gated
pool (techniques of the source's deed tags; properties of its signature family) [05 Interface request (f)].

**08.4.7 Implements: signs and vessels.** `[D]` An implement (`item.tool.implement`: wand, casting staff,
orb, holy symbol, totem; never called a "focus", T-00-22) serves two of 05's rules through facts on the
item: it is a keeper's **sign** (05.7.4) when it bears the fact `sign_of: <keeper>` (made or blessed so);
it is a reserve's **vessel** (05.6.12) when it bears `kept_since:` a time at least a season ago or
`made_by_holder: true`. Implement properties (the arcane bias): *Conduit*, *Blessed*, *Wild-bound* (+1 to
the DC of workings of the branch, the item share of edge), and their *thrift* signatures (tier 3+: once per
scene, the first working of the branch costs 1 less Focus, within 05.6.3's −1 cap). A destroyed vessel loses
its banked points (05.6.12) — and an implement with a signature is never destroyed by a cost (08.1.9).

**08.4.8 Sets and storied items.** `[D]` A **storied** item (rung 6) is authored by chapter 13 or later
content as a fixed property set (one signature, up to two magnitude properties, or a bound ability in place
of the signature), exempt from mod groups but never from the item share, the slot cap or the attunement
limit. Two storied items may be a **set**: each carries a license property flagged `composite_key`, and a
`named_composite` in `composites.yaml` (05's file) keyed to the two licenses is active while both are
attuned (00.10.7) — Diablo's set bonuses as constitution P6 composites, bounded to one composite per pair
[R3 08.7, A-3; C:P6].

### 08.5 Equipping, attunement and identification

**08.5.1 Body slots.** `[D]` Equipped items occupy body slots; carried items are in the pack and count
only toward load (08.9.1).

| Slot | Holds | Count |
|---|---|---|
| hands | weapons, shields, implements, held tools; a two-handed item takes both | 2 |
| body | armor | 1 |
| clothing, cloak, feet, gloves, head | the garment of that kind (a helm, hood, hat or circlet takes head) | 1 each |
| neck | amulet or torc | 1 |
| rings | rings | 2 |
| charms | charms (trophies on a thong or a belt) | 2 |

A buckler and a lit torch may share a hand (08.1.7). Drawing, stowing and handing over a held item follow
00.12.6 and 06's action costs; donning or doffing armor takes its `don_time` and cannot happen in a
conflict. An item out of its slot (in the pack, in another's hands) is not equipped: its properties stop.

**08.5.2 Attunement.** `[D]` (`lic.08.attunement`, held by every character.) At a **breather** outside a
conflict, a character may attune one equipped item that carries a passive, license or item-ability
property; at most **five** at a time (08.2.5), and an ally's attunements count against its PC's five
(16.4.8) [integration: IR ch.16 to 08 (c)]. Attuning: (a) makes its passive and license properties work
while it is equipped; (b) binds its bound power to a free `equipped` slot (05.2.8); (c) **unseals** all its
properties, its bound ability and its flaw to the bearer (the codex shows them); (d) makes a relic or
storied item `cost_immune` (08.1.10). Ending an attunement is a free activity, except under the *Binding*
flaw (08.5.4). Attunement persists while the item is unequipped and ends automatically when the item is not
in the bearer's possession at the end of a `rest_long`. Mundane properties need no attunement.

**08.5.3 Sealed properties and identification.** `[S]` + `[D]` + `[J:flag]`
- **What is sealed** (00.6.5): on an item from loot or a gift, the **signature's name and kind are
  apparent** (that it is troll-work, that it holds a power), but its exact effect, the magnitude properties,
  the bound ability's identity and any flaw are `sealed_properties`. A crafted item is fully known to its
  maker; to others its `masters_mark` (if any) names the maker and the rung. The narrator receives the
  permitted slice: the source's look and feel ("cold to the touch", "it hums near the dead").
- **What unseals** (first match, each a tool write `unseal`): (1) **attunement** (08.5.2c: everything);
  (2) **a property fires or applies** in play — a mundane edge in an OFFER breakdown, a trigger's effect —
  which unseals that property; (3) a **sage's or enchanter's service** (`svc.identify`, 10 coins, a town or
  city: everything); (4) **study**: an Observe beat (or Recall for a known kind) of one interval, primary
  tag `deed.lore.arcana` (or `deed.lore.bestiary` for a creature trophy), DC by the highest sealed tier
  (tiers 1–2 Moderate, 3 Hard, 4 Very hard, 5+ Legendary), stakes Safe; delivered reach is the number of
  sealed properties revealed, in the order the player ranks them (00.14 `deliver`; constitution P17's
  graduated reveal). A failed study reveals nothing, and the same character cannot study that item again
  until their next `rest_long` (P17: a repeated bundled question is not free).
- *Flag:* "Is this property's effect perceivable as it happens?" (for rule 2) True only when the effect
  changes a number the OFFER shows or produces a narrated effect (a burn, a light, a ward that stops a
  blow); false for effects that only shape rolls nobody made. Uncertain → false (the property stays sealed
  until 1, 3 or 4). *Worst case:* a property unsealed one beat early or late (class iv).
- A flaw is revealed by attunement or a study whose delivered reach covers every property, never by sale
  talk; selling an item with a known flaw without saying so is a `conduct.honesty` event (03).

**08.5.4 Flaws and cursed items.** `[D]` Flaws (`item_properties.yaml#flaws`) are what a Flawed degree
effect writes on a crafted item (08.6.6) and what some loot carries: *Heavy* (carry −1), *Loud* (a Sneak
snag), *Brittle* (`cost.gear` one rung heavier), *Marked* (recognizable as its source's or former owner's),
*Thirsty* (supply use +1 per day while attuned), *Unwelcome* (a Talk snag with the source's kind), *Restless*
(long rests at best partial while attuned; spirit and spectral sources only) and *Binding* (cannot be
unattuned until cleansed; fiend, undead and horror sources only). A **cursed** item is one carrying
*Binding*: it is cleansed by `eff.05.end_working` on the item, a curse-lifting rite (05) or `svc.cure`
(band 3 by severity). Loot never carries a flaw by chance (a scavenged critical failure removes a slot and
damages the find instead, 08.3.9). Flaws reach loot in only two ways, both telegraphed by the source's
nature: a crafted item that was itself made Flawed, and an archetype that 09 marks `loot.flaw: flaw.*` (a
lich's rings are Binding; a banshee's tokens Restless) — the flaw is sealed until attunement or study, and
the archetype's tells (09) say what it is before anyone fights it.

### 08.6 Crafting: the second pool-gate domain

**08.6.1 The shape.** `[D]` Crafting runs the same generator as loot (00.11; constitution P5: "a future
feature in a different domain (e.g. crafting) MUST NOT be assumed to need its own bespoke two-axis
design"): the **material** is the pool-gating source, the **manner of making** (crafted, commissioned,
improvised) is the fill-quality circumstance, and the **degree** of the completing beat gives Greater or
Flawed. The Land's two ladders are kept as two independent axes: a **type-tier** fixed by the materials'
rarity band and the crafter's grade (the tier cap: what can be made at all), and a **quality-tier** fixed by
the declared target rung and its obstacle (how well it is made) [R2 #13; R3 08.11; `gen_craft.yaml`].

**08.6.2 Materials.** `[D]` (`data/materials.yaml`: 59 entries, including `mat.residuum` for salvage.)
- **Stock** (iron, steel, timber, cloth, leather, herbs, silver, gold, yew, cold iron, pure silver, ironwood,
  witchwood, volcanic glass, spell-crystal, precious gems, rare metal, reagent herbs, cave fungus …) is
  bought at market by rarity band (band 0 anywhere; 1 villages; 2 towns; 3 cities; 4 never sold).
- **Parts** (pelts, hides, scales, dragon scale, chitin, fangs, horn, ivory, bones, spinner's silk, sinew,
  venom sacs, fire glands, hearts, cores, blood, ichor, ectoplasm, grave dust, spirit residue, animate clay,
  clockwork, living wood, spore caps, feathers) come from harvest (08.3.10). A harvested part keeps its
  **provenance**: the archetype it came from, that archetype's tags and band, and therefore that archetype's
  **signature**. A wyvern's scales make wyvern-work; a troll's hide makes troll-work (Monster Hunter's
  carve-to-craft identity).
- **Gate tags.** A material's `gates` (its own material tag plus its sources' creature tags) are the craft
  pool's source tags, with two additions: `creature.folk` (the maker's hand: the folk-made mundane
  properties are open to anything made) and a part's provenance tags.
- **What a base accepts.** The primary material must share a level-1 material branch with one of the base
  item's `material_tags` (hide is hide: wyvern scale can make a whip whose base lists leather; metal is
  metal: pure silver can make a sword). One **reagent** (an essence, a gem or special stock) may be added;
  it adds its gates and is consumed.
- **Amount.** A project consumes primary material worth, in that material's coins: common ½ the base price
  (rounded down, minimum 1), fine ×1, masterwork ×2, wondrous ×4; a harvested part counts at its listed
  price, and one part is always enough for one charm, ring or amulet. The reagent is one unit.
- **Tier cap** = min(the crafter's grade cap — trained 2, expert 4, master 5 — and the highest rarity band
  among the materials, counting band 0 as 1). A harvested part's band is max(its listed band, its source's
  threat band − 1), so a T4 wyvern's scales carry band 3.

**08.6.3 The craft circumstance.**

```
### 08.6.3  Craft circumstance: who makes it, and how?               [J:enum] [D]
Trigger [T]:        a crafting project is declared (PR-08-5 step 1)
Loads in:           situation.downtime, situation.exploration
License check:      crafted / commissioned: the base item's make.license (any grade) held by the maker;
                    improvised: verb.handle "crude making and repair" (G1), or the license's
                    crude_fallback (dc_shift +5, reach capped Limited)
Decisions (J):      1. CIRCUMSTANCE [J:enum] (gen_craft.yaml#circumstances)
                       crafted - true only when the PC (or a companion under the PC's command) makes it
                         under the base item's make.license, with that trade's tools, at a workplace (a
                         forge for metal, a bench for wood and leather, a still or kitchen for alchemy
                         and cookery, a desk for scribing and inscription). False for work lacking any
                         one of license, tools or workplace (improvised); work done by a paid crafter
                         (commissioned).
                       commissioned - true only when an NPC crafter who holds the make.license is paid
                         to make it; the player names the base, the materials, the target rung and ONE
                         bias tag (ward, strike, sense, move, social, craft, arcane). False for a
                         companion's work under the PC's command (crafted); a gift (08.7).
                       improvised - anything made without one of license, trade tools or workplace:
                         field work with a knife and what is at hand. DEFAULT when uncertain.
Computation [D]:    fill: crafted -> chosen (the player picks each property from up to three shown);
                    commissioned -> biased (x3 toward the named bias tag); improvised -> weighted.
                    A known recipe (08.6.9) overrides the fill for the one slot it names (recipe).
                    Signature slot: the primary material's signature (provenance), 08.6.2.
                    Rung caps: improvised -> common (fine only by Greater); trained -> masterwork;
                    expert and master -> wondrous.
Stakes:             set by the project's step frames (08.6.4)
State writes:       the project clocks; on completion the item (PR-08-5)
Narration may not imply: a property the output does not hold; that tools or a workplace exist when no
                    fact records them
Worst case (J):     crafted vs improvised: chosen fill and a rung cap of masterwork instead of weighted
                    and common -> at most one rung and the choice among three (class i); the frame shows
                    the tools and workplace facts it cites, so the player can see why (class iv)
Examples:           inside crafted: a trained leatherworker at her bench with her tools, making a hide coat.
                    boundary improvised: the same leatherworker in camp, no bench -> improvised; she can
                      still make a serviceable sling (common), and a Greater lifts it to fine.
                    boundary commissioned: Wren pays the smith of Grey Keep -> commissioned; Wren names
                      "strike".
                    tempting non-example: "I watched the smith, so I'll make my own sword" -> watching is
                      not a license; G3, redirect to the crude fallback (a crude blade, improvised) and the
                      license's acquisition paths (05.9).
Anchor:             no
Basis:              [00.11.2 craft circumstances] [R3 08.3 (Essence/Fossil/Bench as entry points)]
                    [R3 08.15 (RoR2 category chests: choose the category, roll within)] [DL-08-15]
```

**08.6.4 The crafting project.** `[D]` *Anchor: yes.* A crafting project is a clocked extended task
(01.14.6) whose two racing clocks reuse 05's rite shape (05.8.2):
1. **Declare** the base item, the material set, the target rung and (commissioned) the bias tag; the engine
   checks the license, the grade cap, tools and workplace facts, and that the materials are in hand.
2. **Clocks.** A **progress** clock (kind `project`, public) of **4** (worn or common), **6** (fine), **8**
   (masterwork) or **12** (wondrous) segments, ticked by delivered reach; decaying 1 per `week` with no tick.
   A **spoilage** clock (kind `danger`, public, **4** segments; **6** for a wondrous target, a long work
   tolerating more setbacks) racing it, ticked by U(severity) of a failed step's cost.
3. **Each step** is one beat of the maker taking the base item's `make.time_per_tick` (a watch for a charm,
   a knife or arrows; a day for most weapons, garments and shields; two or three days for heavy weapons and
   armor; a day per tick for potions and remedies is a watch): verb per the license (smithing and
   leatherwork are Handle methods under the license), the license's **attribute** (smithing Might, woodcraft
   Agility, leathercraft Agility, textiles Agility, alchemy Intellect, cookery Wits, building Might,
   artifice Intellect, jewelcraft Agility, enchanting Intellect, scribing Agility; `licenses.yaml`), primary
   tag the base's `make.deed_tag`, DC = the target rung's obstacle tier (worn and common **Easy**, fine
   **Moderate**, masterwork **Hard**, wondrous **Very hard**), levers: the trade's tools (Precision; required
   — without them the work is improvised), a master's workshop (Precision, when a fact names one), a recipe
   for the property being worked (Amplifying). Stakes **Risky**: a failure ticks spoilage by U(S2) = 1 and
   takes one cost (`cost.time` or `cost.gear` on the materials, 01's menu); a critical failure ticks
   spoilage by U(S3) = 2. A near miss may be taken as success at a cost (01): progress at the framed reach,
   and a `cost.time` that ticks no spoilage.
4. **Progress fills first:** the item is made at the target rung → `generate(gen.craft, material set,
   circumstance, degree = the completing beat's degree, {target, bias, recipe})`. **Spoilage fills
   first:** the work is ruined: the primary material is consumed, the reagent is kept, the time is spent.
5. **Leaving it:** a project left untended loses 1 progress per week; at 0 it is void and the materials are
   kept.
The grade's obstacle cap (trained Hard, expert Very hard, master Legendary; `licenses.yaml#grades`) is why a
trained smith cannot attempt a wondrous blade: its DC is above what the license lets succeed. *Pace*
(T-08-14, `08-craft-sim.py`, 20,000 projects per row): a trained smith (Might +3, competence +2, tools +2 =
**+7**) completes a masterwork 48% of the time (62% with a recipe), in about 5 steps when it completes; with a
master's workshop (+9) 74%; an expert (+10 to +12) 85–90%. A wondrous work at an expert's +11 completes 33%
(57% with a recipe); a master's +13, 62% (81%). Fine work is safe from +5 (89%), common work always. Masterwork
is "Hard: challenges a practiced professional" (T-00-5) and the numbers say so [R4 §9 08 #5 "crafting as an extended task (clock)"; 05.8.2; DL-08-16].
6. **A project is a craft contest** `[revision: I-003]` (03.4.3). Each step's `challenge_band` is at least
   the work's **type-tier** (08.6.1), so a wondrous blade of dragon steel is a band-5 deed though its steps are
   Very hard, the highest DC a work sets. A step on a work whose material set includes an **irreplaceable
   material** (rarity band 4, or a harvested part that carries a named source's provenance) is framed
   **Dire**, and its `cost.gear` on that material is **ruinous** (03.4.5): the steel cannot be bought again.
   A step taken while the spoilage clock stands one segment from full is **at the brink** (a crisis, 03.4.5).
   Steps run in the week planner are a montage and yield counted evidence only (15.10.6); the player may
   instead have the steps of a fine or better work **played as a scene** (15.10.6's "a scene framed inside
   downtime is play"), and the completing beat of a masterwork or wondrous work is always played: those
   beats are judged deeds like any other. *Why:* before this, every step was Risky and no work rose above
   band 4, so a smith's calling could not meet tier 3's crises or tier 5's great deeds at all
   (`04-recog-parity.py`: tier 3 never reached in 90 sessions; with this rule tier 3 at session 18 and
   tier 5 at 45, beside the archer's 19 and 51) [DL-08-30].

**08.6.5 Commissioning.** `[D]` An NPC crafter's availability follows the settlement (`economy.yaml#buying`):
a village has trained crafters (common and fine), a town trained and expert (masterwork), a city expert
and, by Oracle question at Unlikely, a master (wondrous). The engine runs the project with the crafter's
modifier (09/12's NPC template for the trade: trained +5, expert +8, master +11) as engine fortune checks
(01.6.7), one per tick period; the player sees the progress clock (it is public) and receives the item when
it fills. **Price** = the materials (supplied by the player, or bought by the crafter at list) + the
crafter's **weekly wage** (`economy.yaml#craft_wages`: trained 10, expert 25, master 60) × weeks of work,
rounded up to whole weeks + **1 notch** of the item's price band (08.8.2), half paid up front. Spoilage
means the crafter starts over at their own cost once; a second spoilage returns the materials and the
deposit. The player names one **bias tag**, which is the commission's whole say over its properties; a
known recipe the player brings (a pattern book) lets them name one property exactly.

**08.6.6 What the completing beat decides.** `[D]` The made item's rung is the target rung (completion) —
quality-tier is the *declared ambition*, not the luck of one roll. The degree of the **completing beat**
then applies 00.11.3's degree effects: **Greater** on a critical success (one property +1 tier, may exceed
the tier cap by 1; for an improvised item the rung rises one instead, common → fine); **Flawed** when the
spoilage clock stands at its last-but-one segment or later at completion (3 of 4; 5 of 6): one property's
slot holds a flaw instead (28% of completed masterworks at +7, 13% at +11, T-08-14) (the primary material's listed flaws, else engine-drawn among `item_properties.yaml#flaws`
that apply). Every made item records `provenance.maker` and `domain: gen.craft` (03's `cnt.made` reads
them, weighted by the quality index).

**08.6.7 Repair.** `[D]` *Anchor: yes.* (01.13.4; 08.1.9.)

| State | Who may mend it | Frame | Result |
|---|---|---|---|
| damaged, crude | anyone (`verb.handle` "crude making and repair", G1) | Easy, 1 interval, stakes Safe | `serviceable_until_rest_long`: works fully until the next `rest_long`, then damaged again |
| damaged, lasting | the base's make.license (any grade) with tools | Moderate (masterwork Hard; wondrous Very hard; storied Legendary), 1 hour, materials worth 1 notch of the item's band | intact |
| broken | the base's make.license at a grade whose cap reaches the DC, with tools and a workplace | a project clock of **4**, DC by rung as above, the base's make time per tick, materials worth 2 notches | intact; a relic's license and bound ability wake again |

`ab.field_patch` and similar abilities are faster crude repairs (05). A commissioned repair costs
`svc.repair` (1 notch damaged, 2 notches broken). An item repaired from broken keeps every property; nothing
in a repair adds one.

**08.6.8 Salvage.** `[D]` *Anchor: yes.* Breaking an item down for what it is made of: one beat, 1 hour,
verb.handle under the base's make.license (or improvised: +5 DC, half yield), DC Moderate, stakes Safe. On a
success the item is destroyed (it must be the bearer's, intact or damaged, not storied) and yields:
(a) its primary stock material, one unit per 2 load of the base (minimum 1); (b) for an item with a
signature, one unit of **residuum** (`mat.residuum`: an essence whose gates are the signature property's
gate tags and whose rarity band is the item's signature tier − 1, minimum 1) — the item's identity, kept for
a new making; (c) on delivered reach 3+ with the property's craft license, the fact `knows_recipe: <the
signature property>` (Diablo IV's Codex of Power: once found, a power becomes a reusable pattern). A relic's
bound ability is not salvaged (abilities are learned, 05.8.5). Salvage is the release valve for 08.2.7's
surplus: the sixth masterwork trophy becomes material and knowledge, not coin [R3 08.10, A-10; DL-08-17].

**08.6.9 Recipes.** `[D]` A recipe is the fact `knows_recipe: prop.*` on a character. It comes from a
pattern book (08.4.6), a salvage (08.6.8c), a mentor's training week in the property's craft (15; the
mentor must know it), or a crafted completion that is a critical success, which writes the recipe of one
property the crafter chose for it. A recipe lets its holder (a) **name** that property for one slot of any
project whose gated pool contains it (fill method `recipe`: deterministic), and (b) cite it as an
**Amplifying** lever on that project's steps. A recipe does not open a property the materials do not gate:
the troll-hide recipe for *Knitting flesh* still needs troll hide or another part that gates it.

**08.6.10 Enchanting: the one worked property.** `[D]` Enchanting adds **one** property to an existing item
— its `worked` property — and never more than one in the item's life (PoE2's single crafted modifier, R3
A-23):
- **Requirements:** the item is fine or better with an open magnitude slot (a kit's fine item, a
  masterwork whose magnitude slot is empty, a found item whose slot was removed by Flawed); the enchanter
  holds `lic.training.craft_enchanting` **and** a magic training license of the property's branch (an
  elemental property: that element's arcane school or `primal_elements`; a radiant or warding property:
  `divine_*`; any other passive: any arcane, divine or primal license); the enchanter knows `rit.imbue`
  (05.8); a reagent that **gates** the property (a fire gland for an ember property).
- **For a season:** performing `rit.imbue` (05's rite: 6 segments, Hard, 1 hour per step, 2 Focus) seats the
  property until the next `season` boundary (h.08.durations expires it).
- **Lasting:** a crafting project of **8** segments at Hard under `deed.craft.enchanting.imbuing`, a day per
  tick, whose last step is the rite; fill `recipe` if the enchanter knows the property's recipe, else
  `chosen` among the reagent's gated entries.
- **Tier** = min(the reagent's band, the enchanter's grade cap). The property counts toward the item share
  like any other; a worked property that would breach it cannot be chosen (08.2.4).
- A worked property is never a license or a bound power: identity is made, not added.

**08.6.11 Consumables, scrolls and copies.** `[D]` Consumables are made in **batches**: a project of 4
(common) or 6 (fine: the elixirs, antidotes, oils and greater draughts) at a watch per tick yields **three**
doses of one consumable base item, consuming its materials at half its price per dose. A **scroll** is
inscribed by a holder of `lic.training.craft_enchanting` who holds or has a text of the ability: a project
of 6 at Hard, a day per tick, materials worth 25 + 25 × the ability's `min_tier` coins (`price_rule` in
base_items.yaml), yielding one scroll (08.4.5). A **copy** of a teaching text is made under
`lic.training.craft_scribing` (copying): a project of 6 at Moderate, a day per tick, with the original at
hand and the text's language; the copy teaches as the original does.

**08.6.12 Improvised making.** `[D]` Anyone may make crude things with Handle (01.18.14 "crude making and
repair"): a club, a sling, a spear from a sapling and a knife, a travois, field arrows (10 per watch), a
torch from resin and cloth, a snare. Improvised projects use the same clocks with the crude fallback's +5
DC and Limited reach cap; the rung is at most common (fine only by Greater), the fill weighted, and the
item is `worn` when the completing beat was a success at a cost. *Why allow it:* goal 1 — a stranded
character can always make *something* — and the rung cap keeps it from replacing the trade.

**08.6.13 Building.** `[D]` Structures are crafting projects under `lic.training.craft_building`: a
holding's `build_weeks` (economy.yaml) become one 12-segment progress clock per 13 weeks of building or
part of 13, ticked weekly by the master builder's step (engine fortune checks for NPC builders), with
workers paid at `wage.porter`/`wage.skilled`. 11 owns what a holding does once it stands.

### 08.7 Gifts: patron, order and faction boons (`gen.gift`)

**08.7.1 What a gift is, and who decides to give it.** `[D]` A gift is an item (or, from a power, an
ability) produced by `generate(gen.gift, giver, circumstance, none, options)`. This chapter decides only
**what** is given. **Whether** anyone gives is never this chapter's: a faction's reward for a thread is 11's
World Turn or thread completion; an NPC's gift is 15's (standing, bargains); an authority lending an item is
04.11.3's. The pool is gated by the **giver**: a faction's `org_tags` and its patron deed tags (11), an
NPC's `role_tags` (12), a power's creature and deed tags (13) [00.11.1; R3 08.15; R6 V13].

**08.7.2 The gift circumstance.**

```
### 08.7.2  Gift circumstance: what does the gift answer?           [J:enum] [D]
Trigger [T]:        a giver's decision to give, recorded by 11, 15 or 04.11.3 (a fact gift_due.<giver>)
Loads in:           situation.social, situation.downtime
License check:      none
Decisions (J):      1. CIRCUMSTANCE [J:enum] (gen_gift.yaml#circumstances; cites thread, commitment
                       or standing fact ids)
                       earned - true only when a thread, a commitment or a bargain fact names a reward
                         owed to the PC by this giver and the PC has met its terms. False for a gift of
                         goodwill with nothing owed (favored); a gift that creates a NEW obligation
                         (bargained).
                       favored - true only when the giver's standing toward the PC is +2 Friendly or
                         higher and the gift is given unasked or on a simple request. False for a reward
                         owed (earned); anything with a price attached (bargained). DEFAULT when uncertain.
                       bargained - true only when the PC accepts a new obligation in return, written as a
                         commitment fact BEFORE the gift (an oath, a service owed, a pact; 11). False for a
                         debt already owed to the PC (earned).
Computation [D]:    earned -> masterwork, chosen fill; favored -> masterwork, signature fill (the
                    giver's boon_signature placed, magnitude weighted); bargained -> wondrous, chosen
                    fill. The giver's boon_signature (11/13; default: the default signature of its
                    first creature tag) is ALWAYS eligible for its own gifts whatever the gate tags,
                    subject to base kinds and tier: it is the giver's identity. Tier cap = the giver's band (a
                    faction's tier 0-1 -> 1 ... 5+ -> 5; an NPC's or power's threat band).
Stakes:             none (no roll; degree none)
State writes:       the gift item (or ability); provenance gen.gift; fact gifted_by: <giver>
Narration may not imply: properties the output does not hold; that the giver's favor is a debt the PC
                    owes (unless bargained)
Worst case (J):     favored vs earned: the giver's signature placed instead of a choice among three,
                    same rung (class i); bargained wrongly chosen: legal only if the commitment fact was
                    written first, which the player saw and accepted (class ii)
Examples:           inside earned: the Wardens promised "a blade from our armory" for clearing the
                      barrow (thread fact); the barrow is cleared -> earned: masterwork, the player
                      chooses among three.
                    boundary favored: the Wardens' captain, Friendly, gives Wren a cloak for the road
                      unasked -> favored: masterwork carrying the order's boon signature.
                    boundary bargained: the hill spirit offers its token if Wren swears to keep the
                      spring clean (commitment written first) -> bargained: wondrous.
                    tempting non-example: "they like me, so they owe me a reward" -> standing is not a
                      debt; favored at most, and only if the giver chooses to give (11/15).
Anchor:             no
Basis:              [00.11.1 gift domain] [R3 08.15] [R6 V13 patron] [05.8.7] [DL-08-18]
```

**08.7.3 Abilities as gifts.** `[D]` Only a **power** (a `creature.spirit`, `creature.fiend` or celestial
entity, or a keeper of `deed.divine` or `deed.primal`, 13) may give an ability. The output is one ability
from `gen_item_ability.yaml#pool` whose gate tags match the giver's deed tags, granted straight into the
**acquired** partition as `provisional` at rank 1 (05.8.7), possibly with the giver's condition as a
commitment fact. It is the giver's power given, not a relic: it is held, not borrowed, so it carries no
relic surcharge, and evidence from its use counts normally (a gift of power is how some callings begin,
04.11.3's V13). An institution (crown, guild, order) never gives an ability; it gives items, ranks (11) and
training (05.9) [05 Interface request (g); 04.11.3].

**08.7.4 The gifted base.** `[D]` The giver names the base by its customary gift (an order's blade, a
guild's ring, a temple's amulet; 11/13 record it as `boon_base`), or the player names an item tag the giver
plausibly has (`[J:flag]` "Would this giver plausibly own such a thing?" true only when the giver's role or
wealth implies it; uncertain → the customary gift; *worst case:* a different base of the same rung, class
i). A gift is fully unsealed to its recipient (the giver says what it is). Selling a gift the giver learns of
is a `conduct.loyalty` event with the giver (03, 11).

### 08.8 The economy

**08.8.1 Coin.** `[D]` The one currency is the **coin**: one day's plain food and a bed in a common room
(02's assumed unit, confirmed; `economy.yaml#currency`). Coin is a quantity on the character, changed only by
`update_quantity` with a reason. There is no smaller unit: anything worth less than a coin is sold by the
**lot** (5 torches, 2 days' trail rations, 10 candles, 20 sling bullets, 2 flasks of lamp oil for 1 coin),
which keeps every price an integer (SG-23). One hundred coins weigh one load unit [DL-08-19].

**08.8.2 Price bands and notches.** `[D]` Every price falls in a **band**, and each band has a fixed
**notch**: the step by which haggling, gluts and fees move a price (`economy.yaml#price_bands`). Notches are
looked up, never computed, so no percentage ever appears.

| Band | Name | Price | Notch | Examples |
|---|---|---|---|---|
| 0 | trifle | 1 | 1 | a lot of torches; a meal; a ferry |
| 1 | cheap | 2–5 | 1 | a dagger, a hand axe, a padded jack, boots |
| 2 | modest | 6–25 | 2 | a sword, leather armor, a healing draught, a shortbow |
| 3 | costly (**valuable**) | 26–125 | 10 | mail, a longbow, a fine sword, a riding horse, a T1–T2 masterwork trophy |
| 4 | precious | 126–625 | 50 | splint, plate, a courser, a T3 masterwork |
| 5 | treasure | 626–3,125 | 250 | a destrier, a manor's furnishings, a T4–T5 masterwork, a wondrous item |
| 6 | fortune | 3,126+ | 1,000 | a ship, a keep, a storied relic |

Band 3 is the **valuable** band 07.6.1's `rob` row takes (07 Interface request).

**08.8.3 The list price.** `[D]` An item's list price = base price × its rung's multiplier (worn ×½,
rounded down, minimum 1; common ×1; fine ×3; masterwork ×10; wondrous ×30) + the sum of its properties'
values by tier (**20 / 50 / 125 / 300 / 750** for tiers 1–5; a bound power ×2; a license property as its
tier) − 1 notch for a known flaw. Storied items carry an authored price. A fine dagger lists at 6; a
masterwork fang charm with a tier-2 signature and a tier-1 magnitude property at 1×10 + 50 + 20 = **80**.

**08.8.4 Buying.** `[D]` A trader's **asking** price is list + 1 notch. What can be bought depends on the
settlement (`economy.yaml#buying`): a camp or waystation sells band 0–1 goods, `worn` and `common`; a
village up to band 2, fine goods on a weekly 1-in-6; a town up to band 3, fine goods, special stock of rarity
band ≤ 2, masterwork only by commission (08.6.5); a city up to band 5, special stock ≤ 3, and a **curio
dealer** with d4 property items each week (generated as `scavenged` finds at the region's band, sold at list
+ 2 notches). Whether a particular trader has an unlisted thing is an Oracle question at **Unlikely** (one
band above the settlement's limit) or **Remote** (two), asked before the scene's narration claims it
(00.12.7).

**08.8.5 Selling.** `[D]`
- **Mundane items** sell for half of list (×½), minimum 1.
- **Trade goods** sell at list where the goods are scarce and at list − 1 notch where they are common (which
  is which is a fact of the settlement, 13; uncertain → common).
- **Treasure** (gems, art, trade bars) sells at list − 1 notch to a jeweler, broker or temple in a town or
  city; half of list anywhere else.
- **Property items** sell for half of list, and **only** through `clk.find_buyer` (6 segments, kind
  `project`, public; ticks per `week`: town 1, city 2, plus the delivered reach of one Talk beat under
  `deed.influence.trade` per week); a village or camp never buys them. A curio dealer buys at the clock's
  completion.
- **Market depth:** a settlement pays the PC at most camp 10 / village 30 / town 150 / city 750 coins per
  week for anything but trade goods; past it, buyers are gone until `h.08.markets` resets them.
- **Glut:** each sale of the same base item or trade good in one settlement in one week lowers its sale
  price there by one notch, recovering one notch per week.
- **The labor cap** (08.8.9): what the seller made sells for at most its materials' price + the maker's
  craft wage for the days worked.

**08.8.6 Lifestyle and upkeep.** `[D]` Handler `h.08.upkeep` (`week`, phase 4) charges, for every week in
which the PC spent any day in a settlement, the **lifestyle** they keep there (`economy.yaml#lifestyles`):

| Lifestyle | Coins / week | Rest site (07.8) | Social fact |
|---|---|---|---|
| destitute | 0 | rough; a town long rest is at best partial | *shabby*: a Precision snag on Talk where appearance matters |
| poor | 4 | camp | none among common folk; a snag at court |
| modest | 7 | haven | none |
| comfortable | 14 | haven | *means*: citable where credit matters |
| wealthy | 35 (one servant) | haven | a Precision lever on Talk with merchants and officials where means matter |
| noble | 100 (a household of four) | haven | a Precision lever on Talk at court; expected of rank 2+ in a crown faction (11) |

A venture week costs supply instead (10). The handler also charges mount stabling, holdings' upkeep and
any coin wages 16's handler does not. **Shortfall:** unable to pay, the lifestyle falls one rung for that
week, with the lower rung's effects; debt beyond that is 11's. **The Unit of wealth:** for this character, a
Unit = the weekly cost of the current lifestyle (minimum 1); a cost of severity S*n* in coin is U(S*n*) Units
(S1 1, S2 1, S3 2, S4 3, S5 4). 03's generosity ground floor is **1 Unit** (03 Interface request): a
comfortable character's gift of 14 coins matters; a copper to a beggar does not [R5 EQ-05; R: https://
bladesinthedark.com/coin-stash; DL-08-20].

**08.8.7 Haggling.**

```
### 08.8.7  Haggle: argue the price                                  [J:flag] [D]
Trigger [T]:        the PC declares a price negotiation with a trader for an item or service
Loads in:           situation.social.bargaining, situation.downtime.commerce
License check:      basic verb: verb.talk (G1)
Decisions (J):      1. ROOM [J:flag] "Is the price negotiable here?" True only when the seller is a
                       trader, crafter or private seller dealing face to face; false for fixed fees
                       (tolls, temple tithes, a guild's posted rate) and for a seller whose refusal fact
                       (15) names the PC. Uncertain -> true.
Computation [D]:    frame: verb.talk, primary tag deed.influence.trade.haggling, against the trader's
                    Wits defense (or Presence, whichever is higher; 15 composes standing and claim
                    plausibility into it), stakes Risky (failure: cost.closed_door at S2 -- the trader
                    holds firm for the day; critical failure: S3 -- will not deal with the PC this week),
                    reach Standard (levers: a rival offer in the same settlement, a glut, Fine cut or
                    Haggler's, the trader's need).
                    buying: delivered reach 0 -> asking stands (list + 1 notch); 1 -> list; 2 -> list - 1
                    notch; 3 -> list - 2 notches; 4 -> list - 3 notches.
                    selling: delivered reach 0 -> the offer stands (half of list); 1 -> half + 1 notch;
                    2 -> + 2 notches; 3 -> + 3 notches; 4 -> list - 1 notch.
                    floor: never below half of list on a buy; never above list - 1 notch on a sale.
                    one haggle per item per trader per day (01's repetition rule).
Stakes:             risky (cost.closed_door), per Computation
State writes:       the agreed price (a fact on the deal); coin and item transfer on acceptance
Narration may not imply: a price the tool did not compute; that the trader will deal again after a
                    closed door
Worst case (J):     ROOM wrongly true on a fixed fee: the PC rolls where no roll was owed, at worst a
                    closed door for the day (class i); wrongly false: the player can name the trader's
                    kind (class iv)
Examples:           inside: Wren haggles for mail at the Ashford smith: list 50 (band 3, notch 10),
                      asking 60; reach 2 -> 40.
                    boundary: the bridge toll at Grey Keep -> fixed: ROOM false.
                    outside: buying a meal at an inn -> band 0, notch 1: haggling moves 1 coin; the DM
                      need not frame it unless the player insists.
                    tempting non-example: "I tell him it's worth half that" -> an assertion (SG-06), not
                      a lever; a lever needs a fact (a rival's lower price, recorded).
Anchor:             yes. Intent verbs: haggle, bargain, beat down, talk up, negotiate a price. Knobs:
                    dc (the trader's defense), stakes, reach_unit (notches).
Basis:              [15 negotiation (owner of the social frame)] [00.3.9 levers] [R7 §4.2] [DL-08-19]
```

**08.8.8 Services, wages and holdings.** `[D]` Prices consumed by other chapters (`economy.yaml`):
- **Services:** common lodging 1/day; private 3/day; stabling 1/day per mount; bath and laundry 1; a
  messenger 1 per travel day; a scribe 1 per letter, 2 per page copied; a sage 10 per question; identifying
  an item 10; a healer's care 2/day; surgery 10; a temple's cure 26–125 by severity (S1 26, S2 40, S3 60, S4
  90, S5 125); a rite performed for hire personal 10 / local 50 / site 250 / regional 1,250 + components;
  repair 1 notch (damaged) or 2 notches (broken); training per week trained 7, expert 25, master 100;
  passage road 2/day, river 1/day, sea 3/day; a ferry 1; a toll 1.
- **Components by price band** (05.8.2's rites): band 1 means a component costing 1–5 coins, band 2 6–25,
  band 3 26–125, bought where its rarity allows (08.6.2) or gathered (10).
- **Wages** (16 consumes; weekly / daily): porter, torchbearer or camp hand (T1) 7 / 1; skilled hand —
  guide, cook, groom, carter (T1) 10 / 2; soldier, scout, sailor (T2) 14 / 2; specialist — trained healer,
  locksmith, hedge-witch (T2) 21 / 3; veteran (T3) 50 / 8 plus a half share of coin found; champion (T4)
  150 / 25 plus a full share, and only for a thread they believe in; legend (T5) never for coin. Crafters'
  weekly wages: trained 10, expert 25, master 60.
- **Holdings** (11 consumes; buy / build weeks / upkeep per week / staff): cottage 150 / 6 / 1 / 0; townhouse
  600 / 12 / 3 / 1; workshop 400 / 8 / 2 / 1; shop 800 / 10 / 3 / 2; tavern 1,500 / 16 / 8 / 3; farmstead
  1,000 / 12 / 4 / 4; watchtower 3,000 / 26 / 10 / 4; manor 8,000 / 52 / 30 / 10; keep 25,000 / 104 / 80 /
  30. Yields are 11's, rolled from `economy.yaml#holdings` (a shop d6 × 5 a week gross in a town, ×10 in a
  city, before wages; a farmstead 20 supply a week in season), and never exceed labor and rents (AI-8).

**08.8.9 Magic never mints wealth.** `[D]` Eight anti-inflation rules (`economy.yaml#anti_inflation`), each
enforced by a tool, not by the DM's restraint:
1. **Conjured is worthless.** Anything conjured, summoned or transmuted carries the fact `conjured: true`,
   has price 0, cannot be sold, and ends with its effect's duration. Turning base matter into precious
   matter is **G4** unless 13's canon allows it, and then the product is conjured. (5e's *Fabricate*
   lets casters "bypass the gold economy"; here no spell can.)
2. **The labor cap.** What a seller made sells for at most its materials' price + the maker's craft wage for
   the days worked: crafting earns a craftsman's living, never a windfall.
3. **Property items** sell for half of list, and only through `clk.find_buyer` in towns and cities.
4. **Market depth** caps the coin a settlement pays the PC per week.
5. **Glut** lowers the price of repeated sales.
6. **Coin enters only through tables:** purses, hoards, wages, rewards (11), sales and holdings' yields —
   never a DM's choice (INV-3).
7. **Item shares cap economic properties:** supply use −1 a day, carrying capacity +4.
8. **Holdings yield** labor and rents, rolled by 11, never chosen.
[R2 08 "magic that bypasses the economy"; R2 #13; R1 08 "wealth is the most fragile state"; DL-08-19]

**08.8.10 Wealth tiers and the treasure curve.** `[D]` + `[N]` Wealth tiers name what a character holds in
coin and liquid valuables: **W1** scraping 0–50, **W2** solvent 51–300, **W3** prosperous 301–1,500, **W4**
rich 1,501–8,000, **W5** magnate 8,001+ (`economy.yaml#wealth_tiers`). The tables are calibrated so that a
character fighting at their own band and living comfortably drifts up about one tier per power band:

| Band | Coin in per session (2 fights; purses, a share of sales, 1 hoard per ~4 sessions) | Comfortable lifestyle per week | Typical tier |
|---|---|---|---|
| P1 (vs T1–T2) | ~10–25 | 14 | W1–W2 |
| P2 (vs T2) | ~25–60 | 14 | W2 |
| P3 (vs T3) | ~100–200 | 14–35 | W3 |
| P4 (vs T4) | ~400–800 | 35 | W4 |
| P5 (vs T5) | ~1,500–3,000 | 35–100 | W5 |

(Derivation: purse means T1 1.5, T2 7, T3 19, T4 53, T5 135 per carrier, about two carriers of coin per fight
from T2 up; hoard means T1 31, T2 110, T3 495, T4 2,200, T5 8,250, one hoard per about four sessions;
property-item sales at half list are capped by market depth.) The sinks that keep the
curve from running away are lifestyle, training fees, commissions and materials, holdings and wages — every
one of them a thing the player chooses, which is the point: money is how a character turns success into
time, help and a home. *Revisit if* a campaign's PC sits two tiers above this table (OEQ-08-4).

### 08.9 Carrying, supply, light and ammunition

**08.9.1 Load and capacity.** `[D]` Every item has a **load** in load units (`weight` in base_items.yaml):
most hand-held things 1; heavy weapons 2–3; armor worn 1 / 2 / 3 (light / medium / heavy), carried 2 / 4 / 6;
light shields 0–1, heavy 2–3; worn clothing, jewelry, coins under 100, and small things 0; supply 1 per 2
units or part (08.9.4); trade goods by their entry. **Carrying capacity** — the one value Might may feed
(00.4.4) — is **10 + 2 × Might** (Might −1 → 8; 0 → 10; +1 → 12; +3 → 16; +4 → 18); `lic.people.great_frame`
counts Might +1 for this only (02 Interface request); items add at most +4 (08.2.2). The engine computes load
on every possession change.

**08.9.2 Burdened and overloaded.** `[T]` + `[D]` Load above capacity → **burdened**: the engine cites the
Precision snag *burdened* on Evade, Sneak and Exert (outside the two-cited count, inside ±4), Move pace is
one step slower (06), and travel pace one step slower (10). Load above twice capacity → **overloaded**: the
character cannot Move or travel holding it all; they may drag one load-unit-heavy thing one band per round
and do nothing else. Dropping things is a free activity (00.12.6). *Why load units and not weights:*
Mausritter and Cairn show a slot budget is something a player reads at a glance and an engine checks
exactly; the numbers sit so that a P1 archer (Might +1, capacity 12) carries bow, quiver, spear, leather,
rope, bedroll and four days' food (1+1+1+1+1+1+2 = 8) with room for loot, while a knight in plate with a
greatsword and kite shield (3+2+2 = 7) and a week's food (4) is near the line.

**08.9.3 What the pack holds.** `[N]` Nothing in the pack is at hand: drawing a pack item in a conflict is
06's action, not a free one; outside a conflict it costs no time.

**08.9.4 Supply.** `[D]` **Supply** is a quantity (10 owns its consumption and want): 1 supply = one person's
food and water for one day. Trail rations sell 2 supply per coin; market food 1 coin per supply in a camp. A
kit's "food ×N" is N supply (02). Every 2 supply (or part) weighs 1 load unit. Mounts eat 1 supply a day on a
venture unless grazing (08.10.2). Items lower a character's daily use by at most 1 (*Waybread*).

**08.9.5 Light.** `[D]` Light sources are goods; 10 runs `h.10.light` and darkness (06's light values):
torches (a lot of 5 per coin; each burns 6 intervals; bright to `band.close`, dim to `band.near`); a lantern
(5 coins; a flask of oil burns 24 intervals; same light; hooded, it can be shut to darkness as a free
activity); candles (a lot of 10 per coin; each burns 6 intervals; dim to `band.close`); a tinderbox lights a
fire or torch in 1 interval (1 hour in rain). A spent source is marked by `h.08.durations`. *Glowing* items
shed dim light to `band.close` and burn nothing.

**08.9.6 Ammunition.** `[D]` Arrows (20 for 2 coins), bolts (20 for 3), sling bullets (20 for 1) are
quantities, one load unit per 20; each shot writes `ammunition −1` (06.4.9); after a conflict half of those
spent, rounded down, are recovered. A quiver of arrows tipped with an oil carries the oil only for its 3
Strikes.

### 08.10 Mounts, vehicles and vessels

**08.10.1 Mounts are items and companions.** `[D]` A mount is bought as an item (`item.conveyance.mount`;
price, carry capacity, travel pace, weekly upkeep) **and** created as a companion entity whose template,
loyalty and harm are chapter 16's (`companion_hint`: threat band, size, combat-trained). It carries its
own load capacity: donkey 20, pony 20, mule 30, riding horse 25, draft horse 40, courser 25, destrier 30 —
its rider not counted. A rider on a mount holds `flag.mounted` (06); only a war mount (courser, destrier;
`item.conveyance.mount.war`) stays steady in a conflict without a Handle beat each round (16 owns the
check: 16.15.4). Trained beasts that are not mounts are bought at their companion template's `price`
(`companions.yaml`, T-16-19: hound 15, war hound 60, hunting hawk 40) and are companions from the day of
purchase; `base_items.yaml` carries no entry for them [integration: IR ch.16 to 08]. Saddle and tack cost 10; riding without them puts a Precision snag on Handle (ride). Barding (light
60, heavy 300) is the mount's armor (reduction 1 / 2) and makes its travel pace one step slower.

**08.10.2 Upkeep.** `[D]` Stabled in a settlement a mount costs its `upkeep_week` (donkey 2, pony 3, mule 3,
riding horse 5, draft horse 5, courser 8, destrier 10) through `h.08.upkeep`; grazing in grassland or
farmland from spring to autumn costs nothing; on a venture it eats 1 supply a day unless the region grazes
(10). An unfed mount's want is 10's and 16's.

**08.10.3 Vehicles.** `[D]` Carts and wagons are items with carry capacity and crew: handcart 15 (pushed by
one), cart 60 (one draft animal), wagon 150 (two; roads only — off-road terrain is G4 for it), sledge 40 (snow
and ice), carriage 4 passengers (two horses, roads). Pace and the terrain they cross are 10's.

**08.10.4 Vessels.** `[D]` Raft (20 load; downstream), rowboat (30; four people), keelboat (150; crew 6),
river barge (300; crew 8), sailing cog (2,000; crew 12). A vessel has a **hull clock** (4 under 100 coins, 6
under 1,000, 8 above): `cost.gear` against it ticks the clock by U(severity) instead of writing damaged or
broken; a full hull clock is foundering (10). Most travelers buy **passage** (08.8.8), not ships.

---

## Procedures

**PR-08-1 Generating loot.** `[D]` (`generate(gen.loot, …)`; 00.11.3 and PR-00-4 instantiated.)
1. **Trigger and source.** On a side's defeat (06.13.3), a body searched, or a found thing searched
   (08.3.1), take the source: the side's highest-band defeated member, the creature, the hoard's keeper, or
   the place. Refuse if no resolved frame id is attached.
2. **Circumstance** `[J:enum]` per 08.3.2, citing the frame and fact ids; default `scavenged`.
3. **Yield and drop check.** Read the archetype's `loot.yield` (default `trophy`); `hoard` → step 11; `none`
   → step 12; `trophy` → d100 against T1 10 / T2 20 / T3 35 / T4 50 / T5 70; a miss → step 12. `always`
   (principal NPCs) → continue.
4. **Rung and slots** from (circumstance, degree): masterwork for decisive, costly and merciful wins; fine
   or common for scavenged finds by the search's degree. Read the fill method (signature / biased ward /
   chosen / weighted). Tier cap = the source's band.
5. **Base** (08.3.6): trophy base → gear → branch default list by d6; signature-honoring when the fill is
   `signature`; one redraw if the base's gated pool is smaller than the slots. Clamp slots to `slot_cap`.
6. **Pool gate** (08.3.4): domains contains loot; gate_tags match source tags ∪ material tags ∪
   `creature.folk` for armaments from folk or undead ∪ place tags for place-gated entries; drop excluded,
   wrong base kind, saturated, over-tier and forbidden-use entries. Log the pool size.
7. **Degree effects:** Greater on a critical success (+1 tier to the first slot filled); Flawed on a
   scavenged critical failure (remove the magnitude slot; the item is created damaged).
8. **Fill** (08.3.8): signature slot (the archetype's signature, or the method's draw among
   signature-eligible entries, never a relic for `signature`); then each magnitude slot (no signature-only
   entries); remove each pick's mod group; weights doubled, recent five halved; `chosen` shows three per slot
   and waits for the player's pick.
9. **Bound power:** if the signature is `prop.bound_power`, run PR-08-4; if its pool is empty, redraw the
   signature once among non-ability entries.
10. **Caps:** sum the item's contributions (base + properties) per family against the item share (08.2.2)
    and per-item caps (08.2.3); a breaching pick is dropped and refilled once, else the slot stays empty.
    Set tiers (signature = cap (+1 Greater), magnitude = cap − 1, minimum 1). Mark sealed properties
    (08.5.3). Compute list price (08.8.3). Write the item with provenance and the log. → step 12.
11. **Hoard:** generate the hoard table's items (steps 4–10 with the table's rungs), roll `hoard_coin` and
    `hoard_goods`.
12. **Always:** purse (08.3.11) for carriers of coin; gear at worn/common; goods 09 lists. Mark each body
    harvestable (08.3.10). Return everything for narration (08.3.13); the DM names, the codex details.

**PR-08-2 The shared fill step.** `[D]` Loot, craft and gift calls share PR-08-1 steps 6–10 with their own
domain filter, source tags (materials + `creature.folk` + provenance for craft; the giver's tags for gift),
fill map and quality map. A craft call's signature is the primary material's provenance signature (08.6.2);
a gift's favored signature is the giver's boon signature. Recency windows are per domain.

**PR-08-3 Harvesting a body.** `[D]` (08.3.10.)
1. Check FRESH `[J:flag]`; list the parts (materials whose `source_tags` match the body's most specific
   creature tags, or 09's override); mark essences, which need a dissection license or the crude fallback.
2. Frame: Handle, `deed.wilds.foraging.harvest`, DC by the rarest part attempted, stakes Safe (Risky in a
   hazard or a hostile scene), time 1 interval or 1 hour.
3. Deliver by reach (1 common parts; 2 + one special; 3 all; 4 all + one pristine); failure common parts
   and spoiled soft parts; critical failure nothing.
4. Create each part as an item with provenance (archetype, tags, band) and rarity band max(listed, band − 1).
   Set `harvest.done` on the body. Record evidence (03).

**PR-08-4 Generating an item's ability.** `[D]` (`generate(gen.item_ability, …)`, 08.4.3.)
1. Inherit source, circumstance and the parent property's tier (3 → rank 1, 4 → rank 2, 5+ → rank 3).
2. Pool gate: absorbed powers whose gate tags match the source's creature tags; techniques whose first deed tag
   matches the source's deed tags or its `source_to_deed` mapping; drop oath- and conduct-gated, passive,
   `adversary_only` and over-tier entries.
3. Fill by the inherited circumstance (`gen_item_ability.yaml#fill_map`).
4. Write `bound_ability {ability_id, rank}` and `relic: true`, `feeds_evidence: false` on the item.
5. On attunement (08.5.2): bind to a free equipped slot (05.2.8) or mark dormant; at use, `use_ability`
   adds the relic surcharge per 05.6.3.

**PR-08-5 Running a crafting project.** `[D]` (08.6.)
1. **Declare:** base item, material set (primary sharing a level-1 material branch with the base; at most
   one reagent), target rung, circumstance `[J:enum]` (08.6.3), bias tag (commissioned), recipe (if any).
2. **Validate:** license and grade cap (trained ≤ masterwork; expert, master ≤ wondrous; improvised ≤
   common); tools and workplace facts (else improvised); materials in hand in the required amount (08.6.2);
   tier cap = min(grade cap, highest material band).
3. **Create clocks:** progress 4/6/8/12 by target; spoilage 4 (6 for wondrous), racing.
4. **Each step** (`advance_time` by the base's `make.time_per_tick`, every boundary runs): frame per 08.6.4
   (license attribute, `make.deed_tag`, DC by target, levers: tools, workshop, recipe; stakes Risky);
   success → progress + delivered reach; near miss → may take success at a cost (`cost.time`); failure →
   spoilage +1 and one cost; critical failure → spoilage +2.
5. **Progress completes:** `generate(gen.craft, …, degree = the completing beat)` (PR-08-2), with Greater
   on a critical completion and Flawed if spoilage stands at its last-but-one segment or later; consume the
   materials; write `provenance.maker`; record evidence and `cnt.made` (03). **Spoilage completes:** ruin;
   primary consumed, reagent kept.
6. **Commissioned:** the engine runs steps 4–5 as fortune checks with the crafter's modifier; charge the
   price (08.6.5), half up front; one free restart after a spoilage.

**PR-08-6 Buying, selling and haggling.** `[D]` (08.8.)
1. Availability: settlement limits (08.8.4); unlisted things → Oracle (Unlikely / Remote) before narration.
2. Price: list (08.8.3) → asking = list + 1 notch.
3. Haggle (optional, 08.8.7): ROOM flag; frame; reach → notches; floor; one per item per trader per day.
4. Pay: `update_quantity(coin, −price)`; transfer the item (`set_position`/possessions). Narration states
   only the totals the tool returned.
5. Sell: mundane ½ list; trade goods and materials at list or list − 1 notch; treasure list − 1 notch in
   town; property items only through `clk.find_buyer`; apply market depth and glut; apply the labor cap to
   the seller's own make.

**PR-08-7 The weekly economy handlers.** `[D]`
- `h.08.upkeep` (`week`, phase 4): if any day of the week was spent in a settlement, charge the lifestyle;
  charge stabling and holdings' upkeep; charge coin wages not charged by 16; on shortfall, drop the
  lifestyle one rung for the week and write a debt fact for 11.
- `h.08.markets` (`week`, phase 6): recover one glut notch per good per settlement; reset market depth;
  restock city curio dealers (d4 items, scavenged at the region band); tick every `clk.find_buyer` by its
  settlement's rate.
- `h.08.durations` (every boundary, phase 1): expire oils (by uses), elixirs and imbued properties (at
  `season`), mark burnt-out light.

**PR-08-8 Identifying and attuning.** `[D]` (08.5.)
1. Attune at a breather outside conflict: check the five-item limit; set `attuned`; unseal all; bind a
   bound power; set `cost_immune` for relics and storied items.
2. Identify without attuning: study (lore.arcana or lore.bestiary; DC by highest sealed tier; reach =
   properties revealed in the player's ranked order; failure locks study until the next `rest_long`), a
   sage's service, or a property's observable firing.

**PR-08-9 Repairing and salvaging.** `[D]` (08.6.7–08.6.8.)
1. Repair: crude (Handle, Easy, 1 interval → serviceable until `rest_long`), lasting (license, by rung, 1
   hour, 1 notch of materials), broken (license, clock 4, 2 notches).
2. Salvage: the bearer's own non-storied item; license or improvised; Moderate, 1 hour; yields stock by
   load, a residuum of the signature, and on reach 3+ with the property's craft license the recipe.

---

## Tables

Tables embedded in Rules are canonical there: **T-08-2** quality ladder (08.1.4); **T-08-4** weapons
(08.1.5); **T-08-5** armor (08.1.6); **T-08-6** other branches (08.1.8); **T-08-7** condition (08.1.9);
**T-08-8** item share (08.2.2); **T-08-9** the math (08.2.6) and item density (08.2.7); **T-08-10** drop
check (08.3.3); **T-08-11** slot contents (08.4.1); **T-08-12** body slots (08.5.1); **T-08-13** repair
(08.6.7); **T-08-15** price bands (08.8.2), lifestyles (08.8.6), treasure curve (08.8.10). The data files are
canonical for every id and number.

**T-08-1 Optional fields 08 adds to its schemas** (SCHEMAS.md lets owners add optional fields; documented
here). *BaseItem:* `kind`, `weapon_weight`, `harm {severity, harm_tags, band_reach}`, `strike_cost`,
`hands`, `weapon_properties` (≤ 2, T-06-7 ids), `deed_tag`, `training_license`, `reload_actions`,
`armor_class`, `reduction`, `carried_weight`, `snags`, `don_time`, `sleep`, `guard_edge`, `shield_class`,
`body_slot`, `intrinsic` (effect refs of the base), `status`, `implement`, `serves`, `grants_lever`, `uses`,
`quantity`, `quantity_name`, `light_source`, `holds`, `effects`, `priority_rank`, `spread`, `conveyance`,
`carry_capacity`, `travel_pace`, `upkeep_week`, `companion_hint`, `crew`, `hull_clock`, `make {license,
deed_tag, time_per_tick}`, `default_for`, `trophy_eligible`, `price_rule`, `note`; top-level
`kit_resolution`. *PoolEntry (item_properties.yaml):* `kind`, `family`, `item_share`, `bias`, `domains`,
`place_gated`, `signature_only`, `relic`, `saturated_by`, per-tier `trigger {hook, chance, params}` and
`limits`, `value_by_tier`; top-level `bias_tags`, `tier_rule`, `chance_rule`, `default_signatures`, `flaws`.
*Material:* `stock`, `harvest`, `weight`, `fallback_signature`, `flaws`, `gated_pool_size`,
`instance_rule`. *gen_*.yaml:* `pool_ref` (instead of an inline pool, pointing at item_properties.yaml),
`trigger`, `drop_check`, `hoard_map`, `degree_effect_rules`, `pool_gate`, `base_selection`, `contract_09`,
`source`, `signature_rule`, `target_rungs`, `grade_caps`, `quality_map_mode` (`relative_to_target` for
craft), `project_clock`, `step_frame`, `materials_consumed`, `who_decides_to_give`, `ability_gifts`,
`chosen_display`, `base_rule`, `anti_minting`, `called_by`, `source_to_deed`, `binding`. *economy.yaml:* the
keys listed in 08.8 and 08.9.

**T-08-3 The property pool at a glance** (`item_properties.yaml`: 210 entries; 76 signature-eligible).

| Family | Entries | Kind | Base kinds | Typical gates |
|---|---|---|---|---|
| Make (keen, balanced, guarding, sturdy, light make, quiet, supple, reinforced, fine cut, deep pockets, master's mark) | 11 | mundane | by entry | `creature.folk`, metals, fine woods, hides |
| Weather (warm, cool, weatherproof) | 3 | mundane | garments, jewelry | furs, frost and fire natures; frozen, arid, wet places |
| Skill edges (16 deed tags: stealth, thievery, tracking, navigation, survival, athletics, arcana, history, bestiary, persuasion, intimidation, insight, performance, trade, investigation, medicine) | 16 | passive | gloves, boots, cloaks, circlets, rings, amulets, instruments, kits | creature natures matching the deed (feline → stealth, canine → tracking, devil → persuasion…) |
| Craft edges (11 crafts) | 11 | passive | trade tools, gloves | dwarves, metals, essences, gems |
| Elemental (9 harm branches × resist, strike, on-hit, hazard, retort) + condition wards (6) | 51 | passive | worn / weapons | elementals, dragons, fiends, undead, horrors, essences, schools of magic |
| Physical resistance (cut, pierce, crush), banes (8 creature kinds), physical on-hits (bleed, stagger, dread, hobble, expose) | 16 | passive | worn / weapons | beasts, giants, constructs, silver, cold iron, faiths |
| Senses, movement, wards, sustain, light, carry, supply, pace, command, lore | 23 | passive | by entry | beasts, spirits, undead, constructs, places |
| Implements (three branches × edge and thrift) | 6 | passive | implements | schools, faiths, druidic orders, witchwood |
| Relic licenses | 18 | license | jewelry, headwear, tools | the people or nature whose capability it is |
| Bound power | 1 | item_ability | any equippable | any creature, deed, org or essence (tier 3+) |
| Creature signatures (one per level-2 creature tag: 45) and place signatures (9) | 54 | passive / mundane | by entry | one designed identity per nature |

**T-08-4 Default signatures** (`item_properties.yaml#default_signatures`; 09 may name another eligible entry).

| Creature branch | Level-2 tag → signature |
|---|---|
| beast | predator → Hunter's sense · herd → Long stride · vermin → Plague-proof · reptile → Shed skin · avian → Keen eye · aquatic → Tide-skin · monstrous → Monster's hide |
| folk | human → Well-made · elf → Starlight craft · dwarf → Deep-forged · halfling → Lucky stitch · orc → War-cry · goblin → Dirty trick · giant → Giant's grip · beastfolk → Pack sense |
| undead | mindless → Bone-ward · ravenous → Hunger's edge · spectral → Grave-sight · sovereign → Crown of dread |
| spirit | fey → Glamour · place → Wayfinder · ancestor → Ancestral counsel · celestial → Halo |
| fiend | demon → Hellfire · devil → Silver tongue · possessor → Iron will · hellbeast → Brimstone hide |
| construct | golem → Unyielding · animated → Guardian weave · clockwork → Precise mechanism · homunculus → Familiar's eye |
| elemental | fire → Ember heart · earth → Stonefoot · water → Tidewalker · air → Windborne · frost → Rime heart |
| dragon | great → Dragonscale · drake → Drake-fire · wyvern → Wyvern sting · serpentine → Coils |
| horror | aberration → Alien ward · ooze → Acid bite · fungal → Spore ward · plant → Thornward · abomination → Dread aspect |
| places | tomb → Tomb-ward · frozen → Snowshod · wetland → Marsh-strider · arid → Sand-veil · forest → Forest-hush · underground → Deep-sight · sea/coast → Tidecaller · ruin → Ruin-lore · road/settlement → Road-luck |

**T-08-5 Flaws** (`item_properties.yaml#flaws`): Heavy (carry −1) · Loud (Sneak snag) · Brittle (cost.gear +1
rung) · Marked (recognizable) · Thirsty (supply +1/day, attuned) · Unwelcome (Talk snag with its kind) ·
Restless (long rest at best partial; spirit and spectral sources) · Binding (cannot unattune until cleansed;
fiend, undead, horror sources).

**T-08-14 Crafting odds** (`rules/_process/simulation/08-craft-sim.py`, 20,000 projects per row; near misses
taken as success at a cost; spoilage 4, 6 for wondrous).

| Target (clock, DC) | Total modifier | Completes | Mean steps when made | Flawed (of made) | Greater (of made) |
|---|---|---|---|---|---|
| common (4, 10) | +3 | 98.5% | 2.3 | 2.4% | 23.6% |
| fine (6, 15) | +5 / +7 / +9 | 88.7 / 95.2 / 98.0% | 3.9 / 3.6 / 3.2 | 12.1 / 6.2 / 2.1% | 7.5 / 21.7 / 33.4% |
| masterwork (8, 20) | +7 / +9 / +11 / +13 | 47.5 / 73.8 / 87.5 / 95.2% | 5.3 / 5.3 / 4.9 / 4.4 | 28.1 / 20.0 / 12.9 / 6.2% | 10.9 / 9.1 / 16.4 / 30.2% |
| masterwork with a recipe (Great reach) | +7 / +9 / +11 | 61.6 / 83.6 / 92.4% | 4.1 / 4.1 / 3.8 | 21.9 / 15.2 / 9.1% | 10.1 / 8.2 / 15.1% |
| wondrous (12, 25) | +9 / +11 / +13 / +15 | 12.9 / 32.5 / 62.4 / 86.4% | 8.4 / 8.4 / 8.4 / 8.0 | 31.3 / 26.0 / 18.4 / 10.2% | 18.6 / 13.6 / 10.8 / 8.5% |
| wondrous with a recipe | +9 / +11 / +13 | 32.0 / 56.7 / 81.2% | 6.2 / 6.1 / 5.9 | 23.4 / 17.7 / 11.2% | 13.4 / 10.4 / 8.3% |

Reference crafters: a trained crafter with a +3 attribute, +2 competence and tools is **+7**; with a
master's workshop **+9**; an expert (tier-3 calling competence +5) with tools **+10**, with a workshop
**+12**; a master (+6, attribute +4) with tools and workshop **+14**.

**T-08-16 Loot simulation results** (`rules/_process/simulation/08-loot-sim.py`, seeded; output in
`08-loot-sim-output.txt`; 26 reference archetypes from T1 rabble to T5 dragons, eight place contexts,
circumstances decisive 45% / costly 20% / merciful 10% / scavenged 25%, kill degrees critical 20%).

| Measure | Result | Target / reading |
|---|---|---|
| Drop rate by source band (d100 check) | T1 8.1 · T2 21.6 · T3 35.1 · T4 51.3 · T5 75.9% (3,042 events to 1,000 drops) | matches 10/20/35/50/70 within sampling |
| Rungs of 1,000 property drops | masterwork 759 · fine 134 · common 107 | wondrous only from hoards, gifts, crafts |
| Properties per item | 0: 107 · 1: 156 · 2: 737 | masterwork with an empty slot 22 of 759 (2.9%) |
| Property kinds | passive 1,299 · mundane 176 · item ability 140 · license 15 | |
| Relics | bound power 14.0%, any relic 15.5% of drops (about 1 masterwork in 5.3) | rare enough to matter; common enough to find |
| Gated pool size per drop | min 3 · median 9 · max 18 | every drop had a choice |
| 09 contract (pool ≥ 3 at tier 1 on every base) | 25 of 26 archetypes pass; the exception is a T4 aberration's charm at tier 1 (moot) | 09 re-runs on its bestiary |
| Same magnitude property as the previous drop (200 decisive drops per archetype) | mean 13.5%; worst clockwork sentinel 31.7%, slime 25.6% | OEQ-00-5 target ≤ 15% met on the mean; narrow natures repeat (OEQ-08-1) |
| Identical whole item to the previous drop | mean 3.9%, max 14.1% | |
| Item-share breaches caught and refilled at generation | 16 in 1,000 | compliance after generation 1,000 / 1,000 |
| Five attuned items of a realistic haul exceeding a share without the E4 clamp | harm edge 19.4% · edge 18.4% · reduction 26.6% of characters | the clamp binds for about one character in five: the choice of five is real |
| Crafting check: troll-hide coat, commissioned, bias ward, trained (cap 2) | pool 10; magnitude picks Guarding 22%, Crush-proof 18%, Reinforced 16%, Sturdy 13%, Knitting flesh 10% | the bias steers; it does not dictate |

---

## Worked examples

Wren is 00's continuous character *(sheet illustrative; ch.02 owns creation)*: Might +1, Agility +3,
Endurance +1, Wits +2, Intellect 0, Presence 0, Resolve −1; competence `deed` +1, `deed.wilds.tracking` +2,
`deed.martial.archery` +2; training licenses `wilds_tracking` and `martial_archery` (trained); capacity
10 + 2 × 1 = **12** load units; comfortable lifestyle in Ashford (14 a week). Archetype numbers marked
*(illustrative; 09 owns)*. Every pool below was computed from the shipped data by `08-loot-sim.py`'s
`gated_pool` function.

### WE-08-1 A kill becomes a drop, end to end (a giant spider)

*Situation.* Under the Ashford mill, Wren fights a giant spider (`arch.giant_vermin`, `adv.giant_spider` in 09's bestiary *(numbers illustrative; 09)*:
`creature_tags [creature.beast.vermin.arachnid]`, `harm_tags [harm.venom.poison]`, T2, `yield: trophy`,
`purse: none`). Her last shot: d20 13 + 5 = 18 vs Guard 15 → success; the spider is defeated (`on_defeat`
carries frame #417). She was never below half Vitality.

1. **Trigger** (08.3.1): `conflict_end`; one defeated side (the spider) → one loot call.
2. **Circumstance** `[J:enum]`: her own resolved beat defeated it; never Staggered; no lethal frame →
   **decisive** (cites frame #417). Fill **signature**.
3. **Drop check** (08.3.3): T2 trophy → d100 = **14** ≤ 20 → a property item drops.
4. **Rung:** decisive + success → **masterwork** (1 signature + 1 magnitude). Tier cap **2**.
5. **Base** (08.3.6): no trophy base from 09; beast defaults [charm, cloak, leather armor]; the signature
   (`default_signatures[creature.beast.vermin]` = **Plague-proof**, base kinds: worn things) accepts all
   three; d6 = **2** → the charm (`bi.charm`, slot cap 3).
6. **Pool gate** (08.3.4) on `bi.charm` at cap 2 — seven entries: Venom-warded (w3), Venom-proof hazard
   (w2), Pierce-proof (w2), Darksight (w3), Tremor-sense (w1, min tier 2), Cave-eyes (w1, license,
   signature-only, min tier 2), Plague-proof (w3, signature). (No weapon entries: a charm is not a weapon;
   no Spider-grip: its min tier is 3.)
7. **Signature slot:** Plague-proof at tier **2** → `eff.harm_reduction` 2 against `harm.blight.disease`.
8. **Magnitude slot** at tier 2 − 1 = **1**: excluded are Plague-proof's group (resist_blight), Cave-eyes
   (signature-only) and Tremor-sense (min tier 2 > 1). Weights doubled; Venom-warded was produced two loot
   draws ago (by the river serpent) and is halved: Venom-warded 3, Venom-proof 4, Pierce-proof 4, Darksight
   6 → total 17. The engine rolls 1–17 = **13** (bands 1–3 / 4–7 / 8–11 / 12–17) → **Darksight** tier 1.
9. **Caps:** item contributions: reduction `harm.blight.disease` 2 (share 3), one lever (share 1 per roll).
   Pass.
10. **Output:** `item.i0211` — base `bi.charm`, **masterwork**, signature [Plague-proof T2] (apparent: "a
    spider's fang, faintly sour"), magnitude [Darksight T1] (**sealed**), provenance {arch.giant_spider,
    decisive, success, tier cap 2, loc.ashford_mill}. List price 1 × 10 + 50 + 20 = **80** (band 3).
11. **Harvest** (08.3.10): fresh `[J:flag]` true (killed this hour). Parts: chitin (band 1), bones (1), sinew
    (1), spinner's silk (2), venom sac (2, an **essence**). Wren holds no dissection license, so she leaves
    the sac (its crude fallback would cap reach at Limited: common parts only). Frame: Handle, Agility +3,
    competence floor +1 → **+4**, DC Moderate 15 (silk, band 2), stakes Safe. d20 = 14 → 18, **success**,
    delivered reach 2 → the common parts plus one special: **spinner's silk**. Items created with
    provenance; `harvest.done` set.
12. **Narration:** "Among the husks you find one fang worth keeping, still sour with its venom. The silk
    comes away in a sticky skein." The codex shows the charm: masterwork, Plague-proof (reduce disease
    harm 2), one sealed property, 80.

*Boundary pairs.* (a) **Costly:** had the bite dropped her to 0 Vitality before the shot, the fill is
biased toward ward: the signature-eligible entries are Plague-proof (w3, ward → ×3 = 9) and nothing else at
cap 2 but Cave-eyes (w1, min tier 2: eligible at 2 → weight 1) → Plague-proof 90%, Cave-eyes (a relic
license, `lic.people.cave_eyes`) 10%. (b) **Drop check miss:** d100 = 63 → no property item; the harvest
still happens. *Tempting non-example:* "It was a venomous spider, so the charm should protect me from
poison" — Venom-warded was in the pool but was not drawn; the narration may not imply it (INV-2).

### WE-08-2 A weapon crafted from a monster's hide (a wyvern-scale whip)

*Character.* Tamsin, a leatherworker *(illustrative)*: Agility +3; `lic.training.craft_leathercraft`
(trained), competence `deed.craft.leathercraft` +2; her own bench and tools in Ashford (facts
`tamsin.workshop`, `tamsin.tools.leatherworker`). She has two wyvern-scale parts (harvested from a T4
wyvern: band max(1, 4 − 1) = **3**, provenance `arch.wyvern`) and a wyvern venom sac (band 3).

1. **Declare:** base `bi.whip` (material tag `material.hide.leather`; scales are `material.hide.scale`:
   same level-1 branch, accepted), primary = the scales, reagent = the venom sac, target **masterwork**.
2. **Circumstance** `[J:enum]`: her license, her tools, her workplace → **crafted** (fill: chosen).
3. **Validate:** trained may target masterwork; tier cap = min(trained **2**, materials' band 3) = **2**.
   Materials: masterwork consumes ×2 the base price (3 × 2 = 6 coins' worth): two scale parts (4 each) =
   8 ≥ 6. ✓
4. **Clocks:** progress **8**, spoilage **4**. Step frame: Handle under the license, Agility +3, competence
   +2, tools lever +2 → **+7** vs Hard **20** (needs 13: success 40%, near miss 15%); a day per tick.
   - Day 1: d20 15 → 22, success, reach 2 → **2/8**.
   - Day 2: d20 9 → 16, margin −4, failure → spoilage **1/4**; cost `cost.time` S2 (a day spent recutting).
   - Day 3: d20 18 → 25, success → **4/8**.
   - Day 4: d20 11 → 18, margin −2, **near miss**: she takes success at a cost (`cost.time`, no spoilage) →
     **6/8**.
   - Day 5: d20 **20** → 27: success, natural 20 steps up → **critical success**; reach 2 + 1 = 3 → **9/8:
     complete**. Spoilage 1 (below 3) → not Flawed; the completing beat is critical → **Greater**.
5. **Generate** (`gen.craft`, PR-08-2): source tags = scales' gates + venom sac's gates + `creature.folk` +
   the wyvern's provenance tags. Pool on `bi.whip`: Keen, Balanced, Sturdy, Light make, Master's mark,
   Ember-forged, Ember-touched, Venom-forged, Venom-touched, Spell-forged, Spell-touched, Dragon-bane, Wyvern
   sting (Bound power is out: min tier 3).
6. **Signature:** the scales' provenance signature = **Wyvern sting**, at tier 2 + 1 (Greater) = **3**: on a
   hit whose d20 shows **17–20**, the creature hit is poisoned (S2) for the scene. Its mod group is
   `on_hit`, which removes every other on-hit entry (08.2.3).
7. **Magnitude** (chosen, tier 1): the tool draws three by weight — **Keen**, **Venom-forged**, **Sturdy** —
   and Tamsin picks **Keen** (+1 harm with the whip; the whip is not versatile, so the item share of harm
   edge is free).
8. **Output:** a masterwork whip, signature [Wyvern sting T3 (Greater)], magnitude [Keen T1]; maker Tamsin;
   list 3 × 10 + 125 + 20 = **175** (band 4). 03's `cnt.made` fires with weight 4 (the masterwork index).

*Boundary pairs.* (a) **Commissioned** by Wren from Tamsin: the same clocks run as engine fortune checks at
Tamsin's +7; Wren names one bias (`strike`), so the magnitude draw weights strike entries ×3 instead of
showing three; price = Wren's materials + trained wage 10 × 1 week (5 days rounds up) + 1 notch of band 4
(50) = **60 coins**, 30 up front. (b) **Improvised** in camp with a knife: no bench → improvised: +5 DC (25),
reach capped Limited, rung capped common → a serviceable scale whip with no properties at all; the
wyvern's identity is not unlocked without the craft. *Tempting non-example:* "It's wyvern hide, so the whip
should resist fire" — fire resistance is not in this whip's pool (it is a weapon; resistances are worn
things), and the signature is fixed by provenance.

### WE-08-3 A relic lends an off-identity capability (a demon's ring of fire)

*Situation.* In the ash-pits east of Grey Keep, Wren beats a lesser demon (`arch.lesser_demon`
*(illustrative)*: `creature.fiend.demon.lesser`, `harm.fire.flame`, T3). At 2 Vitality it yields; Wren,
against her companion's advice, lets it go back to the pit (fact `mercy.ash_imp`).

1. **Circumstance:** merciful (it yielded, she spared it). Fill **chosen**; rung masterwork; tier cap **3**.
   Drop check: d100 = 22 ≤ 35 ✓.
2. **Base:** fiend defaults [weapon, ring]; d6 = 4 → **ring**. Signature-eligible entries for a ring: Hellfire
   is weapon-only (excluded); the only signature-eligible entry left is the **Bound power** (min tier 3 ≤ 3).
   The tool shows it; Wren takes it.
3. **Item ability** (PR-08-4): source `creature.fiend.demon.lesser` → absorbed powers gated on fiends: Dread
   Gaze; techniques via `source_to_deed[creature.fiend]` → `deed.arcane.fire`, `deed.divine.pact`,
   `deed.influence.intimidation`: Flame Lance, Fire Shroud, Cow, Break the Will, … Chosen: the tool shows
   **Dread Gaze**, **Flame Lance**, **Cow**; Wren picks **Flame Lance** at tier 3 → **rank 1**.
4. **Magnitude** (chosen, tier 2): she picks **Ember-warded** (reduce fire harm 2).
5. **Output:** a masterwork ring, relic: bound [`ab.flame_lance` rank 1], magnitude [Ember-warded T2];
   `feeds_evidence: false`; list 5 × 10 + 250 (a tier-3 bound power ×2) + 50 = **300** (band 4).
6. **Attunement** at the next breather: attuned 1 of 5; Flame Lance binds to equipped slot 1 of 4;
   `cost_immune` while attuned; everything unsealed.
7. **Use, two days later**, against a bandit at `band.near`: G2 (held through the equipped partition). Cost:
   rank 1's **1** Focus **+1 relic surcharge** (Wren holds no `lic.training.arcane_fire`) = **2** (05.6.3).
   Check: Intellect 0 + competence on `deed.arcane.fire.blast` — none, so the floor **+1** — vs Guard 13:
   needs 12 (45%). Success → Moderate fire harm (3) and burning. **No evidence** toward `deed.arcane`
   (00.11.5); the shot at the bandit records nothing toward a calling.

*Boundary pairs.* (a) **Ash**, 05's hedge-taught fire sorcerer (holds `lic.training.arcane_fire`), wears the
ring: **no surcharge** (1 Focus), and her own fire competence applies — but if she already holds Flame Lance,
the ring's copy is **dormant**: a spare (05.2.9). (b) **A license relic:** a clockwork sentinel's costly
drop at T2 carries **Lock-whisper** (`lic.training.guile_thievery` at trained, no competence). At 00's Grey
Keep archive door (WE-00-3), Wren is now **G2** instead of G3: Agility +3, competence floor +1, thieves'
tools Precision +2 = **+6** vs the guild lock's Hard 20 (35%) — legal, not good, and nothing she does with
it teaches her thievery. *Tempting non-example:* "I've cast Flame Lance thirty times now, so I'm becoming a
fire sorcerer" — relic use feeds no calling; to become one, she finds a teacher (05.9).

### WE-08-4 A merchant negotiation that touches prices (Ashford market day)

*Situation.* Ashford is a town (band ≤ 3 goods, special stock ≤ 2, market depth 150 a week).
1. **Selling materials** (trade goods to a crafter, 08.8.5): spinner's silk (list 15, band 2) is scarce in
   Ashford (the settlement fact says silk comes from the south) → **15**; three chitin plates (list 4 each,
   band 1, notch 1) are common in a fen-town → list − 1 notch = **3 each, 9**. A second sale of chitin that
   week would glut: 2 each.
2. **Buying mail.** List 50 (band 3, notch 10) → asking **60**. Wren haggles (08.8.7): ROOM true (a smith, face
   to face). Frame: Talk, Presence 0, competence on `deed.influence.trade.haggling` — only the floor → +1;
   lever: the Salt Guild armorer's quote of 55 recorded yesterday (fact `quote.salt_guild.mail`, Precision
   +2) → **+3** vs the smith's Wits defense 10 + 1 + 2 = **13** (needs 10: 55%). Stakes Risky (a closed door
   for the day). d20 = 14 → 17, success, reach Standard **2** → list − 1 notch = **40**. `update_quantity(coin,
   −40)`. Her load: mail worn 2 (her leather goes in the pack: carried 2): she checks capacity (08.9.1).
3. **Selling the spider charm** (WE-08-1, list 80): a property item → `clk.find_buyer` (6, public). Ashford
   ticks 1 a week; Wren spends a week in town and makes one Talk (trade) beat: reach 2 → **3/6** after week 1;
   week 2: +1 + reach 1 → 5/6; week 3: complete → a buyer pays half of list, **40** (inside the 150 depth).
4. **Lifestyle:** three weeks comfortable = 42 coins through `h.08.upkeep`.

*Boundary pairs.* (a) Failure on the haggle (d20 = 6 → 9): the smith holds firm at **60** and will not haggle
again today (cost.closed_door S2); a critical failure would close his door for the week. (b) A **toll** at
the Grey Keep bridge: ROOM false — a fixed fee is paid or not. *Tempting non-example:* "I tell him mail
like that is worth thirty" — an assertion is not a lever (SG-06); only the recorded quote is.

### WE-08-5 Damage, the item share, and repair

Wren's arming sword (versatile, parrying) in two hands has harm edge +1 from `versatile` — the item share of
harm edge is full. She hones it with a whetstone (+1 harm edge for 3 Strikes): it adds **nothing** (08.2.2),
and the codex says so before the interval is spent. A guard's critical counter imposes `cost.gear` **S3** on
the sword: **damaged** → `versatile` and `parrying` stop (no harm edge, no Guard edge); severity S2 and
bands remain. At the next breather she makes a crude repair (Handle, Easy 10, Agility +3 + floor 1 = +4:
needs 6, 75%): success → serviceable until the next `rest_long`. In Ashford a smith's lasting repair costs
`svc.repair` 1 notch of band 2 (the sword's list 10) = **2 coins**. *Boundary:* an S4 cost would have broken
it: only a licensed smith (a 4-segment project or `svc.repair` 2 notches = 4 coins) could mend it.

### WE-08-6 Identifying before attuning (graduated reveal)

Wren holds a masterwork amulet from a barrow (place-gated hoard, T2): signature apparent ("Whispering:
grave-cold, it murmurs near old stones"), one sealed magnitude property. She has five items attuned and does
not want to drop one blind. **Study:** Observe, Wits +2, competence on `deed.lore.arcana`: floor +1 → +3; DC
by the highest sealed tier (tier 1 → Moderate 15): needs 12 (45%); stakes Safe; the player ranks "what does
it do" first. d20 = 15 → 18: success, reach 2 → up to two sealed properties revealed → the one: **Tomb-ward
T1** (reduce blight harm 1). Had she failed, she could not study it again until her next long rest; the
sage in Ashford (`svc.identify`, 10 coins) would tell her everything, flaw included.

### WE-08-7 Encumbrance after the barrow

Wren (capacity 12) carries: shortbow 1, arrows 1, spear 1, leather worn 1, rope 1, bedroll 1, 6 supply (3),
the charm 0, the amulet 0, and now a looted mail hauberk *carried* (4) and a strongbox of coins (3, plus
240 coins = 2). Load = 1+1+1+1+1+1+3+4+3+2 = **18** > 12 → **burdened** (snag on Evade, Sneak, Exert; one
step slower). Over 24 she could not travel. She abandons the strongbox, pockets the coins (2) → 15, still
burdened; she wears the mail and stows the leather (worn mail 2, carried leather 2: 1+1+1+2+1+1+3+2+2 = 14)
— still over by 2 until she eats into the supply or buys a mule (carry 30).

### WE-08-8 An earned gift from the Wardens

The Wardens of the Marches (a faction, tier 2 *(illustrative; 11)*) promised "a blade from our armory" for
clearing the barrow (thread fact `thr.barrow.reward`). The thread completes; 11 writes `gift_due.wardens`.
1. **Circumstance** `[J:enum]`: a reward owed and its terms met → **earned**: masterwork, chosen; tier cap 2.
2. **Base:** the Wardens' customary gift, an arming sword (`bi.sword`; versatile, so every harm-edge entry
   is saturated and drops out).
3. **Pool** (gift domain; giver tags `org.order.knightly`, its patron deeds `deed.martial`,
   `deed.divine.oaths`, plus the folk hand): Balanced, Sturdy, Light make, Dawn-forged, Dawn-touched — and,
   always eligible for its giver's gifts, the order's **boon signature** (`boon_signature:
   prop.sig_well_made` *(illustrative; 13)*).
4. **Signature** (chosen): Well-made is the only signature-eligible candidate at cap 2 → **Well-made T2**
   (+1 to beats that use the sword). Its mod group (strike_edge) removes Balanced.
5. **Magnitude** (chosen, tier 1): the tool shows **Sturdy**, **Dawn-forged**, **Dawn-touched**; Wren takes
   **Dawn-touched** (on a hit whose d20 shows 20, the creature hit is blinded for 2 rounds).
6. **Output:** fully unsealed (the giver says what it is); fact `gifted_by: fac.wardens`; list 10 × 10 + 50
   + 20 = **170**.

*Boundary:* had the captain merely liked her (standing +2, nothing owed), the gift is **favored**: the same
rung, but Well-made is *placed* (signature fill) and the magnitude slot is a weighted draw — no choice.
Goodwill gives the giver's identity; a debt paid lets the recipient choose. *Non-example:* "they owe me for
saving the miller" when no thread or bargain recorded a reward → no gift is due; whether anyone gives is
11's or 15's.

### WE-08-9 Salvage and a recipe

Wren has three wolf charms with Hunter's sense. She asks Tamsin (leathercraft, trained) to salvage two:
Handle under the license, DC Moderate, 1 hour each. Successes yield each charm's stock (a fang: 1 unit) and
one **residuum** (gates = Hunter's sense's gate, `creature.beast.predator`; band tier − 1 = 1). On the
second, delivered reach 3 → Tamsin writes `knows_recipe: prop.sig_hunters_sense`. From now on, any project
of hers whose gated pool contains Hunter's sense (any predator part, or the residuum) may *name* it for the
signature slot (recipe fill) and cite the recipe as an Amplifying lever on the steps.

### WE-08-10 Enchanting a fine cloak

Ash (05's sorcerer; `lic.training.arcane_fire` trained) has learned `lic.training.craft_enchanting`
(trained) and knows `rit.imbue`. Wren's kit cloak is `common` (no slot); her **fine** boots have an open
slot. Ash uses a fire gland (reagent, band 2: gates fire) to imbue **Ember-warded** — a fire property, so
Ash's fire school license qualifies. *For a season:* the rite (6 segments, Hard, an hour a step, 2 Focus)
seats it until the next `season` boundary. *Lasting:* an 8-segment project at Hard under
`deed.craft.enchanting.imbuing`, a day a tick, whose last step is the rite; tier = min(gland band 2, trained
cap 2) = **2** (reduce fire 2). The boots' `worked` property is now spent: no further enchantment can ever
be added. *Non-example:* imbuing Wren's common cloak — no open slot (common has none); first a crafter must
remake it as fine.

### WE-08-11 The item share at E4 (two fire wards)

Wren wears the demon's ring (Ember-warded T2: fire −2) and a cloak that also carries Ember-warded at T1
(−1); one item cannot hold two entries of the same mod group, but two items each may. A fire bolt deals S3
(5). Receiver side, E4: item reductions against `harm.fire` are 2 + 1 = 3, inside the item share of 3 → 3;
her leather armor reduces only `harm.physical` (0 here). 5 − 3 = **2** taken. If she also held an absorbed
power reducing fire by 1, the family would reach 4 (07's cap): 1 taken. *Non-example:* a third fire-warded
item adds nothing — the item share is full, and the codex shows the clamped line ("items: −3 of 3").

---

## Edge cases & adaptation anchors

**Anchor rules in this chapter** (for 12's `anchors.yaml` recompile): 08.1.11 *Improvised weapon* (knobs:
harm_severity, action_cost, targets); 08.3.10 *Harvest* (dc, time_cost, reach_unit); 08.6.4 *Crafting
project* (dc by target rung, time_cost by make time, reach_unit = progress ticks, stakes); 08.6.7 *Repair*
(dc by rung, time_cost); 08.6.8 *Salvage* (dc, time_cost, reach_unit = yield); 08.8.7 *Haggle* (dc, stakes,
reach_unit = notches). Reach for them before inventing:

- **"I sharpen / polish / reinforce my gear before the fight."** A whetstone or an oil (08.4.5); anything
  more lasting is a repair or a crafting project, never a free bonus. A harm edge from honing adds nothing
  where the item share is full (WE-08-5).
- **"I break the enemy's weapon."** Called shot at a held object (06.4.10) or `ab.sunder`; the result is
  01.13.4's condition ladder (08.1.9). A relic attuned to its bearer is `cost_immune` and cannot be sundered.
- **"I use the troll's club."** Pick it up: it is gear (08.3.11), a base item resolved from 09's gear list
  (a club, or a maul for a troll). If it is huge for a person, it is the improvised `body` rung (S3, two
  actions, a snag) — the size rule, not a new weapon.
- **"I wear the dragon's skull as a helm."** A harvested part is a material, not an item, until made into
  one (08.6): improvised making turns it into a `worn` helm with no properties; a crafter turns it into a
  masterwork with the dragon's signature.
- **"I melt down the cursed ring."** Salvage (08.6.8) destroys an item and returns its identity as residuum
  and possibly a recipe; a *Binding* flaw does not stop salvage of an unattuned item, but an attuned
  Binding item must be cleansed first (the bearer cannot let it go).
- **"I sell my enchanting services."** The labor cap (08.8.9 rule 2): a craftsman's wage, never a windfall.
  As a recurring business it is a holding (a workshop), whose yields are 11's tables.
- **"I conjure gold / transmute lead."** G4 by default (13's canon may allow it); if allowed, conjured, price 0,
  unsellable (AI-1). Redirect: what is the coin *for*? There is usually a service, favor or bargain path.
- **"I give away my wealth to the poor."** A conduct.generosity event when the gift is at least 1 Unit of the
  giver's lifestyle (08.8.6; 03); coin leaves through `update_quantity`.
- **"I hide my coin from the robbers."** A Sneak beat to conceal an object (`verb.sneak` covers palming and
  concealment); a concealable item gives a lever. 07's `rob` row takes what was not hidden, from state.
- **"I bury a cache for later."** Items move to a place (`set_position`), recorded as a cache entity like
  07.6.4's; they stay there as state; 11's World Turn may write a rumor if anyone saw.
- **"I trade my sword for his horse."** Barter: both items' lists are compared; the side with the lower list
  makes up the difference in coin or goods, haggled per 08.8.7 (reach moves notches on the difference).
- **"Is there a magic shop?"** Only a city curio dealer (08.8.4), stocked by the generator weekly; anything
  else is an Oracle question at Unlikely or Remote, asked before narration.
- **"Can I wear two amulets?"** No: body slots are fixed (08.5.1). Two charms, two rings, one of each other
  slot.
- **"I attune to a sixth item."** End another attunement first (a free activity, unless Binding).
- **"My relic's power is my best attack; I'll keep using it until it's mine."** It never becomes hers
  (feeds_evidence false); the mentor path is the way to own it (05.9). Say so in one sentence (P16).
- **"I fight with a shield in each hand."** Two shields give one +1 edge: the same family from items is
  capped at the item share (08.2.2).
- **A mob defeated.** One loot call for the side (08.3.1); harvest per body only if the player spends the
  time (a mob of eight rats is not eight harvest beats unless the player wants rat hides).
- **Looting a sleeping or unconscious creature.** A Sneak or Handle beat to take a held or worn item; it is
  the creature's gear (08.3.11), never a generated property item unless it is defeated or yields (08.3.1).
- **A hazard kills a foe.** Scavenged, by the degree of the search (08.3.2).
- **A companion delivers the killing blow.** Scavenged for loot (the PC's own beat did not defeat it); 16
  may let a companion's loot share go to the companion (a wage share, 08.8.8).
- **The player wants a specific property.** The honest paths: hunt a source that gates it (the pool is
  visible in the codex once a recipe or a salvage teaches it); commission with a bias; craft with a recipe;
  earn a gift and choose. Never a DM's grant.
- **Two-change limit** (00.2.7) for item adaptations: e.g. "a net of spider silk that is sticky" = the net
  base (entangling) with one knob change (Grapple's condition severity S2 → S2 is unchanged; duration +1
  round) and a material property only if crafted.

## State touched

- **Reads:** archetype tags, bands, yield, gear, purse, signatures (09); `on_defeat` payload and frame ids (06,
  01); degrees (01); conditions (06); harm and reduction (07); licenses, grades and abilities (05, 04, 02);
  standing and refusals (15); faction tier, threads, commitments and boon fields (11); place terrain tags
  and site bands (10, 13); time and boundaries (00).
- **Writes:** item entities (create, possessions, condition, equipped, attuned, slot, uses, quantity, loaded,
  bound_ability, sealed flags, provenance, facts `teaches`, `knows_recipe`, `kept_since`, `made_by_holder`,
  `gifted_by`, `conjured`, `harvest.done`, `serves`); quantities `coin`, `supply` (purchase only; 10 owns
  use), `ammunition`; clocks (crafting progress and spoilage, `clk.find_buyer`, vessel hull clocks); facts
  (deals, quotes, debts on shortfall for 11, lifestyle).
- **Visibility:** possessions, coin, item properties shown; unidentified properties sealed (00.6.3); crafting
  and find-buyer clocks public; generation logs available (the player may ask how an item was rolled);
  market depth and glut background (the price shows the effect).
- **Tools:** `generate` (gen.loot, gen.craft, gen.gift, gen.item_ability), `create_entity`, `set_fact`,
  `update_quantity`, `set_position`, `seal`/`unseal`, `frame_check`/`roll_check`/`read_result`/`deliver`/
  `apply_costs`, `create_clock`/`tick_clock`, `roll_table` (purses, hoards), `oracle`, `use_ability` (relic
  surcharge), `grant`/`revoke` (bound abilities through the equipped partition; gift abilities to acquired),
  `evaluate` (item share at E4), `advance_time` (crafting steps), `codex`.
- **Hooks subscribed:** item properties subscribe through their effects (`on_attack_hit`, `on_hit_taken`,
  `on_harm_dealt`, `on_defeat`, `on_vitality_threshold`, `on_condition_applied`); `on_item_acquired` (03's
  `cnt.made`), `on_equip`/`on_unequip` (binding, 05.2.8).
- **Handlers registered** (`data/boundaries.yaml owner-block 08`): `h.08.upkeep` (week, 4; reserved in T-00-9),
  `h.08.markets` (week, 6), `h.08.durations` (every boundary, 1), `h.08.craft_decay` (week, 5; traceability
  alias of `h.00.clock_auto`).
- **Runtime capabilities:** RC-RNG (drop checks, draws, purses), RC-STORE, RC-SEAL (sealed properties),
  RC-SCHED (weekly handlers, crafting time), RC-LOG (generation logs), RC-DATA (the eight files), RC-QUERY
  (tag-ancestry pool gates), RC-EVAL (item share at E4; relic surcharge), RC-AUDIT (narrated item claims vs
  state).

## Interface requests

**To 00 (amendments proposed).**
1. **E4 item sub-cap** (08.2.2): at evaluation-pass step E4, contributions whose source is an item are
   summed and clamped to the family's *item share* before the family's own stacking and cap. One line in
   00.10.4 and a column in 00.10.6 (`item_share`). Without it, the item share is enforced only at generation
   (per item), not across five attuned items.
2. **00.6.2 `Item`**: adopt 08.1.1's fields (all additive; 00.6.2's six unchanged).
3. **Id prefixes**: none new (`flaw.*` entries live inside `item_properties.yaml` and are referenced only
   there; if 00 prefers a registered prefix, add `flaw.` to 00.16.2).
4. **Glossary** additions: *item share*, *attunement* (and *attuned*), *relic*, *bound power*, *worked
   property*, *residuum*, *recipe*, *notch*, *lot*, *load unit*, *burdened*, *overloaded*, *Unit of wealth*,
   *find a buyer*, *market depth*, *glut*, *provenance*, *trophy base*, *drop check*, *yield*.
5. **00.11.3 step 7 integer note**: halving weights is done by doubling all weights first (08.3.8).

**To 01.** `cost_immune` (08.1.10) and the meaning of `damaged`/`broken` (08.1.9) are defined as requested;
improvised weapons use the resembled weapon (08.1.11). *Request:* 01.13.4's S5 row should name "an item with
a signature or a bound ability takes the location form, never destroyed" (08.1.9).

**To 02.** Quality names map onto rungs 1–3 (08.1.4); the coin unit is confirmed (08.8.1); a spellbook is
`bi.spellbook` with `teaches:` (08.4.6); all 39 kit tags resolve (`base_items.yaml#kit_resolution`); a kit's
`fine` item arrives with its slot open; `lic.people.great_frame` counts Might +1 for capacity (08.9.1).

**To 03.** Every base item carries its most specific `item.*` tag first (level 3 where 03 has one); crafted
items carry `provenance.maker` and `provenance.domain: gen.craft`; `quality_index` 1–6; the generosity
ground floor is 1 Unit = the weekly lifestyle cost (08.8.6). *Proposed tags* (`data/tags.yaml`, adopted at integration,
17 level-3 tags): `item.weapon.bludgeon.whip`; shields `item.shield.light.{buckler,round}`,
`item.shield.heavy.{kite,tower}`; treasure `item.goods.treasure.{gem,art,coinage}`; documents
`item.goods.document.{text,map}`; consumables `item.consumable.oil.{weapon,incendiary}`,
`item.consumable.remedy.antidote`; conveyances `item.conveyance.mount.war`, `item.conveyance.vehicle.cart`,
`item.conveyance.vessel.{boat,ship}`. *Integration edit:* 03 drops deed evidence for frames whose license or
ability came through an item with `feeds_evidence: false` (04 request 11).

**To 04.** Relic licenses are `feeds_evidence: false` (08.4.4; `lic.08.relic_grant`); `gen.item_ability`
reuses the active entries of `gen_absorb.yaml` (natural powers in trophies) by reference — 04 must not change
their ids without telling 08; costly = narrow_survival (one classification for both domains).

**To 05.** One item-bound ability per item, signature slot only, at a stated rank (3 → 1, 4 → 2, 5+ → 3);
priority ranks: item intrinsic claims 15–19 (14 + tier), applied consumables 20; Focus consumables use
`eff.restore` within 05.6.11's cap; implements are signs and vessels by item facts (08.4.7); texts teach by
`teaches:`; rite components are priced by band (08.8.8); `gen.gift` abilities go to the acquired partition
(08.7.3); `damaged`/`broken` defined (08.1.9, for `ab.sunder`, `ab.field_patch`). *Request:* `rit.imbue`'s
effect text should cite 08.6.10 (a worked property; one per item, ever).

**To 06.** Weapons are built exactly on T-06-6/T-06-7 (08.1.5); shields +1 Guard edge, no reduction; armor
1/2/3 with snags in other pillars; firepots carry a spread shape (`burst`), smoke pots `linger`; ammunition is a
quantity with half recovery. *Request:* list `armor.<item>` intrinsic snags among the engine-cited snags of
06.4.7 (outside the two-cited count, like repetition), and `burdened` likewise (08.9.2).

**To 07.** Armor reduction 1/2/3; shields 0; items' share of reduction 3 within the cap of 4; the valuable
band is band 3 (26+ coins) for the `rob` row; medium and heavy armor cap a long rest at partial;
remedies carry `eff.07.affliction_shift` (specific −2, general −1); maim offsets (hook, brace, peg, glass eye)
are craftable as `item.tool` bases by 13 or a later data pass on the same schema (price band 2, crafted under
the matching trade) — *open item:* 08 ships no named prosthesis entries; 07.7.6 may reference "a made
replacement (08.6)" generically. Caches hold item ids; nothing with a signature or bound ability is
destroyed (08.1.9).

**To 09 (the loot contract, 08.3.4).** Per archetype: `creature_tags` (most specific first), `harm_tags`,
`evidence_tags`, `org_tags` (folk), `threat_band`, `loot.yield` (`none | trophy | hoard | always`; default
trophy), optional `loot.trophy_base`, `loot.pool_gate_tags`, `loot.flaw`, `signature_property` (default:
`default_signatures`), `gear` (base item ids), `purse` (a table id or `none`), `harvest` override,
`signature_of` on `gen_absorb.yaml` entries. Run the pool-≥-3 check from `08-loot-sim.py` on every
archetype and base. An archetype whose signature is `prop.bound_power` (spellcasters, great dragons) yields a
relic on a decisive win.

**To 10.** Supply (1 per person-day; lots of 2 per coin; 2 per load unit), light sources and burn times,
mounts' and vehicles' pace and carry (08.9–08.10); the `burdened` and `overloaded` states for travel pace;
place terrain tags and site bands open place-gated properties and set hoard bands; the harvest anchor
(08.3.10) is an exploration activity of 1 interval or 1 hour.

**To 11.** Holdings' prices, upkeep and staff (08.8.8) and the rule that yields are labor and rents;
faction `boon_signature` and `boon_base` for gifts; `gift_due.<giver>` facts trigger `gen.gift`; lifestyle
shortfall writes a debt fact; cache dispersal and rumors of lost signature items (08.1.9); market glut and
find-buyer clocks may feed rumors.

**To 12.** Narrate a drop in one line (08.3.13); the generation log is "available" in the codex; the OFFER
shows a relic's surcharge as its own line.

**To 13.** Regional stock (which goods are scarce where), crafters by settlement, `canon_impossible` on
transmutation (AI-1), named storied items and sets (08.4.8), faction boon signatures and customary gifts,
the region's `rare metal`, and settlement facts for curio dealers.

**To 14.** Codex views: possessions with load and slots; item cards (rung, signature, properties, sealed
count, flaw if known, price, provenance); attunement 0–5; equipped-slot bindings; crafting clocks; the item
share as a rollup line per family ("items: +1 of +1 edge on Guard"; R3 08.12 pseudo-stats).

**To 15.** Haggling is 15's negotiation frame with 08's price ladder (08.8.7); `clk.find_buyer` uses Talk
(trade); training fees per week (08.8.8).

**To 16.** Wages by role and band (08.8.8); mounts are items plus companion entities (`companion_hint`);
porters carry 10 load units; a companion's loot share.

## Open empirical questions

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-08-1 | Do narrow natures (clockwork, ooze) repeat magnitude properties too often? | pools as shipped; mean repeat 13.5%, worst 31.7% | **T-08-REPEAT**: after 09 tags its bestiary, re-run `08-loot-sim.py`'s repeat test on every archetype; any archetype above 20% gets a broader trophy base list or two more gated entries |
| OEQ-08-2 | Is the drop check's rate right for play (density 08.2.7)? | T1 10 · T2 20 · T3 35 · T4 50 · T5 70 | **T-08-DENSITY**: count attuned property items per power band across 3 long playtests (or a 60-session simulated campaign with 09/11 tables); if density runs more than one row ahead of 08.2.7, lower each chance by 5 points; if behind, raise |
| OEQ-08-3 | Does the item share bind often enough to make the choice of five matter, without making loot feel pointless? | shares +1 / +1 / 3 | **T-08-SHARE**: playtest survey after 10 sessions — share of loot the player kept for its *effect* vs sold/salvaged; target 30–60% kept; plus the sim's clamp rate 15–30% |
| OEQ-08-4 | Does the wealth curve hold (08.8.10)? | purses, hoards, sinks as shipped | **T-08-WEALTH**: track coin per session in playtests; target the tier table ±1 tier; adjust hoard multipliers first |
| OEQ-08-5 | Are crafting odds at masterwork too harsh for a trained crafter (48% at +7)? | as T-08-14 | **T-08-CRAFT**: 3 crafter-focused playtest arcs; if fewer than half of masterwork attempts by trained crafters with a workshop complete, lower spoilage ticks on failure to 1 for any failure (crit failure included) |
| OEQ-08-6 | Do players understand relics as borrowed power (no growth)? | the OFFER shows the surcharge line | **T-08-RELIC**: in playtests, count player statements that assume relic use grows a calling; target 0 after the first session's explanation |

