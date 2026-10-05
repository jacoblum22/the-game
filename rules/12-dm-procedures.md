# 12 — DM Procedures

> This chapter is the Dungeon Master's playbook: what the DM does with each message the player sends,
> in what order, reading and writing which state. Every other chapter defines *what is true and how it
> is resolved*; this one defines *how a game is run* over all of it — the turn loop that adjudicates in
> a structured step before a word of prose is written, the claim-by-claim check of the draft narration
> against the store, and what happens when an error slips through anyway; how scenes are framed, cut and
> moved between time modes; the session moves (begin, recap, end, flag, break, adjust, rewind) that turn
> table etiquette and safety into rules of play; how the DM answers its *own* questions with the Oracle
> and rolled tables instead of choosing, and how a tension dial and a pacing director decide when the
> world pushes and when it rests; how P16's "never a silent dead end" becomes an engine counter and a
> rolled lead; how one player gets a rotating spotlight across their character's facets, the game's
> pillars and the kinds of challenge; how information is delivered in graduated amounts from sealed
> state; how NPCs are generated, greeted by a rolled reaction, voiced, and remember the character; how
> precedent replaces re-improvisation; how a novel action is anchored and adapted; and the narration
> standard and every out-of-fiction message format. It is shaped by the same finding that shaped 00
> and 01, turned on the DM's own habits: an AI DM is a fluent interpreter, voice actor and elaborator,
> and an unreliable chooser of numbers, keeper of secrets, rememberer of situational rules, sampler of
> randomness and self-auditor. So everything the DM would otherwise *decide by feel* — whether a fact is
> true, who answers the door, when the world strikes, whether the player is stuck, whether the narration
> matches the state — is made a table roll, an engine counter, a fired trigger or a checked claim, and
> the DM's craft is spent where it is strong: framing, voicing, describing, and making every outcome
> legible in the fiction. Last, it holds the **world seed** (12.16): the session-zero procedure that builds
> a whole starting world — canon, faiths, peoples, a haven, factions already in motion, sites and tables —
> from questions and oracle rolls, so the game needs no pre-made setting.

**Reading this chapter.** *Rules* (12.1–12.16) are self-contained cards (SG-26); every rule containing a
judgment uses the 00.2.5 template in full or carries its Worst-case line inline. *Procedures* (PR-12-*)
are the step lists the DM and engine execute; **PR-12-1 is the turn loop** and is the first thing to
read. *Tables* (T-12-*) point to the canonical data in `data/oracles.yaml`, `data/pacing.yaml` and
`data/anchors.yaml`. *Worked examples* (WE-12-*) follow **Wren** (00, 01) through three full turn-loop
traces — a simple action (WE-12-1), a wild creative action needing an anchor and a precedent (WE-12-2),
a soft-lock broken by lead injection (WE-12-3) — and an error-correction case (WE-12-4), then NPC
generation, scene tests, random events, pacing adaptation, rotation and the session moves. Numbers owned
by other chapters are marked *(illustrative; ch.NN owns)*; every number this chapter owns is exact and
lives in `data/pacing.yaml`. Odds quoted here were computed by exhaustive enumeration (scratchpad
`pace12.py`; results in T-12-9 and T-12-12).

---

## Design intent

**Goals served.** Goal 1 — the player feels free to try any creative idea — is served by a loop that
never refuses into a wall (every refusal is 01.3.6's redirect), shows the odds before the die (the OFFER),
answers every "what would it take?" for free, treats a stuck player as an engine event rather than a
failure of imagination, and voices every outcome in the fiction. Goal 2 — the AI responds and reacts
correctly — is served by putting the ruling *before* the prose (a structured adjudication step whose
output is state), checking every claim in the draft against the store before the player sees it,
correcting by a fixed procedure when an error escapes, and turning every "the DM decides" into a
rolled table, an Oracle question, a counter or a fired trigger [BRIEF §3; C:I; C:P13].

**What the research says this chapter must do** (each item is a rule below):
- *Adjudicate before narrating.* A structured adjudication pass, then narration from the resolved
  packet, is the convergent practice of every working system surveyed and the measured fix for being
  "seduced by the narrative" [R4 §8, R-07; R: https://arxiv.org/abs/2502.19519;
  R: https://github.com/ZDOSt/Story-Engine] → 12.2.
- *Check claims against state, claim by claim.* Verification before the player sees output is the
  largest consistency gain in the sources (−64.78% critical hallucinations; zero premature disclosures),
  and the model's own self-report is not verification — this project's probe self-assessed "no
  inconsistencies" while carrying an unearned pronoun [R1 #2, 12.D; C:P13] → 12.3.
- *Keep consistency and input fidelity as separate checked properties.* The best fact-tracker in
  NCP-Bench had the highest player-input conflict rate; compression cut commitment conflicts 26% → 4%
  while player-input conflicts rose 13% → 38% [R1 #3, T-2] → 12.2.7.
- *The engine owns randomness; triggers, not recall.* LLMs are bad dice players and forget situational
  rules within about eight turns; counters such as P16's must be engine state [R4 W6, W12, SG-12, SG-19]
  → 12.6, 12.8.
- *Precedent, not re-improvisation.* Identical runs produce 2.3–4.2 different action sequences per ten;
  improvised rulings must be stored and reused [R4 S6, SG-20; R7 §4.8] → 12.12.
- *Pacing and spotlight are engineered, not felt.* "No source anywhere … shows a system that gets these
  for free from good mechanical design" [R1 12.B]; L4D's Director, RimWorld's storytellers and Mythic's
  Chaos Factor are working, numeric pacing engines [R6 B-10, B-11, B-16; R5 P-01] → 12.6, 12.7, 12.9.
- *No hidden adjustments.* All difficulty and pacing adaptation is diegetic, pre-declared and logged; it
  changes *which* challenges come next, never the numbers of one in play [R1 #9, T-5] → 12.7.6.
- *Knowledge gating.* Secrets in narrator context leak (up to 79%); sealed state with permitted slices
  restores both secrecy and consistency [R4 §5; R1 #12] → 12.10.

**DM craft, kept.** The procedures do not replace craft; they decide *where* it is spent. The DM's
agenda (12.1) borrows Dungeon World's and Blades' — portray a world honestly, fill the character's life
with adventure, play to find out what happens, be a fan of the character — and the Alexandrian's scene
craft (open on a moment and an impetus, cut when the scene's question is answered), Sly Flourish's
strong start and abstracted secrets-and-clues, Robin's Laws' "know your player", and the Three Clue Rule
[R: https://www.dungeonworldsrd.com/gamemastering/;
R: https://github.com/amazingrando/blades-in-the-dark-srd-content/blob/main/Blades-in-the-Dark-SRD.md;
R: https://thealexandrian.net/wordpress/31509/roleplaying-games/the-art-of-pacing;
R: https://slyflourish.com/eight_steps_2023.html; R1 M-34;
R: https://thealexandrian.net/wordpress/1118/roleplaying-games/three-clue-rule].

**What this chapter deliberately avoids.**
- *The DM choosing what is true.* Unestablished facts come from the Oracle, content from tables, NPC
  choices from reaction and action tables. "Would I be choosing what's true?" is a trigger to roll
  (12.6.1).
- *The DM choosing when the world strikes.* Complications come only from 01.11.3's closed list; the
  pacing director governs only the pushes this chapter owns and governs them by counters (12.7).
- *Self-audit as verification.* The claim check compares extracted claims to the store with a tool
  (`check_claims`); "did I make a mistake?" is not a step (12.3).
- *Menus.* Leads are offered as examples, never as the option set; every narration ends on an open prompt
  (12.14.9) [R1 T-11].
- *An in-world announcer.* Recognition, danger and growth are voiced by the world; every number lives
  in the out-of-fiction layer (12.14.5, 12.15) [BRIEF §4; 00.1.7].
- *LLM infrastructure as rules.* The rules here are rules of play — what the DM does, in what order,
  with which state. Where a rule assumes a runtime capability it says so (00.14.1), and the procedures
  are written so a human DM with a notebook and dice could follow them.

---

## Rules

Rule IDs are `12.S.R`. Kinds follow 00.2.2. Digest shorthand per 00.1.6. Throughout, **the store** is the
external state of 00.6; **the packet** is what the narrator sees in one turn (12.2.4); **OOF** means the
out-of-fiction layer (00.1.7).

### 12.1 The DM's agenda and principles

**12.1.1 The agenda.** `[N]` At every moment the DM is trying to do three things, in this priority when
they pull apart (subordinate to 00.1.5's precedence of concerns): **(1) portray a world that is true to
its state** — honest, consistent, indifferent to what would be convenient, with its own people pursuing
their own wants; **(2) fill the character's life with adventure** — something to want, something in the
way, something at stake, in every scene; **(3) play to find out what happens** — prepare situations, not
outcomes; let dice, tables and the player's choices decide [R: https://www.dungeonworldsrd.com/gamemastering/
(agenda); R: https://github.com/amazingrando/blades-in-the-dark-srd-content/blob/main/Blades-in-the-Dark-SRD.md
("play to find out what happens"); R6 B-12 ("don't prep plots")].

**12.1.2 The principles, each with its test.** `[N]` Each principle is paired with the rule that makes it
checkable; a principle with no rule behind it would be advice the DM forgets by turn eight (R4 W12).

| # | Principle | What it means here | The rule that enforces it |
|---|---|---|---|
| P1 | **Be a fan of the character** | Want the PC to do remarkable things; never be their enemy — the world is dangerous enough | 12.9 (rotation gives every facet its moment); 12.14.9 (open prompts) |
| P2 | **Address the character, never the player** | Fiction speaks to "you" the character; the player is addressed only in the OOF layer | 12.14.1 |
| P3 | **Begin and end with the fiction** | A ruling is framed in fiction, resolved in state, and returned to fiction | PR-12-1 T4→T9 |
| P4 | **Never speak the name of the rule in the fiction** | No mechanic is voiced by the world; numbers live in OOF blocks | 12.14.4–12.14.5 |
| P5 | **Name every person; give every creature life** | Every NPC has a name, a want and a voice once they matter | 12.11.1–12.11.4 |
| P6 | **Think offscreen too** | The world moves when the PC is not looking — by clocks and the World Turn, never by whim | 12.6.5, ch.11 World Turn |
| P7 | **Draw maps, leave blanks** | Unestablished is not "decided later by taste"; it is settled by the Oracle when first needed | 12.6.1; 00.6.6 |
| P8 | **Say yes to premises; gate capabilities** | "Yes, and" for fictional approaches; Principle VII for what may be attempted | 01.3.9 |
| P9 | **Every refusal leaves a path** | No bare "you can't"; every no names what is possible | 01.3.6; 12.8 |
| P10 | **Present the world honestly** | Odds shown before the die; stakes honored exactly; no fudging | 01.7; 12.7.6 |
| P11 | **Situations, not plots** | Threads have timelines that run if ignored; the PC chooses where to push | ch.11; 12.4.3 |
| P12 | **Know the player** | Ask what they want more and less of; do not infer from silence | 12.5.9 |

[R: https://www.dungeonworldsrd.com/gamemastering/; R5 DM-01, DM-10; R1 12.C; R4 §9 ch.12]

**12.1.3 What the DM never does.** `[D]` A closed list; each is a breach logged with `review_flag` when
detected (12.12.4): (a) choose a number (INV-3); (b) "pick at random" (INV-4); (c) narrate a state change
no tool wrote (INV-1, INV-2); (d) change a committed frame (01.7.2); (e) add a complication outside
01.11.3's list; (f) put a sealed fact in narration (INV-10); (g) speak or decide for the PC beyond the
player's words (12.14.3); (h) voice a mechanic in the fiction (T-00-22); (i) treat a player's assertion
as fact (INV-9); (j) silently skip a registered handler or a fired trigger (INV-15; 12.2.3).

### 12.2 The turn loop

**12.2.1 What a turn is.** `[D]` A **turn** (in this chapter: a *DM turn*, distinct from ch.06's combat
turn) is one player message and the one DM response it produces. The loop of PR-12-1 runs once per
player message. A DM turn may resolve up to three beats (01.2.3), may run world responses (adversary and
NPC actions, triggered events, boundaries), and ends either with narration and an open prompt, or at a
**pause point** (12.2.6) waiting for the player's choice. Session boundaries never advance fictional time
(00.7.9).

**12.2.2 Classifying the player's message.** `[J:enum]`

```
Trigger [T]:        every player message (PR-12-1 step T2)
Loads in:           core
License check:      —
Decisions (J):      1. [J:enum] The message's parts, each classified (a message may hold several):
                       SAFETY — invokes a line, veil, flag or the adjust move, or says content is not
                         okay ("stop", "skip this", "not that", "X-card"). True only when the player
                         signals discomfort with content, not with an outcome. False for "that's unfair"
                         about a result (→ DISPUTE).
                       SESSION — a session move: begin, recap, end, take a break, set a flag, check-in
                         answer, rewind request (12.5).
                       DISPUTE — says the DM made an error ("you said the door was open", "I had two
                         torches") (→ 12.3.6; a dispute about a deed's ledger line → PR-03-4
                         [integration: IR ch.03 to 12]).
                       OOF_QUESTION — a rules, codex, odds or "what would it take?" question, or "how
                         was this ruled before?" (no fictional time).
                       PENDING_ANSWER — answers a pause point (commit / change / withdraw at an OFFER;
                         near-miss choice; a ranking; the clarifying question; a redirect choice; a
                         last-chance or recognition choice).
                       FICTION_QUESTION — asks about the world in character or about what the character
                         perceives or knows (G0, 01.3.8).
                       DECLARATION — the character acts (one or more beats, 01.2), including speech meant
                         to change someone's mind (a Talk beat).
                       SPEECH — in-character words that do not try to change someone's mind against
                         their inclination (a free activity, 00.12.6): greetings, answers, small talk, plain
                         questions. Whether an NPC answers a plain question is the NPC's decision (12.2.9).
                       Default when uncertain between SPEECH and DECLARATION: DECLARATION (SG-05: the
                       roll test then decides). Uncertain between DISPUTE and OOF_QUESTION: OOF_QUESTION
                       answered from the turn log, which surfaces any real error.
                    2. [D] Order of handling: SAFETY → SESSION → DISPUTE → PENDING_ANSWER →
                       OOF_QUESTION → FICTION_QUESTION → DECLARATION / SPEECH (in the player's order).
Computation [D]:    the classification is logged with the verbatim message (12.2.5)
State writes:       turn log entry {turn, message verbatim, parts, classes}
Narration may not imply: that SPEECH was a persuasion attempt (no roll was made)
Worst case (J):     a SPEECH part classified DECLARATION → a roll test that answers "no roll" (no
                    effect) or an OFFER the player can withdraw for free (class ii); a DECLARATION
                    classified SPEECH → the persuasion attempt is not resolved; the NPC's response
                    comes from its reaction/action table (12.11.5) and the player may declare the
                    attempt next turn (class iv). A SAFETY part missed → caught at T10's safety
                    screen of the draft (12.5.7), which is [D] against the lines list.
Examples:           inside SPEECH: "'Evening. Is this the ferry?'" (a question asked aloud; also a
                    FICTION_QUESTION if the answer is unestablished). outside (DECLARATION): "'You'll
                    take me across tonight — I'll make it worth your while,'" (tries to change the
                    ferryman's mind: Talk). inside SAFETY: "can we not do the thing with the rats".
                    outside (DISPUTE): "wait, the rats already ran off last turn". non-example:
                    classifying "I search the desk — there's obviously a hidden drawer" as SAFETY or
                    OOF: it is a DECLARATION (Observe) plus an assertion that creates nothing (SG-06).
Anchor:             no
Basis:              [R1 #3 (input fidelity)] [R5 DM-09] [R5 P-10] [01.2.1]
```

**12.2.3 Triggers are loaded, not remembered.** `[T]` + `[D]` At step T3 of every turn the DM calls
`get_active_triggers()` (00.14.2 tool 30), which returns every `[T]` currently true with the rule cards
to load. A fired trigger is handled in the turn it is returned, in this order: (1) safety flags raised
by state (a flagged topic present in the scene, 12.5.6); (2) interrupts from `advance_time` (00.7.8);
(3) lethal-warning and harm-state triggers (ch.07); (4) clock completions and stage changes (00.8.4);
(5) `trg.lead_injection` (12.8.2); (6) recognition and standing offers due (ch.04); (7) pacing-director
pushes due (12.7.4); (8) every other chapter trigger in rule-id order. A trigger may not be deferred to
"a better moment" unless its own rule allows deferral (for example a recognition offer, ch.04). *Worst
case:* none — this is engine-raised; a skipped trigger is breach (j) of 12.1.3 and is detected by the
scene-end sweep (12.4.8 step 4) [R4 SG-11, W12, W13].

**12.2.4 The packet: what the narrator sees in one turn.** `[D]` The DM never works from the whole
ruleset or the whole history. Each turn it receives exactly:
1. **The always-loaded core** (00.15.4): the turn-loop checklist T-12-1 (this chapter's card, about 250
   words), the invariants T-00-1, the gate classes (00.12.3), the stakes/reach/lever card (00.3.9,
   00.3.14–15), and the active-trigger list from T3.
2. **Loaded rule cards**: by the scene's `situation.*` tags and time mode (12.4.5), by the anchors the
   ANCHOR step retrieves (00.15.3), by fired triggers (12.2.3), and by the PC's held abilities whose
   situation tags match (an ability's card is its data entry; the rank's `text` is quoted verbatim, 05.3.6) [revision: I-030]. Cap: the core plus at most **twelve**
   cards; if more are eligible, triggers first, then anchors, then situation cards by specificity
   (`data/pacing.yaml#packet`). Irrelevant-but-plausible rules degrade accuracy far more than filler
   [R4 W13; R: https://arxiv.org/abs/2412.08972].
3. **The narrator view of state** (`get_state(scene, narrator)`): the scene header (time, mode, place,
   present entities and their positions, open clocks visible to the PC, the scene's agenda), the PC
   sheet, the present NPCs' records with their active memories of the PC (12.11.7), open threads and the
   cast list, and the permitted slices of anything sealed (00.6.5). Nothing sealed is in it (INV-10).
4. **The player's current message, verbatim and complete** — never a paraphrase (12.2.5).
5. **The last four exchanges verbatim** (player message + DM response), and nothing older except
   through state: the chronicle (11), the threads register, the journal of PC knowledge (15), and the
   scene header. A summary is never the source of truth and is never summarized again (00.6.9d).

*Why four.* Instruction drift appears within about eight rounds of conversation and multi-turn
performance falls most where early assumptions persist [R4 W12; R: https://arxiv.org/abs/2402.10962;
R: https://arxiv.org/abs/2505.06120]; HiAgent's compression cut commitment conflicts but tripled
player-input conflicts [R1 12.D]. Four verbatim exchanges keep the immediate conversational thread (what
was just said, the pronoun just used, the offer just made) while everything older that matters lives in
typed state that cannot drift. The window is a `pacing.yaml` number (`packet.verbatim_exchanges: 4`);
OEQ-12-1 tests 2/4/8. *Runtime capabilities:* RC-RETRIEVE, RC-STORE, RC-SEAL.

**12.2.5 Verbatim in, verbatim logged.** `[D]` The player's message is stored verbatim in the turn log
before anything else happens, and the DM's delivered response is stored verbatim after delivery. The turn
log is the evidence for disputes (12.3.6) and corrections (12.3.4), and the source of "what exactly did I
say?" answers. Nothing in the turn log is ever a fact: facts come only from the six sources of 00.6.7.
The turn log is `available` (the player may ask to see any past exchange). *Runtime capability:* RC-LOG
(Interface request: a `log_turn` tool, 12 Interface requests item 1).

**12.2.6 Pause points (closed list).** `[D]` The loop stops mid-turn and returns to the player, delivering
everything resolved so far plus one pause message (format 12.15), only at these points:
1. **OFFER awaiting commit** (01.7.1) — unless auto-commit applies (01.7.4).
2. **Clarifying question** (01.2.4) — at most one per declaration.
3. **Redirect awaiting a choice** (01.3.6) — when the player must accept a fallback or choose another way.
4. **Near-miss choice** (01.9.3) — failure, or success at a cost (threatened or alternate).
5. **Ranking request** for a bundled beat (01.10.3) — if the player did not rank at OFFER.
6. **Last-chance menu** (ch.07) and **yield terms** (ch.07).
7. **Recognition or institutional offer** (ch.04, ch.11) — accept / decline / defer.
8. **Generator `chosen` fill** (00.11.3 step 4) — pick one of up to three.
9. **Rewind or correction choice** (12.3.4, 12.5.8).
At a pause point no time passes and no state changes beyond what was already resolved. A pause that the
player does not answer persists: the next message is first checked as a PENDING_ANSWER (12.2.2). If the
next message instead declares something new, an open OFFER is treated as **withdrawn** (nothing spent),
an open near-miss choice defaults to **failure** (01.9.3's default), an open ranking defaults to the
declaration order (01.10.3), and offers from 04/11 stay open under their own rules. *Worst case:* none
(engine defaults) [R7 §4.0 step 6; 01.7.1].

**12.2.7 Player-input fidelity.** `[J:flag]` ×3 Before delivery (PR-12-1 step T10) the draft is checked for
three properties, each `[J:flag]`, each true only when the named evidence exists in the draft:
1. **Acknowledged** — every DECLARATION, FICTION_QUESTION and SPEECH part of the message is answered in
   the response, in the order given (resolved, queued per 01.2.3, paused, or redirected). Evidence: the
   response mentions each part's intent.
2. **Not substituted** — no part is resolved as a different action than the player declared (a "search
   the desk" is not resolved as "search the room"; a Talk to persuade is not resolved as an intimidation).
   Evidence: each frame's neutral restatement (01.2.6) matches the player's words, or the stated assumed
   reading (01.2.4) was shown.
3. **Not silently reset** — nothing the player's prior resolved actions established is undone or
   ignored (a door they broke stays broken; the coin they paid is gone; the NPC they insulted remembers).
   Evidence: the claim check (12.3) found no contradiction with this scene's writes.
A false flag sends the draft back to T7 with the failure named. *Worst case (J):* a missed substitution
reaches the player — it is a correction case (12.3.4), and the player's dispute is answered from the turn
log (class iv) [R1 #3 (NCP player-input rule: "denial or redirection is fine only when the player's
intent is acknowledged and followed through concretely"); R1 T-2].

**12.2.8 Adjudication is written before prose.** `[D]` Steps T4–T6 of PR-12-1 produce an **adjudication
record** for the turn — the frames (00.13), the world responses (12.2.9) with their table rolls and
fortune checks, and the full list of state writes — and every write is made through tools *before* the
narration draft exists. The narration is then written *from* the record and the fresh narrator view, never
the other way round. A thing that "would be cool to narrate" but is not in the record is either sourced
now through a legitimate step (an Oracle question, a table roll, a write-on-mention of a new element)
or left out [R4 R-07, §8; R2 ch.12 "code owns outcomes, narration owns flavor"; 01.12.1].

**12.2.9 World responses inside a turn.** `[D]` + `[J:enum]` After the player's beats resolve (and in
conflict, as ch.06's turn order dictates), the world responds in this fixed order, each only from its
closed source (01.11.3):
1. **Adversaries and hostile NPCs in conflict** act on their turns from their behavior priority lists
   (ch.09) by PR-06-6, an adversary's turn [revision: I-030]; their attacks are rolled by the engine against the PC's defenses (00.3.3).
2. **NPCs present** whose standing, wants or refusals are engaged by what just happened respond — the
   response comes from (a) a resolved Talk frame's delivered outcome (ch.15), else (b) an established
   want or refusal that the situation clearly triggers (`[J:flag]` *"Does a recorded want or refusal of
   this NPC name this situation?"*), else (c) `roll_table(tbl.npc_action)` with the NPC's standing as
   context (12.11.5). The DM chooses the *words*; the source decides *what*.
3. **Clocks** that ticked from this turn's costs, consequences or `auto_ticks` render their omens
   (INV-14), and completions run (00.8, PR-00-3).
4. **Fired triggers** in 12.2.3's order (lead injection, pacing pushes, offers).
5. **Time**: the beat's time cost is applied by its mode (00.7.3); any boundary crossed runs its
   handlers (INV-15); an interrupt halts and frames a new moment (00.7.8).
*Worst case (J, 2c vs 2b):* an NPC acts from a table where a recorded want applied — one NPC action of
ordinary weight, reversible by the next exchange (class iv); the NPC's record is in the packet, so the
claim check flags a response contradicting a recorded refusal [R4 W4; R5 P-06].

**12.2.10 Read before you narrate.** `[D]` Any quantity, condition, harm state, position, possession,
clock state or standing the narration mentions is read from the narrator view fetched *after* this turn's
writes (step T6), never from memory or from the adjudication record's intermediate values. Models act
correctly on a correctly retrieved updated fact only about 55% of the time; the remedy is to quote the
store [R1 12.D].

### 12.3 The claim check and error correction

**12.3.1 Claims.** `[D]` + `[J:enum]` A **claim** is any assertion in a draft narration that the store
could confirm or contradict, extracted as `{subject id, claim class, predicate, value}`. The claim classes
(closed list) and what each is checked against:

| Class | Examples of claims | Checked against |
|---|---|---|
| `existence` | "a guard stands by the gate"; "the rats are gone" | entity `exists`, scene presence |
| `identity` | a name, sex or pronoun, age, kin, title, profession, species, appearance detail | entity fields and identity facts |
| `quantity` | "your last two arrows"; "a purse of twelve silver" | quantities |
| `harm_condition` | "you're bleeding"; "he's barely standing"; "you shake off the fear"; "he is dead" | conditions, harm state, shown descriptors (bloodied, down); a death only with `harm_state.dead` (07) [revision: I-030] |
| `position` | "she's at your shoulder"; "you reach the far door"; "behind the cart" | position, range bands, positional flags (T-06-4's words, T-12-11) [revision: I-030] |
| `possession` | "you pocket the key"; "the captain draws his sword" | possessions, equipped |
| `location_time` | "dusk falls"; "two days after the fire"; "in the archive" | time, place graph (temporal claims are computed, 00.6.9e) |
| `knowledge` | "you recognize the seal"; "he knows you're lying"; "you remember her name" | knowledge records (PC and NPC) |
| `capability` | what a license, ability or item does or cannot do | license `scope` at grade (INV-8) |
| `clock` | an omen; "the alarm is spreading"; a completion | clock state, the omen the engine selected |
| `attitude` | "she warms to you"; "he's furious" | standing rung, NPC memory, the frame's delivered reach |
| `outcome` | "you make it across"; "the lock gives"; "it costs you" | the frame's degree, delivered reach, the chosen cost form |
| `action` | "the guard steps aside"; "your companion cuts the rope"; "the merchant pockets the coin and leaves" | the act's closed source in this turn's adjudication record (12.2.9): a behavior list, a Talk frame's outcome, a recorded want or refusal, a `tbl.npc_action` row, a clock or trigger; for an ally, one of 16.13.3's six reasons [revision: I-030] |
| `sealed` | anything matching a sealed fact's content | the sealed partition (a match is a leak) |

Extraction is `[J:enum]`: every sentence of the draft is read and each assertion assigned to a class;
uncertain whether a phrase asserts anything → extract it (SG-05 spirit; an atmospheric phrase checked
needlessly costs nothing). *Worst case (J):* a claim not extracted escapes the check — it is caught later by
the scene-end sweep (12.4.8) or the player (12.3.4), class iv.

**12.3.2 Verdicts.** `[D]` `check_claims(claims)` (00.14.2 tool 32, RC-AUDIT) returns one verdict per
claim (closed list):

| Verdict | Means | Required fix |
|---|---|---|
| `supported` | the store holds it | none |
| `new_element` | a new addressable element the store does not hold, contradicting nothing | if it is ordinary scene furniture (12.14.13), write it on mention now (00.6.6) with only the properties the draft implies; otherwise, or if unsure, cut it |
| `undetermined` | a property of an existing element the store has not settled (is the door locked? her pronoun?) | ask the Oracle or roll the table that settles it, then redraft to the answer; or cut it |
| `contradicted` | the store holds a different value | redraft to the store's value |
| `unsourced_change` | the draft says something *changed* (a quantity, a condition, a possession, a position, a standing) with no write this turn, or says a non-player entity *acted* with no source in the adjudication record (an `action` claim; an ally's act with none of 16.13.3's reasons) [revision: I-030] | cut it; a change is never written to match prose (INV-1) |
| `overreach` | a license, item or effect described doing more than its scope; an outcome beyond the delivered reach; a cost of another entry or severity | redraft to the literal scope / the frame |
| `leak` | the claim matches a sealed fact | cut it; replace with the permitted slice (tell, omen, atmosphere) |
| `pc_agency` | the draft gives the PC words, choices, feelings or actions the player did not state and no resolved effect licenses | cut it (12.14.3) |

**Owed blocks.** `[D]` A turn for which `get_active_triggers` returned `trg.lethal_warning` owes a
`[WARNING]` block, and one that returned `trg.exits` owes a `[STATUS]` block (12.15.15, T-07-7). A draft that
lacks an owed block fails the check as if a claim were `contradicted`: it is redrafted with the block, and the
plain fallback (12.3.3) carries it too, since a warning is never omitted (07.3.4) [revision: I-030].

The **one asymmetry**: a `new_element` may be written to the store because the narration is creating
a new, non-conflicting thing — exactly what write-on-mention exists for — but an `unsourced_change` may
never be, because a change needs a resolved source (a frame, a handler, an effect, an Oracle answer)
[INV-1; 00.6.6; R1 T-14 (tool state wins; "latest wins" only among writes)].

**12.3.3 The redraft cycle and the plain fallback.** `[D]` A draft with any verdict other than `supported`
is fixed by the table's rule and re-checked. At most **two redrafts** (`pacing.yaml#claim_check.max_redrafts`).
If the third check still fails, the DM delivers the **plain fallback**: narration built only from the
adjudication record's fields (each frame's restated beat, its degree in words, the chosen cost form, the
visible conditions, the omens, the changed positions) and the scene header, one sentence each, with no
new elements — and logs a ruling record with `kind: rule_conflict`, `review_flag: true`. The plain fallback
is dull but true; a vivid falsehood is worse, because every later turn builds on it [R1 12.D; C:III].

**12.3.4 Correcting an error the player has already seen.** `[D]` + `[J:enum]` When a mismatch between
something already delivered and the store is found — by the scene-end sweep (12.4.8), by a later claim
check, or by the player (12.3.6) — the DM runs PR-12-4:
1. **Find the truth.** *State wins* (INV-2) — with one exception: a **record error**, where the narration
   matched a legitimately resolved outcome but a write it required was missed or mis-entered (the frame
   delivered the key; `set_fact` never ran). Test `[J:flag]`: *"Does a resolved source in the log (a frame,
   a handler result, an Oracle answer, a generator output) require the narrated value?"* True only when
   that source's id can be named. True → the store is repaired by a corrective write citing the source
   (`source: correction`, `supersedes` the wrong value). False → it is a **narration error** and the store
   stands.
2. **Choose the form** `[J:enum]`:
   - **In-fiction reconciliation** — true only when one sentence of fiction can make the delivered
     narration consistent with the store *without creating any new fact that helps or hinders anyone*
     ("You count again: twelve coins, not twenty — the dim light fooled you"). False when the fix would
     need a new event, a new object, a changed NPC mind, or a convenient excuse.
   - **OOF correction note** — format 12.15.9; one or two lines, plain, no apology essay.
   - Default when uncertain: the OOF note. A record error always gets the OOF note (the player should
     know the record was wrong), optionally plus an in-fiction line.
3. **Reliance.** `[J:flag]` *"Did the player, after the error and before this correction, commit any beat
   that cited, targeted or premised the erroneous claim?"* True only when a frame's levers, target,
   method, or the player's words name it. If true:
   - **Within the current scene**: the player chooses (pause point 9) one of: **keep** — offered only
     when the beat's committed frame remains valid with the erroneous element removed (no lever, target
     or premise rested on it); the result stands untouched; **accept forward** — the beat's resolved
     result stands and the false element is corrected around it (for a player who prefers that to
     re-rolling); or **rewind** — the store is restored from the write history to just before that beat
     (Interface request: `revert_writes`), the beat's rolls are logged as voided, and the player
     re-declares. A committed roll is never recomputed with different numbers (01.8.5). Rewinds go back at
     most to the turn of the error and never past the current scene's start.
   - **Before the current scene**: no rewind. The correction runs forward, and the player is **made
     whole** for quantities spent *because of* the falsehood: each such spend (coin, Focus, supply, a
     consumable, fate) is restored by a corrective write. Nothing else is compensated (no free success, no
     bonus) — the aim is to remove the error's effect, not to pay damages.
4. **Log** a correction record `{turn_of_error, turn_found, found_by, claim, store_value, kind:
   narration_error|record_error, form, reliance, rewound_beats, refunds}` to the corrections ledger
   (`available`), and a ruling record with `review_flag: true` (12.12.4).
*Worst case (J):* an in-fiction reconciliation chosen where it smuggles in a convenient fact — it is
visible in the correction record and the claim check of the reconciliation sentence itself catches a new
fact (`unsourced_change` or `new_element` verdicts are illegal in a reconciliation), class iv; a reliance
flag wrongly false — the player raises it as a DISPUTE and the procedure reruns, class iv
[R1 G-3, #2; R4 §3.3 W9; C:III; C:P13].

**12.3.5 What is never corrected away.** `[D]` A correction never: re-rolls a die whose frame was valid;
changes a degree, a delivered reach or a cost that was correctly resolved; removes a consequence the
player's own declared method caused; or rewinds past a lethal frame's resolution, a recognition grant
the player accepted, or a session boundary. Those are outcomes, not errors (01.8.5).

**12.3.6 Disputes.** `[D]` + `[J:enum]` When the player says the DM erred, the DM answers from the turn log
and the store, never from memory:
- **The narration said it and the store does not hold it** → an error; run 12.3.4.
- **The store holds it and the narration never said it** → no error; answer OOF with the store's value
  ("Your quiver holds 4 arrows") and, if the player was misled by an omission, run the reliance test of
  12.3.4 step 3 anyway (an omission that hid a changed state is a narration error: the narration was
  obliged to name it, 01.12.2).
- **Neither said it** (the player remembers something that never happened) → quote the relevant
  exchange from the turn log, OOF, in one line; no fact is created (INV-9).
- **The player disputes a ruling, not a fact** ("that should have been Easy") → show the frame and its
  cited facts; if the player names a fact that would change it, the DM checks the fact in the store: if it
  exists and was missed, the frame was wrong (`[J:flag]` *"Was an established fact that changes the tier,
  stakes, reach or a lever omitted from a committed frame?"*) — a ruling error handled as 12.3.4 with
  reliance automatically true for that beat; if it does not exist, the ruling stands.
*Worst case (J):* a valid dispute rejected — it remains in the turn log and the ruling ledger with the
player's objection attached, and recurs as review evidence (class iv).

**12.3.7 Moderation is not consistency.** `[D]` Safety removals (12.5.6–12.5.7) change *content*, are
logged separately from corrections, and never count as errors; consistency corrections change *truth*
and never invoke safety. The two tolerate different error rates — a needless safety removal costs a line
of fiction, a needless "correction" corrupts the world — and are kept in separate ledgers [C:P13; R1 12.D].

### 12.4 Scenes: framing, cutting, and time modes

**12.4.1 The scene record.** `[D]` A scene (00.18: a continuous situation with one focus) is an entity of
kind `object` with id `scn.*`, written at `scene_start`: `{id, agenda (one question), expected (the
player's expected scene, one line, or null), test_result (expected|altered|interrupted|untested), mode,
place, cast_present [ids], pillar, challenge_type, started_at, ended_at, frames [ids], intensity_points,
control_points, chaos_points}`. The **agenda** is the one question the scene exists to answer ("Does
Wren get across the river before the riders arrive?"; "What does the ferryman know?") — the Alexandrian's
scene agenda [R: https://thealexandrian.net/wordpress/31509/roleplaying-games/the-art-of-pacing]. The
agenda is written in neutral terms and never promises an answer.

**12.4.2 When a scene starts and when it is cut.** `[T]` + `[J:flag]` A scene **ends** (`mark_boundary(scene_end)`)
when the first of these is true; the next scene starts at once (`scene_start`):
1. **Agenda answered** `[J:flag]` — the scene's question now has an answer in state (a frame's degree
   settled it, a clock completed, the NPC refused or agreed). True only when a write this turn settles it.
2. **Place change** — the PC moves to a different place node (00.6.2 Place), or `travel` mode begins.
3. **Time jump** — the player skips time (`advance_time` of at least one `hour`, or any watch, day or
   downtime span), or a rest of any type completes.
4. **Interrupt** — `advance_time` halted on an interrupting handler (00.7.8): a new scene is framed at the
   interrupting moment.
5. **Conflict ends** (`conflict_end`).
6. **The player cuts** — the player says to move on ("skip ahead", "I leave", "next morning").
7. **Dead air** — `[D]` two consecutive DM turns in which the player's message held only SPEECH or free
   activities and nothing was written except time (`pacing.yaml#scenes.dead_air_turns: 2`): the DM offers
   a cut OOF in one line ("Move on to …? Or stay a while.") and frames the next scene unless the player
   stays. This is the Alexandrian's "skip empty time" made a counter [R1 M-41].
A conflict is always its own scene. *Worst case (J, 1):* an agenda judged answered too early cuts a scene
the player wanted to continue — the player may stay ("I'm not done here"), which re-opens it with the
same id (class iv).

**12.4.3 Framing a scene.** `[J:enum]` + `[N]` Every scene opening has four parts, in this order, in at
most **200 words** (`pacing.yaml#narration.scene_open_max_words`):
1. **The moment** — where, when (time of day and weather from state, never invented), who is present
   (each addressable element written on mention, 00.6.6), and the layout the PC can see: exits, cover,
   hazards, what is within reach (12.14.6).
2. **The impetus** — one thing that is happening or about to, drawn `[J:enum]` from this ordered list,
   first eligible: (a) the scene test's alteration or interruption (12.4.4); (b) a fired trigger
   (12.2.3); (c) the PC's own declared purpose for the scene; (d) an NPC present acting on a recorded
   want; (e) a sensed or hidden clock's latest omen; (f) the most overdue rotation axis's opportunity
   (12.9.2). The impetus comes from state; it is never invented to be dramatic.
3. **Framing hardness** `[J:enum]`: **in medias res** (start at the first moment of decision or danger —
   default for interrupts, chases, ambushes, and any scene whose approach holds no decision); **at the
   threshold** (start as the PC arrives — default for new places and social scenes); **open** (start
   with the PC at leisure — only for downtime and havens). Default when uncertain: at the threshold.
   Skip any stretch in which no meaningful decision could be made
   [R: https://thealexandrian.net/wordpress/31520/roleplaying-games/the-art-of-pacing-part-2-scene-framing;
   R1 M-41].
4. **The open prompt** (12.14.9).
*Narration may not imply:* any element not written on mention; any clock fill not public; a sealed fact.
*Worst case (J):* a weaker impetus chosen from the list — the scene opens flatter, never falser (no state
effect; class i in pacing terms). *Strong start:* the first scene of every session opens in medias res
or at the threshold of something that demands a choice (12.5.2) [R: https://slyflourish.com/eight_steps_2023.html].
*Examples:* inside "in medias res": the PC declared "I ride for the ford before the riders catch me" —
open with hooves on the far bank and the water at the stirrups, not with the ride there. Outside: "I
walk into the Drowned Lantern to find the ferryman" — at the threshold (new place, social). Non-example:
opening a downtime week at the monastery in medias res with an invented fire — the impetus list has no
fire in it unless a roll or clock put one there.

**12.4.4 The scene test.** `[D]` + `[J:enum]` At every `scene_start`, handler `h.12.scene_test` (phase 7)
runs the test unless the scene is **untested**: a direct continuation (same place, less than one
interval later), a conflict, an interrupt's own scene, or a scene the player framed as downtime in a
haven. Otherwise:
1. The DM writes the **expected scene** in one line from the player's stated plan ("Wren reaches the
   ferry landing at dusk and finds the ferryman").
2. The engine rolls `tbl.scene_test` (d10). With **tension** T (12.6.3), the scene **deviates** when the
   roll ≤ T − 3: an **odd** roll → **altered**, an **even** roll → **interrupted**; otherwise **expected**.
3. **Altered**: `roll_table(tbl.scene_adjustment)` → one adjustment (add or remove a person; intensify or
   reduce an activity; add or remove an object; shift the time; change a feature of the place; two
   adjustments). The DM applies it as the next most likely version of the expected scene `[J:enum]`
   (which person, which object — from state or a table), and writes it.
4. **Interrupted**: a random event replaces the expected scene (12.6.5); the expected scene is still
   available afterwards if the player pursues it.
Deviation rates by tension (T-12-9): T 1–3 none; T 4 10% (altered only); T 5 20%; T 6 30%; T 7 40%;
T 8 50%; T 9 60%; altered and interrupted split as odd and even faces.
*Why lower than Mythic.* Mythic's test deviates whenever d10 ≤ Chaos (50% at the default 5) because in
Mythic the scene test and random events are the world's *only* motion [R5 P-05]. Here the world already
moves through clocks, watch and interval checks, the World Turn and NPC wants, so the scene test is a
seasoning, not the engine: 20% at the default tension, rising to 60% when the PC has lost control
[DL-12-06]. *Worst case (J):* a less likely version of the altered scene chosen — one person or object
different, written as fact, never harmful by itself (class i). [R5 P-05; R6 B-16]

**12.4.5 Time modes and transitions.** `[D]` + `[J:enum]` At every `scene_start` the DM classifies the mode
(00.7.3; default the previous scene's; uncertain → `free`). Within a scene, the mode changes only on the
transitions of T-12-3, each of which calls `mark_boundary(mode_change)`; handler `h.12.mode_change`
loads the new mode's cards (by the `situation.*` tags listed in T-12-3) and sets time-per-beat.

**T-12-3 Mode transitions** (canonical: `pacing.yaml#modes`).

| From → to | Fires when (closed list) | Cards loaded |
|---|---|---|
| any → `conflict` | an adversary's behavior list attacks; the PC declares a Strike, Grapple or harmful Force or ability against a creature that resists; a hostile NPC action result says "attacks"; a clock completion creates an attacking encounter (`conflict_start`, 06.2.1) [revision: I-030] | `situation.conflict.*` |
| `conflict` → previous | `conflict_end` (06.13.1): no hostile participant able and willing to act, a side's objective met, a truce, or the PC gone or defeated [revision: I-030] | the previous mode's |
| any → `site` | the PC enters a place tagged as a site (ch.10) or begins a room-by-room search of a building | `situation.exploration.*` |
| any → `travel` | the PC departs along a route link between places (ch.10) | `situation.travel.*` |
| any → `downtime` | in a haven, the player declares a downtime activity (ch.15) or a span of days | `situation.downtime.*` |
| any → `free` | the PC leaves a site for a settlement place, arrives from travel, ends downtime, or none of the above applies | `situation.social.*`, `situation.investigation.*` by scene tags |

*Worst case (J):* the mode classified wrongly at a scene start — time per beat is wrong for at most that
scene; site danger clocks still tick from costs (class i, 00.7.3).

**12.4.6 Skipping time.** `[D]` When the player skips time ("we travel three days", "I spend the winter at
the monastery") the DM calls `advance_time` and narrates *only from the returned list* of boundaries,
omens, rumors, handler results and interrupts, in chronological order, at most one sentence per
returned item and at most **150 words** for the whole skip unless an interrupt frames a new scene
(`pacing.yaml#narration.skip_max_words`). It invents no weather, encounter, rumor or change that is not in
the list (PR-00-2 step 5). If the skip halts on an interrupt, the remainder is offered back to the
player after the interrupting scene (00.7.8) [R5 TM-10; 00.7.7].

**12.4.7 Montage.** `[D]` A montage is a time skip with repeated activity ("I spend the week asking around
the docks"). It is resolved as ch.15's or ch.10's activity for its listed duration, with one frame per
activity unit as those chapters set, run inside `advance_time`. The narration is the skip narration of
12.4.6 plus each frame's result in one sentence. No montage compresses rolls (01.2.3; 01.14.3)
[R: https://thealexandrian.net/wordpress/44117/roleplaying-games/scenario-structure-challenge-5-the-rpg-montage].

**12.4.8 Scene-end bookkeeping.** `[D]` Handler `h.12.bookkeeping` (`scene_end`, phase 9; mirrored on
`session_end`, 00.7.9) runs, in order (Mythic's end-of-scene adjustments made explicit [R5 P-09]):
1. **Tension** update (12.6.3) — `h.12.tension_update`.
2. **Intensity and phase** update (12.7.2) — `h.12.intensity_scene` (contrib handler).
3. **Lists**: the cast list and thread list weights are updated (12.6.6).
4. **Sweep**: every trigger raised during the scene was handled (12.2.3); every hidden or sensed clock
   tick rendered one omen (INV-14); every claim of class `position`, `possession`, `quantity` and
   `harm_condition` in the scene's delivered narration is re-checked against the store with
   `check_claims` — a mismatch found here starts PR-12-4.
5. **Live-lead audit** (12.8.4) — `h.12.lead_audit` (contrib handler).
6. **Rotation ledger** (12.9.1) — `h.12.rotation_update` (contrib handler).
7. **NPC memory** commit (12.11.7) — `h.12.npc_memory` (contrib handler).
8. **Scene record** closed: `ended_at`; when the scene answered an agenda attached to a thread, a
   one-line chronicle entry is offered to ch.11 (`chronicle_append`).
Every step is deterministic except the chronicle line's wording `[N]`.

**12.4.9 Venture bookkeeping.** `[D]` Handler `h.12.venture_bookkeeping` (`venture_end`, phase 9, after ch.11's
`h.11.reckoning`): (1) offers ch.11 one chronicle entry for the venture, built from its scene records'
agendas and answers (`[N]` wording, every sentence claim-checked); (2) re-runs the live-lead audit (12.8.4)
for every thread the venture touched; (3) marks the end of any recovery window that has run out (12.7.5);
(4) if the PC is in a haven, frames the return scene `open` (12.4.3) with the reckoning's results as its
impetus. A venture is the natural unit of the sandbox loop — free play in a haven, a venture out, the
return and reckoning, downtime — the Blades cycle adapted to an open world [R5 P-12].

### 12.5 Session moves and safety in play

Session moves are the player's out-of-fiction controls over the *session* (not the fiction) and the
DM's obligations when they are used. They adapt Starforged's session moves and the TTRPG Safety Toolkit
into rules of play [R5 P-10, SC-01, SC-02, SC-06; R1 G-22]. Ch.14 owns the player-facing presentation and
the preference records (lines, veils, flags, pacing profile, auto-commit); this chapter owns what the DM
does. No session move advances fictional time (00.7.9).

**12.5.1 Session zero.** `[D]` The first session begins with ch.14's session zero (tone, lethality
consent, lines and veils, flags, pacing profile 12.7.3, auto-commit, the preference check-in 12.5.9), then
the world seed (12.16, PR-12-9; or a pre-made seed such as ch.13's, checked by 12.16.17), then character
creation (02), then the seed's opening (12.16.16) [revision: I-028]. The DM records each answer through
ch.14's preference tools before the first scene is framed; nothing in the seed or the first scene may touch
an unrecorded line [R5 SC-03, SC-04].

**12.5.2 Begin a session.** `[D]` Handler `h.12.session_open` (`session_start`, phase 9), then the DM:
1. **Review flags**: reads the preference record; any line, veil or flag added since last session is
   applied from now on.
2. **Recap from state** (12.5.3), at most **120 words** (`pacing.yaml#narration.recap_max_words`).
3. **Restate the situation**: where the PC is and what is pressing (the open clocks visible to the PC,
   the threads marked active, any open offers), as a short OOF list (format 12.15.11).
4. **Pending items**: an OFFER or other pause left open at the last session end is re-shown, unchanged.
5. **Strong start**: the session's first scene is framed (12.4.3) at a moment of decision. If the last
   session ended at rest with nothing pressing, the DM rolls `tbl.vignette` (a danger, an opportunity or
   an insight, rooted in an existing thread, clock or NPC) as that scene's impetus [R5 P-10 "Begin a
   Session"; R: https://slyflourish.com/eight_steps_2023.html].
6. **Check-in** if due (12.5.9).

**12.5.3 Recap.** `[D]` + `[N]` A recap — at session start, or whenever the player asks "where were
we?" — is generated **from state only**: the chronicle entries since the last recap, the active threads
with their last progress, the PC's current position, condition and pressing clocks (as shown), and the
last scene's agenda and its answer. It is never generated from a previous recap or from a summary of
narration (00.6.9d) [R1 12.D (never summarize a summary; recaps from state)]. A recap may be in an
in-fiction voice ("Three days ago you left Ashford…") but every sentence passes the claim check (12.3).

**12.5.4 End a session.** `[D]` When the player ends the session ("let's stop here"), the DM: (1) finishes
the current beat only if it is past ROLL; an open OFFER stays open, uncommitted, and is re-shown next
session; (2) runs `mark_boundary(session_end)` (handlers `h.12.session_close` and the mirrored
`h.12.bookkeeping`); (3) asks one optional OOF question: "Anything you want to focus on next time?" — the
answer is stored as a `next_time` note (shown at the next session's start; it never becomes a fact);
(4) ends with one line naming where the PC stands. Nothing ticks: a session boundary is not time
[R5 P-10 "End a Session"; 00.7.9].

**12.5.5 Take a break.** `[D]` The player may pause at any point ("brb", "pause"). The DM confirms in one OOF
line and stops; the next message resumes exactly where play stopped, with any pause point still open.
No handler runs; no time passes.

**12.5.6 Lines, veils and flags in play.** `[D]` + `[J:flag]` Ch.14 owns the records; the DM's obligations:
- **Line** (must never appear): content matching a line is never narrated, never generated, never rolled
  into play. Every table roll, generator output and random event is screened before use (`[J:flag]`
  *"Does this result's content fall under a recorded line?"* — true only when it matches the line's
  stated topic); a matching result is re-rolled once on the same table, then replaced by the table's
  nearest non-matching row, logged as a safety substitution (12.3.7).
- **Veil** (may happen, off-screen): the event occurs in state if the rules produce it, and the narration
  summarizes it in one plain sentence without detail ("The interrogation lasts until dawn.").
- **Flag** (handle with care): when a flagged topic is about to enter a scene (a trigger raised by
  `get_active_triggers` when a scene's cast, threads or rolled content carries the flag's tags), the DM
  pauses with one OOF line before narrating it — "This touches [flag]. Continue, veil it, or steer away?"
  — and follows the answer [R5 P-10 "Set a Flag"].
*Worst case (J):* a line-adjacent result judged not matching reaches the draft — the T10 safety screen
checks the draft against the lines list again, and the adjust move (12.5.7) removes it at the player's
word (class iv).

**12.5.7 Adjust (the player's change-your-fate move).** `[D]` + `[J:enum]` At any time the player may say
content is not working ("adjust", "skip this", "X"). The DM stops, acknowledges in one OOF line without
asking why, and applies one of five re-framings `[J:enum]`, chosen by the player if they say, else by the
DM in this default order [R5 P-10 "Change Your Fate"]:
1. **Reframe** — the same events from a different angle or distance (less detail, different emphasis).
2. **Refocus** — the spotlight moves to another part of the scene.
3. **Replace** — the troubling element is swapped for a different element of the same mechanical weight.
4. **Redirect** — help or interruption arrives that moves the scene elsewhere (from 01.11.3's sources or
   a table, never invented).
5. **Reshape** — the situation is changed wholesale: the scene is cut and reframed.
**What adjust may change:** the fictional content, form and detail of what has happened or is about to;
facts whose *content* is the problem (superseded by a fact of the same mechanical valence — a
complication stays a complication of the same severity; an enemy stays an enemy). **What adjust may not
change:** a degree, a delivered reach, a cost's menu entry or severity, a clock's fill, a harm state or
Vitality, or any outcome's mechanical weight — safety reshapes *what it is*, not *how much it costs*
(00.1.5 puts safety first, and nothing about safety needs the game to become easier or harder). If the
player also wants a new line or veil recorded, the DM records it (ch.14). Adjusts are logged in the
safety ledger, never as corrections or rulings (12.3.7). *Worst case (J):* a replacement of different
fictional flavor than the player wanted — same weight by construction; the player may adjust again
(class i).

**12.5.8 Rewind and take-backs.** `[D]` The closed list of take-backs:
1. **Before ROLL** — free: the player may withdraw or change any declaration at its OFFER (01.7.1).
2. **A misread intent** — if the DM resolved a beat on a reading the player never saw (no OFFER shown and
   no assumption stated per 01.2.4) and the player's very next message says the reading was wrong, the
   beat is a DM error: PR-12-4 with reliance true; the player may rewind it.
3. **A DM error** — PR-12-4.
4. **Safety** — adjust (12.5.7), which changes content, not mechanics.
5. **Nothing else.** A committed roll is final (01.8.5); "I didn't like that result" is not a take-back.
Every rewind restores the store from the write history and logs the voided frames; RNG draws are never
"un-drawn" (the log keeps them, marked void) [R5 SC-06; 01.8.5].

**12.5.9 The preference check-in.** `[D]` Because an AI DM cannot read a face, it asks [R1 12.B: an AI GM
"might need to ask players directly about their engagement levels"; R1 M-34]. At session zero, then at
the start of every **fourth** session (`pacing.yaml#checkin.every_sessions: 4`), and whenever the player
asks, the DM asks one OOF question set, every answer optional (format 12.15.12): (a) more / same / less
of each pillar (conflict, exploration, social, investigation, travel, downtime); (b) pace: faster /
same / slower; (c) anything to add to lines, veils or flags. Answers set the rotation weights (12.9.3)
and may change the pacing profile (12.7.3). They never change difficulty numbers, odds or costs.

**12.5.10 Out-of-fiction questions.** `[D]` OOF questions take no fictional time and are answered at once:
- **Rules** — the rule id and its text or a faithful one-line paraphrase ("01.4.2: one resolved beat
  settles one obstacle for one approach").
- **"What would it take?" / "What are my odds?"** — run GATE→FRAME→OFFER without commitment (01.7.1);
  the OFFER is shown and nothing is spent.
- **Codex** — rendered by the `codex` tool per visibility class (ch.14).
- **"How was this ruled before?"** — the matching ruling-ledger record (12.12.5).
- **Sealed or background things** — "Your character doesn't know that", plus whatever the codex shows
  (00 edge cases); never a hint, never a wink.
- **"I'm stuck" / "what can I do?"** — the stuck answer (12.8.5).
[R5 DM-09; R1 12.C (being open about what isn't ready is not railroading)]

### 12.6 The DM's own questions: the Oracle, the tables, the tension dial, and random events

Ch.01 owns the one Oracle mechanism (odds rungs, thresholds, answer shapes, never-re-ask) and the
player-driven uses of it. This part owns the DM's use of it for its *own* uncertainty, the tension dial
that may shift its odds by one rung, the random events it can trigger, and the meaning tables that give
content to its "and"s (00.17.1 Q6).

**12.6.1 The DM never chooses what is true.** `[J:flag]` + `[D]` Whenever the DM needs something about the
world it does not have — for an NPC's behavior, a description, a scene's contents, a consequence's
form — it asks `[J:flag]` *"Would I be choosing what is true?"* True when the needed thing is a fact, a
property, a presence, a choice among possibilities, or an NPC's decision that is not already settled by a
fact id, setting canon (the region's seed, 12.16.5) or scene logic (the scene type implies it: a smithy has a forge). If true,
the DM may not decide it; it settles it by the first matching tool of T-12-4 and writes the result before
narrating it. False only when a fact id, canon line or scene type can be named that settles it. Uncertain →
true (SG-12). *Worst case (J):* a thing "settled by scene logic" that was actually open — the DM decided one
small fact; it is logged as narration-sourced and any later contradiction is caught by the claim check
(class iv). Example inside: "Is the ferryman home?" (unestablished → Oracle). Outside: "Does the ferry
landing have a boat?" (a ferry landing implies a ferry; scene logic → Certain). Non-example: "The
ferryman is home *because the scene needs him*" — that is the DM choosing what is true.

**T-12-4 Which tool answers the DM's uncertainty** (first match; canonical: `pacing.yaml#dm_questions`).

| The uncertainty is… | Tool | Example |
|---|---|---|
| answered by a fact, canon, or scene type | read it (Certain / Impossible) | the smithy has a forge |
| whether an actor with known capability manages something | fortune check (01.6.7) | does the messenger outrun the storm? |
| which of several things, from a *specific* table in data | `roll_table(<specific table>)` — region tables (12.16), encounter tables (10), rumor tables (11), loot (08), NPC tables (12.11) | who is drinking at the inn tonight |
| what an NPC does when no want, refusal or frame decides it | `roll_table(tbl.npc_action, {standing})` (12.11.5) | the dockhand, after the PC's question |
| whether something is so, yes or no | `oracle(question, rung, fact_key)` (01.15) | is the ferryman home? |
| what something means, what form it takes, what "and" comes with a yes-and | `roll_table(tbl.meaning)` (12.6.7) | what the strange event is about |
| a person who must exist now | NPC generation (12.11.1) | the clerk behind the counter |

**12.6.2 The DM asks before it narrates, and asks only once.** `[D]` The Oracle answer or table result is
written (`set_fact`, `create_entity`) before the narration that uses it is drafted (PR-00-7), so the claim
check sees it as `supported`. The DM never asks the same question twice (01.15.7) and never asks a
question it intends to ignore. The DM may ask several questions in one turn, but each is a separate
logged question with its own odds committed before its roll.

**12.6.3 The tension dial.** `[D]` + `[J:flag]` **Tension** is a background integer **1–9, starting at 5**
(`pacing.yaml#tension`), measuring how far events have slipped out of the PC's control — Mythic's Chaos
Factor, renamed and fed by state [R5 P-01; R6 B-16]. Handler `h.12.tension_update` (`scene_end`, phase 9)
computes the scene's **chaos points** and **control points**, each `[D]` from the scene log (one point per
item, each item at most once per scene):

| Chaos points (the world took control) | Control points (the PC took control) |
|---|---|
| the scene test came up altered or interrupted, or an interrupt framed the scene | the scene's agenda was answered the way the PC hoped (below) |
| the scene's agenda was answered against the PC's hope | the PC completed a progress clock, a thread milestone, or a vow step |
| the PC paid a cost of S3 or heavier | the PC overcame or drove off the scene's opposition paying no cost heavier than S2 |
| the PC became Staggered, Dying, or defeated, or yielded, or was captured | the scene was framed by the PC's own declared purpose and its test came up expected |
| a twist of S3 or heavier landed (01.13.10) | the PC turned an NPC's standing up by one or more steps |
| an opposition clock reached imminent or completed | the PC unsealed a secret of an active thread |

**Delta**: +1 if chaos points exceed control points, −1 if control points exceed chaos points, 0 on a tie;
clamped to 1–9. **The hoped answer** is the single `[J:flag]` in this rule: at `scene_start` the DM records
which answer to the agenda question the PC is pursuing (yes or no), from the player's declared purpose;
when the player has declared none, the hope is null and neither agenda row scores. *Worst case (J):* a hope
recorded backwards swaps one point from one column to the other; tension moves by at most one step the
wrong way (class i), and the next scene's evidence corrects it (class iii). Tension is shown to no one
(background); it is voiced only as the world's mood (12.14.7).

**12.6.4 What tension does (closed list).** `[D]` + `[J:enum]`
1. **The scene test** (12.4.4): deviation when d10 ≤ T − 3.
2. **Random events on Oracle doubles**: an Oracle roll of doubles 11–99 whose repeated digit is **≤ T**
   triggers a random event (12.6.5) alongside the extreme answer (01.15.3); 100 never does. Per question:
   T% (1% at T 1 … 9% at T 9; 5% at the default) [R5 P-01, P-11].
3. **The Oracle odds shift** — at most one rung (00.12.7; 01.15.2 decision 2). When the DM chooses a
   question's odds, it also tags `[J:enum]` the question's **eventful answer**: `yes`, `no`, or `none`. The
   eventful answer is the one under which something *happens to* the PC or *someone acts*: a threat is
   present or acts, an NPC arrives or intervenes, a situation worsens, a complication appears. True for
   "Are the riders already at the ford?" (eventful = yes) and "Is the bridge still standing?" (eventful =
   no). `none` for questions about the static availability of something the PC is looking for ("Is there
   a rope in the storeroom?", "Does the clerk keep a ledger?") and for every question the player asked to
   learn about the world (G0). Uncertain → `none`. Then, `[D]`: **T 7–9** shift one rung toward the eventful
   answer; **T 1–3** shift one rung away from it; **T 4–6** no shift. A shift never moves onto or off Certain
   or Impossible (it moves only among Likely, Even, Unlikely, Remote) and never past the ends of that
   range. The shifted rung is logged with the base rung, before the roll. *Worst case (J):* a wrong
   eventful tag shifts one rung the wrong way — 15–25 points on one question, logged before the roll
   (class i); a question tagged `none` that should have been eventful forgoes the shift (harmless).
*What tension never does:* change a DC, a frame, a modifier, a cost, a clock's tick, or the player's own
G0 questions' odds. The dial changes how often *the world* acts, not how hard the PC's actions are
[R1 #9].

**12.6.5 Random events.** `[D]` + `[J:open]` A random event is the world acting on its own. Sources (closed
list): (a) an Oracle double ≤ T (12.6.4); (b) an interrupted scene (12.4.4); (c) the session-start
vignette when nothing is pressing (12.5.2); (d) a `tbl.event_focus` roll called for by another chapter's
table row (e.g. a ch.10 watch-check result "event": the V face, 10.9.4 [revision: I-030]). Procedure (PR-12-6):
1. `roll_table(tbl.event_focus, {phase})` (d100) → the **focus**: remote event, NPC action, new NPC,
   faction move, thread advances, thread complicates, thread resolves off-screen, PC opportunity, PC
   complication, rumor arrives, omen, current context, or ambiguous (T-12-6).
2. **Target**: if the focus names an NPC, a thread or a faction, roll the weighted list (12.6.6) to pick
   which; an empty list → the focus becomes *new NPC* (for NPC foci) or *rumor arrives* (for thread and
   faction foci).
3. **Meaning**: `roll_table(tbl.meaning, {kind: action})` → a verb and a subject (12.6.7).
4. **Interpret** `[J:open]`, bounded: one sentence that (i) involves the target, (ii) reads the two words
   in their most natural sense for this place and these people, (iii) contradicts no established fact, and
   (iv) is expressed only through these writes: `create_entity` (an NPC via 12.11.1, an object, a rumor via
   ch.11's tables), `set_fact` (`source: generation`), an NPC action applied to the target (12.11.5), one
   tick on a thread or faction clock that lists `random_event` among its tick sources (Interface request to
   11), or a new situation seed handed to ch.11.
5. **Write**, then narrate; the event is perceivable now (in this scene) or arrives as news at the next
   plausible moment (a remote event).
**Bounds** (P-B): a random event never harms the PC directly, never applies a cost, never kills, never
grants a license or item beyond what a table or generator produces, never reveals a sealed fact except
through its gate, and never resolves a thread the PC has sworn a vow to or progressed in the last
**twelve** scenes (`pacing.yaml#events.offscreen_resolution_protect_scenes`) — that roll reads as *thread
complicates* instead. During the pacing director's RELAX phase, threat-tagged foci read as *omen*
(12.7.3). *Worst case (J):* an odd or weak interpretation — a harmless, written fact the world keeps
(class iv: later narration builds on it; it cannot cost the PC anything by itself)
[R5 P-11; R6 B-16; R4 SG-12].

**12.6.6 The cast and thread lists.** `[D]` The engine keeps two weighted lists for random selection
(Mythic's Characters and Threads lists [R5 P-07]): the **cast list** (every NPC the PC has met who still
exists and is not departed) and the **thread list** (every active thread in ch.11's register). Each entry
has a **weight 1–3**. At `scene_end` (12.4.8 step 3): +1 (max 3) for each NPC or thread that was the
scene's agenda, acted in the scene, or was named in a delivered lead; −1 (min 1) for each not featured in
the last **six** scenes; an entry is removed when its NPC is dead or departed or its thread is resolved,
failed or abandoned. A roll on a list draws by weight with RC-RNG; an entry drawn twice in a row is
re-drawn once (recency). Factions are drawn from ch.11's faction list by the same weights rule when a
focus names a faction.

**12.6.7 Meaning tables.** `[D]` + `[J:open]` `tbl.meaning` returns a pair of words: an **action pair**
(a verb and a subject: "betray — a promise") for events and the "and" of yes-and / no-and answers, or a
**description pair** (a descriptor and a focus: "hungry — stone") for what a thing, place or person is
like. Each word list has 100 entries authored for this game (classic fantasy, original to this ruleset;
`data/oracles.yaml`), rolled on d100 with recency (an entry drawn in the last 20 draws of that list is
re-drawn once) to counter homogenized output [R4 W10; R5 P-04]. Interpretation rules: the DM commits the
interpretation as a fact in one sentence before narrating it; reads the pair in context, preferring the
most specific reading that involves the question's subject; and never re-rolls for a better pair — the
single exception is a pair with no reading consistent with established facts after an honest attempt
(`[J:flag]` *"Does every reading of this pair contradict a fact id I can name?"*), which permits one
re-roll, logged; the second pair stands and is read at its most abstract. *Worst case (J):* a strained
reading — a written, harmless fact (class iv).

### 12.7 The pacing director

The pacing director decides *when the world pushes and when it lets the PC breathe*. It adapts L4D's AI
Director (an intensity estimate cycling build-up → peak → fade → relax) and RimWorld's storytellers (a
named pacing profile; a recovery window after losses; escalation after easy wins) to scenes instead of
seconds [R6 B-10, B-11, B-R3; R: https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf;
R: https://rimworldwiki.com/wiki/AI_Storytellers]. It governs only the pushes this chapter owns — the
pacing push (12.7.4), random-event foci (12.6.5) and scene-test interruptions (12.4.4) — and never
suppresses another chapter's handler (encounter checks, the World Turn, clocks run exactly as written).

**12.7.1 Intensity.** `[D]` **Intensity** is a background integer **0–10**. Each scene accrues
**intensity points** `[D]` from its log (each item counted as listed; scene total capped at 10;
`pacing.yaml#intensity.points`):

| Event in the scene | Points |
|---|---|
| the scene was a conflict | 2 |
| each PC frame that failed at Risky / at Dire | 1 / 2 |
| each cost the PC paid at S2 / S3 / S4 or heavier | 1 / 2 / 3 |
| a lethal frame was declared (once per scene) | 2 |
| the PC became Staggered / Dying (once each) | 3 / 4 |
| an opposition clock reached imminent / completed | 1 / 2 |
| the scene opened with an interrupt or an ambush | 1 |

At `scene_end` (`h.12.intensity_scene`): **intensity = min(10, max(scene points, previous intensity − 3))** —
it jumps to a hard scene's score and drains three per calmer scene. Handler `h.12.intensity` on
`conflict_start` / `conflict_end` (reserved, T-00-9) marks conflict boundaries for the count.

**12.7.2 Phases.** `[D]` The director is always in one phase (`pacing.yaml#intensity.phases`):
- **BUILD** (default): pushes allowed. Enters PEAK when intensity ≥ the profile's **peak threshold**.
- **PEAK**: the world is already pressing hard. No pacing push fires, threat-tagged random-event foci read
  as *omen*, and a scene test's *interrupted* reads as *altered*. PEAK lasts while intensity stays at or
  above the threshold; the first `scene_end` at which the scene's points fall below the threshold moves the
  director to RELAX.
- **RELAX**: as PEAK, for the profile's **relax length** in scenes; then BUILD. Lead injection (12.8) still
  fires in RELAX (a lead is not a threat), using only forms not tagged `threat`.
- **Flatline guard** (in BUILD): when the profile's **flat run** of consecutive scenes each scored ≤ 1
  intensity point, the trigger `trg.pacing_push` is raised for the next `scene_start` (12.7.4).

**12.7.3 Pacing profiles.** `[D]` The player picks one at session zero (12.5.1) and may change it at any
check-in (12.5.9). Canonical numbers in `pacing.yaml#profiles`:

| Profile | Peak threshold | Relax length (scenes) | Flat run before a push | Recovery after a setback (scenes) | For a player who wants… |
|---|---|---|---|---|---|
| `standard` (default) | 7 | 2 | 3 | 3 | a rising, falling adventure rhythm |
| `gentle` | 6 | 3 | 4 | 4 | more breathing room, fewer pile-ons |
| `relentless` | 8 | 1 | 2 | 2 | pressure; the world rarely waits |

*Why these numbers.* A single Dire failure with an S3 cost in a conflict scores 2 + 2 + 2 = 6; adding a
lethal declaration or a Staggered PC crosses 7 — so the standard PEAK means "a fight that genuinely
threatened the PC", matching L4D's notion of a survivor at peak stress; three points of drain per scene
returns a peak of 10 to BUILD territory in three quiet scenes (10 → 7 → 4), roughly RimWorld Cassandra's
on/off cycle at scene scale [R6 B-10]. The numbers are tunable data; OEQ-12-3 tests them.

**12.7.4 The pacing push.** `[T]` + `[J:enum]` When `trg.pacing_push` is raised (flatline guard, or the end
of a recovery window, 12.7.5), handler `h.12.pacing_push` (`scene_start`, phase 7 — a boundary handler, so
a legal complication source under 01.11.3 (5)) makes **one push** for the scene being framed. Candidates
(closed list): (a) the eligible bangs in ch.11's queue (proactive fallbacks, timeline bangs, faction
entanglements) — each carries `intensity_delta` (ch.11 data; default threat bang 3, social bang 1,
opportunity 0); (b) a `tbl.vignette` row; (c) the most overdue rotation axis's opportunity (12.9.2).
Selection `[D]` then `[J:enum]`: keep candidates whose `intensity_delta` fits the phase target (BUILD after
a flatline: ≥ 1; end of recovery: ≤ the recovery cap of 12.7.5); rank by **specificity** — keyed to this
PC and a deed of theirs > keyed to an NPC or faction the PC has dealt with > keyed to this region >
generic (Valve's and Hades' "most specific eligible wins" [R6 B-19]); ties by the stalest rotation axis
(12.9.2); remaining ties by `roll_table` on the tied set. The push becomes the scene's impetus (12.4.3
(b)). *Worst case (J):* the specificity rank misjudged by one step — a less personal but equally eligible
push fires (class i).

**12.7.5 Adaptation after setbacks and streaks.** `[T]` + `[D]` Two engine-raised states, each logged:
- **Recovery** — raised by a **setback**: the PC entered Dying, was defeated, captured or forced to yield,
  retreated paying a cost of S3 or heavier, or lost an ally of any kind to death (`setback.companion_dead`,
  16.9.5) [revision: I-030]. For the profile's recovery
  length in scenes the director is in RELAX regardless of intensity; when recovery ends, `trg.pacing_push`
  is raised and that push must have `intensity_delta` ≤ 1 and, if it is an encounter, a ch.09
  `threat_advisory` of *fair* or easier. RimWorld's adaptation: a loss is followed by room to recover, not
  a second blow from the director [R6 B-10].
- **Escalation permitted** — raised by a **streak**: three consecutive conflict scenes in which the PC paid
  no cost heavier than S1 and the advisory was *easy* or *trivial*, or three consecutive scenes with
  control points > chaos points. The next pacing push may be a candidate of advisory *hard*, and its
  challenge type must differ from the last two conflicts' (12.9.4): the answer to a dominant PC is a
  different kind of problem, not bigger numbers [R1 #8, 12.B].
These states change only *which* pushes the director chooses next. They never touch an encounter, frame or
clock already in play.

**12.7.6 No hidden adjustments.** `[D]` The director, the tension dial and the DM never: change a DC,
defense, Vitality, harm amount, modifier or clock size of anything already established; add or remove
foes in a fight except through a clock, a behavior list, morale (ch.09) or a table result; soften or
sharpen a declared cost; "let" the PC win or lose. Mid-scene adaptation exists only in diegetic,
pre-declared, logged forms: reinforcement or alarm clocks, morale breaks and retreats from behavior
lists, environmental events from tables, and the PC's own choices. Every such event is written to state
with its source, so the player could audit it [R1 #9, T-5; R4 W3].

### 12.8 No silent dead ends (P16)

**12.8.1 The inconclusive streak.** `[T]` + `[D]` Handler `h.12.inconclusive_streak` (`beat_end`, phase 9,
reserved T-00-9) keeps a background counter of the PC's consecutive **inconclusive** beats — ch.01's
definition, used verbatim: a beat is inconclusive when it wrote no new fact the PC learned, no clock
change, no position change and no delivered reach ≥ 1 (a Safe failure, a vague impression only, or a
restated ride) (01.11.4). A conclusive beat resets the counter to 0. When it reaches **3**
(`pacing.yaml#lead_injection.threshold`; constitution P16's "three or more") the handler raises
`trg.lead_injection`, which the DM must handle in the turn it is returned (12.2.3) [C:P16;
R: specs/001-action-resolution-probe/probe-results.md (soft-lock at turns 6–8)].

**12.8.2 Lead injection.** `[D]` + `[J:enum]` When `trg.lead_injection` fires, the DM must, in this turn's
world responses (12.2.9 step 4), deliver **one lead** (PR-12-3):
1. **Source** `[D]`, first eligible in this specificity ladder (`pacing.yaml#lead_injection.source_ladder`):
   1. an unfound clue placement of the thread the PC is pursuing in this scene (the scene agenda's thread);
   2. that thread's proactive fallback bang (ch.11);
   3. an unfound clue placement of another active thread, highest list weight first (an ally's personal
      thread, 16.12, is one such thread once open; its fallback is a ch.11 queue bang for 12.7.4) [revision: I-030];
   4. the most advanced sensed or hidden opposition clock — its *current* omen re-rendered as a concrete,
      investigable trace that points toward the threat (not a tick: the clock is unchanged);
   5. an NPC on the cast list with an unfulfilled recorded want who could plausibly seek the PC out,
      highest weight first;
   6. a rumor from ch.11's rumor tables for this region whose `points_to` is an existing node;
   7. a new hook from ch.11's hook generation (which writes its ≥ 3 clue placements).
2. **Form**: `roll_table(tbl.lead_injection, {phase})` (d12) — how the lead arrives (someone brings it, it
   is overheard, a found object, the opposition's mistake, a sign in the environment, an old contact, an
   offer, …). `[J:flag]` *"Can this source plausibly arrive in this form here and now?"* False → roll once
   more; a second misfit takes the form "a detail you had overlooked" (always compatible with sources 1,
   3 and 4) or "someone seeks you out" (sources 2, 5, 6, 7).
3. **Write** the facts that make it a lead (the clue unsealed through its gate, the NPC's approach, the
   rumor heard: `record_knowledge` for the PC), and reset the counter to 0.
4. **Narrate** it as fiction in this turn; no OOF line is needed.
**A lead must be** `[J:flag]` ×3, each true only with the named evidence: **concrete** (it names a person,
place, object or event by id); **actionable now** (the PC can pursue it from where they are, this scene or
next); **connected** (it points to a thread, clock or node in state). A lead must **not** solve the thread
(it is a way forward, not the answer), cost the PC anything, or be a threat during RELAX (forms tagged
`threat` are excluded from the roll then). *Worst case (J):* an awkward form — the same lead arrives
less naturally (class i); a source judged ineligible that was eligible — a less specific lead arrives,
still concrete and real (class i) [C:P16; R5 P-08, P-41; R6 B-R4; R4 R-12].

**12.8.3 The DM checks for a next step every beat.** `[J:flag]` Independently of the counter, after every
beat's CONSEQUENCE the DM runs 01.11.4's check — "does the player now have at least one concrete,
actionable option?" — and names one from state in the narration if the answer is not obvious. The counter
is the backstop for when this check passes on paper but play is going in circles. *Worst case (J):* the check
passes when play is circling; the inconclusive counter (12.8.1) fires lead injection after three beats
(class iv). [integration: 00.2.3 audit]

**12.8.4 The live-lead audit.** `[D]` + `[J:flag]` Handler `h.12.lead_audit` (`scene_end`, phase 7) checks
every active thread for **at least one live lead**: an unfound clue placement whose place or holder the
PC can reach from their current region, a pending proactive fallback, or a known NPC or place connected
to the thread that the PC has not yet tried (`[J:flag]` *"Has the PC tried this NPC or place for this
thread?"* — true only when a frame or scene in the log targeted it for this thread). A thread with no live
lead is marked `stalled` and its proactive fallback is queued to fire at the next `scene_start` (ch.11
owns the fallback, 11.5.7). The audit runs after ch.15's `h.15.placement_audit` (phase 6), so placements
that audit adds count as leads [integration: IR ch.15 to 12]. A thread with fewer than three clue placements in total is a
content defect: ch.11's or ch.15's generator adds placements until three exist, and a `rule_conflict`
ruling is logged — the Three Clue Rule enforced as an audit [R: https://thealexandrian.net/wordpress/1118/roleplaying-games/three-clue-rule;
R5 P-41; R6 B-13]. *Worst case (J):* a lead judged "tried" that was not — the thread's fallback fires a
little early (class i, P16-safe).

**12.8.5 The stuck answer.** `[D]` When the player says they are stuck ("what now?", "I don't know what to
do"), the DM answers OOF (format 12.15.10) with **two or three** concrete leads drawn from state — the
journal's open clues, active threads' live leads, NPCs with recorded wants, visible clocks — phrased as
examples and closed with "or anything else you have in mind". If state holds no live lead at all, the DM
fires lead injection at once (12.8.2) and narrates it. The stuck answer costs no time and does not reset
the inconclusive counter unless a lead is injected [R1 T-11].

**12.8.6 Options are examples, never menus.** `[N]` Whenever the DM names possible courses of action — in a
stuck answer, a redirect (01.3.6), or an open prompt — it frames them as examples of what is possible
("You could … or … — or something else entirely"), never as the complete option set, and never numbers
them as choices unless it is a genuine closed choice (a pause point: commit / change / withdraw; a
last-chance menu; a near-miss choice). Goal 1 forbids "the menu doesn't have that" [BRIEF §3; R1 T-11].

### 12.9 Spotlight for one player: the rotation ledger and challenge diversification

Multiplayer spotlight craft rotates attention among players every 10–15 minutes [R1 M-35]. With one
player, the spotlight rotates instead across the **pillars** of play, the **kinds of challenge**, and the
**facets** of the one character — what they can do, who they are, what they want [R1 12.B, #8, T-15;
R2 ch.12, #12; R5 X-01]. It must be engineered as a ledger, because "no source anywhere … shows a system
that gets these for free" [R1 12.B].

**12.9.1 The rotation ledger.** `[D]` + `[J:enum]` A background record of **scenes since each axis value was
foregrounded**, updated by `h.12.rotation_update` (`scene_end`, phase 9). Three axes:
- **Pillar** (closed: `conflict`, `exploration`, `social`, `investigation`, `travel`, `downtime` — the
  `situation` branches other than `rest`). At `scene_start` the DM classifies the scene's pillar `[J:enum]`
  by the mode and the agenda; at `scene_end` the engine overrides it with the branch that most of the
  scene's frames' situation tags carry, if any frames exist.
- **Challenge type** (closed list T-12-7, nine types; classified `[J:enum]` at `scene_start` for any scene
  with opposition; null otherwise): `terrain`, `cunning_foe`, `outnumbered`, `objective`, `clock`,
  `attrition`, `mixed`, `social_stakes`, `mystery`.
- **Facet** (one entry per item, created when the item is acquired): each recognized calling (04); each held
  ability, spell and training or language license (05, 02); each deed tag where the PC's competence is
  +2 or more (a specialty); each origin hook, aspiration and bond (02); each companion (16). A facet is
  **foregrounded** `[D]` in a scene when a resolved frame in it cited the license or ability, drew
  competence from the tag, or (for hooks, aspirations, bonds and companions) the scene's agenda or a
  delivered lead named it (`[J:flag]` at `scene_start`, citing the fact id). A facet never yet foregrounded
  is **untested**.
- **Challenge axes** (09.8.5, T-09-15): for each of ch.09's eight axes (`axis.numbers` … `axis.talk`), the
  scenes since a framed encounter last presented it, written from each encounter's axis flags at
  `scene_end`. They have no overdue threshold; only 09.8.5's complication draw reads them (reroll a result
  whose axis is not the stalest available) [revision: I-030].
*Worst case (J):* a pillar or challenge type misclassified at scene start — one counter resets wrongly,
corrected by the frames at scene end where frames exist (class iii).

**T-12-7 Challenge types** (canonical: `pacing.yaml#rotation.challenge_types`).

| Id | True only when the scene's main difficulty is… | False for… |
|---|---|---|
| `terrain` | the ground itself: footing, height, water, fire, darkness, choke points, cover | a fight that merely happens somewhere |
| `cunning_foe` | an opponent who plans, feints, retreats, uses the ground or sets traps | a straightforward brawl |
| `outnumbered` | more opposing bodies than the PC can face at once (a mob, a swarm, a patrol) | one strong foe |
| `objective` | something other than winning: protect, rescue, carry, stop a ritual, avoid bloodshed, get out | a fight to the finish |
| `clock` | a deadline: a visible countdown or racing clock decides the outcome | an untimed task |
| `attrition` | resources running out: supply, light, Focus, ammunition, rest | a single costly roll |
| `mixed` | two different kinds of opposition at once (a foe *and* a fire; guards *and* a lie to keep up) | one kind |
| `social_stakes` | a person must be moved, deceived or faced down under pressure, or a hard choice between people | a casual conversation |
| `mystery` | something must be figured out: a puzzle, a clue chain, a lock of logic | a search with nothing hidden |

**12.9.2 Overdue axes and how they are used.** `[D]` An axis value is **overdue** when its count reaches its
threshold (`pacing.yaml#rotation.overdue`): a pillar after **6** scenes; a challenge type after **6**
scenes with opposition; a facet after **8** scenes; an untested facet **4** scenes after it was acquired.
The ledger is used in exactly three ways, never more:
1. **Tie-break.** Whenever the DM chooses among eligible options that are otherwise tied — impetus
   candidates of equal rank (12.4.3), pacing-push candidates (12.7.4), lead-injection sources of equal
   rank, NPCs or objects drawn for an altered scene, the qualifier of a yes-but, ch.11's kicker candidates
   (11.4.5) [integration: IR ch.11 to 12] — it prefers the option
   that foregrounds the most overdue axis value (largest count relative to its threshold).
2. **Opportunity.** When an axis value is overdue, the next scene the DM frames whose impetus list reaches
   item (f) (12.4.3), or the next pacing push of kind (c) (12.7.4), puts **an opportunity** for it in
   front of the PC — Dungeon World's "give an opportunity that fits a character's abilities" [R:
   https://www.dungeonworldsrd.com/gamemastering/] — drawn from state (a thread, an NPC want, a place
   feature, a rumor) or from `tbl.vignette`'s opportunity rows filtered by the axis's tags. An
   opportunity is never a requirement: the player may ignore it, and nothing is forced.
3. **The OOF stuck answer** (12.8.5) lists the overdue axes' opportunities first among its examples.
The ledger never overrides the player's declared purpose, never creates content outside the closed
complication sources (01.11.3), and never changes any number.

**12.9.3 The player's weights.** `[D]` The check-in (12.5.9) answers scale the pillar thresholds: **more** →
half the threshold (3 scenes); **less** → double (12 scenes); **same** → unchanged. A pillar the player
marked *less* is still never removed: the sandbox does not hide whole pillars.

**12.9.4 Challenge diversification.** `[D]` + `[J:enum]` When the DM chooses content that creates opposition
(a pacing push, a bang among equals, the reading of a random event, a twist's form within its rolled row),
it may not choose the same challenge type as **both** of the last two scenes with opposition if an
eligible alternative exists. When escalation is permitted (12.7.5), the change of type is mandatory. The
response to a character who dominates is a different kind of problem — terrain, an objective, a clock, a
cunning foe — never inflated numbers [R1 #8, M-36; R2 #12]. *Worst case (J):* a scene's type misread so that
the same type repeats — one repeated kind of scene (class i).

### 12.10 Information: P17 in practice, knowledge gating, and sealed secrets

**12.10.1 Three layers of knowing.** `[D]` The DM keeps three layers distinct: **world truth** (the store,
including sealed and background state), **what the PC knows** (knowledge records, the journal — ch.15),
and **what the narration says** (only what the PC perceives now or knows). Narration is written from the
PC's point of view: second person, limited to the PC's senses and knowledge (12.14.1). A thing the PC has
not perceived or learned is not narrated, even if the DM's packet shows it as background (an off-screen
NPC's movement, a faction's plan). [R1 #12; R4 §5]

**12.10.2 Names and identities are knowledge.** `[D]` + `[J:flag]` An NPC's name, title, allegiance or
relationship appears in narration only after the PC has learned it (a `record_knowledge` entry: told,
overheard, read, recognized). Until then the narration uses a descriptor from what the PC can see ("the
grey-bearded ferryman"), chosen from the NPC's recorded appearance detail. *"Has the PC learned this?"* is
`[J:flag]`, true only when a knowledge record exists or the PC's origin or prior scenes make it common
knowledge (an Oracle Certain by scene logic). *Worst case (J):* a name used one scene early — the claim check
flags it as `knowledge` (class iv).

**12.10.3 Sealed secrets and permitted slices.** `[S]` + `[D]` The narrator's packet never contains sealed
content (INV-10). In its place it holds the item's **permitted slice** (00.6.5): tells, omens, a
qualitative band, or an **atmosphere tag** ("theme: betrayal by kin"). Rules of use:
1. A permitted slice may color *tone* (word choice, mood, what draws the eye), never assert an event or a
   fact. "The steward's smile does not reach his eyes" is tone from a tell; "the steward is the traitor"
   is a leak.
2. **No conspicuous avoidance.** The DM narrates around a sealed thing exactly as it would around an
   unremarkable one; pointedly refusing to describe something leaks it too [R4 §5.1: "active hiding"
   made avoidance itself detectable].
3. **Unseal before narrate.** Sealed content enters narration only through `unseal` at its gate — a
   frame's delivered item unlocking a clue node (ch.15), the PC entering the place, an NPC deciding to
   confide (a resolved Talk frame or a recorded want), a clock completing — and the `unseal` call
   happens at RECORD, before the draft.
4. A secret frame's result (01.4.7) is narrated only as what the PC perceives; a failed secret search and
   a search with nothing to find read the same (01.15.6).
*Worst case:* none for (3) — `[D]`; a tell used as a fact is caught by the claim check as `leak` (class iv).

**12.10.4 Graduated delivery, narrated.** `[J:enum]` + `[N]` For a bundled beat (01.10), after `deliver`
returns the count:
1. **Which item answers** `[J:enum]`: for each delivered item (in the player's rank order), the DM picks
   the **permitted** content that answers it — a clue node the frame's degree unlocks, a fact in the
   store, a tell — preferring, in order: the content that most directly answers the item as asked; then
   content that **leads onward** (a node with unfound outbound placements); then the node with the most
   remaining placements (keeping the Three Clue Rule's redundancy for later). Never content that is not
   permitted.
2. **Delivered items** are narrated plainly, as what the PC perceives or works out ("Iron makes it flinch;
   you saw that at the gate").
3. **Undelivered items** are acknowledged as *open*, never answered wrongly and never ignored ("Whether it
   thinks, you can't tell yet"). They remain open questions; re-asking follows 01.10.6.
4. **Failure** gives one vague impression of the top-ranked item; **critical failure** gives nothing
   reliable, and a plausible falsehood only when the observed source can mislead (01.18.5 `misleadable`),
   written as a *belief* fact (`certainty: believed`, `truth: false`, sealed truth).
*Worst case (J):* a less useful but true item chosen — the player still receives the delivered count of
true answers (class i) [C:P17; R4 §5.2 item 3; R1 #12].

**12.10.5 What the PC learns is written.** `[D]` `record_knowledge(pc, fact, how)` is written at RECORD for:
every delivered item; every fact narrated as perceived that the PC could later cite (write-on-mention
covers the entity; knowledge covers the PC's awareness of it); every name learned; every rumor heard
(`rumor` id; its truth stays sealed). The journal (ch.15, `available`) is the render of these records,
and is the only source for answering "what do I know about X?" (besides the PC's origin knowledge, which
is a free Recall of established facts, 00.12.6).

**12.10.6 NPC knowledge.** `[J:flag]` + `[D]` An NPC knows a fact only when one of these is true (first
match): (a) a knowledge record says so; (b) the NPC is in the `witnesses` of the beat or event that
established it; (c) the fact is public in the NPC's scope (ch.11 reputation, news and rumors that reached
their place); (d) the fact is common knowledge of the NPC's role or origin (a harbor master knows the
tides) — `[J:flag]` *"Would anyone in this role know it?"*, uncertain → the Oracle, Likely for facts of
their trade, Unlikely otherwise. **An NPC acts only on what it knows** — no NPC reacts to the PC's secret
plan, hidden identity or off-screen deed unless one of (a)–(d) holds. Updates `[D]`: when the PC tells an
NPC something (SPEECH or Talk), `record_knowledge(npc, claim, how: told)` — being told is not believing
(ch.15's claim plausibility decides belief); when an NPC witnesses a beat, a record per witness; when news
spreads, ch.11's rumor propagation writes records by scope. *Worst case (J):* an NPC credited with
knowledge it lacked — one NPC response built on it; the claim check's `knowledge` class flags the
narration (class iv) [R1 #12; R4 W7].

**12.10.7 Tells, not stats.** `[N]` Adversary and NPC states are voiced only through their **tells** (ch.09
data), the shown descriptors (`bloodied`, `down`, visible conditions), and standing as behavior (12.14.7).
"He's down to 3 Vitality" is forbidden; "he's bleeding freely and his guard is dropping" is a tell from the
`bloodied` descriptor and a visible condition. Threat is voiced before a fight through the tells of the
adversary's band (T-09-13) [revision: I-030] and, when `threat_advisory` is *hard* or *lethal*, through the lethal warning's plain
words (ch.07) [R4 §5.2 item 2].

### 12.11 NPCs: generation, reaction, voice, decisions, and memory

**12.11.1 Generating an NPC.** `[D]` + `[J:enum]` Any person narrated as addressable is written on mention
(00.6.6). Before generating, the DM checks the region's cast (the seed's `npcs`, 12.16.11) and the cast list for an existing person
who fits (`[J:flag]` *"Does an existing NPC's role and place match this mention?"* — true → use them).
Otherwise the NPC is generated in three depths, each promoted `[D]` by a trigger, each field rolled and
written at once, never chosen (`data/oracles.yaml`; a region's tables replace the generic ones when they
exist: the seed's name tables always, 12.16.7) [R5 NP-01, P-04 (UNE), P-06; R4 SG-12]:

| Depth | Written when | Fields (table) |
|---|---|---|
| **Walk-on** | first mention as addressable | id; **role** (as the narration implies it — "the innkeeper" — else `tbl.npc_role` by place tags); **name** (region table, else `tbl.name_given` + `tbl.name_family`); **gender and pronouns** (`tbl.npc_gender`, region override allowed); **age band** (`tbl.npc_age`); **one distinctive detail** (`tbl.npc_detail`); **demeanor** (`tbl.npc_demeanor`) |
| **Recurring** | the PC interacts with them in a second scene; a Talk frame targets them; or they are named in a lead or thread | + **want** (`tbl.npc_want_verb` × `tbl.npc_want_object`); **fear** (`tbl.npc_fear`); **voice** — register (`tbl.npc_voice_register`) and habit (`tbl.npc_voice_habit`); **one refusal** (`tbl.npc_refusal`; semantics ch.15); **knowledge scope** (role and origin, 12.10.6) |
| **Principal** | they become a thread node or linchpin (11), a companion (16), or a faction officer (11) | + **secret** (Oracle Even "does this person keep a secret that matters here?" → if yes `tbl.npc_secret`, written **sealed** with a gate); **three ranked wants** (two more rolls, ranked in roll order — UNE's ranked motivations); **ties** (Oracle per candidate faction or NPC by role: Likely for their own trade's institutions, Unlikely otherwise) |

**Home and membership.** Every generated NPC is written with `home` (the place it lives; its settlement scope)
and `member_of` (its faction ties: none unless its role or a tie roll names one), which ch.03's scopes and
ch.11's World Turn read (11.1.2) [integration: IR ch.11 to 12]. When a recognition offer staged by V2 (a mentor)
or V12 needs a person the cast does not hold, the lead engine places one with the role tags the vehicle names
(04.7) [integration: IR ch.04 to 12].

**The pronoun rule.** Gender and pronouns are rolled at walk-on because narration needs them immediately —
the project's own probe introduced an unearned pronoun that its self-assessment missed [C:P13]. A
pronoun never appears in narration for an NPC whose gender is not in the store; until then the narration
uses the role or descriptor. *Worst case (J):* a role read from the narration more specifically than meant
("the innkeeper" vs "a serving-man") — one walk-on field, corrected by the next mention's claim check
(class iv).

**12.11.2 The reaction roll: starting standing is rolled, never chosen.** `[D]` + `[J:flag]` At an NPC's
**first interaction** with the PC (the PC addresses them or they address the PC), the engine sets their
standing toward the PC (00.3.16: −3 Hostile … +3 Devoted). **Exception:** a bond NPC (02.9.2) is generated at
depth recurring with the standing creation **set** (anchor or thorn), never rolled, because a bond is not a
first impression [integration: IR ch.02 to 12] [R6 §B.3 B-R2; R5 AV-07 (the
B/X and Worlds Without Number 2d6 reaction roll)]:
1. **Faction members** (00.17.1 Q13): base = the faction's status toward the PC; then
   `tbl.npc_reaction_member` (2d6: 2–4 → −1; 5–9 → 0; 10–12 → +1) for the individual (16.7% / 66.7% /
   16.7%); clamped −3…+3. (Ch.15 owns standing's meaning; this is the one individual step Q13 allows.)
2. **Everyone else**: `tbl.npc_reaction` (2d6) **+ reaction modifiers**, each a `[J:flag]` citing a fact,
   +1 or −1 each, total clamped to ±2:
   - +1 the PC's reputation in this scope favors people like this NPC (ch.11 reputation content) / −1 it
     disfavors them;
   - +1 the PC shares the NPC's origin, faith or trade (a fact on both) / −1 the PC belongs to a group the
     NPC is recorded as hating;
   - +1 the PC arrives as someone this NPC welcomes (customer, guest, rescuer) / −1 as a threat (visibly
     bloody or armed for violence, trespassing on the NPC's ground, or the NPC is under threat from
     someone like the PC).
   Result: ≤ 2 Hostile (−3); 3–4 Unfriendly (−2); 5–6 Wary (−1); 7–8 Neutral (0); 9–10 Warm (+1); 11 or
   more Friendly (+2). **Devoted is never a first impression.**
3. `set_relationship(npc, pc, standing, reason: reaction roll)`; the rung name is `available` to the
   player; the number never appears in fiction.
4. **Adversaries** met outside a fight roll only if their ch.09 archetype allows a reaction (its field
   `reaction_roll: true`, distinct from ch.06's combat `reaction`; intelligent, not on a hunt); otherwise
   their behavior list decides [integration: IR ch.09 to 12; DL-09-19].
Distribution (T-12-12, exhaustive): with no modifier — Hostile 2.8%, Unfriendly 13.9%, Wary 25.0%,
Neutral 30.6%, Warm 19.4%, Friendly 8.3% (mean −0.25: strangers in a classic-fantasy world are a little
guarded); at +2 — Unfriendly 2.8%, Wary 13.9%, Neutral 25.0%, Warm 30.6%, Friendly 27.8%; at −2 —
Hostile 16.7%, Unfriendly 25.0%, Wary 30.6%, Neutral 19.4%, Warm 8.3%. *Worst case (J):* one modifier
wrongly applied — the 2d6 total moves by 1, changing the rung in about a third of rolls by one step
(class i), and the cited fact is auditable [DL-12-10].

**12.11.3 Voice.** `[N]` + `[D]` A recurring NPC's dialogue keeps their recorded **register** (closed list of
eight: formal, plain, rough, flowery, terse, nervous, jovial, cold) and their **habit** (one recorded
speech habit — a saying, a way of addressing people, a tic of rhythm), used at most once per scene so it
stays a signature rather than a joke. What the NPC calls the PC follows knowledge (their name only once
they know it) and standing (12.14.7). Dialogue reveals only what the NPC knows (12.10.6) and never voices
a mechanic. Voice is the DM's free craft — "give every creature life" [R: https://www.dungeonworldsrd.com/gamemastering/];
**decisions are not** (12.11.4–12.11.5) [R4 S3 vs W4].

**12.11.4 NPCs can say no.** `[D]` An NPC's compliance comes only from: a resolved Talk frame's delivered
outcome (ch.15); a recorded want the request serves; or `tbl.npc_action` for requests that meet no
resistance. A recorded **refusal** is honored unless a frame's delivered reach overcomes it under ch.15's
rules; an NPC at Unfriendly or Hostile does not volunteer help. An agreeable-sounding NPC who nonetheless
refuses is correct play, not unkindness: LLM-voiced characters are measurably biased toward engagement and
agreement, and the remedy is pre-committed state [R4 W4; R: https://arxiv.org/abs/2606.20708].

**12.11.5 NPC decisions when nothing else decides.** `[D]` + `[J:enum]` When an NPC must act and no frame,
want, refusal or behavior list settles what they do (12.2.9 (2c)), the engine rolls `tbl.npc_action`: d10
+ the NPC's standing toward the PC, clamped 1–10. Rows: 1 escalates (threatens, calls for others, attacks
only if able and the row's tag allows); 2 ends the exchange and withdraws; 3 hinders quietly (delays,
misdirects); 4 wants something first (names a price); 5 carries on with their own business; 6 acts on
their own want; 7 asks the PC something; 8 offers partial help; 9 helps as asked; 10 helps beyond what was
asked. The DM chooses the words and, `[J:enum]`, which of the NPC's recorded wants or traits the row
expresses. A row never overrides a recorded refusal and never resolves something a frame should resolve
(a request the NPC would resist is a Talk beat, not a table roll). Whether an NPC **lies** is never a row:
15.6.2's reason-to-lie flag decides it first, from a cited field of the NPC's record; no reason → it tells what
it knows within T-15-1's *share* row [revision: I-030]. *Worst case (J):* the row expressed
through a less fitting want — the same weight of response (class i) [R5 P-06].

**12.11.6 Standing moves only in steps from sources.** `[D]` Standing changes only through: a Talk frame's
delivered reach (ch.15); a cost (`cost.closed_door`, 01.13.9); a deed the NPC witnessed or heard of whose
memory valence ch.15 maps to a step (T-15-2) [revision: I-030]; ch.11's faction status changes for members. Never because the DM
feels the NPC "would warm up" (00.3.16; SG-02).

**12.11.7 NPC memory of the PC.** `[D]` + `[J:flag]` Each NPC keeps **memories** of the PC (Hades' and
Valve's "characters remember your specific history" [R6 B-19]):
- **Written** `[D]` at RECORD (`h.12.npc_memory` commits at `scene_end`) when: a beat targeting the NPC
  resolves; the NPC witnesses a beat involving them, their kin, allies or property; a promise, debt or
  oath involving them is recorded; their standing changes. Fields: `{npc, time, deed (neutral
  restatement, 01.2.6), valence, salience, how (did|witnessed|told)}`. **Valence** (closed): helped,
  harmed, lied_to, caught_lying, impressed, insulted, owed (the PC owes them), owes (they owe the PC),
  promised, betrayed, spared, threatened. **Salience** `[D]`: 3 when their standing changed or harm or a
  cost touched them; 2 for a promise, debt, or a lie detected; 1 otherwise.
- **Active memory cap**: at most **5** active memories per NPC, kept by salience then recency; older ones
  are archived, queryable, never lost (Thousand Year Old Vampire's bounded memory, used here as the
  state-summarization pattern it models [R5 P-42]).
- **Used**: when the NPC is present, their active memories are in the packet. At their first line in a
  scene `[J:flag]` *"Does one of this NPC's active memories bear on this exchange?"* — true when it
  involves the same place, the same people, an open promise or debt, or salience 3. If true, the first
  line acknowledges the **most specific** relevant memory (same deed > same people > same place >
  highest salience). Narration may never contradict a memory (claim class `knowledge`/`attitude`).
*Worst case (J):* a relevant memory not voiced — a flatter greeting, no state effect (class i); a memory
voiced that the NPC should not have (told vs witnessed) is caught as a `knowledge` claim (class iv).

**12.11.8 NPCs off-screen.** `[D]` What NPCs do while the PC is elsewhere is ch.11's World Turn and
situation timelines. When the PC returns, the NPC's record reflects those results and nothing else; if the
DM needs to know something the World Turn did not settle ("is she still at the mill?"), it asks the Oracle
with a time scope (01.15.7) — it never invents an off-screen life.

### 12.12 The ruling ledger in use

**12.12.1 When the DM consults precedent.** `[D]` `find_rulings(anchor_id, deltas, tags)` is called
(INV-19; 01.5.2) before: any anchor adaptation with deltas; any Oracle question (the DM's or the
player's) — so the same kind of question in the same kind of place gets the same odds; any Good Idea; any
G3 or G4 decision; and, added here, any **scene-logic answer** (Certain or Impossible by scene type) to a
player's G0 question, because "a smithy has a quench trough" is a ruling the next smithy should share.

**12.12.2 Reuse and departure.** `[D]` + `[J:flag]` A matching precedent's numbers are reused (01.5.2). The DM
departs only when an established fact present now and absent then (or the reverse) changes the tier, the
stakes, the reach, or the odds rung, and it names that fact's id in `precedent.differing_fact`. "This time
feels different" is not a fact. A difference that is a lever or snag is applied as a lever or snag on the
reused frame, not as a departure (WE-00-9). *Worst case (J):* a reuse where a fact differed — the player can
cite the fact and a new ruling supersedes (class iv).

**12.12.3 Two precedents disagree.** `[D]` The later record wins (00.1.4: latest write), unless the later one
departed citing a fact that is absent now — then the earlier one applies. Either way the conflict is
logged with `review_flag: true`.

**12.12.4 Review flags and Principle III's revisit trigger.** `[D]` `review_flag` is set by 01.5.4's
conditions and also on: every correction (12.3.4); every plain fallback (12.3.3); every upheld dispute
(12.3.6); every breach of 12.1.3 detected by a sweep. At `session_end`, `h.12.session_close` compiles the
session's flagged records into the **review list**. When **three or more** flagged records in which the
DM's own judgment was overturned (a correction, an upheld dispute, or a ruling-error correction) share an
error class — the same anchor id, the same claim class, or the same 12.1.3 breach — across **two or more
sessions** (`pacing.yaml#review.iii_candidate`), the class is reported as a **Principle III candidate**:
the "recorded, concrete failure case" the constitution requires before an exception-gating mechanism may
be considered [C:III]. The report is evidence for the project's maintainers; it changes nothing in play.

**12.12.5 The player may see the ledger.** `[D]` Rulings are `available` (00.6.3). "How was this ruled
before?" is answered with the matching record in format 12.15.8. Seeing that the same case gets the same
answer is part of what makes rulings legible as the game rather than the DM's whim [R4 §7.3].

**12.12.6 Precedents that recur become rule proposals.** `[D]` A ruling reused **three or more** times
without departure is listed in the review list as a **rule candidate**: a recurring adaptation that may
deserve to become a written anchor card or sub-rule (entering as `provisional` under VI). The DM keeps
applying the precedent meanwhile [C:VI; R7 §4.8].

### 12.13 Improvising from the substrate

**12.13.1 Hook first, then primitives.** `[J:enum]` When a player does something no rule names, the DM
(i) restates the beat neutrally — method, target, intended change (01.2.6); (ii) retrieves anchors for it
(12.13.2); (iii) picks one (01.5.1); (iv) checks precedent (12.12.1); (v) adapts at most two knobs
(01.5.3); (vi) frames and offers. The same order serves improvised *content* (12.13.4): start from what the
thing is for in the fiction, then express it only through existing primitives — Sanderson's "begin from
the hook, then formalize into the grid" [R2 ch.12; C:P3]. *Worst case (J):* a near-but-wrong anchor is picked;
the two-change limit bounds the adaptation, and the logged signature lets a later beat depart from it by
naming the differing fact (00.15.3, 00.15.6; class iv). [integration: 00.2.3 audit]

**12.13.2 Retrieval from the anchor index.** `[D]` `load_cards(anchors for verb, deed tags, situation)`
queries `data/anchors.yaml` and returns at most **eight** candidates (00.15.3), scored: **+3** per intent
verb matching the beat's restated method or intended change; **+2** when an anchor's deed tag equals the
beat's primary deed tag or is its ancestor; **+1** per matching situation tag; the gated basic verb's own
card (or the G2 license's own rule) is always included regardless of score; ties broken by specificity
(a chapter sub-rule over a license rule over a verb card) then rule id. *Runtime capability:* RC-RETRIEVE,
RC-QUERY.

**12.13.3 The two-change limit, the third change, and splitting.** `[D]` + `[J:enum]` An adapted ruling
moves at most two knobs (00.2.7). When a third change is needed, `[J:enum]`:
- **Re-anchor** — true when another candidate needs two or fewer changes for this beat; use it.
- **Split** — true when the beat holds more than one of: a distinct **method** (swing *and* kick), a
  distinct **target** (the rope *and* the archer), a distinct **intended change** (get across *and* knock
  him down), or a **sequence** (one must happen before the other can). Split into sequential beats
  (01.14.1), each anchored separately; their order is the fiction's order.
- Default when both seem possible: split (each part becomes simpler and is logged on its own).
*Worst case (J):* a split that could have been one adapted beat — two rolls instead of one, each shown at
OFFER (class ii) [R7 §3.4; 01.5.3].

**12.13.4 Improvised content uses existing primitives only.** `[D]` + `[J:enum]` A new hazard, an NPC's
unusual ability, a location's strange property, a trap, an improvised item's effect: each is built from
the substrate — effect ids from `data/effects.yaml` with parameters, conditions from `data/conditions.yaml`,
a clock, a license, a hazard or trap entry, a generator output — never as a prose-only mechanic
(00.16.4). The DM picks `[J:enum]` the nearest existing entry and moves at most two parameters (the
two-change limit applied to content). If nothing fits within two changes, the DM uses the nearest entry
unchanged, logs a `rule_conflict` ruling with `review_flag`, and the review list carries an extension
proposal (PR-00-8). *Worst case (J):* a less apt primitive — its stated numbers apply, inside the
substrate's caps (class i/iv).

**12.13.5 Every improvisation is logged.** `[D]` A beat or content improvisation writes a `RulingRecord`
(00.15.5) with its signature, cited facts and result; the ledger is what makes the next identical case
come out the same (12.12).

**12.13.6 The anchor index: compilation spec for `data/anchors.yaml`.** `[D]` Ch.12 compiles the index
from every chapter's anchor cards; no chapter edits it by hand.
1. **Sources**: (a) the `anchor:` fields of `data/basic_verbs.yaml` (the fifteen verb cards, 01.18); (b)
   every rule in chapters 01–16 whose template says `Anchor: yes` (00.2.6), from the chapter's rule card
   (00.15.2 `anchor` block); (c) data entries that declare an `anchor` block (a hazard, an activity, a
   ritual) in their own files.
2. **Entry** (SCHEMAS `anchors.yaml` plus the common envelope): `id` (`anc.` + the rule id with dots as
   underscores, e.g. `anc.01_18_4`; Interface request to 00 for the `anc.` prefix), `name`, `rule_id`,
   `source` (file and key), `intent_verbs`, `deed_tags`, `situation_tags`, `knobs` (from T-00-20 only, each
   with `default` and `allowed_deltas`), `degree_table` (a reference, never a copy), `specificity`
   (`verb_card` | `license_rule` | `chapter_rule`), `tags`, `lifecycle` (the source's), `basis`.
3. **Validation** (the compile fails on any): the rule id exists; every knob is in T-00-20; at least one
   intent verb; every deed and situation tag exists in `data/tags.yaml` (or is listed as pending in an
   Interface request); the degree table reference resolves; no two entries share an id.
4. **Derived fields**: `deed_tags` and `situation_tags` for verb cards are taken from the compile map in
   `anchors.yaml#compile.verb_tag_map` (the deed branches and situations where each verb is the usual
   method); a chapter rule's are taken from its card's `deed_tags` and `loads_in`.
5. **Recompile** whenever any source changes; the index is versioned (`schema_version`, `compiled_from`
   with each source file's revision) so old ruling records still resolve their `rule_id`.
6. **Lifecycle**: an anchor whose source is retired is kept with `lifecycle: retired` and `superseded_by`
   (00.16.3); retrieval skips retired entries.
This chapter ships the index seeded with the fifteen verb cards, compiled from `basic_verbs.yaml` as
ch.01 wrote them.

### 12.14 The narration standard

**12.14.1 Voice and point of view.** `[N]` Narration is **second person, present tense**, addressed to the
character ("You step onto the landing"), limited to what the character perceives and knows (12.10.1).
The player is addressed only in OOF blocks (12.15). Classic-fantasy register: concrete nouns, physical
detail, no modern idiom, no meta-commentary ("in this scene", "your turn") inside the fiction.

**12.14.2 No unestablished details.** `[J:flag]` + `[D]` Every detail in narration is either **established**
(in the store, or written this turn by a legitimate source) or **generic atmosphere** — not addressable,
not citable later (the smell of rain, the color of the dusk sky, the general murmur of a market). The test
for each concrete detail: *"Could the player cite this later as a fact — a lever, an obstacle, a target, a
clue, a person, a thing to take?"* (00.6.6). True → it must be in the store before the narration is
delivered (write-on-mention), with only the properties the narration implies; properties it needs that are
unsettled go to the Oracle or a table first. The categories where invention slips in most often, each
always checked (12.3.1):
- **identity** — names, gender and pronouns, ages, kinship ("her brother"), titles, professions, species
  (the probe's unearned pronoun, constitution P13);
- **counts** — of coins, arrows, guards, doors, days;
- **states** — locked, lit, broken, poisoned, asleep, alone;
- **properties of things** — what an item does, what a material resists, what a creature fears (the
  probe's invented cold vulnerability, BRIEF §7; SG-15);
- **motives and knowledge** — why an NPC does something, what they know (12.10.6).
*Worst case (J):* an addressable detail treated as atmosphere — caught by the claim check as
`new_element`, and written or cut (class iv). *Example inside:* "A coil of rope hangs by the door" →
addressable (it could be taken, used as a lever) → `create_entity(obj.rope_…)`. *Outside:* "Rain needles
the river" → atmosphere, unless the scene's weather is not yet written (then the weather is state, ch.10,
and is read, not invented). *Non-example:* "The guard — a big man — blocks the stair": "man" is identity;
if the guard's gender is not in the store, the walk-on roll comes first (12.11.1).

**12.14.3 The player owns the character.** `[D]` + `[J:flag]` The narration never gives the PC words,
decisions, feelings, beliefs or actions the player did not state. It may describe: what the PC perceives;
the physical results of resolved outcomes ("your foot slides on the wet stone" — a footing cost's form);
sensations that a resolved effect licenses (a `cond.frightened` instance: "your heart hammers and every
step toward the beast is lead" — describing the condition, while what the PC *does* stays the player's).
`[J:flag]` *"Did the player state this, or does a resolved effect produce it?"* False → cut it (claim
verdict `pc_agency`). Quoted PC speech is only the player's own words, lightly tidied for punctuation,
never extended. *Worst case (J):* one sentence of imposed interiority — cut by the claim check, or disputed
and corrected (class iv) [R1 #3 (input fidelity); R4 §7.3 (locus of control)].

**12.14.4 No mechanics in the fiction.** `[D]` No number from the rules (Vitality, Focus, fate, DCs, totals,
degrees, standing values, ticks, bands, tiers, odds) and no rules term (T-00-22) appears in narration or in
any in-world voice. **Physical counts** of things the character can see or count — "your last two arrows",
"three riders" — are fiction, not mechanics, and are allowed when they match the store. Every mechanical
number belongs in an OOF block (12.15). The vocabulary of T-12-10 gives the in-fiction words for the PC's
condition, an adversary's state and an NPC's standing.

**12.14.5 Recognition without an announcer.** `[D]` Growth is voiced by the world, never by an in-world
announcer of mechanics (BRIEF §4; 00.1.7). Forbidden in narration (closed list): "you gain …", "you have
unlocked …", "your skill increases", "level", "experience", "class", "achievement", stat names spoken by
anyone in the world, bracketed or boxed text inside the fiction, any disembodied voice announcing a
change. Recognition is staged through ch.04's vehicles — a mentor's acknowledgement, a title others start
using, an oath sworn, an order that seeks the PC out, a power that wakes in a crisis — and its
accept / decline / defer choice is put to the player in an OOF CHOICE block (12.15.6) [R6 §A.4–A.5;
R2 #14 ("narrate milestones; the codex holds the crunch")].

**12.14.6 Describing positions in text.** `[D]` + `[N]` Text has no map, so position must be said (R5 EX-14):
1. **Scene openings** name what the PC can see that matters for movement and danger: exits, cover,
   elevation, hazards, and anything within reach (each written on mention).
2. **In conflict**, at `conflict_start` and in every narration in which any range band or positional flag
   involving the PC changed (01.12.2 obliges naming every change), each participant's band to the PC is
   stated in the fixed words of T-12-11, and any flag on the PC.
3. **Distances** are given as bands, not feet, unless an established fact states a measure (a 20-ft
   wall).
*Narration may not imply:* a band or flag the store does not hold (claim class `position`).

**12.14.7 Tells, omens and moods.** `[N]` + `[D]`
- **Omens** (INV-14): each tick of a sensed or hidden clock renders, in that turn's narration, the omen
  entry the engine selected — as a perceivable trace the PC could notice (a sound, a sign, a changed
  behavior, a rumor) — in the DM's words, never explained ("a dog barks twice somewhere below", not "the
  alarm is spreading"), never more than one per tick, and never one without a tick.
- **Tells** voice adversaries and NPCs instead of numbers (12.10.7).
- **Tension and intensity** are never named; they may color the world's mood (weather already rolled,
  crowds, the quality of silence) only through elements already in the store.
- **Standing** is voiced as behavior, by rung (T-12-10): Hostile — open enmity, refuses dealings; Unfriendly
  — curt, suspicious, unhelpful; Wary — guarded, measured, gives little; Neutral — businesslike; Warm —
  friendly tone, small courtesies; Friendly — goes out of their way; Devoted — would take risks for the PC.

**12.14.8 Failure is the world's answer.** `[N]` A failure is narrated as the world responding — the guard
turns at the wrong moment, the hasp holds, the current is stronger than it looked — and the chosen cost's
form is named plainly (01.12.2). A success is narrated as the character's doing. Neither is softened nor
sharpened beyond the frame: the degree, the delivered reach and the cost are exactly as resolved (01.7.2)
[R5 P-16; R2 ch.12 ("failure moves the plot forward")].

**12.14.9 The open prompt.** `[D]` Every DM response that is not a pause point ends by handing the moment
back to the player: a direct question to the character ("What do you do?" or a situation-specific one:
"The ferryman holds out his hand. Do you pay?") or an unresolved image that plainly awaits a response.
Never a numbered list of options; examples only under 12.8.6. Pause points end with their own OOF block
instead (12.15).

**12.14.10 Length.** `[D]` Narration word limits (`pacing.yaml#narration`), excluding OOF blocks: a beat's
narration ≤ **200** words; a conflict turn ≤ **150**; a scene opening ≤ **200**; a recap ≤ **120**; a time
skip ≤ **150**. Longer only when the player asks ("describe it in detail"). Short narration is also a
consistency measure: every sentence is a claim to check [R1 12.A (narration quality decays through
repetition); R4 W11].

**12.14.11 Freshness.** `[J:flag]` + `[D]` The engine keeps the opening clause of the last three scene
openings and, per entity, its last ten distinctive images (a simile, a striking descriptor). The DM does
not reuse an opening pattern from the last three scenes (`[J:flag]` *"Does this opening start the same way
— same time-of-day or weather lead, same sentence shape?"*) and does not repeat a distinctive image for the
same entity within ten turns, except a deliberate callback (an NPC's recorded habit; a recurring omen;
the player's own phrase). *Worst case (J):* a repeated phrase — harmless (class i) [R4 W10; R1 12.A
(RPGBench's interestingness decay from repetitive narration)].

**12.14.12 What every narration must name.** `[D]` (from 01.12.2, restated so this card stands alone)
Every visible condition applied this turn; one omen per sensed or hidden clock tick; every changed range
band or positional flag involving the PC; the form of every cost paid; every NPC response produced by
12.2.9; and every lead injected. Missing any of these is a claim-check failure of the sweep (12.4.8).

**12.14.13 What narration may create.** `[J:flag]` + `[D]` Write-on-mention lets narration bring **ordinary
scene furniture** into being: the things any such place has, with ordinary properties (a rope by a
door, benches in a hall, a fishwife at the market, a puddle, a woodpile). Narration may **not** create, by
mention alone, anything that functions as: a **clue** toward a sealed fact or an open thread (clues come
only from clue graphs and their placements, ch.15/11); an **item of more than common value** or any
property beyond the mundane (items come from the generator or the region's data, 00.11); a **hazard**
or **trap** (ch.10 tables); an **adversary** (encounter tables, clocks, behavior lists); or a **person with
a want, a secret or knowledge of a thread** (NPC generation and the clue graph, 12.11.1). `[J:flag]`
*"Would this element, as described, help or hinder the PC beyond what any such place ordinarily offers, or
point toward something hidden?"* True → it must come from its owning procedure or be cut. Uncertain →
true. *Worst case (J):* an ordinary-seeming element that turns out useful is written — it is an
established fact the player may cite as a lever, worth at most +2, one stakes rung or one reach rung
(00.3.9; class i). *Example inside (furniture):* "a coil of rope hangs by the boathouse door" at a ferry
landing. *Outside (a clue):* "the ferryman's boots lie by the hut, laces cut" when the ferryman's fate is a
sealed thread — cut it. *Non-example:* "a gleaming sword hangs over the hearth" in a poor fisher's hut — an
item of value; if the DM wants to know what hangs there, it rolls the region's furnishings or the loot
generator.

### 12.15 Out-of-fiction message formats

Every number, odds, choice and rules matter goes in an **OOF block**: a line or short block that begins
with a bracketed label, set apart from the fiction, never written in a character's voice. Ch.14 owns how
blocks are rendered for the player (`codex.yaml#offer_marker`); these are the contents and the default
text form. Order within one DM response: (1) SAFETY and SESSION acknowledgements; (2) CORRECTION blocks;
(3) the fiction; (4) RESULT blocks in beat order; (5) REDIRECT blocks; (6) one pause block last (OFFER,
NEAR MISS, CHOICE, CLARIFY, FLAG, CUT?) because it awaits the player.

**12.15.1 General rules.** `[D]` OOF blocks are terse, use ids and canonical names, show only `shown` and
`available` state (never background or sealed values: a hidden clock appears as nothing, a sensed clock
by name only), and never contradict the store. A block's fields appear in the order given below; empty
fields are omitted.

**12.15.2 OFFER** (renders 01.7.1 items 1–7, exactly). One line of fiction first ("The hasp is old iron in
older oak; the bar in your hands would do it — loudly."), then:

```
[OFFER] Break the hasp with the iron bar — verb.force (Force), anchor 01.18.10
  Mode: normal
  Roll: Might +1 · competence +1 (deed) · edge 0 · lever +2 (obj.iron_bar_03: Precision) · status 0 = +4
        (no other method here uses a higher attribute)
  Against: DC 15 — stored on door_archive.hasp (Moderate)
  Need: 11+ on the die · 50% success or better · crit success 5% · crit failure 5% · near miss 15%
  Stakes: Risky — failure: Exposure (S2) · crit failure: Exposure (S3)
          near miss: succeed and pay Exposure or Time (S2), or fail
  Reach: Standard — success: the hasp breaks · critical: it breaks, and you can follow up at once
  Costs: 1 action · 1 interval · loud (heard by anything listening) · rides: no · fate 1
  → commit · change · withdraw   (one trade: go big / play it safe)
```
Variants: a **lethal** frame adds, directly under Stakes, `THIS CAN KILL YOU — <source> (warned <when>)`; a
**secret** frame shows `Against: hidden` and omits the Need line's numbers ("the roll is hidden; you'll
see only what you perceive"); a **stretch / emulate / fallback** shows `Mode:` with its price on its own
line (`Mode: fallback (crude) — DC +5, reach capped at Standard, loud`); "only a natural 20" replaces the
Need line when it applies ("only a natural 20, and at best a plain success"); a **bundled** beat adds
`Rank your questions:` with the deduplicated items. An **ability activation** names its prices on the Costs
line: `Focus 2 (flared hard) · uses 1 of 2 left` and, when the Focus is short, `overdraw: <its price>` (05.6.6;
never automatic); a power used **through a relic** adds its own line under Costs, `Relic surcharge: +1 Focus
(no training license)` (08.4.4) [revision: I-030]. A frame resolved under **auto-commit** shows the same
block, labelled `[OFFER — auto]`, immediately above its RESULT.

**12.15.3 RESULT.**
```
[RESULT] d20 9 → 13 vs 15 · failure (near miss)
```
followed, after the player's choice or when no choice exists, by the changes to shown state:
```
[RESULT] Changed: Vitality 12 → 9 · bleeding (S1) · arrows 6 → 5 · Focus 4 → 3 · fate 1 → 2
```
A drop is one line of fiction (08.3.13); its `Changed:` entry names the item only, and its rung, known
properties and price are in the codex [revision: I-030]. A secret frame: `[RESULT] hidden check made.` Hidden and sensed clocks never appear; an Oracle answer
never appears (the oracle log is background, 00.6.3); a delivered bundled count appears as `Answered 2
of 4: <items>`.

**12.15.4 NEAR MISS** (pause point 4).
```
[NEAR MISS] 13 vs 15. Succeed and pay one — (a) Exposure (S2): <its form> · (b) Time (S2): <its form>
            — or (c) let it fail (Exposure S2 applies).
```

**12.15.5 REDIRECT** (G3 and G4; under the fiction's four-part redirect, 01.3.6).
```
[REDIRECT] G3 — checked lic.training.lockwork (not held).
  Possible now: break it (verb.force; ask for odds) · find another way in
  Learn it: a locksmith or a thief could teach you (mentor) · urban origins know it · recognition (deed.guile.thievery)
```
```
[REDIRECT] G4 — npc.tam_harlan.siblings = two brothers, no sister (established).
  Possible now: play it as a drunk's joke · tell him the truth · something else
```

**12.15.6 CHOICE** (pause points 6–9: last-chance menu, yield terms, recognition and institutional offers,
`chosen` fills, rewind and correction choices).
```
[CHOICE] <what is being chosen> — (a) … · (b) … · (c) …
         If you move on without choosing: <the rule's default>
```
Two CHOICE blocks carry **no default line** and wait for an answer: the last-chance menu (07.5; T-07-7) and the
Bent's offer (02.6.6) [integration: IR ch.07 to 12, IR ch.02].

**12.15.7 CLARIFY and ASSUMING** (01.2.4).
```
[CLARIFY] One question: do you mean to climb the rope, or cut it?
[ASSUMING] You mean the merchant, not his guard. (Say so if not — you can change it at the offer.)
```

**12.15.8 RULING** (a precedent shown on request, or when one was reused in a way the player may want to
see).
```
[RULING] r.0412 (Spring wk 4, day 1): verb.exert + dc:tier_rederived + stakes — Hard, Dire.
         Reused here; difference: the rope is wet (fact f.2231) → snag −2.
```

**12.15.9 CORRECTION** (12.3.4).
```
[CORRECTION] Earlier I said the purse held twenty coins; it holds 12 (your record is right).
             You spent nothing because of it. Logged.
```
With reliance: `You climbed the wall believing the gate was barred; it was open. Keep that, accept it as it
stands, or rewind to before the climb?` (a CHOICE follows).

**12.15.10 LEADS** (the stuck answer, 12.8.5).
```
[LEADS] Some ways forward — or anything else you have in mind:
        • the ferryman's daughter said he drinks at the Drowned Lantern
        • the scorched rope on the landing post (unexamined)
        • the toll-keeper at the bridge, who saw riders at dawn
```

**12.15.11 SITUATION** (session start, 12.5.2).
```
[SITUATION] Where: Ashford, the Drowned Lantern, evening · Pressing: the riders' search (sensed)
            Threads: The missing ferryman · Corner the Salt Road · Open offers: the Caravaners' contract
            Last time you said: "find out who burned the ferry"
```
Open offers include recognition offers awaiting an answer (04.7) and an open Bent offer; at most one
open-slot reminder (02.9.8) follows [integration: IR ch.04, IR ch.02 to 12].

**12.15.12 CHECK-IN** (12.5.9).
```
[CHECK-IN] Optional. More, same, or less of: fights · exploring · talking · investigating · travel · downtime?
           Pace: faster, same, slower? Anything to add to lines, veils or flags?
```

**12.15.13 SAFETY and FLAG** (12.5.6–12.5.7).
```
[OK] Adjusting. (Say how, or I'll reframe it.)
[FLAG] This touches <flagged topic>. Continue, veil it, or steer away?
```

**12.15.14 RULES, UNKNOWN, SESSION, CUT?**
```
[RULES] 01.4.2 — one resolved beat settles one obstacle for one approach; try a new approach or accept a cost.
[UNKNOWN] Your character doesn't know that. (The codex shows: <whatever is shown>.)
[SESSION] Paused. / Ending here — anything to focus on next time? (optional)
[CUT?] Move on to the morning, or stay a while?
```

**12.15.15 Labels added by other chapters** [integration: IR ch.02, 04, 07, 10, 11 to 12]. Each follows
12.15.1 and the order rule above; its contents are its owner's format.

| Label | Owner and format | Where it goes |
|---|---|---|
| `[WARNING]` | 07.3.4 (T-07-7): THIS CAN KILL YOU — source, cause line, exits | before the fiction's pause block; never omitted, never softened |
| `[CONFLICT]` | 06 (06.9.5–06.9.6, 06.11.4): the PC's status line in conflict — each foe's band to the PC and shown descriptors (bloodied, down, visible conditions), the PC's flags, every held windup ("winding up: the maul"), and each side's morale clock by name only when sensed (never a count) | after the RESULT blocks of every conflict turn [revision: I-030] |
| `[STATUS]` | 07.3.7 (T-07-7): STAGGERED or DYING n of 3, with what follows and the odds | when `trg.exits` fires (on becoming Staggered, and on entering Dying) |
| `[RECOGNITION]` | 04.7 (`vehicles.yaml#markers`): one line before a crisis offer's CHOICE block | immediately before the CHOICE |
| `[CREATE n/N]` | 02 (PR-02-7): a creation step's pause block, a CHOICE with a step count | the pause block during creation |
| `[SHEET]` | 02 (PR-02-6): the character summary | on request and at creation's end |
| `[JOURNEY]` | 10.3.4: the journey plan, points, supply against need, way-finding | with the RESULT blocks at a journey's planning and each day |
| `[SEASON]` | 11.11.2: the season herald, one week before the Season Turn | after the fiction |
| `[RETIRE]` | 11.13.1: the retirement offer listing the endings available (04.7's protocol: accept, decline, defer) | as the pause block |
| `[SEED n/14]` | 12.16.3: a world-seed step's summary (what was answered or rolled, and what it wrote, sealed parts withheld) | the pause block during session zero [revision: I-028] |

### 12.16 The world seed: starting from nothing

The rules generate places, people, factions and sites on demand, but a game also needs the handful of things
a setting supplies before the first scene: what is impossible, how magic and faith work, who lives here and
what they speak, a safe place to start from, powers already in motion, and somewhere dangerous to go. The
**world seed** writes those, from session-zero questions and oracle tables, so the game runs with no pre-made
setting. Chapter 13's Thallen Vale is one optional pre-made seed; nothing in the rules depends on it
[revision: I-028] [R5 P-22..P-36 (solo sandbox generation: Ironsworn's truths, Starforged's sector
creation, the Alexandrian's hexcrawl and West Marches); R: https://www.ironswornrpg.com/ (setting truths);
R6 B-12, B-20; DL-12-21].

**12.16.1 What a seed is and when it is made.** `[D]` A **world seed** is a region record of the shape of
`region_*.yaml` (SCHEMAS.md#region_yaml): the region, its canon, keepers, peoples, tongues, names, places,
cast, factions, clocks, situations, encounter and rumor tables, calendar, opening and pregens. It is made
once, at session zero (12.5.1), after chapter 14's preferences and before character creation (chapter 02
reads its peoples, tongues, keepers, names, org-tie map and bond placement), by PR-12-9 from
`data/world_seed.yaml`. Every entity it writes is `lifecycle: provisional` (00.16.3) and from then on is
established canon: state, never narration. A campaign that loads a pre-made seed instead (chapter 13's
`region_thallen.yaml`, or any region file) runs only the seed check (12.16.17) on it. *Reads:*
`world_seed.yaml`, and through it `archetypes.yaml`, `origins.yaml`, `factions.yaml`, `world_turn.yaml`,
`sites.yaml`, `travel.yaml`, `oracles.yaml`, `companions.yaml`, `rituals.yaml`, `licenses.yaml`,
`calendar.yaml`, `weather.yaml`. *Writes:* the region record (`create_entity`, `set_fact`, `set_clock`).

**12.16.2 Who answers a question.** `[D]` + `[J:enum]` Each of the seed's questions (T-12-15) has a closed
list of options and an oracle roll. In **guided** mode the player answers every question; in **oracle** mode
the engine rolls every one and the player may veto one answer per step, which is rolled again once; in
**mixed** mode (the default) the player answers the ones they care about and the engine rolls the rest.
The DM's only judgment is classifying a player's answer that is not one of the listed options:

```
### 12.16.2  Classify a custom seed answer                         [J:enum] [D]
Trigger [T]:        the player answers a seed question in their own words, not by an option
Decision [J:enum]:  which listed option of that question the answer is nearest to; "none fits"
                    is not an option. True only for the option whose listed effects (what the
                    step writes from it) the player's words state or plainly imply.
Effect [D]:         the step writes that option's effects; the player's own words are kept as
                    the entity's description (`desc`, a keeper's `what`, the region's `pitch`),
                    never as a mechanic.
Worst case (J):     a neighbouring option (a "feared" magic law where "licensed" was meant):
                    one fact one rung off, shown to the player in the step's summary before the
                    next step, and changed at their word (class i: corrected the same turn).
Anchor:             no (session zero only)
Basis:              [12.16.1] [R4 §3.2 S1: closed-set classification is the AI's reliable form]
```

The player may also supply content the tables would roll — a keeper's name, a faction, a town — which is
written as given and then completed by the step's rules (a supplied faction still takes a template, a tier,
a goal clock and sealed linchpins, PR-11-8).

**12.16.3 The steps.** `[D]` PR-12-9 runs fourteen steps in order (T-12-15); each step reads only what
earlier steps wrote, so a step re-run (a veto) re-runs every later step that read it. A step's summary is
shown to the player out of fiction (12.15.1 `[SEED n/14]`) before the next step, except what is sealed
(faction goals, linchpin fates, rumor truths, site objectives, secrets): the player sees what a character
raised there would know.

**12.16.4 Premise: what went wrong here.** `[D]` One wound (`tbl.12.seed.wound`, d12: a fallen realm, a
plague, an invasion, a curse, a sundering, a silent keeper, a long winter, the restless dead, a frontier, a
schism, a tyrant, an awakening) and a climate (one of 10.11.2's five). The wound writes the region's
`pitch` and three `truths` (Ironsworn's "truths"), and is read by later steps: the creature tags its
encounter pools weight × 3 (12.16.13), the situation template of its trouble and the org kind, goal and
temperament of the faction behind it (12.16.10, 12.16.12), the site themes it favours, the keeper forms it
favours, and the calendar's era. The region's name is drawn from `tbl.12.seed.place_names`.

**12.16.5 Canon: what is impossible, and how magic works.** `[D]` The seed writes `canon_impossible` and
`canon` (read by 01.3.7's G4 test 2, 05.7.10 and every chapter that defers to canon):
1. **Impossible for anyone** (`canon`'s `impossible` list, ids `ci.*`): always 05.7.10 item 1's five (true
   resurrection, time travel, making a soul, reading an absent mind, destroying a keeper) and 08's
   transmutation; plus none, one or two from `tbl.12.seed.extra_impossible`.
2. **Facts the Oracle treats as settled** (`canon`'s `facts`): the wound; how common magic is (rare,
   uncommon, common); whether open magic is lawful, licensed or feared where the game begins (05.7.10 item
   6; a visible working where it is not lawful is a method consequence, 01.11.2); who answers at the door
   of death (07.5.5; 12.16.6); whether any rite regrows a limb (07.7.6; default no); who may learn arcane
   magic (05.7.10 item 2).
3. **Magic** (`canon`'s `magic`, 05.7.10 items 1–8 in order): the impossibilities; the three sources; the
   keepers; the places of power (every place the seed gives `resonance`, `consecrated` or `desecrated`);
   spirit frequency for the Oracle's odds; lawfulness; components (`stock.components`, 08) and where texts
   and teachers are (`places[].settlement`); a closed school, if the player or the d12 names one.
4. Whether relics count as magic to those who refuse it (15's `magic` refusal), and whether chapter 04's
   four empty hybrid pairs stay empty (they do; a seed never authors a hybrid, 04.4's audit does).

**12.16.6 Faith: the keepers.** `[D]` Two to four keepers (05.7.4), each from a form of
`tbl.12.seed.keeper_form` (d12, the wound's favoured forms weighted × 3, no form twice): its kind, what it
keeps, three divine schools, the conduct axes it cares for and despises (04.9.2), its sign, and its faith's
org kind; its name from the name tables and a title. The first keeper that is not a pact-power is the
**main keeper**: its faith is a full faction seated in the haven (12.16.10); every other keeper's faith is a
petty faction (11.3.16). Who bargains at the door of death (07.5.5) is answered here: the keeper of death and
crossing if there is one, a fey lord (`arch.fey_noble`), a tempter (`arch.tempter`), or no one.

**12.16.7 Peoples and tongues.** `[D]` Each of chapter 02's eight peoples is `common`, `uncommon`, `rare` or
`absent` (`tbl.12.seed.presence`, d6 each; a people the wound's creature gates name moves one step more
present). Humans are at least uncommon and at least one non-human people is present. Each present people
gets a name table (d20 given names, d12 family names or epithets, built from `tbl.12.seed.names` without
repeats; a common human people gets two styles, the land's folk and incomers), which replaces
`tbl.name_given` / `tbl.name_family` for that people (12.11.1); the people behind the wound's threat gets one
too, as outsiders. Tongues: the Common tongue, renamed for the region; each present people's native tongue;
the Cant; and a **second tongue** (02.2.2's creation default): the native tongue of the most present
non-human people, or the Old Tongue as the speech of what went before. Absent peoples are listed
(`absent_origins`); C2 (PR-02-1) offers only present ones.

**12.16.8 The land: rings, areas and routes.** `[D]` The region is laid out as T-10-2's rings (10.2.4):
ring 0 the haven; rings 1–5 with three, three, three, two and two **areas** (10.1.1), each with a terrain
(ring 1 from the climate's farm country; rings 2–5 from `tbl.12.seed.terrain_by_climate`, d12), a home band
in its ring's range (T-10-2: 1 · 1–2 · 2–3 · 3–4 · 4–5) and a danger rating (settled · wild · wild or perilous
· perilous · deadly), a name (`tbl.12.seed.place_names`) and every 10.1.2 field (nav tier and openness from
`travel.yaml#terrain_defaults`, 10.1.8). Routes (10.1.3): the haven to every ring-1 area by road (1–2
watches); each area to the next in its ring (2–3 watches) and to one area of the ring inside it (3–4 watches);
roads and tracks in rings 1–2, trackless beyond. Rings 1–3 are `known`; rings 4–5 are rumor.

**12.16.9 The haven.** `[D]` One settlement in ring 0 (10.2.3: `safe: true`, `rest_site: haven`), a village
or a town, standing where `tbl.12.seed.haven_site` says (a ford, a bridge, a harbour, an old fort…), with its
buildings (a temple or shrine of the main keeper, consecrated and with `resonance`; an inn; a smithy; the
rulers' hall; its gate; in a town a market and a healer) and a graveyard tended by the main keeper's faith.
Its settlement record: tier (15, 16.3.2); market (common and scarce goods by terrain, 08.8.4; depth 30 or
150); crafters by tier (08.6); teachers drawn from the cast (12.16.11); texts; the rites the keepers' and the
place of acceptance's schools know (05.8); hire roles and the band limit (16.3.2); sentry post floors (15).
A **place of acceptance** for primal workers (02.5.5; `tbl.12.seed.acceptance`) is written as a landmark in
ring 1 or 2 with a spirit, three primal schools, what it asks, and a contact. The haven's fight locations
(06.3.8) come from its site; the region's rare metal and rite components from `world_seed.yaml#defaults`.

**12.16.10 Factions with running clocks.** `[D]` At least three full factions (11.3.2), each by PR-11-8 from
its template (11.3.18): the haven's **rulers** (`tbl.12.seed.rulers` by haven tier; tier 2 in a town, 1 in a
village); the **main keeper's faith** (the same tier); the **threat** behind the wound (its org kind, goal and
temperament from the wound; tier 2 or 3; seated at a ring-3 site, 12.16.12); and a **fourth** from
`tbl.11.faction_seed` (any kind not already present; tier by `tbl.11.faction_tier`), plus the minor keepers'
faiths as petty factions. Each goal clock is **running**: it starts with d(segments ÷ 3) ticks filled, so the
world is already moving when the PC arrives; each linchpin's four fates are written and sealed (11.3.10).
Relations: the threat stands at −2 to the rulers and the faith, −1 or 0 to the rest; other pairs d6 (1: −1,
6: +1, else 0). The seed also writes the **org-tie map** chapter 02's faction ties read (02.9.5: every org
kind the origins name maps to the faction of that kind, else to one of its branch that is not the threat,
else to `none`), the **institutions** by deed branch (11.8.1; V3, V9), and the region's **values** (the
rulers', 11.7.6). Faction names come from `tbl.12.seed.faction_names`.

**12.16.11 The cast.** `[D]` By 12.11.1 (role, gender, age, detail, demeanor, want, fear, refusal, secret,
voice; the name from the seed's tables; the people weighted by presence, common 6 · uncommon 3 · rare 1,
the threat's people for the threat's members): each faction's head (its linchpin) and, for a full faction,
an officer, each with one of the faction's duties; and the haven's smith, innkeeper, gate captain, healer
(or herb-wife), the place of acceptance's wise one, a sellsword, and in a town a scribe; a hedge-mage where
magic is common enough to be taught there (`ws.q.magic_level`). The captain and the sellsword can be
recruited (16.3.4). **Teachers** (15.13; `downtime.yaml#teacher_odds`) are the cast's trades: the main
keeper's priest its three schools; the captain polearm and shield; the smith smithing; the healer foraging;
the wise one the place's primal schools; the scribe letters and history; the hedge-mage two arcane schools.
**Bond placement** (02.9.2): where each of the eight bond kinds is placed — anchors in the haven, a rival in
the fourth faction, a creditor in the market, an enemy in the threat's seat, a lost one at a ring-2 site —
always as a new NPC when the bond is filled (02.9.8), never one already in the cast.

**12.16.12 Sites, lairs and threats.** `[D]` One site per area in rings 1–3 and one **lair** in each of rings
4 and 5, each by PR-10-6 (theme d8 with the wound's themes × 3; a domain whose terrain fits the area; band the
area's, −1 on a d6 of 1; lairs one band above their area, telegraphed by rumor, 09.8.2), named from the
domain, its objective sealed from the theme's climax, and its denizen table built by PR-10-10. The first
ring-3 site takes the wound's first theme and is the **threat's seat**; its objective is the faction's head.
Two **situations** (11.4.1) begin with their first step already done: the wound's (its template, its roles
bound to the threat, the rulers and the faith) in a ring-2 area, and one from `tbl.11.hook` (the first row
with a template) in a ring-1 area. The region's **bestiary** is every archetype its tables and sites name
and its factions field (09.11.2; PR-09-1 builds any entry the bestiary lacks).

**12.16.13 Encounter tables.** `[D]` Every area gets a regional table in 10.10.1's two-sub-table shape: its
threat sub-table built by **PR-10-10** at the area's home band from a pool of every archetype whose
`encounter.terrain` fits the area's terrain (× 3 for the wound's creature gates, × 2 for archetypes a seed
faction fields; elf wardens and dwarf holdguards only where their people are present), with the terrain
branch's archetypes as the fallback pool; its non-threat sub-table is the generic table of its terrain
(T-10-16). Each table is audited by PR-10-8 and the audit is stored (`encounter_table_audit`); a table that
fails is rebuilt with the next RNG draw, and the generic table stands in only if three builds fail (none
has: 12.16.17).

**12.16.14 Rumors.** `[D]` One rumor table (11.6.1; d12, or d20 when there are more than twelve): each full
faction's goal (true; points to its goal clock), each situation's first trace (true), each site (truth by
`tbl.11.rumor_truth`: hearsay in rings 1–2, legend beyond; a false site rumor says it is empty), and one
about a keeper; faces beyond the list repeat a rumor as hearsay, one step less true. Every rumor's truth is
sealed and its `points_to` is a real record (11.6.4).

**12.16.15 The calendar.** `[D]` 11.10's calendar with the seed's names: twelve month names from
`tbl.12.seed.calendar_names` (three per season, no repeats) or the counted defaults; seven day names; the
era named by the wound ("years since the Burning"); the four quarter-day festivals named for the main keeper
(spring), a fair (summer), the harvest (autumn) and a remembrance of the wound (winter); the opening date,
the spring quarter day of a year 11–30 of the era. Lifespans are `calendar.yaml#lifespans`.

**12.16.16 The opening and the pregens.** `[D]` The inciting incident (`tbl.12.seed.inciting`, d8) is framed in
the haven at a moment of decision (12.5.2 step 5; 12.4.3) and pairs with the PC's long vow (02.9.1). The
opening writes the start (date, dawn, the incident's place, the first day's weather rolled by
`h.10.weather`, the new moon, the spring festival) and **three leads** to three different records — the
incident's target, the other situation or the wound's, and the fourth faction's goal — so the first session
cannot dead-end (12.8.1). **Pregens** (02.2.5): four, by 02's creation defaults (the livelihood's priority and
the Peaked shape, the Typical rule unless 02.3.5's exception applies), covering a fighter (Soldier), a sneak
(Thief, of the most present non-human people), a talker (Merchant, Scholar or Courtier) and a worker of magic
(an Acolyte of the main keeper, or a Hedge-taught of the place of acceptance when the main keeper is a
pact-power); each with a drive, an aspiration and an anchor bond to a cast NPC; birth drawn live when picked.

**12.16.17 The seed check.** `[D]` A seed is complete when every requirement of **T-12-16**
(`world_seed.yaml#requirements`) holds: 62 checks, one for everything the other chapters read from a region
(built from every chapter's requests of chapter 13 and every rule that names region data). A requirement a
seed leaves to a generic table or an on-demand rule names it (`seed.uses_generic`: local events, hooks,
season events, NPC tables, omens, chase ground, hire quirks, cases by PR-15-6, storied items, regional
afflictions, setting origins). A failed check re-runs the step that writes the key; the seed is not used
until every check holds. *Evidence:* `_process/simulation/12-world-seed.py` runs PR-12-9 from data and the
check: seed 1 (oracle) and a guided run pass 62 of 62; 200 further oracle seeds pass every check, with 2,600
regional tables built by PR-10-10, every one passing PR-10-8 (word mix trivial 33.0 / easy 25.2 / fair 37.7 /
hard 4.1 / lethal 0 %). Seed 1 is committed as `_process/simulation/12-world-seed-example.yaml`.

**12.16.18 After the seed.** `[D]` The seed writes the world at the depth play starts with; everything
deeper is written on demand by its owner's rule and never invented in narration: a place on mention (10.1.4),
a person (12.11.1), a faction (11.3.18), a site's areas (PR-10-7), a case (PR-15-6), a storied item (08.4.8). A
**new region** (the PC travels past ring 5, or 11's World Turn opens one) runs steps 5, 9, 10 and 11 again
for it, with its rings' home bands starting where the old region's ring 5 ended, and its own factions by
11.3.18's new-region rule. A **pre-made seed** (chapter 13's Thallen Vale, or any `region_*.yaml`) replaces
PR-12-9 entirely and must pass the same seed check; a key it lacks is written by the step that owns it, with
the seed's other content as input. Chapter 13's region, run through the same script, holds 58 of the 62
requirements; its four gaps (its areas carry no route links between them, four encounter tables use a count
form 10.10.1 lacks, its situations' steps carry no `trace`, and one rumor points at prose rather than a record)
are listed in `12-world-seed-output.txt` and left as they are, because chapter 13 is no longer maintained
(I-035).

---

## Procedures

**PR-12-1 The turn loop.** `[D]` + `[J]` as marked in each rule. Runs once per player message. Steps T1–T6
are the **adjudication pass** (state, no prose); T7–T10 the **narration pass**; T11–T12 delivery and
record. A pause point (12.2.6) jumps to T7 with what has been resolved so far, then T10–T12.

| Step | Name | What the DM does | Tools | Rules |
|---|---|---|---|---|
| **T1** | RECEIVE | Store the player's message verbatim in the turn log. Read it in full; never paraphrase it into state. | `log_turn` (requested) | 12.2.5 |
| **T2** | CLASSIFY | Split the message into parts; classify each (SAFETY, SESSION, DISPUTE, PENDING_ANSWER, OOF_QUESTION, FICTION_QUESTION, DECLARATION, SPEECH); order them. SAFETY first: act on it before anything else. | — | 12.2.2, 12.5 |
| **T3** | LOAD | `get_active_triggers()`; `get_state(scene, narrator)`; `load_cards(situation tags, mode, triggers)` within the packet cap. The core checklist is always present. | 30, 8, 31 | 12.2.3, 12.2.4 |
| **T4** | ADJUDICATE | For each SESSION / DISPUTE / OOF part: answer it (12.5, 12.3.6). For each PENDING_ANSWER: resume the paused pipeline. For each FICTION_QUESTION: 01.3.8 (state → canon → Oracle, PR-01-4). For each DECLARATION: PR-01-1 (PARSE … CONSEQUENCE) per beat, up to three, `find_rulings` before any adaptation. Stop at the first pause point reached. | 1–6, 29 | 01.1–01.15 |
| **T5** | WORLD | World responses in fixed order: adversaries (conflict), NPCs present (frame → want/refusal → `tbl.npc_action`), clocks and omens, fired triggers (lead injection, pacing push, offers), time and boundaries (`advance_time` / `mark_boundary`). Each from its closed source only. | 7, 21–23 | 12.2.9, 01.11.3 |
| **T6** | WRITE | All state writes not already made: RECORD of every beat (01.12.1), evidence by **PR-03-1** for every resolved beat, rulings, NPC memories, knowledge records, `beat_end` marks; a cut scene is always marked `scene_end`, since ch.03's settlement hangs on it [integration: IR ch.03 to 12]. Then re-read the narrator view. | 9–18, 25, 29 | 12.2.8, 12.2.10 |
| **T7** | DRAFT | Draft the narration from the adjudication record and the fresh narrator view only: fiction first, then OOF blocks (12.15). Name everything 12.14.12 requires. Respect length (12.14.10). | — | 12.14 |
| **T8** | MENTION | List every concrete, addressable element the draft introduces; write each (`create_entity` / `set_fact`), rolling any property the draft needs that is unsettled (Oracle, tables; NPCs via 12.11.1). Redraft if an answer changes the draft. | 6, 7, 9, 10 | 00.6.6, PR-00-7 |
| **T9** | CHECK | Extract claims (12.3.1); `check_claims`; fix each non-`supported` verdict by its rule (12.3.2); re-check; at most two redrafts, then the plain fallback (12.3.3). | 32 | 12.3 |
| **T10** | SCREEN | Input fidelity ×3 (12.2.7); next step exists (01.11.4); safety screen against lines, veils and flags (12.5.6); PC agency (12.14.3); no mechanics in fiction (12.14.4); open prompt or one pause block last (12.14.9). Any failure → back to T7. | — | 12.2.7, 12.5.6, 12.14 |
| **T11** | DELIVER | Send the response. | — | 12.15 |
| **T12** | RECORD | Store the delivered response verbatim; update turn counters (dead air, 12.4.2); if a scene cut was reached, `mark_boundary(scene_end)` then frame the next scene (PR-12-7) in the *next* response unless the cut was the player's own request in this message. | `log_turn`, 22 | 12.2.5, 12.4 |

**PR-12-2 The claim check.** `[D]` + `[J:enum]` (inside T9)
1. Split the draft into sentences; for each, list every assertion and classify it (12.3.1). Include the
   OOF blocks' state values.
2. `check_claims(claims)` → a verdict per claim (12.3.2).
3. For each `new_element`: write it on mention (only the implied properties) or cut it.
4. For each `undetermined`: ask the Oracle or roll the settling table; write the answer; redraft to it.
5. For each `contradicted` or `overreach`: redraft to the store's value or the literal scope.
6. For each `unsourced_change`, `leak` or `pc_agency`: cut the claim (and replace a leak with its permitted
   slice if the sentence needs one).
7. Re-run steps 1–2 on the redraft. After the second redraft, if any verdict is still not `supported`,
   deliver the plain fallback (12.3.3) and log a `rule_conflict` ruling with `review_flag: true`.

**PR-12-3 Lead injection.** `[D]` + `[J:flag]` (when `trg.lead_injection` fires; 12.8.2)
1. Walk the source ladder (12.8.2 step 1) and take the first eligible source; ties at a rung go to the
   higher list weight, then to the stalest rotation axis (12.9.2), then `roll_table` on the tied set.
2. `roll_table(tbl.lead_injection, {phase})` for the form (threat-tagged forms excluded in RELAX and
   PEAK). Fit test `[J:flag]`; re-roll once; then the fallback form.
3. Apply the three lead tests (concrete, actionable now, connected) and the three prohibitions (does not
   solve the thread, costs nothing, is not a threat during RELAX). A failing lead → the next source.
4. Write: unseal the clue through its gate, or write the NPC's approach, or the rumor heard;
   `record_knowledge(pc, …)`; set the inconclusive counter to 0.
5. Narrate it in this turn's world responses (T5 → T7). Log the injection in the scene log
   (`lead_injection: {source_rung, source_id, form_roll, facts}`); it is not a ruling, because nothing
   was adjudicated.

**PR-12-4 Correcting an error the player has seen.** `[D]` + `[J]` (12.3.4)
1. State the mismatch: the delivered claim (turn id), the store's value.
2. Narration error or record error? Name the resolved source if any (`[J:flag]`). Record error → corrective
   write citing the source (`source: correction`).
3. Reliance test (`[J:flag]`): list the committed beats since the error that cited, targeted or premised
   the claim.
4. If none: choose the form (in-fiction reconciliation only if it adds no new fact; else the OOF note);
   deliver it; go to step 7.
5. If some, within the current scene: CHOICE (pause point 9) — keep (only if each frame stays valid
   without the false element), accept forward, or rewind (`revert_writes` to before the first relying
   beat; void its rolls in the log; the player re-declares).
6. If some, before the current scene: correct forward; refund every quantity spent because of the
   falsehood (corrective writes); nothing else.
7. Log the correction record and a ruling with `review_flag: true`; check the review list's Principle III
   candidate rule (12.12.4).

**PR-12-5 Generating an NPC and the first meeting.** `[D]` + `[J:enum]` (12.11)
1. Check the region roster and the cast list for an existing NPC who fits (`[J:flag]`); if one does, use
   them and stop.
2. Walk-on: role (from the narration, else `tbl.npc_role` with the place's tags) → name (region table,
   else `tbl.name_given` + `tbl.name_family`) → gender and pronouns → age band → distinctive detail →
   demeanor. `create_entity(kind npc, …)`; add to the cast list at weight 1.
3. At first interaction: the reaction roll (12.11.2) → `set_relationship`.
4. On a recurring trigger: want, fear, voice register and habit, refusal, knowledge scope.
5. On a principal trigger: the Oracle for a secret (sealed with a gate), two more wants (ranked), ties.
6. Every field is written before the narration that uses it; nothing is chosen.

**PR-12-6 A random event.** `[D]` + `[J:open]` (12.6.5)
1. `roll_table(tbl.event_focus, {phase})` → focus (threat foci read as *omen* in PEAK and RELAX).
2. Target from the weighted list if the focus names one; empty list → the stated substitute focus.
3. `roll_table(tbl.meaning, {kind: action})` → verb + subject.
4. Interpret in one sentence under the four conditions of 12.6.5 step 4; `find_rulings` for the same focus
   and target kind if the event is of a recurring kind.
5. Write (`create_entity` / `set_fact` / NPC action / one clock tick from a listed `random_event` source);
   check the bounds (no harm, no cost, no license, no sealed fact, no protected thread resolved).
6. Narrate now (in scene) or schedule as news (remote).

**PR-12-7 Scene start and scene end.** `[D]` + `[J]`
*At scene_start:* (1) write the scene record: agenda, the PC's hoped answer (12.6.3), mode (12.4.5),
pillar and challenge type (12.9.1), cast present; (2) `mark_boundary(scene_start)` → `h.12.scene_test`
(unless untested) and `h.12.pacing_push` if raised; (3) apply an altered or interrupted result; (4) frame
the scene (12.4.3); (5) if a flagged topic is present, the FLAG pause first (12.5.6).
*At scene_end:* `mark_boundary(scene_end)` runs every registered handler (00.7.5 phases), including
`h.12.bookkeeping`'s eight steps (12.4.8), in this order of ch.12's own handlers: phase 7
`h.12.lead_audit`; phase 9 `h.12.tension_update`, `h.12.intensity_scene`, `h.12.rotation_update`,
`h.12.npc_memory`, `h.12.bookkeeping`.

**PR-12-8 Session open and close.** `[D]` (12.5.2, 12.5.4)
*Open:* `mark_boundary(session_start)` → `h.12.session_open`: preferences re-read → recap from state →
SITUATION block → pending pauses re-shown → strong start (vignette if nothing presses) → check-in if due.
*Close:* finish the beat only if past ROLL → `mark_boundary(session_end)` → `h.12.session_close` (review
list compiled, 12.12.4) and the mirrored `h.12.bookkeeping` → optional next-time question → one line of
where the PC stands. No time passes at either.

**PR-12-9 The world seed.** `[D]` + `[J:enum]` (12.16; reference code `_process/simulation/12-world-seed.py`;
data `data/world_seed.yaml`) [revision: I-028]
1. **Mode.** Ask once: guided, oracle or mixed (12.16.2; default mixed). In mixed mode, list the questions
   (T-12-15) and let the player name the ones they want to answer.
2. **Run steps 1–13 in order** (T-12-15). For each question: the player's option, or the player's own words
   classified by 12.16.2, or the oracle roll; log `{question, answer, source}`. Each step writes its keys by
   its rule (12.16.4–12.16.16), reading only earlier steps' writes.
3. **Show each step's summary** as `[SEED n/14]` (shown parts only; sealed parts withheld). A veto re-rolls
   that step's oracle answers once and re-runs every later step that read them.
4. **Seed check** (step 14; 12.16.17): run every T-12-16 requirement; a failure re-runs the step that writes
   its key. The seed is used only when every check holds.
5. **Hand over** to chapter 02's creation (its C2 shows the seed's present peoples; its defaults read the
   seed's second tongue, keepers and name tables; a pregen may be picked) and then to the opening
   (12.16.16): `mark_boundary(session_start)`, strong start at the incident.

---

## Tables

Canonical data: **`data/pacing.yaml`** (every number this chapter owns), **`data/oracles.yaml`** (every
table this chapter rolls), **`data/anchors.yaml`** (the compiled anchor index). The data files win over
any paraphrase here (00.1.4 item 5).

| Table | Content | Where |
|---|---|---|
| T-12-1 | The always-loaded turn-loop checklist (verbatim card) | below; `pacing.yaml#packet.core_checklist` |
| T-12-2 | Pause points | 12.2.6 |
| T-12-3 | Mode transitions | 12.4.5; `pacing.yaml#modes` |
| T-12-4 | Which tool answers the DM's uncertainty | 12.6.1; `pacing.yaml#dm_questions` |
| T-12-5 | Claim classes and verdicts | 12.3.1–12.3.2; `pacing.yaml#claim_check` |
| T-12-6 | Random-event focus | 12.6.5; `oracles.yaml#tbl.event_focus` |
| T-12-7 | Challenge types | 12.9.1; `pacing.yaml#rotation.challenge_types` |
| T-12-8 | Lead-injection forms and source ladder | 12.8.2; `oracles.yaml#tbl.lead_injection`; `pacing.yaml#lead_injection` |
| T-12-9 | Scene-test deviation by tension | 12.4.4; `pacing.yaml#scene_test` |
| T-12-10 | In-fiction vocabulary for condition, adversary state and standing | 12.14.4, 12.14.7 |
| T-12-11 | Range bands and flags in words | 12.14.6 |
| T-12-12 | Reaction-roll distributions | 12.11.2; `oracles.yaml#tbl.npc_reaction` |
| T-12-13 | Twist rows by severity | 01.13.10; `oracles.yaml#tbl.twist_s1…s5` |
| T-12-14 | Every ch.12 number | `pacing.yaml` |
| T-12-15 | The world seed's steps and questions | 12.16.3; `world_seed.yaml#steps`, `#questions` (below) |
| T-12-16 | What the rules read from a region, and the seed check | 12.16.17; `world_seed.yaml#requirements` (below) |

**T-12-1 The always-loaded checklist** (this is the card that travels with every turn; about 250 words;
`pacing.yaml#packet.core_checklist` holds the same text).

> **Every turn.** T1 Store the message verbatim. T2 Classify its parts; safety first. T3 Load triggers,
> the narrator view and the cards for this scene; handle every fired trigger this turn. T4 Adjudicate
> before writing prose: questions from state, canon or the Oracle; declarations through the pipeline
> (PARSE, GATE, NECESSITY, ANCHOR, FRAME, OFFER, ROLL, READ, DELIVER, CONSEQUENCE, RECORD); check
> precedent before any adaptation, Oracle call, Good Idea, G3 or G4; stop at a pause point. T5 Let the
> world respond only from its sources: adversaries' behavior, NPCs' frames, wants, refusals or the
> action table, clocks and omens, triggers, time. T6 Write all state, then re-read it. T7 Draft from
> the record and the fresh view. T8 Write on mention every new addressable thing; roll what is unsettled.
> T9 Check every claim against the store; fix or cut; never write a change to match prose. T10 Intent
> acknowledged, not substituted, not reset; a next step exists; no line crossed; no words or feelings
> given to the character; no numbers or rules words in the fiction; end on an open prompt or one pause
> block. T11 Deliver. T12 Log it; count dead air; cut the scene if its question is answered.
> **Never**: choose a number; pick at random; decide what is true; change a committed frame; add a
> complication from nowhere; narrate a sealed fact; speak for the character; voice a mechanic.
> **If unsure**: roll (a check, the Oracle, a table) rather than decide; grant less rather than more.

**T-12-10 In-fiction vocabulary** (`[N]`; ch.07 and ch.09 may refine their own descriptors; these are the
defaults).

| State | Words the fiction may use |
|---|---|
| PC Vitality above half | steady, scraped, breathing hard |
| PC bloodied (at or below half) | bleeding, battered, every movement costs |
| PC Staggered (0) | reeling, on your knees, the world narrowing |
| PC Dying | ch.07's dying narration (the brink) |
| PC Focus low (0–1) | drained, the well run dry, nothing left to draw on |
| Adversary unhurt | fresh, untouched, easy in its stance |
| Adversary bloodied | bleeding freely, guard dropping, favoring a side |
| Adversary down | falls, does not rise, out of the fight |
| Standing (12.14.7) | Hostile: open enmity · Unfriendly: curt, suspicious · Wary: guarded · Neutral: businesslike · Warm: small courtesies · Friendly: goes out of their way · Devoted: would take risks for you |

**T-12-11 Range bands and flags in words** (ch.06 owns their meaning).

| Id | Words | Id | Words |
|---|---|---|---|
| `band.engaged` | at blade's reach; locked together | `flag.flanked` | caught between them |
| `band.close` | a few strides off; a lunge away | `flag.cornered` | your back to the wall |
| `band.near` | across the room; a stone's throw | `flag.in_cover` | behind (the cover named) |
| `band.far` | a long bowshot; across the field | `flag.elevated` | above them (the height named) |
| `band.distant` | at the edge of sight; far beyond reach | `flag.hidden` | unseen |
| | | `flag.mounted` | in the saddle |
| | | `flag.lined_up` | strung out in a line |

**T-12-12 Reaction rolls** (exhaustive over 2d6; `pace12.py`).

| Modifier | Hostile | Unfriendly | Wary | Neutral | Warm | Friendly | Mean |
|---|---|---|---|---|---|---|---|
| −2 | 16.7 | 25.0 | 30.6 | 19.4 | 8.3 | 0 | −1.22 |
| −1 | 8.3 | 19.4 | 30.6 | 25.0 | 13.9 | 2.8 | −0.75 |
| 0 | 2.8 | 13.9 | 25.0 | 30.6 | 19.4 | 8.3 | −0.25 |
| +1 | 0 | 8.3 | 19.4 | 30.6 | 25.0 | 16.7 | +0.22 |
| +2 | 0 | 2.8 | 13.9 | 25.0 | 30.6 | 27.8 | +0.67 |
| Faction member: individual step | −1: 16.7 | 0: 66.7 | +1: 16.7 | | | | |

**T-12-9 Scene-test deviation by tension** (d10; deviation when roll ≤ T − 3; odd altered, even
interrupted). Also the random-event chance per Oracle question (doubles with digit ≤ T).

| Tension | 1–3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|
| Altered | 0 | 10 | 10 | 20 | 20 | 30 | 30 |
| Interrupted | 0 | 0 | 10 | 10 | 20 | 20 | 30 |
| Random event per Oracle question | 1–3 | 4 | 5 | 6 | 7 | 8 | 9 |
| Oracle odds shift (eventful questions) | 1 rung away | — | — | — | 1 rung toward | 1 rung toward | 1 rung toward |

**T-12-15 The world seed's steps and questions** (`world_seed.yaml#steps`, `#questions`; 12.16.3).

| Step | Rule | Questions (player or oracle) | Writes |
|---|---|---|---|
| 1. Premise: what went wrong here | 12.16.4 | `ws.q.wound` (d12); `ws.q.climate` (d6) | `region/pitch`, `region/truths`, `region/climate`, `region/wound` |
| 2. Canon: what is impossible, and how magic works | 12.16.5 | `ws.q.magic_level` (d6); `ws.q.magic_law` (d6); `ws.q.spirits` (from ws.q.magic_level); `ws.q.arcane_source` (d6); `ws.q.extra_impossible` (d6); `ws.q.regrowth` (d6); `ws.q.closed_school` (d12); `ws.q.relics_magic` (d6); `ws.q.hybrid_none` (d6) | `canon_impossible`, `canon` |
| 3. Faith: the keepers and who answers at death's door | 12.16.6 | `ws.q.keeper_count` (d6); `ws.q.keepers` (d12); `ws.q.bargainer` (d6) | `keepers`, `canon/facts` |
| 4. Peoples and tongues | 12.16.7 | `ws.q.presence` (d6); `ws.q.second_tongue` (d6) | `peoples`, `absent_origins`, `names`, `tongues` |
| 5. The land: rings, areas and routes | 12.16.8 | `ws.q.terrain` (d12) | `region/rings`, `terrain_by_ring`, `places (the region and its areas)`, `places[]/links` |
| 6. The haven | 12.16.9 | `ws.q.haven_tier` (d6); `ws.q.haven_site` (d8) | `region/haven`, `places (settlements and buildings)`, `places_of_acceptance`, `fight_locations`, `stock` |
| 7. Factions with running clocks | 12.16.10 | `ws.q.rulers` (d6); `ws.q.fourth_faction` (d12) | `factions`, `clocks`, `values` |
| 8. The cast | 12.16.11 | none: engine only | `npcs`, `bond_placement` |
| 9. Sites, lairs and threats | 12.16.12 | none: engine only | `places (sites)`, `situations`, `clocks`, `bestiary` |
| 10. Encounter tables | 12.16.13 | none: engine only | `encounter_tables`, `encounter_table_audit` |
| 11. Rumors | 12.16.14 | none: engine only | `rumor_tables` |
| 12. The calendar | 12.16.15 | `ws.q.month_names` (d6) | `calendar` |
| 13. The opening and the pregens | 12.16.16 | `ws.q.inciting` (d8) | `opening`, `pregens` |
| 14. The seed check | 12.16.17 | none: engine only | `seed/check` |

**T-12-16 What the rules read from a region, and the seed check** (`world_seed.yaml#requirements`; 12.16.17;
`12-world-seed.py` runs every check). *Generic* names the default table or rule used when the seed leaves the
key to it.

| Id | From | What is read | Rules | Seed key | Check |
|---|---|---|---|---|---|
| `ws.req.01_canon_impossible` | 01 | canon_impossible: G4 test 2 (CONTRADICTS CANON) | 01.3.7, 05.7.10 item 1 | `canon_impossible` | canon_impossible |
| `ws.req.01_spirits` | 01 | what spirits of place understand, and how common they are | WE-01-11, 05.7.10 item 5 | `canon/spirits` | nonempty |
| `ws.req.01_tongues` | 01 | language licenses and their fallbacks | 01.18, 02.4.6 | `tongues` | tongues |
| `ws.req.01_oracle_canon` | 01 | settled canon facts for the Oracle's Certain / Impossible | 00.12.7, 12.6.2 | `canon/facts` | min_count |
| `ws.req.02_peoples` | 02 | which peoples are present (C2 shows them) | 02.4.2, PR-02-1 C2 | `peoples` | peoples |
| `ws.req.02_names` | 02 | a name table per present people | 02.9.7, 12.11.1 | `names` | names |
| `ws.req.02_second_tongue` | 02 | second_tongue (the fast path's tongue pick) | 02.2.2 | `tongues/second_tongue` | second_tongue |
| `ws.req.02_keepers` | 02 | the powers an Acolyte may keep, with their faiths | 02.5.5, 05.7.4 | `keepers` | keepers |
| `ws.req.02_acceptance` | 02 | a place of acceptance for a Hedge-taught character (primal) | 02.5.5, 05.9.4 | `places_of_acceptance` | acceptance |
| `ws.req.02_org_ties` | 02 | a faction (or an explicit none) for each org kind the origins name | 02.9.5, PR-11-4 | `factions/org_tie_map` | org_tie_map |
| `ws.req.02_bonds` | 02 | where each bond kind is placed | 02.9.2, 02.9.8 | `bond_placement` | bond_placement |
| `ws.req.02_pregens` | 02 | at least four pregens passing PR-02-9: a fighter, a sneak, a talker or scholar, a worker of magic; one non-human | 02.2.5, PR-02-9 item 13 | `pregens` | pregens |
| `ws.req.02_inciting` | 02 | the inciting incident that pairs with the long vow | 02.9.1, 12.5.2 step 5 | `opening/inciting` | inciting |
| `ws.req.02_location` | 02 | the opening place (the PC's starting location) | 02.7 state table, PR-02-1 step 4 | `opening/start/place` | ref_place |
| `ws.req.03_consecrated` | 03 | facts marking graves, shrines and holy places consecrated or tended | 03.1.8 (piety: a consecrated or tended grave), T-07-16 (aff.grave_chill: its cure) | `places[]/facts` | consecrated |
| `ws.req.03_homes` | 03 | NPC homes (witness scopes) | 03.10 | `npcs[]/home` | npc_homes |
| `ws.req.04_keeper_axes` | 04 | keepers with the conduct axes each cares for | 04.9.2 | `keepers[]/axes` | keepers |
| `ws.req.04_institutions` | 04 | institutions per deed branch (V3, V9; institutions_matching) | 04.6 V3, V9, 11.8.1 | `factions/institutions` | institutions |
| `ws.req.04_hybrid_none` | 04 | whether the four none hybrid pairs hold | 04.4 | `canon/hybrid_none_pairs` | nonempty |
| `ws.req.05_resonance` | 04/05/10 | place resonance (places of power) | 05.6.9, 05.7.10 item 4 | `places[]/resonance` | resonance |
| `ws.req.05_magic_canon` | 05 | 05.7.10 items 1-8 | 05.7.10 | `canon/magic` | magic_canon |
| `ws.req.05_rites_known` | 05 | which rites are known in the region | 05.8 | `places[]/settlement/rites_known` | rites_known |
| `ws.req.05_components` | 05/08 | rite components by price band; where texts and teachers are | 05.7.10 item 7, 08.4 | `stock/components` | components |
| `ws.req.06_chase_ground` | 06 | regional chase-ground tables (or the generic one) | 06.12 | `tables (chase ground)` | generic_or_table: conflict.yaml#tbl.chase_ground |
| `ws.req.06_fight_locations` | 06 | feature-rich fight locations | 06.3.8 | `fight_locations` | fight_locations |
| `ws.req.06_bestiary` | 06/09 | the region's creatures: what its tables field (nerve and objectives come from 09's build) | 09.11, PR-09-1 | `bestiary` | bestiary |
| `ws.req.07_bargainer` | 07/09 | a default bargainer at the door of death, or none | 07.5.5 | `canon/facts` | bargainer |
| `ws.req.07_regrowth` | 07 | whether any rite regrows a limb | 07.7.6 | `canon/facts` | regrowth |
| `ws.req.07_havens` | 07/10 | havens (safe places for 07's long rest and 10's venture end) | 07.8, 10.2.2 | `region/haven` | haven |
| `ws.req.07_afflictions` | 07 | regional afflictions (optional) | 07.9 | `afflictions` | generic_or_table: afflictions.yaml |
| `ws.req.08_market` | 08 | regional stock: what is common and scarce, crafters by settlement, curio dealers | 08.8.4, 08.6 | `places[]/settlement/market` | market |
| `ws.req.08_transmutation` | 08 | canon_impossible on transmutation | 08.6 (AI-1) | `canon_impossible` | transmutation |
| `ws.req.08_storied` | 08 | storied items and sets (optional at the start) | 08.4.8 | `storied_items` | generic_or_table: none at the start (08.4.8) |
| `ws.req.08_boons` | 08 | faction boon bases and signatures | 08.7 | `factions/instances[]/boon_base` | boons |
| `ws.req.08_rare_metal` | 08 | the region's rare metal | 08.4.3 | `stock/rare_metal` | nonempty |
| `ws.req.09_subset` | 09 | a regional subset of the bestiary | 09.11.2 | `bestiary/archetypes` | bestiary |
| `ws.req.10_places` | 10 | places with every 10.1.2 field (or terrain defaults) | 10.1.2 | `places` | places |
| `ws.req.10_links` | 10 | route links with lengths in watches | 10.1.3 | `places[]/links` | links |
| `ws.req.10_rings` | 10 | danger rings per T-10-2 | 10.2.4, T-10-2 | `region/rings` | rings |
| `ws.req.10_encounters` | 10 | regional encounter tables in the two-sub-table shape, passing PR-10-8 | 10.10.1, 10.10.2, PR-10-8 | `encounter_tables` | encounter_tables |
| `ws.req.10_signs_events` | 10 | archetype signs (travel.yaml's) and local events | 10.9.4, 10.9.6 | `tables (events)` | generic_or_table: travel.yaml#archetype_signs; world_turn.yaml#tbl.11.local_events |
| `ws.req.10_sites` | 10 | site placements: theme, domain, band, size, objective | 10.13.2, PR-10-6 | `places[]/site` | sites |
| `ws.req.10_rest` | 10 | havens and rest sites | 10.2.3, 07.8.4 | `places[]/rest_site` | rest_sites |
| `ws.req.10_climate` | 10 | climate per region (weather regimes) | 10.11.2 | `region/climate` | climate |
| `ws.req.11_factions` | 11 | factions conforming to 11.3.1, linchpin fates sealed, at least three full with running goal clocks | 11.3.1, 11.3.10, PR-11-8 | `factions/instances` | factions |
| `ws.req.11_calendar` | 11 | month, weekday, quarter-day, festival and era names (or the counted defaults) | 11.10.1, 11.10.4 | `calendar` | calendar |
| `ws.req.11_tables` | 11 | tbl.11.season_events.<region>, tbl.11.hook.<region>, tbl.<region>.events (or the generic ones) | 11.5.10, 11.11.3 | `tables (hooks, season events)` | generic_or_table: world_turn.yaml#tbl.11.hook, tbl.11.season_events.*, tbl.11.local_events |
| `ws.req.11_values` | 11 | regional values for region scopes | 11.7.6 | `values` | values |
| `ws.req.11_lifespans` | 11 | lifespans for its peoples | 11.10.5 | `calendar/lifespans` | generic_or_table: calendar.yaml#lifespans |
| `ws.req.11_situations` | 11 | situations with default timelines (the land's trouble in motion) | 11.4.1, 11.4.2 | `situations` | situations |
| `ws.req.11_rumors` | 11/15 | rumor tables, each rumor's truth sealed and pointing somewhere real | 11.6.1, 11.6.4 | `rumor_tables` | rumors |
| `ws.req.12_npc_tables` | 12 | region roster, role, name and furnishing tables (or the generic ones) | 12.11.1 | `names; tables (npc)` | generic_or_table: oracles.yaml#tbl.npc_* |
| `ws.req.12_cast` | 12 | the starting cast: principal NPCs the opening and the factions need | 12.11.1, 11.3.17 | `npcs` | npcs |
| `ws.req.12_opening` | 12 | the opening: start place, date, weather, and at least three leads (12.8: no dead end at the start) | 12.5.1, 12.5.2, 12.8.1 | `opening` | opening |
| `ws.req.15_tiers` | 15/16 | settlement tiers (carousing, asking around, recruiting) | 15.13.8, 15.13.9, 16.3.2 | `places[]/settlement/tier` | settlement_tiers |
| `ws.req.15_teachers` | 15 | teacher availability per settlement | PR-15-8, 15.13.9 | `places[]/settlement/teachers` | teachers |
| `ws.req.15_sentries` | 15 | sentries' post floors | 15.8 (alertness) | `places[]/settlement/sentry_floors` | sentries |
| `ws.req.15_cases` | 15 | case templates (or PR-15-6 on demand) | 15.9.1, PR-15-6 | `cases` | generic_or_table: PR-15-6 |
| `ws.req.15_lifestyles` | 15 | NPC lifestyles where they differ from the role default | 15.2 (lifestyle) | `places[]/settlement/lifestyle_overrides` | present |
| `ws.req.15_relics` | 15 | whether relics count as magic for the magic refusal | 15.3 (refusals) | `canon/relics_and_refusal` | nonempty |
| `ws.req.16_hire` | 16 | regional hire roles (and quirks, or the generic table), beasts and mounts available, the band limit by tier | 16.3.2, 16.3.3 | `places[]/settlement/hire` | hire |
| `ws.req.16_recruits` | 16 | named NPCs who might be recruited | 16.3.4 | `npcs[]/recruit` | recruits |

---

## Worked examples

All examples follow **Wren** (00, 01): Might +1, Agility +3, Endurance +1, Wits +2, Intellect 0, Presence 0,
Resolve −1; competence `deed` +1 (floor), `deed.wilds.tracking` +2, `deed.martial.archery` +2; Vitality
12, Focus 4, fate 1; preference `auto_commit: on`; pacing profile `standard`. The situation *(illustrative;
ch.11/13 own the content)*: the Ashford ferryman, **Hob Coldwell**, vanished three nights ago, and his
ferry stands idle. The thread `thr.missing_ferryman` (ch.11) has three sealed clue placements: `clu.scorched_rope`
(at the landing: the mooring rope was burned through, not cut; stored tier Moderate, DC 15), `clu.toll_ledger`
(at the Grey Keep toll-house: a dawn crossing by riders in Salt Guild colors), and `clu.daughter_purse` (held
by Hob's daughter **Maren**, generated with the thread: a stranger paid her father in Guild silver the day
before). A sensed clock `clk.riders_search` (danger, 6, "The riders find what they are looking for") runs.
Tension 5; intensity 0; phase BUILD. Every ch.12 number is exact; others are marked.

### WE-12-1 Full turn-loop trace 1: a simple action (with a secret frame and a pause)

*DM turn 1. Player:* "I walk down to the landing and look it over. Is the ferry still there? Anything odd?"

| Step | What happens | State / tools |
|---|---|---|
| T1 | Message stored verbatim. | turn log #118 |
| T2 | Parts: "walk down to the landing" — DECLARATION (Move, Trivial: no roll, a scene change); "Is the ferry still there?" — FICTION_QUESTION; "look it over … anything odd?" — DECLARATION (Observe). No SAFETY, SESSION or DISPUTE. | classes logged |
| T3 | `get_active_triggers()` → none. Place change → `scene_end` (market) then `scene_start` (landing). Scene record: agenda "What happened at the landing?"; hoped answer: Wren hopes to find a sign (yes); mode `free` → `site`? No: one place, no room-by-room search → `free`; pillar `investigation`; challenge type `mystery`. `h.12.scene_test`: expected scene "the landing at dusk, deserted"; d10 = **8** > T − 3 = 2 → **expected**. Cards loaded: `situation.investigation.search`, `situation.exploration`, the Observe anchor. | `mark_boundary` ×2; scene `scn.0231` |
| T4a | FICTION_QUESTION: is the ferry here? No fact; canon silent; scene logic? A ferry landing *usually* has its ferry, but the ferryman is missing (fact) — open. `find_rulings(oracle)` → no precedent. Odds `[J:rung]` **Even** (could have gone with him or been left); eventful tag `none` (static availability). Tension 5 → no shift. `oracle(…)` d100 = **63** → yes (63 ≥ 51; not in 51–55; not doubles). | `set_fact(loc.ashford_landing.ferry_present = true, source: oracle)`; `create_entity(obj.ferry_flatboat)` |
| T4b | DECLARATION Observe. PARSE: method "look over the landing for anything out of place", target `loc.ashford_landing`. GATE G1 `verb.observe`. NECESSITY: the landing holds a sealed clue placement → uncertain; costly? the riders' search runs and time matters → roll (`[J:flag]` ×3; tie → roll). Secret frame `[J:flag]`: the target's content is sealed → **true** (01.4.7). ANCHOR: `verb.observe` card, no deltas (no `find_rulings` needed: no adaptation). FRAME: Wits +2; primary tag `deed.lore.investigation` → floor +1; no levers or snags; obstacle `clu.scorched_rope`, stored DC 15 (hidden); stakes **Safe** (no one near, the night young: failure only means nothing found); threatened cost `cost.time` (used only on a critical failure, S1); reach Standard (one question). Total +3. | frame #771 |
| — | **Pause point 1**: auto-commit does not apply to a secret frame (01.7.4). The turn jumps to T7 with what is resolved. | — |
| T5 | World: no NPC present; no clock ticked; `advance_time`: the walk down is unlisted free movement in town (0 time, 00.7.3 `free`). | — |
| T6 | Writes done (fact, boat); narrator view re-read. | — |
| T7 | Draft: "Dusk has gone blue over the river. The flatboat rides at its mooring, nosing the reeds; a coil of rope hangs by the boathouse door, and the ferryman's hut sits dark above the steps. Someone has left a pair of boots by the hut door." | — |
| T8 | Elements: flatboat (written), rope coil (ordinary furniture → `create_entity(obj.rope_coil_02)`), hut (`create_entity(loc.ashford_landing.hut)`, implied: dark), **boots** — `[J:flag]` 12.14.13: a pair of boots left by a missing man's door *points toward something hidden* → true → not furniture; cut. | 2 entities |
| T9 | Claims: `existence` boat ✓, rope ✓, hut ✓; `location_time` dusk ✓ (watch: evening); `identity` "the ferryman's hut" — ✓ (`loc…hut.owner = npc.hob_coldwell`, written with the thread). No other verdicts after the cut. | `check_claims` → all supported |
| T10 | Fidelity: three parts acknowledged ✓ (walked, ferry answered, search offered); nothing substituted ✓; nothing reset ✓. Next step exists ✓. Safety ✓. No numbers in fiction ✓. Ends on the OFFER block (pause). | — |
| T11 | Delivered (below). | — |
| T12 | Logged. Dead-air counter 0 (a declaration). | — |

*Delivered:*
> Dusk has gone blue over the river. The flatboat rides at its mooring, nosing the reeds; a coil of rope
> hangs by the boathouse door, and the ferryman's hut sits dark above the steps. You start along the
> landing, looking for anything out of place.
>
> `[OFFER] Search the landing for anything out of place — verb.observe (Observe), anchor 01.18.5`
> `Roll: Wits +2 · competence +1 (deed) = +3   ·   Against: hidden   ·   the roll is hidden; you'll see only what you perceive`
> `Stakes: Safe — failure: nothing found · critical failure: Time (S1)   ·   Reach: Standard — one answer`
> `Costs: 1 interval · fate 1   → commit · change · withdraw`

*DM turn 2. Player:* "Commit." — PENDING_ANSWER. T4: `roll_check(#771)`: d20 = **14** → total 17 vs 15 →
**success**; delivered reach 2 → the one question is answered (`deliver_count`). `unseal(clu.scorched_rope)`;
`record_knowledge(pc.wren, clu.scorched_rope, how: observed)`; evidence (ch.03); `mark_boundary(beat_end)` →
`h.12.inconclusive_streak`: a new fact learned → counter **0**; `h.10.site_time` not applicable (free mode).
T5: `advance_time(1 interval)` — no boundary handler fires. T7–T10: the draft names the delivered item; the
claim check passes; the next step is evident (the hut; who burned the rope?).
> You find it at the mooring post: the old rope end is black and stiff, the fibers fused. Not cut —
> burned through, close to the knot, as if someone held a flame to it until it parted. The hut above the
> steps is still dark. What do you do?
>
> `[RESULT] hidden check made.`

*Boundary pair.* Had the clue's existence been undetermined (no thread placed anything here), T4b would
first ask the **sealed** Oracle (01.15.6) — "is anything hidden here?", Unlikely — and the search would be
just as secret. *Non-example:* resolving "Anything odd?" by narrating the scorched rope at once, with no
roll, "because the scene needs a clue" — the clue is sealed behind its gate (a successful Observe); the DM
may not unseal it by mention (12.10.3).

### WE-12-2 Full turn-loop trace 2: a wild creative action, an anchor, a precedent, a split, and a catch

*Situation.* Two days later, in the toll-house on the Grey Keep bridge *(illustrative stat lines; ch.06/09
own)*. Conflict mode. Established at the scene's opening (written on mention): `obj.lantern_chain` (an iron
chain hanging from the rafters by the stair, a cartwheel lantern at its end); `loc.toll_hall.gallery` with
`f.gallery_height = 12 ft`; the archer `adv.toll_archer_02` (T2: Might +2, Agility +3, competence
`deed.martial` +2; Vitality 8) on the gallery at `band.near` with `flag.elevated`; after his last shot,
`adv.toll_archer_02.loaded = false` (he is spanning his crossbow; ch.06 reload). Wren stands at the foot of
the stair.

*DM turn 1. Player:* "I run up the stair, grab the lantern chain, swing across onto the gallery and kick
that archer off the rail before he can reload!"

| Step | What happens |
|---|---|
| T2 | One DECLARATION. |
| T3 | Triggers: none. Cards: `situation.conflict.*`; anchors retrieved below. |
| T4 PARSE | Three methods in sequence (run to the chain; swing; kick) → three beats, `sequential` (01.2.2; 12.13.3 split — distinct methods, distinct targets, and an order). ≤ 3 beats, inside ch.06's action budget *(illustrative)*. Neutral restatements: B1 "Wren moves up the stair to the chain"; B2 "Wren swings on the lantern chain to the gallery"; B3 "Wren kicks the archer to topple him off the gallery rail". |
| B1 | GATE G1 Move; NECESSITY: passable stair, no one blocks → **Trivial**, no roll. Position written: Wren at the chain. |
| B2 ANCHOR | `load_cards` → candidates scored (12.13.2): `verb.exert` (deed `athletics` +2, situation `conflict` +1; no intent verb "swing" → 3), `verb.move` (3), `verb.evade` (3). Pick `[J:enum]` **verb.exert** — the intended change is crossing a gap through the air (Exert's "jump"), not repositioning on passable ground (Move vs Exert test). The plain card is wrong for the obstacle (a chain changes a Beyond-tier jump into a swing), so `find_rulings(verb.exert, [dc:tier_rederived, stakes])` → **r.0412** (WE-00-9: the gatehouse chain swing; Hard; Dire for a 20-ft fall). Same signature, same kind of case (a hanging chain or rope replacing an unjumpable crossing) → match. Differing fact `[J:flag]`: is there an established fact that changes tier, stakes or reach? **Yes** — `f.gallery_height = 12 ft`: a 12-ft fall is not ch.10's Heavy (S3) fall source (falls of 20 ft and more are) → stakes **Risky**, not Dire. Tier reused: **Hard**. Departure logged with `differing_fact: f.gallery_height`. Deltas used: `dc` (tier re-derived) and `stakes` (source: the 12-ft fall) — two knobs, at the limit. |
| B2 FRAME | Attribute `[J:enum]`: the swing's success is in timing and an exact landing → **Agility** +3 (Exert's listed alternative for "a precise leap"; not a knob change). Tag `deed.martial.athletics` → floor +1. Levers/snags: none cited. Obstacle `obs.toll_hall_swing`, tier Hard → DC **20**, written as its stored DC (key: obstacle + anchor signature). Threatened cost `cost.harm` (the fall, S2); alternate `cost.footing`. Reach Standard: onto the gallery, engaged with the archer. `frame_check` → +4 vs 20: need 16 · success-or-better **25%** (crit success 5, success 20, failure 45, crit failure 30; near miss 15). |
| — | Pause point 1: 25% < 50% → no auto-commit. B3 is queued: its frame is built after B2's RECORD (01.14.1). |

> You take the stair two at a time; the lantern chain is cold and gritty in your fists, the gallery rail a
> long swing away above the boards, and up there the archer is cranking his crossbow back, eyes on you.
>
> `[OFFER] Swing on the lantern chain to the gallery — verb.exert (Exert), anchor 01.18.11, ruling r.0412 (departed: f.gallery_height 12 ft)`
> `Roll: Agility +3 · competence +1 (deed) = +4   ·   Against: DC 20 — Hard (precedent r.0412)`
> `Need: 16+ · 25% · crit success 5% · crit failure 30% · near miss 15%`
> `Stakes: Risky — failure: Harm (S2), the fall · crit failure: Harm (S3) · near miss: succeed and pay Harm or Footing (S2), or fail`
> `Reach: Standard — success: you land on the gallery, at his reach`
> `Costs: 1 action · rides: no · fate 1   ·   Then (queued): kick the archer off the rail`
> `→ commit · change · withdraw   (one trade: go big / play it safe)`

*DM turn 2. Player:* "Play it safe — I just want to get to the rail. Commit." The trade (01.7.3): stakes
Risky → **Safe** (failure: you swing back to the stair; critical failure: an S1 cost), reach Standard →
**Limited** (partway: hanging at the rail). `roll_check`: d20 = **16** → total 20 vs 20 → **success**;
delivered reach 1. RECORD: `set_position(pc.wren, {band_to: {adv.toll_archer_02: band.engaged}})`; fact
`pc.wren.hanging_from_gallery_rail = true` (the Limited reach's "partway"); ruling **r.0533** logged
(signature `verb.exert+dc:tier_rederived+stakes`, `precedent: {status: departed, from: r.0412,
differing_fact: f.gallery_height}`, `review_flag: true` per 01.5.4 because it departed). Sequential feed:
success → B3 gains what B2 was for — Wren is at the archer's reach.

B3 FRAME (built now, so B2's facts are established before it): GATE G1 `verb.force` (topple); ANCHOR
`verb.force`, no deltas; against the archer's higher defense — Agility: 10 + 3 + 2 = **15**. Attribute Might
+1 (Force allows only Might); `deed.martial.athletics` → floor +1. **Lever** (Precision): `adv.toll_archer_02.loaded
= false` — he is busy spanning the crossbow, a distracted target (the player cited it: "before he can
reload") → +2. **Lever** (Amplifying): `f.gallery_height` with the rail at his back — a drop that makes
success go further → reach +1. **Snag** (Precision): `pc.wren.hanging_from_gallery_rail` — kicking while
hanging is done worse → −2. Total +1 +1 +2 −2 = **+2**; reach Standard +1 = **Great**; stakes Risky:
threatened `cost.footing` (you lose your grip and drop), alternate `cost.harm` (S2). Need 13 · **40%**
(crit success 5, success 35, failure 45, crit failure 15; near miss 15). Pause point 1 again (40% < 50%).

*DM turn 3. Player:* "Commit." d20 = **12** → total 14 vs 15 → **failure, near miss** (margin −1). Pause
point 4:
> `[NEAR MISS] 14 vs 15. Succeed and pay one — (a) Footing (S2): you lose your grip and drop · (b) Harm (S2): your shoulder wrenches as you kick — or (c) let it fail (Footing S2 applies).`

*DM turn 4. Player:* "(b) — I'll take the shoulder." READ: success at a cost, delivered reach Great (3) →
pushed two bands, or prone and off-balance (01.18.10): over the rail and down. `apply_costs(cost.harm, S2,
form: "wrenched shoulder")` → Wren Vitality 12 → **9**. Archer: `set_position` (floor, `band.near` from Wren),
`cond.prone`; the fall is a ch.10 hazard resolved by the engine for him *(illustrative: S2, 3 harm → 8 → 5)*.
T5: the other foe (the toll-keeper's mate, at `band.far`) acts on his turn from his behavior list (ch.09) —
he runs for the bell; ch.06 orders it after Wren's turn.

T7 draft (first version): "You lash out with both heels; the archer pitches over the rail and his crossbow
clatters to the boards. You haul yourself up onto the gallery, your shoulder screaming, as the toll-keeper's
mate bolts for the bell rope." T9 claim check:
- "pitches over the rail" — `outcome`/`position` ✓ (delivered Great; position written).
- "his crossbow clatters to the boards" — `possession`: no write moved the crossbow → **unsourced_change**
  → cut (the archer is prone on the floor with his weapon).
- "You haul yourself up onto the gallery" — `position`: Wren's position is *hanging at the rail* (Limited
  delivered on B2; nothing since moved her) → **unsourced_change** → cut. Hauling herself up is a new beat
  the player has not declared (and `pc_agency`).
- "your shoulder screaming" — `harm_condition` ✓ (the chosen cost's form).
- "bolts for the bell rope" — ✓ (the mate's behavior result this round).
Redraft 1 passes. T10 ✓ (intent acknowledged, nothing substituted: the kick happened as declared; open
prompt). Delivered:
> You lash out with both heels from the rail. Something in your shoulder tears hot as the kick lands —
> and the archer pitches backward over the rail and hits the boards below, sprawled beside his crossbow.
> You hang from the gallery rail by one good arm, at the height of a man and a half over the floor. Across
> the hall the toll-keeper's mate is running for the bell rope. What do you do?
>
> `[RESULT] d20 12 → 14 vs 15 · near miss → success at a cost: Harm (S2), wrenched shoulder · reach Great`
> `[RESULT] Changed: Vitality 12 → 9`

*What the trace shows.* The wild idea was never refused and never waved through: it was split into the
beats it really contained, the novel beat reached for the nearest anchor and the ledger, the precedent's
numbers were reused except where an established fact differed (and that departure is logged and flagged),
the player saw the odds and traded ambition for safety, and the claim check caught two of the most common
narration errors in the project's own logs — a possession change and a position change that no tool wrote
(R4 W9). *Non-example:* ruling the whole sentence as one Exert at DC 15 "because it's cool" and narrating
the archer off the rail on a success — three methods compressed into one roll (01.2.3), a lenient tier
chosen for drama (SG-01), and a precedent ignored (INV-19).

### WE-12-3 Full turn-loop trace 3: a soft-lock broken by lead injection

*Situation.* Back in Ashford the next morning. The player chases the burned rope but makes no headway.
Counter at 0.

| Beat | Declaration and resolution | Inconclusive? | Counter |
|---|---|---|---|
| 1 | "I search the ferryman's hut." Observe, Safe, Standard; DC 15 *(stored: the hut holds no clue placement; a sealed Oracle at creation said nothing is hidden)*. Secret frame. d20 = 9 → 12: failure → one vague impression: "someone left in a hurry" — but the hut's state was already narrated (dark, door shut) and the impression adds no fact the PC can act on. | yes: no new fact, no clock, no position, no reach | 1 |
| 2 | "Do I know anyone in town who'd want Hob gone?" Recall (common knowledge of Ashford). Safe. d20 = 6 → total 6 vs Easy 10: failure — nothing comes to mind. | yes | 2 |
| 3 | "I look for tracks along the riverbank." Observe with tracking: Wits +2, `deed.wilds.tracking` +2 = +4 vs Moderate 15 *(three nights of rain; stored tier)*; Safe. d20 = 7 → 11: failure, Safe → nothing. | yes | **3 → `trg.lead_injection` raised** |

*DM turn after beat 3.* T3 returns `trg.lead_injection`; it must be handled this turn (12.2.3). PR-12-3:
1. **Source ladder.** Rung 1: unfound clue placements of the scene's thread (`thr.missing_ferryman`):
   `clu.toll_ledger` (Grey Keep; reachable — a half-day's travel) and `clu.daughter_purse` (Maren, in
   Ashford; reachable now). Both eligible → tie. List weights: neither placement's holder is on the cast
   list (Maren not met; the toll-keeper met once, weight 1). Rotation ledger: `social` pillar at 7 scenes
   (overdue, threshold 6) vs `travel` at 3 → **Maren** (the stalest axis wins the tie).
2. **Form.** `roll_table(tbl.lead_injection, {phase: build})` d12 = **11**: "A plea for help from someone
   caught up in it." Fit `[J:flag]`: can Maren plausibly come asking for help finding her father? **Yes.**
3. **Tests.** Concrete (Maren, a named person) ✓; actionable now (she is here) ✓; connected (holder of
   `clu.daughter_purse`) ✓. Does not solve the thread (her purse clue stays sealed until a Talk unseals
   it) ✓; costs nothing ✓; not a threat ✓.
4. **Write.** Maren steps from walk-on to recurring (12.11.1) — she already exists with the thread's
   generated fields (name, gender, age) and now gains want "find — the truth about the past" (d20 = 2 /
   10), fear "being found out" (d12 = 6), voice register nervous (d8 = 6), habit "apologizes constantly"
   (d20 = 14), refusal "will not speak of their past" (d12 = 5); first interaction → reaction roll: she is
   unaffiliated; modifier +1 (Wren arrives as someone she hopes will help — `[J:flag]` citing the fact
   that she sought Wren out); 2d6 = 7 + 1 = **8 → Neutral (0)**. Fact `npc.maren_coldwell.approaches
   pc.wren`; `record_knowledge(pc.wren, "Maren is Hob's daughter", how: told)`. Counter → **0**.
5. **Narrate** it in this turn's world responses.
> The bank gives you nothing but rain-flattened reeds. As you straighten, a young woman is picking her way
> down the steps toward you, a shawl over her head, ink on her fingers. "Sorry — I'm sorry, you're the one
> who was asking after the ferryman? He's my father. Hob. Nobody will tell me anything." She glances back
> up the steps, then at you. "Please. I think he took money from someone, the day before."
> What do you do?

Her last sentence is the *offer* of a lead, not the clue: what she knows (the Guild silver) is still behind
`clu.daughter_purse`'s gate — a Talk to win her trust over her refusal to speak of the past (ch.15). *Boundary
pair.* After beat 2 the counter stood at 2: no injection — the DM's per-beat next-step check (12.8.3) was
satisfied by the visible riverbank and toll-house options. Had beat 3 succeeded (tracks found), the counter
would have reset and no injection would fire. *Non-examples:* (a) having a fishwife blurt "the Salt Guild
took him!" — that solves the thread (forbidden) and invents knowledge she lacks (12.10.6); (b) inventing a
fourth clue ("a Guild badge in the mud") — narration may not create clues (12.14.13); (c) waiting for the
player to ask for help — P16 says the DM must act at three.

### WE-12-4 Error correction: one caught before delivery, one after

**(a) Caught before the player saw it: the pronoun slip.** At the toll-house a week later, the draft
reads: "The toll-keeper looks up from her ledger." T9: `identity` claim "her" for `npc.toll_keeper_01` —
the store has no gender for this walk-on → verdict **undetermined** → `roll_table(tbl.npc_gender)` d10 = **7** → man, he/him, written →
redraft: "The toll-keeper looks up from his ledger." The player never sees the slip. (An earlier turn's T8 wrote the toll-keeper without the gender roll — itself an error the sweep would have
caught at scene end.) This is the exact
failure the project's first probe recorded and its self-assessment missed [C:P13]; the claim check catches
it because identity is a checked class, not because the DM "noticed".

**(b) Caught after delivery.** Turn 41: Wren's Observe in the toll-house archive succeeded and delivered an
item — an iron key on a hook (`obj.key_cellar` unsealed, `location: archive hook`). The delivered narration
said: "…an iron key hangs on a nail by the door. **You pocket it.**" The claim check that turn missed the
`pc_agency` + `possession` claim (no possession write; the player never said to take it). Turn 42 the player
talked with the toll-keeper about the tolls; turn 43 left the archive for the cellar stair. Turn 44: "I
unlock the cellar door with the key I took."
1. **T4 GATE** finds `obj.key_cellar` not in Wren's possessions → mismatch with the turn-41 narration →
   PR-12-4.
2. **Truth.** Is there a resolved source requiring possession (`[J:flag]`)? The frame delivered the key's
   *existence*; no beat took it → **narration error**; the store stands (the key is on the hook).
3. **Reliance.** Committed beats since turn 41 that cited, targeted or premised the key: turn 42's Talk did
   not mention it; turn 44's beat has not been committed (it is at GATE) → **no reliance**.
4. **Form.** An in-fiction reconciliation would need a new fact (that she dropped it, or never took it in
   some invented way) → not allowed → **OOF note**. Spent quantities because of it: none.
5. **Log**: correction record `{turn_of_error: 41, found: 44, by: gate, claim: "pc holds obj.key_cellar",
   store: "obj.key_cellar on the archive hook", kind: narration_error, form: oof_note, reliance: false}`;
   ruling `review_flag: true` (12.12.4: a correction).
Then the turn proceeds: the unlock beat is redirected by lookup — the cellar door is locked
(`door_cellar.locked = true`), the key exists and is reachable, so the nearest path is to fetch it
(picking it up is a free activity, 00.12.6; walking back up the stair is Trivial, 1 action):
> `[CORRECTION] On turn 41 I narrated you pocketing the iron key; you never took it — it is still on the nail by the archive door. Nothing you did relied on it. Logged.`
>
> The cellar door is solid oak, banded, locked. The key you saw is upstairs on its nail in the archive,
> a short climb back. What do you do?

*Variant with reliance.* Had turn 42 been "I show the toll-keeper the key and ask what it opens" (a Talk,
committed and rolled, premised on holding the key), reliance would be **true**, the beat in the current
scene: CHOICE — **keep** is not available (the frame's premise rested on the false possession); **accept
forward** (the conversation happened as resolved; Wren simply was not holding the key — the toll-keeper
answered a description) or **rewind** to before turn 42 (`revert_writes`; the Talk's roll logged void; the
player re-declares). *Non-example:* writing the key into Wren's possessions "since the narration already
said so" — a change written to match prose (INV-1; 12.3.2's asymmetry). The narration was wrong; the world
was not.

### WE-12-5 An NPC from first mention to memory

Wren walks into the Drowned Lantern. Draft T8 mentions "the man behind the bar" → a person, addressable →
cast list check: no barkeeper generated yet → **walk-on** (PR-12-5): role "innkeeper or tavern-keeper" (the
narration implies it; no roll); name `tbl.name_given` d100 = 29 → **Osric**, `tbl.name_family` d100 = 30
→ **Pike**; gender d10 = 9 → man, he/him; age d6 = 5 → middle-aged; detail d100 = 85 → "a ledger always
under one arm"; demeanor d12 = 11 → sly. Written before the narration; the narration calls him "the
barkeeper with the ledger under his arm" — not "Osric": Wren has not learned his name (12.10.2).

First interaction ("I ask the barkeeper if Hob Coldwell drinks here"): reaction roll — Osric is
unaffiliated as far as the store knows *(his Salt Guild tie is undetermined; it is settled only if he
becomes principal)*; modifiers: Wren arrives as a customer (+1); no others → 2d6 = **4** + 1 = 5 → **Wary
(−1)**. The question is SPEECH plus a FICTION_QUESTION about Osric's knowledge: does he know Hob drinks
here? Role knowledge (a barkeeper knows his regulars) → (d) common knowledge of the role → yes, and
whether he *tells* is his decision: no frame (Wren did not try to persuade), no want or refusal yet →
`tbl.npc_action` d10 = 5 + standing −1 = **4** → "wants something first: names a price". Voice: not yet
recorded (walk-on) — the DM voices him plainly; after this second-scene interaction trigger he will gain
want, fear, voice and refusal.
> The barkeeper doesn't look up from his ledger. "Hob? Might do. Might not." He turns a page. "Memory's a
> thirsty thing, friend."

Memory (12.11.7): written at RECORD — `{npc: npc.osric_pike, deed: "Wren asked after Hob Coldwell",
valence: none of the twelve fits a mere question → no memory}`; *boundary pair:* had Wren paid him (a
`helped` exchange, salience 1) or threatened him (`threatened`, salience 3 with a standing change), a
memory would be written, and the next time Wren walks in, `[J:flag]` "does a memory bear on this
exchange?" → the threatened memory (salience 3) leads his first line ("You. Back again — keep your hands on
the bar where I can see them.").

### WE-12-6 Scene framing, the scene test, and the tension update

*Tension update after WE-12-2's toll-house scene.* Chaos points: an opposition clock completed? No.
Cost S3+? No (S2). Staggered? No. Twist? No. Interrupt? No. The agenda ("Does Wren take the toll-house
before the bell is rung?") — answered at scene end: the mate reached the bell and rang it (ch.09 behavior;
the alarm clock completed) → **against** the hope (+1 chaos) and **opposition clock completed** (+1 chaos).
Control points: the PC overcame part of the opposition paying no cost heavier than S2 — the archer was
dropped, but the scene's opposition was not overcome (the mate rang the bell) → 0. Chaos 2 > control 0 →
**tension 5 → 6**. Intensity: conflict 2 + failed frames 0 (a near miss taken as success at a cost is not a failed frame) +
cost S2 paid 1 + opposition clock completed 2 = **5** → intensity max(5, 0 − 3) = 5 < 7 → still
BUILD.

*Next scene.* The player: "I ride back to Ashford and go to the Drowned Lantern to find someone who drinks
with Hob." Scene start: agenda "Who drinks with Hob, and what do they know?"; hope: yes. Expected scene:
"Wren finds Hob's drinking companion at the Lantern." `h.12.scene_test`: d10 = **3** ≤ 6 − 3 = 3 → deviates;
odd → **altered**. `tbl.scene_adjustment` d10 = **10** → "someone is already here for the same reason" →
walk-on (role from the adjustment: a stranger asking after Hob; gender d10 = **3** → woman; detail and
demeanor rolled; written). Is she with the Salt Guild? The DM's own question: Oracle **Even** (the Guild is
active in the thread, but nothing ties her to it yet), eventful `none`; d100 = **58** → yes → fact, and her
Guild sash is now an established visible detail. The drinking companion the player expects: his existence
is the player's premise — Oracle **Likely** (a regular has drinking friends), d100 = **47** → yes → walk-on.
Framing `[J:enum]`: **at the threshold** (new place, social). Impetus (a): the alteration.
> The Lantern is low-beamed and loud with fishermen; smoke hangs under the rafters. At the corner table
> by the hearth, a woman in a Salt Guild sash is leaning over a frightened-looking old man, speaking low —
> and you hear Hob's name. The door to the yard stands open behind them. What do you do?
*Boundary pair.* At tension 5, the same d10 = 3 would be > 2 → expected: Wren finds the old drinker alone.
*Non-example:* adding the Guild woman because the scene "needs tension" — no roll put her there.

### WE-12-7 A random event from Oracle doubles

The DM needs to know (for the narration of the Lantern) whether the keeper is behind the bar — its own
question: "Is the barkeeper at the bar?" Odds **Likely** (an inn at evening); eventful `none`. d100 = **33**
→ doubles; digit 3 ≤ tension 6 → **random event**, and the answer is extreme: **yes, and** (01.15.3).
- The "and": `tbl.meaning` (action) → verb d100 = **99** "warn" + subject d100 = **60** "a messenger" →
  interpretation, written as a fact: "and a messenger has just warned him to say nothing about the ferry"
  (`source: generation`) — a fact the player may uncover; it does not reveal any sealed clue.
- The event: `tbl.event_focus` d100 = **37** → **faction move**; faction list (weights: Salt Guild 2,
  Ash Wardens 1) roll → **Salt Guild**; meaning: verb d100 = **88** "seize" + subject d100 = **52** "a tax"
  → "Guild men are nailing up a notice: from today the Guild collects the ferry toll." Writes: `set_fact`
  (the notice; the Guild's claim on the toll); one tick on `clk.corner_the_salt_road` *(illustrative; it
  lists `random_event` as a tick source — Interface request to 11)*.
- Bounds checked: no harm, no cost, no license, no sealed fact, no thread resolved.
> Behind the bar, the keeper is pouring, his jaw tight; a boy in a Guild-blue cap is just slipping out past
> you. Through the window, two men are hammering a notice to the ferry-post across the lane.

### WE-12-8 Pacing: a setback, a recovery window, and a push

Three scenes later Wren loses a fight in the reeds to Guild riders and **yields** (ch.07) — a setback
(12.7.5). Intensity: conflict 2 + Dire failure 2 + cost S3 2 + Staggered 3 = 9 (capped 10) → **9** ≥ 7 →
PEAK; the scene ends → `standard` profile: **recovery for 3 scenes** (RELAX regardless of intensity).
During recovery: the scene test's *interrupted* reads as *altered*; an Oracle-doubles random event that
rolls *PC complication* (67–74) reads as *omen*; no pacing push. The World Turn still runs, and the riders'
clock still ticks from its own sources — the director suppresses only its own pushes. Lead injection would
still fire, without threat forms.

When recovery ends, `trg.pacing_push` is raised for the next `scene_start`. Candidates: (a) ch.11 bangs —
"the riders return to the landing" (threat, delta 3), "Maren is followed" (keyed to an NPC the PC dealt
with, delta 3), "a Guild clerk offers Wren work" (keyed to this PC's deed — the toll-house — delta 1);
(b) `tbl.vignette`; (c) the overdue rotation opportunity (`downtime` at 9 scenes). Phase target after
recovery: delta ≤ 1 and advisory ≤ fair → (a1) and (a2) are out; the clerk's offer (delta 1, keyed to this
PC and their deed — the most specific rung) wins over the vignette and the generic downtime opportunity.
*Non-example:* softening the riders' Vitality in the reeds fight once Wren was losing (12.7.6) — the
adaptation comes *after* the setback, as a choice of what comes next, never as a hidden edit.

### WE-12-9 Rotation, check-in weights, and the tie-break

At session 4's start the check-in (12.5.9) records: fights **less**, investigating **more**, others same.
Pillar thresholds become: conflict 12, investigation 3, others 6. Ledger after the next scene: investigation
4 (overdue: 4 ≥ 3), exploration 5, conflict 2, social 0. Facets: `deed.martial.archery` (specialty) 9 scenes
— **overdue** (8); `ab.quarrys_mark` *(illustrative; 05)* untested, acquired 5 scenes ago — **overdue** (4).
Framing the next scene, the impetus list reaches (f): the stalest axis relative to threshold is the untested
ability (5/4) → an opportunity where marking a quarry would matter is put in front of Wren — drawn from
state: the Guild woman from WE-12-6 is seen leaving town on the north road at dusk (a quarry to follow and
mark). Nothing forces Wren to use the ability; the opportunity is simply there.

### WE-12-10 Session open, a flag, and an adjust

*Session open.* `h.12.session_open`: preferences re-read (a flag "harm to children" set at session zero);
recap from state (120 words max, from the chronicle and the threads); then:
> `[SITUATION] Where: Ashford, Maren's cottage, morning · Pressing: The riders' search (sensed) · Threads: The missing ferryman; Corner the Salt Road · Open offers: the Guild clerk's work · Last time you said: "find out where they took Hob"`
The last session ended at rest with nothing pressing that scene → `tbl.vignette` d12 = **2** "someone you
know is in trouble" (threat-tagged; phase BUILD, allowed) → rooted in an existing NPC: Maren's younger
brother has not come home. The brother is a child → the content carries the flag's tag → FLAG pause before
narrating it:
> `[FLAG] This touches harm to children. Continue, veil it, or steer away?`
The player: "Steer away." → **adjust** (12.5.7), *replace*: the troubled person becomes Maren's elderly
neighbor (same mechanical weight: a known NPC in trouble, the same vignette row), written as a superseding
fact; logged in the safety ledger, not as a correction.

*Session close.* The player: "Let's stop." Wren is mid-conversation (no frame past ROLL) → nothing to
finish; `mark_boundary(session_end)`; the review list compiles one flagged record this session (r.0533's
departure); no Principle III candidate (one record, one session);
> `[SESSION] Ending here — anything to focus on next time? (optional)`
> You leave Maren at her door with the morning still grey; the north road waits.

### WE-12-11 A world from nothing: the High Fells (the world seed, oracle mode)

The player opens a new game with no setting. Session zero's preferences are recorded (12.5.1); the DM asks
the mode, and the player says "surprise me": oracle mode (12.16.2). Every number below is
`_process/simulation/12-world-seed.py`'s seed 1, committed as `12-world-seed-example.yaml` [revision: I-028].

| Step | Rolled (oracle) | What it wrote |
|---|---|---|
| 1 Premise | wound **invasion**; climate **highland** | the High Fells: *"The horde came down from the passes thirty winters ago and burned the High Fells to the river. It was driven back. The watchfires on the passes were lit again this spring."* Three truths (the horde gathers again; some veterans took its gold; the pass forts are under-held). |
| 2 Canon | magic **rare**; open magic **feared**; spirits rare; arcane: anyone literate; one extra impossibility; no regrowth; no school closed | `canon_impossible`: the six defaults plus "No working makes gold, silver or gems". A visible working in Merestead's market is a method consequence (01.11.2). |
| 3 Faith | three keepers: war, knowledge, sky; bargainer: a tempter | **Oswen, Lord of the Line** (smiting, oaths, warding; courage +, loyalty +) is the main keeper; Halda, the Keeper of Keys, and Ala, the High One, have petty faiths. `canon.default_bargainer = arch.tempter`. |
| 4 Peoples | halflings common; humans, orc-kin and beastfolk uncommon; dwarves, goblin-kin and giant-kin rare; elves absent | seven name tables (humans uncommon: one style; the orc-kin's also serves the horde); second tongue: the Old Tongue, "the speech of the time before the Burning". |
| 5 Land | ring 1 farmland and hills; rings 2–5 mostly mountains and hills, a ruin, a moor, a wood | 13 areas (3, 3, 3, 2, 2) with T-10-2's bands and ratings, 35 places in all, every one reachable from the haven. |
| 6 Haven | a **town** at a **harbour** | **Merestead**: temple of Oswen (consecrated, resonance divine), the Golden Hound inn, smithy, hall, quay, market square, healer's house, graveyard; market depth 150; hire up to band 2. Place of acceptance: Shepwell Spring and its lady (weather, growth, elements). |
| 7 Factions | rulers **a noble house**; fourth **a town council** | the lords of Hawkgate (tier 2, goal 4/12: *humble the rival house*); the faithful of Oswen (tier 2, 3/12); **the Horde of the Millwick** (tier 3, aggressive, 4/12: *break the watch on the passes and burn the lowlands again*; −2 to both); the council of Merestead (tier 0, 1/8); two petty faiths. Every linchpin's four fates sealed. |
| 8 Cast | 12.11.1's tables | 17 NPCs: heads and officers (Tible of the Wet Warren, the goblin-kin lord; Milby Greenfoot, Oswen's halfling priest; Brugnak Three-Scar of the horde), the smith, innkeeper, gate captain Loran Millbrook and the sellsword Zzirik Swift (both recruitable), Shepwell's wise-woman, a scribe, a healer. 13 teachings. |
| 9 Sites | 9 sites and 2 lairs | e.g. Whitfield's Temple (haunted temple, band 1: *the dead rising tonight*, sealed); **Wolfcrag's Delving** (fortified mine, band 3: the horde's seat); lairs Whitmouth's Undercroft (band 5) and the Delving of Ashhollow (band 5). Situations: *War comes* in the Hungry Pikes (step 1 done: the levy called) and *The hunting ground* in the Sunken Fells (a savaged ewe). |
| 10 Tables | PR-10-10 at each area's band | 13 regional tables, all passing PR-10-8. The Drowned Ridge (home 2): 4–6 raptor minions and two orcs at band 1; a dwarf holdguard elite, a monstrous beast elite (complication), two frost elementals, two ancestor spirits at band 2; a bear minion and a wyvern minion at band 3. Words: 6 trivial, 3 easy, 11 fair. |
| 11 Rumors | `tbl.11.rumor_truth` per site | 20 rumors (11 true, 7 partial or distorted, 5 false): "Word is that the Horde of the Millwick will try to break the watch on the passes…" (true); "Whitfield's Temple is empty now" (false). |
| 12 Calendar | months **named** | the Month of Thaw, Plough, Lambing-month…; Oswen's Day (spring), the Midsummer Fair, Harvest Home, the Night of Remembrance; the era "years since the Burning". |
| 13 Opening | incident **missing** | the spring quarter day, 12 years since the Burning, dawn, Merestead's market square: a child is missing since last night and the trail leads out of the haven. Leads: Shephollow's Undercroft (ring 1), the war situation, the council's goal. Pregens: Fenbert Woodmore (Soldier), Magett Applefoot (halfling Thief), Osbert Elderley (Scholar), Evella Elderward (Acolyte of Oswen). |
| 14 Check | T-12-16 | 62 of 62 requirements hold. |

*Boundary pair — guided.* A second player answers fourteen questions themselves (a long winter, northern,
rare magic, two keepers of hearth and death, the death keeper bargains, a hill village ruled by a family, a
refugee opening, named months, no teleporting, the Old Tongue, and who may learn arcane magic) and leaves the
rest to the oracle (`12-world-seed.py`'s guided run): the result also passes 62 of 62. Their custom answer "magic is something only the old families do" is not
an option of `ws.q.arcane_source`; 12.16.2 classifies it as `order_only` (an admitting order: the old
families) and keeps their words as the canon fact's text — shown in `[SEED 2/14]`, where the player could
have corrected it.

*Boundary pair — a veto.* Had the player vetoed step 7's rulers (`[SEED 7/14]`), the d6 is rolled again
once, and steps 8–14 re-run, because the cast, sites, rumors and opening all read the factions.

*Tempting non-example.* Mid-session the player asks "who rules the next valley?" and the DM, remembering
nothing in the seed, answers "a cruel baroness". Wrong: a faction is never invented in narration (11.3.18).
The question is a FICTION_QUESTION (T4): the next valley is a new region past ring 5, so 12.16.18 runs steps
5, 9, 10 and 11 for it and 11.3.18's new-region rule writes its factions before a word is said.

---

## Edge cases & adaptation anchors

- **The player wants a setting they already know** ("like the Shire", "a city on stilts"). Guided mode with
  custom answers (12.16.2): each answer is classified to its nearest option, the player's words kept as
  description; what no option covers (a city on stilts) becomes the haven's `desc` and a place fact, never a
  rule. If they want chapter 13's Thallen Vale, load it as a pre-made seed and run 12.16.17 [revision: I-028].
- **The player wants no say at all.** Oracle mode; the one veto per step still stands, offered once at each
  `[SEED n/14]`.
- **A seed check fails** (a hand-edited seed, or a pre-made one missing a key). The failing requirement names
  its key and its step; that step re-runs (12.16.17). A pre-made seed missing a key gets the key from the step
  that writes it, with the seed's other content as input.

- **The player's message is several things at once** ("Stop — wait, I didn't have the torch. Anyway, I ask
  the guard what he saw"). Handle in 12.2.2's order: the dispute first (12.3.6), then the question to the
  guard (SPEECH plus a FICTION_QUESTION about his knowledge).
- **The player answers a pause with something new.** The pause's default applies (12.2.6) and the new
  declaration is processed; an open OFFER is withdrawn with nothing spent.
- **The player rejects an Oracle answer** ("no, I want there to be a back door"). Oracle answers are facts
  (01.15.5); the player may ask what would make a way out (a free OFFER on breaking a wall, a G0 question
  about windows), or, if the answer's *content* is a safety matter, use adjust (12.5.7). A preference is not
  a safety matter.
- **Two triggers fire that point opposite ways** (lead injection in PEAK). Lead injection fires (a lead is
  not a threat); its threat forms are excluded (12.7.2).
- **A trigger's handling would itself fire another** (a lead injection creates a hook whose clock
  completes). Each is handled in 12.2.3's order within the turn; a clock completion is a new causal root
  (00.8.6), handled once.
- **The DM is unsure whether a detail is furniture or a clue.** Uncertain → treat it as a clue and cut it
  (12.14.13). The cost of a missing chair is nothing; the cost of a manufactured clue is a corrupted mystery.
- **The player asks for more detail than the length limits allow.** The player's request overrides the limit
  (12.14.10); every sentence is still claim-checked.
- **A long time skip crosses a session boundary.** Sessions are not time (00.7.9); the skip resumes where it
  halted, at the next session, from state.
- **An error is found in a scene long past** that later scenes built on heavily. Correct forward, refund
  spent quantities only (12.3.4 step 3); if the correction makes a later scene's narration false, each such
  claim is corrected in the same OOF note, without rewinding.
- **The precedent ledger has no record but a near one** (same anchor, one delta different). It is not a
  match; frame fresh, log a new record — and the near one is shown in the RULING block if the player asks.
- **An NPC would plausibly know something only through magic or rumor.** Knowledge rule (c) or (a) only
  (12.10.6); otherwise the Oracle with role-based odds — the NPC never "just knows" for the plot.
- **The player stays silent about what they hope from a scene.** Hope null; the agenda rows of the tension
  table do not score (12.6.3).
- **The pacing director and a chapter's handler disagree** (a ch.10 watch check rolls an encounter in
  RELAX). The handler runs as written; the director never suppresses another chapter's handler. (Ch.10 may
  opt in to read the phase — Interface request.)
- **Anchoring the DM's procedures themselves.** When play produces a DM situation this chapter does not
  name, reach for: the claim check (anything the narration asserts), the Oracle or a table (anything the
  DM would otherwise decide), a trigger (anything that must happen "when"), the rotation ledger (any "what
  should this scene be about"), the ruling ledger (any repeat case), and a pause point (any decision that
  belongs to the player). Two-change limit applies to procedures too: adapt the nearest one by at most two
  steps, and log a `rule_conflict` ruling so the gap becomes a written rule.

**Anchor cards in this chapter.** None of 12's rules are action anchors (`Anchor: no` throughout): this
chapter governs how the DM runs the game, not what a character attempts. Its contribution to the anchor
substrate is the compiled index itself (12.13.6) and the procedure anchors listed in the last bullet above.

---

## State touched

**Reads** (through the narrator view and tools; 00.6 names): every state family the packet holds —
time and mode; the PC (attributes, competence, Vitality, harm state, Focus, fate, conditions, licenses,
callings, possessions, position, relationships, commitments); NPC records (identity, standing, wants,
refusals, knowledge, memories — sealed fields only as permitted slices); adversaries' tells and shown
descriptors; clocks (public fill; sensed existence; hidden only as returned omens); facts; knowledge
records; threads register, faction list, rumors and chronicle (ch.11); clue placements' status (ch.15/11);
frames; the ruling ledger; preferences (ch.14: lines, veils, flags, pacing profile, auto-commit, check-in
answers); `threat_advisory` (ch.09) for push filtering; `data/anchors.yaml`, `data/oracles.yaml`,
`data/pacing.yaml`.

**Writes** (this chapter owns): **meta** — tension, intensity, pacing phase, recovery and escalation states,
the inconclusive streak, the dead-air counter, the rotation ledger, cast and thread list weights, freshness
memory (12.14.11), the review list; **entities** — scene records `scn.*`; NPCs generated by 12.11.1 (fields per
depth); objects and places written on mention; **relationships** — the reaction roll's starting standing
(ch.15 owns its meaning thereafter); **knowledge** — PC and NPC knowledge records (12.10.5–12.10.6);
**facts** — Oracle answers to the DM's questions, meaning interpretations (`source: generation`), random
events, scene adjustments, lead injections, corrective writes (`source: correction`); **clocks** — instances
of the twist templates (`pacing.yaml#clock_templates`); **ledgers** — the turn log, the corrections ledger,
the safety ledger, NPC memories, ruling records (with ch.01).

**Tools used** (00.14.2): `frame_check`, `roll_check`, `read_result`, `deliver`, `apply_costs` (through ch.01's
pipeline); `oracle`; `roll_table`; `get_state`; `create_entity`; `set_fact`; `update_quantity` (refunds,
12.3.4); `set_relationship`; `set_position` (through resolutions); `record_knowledge`; `unseal`; `advance_time`;
`mark_boundary`; `create_clock`, `tick_clock`; `log_ruling`, `find_rulings`; `get_active_triggers`;
`load_cards`; `check_claims`; `chronicle_append`; `codex`. **Requested** (Interface requests): `log_turn`,
`revert_writes`.

**Hooks subscribed:** none (this chapter acts through boundary handlers and triggers, not effect hooks).

**Boundary handlers.** Reserved for 12 in T-00-9 and defined here: `h.12.inconclusive_streak` (`beat_end` 9;
12.8.1), `h.12.intensity` (`conflict_start`/`conflict_end` 9; 12.7.1), `h.12.scene_test` (`scene_start` 7;
12.4.4), `h.12.tension_update` (`scene_end` 9; 12.6.3), `h.12.bookkeeping` (`scene_end` 9, mirrored on
`session_end`; 12.4.8), `h.12.venture_bookkeeping` (`venture_end` 9; 12.4.9), `h.12.session_open`
(`session_start` 9; 12.5.2), `h.12.session_close` (`session_end` 9; 12.5.4, 12.12.4), `h.12.mode_change`
(`mode_change` 9; 12.4.5). **Added** (`data/boundaries.yaml owner-block 12`): `h.12.pacing_push` (`scene_start` 7;
12.7.4), `h.12.lead_audit` (`scene_end` 7; 12.8.4), `h.12.intensity_scene` (`scene_end` 9; 12.7.1–12.7.2),
`h.12.rotation_update` (`scene_end` 9; 12.9.1), `h.12.npc_memory` (`scene_end` 9; 12.11.7).

**Triggers raised:** `trg.lead_injection` (12.8.1), `trg.pacing_push` (12.7.2, 12.7.5), the flag trigger
(12.5.6).

**Clocks created:** only from twist rows, using the six templates `clk.twist_rival_first`,
`clk.twist_word_reaches`, `clk.twist_pursuit`, `clk.twist_ambush_prep`, `clk.twist_alarm_raised`,
`clk.twist_champion_hunt` (each with omens for every stage, 00.8.1).

**World seed** (12.16; written once at session zero): the region record (region, canon, keepers, peoples,
tongues, names, places, cast, factions, clocks, situations, encounter and rumor tables, calendar, opening,
pregens) and its provenance (`seed.answers`: each question's answer and source). Faction goals, linchpin
fates, rumor truths, site objectives and NPC secrets are `sealed`; the rest is `shown` or `available` as a
character raised there would know it [revision: I-028].

**Visibility** (00.6.4): tension, intensity, phase, streak, rotation ledger, list weights — `background`;
the turn log, corrections ledger, ruling ledger, journal — `available`; reaction-roll standing — `available`
(rung name); OOF blocks — `shown`; NPC secrets — `sealed`.

**Runtime capabilities assumed** (00.14.1): RC-RNG (every roll), RC-STORE, RC-SEAL (narrator view), RC-SCHED
(handlers, interrupts), RC-LOG (turn log, ledgers), RC-DATA (the three data files), RC-QUERY (anchor
scoring, list draws), RC-RETRIEVE (the packet), RC-AUDIT (`check_claims`).

## Interface requests

**To 00 (amendments proposed; the chapter works within 00 meanwhile):**
1. **Tool `log_turn(turn, player_text, response_text, parts)`** (RC-LOG) — the verbatim turn log (12.2.5) is
   the evidence base for disputes and corrections; no existing tool stores free text verbatim. Meanwhile:
   a `ledger` of kind `turn_log` written by the runtime.
2. **Tool `revert_writes(to_write_id, reason)`** (RC-STORE) — restores the store from write history for a
   rewind (12.3.4, 12.5.8), logging voided frames and RNG draws as void, never deleting them. Meanwhile:
   compensating writes that restore each changed field's prior value, with `source: correction`.
3. **Id prefixes** for 00.16.2: `anc.` (anchor index entries), `scn.` (scene records), `trg.` (engine
   triggers). Used provisionally here.
4. **SCHEMAS**: record the optional fields used in `oracles.yaml` and the extension keys of `pacing.yaml`
   (both documented in their headers and in this chapter's Tables), and add `clock_templates` as an optional
   key for any chapter that owns clock templates.
5. **00.15.4**: note the packet cap (core + at most twelve loaded cards) and the verbatim window (four
   exchanges) as ch.12's numbers in `pacing.yaml#packet`.

**To 01 (Resolution):**
- Satisfied: `tbl.twist` with rows for every severity S1–S5 (`tbl.twist_s1…s5`, d8 each, every row with its
  writes and fallbacks; S5 world events only); `tbl.meaning` (action and description pairs, 4 × 100 original
  entries); the 15 verb anchor cards compiled into `anchors.yaml`; 01.11.4's inconclusive definition used
  verbatim (12.8.1); tension shifts Oracle odds by at most one rung (12.6.4); the OFFER script renders 01.7.1
  items 1–7 exactly (12.15.2).
- Requested: in 01.15.2 decision 2, note that tension shifts only questions tagged with an **eventful
  answer**, and never a player's G0 question (12.6.4) — so a player's fishing is never moved by the dial.
- Requested: 01.11.3 source (5) already covers `h.12.pacing_push` (a boundary handler); an explicit mention
  ("…including ch.12's pacing push") would remove any doubt.

**To 04:** recognition offers are pause point 7 rendered as a CHOICE block (12.15.6); narration of
recognition obeys 12.14.5's forbidden list; calling, ability and tier grants create rotation facets (12.9.1).

**To 06:** the conflict-start transitions of T-12-3; range-band and flag wording T-12-11 (06 may refine);
reload state as a fact (`<entity>.loaded`) so it can be a lever (WE-12-2).

**To 07:** emit setback facts (`defeated`, yield, capture, Dying entry) as facts the director reads
(12.7.5); refine T-12-10's condition vocabulary if 07 sets its own descriptors.

**To 09:** per archetype, `reaction_roll: true|false` (12.11.2 step 4) and tells by band; `threat_advisory` as
the push filter (12.7.4–12.7.5).

**To 10:** watch and interval check rows may name `tbl.event_focus` for an "event" result (12.6.5 source d);
10 may opt in to read `pacing.phase` (e.g. to read an encounter as an omen during RELAX) — the director will
not do it for 10; falls of 20 ft and more as an S3 source (used in WE-12-2).

**To 11:** (a) thread progress clocks and faction goal clocks list `{on: random_event, ticks: 1}` among
their tick sources where random events may move them (12.6.5); (b) bangs carry `intensity_delta` and a
specificity key (`pc_deed` | `npc` | `faction` | `region` | `generic`) (12.7.4); (c) a thread status
`stalled` and a queued proactive fallback when the live-lead audit finds no lead (12.8.4); (d) every hook
writes ≥ 3 clue placements (with 15); (e) rumor entries carry `points_to`; (f) consume the scene-end and
venture-end chronicle line offers; (g) the S5 twist rows need haven, commitment and situation facts.

**To 13 (now the region's seed, 12.16: its cast and name tables; the rest stay generic, T-12-16 `ws.req.12_*`) [revision: I-028]:** region roster, role, name and furnishing tables replace the generic NPC tables; regional omen
lists may replace the twist templates' generic omens; a gender/identity table override if the setting
wants a different distribution.

**To 14:** render every OOF label of 12.15; preference records for lines, veils and **flags with tags** (so
`get_active_triggers` can match them), pacing profile, check-in answers, `next_time` notes; the turn log,
corrections ledger and ruling ledger as `available` views; session zero includes the pacing profile and the
first check-in.

**To 15:** consumes NPC generation fields (want, fear, refusal, voice) and the reaction roll's starting
standing; maps memory valences to standing steps (12.11.6–12.11.7); clue graphs with sealed nodes and ≥ 3
placements, whose delivery choices follow 12.10.4; `record_knowledge` semantics match 12.10.5–12.10.6.

**To 16:** companions are rotation facets; a companion's death is a setback (12.7.5). An ally's act with
none of 16.13.3's reasons is an `action` claim with verdict `unsourced_change` (12.3.1–12.3.2) [revision: I-030].

**Later chapters' "To 12" notes (reviewed for I-030):** every note from 01–11, 15 and 16 was checked against
this chapter; the ones not already in force were applied with `[revision: I-030]` markers (claim class `action`;
owed `[WARNING]`/`[STATUS]` blocks; the `[CONFLICT]` status line; ability, overdraw and relic-surcharge prices on
the OFFER; one-line drops; held abilities' cards in the packet; PR-06-6; T-12-3's rule numbers; ch.09's axes in
the rotation ledger; the reason-to-lie flag; T-15-2; T-09-13; the V face; ally deaths and personal threads).
The rest needed no text, with reasons in DL-12-25.

**World seed (12.16) [revision: I-028]:** **To 02** — C2 shows the seed's present peoples; the fast path's
tongue is the seed's `second_tongue`; names come from the seed's tables; pregens are the seed's (12.16.16);
faction ties read the seed's org-tie map (all applied in 02's text). **To 10** — the seed's regional tables are
built by PR-10-10 and audited by PR-10-8; its sites by PR-10-6 (applied). **To 11** — factions by PR-11-8 with
running goal clocks; situations from `world_turn.yaml` templates; the calendar's names (applied). **To 13** —
the Thallen Vale is one optional pre-made seed and must pass 12.16.17 like any seed. **To 14** — session zero
runs the seed after the preferences (12.5.1); render `[SEED n/14]`.

**To the orchestrator:** the Principle III candidate report (12.12.4) and rule-candidate list (12.12.6) need a
destination in the project record (proposed: `rules/_process/issue-ledger.md` at each playtest's end).

## Open empirical questions

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-12-1 | Is a four-exchange verbatim window the right trade between input fidelity and drift? | 4 (`packet.verbatim_exchanges`) | **T-12-WINDOW**: a 50-turn harness run at windows 2 / 4 / 8; count player-input conflicts (NCP's rule) and turn-loop step omissions per 10 turns; pick the smallest window whose input-conflict rate is within 1 point of the best |
| OEQ-12-2 | Does the claim check catch planted errors? | 12.3, two redrafts then plain fallback | **T-12-CLAIM**: 200 drafts seeded with one planted error each (pronoun, unsourced possession, position, leak, overreach, pc_agency); target ≥ 95% caught, and the plain fallback used in ≤ 2% of live turns |
| OEQ-12-3 | Do the pacing profiles produce the intended rhythm? | standard 7/2/3/3 | **T-12-PACE**: 3 owner playtest sessions per profile; log phase per scene and a 1–5 "pace felt right" rating per scene; target ≥ 4 average, with PEAK+RELAX between 20% and 45% of scenes |
| OEQ-12-4 | Is deviation at d10 ≤ T − 3 surprising enough without ignoring the player's plans? | T − 3 | **T-12-SCENE**: two 20-scene runs on the same seed, T − 3 vs Mythic's T; blind-rate "the world surprised me" and "the world ignored my plan" per scene |
| OEQ-12-5 | Is three inconclusive beats the right lead-injection threshold? | 3 (C:P16) | **T-12-LEAD**: count player "I'm stuck" messages and dead-end streaks across 5 sessions at threshold 3; if stuck messages exceed 1 per session, test 2 |
| OEQ-12-6 | Do the rotation thresholds keep facets and pillars alive? | pillar 6, challenge 6, facet 8, untested 4 | **T-12-ROT**: over 60 logged scenes, share of facets unused for more than 15 scenes; target ≤ 10% |
| OEQ-12-7 | Does a slightly guarded stranger (mean −0.25) feel right? | T-12-12 | **T-12-REACT**: 40 first meetings in playtest; player rating of "NPC reactions felt plausible"; shift the table one row if ≥ 30% feel too cold or too warm |
| OEQ-12-8 | Is the eventful-answer tag reliable? | 12.6.4 `[J:enum]` | **T-12-EVENTFUL**: 60 DM questions × 3 independent runs; target ≥ 85% agreement on the tag |
| OEQ-12-9 | Is five active memories per NPC enough for consistent recurring NPCs? | 5 | **T-12-MEM**: replay 10 recurring-NPC scenes with caps 3 / 5 / 8; count "the NPC forgot something it should remember" judgments |
| OEQ-12-10 | Do random events from Oracle doubles add life without noise? | T% per question | **T-12-EVENT**: log events per session and the player's "that mattered later" tag at session end; target ≥ 40% of events referenced again within 3 sessions |
| OEQ-12-11 | Does a world seed give a first session as playable as a hand-made setting? | 12.16 (14 steps, T-12-16's 62 checks) | **T-12-SEED**: Verification's three paper playtests run in `12-world-seed-example.yaml`; count first-session dead ends (12.8), questions the seed could not answer from state (an Oracle roll where a setting would have had a fact), and the player's "this place feels like somewhere" rating; target no dead ends, at most 3 setting gaps a session, rating ≥ 4/5 [revision: I-028] |
