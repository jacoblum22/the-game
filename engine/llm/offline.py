"""Offline stand-in and scripted test double for `StructuredModel` (contracts/model-calls.md, Offline stand-in).

`OfflineModel` is free and deterministic: each role proposes an answer from simple heuristics over the
packet (the player's message is `packet.message`) and the schema's enums, then `conform` repairs the proposal
against the schema, so the output is always schema-valid. It never calls a network and is never presented
as the real game. `ScriptedModel` serves queued responses per role for tests.
"""

from __future__ import annotations

import re
from collections import deque
from collections.abc import Callable, Iterable, Mapping
from functools import lru_cache
from typing import Any

import yaml

from engine.llm.base import CallResult, ModelError, Packet, Role, Stopwatch, new_record, resolve, validate
from engine.llm.env import REPO_ROOT

QUIET_TURNS_TO_CUT = 3  # Director: cut after this many quiet turns, read from a `quiet_turns: N` hint

# ---------------------------------------------------------------- schema helpers


def _options(node: Any, root: Mapping[str, Any]) -> list[Any]:
    """The non-null enum values a (possibly nullable) node allows."""
    node = resolve(node, root)
    if "enum" in node:
        return [o for o in node["enum"] if o is not None]
    if "const" in node:
        return [] if node["const"] is None else [node["const"]]
    out: list[Any] = []
    for key in ("anyOf", "oneOf"):
        for opt in node.get(key, []):
            out.extend(_options(opt, root))
    return out


def _object_node(node: Any, root: Mapping[str, Any]) -> dict[str, Any]:
    node = resolve(node, root)
    if "properties" in node:
        return node
    for key in ("anyOf", "oneOf", "allOf"):
        for opt in node.get(key, []):
            sub = _object_node(opt, root)
            if sub:
                return sub
    return {}


def _array_node(node: Any, root: Mapping[str, Any]) -> dict[str, Any]:
    node = resolve(node, root)
    if "items" in node or node.get("type") == "array":
        return node
    for key in ("anyOf", "oneOf"):
        for opt in node.get(key, []):
            sub = _array_node(opt, root)
            if sub:
                return sub
    return {}


def field(node: Any, root: Mapping[str, Any], *path: str) -> dict[str, Any]:
    """Walk `properties` by name; the segment `[]` steps into array items. {} when absent."""
    cur: Any = node
    for key in path:
        if key == "[]":
            cur = _array_node(cur, root).get("items", {})
        else:
            cur = _object_node(cur, root).get("properties", {}).get(key)
            if cur is None:
                return {}
    return resolve(cur, root)


def enum_at(schema: Mapping[str, Any], *path: str) -> list[Any]:
    node = field(schema, schema, *path)
    return _options(node, schema) if node else []


def _norm(s: Any) -> str:
    return re.sub(r"[\s_\-]+", " ", str(s).strip().lower())


def _pick_enum(value: Any, options: list[Any]) -> Any:
    if value in options:
        return value
    if value is not None and options:
        want = _norm(value)
        for opt in options:
            o = _norm(opt)
            if o == want or o.rsplit(".", 1)[-1] == want or want.rsplit(".", 1)[-1] == o:
                return opt
    return options[0] if options else None


def _allows_null(node: dict[str, Any], root: Mapping[str, Any]) -> bool:
    t = node.get("type")
    if t == "null" or (isinstance(t, list) and "null" in t):
        return True
    if "enum" in node and None in node["enum"]:
        return True
    return any(_allows_null(resolve(o, root), root) for k in ("anyOf", "oneOf") for o in node.get(k, []))


def conform(value: Any, node: Any, root: Mapping[str, Any]) -> Any:
    """Repair `value` into something `node` accepts; generates a minimal value where nothing fits.

    Prefers: the value itself; null where null is allowed and nothing was proposed; a fuzzy enum match;
    the first enum option. Unknown object keys are dropped; arrays are truncated or padded to their bounds.
    """
    node = resolve(node, root)
    if not validate_node(value, node, root):
        return value
    if "const" in node:
        return node["const"]
    if "enum" in node:
        return _pick_enum(value, list(node["enum"]))
    for key in ("anyOf", "oneOf"):
        if key in node:
            opts = [resolve(o, root) for o in node[key]]
            if value is None and _allows_null(node, root):
                return None
            non_null = [o for o in opts if not _allows_null(o, root)]
            for opt in non_null:
                fixed = conform(value, opt, root)
                if not validate_node(fixed, opt, root):
                    return fixed
            return None if _allows_null(node, root) else conform(value, opts[0], root)
    for opt in node.get("allOf", []):
        value = conform(value, opt, root)
    t = node.get("type")
    if isinstance(t, list):
        if value is None and "null" in t:
            return None
        t = next((x for x in t if x != "null"), None)
    if t is None and "properties" in node:
        t = "object"
    if t == "object":
        src = value if isinstance(value, dict) else {}
        props = node.get("properties", {})
        required = node.get("required", [])
        out: dict[str, Any] = {}
        for k, sub in props.items():
            if k in src:
                out[k] = conform(src[k], sub, root)
            elif k in required:
                out[k] = conform(None, sub, root)
        return out
    if t == "array":
        items = node.get("items", {})
        out_list = [conform(v, items, root) for v in (value if isinstance(value, list) else [])]
        if "maxItems" in node:
            out_list = out_list[: node["maxItems"]]
        while len(out_list) < node.get("minItems", 0):
            out_list.append(conform(None, items, root))
        return out_list
    if t == "string":
        text = "" if value is None or isinstance(value, dict | list) else str(value)
        if "maxLength" in node:
            text = text[: node["maxLength"]]
        return text.ljust(node.get("minLength", 0), ".")
    if t == "boolean":
        return value if isinstance(value, bool) else False
    if t in ("integer", "number"):
        num = value if isinstance(value, int | float) and not isinstance(value, bool) else node.get("minimum", 0)
        num = max(num, node.get("minimum", num))
        num = min(num, node.get("maximum", num))
        return int(num) if t == "integer" else num
    if t == "null":
        return None
    return value


def validate_node(value: Any, node: Mapping[str, Any], root: Mapping[str, Any]) -> list[str]:
    """`validate` for a sub-node, resolving `$ref`s against the root schema."""
    return validate(value, {**node, **{k: v for k, v in root.items() if k in ("$defs", "definitions")}})


# ---------------------------------------------------------------- text helpers

_QUOTE = re.compile(r"\"[^\"]*\"|“[^”]*”")


def sentences(text: str) -> list[str]:
    """Split into sentences, keeping quoted speech whole."""
    quotes: list[str] = []

    def hide(m: re.Match[str]) -> str:
        quotes.append(m.group(0))
        ends = "\x01" if re.search(r"[.!?]\W*$", m.group(0)) else ""  # a quote ending a sentence
        return f"\x00{len(quotes) - 1}\x00{ends}"

    masked = _QUOTE.sub(hide, text.strip())
    parts = [p.replace("\x01", "").strip() for p in re.split(r"(?<=[.!?\x01])\s+(?=[A-Z\"“])|(?<=[.!?])\s+|\n+", masked)]
    parts = [p for p in parts if p]
    return [re.sub(r"\x00(\d+)\x00", lambda m: quotes[int(m.group(1))], p) for p in parts]


def _has_word(text: str, phrase: str) -> bool:
    return re.search(rf"(?<![\w]){re.escape(phrase)}(?![\w])", text, re.IGNORECASE) is not None


_SCOPE_WORDS = ("here", "not here", "new this turn")


def entity_aliases(ids: Iterable[Any], context: str) -> dict[str, list[str]]:
    """Lower-case names per entity id: the id, its last segment as words, and text beside it in the packet."""
    out: dict[str, list[str]] = {}
    for eid in ids:
        if not isinstance(eid, str) or eid in ("none", "unknown", "new_npc"):
            continue
        tail = re.split(r"[.:/]", eid)[-1]
        words = _norm(tail)
        names = {eid.lower(), words}
        names.update(w for w in words.split() if len(w) >= 3 and w not in _STOP)
        for line in context.splitlines():
            if eid in line and not line.lstrip().startswith("declares:"):  # the Checker's declaration lines
                rest = line.split(eid, 1)[1]
                for chunk in re.split(r"[:,;|()\[\]—–]|\baliases?\b|\baka\b", rest):
                    chunk = chunk.strip(" -\t'\"").lower()
                    if chunk in _SCOPE_WORDS:  # the Checker view's `; here` / `; not here` (spec 009 B)
                        continue
                    if 2 < len(chunk) < 40 and not re.search(r"[\d.]", chunk):
                        names.add(chunk)
        out[eid] = sorted(names, key=len, reverse=True)
    return out


def named_entity(text: str, aliases: Mapping[str, list[str]]) -> tuple[str, str] | None:
    """The first entity (by position in `text`) one of whose aliases appears; (id, matched alias)."""
    best: tuple[int, str, str] | None = None
    for eid, names in aliases.items():
        for name in names:
            m = re.search(rf"(?<![\w]){re.escape(name)}(?![\w])", text, re.IGNORECASE)
            if m and (best is None or m.start() < best[0]):
                best = (m.start(), eid, m.group(0))
    return (best[1], best[2]) if best else None


_STOP = {
    "the", "a", "an", "you", "your", "scene", "place", "present", "cast", "view", "name", "npc", "pc",
    "location", "time", "known", "facts", "items", "exits", "here", "it", "he", "she", "they", "this",
    "that", "there", "in", "on", "at", "of", "and", "or", "with", "none", "who", "what", "where", "role",
    "rules", "rule", "core", "cards", "message", "recent", "exchanges", "narrator", "instructions",
}


def view_names(view: str) -> list[str]:
    """Display names in the narrator view: `name: X` entries, else capitalised phrases. Never digits."""
    found = re.findall(r"(?im)\bname\s*[:=]\s*([^\n,;|()\[\]]+)", view)
    if not found:
        found = re.findall(r"\b[A-Z][a-z'’]+(?:\s+[A-Z][a-z'’]+){0,2}\b", view)
    out: list[str] = []
    for raw in found:
        name = raw.strip().strip("'\"")
        if not name or re.search(r"\d", name) or name.lower() in _STOP or name in out:
            continue
        out.append(name)
    return out


# ---------------------------------------------------------------- basic verbs

_EXTRA_VERB_WORDS = {
    "verb.move": ["go", "walk", "run", "head", "approach", "step", "enter", "leave", "flee", "follow"],
    "verb.observe": ["look", "examine", "inspect", "watch", "scan", "check", "peer", "investigate"],
    "verb.talk": ["say", "tell", "talk", "speak", "greet", "beg", "plead", "negotiate"],
    "verb.strike": ["fight", "slash", "kick", "swing at", "fire at", "shoot at"],
    "verb.grapple": ["grapple", "hold down"],
    "verb.force": ["force", "kick down", "batter"],
    "verb.sneak": ["steal", "pickpocket", "slip away"],
    "verb.handle": ["open", "pick up", "take", "light", "tie", "search my pack"],
    "verb.recall": ["think back", "try to remember"],
    "verb.endure": ["brace", "hold on"],
    "verb.help": ["aid"],
    "verb.ready": ["get ready", "prepare to", "wait until"],
}


@lru_cache(maxsize=1)
@lru_cache(maxsize=1)
def basic_verbs() -> list[dict[str, Any]]:
    data = yaml.safe_load((REPO_ROOT / "rules" / "data" / "basic_verbs.yaml").read_text(encoding="utf-8"))
    return list(data["verbs"])


@lru_cache(maxsize=1)
def verb_keywords() -> dict[str, list[str]]:
    """verb id → keyword phrases, from rules/data/basic_verbs.yaml (name, covers, intent_verbs) plus synonyms."""
    out: dict[str, list[str]] = {}
    for verb in basic_verbs():
        words = {verb["name"].lower()}
        words.update(str(w).lower() for w in verb.get("anchor", {}).get("intent_verbs", []))
        for cover in verb.get("covers", []):
            words.add(re.sub(r"\s*\(.*\)", "", str(cover)).lower().strip())
        words.update(_EXTRA_VERB_WORDS.get(verb["id"], []))
        out[verb["id"]] = sorted((w for w in words if w and "x" not in w.split()), key=len, reverse=True)
    return out


# The everyday verb a sentence leads with decides the basic verb (rules/data/basic_verbs.yaml's names and covers:
# Observe searches and studies, Talk asks and persuades, Exert climbs and jumps, Move goes and runs, Strike
# attacks, Sneak hides, Grapple seizes, Force breaks, Evade dodges, Recall remembers, Handle uses things).
PRIMARY_VERBS: dict[str, tuple[str, ...]] = {
    "verb.observe": ("look", "search", "examine", "inspect", "study", "listen", "watch", "peer", "scan", "check",
                     "investigate", "observe", "survey", "spot", "track", "read"),
    "verb.talk": ("ask", "tell", "talk", "speak", "say", "persuade", "convince", "greet", "plead", "haggle",
                  "bargain", "threaten", "lie", "question", "chat", "call", "shout", "warn", "negotiate", "sing",
                  "perform", "joke", "introduce myself", "thank"),
    "verb.exert": ("climb", "jump", "leap", "swim", "vault", "lift", "carry", "haul", "balance", "scale"),
    "verb.move": ("go", "run", "walk", "head", "travel", "move", "approach", "enter", "leave", "follow", "return",
                  "cross", "ride", "hurry", "dash", "retreat", "make my way", "set out"),
    "verb.strike": ("attack", "hit", "strike", "stab", "slash", "punch", "shoot", "fight", "kick", "swing", "cut"),
    "verb.sneak": ("sneak", "hide", "creep", "steal", "pickpocket", "slip past", "lurk", "conceal"),
    "verb.grapple": ("grab", "grapple", "wrestle", "pin", "seize", "tackle", "restrain"),
    "verb.force": ("break", "smash", "force", "shove", "push", "pry", "batter", "kick down"),
    "verb.evade": ("dodge", "duck", "evade", "dive clear"),
    "verb.recall": ("remember", "recall", "recognize", "think back"),
    "verb.handle": ("open", "use", "light", "bandage", "mend", "pick up", "take", "tie", "cook", "repair", "eat",
                    "drink", "sit", "wait", "pray", "buy", "pay", "give", "put", "drop", "wash"),
}


def primary_verb(text: str) -> tuple[str, list[str]] | None:
    """The basic verb of the first everyday verb in `text` ("climb onto the roof" climbs: Exert)."""
    best: tuple[int, int, str, str] | None = None
    for vid, words in PRIMARY_VERBS.items():
        for w in words:
            m = re.search(rf"(?<![\w]){re.escape(w)}(?:s|es|ed|ing)?(?![\w])", text, re.IGNORECASE)
            if m and (best is None or (m.start(), -len(w)) < (best[0], best[1])):
                best = (m.start(), -len(w), vid, w)
    return (best[2], [best[3]]) if best else None


def _excluding_verb(text: str) -> str | None:
    """The basic verb whose `excludes` names this act (a literal mention), if any."""
    from engine.resolve.gate import excluded_by

    return next((v["id"] for v in basic_verbs() if excluded_by(v, text) is not None), None)


def match_verb(text: str) -> tuple[str, list[str]] | None:
    """The basic verb whose longest keyword occurs in `text`, with every matched keyword."""
    best: tuple[int, str] | None = None
    hits: dict[str, list[str]] = {}
    for vid, words in verb_keywords().items():
        for w in words:
            if _has_word(text, w):
                hits.setdefault(vid, []).append(w)
                if best is None or len(w) > best[0]:
                    best = (len(w), vid)
    return (best[1], hits[best[1]]) if best else None


RISKY_WORDS = [
    "attack", "stab", "shoot", "fight", "kill", "climb", "jump", "leap", "swim", "steal", "sneak", "lie",
    "deceive", "threaten", "intimidate", "break", "smash", "force", "flee", "dodge", "grab", "tackle",
    "pick the lock", "hide", "chase", "dive", "vault", "punch", "slash", "run past", "bluff", "snatch",
]
OOF_WORDS = ["rule", "rules", "roll", "dice", "dc", "modifier", "stat", "mechanic", "bonus", "hit points",
             "my options", "what can i do", "what do i know", "what now", "what should i do", "stuck", "my sheet",
             "my journal"]


def _restate(text: str) -> str:
    swaps = {"i": "you", "i'm": "you're", "i'll": "you'll", "my": "your", "me": "you", "myself": "yourself",
             "am": "are", "mine": "yours"}
    out = re.sub(r"\b(i'm|i'll|myself|mine|my|me|am|i)\b", lambda m: swaps[m.group(1).lower()], text,
                 flags=re.IGNORECASE)
    return out[:1].upper() + out[1:] if out else out


# ---------------------------------------------------------------- role heuristics

_SPECIAL_CHOICES = ("own_words", "move_on", "details", "suggest")


def _interpret(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:
    msg = packet.message.strip()
    low = msg.lower()
    choices = enum_at(schema, "choice")
    options = [c for c in choices if c not in _SPECIAL_CHOICES]
    out: dict[str, Any] = {"own_words_class": None, "own_words_text": None, "lines_and_veils": [], "answer": None}
    m = re.fullmatch(r"\s*(?:option\s*)?#?(\d+)[.)]?\s*", low)
    if not msg or low in ("skip", "move on", "pass", "next", "default"):
        return {**out, "choice": "move_on"}
    if m and 1 <= int(m.group(1)) <= len(options):
        return {**out, "choice": options[int(m.group(1)) - 1]}
    if low.rstrip().endswith("?") or _has_word(low, "show all"):  # a question about the step, not an answer
        return {**out, "choice": "details"}
    for opt in options:
        label = _norm(str(opt).rsplit(".", 1)[-1])
        if low == str(opt).lower() or (len(label) >= 3 and _has_word(low, label)):
            return {**out, "choice": opt}
    if any(_has_word(low, w) for w in ("details", "tell me more", "more about", "explain")):
        return {**out, "choice": "details"}
    if any(_has_word(low, w) for w in ("suggest", "you pick", "you choose", "surprise me", "dealer's choice")):
        return {**out, "choice": "suggest"}
    classes = enum_at(schema, "own_words_class")
    labels = _block_options(packet.render())
    scored = sorted(((_overlap(msg, lab), i) for i, lab in enumerate(labels[: len(options)])), reverse=True)
    if scored and scored[0][0] >= 0.5 and len(_content(msg)) >= 2:  # a clear paraphrase of one option
        opt = options[scored[0][1]]
        return {**out, "choice": opt, "own_words_class": _pick_enum(opt, classes) if opt in classes else None,
                "own_words_text": None}
    best = max(classes, key=lambda c: (_overlap(msg, _norm(c) + " " + _label_for(c, options, labels)),
                                       -classes.index(c)), default=None)
    return {**out, "choice": "own_words", "own_words_class": best, "own_words_text": msg}


_FILLER = {"the", "a", "an", "of", "and", "or", "to", "in", "on", "at", "is", "are", "it", "its", "do", "does", "not",
           "no", "i", "my", "me", "we", "our", "they", "their", "this", "that", "with", "for", "be", "was", "were",
           "who", "what", "one", "some", "any", "there", "here", "have", "has", "had", "but", "so", "very"}


def _content(text: str) -> set[str]:
    """Content words, crudely stemmed (dead / deaths / dying share nothing; graves / grave do)."""
    words = re.findall(r"[a-z']+", str(text).lower())
    return {re.sub(r"(?:ies|es|s|ed|ing)$", "", w) or w for w in words if w not in _FILLER and len(w) > 2}


def _overlap(msg: str, label: str) -> float:
    """The share of the message's content words that the label also uses."""
    m = _content(msg)
    return len(m & _content(label)) / len(m) if m else 0.0


def _block_options(context: str) -> list[str]:
    """The lettered options of the last question block shown before THIS MESSAGE, in order."""
    head = context.split("[THIS MESSAGE]")[0]
    start = max(head.rfind("[SEED"), head.rfind("[CREATE"))
    return [m.group(1) for m in re.finditer(r"(?m)^\s*\([a-z]\)\s+(.*)$", head[max(start, 0):])]


def _label_for(cls: Any, options: list[Any], labels: list[str]) -> str:
    """The shown label of the option a classification id names (same id, or its last segment), else ""."""
    for i, opt in enumerate(options[: len(labels)]):
        if _norm(opt) == _norm(cls) or _norm(opt).rsplit(".", 1)[-1] == _norm(cls).rsplit(".", 1)[-1]:
            return labels[i]
    return ""


def _reader(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:
    # rule: 12.2.2 (message classes), 01.2.3 (≤3 beats), 01.3.1 (gate), 01.4.1 (necessity), 01.2.6
    context = packet.render()
    targets = entity_aliases(enum_at(schema, "beats", "[]", "target"), context)
    subjects = entity_aliases(enum_at(schema, "fact_questions", "[]", "subject"), context)
    pending = enum_at(schema, "pending_answer")
    rungs = enum_at(schema, "fact_questions", "[]", "odds_rung")
    parts, questions, beats, declared = [], [], [], []
    pending_answer = None
    for sent in sentences(packet.message):
        low = sent.lower().strip(" .!")
        picked = _pending_pick(low, pending) if pending_answer is None else None
        if picked is not None:
            pending_answer = picked
            parts.append({"text": sent, "class": "PENDING_ANSWER", "question_kind": "none", "topic": None})
        elif _QUOTE.search(sent):
            parts.append({"text": sent, "class": "SPEECH", "question_kind": _kind(sent), "topic": None})
        elif not re.search(r"[A-Za-z]{2}", sent):
            parts.append({"text": sent, "class": "OOF_QUESTION", "question_kind": "none", "topic": None})
        elif sent.rstrip().endswith("?") or _ASKS.match(sent):
            oof = "/" in sent or any(_has_word(sent, w) for w in OOF_WORDS)
            parts.append({"text": sent, "class": "OOF_QUESTION" if oof else "FICTION_QUESTION",
                          "question_kind": "none" if oof else _kind(sent), "topic": None})
            if not oof and not _WH.match(sent):  # only a yes/no question goes to the Oracle; "who is here?" is
                # answered from what the scene shows
                hit = named_entity(sent, subjects)
                questions.append({
                    "subject": hit[0] if hit else None, "predicate": sent.rstrip("?").strip(),
                    "odds_rung": rungs[len(rungs) // 2] if rungs else None,
                })
        else:
            parts.append({"text": sent, "class": "DECLARATION", "question_kind": _asked_kind(sent), "topic": None})
            declared.append(sent)
    for sent in declared[:3]:
        verb = primary_verb(sent) or match_verb(sent)
        target = named_entity(sent, targets)
        if not verb and target and str(target[0]).startswith(("npc.", "ally.", "foe.")):  # words to someone: talk
            verb = ("verb.talk", [])
        elif not verb and (ex := _excluding_verb(sent)) is not None:  # "pick the lock": Force names it (G3)
            verb = (ex, [])
        v = verb[0] if verb else None
        beats.append({
            "intent": sent, "method": sent, "purpose": "own_change", "assertion": None, "shape": "now",
            "target": target[0] if target else "none", "verb": v,
            "pressure": "request" if v == "verb.talk" else "none",  # offline Talk is a declared ask (12.2.2)
            # 12.2.2 facets: force against someone; words; a power word (the gate is computed, 00.12.3)
            "against_will": v in ("verb.strike", "verb.grapple") or (v == "verb.force" and bool(target) and str(
                target[0]).startswith(("npc.", "foe."))),
            "uses_power": any(_has_word(sent, w) for w in POWER_WORDS),
            "speech": v == "verb.talk", "g4_fact": None,
            "intent_verbs": verb[1] if verb else [],
        })
    quantity = re.search(r"\b(\d+)\b", packet.message)
    restated = " ".join(_restate(s) for s in declared) or _restate(packet.message.strip())
    return {
        "parts": parts, "pending_answer": pending_answer, "fact_questions": questions, "beats": beats,
        "clarifying_question": None, "restatement": restated,
        "player_quantity": int(quantity.group(1)) if quantity else None,
    }


POWER_WORDS = ["spell", "magic", "witch-sight", "mind-touch", "sorcery", "conjure"]
_KINDS = (("who_knows", r"\bwho\b[\w ]{0,20}\b(?:would|might|could) know\b"), ("who_is", r"^\s*(?:\w+,\s*)?who\b"),
          ("where_is", r"^\s*(?:\w+,\s*)?where\b"), ("what_happened", r"\bwhat happened\b"),
          ("what_want", r"\bwhat do you (?:want|think)\b"), ("what_like", r"^\s*(?:\w+,\s*)?what\b"))


def _kind(sent: str) -> str:  # 12.2.2 question_kind, from the question's first word
    said = sent.strip(" \"'“”‘’")  # a quoted question starts at its first word
    return next((k for k, rx in _KINDS if re.search(rx, said, re.IGNORECASE)), "none") if "?" in sent else "none"


_ASKED = re.compile(r"\bask(?:s|ed|ing)?\b(?:[^.?!]*?\b(who|where|what|when|why|how)\b(.*)|.*\babout\b)", re.I)


def _asked_kind(sent: str) -> str:  # 12.2.2: "I ask Mira what is going on" carries a question too
    m = _ASKED.search(sent)
    if m is None:
        return "none"
    return (_kind(f"{m.group(1)}{m.group(2)}?") if m.group(1) else "none").replace("none", "what_like")


_WH = re.compile(r"^\s*(?:\w+,\s*)?(?:what|who|whom|whose|where|when|why|how|which)\b", re.IGNORECASE)
_ASKS = re.compile(r"^\s*(?:what|who|whom|whose|where|when|why|how|which|is|are|was|were|do|does|did|can|could|"
                   r"would|will|should|has|have|had)\b[^.!]*$", re.IGNORECASE)


def _pending_pick(low: str, pending: list[Any]) -> Any:
    m = re.fullmatch(r"#?(\d+)", low)
    if m and 1 <= int(m.group(1)) <= len(pending):
        return pending[int(m.group(1)) - 1]
    return next((p for p in pending if low in (_norm(p), str(p).lower())), None)


_HEIGHT = re.compile(r"\b(climb\w*|clamber\w*|scal(?:e|es|ing)|jump\w*|leap\w*|vault\w*|roof\w*|wall\w*|cliff\w*|"
                     r"ledge\w*|tree\w*|tower\w*|rope\w*|heights?)\b", re.IGNORECASE)
_WATER = re.compile(r"\b(swim\w*|wade|wading|current|river|ford)\b", re.IGNORECASE)
_PEOPLE = ("npc.", "foe.", "ally.", "pc.")


def _stakes(verb_word: str | None, message: str, view: str, sources: list[Any],
            menus: list[Any]) -> tuple[str | None, list[str]]:
    # rule: 01.6.9 (an established source that would impose a cost if this beat failed; none -> Safe)
    """(stakes source, threatened-cost menus in preference order) for what the act plainly risks: attacking or
    sneaking past someone present (they are aware, or may notice), a fall from a height, the water. A source the
    schema does not offer, or no fitting menu, keeps the beat Safe."""
    target = (re.search(r"(?m)^target: (\S+)", message) or [None, "none"])[1]
    act = " ".join(re.findall(r"(?m)^(?:beat|intent|method): (.*)$", message)) or message
    someone = str(target).startswith(_PEOPLE) or bool(re.search(r"(?m)^(?:npc|foe)\.[\w.]+: ", view))
    pick: tuple[str, list[str]] | None = None
    if verb_word in ("strike", "grapple") and someone:
        pick = ("aware_opponent_or_observer", ["cost.footing", "cost.exposure"])  # harm from them needs a cited fact
    elif verb_word == "force" and str(target).startswith(_PEOPLE):
        pick = ("aware_opponent_or_observer", ["cost.footing", "cost.harm"])
    elif verb_word in ("exert", "move", "evade") and _HEIGHT.search(act):
        pick = ("height_or_depth", ["cost.harm", "cost.footing"])
    elif verb_word in ("exert", "move") and _WATER.search(act):
        pick = ("hazard", ["cost.footing", "cost.harm"])
    elif verb_word == "sneak":
        pick = ("aware_opponent_or_observer", ["cost.exposure"])
    if pick is None or pick[0] not in sources:
        return None, []
    fitting = [m for m in pick[1] if m in menus]
    return (pick[0], fitting) if fitting else (None, [])


# the cost's form in words per stakes source and menu ("" = the engine's own words for the menu entry)
_FORMS: dict[str, dict[str, str]] = {
    "height_or_depth": {"cost.harm": "a fall, and a hard landing", "cost.footing": "you slip and lose your hold",
                        "cost.shortfall": "you get less far than you meant"},
    "aware_opponent_or_observer": {"cost.harm": "a blow taken in return", "cost.footing": "you are knocked off balance",
                                   "cost.exposure": "you are seen", "cost.shortfall": "less comes of it than you meant"},
    "hazard": {"cost.footing": "the current takes your footing", "cost.harm": "the water batters you",
               "cost.shortfall": "you get less far than you meant"},
}


def _obstacle(schema: dict[str, Any], quiet: bool) -> dict[str, Any]:
    # rule: 01.6.5 (class `other` at the middle rung, Moderate, so the offline odds stay comparable across runs);
    # a social or attack beat on a person offers only the defender's defense (01.6.4); with nothing at stake
    # (`quiet`) the verb's trivial class when it has one (looking about, walking open ground: no roll, 01.4.1)
    node = field(schema, schema, "obstacle")
    branches = node.get("anyOf") or [node]
    kinds = {_options(b["properties"]["kind"], schema)[0]: b for b in branches if "properties" in b}
    if "tier" not in kinds:
        k = "opposed" if "opposed" in kinds else next(iter(kinds))
        return {"kind": k, "obstacle_class": None, "tier": None,
                "entity": _options(kinds[k]["properties"]["entity"], schema)[0]}
    classes = [c for b in branches if "properties" in b for c in _options(b["properties"].get("obstacle_class", {}),
                                                                          schema)]
    trivial = {str(c["id"]) for v in basic_verbs() for c in (v.get("anchor") or {}).get("obstacle_classes") or ()
               if c.get("base") == "trivial"}
    easy = next((c for c in classes if c in trivial), None)
    if quiet and easy:
        return {"kind": "tier", "obstacle_class": easy, "tier": None, "entity": None}
    tier_opts = [t for b in branches if "properties" in b for t in _options(b["properties"].get("tier", {}), schema)]
    tier = "moderate" if "moderate" in tier_opts else (tier_opts[len(tier_opts) // 2] if tier_opts else None)
    return {"kind": "tier", "obstacle_class": "other", "tier": tier, "entity": None}


def _framer(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:
    text = packet.render()
    anchors = enum_at(schema, "anchor")
    gate_verb = re.search(r"(?m)^gate: .*\bverb: verb\.(\w+)", packet.message)  # the beat's own verb first
    mentioned = [gate_verb.group(1)] if gate_verb else re.findall(r"verb\.(\w+)", text)
    verb_word = mentioned[0] if mentioned else None
    if verb_word is None:
        hit = match_verb(packet.message)
        verb_word = hit[0].split(".", 1)[1] if hit else None
    anchor = next((a for a in anchors if verb_word and verb_word in str(a)), anchors[0] if anchors else None)
    attrs = enum_at(schema, "attribute")
    verb_attr = None
    if verb_word:
        verb_attr = next((v["attribute"] for v in basic_verbs() if v["id"] == f"verb.{verb_word}"), None)
    menus = enum_at(schema, "threatened_cost", "menu_id")
    alt_menus = enum_at(schema, "alternate_cost", "menu_id") or menus
    source, fitting = _stakes(verb_word, packet.message, packet.view, enum_at(schema, "stakes_source"), menus)
    threatened = fitting[0] if fitting else (menus[0] if menus else None)
    if source:  # an alternate that fits through the same source (cost.shortfall always does)
        alts = [m for m in ("cost.shortfall", "cost.footing", "cost.harm", "cost.time") if m in alt_menus]
        alternate = next((m for m in alts if m != threatened), None)
    else:
        alternate = alt_menus[1] if len(alt_menus) > 1 else (alt_menus[0] if alt_menus else None)
    forms = _FORMS.get(source or "", {})
    attribute = verb_attr if verb_attr in attrs else (attrs[0] if attrs else None)
    if "chose CHANGE" in packet.message:  # 01.7.1: another approach for the same intent
        attribute = next((a for a in attrs if a != attribute), attribute)
    return {
        "anchor": anchor, "deltas": [],
        "attribute": attribute,
        "deed_tag": None, "traits": [],
        "obstacle": _obstacle(schema, quiet=source is None),
        "nudge_why": None, "nudge": "0", "nudge_fact": None, "request_size": "R2",
        "levers": [], "snags": [], "stakes_source": source,
        "stakes_heavy": False, "lethal": False, "reach_whole": False, "reach_one_factor": False,
        "threatened_cost": {"menu_id": threatened, "form_intent": forms.get(str(threatened), "")},
        "alternate_cost": {"menu_id": alternate, "form_intent": forms.get(str(alternate), "")},
        "method_consequences": [], "secret": False,
    }


def _engaged(npcs: list[Any], happened: str, view: str) -> list[Any]:
    """The present NPCs this turn's acts engage (12.2.9: an NPC responds to what it could respond to): named or
    targeted, or the first present one when the player speaks or talks to no one in particular."""
    names = {str(n): [str(n).lower()] for n in npcs}
    for n in npcs:  # the World view's `  npc.x: Name; standing ...` lines
        m = re.search(rf"(?m)^[\s-]*{re.escape(str(n))}: (?:name: )?([^;,\n]+)", view)
        if m and m.group(1).strip():
            names[str(n)] += [m.group(1).strip().lower(), m.group(1).strip().split()[0].lower()]
    hit = [n for n in npcs if any(_has_word(happened, a) for a in names[str(n)]
                                  if len(a) > 2 and a not in _STOP and a not in _FILLER)]
    if hit:
        return hit
    spoke = re.search(r"\((?:SPEECH)\)$", happened, re.MULTILINE) or re.search(
        r"(?m)^beat: .*\b(ask|asks|tell|tells|talk|talks|greet|greets|say|says|speak|speaks|call|calls)\b", happened)
    return list(npcs[:1]) if spoke else []


def _proposer(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:  # rule: PR-12-10
    """Rung 3 offline: one bland ordinary candidate on the asked topic (`topic: <key>` in the message)."""
    m = re.search(r"^topic: ([\w-]+)", packet.message, re.MULTILINE)
    topic = (m.group(1) if m else "local_news").replace("_", " ")
    return {"kind": "ordinary_fact", "subject": f"talk of {topic}", "predicate": "is",
            "value": "nothing out of the ordinary this season"}


def _locator(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:  # rule: PR-12-11
    """Step 1 offline: the candidate turn sharing the most words (4+ letters) with the report; the category from
    the report's words (a stand-in for the model's judgement)."""
    m = re.search(r'^THE PLAYER\'S REPORT: "(.*)"$', packet.message, re.MULTILINE)
    report = (m.group(1) if m else "").lower()
    words = {w for w in re.findall(r"[a-z]{4,}", report)}
    best, score = "none", 0
    for tid, text in re.findall(r"^(turn\.\d+) \| (.*)$", packet.message, re.MULTILINE):
        n = len(words & set(re.findall(r"[a-z]{4,}", text.lower())))
        if n > score:
            best, score = tid, n
    category = ("misread" if re.search(r"\b(meant|didn'?t|did not|never (?:said|asked|tried)|only)\b", report) else
                "rule_wrong" if re.search(r"\b(dc|odds|roll|modifier|harder|easier|chance)\b", report) else
                "contradiction" if re.search(r"\b(earlier|before|just said|contradict)", report) else
                "remembered_wrong" if re.search(r"\b(name|remember|forgot|told me)\b", report) else "other")
    return {"turn": best, "quote": "", "category": category, "subject": "", "key": "", "value": ""}


def _world(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:
    npcs = enum_at(schema, "responses", "[]", "npc")
    return {"responses": [
        {"npc": n, "want_engaged": None, "refusal_engaged": None, "table_context": {"tags": []}}
        for n in _engaged(npcs, packet.message, packet.view)
    ]}


_GOING = re.compile(r"\b(go|goes|going|head|heads|travel|travels|leave|leaves|walk|walks|ride|rides|return|returns|"
                    r"set out|make (?:my|our) way|move on|cross|crosses)\b", re.IGNORECASE)


def _player_message(message: str) -> str:
    m = re.search(r"THE PLAYER'S MESSAGE: \"?(.*?)\"?$", message, re.MULTILINE)
    return "" if not m or m.group(1).strip() == "(none)" else m.group(1).strip()


def _director(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:
    context = packet.render()
    m = re.search(r"quiet[_ ]turns\s*[:=]\s*(\d+)", context, re.IGNORECASE)
    cut = bool(m and int(m.group(1)) >= QUIET_TURNS_TO_CUT)
    place = None
    said = _player_message(packet.message)
    places = enum_at(schema, "next_scene", "place")
    if said and _GOING.search(said) and places:  # "I go to the smithy": cut to that reachable place
        here = re.search(r"(?m)^\s*position: (\S+)", context)
        names = dict(re.findall(r"(?m)^- ([\w.]+): (.+)$", packet.message))  # the PLACES lines, one per place
        aliases: dict[str, list[str]] = {}
        for pid in places:
            if here and pid == here.group(1):
                continue
            nm = names.get(pid, "").strip().lower()
            aliases[pid] = [x for x in (nm, nm.removeprefix("the "), _norm(pid.rsplit(".", 1)[-1])) if len(x) > 2]
        hit = named_entity(said, aliases)
        if hit:
            cut, place = True, hit[0]
    # someone to talk to in the new scene: PR-12-5 meets a resident of the place first, else a walk-on
    cast = ["new_npc"] if "new_npc" in enum_at(schema, "next_scene", "cast", "[]") else []
    return {
        "cut_now": cut,
        "next_scene": {
            "mode": "free", "place": place, "agenda": _agenda(packet, place),
            "hoped_answer": "you get what you came for", "pillar": None, "challenge_type": None, "cast": cast,
        },
        "push": "none", "lead": None,
    }


def _agenda(packet: Packet, place: Any) -> str:
    """The scene's question in neutral words (12.4.2), from what the packet holds: the opening's incident, the
    place the player heads for, else the first open thread the view lists; "" when there is nothing to ask."""
    raised = re.search(r"(?m)^RAISED: .*inciting incident[^:]*: (.+)$", packet.message)
    if raised:
        return f"What comes of it: {raised.group(1).strip().rstrip('.')}?"
    names = dict(re.findall(r"(?m)^- ([\w.]+): (.+)$", packet.message))
    if place and names.get(str(place)):
        return f"What is to be found at {names[str(place)].strip()}?"
    threads = re.search(r"(?m)^open threads: (?:thr\.\S+) ([^;\n]+)", packet.render())
    if threads:
        text = re.split(r"(?<=[.!?])\s|;", threads.group(1).strip())[0].rstrip(" .")
        return f"Where does it lead: {text}?" if text else ""
    return ""


_RESULTS = [  # result words of the record's beat lines (engine/dm/roles/narrator.py DEGREE_WORDS), most specific first
    ("success at cost", "It works, but not cleanly."),
    ("critical success", "It works, and better than anyone could expect."),
    ("critical failure", "It goes badly wrong."),
    ("a near miss", "It almost holds, and everything hangs on the next breath."),
    ("failure", "It does not work, and the moment turns against you."),
    ("success", "It works."),
]
_ANSWERS = {"yes": "Yes, that is so.", "no": "No, it is not so.", "yes, and": "Yes, and more than that.",
            "yes, but": "Yes, though not cleanly.", "no, and": "No, and worse than that.",
            "no, but": "No, though not entirely."}


def _sentence(text: str) -> str:
    t = re.sub(r"\b(?:the character|the PC)\b", "you", text.strip().strip('"').rstrip(" .;"))
    return (t[:1].upper() + t[1:] + ".") if t else ""


def _reach_sentence(delivered: str) -> str:
    """The record's `delivered: <reach>: <ladder words>` as a sentence of fiction, or "" (12.14.4: no ids or
    numbers; Standard reach is what was intended, already said by the result line)."""
    reach, _, words = delivered.partition(": ")
    words = words.strip()
    if not words or reach == "standard" or re.search(r"\d|\b[a-z]+\.[a-z_]+\b", words):
        return ""
    head, _, detail = words.partition(" (")
    detail = detail.rstrip(")").strip()
    if reach == "limited":
        if head.startswith("partway"):
            return _sentence("You get partway" + (f": {detail}" if detail else ""))
        return _sentence(f"Only in part: {head}" + (f", {detail}" if detail else ""))
    return _sentence(f"Better than that: {head}" + (f", {detail}" if detail else ""))


# tbl.npc_action rows (12.11.5: the DM chooses the words): phrasings that keep the row's own words, so a row that
# comes up again for the same person is not told the same way twice running
_NPC_ROW_WORDS: list[tuple[str, list[str]]] = [
    ("escalates", ["{n} escalates, and threatens you.", "{n} turns threatening.", "{n} threatens to call for others."]),
    ("ends the exchange", ["{n} ends the exchange and withdraws.", "{n} withdraws without another word.",
                           "{n} ends the exchange there."]),
    ("hinders quietly", ["{n} hinders you quietly, and delays.", "{n} quietly misdirects you.",
                         "{n} delays, hindering you quietly."]),
    ("wants something first", ["{n} wants something first, and names a price.", "{n} names a price first.",
                               "{n} wants a favor first."]),
    ("carries on", ["{n} carries on with their own business.", "{n} goes on with their own business.",
                    "{n} carries on as before."]),
    ("acts on one of their own wants", ["{n} acts on one of their own wants.", "{n} acts on something they want.",
                                        "{n} turns to their own wants."]),
    ("asks the pc something", ["{n} asks you something.", "{n} asks you something in turn.",
                               "{n} has something to ask you."]),
    ("offers partial help", ["{n} offers partial help.", "{n} offers some help, though not all of it.",
                             "{n} offers to help, partly."]),
    ("helps as asked", ["{n} helps as asked.", "{n} helps, as you asked.", "{n} does as asked, and helps."]),
    ("helps beyond", ["{n} helps beyond what was asked.", "{n} helps, beyond what you asked.",
                      "{n} helps more than was asked."]),
]


def _npc_act(who: str, act: str, recent: str) -> str:
    """One NPC act from the record in words; a table row said the same way in a recent exchange is said
    another way."""
    low = act.lower()
    options = next((ws for key, ws in _NPC_ROW_WORDS if low.startswith(key)), None)
    if options is None:
        head, _, tail = re.sub(r"\bthe PC\b", "you", act).partition(": ")
        first = tail.split(", ")[0].strip() if tail else ""
        return _sentence(f"{who} {head}" + (f", and {first}" if first else ""))
    said = [o.format(n=who) for o in options]
    return next((s for s in said if s not in recent), said[0])


def _npcs(view: str) -> dict[str, str]:
    """{npc id: name} for the people in the narrator view (its top-level `npc.x: Name` lines)."""
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"(?m)^(npc\.[\w.]+): (.+)$", view)}


def _place(view: str) -> tuple[str, str]:
    """(name, description) of the scene's place in the narrator view, else ("", "")."""
    m = re.search(r"(?m)^scene: \S+ at (\S+?);", view)
    if not m:
        return "", ""
    name = re.search(rf"(?m)^{re.escape(m.group(1))}: (.+)$", view)
    block = view.split(f"\n{m.group(1)}: ", 1)[-1] if name else ""
    desc = re.search(r"(?m)^  desc: (.+)$", block)
    return (name.group(1).strip() if name else ""), (desc.group(1).strip() if desc else "")


def _look(view: str, npcs: dict[str, str]) -> list[str]:
    """What a look around shows: the place and who is in it, from the view only."""
    place, desc = _place(view)
    out = []
    if place:
        out.append(_sentence(f"You take in {place}" + (f": {desc}" if desc and desc.lower() != place.lower() else "")))
    names = list(npcs.values())
    if names:
        out.append(f"{' and '.join(names[:3])} {'is' if len(names[:3]) == 1 else 'are'} here.")
    else:
        out.append("No one else is in sight.")
    return out


def _wh_answer(question: str, view: str, npcs: dict[str, str]) -> list[str]:
    """An answer-shaped line for a who / where / what question, from the view only."""
    q = question.lower()
    if re.search(r"\bwho\b", q):
        names = list(npcs.values())
        return [f"{' and '.join(names[:3])} {'is' if len(names[:3]) == 1 else 'are'} here." if names
                else "No one else is in sight."]
    if re.search(r"\bwhere\b", q):
        place, _ = _place(view)
        return [f"You are at {place}."] if place else []
    return _look(view, npcs) if re.search(r"\b(see|here|around)\b", q) else ["Nothing here answers that yet."]


def _narrator(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:
    # The record in THIS MESSAGE, line by line, in words (never the rules text elsewhere in the packet).
    msg = packet.message
    npcs = _npcs(packet.view)
    asked = {m.group(1).rstrip("?") for m in re.finditer(r'(?m)^- question "(.*)": the answer is', msg)}
    lines: list[str] = []
    replies: list[str] = []  # speech is answered after what happened
    handle_of: dict[int, str] = {}  # line index -> the record handle it narrates (spec 006: refs)
    reply_handle: dict[str, str] = {}
    paused = False
    record = msg.split("A REPAIR.", 1)[0]
    for raw in record.splitlines():
        line = raw.strip()
        hm = re.match(r"^- (R\d+)(?: MUST)?: (.*)$", line)
        handle = hm.group(1) if hm else None
        if hm:
            line = "- " + hm.group(2)
        start, n_replies = len(lines), len(replies)
        _narrate_line(line, lines, replies, msg, packet, npcs, asked)
        if line.startswith(("- the turn stops at a pause", "- beat:")) and (
                line.startswith("- the turn stops") or "not resolved yet" in line):
            paused = True
        for k in range(start, len(lines)):
            if handle:
                handle_of[k] = handle
        for r in replies[n_replies:]:
            if handle:
                reply_handle[r] = handle
    if any(not r.endswith("~") for r in replies):  # the speech's listener is the Talk's, never the first in view
        replies = [r for r in replies if not r.endswith("~")]
    replies = [r.rstrip("~") for r in replies]
    reply_handle = {k.rstrip("~"): v for k, v in reply_handle.items()}
    said = list(dict.fromkeys(r for r in replies if not any(ln.startswith(r.split(" hears")[0]) for ln in lines)))
    pairs = [(t, handle_of.get(k)) for k, t in enumerate(lines)] + [(r, reply_handle.get(r)) for r in said]
    pairs = [(t, h) for t, h in pairs if t]
    if "A REPAIR." in msg:  # drop the failing sentences; add one for each missing must-name line (12.3.3)
        rep = msg.split("A REPAIR.", 1)[1]
        bad = re.findall(r"(?m)^\[(\d+)\] ", rep)
        missing = set(re.findall(r"\b(R\d+)\b", rep.split("MISSING", 1)[1])) if "MISSING" in rep else set()
        repairs = [{"replaces": n, "text": "", "refs": [], "about": [], "new": [], "atmosphere": False} for n in bad]
        repairs += [{"replaces": "add", "text": t, "refs": [h], "about": [], "new": [], "atmosphere": False}
                    for t, h in pairs if h in missing]
        return {"repairs": repairs}
    if not pairs:
        pairs.append(("The moment holds.", None))
    if not paused:
        pairs.append(("What do you do?", None))
    sents = [{"text": t, "refs": [h] if h else [], "about": [], "new": [], "atmosphere": False} for t, h in pairs]
    if "fiction" in (schema.get("properties") or {}):  # the fallback shape (B risk 2)
        return {"fiction": " ".join(s["text"] for s in sents),
                "declarations": [{"sentence": str(i), **{k: v for k, v in s.items() if k != "text"}}
                                 for i, s in enumerate(sents)]}
    return {"sentences": sents}


def _narrate_line(line: str, lines: list[str], replies: list[str], msg: str, packet: Packet,
                  npcs: dict[str, str], asked: set[str]) -> None:
    """One record line of THIS MESSAGE in plain words (appended to `lines`, or a reply to `replies`)."""
    if line.startswith("- a new scene opens:"):
        head = line.split(":", 1)[1].split("; frame it")[0].strip()
        where, _, when = head.partition(", ")
        lines.append(f"It is {when} at {where}." if when else _sentence(head))
    elif line.startswith("- note: the inciting incident:"):
        lines.append(_sentence(line.split("incident:", 1)[1]))
    elif line.startswith("- beat:"):
        bits = dict(b.split(": ", 1) for b in line[2:].split("; ") if ": " in b)
        res = bits.get("result")
        undone = bits.get("not done") is not None
        if undone:  # refused, redirected, withdrawn: the act did not happen (the block says why)
            lines.append(_sentence("You size up how to " + re.sub(r"^you\s+", "", bits.get("beat", ""), flags=re.I)))
            return
        lines.append(_sentence(bits.get("beat", "")))
        learned = re.search(r"the PC learns \([^)]*\): (.*)$", line)
        if learned:
            lines += [_sentence(x.replace(" — ", " ", 1)) for x in learned.group(1).split("; ")]
        verb = (primary_verb(bits.get("beat", "")) or ("", []))[0]
        looks = verb == "verb.observe"
        if verb == "verb.talk" and not res:  # words to someone: they answer, or no one is there to
            who = named_entity(bits.get("beat", ""), {k: [v.lower()] for k, v in npcs.items()})
            name = npcs[who[0]] if who else (bits.get("acting on") or next(iter(npcs.values()), None))
            replies.append(f"{name} hears you out, and answers in kind." if name else "No one here answers.")
            return
        if looks and (not res or "success" in res):
            lines += _look(packet.view, npcs)
            if not res:
                return
        if res:
            if "a near miss" in res and "- the turn stops at a pause" not in msg:
                res = res.replace("a near miss", "")  # the near miss was settled: the failure stands
            lines.append(next((t for k, t in _RESULTS if k in res), "It is done."))
        if bits.get("cost paid"):
            lines.append(_sentence(bits["cost paid"]))
        if bits.get("delivered") and res and "success" in res:
            lines.append(_reach_sentence(bits["delivered"]))
    elif line.startswith("- cost paid: "):
        lines.append(_sentence(line.removeprefix("- cost paid: ")))
    elif line.startswith("- the PC learns"):
        lines += [_sentence(x.replace(" — ", " ", 1)) for x in line.split("): ", 1)[-1].split("; ")]
    elif line.startswith(("- visible condition: ", "- harm to ")):
        lines.append(_sentence(line.split(": ", 1)[1]))
    elif line.startswith("- question "):
        m = re.match(r'- question "(.*)": the answer is (.*)$', line)
        if m:
            ans = m.group(2).strip().rstrip(".")
            lines.append(_ANSWERS.get(ans.lower(), _sentence(f"The answer: {ans}")))
    elif re.match(r"- .+ acts: ", line):
        who, act = line[2:].split(" acts: ", 1)
        lines.append(_npc_act(who, act, "\n".join(packet.exchanges)))
    elif re.match(r"- note: an? [\w ]*rest is not possible now", line):
        lines.append("There is no rest to be had yet.")
    elif line.startswith("- note: the character "):
        note = line.removeprefix("- note: the character ")
        lines.append(_sentence("you " + re.sub(r"\b(\w+?)s\b(?= and | rested|$| [a-z])", r"\1", note, count=2)))
    elif line.startswith("- an omen"):
        lines.append(_sentence(line.split(":", 1)[1]))
    elif line.startswith("- part [FICTION_QUESTION]"):
        q = line.split("]", 1)[1].split('"')[1] if '"' in line else ""
        if q and q.rstrip("?") not in asked:
            lines += _wh_answer(q, packet.view, npcs)
    elif line.startswith("- part [SPEECH]"):
        said = line.split("]", 1)[1]
        who = named_entity(said, {k: [v.lower(), *[w for w in v.lower().split()[:1] if w not in ("the", "a", "an")]] for k, v in npcs.items()})
        name = npcs[who[0]] if who else next(iter(npcs.values()), None)
        if name and not any(ln.startswith(name) for ln in replies):  # "~": a guess, dropped if a Talk answers
            replies.append(f"{name} hears you out, and answers in kind." + ("" if who else "~"))
    elif "STATE SUMMARY" in msg and re.match(r"- .+ is (?:at .+, )?in the \w+$", line):  # a recap (12.5.3)
        lines.append(_sentence("You are " + line.split(" is ", 1)[1]))
    elif "STATE SUMMARY" in msg and line.startswith("- earlier: "):
        lines.append(_sentence(line.removeprefix("- earlier: ")))
    elif "STATE SUMMARY" in msg and line.startswith("- an open thread: ") and not any(
            ln.startswith("Still open") for ln in lines):
        lines.append(_sentence("Still open: " + re.split(r"(?<=[.!?])\s", line.split(": ", 1)[1])[0]))


_CLASS_WORDS = [
    ("harm_condition", ["wound", "bleed", "hurt", "dead", "dies", "died", "injur", "poison", "unconscious"]),
    ("possession", ["has", "holds", "carries", "owns", "wields", "draws", "drew", "pocket"]),
    ("knowledge", ["knows", "knew", "remembers", "recognizes", "learns"]),
    ("attitude", ["angry", "friendly", "hostile", "trusts", "fears", "hates", "smiles", "scowls", "glares"]),
    ("position", ["stands", "sits", "near", "beside", "behind", "enters", "leaves", "at the", "in the"]),
]
_CHANGE_WORDS = ["becomes", "became", "now", "breaks", "broke", "falls", "fell", "dies", "died", "opens",
                 "opened", "leaves", "left", "enters", "entered", "draws", "drew", "turns", "turned"]
_PC_INNER = re.compile(r"\byou (feel|felt|think|thought|decide|decided|say|said|want|wanted|realize|realise|"
                       r"fear|hope|wonder|choose|chose)\b", re.IGNORECASE)
_MECHANICS = re.compile(r"\d+|\bd\d+\b|\bDC\b|\broll(?:s|ed)?\b|\bmodifier\b|\bhit points?\b|\bHP\b|\bbonus\b|"
                        r"\bpenalty\b|\bcritical\b|\bnear miss\b|\btier\b", re.IGNORECASE)


def _checker(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:
    # rule: 12.3.1 (one claim per asserting sentence; extract when unsure)
    draft = packet.message
    numbered = re.findall(r"(?m)^\[(\d+)\] (.*)$", draft)  # the turn loop's `[n] sentence` lines (then the player's words)
    if numbered:
        draft = "\n".join(text for _, text in numbered)
    subjects = entity_aliases(enum_at(schema, "claims", "[]", "subject"), packet.render())
    said = packet.message.split("THE PLAYER'S MESSAGE", 1)[1] if "THE PLAYER'S MESSAGE" in packet.message else ""
    claims = []
    for i, sent in enumerate(sentences(draft)):
        hit = named_entity(sent, subjects)
        if not hit:
            continue
        low = sent.lower()
        after = sent[low.find(hit[1].lower()) + len(hit[1]):].strip(" ,.;!?")
        words = after.split()
        cls = next((c for c, ws in _CLASS_WORDS if any(re.search(rf"\b{re.escape(w)}", low) for w in ws)), "action")
        if str(hit[0]).startswith("pc.") and low.startswith("you ") and _overlap(sent, said) >= 0.6:
            cls = "action"  # the player's own declaration, restated (12.14.3): judged as the PC's act
        claims.append({
            "sentence": i, "subject": hit[0], "class": cls,
            "predicate": words[0] if words else "is present",
            "value": " ".join(words[1:]) if len(words) > 1 else sent.strip(),
            "asserts_change": any(_has_word(low, w) for w in _CHANGE_WORDS),
            "pc_words_or_feelings": bool(_PC_INNER.search(sent)),
        })
    sents = sentences(draft)
    last = sents[-1].strip() if sents else ""
    ends_on_prompt = last.endswith("?")
    diff = {k: [] for k in ("undeclared", "unexpressed") if k in schema.get("properties", {})}  # 12.3.1 diff audit
    return {
        **diff,
        "claims": claims,
        "screen": {
            "intent_acknowledged": bool(draft.strip()),
            "intent_substituted": False,
            "next_step_exists": ends_on_prompt or bool(re.search(r"\byou (could|can)\b", draft, re.IGNORECASE)),
            "mechanics_in_fiction": [m.group(0) for m in _MECHANICS.finditer(draft)],
            "ends_on_prompt_or_one_pause": ends_on_prompt,
        },
    }


ROLE_HEURISTICS: dict[Role, Callable[[dict[str, Any], Packet], dict[str, Any]]] = {
    Role.INTERPRET: _interpret,
    Role.READER: _reader,
    Role.FRAMER: _framer,
    Role.WORLD: _world,
    Role.DIRECTOR: _director,
    Role.NARRATOR: _narrator,
    Role.CHECKER: _checker,
    Role.PROPOSER: _proposer,
    Role.LOCATOR: _locator,
}


# ---------------------------------------------------------------- models


def _result(provider: str, role: Role, schema: dict[str, Any], packet: Packet, data: Any,
            turn_id: str | None, attempt: int, watch: Stopwatch, seq: int = 0) -> CallResult:
    rec = new_record(role, schema, provider=provider, model_id=provider, turn_id=turn_id, attempt=attempt, seq=seq,
                     request={"attempt": attempt, "packet": packet.render()})
    rec = rec.model_copy(update={"response": {"data": data, "text": None, "error": None}, "latency_ms": watch.ms()})
    return CallResult(data=data, record=rec)


class OfflineModel:
    """Deterministic, free `StructuredModel`; output always validates against the schema it is given."""

    provider = "offline"

    def propose(self, role: Role, schema: dict[str, Any], packet: Packet) -> dict[str, Any]:
        return ROLE_HEURISTICS[role](schema, packet)

    def fill(
        self, role: Role, schema: dict[str, Any], packet: Packet, *, turn_id: str | None, attempt: int,
        seq: int = 0,
    ) -> CallResult:
        watch = Stopwatch()
        data = conform(self.propose(role, schema, packet), schema, schema)
        return _result(self.provider, role, schema, packet, data, turn_id, attempt, watch, seq)


class ScriptExhausted(ModelError):
    """A ScriptedModel queue ran out and fallback is off."""


class ScriptedModel:
    """Per-role response queues for tests. A queued item is the response data (served as is, unvalidated),
    an exception instance (raised), or a callable `(schema, packet) -> data`. Empty queue → OfflineModel
    when `fallback` is true, else ScriptExhausted. `calls` logs (role, packet) for assertions."""

    provider = "scripted"

    def __init__(self, script: Mapping[Role, Iterable[Any]] | None = None, *, fallback: bool = True):
        self.queues: dict[Role, deque[Any]] = {r: deque(v) for r, v in (script or {}).items()}
        self.fallback = fallback
        self.offline = OfflineModel()
        self.calls: list[tuple[Role, Packet]] = []

    def push(self, role: Role, *responses: Any) -> None:
        self.queues.setdefault(role, deque()).extend(responses)

    def fill(
        self, role: Role, schema: dict[str, Any], packet: Packet, *, turn_id: str | None, attempt: int,
        seq: int = 0,
    ) -> CallResult:
        self.calls.append((role, packet))
        watch = Stopwatch()
        queue = self.queues.get(role)
        if not queue:
            if not self.fallback:
                raise ScriptExhausted(f"no scripted response left for {role.value}")
            data = conform(self.offline.propose(role, schema, packet), schema, schema)
        else:
            item = queue.popleft()
            if isinstance(item, BaseException):
                raise item
            data = item(schema, packet) if callable(item) else item
        return _result(self.provider, role, schema, packet, data, turn_id, attempt, watch, seq)
