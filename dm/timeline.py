"""Dates and the timeline (Jake, 2026-10-31): a fixed calendar on the clock, time facts the DM records, a warning that
prompts them, and what the continuity checker reads about time.

Of the 118 contradictions in the second autoloop set, 29 were about time: day counts and dates ("eleven days since the
oath" on Day 16 for an oath sworn on Day 2), the time of day, and ages and how long ago. The dry run
(kaeris-opening/calendar-dry-run.md), with Sonnet recording the timeline as the DM would, had the checker catch 6 of
the 29 per run with the clock and the timeline before it, and 8 with time acted on at a score of 3, against 2 to 5
without; one new time flag, judged false.

- **Calendar.** Fixed: 12 months of 30 days. The DM says once which date a day is (`change_time` set with `date`),
  and the time line then names the date of each day.
- **Records.** The DM records a time fact with `timeline` (what, the names it's about, and when: a game day, a date, a
  number of days from today, years ago, or a person's age). Code turns each into a game day, and does the sums when
  it's shown: "the oath (Day 2, 14 days ago)". `timeline` with `find` lists the facts about some names.
- **Warning.** A sentence of the last reply that states a time fact (an age, how long ago or for, days to come, a
  calendar word, a date), when the DM recorded nothing with `timeline` that turn. The patterns were written from plain
  English before the dry run was scored; in 540 rounds they fired in 171, and would have prompted the first statement
  of 13 of the 22 clashes whose first statement came in an earlier reply.
- **Checker.** The clock at the end of each turn it reads and at the new reply, and the recorded facts about the
  names the new reply uses (ages, years ago and days to come first; none of today's that have already happened).

Nothing is stored apart from the calls: the records are the DM's `timeline` calls in the transcript, as the routes
are. The code only does sums and flags; the DM decides."""

from __future__ import annotations

import re
from typing import Any

from dm import lore as notebook
from dm.mechanics import (
    DAY,
    MONTH_DAYS,
    MONTHS,
    YEAR_DAYS,
    Refused,
    calendar_day,
    date_text,
    when,
)

SHOWN = 15  # facts in the checker's TIMELINE block


# ---------- dates ----------

def day_of(c: dict[str, Any], d: dict[str, Any]) -> int:
    """The game day of a date {day, month?, year?}; month and year are this month's and year's unless given."""
    if c.get("start") is None:
        raise Refused("no date is set: give day (the game day), or set the date with change_time first")
    today = c["now"] // DAY + 1
    y, rest = divmod(c["start"] + today - 1, YEAR_DAYS)
    full = {"day": d.get("day"), "month": d.get("month") or MONTHS[rest // MONTH_DAYS],
            "year": d.get("year") if d.get("year") is not None else y}
    return calendar_day(full) - c["start"] + 1


# ---------- records ----------

def _ok(e: dict[str, Any]) -> bool:
    return e["kind"] == "call" and e.get("tool") == "timeline" and not e.get("error") and bool(e["input"].get("what"))


def records(transcript: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any]]]:
    """(turn, record) for each fact recorded, in order."""
    return [(t, e["input"]) for t, e in notebook.turns(transcript) if _ok(e)]


def resolve(c: dict[str, Any], a: dict[str, Any]) -> dict[str, Any]:
    """A timeline call's input as it is recorded: what, names, and when as a game day (`day`, which for years ago or an
    age is a day years back, maybe below 1), `exact` (a day, or only a year), `time`, and `age` for an age. Raises
    Refused."""
    what = " ".join(str(a.get("what") or "").split())
    names = [" ".join(str(n).split()) for n in a.get("names") or [] if str(n).strip()]
    if not what:
        raise Refused("what: what happened, or whose age")
    if not names:
        raise Refused("names: the people, places or things it's about, by their notebook names")
    whens = [k for k in ("day", "date", "days_from_today", "years_ago", "age") if a.get(k) is not None]
    if len(whens) != 1:
        raise Refused("give one of day, date, days_from_today, years_ago or age")
    if c["now"] is None:
        raise Refused("the clock isn't set: set it with change_time first")
    today = c["now"] // DAY + 1
    k, v = whens[0], a[whens[0]]
    out: dict[str, Any] = {"what": what, "names": names}
    if k == "day":
        if not isinstance(v, int):
            raise Refused("day: a game day number")
        out |= {"day": v, "exact": True}
    elif k == "date":
        out |= {"day": day_of(c, v if isinstance(v, dict) else {}), "exact": True}
    elif k == "days_from_today":
        if not isinstance(v, int):
            raise Refused("days_from_today: a whole number, below 0 for days ago")
        out |= {"day": today + v, "exact": True}
    else:
        if not isinstance(v, int | float) or v < 0:
            raise Refused(f"{k}: a number of years, 0 or more")
        out |= {"day": today - round(v * YEAR_DAYS), "exact": False} | ({"age": True} if k == "age" else {})
    if t := " ".join(str(a.get("time") or "").split()):
        out["time"] = t
    return out


def fact(c: dict[str, Any], r: dict[str, Any], now: int) -> str:
    """One fact with the sums done as of `now` (seconds): 'the oath (Day 2, the 2nd of Thaw, 1492; 14 days ago)'."""
    today = now // DAY + 1
    if not r["exact"]:
        yrs = round((today - r["day"]) / YEAR_DAYS)
        if r.get("age"):
            return f"{r['what']} ({yrs} years old now)"
        return f"{r['what']} (about {yrs} year{'s' if yrs != 1 else ''} ago)" if yrs else f"{r['what']} (this year)"
    n = r["day"] - today
    rel = "today" if n == 0 else "yesterday" if n == -1 else "tomorrow" if n == 1 else (
        f"{-n} days ago" if n < 0 else f"in {n} days")
    date = date_text(c, r["day"])
    return f"{r['what']} (Day {r['day']}" + (f", {date}" if date else "") + (f", {r['time']}" if r.get("time") else "") \
        + f"; {rel})"


def _words(names: list[str], party: tuple[str, ...]) -> list[str]:
    """A fact's names, and each capitalised word of them ("Gorrak" for "Gorrak Vael"), but not the party's own names,
    which nearly every reply uses."""
    own = {w.casefold() for p in party for w in p.split()} | {p.casefold() for p in party}
    out = []
    for n in names:
        n = re.sub(r"^the\s+", "", n, flags=re.I)
        out += [w for w in [n, *re.findall(r"\b[A-Z][a-z']{3,}\b", n)] if w.casefold() not in own and len(w) > 3]
    return out


def _named(words: list[str], text: str) -> bool:
    return any(re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", text, re.I) for w in words)


def find(c: dict[str, Any], transcript: list[dict[str, Any]], names: list[str]) -> str:
    """`timeline` with find: every fact recorded about those names, with the sums done."""
    want = {re.sub(r"^the\s+", "", n.strip(), flags=re.I).casefold() for n in names if n.strip()}
    got = [r for _, r in records(transcript)
           if want & {re.sub(r"^the\s+", "", n, flags=re.I).casefold() for n in r["names"]}]
    if not got:
        return "Nothing is recorded on the timeline about " + ", ".join(names) + "."
    return "\n".join(f"- {fact(c, r, c['now'])}" for r in got)


def recorded_text(c: dict[str, Any], transcript: list[dict[str, Any]], a: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """A timeline call: (the input as recorded, what the DM is told). Raises Refused."""
    if a.get("find"):
        if a.get("what"):
            raise Refused("find or what, not both")
        return a, find(c, transcript, list(a["find"]))
    r = resolve(c, a)
    return r, "recorded: " + fact(c, r, c["now"])


# ---------- the warning ----------

NUM = (r"(?:\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|"
       r"sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|a hundred|"
       r"a few|a couple of|several|half a|a dozen|many|some)(?:[- ](?:one|two|three|four|five|six|seven|eight|nine))?"
       r"(?: and a half)?")
UNIT = r"(?:days?|nights?|weeks?|fortnights?|months?|moons?|seasons?|years?|winters?|summers?|springs?|autumns?|harvests?)"
SPAN = rf"\b{NUM}\s+{UNIT}\b"
ORD = (r"(?:\d{1,2}(?:st|nd|rd|th)|eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|"
       r"eighteenth|nineteenth|twentieth|twenty-\w+|thirtieth|thirty-first)")
# The dry run's patterns as they were frozen before scoring: an age, how long ago or for, days to come, a relative
# calendar word, a date.
PATTERNS = [re.compile(p, re.I) for p in [
    rf"\b{NUM}\s+years?\s+old\b", rf"\b(?:aged|at the age of|at age)\s+{NUM}\b", rf"\b{NUM}[- ]year[- ]old\b",
    rf"{SPAN}\s+(?:ago|since|before|back|earlier|past)\b", rf"\b(?:for|in|these|the last|the past)\s+{SPAN}",
    rf"{SPAN}\s+(?:later|after|on)\b",
    rf"\b(?:in|within)\s+{SPAN}", rf"{SPAN}\s+(?:off|away|from now|hence|out|yet|left|more)\b",
    r"\b(?:last|next|this|that)\s+(?:week|month|year|spring|summer|autumn|fall|winter|season|harvest|midwinter|midsummer)\b",
    r"\b(?:yesterday|tomorrow|the day before yesterday|the day after tomorrow)\b",
    rf"\bthe\s+{ORD}\b", r"\bDay\s+\d+\b"]]


def stated(text: str, today: int | None) -> list[tuple[str, str]]:
    """(the time words, the sentence) for each sentence of `text` that states a time fact; "Day N" for today is the
    clock, not a fact."""
    out = []
    for s in re.split(r"(?<=[.!?\"”])\s+|\n+", text):
        for p in PATTERNS:
            if (m_ := p.search(s)) and not ((d := re.fullmatch(r"Day\s+(\d+)", m_.group(), re.I)) and int(d[1]) == today):
                out.append((m_.group(), s.strip()))
                break
    return out


def warning(transcript: list[dict[str, Any]], dismissed: set[str]) -> str:
    """The time facts the DM's last reply stated with nothing recorded with `timeline` that turn, or ""."""
    players = [i for i, e in enumerate(transcript) if e["kind"] == "player"]
    if not players:
        return ""
    last = transcript[players[-2] if len(players) > 1 else 0:players[-1]]
    if any(_ok(e) for e in last):
        return ""
    at = [e["at"] for e in transcript[:players[-1]] if e["kind"] == "clock"]
    today = at[-1] // DAY + 1 if at else None
    reply = "\n".join(e["text"] for e in last if e["kind"] == "dm")
    items = [(w, s) for w, s in stated(reply, today) if " ".join(s[:160].split()).casefold() not in dismissed]
    if not items:
        return ""
    return ("[Time facts not on the timeline] Your last reply said these, and you recorded nothing with `timeline`. "
            "Record each one later replies could contradict (a date, a day count, how long ago, an age), or dismiss "
            "the rest with `dismiss_warning`, by the sentence in quotes:\n"
            + "\n".join(f'- {w}: "{" ".join(s[:160].split())}"' for w, s in items))


# ---------- for the continuity checker ----------

HOURS = [(r"midnight", 0), (r"dawn|sunrise|first light", 6), (r"morning", 9), (r"noon|midday", 12), (r"afternoon", 15),
         (r"dusk|sunset|evening", 18), (r"night", 21)]


def hour(t: str | None) -> float | None:
    """The hour a time of day gives ("5:30 PM", "17:30", "dusk"), or None."""
    if not t:
        return None
    if m_ := re.search(r"(\d{1,2})(?::(\d\d))?\s*([AaPp])\.?[Mm]", t):
        return int(m_[1]) % 12 + (12 if m_[3].lower() == "p" else 0) + int(m_[2] or 0) / 60
    if m_ := re.fullmatch(r"(\d{1,2}):(\d\d)", t.strip()):
        return int(m_[1]) + int(m_[2]) / 60
    return next((v for p, v in HOURS if re.search(p, t, re.I)), None)


def clock_at(transcript: list[dict[str, Any]]) -> list[tuple[int, int]]:
    """(turn, the clock when it ended) for each turn after the clock was first set, from the game's clock notes."""
    out: dict[int, int] = {}
    now = None
    for t, e in notebook.turns(transcript):
        if e["kind"] == "clock":
            now = e["at"]
        if now is not None:
            out[t] = now
    return sorted(out.items())


def time_lines(transcript: list[dict[str, Any]], first: int, turn: int) -> str:
    """The TIME block: the clock at the end of turns first..turn-1 and at the new reply (the end of `turn`)."""
    at = dict(clock_at(transcript))
    lines = [f"Turn {n}: {when(at[n])}" for n in range(first, turn) if n in at]
    if turn in at:
        lines.append(f"New reply: {when(at[turn])}")
    return "\n".join(lines)


def for_checker(c: dict[str, Any], before: list[dict[str, Any]], reply: str, now: int | None,
                party: tuple[str, ...] = ()) -> list[str]:
    """The facts recorded before this turn about the names the reply uses: ages, years ago and days to come first,
    then the latest others, SHOWN at most; today's that have already happened are left out (the clock covers them,
    and in the dry run they crowded out older facts)."""
    if now is None:
        return []
    today, hr = now // DAY + 1, (now % DAY) / 3600
    first, rest = [], []
    for i, (_, r) in enumerate(records(before)):
        if not _named(_words(r["names"], party), reply):
            continue
        if r["exact"] and r["day"] == today and (h := hour(r.get("time"))) is not None and h <= hr:
            continue
        (first if not r["exact"] or r["day"] >= today else rest).append((i, r))
    first = first[-SHOWN:]
    keep = sorted(first + rest[-(SHOWN - len(first)):] if len(first) < SHOWN else first, key=lambda x: x[0])
    return [f"- {fact(c, r, now)}" for _, r in keep]
