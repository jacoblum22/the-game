"""C6a-06.py -- card-level basis tags for ch.06 (Revision C6a, ledger I-065). Run: python rules/_process/basis/C6a-06.py
Each basis is the DL entry whose Decision names the card or its section, the constitution clause trace-06 maps it to,
or the research row trace-06 maps its section to (R5's completeness rows CF-01...CF-16: CF-01 06.2, CF-02 06.1,
CF-03 06.3, CF-04 06.4, CF-05 06.4.1, CF-06 06.7, CF-07 06.6, CF-08 06.11, CF-09 06.12, CF-10 06.11.7,
CF-11 06.3.7, CF-12 06.5.8-06.5.10, CF-13 06.14, CF-14 06.15). Maneuvers are basic verbs used as anchors
(DL-00A-19, DL-00A-24). One card had no recorded basis (06.3.10's size ladder): DL-06-30 is written for it."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_basis import apply, RULES

BASIS = {
    "06.1.3": "DL-06-01; C:P9",
    "06.1.4": "DL-00A-19; DL-06-01",             # free activities beside the fifteen basic verbs
    "06.1.5": "DL-06-22; DL-12-26",              # Defend is Evade, an engine snag on the attacker
    "06.1.6": "DL-06-03; C:P9",
    "06.1.7": "DL-06-02; C:P14",
    "06.1.8": "DL-06-01; R5 CF-02",
    "06.2.1": "DL-00A-12; R5 CF-01",             # conflict_start: a time-mode boundary
    "06.2.3": "DL-00A-12; R5 CF-01",             # the round boundary and its handlers
    "06.2.5": "DL-00A-20; R5 CF-01",             # reinforcements only through clocks with omens
    "06.3.1": "DL-06-07; C:IV; C:P3; C:P13",
    "06.3.2": "DL-06-07",
    "06.3.3": "DL-06-07",
    "06.3.4": "DL-06-07",
    "06.3.5": "DL-06-07",
    "06.3.6": "DL-06-07",
    "06.3.7": "DL-06-07; R5 CF-11; C:VII",
    "06.3.8": "DL-06-11; C:III",                 # features as a closed feature_kind enum
    "06.3.9": "DL-06-07; R5 CF-03",
    "06.3.10": "DL-06-30; C:VII",
    "06.4.1": "DL-06-08; R5 CF-05",
    "06.4.4": "DL-06-06; DL-06-02",
    "06.4.6": "DL-00A-16; DL-00A-29; C:P8",      # one evaluation pass; fixed harm magnitudes
    "06.4.7": "DL-00A-10; R5 CF-11",             # snags are the only situational currency
    "06.4.9": "DL-06-06; DL-08-04",              # reloads in T-06-6
    "06.4.11": "DL-00A-03; R5 CF-04",            # who rolls: the target withstands
    "06.5.1": "DL-00A-19; DL-00A-24; C:P8",
    "06.5.2": "DL-00A-19; C:P8",
    "06.5.3": "DL-00A-19; C:P8",
    "06.5.4": "DL-00A-19; DL-12-26",
    "06.5.5": "DL-00A-19; DL-00A-10",
    "06.5.6": "DL-00A-19; DL-06-07",
    "06.5.7": "DL-00A-10; DL-06-07",
    "06.5.8": "DL-06-11; DL-06-27; R5 CF-12",
    "06.5.9": "DL-00A-10; DL-06-03",             # a Precision lever that cancels one repetition snag
    "06.6.1": "DL-06-01; DL-00A-17; R5 CF-07",   # one reaction a round; depth 1
    "06.6.3": "DL-06-22; C:P10",
    "06.6.4": "DL-06-22; C:P6",
    "06.6.5": "DL-06-01; DL-09-04",
    "06.6.6": "DL-06-01; R5 CF-07",
    "06.6.7": "DL-06-19; R5 CF-13",
    "06.7.1": "DL-06-12; R5 CF-06",
    "06.7.2": "DL-06-13",
    "06.7.5": "DL-00A-21",                       # closed stacking vocabulary, exclusion groups
    "06.7.6": "DL-00A-16; DL-06-07",             # engine expressions over position and conditions
    "06.8.1": "DL-06-15; C:P6",
    "06.8.2": "DL-06-15",
    "06.9.2": "DL-06-16; C:I",
    "06.9.4": "DL-06-16",
    "06.9.6": "DL-06-16; C:P3; C:P17",
    "06.10.2": "DL-06-20",
    "06.10.3": "DL-06-20",
    "06.10.4": "DL-06-20; DL-06-27",
    "06.10.5": "DL-06-20",
    "06.10.6": "DL-06-25",
    "06.11.2": "DL-06-18",
    "06.11.3": "DL-06-18",
    "06.11.4": "DL-06-18; DL-00A-20",
    "06.11.5": "DL-06-18",
    "06.11.6": "DL-06-18",
    "06.11.7": "DL-06-18; C:VII; C:P16; R5 CF-10",
    "06.12.1": "DL-06-21; C:P16; R5 CF-09",
    "06.12.2": "DL-06-21",
    "06.12.3": "DL-06-21; C:P8",
    "06.12.4": "DL-06-21",
    "06.12.5": "DL-06-21",
    "06.12.6": "DL-06-21",
    "06.13.1": "R1 §06; DL-00A-12",              # "victory conditions should be a field of the encounter"
    "06.13.3": "DL-06-23",
    "06.13.4": "C:VI; C:P16",
    "06.14.3": "DL-06-19",
    "06.14.4": "DL-06-19; C:V",
    "06.14.5": "DL-06-19",
    "06.15.1": "DL-16-24; R5 CF-14",
    "06.15.2": "C:VII; R5 CF-14",
    "06.15.3": "R5 CF-14",
    "06.15.4": "R5 CF-14",
    "06.15.5": "R5 CF-14; DL-06-07",
}

DL_06_30 = """### DL-06-30: Size is a six-rung ladder stored on the template, read through levers, snags, reach and capacity (revision I-065)
- Decision: 06.3.10 as written: `tiny` · `small` · `medium` · `large` · `huge` · `colossal`, stored in the creature's template (09; a PC is `medium`), never picked by the DM in play. A size step does five things (`data/conflict.yaml#sizes`): against a larger target, Grapple and Force lose one reach rung per step (an engine-cited Amplifying snag; two steps leave G4 for moving or holding the whole creature, with a redirect); against a smaller target they take one Amplifying lever; large melee reaches `band.close`, huge and colossal `band.near`; engagement capacity rises by 2 per step (06.3.5); a mount is at least one step larger than its rider, and a creature two steps larger is a `cover` feature. Recorded at revision C6a: the card shipped with no entry of its own.
- Alternatives considered: no size (rejected: a giant and a goblin would grapple alike, and "I lift the dragon" would have no principled refusal); size as a new modifier family on rolls (rejected: DL-00A-10 makes levers and snags the only situational currency, inside the ±4 cap); size on a grid of squares (rejected: there is no grid, positions are bands and links, DL-06-07); size chosen by the DM per scene (rejected: a judgment where a stored field does, and drift between scenes).
- Evidence: [C:VII] (moving a creature two steps larger is G4 with a redirect, not a harder roll); DL-00A-10; DL-06-07 (bands, links and capacity); DL-06-11 (object size rungs hand / body / heavy / massive, the same discrete shape for objects); [R5 CF-03] (positioning in text without a grid).
- Serves: goal 2 (the engine reads one field; the DM never sets it).
- Revisit if: 09's templates need a seventh rung, or play shows two-step grapples are wanted more often than the redirect allows."""

def add_dl():
    f = os.path.join(RULES, "appendix", "fragments", "DL-06.md")
    d = open(f, encoding="utf-8").read()
    if "### DL-06-30:" not in d:
        open(f, "w", encoding="utf-8").write(d.rstrip("\n") + "\n\n" + DL_06_30 + "\n")

if __name__ == "__main__":
    add_dl()
    apply("06", BASIS)
