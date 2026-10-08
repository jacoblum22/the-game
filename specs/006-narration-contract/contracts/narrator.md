# Contract: Narrator output (replaces model-calls.md B's `fiction` + `mentions`)

Default shape (`narrator_schema: "sentences"`):

```json
{"sentences": [{"text": "…", "refs": ["R1", "fact.12"], "about": ["npc.tam"],
                "new": [{"element_kind": "furniture", "name": "a coil of rope", "ordinary": true,
                         "implied": [{"predicate": "location", "value": "by the door"}]}],
                "atmosphere": false}]}
```

- `refs` enum: this turn's handles then the view's fact ids; `about` enum: the scene scope; `element_kind` enum:
  `pacing.yaml#claim_check.element_tiers` keys. Empty enums drop the field (schemas convention).
- Fallback shape (`narrator_schema: "fiction"`): `{"fiction": "…", "declarations": [{"sentence": "0", "refs",
  "about", "new", "atmosphere"}]}`; sentences are split by code; an index without a declaration has none.
- Repair (narrow redraft): `{"repairs": [{"replaces": "3" | "add", "text", "refs", "about", "new",
  "atmosphere"}]}`; `replaces` enum = the failing indices plus `add`; `text: ""` drops the sentence.
- World tie-breaker: unchanged schema, `want_ids` / `refusal_ids` restricted to the candidates.

THIS MESSAGE record lines read `- R3 <line>`; guidance lines have no handle; a repair appends `REPAIR` with
`[i] sentence — failure; use: <store value>` lines and `MISSING: R2, R5`.
