"""C6c-09.py -- card-level basis tags for ch.09 (Revision C6c, ledger I-065). Run: python rules/_process/basis/C6c-09.py
Each basis is the DL-09 entry whose Decision names the card or its section (archetypes DL-09-01, minds DL-09-18,
band competence DL-09-07, standard line DL-09-04, Vitality solve and premium DL-09-05, variants DL-09-08, the
estimator DL-09-09, lore DL-09-10, behavior lists DL-09-11, morale DL-09-12, the budget DL-09-13, defeat
dispositions DL-09-16, powers and Focus DL-09-17, severity compensation DL-09-20, heavy blows DL-09-21, I-005
DL-09-22, trophies DL-09-23, band tells DL-09-24), the ch.06/07 decision the card applies to adversaries (mobs
DL-06-20, attention order DL-06-16, morale clock DL-06-18, size DL-06-30, reduction cap DL-07-14, Two-Key DL-07-01,
lethal warning DL-07-02, defeat table DL-07-19), the DL-00/DL-00A decision it fixes, or the constitution clause
trace-09 maps it to. Every card had a recorded basis; no DL entry was needed."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply

BASIS = {
    "09.2.2": "DL-09-01; C:P12",                   # one record read by four consumers; cannot / weak spot / cost apart
    "09.2.3": "DL-09-01; C:VI; R3 §09.6",          # 63 archetypes over nine families; new creatures reuse them
    "09.2.7": "DL-09-18",
    "09.3.2": "DL-09-07",
    "09.3.3": "DL-09-04",
    "09.3.4": "DL-09-07; DL-09-04; DL-06-08",      # Guard formula reproduces 06's reference Guard
    "09.3.5": "DL-00A-29; DL-09-21; DL-06-17",     # fixed severity offsets; windup on heavy, S4+ and shaped
    "09.3.6": "DL-09-04; DL-07-14; DL-06-10",      # reduction per T-06-12, cap 4; natural armor has no gap
    "09.3.7": "DL-06-30; DL-06-07",
    "09.3.8": "DL-09-17; DL-09-07; DL-00A-09",     # Focus a special budget, not attribute-derived; DC 10 + attr + c_b
    "09.3.9": "DL-09-04; DL-09-08; DL-06-01",      # Fend from T3; variants shift reactions
    "09.4.1": "DL-09-06; C:I",
    "09.4.3": "DL-09-05",
    "09.4.5": "DL-09-20",
    "09.4.7": "DL-06-20",
    "09.5.1": "DL-09-17; DL-09-21",
    "09.5.2": "DL-09-17",
    "09.5.3": "DL-09-17; DL-09-11; C:P9",          # can_pay false falls through; never buys an action
    "09.5.4": "DL-05-08; C:P13",                   # witnessed fact read by emulate, the Taking and lore
    "09.5.6": "DL-07-01; DL-06-01; DL-00A-17",     # no kill outright, no added action, no depth-2 hook
    "09.5.7": "DL-09-17; DL-09-21; DL-00A-12",     # refresh on a boundary's recover phase
    "09.6.1": "DL-09-09",
    "09.6.2": "DL-09-09; C:II",
    "09.6.3": "DL-09-09; DL-16-13",                # companion one gentler, the hard exception, surprise
    "09.6.5": "DL-09-09; DL-07-02",                # hard and lethal raise 07's notices
    "09.6.7": "DL-09-09; DL-09-13",
    "09.6.8": "DL-09-09",
    "09.6.9": "DL-09-09",
    "09.7.2": "DL-09-11; DL-06-16",
    "09.7.3": "DL-06-16",
    "09.7.5": "DL-09-12; DL-06-18",
    "09.7.6": "DL-09-11; C:VII; C:P16",
    "09.8.1": "DL-09-13",
    "09.8.2": "DL-09-13",
    "09.8.3": "DL-09-13; DL-06-20",                # group shape; four or more fold into a mob
    "09.8.4": "DL-00A-20; DL-06-18",               # reinforcements only on a clock with omens
    "09.8.7": "DL-09-18; DL-09-19; DL-12-10",       # reaction roll or beast mood, never the DM's choice
    "09.8.8": "DL-09-16",
    "09.8.9": "DL-09-22; DL-00-05",
    "09.9.1": "DL-09-01; DL-07-02",
    "09.9.4": "DL-07-19; DL-07-06; DL-07-15",      # captive fate, Death's Bargain, dread
    "09.9.5": "DL-09-09; DL-07-04",                # menu rates by word against 07's ladder
    "09.10.1": "DL-09-24; DL-06-17; C:IV",
    "09.10.3": "DL-09-10; C:P17",
    "09.10.4": "DL-09-10; C:P13",
    "09.11.1": "DL-09-01; DL-09-23",
    "09.11.2": "DL-09-01; DL-00-05; DL-09-22",
    "09.11.3": "DL-09-01; DL-09-23; DL-04-26",
    "09.12.1": "DL-09-01; DL-09-05; C:VI",
    "09.12.2": "DL-00A-22; DL-09-01",              # template sealed; instance carries its own state
}

if __name__ == "__main__":
    apply("09", BASIS)
