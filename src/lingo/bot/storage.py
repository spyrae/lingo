"""SQLite-backed FSM storage for aiogram 3.

Persists FSM state and data across bot restarts so that users
don't lose their lesson/practice progress when the container restarts.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import aiosqlite
from aiogram.fsm.storage.base import BaseStorage, StorageKey

_SCHEMA = """
CREATE TABLE IF NOT EXISTS fsm_states (
    key TEXT PRIMARY KEY,
    state TEXT,
    data TEXT DEFAULT '{}'
);
"""


def _make_key(key: StorageKey) -> str:
    return f"{key.bot_id}:{key.chat_id}:{key.user_id}"


class SQLiteStorage(BaseStorage):
    def __init__(self, db_path: str | Path) -> None:
        self._db_path = Path(db_path)
        self._conn: aiosqlite.Connection | None = None

    async def _ensure_conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = await aiosqlite.connect(self._db_path)
            self._conn.row_factory = aiosqlite.Row
            await self._conn.executescript(_SCHEMA)
            await self._conn.commit()
        return self._conn

    async def set_state(self, key: StorageKey, state: str | None = None) -> None:
        conn = await self._ensure_conn()
        k = _make_key(key)
        state_str = state.state if hasattr(state, "state") else state
        await conn.execute(
            """
            INSERT INTO fsm_states (key, state) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET state = excluded.state
            """,
            (k, state_str),
        )
        await conn.commit()

    async def get_state(self, key: StorageKey) -> str | None:
        conn = await self._ensure_conn()
        k = _make_key(key)
        cursor = await conn.execute("SELECT state FROM fsm_states WHERE key = ?", (k,))
        row = await cursor.fetchone()
        return str(row["state"]) if row and row["state"] else None

    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:
        conn = await self._ensure_conn()
        k = _make_key(key)
        serialized = json.dumps(dict(data), ensure_ascii=False, default=str)
        await conn.execute(
            """
            INSERT INTO fsm_states (key, data) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET data = excluded.data
            """,
            (k, serialized),
        )
        await conn.commit()

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        conn = await self._ensure_conn()
        k = _make_key(key)
        cursor = await conn.execute("SELECT data FROM fsm_states WHERE key = ?", (k,))
        row = await cursor.fetchone()
        if row and row["data"]:
            try:
                return dict(json.loads(row["data"]))
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None
