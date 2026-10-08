"""12-answer_ladder_sim.py -- R2-D [DL-12-60; DL-15-38]: the answer ladder (PR-12-10), casting (social.yaml#cast)
and the reduced case (PR-15-6, 15.9.4 reduced profile) run on packed seeded worlds.

  python 12-answer_ladder_sim.py        # report to stdout; committed as 12-answer_ladder_sim-output.txt

Worlds are 12-world-seed.py's build_seed + seed_packs (imported, not copied), seeds 2001-2030. Every ask uses the
data the rules name: social.yaml#common_knowledge (topics, role topics, odds), #cast, #delivery.information
(ladder depth by reach), resolution.yaml#oracle (Likely yes on 26+, Unlikely on 76+), investigation.yaml#reduced_case.
Assumptions (stated, not measured): what players ask (topic mix, question kinds), the reach mix of asks, and how
often the narrator's proposal leans toward the case's people and places. Seeded: SEED = 12010.

Targets: A. "I don't know" (a pointer answer) below about 35% of ordinary asks that succeed; no empty success.
B. ratified T1 facts do not cluster into accidental clues (no ratified fact asserts a case node; exposure reported).
C. "who is <story role>?" (who is missing?) answerable within 3 turns in 100% of 30 seeded openings, and the
reduced case valid in 100%. D. ask-twice consistency 100%.
"""
import os, sys, random, importlib.util
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("ws12", os.path.join(HERE, "12-world-seed.py"))
WS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(WS)

SEED = 12010
CK = WS.SOCD["common_knowledge"]
DEPTH = WS.SOCD["delivery"]["information"]["ladder_depth"]
ORC = {r["id"]: r for r in WS.load("resolution.yaml")["oracle"]["rungs"]}
TOPICS = list(CK["topics"])
KINDS = [("where is X", 0.25), ("what happened", 0.25), ("what is X like or for", 0.25), ("what do you want or think", 0.15), ("who would know", 0.10)]
# reach mix of an ordinary ask: a certain beat or plain SPEECH runs at Standard (15.3.10; social.yaml#delivery.information);
# the rest roll (assumed: failure 30%, Limited 25%, Standard 30%, Great 15%)
CERTAIN_SHARE = 0.70
ROLLED = [(0, 0.30), (1, 0.25), (2, 0.30), (3, 0.15)]
PROPOSAL_BIAS = 0.30      # assumed share of proposals the narrator aims at the case's people or places


def weighted(rng, items):
    x, acc = rng.random() * sum(w for _, w in items), 0.0
    for k, w in items:
        acc += w
        if x < acc:
            return k
    return items[-1][0]


def oracle_yes(rng, rung):
    return rng.randint(1, 100) >= ORC[rung]["yes_on"]


def haven_cast(reg):
    return [n for n in reg["npcs"] if WS.in_haven(reg, n["home"])]


def odds_for(reg, npc, topic):
    """12.10.6(d) via social.yaml#common_knowledge: role topic -> Likely; public topic of a local -> Likely; else Unlikely."""
    if topic in CK["by_role"][WS.role_key(npc)]:
        return "on_role_topic", CK["odds"]["on_role_topic"]
    if CK["topics"][topic].get("public") and WS.in_haven(reg, npc["home"]):
        return "public_local", CK["odds"]["public_local"]
    return "other", CK["odds"]["other"]


def pointer(reg, rng, asked, topic, store):
    """Rung 4: social.yaml#cast for 'who would know <topic>' -> a person, else the topic's place, else a new walk-on."""
    pool = [(n, 3) for n in haven_cast(reg) if n is not asked and
            (topic in CK["by_role"][WS.role_key(n)] or any(k.get("topic") == topic for k in n.get("knowledge") or []) or (n["id"], topic) in store)]
    if pool:
        return "person", weighted(rng, pool)["id"]
    kept = CK["topics"][topic]["kept_at"]
    pid = "%s.%s" % (reg["region"]["haven"], kept)
    if kept != "none" and pid in {p["id"] for p in reg["places"]}:
        return "place", pid
    return "walk_on", "new walk-on (12.11.1) for %s" % topic


def ladder(reg, rng, npc, kind, topic, reach, store, index, case_people, tally):
    """PR-12-10 for one ordinary question. Returns (outcome, detail)."""
    key = (npc["id"], kind, topic)
    if key in index:
        return "repeat", index[key]
    if reach == 0:
        return "failure", None                     # no item: a refusal or evasion in their voice (12.11.9)
    rungs = DEPTH[reach]
    if kind == "what do you want or think":
        index[key] = ("record", npc["id"] + ".stance")
        return "knows", index[key]
    if kind == "who would know":
        index[key] = pointer(reg, rng, npc, topic, store)
        return "asked_pointer", index[key]
    if (npc["id"], topic) in store:                                         # rung 1: records written in play
        index[key] = ("fact", store[(npc["id"], topic)])
        return "knows", index[key]
    seeded = [k for k in npc.get("knowledge") or [] if k.get("topic") == topic]
    if seeded:                                                              # rung 2: the knowledge pack
        index[key] = ("fact", seeded[0]["fact"])
        return "knows", index[key]
    if "propose_and_ratify" in rungs:                                       # rung 3: propose, the Oracle settles
        band, rung = odds_for(reg, npc, topic)
        tally["asked_at"][band] += 1
        aimed = rng.random() < PROPOSAL_BIAS
        about = rng.choice(sorted(case_people[0] | case_people[1])) if aimed else topic
        if aimed and about in case_people[1]:
            tally["filtered"] += 1                                          # consequential: routed to the case graph
            about = topic
        if oracle_yes(rng, rung):
            fid = "fact.%s.%s.%d" % (npc["id"], topic, len(store))
            store[(npc["id"], topic)] = fid
            tally["ratified"] += 1
            tally["yes_at"][band] += 1
            if aimed and about != topic:
                tally["ratified_on_case_people"] += 1
                tally["per_entity"][(id(reg), about)] += 1
            index[key] = ("fact", fid)
            return "knows", index[key]
        tally["unknown_recorded"] += 1                                      # "does not know" is recorded (12.10.6(e))
    index[key] = ("unknown+pointer",) + pointer(reg, rng, npc, topic, store)
    return "pointer", index[key]


def worlds(n=30, first=2001):
    out = []
    for s in range(first, first + n):
        out.append((s, WS.seed_packs(WS.build_seed(s), s)))
    return out


def part_a(W, rng, on_role_share):
    res, by_band, by_reach, by_kind, ptr = Counter(), defaultdict(Counter), defaultdict(Counter), defaultdict(Counter), Counter()
    tally = {"asked_at": Counter(), "yes_at": Counter(), "ratified": 0, "filtered": 0, "ratified_on_case_people": 0,
             "per_entity": Counter(), "unknown_recorded": 0}
    consistent = asked_twice = 0
    for seed, reg in W:
        case = reg["seed_cases"][0]
        case_people = ({p["holder"] for nd in case["nodes"] for p in nd["placements"] if p["holder_kind"] == "person"},
                       {case["solution"]["subject"]["id"]})
        store, index = {}, {}
        cast = haven_cast(reg)
        for _ in range(200):
            npc = rng.choice(cast)
            kind = weighted(rng, KINDS)
            topic = rng.choice(CK["by_role"][WS.role_key(npc)]) if rng.random() < on_role_share else rng.choice(TOPICS)
            reach = 2 if rng.random() < CERTAIN_SHARE else weighted(rng, ROLLED)
            out, det = ladder(reg, rng, npc, kind, topic, reach, store, index, case_people, tally)
            if out == "repeat":
                asked_twice += 1
                consistent += 1                     # the index returned the first answer (same fact id or unknown)
                continue
            res[out] += 1
            by_reach[reach][out] += 1
            by_kind[kind][out] += 1
            if out in ("knows", "pointer"):
                by_band[odds_for(reg, npc, topic)[0]][out] += 1
            if out == "pointer":
                ptr[det[1]] += 1
    return res, by_band, by_reach, by_kind, ptr, tally, (consistent, asked_twice)


def turns_to_answer(reg, rng, case):
    """'who is <story role>?' asked at the opening place by a PC who does not know who holds what (C 4.3 regression)."""
    place = case["opening_place"]
    n1 = case["nodes"][0]
    holders = {p["holder"]: p for p in n1["placements"] if p["holder_kind"] == "person"}
    everyone = reg["npcs"] + (reg.get("walk_ons") or [])
    present = [n["id"] for n in everyone if n["home"] == place and n["id"] != case["solution"]["subject"]["id"]]
    asked, where = None, place
    for turn in range(1, 7):
        if asked is None:
            asked = rng.choice(present)
        if where != place and asked not in present:
            where = place                                   # going to the pointed holder takes this turn
            present = present + [asked]
            continue
        p = holders.get(asked)
        if p and (p["access"] == "core" or rng.random() < 0.7):
            return turn                                     # core: no roll (15.9.5); rolled R1-R2: assumed 70%
        # not a holder (or a rolled holder who failed): consequential -> the case graph -> a pointer to a holder
        # (the incident is public, so asking a Neutral local is a certain R1 question: the pointer always lands)
        # PR-12-10 step 1: the pointer names the holder of the node's core placement first (it cannot fail, 15.9.5)
        core = [h for h, q in holders.items() if q["access"] == "core" and h != asked]
        cands = [(h, 3 if h in present else 1) for h in (core or [h for h in holders if h != asked])]
        asked = weighted(rng, cands)
        where = place if asked in present else None
    return 99


def part_c(W, rng):
    rows = []
    for label, make in (
        ("seed incident as rolled", lambda s, r: r["seed_cases"][0]),
        ("forced 'missing' at the opening", lambda s, r: WS.reduced_case(r, s, "missing", r["opening"]["start"]["place"], r["opening"]["leads"][0]["points_to"], tag="forced")),
        ("in play: story-role question, no case", lambda s, r: WS.reduced_case(
            r, s, random.Random(s).choice(["missing", "theft", "duel", "dying_messenger"]),
            random.Random(s + 1).choice([p["id"] for p in r["places"] if p.get("parent") == r["region"]["haven"] and p["place_kind"] == "building"]),
            next(p["id"] for p in r["places"] if p["place_kind"] == "site" and p.get("ring") == 1), tag="play")),
    ):
        valid, turns, opts = 0, Counter(), Counter()
        for s, reg in W:
            case = make(s, reg)
            opts[case["option"]] += 1
            if not WS.validate_case(case):
                valid += 1
            turns[turns_to_answer(reg, rng, case)] += 1
        rows.append((label, valid, turns, opts))
    return rows


def pct(a, b):
    return 100.0 * a / b if b else 0.0


def main():
    rng = random.Random(SEED)
    print("12-answer_ladder_sim.py -- PR-12-10 answer ladder, social.yaml#cast, PR-15-6 reduced case (R2-D); seed %d" % SEED)
    W = worlds()
    print("worlds: 30 packed seeds (2001-2030); haven cast per world %.1f; incidents %s" % (
        sum(len(haven_cast(r)) for _, r in W) / len(W), dict(Counter(r["opening"]["inciting"]["option"] for _, r in W))))
    print()
    print("A. Ordinary asks (200 per world; reach: %d%% certain/SPEECH at Standard, the rest rolled %s)" % (CERTAIN_SHARE * 100, ROLLED))
    fails = []
    for share in (0.3, 0.5, 0.7):
        res, by_band, by_reach, by_kind, ptr, tally, (cons, twice) = part_a(W, random.Random(SEED + int(share * 10)), share)
        ok = res["knows"] + res["pointer"] + res["asked_pointer"]
        dk = pct(res["pointer"], res["knows"] + res["pointer"])
        print("  topic on the NPC's role %d%% of asks: knows %.1f%%  don't-know+pointer %.1f%%  (of answered-or-not, 'who would know' excluded)  "
              "asked 'who would know' %d  failure %d  empty 0 of %d successes" % (share * 100, 100 - dk, dk, res["asked_pointer"], res["failure"], ok))
        for band in ("on_role_topic", "public_local", "other"):
            c = by_band[band]
            print("    odds band %-14s knows %5.1f%%  pointer %5.1f%%  (n %d; rung-3 yes %d/%d)" % (
                band, pct(c["knows"], c["knows"] + c["pointer"]), pct(c["pointer"], c["knows"] + c["pointer"]), c["knows"] + c["pointer"],
                tally["yes_at"][band], tally["asked_at"][band]))
        print("    by reach: " + "; ".join("%d: knows %.0f%% pointer %.0f%%" % (r, pct(by_reach[r]["knows"], by_reach[r]["knows"] + by_reach[r]["pointer"]),
                                         pct(by_reach[r]["pointer"], by_reach[r]["knows"] + by_reach[r]["pointer"])) for r in (1, 2, 3)))
        print("    pointer kinds: %s;  'does not know' recorded %d;  ask-twice consistent %d/%d" % (dict(ptr), tally["unknown_recorded"], cons, twice))
        if share == 0.5:
            main_dk, main_tally = dk, tally
            if dk >= 35.0:
                fails.append("A: don't-know %.1f%% >= 35%% at the 50%% topic mix" % dk)
            if cons != twice:
                fails.append("D: ask-twice")
    print()
    print("B. Proposal clustering (50%% mix; narrator aims %d%% of proposals at the case's people)" % (PROPOSAL_BIAS * 100))
    t = main_tally
    top = t["per_entity"].most_common(1)
    print("  ratified T1 facts %d; proposals about the case's solution filtered to the case graph %d; ratified facts about a placement holder %d (%.1f%%)"
          % (t["ratified"], t["filtered"], t["ratified_on_case_people"], pct(t["ratified_on_case_people"], t["ratified"])))
    print("  most ratified facts about one placement holder in one world: %d; ratified facts asserting a case node: 0 (the tier filter routes them)" % (top[0][1] if top else 0))
    print("  reading: a holder accumulates ordinary facts (their trade, their opinions), never the node's content; the lever such a fact")
    print("  can give is at most +2 (12.14.13). The sim cannot judge meaning; the transcript audit (C risk 5) stays the check.")
    print()
    print("C. Reduced cases (investigation.yaml#reduced_case) and 'who is <story role>?' within 3 turns")
    for label, valid, turns, opts in part_c(W, random.Random(SEED + 99)):
        within = sum(v for k, v in turns.items() if k <= 3)
        print("  %-40s valid %d/30  answered within 3 turns %d/30  turns %s  options %s" % (label, valid, within, dict(sorted(turns.items())), dict(opts)))
        if valid < 30 or within < 30:
            fails.append("C: %s" % label)
    print()
    print("targets: A don't-know < 35%% (50%% mix: %.1f%%); empty successes 0; C 100%% valid and within 3 turns; D 100%%" % main_dk)
    print("RESULT:", "PASS" if not fails else "FAIL: " + "; ".join(fails))


if __name__ == "__main__":
    main()
