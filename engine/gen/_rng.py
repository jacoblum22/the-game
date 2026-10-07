"""The random source every generator in `engine/gen` draws from.

A generator never builds its own randomness: it takes an `rng` that satisfies `SeedRng`, the subset of
`random.Random` the reference simulations call. A plain `random.Random(seed)` therefore reproduces the
reference scripts draw for draw, and the engine's logged RC-RNG streams (engine/rng.py) can be passed in
as long as they offer these methods with `random.Random`'s semantics.
"""

from __future__ import annotations

from collections.abc import MutableSequence, Sequence
from typing import Any, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class SeedRng(Protocol):
    """The methods of `random.Random` the generators use (same signatures, same semantics)."""

    def random(self) -> float: ...

    def randint(self, a: int, b: int) -> int: ...

    def randrange(self, start: int, stop: int | None = ..., step: int = ...) -> int: ...

    def choice(self, seq: Sequence[T]) -> T: ...

    def choices(self, population: Sequence[T], weights: Sequence[float] | None = ..., *,
                cum_weights: Sequence[float] | None = ..., k: int = ...) -> list[T]: ...

    def sample(self, population: Sequence[T], k: int, *, counts: Any = ...) -> list[T]: ...

    def shuffle(self, x: MutableSequence[Any]) -> None: ...
