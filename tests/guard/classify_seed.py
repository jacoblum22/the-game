"""One-off seed for `viii9_allow.py` (spec 033 P0): classify today's static hits by rule, print the file body.

    PYTHONUTF8=1 py -3.12 -m tests.guard.classify_seed > tests/guard/viii9_allow_body.txt

Kept only so the seed can be reproduced and reviewed; the reviewed result is `viii9_allow.py`. Delete after P6.
"""

from __future__ import annotations

import re
from collections import defaultdict

from tests.guard.scan import scan

# (regex on "module:function:rule:name" without the "engine." prefix, class, reason); first match wins
RULES: list[tuple[str, str, str]] = [
    # ---- P4: identity, walk-ons, testimony, the word-matching measures (R6 R8 R11)
    (r"^dm\.dm_tools:(_content|_name_tokens|_log_only|_squash|_told|_walk_on|target_kinds):", "pending:P4",
     "R11 measure, R6 identity or R8 testimony word matching"),
    (r"^dm\.dm_tools:_party:pattern:(_PC_WORDS|dm\.npc_layer\.ANIMAL|_NAME)$", "pending:P4", "R6: `pc` literal, `as`"),
    (r"^dm\.dm_tools:_along:pattern:_PC_WORDS$", "pending:P4", "R6: `pc` literal"),
    (r"^audit\.claims:_pronoun_hit:", "pending:P4", "reached only from _log_only (R11)"),
    (r"^audit\.declare:", "pending:P4", "reached only from _log_only (R11)"),
    (r"^audit\.text:", "pending:P4", "D40 primitives; their dm-tools callers are P4's (_told, overlap, _log_only)"),
    (r"^dm\.mentions:", "pending:P4", "R6: write_mentions / find_existing leave dm-tools"),
    (r"^gen\.npc:role_implies:", "pending:P4", "census find: role words imply age and pronouns; `as` replaces it"),
    # ---- P2a: positions, contact, hold release, fight start, penalty details (R1 R2 R5)
    (r"^resolve\.pipeline:(_cleanse|_contact|_moved):", "pending:P2a", "R1: positions come from the DM"),
    (r"^resolve\.change:(_person|typed_goal):", "pending:P2a", "R1: no goal from the verb, no name resolution"),
    (r"^resolve\.conflict:(strike_harm:pattern:NONLETHAL|weapon:)", "pending:P2a", "R5: the DM's weapon and lethality"),
    (r"^dm\.dm_tools:_propose_roll:words:resolve\.change\._VERB_GOAL$", "pending:P2a", "R1: no goal defaults"),
    # ---- P3: the foe's choice (R3)
    (r"^resolve\.conflict:foe_beat:", "pending:P3", "R3: the DM picks the foe's act"),
    # ---- P2b: beat-text decisions and search by id (R7 R10)
    (r"^resolve\.gate:(reads_writing|words):", "pending:P2b", "R7: reads / exclusion are DM fields"),
    (r"^resolve\.frame:(lift_attribute|lift_or_carry|reverses):", "pending:P2b", "R7: lift, attribute, reversal"),
    (r"^retrieve\.anchors:(_intent_hits|_norm):", "pending:P2b", "R10: the anchor is the verb's card id"),
    (r"^retrieve\.scene:(focus_ids|resolve_names|_norm):", "pending:P2b", "R10: focus is ids"),
    # ---- S: search that lists candidates for the DM to judge
    (r"^dm\.codex:", "S", "recall: lists what the record holds; the DM judges"),
    (r"^dm\.fixer:_search_tool:", "S", "recall: keyword search over the record; the DM judges"),
    # ---- F: formatting what the player or the DM reads
    (r"^dm\.oof:", "F", "out-of-fiction text for the player's menus and lines"),
    (r"^dm\.narration:", "F", "block layout for the player"),
    (r"^dm\.packet:", "F", "packet card text"),
    (r"^dm\.player_text:", "F", "second-person rewrite of shown text"),
    (r"^text\.render:", "F", "grammar for rendered lines"),
    (r"^gen\.hooks:", "F", "template fill of generated lead text"),
    (r"^audit\.fallback:", "F", "sentence for a fact line"),
    (r"^resolve\.oracle:positive:", "F", "reached only by oof.fact_short (a label); the oracle question path is not a turn"),
    (r"^resolve\.change:plain:", "F", "label text"),
    (r"^retrieve\.anchors:natural_key:", "F", "sort key"),
    # ---- P: parsing code-made strings, tables and enums of code ids
    (r":re:", "P", "parses a code-made string (cost DSL, rule atom, table range, id, slug, list of ids)"),
    (r":pattern:", "P", "pattern over code-made ids"),
]


def classify(key: str) -> tuple[str, str]:
    for pat, cls, why in RULES:
        if re.search(pat, key):
            return cls, why
    return "P", "enum or table of code ids"


def main() -> None:
    by_mod: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for h in scan():
        cls, why = classify(h.key.removeprefix("engine."))
        by_mod[h.module].append((f"{h.func}:{h.rule}:{h.name}", cls, why))
    for mod in sorted(by_mod):
        print(f'    "{mod}": {{')
        for k, cls, why in sorted(by_mod[mod]):
            print(f'        "{k}": ("{cls}", "{why}"),')
        print("    },")


if __name__ == "__main__":
    main()
