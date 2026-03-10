from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from lingo.memory.database import Database


@dataclass(frozen=True)
class UserLesson:
    user_id: int
    lesson_id: str
    status: str
    score: int | None
    attempts: int
    started_at: str | None
    completed_at: str | None


class LessonProgressRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def list_completed_lesson_ids(self, user_id: int) -> list[str]:
        rows = await self._db.fetchall(
            "SELECT lesson_id FROM user_lessons WHERE user_id = ? AND status = 'completed'",
            (user_id,),
        )
        return [str(r["lesson_id"]) for r in rows]

    async def start_lesson(self, user_id: int, lesson_id: str) -> None:
        now = datetime.utcnow().isoformat(timespec="seconds")
        await self._db.execute(
            """
            INSERT INTO user_lessons (user_id, lesson_id, status, attempts, started_at)
            VALUES (?, ?, 'in_progress', 1, ?)
            ON CONFLICT(user_id, lesson_id) DO UPDATE SET
              status = 'in_progress',
              attempts = user_lessons.attempts + 1,
              started_at = COALESCE(user_lessons.started_at, excluded.started_at)
            """,
            (user_id, lesson_id, now),
        )
        await self._db.commit()

    async def complete_lesson(self, user_id: int, lesson_id: str, score: int) -> None:
        now = datetime.utcnow().isoformat(timespec="seconds")
        await self._db.execute(
            """
            UPDATE user_lessons SET
              status = 'completed',
              score = ?,
              completed_at = ?,
              updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND lesson_id = ?
            """,
            (score, now, user_id, lesson_id),
        )
        await self._db.commit()

