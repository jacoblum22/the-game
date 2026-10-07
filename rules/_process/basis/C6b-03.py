"""C6b-03.py -- card-level basis tags for ch.03 (Revision C6b, ledger I-065). Run: python rules/_process/basis/C6b-03.py
Each basis is the DL-03 entry whose Decision names the card or its section, the DL-00A decision it applies (tag
vocabulary DL-00A-13, conduct axes DL-00A-15, the evidence core shape in the state model DL-00A-22), or the
constitution clause trace-03 maps it to. Every card had a recorded basis; no DL entry was needed."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply

BASIS = {
    "03.1.1": "DL-00A-13; DL-03-15",
    "03.1.4": "DL-00A-13; DL-03-15",               # definitions and distinguish tests cut wrong-choice rates
    "03.1.8": "DL-00A-15; DL-03-13",
    "03.1.9": "DL-00A-13; DL-03-15",               # 03 owns the file; PR-03-6 reconciles proposals
    "03.1.10": "DL-03-08; DL-03-14",               # context class; grounding
    "03.2.1": "DL-00A-22; DL-03-09; C:P5",
    "03.2.2": "DL-03-01; DL-03-05; C:I",
    "03.2.3": "DL-03-12; DL-03-04",
    "03.3.2": "DL-03-01; C:P5",
    "03.4.7": "DL-03-12; DL-03-13",
    "03.5.6": "DL-03-05; DL-03-18",                # pending until scene_end; the in-scene crisis check
    "03.6.2": "DL-03-10",
    "03.7.2": "DL-03-12; C:V; C:P9",
    "03.7.3": "DL-03-27; DL-03-05; DL-03-07",
    "03.8.1": "DL-03-13; DL-00A-15",
    "03.8.2": "DL-03-13; DL-03-05",
    "03.9.2": "DL-03-10; DL-03-11; C:P5",
    "03.9.5": "C:P13; C:P3",
    "03.10.3": "DL-03-09",
    "03.10.4": "DL-03-09",
    "03.10.6": "DL-03-09",
    "03.11.2": "DL-03-11; C:P16",                  # only void and atonement remove evidence
}

if __name__ == "__main__":
    apply("03", BASIS)
