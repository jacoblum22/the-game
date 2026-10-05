# 10 — Exploration, Travel, and Sites

> This chapter governs everything the player character does between the safety of a haven and the
> moment a fight, a conversation or a downtime week begins: the place graph the world is made of
> (places, routes, areas, discovery), the venture that begins when the character leaves safety and
> ends when it returns, travel by watches (routes, pace, the march allowance, forced marches, mounts,
> vehicles and vessels), navigation and getting lost, journey roles, supply and want, foraging and
> hunting, light and darkness, weather, environmental and magical hazards, sites explored area by
> area with a progress clock racing a danger clock, traps, and the catalog of exploration activities
> with their durations. One mechanism ties it together: **one engine-rolled time-tick die per watch
> of travel and per check interval in a site, on which every face means something** (an encounter, an
> omen, a local event, a depletion, a weather or site shift, a discovery, an opportunity, or a lull of
> good going), keyed to the place's danger rating, under the rule that **a threat never arrives
> unannounced: its omen comes first**. The shape answers the two failures this pillar invites in an AI
> Dungeon Master — forgetting what it described and pacing the world by mood — by making every
> described element a recorded place or feature (write-on-mention), every random happening an engine
> roll on a place's own table, and every passage of time a run of registered handlers. The player may
> go anywhere and try anything; the world answers from its own data.

**Reading this chapter.** Rules 10.1–10.15 are the binding text; each is a self-contained card
(SG-26). Procedures PR-10-1…PR-10-9 are the algorithms. Tables T-10-1…T-10-24 summarize the data in
`data/travel.yaml`, `data/weather.yaml`, `data/hazards.yaml`, `data/sites.yaml` and `data/traps.yaml`,
which are canonical for every number and id (00.1.4 line 5). Worked examples WE-10-1…WE-10-6 follow
**Wren** (00's example character: Might +1, Agility +3, Endurance +1, Wits +2, Intellect 0, Presence 0,
Resolve −1; competence `deed` +1, `deed.wilds.tracking` +2, `deed.martial.archery` +2; Vitality 13
after 02's Bent; Focus 4; fate 1; capacity 12). Simulation scripts are in the scratchpad
(`sim10_travel.py`, `sim10_site2.py`, `sim10_nav.py`; copies and results in `_process/simulation/10-exploration-sim.md`) and their results are
reported where they fix a number.

---

## Design intent

**Goals served.** Goal 1 — *the player feels free to try any creative idea* — is served by an open
place graph with no invisible walls (any place may be set out for; any route may be left; the
unlicensed always have a priced way forward: a road, a river, a landmark, more time, or going blind
knowingly), by a closed catalog of exploration activities that are anchors any novel method can be
reached to (10.15), and by sites whose areas are generated from small theme and domain cards so
there is always another room. Goal 2 — *the AI responds and reacts correctly* — is served by moving
every random happening into engine rolls on place-owned tables, every elapsed hour into registered
handlers (00.7.4), every described exit, feature, landmark and sign into state the moment it is
mentioned (00.6.6), and every danger behind an omen the engine selects (INV-14) [BRIEF §3; R4 §9 10].

**The decisive findings.**
1. *Natural-environment adjudication is where every model family failed* in the CoC-Seduce study (mean
   error 9.76%): environmental harm must be explicit tables, never improvised [R4 §9 10 item 1;
   R: https://arxiv.org/abs/2607.02802]. Hence `data/hazards.yaml` and `data/weather.yaml` are
   complete enough that the DM never rates the cold, the fall or the flood by feel.
2. *Geography is the longest-gap contradiction* in long narratives (31% of story length between plant
   and contradiction): routes, distances, travel times and landmarks are stored data, never
   remembered prose [R1 §10; R: research_notes/Long horizon LLM narrative benchmarks].
3. *Every scale needs a resource that ticks at its boundary*, or that scale feels hollow (5e's
   "nothing happens during travel"): the watch spends supply and light and rolls the time-tick die;
   the interval spends light and rolls the site check; the day spends supply and rolls the weather
   [R5 §3.2 findings 1, 3].
4. *The overloaded encounter die* (Necropraxis's Hazard System; the Alexandrian hexcrawl's d12 with a
   keyed-location face) gives every tick of time a meaning, so no roll is null and the world never
   flatlines [R6 §B.2 B-14, B-R5; R: https://necropraxis.com/2014/02/03/overloading-the-encounter-die/; R: https://necropraxis.com/2014/12/23/hazard-system-v0-2/].
5. *Omens before threats* reconciles hidden mechanics with telegraphed lethality: the Mausritter
   omen-on-a-near-miss, Dungeon World's grim portents and Blades' clocks all say the same thing — the
   world shows its hand before it strikes [R5 P-36, P-17, P-19; R6 B-R5; BRIEF §4].
6. *Ironsworn: Delve's site procedure* (a site = theme × domain; areas as progress; approach-specific
   risk; dangers and opportunities from the two cards) is the strongest no-map dungeon crawl for a
   text-only game, and its theme × domain pair is precisely constitution P5's pool gate for what lives
   and lies there [R5 P-28; R2 #13; C:P5].
7. *Time = resolved actions* (Torchbearer's turn per test) is the most AI-friendly site clock; real-time
   light is meaningless in asynchronous text (R5 X-05), so light burns by interval [R5 P-13, §3.2 #3].
8. *Event-paced travel* (The One Ring's journeys) produces fewer, more meaningful events than per-day
   tables; *quarter-day activities* (Forbidden Lands) make a solo traveler's choice between walking,
   foraging, watching and sleeping the survival tension itself [R5 P-31, P-32].

**What this chapter deliberately avoids.**
- *Hex geometry as canon.* The world is a graph of places joined by routes (10.1.1). A region drawn as
  hexes is authored as a graph whose nodes are hexes; nothing in the rules needs coordinates.
- *Encounters built to the character.* Encounters belong to places (09.8.2): a region fields what lives
  there, and the advisory tells the truth about what was drawn.
- *Random encounters with no warning.* A hostile encounter always has an omen first (10.9.5).
- *Death traps.* A trap that can wound gravely shows a telltale before it can fire (10.14.3), and a trap
  can kill only through chapter 07's two keys.
- *Mileage arithmetic by the AI.* Routes store their length in watches; the engine converts pace.
- *A diegetic System.* Danger ratings, clocks and faces are out-of-fiction state; the fiction shows
  tracks, smoke, a hush in the birds.
- *Cutting richness.* Player-facing complexity is not a constraint (DL-00-01); the substrate here is
  dense on purpose, because every activity and hazard is a reach-and-adapt anchor (C:P3 sixth pass).

**Runtime capabilities assumed.** RC-RNG (every check, weather roll, veer, table and draw), RC-STORE
(places, routes, sites, areas, pending threats, supply, light), RC-SEAL (lost status, pending threats,
undiscovered places, trap positions), RC-SCHED (handlers on `interval`, `watch`, `day`, `season`,
`venture_*`, `scene_start`, `beat_end`), RC-LOG, RC-DATA (the five data files), RC-QUERY (terrain tag
ancestry, archetype gates), RC-EVAL (pace, light and supply quantities).

---

## Rules

Rule IDs are `10.S.R`. Kinds per 00.2.2. Rules that carry a `[J:*]` decision use the 00.2.5 template.

### 10.1 The place graph

**10.1.1 The world is a graph of places.** `[D]` Every location the character can be in is a **place**
(entity kind `place`, 00.6.2) and every way between two places is a **route link** on the place it
leaves from. The graph is canonical; descriptions follow it. A place's **place kind** (`place_kind`,
closed list, T-10-1) fixes what rules load there:

| `place_kind` | True only when it is… | Holds | Mode on entry (T-12-3) |
|---|---|---|---|
| `region` | a named stretch of country with one home band and one danger rating (the Marches, the Fenmoor) | areas | — |
| `area` | a stretch of country one can cross in about a day or less, with one terrain (a hex, a valley, a wood) | routes, landmarks, sites, settlements | `travel` while moving |
| `settlement` | a place where people live (village, town, hold, camp) | buildings, districts | `free` |
| `site` | a place explored area by area: a ruin, a cave, a barrow, a lair (10.13) | site areas | `site` |
| `site_area` | one area inside a site, made when explored (10.13.6) | features, exits | `site` |
| `landmark` | a fixed, visible thing in an area used to find the way (a standing stone, a peak, a ford) | — | — |
| `building` | a building or district within a settlement | rooms | `free`, or `site` for a room-by-room search |

`parent` (00.6.2) nests them: region → area → site → site_area, and settlement → building. A place
belongs to exactly one parent; an area's region gives it its home band and danger rating unless the area
overrides them.

**10.1.2 The place record.** `[D]` Chapter 10 extends 00.6.2's `Place` with these fields (all data; 13
authors them for the starter region; generated places get them from the generator that made them):

```yaml
Place (extends 00.6.2 Place):
  place_kind: enum            # 10.1.1
  band: int|null              # home band 1..5 (region, area, site); tier cap for place-gated loot (08.3.5)
  danger: enum|null           # safe | settled | wild | perilous | deadly   (10.9.2)
  safe: bool                  # true = a haven: ventures end here; no time-tick check (10.2.3)
  rest_site: enum|null        # haven | camp | rough   (07.8.2 reads it; null = ask 07.8.2's rung)
  terrain: [tag]              # terrain.* tags (00.6.2); first is primary
  climate: enum|null          # temperate | northern | highland | arid | coastal  (weather zone, 10.11.2)
  nav_tier: enum|null         # easy | moderate | hard | very_hard  (10.4.3; areas)
  forage_tier: enum|null      # by terrain and season unless set (T-10-12)
  game_tier: enum|null        # hunting (T-10-12)
  openness: enum              # open | broken | closed   (encounter distance, landmark visibility, T-10-15)
  landmarks: [place_id]       # visible landmarks (10.4.4)
  water_source: bool|null     # a spring, river or well a traveler can drink from (10.6.2)
  grazing: bool|null          # mounts may graze here in season (10.8.3)
  encounter_table: tbl_id     # 13's regional table, else the generic terrain table (10.10.1)
  hazards: [{hazard_id, where, active_when}]   # standing hazards of the place (10.12)
  resonance: [tag]            # deed keys, branches or conduct axes (04 V11; 05.6.9)
  settlement_scope: place_id|null   # the nearest settlement ancestor or patron settlement (03.10 scope)
  known: bool                 # the PC has heard of it (rumor, map, story)
  discovered: bool            # the PC has been there or perceived it (00.6.2); 10.1.5
  site: SiteRecord|null       # 10.13.3
  state_log: [{at, change}]   # persistent changes made by play (10.13.12)
```

Facts a place may carry, read by other chapters: `desecrated`, `consecrated`, `dead_ground` (05.7.2; dead
ground is the fact that makes primal workings G4 there), `haunted` (a dread source, 07.11.2),
`weather.today` and `weather.tomorrow` (10.11; 05.7.3 reads the first), `light` (10.7.2), `roused` (a
site, 10.13.9), and the starter region's two setting facts `hushed` and `true_bell` (13.2; read only through
the region's hazards and the Waking rule) [integration: IR ch.13]. Each is written with `set_fact` and never
implied by narration alone.

**10.1.3 The route link.** `[D]` A link (00.6.2: `{to, route, travel_watches}`) carries:

```yaml
RouteLink:
  to: place_id
  route: str                  # route id, shared by both directions ("rt.salt_road.3")
  route_kind: enum            # road | track | river | water | trackless | underway | secret | passage
  travel_watches: int         # watches at NORMAL walking pace, fair weather, unburdened (10.3.2)
  terrain: [tag]              # what it crosses (may differ from both ends)
  current: enum|null          # downstream | upstream | none   (water routes)
  known: bool                 # the PC knows this way exists
  danger: enum|null           # overrides the area's rating along it (a patrolled road)
  hazards: [{hazard_id, where}]   # fixed hazards on the way (a ford, a scree slope)
  vehicle_ok: [str]           # bi.* conveyances that can use it (08.10.3)
```

The route kinds mean: **road** (kept, never lost on it, vehicles); **track** (a trail; never lost in fair
visibility); **river** and **water** (by boat, or followed on foot along a bank: never lost); **trackless**
(across country toward a known destination: navigation, 10.4); **underway** (a known underground
passage: never lost with light; navigation without it); **secret** (exists sealed until found by a search
or a clue; `known: false` until then); **passage** (within a site or building; 1 interval to cross).

**10.1.4 Write-on-mention for places.** `[J:flag]` + `[D]`

```
### 10.1.4  Write a place on mention                               [J:flag] [D]
Trigger [T]:        narration (or a table result) introduces a way, a place, a landmark, an exit,
                    a feature of terrain or a sign in a place
Loads in:           situation.travel.*, situation.exploration.*
License check:      none (state discipline)
Decisions (J):      1. ADDRESSABLE [J:flag] (00.6.6): "Could the player cite this later as a route,
                       a destination, a landmark, an obstacle, a hazard, cover, a place to rest or
                       a clue?" True only when it is concrete and locatable ("a deer track down to
                       the stream", "a cairn on the ridge", "a door on the left"); false for pure
                       atmosphere ("mist in the hollows", "the smell of pine"). Uncertain -> true.
Computation [D]:    true -> create_entity(place | object) or a route link with the fields the
                    narration implies; every unimplied field stays undetermined and is settled by
                    the Oracle or the place's tables when first needed (00.6.6). An exit named in a
                    site area is a link with route_kind passage. A "way down to the river" is a
                    route link with route_kind track and travel_watches from T-10-3 if the
                    narration gave no length.
Stakes:             none
State writes:       place or link entities; known: true; discovered per 10.1.5
Narration may not imply: a route, exit or place that has no record after this turn; a length, a
                    danger or a destination the record does not hold
Worst case (J):     an atmospheric detail is recorded needlessly (harmless); a usable one is not, and
                    the claim check (12.3) catches it at the scene end (class iv)
Examples:           inside: "a fallen oak spans the gully" -> landmark + a track link across the
                    gully. inside: "the corridor runs on into the dark" -> a passage link to an
                    undetermined site area. outside: "the wind smells of snow" -> atmosphere; but
                    the weather record already holds snow tomorrow, so nothing new is written.
                    non-example: the player says "there must be a pass through these hills" ->
                    an assertion; it is an Oracle question (Likely in hills) before any link exists.
Anchor:             no
Basis:              [00.6.6] [R1 §10 (geography is long-gap state)] [R4 SG-13] [DL-10-01]
```

**10.1.5 Known, discovered, and the discovery fact.** `[D]` A place is **known** when the PC has a fact
about it (a rumor, a map, a story, an NPC's directions) and **discovered** when the PC has been there or
perceived it directly. Discovery is written `set_fact(loc.<id>, discovered, true)` with:
- `frame_id` = the frame whose delivered result found it (a navigation reach 4, a scout's beat, a search,
  an Explore onward, a vantage Observe), when a frame found it — this is the event 03's `cnt.discovery`
  counts (03.9: "written as the delivered result of the actor's frame");
- `frame_id: null` when the PC simply arrived by a known route or by a table result (the discovery face,
  10.9.4), which records the place but is not evidence: wandering into a place is not finding it.
An undiscovered place is sealed (00.6.4) with the gate "the PC arrives, or perceives it". Rumored
places (`known: true, discovered: false`) appear in the codex's map view by name only, with the truth of
the rumor still sealed (11).

**10.1.6 The settlement scope.** `[D]` Every area and site carries `settlement_scope`: the place id of the
settlement whose people would hear of what is done there (the nearest settlement by route watches, or the
one 13 names as the area's market). Chapter 03's witness scopes (03.10) and chapter 11's reputation read
it. A settlement's own scope is itself. Areas with no settlement within 8 travel watches carry `null`:
deeds done there carry only to witnesses' own scopes.

**10.1.7 Places of power.** `[D]` `resonance: [tag]` on a place names the deed keys, branches or conduct
axes it answers (04's V11 *The Place Answers*; 05.6.9's resonant rest: +1 Focus on a breather or short
rest when a held calling or ability matches). Resonance is data (13) or a written result of a rite
(`rit.consecrate_ground`, 05). `consecrated`, `desecrated` and `dead_ground` are facts with sources;
T-10-24 (`data/hazards.yaml#zones`) lists the magical-zone hazards that go with them (a desecrated
place's dread, dead ground's silence of primal workings).

**10.1.8 Generated places.** `[D]` When play reaches a place no data holds (the player strikes out across
country 13 did not author; a site's new area), the place is generated, never imagined: an area takes its
region's band, danger and climate, a terrain from the region's terrain list by `roll_table`, and its
`nav_tier`, `forage_tier`, `openness` from that terrain's defaults (T-10-12); a site takes a theme and a
domain from the region's site tables (10.13.2); a site area takes its feature from the domain table
(10.13.6). Every generated place is written before it is narrated (PR-10-1 step 2). The DM chooses names
and words, never fields.

### 10.2 Time, modes, ventures and safety

**10.2.1 The modes of this chapter.** `[D]` Three of 00.7.3's time modes are this chapter's to run:
- **`travel`**: each **travel activity is one watch** (00.7.3). The PC spends every watch of a journey day
  on one activity (T-10-6: travel, camp, sleep, forage, hunt, scout, rest, keep watch, map, other).
- **`site`**: each **significant beat is one interval** (00.7.3; `h.10.site_time`, 10.13.5); a beat is
  significant when it resolves a check or performs an activity listed in T-10-20 with a duration; looking
  around casually, talking and free activities take no interval.
- **`free`**, outside settlements, for scenes at one spot in the wild (a parley at a ford, a camp
  conversation): activities take their listed durations (T-10-20).
Transitions follow 12's T-12-3: departing along a route link → `travel`; entering a place whose
`place_kind` is `site` or `site_area`, or beginning a room-by-room search of a building → `site`;
arriving at a settlement → `free`; `conflict_start` → `conflict` and back at `conflict_end`.

**10.2.2 Venture start and end.** `[T]` + `[D]` A **venture** (00.18) runs from leaving safety to returning.
- `venture_start` is marked when the PC moves from a place with `safe: true` onto a route link whose
  destination is not safe, or begins a travel watch outside any safe place.
- `venture_end` is marked when the PC enters a place with `safe: true`, or when chapter 07 records the PC
  captured and carried to a captor's place (the venture ends in captivity; the next is begun from there).
- Handler `h.10.venture` (`venture_start`/`venture_end`, phase 9) writes the **venture record**
  `{id, started_at, from, route_plan, supply_at_start, light_at_start, places_discovered: [ids],
  sites_entered: [ids], encounters: [ids], hazards_met: [ids], ended_at, to, days}` (the start fields at
  start; the rest appended through play; closed at end). Chapter 11's `h.11.reckoning` and 12's
  `h.12.venture_bookkeeping` read it on `venture_end` (00.7.6 runs `venture_end` after rests and
  reflection).
- While a venture is open, the fact `pc.on_venture = true` holds: 08's lifestyle charge is replaced by
  supply (`economy.yaml#lifestyle_rules`), and 07's rest site is never `haven` unless the place is one.

**10.2.3 Safety.** `[D]` A place with `safe: true` is a **haven** for this chapter: no time-tick check
runs there (07's request: "no encounter check in a haven"), its `rest_site` is `haven`, and ventures end
there. Safety is a property of the place, written by data (13: the base town, a friendly hold, a
guarded shrine) or by play (11: a holding the PC owns and garrisons; a village that grants the PC
hospitality writes `safe: true` while standing is Friendly or better). A safe place loses safety only by
a written world change (a faction takes it; a situation's default timeline burns it, 11), never by
narration. Danger may still enter a haven through chapter 11 (a World Turn event, a bang), chapter 12's
pushes, or a clock — never through this chapter's die.

**10.2.4 The West Marches shape.** `[N]` The starter region (13) is laid out as a haven at the center and
**concentric danger rings** (R6 B-15, B-R7): the farther from the base, the higher an area's home band and
danger rating, so distance is the difficulty dial in a game with no character levels (C:P2). This chapter
gives the dial its meaning: band (how strong what lives there is, 09.8.2) and danger rating (how often it
comes, 10.9.2) are separate fields, and both are shown to the player before a journey (10.3.4) as words,
never numbers. T-10-2 is the reference ring layout 13 should start from.

**T-10-2 Reference danger rings** (`data/travel.yaml#rings`; 13 may alter any ring with a DL entry).

| Ring | Typical distance from the haven | Home band | Danger rating | In words to the player |
|---|---|---|---|---|
| 0 | the haven and its fields | — | safe | "safe under the walls" |
| 1 | up to 1 day | 1 | settled | "farm country; trouble is rare and small" |
| 2 | 1–3 days | 1–2 | wild | "the borderland: wild, but folk pass through" |
| 3 | 3–6 days | 2–3 | wild or perilous | "the deep wilds: dangerous things live here" |
| 4 | 6–10 days | 3–4 | perilous | "the old lands: only the strong travel here" |
| 5 | beyond | 4–5 | deadly | "the far reaches: legends live here, and so do the things that killed them" |

**10.2.5 What runs while time passes here.** `[D]` This chapter's handlers (T-10-23) run on these
boundaries and never anywhere else (00.7.4): `h.10.site_time` (`beat_end`, 9), `h.10.light`
(`interval`, 4), `h.10.site_exposure` (`interval`, 2), `h.10.site_check` (`interval`, 7),
`h.10.travel_progress` (`watch`, 4), `h.10.wayfinding` (`watch`, 4, after travel progress by id order),
`h.10.watch_exposure` (`watch`, 2), `h.10.watch_check` (`watch`, 7), `h.10.supply` (`day`, 4),
`h.10.weather` (`day`, 7), `h.10.site_recovery` (`day`, 6), `h.10.day_reset` (`day`, 9), `h.10.site_regrowth` (`week`, 6),
`h.10.weather_regime` (`season`, 6), `h.10.scene_frame` (`scene_start` and `mode_change`, 7), `h.10.venture`
(`venture_start`, `venture_end`, 9). Skipping time runs every one of them for every boundary crossed
(00.7.7): a three-day journey "skipped" is twelve watch checks, three supply days and three weather rolls,
and its narration comes only from the returned list (12.4.6).

### 10.3 Journeys: routes, pace, and the travel watch

**10.3.1 A journey is a plan over the graph.** `[D]` A **journey** is an ordered list of **legs**, each one
route link from one place to the next, ending at a destination the player names (a place id, or "the
standing stones the hermit spoke of" — a known place). The engine finds the legs (the path through
known links with the fewest watches; the player may name a different path); a destination with no known
path is reached by a **trackless** leg across the area toward it (10.4). The plan is a record
`{journey_id, legs, pace, schedule, roles, started_at, progress_points}` written at departure.

**10.3.2 Length and pace.** `[D]` A route's length is its `travel_watches` (W): watches at **normal**
walking pace in fair weather, unburdened, with terrain already folded in by the author (13 writes "3" for
a day and a half over the moor). The engine converts it to **progress points**: a leg needs **6 × W**
points, and each travel watch earns points by the party's **effective pace** on the pace ladder
(`travel.yaml#pace`):

| Pace rung | Points per travel watch | Who moves at it |
|---|---|---|
| crawl | 2 | wading deep snow; groping in the dark; the floor of every slowed party |
| slow | 4 | walkers going carefully, quietly or mapping |
| normal | 6 | walkers; walk-pace mounts (donkey, pony, mule, draft horse); carts and wagons on roads |
| fast | 8 | walkers hurrying |
| ride | 9 | riders on ride-pace mounts (riding horse, courser, destrier); a carriage on a road |
| hard_ride | 12 | riders pressing their mounts |

**The party's base pace** is the slowest member's: a rider escorting a walker walks. **Chosen pace**: the
player picks slow, normal or fast; for a party all on ride-pace mounts (or in a carriage) these mean
normal, ride and hard_ride. **Steps** then move the rung down (never up), clamped at crawl:
1. **burdened** (08.9.2: load above capacity) — one step (a mount's own load against its carry capacity
   counts for the mount); **overloaded** — no travel at all (08.9.2);
2. **weather** off roads (`weather.yaml#states[].pace_steps`: rain 0, storm 1, snow 1, blizzard 2; deep
   snow lying on the ground 1 more) — roads and rivers ignore rain and storm, never snow;
3. **night** (the evening and night watches) without a road, a light or a clear sky — one step;
4. **a hazard on the leg** that slows (`hazards.yaml#…pace_steps`: scree, mire, a flooded ford).
Each step is engine-cited from a fact; none is chosen. Example: Wren (walker, normal) in a storm across
the moor → normal → slow (storm, off-road) → 4 points a watch.

**10.3.3 The travel watch.** `[D]` Each watch of a journey day is given **one activity** (T-10-6) for the PC
and one for each companion (16). The **default day** is: morning *travel*, afternoon *travel*, evening
*camp*, night *sleep* (a `rest_long`, 07.8.1). The player may change any watch's activity before it
starts. A *travel* watch earns its points at `h.10.travel_progress` (`watch`, phase 4); arrival happens
inside the watch when the points needed run out (arrival hour = the hour at which the cumulative points
reach the leg's need, rounded up), and leftover points carry into the next leg if the journey goes on.
Then `h.10.watch_check` (phase 7) rolls the time-tick die (10.9) for the watch, whatever the activity —
an encounter can find a sleeping camp.

**10.3.4 The journey OFFER.** `[D]` + `[N]` Before the first travel watch the engine shows the plan out of
fiction, and the player commits, changes it, or stays. No die is rolled; nothing is hidden that the PC
knows:

```
[JOURNEY] To <destination> by <legs in words>. At <pace>: about <days and watches> (<n> travel watches).
          Country: <region words per T-10-2> · Weather: today <state>; tomorrow <state | unknown>.
          Supply: <carried> for <consumers> = <days> days; needed about <days needed> (+ <margin>).
          Light: <sources and intervals> (needed only at night or underground).
          Way-finding: <none needed | <n> trackless days, <navigator | "no navigator: you would go by
          <landmark | the long way | blind>">>. Known hazards: <list | none known>.
```

A journey into a region whose home band exceeds the PC's power band adds one fixed line: "`[WARNING]
Things there are stronger than you.`" at one band above, or "`[WARNING] Things there are far stronger than
you: what lives there can kill you.`" at two or more. It writes no lethal context (07.3.3's rows fire when
a creature there is first perceived, 09.6.6); it is the earlier, regional notice, the West Marches
promise that distance is danger and that the player is told so [R6 B-15; R5 P-32].

**10.3.5 The march allowance and forced marches.** `[D]` + `[T]` A body can march so much a day.
- **Walkers**: an allowance of **2 march units** a day (reset at the `day` boundary, dawn). A travel watch
  at slow or normal pace costs 1 unit; at fast, 2.
- **Mounts**: each mount has its own allowance of **2 units** (ride pace, or normal for walk-pace
  mounts: 1 unit a watch; hard_ride: 2; a mount loaded past half its carry capacity: +1 per watch).
- **A forced march** is any travel watch that takes a walker or mount past its allowance. For each unit
  over, the walker receives **one stack of `cond.exhausted`** (07.8.10), applied at that watch's end by
  `h.10.travel_progress`; the player may first declare 07.8.10's **push-on** Endure beat (Endurance,
  against Moderate; Hard with one stack held; Very hard with two) to defer the stack by as many watches
  as the delivered reach. A mount's stacks are its own (16/07): at three stacks it cannot be ridden or
  loaded until it has had a long rest.
- So a third travel watch at normal pace in a day is one forced unit, a fourth two, and a walker who
  marches three watches a day for three days without pushing on holds three stacks on the third evening:
  every army story's forced march, priced in the same condition 07 uses for sleeplessness and want.
  `cond.exhausted` is removed by long rests per T-07-14.

**10.3.6 Changing the plan, turning back, and stopping.** `[D]` The player may change destination, pace,
schedule or roles at any watch boundary, or after any interrupt; the journey record keeps the points
earned on the current leg. Turning back on a leg reverses it: the points already earned are the points
needed to return. Stopping in the open turns the next watches into *camp* or *rest*; an interrupted
journey is resumed with its remainder (00.7.8).

**10.3.7 Travel by water.** `[D]` A water leg (`route_kind: river | water`) is travelled by vessel (08.10.4)
or by passage (08.8.8). Paces (`travel.yaml#vessel_pace`, points per watch):

| Vessel | Calm water | Downstream | Upstream | Sea | Watches a day |
|---|---|---|---|---|---|
| raft | — | 8 | cannot | cannot | 2 (moored at night) |
| rowboat | 6 | 8 | 4 | coast only, 4 in calm weather | 2 |
| keelboat | 6 | 9 | 6 | cannot | 3 (crew rows in shifts) |
| river barge | 6 | 8 | 4 | cannot | 3 |
| cog | — | — | — | 16 | 4 (crew in watches; passengers rest) |

A crewed vessel travelling through the night does not tire its passengers: they may sleep aboard
(`rest_site: camp` under cover, `rough` on an open deck). A vessel's **hull clock** (08.10.4) takes
`cost.gear` against the vessel; when it completes the vessel **founders**: everyone aboard is in the water
(`haz.swift_water` on a river, `haz.open_water` at sea, 10.12) and the cargo is lost unless saved by
beats. A water route's hazards (rapids, a weir, reefs) are fixed on its link and met in order; a storm
at sea is the weather's `haz.storm_at_sea`.

**10.3.8 Travel underground.** `[D]` An underground leg (`route_kind: underway`, or trackless through
`terrain.underground`) is travelled as overland, with three differences: it is always dark (10.7.2: a
light is needed, or the party moves at crawl with sight-reliant beats under `cond.blinded`); its
way-finding uses `deed.wilds.navigation.underways`; and weather does not apply (only the place's own
hazards: bad air, flooding, collapse). Watches, supply and the time-tick check run as above.

### 10.4 Navigation and getting lost

**10.4.1 When the way must be found.** `[J:flag]` + `[D]`

```
### 10.4.1  Does this leg need way-finding?                         [J:flag] [D]
Trigger [T]:        a travel watch on a leg begins (h.10.travel_progress, before points)
Loads in:           situation.travel.*
License check:      none for the question
Decisions (J):      1. NEEDED [J:flag] "Is the party leaving every road, river and track, or is the
                       way hidden from them?" True only when (a) the leg's route_kind is trackless, or
                       underway without light, or (b) the leg is a track and the visibility facts say
                       fog, blizzard, or night without light; false on a road or river, on a track in
                       fair visibility, and on a known site passage. Uncertain -> true.
Computation [D]:    true -> one way-finding beat is due for this leg today (10.4.2), at the first
                    such watch of the day; it rides (01.4.2) for the rest of the day unless a
                    snag-bearing condition appears that was not on the frame (fog rolls in, night
                    falls, the party is driven off its line by a chase), which makes a new beat due.
Stakes:             none for the question
State writes:       journey.wayfinding_due
Narration may not imply: that a road-follower might be lost; that a trackless traveler cannot be
Worst case (J):     a needed beat skipped -> the party cannot become lost that day (one day's chance,
                    errs lenient, class i); a needless one -> a roll the player sees at a road's
                    Easy tier (class ii)
Examples:           inside: crossing the Fenmoor from the causeway to the drowned chapel (trackless).
                    inside: the drovers' track in fog (track + fog).
                    outside: the Salt Road at night with a lantern (road). outside: a deer track the
                    party has already followed in daylight today (it rode).
                    non-example: "we follow the stream, so we can't get lost" on a trackless leg ->
                    the stream is a landmark that makes the crude fallback usable (10.4.4); the beat
                    is still due.
Anchor:             no
Basis:              [R5 EX-02] [R: https://thealexandrian.net/wordpress/17308/roleplaying-games/hexcrawl] [01.4.2] [DL-10-04]
```

**10.4.2 The way-finding beat.** `[J:rung]` + `[J:flag]` + `[D]` *Anchor: yes.*

```
### 10.4.2  Find the way                                           [J:rung] [J:flag] [D]
Trigger [T]:        journey.wayfinding_due (10.4.1), or the player asks "where are we?" while lost
Loads in:           situation.travel.*
License check:      lic.training.wilds_navigation (G2; scope "keep a course without road or
                    landmark, by stars or underground"; grade caps trained Hard, expert Very hard,
                    master Legendary). Without it: G3, redirected to the license's crude_fallback
                    (verb.observe, "follow a road, a river or a visible landmark", dc_shift +5, reach
                    capped Limited) when 10.4.4 finds a usable landmark; else 10.4.5's paths.
Decisions (J):      1. TIER [J:rung], only when the area holds no stored nav_tier (data and generated
                       areas hold one; T-10-12 gives the default by terrain):
                       EASY - open country with long sightlines: grassland, farmland, hills, moor;
                         managed woodland with paths. typical: the downs. boundary: downs under low
                         cloud (still easy: weather is a snag, never a tier).
                       MODERATE - country that hides the sky or bends the line: deepwood, marsh,
                         badlands, tundra, coast cliffs. typical: an old wood with clearings.
                         boundary: the trackless Tangle (hard).
                       HARD - country that misleads: swamp, jungle, desert dunes, snowfield,
                         mountains off the passes, ancient deepwood, caves with light. typical: the
                         mire. boundary: a desert with a known well-line (hard) / open sand (v. hard).
                       VERY HARD - featureless or folding country: glacier, open sand sea, open sea
                         out of sight of land under cloud, deep warrens, fey-touched woods.
                       Uncertain between two -> the harder (the tier word is shown in the OFFER).
                    2. LEVERS and SNAGS [J:flag each], citing facts (00.3.9; at most two of each):
                       Precision levers - a map of this area (an item with the fact maps: <area>);
                       the area mapped by the PC (fact area.mapped_by_pc); slow pace (journey fact);
                       stars visible at night (weather clear or fair); a guide's Help (01.14.8).
                       Precision snags (engine-cited) - night without stars; fog, storm, snow or
                       blizzard (weather.today); fast pace.
Computation [D]:    verb.observe; attribute Wits (Intellect when the method is reading a map or the
                    stars); primary tag deed.wilds.navigation.wayfinding (underways underground;
                    stars by stars); DC = the area's stored nav_tier (+5 for the crude fallback);
                    SECRET frame (01.4.7): the character cannot know whether the line is true;
                    threatened cost cost.time (the detour), alternate cost.drain (supply spent on
                    the long way). Reach Standard (Limited for the fallback).
                    Delivered reach -> 0: OFF COURSE (10.4.6: the veer, sealed); 1: on course, the
                    day's pace one step slower (the long way round); 2: on course; 3: on course,
                    +2 points on each travel watch of this leg today (a better line); 4: as 3, and
                    one undiscovered place in the area is discovered (with this frame's id, 10.1.5).
                    Take the time (01.4.4) is allowed at Easy, Moderate and Hard: no roll, reach
                    Standard, and each travel watch of the day earns half its points.
Stakes:             RISKY; DIRE only when the area's standing hazards include one of S3+ that a wrong
                    line walks into (a crevasse field, a sucking bog), cited as the source
State writes:       journey.on_course, or the sealed fact nav.lost (10.4.6); the frame
Narration may not imply: that the character knows the line is wrong; a landmark not in state
Worst case (J):     TIER one rung off: DC 5 off; the tier word is shown even though the odds are not
                    (class i). A wrongly allowed lever: +2 (class i).
Examples:           inside: Wren (no license) crossing the Fenmoor (moderate) toward the drowned
                    chapel, whose tower stands clear on a fair day -> fallback usable: Observe +3 vs
                    20, Limited. boundary: the same in fog -> the tower is not visible: 10.4.5.
                    inside: a trained navigator (+4) on the downs (easy, 10) with the PC's own map
                    (Precision +2) -> +6 vs 10: off course 5%, a better line 35%.
                    non-example: "I've got a good sense of direction" -> an assertion, not a lever.
Anchor:             yes. Intent verbs: find the way, navigate, steer by, keep the line, get our
                    bearings, reorient. Knobs: dc (tier -> stored); attribute (Wits -> Intellect);
                    time_cost (a day -> one leg); reach_unit (course -> progress points). Adapts to:
                    steering a boat through a reed maze; finding the way through a smoke-filled
                    hall; leading refugees through a burning town at night.
Basis:              [R5 EX-02, P-31 (lead the way), P-33 (Map the Area)] [lic.training.wilds_navigation]
                    [R: https://thealexandrian.net/wordpress/17464/roleplaying-games/hexcrawl-part-12-at-the-table] [DL-10-04, DL-10-05]
```

*Odds* (`sim10_nav.py`, exhaustive d20; "off course" = a failure not taken as success-at-cost, or a
critical failure): a trained navigator at +4 is off course 10% at Easy, 35% at Moderate, 60% at Hard,
85% at Very hard; with a map and slow pace (+8), 5 / 15 / 40 / 65%. An unlicensed traveler on the
fallback (+3 against DC +5) is off course 40% at Easy and 65% at Moderate — which is why taking the time
(half points, no roll) and the long way by road exist: patience and the beaten way are open to everyone.

**10.4.3 The area's navigation tier is stored.** `[D]` Every area carries `nav_tier` (13 writes it; a
generated area takes T-10-12's default for its primary terrain). It is the obstacle's stored DC for every
way-finding beat in that area (00.3.8 source 1) and is never re-rated in play; weather, night and pace
are snags and levers on the roll, never tier changes (DL-00A-10).

**10.4.4 Landmarks and the crude fallback.** `[J:flag]` The fallback method — "follow a road, a river or a
visible landmark" — is usable on a trackless leg only when `[J:flag]` *"Is a recorded landmark of this
area (or a river or road in it) visible now?"* True only when the area's `landmarks` or links hold one
AND visibility allows it: daylight and no fog, blizzard or storm for a distant landmark (a peak, a tower);
any light for a near one (a stream walked beside); the sun itself counts under a `clear` or `fair` sky in
an `open` or `broken` area. False in `closed` areas without a stream (deepwood canopy, jungle, swamp,
caves), in fog, and at night without stars or light. Uncertain → false. *Worst case:* a fallback allowed
without a visible landmark — the roll is still made at +5 and Limited (class i).

**10.4.5 When no way-finding is possible.** `[D]` With no license and no usable landmark, way-finding is G3
and the redirect (01.3.6) names every path that exists in state: (a) **the long way**: follow a road,
river or track that reaches the destination or near it (the plan is recomputed with its extra watches);
(b) **wait** for the weather or the day to clear (camp; the time-tick check runs); (c) **a navigator**: a
companion or hireling with the license holds the role (16; 08.8.8 wages); (d) **mark and go slow**: blaze
trees and cairn the way (verb.handle, no roll in fair conditions): the party moves at crawl and can never
be lost *on the way back* along its marks — which is not the same as finding the destination; (e) **go
blind**: walk anyway. Going blind is legal (Move covers travel on foot) and chosen knowingly: no
way-finding beat is made, and each such day is **off course** (10.4.6) — except that a watch which ends
with the destination area's own landmark in sight (the engine checks it at each watch end) puts the
party on course from there. The licensed never face (d)–(e) unless they choose to [C:VII; C:P16].

**10.4.6 Off course: the veer.** `[S]` + `[D]` When a way-finding beat delivers reach 0 (or a blind day
begins), the engine writes the **sealed** fact `nav.lost {journey, intended_leg, veer_to, since,
watches_lost}`:
- `veer_to` is drawn with `roll_table(tbl.10.veer)` (d6): 1–2 the link of the current area nearest the
  intended bearing on its left, 3–4 on its right, 5 a link back the way the party came, 6 circling (no
  link: the watch's points are spent going nowhere). Unknown links may be drawn; they become known when
  the party reaches their ends.
- The day's points accrue toward `veer_to`. The party believes it is on course; narration shows the land
  truly crossed (by its true terrain record), never the land the player expects, and never says "lost".
- On reaching `veer_to`'s place the party arrives there and discovers it (`frame_id: null`, 10.1.5).

**10.4.7 Realizing, and finding the way again.** `[D]` + `[T]` The seal on `nav.lost` opens at the first of:
1. **the expected arrival fails**: at the first watch boundary after the intended leg's points would have
   been complete plus one travel watch, the engine unseals "the place should be here and is not" (the PC
   knows they are off course, not where they are);
2. **a way-finding beat while lost** ("where are we?", the frame of 10.4.2 against the TRUE area's tier):
   reach ≥ 1 reveals the true position (the area and the nearest known place) and the course from here;
   reach 0 reveals only that they are off course;
3. **recognition**: arriving at, or perceiving, a discovered or known place (a landmark seen from a
   vantage on the opportunity face, 10.9.4), or meeting someone who can say where this is;
4. **a license or ability** that answers it: 02's *stonesense* answers "which way is down, how deep, which
   way back" underground as Certain (02's request); a divination working per its text (05).
Recovery costs time, never a roll by itself: **backtrack** along the party's own trail (verb.observe,
`deed.wilds.tracking.trailing`, Easy, or Moderate if rain or snow has fallen since; each watch backtracked
undoes one watch of veer); **reorient** (item 2, then re-plan from the true area); or **strike a line** to
the nearest road or river (the crude fallback's method, always available once the PC knows they are off
course). Lost days have spent supply and watches, and the world ran meanwhile: that is the cost of being
lost, and it is the right size — measured in time, which every clock in the world listens to
[R5 EX-02; R1 G-20].

### 10.5 Journey roles

**10.5.1 The four roles.** `[D]` During a travel or camp watch each traveler may hold **one role** for the
whole watch, written as the fact `journey_role {actor, watch, role}` at the watch's start; 03's
`cnt.journey` reads it at the watch boundary (navigator → `deed.wilds.navigation.wayfinding`; scout →
`deed.wilds.tracking.sign`; forager → `deed.wilds.foraging.food`; lookout →
`deed.wilds.survival.weathersense`; quartermaster → `deed.wilds.survival.provisioning`). The roles are 03's
four plus chapter 16's fifth, **quartermaster**, and 16's companions take them by the same rules (T-10-7;
`travel.yaml#roles`) [integration: IR ch.16 to 10 (a)]:

| Role | Allowed at | What it does (all `[D]`) |
|---|---|---|
| **navigator** | any pace; any watch of a moving party | makes the day's way-finding beat (10.4.2). Without a navigator, 10.4.5 applies even if someone in the party holds the license |
| **lookout** | slow or normal travel; any camp watch | on an **encounter** arrival the party is never `cond.surprised` (06.2.4: the lookout saw them) and the encounter distance is one band farther in `open` and `broken` country (T-10-15); on an **omen** the sign carries one more fact: the kind of thing coming (its archetype family, as a tell); in camp, sleepers are woken before the encounter arrives (the rest is suspended, not broken, 07.8.3) |
| **scout** | slow or normal travel | on an encounter arrival the scout perceives first: the other side is `unaware` (06.2.4) unless its notice beats the scout's Sneak total (rolled by the engine once per watch and stored), and the party may slip away without a beat while the other side is unaware; on a **discovery** face the scout finds the nearest undiscovered site or landmark within the area and may reveal it by its own Observe beat (with a frame id: evidence); a scout is at `band.far` from its party when an encounter starts |
| **forager** | slow travel only | gathers while walking: at the watch's end a forage beat (10.6.4) with an engine-cited Precision snag "on the move", yielding delivered reach − 1 supply (minimum 0) |
| **quartermaster** | any pace; any camp watch; an ally with `kn.quartermaster` or a holder of `lic.training.wilds_survival` | **once per day**, prevents one depletion face (`tbl.10.depletion` rows 1–4: spoiled supply, a guttering light, a damaged item): the face counts as a lull without its progress point (16.8.3) [integration: IR ch.16 to 10] |

**10.5.2 Defaults for one traveler.** `[D]` A PC alone holds **navigator** on a leg that needs way-finding,
otherwise **lookout**; the player may name another. A lone sleeper is no lookout: in a night watch spent
asleep the PC is `unaware` at an encounter's arrival unless a companion keeps watch, a trained animal
(16) guards, a ward (05) stands, or the PC rigged an alarm (verb.setup with cord and pans: the fact
`camp.alarm`, which at arrival means "woken in time": not surprised, though at `band.near`). A role held is
a deed only while the actor holds it for the whole watch; a watch broken by an interrupt counts if the
role was being performed when it came. An ally keeps at most two watches a day in a role (the night rota,
16.8.3); a third falls under 07.8.10's `watches_awake` [integration: IR ch.16 to 10 (b)].

**10.5.3 Roles from licenses.** `[D]` A license whose scope covers a journey task gives the role at the pace
it names (none in the core pool do; 05 and 13 may add one, such as a ranger's "forage at normal pace").
Roles never add actions, and no one holds two roles in one watch (one watch, one activity).

### 10.6 Supply, want, foraging and hunting

**10.6.1 Supply.** `[D]` **Supply** is a quantity on the carrier (08.9.4): **1 supply = one person's food and
water for one day**. Every 2 supply (or part) weighs 1 load unit; trail rations sell 2 supply per coin (08).
This chapter owns its consumption and want. A **consumer** is the PC, each companion and hireling (16),
and each mount that is not grazing (10.8.2). Supply is shown in the codex (00.6.3).

**10.6.2 The daily consumption.** `[D]` Handler `h.10.supply` (`day`, phase 4) runs at each dawn while
`pc.on_venture` is true, or while the PC is anywhere not a haven and not paying a lifestyle (08.8.6):
1. **Need** = 1 per consumer; **+1** per consumer on a day whose weather was `heat` or `scorching`, or that
   was spent in `terrain.arid` (a dry country drinks double), **unless** a `water_source` fact held for the
   party that day (a spring, a river, a well, a successful water forage). Waybread-type items lower one
   consumer's need by 1, never below 1 (08.9.4).
2. **Allocation**: supply is given in the party's standing order (default: the PC, companions, hirelings,
   mounts; the player may set another order at any time out of fiction).
3. **Half rations**: if the player has declared half rations for the day (before dawn), each consumer's
   need is halved, rounded up per two consumers (two travelers on half rations use 1). A consumer on half
   rations is *fed* for the want rule below, but its next long rest is at best `partial` (07.8.4: "no food
   this day"), and a **second consecutive** half-ration day counts as a day without food.
4. **Want**: each consumer left unfed receives **one stack of `cond.exhausted`** (07.8.10) and the fact
   `went_without {actor, day}`; with three stacks held and the want continuing, 07's `deprivation` warning
   fires (07.3.3) and each further stack is instead **S3 harm, no reduction** (lethal once the warning is
   effective) — starving is slow, telegraphed and real (07's text, consumed here).
5. **Spoilage** (the depletion face, 10.9.4) and **water foraged** (10.6.4) are applied at their own moments.
The OFFER of every journey shows supply against need (10.3.4) so want is never a surprise.

**10.6.3 Finding water.** `[D]` In arid country, or in `heat`/`scorching` weather, water is the binding
need. A route link or area with `water_source: true` waives the extra need for a day spent along it. A
**find water** beat (T-10-20) — verb.observe, `deed.wilds.foraging.water`, under
`lic.training.wilds_foraging` (crude fallback: "gather what is plainly edible", dc_shift +5, Limited) —
at the area's forage tier (one step harder in `terrain.arid`) writes `water_source` for the party for
the day on reach ≥ 1, and also fills waterskins to carry the next day's water on reach ≥ 2.

**10.6.4 Forage.** `[D]` + `[J:flag]` *Anchor: yes.*

```
### 10.6.4  Forage: gather food from the land                      [J:flag] [D]
Trigger [T]:        the player gives a watch (or an hour in free mode) to gathering food
Loads in:           situation.travel.*, situation.rest.camp, situation.exploration.wilderness
License check:      lic.training.wilds_foraging (G2: "find food and water for a group; identify edible,
                    medicinal and poisonous plants"). Without it: G3 -> crude_fallback verb.observe
                    "gather what is plainly edible", dc_shift +5, reach capped Limited, consequence:
                    a critical failure gathers something harmful.
Decisions (J):      1. PICKED OVER [J:flag] "Has this area been foraged by this party since the last
                       dawn?" True only when the venture record shows a forage beat in this area today;
                       then an engine-cited Precision snag "picked over" applies. Uncertain -> false.
Computation [D]:    verb.observe, attribute Wits, primary tag deed.wilds.foraging.food; DC = the area's
                    forage_tier for the current season (T-10-12; winter one step harder); stakes SAFE
                    (failure means no food) unless a recorded source exists (a hostile watcher, a
                    hazard where the food grows); reach Standard (Limited on the fallback).
                    Yield: supply = delivered reach (1-4) per watch; per hour in free mode, delivered
                    reach - 1. Forager role on the move: 10.5.1. Critical failure on the fallback:
                    the gathered food carries the sealed fact harmful: aff.nightshade (ingested), an
                    exposure when eaten (07.9.2); a licensed forager's critical failure is the Safe
                    S1 cost only.
                    Season and terrain: T-10-12's forage tier; no food grows on glacier or in the
                    deep underground (G4 there: nothing to gather), and the redirect names hunting,
                    fishing or carried supply.
Stakes:             SAFE (Risky when a source is cited)
State writes:       supply +yield; venture.foraged_in; the harmful fact when it applies
Narration may not imply: food the yield does not hold; that harmful food is known to be harmful
Worst case (J):     PICKED OVER wrong: a 2-point snag misapplied or missed on one roll (class i)
Examples:           inside: Wren (no license, Wits +2, floor +1) in a summer wood (easy) -> fallback:
                    +3 vs 15, Limited: about 0.65 supply a watch. boundary: a trained forager (+4)
                    in the same wood -> +4 vs 10, Standard: about 2 supply a watch (sim10_nav.py).
                    outside: foraging on the Ice Tongue glacier -> G4, nothing grows.
                    non-example: "there must be berries this time of year" -> the season is already
                    in the tier; the claim adds nothing.
Anchor:             yes. Intent verbs: forage, gather, scrounge, find food, collect herbs. Knobs: dc
                    (forage tier -> stored area tier); time_cost (watch -> hour); reach_unit (supply ->
                    herb or material units for 08's crafting). Adapts to: gathering firewood in a wet
                    wood (Handle, the same tiers); collecting a named herb for a remedy (the herb as
                    the obstacle, its rarity band -> tier, 08.6.2).
Basis:              [R5 EX-06, P-31 (forage, hunt, fish)] [lic.training.wilds_foraging] [08.9.4] [DL-10-06]
```

**10.6.5 Hunt and fish.** `[D]` *Anchor: yes.* **Hunt** (one watch): track and take game — a single beat
whose method includes the kill (a shot, a thrown spear, a snare sprung; it requires a missile weapon, a
spear, or snares carried). License `lic.training.wilds_tracking` ("hunt game"); crude fallback
verb.observe "follow fresh, plain tracks", dc_shift +5, Limited. Frame: verb.observe, Wits,
`deed.wilds.tracking.hunting`; DC = the area's `game_tier` (T-10-12); stakes Safe unless a source is
recorded (Risky in an area whose encounter table lists `creature.beast.predator` rows: the threatened
cost is `cost.exposure` toward the time-tick die's pending threat, 10.9.6, if one exists, else
`cost.time`). Yield: **supply = 2 × delivered reach**, and a fresh carcass to harvest (08.3.10: hide,
horn, sinew; 1 interval or 1 hour). Hunting a named great beast is not this rule: it is an encounter
the PC seeks (10.9.6 "seek it"). **Fish** (one watch, at a river, lake or coast with line, net or spear):
verb.handle (basic: "use an object as its nature suggests"), Wits, `deed.wilds.foraging.food`, Easy at
rivers and lakes, Moderate at the coast; yield supply = delivered reach (reach capped Limited without
proper tackle). **Snares** (set during a camp watch, no extra watch): verb.handle; at the next dawn the
engine rolls d6 against the area's game tier (Easy 3+, Moderate 4+, Hard 5+, Very hard 6) for 1 supply;
`lic.training.wilds_tracking` or `wilds_survival` adds +1 to the die. *Knobs:* dc (game tier → a named
quarry's own defense); time_cost (watch → interval for a quick snare in a site); reach_unit (supply →
harvest parts). Numbers (`sim10_nav.py`): a licensed tracker at +4 (Wits +2, competence +2: Wren, whose forester origin gives her `lic.training.wilds_tracking` at `trained` with that competence, 02) averages 4.1 supply a hunting watch in Easy country, 2.7 in Moderate, 1.7 in Hard, and comes back empty-handed 10% / 35% / 60% of the time.

**10.6.6 Living off the land, in sum.** `[N]` A licensed forager in good country feeds two people a day
from one watch; a hunter feeds three or four; a party with neither eats what it carries. That makes the
journey's shape a real choice every day — walk, or feed yourself — which Forbidden Lands and Ironsworn
both identified as the heart of overland play [R5 P-30, P-31].

### 10.7 Light and darkness

**10.7.1 Light sources burn by the interval.** `[D]` Light sources are 08's goods (08.9.5): a **torch**
burns **6 intervals** (bright to `band.close`, dim to `band.near`); a **lantern** burns a flask of oil in
**24 intervals** (same light; hooded, it can be shut to darkness as a free activity); a **candle** burns 6
intervals (dim to `band.close`); a **tinderbox** lights a fire or torch in 1 interval (1 hour in rain);
*glowing* items shed dim light to `band.close` and burn nothing. Handler `h.10.light` (`interval`, phase 4)
takes 1 from the remaining intervals of every lit source, in every time mode (a torch carried through a
night watch of travel burns 36 intervals: six torches). When a source reaches **1 interval** remaining,
the engine raises a narration obligation — *it gutters* — so its end is never a surprise; at 0 it is
spent (08's `h.08.durations` marks the item). Lighting, shuttering and dousing are free activities.

**10.7.2 The light of a scene.** `[D]` `scene.light` (06.3.7: `bright | dim | dark`) is computed by
`h.10.scene_frame` at every `scene_start`, and recomputed at every `watch` boundary and whenever a light is
lit, spent, doused or carried away (T-10-9; first match):
1. **Underground, or indoors without windows, or inside a site whose domain is `dark`**: dark, except within
   a light's radius (bright to its bright band, dim to its dim band).
2. **Outdoors, morning or afternoon watch**: bright; dim in `fog`, `storm`, `thunderstorm` or `blizzard`;
   dim under the canopy of a `closed` area (deepwood, jungle, swamp).
3. **Outdoors, evening or night watch**: dim under a `clear` or `fair` sky in an `open` or `broken` area
   (moon and stars); dark otherwise (`overcast`, `rain`, `fog`, storms, snow, or a `closed` area).
4. Lights then brighten their radius as in 1.
The value is written as the fact `scene.light` (06 reads it for `flag.obscured` and `cond.blinded`; 07.8.2
and 10.9.3 read it). Night-sight (an origin's or ability's license) treats dark as dim and dim as bright
for its holder's own sight-reliant beats only.

**10.7.3 What darkness does.** `[D]` In `dark`, without light or night-sight: sight-reliant beats are under
`cond.blinded` (06.3.7); travel moves at **crawl**; in a site, **Explore onward** by sight is G4 and is
re-anchored to Explore by touch (10.13.5: Observe by touch, an engine-cited Precision snag, reach capped
Limited); the site check's cadence is one step faster (10.9.3); and a hazard whose `perceived_on_sight` is
true is not perceived until touched, so its `severity` warning cannot fire, so it cannot be lethal
(07.3.5), though it can put the character Down — which is why light is the delver's first supply. A light
cuts both ways: a carried light is a `trait.sense.visible` fact; denizens and watchers perceive its bearer
at `band.far` in dark places, and hiding while carrying an unshuttered light is G4 (06.3.7: no veil).

**10.7.4 Reading the budget.** `[N]` A delve of about fourteen intervals (the median of `sim10_site2.py`
for a medium site) burns three torches or most of a lantern flask; a deep site wants a lantern and spare
oil. Shadowdark taught that light running out is a dungeon's best clock; real-time light is meaningless in
asynchronous text (R5 X-05), so here the intervals burn by resolved beats [R5 P-13, P-34].

### 10.8 Mounts, vehicles and vessels

**10.8.1 Paces of conveyances.** `[D]` Each mount and vehicle carries `travel_pace` (08's base items:
`walk` → the walker ladder, `ride` → ride, `river`/`sea` → 10.3.7); T-10-5 lists them. A party moving with
a vehicle moves at the vehicle's pace and only where its `vehicle_ok` allows (08.10.3): a **wagon** or
**carriage** needs a road (elsewhere G4, with the redirect "unload to pack animals or porters"); a **cart**
or **handcart** goes on roads and tracks, and across `terrain.plains` at slow pace; a **sledge** needs
snow lying or frozen terrain (normal pace there; G4 elsewhere). Barding and war tack make a mount's pace
one step slower (08.10.1).

**10.8.2 Feeding mounts.** `[D]` A mount eats **1 supply a day** (10.6.2) unless it **grazes**: the camp
watch (default evening) was spent where `grazing` holds — the area's fact (13), defaulting to true in
`terrain.plains.*`, `terrain.highland.hills` and `terrain.forest.woodland` from spring to autumn, false
otherwise and always in winter. A mount left unfed takes the want rule (one `cond.exhausted` stack; 16/07).
Mounts drink where people drink; in arid country they need the extra water too.

**10.8.3 Riding.** `[D]` Riding is basic (verb.handle, "ride", 00.12.5): ordinary riding on a journey
never rolls. A beat is needed only when something makes it uncertain and costly: a hard ride over
broken ground at night (verb.handle, Presence or Agility, Moderate, threatened cost `cost.footing`: the
mount stumbles), a ford in spate (10.12), a mount frightened by a creature with dread (16's check,
16.15.4).
Mounted conflict is 06.15's.

**10.8.4 Porters and pack animals.** `[D]` A pack animal or porter adds its carry capacity to the party's
load budget (08.10.1; porters carry 10 load units, 08.8.8) and is a consumer (10.6.1). The party's pace is
the slowest member's (10.3.2), so a donkey train walks.

### 10.9 The time-tick check: one die, every face means something

**10.9.1 One die per tick of time.** `[D]` + `[T]` Whenever exploration time passes outside a haven, the
engine rolls **one d12** — the **time-tick check** — and every face has a meaning (T-10-10). The die is
rolled by a boundary handler, so its results are complications the rules allow (01.11.3 item 5), never
the DM's choice:
- **Travel and the wild**: `h.10.watch_check` (`watch`, phase 7) rolls once at the end of every watch the
  PC spends outside a haven and outside a site — travelling, camping, sleeping, foraging, waiting — at the
  danger rating of the area (or route link) where the watch ended.
- **Sites**: `h.10.site_check` (`interval`, phase 7) rolls once every **cadence** intervals of site time
  (10.9.3) at the site's danger rating, with the site's own faces.
- **Havens**: never (10.2.3). **Conflict**: a watch or check boundary that falls inside a conflict is
  deferred to `conflict_end` (the fight is already the event).
The DM never rolls the die, never chooses a face, and narrates only what the face's results return
(PR-00-2 step 5) [R6 B-14, B-R5; R: https://necropraxis.com/2014/12/23/hazard-system-v0-2/].

**10.9.2 Danger ratings.** `[J:rung]` + `[D]` Every region, area, site and route link carries a **danger
rating** (`danger`), a five-rung ladder of *how often* the place's dangers come (its *band* says how strong
they are). Data holds it for authored places (13); the DM picks it only for a generated place without one:

```
### 10.9.2  Danger rating                                          [J:rung] [D]
Trigger [T]:        a place is generated (10.1.8) or entered with danger: null
Loads in:           situation.travel.*, situation.exploration.*
License check:      none
Decisions (J):      1. RATING [J:rung]:
                       SAFE - a haven (10.2.3); no check. Only for places with safe: true.
                       SETTLED - people live and travel here; trouble is rare and mostly human.
                         typical: farm country around a town. boundary: a patrolled road through a
                         wood (settled) / the same wood off the road (wild).
                       WILD - no one keeps this land; beasts and outlaws live in it.
                         typical: the forest a day beyond the last farm. boundary: hill pasture
                         grazed in summer (wild) / the same hills in a bad winter (still wild: the
                         weather is not the rating).
                       PERILOUS - something dangerous holds or haunts this land.
                         typical: the marches of an orc warband; a barrow field. boundary: a ruin
                         with a known occupant (perilous) / the occupant's lair itself (deadly).
                       DEADLY - the land itself is a predator's territory or a curse.
                         typical: a dragon's range; the blighted heart of the old kingdom.
                       Uncertain between two -> the region's rating (generated places inherit),
                       else the lower (the band, not the rating, carries lethality).
Computation [D]:    the rating selects the face map (T-10-10). Modifiers, engine-applied: the NIGHT
                    watch counts one rung higher (cap deadly); a road or a route link with danger set
                    by data uses that value; a SITE's rating comes from its theme (10.13.2).
Stakes:             none
State writes:       place.danger
Narration may not imply: a rating in words other than T-10-2's
Worst case (J):     one rung: one more or one fewer encounter face and omen face on the d12 (about
                    0.1-0.2 more threats a day, sim10_travel.py), for one generated place (class i)
Examples:           above.
                    non-example: "we're careful, so treat it as settled" -> care is a lookout and a
                    slow pace (10.5), never a rating.
Anchor:             no
Basis:              [R5 P-34 (Shadowdark danger -> cadence)] [R5 P-33 (terrain flat check)] [R6 B-15] [DL-10-07]
```

**10.9.3 Site cadence.** `[D]` A site checks every **3 intervals** at settled, **2** at wild and perilous,
and **every interval** at deadly; in `dark` (10.7.2) without light the cadence is one step faster (3 → 2
→ 1); a **roused** site (10.13.9) checks every interval and counts one rung higher. The engine keeps
`site.intervals_since_check`; `h.10.site_check` rolls when it reaches the cadence and resets it. Taking the
time (01.4.4), resting, searching and fighting all spend intervals, so all of them feed the check — the
Torchbearer insight that time in a dungeon is measured in what you do [R5 P-13, P-34].

**10.9.4 The faces.** `[D]` T-10-10 maps the d12 by danger rating (`travel.yaml#watch_check` and
`#site_check`). Each face names its result handler; every result is written to state before narration.

*Travel faces.*
- **E · Encounter.** A pending threat arrives (10.9.6); if none is pending, roll the place's encounter table
  (10.10.1): a **non-threat** row arrives now; a **threat** row becomes a pending threat and shows its first
  omen instead (10.9.5).
- **O · Omen.** If a threat is pending, its second sign shows and it **arrives** (it was close). Otherwise
  roll the encounter table: a threat row becomes pending and shows its first omen; a non-threat row shows a
  sign of travelers ahead (it arrives at the next E face, or the party may seek it).
- **V · Local event.** `roll_table(tbl.<region>.events)` if 13 provides one, else 12's
  `roll_table(tbl.event_focus, {phase})` (12.6.5 source d): the world acting on its own, bounded by 12.6.5
  (never harms, never costs).
- **D · Depletion.** `roll_table(tbl.10.depletion)` (d6): 1–2 one supply spoils or is spilled (−1; if none
  carried, a waterskin leaks: no water source this day in arid country); 3 a burning light gutters (−2
  intervals; if none is lit, a torch or the oil in store is found damp: one source loses half its
  remaining intervals, rounded down); 4 a strap, string or boot gives (one carried item `damaged`, 08.1.9, engine's draw among
  non-relic gear); 5 a mount goes lame for the day (pace one step slower; if no mount, ammunition −2); 6
  a hard stretch: the next travel watch earns 2 fewer points. Depletion never harms and never reaches an
  item that is `cost_immune` (08.1.10).
- **W · Weather shift.** `roll_table(tbl.10.weather_shift)` (d6): 1–3 the weather moves one step along its
  `worse` link, 4–6 along its `better` link (`weather.yaml#states`), now; the change applies from the next
  watch; a shift into a state whose hazard applies to exposed travelers interrupts (10.9.8).
- **F · Discovery.** If the area holds an undiscovered place (a site, landmark or settlement, sealed),
  the one nearest the party's route is **discovered** (10.1.5, `frame_id: null`; a scout's beat may make it
  evidence, 10.5.1). If none, `roll_table(tbl.10.find)` (d12: a spring, a waymark cairn, an old campsite, a
  roadside shrine, a cache, a fallen statue, a carcass worth harvesting, a wreck or abandoned cart, a
  signpost, fresh sign of passage, a viewpoint, a lone grave) — each written on mention as a landmark or
  object, several of them levers or loot (a cache rolls 08.3.12 at band − 1, a carcass is harvestable).
- **P · Opportunity.** `roll_table(tbl.10.opportunity)` (d8): 1 windfall (+1 supply: fruit, eggs, a
  snared hare); 2 game sighted (a Precision lever for a hunt in this area today); 3 a better line (+2
  points to the next travel watch); 4 shelter found (the next camp in this area is `camp`, not `rough`,
  and keeps out S2 weather); 5 a vantage (an Observe from height: the adjacent areas' danger words, the
  nearest undiscovered landmark, and recognition if lost, 10.4.7); 6 others' trail marks (a Precision
  lever on way-finding today); 7 water (a `water_source` for the day); 8 a quiet hour (a breather's worth
  of rest without stopping: `breather` boundary at the watch's end, 07.8.1, if no conflict).
- **L · Lull: good going.** Nothing stirs. If travelling, the watch earns **+1 point**; if camping or
  sleeping, the rest is undisturbed; a pending threat's timer does **not** advance this check (10.9.6).

*Site faces* (the same letters where they mean the same thing; the content comes from the site's cards):
- **E · Encounter** and **O · Omen**: as above, with the site's denizen table (10.13.7) in place of the
  region's.
- **S · Stir.** The site's danger clock ticks 1 (10.13.8), with its omen (INV-14).
- **D · Depletion.** As above, but rows 5–6 read: a rope or pole frays (one `damaged`), the air turns bad
  for a moment (a burning light −2 intervals).
- **H · Shift.** `roll_table` on the site domain's `shift` list (10.13.2): water rises, a draught snuffs an
  unshielded flame, a door swings shut behind, dust sifts from a cracking ceiling, a passage is blocked
  (a new obstacle on the way out), a sound carries — each a written fact about the place.
- **F · Discovery.** `roll_table` on the theme's and domain's `discoveries` (10.13.2): a feature of the
  current area that answers something (an inscription, a map scratched on a wall, a body with a key).
- **P · Opportunity.** `roll_table(tbl.10.site_opportunity)` (d8): 1 a secure corner (this area becomes
  `rest_site: camp`); 2 a clue toward the heart (the progress clock +1); 3 a forgotten cache (08.3.12
  `hoard` at site band − 1, small: coin and goods only); 4 an unguarded moment (the next denizen met is
  `unaware`); 5 a short way (the progress clock +1); 6 old marks of earlier delvers (a Precision lever on
  Explore onward here); 7 a light source found (a lantern with half a flask, or three torches); 8 a way out
  (a new exit link from this area to the surface or a known area).
- **L · Lull.** As above (no progress point; the pending timer does not advance; the danger clock is still).

**T-10-10 The time-tick die by danger rating** (canonical: `travel.yaml#watch_check`, `#site_check`).

| Rating | Travel faces (d12) | Site faces (d12) |
|---|---|---|
| settled | 1 E · 2 O · 3 V · 4 D · 5 W · 6 F · 7 P · 8–12 L | 1 E · 2 O · 3 S · 4 D · 5 H · 6 F · 7 P · 8–12 L |
| wild | 1 E · 2–3 O · 4 V · 5 D · 6 W · 7 F · 8 P · 9–12 L | 1 E · 2–3 O · 4 S · 5 D · 6 H · 7 F · 8 P · 9–12 L |
| perilous | 1–2 E · 3–4 O · 5 V · 6 D · 7 W · 8 F · 9 P · 10–12 L | 1–2 E · 3–4 O · 5–6 S · 7 D · 8 H · 9 F · 10 P · 11–12 L |
| deadly | 1–3 E · 4–5 O · 6 V · 7 D · 8 W · 9 F · 10 P · 11–12 L | 1–2 E · 3–5 O · 6–7 S · 8 D · 9 H · 10 F · 11 P · 12 L |

*What it produces* (`sim10_travel.py`, 20,000 days per row, four checks a day, the night watch one rung
higher, threat share of the encounter table 25 / 60 / 75 / 85%, no avoidance): arrivals per day —
settled 0.38 (0.16 hostile), wild 0.57 (0.45 hostile), perilous 0.77 (0.66 hostile), deadly 0.89 (0.81
hostile); omens per day 0.44 / 0.64 / 0.77 / 0.86; local events, discoveries, opportunities, depletions and
weather shifts about one each per three days at every rating; lulls 1.6 / 1.2 / 0.9 / 0.7 a day. A party
that answers half its omens by avoiding the threat meets about 40% fewer hostile encounters (wild: 0.27 a
day). So a three-day crossing of wild country brings about two hostile meetings, each announced, and a
discovery, an opportunity and a local event — nothing like the empty road of a game whose dice only
mean "monster or nothing" [R5 §3.2 #1; R5 §6 "encounter density"].

**10.9.5 Omens before threats.** `[D]` + `[T]` The rule of this chapter: **a hostile encounter never arrives
without an omen first.** Concretely:
1. Every encounter table row carries `threat: true | false` (10.10.1). A **threat** is any row whose
   creatures would attack, ambush, rob or capture the PC on meeting (an archetype with a hostile
   `reaction_roll: false` mind, or any row 13 marks so); travelers, traders, pilgrims, grazing herds and
   wary animals are non-threats until the reaction roll says otherwise (10.10.5), and a reaction roll is
   itself a telegraph (12.11.2).
2. A threat row drawn by any face becomes a **pending threat** (`enc.pending`, sealed; one at a time per
   party): `{id, row, adversary refs, count, sign_stage: 1, checks_since: 0, created_at, place}`. Its first
   sign is narrated at once: an omen drawn from the row's archetype `signs` (`travel.yaml#archetype_signs`;
   13's regional signs override), never naming the creature, always perceivable (tracks, spoor, a sound,
   a smell, the silence of birds, a dead traveler, smoke on the ridge).
3. It **arrives** at the first of: the next **E** face; the next **O** face (whose result is then its
   second, nearer sign in the same breath as its arrival); or the **fourth check after** its creation,
   lulls not counted (it had been shadowing the party all along).
   At wild rating that is usually within a day of travel.
4. A threat that is **out of band** (its threat band ≥ `power_band(pc)` + 1) shows, with its first sign,
   one band tell (09.6.6); at + 2 or more its arrival will raise the lethal warning at first perception
   (07.3.3, 09.6.6) — and the first sign already says, in fiction, that this is something the character
   should not meet ("the tracks are the width of a cartwheel").
5. A threat 13 marks `ambush: true` (brigands at a narrows, a lurker in a pool) is still announced: its
   first sign is the ambush ground itself ("the track narrows between two banks of gorse, and the birds
   are quiet") written as a feature, so a wary player can refuse the ground.
This makes the hidden-mechanics lock and the telegraphed-lethality lock one rule [BRIEF §4; R5 P-36; R6
B-R5]: the world always shows its hand, and the player always has at least one decision between the sign
and the blow.

**10.9.6 Answering an omen.** `[D]` + `[J:enum]` While a threat is pending, the player may act on it
(each is an ordinary beat or plan change; the pending record is updated by its result):

| Answer | How | Result |
|---|---|---|
| **Avoid** | change route or pace: take another link (no roll; costs the detour's watches), or go on at **slow** pace quietly: a Sneak beat for the party (verb.sneak, Agility; the lead traveler's or a group action, 01.14.7) against the pending creatures' notice (their defense, 00.3.8), stakes Risky (cost.exposure), reach Standard | a success (or a detour) writes the pending threat `evaded`: it does not arrive from this check sequence (it stays in the place: a lair, a band of raiders, written for 11 and the encounter log); a failure: it arrives at once, aware of the party |
| **Investigate** | Observe the sign (verb.observe, Wits, `deed.wilds.tracking.sign`; 09.10.2 lore by Recall if the sign is distinctive), at the row's stored tier (by band: T1 Easy … T5 Legendary), a P17 bundle | items delivered from: what kind (archetype), how many (count band), how near (checks until arrival), the advisory word (09.6.5), its disposition if it has one (09's defeat disposition) |
| **Prepare** | Setup beats: choose ground, lay an ambush, fortify the camp, rig an alarm (verb.setup; 01.14.9) | the arrival begins at the PC's chosen positions, the PC side `aware`, the Setup facts in place as levers; the threat still arrives on its schedule |
| **Seek it** | go toward it (Move; Observe to track, 10.15) | it arrives now, the PC side aware, at the encounter distance of T-10-15 one band farther |
| **Ignore** | do nothing | it arrives on its schedule |

`[J:enum]` *Which answer is the player's beat?* Classified from the declaration; uncertain → Investigate
(the safest reading: it changes nothing until the player commits). *Worst case:* an avoidance read as
preparation leaves the threat on schedule — the player sees the result line and may still act (class ii).

**10.9.7 Reading the pacing phase (opt-in).** `[D]` Chapter 10 opts in to 12's pacing director (12's
request) in exactly one way: while the director is in **RELAX** or a **recovery** window (12.7.2, 12.7.5),
a pending threat's fourth-check timer does not run (it arrives only on an E or O face), and an E face with
nothing pending that draws a threat row produces the omen only (as it always does). Nothing already
arrived is softened, no face is re-rolled, no table is changed, and the record shows the rule that applied
(12.7.6: declared, logged, diegetic). Everything else in this chapter runs exactly as written in every
phase.

**10.9.8 Which results stop time.** `[D]` The time-tick handlers are `interrupting` (00.7.8) only for these
results: an encounter **arrives**; an **omen** shows (the player decides what to do about it); a **local
event** that is perceivable now and asks for a response (12.6.5 step 5); a **weather shift** into a state
whose hazard applies to the party as exposed (T-10-14); a **hazard** exposure that will recur (10.12.3).
Depletion, discovery, opportunity and lull never interrupt; they are returned in the list and narrated in
the skip's summary (12.4.6), and the player may turn aside for a discovery at the next watch.

**10.9.9 Narration of the check.** `[N]` One sentence per returned result, in order, from its record:
the omen's sign words, the event's written fact, the find's entity, the weather's new state. *Narration may
not imply:* a face that was not rolled; a threat's identity before it is perceived; a number (a rating,
a face, a clock fill); that nothing will come of an omen.

### 10.10 Encounters: tables, distance, awareness, reaction

**10.10.1 The encounter table format.** `[D]` Encounters belong to places (09.8.2). Every area, route link
and site points at an **encounter table** (`encounter_table`): chapter 13's regional tables, or this
chapter's **generic terrain tables** (`travel.yaml#encounter_tables`, one per terrain branch, d12) for any
place 13 did not cover. Every row is a record:

```yaml
EncounterRow:
  range: str                # die faces, e.g. "1-2"
  kind: enum                # adversary | people | beasts | sign_only | situation
  ref: [arch.* | adv.* | npc_template | situation_seed]   # 09's archetype groups or bestiary ids
  band: enum|int            # "home" | "home-1" | "home+1" | a fixed band 1..5 (13's tables)
  count: str                # "1", "2-4", "group" (the archetype's encounter.group, 09.8.3)
  threat: bool              # 10.9.5
  ambush: bool              # 10.9.5 item 5
  complication: bool        # roll tbl.09.complication on arrival (09.8.5)
  when: [day | night | any] # rows outside their time re-roll once, then stand
  terrain: [tag] | null     # a narrower terrain filter inside the table's branch
  signs: [str] | null       # row-specific omen signs (else the archetype's)
```

**Two sub-tables.** The generic tables, and every regional table 13 writes in the same shape, are split into a
**threat** sub-table (d20, rows by relative band: 6 faces' worth at home − 1, 11 at home, 3 at home + 1 — exactly
09.8.2's 30/55/15) and a **non-threat** sub-table (d6). An E or O face with nothing pending first rolls d12 against
the place's danger rating — threat on **1–3** settled, **1–7** wild, **1–9** perilous, **1–10** deadly (25 / 58 / 75 /
83%, the shares `sim10_travel.py` assumed) — and then rolls the chosen sub-table (`travel.yaml#watch_check.threat_share_d12`).
So the same terrain table serves every ring, and the mixture rule of 10.10.2 item 4 holds by construction.

The engine fields a row as 09.8.3 does: it resolves `band` against the place's home band (clamped to the
archetype's fielded bands, `archetypes.yaml#bands`; an archetype that cannot be fielded at the band re-rolls
the row once, then takes the nearest band it has), picks the bestiary entry of that archetype at that band
(`adversaries.yaml`), rolls the count (`tbl.09.group_shape`), folds four or more of one template into a
**mob** (06.10.2), and adds a leader when the group lists one.

**10.10.2 The table budget (09's contract).** `[D]` Every encounter table, generic or regional, must pass
the audit PR-10-8 before use (13 runs it on its tables; the generic tables pass it by construction):
1. **Bands**: among threat rows, by weight, about **30% at home − 1, 55% at home, 15% at home + 1**; no row
   above home + 1 — anything stronger is a **lair**, a place with a known occupant reachable only by going
   there, signposted by rumor and omen (09.8.2).
2. **Shapes** (T-09-10): crowds are mobs; individuals of the home band at most two; at home bands 4 and 5,
   never two individuals of the home band — a pair becomes a leader (elite) with a lower-band mob, or one
   solo (09.8.1 rule 2).
3. **Words**: against a reference PC of the home band, at least two thirds of threat rows (by weight) are
   `fair` or easier and none is `lethal` (09.8.1 rule 3); a `hard` row carries `complication: false` (a
   complication is a different problem, not a bigger one).
4. **Mixture**: at least one row in four (by weight) is a non-threat (`people`, `beasts` that are not
   predators, `sign_only`) at settled and wild ratings; one in six at perilous; deadly tables may be all
   threats.
5. **Out-of-band rows** are allowed only at home + 1 and always telegraph by 10.9.5 item 4.
The budget is the distribution chapter 04's pacing assumes (09.8.2, I-005).

**10.10.3 Arrival: distance.** `[D]` When an encounter arrives, the engine rolls its starting distance on
T-10-15 by the place's `openness` and the light (`scene.light`), then applies: lookout +1 band farther (open
and broken only), scout +1 band farther (any), fog or night without light → read the place as `closed`,
`ambush` rows start at the ambush ground's distance (usually `band.close`). The result is each
participant's starting band to the PC for 06.3.9 if a conflict starts.

**T-10-15 Encounter distance** (`travel.yaml#encounter_distance`; d6).

| Openness | 1 | 2 | 3 | 4 | 5 | 6 | Examples |
|---|---|---|---|---|---|---|---|
| open | near | near | far | far | distant | distant | grassland, moor, desert, tundra, lake shore, glacier |
| broken | close | near | near | far | far | distant | hills, woodland, farmland with hedges, badlands, ruins above ground |
| closed | close | close | close | near | near | far | deepwood, jungle, swamp, caves, site areas, streets, fog, night without light |

**10.10.4 Arrival: who notices whom.** `[D]` Awareness is state, never the DM's call (06.2.4 reads it):
1. **The PC side** is aware of an arriving encounter if any of: a lookout or scout holds its role (10.5.1);
   the encounter was investigated or prepared for (10.9.6); its creatures are not hiding (a non-ambush row,
   in light the PC can see by); or the PC's passive notice (01.4.6) beats the creatures' stored Sneak total
   (the engine rolled it when the row was fielded, for `ambush` rows and for creatures 09 marks stealthy).
2. **The creatures** are aware of the PC unless: the party moved at slow pace with a successful Sneak that
   watch or against this pending threat (10.9.6 Avoid's beat or the scout's stored total) and the PC's light
   (if any) is shuttered; or the PC is in a `veil` feature or hidden (`flag.hidden`, 06.3.7).
3. A side that is aware of the other while the other is not may **avoid** (leave without a beat while it
   stays unaware), **parley** first, **prepare**, or **strike** (06.2.4 surprise then applies).

**10.10.5 Arrival: what they want.** `[D]` First match (09.8.7): sapient and cunning creatures whose
archetype has `reaction_roll: true` take 12's reaction roll (12.11.2) at the first interaction; animals and
`reaction_roll: false` creatures that are not mindless roll `tbl.09.beast_mood` (2d6, with its cited
modifiers); mindless creatures follow their behavior list; creatures on a mission act on it. The advisory is
computed at framing (09.6.5), the band tells are shown (09.10.1), and if it is `hard` 07's danger notice and
if `lethal` 07's lethal warning are delivered **before** the first beat (07.3.3–07.3.8). The player then
chooses — fight, flee, talk, hide, trade, bargain — and the scene runs in the mode that choice brings
(06 for a fight, 15 for talk, 06.12 for a chase).

**10.10.6 An encounter's aftermath on the journey.** `[D]` After the encounter scene ends (`scene_end`), the
journey resumes with its remainder (00.7.8). The encounter is added to the venture record. A row whose
creatures were not defeated and not evaded remains **in the place** as a fact for that area (a band of
brigands camped at the ford: `area.occupants`), so a return trip meets the same band, wiser — unless 11's
World Turn moves it. A fled PC is **tracked** by pursuers who can (06.12.6's mirror, below).

**10.10.7 Pursuit across country.** `[D]` *Anchor: yes.* When a chase (06.12) ends with the fleer at
`band.distant` and the pursuers' behavior says they keep hunting (`kill`, `capture` and `rob` objectives
while not broken; hungry beasts), the pursuit continues at the **travel scale**: the pursuers become a
pending threat for the fleeing party with **sign_stage 2** (it arrives at the next E or O face, or the
second check), unless the party breaks its trail: a **cover tracks** beat (verb.sneak with Wits,
`deed.guile.stealth`, or `deed.wilds.tracking` under the tracking license; the pursuers' best Wits defense;
one watch at slow pace; stakes Risky) that succeeds writes `evaded`; water, rock or rain since the flight
(levers, cited) make it easier. The reverse — the PC trailing a fled quarry — is **Track** (10.15, T-10-20):
an Observe beat at the trail's tier per watch, each success a tick on 06.12.6's `clk.run_down` at travel
scale (one tick per watch at Standard), the quarry's `clk.quarry_away` ticking 1 a watch by its own pace.
*Knobs:* time_cost (round → watch); dc (ground tier → trail tier, T-10-20); reach_unit (ticks).

### 10.11 Weather

**10.11.1 Weather is a rolled record, not a mood.** `[D]` The weather of a region on a day is the fact
`weather.today` (one **state** from the closed list T-10-13) and its successor `weather.tomorrow`
(sealed until forecast). No narration may describe weather the record does not hold (12.14.2), and every
mechanical effect of weather — pace, way-finding, light, distance, exposure, rest quality, tracking, fire,
the primal source — is read from the state's data (`weather.yaml#states`). Chapter 05's source-present
test reads `weather.today` (05.7.3; 05's request) [R4 §9 10 item 1: environment as explicit tables].

**T-10-13 Weather states** (canonical: `weather.yaml#states`). *Pace* = steps slower off roads (10.3.2);
*Way* = a Precision snag on way-finding; *Light* by day; *Dist.* = read openness as; *Exposure* = the
hazard an exposed traveler meets each watch (10.12.3); *Fire* = tier to light a fire in the open.

| State | Temp. | Pace | Way | Light (day) | Dist. | Exposure (per watch, exposed) | Fire | Also |
|---|---|---|---|---|---|---|---|---|
| clear | mild | 0 | — | bright | as is | — | Trivial | stars at night (a way-finding lever) |
| fair | mild | 0 | — | bright | as is | — | Trivial | stars at night |
| overcast | mild | 0 | — | bright | as is | — | Trivial | nights are dark |
| wind | mild | 0 | — | bright | as is | — | Easy | moving air (05.7.3); unshielded flames gutter (−1 interval each watch) |
| fog | cool | 0 | snag | dim | closed | — | Easy | sounds carry; landmarks hidden (10.4.4) |
| rain | cool | 0 | — | bright | as is | — | Easy (tinderbox 1 hour) | trails one tier harder to follow; water present |
| storm | cool | 1 | snag | dim | closed | `haz.storm_exposure` | Moderate | rivers rise (fords one rung worse next day); nights dark |
| thunderstorm | warm | 1 | snag | dim | closed | `haz.storm_exposure`; on heights or open ground `haz.lightning` | Moderate | lightning present (05.7.3) |
| heat | hot | 0 | — | bright | as is | `haz.heat` (travel or labor by day) | Trivial | +1 water need (10.6.2) |
| scorching | very hot | 1 | — | bright | as is | `haz.scorching_heat` (travel or labor by day) | Trivial | +1 water need; the day watches are best spent resting in shade |
| frost | freezing | 0 | — | bright | as is | `haz.cold` at night without fire or shelter | Easy | water skins freeze overnight unless kept warm |
| snow | freezing | 1 | snag | dim | broken | `haz.cold` | Moderate | writes `snow_lying` (10.11.4); trails of the day are easy to follow |
| blizzard | bitter | 2 | snag | dim | closed | `haz.blizzard` | Hard | travel off roads at crawl; writes `snow_lying` |
| bitter | bitter | 0 | — | bright | as is | `haz.bitter_cold` | Moderate | breath-ice; waterskins freeze |

**10.11.2 Climate zones and the season's regime.** `[D]` Every region (and any area that overrides it)
has a `climate`: **temperate** (the default; downs, farmland, woods), **northern** (pine, tundra, long
winters), **highland** (mountains and high moor: colder, windier, sudden), **arid** (badlands and desert),
**coastal** (shores and islands: wind, fog, mild winters). Underground places have no weather. Each
climate has one **regime table per season** (`weather.yaml#regimes`: 5 climates × 4 seasons, each a d12
over the states). Handler `h.10.weather_regime` (`season`, phase 6) sets each region's current regime at
the season boundary (season ids from chapter 11's calendar). The seasons are 00's 13-week seasons
(spring, summer, autumn, winter, in the order 11's calendar gives them).

**10.11.3 The daily roll, with persistence.** `[D]` Handler `h.10.weather` (`day`, phase 7) runs at each
dawn for every region the PC is in or adjacent to (and for any region a pending forecast concerns):
1. `weather.today` ← `weather.tomorrow` (rolled yesterday).
2. Roll `weather.tomorrow`: d6 — on **1–2** it is the same as today (weather holds), provided today's state
   appears in the season's table; otherwise, and on **3–6**, `roll_table(<climate>.<season>)` (d12).
3. Write both facts on the region (`set_fact`, `source: generation`); `weather.tomorrow` is sealed until a
   forecast unseals it.
4. Apply standing weather facts (10.11.4) and return the day's weather for narration.
The weather-shift face (10.9.4) moves *today's* state one step along its `worse` or `better` link for the
rest of the day. Chapter 02's *weather-ache* reveals the day's rolled weather at each `day` boundary after
this handler (02's request): it reads `weather.today` at step 4, and if the holder's knack covers
foresight, `weather.tomorrow`.

**10.11.4 Lying snow, high water, drought.** `[D]` Three standing facts carry weather across days: **`snow_lying`**
(set by a snow or blizzard day at freezing or colder; cleared after two consecutive days of states warmer
than `frost`): off-road pace one more step slower, tracks plain (trailing Easy), forage one tier harder;
**`high_water`** (set by a storm or thunderstorm day, or two consecutive rain days, on every river link
of the region; cleared after two dry days): fords one rung more severe (10.12), river travel downstream
+2 points, upstream −2; **`drought`** (set by five consecutive heat or scorching days; cleared by a rain
day): `water_source` false on streams and springs not marked perennial, forage one tier harder.

**10.11.5 Reading the weather ahead.** `[D]` *Anchor: yes.* **Read the weather** (one interval at dusk or
dawn, outdoors): verb.observe, Wits, `deed.wilds.survival.weathersense`, licensed by
`lic.training.wilds_survival` ("read weather a day ahead"); Easy, Safe; reach ≥ 1 unseals
`weather.tomorrow` for the PC. Without the license it is G3; the redirect names asking a local (verb.talk:
shepherds, fishers and farmers know their sky), 02's weather-ache, or waiting. *Knobs:* dc (Easy → Moderate
in an unfamiliar climate); time_cost; targets (tomorrow → the next three days at a tier harder each).

**10.11.6 Sheltering.** `[D]` Shelter negates weather exposure for the watches spent in it: a building, a
tent (`item.tool.container`'s tent entry, 08), a cave or overhang (a feature or landmark), a covered
vessel, a snow hole dug (verb.handle under `lic.training.wilds_survival`, 1 interval, Moderate; fallback:
a crude lean-to, Handle +5 Limited, which shelters from rain and wind but not from blizzard or bitter
cold), or the opportunity face's shelter. A camp with a **fire** negates `haz.cold` and `haz.bitter_cold`
for its sleepers (not `haz.blizzard`, which only shelter answers). *Narration may not imply* shelter that
no fact records [R4 §9 10 item 1].

### 10.12 Hazards

**10.12.1 The hazard entry.** `[D]` A **hazard** is a source of harm in the environment that no one aims:
weather, falls, water, fire, bad air, collapse, deprivation, sickness in the land, and places where magic
is wrong. Chapter 10 owns every hazard entry (`data/hazards.yaml`; 00.17.1 Q18); chapter 07 owns what the
harm does (07.10). Each entry is data (SCHEMAS `hazards.yaml`, with this chapter's optional fields):

```yaml
Hazard:
  id: haz.*
  terrain_tags: [tag]          # where it is found (empty: anywhere)
  harm_tags: [tag]             # harm.* (cascade applies to resistances, 00.10.5)
  severity: S1..S5             # fixed, or by_band: [S?, S?, S?, S?, S?] for band-scaled hazards
  resist: {verb: endure|evade|exert|none, attribute, dc_tier|effect_dc, stakes: risky|dire}   # 01's request
  cadence: enum                # exposure (once per entry) | round | interval | watch | day
  conditions: [effect_ref]     # on a failed resist (07.10.1)
  affliction: aff.*|null       # an exposure to this affliction instead of, or besides, harm (07.9.2)
  no_reduction: bool           # falls, want, drowning, choking, cold, heat, magic: true (07's request)
  perceived_on_sight: bool     # 07's request: whether perceiving the place perceives the hazard
  signs: [str]                 # >= 2 perceivable signs (what the narrator shows before it bites)
  omens: [str]                 # for hazards that approach (avalanche, flood): the stirring of it
  lethal_context: bool         # 07.3.3 "hazard" row
  aftermath: str|null          # where a PC put Down by it ends up (07's request)
  protections: [{means, effect}]   # what steps it down or negates (shelter, fire, rope, gear, a license)
  pace_steps: int              # slows travel through it (10.3.2)
  feature_kind: hazard         # 06.3.8: usable in a fight (Force a foe into it; periodic harm)
  avoid: [str]                 # verbs that get round it (the anchor's knobs)
```

**10.12.2 Exposure.** `[D]` An **exposure** happens when a character enters a hazard, or at each boundary
of its cadence while the character remains in it (`h.10.watch_exposure`, `watch`, phase 2;
`h.10.site_exposure`, `interval`, phase 2; conflict rounds by 06's `h.06.ongoing_harm` for a hazard
feature). Each exposure is chapter 07.10.1's procedure: the exposed character makes the entry's resisted
check (`resist`; the effect DC is the tier matching the severity unless the entry lists one), reading
01.18.3's table unless the entry has its own; a failure deals the hazard's harm at its severity
(`apply_harm`, `no_reduction` per the entry, `periodic: true` after the first), then its conditions or
affliction exposure. Protections apply first: each cited `protections` row steps the severity down one
rung or negates the exposure (`eff.hazard_step` from items and abilities counts the same way, at most
two steps in all, 00.10.4 E2). Stakes follow the severity (S1–S2 Risky, S3+ Dire); a lethal frame needs
the entry's `lethal_context` and the warning taken effect (07.3.5–07.3.6).

**10.12.3 Continuing hazards and the choice to leave.** `[D]` + `[T]` A hazard with a cadence of `round`,
`interval` or `watch` keeps exposing until the character leaves it; its handler `interrupts` time after the
first exposure (10.9.8) so the player can choose to get out. Leaving a hazard is a Move (Evade if it is
rushing at you; Exert if it holds you: a mire, a current) at the entry's tier. *Certain with cost* (01.4.5)
applies when there is no way to avoid an exposure the method requires (wading the freezing ford): no roll,
the hazard's harm is the method consequence.

**10.12.4 Seeing it coming.** `[D]` + `[N]` Every hazard has **signs** (its look: the ford's speed, the
scree's looseness, the bog's green skin) and, if it approaches, **omens** (the avalanche's crack, the
river's rising roar). When a hazard is in a place the PC enters and its `perceived_on_sight` is true (in
light enough to see it: 10.7.3), its sign is narrated on entry (write-on-mention: a feature with the
hazard id). A hazard of S4 or S5 raises 07's `severity` warning when perceived, and an entry with
`lethal_context: true` raises the `hazard` warning when the PC is about to enter it (07.3.3) — so a
hazard that can kill always speaks first. Hidden hazards (`perceived_on_sight: false`: bad air, thin ice
under snow, a quicksand crust) are found by passive notice (01.4.6) against their detect tier or by
Observe, and until perceived cannot be lethal (07.3.5): they can put a character Down, never kill
[BRIEF §4; DL-10-11].

**10.12.5 Falls.** `[D]` Falls are 07.10.3's and 06.5.8's: **10 ft S2, 20 ft S3, 40 ft S4, 80 ft or more S5**,
`harm.physical.crush`, no reduction, the faller `cond.prone`. This chapter adds the heights' places in
exploration: every `height` feature, cliff, shaft and drop records its height in feet when mentioned
(10.1.4); a height of **20 ft or more** is a **Heavy (S3) source** for 01.6.9's stakes test (Dire) — 01's
and 12's request; a height of 40 ft or more beside or beneath the PC is a `severity` warning source when
perceived (07.10.3). A **climb** that fails partway (reach 1 delivered, then a failure on the next pitch, or
a failure on a single climb) falls from the height reached: the engine takes the recorded height of the
pitch × the fraction climbed (a reach-1 delivery means half), rounded down to the ladder's step below. A
rope tied off (a fact) is a Protective lever (stakes −1) and limits a fall to the rope's slack (10 ft, S2).
`haz.fall_10`, `haz.fall_20`, `haz.fall_40`, `haz.fall_80` are the data entries.

**10.12.6 Water and breath.** `[D]` Swimming is verb.exert (Might, or Endurance for distance), against the
water's tier: calm Easy, a current Moderate, a river in spate Hard, a sea swell Hard, a whirlpool or weir
Very hard. A failure in moving water is `haz.swift_water` (S3, `harm.physical.crush`, swept one link
downstream: its `aftermath`), in deep still water a failure is going under (07.10.4: breath for 6 rounds +
2 per Endurance point, then `cond.choking`). Armor makes swimming worse: medium armor an engine-cited
Precision snag, heavy armor G4 for swimming (the redirect: shed it, 1 round per load unit of armor, or
cross another way). Cold water adds `haz.cold_water` (S2, per interval immersed). Drowning and smoke use
07.10.4 exactly (07's request).

**10.12.7 Sickness in the land.** `[D]` Some places carry **disease vectors** as hazards whose effect is an
affliction exposure (07.9.2) rather than harm: `haz.marsh_miasma` (a day in fen or swamp in the warm
seasons without precautions: exposure to `aff.marsh_fever`), `haz.foul_water` (drinking from water marked
foul: `aff.red_flux`), `haz.barrow_air` (a night spent inside a barrow or crypt: `aff.grave_chill`),
`haz.vermin_nest` (sleeping among vermin, or an area of a sewer or warren: `aff.rat_plague`),
`haz.spore_cloud` (disturbing a fungal growth: `aff.grey_spore`). Precautions (smoke and nets against
insects; boiling water; sleeping outside the barrow) are listed in each entry's `protections`, and each
negates its exposure. The vector is written on the place (`place.hazards`) and shown on entry by its signs
(the whine of midges, the green scum, the cold that lingers in the stones).

**10.12.8 Places where magic is wrong.** `[D]` Magical zones are hazards with harm, dread or rule effects:
`haz.desecrated_ground` (a dread exposure S1 per day spent there, 07.11.2; divine workings take 05's snag),
`haz.dead_ground` (no harm; the fact `dead_ground` makes primal workings G4, 05.7.2; Focus does not return
at a breather there), `haz.wild_magic` (each arcane or primal working cast there rolls d20: on 1–3 an
`haz.arcane_surge` exposure, S3 `harm.arcane.raw`, to the caster), `haz.fey_crossing` (way-finding in it is
Very hard; a night spent asleep there: an Endure (Resolve) Moderate or wake a day later, the world having
run), `haz.haunting` (a dread exposure S2 at each night watch, 07.11.2; `harm.mind.strain` tagged),
`haz.blight_zone` (`harm.blight.decay` S2 per day exposed; supply carried spoils one a day), and
`haz.ward_line` (a standing ward: crossing it is an exposure at its rite's tier, its harm per the rite, 05).
Each carries signs (the grass grey in a ring, the silence of birds, a cold that has no source) and is
written on its place.

**10.12.9 A hazard no one listed.** `[J:rung]` A source of harm with no entry is rated with chapter 07's
anchor **07.10.2** (hazard severity by what it would do to an unprotected adult; harm tags by what it is;
effect DC by the rung; the rating stored on the source). This chapter adds only the **cadence** knob's
choice: `[J:enum]` *exposure* (it harms once, on contact: a falling beam), *round* (it keeps harming in a
fight: a burning floor), *interval* (it harms while one stays in it in a site: smoke in a corridor),
*watch* (it harms while one travels or camps in it: a hot wind). Uncertain → the shorter cadence (the
player can leave sooner). *Worst case:* one cadence step too long — one extra exposure before the player
can act, never lethal without a warning on record (class i).

**10.12.10 Aftermath.** `[D]` When a hazard puts a PC **Down** (07.2.9), the entry's `aftermath` says where
and how the character comes to: `haz.swift_water` "washed ashore at the next link downstream, gear wet,
one carried item lost (engine's draw)"; `haz.avalanche` and `haz.cave_in` "buried: Down until dug out —
a companion's three Force beats (Moderate) or the PC's own Endure each hour (Hard) from beneath"; `haz.blizzard`
"wakes under the snow at the next dawn with one more `cond.exhausted` stack"; and so on. Chapter 07's
`leave` disposition applies to whatever else would find the character (07.6.1).

**T-10-14 The hazard index** (`data/hazards.yaml`; each row's full data, signs, protections and
aftermath are there).

| Id | Severity | Resist | Cadence | Lethal ctx | Perceived on sight | Notes |
|---|---|---|---|---|---|---|
| haz.cold | S1 | Endure (End.) Easy | watch | no | yes | freezing nights without fire or shelter; warm gear −1 rung |
| haz.bitter_cold | S3 | Endure Hard | watch | yes | yes | + `cond.exhausted` on a failure; fire or shelter negates |
| haz.blizzard | S3 | Endure Hard | watch | yes | yes | only shelter negates; way-finding Very hard snags |
| haz.heat | S1 | Endure Easy | watch (day) | no | yes | travel or labor by day; shade negates |
| haz.scorching_heat | S3 | Endure Hard | watch (day) | yes | yes | + exhausted on failure; resting in shade negates |
| haz.storm_exposure | S2 | Endure Moderate | watch | no | yes | rest at best partial |
| haz.lightning | S4 | Evade Very hard | watch | yes | yes | only on heights or open ground in a thunderstorm |
| haz.storm_at_sea | S3 | Exert Hard (keep aboard) | watch | yes | yes | failing: overboard (`haz.open_water`) |
| haz.thin_air | S2 | Endure Moderate | watch | no | no | above the tree line on high peaks; + exhausted |
| haz.fall_10 / _20 / _40 / _80 | S2 / S3 / S4 / S5 | none (falling rolls nothing) | exposure | no / no / yes / yes | yes | 06.5.8, 07.10.3; 20 ft+ is a Heavy source |
| haz.rockfall | S3 | Evade Hard | exposure | no | yes | omen: pebbles skittering |
| haz.avalanche | S5 | Evade Legendary | exposure | yes | yes (slope) | omens: a crack, a hush, a rumble |
| haz.cave_in | S4 | Evade Very hard | exposure | yes | no | omens: dust sifting, timbers groaning |
| haz.scree | S2 | Exert Moderate (footing) | exposure | no | yes | a slide 10 ft; pace −1 |
| haz.mire | S2 | Exert Moderate | interval | no | no | `cond.restrained` while held; slow drowning if alone |
| haz.quicksand | S3 | Exert Hard | round | yes | no | then breath (07.10.4) |
| haz.thin_ice | S2 | Evade Moderate | exposure | no | no | then `haz.cold_water` |
| haz.cold_water | S2 | Endure Moderate | interval | no | yes | immersion |
| haz.swift_water | S3 | Exert Hard | round | yes | yes | swept downstream (aftermath) |
| haz.ford | S2 (S3 in high water) | Exert Moderate (Hard) | exposure | no (yes in spate) | yes | crossing a river on foot or horse |
| haz.open_water | S3 | Exert Hard | interval | yes | yes | in the sea or a great lake |
| haz.drowning | per 07.10.4 | Endure | round | inherits | yes | breath rule |
| haz.smoke | S1 | Endure Easy | round | no | yes | `cond.choking` per 07.10.4 |
| haz.fire | S2 / S3 (room) / S4 (inferno) | Evade | round | S4: yes | yes | `cond.burning` |
| haz.wildfire | S3 | Evade Hard | interval | yes | yes | omens: smoke on the wind, fleeing beasts |
| haz.lava | S5 | Evade Legendary | exposure | yes | yes | |
| haz.bad_air | S2 | Endure Moderate | interval | no | no | `harm.venom.gas`; lights burn low (a sign) |
| haz.firedamp | S4 | Evade Very hard | exposure | yes | no | an open flame in bad air: explosion |
| haz.darkness | — | — | — | no | — | not harm: 10.7.3's rules, listed for retrieval |
| haz.starvation | S3 per stack past 3 | none | day | yes (after warning) | — | 07.8.10 want; `h.10.supply` |
| haz.thirst | as starvation | none | day | yes (after warning) | — | arid need, 10.6.2 |
| haz.marsh_miasma | aff.marsh_fever | Endure (exposure) | day | (affliction's) | yes | warm seasons; smoke and nets negate |
| haz.foul_water | aff.red_flux | Endure | exposure | (affliction's) | no | boiling negates |
| haz.barrow_air | aff.grave_chill | Endure | night | (affliction's) | yes | sleeping outside negates |
| haz.vermin_nest | aff.rat_plague | Endure | night | (affliction's) | yes | |
| haz.spore_cloud | aff.grey_spore | Endure | exposure | (affliction's) | yes | a cloth over the mouth −1 rung |
| haz.desecrated_ground | dread S1 | Endure (Resolve) | day | no | no | divine snag |
| haz.dead_ground | — | — | — | no | no | primal G4 |
| haz.wild_magic / haz.arcane_surge | S3 | Endure Hard | per working | no | no | 1–3 on d20 per working |
| haz.fey_crossing | — | Endure (Resolve) Moderate | night | no | no | lose a day |
| haz.haunting | dread S2 | Endure (Resolve) | night | no | no | |
| haz.blight_zone | S2 | Endure Moderate | day | no | yes | supply spoils |
| haz.ward_line | per rite | per rite | exposure | per rite | no | 05's rites |

### 10.13 Sites: the delve

**10.13.1 What a site is.** `[D]` A **site** is a place explored area by area rather than crossed: a barrow, a
ruined keep, a cave system, a drowned temple, a wyvern's crag, a bandit warren, a sewer under a town. It is
an entity with `place_kind: site` and a **site record** (10.13.3). Entering it changes the mode to `site`
(T-12-3): each significant beat is one interval (10.13.5), the time-tick die rolls on the site's cadence
with the site's faces (10.9.3–10.9.4), and two clocks race — the **progress clock** toward the site's
heart and the **danger clock** of the site waking (10.13.8). The procedure is Ironsworn: Delve's, rebuilt on
this ruleset's frame and clocks: a site is a **theme × domain** pair; areas are generated when explored;
the approach chosen sets the risk; dangers and discoveries come from the two cards; the heart is located
when progress completes [R5 P-28; R: https://tomkinpress.com/pages/ironsworn-delve].

**10.13.2 Themes and domains.** `[D]` A **theme** says what *happened* to the place and what it has become;
a **domain** says what *kind* of place it physically is. Each is a card in `data/sites.yaml`; the pair
gates everything found inside, so 8 themes × 14 domains give 112 kinds of site from 22 cards (C:V).

| Theme (`site.theme.*`) | What it means | Default danger | Gates (denizens) | Place facts |
|---|---|---|---|---|
| ancient | forgotten by all; old works and old guardians | wild | construct, spirit.ancestor, undead.mindless, beast.vermin | — |
| corrupted | twisted by dark power | perilous | fiend, undead, horror, folk (cultists) | `desecrated` |
| fortified | held and defended by those within | wild | folk (soldiers, brigands, orcs, goblins), beast (war-hounds) | — |
| hallowed | holy, or once holy, guarded by its faith | settled | spirit.celestial, spirit.ancestor, construct, folk (wardens) | `consecrated`; `resonance` the keeper's axes |
| haunted | the dead do not rest here | perilous | undead.spectral, undead, spirit.ancestor | `haunted` |
| infested | overrun by creatures that breed | wild | beast.vermin, beast.predator, horror (ooze, fungal), folk.goblin | — |
| ravaged | broken by war, fire or disaster | wild | beast (scavengers), folk (looters), undead.ravenous | — |
| wild | taken back by nature and the primal world | wild | beast, spirit.fey, spirit.place, horror.plant | `resonance` primal |

| Domain (`site.domain.*`) | Terrain tags | Light | Explore tier | Typical size | Rest site |
|---|---|---|---|---|---|
| barrow | terrain.ruin.tomb.barrow | dark | moderate | small | rough |
| crypt | terrain.ruin.tomb.crypt, .catacomb | dark | moderate | medium | rough |
| cavern | terrain.underground.cave | dark | moderate | medium | rough |
| flooded cave | terrain.underground.cave.flooded | dark | hard | medium | rough |
| mine | terrain.underground.mine | dark | moderate | medium | rough |
| warren | terrain.ruin.dungeon.warren, terrain.underground.tunnel | dark | hard | large | rough |
| underkeep | terrain.ruin.dungeon, .vault | dark | moderate | large | rough |
| temple | terrain.ruin.temple | dim | easy | medium | camp (secured) |
| stronghold | terrain.ruin.fortress | dim | easy | large | camp (secured) |
| tower | terrain.ruin.fortress | dim | moderate | small | camp (secured) |
| sewer | terrain.underground.sewer | dark | moderate | medium | rough |
| tanglewood | terrain.forest.deepwood.tangle | dim | hard | medium | rough |
| fen | terrain.wetland.fen, .marsh | bright | hard | medium | rough |
| icereach | terrain.frozen.glacier | bright | hard | medium | rough |

Each card holds (`sites.yaml`): `terrain_tags`, `creature_gate_tags` and `creature_weights` (which
denizens live there), `loot_gate_tags` (08.3.4 item 4: the place axis of the loot pool gate), `features`
(d12, the look of an area), `dangers` (d12, what a danger result becomes), `discoveries` (d6),
`shift` (d6, the H face), `hazards` and `traps` (weighted lists), `climax` (d6, what guards the heart;
themes), the danger clock's `omens` (themes), `regrowth` (themes), and the place facts above. Chapter 13
may add regional cards in the owner-block and must set any site's theme, domain, band and size it places
by hand; a site generated in play takes them from the region's site tables (`tbl.<region>.sites`, else
`sites.yaml#site_generation`).

**10.13.3 The site record.** `[D]`

```yaml
SiteRecord:
  theme: site.theme.*
  domain: site.domain.*
  band: 1..5                 # threat band of its denizens; tier cap of its loot (08.3.5)
  size: small | medium | large | vast
  danger: settled | wild | perilous | deadly   # from the theme (10.13.2), +1 rung at band 4-5 (cap deadly)
  explore_tier: easy | moderate | hard | very_hard   # domain's, +1 rung at band 4-5; stored (00.3.8)
  progress_clock: clk.*      # "The heart of <site>", public (10.13.8)
  danger_clock: clk.*        # "<site> wakes", sensed (10.13.8)
  objective: {kind, ref, sealed: bool}   # 10.13.10; authored by 13 or rolled from the theme's climax
  areas: [place_id]          # every area generated, in order
  frontier: place_id         # the deepest area reached on the main way
  path: [place_id]           # the known way from the entrance to the frontier
  side_areas: [place_id]     # branches off the main way (10.13.6 contents 10)
  secured: [place_id]        # areas made safe to rest in (10.13.11)
  denizens: [{id, area, status: unaware|aware|alarmed|fled|defeated|gone}]
  traps: [{id, area, state: hidden|perceived|disarmed|spent|reset}]
  roused: bool
  entrances: [place_id]
  last_left: time|null
  state_log: [{at, change}]
```

Sizes fix the clocks (`sites.yaml#sizes`): **small** progress 6 / danger 8; **medium** 8 / 8; **large** 12 /
12; **vast** two progress clocks of 12 in sequence ("the halls", then "the deep", linked: the first's
completion creates the second) with a danger clock of 12.

**10.13.4 Entering a site.** `[D]` When the PC enters a site (by its entrance link or a found way in):
1. `h.10.scene_frame` marks `mode_change` to `site`; the site record is created if new (PR-10-6: theme,
   domain, band, size, clocks, objective; the denizen table is built), else loaded.
2. The **entrance area** is generated (10.13.6) or loaded; its feature and the theme's first sign are
   narrated (a hallowed temple's broken bell; a corrupted mine's smell of burnt hair).
3. The **site OFFER** is shown out of fiction (no die): theme and domain in words, the band word against
   the PC's (`[WARNING]` lines as 10.3.4's when the band is higher), the light needed (dark domains), what
   is known of the heart (rumors, maps), and the two clocks: progress shown, danger "sensed" (it exists; its
   fill is not shown).
4. Site checks begin counting intervals (10.9.3); `h.10.light` burns lights by the interval (10.7.1).

**10.13.5 Site time.** `[D]` Handler `h.10.site_time` (`beat_end`, phase 9): in `site` mode, each
**significant** beat advances **1 interval** (00.7.3), and activities with a listed duration (T-10-20)
advance theirs instead (a careful Explore onward is 2; a short rest 6; a long rest a watch). A beat is
significant when it resolved a check (a frame was rolled or taken with time) or performed a listed
activity; talk, free activities (00.12.6), casual looking (01.4.6) and out-of-fiction questions are not.
A conflict inside a site takes the time of its rounds, rounded up to 1 interval at `conflict_end`. A party
makes **one** significant beat per interval: an ally's beat is made in the PC's place, never beside it
(16.8.2) [integration: IR ch.16 to 10 (c)].

**10.13.6 Explore onward.** `[J:enum]` + `[D]` *Anchor: yes.* The Delve move: go deeper toward the heart.

```
### 10.13.6  Explore onward                                       [J:enum] [D]
Trigger [T]:        in site mode, the player declares going on, deeper, further, onward, or toward the
                    heart (not into a known area: walking known ground is 10.13.11's traversal)
Loads in:           situation.exploration.*
License check:      basic verbs (G1): verb.observe (care), verb.sneak (stealth), verb.move (haste)
Decisions (J):      1. APPROACH [J:enum] from the method as described:
                       CARE - looking, testing, checking corners, sounding floors. True when the
                         method dwells on noticing; false when it dwells on speed or silence.
                       STEALTH - keeping quiet, keeping to shadow, staying unseen. True when the
                         method dwells on not being noticed.
                       HASTE - pushing on fast, running the corridor, getting through before
                         something happens. True when the method dwells on speed.
                       Uncertain -> CARE (the slowest, least risky reading; the OFFER shows it).
Computation [D]:    CARE: verb.observe, Wits, primary tag deed.lore.investigation.search (built
                      domains) or deed.wilds.navigation.underways (natural caves, tanglewood, fen,
                      icereach); 2 intervals; threatened cost cost.time (feeds the danger clock).
                      On success the new area's traps and hidden hazards are perceived at once
                      (care reads telltales).
                    STEALTH: verb.sneak, Agility, deed.guile.stealth.sneaking; 1 interval; threatened
                      cost cost.exposure. On success denizens in the new area are unaware (06.2.4).
                      Not with an unshuttered light (10.7.3: G4; redirect: shutter it or go by care).
                    HASTE: verb.move, Agility, deed.martial.athletics.running; 1 interval; framed
                      reach GREAT; trait.sense.loud (the danger clock ticks 1 whatever the degree);
                      threatened cost cost.footing. Traps and hidden hazards in the new area are met
                      only by passive notice (01.4.6).
                    DC: the site's stored explore_tier. Stakes RISKY (the danger clock listens: a
                    running clock is a cost source, 01.6.9); DIRE where the area being entered holds a
                    perceived S3+ hazard on the way. Reach STANDARD (GREAT for haste).
                    Delivered reach -> progress clock ticks (00.8.2). Reach >= 1 enters a NEW AREA on
                    the main way (PR-10-7): it becomes the frontier. Reach 0 (failure): no new area
                    (a wrong turn, a dead end), and the READ cost. Critical success: also roll
                    tbl.10.site_opportunity.
                    In darkness without light or night-sight: CARE by touch only (an engine-cited
                    Precision snag, reach capped Limited); STEALTH and HASTE are G4 (redirect: light,
                    or by touch).
Stakes:             RISKY (DIRE per above)
State writes:       progress clock; new area entity; site.frontier/path; costs; danger clock ticks
Narration may not imply: an area, exit or denizen the generation did not write; progress in words
                    beyond the clock ("you sense the heart is near" only when the clock is at or
                    past its last quarter)
Worst case (J):     APPROACH misread: the other approach's tick, interval or cost profile for one beat
                    (one interval, one tick, or one cost form; class i), shown in the OFFER first
Examples:           inside CARE: "I go on slowly, tapping the floor with my spear." inside STEALTH:
                    "I slip along the wall with the lantern hooded." inside HASTE: "We run for the
                    stair before the water rises." boundary: "I move on quickly but quietly" ->
                    the method names both; the player picks at OFFER, default CARE.
                    non-example: "I explore the whole floor" -> a compound of many beats (01.2.3):
                    one Explore onward at a time, each its own area.
Anchor:             yes. Intent verbs: explore, delve, press on, go deeper, find the way in, push
                    through. Knobs: dc (explore tier -> stored area tier); attribute (Wits /
                    Agility); time_cost (1 interval -> 2 for care); reach_unit (progress ticks);
                    stakes. Adapts to: searching a burning town for a person (progress toward the
                    person, the fire as the danger clock); crossing a besieged city's streets;
                    working through a hedge maze.
Basis:              [R5 P-28 (Delve the Depths: edge / shadow / wits)] [R5 P-13] [01.14.6] [DL-10-14]
```

*The race, simulated* (`sim10_site2.py`, 20,000 delves per cell; one Explore onward and one other
significant beat per area, the other beat succeeding three times in five; failures and exposure costs
tick the danger clock; site checks at wild cadence; fights tick it once). For a **medium** site (progress
8, danger 8) entered by a PC whose explore modifier is +5 against Moderate (15): the danger clock completes
first in **25%** of careful delves, 21% of stealthy ones and 36% of hasty ones, after about 9–10 beats and
13 intervals (stealth 9 intervals, haste 6); at +9 it is 4% / 3% / 9%; at +3, 46% / 42% / 54%. A small site
(6/8) rouses 12% of the time, a large one (12/12) 26%. A roused site is not a defeat (10.13.9): it is the
place turning on the intruder, which a strong or lucky delver still survives — so about one careful delve in
four ends with the place awake and the heart still ahead, the tension Delve's menace track gives.

**10.13.7 New areas.** `[D]` When Explore onward delivers reach ≥ 1, or the PC enters an unexplored side
passage, the engine generates the area (PR-10-7) and writes it before narration:
1. **Feature**: `roll_table` on the domain's `features` (d12): what the area looks like and what is in it
   that could be used (each written as a feature with 06.3.8's `feature_kind` where it has one: a gallery is
   a `height` with its drop in feet, a fallen pillar is `cover`, a flooded floor is `difficult_ground`).
2. **Contents**: `roll_table(tbl.10.area_contents)` (d12): **1–3** nothing more; **4** a discovery (theme or
   domain `discoveries`); **5–6** denizens — the site denizen table (10.13.13) drawn as a time-tick
   encounter: a pending threat arrives here if one is pending; otherwise a threat row becomes pending and
   this area shows its sign (droppings, a cold hearth, scratches, a stink) — the omen-first rule holds inside
   sites too; a non-threat row is here; **7** a trap (the domain's trap list, theme-weighted; 10.14); **8** a
   hazard (the domain's hazard list); **9** an obstacle on the way on (a barrier: a stuck or locked door, a
   rubble choke, a gap with a recorded drop; stored tier by the site's explore tier); **10** a branch (a side
   passage: a new `passage` link to a side area; side areas do not advance progress, roll contents with +2,
   capped at 12); **11** a cache (08.3.12's hoard at site band − 1, coin and goods only, or `generate(gen.loot,
   place, scavenged, degree of the search)` for one item when found by a Search beat); **12** a theme danger
   (`roll_table` on the theme's `dangers`).
3. **Exits**: one link onward (unexplored), the link back, and any the feature implies.
The area is `discovered` with the Explore beat's frame id (10.1.5). Every element named is written
(10.1.4). The DM chooses words; the tables chose things.

**10.13.8 The two clocks.** `[D]` Created at the site's first entry from `sites.yaml#clock_templates`:
- **The progress clock** "The heart of <site>" — kind `progress`, **public** (the player sees how far in
  they are), segments by size (10.13.3); tick sources: Explore onward's delivered reach; the opportunity
  rows "a clue toward the heart" and "a short way" (+1 each); a map of the site found or bought (+2 once,
  a fact); defeating a **gatekeeper** denizen placed by a theme danger result (+1). It never ticks down
  during a visit.
- **The danger clock** "<site> wakes" — kind `danger`, **sensed** (00.8.4: known to exist, fill hidden;
  each tick renders one omen of its stage from the theme's list, INV-14), segments by size; tick sources:
  `trait.sense.loud` beats (1), `cost.exposure` (U(severity)), `cost.time` (U(severity)), the site check's
  **S** face (1), `conflict_start` inside the site (1), a trap or alarm that sounds (its listed ticks);
  `decay`: −2 at each `day` boundary on which it did not tick (the site settles while the PC is away);
  `links`: at **half**, roll the theme's `dangers` once (a danger is written: a patrol becomes a pending
  threat, a door is barred, a hazard is set off — the place reacting); `on_complete`: the site is **roused**
  (10.13.9), `interrupting: true`, `then: reset` (it may fill again: the second time, the guardian comes
  for the PC, 10.13.9).
The clocks race (00.8.5) only in this sense: completing the progress clock first does not void the danger
clock — the heart is found, and the place is still waking on the way out (`races_with: null`; DL-10-15).

**10.13.9 Roused.** `[T]` + `[D]` When the danger clock completes: `site.roused = true`; the site's danger
rating counts one rung higher (cap deadly) and its cadence becomes every interval (10.9.3); every
unaware denizen becomes alarmed (alertness, 15); the theme's **climax** guardian (or the objective's own
keeper, 10.13.10), if not met, becomes a **pending threat** with `sign_stage: 2` — the PC hears it coming
(its sign is mandatory now) and it arrives on the next E or O face or the second check. Roused is cleared
when the danger clock decays to half or below (days away). If the danger clock completes a **second** time
in one visit, the guardian arrives at once (at `band.near`, the PC side aware: it was heard). If the
guardian's archetype carries `lethal_context` (09) the lethal warning is due at the imminent stage of the
danger clock (PR-00-3 step 3; 07.3.3 `clock` row) — the place's waking can kill, and the player is told
before it does.

**10.13.10 The heart.** `[D]` When the progress clock completes, the next area generated is **the heart**:
the objective the site holds. It is authored by 13 for placed sites, or rolled once at the site's creation
from the theme's `climax` (d6) and sealed until reached. Objective kinds (closed): **hoard** (08.3.12's hoard
at the site band, the place as its source: its domain terrain tags and its theme's loot tags gate the pool,
08.3.4 item 4; circumstance `decisive` if its keeper was defeated by the PC, else `scavenged` with the search
beat's degree); **guardian** (a solo, or an elite with a lower-band mob, of the theme's climax archetype at
site band — never two equal individuals at bands 4–5, 09.8.1 — and the advisory is computed and shown
before the first beat); **sealed way** (a barrier at the site's explore tier + 1 rung, with the hoard or the
objective behind it); **rite in progress** (a cultist rite or a waking: a countdown clock of 4 racing the PC,
05's rite as its content); **the lost** (a captive, a body, a relic someone wants, a thread's object, 11);
**a place of power** (a spring, an altar, a tree: `resonance` written; 04's V11 and 05's resonant rest read
it; a cleansing or consecration may be done here); **a way through** (the site was a pass: the far exit opens
a route link). A site may hold several objectives (13); the progress clock leads to the first, and a further
objective is a new progress clock of the site's size − 2 (minimum 4), linked from the first.

**10.13.11 Retreat, rest and return.** `[D]` *Anchor: yes (retreat).*
- **Walking known ground**: moving along the site's `path` between known areas takes **1 interval per 2
  areas** (rounded up), with no Explore beat; site checks run. Leaving from the frontier therefore takes
  half the areas' count in intervals; a map of the site (made by the Map activity, T-10-20, or found)
  halves it again (rounded up).
- **Escape**: when the site is roused and a pending threat or an encounter is on the PC, leaving is a
  chase (06.12) whose ground is drawn from the domain's features, with `clk.escape` sized 4 + 1 per 4 areas
  of path (max 8): the place itself is the pursuer's ally.
- **Resting inside**: a site area's `rest_site` is `rough` unless **secured** (a barricaded room or a secure
  corner: Handle or Force to bar the way, 1 interval, against the site's explore tier; or the opportunity
  face): a secured area is `camp` while the danger clock is not imminent (07.8.2). A short rest is 6 intervals
  of site checks; a long rest a watch (36 intervals: 12 to 36 checks): resting in a delve is possible and
  dangerous, exactly as it should be (07.8.12).
- **Return**: a site left and re-entered keeps its record. On re-entry, for each **full week** since
  `last_left` the progress clock loses **1 segment** (collapses, new barricades, the way half-forgotten),
  to at most half its filled segments, never below the number of `secured` areas on the path; the danger
  clock has decayed by its daily rule; **regrowth** (`h.10.site_regrowth`, `week`, phase 6): for themes with
  `regrowth` (corrupted and infested on 5–6, haunted, ravaged and wild on 6; T-10-18), each cleared area on the path rolls d6 and on
  the theme's regrowth range something moves in (a denizen row is written there as pending: its sign will
  show on arrival). Defeated denizens stay defeated; disarmed traps stay disarmed unless the theme resets
  them (fortified: the garrison re-arms one trap a week).

**10.13.12 What persists.** `[D]` Everything written in a site stays written: areas, features, exits, the
path, opened and broken doors, triggered and disarmed traps, the dead and the fled, the hoard taken, the
heart's state. `state_log` keeps each change with its time. A site cleared of its denizens and its objective
is written `cleared` (11 may give it to a faction, a squatter or a new occupant at a World Turn — never by
narration). A PC may make a cleared site a holding through 11.

**10.13.13 Who lives there: the site's denizen table.** `[D]` A site's encounter table is built once, at
creation (PR-10-6), and stored on the record: the archetypes whose `creature_tags` match the theme's
`creature_gate_tags` (00.5.4c) and whose `encounter.terrain` includes one of the domain's terrain tags
(or an ancestor), weighted by the theme's `creature_weights`, fielded at the site's band by 10.10.1–10.10.2
(home band = the site band; 30/55/15 across band − 1 / band / band + 1; crowds as mobs). Thirteen's
authored sites may give their own table. This is constitution P5's pool gate applied to where creatures
live: the theme × domain pair is what fundamentally characterizes the place, so it gates what is met, what
is found and what can be harvested — the same pair gates the place-gated loot (08.3.4 item 4) and the
hoard (08.3.12) [C:P5; R2 #13; R5 P-28].

**10.13.14 Many sites, one procedure.** `[N]` A lair in the wild (a wyvern crag), a building in a town (a
merchant's house broken into at night), a ship's hold, a besieged keep — each is a site with a theme and a
domain, small, its clocks sized by 10.13.3. A settlement building searched room by room uses the site
procedure with `fortified` or `ravaged` and the stronghold or tower domain (T-12-3's "room-by-room search").

### 10.14 Traps

**10.14.1 The trap entry.** `[D]` A **trap** is a made thing that harms or holds whoever trips it (`data/
traps.yaml`; SCHEMAS `traps.yaml` plus this chapter's optional keys):

```yaml
Trap:
  id: trap.*
  kind: mechanical | magical | natural_snare | alarm
  trigger: str                       # what sets it off (a plate, a wire, a lid, a word, a light)
  telltale: str                      # 10.14.3: what is always visible
  detect: {verb: verb.observe, dc_tier_by_band: [5 tiers]}       # concealment of the mechanism
  disarm: {license: lic.*, verb, dc_tier_by_band: [5 tiers]}     # 01's request shape; G3 fallbacks below
  resist: {verb: evade|endure|exert, attribute}                  # the victim's resisted check
  harm: {severity_by_band: [S?, S?, S?, S?, S?], harm_tags: [tag]}
  effects: [effect_ref]              # conditions, holds, afflictions, an alarm tick
  alarm_ticks: int                   # ticks on the site's danger clock when it fires
  reset: once | manual | automatic
  bypass: [{method, verb, tier_delta}]   # the anchor's creative ways round (10.14.5)
  lethal_context: bool               # true when its S4+ harm can kill (perceived: 07.3.3)
  aftermath: str|null
```

**10.14.2 Where traps are.** `[D]` Traps are placed by 13 in authored sites, by the area-contents roll
(10.13.7 result 7), by a theme danger, or by a denizen's behavior list (a goblin warren's snares). A trap's
exact position and nature are **sealed** (00.6.5) until perceived; its **telltale** is not (10.14.3).

**10.14.3 No gotcha: the telltale rule.** `[D]` + `[N]` Every trap carries a **telltale** that is narrated, as
a feature of the area, when the PC first perceives the area — a scorched stripe on the floor, a skeleton
crumpled before a door, a row of holes in the wall at knee height, a too-clean flagstone in a dusty hall, a
taut line glinting at ankle height in torchlight, a rune half-hidden under soot. The telltale is written on
mention (it is addressable), it is always shown, and it never names itself a trap. An attentive player who
asks about it (an Observe of the telltale: 1 interval, at the trap's detect tier) or delves with **care**
(10.13.6) perceives the trap. Passive notice (01.4.6) perceives it if notice beats its detect tier. At bands where a
trap's harm is S1–S2 it may have a **subtle** telltale (narrated, but innocuous on its face: a loose
flagstone; `telltale_kind_by_band`); wherever its harm is S3 or heavier it always has a **plain** one (something that says *danger here* to
anyone who looks: the bones, the scorch, the holes). Combined with 07's keys — a trap perceived at S4+
raises the `severity` warning; an unperceived trap's harm is never lethal (07.3.5) — no trap kills a
character whose player was not shown its sign and warned [BRIEF §4; R1 §07 ("traps that always counter the
players" as a DM mistake); DL-10-17].

**10.14.4 Springing a trap.** `[D]` When a beat's method passes a trap's trigger (walking the plate, opening
the lid, crossing the wire, reading the word aloud) and the trap is neither disarmed nor bypassed, it
fires: its victim makes the trap's resisted check against the **effect DC = the trap's detect tier for its
band, one rung up** (the maker's craft against the victim's reflexes), read by 01.18.3's table: critical
success — no effect and a Precision lever; success — no effect; near miss — no effect and one other cost
(footing, gear, time); failure — the trap's harm at its band severity and its effects; critical failure —
one rung heavier. `alarm_ticks` tick the site's danger clock whatever the result. A **perceived** trap fired
on purpose (to spring it safely) is 10.14.5's "spring it from afar". Reset per the entry.

**10.14.5 Dealing with a perceived trap.** `[J:enum]` + `[D]` *Anchor: yes.* Once perceived, a trap is an
obstacle with stored tiers (`detect` and `disarm` by band; 00.3.8). Every way of dealing with it is an
existing verb (T-10-19, `traps.yaml#ways`):

| Way | Verb (license) | DC | On success | On failure |
|---|---|---|---|---|
| **Disarm** | verb.handle (`lic.training.guile_thievery`: "disarm mechanical traps"; magical traps need warding, 05.7.7) | the disarm tier | disarmed; parts may be salvaged (08.6.8) | near miss: success at cost; failure: the cost (time or footing); critical failure: it fires on the disarmer |
| **Jam** | verb.handle or verb.force with a wedge, spike, rope or cloth (G1; a tool is a Precision lever) | disarm tier − 1 rung (min Easy) | jammed for the scene (a fact) | as disarm; a forced jam is `trait.sense.loud` |
| **Spring it from afar** | verb.handle or verb.strike (a thrown stone, a pole, a dragged sack) | Easy, or Moderate for a pressure plate under a heavy weight | it fires harmlessly (spent, or resets per entry) | it does not fire; try again (repetition snags) |
| **Bypass** | verb.exert (jump the plate, climb past the wire, chimney over the pit) or verb.sneak (slip under the beam's eye) | the obstacle's own tier (a 10-ft leap Moderate…) | passed; the trap remains | the trap fires on the bypasser at a Protective lever (stakes −1) |
| **Break** | verb.force (smash the mechanism, `trait.sense.loud`) | disarm tier | destroyed | loud failure; on critical failure it fires |
| **Understand** | verb.observe (Intellect) or verb.recall (`deed.lore.engineering.mechanisms`) | detect tier | its trigger, effect and reset are known: a Precision lever on any other way | nothing learned |
| **Use** | verb.setup (lure a foe across it; reset it behind you) | the setup's own tier | a lever or a fact for a later beat (the foe at the plate) | as setup |
| **Avoid** | another route (a side passage), or wait for it to reset | — | no roll | — |

`[J:enum]` *Which way is the player's method?* Classified from the declared method; uncertain → the way
with the lower stakes (Understand before Disarm). *Worst case:* the neighboring way's DC and consequence
for one beat (class i), shown in the OFFER. The unlicensed are never stuck: jam, spring, bypass, break,
understand, use and avoid are basic verbs (C:VII redirect: "a thief could teach you to disarm it").

**10.14.6 Trap tiers by band.** `[D]` A trap's detect and disarm tiers and its harm rise with the band of the
site that holds it (`traps.yaml#entries[].detect.dc_tier_by_band`, `harm.severity_by_band`). Reference: a band-1
needle trap is detect Easy / disarm Moderate / S1 + poison; a band-5 crushing ceiling is detect Very hard /
disarm Legendary / S5, `lethal_context: true`, plain telltale. Magical traps (glyphs, wards) use the arcane
or divine warding license for disarm and Recall (`deed.lore.arcana`) for Understand.

**10.14.7 Alarms.** `[D]` An **alarm** trap harms no one: it ticks the site's danger clock by its
`alarm_ticks` (bells and gongs 2; a howling ward 3), and in a fortified site makes the next E face an
arrival (a guard comes to look). It follows every rule above (telltale, ways).

**10.14.8 Traps the PC makes.** `[D]` A snare, a deadfall, a tripwire with bells: a Setup or Handle beat
(1 interval for a snare or alarm line; 1 hour for a deadfall or pit) under the basic verbs for crude traps
(Handle: "crude making") or a license for refined ones (`lic.training.guile_thievery`; `wilds_survival` for
snares and deadfalls). The made trap is a trap entity with `detect` tier = the maker's delivered reach rung
(1 Easy … 4 Very hard), harm per the trap kind at the maker's band, and a telltale like any other (the
foe's notice may find it). It fires on a foe by 10.14.4 with the roles reversed.

### 10.15 Exploration activities

**10.15.1 The catalog.** `[D]` Every exploration activity is an anchor (00.2.6): a named intent with its basic
verb or license, attribute, DC source, duration by mode, reach meaning and knobs, so that any method a
player invents finds its nearest card (12.13). T-10-20 (`travel.yaml#activities`) is canonical; the rules
above hold the fuller cards for Explore onward (10.13.6), Find the way (10.4.2), Forage (10.6.4), Hunt and
fish (10.6.5), Read the weather (10.11.5), Pursuit (10.10.7), and dealing with traps (10.14.5).

**10.15.2 Durations by mode.** `[D]` An activity's duration is the column of its time mode: **site**
(intervals), **free** (minutes and hours, in the wild outside travel), **travel** (watches, when it is the
watch's activity). Time passes through `advance_time`, so every boundary in it runs (INV-15). Taking the
time (01.4.4) doubles the duration and removes the roll where it is allowed.

**10.15.3 One area, one search.** `[D]` Search and listen ride (01.4.2) for an area until something in it
changes (a new sound, a moved object, a trap sprung): searching the same unchanged room again with the
same method delivers nothing new and spends its interval. A different method (sounding the walls instead of
looking) is a new beat at its own repetition (01.14.3).

**T-10-20 Exploration activities** (canonical: `travel.yaml#activities`). *Dur.* = site / free / travel.
*Tier* = the DC source (stored on the obstacle when first set).

| Id | Intent verbs | Verb (license) · attribute · primary tag | Tier | Dur. (site / free / travel) | Reach means | Knobs |
|---|---|---|---|---|---|---|
| act.explore_onward | delve, press on, go deeper | 10.13.6 | site explore tier | 1 (care 2) / — / — | progress ticks | dc, attribute, time_cost, reach_unit, stakes |
| act.search | search, look for, examine, check | observe · Wits (Intellect for documents) · lore.investigation.search | the hidden thing's detect tier; an area with nothing: sealed Oracle first (01.4.7) | 1 per area / 10 min per room, 1 hour per building / — | items found (P17) | dc, time_cost, targets |
| act.listen | listen at, eavesdrop on, hear | observe · Wits · lore.investigation.search | by the door or distance: Easy / Moderate thick door | 0 if a single quick beat, else 1 / 1 min / — | items heard | dc, targets |
| act.map | map, chart, sketch the way | handle · Intellect · wilds.navigation.mapping (licensed for charts; a sketch is G1) | Easy (site); the area's nav tier (travel) | +1 per area while delving (or the area's walk-back) / 1 hour / 1 watch | a map fact: site walk-back halved; area: a way-finding lever | time_cost, dc |
| act.scout | scout, range ahead, reconnoiter | sneak or observe · Agility or Wits · wilds.tracking.sign | the area's denizens' notice / the area's nav tier | 1 / 1 hour / 1 watch (role) | what lies ahead: the next area's contents (site) or an adjacent area's danger word, landmarks and pending signs (travel) | dc, time_cost, targets |
| act.track | track, trail, follow sign | observe · Wits · wilds.tracking.trailing (license for old or hard trails; fallback: fresh plain tracks, +5) | trail tier: fresh in soft ground Easy, a day old or hard ground Moderate, rain or rock Hard, a deliberate cover Very hard | 1 / 1 hour / per watch at slow pace | following on: run-down ticks or "still on it" | dc, time_cost, reach_unit |
| act.cover_tracks | hide a trail, lose them | sneak · Wits · guile.stealth (or wilds.tracking under its license) | pursuers' best Wits defense | 1 / 1 hour / 1 watch at slow pace | trail tier raised one rung per reach | dc, time_cost |
| act.climb | climb, scale, descend | exert · Might (Agility for a delicate pitch) · martial.athletics.climbing | the face's tier: rough wall Easy, cliff Moderate, sheer or wet Hard, overhang Very hard | 1 per 60 ft / 10 min per 60 ft / — | 1 halfway, 2 the top, 3 the top with time saved, 4 + a lever | dc, time_cost, stakes (height) |
| act.swim | swim, cross the water, dive | exert · Might (Endurance for distance) · martial.athletics.swimming | water's tier (10.12.6) | 1 per crossing / 10 min / — | 1 partway, 2 across | dc, stakes, attribute |
| act.jump | leap, vault, jump across | exert · Might or Agility · martial.athletics.jumping | gap: 5 ft Easy, 10 ft Moderate, 12 ft Hard (running start), 15 ft Very hard; 30 ft Beyond | 0 (part of another beat) or 1 | across | dc, stakes |
| act.squeeze | crawl through, squeeze, wriggle | exert · Agility · martial.athletics.acrobatics | a crawl Easy; a tight squeeze Moderate; in armor medium +1 rung, heavy G4 | 1 / 10 min / — | through | dc, attribute |
| act.force_way | break down, force open, clear | force · Might · martial.athletics.lifting | the barrier's tier (a stuck door Easy, a barred door Hard) | 1 / 1 min / — | open; overflow a lever | dc, targets |
| act.pick_lock | pick, open the lock | handle · Agility · guile.thievery.lockpicking (`lic.training.guile_thievery`; fallback: force) | the lock's tier | 1 / 10 min / — | open | dc |
| act.disarm | disarm, jam, spring the trap | 10.14.5 | the trap's tiers | 1 / 10 min / — | 10.14.5 | dc, verb |
| act.dig | dig, clear rubble, tunnel | force or exert · Might/Endurance · martial.athletics.lifting | a progress clock (rubble 4, a collapse 6, a tunnel 8+) | 1 per tick roll / 1 hour per tick roll / — | clock ticks | dc, time_cost, reach_unit |
| act.secure | barricade, bar the door, make safe | handle or force · Might · craft.building | the site's explore tier | 1 / 10 min / — | the area is secured (rest site camp) | dc |
| act.light_fire | make fire, light a torch, kindle | handle · Agility · wilds.survival.firecraft | weather's fire tier (T-10-13) | 1 / 10 min / (part of camp) | fire; reach 2: no smoke | dc, time_cost |
| act.make_camp | make camp, pitch, settle | free activity; handle for shelter (wilds.survival.shelter) | the shelter: Trivial in fair weather; storm Moderate; snow hole Moderate | — / 1 hour / part of the camp watch | camp rest site; shelter and fire facts | time_cost |
| act.keep_watch | keep watch, stand guard | free (the lookout role) | — | while resting / per hour / per watch | the camp is aware (10.5.1) | duration |
| act.forage | forage, gather | 10.6.4 | forage tier | — / 1 hour / 1 watch | supply | dc, time_cost, reach_unit |
| act.hunt / act.fish / act.snare | hunt, fish, set snares | 10.6.5 | game tier | — / — / 1 watch | supply (×2 hunt) | dc, reach_unit |
| act.find_water | find water | 10.6.3 | forage tier (+1 rung arid) | — / 1 hour / 1 watch | water source | dc |
| act.read_weather | read the sky | 10.11.5 | Easy | — / 1 interval / — | forecast | dc, targets |
| act.find_way | navigate, reorient | 10.4.2 | nav tier | — / — / per day | course | dc, attribute |
| act.ford | ford, wade across | exert · Might · martial.athletics.swimming | haz.ford's tier | 1 / 10 min / part of the watch | across | dc, stakes |
| act.rope | rig a rope, lower, belay | handle · Agility · martial.athletics.climbing | Easy (anchor point present); Moderate (improvised) | 1 / 10 min / — | a rope fact: Protective lever on climbs and falls | dc |
| act.harvest | skin, butcher, carve | 08.3.10 | by the rarest part | 1 or 1 hour | parts | dc, time_cost, reach_unit |
| act.scavenge | loot the room, strip the dead | observe · Wits · lore.investigation.search | Easy (a room's plain contents) | 1 / 10 min / — | 08.3.11 gear and coin; a hidden cache needs Search | time_cost |
| act.study | read the inscription, study the mural | observe · Intellect (a language license for scripts) · lore.history | the text's tier | 1 / 1 hour / — | items (P17) | dc, attribute |
| act.signal | signal, call out, light a beacon | handle or talk · Presence | Easy | 1 / 1 min / — | heard by whom it reaches; `trait.sense.loud` | targets |
| act.haul | drag, carry out, haul up | exert · Might (Endurance over distance) · martial.athletics.lifting | load vs capacity: within Easy, burdened Moderate, overloaded G4 | per area walked / per hour / at crawl | moved | dc, time_cost |
| act.rest | breather, short rest, long rest | 07.8 | — | 1 / 6 / one watch | 07's recovery | — |

---

## Procedures

**PR-10-1 Writing or generating a place.** `[D]` + `[J:flag]` (10.1.4, 10.1.8)
1. Narration or a table names a way, a place, a landmark, an exit, a feature or a sign: apply 10.1.4's
   ADDRESSABLE test; if false, stop.
2. If the element is a place no data holds: generate it (10.1.8) — region inheritance for band, danger and
   climate; `roll_table` for terrain from the region's list; T-10-12's defaults for `nav_tier`,
   `forage_tier`, `game_tier`, `openness`, `grazing`, `water_source`; a site takes PR-10-6.
3. `create_entity` (place, object or link) with every field the narration implies; leave the rest
   undetermined (00.6.6); write `known`; write `discovered` with the frame id if a frame found it (10.1.5).
4. If the narration needs an undetermined property now, ask the Oracle first (00.12.7) and narrate the
   answer. Then deliver the narration.

**PR-10-2 A journey.** `[D]` (10.3)
1. The player names a destination. Compute legs over known links (fewest watches); a destination with no
   known path gets a trackless leg (10.4). Compute effective pace (10.3.2), points per leg (6 × W), watches,
   days at the default schedule, supply need (10.6.2), light need, way-finding needs, known hazards, region
   bands against `power_band(pc)`.
2. Show the journey OFFER (10.3.4). The player commits, changes the plan, or stays.
3. Mark `mode_change` to `travel`; if leaving a haven, mark `venture_start` (10.2.2). Write the journey record.
4. For each watch, the player's chosen activity (default day of 10.3.3) and each traveler's role (10.5)
   are written as facts; then `advance_time(1 watch, travel)` runs PR-10-3.
5. If `advance_time` halts on an interrupt, frame the interrupting scene (12.4.3); after it, offer the
   remainder of the journey back to the player (00.7.8).
6. On arrival, mark `mode_change` (to `free` at a settlement, `site` at a site); at a haven mark
   `venture_end`.

**PR-10-3 The watch boundary in the wild.** `[D]` (the order is 00.7.5's phases; within a phase, owner then id)
1. Phase 1: `h.00.durations` (effects and conditions with watch durations end).
2. Phase 2: `h.10.watch_exposure`: for each exposed traveler, each hazard whose exposure applies this
   watch (weather states, T-10-13; place hazards with a `watch` cadence) — protections first, then 07.10.1's
   resisted check, harm, conditions.
3. Phase 4: `h.07.fatigue` (07); `h.10.travel_progress`: if the activity was *travel*, way-finding first if
   due (10.4.1–10.4.2; the beat may need the player's OFFER: the handler raises it as a pause point before
   the watch is spent, 12.2.6), then points by effective pace (+1 if this watch's check is a lull: applied
   after phase 7 as a correction to the same watch), arrival, march units and forced-march stacks
   (10.3.5); `h.10.wayfinding`: veer accrual if `nav.lost`, and the seal test of 10.4.7 item 1.
4. Phase 5: `h.00.clock_auto` (every clock's watch rows).
5. Phase 7: `h.10.watch_check` (PR-10-4), unless the place is a haven or the PC is in a site.
6. Phase 9: record (journey record, venture record, `journey_role` facts closed; 03's `cnt.journey` reads them).
7. If any handler raised an interrupt, `advance_time` halts after phase 9 and returns the remainder.

**PR-10-4 The time-tick check.** `[D]` (10.9)
1. Rating: the place's (or the link's) danger, +1 rung on the night watch (cap deadly); a site's rating and
   cadence per 10.9.3 (+1 rung if roused). For a site, increment `intervals_since_check`; roll only at the
   cadence.
2. Roll d12 (`roll_table`); read the face from T-10-10 for the rating and context (travel or site).
3. If a threat is pending: increment its `checks_since` unless the face is L or the pacing opt-in (10.9.7)
   pauses it; on E or O, or on `checks_since` = 4, it arrives (go to PR-10-5) — on O, render its second sign
   first.
4. Else on E or O: roll d12 for the threat share of the rating (`watch_check.threat_share_d12`; sites use
   their denizen table's own threat flags); roll the chosen sub-table; field the row (10.10.1). A threat
   row becomes `enc.pending` with its first sign rendered now (archetype `signs`; out-of-band rules of
   10.9.5 item 4); a non-threat row on E arrives (PR-10-5); a non-threat row on O is a sign of travelers.
5. On V, D, W/H, F, P, S, L: run the face's table and write its results (10.9.4).
6. Return every result for narration; raise an interrupt for the results listed in 10.9.8.

**PR-10-5 An encounter arrives.** `[D]` (10.10)
1. Field the row (if not already fielded): band against home band clamped to the archetype's bands; the
   bestiary entry or PR-09-1's build; count by `tbl.09.group_shape`; four or more of one template → a mob;
   shape rules for home bands 4–5 (10.10.2 item 2); a leader if the group lists one; complication if the row
   says so (09.8.5).
2. Distance: T-10-15 by openness and light, then the role and ambush modifiers (10.10.3).
3. Awareness of each side (10.10.4), written as alertness facts (15) for 06.2.4.
4. Write every participant (`create_entity`); compute `threat_advisory` (09.6.5); render band tells
   (09.10.1); raise 07's danger notice (hard) or lethal warning (lethal; out of band by two or more) before
   anything else happens (07.3.3–07.3.8).
5. Reaction: 12's reaction roll, `tbl.09.beast_mood`, the behavior list, or the mission (10.10.5).
6. Frame the scene (12.4.3) at the distance; the player declares. A conflict starts only by 06.2.1.
7. After `scene_end`: add the encounter to the venture record; write survivors' presence on the place
   (10.10.6); start a pursuit pending threat if a chase ended with pursuers hunting (10.10.7).

**PR-10-6 Creating a site.** `[D]` (10.13.2–10.13.4, 10.13.13)
1. Theme, domain, band, size: authored (13), or rolled by `sites.yaml#tables.tbl.10.site_generation`.
2. `danger` from the theme (+1 rung at band 4–5); `explore_tier` from the domain (+1 rung at band 4–5);
   store both.
3. Clocks from `clk.10.site_progress` and `clk.10.site_danger` with the size's segments and the theme's
   omens.
4. Objective: authored, or `roll_table` the theme's `climax` (d6), sealed until reached.
5. Denizen table: archetypes gated by the theme's `creature_gate_tags` and the domain's terrain
   (`sites.yaml#denizen_table_rule`; fallback to the theme gate alone for the 20 pairs listed there),
   weighted by `creature_weights`, split into threat and non-threat by each archetype's mind and
   disposition (a `rob`, `capture`, `kill`, `drag_to_lair` disposition or a mindless guard is a threat),
   bands 30/55/15 around the site band. Store it on the record.
6. Place facts from the theme (`desecrated`, `consecrated`, `haunted`, resonance); place hazards from
   the theme where its dangers name standing hazards.
7. Write the record; the entrance area is generated by PR-10-7 on first entry.

**PR-10-7 Explore onward and a new area.** `[D]` + `[J:enum]` (10.13.6–10.13.7)
1. Classify the approach (10.13.6 decision); build the frame (verb, attribute, tag, DC = stored explore
   tier, stakes, reach, threatened cost, snags for darkness); OFFER; roll.
2. READ: delivered reach → progress clock ticks; costs → danger clock by its sources; haste's loud tick.
3. If reach ≥ 1: generate the area — feature (domain d12), contents (`tbl.10.area_contents` d12; side
   areas +2), exits; write it; it becomes the frontier and joins the path; `discovered` with the frame id.
4. Contents results run their own procedures: denizens through the omen-first rule (PR-10-4 step 3–4 with
   the site table), traps (10.14.2: telltale rendered), hazards (10.12.4: signs rendered), obstacles (a
   barrier entity with its tier stored), branches (a passage link), caches (sealed until searched or seen),
   theme dangers.
5. If care succeeded: perceive the area's traps and hidden hazards (unseal). If stealth succeeded: the
   area's denizens are `unaware`. Critical success: `tbl.10.site_opportunity`.
6. If the progress clock is complete: the next Explore onward (or any move onward) reaches the heart
   (10.13.10).
7. `h.10.site_time` advances the beat's intervals at `beat_end`; site checks run on their cadence.

**PR-10-8 Auditing an encounter table.** `[D]` (10.10.2; run by 13 on every regional table and by the
generator for the generic ones — `gen10_travel.py` prints the result)
1. Sum the threat sub-table's weight by relative band: it must be 30 / 55 / 15 (± one d20 face) at home − 1
   / home / home + 1, and nothing above home + 1.
2. For each threat row, field it against a reference PC of the home band with the archetype's usual group;
   apply the shape rules (crowds as mobs; bands 4–5 never two equal individuals); compute the advisory
   word **with the archetype's counter held** (09.6.4's `advisory_alone` convention: the reference PC
   carries the named counter, e.g. fire against a troll), and print the no-counter word
   (`advisory_without_counter`) beside it, so a row whose danger hangs on a counter is visible. At least two
   thirds of the threat weight must be `fair` or easier, none `lethal` (both tests read the counter-held
   word). A generic (band-relative) table is audited at every home band 1–5
   (`_process/simulation/10-word-audit.py`) [integration: I-027; DL-INT-04].
3. The non-threat sub-table must exist (d6, six rows) unless the table is marked deadly-only.
4. Every row cites archetype or adversary ids that exist, and every threat archetype has `signs`
   (`travel.yaml#archetype_signs` or a regional override).
5. A failing table is not used; the generic table of its terrain branch stands in, and an issue is logged.

**PR-10-9 Leaving and returning to a site.** `[D]` (10.13.11)
1. Leaving: the PC walks the path back (1 interval per 2 areas, halved with a map); site checks run; if the
   site is roused with a pending threat or an encounter on the PC, leaving is a chase (06.12) sized by
   10.13.11. On exit, write `last_left`; `mode_change` to `travel`.
2. While away: `h.00.clock_auto` decays the danger clock 2 a day it did not tick; `h.10.site_recovery`
   clears `roused` at half or below; `h.10.site_regrowth` rolls weekly for regrowing themes.
3. Returning: compute progress drift (1 segment per full week away, at most half the filled segments, never
   below the secured areas on the path); load the record; re-enter at the entrance; the known path is
   walked at 1 interval per 2 areas to the frontier; regrown denizens show their signs on arrival.

---

## Tables

Tables embedded in the Rules are canonical and indexed here; the data files are canonical for every number
and id (00.1.4 line 5).

| Table | What | Rule | Data |
|---|---|---|---|
| T-10-1 | Place kinds | 10.1.1 | — (Place field `place_kind`) |
| T-10-2 | Reference danger rings | 10.2.4 | `travel.yaml#rings` |
| T-10-3 | Route kinds and their way-finding | 10.1.3, 10.4.1 | — |
| T-10-4 | Pace ladder, steps and effects | 10.3.2, 10.5.1 | `travel.yaml#pace` |
| T-10-5 | Vessel paces | 10.3.7 | `travel.yaml#vessel_pace` |
| T-10-6 | Watch activities | 10.3.3 | `travel.yaml#activities_by_watch` |
| T-10-7 | Journey roles | 10.5.1 | `travel.yaml#roles` |
| T-10-8 | March allowance | 10.3.5 | `travel.yaml#march` |
| T-10-9 | Scene light | 10.7.2 | — |
| T-10-10 | The time-tick die by danger rating | 10.9.4 | `travel.yaml#watch_check`, `#site_check` |
| T-10-11 | Face result tables (depletion, find, opportunity, veer, site opportunity, area contents) | 10.9.4, 10.4.6, 10.13.7 | `travel.yaml#tables`, `sites.yaml#tables` |
| T-10-12 | Terrain defaults | 10.1.8, 10.4.3, 10.6.4 | `travel.yaml#terrain_defaults` (below) |
| T-10-13 | Weather states | 10.11.1 | `weather.yaml#states` |
| T-10-14 | Hazard index | 10.12 | `hazards.yaml` |
| T-10-15 | Encounter distance | 10.10.3 | `travel.yaml#tables.tbl.10.encounter_distance` |
| T-10-16 | Generic encounter tables | 10.10.1 | `travel.yaml#encounter_tables` (below) |
| T-10-17 | Site themes and domains | 10.13.2 | `sites.yaml` |
| T-10-18 | Site sizes, clocks and regrowth | 10.13.3, 10.13.8, 10.13.11 | `sites.yaml#sizes`, `#clock_templates`, themes' `regrowth` |
| T-10-19 | Ways of dealing with a trap | 10.14.5 | `traps.yaml#ways` |
| T-10-20 | Exploration activities | 10.15 | `travel.yaml#activities` |
| T-10-21 | Climate regimes | 10.11.2 | `weather.yaml#regimes` |
| T-10-22 | Traps | 10.14 | `traps.yaml#traps` (below) |
| T-10-23 | Handlers registered by ch.10 | 10.2.5 | `data/boundaries.yaml owner-block 10` |
| T-10-24 | Magical zones | 10.12.8 | `hazards.yaml` (zone entries) |

**T-10-3 Route kinds.**

| `route_kind` | Way-finding needed? | Vehicles | Notes |
|---|---|---|---|
| road | never | all `vehicle_ok` | ignores rain and storm for pace |
| track | only in fog, blizzard, or night without light | carts, handcarts | |
| river / water | never (on the water or along a bank) | vessels | current changes pace (10.3.7) |
| trackless | always (10.4) | carts only on plains | |
| underway | only without light | none | `deed.wilds.navigation.underways` |
| secret | as its kind once found | — | sealed until found |
| passage | never | — | inside sites and buildings; 1 interval |

**T-10-8 March allowance.** Walkers 2 units a day; mounts 2; slow and normal 1 unit a watch, fast and
hard_ride 2; a mount loaded past half its capacity +1 a watch; each unit over → one `cond.exhausted` stack at
the watch end (push-on may defer, 07.8.10); a mount at three stacks cannot be ridden or loaded until a long
rest. Reset at dawn.

**T-10-9 Scene light** (first match): underground / windowless / dark-domain site → dark outside a light's
radius · outdoors by day → bright (dim in fog, storm, thunderstorm, blizzard, or under a closed canopy) ·
outdoors by night → dim under clear or fair sky in open or broken country, else dark · a light: bright to its
bright band, dim to its dim band · night-sight: one step brighter for its holder only.

**T-10-12 Terrain defaults** (`travel.yaml#terrain_defaults`; forage by season: spring / summer / autumn /
winter; "none" = G4: nothing to gather or hunt; water: true, false, foul, with fire, or an Oracle rung).

| Terrain | Nav | Forage | Game | Open | Graze | Water |
|---|---|---|---|---|---|---|
| settlement | easy | none | none | broken | no | yes |
| road | easy | mod / easy / easy / hard | mod | broken | yes | Likely |
| forest.woodland | easy | mod / easy / easy / hard | easy | broken | yes | yes |
| forest.deepwood | moderate | mod / easy / easy / hard | easy | closed | no | yes |
| forest.jungle | hard | easy / easy / easy / mod | mod | closed | no | yes |
| highland.hills | easy | mod / mod / easy / hard | mod | broken | yes | yes |
| highland.mountains | hard | hard / hard / hard / v.hard | hard | broken | no | yes |
| highland.cliffs | moderate | hard / hard / hard / v.hard | hard | open | no | Even |
| plains.grassland | easy | mod / easy / easy / hard | easy | open | yes | Likely |
| plains.farmland | easy | easy / easy / easy / mod | mod | broken | yes | yes |
| plains.moor | easy | mod / mod / mod / hard | mod | open | yes | yes |
| wetland.marsh | moderate | mod / easy / easy / hard | mod | open | yes | yes |
| wetland.swamp | hard | mod / mod / mod / hard | mod | closed | no | yes |
| wetland.fen | moderate | mod / mod / mod / hard | mod | open | no | yes |
| arid.desert | hard | v.hard (all) | hard | open | no | no |
| arid.badlands | moderate | hard (all) | hard | broken | no | no |
| frozen.tundra | moderate | hard / mod / hard / v.hard | mod | open | yes | with fire |
| frozen.glacier | very hard | none | v.hard | open | no | with fire |
| frozen.snowfield | hard | v.hard (all) | hard | open | no | with fire |
| water.river | easy | easy (fishing) | easy | open | no | yes |
| water.lake | easy | easy | mod | open | no | yes |
| water.coast | moderate | easy / easy / easy / mod | mod | open | no | no (salt) |
| water.sea | very hard | none | hard | open | no | no |
| underground.cave | hard | hard | v.hard | closed | no | Even |
| underground.mine | moderate | v.hard | none | closed | no | Unlikely |
| underground.tunnel | hard | v.hard | none | closed | no | Unlikely |
| underground.sewer | moderate | hard | none | closed | no | foul |
| ruin (all) | moderate | hard | hard | broken | no | Even |

**T-10-16 Generic encounter tables** (`travel.yaml#encounter_tables`; threat d20 with relative bands —
faces 1–6 home − 1, 7–17 home, 18–20 home + 1 — and non-threat d6; every table audited 30/55/15).

| Terrain | Threat rows (d20) | Non-threat rows (d6) |
|---|---|---|
| road | footpads (ambush) · wolves · highwaymen with a captain (complication) · deserters · orc raiders · goblin ambush · ogre (+1) · troll under a bridge (+1) | merchants · pilgrims · road wardens · a messenger · a tinker · refugees |
| settlement | footpads (night) · stray dogs · thugs · cultists (night) · ghouls (night) · a hag (+1, night) | townsfolk · a beggar with news · the watch · a merchant · a drunk · a procession |
| forest | wolves · spiders (ambush) · brigands (ambush) · wolf pack (complication) · bear · wild fey · monstrous beast (+1) · troll (+1) | woodcutters · a hunter · deer · charcoal-burners · a hermit · a warden of the wood |
| highland | wolves · goblins (ambush) · orcs · bear · raptor · ogre (complication) · giant (+1) · wyvern (+1) | shepherds · wild goats · dwarf traders · prospectors · an eagle's circling (sign) · a pilgrim |
| plains | wolves · mounted raiders · gnolls · orcs (complication) · stampede · monstrous beast · great cat (+1) · wyvern (+1) | drovers · a caravan · wild horses · a lord's hunt · a farmer · travelers |
| wetland | giant vermin · reptiles · lizardfolk (ambush) · bog-dead · a hag · water beast · troll (+1) · strangling plant (+1) | eel-fishers · a punt-man · herons rising (sign) · a hermit · lizardfolk traders · a will-o'-the-wisp (sign) |
| arid | scorpions · reptiles · gnolls · raiders (ambush) · fire elemental · great cat · drake (+1) · earth elemental (+1) | a caravan · nomads · a well-keeper · a mirage (sign) · pilgrims · a wanderer half-dead |
| frozen | wolves · bear · wolf pack (complication) · giant · frost elemental · troll (+1) · giant (+1) | trappers · reindeer · a sled party · an ice-fisher · a cairn (sign) · an abandoned camp (sign) |
| water | water beasts · river pirates · pirates (complication) · water elemental · lizardfolk · a great water beast (+1) · a serpent of the deep (+1) | fisherfolk · a ferry · a barge · merchants · a drowned body (sign) · seals or otters |
| underground | giant vermin · goblins (ambush) · ooze · fungal · orcs · skeletons · aberration (+1) · drake (+1) | dwarf miners · a lost delver · blind fish (sign) · myconid traders · tool marks (sign) · bats (sign) |
| ruin | giant vermin · skeletons · ghouls · looters · cultists · a ghost · a wight (+1) · a golem (+1) | scavengers · a scholar · a pilgrim · crows (sign) · a lone dog · rival treasure-hunters |

**T-10-22 Traps** (`traps.yaml`; tiers and severities by site band 1→5; telltale plain from S3).

| Trap | Kind | Detect | Disarm | Harm by band | Notes |
|---|---|---|---|---|---|
| trap.pit | mechanical | easy→legendary | moderate→legendary | S2 S2 S3 S3 S4 | drop 10/20/40 ft by band |
| trap.spiked_pit | mechanical | moderate→ | moderate→ | S2 S3 S3 S4 S4 | bleeding; wound rot |
| trap.snare | snare | easy→ | easy→ | S1 S1 S1 S2 S2 | restrained; cut free |
| trap.deadfall | snare | easy→ | easy→ | S2 S2 S3 S3 S3 | pinned |
| trap.needle_lock | mechanical | moderate→ | moderate→ | S1 (all) | widow venom (wyvern venom at 4–5) |
| trap.dart_wall | mechanical | moderate→ | moderate→ | S1 S2 S2 S3 S3 | adder venom at band 3+ |
| trap.falling_slab | mechanical | moderate→ | hard→ | S2 S3 S3 S4 S5 | pinned; once |
| trap.collapsing_stair | mechanical | easy→ | moderate→ | S2 S2 S3 S3 S4 | engineering license |
| trap.scything_blade | mechanical | moderate→ | hard→ | S2 S3 S3 S4 S4 | bleeding |
| trap.falling_portcullis | mechanical | easy→ | hard→ | S3 S3 S4 S4 S4 | splits a party; alarm 2 |
| trap.murder_hole | manned | easy→ | — | S2 S2 S3 S3 S4 | burning; fires per defender beat |
| trap.alarm_line | alarm | easy→ | easy→ | — | danger clock +2 |
| trap.alarm_ward | magical alarm | moderate→ | moderate→ | — | danger clock +3 |
| trap.curse_glyph | magical | moderate→ | hard→ | S1 S2 S2 S3 S3 | evil eye curse |
| trap.flame_jet | magical | moderate→ | hard→ | S2 S3 S3 S4 S5 | burning |
| trap.flooding_room | mechanical | moderate→ | hard→ | S2 S2 S3 S3 S4 | breath; a clock of 4 |
| trap.gas_vent | mechanical | moderate→ | moderate→ | S1 S1 S2 S2 S3 | drowse; choking |
| trap.net | mechanical | easy→ | easy→ | — | restrained; capture |
| trap.rolling_stone | mechanical | hard→ | very hard→ | S3 S3 S4 S4 S5 | a chase of 4 |
| trap.crushing_ceiling | mechanical | hard→ | very hard→ | S3 S4 S4 S5 S5 | racing clocks of 4 |

**T-10-23 Handlers registered by chapter 10** (`data/boundaries.yaml owner-block 10`).

| Handler | Boundary | Phase | Interrupting | Rule |
|---|---|---|---|---|
| h.10.site_time | beat_end | 9 | no | 10.13.5 |
| h.10.light | interval | 4 | no | 10.7.1 |
| h.10.site_exposure | interval | 2 | after the first exposure of a recurring hazard | 10.12.2 |
| h.10.site_check | interval | 7 | per result (10.9.8) | 10.9 |
| h.10.watch_exposure | watch | 2 | after the first exposure of a recurring hazard | 10.12.2 |
| h.10.travel_progress | watch | 4 | arrival at a site or settlement: no (a mode change) | 10.3 |
| h.10.wayfinding | watch | 4 | when the lost seal opens | 10.4.6–10.4.7 |
| h.10.watch_check | watch | 7 | per result (10.9.8) | 10.9 |
| h.10.supply | day | 4 | when the deprivation warning fires | 10.6.2 |
| h.10.site_recovery | day | 6 | no | 10.13.9, 10.13.11 |
| h.10.weather | day | 7 | no | 10.11.3 |
| h.10.day_reset | day | 9 | no | 10.3.5, 10.4.1, 10.6.4 (march units, way-finding ride, picked-over) |
| h.10.site_regrowth | week | 6 | no | 10.13.11 |
| h.10.weather_regime | season | 6 | no | 10.11.2 |
| h.10.scene_frame | scene_start, mode_change | 7 | no | 10.7.2, 10.13.4 |
| h.10.venture | venture_start, venture_end | 9 | no | 10.2.2 |

---

## Worked examples

All examples follow **Wren** (P1; Wits +2, Agility +3, Might +1, Endurance +1; competence `deed` +1,
`deed.wilds.tracking` +2, `deed.martial.archery` +2; her forester origin's `lic.training.wilds_tracking` at
`trained`, 02; Vitality 13; Focus 4; fate 1; capacity 12). She holds no navigation, foraging or thievery
license. Region data are illustrative stand-ins for chapter 13's *(illustrative; 13 owns)*; every rule,
table and number from this chapter is exact. Dice are the engine's.

### WE-10-1 Three days to the drowned chapel: an omen, an encounter interrupt, and a storm

*Situation.* Autumn, week 2, day 3, dawn, at Ashford (`safe: true`). The Brackmarch region: home band 1,
danger wild, climate coastal. Wren carries 4 supply (2 load units), a lantern with a full flask (24
intervals), five torches, rope. Destination: the drowned chapel at Reedholm, known by rumor.

**The plan (PR-10-2).** Legs: L1 the Salt Road to Brackwater ford (road, W = 2 → 12 points, the road link
`danger: settled`); L2 across the Fenmoor (trackless, W = 3 → 18 points; the chapel tower is the area's
landmark). Pace normal (6). The journey OFFER:

```
[JOURNEY] To the drowned chapel by the Salt Road, then across the Fenmoor. At a normal pace: about two
          and a half days (5 travel watches).
          Country: the borderland: wild, but folk pass through · Weather: today fair; tomorrow unknown.
          Supply: 4 for 1 = 4 days; needed about 3 (+1).
          Way-finding: 1 trackless day, no navigator: you would go by the chapel tower.
          Known hazards: none known.
```

No warning line (home band 1 = Wren's band). She commits; `venture_start` fires (she leaves a haven);
`h.10.venture` writes the venture record.

**Day 1.**

| Watch | Activity | Phase 2 | Phase 4 (points) | Phase 7 (check) | Result |
|---|---|---|---|---|---|
| morning | travel L1 | — | +6 → 6/12 | road, settled: d12 = 9 → **L** | +1 point → 7/12 |
| afternoon | travel L1 | — | +6 → 13 ≥ 12: arrives at the ford in hour 5 | Brackwater (area, wild; its table is the road table): d12 = 3 → **O** | interrupt (below) |

Wren stops at the ford for the day rather than start the fen in the last hour of light (the leftover point
is dropped: 10.3.6). The omen: nothing is pending, so the engine rolls the threat share for wild — d12 = 5
(≤ 7: threat) — then the road threat sub-table: d20 = 9 → **highwaymen with a captain** (`arch.brigand`,
`home` → band 1, `group`, complication). A pending threat is written (sealed: what, how many); its first sign
from `archetype_signs` is rendered: *a cold fire by the ford with far too many bootprints around it, the ash
still warm underneath.* `advance_time` halts (10.9.8).

*Answer: investigate (10.9.6).* Observe, Wits +2, `deed.wilds.tracking.sign` → competence +2 (tracking) =
**+4**; DC: the row's tier by band, T1 → Easy (10); stakes Risky (an observer may be watching the ford:
`cost.exposure` threatened); reach Standard. She ranks the bundle: how many, how near, what kind. d20 = 13 →
17, success → `deliver_count(3, 2)` = 2 items (01.10.4): the engine fields the row now — `tbl.09.group_shape`
d6 = 4 → five: a mob of four (`adv.brigand_band`) and a leader (an elite of the archetype) — and reports how
near: *they watch the ford; a lone camp will see them tonight* (the pending timer can run at most to the
fourth check). *Answer: prepare.* She camps in an alder hollow off the road (07.8.2: camp) and strings a cord
with her cook-pot on it across the path (verb.setup, Trivial in the circumstances: the fact `camp.alarm`).

| Watch | Activity | Check | Result |
|---|---|---|---|
| evening | camp (lookout) | wild: d12 = 2 → **O** | a threat is pending → its second sign (*boots in the reeds, a whispered count*) and **arrival** |

*Arrival (PR-10-5).* Distance: Brackwater is `broken`, but it is night without light → read as `closed`: d6
= 5 → `band.near`. Awareness: Wren holds lookout in a camp watch and the alarm line jangles → not surprised.
Advisory (09.6.5): P1 against a T1 mob of four and an elite → **fair** (shown only on request; the band tells
are rendered). The brigands' objective is `rob` (their disposition); they are on a mission (10.10.5), so
they come on. The conflict (06; summarized): Wren drops the captain with an arrow in round 1 (a critical
hit); the mob's morale clock breaks in round 3 and they scatter into the reeds. `conflict_end`; the venture
record gains the encounter; the survivors are written on the area (`area.occupants: brigands, scattered`,
10.10.6). Wren searches the captain: 08.3.11's purse (T1: 1d4 − 1 = 2 coins) and his gear.

| Watch | Activity | Check | Result |
|---|---|---|---|
| night | sleep (`rest_long`) | night rung +1 → perilous: d12 = 11 → **L** | rest undisturbed; the long rest completes at dawn, quality **full** (camp, fed, no interruption) |

**Day 2.** At dawn: `rest_long` (event) runs first (00.7.6), then the `day` boundary: `h.10.supply` (4 → **3**
supply); `h.10.weather`: today ← tomorrow, which was rolled yesterday (d6 = 4 → coastal autumn d12 = 9 →
**storm**); tomorrow is rolled now (d6 = 5 → d12 = 1 → **fair**, sealed). A storm day writes **`high_water`** on
the region's river links (10.11.4).

*Way-finding.* L2 is trackless (10.4.1: needed). Wren holds no navigation license, so the beat would be the
crude fallback — usable only if a landmark is visible (10.4.4): the chapel tower is a distant landmark and
the storm hides it; under a storm sky the sun does not count. **False.** 10.4.5's redirect lists what state
holds: *the long way*: the Brack river-bank track runs to the chapel's causeway head (W = 4 → 24 points, no
way-finding); *wait* for the storm; *a navigator* (none); *mark and go slow* (crawl); *go blind*. She takes
the long way. Pace: a track is off-road → storm, one step → **slow (4)**.

| Watch | Phase 2: exposure | Points | Check (wild) | Result |
|---|---|---|---|---|
| morning | `haz.storm_exposure` (S2): Endure, Endurance +1, floor +1 = +2 vs Moderate 15, Risky: d20 = 6 → 8, **failure** | +4 → 4/24 | d12 = 7 → **F** | S2 harm: 3, no reduction (the entry's `no_reduction`): Vitality **13 → 10**. The discovery: the area holds an undiscovered place — **an eel-weir with a fisher's hut** — discovered (`frame_id: null`) |
| afternoon | Endure: d20 = 14 → 16, success | +4 → 8/24 | d12 = 11 → **L** | +1 → **9/24** |
| evening | sheltered in the fisher's hut: no exposure | camp | d12 = 6 → **W** | weather shift d6 = 5 → better: storm → **rain** (no exposure in rain) |
| night | — | sleep | perilous: d12 = 12 → **L** | full long rest (shelter, fed): Vitality 10 → **13** (07.8.5) |

**Day 3.** Dawn: supply 3 → **2**; today ← **fair**; tomorrow rolled (sealed). `high_water` stays (two dry days
clear it).

| Watch | Points | Check (wild) | Result |
|---|---|---|---|
| morning (normal, fair) | +6 → 15/24 | d12 = 12 → L | +1 → 16/24 |
| afternoon | +6 → 22/24 | d12 = 5 → **D** | depletion d6 = 3: no light is burning, so a stored source is found damp: the lantern's flask loses half its remaining intervals, **24 → 12** |
| evening (travel: a third travel watch) | +6 → 28 ≥ 24: arrives at the causeway head in hour 2 | d12 = 10 → L | **forced march**: the third travel watch is one march unit over the allowance (10.3.5) |

The forced unit would apply one `cond.exhausted` stack at the evening watch's end; Wren declares
**push-on** (07.8.10): Endure, Endurance +1, floor +1 = +2 vs Moderate 15: d20 = 15 → 17, success,
delivered reach 2 → the stack is deferred two watches. She camps at the causeway head (a fire; camp). At the
next dawn the `rest_long` event runs first (it removes no stack: she holds none yet), then the deferred stack
lands at the `watch` boundary: she starts the delve with **one stack** (−1 on every check) — the honest
price of the extra watch. *Boundary pair:* had she camped at the afternoon's end (22/24) instead, she would
arrive mid-morning of day 4 with no stack and one more supply spent; had she failed the push-on, the stack
would have landed that evening.

*Narration.* The skip of each day is narrated only from the returned list (12.4.6): the bootprints, the
whispered count, the rain driving sideways and the cold of it, the eel-weir and its hut, the weather
easing, the damp flask. Nothing else happens on the road, because nothing else was rolled.

*Non-example.* "It's only a bit of rain, I'll walk the fen anyway with the tower as my guide." The tower is
not visible in the storm (10.4.4), so the fallback's method does not exist this day; the honest options
were the five the redirect named. The DM does not let the tower show "just enough".

### WE-10-2 The chapel crypt: a delve from entry to the heart, the danger clock at its heels

*The site.* Under the drowned chapel: theme **haunted**, domain **crypt**, band 1, size **small** (progress 6,
danger 8; 10.13.3). Haunted → danger **perilous** (band 1: no step) → site cadence **2 intervals**; crypt →
explore tier **moderate** (15), dark. Place facts: `haunted`. The objective, rolled at creation from the
haunted `climax` (d6 = 1) and sealed: **guardian — the barrow-wight on its throne** (`arch.wight`, whose bands
are 2–4: built at band 2 by PR-09-1, one band above Wren). The denizen table is haunted × crypt (a terrain
match; no fallback). Wren lights the lantern (12 intervals left); she carries one `cond.exhausted` stack.

**Entering (10.13.4).** The entrance area A1: domain feature *iron gates rusted half-open*; the theme's first
sign: *your breath smoking in the stairwell, though the day outside was mild.* The site OFFER: "A haunted crypt
under the chapel. Band: like you. Dark: you need light (lantern 12 intervals, 5 torches). Progress 0/6. The
place is uneasy (sensed)." Progress is public; the danger clock is sensed.

Wren's **care** approach: Observe, Wits +2, `deed.lore.investigation.search` → floor +1, `cond.exhausted` −1
(status) → **+2** vs 15: 40%; Risky; 2 intervals; threatened cost `cost.time` (the danger clock listens).

| # | Beat | Roll | Progress | Danger | Intervals | Site check (cadence 2) and what it did |
|---|---|---|---|---|---|---|
| 1 | Explore onward, care | d20 15 → 17, success, reach 2 | **2/6** | 0/8 | 2 | d12 = 9 → **F**: a crypt discovery (d6 = 1): *a family's names and dates* (lore, written) |
| — | new area A2: *an ossuary of skulls set in patterns* (`cover`); contents d12 = 5 → **denizens**: the haunted × crypt table rolls a threat row — **skeletons** (`arch.skeleton`, home band, mob) — nothing is pending, so it becomes pending and A2 shows its sign: *old bones scattered across the floor, and then, further on, gathered into heaps* | | | | | |
| 2 | Explore onward, care | d20 7 → 9, failure (margin −6) | 2/6 | **1/8** (cost.time S2 = U 1; omen, stirring: *a whisper that is almost your name*) | 4 | d12 = 3 → **O**: the skeletons were pending → second sign (*a clatter in the dark, rhythmic*) and **arrival** |
| — | Arrival: distance in a site (closed) d6 = 5 → `band.near`; Wren sees them by her lantern (they are not hiding) → aware; advisory P1 vs a T1 mob of four → **easy**. `conflict_start` inside the site → danger **2/8** (stirring omen: *a lantern guttering though the air is still*). Wren fights (06; four rounds); the mob falls. `conflict_end` rounds up to 1 interval | | | 2/8 | 5 | (one interval since the last check) |
| 3 | Explore onward: **haste** — "I run the gallery before the rest of them wake" (stealth is G4: a lit lantern, 10.7.3; shuttered, the crypt is dark and stealth would be by touch). Move, Agility +3, floor +1, −1 = **+3** vs 15, reach **Great**, `trait.sense.loud` | d20 16 → 19, success, reach 3 | **5/6** | **3/8** (loud) | 6 | d12 = 6 → **S** (perilous S = 5–6): danger **4/8** → stage **building** (omen: *footsteps matching yours, a beat behind*) and the clock's **half link** fires: the haunted `dangers` d12 = 7 → *a wail rises and falls: the danger clock +2* → **6/8** → **imminent** (remaining 2 ≤ max(1, 8 ÷ 4)): omen *every niche you passed is empty now that was full* |

**The warning.** The danger clock is imminent and its `on_complete` would bring the climax guardian — a
`lethal_context` archetype — to the PC: PR-00-3 step 3 raises 07's lethal-warning trigger (cause `clock`):

```
[WARNING] THIS CAN KILL YOU — something in this crypt. The signs say something deadly is very close.
          From your next action on, falling here can mean Dying. Fate: 1.
          Exits now: Retreat — the way out is 3 areas back (2 intervals; the place is waking) · or go on.
```

New area A3 (from beat 3): *a chapel with a broken altar*; contents d12 = 2: nothing more. Wren goes on: the
heart is one tick away and she knows it.

| # | Beat | Roll | Progress | Danger | Intervals | Check |
|---|---|---|---|---|---|---|
| 4 | Explore onward, care (+2 vs 15) | d20 11 → 13: **near miss** (margin −2); she takes **success at a cost**: reach 2, one S2 cost — the threatened `cost.time` | **6/6 — complete** | **7/8** (U 1; imminent omen: *a crowd of shapes at the edge of the light*) | 8 | d12 = 12 → L |

**The heart (10.13.10).** The progress clock is complete; the next area is the heart: *a burial hall, a throne
of stacked stone, and on it a thing in rusted mail whose eyes are two cold sparks.* The wight (T2, built at
band 2) is perceived: it is one band above Wren → its band tell is rendered (09.6.6); its archetype carries
`lethal_context` → a second lethal warning, now for this source (07.3.3 `archetype`: one context per source
per scene), with its tell as the sign. The advisory: P1 against one T2 → **easy** by T-09-10 — an honest
word: the wight is beatable, and it can kill. Wren fights; she spends Focus on a push in the second round,
takes a Moderate wound when Staggered, and destroys it in round five (06/07; summarized). The hoard behind the
throne: 08.3.12 at band 1 (one fine item and 3d6 × 3 coins), the source the defeated keeper → `decisive`.

**Out (10.13.11).** The path is A1–A2–A3–heart: 4 areas → **2 intervals** (no map). The interval counter
stood at 0 after beat 4's check; leaving takes 2 intervals → one check: d12 = 5 → **S** → danger **8/8 → roused**. The climax guardian is already destroyed, so nothing comes
for her; every surviving denizen becomes alarmed, and the cadence becomes every interval — but Wren is on
the stair. She is out at interval 10 of a 12-interval lantern flask.

*What the race showed.* Progress completed at danger 7/8: the haste beat's speed (3 ticks for 1 interval)
paid for itself, and its noise and the half-link danger nearly brought the place down on her. `sim10_site2.py`
puts a careful at-band delver's chance of rousing a small site first at about 12% and a medium one at 25%;
Wren's exhaustion (+2 instead of +3) and a perilous theme put her on the harder side of that.

*Non-example.* "The heart must be near, so I search for a secret door to skip ahead." A search delivers
what the area holds (a discovery, a cache, a trap); it does not tick the progress clock unless a table result
says so (a map, a clue toward the heart). Progress comes from Explore onward and from listed sources only.

### WE-10-3 A trap found and bypassed creatively

*Situation.* The cellars under Grey Keep (a site: theme fortified, domain underkeep, band **2**). Wren takes a
new area by **haste**, so its traps are met only by passive notice. The area's contents rolled a trap: the
underkeep list, `trap.pit` (band 2: detect **Moderate**, disarm **Hard**, harm **S2**, a 10-ft drop; telltale
**subtle** at band 2, because the harm is S2).

**Passive notice (01.4.6).** Wren's notice = 10 + Wits 2 + competence on `deed.lore.investigation.search`
(floor 1) = **13** < 15: not perceived. But the telltale is narrated as the area's feature (10.14.3): *the
storeroom floor is grey with dust, except one flagstone near the far door, swept almost clean.*

**The player asks about it.** "I crouch and look at that clean stone." → Observe the telltale, 1 interval;
Wits +2, floor +1 = +3 vs Moderate 15 (the detect tier); stakes Safe (nothing listens yet). d20 = 13 → 16:
success. The trap unseals: *a counterweighted lid over a pit; step on it and it tips.*

**The creative method.** "I jam my spear under the lip of the lid, wedged against the frame, so it can't tip,
and walk across on the spear side." → classified **Jam** (10.14.5; the method fixes the lid rather than
working the mechanism; uncertain between Jam and Disarm → the way with lower stakes, which is Jam anyway).
Verb.handle (basic), Agility +3, floor +1; DC = disarm tier − 1 rung = Hard − 1 = **Moderate (15)**; lever:
the spear (a held item, `pc.wren.holds item.spear`) typed **Precision** (a tool that lets the method be done
better) → **+6**; stakes **Risky** (a 10-ft drop is an S2 source); threatened cost `cost.footing`. Odds: needs 9
→ 60%. d20 = 11 → 17: success. The fact `trap.pit_07.jammed = scene` is written; she crosses. The spear stays
wedged (she must leave it or un-jam it on the way back: the trap is live again when it is removed).

*Boundary pairs.* (a) Had she rolled a **near miss**, success at a cost: jammed, and her alternate cost — the
spear `damaged` (`cost.gear`, 08.1.9). (b) A **critical failure** fires the trap on her: Evade, Agility +3
against the effect DC = the detect tier one rung up = **Hard (20)**, by 01.18.3's table; a failure is S2 harm
(3) and `cond.prone` at the bottom of a 10-ft pit, no reduction (a fall). It cannot be lethal: S2, no lethal
context. (c) The licensed thief's way: **Disarm**, Handle under `lic.training.guile_thievery` against **Hard**
(20) — slower to succeed, but leaves the trap safe for good.

*Tempting non-example.* "I know there's a pit, so I walk around it." The storeroom is recorded as a
`chokepoint` between shelving: there is no "around" in state. If the room had a recorded edge, *walk the
edge* is the pit's bypass row — an Exert at Moderate, not a free step.

### WE-10-4 Lost in the Greywood, and found again

*Situation.* Wren sets out from the Greywood's edge for the hermit's tower: one trackless leg, **W = 2** (12
points), across `terrain.forest.deepwood` (nav **moderate**, `closed`). Weather fair. The area's landmarks
hold *the Wending stream*, which runs most of the way. No navigator.

**Way-finding (10.4.2).** Unlicensed → G3 → the crude fallback; 10.4.4: the stream is a near landmark, visible
by daylight → usable. Observe, Wits +2, floor +1 = **+3** vs Moderate + 5 = **20**; reach capped **Limited**;
a **secret frame** (the OFFER shows the modifier, stakes Risky, threatened `cost.time`; not the DC or odds).
d20 = 9 → 12: failure (margin −8): **off course**. `nav.lost` is written sealed: `tbl.10.veer` d6 = 3 → the
link nearest the bearing on its **right**: the Thornway crossing (an undiscovered place, link W = 3 → 18
points).

| Time | Points toward the veer | What the narration shows (true terrain) |
|---|---|---|
| day 1 morning | 6/18 | *the stream bends and you keep with it; the oaks give way to holly and bramble* |
| day 1 afternoon | 12/18 | *no tower yet; the ground rises; the stream is somewhere behind you now* |

The intended leg would have completed at the afternoon's end (12 points). The seal opens at the first boundary
after that **plus one travel watch** (10.4.7 item 1): not yet. She camps, sleeps; supply 2 → 1 at dawn.

| Time | Points | Event |
|---|---|---|
| day 2 morning | 18/18: arrives at the Thornway crossing | the seal test fires at this same boundary: *the tower should have been here a day ago*; and she arrives at a place she can name (a road crossing she has never seen): discovered (`frame_id: null`); her position is known (10.4.7 item 3) |

**Recovery.** From the crossing, the engine re-plans: the tower is two links away by the Thornway road and a
short trackless leg (W = 1). Wren chooses to **take the time** on the trackless leg (01.4.4; the fallback is
legal here, Moderate allows it): no roll, Standard reach, each travel watch earns half its points — W = 1 → 6
points at 3 a watch = 2 watches. She arrives at the tower on day 2's evening. Cost of being lost: about a day
and one supply; nothing else, because the time-tick checks of those watches all came up lulls and a
discovery (the Thornway crossing itself is now on her map).

*Boundary pairs.* Had she taken the time from the start: 12 points at 3 a watch = 4 travel watches, arriving
on day 2's afternoon, never lost — half a day sooner than what happened, and certain. Had she rolled a near
miss and taken success at a cost: on course at Limited reach (the day's pace one step slower: 4 a watch,
arriving on day 2's morning) and one S2 `cost.time` (3 hours).

*Non-example.* "I'm sure this is the way; I've got a good feel for the woods." An assertion (SG-06): no lever,
no fact. And the DM never says "you are lost" before a seal opens: the player learns it the way the
character does.

### WE-10-5 An omen answered: the wyvern's range

*Situation.* Wren's journey OFFER into the Crag Moors (home band 2, perilous) showed: "`[WARNING] Things there
are stronger than you.`" On the second afternoon the check (perilous) rolls d12 = 3 → **O**; the threat share
d12 = 4 (≤ 9) → threat; the highland threat sub-table d20 = 20 → **wyvern** (`home+1` → band 3). Band 3 is two
above Wren's band 1, so 10.9.5 item 4 applies: the first sign says what the warning will say — *a sheep
carried off whole; the drag-marks end in the middle of the heather, as if it was lifted* — and a band tell is
rendered with it; when the wyvern is first perceived, 07's lethal warning will fire at once (09.6.6).

*Answer: avoid.* The area has a second link down into the Hollins valley (+1 watch). Wren takes it: no roll
(a detour), the pending threat is written `evaded`, the wyvern stays in the Crag Moors as a fact of the place
(10.10.6) — a lair a stronger Wren may come back to. *Boundary:* had she chosen to go on at slow pace and
Sneak past (Agility +3, `deed.guile.stealth` → floor +1 = +4 against the wyvern's Wits defense), a failure
would have brought it down on her at once, aware, at `band.far` — with the lethal warning shown before its
first attack (07.3.5: at least one decision between the warning and the blow).

### WE-10-6 A hungry day, and a hunt

*Situation.* Wren reaches the hermit's tower with 0 supply (the Greywood took a day she had not planned).
The hermit has none to spare (an Oracle question, Unlikely: no). At the next dawn `h.10.supply` finds her
unfed: **one `cond.exhausted` stack** and `went_without` (10.6.2). The deprivation warning is two stacks away.

*Hunt (10.6.5).* One watch in the Greywood (deepwood: game tier **Easy**). Observe, Wits +2,
`deed.wilds.tracking.hunting` → competence +2 = +4, status −1 (exhausted) → **+3** vs 10; licensed
(`lic.training.wilds_tracking`: "hunt game"); stakes **Risky** (the forest table holds
`creature.beast.predator` rows — wolves, a bear — so a source exists, 10.6.5; threatened `cost.time`); reach Standard.
d20 = 12 → 15: success → supply = 2 × 2 = **4**, and a fresh deer carcass: she harvests hide and antler (08.3.10,
1 hour). *Boundary pair:* the same hunt on the crude fallback (no license) would be Observe +3 vs 15 at Limited
reach: 2 supply on a success. A forage watch instead (no license: fallback +3 vs Easy + 5 = 15, Limited,
Safe) would average 0.65 supply.

---

## Edge cases & adaptation anchors

### Reaching for an anchor

The anchors of this chapter (each `Anchor: yes` with its knobs; compiled into `anchors.yaml` at integration):

| Anchor | Rule | Intent verbs | Knobs |
|---|---|---|---|
| Find the way | 10.4.2 | navigate, steer by, reorient, keep the line | dc, attribute, time_cost, reach_unit |
| Forage | 10.6.4 | forage, gather, scrounge | dc, time_cost, reach_unit |
| Hunt / fish / snare | 10.6.5 | hunt, stalk, fish, set snares | dc, time_cost, reach_unit |
| Read the weather | 10.11.5 | read the sky, forecast | dc, time_cost, targets |
| Pursuit across country | 10.10.7 | track the fled, lose pursuers | time_cost, dc, reach_unit |
| Explore onward | 10.13.6 | delve, press on, go deeper | dc, attribute, time_cost, reach_unit, stakes |
| Retreat through known ground | 10.13.11 | withdraw, get out, back the way we came | time_cost, dc (as a chase when roused) |
| Deal with a trap | 10.14.5 | disarm, jam, spring, bypass, break, understand, use | dc, verb, stakes |
| Every activity of T-10-20 | 10.15 | (per row) | (per row) |
| Hazard severity (07's) with cadence | 07.10.2 + 10.12.9 | burn, crush, drown, freeze, fall | harm_severity, harm_tags, dc, duration |

**How to reach.** A method no rule names is matched by intent verb to the nearest card (12.13), then at most two
knobs move (00.2.7). Typical reaches:
- *"I climb a tall tree to get my bearings."* → not an adapted Find the way: the climb is
  `act.climb` (Easy, 1 interval in free mode), and its success is a **Precision lever** (a vantage fact) on
  the day's way-finding beat — two beats, not one adapted card. A tree above a closed canopy also makes the
  sun or a distant landmark visible (10.4.4: true for that beat).
- *"I follow the birds to water."* → Find water (10.6.3) with `dc` unchanged and the method's fact (birds
  flying low at dusk, if established) as a lever; the birds are not a fact until narration or the Oracle
  makes them one.
- *"I build a raft to cross the lake."* → 08.6.13 building as a crafting project (a raft: clock 4, 1 hour a
  tick, `lic.training.craft_woodcraft` or crude making by Handle at Limited), then water travel by 10.3.7.
- *"I set the gorse alight to drive the wolves off."* → `haz.wildfire` is now the PC's: 06.5.10 environment use
  with the fire as a hazard feature; the fire spreads by its own cadence (interval) and is a `trait.sense.loud`
  and visible fact for every listening clock and watcher in the region.
- *"I wait in the dark and listen for which way the draught blows."* → Explore onward by care with
  `attribute` Wits and `time_cost` 2 intervals; the draught (if established by a site shift or a feature) is a
  Precision lever, else an Oracle question (Likely in caves).
- *"I mark the tunnels with chalk."* → `act.map` (a sketch, G1): the walk-back halves; also prevents the veer
  inside a warren (10.4.5 (d)'s logic).
- *"I lure the troll onto the pit."* → Deal with a trap: **Use** (verb.setup), its success a fact for the
  next beat (the troll at the plate), the trap firing by 10.14.4 with the troll as victim.

### Edge cases

- **A road that crosses a trackless area.** The road is a link; following it needs no way-finding; leaving it
  makes the next leg trackless. A party may ride the road for part of a leg and strike off later: two legs.
- **Night travel with a light.** A light on a road removes the night step; off-road it removes the step for
  way-finding visibility (a near landmark) but not for terrain (the night step stays: you cannot see the
  ground beyond your torch) — and the torch burns 6 intervals each, 6 torches a watch, and makes the party
  visible at `band.far` to everything that watches (10.7.3).
- **Two pending threats.** There is only ever one pending threat per party. A second threat row drawn while
  one is pending is discarded and the face reads as the pending one's next sign (O) or its arrival (E). The
  world announces one thing at a time; two at once is a complication the tables do not make.
- **A pending threat and a change of area.** It follows the party (it was shadowing it) unless avoided,
  evaded or the party enters a haven, where it stays outside: on the party's next departure it is the first
  thing waiting (its checks continue from where they stopped).
- **An encounter at a haven's gate.** None by this chapter: the time-tick die does not roll in a haven. A
  World Turn bang or a pacing push may still bring trouble to the gate (11, 12).
- **The PC is captured.** The venture ends in captivity (10.2.2); 07.6.3 makes captivity a situation. A
  captor's place is not safe; its own checks run (it is a site or a settlement as written).
- **The weather changes inside a site.** It doesn't: underground and indoor places have no weather. A site
  with open-air areas (a ruined temple's garth) reads the region's weather in those areas only.
- **A storm at sea when the PC is a passenger.** `haz.storm_at_sea` applies to those on deck; passengers
  below are sheltered; the hull clock still takes the storm's `cost.gear` each watch.
- **The progress clock completes mid-encounter.** It cannot: progress ticks only from Explore onward and
  listed sources, never during a conflict.
- **A roused site and a long rest inside it.** Legal; a long rest is a watch of site checks at every interval
  with the rating one rung up: perilous becomes deadly — 36 checks, about 15 encounter or omen faces. The
  rest site is `rough` unless secured and the danger clock is not imminent (it is complete, so not
  imminent: a secured room in a roused site is `camp` until its clock fills again). The player is shown the
  rest's best quality first (07.8.4).
- **Darkness at the worst moment.** The last torch gutters (its 1-interval warning was narrated). The PC is now
  in `dark`: sight-reliant beats are `cond.blinded`; Explore onward only by touch; the site's cadence one step
  faster. Lighting a new source takes a tinderbox and 1 interval (a site beat). This is the delve's oldest
  clock and the reason the journey OFFER counts light.
- **A hazard improvised by the player** (collapsing a ceiling onto pursuers): rate it by 07.10.2, choose its
  cadence by 10.12.9; the PC, having caused it, is warned by the same rules as anyone (07.3.3 `severity`).
- **Losing the trail in a chase across country.** The pursuers' pending threat is `evaded` by Cover tracks; if
  the PC instead hides (a veil, a cave), it is 06.12.5's Sneak at travel scale: one watch, against the
  pursuers' best notice.
- **A secret route found by a search.** It becomes `known` and gets a `route_kind` (usually `passage` or
  `track`) and a length; until then its existence was sealed (an Oracle question asked sealed if no data held
  it, 01.15.6).
- **The player asks "how far is it?"** Out of fiction and free: the engine answers from the plan in watches
  and days at the chosen pace (12.5.10). In fiction, the narrator says it the way people do ("two days' walk,
  if the weather holds").
- **A companion navigates and the PC disagrees.** The navigator's beat stands; the PC may take the role
  instead at the next watch (one role per watch).
- **Supply at 0 and a hunt fails.** Want applies at dawn; the PC may keep hunting (one watch at a time) or
  turn back. Starvation is warned at three stacks (07.8.10): no one starves without being told.
- **Foraging in farm country.** The farmland's forage tier is Easy, and the food belongs to someone: a method
  consequence (01.11.2: a trace) and, if seen, `cost.exposure` toward the farmer's standing (15).
- **A site whose theme × domain gate is thin.** The 20 pairs listed in `sites.yaml#denizen_table_rule` use
  the theme gate alone: an icereach shrine of the hallowed dead draws ancestors and celestials who came
  there, though they would not live on ice. Thirteen may author better tables for any pair it places.
- **Out-of-band rows on a generic table at home band 5.** `home+1` is band 6, which does not exist: the row is
  fielded at band 5 as an elite (09.4.6) and its sign still carries the band tell.
- **A haven that becomes unsafe.** 11 writes `safe: false` (the town is sacked); the next watch there rolls the
  die at the place's new danger rating, which 11's world change also sets.

## State touched

- **Entities written:** places (regions, areas, settlements, sites, site areas, landmarks, buildings) and
  route links (10.1); features (06.3.8 kinds) on mention; pending threats (`enc.pending`, sealed);
  encounter participants (via 09's templates); the journey record; the venture record; the site record;
  trap instances; hazard instances on places; made traps; caches and found items (via 08's generator).
- **Facts written:** `loc.*.discovered` (with frame id when a frame found it), `known`, `journey_role`,
  `nav.lost` (sealed), `weather.today`, `weather.tomorrow` (sealed until forecast), `snow_lying`,
  `high_water`, `drought`, `scene.light`, `water_source` (daily), `camp.alarm`, `area.mapped_by_pc`,
  `area.occupants`, `went_without`, `rest_site`, `secured`, `roused`, `cleared`, `trap.*.jammed`,
  `harmful` food, `pc.on_venture`, `desecrated`/`consecrated`/`haunted`/`dead_ground` from site themes.
- **Quantities changed:** supply (consumption, foraging, hunting, spoilage), light-source intervals,
  ammunition (depletion), march units (per traveler and mount), progress points (journey), Vitality via
  `apply_harm` (07) from hazards and traps.
- **Conditions applied (06's ids):** `cond.exhausted` (forced march, want, cold and heat exposures, bad air,
  thin air), `cond.prone` (falls), `cond.restrained` (mire, quicksand, snares, nets), `cond.pinned` (deadfalls,
  slabs), `cond.bleeding`, `cond.burning`, `cond.choking`, `cond.blinded` (darkness), `cond.deafened`
  (lightning aftermath), `cond.surprised` (by 06.2.4 from this chapter's awareness facts).
- **Afflictions exposed (07's ids):** `aff.marsh_fever`, `aff.red_flux`, `aff.grave_chill`, `aff.rat_plague`,
  `aff.grey_spore`, `aff.nightshade` (harmful food), `aff.widow_venom`, `aff.wyvern_venom`, `aff.adder_venom`,
  `aff.drowse`, `aff.evil_eye`, `aff.wound_rot`.
- **Clocks created:** `clk.10.site_progress`, `clk.10.site_danger` per site (sensed, omens from the theme);
  dig and rite countdown clocks from site tables; run-down / quarry-away at travel scale (06's templates).
- **Tools used:** `advance_time`, `mark_boundary` (`venture_start`, `venture_end`, `mode_change`),
  `roll_table` (every table here), `create_entity`, `set_fact`, `seal`/`unseal`, `update_quantity`,
  `apply_harm` (07), `apply_condition` (06), `create_clock`/`tick_clock`, `frame_check`/`roll_check` (01),
  `oracle` (01), `generate` (08: caches, hoards), `threat_advisory` (09), `record_evidence` (03, through its
  counters `cnt.discovery` and `cnt.journey`), `get_state`.
- **Hooks subscribed:** none by effects of this chapter (its handlers are boundary handlers, depth 0);
  `on_fact_set` patterns are read by 03's counters (`loc.*.discovered`) — 03 owns that subscription.
- **Handlers registered:** T-10-23 (16 handlers; `data/boundaries.yaml owner-block 10`).
- **Visibility classes:** places discovered → shown; known-but-undiscovered → available (name only);
  undiscovered → sealed; supply, light, progress clock → shown; danger clock → sensed (existence shown, fill
  background); pending threats → sealed (their signs are narrated); `nav.lost` → sealed until its gate;
  weather today → shown, tomorrow → sealed until forecast; danger ratings and bands → available as words
  (T-10-2); hazard and trap entries → sealed until perceived, then available.
- **Runtime capabilities assumed:** RC-RNG, RC-STORE, RC-SEAL, RC-SCHED, RC-LOG, RC-DATA, RC-QUERY, RC-EVAL,
  RC-RETRIEVE (00.14.1).

## Interface requests

### Requests made of this chapter, and where each is answered

| From | Request | Answered by |
|---|---|---|
| 01 | hazard `resist` fields | `hazards.yaml` every entry `resist {verb, attribute, dc_tier, stakes}`; traps' `resist`; 10.12.1–10.12.2 |
| 01 | listening-clock tick sources `trait.sense.loud`, `cost.exposure`, `cost.time` | the site danger clock template `clk.10.site_danger` lists all three (10.13.8) |
| 01, 12 | falls of 20 ft and more are a Heavy (S3) source | 10.12.5; `haz.fall_20` notes; every height feature records `drop_ft` |
| 01 | site time per significant beat | 10.13.5, `h.10.site_time` |
| 02 | weather-ache reads the day's weather after `h.10.weather`; stonesense underground is Certain | 10.11.3 step 4; 10.4.7 item 4 |
| 03 | `loc.*.discovered` with its frame id | 10.1.5 (and `frame_id: null` for mere arrival, by design) |
| 03 | journey roles as facts per watch | 10.5.1 `journey_role {actor, watch, role}`; evidence tags in `travel.yaml#roles` |
| 03 | settlement ancestry on places | 10.1.6 `settlement_scope` |
| 04, 05 | place `resonance`; `desecrated`, `consecrated`, dead-ground facts; the weather record | 10.1.2, 10.1.7, 10.12.8, 10.11.1; hallowed/corrupted/wild themes write them (10.13.2) |
| 06 | hazards as features (`feature_kind: hazard`) with severity and cadence | every `hazards.yaml` entry carries `feature_kind: hazard`, severity, cadence; site domain features carry 06.3.8 kinds |
| 06 | `scene.light` | 10.7.2, T-10-9 |
| 06 | fall severities | 10.12.5 (adopts 06.5.8 / 07.10.3) |
| 06 | tracking a fled quarry or fleeing PC after `band.distant` | 10.10.7 |
| 06 | `tbl.chase_ground` may be replaced by regional tables | agreed; sites use their domain features as chase ground (10.13.11) |
| 07 | hazard `lethal_context`, `aftermath`, perceived on sight | every entry; 10.12.4, 10.12.10 |
| 07 | `place.rest_site`; no encounter check in a haven | 10.1.2; 10.2.3 |
| 07 | `h.10.supply` applies `cond.exhausted` per day without food or water | 10.6.2 step 4 |
| 07 | forced marches use the push-on rule | 10.3.5 |
| 07 | drowning and smoke use 07.10.4; want and falls take no reduction | 10.12.6; `haz.drowning`, `haz.smoke`; `no_reduction: true` on falls, want, cold, heat |
| 08 | capacity 10 + 2 × Might; 2 supply per load unit; lots of 2 per coin; torch 6 intervals, lantern 24 per flask | 10.6.1, 10.7.1 (consumed as given) |
| 08 | mounts' and vehicles' pace and carry; burdened/overloaded travel pace | 10.3.2, 10.3.7, 10.8; T-10-5 |
| 08 | place terrain tags and site bands open place-gated properties and set hoard bands | 10.13.10, 10.13.13; `sites.yaml` `loot_gate_tags`; site band = tier cap |
| 08 | harvest is an exploration activity of 1 interval or 1 hour | `act.harvest` (T-10-20) |
| 09 | encounters belong to places; T-09-10 budget; crowds as mobs; never two equal-band T4/T5; Δ 30/55/15 | 10.10.1–10.10.2, PR-10-8; every generic table audited 6/11/3 of 20 |
| 09 | out-of-band foes always warned | 10.9.5 item 4 (the omen already says it), 10.10.5 (09.6.6 at perception) |
| 09 | encounter distance and notice are 10's | 10.10.3–10.10.4, T-10-15 |
| 12 | watch/interval check rows may name `tbl.event_focus` | the V face (10.9.4) |
| 12 | 10 may opt in to read the pacing phase | 10.9.7 (one narrow, declared use) |

### What this chapter needs from, or offers to, other chapters

- **To 00 (amendments proposed; orchestrator decision):**
  1. **Place extension.** 00.6.2's `Place` gains the fields of 10.1.2 (`place_kind`, `band`, `danger`, `safe`,
     `rest_site`, `climate`, `nav_tier`, `forage_tier`, `game_tier`, `openness`, `landmarks`,
     `water_source`, `grazing`, `encounter_table`, `hazards`, `resonance`, `settlement_scope`, `known`,
     `site`, `state_log`) and the link fields of 10.1.3. Owners may add fields (00.6.2 says so); recorded here
     so the implementer sees them in one place.
  2. **Handlers.** T-00-9 gains `h.10.wayfinding` (watch, 4), `h.10.watch_exposure` (watch, 2),
     `h.10.site_exposure` (interval, 2), `h.10.site_recovery` (day, 6), `h.10.day_reset` (day, 9),
     `h.10.site_regrowth` (week, 6), `h.10.scene_frame` (scene_start and mode_change, 7). Contrib file:
     `data/boundaries.yaml owner-block 10`.
  3. **A quantity for travel.** T-00-13 has no quantity for travel progress; `speed` is 06's bands per move
     action. Proposed: add **`travel_points`** (points per travel watch, family `adjust`, cap: the pace ladder's
     envelope 2…12) so items and abilities can change journey speed through the substrate
     (`eff.10.travel_points` in `data/effects.yaml owner-block 10`). Until amended, no item or ability in the data
     touches journey speed; pace changes come only from 10.3.2's steps.
  4. **SCHEMAS.** `hazards.yaml`, `travel.yaml`, `sites.yaml`, `traps.yaml`, `weather.yaml` use the optional keys
     documented in each file's header (band-indexed tiers `dc_tier_by_band`, `severity_by_band`; sub-tables;
     `archetype_signs`; `terrain_defaults`; `states`; `climates`). The SCHEMAS sections should list them.
  5. **Glossary additions:** danger rating, home band, pending threat, omen-first rule, time-tick check (the
     die), face, lull, march allowance, forced march, journey role, way-finding, off course / the veer,
     progress points, telltale, site, theme, domain, area (site area), the heart, roused, secured, haven (this
     chapter's use of 07's word for a safe place).
- **To 01:** none required. (Optional integration note in 01.13.10: in site mode a `cost.twist` may read the
  site theme's `dangers` table instead of `tbl.twist` at S3–S4 — a better-fitting twist; not assumed here.)
- **To 03:** propose level-3 tags `terrain.ruin.fortress.tower`, `terrain.road.causeway`,
  `terrain.water.river.ford` (`data/tags.yaml`, adopted at integration); confirm `cnt.discovery` ignores `frame_id: null`
  discoveries (10.1.5) and `cnt.journey` reads `journey_role` facts as written.
- **To 09:** `archetype_signs` (travel.yaml) is this chapter's omen text per archetype (stage 1 and 2); 09 may
  move it into `archetypes.yaml` as a `signs` field at integration — a distinct thing from `tells` (a tell is
  what the creature looks like; a sign is the trace it leaves before it is seen).
- **To 11:** consume the venture record at `h.11.reckoning`; place `occupants`, `cleared` sites and `evaded`
  pending threats as World Turn inputs; `safe` changes are 11's writes; regional events table
  `tbl.<region>.events` (if 11 or 13 want region-specific V faces); calendar season ids for
  `h.10.weather_regime`.
- **To 12:** the V face calls `tbl.event_focus` (12.6.5 d); the time-tick die's results are a legal
  complication source (01.11.3 item 5); `[JOURNEY]` is an out-of-fiction block for 12.15 (format 10.3.4);
  12.4.6's skip narration reads this chapter's returned lists; the anchors of this chapter for
  `anchors.yaml`.
- **To 13:** for the starter region — places with every 10.1.2 field (or terrain defaults), route links with
  lengths in watches, danger rings per T-10-2, regional encounter tables in the two-sub-table shape (PR-10-8
  audit), regional `archetype_signs` and events, site placements with theme, domain, band, size and objective,
  havens (`safe: true`) and rest sites, `resonance` places, climate per region, weather regimes if the region's
  climate differs from the five.
- **To 14:** codex views — **Journey** (the plan, points, supply against need, light), **Map** (discovered
  places and links; known-by-rumor names), **Site** (progress clock, danger "sensed", areas and path, secured
  areas), **Weather** (today; tomorrow if forecast). The player's guide should say: the world shows its hand
  before it strikes (omens); the farther from home, the more dangerous; light and food are the delver's first
  supply; you can always take the long way or take your time.
- **To 15:** `act.search` and `act.study` are this chapter's exploration forms of investigation; a clue graph's
  placements may sit in site areas (15 places them, 10 generates the areas they sit in).
- **To 16:** journey roles (T-10-7) for companions; mounts as consumers and march units (10.3.5, 10.8.2);
  porters' carry; a companion scout starts encounters at `band.far` from the party.

## Open empirical questions

Each ships with the concrete default already in the rules and a named test.

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-10-1 | Is the encounter density right — enough to make travel matter, few enough that it is not a grind? | T-10-10 faces; threat share 25/58/75/83%; arrivals 0.38 / 0.57 / 0.77 / 0.89 a day | **T-10-DENSITY**: 30 simulated and 10 played travel days per rating; count encounters that produced a lead, a choice or a cost vs "filler"; target filler ≤ 1 in 3 and a player rating of "travel mattered" ≥ 4/5 |
| OEQ-10-2 | Do omens get answered? (the omen-first rule works only if players read signs) | one sign at creation, a second at arrival | **T-10-OMEN** (with 00's T-00-OMEN): share of first signs that draw an avoid / investigate / prepare / seek answer; target ≥ 50%; if lower, the lookout's extra fact becomes default for every omen |
| OEQ-10-3 | Is the site race calibrated (rousing a quarter of careful at-band delves)? | sizes 6/8, 8/8, 12/12; cadence 3/2/2/1 | **T-10-DELVE**: re-run `sim10_site2.py` with real beat logs from 5 played delves (other-beats-per-area and their success rate measured, not assumed at 1 and 0.6) and compare to 25% ± 10 at medium |
| OEQ-10-4 | Is getting lost too frequent for the unlicensed? | fallback +5 / Limited; take the time allowed to Hard | **T-10-LOST**: 20 trackless days by unlicensed PCs in play: how often did players choose take-the-time vs roll, and did being lost ever produce a dead end (P16)? target: no dead ends; ≥ 1 in 3 lost days led to a discovery |
| OEQ-10-5 | Does the daily weather persistence feel right? | d6 1–2 holds, else the regime d12 | **T-10-WEATHER**: 200 simulated days per climate × season: mean spell length of each state; target 1.5–3 days for rain and fair, ≤ 2 for storms |
| OEQ-10-6 | Do telltales prevent "gotcha" without making traps trivial? | plain from S3, subtle at S1–S2 | **T-10-TRAP**: 30 trap meetings in play: share where the player engaged the telltale before triggering; target 40–80% (below: telltales too subtle; above: too obvious) |
| OEQ-10-7 | Is the supply economy tight enough to make foraging and hunting decisions real? | 1 a day; +1 dry/hot; forage yields by reach | **T-10-SUPPLY**: 10 played ventures: count days with a supply decision (half rations, forage watch, hunt, turn back); target ≥ 1 per 3 days on ventures longer than 3 days |

