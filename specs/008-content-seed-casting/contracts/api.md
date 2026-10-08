# Engine entry points (part B calls these)

```python
# engine/gen/cast.py  (00.11.1 `cast`, social.yaml#cast)
base_pool(state, pc) -> list[str]                         # the gate's exclusions (ex incident._people)
cast(state, role, *, scope, topic=None, asker=None, exclude=(), faction=None) -> str | None
    # "who is <role>" (role) or "who would know <topic>" (topic); None = empty pool
pointer_target(state, topic, *, scope, asker=None) -> tuple[Literal["person", "place", "walk_on"], str]
    # rung 4: a person by cast, else the topic's kept_at place in the settlement, else a walk-on role to generate

# engine/gen/case.py  (PR-15-6 reduced profile, 15.9.4)
reduced_case(reg, seed, option, place, lead_target, tag="incident") -> dict   # on a region record (seed time)
validate_case(case) -> list[str]                                              # [] = valid
story_option(role_words) -> str | None                                        # who-question -> inciting option
case_for_question(tx, role_words, place, *, lead_target=None) -> dict | None  # on demand, writes to the store
case_covering(state, role_words) -> dict | None                               # an existing case for the question
pointer(case, node_id, *, asked=None, state=None) -> str | None              # the core holder first, else a live one
mark_found(tx, case_id, node_id, placement_id=None) -> None
cases(state) -> dict[str, dict]                                               # meta world.cases

# engine/dm/incident.py
incident_line(state) -> str          # the incident case as the PC knows it
start_knowledge(ctx, tx) -> list[str]  # I-149 name knowledge; returns the NPC ids named
settle_who(ctx, text, *, asked=False, exclude=()) -> tuple[str, str] | None   # unchanged signature (part B retires)
```
