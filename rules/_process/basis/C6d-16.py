"""C6d-16.py -- card-level basis tags for ch.16 (Revision C6d, ledger I-065). Run: python rules/_process/basis/C6d-16.py
Each basis is the DL-16 entry whose Decision names the card or its section (band rule DL-16-01, retinue DL-16-02,
lines DL-16-04, hiring DL-16-05, knacks DL-16-06, acceptance and will DL-16-07, the two clocks DL-16-08, counsel
DL-16-10, departure DL-16-11, betrayal DL-16-12, journey roles and duties DL-16-15, death DL-16-16, growth DL-16-17,
legacy DL-16-20, effects and handlers DL-16-21, creation bonds DL-16-23), the other chapter's decision the card
applies (companions' 0 actions and Command DL-06-01/19, Flank DL-06-07, attention order DL-06-16, Fend DL-06-22,
Help DL-01-24, bleeding out DL-07-20, defeat DL-07-19, rest DL-07-11, witnesses DL-03-09, reputation DL-11-15,
vehicles DL-04-12, spotlight facets DL-12-12, NPC depth and memories DL-12-13, starting standing DL-12-10, request
size DL-15-09, memory valences DL-15-03, learning DL-15-28, lifestyles DL-08-20, attunement DL-08-14, minds DL-09-18,
the state model DL-00A-22, the standing scale DL-00A-27, clocks with omens DL-00A-20), the constitution clause
trace-16 maps the card to, or a research row (R5 NP-05 companions, R5 NP-06 NPC voice, R5 G-3 the companions gap
16.12.1 cites, R5 EQ-10 mounts, R6 D-R4 successors). Two cards' rules had no recorded basis and gain DL entries:
DL-16-25 (16.3.7 beasts' three roads, 16.15.2 temperament, 16.15.5 familiars) and DL-16-26 (16.6.5 a want
fulfilled)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply

BASIS = {
    "16.1.1": "C:V; C:III; R5 NP-05",                        # seven kinds, closed
    "16.1.2": "C:II; DL-00A-22; R5 NP-05",
    "16.1.3": "C:P3; DL-00A-22",
    "16.1.4": "DL-12-13; DL-00A-27; R5 NP-05",               # every NPC rule still applies
    "16.2.2": "DL-16-02",
    "16.2.5": "DL-16-02; C:P16",
    "16.3.1": "DL-16-01; C:P16; C:VII",
    "16.3.2": "DL-16-05; DL-16-01",
    "16.3.4": "DL-15-09; C:III; C:P8",                       # sized by what following costs THEM
    "16.3.5": "DL-16-23; DL-02-17",
    "16.3.7": "DL-16-25; DL-16-01; C:III",
    "16.3.8": "DL-16-01; C:VII",
    "16.3.9": "DL-16-01; DL-09-18; C:P16",
    "16.4.1": "DL-16-04; DL-16-22",
    "16.4.3": "DL-16-04",
    "16.4.4": "DL-16-04; C:P9",                              # Focus by band, long rest; no summoning allies
    "16.4.5": "DL-16-04",
    "16.4.6": "DL-16-04; DL-16-01; C:P13",
    "16.4.7": "DL-16-06",
    "16.4.8": "DL-08-14; DL-16-04",                          # attunement counts against the PC; inside the line's clamps
    "16.5.1": "DL-00A-27; DL-16-07; DL-16-08",
    "16.5.2": "DL-16-07",
    "16.5.4": "DL-16-08; C:I; C:III",
    "16.5.5": "DL-12-13; DL-00A-15; C:II",                   # drives rolled once on the conduct axes
    "16.5.8": "DL-16-08; DL-00A-20",                         # every tick renders an omen
    "16.6.1": "DL-16-11; C:V",                               # eleven departure causes, closed
    "16.6.3": "DL-16-11",
    "16.6.4": "DL-15-03; C:III",
    "16.6.5": "DL-16-26; C:V",
    "16.6.6": "DL-16-12",
    "16.6.7": "DL-12-10; DL-16-20",                          # standing written once; content leavers are successors
    "16.7.1": "DL-06-01; DL-06-19; C:P9",
    "16.7.2": "DL-16-07; C:VII",
    "16.7.3": "DL-06-19; DL-16-07; DL-16-21",
    "16.7.6": "DL-06-19; DL-16-07",
    "16.7.7": "DL-00A-03; C:I; C:P8",                        # the engine rolls every ally beat
    "16.7.8": "DL-01-24; DL-06-07; DL-06-19",
    "16.7.9": "DL-06-01; DL-06-22; DL-16-07",
    "16.7.10": "DL-06-16",
    "16.8.1": "DL-16-07; C:III",
    "16.8.3": "DL-16-15; DL-10-19",
    "16.8.4": "DL-07-11; DL-16-04",
    "16.8.5": "DL-16-15",
    "16.9.3": "DL-07-20; DL-07-19",
    "16.9.4": "DL-16-16; DL-15-03; DL-16-08",
    "16.9.6": "DL-16-16",
    "16.10.2": "DL-16-06; DL-15-28",
    "16.10.3": "DL-16-04",
    "16.10.5": "DL-06-01; DL-16-17; C:P9",
    "16.11.1": "DL-03-09; DL-11-15",
    "16.11.2": "DL-04-12; C:III",
    "16.11.3": "DL-11-15; DL-03-09",
    "16.12.2": "R5 G-3; DL-16-08",                           # 16.12's basis (16.12.1); opens at the regard moment
    "16.12.3": "DL-16-23; DL-16-06; DL-16-08",
    "16.12.4": "DL-16-08; DL-11-16",
    "16.12.5": "DL-16-12; DL-11-01",
    "16.13.1": "DL-12-13; R5 NP-06",
    "16.13.2": "DL-12-13; C:P3",
    "16.13.4": "DL-16-10; C:IV",                             # the banter budget
    "16.13.5": "DL-12-12",
    "16.14.1": "DL-08-20; DL-16-05",
    "16.14.2": "DL-16-05; DL-15-20",
    "16.14.3": "DL-16-21; DL-16-08",
    "16.14.5": "DL-16-08; DL-16-07",
    "16.14.6": "DL-16-21; DL-16-08",
    "16.15.1": "DL-16-08; C:V",
    "16.15.2": "DL-16-25; DL-16-07",
    "16.15.3": "DL-16-08; C:V",
    "16.15.4": "C:III; R5 EQ-10",
    "16.15.5": "DL-16-25; DL-16-08",
    "16.15.6": "DL-16-01; C:VII",
    "16.16.1": "DL-16-20; DL-11-26; R6 D-R4",
    "16.16.2": "DL-16-20",
}

if __name__ == "__main__":
    apply("16", BASIS)
