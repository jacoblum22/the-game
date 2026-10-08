"""12-answer_ladder_sim.py -- R2-D [DL-12-60; DL-15-38], revised R2-H [DL-12-90; DL-12-91]: questions to NPCs
(PR-12-10), lazy settlement of testimony (PR-12-12), casting and the reduced case (PR-15-6) on packed seeded worlds.

  python 12-answer_ladder_sim.py        # report to stdout; committed as 12-answer_ladder_sim-output.txt

R2-H retired the R2-D ladder (store, pack, propose-and-ratify, pointer) as a source of speech: an ordinary answer is
now the NPC's own words (testimony), so R2-D's part A ("I don't know" + pointer share) and part B (clustering of
ratified facts) measured machinery that no longer runs, and are replaced. What a sim can still say honestly:
  A. how often the asked NPC's speaker card holds nothing on the topic (no record, no pack fact, not a role topic, not
     public news of their home): the share of answers that will be hearsay, a guess or an opinion (testimony, settled
     lazily) or a rare in-voice "I don't know". The live "I don't know" rate is the narrator's (OEQ-12-25).
  B. lazy settlement (PR-12-12): settlements and Oracle rolls per 100 asks against R2-D's propose-and-ratify, the share
     of settled claims found false, and that no accepted or ratified claim asserts a case node (consequential claims
     route to the case).
  C. unchanged: "who is <story role>?" answerable within 3 turns, and the reduced case valid (the consequential route
     of PR-12-10 step 1 is unchanged).
Ask-twice consistency (R2-D's D) is now the narrator's, fed its own `said` records: not simulable, measured live.

Worlds are 12-world-seed.py's build_seed + seed_packs (imported, not copied), seeds 2001-2030. Data the rules name:
social.yaml#common_knowledge (topics, role topics), #cast, resolution.yaml#oracle (Likely yes on 26+),
investigation.yaml#reduced_case. Assumptions (stated, not measured): what players ask (topic mix, question kinds), the
reach mix, how often testimony is about the case's people (TESTIMONY_BIAS), how often a claim would help or hinder beyond
the ordinary (BEYOND_SHARE), and how often a player relies on what they were told (ACTED_SHARE). Seeded: SEED = 12010.
"""
import os, sys, random, importlib.util
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("ws12", os.path.join(HERE, "12-world-seed.py"))
WS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(WS)

SEED = 12010
CK = WS.SOCD["common_knowledge"]
ORC = {r["id"]: r for r in WS.load("resolution.yaml")["oracle"]["rungs"]}
TOPICS = list(CK["topics"])
KINDS = [("where is X", 0.25), ("what happened", 0.25), ("what is X like or for", 0.25), ("what do you want or think", 0.15), ("who would know", 0.10)]
# reach mix of an ordinary ask: a certain beat or plain SPEECH runs at Standard (15.3.10; social.yaml#delivery.information);
# the rest roll (assumed: failure 30%, Limited 25%, Standard 30%, Great 15%)
CERTAIN_SHARE = 0.70
ROLLED = [(0, 0.30), (1, 0.25), (2, 0.30), (3, 0.15)]
TESTIMONY_BIAS = 0.30     # assumed share of answers about the case's people (R2-D's PROPOSAL_BIAS, same value)
BEYOND_SHARE = 0.20       # assumed share of ordinary claims that would help or hinder beyond the ordinary (12.14.13's question)
ACTED_SHARE = 0.25        # assumed share of answers the player later relies on (acts on, cites, travels to; PR-12-12 triggers)
# R2-D baseline, from the committed R2-D output (50% mix): rung-3 Oracle rolls 693 + 136 + 1184 = 2013 in 6000 asks
R2D_ORACLE_PER_100 = 100.0 * 2013 / 6000


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


def worlds(n=30, first=2001):
    out = []
    for s in range(first, first + n):
        out.append((s, WS.seed_packs(WS.build_seed(s), s)))
    return out


def card_has(reg, npc, topic, said_topics):
    """PR-12-10 step 3: does the speaker card hold anything on the topic? (records written in play count as said here)"""
    if topic in said_topics:
        return "said"
    if any(k.get("topic") == topic for k in npc.get("knowledge") or []):
        return "pack"
    band = odds_for(reg, npc, topic)[0]
    return band if band != "other" else None


def part_a(W, rng, on_role_share):
    """Asks of ordinary questions; per ask: willing or not (reach 0 = unwilling), the card's content, and one claim."""
    res, card, settle = Counter(), Counter(), Counter()
    per_holder = Counter()
    for seed, reg in W:
        case = reg["seed_cases"][0]
        holders = {p["holder"] for nd in case["nodes"] for p in nd["placements"] if p["holder_kind"] == "person"}
        solution = case["solution"]["subject"]["id"]
        cast = haven_cast(reg)
        said = defaultdict(set)
        for _ in range(200):
            npc = rng.choice(cast)
            kind = weighted(rng, KINDS)
            topic = rng.choice(CK["by_role"][WS.role_key(npc)]) if rng.random() < on_role_share else rng.choice(TOPICS)
            reach = 2 if rng.random() < CERTAIN_SHARE else weighted(rng, ROLLED)
            if reach == 0:
                res["unwilling"] += 1                       # a refusal or evasion in their voice (12.11.9)
                continue
            res["answered"] += 1
            if kind in ("what do you want or think", "who would know"):
                card["own_mind"] += 1                       # their stance, or whom they would send you to: always sayable
            else:
                card[card_has(reg, npc, topic, said[npc["id"]]) or "empty"] += 1
            said[npc["id"]].add(topic)
            # the claim the words make, and whether it is ever settled (PR-12-12)
            about = rng.choice(sorted(holders | {solution})) if rng.random() < TESTIMONY_BIAS else None
            if rng.random() >= ACTED_SHARE:
                settle["never"] += 1
                continue
            if about == solution:
                settle["case"] += 1                         # consequential: the case settles it; never a clue
                continue
            if rng.random() < BEYOND_SHARE:
                settle["oracle"] += 1
                if oracle_yes(rng, "likely"):
                    settle["true"] += 1
                    if about:
                        per_holder[(seed, about)] += 1
                else:
                    settle["false"] += 1
            else:
                settle["accepted"] += 1
                settle["true"] += 1
                if about:
                    per_holder[(seed, about)] += 1
    return res, card, settle, per_holder


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
    print("12-answer_ladder_sim.py -- PR-12-10 speak freely, PR-12-12 lazy settlement, PR-15-6 reduced case (R2-D, revised R2-H); seed %d" % SEED)
    W = worlds()
    print("worlds: 30 packed seeds (2001-2030); haven cast per world %.1f; incidents %s" % (
        sum(len(haven_cast(r)) for _, r in W) / len(W), dict(Counter(r["opening"]["inciting"]["option"] for _, r in W))))
    print()
    print("A. The speaker card (200 ordinary asks per world; reach: %d%% certain/SPEECH, the rest rolled %s)" % (CERTAIN_SHARE * 100, ROLLED))
    print("   an empty card means the answer is hearsay, a guess or an opinion (testimony, settled lazily), or a rare in-voice")
    print("   'I don't know'; 'said' = the topic was asked of them before (their own words are on the card)")
    fails = []
    for share in (0.3, 0.5, 0.7):
        res, card, settle, per_holder = part_a(W, random.Random(SEED + int(share * 10)), share)
        asked = sum(v for k, v in card.items() if k != "own_mind")
        first = asked - card["said"]
        print("  topic on the NPC's role %d%% of asks: answered %d, unwilling %d; card empty on the topic: %.1f%% of first asks, %.1f%% of all"
              " knowledge asks  by source %s" % (share * 100, res["answered"], res["unwilling"], pct(card["empty"], first), pct(card["empty"], asked),
                                                 {k: card[k] for k in ("on_role_topic", "pack", "public_local", "said", "empty")}))
        if share == 0.5:
            main_res, main_settle, main_holder = res, settle, per_holder
    print()
    print("B. Lazy settlement (50%% mix; assumed: %d%% of answers relied on, %d%% of claims beyond the ordinary, %d%% about the case's people)"
          % (ACTED_SHARE * 100, BEYOND_SHARE * 100, TESTIMONY_BIAS * 100))
    t, n = main_settle, main_res["answered"]
    settled = n - t["never"]
    print("  settlements %.1f per 100 answers (never settled %d of %d); routed to the case %d; accepted %d; Oracle at Likely %d (yes %d, no %d)"
          % (pct(settled, n), t["never"], n, t["case"], t["accepted"], t["oracle"], t["true"] - t["accepted"], t["false"]))
    print("  Oracle rolls per 100 asks: %.1f (R2-D propose-and-ratify: %.1f); settled claims found false (speaker wrong): %.1f%%"
          % (pct(t["oracle"], n + main_res["unwilling"]), R2D_ORACLE_PER_100, pct(t["false"], settled - t["case"])))
    top = main_holder.most_common(1)
    print("  true claims about a placement holder %d; most about one holder in one world %d; true claims asserting a case node: 0"
          " (consequential claims route to the case, which never delivers a clue by them)" % (sum(main_holder.values()), top[0][1] if top else 0))
    print("  reading: the narrator's words are no longer rolled; truth is decided for the quarter of claims a player relies on.")
    print("  The sim cannot judge meaning or self-consistency: OEQ-12-25 (live runs) measures contradictions, repeats and runarounds.")
    if t["false"] + t["true"] + t["case"] != settled:
        fails.append("B: settlement accounting")
    print()
    print("C. Reduced cases (investigation.yaml#reduced_case) and 'who is <story role>?' within 3 turns")
    for label, valid, turns, opts in part_c(W, random.Random(SEED + 99)):
        within = sum(v for k, v in turns.items() if k <= 3)
        print("  %-40s valid %d/30  answered within 3 turns %d/30  turns %s  options %s" % (label, valid, within, dict(sorted(turns.items())), dict(opts)))
        if valid < 30 or within < 30:
            fails.append("C: %s" % label)
    print()
    print("targets: B accounting holds and no accepted claim asserts a case node; C 100% valid and within 3 turns."
          " R2-D's A target (don't-know < 35%) and D (ask-twice) are retired with the ladder (DL-12-90).")
    print("RESULT:", "PASS" if not fails else "FAIL: " + "; ".join(fails))


if __name__ == "__main__":
    main()
