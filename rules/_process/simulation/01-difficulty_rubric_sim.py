"""I-158 (with I-143, I-155, P-024, P-051, P-107, P-117): difficulty rubric sim, lane D §5 [revision: R2-C].

Seeded with random.Random(158). Odds are exhaustive d20 enumerations through the engine's degree rule
(engine/resolve/odds.py and roll.degree: the T-01-3 enumerator, 01.8.1), so the numbers are the OFFER's.
Obstacle classes and tiers are read from rules/data/basic_verbs.yaml (anchor.obstacle_classes) and
rules/data/resolution.yaml (dc_tiers, read_costs).

Variants (D §3):
  as_played  today's tie-breaks: tier up when between two rungs; every hindering fact a -2 snag (two-snag, +-4
             caps); any observer present makes the beat costly and Risky; social beats framed on a tier, not
             15.3.3; fights framed Moderate for every approach (P-117).
  A          guardrails: one cited Precision snag, a further hindering fact a Protective snag (stakes +1);
             everyday acts take the lower of two rungs; an observer counts only if they would act on a failure;
             social beats use 15.3.3 (Neutral R1 certain); trivial or not-costly beats do not roll; the
             critical-failure guard (01.6.13). Fights unchanged (A leaves P-117 alone).
  B          A + rubric: tier = the class base + a nudge (-1/0/+1) that needs a cited intrinsic fact; class
             `other` falls back to A; fights use the defense formula per approach.
  C          Blades-style: every unopposed roll is against Easy (10); hindering facts and obstacle quality
             (Moderate and up) raise stakes instead. No critical-failure widening (kept 01.8.1).
PCs: modifier at the attribute the act uses: off-attribute -1, untrained 0, average +2 (CT-1), P1 specialist
  +5 (CT-2), P3 +9 (CT-3) (00.3.17's calibration PCs). Lane D's draft used +3/+7; 00.3.17 is canonical.
Model-error injection: tier +-1 (p 0.2), an extra hindering snag (q 0.2), stakes one rung high (r 0.15). Under
  B a tier error is a wrong nudge: possible only when an intrinsic fact is citable, and never beyond base +-1.
"""
import functools
import os
import random
import statistics
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
from engine.resolve.odds import odds  # noqa: E402  exhaustive d20, 01.8.1
from engine.resolve.roll import degree  # noqa: E402

DATA = os.path.join(ROOT, "rules", "data")
RES = yaml.safe_load(open(os.path.join(DATA, "resolution.yaml"), encoding="utf-8"))
BV = yaml.safe_load(open(os.path.join(DATA, "basic_verbs.yaml"), encoding="utf-8"))
TIERS = ["trivial", "easy", "moderate", "hard", "very_hard", "legendary"]
DC = {t["id"]: t["dc"] for t in RES["dc_tiers"]}
CLASS_BASE = {(v["id"].split(".")[1], c["id"]): c["base"] for v in BV["verbs"]
              for c in v["anchor"].get("obstacle_classes", [])}
STAKES = ["safe", "risky", "dire"]
SEV = {(r["stakes"], r["degree"]): int(r["severities"][0][1]) if r["severities"] else 0 for r in RES["read_costs"]}
HAZ_TIER = {1: "easy", 2: "moderate", 3: "hard", 4: "very_hard", 5: "legendary"}  # 00.3.8 effect DC by severity
PCS = [("off-attr", -1), ("untrained", 0), ("average", 2), ("P1", 5), ("P3", 9)]
VARIANTS = ["as_played", "A", "B", "C"]
P_TIER, Q_SNAG, R_STAKES = 0.2, 0.2, 0.15
SEED = 158


def R(label, verb, cls, **k):
    """One act. cls: an obstacle class id of the verb, or 'other' (then `tier` is the honest rung).
    between: the as-played Framer saw two rungs and took the higher. nudge/intr: B's nudge and whether an
    intrinsic fact is citable. hind: situational hindering facts. src: stakes sources other than an observer.
    obs: none | passive (present, would not act on a failure) | acts. costly: failure costs something anyway.
    opp: an opposed defense. social: a 15.3.3 DC, or 'certain'. ap: the as-played tier when logged."""
    r = dict(label=label, verb=verb, cls=cls, between=False, nudge=0, intr=False, hind=0, src=(), heavy=False,
             obs="none", costly=False, opp=None, social=None, secret=False, every=False, anchor=False, haz=None,
             tier=None, ap=None)
    r.update(k)
    if cls == "other":
        base = r["tier"]
    else:
        base = CLASS_BASE[(verb, cls)]
        if base == "by_hazard":
            base = HAZ_TIER[r["haz"]]
    r["base"] = base
    if r["ap"] is None:
        r["ap"] = TIERS[min(5, TIERS.index(base) + 1)] if r["between"] else base
    return r


E = dict(every=True)
A_ = dict(anchor=True)
ACTS = [
    # everyday acts (T-00-5's new everyday rows and the logged playtest cases)
    R("walk a dry road at noon", "move", "open_ground", **E, **A_),
    R("push through the market crowd (I-158)", "move", "crowd", ap="moderate", hind=2, obs="passive", costly=True, **E),
    R("slip through the crowd toward the gate", "move", "crowd", between=True, hind=1, obs="passive", costly=True, **E),
    R("find a seat in a packed inn", "move", "crowd", between=True, obs="passive", **E),
    R("cross a muddy field", "move", "rough_ground", between=True, **E),
    R("push through a thicket at leisure (P-051)", "move", "rough_ground", ap="moderate", hind=1, **E),
    R("push through a thicket, pursued", "move", "rough_ground", between=True, hind=1, src=("clock",), **E),
    R("open an unbarred wicket, gatekeeper watching (P-024)", "handle", "ordinary_use", ap="easy", obs="passive", **E),
    R("open an unlocked door", "handle", "ordinary_use", **E, **A_),
    R("light a lamp in the dark", "handle", "ordinary_use", **E),
    R("lift a sticking latch by a sleeper", "handle", "awkward", between=True, obs="acts", **E),
    R("mend a torn strap before the ride", "handle", "awkward", **E),
    R("carry a sack of grain to the cart", "exert", "ordinary_effort", between=True, **E),
    R("carry a wounded friend out of the smoke", "exert", "ordinary_effort", between=True, hind=1, src=("hazard", "clock"), **E),
    R("climb a rough stone wall, patrol due", "exert", "ordinary_effort", src=("clock",), **E, **A_),
    R("climb a knotted rope with handholds", "exert", "easy_holds", **E, **A_),
    R("haul a cart out of a rut before the rain", "exert", "ordinary_effort", between=True, hind=1, src=("clock",), **E),
    R("jump a narrow stream", "exert", "ordinary_effort", **E),
    R("ask a stranger the way (first question, P-107)", "talk", "other", tier="moderate", ap="moderate", hind=1, social="certain", src=("goodwill",), **E),
    R("ask the ferryman a small favour (Neutral R2)", "talk", "other", tier="moderate", ap="moderate", social=12, src=("goodwill",), **E),
    R("ask a wary guard to let you wait inside (Wary R1)", "talk", "other", tier="moderate", ap="moderate", social=11, src=("goodwill",), **E),
    R("tell a neutral clerk a small lie about your errand", "talk", "other", tier="moderate", ap="moderate", social=12, src=("goodwill",), **E),
    R("shout to travellers on the road (P-024)", "talk", "be_heard", ap="moderate", hind=1, costly=True, **E),
    R("read a posted notice in a known tongue (P-110)", "observe", "in_plain_view", **E),
    R("listen at a door for voices", "observe", "careless_concealment", **E),
    R("recall your village's saint's day", "recall", "own_knowledge", **E),
    R("recall a widely known legend, herald listening", "recall", "widely_known", between=True, obs="acts", **E),
    R("spot a carelessly hidden coin purse", "observe", "careless_concealment", costly=True, **E, **A_),
    R("calm a familiar nervous horse", "handle", "other", tier="easy", opp=10, src=("item",), **E, **A_),
    R("shove past a drunk blocking the alley", "move", "other", tier="easy", opp=11, obs="acts", **E),
    R("balance along a plank over a ditch", "exert", "ordinary_effort", **E),
    R("bargain with a friendly merchant (Friendly R2)", "talk", "other", tier="moderate", ap="moderate", social="certain", src=("goodwill",), **E),
    # T-00-5 / T-01-2 anchor rows
    R("follow a clear trail across hard ground", "observe", "clear_trail", src=("clock",), **A_),
    R("force an iron hasp in old oak, keep guarded", "force", "sound_fitting", obs="acts", src=("item",), **A_),
    R("talk a neutral T2 guard into bending a small rule (R3)", "talk", "other", tier="moderate", ap="moderate", social=16, src=("goodwill",), **A_),
    R("pick a guild-made lock (licensed)", "handle", "other", tier="hard", src=("clock",), **A_),
    R("leap a 12-ft gap from a running start", "exert", "gap_leap", src=("height",), heavy=True, **A_),
    R("cut a hanging rope with an arrow at 60 ft", "strike", "tiny_and_far", src=("clock",), **A_),
    R("track a ranger over rock in rain", "observe", "faint_trail", src=("clock",), **A_),
    R("forge a noble's seal to pass a clerk (licensed)", "handle", "other", tier="very_hard", src=("item",), **A_),
    R("swim a flooded river in spate, clothed", "exert", "extreme", src=("hazard",), heavy=True, **A_),
    R("hold a collapsing gate alone for a minute", "exert", "limit", src=("hazard",), heavy=True, **A_),
    R("climb the smooth inside of a well shaft", "exert", "limit", src=("height",), heavy=True, **A_),
    # the rest of the field
    R("sneak past a sleepy guard", "sneak", "other", tier="easy", opp=10, obs="acts"),
    R("sneak past the ogre", "sneak", "other", tier="moderate", opp=12, obs="acts", heavy=True),
    R("search a desk for a hidden drawer, owner due", "observe", "deliberate_concealment", src=("clock",), secret=True),
    R("find a smuggler's compartment", "observe", "expert_concealment", src=("clock",), secret=True, between=True),
    R("find a hidden catch in a vault at leisure (I-143)", "observe", "expert_concealment", costly=True, secret=True),
    R("read whether the merchant is lying", "observe", "other", tier="moderate", opp=11, secret=True, src=("goodwill",)),
    R("recall a rival house's crest, herald watching", "recall", "trade_knowledge", obs="acts"),
    R("recall an old treaty's terms", "recall", "edge_of_common", costly=True),
    R("break down a barred door, guards coming", "force", "reinforced", src=("clock",), obs="acts"),
    R("kick in a rotten board (noise)", "force", "flimsy", src=("clock",), between=True),
    R("throw a lantern at a hanging sack at 30 ft", "strike", "small_or_far_object", src=("item",)),
    R("hit a barrel with a thrown rock", "strike", "large_near_object"),
    R("reach cover across the yard under arrows", "evade", "cover_far", obs="acts", heavy=True),
    R("duck behind the cart", "evade", "cover_near", obs="acts"),
    R("rig a tripwire before the guards come", "setup", "prepared", src=("clock",)),
    R("kick dust in a thug's eyes", "setup", "other", tier="easy", opp=11, obs="acts"),
    R("climb a crumbling tower wall at night", "exert", "hard_climb", hind=1, src=("height",), heavy=True, intr=True, nudge=1),
    R("swim across a strong current", "exert", "hard_climb", src=("hazard",)),
    R("cross a rope bridge in wind", "exert", "hard_climb", hind=1, src=("height",), heavy=True),
    R("pick across loose scree above a drop", "move", "rough_ground", hind=1, src=("height",), heavy=True, intr=True, nudge=1, between=True),
    R("dash across a burning hall", "move", "hazardous", haz=2, src=("hazard",)),
    R("get past a mob blocking the bridge", "move", "obstructed", obs="acts", hind=1),
    R("repair a cracked wagon wheel on the road", "handle", "crude_work", src=("clock",), intr=True, nudge=1),
    R("open a well-oiled gate quietly", "handle", "ordinary_use", obs="acts", intr=True, nudge=0),
    R("intimidate a thug into backing off (R2)", "talk", "other", tier="moderate", ap="moderate", opp=13, obs="acts"),
    R("persuade an unfriendly captain (Unfriendly R1)", "talk", "other", tier="moderate", ap="hard", social=13, src=("goodwill",)),
    R("juggle torches to hold a crowd", "talk", "other", tier="moderate", src=("item",), between=True),
    R("imitate a bird call to signal an ally", "talk", "other", tier="easy", obs="acts"),
    R("balance a coin on a blade to impress", "handle", "other", tier="easy", costly=True),
]
# The class-`other` share is measured on the unopposed, unlicensed acts a rubric must cover; social and opposed
# beats never use a tier under A/B/C, so they are not "rubric misses".
RUBRIC_ACTS = [a for a in ACTS if a["opp"] is None and a["social"] is None]


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


@functools.cache
def frame(i, mod, variant, terr=0, kerr=0, serr=0):
    """The frame of act i for a PC at `mod` under `variant`, with injected errors: terr tier rungs, kerr extra
    hindering snags, serr stakes rungs. Returns None for a beat that does not roll."""
    a = ACTS[i]
    intr = a["intr"] or variant == "B*"  # B*: B with a citable intrinsic fact on every act (B's worst case)
    variant = "B" if variant == "B*" else variant
    played = variant == "as_played"
    # tier (the DM's rung)
    if played or variant == "C":
        t = TIERS.index(a["ap"] if played else a["base"]) + terr
    elif variant == "A" or (variant == "B" and a["cls"] == "other"):
        t = TIERS.index(a["base"] if a["every"] else a["ap"]) + terr
    else:  # B: base + a nudge that needs a citable intrinsic fact, never two rungs, never across the trivial
        b = TIERS.index(a["base"])  # line (01.4.1 UNCERTAIN reads the class base; 01.6.5)
        t = 0 if b == 0 else clamp(b + clamp(a["nudge"] + (terr if intr else 0), -1, 1), 1, 5)
    t = clamp(t, 0, 5)
    # does it roll?
    sources = set(a["src"])
    if a["obs"] == "acts" or (played and a["obs"] == "passive"):
        sources.add("observer")
    social_tier = played and a["social"] is not None
    opposed = (a["opp"] is not None or a["social"] is not None) and not social_tier
    if a["social"] == "certain" and not played:
        return None
    if not opposed and t == 0:
        return None
    if not played and not (sources or a["costly"]):
        return None
    # DC
    if a["opp"] is not None:
        dc = a["opp"]
    elif a["social"] is not None and not played:
        dc = a["social"]
    elif variant == "C":
        dc = DC["easy"]
    else:
        dc = DC[TIERS[t]]
    st = (2 if a["heavy"] else 1) if sources else 0
    if variant == "C" and not opposed and t >= 2:
        st += 1  # obstacle quality moves stakes, not the roll
    h = a["hind"] + kerr
    if played:
        prec, prot = min(h, 2), 0
    elif variant == "C":
        prec, prot = 0, min(h, 2)
    else:
        prec, prot = min(h, 1), min(max(h - 1, 0), 1)
    st = clamp(st + prot + serr, 0, 2)
    m = mod - 2 * prec
    o = odds(m, dc)
    long_shot = False
    guarded = variant in ("A", "B") and not opposed and not a["secret"] and st < 2
    if guarded and o.critical_failure > max(5, o.success_or_better):
        if prec:  # 01.6.13 (1): the cited Precision snag applies as Protective instead
            m, st = m + 2, min(2, st + 1)
            o = odds(m, dc)
        if o.critical_failure > max(5, o.success_or_better):  # a rung the guard added does not exempt it
            long_shot = True  # 01.6.13 (2): shown labelled, with the best computed alternative
    return dict(mod=m, dc=dc, st=st, o=o, opposed=opposed, secret=a["secret"], long_shot=long_shot,
                guarded=guarded)


def s_of(f):
    return 100 if f is None else f["o"].success_or_better


def pct(x):
    return "%5.1f" % x


out = []
P = out.append
P("I-158 difficulty rubric sim (lane D §5), seed %d. Acts: %d (everyday %d, T-00-5 anchor rows %d); PCs %s."
  % (SEED, len(ACTS), sum(a["every"] for a in ACTS), sum(a["anchor"] for a in ACTS),
     ", ".join("%s %+d" % p for p in PCS)))
other = [a for a in RUBRIC_ACTS if a["cls"] == "other"]
P("Rubric coverage: %d of %d unopposed, non-social acts fall in class `other` (%.1f%%; target < 10%%): %s"
  % (len(other), len(RUBRIC_ACTS), 100 * len(other) / len(RUBRIC_ACTS), "; ".join(a["label"] for a in other)))

# 1. share of everyday acts that roll; 2. mean success-or-better
P("\n1-2. Everyday acts: share that roll; mean success-or-better (no roll = 100) per PC; T-00-5 anchor rows the same")
P("variant   | roll share | everyday " + " ".join("%9s" % n for n, _ in PCS) + " | anchor " + " ".join("%9s" % n for n, _ in PCS))
for v in VARIANTS:
    ev = [i for i, a in enumerate(ACTS) if a["every"]]
    an = [i for i, a in enumerate(ACTS) if a["anchor"]]
    rolls = statistics.mean(frame(i, m, v) is not None for i in ev for _, m in PCS)
    P("%-9s |   %5.1f%%   |          " % (v, 100 * rolls)
      + " ".join("%9s" % pct(statistics.mean(s_of(frame(i, m, v)) for i in ev)) for _, m in PCS)
      + " |        " + " ".join("%9s" % pct(statistics.mean(s_of(frame(i, m, v)) for i in an)) for _, m in PCS))

# 3. CF > S; 4. max CF at Safe / Risky
P("\n3-4. Rolled frames (acts x PCs): CF > S overall; on non-Dire unopposed non-secret frames (raw / shown"
  " without the long-shot label / labelled long shot); max CF at Safe and Risky (all; excluding long shots)")
for v in VARIANTS:
    fs = [frame(i, m, v) for i in range(len(ACTS)) for _, m in PCS]
    fs = [f for f in fs if f]
    bad = [f for f in fs if f["o"].critical_failure > f["o"].success_or_better]
    nd = [f for f in bad if f["st"] < 2 and not f["opposed"] and not f["secret"]]
    unl = [f for f in nd if not f["long_shot"]]
    mx = {s: max([f["o"].critical_failure for f in fs if f["st"] == s] or [0]) for s in (0, 1)}
    mx2 = {s: max([f["o"].critical_failure for f in fs if f["st"] == s and not f["long_shot"]] or [0]) for s in (0, 1)}
    mx3 = {s: max([f["o"].critical_failure for f in fs if f["st"] == s and not f["long_shot"] and not f["opposed"]
                   and not f["secret"]] or [0]) for s in (0, 1)}
    P("%-9s | rolled %3d | CF>S %3d | non-Dire unopposed: %3d / %3d / %3d | max CF Safe %2d%% Risky %2d%%"
      " | excl. long shots: %2d%% / %2d%% | also excl. opposed and secret: %2d%% / %2d%%"
      % (v, len(fs), len(bad), len(nd), len(unl), sum(f["long_shot"] for f in nd), mx[0], mx[1], mx2[0], mx2[1],
         mx3[0], mx3[1]))

# 5. approach spread in fights (P-117)
APPROACHES = [("strike", "might", "atk"), ("shoot", "agility", "atk"), ("grapple", "might", "grab"),
              ("shove", "might", "grab"), ("feint", "wits", "wits")]
PROFILES = {"off-attr": dict(might=-1, agility=0, wits=1), "untrained": dict(might=0, agility=0, wits=0),
            "average": dict(might=2, agility=1, wits=0), "P1": dict(might=5, agility=2, wits=1),
            "P3": dict(might=9, agility=4, wits=2)}
rng = random.Random(SEED)
DEFENDERS = []
for _ in range(300):  # band 1-2 foes (archetypes.yaml guard 12-15): attributes and combat competence
    ag, mi, wi, comp = rng.randint(0, 3), rng.randint(0, 3), rng.randint(-1, 2), rng.randint(1, 2)
    DEFENDERS.append(dict(atk=10 + ag + comp, grab=10 + max(ag, mi) + comp, wits=10 + wi))
P("\n5. Fight approach spread over %d foes x 5 approaches (strike, shoot, grapple, shove, feint): share of beats"
  " with >= 3 distinct odds; mean distinct; mean stdev of success %%" % len(DEFENDERS))
spread = {}
for v in VARIANTS:
    row = []
    for n, _ in PCS:
        pr = PROFILES[n]
        dist, sds = [], []
        for d in DEFENDERS:
            if v in ("as_played", "A"):  # P-117 as logged: one tier (Moderate), one attribute, every approach
                ss = [odds(max(pr.values()), DC["moderate"]).success_or_better for _ in APPROACHES]
            else:
                ss = [odds(pr[att], d[kind]).success_or_better for _, att, kind in APPROACHES]
            dist.append(len(set(ss)))
            sds.append(statistics.pstdev(ss))
        share = 100 * sum(x >= 3 for x in dist) / len(dist)
        spread[(v, n)] = share
        row.append("%s %5.1f%% %.1f %4.1f" % (n, share, statistics.mean(dist), statistics.mean(sds)))
    P("%-9s | " % v + " | ".join(row))

# 6-7. Monte Carlo sessions, with and without model-error injection
P("\n6-7. Monte Carlo: 2,000 sessions x 30 beats per PC (acts drawn uniformly); S3+ costs per session; P(a run"
  " of 3 failures). Errors: tier +-1 p=%.2f, extra snag q=%.2f, stakes +1 r=%.2f" % (P_TIER, Q_SNAG, R_STAKES))


def sessions(v, mod, inject):
    rng = random.Random(SEED)
    s3, runs = [], 0
    for _ in range(2000):
        streak = best = n3 = 0
        for _ in range(30):
            i = rng.randrange(len(ACTS))
            terr = rng.choice((-1, 1)) if rng.random() < P_TIER else 0
            kerr = 1 if rng.random() < Q_SNAG else 0
            serr = 1 if rng.random() < R_STAKES else 0
            face = rng.randint(1, 20)
            f = frame(i, mod, v, *((terr, kerr, serr) if inject else (0, 0, 0)))
            if f is None:
                streak = 0
                continue
            d = degree(face, f["mod"], f["dc"])
            if d in ("failure", "critical_failure"):
                streak += 1
                best = max(best, streak)
                n3 += SEV[(STAKES[f["st"]], d)] >= 3
            else:
                streak = 0
        s3.append(n3)
        runs += best >= 3
    return statistics.mean(s3), 100 * runs / 2000


for inject in (False, True):
    P(("with errors" if inject else "no errors") + ":")
    for v in VARIANTS:
        P("  %-9s | " % v + " | ".join("%s S3+ %.2f, 3-fail %4.1f%%" % ((n,) + sessions(v, m, inject)) for n, m in PCS))

# error bound: worst success drop per beat
P("\nError bound: worst success-or-better drop per beat (points) over acts x PCs: any single error; all errors"
  " together (tier +1 and an extra snag; a no-roll beat that starts rolling counts from 100). B* = B with a"
  " citable intrinsic fact on every act (B's worst case: a wrong nudge is always possible)")
drops = {}
for v, rows in [(v, "all") for v in VARIANTS] + [("B", "rubric"), ("B", "other"), ("B*", "rubric")]:
    single = combined = 0
    worst = []
    for i in range(len(ACTS)):
        if rows != "all" and (ACTS[i]["cls"] == "other") != (rows == "other"):
            continue
        for n, m in PCS:
            s0 = s_of(frame(i, m, v))
            single = max(single, s0 - s_of(frame(i, m, v, 1, 0)), s0 - s_of(frame(i, m, v, 0, 1)),
                         s0 - s_of(frame(i, m, v, -1, 0)))
            c = max(s0 - s_of(frame(i, m, v, t, k)) for t in (-1, 0, 1) for k in (0, 1))
            combined = max(combined, c)
            worst.append((c, ACTS[i]["label"], n))
    drops[(v, rows)] = (single, combined)
    worst.sort(key=lambda w: -w[0])
    P("%-9s %-6s | single %3d | combined %3d | worst: %s" % (v, rows, single, combined,
                                                         "; ".join("%s (%s) %d" % (w[1], w[2], w[0]) for w in worst[:2])))

# 8. CT-1..CT-6
S = lambda m, t: odds(m, DC[t]).success_or_better  # noqa: E731
ct6 = all(odds(m, DC[t]).critical_failure <= 10 for t in TIERS[1:] for m in range(-8, 17)
          if odds(m, DC[t]).success_or_better >= 50)
CT = [("CT-1 +2 vs Easy >= 60", S(2, "easy") >= 60, S(2, "easy")),
      ("CT-2 +5 vs Moderate 50-65", 50 <= S(5, "moderate") <= 65, S(5, "moderate")),
      ("CT-2 +1 vs Moderate 30-40", 30 <= S(1, "moderate") <= 40, S(1, "moderate")),
      ("CT-3 +5 vs Hard 25-35", 25 <= S(5, "hard") <= 35, S(5, "hard")),
      ("CT-3 +9 vs Hard 45-55", 45 <= S(9, "hard") <= 55, S(9, "hard")),
      ("CT-4 +5 vs Very hard <= 10", S(5, "very_hard") <= 10, S(5, "very_hard")),
      ("CT-4 +12 vs Very hard 35-45", 35 <= S(12, "very_hard") <= 45, S(12, "very_hard")),
      ("CT-5 +14 vs Legendary 20-30", 20 <= S(14, "legendary") <= 30, S(14, "legendary")),
      ("CT-5 <= +9 vs Legendary only a natural 20", all(S(m, "legendary") <= 5 for m in range(-8, 10)), "-"),
      ("CT-6 S >= 50 => CF <= 10 (all rungs, -8..+16)", ct6, "-")]
P("\n8. Calibration targets (ladder from resolution.yaml; unchanged by the rubric): "
  + "; ".join("%s: %s (%s)" % (n, "pass" if ok else "FAIL", val) for n, ok, val in CT))

# acceptance (variant B)
easy_every = [i for i, a in enumerate(ACTS) if a["every"] and a["base"] == "easy" and a["opp"] is None
              and a["social"] is None]
fb = [frame(i, 0, "B") for i in easy_every]
acc1 = all(f is None or (f["o"].success_or_better >= 45 and f["o"].critical_failure <= 10) for f in fb)
worst1 = min((f["o"].success_or_better, f["o"].critical_failure) for f in fb if f)
fsB = [frame(i, m, "B") for i in range(len(ACTS)) for _, m in PCS]
acc2 = sum(1 for f in fsB if f and f["st"] < 2 and not f["opposed"] and not f["secret"] and not f["long_shot"]
           and f["o"].critical_failure > f["o"].success_or_better)
modB = [i for i, a in enumerate(ACTS) if a["cls"] != "other" and a["opp"] is None and a["social"] is None
        and TIERS.index(a["base"]) + a["nudge"] == 2]
p1_mod = S(5, "moderate")
p1_rows = statistics.mean(s_of(frame(i, 5, "B")) for i in modB)
acc5 = statistics.mean(spread[("B", n)] for n, _ in PCS)
P("\nAcceptance (variant B):")
P("  [%s] untrained on everyday Easy-class acts: every rolled frame S >= 45 and CF <= 10 (worst S %d / CF %d)"
  % ("pass" if acc1 else "FAIL", worst1[0], worst1[1]))
P("  [%s] non-Dire unopposed non-secret frames shown with CF > S (not labelled long shot): %d"
  % ("pass" if acc2 == 0 else "FAIL", acc2))
P("  [%s] P1 (+5) at Moderate succeeds >= 50%%: %d%% clean; mean %.1f%% over Moderate-class rows (snags included)"
  % ("pass" if p1_mod >= 50 else "FAIL", p1_mod, p1_rows))
P("  [%s] CT-1..CT-6 hold" % ("pass" if all(ok for _, ok, _ in CT) else "FAIL"))
P("  [%s] >= 3 distinct odds across approaches in >= 70%% of combat beats: %.1f%% (mean over PCs; per PC %s)"
  % ("pass" if acc5 >= 70 else "FAIL", acc5, ", ".join("%s %.0f%%" % (n, spread[("B", n)]) for n, _ in PCS)))
P("  [%s] worst-case success drop per beat under error injection <= 25 points: single error %d, all errors %d"
  % ("pass" if drops[("B", "all")][1] <= 25 else "FAIL", drops[("B", "all")][0], drops[("B", "all")][1]))
P("         (rubric rows: single %d, all %d; rubric rows if every act had a citable intrinsic fact: single %d,"
  " all %d; class `other`: single %d, all %d)" % (drops[("B", "rubric")] + drops[("B*", "rubric")]
                                                 + drops[("B", "other")]))
P("  [%s] class `other` share < 10%%: %.1f%%"
  % ("pass" if len(other) / len(RUBRIC_ACTS) < 0.10 else "FAIL", 100 * len(other) / len(RUBRIC_ACTS)))
print("\n".join(out))
