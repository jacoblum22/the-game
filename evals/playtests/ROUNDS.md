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
