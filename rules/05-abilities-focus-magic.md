# 05 — Abilities, Focus, and Magic

> This chapter governs everything a character can do beyond the fifteen basic verbs: the abilities they
> hold, the fixed number of places those abilities live in, the one pool (Focus) that pays for them, and
> magic, which in this game is a named subsystem built from the same parts. It is shaped by three
> commitments. First, a calling never owns a list of powers (constitution P5): there is **one shared
> ability pool**, every entry tagged by what it is evidence of, and a calling's tiers only grant *picks*
> into that pool. Second, every ability is a closed-form record, never a paragraph of prose: one of eight
> template forms, a literal positive scope, a governing principle, separate limitation / weakness / cost
> fields, effect references into the composition substrate, an explicit engine-counted recharge, and a
> price for stretching it past its text. That is what lets the player try something the ability's
> author never wrote down and lets the AI rule on it by lookup. Third, power is bounded by structure
> rather than by audit: twenty slots and no twenty-first, one Focus pool capped at twelve, a power-budget
> formula every entry is checked against by script, and structural retirement (replace, restate, shelve,
> fold) wherever something new arrives.

**Reading this chapter.** Rules are 05.1–05.12. The data is canonical for numbers and ids:
`data/abilities.yaml` (the pool: 266 abilities), `data/licenses.yaml` (81 training licenses and the Focus
licenses), `data/rituals.yaml` (24 rites and the rite-design tables), `data/composites.yaml` (named
composites and the priority tables), with additions to shared files in `data/effects.yaml owner-block 05` and
`data/boundaries.yaml owner-block 05`. The data files are generated and validated by
`rules/_process/simulation/05-gen_data05/gen_data05.py` (ids, tags, effect ids, parameter ranges, coverage, and the
power budget of every rank of every ability). Worked examples continue 00's character **Wren** and add
**Ash**, a hedge-taught fire sorcerer. Numbers owned by chapters not yet written (06, 07, 08, 09) are
marked *(illustrative; ch.NN owns)*.

---

## Design intent

**Goals served.** Goal 1 (the player feels free to try any creative idea) through three priced ways past
an ability's literal text (stretch, emulate, crude fallback), a universal Focus *push* that needs no
ability at all, rites that can be designed in play, and a pool rich enough that any way of playing finds
abilities that fit it. Goal 2 (the AI rules correctly) by making every ability a record the engine
executes: the DM classifies (which ability, which target, does the principle still apply, is the source
present), and tools compute cost, legality, uses, composition and effect [BRIEF §3; BRIEF A2 #1, #6, #12,
#13].

**The bets this chapter makes.**

1. **One pool, tag-gated, tier-floored.** 179 calling-partition abilities cover all 81 level-2 deed tags
   (at least two each, one usable at tier 1) and all nine branches at every minimum tier; 57 more are
   gated by conduct axes for vows and dark callings, three at each pole a calling uses (tiers 1, 3 and 5);
   27 mirror ch.04's absorbable powers; and three **branch workings** are held through magic training
   itself, so that a caster is never weaponless (05.7.11) [revision: I-007, I-009, I-015]. A calling's
   picks are drawn from this pool through its tags (04.8.4). The count is justified in 05.11.6
   [C:P5; C:V; DL-05-02].
2. **A closed grammar of eight forms** (Edge, Lever, Permission, Working, Reaction, Form, Exception,
   Reserve), which is Fate's three stunt patterns widened to cover what a d20 game with a substrate
   needs. Every ability is exactly one form. No published game trusts open, free-text powers without a
   fixed list or a fixed grammar, and this one must be run by an AI on its thousandth use
   [R1 §05; R: https://fate-srd.com/fate-core/stunts-refresh; C:P10; DL-05-04].
3. **Structured and unstructured use.** An ability used as written is reliable. Used *within its
   governing principle but outside its text* it is a **stretch**: allowed, at a higher DC, one more
   Focus, and capped reach, and mastery widens the envelope. This is Mother of Learning's structured
   versus unstructured casting and Ars Magica's formulaic versus spontaneous magic, expressed as a
   lookup [R2 #4; R: http://www.redcap.org/page/Spontaneous_spell; DL-05-07].
4. **One Focus pool, many ways to fill it.** Costs come in five discrete bands (0–4). Identity shows in
   *generation* (ch.04's nine family triggers) and in each magic branch's own limitation, weakness and
   miscast, never in a second currency [C:P9; R3 05.7, #13; DL-05-10].
5. **Power is paid for with P12's three levers as prices.** The budget formula of 05.11 gives every
   ability an allowance from its minimum tier and then *adds* allowance for each Focus point, each
   recharge limit, each limitation and each weakness it carries. Passives carry none of those terms, so
   they are budgeted lower by construction (13th Age's lesson: always-on must be modest)
   [C:P12; R1 M-22; R2 §05 power-budget benchmark; DL-05-16].
6. **Magic is abilities plus four things:** a source that can fail in its own way (miscast), a
   limitation each branch carries, rites that take time and material, and learning by watching. Nothing
   in magic bypasses the gate, the frame or the substrate [00.17.1 Q20; R5 MG-03, MG-04, MG-07, MG-08].

**What this chapter deliberately avoids.**
- Ability lists owned by callings; spell slots or any second resource; attribute-derived Focus
  [C:P5; C:P9; 00.3.13].
- A twenty-first slot. No rule, item, tier, boon or rite raises the ceiling or resizes a partition
  [C:V; R2 §05: cap-breaking in the source fiction is a rare, priced exception that this game declines].
- Prose-only mechanics, soft phrasing ("offers no protection against…"), and effect text that describes
  an ability by what it lacks [SG-15; R3 05.9].
- Extra actions. No ability, flare or composite adds an action (INV-11). Abilities change what an action
  *contains*.
- Chains. An effect caused by a trigger never fires another trigger (INV-12); the one-link limit is
  designed for, not worked around (05.10.5).
- Open-ended power creation. A player cannot author a new ability in play. They can stretch one, emulate
  one, or design a **rite** whose effects are drawn from the effect library and priced by a table
  (05.8.4) [C:V; R1 §05 "no surveyed published system uses" an open framework].
- A corruption meter. Magic's dangers are concrete and local (miscast, overdraw, a rite's failure
  costs, a debt owed); moral consequence is ch.04's shadows and Fraying, which already exist
  [R5 MG-07; DL-05-21].

**Research basis in brief.** HWFWM's 20-slot grid and its failure modes (status sprawl, accreting text)
[R2 §05, #3]; Stormlight, Allomancy and Feruchemy as fuel designs [R2 #8]; Path of Exile's support gems,
one-copy rule and projectile priority order, Isaac's replacer ranks, Slay the Spire's hooks and Risk of
Rain 2's chain terminator [R3 05.2–05.5, 2B]; Fate stunts, Blades special abilities, 13th Age's
conditional redesign and HERO's discrete cost brackets [R1 §05, M-17…M-22]; and, from this author's own
search: Pathfinder 2e focus points (a small pool, restored by a ten-minute activity)
[R: https://2e.aonprd.com/Rules.aspx?ID=276], Ars Magica's formulaic and spontaneous casting
[R: http://www.redcap.org/page/Spontaneous_spell], Mage: The Ascension's vulgar-versus-coincidental
cost for witnessed impossibility [R: https://en.wikipedia.org/wiki/Mage:_The_Ascension], Earthdawn's
thread weaving as extra time for bigger workings [R: https://earthdawn.fandom.com/wiki/Spellcasting],
Ironsworn's assets (three abilities each, bought one at a time, rituals as assets)
[R: https://ironsworn-rpg.fandom.com/wiki/Assets], and Dungeon World's Ritual move with its closed list
of conditions [R: https://www.dungeonworldsrd.com/classes/wizard/].

---

## Rules

Rule ids are `05.S.R`. Kinds follow 00.2.2. Rules that contain a `[J:*]` decision use the 00.2.5
template; `[D]`, `[T]`, `[S]` and `[N]` rules are written compactly. "The engine" means the deterministic
tools the DM operates (00, Principle I).

### 05.1 Foundations

**05.1.1 What an ability is.** `[D]` An **ability** is a license (00.12.1) with mechanics: an entry of
`data/abilities.yaml` (id `ab.*`) that a character **holds** in a slot. A **spell** is an ability whose
first tag is under `deed.arcane`, `deed.divine` or `deed.primal`; it is the same record with `kind:
spell` and the trait `trait.nature.magical`. Everything else a character may be licensed to do
(training, languages, calling capabilities, fact licenses, rites) is a license **without** a slot
(05.2.3). The one exception is the three **branch workings** (05.7.11): `ab.*` records with `slot_class:
license`, held by every holder of a magic training license of their branch and occupying no slot
[revision: I-009]. An ability is read literally at its active rank (INV-8): it does what its `scope` and `effects`
say and nothing else, and narration may never describe it doing more [00.12.2; 01.3.3].

**05.1.2 Abilities in state.** `[D]` `Character.slots` (00.6.2) holds three lists of held abilities.
Each entry is:

```yaml
HeldAbility:
  ability_id: ab.*
  partition: calling | acquired | equipped
  source: {kind: pick | learned | taught | absorbed | gift | item, ref: <calling id + tier | clock id | mentor id | library | offer id | item id>}
  rank: 1..3                 # computed, never stored by hand (05.3.9)
  uses: {remaining: int, per: boundary} | null
  sustained: bool            # true while this ability's sustained effect is running
  bound: bool                # equipped partition only: true while the item's ability occupies a slot
  lifecycle: provisional | permanent
  acquired_at: time
```

`Character.focus` gains fields owned by this chapter: `{current, max, reserve: {banked: int, capacity:
int, charging: int, vessel: item_id|null}, state: steady | spent, generated_this_scene: int,
restored_by_consumables_since_long_rest: int, breathers_since_short_rest: int, short_rests_today: int,
overdraws_since_long_rest: int}`. `Character.shelf: [ability_id]` holds acquired abilities that are known
but not slotted (05.2.6). `Character.witnessed: [ability_id]` and learning clocks are 05.8's. Visibility:
slots, ranks, uses, Focus and the shelf are **shown**; `witnessed` and learning clocks are **available**
(00.6.4).

**05.1.3 The words.** `[N]` **Hold**: have an ability in a slot. **Pick**: a calling tier's right to
fill a calling slot from the pool (04.8.4). **Activation**: one use of an active ability. **Working**: an
activation that is itself the character's beat. **Rider**: an activation that attaches to the
character's own beat. **Stretch**, **emulate**, **crude fallback**: the three priced ways past a
license's text (01.3.5). **Flare**: one optional surcharge on an activation (05.6.8). **Push**: spending
Focus on an ordinary beat (05.6.7). **Spent**: at 0 Focus. **Overdraw**: paying Focus with Vitality.
**Rite**: this chapter's short word for a ritual, a clocked magical extended task (`rit.*`).
**Miscast**: a working of magic that goes wrong in its branch's way. **Shelf**: known, unslotted acquired
abilities.

### 05.2 Slots and the hard ceiling

**05.2.1 Twenty slots in three partitions.** `[D]` A character holds at most **20** abilities:

| Partition | Slots | Filled by | Usable when | Changes at |
|---|---|---|---|---|
| `calling` | **12** | a **pick** granted by a calling tier (04.8.4), and nothing else | always, at the rank the holding calling's tier gives | recognition, crystallization, the `season` re-pick, the Retrain activity (04.8.7) |
| `acquired` | **4** | abilities **learned** (a completed learning clock), **taught** (a mentor), **absorbed** (the Taking, 04.10), or given as a **gift** (a patron or power, 08's `gen.gift`) | always, at rank 1 (absorbed powers: at the tier the generator gave) | any completed `rest_long` (05.2.7) |
| `equipped` | **4** | the one item-bound active ability of an equipped item (00.11.5; 08) | only while the item is equipped and its ability is **bound** | a `breather` outside conflict, or the equip action in conflict (05.2.8) |

These are the reference values of 00.17.1 Q2 (20 = 12 + 4 + 4), adopted without change. The partitions
do not lend to each other: an empty calling slot cannot hold a learned ability, and four acquired slots
are four however many callings a character has. *Why 20:* it is the one cap with a tested precedent in
this project's research (HWFWM's 4 × 5), it sits near the top of the converged "about five modifiers per
active thing" range once divided among three callings, and ch.04's ladder fills the calling partition
exactly when three callings reach tier 3 (3 × 4 picks), so the ceiling starts to bind at the moment a
character is broad enough for consolidation to be attractive [R2 §05; R3 05.1; 04.8.4; DL-05-01].

**05.2.2 The ceiling is closed.** `[D]` No effect, item, boon, rite, tier or ruling adds a slot or moves
a slot between partitions. `grant` (tool #28) refuses a write that would exceed a partition. Where the
source fiction lets rare gifts break a cap, this ruleset does not: a cap that can be raised is a menu
that grows [C:V; C:P5 "hard total-slot ceiling"; INV-13].

**05.2.3 What does not take a slot.** `[D]` Only `ab.*` entries are held in slots. These are licenses
and take none: training licenses (`lic.training.*`, 05.9), languages, the calling capabilities
(`lic.call.*`, 04.5.3), the Focus licenses (`lic.focus.*`, 05.6), fact licenses (01.3.2), known rites
(`rit.*`, 05.8.1), the branch working a magic training license carries (05.7.11) [revision: I-009], the passive and mundane properties of items (08's item-layer budget), a calling's
Focus trigger, boon or composite (04.5.4), and conditions. Each of those is bounded by its own owner:
training by time (05.9.4), rites by material and time, item properties by 08's budget, family mechanics
by one per calling.

**05.2.4 How slots open.** `[D]` All twenty slots exist from character creation. What limits their use
is the right to fill them:
- **Calling slots** are filled only through the **pick allowance** `A` (04.8.4): cumulative 2, 3, 4, 5, 6
  picks for a deed-keyed calling at tiers 1–5; 1, 1, 2, 2, 3 for a vow or dark calling; `A` never exceeds
  12. A character with no calling has an empty calling partition.
- **Acquired slots** are open to any character, recognized or not, who completes an acquisition path
  (05.8.5–05.8.7). This is where a character without a calling, or one learning outside their calling,
  holds abilities [C:P2 baseline; C:P4: breadth of access is not day-one power, since each acquired
  ability is held at rank 1 and each costs weeks to learn].
- **Equipped slots** are open to any character who equips an item with an item-bound active ability.

**05.2.5 When the calling partition is full.** `[D]` A new pick **replaces** a held calling ability of
the player's choice (04.8.4 "at the cap"). The replaced ability is retired *from the character*
(`retire`, tool #28) and returns to the pool; it is not moved to the shelf, because the shelf belongs to
the acquired partition. An ability that names another in its `replaces` field takes that ability's slot
without using a new one (an upgrade path: the DCC fork, a replacement and never an addition)
[C:VI; R3 05.12].

**05.2.6 When the acquired partition is full: the shelf.** `[D]` A fifth acquired ability goes to the
**shelf**: known, not held, not usable (a beat that needs it is G3, and the redirect says "it is on your
shelf: you can bring it back after a long rest"). The shelf holds at most **4** abilities. A ninth
acquired ability (4 slotted + 4 shelved + 1) requires the player to **forget** one of the nine at once
(`retire`; it may be learned again later by its paths, at full clock). Absorbed powers use ch.04's
**library** in place of the shelf (size 4–12 by the Devourer's tier, 04.10.3); the two stores are
separate and neither can hold the other's contents [C:V; R3 04.18; DL-05-03].

**05.2.7 Re-slotting at a long rest.** `[D]` On every completed `rest_long` of quality `full` or
`partial` (07), handler `h.05.reslot` (phase 3) lets the player exchange any number of abilities between
the acquired slots and the shelf or library. No check, no Focus, no time beyond the rest. An
`interrupted` rest allows no exchange. Uses do not refresh by re-slotting: an ability returns with the
`uses.remaining` it had when it left, and then the rest's own recharge applies (05.4.6) [04 Interface
request 8].

**05.2.8 Binding equipped abilities.** `[D]` Equipping an item with an item-bound active ability
**binds** that ability to a free equipped slot. With all four in use, the new item's ability is
**dormant**: the item's passive and mundane properties work, its active ability does not, and the codex
says which. The player may choose which four are bound at any `breather` outside conflict. In conflict,
unequipping an item unbinds at once, and the action that equips an item binds its ability if a slot is
free (the action is ch.06's). An ability held through the equipped partition is used at the rank the
item states (08), never at a calling's rank, and its first tag earns no evidence when the item is a
relic (`feeds_evidence: false`, 00.11.5).

**05.2.9 One of each.** `[D]` Three engine-enforced exclusions keep a full sheet from stacking
[R3 05.2 the one-copy rule; INV-13]:
1. **One instance per ability id** across all partitions. A second source of an ability already held
   grants nothing (a relic of a technique you know is only a spare).
2. **One held ability per `mod_group`** across the calling and acquired partitions (the pool gate of
   04.8.4 already refuses a second in the calling partition). An equipped item whose ability shares a
   `mod_group` with a held ability stays dormant.
3. **One running effect per behavioral slot** (`slot.stance`, `slot.aura`, `slot.body_form`,
   `slot.movement_mode`, `slot.strike_delivery`, `slot.spell_delivery`, `slot.defense_reaction`) by
   priority rank (05.10.3), and **one sustained working** at a time (05.4.7).

**05.2.10 Provisional abilities.** `[D]` A pick is `provisional` with the tier that granted it and is
confirmed or lapses with it (04.8.2). A learned, taught, absorbed or gifted ability is `provisional`
until the first `reflection` after it has been activated (or, for a passive, has applied) in at least
**three** different scenes; at that reflection it becomes `permanent`. One that has not reached three
scenes by the second `season` boundary after it was acquired is moved to the shelf (never deleted) and
the codex says so one season earlier. A provisional ability works in full; the status is a trial of
whether the character lives with it, per Principle VI at character scale [C:VI; 00.17.1 Q12; DL-05-22].

### 05.3 The ability template grammar

**05.3.1 The record.** `[D]` Every entry of `data/abilities.yaml` has these fields (the License schema of
00.12.1 plus the fields `data/SCHEMAS.md#abilities.yaml` requires plus this chapter's optional ones,
T-05-2). No field is prose-only mechanics: every mechanical consequence is an effect reference, a number
on a named scale, or a table reference (00.16.4).

| Field | Content | Lever (P12) |
|---|---|---|
| `id`, `name`, `kind` | `ab.*`; `ability` or `spell` | |
| `tags` | the **first** tag is a `deed` tag at level 2 or 3 (it is the ability's evidence tag, competence tag and pool-gate tag); then any `conduct`, `harm` and `trait` tags | |
| `min_tier`, `mod_group`, `slot_class` | 1–5; the exclusion family; `calling`, `acquired`, `equipped`, or `license` (the three branch workings, 05.7.11, which also carry `granted_by`, `deed_tag_rule` and `rank_rule`) | |
| `form` | one of the eight forms (05.3.2) | |
| `activation`, `timing` | `passive` or `active`; for actives `beat`, `rider`, `reaction` or `trigger` (05.3.4) | |
| `regime`, `hook`, `slot` | the combination regime (00.10.7), with its hook or behavioral slot | |
| `principle` | one sentence naming **the operation and what it operates on** (the governing principle; 05.5.1) | |
| `scope` | the positive, literal statement of what it lets the holder do (rendered from the active rank's `text`) | **scope** |
| `limitation` | the boundary of the scope, written as what it applies *to* (targets, conditions, bands, needs) | **limitation** |
| `weakness` | present only if intended: an explicit vulnerability the ability creates, as an effect reference | **weakness** |
| `cost`, `cost_text` | `{focus: 0–4}`; any price paid elsewhere (Vitality, a component, time), as effect references | **cost** |
| `limits`, `refresh_on` | `{per: <boundary>, uses: n}`; an optional hook that returns one use (05.4.6) | |
| `check` | how it is resolved: `none`, `aimed` (the holder rolls) or `resisted` (the target rolls), with verb, attribute and what it works against | |
| `effects` | effect references (00.10.1); for a ranked ability, the active rank's list | |
| `ranks` | 1–3 complete restatements `{rank, text, effects, cost, limits}` (05.3.9) | |
| `excludes` | the nearest things it does not cover, each naming what would | |
| `stretch`, `emulate`, `crude_fallback`, `acquisition_paths` | 05.5 | |
| `flares` | which of the six flares it accepts (05.6.8) | |
| `spread` | at most one spread tag it carries natively (05.10.4) | |
| `composite_key` | true on the few abilities that key a named composite (05.10.6) | |
| `dictates_choice` | true when an effect it applies dictates another being's choices (charm, compulsion, fear), for 03.2.6 | |
| `narration_may_not_imply` | a closed list | |
| `budget` | `{value, allowance, terms}` as computed by 05.11 | |
| `replaces`, `requires_conduct`, `conduct_pole`, `adversary_only`, `mirror_of` | optional | |

The four P12 fields are **separate fields**, never one sentence, because the project's one recorded
ability failure came from a limitation and an implied weakness sharing a clause ("no protection against
cold" narrated as a cold vulnerability). A `limitation` is a scope boundary, written positively
("Applies to harm tagged `harm.fire`"). A `weakness` is an effect reference with its own literal text,
and an ability with no `weakness` field **has none**: the narrator may not supply one
[C:P12; R3 05.9, #12; SG-15; R: specs/003-ability-acquisition-probe/implementation-results.md].

**05.3.2 The eight forms (the closed grammar).** `[D]` Every ability is exactly one form. A form fixes
which regime, operations and timing an ability may use, so an ability's shape is checkable before its
numbers are [R1 M-17; C:P10; DL-05-04].

| Form | What it is | Regime · timing | Operations it may use | Fate pattern it extends |
|---|---|---|---|---|
| **Edge** | a number in narrow circumstances | additive · passive | `modify` (edge, harm_edge, reduction, adjust), `multiply`, `step` | action bonus |
| **Lever** | a citable fact under a stated condition | additive · passive, or rider | `lever` | action bonus |
| **Permission** | a method the basic verbs exclude, resolved by an ordinary frame | additive · beat | `grant_license`, `claim_slot` on `slot.movement_mode`, or none (the scope is the permission) | add a new action |
| **Working** | the activation *is* the beat: it produces effects through an aimed or resisted check | independent_trigger · beat | `harm`, `apply_condition`, `remove_condition`, `resource`, `move`, `tick`, `reveal`, `create`, `trigger_check`, `set_fact` | add a new action |
| **Reaction** | fires on a hook, off the holder's own beat | independent_trigger · reaction or trigger | `prevent`, `redirect`, `harm`, `apply_condition`, `move`, `resource`, `lever` | rules exception |
| **Form** | replaces *how* something works for a duration | priority_exclusive · beat or rider | `claim_slot` (with the effects the claim carries) | rules exception |
| **Exception** | one stated exception to one stated rule in a narrow context | additive · passive, or rider | `restrict` (as an immunity), `step`, `modify` on a cap-bound quantity, `economy` (reactions only) | rules exception |
| **Reserve** | converts or returns a resource | independent_trigger · rider, reaction or trigger | `resource`, `modify` (`focus_cost`, maxima) | (fate-point economy; this game allows it inside 05.6's caps) |

A proposed ability that fits no form is not an ability: it is a rite (05.8), an item (08), a calling
capability (04), or out of scope. Adding a form is an amendment to this chapter.

**05.3.3 Passive and active.** `[D]` + `[J:flag]` [C:P5]
- A **passive** ability has no cost, no limits and no usage state. It applies whenever its effects'
  `applies_when` expressions hold. The engine evaluates every clause that reads tracked state (tags,
  verbs, bands, flags, conditions, harm tags). A clause that reads the fiction ("when tracking by scent",
  "when you have had an interval to study the lock") is a `[J:flag]` the DM answers when framing:
  *true only when* an established fact or the declared method makes it so; *false* when it rests on the
  player's assertion alone; uncertain → false (SG-05). A passive is verified by the narration-consistency
  check (12) and by the frame's breakdown, which lists every passive that contributed.
- An **active** ability is invoked by the player, costs Focus or a use or both, and passes through
  `use_ability` (05.4.1). Any ability with a `cost`, a `limits` entry or a duration is active.
- *Worst case of a wrong fiction-clause call:* one passive wrongly applied gives its listed number once
  (at most +2 edge, one lever, one severity step) and appears by id in the OFFER breakdown (class i).
- Passives are budgeted lower than actives by construction (05.11.2), and a passive may never contain
  `prevent`, a condition of the hard-control group, or harm of S3 or more (T-05-9).

**05.3.4 Timing.** `[D]` An active ability has exactly one timing:

| Timing | When it is used | Action cost | Limit |
|---|---|---|---|
| `beat` | it is the declared beat (a Working, a Permission, entering a Form) | whatever ch.06 charges for the verb the ability is anchored to (`check.verb`) | one beat is one activation |
| `rider` | declared with the holder's own beat of a named verb or tag, in the same frame | none beyond the beat | **one rider per beat** (05.4.3) |
| `reaction` | on its hook, in response to another's act | the holder's reaction (06) | one reaction per trigger event; 06 sets reactions per round |
| `trigger` | on its hook, as a consequence of the holder's own resolved beat or of a boundary | none | fires at most once per event; subject to depth (05.10.5) |

A `trigger` ability with a Focus cost fires only on the player's yes. The engine asks at the moment the
hook fires and shows the cost; the player may set a standing answer per ability (`always`, `ask`,
`never`) in the codex. A `trigger` with no Focus cost fires automatically and may be set to `never`.

**05.3.5 How an ability is resolved.** `[D]` The `check` field decides who rolls, per 00.3.3:
- `none`: no roll. The effects apply when the activation is validated (most riders, Forms, Reserves,
  Edges and Levers).
- `aimed`: the holder rolls **one d20**. Attribute: the ability's `attribute`. Competence: the highest
  entry on the ability's **first tag** or an ancestor (00.3.6). Against: the target's defense named in
  `check.against` (a creature), or an obstacle tier (an object or the world). A harm-dealing aimed
  Working shifts its severity by `(delivered reach − 2)` like a Strike (00.3.15); other effects use
  delivered reach as the ability's text states.
- `resisted`: the holder does not roll. Each target rolls Endure or Evade (`check.resist_verb`,
  `check.resist_attribute`) against the holder's **effect DC** = `10 + attribute + competence(first tag)
  + edge` (00.3.8), read on 01.18.3's table unless the ability gives its own degree table.
A rider has `check: none` and rides the roll of the beat it attaches to: its effects apply on the
degrees its text names (default: any success).

**05.3.6 Literal, positive text.** `[D]` Each rank's `text` is rendered **verbatim** into the narration
packet whenever the ability is used or applies, so the narrator works from the words on the page and
never from memory [R4 §9 05 #4]. Authoring rules, enforced by the generator script where mechanical:
(a) say what it does and to what; (b) no clause of the form "does not protect against", "offers no", or
"but leaves you"; (c) no figurative language inside a mechanical clause; (d) every number is a value on a
00 scale; (e) a "Does not:" line appears only in `excludes`, and each exclusion names the license or verb
that *would* cover the thing; (f) no behavioural hints ("may tempt you to…").

**05.3.7 Narration may not imply.** `[N]` Every ability carries a closed list. The defaults, which each
entry extends, are: a harm type, target, range band or duration other than the text's; a weakness the
record does not hold; an effect on a being or object outside the stated targets; that the ability can do
again what its uses or Focus no longer allow; any of the seven sensitive upgrades (perception, memory,
mobility, control, access, awareness, freedom; 01.3.3) beyond the scope's words.

**05.3.8 Tags an ability carries.** `[D]` The first tag fixes four things at once: which callings may
pick it (04.8.4), which competence its check uses (05.3.5), where `cnt.focus` evidence lands when Focus
is spent on it (03.7.4), and which training license's grade governs its stretch and flares (05.9.2).
`trait.*` tags pull in 01.17's general rules (a `trait.action.speech` working is forbidden while
`cond.choking`; a `trait.sense.loud` one ticks listening clocks). `harm.*` tags are the harm it deals.
A `conduct.*` tag with `conduct_pole` marks an oath-gated ability (05.3.10).

**05.3.9 Ranks: restated, never appended.** `[D]` An ability has one to three **ranks**. Each rank is a
complete restatement: its own text, effects, cost and limits. Exactly one rank is active:

`rank = min(highest authored rank, 1 + floor((T − min_tier) ÷ 2))`

where `T` is the tier of the calling whose pick holds the ability (04.5.5), lowered by a Fraying
suspension where one applies. For a pick carried through a consolidation or a fork, `T` is the higher of
the new calling's tier and the `tier_reached` of the specialty the pick came from (04.8.5 step 3), so a
consolidation never lowers a rank. So an ability with `min_tier` 1 is at rank 2 from tier 3 and rank 3 at
tier 5; `min_tier` 2 or 3 reaches rank 2 at tiers 4 or 5; `min_tier` 4 or 5 has one rank. An ability held
in the **acquired** partition is always rank 1. One held through an **item** has the rank the item
states. The codex shows only the active rank's text. When a rank changes, the old text is gone; nothing
accumulates [R2 #3; 04 Interface request 4].

**05.3.10 Oath-gated abilities.** `[D]` An ability with a `conduct.*` tag is eligible only for a calling
whose `pool_gate.conduct` lists that axis **and** whose `pole` equals the ability's `conduct_pole`
(positive: vows and oath-bearing callings; negative: dark callings). While the calling that holds it is
suspended by the Fraying (04.9.3), the ability is suspended with it: it stays in its slot, and
`use_ability` refuses it with the reason. These abilities have no `emulate` (a vow's power cannot be
copied by watching) and their `acquisition_paths` list recognition only.

### 05.4 Using an ability

**05.4.1 `use_ability`.** `[D]` Tool #19. Every activation, stretch and emulation runs PR-05-1. The tool
validates, in this order and with the first failure returned as a refusal that names its reason:
(1) **held**: the ability is in a slot (or the mode is `emulate` and 05.5.4 holds), bound if equipped,
not suspended; (2) **timing**: a beat, a rider on a beat of an allowed verb or tag, the holder's unused
reaction, or the hook that fired; (3) **limitation**: every limitation clause that reads state holds
(target tags, bands, flags, conditions, a free hand, speech); (4) **uses**: `uses.remaining ≥ 1`;
(5) **exclusions**: one rider per beat, one sustained working, behavioral-slot priority (the tool
*warns*, it does not refuse, when a new claim would be suppressed by a higher rank already running);
(6) **Focus**: the computed cost (05.6.3) is at most `focus.current`, or the player accepts an overdraw
(05.6.6). A refusal spends nothing: no Focus, no use, no action, no time (01.3.6).

**05.4.2 What an activation spends, and when.** `[D]` Focus and the use are spent when the activation is
**committed**: at the OFFER's commit for a beat or rider, at the player's yes for a reaction or trigger.
They are spent whether the check then succeeds or fails. They are **not** spent when the tool refuses,
when the player withdraws at the OFFER, or when the event the ability answered is cancelled before the
ability resolves (00's edge case: a second `prevent` on an event already prevented keeps its use)
[01.7; R7 §5 Ex.7 Case B].

**05.4.3 One rider per beat.** `[D]` A beat carries at most one `rider` activation. A Form already
running, passives, and levers already established are not riders and are not limited by this rule. This
is the exclusivity that stops "several effects in one action" without adding an action economy of its
own (WoW's global cooldown, 5e's bonus-action patch) [R1 §05 "bonus-action riders"; R3 F-2; INV-11].

**05.4.4 Targets.** `[D]` An ability names its targets over **relationship-state**, never over geometry:
"one being within `band.near`", "each being engaged with you", "one being carrying `cond.exposed`". The
engine checks bands, flags and conditions at commitment. Multi-target abilities use a **spread tag**
(05.10.4), whose selection rule and cap are data. A target that turns out to be illegal at commitment
(it moved; it is not what it seemed) is dropped; if none remain the activation is refused under 05.4.1
and spends nothing [R3 #7; 00.17.1 Q14].

**05.4.5 Durations.** `[D]` Durations use `substrate.yaml#duration_forms` only (SG-28): `rounds:N`,
`intervals:N`, `hours:N`, `watches:N`, `days:N`, `scene`, `conflict`, `until_rest:<type>`, `uses:N`,
`while:<state expr>`, `permanent`. An ability's running effect is an `effect_instance` with a source and
a remaining duration, expired by `h.00.durations`. A `while:` duration ends the instant its expression
is false (a stance ends when the holder is `cond.prone` if its text says so).

**05.4.6 Uses and recharge.** `[D]` + `[T]` Every active ability declares one of these seven recharge
types, each engine-counted and refreshed by a registered handler in phase 3. No recharge exists only in
prose [C:P5; 00.10.9; R3 05.8].

| Type | Data form | Refreshed by | Meaning |
|---|---|---|---|
| **At will** | `cost: {focus: 0}`, no `limits` | n/a | usable every time its timing allows |
| **Focus only** | `cost: {focus: 1–4}`, no `limits` | n/a | limited by the pool alone |
| **Per round** | `limits: {per: round, uses: n}` | `h.05.round_recharge` | reactions and counters |
| **Per conflict** | `limits: {per: conflict_end, uses: n}` | `h.05.conflict_recharge` | "once per fight" |
| **Per scene** | `limits: {per: scene_end, uses: n}` | `h.05.scene_recharge` | the usual limit outside conflict |
| **Per rest** | `limits: {per: rest_short, uses: n}` or `{per: rest_long, …}` or `{per: day, …}` | `h.05.rest_recharge`; `h.05.day_recharge` | `day` refreshes at dawn whether or not the character slept |
| **Once** | `limits: {per: never, uses: n}` | never | single-use-ever; the ability stays held and spent unless its text says it is then retired |

The **refresh ladder** is `round < conflict_end < scene_end < rest_short < rest_long`. A boundary
refreshes every use whose `per` is at or below it on the ladder, so a short rest refreshes per-scene uses
and a long rest refreshes everything but `day` and `never`. `refresh_on: {hook, when}` returns **one**
use (never above the maximum) when its hook fires; the return is an independent trigger and obeys depth.
A rest of quality `interrupted` refreshes nothing; `partial` refreshes as `full` for uses (Focus differs,
05.6.9).

**05.4.7 Sustained workings.** `[D]` + `[T]` An effect with `trait.duration.sustained` lasts while the
holder concentrates (01.17). A character sustains **one** working at a time; beginning a second ends the
first (the player is warned). Sustaining costs no Focus per round. It ends when the holder chooses (a
free activity), becomes `cond.stunned` or `cond.unconscious`, becomes **Spent** (05.6.5), or fails the
concentration check that harm forces (01.17: Endure with Resolve against Easy for S1–S2 harm, Moderate
S3, Hard S4, Very hard S5). The aura and stance slots are separate limits and may run beside one
sustained working.

**05.4.8 Evidence from abilities.** `[D]` An activation is the holder's declared deed: its frame's
primary deed tag is the ability's first tag, and judged evidence is ch.03's to compute. Counted evidence
fires from this chapter's events: `on_focus_spent` carries the ability's first tag and the Focus spent
(`cnt.focus`); a condition applied by an ability feeds `cnt.control`; harm prevented or reduced by one
feeds `cnt.ward` (03.7). Abilities used through a relic write no evidence (00.11.5). An emulation's
evidence lands on the emulated technique's first tag.

### 05.5 The governing principle: stretch, emulate, and what an ability cannot do

**05.5.1 The principle sentence.** `[D]` Every ability's `principle` is one sentence with exactly one
**operation** (a verb) and one **object category** (what the verb acts on), written so that a new use can
be tested against it: "Push a body of air in one direction." "Set a mark on one creature that your
senses can follow." "Turn a blow aside with a shield." "Mend living flesh." The principle is the
derivation the DM reasons from when the player proposes a use the text does not list, in the way a
single physical rule lets every use of Allomantic pushing be derived instead of invented
[R2 #4; BRIEF A2 #12]. Principles are authored to a standard the script checks: at most 20 words, one
sentence, no number.

**05.5.2 Stretch (unstructured use).**

```
### 05.5.2  Stretching an ability                                  [J:flag] [D]
Trigger [T]:        the player declares a use of a HELD ability or license that its scope text does not
                    cover (01.3.4 finds an uncovered clause) and asks to do it with that ability
Loads in:           every situation in which an ability is used (the card travels with use_ability)
License check:      the held ability itself, gate mode `stretch` (01.3.5). A license whose `stretch` is
                    null cannot be stretched: G3 for the excess.
Decisions (J):      1. SAME OPERATION [J:flag] "Does the new use perform the operation the principle
                       sentence names, on something in the principle's object category, differing only
                       in target, scale or form?" True only when both the verb and the object category
                       still apply read literally. False when the use needs a different verb (pull
                       where the principle pushes; create where it moves; know where it marks), a
                       different object category (stone where it says air; a mind where it says a
                       body), or appears on the cannot list (05.5.3). Uncertain -> false (SG-05).
                    2. SENSITIVE UPGRADE [J:flag] (01.3.3) "Would the stretched use give perception,
                       memory, mobility, control, access, awareness or freedom the scope does not
                       already grant?" True -> not a stretch: G3 or G4.
Computation [D]:    PR-05-2. The stretch is ALWAYS a rolled Working, even if the ability normally has
                    check: none: verb = the ability's check.verb (default verb.handle), attribute = the
                    ability's attribute, deed tag = its first tag. DC = the obstacle's DC (01.6.4) +
                    stretch.dc_shift, shown as its own line. Focus = the ability's cost +
                    stretch.cost_add. Reach capped at stretch.reach_cap. The ability's uses are spent
                    as for a normal activation. Its listed effects apply only as far as the new use
                    needs them, at most one severity rung, one condition, or delivered reach in
                    ticks. Grade widens the prices (T-05-6): trained +5 DC, +1 Focus, Limited;
                    expert +5 DC, +1 Focus, Standard; master +0 DC, +1 Focus, Standard. ch.04's Sure
                    Hand adds a Precision lever (it counts toward the two-lever limit).
Stakes:             framed as any beat (01.6.9); a critical failure of a stretched SPELL is a miscast
                    (05.7.5)
State writes:       frame (gate.mode: stretch); Focus; uses; the effects' writes; a ruling record with
                    signature "<ability id>+stretch+<object>" (precedent, 00.15.6)
Narration may not imply: that the stretch is now part of the ability (the next use is a stretch again,
                    at the same price, unless a precedent is reused); success beyond the capped reach
Worst case (J):     decision 1 wrongly true: one beat at DC +5, one more Focus and Limited reach, which
                    is worse than a licensed use by construction, logged with the principle sentence
                    it relied on (class i and iv). Wrongly false: the player is redirected to the
                    crude fallback or a basic verb and may point to the principle; the ruling ledger
                    then holds the answer for next time (class iv).
Examples:           inside: ab.gust ("Push a body of air in one direction") used to blow a cloud of
                      marsh gas off a bridge: same verb (push), same object (air), new target ->
                      stretch (WE-05-2).
                    inside (boundary): ab.flame_lance ("Throw a line of fire at one target") used to
                      light a signal beacon at band.far: same verb, same object, the target is a
                      thing and not a foe -> stretch; reach Limited = the beacon catches, slowly.
                    outside: ab.gust used to pull a dropped letter toward the caster: the principle
                      pushes; pulling is a different operation -> false. Redirect: push it against
                      the far wall and go and get it.
                    outside (boundary): ab.mend_flesh ("Close a wound in living flesh") used on a
                      cracked wooden mast: the object category is living flesh; timber is not ->
                      false.
                    non-example: ab.quarrys_mark ("Fix your aim on one creature you have struck")
                      used "to know where the creature will be tomorrow": that is foresight, a
                      sensitive upgrade (awareness) the scope does not grant -> decision 2 true ->
                      G3; the redirect names deed.arcane.divination and what the mark does give.
Anchor:             yes. Intent verbs: "use my <ability> to", "bend", "turn it to", "do the same but".
                    Knobs: dc (default obstacle + 5; allowed delta: +0 at master grade); focus_cost
                    (default +1; no delta); reach_unit (default: the ability's own; allowed delta:
                    object state or clock ticks when the target is a thing); targets (default one;
                    allowed delta: none upward). Degree table: 01.18.2. Covers: any new use of a held
                    license that keeps its principle. Does not cover: the cannot list; emulation of
                    another's technique (05.5.4).
Basis:              [00.12.4] [01.3.5] [R2 #4] [R: http://www.redcap.org/page/Spontaneous_spell]
                    [R7 §4.4] [DL-05-07]
```

**05.5.3 The cannot list.** `[D]` A stretch, an emulation, a flare or a ruling can never make an ability
do any of the following. Each line is a refusal by lookup, voiced with 01.3.6's redirect:
1. **Change its operation or its object category** (05.5.2 decision 1).
2. **Change the harm family it deals** (a `harm.fire` working stays fire) or add a harm type.
3. **Lift one of its own P12 fields**: act without its limitation, without its weakness, without its
   cost, or beyond its uses.
4. **Outlast its duration form** by more than the Lasting flare's one step, or become permanent.
5. **Reach past its band** by more than the Far flare's one band, or act on a target it cannot
   perceive.
6. **Grant** a license, an ability, a fact about the world's past, an item of lasting value, or a
   standing change the degree table did not deliver (INV-7).
7. **Add an action**, a second rider, or a second sustained working (INV-11; 05.4.3; 05.4.7).
8. **Supply a sensitive upgrade** its scope does not name (01.3.3).
9. **Contradict setting canon** (`canon_impossible`, ch.13): that is G4 for everyone.
10. **Affect more targets** than its spread tag's cap (05.10.4).

**05.5.4 Emulate (learning by observation).**

```
### 05.5.4  Emulating a technique                                   [J:flag] [D]
Trigger [T]:        the player declares an attempt at an ACTIVE ability they do not hold, of a tag
                    where they hold the training license (the domain license, 05.9)
Loads in:           every situation
License check:      lic.training.<tag> whose `emulate` is not null, gate mode `emulate` (01.3.5).
                    Without the training license: G3; crude_fallback of that license; acquisition
                    paths named.
Decisions (J):      1. WITNESSED [J:flag] "Did the character perceive this technique performed, start
                       to finish, by someone or something that holds it?" True only when the scene
                       log holds its use within the character's senses (the engine writes
                       pc.witnessed.<ab id> when an entity uses an ability in a scene the PC is
                       present in and could perceive it: the DM confirms line of sight or hearing as
                       the technique needs). False for hearing it described, for seeing only its
                       result, and for a claim by the player. Uncertain -> false. The Open Art
                       (04.5.3, tier 5) replaces this decision with "true" under the calling's key.
Computation [D]:    PR-05-3. Legal only when all hold: the ability's first tag is at or under the
                    training license's tag; its min_tier <= the grade's technique cap (trained 2,
                    expert 4, master 5; T-05-6); it is active, not oath-gated, not adversary_only; the
                    character does not hold it. Then: the activation runs as written at rank 1 with
                    DC + emulate.dc_shift (aimed), or the targets' resist checks gain a Precision
                    lever (resisted), or the beat it rides takes the DC shift (rider); Focus = cost x
                    emulate.cost_mult (a cost of 0 becomes 1); reach capped at emulate.reach_cap. On
                    a critical failure emulate.crit_fail applies in place of the READ cost when it is
                    worse (for a spell: a miscast one severity rung heavier, 05.7.5). On a success
                    the learning clock clk.learn.<ab id> ticks by delivered reach and NOTHING else
                    is granted (INV-7).
Stakes:             as framed; never lethal by the emulation itself
State writes:       frame (gate.mode: emulate); Focus; the effects' writes; clock; evidence at the
                    emulated technique's first tag
Narration may not imply: that the character now knows the technique; that the result matched a
                    practiced use (reach is capped)
Worst case (J):     WITNESSED wrongly true: one attempt at double Focus, DC +5 and Limited reach, and
                    1 tick on a 6- to 12-segment clock (class i). Wrongly false: the player names the
                    scene; the scene log settles it (class iv).
Examples:           inside: Ash holds lic.training.arcane_fire (trained) and watched a cult adept cast
                      ab.fire_shroud (min_tier 2) across a courtyard -> emulate: DC +5, Focus 2 x 2 =
                      4, Limited reach.
                    outside: the same adept cast ab.rime_spear; Ash has no frost training -> G3, and
                      the fallback of lic.training.arcane_frost is `none`.
                    outside (boundary): Ash watched ab.firestorm (min_tier 5): above the trained
                      technique cap of 2 -> refused: "you saw what he did and none of how".
                    non-example: Wren saw a duelist's riposte once and the player says she "picked it
                      up": a roll never grants a license. With lic.training.martial_blade she may
                      emulate it and tick the clock; without it, she may ask the duelist to teach her.
Anchor:             yes. Intent verbs: "copy", "do what I saw", "imitate", "try their trick". Knobs:
                    dc (default +5; no delta); focus_cost (default x2; no delta); reach_unit (the
                    technique's own); targets (the technique's own; no delta). Degree table: the
                    technique's, with the reach cap. Covers: any active ability of a trained tag that
                    the character witnessed. Does not cover: passives; oath-gated abilities; the
                    powers of creatures (04.10, the Taking); rites (learned from a text or teacher).
Basis:              [00.12.4] [01.3.5] [R7 §4.4, §5 Ex.7] [R: https://www.d20srd.org/srd/skills/useMagicDevice.htm]
                    [04.5.3] [DL-05-08]
```

**05.5.5 Crude fallback.** `[D]` Every license in `data/licenses.yaml` and every ability declares a
`crude_fallback`: either `none` (an untrained person cannot do this at all, which is the case for every
spell) or a basic verb, a method, a DC shift of 0, 5 or 10, a reach cap and a consequence. An ability's
fallback is usually its training license's. The fallback is what a G3 redirect offers (01.3.6); this
chapter's duty is that the field is never missing. The generator script refuses an entry without
`principle`, `stretch`, `emulate` and `crude_fallback` keys (each may be null or `none`, explicitly)
[01 Interface request; INV-7].

**05.5.6 Precedent.** `[D]` Each stretch is logged with the signature `<ability id>+stretch+<object>`.
A later stretch with the same signature reuses the recorded DC source, reach cap and effect mapping
(00.15.6). A stretch never becomes part of the ability: text changes only by rank (05.3.9) or by a
content revision at a boundary (05.12.3) [R3 #10: granted abilities are never reinterpreted mid-life].

### 05.6 Focus

Focus is the one pool that pays for every active ability of every calling [C:P9; 00.3.13]. It is not
Vitality, it is not derived from any attribute, and nothing in this ruleset creates a second pool. In
the fiction it is whatever the character draws on to do more than an ordinary person can in a moment:
breath and nerve for a swordsman, held attention for a thief, the gathered will of a sorcerer, a
priest's standing with what they serve. The codex calls it Focus; no one in the world does (00.1.7).

**05.6.1 The pool.** `[D]` `focus.current` runs from 0 to `focus.max`. `focus.max` is evaluated through
the pass (quantity `focus_max`, family `adjust`):

`focus.max = base + T_high + breadth`, clamped to **12**

| Term | Value | Source |
|---|---|---|
| `base` | 3–5, reference **4** | set at creation by ch.02 inside 00.3.13's envelope; never changes |
| `T_high` | 0–5 | the highest tier among held callings that are not suspended (provisional tiers count, as they do for `power_band`), counting a consolidated calling's specialties at their `tier_reached` (04.8.5), so a consolidation never lowers the pool |
| `breadth` | 0–3 | +1 for each **other** held calling (deed-keyed or oath) at tier 3 or higher |

| Character | focus.max (base 4) |
|---|---|
| no calling | 4 |
| one calling at tier 1 / 2 / 3 / 4 / 5 | 5 / 6 / 7 / 8 / 9 |
| tier 5, with a second calling at tier 3+ | 10 |
| tier 5, with two more callings at tier 3+ | 11 |
| tier 5, with two more callings and an oath calling, all at tier 3+ | 12 |

Growth is therefore history-gated like everything else (P2): the pool deepens when a tier
crystallizes, and it is the only thing about Focus that a tier changes. The rejected alternative, a
per-tier discount on costs (Stormlight's "holds it better with each Ideal"), would have made every cost
in the data a moving number; a deeper pool gives the same felt efficiency with costs that never change
[R2 #8; DL-05-09]. When `focus.max` falls (a lapse, a suspension), `current` is clamped to the new
maximum at once.

**05.6.2 Costs come in five bands.** `[D]` An ability's base cost is one of five values, and the band an
ability may use is bounded by its minimum tier [R1 §05: HERO's discrete brackets stop arbitrage between
near-equal effects; DL-05-11]:

| Focus | Band name | Typical content | Lowest `min_tier` |
|---|---|---|---|
| 0 | **knack** | a rider or permission worth using every time; a branch working (05.7.11) | 1 |
| 1 | **lesser** | one notch above a basic action: a severity rung, a condition, a lever that lasts | 1 |
| 2 | **greater** | a scene-shaping effect, several targets, a hard counter | 1 |
| 3 | **grand** | what a fight or a venture turns on | 3 |
| 4 | **pinnacle** | once-a-day magnitude | 5 |

**05.6.3 What an activation costs.** `[D]` The engine evaluates `focus_cost` in this order and shows the
breakdown in the OFFER:
1. the active rank's base cost;
2. × `emulate.cost_mult` when emulating (a base of 0 becomes 1);
3. + `stretch.cost_add` when stretching;
4. + 1 for each flare (05.6.8);
5. + 1 **relic surcharge** when the ability is held through an item and the holder has no training
   license at or above its first tag (the Honorblade rule: borrowed power costs more and never grows)
   [R2 #9; 00.11.5];
6. ± `adjust` effects (`eff.focus_cost_step`), summed, with these caps: reductions total at most −1 per
   activation and never bring a cost that began above 0 below **1**; increases total at most +2;
7. clamp: a result above **6** is not payable (00.3.13): the tool refuses and names the largest
   component the player could drop.

**05.6.4 Paying.** `[D]` + `[T]` Focus is paid by `update_quantity(focus, −n)` inside `use_ability` at
commitment (05.4.2). The write fires `on_focus_spent` with the ability's first tag, which is what ch.03's `cnt.focus` counter and any subscribed effect read.
Focus is never negative. Costs from 01's menu (`cost.drain`) take Focus only when the beat used an
ability, concentration or a push (01.13.3).

**05.6.5 Spent.** `[T]` + `[D]` When a spend, a drain or an overdraw leaves `focus.current = 0`, the
engine sets `focus.state = spent` and writes the fact `pc.focus.spent` [R2 #8: Stormlight's emptiness
leaves the user deflated]. While Spent:
- every sustained working the character is holding ends (05.4.7);
- beats with `trait.action.concentrate` take an **engine-applied Precision snag** citing the Spent fact
  (−2; outside the two-snag count and inside the ±4 cap, like 01's repetition snags);
- the character cannot flare or push;
- abilities that cost 0 Focus still work; so do passives, items, and everything the basic verbs cover.
  For a caster this includes the **branch working** (05.7.11), so Spent is weak, never weaponless: a
  Spent tier-3 caster beats one foe of its band 81–91% of the time on the working alone (06-conflict-sim J2)
  [revision: I-009].
Spent ends the moment `focus.current ≥ 1`, by any channel. It is not a condition and nothing cleanses
it but Focus. *Narration may not imply* collapse, unconsciousness, harm, or any lasting mark: Spent is
being out of reserves, and the two effects above are all it does.

**05.6.6 Overdraw.** `[D]` + `[T]` A character who lacks the Focus for an activation may pay the
**shortfall** from the body. This is the price of power the fiction always promised and the reason a
caster at 0 is still dangerous [R5 MG-07; R2 §05 Feruchemy and Hemalurgy as costs paid elsewhere].
- **Price.** A shortfall of 1, 2 or 3 Focus deals S2, S3 or S4 harm (3, 5 or 8 Vitality) tagged
  `harm.mind.strain` to the character, through `apply_harm(lethal: false)`, with no reduction applying,
  and adds one stack of `cond.exhausted` lasting `until_rest:rest_long`. A shortfall above 3 is not
  payable.
- **Limits.** Three overdraws between long rests (`cond.exhausted` has three stacks; the engine counts
  `overdraws_since_long_rest`). The tool refuses an overdraw that would bring Vitality to 0 or below, so
  overdraw can never Stagger its user, and a Staggered or Dying character cannot overdraw at all.
- **The OFFER says so.** An overdraw is never automatic: `use_ability` returns the price, and the player
  accepts or withdraws. It leaves the character Spent.
- An overdraw is not available for a push, a flare (drop the flare instead) or the Taking.

**05.6.7 Push.** `[D]` Any character, with or without abilities, may spend **1 Focus** on their own
declared, rolled beat to **push** it: the player chooses **reach +1 rung** or **stakes −1 rung**. This is
the universal use of Focus, and it is why Focus matters to a character with no calling from the first
scene [C:P2 baseline floor; R3 #9 "spend Focus to push Effect"; 01 Interface request].
- **Where.** Only on a beat whose primary deed tag (or an ancestor) carries competence **above the PC
  floor** for this character: you can push what you are trained at. Not on a resisted check (it is not
  a declared beat), not on an Oracle question, not while Spent.
- **How.** Declared at the OFFER, before commitment; once per beat; it is a step effect
  (`eff.reach_step` or `eff.stakes_step`, family `step`), so it counts inside the ±2 effect-step cap and
  the ladders' clamps (framed reach never above Great; stakes never below Safe). It is **not** a lever:
  it cites no fact, does not count toward the two-lever limit, and never changes the roll or the DC.
  It may be combined with 01.7.3's ambition or caution trade.
- **License.** `lic.focus.push` (`data/licenses.yaml`), held by every character (license kind `universal`,
  00.12.1). The spend fires `on_focus_spent` with the beat's primary deed tag, which 03's `cnt.focus` credits.
- **Grit.** The push may instead be declared as **grit** (07.2.5): the beat ignores status penalties from
  wounds, and gains no reach from the push. Same price (1 Focus), same once per beat, declared at the OFFER
  like the push [integration: IR ch.07 to 05].
- *Why reach or stakes and never +2 to the roll:* a flat accuracy purchase is the textbook ability tax
  (5e's −5/+10 turned inside out): it would be right on every roll and would make Focus a second
  modifier family. Reach and stakes change what a result is worth, and the lever stays the only
  circumstance currency [R1 M-24; 00.3.9; DL-05-12].

**05.6.8 Flare.** `[D]` When activating an ability the holder may **flare** it: pay **+1 Focus** for one
of the six flares the ability's `flares` field lists. A holder at grade `master` in the ability's
training license may take two different flares on one activation (+2). This is Allomancy's flare (more
for much faster burn) and Path of Exile's support gem (a behaviour change that raises the cost and
carries a stated drawback) in one closed list [R2 #8; R3 05.3; DL-05-13].

| Flare | Effect (a step or a core effect; inside every cap) | Listed on an ability when |
|---|---|---|
| **Hard** | the harm it deals is one severity rung heavier; if it deals no harm, the condition it applies is | it deals harm or applies a condition |
| **Far** | its range is one band further | it names a band |
| **Wide** | one more target that the ability's own targeting rule allows (inside the spread cap) | it is a Working on one target |
| **Lasting** | its duration is one step longer: `rounds:N` → `scene`; `scene` or `conflict` → `until_rest:rest_short`; `intervals:N` → `hours:N` | it has one of those durations |
| **Quiet** | it loses `trait.sense.loud`, `.audible` and `.visible` (its *effect* is still perceivable where it lands), and the flare tell below | it carries a sense trait, or it is a spell: every working of magic is perceived through its branch's limitation (the spoken word, the shown sign, the stirred source; 05.7.2) [revision: I-008] |
| **Sure** | a Precision lever on its aimed check, or a Precision snag on each target's resist check (counts toward the two-lever or two-snag limit) | its `check` is `aimed` or `resisted` |

- **The tell (the drawback).** A flared activation is `trait.sense.visible` and `trait.sense.audible`
  whatever it was before: anyone who can perceive the character knows they drew deep (a glow, a held
  breath let out, a word spoken too loudly). Only Quiet removes it, and Quiet is then the one flare
  taken unless the holder is a master.
- **The risk.** A flared **spell** that critically fails miscasts one severity rung heavier (05.7.5).
- A flare is refused when the cost would pass 6, while Spent, and on an emulation or a stretch (both are
  already beyond the holder's practiced use).

**05.6.9 Recovery by rest.** `[D]` Handler `h.05.focus_recover` runs in phase 3 of the three rest
boundaries, after 07's `h.07.rest_recovery`, and reads the rest's `quality` from the boundary event
(contract Q1). Rest durations are 00.7.2's.

| Rest | Quality `full` | Quality `partial` | Quality `interrupted` | Limit |
|---|---|---|---|---|
| `breather` (1 interval) | **+1** | +1 | 0 | counts toward at most **2** Focus-restoring breathers between short rests (`breathers_since_short_rest`); further breathers restore 0 Focus |
| `rest_short` (1 hour) | **+ half of `focus.max`, rounded up** | + a quarter of max, rounded up | +1 | the first **2** short rests of a day restore this much; later ones restore as a breather |
| `rest_long` (a watch of sleep) | **to `focus.max`**; reserve banking resolves (05.6.12) | to three quarters of max, rounded up (never lowering `current`) | as a `rest_short` of quality `partial` | at most one per day (00.7.2) |

- **Resonant place.** When the rest is taken at a place whose `resonance` list (ch.10/13) contains a tag
  at or above the key of a calling the character holds, or at or above the first tag of an ability they
  hold, a `breather` or `rest_short` restores **+1** more (Cradle's matched aura: the place refills what
  it resembles) [R2 §05 recovery channels].
- Recovery never raises `current` above `max`. A rest's uses-refresh is 05.4.6's.
- *Design note.* Focus returns in three sizes that match the three rests, so the choice of when to stop
  is a real one: a breather buys one more activation, an hour buys half the pool, and each costs time
  that 10's checks and 11's clocks charge for [R: https://2e.aonprd.com/Rules.aspx?ID=276 (ten minutes
  restores one point); DL-05-14].

**05.6.10 Generation: how calling identity shows.** `[D]` Focus is one currency; *where it comes from*
differs by who the character is. Each deed family's **Focus trigger** (04.5.4;
`callings.yaml#families[].focus_trigger`) restores 1 Focus when its hook and condition hold, once per
scene from tier 2 and twice per scene from tier 4. This chapter confirms ch.04's nine triggers
unchanged and owns their bounds:

| Family | The trigger restores 1 Focus when… | What it feels like |
|---|---|---|
| martial | a deed of the calling defeats a foe at or above the character's band | momentum (rage and fury designs) |
| guile | a deed of the calling critically succeeds against one who never saw it coming | the clean job |
| wilds | a breather is completed outside any settlement | the land gives back |
| lore | a deed of the calling uncovers a clue or a sealed fact | the click of understanding |
| arcane | a working of the calling critically succeeds | the formula ringing true |
| divine | the calling lifts a condition from another, or brings another back from Dying | grace returned for grace given |
| primal | dawn comes under open sky or in wild country | the turning day |
| influence | a deed of the calling moves someone's standing upward | the room warming |
| craft | a deed of the calling completes a project clock | the finished thing |

Bounds, all engine-counted:
- **The generation cap.** From triggers, composites, boons and abilities of the Reserve form together, a
  character gains at most **3 Focus per scene** (`generated_this_scene`, reset by `h.05.scene_recharge`).
  Rests, consumables and the reserve are outside this cap and have their own.
- A hybrid has no Focus trigger (it has a composite, 04.5.4); a vow or dark calling has a boon. A
  character with two specialist callings has two triggers, each with its own per-scene uses, under the
  one cap.
- A trigger fires only on a depth-0 event (INV-12). A defeat made by a declared beat is depth 0, and so
  is one made by a condition's scheduled periodic harm (00.10.8 lists both as causal roots), so the
  martial trigger fires on either; a defeat caused by another triggered effect is depth 1 and does not
  fire it.
- Why this resolves identity without a second resource: the pool, the costs and the bookkeeping are one
  system for a character with three callings; only the refill rule differs, and it is one line per
  family [R3 05.7, #13; C:P9; C:P14 "cheap, structural feel difference"; DL-05-10].

**05.6.11 Consumables and other sources.** `[D]` An item or effect restores Focus only through
`eff.restore {quantity: focus}` (08 owns the items). Bound: at most **4 Focus between long rests** from
consumables (`restored_by_consumables_since_long_rest`); past it a draught restores nothing and the
codex says so before it is drunk. A being's effect that restores another's Focus (a blessing, a song)
is an ability of the Reserve form and counts against the *recipient's* generation cap.

**05.6.12 The reserve (bank and draw).** `[D]` A bounded second way to hold Focus, inside the one pool:
Feruchemy's shape, in which what is stored now is exactly what is drawn later [R2 #8, §05; DL-05-15].
- **License and vessel.** Requires `lic.focus.reserve` (learned from a mentor or a text, or from an
  origin; `data/licenses.yaml`) and a **vessel**: one item tagged `item.tool.implement` that the
  character has kept for at least a season or made themselves (a fact on the item). One vessel at a
  time.
- **Capacity** `R` = 2, or 3 when `T_high ≥ 3`, or 4 when `T_high = 5`.
- **Bank.** On completing a `rest_long` of quality `full`, the player may declare `n` points
  **charging** (`n ≤ R − banked`). Until the next completed `rest_long`, `focus.max` is lower by `n`
  (an `adjust` of −n). At that next long rest, if the character was never Spent in between, the `n`
  points enter `reserve.banked`; if they were, the charge is lost and the maximum returns.
- **Draw.** At any time the vessel is in hand or worn, as a free activity (no action, no check), the
  player moves any number of banked points into `focus.current`, up to
  `focus.max`. Drawn points are gone from the reserve. The ratio is 1 : 1, always.
- **Separate fields (P12).** *Limitation:* `R` points, charged a day ahead. *Weakness:* the reserve
  lives in the vessel; without the vessel in hand or worn, it cannot be drawn, and whoever holds the
  vessel and the license can draw it. An effect that drains Focus drains `current`, not the reserve.
  *Cost:* a day lived at a lower maximum for each charge.
- The reserve is outside the generation cap and the consumable cap; its own bound is `R`.

**05.6.13 Losing Focus to others.** `[D]` An adversary power or hazard may drain Focus only through
`eff.drain {quantity: focus, units}` with units = U(severity) of the effect (1, 1, 2, 3, 4), resisted
by Endure with Resolve unless it is a declared cost of the character's own failed beat. A character
loses at most **4 Focus per scene** to drains. A power that would empty the pool outright (the
"aluminum" case) is legal only for an adversary of threat band 4 or 5, and only when the adversary's
tells name it before it is used (09) [R2 §05: a zeroing effect is a rare, telegraphed weakness-exploit].

**05.6.14 What Focus is not for.** `[D]` Focus never buys an action (INV-11), a reroll (that is `fate`,
01.16), a bonus to a roll (05.6.7), a license (INV-7), or Vitality except through an ability whose
effect restores it. No effect converts Vitality into Focus except overdraw's fixed, bounded price.

### 05.7 Magic

Magic is a named subsystem and not a separate engine [00.17.1 Q20; R5 G-16]. A spell is an ability; a
rite is a clock; a mage's training is a license. What makes it *magic* is four things this part adds:
a **source** with its own way of failing, a **signature** each branch carries in P12's three fields,
**rites** for what a single beat cannot hold, and **learning** by teacher, text and observation. What
magic is in the world (where it comes from, who may use it, what it can never do) is ch.13's canon; this
chapter fixes what canon must answer (05.7.10).

**05.7.1 A spell.** `[D]` A spell is an entry of `data/abilities.yaml` with `kind: spell`: its first tag
is under `deed.arcane`, `deed.divine` or `deed.primal`, and it carries `trait.nature.magical`. It
occupies a slot, costs Focus, has ranks, composes through the substrate and is budgeted like every other
ability. There are no spell slots, no spell lists by calling, and no preparation step: a held spell is
usable whenever `use_ability` validates it [C:P9: 5e unified multiclass slots for the same reason this
game unifies everything]. To cast any spell of a school (a level-2 magic tag) a character must hold that
school's **training license** (05.9); an ability held without it (a relic, a gift) works at the relic
surcharge (05.6.3).

**05.7.2 The three sources.** `[D]` Each magic branch is one source, and each source has a fixed
signature. The signature is applied by the engine to every spell of the branch, so a new spell inherits
it at no authoring cost, and a hybrid caster carries two signatures over one Focus pool.

| | **Arcane** (`deed.arcane`) | **Divine** (`deed.divine`) | **Primal** (`deed.primal`) |
|---|---|---|---|
| Source | formula, worked by the caster's own knowledge | power granted by a **keeper**: a god, an oath, a pact | the living world and its spirits |
| Casting attribute | Intellect | Presence | Resolve |
| **Limitation** (what every working needs) | **word and gesture**: `trait.action.speech` and `trait.action.manipulate` (a voice and a free hand) | **the sign and the regard**: `trait.action.speech` (the invocation), the keeper's sign worn or in hand (an item tagged `item.tool.implement`), and the keeper's regard (05.7.4) | **the source present**: the element, growing thing, beast, weather or spirit the working acts through is in the scene (05.7.3) |
| **Weakness** (what it is open to) | every arcane working can be **countered and unwoven** by arcane warding (05.7.7), and is audible when cast | profane ground and profane wards oppose it: a Precision snag on divine workings where a fact marks the place `desecrated` | **dead ground**: inert where canon or a fact marks the place lifeless, sealed or iron-bound (G4 there) |
| **Cost** beyond Focus | none | none | none |
| **Miscast** (05.7.5) | **Backlash**: raw force turns on the caster | **Silence**: the keeper withholds | **Debt**: the place is owed |
| Family Focus trigger (04) | a working critically succeeds | lifting a condition; bringing back from Dying | dawn in wild country |

*Why these three attributes:* each lies in ch.04's list for its family's one attribute increase, so a
caster's growth and casting agree; and no one attribute serves two sources, so a hybrid of two magics
pays for breadth with a split (P4) [04.2.2; 00.4.2].

**05.7.3 The source present (primal).**

```
### 05.7.3  The source present                                     [J:flag]
Trigger [T]:        a primal working is declared (first tag under deed.primal)
Loads in:           situation.* (travels with every primal ability card)
License check:      the ability, or lic.training.primal_* for a small working
Decisions (J):      1. PRESENT [J:flag] "Is the thing this working acts through established in the
                       scene?" True only when a fact, the place's terrain tags, the weather record or
                       an entity in the scene supplies it: open flame or embers for fire; standing or
                       running water; bare earth or stone underfoot; moving air (any place open to the
                       sky, or a draught recorded as a fact); living plants; the beast addressed; a
                       spirit whose presence the Oracle or a fact has established. False when it rests
                       on the player's assertion ("surely there is a root somewhere") : that is an
                       Oracle question first (00.12.7). Uncertain -> ask the Oracle.
Computation [D]:    present -> the working proceeds. Absent -> G4 for this method (reach Zero), with
                    the redirect naming what would supply the source. A source the caster CARRIES
                    counts (a lit torch, a waterskin poured out, a potted seedling) and is used up by
                    a working of Standard reach or more when it is that small.
Stakes:             none of its own
State writes:       the cited fact id in the frame (INV-20)
Narration may not imply: a source that no fact holds
Worst case (J):     PRESENT wrongly true: one working cast where it should have been redirected; its
                    cost and check still apply (class i). Wrongly false: the player names the fact;
                    no Focus was spent (class iv).
Examples:           inside: ab.root_snare in a forest clearing (terrain.forest) -> present.
                    boundary: ab.root_snare on a flagstone floor with moss in the cracks, the moss
                      recorded when the cellar was described -> present (the fact exists).
                    outside: ab.root_snare in a bare iron cell -> absent -> G4; "nothing grows here
                      to answer you".
                    non-example: ab.gust indoors: moving air needs a recorded draught or an opening;
                      the player's "there must be a draught" is an Oracle question (Likely in an old
                      keep, Unlikely in a sealed vault).
Anchor:             no
Basis:              [R2 §05 Cradle: aura of a matching place] [R7 §5 Ex.11] [00.12.7] [DL-05-18]
```

**05.7.4 The keeper's regard (divine).** `[D]` Every holder of a divine training license has a
**keeper** recorded as a fact when the license is acquired (`pc.keeper.<school> = <power, order or
oath>`; ch.13 supplies the powers and their conduct axes). Divine workings are usable while the keeper's
regard holds:
- for a character whose divine calling carries an oath: while the calling is below Fraying stage 2
  (04.9.3 suspends the tier's grants at stage 2 and the calling at stage 3);
- for a character with divine training and no divine calling: while their standing with the keeper's
  faith (11) is Neutral or better.
When regard fails, `use_ability` refuses the school's spells with the reason, and the redirect names
atonement (04.9.4) or mending the standing. This is the whole of "losing your powers" in this ruleset:
it is a state the player can read in the codex before acting, never a judgment made at the moment of
casting [C:P5 "a Paladin's ability to atone"; R2 #6].

**05.7.5 Miscast.** `[T]` + `[D]` A working of magic is **miscast** when (a) its aimed check is a
critical failure, or (b) it is resisted and **every** target critically succeeds. The miscast **replaces**
the critical failure's heavier menu cost (01.9.2); it is never added to it.

- **Severity.** For (a): the critical-failure severity of the frame's stakes (Safe S1, Risky S3, Dire
  S4; 01.18.2). For (b): S1. One rung heavier if the working was flared or emulated (to a maximum of
  S4).
- **What happens** is fixed by branch and severity (`abilities.yaml#miscast`), applied by the engine:

| Severity | Arcane **Backlash** | Divine **Silence** | Primal **Debt** |
|---|---|---|---|
| S1 | 1 harm (`harm.arcane.raw`) to the caster | this ability cannot be used again until `scene_end` | the caster's next primal working this scene costs +1 Focus |
| S2 | 3 harm | this ability is silent until the next `day` boundary (dawn) | every primal working costs +1 Focus until `scene_end` |
| S3 | 5 harm and `cond.dazed` for `rounds:1` | every spell of the school is silent until dawn | every primal working costs +1 Focus until the caster makes an **offering** |
| S4 | 8 harm, `cond.dazed` for `rounds:1`, and every arcane working the caster is sustaining ends | every divine spell the caster holds is silent until dawn, and the keeper's rite of purification (`rit.purification`) or a second dawn is needed to end it | the debt of S3, and one stack of `cond.exhausted` until `rest_long` |

- **Backlash** is applied with `apply_harm(lethal: false)` unless the frame itself was lethal (INV-6).
- An **offering** is a free activity at a `breather` in a place where the source is present: the caster
  gives up 1 supply, or an item, or an hour of tending the place, and the debt ends.
- *Narration may not imply* any consequence the row does not list: no lasting corruption, no change of
  nature, no attention from an entity, unless a rite's own failure costs say so.
- *Why a table by branch:* the three sources fail differently so that they feel different to live with,
  using only core effects (harm, restrict, cost step, one condition) [R5 MG-07; R2 §05 P12 levers by
  source; R: https://en.wikipedia.org/wiki/Mage:_The_Ascension (Paradox as the price of visible
  impossibility); DL-05-19].

**05.7.6 Small workings.**

```
### 05.7.6  Small working                                          [J:flag] [D]
Trigger [T]:        a holder of a magic training license declares a small use of that school that no
                    held spell covers ("I light the candle with a word", "I chill the wine", "I make
                    the shutters rattle")
Loads in:           every situation
License check:      lic.training.<magic school>, scope clause "small workings" (G2)
Decisions (J):      1. TOOL-EQUIVALENT [J:flag] "Could an ordinary person holding a common tool do this
                       in the same time?" True only when a named mundane tool or act would produce the
                       same result at the same scale: flint and steel, a fan, a bucket of water, a
                       cupped hand, a thrown pebble's noise, a knife's small cut in cloth. False for
                       anything that harms a being, applies a condition, moves a being, opens what is
                       locked or sealed, reveals what is hidden, or works beyond band.close. Uncertain
                       -> false.
Computation [D]:    true -> verb.handle with the school's casting attribute and the school's tag as
                    deed tag; no Focus; no use; reach capped Limited; normally no roll (01.4: not
                    uncertain and not costly). If circumstances make it uncertain and costly, frame
                    it against an Easy obstacle. The result is recorded as a fact (a lit candle is a
                    fact a later beat may cite as a lever, 00.3.9 a). It carries the branch's
                    limitation (voice and hand; the sign; the source present).
                    false -> not a small working: a held spell, a stretch of one, an emulation, or G3.
Stakes:             Safe unless framed otherwise
State writes:       the fact the working establishes
Narration may not imply: harm, a condition, or an effect larger than the tool would give
Worst case (J):     wrongly true: one tool's worth of effect without the tool (class i).
Examples:           inside: a fire-trained sorcerer lights a pipe, a candle across the table, a fuse
                      held in the hand.
                    boundary: lighting a hayrick ten paces away: a torch could, at that distance,
                      only by being thrown -> beyond band.close -> false; it is a stretch of a fire
                      spell or a thrown torch.
                    outside: "I heat the guard's sword hilt so he drops it": harms or hinders a
                      being -> false -> a spell (a stretch of ab.flame_lance, or G3 without one).
                    non-example: "I make a small light and so I can see in the dark like a cat":
                      the light is a small working; seeing like a cat is a sensitive upgrade no
                      candle gives.
Anchor:             yes. Intent verbs: "a little magic", "with a word I", "a cantrip to". Knobs: dc
                    (default no roll; allowed delta: Easy tier); attribute (the branch's); reach_unit
                    (object state); time_cost (the tool's). Covers: tool-equivalent effects of a held
                    school. Does not cover: anything on the False list above.
Basis:              [R2 §05 MoL: mastery makes small things free] [C:VII] [01.4.1] [DL-05-20]
```

**05.7.7 Sensing, unweaving, countering and dispelling.** `[D]` [R5 MG-08; R2 §05 "negation is mandatory
for every mage"]
- **Sense.** Every magic training license lets its holder Observe for `trait.nature.magical` effects of
  **their own branch** within `band.near`: against the effect's stored effect DC if its maker concealed
  it, else Moderate. Delivered reach gives, in order: that magic is here; its branch and school; its
  maker's signature (if the character has met it before); what it does. Other branches' magic is read
  only with `lic.training.lore_arcana` or a spell that says so.
- **Unweave your own.** A caster ends any working they are running as a free activity.
- **Effects carry their DC.** When a lasting magical effect is created, the engine stores its maker's
  effect DC on the `effect_instance` (stable numbers, anchor property 6). Everything that opposes the
  effect later rolls against that stored number.
- **Dispel** (an existing effect): `ab.unbinding` (arcane, `deed.arcane.warding.dispelling`),
  `ab.cast_out` (divine, exorcism: possession, the works of undead and fiends) and `ab.lift_the_hex`
  (primal, curses) are Workings whose aimed check runs against the stored effect DC. Delivered reach 1
  suppresses the effect for `rounds:3`; 2 ends it; 3 ends it and tells the dispeller its maker's
  signature; 4 also ends one more effect of the same maker in the scene.
- **Counter** (a working as it is cast): `ab.counterspell` (arcane, `deed.arcane.warding.countering`) is
  a Reaction on `on_declare` of another's magical working within `band.near`; its aimed check runs
  against that caster's effect DC; a success prevents the working (which still spends its caster's Focus
  and action). Divine and primal workings are countered at a Precision snag (the formula is not the
  counterer's own). There is no general counter outside arcane warding: that is arcane's side of its own
  weakness.
- Without those abilities, a holder of the right training may attempt them by **emulation** if
  witnessed (05.5.4), and anyone may use the crude fallback of the effect itself where it has a physical
  anchor (break the circle, burn the fetish: `verb.force` at the object's tier).

**05.7.8 Healing and its limits.** `[D]` Magical healing restores **Vitality** through `eff.restore`
and removes conditions through `eff.cleanse`. It does not remove wounds, marks or afflictions unless the
ability or rite says so by id (those are 07's), and it never raises the dead (ch.13's canon decides
whether anything does). Each being accepts at most **2 healing effects that restore Vitality between its
long rests** (`healings_since_long_rest`, a counter on the recipient, reset by `h.05.rest_recharge`);
a third restores 0 and the tool says so before Focus is spent. The cap is what stops Focus from being
converted into unbounded Vitality across a day, and it is the recipient's limit, so two healers do not
double it [R5 HR-09: Worlds Without Number's System Strain; DL-05-23].

**05.7.9 Magic and the gate.** `[D]` Magic changes what is G4 for its holder and for no one else. A
30-foot chasm is Beyond for a jump and Standard reach for `ab.long_step`. The pipeline is unchanged: the
spell is the license (G2), the frame is computed, the OFFER shows the DC, the Focus and the stakes, and
the sensitive-upgrade test (01.3.3) is answered by the spell's scope text. "It's magic" is never a
reason: a spell does its literal text, a stretch keeps its principle, and a wish the pool does not hold
is a rite to be designed (05.8.4) or a G3 with paths.

**05.7.10 What setting canon must supply.** `[D]` Chapter 13 owns these; until it is written the defaults
in brackets apply, and each is a fact the Oracle treats as settled:
1. `canon_impossible` for magic: what no working can do for anyone [true resurrection; travel through
   time; creating a soul; reading a mind that is not present; destroying a keeper].
2. The **source** of each branch in the world's own words, and whether anyone can learn each or a gift is
   needed [arcane: anyone literate with a teacher or a text; divine: anyone a keeper accepts; primal:
   anyone a place or spirit accepts].
3. The **keepers**: each power, its conduct axes, its sign, its faith as a faction (04, 11).
4. **Places of power**: `resonance` tags on places (05.6.9), `desecrated` and dead ground (05.7.2).
5. How common **spirits** are, for the Oracle's odds [rare: Unlikely in any given place; Likely at a
   place with `resonance`].
6. Whether magic is lawful, feared or licensed where the game begins (a `trait.sense.visible` working in
   a market is a method consequence under 01.11.2 when it is not).
7. Named **components** for rites by price band (08), and where texts and teachers are found.
8. Any school canon closes or opens [none closed; `deed.arcane.necromancy.raising` and `deed.divine.pact`
   write conduct evidence when used on the unwilling, 03].

**05.7.11 The branch working.** `[D]` `[revision: I-009]` Every magic branch has one **branch working**: the
source used raw, without a school's shaping. It is the caster's equivalent of a Strike with a weapon they
are trained in, so that a caster at 0 Focus is weak and never weaponless [06.10.6; 06 Interface request
(b) to 05; R5 MG-07].

| Branch | Working | Reach and target | Harm | Its own touch |
|---|---|---|---|---|
| Arcane | **Force Bolt** (`ab.force_bolt`) | one being or object you can see within `band.near` | force (`harm.arcane.force`) | a critical success also pushes the target one band away |
| Divine | **Rebuke** (`ab.rebuke`) | one being within `band.close` that can see the keeper's sign or hear the invocation | radiant for a sacred keeper, necrotic for a profane one | one rung heavier against the opposed nature (`creature.undead` or `creature.fiend` for a sacred keeper; `trait.nature.sacred` for a profane one) |
| Primal | **Wild Lash** (`ab.wild_lash`) | one being within `band.near` of you and of the source present (05.7.3) | the source's: piercing (growing things), crushing (stone, water), cutting (wind) or fire | the target is off-balance until the end of its next turn |

1. **Held through training, in no slot.** A character who holds any training license of the branch with
   its `requires` met (05.9.4) holds that branch's working. It has `slot_class: license`: it occupies no
   slot, is never picked, learned, taught, absorbed, gifted or bound to an item, and is not counted by
   05.2.9's one-of-each rules. Losing every license of the branch (or the keeper's regard, 05.7.4) loses it.
2. **The school it is cast through.** The frame's deed tag is one level-2 school of the branch whose
   training license the caster holds (the player names it; default: the highest competence). Competence,
   ch.03's evidence, `cnt.focus` from a push, the stretch grade and the flare count all read that school.
3. **Rank by grade.** Rank 1, 2 or 3 at grade `trained`, `expert` or `master` in that school's license
   (05.9.2): Moderate, Heavy or Grievous harm, shifted by delivered reach like a Strike. These are exactly
   06.4.5's mastery steps for a weapon, so a caster's baseline grows when a fighter's does and never
   beyond it.
4. **Cost and resolution.** 0 Focus, at will, timing `beat`; anchored to `verb.strike` (one action,
   06.1.3) and aimed against Guard with the branch's casting attribute. It carries its branch's
   limitation, weakness and miscast like any spell (05.7.2, 05.7.5). It accepts the push (05.6.7) and the
   flares its record lists; while Spent neither is available, but the working is.
5. **What it is not.** It shapes nothing: it does not burn, freeze, bind, charm, ward or linger. A shaped
   effect is a spell of a school; a tool's worth of effect is a small working (05.7.6).

*Budget* (05.11): allowance 4 / 6 / 8 at ranks 1–3 (tier term 2 / 4 / 6, beat 2, no Focus); values 3–4 /
4–6 / 6–7. *Simulated* (`06-conflict-sim.py` section J, 20,000 fights a row; ch.02's `sim02.py`): a new
caster (+5) beats one T2 foe 92.8–93.6% on the working alone (a staff gave 51%); a Spent tier-3 caster
beats one T3 foe 80.7–91.0% (74.5–86.8% when the T3 Fends, as 09's templates do), where it won 0.4%
before; at every band the working stays below the martial specialist with no Focus (P3 81–91% against
99.7%; P4 11–48% against 87%; P5 7–30% against 80%). Focus still pays as much as it pays a fighter:
pushing the working raises a P3 caster's odds against one T4 from 34% to 55% (a fighter's push: 62% to
84%) and against two T3 from 26% to 47% (73% to 90%) [DL-05-31].

### 05.8 Rites, research and learning

**05.8.1 A rite.** `[D]` A **rite** (`rit.*`, `data/rituals.yaml`) is magic too large for one beat:
a clocked extended task (01.14.6) with a license. It is known, not held: a rite takes no slot (05.2.3).
A character **knows** a rite when they have its text (an item with the fact `teaches: rit.*`) or were
taught it, **and** hold the training license of its first tag at the rite's `grade` or higher. The list
is closed at 24 authored rites plus rites designed in play (05.8.4) [C:V; R5 MG-04;
R: https://ironsworn-rpg.fandom.com/wiki/Assets (rituals as a fixed set of assets)].

**05.8.2 Performing a rite.** `[D]` PR-05-5. In summary:
- **Begin.** Requirements are checked: knowledge and grade, every listed **component** in hand (08 prices
  them by the band named), the place (if the rite names one), the number of trained participants, and
  the rite's Focus (paid once, at the start, by the leader). The engine creates two racing clocks from
  the rite's template: the **progress** clock (4, 6, 8 or 12 segments, public) and the **strain** clock
  (4 segments, public, kind `danger`).
- **Each step** is one extended beat by the leader: an aimed check with the branch's casting attribute
  and the rite's first tag against the rite's stored DC tier. Time advances by `time_per_tick` through
  `advance_time`, so every boundary handler runs and an interrupt may halt the step with its time
  unspent (00.7.8). Progress ticks by **delivered reach**. A failure ticks strain by U(severity) of the
  frame's cost and applies one entry of the rite's `failure_costs`. Helpers use Help (01.14.8) if they
  hold the training.
- **Complete.** Progress fills first: the rite's `effects` apply, with the leader's effect DC stored on
  anything lasting; components are consumed.
- **Fray.** Strain fills first: the rite fails, components are consumed, and the leader suffers a miscast
  of the rite's branch at S3 (05.7.5).
- **Leave it.** A rite left untended loses 1 progress per `watch` (the clock's `decay`); at 0 it is void
  and the components are kept.
- A rite inside a conflict is played round by round only if its `time_per_tick` is rounds; any longer
  rite cannot be advanced while a conflict runs.

**05.8.3 What rites are for.** `[N]` Rites hold the magic of scale and permanence that would break a
fight if it were a spell: warding a house, calling rain on a valley, questioning the dead, binding a
spirit, consecrating ground, laying or lifting a curse, sending word across a kingdom. Their price is
time, material and exposure to the world's clocks, never a large Focus number
[R: https://earthdawn.fandom.com/wiki/Spellcasting (more threads, more time);
R: https://www.dungeonworldsrd.com/classes/wizard/ (Ritual)].

**05.8.4 Designing a rite (magical research).**

```
### 05.8.4  Designing a rite                                       [J:rung] [J:enum] [D]
Trigger [T]:        the player wants a magical effect that no held ability, stretch, emulation or known
                    rite gives, and chooses to research it
Loads in:           situation.downtime.project, situation.investigation.research
License check:      a training license of the effect's school at the grade the scale needs (below);
                    without it: G3 (find a practitioner; commission it, 15)
Decisions (J):      1. EXPRESSIBLE [J:enum] Map the wanted effect to effect references: (a) the effects
                       of an existing ability at a larger scale; (b) one to three core or 05-block
                       effects with parameters inside their declared ranges; (c) neither. Default
                       when unsure: (c). (c) -> the effect is beyond the art (G4 if canon forbids it,
                       else "no one knows how": a thread for 11, not a rite).
                    2. SCALE [J:rung] (T-05-8)
                       personal: one willing being or one object in hand; lasts a scene to a day.
                         Typical: a charm against one named poison. Boundary: a ward on one door.
                       local: a room, a small group, or one unwilling being; lasts days. Typical:
                         a ward on a house's doors. Boundary: a curse on one named person.
                       site: a building, a grove, a company of people; lasts a season. Typical:
                         consecrating a chapel. Boundary: hiding a camp of thirty from scrying.
                       regional: a valley, a town, a host; lasts a season or leaves a permanent
                         mark. Typical: rain on a valley. Boundary: closing a mountain pass with snow.
Computation [D]:    PR-05-6. The scale row fixes: research clock (8 / 8 / 12 / 12 segments, a project,
                    ticked by a research week: delivered reach, ch.15); the grade needed (trained /
                    trained / expert / master); the new rite's progress clock (4 / 6 / 8 / 12), DC
                    tier (Moderate / Hard / Very hard / Legendary), Focus (1 / 2 / 3 / 4), and the
                    NUMBER of conditions (1 / 2 / 3 / 4). The engine draws that many conditions from
                    tbl.05.rite_conditions (roll_table, no repeats); the DM fills each condition's
                    specifics only from established facts or the Oracle. Completing the research
                    clock writes a new entry rit.custom.<n> with lifecycle: provisional and a ruling
                    record. It becomes permanent when performed to completion twice; if never
                    completed by the second season boundary it is retired (the notes remain: the
                    research clock restarts at half).
Stakes:             research beats are Safe or Risky as framed by 15; the rite itself as 05.8.2
State writes:       project clock; the rite entry; ruling ledger; a thread when a condition is a quest
Narration may not imply: that the rite will work (it has a DC and a strain clock); an effect beyond the
                    mapped references
Worst case (J):     a one-rung scale error: 2 to 4 segments, one DC step, one Focus and one condition
                    more or less, all shown to the player before the first research week is spent
                    (class i). EXPRESSIBLE wrongly (a) or (b): the effect is still only what the
                    referenced effects do, at the row's price (class i).
Examples:           inside (local): "ward my rooms so I know if anyone enters": eff.tick_clock on an
                      alarm the caster perceives + eff.write_fact -> (b); local; 2 conditions drawn:
                      material, place.
                    boundary (site vs regional): "keep the river from flooding the lower town this
                      spring": a town -> regional; master grade; 4 conditions.
                    outside: "bring my brother back from the dead": canon_impossible -> G4; the
                      redirect names rit.raise_shade (speak with him) and the funeral rite.
                    non-example: "a rite that makes me permanently stronger": no effect in the
                      library changes an attribute (00.4.3) -> (c).
Anchor:             yes. Intent verbs: "research", "devise", "work out how to", "a ritual to". Knobs:
                    dc (by scale; no delta); time_cost (by scale; allowed delta: one step longer as a
                    drawn condition); targets (by scale); focus_cost (by scale).
Basis:              [R: https://www.dungeonworldsrd.com/classes/wizard/] [R5 MG-04: Ars Magica lab work]
                    [C:V] [C:VI provisional] [00.8.3] [DL-05-24]
```

The eight conditions of `tbl.05.rite_conditions` (a d8 table; Dungeon World's seven plus *place*):
**1 time** (`time_per_tick` one step longer: interval → hour → watch → day); **2 first you must** (a
prerequisite deed, written as a thread, 11); **3 help** (two more trained participants); **4 material**
(a component one price band above the rite's row); **5 lesser** (the rite's reach is capped at
Limited); **6 danger** (the strain clock has 3 segments, not 4); **7 sacrifice** (a relic or enchanted
item is consumed, or the leader's maximum Focus is 1 lower until the next `season` boundary); **8
place** (it can be performed only at a named place of resonance).

**05.8.5 Learning an ability outside a pick.** `[D]` + `[T]` Abilities of the pool may be learned into the
**acquired** partition by any character who holds the training license of the ability's first tag at a
grade whose technique cap covers its `min_tier` (T-05-6). Learning runs on one clock per ability,
`clk.learn.<ability id>` (kind `project`, public): **6** segments for `min_tier` 1–2, **8** for 3–4,
**12** for 5. Its only tick sources:

| Source | Ticks | Requires |
|---|---|---|
| a successful **emulation** of it (05.5.4) | delivered reach (1 at Limited) | having witnessed it |
| a downtime week of **training with a mentor** who holds it (ch.15's training activity; the mentor holds `lic.call.proof` or the ability at rank 2+) | 3 | the mentor's consent (standing, payment, a favor: 15) |
| a downtime week of **study from a text** that teaches it (an item with the fact `teaches: <id>`) | 2 | literacy in the text's language |
| a downtime week of **practice alone** after witnessing it | 1 | — |

On completion the engine grants the ability (`grant`, provisional, `source.kind: learned` or `taught`)
into a free acquired slot, or onto the shelf. A roll never grants it (INV-7); the clock does, and the
clock is an acquisition path of the `project` type. Oath-gated abilities, absorbed powers and
`adversary_only` entries cannot be learned this way. *Pace:* a tier-1 technique from a willing mentor is
two weeks; picked up in the field by emulation alone it is six successful attempts at double Focus. That
gap is the price of having no teacher, and it is what makes a teacher worth seeking (P15: breadth is
paid for in time) [C:P15; R7 §2.14; DL-05-08].

**05.8.6 Promotion.** `[D]` When a pick's candidates (04.8.4) include an ability the character already
holds in the acquired partition or on the shelf, picking it **moves** it to the calling partition, frees
the acquired slot, and gives it the calling's rank from then on. (This asks ch.04 to treat
acquired-held abilities as eligible and to rank them first; see Interface requests. Until then the
player may forget the ability at a long rest and pick it in the ordinary way.)

**05.8.7 Learning a rite; gifts.** `[D]` A rite is learned from its text or its teacher with a 6-segment
project clock (the same tick table without the emulation row: rites are not emulated). A **gift** from a
patron or power (08's `gen.gift` with `output_kind: ability`) is granted straight into the acquired
partition as `provisional` and may name a condition of the giver's (a commitment fact, 11).

### 05.9 Training licenses and grades

**05.9.1 One training license per level-2 deed tag.** `[D]` `data/licenses.yaml` holds 81 entries
`lic.training.<branch>_<child>`, one for every level-2 deed tag, each conforming to 00.12.1 with all of
`principle`, `scope`, `excludes`, `grades`, `attribute`, `crude_fallback`, `stretch`, `emulate` and
`acquisition_paths` present. A training license is the **domain license** of its tag: it licenses the
methods of that trade or art which the basic verbs exclude (picking a lock, surgery, forging a blade,
casting a school's spells), and it is what makes emulation, stretch grades, learning and flares
available for abilities under the tag. Where the tag's ordinary methods are already basic verbs (a
sword is swung with Strike), the license covers the tag's *techniques* and adds nothing to the verb.

**05.9.2 Grades.** `[D]` Every training license has three ordered grades. Ch.04 sets the grade from a
calling's tier (04.5.1: narrow and fine callings reach `expert` at tier 3 and `master` at tier 5; broad
and hybrid callings reach `expert` at tier 4); every other path grants `trained`. This chapter owns what
each grade means (T-05-6):

| Grade | Licensed methods succeed up to (obstacle tier cap) | Technique cap (emulate, learn) | Stretch price | Flares per activation | How it is reached |
|---|---|---|---|---|---|
| **trained** | Hard | `min_tier` ≤ 2 | DC +5, +1 Focus, reach Limited | 1 | origin, mentor, text, or a calling's Mark at tier 1–2 |
| **expert** | Very hard | `min_tier` ≤ 4 | DC +5, +1 Focus, reach Standard | 1 | a calling's tier only |
| **master** | Legendary | `min_tier` ≤ 5 | DC +0, +1 Focus, reach Standard | 2 | a calling's tier only |

The **obstacle tier cap** is the license's reach limit by grade: a trained locksmith facing a Very hard
lock is at reach Zero for picking it (G4 for that method; the redirect names the crude fallback and what
an expert could do). This keeps a +2 from a mentor from opening every door in the world while leaving
the dice to decide everything inside the grade [WE-00-3].

**05.9.3 Competence from training.** `[D]` A training license acquired by the mentor or text path
carries `grants_competence: [{tag: <its tag>, value: 2}]` (00.3.6). An origin's value is ch.02's (at most
+2). A calling's competence is ch.04's and is higher; competence is highest-only, so they never add.
Higher grades grant no competence of their own.

**05.9.4 Acquiring a training license.** `[D]` Paths, each a lookup for the G3 redirect:
- **origin** (02) at creation;
- **mentor**: an 8-segment project clock; a downtime training week with a mentor (who holds
  `lic.call.proof` for the tag, or the license at `expert`) ticks 2; so four weeks. It writes
  `cnt.training` (03.5.5);
- **text**: the same clock, 1 tick per week of study from a manual;
- **recognition**: a calling's Mark (04.5.3) lets the character use every training license at or under
  the calling's key at the tier's grade;
- for the three magic branches, an added `requires`: arcane, literacy and a text or teacher; divine, a
  keeper who accepts the character (05.7.4); primal, a place or spirit that accepts them (a fact, or
  the Oracle at a place of resonance). Chapter 13 may tighten these.
There is no cap on how many training licenses a character holds. The bound is time: each costs a month
with a teacher or two alone, grants +2 and the lowest grade, and opens four acquired slots' worth of
techniques at rank 1. Breadth is available and is not power [C:P4; C:P15; C:P11: nothing is bought with
points].

### 05.10 Composition: how abilities combine

Everything an ability does is an effect reference, so everything an ability does combines through 00.10
with no rule written for the pair. This part states what the substrate means for abilities, fixes the
priority ranks and the spread tags that 00 left to this chapter, and authors the named composites.

**05.10.1 One regime per ability.** `[D]` The form fixes the regime (05.3.2), and the regime tells the DM
and the engine how the ability combines with anything [R3 05.5, #3]:
- **additive** (Edge, Lever, Permission, Exception): its numbers enter the evaluation pass in their
  families and are capped there. Three edge passives do not give +3: the edge family is capped at +2
  (00.3.5). The codex shows the cap being hit.
- **independent_trigger** (Working, Reaction, Reserve): it resolves on its hook, each subscriber
  separately, in 00.10.7's order (the target's prevents and redirects, then the actor's effects, then
  others'; by priority rank, then by acquisition time).
- **priority_exclusive** (Form, and any ability with a `slot`): it claims one behavioral slot; the highest
  rank owns it and the rest are suppressed, numbers included.
- **named_composite**: an entry of `data/composites.yaml`, active while both of its keys are present.

**05.10.2 The same thing twice.** `[D]` Two instances of one effect id never stack (INV-13); one ability id
is held once (05.2.9); one `mod_group` is held once. A lever is one fact, and one fact yields one lever
(00.3.9 d), so two abilities that each "grant a Precision lever" give two levers only when they cite
different facts, and at most two levers apply to a roll. These four rules are the whole of
anti-stacking; no ability's text needs a "does not stack with" line.

**05.10.3 Priority ranks.** `[D]` Every claim on a behavioral slot (T-00-14) carries a `priority_rank`
from these bands (`composites.yaml#priority_rank_bands`). The bands put what is *applied to* a character
above what the character *is*, and what another being imposes above both:

| Band | Source of the claim |
|---|---|
| 10–12 | an ability: 10 at rank 1, 11 at rank 2, 12 at rank 3 |
| 12 | an absorbed power (ch.04's data) |
| 15–19 | an item's intrinsic property (08) |
| 20–24 | an applied consumable: an oil, a draught (08) |
| 30–34 | a named composite or a rite |
| 40–49 | a claim imposed by another being (a curse that forces a shape, a hold that fixes how you move) |

The highest rank owns the slot; ties go to the earlier-acquired claim; a suppressed claim keeps counting
its duration and resumes if the owner ends first; the holder may **drop** a running claim of their own
as a free activity so that a lower one resumes. `use_ability` warns before Focus is spent on a claim
that would be suppressed at once (WE-00-6: Cinder Stride at rank 10 under Rime Oil at rank 20).
[C:P6 companion; R3 05.4: Isaac's replacers, ranked instead of paired]

**05.10.4 Spread tags: one ordered vocabulary for "more than one target".** `[D]` An ability that affects
several targets carries exactly one **spread tag**, and each tag is a selection rule over
relationship-state with a cap. When several spread tags meet on one working (its own, the Wide flare, an
item, a composite), they resolve in this fixed order, each applied to the targets the previous one
produced, and never above **six targets in total**. No combination has a name or a rule of its own
[C:P6 companion; R3 05.4, E-3: pierce, then fork, then chain; R3 #7].

| Order | Tag | Selects | Cap | Harm to each |
|---|---|---|---|---|
| 1 | `pierce` | the primary target, then each further being carrying `flag.lined_up` with it, nearest first | 4 | full |
| 2 | `burst` | the primary target and each being within `band.engaged` of it (or of the named point), friend and foe | 6 | full |
| 3 | `cone` | each being at `band.engaged` with the source, then each at `band.close` in the primary target's group; friend and foe (ch.06's sixth shape, T-06-15) | 4 | full |
| 4 | `fork` | the primary target and one more eligible being within `band.close` of it per extra target the text grants | 5 | full |
| 5 | `chain` | after the primary resolves, the nearest other being within `band.close` of the last target, friend or foe | 3 | one severity rung lighter at each leap |
| 6 | `linger` | the place itself: any being that enters it or ends its turn there, for the duration | 5 | as the ability states |

The order is ch.06's T-06-15, which adopted this chapter's five tags unchanged and inserted `cone` third. A
`slot.spell_delivery` form (`eff.05.spell_delivery`) reads as a shape: `line` → `pierce`, `burst` → `burst`,
`cone` → `cone`, `chain` → `chain`, `zone` → `linger`; `bolt` and `touch` are single-target
[integration: IR ch.06 to 05 (a)].

One roll serves all targets of an aimed working (the same total is compared to each defense); each
target of a resisted working rolls for itself. The **Wide** flare adds `fork` with one extra target to an
ability with no spread tag, or raises the cap of the tag it has by one. A spread selects by
relationship-state at commitment and is indifferent to side unless the ability's text says "foes".

**05.10.5 Designing inside the one-link limit.** `[D]` Hook subscribers fire only on depth-0 events
(INV-12). For abilities this divides cleanly:
- What a **beat** or a **rider** does is caused directly by the declared beat: depth 0. Conditions it
  applies, harm it deals and Focus it spends can fire other abilities' triggers.
- What a **reaction** or **trigger** does was caused by a hook: depth 1. It fires nothing further. Core
  rules still run (harm lowers Vitality, a threshold is still crossed, a clock still ticks).
So an intended two-step synergy is written with its *first* step as a beat or rider: Staggering Blow (a
rider) applies `cond.dazed` at depth 0, and Pressing Advantage (a trigger on a condition applied by
self) fires. Quarry's Mark (a trigger) applies `cond.exposed` at depth 1, and Pressing Advantage does
not fire on it. The codex's ability view states each ability's timing so the player can see which pairs
connect [00.10.8; WE-00-6; OEQ-00-4].

**05.10.6 Named composites.** `[D]` `data/composites.yaml` holds the designed combinations: the ones
distinctive enough to deserve a name (Stormlight's Three Lashings; Mistborn's Compounding, bounded)
[C:P6; R2 #39, #40]. A composite is keyed on **exactly two low-cardinality keys** and is active only
while both are present and neither is suppressed. Chapter 05 authors three key kinds; ch.04 authors the
fourth in its owner-block.

| Key kind | Keys | Present when | Entries |
|---|---|---|---|
| `harm_branch` | two of the ten harm branches (at most 45 pairs) | a depth-0 harm event of one branch lands on a target carrying a condition tagged with the other | 8: Thermal Shock, Shatter, Cauterize, Flashfire, Searing Purge, Dread Rot, Stormfrost, Swift Venom |
| `conduct_axis` | two of the ten conduct axes | the character holds, unsuspended, an oath-gated ability on each axis at the positive pole | 5: Tempered Judgment, Stand Between, True and Faithful, Servant of All, The Quiet Flame |
| `composite_key_license` | two abilities flagged `composite_key` (18 abilities are flagged) | the character holds both, and the entry's stated circumstance holds | 9: Phalanx, Marked for Death, Holy Fire, Warded Shield, Wildfire Wind, Storm in the Mist, Battle Hymn, Briar Cage, Ill Omen |
| `deed_branch` | two deed branches (36 pairs) | the character holds the named hybrid calling | 32, ch.04 (`data/composites.yaml owner-block 04`) |

Rules for all four: (a) a composite is at most **4 effect units** (05.11.4); (b) it uses only effects of
`effects.yaml`; (c) it may **suppress named components** (Holy Fire replaces the two strike-delivery
claims it is built from, which is how a designed pair overrides the priority rule that would otherwise
silence one of them); (d) it never adds an action; (e) harm-branch composites belong to the *world*:
they fire for anyone, adversaries included, which is what makes "douse the burning man" and "shatter the
frozen lock" things a player can reason toward without holding any ability; (f) pairs with no entry
have no composite, and the narrator may not invent one ("the fire and the frost together shatter his
mail" is forbidden where no entry exists, WE-00-6).

**05.10.7 Reading order for the DM.** `[N]` When two abilities meet, the DM looks nothing up beyond the
two records: (1) do both claim one behavioral slot? the higher rank owns it; (2) is there a composite
keyed on this pair? the engine reports it; (3) otherwise each applies as its regime says, and the frame's
breakdown shows the result. The DM never reasons about an interaction; the engine returns it [R4 §9 05
#3; SG-10].

### 05.11 Budgeting: what an ability is allowed to be worth

**05.11.1 The method.** `[D]` Every rank of every ability has a **value** and an **allowance**, both in
**effect units** (EU). The value is the sum of the units of its effects (T-05-9). The allowance is
computed from the ability's minimum tier and from the prices it pays. An ability is legal when

`allowance − 2 ≤ value ≤ allowance`

and the generator script refuses any entry outside that band. The lower bound is what makes abilities of
one tier comparable (none is a trap); the upper bound is what keeps them inside the tier
[R2 §05: an explicit, checkable budget scales where curated benchmarking does not; R1 M-22; C:P11's
audit discipline, applied to a pool that is picked from and never bought with points; DL-05-16].

**05.11.2 The allowance.** `[D]`

`allowance = tier + 2 × Focus + recharge + timing + limitation + weakness + other cost`

| Term | Value | Lever (P12) |
|---|---|---|
| **tier** | `min_tier + 2 × (rank − 1) + 1` | — |
| **Focus** | 2 per point of the rank's cost | cost |
| **recharge** | none or per round 0 · per conflict or per scene 1 · per short rest 2 · per long rest or per day 3 · once ever 4 (minus 1 per use beyond the first in the period) | cost |
| **timing** | beat 2 · reaction 1 · rider 0 · trigger 0 · passive 0 | cost (the action or reaction it uses) |
| **limitation** | +1 per narrowing clause beyond the form's default (a required state, a required weapon *and* stance, a required standing), at most 2 | limitation |
| **weakness** | +1 for a condition or snag on the holder; +2 for lost senses or doubled harm | weakness |
| **other cost** | +1 per component, interval of work or S1 of Vitality; +2 for S2 of Vitality or Focus given away | cost |

Three consequences follow from the formula, by construction:
- **Passives are budgeted lower than actives.** A passive has no Focus, recharge or timing term, so at
  tier 1 its allowance is 2 EU (one conditional +1, or one standing lever), where a tier-1 Working that
  costs 1 Focus has 6. A passive may also never prevent, apply hard control, or deal S3 harm (05.3.3).
- **P12's three levers are prices.** An ability that accepts a narrower scope, an explicit weakness or a
  cost paid elsewhere is *allowed more*. The fields are separate in the record and separate in the
  arithmetic.
- **A rank is worth 2 EU.** Each rank raises the tier term by 2, so growth by rank is the same size for
  every ability, and a rank-3 ability of `min_tier` 1 has the tier term of a rank-1 ability of
  `min_tier` 5.

**05.11.3 Bounds the budget does not replace.** `[D]` The budget compares abilities with each other; 00's
caps bound them absolutely, and the script checks both: edge at most +2, harm edge at most +2, severity
steps from effects at most ±2, reduction inside ch.07's cap, a Focus cost inside its band for the
`min_tier` (05.6.2), and no effect that adds an action.

**05.11.4 Composites, flares and rites.** `[D]` A named composite is at most **4 EU** (two ranks' worth: a
reward for holding a pair, never a third ability). A flare is worth 2 EU for its 1 Focus, the same rate
as the allowance pays, so flaring is never better than the ability's own cost-to-value and never worse.
Rites are priced by scale (T-05-8), not by EU, because their price is time and material.

**05.11.5 The method applied.** `[D]` Three abilities at tier 1 and one at tier 5, as the script computed
them (every entry's `budget` field in the data shows the same arithmetic):

| Ability | Form · timing · price | Allowance | Effects (EU) | Value |
|---|---|---|---|---|
| `ab.throwers_eye` r1 | Edge · passive | tier 2 = **2** | +1 to thrown Strikes within close (2) | **2** |
| `ab.aimed_shot` r1 | Working · rider · 1 Focus · one narrowing clause (did not move) | 2 + 2 + 0 + 0 + 1 = **5** | Precision lever on the shot (1) + one severity rung (2) | **3** |
| `ab.flame_lance` r1 | Working · beat · 1 Focus | 2 + 2 + 2 = **6** | S2 fire harm (2) + burning beyond a round (3) | **5** |
| `ab.flame_lance` r3 | same, rank 3 | 6 + 2 + 2 = **10** | S4 fire harm (5) + burning (3) | **8** |
| `ab.firestorm` r1 | Working · beat · 3 Focus · per long rest | 6 + 6 + 3 + 2 = **17** | S4 harm (5) + five more targets (5) + burning (3) + lingering S2 (2) | **15** |

Across the 239 budgeted abilities and their 526 ranks: 175 ranks sit exactly on their allowance, 180 are
one unit under, 171 are two under, and none is over (`abilities.yaml#census.budget_slack`) [revision:
I-007, I-009, I-015]. The 27
absorbed powers are ch.04's and are costed by 04.10.4's three separate costs, not by this table.

**05.11.6 How many abilities, and why.** `[D]` The pool holds **266** entries: 179 tag-gated, 57
oath-gated, 3 branch workings, 27 absorbed [revision: I-007, I-009, I-015]. The count is set by coverage, not by taste [C:V; DL-05-02]:
- **Every level-2 deed tag has at least two** (one usable at tier 1), because ch.04 has a calling for
  every level-2 tag and that calling's *own* pool is its tag (04.8.4): 81 tags × 2 = 162 is the floor.
- **Every branch has at least two at each minimum tier 1–5**, so a branch calling and a narrow calling's
  kin pool always have a candidate at each new tier: this adds 14.
- **Every conduct axis has three at each pole a calling uses (tiers 1, 3, 5)**, which is what a vow's or
  a dark calling's three picks need (allowance 1, 1, 2, 2, 3): 30 + 27 (courage has no dark calling).
  The first pool had two at the negative pole, so a dark calling's tier-5 pick was kept for want of a
  candidate; `05-ladder-check.py` now proves every calling × axis × tier ladder complete [revision: I-007].
- **Every primal element has a `min_tier` 1 working** (fire, water, earth, air), because the Touched's
  spark names one of the four and must start with its own (02.6.3): this adds 3 [revision: I-015].
- **One branch working per magic branch** (05.7.11), outside the pick pool: this adds 3 [revision: I-009].
- **Above that floor the pool is deliberately not grown.** A narrow calling sees its own two or three and
  the rest of its branch (14 to 26); three candidates are shown per pick (04.8.4); and the eight forms,
  six flares, three ranks and one stretch per ability multiply what each entry can do. The research is
  consistent that depth comes from interactions among few primitives and bloat from their number
  [R3 05.16; C:V]. New abilities enter only as provisional content at a boundary (05.12.3).

### 05.12 Lifecycle: provisional status, replacement and retirement

Principle VI forbids purely additive growth and asks that retirement be structural, telegraphed and
bundled at boundaries [C:VI]. For abilities it is satisfied at two scales.

**05.12.1 At character scale.** `[D]` Nothing in this chapter adds without also bounding or replacing:

| Move | What happens | Where |
|---|---|---|
| **Restate** | a rank replaces the previous rank's whole text and effects; nothing accumulates | 05.3.9 |
| **Replace** | at the calling cap a new pick takes a held ability's slot; an ability with `replaces` takes its predecessor's slot | 05.2.5; 04.8.4 |
| **Promote** | an acquired ability picked through a calling moves partitions; no new slot | 05.8.6 |
| **Shelve and forget** | the fifth acquired ability is shelved; the ninth is forgotten | 05.2.6 |
| **Re-slot** | acquired slots are re-chosen at a long rest; calling picks at the season re-pick or by Retrain | 05.2.7; 04.8.7 |
| **Lapse** | a provisional pick lapses with its tier; a provisional acquired ability unused for two seasons is shelved | 04.8.2; 05.2.10 |
| **Fold** | when a calling folds, its picks return to the pool and its training stays at `trained` | 04.8.6 |
| **Consolidate** | several callings become one; picks are kept as legacy picks against the one new allowance | 04.8.5; WE-05-4 |

A squish is none of these: lowering every ability's numbers retires nothing and is never offered as
consolidation [C:VI].

**05.12.2 Telegraphing.** `[T]` + `[N]` Every one of those moves happens only at a boundary the player can
see coming (a long rest, a reflection, a `season` boundary, a crystallization) and only by the player's
choice or after a warning one boundary earlier. The codex marks provisional abilities and names the
boundary at which each will be tested. No ability is ever reinterpreted in place: its text changes only
by rank or by 05.12.3 [R3 #10: the cost of unbudgeted reworks].

**05.12.3 At content scale.** `[D]` Every entry of this chapter's data files ships `lifecycle:
provisional` (00.16.3). Content changes follow these rules:
- **Promotion** to `permanent` is the verification wave's, entry by entry, on the evidence of play.
- **Retirement** is `lifecycle: retired` with `superseded_by`; ids are never reused or deleted. A
  character holding a retired ability keeps it until the next `season` boundary, when the engine offers
  the successor in the same slot (a fork: the old one is replaced, never joined).
- **Folding into base.** An ability that play shows to be mandatory (always picked, always used before
  another: the no-decision button) is folded into the training license's scope or into the successor's
  text, and retired [R3 05.11, 05.12: Kaiten; PoE2's Acrobatics].
- **Adding** an ability requires: one of the eight forms; a first tag at level 2 or 3; a `mod_group`; a
  budget inside the band; and, when the pool already holds one in that `mod_group`, either a `replaces`
  link or the retirement of the older entry. The pool grows only where coverage (05.11.6) has a hole.
- **Custom rites** are provisional by rule (05.8.4) and are the one kind of content created in play.

---

## Procedures

**PR-05-1 Using an ability.** `[D]` (`use_ability(actor, ability_id, targets, frame_id, mode, flares)`,
tool #19; runs inside ch.01's pipeline at GATE and FRAME, or on a hook for reactions and triggers)
1. **Look up** the held entry and its active rank (05.3.9). Mode is `normal`, `stretch` (PR-05-2) or
   `emulate` (PR-05-3).
2. **Validate** in the order of 05.4.1: held and bound and not suspended → timing → limitation clauses
   that read state → uses → exclusions (one rider per beat; one sustained working; warn on a suppressed
   slot claim) → Focus. For a spell also: the branch signature (voice and free hand; the sign and the
   keeper's regard; the source present, 05.7.3). On the first failure return the refusal with its reason
   and the redirect data (01.3.6). Nothing is spent.
3. **Cost.** Evaluate `focus_cost` by 05.6.3 and show its breakdown. If it exceeds `focus.current`,
   return the overdraw price (05.6.6) for the player to accept or withdraw.
4. **Frame.** For `check: aimed`, the frame's attribute, deed tag (the first tag), DC source and any
   stretch or emulate shift are set from the record; the DM adds levers, stakes and reach as for any
   beat. For `check: resisted`, compute the effect DC and create one resisted frame per target. For
   `check: none`, no frame of its own (a rider uses the frame of the beat it rides).
5. **OFFER.** The player sees the ability's literal text, the Focus cost, the uses left, the odds, the
   stakes and reach, and commits, changes or withdraws (01.7). Reactions and triggers show the same in
   one line at the moment the hook fires.
6. **Commit.** Spend Focus and one use (`update_quantity`; `on_focus_spent` fires). Set `Spent` if Focus
   is now 0.
7. **Roll and read** (01.8–01.9), or have each target roll its resisted check.
8. **Apply effects** through PR-00-6 with the right depth (beat and rider: 0; reaction and trigger: 1),
   in the order the rank lists them, each on the degrees the text names (default: any success; a
   resisted effect per 01.18.3). Store the effect DC on anything lasting. Resolve spread tags
   (05.10.4), slot claims (05.10.3) and composites (05.10.6).
9. **Miscast** check for spells (PR-05-7).
10. **Record.** State writes, evidence (the frame's primary tag is the first tag), the rank's verbatim
    text and every narration obligation go to the narration packet. The narrator restates nothing the
    packet does not hold.

**PR-05-2 Stretching.** `[J:flag]` + `[D]`
1. Find a precedent with signature `<ability id>+stretch+<object>` (`find_rulings`); if one matches and no
   stated fact differs, reuse its mapping and go to step 4.
2. Answer 05.5.2's two decisions, citing the principle sentence and the facts. Either false → G3 for the
   excess, with the redirect; stop.
3. Map the use: verb (`check.verb` or `verb.handle`), obstacle and its DC source, which of the ability's
   listed effects the use needs (at most one severity rung, one condition, or delivered reach in ticks
   or object state).
4. Prices by grade (T-05-6): DC shift, +1 Focus, reach cap. Sure Hand's lever if the holder has it.
5. Run PR-05-1 from step 3 with mode `stretch`. A stretch is never flared.
6. Log the ruling (kind `adaptation`) with the signature.

**PR-05-3 Emulating.** `[J:flag]` + `[D]`
1. Check the license: `lic.training.<level-2 tag of the technique>` held, `emulate` not null, the
   technique's `min_tier` within the grade's cap, active, not oath-gated, not `adversary_only`, not held.
2. WITNESSED (05.5.4), or the Open Art.
3. Run PR-05-1 from step 3 at rank 1 with mode `emulate`: DC shift (aimed), a Precision lever for each
   resisting target (resisted), Focus × 2 (0 becomes 1), reach capped at Limited, no flare.
4. On a critical failure apply `emulate.crit_fail` when worse than the READ cost.
5. On any success tick `clk.learn.<ability id>` by delivered reach (create it if absent: 6, 8 or 12
   segments). On completion → PR-05-8.

**PR-05-4 Recovering Focus and uses at a rest.** `[D]` (`h.05.focus_recover`, `h.05.rest_recharge`,
`h.05.reslot`, `h.05.reserve`; phase 3 of `breather`, `rest_short`, `rest_long`)
1. Read the rest type and its `quality` from the boundary event (07).
2. Focus: add the amount of T-05-5 for the type and quality, subject to the breather and short-rest
   limits; add +1 for a resonant place (breather and short rest); clamp to `focus.max`; clear `Spent` if
   Focus ≥ 1.
3. Uses: unless the quality is `interrupted`, refresh every use at or below the rest on the refresh
   ladder (05.4.6).
4. `rest_short`: reset `breathers_since_short_rest`. `rest_long`: reset the healing, overdraw and
   consumable counters; resolve the reserve (bank the charged points or lose the charge; accept a new
   declaration); offer the re-slot of the acquired partition (quality `full` or `partial`).
5. Return what changed for the narration packet. The narrator says the character is rested in the
   fiction's terms and states no numbers.

**PR-05-5 Performing a rite.** `[D]`
1. **Check requirements**: the rite is known; the training license at the rite's grade; components in
   hand; place; participants; Focus. Missing → a refusal naming what is missing and where it might be
   found (01.3.6).
2. **Begin**: spend the Focus; create the progress clock and the 4-segment strain clock from the rite's
   template, racing (00.8.5); write the fact that the rite is under way at this place.
3. **Step**: the leader declares a step; `frame_check` an aimed check (branch attribute, the rite's first
   tag, the stored DC tier; helpers by 01.14.8; stakes as framed, Risky by default). OFFER. On commit,
   `advance_time` by `time_per_tick`; if it is interrupted, the step has not happened and the remainder
   is returned (00.7.8).
4. **Read**: success → tick progress by delivered reach. Failure → apply one of the rite's
   `failure_costs` (the DM picks the fitting menu entry, 01.13.1) and tick strain by U(severity). A
   critical failure is not a miscast by itself: the strain clock is where a rite's danger lives.
5. **Finish**: progress full → apply `effects` with the leader's effect DC stored; consume components;
   log the chronicle line. Strain full → the rite fails; components are consumed; the leader takes the
   branch's miscast at S3; any `canon_check` note of the rite applies.
6. **Leave it**: the progress clock decays 1 per `watch` untended; at 0 it is void, the strain clock is
   voided with it, and the components are kept.

**PR-05-6 Designing a rite.** `[J:enum]` + `[J:rung]` + `[D]`
1. EXPRESSIBLE and SCALE (05.8.4). If not expressible → the redirect; stop.
2. Read the scale row (T-05-8): grade needed, research clock, and the new rite's numbers.
3. Draw the scale's number of conditions from `tbl.05.rite_conditions` (`roll_table`, no repeats). Fill
   each condition's specifics from established facts, else from the Oracle (which place; which
   material; which deed).
4. Show the player the whole design before any time is spent: effects, scale, clock, DC tier, Focus,
   components, conditions.
5. Research: a project clock ticked by research weeks (15) at delivered reach. On completion write
   `rit.custom.<n>` (`lifecycle: provisional`), log the ruling, and create any thread a condition needs.
6. Perform it by PR-05-5.

**PR-05-7 Miscast.** `[T]` + `[D]`
1. Trigger: an aimed working's degree is critical failure, or every target of a resisted working rolled
   a critical success.
2. Severity: S1 / S3 / S4 for Safe / Risky / Dire stakes (resisted trigger: S1); +1 rung if flared or
   emulated; at most S4.
3. Apply the branch's row (`abilities.yaml#magic.miscast`) in place of the critical failure's menu cost.
   Backlash harm is non-lethal unless the frame was lethal.
4. The packet carries the row's literal text; the narrator gives it a form in the fiction and adds
   nothing.

**PR-05-8 Learning completes.** `[D]`
1. On `on_clock_complete` of `clk.learn.<ability id>`: verify the training license and its grade still
   cover the ability.
2. `grant(ability, partition: acquired, rank: 1, provisional: true, source: learned | taught)`. If the
   four acquired slots are full, place it on the shelf; if the shelf is full, the player names one of
   the nine to forget.
3. Remove `pc.witnessed.<ability id>` (it is now known). Write the chronicle line.

**PR-05-9 Authoring an ability (content procedure).** `[D]`
1. Search the pool: does an ability of this `mod_group` or with these effects already exist? Expand
   before adding (PR-00-8).
2. Choose the form (05.3.2); if none fits, it is not an ability.
3. Write the principle (one operation, one object category), the literal rank text, the limitation as a
   positive scope, and any weakness or other cost as separate fields.
4. Express every mechanic as effect references; price them with T-05-9.
5. Compute the allowance (05.11.2) for each rank; adjust until `allowance − 2 ≤ value ≤ allowance`.
6. Give it at least one exclusion that names what *would* cover the excluded thing.
7. Add it to the generator's tables and run the generator: it must pass every check.
8. Lifecycle `provisional`; a DL entry if it uses a new effect definition.

---

## Tables

Tables embedded in Rules are canonical and indexed here: **T-05-1** partitions (05.2.1); **T-05-2**
fields of an ability record (05.3.1); **T-05-3** the eight forms (05.3.2); **T-05-4** recharge types and
the refresh ladder (05.4.6); **T-05-5** Focus recovery by rest (05.6.9), with the maximum (05.6.1), the
cost bands (05.6.2) and the flares (05.6.8); **T-05-6** training grades (05.9.2); **T-05-7** the three
sources of magic (05.7.2) and the miscast table (05.7.5); **T-05-8** rite scales (below); **T-05-10**
priority-rank bands (05.10.3); **T-05-11** spread tags (05.10.4). The data files are canonical for every
id and number.

**T-05-8 Rite scales.** `[J:rung]` (`rituals.yaml#scales`) *Worst case of a one-rung error:* 2–4 segments,
one DC step, one Focus, one condition; shown before any time is spent (class i).

| Scale | Anchor | Research clock | Grade needed | Progress clock | DC tier | Focus | Conditions drawn |
|---|---|---|---|---|---|---|---|
| personal | one willing being or one object in hand; lasts a scene to a day | 8 | trained | 4 | Moderate | 1 | 1 |
| local | a room, a small group, or one unwilling being; lasts days | 8 | trained | 6 | Hard | 2 | 2 |
| site | a building, a grove, a company of people; lasts a season | 12 | expert | 8 | Very hard | 3 | 3 |
| regional | a valley, a town, a host; lasts a season or leaves a permanent mark | 12 | master | 12 | Legendary | 4 | 4 |

**T-05-9 Effect units.** `[D]` The price list of 05.11 (`abilities.yaml#budget.effect_units`). An effect not listed is priced as the nearest listed one, and a new effect definition must add its row.

| Effect | Units | Effect ids |
|---|---|---|
| Check edge +1 / +2 in a stated circumstance | 2 / 4 | `eff.check_edge`, `eff.defense_edge`, `eff.effect_dc_edge` |
| Lever for one beat or one round | 1 | `eff.grant_lever` |
| Lever that stands for a scene, or whenever a stated circumstance holds | 2 | `eff.grant_lever` |
| Reach +1 rung; stakes -1 rung | 2 each | `eff.reach_step`, `eff.stakes_step` |
| Harm S1 / S2 / S3 / S4 / S5 to one target | 1 / 2 / 3 / 5 / 7 | `eff.deal_harm` |
| Harm severity +1 rung on your own attack | 2 | `eff.harm_severity_step` |
| Harm edge +1 / +2 | 1 / 2 | `eff.harm_edge` |
| Strike or spell delivery changed (harm type, form) | 1 (+ its harm edge) | `eff.strike_delivery`, `eff.05.spell_delivery` |
| Each target beyond the first (through a spread tag) | 1 | `spread` |
| Condition, light group (off_balance, distracted, exposed, slowed, deafened, chilled) | 1 (+1 if it lasts beyond a round) | `eff.apply_condition` |
| Condition, middle group (prone, weakened, frightened, blinded, grabbed, burning, bleeding, dazed, choking, poisoned, exhausted) | 2 (+1 beyond a round) | `eff.apply_condition` |
| Condition, hard-control group (stunned, restrained, charmed, unconscious, pinned, frozen) | 4 (+1 beyond a round) | `eff.apply_condition` |
| Harm reduction 1 for one harm branch / for all physical harm or several branches | 1 / 2 per point | `eff.harm_reduction` |
| Resistance (halve) one harm branch | 3 | `eff.harm_resistance` |
| Hazards of a kind count one rung lower | 2 | `eff.hazard_step` |
| Negate one hit; negate one working | 4 | `eff.prevent_hit`, `eff.05.counter_working` |
| Take a hit meant for another | 2 | `eff.intercept` |
| End a condition; end a magical effect | 2 / 3 | `eff.cleanse`, `eff.05.end_working` |
| Immunity to one named condition; a restriction placed on a target | 2 | `eff.condition_immunity`, `eff.restrict` |
| Restore Vitality 1 / 3 / 5 / 8 | 1 / 2 / 3 / 5 | `eff.restore` |
| Restore or drain 1 Focus; return one use of an ability | 2 | `eff.restore`, `eff.drain`, `eff.05.refresh_use` |
| Maximum Vitality or Focus +1 | 2 | `eff.max_modify` |
| Focus cost -1 in a stated circumstance | 2 | `eff.focus_cost_step` |
| Move self or a target one band; add or clear one positional flag | 1 each | `eff.reposition` |
| Movement mode: climb or swim / burrow / fly | 2 / 3 / 4 | `eff.movement_mode` |
| Another shape | 4 | `eff.body_form` |
| One more reaction per round | 3 | `eff.reaction_grant` |
| Tick a clock by 1 / by delivered reach | 1 / 2 | `eff.tick_clock` |
| Reveal one sealed fact or tell | 2 | `eff.reveal` |
| Bring a helper or object into being (threat band B) | 2 x B | `eff.summon` |
| Establish a fact (a mark, a sign, a bond) | 1 | `eff.write_fact` |
| A temporary license for another, or a method beyond the basic verbs (ordinary / world-bending) | 2 / 4 | `eff.grant_license`, `Permission scope` |

**T-05-12 The pool by branch and minimum tier.** `[D]` (`abilities.yaml#census`; checked against ch.04's coverage requests by the generator.)

| Group | Total | min_tier 1 | 2 | 3 | 4 | 5 | Level-2 tags covered (each with at least 2, one at tier 1) |
|---|---|---|---|---|---|---|---|
| `deed.martial` | 26 | 12 | 6 | 4 | 2 | 2 | 12 of 12 |
| `deed.guile` | 17 | 8 | 3 | 2 | 2 | 2 | 8 of 8 |
| `deed.wilds` | 14 | 6 | 2 | 2 | 2 | 2 | 6 of 6 |
| `deed.lore` | 18 | 9 | 3 | 2 | 2 | 2 | 9 of 9 |
| `deed.arcane` | 26 | 11 | 5 | 4 | 3 | 3 | 11 of 11 |
| `deed.divine` | 17 | 8 | 2 | 3 | 2 | 2 | 8 of 8 |
| `deed.primal` | 20 | 10 | 3 | 3 | 2 | 2 | 7 of 7 |
| `deed.influence` | 18 | 9 | 3 | 2 | 2 | 2 | 9 of 9 |
| `deed.craft` | 23 | 11 | 4 | 3 | 3 | 2 | 11 of 11 |
| branch workings (05.7.11; held through training, no slot) | 3 | 3 | 0 | 0 | 0 | 0 | one per magic branch |
| oath-gated, positive pole | 30 | 10 | 0 | 10 | 0 | 10 | 10 axes x 3 |
| oath-gated, negative pole | 27 | 9 | 0 | 9 | 0 | 9 | 9 axes x 3 |
| absorbed powers (ch.04) | 27 | 16 | 9 | 2 | 0 | 0 | gated by creature tags |
| **all** | **266** | 122 | 40 | 46 | 20 | 38 | 81 of 81 |

**T-05-14 Index of the pool.** `[D]` One row per level-2 deed tag, then per conduct axis. Each ability is shown as *Name* (minimum tier · Focus at rank 1 · timing). The data file is canonical.

| Tag | Abilities |
|---|---|
| `martial.blade` | *Riposte* (1 · 1F · reaction); *Cleaving Arc* (2 · 1F · rider); *Finishing Stroke* (5 · 3F · beat, /scene) |
| `martial.axe` | *Hew* (1 · 1F · rider); *Sunder* (3 · 2F · beat) |
| `martial.bludgeon` | *Staggering Blow* (1 · 1F · rider); *Shatter Guard* (4 · 2F · rider) |
| `martial.polearm` | *Set the Spear* (1 · 0F · reaction, 1/round); *Long Guard* (2 · 1F · rider) |
| `martial.archery` | *Aimed Shot* (1 · 1F · rider); *Volley* (3 · 1F · beat) |
| `martial.thrown` | *Thrower's Eye* (1 · — · passive); *Pinning Cast* (2 · 1F · rider) |
| `martial.unarmed` | *Iron Palm* (1 · — · passive); *Clinch and Throw* (2 · 1F · rider) |
| `martial.shield` | *Shield Block* (1 · 0F · reaction, 1/round); *Shield Wall* (3 · 1F · rider) |
| `martial.armor` | *Armored Ease* (1 · — · passive); *Bulwark* (4 · 2F · reaction, /scene) |
| `martial.tactics` | *Pressing Advantage* (1 · 0F · trigger, /scene); *Read the Field* (2 · 0F · beat); *Commanding Ground* (5 · 3F · beat, /scene) |
| `martial.mounted` | *Lance Charge* (1 · 1F · rider); *Saddle-Born* (3 · — · passive) |
| `martial.athletics` | *Surefoot* (1 · — · passive); *Mighty Heave* (2 · 1F · beat) |
| `guile.stealth` | *Soft Step* (1 · — · passive); *Vanish* (3 · 1F · beat) |
| `guile.thievery` | *Light Fingers* (1 · — · passive); *Ghost at the Lock* (2 · 1F · rider) |
| `guile.deception` | *Plausible Lie* (1 · — · passive); *Misdirection* (4 · 1F · reaction, /scene) |
| `guile.disguise` | *Quick Change* (1 · 0F · beat); *The Living Mask* (5 · 2F · beat, /long rest) |
| `guile.ambush` | *Backstab* (1 · 1F · rider); *Spring the Trap* (2 · 0F · rider, /conflict); *Throat of Night* (5 · 3F · beat, /scene) |
| `guile.poisoncraft` | *Envenom* (1 · 0F · rider); *Slow Draught* (4 · 2F · beat) |
| `guile.escape` | *Slip Free* (1 · 0F · beat); *Gone Like Smoke* (2 · 1F · rider) |
| `guile.streetwise` | *Word on the Street* (1 · 0F · beat, /scene); *A Door in Every Town* (3 · 0F · beat, /scene) |
| `wilds.survival` | *Hard Country* (1 · — · passive); *Shelter Anywhere* (3 · 0F · beat) |
| `wilds.tracking` | *Quarry's Mark* (1 · 1F · trigger, /scene); *Read Sign* (2 · 0F · beat); *Relentless Pursuit* (4 · — · passive); *Apex Hunter* (5 · 2F · rider) |
| `wilds.navigation` | *Pathfinder* (1 · — · passive); *Hidden Ways* (3 · 1F · beat, /scene) |
| `wilds.animals` | *Gentle Hand* (1 · 0F · beat); *Beast at Heel* (2 · 0F · rider) |
| `wilds.foraging` | *Green Larder* (1 · — · passive); *Wild Physic* (4 · 1F · beat, /short rest) |
| `wilds.seafaring` | *Sea Legs* (1 · — · passive); *Storm Helm* (5 · 3F · beat, /scene) |
| `lore.history` | *Old Tales* (1 · — · passive); *Herald's Eye* (2 · 0F · beat) |
| `lore.languages` | *Gift of Tongues* (1 · 0F · beat, /scene); *Cipher-Breaker* (3 · — · passive) |
| `lore.bestiary` | *Know the Beast* (1 · 0F · beat); *Weak Point* (2 · 1F · rider) |
| `lore.medicine` | *Field Surgeon* (1 · 0F · beat); *Master's Remedy* (4 · 2F · beat) |
| `lore.engineering` | *Find the Flaw* (1 · 0F · beat); *Clockwork Sense* (3 · 0F · beat) |
| `lore.law` | *Letter of the Law* (1 · — · passive); *The Unanswerable Case* (5 · 3F · beat, /scene) |
| `lore.arcana` | *Spell-Sight* (1 · 0F · beat); *Theory of the Weave* (2 · — · passive) |
| `lore.religion` | *Name the Power* (1 · 0F · beat); *Know the Unclean* (4 · — · passive) |
| `lore.investigation` | *Keen Search* (1 · — · passive); *Reconstruct the Scene* (5 · 3F · beat, /scene) |
| `arcane.fire` | *Flame Lance* (1 · 1F · beat); *Fire Shroud* (2 · 2F · rider); *Firestorm* (5 · 3F · beat, /long rest) |
| `arcane.frost` | *Rime Spear* (1 · 1F · beat); *Glaze* (3 · 2F · beat) |
| `arcane.storm` | *Arc Bolt* (1 · 1F · beat); *Thunderclap* (4 · 2F · beat) |
| `arcane.earth` | *Clutching Earth* (1 · 1F · beat); *Stoneskin* (3 · 2F · beat) |
| `arcane.illusion` | *Phantom* (1 · 1F · beat); *Veil* (2 · 2F · beat); *Mirror Host* (5 · 3F · beat, /scene) |
| `arcane.divination` | *Trace the Thread* (1 · 1F · beat); *Foresee* (4 · 2F · reaction, /scene) |
| `arcane.warding` | *Spell Ward* (1 · 1F · reaction); *Counterspell* (2 · 2F · reaction); *Unbinding* (3 · 2F · beat) |
| `arcane.mind` | *Honeyed Thought* (1 · 1F · beat); *Compel* (4 · 3F · beat) |
| `arcane.summoning` | *Call Servant* (1 · 1F · beat, /scene); *Banish* (3 · 2F · beat) |
| `arcane.necromancy` | *Wither* (1 · 1F · beat); *Drain Life* (2 · 2F · beat); *Raise the Fallen* (5 · 3F · beat, /long rest) |
| `arcane.alteration` | *Feather Fall* (1 · 1F · reaction); *Long Step* (2 · 2F · beat) |
| `divine.healing` | *Mend Flesh* (1 · 1F · beat); *Purge* (2 · 1F · beat); *Breath of Life* (5 · 3F · beat, /long rest) |
| `divine.warding` | *Sanctuary* (1 · 1F · beat); *Blessing* (2 · 1F · beat) |
| `divine.smiting` | *Smite* (1 · 1F · rider); *Searing Light* (3 · 2F · beat) |
| `divine.rites` | *Last Rites* (1 · 0F · beat); *Cleansing Rite* (4 · 2F · beat) |
| `divine.oaths` | *Sworn Purpose* (1 · 0F · beat, /long rest); *Binding Vow* (4 · 2F · beat) |
| `divine.revelation` | *Discern* (1 · 1F · beat, /scene); *Prophetic Dream* (3 · 0F · trigger, /long rest) |
| `divine.exorcism` | *Turn the Dead* (1 · 1F · beat); *Cast Out* (3 · 2F · beat) |
| `divine.pact` | *Patron's Brand* (1 · 1F · beat); *Blood Price* (5 · 1F · rider) |
| `primal.growth` | *Root Snare* (1 · 1F · beat); *Thorn Coat* (2 · 1F · rider); *Renewal* (4 · 2F · beat) |
| `primal.beastkin` | *Beast Speech* (1 · 0F · beat); *Borrowed Senses* (3 · 2F · beat) |
| `primal.weather` | *Gust* (1 · 1F · beat); *Fog Bank* (2 · 2F · beat); *Call Lightning* (5 · 3F · beat, /scene) |
| `primal.shapeshifting` | *Claws* (1 · 1F · rider); *Beast Form* (3 · 2F · beat); *Elemental Form* (5 · 3F · beat, /short rest) |
| `primal.spirits` | *Spirit Tongue* (1 · 0F · beat); *Spirit Bargain* (4 · 2F · beat, /scene) |
| `primal.elements` | *Cinder Stride* (1 · 1F · rider); *Undertow* (1 · 1F · beat); *Stolen Breath* (1 · 1F · beat); *Heave* (1 · 1F · beat); *Stone Shape* (3 · 2F · beat) |
| `primal.hexcraft` | *Evil Eye* (1 · 1F · beat); *Lift the Hex* (2 · 2F · beat) |
| `influence.persuasion` | *Silver Tongue* (1 · — · passive); *Turn the Room* (3 · 1F · beat) |
| `influence.command` | *Rally* (1 · 1F · beat); *Hold the Line* (4 · 2F · rider) |
| `influence.performance` | *Stirring Song* (1 · 1F · beat); *Captivate* (2 · 1F · beat) |
| `influence.intimidation` | *Cow* (1 · 1F · rider); *Break the Will* (5 · 3F · beat, /scene) |
| `influence.intrigue` | *Web of Whispers* (1 · 0F · beat, /scene); *Leverage* (4 · 1F · rider) |
| `influence.trade` | *Sharp Bargain* (1 · — · passive); *Appraiser's Eye* (2 · 0F · beat) |
| `influence.etiquette` | *Courtly Grace* (1 · — · passive); *Foreign Manner* (3 · — · passive) |
| `influence.insight` | *Read the Heart* (1 · 0F · beat); *Ear for a Lie* (2 · — · passive) |
| `craft.smithing` | *Keen Edge* (1 · 0F · beat); *Masterwork* (4 · — · passive) |
| `craft.woodcraft` | *Fletch True* (1 · 0F · beat); *Sound Timber* (2 · 0F · beat) |
| `craft.leathercraft` | *Field Patch* (1 · 0F · beat); *Cure Hide* (3 · — · passive) |
| `craft.textiles` | *Knot Lore* (1 · — · passive); *Dressed for It* (2 · 0F · beat) |
| `craft.alchemy` | *Quick Tincture* (1 · 0F · beat, /long rest); *Firepot* (2 · 0F · beat); *Grand Elixir* (5 · 2F · beat, /long rest) |
| `craft.cookery` | *Hearty Fare* (1 · 0F · trigger, /short rest); *A Table Laid* (3 · 1F · beat, /scene) |
| `craft.building` | *Dig In* (1 · 0F · beat); *Breach* (4 · 1F · beat) |
| `craft.artifice` | *Rig a Trap* (1 · 0F · beat); *Clockwork Servant* (5 · 2F · beat, /long rest) |
| `craft.jewelcraft` | *True Cut* (1 · — · passive); *Fine Setting* (3 · — · passive) |
| `craft.enchanting` | *Rune of Keenness* (1 · 1F · beat); *Bind Power* (4 · — · passive) |
| `influence.teaching` | *Patient Teacher* (1 · — · passive); *Lend the Art* (5 · 2F · beat, /scene) |
| `craft.scribing` | *Fair Copy* (1 · 0F · beat); *Field Map* (2 · 0F · beat) |
| `conduct.courage` (positive) | *Stand Fast* (1 · 0F · reaction, /scene); *Into the Breach* (3 · 1F · rider); *Undaunted* (5 · — · passive) |
| `conduct.generosity` (positive) | *Open Purse* (1 · 0F · trigger, /scene); *Shared Strength* (3 · 0F · rider); *The Widow's Mite* (5 · 0F · trigger, /long rest) |
| `conduct.honesty` (positive) | *The Plain Word* (1 · — · passive); *Unclouded* (3 · — · passive); *Word as Bond* (5 · 2F · beat, /scene) |
| `conduct.humility` (positive) | *Quiet Service* (1 · — · passive); *The Unseen Hand* (3 · — · passive); *The Last Made First* (5 · 2F · beat, /scene) |
| `conduct.justice` (positive) | *Name the Wrong* (1 · 0F · rider); *Mark of Judgment* (3 · 1F · beat, /scene); *The Scales Balanced* (5 · 2F · reaction, /scene) |
| `conduct.loyalty` (positive) | *At Your Side* (1 · — · passive); *Take the Blow* (3 · 1F · reaction, 1/round); *Unbroken Bond* (5 · 2F · reaction, /long rest) |
| `conduct.mercy` (positive) | *The Open Hand* (1 · 1F · trigger, /scene); *Balm of Mercy* (3 · 1F · beat); *Quarter Given* (5 · 2F · reaction, /scene) |
| `conduct.piety` (positive) | *The Daily Office* (1 · 0F · trigger, /day); *Hallow* (3 · 1F · beat, /scene); *Intercession* (5 · 2F · beat, /long rest) |
| `conduct.protection` (positive) | *Interpose* (1 · 0F · reaction, 1/round); *Shelter the Weak* (3 · 1F · rider); *None Shall Pass* (5 · 2F · rider) |
| `conduct.restraint` (positive) | *Measured Blow* (1 · 0F · rider); *Still Water* (3 · 1F · reaction, /scene); *The Empty Hand* (5 · 1F · rider) |
| `conduct.generosity` (negative) | *Grasping Hand* (1 · — · passive); *The Price of Everything* (3 · 0F · beat); *Hoard-Heart* (5 · 0F · trigger, /long rest) |
| `conduct.honesty` (negative) | *Forked Tongue* (1 · — · passive); *False Witness* (3 · 1F · beat); *Web of Lies* (5 · 2F · beat, /scene) |
| `conduct.humility` (negative) | *None My Equal* (1 · — · passive); *Towering Will* (3 · — · passive); *Peerless* (5 · 1F · rider) |
| `conduct.justice` (negative) | *Heavy Hand* (1 · 0F · rider); *Make an Example* (3 · 1F · beat, /scene); *Iron Decree* (5 · 2F · beat, /scene) |
| `conduct.loyalty` (negative) | *Knife in the Back* (1 · 0F · rider); *Turncoat* (3 · 1F · beat, /scene); *The Last Embrace* (5 · 2F · beat, /scene) |
| `conduct.mercy` (negative) | *Twist the Knife* (1 · 0F · rider); *Terror of Example* (3 · 1F · trigger, /scene); *No Quarter* (5 · 1F · rider) |
| `conduct.piety` (negative) | *Defiler's Touch* (1 · 1F · beat); *Scorn the Holy* (3 · — · passive); *Unhallow* (5 · 2F · beat, /long rest) |
| `conduct.protection` (negative) | *Cull the Weak* (1 · 0F · rider); *Living Shield* (3 · 1F · reaction, /scene); *The Cold Calculus* (5 · 2F · reaction, /long rest) |
| `conduct.restraint` (negative) | *Red Mist* (1 · 0F · rider); *Blood for Blood* (3 · 0F · trigger, 1/round); *Wrath Unbound* (5 · 2F · rider) |
| branch working (`deed.arcane`) | *Force Bolt* (1 · 0F · beat) |
| branch working (`deed.divine`) | *Rebuke* (1 · 0F · beat) |
| branch working (`deed.primal`) | *Wild Lash* (1 · 0F · beat) |

**T-05-13 The authored rites.** `[D]` (`data/rituals.yaml`; every rite also has a 4-segment strain clock.)

| Rite | First tag | Scale · grade | Progress clock · DC tier · Focus · time per step | What it does (the data's `scope` is binding) |
|---|---|---|---|---|
| `rit.ward_threshold` Ward the Threshold | `arcane.divination.detection` | local · trained | 6 · hard · 2 · 1 interval | Set a watch on an opening that tells its maker when it is crossed. |
| `rit.scrying_pool` The Scrying Pool | `arcane.divination.scrying` | local · expert | 6 · hard · 2 · 1 interval | See and hear a known place or person from afar through a still surface. |
| `rit.bind_familiar` Bind a Familiar | `arcane.summoning.familiar` | personal · trained | 4 · moderate · 1 · 1 hour | Bind a small creature to yourself as a lasting companion. |
| `rit.circle_of_binding` Circle of Binding | `arcane.summoning.binding` | local · expert | 6 · hard · 2 · 1 interval | Hold one otherworldly being inside a drawn boundary. |
| `rit.sending` A Sending | `arcane.mind.telepathy` | personal · trained | 4 · moderate · 1 · 1 interval | Carry a few words to one known mind at a distance. |
| `rit.raise_shade` Raise a Shade | `arcane.necromancy.communing` | local · expert | 6 · hard · 2 · 1 interval | Call the shade of one dead person to answer. |
| `rit.seal_the_way` Seal the Way | `arcane.warding.sealing` | local · trained | 6 · hard · 2 · 1 interval | Close a door or lid so that only its word opens it. |
| `rit.foresight` The Long Look | `arcane.divination.foresight` | local · expert | 6 · hard · 2 · 1 hour | See the shape of what a chosen course will meet. |
| `rit.consecrate_ground` Consecrate Ground | `divine.warding.consecration` | site · expert | 8 · very hard · 3 · 1 hour | Give a place into your keeper's keeping. |
| `rit.funeral` The Funeral Rite | `divine.rites.funerary` | personal · trained | 4 · moderate · 1 · 1 interval | Send the dead on with the words of the faith. |
| `rit.oath_binding` The Oath-Binding | `divine.oaths.binding` | local · trained | 6 · hard · 2 · 1 interval | Bind two or more willing parties to their sworn word. |
| `rit.purification` Purification | `divine.rites.purification` | local · trained | 6 · hard · 2 · 1 hour | Wash a lasting foulness from one being. |
| `rit.vigil_of_healing` Vigil of Healing | `divine.healing.sustaining` | local · trained | 6 · hard · 2 · 1 watch | Keep watch over a body through the night so that it mends. |
| `rit.augury` Augury | `divine.revelation.prophecy` | personal · trained | 4 · moderate · 1 · 1 interval | Ask your keeper whether a course is well or ill. |
| `rit.great_exorcism` The Great Exorcism | `divine.exorcism.banishing` | site · expert | 8 · very hard · 3 · 1 interval | Drive a haunting or a possessor out for good. |
| `rit.seasonal_blessing` Blessing of the Season | `divine.rites.seasonal` | site · expert | 8 · very hard · 3 · 1 hour | Ask your keeper's favor on a community's season. |
| `rit.call_rain` Call the Rain | `primal.weather.rain` | regional · master | 12 · legendary · 4 · 1 hour | Turn the weather of a whole country for a day. |
| `rit.speak_with_the_land` Speak with the Land | `primal.spirits.speaking` | local · trained | 6 · hard · 2 · 1 interval | Ask a place what it has witnessed. |
| `rit.beast_bond` The Beast-Bond | `primal.beastkin.bond` | personal · trained | 4 · moderate · 1 · 1 hour | Join yourself to one animal as its companion. |
| `rit.lift_curse` Lift the Curse | `primal.hexcraft.unhexing` | local · expert | 6 · hard · 2 · 1 hour | Unmake a lasting curse. |
| `rit.lay_curse` Lay a Curse | `primal.hexcraft.cursing` | local · expert | 6 · hard · 2 · 1 hour | Bind a lasting ill onto one named being. |
| `rit.harvest_bounty` Bounty of the Field | `primal.growth.bounty` | site · expert | 8 · very hard · 3 · 1 hour | Make one field or orchard bear beyond its measure. |
| `rit.spirit_walk` The Spirit Walk | `primal.spirits.ancestors` | personal · trained | 4 · moderate · 1 · 1 hour | Go out of yourself to ask those who came before. |
| `rit.imbue` Imbue | `craft.enchanting.imbuing` | local · trained | 6 · hard · 2 · 1 hour | Seat one magical property in a made thing for a season; made lasting, it is 08.6.10's worked property: one per item, ever [integration: IR ch.08 to 05]. |
---

## Worked examples

Two characters carry the examples. **Wren** is 00's forester, here at two points in her life: unrecognized
(Focus 4/4), and as a tier-1 **Archer** (`call.archer`, key `deed.martial.archery`; competence +3; Focus
5/5). Her attributes are 00's: Might +1, Agility +3, Endurance +1, Wits +2, Intellect 0, Presence 0,
Resolve −1. **Ash** is a tier-3 **Pyromancer** (key `deed.arcane.fire`; competence +5; training grade
`expert`; Intellect +3, Resolve +1, Agility +1; Vitality 12; Focus max 4 + 3 = **7**), so his casting
modifier is +8 and his effect DC is 10 + 3 + 5 = **18**. Numbers that belong to chapters not yet written
(adversary blocks, armor, what a condition does) are marked *(illustrative; ch.NN owns)*; this chapter's
own mechanics (costs, uses, ranks, budgets, miscasts, clocks, composition) are exact and match the data.

### WE-05-1 A spell cast end to end

*Situation.* A crypt stair. A ghoul (`creature.undead.ravenous`, T2: Vitality 10, Guard 13
*(illustrative; 09)*) stands at `band.near`, outlined against the torch Wren dropped on the landing
(fact `obj.torch_02.lit_at = loc.crypt.landing`, recorded two beats ago). Player: "Flame Lance, and I
put everything into it."

1. **Held and rank.** `ab.flame_lance`, calling partition, picked through the Pyromancer at tier 3:
   rank = min(3, 1 + floor((3 − 1) ÷ 2)) = **2**. Rank 2's literal text: *"Throw fire at one target
   within band.near. On a success it takes Heavy fire harm (shifted by delivered reach) and is burning."*
2. **Validation** (PR-05-1 step 2). Timing: his beat. Limitation: one target he can see within
   `band.near`: yes. Arcane signature: `trait.action.speech` and `trait.action.manipulate`: he is not
   choking and his off hand is free: yes. Uses: none tracked (Focus only).
3. **Flare.** "Everything into it" is the **Hard** flare (the list on the ability: hard, far, wide,
   lasting, quiet, sure). At grade `expert` he may take one.
4. **Cost** (05.6.3): base 1 + flare 1 = **2**. Focus 7 → would be 5.
5. **Frame.** Aimed; anchor `verb.strike`; attribute Intellect **+3**; deed tag
   `deed.arcane.fire.blast`, competence **+5** from the calling at `deed.arcane.fire`; edge 0. One lever:
   the torch's light behind the ghoul, typed **Precision** (+2). Total **+10** against Guard **13**: he
   needs a 3. Odds: success or better 90%, critical success 40% (13+), critical failure 5% (a natural 1:
   total 11 is a failure by 2, stepped down). Stakes **Risky** (on a failure the ghoul closes:
   `cost.footing`, S2). Reach **Standard**.
6. **OFFER.** "Flame Lance, flared hard: 2 Focus, you need a 3 (90%). It will be seen and heard on the
   stair below. If it fails the ghoul is on you; if it goes badly wrong the fire turns on you." Commit.
7. **Commit.** `update_quantity(focus, −2)` → 5/7. `on_focus_spent` → ch.03 counts `cnt.focus`, 2 units,
   at `deed.arcane.fire.blast`.
8. **Roll.** d20 = **9** → total 19, margin +6: **success**; delivered reach 2.
9. **Harm, dealer side** (00.10.5): base S3; reach step (2 − 2) = 0; Hard flare +1 (an effect step,
   inside the ±2 cap) → **S4**; convert → **8**; harm edge 0. **Receiver side:** no reduction, no fire
   resistance → **8**. The ghoul is at 2 (bloodied: shown).
10. **Condition.** `apply_condition(cond.burning)`, one stack. At the ghoul's turn end its periodic
    S1 fire harm *(illustrative; 06)* brings it to 1.
11. **Hooks.** The lance is a beat: its events are depth 0. Ash's arcane Focus trigger needs a critical
    success: it does not fire. The flare's tell and `trait.sense.visible`/`audible` are method
    consequences: the site's listening clock ticks if it lists them (10).
12. **Narration packet:** the rank's text verbatim, "8 fire harm, bloodied, burning (visible)", the
    flare's tell. The narrator may say the stair lights white and the ghoul's rags catch. It may not say
    the ghoul is blinded, or that the stair is now on fire (no fact says the stair burns).

*Boundary: the same cast, a critical success.* d20 = 14 → 24, margin +11. Delivered reach 3: reach step
+1, flare +1 → S5 = **12** harm; the ghoul is destroyed. The arcane trigger fires (`on_degree`, critical
success, an ability under the calling key): +1 Focus → 6/7, `generated_this_scene` = 1 of 3.

*Boundary: the same cast, a natural 1.* Critical failure → **miscast** in place of the heavier menu cost
(05.7.5). Risky stakes → S3, one rung heavier for the flare → **S4 Backlash**: 8 raw harm to Ash
(Vitality 12 → 4), `cond.dazed` for a round, and his sustained workings end. The OFFER said so.

*Non-example.* "The lance also sets the ghoul's nest alight so the others can't come up." The ability's
target is one being. Setting the nest alight is a second beat (a stretch of the same ability at a thing,
05.5.2, or a thrown torch), with its own frame.

### WE-05-2 An ability stretched within its principle

*Situation.* Wren, unrecognized, spent six weeks of a winter's downtime with the hedge-witch of
Ashford, who vouched for her to the spirit of the Mere (the `requires` of a primal training): four weeks
for `lic.training.primal_weather` (8 segments at 2 per week) and two more for `ab.gust` (6 segments at 3
per week). She holds Gust in the acquired partition at rank 1. Training competence `deed.primal.weather` +2; Resolve −1; effect DC
10 − 1 + 2 = **11**. Focus 4/4. She is not good at this, and that is the point of P4: breadth is
available and is not power.

On the Mere causeway a cloud of marsh gas lies over the first span (hazard `haz.marsh_gas`, S2,
`harm.venom.gas` *(illustrative; 10)*). The day's weather record says *breezy, from the west*. Player:
"I use Gust to blow the gas off the bridge."

1. **Literal scope.** Gust's text strikes "up to two targets within band.near in a line", pushing and
   knocking them prone. A gas cloud is not a target that can be pushed a band or knocked prone: the
   scope does not cover this. → is it a **stretch**?
2. **Decision 1, same operation.** Principle: *"Push a body of air in one direction."* The use pushes
   (the same verb) a body of air with the gas in it (the same object category), at a different target
   and scale. **True.** **Decision 2, sensitive upgrade:** none. → stretch, gate mode `stretch`.
3. **Source present** (05.7.3): moving air under open sky: yes (the weather fact).
4. **Prices** at grade `trained`: DC +5, +1 Focus, reach Limited. Cost 1 + 1 = **2** Focus.
5. **Frame.** A stretch is always rolled: `verb.handle`, attribute Resolve **−1**, deed tag
   `deed.primal.weather.wind`, competence **+2**. Lever: the west breeze, typed Precision (+2). Total
   **+3**. Obstacle: the cloud, tier `[J:rung]` Moderate (15), stored as `haz.marsh_gas_01.disperse_dc =
   15`; +5 stretch = **20**. She needs a 17: 20%. Stakes Risky (a failure means she breathes it trying:
   the hazard's own S2). Reach capped Limited.
6. **OFFER.** "Stretching Gust: 2 Focus, you need a 17 (20%). Best case the first span is clear for a
   few breaths. Or hold your breath and run it: Endure, Moderate." The player commits anyway.
7. **Roll.** d20 = **18** → 21: success. Focus 4 → 2. Delivered reach 1 (capped): the gas is pushed off
   the first span for `rounds:3` (the effect mapped in step 3 of PR-05-2: one reach unit of object
   state). She crosses the span; the second span is still hers to deal with.
8. **Ruling logged:** signature `ab.gust+stretch+gas_cloud`, DC source tier Moderate +5, reach Limited.
   Next time anyone with Gust tries it, the numbers are these.

*Outside the boundary.* "I use Gust to pull the ferryman's dropped pole back to me." The principle
pushes. Pulling is a different operation: decision 1 is false; no Focus is spent; the redirect offers
pushing the pole against the far bank and wading for it.

*Tempting non-example.* "I use Gust to carry my voice to the far shore so the ferryman hears every
word." Carrying a sound across a lake so that it is understood is perception at a distance for the
hearer and a message for her: no part of *pushing air* names it, and it would hand her a capability
(`rit.sending` exists for it). Decision 1 is false on the object (speech is not a body of air to be
pushed, it is information), and a shout across the water is already the basic Talk, loud.

### WE-05-3 Abilities composing through the substrate

Three cases, one for each way two abilities meet.

**(a) Two claims on one slot (priority-exclusive).** Wren the Archer holds `ab.cinder_stride` (a gift of
the hedge-witch, acquired partition, rank 1, priority rank 10) and has coated her spear in Rime Oil (an
applied consumable, rank 20; WE-00-6). Both claim `slot.strike_delivery`. `use_ability` warns: "Rime Oil
(rank 20) owns your Strikes; Cinder Stride would be suppressed: no fire, no +1." She has three choices,
all by lookup: spend nothing; wipe the oil off (drop the higher claim, a free activity) and then spend 1
Focus on Cinder Stride; or keep the oil. Nothing merges: no composite is keyed on that pair.

**(b) A rider feeds a trigger; a trigger does not.** Hale, a tier-3 hammerman, holds
`ab.stagger_blow` (rider, 1 Focus) and `ab.pressing_advantage` (trigger on `on_condition_applied`, by
self; once per scene). He declares a Strike with Staggering Blow. The hit is a depth-0 event; the
rider's `cond.dazed` is applied by the declared beat itself, also depth 0; Pressing Advantage fires:
+1 Focus (net cost of the blow: 0), `generated_this_scene` = 1. Had he instead held
`ab.quarrys_mark` (a *trigger* on `on_attack_hit`), its `cond.exposed` would be a depth-1 event and
Pressing Advantage would not fire (INV-12), which is exactly WE-00-6. The difference is the `timing`
field, visible on both records.

**(c) A named composite.** Ash faces Captain Hesk's squire, who was chilled a moment ago by the
hedge-witch's frost bolt: `cond.chilled` (tag `harm.frost`), one stack. Ash casts Flame Lance (rank 2,
no flare; +8 against Guard 12 *(illustrative)*): d20 = 11 → 19, success, reach 2.
- Dealer side: base S3, no steps → the harm event deals `harm.fire.flame`.
- The engine finds `comp.thermal_shock` (keys `harm.fire`, `harm.frost`; present because a depth-0 fire
  harm event lands on a target carrying a frost-tagged condition): the harm is **one severity rung
  heavier** → S4 = **8**, and `cond.chilled` ends. Because the composite ended the chill first,
  Flame Lance's own `cond.burning` then applies with nothing to neutralize it (how chill and burning
  cancel each other when both would stand is 06's, WE-00-7).
- Receiver side: the squire's leather reduces `harm.physical` only → 8 fire harm.
- Budget check on the composite: one severity step (2) + one cleanse (2) = 4 EU, the cap.

*Non-example.* "My Flame Lance and Wren's Rime Oil together should shatter his sword." No composite is
keyed on that pair for an object, `comp.shatter` needs a *frozen* target and *crushing* harm, and a
sword is not a creature carrying a condition. The engine returns nothing, so the narrator adds nothing.
Breaking the sword is `ab.sunder`, or Force.

### WE-05-4 Slots reallocated at a consolidation

*Before.* Late in her second year Wren holds two callings and nine abilities:

| Partition | Held | Source |
|---|---|---|
| calling (7 of 12) | Aimed Shot (rank 2), Volley (rank 1), Surefoot (rank 2), Read the Field (rank 1) | Archer, tier 3: 4 picks |
| | Quarry's Mark (rank 1), Read Sign (rank 1), Pathfinder (rank 1) | Tracker, tier 2: 3 picks |
| acquired (2 of 4) | Cinder Stride (rank 1), Gust (rank 1) | gift; learned |
| equipped (1 of 4) | the Ember-Fang Charm has no active ability; her bow's *Far-Seeing* is bound | item |

Pick allowance `A` = min(12, 4 + 3) = 7. Seats: 2 of 3 deed seats. Focus max = 4 + 3 (highest tier) + 0
(the Tracker is at tier 2, below 3) = **7**.

*The offer.* At the `season` boundary `h.04.season_consolidation` finds `req.hybrid.1` met for martial ×
wilds and offers **Ranger** (04.8.5, hybrid consolidation). She accepts.

*After, by 04.8.5 and this chapter:*
1. **Tier.** The Ranger's tier is the highest tier, not above 3, whose threshold the new key meets: here
   **2**. Focus max stays **7**: `T_high` counts a consolidated calling's specialties at their
   `tier_reached` (05.6.1), and the Archer specialty reached 3. Consolidation costs nothing on the day.
2. **Picks.** All seven abilities stay. `picks_total[2]` for a hybrid is 3, so `legacy_picks` = 7 − 3 =
   **4**. Allowance `A` = min(12, 3 + 4) = 7: the calling partition is exactly as full as before.
3. **Ranks** (05.3.9). Each pick's `T` is the higher of the Ranger's tier (2) and the `tier_reached` of
   the specialty it came from: the Archer's four keep `T` = 3 (Aimed Shot and Surefoot stay rank 2); the
   Tracker's three have `T` = 2 (rank 1, as before). Nothing got weaker.
4. **What changed structurally.** Two seats became one. Two ladders were retired. The Archer's and
   Tracker's separate allowances (which would have reached 6 + 6 = 12 at tier 5 each) became one
   allowance that reaches 6: the next four tier-ups of the Ranger each **cancel a legacy pick** and add
   no ability. The partition has not grown and will not; what she gained is a free seat.
5. **The season re-pick** (04.8.7), same boundary: one swap, with the Ranger's pool gate (own: both
   branches). She swaps Pathfinder for **Beast at Heel** (`deed.wilds.animals.training`, `min_tier` 2:
   eligible at tier 2). Pathfinder returns to the pool. Slots used: still 7.

*Boundary: at the cap.* A character with three callings at tier 3 holds 12 of 12. Reaching tier 4 in one
of them grants a pick with no free slot: the pick **replaces** a held calling ability of the player's
choice (05.2.5), which is retired from the character. If the new pick `replaces` the old ability by its
data (an upgrade path), it simply takes that slot.

*Non-example.* "My acquired partition has two free slots, so the tier-4 pick goes there." Partitions do
not lend (05.2.1). Acquired slots are filled only by learning, teaching, absorption or gift.

### WE-05-5 A Focus economy across a fight, a rest and a day

*One fight, traced.* Wren the Archer (Focus 5/5; attack +6; Guard 14; Vitality 12) against a cinder hound
(T2: Vitality 10, Guard 13, attack +4, S2 harm *(illustrative; 09)*). One beat per round each
*(illustrative; 06 owns the action economy)*.

| Round | Wren | Focus | Hound |
|---|---|---|---|
| 1 | Strike with **Aimed Shot** (rider, 1 Focus; she has not moved): Precision lever +2, total +8, needs 5. d20 = 11 → 19: success. Harm S2 + one rung = S3 = **5**. | 5 → 4 | 10 → 5 (bloodied) |
| | Her attack hit: **Quarry's Mark** asks (trigger, 1 Focus, once per scene). Yes: the hound is exposed until the scene ends. | 4 → 3 | exposed |
| | | | It bites: +4 against 14, d20 = 13 → 17: S2 = 3. Wren 12 → 9. |
| 2 | Aimed Shot again; exposed gives her a second Precision lever (a different fact): +10, needs 3. d20 = 6 → 16: success. S3 = 5. | 3 → 2 | 5 → 0: defeated |

Three Focus spent in two rounds; she ends at 2/5 and is not Spent. `conflict_end` and `scene_end`
refresh Quarry's Mark's use. A **breather** (one interval) restores 1 → 3/5. Had she camped an hour (a
**short rest**), ceil(5 ÷ 2) = 3 more → 5/5.

*The same fight, simulated* (20,000 runs each; script
`rules/_process/simulation/05-focus-sim.py`; results in `05-focus-sim.md`; the model's assumptions are
stated there and are 00.3.7's):

| Case | Wins | Rounds | Focus spent | Focus left | Ends Spent | Vitality left (wins) |
|---|---|---|---|---|---|---|
| Wren, tier 1, Focus 5, **spends none** | 87.0% | 4.44 | 0 | 5.00 | 0% | 6.7 |
| Wren, tier 1, Focus 5, spends freely | 99.6% | 2.36 | 3.34 | 1.66 | 6.2% | 9.7 |
| Wren, tier 1, **starting at 2** | 96.9% | 3.04 | 2.00 | 0.00 | 100% | 8.6 |
| Ash, tier 3, Focus 7, **spends none** (a staff) vs T3 | 0.1% | 3.00 | 0 | 7.00 | 0% | 3.4 |
| Ash, tier 3, Focus 7, spends freely vs T3 | 81.3% | 3.60 | 5.64 | 1.84 | 30.5% | 7.9 |
| Ash, tier 3, **starting at 3** vs T3 | 40.7% | 3.31 | 3.09 | 0.21 | 80.5% | 5.8 |

What the numbers say: (1) a full pool roughly **halves** a fair fight (4.4 rounds to 2.4) and turns the
remaining risk into spent Focus; (2) a fight at one band costs a tier-1 character about **two thirds of
the pool** and a tier-3 caster about **four fifths**, so every fight leaves a real decision about the
next one; (3) a martial character without Focus is weakened, a caster without Focus is nearly helpless
against an equal foe (0.1%), which is the lever that makes overdraw (05.6.6) and the rest ladder matter
to casters most; (4) a caster who starts a fight at 3 of 7 is at 41%: the codex shows the pool, and the
threat advisory (09) plus this number is the telegraph.

*A venture day* (Wren, five fights against T2 foes; a breather after every fight, of which only two
between short rests restore Focus; Vitality restored between fights so that the measure isolates
Focus):

| | Fight 1 | Fight 2 | Fight 3 | Fight 4 | Fight 5 |
|---|---|---|---|---|---|
| **Short rests after fights 2 and 4**: Focus at start (mean) | 5.00 | 2.66 | 3.00 | 1.00 | 3.00 |
| Focus spent in the fight (mean) | 3.34 | 2.66 | 3.00 | 1.00 | 3.00 |
| **Breathers only**: Focus at start (mean) | 5.00 | 2.66 | 1.00 | 0.00 | 0.00 |

With two short rests she spends 13 Focus across the day from a pool of 5 (the rests restored 8),
and never starts a fight empty. With breathers alone she is at 0 from the fourth fight on. The hour a
short rest costs is therefore the real price of Focus, paid in 10's checks and 11's clocks: the
recovery numbers were chosen so that this is so (DL-05-14).

*Non-example.* "I take ten breathers in a row to get back to full." Only two breathers between short
rests restore Focus (05.6.9); the third restores none and the codex says so before the interval is
spent.

### WE-05-6 Learning by observation

*Situation.* Ash watched a cult adept cast `ab.fire_shroud` across a courtyard (the scene log holds the
adept's `use_ability`; the DM confirms line of sight) → `pc.witnessed.ab.fire_shroud`. Two scenes
later, cornered by the adept's hounds, the player says: "I do what she did. The shroud."

1. **Legal?** He holds `lic.training.arcane_fire` at `expert` (technique cap `min_tier` 4); Fire Shroud
   is `deed.arcane.fire.shaping`, `min_tier` 2, active, not oath-gated; he does not hold it; witnessed:
   true. → emulation (PR-05-3).
2. **Shape.** Fire Shroud is a rider with `check: none`, so it rides a beat and that beat takes the
   shift. He rides it on a Flame Lance at the nearest hound (Guard 13).
3. **Prices.** Lance DC 13 + 5 = **18**; Focus: lance 1 + shroud 2 × 2 = **5** of his 7; the ridden
   beat's reach is capped at Limited; no flare.
4. **OFFER.** "Emulating Fire Shroud on a Flame Lance: 5 Focus, you need a 10 (55%). The lance will be
   weak. You will have 2 Focus left." Commit. Focus 7 → 2.
5. **Roll.** d20 = 12 → 20: success. The lance lands at Limited reach (S3 − 1 rung = S2 = 3 harm, and
   burning). The shroud runs at **rank 1** for the scene: he halves fire harm, and each foe that ends
   its turn engaged with him takes Light fire harm.
6. **Learning.** `clk.learn.ab.fire_shroud` is created (6 segments for `min_tier` 2) and ticks by
   delivered reach: **1 of 6**. Nothing else is granted (INV-7).

*What it would take to know it.* Five more successful emulations at 4 Focus each for the shroud; or the adept's
grimoire (a text: 2 ticks per week of study → three weeks); or a willing teacher (3 per week → two
weeks). On completion it enters his acquired partition at rank 1, or, if his Pyromancer has a pick to
spend, it can be **promoted** to the calling partition and rank with his tier (05.8.6).

*Outside.* The adept also threw `ab.rime_spear`. Ash has no frost training: G3;
`lic.training.arcane_frost`'s fallback is `none`; the redirect names a teacher or a text.
*Non-example.* "I rolled a 20 emulating it, so I've got it now." A roll never grants a license; a
critical success ticks the clock by the delivered reach (still capped at Limited: 1) and gives the
follow-up lever of 01.9.1.

### WE-05-7 A rite performed, and a rite designed

**Performed.** Ash wants to ward their rooms at the Grey Goose with `rit.ward_threshold` (local scale:
progress 6, DC tier Hard = 20, Focus 2, one interval per step; a pinch of silver dust, price band 1).
He has the rite's text in the adept's grimoire. The first time he asks, the requirement check refuses
him by lookup: the rite's first tag is `deed.arcane.divination.detection`, and his training is fire.
"The grimoire's hand is clear, but nothing in you knows how to read a threshold." Paths, from the
license entry: a month with a teacher or two with a manual for `lic.training.arcane_divination`, then
the rite's own 6-segment learning clock.

Three months later, trained (`trained` grade; competence +2 at `deed.arcane.divination`; casting
modifier Intellect +3 + 2 = **+5**), he performs it. Focus 7 → 5. Two clocks appear: **Ward the
Threshold 0/6** and **the working frays 0/4**.

| Step | d20 | Total vs 20 | Result | Progress | Strain | Time |
|---|---|---|---|---|---|---|
| 1 | 16 | 21 | success, reach 2 | 2/6 | 0/4 | 1 interval |
| 2 | 9 | 14 | failure (Risky): `cost.time`, S2 → one more interval; strain +U(S2) = 1 | 2/6 | 1/4 | 2 intervals |
| 3 | 15 | 20 | success | 4/6 | 1/4 | 1 interval |
| 4 | 5 | 10 | **critical failure** (margin −10): the cost is one rung heavier (S3): `cost.drain`, 2 Focus; strain +U(S3) = 2 | 4/6 | 3/4 | 1 interval |
| 5 | 18 | 23 | success | 6/6 **complete** | voided | 1 interval |

Six intervals in all; the inn's `interval` handlers ran six times (light, the site check). Focus 7 → 5
at the start, → 3 after step 4. The ward stores his effect DC for this art, 10 + 3 + 2 = **15**, on each
of three openings for a week. Had step 5 failed with a cost of S2 or more, strain would have filled:
the rite fails, the silver is gone, and Ash takes an arcane Backlash at S3 (5 harm, dazed).

**Designed.** Later the player wants "a ward that hides our winter camp from scrying".
- EXPRESSIBLE: `eff.restrict` (forbid the sense *scrying* on the place) and `eff.write_fact` → (b).
- SCALE: a camp of a dozen, for the season → **site**: grade `expert` needed in
  `deed.arcane.warding`. Ash has that school only at `trained` → he can research it with someone who
  does, or commission it (15). He finds the warden of Carrow Hold.
- The row: research clock 12; the rite: progress 8, Very hard (25), Focus 3, **3 conditions**.
  `roll_table(tbl.05.rite_conditions)` draws 4 (**material**), 8 (**place**), 2 (**first you must**).
  The DM fills them from state: a component of price band 3 (the Oracle: "is there cold iron from a
  fallen star in the hold's treasury?" Unlikely, 81 → yes); the camp must stand on the old barrow (a
  place with recorded resonance); and first the barrow's spirit must consent (a thread).
- The player sees all of it before a week is spent, and decides whether the winter is worth it.

### WE-05-8 Spent, overdraw, and a push

**Overdraw.** Ash, Focus 1/7, Vitality 9, two ghouls on the stair. He casts Flame Lance (1 Focus) → 0:
**Spent**. His sustained `ab.phantom` ends at once (05.6.5). On the ghouls' turn one hits for S3 (5).
The player wants Spell Ward (reaction, 1 Focus; rank 2: two rungs lighter). Shortfall 1 → the tool
returns the overdraw price: **S2, 3 Vitality** (`harm.mind.strain`, no reduction, never lethal) and one
stack of `cond.exhausted` until his next long rest; it is his first overdraw of three. The arithmetic
is on the OFFER line: pay 3 to turn 5 into 1 (S3 two rungs lighter is S1). He accepts: Vitality 9 − 3 −
1 = **5**, exhausted ×1, still Spent. *Refused case:* at Vitality 3 the same overdraw would bring him to
0: the tool refuses it (05.6.6), and the hit lands whole.

**Push, with no ability at all.** Wren before any calling (Focus 4/4; competence `deed.wilds.tracking`
+2 from her origin) follows the cinder hound's trail: Observe, Wits +2, competence +2, against the
trail's tier Moderate (15); a pursuit clock of 6. Reach Standard. She **pushes** for reach (1 Focus →
3/4): framed reach Great. d20 = 13 → 17: success, delivered reach 3: the pursuit clock ticks **3**
instead of 2. `on_focus_spent` carries `deed.wilds.tracking.trailing`.
- *Outside:* the same Wren tries to push a Handle beat at a lock. Her competence there is the floor only
  (and lockpicking is G3 for her anyway): a push is refused; nothing is spent.
- *Non-example:* "I push for +2 on the roll." A push buys reach or stakes, never the roll (05.6.7).

**Spent, and still casting (05.7.11)** `[revision: I-009]`. Ash, Spent and at Vitality 5 after the overdraw,
the second ghoul (T2, Guard 13) engaged with him. He casts **Force Bolt** through his fire school: one
action, 0 Focus, Intellect +3 + competence +5 = **+8** against Guard 13 (needs a 5: 80%). Grade `expert`
→ rank 2 → Heavy (S3). Spent adds no snag: the bolt is not `trait.action.concentrate`. d20 = 14 → 22,
margin +9: success, 5 force harm (armor would not reduce it, 09.3.6); the ghoul at 10 is bloodied. His
second bolt (−2 repetition) needs a 7; a natural 20 on it would be a critical success, S4, and push the
ghoul to `band.close`. No Focus moves, and no flare or push is possible while Spent.
- *Boundary:* the same bolt flared Hard. Refused: a flare costs Focus and he is Spent (05.6.5). The
  working itself is still offered.
- *Boundary:* Ash an hour later at Focus 4, pushing the bolt: 1 Focus, framed reach Great, Grievous on a
  plain success. `cnt.focus` lands at `deed.arcane.fire` (the school he cast it through).
- *Non-example:* "I use Force Bolt to set the ghoul's rags alight." The working shapes nothing; burning is
  Flame Lance's (or a stretch of it), and the redirect says so.

### WE-05-9 Tempting non-examples, with the refusal each gets

| The player says | Why it is tempting | The ruling, by lookup |
|---|---|---|
| "My Hard Country means the frost wraith's touch does less." | cold is cold | The limitation reads "hazards of cold and of heat". The wraith's touch is an attack. The `excludes` line names armor, cover or a ward. No effect; narration may not soften the touch. |
| "I sustain Veil and Phantom together." | both are illusions | One sustained working (05.4.7). Starting the second ends the first; the tool warns. |
| "Quarry's Mark tells me where it went." | it is a *mark* | Scope: exposed, and a Precision lever on tracking beats this scene. Its `narration_may_not_imply` lists knowledge of location. Track it: Observe, with the lever. |
| "I flare it twice: Hard and Far." | Focus to spare | Two flares need `master` grade (05.6.8). At `expert`: one. |
| "Smite and Cinder Stride both, so fire *and* radiance." | it sounds designed | It is: `comp.holy_fire` exists for exactly that pair, and the engine reports it. For any pair with no entry, the higher rank owns the slot and nothing merges. |
| "I'm out of Focus but it's only a cantrip-sized Flame Lance." | small workings are free | A small working is tool-equivalent and harms nothing (05.7.6). Throwing fire at a being is the spell: 1 Focus, or an overdraw at 3 Vitality. |
| "The rite failed, so I just start again with the same silver." | nothing visibly broke | When strain fills, components are consumed (05.8.2). When a rite is *left* and decays to 0, they are kept. |

---

## Edge cases & adaptation anchors

### Anchors this chapter offers

Seven rules of this chapter are anchors (00.2.6): rules the DM may reach for when an action matches no
rule. Four are written as full cards in Rules (05.5.2 Stretch, 05.5.4 Emulate, 05.7.6 Small working,
05.8.4 Designing a rite). Three more are carded here because their rules above are `[D]` procedures.

```
### 05.8.2  Performing a rite (as an anchor)                       [D]
Anchor:             yes. Intent verbs: "perform the ritual", "work it slowly and carefully", "a long
                    working", "do it properly this time". Knobs: dc (default the rite's tier; allowed
                    delta: none); time_cost (default the rite's time_per_tick; allowed delta: one step
                    longer); targets (the rite's own); focus_cost (the rite's own); stakes (default
                    Risky; allowed delta: Dire when a hostile presence is in the place). Degree table:
                    success -> progress by delivered reach; failure -> one listed failure cost and
                    strain by U(severity); 01.18.2 otherwise. Covers: any long, careful task with a
                    way to go wrong that is not sudden: the two racing clocks (progress by reach,
                    a 4-segment strain clock by U of each failure's cost) are the reusable shape, for
                    surgery, a forging, disarming a great trap, a tense negotiation in stages. Does
                    not cover: a single beat (01); a project across downtime (15: a project clock
                    alone, no strain clock).
Basis:              [00.8.5] [01.14.6] [05.8.2] [R: https://bladesinthedark.com/progress-clocks]
```

```
### 05.7.7  Opposing a lasting effect (as an anchor)                [D]
Anchor:             yes. Intent verbs: "dispel", "break the ward", "undo it", "unpick", "counter",
                    "end the effect". Knobs: dc (default the effect's STORED effect DC; allowed delta:
                    a Precision snag when the opposer's branch differs from the effect's); attribute
                    (the opposer's casting attribute; allowed delta: by_method when the effect has a
                    physical anchor and the method is Force); reach_unit (default: 1 suppress for
                    rounds:3, 2 end, 3 end and learn the maker's signature, 4 end one more of the
                    same maker); targets (one effect; allowed delta: none). Covers: any attempt to end
                    something lasting that someone made: a ward, a curse, a summoning, an oath-bond,
                    a glamour, and by analogy a mundane lasting arrangement with a maker (a blockade,
                    a rumor campaign) when 11 gives it a stored DC. Does not cover: a condition with
                    its own cleanse list (00.9.1); a working as it is cast (ab.counterspell).
Basis:              [00.3.8 stored DCs] [05.7.7] [R5 MG-08]
```

```
### 05.6.7  Push (as an anchor)                                     [D]
Anchor:             yes. Intent verbs: "give it everything", "dig deep", "put my back into it", "make
                    it count", "careful: I can't afford to fail". Knobs: focus_cost (default 1; allowed
                    delta: none); reach_unit (the beat's own); stakes (the beat's own). Covers: any
                    wish to trade a personal reserve for a better result or a safer failure on a
                    trained beat. Does not cover: a bonus to the roll (levers only); a beat at a tag
                    where the actor has only the floor; resisted checks.
Basis:              [05.6.7] [01.7.3] [R3 #9]
```

### Edge cases

**Slots and holding**
- **A relic grants an ability the character already holds.** One instance per ability id (05.2.9): the
  item's ability stays dormant; the held one is used at its own rank with no relic surcharge.
- **A calling is suspended by the Fraying.** Its picks stay in their slots; ranks are computed with the
  lowered tier (05.3.9); oath-gated abilities are refused by `use_ability` with the reason. Nothing is
  re-slotted, and the slots do not free.
- **A tier lapses and the pick lapses with it** (04.8.2). The ability returns to the pool and its slot
  frees. If the character had begun a learning clock for it, the clock remains.
- **The shelf is full and a gift arrives.** The player names one of the nine to forget before the gift
  is granted; a declined gift is 08's and 11's to handle (the giver may take offense).
- **An equipped item is taken from the character.** Its bound ability unbinds at once; a Form it was
  running ends; its uses are remembered on the item, not the character.
- **Two abilities of one `mod_group` would be held through consolidation.** Consolidation keeps picks
  as they are (04.8.5); the engine does not evict. The exclusion applies to *new* grants, and the next
  season re-pick shows the pair to the player as a suggested swap.

**Activation**
- **The target becomes illegal between OFFER and commit.** The activation is refused and spends nothing
  (05.4.4).
- **A rider is declared on a beat that then needs no roll** (01.4: not uncertain). The rider applies as
  on a success; its Focus is spent.
- **A reaction and a trigger both answer one event.** 00.10.7's order: the target's `prevent` and
  `redirect` first; if the event is cancelled, later subscribers do not fire and keep their uses.
- **An ability's `applies_when` names a condition ch.06 has not yet defined precisely.** The reserved
  ids of T-00-15 are used as written; if 06 changes what a condition does, the ability's effect
  reference is unchanged and the new meaning flows through.
- **The player wants to use an ability "a little": less harm, a shorter push.** Any effect may be
  delivered at less than its listed magnitude by the player's choice; cost and use are unchanged.
- **An ability would apply a condition the target is immune to.** The rest of its effects apply; the
  packet says the condition did not take, so the narrator does not narrate it.
- **A passive's fiction clause is disputed.** The DM's flag stands for the beat and is logged; the
  player may cite a fact; if a fact exists, the next frame applies it. No retroactive change (01.8.5).

**Focus**
- **Focus reaches 0 from a drain during someone else's turn.** Spent applies at once: sustained
  workings end at that moment.
- **A Focus trigger fires while at maximum.** Nothing is gained and the per-scene use is still spent
  (the trigger fired). The generation counter is not advanced.
- **Two characters' effects would each restore the same character's Focus in one scene.** Both count
  against the recipient's cap of 3.
- **The vessel of a reserve is destroyed.** The banked points are lost. A stolen vessel keeps them for
  whoever holds the vessel and the license.
- **A long rest is interrupted.** Focus restores as a partial short rest; uses do not refresh; no
  re-slot; a reserve charge in progress is not resolved (it resolves at the next completed long rest).
- **An ability reduces a cost that a flare raised.** Order of 05.6.3: flares add first; reductions
  apply after, capped at −1 in total.

**Magic**
- **A caster is silenced or bound.** Arcane and divine workings need speech (and arcane a free hand):
  `use_ability` refuses on the limitation, with the redirect naming what would free them. Primal
  workings have no such need; passives are unaffected.
- **A spell is cast where canon marks magic inert.** G4 (trait.nature.magical, 01.17); no Focus spent.
- **A resisted spell meets a mindless target.** `trait.nature.mental` effects are G4 against it for that
  target only; other targets resolve.
- **A divine caster acts against the keeper's axes with a working.** The working resolves; 03 records
  the conduct evidence; 04's strain rises; regard fails only when the Fraying reaches stage 2 (05.7.4).
  No rule punishes the cast itself.
- **Two casters try to dispel each other's dispel, or to counter a counter.** A dispel is instant: there
  is nothing lasting left to oppose. A counter cannot itself be countered: it is a reaction, so its
  casting is a depth-1 event, and subscribers fire only on depth-0 events (INV-12).
- **A summoned or raised being's summoner is Spent, unconscious or dead.** A lasting summoning runs its
  duration; a sustained one ends. A servant with no one to command it does nothing (INV-11).
- **A rite needs a participant the PC does not have.** Hirelings and companions who hold the training
  count (16); the redirect names where such people are found (11's `institutions_matching`).
- **A rite is performed in a conflict.** Only a rite whose `time_per_tick` is in rounds can be advanced;
  none of the 24 authored rites is. The rite's clock holds while the fight runs and decays by the
  watch, not by the round.
- **The player invents a spell.** There is no spell creation. The answers, in order: a stretch of a held
  ability; an emulation; a rite designed by research (05.8.4); a thread to find a teacher or text of an
  ability the pool holds; and, for something the pool lacks, a note in the ruling ledger with
  `review_flag` so that the content team sees the hole (05.12.3).

**Reaching and adapting**
- *"I do something half-magical with my training, but I hold no spell for it."* → Small working if
  tool-equivalent; else stretch of the nearest held spell; else G3 with paths.
- *"I want to weaken my own ability to make it subtle."* → the Quiet flare; or deliver it at less than
  full magnitude.
- *"I use an ability on myself that targets a foe"* (Clutching Earth to anchor myself against a wind) →
  a stretch if the principle's operation and object still hold (the ground closes on what stands on it:
  yes), at the stretch price.
- *"I combine my two abilities into one move."* → one rider per beat; a Form already running plus a
  rider is legal; a composite if the pair has one; otherwise two beats.
- *"I pour all my Focus into one blow."* → one flare (two at master). The rest stays in the pool: Focus
  has no free-spend dial, by design (R1 M-24).
- *An adversary uses an ability from the pool.* Same record, same rules, the adversary's Focus is 09's
  to give; `adversary_only` entries are 09's own and never enter a pick or a learning clock.

## State touched

**State families written (owner per 00.6.3: abilities, slots and Focus are this chapter's).**
- `Character.slots.{calling, acquired, equipped}`: `HeldAbility` records (05.1.2): `grant`, `retire`
  (tool #28).
- `Character.shelf`; `Character.witnessed` (`set_fact` under `pc.witnessed.<ability id>`).
- `Character.focus.{current, max, state, reserve, generated_this_scene, breathers_since_short_rest,
  short_rests_today, restored_by_consumables_since_long_rest, overdraws_since_long_rest}`:
  `update_quantity`, with `focus.max` evaluated through the pass.
- Per being: `healings_since_long_rest` (a counter on the recipient).
- Uses per held ability (`uses.remaining`); `sustained`; `bound`.
- `effect_instance` records for running effects, each with its maker's stored effect DC.
- Licenses held: training licenses and their grade (`LicenseInstance`), `lic.focus.*`; competence
  entries with `source: <license id>` (00.3.6).
- Clocks created and owned (00.17.1 Q7): `clk.learn.<ability id>` (project; 6, 8 or 12), `clk.train`
  (project; 8), `clk.learn_rite` (project; 6), a rite's progress clock (4, 6, 8 or 12) and its strain
  clock (danger; 4), a rite-design research clock (project; 8 or 12).
- Facts: `pc.focus.spent`; `pc.keeper.<school>`; rite-in-progress facts; facts established by small
  workings and by `eff.write_fact` effects; `rit.custom.<n>` entries; ruling records for stretches.

**State read, through the owner's interface.** Calling tiers, specialties, the Fraying stage and pick
allowance (04); rest type and quality on the rest boundaries (07); Vitality for overdraw refusals and
`apply_harm(lethal: false)` (07); conditions and their definitions (06); range bands, flags, engagement
and reactions per round (06); place `resonance`, terrain tags and weather (10, 13); faction standing
with a keeper's faith (11); item tags `item.tool.implement` and relic flags (08); the scene log of
abilities used by others (09, 12).

**Tools used** (00.14.2): `use_ability` (#19, owned here), `frame_check`, `roll_check`, `read_result`,
`apply_costs`, `apply_effect`, `apply_harm`, `apply_condition` / `remove_condition`, `update_quantity`,
`evaluate`, `set_fact`, `create_clock` / `tick_clock`, `advance_time`, `roll_table`
(`tbl.05.rite_conditions`), `grant` / `revoke` / `retire`, `log_ruling` / `find_rulings`,
`record_evidence` (through 03's counters), `oracle` (the source present; rite-design specifics).

**Hooks subscribed** (00.10.2): by abilities in the data: `on_declare`, `on_degree`, `on_check_against`,
`on_attack_hit`, `on_hit_taken`, `on_harm_taken`, `on_defeat`, `on_move`, `on_condition_applied`,
`on_resource_depleted`, `on_boundary`, `on_fact_set`. By this chapter's engine rules:
`on_resource_depleted` (Focus → Spent), `on_focus_spent` (emitted), `on_clock_complete` (learning).

**Boundary handlers** (`data/boundaries.yaml owner-block 05`): the five reserved by 00 (`h.05.round_recharge`,
`h.05.conflict_recharge`, `h.05.scene_recharge`, `h.05.day_recharge`, `h.05.focus_recover`), defined in
05.4.6 and 05.6.9; four added: `h.05.rest_recharge` (rests, phase 3), `h.05.reslot` (`rest_long`, 3),
`h.05.reserve` (`rest_long`, 3), `h.05.provisional_abilities` (`reflection` and `season`, 8).

**Effect definitions added** (`data/effects.yaml owner-block 05`): `eff.05.spell_delivery`,
`eff.05.defense_reaction`, `eff.05.waive`, `eff.05.refresh_use`, `eff.05.counter_working`,
`eff.05.end_working` (DL-05-25).

**Visibility** (00.6.4): slots, held abilities with the active rank's literal text, uses, Focus, the
reserve, the shelf, known rites and running clocks of this chapter: **shown**. `witnessed`, learning
clocks, budgets and priority ranks: **available**. Effect DCs of others' effects: **sealed** until
identified (ab.spell_sight; 05.7.7).

**Runtime capabilities assumed** (00.14.1): RC-STORE (slots, uses, counters, effect instances),
RC-EVAL (the pass, hooks, regimes, depth, slot priority, spread resolution, composites), RC-SCHED (the
recharge and recovery handlers, rite time), RC-RNG (`tbl.05.rite_conditions`, checks), RC-DATA (the four
data files validated on load), RC-QUERY (tag ancestry for training licenses and pool gates), RC-LOG
(ruling records for stretches; the scene log of witnessed abilities), RC-RETRIEVE (an ability's card is
its data entry: retrieved by id when held abilities are in the situation).

## Interface requests

**To 00 (proposed amendments; this chapter works within 00 as written meanwhile).**
1. **T-00-9 / `boundaries.yaml`:** add `h.05.rest_recharge`, `h.05.reslot`, `h.05.reserve`,
   `h.05.provisional_abilities` (`data/boundaries.yaml owner-block 05`).
2. **`effects.yaml` owner-block 05:** six definitions (`data/effects.yaml owner-block 05`). Two stretch an
   operation's wording and should be confirmed: `eff.05.waive` uses op `prevent` to negate a named snag
   or provoked reaction (not a hit); `eff.05.end_working` uses op `remove_condition` to end a magical
   `effect_instance` that is not a condition.
3. **License kind for a universal license.** `lic.focus.push` is held by every character and is neither a
   basic verb (the list of fifteen is closed) nor training; it is written `kind: fact` with `universal:
   true`. Proposed: add `universal` to `substrate.yaml#license_kinds`.
4. **`Character` shape (00.6.2):** the `focus` fields and `shelf`, `witnessed` of 05.1.2;
   `HeldAbility`; a per-being `healings_since_long_rest`.
5. **Expression context:** `applies_when` in this chapter's data reads "this beat", "this Strike", "the
   target of the Strike", "your next beat against X": event-scoped references. Proposed: add `event`
   and `event.target` to the documented context keys.
6. **Hook observers.** `ab.counterspell` (on another's `on_declare`), `ab.riposte` (on the `on_degree`
   of an attack against the holder), `ab.set_spear` and `ab.feather_fall` (on another's `on_move`)
   subscribe as *other entities* to events that are not their own. 00.10.7's ordering already allows
   "other entities' effects"; a sentence in 00.10.2 saying a subscriber may filter on events targeting
   or near it would remove doubt.
7. **Glossary additions:** hold, pick (04's), partition, shelf, form (of an ability; *distinguish*
   `slot.body_form`), timing, rider, working, flare, push, Spent, overdraw, reserve, vessel, keeper,
   regard, miscast (Backlash / Silence / Debt), small working, rite, strain clock, spread tag, effect
   unit, allowance, training grade (trained / expert / master), technique cap, promotion.
8. **`focus` in rules text.** T-00-22 bans *focus* for an item; this chapter uses *implement*, *sign* and
   *vessel*. No change requested.

**To 01 (Resolution).** (a) `frame.gate.mode` values `stretch` and `emulate` are used exactly as 01.3.5
defines them; this chapter adds that a stretch is always a rolled beat and that grade changes the
prices (T-05-6). (b) The **push** (05.6.7) is a step effect declared at OFFER beside 01.7.3's trade;
`cost.drain` may take Focus when a push was used (01.13.3 already says so). (c) A spell's critical
failure is replaced by the miscast (05.7.5): 01.9.2 should name it as an alternate cost source. (d)
Small workings (05.7.6) use `verb.handle`'s card with the branch's attribute: the Handle card's
attribute list should admit "the license's attribute".

**To 02 (Character).** Base Focus 3–5 (reference 4); at least one origin per magic branch granting that
branch's first training license (as 04 also asks), each with its `requires` satisfied by the origin
(literacy and a text; a keeper; a place); origins may grant `lic.focus.reserve`; origin training grants
competence of at most +2 at the tag. No origin grants a held ability into the calling partition; an
origin may grant **one** ability into the acquired partition at rank 1 (a gift, `source.kind: gift`).

**To 03 (Tags and evidence).** (a) `cnt.focus` should also count Focus spent on a **push**, at the
frame's primary deed tag. (b) Every ability's first tag is a deed tag at level 2 or 3 (done, script-
checked). (c) `dictates_choice: true` is set on the 13 abilities that apply charm, fear, compulsion or
a restriction on another's choices (done). (d) An emulation's evidence lands on the emulated technique's
first tag; a small working's on the school's level-2 tag. (e) Abilities used through relics write no
evidence (00.11.5; 04's item 11).

**To 04 (Recognition and growth). The requests of 04's block are met as follows.**
1. Calling partition **12**, acquired **4**: adopted (05.2.1).
2. Every `slot_class: calling` ability has its first tag at deed level 2 or 3, `min_tier` 1–5,
   `mod_group`, and 1–3 `ranks` as complete restatements; `requires_conduct` and `conduct_pole` on the
   57 oath-gated ones; `replaces` is supported and unused, by decision (DL-05-34): growth inside an
   ability is its ranks, and `replaces` is the content-lifecycle link 05.12.3 now enforces by script.
3. Coverage: every one of the 81 level-2 deed tags has at least two abilities, one at `min_tier` 1;
   every branch has at least 14 with two or more at each `min_tier` (T-05-12); every conduct axis has
   three at each pole a calling uses (`min_tier` 1, 3, 5) [revision: I-007].
4. Rank rule kept, with one addition **requested of 04**: for a pick carried through a consolidation or
   fork, the tier read is the higher of the new calling's tier and the specialty's `tier_reached`
   (05.3.9), and `T_high` for the Focus maximum reads the same (05.6.1). Without it a consolidation to a
   lower tier would lower ranks and the pool, against 04.8.5's "nothing is lost on the day".
5. 81 training licenses with grades `trained < expert < master` and `recognition` among the paths.
6. The nine family Focus triggers are **confirmed unchanged**; this chapter adds the generation cap of 3
   per scene (05.6.10).
7. Every license carries `stretch` and `emulate` (explicit null where none). Sure Hand and the Open Art
   read `frame.gate.mode` and the training license's `emulate` block.
8. The 27 absorbed powers are mirrored by reference with `slot_class: acquired`; re-slotting at
   `rest_long` is 05.2.7; they use ch.04's library and not the shelf.
9. `composites.04.yaml` merges as owner-block 04; this chapter's 22 composites use the other three key
   kinds and do not touch deed-branch pairs.
10. **New requests of 04:** (a) the pick gate should require `conduct_pole` to equal the calling's
    `pole` (vows and dark callings share an axis in `pool_gate.conduct`, and the 30 positive and 27
    negative abilities must not cross); (b) **promotion** (05.8.6): an ability held in the acquired
    partition or on the shelf should be eligible for a pick and ranked first; (c) negative-pole
    coverage is now three per axis (`min_tier` 1, 3 and 5), so a dark calling's tier-5 pick has its
    candidate; and the Monk, an oath-bearing calling with `conduct.restraint` in its pool gate, carries
    `pole: positive` so the gate admits the restraint abilities (`05-ladder-check.py`) [revision: I-007].

**To 06 (Conflict).** (a) Define the reserved conditions as this chapter's data uses them: `exposed`
gives attackers a lever (the Focus simulation and Quarry's Mark assume a Precision lever); `dazed`,
`slowed`, `weakened`, `off_balance` as T-00-15. (b) What action each verb costs, so that `timing: beat`
abilities inherit it; reactions per round, and whether `eff.reaction_grant` is allowed (it is unused by
this pool). (c) Engagement links and `flag.lined_up`, which the `burst` and `pierce` spread tags select
on; `conflict.yaml#multi_target` should adopt the five spread tags and their caps (05.10.4). (d) A
"bloodied" state expression (04 also asks). (e) Stances end at `conflict_end` unless their text says
scene; the stance slot and the aura slot are separate. (f) The companion **command action**, which
summoned servants, raised dead and automatons use (INV-11). (g) Sizes ("one size step larger") for
`ab.clinch_throw` and `ab.pinning_cast`.

**To 07 (Harm, recovery, death).** (a) Rest `quality` (`full | partial | interrupted`) on the three rest
boundaries, and that `h.07.rest_recovery` runs before `h.05.focus_recover`. (b) `apply_harm(lethal:
false, no_reduction: true)` for overdraw and Backlash. (c) The healing cap (05.7.8) counts every
Vitality-restoring ability, rite and item effect: 07's natural recovery and treatment by rest are
outside it; 07 should say whether its own *treatment* activity counts (this chapter assumes
`ab.field_surgeon` does). (d) What *stabilized* means for `ab.breath_of_life`; wounds and marks are
never removed by this chapter's abilities except through `rit.vigil_of_healing`'s one recovery step.
(e) `cond.exhausted` (three stacks) is used by overdraw: 07/06 should confirm its per-stack effect.
(f) Staged afflictions as the carrier for `rit.lay_curse` and `ab.slow_draught`.

**To 08 (Items).** (a) An item carries at most one item-bound active ability, as a full ability record
with a stated rank; item passives use no slot. (b) Relic licenses: `feeds_evidence: false`; this
chapter adds the +1 Focus relic surcharge (05.6.3). (c) Priority ranks 15–19 for intrinsic properties
and 20–24 for applied consumables (05.10.3). (d) Focus-restoring consumables use `eff.restore`; the cap
of 4 per long rest is this chapter's. (e) Implements (`item.tool.implement`): a keeper's sign and a
reserve's vessel are implements; an item fact "kept for a season" or "made by the holder". (f) Texts
that teach (`teaches: <ab.* | rit.* | lic.training.*>`), components by price band, healer's and
alchemist's kits, prepared firepots and poison doses. (g) `gen.gift` with `output_kind: ability` grants
into the acquired partition. (h) What `damaged` and `broken` mean (`ab.sunder`, `ab.field_patch`).

**To 09 (Adversaries).** (a) Adversaries may hold pool abilities by id (and `adversary_only` ones of
09's own, which this pool never offers); when one is used in the PC's perception the scene log records
it (the `witnessed` fact). (b) Tells are what `ab.read_the_field` and `ab.know_the_beast` reveal. (c)
Focus-emptying powers only at T4–T5 with a tell (05.6.13). (d) Each adversary's effect DC is stored on
its lasting effects.

**To 10 (Exploration) and 13 (Starter setting).** (a) Place `resonance: [tag]`, and `desecrated`,
`consecrated` and dead-ground facts. (b) The weather record as a fact the source-present test reads.
(c) The eight canon items of 05.7.10. (d) Keepers with axes, signs and faiths. (e) Where teachers and
texts are; which rites are known in the region. (f) 13 may tighten the `requires` of magic training.

**To 11 (Living world).** Standing with a keeper's faith (05.7.4); settlement tiers used as DCs by
`ab.word_on_the_street`, `ab.web_of_whispers`, `ab.black_market`; morale and social clocks ticked by
abilities; threads created by a rite's "first you must" condition and by spirit bargains.

**To 12 (DM procedures).** (a) An ability's rule card is its data entry, loaded when the ability is held
and its situation tags match; the rank's literal text is quoted in the narration packet (05.3.6). (b)
`tbl.05.rite_conditions` in `data/rituals.yaml` is rolled with `roll_table`. (c) The OFFER line for an
activation shows Focus, uses, flare and overdraw prices. (d) The seven anchors of this chapter for
`anchors.yaml`.

**To 14 (Player's guide).** Codex views: **Abilities** (by partition; the active rank's literal text;
cost; uses left; timing; flares; the stretch price; provisional flag), **Focus** (current, maximum and
its three terms, Spent, the reserve, the rest table, the two caps), **Shelf and learning** (clocks),
**Rites known**, **Training** (licenses and grades). The guide should say: every ability does exactly
what its text says; you may always try to stretch it; Focus comes back with rest, and an hour is worth
half your pool.

**To 15 (Social, investigation, downtime).** The training activity (ticks `clk.train` and `clk.learn`
at the rates of 05.8.5 and 05.9.4 and writes `cnt.training`); a research activity for rite design
(delivered reach per week); commissioning a rite or a text; Retrain (04) swaps a pick.

**To 16 (Companions).** Familiars, bonded beasts, summoned servants, raised dead and automatons are
companions of the stated threat band: no turn of their own, commanded by 06's action; `ab.beast_at_heel`
modifies that action.

## Open empirical questions

Each ships a concrete default and names the test that would settle it.

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-05-1 | Is 2 EU per Focus point the right exchange rate, and is the ±2 band tight enough that same-tier abilities feel comparable? | 05.11.2 | **T-05-BUDGET**: 200 simulated fights per ability pair at each tier with ch.06's real action economy; target: no tier-1 ability raises win rate over another by more than 10 points at equal Focus spent; re-price the outliers' effect units |
| OEQ-05-2 | Does the recovery ladder (+1 / half / full, two breathers, two short rests) give 3–5 meaningful fights a day without making the hour free? | 05.6.9; the simulation shows 5 fights sustained with two short rests and exhaustion by fight 4 without | **T-05-DAY**: 3 played ventures; log Focus at each fight's start and the rests chosen; target: a short rest is taken in 40–70% of opportunities (neither automatic nor ignored) |
| OEQ-05-3 | Does the AI apply the SAME OPERATION flag for stretches consistently? | 05.5.2, tie-break false, precedent ledger | **T-05-STRETCH**: 40 proposed stretches (20 designed inside, 20 outside) × 3 independent DM runs; target ≥ 85% agreement with the designed answer, and no outside case allowed in more than 1 of 3 runs |
| OEQ-05-4 | Do the three miscast shapes feel different in play, and is S4 Backlash (8 harm) too swingy for a 12-Vitality caster? | 05.7.5 | **T-05-MISCAST**: simulate 1,000 castings per branch at each stakes rung; measure how often a miscast changes a fight's outcome; target ≤ 5% of fights decided by a miscast at Risky stakes |
| OEQ-05-5 | Is the generation cap of 3 per scene ever binding, and do the nine family triggers fire at comparable rates? | 05.6.10 | **T-05-TRIGGER**: per-family trigger counts over 10 sessions of play; target each family 0.3–0.8 fires per scene at tier 2–3; retune the outliers' conditions (04 owns the data) |
| OEQ-05-6 | Is a pool of 266 enough variety across a long campaign, and are any abilities never picked (dead) or always picked (mandatory)? | 05.11.6; 05.12.3 | **T-05-PICKRATE**: pick logs across 30 characters; an ability shown ≥ 10 times and picked in < 5% or > 60% of showings is flagged for re-pricing, folding or retirement |
| OEQ-05-7 | Does the narrator keep to the literal rank text (no invented weaknesses or extra effects)? | 05.3.6, 05.3.7; verbatim text in the packet | **T-05-LITERAL**: 100 activations audited with `check_claims`; target ≤ 2% narrated effects not in the packet (the probe's baseline was 1 in 6) |
| OEQ-05-8 | Is one-link composition enough for the designed synergies of this pool? | 05.10.5 | **T-00-DEPTH** (00's test) run on this data: of the 22 composites and every rider-plus-trigger pair, count intended synergies that need a second link; target < 5% |
| OEQ-05-9 | Are learning times right (two weeks with a teacher for a tier-1 technique; six emulations without)? | 05.8.5 | **T-05-LEARN**: over 10 sessions, count learning clocks started, completed and abandoned; target ≥ 50% of started clocks completed within a season of play |
| OEQ-05-10 | Does the healing cap of 2 per long rest hold up with ch.07's real recovery numbers? | 05.7.8 | **T-05-HEAL**: simulate a venture day with a healer at tiers 1, 3, 5 using 07's numbers; target: healing extends a day by 1–2 fights, never indefinitely |
