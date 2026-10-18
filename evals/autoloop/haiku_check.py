"""Can Haiku catch the DM's contradictions? (Jake, 2026-10-18) The same rounds and the same state as jev_check.py (the
reply, the turns before it word for word, the notebook entries it names), one call each; Haiku quotes the clashing
line if there is one. Nothing in the game is changed. The key is read from the repo's .env (ANTHROPIC_API_KEY) and
given to this client only: it never goes into the environment, where Claude Code would pick it up for the DM.
    PYTHONPATH=".;evals/autoloop" .venv/Scripts/python evals/autoloop/haiku_check.py <negatives> <out.json> [model] [severity]"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import anthropic
import jev_check as base

MODEL = sys.argv[3] if len(sys.argv) > 3 else "claude-haiku-5-5"
ENV = Path(__file__).parents[2] / ".env"
KEY = next(line.split("=", 1)[1].strip().strip('"') for line in ENV.read_text(encoding="utf-8").splitlines()
           if line.startswith("ANTHROPIC_API_KEY="))
client = anthropic.Anthropic(api_key=KEY, max_retries=5)
SYSTEM = ("You check a solo D&D game run by an AI DM for continuity errors. You get the DM's notebook entries, the "
          "turns before, and the DM's NEW REPLY. Find any statement in the NEW REPLY that contradicts EARLIER PLAY or "
          "the NOTEBOOK, or contradicts another statement in the same reply: numbers and counts, times, dates and ages, "
          "distances and travel times, places, who did or said what, who has what. Something that changed because of "
          "events in play is not a contradiction; neither is something new that clashes with nothing; neither is a "
          "character lying or being wrong, if the story shows that. Only flag what the text shows plainly.")
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["contradiction", "quote", "clashes_with"],
          "properties": {"contradiction": {"type": "boolean"},
                         "quote": {"type": "string", "description": "the NEW REPLY's words, short; empty if none"},
                         "clashes_with": {"type": "string", "description": "what it clashes with, short; empty if none"}}}


# Second try (the first flagged 56 of 60 clean rounds with Sonnet): every problem with a severity, so the game can act
# only on the ones a player would notice.
SYSTEM2 = SYSTEM + (" List each problem with a severity: 1 a nitpick a player wouldn't notice or mind (a minute of "
                    "clock drift, loose wording); 2 a player paying attention would notice; 3 it breaks the story (a "
                    "dead man acting, a place in two directions, a count that can't be). Return an empty list if none.")
SCHEMA2 = {"type": "object", "additionalProperties": False, "required": ["problems"],
           "properties": {"problems": {"type": "array", "items": {
               "type": "object", "additionalProperties": False, "required": ["quote", "clashes_with", "severity"],
               "properties": {"quote": {"type": "string"}, "clashes_with": {"type": "string"},
                              "severity": {"type": "integer", "enum": [1, 2, 3]}}}}}}
MODE2 = len(sys.argv) > 4 and sys.argv[4] == "severity"


def ask(case: dict) -> dict:
    try:
        r = client.messages.create(
            model=MODEL, max_tokens=4000, system=SYSTEM2 if MODE2 else SYSTEM,
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA2 if MODE2 else SCHEMA}},
            messages=[{"role": "user", "content": base.state(case["game"], case["round"])}])
        text = next(b.text for b in r.content if b.type == "text")
        got = json.loads(text)
        if MODE2:
            got["severity"] = max((x["severity"] for x in got["problems"]), default=0)
            got["contradiction"] = got["severity"] >= 2
            got["quote"] = " / ".join(x["quote"] for x in got["problems"] if x["severity"] >= 2)
        return case | got | {"tokens": r.usage.input_tokens, "out": r.usage.output_tokens}
    except Exception as e:  # noqa: BLE001
        return case | {"error": f"{type(e).__name__}: {str(e)[:200]}"}


def main() -> None:
    cs = base.cases()
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(ask, cs))
    Path(sys.argv[2]).write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    ok = [r for r in res if "contradiction" in r]
    pos, neg = [r for r in ok if r["label"]], [r for r in ok if not r["label"]]
    print(f"{MODEL}: {len(ok)} of {len(res)} answered; {sum(r['tokens'] for r in ok)} input, "
          f"{sum(r['out'] for r in ok)} output tokens; errors: {sorted({r['error'][:80] for r in res if 'error' in r})}\n"
          f"caught {sum(r['contradiction'] for r in pos)} of {len(pos)} contradiction rounds; "
          f"flagged {sum(r['contradiction'] for r in neg)} of {len(neg)} clean rounds", file=sys.stderr)
    if MODE2:
        for cut in (2, 3):
            print(f"severity {cut}+: caught {sum(r['severity'] >= cut for r in pos)} of {len(pos)}; "
                  f"flagged {sum(r['severity'] >= cut for r in neg)} of {len(neg)} clean", file=sys.stderr)


if __name__ == "__main__":
    main()
