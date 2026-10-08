# Playtest rounds

Engine model: Claude Haiku 5.5 via the Claude Code CLI; player: Claude Sonnet. No Gemini, no API spend.

## Round 1 (code ead9d5c, 5 personas × 40 inputs, ~25 of them setup)

| Persona | Play turns | Narrator calls/turn | Fallbacks | Notes |
|---|---|---|---|---|
| breaker | 7 | 2.14 | 3 | setup help loops (P-013), hidden lists |
| newcomer | 18 | 1.39 | 6 | never got the scene described (P-018) |
| explorer | 16 | 3.06 | 12 | fallback debug text, "what do I know" loops (P-019) |
| talker | 18 | 2.67 | 13 | raw NPC-action text (P-021), duplicate OFFER (P-020), rejected model output (P-022) |
| fighter | 18 | 2.67 | 9 | intent substitution to violence (P-023), odds on trivial acts (P-024) |

Fixed and merged into integrate-r1 (12f51f2), suite 996 passed, validator 0/0:
P-001 Oracle crash leak + CLI never prints engine errors · P-002 claim-check convergence · P-003 fallback reads as
fiction, time costs in words · P-004 held licence passes the gate · P-006/P-009/P-010/P-013/P-014 setup questions
answered, full lists, glosses, pronoun with name · P-016/P-018 mixed OOC+fiction messages narrated, checked
sentences delivered past the redraft budget. Harness: quick setup, 15-turn limit, faster CLI, pinned worktrees.
Ledger: I-131..I-136.

## Rolling runs (from 12f51f2)

| Run | Code | Play turns | Narrator calls/turn | Fallbacks | Main findings |
|---|---|---|---|---|---|
| breaker 170157 | 12f51f2 | 17 | 1.94 (r1 2.14) | 2 (r1 3 of 7) | prose now good; NPC replies cut (P-026); OFFER leaks (P-027); pause questions (P-028) |
| newcomer 170200 | 12f51f2 | 17 | 2.06 (r1 1.39) | 1 (r1 6) | setup now clear; NPC never speaks (P-026); talk redirected (P-031); movement unwritten (P-032) |
| fighter 170318 | 12f51f2 | 17 | 2.0 (r1 2.67) | 3 (r1 9) | odds screens clear; movement (P-032); success reveals nothing (P-025); note leak (P-034) |
| talker 170207 | 12f51f2 | 17 | 2.41 (r1 2.67) | 2 (r1 13) | conversations stall: NPCs never speak (P-026); friend bond contradicted (P-036); held until P-026 merges |
| explorer 170204 | 12f51f2 | 17 | 2.41 (r1 3.06) | 2 (r1 12) | NPC never answers (P-026); lore question → sorcery redirect (P-038); held until P-026/P-031 merge |
| newcomer 172552 | 790deb1 | 17 | 1.65 | 0 | setup fine; guard never answers (P-026); notice text contradicts itself (P-041) |
| fighter 172629 | 790deb1 | 17 | 1.65 | 2 | odds screens clear; fallback grammar (P-040); success gives no names (P-025) |
| breaker 172452 | 790deb1 | 17 | 2.35 | 2 | challenger never speaks (P-026); "what do I know?" unanswered (P-019); scene lines repeat (P-030) |
| newcomer 174833 | a184dff | 17 | 1.88 | 2 | setup fine; repetition (P-030); "the record holds" leak (P-045); arrival never a person (P-046) |
| breaker 175045 | a184dff | 17 | 1.47 | 1 | reach/Go big explanations clear; NPC reacted naturally; Luck question reframed offer (P-047); framer rejections (P-049) |
| fighter 174829 | a184dff | 17 | 2.47 | 3 | Go big dead end (P-050); odds band oddity (P-051); name collision (P-052) |
| explorer 174825 | a184dff | 17 | 2.53 | 3 | raw dict in OFFER (P-053); omen/notice not described (P-054); "what do I know" rolled (fixed since) |
| talker 175928 | 50f21c3 | 17 | 2.0 | 0 | first run with NPC replies: Borin answers well; a silent NPC stalls (P-056); roll results unclear (P-012); Enter=Withdraw trap (P-044) |
| breaker 181158 | 5ec5452 | 17 | 1.41 | 1 | change approach broken (P-057); learned facts raw (P-058); Fate spend unclear (P-059) |
| fighter 181737 | eeff286 | 17 | 1.47 | 2 | odds screens and Go big clear; cryptic condition redirect traps the PC (P-060) |
| explorer 181732 | eeff286 | 17 | 2.0 | 0 | storyteller never tells the story (P-061); journal labels (P-062) |
| newcomer 181028 | 5ec5452 | 17 | 2.06 | 0 | NPC's question never printed; notice words withheld (P-061) |
| talker 182337 | 04a3736 | 17 | 1.88 | 1 | NPCs silent (P-056/P-061); talk framed as force (P-064); child became a man (P-065) |
| breaker 183202 | 04a3736 | 17 | 1.47 | 0 | Bram never replies (P-061); roll results unclear (P-012); change approach (P-057); garbled OFFER fragment (P-066) |
| fighter 183858 | ae21453 | 17 | 1.71 | 1 | odds screens clear; missing person never named (P-067); NPC parrots the player (P-068) |
| newcomer 184243 | ae21453 | 17 | 1.24 | 1 | setup clear; witness talks but knows nothing (P-067: store holds nothing about the incident) |
| explorer 184224 | ae21453 | 17 | 2.65 | 0 | unintroduced name used (P-069); muddled reading of a bill |
| breaker 185133 | ae21453 | 17 | 2.0 | 2 | journal lists unmet people (P-070); options once unanswered (P-071) |
| fighter 185739 | 0a0acdf | 17 | 1.35 | 0 | "opening vivid, no complaints"; odds clear; raw source text (P-072); possession drift (P-073) |
| newcomer 190015 | 0a0acdf | 17 | 1.59 | 1 | Wanderer request ignored (P-074); NPC echo (fixed since in 00b6534) |
| talker 185715 | 0a0acdf | 17 | 2.12 | 2 | conversations work: "good NPC reply with some suspense", NPC agrees to meet; roll after consent (P-075); repeated refusals (P-078) |
| breaker 191540 | 1fd21f9 | 17 | 1.18 | 1 | vivid scenes, distinct NPCs; opening fell back (P-079); OFFER reprinted in full after a question |
| fighter 191941 | a42ed5e | 17 | 1.0 | 0 | zero redrafts all run; odds clear; tracking loop (P-082); generic cost text (P-083) |
| explorer 191535 | 1fd21f9 | 17 | 2.35 | 0 | hidden checks give nothing (P-086); name swap (P-085) |
| breaker 193315 | 9e4bd7f | 17 | 0.59 | 0 | CRASH LOOP from turn 6 (P-084), fixed |
| newcomer 192159 | a42ed5e | 17 | 2.18 | 2 | setup "fine" throughout; Try-it-anyway dead end (P-087) |
| talker 192340 | a42ed5e | 17 | 1.88 | 3 | refusals clear and fair; near-miss Enter default (P-089); early [CUT?] (P-088) |
| fighter 193420 | 9e4bd7f | 17 | 1.88 | 1 | kit weapon missing (P-090); possessive grammar (P-091) |
| newcomer 194948 | eac0c0f | 17 | 1.82 | 1 | setup fine; hidden success unnamed (fixed in 0c15da2); CUT prompt (P-092); month names (P-093) |
| breaker 195445 | b3adaaa | 17 | 1.35 | 0 | no crashes; cast inconsistency (P-095) |
| talker 194952 | eac0c0f | 17 | 1.71 | 1 | vivid; success reveals nothing when the store is empty (I-153); garbled journal (P-097) |
| explorer 194940 | eac0c0f | 17 | 2.24 | 2 | objects never described (I-153); travel arrival fallback (P-098) |
| fighter 195734 | b3adaaa | 17 | 1.71 | 3 | first real duel: odds/Go big clear; positions unwritten in conflict (P-099); harm not shown (P-101) |
| fighter 202001 | 7b46664 | 17 | 1.12 | 0 | no crashes; success-then-redirect confusion (P-104) |
| breaker 201338 | 7b46664 | 17 | 1.76 | 0 | two questions half-answered (P-080); unreadable bill unclear (P-105) |
| newcomer 201306 | 7b46664 | 17 | 1.76 | 0 | setup fine; hidden failure vague (P-106); object description drift |
| talker 201412 | 7b46664 | 17 | 2.0 | 2 | mostly clear/atmospheric; harsh social odds (I-155); fallback internal text (P-108) |
| explorer 201748 | 7b46664 | 17 | 1.76 | 0 | successes reveal nothing (I-153); detail repetition; journal wording (P-109) |
| newcomer 203722 | b3a579d | 17 | 1.65 | 0 | no errors; texts never readable (P-110); mist figure never resolves (I-153) |
| breaker 203717 | b3a579d | 17 | 2.12 | 1 | literacy breaks both ways (P-110/P-111); queue-note leak (P-111) |
| explorer 204217 | b3a579d | 17 | 1.94 | 0 | "fine overall"; success narrated as failure (P-112); NPC dodges (I-153) |
| talker 204112 | b3a579d | 17 | 1.71 | 0 | name mix-up (P-113); stonewalling alike (P-114); Recall as Talk (P-115) |
| fighter 205745 | 8fc6117 | 17 | 1.18 | 0 | first real combat: works, odds clear; foe strike unnarrated (P-116); flat odds (P-117) |
| newcomer 205857 | 8fc6117 | 17 | 1.59 | 0 | setup fine; NPC never states the warning/work (I-153) |
| breaker 210433 | 8fc6117 | 17 | 1.76 | 0 | harsh odds again (I-155); junk-object journal line (P-119); everyone refuses (P-114) |
| talker 210953 | 8fc6117 | 17 | 1.82 | 1 | real leads from Belo; success-then-refusal (P-120); coins ignored (P-121) |
| explorer 210627 | 8fc6117 | 17 | 2.41 | 0 | critical success still refused (P-120 high); proverb-dodging NPC; vague notice text |
| fighter 212725 | 06c7def | 17 | 2.06 | 2 | odds/grapple clear; knack vs licence redirect (P-122); gentle take = attack (P-123) |
| newcomer 212731 | 06c7def | 17 | 1.88 | 1 | NPC agrees but never says what (P-120); harsh call-out odds (I-158) |
