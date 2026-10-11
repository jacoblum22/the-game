# Fidelity audit B: engine shortcuts outside the fight code (branch spec033-base, 2026-10-11)

Scope: engine/ except ch.06, resolve/conflict.py, resolve/foe_act.py and the foe call (audit A). Read-only. Reach = `tests/guard/reached.txt`
(R = the recorded dm-tools game reaches it, N = pipeline-only or unreached) plus 13 dm-tools saves (225 turns, 34 committed frames, 74 OFFER blocks).
Impact: H = a player notices or the result is wrong, M = sometimes, L = cosmetic. "Silent" = no `not_chosen:` log, no `# coarse:`, no ponytail.

## 1. Not-in-the-code-comments gaps, found by grepping rule ids against callers (H first)

| # | What the rules say | What the code does (file:line) | Evidence | Imp | Reach |
|---|---|---|---|---|---|
| 1 | 01.16.2/01.16.3: fate is earned (hard luck, thread done, vow kept) and spent to reroll a seen die | Nothing earns fate. Only spend is the Threshold reprieve (harm/threshold.py:420). `roll_check(frame, env.rng)` passes no `on_roll` (resolve/pipeline.py:869; hook exists at roll.py:81-94). The OFFER still prints "Fate: N (you may spend one to reroll the die once you see it)" (dm/oof.py:453-455) and the help text promises it (dm/turn.py:526) | 73 of 74 OFFER blocks in dm-tools saves show the promise; no reroll path exists | H | R |
| 2 | 01.6.2 (deed tag, J:enum), 01.6.8 (levers/snags, J), 01.6.5 (nudge), 01.6.10 (reach WHOLE/ONE FACTOR), 01.4.7 (secret), 01.3 traits incl. `loud` | `propose_roll` has no field for any of them. `code_framer` takes `_framer_default`: deed tag = first of the anchor's list (dm/schemas.py:538), levers/snags `[]`, nudge 0, traits `[]`, secret False, reach Standard (dm/schemas.py:535-546, dm_tools.py:1004-1052). Silent | 34 of 34 frames: 0 levers, 0 snags, 0 traits, 0 consequences, 0 secret, nudge 0. Observe is always `deed.lore.investigation`, Talk `deed.influence`, Handle `deed.craft`, never tracking, insight or medicine (14 of 129 anchors list several). Competence, the +2/-2 swing, noise and Limited reach are never used | H | R |
| 3 | 15.3.2: request size R1-R5 is the Framer's pick; DC +0/+2/+5/+8/+10 | `request_size` is the constant "R2" (dm/schemas.py:541). DM has no field. DL-01-33(d) says "the Framer's pick, as the engine does" | 6 of 6 Talk frames: DC 12 opposed (10 + R2's +2), whether it asked directions or a leader's name at sword point | H | R |
| 4 | 00.7.3: the DM classifies the time mode at each scene start (default previous, uncertain = free); only significant beats cost an interval; DL-01-50: take-the-time costs minutes | Every dm-tools place scene is forced to `site` (dm_world.py:65-70 "assumption A1", dm_tools.py:1504). Every non-idle exchange costs one 10-minute interval, `significant=True` hard-coded (dm_world.py:73-83). The mode's own handlers are unbuilt (`h.10.site_time`, `site_check`, `light`, `site_exposure`) | Talker save 005927: 17 turns, 17 interval boundaries + 2 hours; 17 skips each of site_check/light/site_exposure. A 17-turn chat is ~3 hours | H | R |
| 5 | 07.6.1/07.2.9: when the PC goes Down the victor's `defeat_disposition` runs (captive, robbed, left); waking after an interval is only "if nothing took it" | `_wake` says "no victor in M1 takes a Down PC: nothing runs a disposition" (dm/turn.py:846-866). `run_disposition` is called only from the Threshold (harm/threshold.py:385) and a yield (exits.py:106) | save 073517 turn.26: officer drops PC to 0, "out cold for 10 minutes... the fight is over", officer unchanged, nothing taken (1 of 1 Down) | H when it happens | R |
| 6 | Ch.05 tool 19 `use_ability` (05.4.1): activate abilities, spend Focus | `abilities/use.py` (`check_use`, `commit_use`, `offer_view`) has no caller outside tests; no DM tool; only recharge handlers run. Event families `effect_applied/expired` (effects), `tally_settled` (growth), `offer_*` are refused as NotBuilt (store/events.py:628-634) | Characters are created with abilities and Focus; none can act | H | N (never reached) |
| 7 | 01.10 / T-01-6: deliver N items by reach; player ranks; undelivered stay unresolved. 01.15: Oracle answers open world questions | dm-tools bypasses the answer ladder and has no Oracle tool (dm_tools.py docstring lists the other bypasses, not the Oracle). Reach of an Observe/Recall success limits nothing; the DM says what is found (`answer.deliver_count` N; only `oracle.positive` R) | no tool; coverage lists 01.10.1-.7 and 01.15.4-.6 as `to-build` | H (design bypass, undocumented) | R |
| 8 | 07.2.4/07.2.5/PR-07-2: every wound gets a record (site, status penalty, restriction, max-Vitality -2..-4, healing clock); 07.8.10 `h.07.fatigue` (no sleep = exhausted) | Wound load is counted, no record: `_coarse_wound` (harm/apply.py:176-185), brink penalty skipped (apply.py:377), light/moderate "nothing to heal" (harm/rest.py:173), no fatigue. All logged only to `log.coarse` | Staggered/Dying PCs have no leg/arm/head effect; staying awake costs nothing | M | R |
| 9 | Ch.10 travel (weather, light, supply, wayfinding, watch checks), ch.11 world turn, ch.03 growth, ch.04 callings, ch.08 upkeep | 80 of 105 boundary handlers are unbuilt (10 of the 35 marked M1: `ruling_log`, `scene_cleanup`, `bent_offer`, `site_time`, `scene_frame`, `fallback_counters`, `session_open/close`, `mode_change`, `h08.durations`). Travel is `advance_time` by link length (world/places.py:291-310). The PC never advances (no `tally_settled`, no `grant`) | 136 `handler_skipped` events in one 27-turn save (073517) | M-H (grows with game length) | R |
| 10 | 01.4.2 let it ride: a failure stands too; a ride ends on a changed lever or superseded fact | `_rides` covers success only, ends at scene end (resolve/pipeline.py:637-653, ponytail) | not counted; a failed attempt can be retried at once | M | R |
| 11 | Ch.08 making/mending; DM may set `change_kind=make` | Rolled, then refused "not built yet (ch.08)" (resolve/change.py:404-405) | the player rolls for nothing | M | R |
| 12 | 15.7.1 price bands by request size | `change coin amount` is any positive figure (dm_tools.py:1355-1385); `deal_price` runs only on the pipeline's deal path | no band check | M | R |
| 13 | 11.13.3 epilogue steps 2,5,7-9 (settlement, bequests, timeskip, successors, inheritance) | Not built, logged `log.coarse` (dm/ending.py:12-18, 141) | the recorded game retires and starts a fresh character | M | R |

## 2. The ponytail / "not yet" comments (every one outside audit A)

| Where | Rule skipped | Matters in play? | Imp | Reach |
|---|---|---|---|---|
| dm/world_step.py:438 (owner's example); dm_world.py:140 companion target | 06.2.2 tempo order; 06.9.3 band check | Audit A's. The module docstring (world_step.py:5) still says "no round-by-round conflict" though conflict exists: stale | - | R |
| resolve/pipeline.py:637 `_rides` | 01.4.2 | see 1.10 | M | R |
| resolve/pipeline.py:1060 `_cleanse` | 00.9.1 | A stated beat with no target (or the holder) of a cleanse verb ends the condition: "aimed at" is inferred from the target, a VIII.9 inference | M | R |
| resolve/necessity.py:67 `certain_talk` | 15.3.10 hesitation test, certainty size, ceiling | Dead on dm-tools: `Beat.asks` is never set (Beat built at dm_tools.py:788-795 sets no `asks`), so talk is never "certain"; the DM decides whether to roll | L | R |
| resolve/frame.py:422 `alternatives` | 12.15.2 | "Another way" odds reuse the current competence | L | R |
| resolve/gate.py:120 `active_effects`, :220 `_plain_cover` | 00.12.3 | licence-rank effects uncollected; two covering licences picked by price | L | R |
| resolve/costs.py (no comment): `cost.gear` S2 writes the literal place "left behind", S4 only `broken`; `cost.drain` picks focus/supply/ammo/light by fixed order | 01.13.4, 01.13.3 | a string is stored where the rule says a named place or the foe's possession | M | R |
| store/views.py:63, text/render.py:151, gen/_seed_lib.py:248, audit/fallback.py:135, world/places.py:256 | perf, grammar number, reused given name, 200-char clause drop, a heard place is a 1-interval passage | cosmetic; places.py:256 matters only if the DM could name a far place (it has no tool) | L | R |
| dm/npc_layer.py (x8), dm/packet.py (x2), dm/testimony.py (x3), dm/roles/reader.py (x3), roles/framer.py:180, dm/turn.py:429, dm/player_text.py:137, store/details.py:47, store/views.py:45, audit/* (x7), dm/dispute.py (x2), dm/narration.py:233, dm/answer.py:82, resolve/oracle.py:39, resolve/gate.py:234, resolve/frame.py:819 | 12.11.9 NPC layer (tags `names_object`, `asks_truce`, `harms_innocent` "never fire"), 12.3 claim checks, 01.15, T-01-6 Exceptional bonus | All pipeline-only. Many are word lists, so each is a VIII.9 violation if the pipeline is ever run; DL-12-161 says deletion is spec 033 R13 | L (dm-tools) | N |
| `# coarse:` tags (23 in engine/ outside conflict.py): harm/*, dm/turn.py (07.5.9 Last Stand is "the next whole turn" not three actions; 07.5.10 Gamble has no confirm; 07.8.2 rest site guessed from place kind), abilities/recharge.py:66, dm/ending.py | ch.07, 05.6.10, 11.13 | see 1.5, 1.8, 1.13; Last Stand is M | M | R |
| `# TODO` dm/context.py:44, game.py:59 | 12.3.6 dispute default; cross-family checker | none on dm-tools | L | N |

Unbuilt-and-uncommented: the coverage tool (engine/build/coverage.py) lists 315 rules as `to-build` (untagged, "triage is open work", specs/004/coverage-m1.md, 2026-10-07); a grep of 1.1-1.13 above came from that list. It was never re-run into the ledger.

## 3. Logged defaults on the dm-tools path (`_default(` / `not_chosen:`), 225 turns: 11 turns carried one

| Field (file:line) | Class | Note |
|---|---|---|
| `cost_form` (dm_tools.py:385, costs.py:471) | STANDS-IN | the rule gives the pick to the DM (DL-01-60); omitted = first listed (least severe); 0 seen |
| `fail_on` (pipeline.py:1093-1105; dm_tools.py:968) | STANDS-IN | code chooses who notices, which item is lost, who refuses (01.13.4/.6/.9); 6 of 225 turns, the commonest default |
| `force` 948, `foes.<id>` + `.target` (dm_world.py:133,142), `fight.starts` 891 | STANDS-IN | ch.06 choices; audit A |
| `fight.to` 894/1279, `position` 918, `change_whom` 979, `who` 1183, `what` 1206 | OMITTED-DETAIL | start band, who moves; fine under D3 |
| `weapon` 962 (from the `wields` fact), `as` 683/1297 (they), `name` 1303 (rolled), `npc_leaves.to` 1289 (off-scene) | OMITTED-DETAIL | fine |

Silent stand-ins (no log, so D3's count under-reports): deed tag, request size R2, levers/snags/traits/reach/secret (1.2, 1.3); forced `site` mode and one interval per exchange (1.4); `rest what=` unknown kind becomes `rest_short` (dm_tools.py:1318); rest site "haven if settlement/building else camp" (turn.py:757); PC wakes after one interval (1.5); `cost.drain` quantity order. Default-logging catches only the fields someone remembered to log.

## 4. Decisions made on stale or lost information

| Item | Mechanism | Imp |
|---|---|---|
| Accepted "try it anyway" re-frame | The DM's attribute, difficulty, stakes and `fail_cost` live in `t.env.proposal`, set only in the proposing turn (dm_tools.py:807). The redirect pause stores no proposal (pipeline.py:834-847), so the answer turn frames with the empty default (Safe, first attribute, easy tier; dm_tools.py:1006). Seen once in 13 saves (011012, seq 729), which led to no roll; code-traced only | M |
| Success ride (1.10) | A stored success is applied to a later beat without re-checking the lever, fact or target state it rested on | M |
| `_witness` (dm_world.py:187-195) | A short clue node is told to the DM once, then `told_short` suppresses it; if the DM ignores it the node stays short. DL-12-160's revisit trigger ("three triggers ignored") has no counter in engine/ | M |
| Footing options (costs.py:376-440, :466-479) | Options computed at roll time, written after the DM's tool calls in the same turn, not re-checked | L |
| Rest quality and site (turn.py:757-761 then rest.py:105) | Fixed at the start, applied at the end | L |

## 5. Rules revisions that describe a shortcut

| Entry | Finding |
|---|---|
| DL-01-33 (c),(d) [R2-G, I-160] | "this documents the engine's behaviour" for 15.3.10 and 15.3.2. Clause (d) says the Framer picks the request size; on dm-tools nobody does (1.3) |
| DL-12-160 [R2-M] | Retires the lead write and the audit's placing of a clue reserve (15.9.4). The "at least two live sources" guarantee became a note the DM may hold. Soft-lock risk accepted, no measurement in code |
| DL-12-128/-130 [R2-L], dm_tools.py:1116-1117, :1230 | Rules: the ceiling grid binds (provisional). dm-tools: `mood` is "no roll, no ceiling [owner ruling 2026-10-10]" and `asks` is "never a gate". No DL records this ruling; the rules still say the opposite, though DL-01-60/-61/-62 claim "these rules describe the target both engines answer to" |
| DL-01-50 / 00.7.3 [R2-L] | Rules: unlisted beats take no time but take-the-time (minutes). dm-tools charges 10 minutes per exchange (1.4); the revision is not honoured on the live path |
| Whole dm-tools engine (specs 031-033) | Pipeline, Director scene cuts, Oracle, NPC layer, answer ladder are replaced; rules ch.12/01.15 were not revised for it. The departures live in specs and code comments only |

## The pattern
- Each rule is built for the case the code could do (a table, a constant, the first list entry) and the judgement part the rule gives to the DM is replaced by a default: deed tag, request size, levers, reach, mode, observer, footing form.
- The default is silent more often than it is logged; the D3 `not_chosen` count therefore reads clean while the roll odds are not the rules' odds (every Talk is DC 12; no roll uses a lever).
- Player-facing text promises more than the code does (the fate line, the reroll help). The promise was written for the rule, the code was never connected.
- Gaps are tagged `# coarse:` by milestone ("M2", "M3"). Nothing ever moved a milestone that the dm-tools engine made impossible to reach, such as ch.05 abilities, wounds and Down dispositions.
- Rules prose was updated to bless the engine (DL-01-33) or left unrevised after a spec departed from it (mood, time, Oracle), so rules and code both claim to be the target.

Unverified: how often 1.10 (ride) and 1.12 (coin) bite in play (no counts); the 315 `to-build` ids beyond those spot-checked; the redirect re-frame (code-traced, no frame seen after it in saves). The saves are offline-DM stub games (passage "x"), so DM-side behaviour was not sampled.
