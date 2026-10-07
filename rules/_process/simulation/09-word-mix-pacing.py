"""09-word-mix-pacing.py -- [revision: I-045] what 04's pacing gives when a PC's fights come in the word mix the
shipped encounter tables actually produce, against the mix 04 assumes (DL-00-05: easy 25 / fair 40 / hard 30 /
lethal 5 %).

04-recog04.py (loaded by path, not copied) draws each conflict's challenge band as the PC's power band shifted by
the advisory word at framing (03.4.3: trivial -2, easy -1, fair 0, hard +1, lethal +2). This script swaps only
that distribution (`CONFLICT_OFFSET`, 20 faces) and re-runs R1's two fighting characters (the focused archer and
the swordsman), 200 seeds each, as 04-recog04.py does:
  A. DL-00-05's assumed mix (04.3.5, T-04-8 R1): the reference;
  B. the rolled-encounter mix: the threat faces of every shipped or built table (the 55 generic tables,
     10-word-audit-output.txt; the 560 site denizen tables, 10-site-tables-output.txt; the 2,600 world-seed
     regional tables, 12-world-seed-output.txt), each source weighted by its table count;
  C. a campaign mix: half the fights from B (what the road throws), half from 09.8.1 rule 3's chosen fights
     (a site heart, a lair, a quarry: fair 50 / hard 40 / lethal 10, the hard-leaning share 10.13.10 and 09.8.2
     allow), the mix 09.12.3 now names as the planning assumption.
Seeded (04-recog04's own seeds 1-200); deterministic. Output: 09-word-mix-pacing-output.txt.
"""
import os, re, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("r04", os.path.join(HERE, "04-recog04.py"))
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
WORDS = ["trivial", "easy", "fair", "hard", "lethal"]
OFF = {"trivial": -2, "easy": -1, "fair": 0, "hard": 1, "lethal": 2}

def read_mix(fn, pat):
    txt = open(os.path.join(HERE, fn), encoding="utf-8").read()
    line = [l for l in txt.splitlines() if re.search(pat, l)][0]
    return {w: float(re.search(w + r" ([\d.]+)%", line).group(1)) for w in WORDS}

def site_mix():
    txt = open(os.path.join(HERE, "10-site-tables-output.txt"), encoding="utf-8").read()
    tot = dict.fromkeys(WORDS, 0)
    for m in re.finditer(r"\| b\d \d+/\d+/\d+ ((?:[tefhl]\d+)+)", txt):
        for k, n in re.findall(r"([tefhl])(\d+)", m.group(1)):
            tot[{"t": "trivial", "e": "easy", "f": "fair", "h": "hard", "l": "lethal"}[k]] += int(n)
    s = sum(tot.values())
    return {w: 100.0 * v / s for w, v in tot.items()}

def faces(mix):
    """20 d20 faces of offsets, largest remainder."""
    raw = {w: mix[w] / 5.0 for w in WORDS}
    n = {w: int(raw[w]) for w in WORDS}
    for w in sorted(WORDS, key=lambda w: raw[w] - n[w], reverse=True)[:20 - sum(n.values())]:
        n[w] += 1
    return [OFF[w] for w in WORDS for _ in range(n[w])], n

gen = read_mix("10-word-audit-output.txt", r"^word mix over all threat faces")
seed = read_mix("12-world-seed-output.txt", r"regional encounter tables built and audited")
site = site_mix()
B = {w: (55 * gen[w] + 560 * site[w] + 2600 * seed[w]) / (55 + 560 + 2600) for w in WORDS}
CHOSEN = {"trivial": 0, "easy": 0, "fair": 50, "hard": 40, "lethal": 10}
Cm = {w: (B[w] + CHOSEN[w]) / 2.0 for w in WORDS}
A = {"trivial": 0, "easy": 25, "fair": 40, "hard": 30, "lethal": 5}
print("sources: generic %s" % {w: round(v, 1) for w, v in gen.items()})
print("         site    %s" % {w: round(v, 1) for w, v in site.items()})
print("         seed    %s" % {w: round(v, 1) for w, v in seed.items()})
for lab, mix in (("A. DL-00-05 assumed", A), ("B. rolled encounters (tables)", B), ("C. campaign: half rolled, half chosen", Cm)):
    off, n = faces(mix)
    r.CONFLICT_OFFSET = off
    print()
    print("%s: mix %s -> d20 faces %s" % (lab, " / ".join("%s %.1f" % (w, mix[w]) for w in WORDS), n))
    for style, key, mk in [(r.ARCHER, "deed.martial.archery", None), (r.PURE, "deed.martial.blade", r.CH_SWORD)]:
        res, pol, confs = r.tiers_of(style, [key], mk=mk)
        print("    %-52s %s | T5 within 60: %d of 200" % (style.name, r.line(res), sum(1 for x in res[5] if x < 99)))
