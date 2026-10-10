# Spec 029: made-up and edge cases (written and committed before implementing)

Owner rule (DL-00-08, strengthened after round 8, DL-00-10): every fix passes made-up cases and edge cases, and the
breadth cases are **enumerated from every kind the data has**, not imagined. Each case is labelled **data-enumerated**
(one per kind in a table of the game's data), **playtest** (round 8, from the saves), **made-up** (a plausible play
situation not taken from a save) or **edge** (a boundary of the rule). Each becomes a test in
`tests/engine/test_spec029_cases.py`; the clue judgment's model cases are also items of the labelled sets
(`specs/025-hooks-clues-willingness/clue_set.yaml` for single questions, `clue_set_multi.yaml` here for messages with
several parts), measured on Haiku.

**What "has its terms" means, for every kind below**: when the lead or incident is made, (1) *who* (people by id,
bound or cast or created), (2) *what* (the act or event, as data), (3) *where* (a place bound or created) are written
as unsealed knowledge on the card of every person who would know; (4) *the words* of any document or message exist as
a `text` fact on a document entity made at the same time (a spoken message is a card field); (5) *the pay* where one
is offered is a job fee. Nothing a case seals (a node's answer) is on any card. A person asked "what / who / where"
about the lead has something to say; a document the player reads delivers its words.

## Data-enumerated: one case per kind (the table is walked by the test, so a new kind fails until it has terms)

### Incidents (`tbl.12.seed.inciting`, 8)
| # | Kind | Terms the test requires (beside the generic five) |
|---|---|---|
| K1 | alarm | what the watch saw at the gate (not the sealed war-band), who raised it, who saw it; at the gate |
| K2 | dying_messenger | the rider's dying words (the message) on the reporter's card, who heard them, where the rider fell; the person the message was for is the sealed subject (not on a card). The rider is a body on stage (an entity, dead) |
| K3 | missing | since when, last seen where (a place bound), who raised the hue, the reward (a job fee) and who posts it; a posted notice with the words; the missing person is the sealed subject (never on a card) |
| K4 | offer | the work, the pay (a job fee), the destination, the warning's words; held by the reporter **and the person on stage** (the offerer, the case subject, identity sealed) |
| K5 | theft | what is known of the loss (the niche empty at dawn, the seal broken), who found it gone, where; the sealed answer (what exactly was taken) is not on a card |
| K6 | omen | what was seen (a sign over the walls, in the sky or the earth), where, who saw it, who reads omens (the keeper's priest); the sealed answer (what it shows) is not on a card |
| K7 | refugees | the story they tell (words), where they are now (the group exists), who speaks for them (the case subject, **on stage**), who doubts them |
| K8 | duel | the challenge's words, the grievance, who was challenged, where; the challenger is the case subject, **on stage** |

### The situation's trace as a lead (`world_turn.yaml#situation_templates`, 16; lead 2 is one of them)
| # | Template (trace) | Document that holds the words (where) |
|---|---|---|
| K9 | feud ("hard words at the market") | none; the market people and the houses' heads |
| K10 | sickness ("a door marked with chalk") | none; the healer, the household |
| K11 | road_of_knives ("a looted wagon in the ditch") | the gate log: the wagon's departure line |
| K12 | succession ("two banners in the hall") | none; the hall's clerk and officers: whose banners |
| K13 | hunger ("long queues at the bakery") | the market's price board |
| K14 | hunting_ground ("a savaged ewe") | none; the shepherd, the near farm |
| K15 | the_rite ("a stolen bell, a missing sheep") | none; the temple warden, the farm |
| K16 | war_comes ("the levy called") | a muster notice at the hall |
| K17 | flood_and_fire ("the ford impassable") | the gate's board of closed roads |
| K18 | the_debt ("a bailiff at the door") | the bailiff's writ at the market |
| K19 | the_missing ("a mother asking at every door") | a posted description at the market |
| K20 | festival_trouble ("strangers buying lamp oil") | the market's sale tally |
| K21 | cursed_ground ("birds silent over the field") | none; the farmer, the hedge-wise |
| K22 | the_prisoner ("a closed cart on the road at night") | **the gate log**: the entry for the cart |
| K23 | scandal ("whispers in the hall") | none; the hall's clerk |
| K24 | the_enemy ("a familiar face in the crowd, gone") | none; the gate watch |

For each: who saw it (people by id), what they saw (the trace and its detail as data), where (a place bound), and,
for the ones with a document, a document entity at that place whose `text` is the entry. Never the situation's sealed
timeline (its later steps, its taker, its culprit).

### Other opening lead, documents, injection, rumor and hook kinds
| # | Kind | Terms |
|---|---|---|
| K25 | the hire lead (fourth faction) | task, pay, destination, contact (the head), the notice's words (already, kept) |
| K26 | document: hire | `text` exists; the contact and the members hold the job |
| K27 | document: warning | `text` exists; why (the reason), where it points, who to report to; the contact holds them |
| K28 | document: charter | `text` exists; whose right, since when (year), who judges disputes; the contact holds them |
| K29 | document: bounty | `text` exists; the reward (a job fee, not in the words), for whom, the contact |
| K30-K41 | lead-injection form 1..12 (`tbl.lead_injection`) | 1 someone brings it (a bringer by id, their words); 2 overheard (two speakers, the words); 3 a found object (an object with a `text`); 4 the opposition's mistake (a trace: object or place, naming the opposing faction); 5 a sign in the land (a place trace); 6 an old contact (a cast person remembers); 7 an offer (a cast person, their price in coin or favour); 8 someone seeks you out (a cast person, why); 9 a detail overlooked (an object or place here); 10 pressure shows itself (the threat's visible move, where); 11 a plea for help (a person in trouble, what they ask); 12 common talk (a public place, who is talking) |
| K42 | rumor: a faction's goal | who tells it (the people who carry it), what it says, where it points |
| K43 | rumor: a situation's trace | as K9-K24's witnesses; where it points |
| K44 | rumor: a site (true, partial, false words) | who tells it, what it says, the place it points to (all three wordings) |
| K45 | rumor: the keeper's dream | who tells it (the faithful), where it points |
| K46-K52 | creation hook: thread, rumor, npc, place, debt, enemy, question | the hook's text as data; who (the PC's bond NPC where the kind binds one: npc, debt, enemy, question), where (place, question), knowers; with no bond the hook has no knowers and is the PC's own note |

## Round-8 playtest cases (from the saves `playtest-20261010-0132*`)
| # | Label | Case | Pass when |
|---|---|---|---|
| P1 | playtest | Talker [19]-[23]: Fenwin looks at the gate log's last entry; "what does the entry say about the cart?" | The gate log is a document at the gate, made with the cart lead; its `text` is the entry. Reading it delivers those words (a `learned` fact); the part is marked answered because a fact was delivered. Never "waiting on your reading". |
| P2 | playtest | Talker: "whose cart was it, and where did it go?" put to the gate watch | The watch's card holds who (the carter and the owner's mark, by id), what, where it went; the answer has content, not a dodge. |
| P3 | playtest | Explorer [19]-[21]: "two banners in the hall"; the hall's people are asked whose they are | The clerk's and officers' cards hold whose banners (the two claimants), what, where. |
| P4 | playtest | Fighter: the duel opening. The case's challenger is the youth on stage | The opening's cast contains the case subject's id; the Director may not cast a second challenger; the scene knows them as "the challenger"; their name is sealed until the node is delivered. |
| P5 | playtest | Explorer [19]-[21]: "what do I know about the Long Downs and the winter that brought the realm down", after Betric said the banners are the old colours of the Long Downs, from before the winter | The answer lists the thread text (the wound), and **what you were told**: "Betric told you: ..." with the words; the compound is split; no "Nothing on record". |
| P6 | playtest | Explorer [18]: Betric (core holder of "who the challenger is") is asked "What are the banners, and who is the young man really?" at Standard reach, plain SPEECH | One clue judgment sees both parts. The clue is delivered **outside the cap** as a `learned` fact; the banners part is answered ordinarily; the challenger is the person on stage (P4). |

## Made-up and edge cases for P9 and the journal
| # | Label | Case | Pass when |
|---|---|---|---|
| C1 | made-up | Two questions in one message where the **second** is the clue question (the P6 shape, Limited reach, a Talk beat) | Delivered. The first part is answered ordinarily within `deliver_count`; the clue is not counted against it. |
| C2 | edge | Three questions at Limited reach (`deliver_count(3,1)=1`) with the clue **third** | Delivered outside the count; exactly one ordinary answer. |
| C3 | edge | One message of four parts: how many clue calls? | Exactly one (never one per part); zero when no open clue or no question. |
| C4 | edge | A question that sounds like a clue but is not ("who leads the evening prayers?" beside the refugees' clue) | Judged none: no delivery, no pointer; the part is ordinary. |
| C5 | edge | An Unfriendly (standing -2) holder of a core clue is asked it as the second part | Delivered (mood and ceiling never block 15.9.5). A recorded refusal covering telling still blocks it. |
| C6 | edge | A clue the PC already found, asked again as part 2 | Not re-delivered; no learned line; the part is ordinary and nothing says "answered". |
| C7 | edge | The holder is absent (the PC asks a non-holder present) | The non-holder's pointer to the holder, as a `learned` fact; no clue is delivered; the node stays unfound. |
| C8 | made-up | The delivery is a fact, not an act: speech with no Talk beat | `record.learned` carries the clue line; `record.npc_actions` has no line for it; the line names no speaker. |
| C9 | edge | A part answered by the clue judgment and a part answered ordinarily | Only the part that delivered a fact is `handled == "answered"`; the ordinary part is not stamped by this path. |
| C10 | edge | "who is <story role>" (typed) beside an ordinary part | The typed route delivers the case node without a model call; the cap counts only the ordinary part. |
| J1 | made-up | "What do I know about the miller's daughter?" after the baker said she "left with a tinker" | The baker's line is under the daughter, attributed ("Baker told you: ..."), labelled testimony. |
| J2 | edge | "What do I know about the winter and the banners?" | Split into "the winter" and "the banners"; each part is searched over thread text, said records and knowledge. |
| J3 | made-up | Two speakers contradicted each other on the same topic | Both lines are shown, each attributed; no verdict. |
| J4 | edge | Nothing known, nothing told | The existing "Nothing on record" line, with the three ways to find out. |
| J5 | edge | The compound is two real entities ("Gribnik and the sellsword") | Both entities' lines and each one's told lines; no thread name cut at 60 characters is matched. |
| S1 | edge | Sealed content: the card of every knower of every incident kind | Contains no node answer (the case subject's name, "a war-band of X", the relic's name). |
