"""Character creation as a conversation (PR-02-7; PR-02-1 workshop, PR-02-2 quick start, PR-02-3 ready-made;
PR-02-4 birth; PR-02-6 finish; T063).

    flow = CreationFlow(ctx)               # ctx: engine.dm.context.TurnContext
    resp = flow.begin()                    # [CREATE 1/5] Before we begin (taste, lines and veils, path)
    resp = flow.submit("quick start. No spiders, please; torture only off-stage")
    ...                                    # one [CREATE n/N] block per message; skipped ones take the default
    resp = flow.answer("begin")            # at "Ready?": the PC is written; phase "play"
    resp = new_character(ctx)              # after an ending: creation again in the same world

Every answer is a `creation_answered` event (block, choice, source, words) and every block a `pause_opened` /
`pause_closed` pair; the draft is a fold of the answers since the last `start` marker, so a restart re-presents
exactly the open block. The PC is written when the player begins (after the validated sheet is shown), so "change
something" never has to unwrite a character. Lines and veils from 1(b) are written at once as `pref.safety.lines` /
`pref.safety.veils` facts (engine/audit/safety.py reads them).
"""

from __future__ import annotations

import itertools
import re
from typing import Any

from pydantic import BaseModel, Field

from engine import ids
from engine.abilities.focus import define_focus
from engine.audit.safety import SafetyEntry, safety_fact
from engine.dm.context import TurnContext
from engine.dm.response import Choice, OofBlock, Pause, Response
from engine.dm.roles.interpret import DETAILS, MOVE_ON, OWN_WORDS, SUGGEST, InterpretResult, interpret
from engine.dm.seed_flow import PHASE_KEY, close_pause, flow_tx, open_pause, present_pause
from engine.gen.birth import BentState, birth_draw, circumstance_for, source_tags
from engine.store.db import Transaction
from engine.store.events import WORLD, EntityRecord, Event, LicenseInstance, PauseRecord, Quantity
from engine.store.projection import WorldState
from engine.world.social import LoggedSeedRng

FLOW = "creation"
HUMAN = "orig.people.human"
SOLDIER = "orig.life.soldier"
ATTRS: tuple[str, ...] = ("might", "agility", "endurance", "wits", "intellect", "presence", "resolve")
FAST: tuple[str, ...] = ("c0", "c1", "c8.drive", "c8.anchor", "c9.name")
READY_MADE: tuple[str, ...] = ("c0", "rm.pick", "rm.name")
PATHS = (("fast", "Quick start (five questions, a few minutes)"), ("full", "the full workshop"),
         ("ready_made", "a ready-made character"))
TASTES = (("fights", ("fight", "combat", "battle", "brawl")), ("exploring", ("explor", "ruin", "dungeon")),
          ("talking", ("talk", "social", "persua", "negotia", "intrigue")), ("mysteries", ("myster", "investig",
          "puzzle", "secret")), ("journeys", ("journey", "travel", "road")), ("building", ("build", "own place",
                                                                                         "home", "found")))
MANNERS = ("unremarked", "hard", "omened")  # 02.6.4 (gifted is the Touched livelihood's, never classified)
PRONOUNS = (("she/her", r"\bshe\b|\bher\b"), ("he/him", r"\bhe\b|\bhim\b"), ("they/them", r"\bthey\b|\bthem\b"))
_VEIL = re.compile(r"off[- ]?(stage|screen|camera|page)|only (mentioned|implied|offstage)|not on (screen|stage)|"
                   r"never (shown|on screen)|fade to black|in passing", re.I)
_NONE = re.compile(r"^\s*(no|none|nothing|nope|nothing ruled out|nothing\W*all fine|all good)\W*$", re.I)
OPEN = "open"
BEGIN, CHANGE = "begin", "change"
PREFIX_NAME = "name:"

WELCOME = ("Welcome. This is an adventure told in words. You say what your character does, in your own words, "
           "and I tell you what happens. There is no menu and no wrong way to ask. I keep the rules, and when "
           "the dice matter I show you the odds before you commit. Your character can die, but never without "
           "a plain warning and a choice first.")
FIRST_USE = ("[RULES] Say what you do in your own words. You can always ask \"what are my options?\" or \"what do "
             "I know?\" and I will answer plainly.\n"
             "[RULES] When something is risky I will show you the odds and what failure would cost before you "
             "commit. You can change your mind then.\n"
             "[RULES] No roll can kill your character unless I have warned you first, in these brackets.")


class CreationError(RuntimeError):
    """An answer arrived with no creation block open."""


# ------------------------------------------------------------------------------------------- data


def _origins(rules: Any) -> dict[str, Any]:
    return dict(rules.origins)


def _kits(rules: Any) -> dict[str, Any]:
    return {k["id"]: k for k in rules.doc("kits")["kits"]}


def _odoc(rules: Any) -> dict[str, Any]:
    return dict(rules.doc("origins"))


def _of_kind(rules: Any, kind: str) -> list[str]:
    """The origins of a kind in data order (the core list; setting blocks are not offered)."""
    return [o["id"] for o in _odoc(rules)["origins"] if o["kind"] == kind]


def present_peoples(state: WorldState, rules: Any) -> list[str]:  # rule: 12.16.7
    """The peoples C2 offers: those the seed made present (all eight when no seed ran)."""
    pres = state.meta.get("world.peoples")
    allp = _of_kind(rules, "people")
    if not pres:
        return allp
    here = {p["origin"] for p in pres if p.get("present") != "absent"}
    return [p for p in allp if p in here]


# ------------------------------------------------------------------------------------------- the draft


class Draft(BaseModel):
    """The creation record so far: a fold of `creation_answered` since the last `start` marker."""

    values: dict[str, Any] = Field(default_factory=dict)
    answered: list[str] = Field(default_factory=list)
    defaults: dict[str, bool] = Field(default_factory=dict)
    words: dict[str, str] = Field(default_factory=dict)
    birth: dict[str, Any] | None = None
    names_offered: list[str] = Field(default_factory=list)
    started: bool = False
    changing: bool = False  # "change something" was chosen at Ready?: ask which block
    done: bool = False
    new_character: bool = False

    @property
    def path(self) -> str:
        return str(self.values.get("c0") or "fast")

    def get(self, key: str, default: Any = None) -> Any:
        v = self.values.get(key)
        return default if v is None else v


def fold(state: WorldState) -> Draft:  # rule: PR-02-7
    d = Draft()
    for a in state.creation_answers:
        b, c = a["block"], a.get("choice")
        if b == "start":
            d = Draft(started=True, new_character=bool((c or {}).get("new_character")))
        elif b == "change":
            d.changing = c is None
            if c:
                d.answered = [x for x in d.answered if x != c]
                d.values.pop(c, None)
        elif b == "birth":
            d.birth = c
        elif b == "names":
            d.names_offered = list(c or [])
        elif b == "ready":
            d.done = True
        else:
            d.changing = False
            if b not in d.answered:
                d.answered.append(b)
            d.values[b] = c
            d.defaults[b] = a.get("source") == "default"
            if a.get("words"):
                d.words[b] = a["words"]
    return d


def sequence(d: Draft, rules: Any) -> list[str]:  # rule: PR-02-2
    """The blocks of the chosen path, in order (C2 rule only for a non-human; C7 only when the kit has a choice)."""
    if "c0" not in d.answered:
        return ["c0"]
    if d.path == "ready_made":
        seq = list(READY_MADE)
    elif d.path == "full":  # rule: PR-02-1
        seq: list[str] = ["c0", "c1", "c2.people"]
        if d.get("c2.people", HUMAN) != HUMAN:
            seq.append("c2.rule")
        seq += ["c3", "c4", "c5", "c6"]
        kit = _kits(rules).get(_origins(rules)[d.get("c1", SOLDIER)].get("kit_id"), {})
        if kit.get("choices"):
            seq.append("c7")
        seq += ["c8.drive", "c8.anchor", "c8.aspiration", "c8.true_thing", "c9.name"]
    else:
        seq = list(FAST)
    name = d.values.get("c9.name")
    if isinstance(name, dict) and not name.get("pronouns"):
        seq.append("c9.pronouns")
    return seq


def next_block(d: Draft, rules: Any) -> str | None:
    return next((b for b in sequence(d, rules) if b not in d.answered), None)


# ------------------------------------------------------------------------------------------- blocks


class Block(BaseModel):
    id: str
    title: str
    lines: list[str]
    options: list[Choice] = Field(default_factory=list)
    default: str | None = None
    default_line: str
    classes: list[str] = Field(default_factory=list)
    limits: bool = False
    inline: bool = False  # the options are named in the question lines (1(c)), not listed again
    cards: tuple[str, ...] = ("PR-02-7",)


def _numbering(bid: str, d: Draft, rules: Any) -> str:
    seq = [b for b in sequence(d, rules) if b != "c9.pronouns"]
    key = "c9.name" if bid == "c9.pronouns" else bid
    n = seq.index(key) + 1 if key in seq else len(seq)
    total = 5 if d.path == "fast" or "c0" not in d.answered else len(seq)
    return f"[CREATE {n:d}/{total:d}]"


def _letters(options: list[Choice]) -> list[str]:
    return [f"({chr(97 + i)}) {c.label}" for i, c in enumerate(options)]


def block_spec(bid: str, d: Draft, state: WorldState, rules: Any, *, show_all: bool = False) -> Block:
    # rule: PR-02-7
    """The fixed parts of one block: title, question, options in the rules' order, default line."""
    OR = _origins(rules)
    life = OR[d.get("c1", SOLDIER)]
    up_id = d.get("c3") or life["defaults"]["upbringing"]
    up = OR[up_id]
    if bid == "c0":
        return Block(id=bid, title="Before we begin", options=[Choice(id=i, label=t) for i, t in PATHS if
                                                                 i != "ready_made" or state.meta.get("world.pregens")],
                     lines=["(a) What would you like plenty of? Up to two: fights · exploring · talking your way "
                            "through · mysteries · journeys · building something of your own. Anything you'd "
                            "like less of?",
                            "(b) Is there anything you would rather never see in the story, or only off-stage?",
                            "(c) Quick start (five questions, a few minutes), the full workshop, or a ready-made "
                            "character?"],
                     default="fast", default_line="a bit of everything · nothing ruled out (you can say so at any "
                     "time) · quick start", classes=[t for t, _ in TASTES], limits=True, inline=True,
                     cards=("PR-02-7", "12.5.6"))
    if bid == "c1":
        lives = _of_kind(rules, "livelihood")
        first = list(_odoc(rules)["creation_defaults"]["first_seven"])
        shown = lives if show_all else first
        opts = [Choice(id=x, label=f"{OR[x]['name']} — {OR[x].get('gloss', '')}".rstrip(" —")) for x in shown]
        if not show_all:
            opts.append(Choice(id="more", label=f"{len(lives) - len(first):d} other lives"))
        return Block(id=bid, title="Who are you?", options=opts, default=SOLDIER, default_line="Soldier.",
                     lines=["Pick a life your character led before this story, or describe them in a sentence and I "
                            "will find the nearest.",
                            "You are human unless you tell me otherwise (\"peoples\" shows the others)."],
                     classes=lives, cards=("PR-02-7", "02.2.4"))
    if bid == "c2.people":
        ps = present_peoples(state, rules)
        return Block(id=bid, title="Your people.", lines=["Who were you born among?"], default=HUMAN,
                     options=[Choice(id=p, label=f"{OR[p]['name']} — {OR[p].get('tradeoff', '')}") for p in ps],
                     default_line="Human.", classes=ps)
    if bid == "c2.rule":
        return Block(id=bid, title="Your people.", lines=["Typical of your kind, or uncommon?"],
                     options=[Choice(id="typical", label="typical of your kind (+7, three placements decided)"),
                              Choice(id="free", label="uncommon (+5, free)")],
                     default=_default_rule(d.get("c2.people", HUMAN), life["id"], rules), default_line="typical.")
    if bid == "c3":
        ups = _of_kind(rules, "upbringing")
        return Block(id=bid, title="Where did you grow up?", lines=["Where did you grow up?"],
                     options=[Choice(id=u, label=f"{OR[u]['name']} — {OR[u].get('tradeoff', '')}") for u in ups],
                     default=life["defaults"]["upbringing"], default_line=f"{OR[life['defaults']['upbringing']]['name']}.",
                     classes=ups)
    if bid == "c4":
        rule = _rule(d, rules)
        shapes = _shapes(d.get("c2.people", HUMAN), rule, rules)
        opts = [Choice(id=s, label=f"{s}: {', '.join(f'{v:+d}' for v in arr)}") for s, arr in shapes.items()]
        place = default_placement(d.get("c2.people", HUMAN), rule, "peaked", life["defaults"]["attribute_priority"],
                                  rules)
        return Block(id=bid, title="What are you made of?",
                     lines=[f"Here is how a {life['name'].lower()} usually stands: " + _attr_line(place) + ".",
                            "Pick a shape; the engine places it by your life's priorities."],
                     options=opts, default="peaked", default_line="peaked, placed as shown.")
    if bid == "c5":
        profs = list(_odoc(rules)["profiles"])
        return Block(id=bid, title="What can you do?",
                     lines=["Deep in two, a trick up your sleeve, well-rounded, or a bit of everything?"],
                     options=[Choice(id=p["id"], label=f"{p['name']} — {p['text']}") for p in profs],
                     default=life["defaults"]["profile"], default_line=f"{life['defaults']['profile']}.")
    if bid == "c6":
        return Block(id=bid, title="Your early years.",
                     lines=["Was anything said about your birth, or about your early years?"],
                     default=None, default_line="nothing remarked.", classes=list(MANNERS),
                     cards=("PR-02-7", "02.6.4"))
    if bid == "c7":
        kit = _kits(rules)[life["kit_id"]]
        opts = [Choice(id=f"kit:{i:d}", label=" + ".join(_item_name(it["item_tag"]) for it in opt))
                for i, opt in enumerate(kit["choices"][0]["options"])]
        return Block(id=bid, title="What you carry.", lines=[f"{kit['name']}: which do you carry?"], options=opts,
                     default="kit:0", default_line="the first.")
    if bid == "c8.drive":
        seeds = list(life["drive_seeds"])
        return Block(id=bid, title="What do you want?",
                     lines=["One sentence: the thing your character wants most, or believes most. Or take one of "
                            "these:"], options=[Choice(id=f"drive:{i:d}", label=f'"{s}"') for i, s in enumerate(seeds)],
                     default="drive:0", default_line="the first one.")
    if bid == "c8.anchor":
        seeds = [up["bond_seeds"][0], life["bond_seeds"][0]]
        return Block(id=bid, title="Who matters to you?",
                     lines=["Name one person your character would cross the country for, and what they are to you. "
                            "Or:"], options=[Choice(id=f"bond:{i:d}", label=_bond_text(s)) for i, s in enumerate(seeds)],
                     default="bond:0", default_line="the first one.")
    if bid == "c8.aspiration":
        asp = list(life.get("aspiration_seeds") or [])
        opts = [Choice(id=f"asp:{i:d}", label=a["text"]) for i, a in enumerate(asp)] + [Choice(id=OPEN,
                                                                                         label="leave it open")]
        return Block(id=bid, title="Who you hope to become", lines=["Who does your character hope to become?"],
                     options=opts, default=OPEN, default_line="open (it can be found in play).")
    if bid == "c8.true_thing":
        return Block(id=bid, title="One true thing", lines=["One thing about your character that is simply true?"],
                     default=OPEN, default_line="open.")
    if bid in ("c9.name", "rm.name"):
        opts = [Choice(id=PREFIX_NAME + n, label=n) for n in d.names_offered]
        lines = ["A name, and how I should speak of your character (he, she, they, or as you like).",
                 "Say \"suggest\" and I will offer three names."]
        default: str | None = None
        line = "I will offer three names and wait; a character needs a name."
        if bid == "rm.name":
            pg = _pregen(state, d.get("rm.pick"))
            lines = [f"{pg.get('name')} ({pg.get('pronouns')}), or another name?"] + lines[1:]
            opts = [Choice(id="keep", label=f"keep {pg.get('name')}")] + opts
            default, line = "keep", f"{pg.get('name')}."
        return Block(id=bid, title="What are you called?", lines=lines, options=opts, default=default,
                     default_line=line, cards=("PR-02-7", "02.9.6"))
    if bid == "c9.pronouns":
        nm = (d.get("c9.name") or {}).get("name", "your character")
        return Block(id=bid, title="What are you called?", lines=[f"How should I speak of {nm}?"],
                     options=[Choice(id=p, label=p) for p, _ in PRONOUNS], default=None,
                     default_line="I will wait; I never guess a character's pronouns.", cards=("PR-02-7", "02.9.6"))
    if bid == "rm.pick":
        pgs = state.meta.get("world.pregens") or []
        opts = [Choice(id=p["id"], label=f"{p['name']} — {p['sentence']} Good at: {p['good_at']}. Wants: "
                       f"\"{p['drive']}\"") for p in pgs]
        return Block(id=bid, title="A ready-made character", lines=["Pick one; you may rename them."], options=opts,
                     default=opts[0].id if opts else None, default_line=f"{pgs[0]['name']}." if pgs else "",
                     cards=("PR-02-3",))
    raise CreationError(f"unknown creation block {bid}")


def _render(spec: Block, numbering: str) -> str:
    lines = [f"{numbering} {spec.title}"] + ["  " + x for x in spec.lines]
    if spec.options and not spec.inline:
        lines += ["  " + x for x in _letters(spec.options)]
    lines.append(f"  If you move on without choosing: {spec.default_line}")
    return "\n".join(lines)


# ------------------------------------------------------------------------------------------- numbers


def _rule(d: Draft, rules: Any) -> str:
    return str(d.get("c2.rule") or _default_rule(d.get("c2.people", HUMAN), d.get("c1", SOLDIER), rules))


def _default_rule(people: str, life: str, rules: Any) -> str:  # rule: 02.3.5
    """Typical for a people with a Typical rule (floors or fixed), Free for humans; the caster exception."""
    pr = _origins(rules)[people]["attribute_rules"] or {}
    if not (pr.get("floors") or pr.get("fixed")):
        return "free"
    casting = (_origins(rules)[life].get("magic") or {}).get("casting_attribute")
    if casting and (pr.get("fixed") or {}).get(casting) == -1:
        return "free"
    return "typical"


def _shapes(people: str, rule: str, rules: Any) -> dict[str, list[int]]:
    pr = _origins(rules)[people]["attribute_rules"] or {}
    if rule == "typical" and pr.get("shapes"):
        return dict(pr["shapes"])
    return {k: v for k, v in _odoc(rules)["attribute_shapes"]["free"].items() if k != "sum"}


def default_placement(people: str, rule: str, shape: str, priority: list[str], rules: Any) -> dict[str, int]:
    # rule: 02.3.5
    """Among the legal placements of the shape, the lexicographic maximum along the livelihood's priority."""
    pr = _origins(rules)[people]["attribute_rules"] or {}
    arr = _shapes(people, rule, rules)[shape]
    fixed, floors = (pr.get("fixed") or {}, pr.get("floors") or {}) if rule == "typical" else ({}, {})
    best: tuple[tuple[int, ...], dict[str, int]] | None = None
    for perm in set(itertools.permutations(arr)):
        a = dict(zip(ATTRS, perm, strict=True))
        if all(a[k] == v for k, v in fixed.items()) and all(a[k] >= v for k, v in floors.items()):
            key = tuple(a[x] for x in priority)
            if best is None or key > best[0]:
                best = (key, a)
    if best is None:
        raise CreationError(f"no legal placement of {shape} for {people} ({rule})")
    return best[1]


def _training_license(tag: str, rules: Any) -> str | None:  # rule: 02.5.3
    lid = "lic.training." + tag.removeprefix("deed.").replace(".", "_")
    return lid if rules.has(lid) else None


def _picks(life: dict[str, Any], profile: str, rules: Any) -> tuple[list[str], list[str], str | None]:
    # rule: 02.5.2
    """Deep, access and technique for a profile: the livelihood's defaults for its own profile, else the list in
    order (a magic livelihood keeps its default school as its one magic pick)."""
    dflt = life["defaults"]
    if profile == dflt["profile"]:
        return list(dflt["deep"]), list(dflt["access"]), dflt.get("technique")
    prof = next(p for p in _odoc(rules)["profiles"] if p["id"] == profile)
    magic = life.get("magic")
    pool = [t for t in life["trainings"] if not t.startswith(("deed.arcane", "deed.divine", "deed.primal"))]
    if magic:
        pool = list(dflt["deep"]) + pool
    deep = pool[: prof["deep"]]
    access = pool[prof["deep"]: prof["deep"] + prof["access"]]
    tech = None
    if prof["technique"]:
        tech = dflt.get("technique") or next(iter(life.get("technique_suggestions") or []), None)
    return deep, access, tech


def _tongues(people: dict[str, Any], up: dict[str, Any], intellect: int, second: str,
             rules: Any) -> tuple[dict[str, str], list[str]]:  # rule: 02.4.6
    """Tongues with grades and the learning picks taken by the default order (02.2.2, 02.5.6)."""
    order = ("broken", "accented", "native")
    held: dict[str, str] = {x["license"]: x["grade"] for x in people.get("languages") or []}
    for x in up.get("languages") or []:
        if order.index(x["grade"]) > order.index(held.get(x["license"], "broken")) or x["license"] not in held:
            held[x["license"]] = x["grade"]
    other: list[str] = [lic for lic in up.get("licenses") or [] if lic == "lic.lang.letters"]
    for _ in range(int(up.get("language_picks") or 0)):  # an upbringing's tongue pick: the second tongue
        if second not in held:
            held[second] = "accented"
    picks = max(0, intellect)
    for step in ("letters", "common", "second", "old"):  # rule: 02.5.6
        if picks <= 0:
            break
        if step == "letters" and "lic.lang.letters" not in other:
            other.append("lic.lang.letters")
        elif step == "common" and held.get("lic.lang.common", "broken") != "native":
            g = held.get("lic.lang.common")
            held["lic.lang.common"] = order[min(2, order.index(g) + 1)] if g else "broken"
        elif step == "second" and second not in held:
            held[second] = "accented"
        elif step == "old" and "lic.lang.old_tongue" not in held and rules.has("lic.lang.old_tongue"):
            held["lic.lang.old_tongue"] = "accented"
        else:
            continue
        picks -= 1
    return held, other


def _attr_line(a: dict[str, int]) -> str:
    return ", ".join(f"{k.capitalize()} {a[k]:+d}" for k in ATTRS)


def _item_name(tag: str, note: str | None = None) -> str:
    return note or tag.rsplit(".", 1)[-1].replace("_", " ")


def _bond_text(seed: str) -> str:
    return seed.split(":", 1)[1].strip() if ":" in seed else seed


def _pregen(state: WorldState, pid: str | None) -> dict[str, Any]:
    pgs = state.meta.get("world.pregens") or []
    return next((p for p in pgs if p["id"] == pid), pgs[0] if pgs else {})


def build_record(d: Draft, state: WorldState, rules: Any) -> dict[str, Any]:  # rule: PR-02-6
    """The whole character from the answers, every unanswered choice at its 02.2.2 default."""
    OR = _origins(rules)
    if d.path == "ready_made":
        pg = _pregen(state, d.get("rm.pick"))
        nm = d.get("rm.name") or {}
        life, people, up = OR[pg["livelihood"]], OR[pg["people"]], OR[pg["upbringing"]]
        rule, shape, profile = pg.get("rule", "free"), pg.get("shape", "peaked"), pg.get("profile", "focused")
        attrs = dict(pg["attributes"])
        deep, access, tech = list(pg.get("deep") or []), list(pg.get("access") or []), pg.get("technique")
        drive, anchor = pg.get("drive"), pg.get("anchor_bond")
        asp = pg.get("aspiration")
        name = nm.get("name") or pg["name"]
        pronouns = nm.get("pronouns") or pg.get("pronouns")
        manner, kit_pick, true_thing = "unremarked", 0, None
    else:
        life = OR[d.get("c1", SOLDIER)]
        people = OR[d.get("c2.people", HUMAN)]
        up = OR[d.get("c3") or life["defaults"]["upbringing"]]
        rule, shape = _rule(d, rules), str(d.get("c4", "peaked"))
        profile = str(d.get("c5") or life["defaults"]["profile"])
        attrs = default_placement(people["id"], rule, shape, life["defaults"]["attribute_priority"], rules)
        deep, access, tech = _picks(life, profile, rules)
        drive = d.get("c8.drive") or life["drive_seeds"][0]
        anchor = d.get("c8.anchor") or _bond_text(up["bond_seeds"][0])
        a = d.get("c8.aspiration", OPEN)
        asp = None if a == OPEN else a
        nm = d.get("c9.name") or {}
        name, pronouns = nm.get("name"), nm.get("pronouns") or d.get("c9.pronouns")
        manner = d.get("c6") or ("hard" if up["id"] == "orig.up.bonded" else "unremarked")
        kit_pick = int(str(d.get("c7", "kit:0")).split(":")[1])
        true_thing = None if d.get("c8.true_thing", OPEN) == OPEN else d.get("c8.true_thing")
    if people["id"] == HUMAN:  # rule: 02.4.3
        extra = next((t for t in life["trainings"] if t not in deep + access), None)
        if extra:
            access = access + [extra]
    tongues_meta = state.meta.get("world.tongues") or {}
    second = tongues_meta.get("second_tongue") or _odoc(rules)["creation_defaults"]["second_tongue"]
    tongues, other = _tongues(people, up, attrs["intellect"], second, rules)
    lics: list[str] = ["lic.focus.push"] + [x for x in other if x not in ("lic.focus.push",)]
    lics += [x for x in up.get("licenses") or [] if x not in lics]
    lc = up.get("license_choice")
    if lc:
        lics.append(next((x for x in lc["of"] if x not in lics), lc["of"][0]))
    for t in deep + access:
        lid = _training_license(t, rules)
        if lid and lid not in lics:
            lics.append(lid)
    lics += [x for x in people.get("licenses") or [] if x not in lics]
    kits = _kits(rules)
    items: list[dict[str, Any]] = []
    coin = 0
    for kid in (up.get("kit_id"), life.get("kit_id")):
        kit = kits.get(kid or "")
        if not kit:
            continue
        items += [{**it, "kit": kid} for it in kit["items"]]
        for ch in kit.get("choices") or []:
            opt = ch["options"][min(kit_pick, len(ch["options"]) - 1) if kid == life.get("kit_id") else 0]
            items += [{**it, "kit": kid} for it in opt]
        coin += int(kit.get("coin") or 0)
    abilities = [tech] if tech else []
    return {
        "name": name, "pronouns": pronouns, "people": people["id"], "upbringing": up["id"], "livelihood": life["id"],
        "rule": rule, "shape": shape, "profile": profile, "attributes": attrs,
        "competence": {t: 2 for t in deep}, "deep": deep, "access": access, "abilities": abilities,
        "licenses": lics, "tongues": tongues, "tags": list(people.get("tags") or []),
        "vitality": 12 + attrs["endurance"],  # rule: 02.7.1
        "focus_base": int(up.get("focus_base") or 4),  # rule: 02.7.2
        "fate": 1, "dread_threshold": 8 + attrs["resolve"],  # rule: 02.7.3
        "items": items, "coin": coin, "drive": drive, "anchor": anchor, "aspiration": asp, "true_thing": true_thing,
        "manner": manner, "hooks": [h for o in (people, up, life) for h in (o.get("hooks") or [])[:1]],
    }


def apply_birth(rec: dict[str, Any], birth: dict[str, Any] | None) -> dict[str, Any]:  # rule: PR-02-4
    """Step 6's grants for a gift: its competence entry (+2), training license and gifted ability."""
    out = {**rec, "competence": dict(rec["competence"]), "abilities": list(rec["abilities"]),
           "licenses": list(rec["licenses"])}
    for e in (birth or {}).get("entries", []):
        comp = e.get("competence")
        if isinstance(comp, dict) and comp.get("tag"):
            out["competence"][comp["tag"]] = int(comp.get("value", 2))
            lid = comp.get("license")
            if lid and lid not in out["licenses"]:
                out["licenses"].append(lid)
        if e.get("gifted_ability") and e["gifted_ability"] not in out["abilities"]:
            out["abilities"].append(e["gifted_ability"])
    return out


def validate(rec: dict[str, Any], state: WorldState, rules: Any) -> list[tuple[str, str]]:  # rule: PR-02-9
    """The character tests (a subset of PR-02-9): (block to return to, what failed)."""
    errs: list[tuple[str, str]] = []
    a = rec["attributes"]
    total = 7 if rec["rule"] == "typical" else 5
    if set(a) != set(ATTRS) or any(not -1 <= v <= 3 for v in a.values()) or sum(a.values()) != total:
        errs.append(("c4", f"the attributes must be seven values from -1 to +3 summing to {total:+d}"))
    if rec["people"] not in present_peoples(state, rules):
        errs.append(("c2.people", "that people does not live in this region"))
    if len(rec["deep"]) > 2:
        errs.append(("c5", "at most two trainings are held deep"))
    if not 11 <= rec["vitality"] <= 15:
        errs.append(("c4", "Vitality must be 11 to 15 at creation"))
    if not rec.get("name"):
        errs.append(("c9.name", "a character needs a name"))
    if not rec.get("pronouns"):
        errs.append(("c9.pronouns", "I need to know how to speak of your character"))
    return errs


# ------------------------------------------------------------------------------------------- the sheet


def sheet(rec: dict[str, Any], rules: Any) -> str:  # rule: PR-02-6
    """The [SHEET] block (PR-02-6 step 3); Guard and dread are computed for display only (02.7.4)."""
    OR = _origins(rules)
    a = rec["attributes"]
    attrs = " · ".join(f"{k.capitalize()} {a[k]:+d}" if a[k] else f"{k.capitalize()} 0" for k in ATTRS)
    tags = {it["item_tag"] for it in rec["items"]}
    shield = any(t.startswith("item.shield") for t in tags)
    weapons = {t.split(".")[2] for t in tags if t.startswith("item.weapon.") and len(t.split(".")) > 2}
    comp = 2 if any(t.split(".")[-1] in weapons | ({"shield"} if shield else set()) for t in rec["competence"]) else 1
    guard = 10 + a["agility"] + comp + (1 if shield else 0)  # 06.4.1, coarse: the readied weapon or shield
    plain = ", ".join(t.split(".")[-1].replace("_", " ") for t in rec["deep"]) or "nothing yet"
    also = ", ".join(t.split(".")[-1].replace("_", " ") for t in rec["access"]) or "none"
    lines = [f"[SHEET] {rec['name']} ({rec['pronouns']}) — {OR[rec['people']]['name']} · "
             f"{OR[rec['upbringing']]['name']} · {OR[rec['livelihood']]['name']}",
             "  " + attrs,
             f"  Vitality {rec['vitality']:d}/{rec['vitality']:d} · Focus {rec['focus_base']:d}/{rec['focus_base']:d} · "
             f"fate {rec['fate']:d} · Guard {guard:d} · dread 0 of {rec['dread_threshold']:d}",
             f"  Good at (+2): {plain}      Also trained: {also}"]
    for ab in rec["abilities"]:
        e = rules.abilities.get(ab) or {}
        cost = e.get("cost") or {}
        lines.append(f"  Technique: {e.get('name', ab)} — {cost.get('focus', 0)} Focus")
    birth = rec.get("birth_entries") or []
    if birth:
        lines.append("  From birth: " + " · ".join(f"{b['name']}" for b in birth))
    letters = "reads" if "lic.lang.letters" in rec["licenses"] else "cannot read"
    tongue = ", ".join(f"{lic.split('.')[-1].replace('_', ' ').capitalize()} ({g})" for lic, g in rec["tongues"].items())
    lines.append(f"  Speaks: {tongue} · {letters}")
    items = ", ".join(_item_name(it["item_tag"], it.get("note")) for it in rec["items"])
    lines.append(f"  Carries: {items} · {rec['coin']:d} coin")
    asp = rec["aspiration"]["text"] if isinstance(rec.get("aspiration"), dict) else (rec.get("aspiration") or OPEN)
    lines.append(f"  Wants: \"{rec['drive']}\"   Hopes to become: {asp}   Matters: {_anchor_text(rec['anchor'])}")
    still = [k for k, v in (("thorn bond", None), ("true thing", rec.get("true_thing")),
                            ("aspiration", rec.get("aspiration"))) if not v]
    lines.append(f"  Still open: {', '.join(still) or 'nothing'}   · You may adjust your choices once before your first "
                 "night's rest.")
    return "\n".join(lines)


def _anchor_text(anchor: Any) -> str:
    if isinstance(anchor, dict):
        return f"{anchor.get('npc')} ({anchor.get('kind', 'friend')})"
    return str(anchor)


# ------------------------------------------------------------------------------------------- writing


def write_character(tx: Transaction, rec: dict[str, Any], d: Draft) -> str:  # rule: PR-02-6
    """Step 2: the PC entity with everything engine/harm and engine/abilities read, kit items, facts, meta."""
    st = tx.state
    pc = ids.entity_id("pc", rec["name"], st.entities)
    data = {"attributes": dict(rec["attributes"]), "abilities": list(rec["abilities"]),
            "competence": dict(rec["competence"]), "pronouns": rec["pronouns"], "people": rec["people"],
            "upbringing": rec["upbringing"], "livelihood": rec["livelihood"], "rule": rec["rule"],
            "profile": rec["profile"], "deep": rec["deep"], "access": rec["access"]}
    qs = {"vitality": Quantity(current=rec["vitality"], min=0, max=rec["vitality"]),  # rule: 02.7.1
          "fate": Quantity(current=rec["fate"], min=0, max=3),  # rule: 02.7.3
          "dread": Quantity(current=0, min=0, max=rec["dread_threshold"]),
          "coin": Quantity(current=rec["coin"], min=0, max=None)}
    lics = [LicenseInstance(license_id=lid, grade="trained", source="creation") for lid in rec["licenses"]]
    lics += [LicenseInstance(license_id=lid, grade=g, source="creation") for lid, g in rec["tongues"].items()]
    tx.add(Event.of("entity_created", source="creation", rule_id="PR-02-6", entity=EntityRecord(
        id=pc, kind="pc", name=rec["name"], tags=rec["tags"], data=data), quantities=qs, licenses=lics))
    tx.add(define_focus(pc, base=rec["focus_base"]))  # rule: 02.7.2
    carried: list[str] = []
    for it in rec["items"]:
        iid = ids.entity_id("item", _item_name(it["item_tag"]), tx.state.entities)
        tx.add(Event.of("entity_created", source="creation", rule_id="02.8.1", entity=EntityRecord(
            id=iid, kind="item", name=_item_name(it["item_tag"]), tags=[it["item_tag"]],
            data={k: v for k, v in it.items()} | {"owner": pc})))
        carried.append(iid)
    facts: list[tuple[str, Any, str, str]] = [
        ("origin.people", rec["people"], "02.4.7", "fact"), ("origin.upbringing", rec["upbringing"], "02.4.7", "fact"),
        ("origin.livelihood", rec["livelihood"], "02.4.7", "fact"), ("origin.rule", rec["rule"], "02.4.7", "fact"),
        ("carries", carried, "02.8.1", "fact"), ("drive", rec["drive"], "02.9.1", "commitment"),
        ("bond.anchor", rec["anchor"], "02.9.2", "fact"),
        ("hooks", rec["hooks"], "02.9.7", "fact"),
    ]
    if rec.get("aspiration"):
        facts.append(("aspiration", rec["aspiration"], "02.9.3", "fact"))
    if rec.get("true_thing"):
        facts.append(("true_thing", rec["true_thing"], "02.9.4", "fact"))
    if d.words.get("c6"):
        facts.append(("birth.account", d.words["c6"], "02.6.4", "fact"))
    for e in rec.get("birth_entries") or []:
        facts.append((f"birth.{e['layer']}", {"id": e["id"], "name": e["name"], "text": e["text"],
                                               "effects": e["effects"]}, "PR-02-4", "fact"))
    for pred, val, rule, kind in facts:
        tx.add(Event.of("fact_set", {"source": "player_accepted"}, source="creation", rule_id=rule, fact_id=tx.mint(
            ids.FACT), subject=pc, predicate=pred, value=val, kind=kind, visibility="shown",
            supersedes=tx.state.current_fact_id(pc, pred)))
    anchor = rec.get("anchor")
    if isinstance(anchor, dict) and anchor.get("npc") in tx.state.entities:
        tx.add(Event.of("relationship_set", source="creation", rule_id="02.9.2", a=pc, b=anchor["npc"],
                        kind=f"bond.{anchor.get('kind', 'friend')}", value=1, new_value=1, reason="anchor bond"))
    start = ((tx.state.meta.get("world.opening") or {}).get("start") or {}).get("place")
    if start in tx.state.entities and tx.state.entities[start].kind == "place":
        from engine.world.places import put

        put(tx, pc, start)
    still = [k for k, v in (("thorn", None), ("true_thing", rec.get("true_thing")),
                            ("aspiration", rec.get("aspiration"))) if not v]
    creation = {"path": d.path, "choices": {b: {"value": d.values.get(b), "default": d.defaults.get(b, False)}
                                            for b in d.answered}, "birth": d.birth, "open_slots": still,
                "window": "open", "bent": BentState().model_dump(), "manner": rec["manner"]}
    tx.add_all([Event.of("meta_set", source="creation", rule_id="02.2.6", key=f"{pc}.creation", value=creation),
                Event.of("meta_set", source="creation", rule_id="02.2.6", key="pc.creation", value={**creation,
                                                                                                    "pc": pc}),
                Event.of("meta_set", source="creation", rule_id="PR-02-6", key="pc.active", value=pc),
                Event.of("meta_set", source="creation", rule_id="PR-02-6", key=PHASE_KEY, value="play")])
    return pc


# ------------------------------------------------------------------------------------------- answers


def _ev(block: str, choice: Any, source: str, words: str | None = None, rule: str = "PR-02-7") -> Event:
    return Event.of("creation_answered", {"source": source}, source="player" if source.startswith("player") else
                    "engine", rule_id=rule, block=block, choice=choice, words=words)


def parse_limits(entries: list[str]) -> tuple[list[str], list[str]]:  # rule: 12.5.6
    """1(b)'s entries, verbatim: an entry asking for something only off-stage is a veil, anything else a line."""
    lines, veils = [], []
    for e in entries:
        if not e.strip() or _NONE.match(e):
            continue
        (veils if _VEIL.search(e) else lines).append(e.strip())
    return lines, veils


def parse_taste(text: str) -> list[str]:  # rule: 02.10.1
    """Up to two pillars the player wants plenty of, in the order named (words before "less")."""
    low = text.lower().split("less")[0]
    found = sorted((low.find(k), t) for t, keys in TASTES for k in keys if k in low)
    out: list[str] = []
    for _, t in found:
        if t not in out:
            out.append(t)
    return out[:2]


def parse_name(text: str) -> tuple[str | None, str | None]:  # rule: 02.9.6
    """A name and pronouns from the player's words ("Wren, she/her"; "call me Tam. He."): never guessed."""
    t = text.strip()
    pron = None
    for p, rx in PRONOUNS:
        if re.search(r"\b" + p.replace("/", r"\s*/\s*") + r"\b", t, re.I) or re.search(rx, t, re.I):
            pron = p
            break
    m = re.search(r"(?:call (?:me|them|him|her)|name is|named|called|i am|i'm)\s+([A-Z][\w'’-]*(?:\s+[A-Z][\w'’-]*)*)",
                  t, re.I)
    name = m.group(1) if m else re.split(r"[,;(.]|\s+-\s+|\b(?:she|he|they)\b", t, maxsplit=1, flags=re.I)[0]
    name = " ".join(w for w in name.strip().split() if w.lower() not in ("she/her", "he/him", "they/them"))
    return (name or None), pron


_NOT_NAMES = frozenset({"skip", "yes", "no", "ok", "okay", "begin", "quick", "none", "nothing", "default", "next",
                        "move on", "pass", "details", "suggest", "random", "anything", "whatever", "idk"})


_NOT_NAME_WORDS = frozenset({"my", "your", "his", "her", "our", "their", "who", "which", "that", "is", "am", "are",
                             "was", "i", "me", "and", "with"})


def plausible_name(name: str) -> bool:  # rule: 02.9.6
    """Words that could be a character's name: letters (with ' - and spaces), 2-40 long, at most five words,
    not a bare number or a menu word."""
    n = name.strip()
    words = n.lower().split()
    if words and (words[0] in ("the", "a", "an") or _NOT_NAME_WORDS & set(words)):
        return False  # "my sister Ada", "the one who waits": a description, not a name
    return (bool(re.fullmatch(r"[^\W\d_][^\W\d_'’ -]*(?:['’ -]+[^\W\d_]+)*\.?", n)) and 2 <= len(n) <= 40
            and len(n.split()) <= 5 and n.lower().rstrip(".") not in _NOT_NAMES)


def suggest_names(ctx: TurnContext, people: str, n: int = 3) -> list[str]:  # rule: 02.9.6
    """Three names from the seed's name table for the people (12.16.7), else the generic fallback table."""
    tables = [t for t in ctx.state.meta.get("world.names") or [] if t.get("people") == people] or \
        [t for t in ctx.state.meta.get("world.names") or [] if t.get("people") == HUMAN]
    out: list[str] = []
    if tables:
        t = tables[0]
        for _ in range(n * 4):
            g = ctx.rng.choice([r["result"] for r in t["given"]], "creation.name.given", table_id=t["id"])
            f = ctx.rng.choice([r["result"] for r in t.get("family") or [{"result": ""}]], "creation.name.family",
                               table_id=t["id"])
            nm = f"{g} {f}".strip()
            if nm not in out:
                out.append(nm)
            if len(out) == n:
                break
    else:
        rows = [r["result"] for r in ctx.rules.table("tbl.name_given")["results"]]
        while len(out) < n:
            nm = ctx.rng.choice(rows, "creation.name.given", table_id="tbl.name_given")
            if nm not in out:
                out.append(nm)
    return out


class CreationFlow:
    """PR-02-7 one block at a time; the draft is always re-folded from the record."""

    def __init__(self, ctx: TurnContext):
        self.ctx = ctx
        self.retry: list[OofBlock] = []  # a note shown when a block is asked again (a name that is not one)

    # ---------------------------------------------------------------- public

    def begin(self, *, new: bool = False) -> Response:
        """Start creation (or re-present the open block). `new`: a second character in the same world."""
        st = self.ctx.store.state
        rec = st.open_pause()
        if rec is not None and (rec.detail.get("flow") in (FLOW, "seed") or not new):
            return self.present()
        with flow_tx(self.ctx) as tx:
            if rec is not None:  # e.g. the ending's menu: the player chose a new character
                close_pause(tx, rec, "new_character", "option")
            return open_creation(self.ctx, [], new_character=new or fold(st).done)

    def present(self) -> Response:
        rec = self.ctx.store.state.open_pause()
        if rec is None:
            return Response(phase="play")
        return present_pause(rec, "creation" if rec.detail.get("flow") == FLOW else "seed")

    def submit(self, message: str) -> Response:
        return self._answer(message=message)

    def answer(self, choice_id: str) -> Response:
        return self._answer(choice_id=choice_id)

    def draft(self) -> Draft:
        return fold(self.ctx.store.state)

    # ---------------------------------------------------------------- internals

    def _answer(self, *, message: str | None = None, choice_id: str | None = None) -> Response:
        st = self.ctx.store.state
        rec = st.open_pause()
        if rec is None or rec.detail.get("flow") != FLOW:
            raise CreationError("no creation block is open")
        bid = str(rec.detail["block"])
        d = fold(st)
        choices = [Choice(id=c["id"], label=c.get("label", c["id"])) for c in rec.choices]
        if choice_id is not None:
            res = InterpretResult(choice=choice_id, picks=[choice_id], direct=True)
        else:
            spec = block_spec(bid, d, st, self.ctx.rules, show_all=bool(rec.detail.get("all"))) \
                if bid not in ("ready", "change") else None
            res = interpret(self.ctx, message or "", choices=choices, block=_block_text(rec),
                            classes=spec.classes if spec else (), lines_and_veils=bool(spec and spec.limits),
                            cards=spec.cards if spec else ("PR-02-7",))
        if res.choice == DETAILS or (bid == "c1" and res.choice == "more"):
            if bid == "c1":
                with flow_tx(self.ctx) as tx:
                    close_pause(tx, rec, "more", "option")
                    return self._ask(tx, [], "c1", fold(tx.state), show_all=True)
            return present_pause(rec, "creation", [OofBlock(kind="NOTE", text=_details(choices))])
        with flow_tx(self.ctx) as tx:
            notes = self._apply(tx, rec, bid, d, res, message)
            if notes is None:  # the block stays open (a name is required; names were offered)
                return self._ask(tx, self.retry, bid, fold(tx.state), reopen=rec)
            return self.advance(tx, notes)

    def _apply(self, tx: Transaction, rec: PauseRecord, bid: str, d: Draft, res: InterpretResult,
               message: str | None) -> list[OofBlock] | None:  # rule: PR-02-7
        words = res.own_words_text or (message if res.choice == OWN_WORDS else None)
        opts = [c["id"] for c in rec.choices]
        picked = res.choice if res.choice in opts else None
        if bid == "ready":
            close_pause(tx, rec, picked or BEGIN, "option" if picked else "default")
            if picked == CHANGE:
                tx.add(_ev("change", None, "player_option"))
                return []
            return self._begin(tx)
        if bid == "change":
            close_pause(tx, rec, picked or BEGIN, "option" if picked else "default")
            if picked and picked != BEGIN:
                tx.add(_ev("change", picked, "player_option"))
                return []
            return self._begin(tx)
        if bid == "c0":
            return self._apply_c0(tx, rec, res, words, message or "")
        if bid in ("c9.name", "rm.name"):
            return self._apply_name(tx, rec, bid, d, res, words)
        if bid == "c9.pronouns":
            val = picked or (parse_name(words or "")[1] if words else None) or (words.strip() if words else None)
            if not val:
                close_pause(tx, rec, None, "withdrawn")
                return None
            close_pause(tx, rec, val, "option" if picked else "own_words", words)
            tx.add(_ev(bid, val, "player_option" if picked else "player_words", words, rule="02.9.6"))
            return []
        spec = block_spec(bid, d, tx.state, self.ctx.rules, show_all=bool(rec.detail.get("all")))
        value, src = self._value(bid, spec, picked, res, words)
        close_pause(tx, rec, value if isinstance(value, str) else bid, {"player_option": "option", "player_words":
                                                                         "own_words"}.get(src, "default"), words)
        tx.add(_ev(bid, value, src, words if src == "player_words" else None))
        notes: list[OofBlock] = []
        if bid == "c1":
            people = self._people_named(message or words or "")
            if people:
                tx.add(_ev("c2.people", people, "player_words", message, rule="PR-02-2"))
            life = _origins(self.ctx.rules)[value]
            notes.append(OofBlock(kind="NOTE", text=f"{life['name']}, then: {life.get('gloss', '')}."))
        return notes

    def _value(self, bid: str, spec: Block, picked: str | None, res: InterpretResult,
               words: str | None) -> tuple[Any, str]:
        """The block's value: the option, the player's own words (classified or verbatim), or the default."""
        labels = {c.id: c.label for c in spec.options}
        if picked:
            src = "player_option"
            if bid == "c8.drive" or bid == "c8.aspiration":
                if picked == OPEN:
                    return OPEN, src
                if bid == "c8.aspiration":
                    life = _origins(self.ctx.rules)[fold(self.ctx.state).get("c1", SOLDIER)]
                    return life["aspiration_seeds"][int(picked.split(":")[1])], src
                return labels[picked].strip('"'), src
            if bid == "c8.anchor":
                return labels[picked], src
            return picked, src
        if res.choice == OWN_WORDS and words:
            if bid in ("c8.drive", "c8.anchor", "c8.true_thing"):
                return words, "player_words"
            if bid == "c8.aspiration":
                return {"text": words, "tags": []}, "player_words"
            if bid == "c6":
                return (res.own_words_class if res.own_words_class in MANNERS else "unremarked"), "player_words"
            if res.own_words_class in (spec.classes or labels):
                return res.own_words_class, "player_words"
        dflt: Any = spec.default
        if bid == "c8.drive":
            dflt = labels[spec.default or ""].strip('"')
        elif bid == "c8.anchor":
            dflt = labels[spec.default or ""]
        return dflt, "default"

    def _apply_c0(self, tx: Transaction, rec: PauseRecord, res: InterpretResult, words: str | None,
                  message: str) -> list[OofBlock]:  # rule: PR-02-7
        """1(a) taste, 1(b) lines and veils (verbatim, as safety facts), 1(c) the path."""
        paths = [c["id"] for c in rec.choices]
        path = res.choice if res.choice in paths else "fast"
        text = words or message
        taste = parse_taste(text)
        lines, veils = parse_limits(res.lines_and_veils)
        close_pause(tx, rec, path, "option" if res.choice in paths else "default", words)
        tx.add(_ev("c0.taste", taste, "player_words" if taste else "default", text if taste else None,
                   rule="02.10.1"))
        tx.add(_ev("c0.limits", {"lines": lines, "veils": veils}, "player_words" if lines or veils else "default",
                   "; ".join(res.lines_and_veils) or None, rule="12.5.6"))
        for kind, items in (("line", lines), ("veil", veils)):
            for topic in items:
                tx.add(safety_fact(SafetyEntry(kind=kind, topic=topic), tx.state, tx.mint))  # type: ignore[arg-type]
        if tx.state.current_fact_id(WORLD, "pref.lethality.acknowledged") is None:
            tx.add(Event.of("fact_set", {"source": "player_accepted"}, source="player", rule_id="14.3.3",
                            fact_id=tx.mint(ids.FACT), subject=WORLD, predicate="pref.lethality.acknowledged",
                            value=True, visibility="shown"))
        tx.add(_ev("c0", path, "player_option" if res.choice in paths else "default", rule="02.10.1"))
        return []

    def _apply_name(self, tx: Transaction, rec: PauseRecord, bid: str, d: Draft, res: InterpretResult,
                    words: str | None) -> list[OofBlock] | None:  # rule: 02.9.6
        opts = [c["id"] for c in rec.choices]
        if res.choice in (SUGGEST, MOVE_ON) and not (bid == "rm.name" and res.choice == MOVE_ON):
            people = d.get("c2.people", HUMAN) if bid == "c9.name" else _pregen(tx.state, d.get("rm.pick")).get(
                "people", HUMAN)
            names = suggest_names(self.ctx, people)
            close_pause(tx, rec, None, "withdrawn")
            tx.add(_ev("names", names, "oracle_roll", rule="02.9.6"))
            return None
        name: str | None
        pron: str | None
        if res.choice in opts and res.choice.startswith(PREFIX_NAME):
            name, pron = res.choice[len(PREFIX_NAME):], None
            src = "player_option"
        elif bid == "rm.name" and (res.choice == "keep" or res.choice == MOVE_ON):
            pg = _pregen(tx.state, d.get("rm.pick"))
            name, pron, src = pg.get("name"), pg.get("pronouns"), "default" if res.choice == MOVE_ON else "player_option"
        else:
            name, pron = parse_name(words or "")
            src = "player_words"
            if name and not plausible_name(name):  # "1", "skip", "?": ask again, never accept it as a name
                self.retry = [OofBlock(kind="NOTE", text=f'"{name}" does not sound like a name. What is your '
                                       'character called? (Say "suggest" for three names.)')]
                name = None
            elif name and name.islower():
                name = name.title()
        if not name:
            close_pause(tx, rec, None, "withdrawn")
            return None
        if bid == "rm.name" and not pron:
            pron = _pregen(tx.state, d.get("rm.pick")).get("pronouns")
        close_pause(tx, rec, name, {"player_option": "option", "player_words": "own_words"}.get(src, "default"), words)
        tx.add(_ev(bid, {"name": name, "pronouns": pron}, src, words, rule="02.9.6"))
        return []

    def _people_named(self, text: str) -> str | None:  # rule: PR-02-2
        """C2 only if the player names a people (in their C1 answer): the first present people named."""
        low = text.lower()
        OR = _origins(self.ctx.rules)
        for p in present_peoples(self.ctx.state, self.ctx.rules):
            if p == HUMAN:
                continue
            stem = OR[p]["name"].lower().split("-")[0].rstrip("s")
            if re.search(r"\b" + re.escape(stem[:5]), low):
                return p
        return None

    def _begin(self, tx: Transaction) -> list[OofBlock]:  # rule: PR-02-6
        """The player begins: write the validated character (the record shown on the sheet)."""
        d = fold(tx.state)
        rec = apply_birth(build_record(d, tx.state, self.ctx.rules), d.birth)
        rec["birth_entries"] = (d.birth or {}).get("entries", [])
        pc = write_character(tx, rec, d)
        tx.add(_ev("ready", pc, "player_option", rule="PR-02-6"))
        return [OofBlock(kind="NOTE", text=f"{rec['name']} is ready. The story begins.")]

    # ---------------------------------------------------------------- what comes next

    def advance(self, tx: Transaction, blocks: list[OofBlock]) -> Response:  # rule: PR-02-7
        d = fold(tx.state)
        if d.done:
            return Response(phase="play", oof_blocks=blocks)
        if d.changing:
            return self._ask_change(tx, blocks, d)
        bid = next_block(d, self.ctx.rules)
        if bid is not None:
            return self._ask(tx, blocks, bid, d)
        return self._finish(tx, d, blocks)

    def _finish(self, tx: Transaction, d: Draft, blocks: list[OofBlock]) -> Response:  # rule: PR-02-6
        """Birth (PR-02-4, once; again only if its sources changed), validate, show the sheet, ask Ready?"""
        rules = self.ctx.rules
        base = build_record(d, tx.state, rules)
        src = source_tags(base["people"], base["upbringing"], base["livelihood"])
        if d.birth is None or d.birth.get("source_tags") != src:
            circ = circumstance_for(base["livelihood"], base["manner"])
            recent = list(tx.state.meta.get("gen.birth.recent") or [])
            draw = birth_draw(LoggedSeedRng(self.ctx.rng, "gen.birth", stream="gen"), src, circ, recent=recent)
            tx.add(_ev("birth", draw.model_dump(mode="json"), "oracle_roll", rule="PR-02-4"))
            tx.add(Event.of("meta_set", source="gen.birth", rule_id="PR-02-4", key="gen.birth.recent",
                            value=(recent + [e.id for e in draw.entries])[-5:]))
            d = fold(tx.state)
        rec = apply_birth(base, d.birth)
        rec["birth_entries"] = (d.birth or {}).get("entries", [])
        errs = validate(rec, tx.state, rules)
        if errs:
            bid, why = errs[0]
            if bid in d.answered:
                tx.add(_ev("change", bid, "default", rule="PR-02-6"))
            d = fold(tx.state)
            nxt = bid if bid in sequence(d, rules) else (next_block(d, rules) or "c9.name")
            return self._ask(tx, [*blocks, OofBlock(kind="NOTE", text=f"Not yet: {why}.")], nxt, d)
        told = _birth_tale(rec["birth_entries"])
        out = [*blocks, *([OofBlock(kind="NOTE", text=told)] if told else []), OofBlock(kind="SHEET", text=sheet(rec, rules))]
        if tx.state.meta.get("player.new_to_this") is not False:  # no answer: treated as new (02.10.1)
            out.append(OofBlock(kind="RULES", text=FIRST_USE))
        choices = [Choice(id=BEGIN, label="begin"), Choice(id=CHANGE, label="change something (say what, or "
                                                                             "\"details\")")]
        text = ("[CREATE] Ready? Begin, or change something (say what, or \"details\").\n"
                "         You may also adjust these choices once after you have tried them, any time before your "
                "character's first night's rest.\n"
                "         If you move on without choosing: begin.")
        return self._pause(tx, out, text, "Ready?", choices, BEGIN, {"block": "ready"})

    def _ask_change(self, tx: Transaction, blocks: list[OofBlock], d: Draft) -> Response:
        seq = [b for b in sequence(d, self.ctx.rules) if b not in ("c0", "c9.pronouns")]
        choices = [Choice(id=b, label=block_spec(b, d, tx.state, self.ctx.rules).title) for b in seq]
        choices.append(Choice(id=BEGIN, label="nothing after all: begin"))
        text = "[CREATE] What would you like to change?\n" + "\n".join("  " + x for x in _letters(choices)) + \
            "\n  If you move on without choosing: begin."
        return self._pause(tx, blocks, text, "What would you like to change?", choices, BEGIN, {"block": "change"})

    def _ask(self, tx: Transaction, blocks: list[OofBlock], bid: str, d: Draft, *, show_all: bool = False,
             reopen: PauseRecord | None = None) -> Response:
        spec = block_spec(bid, d, tx.state, self.ctx.rules, show_all=show_all)
        text = _render(spec, _numbering(bid, d, self.ctx.rules))
        lead: list[OofBlock] = []
        if bid == "c0" and reopen is None:
            lead = [OofBlock(kind="NOTE", text=WELCOME)]
        return self._pause(tx, blocks, text, spec.title, spec.options, spec.default,
                           {"block": bid, "all": show_all}, lead=lead)

    def _pause(self, tx: Transaction, blocks: list[OofBlock], text: str, prompt: str, choices: list[Choice],
               default: str | None, detail: dict[str, Any], lead: list[OofBlock] | None = None) -> Response:
        own = [*(lead or []), OofBlock(kind="CREATE", text=text)]
        rec = open_pause(tx, "create_step", prompt, choices, default,
                         {"flow": FLOW, **detail, "blocks": [b.model_dump() for b in own]}, "PR-02-7")
        return Response(phase="creation", oof_blocks=[*blocks, *own], pause=Pause.of(rec))


def open_creation(ctx: TurnContext, blocks: list[OofBlock], *, new_character: bool = False) -> Response:
    # rule: PR-12-9
    """Hand over to creation inside the open transaction (the seed's step 5, or a new character)."""
    tx = ctx.need_tx()
    n = sum(1 for a in tx.state.creation_answers if a["block"] == "start")
    tx.add(_ev("start", {"n": n + 1, "new_character": new_character}, "default", rule="PR-02-7"))
    tx.add(Event.of("meta_set", source="creation", rule_id="PR-02-7", key=PHASE_KEY, value="creation"))
    return CreationFlow(ctx).advance(tx, blocks)


def new_character(ctx: TurnContext) -> Response:  # rule: PR-02-7
    """After an ending: creation again in the same world (contracts/engine-api.md `game.new_character`)."""
    return CreationFlow(ctx).begin(new=True)


def _birth_tale(entries: list[dict[str, Any]]) -> str:  # rule: 02.6.8
    """The birth results told as things that were always true (one sentence each, no numbers)."""
    return " ".join(str(e.get("text", "")).rstrip(".") + "." for e in entries if e.get("text"))


def _details(choices: list[Choice]) -> str:
    return "\n".join(f"{i + 1}. {c.label}" for i, c in enumerate(choices))


def _block_text(rec: PauseRecord) -> str:
    return "\n".join(str(b.get("text", "")) for b in rec.detail.get("blocks", []))
