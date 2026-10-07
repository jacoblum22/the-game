"""C6b-appendix.py -- DL-00A-33, DL-01-28, DL-INT-13's evidence and the BRIEF §6 trace rows for ch.00-03
(Revision C6b, ledger I-065). Run: python rules/_process/basis/C6b-appendix.py  (idempotent), then
integration-assemble-appendix.py. DL-00 / DL-00A live in decision-log.md's hand-written head (above the assembly
marker), so DL-00A-33 is inserted there, after DL-00A-32."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.normpath(os.path.join(HERE, "..", "..", "appendix"))
FR = os.path.join(APP, "fragments")
MARK = "<!-- ===== assembled at integration from appendix/fragments/ (do not edit below; edit the fragments) ===== -->"

DL_00A_33 = """### DL-00A-33: Reading order follows dependency, not chapter number (revision I-065)
- Decision: [revision: I-065] 00.1.3: implementers and chapter authors read 00 → 01 → 12 → 03 → 04 → 05 → 06 → 07 → 02 → 08 → 09 → 10 → 15 → 16 → 11 → 13 → 14; players read 14 → 13 (opening only) → the codex; the AI DM at runtime reads nothing in order and receives the always-loaded core plus retrieved cards (DL-00A-24).
- Alternatives considered: chapter-number order (rejected: 02 builds a character out of 03's tags, 04's floor and power band, 05's Focus and 07's Vitality, so a reader meeting it second meets terms not yet defined; 12's turn loop is the frame every later procedure runs inside, so it follows 01's pipeline directly); no stated order (rejected: authors writing in parallel need one shared order for which chapter's terms they may take as given).
- Evidence: the dependency direction of 00.1.2 ("dependencies run downward only through the contracts in 00.17") and the "Consumes" column of 00.17.2; the chapter map of BRIEF §A1. The card carried no basis of its own until revision C6b's audit (I-065).
- Serves: goal 2 (authors and implementers meet each term after the rule that defines it).
- Revisit if: a chapter's "Consumes" row in 00.17.2 names a chapter that comes after it in this order (then reorder)."""

DL_01_28 = """### DL-01-28: Auto-commit rolls only frames the player has already accepted in principle (revision I-065)
- Decision: [revision: I-065] 01.7.4: with the player's `auto_commit` preference on, a frame rolls without waiting (`offer.choice = auto`) only when its stakes are Safe or Risky, it is not lethal, not secret, carries no mode price (no fallback, stretch or emulate), and shows success-or-better ≥ 50%; the OFFER is still logged and shown with the result. Every other frame waits for an explicit commit, and a lethal frame never auto-commits (00.13.2).
- Alternatives considered: no auto-commit (rejected: a Safe or Risky frame the player would take anyway costs a round-trip per beat, against goal 1's flow); auto-commit on any frame the player has not vetoed (rejected: Dire and lethal frames and mode prices are the choices the OFFER exists for, BRIEF A2 #2 and DL-01-07, and a secret frame shows no odds to accept).
- Evidence: each exclusion restates a rule that already holds: a lethal frame needs an explicit commit (00.13.2, INV-6, DL-00A-11); a secret frame shows no DC or odds (DL-01-13); fallback, stretch and emulate are prices the player consents to (DL-00A-19). The 50% line is a default, not a measured value: it is the point at which success is at least as likely as not, so the engine never auto-rolls a frame the odds argue against. The card carried no basis of its own until revision C6b's audit (I-065).
- Serves: goal 1 (fewer pauses on choices already made in principle); goal 2 (the boundary is a closed test the engine checks).
- Revisit if: preference logs show players turning auto-commit off after an auto-rolled failure, or re-declaring after auto-rolled frames (then raise the line or exclude Risky)."""

INT13_OLD = "05.8.6's stale \"until ch.04 agrees\" sentence was corrected (04.8.4 had adopted the request)."
INT13_NEW = INT13_OLD + (" Revision C6b audited ch.00-03 (357 rule cards): 141 carried no tag of their own (ch.00 37, ch.01 61,"
                         " ch.02 21, ch.03 22); all 141 are tagged by `rules/_process/basis/C6b-00.py` ... `C6b-03.py`. Six"
                         " ch.00 cards restating the orchestration brief cite it as a repo artifact (`[R: rules/_process/BRIEF.md"
                         " §N]`); two cards had no recorded basis and gained one: DL-00A-33 (00.1.3's reading order) and DL-01-28"
                         " (01.7.4's auto-commit). No card's only honest basis was a derivation, so the revisit clause's fifth"
                         " form was not needed.")

ROW = {
    "00": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 00 (113); 37 tagged at revision C6b, 00.1.3 by the new DL-00A-33; validator BASIS (DL-INT-13) | Satisfied |",
    "01": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 01 (121); 61 tagged at revision C6b, 01.7.4 by the new DL-01-28; validator BASIS (DL-INT-13) | satisfied |",
    "02": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 02 (60); 21 tagged at revision C6b; validator BASIS (DL-INT-13) | satisfied |",
    "03": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 03 (63); 22 tagged at revision C6b; validator BASIS (DL-INT-13) | satisfied |",
}


def rw(p, f):
    s = open(p, encoding="utf-8").read()
    t = f(s)
    if t != s:
        open(p, "w", encoding="utf-8", newline="\n").write(t)


def add_00a(s):
    if "### DL-00A-33:" in s:
        return s
    assert s.count(MARK) == 1
    head, tail = s.split(MARK)
    return head.rstrip("\n") + "\n\n" + DL_00A_33 + "\n\n" + MARK + tail


def add_01(s):
    if "### DL-01-28:" in s:
        return s
    return s.rstrip("\n") + "\n\n" + DL_01_28 + "\n"


def int13(s):
    if "Revision C6b audited" in s:
        return s
    assert s.count(INT13_OLD) == 1
    return s.replace(INT13_OLD, INT13_NEW)


def main():
    rw(os.path.join(APP, "decision-log.md"), add_00a)
    rw(os.path.join(FR, "DL-01.md"), add_01)
    rw(os.path.join(FR, "DL-INT.md"), int13)
    for c, row in ROW.items():
        p = os.path.join(FR, "trace-%s.md" % c)
        lines = open(p, encoding="utf-8").read().rstrip("\n").split("\n")
        if any(l.startswith("| BRIEF §6 |") for l in lines):
            continue
        last = max(i for i, l in enumerate(lines) if l.startswith("|"))
        lines.insert(last + 1, row)
        open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("DL-00A-33, DL-01-28, DL-INT-13 evidence and four BRIEF §6 trace rows in place")


if __name__ == "__main__":
    main()
