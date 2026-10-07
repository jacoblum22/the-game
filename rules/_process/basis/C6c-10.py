"""C6c-10.py -- card-level basis tags for ch.10 (Revision C6c, ledger I-065). Run: python rules/_process/basis/C6c-10.py
Each basis is the DL-10 entry whose Decision names the card or its section (place graph DL-10-01, route length
DL-10-02, pace ladder DL-10-03, way-finding DL-10-04/05, supply DL-10-06, danger rating DL-10-07, the d12 DL-10-08,
omens DL-10-09, tables DL-10-10/26/27/28, hazards DL-10-11, weather DL-10-12, sites DL-10-13..16, traps DL-10-17,
march allowance DL-10-18, roles DL-10-19, handlers DL-10-20, pacing opt-in DL-10-22, light DL-10-23, ventures
DL-10-24, lost DL-10-25, settlements DL-10-29, hearts DL-10-30), the DL-00A or other chapter's decision the card
applies, the constitution clause trace-10 maps it to, or the research row trace-10 maps its section to (R5 EX-01
10.3, EX-02 10.4, EX-03 10.5, EX-04 10.11, EX-05 10.12, EX-06 10.6, EX-07 10.1, EX-08 10.13, EX-09 10.7, EX-10
search, EX-14 spatial description, AV-06 tables, AV-08 traps, HR-07 deprivation, EQ-09 supply and light, EQ-10
mounts and vehicles, X-05 real-time light excluded; R6 B-15 distance as difficulty). One card had no recorded
basis (10.1.6's settlement scope: its derivation and its 8-watch cut): DL-10-31 is written for it."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply

BASIS = {
    "10.1.1": "DL-10-01; C:IV; R5 EX-07",
    "10.1.2": "DL-10-01; DL-00A-22; C:P3",
    "10.1.3": "DL-10-01; DL-10-02",
    "10.1.5": "DL-10-01; C:P3; R5 EX-13",          # sealed until discovered; discovery carries the frame id
    "10.1.6": "DL-10-31; DL-03-09; DL-11-15",
    "10.1.7": "DL-05-14; C:P13",                   # resonant rest; resonance and zones are facts with sources
    "10.1.8": "DL-10-01; DL-12-23; C:I",           # generated, never imagined; written before narrated
    "10.2.1": "DL-00A-12; R5 TM-01",
    "10.2.2": "DL-10-24",
    "10.2.3": "DL-10-24; DL-07-11",
    "10.2.4": "R6 B-15; C:P2; DL-10-07",
    "10.2.5": "DL-10-20; DL-00A-12; C:I",
    "10.2.6": "DL-10-29",
    "10.3.1": "DL-10-02; R5 EX-01",
    "10.3.2": "DL-10-02; DL-10-03",
    "10.3.3": "DL-10-02; R5 EX-01",
    "10.3.5": "DL-10-18; R5 HR-07",
    "10.3.6": "DL-10-02; R5 EX-01",
    "10.3.7": "DL-10-03; R5 EQ-10",                # vessel paces in points on the same ladder
    "10.3.8": "DL-10-23; DL-10-04; R5 EX-01",
    "10.4.3": "DL-10-05; DL-00A-10",
    "10.4.4": "DL-10-05; C:VII",
    "10.4.6": "DL-10-25; C:P3",
    "10.5.1": "DL-10-19; R5 EX-03",
    "10.5.2": "DL-10-19; C:IV",
    "10.5.3": "DL-10-19; DL-00A-19",
    "10.6.1": "DL-10-06; R5 EQ-09",
    "10.6.2": "DL-10-06; DL-07-21; R5 HR-07",
    "10.6.3": "DL-10-06; C:VII",
    "10.6.5": "DL-10-06; C:VII; R5 EX-06",
    "10.7.1": "DL-10-23; R5 X-05; R5 EQ-09",
    "10.7.2": "DL-10-23",
    "10.7.3": "DL-10-23; C:VII",
    "10.8.1": "DL-10-03; R5 EQ-10; C:VII",         # vehicles G4 off their routes
    "10.8.2": "DL-10-06; DL-07-21; R5 EQ-10",
    "10.8.3": "DL-00A-19; R5 EQ-10",               # riding is basic Handle; rolls only when uncertain and costly
    "10.8.4": "DL-10-03; R5 EQ-10",                # the slowest member's pace
    "10.9.4": "DL-10-08; DL-10-29; C:P16",         # every face means something; face 5 with no mount or ammunition
    "10.9.6": "DL-10-09; C:P17",
    "10.9.7": "DL-10-22",
    "10.9.8": "DL-10-08; DL-00A-12",
    "10.9.9": "DL-10-08; DL-10-09; C:P3",
    "10.10.1": "DL-10-10; DL-10-26; DL-10-27; R5 AV-06",
    "10.10.2": "DL-10-10; DL-10-26; DL-10-28; DL-09-13",
    "10.10.3": "C:IV; R5 EX-14; DL-10-19",         # distance in bands; lookout and scout one band farther
    "10.10.4": "DL-10-28; DL-06-05; DL-10-19",     # awareness from state; a lethal row never ambushes
    "10.10.5": "DL-09-18; DL-09-19; DL-12-10",
    "10.10.6": "DL-09-13; C:P13",                  # an undefeated band stays in the place
    "10.10.7": "DL-06-21; DL-10-09",
    "10.11.2": "DL-10-12; R5 EX-04",
    "10.11.3": "DL-10-12; C:I",
    "10.11.4": "DL-10-12",
    "10.11.5": "DL-10-12; C:VII",
    "10.12.1": "DL-10-11; R5 EX-05",
    "10.12.2": "DL-10-11; DL-07-14",
    "10.12.3": "DL-10-11; C:P16",
    "10.12.5": "DL-07-14; DL-10-11",
    "10.12.6": "DL-07-14; DL-10-11",
    "10.12.7": "DL-10-11; DL-07-17",
    "10.12.8": "DL-10-11; DL-07-15",
    "10.12.9": "DL-07-14; C:III",
    "10.12.10": "DL-10-11; C:P16",
    "10.13.2": "DL-10-13; C:V",
    "10.13.3": "DL-10-13; DL-10-16",
    "10.13.4": "DL-10-13; DL-10-16; R5 EX-08",
    "10.13.5": "DL-00A-12; DL-10-14; R5 EX-08",
    "10.13.7": "DL-10-14; DL-10-13; DL-10-01",
    "10.13.8": "DL-10-15; DL-10-16; DL-00A-20",
    "10.13.9": "DL-10-15; C:P16",
    "10.13.10": "DL-10-30; DL-10-13",
    "10.13.11": "DL-10-16; R5 EX-08",
    "10.13.12": "DL-10-16; C:P13",
    "10.13.14": "DL-10-13; R5 EX-08",
    "10.14.1": "DL-10-17; R5 AV-08",
    "10.14.2": "DL-10-17; C:P3",
    "10.14.4": "DL-10-17; C:P8",
    "10.14.5": "DL-10-17; C:VII; C:P16",
    "10.14.6": "DL-10-17",
    "10.14.7": "DL-10-17; DL-00A-20",
    "10.14.8": "DL-10-17; DL-00A-19",
    "10.15.1": "DL-00A-24; DL-00A-19; R5 EX-10",
    "10.15.2": "DL-00A-12",
    "10.15.3": "DL-06-03; R5 EX-10",               # repetition: same method, nothing new
}

if __name__ == "__main__":
    apply("10", BASIS)
