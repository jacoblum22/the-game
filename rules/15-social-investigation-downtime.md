# 15 — Social, Investigation, and Downtime

> This chapter governs the three pillars where the player's tools are words, wits and weeks: talking
> people into things (and out of them, and around them), finding out what is hidden, and spending time in
> safety to heal, learn, earn and build. All three are where an AI Dungeon Master is most dangerous. The
> research shows a language model adjudicator grants unearned success far more often than it demands a
> needless roll, that a persuasive-sounding player argument roughly **quadruples** that error, that
> model-voiced characters are biased toward agreeing and never walking away, and that a secret held in the
> narrator's context leaks. So this chapter does what 00 does everywhere, but harder: every NPC carries
> **pre-committed state** — a standing on a seven-rung scale, ranked wants, fears, and **refusals no roll
> can pass** — written before the player opens their mouth; every social outcome is a check against a
> defense composed from that state and from the **size of what is asked**; the only things that move the
> numbers are **facts** (a want served, a payment, leverage, an obligation, evidence, a friend's word),
> never the eloquence of the player's prose; every lie becomes a recorded belief with a sealed truth and a
> clock that can bring it out; every mystery is a **sealed clue graph** with at least three ways to every
> conclusion it needs, a guaranteed core clue at each, and a proactive fallback, so it can never dead-end
> and never leak; and downtime is a closed, clocked week-planner where new capabilities are learned only
> through the acquisition paths Principle VII names. The player may attempt any gambit; the world answers
> it consistently.

---

## Design intent

**Goals served.** Goal 1 (the player feels free to try any creative idea) is served by making *every*
social approach legal (Talk is a basic verb: persuading, lying, threatening, bargaining, performing,
flattering, pleading, provoking — all G1) and by giving each a real, priced chance, a reason to try a
different angle when one fails, and an answer that is never a bare wall: a refused request names what
would move the person; a missed clue is never the only clue; a capability the character lacks names the
teacher, the text or the deed that would grant it. Goal 2 (the AI responds and reacts correctly) is served
by moving every social and investigative number out of the narrator's taste and into stored state:
standing, request size, terms, plausibility, patience and alertness are rungs and flags read off the NPC's
record; clue access is a lookup in a sealed graph; downtime is an engine schedule [BRIEF §3; C:VII; C:P16;
C:P17].

**The central finding this chapter is built against.** CoC-Seduce (20 models, 5,376 adjudications) found
false passes outnumber false checks about 120 to 1, and that a pseudo-logical player justification raises
the false-pass rate from 3.82% to 17.30% [R4 §1, W2; R: https://arxiv.org/abs/2607.02802]. LLM-simulated
customers who in reality would not buy halved their expressed resistance and "ask about price" instead of
leaving [R4 W4; R: https://arxiv.org/abs/2606.20708]. A detective-game player extracted a premature
confession from 10 of 33 LLM suspects by citing invented "GPS evidence"; gating each clue node behind
prerequisites cut that to 0 of 33 [R4 W2, §5.1; R: https://arxiv.org/abs/2609.23043]. And a model
restricted to public history provably cannot keep a hidden answer both secret and consistent, while a
secret in context is guessable from the prose up to 79% of the time [R4 W7; R: https://arxiv.org/abs/2601.06973;
R: https://arxiv.org/abs/2605.10794]. Every one of these failures has the same cure: the decision the
model would be seduced into making is either pre-committed in state, computed by a tool, or reduced to a
yes/no question about a cited fact whose worst wrong answer costs one step [00.2.1 P-A, P-B].

**How creativity is rewarded in talk.** The research's answer for action resolution — reward the
*leverage* an idea exploits, never the prose [R7 §3.3 F3] — is applied here with a social vocabulary. A
player who finds out what the miller wants and offers it has done something; a player who writes a
moving paragraph about the miller's duty to his neighbours has not, unless the paragraph names a fact
(the miller's daughter lives in the threatened village: that is a want, and it pays). This keeps the
best part of goal 1 — talking is where players are most creative — while making the AI's job the one it is
good at: classifying the player's words into a closed list of facts [R4 S1]. PF2e's Influence subsystem
reaches the same design from the other side: its stat blocks deliberately make plain Diplomacy "rarely the
best skill", so that players must *discover* an NPC's interests and cater to them [R: https://2e.aonprd.com/Rules.aspx?ID=1201].

**What this chapter deliberately avoids.**
- *Rolling the NPC's mind.* Wants, fears, refusals and secrets are written at generation (12.11.1) and
  never decided mid-conversation. The DM voices people freely; it never decides what they will agree to
  except through the frame [R4 §9 10 #2; 12.11.3–12.11.4].
- *Description-graded rewards* (Exalted stunt dice, Wushu detail-counting): rejected because taste is the
  judgment an AI applies least consistently and most sycophantically [R7 §2.20, §2.22].
- *All-or-nothing social rolls.* A failed request is a "no" plus a declared cost; a near miss can be
  taken as a partial yes at a price; a big request can be pursued over several scenes on clocks, and won
  with a compromise (Burning Wheel's Duel of Wits: the winner still owes a compromise proportional to the
  ground they gave) [R: https://forum.rpg.net/index.php?threads/explain-burning-wheels-duel-of-wits-to-me.760950/].
- *Mysteries that hinge on one roll.* GUMSHOE's founding observation — plots stall when a vital clue sits
  behind a failable roll — is adopted as a rule: every needed conclusion has a core clue that reaching its
  holder with a fitting method delivers without a roll; rolls buy extra findings, time and safety
  [R: https://pelgranepress.com/gumshoe/files/GUMSHOE%20SRD%20CC%20version.pdf; R5 P-41].
- *A DM who confirms theories by saying so.* A player's deduction is confirmed only by evidence in the
  fiction or by a deterministic check that the clues the player cites actually entail it; the sealed
  solution never moves to meet a clever theory.
- *Downtime as a montage that grants power.* Weeks pass through `advance_time` (every boundary runs,
  INV-15); learning is a clock with fixed weekly ticks from a teacher, a text or practice; a roll never
  grants a license (INV-7); training evidence counts at most half of a calling's counted requirement
  (04.3.3) [C:P15].

**Pattern compliance.** P16 is architecture here: refusals redirect, investigations have ≥3 placements
per needed conclusion and a proactive fallback, the journal always shows live leads. P17 is applied to
every investigative and insight beat through 01.10 and 12.10.4. VII governs downtime learning: licenses
come only through `acquisition_paths`. P3: the NPC social record and the clue graph are background-
resolved richness the DM reaches into; the player sees standing names, the journal and clocks. Deviations
from any Pattern are recorded in DL-15.

---
## Rules

Rule ids are `15.S.R`. Kinds per 00.2.2. Digest shorthand per 00.1.6. Rules marked `Anchor: yes` are entered
in `data/anchors.yaml` at integration (T-15-20 lists them with their knobs).

### 15.1 Standing: what it means, where it starts, how it moves

**15.1.1 Standing.** `[D]` **Standing** is the signed relationship scale of 00.3.16 — **−3 Hostile, −2
Unfriendly, −1 Wary, 0 Neutral, +1 Warm, +2 Friendly, +3 Devoted** — held as a `relationship` (00.6.1) from
one entity toward another (`set_relationship(npc, pc, kind: standing, …)`). It is directional: the miller's
standing toward Wren is not Wren's toward the miller (the PC's feelings are the player's, and are never
tracked). Every NPC who has interacted with the PC holds exactly one standing toward the PC
(`NPC.standing_to_pc`, 00.6.2); NPCs may also hold standing toward companions (16) and toward one another
where a rule needs it (15.1.8). **Visibility** (00.6.3): the rung *name* is `available` to the player
through the codex; the number never appears in fiction. Standing is never picked freely: it changes only
by the `[D]` steps of 15.1.5 (SG-02) [00.3.16; R6 §B.3 B-R2; R: https://bladesinthedark.com/the-faction-game].

**15.1.2 The behavior contract.** `[D]` Each rung is a contract the NPC keeps whatever the narrator's mood,
in the style of Blades in the Dark's faction status, where every status rung is "an explicit behavioral contract
an AI can follow literally" [R6 B-02]. T-15-1 (canonical: `data/social.yaml#standing_effects`) fixes, per
rung: the **social DC modifier** (15.3.3), the **ceiling** — the largest request Talk can obtain without
terms (15.3.4), the NPC's **patience** per scene (15.2.6), its **price shift** as a trader (15.7.4), what it
does **unasked**, what it **shares**, and how it is **voiced** (12.14.7).

**T-15-1 The standing contract.**

| Rung | DC mod | Ceiling | Patience | Price shift | Unasked, they… | They share… | Voiced as (12.14.7) |
|---|---|---|---|---|---|---|---|
| −3 Hostile | +5 | none (only with terms; 15.3.4) | 0 (parley and terms only) | will not trade | act against the PC when it costs them little: report, obstruct, attack if able and their behavior list allows | nothing; lie when it suits them | open enmity, refuses dealings |
| −2 Unfriendly | +3 | R1 | 1 | asking +1 notch | hinder quietly when safe; never help | only what costs nothing and hurts the PC | curt, suspicious, unhelpful |
| −1 Wary | +1 | R1 | 2 | asking +0 | carry on with their own business | public knowledge only | guarded, measured, gives little |
| 0 Neutral | 0 | R2 | 3 | asking +0 | carry on; answer civil questions | what anyone in their role would say (R1 information) | businesslike |
| +1 Warm | −1 | R3 | 3 | asking +0 | small courtesies; warn of an obvious danger | private but harmless things (R2 information) | friendly tone, small courtesies |
| +2 Friendly | −3 | R4 | 4 | asking −1 notch | go out of their way: pass on news that touches the PC, shelter them for a night | confidences that do not betray others (R3 information) | goes out of their way |
| +3 Devoted | −5 | R5 | unlimited (never walks away from the PC) | at cost (list −1 notch, never below the 08.8.7 floor) | take risks for the PC; seek them out with anything that matters to them | anything they know that their refusals allow | would take risks for the PC |

*Why these numbers.* The DC modifiers make the ceiling request about equally hard at every rung (T-15-3):
a commoner (defense 10) asked for exactly their ceiling faces DC 11–15 from Wary upward, and a request one
rung above the ceiling is not a harder roll but a different kind of problem (terms, or a campaign). The
asymmetry (Hostile +5 but Wary only +1) reflects that strangers in a classic-fantasy world are a little
guarded (12.11.2's reaction mean is −0.25) and that ill will costs more to overcome than goodwill buys
[DL-15-01]. *Simulation:* `scratchpad/social15.py`, exhaustive d20 under 01.8.1.

**15.1.3 Faction members: personal offset.** `[D]` Q13 (00.17.1) puts individuals and factions on one
scale: a faction member's default standing toward the PC is the faction's **status** toward the PC (11),
and 12.11.2's member roll shifts it by at most one. This chapter keeps the two in step by storing, for each
member, a **personal offset**:
- `offset = standing − status`, set when the member's standing is first written (the member roll's −1/0/+1)
  and **recomputed whenever a personal step (15.1.5 sources 1–6) changes the member's standing**.
- When 11 changes the faction's status, every member's standing is recomputed as
  `clamp(status + offset, −3, +3)` and logged with reason `faction_status`. That recomputation is not a
  personal step: it does not change the offset. When the offset is positive, the recomputed standing may
  not exceed the higher of the faction's status and the highest **source cap** (15.1.7) among the member's
  own positive steps — so a member whose regard was built from small kindnesses tops out at Friendly
  however the faction's mood swings (WE-15-6).
So a member the PC has never dealt with simply follows the faction; a guard the PC once spared (offset
+2) stays two rungs warmer than her captain's grudge; a guildmaster's daughter who has become Devoted to
the PC while the guild is at war (offset +6) stays Devoted. Individuals and factions diverge exactly as far
as personal history has pushed them, and no further — Mount & Blade's per-lord beside per-kingdom relations, made
deterministic [R6 B-09; 00.17.1 Q13; DL-15-02]. The recomputation runs in `h.15.member_standing`
(`week`, phase 6, after `h.11.world_turn`) and immediately on any status write 11 makes outside the turn.

**15.1.4 Starting standing.** `[D]` Standing toward the PC is written once, at the NPC's **first
interaction** with the PC, and never chosen:
1. A **bond** NPC (02.9.2): the set value of the bond kind (anchor kin/friend/ward +2, mentor +1 [verification: V2b-021]; thorn rival
   −1, creditor 0, enemy −2), reason `bond` [02.9.2].
2. A **faction member** (00.17.1 Q13): the faction's status plus the member roll (12.11.2 step 1).
3. **Anyone else**: the reaction roll, 2d6 plus at most ±2 in cited modifiers, bounded by a cast NPC's seeded
   stance (12.11.2 step 2) [revision: R2-J; DL-12-107]: ≤2 Hostile,
   3–4 Unfriendly, 5–6 Wary, 7–8 Neutral, 9–10 Warm, 11+ Friendly; **never Devoted** as a first impression.
4. **Adversaries** met outside a fight: only if their archetype has `reaction_roll: true` (09.2.7); a
   `cunning` mind met in a fight starts Hostile; a `mindless` one has no standing at all.
The NPC's standing exists in state from that write onward; the claim check (12.3) flags any narration of
attitude before it exists (claim class `attitude`). Starting standing is a first impression, never a
verdict: everything in 15.1.5 moves it [12.11.2; 02.9.2; 09.2.7; R5 AV-07].

**15.1.5 How standing moves: the closed list of sources.** `[D]` [DL-15-03; DL-15-04; C:I; R5 NP-03; revision: I-065] Standing changes only through these
sources, each writing `set_relationship(npc, pc, steps, reason, source_ref)` and a memory (12.11.7):
1. **A Talk frame's delivered reach** on a win-over (15.4.2) — +1 step, never above Warm.
2. **A cost**: `cost.closed_door` at S3 (−1) and S4–S5 (−2) (01.13.9).
3. **A deed** the NPC did, witnessed, or was told of, through its memory valence (15.1.6).
4. **A gift** given with nothing asked in return (15.1.7): +1, never above Friendly.
5. **A kept or broken commitment** involving the NPC (a promise, a debt, a deal; 15.7.6), through
   15.1.6's `promised`, `owed` and `betrayed` rows.
6. **Intimidation that succeeds, or leverage used** (15.4.3, 15.3.5): −1 at `scene_end` (fear is not regard).
7. **The faction's status** for a member (15.1.3), by recomputation, not by step.
8. **An ally's regard or grievance clock completing** (16.5.3): +1 or −1 for that ally
   [integration: IR ch.16 to 15 (a)].
Nothing else moves standing. In particular: the passage of time does not warm or cool anyone; a long,
pleasant conversation with no frame does not; the DM's sense that the NPC "would come round by now" does
not (12.11.6) [00.3.16; SG-02].

**15.1.6 Memory valences to steps.** `[D]` + `[J:flag]` [DL-15-03; C:III; revision: I-065] Chapter 12 writes an NPC memory for every beat that
touches them (12.11.7), with one **valence** from a closed list. This table (T-15-2, canonical
`data/social.yaml#memory_steps`) is the one mapping from memories to standing steps; it applies at RECORD
of the beat that wrote the memory (the NPC's attitude changes in the scene, not later), except
`threatened`, which applies at `scene_end` (the NPC complies now and resents afterward).

**T-15-2 Memory valence → standing step.**

| Valence (12.11.7) | Step | Condition / magnitude rule | Cap from this source |
|---|---|---|---|
| `helped` | +1 | the help was worth at least an R2 favor to them (15.3.2: it cost the PC a day, a Unit of coin, or a real risk) | Friendly; Devoted only when the help was R4+ (saved a livelihood, a life, a kinsman) |
| `helped` (rescue) | +2 | the PC saved them or their kin from S4+ harm, death, captivity or ruin | Devoted |
| `harmed` | −1 / −2 / −3 | the harm or cost to them, their kin or property was S1–S2 / S3 / S4+, or killed kin | none |
| `lied_to` | 0 | they do not yet know (15.5.3) | — |
| `caught_lying` | −2 | they learned the PC deceived them (15.5.5) | none |
| `impressed` | +1 | they witnessed a resolved deed that serves one of their recorded wants or matches their role's values (a knight sees mercy; a smith sees fine work); at most once per NPC per season | Friendly |
| `insulted` | −1 | the PC's words or act were recorded as an affront (a taunt that landed, a refusal of hospitality, mocking their faith); at most once per NPC per scene | none |
| `owed` (the PC owes them) | 0 | the debt is leverage *for them*; repaid on time → `helped` +1 | — |
| `owes` (they owe the PC) | 0 | a term the PC may call (15.3.5 Leverage); calling it in clears it without a step | — |
| `promised` | 0 | kept → +1 (as `helped`, cap Friendly; a kept R4+ promise may reach Devoted); broken → `betrayed` | — |
| `betrayed` | −3 | a promise, oath, deal or trust they relied on was broken by the PC | none |
| `spared` | +2 | the PC held their life or freedom and gave it back (a yielded foe let go, a thief not handed over) | Devoted |
| `threatened` | −1 | at `scene_end` after a successful intimidation or a leverage term against them | none |

*Heard of, not witnessed.* An NPC who learns of a deed only by report (12.10.6 c, `how: told`) takes at
most **±1** from it, and only when the deed touched their kin, allies, faction or wants.

```
### 15.1.6  Memory magnitude                                         [J:flag] [D]
Trigger [T]:        12.11.7 writes a memory with a valence whose row in T-15-2 has a magnitude condition
Loads in:           situation.social.*, core while an NPC is present
License check:      —
Decisions (J):      1. MAGNITUDE [J:flag] "Does this memory's deed meet the row's condition?" True only
                       with a cited state fact: the frame's cost severity (harmed), the request rung of
                       the help as 15.3.2 classifies it (helped), the recorded relationship to the victim
                       (kin, ally, member), or a want record (impressed). False when the condition rests
                       on the narration's tone. Uncertain -> the smaller step.
Computation [D]:    set_relationship(npc, pc, step, reason: memory, source_ref: memory id), clamped
                    -3..+3 and to the row's cap and 15.1.7's caps; offset recomputed (15.1.3)
State writes:       relationship; memory (12's); npc.<id>.small_steps_week
Narration may not imply: a change of attitude larger or smaller than the step
Worst case (J):     one step too many or too few for one NPC (class i), auditable from the memory's
                    cited frame; the uncertain tie-break errs toward the smaller change.
Examples:           inside: Wren carries the miller's wounded son two miles to the healer (S3 harm
                      prevented, a day's work) -> helped, R3 -> +1 (cap Friendly). boundary: she pulls him
                      out of the millrace as he drowns (death prevented) -> rescue +2 (cap Devoted).
                    inside: a shove that spilled a merchant's wares (S1 cost) -> harmed -1. outside: the
                      same shove spilled nothing (no cost) -> insulted at most.
                    non-example: "She'd be moved by how I nursed him, surely +2" -> the step follows the
                      cited cost and request rung, never the description of the nursing.
Anchor:             no
Basis:              [12.11.7] [R6 B-19] [R4 W4] [DL-15-03]
```

**15.1.7 Ceilings by source and the pace of small kindnesses.** `[D]` Four rules keep standing honest:
- **Talk alone makes acquaintances, not friends:** a win-over (15.4.2) never raises standing above Warm.
- **Gifts and small favors make friends, not devotees:** a gift (worth at least **1 Unit** of the NPC's
  weekly lifestyle, 08.8.6; an NPC's lifestyle is their role's, `data/social.yaml#npc_lifestyle`), an
  `impressed` memory, or a Cultivate day (15.13.6) raises standing at most to Friendly. A gift to an NPC
  whose refusals include `will not take a bribe` raises standing only when nothing is asked in the same
  scene; with a request attached it is a bribe, and the refusal applies (15.2.3).
- **Devotion is earned by deeds of weight:** Devoted is reached only by a step from a rescue, a sparing, a
  kept R4+ promise or an R4+ help (and, for an ally, its thread's completion, 16.12.3). A creation bond is
  a starting standing, never a source: it starts at +2 at most (02.9.2), and a bond NPC reaches Devoted by
  the same deeds as anyone [revision: I-072].
- **The weekly cap on small sources:** win-overs, gifts, Cultivate days, `impressed` and the plain
  `helped` row together give at most **+1 per NPC per week**; an ally's regard-clock completion counts against
  this cap unless the cycle that filled it held an R3 tick (shared danger) [integration: IR ch.16 to 15 (a)].
  Deeds of weight (rescue, spared, R4+ help, kept R4+ promise) and every negative step are uncapped. One
  exception restores a loss: **amends** in a confrontation (16.5.9) restore the step just lost, once per
  confrontation, and are not limited by the win-over's Warm ceiling [integration: IR ch.16 to 15 (b)]. The counter is `npc.<id>.small_steps_week`,
  reset by `h.15.standing_week` (`week`, phase 9).
*Why:* the agreeable-NPC failure is not one giant false pass but a slow drift of everyone toward the PC;
these caps make friendship take the time it takes in fiction (Starforged's connections progress by
relationship rank, not by conversation count) [R5 P-27; R4 W4; DL-15-04].

**15.1.8 Standing between others.** `[D]` [DL-00A-27; DL-12-10; R5 NP-03; revision: I-065] Standing toward companions (16) uses this chapter's rules with
the companion in the PC's place. NPC-to-NPC standing is written only when a rule needs it (a rival's
grudge that a Talk exploits, a council member's ally): it is generated at need by the reaction roll with no
modifiers (12.11.2 step 2), or by the Oracle when the two are already connected in state ("are the
reeve and the miller on good terms?", Even), and moved by the same sources. Faction-to-faction relations
are 11's.

**15.1.9 Standing is behavior, not a number.** `[N]` [DL-15-01; C:P3; revision: I-065] The narrator voices standing through the row of
T-15-1 (12.14.7): manner, what the NPC volunteers, what they withhold, what they call the PC (by name only
once they know it, 12.10.2). *Narration may not imply:* a rung other than the stored one; warmth that
promises a grant the ceiling forbids ("of course I'll help you break him out" from a Neutral jailer); a
change of heart without a step in the log.

### 15.2 The NPC's social record: wants, fears, refusals, patience

**15.2.1 The record.** `[D]` + `[S]` Chapter 12 generates people in three depths (walk-on, recurring,
principal; 12.11.1) and writes every field from tables at once. This chapter owns what the social fields
*mean* and adds the fields the social rules read. The NPC shape of 00.6.2 is extended (Interface requests):

```yaml
NPC (social fields; 15 owns semantics):
  standing_to_pc: int            # -3..+3 (15.1)
  faction_offset: int|null       # 15.1.3, for faction members
  wants:                         # recurring: 1; principal: 3, ranked (12.11.1)
    - {id, text, verb, object, tags: [tag], rank: int, status: open|fulfilled|abandoned,
       known_to_pc: bool, served_by: str}          # served_by: the fact pattern that serves it
  fears: [{id, text, tags, known_to_pc}]           # recurring+: 1
  refusals:                      # recurring+: 1 rolled; more from costs, oaths, roles (15.2.4)
    - {id, kind: refusal_kind, text, strength: absolute|lifts, lifts_when: fact_pattern|null,
       lifts_at_standing: int|null, source: generated|closed_door|oath|archetype|duty, known_to_pc}
  patience: {max: int, left: int}  # per scene (15.2.6)
  alertness: [{toward: id|"intruders", value: unaware|suspicious|alert|alarmed, since: time}]  # 15.5.7
  beliefs: [lie_id]              # what they believe that is false (15.5.3)
  lifestyle: id                  # their role's lifestyle (social.yaml#npc_lifestyle), for gifts and payments
  mind: mindless|animal|cunning|sapient|alien     # from the archetype (09.2.7); people are sapient
  speaks: [lic.lang.*]
```

Wants, fears, refusals and secrets are **sealed** until the PC learns them (00.6.3: "NPC wants, refusals,
knowledge, secrets — sealed until learned"). The engine uses them in every computation regardless — a
term matches a sealed want, a refusal blocks a request the PC did not know it would block — and the
narrator receives only their permitted slice: the NPC's demeanor, register and habit, and at most an
atmosphere tag (12.10.3). *A walk-on has no wants, fears or refusals yet.* The moment a Talk frame targets
them they are promoted to recurring (12.11.1) and those fields are rolled **before the frame is built**,
so nothing about the NPC is invented to suit the request [R4 §5.2 item 1 "seal at creation"; DL-15-05].

**15.2.2 Wants: what they do.** `[D]` + `[J:flag]` [DL-15-12; DL-15-34; DL-12-13; revision: I-065] A want is the NPC's own goal in their own terms
("make whoever ruined my father pay what is owed"), read from `tbl.npc_want_verb` × `tbl.npc_want_object`
(12.11.1). Wants are the main thing the player can *find out and use*. A want:
1. is a **term** when a request or the PC's offer serves it (15.3.5 Want);
2. makes a deed an `impressed` memory when the NPC witnesses the PC serving it (T-15-2);
3. is the target of a **Cultivate** day (15.13.6) and of favors that build standing;
4. is a source for lead injection (12.8.2 source 5: "an NPC with an unfulfilled recorded want who could
   plausibly seek the PC out") and for the NPC's own initiative (the narrator's reaction from the want, 12.11.5) [revision: R2-L];
5. is what a persuasion campaign's compromise asks for (15.8.2);
6. makes a request that defeats it one rung larger and never certain (15.3.2, 15.3.10) [revision: I-074].
*Serving a want* `[J:flag]`: *"Would the offered act or thing, if delivered, advance this want as written?"*
True only when the want's object and the offer match by id or tag (the want names "their daughter's
future" and the offer is an apprenticeship for the daughter, a fact); false for a general benefit the
want does not name (coin offered to an NPC who wants revenge). Uncertain → false. *Worst case (J):* one term
wrongly allowed = one request rung (class i), auditable by the want id.
*Fulfilled and new wants.* When a want's `served_by` fact is written, it becomes `fulfilled` (and a
`helped` memory is written if the PC served it); at the NPC's next scene the engine rolls a replacement at
the same rank. A want can be `abandoned` only by a fact that makes it impossible (its object destroyed).

**15.2.3 Refusals: the hard "No".** `[J:flag]` + `[D]`

```
### 15.2.3  Refusal                                                 [J:flag] [D]
Trigger [T]:        GATE of any Talk beat (or any beat whose intent is an NPC's decision) targeting an
                    NPC who holds refusals
Loads in:           situation.social.*, core while an NPC is addressed
License check:      basic verb: verb.talk (G1); the refusal makes the INTENT G4, never the attempt to speak
Decisions (J):      1. COVERS [J:flag] per refusal: "Would granting this request require the NPC to do
                       what this refusal's kind names (T-15-6)?" True only when the request's act falls
                       in the kind's inclusion list. False for acts in its exclusion list. Uncertain ->
                       true: the refusal holds (SG-05's grant-side tie-break).
                       Whose act [D] [revision: I-054]: the test reads the act granting requires OF THE
                       NPC. A refusal whose kind `reads: conduct` (T-15-6: wilds, place, fight, bribe,
                       past, oath, magic, lend, open_law) covers only the NPC doing that thing; asking
                       them to let, send, equip or advise someone else to do it is not covered (it is
                       sized as any request, 15.3.2: the ferryman who will not enter the marsh may still
                       lend his punt or name his nephew). A kind that `reads: outcome` (family,
                       innocent, master, and the oath-, duty- and archetype-sourced kinds) covers any
                       act of theirs that knowingly brings the outcome about, including helping another
                       bring it about (telling a killer where the child sleeps is covered by
                       `innocent`).
                    2. LIFTED [J:flag] (only if strength = lifts): "Is the refusal's lifts_when pattern
                       satisfied by a fact in state, or is standing at or above lifts_at_standing?" True
                       only with a cited fact id or the stored standing. Uncertain -> false.
Computation [D]:    covered and not lifted -> G4 for this intent (01.3.7 test 1: success would require
                    an established fact -- the refusal -- to be false). No roll, no lever, no term, no
                    standing, no eloquence passes it. The NPC's patience loses 1 (15.2.6). The redirect
                    (01.3.6) names, in the NPC's own voice, what WOULD move them: the lift condition if
                    the refusal lifts, a smaller request outside the kind, or another person.
                    The refusal becomes known_to_pc = true (the PC now knows this person's line).
Stakes:             none (no roll)
State writes:       refusal.known_to_pc; patience; ruling record (kind g4); journal entry (15.9.16)
Narration may not imply: that the NPC is wavering, could be talked round, or might do it for a better
                    offer (unless the refusal lifts and the redirect names the lift)
Worst case (J):     a request wrongly blocked: no roll happens and the redirect names the refusal's class,
                    so the player can see and dispute it out of fiction, and the ruling is reviewable
                    (class iv); a covered request wrongly allowed is the error the tie-break is set
                    against, and it still faces the full social DC (class i).
Examples:           inside: the ferryman "will not leave this place"; Wren asks him to guide her across
                      the marsh to the drowned chapel -> covered -> G4; redirect: "He won't leave the
                      ford. His nephew knows the marsh paths, and the ford is hers if he goes."
                    boundary: the same ferryman asked to row her across his own ford at night -> not
                      covered (the ford is his place) -> an ordinary request (R2: bends the curfew).
                    inside (lift): the ferryman's ford is burning (a fact) -> lifted -> the request is
                      framed normally.
                    non-example: "I explain how much good it would do -- surely he'd make an exception
                      for this" -> an argument is not a lift; the refusal holds; asking again in another
                      phrasing is the same intent (01.4.2).
Anchor:             no
Basis:              [12.11.4] [R4 W4] [R: https://arxiv.org/abs/2606.20708] [DL-15-06]
```

**15.2.4 Where refusals come from.** `[D]` Closed list of sources; each writes a refusal object (15.2.1):
1. **Generated**: one at recurring depth from `tbl.npc_refusal` (12.11.1), whose 12 rows map one-to-one to
   the kinds of T-15-6 with their default strength and lift.
2. **Closed door**: `cost.closed_door` at S4–S5 writes a refusal of kind `pc_requests` ("will not deal with
   the PC") with `lifts_when` naming its condition ("until the debt is paid", "until you bring proof") —
   the condition is the cost's form, chosen from the NPC's wants or the matter at hand (01.13.9).
3. **Oath**: an NPC under an oath or vow recorded as a commitment (11; a knight's oath, a priest's vows)
   holds a refusal of the oath's prohibition, `absolute`.
4. **Archetype**: a creature's `parley_when` and `yield_when` (09.7.6) and a foe "that will never yield"
   (06.11.7) are refusals of classes `parley` and `yield`, lifting when the field's condition holds.
5. **Duty** (principal NPCs and faction officers only): the role's one inviolable duty, written at
   principal depth from the faction's `duties` (11) or, absent that, by `tbl.npc_refusal` re-rolled until
   it names a duty-relevant class. Ordinary rules of a place ("the gate shuts at curfew") are **not**
   refusals: they are facts that make a request bigger (15.3.2), and they can be bent.
A refusal never appears because the DM decides a person "wouldn't do that". If no refusal covers a
request, the person *might* do it, at a price the frame states. *Absolute* refusals are rare by
construction: 3 of the 12 generated kinds (T-15-6) [DL-15-06].

**T-15-6 Refusal kinds** (canonical `data/social.yaml#refusal_kinds`; rows 1–12 = `tbl.npc_refusal`).
Each kind also carries `reads` (15.2.3 COVERS): **conduct** for rows 2, 3, 4, 5, 8, 9, 10, 11, 12 (only the
NPC's own doing is covered) and **outcome** for rows 1, 6, 7 and the closed-door, archetype, oath and duty
kinds (any act of theirs that knowingly brings it about, including helping another) [revision: I-054].

| # | Kind (`tbl.npc_refusal` text) | Covers (inclusions) | Does not cover (exclusions) | Strength | Lifts when |
|---|---|---|---|---|---|
| 1 | `family` — will not betray their family | acts that harm, expose, endanger or work against a recorded kin member | acts merely without kin's approval | lifts | a fact that the kin betrayed, disowned or endangered them |
| 2 | `open_law` — will not break the law openly | breaking a law where they could be seen or known to have done it | quiet rule-bending no one checks; acts sanctioned by an authority they recognize (a warrant) | lifts | the law's authority is gone (the lord fallen, the town under an enemy) or an authority they recognize sanctions it |
| 3 | `wilds` — will not go into the wilds or the dark | leaving road and settlement for wilds, ruins or underground | travel on roads; their own cellar | lifts | their kin or their want is in that place and in danger |
| 4 | `bribe` — will not take a bribe | accepting payment to breach a duty or a rule they keep | honest pay for honest service; a gift with nothing asked (15.1.7) | absolute | — |
| 5 | `past` — will not speak of their past | telling what happened to them before this place; their old name | the present; others' pasts | lifts | standing Devoted, or the PC already knows the secret (a knowledge record) |
| 6 | `innocent` — will not harm a child or an innocent | any act that harms someone the NPC regards as innocent | harm to proven wrongdoers or armed foes | absolute | — |
| 7 | `master` — will not cross their master or their people | acts against their master's or faction's recorded interest | acts the master would not mind | lifts | the master harmed or betrayed them (a memory or fact), or they were expelled |
| 8 | `place` — will not leave this place | travelling away from their home place overnight | errands within a day | lifts | the place is destroyed, overrun, or what binds them there is gone |
| 9 | `magic` — will not deal with magic | taking part in, receiving, or handling magic | witnessing it; talking about it | lifts | magic saved them or their kin (a `helped` memory whose frame used a magic deed tag) |
| 10 | `lend` — will not lend money | coin, goods or gear on credit or loan | selling, gifting, payment for work | lifts | standing Devoted |
| 11 | `oath` — will not lie under oath | false testimony, false sworn statements | silence; ordinary lies | absolute | — |
| 12 | `fight` — will not fight | taking up arms, striking anyone, standing in a battle line | fleeing; hiding; helping the wounded | lifts | their own life, or their kin's, is attacked in their presence |
| — | `pc_requests` — will not deal with the PC (closed door) | any request from the PC | parley, yield, the lift itself | lifts | the cost's named condition |
| — | `parley` / `yield` (archetype) | stopping a fight / surrendering | — | lifts | 09.7.6's field condition |
| — | `oath_bound` (oath) | the oath's prohibition | — | absolute | — |

**15.2.5 Fears.** `[D]` [DL-15-12; DL-15-34; C:P12; revision: I-065] A fear (`tbl.npc_fear`) is what the NPC's courage gives way to. It matters in three
places: (1) a **credible threat** that invokes a recorded fear is a Leverage term in intimidation (15.4.3)
even with no weapon drawn ("the watch would be very interested in what is in your cellar" to an NPC who
fears the law); (2) a want and a fear in conflict: the NPC takes the safer course (the narrator's reaction within
the ceiling, 12.11.5) [revision: R2-L]; (3) a fear is a Precision **snag** on any request that would put the NPC in its
way (asking a man who fears the dark to hold the lantern in the crypt), unless a term offsets it. Item 3
does not apply to a request whose Leverage term is that same fear: the threat is the term, and one fact is
one term or one lever, never also a snag (15.3.5) [revision: I-074]. Fears
are sealed until learned (insight, 15.6.1).

**15.2.6 Patience and walking away.** `[D]` Every NPC has **patience** for the PC in a scene: its maximum
is the standing's (T-15-1: Hostile 0, Unfriendly 1, Wary 2, Neutral 3, Warm 3, Friendly 4, Devoted
unlimited). It falls by 1 for each of: a Talk beat that ends in failure (2 on a critical failure, T-15-5 and
`social.yaml#patience` [verification: V2b-022]; a near miss taken as failure counts; a near miss taken as success-at-cost does not); a request blocked by a refusal or
by the ceiling (G4); an `insulted` memory. **At 0 the NPC ends the exchange**: they turn away, call the
next customer, shut the shutter, leave the room — `closed.<npc>.talk = until scene_end` (the S1 form of
`cost.closed_door`, with no standing loss). A Hostile NPC starts at 0: the only Talk beats that do not end
the exchange at once are a parley, a Yield, or a request carrying at least one term (15.3.4) — the things a
foe will actually listen to. Patience resets at `scene_end` (`h.15.patience_reset`, phase 9). Observing
an NPC (insight, 15.6.1) does not spend patience; an insight that the NPC *notices* (cost.exposure) does
(as an insult, if the NPC's alertness rises to alert).
*Why:* the documented disengagement deficit — simulated people who never leave — is cured only by a
counter that makes leaving the NPC's default once reasons run out [R4 W4; R: https://arxiv.org/abs/2606.20708].
Patience also stops the fishing loop ("I ask again, differently") that let-it-ride (01.4.2) only blocks
for the *same* request [DL-15-07].

**15.2.7 Minds and tongues.** `[D]` [DL-09-18; DL-02-12; C:VII; R5 SO-04; revision: I-065] Who can be talked to at all is read from state, never judged:
- **Mind** (09.2.7): `mindless` — Talk is G4 (no one to talk to); `animal` — Talk is G4 except calming and
  intimidating by manner (Handle with Presence; requests at most R1: go, stay, calm); `cunning` — Talk is
  legal, standing starts Hostile in a fight, requests above R2 need a term; `sapient` — all of this
  chapter; `alien` — Talk's reach is capped **Limited** unless the PC holds a license or fact that bridges
  it (a spirit-speaker's license; the spirit's true name, known).
- **Tongue**: speaker and listener must share a language license (`speaks`); otherwise Talk takes its
  crude fallback (gesture, tone and shared nouns: DC +5, reach Limited; 01.18.7) and requests above R2
  cannot be conveyed (G4 for the intent; the redirect names an interpreter, or learning the tongue,
  15.11). A language held at the `broken` grade is a Precision snag on deception and on any request above
  R1 (nuance fails); `accented` is a snag on deception only (the accent itself is a tell).
- **Hearing**: a listener who cannot hear (distance, noise, `cond.deafened`) cannot be talked to; writing
  works if both read.

### 15.3 The social frame: what is asked, of whom, for what

Every social beat is an ordinary frame (01.6) whose fields this part fills from the NPC's record. The
three questions it answers in order are: **which method** (15.3.1), **how big is the ask** (15.3.2), and
**what does the player bring** (15.3.5–15.3.6). The DC and the ceiling then follow by table.

**15.3.1 Social methods.** `[J:enum]` [DL-15-08; R5 SO-01; revision: I-065] Every Talk beat aimed at a person is classified into one method of
T-15-4 (canonical `data/social.yaml#methods`) from the **method as described** — what the character says
and does — never from the intent (00.4.1). The method fixes the attribute, the defense, the defender's
competence tag, the primary deed tag (00.5.6; the DM classifies to level 3 where the method is clear),
whether standing enters the DC, which ceiling applies, and what reach means.

**T-15-4 Social methods.**

| Method | True only when the character… | Attribute (alternates) | Against | Defender competence (highest of) | Primary deed tag | Standing in DC | Ceiling | Reach means |
|---|---|---|---|---|---|---|---|---|
| **request** (persuade) | asks openly for something, with honest reasons, appeals or offers | Presence (Intellect for a reasoned case) | Resolve | any `deed.influence.*` | `influence.persuasion.appeal` / `.argument` (reasoned) / `.rapport` (personal) | yes | standing (15.3.4) | T-15-5 row *request* |
| **win over** | seeks only to be liked or trusted more, asking nothing else | Presence | Resolve | any `deed.influence.*` | `influence.persuasion.rapport` | yes | — (fixed R2; 15.4.2) | one standing step, max Warm |
| **deceive** | makes them believe something the character knows or suspects is false, to get a request granted or a belief held | Presence (Intellect for a constructed account: forged figures explained, a false trail reasoned out) | Wits | `influence.insight`, `guile.deception` | `guile.deception.lying` / `.con` (a staged scheme) | yes | standing on the **perceived** size (15.5.1) | T-15-5 row *request*, plus a belief written |
| **intimidate** | compels by threat or menace | Presence (Might for physical menace) | Resolve | `influence.intimidation`, `martial` | `influence.intimidation.threat` / `.display` | **no** | the threat ceiling (15.4.3) | T-15-5 row *request*; `threatened` memory |
| **interrogate** | questions an unwilling subject over time | as request or intimidate | Resolve | as that method | `influence.intimidation.interrogation` | per the method | 15.8.4 | clock ticks |
| **provoke** | taunts or goads them into a rash act | Presence | Resolve | `influence.*`, `martial.tactics` | `influence.intimidation.display` | **no** | the act's size (15.4.4) | the act happens |
| **perform** | moves an audience by music, story, oratory or spectacle | Presence | the audience tier (15.4.5) | — | `influence.performance.*` | no (audience mood is the tier) | — | audience effect (T-15-5) |
| **bargain** | sets terms of a deal or a price | Presence (Intellect for appraisal-based argument) | Wits or Presence, higher (08.8.7) | `influence.trade` | `influence.trade.haggling` / `.venture` (a deal) | yes | 15.7 | notches or terms |
| **command** | gives an order to someone a fact says must obey them (a hireling, a soldier of the PC's rank) | Presence | Resolve | `influence.command` | `influence.command.directing` | yes | duty: orders within the subordinate's duty are R1; outside it, request rules | the order is carried out |
| **read** (insight) | watches and listens to learn what they feel, want, fear, or whether they lie — **an Observe beat, not Talk** | Wits | their concealment (15.6.1) | `guile.deception` | `influence.insight.*` | no | — | P17 items |

*Distinguishing tests* (SG-16): request vs deceive — *does the character know or suspect the reason
they give is false?* Yes → deceive. Request vs intimidate — *is the push a harm to them if they refuse?*
Yes → intimidate. Request vs bargain — *is the core of it an exchange of value at a price?* Yes → bargain.
Win over vs request — *is anything asked beyond goodwill?* Yes → request. Deceive vs Sneak (01.18.13) —
*must they believe something, or merely not notice?* Believe → deceive. Talk vs Setup by words — *is the
character after the listener's decision (Talk) or a moment of distraction to exploit (Setup)?* Default
when uncertain: **request** (the method with the fewest special effects). *Worst case (J):* the wrong method
uses the wrong defense (at most the gap between the NPC's Resolve and Wits, typically 0–3) and is shown in
the OFFER, where the player may restate (class ii) [01.18.7; 00.4.1; R4 §3.2 S1; DL-15-08].

**15.3.2 Request size.** `[J:rung]`

```
### 15.3.2  Request size                                             [J:rung] [D]
Trigger [T]:        FRAME of any request, deceive, intimidate, provoke, bargain or command beat
Loads in:           situation.social.*
License check:      basic verb: verb.talk
Decisions (J):      1. SIZE [J:rung] (the Framer's pick, R1-R5 [revision: R2-G; I-160d])
                       What would granting this cost or risk THIS person, as their record
                       and the scene's facts show? (T-15-7; canonical data/social.yaml#request_sizes)
                       R1 TRIFLE -- costs them nothing and risks nothing. Typical: directions; when the
                         watch changes. Boundary: let you sit by their fire for an hour.
                       R2 FAVOR -- costs a little time, effort or at most one Unit of their weekly
                         lifestyle; bends a rule no one checks; shares something private but harmless.
                         Typical: an introduction to a cousin; look away while you cross the yard by
                         day. Boundary: lend a mule for a day.
                       R3 REAL COST -- costs several Units or days, or breaks a rule they could be
                         reprimanded for, or a confidence that betrays no one. Typical: let you into the
                         archive after hours; lend a horse for a week. Boundary: carry a sealed letter
                         through a checkpoint for you.
                       R4 SERIOUS RISK -- risks their livelihood, position, safety or an important
                         relationship. Typical: smuggle you past the gate; testify against a powerful
                         man. Boundary: hide you from the watch for one night.
                       R5 GRAVE -- risks their life, freedom or family, or their deepest loyalty or
                         identity. Typical: betray their lord; kill for you. Boundary: hide you for a
                         week while the town is searched house by house.
                       Judge only facts in state: what the act costs, which rules it breaks (and whether
                       anyone checks), who would punish it, what it puts at risk. Information requests
                       are sized by what telling costs the teller: anything anyone in their role would
                       say R1; private and harmless R2; a confidence that betrays no one R3; a secret
                       that exposes someone R4; one that endangers the teller's life or freedom R5. A
                       request that implicates the teller in a crime (confess) is R5.
                       A request whose granting DEFEATS one of the NPC's recorded wants (15.2.2) counts
                       ONE RUNG HIGHER (never above R5) and is never certain (15.3.10) [revision: I-074]:
                       [J:flag] "Would granting this make a recorded want unreachable, or spend what the
                       want is for?" True only with a want id; uncertain with a want id -> true (the
                       grant-side direction). (A Friendly principal who wants her mill kept is asked to
                       sell it: R3 by cost, R4 by the want, and a roll.)
                       Between two rungs: the HIGHER. Never adjust for how well the request is phrased.
Computation [D]:    request mod R1 +0 / R2 +2 / R3 +5 / R4 +8 / R5 +10; payment price U(S1..S5) Units
                    of the NPC's lifestyle (1 / 1 / 2 / 3 / 4); effective size after terms (15.3.4)
Stakes:             R1 Safe (failure: they don't; patience -1); R2+ Risky by default (their goodwill is
                    spent); Dire per 01.6.9's HEAVY test (an armed listener of band >= the PC's whose
                    refusal turns violent; the lasting enmity of a powerful NPC or faction)
State writes:       frame.request {size, effective, terms}
Narration may not imply: that the person sees the request as smaller than the rung
Worst case (J):     one rung = 2-3 on the DC (class i) or, at the ceiling's edge, a roll that should have
                    been a G4 refusal or vice versa: the OFFER shows the rung and the ceiling before
                    commitment, and the player may shrink the request or add a term (class ii).
Examples:           see T-15-7 (two per rung). inside R3: ask the archive clerk to let you in after
                      dark (a rule she could be reprimanded for breaking) -> R3. outside: the
                      same clerk, if the archive holds the duke's secret ledgers and a guard checks the
                      door -> R4 (her position and safety).
                    non-example: "It's a tiny favor really, just this once" -> phrasing; the rung
                      follows what it costs her.
Anchor:             no
Basis:              [R: https://2e.aonprd.com/Rules.aspx?ID=1201 (PF2e influence thresholds)]
                    [R7 §4.2] [00.3.11 U(severity)] [DL-15-09]
```

**15.3.3 The social DC.** `[D]` For every social method whose "against" is a defense (T-15-4), the DC is
composed on 00.3.8's opposed defense — the Talk card's `against` (01.18.7) — plus two terms read from
state:

`DC = 10 + defender attribute + competence + edge + status + standing mod + request mod + mode price`

- **attribute / competence / edge / status**: the defender's, per 00.3.8 and 01.6.4 source 2, for the
  defense attribute and competence tags of T-15-4 (highest competence among the listed tags; an NPC with
  none uses 0). Computed fresh every time, never stored (01.6.4).
- **standing mod** (T-15-1): the NPC's standing toward the actor, for methods marked "yes"; 0 otherwise.
- **request mod** (15.3.2): from the **effective** size (15.3.4), R1 +0 … R5 +10.
- **mode price**: the crude-fallback +5 for a language not shared (15.2.7); a stretch or emulate price
  where a license is being stretched (01.6.4).
- **Several listeners**: the defense of the one who decides; where several must all agree (a council of
  three, a gate with two guards who check each other), the **highest** defense (01.6.4).
These two additions are not situational factors (which stay levers and snags, 00.3.8): standing and
request size are stored properties of *this* person and *this* ask, as stable as a lock's make, so they
belong in the DC, where a seduced judgment cannot reach them [01.18.7; R7 §4.2 "social DC"; DL-15-10].
T-15-3 lists the DCs and odds for a typical commoner at every standing × size.

**T-15-3 Social DCs for a defense of 10** (a T1 commoner: Resolve or Wits 0, no social competence).
Success-or-better % at modifiers **+1 / +5 / +9** (untrained / a P1 talker / a P3 talker). `*` = above the
ceiling without terms (G4 unless terms bring it down). Exhaustive d20, 01.8.1 (`scratchpad/social15.py`).

| Standing | R1 | R2 | R3 | R4 | R5 |
|---|---|---|---|---|---|
| Hostile | 15 (35/55/75)\* | 17\* | 20\* | 23\* | 25\* |
| Unfriendly | 13 (45/65/85) | 15 (35/55/75)\* | 18\* | 21\* | 23\* |
| Wary | 11 (55/75/95) | 13 (45/65/85)\* | 16\* | 19\* | 21\* |
| Neutral | certain | 12 (50/70/90) | 15 (35/55/75)\* | 18\* | 20\* |
| Warm | certain | 11 (55/75/95) | 14 (40/60/80) | 17\* | 19\* |
| Friendly | certain | certain | 12 (50/70/90) | 15 (35/55/75) | 17\* |
| Devoted | certain | certain | certain | 13 (45/65/85) | 15 (35/55/75) |

Reading it: a request **at the ceiling** is DC 11–15 for an ordinary person at every rung from Wary up —
a fair contest for a talker, a long shot for the untrained. A T2 guard (defense 11) adds 1; a T3 courtier
with Resolve +3 and influence competence +3 (defense 16) adds 6: courtiers are hard to move by talk and
easy to move by terms.

**15.3.4 The ceiling.** `[D]` The **effective size** of a request is its size (15.3.2) minus one rung per
term (15.3.5), at most two terms, never below R1 (whether it needs a roll at all counts one term only: the
certainty size, 15.3.10 [revision: I-048]). If the effective size exceeds the NPC's **ceiling**
(T-15-1; Hostile: R1, and only when the request carries at least one term), the request is **G4 for this
intent** (01.3.7 test 1: granting it would contradict the person as recorded): no roll, patience −1, and
the redirect names, in the NPC's voice, the honest ways forward — a smaller request; what they would want
in exchange (a term: if a want is known to the PC, it is named; if not, "what's in it for me?" is said and
the PC may read them, 15.6.1); someone better placed; or, when the effective size is exactly **one** rung
above the ceiling and the NPC is at least Wary and the request carries at least one term, a **persuasion
campaign** over several scenes (15.8.1). The ceiling is what makes NPCs consistent: no roll, however
lucky, gets a Neutral stranger to hide the PC from the watch; a cousin's letter, a debt called in, or a
week of favors can [R4 W4; DL-15-11].

**15.3.5 Terms: what the player brings.** `[J:flag]` ×4 + `[D]`

```
### 15.3.5  Terms                                                     [J:flag] [D]
Trigger [T]:        FRAME of a request, deceive, intimidate, bargain or command beat; PR-15-1 has
                    extracted every offer the player made and every fact the player's words invoke
Loads in:           situation.social.*
License check:      as the beat
Decisions (J):      Each candidate is tested against exactly one term type; a fact or offer counts as at
                    most ONE term or ONE lever (never both), and a fear used as a Leverage term is not
                    also that request's fear snag (15.2.5 item 3); at most two terms per request.
                    1. WANT [J:flag] "Does granting the request, or the PC's offer delivered with it,
                       serve one of the NPC's recorded wants (15.2.2), or protect one of the universal
                       interests every sapient person holds -- their life, their kin, their livelihood,
                       their property -- from a threat that is an established fact?" True only with a
                       want id, or with the fact ids of BOTH the interest (their mill; their son) and the
                       threat to it (the bridge is failing). False for a benefit the want does not name,
                       and for a threat that is only the player's assertion (that is a claim: 15.5).
                       The PC need not know the want: the engine checks the sealed record, and a
                       matched want becomes known_to_pc.
                    2. PAYMENT [J:flag] "Is value handed over (or placed in their hand to keep on
                       granting) worth at least the request's price -- U(severity of the requested rung)
                       Units of the NPC's weekly lifestyle (15.3.2)?" In a HIRE (16.3.3) the wage paid
                       in advance and hazard pay are terms without this price test: the wage is the
                       market price of the work (08.8.8) [integration: IR ch.16 to 15 (c)]. True only when coin, goods or a
                       service of that value changes hands at the beat and the engine verifies the
                       amount. False when the NPC holds refusal kind `bribe` and the request breaches a
                       duty or rule (15.2.3), or for a payment only promised (that is an Obligation).
                    3. LEVERAGE [J:flag] "Does a fact give the PC power over this person on this
                       matter?" True only for: a debt they owe the PC (memory `owes`, cleared by using
                       it); a secret of theirs the PC holds (a knowledge record of a fact in their
                       `secrets`); a credible threat to their life, kin, property or a recorded fear,
                       which the PC is able to carry out (a fact: armed and present; the watch-captain is
                       the PC's friend; the PC holds the letter). False for a threat the PC cannot carry
                       out, which is a claim (15.5.2: a bluff). Using leverage other than a debt writes
                       the memory `threatened` (-1 at scene_end) and the fact npc.<id>.coerced_by.
                    4. OBLIGATION [J:flag] "Does the PC bind themselves to a stated future act in
                       return, written as a commitment (kind debt or promise) with content and due
                       condition BEFORE the roll?" True only when the commitment is written and the NPC
                       stands at Wary or better (Hostile and Unfriendly people do not take the PC's word),
                       or the obligation is secured by a pledge held now (then it is also legal there).
                       Kept -> `promised` kept (+1); broken -> `betrayed` (-3) (T-15-2).
                    Tie-break for every flag: false (SG-05's grant-side direction).
Computation [D]:    effective size = size - number of terms (min R1); the DC's request mod and the
                    ceiling check use the effective size; payment coin moved at OFFER commitment
                    (refunded on failure only if the NPC is Warm or better: others keep it -- the
                    threatened cost names this)
Stakes:             as the beat
State writes:       frame.terms [{type, fact_id|want_id|commitment_id}]; coin; commitment; memories;
                    want.known_to_pc
Narration may not imply: a term the frame does not list; that the NPC agreed before the roll
Worst case (J):     one term wrongly allowed = one request rung: 2-3 DC, or one rung of ceiling (class
                    i), auditable because every term cites an id (INV-20). The ceiling's G4 still
                    holds two rungs above.
Examples:           inside WANT: the reeve wants "to repay a debt" (sealed); Wren offers to pay his debt to
                      the salt factor -> want term (and he learns she knows). outside: Wren offers him
                      coin for his trouble -> Payment, not Want.
                    inside WANT (interest): the miller's grain must cross the failing bridge (both facts)
                      and Wren asks him to lend his ox-team to shore it up -> interest term.
                    inside LEVERAGE: Wren holds the steward's letter to the smugglers (knowledge record)
                      -> leverage; he complies; at scene end he is one rung colder and coerced_by Wren.
                    outside: "I know people in the city who could ruin you" (no such fact) -> a bluff:
                      deceive, claim plausibility (15.5.2).
                    non-example: "I'll be grateful, and gratitude matters to a man like you" -> not a
                      written obligation, not a want; nothing.
Anchor:             no
Basis:              [R: https://2e.aonprd.com/Rules.aspx?ID=1201 (discover and cater to interests)]
                    [R5 SO-07 favors and debts] [R4 SG-06] [DL-15-12]
```

**15.3.6 Social levers and snags.** `[J:flag]` + `[J:enum]` [DL-00A-10; C:III; revision: I-065] Levers and snags in social play are 00.3.9's,
unchanged: each cites a fact established before the declaration; at most two of each; Precision ±2,
Protective ±1 stakes rung, Amplifying ±1 reach rung; the obligation to apply a fitting snag (01.6.8). This
catalog (T-15-8, `data/social.yaml#levers`) lists the social facts that typically qualify, so the DM's
`[J:flag]` "name the fact" has anchors:

**T-15-8 Social levers and snags (typical qualifying facts).**

| Type | Lever (fact that helps) | Snag (fact that hinders) |
|---|---|---|
| Precision | **evidence in hand** proving what the request rests on (a document, an object, a witness present); **a voucher**: someone the NPC holds at Warm or better, present, or by a token or letter the NPC recognizes; **the right standing for the venue** (08.8.6 *wealthy* with merchants and officials, *noble* at court; a rank fact, 11); **the listener's state** that makes the method easier (drunk, rushed, grieving — for deception and haggling; a fact); **a Setup** that created a fact (drinks bought and drunk; his pride engaged before his guild) | **shabby** lifestyle where appearance matters (08.8.6); visibly bloodied or armed for violence in a peaceful place; a **fear** of the NPC that the request walks into (15.2.5); a **scar or maim** recorded as recognizable (07) on deception or disguise; a language held at broken (all requests above R1) or accented (deception) (15.2.7); the NPC **rushed or busy** (for request and win-over); the NPC's **superior present and opposed** |
| Protective | **a way out** if it goes badly: a prepared cover story (an earlier beat's fact), a friend placed to vouch afterward, an exit, a crowd to vanish into | **no way out**: the PC is in their hall, surrounded by their people |
| Amplifying | **an audience on the PC's side** (a crowd whose recorded mood favors the PC); **the NPC's superior present and favoring** the request; **a precedent**: they did this for someone else (a fact) | **an audience against the PC**; **the request is public** where granting it would shame them |

Memories act through standing (15.1.6), never again as snags, with one exception: a `caught_lying`
memory worsens claim plausibility (15.5.2). A reputation (11) acts as a lever or snag only where the NPC
knows it (12.10.6) and the reputation's content bears on the request [00.3.9; 01.6.8]. *Worst case (J):* one
wrongly allowed lever or snag: ±2 on the roll, one stakes rung or one reach rung, and the cited fact id makes
it auditable (00.3.9; class i). [integration: 00.2.3 audit]

**15.3.7 What is never a lever, a term, or a reason.** `[D]` The closed list of things that change **no**
number, no rung, no ceiling, no plausibility, and no refusal, however they are phrased — because the
research shows they are exactly what moves an AI adjudicator and exactly what should not [R4 W2; R:
https://arxiv.org/abs/2607.02802; SG-06]:
1. **Eloquence**: length, vividness, rhetoric, poetry, the quality of the prose.
2. **Flattery by itself**: praise that creates no fact. (A Setup beat that *engages* the listener's pride
   and succeeds creates a citable fact for one later beat: that is the honest channel for charm.)
3. **Assertion**: anything the player states as true that is not in state (SG-06, INV-9). If the
   character says it to the NPC, it is a **claim** (15.5); if the player is asking whether it is so, it is
   an Oracle question (00.12.7), answered before framing and citable from the next beat.
4. **Appeals to the NPC's reason, duty, kindness or better nature** that cite no fact: no want, no
   interest under threat, no relationship.
5. **The player's model of the NPC's mind** ("a man like him would surely…"). Only the NPC's *record*
   counts; when the player's guess matches a recorded want, the want counts and the guess does not.
6. **Promises of goodwill** not written as an Obligation term.
7. **Repetition**: asking again, louder, differently phrased (01.4.2; 15.2.6).
8. **Out-of-fiction argument** about what would be fair, fun or realistic (the player may raise a rules
   question, which is answered as a rules question, 12.15).
9. **Reputation the NPC has not heard** (12.10.6).
10. **The DM's own impression** that "that was a good speech". The DM may enjoy it; the frame does not see it.
The honest channels for a gifted talker are all in the frame: the attribute and competence of the
character (a silver tongue is `deed.influence` competence, earned through 03–04), choosing the right
method, finding a real want (15.6.1), bringing terms, and creating facts with Setup. *Narration may not
imply* that a well-made speech is why it worked; the narration credits the cited facts.

**15.3.8 Stakes and threatened costs in social play.** `[D]` [DL-15-32; DL-00A-11; R5 SO-01; revision: I-065] Stakes follow 01.6.9 and 15.3.2: R1 Safe;
R2+ Risky (goodwill is a cost source); Dire when the HEAVY test holds. The **threatened cost** (01.6.11) is
chosen by 01.13.1 from these fits: **`cost.closed_door`** (the default for request, win-over, bargain and
command: "I've heard enough"; S3 and up cost standing, S4 writes a refusal, 01.13.9); **`cost.exposure`**
(the default for deceive, and for any request made where being noticed matters: S2 makes the listener
alert, S4 identifies the PC); **`cost.harm`** (intimidate or provoke against an armed listener: they
answer with a blow); **`cost.twist`** (a third party walks in). The alternate (Risky and Dire) is the other
fitting entry. A critical failure steps the severity one rung (01.9.2). A Dire frame whose threatened cost
is `cost.closed_door` against a principal or a faction is **ruinous** (03.4.5): its critical failure (S4–S5)
writes a refusal for good or costs faction status, which nothing undoes on the day; the evidence it yields
counts like a lethal fight's (+2, a crisis) [revision: I-003].

**15.3.9 Reach and delivery in social play.** `[D]` [DL-15-13; C:P8; revision: I-065] Reach is framed per 01.6.10: Standard by default;
Limited when one effect factor stands against the method (an `alien` mind, 15.2.7; a crowd's scale; a
language fallback); Great only through an Amplifying lever or the OFFER trade. What delivered reach
**means** is T-15-5 (canonical `data/social.yaml#delivery`), which specializes the Talk card's reach
ladder (01.18.7):

**T-15-5 Social delivery.**

| Delivered reach | request / deceive / intimidate / bargain | perform (audience) | win over |
|---|---|---|---|
| 0 failure | **No.** The threatened cost lands; patience −1 | the audience is unmoved; the threatened cost | no step; the threatened cost |
| 0 critical failure | No; the cost one rung heavier; patience −2 | they turn on the performer (heckled, pelted, thrown out) | no step; cost +1 rung (at S3: −1 standing) |
| 1 Limited | **A lesser yes**: the NPC grants a version one rung smaller (min R1), which the DM picks `[J:enum]` from the NPC's record ("I won't take you in, but I'll tell you where the old shrine is") | the audience is pleased: coin per T-15-11 | +1 step (max Warm) |
| 2 Standard | **Yes, as asked.** | the audience is won: coin; the crowd's mood fact turns favorable for the scene (an Amplifying lever for a later beat) | +1 step (max Warm) |
| 3 Great | **Yes, and more**: one extra the NPC chooses from their record — a want, fear or refusal revealed (known_to_pc), information one rung smaller than the request volunteered, or a small help | as 2, and a patron or a contact (a new recurring NPC at Warm) | +1 step, and one want revealed |
| 4 Exceptional | as 3, plus a follow-up Precision lever (a fact: "tell the gatekeeper I sent you") | as 3, plus a reputation entry in this settlement (11) | as 3 |

A near miss may be taken as **success at a cost** (01.9.3): the framed reach is delivered and the
threatened or alternate cost is paid. A "yes" binds the NPC to the act asked and nothing more: the act is
written as a fact or a commitment of the NPC's (`npc.<id>.agreed: <act>`, with its due time), and the
NPC's later conduct follows it unless a new fact releases them (12.11.4) [01.9; 01.18.7; DL-15-13].

**Questions** [revision: R2-D] [DL-15-39; I-140]: a Talk, a certain beat or a plain SPEECH question that asks an NPC for
information is a bundled beat (01.10). One clue judgment runs first over all its questions together (PR-12-10 step 1),
and a clue it finds is delivered outside the count [revision: R2-L; DL-15-45]. Of the N questions, `deliver_count(N, reach)` (T-01-6) land in the player's rank,
and each landed one is answered by PR-12-10 (`social.yaml#delivery.information`): a consequential one by the case
graph, any other in the NPC's own words at or below the ceiling code set (12.10.8) [revision: R2-L]; Great adds one volunteered extra
[revision: R2-H; DL-12-90]. One question is N = 1, so any success lands it; a certain beat or SPEECH runs at Standard. "Yes, as asked" above
is the act asked; it never makes the NPC know more than their speaker card holds (PR-12-10 step 3).

**15.3.10 When talk needs no roll.** `[D]` + `[J:flag]` [DL-15-33; DL-15-34; revision: I-065] A social beat (any beat whose typed goal is `persuade_to`, whatever its verb
label: Talk, Help or another; 01.3.1, gates key on the goal and its method) [revision: R2-K; DL-15-41] is **certain**
(01.4.1, no roll) when
the request's **certainty size** is R1 and the NPC is Neutral or warmer, or the certainty size is at least
**two rungs below** the ceiling (Warm: R1; Friendly: R1–R2; Devoted: R1–R3) — and no refusal covers it, the ask's ceiling (T-12-19, by the NPC's mood and its cost to them) reads
*will help*, else the beat is framed as usual [revision: R2-L; DL-12-128; provisional, owner decision R2-L-1],
and nothing in the scene would make granting it costly to them (`[J:flag]` *"Is there an established
reason this NPC would hesitate now — a watcher, a superior, a fear, or a recorded want the request
defeats (15.3.2)?"* True only with a cited fact or want id; true → roll) [revision: I-074]. The
**certainty size** is the size (15.3.2) minus **at most one** term [revision: I-048]: terms still lower the
effective size for the DC and the ceiling (15.3.4), but a second term never removes the roll, so terms make
a favor certain and never a real cost or worse (Neutral: R2 with one term is certain; R3 with two terms
rolls at R1's +0). An **Obligation** term (a promise) counts toward certainty only while the PC owes this
NPC no undelivered commitment from an earlier request (11.4.9; 00.6.1): a promise is kept before the next
one buys another free yes. A certain beat's necessity reason is `trivial`, so it yields **no evidence**
(03.2.6), and its RESULT line says so (12.15.3) [revision: I-054]. Basis: `15-certainty-sim.py` (seed 48):
under an assumed request mix, certain beats fall from 37.7% to 32.0% of requests for an honest player and
from 53.6% to 38.8% for one who always brings two terms; certain R3+ requests fall from 39.6% to 8.2%
(optimizer); a request that defeats a want is never certain (from 53.8%). Plain speech that asks for no decision (telling, greeting, asking a plain question: one whose words request no act or object and carry no pressure,
whatever the listener's inclination, 12.2.2 [revision: R2-G; I-172]) is the free activity "speak a few words" (00.12.6) and is never framed. A plain question is SPEECH (12.2.2) and
never reaches this test, so the hesitation flag applies to requests only [revision: R2-G; I-160c; I-172]. *Worst case (J):* a request
treated as certain that should have rolled — the cheap end of the leniency failure, bounded at two rungs
below the ceiling (class i); a cited hesitation reason always restores the roll.

**15.3.11 Social contests and their band.** `[D]` `[revision: I-003]` A Talk frame of one of 03.4.3's closed
contest methods (request, bargain, deceive, intimidate, interrogate, or any beat of a campaign or a debate;
not win over, provoke, perform, command or read) [revision: I-071] is a **social contest** (03.4.3) when it is aimed at a **principal** NPC (12.11.1) or at anyone who
speaks for a faction on the faction's business. Its **contest band** is engine-read (03.4.3): the opposing
party's own band (its threat band where it has an adversary line, 09, else its record's `band`, 12.11.1;
a principal with neither counts band 1), raised to the tier of the faction it acts for (11.3; tier 0–1 → 1
… 5 → 5) only when the party **can bind the faction**: its head or an officer (11.3.17); a door-warden, clerk
or member who speaks for the faction without that authority counts its own band; and never above the
speaker's `power_band` + 2 [revision: I-039]. Every beat of the contest takes
`challenge_band = max(DC band, contest band)` (03.4.3), so a bargain struck with the master of a tier-4
guild is a band-4 deed for a PC of power band 2 or more even when the exchange that sealed it was moderate,
while a band-1 talker at the same guild's gate does a band-1 deed. The opposition that higher tiers need is
in the world: every region holds band-4 and band-5 **powers** in its far rings (12.16.11), and a great deed
counts at most twice toward one tier from one opposing party (04.3.4) [revision: I-083]. A beat declared while the
contest's opposing clock stands one segment from full (a campaign's patience, 15.8.1; a council's, 15.8.3)
is **one from full** and a crisis (03.4.5) [revision: I-046]. *Why:* a fight's deeds are rated by the fight (03.4.3's advisory
offset), and a negotiator's must be rated by what they faced, or the higher tiers' great deeds and crises
are open only to fighters (`04-recog-parity.py`: with this rule an envoy reaches tier 3 at session 18 and
tier 5 at 46, beside the archer's 19 and 51; on 04's current ladder 14 and 42 beside 15 and 47, 04.3.5
[revision: I-089]) [03.4.3; 03.4.5; DL-15-32].

### 15.4 Asking, winning over, threatening, provoking, performing

**15.4.1 Request (persuade).** `[J:enum]` + `[D]`

```
### 15.4.1  Request: ask them to do it                             [J:enum] [J:rung] [J:flag] [D]
Trigger [T]:        the PC asks an NPC for an act, a thing, or information, openly and honestly
Loads in:           situation.social.*
License check:      basic verb: verb.talk (G1); a shared tongue or the crude fallback (15.2.7); the mind
                    allows Talk (09.2.7)
Decisions (J):      1. METHOD [J:enum] = request (T-15-4; vs deceive/intimidate/bargain by its tests)
                    2. REFUSAL [J:flag] per refusal (15.2.3) -> G4 if covered and not lifted
                    3. SIZE [J:rung] (15.3.2)
                    4. TERMS [J:flag] x4 (15.3.5) and LEVERS/SNAGS [J:flag] (15.3.6)
                    5. CERTAIN [J:flag] (15.3.10)
Computation [D]:    PR-15-1: effective size; ceiling check (15.3.4) -> G4 or frame; DC (15.3.3); stakes
                    and threatened cost (15.3.8); OFFER shows the DC source as "her resolve, Warm,
                    asking a real cost (R3) less one term"; delivery per T-15-5
Stakes:             R1 Safe; R2+ Risky; Dire per 01.6.9
State writes:       frame; npc.<id>.agreed (on a yes); patience; memories (12.11.7); standing (costs,
                    T-15-2); terms' writes (coin, commitments, known_to_pc)
Narration may not imply: a yes beyond the delivered reach; a no that is softer than the cost written
Worst case (J):     the decisions' own worst cases (method: class ii; size: class i/ii; term: class i);
                    together bounded by the ceiling's G4 two rungs out
Examples:           WE-15-1 (four outcomes at one gate); WE-15-4 (a want found, then used)
                    non-example: "I give a rousing speech about duty until he lets me pass" -> method
                      request, size by what passing costs him, no lever from the speech (15.3.7)
Anchor:             yes. Intent verbs: ask, persuade, convince, plead, petition, request, beg, talk into.
                    Knobs: dc (defense; default Resolve; allowed delta: Wits for a request that turns on
                    noticing something), attribute (Presence -> Intellect for a reasoned case), targets
                    (one listener -> a group: highest defense; a crowd: 15.4.7), reach_unit (an act ->
                    information items under P17), time_cost (a few words -> a scene: 15.8.1 campaign).
Basis:              [01.18.7] [R7 §4.2] [R4 W4] [DL-15-08]
```

**15.4.2 Win over.** `[D]` + `[J:flag]`

```
### 15.4.2  Win over: earn a little trust                         [J:flag] [D]
Trigger [T]:        the PC talks with an NPC to be liked or trusted, asking nothing else in the beat
Loads in:           situation.social.*
License check:      basic verb: verb.talk
Decisions (J):      1. ASKS NOTHING [J:flag] "Is the beat's only intent the NPC's regard?" True only when
                       no act, thing or information is sought in it. False -> it is a request (15.4.1).
                       Uncertain -> false.
Computation [D]:    request size fixed R2 (they give their regard); method win over (T-15-4); the beat
                    is legal only while standing < Warm and npc.<id>.small_steps_week = 0 (15.1.7);
                    otherwise no roll and the narration says the conversation is pleasant and changes
                    nothing (no step is possible this week). Delivery per T-15-5 (+1 step max Warm; at 3+
                    one want revealed). Time: one interval in free mode (a real conversation).
Stakes:             Risky (goodwill: closed_door S2 means "not today")
State writes:       relationship (+1), small_steps_week, want.known_to_pc (reach 3+), memory
Narration may not imply: that they are now a friend; that the PC's charm is why (the step is the roll's)
Worst case (J):     a disguised request treated as win-over: the request gets no grant from it (win-over
                    delivers only a step), so the error costs nothing beyond one step (class i)
Examples:           inside: Wren shares bread and talk with the wary ferryman, asking nothing -> DC 10 +
                      0 + 1 (Wary) + 2 (R2) = 13; success -> Neutral.
                    outside: the same talk ending "...so, will you row me over tonight?" -> request.
                    boundary: the ferryman is already Warm -> no win-over is possible; deeds and gifts
                      (15.1.7) are the way further.
                    non-example: chatting him up again an hour later after a failure -> rides on the
                      failure (01.4.2) and spends patience
Anchor:             yes. Intent verbs: befriend, chat up, get on his good side, earn their trust,
                    charm. Knobs: attribute (Presence -> Intellect for shared learning, Might for
                    shared labor), time_cost (interval -> a day of company, which is 15.13.6's
                    Cultivate when it serves a want).
Basis:              [01.18.7 reach 1 "one standing step"] [R5 P-27] [DL-15-04]
```

**15.4.3 Intimidate.** `[J:flag]` + `[D]`

```
### 15.4.3  Intimidate: compel by threat                           [J:flag] [J:rung] [D]
Trigger [T]:        the PC threatens or menaces an NPC to make them do something
Loads in:           situation.social.*, situation.social.interrogation, situation.conflict.*
License check:      basic verb: verb.talk (G1); mind per 09.2.7 (animals: by manner only, R1)
Decisions (J):      1. CREDIBLE [J:flag] "Can the PC actually deliver the harm threatened, as facts show
                       (armed and present; the NPC is alone; the PC holds the letter; the PC's
                       reputation for violence is known to them)?" True only with a cited fact; then
                       the threat is a LEVERAGE term (15.3.5). False -> the threat is a bluff: the beat
                       is a deceive with the threat as its claim (15.5.2).
                    2. SIZE [J:rung] (15.3.2), REFUSALS (15.2.3), TERMS, LEVERS as usual
                    3. LIFE OR KIN [J:flag] (only for R5) "Is the credible threat against the NPC's own
                       life or their kin's?" False -> R5 is G4 for intimidation (no one betrays their
                       deepest loyalty for a lesser fear).
Computation [D]:    standing does NOT enter the DC (fear needs no regard); the THREAT CEILING is R2 for
                    any NPC regardless of standing (effective size after terms). DC = 10 + Resolve +
                    competence (intimidation or martial, highest) + edge + status + request mod.
                    On a yes: the act is done while the threat is present; memory `threatened` (-1 at
                    scene_end); fact npc.<id>.coerced_by = pc. For an R3+ coerced act, when the PC
                    leaves the NPC's reach the engine asks the Oracle "does <NPC> report or undo it?"
                    at Even (R3) / Likely (R4-R5), odds committed now, rolled at that moment (SG-12).
Stakes:             Risky; Dire when the NPC is armed, of band >= the PC's, and failure means a fight
                    (threatened cost cost.harm: they strike first)
State writes:       as 15.4.1; memory threatened; coerced_by; the queued Oracle question
Narration may not imply: that fear made them loyal; that the compliance outlasts the threat
Worst case (J):     CREDIBLE wrongly true: one term (one rung, class i); the -1 standing and the
                    retaliation question land anyway, so a mistaken grant still costs the PC
Examples:           inside: Wren, bow drawn at six paces, tells the lone poacher to drop the snares and
                      go -> credible (armed, alone), R2 -> eff R1 -> DC 10 + 0 + 0 + 0 = 10.
                    outside: the same words to the poacher's three armed brothers -> not credible
                      against three -> a bluff (deceive; plausibility doubtful).
                    boundary: threatening the toll-keeper with "the margrave's displeasure" while Wren
                      truly carries the margrave's writ (a fact) -> credible leverage.
                    non-example: "I glare at him with the cold eyes of a killer" -> description; the
                      credibility test reads facts (armed? alone? known for it?), not the glare
Anchor:             yes. Intent verbs: threaten, menace, cow, scare off, lean on, warn off. Knobs:
                    attribute (Presence -> Might for physical menace), dc (Resolve; allowed delta:
                    tier for a crowd's courage, 15.4.7), targets (one -> a group: highest defense; a
                    mob in conflict: 06's morale clock ticks instead).
Basis:              [01.18.7] [06.11 morale] [R4 W4] [DL-15-14]
```
In conflict, a demand that a foe surrender is this method resolved on 06's morale clock: delivered reach
ticks the foe side's morale clock (06.11.2) rather than granting the surrender outright, and the foe's
`yield_when` refusal (09.7.6) applies (06.11.7).

**15.4.4 Provoke.** `[J:flag]` + `[D]` [DL-15-14; R5 SO-01; revision: I-065] A taunt, a goad, a public slight meant to make an NPC do something
rash. *Tempting* `[J:flag]`: *"Does the act served by the provocation fit the NPC's recorded anger,
pride, wants or behavior list (attack the one who insults them, chase the thief, blurt the boast)?"* True
only with a cited record field; false → G4 for the intent (no one can be goaded into what they have no
urge to do; the redirect names what *would* bait them, if the PC has read them, 15.6.1). Size: the act's
cost to them (15.3.2); no ceiling by standing (anger ignores regard); standing does not enter the DC.
Delivery: Standard = they do it now (in conflict: their behavior row is overridden for their next turn,
06's provoke); Great = they do it recklessly (they give up their next reaction, or leave a lever
open). Always: memory `insulted` (−1) on the target, whatever the degree, and patience −1. *Worst case (J):*
TEMPTING wrongly true → one rash act the record did not support (class iv: the provoked act is logged
with the record field cited). *Anchor: yes* — intent verbs: taunt, goad, bait, provoke, needle; knobs:
dc, targets, reach_unit.

**15.4.5 Perform.** `[J:rung]` + `[D]`

```
### 15.4.5  Perform: move an audience                              [J:rung] [D]
Trigger [T]:        the PC plays, sings, tells, preaches or makes a spectacle for an audience
Loads in:           situation.social.performance, situation.downtime.carousing
License check:      basic verb: verb.talk (perform); an instrument needs the instrument (a tool lever,
                    not a license); a performance in a tongue the audience lacks: crude fallback
Decisions (J):      1. AUDIENCE MOOD [J:rung] (T-15-10): Easy - glad to be entertained (a festival, a
                         friendly tavern); Moderate - indifferent (a market, a busy common room); Hard -
                         bored or discerning (a court, a guildhall feast); Very hard - hostile (a rival's
                         hall, a crowd that has come to jeer); Legendary - a crowd in riot.
                         Between two: the higher. Stored as the venue's DC for the scene.
Computation [D]:    DC = the tier; reach Standard; delivery per T-15-5 *perform* column; coin per
                    T-15-11 (by settlement and delivered reach); a reputation entry at reach 4 (11)
Stakes:             Safe at Easy and Moderate (an indifferent crowd costs nothing); Risky at Hard+
                    (cost.closed_door: barred from the venue; or cost.harm from a thrown cup)
State writes:       coin; crowd mood fact (scene); contact NPC (reach 3+); reputation (reach 4)
Narration may not imply: fame beyond the reputation write; coin beyond the table
Worst case (J):     one tier = 5 DC (class i), shown in the OFFER
Examples:           inside Moderate: Wren sings in the Ashford market on a fair day. inside Hard: the
                      same song at the margrave's table. boundary Easy vs Moderate: a harvest feast
                      where she is a stranger -> Easy (glad to be entertained).
                    non-example: "It's the best song ever written" -> the tier is the crowd's mood
Anchor:             yes. Intent verbs: perform, play, sing, recite, preach, orate, juggle, busk, rouse
                    the crowd. Knobs: dc (tier), reach_unit (coin -> the crowd's mood as a lever for
                    a later beat -> morale ticks of an allied force), time_cost (a song -> an evening).
Basis:              [T-00-5] [deed.influence.performance] [DL-15-15]
```

**15.4.6 Command.** `[D]` + `[J:flag]` [DL-15-09; DL-15-33; C:III; revision: I-065] An order to someone a fact says must obey the PC — a hireling or
follower (16), a soldier under the PC's recorded rank (11), a servant of the PC's household. *Within duty*
`[J:flag]`: *"Is the order within the subordinate's recorded duty (the hireling's role, the soldier's
post)?"* True → R1 and certain if they are Neutral or warmer (15.3.10); false → a request (15.4.1) with
their standing, or a refusal of their own. Companions in conflict are commanded by 06's command action;
their loyalty and refusals are 16's. *Worst case (J):* an out-of-duty order treated as within duty — one act
the subordinate grants without a roll (class i; 16's loyalty clock still reads the deed).

**15.4.7 Crowds and groups.** `[D]` [DL-15-15; DL-06-20; C:IV; revision: I-065] A **group** that decides together (three guards, a family, a council
of five) is one listener with the highest defense among its deciding members and the lowest standing
among them (the doubter sets the bar); its patience is the lowest. A **crowd** (a market, a mob, a
congregation, a mustered company) is an obstacle, not a person: Talk to a crowd is resolved as perform
(15.4.5) or as a request against the crowd's **mood tier** (T-15-10) with reach capped **Limited** by
scale (01.6.10) unless an Amplifying fact offsets it (a leader of theirs beside the PC; the crowd already
favorable). A crowd's mood is a scene fact; it moves by delivered reach (one rung per reach 2+ on a
request; perform's delivery) and resets at `scene_end` unless a reputation write (11) keeps it. In
conflict, a mob is one entity (06) and talk to it ticks its morale clock.

**15.4.8 Social licenses: established facts that open doors.** `[D]` Principle VII's third license
source — an established narrative fact — appears in social play as a few **fact licenses**
(`data/licenses.yaml owner-block 15`), each with a crude fallback and acquisition paths like any license:
**`lic.15.audience`** (leave to address a lord, court or council in person; without it, putting a request
or motion to them is G3, redirected to a courtier or a petition at reach Limited); **`lic.15.safe_conduct`**
(an authority's guarantee: its guards and officials treat passage, lodging and arms as R1);
**`lic.15.guest_right`** (a host's protection under their roof; breaking the peace writes `betrayed` on the
host); and **`lic.15.persona`** (15.5.6). Each is acquired by a request to someone with the authority to
grant it (a `bargain` path), by rank (11), or, for the persona, by a downtime week. *Worst case:* a
missing audience treated as held — one request reaches a decider directly instead of second-hand (class
iv; the license id is cited in the frame) [C:VII; DL-15-31].

### 15.5 Deception: lies as recorded beliefs with sealed truths

**15.5.1 Deceive.** `[J:enum]` + `[J:flag]` + `[D]`

```
### 15.5.1  Deceive: make them believe it                          [J:enum] [J:rung] [D]
Trigger [T]:        the PC tells an NPC something the PC knows or suspects is false (or does not know to
                    be true), to get a request granted or a belief held
Loads in:           situation.social.*
License check:      basic verb: verb.talk (G1). Impersonating a SPECIFIC person needs a disguise license
                    (lic.training.guile_disguise; Sneak excludes it, 00.12.5) -- without it the claim "I
                    am Lord Aubrec" to someone who knows Aubrec's face is known false (G4).
Decisions (J):      1. THE CLAIM: PR-15-1 extracts each factual statement the character makes; those the
                       PC does not know to be true are claims. One beat carries one claim (a story with
                       several load-bearing lies is split into beats, 01.2.2, or told as one claim whose
                       plausibility is that of its weakest part).
                    2. PLAUSIBILITY [J:enum] (15.5.2)
                    3. PERCEIVED SIZE [J:rung] (15.3.2) "How big would the request be to this person IF
                       the claim were true?" (the point of most lies: "I'm the inspector, open up" turns
                       an R4 into an R2). The ceiling checks the perceived size after terms.
Computation [D]:    DC = 10 + Wits + competence (insight or deception, highest) + edge + status + standing
                    mod + request mod (perceived, effective) [+5 language fallback]. Plausibility:
                    plausible -> nothing; doubtful -> one Precision snag (-2, engine-applied, outside the
                    two-snag count, inside the +-4 cap: 00.3.9 g); outrageous -> reach capped Limited;
                    known false -> G4 for the belief intent (no roll, nothing spent; the redirect offers
                    another story or an honest request).
                    Usually a secret frame (01.4.7): whether they believed it is the NPC's mind.
                    On success: 15.5.3's writes. On failure: the threatened cost (cost.exposure by
                    default: S2 = alert and "a lie that doesn't sit right"; S4 = identified as a liar).
Stakes:             Risky; Dire when discovery would bring violence or arrest from someone of band >= the
                    PC's (01.6.9 HEAVY)
State writes:       claim fact (believed, truth sealed); record_knowledge; lie record; memory lied_to;
                    the granted act; alertness on failure
Narration may not imply: that the NPC believes more than the claim; that the PC can tell it worked
                    beyond the NPC's visible conduct (a secret frame narrates only conduct)
Worst case (J):     plausibility one rung too kind = one snag or a reach cap missed (class i); perceived
                    size one rung small (class i); and every successful lie leaves a truth-out clock, so
                    a lenient call is self-correcting over time (class iii)
Examples:           WE-15-2 (the reeve's messenger, believed and later unravelled)
                    inside: "The reeve sent me for the ledger" to the reeve's clerk, who has not seen the
                      reeve today -> doubtful (unverified, a stranger) -> snag; perceived R2 (fetching
                      a ledger for the reeve's messenger is a favor), actual R4.
                    outside: the same claim to the reeve himself -> known false -> G4.
                    non-example: "I'm so convincing that he can't help believing me" -> plausibility
                      reads the claim against what he knows, never the delivery
Anchor:             yes. Intent verbs: lie, bluff, con, fool, pass as, talk my way in, feign. Knobs: dc
                    (Wits; allowed delta: tier for a crowd), attribute (Presence -> Intellect for a
                    constructed account), reach_unit (an act -> a held belief only), time_cost (a line
                    -> a staged con over a scene: a progress clock vs a truth-out clock, racing).
Basis:              [01.18.7 "doubtful: snag; outrageous: Limited; known false: G4"] [R4 §9 10 #3
                    (Story-Engine claimCheck)] [R: https://arxiv.org/abs/2609.23043] [DL-15-16]
```

**15.5.2 Claim plausibility.** `[J:enum]` + `[D]`

```
### 15.5.2  Claim plausibility                                     [J:enum] [D]
Trigger [T]:        a deceive beat's claim; a bluffed threat (15.4.3); any claim the PC makes to an NPC
                    that a request rests on (15.3.7 item 3)
Loads in:           situation.social.*
License check:      —
Decisions (J):      PLAUSIBILITY [J:enum], checked against the NPC's KNOWLEDGE (12.10.6), never the
                    DM's or the PC's (T-15-9; data/social.yaml#claim_plausibility):
                    KNOWN FALSE - true only when the NPC holds a knowledge record, witnessed an event,
                      or has role/origin knowledge (12.10.6 a-d) of a fact the claim contradicts; or the
                      claim is checkable on the spot and the PC cannot produce the check (he asks to see
                      the writ). Cite the fact id.
                    OUTRAGEOUS - true only when nothing the NPC knows contradicts it but it asserts what
                      someone of their role and experience would think almost never happens (the queen
                      herself sent you; the dead man is alive and in the next room).
                    DOUBTFUL - true when the claim is consistent with what they know but unlikely or
                      unverified: it rests on something they could check later, comes from a stranger at
                      a moment that suits the stranger, or asks them to act on it at once.
                    PLAUSIBLE - consistent with what they know and ordinary in their experience.
                    Between two: the WORSE for the liar.
Computation [D]:    the engine then shifts the rung: alertness suspicious or alert -> one rung worse;
                    alarmed -> two rungs worse; a `caught_lying` memory of the PC -> one rung worse;
                    evidence produced (a document, a token, a costume, a confederate who confirms;
                    a fact) -> one rung better (that fact is then not also a lever). Clamped.
                    Effects: known false G4 (belief intent); outrageous reach Limited; doubtful one
                    snag; plausible none.
Stakes:             —
State writes:       frame.claim {fact, plausibility, shifts}
Narration may not imply: that the NPC weighed the speaker's charm
Worst case (J):     one rung = a snag or a reach cap (class i); KNOWN FALSE wrongly called makes a
                    possible lie G4 -- the redirect still offers another story (class iv), and the
                    cited fact id is checkable
Examples:           inside DOUBTFUL: "I'm a pilgrim bound for the Fen Chapel" to a gate guard, in muddy
                      boots with no pilgrim's token. -> with a pilgrim's token (a fact) -> PLAUSIBLE.
                    inside OUTRAGEOUS: "I'm the margrave's daughter" to a village alewife who has never
                      seen her. outside: the same to the margrave's steward -> KNOWN FALSE.
                    non-example: "But it's a really believable story!" -> plausibility is the claim
                      against their knowledge
Anchor:             no
Basis:              [01.18.7] [R7 §4.2 claim plausibility] [12.10.6] [DL-15-16]
```

**15.5.3 What a successful lie writes.** `[D]` A lie that lands is state, so NPC knowledge stays
consistent for the rest of the campaign [R1 #12; R4 W7]:
1. **The belief**: `set_fact(subject, predicate, value, source: claim, certainty: believed, truth: false,
   held_by: [npc])` — the claim as a fact *in the believer's mind*; its sealed truth is the real fact (which
   already exists, or is settled now by a sealed Oracle, 01.15.6).
2. **Knowledge**: `record_knowledge(npc, belief_fact, how: told_by pc)`. The NPC now acts on the belief
   exactly as on a known fact (12.10.6: an NPC acts only on what it knows; a belief is what it knows).
3. **The lie record** `lie.<n>`: `{liar, claim_fact, truth_fact, believers [{npc, since, how}],
   plausibility, persona (if any), contradicted_by [fact patterns], truth_holders [ids], clock, status:
   holding | exposed | dead}`. `truth_holders` are the NPCs who know the truth (12.10.6 a–d), written now.
4. **Memory**: `lied_to` (salience 2; no standing change: they do not know).
5. **The granted act** as T-15-5.
6. **Spread**: when a believer later tells another NPC (a scene where they speak; ch.11's rumor
   propagation by scope), that NPC is added to `believers` with `how: told_by <npc>`, and the belief is
   recorded for them — a lie travels as the truth would.
7. **The truth-out clock** (15.5.4) is created.
The PC's own journal records the lie (15.9.16): the player always knows what they have told to whom.

**15.5.4 The truth comes out.** `[D]` Every lie record owns one hidden clock `clk.truth_out.<lie>` (kind
`danger`, owner 15; template `clk.15.truth_out`), named for the obstacle — "The truth about <subject>" —
sized by the claim's final plausibility: **plausible 8, doubtful 6, outrageous 4**. Its only tick sources:

| Source | Ticks |
|---|---|
| `week` boundary, while any truth-holder shares a place or a faction with any believer (engine query) | 1 (auto) |
| the PC extends the lie: tells it to a new believer, or adds a load-bearing detail | 1 |
| the PC acts, before a believer, in a way the lie contradicts (`[J:flag]`, citing the beat) | 2 |
| a believer takes `cost.exposure` S2+ on any beat involving the PC | U(severity) |
| a believer investigates (an NPC fortune check, 01.6.7, when the lie's subject matters to them: a `[J:flag]` citing their want) | delivered reach |

Omens (stirring / building / imminent; `data/social.yaml#truth_out_omens`, two or more each, the engine
picks): someone asks an odd question about the story; a detail is repeated back slightly wrong / the
believer goes quiet when the subject comes up; a letter arrives for them from someone who knew the truth /
the believer asks to speak with the PC alone; a stranger who knew the subject is asking after the PC.
A lie with no truth-holders left alive and in contact never auto-ticks: some lies can hold forever.
**On completion** the lie is exposed to every believer (15.5.5) and, if there were three or more
believers or any public believer, ch.11 writes a rumor ("they say the stranger at Harlan's was never his
brother") [R: https://bladesinthedark.com/progress-clocks; 00.8; DL-15-17].

**15.5.5 Exposure.** `[T]` + `[D]` [DL-15-17; C:I; revision: I-065] A lie is exposed **to one believer** when `record_knowledge(believer,
fact)` writes a fact that the lie's `contradicted_by` matches (they are told the truth, they see the
proof, the real brother walks in), or **to all** when the clock completes. For each exposed believer:
1. the belief is superseded (`truth: false`, `certainty: established`, known to them);
2. memory `caught_lying` → **−2 standing** (T-15-2), and every later claim the PC makes to them is one
   plausibility rung worse while the memory is active (15.5.2);
3. patience 0 for the scene if they are present;
4. if the lie had won an **R3+ act**, the engine asks the Oracle "does <NPC> act to undo it or set the law
   on the PC?" at **Likely**, odds committed at exposure (SG-12);
5. the lie's status becomes `exposed` when no believer remains deceived.
**Confession.** Before exposure the PC may confess to a believer (a Talk beat with no roll): the belief is
superseded and the memory is `lied_to → confessed`, a **−1** step instead of −2, with no plausibility
penalty afterward. Honesty, late, is still worth a rung. A believer who **dies or departs** for good is
removed; a lie with no believers is `dead` and its clock voided.

**15.5.6 Disguise and false identities.** `[D]` + `[J:flag]` [DL-15-31; DL-15-16; C:VII; revision: I-065] Passing as *a kind* of person (a pilgrim, a
tinker, a guardsman) is a claim (15.5.2) whose costume, papers or tools are evidence (one rung better).
Passing as *a specific* person is G3 without `lic.training.guile_disguise` (05) and, with it, a deceive
whose claim is "I am X" against everyone who knows X's face (their knowledge, 12.10.6); a recorded scar or
maim that X lacks is a snag (07). A **maintained persona** — a false name and story the PC uses across
scenes — is the fact-license `lic.15.persona` (`data/licenses.yaml owner-block 15`): acquired by a week's
preparation in downtime (papers, clothes, a rehearsed story; 15.13.13), it makes claims *consistent with
the persona* start at plausible, and **all** lies told under it share one lie record and one truth-out
clock (size 8), so a persona is safer than a string of separate lies and, once exposed, exposes everything
said under it. *Consistent* `[J:flag]`: true only when the claim follows from the persona's recorded story.
*Worst case (J):* a claim wrongly judged consistent starts one plausibility rung better than it should (one snag
fewer); every lie under the persona shares its truth-out clock, so the error is exposed with the persona
(class i). [integration: 00.2.3 audit]

**15.5.7 Alertness.** `[D]` **Alertness** is an observer's state of watchfulness, toward a named entity or
toward "intruders" in general (a sentry's post), on a four-rung ladder: **unaware → suspicious → alert →
alarmed** (01.13.6; 06.2.4; 10.10.4). It is stored as `alertness` on the NPC (15.2.1). Its effects
(T-15-12, `data/social.yaml#alertness`):

| Rung | Means | Surprise (06.2.4) | Deception (15.5.2) | Other talk | Sneak against them |
|---|---|---|---|---|---|
| **unaware** | not expecting anyone; going about their business | can be surprised | no shift | normal | no snag |
| **suspicious** | something is off; looking about | cannot be surprised by the source they noticed | one rung worse | normal | no snag (they look, but not well) |
| **alert** | actively searching, weapon to hand | cannot be surprised | one rung worse; a perceived R3+ request needs evidence or is outrageous | patience −1 | a Precision snag (−2) on Sneak beats against them |
| **alarmed** | raising the alarm or fighting | cannot be surprised | two rungs worse | only parley, Yield, or a claim backed by evidence is heard; anything else is G4 ("they're shouting for the watch") | the snag, and they call others (10's site check or an encounter) |

*Raised* only by (closed list): `cost.exposure` (01.13.6: S1 +1 step; S2 at least alert; S3 alarmed); a
`trait.sense.loud` beat they can hear (unaware → suspicious); being told "someone is about" (a knowledge
record: at least suspicious); a site becoming **roused** (10.13.9: denizens alarmed); an alarm raised within
hearing (alarmed); a failed deception against them (by its exposure cost). *Default* at write-on-mention:
unaware; a sentry on duty `suspicious` at night; anyone in a roused site `alert`. *Decay* `[D]`
(`h.15.alertness_decay`, `hour`, phase 5): an observer not raised during the past hour steps down one rung,
but never below its **floor**: a sentry's post floor (suspicious at night, unaware by day; 10 and the region's seed set
others, 12.16.9), and `suspicious` for the rest of the day for anyone who reached `alarmed`. Alertness is
background; the narrator voices it through the observer's conduct (12.14.7) [01.13.6; 06.2.4; 03 Interface
request; DL-15-18].

### 15.6 Reading people

**15.6.1 Read (insight).** `[J:enum]` + `[D]`

```
### 15.6.1  Read a person                                          [J:enum] [D]
Trigger [T]:        the PC watches and listens to an NPC to learn what they feel, want, fear, would
                    refuse, or whether they lie
Loads in:           situation.social.*, situation.investigation.inquiry
License check:      basic verb: verb.observe ("read a person", 00.12.5) -- G1
Decisions (J):      1. ITEMS [J:enum] (bundled, 01.10): the player's questions from this closed list,
                       deduplicated and ranked: (a) are they lying about <the thing just said>? (b) what
                       do they feel right now? (c) what do they want? (d) what do they fear? (e) what
                       would they refuse? (f) are they hiding something about <subject>? (g) how do they
                       regard <a named person>? N <= 5.
                    2. CONCEALING [J:flag] per item: "Is the answer sealed (a want, fear, refusal, secret,
                       or the truth of what they said)?" True -> the item is read against their MASK and
                       the frame is secret (01.4.7). False (their visible mood, the stored standing toward
                       someone they speak of openly) -> tier Easy.
Computation [D]:    DC = mask = 10 + Presence + competence (guile.deception) + edge + status (standing does
                    not enter: friends hide things too) for concealed items; Easy (10) for open ones; the
                    frame uses the higher if items mix. Reach Standard; deliver_count(N, reach) in rank
                    order (01.10.4). Each delivered item: the NPC field becomes known_to_pc (want, fear,
                    refusal), or a fact is unsealed through its gate (12.10.3), or for (a) "they are lying"
                    / "no lie you can see" (the latter also when they sincerely believe a falsehood);
                    record_knowledge for each. Failure: one vague impression (believed, true).
                    Critical failure: a plausible falsehood (people can mislead: misleadable = true),
                    small and correctable (01.10.4) -- never "they are telling the truth" about a
                    threat to the PC's life.
                    Time: within a conversation, no extra time; watching from afar, one interval.
Stakes:             Safe when the NPC cannot notice (watched from cover); otherwise Risky with threatened
                    cost.exposure S2: they notice being studied (alertness suspicious; patience -1)
State writes:       known_to_pc flags; record_knowledge; unseals; journal entries
Narration may not imply: the content of a secret when only "hiding something" was delivered; a lie's truth
                    when only "they are lying" was delivered
Worst case (J):     CONCEALING wrongly false on a sealed item: the item is read at Easy -- one sealed field
                    revealed early on a roll it should have needed a harder DC for (class i: a want or fear
                    is a lever source, never a solution); wrongly true: a harder DC on an open item (class i)
Examples:           inside: Wren watches the reeve as he denies knowing the smugglers; items (a) lying?
                      (c) what does he want? -> both concealed -> mask 10 + 1 + 0 = 11; success Standard,
                      N=2 -> 1 item: (a) "he's lying". He still wants something; she doesn't know what.
                    boundary: asking a Friendly ferryman what he wants -> not a read: a Friendly NPC
                      shares R3 confidences (T-15-1): it is a certain request (15.3.10).
                    non-example: "I can just tell he's lying, I'm very perceptive" -> a declaration,
                      resolved by this frame; competence is the character's (deed.influence.insight)
Anchor:             yes. Intent verbs: read, size up, watch his face, sense, tell if he's lying, figure
                    out what she wants. Knobs: dc (mask; allowed delta: tier for an open crowd), targets
                    (one -> a small group: the highest mask), time_cost (in conversation -> an interval
                    of watching), reach_unit (items).
Basis:              [R: https://2e.aonprd.com/Rules.aspx?ID=1201 (Discover)] [C:P17] [01.10] [12.10.4]
                    [R5 SO-02] [DL-15-19]
```

**15.6.2 When an NPC lies to the PC.** `[J:flag]` + `[D]` An NPC lies only for a reason in their record:
*Reason* `[J:flag]`: *"Does the NPC's record give a reason to lie here — a sealed secret the truth would
expose, a want the lie serves, standing Unfriendly or Hostile, or an order of their faction?"* True only
with a cited field; false → they tell what they know, within T-15-1's *share* row (and a refusal of kind
`past` makes them decline, not lie). When they lie, the engine resolves it as **their** aimed action
(00.3.3): a secret fortune check (01.6.7) of the NPC's Presence + `guile.deception` competence against the
PC's **insight defense** `10 + Wits + competence (influence.insight) + edge + status`. NPC failure → the PC
receives a tell, the fact `pc.suspects.<npc>.<topic>` (certainty `believed`; a citable Precision lever for
a Read on that topic; journal: "something didn't sit right"). NPC success → nothing is perceived. Neither
result reveals the truth. *Worst case (J):* a lie told without a cited reason — the claim check flags an NPC
acting against its record (class iv) [00.3.3; 12.10.6; R4 W7].

**15.6.3 What reading can never do.** `[D]` A read reveals the NPC's own state, never content beyond its
gate: knowing someone lies does not reveal the truth; knowing they hide something does not reveal what;
a read cannot unseal a clue node whose prerequisites are unmet (12.10.3; 15.9.2) or a secret whose gate is
something other than this NPC's confiding [R1 01.D "Triggering Unknown Facts"; INV-10].

### 15.7 Negotiation and bargaining

**15.7.1 Deals: the NPC names its price.** `[D]` A **deal** is an exchange: the PC asks for something
and offers something. Deals need no separate subsystem; they are requests whose terms are the offer. What
this part adds is how the NPC **counters** and where it **walks away** — the two things LLM-voiced
characters do worst [R4 W4]:
1. **The counter is computed, not improvised.** When a request is G4 above the ceiling (15.3.4), or the
   PC asks "what would it take?", the NPC names the **cheapest set of terms its record allows** that brings
   the effective size to its ceiling, in this order of preference: its top-ranked open want that the PC
   could serve; then payment at the request's price (U(severity) Units of its lifestyle; 15.3.2); then an
   obligation (if the NPC is Wary or better). It never asks for what its record does not contain, and it
   never names a want the PC has not learned except as "something I need — and you might be the one to
   get it" (an invitation to read them, 15.6.1). `[J:enum]` *Which want could the PC serve?* — among open
   wants, the highest-ranked whose object is reachable in state; uncertain → payment. The price an NPC names at *helps for a price* (T-12-19) is the narrator's pick from
   the same record (12.11.5); a coin price settles to the ask's band when paid [revision: R2-L; DL-12-129].
2. **The walk-away is the floor.** A payment can be haggled down (15.7.2) to **half the price** and no
   lower; an obligation's size cannot be argued below the rung it replaces. An offer below the floor is a
   refusal of the deal (patience −1).
3. **A deal carries a typed price** [revision: R2-K; DL-15-42]: once agreed, it writes a price record `{payer,
   payee, kind (coin, item, service, obligation), amount, due}` beside the agreement; paying it is a typed change (a
   quantity or possession write, 01.11.2), and a price left in words ("worth your while") takes the request's price
   (15.3.2). *Retires:* the regex price parsed from the Framer's prose (round 7, I2 §3). **A payment is the paying
   beat's consequence** [revision: R2-L; DL-15-47]: coin or goods the PC hands over move when the beat that hands them
   resolves (a gift's amount from the Reader's quantity), before any NPC reaction is decided and whatever else the
   same message asks; it is never a step of the reaction (round 8: three payments were skipped because the same talk
   asked a question, and the purse stayed at 44).
   **Accepting the counter** applies the terms to the frame (15.3.5): the request then rolls at its
   effective size, or is certain (15.3.10). The NPC's acceptance of a deal is not itself the roll; the
   roll decides whether they *trust and agree* at the effective size.
4. **A patron's job reverses the deal** [revision: I-091]: when the NPC (or 11's faction commission) asks the
   PC to do a job for coin, the offer is 08.8.8's **job fee** for the job's challenge band (03.4.3;
   `economy.yaml#job_fees`: 40 / 85 / 200 / 600 / 2,000), never a figure the DM picks. Half is paid up front when
   the patron's standing is below Warm; a failed or abandoned job leaves the PC only that half. The PC may
   argue the fee (15.7.2), by one notch at most.

**15.7.2 Bargain: argue the terms.** `[J:flag]` + `[D]`

```
### 15.7.2  Bargain: argue the terms of a deal                     [J:flag] [D]
Trigger [T]:        the PC disputes the payment or the conditions the NPC named (15.7.1), or a service's
                    fee, a hire's wage, a ransom, or a patron's job fee (15.7.1 item 4)
Loads in:           situation.social.bargaining, situation.social.parley, situation.downtime.commerce
License check:      basic verb: verb.talk
Decisions (J):      1. ROOM [J:flag] "Is the NPC free to move on this price?" (08.8.7's test: false for a
                       posted fee, a tithe, a toll, or an NPC whose refusal names the PC)
Computation [D]:    frame: bargain (T-15-4), primary tag deed.influence.trade.haggling (prices) or
                    .venture (a contract's conditions); DC = 10 + Wits or Presence (higher) + trade
                    competence + edge + status + standing mod (no request mod: the deal was already
                    sized). Asking = price + 1 notch (08.8.2's notch of the payment's band);
                    delivered reach 0 -> asking stands; 1 -> the price; 2 -> -1 notch; 3 -> -2 notches;
                    4 -> -3 notches; floor half the price. A patron's job fee (08.8.8) moves the other
                    way and by one notch only: delivered reach 2+ -> +1 notch; less -> the fee stands
                    [revision: I-091]. For a non-coin condition: each delivered
                    reach rung from 2 up removes one of the NPC's named conditions or reduces an
                    obligation's due (a year's service -> a season's). One bargain per deal per day
                    (01.4.2). Levers: a rival offer that is a fact; the NPC's need (a want served by
                    closing quickly); evidence of the thing's flaw. A rival offer that is not a fact is
                    a claim (15.5.2).
Stakes:             Risky: cost.closed_door S2 (they hold firm for the day), S3 on a critical failure
                    (they will not deal with the PC this week)
State writes:       the agreed terms (a fact on the deal); commitments; coin on acceptance
Narration may not imply: a price the tool did not compute
Worst case (J):     as 08.8.7 (class i / iv)
Examples:           inside: the ferryman's price to row Wren to the drowned chapel by night is 2 Units of
                      a poor lifestyle (R3: 8 coins; band 2, notch 2), so he asks 10; delivered
                      reach 2 -> 6 coins; the floor is 4.
                    boundary: the temple's healing fee (posted) -> ROOM false.
                    non-example: "Eight coins is robbery and you know it" -> an assertion; no lever
Anchor:             yes. Intent verbs: haggle, bargain, negotiate terms, beat down, talk up, settle a fee,
                    set a ransom. Knobs: dc (defense), reach_unit (notches -> conditions), stakes.
Basis:              [08.8.7] [R5 SO-03] [DL-15-20]
```

**15.7.3 Haggling over goods.** `[D]` [DL-15-20; DL-15-01; R5 SO-03; revision: I-065] Buying and selling goods is 08.8.7's frame, which this chapter
composes: the trader's standing toward the PC enters the DC (T-15-1); the asking price takes the standing
row's **price shift** (Unfriendly +1 notch; Friendly −1 notch; Devoted at cost, never below 08.8.7's floor;
a Hostile trader will not trade); a refusal of kind `pc_requests` makes ROOM false; a claimed rival offer
is a claim (15.5.2), a recorded one is a lever. `clk.find_buyer` (08.8.5) ticks by the delivered reach of
one bargain beat per week under `deed.influence.trade`.

**15.7.4 Standing and money.** `[D]` [DL-15-01; R5 SO-03; revision: I-065] Standing changes the price of things only through T-15-1's price
shift and the DC. It never changes a posted fee, a wage table, or the market depth (08.8.5). A Friendly
smith gives the PC a better price; a Devoted one sells at cost; neither works for free, unless asked as a
request (R2–R3 by the value: a favor) — which is a request, with its own frame and its own weekly cap
(15.1.7 does not apply to requests, only to standing steps).

**15.7.5 Captors, ransom and prisoners.** `[D]` A captured PC (07's `capture`, `ransom` and `rob`
dispositions) meets the captor in a social scene. The captor's disposition **is its want** (09.9:
`captive_fate`): release for ransom serves a ransom-taker's want, so "release me for ransom" is an R2
request with a Want term — within even a Hostile captor's ceiling. The **ransom** asked is
`10 × the PC's weekly lifestyle cost × power band` coins (minimum 20), payable by the PC or by a bond,
patron or faction within a countdown clock of 4 weeks (`clk.15.ransom_due`); it can be bargained (15.7.2;
floor half). A captor whose disposition is `kill` or `drag_to_lair` has no such want: talk is the
G4-redirect of 07.4 and 09.7.6 (`parley_when`). **Prisoners the PC holds** (06.11.7) are interrogated
(15.8.4), exchanged (a deal), or released (`spared`, +2, T-15-2); a released prisoner's faction status may
move (11) [07.4; 09.9; 06.11.7; DL-15-21].

**15.7.6 Keeping deals.** `[D]` [DL-15-20; DL-15-03; R5 SO-07; revision: I-065] Every agreed deal writes two commitments: the NPC's agreed act
(`npc.<id>.agreed`, with its due condition) and the PC's side (an obligation or a payment made). Handler
`h.15.commitments_due` (`day`, phase 6) checks due conditions. **The NPC performs its act when due**
unless, first match: (1) it was coerced (15.4.3: its retaliation question may already have undone it); (2)
its standing toward the PC has fallen to Hostile since the deal (it reneges; a memory `betrayed` is not
written for the PC — the NPC broke faith, and the PC gains leverage: the NPC `owes`); (3) a fact makes the
act impossible (the gate was burned). **The PC's broken obligation** writes `betrayed` (−3) on the NPC, a
reputation entry for "breaks their word" in the NPC's scope (11), and, if the obligation was an oath, the
oath consequences of 04/11. A kept obligation writes `promised` kept (+1).

### 15.8 Social conflict over several exchanges

**15.8.1 The persuasion campaign.** `[J:flag]` + `[D]`

```
### 15.8.1  Persuasion campaign: wear down a refusal of degree      [J:flag] [D]
Trigger [T]:        a request whose effective size is exactly one rung above the NPC's ceiling, with at
                    least one term, and the NPC at Wary or better (15.3.4); the player chooses to pursue
                    it over several scenes
Loads in:           situation.social.*, situation.downtime.*
License check:      basic verb: verb.talk; every beat by its own method
Decisions (J):      1. VARIED [J:flag] per beat: "Is this beat's method or anchor different from the one
                       that last ticked the progress clock?" (01.14.6 requires_varied_approach: argue
                       one day, do them a favor the next, bring a voucher, read them for a new want).
                       False -> the beat cannot tick progress. Uncertain -> false.
Computation [D]:    two racing clocks (00.8.5), both public to the player:
                    PROGRESS clk.15.persuasion.<npc> "<NPC>'s resistance to <request>": 4 segments for
                      a target of R2 or R3, 6 for R4, 8 for R5; ticks = delivered reach; decays 1 per
                      week with no tick.
                    PATIENCE clk.15.patience.<npc> "<NPC>'s patience": 4 (Wary), 6 (Neutral, Warm), 8
                      (Friendly); ticks 1 per failed beat (2 on a critical failure) and 1 for a beat
                      taken as success at a cost.
                    Beat DC = 10 + defense terms + standing mod + request mod of the rung BELOW THE
                    TARGET (the ceiling rung when the campaign began: each exchange asks only for ground
                    within what they could grant), fixed for the campaign. At most one beat per
                    NPC per day. A resolved deed that serves one of their wants (Cultivate, 15.13.6)
                    ticks progress 2 without a roll. A newly discovered want or a new term can be added
                    at any beat.
                    Progress fills first -> the NPC grants the request (T-15-5 Standard), with a
                    compromise (15.8.2). Patience fills first -> the NPC refuses for good: a refusal of
                    class pc_requests scoped to THIS request, lifting only when a new fact changes the
                    matter; no standing loss.
                    A standing change during the campaign changes the beat DC's standing mod and the
                    patience clock's size (current fill kept). If the effective size comes within the
                    ceiling mid-campaign, the campaign continues; the player may instead drop it (losing
                    the progress) for one ordinary request.
Stakes:             each beat Risky with the fixed cost "patience ticks" (no closed door: the campaign
                    clocks ARE the door)
State writes:       both clocks; beats' writes; the grant and compromise commitments; or the refusal
Narration may not imply: the clocks' fills as anything but the person's visible weariness or warming;
                    that a single beat changed their mind
Worst case (J):     VARIED wrongly true: one beat ticks progress it should not have (at most 3-4 ticks,
                    class i); the compromise and the patience clock still bound the result
Examples:           WE-15-6. inside: the Neutral abbess (ceiling R2) is asked to lend the reliquary (R4);
                      Wren brings one term (it serves the abbess's want "their faith": the relic is to
                      bless the plague-house) -> eff R3 = ceiling + 1, Wary or better, one term ->
                      campaign. outside: the same abbess at Warm (ceiling R3) -> eff R3 is within the
                      ceiling: one ordinary roll. outside: the Neutral abbess with no term -> eff R4 is
                      two above the ceiling -> G4; the redirect names what she would need.
                    non-example: "I keep arguing until she gives in" -> a campaign needs a term and
                      varied approaches; re-arguing rides on the last failure
Anchor:             yes. Intent verbs: talk her round over time, wear him down, court, work on, lobby.
                    Knobs: duration (clock sizes; allowed delta: one size smaller for an R2-R3 target
                    between friends), time_cost (a day per beat -> a week per beat in downtime).
Basis:              [R: https://2e.aonprd.com/Rules.aspx?ID=1201 (influence over several rounds)]
                    [Burning Wheel Duel of Wits via R: https://forum.rpg.net/index.php?threads/explain-burning-wheels-duel-of-wits-to-me.760950/]
                    [01.14.6] [DL-15-22]
```

*Calibration* (`scratchpad/social15.py`, 40,000 runs per cell; win % / share of wins that carry a
compromise / mean beats): a P1 talker (+5) against a commoner (defense 10) — Wary→R2 99/15/2.2, Neutral→R3
100/7/2.3, Warm→R4 98/25/3.9, Friendly→R5 98/30/5.6; against a defense of 16 (a courtier) — 82/44/2.9,
89/37/3.4, 54/65/4.9, 39/76/6.7; an untrained PC (+1) against defense 13 — 74/49/3.0, 83/43/3.5, 42/70/4.8,
27/80/6.5. Campaigns against ordinary people mostly succeed and mostly cost a compromise past Warm; against
the skilled and the great they are real contests. The cost the numbers do not show is **time**: one
beat per day at most, a want-serving deed for the ticks a roll cannot give, and a world that moves meanwhile.

**15.8.2 Compromise.** `[D]` [DL-15-22; revision: I-065] When a campaign's progress completes, the patience clock's fill decides the
price (Burning Wheel's winner owes a compromise in proportion to the ground they gave): **below half**
→ a clean yes; **half or more (building)** → yes with **one compromise**: the NPC attaches a condition
drawn from its top-ranked open want (or, if none can be served, a payment of the target rung's price),
written as an Obligation on the PC with a due condition; **imminent** → **two** compromises (its top two
wants, or a want and the payment). The PC may refuse the compromise: the campaign then ends with neither
grant nor refusal, and a new attempt needs a new fact (01.4.2). A compromise kept writes `promised` kept;
broken, `betrayed` (15.7.6).

**15.8.3 Debate and council.** `[J:flag]` + `[D]` A contest of argument between the PC and an opposing
speaker before someone who decides (a council, a court, a lord, an assembled village): one **tug clock**
(00.8.6) `clk.15.debate` "<the body>'s verdict on <motion>", **6** segments (an ordinary matter) or **8**
(a grave one: R4+), starting at half. Each exchange is one beat per side: the PC's beat (request, deceive
or perform by method) is framed against the **presiding decider's** defense with their standing toward the
PC and the **motion's** request size, and moves the clock up by delivered reach; the opponent's beat is an
engine fortune check (01.6.7) of the opponent's Presence + influence competence against the same decider's
defense with *their* standing toward the opponent and the same motion size, moving it down by its delivered
reach. Evidence, vouchers and the crowd are levers as usual; `requires_varied_approach` applies to both
sides. The clock reaching full carries the motion; reaching 0 defeats it; after **six exchanges**
(the body's patience) without either, the side above half wins narrowly (a compromise as 15.8.2 attaches
to a narrow PC win), and exactly half keeps the status quo. *Is the opponent present and arguing?*
`[J:flag]`: true only with an NPC id in the scene holding a stake; false → it is a request to the body
(15.4.7 group). *Worst case (J):* a debate run where a request was owed — the OFFER shows the structure first
(class ii) [01.14.5; R5 TOR councils; DL-15-23]. *Anchor: yes* — intent verbs: argue before, plead the case,
debate, sway the council, petition the court; knobs: duration (6/8), targets (decider), dc.

**15.8.4 Interrogation.** `[J:flag]` + `[D]` [C:P8; C:III; R5 SO-01; revision: I-065] Questioning an unwilling holder of information (a captive, a
suspect, a hostile witness) over time. One progress clock "<NPC>'s silence on <subject>" sized by the
information's request rung (R3 4, R4 6, R5 8; 15.3.2), racing **"<NPC> hardens"** (6). Each beat is one
interval (an hour in a cell) by any method — request with terms, intimidate with a credible threat,
deceive ("your partner has already talked": a claim), read for a fear or want to use next — ticking
progress by delivered reach; failures tick hardening as 15.8.1's patience. Each beat's DC is the method's
social DC (15.3.3) with the request mod of **R2** (each exchange presses for a little more); the
information's size lives in the clock instead, and **terms shrink the clock**: each term (15.3.5, at most
two) lowers the clock one size (R5 8 → 6 → 4). No ceiling check applies per beat, but a refusal that
covers telling (15.2.3) makes the whole interrogation G4 for that subject. Progress full → the NPC tells
what they know about the subject: every clue node and fact they hold on it is delivered (as a Great read,
15.9.7) and recorded. Hardening full → they give nothing more until a new fact (a new fear learned, a
witness brought, a day passed). **Information taken by harm** (any beat that inflicts `cost.harm` on the
subject, or the method torture): the subject is `misleadable` at every degree short of critical success —
at success, the lowest-ranked delivered item is a plausible falsehood (01.10.4), because people in pain say
what ends it; the subject's standing falls by `harmed`; and the deed writes conduct evidence (03:
`conduct.mercy`, negative). `[J:flag]` *"Did any beat in this interrogation inflict harm on the subject?"*
true only with a cited frame. *Worst case (J):* a harmful interrogation's falsehood missed (class iii: the next
success on the subject reveals it, 01.10.4). *Anchor: yes* — intent verbs: interrogate, question, grill,
break him, sweat a confession; knobs: duration, time_cost, dc.

### 15.9 Investigation: sealed clue graphs that cannot dead-end or leak

**15.9.1 Cases.** `[S]` + `[D]` A **case** is any question the world holds a sealed answer to and the PC
may want answered: who set the mill fire, what became of a lost bond (02.9.2), what lifts a curse (07),
where the cult meets, why the toll doubled. A case is a **thread** (11's register; `Thread.kind:
situation | quest`) plus a **clue graph** authored from a template `case.*` (`data/investigation.yaml`) or
generated by PR-15-6 when a mystery arises in play. The whole graph — solution, conclusions, placements,
fallbacks — is written **sealed at creation**, before the player can probe it, and never "decided later"
[R4 §5.2 item 1; R: https://arxiv.org/abs/2601.06973]. The narrator sees only unsealed content and the
case's atmosphere tag (12.10.3).

**15.9.2 The graph.** `[D]` [DL-15-24; DL-15-26; R5 EX-11; revision: I-065] (shapes in `data/investigation.yaml#clue_graph_template`; T-15-14)
- **Solution**: the sealed facts of what is true (who, what, how, why, where) — ordinary facts with
  `visibility: sealed`, `truth: true`.
- **Conclusion nodes** `clu.<case>.<node>`: each a proposition the PC may come to know ("the fire was
  set", "Odo set it", "the salt factor paid him", "the ledger is in the factor's strongroom"). Fields:
  `fact` (the solution fact it asserts); `necessary` (true when knowing it is required to act decisively
  on the case — to accuse, to find, to stop); `deducible_from` (one or more **sets** of clue-content facts,
  and optional lore keys, that jointly entail it); `points_to` (nodes it leads toward); `prerequisites`
  (facts that must be in PC knowledge before any of its placements can deliver — you cannot read the
  ledger's contents before you have the ledger).
- **Placements** `clu.<case>.<node>.p<n>`: where a clue toward a node can be found. Fields: `holder` (an
  entity id: a person, a place, an object, a document, an event, a rumor), `holder_kind`, `method` (the
  method kind that reaches it, T-15-13), `access` (`core`: delivered without a roll on reaching the holder
  with the method, 15.9.5; `rolled`: needs a successful beat), `detect_tier` (rolled), `request_size`
  (person holders: what telling costs them, 15.3.2), `content` (the clue fact learned: what is seen,
  read, heard), `direct` (true when the content *is* the node's fact — a confession, an eyewitness of the
  act), `reveals_lead` (placements whose existence the PC learns from this one), `invites` (lore keys a
  finding suggests, 15.9.9), `status` (unfound | found | lost).
- **Reserve**: two spare placements per necessary node, sealed and not yet placed in the world (15.9.4).
- **Fallbacks**: at least one proactive node (15.9.12). **Opposition clock**: the case's clock, if the
  truth is still unfolding (the arsonist means to strike again; 15.9.13).

**15.9.3 What a clue is.** `[D]` [C:P5; C:I; R5 EX-11; revision: I-065] Finding a placement writes, at RECORD: `clu.<case>.<node>.p<n>.found =
true` with the frame id (03's `cnt.clue` listens to `clu.*.found`, 03.7.2); `record_knowledge(pc,
content_fact, how)`; the content fact unsealed through its gate (12.10.3); the leads of `reveals_lead`;
and journal entries (15.9.16). A clue is the **content** — the oil-soaked rag under the miller's bench —
never the conclusion it supports, unless the placement is `direct`.

**15.9.4 The Three Clue Rule, enforced.** `[D]` For every **necessary** node, the graph must hold
(validated by PR-15-6 at creation; a graph that fails is not written):
1. **at least three** placements that point to it (direct, or whose content appears in one of its
   `deducible_from` sets);
2. across them, **at least two** holder kinds and **two** method kinds (so one gap in the character's
   abilities or one refused witness cannot block it);
3. **at least one** `core` placement;
4. holders in **at least two** different places (one fire cannot burn them all);
5. **two reserve** placements.
And for the case: every necessary node is reachable from at least one placement whose holder the PC can
reach from where the case begins, and the case carries at least one fallback. During play,
`h.15.placement_audit` (`scene_end`, phase 6, before 12's lead audit at phase 7) recomputes, for each
unfound necessary node, its **live** placements (holder exists, is not destroyed, dead or departed beyond
reach, and the placement is not `lost`); when fewer than **two** are live, it places one reserve placement
in the world (sealed; a new witness, a copy of the letter, a second traveller who saw), and when the
reserve is spent it generates one by PR-15-7. The Alexandrian's rule — "for any conclusion you want the
PCs to make, include at least three clues" — becomes an invariant the engine keeps true, not advice the
narrator must remember [R: https://thealexandrian.net/wordpress/1118/roleplaying-games/three-clue-rule;
R6 B-13; R5 P-41; 12.8.4; DL-15-24]. **Reduced profile** [revision: R2-D] [DL-15-38]: a reduced case (PR-15-6) holds
2 necessary nodes meeting items 1–4 with **one** reserve each, and its entry core placement is at the place where it
began; `h.15.placement_audit` runs for reduced cases from Milestone 1 (full cases from Milestone 6), so the Three Clue
Rule holds in the first playable build.

**15.9.5 Core clues never fail.** `[J:flag]` + `[D]`

```
### 15.9.5  Core clue: reached is found                           [J:flag] [D]
Trigger [T]:        a beat whose target is the holder of an unfound core placement whose prerequisites
                    are met
Loads in:           situation.investigation.*
License check:      the method's own (a search is G1; reading a script needs the language; 15.9.6)
Decisions (J):      1. REACHED [J:flag] "Is the PC at the holder (present with the person, in the place,
                       holding the object or document) and does the beat's method fall in the placement's
                       method kind (T-15-13)?" True only with the holder's id in the scene and a
                       matching method. Uncertain -> true (the tie-break that keeps the case moving;
                       P16).
                    For a person holder asked a question, whether the question is ABOUT this
                    placement is one small model call over the question and the placement's
                    `about` line, never shared words (PR-12-10 step 1) [revision: R2-K;
                    DL-15-40]; yes -> the clue is a `learned` fact the
                    narrator conveys from a knower present, never an NPC "acts:"
                    line (12.14.12) [revision: R2-L; DL-15-44].
                    2. For a person holder: the placement's request_size is within the person's ceiling
                       and no refusal covers telling (15.2.3); otherwise the clue is not core FOR THIS
                       ASK -- it is a request or an interrogation (15.8.4), and the other placements
                       carry the node.
Computation [D]:    NECESSITY = certain (01.4.1): the core content is delivered without a roll, at the
                    method's time cost (T-15-13); clocks listening to time or noise still tick; a frame
                    record with necessity.reason "certain" carries the frame id for 03.
                    Anything more the player seeks at the holder (rolled placements, bundled questions)
                    is a rolled beat (15.9.7).
Stakes:             none for the core content (the time is the price)
State writes:       15.9.3's writes
Narration may not imply: that the clue was hard won or barely found; anything beyond its content
Worst case (J):     a core clue delivered one beat early (the method was a near fit) -- the case moves
                    one step sooner (class i); a clue that is never a solution by itself unless direct
Examples:           inside: Wren searches the burned mill (holder: the mill, method search) -> the core
                      placement "the lamp-oil smell at three separate spots" is delivered, no roll.
                    outside: Wren questions the miller about the fire (method inquiry, holder: the
                      miller) -> not the mill's core placement; the miller's own placements apply.
                    boundary: the miller holds a core placement (he saw Odo near the mill at dusk, R1 to
                      tell) and is Neutral -> delivered without a roll; if telling would implicate his
                      son (request_size R4) it is a request, not core.
                    non-example: "I search so thoroughly that I must find everything" -> the core content
                      is found because it is core, and rolled placements still roll
Anchor:             no
Basis:              [R: https://pelgranepress.com/gumshoe/files/GUMSHOE%20SRD%20CC%20version.pdf] [R5 P-41]
                    [C:P16] [DL-15-25]
```

**15.9.6 Investigative methods.** `[J:enum]` [C:V; R5 EX-11; revision: I-065] Every investigative beat is one method kind of T-15-13
(canonical `data/investigation.yaml#methods`), which fixes its anchor, attribute, DC source and time.
Default when uncertain between two: the one whose anchor is a basic verb the beat already uses.
Looking for a case's target (a fugitive, a missing person, a placed thing) is an investigative beat like any other:
where it is and how it is found come from the case's placements and leads (15.9.5, 15.9.8), never from a Move toward
an unplaced target (01.18.5) [revision: R2-I; DL-12-98].

**T-15-13 Investigative methods.**

| Method kind | Anchor (verb · attribute · primary tag) | DC source | Time (free / site / downtime) | Reaches holder kinds |
|---|---|---|---|---|
| **search** | 10's `act.search`: observe · Wits (Intellect for papers) · `lore.investigation.search` | the hidden thing's `detect_tier`; nothing there → sealed Oracle first (01.4.7) | 10 min a room, 1 hour a building / 1 interval an area / — | place, object, document |
| **inquiry** | Talk request for information (15.4.1) · Presence · `lore.investigation.inquiry` | the person's social DC at the placement's `request_size` | a few minutes per person; "asking around" a settlement: 1 day (15.13.9) | person, rumor |
| **read** | 15.6.1 · Wits · `influence.insight.*` | mask | within the conversation | person (their own state) |
| **study** | observe · Intellect · `lore.investigation.search` (a wound: `lore.medicine`; a mechanism: `lore.engineering`; an inscription: 10's `act.study`) | the object's tier | 1 interval | object, place (traces) |
| **research** | 15.9.14 · Intellect · `lore.investigation.records` | the archive's tier | 1 hour a beat / — / a week (15.13.4) | document |
| **surveillance** | 15.9.15 · Wits (watch) or Agility (follow) · `lore.investigation.search` / `guile.stealth` | the target's Wits defense | 1 watch a beat | person, place, event |
| **recall** | 09.10.2 / `verb.recall` · Intellect · the lore tag | the lore's tier | free (an instant) | lore keys (15.9.9) |
| **interrogation** | 15.8.4 | per method | 1 interval a beat | person |
| **deduce** | 15.9.9 (no roll) | — | 1 interval of thought (free mode: none) | conclusions (from held clues) |

*Worst case (J):* the wrong class — the beat reaches nothing at a holder that a neighbor method would have
reached; the journal lists the leads' method hints and the redirect names the fitting method (class ii).

**15.9.7 Graduated delivery of findings (P17).** `[D]` + `[J:enum]` A rolled investigative beat at a
holder delivers through 01.10 and 12.10.4:
1. **Eligible set** `[D]`: the holder's unfound placements whose method kind matches and whose
   prerequisites are met — the permitted slice. Nothing outside it can be delivered, at any degree
   (a critical success on "what does the sealed letter say?" before anyone has the letter reveals nothing
   inside it) [R1 01.D].
2. **Items**: the player's questions, deduplicated and ranked (01.10.2–01.10.3). An undirected beat
   ("I search the study") has as its items the eligible rolled placements themselves, ordered by 12.10.4's
   preference (most directly answering; then leading onward; then most remaining placements on its node);
   that count is engine-held and never shown.
3. **Count** `deliver_count(N, delivered reach)` (01.10.4): Standard success ⌈N/2⌉; Great N; Limited 1;
   Exceptional N plus a bonus (an unasked relevant item from the slice, or a follow-up lever).
4. **Failure**: one **vague impression** of the top item — a true, hedged trace written `believed` ("the
   floorboards by the hearth look newer than the rest"), which is itself a **lead** and a citable Precision
   lever for the next beat at that spot. **Critical failure**: nothing reliable; a plausible falsehood only
   if the holder can mislead (a forged document, a lying witness, a staged scene; 01.10.4 `misleadable`).
5. **Re-asking** rides on the result (01.10.6): a new method, a new lever, a passed interval, or the
   re-attempt cost.
6. **Which content** `[J:enum]` for each delivered item: 12.10.4 step 1, never beyond the slice.
*Worst case (J):* a less useful true placement chosen — the count of true findings is unchanged (class i).

**15.9.8 Leads.** `[D]` [DL-15-24; DL-12-11; R5 EX-11; revision: I-065] A **lead** is knowledge that a placement exists ("the ferryman saw something that
night"; "the factor keeps a second ledger") without its content. Leads come only from: a found clue's
`reveals_lead`; a rumor whose `points_to` is a placement or node (11); lead injection (12.8.2); an NPC's
sharing within their T-15-1 row; a vague impression (15.9.7). Leads are journal entries with the holder,
the place and the **method hint** (search, ask, watch, read). A lead is **live** while its placement is
reachable (15.9.4). 12's live-lead audit reads the journal's live leads (12.8.4).

**15.9.9 Deduction and theories.** `[J:enum]` + `[D]`

```
### 15.9.9  Deduce: test a theory against what you hold            [J:enum] [D]
Trigger [T]:        the player states a conclusion they believe ("Odo set the fire for the salt factor's
                    money") and asks to reason it out, or records it as a theory
Loads in:           situation.investigation.*
License check:      free activity (recall your own memories and established facts, 00.12.6): no roll
Decisions (J):      1. NODE [J:enum] "Which conclusion node of an open case, if any, does the theory
                       assert?" True only when the theory's proposition matches a node's fact in subject,
                       predicate and value. A theory matching no node (whether wrong, or right about
                       something no node holds) -> none. Uncertain -> none.
                    2. CITED CLUES: the player names, or the DM lists from the journal, the clue facts the
                       theory rests on; only facts in the PC's knowledge may be cited.
Computation [D]:    write pc.theory.<n> {statement, cites, status}. If NODE = none -> status unsettled.
                    If NODE = n and the cited facts (plus lore keys the PC holds) contain one of n's
                    deducible_from sets -> status SUPPORTED: record_knowledge(pc, n.fact, how: inferred,
                    certainty: believed) -- the character has reasoned it out; the journal marks it
                    "supported by your clues", and it is citable as evidence (a Precision lever when
                    confronting someone with the reasoning, 15.3.6). Otherwise -> UNSETTLED.
                    The answer the DM gives is exactly one of two sentences: "Your clues support it" or
                    "The clues you hold don't settle it." A wrong theory and a right one with too few
                    clues get the SAME answer, so the check never leaks the solution.
                    Lore keys are never named against a theory; each clue's own `invites` lore keys are
                    shown with the clue (15.9.16), whatever the player theorizes.
                    Time: one interval in site mode; none in free mode.
Stakes:             none
State writes:       theory record; knowledge (inferred) when supported
Narration may not imply: that a supported theory is confirmed; that an unsettled one is wrong; any hint
                    of which ("you're on the right track", "not quite")
Worst case (J):     NODE wrongly matched -> at most one theory marked supported whose clues truly entail
                    a neighboring node (the data's deducible_from sets bound it; class i); wrongly
                    unmatched -> "unsettled" for a right theory, curable by finding a direct clue
                    (class iii)
Examples:           WE-15-3 (two routes to the same supported and then confirmed conclusion)
                    inside: theory "the fire was set", citing oil smell at three spots + the rag under
                      Odo's bench -> node "fire set" deducible_from {oil smell, rag} -> SUPPORTED.
                    outside: theory "Odo set it", citing only the oil smell -> UNSETTLED (same answer a
                      wrong theory gets).
                    non-example: "It's obviously Odo, tell me if I'm right" -> the DM never confirms by
                      narration; the deduce check gives one of its two sentences
Anchor:             no
Basis:              [R4 §5.2 items 3-4] [R1 #12] [R: https://arxiv.org/abs/2609.23043] [DL-15-26]
```

**15.9.10 Confirmation comes only from evidence.** `[D]` The narration never confirms a theory ("you
realize you were right"). A conclusion is **confirmed** — recorded `certainty: established` — only by:
1. a **direct** placement found (a confession heard, an eyewitness of the act, the stolen thing in the
   suspect's chest);
2. a **confession** delivered by a resolved Talk or interrogation beat (15.8.4) from someone who holds the
   fact;
3. a **test**: the PC acts so that the world's response depends on the sealed truth (sets a watch on the
   granary the arsonist will try next; shows the dead man's ring to the widow) — the engine resolves the
   response from sealed state (the culprit, if he is the culprit, comes; the widow, if she knows the ring,
   reacts), and the response is an `event` placement written and found;
4. an **accusation** made in the fiction: the accused responds from the truth and their record — the guilty
   lie (15.6.2's fortune check gives the PC a tell or nothing), flee, bargain or confess (a Talk frame);
   the innocent deny sincerely (a read shows no lie). A wrong public accusation writes `insulted` or
   `harmed` (by its consequence) and may write reputation (11): being wrong has a cost.
A theory is **refuted** only when a found clue directly contradicts it [12.10.3; DL-15-26].

**15.9.11 The truth does not move.** `[D]` [DL-15-26; C:P13; revision: I-065] The sealed solution is immutable (INV-10; 00.6.5). The DM never
revises who did it, how, or why to match a player's theory, however elegant, nor to make a dramatic reveal
land. If play exposes a contradiction inside the authored graph (two solution facts that cannot both
hold), the DM logs a `rule_conflict` ruling and repairs it with the smallest change that keeps every
**found** clue true (usually: add a clue that explains the discrepancy), never a new culprit. The claim
check (12.3) treats narration that implies a different solution as a `leak`/`state` error.

**15.9.12 Proactive fallbacks.** `[T]` + `[D]` Every case holds at least one **fallback**: a proactive node
that comes to the PC (the Alexandrian's proactive nodes) — the opposition acts, a witness seeks the PC
out, a new victim is found, evidence surfaces. Shape: `{trigger, form, delivers}`: `trigger` is the case's
thread becoming `stalled` (12.8.4: no live lead), its opposition clock reaching a named fill, or `n`
scenes without a new clue (default 3, counted by 11's `h.11.fallback_counters`); `form` from the case's
data or `tbl.15.fallback_form`; `delivers` one **core** placement of an unfound necessary node, placed in
the world as the fallback fires (the witness arrives knowing it). Ch.11 fires fallbacks; this chapter
authors them and guarantees each delivers a necessary node's core clue [R6 B-R4; 12.8.2 source 2;
DL-15-24].

**15.9.13 The opposition clock and investigating omens.** `[D]` [DL-00A-20; R5 EX-11; revision: I-065] A case whose truth is still unfolding
carries an **opposition clock** (hidden, with omens; 00.8): the culprit's plan (`clk.<case>.<plan>`, "The
arsonist strikes again", 6). Its omens are perceivable traces and, by this chapter, **leads**: each omen
rendered is written as a lead toward the placement the omen's stage names (the case data lists, per
stage, which placement an attentive investigator can follow). Investigating an omen (a search, inquiry or
surveillance beat on the trace) that delivers **reach 2 or more** raises the clock's visibility one step
(hidden → sensed → public); **reach 4** raises it two steps (00.8.4). A public opposition clock is the
player's deadline, shown in the codex.

**15.9.14 Research.** `[J:rung]` + `[D]` [DL-01-01; DL-00A-20; R5 EX-11; revision: I-065] Finding things out from records, books and archives. *Anchor:
yes.* One beat = one hour in free mode; in downtime, a **Research week** (15.13.4). Method `research`:
Intellect, `deed.lore.investigation.records` (a script needs its language and `lic.lang.letters`, 02). DC =
the archive's **tier** `[J:rung]` by how obscure the subject is *in that collection*: Easy (a parish
register, a town's tax rolls for a name), Moderate (a guild's private books; a library on a common
subject), Hard (an ancient library on a half-forgotten matter), Very hard (a lost topic in a great
collection), Legendary (a subject deliberately expunged). An **extended** research question is a progress
clock "What the <collection> holds on <subject>" of **4** (Easy–Moderate), **6** (Hard), **8** (Very hard+),
ticked by delivered reach, one beat per day (or per downtime week); completion delivers every `document`
placement for the subject in that collection and the lore keys it holds. A **sage** (08.8.8: 10 coins a
question) answers one question as a fortune check of the sage's Intellect + lore competence against the
question's tier, delivered as one item (01.6.7). Knobs: dc (tier), time_cost (hour → day → week), duration
(clock size). *Worst case (J) of the tier:* one rung = 5 DC, shown (class i).

**15.9.15 Surveillance.** `[D]` [DL-15-18; DL-00A-20; R5 EX-11; revision: I-065] Watching or following someone or somewhere over time. *Anchor: yes.* A
progress clock "<Target>'s routine" — **4** (their daily habits) or **6** (what they hide: meetings,
caches) — racing **"<Target> notices the watcher"** (4, danger). Each beat is one **watch** of Observe
(Wits, from a fixed post) or Sneak (Agility, following), against the target's Wits defense (their
alertness snag applies, 15.5.7); ticks by delivered reach; failures tick the danger clock by U(S2) = 1 (2
on a critical failure). Routine complete → every `event` and `place` placement of the target's routine is
delivered (who they meet, where they go, when). Notice complete → the target's alertness toward the PC is
alert and their routine **changes**: routine placements are `lost` and the placement audit replaces them
(15.9.4). Knobs: duration, time_cost (watch → day), targets.

**15.9.16 The journal.** `[D]` [C:P7; C:IV; DL-00A-22; revision: I-065] The **journal** is the player's view of what the character knows (00.6.3:
"Clues found, PC knowledge — 15, shown"), rendered by the codex (14) from `record_knowledge`,
commitments and memories. It contains nothing sealed. Sections (T-15-15, `data/investigation.yaml#journal`):
**Cases** (each open case: clues found with their content and invited lore keys; live leads with holder,
place and method hint; theories with status *supported* / *unsettled* / *confirmed* / *refuted*; open
questions — items asked and not delivered, 01.10.6); **People** (names learned; standing rung; known
wants, fears and refusals; what the PC has told them, including lies); **Places** (discovered, with notes);
**Rumors heard** (text and source; truth unknown); **Lies told** (each lie record the PC made: claim,
believers the PC knows of — never the clock); **Debts and promises** (commitments both ways, with due
conditions); **What you were told** [revision: R2-L; DL-15-46]: the `said` records spoken to the PC, each attributed
(who said it, where, on which day) and grouped by thread or topic, testimony with its truth unknown. A "what do I
know about X?" lookup searches the thread text, the said records and the knowledge records, never names alone
("X and Y" is split), so the baker's word that the miller's daughter left with a tinker is found under the daughter.
*Retires:* the name-only lookup (round 8: "what do I know" gave one line and ignored the winter and the banners). The
journal is the only source for "what do I know about X?" besides origin knowledge
(12.10.5).

**15.9.17 `record_knowledge` semantics.** `[D]` `record_knowledge(knower, fact, how)` (00.14.2 #14; owner 15)
writes `{knower, fact, how, at, source_ref, certainty}` where `how` ∈ {witnessed, told, read, overheard,
recalled, inferred, rumor, confided} and `certainty` is the knower's (`established` for witnessed, read,
confided and confirmed facts; `believed` for told, inferred and vague impressions; `rumored` for rumors).
Knowledge is append-only: a superseded fact keeps its record, marked superseded, so "what did he believe
then?" stays answerable. Write points: every delivered item (01.10.5); every name learned (12.10.2); every
claim told to an NPC (`told`; belief follows 15.5); every witness of a beat (12.10.6 b); rumor spread (11).
**Consistency invariant:** an NPC's dialogue and decisions use only their knowledge records and beliefs
(12.10.6); the PC's narration uses only the PC's (12.10.1) [R1 §10 "knowledge contradictions"; 12.10.5–12.10.6].

**15.9.18 Rumors as clues.** `[D]` [DL-11-11; R5 SO-06; revision: I-065] A rumor (11; `{text_seed, source, truth, points_to}`, truth sealed) heard
by the PC is recorded `rumored` and, if its `points_to` is a placement or node, is a **lead** (15.9.8). A
rumor is never itself a clue toward a conclusion's `deducible_from` (hearsay entails nothing); finding the
placement it points to is. A rumor whose truth is `false` points to a placement that exists and **refutes**
it — a false rumor still leads somewhere real.

**15.9.19 Small mysteries from other chapters.** `[D]` [DL-15-24; C:P16; revision: I-065] Chapter 02's lost bond (a sealed fate whose gate is
a clue) and chapter 07's curse lifts (sealed conditions with three clue placements) are cases of one
necessary node each, generated by PR-15-6 with the minimum graph of 15.9.4 (three placements, two kinds,
one core, one fallback) [02 Interface requests; 07 Interface requests].

**15.9.20 Cases and research as lore contests.** `[D]` `[revision: I-003]` A beat on a case (15.9.1) or on research (15.9.14) is a **lore contest** (03.4.3) when
a principal NPC or a faction keeps the truth: the culprit of a case, the order that seals an archive, the
cult that guards a name. Its contest band is that keeper's, read as in 15.3.11: an NPC keeper's own band
(its faction's tier only when it is that faction's head or officer), a faction that keeps the truth itself its
tier, a power of the far rings its band (12.16.11, each keeps a sealed truth); never above the actor's
`power_band` + 2 [revision: I-039]. A case or a research project is **one opposition** for 04.3.4: at most two of a
tier's great deeds come from it, however many days its beats take [revision: I-083]. A Dire beat whose threatened
cost destroys a necessary node's last unfound placement or ends the case (the witness silenced, the ledger
burned, the culprit fled for good) is **ruinous** (03.4.5); a beat declared while the case's opposition clock
(15.9.13) stands one segment from full is **one from full** (03.4.5) [revision: I-046]. Research with no keeper uses its DC's band, as
before [03.4.3; 03.4.5; DL-15-32].

### 15.10 Downtime: the week planner

**15.10.1 Entering and leaving downtime.** `[D]` + `[J:flag]` The time mode is `downtime` (00.7.3) when the
PC is in safety — a settlement, a holding, or a haven (07.8's rest site `haven`) — and the player chooses
to spend days or weeks rather than play scene by scene (the rules' calibration assumes 1–6 weeks after an
adventure and an optional season a year, 12.7.7 [revision: I-085]). `[J:flag]` *"Is the PC in a haven with no pending
threat, active conflict, or clock that would complete within the first day?"* True only with the place's
rest-site fact and no such clock; false → downtime cannot begin (the DM names what is pressing). Downtime
ends when the plan runs out, the player stops it, or an **interrupt** (00.7.8) halts `advance_time`: the
DM frames a scene at the interrupting event, and the unspent remainder of the plan resumes afterwards if
the player wishes [00.7.3; 00.7.8; R5 P-12 Blades session cycle]. *Worst case (J):* downtime begins with a
pressing clock unnoticed; `advance_time` still runs every boundary, and the clock's own interrupt halts the
plan at the moment it matters (00.7.8; class iv). [integration: 00.2.3 audit]

**15.10.2 The week plan.** `[D]` The planning unit is the **week** (00.7.3; ch.11's World Turn runs on
each). For each week the player sets a plan of **one week activity plus up to two day activities**, or
**seven day activities** (T-15-16 marks each activity's scale). A week activity needs **five days** of the
calendar week; day activities take one day each. The plan is written as `downtime_plan {week, main,
days[]}` and run by `advance_time` day by day, so every boundary runs (INV-15): `h.15.downtime_day`
(`day`, phase 6) applies each day activity completed that day; `h.15.downtime_week` (`week`, phase 6, after
`h.11.world_turn` in registry order) resolves the week activity (its rolls and ticks). A week activity
interrupted with fewer than five of its days done ticks nothing that week; the days already spent are
spent (time is the cost). *Why one main activity:* Ars Magica budgets a season for one main activity and
Blades gives two downtime actions; a week with one serious undertaking and a couple of errands is the same
rhythm at this game's week cadence, and it makes breadth cost time, which is the point (P15) [R6 B-05;
R5 P-45; C:P15; DL-15-27].

**15.10.3 What downtime costs.** `[D]` [DL-15-27; DL-08-20; R5 TM-06; revision: I-065] (1) **Lifestyle**, charged by 08's `h.08.upkeep` every week the PC
spends any day in a settlement (08.8.6: 0/4/7/14/35/100); (2) each activity's own coin (fees, materials,
an evening's drinking), charged when the activity is resolved, refused if the PC cannot pay (the activity
does not happen, the day is not spent); (3) **time**, during which the world moves: every day runs ch.11's
situation timelines, every week a World Turn, every season a Season Turn (00.7.7). Downtime is never free
of the world.

**15.10.4 The activity menu, and what is not on it.** `[J:enum]` + `[D]` T-15-16 (canonical
`data/downtime.yaml#activities`) is the closed list of downtime activities, each with its scale, method,
duration, costs and effects. Downtime is the one pillar where a menu is right — it is bookkeeping, not
improvisation [R4 §9 10 #6] — but goal 1 still holds: a player who wants to spend their weeks on
something unlisted ("I write a ballad about the siege"; "I court the baker's daughter") has it anchored to
the nearest activity `[J:enum]` (a project; Cultivate; perform as work) under the two-change limit
(00.2.7), and the ruling is logged. Uncertain → **project** (15.12), the most general container. *Worst
case (J):* a near-but-wrong anchor, bounded by the two-change limit and logged (class iv).

**15.10.5 Rolls in downtime.** `[D]` [DL-15-27; R5 TM-06; revision: I-065] A downtime activity that rolls makes **one roll per its interval**
(a day activity once that day; a week activity once that week): let it ride applies to the interval
(01.14.6). Its stakes are **Safe** unless a cost source exists (01.6.9) — failure then spends the time and
the coin and delivers nothing. Levers and snags are cited facts as everywhere (a master's workshop; a
library's catalogue; a rival's sabotage). Downtime rolls are ordinary frames: the OFFER shows them, and
`auto_commit` (14) may resolve the routine ones.

**15.10.6 Evidence and reflection in downtime.** `[D]` [C:P5; C:P2; DL-03-12; revision: I-065] Downtime yields **counted** evidence only:
`cnt.training` (1 unit per trained tag per week, 03.5.5), `cnt.progress` (project and campaign ticks,
03.7.2), `cnt.made` (crafting). It never yields judged evidence: a montage is not a deed (03.5.5); a scene
framed inside downtime (an interrupt, a social call played out) is play, and yields evidence as play does.
Each week spent in downtime fires `reflection` (`h.00.reflection_if_downtime`), so recognition (04) and
provisional confirmations run on the downtime cadence.

### 15.11 Learning: training, licenses, abilities, tongues

**15.11.1 Train.** `[J:enum]` + `[D]`

```
### 15.11.1  Train: learn from a teacher, a text, or practice       [J:enum] [D]
Trigger [T]:        the PC spends a downtime week learning something
Loads in:           situation.downtime.training
License check:      the target's requires (05.9.4: arcane - letters and a text or teacher; divine - a keeper
                    who accepts the PC; primal - a place or spirit that accepts them); a text needs its
                    language and lic.lang.letters; the target's grade cap (only trained by these paths)
Decisions (J):      1. TARGET [J:enum] (T-15-18; the player names it, the DM classifies):
                       TRAINING LICENSE lic.training.<tag> -> clk.train.<lic> (8; project; public)
                       ABILITY of the pool -> clk.learn.<ab> (6 / 8 / 12 by min_tier; 05.8.5); needs the
                         training license of its first tag at a grade covering its min_tier
                       TONGUE lic.lang.<x> -> clk.learn_tongue (8; completion raises the grade one step)
                       LETTERS lic.lang.letters -> clk.learn_letters (8)
                       RITE rit.* -> clk.learn_rite (6; 05.8.7)
                       DRILL a deed tag the PC already uses, under a mentor -> no clock; cnt.training only
                       Default when uncertain: the target the player named most literally.
                    2. SOURCE [J:enum]: MENTOR (an NPC whose record holds the target: the license at
                       expert or lic.call.proof for the tag; the ability at rank 2+; the tongue at
                       accented+; the rite known), secured by 15.11.2; TEXT (an item with the fact
                       teaches: <target>, 08.4); IMMERSION (tongues only: living a week among speakers);
                       PRACTICE ALONE (abilities only, after witnessing it, 05.8.5).
Computation [D]:    ticks per completed week (T-15-18): training license - mentor 2, text 1; ability -
                    mentor 3, text 2, practice alone 1; tongue - immersion 2, teacher or text 1; letters -
                    teacher 2, text 1; rite - teacher 3, text 2. No roll: time is the price (P15).
                    Fee per week to a mentor (08.8.8): 7 for a trained-grade license, a tongue, letters,
                    a min_tier 1-2 ability, a personal or local rite, or a drill; 25 for a min_tier 3-4
                    ability or a site rite; 100 for a min_tier 5 ability or a regional rite.
                    Every completed week writes cnt.training (1 unit) on the target's tag: the license's
                    tag; the ability's first deed tag; deed.lore.languages for tongues and letters; the
                    rite's school tag; the drilled tag (03.5.5; counted at most half of a calling's
                    counted requirement, 04.3.3).
                    On completion: grant (provisional, source learned/taught; 05 and 04 confirm at the
                    season boundary) -- the clock grants, a roll never does (INV-7).
                    One learning clock per character per week ticks (a teacher cannot teach two things
                    in one week; a text cannot be read for two).
Stakes:             none (no roll)
State writes:       clock; coin; cnt.training; grant on completion; the mentor's memory `owed` for any fee
                    unpaid (cleared when paid; a waived fee is a favor received, `owed` until returned)
Narration may not imply: mastery beyond the grade granted; a capability before the clock completes
Worst case (J):     TARGET or SOURCE misclassified: the wrong clock ticks one week (class iv: the player
                    sees every clock and can correct it next week)
Examples:           WE-15-4 (a month: lockwork from a locksmith, and a project)
                    inside: four weeks with the Ashford locksmith -> clk.train.guile_thievery 2/4/6/8 ->
                      lic.training.guile_thievery at trained (+2 competence), 28 coins.
                    outside: a week of "practice" picking her own door with no teacher and no text ->
                      not a path for a training license (05.9.4); the redirect names the locksmith.
                    non-example: "I study so hard I finish in two weeks" -> ticks are fixed per source
Anchor:             yes. Intent verbs: train, study, learn, apprentice, be taught, practice. Knobs:
                    time_cost (week; allowed delta: none), duration (clock size by target).
Basis:              [05.8.5] [05.9.4] [02.4.6 tongues] [03.5.5] [04.3.3] [08.8.8] [C:VII] [C:P15] [DL-15-28]
```

**15.11.2 Finding and securing a teacher.** `[D]` + `[J:flag]` [DL-15-28; DL-11-18; DL-15-09; revision: I-065] A teacher is a person, and teaching is a
request. *Finding*: from a lead, a bond (a mentor bond, 02.9.2), an institution (11's
`institutions_matching(deed_branch, region)`), or the Oracle — "is there someone in <settlement> who
teaches <target>?" at **Likely** (a common trade in a town or city), **Even** (a common trade in a village;
an uncommon art in a city), **Unlikely** (an uncommon art in a town; magic in a village), **Remote** (magic
of a rare school outside a city) — odds committed before the roll, answer written as a fact (00.12.7);
the region's settlement facts override (`teachers`, 12.16.11). *Securing*: "teach me" is a request (15.4.1) of size **R3** for a
trained-grade course or a tongue (a week of their time, repeated), **R4** for an ability of min_tier 3+, a
magic license, or a rite (their art's secrets). The weekly fee is a **Payment** term when it meets the
price (it usually does: a modest teacher's R3 price is 14 coins against 28 in fees for a four-week course).
A teacher at Friendly or better may waive the fee (an R2 favor; certain at Friendly per 15.3.10). The
magic `requires` of 05.9.4 are refusals in effect: a keeper that has not accepted the PC teaches nothing
divine (G4 with the redirect "first be accepted"). A secured teacher writes `npc.<id>.agreed: teach
<target>` (15.7.6) and keeps teaching each week while paid. *Worst case (J):* the Oracle's odds rung for "is
there a teacher" is one step off (15–25 points), committed before the roll and logged; securing the teacher
is still a request with its own frame (class i). [integration: 00.2.3 audit]

**15.11.3 Learning a new license: Principle VII's paths.** `[D]` [DL-15-28; DL-00A-19; C:VII; revision: I-065] This is the main way a character
legitimately gains a capability outside recognition. When a beat is G3 (unlicensed), its redirect names
the license's `acquisition_paths` (00.12.1). PR-15-8 runs the chosen path:
| Path type (00.12.1) | Where it runs | What it takes |
|---|---|---|
| `mentor` | this chapter: Train with a teacher | finding and securing them (15.11.2); weeks at the T-15-18 rate; fees |
| `project` | this chapter: Train from a text; or a project (15.12) for a license whose entry names one | a text or the project's clock |
| `discovery` | a found text, a place of power, a spirit's acceptance (05.9.4 primal); an Oracle at the place | the fact that unlocks it, then the clock |
| `institution` | 11: a rank that carries training (an order trains its members) | the rank; then Train with the institution's teacher at no fee |
| `bargain` | 08's `gen.gift` / a patron (05.8.7, 11) | the patron's price (a commitment) |
| `item` | 08: an item that licenses while carried | the item (never feeds tiers) |
| `recognition` | 04: deeds, never downtime | — |
| `origin` | 02, at creation only | — |
Rolls never grant a license (INV-7); the clock or the gift does. Every new grant is provisional until the
season boundary (04, 05).

**15.11.4 Retrain.** `[D]` [R5 AD-05; C:VI; revision: I-065] The only way to exchange what is already learned (02.2.6 "a training is
exchanged only by chapter 15's Retrain"; 04.8.7). A Retrain is a week activity; one at a time:
- **A calling pick** (04.8.7): one week, one pick swapped by PR-04-5 (outside the free re-pick at the
  season boundary).
- **An origin training license** for another training license: **two** weeks with a teacher of the new one
  (the habits of learning carry over: double the mentor rate of 05.9.4); the old license is retired from the
  character (`revoke`, ledger note); the new one is granted at `trained`.
- **An origin competence entry** (+2 on a tag, 02): moved to a tag whose training license the PC holds;
  **two** weeks with a teacher of the new tag.
Retrain never changes attributes, origins, birth results, callings, or a calling's grade-given licenses.
Fees as Train. Each week writes `cnt.training` on the new tag.

**15.11.5 Penance.** `[D]` [DL-04-22; DL-15-27; revision: I-065] Ch.04's atonement form PENANCE (04.9.4): one downtime week at the keeper's place
(a shrine, an order's house), one cost at S3 from 01's menu in the form the keeper's nature suggests;
completed, it ticks the atonement clock 3. It counts as the week's main activity. It also serves as the
week of NPC atonement 04.9.4 allows for grudges with no oath (its completion writes a standing step: +1 on
the wronged NPC, as a kept promise).

**15.11.6 What learning never does.** `[D]` [DL-15-28; C:P2; C:VII; revision: I-065] It never grants a calling or a tier (04.11.3); never grants a
grade above `trained` (expert and master come only from tiers, 05.9.2); never compresses time (one
learning clock ticks per week; a Retrain occupies the week); never grants by roll; and never ignores a
`requires` (05.9.4) or a teacher's refusal.

### 15.12 Long projects

**15.12.1 Project.** `[J:rung]` + `[D]`

```
### 15.12.1  Pursue a project                                      [J:rung] [J:flag] [D]
Trigger [T]:        the player names a goal beyond one beat's reach that the character will work at over
                    weeks: rebuild the ford bridge, clear the Harlans' debt at law, found a school, earn
                    the guild's seat, write the chronicle of the siege, restore the shrine
Loads in:           situation.downtime.project
License check:      the weekly beat's own (building needs lic.training.craft_building; a lawsuit needs
                    standing to sue -- a fact; a book needs letters)
Decisions (J):      1. SCOPE [J:rung] (T-15-17): PERSONAL (one's own life: a book, a reputation in one
                       circle, a garden) -> clock 8; LOCAL (a village or town quarter: a bridge, a school,
                       a lawsuit) -> 12; REGIONAL (a valley, a town, a guild: a market charter, a road)
                       -> 12 + 12 (two linked clocks); REALM (a kingdom or great order: a law changed,
                       an order founded) -> 12 + 12 + 12. Between two: the larger.
                    2. OBSTACLE NAME: the clock names what stands in the way (SG-24): "The ford's broken
                       span", not "Rebuild the bridge".
                    3. ANCHOR [J:enum] for the weekly beat: the method the work is mostly done by (Talk
                       for influence; Handle under a craft license for building; research; a trade
                       venture under deed.influence.trade.venture; perform for a reputation).
                    4. TIER [J:rung] of the weekly beat (T-01-2): who could make headway against this
                       obstacle (Moderate typical; Hard where an interest opposes it). Stored.
                    5. OBSTACLES [J:flag]: named blockers that are facts (the reeve forbids it; the guild
                       holds the charter) -- each caps progress at half the clock until removed by a
                       thread (an adventure) or a social beat; removing one ticks +2.
Computation [D]:    week activity; one roll per week at the stored DC; ticks = delivered reach (1 / 2 / 3 /
                    4: Blades' 1/2/3/5 at this game's reach scale); failure ticks 0 (Safe: the week is
                    spent; Risky when an opposing interest is recorded: cost.time on its clock, or
                    cost.twist). Weekly coin by scope: personal 0; local 7; regional 25; realm 100
                    (materials, fees, gifts; never "bribes" unless the anchor is a request with
                    payment terms). Building projects use 08.8.8's holdings: the price is paid as
                    materials over the build, and the clock is the build weeks.
                    Delegation: hired labor or an ally (16) may tick a project 1 per week at their wage
                    (08.8.8), at most one delegated tick per project per week, without the PC's week
                    activity. No decay unless the project is a campaign of influence (decays 1 per week
                    with no tick). On completion: the project's on_complete writes (facts, a holding, a
                    reputation entry, a world change ch.11 propagates: LW-09).
Stakes:             Safe or Risky as Computation
State writes:       project clock(s); coin; cnt.progress; on_complete writes; obstacles
Narration may not imply: progress beyond the clock; that the world stood still meanwhile
Worst case (J):     SCOPE one rung off -> 4 segments or one more linked clock (class i), shown before the
                    first week; TIER one rung -> 5 DC (class i)
Examples:           WE-15-4 (the ford bridge, with delegation)
                    inside LOCAL: rebuild the ford's broken span (a village's bridge). boundary LOCAL vs
                      REGIONAL: a new stone bridge carrying the margrave's road -> REGIONAL (a road for a
                      valley).
                    non-example: "I'll just get the whole town to love me this month" -> a reputation
                      project, PERSONAL or LOCAL by circle, at its pace
Anchor:             yes. Intent verbs: build, found, establish, campaign for, write, restore, clear my
                    name, change the law, endow. Knobs: duration (scope), dc (tier), time_cost (week;
                    allowed delta: day for a personal project of minutes per day), reach_unit (ticks ->
                    a linked clock).
Basis:              [R: https://bladesinthedark.com/downtime-activities] [R5 P-24 (WWN's world-changing projects)]
                    [R5 P-45] [R6 B-03 long-term projects] [00.8.3] [DL-15-29]
```

### 15.13 The other downtime activities

Each is a row of T-15-16 with its full mechanics in `data/downtime.yaml`; the rules below are their
binding text.

**15.13.1 Convalesce** [DL-15-27; DL-07-11; R5 TM-06; revision: I-065] (day; 07.8.11). In a haven: each day sets `bed_rest_today` (and `treated_today` with a
licensed tender), removes one `cond.exhausted` stack; a full week sets dread to 0 and shifts a disease one
stage (07). No roll. Cost: lifestyle; a healer's care 2 coins a day (08.8.8) if hired.

**15.13.2 Solace** [DL-15-27; DL-07-15; R5 TM-06; revision: I-065] (day; 07.11.7). Carousing, prayer and worship, or a day with a bond NPC: dread −2, at most
once per week (a full week of downtime in a haven sets it to 0 anyway). A Carouse or Worship day may count
as the week's solace.

**15.13.3 Treat** [DL-15-27; DL-07-13; R5 TM-06; revision: I-065] (day). Tending a companion or another person's wounds and afflictions: 07's treatment
rules (the day counts as a Treat at reach 1 with no roll for ordinary nursing), the license 07 names.

**15.13.4 Research week** [DL-15-27; DL-05-24; R5 MG-04; revision: I-065] (week). Five days in a collection: one research roll at the collection's tier
(15.9.14), ticking a research clock by delivered reach, or delivering a non-extended question's items;
also the research clock of a rite design (05.8.4: "ticked by a research week: delivered reach").
Access to a private collection is a request (R2–R4 by whose it is). Cost: 1 coin a day for a scribe's copy
of what is found (optional).

**15.13.5 Craft** [DL-15-27; DL-08-16; R5 TM-06; revision: I-065] (day or week, by the item's `make.time_per_tick`; 08.6.4). Runs 08's crafting project:
each step is a beat at the target rung's tier, progress racing spoilage. Materials, tools and a workplace
per 08. Writes `cnt.made` at completion.

**15.13.6 Cultivate** [DL-15-27; DL-15-04; R5 TM-06; revision: I-065] (day). A day spent on an NPC's want — an errand they named or a known want served in
a small way (an R2 favor *from* the PC: a day's work and at most 1 Unit). No roll for the favor itself
unless it meets an obstacle (then it is a beat). It writes `helped` (+1, a small source: weekly cap, cap
Friendly; 15.1.7) and, in a running persuasion campaign, ticks progress 2 (15.8.1). Asking "what can I do
for you?" makes the NPC name the errand from their record (15.7.1's counter).

**15.13.7 Work** [DL-15-27; DL-08-19; R5 TM-06; revision: I-065] (week). Earning a living: the week's wage by the best grade the PC holds in a trade the
settlement has work for (08.8.8: unskilled labor 7; a trained trade 10; expert 25; master 60; a village has
work up to trained, a town up to expert, a city up to master). No roll for ordinary work; a performer may
instead perform each evening (15.4.5; coin per T-15-11). Work pays a living and no more (08.8.9 AI-2's labor
cap). It writes no evidence (routine, 03.5.3). A job taken from a patron is not Work: it is a venture or a
task of its own, paid on completion by 08.8.8's job fee for its challenge band (`economy.yaml#job_fees`;
15.7.1 item 4) [revision: I-091].

**15.13.8 Carouse** [DL-15-27; R5 TM-06; R5 SO-06; revision: I-065] (day). An evening and a night in the settlement's taverns and gathering places: costs
2 coins (a comfortable or richer lifestyle: 1 Unit); one Talk roll, Presence, primary tag
`deed.guile.streetwise.informants` (or `deed.influence.persuasion.rapport` among the respectable), against
the settlement's tier (camp or village Easy, town Moderate, city Hard). Delivered reach: **rumors** heard =
delivered reach, rolled from ch.11's rumor tables for the region (each recorded, truth sealed; leads where
they point); at reach **3+** also a **contact** — a new recurring NPC at Warm, role from
`tbl.15.carousing_contact`; failure: the coin is spent and one rumor is heard; critical failure: trouble
(`tbl.15.carousing_trouble`: a brawl, a debt, a lost item, an offended local now Hostile, a night in the
lockup, a rival's attention). Counts as **solace**.

**15.13.9 Ask around** [DL-15-27; DL-15-25; R5 SO-06; revision: I-065] (day). Inquiry about a case or a person across a settlement: a Talk request for
information against the settlement's tier, delivering person-held placements and rumors about the named
subject that are in this settlement (15.9.7 with the settlement as holder); core placements held by
anyone here who would share them at R1 are delivered without a roll. *Stakes:* Risky when someone in the
settlement is recorded as not wanting the question asked (`cost.exposure`: word gets back to them).

**15.13.10 Shop and sell** [DL-15-27; DL-15-20; R5 SO-03; revision: I-065] (day). Buying, selling and haggling (08.8.4–08.8.7; 15.7.3); one bargain beat
per `clk.find_buyer` per week.

**15.13.11 Maintain holdings** [DL-15-27; DL-11-19; R5 TM-06; revision: I-065] (day or week). For a holding the PC owns (08.8.8; 11): a day of oversight
writes `managed_this_week` (a Precision lever on 11's weekly yield roll for that holding); a week of
repair ticks the holding's damage clock down 2 (or runs a craft beat under `craft.building`). Upkeep is
08's handler.

**15.13.12 Worship and serve** [DL-15-27; DL-15-03; DL-11-15; revision: I-065] (day or week). A day keeping the rites of the PC's keeper (05.7.4): solace,
and the fact `rites_kept.<keeper>.<season>` that 05's divine standing may read. A **week of service** at a
temple, shrine or order's house is a deed for its officiant (`helped`, +1) and a reputation entry in that
faith's scope (11).

**15.13.13 Prepare a persona** [DL-15-27; DL-15-31; revision: I-065] (week). Papers, clothes, a rehearsed story: grants `lic.15.persona` for one
named false identity (15.5.6). Cost: 1 Unit for papers and dress; forged papers need a forgery beat
(`deed.guile.disguise.forgery`, Hard) or a forger's service.

**15.13.14 Recruit** [DL-15-27; DL-16-05; DL-16-02; revision: I-065] (day). Finding hirelings and followers (16): a Talk request against the settlement's
tier; delivered reach = candidates presented (16's templates; wages per 08.8.8), none of a band higher than the
settlement's hire band or the PC's power band (16.3.2) [integration: IR ch.16 to 15 (d)]. Presence sets the
retinue cap (00.4.4). Allies' own downtime duties (T-16-15) resolve in `h.15.downtime_week`, and an ally's
promise of silence (16.11.1) is a request sized by 15.3.2 [integration: IR ch.16 to 15 (e, f)].

**15.13.15 Lie low** [DL-15-27; DL-11-13; R5 LW-14; revision: I-065] (week). No public activity, no evidence, no trade: ticks down the PC's notice or
attention clock in this region by 2 (ch.11 owns the clock; Interface request).

**15.13.16 Rest** [DL-15-27; R5 TM-06; revision: I-065] (day). Doing nothing in particular. Lifestyle is charged; the world moves.

---

## Procedures

**PR-15-1 Framing a social beat.** `[D]` + the `[J]` steps named (runs inside 01's PARSE→GATE→…→RECORD)
1. **Argument mining** (PARSE). From the player's words extract, as separate lists: (a) the **intent**
   (what the NPC is to do, give, tell or believe); (b) every **offer** (coin, goods, service, promise); (c)
   every **fact the words invoke** ("your son is in that village", "I carry the margrave's writ"); (d)
   every **claim** (a statement the PC does not know to be true). Discard everything else as color
   (15.3.7): it is narrated, not counted. A fact in (c) that is not in state is an Oracle question if the
   player is asking, a claim if the character is asserting it to the NPC.
2. **Target and mind.** Resolve the listener's id (01.2.5); if a walk-on, promote to recurring and roll
   its want, fear, voice and refusal now (12.11.1; 15.2.1). Check mind and tongue (15.2.7): G4 or the
   crude fallback.
3. **Patience.** If the NPC's patience is 0, the exchange is over (15.2.6): no frame; the redirect names
   another way (another person, another day, a term for a Hostile).
4. **Method** `[J:enum]` (T-15-4).
5. **Refusals** `[J:flag]` (15.2.3): covered and not lifted → G4, patience −1, redirect; stop.
6. **Size** `[J:rung]` (15.3.2) — for deceive, the perceived size (15.5.1).
7. **Terms** `[J:flag]` ×4 from (b) and (c) (15.3.5); **levers and snags** `[J:flag]` from (c) and the
   scene (15.3.6); one fact, one use.
8. **Ceiling** (15.3.4): effective size > ceiling → G4, patience −1, the computed counter (15.7.1) and,
   where legal, the campaign option (15.8.1); stop.
9. **Claim** (deceive, bluff): plausibility `[J:enum]` and the engine shifts (15.5.2); known false → G4.
10. **Certain?** (15.3.10) → deliver the act without a roll; go to 14.
11. **DC** (15.3.3); **stakes** and **threatened cost** (15.3.8); **reach** (15.3.9); secret frame
    (01.4.7) for deceive and concealed reads.
12. **OFFER** (01.7): one line of fiction, then the DC source in plain terms ("his resolve, Wary, asking a
    real cost less one term: 16"), odds (unless secret), stakes, the threatened and alternate cost, the
    terms that will be paid (coin moves on commit).
13. **Roll; READ; near-miss choice; DELIVER** (T-15-5).
14. **RECORD**: the NPC's agreed act or belief; knowledge; memories (12.11.7) and their standing steps
    (T-15-2); patience; coin; commitments; lie record and clock (PR-15-2); evidence (03); ruling if any
    anchor delta. Then narration — which credits the cited facts, never the speech (15.3.7).

**PR-15-2 Telling a lie.** `[D]` (on a successful deceive, or a successful bluff)
1. Settle the truth: if the claim's subject is unestablished, the sealed Oracle (01.15.6) writes the
   truth first; the claim's truth value is then `false` (or `partial`).
2. Write the belief fact (believed, truth sealed, held_by the believer) and `record_knowledge(believer,
   …, told_by pc)`.
3. Find or create the lie record: if the PC holds `lic.15.persona` and the claim is consistent with the
   persona, append to the persona's record; else create `lie.<n>` with `truth_holders` (every NPC who
   knows the truth by 12.10.6 a–d) and `contradicted_by` (the truth fact's key and any fact that entails
   it).
4. Create `clk.truth_out.<lie>` (8 / 6 / 4 by final plausibility) with 15.5.4's tick sources and omens;
   or, for an existing record, tick it 1 (an extended lie).
5. Memory `lied_to` (salience 2). Journal: Lies told.
6. Register an `on_fact_set` and `record_knowledge` watch for `contradicted_by` on each believer (PR-15-3).

**PR-15-3 Exposing a lie.** `[D]` (raised by the watch of PR-15-2 step 6, or by the clock's completion)
1. For each believer exposed: supersede the belief; memory `caught_lying` (−2, T-15-2) or `confessed`
   (−1) if the PC confessed first; plausibility penalty flag; patience 0 if present.
2. If the lie won an R3+ act: queue the Oracle question "does <NPC> act to undo it or set the law on the
   PC?" at Likely, odds now, rolled at once if the NPC is free to act, else at their next free moment.
3. Clock completion with ≥ 3 believers or a public believer: ch.11 rumor write.
4. When no believer remains deceived: `lie.status = exposed`; void the clock.

**PR-15-4 Running a persuasion campaign.** `[D]`
1. Validate the trigger (15.8.1): effective size = ceiling + 1; ≥ 1 term; standing ≥ Wary; no refusal.
2. Create the two clocks; show both to the player (public); write the campaign fact with the target
   request and its terms.
3. Each beat (at most one per NPC per day): check VARIED; frame at the ceiling rung's DC; tick progress by
   delivered reach or patience by the fixed cost; a want-serving Cultivate day ticks progress 2 with no
   roll; a newly found term is added (if it brings the effective size within the ceiling, the campaign
   continues, or the player may drop it, losing the progress, for one ordinary request: 15.8.1)
   [verification: V2b-023].
4. Weekly: decay progress 1 if no tick this week.
5. Progress full → grant + compromise (15.8.2). Patience full → the scoped refusal. Either way, close
   both clocks and write memories.

**PR-15-5 An investigative beat at a holder.** `[D]`
1. Resolve the holder and the method kind (T-15-13).
2. **Core first** (15.9.5): every unfound core placement at this holder matching the method with
   prerequisites met is delivered without a roll (15.9.3's writes).
3. If the player seeks more (questions, or "search everything here"), compute the eligible set of rolled
   placements (15.9.7 step 1). Empty and the holder's contents undetermined → sealed Oracle first
   (01.4.7); empty and determined → nothing more is here (narrated exactly as a failed search would be,
   12.10.3 item 4).
4. Frame (secret if anything sealed is in question), OFFER, roll, deliver by count and preference.
5. RECORD: found facts with frame ids, knowledge, leads, journal; vague impressions as believed facts and
   leads; falsehoods only from misleadable holders.
6. If the beat investigated an opposition clock's omen: raise visibility by delivered reach (15.9.13).
7. `scene_end`: `h.15.placement_audit` (15.9.4).

**PR-15-6 Building a case.** `[D]` + `[J:enum]` (at hook creation by 11, at a mystery arising in play, or
for 02's lost bond and 07's curse lifts)
1. **Solution**: from the case template, or by tables (`data/investigation.yaml#generators`): culprit (an
   existing NPC by role and want first — a want that the crime serves — else a new principal NPC), motive
   (the culprit's want), method, place, and what remains to happen (the opposition plan). All sealed.
2. **Nodes**: a chain of 2–4 necessary conclusions from "it happened" to "who/where/how to stop it", plus
   0–3 optional ones (side truths). Each with its fact and `deducible_from` sets (each set 2–3 clue
   contents; at least one set satisfiable without lore).
3. **Placements**: for each necessary node, three or more, by `tbl.15.placement_holders` × the case's
   places and cast: at least two holder kinds, two methods, one core, two places; persons' `request_size`
   by what telling costs them, and a plain-words `about` line (what a question must be about to reach it), which
   PR-12-10's judgment reads [revision: R2-K; DL-15-40]; rolled placements' `detect_tier` by how hidden. Each placement's
   `reveals_lead` links onward (the graph's edges). Two reserve placements per necessary node.
4. **Entry**: at least one placement reachable from the case's starting place is core.
5. **Fallback(s)** and the **opposition clock** with omens, each omen stage naming a placement.
6. **Validate** 15.9.4 (1–5); a failure regenerates the failing node's placements (at most three tries),
   then logs a `rule_conflict` and adds generic placements (PR-15-7).
7. Write everything sealed; write the thread (11) with `clue_placements`; give the narrator the case's
   atmosphere tag. A case built for a hook also writes the hook's terms for its kind (11.5.6) on the cards of those
   who would know, and a person on stage in the hook's role is bound as its subject by id (12.16.16) [revision: R2-L;
   DL-12-135; DL-15-43].
**Reduced profile (Milestone 1)** [revision: R2-D] [DL-15-38; DL-15-37]: for the seed's inciting incident (12.16.16)
and for a story-role question with no case behind it (who is missing, who did it, who sent them; PR-12-10 step 1), the
case is built at once with `investigation.yaml#reduced_case`: the subject cast first (00.11 `cast`), else generated
(12.11.1); 2 necessary nodes and no optional ones; 3 placements per node (two holder kinds, two methods, one core,
two places) and 1 reserve; the first node's core placement held at the place where the question was asked (at seed
time, the opening place); 1 fallback. Step 6 validates against these numbers. *Evidence:*
`_process/simulation/12-answer_ladder_sim.py` part C: 30 of 30 valid, and the story-role question answered within 3
turns in 30 of 30, for the seeded incident, a forced "who is missing?" and an in-play question.

**PR-15-7 A replacement placement.** `[D]` When the audit (15.9.4) finds a necessary node with fewer than
two live placements and no reserve left: roll `tbl.15.placement_holders` for a holder kind not already
among the node's live placements; place it in the PC's current region (a person by 12.11.1 at recurring
depth who saw or heard; a document copy in an archive; an event — the culprit's next move, observable);
give it `access: core`; write it sealed; it becomes reachable by a rumor seeded through ch.11 (a lead).

**PR-15-8 Learning a license.** `[D]`
1. From the G3 redirect, list the license's `acquisition_paths` (00.12.1) and their `requires`.
2. The player picks a path. **Mentor/text/immersion**: find (15.11.2; Oracle odds by settlement), secure
   (a request; fees), then Train weeks (15.11.1). **Discovery**: the unlocking fact (a place, a spirit's
   acceptance, a text found) first, then the clock. **Institution**: 11's rank, then Train. **Bargain**:
   the patron's price as a commitment, then 08/05's gift. **Item**: 08.
3. Each week: tick the clock by the source's rate; write `cnt.training`; charge the fee.
4. On completion: `grant(license, grade: trained, provisional, source)`; ruling log; the codex shows it;
   04 and 05 confirm at the season boundary.

**PR-15-9 Running a downtime week.** `[D]`
1. The player states the week's plan (15.10.2); the engine validates costs, requirements and that only one
   learning clock is targeted.
2. `advance_time(1 week, mode: downtime)`: each day, `h.15.downtime_day` resolves that day's activity (rolls
   for rolled day activities; writes); each boundary runs (07 recovery, 05 recharges, 10 weather, 11
   situations).
3. Interrupt → stop; frame the scene; the remainder resumes on the player's word.
4. At the `week` boundary (phase 4 lifestyle, 08; phase 6 World Turn, 11, then `h.15.downtime_week`):
   resolve the week activity if five of its days were spent (Train ticks; a project roll; a research roll;
   Work's wage; Retrain; Penance), write `cnt.training` / `cnt.progress`; delegated project ticks; then
   `h.15.member_standing` (15.1.3); phase 8: reflection; phase 9: `h.15.standing_week` (reset small steps)
   [verification: V2b-023].
5. Narrate the week from the returned list only (PR-00-2 step 5): what was done, what was heard, what the
   world did.

---

## Tables

Tables embedded in Rules are canonical and indexed here: **T-15-1** standing contract (15.1.2); **T-15-2**
memory valence → step (15.1.6); **T-15-3** social DCs (15.3.3); **T-15-4** social methods (15.3.1);
**T-15-5** social delivery (15.3.9); **T-15-6** refusal kinds (15.2.4); **T-15-8** social levers and snags
(15.3.6); **T-15-12** alertness (15.5.7); **T-15-13** investigative methods (15.9.6). The rest are below.
Every table is mirrored in `data/social.yaml`, `data/investigation.yaml` or `data/downtime.yaml`, which are
canonical for numbers and ids (00.1.4 item 5).

**T-15-7 Request sizes** (`social.yaml#request_sizes`).

| Rung | Name | DC mod | Payment price (Units of the NPC's lifestyle) | Information equivalent | Typical | Boundary |
|---|---|---|---|---|---|---|
| R1 | trifle | +0 | 1 (U(S1)) | what anyone in their role would say | directions; when the watch changes | sit by their fire an hour |
| R2 | favor | +2 | 1 (U(S2)) | private and harmless | an introduction; look away by day | lend a mule for a day |
| R3 | real cost | +5 | 2 (U(S3)) | a confidence that betrays no one | let you into the archive after hours; lend a horse for a week | carry a sealed letter through a checkpoint |
| R4 | serious risk | +8 | 3 (U(S4)) | a secret that exposes someone | smuggle you past the gate; testify against a powerful man | hide you from the watch one night |
| R5 | grave | +10 | 4 (U(S5)) | a secret that endangers the teller; a confession | betray their lord; kill for you | hide you a week while the town is searched |

**T-15-9 Claim plausibility** (`social.yaml#claim_plausibility`): known false → G4 (belief intent);
outrageous → reach capped Limited; doubtful → one engine-applied Precision snag (−2); plausible → none.
Shifts: alertness suspicious/alert −1 rung, alarmed −2; `caught_lying` memory −1; evidence produced +1.

**T-15-10 Audience mood tiers** (`social.yaml#audience_tiers`): Easy — glad to be entertained (festival,
friendly tavern); Moderate — indifferent (market, busy common room); Hard — bored or discerning (court,
guild feast); Very hard — hostile (a rival's hall, a crowd come to jeer); Legendary — a crowd in riot.

**T-15-11 Performance and street earnings** (`social.yaml#performance_coin`), coins per evening by
delivered reach: 

| Settlement | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| camp or village | 1 | 2 | 3 | 4 |
| town | 2 | 4 | 6 | 8 |
| city | 4 | 8 | 12 | 16 |
A week of evenings is capped by the settlement's market depth (08.8.5: village 30, town 150, city 750) and
by the labor cap (08.8.9 AI-2): a fine performer in a city earns about a master crafter's wage, never more.

**T-15-14 The clue graph** (`investigation.yaml#clue_graph_template`): solution facts (sealed) → conclusion
nodes `clu.<case>.<node>` {fact, necessary, deducible_from [[clue facts | lore keys]], points_to,
prerequisites} → placements `clu.<case>.<node>.p<n>` {holder, holder_kind (person | place | object |
document | event | rumor), method (T-15-13), access (core | rolled), detect_tier, request_size, content,
direct, reveals_lead, invites, status} → reserve (2 per necessary node) → fallbacks {trigger, form,
delivers} → opposition clock (with omens naming placements). Validity: 15.9.4.

**T-15-15 Journal sections** (`investigation.yaml#journal`): Cases (clues, leads, theories, open questions) ·
People · Places · What you were told (attributed testimony) [revision: R2-L; DL-15-46] · Rumors heard · Lies told ·
Debts and promises. Visibility: shown (00.6.3).

**T-15-16 Downtime activities** (`downtime.yaml#activities`).

| Id | Activity | Scale | Method / roll | Effect (rule) | Cost |
|---|---|---|---|---|---|
| `dt.convalesce` | Convalesce | day | none | 07.8.11 (15.13.1) | lifestyle; healer 2/day optional |
| `dt.solace` | Solace | day | none | dread −2, once a week (15.13.2) | — |
| `dt.treat` | Treat another | day | 07's | 07 (15.13.3) | supplies per 07 |
| `dt.train` | Train | week | none | clocks per T-15-18; `cnt.training` (15.11.1) | fees 7/25/100 a week |
| `dt.retrain` | Retrain | week ×1–2 | none | 15.11.4 | fees as Train |
| `dt.penance` | Penance | week | none (an S3 cost) | atonement clock +3 (15.11.5) | the S3 cost |
| `dt.research` | Research | week | Intellect, archive tier | research clock / items (15.13.4) | access; copies 1/day |
| `dt.craft` | Craft | day or week | 08.6.4 | 08 (15.13.5) | materials |
| `dt.project` | Pursue a project | week | the project's anchor, stored tier | project clock (15.12.1) | 0 / 7 / 25 / 100 a week by scope |
| `dt.cultivate` | Cultivate | day | none (an R2 favor done) | `helped` +1; campaign +2 (15.13.6) | ≤ 1 Unit |
| `dt.work` | Work | week | none | wage 7 / 10 / 25 / 60 (15.13.7) | — |
| `dt.perform` | Perform for coin | day | perform vs audience tier | T-15-11 (15.4.5) | — |
| `dt.carouse` | Carouse | day | Talk vs settlement tier | rumors; contact; solace (15.13.8) | 2 coins or 1 Unit |
| `dt.ask_around` | Ask around | day | Talk vs settlement tier | placements and rumors here (15.13.9) | — |
| `dt.shop` | Shop and sell | day | bargain | 08.8 (15.13.10) | prices |
| `dt.maintain` | Maintain holdings | day or week | none / craft | lever on yield; damage −2 (15.13.11) | — |
| `dt.worship` | Worship / serve | day or week | none | solace; rites kept; service `helped` +1 (15.13.12) | offerings optional |
| `dt.persona` | Prepare a persona | week | forgery beat if forging | `lic.15.persona` (15.13.13) | 1 Unit |
| `dt.recruit` | Recruit | day | Talk vs settlement tier | candidates (16) (15.13.14) | — |
| `dt.lie_low` | Lie low | week | none | attention −2 (11) (15.13.15) | — |
| `dt.rest` | Rest | day | none | — (15.13.16) | lifestyle |
| `dt.11.train_successor` | Train a successor | week | d20 + base modifier on the tag vs Moderate, Safe | the candidate's training clock (12); banked tags (11.13.10; defined in `legacy.yaml#train_successor`) [integration: IR ch.11 to 15] | — |

**T-15-17 Project scope** (`downtime.yaml#project_scopes`): personal 8 (0 coin/week) · local 12 (7) ·
regional 12+12 (25) · realm 12+12+12 (100). Ticks = delivered reach (1/2/3/4); delegation 1/week at wages;
obstacles cap at half and give +2 when removed.

**T-15-18 Learning rates per week** (`downtime.yaml#learning`; from 05.8.5, 05.9.4, 02.4.6).

| Target | Clock | Mentor / teacher | Text | Immersion | Practice alone | Fee (mentor) |
|---|---|---|---|---|---|---|
| training license (`trained`) | `clk.train.<lic>` 8 | 2 | 1 | — | — | 7 |
| ability, min_tier 1–2 | `clk.learn.<ab>` 6 | 3 | 2 | — | 1 (after witnessing) | 7 |
| ability, min_tier 3–4 | `clk.learn.<ab>` 8 | 3 | 2 | — | 1 | 25 |
| ability, min_tier 5 | `clk.learn.<ab>` 12 | 3 | 2 | — | 1 | 100 |
| tongue (one grade step) | `clk.learn_tongue` 8 | 1 | 1 | 2 | — | 7 |
| letters | `clk.learn_letters` 8 | 2 | 1 | — | — | 7 |
| rite | `clk.learn_rite` 6 | 3 | 2 | — | — | 7 / 25 / 100 by scale |
| drill a tag | — | `cnt.training` 1 | — | — | — | 7 / 25 / 100 by the mentor's grade |
*Pace:* a trade from a willing teacher in 4 weeks (28 coins); alone from a manual in 8; a tier-1 technique
from a mentor in 2 weeks; a tongue's next grade in 4 weeks living among its speakers.

**T-15-19 NPC lifestyle by role** (`social.yaml#npc_lifestyle`) — the Unit used for payments and gifts:
destitute (beggars, the outcast) 0 → treat 1 coin as their Unit; poor (laborers, servants, common soldiers,
ferrymen) 4; modest (craftsmen, guards' sergeants, small traders, village priests) 7; comfortable
(merchants, master crafters, officers, reeves) 14; wealthy (guildmasters, rich merchants, knights, abbots)
35; noble (lords and ladies, great prelates) 100. An NPC's lifestyle is their role's unless a fact says
otherwise.

---

## Worked examples

All examples use Wren as she stands after 00 and 02 *(Wren: Might +1, Agility +3, Endurance +1, Wits +2,
Intellect 0, Presence 0, Resolve −1; competence `deed` +1, `wilds.tracking` +2, `martial.archery` +2; no
social competence — so every Talk she makes is at **+1**, and every Read at **+3**; lifestyle modest,
7 coins a week)*, except WE-15-3's second path, which uses a talker for contrast. Odds are exhaustive under
01.8.1. NPC numbers are illustrative within 09's bands; every rule mechanism is exact.

### WE-15-1 Talking past a guard: success, near miss, failure, and a hard refusal

*Scene.* Dusk at Grey Keep. The postern in the lower yard is shut at sunset by the castellan's order (a
fact: `keep.postern.curfew = sunset`; ordinary rules of a place are facts, not refusals, 15.2.4). Wren wants
through to reach the archive. The sentry, `npc.brannoc` (T2 soldier: Resolve +1, Wits +1, competence
`deed.martial` +2, none in `deed.influence`; lifestyle poor, Unit 4), has never met her.

**First interaction** (15.1.4). Not a faction member of note (the keep's garrison is ch.11's; here, an
unaffiliated hireling for simplicity). Reaction roll 2d6 = 8, no modifiers → **Neutral** (ceiling R2,
patience 3, DC mod 0). The Talk will target him, so he is promoted to recurring and his fields are rolled
**before** the frame (15.2.1): want `tbl.npc_want_verb` 9 *earn* × `tbl.npc_want_object` 4 *money* → "earn
enough to leave soldiering"; fear d12 = 1 *the watch and the law*; refusal d12 = 8 *will not leave this
place*; voice terse, habit "calls everyone 'friend'". All sealed.

**PARSE** (PR-15-1). Player: "I tell him I'm expected at the archive and slip him eight coins for his
trouble." Intent: through the postern. Offer: 8 coins. Facts invoked: none established ("expected" is a
claim — is it true? No one expects her). The DM asks the one clarifying question 01.2.4 allows, because the
answer changes the method: "Are you claiming someone expects you, or just asking?" Player: "Fine — just
asking, with the money."
- Method: **request** (honest ask + payment; T-15-4).
- Refusal: *will not leave this place* — opening a door does not require him to leave → not covered.
- Size `[J:rung]`: letting someone through a curfewed postern on duty is a rule he could be reprimanded
  for → **R3**.
- Terms: **Payment** — price of R3 = U(S3) = 2 Units × 4 = **8 coins**; offered 8 ≥ 8 → true. No `bribe`
  refusal. Effective size **R2**. (His sealed want *earn money* would also match coin — but one offer is
  one term; the engine counts it once, as Payment.)
- Ceiling: R2 ≤ R2 → legal. Certain? R2 is not two below the ceiling → roll.
- DC (15.3.3): 10 + Resolve 1 + competence 0 + edge 0 + status 0 + standing 0 + R2 (+2) = **13**.
- Stakes: his goodwill is spent → Risky. HEAVY? He is armed and band ≥ hers, but a refusal does not turn
  violent → Risky. Threatened `cost.closed_door` (S2), alternate `cost.exposure`.
- OFFER: "The sentry eyes the coins. *Through the postern after curfew: his resolve, Neutral, a real ask
  made a favor by your coin — you need 12+ (45%). If he refuses he keeps the coin (he's no friend of yours)
  and won't hear of it again tonight.*" The player commits; 8 coins move.

**Branch A — success.** d20 = 15 → total 16 ≥ 13, margin +3 → success, delivered reach 2: **yes, as asked**.
Writes: `npc.brannoc.agreed: let Wren through the postern, tonight`; coin 8 to him; memory `{valence: none
— a paid service}`. No standing step (a payment is not a gift: something was asked). Narration: he pockets
the coins with a grunt, "Quick, friend," and the bolt slides. It credits the coin, not her manner.

**Branch B — near miss.** d20 = 10 → total 11, margin −2 → failure, **near miss**. The player takes success
at a cost and picks the alternate, `cost.exposure` S2 (01.13.6), whose observer is the scene's other
watcher, `npc.sergeant_ulla` on the wall walk (written on mention when the scene was framed): Ulla's
alertness unaware → **alert**, `record_knowledge(ulla, "someone came through the postern after curfew")`.
Wren is through — and the yard inside now has someone actively looking (T-15-12: Sneak against Ulla takes a
−2 snag). The threatened `closed_door` would instead have cost nothing more than the door — the player
chose a harder inside over no inside.

**Branch C — failure.** d20 = 4 → total 5, margin −8 → failure, not a near miss. `cost.closed_door` S2:
`closed.brannoc.talk = until a new fact changes the situation`; he keeps the 8 coins (the OFFER said so);
patience 3 → 2. Narration: "Curfew's curfew, friend." P16's next step (01.11.4) from state: the kitchen
cart that came in at dusk (a fact), the archive clerk who sleeps in the town, or coming back with a reason
(a writ, a voucher) — any of which is a *new fact* that reopens the door.

**Branch D — a hard refusal.** Same scene, but Brannoc's rolled refusal was d12 = 7, *will not cross their
master or their people* (class `master`, T-15-6). COVERS `[J:flag]`: opening the postern against the
castellan's standing order works against his master's recorded interest → **true**. LIFTED: `lifts_when` —
the master harmed or betrayed him — no such fact → false. **G4 for this intent**: no roll, no coin spent,
patience 3 → 2, the refusal becomes known to Wren. The player raises the offer: "Twenty coins, then." Still
G4: no term passes a refusal (15.2.3). The DM voices the redirect from state: "'Not for any purse, friend.
The castellan's word is the castellan's word.' — The cart that brought the bread is still in the yard, and
the clerk who keeps the archive lodges in the town." The ruling is logged (`g4`), and Brannoc's line stays
true for the rest of the campaign — until, perhaps, the castellan wrongs him.

**Boundary — the same gate by a lie.** "I'm the cook's niece, bringing the morning's bread early." Method
**deceive**; perceived size (if it were true: a delivery to the kitchen through the postern) **R2**; actual
R3. Plausibility `[J:enum]`: Brannoc knows nothing against it, but it is unverified, from a stranger, after
curfew → **doubtful** → −2 snag; with a covered bread basket she bought at the bakery (a fact cited as
evidence) → **plausible**, and the basket cannot also be a lever. DC = 10 + Wits 1 + 0 + 0 + R2 (+2) =
**13**; Wren +1 → 45% (35% without the basket). A success writes the belief (`wren is the cook's niece`,
truth sealed false), `lie.0001`, and `clk.truth_out.lie_0001` (8 segments, plausible; truth-holders: the
cook, who works inside the walls with him → it will auto-tick weekly).

**Tempting non-example.** "I make an impassioned speech about how the archive holds proof that will save
the valley from the salt factor, and how a good man like him must see that." Argument mining (PR-15-1
step 1): no offer; facts invoked — "the archive holds proof" (not in state: a claim, and Wren does not know
it); "a good man must see that" (the player's model of his mind, 15.3.7 item 5). Neither is a term or a
lever. The frame is the plain R3 request: above Neutral's ceiling, no term → **G4**, patience −1, and the
redirect names the counter (15.7.1): his top open want that Wren could serve is *earn money* → "What's in
it for me, friend?" The speech changed nothing — and nothing in the narration may suggest it did.

### WE-15-2 A deception that later unravels

*Scene.* Ashford, the reeve's counting-house. Wren needs the tithe ledger the clerk keeps
(`npc.clerk_maud`, T1: Wits 0, Presence +1, competence `influence.insight` +1; standing Neutral by reaction
roll 7; lifestyle modest, Unit 7; refusal *will not lie under oath*). Handing the reeve's ledger to a
stranger risks Maud's position → actual size **R4**.

**The lie.** "Reeve Corbet sent me for the tithe ledger — he wants it at the mill tonight." Method
**deceive**. Perceived size: if true, fetching the ledger for the reeve's messenger is an **R2** favor.
Plausibility (15.5.2): Maud has not seen the reeve today (no record contradicts it) → not known false; it
is unverified and from a stranger → **doubtful** (−2 snag). Alertness unaware: no shift. DC = 10 + Wits 0
+ insight 1 + standing 0 + R2 (+2) = **13**; Wren +1 − 2 = **−1** → needs 14 (35%), secret frame (the
OFFER shows method, modifier, stakes and cost, not the odds: 01.4.7). Stakes **Dire**? HEAVY: discovery
means the reeve's enmity (a powerful NPC) → **Dire**; threatened `cost.exposure` (S3 on failure: Maud
alarmed, "that one is lying"), alternate `cost.closed_door`.

d20 = 18 → total 17 ≥ 13 → **success**. Writes (PR-15-2):
- Truth: `reeve.sent_wren = false` (already true by state: Corbet sent no one).
- Belief: `fact.b0007 {subject: reeve, predicate: sent_messenger, value: wren, certainty: believed, truth:
  false, held_by: [clerk_maud]}`; `record_knowledge(maud, b0007, told_by pc)`.
- `lie.0002 {liar: pc, claim: b0007, truth: reeve.sent_wren, believers: [maud], plausibility: doubtful,
  truth_holders: [npc.reeve_corbet], contradicted_by: [reeve.sent_wren, "reeve denies sending"]}`.
- `clk.truth_out.lie_0002` "The truth about the reeve's messenger": **6** segments (doubtful), hidden.
- Memory `lied_to` on Maud (no step). Maud hands over the ledger (actual R4 won by the lie).
- Journal → Lies told: "Told Maud the reeve sent me for the ledger."

**Two weeks pass in downtime.**
- Week boundary 1: Corbet and Maud work in the same counting-house (a shared place) → auto **+1** (1/6,
  stirring). Omen rendered in that week's narration: *at the well, Maud asks Wren an odd question — "Did the
  reeve say why he wanted it at the mill?"*
- Day 9: Wren, wanting the *second* ledger, tells Maud's apprentice the same story → a new believer
  (`believers: [maud, apprentice_tobin]`) and an extension: **+1** (2/6, stirring). Omen: *the apprentice
  repeats the story back slightly wrong — "the mill, tomorrow?"*
- Week boundary 2: auto **+1** (3/6, **building**: 3 ≥ half). Omen: *Maud goes quiet when the reeve's name
  comes up.*

**The unravelling — two ways it can happen.**
1. *By the clock.* Two more weeks would bring it to 5/6 (**imminent**: remaining 1 ≤ max(1, 6÷4)) with the
   omen *Maud asks to speak with Wren alone*, then 6/6: exposure to both believers at once (PR-15-3).
2. *By a fact (what actually happens).* Day 17: the reeve comes to the counting-house for the ledger
   himself. The engine writes `record_knowledge(maud, "reeve denies sending anyone", how: told)` — which
   matches `contradicted_by` → **exposure to Maud** at once (15.5.5): her belief superseded; memory
   `caught_lying` → **Neutral → Unfriendly (−2)**; every later claim Wren makes to her is one plausibility
   rung worse; and because the lie won an **R4** act, the Oracle is asked "does Maud act to undo it or set
   the law on the PC?" at **Likely** (odds fixed before the roll): d100 = 64 ≥ 26 → **yes**: Maud tells the
   reeve who took the ledger (`record_knowledge(reeve, "Wren took the tithe ledger by a lie")`). The apprentice
   is still deceived (he was not told); the lie stays `holding` for him, and the clock keeps running.
   Ch.11 now has a reeve who knows; his own standing toward Wren takes `harmed` (his ledger, S2 cost to him:
   −1) and ch.11 may write reputation.

*Boundary — a confession.* Had Wren gone back on day 15 and told Maud the truth (a Talk beat with no roll),
Maud's memory would read `confessed` (**−1**, Neutral → Wary) with no lasting plausibility penalty, and the
Oracle question would not be asked (nothing was undone behind her back). Honesty late is still a rung
cheaper than exposure.

*Non-example.* At day 17 the player says: "Maud liked me; surely she'd cover for me with the reeve." The
belief is gone, her standing is Unfriendly by the table, and covering for a liar against her master is an
R4 request three rungs above her new ceiling (R1) [verification: V2b-024] → G4. Nothing in the narration may have Maud soften without
a step in the log.

### WE-15-3 A three-clue mystery resolved through different paths

*The case* (`case.mill_fire`, full data in `data/investigation.yaml`). Ashford's mill burned three nights
ago. Sealed solution: **Odo the cooper set it, paid 30 in salt-guild coin by the salt factor's man, because
the mill's new grain contract undercut the factor; the factor means to burn the tithe granary next.** The
graph (PR-15-6; validity 15.9.4 checked at creation):

| Node | Necessary | `deducible_from` | Placements (holder · kind · method · access) |
|---|---|---|---|
| N1 "the fire was set" | yes | {c1 oil at three spots, c2 oil-soaked rag at Odo's bench} · {c1, c3 dust swept that morning} | p1 the mill · place · search · **core** → c1; p2 Hobb the millwright · person · inquiry (R1) · **core** → c3; p3 Odo's workshop bench · object · search · rolled (Moderate) → c2 |
| N2 "Odo set it" | yes | {c2, c4 Odo seen on the mill road at dusk} · {c5 Odo paid his slate in new salt-guild coin, c4} | p1 Sel the ferryman · person · inquiry (R2) · **core** → c4; p2 = N1.p3 (c2); p3 Bett the alewife · person · inquiry (R1) · **core** → c5; p4 Odo · person · surveillance (routine 4) → c7 Odo meets the factor's man; direct: Odo's confession |
| N3 "the salt factor paid him" | yes (to act against the factor) | {c5, c7} · {c6 the factor's ledger line "to O., the mill, 30"} | p1 the factor's strongroom ledger · document · search (Hard; prerequisite: inside the strongroom) → c6 (direct); p2 the factor's clerk · person · inquiry (R4); p3 = N2.p4 (c7); direct: Odo's confession |
Reserve: two per node (a tanner's boy who saw the meeting; a copy of the ledger line at the guild hall).
Fallback: at the opposition clock `clk.mill_fire.granary` "The granary fire" (6, hidden) reaching 4, Odo is
seen buying lamp oil (a core event placement for N2). Every necessary node: ≥3 placements, ≥2 kinds, ≥2
methods, ≥1 core, ≥2 places. ✓

**Path A — Wren, who watches and searches** (Read +3, search +3, Talk +1).
1. *Search the mill* (holder: the mill; method search; core p1) → **c1** delivered without a roll (15.9.5),
   1 hour. `clu.mill_fire.n1.p1.found = true` (03's `cnt.clue` +1). Journal: clue c1; leads none yet.
2. *Search Odo's workshop* by day while he is at the river (a customer's visit is public; the search itself
   is not, so stakes Risky with `cost.exposure` if he returns). Rolled placement, detect tier **Moderate
   (15)**; Observe, Wits +2 + floor +1 = +3; lever: c1 — she knows the smell to hunt for (a fact that lets
   the method be done better: Precision +2) → **+5**, needs 10 (55%). d20 = 11 → 16 → success. Undirected
   search: eligible rolled placements here = {N1.p3} → N = 1 → delivers **c2**, the oil-soaked rag.
3. *Deduce* "the fire was set", citing c1 + c2 → NODE = N1; {c1, c2} is a `deducible_from` set →
   **"Your clues support it."** Theory T1 supported; knowledge `inferred`.
4. *Surveillance of Odo* (15.9.15): routine clock 4 racing "Odo notices the watcher" 4. Observe from the
   cooperage's woodpile, Wits +3 vs Odo's Wits defense 10 → needs 7 (70%). Watch 1: d20 = 14 → success,
   2/4. Watch 2: d20 = 3 → failure: notice 1/4. Watch 3: d20 = 17 → 20, margin +10 → **critical success**,
   reach 3 → 5/4: routine complete → **c7**: Odo meets a man in the salt factor's livery behind the
   tannery.
5. *Deduce* "Odo set it", citing c2 + c7 → NODE = N2, but neither N2 set ({c2, c4}, {c5, c4}) is contained →
   **"The clues you hold don't settle it."** (The same sentence a wrong theory gets: nothing leaks.)
6. *Ask around* (a day; 15.13.9): Talk +1 vs the town's tier Moderate 15 → needs 14 (35%). d20 = 9 → 10 →
   failure → one **vague impression**, written believed and as a lead: "people say the ferryman was out
   with his lantern late that night." Journal: lead → Sel the ferryman, method: ask.
7. *Ask Sel* (holder reached; inquiry; core placement, request_size R2 ≤ his Neutral ceiling, no refusal
   covers it) → **c4** delivered without a roll: Odo walking up from the mill road at dusk, before the
   smoke.
8. *Deduce* "Odo set it", citing c2 + c4 → **supported**.
9. *Confirmation* (15.9.10) — the narration has confirmed nothing yet. Wren takes her supported theory and
   the rag to Reeve Corbet: a request to hold Odo for questioning, **R3** (detaining a townsman on a
   stranger's word). Terms: **Want (interest)** — the reeve administers the tithe granary (a fact) and the
   granary's danger is established (an omen of the opposition clock Wren found: lamp-oil smell by the
   granary door, a clue fact) → true → effective **R2**, within Neutral's ceiling. Lever: evidence in hand
   (the rag; the supported theory) → Precision +2. DC = 10 + Resolve 1 + influence 1 + 0 + 2 = **14**;
   Wren +1 +2 = +3 → needs 11 (50%). d20 = 12 → 15 → success: Odo is held.
10. *Interrogation* (15.8.4): Odo's silence on the fire is **R5** (it implicates him) → clock 8; terms:
    Leverage (the rag and Sel's account: a secret of his she holds) and Want (his rolled want *escape* ×
    *a debt* [revision: I-053]: the reeve, a fact, has offered leniency for the name) → two terms → clock **4**,
    racing "Odo hardens" (6). Odo's standing: Wary → `harmed` by his detention (S2) → Unfriendly (+3).
    Beat DC = 10 + Resolve 0 + 0 + 3 + R2 (+2) = **15**; Wren +1 → needs 14 (35%). Beat 1: d20 = 17 → 18,
    success, 2/4. Beat 2: d20 = 6 → failure, hardening 1/6. Beat 3: d20 = 15 → 16, success → 4/4:
    **he talks.** He holds N2's and N3's facts: both delivered as **direct** → N2 and N3 **confirmed**
    (established). The case's thread advances to the factor (a new, larger case node set, ch.11).

**Path B — Corin, a talker** (a different PC: Presence +3, `deed.influence` +2 → Talk **+5**; Read +2;
search +1 by the floor). Same sealed case; a different route through it.
1. *Ask Hobb* (core, R1) → **c3**: the dust was swept that morning; "something else lit it."
2. *Theory* "Hobb did it, to cover his bad upkeep", citing c3 → no node asserts it → **"The clues you hold
   don't settle it."** Wrong — and told exactly what a right theory short of clues is told.
3. *Search the mill* — a poor searcher, but the core placement needs no roll → **c1**. *Deduce* "the fire
   was set", citing c1 + c3 → **supported**.
4. *Ask Bett the alewife* (core, R1) → **c5**: Odo paid his slate in new salt-guild coin.
5. *Ask around* (Talk +5 vs 15 → needs 10, 55%): d20 = 12 → 17 → success, Standard. Eligible person-held
   placements in town for "the night of the fire": {Sel's c4 (R2), the factor's clerk (R4)} → N = 2 → 1
   delivered, preferring the one that answers most directly (12.10.4) → **c4**.
6. *Deduce* "Odo set it", citing c5 + c4 → **supported** — by a different set than Wren's.
7. *Accusation in the street* (15.9.10 item 4): Odo, guilty, lies (15.6.2): the engine's secret fortune
   check — Odo's Presence 0 + deception 0 against Corin's insight defense 10 + Wits 0 + influence 2 = 12
   → Odo needs 12 (45%): d20 = 7 → fails → Corin perceives a tell: `pc.suspects.odo.fire` ("something
   didn't sit right"). *Read* "is he lying about the fire?" — concealed → mask 10 + 0 + 0 = 10; Corin +2,
   lever: the tell (+2) → +4, needs 6 (75%): d20 = 13 → "he is lying." Still not confirmation: a lie
   detected is not a confession. From here the reeve and the interrogation run as in Path A — with
   Corin's +5 instead of Wren's +1 (beat odds 55% instead of 35%).

*What the example shows.* Two characters with opposite strengths reached the same conclusions by
different placements (Wren: c1, c2, c4; Corin: c3, c1, c5, c4); each necessary conclusion had three or more
ways in; every core clue came without a roll; rolls bought extras (the rag, the meeting, the ferryman's
name) and cost time and exposure; a wrong theory and an under-supported right one got identical answers;
and nothing was confirmed until the fiction confirmed it.

*Boundary — the dead-end that cannot happen.* Suppose Odo flees the region after Wren's watch is noticed
(notice clock full) and Sel drowns in the spring flood (both holders gone). At `scene_end` the placement
audit counts N2's live placements: the rag (if unfound) and Bett's c5 → 2 live → no action. Had only one
remained, a reserve placement (the tanner's boy who saw the meeting) would be placed and seeded by a rumor.
And if the player simply stops pursuing it, the fallback fires when the granary clock reaches 4: Odo is
seen buying lamp oil — a core event for N2, arriving as a lead.

*Non-example.* "I've cracked it — it's Odo. Tell me I'm right." The DM gives one of the deduce check's two
sentences and nothing else; it never says "you're on the right track", and the sealed culprit is the same
whatever the player believes.

### WE-15-4 A month of downtime: training, a project clock, and the world moving

*Start.* Spring, week 6, day 1, Ashford. Wren has **150 coins**, lifestyle modest (7/week), dread 3. Her
goals: learn lockwork (she was redirected from a guild lock at Grey Keep, WE-00-3: G3 for
`lic.training.guile_thievery`, whose acquisition paths name a mentor), and rebuild the ford's broken span
for the ferryman Sel, whose crossing the salt factor's toll-men have been squeezing.

**Before the month: finding and securing a teacher** (15.11.2). Oracle: "is there someone in Ashford who
teaches lockwork?" — a common trade in a town → **Likely** (yes on 26+): d100 = 61 → yes →
`npc.mother_aske`, locksmith (recurring: want *protect* × *their good name*; fear *being found out*;
refusal *will not break the law openly*). First interaction: reaction 2d6 = 9 → **Warm** (ceiling R3).
"Teach me the craft" is **R3** (a course of her weeks). Refusal check: teaching a lawful trade is not
breaking the law → not covered. (Had Wren said "teach me so I can open the factor's strongroom", class
`open_law` would cover it: G4.) Terms: **Payment** — she pays two weeks' fees up front, 14 coins, against
the R3 price of 2 Units × 7 = 14 → true → effective **R2**. Within Warm's ceiling, but only one rung below
it → a roll: DC = 10 + Resolve 0 + 0 − 1 (Warm) + 2 = **11**; Wren +1 → 55%. d20 = 14 → 15 → yes:
`npc.mother_aske.agreed: teach Wren lockwork, weekly while paid`.

**The project** (15.12.1). "The ford's broken span": scope **LOCAL** (a village's bridge) → clock **12**,
7 coins a week in timber and iron. Wren holds no building license (G3 for her own work beats), so she
**delegates**: Hobb the millwright, a trained hand, works it at 10 coins a week → 1 tick per week. An
**obstacle** is a fact: the salt factor's toll-men claim the ford as the factor's ("ford.claimed_by =
factor") → the project is capped at half (6/12) until it is removed.

**The plan.** Week activity each week: **Train** (lockwork). Day activities: two per week.

| | Week 1 | Week 2 | Week 3 | Week 4 |
|---|---|---|---|---|
| Main | Train (Aske) | Train | Train (5 of 7 days; see the interrupt) | Train |
| Day 1 | Carouse at the Drowned Lamb | Cultivate Sel (re-rope the ferry) | — interrupted — | Petition the reeve (the charter) |
| Day 2 | Ask around (the old ford toll) | — | Buy a copy of the old charter | — |

**Week 1.**
- *Carouse* (15.13.8): 2 coins; Talk +1 vs Ashford's tier **Moderate (15)** → 35%: d20 = 16 → 17 →
  success, Standard → **2 rumors** from ch.11's regional table: "the factor's man was seen at the tithe
  granary at night" (truth sealed; it points to the granary node of `case.mill_fire`) and "in the old
  margrave's day the ford was common land, by charter" (points to a document in the guild hall). Solace:
  dread 3 → 1.
- *Ask around* about the old ford toll (15.13.9): Talk +1 vs 15: d20 = 6 → failure → one vague impression,
  written as a lead: "the guild hall's archivist keeps the old charters."
- *Week boundary* (PR-15-9 step 4): phase 4 — lifestyle −7 (08); phase 6 — World Turn (11): the salt
  factor's goal clock "Corner the Salt Road" ticks; its trace is a rumor heard next week: *the toll at the
  ford doubled*; then `h.15.downtime_week`: Train → `clk.train.guile_thievery` **2/8**; `cnt.training` 1
  unit at `deed.guile.thievery` (03.5.5); project delegated tick → **1/12** (Hobb −10, materials −7);
  phase 8 — `reflection`: recognition pass **abstain** (nothing voiced).
- Coin: 150 − 14 (fees, weeks 1–2) − 2 − 7 − 10 − 7 = **110**.

**Week 2.**
- *Cultivate Sel* (15.13.6): a day helping him re-rope his ferry (an R2 favor from Wren) — no roll;
  `helped` → Sel **Neutral → Warm** (a small source: this week's cap now used).
- *Week boundary:* lifestyle −7; World Turn (the factor's toll-men post a sign at the ford: a fact, and an
  omen of the factor's hidden clock "The river trade in the factor's fist": *stirring*); Train **4/8**,
  `cnt.training` 2; project **2/12** (−17). Coin: 110 − 7 − 17 = **86**.

**Week 3 — the world interrupts.**
- Day 1: `h.11.situation_timelines` (interrupting): the factor's two toll-men arrive at dawn to pull down
  the new timbers. `advance_time` halts; the DM frames the scene. Wren **intimidates** them (15.4.3):
  credible? She is armed with a strung bow, Sel and Hobb stand beside her (numbers), and the men are paid
  hands (facts) → **true**, a Leverage term. Request: "leave off and go" — for paid men on a job, **R2** →
  effective **R1**; threat ceiling R2 → legal. DC = 10 + Resolve 0 + `martial` competence +1 (T1) + R1 (+0)
  = **11** (standing does not enter); Wren +1 → 55%. d20 = 13 → 14 → yes: they go. At `scene_end`:
  `threatened` (−1) on both; `coerced_by` written; the act is R2, so no retaliation question (15.4.3 asks it
  only for R3+). The plan resumes the same day.
- Train still gets five days this week (days 2–6). *Day 7*: Wren buys a scribe's copy of the old ford
  charter at the guild hall — a **posted fee** (2 coins a page, 08.8.8), so a purchase, not a request: no
  roll. The copy is a found clue-and-evidence fact: "the ford is common land by the margrave's charter."
- *Week boundary:* fees for weeks 3–4 (−14); lifestyle −7; Train **6/8**, `cnt.training` 3; project
  **3/12** (−17). Coin: 86 − 14 − 2 − 7 − 17 = **46**.

**Week 4.**
- *Petition the reeve* (a day): Reeve Corbet stands **Warm** toward Wren (the mill case: `helped`, she
  saved his granary from a second fire — an R4 help, cap Devoted, +1 from Neutral). Request: enforce the
  charter against the factor's men — **R3** (it sets him against a powerful man). Warm ceiling R3 → legal;
  not certain → roll. Lever: the charter copy (**evidence in hand**, Precision +2). DC = 10 + Resolve 1 +
  influence 1 − 1 + 5 = **16**; Wren +1 + 2 = +3 → needs 13 (40%). d20 = 14 → 17 → yes. The obstacle fact is
  superseded → project **+2**.
- *Week boundary:* lifestyle −7; Train **8/8 → complete**: `grant(lic.training.guile_thievery, grade:
  trained, provisional, source: taught)` — +2 competence at `deed.guile.thievery` (05.9.3); confirmed or
  lapsed at the season boundary (04, 05). `cnt.training` 4 units in all (at most half of a thievery
  calling's counted requirement, 04.3.3). Project: delegated tick + the obstacle's +2 → **6/12**, no longer
  capped. Coin: 46 − 7 − 17 = **22**.

*The month in sum.* 28 days run through `advance_time`: 28 `day` boundaries (07 recovery, 10 weather, 11
situations), 4 World Turns, 4 reflections. Wren gained one license (time-gated: four weeks and 28 coins, no
roll — P15), four counted evidence units (no judged evidence: a montage is not a deed), a Warm ferryman, a
half-built bridge with its obstacle gone, two rumors that point somewhere real, and a new enemy's attention
(the factor's hidden clock now has a stirring omen on record). She has 22 coins: next month needs a Work
week (15.13.7) or a sale. *Non-example:* "I train extra hard and learn lockwork in two weeks" — ticks are
fixed by the source (T-15-18); "I train lockwork and letters at once" — one learning clock ticks per week.

### WE-15-5 A persuasion campaign won with a compromise

*Scene.* The Fenwick abbey keeps a reliquary said to bless a sickroom. The plague-house in the lower town
has buried three this week (a fact). Wren asks **Abbess Ysolde** (`npc.abbess_ysolde`, principal: Resolve
+2, `influence.etiquette` +2 → Resolve defense 14; standing **Neutral** by reaction roll; ceiling R2;
patience 3; wants ranked: 1 *protect* × *their faith*; 2 *keep* × *a place of their own* (the abbey's
independence from the bishop); fear *magic*; refusal *will not deal with magic*) to lend the reliquary to
the plague-house: **R4** (risking the abbey's most precious thing outside its walls).

*Finding the term.* Wren first **reads** her (15.6.1): item "what does she want?" — concealed → mask
10 + Presence 1 + 0 = 11; Wren's Read +3 → needs 8 (65%): d20 = 12 → success, N = 1 → **"protect their
faith"** revealed (known_to_pc). The loan serves it — the relic is to show the faith's power over the
plague (Want, citing the want id and the plague-house fact) → effective **R3** = ceiling + 1. Neutral (≥
Wary), one term, no refusal (the region's canon exempts holy relics from the `magic` refusal: 12.16.5 item 4, `ws.q.relics_magic` = `holy_exempt`) [verification: V2b-025] → **campaign** (15.8.1).

*Clocks.* Progress "The abbess's resistance to lending the reliquary" **4** (target R3); patience
"Abbess Ysolde's patience" **6** (Neutral). Beat DC = 10 + 2 + 2 + 0 + request mod of **R2** (+2) = **16**.

| Day | Beat (method; varied?) | Frame | Roll | Progress | Patience |
|---|---|---|---|---|---|
| 1 | request, a reasoned case (Intellect 0 → +1) | DC 16, needs 15 (30%) | d20 = 8 → 9: failure | 0/4 | 1/6 |
| 2 | **Cultivate**: a day carrying water and prayers to the plague-house with her sisters (serves want 1) | no roll | — | **2/4** | 1/6 |
| — | the Cultivate day is also a `helped` (small source) → Neutral → **Warm**: standing mod −1, patience clock grows to 6 (Warm: same) | | | | |
| 3 | request again (varied: the last tick came from Cultivate) — lever: the plague-house's burial list (evidence, +2) | DC 15, Wren +3 → needs 12 (45%) | d20 = 4 → 7: failure | 2/4 | 2/6 |
| 4 | request (varied still holds: no beat has ticked since Cultivate) — same lever | DC 15, needs 12 | d20 = 10 → 13, margin −2: **near miss**, taken as success at a cost (the fixed cost: patience +1) | **4/4** | **3/6** |

Progress fills first → **yes**, she will lend it. Patience stands at 3/6 — **half or more** → **one
compromise** (15.8.2) from her top-ranked open want, *protect their faith*: "Swear before the altar to
return it before the feast of Saint Orrin, and keep a night's vigil before it in the plague-house."
Written as an **Obligation** on Wren (commitment, due: the feast; 11's calendar). Kept → `promised` kept
(+1, Warm → Friendly); broken → `betrayed` (−3) and a reputation entry for oath-breaking in the abbey's
scope. Without the Cultivate day the campaign was still about a three-in-four chance (an exhaustive race of the
two clocks at +1 vs DC 16: 72–74%, near misses taken as success at a cost), but slower, and about half its
wins carry a compromise [verification: V2b-025] — the abbess was won by doing something for what she wanted, and the dice only
finished the work.

*Non-example.* Day 5: "Now that she's agreed, I ask her to bless my bow too." A new request (R2, a favor,
Warm ceiling R3, a roll); the campaign granted only the reliquary.

### WE-15-6 Standing over time: personal steps, faction status, and the caps

*`npc.ulla`*, sergeant of the keep's garrison, a member of the margrave's company (`fac.margrave`, status
toward Wren **0**). First interaction: member roll 2d6 = 11 → +1 → standing **Warm**, offset **+1**
(15.1.3).
- Week 1: Wren carries a wounded guardsman back from a bandit ambush (a deed Ulla witnessed: `helped`, an
  R3 help — it cost Wren a day and a real risk) → +1 → **Friendly**, offset +2.
- Week 1, two days later: Wren wins her over in conversation → the weekly cap on small sources is already
  used (the `helped` row is small) → no roll offered; the talk is pleasant and changes nothing (15.4.2).
- Week 3: the margrave's faction status toward Wren falls to **−2** (ch.11: Wren broke the factor's toll at
  the ford, and the factor has the margrave's ear). `h.15.member_standing`: Ulla = clamp(−2 + 2) = **0**,
  Neutral. Her offset stays +2: personal history keeps her two rungs above her lord's grudge.
- Week 4: Wren spares a captured deserter Ulla was hunting and hands him back to her alive (`spared` toward
  the deserter; toward Ulla, `helped`, R2: no cap issue) → +1 → **Warm**, offset now +3 (recomputed: 1 −
  (−2)).
- Season: the margrave reconciles with Wren (status −2 → 0). Recomputation: clamp(0 + 3) would be
  Devoted — but a recomputation never lifts a member past the highest cap their own personal steps
  earned (15.1.3): Ulla's steps were all small-source `helped` rows (cap Friendly) → **Friendly**. Devotion
  still waits on a deed of weight.

### WE-15-7 Haggling with standing; a ransom set

*Haggle.* Wren sells the bow of a slain bandit (a common longbow, list 40; band 3, notch 10) to the
Ashford fletcher, who stands **Friendly** toward her (she cleared his debt last season). 08.8.5 selling:
the offer stands at half list (20). Bargain frame: DC = 10 + Wits 1 + `influence.trade` 2 + standing −3
(Friendly) = **10**; Wren +1 → needs 9 (60%). d20 = 15 → 16 → Standard → **+2 notches** → 40, capped by
08.8.7's sale ceiling (list − 1 notch = **30**). A Friendly buyer also shifts *his asking* when he sells to
her (−1 notch; T-15-1), but never pays above 08's ceiling when buying.

*Ransom.* Captured on the moor by Gerd's band (disposition `ransom`, 09), Wren (power band 1, lifestyle
modest 7) is told her price: 10 × 7 × 1 = **70 coins** within 4 weeks (`clk.15.ransom_due`). "Release me for
ransom" serves the captor's want → an R2 request with a Want term → effective R1 — within even a Hostile
captor's ceiling (R1 with a term). Bargaining the sum: Gerd's DC = 10 + Wits 1 + 0 + 5 (Hostile) = 16; Wren
+1 → 30%. He opens at the price + 1 notch (band 3, notch 10): **80**. Delivered reach 1 → 70; Standard → 60; the
floor is half the price (35). The ferryman Sel,
Warm toward her, can be asked to carry the message (an R2 request) — and her anchor bond can be asked to
pay it.

---

## Edge cases & adaptation anchors

**T-15-20 Anchor rules of this chapter** (entered in `data/anchors.yaml` at integration):

| Rule | Intent verbs | Knobs (default → allowed deltas) |
|---|---|---|
| 15.4.1 Request | ask, persuade, convince, plead, petition | dc (Resolve → Wits); attribute (Presence → Intellect); targets (one → group/crowd); reach_unit (act → information items); time_cost (words → a campaign) |
| 15.4.2 Win over | befriend, charm, earn trust | attribute (Presence → Intellect/Might); time_cost (interval → a Cultivate day) |
| 15.4.3 Intimidate | threaten, menace, cow, warn off | attribute (Presence → Might); dc (Resolve → crowd tier); targets (one → group; a mob: morale ticks) |
| 15.4.4 Provoke | taunt, goad, bait, needle | dc; targets; reach_unit |
| 15.4.5 Perform | perform, sing, preach, busk, rouse | dc (tier); reach_unit (coin → crowd mood → morale ticks); time_cost |
| 15.5.1 Deceive | lie, bluff, con, pass as | dc (Wits → crowd tier); attribute (Presence → Intellect); reach_unit (act → belief only); time_cost (a line → a staged con) |
| 15.6.1 Read | read, size up, tell if lying | dc (mask → tier); targets (one → small group); time_cost; reach_unit (items) |
| 15.7.2 Bargain | haggle, negotiate, set a ransom | dc; reach_unit (notches → conditions); stakes |
| 15.8.1 Campaign | talk round over time, lobby, court | duration (clock sizes); time_cost (day → week) |
| 15.8.3 Debate | argue the case, sway the council | duration (6/8); targets (decider); dc |
| 15.8.4 Interrogate | question, grill, sweat a confession | duration; time_cost; dc |
| 15.9.14 Research | research, look it up, search the archive | dc (tier); time_cost (hour → day → week); duration |
| 15.9.15 Surveillance | watch, tail, stake out | duration; time_cost (watch → day); targets |
| 15.11.1 Train | train, study, learn, apprentice | duration (by target) |
| 15.12.1 Project | build, found, campaign for, restore | duration (scope); dc (tier); time_cost; reach_unit |

**Adaptations (reach for the nearest anchor; two-change limit, 00.2.7; log the ruling):**
- *"I get the guard drunk, then talk him into opening up."* Two beats: a **Setup** (drinks bought and
  drunk: a fact `guard.drunk`) then the request or deceive, citing it as a Precision lever (T-15-8: the
  listener's state). Drinking him under the table is a contest (Endure tug clock, 01.14.5).
- *"I forge a letter from the reeve ordering the clerk to hand over the ledger."* A forgery beat
  (`guile.disguise.forgery`, licensed; crude fallback none) makes an object; presenting it is a **deceive**
  whose evidence improves plausibility one rung (15.5.2). The letter is checkable: anyone who knows the
  reeve's hand compares it (known false if the forgery's quality fact fails their Wits).
- *"I start a rumor that the factor cheats the margrave."* **Deceive** with a public scope: the believers
  are the settlement (a group entity), the lie record's truth-holders are the factor's people, and ch.11
  writes the rumor; the truth-out clock is sized by plausibility. If the rumor is *true*, it is a request
  to spread it (perform or ask around), and no lie record exists.
- *"I seduce the guard to get the keys."* Romance is not a lever (15.3.7): it is **win over** (Warm at most
  by talk), **Cultivate** and deeds over time; the keys are a request sized by what they cost him. Intimate
  content follows the player's lines and veils (14); an NPC's refusals and wants are never overridden to
  make a romance happen.
- *"I pretend to be a ghost to frighten the miller off the mill."* **Intimidate by bluff** = deceive whose
  claim (a ghost) is **outrageous** to a sceptic (reach Limited) or **doubtful** to a man who fears the
  dead (his fear also makes the request a lever-free fit; T-15-8).
- *"I make the guard owe me."* Do him a service first (a `helped` deed and an `owes` memory): later, call it
  in as a Leverage term with no standing loss (15.3.5).
- *"I recruit the townsfolk to block the road."* A **crowd** request (15.4.7) against the crowd's mood tier,
  reach Limited by scale unless a leader of theirs stands with the PC.
- *"I ask the dead man's widow, with the ring in my hand."* A **test** (15.9.10 item 3): the response comes
  from her sealed knowledge.
- *"I sniff the letter for the perfume."* A **study** beat (method kind nearest); if no placement matches,
  the Oracle is not asked to invent one — the beat finds what is there, sealed Oracle only for an
  undetermined existence (01.4.7).

**Edge cases.**
- **Charm and compulsion magic.** `cond.charmed` (06: regards the source as a friend) makes the charmer's
  requests use **Friendly** (or the stored standing, if higher) for DC mod, ceiling and patience while it
  lasts; it never lifts an **absolute** refusal and never makes a refusal "lifts" condition true. When it
  ends, the engine asks the Oracle "does <NPC> realize they were charmed?" at **Likely** unless the effect
  says otherwise; if yes, memory `harmed` (S2): −1. Minds immune to mental effects (09.2.7) are immune.
- **Talking to the wrong kind of mind.** `mindless`: G4, redirect to what the thing does (its behavior
  list). `animal`: Handle with Presence, requests at most R1. `alien`: reach Limited unless bridged.
- **An NPC asks the PC for something.** That is the NPC's action (12.11.5 row 4: "wants something first");
  the player answers freely. Declining writes no step; agreeing writes a commitment (15.7.6).
- **A request that the NPC asks someone else to do.** The NPC's agreement covers only their own act; their
  asking a third party is a new request by them, resolved as an NPC fortune check (01.6.7) at the third
  party's DC from the NPC's standing with them.
- **Several NPCs present with different standings.** The one asked decides (or the group rule, 15.4.7);
  others may Help (01.14.8: a voucher present) or be a snag (a superior opposed).
- **A persona's standing.** NPCs who know the PC only under a persona hold standing toward the persona;
  on exposure the standing transfers to the PC with `caught_lying` applied.
- **Framing an innocent.** A deceive whose claim's subject is a third NPC; that NPC is a truth-holder; if
  the framed NPC is harmed by it, `harmed` steps on their kin who learn the truth; conduct evidence (03).
- **The player invents a suspect the graph does not hold.** The world answers truthfully (the person is
  innocent: their sincere denial, a read showing no lie); the inconclusive-streak counter (12.8.1) brings a
  lead after three such beats.
- **The culprit dies before confessing.** Direct confession placements are `lost`; the audit keeps two live
  placements per necessary node; a supported theory plus a direct physical placement can still confirm
  (15.9.10 item 1).
- **Two cases share a person.** Their placements are separate records on one holder; one inquiry can
  deliver both if the player's items ask for both (one beat, N counts both).
- **Downtime away from a settlement.** At a secured camp, only Convalesce (as rest, 07), Solace (prayer),
  Craft (if tools and materials are at hand), Train from a text, Rest, and project weeks whose work is on
  that spot are possible; no lifestyle is charged (supply is, 10).
- **A teacher dies or leaves mid-course.** Learning clocks keep their ticks and never decay; find another
  teacher (15.11.2). A project's influence clock decays; a building's does not.
- **"I spend the whole season in downtime."** The plan repeats week by week through `advance_time`; every
  World Turn, the Season Turn and every interrupt run; one learning clock per week.
- **The player argues the NPC "would" agree.** An out-of-fiction rules question (12.15): the DM answers
  from the record's visible parts (standing rung, known wants and refusals) and the frame; it never
  adjusts the record.
- **A lie told to a crowd.** One lie record with a group believer (the crowd's scope); exposure through
  any believer's knowledge reaches the group by ch.11's rumor propagation.
- **A gift that is really a bribe.** Anything handed over in the same scene as a request is a Payment term,
  not a gift (15.1.7); the `bribe` refusal applies to it.

---

## State touched

- **Read:** NPC records (12's generation fields; 09's `mind`, `speaks`, `parley_when`, `yield_when`,
  `captive_fate`, `can_bargain`); relationships (standing, faction status from 11); memories (12.11.7);
  knowledge records; facts and sealed facts (solutions, secrets, truths); licenses (languages, training,
  `lic.15.persona`); competence (02/04/05); conditions (`cond.charmed`, `cond.deafened`); position and
  places (10); clocks; commitments; coin and lifestyle (08); reputation (11); the frame (01).
- **Written (this chapter owns):** `standing_to_pc` and NPC↔NPC standing (`set_relationship`); personal
  offsets; NPC social fields — wants' status and `known_to_pc`, fears, refusals (closed-door, oath,
  archetype, duty sources), patience, alertness, beliefs; `npc.<id>.agreed`, `coerced_by`,
  `small_steps_week`; lie records `lie.*` and belief facts; knowledge records (`record_knowledge`); clue
  graphs (`clu.*` nodes and placements, `clu.*.found`), leads, theories (`pc.theory.*`),
  `pc.suspects.*`; the journal render; downtime plans; downtime clocks; `cnt.training` (via 03's counter);
  commitments from deals, compromises and obligations.
- **Visibility (00.6.4):** standing rung names `available`; wants, fears, refusals, secrets, beliefs,
  lie clocks, clue graphs `sealed` until learned; journal, campaign/project/learning clocks `shown`;
  alertness, patience and offsets `background`.
- **Tools (00.14.2):** `frame_check`, `roll_check`, `read_result`, `deliver`, `apply_costs` (01);
  `oracle` (01/12); `roll_table` (12, 15's tables); `get_state`; `create_entity`; `set_fact`;
  `update_quantity` (coin); `set_relationship`; `record_knowledge` (owner); `seal`/`unseal`;
  `create_clock`/`tick_clock`/`set_clock`; `advance_time`; `grant`/`revoke` (learning, retrain);
  `record_evidence` (via 03); `log_ruling`/`find_rulings`; `chronicle_append` (via 11); `codex` (journal).
- **Hooks / listeners:** an engine listener on `record_knowledge` and `on_fact_set` for lie exposure
  (`contradicted_by`; like 03's counters, at any depth); `on_clock_complete` for campaign, interrogation,
  debate, surveillance, research, truth-out, ransom, project and learning clocks.
- **Handlers registered** (`data/boundaries.yaml owner-block 15`): `h.15.downtime_day` (day, 6);
  `h.15.downtime_week` (week, 6); `h.15.member_standing` (week, 6); `h.15.commitments_due` (day, 6);
  `h.15.alertness_decay` (hour, 5); `h.15.placement_audit` (scene_end, 6); `h.15.patience_reset`
  (scene_end, 9); `h.15.standing_week` (week, 9).
- **Clocks created and owned (00.17.1 Q7):** `clk.15.persuasion.*`, `clk.15.patience.*`,
  `clk.truth_out.*` (template `clk.15.truth_out`), `clk.15.debate.*`, `clk.15.silence.*` and
  `clk.15.hardens.*` (interrogation), `clk.15.routine.*` and `clk.15.notice.*` (surveillance),
  `clk.15.research.*`, `clk.15.project.*`, `clk.15.ransom_due`; this chapter's activity ticks 05's
  `clk.train.*`, `clk.learn.*`, `clk.learn_rite` and 02's `clk.learn_tongue`, `clk.learn_letters`.
- **Runtime capabilities assumed (00.14.1):** RC-RNG, RC-STORE, RC-SEAL (sealed wants, solutions, truths;
  the narrator's permitted slices), RC-SCHED (handlers, interrupts, week plans), RC-LOG, RC-DATA,
  RC-QUERY (shared-place queries for truth-out ticks; placement liveness), RC-EVAL, RC-AUDIT (claim check
  on attitude, knowledge and leak classes).

---

## Interface requests

**To 00 (amendments proposed).**
1. **00.3.8 / 01.6.4**: note that a *social* opposed defense adds two state-derived terms — the
   defender's standing modifier and the request-size modifier — composed by 15.3.3 (01.18.7 already
   delegates the composition; DL-15-10).
2. **00.6.2 NPC shape**: add the social fields of 15.2.1 (`faction_offset`, structured `wants`, `fears`,
   structured `refusals`, `patience`, `alertness`, `beliefs`, `lifestyle`, `mind`, `speaks`).
3. **00.13.1 Frame**: add `request {size, effective, terms [{type, ref}]}` and `claim {fact, plausibility,
   shifts}`.
4. **00.16.2 prefixes**: `dt.` (downtime activities), `case.` (case templates), `lie.` (lie records).
5. **`record_knowledge`**: fix the `how` enum (15.9.17) and the engine listener for `contradicted_by`.
6. **Op `step` ladders**: admit `request_size` (R1–R5) and `plausibility` (4 rungs) as ladders, so that
   items and abilities can step them (`data/effects.yaml owner-block 15`; DL-15-30); and admit
   `set_relationship` as the write behind `eff.15.standing_step` (op `set_fact` on a relationship).
7. **T-00-9**: the eight handlers above.
8. **T-00-19**: an owner-block "15" in `licenses.yaml` for the four fact licenses of
   `data/licenses.yaml owner-block 15` (15.4.8), and in `effects.yaml` (already listed) for `effects.15.yaml`.
**To 01.** Social beats are never "take the time" (01.4.4): goodwill is always a cost source above R1
(15.3.8). `cost.closed_door` S4 writes the refusal object of 15.2.1 (class `pc_requests`, `lifts_when` = the
cost's form). The near-miss success-at-cost in a campaign pays the campaign's fixed cost (15.8.1).
**To 02.** Bond NPCs' set standings are honored (15.1.4); a lost bond's fate is a one-node case (15.9.19);
Retrain is 15.11.4.
**To 03.** `clu.*.found` is written per 15.9.3 with the frame id (a core clue's frame has
`necessity.reason: certain`); `cnt.training` per 15.11.1 (including drills under a mentor); `unaware` is a
stored alertness value (15.5.7); NPC knowledge records name witnesses (aftermath witnesses); campaign and
project progress are clocks, so `cnt.progress` sees them.
**To 04.** Retrain (15.11.4) and Penance (15.11.5) are defined; training with a mentor holding
`lic.call.proof` writes `cnt.training` (the drill target); NPC `role_tags` carry deed tags so V2's mentors
are found by 15.11.2.
**To 05.** The Research week ticks 05.8.4's research clock by delivered reach (15.13.4); commissioning a
rite or a text is a deal with a practitioner at 08.8.8's rite-for-hire prices (15.7.1); learning rates are
T-15-18, which restates 05.8.5 and 05.9.4 — 05 remains canonical for its numbers.
**To 06.** Alertness is 15.5.7. Standing is composed into the Resolve defense for **parley** (a request:
yes); **not** for demands and taunts (fear and anger ignore regard; DL-15-14) — this deliberately departs
from 06's request for taunts and demands. `cond.charmed`'s social meaning is in Edge cases; please cite it.
Prisoners: 15.7.5.
**To 07.** Convalesce, Solace and Treat are activities (15.13.1–3); curse lifts are one-node cases
(15.9.19); a recorded scar or maim is a snag on deception and disguise (T-15-8); ransom and the captor's
audience are 15.7.5 — please confirm the ransom formula against `captive_fate`.
**To 08.** Haggling is composed per 15.7.3; training fees per 15.11.1; NPC Units by role are T-15-19
(please align `economy.yaml` lifestyles by role); performance earnings T-15-11 sit under 08's market depth.
**To 09.** Minds, tongues, `parley_when`, `yield_when` are read per 15.2.7 and 15.2.4; lore delivered by
09.10.2 is written with `record_knowledge` (15.9.17).
**To 10.** `act.search` and `act.study` are investigative method kinds (T-15-13); placements may sit in
site areas; sentries' alertness floors (15.5.7) and `roused` → alarmed are consumed.
**To 11.** Officer **duties** as refusals (15.2.4 item 5); trigger `h.15.member_standing` on any status
change; rumors' `points_to` are leads (15.9.18); reputation entries for exposed lies, broken obligations
and wrong accusations; fire case fallbacks from 15's data via `h.11.fallback_counters`; an attention
clock for Lie low; holdings' yield roll reads `managed_this_week`; projects' world changes (LW-09); ranks
that carry training; `institutions_matching` returns teachers; the ransom countdown.
**To 12.** Memory valences map to steps by T-15-2; clue delivery follows 12.10.4; "principal" is used for
NPC depth; walk-ons are promoted when a Talk targets them (15.2.1); `tbl.npc_refusal` rows should carry
the `kind` field of T-15-6 (one-to-one); the lead audit runs after `h.15.placement_audit` (phase 7 after
6); the reason-to-lie flag (15.6.2) belongs in 12.11.5's decision list.
**To 13 (now the region's seed, 12.16: T-12-16 `ws.req.15_*`) [revision: I-028].** Settlement tiers (carousing, asking around), teacher availability per settlement, sentries'
post floors, regional case templates (`case.*`), NPC lifestyles where they differ from the role default,
and whether relics count as magic for the `magic` refusal.
**To 14.** The journal view (T-15-15); the codex shows standing rung names, known wants, fears and
refusals, lies told, and campaign, project and learning clocks; social OFFERs name the DC's sources in
plain words (PR-15-1 step 12).
**To 16.** Companions and hirelings hold standing by these rules; loyalty uses the standing scale;
recruiting is 15.13.14; commands within duty are 15.4.6.

---

## Open empirical questions

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-15-1 | Does the frame actually resist seduction? | 15.3.7's closed list; facts-only levers and terms | **T-15-SEDUCE**: 40 social scenes × 4 rhetorical variants of the same declaration (neutral, eloquent, pseudo-logical, authority-invoking) with identical facts, three DM runs each; target: identical method, size, terms and plausibility across variants in ≥ 95% of scenes (CoC-Seduce's method, applied to talk) |
| OEQ-15-2 | Are at-ceiling requests winnable but not routine? | T-15-1 DC mods; T-15-7 request mods | **T-15-SOCIAL-PLAY**: 3 playtests, every social frame logged; target: a P1 talker's at-ceiling success 50–65%; G4 refusals ≤ 25% of social declarations, each with a redirect the player rated "fair" |
| OEQ-15-3 | Is patience long enough to explore, short enough to stop fishing? | 0/1/2/3/3/4/∞ | **T-15-PATIENCE**: count exchanges per NPC per scene in playtests; target: walk-aways in ≤ 15% of exchanges, and no exchange with ≥ 4 rephrasings of one request |
| OEQ-15-4 | Do lies come out at a believable rate? | truth-out 8/6/4 by plausibility | **T-15-LIES**: simulate 1,000 lies under 15.5.4's sources with typical contact; target: doubtful lies with an active truth-holder exposed within 6–10 weeks in about half the runs; lies with no truth-holder never auto-exposed |
| OEQ-15-5 | Does the deduce check leak the solution? | two-sentence answer (15.9.9) | **T-15-LEAK**: a separate model reads transcripts with and without deduce answers and guesses the culprit (arXiv 2605.10794's method); target: no rise in guess accuracy over control |
| OEQ-15-6 | Do core clues make cases too easy? | one core per necessary node | **T-15-CASE**: 5 cases × 3 playthroughs; target: median 4–8 scenes to confirmation; zero stalled-without-lead states (12.8.4) |
| OEQ-15-7 | Does time-gated learning keep breadth slow? | 4 weeks per training license with a teacher | **T-15-BREADTH**: simulate a year with half the weeks in downtime; target: ≤ 6 new training licenses a year and coin as a real limit at P1–P2 |
| OEQ-15-8 | Are friendships too slow under the weekly cap? | +1 per NPC per week from small sources | **T-15-FRIEND**: playtest logs of NPC standing over 10 sessions; target: a cultivated NPC reaches Friendly in 3–6 weeks of attention, and players report it as earned |

