"""Places and routes (Jake, 2026-10-20): where the party is, how far apart places are, and travel by the SRD.

In the three 180-round games of the second autoloop set, travel times and distances were the second biggest source
of contradictions (14 of 118 flagged, plus places restated differently). Dry runs on those games
(kaeris-opening/route-dry-run.md) showed that code can't reliably read from a sentence which two places a number
connects, but checks on the DM's own records of roads catch the clashes: with Sonnet standing in for the DM, they
found 11 real ones, 4 doubtful and 5 false, including all 4 targeted.

- **Records.** The DM records roads with `route`: places in the order the road runs, a leg per gap (miles, or a time
  turned into miles by the SRD's travel pace), and links of no distance (a place inside another, adjoining it, or a
  permanent portal). `travel` moves the party along recorded routes and moves the clock. Each reply names where the
  party is (`place`).
- **Checks** on the records, each time they're replayed: ALONG, the same two places more than 25% off what was
  recorded before; FIT, longer than two recorded routes through a third place added together, or shorter than their
  difference (when the compass puts the third place on the way, at least 0.7 times their sum); DIRECTION, the same two
  places given opposite compass directions.
- **Warnings** that prompt records, because the DM will miss more than Sonnet did: a place that isn't in the notebook,
  a move with no route or link recorded, a distance given with no route, a place's name inside another place's name
  with no link, and once for each new place entry, whether it's inside a known place. By the end of each game they
  would have prompted 88% of the places, 70% of the route legs and 27 of 30 links Sonnet recorded.

Nothing is stored apart from the calls: the records are the DM's `route`, `travel` and `place` calls in the
transcript, replayed each time with the notebook as it is now, so going back to an earlier line needs nothing more,
and a place noted later is matched to the records that used it. The code only flags; the DM decides. A warning stays
until it's settled or dismissed (dismiss_warning), except the "inside?" question, which is asked once."""

from __future__ import annotations

import functools
import heapq
import math
import re
from typing import Any

from dm import lore as notebook
from dm import srd
from dm.mechanics import Refused

# ---------- SRD travel ----------

PACE_MPH = {"slow": 2, "normal": 3, "fast": 4}  # Travel Pace: miles per hour, the same on foot, riding or in a cart
GALLOP_MPH = 8  # Mounts and Vehicles: a gallop for about an hour covers twice the fast pace's distance
DAY_HOURS = 8  # the Travel Pace table assumes 8 hours of travel a day
CURRENT_MPH = 3  # Rowed Vessels: going downstream, add the current (typically 3 miles per hour)
ROWED = ("rowboat", "keelboat")
WATER = "water"  # a water route and a road between the same two places are different ways (bard2 R82)
LAND = "land"
BY = ("foot", "horse", "cart", "boat")


@functools.cache
def vessels() -> dict[str, float]:
    """Waterborne vehicles' speeds (mph), from the SRD's equipment."""
    return {e["name"].lower(): float(e["speed"]["quantity"]) for e in srd.table("Equipment").values()
            if e.get("vehicle_category") == "Waterborne Vehicles"}


def speed(a: dict[str, Any]) -> float:
    """Miles per hour for a road record or a journey: by (foot, horse, cart, boat), pace, vessel, downstream,
    difficult. Raises Refused."""
    by = a.get("by") or "foot"
    if by not in BY:
        raise Refused(f"by: one of {', '.join(BY)}")
    if by == "boat":
        v = (a.get("vessel") or "rowboat").lower()
        if v not in vessels():
            raise Refused(f"vessel: one of {', '.join(sorted(vessels()))}")
        # a vessel's speed is the vessel's: no fast or slow pace on water (Mounts and Vehicles)
        return vessels()[v] + (CURRENT_MPH if a.get("downstream") and v in ROWED else 0)
    pace = a.get("pace") or "normal"
    if pace == "gallop":
        if by != "horse":
            raise Refused("pace gallop: only riding (by horse)")
        mph: float = GALLOP_MPH
    elif pace in PACE_MPH:
        mph = PACE_MPH[pace]
    else:
        raise Refused("pace: slow, normal or fast (or gallop, riding)")
    return mph / 2 if a.get("difficult") else mph  # difficult terrain: half the distance in the same time


def day_hours(a: dict[str, Any]) -> float:
    """Hours of travel in a day: 8, or for a crewed ship as many as the DM gives (up to 24)."""
    h = a.get("hours_a_day")
    if h and (a.get("by") != "boat" or not 0 < h <= 24):
        raise Refused("hours_a_day: only by boat, up to 24 (some ships travel up to 24 hours a day)")
    return float(h or DAY_HOURS)


def miles(leg: Any, a: dict[str, Any]) -> float | None:
    """A leg ({miles} or {hours} or {days}, or {} / None when not stated) in miles."""
    if not leg:
        return None
    given = [k for k in ("miles", "hours", "days") if leg.get(k) is not None]
    if len(given) > 1:
        raise Refused("a leg is given as one of miles, hours or days")
    if not given:
        return None
    v = float(leg[given[0]])
    if v < 0:
        raise Refused("a leg can't be negative")
    if given[0] == "miles":
        return v
    hours = v * day_hours(a) if given[0] == "days" else v
    return hours * speed(a)


def hm(hours: float) -> str:
    """5.25 -> '5 hours 15 minutes'."""
    total = round(hours * 60)
    h, mi = divmod(total, 60)
    out = [f"{h} hour{'s' if h != 1 else ''}"] if h else []
    out += [f"{mi} minute{'s' if mi != 1 else ''}"] if mi or not h else []
    return " ".join(out)


def num(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".") if x < 10 else f"{x:.0f}"


def mi(x: float) -> str:
    return f"{num(x)} mile" + ("" if num(x) == "1" else "s")


# ---------- the records ----------

def norm(x: Any) -> str:
    return re.sub(r"^the\s+", "", " ".join(str(x).split()), flags=re.I).casefold()


def entry(lore: dict[str, Any], x: Any) -> str | None:
    """The notebook entry a place's name is, with or without a leading "the"."""
    bare = re.sub(r"^the\s+", "", " ".join(str(x).split()), flags=re.I)
    return notebook.find(lore, x) or notebook.find(lore, bare) or notebook.find(lore, "the " + bare)


def _ok(e: dict[str, Any], *tools: str) -> bool:
    return e["kind"] == "call" and e.get("tool") in tools and not e.get("error")


def records(transcript: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any]]]:
    """(turn, call) for each route, travel and place call, in order."""
    return [(t, e) for t, e in notebook.turns(transcript) if _ok(e, "route", "travel", "place")]


def positions(transcript: list[dict[str, Any]]) -> list[tuple[int, int, str, bool]]:
    """(index in the transcript, turn, place, by travel) each time the party's place is given: each reply's `place`
    and each journey's end."""
    out, t = [], 0
    for i, e in enumerate(transcript):
        if e["kind"] == "player":
            t += 1
        if _ok(e, "place") and e["input"].get("place"):
            out.append((i, t, e["input"]["place"], False))
        elif _ok(e, "travel"):
            out.append((i, t, e["input"]["to"], True))
    return out


def here(transcript: list[dict[str, Any]]) -> str | None:
    """Where the party is: the last place given."""
    p = positions(transcript)
    return p[-1][2] if p else None


VEC = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}


def vec(d: Any) -> tuple[float, float] | None:
    """'north-east', 'west-northwest' -> a unit vector, or None."""
    ws = re.findall(r"north|south|east|west", str(d or "").lower())
    x, y = sum(VEC[w][0] for w in ws), sum(VEC[w][1] for w in ws)
    n = math.hypot(x, y)
    return (x / n, y / n) if n else None


class Atlas:
    """The DM's records replayed in order, names matched to the notebook as it is now. Places linked with no distance
    (inside, adjoining, a portal) count as one place. `flags` holds the checks' findings."""

    def __init__(self, lore: dict[str, Any], transcript: list[dict[str, Any]] | None = None) -> None:
        self.lore = lore
        self.parent: dict[str, str] = {}
        self.shown: dict[str, str] = {}  # a place's key -> its name as the notebook or the DM wrote it
        self.facts: dict[tuple[str, frozenset[str]], tuple[float, int]] = {}  # (land/water, pair) -> (miles, turn)
        self.vecs: dict[tuple[str, str], tuple[float, float]] = {}
        self.dirs: dict[tuple[str, str], tuple[str, int]] = {}
        self.flags: list[tuple[str, str]] = []  # (key to dismiss it by, text)
        self.involves: list[set[frozenset[str]]] = []  # each flag's pairs of places
        self.links: list[tuple[str, str]] = []
        self.stops: list[str] = []  # every place a record names, as written
        for t, e in records(transcript or []):
            if e["tool"] == "route":
                self.add(e["input"], t)
            elif e["tool"] == "travel":
                self.add_journey(e["input"], t)

    # ---- names ----
    def key(self, name: Any) -> str:
        """A place's key: its notebook entry's name if it has one, merged with the places it's linked to."""
        n = entry(self.lore, name) or str(name)
        k = norm(n)
        self.shown.setdefault(k, " ".join(n.split()))
        while self.parent.get(k, k) != k:
            k = self.parent[k]
        return k

    def name(self, k: str) -> str:
        return self.shown.get(k, k)

    # ---- recording ----
    def link(self, a: str, b: str) -> None:
        self.stops += [a, b]
        self.links.append((a, b))
        ka, kb = self.key(a), self.key(b)
        if ka == kb:
            return
        self.parent[kb] = ka
        for (cls, pair) in list(self.facts):  # the facts about b are about a now
            if kb in pair:
                v = self.facts.pop((cls, pair))
                new = frozenset(ka if p == kb else p for p in pair)
                if len(new) == 2:
                    self.facts.setdefault((cls, new), v)
        for (x, y) in list(self.vecs):
            if kb in (x, y):
                v = self.vecs.pop((x, y))
                nx, ny = (ka if x == kb else x), (ka if y == kb else y)
                if nx != ny:
                    self.vecs.setdefault((nx, ny), v)

    def add_journey(self, a: dict[str, Any], turn: int) -> list[str]:
        """A journey that gave its own distance (no route was recorded) is a road from where it started."""
        if a.get("from") and any(a.get(k) is not None for k in ("miles", "hours", "days")):
            leg = {k: a[k] for k in ("miles", "hours", "days") if a.get(k) is not None}
            return self.add({**a, "stops": [a["from"], a["to"]], "legs": [leg]}, turn)
        return []

    def add(self, a: dict[str, Any], turn: int) -> list[str]:
        """One route record: links, and a road (stops in order, legs, total, direction). Returns the new flags' texts."""
        for ln in a.get("links") or []:
            self.link(ln["a"], ln["b"])
        stops = a.get("stops") or []
        if len(stops) < 2:
            return []
        self.stops += stops
        cls = WATER if a.get("by") == "boat" else LAND
        st = [self.key(s) for s in stops]
        legs = [miles(x, a) for x in (a.get("legs") or [])][:len(st) - 1]
        legs += [None] * (len(st) - 1 - len(legs))
        tot = miles(a.get("total"), a)
        if tot is not None and sum(x is None for x in legs) == 1:
            legs[legs.index(None)] = max(tot - sum(x for x in legs if x is not None), 0)
        for i, x in enumerate(legs):  # a missing leg from an earlier fact around it
            if x is None:
                for j in range(i, -1, -1):
                    for kk in range(i + 1, len(st)):
                        f = self.facts.get((cls, frozenset([st[j], st[kk]])))
                        others = [legs[t] for t in range(j, kk) if t != i]
                        if f and None not in others:
                            legs[i] = max(f[0] - sum(others), 0)  # type: ignore[arg-type]
                            break
                    if legs[i] is not None:
                        break
        new: dict[frozenset[str], float] = {}
        for i in range(len(st)):
            for j in range(i + 1, len(st)):
                seg = legs[i:j]
                if seg and None not in seg and st[i] != st[j]:
                    new[frozenset([st[i], st[j]])] = sum(seg)  # type: ignore[arg-type]
        if tot is not None and st[0] != st[-1]:
            new.setdefault(frozenset([st[0], st[-1]]), tot)
        found: list[str] = []
        said = {k: entry(self.lore, x) or x for k, x in zip(st, stops)}  # names as this record gives them
        for pair, d in new.items():
            a_, b_ = sorted(pair)
            na, nb = said.get(a_, self.name(a_)), said.get(b_, self.name(b_))
            k = (cls, pair)
            fkey = f"turn {turn}: {na} - {nb}"
            if a.get("correct"):  # the DM's correction: it replaces the record, and the clashes over it go
                self.facts[k] = (d, turn)
                keep = [i for i, inv in enumerate(self.involves) if pair not in inv]
                self.flags, self.involves = [self.flags[i] for i in keep], [self.involves[i] for i in keep]
                continue
            if k in self.facts:
                f, ft = self.facts[k]
                if abs(d - f) > .25 * max(d, f) and abs(d - f) > .5:
                    found.append(f"{na} to {nb}: {mi(d)} (turn {turn}), but {mi(f)} on turn {ft}.")
                    self.flags.append((fkey, found[-1]))
                    self.involves.append({pair})
                continue
            for c in sorted({p for (cl, kk) in self.facts if cl == cls for p in kk} - {a_, b_}):
                ac, cb = self.facts.get((cls, frozenset([a_, c]))), self.facts.get((cls, frozenset([c, b_])))
                if ac and cb:
                    lo, hi = abs(ac[0] - cb[0]), ac[0] + cb[0]
                    v1, v2 = self.vec_of(a_, c), self.vec_of(c, b_)
                    between = bool(v1 and v2 and v1[0] * v2[0] + v1[1] * v2[1] >= .7)  # within 45 degrees: on the way
                    if between:
                        lo = .7 * hi
                    if d > 1.25 * hi + .5 or d < .75 * lo - .5:
                        nc = self.name(c)
                        found.append(f"{na} to {nb}: {mi(d)} (turn {turn}), but {na} to {nc} is {mi(ac[0])} "
                                     f"(turn {ac[1]}) and {nc} to {nb} {num(cb[0])} (turn {cb[1]})"
                                     + (f", and the compass puts {nc} on the way" if between else "")
                                     + f", so it should be {num(lo)} to {mi(hi)}.")
                        self.flags.append((fkey, found[-1]))
                        self.involves.append({pair, frozenset([a_, c]), frozenset([c, b_])})
            self.facts[k] = (d, turn)
        if a.get("direction") and st[0] != st[-1]:
            if v := vec(a["direction"]):
                self.vecs.setdefault((st[0], st[-1]), v)
            dw = str(a["direction"]).lower().replace("-", " ").split()[-1]
            fw, bw = (st[0], st[-1]), (st[-1], st[0])
            old = self.dirs.get(fw) or self.dirs.get(bw)
            if (bw in self.dirs and self.dirs[bw][0] == dw) or (fw in self.dirs and OPP.get(self.dirs[fw][0]) == dw):
                found.append(f"{said[st[0]]} to {said[st[-1]]}: {dw} (turn {turn}), but the other way on "
                             f"turn {old[1]}.")  # type: ignore[index]
                self.flags.append((f"turn {turn}: {said[st[0]]} - {said[st[-1]]} direction", found[-1]))
                self.involves.append({frozenset([st[0], st[-1]])})
            self.dirs.setdefault(fw, (dw, turn))
        return found

    def vec_of(self, a: str, b: str) -> tuple[float, float] | None:
        if v := self.vecs.get((a, b)):
            return v
        v = self.vecs.get((b, a))
        return (-v[0], -v[1]) if v else None

    # ---- asking ----
    def path(self, a: Any, b: Any, cls: str = LAND) -> tuple[float, list[str]] | None:
        """The shortest recorded way from a to b (miles, the places it goes through), or None."""
        ka, kb = self.key(a), self.key(b)
        if ka == kb:
            return 0.0, []
        edges: dict[str, list[tuple[str, float]]] = {}
        for (cl, pair), (d, _) in self.facts.items():
            if cl == cls:
                x, y = sorted(pair)
                edges.setdefault(x, []).append((y, d))
                edges.setdefault(y, []).append((x, d))
        best, heap = {ka: 0.0}, [(0.0, ka, [ka])]
        while heap:
            d, k, via = heapq.heappop(heap)
            if k == kb:
                return d, [self.name(p) for p in via[1:-1]]
            if d > best.get(k, math.inf):
                continue
            for nxt, dd in edges.get(k, []):
                if d + dd < best.get(nxt, math.inf):
                    best[nxt] = d + dd
                    heapq.heappush(heap, (d + dd, nxt, via + [nxt]))
        return None

    def connected(self, a: Any, b: Any) -> bool:
        return self.path(a, b, LAND) is not None or self.path(a, b, WATER) is not None

    def recorded(self, a: Any, b: Any) -> bool:
        """A distance is recorded between the two, or they're linked (the dry run's test for "already recorded")."""
        ka, kb = self.key(a), self.key(b)
        return ka == kb or any((cl, frozenset([ka, kb])) in self.facts for cl in (LAND, WATER))


def for_checker(lore: dict[str, Any], before: list[dict[str, Any]], reply: str) -> list[str]:
    """The recorded routes between the places a reply names and the party's place, for the continuity checker
    (Jake, 2026-10-22). `before`: the transcript before this turn, so only routes from earlier turns count. For each
    pair: the distance recorded for it (legs along one road count); else a sum through one other place the compass
    puts on the way; else the bounds two routes through one place allow, as the fit check. A route with an open
    clash over it is left out. In the dry run on 57 rounds the checker caught 11 of 11 real clashes this way (3
    without routes); with every route added up as a distance it made 8 bad changes, here none."""
    atlas = Atlas(lore, before)
    names: dict[str, str] = {x: x for x in atlas.stops} | _places(lore)  # any name -> the place
    named = sorted({n for x, n in names.items() if len(x) > 3 and re.search(
        r"(?<!\w)" + re.escape(re.sub(r"^the\s+", "", x, flags=re.I)) + r"(?!\w)", reply, re.I)})
    where = here(before)
    ends = sorted(set(named + ([where] if where else [])))
    disputed = lambda pr: any(pr in inv for inv in atlas.involves)  # noqa: E731
    lines: list[str] = []
    seen: set[frozenset[str]] = set()
    for a in ends:
        for b in ends:
            ka, kb = atlas.key(a), atlas.key(b)
            pair = frozenset([ka, kb])
            if a >= b or ka == kb or pair in seen:
                continue
            for cls in (LAND, WATER):
                how = "by water" if cls == WATER else "by land"
                f = atlas.facts.get((cls, pair))
                d = f[0] if f and not disputed(pair) else None
                lo = hi = None
                if not f:
                    others = {q for (cl, kk) in atlas.facts if cl == cls for q in kk} - pair
                    for c in sorted(others):
                        f1, f2 = atlas.facts.get((cls, frozenset([ka, c]))), atlas.facts.get((cls, frozenset([c, kb])))
                        if not f1 or not f2 or disputed(frozenset([ka, c])) or disputed(frozenset([c, kb])):
                            continue
                        v1, v2 = atlas.vec_of(ka, c), atlas.vec_of(c, kb)
                        if v1 and v2 and v1[0] * v2[0] + v1[1] * v2[1] >= .7:  # on the way
                            d = f1[0] + f2[0]
                            break
                        lo, hi = max(lo or 0, abs(f1[0] - f2[0])), min(hi or math.inf, f1[0] + f2[0])
                if d:
                    seen.add(pair)
                    t = hm(d / PACE_MPH["normal"]) if cls == LAND else hm(d / vessels()["rowboat"]) + " by rowboat"
                    lines.append(f"- {a} to {b}: {mi(d)} {how} ({t})")
                elif hi is not None and hi >= (lo or 0):
                    seen.add(pair)
                    lines.append(f"- {a} to {b}: no route recorded between these two, but the routes recorded put "
                                 f"them between {num(lo or 0)} and {mi(hi)} apart {how}")
    return lines


def ask(lore: dict[str, Any], transcript: list[dict[str, Any]], a: dict[str, Any]) -> str:
    """route with from and to: how far, and how long at each pace, without moving."""
    atlas = Atlas(lore, transcript)
    frm = a.get("from") or here(transcript)
    if not frm:
        raise Refused("from: where from? (no place is recorded for the party yet)")
    to = a["to"]
    out = []
    land, water = atlas.path(frm, to, LAND), atlas.path(frm, to, WATER)
    if not land and not water:
        return (f"No route from {atlas.name(atlas.key(frm))} to {atlas.name(atlas.key(to))} is recorded yet. "
                "When you say how far it is, record it with `route`.")
    for got, how in ((land, "by land"), (water, "by water")):
        if not got:
            continue
        d, via = got
        if d == 0:
            out.append(f"{to} is at {frm} (linked): no travel")
            continue
        line = f"{mi(d)} {how}" + (f" by way of {', '.join(via)}" if via else "")
        if how == "by land":
            line += ": on foot or riding, " + ", ".join(f"{p} pace {hm(d / mph)}" for p, mph in PACE_MPH.items())
        else:
            line += ": by rowboat " + hm(d / vessels()["rowboat"])
        out.append(line)
    return f"{atlas.name(atlas.key(frm))} to {atlas.name(atlas.key(to))}: " + "; ".join(out) + "."


def journey(lore: dict[str, Any], transcript: list[dict[str, Any]], a: dict[str, Any]) -> tuple[dict[str, Any], float, str]:
    """travel: the call as it's recorded (with `from`), the clock time it takes in seconds, and what happened."""
    a = dict(a)
    a["from"] = a.get("from") or here(transcript)
    if not a["from"]:
        raise Refused("from: where from? (no place is recorded for the party yet)")
    if not a.get("to"):
        raise Refused("to: where to?")
    mph = speed(a)
    per_day = day_hours(a)
    atlas = Atlas(lore, transcript)
    frm, to = atlas.name(atlas.key(a["from"])), atlas.name(atlas.key(a["to"]))
    flags = atlas.add_journey(a, notebook.now(transcript))
    got = atlas.path(a["from"], a["to"], WATER if a.get("by") == "boat" else LAND)
    if got is None:
        raise Refused(f"no route from {frm} to {to} is recorded"
                      + (" by water" if a.get("by") == "boat" else "")
                      + ": give miles, hours or days (or record the road with `route` first)")
    d, via = got
    if d == 0:
        return a, 0, f"{to} is at {frm} (linked): no travel time; the party is at {to}"
    hours = d / mph
    if a.get("forced_march") or hours <= per_day:
        clock_hours = hours
    else:  # 8 hours on the road, then the night until the same hour next morning
        clock_hours = hours + (24 - per_day) * (math.ceil(hours / per_day) - 1)
    how = {"foot": "on foot", "horse": "riding", "cart": "by cart", "boat": f"by {a.get('vessel') or 'rowboat'}"}[a.get("by") or "foot"]
    pace = "" if a.get("by") == "boat" else f" at a {a.get('pace') or 'normal'} pace"
    text = (f"{frm} to {to}: {mi(d)}" + (f" by way of {', '.join(via)}" if via else "") + f", {how}{pace}"
            + (" over difficult terrain" if a.get("difficult") else "") + f": {hm(hours)} of travel")
    if not a.get("forced_march") and hours > per_day:
        days = math.ceil(hours / per_day)
        text += f" over {days} days ({num(per_day)} hours a day, nights included)"
    if a.get("pace") == "gallop" and hours > 1:
        text += "; a gallop lasts about an hour (Mounts and Vehicles)"
    if a.get("forced_march") and hours > DAY_HOURS and a.get("by") != "boat":
        extra = math.ceil(hours - DAY_HOURS)
        text += (f". Forced March: each traveller makes a Constitution saving throw at the end of each hour past "
                 f"8: DC {', '.join(str(10 + i) for i in range(1, extra + 1))}; each failure is one level of exhaustion")
    if flags:
        text += ". The distance given doesn't fit the routes recorded: " + " ".join(flags)
    return a, clock_hours * 3600, text + f"; the party is at {to}"


def recorded_text(lore: dict[str, Any], transcript: list[dict[str, Any]], a: dict[str, Any]) -> str:
    """route with stops or links: what was recorded, and any clash with the routes before it."""
    if not (a.get("stops") or a.get("links")):
        if not a.get("to"):
            raise Refused("give stops (a road), links, or to (to ask how far)")
        return ask(lore, transcript, a)
    stops = a.get("stops") or []
    if len(stops) == 1:
        raise Refused("stops: at least two places, in the order the road runs")
    if len(a.get("legs") or []) > max(len(stops) - 1, 0):
        raise Refused("legs: one per gap between stops")
    for ln in a.get("links") or []:
        if not ln.get("a") or not ln.get("b") or ln.get("how") not in ("inside", "adjoining", "portal"):
            raise Refused("a link is {a, b, how: inside, adjoining or portal}")
    atlas = Atlas(lore, transcript)
    flags = atlas.add(a, notebook.now(transcript))
    parts = []
    if stops:
        parts.append("road " + " - ".join(stops))
    parts += [f"{ln['a']} {ln['how']} {ln['b']}" if ln["how"] != "inside" else f"{ln['a']} inside {ln['b']}"
              for ln in a.get("links") or []]
    missing = sorted({x for x in [*stops, *(v for ln in a.get("links") or [] for v in (ln["a"], ln["b"]))]
                      if not entry(lore, x)})
    text = "recorded: " + "; ".join(parts)
    if missing:
        text += ". Not in the notebook: " + ", ".join(missing) + " (add each as a place, or use its notebook name)"
    if flags:
        text += ". Doesn't fit what was recorded before: " + " ".join(flags)
    return text


# ---------- warnings ----------

PLACE_WORDS = ("chapel shrine temple church hill ford inn tavern mill keep hall village town landing causeway isle "
               "island barn hut cairn camp steading bridge mine shaft gate tower fort farm quay dock pass ledge weir "
               "manor abbey priory crossing lake marsh fen stones fold hollow lamp crypt barrow tomb gatehouse harbour "
               "harbor port market square well spring grove wood woods forest ridge peak cave cavern ruin ruins outpost "
               "hamlet city castle citadel monastery convent lodge cottage croft estate warehouse docks wharf "
               "lighthouse").split()
RECENT = 10  # a place word counts for a place named in the last 10 turns
NUMW = (r"(?:\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|forty|fifty|"
        r"sixty|a hundred|hundred|half an?|a quarter of an?|a couple of|a few|several|thirty-odd|twenty-five)")
UNIT = r"(?:miles?|leagues?|hours?|days?|minutes?)"
TRAVEL = re.compile(
    rf"\b{NUMW}(?:[\s-]+and a half)?[\s-]+{UNIT}\b(?:[\s-]+and a half)?['’]?s?\s+(?:walk|ride|march|road|journey|travel|"
    rf"sail|on foot|by|away|off|on|out|from|back|ahead|up|down|north|south|east|west|upriver|downriver|further|past|short)"
    rf"|\b{NUMW}[\s-]+miles?\b"
    rf"|\b(?:an?|one|half a|another|a long|a short|a hard|a slow|most of a)\s+(?:day|night|morning|afternoon|hour)['’]?s?"
    rf"\s+(?:hard\s+)?(?:walk|ride|march|descent|climb|sail|journey|road|travel)"
    rf"|\bshort (?:walk|climb|ride)\b|\bhalf a day\b|\bday and (?:a half|more)\b", re.I)
# a time that isn't a distance: a deadline, an age, a rest, a clock time
NOT_TRAVEL = re.compile(r"\b(after|o'clock|past (?:six|seven|eight|nine|ten|eleven|twelve|one|two|three|four|five)|sleep|"
                        r"rest|wait|dusk|dawn|bell|night is|dark is|assize|midwinter|deadline|left|ago|old|years?|"
                        r"hit points?|rounds?|slots?|until|by then|in time|gp|coins?)\b", re.I)
SHOWN = 10  # items of one kind listed in a message


def dismissed(transcript: list[dict[str, Any]]) -> set[str]:
    return {" ".join(str(x).split()).casefold() for e in transcript if _ok(e, "dismiss_warning")
            for x in e["input"].get("items") or []}


def _places(lore: dict[str, Any]) -> dict[str, str]:
    """Every name of every notebook place, normalised -> the entry's name."""
    return {norm(x): n for n, e in lore["entries"].items() if e["kind"].strip().casefold() == "place"
            for x in [n, *e["other_names"]]}


def _mentions(lore: dict[str, Any], transcript: list[dict[str, Any]], atlas: Atlas) -> Any:
    """Each distance or travel time in a reply next to a noted place (in its sentence or one of the two before it):
    (turn, sentence, the distance's words, the places named, where the party was, its key)."""
    noted = _places(lore)
    if not noted:
        return
    made = [i for i, e in enumerate(transcript) if e["kind"] == "call" and e.get("tool") == "finish_character"]
    start = made[-1] + 1 if made else 0
    names_re = re.compile(r"\b(" + "|".join(re.escape(x) for x in sorted(noted, key=len, reverse=True) if len(x) > 2)
                          + r")\b") if any(len(x) > 2 for x in noted) else None
    word_re = re.compile(r"\bthe\s+(?:[a-z][\w'’\-]*\s+){0,2}?(" + "|".join(PLACE_WORDS) + r")\b")
    by_word = {w: {n for x, n in noted.items() if re.search(r"\b" + w + r"\b", x)} for w in PLACE_WORDS}
    last_named: dict[str, int] = {}
    where: str | None = None
    for i_, (t, e) in enumerate(notebook.turns(transcript)):
        if i_ < start:
            continue
        if _ok(e, "place") and e["input"].get("place"):
            where = e["input"]["place"]
        elif _ok(e, "travel"):
            where = e["input"]["to"]
        if e["kind"] != "dm":
            continue

        def places_in(s: str) -> set[str]:
            got = {noted[m_.group(1)] for m_ in names_re.finditer(s.casefold())} if names_re else set()
            for n in got:
                last_named[n] = t
            for m_ in word_re.finditer(s):
                hits = by_word[m_.group(1)]
                if len(hits) == 1:
                    n = next(iter(hits))
                    if n in last_named and t - last_named[n] <= RECENT:
                        got.add(n)
            return got
        sents = [s for s in re.split(r"(?<=[.!?])\s+|\n+", e["text"]) if s.strip()]
        found = [places_in(s) for s in sents]  # names in this reply count as recent too
        hk = atlas.key(where) if where else None
        for i, s in enumerate(sents):
            m_ = TRAVEL.search(s)
            if not m_:
                continue
            clause = re.split(r"[,;:]", s[:m_.start()])[-1] + m_.group() + s[m_.end():m_.end() + 25]
            if NOT_TRAVEL.search(clause):
                continue
            ps: set[str] = set()
            for back in (0, 1, 2):
                if i - back >= 0:
                    ps = {p for p in found[i - back] if atlas.key(p) != hk}
                    if ps:
                        break
            if ps:
                yield t, s.strip(), m_.group(), ps, where, hk


def distances(lore: dict[str, Any], transcript: list[dict[str, Any]], atlas: Atlas) -> list[tuple[str, str]]:
    """A distance next to a noted place with no route recorded from that place to where the party was or to the
    other place named: (key, text)."""
    out: dict[str, str] = {}
    for t, s, _, ps, where, hk in _mentions(lore, transcript, atlas):
        ends = ps | ({where} if where else set())
        if all(any(atlas.recorded(p, q) for q in ends if q != p) for p in ps):
            continue
        k = f"turn {t}: " + ", ".join(sorted(ps))
        out.setdefault(k, f'"{s[:160]}"' + (f" (the party was at {where})" if where else ""))
    return list(out.items())


# reading an amount: a few phrases the patterns miss (the dry run's reader), in hours on foot
SPECIAL = [(r"hard night|night.s (hard )?(march|climb)", 8), (r"day and a half", 12), (r"two days? and a half", 20),
           (r"few hundred yards|short walk|four streets", .1), (r"long day", 10), (r"morning", 4), (r"day and more", 10),
           (r"half a day", 4), (r"a few hours", 3)]
NUM = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
       "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40,
       "half a": .5, "half an": .5, "quarter of a": .25, "a quarter": .25, "a quarter of a": .25, "quarter of an": .25,
       "a quarter of an": .25, "a couple of": 2, "a few": 3, "several": 3}
_N = (r"(?P<n>\d+(?:\.\d+)?|half an?|a quarter(?: of an?)?|quarter of an?|a couple of|a few|several|an?|one|two|three|"
      r"four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|forty)(?P<h>\s+and\s+a\s+half)?")
_MILES = re.compile(rf"\b{_N}[\s-]+(?P<u>miles?|leagues?)\b", re.I)
_TIME = re.compile(rf"\b{_N}[\s-]+(?P<u>hours?|minutes?|days?|nights?)\b", re.I)


def stated_miles(words: str) -> float | None:
    """The miles a distance's words give ("two hours" at a normal pace: 6), or None if they can't be read."""
    def n(m_: re.Match[str]) -> float:
        v = m_.group("n").lower()
        return (float(v) if v[0].isdigit() else NUM.get(v, 1)) + (.5 if m_.group("h") else 0)
    if m_ := _MILES.search(words):
        return n(m_) * (3 if m_.group("u").lower().startswith("league") else 1)
    for pat, h in SPECIAL:
        if re.search(pat, words, re.I):
            return h * PACE_MPH["normal"]
    if m_ := _TIME.search(words):
        u = m_.group("u").lower()
        return n(m_) * (DAY_HOURS if u[0] in "dn" else 1 / 60 if u.startswith("min") else 1) * PACE_MPH["normal"]
    return None


def restated(lore: dict[str, Any], transcript: list[dict[str, Any]], atlas: Atlas) -> list[str]:
    """In the last reply, a distance next to a place with a route recorded that's more than 25% off it (as the
    ALONG check). Asked once: the reply has gone to the player, so the DM can only correct the record or the story
    from here."""
    out: list[str] = []
    last = notebook.now(transcript) - 1
    for t, s, words, ps, where, hk in _mentions(lore, transcript, atlas):
        said = stated_miles(words)
        if t != last or said is None:
            continue
        for p in sorted(ps):
            for q in sorted(ps | ({where} if where else set())):
                if q == p or not atlas.recorded(p, q):
                    continue
                got = atlas.path(p, q) or atlas.path(p, q, WATER)
                if got and abs(said - got[0]) > .25 * max(said, got[0]) and abs(said - got[0]) > .5:
                    line = (f'"{s[:160]}": if that is {p} to {entry(lore, q) or q}, '
                            f"the recorded route is {mi(got[0])} ({hm(got[0] / PACE_MPH['normal'])} on foot), "
                            f"and \"{words}\" is about {mi(said)} at a normal pace")
                    if line not in out:
                        out.append(line)
    return out


def moves(atlas: Atlas, transcript: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """Each change of the party's place that wasn't a journey, between places with no route or link recorded."""
    out: dict[str, str] = {}
    pos = positions(transcript)
    for (_, _, x, _), (_, t, y, by_travel) in zip(pos, pos[1:]):
        if by_travel or atlas.key(x) == atlas.key(y) or atlas.connected(x, y):
            continue
        nx, ny = entry(atlas.lore, x) or x, entry(atlas.lore, y) or y
        out.setdefault(f"{nx} -> {ny}", f"turn {t}")
    return list(out.items())


def unnoted(lore: dict[str, Any], transcript: list[dict[str, Any]], atlas: Atlas) -> list[str]:
    """Places the party has been, and route stops, that aren't in the notebook."""
    out: list[str] = []
    for x in [p for _, _, p, _ in positions(transcript)] + atlas.stops:
        x = " ".join(str(x).split())
        if x and not entry(lore, x) and norm(x) not in {norm(o) for o in out}:
            out.append(x)
    return out


def contained(lore: dict[str, Any], transcript: list[dict[str, Any]], atlas: Atlas) -> list[tuple[str, str]]:
    """Two places, one's name inside the other's (Greyshaft lowest gate, Greyshaft), not linked: (inner, outer)."""
    names: dict[str, str] = {}
    for x, n in _places(lore).items():
        names.setdefault(x, n)
    for x in [p for _, _, p, _ in positions(transcript)] + atlas.stops:
        names.setdefault(norm(x), entry(lore, x) or " ".join(str(x).split()))
    out = []
    for a, na in names.items():
        for b, nb in names.items():
            if na != nb and len(b) > 3 and re.search(r"\b" + re.escape(b) + r"\b", a) \
                    and atlas.key(na) != atlas.key(nb) and (na, nb) not in out:
                out.append((na, nb))
    return out


def new_places(lore: dict[str, Any], transcript: list[dict[str, Any]], atlas: Atlas) -> list[str]:
    """Place entries made in the last turn (before the player's newest line) that aren't linked to anything yet."""
    t_now = notebook.now(transcript)
    linked = {atlas.key(x) for ln in atlas.links for x in ln}
    out = []
    for t, e in notebook.turns(transcript):
        if t == t_now - 1 and _ok(e, "write_lore") and e["input"].get("create") \
                and str(e["input"].get("kind", "")).strip().casefold() == "place":
            n = notebook.find(lore, e["input"]["create"])
            if n and atlas.key(n) not in linked and n not in out:
                out.append(n)
    return out


def warning(lore: dict[str, Any], transcript: list[dict[str, Any]]) -> str:
    """The warnings for this turn, or "" if there are none."""
    atlas = Atlas(lore, transcript)
    gone = dismissed(transcript)
    keep = lambda k: " ".join(k.split()).casefold() not in gone  # noqa: E731
    parts = []

    def section(head: str, items: list[str], tail: str) -> None:
        if items:
            more = f" (and {len(items) - SHOWN} more)" if len(items) > SHOWN else ""
            parts.append(f"[{head}] " + tail + "\n" + "\n".join(f"- {x}" for x in items[-SHOWN:]) + more)

    section("Routes that don't fit", [f'"{k}": {v}' for k, v in atlas.flags if keep(k)],
            "These routes you recorded don't fit the ones recorded before them. Correct the record that's wrong "
            "(record that road again with the right distance and `correct`), or dismiss one with `dismiss_warning`, "
            "by the name in quotes, if it isn't a clash.")
    section("Places not in your notebook", [f'"{x}"' for x in unnoted(lore, transcript, atlas) if keep(x)],
            "The party's place or a route names these, which are no entry's name or other name. Add each as a place, "
            "or give its notebook name (`add_other_names` if it's another name for an entry).")
    section("Moves with no route", [f'"{k}" ({v})' for k, v in moves(atlas, transcript) if keep(k)],
            "The party's place changed between these with no travel, and no route or link between them is recorded. "
            "Record the route (with its distance, if you've said it), or the link (inside, adjoining, portal).")
    section("Distances with no route", [f'"{k}": {v}' for k, v in distances(lore, transcript, atlas) if keep(k)],
            "Your replies gave these distances or travel times with no route recorded for them. Record each with "
            "`route`, or dismiss it.")
    section("Places inside places?", [f'"{a} / {b}"' for a, b in contained(lore, transcript, atlas) if keep(f"{a} / {b}")],
            "One's name is inside the other's. If the first is inside, or right at, the second, link them with "
            "`route` (inside or adjoining); if not, dismiss it.")
    section("Distances off the records", restated(lore, transcript, atlas),
            "Your last reply gave these distances, which are more than a quarter off the routes recorded. If the "
            "reply was wrong, keep to the record from now on; if the record was wrong, record that road again with "
            "the right distance and `correct`. If the number wasn't about those two places, leave it.")
    if fresh := new_places(lore, transcript, atlas):
        parts.append("[New places] Is any of these inside, or right at, a place already in your notebook (an inn in a "
                     "town, a cairn in a pass)? If so, link them with `route`: " + ", ".join(fresh) + ".")
    return "\n".join(parts)
