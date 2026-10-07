"""C6b-01.py -- card-level basis tags for ch.01 (Revision C6b, ledger I-065). Run: python rules/_process/basis/C6b-01.py
Each basis is the DL-01 entry whose Decision names the card or its section, the DL-00A architecture decision the card
implements (frame and supplied ids DL-00A-02, dice DL-00A-03, envelope DL-00A-04, attributes DL-00A-08, levers
DL-00A-10, severity/stakes/reach DL-00A-11, licenses and the fifteen verbs DL-00A-19), a later DL that names it, or the
constitution clause trace-01 maps it to. One card had no recorded basis: 01.7.4 (auto-commit) now has DL-01-28."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply

VERB = "DL-00A-19; DL-00A-08"   # the fifteen closed verbs (R7) and the verb -> attribute map

BASIS = {
    "01.1.2": "DL-00A-19; DL-01-20",               # literal reading with beat splitting; beats per declaration
    "01.1.3": "DL-00A-23; C:P13",                  # roll_check requires a committed frame
    "01.1.4": "DL-00A-02; C:I",
    "01.3.2": "DL-00A-19; C:V",
    "01.3.8": "DL-00A-19; DL-01-13; C:VII",        # gate classes G0-G4; sealed Oracle for existence questions
    "01.6.1": "DL-00A-08",
    "01.6.2": "DL-00A-06; DL-00A-13",
    "01.6.4": "DL-00A-02; DL-01-21",
    "01.6.6": "DL-00A-03",
    "01.6.12": "DL-00A-02; DL-00A-04; C:I",
    "01.7.4": "DL-01-28",                          # new
    "01.8.2": "DL-01-03; C:P8",
    "01.8.3": "DL-01-02; DL-01-04",
    "01.8.4": "DL-00A-16; DL-01-06",               # closed on_roll hook; the fate reroll
    "01.9.1": "DL-00A-11; DL-01-22",
    "01.9.2": "DL-01-04",
    "01.9.4": "DL-01-15; DL-01-07",                # exact writes per severity; the declared alternate
    "01.10.2": "DL-01-12; C:P17",
    "01.10.3": "DL-01-12; C:P17",
    "01.10.6": "DL-01-16; C:P17",
    "01.10.7": "DL-01-12; DL-01-20",
    "01.11.1": "DL-01-04; DL-01-07; DL-01-15",
    "01.12.2": "C:P13; DL-00A-02; DL-00A-20",      # narration follows state; one omen per hidden tick
    "01.12.3": "DL-00A-12; DL-00A-24",             # registered handler; ruling ledger
    "01.13.2": "DL-01-15; DL-00A-29",
    "01.13.3": "DL-01-15",
    "01.13.4": "DL-01-15; DL-08-05",
    "01.13.5": "DL-01-15",
    "01.13.6": "DL-01-15; DL-15-18",
    "01.13.7": "DL-01-15; DL-00A-21",
    "01.13.8": "DL-01-15",
    "01.13.9": "DL-01-15; DL-00A-27",              # closed door's standing steps
    "01.13.10": "DL-01-15; DL-12-15",
    "01.14.2": "DL-01-12",
    "01.14.10": "DL-00A-19",
    "01.15.3": "DL-01-11",
    "01.15.5": "DL-01-11; DL-01-26; C:P16",
    "01.15.6": "DL-01-13",
    "01.15.8": "DL-01-26; DL-00A-10",
    "01.16.1": "DL-00A-26; DL-01-06",
    "01.16.3": "DL-01-06",
    "01.16.4": "DL-00A-26; DL-07-07",
    "01.18.1": "DL-00A-19; DL-00A-01",             # the R7 anchor standard
    "01.18.2": "DL-01-02; DL-01-22",
    "01.18.3": "DL-01-23",
    "01.18.4": VERB,
    "01.18.5": VERB,
    "01.18.6": VERB + "; DL-02-12",                # lore specialties are licenses
    "01.18.7": VERB,
    "01.18.8": VERB + "; DL-00A-29",
    "01.18.9": VERB,
    "01.18.10": VERB,
    "01.18.11": VERB,
    "01.18.12": VERB + "; DL-01-23",
    "01.18.13": VERB,
    "01.18.14": VERB,
    "01.18.15": VERB + "; DL-01-23",
    "01.18.16": VERB + "; DL-00A-10",              # Setup creates a lever
    "01.18.17": VERB + "; DL-01-24",
    "01.18.18": VERB,
    "01.18.19": "DL-00A-19",                       # Yield and Retreat are named uses of Talk and Move
}

if __name__ == "__main__":
    apply("01", BASIS)
