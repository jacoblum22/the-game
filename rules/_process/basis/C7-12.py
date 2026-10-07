"""C7-12.py -- card-level basis tags for ch.12 (Revision C7, ledger I-065). Run: python rules/_process/basis/C7-12.py
Each basis is the DL-12 entry whose Decision names the card or its section (turn loop DL-12-01, packet DL-12-02,
claim verdicts DL-12-03, error correction DL-12-04, write-on-mention DL-12-05, tension and the Oracle DL-12-07, pacing
DL-12-09, reaction roll DL-12-10, lead injection DL-12-11, spotlight DL-12-12, NPC depths DL-12-13, session moves
DL-12-14, twists DL-12-15, anchor index DL-12-16/26, narration limits DL-12-17, OOF blocks DL-12-18, Principle III
candidates DL-12-19, pause points DL-12-20, the world seed DL-12-21..24 and DL-12-29..35, claim class `action`
DL-12-25), the other chapter's decision the card applies (the World Turn DL-11-01/02, rumors DL-11-11, factions
DL-11-03/05, calendar DL-11-21, keepers DL-05-35), the constitution clause trace-12 maps it to (C:I, C:III, C:P7,
C:P13, C:P16, C:P17), or the R5 row trace-12 maps its section to (DM-01, DM-02, DM-05, DM-06, DM-07, DM-08, DM-09,
TM-03, TM-10, RS-14, EX-14, LW-01, LW-06, LW-07, SO-06). No card lacked a recorded basis."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply

S = "DL-12-21; DL-12-22; DL-12-23; DL-12-24"
BASIS = {
    "12.1.3": "DL-12-01; C:I; R5 DM-01",                    # closed list of breaches
    "12.2.1": "DL-12-01; R5 DM-02",
    "12.2.5": "DL-12-02; DL-12-01; C:P13",                  # verbatim message and response
    "12.3.1": "DL-12-25; DL-12-03; C:P13; R5 DM-08",
    "12.3.5": "DL-12-04; C:P8",
    "12.3.6": "DL-12-04; C:P13; R5 DM-08",
    "12.4.5": "DL-12-01; R5 TM-03",
    "12.5.5": "DL-12-14; R5 TM-10",
    "12.6.1": "DL-12-07; C:I; R5 RS-14",                    # BRIEF A2 #10: the engine owns the DM's choices
    "12.6.2": "DL-12-07; DL-12-01",
    "12.7.1": "DL-12-09; R5 TM-09",
    "12.7.2": "DL-12-09; R5 TM-09",
    "12.7.7": "DL-12-30; DL-12-09",
    "12.8.3": "DL-12-11; C:P16",
    "12.9.1": "DL-12-12; C:II; C:IV",
    "12.9.3": "DL-12-12; DL-12-14",                         # check-in halves or doubles thresholds
    "12.10.2": "DL-12-03; C:P17; C:P13",
    "12.10.5": "DL-12-01; C:P13; C:P17",
    "12.11.6": "DL-12-10; DL-12-25",
    "12.11.8": "DL-11-01; DL-11-02; R5 DM-07",
    "12.12.1": "DL-12-19; C:III; R5 DM-05",
    "12.12.2": "DL-12-19; C:III; R5 DM-05",
    "12.12.3": "DL-12-19; R5 DM-05",
    "12.13.2": "DL-12-16; R5 DM-04",                        # scores 3 / 2 / 1
    "12.13.4": "DL-12-16; C:V; C:III; R5 DM-04",
    "12.13.5": "DL-12-19; R5 DM-05",
    "12.13.6": "DL-12-16; DL-12-26",
    "12.14.1": "DL-12-17; C:IV; R5 DM-06",
    "12.14.2": "DL-12-05; DL-12-03; R5 DM-06",
    "12.14.4": "DL-12-01; C:P7; R5 DM-06",                  # T10 screen: no mechanics in fiction
    "12.14.6": "DL-12-17; R5 EX-14",
    "12.14.7": "DL-12-17; DL-11-10; R5 DM-06",
    "12.14.9": "DL-12-20; C:P16",
    "12.14.12": "DL-12-17; DL-12-01; R5 DM-06",
    "12.14.13": "DL-12-05; C:VII",
    "12.15.1": "DL-12-18; C:P7; R5 DM-09",
    "12.15.2": "DL-12-18; R5 OB-05",
    "12.15.3": "DL-12-18; C:P7",
    "12.15.4": "DL-12-18; DL-12-20",
    "12.15.5": "DL-12-18; C:VII",
    "12.15.6": "DL-12-18; DL-12-20",
    "12.15.7": "DL-12-18; DL-12-20",
    "12.15.8": "DL-12-18; DL-12-19; R5 DM-05",
    "12.15.9": "DL-12-18; DL-12-04",
    "12.15.10": "DL-12-18; DL-12-11; C:P16",
    "12.15.11": "DL-12-18; DL-12-14",
    "12.15.12": "DL-12-18; DL-12-14",
    "12.15.13": "DL-12-18; DL-12-14",
    "12.15.14": "DL-12-18; C:P7; R5 DM-09",
    "12.15.15": "DL-12-18; DL-12-25",
    "12.16.1": S,
    "12.16.3": "DL-12-21; DL-12-22",
    "12.16.4": "DL-12-33; DL-12-22; DL-12-21",
    "12.16.5": "DL-12-22; DL-12-24; DL-12-21",
    "12.16.6": "DL-12-22; DL-05-35; DL-12-21",
    "12.16.7": "DL-12-22; DL-12-21",
    "12.16.8": "DL-12-35; DL-12-32; DL-12-21; R5 LW-06",
    "12.16.9": "DL-12-22; DL-12-21",
    "12.16.10": "DL-12-34; DL-11-05; DL-12-21; R5 LW-01",
    "12.16.11": "DL-12-29; DL-12-32; DL-12-13; DL-12-21",
    "12.16.12": "DL-12-23; DL-12-21; R5 LW-07",
    "12.16.13": "DL-12-35; DL-12-21",
    "12.16.14": "DL-11-11; DL-12-21; R5 SO-06",
    "12.16.15": "DL-12-33; DL-11-21; DL-12-21",
    "12.16.16": "DL-12-22; DL-12-21",
    "12.16.17": "DL-12-24; DL-12-36",
    "12.16.18": "DL-12-23; DL-12-31; DL-12-35",
}

if __name__ == "__main__":
    apply("12", BASIS)
