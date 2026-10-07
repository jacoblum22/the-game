"""C7-11.py -- card-level basis tags for ch.11 (Revision C7, ledger I-065). Run: python rules/_process/basis/C7-11.py
Each basis is the DL-11 entry whose Decision names the card or its section (World Turn DL-11-01/02, situations and
propagation DL-11-07, traces DL-11-10, rumors DL-11-11/29, lifecycles DL-11-12, reputation DL-11-15, threads
DL-11-16/17, ranks DL-11-18, holdings DL-11-19, retirement DL-11-20, calendar DL-11-21, aging DL-11-22, the season
boundary DL-11-23, the chronicle DL-11-24, legacy ledgers DL-11-25, successors DL-11-26, open seats DL-11-32), the other
chapter's decision the card applies (principal NPCs DL-12-13, the seed DL-12-21/24, twists DL-12-15, gifts DL-08-18),
the constitution clause trace-11 maps it to, or the R5 row that names its subject (LW-01 factions, LW-05 propagation,
LW-06 region generation, LW-11 retirement, LW-13 the thread register, SO-06 rumors, AD-07 reputation and titles,
EQ-12 holdings, TM-07 calendar, TM-08 season phase, HR-10 aging, HR-11 continuity). Two cards had no recorded basis
for their own numbers: DL-11-35 (11.9.5 strikes on holdings, 11.9.6 improvements) and DL-11-36 (11.10.4 festival
effects) are written for them (C7-appendix.py)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply

BASIS = {
    "11.1.5": "DL-11-02; DL-11-10; C:P3",                   # narrator view: behavior, omens, traces; sealed stays sealed
    "11.2.6": "DL-11-01; DL-11-20",                         # the World Turn runs unchanged through a retirement timeskip
    "11.3.17": "DL-11-32; DL-12-13; R5 LW-01",              # officers are principal NPCs; open seats
    "11.3.18": "DL-12-21; DL-12-24; R5 LW-06",              # factions come from the seed or a setting that passes the check
    "11.4.3": "DL-11-07; C:V; R5 LW-05",                    # closed list of situation sources; sealed timelines
    "11.4.10": "DL-12-15; DL-11-07",                        # world queries for 12's S5 twist rows
    "11.5.2": "DL-11-16; DL-11-12; C:V; R5 LW-13",          # thread kinds; vows never expire
    "11.5.8": "DL-11-12; DL-11-17; DL-11-01; R5 LW-13",     # step 8 upkeep: expiry, stalls, fallbacks
    "11.5.12": "DL-11-16; DL-11-17; R5 LW-13",              # other chapters' threads on the one register
    "11.6.5": "DL-11-11; DL-11-01; R5 SO-06",               # spread by scope steps at step 7
    "11.6.6": "DL-11-10; DL-11-11; R5 SO-06",               # news is the always-true trace kind
    "11.6.7": "DL-11-11; R5 SO-06",
    "11.6.8": "DL-11-11; DL-11-15; R5 SO-06",               # deeds seed rumors that reputation scores
    "11.6.9": "DL-11-29; DL-11-11; R5 SO-06",               # planted rumors
    "11.7.4": "DL-11-15; DL-11-23; R5 AD-07",               # spread at score - 2 at the Season Turn
    "11.7.8": "DL-11-15; R5 AD-07",
    "11.7.10": "DL-11-15; DL-11-26; R5 AD-07",              # renown and breadth, read by legend and inheritance
    "11.8.2": "DL-11-18; C:VII; R5 AD-07",                  # seats, never capability
    "11.8.3": "DL-11-18; DL-11-21",                         # sittings; quarter days
    "11.8.4": "DL-11-18; C:V; C:VII",                       # closed list of benefits
    "11.8.5": "DL-11-18",                                   # duty, service, values
    "11.9.2": "DL-11-19; R5 EQ-12",
    "11.9.3": "DL-11-19; DL-11-01; R5 EQ-12",               # holdings in step 2
    "11.9.5": "DL-11-35; DL-11-19; R5 EQ-12",
    "11.9.6": "DL-11-35; DL-11-19; C:V; R5 EQ-12",
    "11.9.9": "DL-08-18; C:P5",                             # whether a gift is due is 11's, what is given 08's
    "11.10.2": "DL-11-21; R5 TM-07",
    "11.10.3": "DL-11-21; R5 TM-07",                        # 28-day moon, thirteen a year
    "11.10.4": "DL-11-36; DL-11-21; C:V; R5 TM-07",
    "11.11.3": "DL-11-23; DL-11-12; C:VI; R5 TM-08",
    "11.11.5": "DL-11-22; DL-11-24; DL-11-21; R5 TM-08",    # aging, annual festival, year digest
    "11.12.3": "DL-11-24; C:P13",
    "11.12.4": "DL-11-24; C:P13",
    "11.12.5": "DL-11-24",
    "11.13.2": "DL-11-20; C:V; R5 LW-11",
    "11.13.6": "DL-11-26; DL-11-25; R5 LW-11",              # bequeathed threads at half progress
    "11.13.7": "DL-11-20; C:P2; R5 HR-11",
    "11.13.11": "DL-11-26; DL-11-10; R5 HR-11",             # queue refilled; kickers
}

if __name__ == "__main__":
    apply("11", BASIS)
