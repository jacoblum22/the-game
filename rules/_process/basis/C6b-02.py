"""C6b-02.py -- card-level basis tags for ch.02 (Revision C6b, ledger I-065). Run: python rules/_process/basis/C6b-02.py
Each basis is the DL-02 entry whose Decision names the card or its section, the DL-00A architecture decision it
applies (attribute ranges DL-00A-07, Focus DL-00A-09, one-copy rule DL-00A-16, gate->fill DL-00A-18), or the
constitution clause trace-02 maps it to. Every card had a recorded basis; no DL entry was needed."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply

BASIS = {
    "02.1.1": "DL-02-01; DL-00A-22; C:P3",
    "02.1.2": "DL-02-01",
    "02.1.4": "DL-00A-02; C:I; C:P13",
    "02.3.3": "DL-02-03; DL-02-04",
    "02.3.6": "DL-00A-07; DL-02-11; DL-02-26",
    "02.4.2": "DL-02-22; DL-02-04",
    "02.4.3": "DL-02-04",                          # humans take one extra access training
    "02.4.5": "DL-02-06; DL-02-23",
    "02.4.8": "DL-02-22; DL-13-07",                # PR-02-9's origin audit, applied to a setting's additions
    "02.5.3": "DL-02-07; DL-02-06; C:VII",
    "02.5.6": "DL-02-12; DL-00A-07",               # Intellect's one derived value
    "02.5.7": "DL-00A-16; DL-02-05; C:P4",         # INV-13 one copy; the replacement keeps the 3-unit budget
    "02.6.2": "DL-02-08; DL-00A-18; C:P1",
    "02.6.7": "DL-02-11; DL-02-26; C:P1",
    "02.7.2": "DL-02-10; DL-00A-09; C:P9",
    "02.7.3": "DL-01-06; DL-00A-28",               # fate starts at 1; power band 1 with no tier
    "02.7.4": "DL-00A-07; C:P7",                   # derived values, shown on the sheet
    "02.8.1": "DL-02-13",
    "02.9.6": "C:P13",                             # the unearned pronoun was P13's first data point
    "02.10.2": "DL-02-17; C:P16",                  # the drive opens play pointed at what the player wants
    "02.11.2": "DL-02-14",                         # the past is expressed as prologue chronicle lines
}

if __name__ == "__main__":
    apply("02", BASIS)
