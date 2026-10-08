# D. Adjudication, difficulty and player-facing presentation

Lane D of playtest round 2: handoff themes D (models choosing what code could choose), E (no difficulty rubric)
and F (player blocks read as rules text). The owner decision is I-158, with I-143 and I-155. Written 2026-10-07,
read-only on the repo. The odds below are exhaustive d20 enumerations under 01.8.1, done in a scratch script.
Web sources are cited inline. Anything marked *(unverified)* is from memory.

---

## 1. The problem, and how adjudication flows today

### 1.1 Current flow (PR-01-1 to PR-01-3, as built)

1. **Reader** (`engine/dm/roles/reader.py`, schema `engine/dm/schemas.py:reader_schema`). One Gemini call per
   message. For each beat it returns:
   - `verb` (an enum of 15);
   - `license` (the PC's held licences);
   - `would_be_license` (an enum of **all 83 licences**);
   - `gate` (G0–G4);
   - `necessity` (7 values);
   - `target` (scene ids);
   - free-text `intent` and `method`.

   Regex post-passes fix known misreads: `_knowledge_parts` for "what do I know" (P-038/P-115) and
   `_plain_reading` for reading a notice (P-110).
2. **Gate** (`engine/resolve/gate.py:check_gate`). The engine re-checks the *proposed* gate against holdings. It
   already overrides some proposals:
   - "G1 before G3": a basic verb with no named licence is G1 (P-031, P-038).
   - The speech-verb plain-form rule (P-122).

   It still starts from whatever class the Reader proposed.
3. **Framer** (`engine/dm/roles/framer.py`). One call per rolled beat. It picks:
   - the anchor (limited to the verb family since ea57355);
   - attribute, obstacle kind and tier;
   - up to 2 levers and 2 snags (any scene fact id);
   - stakes source and heaviness, lethal flag;
   - reach factors, threatened and alternate costs.

   `frame_check` refuses illegal frames. The schema already makes 8 of 17 illegal choices impossible (P-049,
   01a3737).
4. The engine computes the modifier, DC and odds (01.8.1, T-01-3). It renders the OFFER (12.15.2), then rolls,
   reads and delivers.

### 1.2 What goes wrong

**Wrong gates and verbs (theme D).**
- Redirects for things the sheet says the PC can do: P-004 (tracking), P-122 ("knack for intimidation" →
  "haven't learned Intimidation"), P-031 (gentle talk → "needs Stonesense"), P-038.
- Gentle acts framed as force: P-023, P-064 ("turn the child's face", Handle at 35%), P-123.
- Recall framed as Talk: P-115.
- The root cause is that the model fills `gate` and `would_be_license` from 5 × 83 options. The research is
  consistent here. Accuracy falls steeply with the size of the option set: gpt-3.5-turbo zero-shot drops from
  94.29% on 2 categories to 32.51% on 60 ([Lu et al., ACL Findings 2024](https://arxiv.org/html/2406.07001)).
  Shrinking the label space first helps (+3 to +14 macro-F1,
  [Haystack to Needle 2025](https://arxiv.org/abs/2502.08436)). Each patch so far moved one decision from model to
  code for one case. The structural fix is to move the whole decision.

**Harsh, flat odds (theme E).** The odds audit (I-158) shows the engine follows T-01-3 exactly. The harshness
comes from the Framer stacking choices that each have a defensible tie-break:
- "Between two rungs: the HIGHER" (01.6.5).
- "Uncertain snag → applied", and a fitting hindering fact must always be a snag (01.6.8).
- "Stakes tie-break TRUE" (01.6.9).
- "Roll tie-break TRUE", and any observer present makes a beat COSTLY (01.4.1).

Each of these is anti-leniency (SG-05). Their basis is real: in
[Seduced by the Narrative (2026)](https://arxiv.org/html/2607.02802), adjudication errors were overwhelmingly
lenient (9.58% false pass vs 0.08% false check). **But they compound.** "Push through a crowd":

| Step | Odds (success / crit failure) |
|---|---|
| Easy → Moderate (tie-break up) | −25 points |
| Two −2 snags | −20 more |
| **Result** | **10% / 45%** |

On a Risky frame, that critical failure is an S3 cost (01.9.2). Other cases:
- A first friendly question went 25% / 30%, with a sword blow as the critical-failure cost (P-107, I-155).
  Ch.15 already rules this exchange *certain*: Neutral standing, request size R1, T-15-3. The Framer picked a
  Moderate tier instead of the opposed social DC that code can compute (15.3.3).
- Opening an unbarred wicket got a full odds screen (P-024).
- Every fight action showed 60% whatever the approach (P-117).

**Rules text on screen (theme F).** Examples: "Mode: fallback — DC +5, reach capped at limited", "(time, S1)"
(P-005, I-134); "Go big" unexplained (P-028, I-138); "[CUT?]" with no hint of what Enter does (P-092); Enter
meaning Withdraw (P-044); hidden rolls that show no odds even though setup promised odds (P-051, I-143). The
engine's fixes rewrite strings (`plain_offer_words`, `_fix_pronouns`, `_difficulty_phrase`). That is theme G's
string munging, applied to the OFFER.

---

## 2. What the field does

### 2.1 Code decides, the model proposes

- **Shrink the choice, then let the model choose.** Two sources:
  - Two-stage "reduce then compare" lifted gpt-3.5 from 40.2% to 62.0% average accuracy on many-class intent
    sets ([Lu et al. 2024](https://arxiv.org/html/2406.07001)).
  - Retrieval prefiltering plus hierarchical selection reached 94.3% vs 58.6% for one-pass selection over
    thousands of labels ([arXiv 2412.05137](https://arxiv.org/abs/2412.05137)).

  The Reader's verb list (15) is already small. The 83-licence enum is the outlier.
- **Constrain the final object, not the reasoning.** In
  [Let Me Speak Freely (EMNLP 2024)](https://aclanthology.org/2024.emnlp-industry.91.pdf):
  - JSON formats *improved* classification. Gemini 1.5 Flash on DDXPlus went from 41.6% to 60.3%.
  - Answer-first JSON suppressed reasoning on reasoning tasks.

  Implication: put a short `why` field *before* any judgment enum. Gemini honours property order. Keep enums for
  pure classification.
- **Gemini limits.** Structured output supports string enums. With a schema, Vertex promises 100% valid JSON
  ([Google Cloud docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/control-generated-output)).
  But large schemas with long enum text fail with "too many states for serving"
  ([python-genai #660](https://github.com/googleapis/python-genai/issues/660)). There is no published
  enum-cardinality limit. Smaller enums are cheaper and safer.
- **Authoritative state beats model memory of rules.**
  - FIREBALL: structured state raised executable command accuracy from 23.5% to 72.6%. Still well short of safe
    autonomy ([ACL 2023](https://aclanthology.org/2023.acl-long.229.pdf)).
  - RPGBench: even the best model made mechanics errors in about 24% of rounds (Gemini 2.0 Flash MEC 0.765,
    [arXiv 2502.00595](https://arxiv.org/html/2502.00595)).
  - A GM given separate dice and state functions was rated most consistent (4.39/5,
    [arXiv 2409.06949](https://arxiv.org/html/2409.06949v1)).
  - DungeonBench enumerates legal options in code because decision spaces reach the hundreds
    ([arXiv 2607.29577](https://arxiv.org/html/2607.29577v1)).
- **Models are poor at ordinal ratings without anchors.** LLM judges show central tendency, round-number
  clustering, order effects and anchoring ([arXiv 2405.01724](https://arxiv.org/html/2405.01724);
  [2506.22316](https://arxiv.org/html/2506.22316v3)). Calibrated rubrics help (+13.4% Kendall,
  [AutoCalibrate](https://aclanthology.org/2024.lrec-main.237/)). This is the case for a rubric lookup over a
  free tier choice, with at most a bounded nudge from the model.

### 2.2 Difficulty design

- **D&D 5e DMG p.237–238.** "Only call for a roll if there is a meaningful consequence for failure." Most people
  manage DC 5 "with little chance of failure… let characters succeed… without making a check". "If the only DCs
  you ever use are 10, 15, and 20, your game will run just fine"
  ([DMG text](https://online.anyflip.com/tqblu/sfae/files/basic-html/page237.html)).
- **Fate Condensed** gives a *countable-factor* rubric. Not tough: Mediocre (+0), "or just tell the player they
  succeed". "At least one reason why the task is tough": Fair (+2). "For every extra factor working against them,
  add another +2." Low difficulties "give them a chance to show off"
  ([Fate Condensed](https://fate-srd.com/fate-condensed/being-game-master);
  [Fate Core](https://fate-srd.com/fate-core/four-outcomes)). Fate also sees "no real reason to keep difficulty
  secret".
- **Blades in the Dark.** "We don't make an action roll unless the PC is put to the test." The GM sets
  **position** (risk) and **effect** (payoff) independently. The default is Risky / Standard. Situation changes
  position and effect, never the player's dice
  ([action roll](https://bladesinthedark.com/action-roll),
  [position & effect](https://bladesinthedark.com/setting-position-effect)). The ruleset already borrows the
  vocabulary (stakes / reach, 01.7.3) but lets situation hit the roll too.
- **PbtA.** "To do it, do it": no move, no roll. With +1, a miss (6−) is 27.8% and 10+ is 27.8%. With +2, a miss
  is 16.7%. The miss band never exceeds the full-success band at an ordinary stat
  ([Apocalypse World basic moves](http://apocalypse-world.com/previews/BasicMoves2Epreview.pdf)). The GM move
  "tell them the requirements or consequences and ask" is the telegraph
  ([Dungeon World SRD](https://www.dungeonworldsrd.com/gamemastering/)).
- **Ironsworn.** Odds come only from stat + d6 against 2d10. Difficulty lives in progress-track rank and in how
  bad Pay the Price is. "On a miss: something always happens"
  ([Ironsworn SRD](https://tedtschopp.github.io/Ironsworn-SRD/Ironsworn%20SRD.html)).
- **Mythic GME.** Odds are words on a fixed ladder (Certain … Impossible) shifted by the Chaos Factor
  *(unverified detail)*. The ruleset's Oracle already uses this pattern.
- **PF2e degrees**, which 01.8.1 follows. Critical failure at margin ≤ −10 means low modifiers against high DCs
  give critical-failure bands far wider than success bands (T-01-3: −4 vs DC 15 = 10% / 45%). In PF2e that is
  acceptable because GMs rarely roll untrained PCs against level-appropriate DCs for everyday acts. Here the AI
  does exactly that.

### 2.3 Presentation in digital RPGs

- **Disco Elysium.** Hovering a check shows % chance plus a modifier list. Difficulty words (Trivial … Godly)
  name the *target number*, not the odds. White checks can be retried after a change; red checks cannot. So the
  colour signals commitment ([wiki](https://discoelysium.wiki.gg/wiki/Skills);
  [Kurvitz/RPS](https://www.rockpapershotgun.com/disco-elysium-rpg-details)).
- **Citizen Sleeper** separates the likelihood of outcomes from what a bad one costs, with labels SAFE / RISKY /
  DANGER ([TheGamer guide](https://www.thegamer.com/citizen-sleeper-beginner-tips-tricks-shortcuts-getting-started-survival/)).
  This is the closest analogue to stakes and odds.
- **Baldur's Gate 3** shows the DC and every bonus on the roll panel, with advantage as two visible dice
  ([TheGamer](https://www.thegamer.com/baldurs-gate-3-difficulty-class-dc-check-explained/)).
- **Griftlands** shows the opponent's *intent* and what it threatens, not a % chance
  ([PC Gamer](https://www.pcgamer.com/griftlands-complex-double-deck-building-shows-promise-in-early-access/)).
- **AI products.**
  - Hidden Door uses "a simple spinner indicating that an intent may or may not succeed" and avoids "a crunchy
    game of numbers" ([blog](https://www.hiddendoor.co/blog/techcrunch-demo)).
  - Friends & Fables removed default DCs on rolls ([patch notes](https://fables.gg/patch-notes/patch-notes)).
  - No AI GM product documents a pre-commit odds screen as complete as ours.
- **Number perception.**
  - Players read an 85% hit chance as "basically should not miss", so XCOM quietly inflates displayed odds
    ([Solomon, Game Developer](https://www.gamedeveloper.com/design/jake-solomon-explains-the-careful-use-of-randomness-in-i-xcom-2-i-)).
  - Sid Meier's testers felt a 3-to-1 loss was unfair
    ([GameSpot](https://www.gamespot.com/articles/meier-on-crafting-the-epic-journey-full-keynote-video-inside/1100-6253256/)).
  - Hiding odds inflates beliefs: in a preregistered 617-subject study, censored odds raised willingness to pay
    by 45% ([Cordes et al. 2024](https://eprints.soton.ac.uk/505957/1/1-s2.0-S016726812400369X-main.pdf)).

  The lesson is honesty plus words. Show the number, a plain word for it, and what failure costs, in that order.
  Do not fudge (Principle VII).

---

## 3. I-158: three options

**Shared baseline.** Every option fixes three things that are errors under the current rules rather than design
questions:

1. Social beats against an NPC always use the computed 15.3.3 DC, never a tier. Neutral R1 is therefore
   *certain*.
2. A cost must come from its stakes source (proposal 4).
3. Trivial acts don't roll (proposal 3).

**PC used in the examples:** Might −1, Agility +1, Presence 0, trained (+1) where relevant. "S/CF" means
success-or-better % / critical-failure %.

### Option A: guardrails on the current ladder (smallest change)

The model still picks the tier. Four rules bound the result:
- **Snag cap.** At most **one** cited Precision snag (−2). A second hindering fact applies as a Protective snag
  (stakes +1) instead. Engine repetition snags are unchanged.
- **Everyday tie-break.** For an act listed in T-00-5's new everyday rows (crowds, doors, ordinary climbs and
  carries, asking someone something), take the **lower** rung between two. Elsewhere, still the higher.
- **Critical-failure guard.** On a frame that is not Dire, not opposed and not secret, critical failure may not
  exceed success-or-better. `frame_check` refuses such a frame with the message "drop a snag or lower the tier",
  and the default frame applies on a second miss.
- **Roll test.** An observer makes a beat COSTLY only if they would *act on* a failure (are hostile, or the act
  is against their wishes). Mere presence does not.

| Case | Today | A |
|---|---|---|
| Push through crowd (Might) | Moderate, two snags: 10 / 45 | Easy, one snag (−2 vs 10): **45 / 10** |
| First friendly question | 25 / 30 | certain (no roll) |
| Thicket push, Safe stakes (I-143) | 20 / 35 | Easy, no snag (0 vs 10): **55 / 5**, or no roll if nothing presses |
| Shout to travellers | 25 / 30 | Easy (+0 vs 10): 55 / 5 |

- **For:** a prompt and `frame_check` change plus three rule clauses. No new data. Fast.
- **Against:** the model still makes the tier choice, so there is no consistency guarantee across turns or models
  (the Haiku vs Flash drift risk stays). P-117 flat odds are untouched.

### Option B: rubric lookup, code-computed difficulty, bounded nudge (recommended)

Includes all of A, plus:
- **Per-verb obstacle classes.** Each basic verb gets a short closed list of obstacle classes in
  `basic_verbs.yaml`, each with a base tier. Move, for example:
  - open ground: trivial
  - crowd: Easy
  - packed crush or rough ground: Easy
  - barrier or climb: Moderate
  - sheer: Hard
  - hazardous: by hazard

  Handle, Force, Observe and Recall get their own lists. The rows come from T-00-5 and 01.18.x, which already
  hold the examples.
- **What the Framer picks.** Only `obstacle_class` (≤6 options) and optionally `nudge` (−1, 0 or +1). A nudge
  needs a cited *intrinsic* fact id (01.6.5's "still true tomorrow" test) and a `why` field placed before it. The
  engine computes tier = base + nudge, then stores the DC as today.
- **Opposed beats** (Talk, Strike, Sneak against an aware watcher) always use the defense formula. The Framer
  only names the defender.
- **Odds vary by approach because the rubric is per verb and attribute.** The engine computes 2–3 alternative
  approaches at zero model cost and shows them under "Try another way" (proposal 5).

| Case | B |
|---|---|
| Crowd, slipping through (Move, Agility +2) | Easy, one snag: 0 vs 10 = **55 / 5** |
| Crowd, shoving (Move, Might +0) | −2 vs 10 = **45 / 10** |
| Talk R2 (a small favour), Neutral commoner | DC 12, +1 = **50 / 5** |
| Fight, fighter Might +4: Strike vs guard defense 12 / Grapple vs 13 / Feint (Wits +0) vs 10 | **65 / 60 / 55** (distinct per approach, P-117) |
| Worst model error | one rung (±25 points), always tied to a cited fact |

- **For:**
  - Same act, same odds, on any model.
  - The model's choice shrinks to ≤6 + 3 options, which is what the classification evidence supports.
  - Every DC can be audited from data.
  - Fixes P-117.
  - Removes the "HIGHER" tie-break as a judgement call.
- **Against:**
  - Authoring the class lists (about 15 verbs × 5 rows) and a data-generator change.
  - Odd acts may fit no class. The class `other` then falls back to Option A's model-picked tier with guardrails.

### Option C: risk out of the roll, Blades-style (largest change)

- The roll is the PC's: attribute + competence + Precision **levers** against **Easy (10)** for any unopposed
  act. Obstacle quality and situation move **stakes** (risk) and **reach** (payoff) instead, as in Blades.
- Hard intrinsic obstacles (a guild lock) become *Limited reach*, which means a progress clock, rather than a
  higher DC.
- Optionally widen critical failure to margin ≤ −15 for unopposed checks:
  - −4 vs 15: 10 / 20 instead of 10 / 45.
  - −2 vs 15: 20 / 10 instead of 20 / 35.

| Case | C |
|---|---|
| Crowd (Agility +2 vs 10), stakes Risky | **65 / 5** |
| Guild lock | 55%-ish per attempt, Limited reach (2–3 successes on a clock) |

- **For:**
  - The cleanest separation of "how likely" from "how bad".
  - The Framer only sets stakes and reach (two 3-rung ladders), the smallest choice surface.
  - Never harsh by stacking.
- **Against:**
  - Rewrites 00.3.8, 01.6.5, T-00-5 and the CT-1…CT-6 calibration. Every stored-DC and ch.07/09/15 sim would
    need re-running.
  - Odds for unopposed acts flatten. Approach variety comes only from attribute and levers, so P-117 gets
    worse.
  - Widening the critical-failure band breaks PF2e parity and every T-01-3 citation.

### Recommendation

**Option B, delivered in two steps.** Option A's four guardrails are a strict subset of B. Ship them first as
rules clauses plus `frame_check` and the prompt. Then add the obstacle-class data and the computed tier.

**Keep 01.8.1 and T-01-3 unchanged.** The critical-failure guard and the snag cap remove the harsh region
(critical failure > success) from non-Dire unopposed frames without touching the degree rule. CT-6 (≥ 50%
success ⇒ critical failure ≤ 5%) already holds and keeps holding.

**Answers to I-158's three questions:**
1. Everyday acts are Easy or no roll, by rubric row.
2. The snag cap is one Precision snag; further hindering facts go to stakes.
3. Critical failure may not exceed success except on Dire, opposed or secret frames. Opposed frames are
   honest contests, and a Dire frame is telegraphed with a warning.

---

## 4. Ranked proposals

Cost basis: Gemini 3.8 Flash introductory price, $0.75 / 1M input and $3.75 / 1M output, cached input $0.075 / 1M
(through 2026-12-31; it doubles on 2027-01-01) ([pricing](https://ai.google.dev/gemini-api/docs/pricing)). A
15k-token packet costs about 1.1¢ uncached and about 0.1¢ if the stable prefix is cached.

### P1. The gate is computed; the Reader proposes only verb, target and method facets

**Rules.**
- **00.12.3:** mark the class `[D]`. "The engine computes the class from (verb, method facets, held licences,
  the verb's `excludes`, active conditions, cited G4 fact); no role proposes it."
- **12.2.2:** the Reader's beat decisions shrink to verb (15), target, method facets, and the queued/conditional
  shape (I-146c). Method facets are yes/no questions:
  - `against_will`: acts on a person's body or property against their will;
  - `uses_power`: needs a supernatural or licensed technique;
  - `speech`: mainly words.
- **PR-01-5 step 1:** the would-be licence is looked up from the verb's `excludes[].needs` and licence data by
  code.

**Engine.**
- `reader_schema`: drop `gate`, `license`, `would_be_license`, `necessity`. Add 3 booleans and keep `g4_fact`.
- `gate.check_gate` becomes a pure function of facts. The verb plus facets choose the covering verb card:
  - `speech` and not `against_will` → Talk, so "gently take" is Handle, not Grapple.
  - `against_will` → Force, Grapple or Strike, by method.
  - A held licence whose scope tags match the verb and facets → G2.
  - A sheet knack (e.g. "intimidating") is an *edge*, never a gate.
- Delete `reader_check`'s G2 rule.

**Interactions.**
- **A (memory):** the Reader needs only the message, the last 2 exchanges, scene entity ids with short labels,
  and the PC's knacks as words. No licence list. That is about 1k fewer tokens. Precedents (12.12) for gate
  rulings are looked up by `gate_signature` in code, as today.
- **B (claims):** none directly. Fewer wrong-class frames means fewer narrations contradicting the sheet.
- **C (content):** "addressed NPC answers" (C's default layer) receives SPEECH parts unchanged.

**Cost:** about −0.05 to −0.1¢ per turn (smaller schema and prompt). It also removes whole wasted turns from
redirects; each redirect cost a full turn at about 1–3¢.

**Test.**
1. A golden set of ~80 player lines taken from the 62 runs (the exact inputs at P-004, P-023, P-031, P-038,
   P-064, P-115, P-122, P-123, plus neutral controls), labelled with verb and facets.
2. Run the Reader on Flash and Haiku, 3 seeds each. Targets: verb accuracy ≥ 95%, computed gate ≥ 98%.
3. A table test for `check_gate` covering every verb × facet × licence combination.

**Supersedes (delete):**
- the "G1 before G3" override and the `_plain_form_of` speech special-case in `gate.py` (1e3ec97, 1062541;
  P-031, P-038 gate part, P-122);
- reader prompt lines 41–47 on gates, would-be licences and "gentle touch" (ea57355, 1062541; P-023/P-064
  prompt patches, P-123);
- the `reader_check` G2 rule.

### P2. Difficulty rubric (I-158 Option B), with snag cap and critical-failure guard

**Rules (outline).**
- **00.3.8:** DC source order becomes stored → opposed / social 15.3.3 (mandatory for any beat whose `against`
  is a defense) → **rubric tier**. The rubric tier is the verb's obstacle-class base, plus at most one nudge
  citing an intrinsic fact.
- **T-00-5:** add a column "rubric class" and everyday rows (crowd, unbarred door, carry, ordinary question).
  **T-01-2** mirrors it.
- **01.6.5:** replace "Between two adjacent rungs: the HIGHER" with "the class's base. A nudge of one rung needs
  a cited intrinsic fact. Never two."
- **00.3.9(b) / 01.6.8:** "at most one cited Precision snag. A further fitting hindering fact applies as a
  Protective snag (stakes +1). The obligation to apply fitting snags stands." The ±4 cap stays for levers and
  engine snags.
- **01.6.12 (new clause):** the critical-failure guard. "On a frame not Dire, not opposed and not secret,
  `odds.critical_failure ≤ max(5, odds.success_or_better)`. If not, the engine converts the cited Precision snag
  to Protective. If it still fails, the OFFER is shown with the label *long shot* and the best computed
  alternative approach."
- **T-01-3 / T-00-6 / 01.8.1:** numbers unchanged. Add one sentence pointing to the guard.
- **Ch.15 first-contact guidance (I-155):** a first question to a stranger is SPEECH or R1 (certain at Neutral
  and above). T-15-3 already says so; 01.6.4 should cite it.

**Engine.**
- `basic_verbs.yaml` gets `obstacle_classes`. If the data is generated, change the generator in
  `rules/_process/simulation/*gen*` and re-run it.
- `framer_schema`: replace `obstacle.tier` with `obstacle_class` (verb-scoped enum) + `nudge_why` + `nudge`
  (−1/0/+1) + `nudge_fact`.
- Restrict `snags` to facts code-tagged as relevant to the verb's situation tags (≤8 candidates).
- `frame._dc` computes the tier. `frame_check` enforces the snag cap and the guard.

**Interactions.**
- **A (memory):** the Framer packet needs:
  - the beat;
  - ≤4 anchor cards;
  - the verb's class list;
  - ≤8 candidate facts, filtered by code;
  - stakes sources computed from state;
  - one precedent line if the obstacle signature has a ruling (12.12.1).

  No PC sheet (the modifier is computed). That is smaller than today's packet, and the static prefix
  (instructions, verb cards) can be cached.
- **B (claims):** the frame's typed fields (DC source, class, cited facts) give the narrator nothing new to
  claim. The checker can verify "the crowd parted" against `delivered.reach`.
- **C (content):** none.

**Cost:** about +40 output tokens when a nudge is given (+0.015¢). Social R1 beats skip the Framer entirely
(about −1¢ each).

**Test:** the seeded sim in §5. A unit test that every class row resolves. A playtest odds audit, which must show
zero non-Dire unopposed OFFERs with CF > S, and ≥3 distinct odds across offered approaches in ≥70% of combat
beats.

**Supersedes (delete):** framer prompt lines 22–27 (tier and snag tie-breaks), and the "Moderate default" in
`default_frame`. The fallback becomes the class base for `other`, otherwise Easy.

### P3. Necessity computed: a no-roll fast path and a quieter OFFER for safe beats

**Rules.**
- **01.4.1, COSTLY:** replace "when an aware opponent or observer is present" with "when an aware party would act
  on a failure (hostile, or the act is against their wishes)".
- **01.4.1, UNCERTAIN:** "trivial = the verb's class base is `trivial`".
- **01.7.4:** the default auto-commit preference becomes **on for Safe frames** (cost at most S1). The block
  shows as `[OFFER — auto]` with a one-line result, never for Risky, Dire or lethal frames. This answers P-024's
  "full odds screen for an unbarred wicket".
- **12.2.2:** the SPEECH/DECLARATION tie-break is unchanged, but a DECLARATION whose computed social DC is
  "certain" resolves without a roll.

**Engine.**
- A `necessity()` function in `engine/resolve/` computes the value from class base, stakes sources, ride state
  and social certainty. The Reader no longer proposes it.
- `_plain_reading` becomes one rule inside `necessity()`: reading words on record in a known tongue is trivial.
  It keys on verb plus target, not on regex over the method text.

**Interactions.**
- **A (memory):** needs the scene's awareness and disposition. That comes from C's default NPC layer (stance per
  present NPC), so it is a shared field, not prompt text.
- **B (claims):** for no-roll beats, the narration contract is "succeed at Standard reach" (01.4.1's bound).
- **C (content):** a GUMSHOE-style rule belongs here. If the requested information is a *core clue* (C's tier 3
  content), getting it never rolls ([GUMSHOE practice per HANDOFF §8]). The roll only buys extras.

**Cost:** saves a Framer call (about 1¢) on every trivial or certain beat. In the transcripts that is plausibly
20–30% of declarations *(estimate)*.

**Test:** the golden set gains expected necessity labels. A sim counter for the "no-roll share" of everyday acts.

**Supersedes:** `_plain_reading` (P-110 regex), the Reader's `necessity` field, and the costs.py ponytail
("observer is a judgement call"), which gives way to computed awareness.

### P4. A cost follows its source, and severity follows stakes

**Rules.**
- **01.6.9 / 01.6.11:** each stakes source in 01.6.9's closed list maps to the cost menus it may draw:
  - goodwill or trust → `cost.standing` / `cost.exposure`;
  - an armed opponent → `cost.harm`;
  - a clock → `cost.time`;
  - and so on.

  A first friendly question with a Neutral listener has the source "goodwill" (Risky at most). Its critical
  failure is a standing loss (S3 = "they take offence and remember"), never a sword blow (I-155).
- **01.9.2:** no change.

**Engine:** a table in `resolution.yaml` (or `costs.py`'s `uncited_by_stakes`, which already half-does this)
narrows the `threatened_cost` enum per declared `stakes_source` in the schema. It extends P-049's "impossible by
schema" approach.

**Interactions.**
- **B (claims):** the cost is typed (menu, severity, form), so the claim checker verifies the narrated price
  deterministically. That is the 00.13.1 contract made checkable.
- **C (content):** standing costs write ch.15 standing.

**Cost:** 0.

**Test:** schema unit test and an audit query across saved frames (no `cost.harm` without an armed or hazard
source).

**Supersedes:** the packet note from P-049 that covers cost legality, since the schema now enforces it.

### P5. Plain-language OFFER from typed templates, one menu convention, computed alternatives

**Rules: 12.15.2 is rewritten as a template over frame fields.** Every rule id stays out of the player text.
Proposed default:

```
Slip through the crowd toward the gate.
  Chance: better than even — 55%   (Agility +1, practised +1, packed bodies −2)
  If it works:  you reach the gate.          Very well (5%): and no one marks you.
  If it fails:  you're stuck and jostled — a setback.   Badly (5%): something's lost in the press — serious.
  Takes: a minute · noisy
  [Enter] Do it   [b] Go big   [s] Play it safe   [c] Another way   [w] Back off   [?] Explain
  Another way:  shove through (45%) · wait for it to thin (no roll, takes an hour)
```

- **Fixed word maps (a glossary, in rules):**
  - chance bands: 95 almost certain · 75–90 likely · 55–70 better than even · 45–50 even · 25–40 unlikely ·
    10–20 long shot · 5 only by luck;
  - severity: S1 a nuisance · S2 a setback · S3 serious · S4 grave · lethal "THIS CAN KILL YOU";
  - reach: Limited "partly" · Standard "what you wanted" · Great "more than you asked".
- **Show the number *and* the word.** Disco and BG3 show numbers. Citizen Sleeper and Hidden Door show words.
  The XCOM and Sid Meier evidence says numbers alone get misread.
- **Go big:** "Go big: if it works you get more; if it fails it costs more; same chance." **Play it safe** is the
  mirror (I-138 confirmed, shorter).
- **Mode and fallback (I-134):** "You're improvising without training: harder (+5), and at best a partial
  result."
- **Secret frames (I-143):** keep the stakes lines and replace the chance line with "You can't judge how hard
  this is." 01.7.1's promise is amended to "odds or the reason they're hidden".
- **One menu convention for every pause** (OFFER, CUT, near miss, redirect, last chance):
  - Enter = the labelled default, always printed (P-092, P-044);
  - letters for alternatives;
  - `?` explains any term from the glossary, not from rule cards.

**Engine.**
- `engine/dm/oof.py:offer_block` renders from typed `Frame` fields through a template module.
- "Another way" options are computed by the engine. They reuse the beat's DC source with the verb's
  `alt_attributes` and sibling anchors whose DC is computable without the model (opposed, stored, or same class).
  Zero model calls.
- The near-miss line stays as today but uses the severity words.

**Interactions.**
- **B (claims):** the "If it works / If it fails" lines are generated from `reach` and the costs. They *are* the
  promise the narration must keep (00.13.1, 01.7.2). The checker compares narration against the same fields, not
  against the prose of the OFFER.
- **C (content):** "If it works: you reach the gate" must name a deliverable C can fill. If reach at Standard has
  no store-backed content (I-153), the engine should not offer the roll. It answers "nothing more to learn here"
  or routes to C's generator first.

**Cost:** 0 (code templates).

**Test:** snapshot tests of rendered blocks for 20 canonical frames. A readability check that the block contains
none of the forbidden tokens (`S\d`, `DC`, `verb.`, `anchor`, `Mode:`). Player-persona notes on "didn't
understand the offer" should fall to near zero.

**Supersedes (delete):**
- `frame.plain_offer_words`, `_fix_pronouns` (ponytail) and `_fact_words` string rewriting;
- `oof._difficulty_phrase`;
- the TRADE_LABELS strings (af1fdce, 172b2b2; P-005, P-028 rendering part);
- the "what does X mean" answers drawn from 01.6.9/01.7.x card text, replaced by the glossary.

**Keep:** Enter re-prompts instead of withdrawing (P-044), the RESULT block after every roll, and "change asks
how".

### P6. Adjudication regression kit (golden set + sim)

This is the test harness for P1–P5 rather than a feature. It is listed separately because without it, every model
swap (Haiku → Flash → 3.8 Flash) silently changes difficulty.
- The golden set from P1/P3 lives in `evals/`.
- The seeded sim from §5 lives in `rules/_process/simulation/`.

**Cost:** about 80 Reader calls × 3 seeds ≈ 240 × 1¢ ≈ $2.40 per model per run.

### Fixes to keep vs retire

| Keep (the right idea, extend it) | Retire when P1–P5 land |
|---|---|
| 01a3737: illegal choices impossible by schema (P-049) | `gate.py` "G1 before G3" word-match override (1e3ec97) |
| ea57355: anchor candidates limited to the verb family (P-023, I-146a) | `gate.py` speech-verb `_plain_form_of` case (1062541, P-122) |
| `_knowledge_parts` pre-router for "what do I know" (P-038/P-115). Code routing obvious OOF patterns *before* the model is the right pattern; move it ahead of the Reader call to save it | Reader prompt gate, would-be-licence and "gentle touch" lines; `reader_check` G2 rule |
| 172b2b2: Enter re-prompts, RESULT after every roll, change asks how (P-044) | `_plain_reading` regex (P-110), folded into `necessity()` |
| Stored DC per obstacle + anchor signature (01.6.5) | `plain_offer_words`, `_fix_pronouns`, `_fact_words`, `_difficulty_phrase`, TRADE_LABELS (af1fdce) |
| Trade NOTE when a trade is taken (I-138) | Framer "Moderate default" in `default_frame`; tier and snag tie-break prompt lines |
| | costs.py "observer is a judgement call" ponytail |

---

## 5. Seeded sim design: `rules/_process/simulation/01-difficulty_rubric_sim.py`

Described here, not added to the repo.

**Inputs (in the script, seeded with `random.Random(158)`):**
- **Act corpus, about 70 rows.** T-00-5 typical and boundary examples, plus the logged playtest cases:
  - I-158 crowd and first question;
  - P-024 wicket and shout;
  - P-051 thicket;
  - P-107 friendly chat;
  - P-117 fight actions.

  Each row carries verb, obstacle class, intrinsic facts, situational hindering facts (0–3), stakes source,
  opposed defense (if any) and social standing × request size.
- **PCs**, from `archetypes.yaml`: untrained (attr 0, comp 0), P1 (+3) and P3 (+7) at the relevant attribute,
  plus an off-attribute variant (−1).
- **Variants:**
  - `as_played`: the current tie-breaks. Tier up when between rungs, every hindering fact a −2 snag, observer ⇒
    Risky.
  - `A`, `B` and `C`, as in §3.

**Computation:** exhaustive d20 for every act × PC × variant, using the same degree function as `odds01.py`.
Then a seeded Monte Carlo of 2,000 sessions of 30 beats (a mixed act draw) per PC, measuring streaks and
cost load.

**Model-error injection.** With seeded probabilities, simulate the Framer erring:
- tier ±1, p = 0.2;
- an extra snag, q = 0.2;
- stakes one rung high, r = 0.15.

This measures how much each variant *bounds* the damage. The expectation is that B caps tier error at one rung
with a cited fact, and the snag cap absorbs q entirely.

**Metrics printed (summaries only):**
1. Share of everyday acts that roll at all.
2. Mean success-or-better for everyday acts and for T-00-5 anchor acts, per PC.
3. Count of frames with CF > S, overall and on non-Dire unopposed frames.
4. Maximum CF at Safe and at Risky.
5. Approach spread: the number of distinct odds among offered alternatives, and their standard deviation (P-117).
6. Expected S3+ costs per 30-beat session.
7. P(3 failures in a row).
8. CT-1…CT-6 re-checked.

**Acceptance targets (proposal for the owner):**
- An untrained PC on everyday Easy-row acts succeeds ≥ 45% with CF ≤ 10%.
- Zero non-Dire unopposed frames with CF > S.
- A P1 at Moderate succeeds ≥ 50%.
- CT-1…CT-6 still pass.
- ≥ 3 distinct odds across approaches in ≥ 70% of combat beats.
- Under error injection, variant B's worst-case success drop per beat is ≤ 25 points.

**Output:** commit `01-difficulty_rubric_sim-output.txt` next to it. Cite it from the DL entry for I-158.

---

## 6. Risks and open questions for the owner

1. **Leniency backlash.** Computing gates and lowering everyday tiers removes the anti-leniency tie-breaks that
   SG-05 rests on. The leniency risk measured in *Seduced by the Narrative* was persuasive player text making
   *the model* skip rolls. Once necessity and DC are computed from data, player rhetoric can't move them. That
   threat is answered by code, not by harsh tie-breaks. Confirm the owner accepts this argument.
2. **Rubric coverage.** Some acts fit no obstacle class. The fallback `other` uses Option A guardrails. Ask the
   sim to report the share of acts that land in `other` (target < 10%).
3. **The critical-failure guard is a soft cap, not a new degree rule.** Is the owner comfortable that opposed and
   Dire frames may still show CF > S? For example, an untrained PC trying to outwrestle an ogre. The proposal
   says yes, because that is honest and telegraphed.
4. **Auto-commit on Safe frames** changes 01.7.4's default and 01.7's "the player sees the frame before the die".
   Offer it as a creation-time preference, defaulting to on?
5. **Numbers on screen.** The proposal shows both % and words. Some owners prefer words only, the Hidden Door
   style. Decide once, in ch.14's preferences.
6. **Facets vs verbs.** P1's three yes/no facets are a hypothesis. Confirm with the golden set that facets plus
   verb give the right covering card more often than today's free choice. If not, fall back to a two-stage
   Reader (verb family first, then card).
7. **Model drift.** Even with P1–P5, the Reader's verb choice is a model decision. Pin the golden set as a release
   gate for any model change (Flash version bumps happen every few months; prices double on 2027-01-01).
8. **Content dependency (C).** "Never offer a roll whose success has nothing to deliver" ties P5 to I-153. If C's
   content contract slips, keep the current stopgap and drop that clause from P5.

**Ruleset ids to revise** (each as a revision with a DL entry in `DL-CC.md`, re-assembled appendices, anchors
and a clean validator):
- 00.3.8, 00.3.9, 00.12.3, T-00-5 (+ T-01-2);
- 01.4.1, 01.6.5, 01.6.8, 01.6.9, 01.6.11, 01.6.12, 01.7.1, 01.7.3, 01.7.4;
- 12.2.2, 12.15.2 (+ a glossary card in ch.14), PR-01-5;
- notes only on 01.8.1, T-01-3, T-00-6.

Ledger rows closed by this: I-158, I-143, I-155, I-134, I-138, I-146a/c (with P1's shape field), P-024, P-117,
P-092.
