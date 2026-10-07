"""C6a-04.py -- card-level basis tags for ch.04 (Revision C6a, ledger I-065). Run: python rules/_process/basis/C6a-04.py
Each basis is the DL entry whose Decision names the card or its section, the constitution clause the chapter's
traceability matrix maps it to, or the research digest entry it rests on (checked by reading each card and entry)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply

BASIS = {
    "04.1.2": "DL-04-01; DL-04-29",                  # state of a derived label; confirmed_tier (I-037)
    "04.1.3": "DL-04-01; DL-04-17; DL-04-23",        # calling, seat, the five named tiers
    "04.1.4": "C:P3; C:P13; DL-04-13",               # trace-04 P3/P13; Leanings view
    "04.2.2": "DL-04-11; DL-04-12; DL-04-22; DL-04-23",  # family defaults: Focus trigger, vehicles, shadow, attributes
    "04.2.7": "DL-04-02; DL-04-06",                  # full coverage at level 2; Monk/Devourer variants
    "04.4.2": "DL-04-10",
    "04.4.4": "DL-04-10; DL-04-15",                  # K5 margin; provisional, renounceable, lapses
    "04.4.5": "R6 A-07, A-21, V7",                   # scheduled reflection boundary + crisis awakening
    "04.4.6": "C:I; DL-04-10",                       # engine tool emitting policy packets
    "04.5.2": "DL-04-23",
    "04.5.3": "DL-04-23; C:VII",
    "04.5.7": "DL-04-23",
    "04.7.2": "DL-04-14; DL-12-18; C:VII",           # offer protocol; OOF block order
    "04.7.3": "DL-04-14",
    "04.7.7": "DL-04-14",
    "04.7.8": "R6 R-A5; 00.17.1 Q4",                 # 04 emits, 11 consumes; never writes faction state
    "04.8.3": "DL-04-06; C:P5",                      # base and variant are one lineage
    "04.9.3": "DL-04-22; DL-05-36",
    "04.9.5": "DL-04-22",
    "04.10.1": "DL-04-19; C:VII",
    "04.11.2": "DL-11-18; R6 R-A5",                  # ranks contested by V9 trials; rank never capability
}
if __name__ == "__main__":
    apply("04", BASIS)
