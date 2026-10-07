"""C6d-appendix.py -- DL-16-25, DL-16-26 and the BRIEF §6 trace rows for ch.15-16 (Revision C6d, ledger I-065).
Run: python rules/_process/basis/C6d-appendix.py  (idempotent), then integration-assemble-appendix.py.
DL-INT-13 is left as it is (its evidence is extended by whoever closes I-065)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.normpath(os.path.join(HERE, "..", "..", "appendix"))
FR = os.path.join(APP, "fragments")

DL_16_25 = """### DL-16-25: A beast joins by purchase, rite or taming at a fixed standing; four temperaments; a familiar is a band-1 beast at Friendly (revision I-065)
- Decision: [revision: I-065] 16.3.7: a beast follows by one of three roads, each with a fixed starting standing: **bought trained** (an 08 purchase) at Neutral; **bonded** by `rit.beast_bond` at Friendly, the rite's scope; **tamed** at Wary, after a 15.12 project on a 6-segment clock ticked by one Handle beat a day, open only to a non-monstrous `creature.beast` at or below the PC's power band. 16.15.2: every beast has one of four temperaments from its template (d4 for a tamed wild beast): `steady`, `skittish`, `fierce`, `gentle`, each a fixed edit of 16.7.4's losing heart or of 16.7.3's orders. 16.15.5: a familiar bound by `rit.bind_familiar` is a band-1 tiny beast ally (Vitality 3, one place) that starts Friendly and is moved by 16.15.3's beast list.
- Alternatives considered: beasts joining by a Talk request like people (rejected: an `animal` mind cannot be asked, 15.2.7 and DL-09-18); one starting standing for every road (rejected: a beast raised by the rite and one caught in the wild would trust the PC alike); temperament as narration only (rejected: the narrator would decide, at the moment of the fight, whether the hound runs); a familiar as a bound being with no loyalty (rejected: 05's rite makes a living creature that understands the PC, not a working's servant).
- Evidence: the three standings are read from their sources: a bought animal has no history with the PC (Neutral, the scale's zero, 00.3.16), `rit.beast_bond`'s scope says Friendly, and a wild beast brought to hand only tolerates its keeper (Wary). PR-16-1 step 6 writes the same three values. The taming clock's 6 segments match DL-16-08's six-segment loyalty clocks; the taming test reuses DL-16-01's band rule. The 6 and the d4 temperament roll are defaults, not measured values: no simulation or playtest set them. The cards carried no basis of their own until revision C6d's audit (I-065).
- Serves: goal 2 (the beast's trust and its nerve are state, not mood); goal 1 (a hound, a hawk or a tamed wolf are all reachable, each at a visible price).
- Revisit if: tamings in play routinely take more than two weeks, or never fail (then size the clock by the beast's band), or players report temperament as the only thing that decides whether a beast is useful. Open: ledger I-098 (whether 16.6.2's departure clock starts for a tamed beast that joins at Wary); until it is settled, the Wary start is recorded as written."""

DL_16_26 = """### DL-16-26: An ally whose joining want is fulfilled stays at Friendly or warmer and leaves content at Warm or below (revision I-065)
- Decision: [revision: I-065] 16.6.5: when the want an ally joined for is fulfilled (its thread completed, or the want's fact written true), its standing decides: Warm or below, it leaves content at the next haven (departure cause `want_fulfilled`, a `helped` memory, a chronicle line; often a contact afterwards); Friendly or Devoted, it stays, its joining becomes `{kind: bond}`, and a new want is rolled on 12's tables.
- Alternatives considered: every such ally leaves (rejected: a companion the PC has befriended would walk away at the moment of its happiest ending); every such ally stays (rejected: the want was the reason it came, and a Warm acquaintance has no reason left); a judged "would they stay?" flag (rejected: a judgment where the standing already answers, DL-16-07's lookup principle).
- Evidence: the line sits where DL-16-08 puts the regard clocks' ceiling and where 16.12.2 opens the personal thread (Friendly is the rung at which an ally confides); a content leaver is a successor candidate (DL-16-20, 16.16.1), so leaving is not a loss to the story. The Warm/Friendly line is a default read from those rules, not a measured value. The card carried no basis of its own until revision C6d's audit (I-065).
- Serves: goal 2 (one lookup decides it); goal 1 (fulfilling a friend's want never costs the friend).
- Revisit if: players report allies leaving right after their thread as a punishment (then make leaving a choice offered at Warm)."""

ROW = {
    "15": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 15 (104); 57 tagged at revision C6d; validator BASIS (DL-INT-13) | satisfied |",
    "16": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 16 (101); 73 tagged at revision C6d, 16.3.7, 16.15.2 and 16.15.5 by the new DL-16-25, 16.6.5 by the new DL-16-26; validator BASIS (DL-INT-13) | satisfied |",
}


def rw(p, f):
    s = open(p, encoding="utf-8").read()
    t = f(s)
    if t != s:
        open(p, "w", encoding="utf-8", newline="\n").write(t)


def add_16(s):
    for head, body in (("### DL-16-25:", DL_16_25), ("### DL-16-26:", DL_16_26)):
        if head not in s:
            s = s.rstrip("\n") + "\n\n" + body + "\n"
    return s


def main():
    rw(os.path.join(FR, "DL-16.md"), add_16)
    for c, row in ROW.items():
        p = os.path.join(FR, "trace-%s.md" % c)
        lines = open(p, encoding="utf-8").read().rstrip("\n").split("\n")
        if any(l.startswith("| BRIEF §6 |") for l in lines):
            continue
        last = max(i for i, l in enumerate(lines) if l.startswith("|"))
        lines.insert(last + 1, row)
        open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("DL-16-25, DL-16-26 and two BRIEF §6 trace rows in place")


if __name__ == "__main__":
    main()
