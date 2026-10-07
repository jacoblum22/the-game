"""The plain wording table for world setup and character creation (engine/dm/text/setup.yaml): every seed question,
option and creation block has a plain entry, and the player never reads rules jargon on those screens."""

from __future__ import annotations

import re
from pathlib import Path

from engine.data.loader import load_rules
from engine.dm import setup_text as T
from engine.dm.context import TurnContext
from engine.dm.creation import _odoc, _of_kind, _origins
from engine.dm.seed_flow import SeedFlow, question_options
from engine.dm.seed_recap import AUTO
from engine.gen._seed_lib import data as seed_data
from engine.gen.world_seed import LAST_STEP
from engine.llm.offline import OfflineModel
from tests.fixtures.game import new_store

RULES = load_rules()
BLOCKS = ("c0", "c1", "c2.people", "c2.rule", "c3", "c4", "c5", "c6", "c7", "c8.drive", "c8.anchor",
          "c8.aspiration", "c8.true_thing", "c9.name", "c9.pronouns", "rm.pick", "rm.name", "ready", "change")
# words that belong to the rulebook, not to a player's screen (the owner's list)
JARGON = re.compile(r"\boracle\b|the engine|\bthe DM\b|classif|\bveto|method consequence|\bband \d|\barch\.|"
                    r"\(the default\)|five things no magic|hybrid pair|pregen|running clock|encounter table|"
                    r"seed check|\brings?\b|Oracle's odds|\[SEED|\[CREATE|\bws\.q\.|\bkf\.|\borg\.|\borig\.", re.I)


def _missing() -> list[str]:
    out: list[str] = []
    for n in range(1, LAST_STEP + 1):
        if not T.step_title(n):
            out.append(f"seed step {n}: title")
    for qid in seed_data().QS:
        q = T.question(qid)
        for key in ("prompt", "pick", "what"):
            if not q.get(key):
                out.append(f"{qid}: {key}")
        tiers = ("village", "town") if qid == "ws.q.rulers" else (None,)
        for tier in tiers:
            from engine.gen.world_seed import WorldSeed

            ws = WorldSeed.from_seed(1, mode="mixed")
            ws.st["tier"] = tier or "village"
            for c in question_options(qid, ws):
                if T.option_label(qid, c.id, "", tier) == "":
                    out.append(f"{qid}: option {c.id}" + (f" ({tier})" if tier else ""))
    for mode in ("guided", "oracle", "mixed"):
        if not T.seed("mode", "options", mode):
            out.append(f"seed mode: option {mode}")
    for bid in BLOCKS:
        b = T.block(bid)
        if not b.get("title"):
            out.append(f"creation block {bid}: title")
        if bid not in ("c0",) and not b.get("prompt"):
            out.append(f"creation block {bid}: prompt")
    OR = _origins(RULES)
    rule_sets = {"c0": ["fast", "full", "ready_made"], "c2.people": _of_kind(RULES, "people"),
                 "c2.rule": ["typical", "free"], "c3": _of_kind(RULES, "upbringing"),
                 "c4": [k for k in _odoc(RULES)["attribute_shapes"]["free"] if k != "sum"],
                 "c5": [p["id"] for p in _odoc(RULES)["profiles"]], "ready": ["begin", "change"]}
    for bid, ids in rule_sets.items():
        for oid in ids:
            if T.block_option(bid, oid, "") == "":
                out.append(f"creation block {bid}: option {oid}")
    assert OR  # the origins loaded
    return out


def test_every_seed_question_option_and_creation_block_has_plain_wording() -> None:
    missing = _missing()
    assert not missing, "no plain entry in engine/dm/text/setup.yaml for:\n  " + "\n  ".join(missing)


def test_the_plain_wording_has_no_rules_jargon() -> None:
    bad: list[str] = []

    def walk(node: object, path: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")
        elif isinstance(node, str) and JARGON.search(node):
            bad.append(f"{path}: {node}")

    walk(T.table(), "setup")
    assert not bad, "\n".join(bad)


def test_seed_screens_read_plainly_and_one_option_questions_are_not_asked(tmp_path: Path) -> None:
    store = new_store(tmp_path)
    flow = SeedFlow(TurnContext.for_store(store, model=OfflineModel()))
    r = flow.start()
    assert r.oof_blocks[-1].text.splitlines()[0] == "Before your character: the world"
    assert r.pause is not None and r.pause.prompt == "Who decides what the world is like?"
    shown: list[str] = []
    r = flow.answer("guided")
    asked: list[str] = []
    while r.phase == "seed":
        assert r.pause is not None
        shown += [b.text for b in r.oof_blocks] + [r.pause.prompt] + [c.label for c in r.pause.choices]
        rec = store.state.open_pause()
        assert rec is not None
        if rec.detail.get("question"):
            asked.append(str(rec.detail["question"]))
        r = flow.submit("")
    shown += [b.text for b in r.oof_blocks]
    assert not set(AUTO) & set(asked) and "ws.q.wound" in asked
    hits = [t for t in shown if JARGON.search(t)]
    assert not hits, hits[:3]
    # every question block says how to answer in one line, the same way
    assert all("press Enter" in t.splitlines()[-1] for t in shown if t.startswith("World ") and "  1)" not in t
               and "(a)" in t)
