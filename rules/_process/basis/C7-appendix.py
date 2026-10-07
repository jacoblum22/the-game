"""C7-appendix.py -- DL-11-35/36, the BRIEF §6 trace rows for ch.11 and 12, and DL-INT-13 brought up to date
(Revision C7, ledger I-065; closes the row). Run: python rules/_process/basis/C7-appendix.py (idempotent); the
orchestrator re-assembles the appendix."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.normpath(os.path.join(HERE, "..", "..", "appendix", "fragments"))

DL = [("### DL-11-35:", """### DL-11-35: A strike on a holding is an opposed faction check; improvements are a closed priced list (revision I-065)
- Decision: [revision: I-065] 11.9.5: a faction's strike on a PC's holding is 11.3.5's faction check against `10 + 2 × garrison + 2 × the PC's domain tier` (0 if none), +2 with walls; success ticks the holding's 6-segment damage clock +2, critical success +4; a full clock ruins the holding (repair: a project of half its build weeks) or, for a manor or keep and a faction whose `fields` could hold it, seizes it; a week of repair ticks the clock down 2. 11.9.6: improvements come from a closed list of nine (`world_turn.yaml#improvements`), each with a price, build weeks, an effect and a minimum holding; a holding below a manor carries at most three, a manor or keep six.
- Alternatives considered: holdings outside the faction economy, harmed only by situations (rejected: 11.3.8 already lets a Hostile faction `strike` the PC, and its holdings are where a strike lands); free-form improvements priced by the DM (rejected: C:V, and a DM figure is a number the DM chose, INV-3); an improvement per building kind with no cap (rejected: a cottage would end up a fortress).
- Evidence: the DC is DL-11-03's opposed DC (`10 + defender rating + 2 × defender tier`) with the holding's garrison (0–3) as the defender's rating and the PC's domain tier as its tier, so a walled, garrisoned holding of a ruling PC defends like a faction of that size; the 6-segment damage clock is a 00 clock size (DL-00A-20). The improvement prices (150 to 1,000) and build weeks (4 to 10) sit inside 08's holding prices (`economy.yaml#holdings`: cottage 150 … keep 25,000), so an improvement never costs more than a mid-sized holding. The tick sizes (+2 / +4, repair −2), the prices, the build weeks and the 3 / 6 caps are defaults, not measured values; no simulation set them. The cards carried no basis of their own until revision C7's audit (I-065).
- Serves: goal 1 (what the PC builds can be struck and defended); goal 2 (one check and one closed list); C:V.
- Revisit if: `11-world-sim.py` or play shows Hostile factions ruining a defended holding more often than once a year, or the market charter's doubled yield outrunning 08's anti-inflation targets."""),
      ("### DL-11-36:", """### DL-11-36: Festivals carry effects from a closed list of six (revision I-065)
- Decision: [revision: I-065] 11.10.4: a festival is `{id, name, season, week, day, effects}` in `calendar.yaml`, its effects from a closed list: market (find-buyer clocks +1, one haggling notch waived that week), sitting (ranks conferred, 11.8.3), rumor surge (circulating rumors drawn at weight 3; Carouse yields one more), truce (faction strikes in its scope read as `goal`), rite day (a named school's rituals one scale lower in cost) and hiring fair (one more recruiting candidate). The four quarter days are festivals with market and sitting unless the region's seed says otherwise.
- Alternatives considered: festivals as flavor only (rejected: a calendar that changes nothing is not read, and R5 TM-07 names festivals as a timekeeping duty); festival effects written per setting (rejected: C:V; each chapter that reads a festival would need to parse free text).
- Evidence: each effect is a one-notch shift on a rule another chapter already owns (08/15 haggling and find-buyer clocks, 11.8.3 sittings, 11.6 rumor draws, 11.3.6 strikes, 05's ritual cost scale, 16's recruiting), so a festival adds no new mechanic. The quarter-day pair follows DL-11-21 (a quarter day opens each season) and DL-11-18 (ranks at sittings, default the season's first week). The sizes (+1 tick, one notch, weight 3, one more) are defaults, not measured values; no simulation set them. The card carried no basis of its own until revision C7's audit (I-065).
- Serves: goal 2 (dates are computable and do something); C:V.
- Revisit if: a festival effect proves to be the cheapest way to an outcome (players plan every sale or recruitment around one)."""),
      ]

ROWS = {
    "trace-11.md": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 11 (113); 38 tagged at revision C7, 11.9.5 and 11.9.6 by the new DL-11-35, 11.10.4 by the new DL-11-36; validator BASIS (DL-INT-13) | satisfied |",
    "trace-12.md": "| BRIEF §6 | Every rule cites its basis (`[C:]`, `[R]` or `[DL-]`) at card level | every rule card of 12 (136); 67 tagged at revision C7; validator BASIS (DL-INT-13) | satisfied |",
}

EV_OLD = "Again no card's only honest basis was a derivation. No card's only honest basis was a derivation, so the revisit clause's fifth form was not needed."
EV_NEW = ("Revision C6d audited ch.15-16 (205 rule cards): 130 carried no tag of their own (ch.15 57, ch.16 73); all are tagged by "
          "`rules/_process/basis/C6d-15.py` and `C6d-16.py`, and DL-16-25 and DL-16-26 were written for cards with no recorded basis. "
          "Revision C6e audited ch.08 (82 rule cards): 46 untagged, all tagged by `C6e-08.py`; DL-08-39..41 written. "
          "Revision C7 audited ch.11-12 (249 rule cards): 105 untagged (ch.11 38, ch.12 67), all tagged by `C7-11.py` and `C7-12.py`; "
          "DL-11-35 (11.9.5 strikes on holdings, 11.9.6 improvements) and DL-11-36 (11.10.4 festivals) written. "
          "With that, `BASIS_CHAPTERS` holds 00-12 and 15-16, every chapter the audit covered (ch.13 is an unmaintained optional setting and stays out; ch.14, the player's guide, was outside the audit) "
          "and the validator reports 0 untagged cards. No card's only honest basis was a derivation, so the revisit clause's fifth form was not needed. [revision: I-065, C7]")
RV_OLD = "- Revisit if: the remaining chapters (00-03, 08-12, 15-16) turn up cards whose only honest basis is a derivation from another rule (then admit `[derived: NN.S.R]` as a fifth form in 00.1.6 rather than tag it with that rule's DL)."
RV_NEW = ("- Revisit if: a new rule card's only honest basis is a derivation from another rule (then admit `[derived: NN.S.R]` as a fifth form in 00.1.6 rather "
          "than tag it with that rule's DL); or ch.13 returns to maintenance, or ch.14 gains rule cards (then audit the chapter with `basis_audit.py NN` and add it to `BASIS_CHAPTERS`). "
          "New cards in any listed chapter are held to the rule by the validator. [revision: I-065, C7]")


def main():
    p = os.path.join(FR, "DL-11.md")
    s = open(p, encoding="utf-8").read()
    for head, body in DL:
        if head not in s:
            s = s.rstrip("\n") + "\n\n" + body + "\n"
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    for f, row in ROWS.items():
        p = os.path.join(FR, f)
        lines = open(p, encoding="utf-8").read().rstrip("\n").split("\n")
        if not any(l.startswith("| BRIEF §6 |") for l in lines):
            last = max(i for i, l in enumerate(lines) if l.startswith("|"))
            lines.insert(last + 1, row)
            open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    p = os.path.join(FR, "DL-INT.md")
    s = open(p, encoding="utf-8").read()
    for old, new in ((EV_OLD, EV_NEW), (RV_OLD, RV_NEW)):
        if new not in s:
            assert s.count(old) == 1, old[:60]
            s = s.replace(old, new)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("DL-11-35/36, BRIEF §6 rows for 11 and 12, DL-INT-13 updated")


if __name__ == "__main__":
    main()
