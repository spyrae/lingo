from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import aiosqlite


class Database:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA foreign_keys = ON")
        await self.apply_schema()

    async def apply_schema(self) -> None:
        conn = self.conn
        schema_path = Path(__file__).with_name("schema.sql")
        schema_sql = schema_path.read_text(encoding="utf-8")
        await conn.executescript(schema_sql)
        await conn.commit()

    async def disconnect(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Database not connected")
        return self._conn

    async def execute(self, query: str, params: Sequence[Any] = ()) -> aiosqlite.Cursor:
        return await self.conn.execute(query, params)

    async def executemany(self, query: str, params: Sequence[Sequence[Any]]) -> None:
        await self.conn.executemany(query, params)
        await self.conn.commit()

    async def fetchone(
        self, query: str, params: Sequence[Any] = ()
    ) -> dict[str, Any] | None:
        cursor = await self.execute(query, params)
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def fetchall(
        self, query: str, params: Sequence[Any] = ()
    ) -> list[dict[str, Any]]:
        cursor = await self.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    async def commit(self) -> None:
        await self.conn.commit()

