"""C6d-15.py -- card-level basis tags for ch.15 (Revision C6d, ledger I-065). Run: python rules/_process/basis/C6d-15.py
Each basis is the DL-15 entry whose Decision names the card or its section (standing rungs DL-15-01, valences
DL-15-03, caps DL-15-04, methods DL-15-08, request size DL-15-09, terms DL-15-12, delivery DL-15-13, threats and
taunts DL-15-14, audiences DL-15-15, plausibility DL-15-16, lies DL-15-17, alertness DL-15-18, deals DL-15-20,
campaigns DL-15-22, the Three Clue Rule DL-15-24, core clues DL-15-25, deduction DL-15-26, the downtime week
DL-15-27, learning DL-15-28, fact licenses DL-15-31, contests DL-15-32, certainty DL-15-33/34), the other chapter's
decision the card applies (DL-00A-10/11/20/22/27, DL-01-01, DL-02-12, DL-03-12, DL-04-22, DL-05-24, DL-06-20,
DL-07-11/13/15, DL-08-16/19/20, DL-09-18, DL-11-11/13/15/18/19, DL-12-10/11/13, DL-16-02/05), the constitution
clause trace-15 maps the card to, or the R5 row trace-15 maps its section to (NP-03 15.1, SO-01 15.3-15.4,
SO-03 15.7.1-15.7.4, SO-07 15.7.6, EX-11 15.9, TM-06 15.10-15.13, AD-05 15.11.4, MG-04 15.13.4) or that names the
card's subject (SO-04 languages for 15.2.7, SO-06 rumors for 15.9.18 and the rumor-yielding days, LW-14 notoriety
for Lie low). No card lacked a recorded basis."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply

BASIS = {
    "15.1.5": "DL-15-03; DL-15-04; C:I; R5 NP-03",          # the closed source list; tool writes only
    "15.1.6": "DL-15-03; C:III",
    "15.1.8": "DL-00A-27; DL-12-10; R5 NP-03",               # one scale; NPC-to-NPC by the reaction roll
    "15.1.9": "DL-15-01; C:P3",                              # the rung's behavior contract; narration matches state
    "15.2.2": "DL-15-12; DL-15-34; DL-12-13",                # wants as terms; defeating a want; rolled at depth
    "15.2.5": "DL-15-12; DL-15-34; C:P12",                   # fear as Leverage; not also a snag; weakness vocabulary
    "15.2.7": "DL-09-18; DL-02-12; C:VII; R5 SO-04",         # five minds; tongues; gate by state
    "15.3.1": "DL-15-08; R5 SO-01",
    "15.3.6": "DL-00A-10; C:III",                            # 00.3.9's levers unchanged; a catalog for the flag
    "15.3.8": "DL-15-32; DL-00A-11; R5 SO-01",
    "15.3.9": "DL-15-13; C:P8",
    "15.3.10": "DL-15-33; DL-15-34",
    "15.4.4": "DL-15-14; R5 SO-01",                          # standing does not enter provocation
    "15.4.6": "DL-15-09; DL-15-33; C:III",                   # within duty = R1, certain at Neutral+
    "15.4.7": "DL-15-15; DL-06-20; C:IV",                    # crowds are obstacles, not people; mobs in conflict
    "15.5.5": "DL-15-17; C:I",
    "15.5.6": "DL-15-31; DL-15-16; C:VII",                   # persona license; claims; specific-person disguise licensed
    "15.7.3": "DL-15-20; DL-15-01; R5 SO-03",
    "15.7.4": "DL-15-01; R5 SO-03",
    "15.7.6": "DL-15-20; DL-15-03; R5 SO-07",
    "15.8.2": "DL-15-22",
    "15.8.4": "C:P8; C:III; R5 SO-01",                       # interrogation clocks ticked by delivered reach
    "15.9.2": "DL-15-24; DL-15-26; R5 EX-11",
    "15.9.3": "C:P5; C:I; R5 EX-11",                         # clu.*.found with frame ids; clue writes
    "15.9.6": "C:V; R5 EX-11",                               # nine method kinds, closed
    "15.9.8": "DL-15-24; DL-12-11; R5 EX-11",                # live leads; lead injection
    "15.9.11": "DL-15-26; C:P13",                            # the solution never moves
    "15.9.13": "DL-00A-20; R5 EX-11",                        # opposition clock with omens
    "15.9.14": "DL-01-01; DL-00A-20; R5 EX-11",              # archive tier on the DC ladder; extended clock
    "15.9.15": "DL-15-18; DL-00A-20; R5 EX-11",              # racing clocks; alertness on notice
    "15.9.16": "C:P7; C:IV; DL-00A-22",                      # the player's record; nothing sealed
    "15.9.18": "DL-11-11; R5 SO-06",
    "15.9.19": "DL-15-24; C:P16",
    "15.10.3": "DL-15-27; DL-08-20; R5 TM-06",
    "15.10.5": "DL-15-27; R5 TM-06",
    "15.10.6": "C:P5; C:P2; DL-03-12",
    "15.11.2": "DL-15-28; DL-11-18; DL-15-09",               # teachers from institutions; teaching is a request
    "15.11.3": "DL-15-28; DL-00A-19; C:VII",                 # acquisition paths; rolls never grant
    "15.11.4": "R5 AD-05; C:VI",
    "15.11.5": "DL-04-22; DL-15-27",                         # atonement by a clock; a week activity
    "15.11.6": "DL-15-28; C:P2; C:VII",
    "15.13.1": "DL-15-27; DL-07-11; R5 TM-06",
    "15.13.2": "DL-15-27; DL-07-15; R5 TM-06",
    "15.13.3": "DL-15-27; DL-07-13; R5 TM-06",
    "15.13.4": "DL-15-27; DL-05-24; R5 MG-04",
    "15.13.5": "DL-15-27; DL-08-16; R5 TM-06",
    "15.13.6": "DL-15-27; DL-15-04; R5 TM-06",
    "15.13.7": "DL-15-27; DL-08-19; R5 TM-06",               # wages and the labor cap
    "15.13.8": "DL-15-27; R5 TM-06; R5 SO-06",
    "15.13.9": "DL-15-27; DL-15-25; R5 SO-06",               # core placements without a roll
    "15.13.10": "DL-15-27; DL-15-20; R5 SO-03",
    "15.13.11": "DL-15-27; DL-11-19; R5 TM-06",
    "15.13.12": "DL-15-27; DL-15-03; DL-11-15",              # helped +1; reputation entry in the faith's scope
    "15.13.13": "DL-15-27; DL-15-31",
    "15.13.14": "DL-15-27; DL-16-05; DL-16-02",
    "15.13.15": "DL-15-27; DL-11-13; R5 LW-14",
    "15.13.16": "DL-15-27; R5 TM-06",
}

if __name__ == "__main__":
    apply("15", BASIS)
