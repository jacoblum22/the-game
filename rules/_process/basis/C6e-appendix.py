"""C6e-appendix.py -- DL-08-39..41 and the BRIEF §6 trace row for ch.08 (Revision C6e, ledger I-065).
Run: python rules/_process/basis/C6e-appendix.py  (idempotent), then integration-assemble-appendix.py.
DL-INT-13 is left as it is (the orchestrator closes I-065 and updates it)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.normpath(os.path.join(HERE, "..", "..", "appendix"))
FR = os.path.join(APP, "fragments")

DL = [("### DL-08-39:", """### DL-08-39: Body slots are a closed table of eight kinds (revision I-065)
- Decision: [revision: I-065] 08.5.1: an equipped item occupies a body slot from one closed table: hands 2 (a two-handed item takes both), body 1 (armor), one each for clothing, cloak, feet, gloves and head, neck 1, rings 2, charms 2, and `fitted` 1 per maim a prosthesis offsets (DL-08-32). A pack item is carried, counts only toward load (08.9.1) and is not equipped, so its properties stop. Donning or doffing armor takes its `don_time` and never happens in a conflict.
- Alternatives considered: no slots, only attunement's five (rejected: five attuned rings would stack the same family five times before 08.2.2's item share clamps it, and the codex could not say what a character visibly wears); a slot per base item kind (rejected: open-ended; a new base kind would add a slot); more ring and charm slots (rejected: attunement's five is the binding limit, and two of each already lets a character fill it from jewelry alone).
- Evidence: the counts follow the genre's paper-doll convention (R5 EQ-01: equipment and properties) and fit attunement's five (DL-08-14): the slots that hold attunable property items (hands, body, garments, neck, rings, charms) hold more than five, so the slots never bind before attunement does. The individual counts (2 rings, 2 charms) are defaults, not measured values; no simulation or playtest set them. The card carried no basis of its own until revision C6e's audit (I-065).
- Serves: goal 2 (one closed table; an item is equipped or it is not); C:V (bounded counts).
- Revisit if: play shows characters routinely carrying more property jewelry than they can wear, or 16's allies need slots of their own."""),
      ("### DL-08-40:", """### DL-08-40: Consumables are made three at a time; scrolls and copies are six-segment projects (revision I-065)
- Decision: [revision: I-065] 08.6.11: a consumable project is 4 segments (common) or 6 (fine), a watch a tick, and yields three doses of one consumable base item for materials at half its price per dose. A scroll needs `lic.training.craft_enchanting` and the ability's text or the ability: 6 segments at Hard, a day a tick, materials of 25 + 25 × the ability's `min_tier` coins, one scroll. A copy of a teaching text needs `lic.training.craft_scribing`, the original and its language: 6 segments at Moderate, a day a tick; the copy teaches as the original does.
- Alternatives considered: one dose per project (rejected: a common draught would take a full project, so brewing could never supply a party; 08.6.4's clocks are sized for one durable item); free copying by anyone literate (rejected: a teaching text would multiply without a crafter, and 05.8.5's learning gate would be paid once for a whole party and its allies).
- Evidence: the segment counts are 08.6.4's progress ladder at the target rung (DL-08-16: common 4, fine 6). Materials for three doses cost one and a half doses' list price, and 08.8.9's labor cap bounds what the batch sells for. The 25 + 25 × `min_tier` scroll cost is the `price_rule` in base_items.yaml. The batch size of three and the scroll cost are defaults, not measured values; no simulation set them. The card carried no basis of its own until revision C6e's audit (I-065).
- Serves: goal 2 (each kind of making uses the one clock and DC ladder); 08.8.9 (making earns a living, not a fortune).
- Revisit if: `08-campaign-sim.py` or play shows brewed consumables outselling every other craft income at a band."""),
      ("### DL-08-41:", """### DL-08-41: A vessel takes harm on a hull clock of 4, 6 or 8 by its price (revision I-065)
- Decision: [revision: I-065] 08.10.4: a vessel has a hull clock of 4 segments under 100 coins, 6 under 1,000 and 8 above. `cost.gear` against a vessel ticks the clock by U(severity) instead of writing damaged or broken, and a full clock is foundering (10). Most travelers buy passage (08.8.8), not ships.
- Alternatives considered: 08.1.9's damaged / broken states for a vessel (rejected: one hard wave would break a ship outright, and a ship is a place with a crew, not a sword); a hull in Vitality (rejected: a vessel is not a combatant, and 00.4's clocks already carry graded damage to things).
- Evidence: the clock sizes follow 00's clock sizes (DL-00A-20: 4, 6, 8) and the price bands of 08.8.2, so a dearer, larger vessel takes more harm before it founders. The thresholds (100 and 1,000 coins) are defaults, not measured values; no simulation set them. The card carried no basis of its own until revision C6e's audit (I-065).
- Serves: goal 2 (one clock, read by 10's water travel); C:P3 (the hull is state, not narration).
- Revisit if: 10's water hazards in play sink vessels much faster or slower than their crews can answer."""),
      ]

ROW = "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 08 (82); 46 tagged at revision C6e, 08.5.1, 08.6.11 and 08.10.4 by the new DL-08-39..41; validator BASIS (DL-INT-13) | satisfied |"


def main():
    p = os.path.join(FR, "DL-08.md")
    s = open(p, encoding="utf-8").read()
    for head, body in DL:
        if head not in s:
            s = s.rstrip("\n") + "\n\n" + body + "\n"
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    p = os.path.join(FR, "trace-08.md")
    lines = open(p, encoding="utf-8").read().rstrip("\n").split("\n")
    if not any(l.startswith("| BRIEF §6 |") for l in lines):
        last = max(i for i, l in enumerate(lines) if l.startswith("|"))
        lines.insert(last + 1, ROW)
        open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("DL-08-39..41 and the BRIEF §6 trace row for 08 in place")


if __name__ == "__main__":
    main()
