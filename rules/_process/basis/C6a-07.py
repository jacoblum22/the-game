"""C6a-07.py -- card-level basis tags for ch.07 (Revision C6a, ledger I-065). Run: python rules/_process/basis/C6a-07.py
Each basis is the DL entry whose Decision names the card or its section, the constitution clause trace-07 maps it to,
or R5's completeness row for the situation it rules (HR-01 Vitality loss, HR-02 lasting injury / scars, HR-03 dying,
HR-05 rest, HR-06 mental harm, HR-07 deprivation, HR-08 afflictions, HR-09 healing magic's limits, CF-10 capture).
Every card had a recorded basis; no DL entry was needed."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply

BASIS = {
    "07.1.1": "C:P13; DL-00A-09",
    "07.1.2": "DL-07-18; DL-00-04",
    "07.1.3": "DL-07-03; DL-07-04; C:V; C:P10",
    "07.1.4": "DL-00A-22; R5 HR-01",             # a shown descriptor (visibility classes)
    "07.2.1": "C:I; DL-07-03; DL-07-14",
    "07.2.7": "DL-07-04; DL-07-23; R5 HR-03",
    "07.2.9": "DL-07-03; DL-06-23; DL-07-21",    # load 3 non-lethal, nonlethal mode, deprivation collapse
    "07.2.10": "R1 §09; DL-06-23",               # the opposition's side stays cheap to run
    "07.2.11": "DL-06-23; DL-07-01",
    "07.3.2": "DL-07-01",
    "07.3.6": "DL-07-01",
    "07.3.8": "DL-07-02",
    "07.3.9": "DL-07-01; C:III",
    "07.4.4": "DL-07-09; DL-07-19",
    "07.5.1": "DL-07-05; C:P10",
    "07.5.3": "DL-07-05; DL-07-19",
    "07.5.4": "DL-07-05; DL-07-10",
    "07.5.6": "DL-07-05; DL-07-19",
    "07.5.7": "DL-07-05; DL-07-09",
    "07.5.9": "DL-07-05; DL-07-01",
    "07.5.10": "DL-07-05; C:P8",
    "07.5.11": "DL-07-05; C:VI",
    "07.5.12": "DL-07-05; R5 HR-02",
    "07.5.13": "DL-07-01; C:III",
    "07.6.5": "R5 CF-10; DL-06-23",
    "07.7.1": "R5 HR-02; DL-07-10",
    "07.7.2": "R5 HR-02; DL-07-10",
    "07.7.4": "DL-07-10; DL-00A-07; C:P4",       # maims drawn by table; at most -1 per attribute
    "07.7.6": "DL-08-32; C:P12",
    "07.8.1": "DL-07-11; DL-07-23; R5 HR-05",
    "07.8.3": "DL-07-11",
    "07.8.4": "DL-07-11",
    "07.8.5": "DL-07-12; C:I",
    "07.8.6": "DL-07-13",
    "07.8.7": "DL-07-13",
    "07.8.9": "DL-05-23; R5 HR-09",
    "07.8.10": "DL-07-21; R5 HR-07",
    "07.8.11": "DL-07-13; R5 HR-05",
    "07.9.2": "DL-07-17; R5 HR-08",
    "07.9.3": "DL-07-17; C:P8",
    "07.9.4": "DL-07-17",
    "07.9.5": "DL-07-17",
    "07.9.6": "DL-07-17",
    "07.9.7": "DL-07-17",
    "07.9.8": "DL-07-17",
    "07.9.9": "DL-07-17; C:VII",
    "07.10.1": "DL-07-14",
    "07.10.3": "DL-07-14",
    "07.10.4": "DL-07-14",
    "07.11.2": "DL-07-15; R5 HR-06",
    "07.11.3": "DL-07-15",
    "07.11.5": "DL-07-15",
    "07.11.7": "DL-07-15",
    "07.12.2": "DL-07-20",
    "07.12.3": "DL-07-20",
    "07.12.4": "DL-07-20",
}
if __name__ == "__main__":
    apply("07", BASIS)
