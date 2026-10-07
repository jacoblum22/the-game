"""I-038: free-Oracle lever fishing, before and after the 01.15.8 limits. Seeded.
Model: a scene of R rolls; before each roll the player asks up to Q free G0 questions at LIKELY (75% yes,
T-01-10) until it has the levers it may use. Each yes is a citable fact (+2 Precision).
OLD: two levers per roll (00.3.9b), no other limit.  NEW (01.15.8): one free-fact lever per roll, free-fact
levers on at most CAP rolls per character per scene, odds unchanged (01.15.2).
Reports the mean free-fact roll bonus per roll and the d20 success swing it buys at a 50% base roll."""
import random
P_YES = 0.75
def scene(rng, R, Q, rule, cap=2):
    bonus = []; rolls_used = 0
    for _ in range(R):
        want = 2 if rule == "old" else (1 if rolls_used < cap else 0)
        got = 0; asked = 0
        while got < want and asked < Q:
            asked += 1
            if rng.random() < P_YES: got += 1
        if rule == "new" and got: rolls_used += 1
        bonus.append(2 * got)
    return bonus
def main():
    rng = random.Random(38)
    N = 20000
    print("I-038 oracle fishing sim, seed 38, N=%d scenes per cell" % N)
    print("R=rolls/scene Q=free questions/roll | mean free bonus per roll: OLD  NEW(cap1) NEW(cap2) NEW(cap3)")
    for R in (3, 5, 8):
        for Q in (1, 3, 6):
            row = []
            for rule, cap in (("old", 0), ("new", 1), ("new", 2), ("new", 3)):
                tot = sum(sum(scene(rng, R, Q, rule, cap)) for _ in range(N))
                row.append(tot / (N * R))
            print("R=%d Q=%d | %.2f  %.2f  %.2f  %.2f" % (R, Q, *row))
    print("A +1 is 5 points of d20 success; OLD at Q>=3 is ~+3.8 per roll (~19 points) on every roll.")
main()
