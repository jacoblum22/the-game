"""C6a-appendix.py -- DL-INT-13 and the BRIEF §6 trace rows for ch.04-07 (Revision C6a, ledger I-065).
Run: python rules/_process/basis/C6a-appendix.py  (idempotent), then integration-assemble-appendix.py."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.normpath(os.path.join(HERE, "..", "..", "appendix", "fragments"))

DL_INT_13 = """### DL-INT-13: Every rule card cites its basis at card level; a section-level basis does not suffice (I-065)
- Decision: [revision: I-065] BRIEF §6 and 00.1.6 are met card by card: every rule card (`**NN.S.R Title.**`) carries a basis tag of 00.1.6's forms, `[C:…]`, `[R…]` or `[DL-…]`, alone or in a compound group. A tag added after authoring is written `[<basis>; revision: I-065]` right after the card's kind tags. The basis is, in order of preference: the DL entry whose Decision names the card or its section; the constitution clause the chapter's traceability fragment maps the card to; the research row (digest entry or R5 completeness row) the chapter or its trace maps the section to. Where none exists, a DL entry is written in the chapter's fragment (Decision / Alternatives / Why) rather than a basis guessed. `basis_audit.py` defines a card and a tag; `validate_ruleset.py` BASIS WARNs on an untagged card in `BASIS_CHAPTERS`, a list extended chapter by chapter.
- Alternatives considered: accepting a section's intro or first-card DL plus the card's derivation cross-references as meeting §6 (the ledger's first proposal; rejected: an AI reading one card through `rq.py` sees no section intro, so the basis must travel with the card, and a derivation reference such as "(06.3.5)" names a dependency, not the reason); one tag per section heading (rejected: the same retrieval problem, and sections mix decisions); a basis field in a side table (rejected: drifts from the text it describes).
- Evidence: C6a script audit of ch.04-07 (342 rule cards): 188 carried no tag of their own (ch.04 21, ch.05 34, ch.06 77, ch.07 56; the constitution audit's 216 for ch.04-08 counted with a stricter one-line match). All 188 are tagged by `rules/_process/basis/C6a-04.py` ... `C6a-07.py`; two had no recorded basis and gained one: DL-05-41 (05.6.11's consumable Focus cap) and DL-06-30 (06.3.10's size ladder). 05.8.6's stale "until ch.04 agrees" sentence was corrected (04.8.4 had adopted the request).
- Serves: goal 2 (every rule's reason is one lookup away from the rule); BRIEF §6.
- Revisit if: the remaining chapters (00-03, 08-12, 15-16) turn up cards whose only honest basis is a derivation from another rule (then admit `[derived: NN.S.R]` as a fifth form in 00.1.6 rather than tag it with that rule's DL)."""

ROW = {
    "04": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 04 (65); 21 tagged at revision C6a; validator BASIS (DL-INT-13) | satisfied |",
    "05": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 05 (89); 34 tagged at revision C6a, 05.6.11 by the new DL-05-41; validator BASIS (DL-INT-13) | satisfied |",
    "06": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 06 (99); 77 tagged at revision C6a, 06.3.10 by the new DL-06-30; validator BASIS (DL-INT-13) | satisfied |",
    "07": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 07 (89); 56 tagged at revision C6a; validator BASIS (DL-INT-13) | satisfied |",
}

def main():
    p = os.path.join(FR, "DL-INT.md")
    s = open(p, encoding="utf-8").read()
    if "### DL-INT-13:" not in s:
        open(p, "w", encoding="utf-8").write(s.rstrip("\n") + "\n\n" + DL_INT_13 + "\n")
    for c, row in ROW.items():
        p = os.path.join(FR, "trace-%s.md" % c)
        lines = open(p, encoding="utf-8").read().rstrip("\n").split("\n")
        if any(l.startswith("| BRIEF §6 |") for l in lines):
            continue
        last = max(i for i, l in enumerate(lines) if l.startswith("|"))  # append to the fragment's table
        lines.insert(last + 1, row)
        open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("DL-INT-13 and four BRIEF §6 trace rows in place")

if __name__ == "__main__":
    main()
