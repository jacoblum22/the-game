# sim02.py -- runs chapter 06's conflict simulation (rules/_process/simulation/06-conflict-sim.py) with
# the stat lines of characters produced by chapter 02's creation rules, at power band 1, spending no Focus.
import importlib.util, sys
sys.argv = [sys.argv[0], "20000"]
spec = importlib.util.spec_from_file_location("sim06", r"C:\Users\jacob\the-game\rules\_process\simulation\06-conflict-sim.py")
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
