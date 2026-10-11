"""The event store: one SQLite file per game (data-model.md §1; T010).

    store = Store.create(path, seed=1234, milestone=1, config={...})   # writes the schema and `game_created`
    with store.transaction(turn_id="turn.1") as tx:                   # one SQLite transaction on exit
        fid = tx.mint("fact")
        tx.add(Event.of("fact_set", fact_id=fid, subject="world", predicate="weather", value="rain",
                        source="oracle", rule_id="00.14.2"))
        tx.state                                                       # the working projection, staged events in
    store.state                                                        # the projection (staged events
                                                                       # included while a transaction is open)
    store = Store.open(path)                                           # resume: latest snapshot + later events

Inside a transaction, `tx.state` and `store.state` are the same object: reducers mutate it in place and a
rollback rebuilds it from the latest snapshot and the log. `events` is append-only: SQLite triggers abort any UPDATE or DELETE. An event is validated twice before it is
staged: its payload model at construction, and `payload.check(tx.state)` against the working projection (every
id it names must exist or be created earlier in the same transaction). If the block raises, nothing is written
and every participant (the RNG) is restored to where it was.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterable, Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Protocol

from engine import ids
from engine.store.events import Event, Rejected, Timestamp, WritesReverted
from engine.store.projection import WorldState, apply_inplace, fold, project, reverted_seqs
from engine.store.records import TurnRecord

ENGINE_VERSION = "0.1.0"
DB_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  seq INTEGER PRIMARY KEY, branch_id TEXT NOT NULL DEFAULT 'main', turn_id TEXT, beat_id TEXT, game_time TEXT,
  type TEXT NOT NULL, payload TEXT NOT NULL, source TEXT NOT NULL, rule_id TEXT, schema_ver INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS events_type ON events(type);
CREATE INDEX IF NOT EXISTS events_turn ON events(turn_id);
CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
  BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
  BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
CREATE TABLE IF NOT EXISTS rng_draws (
  seq INTEGER PRIMARY KEY, stream TEXT NOT NULL, purpose TEXT NOT NULL, sides INTEGER, table_id TEXT,
  result INTEGER NOT NULL, event_seq INTEGER);
CREATE TRIGGER IF NOT EXISTS rng_no_update BEFORE UPDATE ON rng_draws
  BEGIN SELECT RAISE(ABORT, 'rng_draws are append-only'); END;
CREATE TRIGGER IF NOT EXISTS rng_no_delete BEFORE DELETE ON rng_draws
  BEGIN SELECT RAISE(ABORT, 'rng_draws are append-only'); END;
CREATE TABLE IF NOT EXISTS turns (
  turn_id TEXT PRIMARY KEY, input_verbatim TEXT NOT NULL, parts TEXT, delivered_verbatim TEXT, pause TEXT,
  verdicts TEXT, fallback_used INTEGER, cost_usd REAL, latency_ms INTEGER, record TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS model_calls (
  row_id INTEGER PRIMARY KEY, call_id TEXT NOT NULL, turn_id TEXT, role TEXT, attempt INTEGER NOT NULL DEFAULT 0,
  provider TEXT, model_id TEXT, schema_hash TEXT, request TEXT, response TEXT, tokens_in_cached INTEGER,
  tokens_in INTEGER, tokens_out INTEGER, tokens_thinking INTEGER, cost_usd REAL, latency_ms INTEGER,
  outcome TEXT, extra TEXT);
CREATE INDEX IF NOT EXISTS model_calls_key ON model_calls(turn_id, role, attempt);
CREATE TABLE IF NOT EXISTS snapshots (seq INTEGER PRIMARY KEY, blob TEXT NOT NULL, hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS facts_idx (
  fact_id TEXT NOT NULL, subject TEXT NOT NULL, predicate TEXT NOT NULL, value TEXT, valid_from_seq INTEGER NOT NULL,
  valid_to_seq INTEGER, source TEXT, certainty TEXT, visibility TEXT);
CREATE INDEX IF NOT EXISTS facts_sp ON facts_idx(subject, predicate, valid_from_seq);
CREATE INDEX IF NOT EXISTS facts_id ON facts_idx(fact_id);
CREATE TABLE IF NOT EXISTS rulings_idx (signature TEXT NOT NULL, ruling_id TEXT NOT NULL, event_seq INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS rulings_sig ON rulings_idx(signature);
CREATE TABLE IF NOT EXISTS branches (branch_id TEXT PRIMARY KEY, parent_id TEXT, fork_seq INTEGER);
CREATE TABLE IF NOT EXISTS minted (prefix TEXT PRIMARY KEY, n INTEGER NOT NULL);
"""

MODEL_CALL_COLUMNS = ("call_id", "turn_id", "role", "attempt", "provider", "model_id", "schema_hash", "request",
                      "response", "tokens_in_cached", "tokens_in", "tokens_out", "tokens_thinking", "cost_usd",
                      "latency_ms", "outcome")
_JSON_COLUMNS = ("request", "response")

# Counter prefixes no event creates (a beat id is minted by the Reader and only stamped on events as their
# `beat_id`; a beat that writes nothing leaves no trace). The store keeps their high-water mark in `minted`,
# committed with the transaction, so they are unique across turns and survive a reopen.
MINT_ONLY = (ids.BEAT,)

# Events a writes_reverted may target (DL-12-04: writes, within the current scene).
REVERTIBLE = frozenset({
    "entity_created", "fact_set", "quantity_changed", "quantity_defined", "relationship_set", "position_set",
    "knowledge_recorded", "clock_created", "clock_ticked", "condition_applied", "condition_removed", "sealed",
    "unsealed", "license_granted", "license_revoked", "meta_set",
})
# A take-back past the scene start (12.5.8 item 3) also reverts the scene change and the time that passed, so the PC
# is back in the beat's scene at the beat's hour (the RNG draws and the logs stay).
TAKE_BACK_EXTRA = frozenset({"scene_started", "scene_ended", "time_advanced", "boundary_marked"})


def is_mode_switch(ev: Event) -> bool:
    """[spec 033 P9] A `set_mode` event: it moves the time mode and no time. A rewind reverts it with the writes it came with."""
    p = ev.payload
    return ev.type == "time_advanced" and bool(getattr(p, "mode", None)) and p.to == p.from_  # type: ignore[union-attr]


class TxParticipant(Protocol):
    """Something with in-memory state that must roll back with a transaction (the RNG streams)."""

    def checkpoint(self) -> object: ...

    def restore(self, token: object) -> None: ...


class StoreError(RuntimeError):
    pass


def _dumps(x: Any) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), default=str)


class Transaction:
    """A batch of events committed together. Use through `Store.transaction()`; never construct directly."""

    def __init__(self, store: Store, turn_id: str | None) -> None:
        self.store = store
        self.turn_id = turn_id
        # The working state IS the committed state object, mutated in place (a deep copy per turn costs tens of
        # ms in a long game). A rollback rebuilds the committed state from the last snapshot and the log.
        self.state: WorldState = store.state
        self.events: list[Event] = []
        self.draws: list[dict[str, Any]] = []
        self._minted: dict[str, int] = {}
        self._broken = False

    def peek_seq(self) -> int:
        """The seq the next `add` will get."""
        return self.store.last_seq + len(self.events) + 1

    def mint(self, prefix: str) -> str:
        """A fresh counter id ('fact.7'); see engine/ids.py."""
        n = max(self.state.counters.get(prefix, 0), self.store.minted_hw.get(prefix, 0),
                self._minted.get(prefix, 0)) + 1
        self._minted[prefix] = n
        return ids.counter_id(prefix, n)

    def add(self, event: Event) -> int:
        """Validate `event` against the working state, stage it and reduce it in. Returns its seq.
        Raises `Rejected` (nothing staged) when a reference check fails."""
        if self._broken:
            raise StoreError("transaction is broken by an earlier reducer failure; let it roll back")
        if event.seq is not None:
            raise StoreError("event already has a seq; events are appended once")
        seq = self.peek_seq()
        ev = event.model_copy(update={
            "seq": seq,
            "turn_id": event.turn_id or self.turn_id,
            "game_time": event.game_time or self.state.time.now,
        })
        ev.payload.check(self.state)
        try:
            if isinstance(ev.payload, WritesReverted):
                self._revert(ev)
            else:
                apply_inplace(self.state, ev)
        except Rejected:
            raise
        except Exception:
            self._broken = True
            raise
        self.events.append(ev)
        return seq

    def add_all(self, events: Iterable[Event]) -> list[int]:
        return [self.add(e) for e in events]

    def _revert(self, ev: Event) -> None:  # rule: 12.14 (DL-12-04 scoping)
        p = ev.payload
        assert isinstance(p, WritesReverted)
        scene = self.state.scene
        if scene is None:
            raise Rejected("writes_reverted outside a scene")
        staged = {e.seq: e for e in self.events}
        # 12.5.8 item 3 (DL-12-85): a take-back may reach before the scene start, and reverts the scene change too
        allowed = REVERTIBLE | TAKE_BACK_EXTRA if p.take_back else REVERTIBLE
        for s in p.reverted:
            if s < scene.started_seq and not p.take_back:
                raise Rejected(f"writes_reverted: seq {s} is before the current scene (DL-12-04)")
            if s in self.state.reverted:
                raise Rejected(f"writes_reverted: seq {s} is already reverted")
            target = staged.get(s) or self.store.event(s)
            if target is None or (target.type not in allowed and not is_mode_switch(target)):
                raise Rejected(f"writes_reverted: seq {s} is not a revertible write")
        try:
            self.state = self.store._replay(before=min(p.reverted), extra=[*self.events, ev])  # noqa: SLF001
        except Rejected:
            raise
        except Exception as e:  # a later event depended on a reverted one
            raise Rejected(f"writes_reverted: the remaining events no longer apply ({e}); revert those too") from e

    def new_mints(self) -> dict[str, int]:
        """MINT_ONLY counters this transaction raised above the store's high-water mark."""
        hw = self.store.minted_hw
        return {p: n for p, n in self._minted.items() if p in MINT_ONLY and n > hw.get(p, 0)}

    def _commit(self) -> None:
        if self._broken:
            raise StoreError("transaction is broken")
        if not self.events and not self.draws and not self.new_mints():
            return
        self.store._write(self)  # noqa: SLF001


class Store:
    """One game's SQLite file. `state` is the committed projection."""

    def __init__(self, conn: sqlite3.Connection, path: Path) -> None:
        self.conn = conn
        self.path = path
        self.state = WorldState()
        self.last_seq = 0
        self._tx: Transaction | None = None
        self._participants: list[TxParticipant] = []
        self._turn_n = 0
        self.minted_hw: dict[str, int] = {}  # MINT_ONLY high-water marks (table `minted`)

    # ---------------------------------------------------------------- open / create
    @staticmethod
    def _connect(path: Path) -> sqlite3.Connection:
        conn = sqlite3.connect(str(path), isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @classmethod
    def create(cls, path: Path | str, *, seed: int, milestone: int = 1, config: Mapping[str, Any] | None = None,
               rules_hash: str | None = None, engine_version: str = ENGINE_VERSION) -> Store:
        """A new game file with its `game_created` event (FR-040 stamp). Refuses an existing file."""
        path = Path(path)
        if path.exists():
            raise StoreError(f"{path} already exists")
        if rules_hash is None:
            from engine.data.loader import rules_hash as _rh

            rules_hash = _rh()
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = cls._connect(path)
        conn.executescript(SCHEMA)
        conn.execute(f"PRAGMA user_version={DB_VERSION}")
        conn.execute("INSERT INTO branches(branch_id, parent_id, fork_seq) VALUES ('main', NULL, 0)")
        store = cls(conn, path)
        store.append([Event.of("game_created", source="engine", rule_id="FR-040", seed=seed,
                               engine_version=engine_version, rules_hash=rules_hash, milestone=milestone,
                               config=dict(config or {}))])
        return store

    @classmethod
    def open(cls, path: Path | str) -> Store:
        """Resume a game: the latest valid snapshot plus every later event."""
        path = Path(path)
        if not path.exists():
            raise StoreError(f"no game at {path}")
        conn = cls._connect(path)
        conn.executescript(SCHEMA)  # idempotent; adds index tables a newer engine introduced
        store = cls(conn, path)
        row = conn.execute("SELECT MAX(seq) FROM events").fetchone()
        store.last_seq = int(row[0] or 0)
        store.state = store._replay()
        store._turn_n = store._max_turn_n()
        store.minted_hw = {r["prefix"]: int(r["n"]) for r in conn.execute("SELECT prefix, n FROM minted")}
        return store

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> Store:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ---------------------------------------------------------------- writing events
    def attach(self, participant: TxParticipant) -> None:
        """Register in-memory state that rolls back with transactions (the RNG does this itself)."""
        self._participants.append(participant)

    @property
    def in_transaction(self) -> bool:
        return self._tx is not None

    @contextmanager
    def transaction(self, turn_id: str | None = None) -> Iterator[Transaction]:
        """Stage events; commit them in one SQLite transaction when the block exits cleanly."""
        if self._tx is not None:
            raise StoreError("a transaction is already open")
        tokens = [(p, p.checkpoint()) for p in self._participants]
        tx = Transaction(self, turn_id)
        self._tx = tx
        try:
            yield tx
            tx._commit()  # noqa: SLF001
        except BaseException:
            for p, t in tokens:
                p.restore(t)
            if tx.events or tx._broken or tx.state is not self.state:  # noqa: SLF001
                self.state = self._replay()
            raise
        finally:
            self._tx = None

    def append(self, events: list[Event], turn_id: str | None = None) -> list[int]:
        """Append `events` in one transaction (all or nothing). Returns their seqs."""
        if self._tx is not None:
            return self._tx.add_all(events)
        with self.transaction(turn_id) as tx:
            return tx.add_all(events)

    def _write(self, tx: Transaction) -> None:
        c = self.conn
        reverted = False
        c.execute("BEGIN IMMEDIATE")
        try:
            for ev in tx.events:
                c.execute(
                    "INSERT INTO events(seq, branch_id, turn_id, beat_id, game_time, type, payload, source, rule_id,"
                    " schema_ver) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (ev.seq, ev.branch_id, ev.turn_id, ev.beat_id,
                     ev.game_time.model_dump_json() if ev.game_time else None, ev.type, _dumps(ev.payload_json()),
                     ev.source, ev.rule_id, ev.schema_ver))
                self._index_event(ev)
                reverted = reverted or ev.type == "writes_reverted"
            for d in tx.draws:
                c.execute("INSERT INTO rng_draws(stream, purpose, sides, table_id, result, event_seq)"
                          " VALUES (:stream,:purpose,:sides,:table_id,:result,:event_seq)", d)
            mints = tx.new_mints()
            for prefix, n in mints.items():
                c.execute("INSERT INTO minted(prefix, n) VALUES (?, ?) ON CONFLICT(prefix) DO UPDATE SET n=excluded.n",
                          (prefix, n))
            c.execute("COMMIT")
        except BaseException:
            c.execute("ROLLBACK")
            raise
        self.minted_hw.update(mints)
        if tx.events:
            self.last_seq = tx.events[-1].seq or self.last_seq
            self.state = tx.state
        if reverted:
            self.rebuild_indexes()
        if any(ev.type == "scene_ended" for ev in tx.events):
            self.snapshot()

    def _index_event(self, ev: Event) -> None:
        p = ev.payload_json()
        if ev.type == "fact_set":
            if p.get("supersedes"):
                self.conn.execute("UPDATE facts_idx SET valid_to_seq=? WHERE fact_id=? AND valid_to_seq IS NULL",
                                  (ev.seq, p["supersedes"]))
            self.conn.execute(
                "INSERT INTO facts_idx(fact_id, subject, predicate, value, valid_from_seq, valid_to_seq, source,"
                " certainty, visibility) VALUES (?,?,?,?,?,NULL,?,?,?)",
                (p["fact_id"], p["subject"], p["predicate"], _dumps(p["value"]), ev.seq, p["source"],
                 p["certainty"], p["visibility"]))
        elif ev.type == "ruling_logged":
            r = p["ruling"]
            self.conn.execute("INSERT INTO rulings_idx(signature, ruling_id, event_seq) VALUES (?,?,?)",
                              (r["signature"], r["id"], ev.seq))

    def rebuild_indexes(self) -> None:
        """Drop and re-derive facts_idx and rulings_idx from the events (skipping reverted writes)."""
        evs = list(self.events())
        skip = reverted_seqs(evs)
        c = self.conn
        c.execute("BEGIN IMMEDIATE")
        try:
            c.execute("DELETE FROM facts_idx")
            c.execute("DELETE FROM rulings_idx")
            for ev in evs:
                if ev.seq not in skip:
                    self._index_event(ev)
            c.execute("COMMIT")
        except BaseException:
            c.execute("ROLLBACK")
            raise

    # ---------------------------------------------------------------- reading events and state
    @staticmethod
    def _row_event(r: sqlite3.Row) -> Event:
        return Event(seq=r["seq"], branch_id=r["branch_id"], turn_id=r["turn_id"], beat_id=r["beat_id"],
                     game_time=Timestamp.model_validate_json(r["game_time"]) if r["game_time"] else None,
                     type=r["type"], payload=json.loads(r["payload"]), source=r["source"], rule_id=r["rule_id"],
                     schema_ver=r["schema_ver"])

    def events(self, since: int = 0, until: int | None = None, types: Iterable[str] | None = None) -> Iterator[Event]:
        """Committed events with since < seq <= until, in order, optionally of the given types."""
        q = "SELECT * FROM events WHERE seq > ?"
        args: list[Any] = [since]
        if until is not None:
            q += " AND seq <= ?"
            args.append(until)
        if types is not None:
            ts = list(types)
            q += f" AND type IN ({','.join('?' * len(ts))})"
            args += ts
        for r in self.conn.execute(q + " ORDER BY seq", args):
            yield self._row_event(r)

    def event(self, seq: int) -> Event | None:
        r = self.conn.execute("SELECT * FROM events WHERE seq=?", (seq,)).fetchone()
        return self._row_event(r) if r else None

    def rebuild(self) -> WorldState:
        """The projection rebuilt from every event, ignoring snapshots (must equal `state`)."""
        return project(self.events())

    def _replay(self, before: int | None = None, extra: list[Event] | None = None) -> WorldState:
        """Latest usable snapshot (below `before`) + committed events after it + `extra` staged events."""
        start = WorldState()
        q = "SELECT seq, blob, hash FROM snapshots" + (" WHERE seq < ?" if before is not None else "")
        for r in self.conn.execute(q + " ORDER BY seq DESC", (before,) if before is not None else ()):
            if hashlib.sha256(r["blob"].encode()).hexdigest() != r["hash"]:
                continue
            try:  # a snapshot from another engine version may not load: fall back to an older one or the log
                start = WorldState.model_validate_json(r["blob"])
                break
            except ValueError:
                continue
        evs = list(self.events(since=start.last_seq)) + list(extra or [])
        skip = reverted_seqs(evs)
        if skip and min(skip) <= start.last_seq:
            return self._replay(before=min(skip), extra=extra)
        return fold(start, evs, skip=skip)

    def snapshot(self) -> int:
        """Checkpoint the committed projection (done automatically after scene_ended). Returns its seq."""
        blob = self.state.model_dump_json()
        self.conn.execute("INSERT OR IGNORE INTO snapshots(seq, blob, hash) VALUES (?,?,?)",
                          (self.state.last_seq, blob, hashlib.sha256(blob.encode()).hexdigest()))
        return self.state.last_seq

    # ---------------------------------------------------------------- facts and rulings indexes
    def fact(self, subject: str, predicate: str, at_seq: int | None = None) -> dict[str, Any] | None:
        """Bi-temporal: the fact (subject, predicate) as it stood after event `at_seq` (default: now)."""
        at = self.last_seq if at_seq is None else at_seq
        r = self.conn.execute(
            "SELECT * FROM facts_idx WHERE subject=? AND predicate=? AND valid_from_seq<=?"
            " AND (valid_to_seq IS NULL OR valid_to_seq>?) ORDER BY valid_from_seq DESC LIMIT 1",
            (subject, predicate, at, at)).fetchone()
        return self._fact_row(r) if r else None

    def fact_history(self, subject: str, predicate: str) -> list[dict[str, Any]]:
        rows = self.conn.execute("SELECT * FROM facts_idx WHERE subject=? AND predicate=? ORDER BY valid_from_seq",
                                 (subject, predicate))
        return [self._fact_row(r) for r in rows]

    @staticmethod
    def _fact_row(r: sqlite3.Row) -> dict[str, Any]:
        d = dict(r)
        d["value"] = json.loads(d["value"])
        return d

    def rulings(self, signature: str) -> list[tuple[str, int]]:
        """(ruling_id, event_seq) of every logged ruling with this signature, oldest first (00.15.6)."""
        rows = self.conn.execute("SELECT ruling_id, event_seq FROM rulings_idx WHERE signature=? ORDER BY event_seq",
                                 (signature,))
        return [(r[0], r[1]) for r in rows]

    # ---------------------------------------------------------------- side tables
    def record_rng_draw(self, stream: str, purpose: str, result: int, *, sides: int | None = None,
                        table_id: str | None = None, event_seq: int | None = None) -> None:
        """Log one draw (FR-027). Inside a transaction it is staged and rolls back with it."""
        row = {"stream": stream, "purpose": purpose, "sides": sides, "table_id": table_id, "result": result,
               "event_seq": event_seq}
        if self._tx is not None:
            row["event_seq"] = event_seq if event_seq is not None else self._tx.peek_seq()
            self._tx.draws.append(row)
        else:
            row["event_seq"] = event_seq if event_seq is not None else self.last_seq + 1
            self.conn.execute("INSERT INTO rng_draws(stream, purpose, sides, table_id, result, event_seq)"
                              " VALUES (:stream,:purpose,:sides,:table_id,:result,:event_seq)", row)

    def rng_draws(self, stream: str | None = None) -> list[dict[str, Any]]:
        q, args = "SELECT * FROM rng_draws", ()
        if stream is not None:
            q, args = q + " WHERE stream=?", (stream,)
        return [dict(r) for r in self.conn.execute(q + " ORDER BY seq", args)]

    def record_model_call(self, rec: Any) -> None:
        """Log one model call. `rec` is engine.llm.base.ModelCallRecord or anything with `.model_dump()` (or a
        mapping) carrying the model_calls columns; unknown keys go to `extra`. Written at once, outside any
        transaction, so failed turns keep their cost. A retried call_id adds a row; the latest row wins."""
        d = dict(rec.model_dump(mode="json") if hasattr(rec, "model_dump") else rec)
        row = {k: d.pop(k, None) for k in MODEL_CALL_COLUMNS}
        if row["call_id"] is None:
            raise StoreError("model call record without call_id")
        row["attempt"] = row["attempt"] or 0
        for k in _JSON_COLUMNS:
            row[k] = _dumps(row[k]) if row[k] is not None else None
        if hasattr(row["outcome"], "value"):
            row["outcome"] = row["outcome"].value
        row["extra"] = _dumps(d) if d else None
        cols = (*MODEL_CALL_COLUMNS, "extra")
        self.conn.execute(f"INSERT INTO model_calls({','.join(cols)}) VALUES ({','.join(':' + k for k in cols)})", row)

    def model_calls(self, turn_id: str | None = None) -> list[dict[str, Any]]:
        """Model call rows (latest row per call_id), in call order; `request`/`response` parsed."""
        q = ("SELECT * FROM model_calls WHERE row_id IN (SELECT MAX(row_id) FROM model_calls GROUP BY call_id)"
             + (" AND turn_id=?" if turn_id is not None else "") + " ORDER BY row_id")
        out = []
        for r in self.conn.execute(q, (turn_id,) if turn_id is not None else ()):
            d = dict(r)
            for k in (*_JSON_COLUMNS, "extra"):
                d[k] = json.loads(d[k]) if d[k] is not None else None
            out.append(d)
        return out

    def new_turn_id(self) -> str:
        self._turn_n += 1
        return ids.counter_id(ids.TURN, self._turn_n)

    def _max_turn_n(self) -> int:
        n = 0
        rows = self.conn.execute("SELECT turn_id FROM turns UNION SELECT DISTINCT turn_id FROM events"
                                 " WHERE turn_id IS NOT NULL")
        for (t,) in rows:
            parsed = ids.parse_counter_id(t) if isinstance(t, str) else None
            if parsed and parsed[0] == ids.TURN:
                n = max(n, parsed[1])
        return n

    def save_turn(self, record: TurnRecord | Mapping[str, Any]) -> None:
        """Insert or replace the turn record (T6 may save a partial record that T12 completes)."""
        rec = record if isinstance(record, TurnRecord) else TurnRecord.model_validate(record)
        d = rec.model_dump(mode="json", by_alias=True)
        self.conn.execute(
            "INSERT OR REPLACE INTO turns(turn_id, input_verbatim, parts, delivered_verbatim, pause, verdicts,"
            " fallback_used, cost_usd, latency_ms, record) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (rec.turn_id, rec.input_verbatim, _dumps(d["parts"]), rec.delivered_verbatim,
             _dumps(d["pause"]) if rec.pause is not None else None, _dumps(d["verdicts"]), int(rec.fallback_used),
             rec.cost_usd, rec.latency_ms, _dumps(d)))
        parsed = ids.parse_counter_id(rec.turn_id)
        if parsed and parsed[0] == ids.TURN:
            self._turn_n = max(self._turn_n, parsed[1])

    def turn(self, turn_id: str) -> TurnRecord | None:
        r = self.conn.execute("SELECT record FROM turns WHERE turn_id=?", (turn_id,)).fetchone()
        return TurnRecord.model_validate_json(r[0]) if r else None
