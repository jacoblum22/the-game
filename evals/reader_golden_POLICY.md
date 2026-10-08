# Reader golden set: labelling policy

- **Date:** 2026-10-08.
- **Why:** spec 007's Reader scored 85.7% (verb) and 93.4% (gate) on `evals/reader_golden.jsonl`. Most misses were
  about beat segmentation: which act is the scored first beat when a move or gesture comes with words, and whether a
  plain question is SPEECH (no beat) or a Talk beat. The labels themselves disagreed on these points (g002 "step
  through ... and call" was labelled Talk, g027 "walk over ... and say" was labelled Move). A measuring stick with
  inconsistent marks is a harness bug.
- **How (blind, policy-first):** this policy was written from the rules only (12.2.2, DL-12-50, 01.2.1-01.2.6,
  01.14.4, 00.12.6, 00.12.3, 01.3.8, 12.2.9, 15.3.10, 14.6.3, T-00-11) before any Reader answer was opened. It was then
  applied to all 91 lines. Only after that were the stored Haiku answers rescored. A label was changed only where
  the policy requires it.
- **Caveat on blindness:** each golden line also carries a `recorded` field (the old play engine's answer, from the
  playtests). This is not the spec-007 Reader. The audit's first `head` of the file showed it for g001-g005. After
  that, every view of the file stripped it. No spec-007 answer (`evals/baselines/reader_golden_haiku*`) was opened
  before the relabel.

## Policy

### A. Parts and beats

- **A1. Classify each part first** (12.2.2 dec. 1). Only DECLARATION parts make beats. SPEECH, OOF_QUESTION, and a
  FICTION_QUESTION answered from state or the character's own knowledge (G0, 00.12.3, 01.3.8 (1)-(2), (4)) make no
  beat. For such lines verb, gate and necessity are null.
- **A2. "What do I know about X?" and "what are my options?"** are codex questions (OOF_QUESTION, 14.6.3, 12.2.2). They
  make no beat and have no question kind.
- **A3. A question that needs finding out is a beat.** Examples are looking, searching, reading a person, or recalling
  specialist lore. The beat is Observe or Recall (01.3.8 (3)).
- **A4. Free activities are never beats** (00.12.6; the closed no-roll list under 01.4.1). They include drawing,
  holding or stowing a weapon, putting down or picking up an unattended item, waiting, resting, speaking a few words,
  and looking around casually. A look the player makes explicitly casual ("without staring", a glance) counts as a
  casual look. A deliberate look, search or study is an Observe beat.

### B. Which beat is first

- **B1. The first beat is the first now-beat in the player's order** (12.2.2 dec. 2: "DECLARATION / SPEECH (in the
  player's order)"; 01.2.3: "resolves the first three in the player's order"). The rules give no priority to "the
  act the outcome depends on", so order in the text decides.
- **B2. Queued and conditional beats are not now-beats.** These are Ready beats such as "I'm ready if they draw" and
  "I attack if they keep stalling", and "if X, then Y" beats (12.2.2 dec. 3 shape; 01.14.4). They are skipped when a
  now-beat exists. A conditional with no other beat to wait on is this turn's beat (as `now_beats` reads 12.2.2).
- **B3. A move is not a free activity.** Move is a basic verb (T-00-11) and is not in 00.12.6's closed list. A move
  with an evident purpose of its own is its own Move beat (01.2.2: one beat per distinct (method, target, intended
  change); its split test passes because the words could still be said if the move failed). That purpose is getting
  somewhere: through a gate, over to a person or place, after someone, out of a room. If the move comes before the
  words, it is the first beat. Examples: "I step through [the gate] ... and call to the strangers", "I walk over to
  Seley and say".
- **B4. A step, posture or gesture whose only evident purpose is to support another act is part of that act's
  beat** (01.2.1: INTENT is "what the player wants to be true afterward", and such a step states no change of its own;
  01.2.2: no distinct intended change, so no separate beat). This covers:
  - menace: stepping toward someone while threatening, looming, slamming a fist (T-00-11 Talk: "Might (physical
    menace)");
  - manner: sitting "so I'm lower than her", leaning forward, turning toward someone;
  - attention: a tap on the shoulder, gently turning a face;
  - reach: stepping in to strike or grab. The 01.2.2 split test fails here, because the blow cannot be attempted as
    described without closing.
- **B5. Touching a person or what they hold against their will is its own beat,** for example grabbing a collar,
  shoving, snatching or clamping a mouth. It has its own change: the person is held, moved or deprived. So it is the
  first beat when said first, even when words follow (01.2.2; 12.2.2 facet `against_will`).
- **B6. Keeping up a state is not a new beat.** An already established grip or position ("I keep my grip on his arm")
  makes no beat.
- **B7. Verb = T-00-11's `covers` list, read literally.**
  - Forcing a way through a crowd is Move ("slip through a crowd"; other attribute "Might (force a way through)").
  - Shoving one particular person is Force.
  - Snatching a held item is Grapple.
  - Touching something to test it ("to see if it smears") is Observe ("study"), because the intent is to learn
    (01.2.1).

### C. Plain question: SPEECH or Talk

- **C1. The words decide, not the listener's inclination.** SPEECH is "in-character words that do not try to change
  someone's mind against their inclination ... plain questions. Whether an NPC answers a plain question is the NPC's
  decision (12.2.9)" (12.2.2). A plain question stays SPEECH even when the context makes the listener wary or evasive.
  The NPC's answer or refusal then comes from 12.2.9 and PR-12-10.
- **C2. A question becomes a Talk beat when its words try to move the listener.**
  - It asks for an act, an object or a favour, which is a request for a decision (15.3.10: plain speech "asks for no
    decision"). Examples: "ask the clerk to give me the ledger", "tell the smuggler to back off".
  - Or it carries pressure: a threat, an offer or bribe, a plea, or explicit insistence ("press him", "last chance",
    "enough dodging", "don't lie to me").
  - "Talk to X" with no content stated is a DECLARATION by the tie-break (12.2.2; 01.2.1 dec. 2).
- **C3. Tie-break.** When the classifier cannot tell whether the words try to move the listener, the part is a
  DECLARATION, which means Talk (12.2.2 default; SG-05).

### D. Facets and question kind on mixed messages

- **D1. Facets belong to the first beat** (12.2.2 dec. 3 records them per beat).
  - A Move beat followed by words has `speech` false. The words are another part.
  - A Talk beat has `speech` true and `against_will` false, threats included. Words never act on a body or property
    (12.2.2's definition of `against_will`).
  - `against_will` is true when the beat takes, restrains, moves or harms a person or what they hold without their
    evident consent. That includes "grab gently" when the item is taken from someone's hold. It is false for contact
    that leaves the person free (a tap, a guiding touch).
  - `uses_power` is true when the beat needs a supernatural or licensed technique.
- **D2. Lines with no beat have no facets in the rules.** The harness keeps a placeholder: `speech` is true for
  in-character words, and false for questions put to the DM. These values are not scored (see the scorer fix below).
- **D3. `question_kind` is the kind of the first question part in the player's order** (12.2.2 dec. 3: "question
  parts only"; the scorer reads the first part with a kind). It is independent of which part holds the first beat.
  - A question part asks for a fact. It can be direct, reported ("I ask him why ..."), or an imperative demand for
    information ("State your name", "Tell me about ...", "Name the price"). It can be put to an NPC or to the DM about
    the world or perception ("What can I see from here?").
  - Each such part takes the closest of the six kinds. A price, or what someone wants or feels, is `what_want`. "Is
    he your kin?" is `who_is`.
  - These are not question parts: phatic checks that ask for no fact ("Can you hear me?", "Did I hear right?"); codex
    questions (A2); and declared acts of finding out ("I try to remember what ...", "to see if ...").
  - No question part: `none`.

## Ledger rows raised (owner to rule)

| Row | Question |
|---|---|
| I-171 | B3/B4 |
| I-172 | C1 |
| I-173 | D3 |
| I-174 | D1 |

## Label changes (all 91 lines reviewed; 16 changed)

| Line | Field(s) | Old | New | Policy |
|---|---|---|---|---|
| g002 | verb, necessity, speech | verb=verb.talk, necessity=uncertain_and_costly, speech=True | verb=verb.move, necessity=trivial, speech=False | B1, B3, D1: "step through" the gate has a destination of its own and comes first; the call follows |
| g010 | question_kind | question_kind=what_like | question_kind=who_is | D3: "Can you hear me?" is phatic; the first question part is "Tell me your name" |
| g013 | question_kind | question_kind=none | question_kind=what_want | D3: "Name the price" is an imperative demand for what he wants |
| g014 | verb, against_will | verb=verb.handle, against_will=False | verb=verb.grapple, against_will=True | B5, B7, D1: the token is taken from the child's hold (T-00-11 grapple: snatch a held item), with no consent shown |
| g020 | verb, gate, necessity | verb=verb.move, gate=G1, necessity=trivial | verb=None, gate=None, necessity=None | B4, C1: sitting "so I'm lower than her" serves the words; the words are plain questions and an offer of help (SPEECH) |
| g021 | question_kind | question_kind=what_happened | question_kind=who_is | D3: the first question part is "he's your kin, isn't he?" (who is Liso) |
| g022 | verb, gate, necessity | verb=verb.observe, gate=G1, necessity=take_the_time | verb=None, gate=None, necessity=None | A1, A4: a look explicitly made casual ("without staring") is free, so the question is G0 |
| g026 | question_kind | question_kind=who_is | question_kind=what_like | D3: the first question part is "What can you give me?" (what is on offer) |
| g027 | speech | speech=True | speech=False | D1: the first beat is the walk (Move); the words are another part |
| g029 | speech | speech=True | speech=False | D1: the first beat is the walk (Move); the words are another part |
| g040 | verb | verb=verb.handle | verb=verb.observe | B7: touching the chalk "to see if it smears" is study; the intent is to learn |
| g047 | question_kind | question_kind=who_knows | question_kind=what_like | D3: the first question part is "What can I see from here?" (a FICTION_QUESTION about perception) |
| g051 | question_kind | question_kind=none | question_kind=what_want | D3: "whether he's scared of carts" is a reported question about what he feels |
| g058 | verb, against_will | verb=verb.force, against_will=True | verb=verb.move, against_will=False | B7, D1: shoving through a press is Move ("Might (force a way through)"); no single person is acted on |
| g059 | question_kind | question_kind=who_is | question_kind=what_want | D3: "what he wants for the name of the thief" asks for a price |
| g088 | question_kind | question_kind=what_like | question_kind=none | D3: "I try to remember what ..." is a declared Recall, not a question part |

No input text (`line`, `context`) was changed.

## Scorer fix

`evals/reader_golden.py` scored the facets on lines whose label has no beat (plain SPEECH, G0) whenever the Reader
proposed a beat. Facets belong to the first beat (12.2.2 dec. 3; policy D1/D2), so on those lines the comparison
was meaningless. It also counted the segmentation error a second time, after `verb` had already counted it. The
facets are now scored only where the label has a beat.

The scorer's other assumptions match the policy, so nothing else was changed:
- the first now-beat is the scored beat (B1, B2);
- the first part with a question kind is the scored kind (D3).

## Rescore of the stored final answers

This rescore used `evals/baselines/reader_golden_haiku.jsonl` through `py -3.12 evals/reader_live.py --cached`, with
no model call. "Facets" pools `against_will`, `uses_power` and `speech`.

| Measure | Old labels, old scorer (as published) | Old labels, fixed scorer | New labels, fixed scorer |
|---|---|---|---|
| verb | 85.7% (78/91) | 85.7% (78/91) | **83.5% (76/91)** |
| gate | 93.4% (85/91) | 93.4% (85/91) | **91.2% (83/91)** |
| facets (pooled) | 93.6% (205/219) | 94.2% (195/207) | **96.0% (193/201)** |
| - against_will | 93.2% (68/73) | 92.8% (64/69) | 92.5% (62/67) |
| - uses_power | 100% (73/73) | 100% (69/69) | 100% (67/67) |
| - speech | 87.7% (64/73) | 89.9% (62/69) | 95.5% (64/67) |
| question_kind | 82.4% (75/91) | 82.4% (75/91) | **85.7% (78/91)** |
| negation pairs: verb / gate | 95.5% / 100% | 95.5% / 100% | 95.5% / 100% (no pair line changed) |
| negation pairs: facets, question_kind | 98.4% (62/63), 100% | same | same |

Relabelling made verb and gate **worse** by two lines each. The Reader matched the new label on 9 of the 16 changed
lines:
- g002, g040: verb;
- g010, g047, g051, g059, g088: question_kind;
- g027, g029: speech.

It missed the new label on 6:
- g014: the Reader says Handle with `against_will`, and `covering_verb` keeps Handle;
- g020, g022, g058: verb;
- g013, g021: question_kind.

g026 is missed under both labels.

**Residual error under this policy.** The Reader's largest remaining error is the one policy B4/A4 rules out: it
makes a beat of a supporting step, posture or free activity. Examples: the step to reach in g004, the face turn in
g010, sitting in g020, turning toward someone in g031 and g037, resting (as Endure) in g048, staying put in g061.
Owner rulings on I-171..I-174 may move some of these lines. Until they do, the labels follow this policy.

The baselines `evals/baselines/reader_golden.txt` (the old engine's recorded answers) and `reader_golden_haiku.txt`
were regenerated against the new labels. The `_run1`..`_run3` files are kept as history.
