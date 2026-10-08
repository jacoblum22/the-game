# Research and decisions: spec 006

Sources: `research_notes/Playtest round 2 solutions/` (00_SYNTHESIS §1.1, §2, §7; B P1, P3, P5, §4; C §4.1,
§4.4) and the R2-B rules. Clarify was skipped; each decision below is an assumption the owner can reverse.

**R1. Output shape.** `sentences[]` of `{text, refs, about, new[], atmosphere}`. `refs` = enum of record handles
plus the view's fact ids (the same `scene_facts` ids the view renders, so citing outside the packet is
impossible); `about` = enum of the scene scope; `new[]` = `{element_kind, name, ordinary, implied[]}`. The
fallback shape (config `narrator_schema: "fiction"`) is `{fiction, declarations: [{sentence: "0".."29", …}]}`
(string index: INV-3 allows no numeric field). Both become the same `DeclaredSentence` list. *Rejected:* a
trailing `mentions` list (P-002: the carry-over had to re-guess sentences).

**R2. Handles.** One handle per record line in `record_text` order. Must-name (12.14.12 plus B P1 (d) and
12.3.3's rendered-line list): each resolved beat's outcome, each cost form, harm, visible condition, changed
position, each delivered `learned` item, each Oracle answer, each NPC response, each omen, a lead or the
inciting incident, a "cannot make out" note. Citable, not must-name: activities, other notes, a scene header.
Guidance lines (speech, reading, pause) carry no handle.

**R3. Judging.** Per sentence: (a) each ref becomes a claim with the subject given (fact → its subject and a
class from its predicate; handle → the item's entity and class: beat → `outcome`, NPC response → `action`,
omen → `clock`, cost/harm/condition → `harm_condition`/`outcome`, position → `position`) judged by
`check_claims`; (b) Checker claims in the sentence take the declared subject when the sentence declares exactly
one non-PC subject and the Checker said `unknown` or another id; (c) an action claim whose subject's response
or beat handle the sentence cites is sourced by the citation, unless it asserts a change the cited line does
not cover; (d) a claim restating a cited line (75% of its words) is supported. This replaces `GIVEN_NOTES` /
`_restates_given` / `_reacts_to_incident` / `_atmosphere` / the addressed-speech exception and `_DEEDS`.

**R4. Undeclared sentences.** A sentence with no refs, `about` or `new` and no atmosphere flag fails only when
the name/numeral scans or the audit find something in it (12.3.1a: "code scans … the audit finds the rest");
otherwise it is atmosphere. A resolvable entity name missing from `about` is added by code and counted as
under-declaration (not a failure); an unresolvable mid-sentence proper name fails (redraft). An audit claim on
an undeclared subject is judged by its verdict and counted as an undeclared assertion.

**R5. Tiers and `undetermined`.** `element_kind` → tier from `pacing.yaml#claim_check.element_tiers`;
`person|item|document` with `ordinary: false` → T2; unknown kind → T2. T0/T1a written on mention (00.6.6);
T1b settled by the Oracle (Likely when a present NPC in `about` speaks it, else Unlikely); T2 passes only when a
cited handle's words cover the element's name, else cut. `undetermined` is incidental when the class is
`identity` (not name, gender or pronouns) or `possession` of an ordinary thing and the predicate is not a
consequential word (lock, armed, weapon, present, know, hidden, secret, trap, alive, dead); incidental →
written as narrated (fact, source `narration`); consequential → Oracle (`_settle`, kept for these only).
Principle I: 12.14.13's question is `[J:flag]`; code applies only 12.3.2's own enumerated consequential properties and its "uncertain → consequential" default (any class other than identity or ordinary possession is consequential), so code never rules a property incidental that the rule did not. ponytail: the word list stands in for the flag until a declaration field carries it.

**R6. Motive match.** Wants and refusals carry no tags. Code pre-filters each engaged NPC's motives by
content-word overlap with the event (the player's parts and beat restatements). No candidate → the action row;
one or more → the World call (now given only the candidates) decides when `world_judge` is on (default on),
else the best overlap. This keeps 12.2.9's `[J:flag]` with the model (Principle I) and makes the call rare
(walk-ons have no motives). The task wording said "two or more"; one candidate also needs a judgement, so the
call fires on one too. Recorded as a deviation.

**R7. Activity storage.** A fact `activity` (string) on the NPC, superseding the last; it is current when
written after the scene started (`valid_from_seq >= scene.started_seq`). Rolled for each present NPC without a
current activity, at T5 and before a scene-opening narration. Role → `tbl.npc_activity.by_role` key: the
role itself if a key, else the first word of the `tbl.npc_role` row that names it, else `other`.

**R8. Practice.** First of `select_order` whose test holds: fight (conflict mode, or a Strike/Grapple/Force
beat targets a person); trade (a talk/speech whose words name goods, price, buy, sell, coin, pay, trade);
greeting / conversation (an addressed NPC not yet / already spoken with this scene: meta `npc.spoken`
`{scene, npcs}`); crowd (a lead, incident note or violent beat, nobody addressed); work. Greeting vs
conversation is per NPC. Row clamp: nearest allowed row, toward 5 on a tie; row 1 allowed at Hostile.

**R9. Repair.** One narrow call per round: THIS MESSAGE = the record (handles) + the failing sentences with
failure and store value + missing must-name handles; schema `repairs[]` of `{replaces: "<index>"|"add", …a
sentence}`; an empty `text` drops it. Only the replacements go to the Checker. After two rounds: cut what
still fails; render uncovered must-name items in place of the sentence that cited them (else before the
prompt). The open prompt is restored only if the first draft had one and repair cut it. Screen failures that
belong to a sentence (mechanics, echoed quote, safety cut) become sentence failures; a whole-draft
substitution flag costs one full redraft.

**R10. Replay methodology.** The corpus has packets, not stores. The plug rebuilds a new-contract THIS
MESSAGE from the recorded record lines (handles assigned in order, must-name by line kind), enums from the
recorded view (fact ids, entity ids), calls Haiku through the Claude CLI with the new prompt, and judges with
`engine.audit.declare`'s packet mode (refs resolve to packet lines: support = packet, DL-12-42; scans; tiers;
coverage). Repair rounds call the narrator again; cuts and calls are counted. Store contradictions are not
measurable here; they are covered by unit tests and the long-horizon harness.

**R11. Oracle answers as statements.** Rendered from the entry's subject and predicate through
`render.relation(…, neg=answer == "no")`; when the predicate has no listed verb, a "yes" is the question's own
words and a "no" is left out (logged). No negation gloss is stored: the typed fields already carry it.
