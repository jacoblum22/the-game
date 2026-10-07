"""TurnContext: everything one turn of PR-12-1 needs, bundled (the store, the open transaction, rules, RNG, model,
model-call recorder, game config and milestone).

    ctx = TurnContext.for_store(store, model=OfflineModel(), config={"oracle_free_cap_per_scene": 6})
    result = run_turn(ctx, "I slip past the watchman.")          # engine/dm/turn.py opens and commits `ctx.tx`

`tx` is set by the turn loop for the length of one turn (T1-T6) and is None between turns. `state` reads the working
projection inside a turn (staged events included) and the committed one outside. Injectable hooks (`harm_hook`,
`dispute`) let a front end or a test replace a collaborator; each default names the module that owns it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from engine.data.loader import Rules, load_rules
from engine.llm.base import ModelCallRecord, StructuredModel
from engine.rng import Rng
from engine.store.db import Store, Transaction
from engine.store.projection import WorldState
from engine.time.scheduler import TimeContext

Recorder = Callable[[ModelCallRecord], None]


class DisputeHandler(Protocol):
    """12.3.6: answer a DISPUTE part from the turn log and the store. Returns the OOF answer line."""

    def __call__(self, ctx: TurnContext, text: str) -> str: ...


@dataclass
class TurnContext:
    store: Store
    rules: Rules
    rng: Rng
    model: StructuredModel
    recorder: Recorder | None = None  # default: store.record_model_call
    config: Mapping[str, Any] = field(default_factory=dict)  # GameConfig fields (contracts/engine-api.md)
    milestone: int = 0  # 0: the game's (game_created)
    tx: Transaction | None = None
    dispute: DisputeHandler | None = None  # TODO(engine/audit dispute handling, 12.3.6): default in turn.py
    call_ids: list[str] = field(default_factory=list)  # model calls made this turn (TurnRecord.model_calls)

    @classmethod
    def for_store(cls, store: Store, *, model: StructuredModel, rules: Rules | None = None, rng: Rng | None = None,
                  config: Mapping[str, Any] | None = None, recorder: Recorder | None = None) -> TurnContext:
        return cls(store=store, rules=rules or load_rules(), rng=rng or Rng.for_store(store), model=model,
                   recorder=recorder, config=dict(config or {}))

    @property
    def state(self) -> WorldState:
        return self.tx.state if self.tx is not None else self.store.state

    @property
    def turn_id(self) -> str | None:
        return self.tx.turn_id if self.tx is not None else None

    def need_tx(self) -> Transaction:
        if self.tx is None:
            raise RuntimeError("no open turn transaction (run inside engine.dm.turn.run_turn)")
        return self.tx

    def mint(self, prefix: str) -> str:
        return self.need_tx().mint(prefix)

    def time_ctx(self) -> TimeContext:
        return TimeContext(self.need_tx(), self.rules, self.rng, milestone=self.milestone)

    def record_call(self, rec: ModelCallRecord) -> None:
        """The recorder every role call uses: logs the call and keeps its id for the turn record."""
        if rec.call_id and rec.call_id not in self.call_ids:
            self.call_ids.append(rec.call_id)
        (self.recorder or self.store.record_model_call)(rec)

    @property
    def free_cap(self) -> int | None:
        cap = self.config.get("oracle_free_cap_per_scene", 6)
        return int(cap) if cap is not None else None

    def auto_commit(self) -> bool:
        """The player's `auto_commit` preference (01.7.4; ch.14): meta, else the config, else off."""
        v = self.state.meta.get("auto_commit")
        if v is None:
            v = self.config.get("auto_commit", False)
        return bool(v)
