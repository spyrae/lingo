from pathlib import Path

import pytest

from lingo.memory.database import Database


@pytest.mark.asyncio
async def test_apply_schema_creates_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "lingo.db"
    db = Database(db_path)
    await db.connect()
    try:
        row = await db.fetchone(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        assert row is not None
        assert row["name"] == "users"

        row = await db.fetchone(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='vocabulary'"
        )
        assert row is not None
        assert row["name"] == "vocabulary"
    finally:
        await db.disconnect()


@pytest.mark.asyncio
async def test_can_insert_user(tmp_path: Path) -> None:
    db_path = tmp_path / "lingo.db"
    db = Database(db_path)
    await db.connect()
    try:
        await db.execute("INSERT INTO users (telegram_id) VALUES (?)", (123,))
        await db.commit()
        user = await db.fetchone("SELECT telegram_id, level FROM users WHERE telegram_id = ?", (123,))
        assert user is not None
        assert user["telegram_id"] == 123
        assert user["level"] == "beginner"
    finally:
        await db.disconnect()


