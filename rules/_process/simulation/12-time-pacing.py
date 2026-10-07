"""I-085: world time against play time. Seeded (seed 85). Python 3 + stdlib (imports 04-recog04.py).
Joins 04-recog04.py's per-seed session at each tier (200 seeds x 60 sessions, archer and swordsman) to a
world-time schedule, and checks the schedule against 11-world-sim.py's weekly throughput.

Reference schedule (pacing.yaml#world_time, 12.5.5):
  an ADVENTURE is 2-4 sessions (uniform); each adventure session spends 2-10 world days (triangular, mode 5:
    a journey of a few days, a site, a town scene: 10's journey legs and 15's scene lengths);
  after each adventure the player takes DOWNTIME of 1-6 weeks (uniform; training, recovery, projects: 15.10);
  optionally one LONG DOWNTIME of a season (13 weeks) a year (a winter, 15.10), policy 'winters'.
Aging (11.10.5, calendar.yaml#lifespans): checks begin at the people's aging age; age +1 a Year Turn (52 weeks).
11-world-sim.py (engaged, 300 seeds x 104 weeks): threads completed median 19 per 104 weeks."""
import importlib.util, os, random, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("recog04", os.path.join(HERE, "04-recog04.py"))
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
THREADS_PER_WEEK = 19 / 104.0          # 11-world-sim-output.txt, engaged: threads_completed median
AGING = {"human": 50, "halfling": 50, "orc": 35, "dwarf": 120, "elf": 300}
START = {"young": 18, "grown": 30, "old": 55}

def schedule(rng, sessions, winters):
    """world week (float) at the END of each session 1..sessions"""
    t, out, s, wintered = 0.0, [], 0, set()
    while s < sessions:
        for _ in range(rng.randint(2, 4)):
            if s >= sessions:
                break
            t += rng.triangular(2, 10, 5) / 7.0; s += 1; out.append(t)
        t += rng.uniform(1, 6)
        y = int(t // 52)
        if winters and (t % 52) >= 39 and y not in wintered:   # the first downtime in a year's last quarter
            wintered.add(y); t += 13
    return out

def main():
    print(__doc__.splitlines()[0])
    rng = random.Random(85)
    tiers = {}
    for name, style, key, mk in (("archer", R.ARCHER, "deed.martial.archery", None), ("swordsman", R.PURE, "deed.martial.blade", R.CH_SWORD)):
        res, _, _ = R.tiers_of(style, [key], mk=mk)
        tiers[name] = res
        print("%-9s tier sessions (median of reached): %s" % (name, " ".join("T%d %s" % (t, st.median([x for x in res[t] if x < 99]) if any(x < 99 for x in res[t]) else "-") for t in range(1, 6))))
    for winters in (False, True):
        print("\npolicy: %s" % ("one season-long downtime a year (winters)" if winters else "no long downtime"))
        wps = []
        for name, res in tiers.items():
            yrs = {t: [] for t in range(1, 6)}
            for i in range(len(res[1])):
                sch = schedule(rng, 60, winters)
                wps.append(sch[-1] / 60.0)
                for t in range(1, 6):
                    if res[t][i] < 99: yrs[t].append(sch[res[t][i] - 1] / 52.0)
            print("  %-9s world years at tier (p10/median/p90): %s" % (name, "  ".join("T%d %.1f/%.1f/%.1f" % (t, *[sorted(v)[int(q * (len(v) - 1))] for q in (0.1, 0.5, 0.9)]) if v else "T%d -" % t for t, v in yrs.items())))
        m = st.median(wps)
        print("  weeks per session: median %.2f (p10 %.2f, p90 %.2f); seasons per 10 sessions %.1f" % (m, sorted(wps)[len(wps) // 10], sorted(wps)[9 * len(wps) // 10], 10 * m / 13))
        print("  join with 11-world-sim: threads completed per session %.2f -> %.1f sessions a thread (adventure model: 2-4)" % (m * THREADS_PER_WEEK, 1 / (m * THREADS_PER_WEEK)))
        years60 = 60 * m / 52
        print("  60 sessions = %.1f world years; aging checks met within 60 sessions by start age and people:" % years60)
        for pe, ag in AGING.items():
            row = []
            for band, a0 in START.items():
                n = max(0, int(a0 + years60) - max(ag, a0) + (1 if a0 >= ag else 0)) if a0 + years60 >= ag else 0
                row.append("%s %d" % (band, n))
            print("    %-8s (aging at %3d): %s" % (pe, ag, ", ".join(row)))

if __name__ == "__main__":
    main()
