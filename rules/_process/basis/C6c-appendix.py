"""C6c-appendix.py -- DL-10-31, DL-INT-13's evidence and the BRIEF §6 trace rows for ch.09-10 (Revision C6c, ledger
I-065). Run: python rules/_process/basis/C6c-appendix.py  (idempotent), then integration-assemble-appendix.py."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.normpath(os.path.join(HERE, "..", "..", "appendix"))
FR = os.path.join(APP, "fragments")

DL_10_31 = """### DL-10-31: A place's settlement scope is its nearest settlement within 8 travel watches, else none (revision I-065)
- Decision: [revision: I-065] 10.1.6: every area and site stores `settlement_scope`, the place id of the settlement whose people would hear of what is done there: the one the region's seed or setting names as the area's market, else the nearest settlement by route watches. A settlement's scope is itself. An area with no settlement within 8 travel watches stores `null`, and deeds done there reach only the witnesses' own scopes (03.10.5). 03's witness scopes and 11's reputation read the field; nothing else computes it.
- Alternatives considered: computing the scope at each deed from the graph (rejected: 03.10.5 and 11 would each walk the graph and could disagree, and a stored field is one value the codex and both chapters read); the nearest settlement at any distance (rejected: a deed in the deep wild would reach a town four days off with no carrier, against DL-03-09's rule that only carried deeds go public); scope by region (rejected: too coarse for 11's per-settlement reputation).
- Evidence: the field answers 03's interface request (settlement ancestry on places, 10's request table) and feeds DL-03-09's public tally and DL-11-15's witnessed reputation. The 8-watch line is a default, not a measured value: on 10.3.3's default day of two travel watches it is four days' walk from the nearest gate; no simulation or playtest set it. The card carried no basis of its own until revision C6c's audit (I-065).
- Serves: goal 2 (one stored field, read the same way by 03 and 11); goal 1 (what is done in the deep wild stays the witnesses' story).
- Revisit if: 11's reputation in play shows deeds near a ring's edge flipping in and out of a town's knowledge as areas are generated (then store the scope at generation and never recompute it, or widen the line)."""

INT13_OLD = "(00.1.3's reading order) and DL-01-28 (01.7.4's auto-commit)."
INT13_NEW = INT13_OLD + (" Revision C6c audited ch.09-10 (180 rule cards): 133 carried no tag of their own (ch.09 50, ch.10 83);"
                         " all 133 are tagged by `rules/_process/basis/C6c-09.py` and `C6c-10.py`. One card had no recorded"
                         " basis and gained one: DL-10-31 (10.1.6's settlement scope). Again no card's only honest basis was a"
                         " derivation.")

ROW = {
    "09": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 09 (76); 50 tagged at revision C6c; validator BASIS (DL-INT-13) | satisfied |",
    "10": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 10 (104); 83 tagged at revision C6c, 10.1.6 by the new DL-10-31; validator BASIS (DL-INT-13) | satisfied |",
}


def rw(p, f):
    s = open(p, encoding="utf-8").read()
    t = f(s)
    if t != s:
        open(p, "w", encoding="utf-8", newline="\n").write(t)


def add_10(s):
    if "### DL-10-31:" in s:
        return s
    return s.rstrip("\n") + "\n\n" + DL_10_31 + "\n"


def int13(s):
    if "Revision C6c audited" in s:
        return s
    assert s.count(INT13_OLD) == 1
    return s.replace(INT13_OLD, INT13_NEW)


def main():
    rw(os.path.join(FR, "DL-10.md"), add_10)
    rw(os.path.join(FR, "DL-INT.md"), int13)
    for c, row in ROW.items():
        p = os.path.join(FR, "trace-%s.md" % c)
        lines = open(p, encoding="utf-8").read().rstrip("\n").split("\n")
        if any(l.startswith("| BRIEF §6 |") for l in lines):
            continue
        last = max(i for i, l in enumerate(lines) if l.startswith("|"))
        lines.insert(last + 1, row)
        open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("DL-10-31, DL-INT-13 evidence and two BRIEF §6 trace rows in place")


if __name__ == "__main__":
    main()
