"""The model roles' calls (contracts/model-calls.md): each builds its schema, cards and packet, calls
`engine.llm.base.call_role` with the role's default and a semantic `check=`, and returns a typed result.

Reader (A1) `engine.dm.roles.reader.read_message`; Framer (A2) `engine.dm.roles.framer.framer_for`; World (W)
`engine.dm.roles.world.npc_responses` / `world_view`. Prompts: `engine.dm.roles.prompts.load_prompt`.
"""
