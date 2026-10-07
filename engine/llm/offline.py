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
            if eid in line:
                rest = line.split(eid, 1)[1]
                for chunk in re.split(r"[:,;|()\[\]—–]|\baliases?\b|\baka\b", rest):
                    chunk = chunk.strip(" -\t'\"").lower()
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
OOF_WORDS = ["rule", "rules", "roll", "dice", "dc", "modifier", "stat", "mechanic", "bonus", "hit points"]


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
    out: dict[str, Any] = {"own_words_class": None, "own_words_text": None, "lines_and_veils": []}
    m = re.fullmatch(r"\s*(?:option\s*)?#?(\d+)[.)]?\s*", low)
    if not msg or low in ("skip", "move on", "pass", "next", "default"):
        return {**out, "choice": "move_on"}
    if m and 1 <= int(m.group(1)) <= len(options):
        return {**out, "choice": options[int(m.group(1)) - 1]}
    for opt in options:
        label = _norm(str(opt).rsplit(".", 1)[-1])
        if low == str(opt).lower() or (len(label) >= 3 and _has_word(low, label)):
            return {**out, "choice": opt}
    if any(_has_word(low, w) for w in ("details", "tell me more", "more about", "explain")):
        return {**out, "choice": "details"}
    if any(_has_word(low, w) for w in ("suggest", "you pick", "you choose", "surprise me", "dealer's choice")):
        return {**out, "choice": "suggest"}
    classes = enum_at(schema, "own_words_class")
    return {**out, "choice": "own_words", "own_words_class": classes[0] if classes else None,
            "own_words_text": msg}


def _reader(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:
    # rule: 12.2.2 (message classes), 01.2.3 (≤3 beats), 01.3.1 (gate), 01.4.1 (necessity), 01.2.6
    context = packet.render()
    targets = entity_aliases(enum_at(schema, "beats", "[]", "target"), context)
    subjects = entity_aliases(enum_at(schema, "fact_questions", "[]", "subject"), context)
    pending = enum_at(schema, "pending_answer")
    licences = entity_aliases(enum_at(schema, "beats", "[]", "license"), context)
    rungs = enum_at(schema, "fact_questions", "[]", "odds_rung")
    parts, questions, beats, declared = [], [], [], []
    pending_answer = None
    for sent in sentences(packet.message):
        low = sent.lower().strip(" .!")
        picked = _pending_pick(low, pending) if pending_answer is None else None
        if picked is not None:
            pending_answer = picked
            parts.append({"text": sent, "class": "PENDING_ANSWER"})
        elif _QUOTE.search(sent):
            parts.append({"text": sent, "class": "SPEECH"})
        elif sent.rstrip().endswith("?"):
            oof = "/" in sent or any(_has_word(sent, w) for w in OOF_WORDS)
            parts.append({"text": sent, "class": "OOF_QUESTION" if oof else "FICTION_QUESTION"})
            if not oof:
                hit = named_entity(sent, subjects)
                questions.append({
                    "subject": hit[0] if hit else None, "predicate": sent.rstrip("?").strip(),
                    "odds_rung": rungs[len(rungs) // 2] if rungs else None,
                })
        else:
            parts.append({"text": sent, "class": "DECLARATION"})
            declared.append(sent)
    for sent in declared[:3]:
        verb = match_verb(sent)
        target = named_entity(sent, targets)
        licence = named_entity(sent, licences)
        if licence:
            gate = "G2"
        elif verb:
            gate = "G1"
        else:
            gate = "G3"  # 01.3.1: default when uncertain between G1 and G3
        risky = any(_has_word(sent, w) for w in RISKY_WORDS)
        beats.append({
            "intent": sent, "method": sent, "assertion": None, "shape": None,
            "target": target[0] if target else "none",
            "verb": verb[0] if verb else None,
            "license": licence[0] if licence else "none",
            "gate": gate, "g4_fact": None,
            "necessity": "uncertain_and_costly" if risky else "trivial",
            "intent_verbs": verb[1] if verb else [],
        })
    quantity = re.search(r"\b(\d+)\b", packet.message)
    restated = " ".join(_restate(s) for s in declared) or _restate(packet.message.strip())
    return {
        "parts": parts, "pending_answer": pending_answer, "fact_questions": questions, "beats": beats,
        "clarifying_question": None, "restatement": restated,
        "player_quantity": int(quantity.group(1)) if quantity else None,
    }


def _pending_pick(low: str, pending: list[Any]) -> Any:
    m = re.fullmatch(r"#?(\d+)", low)
    if m and 1 <= int(m.group(1)) <= len(pending):
        return pending[int(m.group(1)) - 1]
    return next((p for p in pending if low in (_norm(p), str(p).lower())), None)


def _framer(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:
    text = packet.render()
    anchors = enum_at(schema, "anchor")
    mentioned = re.findall(r"verb\.(\w+)", text)
    verb_word = mentioned[0] if mentioned else None
    if verb_word is None:
        hit = match_verb(packet.message)
        verb_word = hit[0].split(".", 1)[1] if hit else None
    anchor = next((a for a in anchors if verb_word and verb_word in str(a)), anchors[0] if anchors else None)
    attrs = enum_at(schema, "attribute")
    verb_attr = None
    if verb_word:
        verb_attr = next((v["attribute"] for v in basic_verbs() if v["id"] == f"verb.{verb_word}"), None)
    tiers = enum_at(schema, "obstacle", "tier")
    menus = enum_at(schema, "threatened_cost", "menu_id")
    alt_menus = enum_at(schema, "alternate_cost", "menu_id") or menus
    return {
        "anchor": anchor, "deltas": [],
        "attribute": verb_attr if verb_attr in attrs else (attrs[0] if attrs else None),
        "deed_tag": None, "traits": [],
        "obstacle": {"kind": "tier", "tier": tiers[len(tiers) // 2] if tiers else None, "entity": None},
        "levers": [], "snags": [], "stakes_source": None,
        "stakes_heavy": False, "lethal": False, "reach_whole": False, "reach_one_factor": False,
        "threatened_cost": {"menu_id": menus[0] if menus else None, "form_intent": "a setback that fits the moment"},
        "alternate_cost": {
            "menu_id": alt_menus[1] if len(alt_menus) > 1 else (alt_menus[0] if alt_menus else None),
            "form_intent": "a different price that fits the moment",
        },
        "method_consequences": [], "secret": False,
    }


def _world(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:
    npcs = enum_at(schema, "responses", "[]", "npc")
    tags = enum_at(schema, "responses", "[]", "table_context", "tags", "[]")
    return {"responses": [
        {"npc": n, "want_engaged": None, "refusal_engaged": None, "table_context": {"tags": tags[:1]}}
        for n in npcs
    ]}


def _director(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:
    m = re.search(r"quiet[_ ]turns\s*[:=]\s*(\d+)", packet.render(), re.IGNORECASE)
    return {
        "cut_now": bool(m and int(m.group(1)) >= QUIET_TURNS_TO_CUT),
        "next_scene": {
            "mode": "free", "place": None, "agenda": "follow the most pressing open thread",
            "hoped_answer": "you get what you came for", "pillar": None, "challenge_type": None, "cast": [],
        },
        "push": "none", "lead": None,
    }


_DEGREES = [
    ("critical_success", "It works better than you hoped."),
    ("success_at_cost", "It works, but not cleanly."),
    ("critical_failure", "It goes badly wrong."),
    ("near_miss", "It almost holds, and everything hangs on the next breath."),
    ("failure", "It does not go the way you wanted."),
    ("success", "It works."),
]


def _narrator(schema: dict[str, Any], packet: Packet) -> dict[str, Any]:
    names = view_names(packet.view)
    result = "The world waits on you."
    for haystack in (packet.message, packet.render()):
        low = haystack.lower()
        hit = next((line for key, line in _DEGREES if key in low or key.replace("_", " ") in low), None)
        if hit:
            result = hit
            break
    lines = [f"The moment settles over {names[0]}." if names else "The moment settles.", result,
             "What do you do?"]
    return {"fiction": " ".join(lines), "mentions": []}


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
    subjects = entity_aliases(enum_at(schema, "claims", "[]", "subject"), packet.render())
    claims = []
    for i, sent in enumerate(sentences(draft)):
        hit = named_entity(sent, subjects)
        if not hit:
            continue
        low = sent.lower()
        after = sent[low.find(hit[1].lower()) + len(hit[1]):].strip(" ,.;!?")
        words = after.split()
        cls = next((c for c, ws in _CLASS_WORDS if any(re.search(rf"\b{re.escape(w)}", low) for w in ws)), "action")
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
    return {
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
