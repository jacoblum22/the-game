# sim02.py -- runs chapter 06's conflict simulation (rules/_process/simulation/06-conflict-sim.py) with
# the stat lines of characters produced by chapter 02's creation rules, at power band 1, spending no Focus.
import os as _os
_RULES = _os.environ.get('GAME_RULES', _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..')))
import importlib.util, sys
sys.argv = [sys.argv[0], "20000"]
spec = importlib.util.spec_from_file_location("sim06", _os.path.join(_RULES, '_process', 'simulation', '06-conflict-sim.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
LINES = [
 ("06's reference P1 line (+5, Guard 14, Vit 12, armor 1)", dict()),
 ("Wren: Free hunter (+5, Guard 14, Vit 12, armor 1, tempo +3)", dict(atk=5, guard=14, vit=12, armor=1, tempo=3)),
 ("Bram: Free soldier, shield (+5, Guard 14, Vit 14, armor 1, tempo +1)", dict(atk=5, guard=14, vit=14, armor=1, tempo=1)),
 ("Dwarf Typical soldier (+5, Guard 12, Vit 14, armor 1, tempo +3)", dict(atk=5, guard=12, vit=14, armor=1, tempo=3)),
 ("Orc-kin Typical soldier, knack on blades (+6, Guard 15, Vit 14, armor 1)", dict(atk=6, guard=15, vit=14, armor=1, tempo=1)),
 ("Thessaly: Free acolyte, mace, no Focus (+0, Guard 11, Vit 12, no armor)", dict(atk=0, guard=11, vit=12, armor=0, tempo=2)),
 ("Elf Typical apprentice, staff, no Focus (+1, Guard 13, Vit 11, no armor)", dict(atk=1, guard=13, vit=11, armor=0, tempo=3)),
 ("Weakest legal line (+0, Guard 10, Vit 11, no armor, tempo +0)", dict(atk=0, guard=10, vit=11, armor=0, tempo=0)),
]
for title, mk in (("one T1 foe (rabble)", lambda: [m.Foe(1)]), ("two T1 foes", lambda: [m.Foe(1), m.Foe(1)]), ("one T2 foe (trained)", lambda: [m.Foe(2)])):
    m.table("New characters (band 1, no Focus spent) against " + title)
    for label, over in LINES:
        m.run(label, 1, mk, pc_over=over)

# ---- Revision I-009: the same new casters using their branch working (05.7.11; rank 1 = S2, no Focus, no slot).
# Casting modifier = casting attribute + the school's +2 (02.5.5). Vitality 12 + Endurance (02.7.1); Guard 10 +
# Agility + floor 1 (no armor). "default" lines are T-02-6's default placement. Since revision I-009 a magic livelihood
# whose Typical rule would fix the casting attribute at -1 defaults to the Free rule (02.3.5); the three "keeping the
# Typical rule" lines are that choice made against the grain, which the DM states before confirming (02.10).
ARC = dict(elemental=True, push_on_crit=True)   # Force Bolt: harm.arcane.force
DIV = dict(elemental=True)                      # Rebuke: radiant or necrotic
PRI = dict(elemental=False)                     # Wild Lash: physical unless the source is fire
CASTERS = [
 ("Thessaly: Free acolyte, Rebuke (+5, Guard 11, Vit 12)", dict(atk=5, guard=11, vit=12, armor=0, tempo=2), DIV),
 ("Elf Typical apprentice, Force Bolt (+5, Guard 13, Vit 11)", dict(atk=5, guard=13, vit=11, armor=0, tempo=3), ARC),
 ("Human Free hedge-taught (default), Wild Lash (+5, Guard 11, Vit 13)", dict(atk=5, guard=11, vit=13, armor=0, tempo=3), PRI),
 ("Human Free Touched (default), Wild Lash (+5, Guard 13, Vit 12)", dict(atk=5, guard=13, vit=12, armor=0, tempo=2), PRI),
 ("Orc-kin apprentice (default since I-009: Free rule), Force Bolt (+5, Guard 11, Vit 12)", dict(atk=5, guard=11, vit=12, armor=0, tempo=3), ARC),
 ("Goblin-kin acolyte keeping the Typical rule (Presence -1), Rebuke (+1, Guard 12, Vit 14)", dict(atk=1, guard=12, vit=14, armor=0, tempo=3), DIV),
 ("Orc-kin apprentice keeping the Typical rule (Intellect -1), Force Bolt (+1, Guard 12, Vit 12)", dict(atk=1, guard=12, vit=12, armor=0, tempo=4), ARC),
 ("Beastfolk hedge-taught keeping the Typical rule (Resolve -1), Wild Lash (+1, Guard 13, Vit 14)", dict(atk=1, guard=13, vit=14, armor=0, tempo=4), PRI),
 ("Weakest legal caster (+1, Guard 10, Vit 11, tempo +0), Wild Lash", dict(atk=1, guard=10, vit=11, armor=0, tempo=0), PRI),
]
for title, mk in (("one T1 foe (rabble)", lambda: [m.Foe(1)]), ("two T1 foes", lambda: [m.Foe(1), m.Foe(1)]), ("one T2 foe (trained)", lambda: [m.Foe(2)])):
    m.table("New casters using their branch working (band 1, no Focus spent; revision I-009) against " + title)
    for label, over, bw in CASTERS:
        m.run(label, 1, mk, pc_over=over, caster=dict(sev=2, **bw))
