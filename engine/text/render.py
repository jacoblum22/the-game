"""Typed rendering (B P4; 12.14.4, 12.3.3): player-facing sentences built from typed fields, never by regex over
model text. Verbs come from a closed list (`VERBS`: the Reader's 15 basic verbs and the relation registry's verbs);
a verb outside it raises KeyError, so a new one is added here, never guessed from its spelling.

    clause("npc.tam", "hold", "the lamp", names={"npc.tam": "Tam"})        -> "Tam holds the lamp"
    clause("pc.wren", "be", "inside", pc="pc.wren", neg=True)             -> "you are not inside"
    relation("the cart", "held_by", "Tam")                                -> "the cart is held by Tam"
    np("owl") -> "an owl";  np("wolf", 3) -> "three wolves";  sentence("it works") -> "It works."

Free text (an Oracle question, NPC speech, a Reader restatement) is never passed through here: it is shown
verbatim or quoted by the caller, or not at all.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Literal

DEGREE_WORDS = {  # 12.14.4: the degree in plain words, never "success"/"failure"
    "critical_success": "it goes better than hoped",
    "success": "it works",
    "failure": "it doesn't work",
    "critical_failure": "it goes badly",
}

_IRREGULAR = {  # lemma: (third person singular, past, past participle)
    "be": ("is", "was", "been"), "have": ("has", "had", "had"), "do": ("does", "did", "done"),
    "go": ("goes", "went", "gone"), "say": ("says", "said", "said"), "hold": ("holds", "held", "held"),
    "see": ("sees", "saw", "seen"), "know": ("knows", "knew", "known"), "keep": ("keeps", "kept", "kept"),
    "take": ("takes", "took", "taken"), "wear": ("wears", "wore", "worn"), "bear": ("bears", "bore", "borne"),
    "stand": ("stands", "stood", "stood"), "sit": ("sits", "sat", "sat"), "lie": ("lies", "lay", "lain"),
    "hang": ("hangs", "hung", "hung"), "lead": ("leads", "led", "led"), "read": ("reads", "read", "read"),
    "find": ("finds", "found", "found"), "give": ("gives", "gave", "given"), "strike": ("strikes", "struck", "struck"),
    "think": ("thinks", "thought", "thought"), "get": ("gets", "got", "got"), "set": ("sets", "set", "set"),
    "speak": ("speaks", "spoke", "spoken"), "hide": ("hides", "hid", "hidden"), "bind": ("binds", "bound", "bound"),
    "tell": ("tells", "told", "told"), "make": ("makes", "made", "made"), "ride": ("rides", "rode", "ridden"),
    "lend": ("lends", "lent", "lent"), "bar": ("bars", "barred", "barred"), "admit": ("admits", "admitted", "admitted"),
    "grip": ("grips", "gripped", "gripped"), "run": ("runs", "ran", "run"), "cast": ("casts", "cast", "cast"),
    "seek": ("seeks", "sought", "sought"), "ring": ("rings", "rang", "rung"),
}
_MODALS = {"can": "could", "will": "would", "could": "could", "would": "would", "may": "might", "might": "might",
           "must": "must", "should": "should"}  # modal: its past; no agreement, 'not' follows ('cannot')
_REGULAR = frozenset((
    # the basic verbs' phrases (BEAT_VERBS)
    "move look talk grapple force strain evade dodge sneak work endure help ready turn try "
    # the relation registry and the predicates games write
    "carry own belong contain notice watch guard block cover face wait live serve ask answer want fear need seem "
    "post address attach occupy locate arm carve announce advertise border connect enclose exist mark open close "
    "lean lock show call claim pass follow hunt point approach arrive remain rest stare glare smile nod bark touch "
    "pull tend sound swallow offer screen shout refer flow edge tie"
).split())
VERBS = frozenset(_IRREGULAR) | _REGULAR | frozenset(_MODALS)

BEAT_VERBS: dict[str | None, tuple[str, str]] = {  # the Reader's verb enum: (with a target, without one)
    "verb.move": ("move toward", "move"), "verb.observe": ("look at", "look around"),
    "verb.recall": ("think back on", "think back"), "verb.talk": ("speak to", "speak up"),
    "verb.strike": ("strike at", "strike out"), "verb.grapple": ("grapple with", "grapple"),
    "verb.force": ("force", "force a way through"), "verb.exert": ("strain against", "strain"),
    "verb.evade": ("evade", "dodge aside"), "verb.sneak": ("sneak past", "move quietly"),
    "verb.handle": ("work at", "work carefully"), "verb.endure": ("hold out against", "hold out"),
    "verb.setup": ("set things up against", "set things up"), "verb.help": ("help", "lend a hand"),
    "verb.ready": ("get ready for", "get ready"), None: ("turn to", "make the attempt"),
}

RELATIONS = {  # predicates the engine writes -> verb phrase (first word the lemma); the value is the object
    "owner": "belong to", "holder": "be held by", "held_by": "be held by", "carried_by": "be carried by",
    "worn_by": "be worn by", "location": "be at", "position": "be at", "kind": "be",
    **dict.fromkeys(("state", "condition", "desc", "posture", "mood", "demeanor", "look", "appearance"), "be"),
    **dict.fromkeys(("text", "content", "contents", "wording", "inscription", "writing", "words"), "read"),
    # 00.6.6a details (`detail.<slot>`) and the scene state code writes (12.11.9): the value is a state or a doing
    **dict.fromkeys(("detail.state", "detail.activity", "detail.manner", "detail.posture", "detail.mood",
                     "detail.look", "detail.stage", "alertness"), "be"),
    "detail.held": "hold", "detail.worn": "wear", "detail.clothing": "wear",
}
OMITTED = ("detail.", "wound_load", "harm_state", "voice")  # other slots and bookkeeping: no plain sentence ('')
PREPS = frozenset("by of in on at to from with for under near behind inside".split())
_LOC_PREPS = PREPS | frozenset((
    "beyond beside pushed set against above below within outside across along among amid between around over "
    "through past toward towards atop upon into onto beneath underneath here there up down hung hanging lying "
    "standing where just close").split())
_KEEP = frozenset("the a an his her their my your its this that these those someone".split())
_DET = frozenset("some any each every no one both all our another nobody everyone".split())
_ID = re.compile(r"[a-z]+(?:\.[a-z0-9_]+)+")


def forms(lemma: str) -> tuple[str, str, str]:
    """(third person singular, past, past participle) of a verb in the closed list."""
    if lemma in _IRREGULAR:
        return _IRREGULAR[lemma]
    if lemma in _MODALS:
        return lemma, _MODALS[lemma], _MODALS[lemma]
    if lemma not in _REGULAR:
        raise KeyError(f"verb {lemma!r} is not in the closed list (engine/text/render.py)")
    y = lemma.endswith("y") and lemma[-2:-1] not in "aeiou"
    s3 = lemma[:-1] + "ies" if y else lemma + "es" if lemma.endswith(("s", "sh", "ch", "x", "z", "o")) else lemma + "s"
    past = lemma[:-1] + "ied" if y else lemma + "d" if lemma.endswith("e") else lemma + "ed"
    return s3, past, past


Form = Literal["lemma", "s3", "past", "pp"]
_HEADS: dict[str, tuple[str, Form]] = {}
for _v in sorted(VERBS):  # later wins: a third-person form over a lemma over a past over a participle
    _s3, _past, _pp = forms(_v)
    _HEADS |= {_pp: (_v, "pp"), _past: (_v, "past"), _v: (_v, "lemma"), _s3: (_v, "s3")}
_HEADS |= {"are": ("be", "lemma"), "were": ("be", "past")}


def verb_head(word: str) -> tuple[str, Form] | None:
    """'carries' -> ('carry', 's3'), 'held' -> ('hold', 'pp'); None for a word not in the closed list."""
    return _HEADS.get(word.lower())


def the_name(name: str) -> str:
    """'bench' -> 'the bench'; a proper name or one with its own article stays as it is."""
    return name if not name[:1].islower() or name.split(" ", 1)[0] in _KEEP else f"the {name}"


def who(eid: str | None, *, names: Mapping[str, str] | None = None, pc: str | None = None) -> str:
    """An id as the player knows it (`names` from `narrator.name_of`, 12.10.2): 'you' for the PC, 'someone' for an
    id with no name; words that are not an id ('the bench') are already a noun phrase."""
    if not eid:
        return "someone"
    if eid == pc or eid.lower() == "you":
        return "you"
    if names is not None and eid in names:
        return the_name(names[eid]) if names[eid] else "someone"
    return "someone" if _ID.fullmatch(eid) else eid


def _verb(lemma: str, *, you: bool, neg: bool, tense: str) -> str:
    past = tense == "past"
    if lemma == "be":
        be = ("were" if you else "was") if past else ("are" if you else "is")
        return f"{be} not" if neg else be
    if lemma in _MODALS:
        m = _MODALS[lemma] if past else lemma
        return ("cannot" if m == "can" else f"{m} not") if neg else m
    if neg:
        return f"{'did' if past else 'do' if you else 'does'} not {lemma}"
    s3, past_form, _ = forms(lemma)
    return past_form if past else lemma if you else s3


def clause(subject: str | None, verb: str, obj: str | None = None, *, neg: bool = False,
           tense: Literal["present", "past"] = "present", plural: bool = False,
           names: Mapping[str, str] | None = None, pc: str | None = None) -> str:
    """Subject (an id, or words), a verb phrase whose first word is a lemma from `VERBS` ('think back on'), and an
    object in words. The verb agrees with whatever is printed in the subject slot ('you take', 'Tam takes'), or
    with a plural subject when the caller knows it is one."""
    # ponytail: a named subject is singular unless the caller says plural; an entity number field would settle it
    lemma, _, rest = verb.partition(" ")
    forms(lemma)  # KeyError outside the closed list
    subj = who(subject, names=names, pc=pc)
    v = _verb(lemma, you=plural or subj == "you", neg=neg, tense=tense)
    return " ".join(x for x in (subj, v, rest, obj) if x)


def slug_words(slug: str) -> str:
    """A predicate key as words: 'plane_s_iron' -> "plane's iron", 'sees_the_pc_coming' -> 'sees you coming'."""
    p = re.sub(r"\b(?:the )?pc s\b", "your", slug.replace("_", " ").replace(".", " "))
    return re.sub(r"\b(\w+) s\b", r"\1's", re.sub(r"\b(?:the )?pc\b", "you", p)).strip()


def relation(subject: str, predicate: str, value: str | None = None, *, neg: bool = False) -> str:
    """A fact as a clause: the registry's template, else a predicate that starts with a verb from the closed list
    ('was_last_seen_at', 'holds_the_rim'). A yes/no (`value` None) with no such verb is '' (never guessed);
    a valued one falls back to "the cart's colour: red", the value verbatim."""
    if predicate in RELATIONS:
        if value is None:
            return ""  # "condition: yes" says nothing
        verb = RELATIONS[predicate]
        if value is not None and predicate in ("location", "position"):
            first = value.split(" ", 1)[0].lower()
            verb = "be" if first in _LOC_PREPS or first.endswith("ed") else verb  # never "is at within" (P-040)
        elif value is not None and predicate == "kind" and value.split(" ", 1)[0].lower() not in _KEEP | _DET:
            value = np(value)
        if verb == "read":
            return f"{clause(subject, verb, neg=neg)}: {value}"  # the words themselves, verbatim
        return clause(subject, verb, value, neg=neg)
    if predicate.startswith(OMITTED):
        return ""
    w = slug_words(predicate).split()
    if w[:1] == ["whether"]:
        w = w[1:]
    if w[:1] and w[0] in ("it", "he", "she", "they"):
        w = w[1:]
    head = verb_head(w[0]) if w else None
    first = (value or "").split(" ", 1)[0].lower().strip(",")
    plural = False
    if head is not None and head[1] == "lemma":  # 'have', 'tie': a plural subject's verb; else a noun ('rest_of')
        plural = value is not None and subject[:1].islower() and subject.split(" ")[-1].endswith("s")
        head = head if plural else None
    if head is not None and (("or" in w) or (value is None and len(w) > 1 and w[1] in ("or", "and"))):
        head = None  # 'open_or_shut', 'guarded_or_unguarded': the question's options, not a statement
    tail = " ".join(x for x in (*w[1:], value) if x)
    if head is not None:
        lemma, form = head
        if value is None and (not w[1:] or w[-1] in PREPS or {"not", "does", "no", "and"} & set(w[1:2] + w[-2:])):
            return ""  # "belongs_to", "notices_the_pc_coming_does_not": not a whole statement
        content = [x for x in w if x not in _KEEP and x != "of"]
        if value is None and len(set(content)) < len(content):
            return ""  # 'rests_in_fingers_the_pc_s_fingers': a question slug with a doubled word, not a statement
        if form in ("past", "pp") and forms(lemma)[1] == forms(lemma)[2]:  # 'addressed_to' vs 'answered'
            form = "pp" if w[1:2] and w[1] in _LOC_PREPS | {"as"} else "past"
            if form == "past" and (value is None or first in _LOC_PREPS | {"yes", "no", "with"}):
                form = ""  # 'carved_subject', 'occupied: yes, by ...': a state, not a deed; said as a label below
        if form == "pp":
            return clause(subject, "be", f"{w[0]} {tail}", neg=neg)
        if form:
            return clause(subject, lemma, tail, neg=neg, tense="past" if form == "past" else "present", plural=plural)
    if value is None:
        return ""
    if w and w[-1] in PREPS:  # "adjacent_to", "part_of"
        return clause(subject, "be", f"{' '.join(w)} {value}", neg=neg)
    poss = "'" if subject.endswith("s") else "'s"
    return f"{subject}{poss} {' '.join(w)}: {value}"


_NUMBERS = "two three four five six seven eight nine ten eleven twelve".split()
_PLURAL = {"man": "men", "woman": "women", "child": "children", "foot": "feet", "tooth": "teeth", "mouse": "mice",
           "person": "people", "goose": "geese", "ox": "oxen", "sheep": "sheep", "deer": "deer", "fish": "fish"}
_VES = ("wolf", "leaf", "thief", "half", "shelf", "calf", "loaf", "knife", "wife", "life", "elf", "dwarf")


def article(word: str) -> str:
    """'a' or 'an' by sound, for the few spellings that differ: 'an hour', 'a unicorn'."""
    w = word.lower()
    vowel = w[:1] in tuple("aeiou") and not w.startswith(("uni", "use", "usu", "one", "eu", "ewe"))
    return "an" if vowel or w.startswith(("hour", "honest", "honou", "heir")) else "a"


def plural(noun: str) -> str:
    """The plural of a noun phrase's last word: 'wolf' -> 'wolves', 'rusty key' -> 'rusty keys'."""
    head, _, last = noun.rpartition(" ")
    lw = last.lower()
    if lw in _PLURAL:
        out = _PLURAL[lw]
    elif lw in _VES:
        out = last[:-2] + "ves" if lw.endswith("fe") else last[:-1] + "ves"
    elif lw.endswith(("s", "sh", "ch", "x", "z")):
        out = last + "es"
    elif lw.endswith("y") and lw[-2:-1] not in tuple("aeiou"):
        out = last[:-1] + "ies"
    else:
        out = last + "s"
    return f"{head} {out}" if head else out


def np(noun: str, n: int = 1, *, definite: bool = False) -> str:
    """A noun phrase with its article or number in words (no digits in fiction, 12.14.4): 'an owl', 'the owl',
    'three owls', 'many owls'."""
    if n == 1:
        return f"{'the' if definite else article(noun)} {noun}"
    count = "the" if definite else _NUMBERS[n - 2] if 2 <= n <= 12 else "many"
    return f"{count} {plural(noun)}"


def degree_words(degree: str | None, *, near_miss: bool = False, success_at_cost: bool = False) -> str:
    """A rolled beat's result in words (12.14.4); '' with no roll."""
    if degree is None:
        return ""
    if success_at_cost:
        return "it works, at a cost"
    return "it falls just short" if near_miss else DEGREE_WORDS.get(degree, "it is settled")


def sentence(text: str) -> str:
    """Capitalised, with a full stop unless it already ends a sentence; '' stays ''."""
    s = text.strip().rstrip(" ,;:—-")
    return "" if not s else s[0].upper() + s[1:] + ("" if s[-1] in ".!?\"”" else ".")
