# Spec 032: made-up cases, edge cases and the enumerations (committed before any implementation)

Owner rule (DL-00-08, DL-00-10): every fix passes made-up cases and edge cases **plus the save it came from**, and
breadth cases are **enumerated from the game's data**, not imagined. Each case below is labelled **data** (one per
kind in a table the test walks, so a new kind without a case fails), **save** (from the traced save or round-8/9
saves), **made-up** (a plausible play situation) or **edge** (a boundary of the rule). Each becomes a test in
`tests/engine/test_spec032_*.py` (offline, scripted DM model); the model-facing ones are also items of the labelled
sets (`heldout.yaml`, phase 1) measured on Haiku.

**Held-out rule.** Phase 1 writes `specs/032-dm-tools-mvp/heldout.yaml` (24 items: 6 prose-only targets, 6 fight
exchanges, 6 said/told passages, 3 presence, 3 pronoun) with labels **before any model sees them or any fix
exists**. Only phase 7 runs it. If a fix is tuned on it, the set is spent and phase 7 says so.

Counts below were read from the data on 2026-10-10 (`rules.ids(...)`, `pacing.yaml`, `resolution.intended_change`).
Each test asserts its table's length so a changed data file fails loudly.

## R. People and things that exist only in prose (G4) - resolver

| # | Kind | Case | Expected |
|---|---|---|---|
| R1-R15 | data: the 15 verbs (`verb.endure ... verb.talk`) | `propose_roll` with that verb and target "the pale beast" (prose only) | the target is made (creature, `mind: animal`), the roll is gated/framed as for an entity; never `REFUSED: no one on record` |
| R16 | save | fighter turn 9: target "the beast in the clearing" | same; one entity, reused on turn 12 ("the pale beast") by alias |
| R17 | save | explorer/scripted: "the carter at the well", "the lead guard" | a walk-on with that role, here, `name_known` false |
| R18 | made-up | plural "the carters" | a group NPC (as `cast_described`) |
| R19 | edge | the DM's name matches an existing entity's alias/role | reuse it, no duplicate |
| R20 | edge | "the beast" while an entity "beast" exists in another place | the one here; if only elsewhere: refused as not here (spine) |
| R21 | edge | empty / "none" / "world" | no target (as today) |
| R22 | edge | a named person who is dead or down | refused with the reason (spine, today's `_acting`) |
| R23 | edge | the same description twice in one turn | one entity |
| R24-R33 | data: the 10 DM change kinds (+ `fight`, 11) with `who`/`to` in prose | each kind accepts a prose-only person where a person is valid (coin payee, give_item receiver, condition on, npc_leaves, fact subject...) and refuses where not (e.g. `travel`) | per kind |

## F. Fights (G1, G7, G8) - the foe turn

Foe outcomes the code has today (`conflict.foe_beat`, read from the code, one case each):

| # | Foe state | Expected `foe_beat` result |
|---|---|---|
| F1 | held by the PC | breaks free (or fails to) |
| F2 | prone | gets up |
| F3 | not engaged | closes one band |
| F4 | engaged, d20 misses the PC's Guard | "strikes at you and misses"; no harm |
| F5 | engaged, hit | harm applied by code at the line's severity |
| F6 | engaged, critical | one rung more severe |

After a hit the PC's harm ladder (`engine/harm/state.py`; verify the names in the phase): F7 staggered, F8 down (the exchange ends, `_wake`), F9 dying
(`dying_check` at turn end), F10 threshold (`_harm_followups`; the PC may die). Each F7-F10 is walked once.

| # | Kind | Case | Expected |
|---|---|---|---|
| F11 | save | replay fighter turns 9-15 on the new code | a `conflict_start` at the first committed attack; one foe turn per non-paused exchange; no refused `propose_roll`; Vitality moves only by rolls or foe turns |
| F12 | save | turn 11 context ("roll away ... then swing again") with the fight facts shown | the DM proposes the swing now (5 samples on Haiku, report k/5; not a code check) |
| F13 | made-up | two foes, one drops mid-exchange | `able()` skips it; `check_end` ends the fight when none is able |
| F14 | made-up | the PC talks (shouts) during a fight | the foe still acts (a turn is spent; refused/withdrawn beats spend nothing, 01.3.6) |
| F15 | made-up | the PC flees (verb.move) | bands widen; foe closes; no strike while not engaged |
| F16 | made-up | an NPC turns on the PC (DM calls `change fight who=npc`) | `conflict.start`, the first foe turn runs as a roll; harm by code; not by prose |
| F17 | edge | the OFFER is open | no foe turn this turn (pipeline: a pause skips the world step); it runs on the answer turn after `_resume` |
| F18 | edge | the PC's roll kills or downs the foe | no foe turn from it; the DM narrates the end; `conflict_end` fires |
| F19 | edge | PC already Down/Dying | the foe turn does not run past the Down rules (`_turn_end` first) |
| F20 | edge | no conflict (a talk scene) | no foe turn; zero extra DM calls |
| F21 | edge | a fight with a creature (`mind: animal`) | foe line from `adversaries` if the description matches an `adv.*` (156 entries), else the default line (`beh.default_beast`) |
| F22-F25 | data: foe behavior defaults (`beh.default_melee`, `default_beast`, `default_mob`, `default_ranged`) | which line each uses | M1 uses `default_melee` only (ponytail comment in `foe_beat`); the test records that ranged/mob fall back to it |
| F26 | edge | the nonlethal flag on the PC's blow | the harm rules still read the method's words (`NONLETHAL`); the foe goes Down not Dead |

**OFFER words (G8)**: O1-O9 data: each of the 9 `cost.*` ids (`closed_door, drain, exposure, footing, gear, harm,
shortfall, time, twist`) offered as `fail_cost` on a verb it fits: accepted by `frame_check` or falls back to the
first acceptable source, never raises. O10 save: turn 12's title "Hurt the beast's lunge" becomes the DM's goal words.
O11 edge: `fail_cost` not in the menu for that stakes source. O12 edge: no goal words (default title as today).

## T. Time and the world (G2) - the world step

Modes (`clock.MODES`, 5): T1 site (1 interval per significant exchange), T2 free (0 unless listed), T3 travel
(1 watch), T4 downtime (listed days), T5 conflict (1 round per exchange). Each asserts the clock delta after one
plain talk exchange.
- T6 edge: `advance_time` returns an interrupt: the DM is told, the scene is cut (reason `interrupt`).
- T7 save/made-up: a clock ticks on an interval boundary: its omen text is a fact in the next DM context.
- T8 made-up: eight inconclusive talk exchanges raise `trg.lead_injection`; `inject_lead` writes a lead; the DM is
  told what arrived (data, not "toward X", DL-12-139).
- T9 edge: `beat_end` marked once per exchange, and `dead_air` increments only on quiet exchanges.
- T10 edge: a turn with a refused/withdrawn beat spends no time.
- T11 edge: a paused (OFFER) turn spends no time; the answer turn does.
- T12 save: the fighter save's "afternoon" at hour 0: after the change, hour advances; the DM's "Now:" line moves.

### Scene cuts (`pacing.yaml#scenes.cut_triggers`, 7): one case each

| # | Trigger | dm-tools decision |
|---|---|---|
| C1 | agenda_answered | not applicable (no agenda); asserted never to fire |
| C2 | place_change | already handled (`_sync_scene`, `travel`) |
| C3 | time_jump | cut in code; the DM is told |
| C4 | interrupt | cut in code; the DM is told |
| C5 | conflict_end | cut in code at the next exchange |
| C6 | player_cut | the DM's `travel` is the cut; asserted not double-cut |
| C7 | dead_air (`dead_air_turns` = 2) | cut in code, not an offer line (no Director) |
After each cut the mood hold resets (D3: once per scene); a new `mood` roll is made on the next ask.

## J. Told: what NPCs say reaches the journal (G3)

The DM's `said` list, per question kind (`QUESTION_KINDS`, 7): J1 none, J2 who_is, J3 where_is, J4 what_happened,
J5 what_like, J6 what_want, J7 who_knows - each walked: a said record with speaker, place, day; shown in "what you
were told" as `X told you: "..."`; never a world fact; `settle` untouched.
- J8 edge: the speaker is absent, dead or unknown: dropped and logged (`told_dropped`), not written.
- J9 edge: the same line twice in a scene: one record (`testimony.is_repeat`).
- J10 edge: empty `said` (the DM omitted it): nothing written, nothing breaks.
- J11 edge: the PC's own words are never a said-to-PC record.
- J12 save: the talker save (Ivette, Tobbo, Kazain lines) - the journal shows them, attributed.
- J13 edge: a clue delivered through `reveal_clue` is a `learned` fact (as today) and is not also written as hearsay.
- J14 made-up: "what do I know about X" after three said records about X lists them with speaker, place, day.

## I. Items (G5)

Per DM change kind that moves a thing (`give_item`, `new_item`, `coin`): I1 give_item PC to NPC, I2 NPC to PC, I3 NPC to
NPC, I4 from a person not holding it (refused), I5 to someone not here (refused), I6 `new_item` that duplicates a
held item (echoed as a fact), I7 coin from no source (refused), I8 coin overspend (refused), I9 NPC with no purse
pays "from their own means" (as today). I10 save: the C-fighter knife made with `new_item` instead of moved; the
echo names the existing one. I11 edge: a loose item here (no holder) can be given by anyone present. I12 log-only:
a passage "hands you a loaf" with no change call is logged, never blocked, precision measured on the labelled set.

## Q. Presence and pronouns (G6) - four pronoun sets x presence states

Pronoun sets in the data: `she/her`, `he/him`, `they/them` (groups), `it` (creatures). Presence states: here, elsewhere
(met), dead, down, left this turn, never met.
- Q1-Q4: the card shows each pronoun set (data).
- Q5-Q8: "Not here:" lists met people who are elsewhere/gone (3 states) and omits never-met people.
- Q9 save: round-9 Octette Vasac (record he/him) - 5 passage sentences flipped to "her": the log-only check
  flags them; the labelled set records precision; **no block**.
- Q10 edge: two people named in a sentence (no verdict, as `_pronoun_hit` already).
- Q11 edge: a PC pronoun ("you") never flagged.
- Q12 edge: absent named person in passage but named in the recent conversation: not flagged.
- Q13 save: C-fighter "an officer who is not present": logged as `absent_named`.
- Q14 spine: every tool refuses an absent, dead or down actor (R22 + `_acting`), one revision then dropped and logged
  (cases E1-E5 below).

## L. Leak audit (G9)

L1 save: the 10 false flags (NPC's name + "matter") do not flag after name tokens are removed. L2 made-up: a real
leak (a sealed fact paraphrased with 60% of its content words) still flags. L3 edge: a secret made only of a name
and common words (fewer than 3 content words left) is skipped. L4 edge: name tokens of every entity, not just the
holder. L5 edge: multi-word names ("Octette Vasac"). L6 edge: a clue delivered by `reveal_clue` this turn is not a
leak (as today).

## E. One revision, then drop (the enforcement contract)

E1 dead actor, E2 absent actor, E3 item not owned, E4 coin from no source, E5 sealed secret outside the clue rule
(data: the 8 incident kinds' sealed answers). For each: the first breach returns `REFUSED: <reason>` and the DM
may revise once (existing tool loop); a second breach on the same call is dropped and logged in `screen.dm_tools.
dropped`; the turn never fails. E6 edge: a breach inside the last tool slot (no revision left): dropped and logged.
E7 edge: "nothing done to the PC without a roll": a `condition_add` or harm on the PC outside `propose_roll`/the foe
turn is refused (this is new: today `condition_add` on the PC is allowed). E8: `condition_add` on an NPC is allowed.

Conditions (data, 33 `cond.*`): K1-K33 walked on an NPC (apply, then remove; an unknown id is refused with examples)
and on the PC (refused unless the roll/foe turn made it, E7). `wound_*` (4) and `unconscious` look harm-owned (they come from `apply_harm`): the phase checks in the code whether the
DM may add them today and, if so, refuses them (proposal; not verified in this design slice).

## S. Resuming keeps the engine (G10)

Stored `engine` in {missing, "pipeline", "dm-tools"} x the caller's `GameConfig.engine` in {default, "pipeline",
"dm-tools"}: S1-S9. Expected: the save's value wins (missing = pipeline); a `dm_secrets` value likewise. S10 edge: a
save with an open OFFER resumes into the right engine's `play_answer`. S11 edge: replay (`Game.replay`) redrives with
the stored config. S12 save: the fighter dm-tools save reopened with a default config stays dm-tools.

## X. `/fix` on dm-tools turns (G11) - states x report kinds

Turn states (5): X1 plain talk, X2 an OFFER open, X3 a rolled and resolved turn, X4 a turn with `change` calls, X5 a turn
with a `reveal_clue`. Report kinds (`DisputeKind`, 4): explained, corrected, taken_back, not_found. Walk the 5 x 4 =
20 cells with the scripted Fixer (offline), each: the correction turn recorded, the Fixer's tool output includes the
DM tool log for that turn, `Now:` shown, no crash. Live (Sonnet): the 4 saved complaints from the head-to-head
(`B/C` runs: "Kazain has not come down", "the bowl", "afternoon", "Changed: your opponent worn") must be repaired or
explained; reported as k/4 against the pipeline's. X21 edge: `/fix` with an OFFER open reframes with the code
framer (no Framer model call). X22 edge: `/fix` right after a clue: a correction never delivers a clue (INV-10).
X23 real (P6, pinned-trace.md): save 175211 turn.16, "pinned" with no holder: the Fixer sees `cinst.1` came from
turn.4's footing cost and `remove_fact` with that `cinst.1` takes it off (`Now:` shows it). Live set: `evals/feedback_corpus.py --set dmtools`
(4 saved, the pinned one, 4 made-up; labelled in tests/fixtures/feedback_corpus/dmtools.json before any run).

## N. NPC agency and the mood-and-cost probe (G13)

The 12 cells of T-12-19 (3 moods x 4 costs): N1-N12, plus the 4 repeat-ask probes (A7, A8, A10, A11) N13-N16, run on
both arms. Measures: M1 grant rate by mood and cost, M2 ceiling violations (the pushover rate), M3 in-character
refusals, M5 repeat caving, M8 voice distinctness, M10 leaks. The cost of each ask is **fixed by the cell** (not read
from the DM's `asks`), so the ceiling log's weakness (the DM listing its own asks) cannot hide a violation.

## P8a. The people and things the DM names (written before the code; the 24 held-out items are SEEN and are not tuned on)

Traced causes (heldout.json, P7 saves): H02 the DM made the seller with `new_npc who=npc.eel_seller` (the game gave her `npc.orla_tanner`),
then aimed the roll at `npc.eel_seller`: `_party` returns an id-shaped string as written, so it was refused. H03/H04 `PERSON_VERBS` is a hand
list (talk, strike, grapple, help): sneak and observe are not in it, so "the rider on the grey horse" is returned as written and refused. H06
force is not in it either: "the stuck hatch" refused, and a strike at a hatch would have been made a person. H01 the wolfhound was made, but as
a human NPC ("Lom Underhill", role wolfhound): `ANIMAL` matches the head noun only after a space, so "wolfhound" is no creature (the scorer's
"no hound entity" is that). The three P7 `said` drops: `_told` never makes a speaker; `travel` moves only the PC (Dunbert).
Rule being built: each verb's target kinds come from `rules/data/basic_verbs.yaml` (the `against` text and the `targets` knob: person,
object, both with the first-named kind first), the DM's `change_kind` slot kinds (`resolution.yaml#intended_change`) break a tie, and an object or
a feature is never refused: the roll is on the obstacle named in words. A person or creature named in prose is made as a walk-on.

Enumerated from the data: the 15 verbs x {a person phrase, a creature phrase, an object phrase} = 45 cells; the 4 `said` speaker shapes
(id, role phrase, invented id, name) x 5 states (here, elsewhere, dead, not in the passage, repeated).
- P1 data: `target_kinds` for the 15 verbs equals what the YAML says (talk, grapple, sneak, help person-only; strike, force, setup person then
  object; observe, handle, move object then person; exert, endure object; recall, evade, ready none).
- P2 matrix: 15 verbs x person ("the sentry on the wall-walk"), creature ("the wolfhound"), object ("the stuck hatch") through `_party`+`_propose_roll`:
  never "no one or nothing on record"; a person phrase for a verb that takes a person is one walk-on; a creature is `mind: animal`; an object
  phrase for an object-first verb makes no entity.
- P3 real (H02 replay): `new_npc who=npc.eel_seller` then `propose_roll talk target=npc.eel_seller`: the roll targets the one seller made, not a second.
- P4 edge: an invented-looking id never made by `new_npc` (`npc.rider_on_the_ridge`, observe; `npc.watch_sentry`, sneak) is the DM naming a walk-on.
- P5 edge: an invented object id (`object.stuck_hatch`, force) is not refused and makes no person.
- P6 edge: an invented id whose words match someone here (`npc.harbour_watch` -> Sela Vey) is that person, not a second one.
- P7 made-up: strike at "the stuck door" with `change_kind=open` is an object (no person called "stuck door").
- P8 made-up: "the wolfhound", "a sheepdog", "the deerhound" are creatures; "the houndsman", "the dogcatcher", "the horse trader" are people.
- P9 real (J, P7 explorer): `said` by "the carter at the trough", present in the passage and not on record: made as a walk-on, the line is filed.
- P10 edge: `said` by an invented id (`npc.longbridge_man`) whose words are in the passage: made, filed.
- P11 edge: `said` by a role phrase that is nowhere in the passage ("the ghost of nobody"): dropped, "no one on record".
- P12 edge: `said` by someone recorded elsewhere or dead (by name or by the role phrase): dropped ("not here" / "dead"), no second person made.
- P13 real (B, P7 talker): `travel` with `who="Dunbert"` takes her along; two travels in a row, she is still here, `reveal_clue` works, her lines are filed.
- P14 edge: `travel` with no `who`: nobody else moves (explicit, no code guess); `travel` with a `who` that is not here, dead or unknown: travel
  still happens, the output says who stayed and why.
- P15 edge: `travel` with `who` naming two people (comma list) takes both.

### P8a revision [orchestrator design steer, same day]: code does no name matching

Fragility ruling: an exact id (or the exact name, or the id the DM chose for `new_npc` this turn) is that entity; anything else the DM names is
NEW. Code makes a minimal walk-on with the DM's words as its role/alias and tells the DM its id ("(New on record, here now: <words> (<id>). Use
these ids from now on.)"); the situation block lists it with the id. Changed cases (the tests carry the same numbers):
- P6 replaces the old P6: "the rider on the grey horse" then "the horseman" are two walk-ons; the situation shows both ids and the DM's words;
  using the id is that entity. P6b: 100 ways of introducing someone (10 adjectives x 10 roles, incl. invented `npc.` ids): 100 distinct walk-ons, nothing refused.
- P8 stays for the *kind* only (`ANIMAL`: a made walk-on is a creature, `mind: animal`); it is never used to find an existing entity.
- P11: a said line that is not verbatim in the passage is dropped whoever the speaker is; a verbatim line by an unrecorded speaker (any words) is a new walk-on's.
- P12: a speaker on record elsewhere or dead is dropped when named by id (or exact name); a role phrase for them is a new person (the DM must use the id).
- P13-P15: `travel` `who` is a comma list of ids (an exact name also works); the old head-noun/role matching cases are gone with the code.
Removed from the code: `_labels`/`_speaker` label matching, `find_existing`/`cast_described` reuse in `_party`, the head-noun reuse of P3 ("the pale beast" ->
"the beast in the clearing"), the group walk-on for plurals. P3 tests R1/R16/R17-R20 were rewritten for it.

## P8b. Fights and costs (written BEFORE the fixes; the held-out set is spent and is not used here)

Traced causes (from `heldout_run/heldout.json`, the P7 saves and a replay of H07 offline):
(1) `code_framer` asked `schema_context` for the cost menu without `cost_menu_ids`, so in a scene with no scene facts the
menu was `cost.twist` alone and every `propose_roll` was refused ("cost.twist only when no other entry is a candidate"):
H07/H10/H11 had no roll, so no foe turn. (2) A fallback of `threatened[0]` of the first source = `cost.harm` (tie order)
whenever the DM's `fail_cost` was not legal in any source: "you get hurt" for reading tracks (talker turn.9: the DM said
`cost.time`, no clock existed). (3) `code_framer` never sets `trait.delivery.melee`, so a PC melee Strike writes no contact
band (`_contact`): the seeded `near` stays and the foe's first acts are band moves. (4) `changed_line` writes
"<name> <state>" with no verb ("your opponent worn"). Rule 06.3.9: the DM sets each participant's start band from the
scene; unestablished is `near`.

Data enumerated: foe action kinds (`foe_beat`): break free (held; miss / success / critical), stand (prone), move toward
(band `close`/`near`/`far`/`distant` -> one nearer), close to `engaged`, strike (miss / hit / critical hit): 11 kinds.
Starting ranges (`conflict.BANDS`): engaged, close, near, far, distant. Informational verbs (basic_verbs covers "search,
study, listen, read", "common knowledge"): `verb.observe`, `verb.recall`. Cost ids (9): the DM's `fail_cost` enum.
State words (`state_words`): fresh, worn, bloodied, staggered, down, dying, dead, "down and dying", "down, out cold".

- **R1-R5 starting range (made-up).** `change fight who=<foe> to=<band>` for each of the 5 bands seeds exactly that band; the
  first foe turn is a strike for `engaged`, "closes in, now at arm's reach" for `close`, "moves toward you" for the other three.
- **R6 default.** `change fight` with no `to`: band `near` (06.3.9). **R7 edge.** `to` is not a band ("across the moon"): the fight
  starts at `near`, the output says so, nothing is refused (no new block). **R8 edge.** `to` given for a foe already fighting:
  the band is unchanged (06.3.9 is the start only). **R9 edge.** `to` is an id-like or capitalised word ("Close"): read as `close`.
- **M1-M3 melee contact (made-up, the P7 fighter trace).** A PC `verb.strike` / `verb.grapple` / `verb.force` at a person in
  the room with no range stated: after the roll the pair is `engaged`; the foe's first turn is a strike, never "moves toward you".
- **M4 edge.** A strike after `change fight to=near` (a thrown knife across the room): no melee trait, the band stays `near`,
  the foe's first turn is "moves toward you". **M5 edge.** A strike with the foe already `close`: melee, engaged after the roll.
- **X1-X4 exchange endings (data: open pause stages offer, near_miss, go-big re-offer; settled).** With the OFFER open, with a near-miss
  menu open, after `go_big` (the same offer shown again): zero foe turns and no time spent. The answer that settles the roll:
  exactly one foe turn per foe (two foes: two turns, one each).
- **K1-K11 every foe action kind.** One exchange each, state set by the case (hold, prone, each band, die forced): exactly one
  foe turn, the words below. K1 held, fails to break free; K2 held, breaks free; K3 held, critical (tears free, PC off
  balance); K4 prone, stands; K5-K8 `close`/`near`/`far`/`distant`: one band nearer (K5 reaches `engaged`: "closes in");
  K9 engaged, misses; K10 hits (Vitality drops); K11 critical hit (one rung more). K12 edge: a downed foe gives no turn.
- **C1-C9 a scene with no scene facts (the held-out refusal).** Strike at an engaged foe in a bare scene, one case per
  `fail_cost` id (9): the roll is OFFERED (never "NOT POSSIBLE"), and the threatened cost is the DM's when legal there.
  **C10 edge.** The refusal text, if a frame ever fails, never names `cost.twist` unless the twist is the DM's own choice.
- **I1-I10 informational verbs.** `verb.observe` x 5 DM choices (none, harm, time, exposure, drain), `verb.recall` x 5: the framed
  threatened cost is the DM's choice when legal in some source, else the first legal of the verb's list in the data, and
  `cost.harm` only when the DM chose it AND it is legal; "you get hurt" never appears for a failed read when the DM chose
  `cost.time`/`cost.exposure`/`cost.drain` or nothing. **I11 edge.** A listening clock exists (`cost.time` becomes legal): the
  threatened cost is `cost.time`. **I12 edge.** No cost of the verb's list is legal and the DM asked for risky: the roll is
  Safe (made at once, failure costs nothing), not harm.
- **L1-L9 the Changed line.** For each state word, a hurt foe with a known name: "Changed: Milby is worn"; with an unknown name:
  "your opponent is worn". **L10 edge.** The PC and the foe both lose Vitality in a beat: "Vitality 12 → 9 · bloodied · Milby is
  worn". **L11 edge.** A foe that is dead / down and dying: "is dead", "is down and dying".
