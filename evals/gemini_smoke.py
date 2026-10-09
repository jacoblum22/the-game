"""Gemini smoke test: one tiny request per role, with the engine's real schemas, before the first real game.

OWNER-RUN ONLY. Tests and build workers never run it (it spends money). Run from the repo root:

    python evals/gemini_smoke.py                     # every role
    python evals/gemini_smoke.py --roles reader      # just one (comma-separated list)
    python evals/gemini_smoke.py --dry-run           # build and check the requests, send nothing, no key needed

It reads GEMINI_API_KEY from the environment or `.env` at the repo root, sends each role's captured schema
(`tests/engine/fixtures_gemini_schemas/<role>.json`, from a real offline game) through the same adapter the
game uses (`engine.llm.gemini.GeminiModel`: converted schema, thinking level, max_output_tokens), validates the
answer against the original schema, and prints ok / FAIL per role with the error text, tokens and cost.
Exit status: 0 all ok, 1 a role failed, 2 no key.

Cost: seven small calls at gemini-3.8-flash prices; expect about 1-2 cents in all (mostly thinking and output
tokens). The script prints a worst-case ceiling (every call using its whole max_output_tokens) before sending.
Importing this file sends nothing; only `main()` does, and only without --dry-run.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.llm import budget  # noqa: E402
from engine.llm.base import (  # noqa: E402
    MissingKey,
    ModelError,
    Packet,
    Role,
    RoleModel,
    StructuredModel,
    validate,
)
from engine.llm.gemini import build_config, max_output_tokens  # noqa: E402
from engine.llm.gemini_schema import convert, problems  # noqa: E402

FIXTURES = REPO_ROOT / "tests" / "engine" / "fixtures_gemini_schemas"
ROLE_ORDER = [Role.INTERPRET, Role.READER, Role.FRAMER, Role.WORLD, Role.DIRECTOR, Role.NARRATOR, Role.CHECKER,
              Role.PROPOSER, Role.UNDERSTAND]

SCENE = (
    "Test scene (a connectivity check, not a real game): Wren (pc.wren), a scout, stands in the village shrine "
    "at dusk. Rain on the roof; fresh mud on the floor. Use only ids the response schema offers."
)
MESSAGES = {
    Role.INTERPRET: "Player's answer to 'Which climate?': the misty coast, I think.",
    Role.READER: "I look around the shrine for tracks.",
    Role.FRAMER: "Beat to frame: Wren searches the shrine floor for tracks (verb.observe).",
    Role.WORLD: "What happened: Wren searched the shrine and found muddy tracks.",
    Role.DIRECTOR: "The scene at the shrine has gone quiet. quiet_turns: 1",
    Role.NARRATOR: "Outcome: success. Wren finds fresh boot prints leading to the back door. Narrate it briefly.",
    Role.CHECKER: "Draft to check:\n0: Wren kneels by the altar.\n1: Fresh boot prints lead to the back door.\n"
                  "2: What do you do?",
    Role.PROPOSER: "The innkeeper is asked: what are the roads like? topic: roads (routes, distances, the state of "
                   "the ways)",
    Role.UNDERSTAND: "THE PLAYER'S REPORT: \"Wren's cloak was grey, not blue\"\nNOW: spring, the morning of day 1\n"
                     "PEOPLE:\nnpc.wren: Wren (she/her)\nTRANSCRIPT:\nturn.4 | player: \"I look at Wren.\" | game: "
                     "\"Wren's blue cloak drips.\"",
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="One tiny Gemini request per role with the engine's real schemas.")
    p.add_argument("--roles", default="", help="comma-separated roles (default: every role with a fixture)")
    p.add_argument("--model", default=RoleModel().model, help="model id (default: %(default)s)")
    p.add_argument("--thinking", default=RoleModel().thinking, help="thinking level (default: %(default)s)")
    p.add_argument("--fixtures", type=Path, default=FIXTURES, help="folder of <role>.json schemas")
    p.add_argument("--dry-run", action="store_true", help="build and check the requests; send nothing")
    args = p.parse_args(argv)
    names = [r.strip() for r in args.roles.split(",") if r.strip()]
    try:
        args.role_list = [Role(n) for n in names] or list(ROLE_ORDER)
    except ValueError as exc:
        p.error(f"unknown role ({exc}); choose from {', '.join(r.value for r in ROLE_ORDER)}")
    return args


def load_schema(folder: Path, role: Role) -> dict[str, Any] | None:
    path = folder / f"{role.value}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def build_packet(role: Role) -> Packet:
    return Packet(
        instructions=f"You are the {role.value} step of a text role-playing game engine. Fill every field of the "
                     "response schema with plausible values for the tiny test scene. Keep strings short.",
        core=SCENE,
        message=MESSAGES.get(role, "Fill the schema."),
    )


def ceiling_usd(role: Role, schema: dict[str, Any], packet: Packet, cfg: RoleModel) -> float:
    """Worst case for one call: the estimated prompt (about 3.5 characters a token) plus the whole output cap."""
    price = budget.price_for(cfg.model)
    if price is None:
        return 0.0
    chars = len(packet.render()) + len(json.dumps(convert(schema).schema))
    return (chars / 3.5) * price.input_per_m / 1e6 + max_output_tokens(role, cfg.thinking) * price.output_per_m / 1e6


def run(args: argparse.Namespace, model_factory: Callable[[dict[Role, RoleModel]], StructuredModel],
        out: Callable[[str], None] = print) -> int:
    cfg = RoleModel(model=args.model, thinking=args.thinking)
    jobs: list[tuple[Role, dict[str, Any], Packet]] = []
    for role in args.role_list:
        schema = load_schema(args.fixtures, role)
        if schema is None:
            out(f"{role.value:<10} skip  no fixture {args.fixtures / (role.value + '.json')}")
            continue
        jobs.append((role, schema, build_packet(role)))
    worst = sum(ceiling_usd(r, s, p, cfg) for r, s, p in jobs)
    out(f"{len(jobs)} role(s), model {cfg.model}, thinking {cfg.thinking}; worst case ${worst:.4f}")
    model = None if args.dry_run else model_factory({r: cfg for r, _, _ in jobs})  # MissingKey raises here
    bad = 0
    for role, schema, packet in jobs:
        config, notes = build_config(role, schema, packet, cfg)
        sent = config.response_json_schema if isinstance(config.response_json_schema, dict) else {}
        issues = problems(sent)
        if args.dry_run:
            out(f"{role.value:<10} built schema {len(json.dumps(sent))} bytes, max_output_tokens "
                f"{config.max_output_tokens}, relaxed {len(notes)}, problems {issues or 'none'}")
            bad += bool(issues)
            continue
        assert model is not None
        bad += not _send(model, role, schema, packet, out)
    return 1 if bad else 0


def _send(model: StructuredModel, role: Role, schema: dict[str, Any], packet: Packet,
          out: Callable[[str], None]) -> bool:
    try:
        res = model.fill(role, schema, packet, turn_id=None, attempt=0)
    except ModelError as exc:
        out(f"{role.value:<10} FAIL  {type(exc).__name__}: {exc}")
        return False
    rec = res.record
    cost = (f"in {rec.tokens_in} (+{rec.tokens_in_cached} cached) out {rec.tokens_out} think "
            f"{rec.tokens_thinking}  ${rec.cost_usd:.5f}  {rec.latency_ms / 1000:.1f}s")
    level = rec.request.get("schema_level", 0)
    tag = f"  [schema level {level}: {'; '.join(rec.request.get('schema_rejected', []))}]" if level else ""
    errs = ["no JSON: " + str((rec.response or {}).get("error"))] if res.data is None else validate(res.data, schema)
    if errs:
        out(f"{role.value:<10} FAIL  {'; '.join(errs[:3])}  {cost}{tag}")
        return False
    out(f"{role.value:<10} ok    {cost}{tag}")
    return True


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    def factory(models: dict[Role, RoleModel]) -> StructuredModel:
        from engine.llm.gemini import GeminiModel

        return GeminiModel(models, max_retries=1)

    try:
        return run(args, factory)
    except MissingKey as exc:
        print(f"no key: {exc}. Put GEMINI_API_KEY=... in .env at the repo root (see .env.example).")
        return 2


if __name__ == "__main__":
    sys.exit(main())
