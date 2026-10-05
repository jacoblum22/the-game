## Traceability — 03 Tags and Evidence

| Clause | Requirement (short) | Satisfied by (rule ids) | Status |
|---|---|---|---|
| C:I | The AI DM is the mechanical engine; tools do the arithmetic | 03.2.2 (`record_evidence` validates, computes, stores, returns an id only), 03.4 (all points engine-computed), PR-03-1 (the DM's steps), PR-03-2 (settlement) | satisfied |
| C:II | A custom ruleset exploiting AI capacity | 03.1 (832-tag vocabulary with definitions and tests), 03.5 (per-node settlement at every level of the tree), 03.9 (eleven sealed measures) | satisfied |
| C:III | Flexibility within bounds; base-model judgment by default; no blanket override | 03.1.5 (tag classification `[J:enum]`), 03.3.3 (conduct `[J:flag]`/`[J:enum]` with citations), 03.3.4 (leniency bounds), 03.10.1 (witness flag); every `[J]` with a Worst case line; PR-03-4 (correction) | satisfied |
| C:IV | Single player, text only | 03.2.7 (PC and opted-in companions only) | satisfied |
| C:V | Closed primitives | 03.1.2 (bounded vocabulary, sibling budget of 8, level 4 reserved), 03.7.2 (closed counter list), 03.3.1 (closed basis enum) | satisfied |
| C:VI | Consolidation; provisional by default; no pure stacking | every tag and evidence.yaml entry `lifecycle: provisional`; PR-03-6 step 7 (retire with `superseded_by`, evidence carried to the successor); 03.6 (`recent` supplies 04's provisional confirmation and relabel inputs) | satisfied (inputs; mechanics in 04) |
| C:VII | Default-deny capability gate | 03.3.1 (evidence only from gated, resolved beats; G3/G4 never evidence); INV-7 respected: evidence never grants a license (04 does, through recognition) | satisfied |
| C:P2 | History-gated tiers; no separate level number | 03.9.2–03.9.4 (tallies are the only growth input; tiers key on them), 03.4.1 (harder-when-higher through relative quality), T-03-10 (slowing curve without a level) | satisfied (inputs; tiers in 04) |
| C:P3 | Granular state; classify background vs player-facing; reconcile | State touched table (ledger available; tallies sealed; public and last-exercised background), 03.9.5 (tallies recomputable from the ledger), PR-03-4 (void and re-settle), 03.11 | satisfied |
| C:P5 (hierarchy) | A narrow event counts at every level of its hierarchy at once | 03.5.2, PR-03-2 step 4 (cascade to every ancestor), 03.9.2 | satisfied |
| C:P5 (dual-tier, deterministic counters) | Eligibility gated by engine-tracked counters; primary and secondary requirement | 03.7 (counted tally), 03.9.4 (shapes 04 can require), 03.9.3 | satisfied (thresholds in 04) |
| C:P5 (specialist at any depth; hybrid by co-occurrence) | Dominance of one tag at any level; co-occurrence across unrelated branches | 03.9.3 `share`, `dominance`, `cooccurrence`, `profile`; T-03-10 balance figures | satisfied (callings in 04) |
| C:P5 (significance is base-model judgment) | The "does this count" call is the DM's judgment, not a trigger taxonomy | 03.3.2 (reads the DM's own pre-committed frame judgments), 03.3.3 (conduct judgment), 03.1.5 (tag judgment) | satisfied with a recorded refinement (DL-03-01; PATCH note requested) |
| C:P5 (values-expressive evidence with no dice) | Moments with no roll may be evidence | 03.3.1 basis `choice`, 03.3.3 | satisfied |
| C:P5 (self-correction; atonement) | No single judged moment locks in a result | 03.3.4 item 6 (blast radius), 03.5 (saturation), 03.8.3–03.8.4 (strain, atonement) | satisfied |
| C:P5 (capture mechanism) | Record that a significant moment happened and what it is evidence of | 03.2 (EvidenceEvent, `record_evidence`), PR-03-1 | satisfied (the deferred `tag_event` item) |
| C:P5 (resolved outcomes only) | Emergent content from resolved outcomes | 03.3.1, 03.2.6 | satisfied |
| C:P7 | Player-facing reference layer | 03.11.1 (ledger view for the codex) | satisfied (spec in 14) |
| C:P8 | Deterministic degrees | 03.4.2 (points read the computed degree; success-at-cost as success) | satisfied |
| C:P9 | One shared Focus pool | 03.7.2 `cnt.focus`, 03.7.4 | satisfied (evidence side) |
| C:P13 | Tools own mechanics; external store; verification independent of the narrator | 03.9.1 (sealed tallies never in narrator context), 03.3.4 item 4, 03.9.5 (audit from the ledger) | satisfied |
| C:P15 | Time-gated specialization as an alternative | 03.5.5 `cnt.training` (weeks trained, countable by 04/05) | supported |
| C:P16 | No silent dead ends | not applicable to evidence; 03.11.2 gives the player a dispute path | n/a |
| BRIEF §8 | Tag vocabulary content; `tag_event` capture mechanism | 03.1 + `data/tags.yaml`; 03.2–03.6 + `data/evidence.yaml` | resolved |
| 00.17.2 (03 contract) | tags below level 2; `record_evidence` and full schema; significance; weighting; saturation; recency; counted hooks; `tally` | 03.1; 03.2; 03.3; 03.4; 03.5; 03.6; 03.7; 03.9.2 | satisfied |
