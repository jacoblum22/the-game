"""The DM's notebook (owner, 2026-10-13): what the DM has said about the world, so it can be found again.

An entry is a person, place, group, item, event... with a kind (free text), other names, a description (parts, each
stamped with the turn it was written) and relationships: bullet lines, each stored once and shown on every entry it
mentions ([[links]] or plain names alike). The code only stores, finds and shows; the DM decides what goes in.
The player never sees the notebook.

A turn is a player's line and everything after it, up to the next one; turn 0 is the opening. The DM sees the turn
number in its status, so the numbers mean the same everywhere."""

from __future__ import annotations

import copy
import difflib
import re
from typing import Any

from dm.mechanics import Refused

LINK = re.compile(r"\[\[([^\]]+)\]\]")
PAGE = 10  # lines a lookup shows at once
PATHS = 5  # two-step connections shown
NOTES = 10  # lines of notes each turn
SKIP = 3  # an entry shown in the last 3 turns isn't shown again
ANSWER, ANSWER_CHARS = 4, 1500  # entries a write answers with, and the characters of each
SNIP = 160  # characters either side of a match in recall
TASKS = ("quest", "lead")  # kinds shown every turn while open (owner, 2026-10-13)
STATUSES = ("open", "done", "dropped")


def new() -> dict[str, Any]:
    return {"entries": {}, "relationships": [], "next_id": 1, "shown": {}}


# ---------- names ----------

def _key(s: Any) -> str:
    return " ".join(str(s).split()).casefold()


def _names(lore: dict[str, Any], n: str) -> list[str]:
    return [n, *lore["entries"][n]["other_names"]]


def find(lore: dict[str, Any], name: Any) -> str | None:
    """The entry called `name`, by its name or one of its other names (any capitals)."""
    k = _key(name)
    return next((n for n in lore["entries"] if k in {_key(x) for x in _names(lore, n)}), None)


# Small joining words match in any capitals; a name's other capitalised words must be capitalised in the text too
# (owner, 2026-10-13: the dog Lamp isn't every lamp; "the Butcher of Blackshire" is "The Butcher of Blackshire").
SMALL = {"the", "of", "a", "an", "and", "in", "on", "at", "to", "for", "from", "by", "with"}


def _word(w: str) -> str:
    if w[:1].isupper() and w.casefold() not in SMALL:
        return re.escape(w[0]) + "(?i:" + re.escape(w[1:]) + ")"  # "LAMP" is still Lamp
    return "(?i:" + re.escape(w) + ")"


def _pattern(names: list[str], capitals: bool = True) -> re.Pattern[str]:
    """Any of the names as whole words ("Brakka's" counts as Brakka). capitals=False: any capitals (a keyword)."""
    alts = sorted({r"\s+".join((_word(w) if capitals else re.escape(w)) for w in x.split()) for x in names if x.split()},
                  key=len, reverse=True)
    return re.compile(r"(?<!\w)(?:" + "|".join(alts) + r")(?!\w)", 0 if capitals else re.IGNORECASE)


def _patterns(lore: dict[str, Any]) -> dict[str, re.Pattern[str]]:
    return {n: _pattern(_names(lore, n)) for n in lore["entries"]}


def _spans(text: str, pats: dict[str, re.Pattern[str]]) -> list[tuple[int, int, str]]:
    """Where `text` names entries. The longest name wins: "Anvil Father" is the god, not also Anvil the mule."""
    found = sorted(((m_.start(), m_.end(), n) for n, p in pats.items() for m_ in p.finditer(text)),
                   key=lambda s: (s[0] - s[1], s[0]))
    kept: list[tuple[int, int, str]] = []
    for s in found:
        if all(s[1] <= k[0] or s[0] >= k[1] for k in kept):
            kept.append(s)
    return sorted(kept)


def mentioned(lore: dict[str, Any], text: str, pats: dict[str, re.Pattern[str]] | None = None) -> list[str]:
    """The entries `text` mentions, linked or not."""
    got = {n for _, _, n in _spans(text, _patterns(lore) if pats is None else pats)}
    return [n for n in lore["entries"] if n in got]


def close(lore: dict[str, Any], name: str) -> list[str]:
    """Entries whose names share a word with `name`, contain it, or are spelt nearly the same: for a name not found."""
    words = {w for w in re.findall(r"\w+", _key(name)) if len(w) > 2}
    out = []
    for n in lore["entries"]:
        keys = [_key(x) for x in _names(lore, n)]
        if any(_key(name) in k or k in _key(name) or words & set(re.findall(r"\w+", k))
               or difflib.SequenceMatcher(None, _key(name), k).ratio() >= 0.8 for k in keys):
            out.append(n)
    return out[:PAGE]


def _task(e: dict[str, Any]) -> bool:
    return e["kind"].strip().casefold() in TASKS


def _short(lore: dict[str, Any], n: str) -> str:
    e = lore["entries"][n]
    text = " ".join(p["text"] for p in e["description"])
    return f"{n} ({e['kind']}): " + (text if len(text) <= SNIP else text[:SNIP].rsplit(" ", 1)[0] + "…")


def _not_found(lore: dict[str, Any], name: str) -> str:
    near = close(lore, name)
    # and entries whose description has the name in it: someone entered before their name was known (owner, 2026-10-13)
    word = re.compile(rf"(?<!\w){re.escape(' '.join(name.split()))}(?!\w)", re.IGNORECASE)
    says = [n for n in lore["entries"] if n not in near
            and word.search(" ".join(p["text"] for p in lore["entries"][n]["description"]))][:PAGE]
    return (f"no entry {name!r}" + (": close matches:\n" + "\n".join(_short(lore, n) for n in near) if near else "")
            + ("\nentries whose description mentions it:\n" + "\n".join(_short(lore, n) for n in says) if says else ""))


# ---------- facts: relationship lines and description parts, with the entries each one involves ----------

def _facts(lore: dict[str, Any]) -> list[dict[str, Any]]:
    pats = _patterns(lore)
    out = []
    for r in lore["relationships"]:
        out.append({"text": f"[{r['id']}] {r['from']}: {r['text']}", "turn": r["turn"], "order": r["id"], "rel": r,
                    "involves": {r["from"], *mentioned(lore, r["text"], pats)}})
    for n, e in lore["entries"].items():
        for i, p in enumerate(e["description"]):
            out.append({"text": f"{n} (description): {p['text']}", "turn": p["turn"], "order": -i, "rel": None,
                        "involves": {n, *mentioned(lore, p["text"], pats)}})
    return out


def _newest(f: dict[str, Any]) -> tuple[int, int]:
    return (-f["turn"], -f["order"])


# ---------- the transcript, by turns ----------

def turns(transcript: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any]]]:
    """(turn, item) for each item of the transcript."""
    out, t = [], 0
    for e in transcript:
        if e["kind"] == "player":
            t += 1
        out.append((t, e))
    return out


def now(transcript: list[dict[str, Any]]) -> int:
    return sum(e["kind"] == "player" for e in transcript)


def turn_text(transcript: list[dict[str, Any]], turn: int) -> str:
    """One turn word for word as the player saw it (their line, the DM's text, the tool lines), or "" if none."""
    items = [e for t, e in turns(transcript) if t == turn and e["kind"] in ("player", "dm", "tool")]
    return f"Turn {turn}:\n" + "\n".join({"player": "Player: ", "dm": "DM: ", "tool": "["}[e["kind"]] + e["text"]
                                         + ("]" if e["kind"] == "tool" else "") for e in items) if items else ""


def recent_text(transcript: list[dict[str, Any]]) -> str:
    """The DM's last reply before the player's newest line, that line, and what the DM has said since."""
    said = [(t, e) for t, e in turns(transcript) if e["kind"] in ("player", "dm")]
    t = now(transcript)
    return "\n".join(e["text"] for tt, e in said if tt >= t - 1 and not (tt == t - 1 and e["kind"] == "player"))


# ---------- writing ----------

def write(lore: dict[str, Any], a: dict[str, Any], turn: int) -> tuple[dict[str, Any], str]:
    """One write_lore call. All-or-nothing: returns (new notebook, what changed), or raises Refused."""
    lore = copy.deepcopy(lore)
    ents, out = lore["entries"], []

    def text(v: Any, what: str) -> str:
        v = str(v or "").strip()
        if not v:
            raise Refused(f"{what} is missing or empty")
        return v

    def free(name: str, but: str | None = None) -> None:
        n = find(lore, name)
        if n and n != but:
            raise Refused(f"{name!r} is already " + ("an entry" if _key(n) == _key(name) else f"another name of {n}")
                          + ": use that entry, or merge the two")

    def entry(name: Any) -> str:
        n = find(lore, name)
        if not n:
            raise Refused(_not_found(lore, str(name)))
        return n

    def relationships(n: str, lines: list[Any]) -> None:
        for x in lines:
            r = {"id": lore["next_id"], "from": n, "text": text(x, "a relationship"), "turn": turn}
            lore["next_id"] += 1
            lore["relationships"].append(r)
            out.append(f"relationship [{r['id']}] added to {n}")

    if a.get("create") and a.get("entry"):
        raise Refused("create a new entry, or change an existing one (entry), not both in one call")
    target = None
    if a.get("create"):
        name = " ".join(text(a["create"], "create").split())
        free(name)
        others = [" ".join(text(x, "an other name").split()) for x in a.get("other_names") or []]
        for o in others:
            free(o)
        if len({_key(x) for x in [name, *others]}) < 1 + len(others):
            raise Refused("the name and other names must all differ")
        ents[name] = {"kind": text(a.get("kind"), "kind (e.g. person, place, group)"), "other_names": others,
                      "description": [{"text": text(a.get("description"), "description"), "turn": turn}]}
        out.append(f"entry {name} ({ents[name]['kind']}) created")
        target = name
    elif a.get("entry"):
        target = entry(a["entry"])
    elif any(a.get(k) for k in ("kind", "description", "add_to_description", "add_relationships", "relationships",
                                "add_other_names", "remove_other_names", "rename", "other_names", "status")):
        raise Refused("say which entry: entry (an existing one) or create (a new one)")
    if target:
        e = ents[target]
        if a.get("entry"):
            if a.get("kind"):
                e["kind"] = text(a["kind"], "kind")
                out.append(f"{target} is now a {e['kind']}")
            if a.get("description"):
                e["description"] = [{"text": text(a["description"], "description"), "turn": turn}]
                out.append(f"{target}'s description rewritten")
            if a.get("add_to_description"):
                e["description"].append({"text": text(a["add_to_description"], "add_to_description"), "turn": turn})
                out.append(f"added to {target}'s description")
            for o in a.get("add_other_names") or []:
                o = " ".join(text(o, "an other name").split())
                free(o)
                e["other_names"].append(o)
                out.append(f"{target} is also called {o}")
            for o in a.get("remove_other_names") or []:
                keep = [x for x in e["other_names"] if _key(x) != _key(o)]
                if len(keep) == len(e["other_names"]):
                    raise Refused(f"{o!r} isn't one of {target}'s other names: " + (", ".join(e["other_names"]) or "none"))
                e["other_names"] = keep
                out.append(f"{o} is no longer a name of {target}")
        if a.get("status"):
            if a["status"] not in STATUSES:
                raise Refused(f"status: one of {', '.join(STATUSES)}")
            if not _task(e):
                raise Refused(f"status is for a quest or a lead; {target} is a {e['kind']}")
            e["status"] = a["status"]
            out.append(f"{target} is now {a['status']}")
        relationships(target, [*(a.get("relationships") or []), *(a.get("add_relationships") or [])])
        if a.get("rename"):
            new_name = " ".join(text(a["rename"], "rename").split())
            free(new_name, but=target)
            e["other_names"] = [x for x in e["other_names"] if _key(x) != _key(new_name)] + [target]
            lore["entries"] = ents = {(new_name if n == target else n): v for n, v in ents.items()}
            for r in lore["relationships"]:
                if r["from"] == target:
                    r["from"] = new_name
            if target in lore["shown"]:
                lore["shown"][new_name] = lore["shown"].pop(target)
            out.append(f"{target} renamed {new_name} ({target} stays as an other name, so links to it still work)")

    if (rid := a.get("change_relationship")) is not None or (rid := a.get("remove_relationship")) is not None:
        r = next((r for r in lore["relationships"] if r["id"] == rid), None)
        if not r:
            raise Refused(f"no relationship [{rid}]")
        if a.get("change_relationship") is not None:
            r["text"], r["turn"] = text(a.get("text"), "text (the relationship's new wording)"), turn
            out.append(f"relationship [{rid}] rewritten")
        else:
            lore["relationships"].remove(r)
            out.append(f"relationship [{rid}] removed")
    if a.get("merge"):
        src, dst = entry(a["merge"]), entry(a.get("into"))
        if src == dst:
            raise Refused(f"{a['merge']!r} and {a.get('into')!r} are the same entry")
        d, s = ents[dst], ents.pop(src)
        d["other_names"] += [x for x in [src, *s["other_names"]] if _key(x) not in {_key(y) for y in d["other_names"]}]
        d["description"] += s["description"]
        for r in lore["relationships"]:
            if r["from"] == src:
                r["from"] = dst
        lore["shown"].pop(src, None)
        out.append(f"{src} merged into {dst}: its description and relationships moved, its names are now other names")

    if not out:
        raise Refused("nothing to write: pass create, entry (with what changes), change_relationship, "
                      "remove_relationship, or merge")
    new_text = " ".join(str(v) for k in ("description", "add_to_description", "text") for v in [a.get(k)] if v)
    new_text += " ".join(str(x) for k in ("relationships", "add_relationships") for x in a.get(k) or [])
    missing = sorted({m_.strip() for m_ in LINK.findall(new_text) if not find(lore, m_)})
    if missing:
        out.append("no entry yet for " + ", ".join(missing) + " (create one if it matters)")
    return lore, "; ".join(out)


def answer(before: dict[str, Any], a: dict[str, Any], transcript: list[dict[str, Any]], skip: set[str]) -> tuple[str, list[str]]:
    """What the notebook already said, before this write, about the entry written and the entries its new text names:
    the DM writes its notes before its reply, so this puts what's established in front of it as it's about to narrate
    the new thing (owner, 2026-10-18; 108 of 118 contradictions in set 2 had the fact in the conversation and were
    missed anyway). `skip`: entries not to show (the party's, and those already shown this turn). Returns (the text,
    the entries shown)."""
    new_text = " ".join(str(v) for k in ("description", "add_to_description", "text") for v in [a.get(k)] if v)
    new_text += " " + " ".join(str(x) for k in ("relationships", "add_relationships") for x in a.get(k) or [])
    names = [a.get("entry"), a.get("into"), a.get("merge"), *LINK.findall(new_text)]
    found = [n for x in names if x and (n := find(before, x))]
    found += mentioned(before, new_text)
    out, shown_ = [], []
    for n in dict.fromkeys(found):
        if n in skip or len(shown_) == ANSWER:
            continue
        text = look(before, [n], transcript)
        out.append(text if len(text) <= ANSWER_CHARS else text[:ANSWER_CHARS].rsplit("\n", 1)[0] + "\n…")
        shown_.append(n)
    if not out:
        return "", []
    return ("[What your notebook already said about these, before this write: make what you write and narrate fit "
            "it, or say plainly what changed and why]\n" + "\n\n".join(out)), shown_


def shown(lore: dict[str, Any], a: dict[str, Any]) -> str:
    """What the player sees of a write that went through (owner, 2026-10-13): which entries changed, never what was
    written. `lore` is the notebook after the write."""
    def n(name: Any) -> str:
        return find(lore, name) or str(name)
    rels = len(a.get("relationships") or []) + len(a.get("add_relationships") or [])
    out = []
    if a.get("create"):
        out.append(f"created an entry for {n(a['create'])}")
    elif a.get("entry"):
        e = n(a["entry"])
        if a.get("rename"):
            out.append(f"renamed {a['entry']} to {e}")
        if any(a.get(k) for k in ("kind", "description", "add_to_description", "add_other_names", "remove_other_names", "status")):
            out.append(f"updated {e}")
    if rels:
        out.append(f"added {rels} relationship{'s' if rels > 1 else ''} to {n(a.get('create') or a.get('entry'))}")
    if a.get("change_relationship") is not None:
        out.append("changed a relationship")
    if a.get("remove_relationship") is not None:
        out.append("removed a relationship")
    if a.get("merge"):
        out.append(f"merged {a['merge']} into {n(a.get('into'))}")
    return "notebook: " + "; ".join(out)


# ---------- looking up ----------

def look(lore: dict[str, Any], names: list[str], transcript: list[dict[str, Any]], page: int = 1) -> str:
    """One entry in full, or how two entries are connected."""
    if not 1 <= len(names) <= 2:
        raise Refused("names: one entry, or two to see how they're connected")
    found = [find(lore, n) for n in names]
    if None in found:
        raise Refused(_not_found(lore, names[found.index(None)]))
    if len(found) == 2:
        return _connection(lore, found[0], found[1])  # type: ignore[arg-type]
    n = found[0]
    assert n
    e = lore["entries"][n]
    recent = set(mentioned(lore, recent_text(transcript))) - {n}
    every = _patterns(lore)
    last = next((t for t, x in reversed(turns(transcript)) if x["kind"] in ("player", "dm")
                 and every[n].search(x["text"]) and n in mentioned(lore, x["text"], every)), None)
    lines = [f"{n} ({e['kind']}" + (f"; also: {', '.join(e['other_names'])}" if e["other_names"] else "") + ")",
             "Description:", *(f"(t{p['turn']}) {p['text']}" for p in e["description"]),
             f"Last mentioned in play: turn {last}" if last is not None else "Not mentioned in play yet"]
    facts = [f for f in _facts(lore) if f["rel"] and n in f["involves"]]
    facts.sort(key=lambda f: (not (f["involves"] - {n}) & recent, *_newest(f)))
    shown = facts[(page - 1) * PAGE:page * PAGE]
    lines.append("Relationships (" + ("those with something from the last turns first, then " if recent else "")
                 + "newest first):" if facts else "Relationships: none yet")
    lines += [f"• {f['text']} (t{f['turn']})" + (" (came up just now)" if (f["involves"] - {n}) & recent else "")
              for f in shown]
    if len(facts) > page * PAGE:
        lines.append(f"…and {len(facts) - page * PAGE} more (page {page + 1})")
    elif facts and not shown:
        lines.append(f"(no page {page}: there are {len(facts)} relationships)")
    return "\n".join(lines)


def _connection(lore: dict[str, Any], a: str, b: str) -> str:
    if a == b:
        raise Refused(f"those are two names of the same entry, {a}")
    facts = _facts(lore)
    head = [f"{a} ↔ {b}"]
    direct = sorted((f for f in facts if {a, b} <= f["involves"]), key=_newest)
    head.append("Directly:" if direct else "Directly: nothing recorded")
    head += [f"• {f['text']} (t{f['turn']})" for f in direct[:PAGE]]
    if len(direct) > PAGE:
        head.append(f"…and {len(direct) - PAGE} more")
    paths = []
    for c in lore["entries"]:
        if c in (a, b):
            continue
        ac = sorted((f for f in facts if {a, c} <= f["involves"]), key=_newest)
        cb = sorted((f for f in facts if {c, b} <= f["involves"]), key=_newest)
        if ac and cb:
            paths.append((min(ac[0]["turn"], cb[0]["turn"]), c, ac[0], cb[0]))
    paths.sort(key=lambda p: -p[0])
    head.append("Through one other entry:" if paths else "Through one other entry: nothing recorded")
    for _, c, x, y in paths[:PATHS]:
        head.append(f"• via {c}: {x['text']} (t{x['turn']}) / {y['text']} (t{y['turn']})")
    if len(paths) > PATHS:
        head.append(f"…and {len(paths) - PATHS} more")
    return "\n".join(head)


def recall(lore: dict[str, Any], transcript: list[dict[str, Any]], search: list[str] | None = None,
           turn: int | None = None, page: int = 1) -> str:
    """The game log: one turn word for word, or the mentions of a word, a phrase or an entry (with its other names),
    newest first; two of them: only the turns where both come up."""
    tt = turns(transcript)
    if turn is not None:
        if not (text := turn_text(transcript, turn)):
            raise Refused(f"no turn {turn}: turns run from 0 to {now(transcript)}")
        return text
    search = [s for s in (search or []) if str(s).strip()]
    if not 1 <= len(search) <= 2:
        raise Refused("pass search (one or two words, phrases or entry names) or turn")
    every = _patterns(lore)
    spans: dict[int, list[tuple[int, int, str]]] = {}

    def finder(s: str) -> Any:
        """Where a term is in a text, or None: an entry as play names it (capitals, longest name); a keyword anyhow."""
        if n := find(lore, s):
            def at(text: str) -> tuple[int, int] | None:
                sp = spans.setdefault(id(text), _spans(text, every))
                return next(((a, b) for a, b, x in sp if x == n), None)
            return at
        p = _pattern([str(s)], capitals=False)
        return lambda text: (m_.start(), m_.end()) if (m_ := p.search(text)) else None
    finds = [finder(s) for s in search]
    said = [(t, e) for t, e in tt if e["kind"] in ("player", "dm")]
    both = {t for t in {t for t, _ in said} if all(any(f(e["text"]) for tt_, e in said if tt_ == t) for f in finds)}
    hits = [(t, e) for t, e in reversed(said) if t in both and any(f(e["text"]) for f in finds)]
    what = " and ".join(repr(s) for s in search)
    if not hits:
        return f"no mentions of {what}" + (" in the same turn" if len(search) == 2 else "")
    shown = hits[(page - 1) * PAGE:page * PAGE]
    out = [f"{len(hits)} mentions of {what}" + (" in the same turn" if len(search) == 2 else "") + ", newest first:"]
    for t, e in shown:
        a, b = min(x for f in finds if (x := f(e["text"])))
        s, end = max(0, a - SNIP), min(len(e["text"]), b + SNIP)
        snippet = ("…" if s else "") + e["text"][s:end].replace("\n", " ") + ("…" if end < len(e["text"]) else "")
        out.append(f"turn {t}, {'player' if e['kind'] == 'player' else 'DM'}: {snippet}")
    if len(hits) > page * PAGE:
        out.append(f"…and {len(hits) - page * PAGE} more (page {page + 1})")
    return "\n".join(out)


# ---------- each turn ----------

REMINDER = ("Record new names and facts in your notebook with write_lore as you say them (hidden from the player); "
            "look things up with lore and recall before you state something you said earlier.")


def notes(lore: dict[str, Any], transcript: list[dict[str, Any]], party: tuple[str, ...] = ()) -> tuple[dict[str, Any], str]:
    """The turn number, the notebook entries the last turns mention and those they link to (one line each, skipping
    any shown in the last 3 turns), and the reminder. Returns (the notebook with what was shown, the text).
    `party`: the PC's and companions' names; their entries are neither shown nor followed (owner, 2026-10-13): they
    come up nearly every turn, and their sheets are in the instructions."""
    lore, turn = copy.deepcopy(lore), now(transcript)
    out: list[str] = []
    skip = {e for p in party for e in (find(lore, p), find(lore, p.split()[0])) if e}
    tasks = [n for n, e in lore["entries"].items() if _task(e) and e.get("status", "open") == "open"]
    skip |= set(tasks)  # shown in full above the names
    seen = [n for n in mentioned(lore, recent_text(transcript)) if n not in skip] if lore["entries"] else []

    def fresh(n: str) -> bool:
        return turn - lore["shown"].get(n, -SKIP - 1) > SKIP

    for n in seen:
        if fresh(n) and len(out) < NOTES:
            out.append(_short(lore, n))
            lore["shown"][n] = turn
    if seen:
        facts = sorted((f for f in _facts(lore) if f["involves"] & set(seen)), key=_newest)
        for f in facts:
            for c in sorted(f["involves"] - set(seen) - skip):
                if fresh(c) and len(out) < NOTES:
                    out.append(_short(lore, c) + " ← linked from " + ", ".join(sorted(f["involves"] & set(seen))))
                    lore["shown"][c] = turn
    text = f"[Turn {turn}]"
    if tasks:
        text += "\n[Open quests and leads]\n" + "\n".join(
            f"{n} ({lore['entries'][n]['kind']}): " + " ".join(d["text"] for d in lore["entries"][n]["description"])
            for n in tasks)
    if out:
        text += "\n[Notebook: names from the last turns]\n" + "\n".join(out)
    return lore, text + "\n" + REMINDER
