# Data model: Measurement harness

## `evals/corpus/narration.json.gz`

```text
{ "format": 1, "population": {...counts...},
  "saves":    { <save stem>: {"late": bool, "turns": int, "calls": {role: n}} },
  "turns":    [ {"save", "turn", "fallback": bool, "calls": {role: n},
                 "versions": [ {"kind": draft|redraft|cut, "sents": [key...],
                                "mentions": [[name, kind]...],
                                "claims": [[sentence, class, unknown_subject: bool]...],
                                "verdicts": [[verdict, fix, reason_head]...]} ]} ],
  "sections": { <sha16>: <section text> },
  "packets":  [ {"save", "turn", "sections": [[name, sha16]...], "draft": {"fiction", "mentions"}} ] }
```

- `sents` are `narration._key` forms of the checker's numbered sentences (enough for instability; prose is in
  `packets[].draft` where it matters).
- A packet's `turn` links it to its `turns` entry (claims and verdicts of the first checked version).
- Validation: file ≤ 3 MB; every packet's section hashes resolve.

## `evals/reader_golden.jsonl` (one object per line)

| Field | Type | Notes |
|---|---|---|
| `id` | str | `g001`… |
| `source` | str | `<transcript stem>#<input>` or `constructed` |
| `issue` | str? | `P-023` etc. |
| `pair` | str? | shared id for a negated minimal pair |
| `context` | str | one line: who and what is in the scene, any licence held |
| `line` | str | the player's words |
| `labels` | obj | `verb` (`verb.*` or null), `gate` (G0–G4), `necessity` (01.4.1 reason), `against_will`, `uses_power`, `speech` (bool), `question_kind` (`who_is` `where_is` `what_happened` `what_like` `what_want` `who_knows` `none`) |
| `recorded` | obj? | today's Haiku Reader answer: `verb`, `gate`, `necessity` of the first beat (null when no beat) |

## Long-horizon summary (`evals/baselines/longhorizon.txt`)

One block per mode (`aged`, `scripted`): seed, turns, then one line per metric of R9.
