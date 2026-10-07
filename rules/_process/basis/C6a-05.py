"""C6a-05.py -- card-level basis tags for ch.05 (Revision C6a, ledger I-065). Run: python rules/_process/basis/C6a-05.py
Each basis is the DL entry whose Decision names the card or its section, the constitution clause trace-05 maps it to,
or the research the chapter cites for it. One card had no recorded basis (05.6.11's consumable cap): DL-05-41 is
written for it here. 05.8.6's stale "until ch.04 agrees" sentence is corrected (04.8.4 adopted the request)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply, RULES

BASIS = {
    "05.1.1": "C:VII; C:P5; DL-05-02",            # an ability is a license with mechanics; one shared pool
    "05.1.2": "DL-05-01; DL-05-03; DL-05-22",     # partitions, shelf, provisional status
    "05.1.3": "DL-05-04; DL-05-07; DL-05-08",     # forms, stretch, emulation
    "05.2.3": "DL-05-01; DL-05-31",               # closed slot ceiling; the branch working takes no slot
    "05.2.7": "DL-05-03",                         # re-slotting at a completed long rest
    "05.2.8": "DL-05-01; DL-00A-25",              # four equipped slots inside the hard ceiling
    "05.3.4": "DL-05-04; C:P5",                   # each form fixes its timing; trace-05 P5 (passive/active)
    "05.3.5": "DL-05-04; C:P8",
    "05.3.7": "C:P13",
    "05.3.8": "DL-05-02; DL-05-06",               # first tag gates the pool and the training license
    "05.3.10": "DL-05-28; DL-05-36",
    "05.4.1": "C:I; C:P16",
    "05.4.5": "DL-00A-12; R5 §3.3",               # SG-28: durations in the time ladder's units
    "05.4.7": "DL-05-26",                         # sustained workings end when Spent
    "05.4.8": "DL-03-12",                         # counted evidence from engine counters (cnt.focus)
    "05.5.3": "DL-05-07; C:III; C:P9",
    "05.5.5": "C:VII; C:P16",
    "05.6.4": "C:P9; DL-03-12",                   # 05.6's one pool; on_focus_spent feeds cnt.focus
    "05.6.11": "DL-05-41",
    "05.6.14": "C:P9; DL-05-12; DL-05-26",
    "05.7.2": "DL-05-18",
    "05.7.9": "C:VII",
    "05.7.10": "DL-12-21; DL-12-24",              # the seed writes canon; the seed check lists what a setting supplies
    "05.8.2": "DL-05-24",
    "05.8.6": "DL-04-18; DL-05-27",
    "05.8.7": "DL-05-24; DL-05-22",
    "05.9.1": "DL-05-06",
    "05.9.2": "DL-05-06",
    "05.9.3": "DL-05-06; DL-05-37",
    "05.10.2": "DL-00A-16; DL-00A-10",            # INV-13 one-copy rule; one fact, one lever
    "05.10.5": "DL-00A-17",                       # one-link recursion terminator (INV-12)
    "05.11.2": "DL-05-16",
    "05.11.3": "DL-05-16; DL-05-11",
    "05.11.4": "DL-05-16; DL-05-13; DL-05-24",
}

def text_fixes():
    p = os.path.join(RULES, "05-abilities-focus-magic.md")
    s = open(p, encoding="utf-8").read()
    old = ("the acquired slot, and gives it the calling's rank from then on. (This asks ch.04 to treat\n"
           "acquired-held abilities as eligible and to rank them first; see Interface requests. Until then the\n"
           "player may forget the ability at a long rest and pick it in the ordinary way.)")
    new = ("the acquired slot, and gives it the calling's rank from then on. Ch.04 treats acquired-held and\n"
           "shelved abilities as eligible for a pick and ranks them first (04.8.4) [revision: I-065].")
    if old in s:
        assert s.count(old) == 1
        s = s.replace(old, new)
    else:
        assert s.count(new) == 1
    open(p, "w", encoding="utf-8").write(s)

    f = os.path.join(RULES, "appendix", "fragments", "DL-05.md")
    d = open(f, encoding="utf-8").read()
    if "### DL-05-41:" not in d:
        d = d.rstrip("\n") + "\n\n" + DL_05_41 + "\n"
        open(f, "w", encoding="utf-8").write(d)

DL_05_41 = """### DL-05-41: Consumables restore at most 4 Focus between long rests (revision I-065)
- Decision: 05.6.11 as written: items and effects restore Focus only through `eff.restore {quantity: focus}`; consumables restore at most **4 Focus** between long rests (`restored_by_consumables_since_long_rest`), and past the cap a draught restores nothing, with the codex saying so before it is drunk. A being that restores another's Focus does it by a Reserve-form ability counted against the recipient's generation cap (DL-05-10). Recorded at revision C6a: the card shipped with no entry of its own.
- Alternatives considered: no cap (rejected: coin buys Focus, so wealth becomes a second recovery channel beside DL-05-14's rests and the push and flare economy stops being a decision; the same reasoning as DL-05-23's healing cap); a count cap like healing's two effects (rejected: draughts differ in size, so a count cap would reward the largest draught and make small ones worthless); a cap that scales with the Focus maximum (rejected: a second number to track, and it favours the characters who already have the most Focus).
- Evidence: [C:P9] (Focus is the one pool, 05.6); DL-05-09 (the cap equals the reference base Focus of 4: at most one starting pool's worth from consumables between long rests, a third of the capped maximum of 12); DL-05-14 (rest recovery); DL-05-23 (the parallel Vitality cap, [R5 HR-09]); `base_items.yaml` (`item.consumable.potion.elixir` clarity draught restores 1 per draught, so the cap is four draughts).
- Serves: goal 2 (one bound, checked by the tool before the item is used).
- Revisit if: T-05-DAY logs show consumables are the main recovery between rests, or are never used."""

if __name__ == "__main__":
    text_fixes()
    apply("05", BASIS)
