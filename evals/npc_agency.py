"""NPC agreeableness (spec 032 G13; OEQ-12-28): how often NPCs grant what is asked, by mood and cost, and how often
the engine goes over the T-12-19 ceiling. Haiku engine through the Claude CLI, a Haiku judge checked by hand.

    py -3.12 evals/npc_agency.py ab --arm dm-tools|pipeline --out <dir>   # one arm of the seeded A/B (live, Haiku)
    py -3.12 evals/npc_agency.py report <dir>                             # the arms side by side
    py -3.12 evals/npc_agency.py baseline <save.db> [...]                 # M1 on saves as played (round-8 baseline)
    py -3.12 evals/npc_agency.py ab --arm dm-tools --offline --out <dir>  # stand-ins only, no model (harness check)

The A/B: twelve seeded scenes, one per mood x cost cell of T-12-19, plus four repeat-ask probes (the same ask three
times with flattery and no event), on the dock fixture with one asked person present. The cost of each ask is fixed
by the CELL, never read from the engine (so the DM listing its own `asks` cannot hide a violation). The mood is
pinned for the scene in both arms (the held willingness band: open=willing, guarded, closed=unwilling).
Arms: `dm-tools` (spec 031: one DM role in a tool loop, `engine/dm/dm_tools.py`; Haiku is that role) and `pipeline`
(the Reader -> ... -> Narrator turn at this commit; the Reader is scripted: one SPEECH part, so no frame rolls; Haiku is
the Narrator; every other role is offline). The judge labels each reply: granted, conditional (for a price or on a
condition), partial, refused, deflected or none, and whether a refusal gives the person's own reason. Measures: M1
grant rate by mood and cost, M2 costly asks (real/big) that were granted, listed to be read (observation, no gate), M3 in-character refusals, M4 flips with no
event (repeat probes), M5 repeat-ask caving, M8 voice distinctness (blind attribution of five lines to five cards),
M10 secret leaks (code)."""

from __future__ import annotations

import json
import re
import sqlite3
import sys
import tempfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# imported once here, before the worker threads (a first import from two threads at once fails half-initialised)
import engine.dm.turn  # noqa: E402, F401
from engine.llm.offline import conform  # noqa: E402, F401
from evals.playtest import ask_claude  # noqa: E402, F401
from tests.fixtures.scene_dock import build_dock  # noqa: E402, F401

GRID = {"open": {"none": "help", "small": "help", "real": "price", "big": "partial_or_refuse"},
        "guarded": {"none": "help", "small": "price", "real": "partial_or_refuse", "big": "refuse"},
        "closed": {"none": "partial", "small": "refuse", "real": "refuse", "big": "refuse_may_escalate"}}
STANDING = {"open": 1, "guarded": -1, "closed": -3}  # the pin's standing, so the relationship agrees with the band
BAND = {"open": "willing", "guarded": "guarded", "closed": "unwilling"}  # the held willingness (answer.HELD)
ARMS = ("pipeline", "dm-tools")
LABELS = ("granted", "conditional", "partial", "refused", "deflected", "none")
HAIKU = "haiku"

# one asked person per cell: name, role, pronouns, demeanor, want, refusal, secret (sealed: never in a reply)
CELLS: list[dict[str, Any]] = [
    {"id": "A1", "mood": "open", "cost": "none", "name": "Bram Weller", "role": "fisherman", "pr": "he/him",
     "dem": "easygoing", "want": "a good catch before the frost", "refusal": "will not go out on the water at night",
     "secret": "Bram owes the reeve eleven crowns", "ask": "Which way to the ferry?", "qk": "where_is"},
    {"id": "A2", "mood": "open", "cost": "small", "name": "Mira Lantry", "role": "lamplighter", "pr": "she/her",
     "dem": "cheerful", "want": "to finish her round before the bells", "refusal": "will not leave a street dark",
     "secret": "Mira sells lamp oil out of the guild's stores", "ask": "Could you lend me your spare lantern for the night?",
     "qk": "none"},
    {"id": "A3", "mood": "open", "cost": "real", "name": "Hesta Coombe", "role": "laundress", "pr": "she/her",
     "dem": "warm", "want": "to move her mother out of the river ward", "refusal": "will not lie under oath",
     "secret": "Hesta hid a deserter in her loft last winter",
     "ask": "If the watch asks, will you tell them I was with you all evening? I wasn't.", "qk": "none"},
    {"id": "A4", "mood": "open", "cost": "big", "name": "Doran Pike", "role": "boatwright", "pr": "he/him",
     "dem": "steady", "want": "to keep his yard licence", "refusal": "will not cross the harbour master",
     "secret": "Doran's yard builds hulls for smugglers", "ask": "Will you hide me in your boat shed from the watch tonight?",
     "qk": "none"},
    {"id": "A5", "mood": "guarded", "cost": "none", "name": "Pell Garron", "role": "dock porter", "pr": "he/him",
     "dem": "wary", "want": "steady work through the winter", "refusal": "will not carry for strangers after dark",
     "secret": "Pell skims a crate from every third barge", "ask": "Is this the ferry landing?", "qk": "what_like"},
    {"id": "A6", "mood": "guarded", "cost": "small", "name": "Ysolde Marr", "role": "tavern keeper", "pr": "she/her",
     "dem": "shrewd", "want": "to keep trouble out of her house", "refusal": "will not talk about her regulars to the watch",
     "secret": "Ysolde waters the ale on fair days", "ask": "Does Hob the tinker drink here?", "qk": "who_is"},
    {"id": "A7", "mood": "guarded", "cost": "real", "name": "Garrick Fenn", "role": "dockhand", "pr": "he/him",
     "dem": "tired", "want": "to get home to his children", "refusal": "will not stay on the dock past the bell",
     "secret": "Garrick lost his last wages at dice", "ask": "Will you watch my cart overnight?", "qk": "none"},
    {"id": "A8", "mood": "guarded", "cost": "big", "name": "Anselm Quill", "role": "clerk", "pr": "he/him",
     "dem": "careful", "want": "a seat on the town council", "refusal": "will not put his name to a charge",
     "secret": "Anselm forged the reeve's seal once", "ask": "Will you testify against the reeve for me?",
     "qk": "none"},
    {"id": "A9", "mood": "closed", "cost": "none", "name": "Kett Barrow", "role": "gate guard", "pr": "he/him",
     "dem": "surly", "want": "to be off duty", "refusal": "will not open the gate after dusk",
     "secret": "Kett sleeps at his post on the night watch", "ask": "What hour is it?", "qk": "what_like"},
    {"id": "A10", "mood": "closed", "cost": "small", "name": "Rook Ashby", "role": "charcoal burner", "pr": "he/him",
     "dem": "sour", "want": "to be left alone", "refusal": "will not share his fire with townsfolk",
     "secret": "Rook poaches deer from the lord's wood", "ask": "May I sit by your fire a while?", "qk": "none"},
    {"id": "A11", "mood": "closed", "cost": "real", "name": "Ilse Varga", "role": "archivist", "pr": "she/her",
     "dem": "cold", "want": "to keep the archive whole", "refusal": "will not open the archive after dark",
     "secret": "Ilse burned the tithe rolls of the flood year", "ask": "Will you let me into the archive after dark?",
     "qk": "none"},
    {"id": "A12", "mood": "closed", "cost": "big", "name": "Varn Holt", "role": "man-at-arms", "pr": "he/him",
     "dem": "hard", "want": "his lord's favour", "refusal": "will not betray his lord",
     "secret": "Varn knows the strongroom key hangs behind the chapel altar",
     "ask": "Betray your lord: give me the key to his strongroom.", "qk": "none"},
]
REPEATS = ("A7", "A8", "A10", "A11")  # guarded and closed asks repeated with flattery, no event (M5)
FLATTERY = ("Come now, you seem a fair sort. Surely you can do this one thing for me?",
            "Please, I'm asking you as a friend. Just this once?")


# ------------------------------------------------------------------------------------------------ scene and turn


def _scene(tmp: Path, cell: dict[str, Any]) -> tuple[Any, str]:
    """The dock fixture with the fixture's two NPCs moved off and this cell's person present, mood held."""
    from engine import ids
    from engine.store.events import EntityRecord, Event

    dock = build_dock(tmp, seed=1000 + CELLS.index(cell))
    with dock.store.transaction("turn.0b") as tx:
        away = ids.entity_id("place", "The Harbour Wall", tx.state.entities)
        tx.add(Event.of("entity_created", source="fixture", rule_id="PR-12-5", entity=EntityRecord(
            id=away, kind="place", name="The Harbour Wall", data={"place_kind": "landmark"})))
        for e in (dock.ferryman, dock.watch):
            tx.add(Event.of("position_set", source="fixture", rule_id="10.1.1", entity=e, location=away))
        npc = ids.entity_id("npc", cell["name"], tx.state.entities)
        tx.add(Event.of("entity_created", source="fixture", rule_id="PR-12-5", entity=EntityRecord(
            id=npc, kind="npc", name=cell["name"], sealed_fields=["refusals", "secrets", "wants"],
            data={"role": cell["role"], "pronouns": cell["pr"], "demeanor": cell["dem"], "name_known": True,
                  "wants": [cell["want"]], "refusals": [cell["refusal"]], "secrets": [cell["secret"]]})))
        tx.add(Event.of("position_set", source="fixture", rule_id="10.1.1", entity=npc, location=dock.place))
        tx.add(Event.of("relationship_set", source="fixture", rule_id="12.11.2", a=npc, b=dock.pc, kind="standing",
                        value=STANDING[cell["mood"]], new_value=STANDING[cell["mood"]], reason="eval pin"))
        from engine.dm.answer import HELD
        from engine.world.common import meta

        tx.add(meta(HELD, {"scene": dock.scene, "npcs": {npc: {"band": BAND[cell["mood"]], "why": "eval pin"}}},
                    "PR-12-10"))
    return dock, npc


def _reader(text: str, cell: dict[str, Any]) -> dict[str, Any]:
    part = {"text": text, "class": "SPEECH", "question_kind": cell["qk"], "topic": None}  # the sole NPC is addressed
    return {"parts": [part],
            "pending_answer": None, "fact_questions": [], "beats": [], "clarifying_question": None,
            "restatement": text, "player_quantity": None}


def _haiku(schema: dict[str, Any], packet: Any) -> dict[str, Any]:
    from evals.playtest import ask_claude

    raw, _ = ask_claude(packet.instructions, packet.render(include_instructions=False), schema, HAIKU)
    return conform(raw, schema, schema)


def run_cell(cell: dict[str, Any], arm: str, turns: int, *, offline: bool = False) -> dict[str, Any]:
    """Play `turns` turns of the cell's ask (then flattery) and return each reply with the engine's own log.
    `offline`: no model call; the offline stand-ins answer (a harness check, never a measurement)."""
    from engine.dm import dm_tools
    from engine.dm.context import TurnContext
    from engine.dm.schemas import prune
    from engine.dm.turn import play_turn
    from engine.llm.base import Role
    from engine.llm.offline import ScriptedModel

    tools = arm == "dm-tools"
    with tempfile.TemporaryDirectory(prefix=f"npcag-{cell['id']}-", ignore_cleanup_errors=True) as t:
        dock, npc = _scene(Path(t), cell)
        model = ScriptedModel({})
        ctx = TurnContext.for_store(dock.store, model=model, rules=dock.rules, rng=dock.rng,
                                    config={"world_judge": False, **({"engine": dm_tools.ENGINE} if tools else {})})
        out = []
        for i in range(turns):
            text = cell["ask"] if i == 0 else FLATTERY[(i - 1) % len(FLATTERY)]
            if not tools:
                data = _reader(text, cell)
                model.push(Role.READER, lambda schema, packet, d=data: prune(d, schema))
            role = dm_tools.DM_ROLE if tools else Role.NARRATOR  # since P2 the DM has its own role [spec 032 P7]
            if not offline:  # dm-tools: the DM role is Haiku; pipeline: the Narrator is
                model.push(role, *([_haiku] * (dm_tools.MAX_TOOLS + 2 if tools else 3)))
            res = dm_tools.play_turn(ctx, text) if tools else play_turn(ctx, text)
            model.queues.get(role, []).clear()
            row: dict[str, Any] = {"ask": text, "reply": res.response.fiction, "paused": res.response.pause is not None}
            if tools:
                log = res.turn_record.screen["dm_tools"]
                row["tools"] = [f"{x['tool']}: {x['out'][:80]}" for x in log["tools"]]
                row["engine_asks"] = log.get("asks", [])
            out.append(row)
        dock.store.close()
    return {"cell": cell["id"], "arm": arm, "turns": out}


# ------------------------------------------------------------------------------------------------ the judge

JUDGE_SYSTEM = (
    "You label how a tabletop RPG character answered a request. Read the character card, the player's ask and the "
    "passage. Label the asked character's response: granted (does or agrees to do all of it, freely), conditional "
    "(agrees for a price or on a condition), partial (gives some of it, or later), refused (says no or will not), "
    "deflected (avoids answering without a clear no), none (does not respond at all). in_character: for refused or "
    "deflected only, true when the refusal gives a reason that is the character's own (a want, a duty, a fear, a "
    "limit, their situation or a person), false for a generic no. Judge only the asked character.")
JUDGE_SCHEMA = {"type": "object", "properties": {
    "label": {"type": "string", "enum": list(LABELS)}, "in_character": {"type": "boolean"},
    "why": {"type": "string"}}, "required": ["label", "in_character", "why"]}


def judge(card: str, ask: str, passage: str) -> dict[str, Any]:

    prompt = f"CHARACTER CARD:\n{card}\n\nTHE PLAYER'S ASK:\n{ask}\n\nTHE PASSAGE:\n{passage}"
    data, _ = ask_claude(JUDGE_SYSTEM, prompt, JUDGE_SCHEMA, HAIKU)
    return dict(data)


def card_of(cell: dict[str, Any]) -> str:
    return (f"{cell['name']} ({cell['pr']}), {cell['role']}, {cell['dem']}; wants {cell['want']}; "
            f"{cell['refusal']}")


def violates(label: str, ceiling: str) -> bool:  # T-12-19's order: help > price > partial > refuse
    if ceiling in ("price", "partial", "partial_or_refuse"):
        return label == "granted"
    if ceiling in ("refuse", "refuse_may_escalate"):
        return label in ("granted", "conditional", "partial")
    return False


def leaked(cell: dict[str, Any], text: str) -> bool:  # M10: the sealed secret's distinctive words in the reply
    words = [w for w in re.findall(r"[a-z]{5,}", cell["secret"].lower()) if w not in cell["name"].lower()]
    low = text.lower()
    return sum(w in low for w in words) >= max(2, len(words) // 2 + 1)


# ------------------------------------------------------------------------------------------------ commands


def cmd_ab(arm: str, out_dir: Path, *, offline: bool = False) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(c, 3 if c["id"] in REPEATS else 1) for c in CELLS]
    with ThreadPoolExecutor(4) as pool:
        runs = list(pool.map(lambda j: run_cell(j[0], arm, j[1], offline=offline), jobs))
    by_id = {c["id"]: c for c in CELLS}

    def label(r: dict[str, Any]) -> dict[str, Any]:
        c = by_id[r["cell"]]
        for t in r["turns"]:
            t.update(judge(card_of(c), t["ask"], t["reply"]))
            t["ceiling"] = GRID[c["mood"]][c["cost"]]
            t["violation"] = violates(t["label"], t["ceiling"])
            t["leak"] = leaked(c, t["reply"])
        return r

    with ThreadPoolExecutor(4) as pool:
        runs = list(pool.map(_label_offline if offline else label, runs))
    (out_dir / f"{arm}.json").write_text(json.dumps(runs, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{arm}: {sum(len(r['turns']) for r in runs)} replies -> {out_dir / (arm + '.json')}")
    return 0


def _label_offline(r: dict[str, Any]) -> dict[str, Any]:
    """--offline: no judge call either; every reply is labelled `none` so the harness runs end to end."""
    c = next(c for c in CELLS if c["id"] == r["cell"])
    for t in r["turns"]:
        t.update(label="none", in_character=False, why="offline", ceiling=GRID[c["mood"]][c["cost"]])
        t["violation"] = violates(t["label"], t["ceiling"])
        t["leak"] = leaked(c, t["reply"])
    return r


def _rate(xs: list[bool]) -> str:
    return f"{sum(xs)}/{len(xs)}" if xs else "-"


GRANT = ("granted", "conditional", "partial")


def summarize(runs: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {c["id"]: c for c in CELLS}
    first = [(by_id[r["cell"]], r["turns"][0]) for r in runs]
    rows = {m: _rate([t["label"] in GRANT for c, t in first if c["mood"] == m]) for m in GRID}
    cols = {k: _rate([t["label"] in GRANT for c, t in first if c["cost"] == k]) for k in ("none", "small", "real", "big")}
    allt = [(by_id[r["cell"]], t) for r in runs for t in r["turns"]]
    refusals = [t for _, t in allt if t["label"] in ("refused", "deflected")]
    caved, flips = [], []
    for r in runs:
        if len(r["turns"]) > 1:
            labs = [t["label"] for t in r["turns"]]
            caved.append(labs[0] in ("refused", "deflected") and any(x in GRANT for x in labs[1:]))
            flips.append(len({x in GRANT for x in labs}) > 1)
    return {"grant_by_mood": rows, "grant_by_cost": cols,
            "cells": {c["id"]: f"{c['mood']}x{c['cost']}:{t['label']}" for c, t in first},
            # owner ruling 2026-10-10: no ceiling gate; costly asks that were granted are listed to be read
            "costly_grants": [f"{r['cell']} ask {i + 1} ({by_id[r['cell']]['mood']} x {by_id[r['cell']]['cost']}) {t['label']}: "
                              f"\"{t['ask'][:70]}\" -> {t['reply'][:140]!r}"
                              for r in runs for i, t in enumerate(r["turns"])
                              if by_id[r["cell"]]["cost"] in ("real", "big") and t["label"] in GRANT],
            "costly_asks": _rate([t["label"] in GRANT for c, t in allt if c["cost"] in ("real", "big")]),
            "in_character_refusals": _rate([bool(t.get("in_character")) for t in refusals]),
            "repeat_caving": _rate(caved), "flips_no_event": _rate(flips),
            "leaks": _rate([t["leak"] for _, t in allt])}


VOICES = ("A1", "A4", "A6", "A10", "A12")  # five different people, moods and trades (M8)


def voice_distinctness(runs: list[dict[str, Any]]) -> str:
    """M8: one blind attribution per arm: the first quoted line of five people, shuffled against their five cards;
    the judge matches them. Chance is 1 in 5."""

    by_id = {c["id"]: c for c in CELLS}
    lines = []
    for r in runs:
        if r["cell"] in VOICES:
            m = re.search(r"[\"“]([^\"”]{8,})[\"”]", r["turns"][0]["reply"])
            lines.append((r["cell"], m.group(1) if m else ""))
    order = sorted(lines, key=lambda x: x[1][::-1])  # a fixed shuffle: by the line's reversed text
    cards = "\n".join(f"{i}. {by_id[c]['role']}, {by_id[c]['dem']}; wants {by_id[c]['want']}"
                      for i, c in enumerate(VOICES))
    quotes = "\n".join(f"{chr(65 + i)}. \"{q}\"" for i, (_, q) in enumerate(order))
    schema = {"type": "object", "properties": {"matches": {"type": "array", "items": {"type": "object", "properties": {
        "line": {"type": "string"}, "card": {"type": "integer"}}, "required": ["line", "card"]}}},
              "required": ["matches"]}
    data, _ = ask_claude("Match each spoken line to the character card of the one who says it. Each card is used "
                         "once.", f"CARDS:\n{cards}\n\nLINES:\n{quotes}", schema, HAIKU)
    right = 0
    for m in data.get("matches", []):
        i, c = ord((str(m.get("line") or "?")[:1]).upper()) - 65, int(m.get("card", -1))
        if 0 <= i < len(order) and 0 <= c < len(VOICES) and VOICES[c] == order[i][0]:
            right += 1
    return f"{right}/{len(order)}"


def cmd_report(out_dir: Path, *, voice: bool = True) -> int:
    arms = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(out_dir.glob("*.json"))
            if p.stem in ARMS}
    sums = {a: summarize(r) for a, r in arms.items()}
    keys = ["costly_asks", "in_character_refusals", "repeat_caving", "flips_no_event", "leaks"]
    print("| measure | " + " | ".join(sums) + " |\n|---|" + "---|" * len(sums))
    for m in GRID:
        print(f"| M1 grant, {m} | " + " | ".join(s["grant_by_mood"][m] for s in sums.values()) + " |")
    for k in ("none", "small", "real", "big"):
        print(f"| M1 grant, cost {k} | " + " | ".join(s["grant_by_cost"][k] for s in sums.values()) + " |")
    for k in keys:
        print(f"| {k} | " + " | ".join(str(s[k]) for s in sums.values()) + " |")
    print("| M8 voice distinctness (blind, chance 1/5) | " + " | ".join(voice_distinctness(r) if voice else "-" for r in arms.values())
          + " |")
    print()
    for a, s in sums.items():
        print(f"- {a}: " + ", ".join(s["cells"].values()))
        print(f"  costly asks (real/big) granted, to read ({a}, no gate): {s['costly_asks']}")
        print("".join(f"    - {x}\n" for x in s["costly_grants"]), end="")
    return 0


# ------------------------------------------------------------------------------------------------ baseline


_BAND = re.compile(r"^- R\d+ MUST: (.+?) acts: .*?\b(willingly|guardedly|refuses to answer|replies|turns you away)",
                   re.M)


def baseline(saves: list[Path]) -> int:
    """M1/M3/M4/M10 on saves as played: each narrator call whose record gave an NPC a willingness band; the judge
    labels the reply; the cost is the judge's estimate (no Reader cost field then)."""
    rows: list[dict[str, Any]] = []
    for save in saves:
        con = sqlite3.connect(f"file:{save.as_posix()}?mode=ro", uri=True)
        secrets = [str(v) for (v,) in con.execute(
            "select json_extract(payload, '$.value') from events where type='fact_set' "
            "and json_extract(payload, '$.visibility')='sealed'") if isinstance(v, str) and len(v) > 20]
        calls = con.execute("select turn_id, request, response from model_calls where role='narrator' "
                            "order by row_id").fetchall()
        seen: set[str] = set()
        for turn, req, resp in calls:
            if turn in seen:
                continue
            seen.add(turn)
            packet = str(json.loads(req)["packet"])
            m = _BAND.search(packet)
            if not m:
                continue
            band = {"willingly": "willing", "replies": "willing", "guardedly": "guarded"}.get(m.group(2), "unwilling")
            passage = str((json.loads(resp).get("data") or {}).get("passage") or "")
            said = re.search(r'THE PLAYER\'S MESSAGE: "(.*)"', packet)
            rows.append({"save": save.stem, "turn": turn, "npc": m.group(1), "band": band,
                         "ask": said.group(1) if said else "", "passage": passage,
                         "leak": any(s.lower()[:40] in passage.lower() for s in secrets)})
        con.close()

    def lab(r: dict[str, Any]) -> dict[str, Any]:
        r.update(judge(f"{r['npc']} (from the save)", r["ask"], r["passage"]))
        return r

    with ThreadPoolExecutor(4) as pool:
        rows = list(pool.map(lab, rows))
    out = ROOT / "evals" / "baselines" / "npc_agency_round8.json"
    out.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    print("| band | asks | granted/conditional/partial | refused/deflected | in-character refusals |\n|---|---|---|---|---|")
    for band in ("willing", "guarded", "unwilling"):
        b = [r for r in rows if r["band"] == band]
        ref = [r for r in b if r["label"] in ("refused", "deflected")]
        print(f"| {band} | {len(b)} | {_rate([r['label'] in GRANT for r in b])} | {len(ref)} | "
              f"{_rate([bool(r.get('in_character')) for r in ref])} |")
    flips = 0
    for grp in _groups(rows).values():
        labs = [r["label"] in GRANT for r in grp]
        flips += sum(1 for a, b in zip(labs, labs[1:], strict=False) if a != b)
    print(f"\nM4 grant-side flips within a save for the same NPC (no event check; bands as played): {flips}")
    print(f"M10 leaks (a sealed fact's first 40 characters in a reply): {_rate([r['leak'] for r in rows])}")
    print(f"rows: {len(rows)} -> {out}")
    return 0


def _groups(rows: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    out: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in rows:
        out.setdefault((r["save"], r["npc"]), []).append(r)
    return out


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else ""
    if cmd == "baseline":
        return baseline([Path(a) for a in argv[1:]])
    if cmd == "ab":
        return cmd_ab(argv[argv.index("--arm") + 1], Path(argv[argv.index("--out") + 1]), offline="--offline" in argv)
    if cmd == "report":
        return cmd_report(Path(argv[1]), voice="--no-voice" not in argv)
    print(__doc__)
    return 2


Run = Callable[[], int]

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
