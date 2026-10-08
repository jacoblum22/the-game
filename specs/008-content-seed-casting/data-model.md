# Data model: 008 part A

Field lists follow the reference (`R2-D-report.md` "For the engine spec"); only the store mapping is new.

| Record (region record) | Fields | In the store |
|---|---|---|
| place pack | `look`, `furniture[]` (2-4), `exits[]` (place ids) | place entity `data` |
| NPC pack | `knowledge[] {fact, slot: trade/local/tie/rumor, topic, text, how: seed, tier}`, `stance {toward, stance, why}` | NPC `data`; `knowledge` sealed (`sealed_fields`) |
| walk-on (`reg.walk_ons`) | id, name, role, depth `walk_on`, home, member_of, knowledge, basis | NPC entity, `name_known: False`, positioned at home (not the missing subject) |
| document (`reg.documents`) | id `doc.<tag>`, kind `document`, option, at, text, table | `object` entity (data: kind, option, table) + `text` fact (available) + position `at` |
| lead (`opening.leads[]`) | + `document`, `names` | meta `world.opening` |
| case (`reg.seed_cases`; `reg.cases` lists ids) | id, profile `reduced`, trigger, option, opening_place, solution {subject {id, role, words}, leads_to, sealed}, nodes[2] {id, fact, necessary, points_to, placements[3], reserve[1]}, fallbacks, audit, basis | meta `world.cases` {id: record}; `world.opening.case` = id |
| placement | id, holder, holder_kind (person/document/place/object), method, access (core/rolled), at, content, status (unfound/found/lost), sealed | inside the case record |

State transitions (in play): node `found` (set when its answer is told: `settle_who`; later the ladder);
placement `status` unfound -> found | lost; reserve -> placed by `h.15.placement_audit` (appended to
`placements`, `audit_log` entry); a PR-15-7 generic placement when the reserve is spent.

Validation: `validate_case` (15.9.4 reduced numbers from `investigation.yaml#reduced_case`); `check_packs` (7 rows).
