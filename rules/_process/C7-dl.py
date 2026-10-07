"""C7-dl.py -- DL entries for revision C7's rows I-091 (ch.11), I-095, I-098, I-105 (idempotent).
Run: python rules/_process/C7-dl.py ; the orchestrator re-assembles the appendix."""
import os
FR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "appendix", "fragments")

NEW = {
"DL-04.md": [("### DL-04-33:", """### DL-04-33: The pacing targets assume a campaign mix with about half of a PC's fights chosen; nothing pushes the PC to keep pace (revision I-095)
- Decision: [revision: I-095] 04.3.5 and T-04-8 state that DL-00-05's assumed fight mix (easy 25 / fair 40 / hard 30 / lethal 5 %) is a **campaign** mix: it holds when about half of a PC's fights are chosen (a site's heart, a lair, a quarry: fair 50 / hard 40 / lethal 10, 10.13.10, 09.8.2) and half are the road's rolled encounters (trivial 34 / easy 27 / fair 35 / hard 4 / lethal 0, 09.12.3). 04.3.5 shows the three rows (assumed, half chosen, rolled only) and T-04-8 gains R15. A PC who fights only rolled encounters stalls, and that is intended: growth comes from seeking out danger. 12.7.4's pacing director is **not** given a duty to offer a chosen fight when the share falls; the rules guarantee only that one is always within reach (12.16.12's sites and lairs, 11.5.10's hook supply, 12.8.5's stuck answer). 02.11.1's "median session 4" carries the same caveat.
- Alternatives considered: make the rolled tables harsher to match the assumed mix (rejected: 09.8.1 rule 3 keeps the road fair or easier by design, DL-09-26, and a harsher road kills travelling PCs, not just slows them); retune 04's ladder to the rolled mix (rejected: a PC who seeks out danger would then race past the targets, tier 5 near session 30); a pacing-director rule that tracks the chosen share and pushes a lair or quarry when it falls (rejected: the director governs intensity, not growth, 12.7; pushing a PC toward fights to keep it on a growth schedule overrides the player's chosen play, which 12.9.2 forbids for every opportunity, and the existing opportunity and stuck-answer channels already put chosen fights in front of the player).
- Evidence: `rules/_process/simulation/09-word-mix-pacing.py` (200 seeds) and `09-word-mix-pacing-output.txt`: archer medians by tier, assumed mix 5 / 10 / 18 / 32 / 54 (reproduces 04.3.5's table), half chosen 6 / 13 / 21 / 34 / 58 (135 of 200 reach tier 5 within 60), rolled only 20 / 58 / never; swordsman 3 / 7 / 12 / 20 / 34, 3 / 8 / 13 / 21 / 36, 11 / 36 / 52 / never.
- Serves: goal 1 (a focused identity deepens at the intended pace for a PC who goes looking for trouble); C:P2 (power from what the character did); the sandbox (the player picks the pace).
- Revisit if: T-04-PACE logs show focused PCs choosing well under half of their fights and players reporting growth as stalled (then make the ratio visible in 14's player guidance first, and only then consider a director rule)."""),
              ("### DL-04-34:", """### DL-04-34: 04.3.4's "In fiction" column is staging guidance, not a requirement (revision I-098)
- Decision: [revision: I-098] 04.3.4: the "In fiction" column says how narration and the codex speak of a tier; a tier is confirmed by the other columns alone. Tier 4's "done in many countries" is the Contexts column (5 distinct kinds of opposition or obstacle, 04.3.1) in words, not a geographic gate; a one-region campaign reaches Exalted on the same deeds, and the fiction says "many countries" literally only where play has crossed into new regions (12.16.18).
- Alternatives considered: a region-count requirement at tier 4 (rejected: no 03.9 field counts regions, a gate on geography would block a campaign that stays home and is not what the tier measures); delete the column (rejected: the codex and the recognizer need the tier's in-world wording); reword the tier-4 cell (rejected: the phrase is the genre's, and the note removes the gate reading without losing it).
- Evidence: 04.3.1's field table: `contexts` = `detail(pc, key, since).distinct.contexts`, distinct kinds of opposition or obstacle; no field reads region. Revision C5b (I-084) recorded the FORK reading in a one-region seed.
- Serves: goal 2 (one reading of the ladder); goal 1 (a campaign that stays in its first region is not capped at tier 3).
- Revisit if: the codex or recognizer text in play ever cites geography as a missing requirement."""),
],
"DL-11.md": [("### DL-11-37:", """### DL-11-37: A patron's coin reward for a thread is 08.8.8's job fee for its band (revision I-091)
- Decision: [revision: I-091] 11.5.11: a completed thread's promised coin is 08.8.8's job fee for the thread's challenge band (`economy.yaml#job_fees`: 40 / 85 / 200 / 600 / 2,000), no longer "the patron's means at 08's wage scale". 11.5.12's (and `world_turn.yaml#thread_sources`') row "a faction's commission" cites the fee; T-11-4's `aid_pc` opportunity bang says a job pays the job fee of its band (mirrored in `factions.yaml` by `11-gen_factions.py`); the Friendly row's "jobs offered" cites it; the thread schema's `reward` comment names `job_fees` for coin.
- Alternatives considered: keep "the patron's means at 08's wage scale" (rejected: it names no table, so the DM would choose a number, INV-3, and 08.8.8 now prices exactly this); a fee per thread rank (troublesome … epic) instead of band (rejected: 08.8.8 keys fees by challenge band, 03.4.3, and two tables for one payment would disagree).
- Evidence: 08.8.8 and DL-08-36 (job fees by band, four weeks of that band's hire wage); 15.7.1 item 4 (a patron's job is offered at the fee, revision C6e). The `factions.yaml` diff is the one `aid_pc` line.
- Serves: goal 2 (one table prices a job wherever it comes from); C:I (no DM-chosen figure).
- Revisit if: DL-08-36's fees are retuned (this entry follows them)."""),
],
}
DL16_OLD = "Open: ledger I-105 (whether 16.6.2's departure clock starts for a tamed beast that joins at Wary); until it is settled, the Wary start is recorded as written."
DL16_NEW = ("[revision: I-105] Settled: 16.6.2's departure clock starts only when standing **steps down** to Wary from Neutral or warmer, never on joining at Wary. "
            "A tamed beast (or a hire whose reaction roll left it Wary) holds at Wary until regard lifts it to Neutral (a well-kept beast: B1 + B2, +2 a week on a 6-segment regard clock, so three weeks) or grievance drops it to Unfriendly (16.6.3). "
            "Rejected: starting tamed beasts at Neutral (a wild animal brought to hand would trust its keeper as a kennel-trained hound does, and the taming road would match buying); "
            "a longer departure clock for beasts (still wastes the project for a PC who cares for the beast, since regard cannot climb a rung in under three weeks). "
            "Revisit if: Wary allies that joined that way are reported as dead weight (then give them a regard bonus for the first week).")


def main():
    for f, ents in NEW.items():
        p = os.path.join(FR, f)
        s = open(p, encoding="utf-8").read()
        for head, body in ents:
            if head not in s:
                s = s.rstrip("\n") + "\n\n" + body + "\n"
        open(p, "w", encoding="utf-8", newline="\n").write(s)
    p = os.path.join(FR, "DL-16.md")
    s = open(p, encoding="utf-8").read()
    if DL16_NEW not in s:
        assert s.count(DL16_OLD) == 1
        s = s.replace(DL16_OLD, DL16_NEW)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("DL-04-33/34, DL-11-37, DL-16-25 (I-105) in place")


if __name__ == "__main__":
    main()
