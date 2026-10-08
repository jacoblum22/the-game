# Engine entry points (009 part A), for part B and the roles

```python
# engine/store/details.py
slots(rules=None) -> dict[str, str]                       # slot -> persistence (person and object lists merged)
write_detail(state, mint, eid, slot, value, *, source="narration", because=None, rules=None) -> DetailWrite
active_details(state, eid, rules=None) -> list[FactRecord]  # scene details, then the capped lasting ones
archived_details(state, eid, rules=None) -> list[FactRecord]
expire_events(state, mint) -> list[Event]                 # 12.4.8 step 8 (end_scene stages them)
used_event(fact_ids) -> Event                             # usage marks (part B emits at RECORD, T12)

# engine/retrieve/scene.py
alias_index(state) -> (strong, weak)                      # normalised key -> ids (PC-known names only)
resolve_names(state, text, index=None) -> list[str]       # ids named in text, full names first
spotlight(state, message="", last_delivery="", beat=None, *, k=None, scope=None) -> list[str]   # 12.2.4
scene_starts(state) -> list[int]                          # recency: the newest two scene starts

# engine/retrieve/episodes.py
cards_for(state, ids, k=2) -> list[SceneCard]                  # ended scenes; entity overlap, then recency
card_lines(state, card) -> list[str]                           # as the PC knows it

# engine/dm/packet.py
view_for(role, state, ctx=None) -> str      # ctx: {focus, message, last_delivery, beat} (view_ctx builds it)
# build_packet(role, view=WorldState, ...) calls view_for; strings and dicts pass through unchanged

# engine/dm/codex.py
promise_question(text) -> bool
promise_subject(text) -> str | None
promises(state, about, rules=None) -> CodexView
```

Part B hookups (not done here; spec 006 / 007 files):
- `engine/dm/roles/world.py::world_view`: `render_view(scene_view(state))` -> `view_for(Role.WORLD, state, ctx)`.
- `engine/dm/roles/checker.py::checker_ids`: add `spotlight(...)` ids.
- `engine/dm/mentions.py::_one` (reuse branch): `write_detail(...)` per implied property; contradictions to the
  claim check.
- RECORD (T12, `engine/dm/narration.py`): `used_event(...)` for details the delivered sentences state.
