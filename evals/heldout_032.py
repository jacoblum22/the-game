"""Spec 032 P7.4 (gate C11): run the 24 labelled held-out items (`specs/032-dm-tools-mvp/heldout.yaml`) ONCE.

    py -3.12 evals/heldout_032.py --out <dir>            # live: Haiku is the DM role, through the Claude CLI
    py -3.12 evals/heldout_032.py --offline --out <dir>  # stand-ins only, no model (a harness check, never a measure)
    py -3.12 evals/heldout_032.py --only H01,H07 ...     # a subset (for debugging the harness; a live run is once)

Each item gets a fresh scene (the dock fixture, its place renamed for the item, the entities the item says exist), one
earlier DM passage in RECENT CONVERSATION, then the item's player line through `dm_tools.play_turn` with the DM role
(`dm_tools.DM_ROLE`). A roll the DM offers is answered by "commit" (the foe turn comes on the answer), so an
exchange is one to four engine turns. Scoring is by code from the turn log: the tool calls, the `said` records, the
foe turns, the state afterwards, and a pronoun/presence scan of the passage. A verdict is `pass`, `fail`, or `judge`
(code cannot decide: the passage and the log are printed for a person). The set is spent if anything is tuned on it.

Limits, stated once: the `said` items (H13-H18) score the speaker and a topic word the DM echoes, not the item's
exact wording (the DM invents what the person says; the item passage is printed beside it for the judge)."""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import engine.dm.turn  # noqa: E402, F401  (first import before any worker: half-initialised otherwise)
from engine.llm.offline import conform  # noqa: E402, F401
from tests.fixtures.scene_dock import build_dock  # noqa: E402, F401

HELDOUT = ROOT / "specs" / "032-dm-tools-mvp" / "heldout.yaml"
HAIKU = "haiku"
FAMILIES = {"prose_target": "R prose-only", "fight_exchange": "F fight", "said": "J said", "said_edge": "J said",
            "presence": "Q presence", "pronoun": "Q pronoun"}

# ------------------------------------------------------------------------------------------------ the scenes
# person: (name, role, pronouns, options). options: vit=(cur, max), band, dead, down, away=<place>, walkon, mind, group.
P = tuple[str, str, str, dict[str, Any]]
SCENES: dict[str, dict[str, Any]] = {
    "H01": {"place": "The Wet Quay", "prior": "Rain beads on the wet quay. A wolfhound the size of a calf breaks from "
            "behind the fish crates, lips back, and lunges straight at you."},
    "H02": {"place": "The Eel Market", "prior": "At the market a woman sells eels from a wooden barrel, her sleeves wet "
            "to the elbow. She eyes your purse and names a price."},
    "H03": {"place": "The Ridge Road", "prior": "On the far ridge a rider sits motionless on a grey horse, watching the "
            "road below."},
    "H04": {"place": "The Postern Wall", "prior": "A sentry paces the wall-walk above the postern gate, lantern "
            "swinging. The postern door lies in deep shadow beyond him."},
    "H05": {"place": "The Tavern Yard", "prior": "A drunk lurches out of the tavern door straight at you, arms wide, "
            "reeking of spirits."},
    "H06": {"place": "The Cellar Stair", "prior": "At the foot of the cellar stair a hatch is stuck fast under a rotten "
            "beam, the damp having swollen the timber."},
    "H07": {"place": "The Alley", "prior": "Marek Voss, a bandit, is engaged with you in the alley, blades out.",
            "people": [("Marek Voss", "bandit", "he/him", {"vit": (8, 8), "band": "engaged"})], "fight": ["Marek Voss"]},
    "H08": {"place": "The Alley", "prior": "You are on the ground, winded. Marek Voss stands over you, blade raised.",
            "people": [("Marek Voss", "bandit", "he/him", {"vit": (8, 8), "band": "engaged"})], "fight": ["Marek Voss"],
            "pc_vit": 5, "pc_prone": True},
    "H09": {"place": "The Alley", "prior": "Marek Voss circles you, blade out, close enough to strike.",
            "people": [("Marek Voss", "bandit", "he/him", {"vit": (8, 8), "band": "engaged"})], "fight": ["Marek Voss"]},
    "H10": {"place": "The Alley", "prior": "Marek Voss presses you against the wall. To your left a side alley opens.",
            "people": [("Marek Voss", "bandit", "he/him", {"vit": (8, 8), "band": "engaged"})], "fight": ["Marek Voss"]},
    "H11": {"place": "The Alley", "prior": "Marek Voss sways, bleeding badly, one hand on a wall, still on his feet.",
            "people": [("Marek Voss", "bandit", "he/him", {"vit": (1, 8), "band": "engaged"})], "fight": ["Marek Voss"]},
    "H12": {"place": "The Alley", "prior": "Marek Voss lies out cold in the dirt. Sill Orren fights on, engaged with you.",
            "people": [("Marek Voss", "bandit", "he/him", {"vit": (8, 8), "band": "engaged", "down": True}),
                       ("Sill Orren", "bandit", "he/him", {"vit": (8, 8), "band": "engaged"})],
            "fight": ["Marek Voss", "Sill Orren"]},
    "H13": {"place": "The Ferry Landing", "prior": "Ola Brandt the ferrywoman leans on her pole at the landing, watching "
            "the water.", "people": [("Ola Brandt", "ferrywoman", "she/her", {})],
            "ask": "I ask Ola Brandt what she knows about a man called Tam Harlan.", "speaker": "Ola Brandt",
            "words": ["harlan", "tam", "landing", "owes", "watch"]},
    "H14": {"place": "The Chandlery", "prior": "The chandler wipes his hands on his apron behind a counter of candles.",
            "people": [("the chandler", "chandler", "he/him", {"walkon": True})],
            "ask": "I ask the chandler where the girl went.", "speaker": "the chandler",
            "words": ["mill", "road", "dusk", "alone", "girl"]},
    "H15": {"place": "The Chapel Yard", "prior": "Mother Aldis stands before the ruin, her hands folded.",
            "people": [("Mother Aldis", "abbess", "she/her", {})],
            "ask": "I ask Mother Aldis what happened to the roof.", "speaker": "Mother Aldis",
            "words": ["roof", "midnight", "beam", "inside", "fell", "came down"]},
    "H16": {"place": "The Inn Common Room", "prior": "Corvin, a lean traveller, nurses a cup by the fire.",
            "people": [("Corvin", "traveller", "he/him", {})],
            "ask": "I ask Corvin what the east gate is like.", "speaker": "Corvin",
            "words": ["gate", "bell", "guard", "six", "seven", "quiet"]},
    "H17": {"place": "The Vault Stair", "prior": "Brother Hale stands before the vault door and will not meet your eyes.",
            "people": [("Brother Hale", "sexton", "he/him", {})],
            "ask": "I ask Brother Hale what he wants.", "speaker": "Brother Hale", "words": ["lamp", "vault"]},
    "H18": {"place": "The Carter's Rest", "prior": "The carter sits on his shaft, chewing a straw.",
            "people": [("the carter", "carter", "he/him", {"walkon": True})],
            "ask": "I ask the carter who might know where the butcher went.", "speaker": "the carter",
            "words": ["pell", "smith"]},
    "H19": {"place": "The Yard", "prior": "Nan the cook wipes her hands, nods to Joss, and goes back across the yard to "
            "the kitchen, the door banging behind her.",
            "people": [("Joss", "stable hand", "he/him", {}), ("Nan", "cook", "she/her", {"away": "The Kitchen"})]},
    "H20": {"place": "The Gatehouse", "prior": "Inside the gatehouse the old guard Dowl lies dead on the floor, a cold "
            "lantern at his side.", "people": [("Dowl", "guard", "he/him", {"dead": True})]},
    "H21": {"place": "The Inn", "prior": "The barmaid polishes a mug behind the counter. You have not met the "
            "innkeeper of this place.", "people": [("Wenna Rask", "barmaid", "she/her", {})]},
    "H22": {"place": "The Courier Post", "prior": "Imre Cass, a courier, waits by the post door, a satchel at the feet.",
            "people": [("Imre Cass", "courier", "she/her", {})]},
    "H23": {"place": "The Overturned Cart", "prior": "The Vane twins stand by the overturned cart on the road.",
            "people": [("The Vane twins", "twins", "they/them", {"group": 2})]},
    "H24": {"place": "The Marsh Shallows", "prior": "A marsh heron stands in the shallows, still as a post.",
            "people": [("The marsh heron", "heron", "it/its", {"mind": "animal"})]},
}
# the walk-on / absent speakers the checks look for, by item
WHO = {"H07": "Marek Voss", "H08": "Marek Voss", "H09": "Marek Voss", "H10": "Marek Voss", "H11": "Marek Voss",
       "H12": "Sill Orren", "H19": "Nan", "H20": "Dowl", "H21": "Wenna Rask", "H22": "Imre Cass",
       "H23": "The Vane twins", "H24": "The marsh heron"}


# ------------------------------------------------------------------------------------------------ build and run


def _build(item_id: str, tmp: Path, *, offline: bool) -> tuple[Any, dict[str, str], Any]:
    from engine import ids
    from engine.dm import dm_tools
    from engine.dm.context import TurnContext
    from engine.llm.offline import ScriptedModel
    from engine.resolve import conflict
    from engine.store.conditions import apply_condition
    from engine.store.events import EntityRecord, Event, Quantity
    from engine.time.scheduler import TimeContext
    from engine.world.scenes import end_scene, start_scene
    from engine.world.social import cast_described

    sc = SCENES[item_id]
    dock = build_dock(tmp, seed=3200 + int(item_id[1:]))
    ents: dict[str, str] = {}
    with dock.store.transaction("turn.0b") as tx:
        tctx = TimeContext(tx, dock.rules, dock.rng)
        place = ids.entity_id("place", sc["place"], tx.state.entities)
        tx.add(Event.of("entity_created", source="heldout", rule_id="PR-12-5", entity=EntityRecord(
            id=place, kind="place", name=sc["place"], data={"place_kind": "landmark"})))
        for e in (dock.ferryman, dock.watch):  # the fixture's two NPCs are not in this scene
            tx.add(Event.of("position_set", source="heldout", rule_id="10.1.1", entity=e, location=dock.place))
        tx.add(Event.of("position_set", source="heldout", rule_id="10.1.1", entity=dock.pc, location=place))
        here: list[str] = []
        for name, role, pr, o in sc.get("people", []):
            if o.get("walkon"):
                eid = cast_described(tctx, name, place)
                assert eid is not None
                ents[name] = eid
                here.append(eid)
                continue
            data: dict[str, Any] = {"role": role, "pronouns": pr, "demeanor": "calm", "name_known": not o.get("walkon")}
            if o.get("group"):
                data["group"] = o["group"]
            if o.get("mind"):
                data["mind"] = o["mind"]
            eid = ids.entity_id("npc", name, tx.state.entities)
            vit = o.get("vit")
            tx.add(Event.of("entity_created", source="heldout", rule_id="PR-12-5", entity=EntityRecord(
                id=eid, kind="npc", name=name, data=data, exists="dead" if o.get("dead") else "exists"),
                quantities={"vitality": Quantity(current=vit[0], min=0, max=vit[1])} if vit else {}))
            at = place
            if o.get("away"):  # met, but in another place
                at = ids.entity_id("place", o["away"], tx.state.entities)
                tx.add(Event.of("entity_created", source="heldout", rule_id="PR-12-5", entity=EntityRecord(
                    id=at, kind="place", name=o["away"], data={"place_kind": "landmark"})))
            tx.add(Event.of("position_set", source="heldout", rule_id="10.1.1", entity=eid, location=at))
            ents[name] = eid
            if at == place:
                here.append(eid)
        end_scene(tctx, "held-out item")  # the fixture's dock scene gives way to this item's
        start_scene(tctx, place=place, mode="site", agenda="", cast=here)
        for name in sc.get("fight", []):
            eid = ents[name]
            if sc["people"][[p[0] for p in sc["people"]].index(name)][3].get("down"):
                tx.add(dm_tools._fact(tx, eid, "defeated", {"manner": "unconscious"}))
        live = [ents[n] for n in sc.get("fight", [])]
        if live:
            conflict.start(tctx, dock.pc, live, "held-out item")
            for n in sc["fight"]:
                if dict((p[0], p[3]) for p in sc["people"])[n].get("band") == "engaged":
                    conflict._set_band(tx, dock.pc, ents[n], "engaged", "06.3.9")
        if sc.get("pc_vit") is not None:
            cur = tx.state.quantities[dock.pc]["vitality"].current
            tx.add(Event.of("quantity_changed", source="heldout", rule_id="12.3.4", entity=dock.pc, quantity="vitality",
                            delta=sc["pc_vit"] - cur, new_value=sc["pc_vit"], reason="held-out setup"))
        if sc.get("pc_prone"):
            tx.add_all(apply_condition(tx.state, tx.mint, dock.rules, dock.pc, "cond.prone",
                                       source={"kind": "heldout"}).events)
    ctx = TurnContext.for_store(dock.store, model=ScriptedModel({}), rules=dock.rules, rng=dock.rng,
                                config={"world_judge": False, "engine": dm_tools.ENGINE})
    from engine.store.records import TurnRecord

    dock.store.save_turn(TurnRecord(turn_id=dock.store.new_turn_id(), input_verbatim="(earlier)",
                                    delivered_verbatim=sc["prior"]))
    return ctx, ents, dock


def _haiku(schema: dict[str, Any], packet: Any) -> dict[str, Any]:
    from evals.playtest import ask_claude

    raw, _ = ask_claude(packet.instructions, packet.render(include_instructions=False), schema, HAIKU)
    return conform(raw, schema, schema)


def run_item(item: dict[str, Any], *, offline: bool = False) -> dict[str, Any]:
    """One item: its scene, its player line, the exchange (offers answered `commit`), the log the scorers read."""
    from engine.dm import dm_tools
    from engine.resolve import conflict

    iid = item["id"]
    text = SCENES[iid].get("ask") or item["player"]
    with tempfile.TemporaryDirectory(prefix=f"held-{iid}-", ignore_cleanup_errors=True) as t:
        ctx, ents, dock = _build(iid, Path(t), offline=offline)
        turns: list[dict[str, Any]] = []
        say = text
        for step in range(4):
            if not offline:
                ctx.model.push(dm_tools.DM_ROLE, *([_haiku] * (dm_tools.MAX_TOOLS + 2)))
            res = dm_tools.play_turn(ctx, say) if step == 0 else dm_tools.play_answer(ctx, say)
            ctx.model.queues.get(dm_tools.DM_ROLE, []).clear()
            s = res.turn_record.screen["dm_tools"]
            turns.append({"input": say, "passage": res.response.fiction, "tools": s["tools"], "refusals": s["refusals"],
                          "said": s["said"], "told_dropped": s["told_dropped"], "log_only": s["log_only"],
                          "foe_turns": s["world"]["foe_turns"], "paused": res.response.pause is not None})
            pause = dock.store.state.open_pause()
            if pause is None:
                break
            ids_ = [c["id"] for c in pause.choices]
            say = "commit" if "commit" in ids_ else ids_[0]
        st = dock.store.state
        pc = dock.pc
        after = {"ents": {e: [x.name, str(x.data.get("role") or ""), x.exists] for e, x in st.entities.items()
                          if x.kind == "npc"},
                 "fight_live": bool(conflict.record(st)), "pc_vit": st.quantities[pc]["vitality"].current,
                 "down": [e for e in ents.values() if st.fact_value(e, "defeated")
                          or (st.quantities.get(e, {}).get("vitality") and st.quantities[e]["vitality"].current <= 0)]}
        dock.store.close()
    return {"id": iid, "kind": item["kind"], "player": text, "ents": ents, "turns": turns, "after": after}


# ------------------------------------------------------------------------------------------------ the scorers
MALE = re.compile(r"\b(he|him|his|himself)\b", re.I)
FEMALE = re.compile(r"\b(she|her|hers|herself)\b", re.I)
SINGULAR = re.compile(r"\b(he|him|his|himself|she|her|hers|herself)\b", re.I)
THEY = re.compile(r"\b(they|them|their|theirs|themselves?)\b", re.I)
IT = re.compile(r"\b(it|its|itself)\b", re.I)


def _unquoted(passage: str) -> str:
    return re.sub(r"[\"“][^\"”]*[\"”]", " ", passage)


def _calls(run: dict[str, Any], tool: str = "propose_roll") -> list[dict[str, Any]]:
    out = []
    for t in run["turns"]:
        for c in t["tools"]:
            if c["tool"] == tool:
                try:
                    args = json.loads(c["args"])
                except ValueError:
                    args = {}
                out.append({**args, "out": c["out"]})
    return out


def _refused(run: dict[str, Any]) -> list[str]:
    return [c["out"][:120] for t in run["turns"] for c in t["tools"] if c["out"].startswith("REFUSED")]


def _passage(run: dict[str, Any]) -> str:
    return " ".join(t["passage"] for t in run["turns"] if t["passage"])


def _foe_turns(run: dict[str, Any]) -> list[dict[str, Any]]:
    return [f for t in run["turns"] for f in t["foe_turns"]]


def _sentences_with(passage: str, word: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", passage) if re.search(rf"\b{re.escape(word)}\b", s, re.I)]


def _created(run: dict[str, Any]) -> list[str]:
    """People/creatures that exist after but were not set up: the walk-ons the engine made."""
    return [n for e, (n, _, _) in run["after"]["ents"].items() if e not in run["ents"].values()
            and not n.startswith(("Tam Harlan", "Sela Vey"))]


def score(item: dict[str, Any], run: dict[str, Any]) -> tuple[str, str]:
    """(verdict, note) for one item by its `check`; verdict is pass / fail / judge."""
    iid, check = item["id"], item["check"]
    rolls, refused, passage = _calls(run), _refused(run), _passage(run)
    ok = [r for r in rolls if not r["out"].startswith("REFUSED")]
    verb = {"H01": "verb.strike", "H02": "verb.talk", "H03": "verb.observe", "H04": "verb.sneak",
            "H05": "verb.grapple", "H06": "verb.force"}.get(iid)
    if iid in ("H01", "H04", "H05", "H06"):
        if refused:
            return "fail", f"REFUSED: {refused[0]}"
        if not any(r.get("verb") == verb for r in ok):
            return "fail", f"no accepted propose_roll with {verb} (rolls: {[r.get('verb') for r in rolls]})"
        if iid == "H01":
            hounds = [n for n in _created(run) if "hound" in n.lower()]
            if len(hounds) != 1:
                return "fail", f"hound entities afterwards: {hounds}"
        return "pass", "accepted"
    if iid in ("H02", "H03"):
        if refused:
            return "fail", f"REFUSED: {refused[0]}"
        if ok and any(r.get("verb") == verb for r in ok):
            return "pass", "accepted"
        if ok:
            return "fail", f"roll with another verb: {[r.get('verb') for r in ok]}"
        return "judge", "no roll: read the passage (H02: about the seller as a person; H03: no invented usable name)"
    foes = _foe_turns(run)
    if iid in ("H07", "H09"):
        return ("pass", "1 foe turn") if len(foes) == 1 else ("fail", f"{len(foes)} foe turns: {foes}")
    if iid == "H08":
        mine = [r for r in rolls if "marek" in str(r.get("target", "")).lower() and not r["out"].startswith("REFUSED")]
        if mine:
            return "pass", f"propose_roll at Marek ({mine[0].get('verb')})"
        return "fail", f"no accepted propose_roll at Marek (tool calls: {sum(len(t['tools']) for t in run['turns'])})"
    if iid == "H10":
        hit = any(re.search(r"strikes|lands", str(f.get("did", ""))) for f in foes)
        if len(foes) == 1 and not hit:
            return "pass", f"1 foe turn: {foes[0].get('did')}"
        return "fail", f"{len(foes)} foe turns: {foes}; a strike landed" if hit else f"{len(foes)} foe turns: {foes}"
    if iid == "H11":
        ended = not run["after"]["fight_live"]
        want = 0 if ended else 1
        return ("pass" if len(foes) == want else "fail",
                f"fight {'ended' if ended else 'went on'}; {len(foes)} foe turns (want {want})")
    if iid == "H12":
        sill = run["ents"]["Sill Orren"]
        who = [f.get("foe") for f in foes]
        return ("pass", "Sill acted once") if who == [sill] else ("fail", f"foe turns by {who}")
    if check == "said":
        who = run["ents"][SCENES[iid]["speaker"]]
        said = [s for t in run["turns"] for s in t["said"]]
        mine = [s for s in said if s["speaker"] == who]
        if iid == "H18" and any(s["speaker"] != who for s in said):
            return "fail", f"a record from someone else: {[s['speaker'] for s in said]}"
        if not mine:
            drop = [d.get("why") for t in run["turns"] for d in t["told_dropped"]]
            return "fail", f"no said record from {who} (dropped: {drop[:2]})"
        topic = [w for w in SCENES[iid]["words"] if any(w in s["words"].lower() for s in mine)]
        if not topic:
            return "judge", f"{len(mine)} record(s) from the right speaker; no topic word of {SCENES[iid]['words']}"
        return "pass", f"{len(mine)} record(s) from the speaker, on topic ({topic})"
    if iid == "H19":
        hits = _sentences_with(passage, "Nan")
        if any(c["out"] and "nan" in json.dumps(c).lower() for c in _calls(run, "reveal_clue")):
            return "fail", "a tool call used Nan"
        return ("pass", "Nan is not mentioned") if not hits else ("judge", f"Nan is mentioned: {hits[:2]}")
    if iid == "H20":
        who = run["ents"]["Dowl"]
        if any(s["speaker"] == who for t in run["turns"] for s in t["said"]):
            return "fail", "a said record from Dowl (dead)"
        used = [c for c in _calls(run, "reveal_clue") + _calls(run, "mood") if "dowl" in json.dumps(c).lower()
                and not c["out"].startswith("REFUSED")]
        if used or [r for r in ok if "dowl" in str(r.get("target", "")).lower()]:
            return "fail", "a tool call treated Dowl as a living actor"
        quoted = re.search(r"Dowl[^.\"“]{0,60}[\"“]|[\"”]\s*,?\s*(says|asks|replies)\s+Dowl", passage)
        return ("judge", f"read the passage for Dowl speaking: {_sentences_with(passage, 'Dowl')[:2]}") if quoted or \
            _sentences_with(passage, "Dowl") else ("pass", "Dowl is silent")
    if iid == "H21":
        bar = run["ents"]["Wenna Rask"]
        said = [s["speaker"] for t in run["turns"] for s in t["said"]]
        odo = [e for e, (n, _, _) in run["after"]["ents"].items() if "odo" in n.lower()]
        if bar not in said:
            return "fail", f"the barmaid has no said record (speakers: {said})"
        odo_spoke = [s for s in said if s in odo]
        if "odo" in passage.lower() and not odo and re.search(r"Odo[^.]{0,40}(says|replies|answers|calls)", passage):
            return "fail", "Odo speaks and was never made"
        prior = re.search(r"\b(again|old friend|last time|remember(s|ed)? you)\b", passage, re.I)
        return ("judge", "barmaid answers; check Odo/no prior meeting") if (odo_spoke or prior) else ("pass", "barmaid answers; Odo absent")
    if iid in ("H22", "H23", "H24"):
        text = _unquoted(passage)
        bad, good = {"H22": (MALE, FEMALE), "H23": (SINGULAR, THEY), "H24": (SINGULAR, IT)}[iid]
        wrong = bad.findall(text)
        if wrong:
            return "fail", f"wrong pronouns {sorted({w.lower() for w in wrong})}"
        return "pass", "no wrong pronoun" + ("" if good.search(text) else " (none used at all)")
    return "judge", "no scorer"


# ------------------------------------------------------------------------------------------------ the run


def load_items() -> list[dict[str, Any]]:
    head, body = HELDOUT.read_text(encoding="utf-8").split("\nitems:\n", 1)
    return list(yaml.safe_load("items:\n" + body)["items"])


def main(argv: list[str]) -> int:
    offline = "--offline" in argv
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    items = [i for i in load_items() if only is None or i["id"] in only]
    runs, rows = [], []
    for item in items:
        try:
            run = run_item(item, offline=offline)
            verdict, note = score(item, run)
        except Exception as exc:  # noqa: BLE001 - an item that cannot run is a fail, shown, never hidden
            run, verdict, note = {"id": item["id"], "error": repr(exc)}, "fail", f"ERROR {exc!r}"
        runs.append({**run, "verdict": verdict, "note": note})
        rows.append((item, verdict, note))
        print(f"{item['id']} {FAMILIES[item['kind']]:<13} {verdict:<5} {note[:150]}", flush=True)
    if out is not None:
        out.mkdir(parents=True, exist_ok=True)
        (out / ("heldout_offline.json" if offline else "heldout.json")).write_text(
            json.dumps(runs, indent=1, ensure_ascii=False), encoding="utf-8")
    print()
    for fam in dict.fromkeys(FAMILIES.values()):
        mine = [v for i, v, _ in rows if FAMILIES[i["kind"]] == fam]
        if mine:
            print(f"{fam:<13} pass {mine.count('pass')}  judge {mine.count('judge')}  fail {mine.count('fail')}  of {len(mine)}")
    k = sum(v == "pass" for _, v, _ in rows)
    j = sum(v == "judge" for _, v, _ in rows)
    print(f"TOTAL pass {k}  judge {j}  fail {len(rows) - k - j}  of {len(rows)}  (C11: at least 80% = {-(-len(rows) * 4 // 5)} "
          f"after the judge items are read)" + ("   [OFFLINE: a harness check, not a measurement]" if offline else ""))
    for item, v, _ in rows:
        if v == "judge":
            r = next(x for x in runs if x["id"] == item["id"])
            print(f"\nJUDGE {item['id']}: pass rule: {item['pass']}\n  player: {r['player']}")
            print("  tools: " + "; ".join(f"{c['tool']}: {c['out'][:70]}" for t in r["turns"] for c in t["tools"]))
            print("  said: " + "; ".join(f"{s['speaker']}: {s['words'][:80]}" for t in r["turns"] for s in t["said"]))
            print("  passage: " + " ".join(t["passage"] for t in r["turns"])[:700])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
