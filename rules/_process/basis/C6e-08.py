"""C6e-08.py -- card-level basis tags for ch.08 (Revision C6e, ledger I-065). Run: python rules/_process/basis/C6e-08.py
Each basis is the DL-08 entry whose Decision names the card or its section (property kinds DL-08-01, ladder DL-08-02,
item share DL-08-07, drops DL-08-08/33/34/35, circumstances DL-08-09, base selection DL-08-10, pool gate DL-08-13/29,
attunement DL-08-14, craft DL-08-15/16/17/27/30, gifts DL-08-18, coin and bands DL-08-19, lifestyle and the Unit
DL-08-20, load DL-08-22, item abilities DL-08-23/24, values DL-08-25, sealing DL-08-26, mod groups DL-08-28, prostheses
DL-08-32, job fees DL-08-36, materials DL-08-37), the other chapter's decision the card applies (reduction cap
DL-07-14, Guard DL-06-08, action budget DL-06-01, healing cap DL-05-23, consumable Focus cap DL-05-41, learning
DL-05-08, rites DL-05-24, the reserve DL-05-15, keepers DL-05-35, kits DL-02-13, supply DL-10-06, light DL-10-23,
holdings DL-11-19, retinue places DL-16-02, generator DL-00A-18, verbs DL-00A-19, state DL-00A-22, tags DL-00A-13),
the constitution clause trace-08 maps it to, or the R5 row trace-08 maps its section to (EQ-01 equipment, EQ-02
encumbrance, EQ-04 buying, EQ-07 crafting, EQ-09 supply and light, EQ-10 mounts and vehicles, EQ-11 services, EQ-12
holdings, EQ-13 treasure), and R3 A-23 for 08.6.10's single worked property. Three cards had no recorded basis for
their own numbers: DL-08-39 (08.5.1 body slots), DL-08-40 (08.6.11 batches, scrolls and copies) and DL-08-41
(08.10.4 hull clock) are written for them."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply

BASIS = {
    "08.1.6": "DL-07-14; DL-08-07; C:P12; R5 EQ-01",        # reduction by weight, cap 4, item share 3; paid in other pillars
    "08.1.7": "DL-06-08; DL-07-14; R5 EQ-01",               # +1 edge to Guard; shields reduce nothing
    "08.1.8": "DL-00A-13; C:II; R5 EQ-01",                  # the base-item roster by tag branch
    "08.1.12": "DL-02-13; DL-00A-13",                       # kits by item tag; 00.17.1 Q17
    "08.2.3": "DL-08-02; DL-08-28; DL-08-27; C:V; C:P11",
    "08.2.4": "DL-08-07; C:P11",
    "08.3.4": "DL-08-13; DL-08-29; DL-00A-18; C:P5",
    "08.3.7": "DL-08-09; DL-08-02; DL-08-33",
    "08.3.8": "DL-08-09; DL-08-10; DL-08-24; DL-00A-18",
    "08.3.9": "DL-00A-18; DL-08-09; C:P8",                  # Greater / Flawed degree effects
    "08.3.11": "DL-08-08; DL-08-34; DL-08-19; R5 EQ-13",    # purse, gear and goods; table-only coin entry
    "08.3.12": "DL-08-33; DL-08-08",
    "08.3.13": "C:IV; C:P7; DL-08-26",                      # one-line narration; the codex shows the rest
    "08.4.2": "DL-08-01; C:P10",
    "08.4.3": "DL-08-23; DL-08-24; C:V",
    "08.4.5": "DL-05-23; DL-05-41; R5 EQ-09",
    "08.4.6": "DL-05-08; DL-05-24; DL-08-17",               # learning clock, rite clock, recipes
    "08.4.7": "DL-05-15; DL-05-35; DL-08-07",               # vessel, sign, implement signature
    "08.5.1": "DL-08-39; DL-08-32",
    "08.5.2": "DL-08-14; C:V",
    "08.5.3": "DL-08-26; DL-00A-22; C:P17",
    "08.5.4": "DL-08-16; DL-08-26; DL-00A-18",              # flaws only from Flawed crafts or 09's marked loot
    "08.6.2": "DL-08-37; DL-08-12; DL-08-17; R5 EQ-07",
    "08.6.5": "DL-08-15; DL-08-16; R5 EQ-11",
    "08.6.6": "DL-08-16; DL-08-30; C:P8",
    "08.6.9": "DL-08-17; DL-08-15; C:P15",
    "08.6.10": "DL-08-27; R3 A-23",
    "08.6.11": "DL-08-40; DL-08-16",
    "08.6.12": "DL-08-15; DL-00A-19",                       # improvised work weighted, capped at common; Handle's crude fallback
    "08.6.13": "DL-11-19; DL-08-19; R5 EQ-12",
    "08.7.3": "DL-08-18; DL-08-23",
    "08.7.4": "DL-08-18; C:III",
    "08.8.2": "DL-08-19",
    "08.8.3": "DL-08-25; DL-08-02",
    "08.8.4": "DL-08-19; R5 EQ-04",
    "08.8.10": "DL-08-20; DL-08-35; DL-08-36; R5 EQ-13",
    "08.9.1": "DL-08-22; R5 EQ-02",
    "08.9.2": "DL-08-22; R5 EQ-02",
    "08.9.3": "R5 EQ-02; DL-06-01",                         # drawing from the pack is an action
    "08.9.4": "DL-10-06; R5 EQ-09",
    "08.9.5": "DL-10-23; R5 EQ-09",
    "08.9.6": "DL-08-04; R5 EQ-09",
    "08.10.1": "R5 EQ-10; DL-16-02",                        # bought as an item, a beast ally at 0 places
    "08.10.2": "DL-08-20; R5 EQ-10",
    "08.10.3": "R5 EQ-10",
    "08.10.4": "DL-08-41; R5 EQ-10",
}

if __name__ == "__main__":
    apply("08", BASIS)
