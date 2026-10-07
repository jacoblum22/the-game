"""RC-RNG: named random streams seeded from the game seed; every draw logged (FR-027; T014).

    rng = Rng.for_store(store)            # seed from game_created; replays the logged draws to resume
    rng.d(20, "roll_check frame.3")       # 1..20 on the "dice" stream
    rng.d100("oracle: is the door barred?", stream="oracle")
    rng.choice(["a", "b"], "npc name", stream="gen", table_id="tbl.name_given")
    rng.weighted({"x": 3, "y": 1}, "denizen", stream="gen")

Every helper reduces to ONE primitive: `randint(1, n)` on a named stream, logged as (stream, purpose, sides=n,
table_id, result). Resume replays the logged primitives per stream in order (and checks each result), so a
resumed game draws exactly what an unbroken one would. A draw made inside a store transaction rolls back with
it: the log row is never written and the stream is restored.

Stream seeds: sha256(f"{game_seed}:{stream}") -> 64-bit int. Streams are independent: adding draws on "gen"
never shifts the "dice" sequence. Conventional names: dice (checks), oracle, tables, gen (generators), seed
(world seed), npc.
"""

from __future__ import annotations

import hashlib
import random
from collections.abc import Mapping, Sequence
from typing import Any, Protocol, TypeVar

T = TypeVar("T")


class DrawLog(Protocol):
    def record_rng_draw(self, stream: str, purpose: str, result: int, *, sides: int | None = None,
                        table_id: str | None = None, event_seq: int | None = None) -> None: ...


class RngDivergence(RuntimeError):
    """Replaying the draw log produced a different result: the seed or the stream derivation changed."""


def stream_seed(game_seed: int, stream: str) -> int:
    return int.from_bytes(hashlib.sha256(f"{game_seed}:{stream}".encode()).digest()[:8], "big")


class Rng:
    def __init__(self, seed: int, log: DrawLog | None = None) -> None:
        self.seed = seed
        self.log = log
        self._streams: dict[str, random.Random] = {}

    @classmethod
    def for_store(cls, store: Any) -> Rng:
        """The game's RNG: seeded from `game_created`, resumed from `rng_draws`, attached to the store so
        transactions roll it back."""
        if store.state.game is None:
            raise ValueError("store has no game_created event")
        rng = cls(store.state.game.seed, log=store)
        rng.replay(store.rng_draws())
        store.attach(rng)
        return rng

    def _stream(self, name: str) -> random.Random:
        s = self._streams.get(name)
        if s is None:
            s = self._streams[name] = random.Random(stream_seed(self.seed, name))
        return s

    def replay(self, draws: Sequence[Mapping[str, Any]]) -> None:
        """Advance the streams past already-logged draws (resume). Raises RngDivergence on a mismatch."""
        for d in draws:
            got = self._stream(d["stream"]).randint(1, int(d["sides"]))
            if got != d["result"]:
                raise RngDivergence(f"rng_draws seq {d.get('seq')}: replay gave {got}, log has {d['result']}")

    # -- transaction participation (engine/store/db.py TxParticipant)
    def checkpoint(self) -> object:
        return {k: s.getstate() for k, s in self._streams.items()}

    def restore(self, token: object) -> None:
        assert isinstance(token, dict)
        for k in list(self._streams):
            if k in token:
                self._streams[k].setstate(token[k])
            else:
                del self._streams[k]

    # -- the one primitive
    def draw(self, n: int, purpose: str, *, stream: str = "dice", table_id: str | None = None) -> int:
        """1..n on `stream`, logged with its purpose."""
        if n < 1:
            raise ValueError(f"cannot draw from {n} outcomes")
        if not purpose:
            raise ValueError("every draw needs a purpose (FR-027)")
        result = self._stream(stream).randint(1, n)
        if self.log is not None:
            self.log.record_rng_draw(stream, purpose, result, sides=n, table_id=table_id)
        return result

    # -- helpers
    def d(self, sides: int, purpose: str, *, stream: str = "dice") -> int:
        """One die: 1..sides."""
        return self.draw(sides, purpose, stream=stream)

    def d100(self, purpose: str, *, stream: str = "dice") -> int:
        return self.draw(100, purpose, stream=stream)

    def choice(self, seq: Sequence[T], purpose: str, *, stream: str = "tables", table_id: str | None = None) -> T:
        """One element of `seq`, uniformly."""
        if not seq:
            raise ValueError("choice from an empty sequence")
        return seq[self.draw(len(seq), purpose, stream=stream, table_id=table_id) - 1]

    def weighted(self, table: Mapping[T, int] | Sequence[tuple[T, int]], purpose: str, *, stream: str = "tables",
                 table_id: str | None = None) -> T:
        """One key by integer weight (weights >= 0, at least one > 0), in the table's own order."""
        items = list(table.items()) if isinstance(table, Mapping) else list(table)
        total = sum(w for _, w in items)
        if total <= 0 or any(w < 0 for _, w in items):
            raise ValueError("weights must be >= 0 with a positive total")
        r = self.draw(total, purpose, stream=stream, table_id=table_id)
        for value, w in items:
            r -= w
            if r <= 0:
                return value
        raise AssertionError("unreachable")

    def roll_die(self, die: str, purpose: str, *, stream: str = "tables", table_id: str | None = None) -> int:
        """A die expression from rules data: 'd20' or 'kdN' (sum of k draws)."""
        count, _, sides = die.lower().partition("d")
        k = int(count) if count else 1
        return sum(self.draw(int(sides), purpose, stream=stream, table_id=table_id) for _ in range(k))

    def pick(self, table: Mapping[str, Any], purpose: str, *, stream: str = "tables") -> tuple[int, Any]:
        """Roll a data table (`die` plus `results` rows with `range` 'a-b', 'a', [a, b] or a); return (roll, row).
        Recency and context filtering are roll_table's (12), not this helper's."""
        roll = self.roll_die(str(table["die"]), purpose, stream=stream, table_id=table.get("id"))
        for row in table["results"]:
            lo, hi = _range(row["range"])
            if lo <= roll <= hi:
                return roll, row
        raise ValueError(f"{table.get('id')}: no row covers {roll}")


def _range(r: Any) -> tuple[int, int]:
    def num(x: Any) -> int:
        return 100 if str(x).strip() == "00" else int(x)

    if isinstance(r, int):
        return r, r
    if isinstance(r, (list, tuple)):
        return num(r[0]), num(r[-1])
    a, _, b = str(r).partition("-")
    return num(a), num(b or a)
