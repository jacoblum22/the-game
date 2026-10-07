"""C6b-00.py -- card-level basis tags for ch.00 (Revision C6b, ledger I-065). Run: python rules/_process/basis/C6b-00.py
Each basis is the DL-00 / DL-00A entry whose Decision fixes the card (the architecture decisions, each with its research
evidence), a later DL that names the card, the constitution clause trace-00 maps it to, or the orchestration BRIEF
section the card restates (`[R: rules/_process/BRIEF.md §N]`, a repo artifact under 00.1.6: §9/§A1 chapter map and
contracts, §12 data file conventions). One card had no recorded basis: 00.1.3 (reading order) now has DL-00A-33."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply

BASIS = {
    "00.1.1": "DL-00A-24; DL-00A-22; C:P7",        # core + retrieved cards; visibility classes; codex
    "00.1.2": "R: rules/_process/BRIEF.md §A1",    # the revised chapter map
    "00.1.3": "DL-00A-33",                         # new: reading order follows dependency
    "00.2.3": "DL-00A-01; C:III",                  # mandatory "Worst case:" line
    "00.2.5": "DL-00A-01; DL-INT-12",              # rule template; two compliant forms
    "00.3.4": "DL-00A-01; DL-00A-16",              # SG-23 integers, no percentages
    "00.3.11": "DL-00A-11; DL-00A-29",
    "00.3.14": "DL-00A-11; DL-01-04",
    "00.4.4": "DL-00A-07",                         # each attribute feeds at most one listed derived value
    "00.5.5": "DL-00A-13; DL-00A-32",
    "00.6.2": "DL-00A-22",
    "00.6.7": "DL-00A-22; DL-00A-01",              # typed facts; SG-06 assertion is not fact
    "00.7.3": "DL-00A-12",
    "00.7.4": "DL-00A-12; DL-INT-08",
    "00.7.5": "DL-00A-12; DL-INT-05",
    "00.7.6": "DL-00A-12",
    "00.7.8": "DL-00A-12",                         # "interrupts halt the skip"
    "00.8.3": "DL-00A-20",
    "00.8.6": "DL-00A-20",                         # links; tug
    "00.8.7": "DL-00A-20",
    "00.9.2": "DL-00A-21",
    "00.9.4": "DL-00A-21; DL-06-12",
    "00.10.5": "DL-00A-16; DL-00A-29",
    "00.12.6": "DL-00A-19",                        # basic tier = fifteen verbs plus free activities
    "00.13.2": "DL-00A-02; DL-00A-10; DL-00A-11",  # committed frame; cited levers; lethal legality (INV-6)
    "00.14.1": "DL-00A-23",
    "00.14.2": "DL-00A-23",
    "00.14.3": "DL-00A-02; C:I",                   # INV-3
    "00.15.2": "DL-00A-24",
    "00.15.3": "DL-00A-24; DL-12-16",
    "00.15.5": "DL-00A-24; C:III",
    "00.16.1": "R: rules/_process/BRIEF.md §12",
    "00.16.2": "DL-INT-11; R: rules/_process/BRIEF.md §12",
    "00.16.4": "R: rules/_process/BRIEF.md §12",
    "00.16.5": "DL-INT-01; R: rules/_process/BRIEF.md §12",
    "00.17.2": "R: rules/_process/BRIEF.md §9, §A1",
    "00.18.1": "DL-00A-01",                        # SG-21 canonical names / banned words
}

if __name__ == "__main__":
    apply("00", BASIS)
