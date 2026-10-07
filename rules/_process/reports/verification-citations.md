# Verification: web citations (V2c3)

Agent: V2c3 (Opus). Scope: every external URL cited in ch.02, 06, 07 and 10 (ledger rows I-010, I-012, I-014, I-021).
Nothing committed.

## Method
- Extraction script (regex over the four chapter files, deduped by exact URL): **63 citations, 39 unique URLs** on
  25 hosts (02: 10, 06: 14, 07: 9, 10: 6 unique by first citation).
- Each unique URL was to be fetched with WebFetch and the prompt "Does this page support the claim: <claim>?".
  Ten fetches were tried, mechanics first (07 dying/wounds: PF2e 2319, Cairn combat, Torchbearer FAQ, Blades
  harm, Dungeon World Face Death, Fate conceding; then Ironsworn, arXiv 2607.02802, 13th Age combat, Necropraxis).
  **Every one returned EGRESS_BLOCKED**: this session's network policy denies the host. A plain HTTPS probe of
  all 25 hosts through the session proxy also failed for every host (no connection). Per the proxy README, policy
  denials are not retried or routed around, so **no page could be read in this session**.
- Fallback check, done locally: whether the URL is listed in a research digest (`rules/_process/research/R1-R7`)
  under the same subject, or whether the same bracket co-cites a digest entry. This is provenance, not verification.

## Verdicts
| verdict | count |
|---|---|
| verified | 0 |
| partly verified | 0 |
| unreachable | 39 |
| wrong | 0 |

Of the 39: 17 URLs are listed in a digest under the matching subject; 21 are not listed but share their bracket with
a digest entry or DL row; 1 (#22, OSE morale) has no digest entry in its own bracket (the next citation in the same
sentence co-cites R1 §4 T-5). No citation was shown wrong, so no fixes were made (no `[verification: V2c-NNN]` tags)
and no ledger rows were opened: no rule's sole basis failed a check. #8 (PF2e free boosts, 02.3.4) rests on the URL
plus DL-02-04 only, with no digest entry; it is the first to read when the hosts are reachable.

## Hosts to allow (to finish this check)
2e.aonprd.com, arxiv.org, bg3.wiki, billhook.bearblog.dev, bladesinthedark.com, cairnrpg.com, cubicle7games.com,
darkestdungeon.wiki.gg, en.wikipedia.org, fate-srd.com, game8.co, necropraxis.com, oldschoolessentials.necroticgnome.com,
pelgranepress.com, roll20.net, rpgsystems.wikidot.com, samhaine.wordpress.com, sites.google.com, takeonrules.com,
thealexandrian.net, tomkinpress.com, troikasrd.ttrpg.tools, www.13thagesrd.com, www.dndbeyond.com, www.dungeon-world.com.

## Citations
| # | url | chapter:rule | claim | verdict | action |
|---|---|---|---|---|---|
| 1 | https://bladesinthedark.com/character-creation | 02:Design intent, 02:02.4.1, 02:02.9.2 | Blades in the Dark builds a character from separate heritage, background and playbook picks, each with a written detail | unreachable | none; digest backing: co-cited: R1 M-30 (url not in any digest) |
| 2 | https://en.wikipedia.org/wiki/Ironsworn | 02:Design intent, 02:02.3.1 | Ironsworn assigns stats from a fixed 3, 2, 2, 1, 1 array | unreachable | none; digest backing: co-cited: R2 02 (url not in any digest) |
| 3 | https://bg3.wiki/wiki/Character_creation | 02:02.2.1 | Baldur's Gate 3 offers a premade Origin beside a fully custom character | unreachable | none; digest backing: co-cited: R1 M-31 (url not in any digest) |
| 4 | https://takeonrules.com/2018/07/09/lets-read-stars-without-number-character-creation/ | 02:02.2.1 | Worlds/Stars Without Number backgrounds list quick skills beside the full tables | unreachable | none; digest backing: co-cited: R5 §4 item 6 (url not in any digest) |
| 5 | https://cairnrpg.com/second-edition/players-guide/character-creation/ | 02:02.2.2 | Cairn rolls attributes and then allows one swap | unreachable | none; digest backing: co-cited: R4 SG-12 (url not in any digest) |
| 6 | https://game8.co/games/BG3/archives/421001 | 02:02.2.6 | Baldur's Gate 3 lets a player rebuild (respec) at camp for a fee | unreachable | none; digest backing: co-cited: R1 02 (url not in any digest) |
| 7 | https://en.wikipedia.org/wiki/Mistborn_Adventure_Game | 02:02.3.1 | Mistborn Adventure Game ranks attributes strong, average and weak | unreachable | none; digest backing: co-cited: R2 02 (url not in any digest) |
| 8 | https://2e.aonprd.com/Rules.aspx?ID=2079 | 02:02.3.4, 02:Edge cases | PF2e lets any character replace an ancestry's boosts and flaw with two free boosts | unreachable | none; digest backing: co-cited: DL-02-04 only (url not in any digest) |
| 9 | http://rpgsystems.wikidot.com/burning-wheel | 02:02.4.1 | Burning Wheel builds a character from the lifepaths they walked | unreachable | none; digest backing: co-cited: R1 M-30 (url not in any digest) |
| 10 | https://roll20.net/compendium/13thage/Rules:Creating%20Characters | 02:02.9.4, 02:02.9.5 | 13th Age's One Unique Thing is narrative, never a mechanical grant | unreachable | none; digest backing: co-cited: R1 M-28, R2 02 (url not in any digest) |
| 11 | https://arxiv.org/abs/2502.19519 | 06:Design intent, 06:06.9.1 | An AI GM drifts in combat (target selection, consistency); static vs agentic GM study | unreachable | none; digest backing: R4 (url listed; W3/W12, §9 06) |
| 12 | https://2e.aonprd.com/Rules.aspx?ID=220 | 06:Design intent, 06:06.4.3 | PF2e three-action economy: costs vary by action, repeated attacks take a multiple-attack penalty | unreachable | none; digest backing: co-cited: R1 #7, R7 §5 Ex.7 (url not in any digest) |
| 13 | https://2e.aonprd.com/Rules.aspx?ID=2423 | 06:06.2.2 | PF2e rolls initiative from Perception | unreachable | none; digest backing: co-cited: R3 §06.5 (url not in any digest) |
| 14 | https://troikasrd.ttrpg.tools/the-rules/05-initiative/ | 06:06.2.2 | Troika uses a token-bag initiative (cited as considered and rejected) | unreachable | none; digest backing: co-cited: R3 §06.5 (rejected alternative) (url not in any digest) |
| 15 | https://2e.aonprd.com/Rules.aspx?ID=2541 | 06:06.2.4 | PF2e handles foes unnoticed at the start of an encounter (surprise/stealth initiative) | unreachable | none; digest backing: co-cited: R5 CF-01 (url not in any digest) |
| 16 | https://www.13thagesrd.com/combat-rules/ | 06:06.4.5, 07:Design intent, 07:07.4 | 13th Age scales weapon damage dice with level; 13th Age lets PCs flee at the cost of a campaign loss | unreachable | none; digest backing: R6 (url listed: "13th Age fleeing / campaign loss") |
| 17 | https://samhaine.wordpress.com/2020/04/06/savage-worlds-rules-summary/ | 06:06.4.10 | Savage Worlds called shots are a fixed penalty for a fixed effect | unreachable | none; digest backing: R7 (url listed) |
| 18 | https://2e.aonprd.com/Actions.aspx?ID=2256 | 06:06.6.2 | PF2e reactive strike triggers on leaving reach / manipulate actions | unreachable | none; digest backing: co-cited: R5 CF-07 (url not in any digest) |
| 19 | https://pelgranepress.com/2016/07/11/13th-age-mooks-destined-to-die/ | 06:06.10.1 | 13th Age mooks are pooled into a mob whose damage removes members | unreachable | none; digest backing: co-cited: R1 §06 #7 (url not in any digest) |
| 20 | https://2e.aonprd.com/Rules.aspx?ID=3365 | 06:06.10.1 | PF2e troops act as one creature with a shared pool | unreachable | none; digest backing: co-cited: R1 §06 #7 (url not in any digest) |
| 21 | https://cairnrpg.com/first-edition/cairn-srd/ | 06:06.10.1 | Cairn detachments: groups fight as one unit | unreachable | none; digest backing: R6 (url listed) |
| 22 | https://oldschoolessentials.necroticgnome.com/srd/index.php/Morale_(Optional_Rule | 06:06.11.1 | OSE morale checks at the first death and at half strength | unreachable | none; digest backing: co-cited: none in bracket; R1 §4 T-5 in the adjacent cite (url not in any digest) |
| 23 | https://billhook.bearblog.dev/saves-and-morale-in-shadowdark/ | 06:06.11.1 | Shadowdark morale: foes flee at half strength / leader death | unreachable | none; digest backing: co-cited: R1 §4 T-5 (url not in any digest) |
| 24 | https://2e.aonprd.com/Traits.aspx?ID=653 | 06:06.14.1, 06:06.14.2 | PF2e minions act only when commanded | unreachable | none; digest backing: co-cited: R1 §06 G-5, R5 CF-13 (url not in any digest) |
| 25 | https://2e.aonprd.com/Rules.aspx?ID=2319 | 07:Design intent, 07:07.2.8, 07:07.5.8, 07:07.8.8, 07:07.9.1 | PF2e dying 1-4, recovery check of rising DC, wounded condition, hero-point escape | unreachable | none; digest backing: R6 §C (url listed) |
| 26 | https://cairnrpg.com/second-edition/wardens-guide/combat/ | 07:Design intent, 07:07.7.3, 07:07.8.5 | Cairn damage goes to protection (HP) then flesh (STR); critical damage and scars | unreachable | none; digest backing: R5, R6 (url listed) |
| 27 | https://sites.google.com/view/torchbearerwiki/faq | 07:Design intent, 07:07.3.1 | Torchbearer closes the doors to death except in stated circumstances | unreachable | none; digest backing: R6 C-R1 (url listed) |
| 28 | https://bladesinthedark.com/consequences-harm | 07:Design intent, 07:07.8.8, 07:07.11.6 | Blades in the Dark harm levels, resistance rolls and trauma | unreachable | none; digest backing: R7 (url listed) |
| 29 | https://www.dungeon-world.com/not-the-end-face-death/ | 07:Design intent, 07:07.5.2 | Dungeon World's revised Last Breath / Face Death menu | unreachable | none; digest backing: R6 C-R3 (url listed) |
| 30 | https://fate-srd.com/fate-core/conceding-conflict | 07:Design intent, 07:07.4 | Fate lets a player concede a conflict and choose the loss | unreachable | none; digest backing: R6 C-14 (url listed) |
| 31 | https://darkestdungeon.wiki.gg/wiki/Stress | 07:Design intent, 07:07.11.4 | Darkest Dungeon: acting at Death's Door and stress breaks | unreachable | none; digest backing: R6 C-12 co-cite (url not in digest) |
| 32 | https://cubicle7games.com/en_US/blog/the-one-ring-the-shadow | 07:Design intent, 07:07.11.6 | The One Ring: Shadow points and permanent scars (miserable/flaws) | unreachable | none; digest backing: R6 C-19 co-cite (url not in digest) |
| 33 | https://www.dndbeyond.com/srd | 07:07.8.2 | D&D 5e SRD short and long rests | unreachable | none; digest backing: R5 HR-05, R6 (url listed) |
| 34 | https://arxiv.org/abs/2607.02802 | 10:Design intent | CoC-Seduce study: natural-environment adjudication is where every model family failed (mean error 9.76%) | unreachable | none; digest backing: R4 §9 10 item 1 (url listed, 9.76% matches R4 l.274) |
| 35 | https://necropraxis.com/2014/02/03/overloading-the-encounter-die/ | 10:Design intent | Overloaded encounter die gives every time-tick roll result a meaning | unreachable | none; digest backing: R6 B-14 (url listed) |
| 36 | https://necropraxis.com/2014/12/23/hazard-system-v0-2/ | 10:Design intent, 10:10.9.1 | Necropraxis Hazard System v0.2: one die drives encounters, depletion and omens | unreachable | none; digest backing: R6 B-14 (url listed) |
| 37 | https://thealexandrian.net/wordpress/17308/roleplaying-games/hexcrawl | 10:10.4.1 | Alexandrian hexcrawl: navigation check per watch, getting lost | unreachable | none; digest backing: R6 (url listed) |
| 38 | https://thealexandrian.net/wordpress/17464/roleplaying-games/hexcrawl-part-12-at-the-table | 10:10.4.2 | Alexandrian hexcrawl at the table: watch procedure, navigation and lost rules | unreachable | none; digest backing: R6 (url listed) |
| 39 | https://tomkinpress.com/pages/ironsworn-delve | 10:10.13.1 | Ironsworn: Delve sites are theme x domain; progress locates the heart | unreachable | none; digest backing: R5 P-28 (url listed) |
