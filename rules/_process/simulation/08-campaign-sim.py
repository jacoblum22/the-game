"""08-campaign-sim.py -- I-018 (OEQ-08-2, OEQ-08-4): a seeded campaign wealth and power simulation.

Runs whole campaigns of 70 sessions through bands P1-P5 with chapter 08's drop rules exactly as the loot generator
implements them (08-loot-sim.py's PR-08-1 code, imported, on the real bestiary of data/archetypes.yaml), and measures,
per power band, what 08.2.7 (item density) and 08.8.10 (the treasure curve) assume.

Model (every number from the rules or stated here as an assumption):
- Band pacing (04's tiers at sessions ~4/9/19/34/56, 08.2.7): P1 sessions 1-9, P2 10-19, P3 20-34, P4 35-56,
  P5 57-70.
- Two fights a session (08.2.7, 08.8.10). Each fight is a roll on a generic encounter table (travel.yaml, a terrain
  drawn uniformly, the threat sub-table at home band = the PC's band, d20 faces as written): the row's archetype at its
  relative band (home-1 / home / home+1, clamped 1-5), with its yield and purse from archetypes.yaml, so the mix of
  beasts that drop nothing, folk with purses and principals that always drop is the tables' own.
- Loot (08.3.3): yield trophy rolls d100 against gen_loot.yaml#drop_check; always drops; a hoard-keeper met on the
  road (the encounter tables are travel) drops as a trophy, and its hoard is found in its lair (08.3.12), one of the
  site treasures below. Circumstance decisive 45% / costly 20% / merciful 10% /
  scavenged 25%, degrees as 08-loot-sim.py (critical 20% on a kill).
- Site treasure: one hoard per ~4 sessions (08.8.10's derivation), at the PC's band.
- Coin (08.8.10): purses for archetypes with `purse: band`, one to three carriers a fight (mean 2), economy.yaml#purses
  at the foe's band; hoard coin economy.yaml#hoard_coin for every hoard. Goods are not counted (a lower bound).
- Keeping and selling: the PC keeps the five best property items attuned (most properties, then highest tier) and
  four spares; the rest are sold at half list (08.8.4) through clk.find_buyer, one sale every 3 sessions (town:
  1 tick a week + a Talk beat's reach of about 1 on a 6-segment clock), capped by a town's market depth (150 a week).
- Spending: one week of lifestyle per session: comfortable (14) at P1-P3, wealthy (35) at P4, half wealthy half
  noble (68) at P5. Training fees, commissions, materials, holdings and wages are not spent (an upper bound on coin).
Usage: python 08-campaign-sim.py [campaigns]   (default 300; seeded; output 08-campaign-sim-output.txt)
"""
import os, sys, random, statistics, collections, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "08-loot-sim.py"), encoding="utf-8").read()
_src = _src.split("# ---------------------------------------------------------------- the 1,000-drop run")[0]
G = {"__file__": os.path.join(HERE, "08-loot-sim.py"), "__name__": "loot08"}
exec(compile(_src, "08-loot-sim.py (generator part)", "exec"), G)
Gen, L, BI, LOOT = G["Gen"], G["L"], G["BI"], G["LOOT"]
ECON = L("economy.yaml")
PVAL = {int(k): v for k, v in ECON["property_value_by_tier"].items()}
QMULT = {"worn": 0.5, "common": 1, "fine": 3, "masterwork": 10, "wondrous": 30}
YIELD = LOOT["drop_check"]["yield"]["trophy"]
HOARD = {int(k[1]): v for k, v in LOOT["hoard_map"].items() if k.startswith("T")}

CAMPAIGNS = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 300
SESSIONS = 70
BAND_OF = lambda s: 1 if s <= 9 else (2 if s <= 19 else (3 if s <= 34 else (4 if s <= 56 else 5)))
LIFESTYLE = {1: 14, 2: 14, 3: 14, 4: 35, 5: 68}
TABLE_ITEMS = {1: (2, 4), 2: (4, 6), 3: (8, 12), 4: (15, 25), 5: (25, None)}   # 08.2.7 property items won (typical)
TABLE_TIER = {1: "W1-W2", 2: "W2", 3: "W3", 4: "W4", 5: "W5"}                   # 08.8.10 typical tier
WT = [(50, "W1"), (300, "W2"), (1500, "W3"), (8000, "W4"), (10 ** 12, "W5")]

ARCHS = []
for x in L("archetypes.yaml")["archetypes"]:
    ARCHS.append(dict(id=x["id"], tags=list(x["creature_tags"]), harm=list(x["harm_tags"]), gear=list(x.get("gear") or []),
                      trophy=x["loot"]["trophy_base"], deeds=list(x.get("evidence_tags") or []), orgs=list(x.get("org_tags") or []),
                      yld=x["loot"]["yield"], purse=x.get("purse"), lo=x["bands"][0], hi=x["bands"][1]))
BY_BAND = {b: [a for a in ARCHS if a["lo"] <= b <= a["hi"]] for b in range(1, 6)}
BY_ID = {a["id"]: a for a in ARCHS}
TABLES = L("travel.yaml")["encounter_tables"]

def roll_fight(rng, home):
    tb = rng.choice(TABLES)["threat_by_home"][home]
    d = rng.randint(1, 20)
    for row in tb:
        lo, _, hi = row["range"].partition("-")
        if int(lo) <= d <= int(hi or lo):
            break
    off = {"home-1": -1, "home": 0, "home+1": 1}[row["band"]]
    ref = row["ref"][0]
    cnt = row["count"]
    carriers = 1 if cnt in ("1", "group") else min(3, int(str(cnt).split("-")[0]))
    return BY_ID[ref], min(5, max(1, home + off)), carriers

def dice(expr, rng):
    """'3d6 x 3', '4d6 + 5', '1d4 - 1', '2d6'"""
    e = expr.replace(" ", "")
    mult = 1
    if "x" in e:
        e, m = e.split("x"); mult = int(m)
    add = 0
    for sign in ("+", "-"):
        if sign in e:
            e, a = e.split(sign); add = int(a) * (1 if sign == "+" else -1)
    n, d = e.split("d"); n = int(n or 1)
    return max(0, (sum(rng.randint(1, int(d)) for _ in range(n)) + add) * mult)

PURSE = {p["band"]: p["coin"] for p in ECON["purses"]}
HCOIN = {h["band"]: h["coin"] for h in ECON["hoard_coin"]}

def circumstance(rng):
    r = rng.random()
    return "decisive" if r < 0.45 else ("costly" if r < 0.65 else ("merciful" if r < 0.75 else "scavenged"))

def degree_for(rng, circ):
    if circ == "scavenged":
        r = rng.random()
        return "critical_success" if r < 0.05 else ("success" if r < 0.55 else ("failure" if r < 0.95 else "critical_failure"))
    return "critical_success" if rng.random() < 0.2 else "success"

def list_price(it):
    base = BI[it["base"]]["price"]
    return int(base * QMULT[it["rung"]]) + sum(PVAL.get(min(5, t), 750) for _, t, _, _ in it["props"])

def value_key(it):
    return (len(it["props"]), max([t for _, t, _, _ in it["props"]] or [0]), list_price(it))

def campaign(seed):
    rng = random.Random(seed)
    gen = Gen(zlib.crc32(("campaign%d" % seed).encode()) % 100000)
    coin, owned, sale_wait = 0, [], 0
    out = {b: collections.Counter() for b in range(1, 6)}
    for s in range(1, SESSIONS + 1):
        band = BAND_OF(s)
        o = out[band]
        o["sessions"] += 1
        won = []
        for _ in range(2):
            src, fb, carriers = roll_fight(rng, band)
            a = dict(src); a["band"] = fb
            o["fights_" + a["yld"]] += 1
            if a["purse"] == "band":
                coin += sum(dice(PURSE[fb], rng) for _ in range(carriers))
            if a["yld"] == "none":
                continue
            # 08.3.12 [revision: I-018]: a hoard-keeper met away from its lair drops as a trophy; its hoard waits in the
            # lair, which is a site and is counted among the site treasures below
            if a["yld"] in ("trophy", "hoard") and rng.randint(1, 100) > YIELD["T%d" % fb]:
                continue
            circ = circumstance(rng)
            deg = degree_for(rng, circ)
            if circ == "merciful" and a["tags"][0].startswith(("creature.undead.mindless", "creature.construct", "creature.horror.ooze")):
                circ = "decisive"
            won.append(gen.generate(a, circ, deg, [])); won[-1]["src"] = "fight (%s)" % a["yld"]
        if rng.random() < 0.25:                      # a site's treasure (08.3.12) about one session in four
            a = dict(rng.choice(BY_BAND[band])); a["band"] = band
            coin += dice(HCOIN[band], rng); o["hoards"] += 1
            for row in HOARD[band]:
                for _ in range(row["count"]):
                    won.append(gen.generate(a, "scavenged", "success", [], force_rung=row["rung"])); won[-1]["src"] = "site treasure"
        for it in won:
            if not it["props"]:
                o["no_property_items"] += 1
                continue
            o["property_items"] += 1
            o["src " + it["src"]] += 1
            o["rung_" + it["rung"]] += 1
            if it["bound"]:
                o["bound_power_items"] += 1
            if it["relic"]:
                o["relics"] += 1
            owned.append(it)
        owned.sort(key=value_key, reverse=True)
        keep, surplus = owned[:9], owned[9:]
        sale_wait += 1
        if surplus and sale_wait >= 3:
            sold = surplus.pop(0); sale_wait = 0
            coin += min(list_price(sold) // 2, 150 * 3); o["sales"] += 1
        owned = keep + surplus
        coin = max(0, coin - LIFESTYLE[band])
        attuned = owned[:5]
        o["end_coin"] = coin
        o["attuned"] = len(attuned)
        o["bound_attuned"] = min(4, sum(1 for i in attuned if i["bound"]))
        o["top_sig_tier"] = max([t for i in attuned for _, t, sl, _ in i["props"] if sl == "signature"] or [0])
        o["wondrous_attuned"] = sum(1 for i in attuned if i["rung"] == "wondrous")
    return out

def q(xs):
    xs = sorted(xs); n = len(xs)
    return "%s / %s / %s" % (xs[n // 10], statistics.median(xs), xs[(9 * n) // 10])

def tier(c):
    return next(t for lim, t in WT if c <= lim)

if __name__ == "__main__":
    runs = [campaign(1800 + i) for i in range(CAMPAIGNS)]
    lines = []
    P = lambda *a: (lines.append(" ".join(str(x) for x in a)), print(" ".join(str(x) for x in a)))
    P("=== ch.08 campaign wealth and power simulation (I-018; %d campaigns x %d sessions; seeded) ===" % (CAMPAIGNS, SESSIONS))
    P("p10 / median / p90 per campaign, per band (P1 s1-9, P2 s10-19, P3 s20-34, P4 s35-56, P5 s57-70)")
    P("band | property items won in band (08.2.7 typical) | per session | masterwork / wondrous / fine | bound-power items won | attuned at band end | bound attuned | top signature tier | coin at band end -> tier (08.8.10 typical)")
    verdict = []
    for b in range(1, 6):
        it = [r[b]["property_items"] for r in runs]
        ps = [r[b]["property_items"] / r[b]["sessions"] for r in runs]
        mw = statistics.mean(r[b]["rung_masterwork"] for r in runs); wd = statistics.mean(r[b]["rung_wondrous"] for r in runs)
        fi = statistics.mean(r[b]["rung_fine"] for r in runs)
        bp = [r[b]["bound_power_items"] for r in runs]
        coin = [r[b]["end_coin"] for r in runs]
        tiers = collections.Counter(tier(c) for c in coin)
        lo, hi = TABLE_ITEMS[b]
        P("P%d | %s (%s) | %.2f | %.1f / %.1f / %.1f | %s | %s | %s | %s | %s -> %s (%s)" % (
            b, q(it), "%d-%s" % (lo, hi if hi else "+"), statistics.mean(ps), mw, wd, fi, q(bp),
            q([r[b]["attuned"] for r in runs]), q([r[b]["bound_attuned"] for r in runs]), q([r[b]["top_sig_tier"] for r in runs]),
            q(coin), tier(statistics.median(coin)), TABLE_TIER[b]))
        srcs = sorted({k for r in runs for k in r[b] if k.startswith("src ")})
        P("     property items by source (mean): " + ", ".join("%s %.1f" % (k[4:], statistics.mean(r[b][k] for r in runs)) for k in srcs))
        P("     fights by yield (mean): " + ", ".join("%s %.1f" % (k[7:], statistics.mean(r[b][k] for r in runs)) for k in sorted({k for r in runs for k in r[b] if k.startswith("fights_")})))
        P("     wealth tiers at band end: %s" % ", ".join("%s %.0f%%" % (t, 100.0 * tiers[t] / CAMPAIGNS) for t in ("W1", "W2", "W3", "W4", "W5")))
        med = statistics.median(it)
        row = max([k for k, (lo_k, _) in TABLE_ITEMS.items() if med >= lo_k] or [1])   # the highest row the median reaches
        verdict.append((b, med, lo, hi, row - b))
    P()
    P("08.2.7 check (VI revisit trigger: density more than one row ahead of the table):")
    for b, med, lo, hi, ahead in verdict:
        state = "within its row" if med >= lo and (hi is None or med <= hi) else (
            "MORE THAN ONE ROW AHEAD" if ahead >= 2 else ("one row ahead" if ahead == 1 else ("above its row, short of the next" if med > (hi or 1e9) else "below its row")))
        P("  P%d median %s items vs typical %d-%s: %s" % (b, med, lo, hi if hi else "+", state))
    allr = collections.Counter()
    for r in runs:
        for b in range(1, 6):
            for k in ("rung_masterwork", "rung_wondrous", "rung_fine"):
                allr[k] += r[b][k]
    n = sum(allr.values())
    P("rungs of property items over the campaign: masterwork %.0f%%, wondrous %.0f%%, fine %.0f%%" % tuple(100.0 * allr[k] / n for k in ("rung_masterwork", "rung_wondrous", "rung_fine")))
    with open(os.path.join(HERE, "08-campaign-sim-output.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
