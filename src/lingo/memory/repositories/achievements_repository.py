from __future__ import annotations

from lingo.memory.database import Database


class AchievementsRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def list_unlocked_ids(self, user_id: int) -> set[str]:
        rows = await self._db.fetchall(
            "SELECT achievement_id FROM achievements WHERE user_id = ?",
            (user_id,),
        )
        return {str(r["achievement_id"]) for r in rows}

    async def unlock(self, user_id: int, achievement_id: str) -> bool:
        """
        Returns true if newly unlocked.
        """
        cur = await self._db.execute(
            "INSERT OR IGNORE INTO achievements (user_id, achievement_id) VALUES (?, ?)",
            (user_id, achievement_id),
        )
        await self._db.commit()
        # aiosqlite Cursor.rowcount is supported
        return bool(getattr(cur, "rowcount", 0))

