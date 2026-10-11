# Trace: "Calella" / "Ysnae" name mix-up (save playtest-20261011-011012-fighter-dm-tools)
Note: transcript input 26 = save turn.11 (the /fix). Cause class: CODE (display leak) + ambiguous model wording. NOT spec 033 walk-on naming.
## Answers
1. PC = Calella Stoneby (pc.calella_stoneby; sheet and cast packet both say so; Eda's "Calella" is correct). Stranger entity =
   npc.ysnae_of_the_grey_havens, name "Ysnae of the Grey Havens", role "thing from the wound that is at the gate", name_known:false.
2. Yes, and the playtester read it as a self-introduction. turn.4 (call.turn.4.dm.1.0, `said` row): "You came out to me with a naked blade.
   Calella Stoneby. I have been asking after you since the wound opened." She is addressing the PC by full name. The earlier draft
   (call.turn.4.dm.0.0) had: "Calella Stoneby. Someone has been asking for you by name." The model was following the seeded thread
   thr.sit_iron_wolds_local "a stranger asks after the PC by name". The bare "Calella Stoneby." fragment reads as a name-announce.
3. DM packet (turn.4, both calls) was correct and clear: "The player's character (pc.calella_stoneby): Calella Stoneby (she/her...)" and
   "- npc.ysnae_of_the_grey_havens: the thing from the wound that is at the gate (she/her; elf): ... mood toward you: not set".
   The DM was never shown "Ysnae" except inside the id (display_name gives the role label because name_known is false). No misidentification
   in the packet; the model made no error of who-is-who, only a terse, ambiguous line.
4. Not new_npc, not _walk_on, not the DM's `name` field. Event 415, turn.1, source npc_generation: the Director (call.turn.1.director.0.0)
   returned cast_described ["...the thing from the wound that is at the gate"]; code created the walk-on via the pre-spec path
   (engine/dm/mentions.py:276 -> gen_npc.walk_on; engine/world/social.py:245 sets name_known False) and ROLLED the name from world.names
   (elf "X of the Grey Havens"). The DM's later tool calls named her only by id (target npc.ysnae_..., as "she"); dm_tools._walk_on
   (dm_tools.py:645) never ran for her. Spec 033 R6 (DM-supplied name/pronouns) is not involved.
5. /fix (call.turn.11.fixer.0-3, 4 calls): verdict misread / record_stands, outcome "explain", writes none, reverted none. Its facts were true
   (the stranger addressed the PC by name; Eda is right) but it said "She never gave a name ... the record files her as Ysnae of the Grey
   Havens" and never explained why the screen shows a name the PC has not learned, so notes [27][29][30][35] stay confused.
## Real defect found (differs from the suspected "model gave her the PC's name")
The only place "Ysnae of the Grey Havens" reached the player is the result line (turn.8): "Changed: Ysnae of the Grey Havens is dead".
engine/dm/oof.py:changed_line, lines 665-666:
  name = _ent_name(state, eid) or (state.entities[eid].name if ... name_known(state, eid) else "your opponent")
_ent_name (oof.py:720) returns e.name whenever the entity is not sealed and is player-facing; it never checks name_known, so the
name_known-guarded fallback is dead code for any shown NPC. Compare line 632 of the transcript: the unnamed "the pale thing in the mist" is
printed because its name IS its label. Every foe created by the Director/mentions walk-on path with a rolled name leaks that name when hurt.
Code is authoring player-visible truth ("her name") that the PC never learned (12.10.2); display_name()/_who() in the same file do it right.
Origin: commit ea6f698 (I-154), older than spec 033.
## Frequency
This save: 1 leak (turn.8 result), 1 ambiguous name line (turn.4), 1 confused /fix. Other leak sites of e.name in player text not audited.
Check: grep "_ent_name(" engine/dm/oof.py for other uses.
## Fix candidates (after cause)
- A. changed_line: use display_name(state, eid) (engine/store/views.py:92) instead of _ent_name; keeps "the thing from the wound ... is dead".
  Removes the leak. Add a test: hurt unnamed walk-on, no rolled name in the Changed line.
- B. Narration wording: "Calella Stoneby." as a bare sentence invites misreading; model-side, low priority. Do not add a code check.
- C. Fixer: when the player asks about a name the PC has not learned, its entity view should say name_known false, so it can answer "you
  have not learned her name; the screen should not have shown it" (it saw the rolled name with no flag).
