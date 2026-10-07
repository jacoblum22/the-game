"""10_table_builder.py -- PR-10-10 (ch.10): build an encounter table's threat sub-table from a gate.

One deterministic algorithm, given a pool of archetypes with weights, a home band and the engine's RNG, writes a
d20 threat sub-table that passes PR-10-8 by construction:
  - eight slots: 3+3 faces at home-1, 3+3+3+2 at home, 2+1 at home+1 (09.8.2's 30/55/15);
  - each slot draws an archetype from the pool by weight among those fielded at the slot's band
    (archetypes.yaml#bands), without repeating one already on the table while another is available;
  - each slot starts at the shape T-10-25 gives for its home band and position (a crowd, a pair, an elite, one, a
    minion, a solo) and steps down the shape ladder until PR-09-4's word for that shape, against a reference PC
    of the home band with the counter held (PR-10-8 step 2; at home band 1 against the light reference as well,
    [revision: I-040]), is at most the slot's ceiling: fair for home-1 and
    home rows, hard for home+1 rows (09.8.1 rule 3: a rolled fight is never lethal; hard is its ceiling). The high
    face of a ranged count must not be lethal either. A slot whose archetype fails at the bottom rung redraws.
  - a slot that no pool archetype can fill at its band widens the pool to its fallback (the caller's: a site's
    theme gate alone, a region's terrain branch), and only then takes the nearest band any pool archetype has.
  - the second home row carries `complication: true` (its word is at most fair by construction); a lurker
    archetype's row is an ambush.
Used by: `10-site-tables.py` (every site theme x domain pair at every band, I-022) and `12-world-seed.py`
(a world seed's regional tables, 12.16, I-028). The audit (`10-word-audit.py`) is imported, not copied.
"""
import os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("word_audit_10", os.path.join(HERE, "10-word-audit.py"))
WA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(WA)
ARCH = WA.ARCH
WORDS = WA.WORDS

SLOTS = [(3, -1), (3, -1), (3, 0), (3, 0), (3, 0), (2, 0), (2, 1), (1, 1)]
# T-10-25 start shapes: (count, variant) per home band, one per slot (same order as SLOTS)
START = {
    1: [("1-2", "standard"), ("1-2", "standard"), ("6-8", "minion"), ("6-8", "minion"), ("2", "standard"), ("1", "elite"), ("1", "standard"), ("2", "minion")],
    2: [("4-6", "minion"), ("2", "standard"), ("2", "standard"), ("1", "elite"), ("4-6", "minion"), ("2", "standard"), ("1", "minion"), ("1", "minion")],
    3: [("6-8", "minion"), ("2", "standard"), ("1", "elite"), ("2", "minion"), ("1", "elite"), ("1", "standard"), ("1", "minion"), ("1", "minion")],
    4: [("2", "standard"), ("1", "elite"), ("1", "standard"), ("1", "elite"), ("1", "standard"), ("1", "standard"), ("1", "minion"), ("1", "minion")],
    5: [("2", "standard"), ("1", "standard"), ("1", "standard"), ("1", "minion"), ("1", "minion"), ("1", "standard"), ("1", "solo"), ("1", "solo")],
}
# the shape ladder, most dangerous first; a slot steps down from its start shape
LADDER = [("6-8", "minion"), ("4-6", "minion"), ("2", "standard"), ("1", "elite"), ("1-2", "standard"), ("1", "standard"), ("2", "minion"), ("1", "minion")]
SOLO_LADDER = [("1", "solo"), ("1", "elite"), ("1", "standard"), ("1", "minion")]
CEILING = {-1: "fair", 0: "fair", 1: "hard"}
LABEL = {-1: "home-1", 0: "home", 1: "home+1"}


def _slot_band(home, off):
    return max(1, min(5, home + off))


def _rungs(start):
    lad = SOLO_LADDER if start[1] == "solo" else LADDER
    return lad[lad.index(start):]


def _weighted_pick(rng, items):
    """items: list of (key, weight>0); one engine draw (RC-RNG)."""
    tot = sum(w for _, w in items)
    x = rng.random() * tot
    for k, w in items:
        x -= w
        if x < 0:
            return k
    return items[-1][0]


def try_slot(arch, home, off, start):
    """Step down the ladder for one archetype; returns (row-dict, word) or (None, None)."""
    for count, variant in _rungs(start):
        row = {"range": "1", "band": LABEL[off], "ref": [arch], "count": count, "variant": variant, "leader": False}
        r = WA.audit_row(row, home)
        if r["problems"] or "mid" not in r:
            continue
        ok = WORDS.index(r["mid"][0]) <= WORDS.index(CEILING[off]) and r["high"][0] != "lethal"
        if ok and "light_mid" in r:   # [revision: I-040] the light reference at its bands, same ceiling
            ok = WORDS.index(r["light_mid"][0]) <= WORDS.index(CEILING[off]) and r["light_high"][0] != "lethal"
        if ok:
            return row, r["mid"][0]
    return None, None


def build_threat_table(pool, home, rng, fallback_pool=None, notes=None):
    """pool / fallback_pool: dict arch_id -> weight. Returns (rows, log) where rows are EncounterRows (10.10.1)
    and log lists each slot's choice and any fallback used."""
    rows, log, used = [], [], set()
    face = 1
    for i, (w, off) in enumerate(SLOTS):
        b = _slot_band(home, off)
        chosen = None
        for which, src in (("pool", pool), ("fallback", fallback_pool or {})):
            cands = {a: wt for a, wt in src.items() if a in ARCH and ARCH[a]["bands"][0] <= b <= ARCH[a]["bands"][1] and wt > 0}
            tried = set()
            while cands.keys() - tried:
                fresh = [(a, wt) for a, wt in sorted(cands.items()) if a not in tried and a not in used]
                pick_from = fresh or [(a, wt) for a, wt in sorted(cands.items()) if a not in tried]
                a = _weighted_pick(rng, pick_from)
                tried.add(a)
                row, word = try_slot(a, home, off, tuple(START[home][i]))
                if row:
                    chosen = (row, word, which)
                    break
            if chosen:
                break
        if not chosen:
            # nearest band any pool archetype has (a weaker creature than the slot asks for), fixed band
            allp = dict(fallback_pool or {}); allp.update(pool)
            best = sorted(((min(abs(b - ARCH[a]["bands"][0]), abs(b - ARCH[a]["bands"][1])), a) for a in allp if a in ARCH))
            for _, a in best:
                nb = max(ARCH[a]["bands"][0], min(ARCH[a]["bands"][1], b))
                row = {"range": "1", "band": nb, "ref": [a], "count": "1", "variant": "standard", "leader": False}
                r = WA.audit_row(row, home)
                if "mid" in r and WORDS.index(r["mid"][0]) <= WORDS.index(CEILING[off]) and \
                        ("light_mid" not in r or WORDS.index(r["light_mid"][0]) <= WORDS.index(CEILING[off])):
                    chosen = (row, r["mid"][0], "nearest band")
                    break
        if not chosen:
            raise RuntimeError("PR-10-10: no archetype can fill slot %d at home %d" % (i + 1, home))
        row, word, which = chosen
        used.add(row["ref"][0])
        lo, hi = face, face + w - 1
        face = hi + 1
        out = {"range": str(lo) if lo == hi else "%d-%d" % (lo, hi), "kind": "adversary", "ref": row["ref"], "band": row["band"], "count": row["count"]}
        if row["variant"] != "standard":
            out["variant"] = row["variant"]
        a = ARCH[row["ref"][0]]
        out.update({"threat": True, "ambush": "lurker" in a["roles"], "complication": i == 3, "when": "any"})
        if notes and row["ref"][0] in notes:
            out["note"] = notes[row["ref"][0]]
        rows.append(out)
        log.append((i + 1, row["ref"][0], row["band"], row["count"], row["variant"], word, which))
    return rows, log
