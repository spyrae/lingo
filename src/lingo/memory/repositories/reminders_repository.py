from __future__ import annotations

from dataclasses import dataclass

from lingo.memory.database import Database


@dataclass(frozen=True)
class ReminderRecipient:
    user_id: int
    telegram_id: int
    reminder_time: str


class RemindersRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def list_due_recipients(self, *, today_iso: str, hhmm: str) -> list[ReminderRecipient]:
        rows = await self._db.fetchall(
            """
            SELECT u.id AS user_id, u.telegram_id AS telegram_id, u.reminder_time AS reminder_time
            FROM users u
            LEFT JOIN reminders_sent rs
              ON rs.user_id = u.id AND rs.date = ?
            WHERE u.reminder_enabled = 1
              AND u.reminder_time = ?
              AND rs.id IS NULL
            """,
            (today_iso, hhmm),
        )
        return [
            ReminderRecipient(
                user_id=int(r["user_id"]),
                telegram_id=int(r["telegram_id"]),
                reminder_time=str(r["reminder_time"]),
            )
            for r in rows
        ]

    async def mark_sent(self, *, user_id: int, today_iso: str, hhmm: str) -> None:
        await self._db.execute(
            "INSERT OR IGNORE INTO reminders_sent (user_id, date, reminder_time) VALUES (?, ?, ?)",
            (user_id, today_iso, hhmm),
        )
        await self._db.commit()

