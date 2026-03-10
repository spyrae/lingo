from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from lingo.memory.database import Database


@dataclass(frozen=True)
class User:
    id: int
    telegram_id: int
    level: str
    total_xp: int
    current_streak: int
    longest_streak: int
    last_activity_date: str | None
    daily_goal: int
    reminder_enabled: int
    reminder_time: str


class UserRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        row = await self._db.fetchone(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,),
        )
        if row is None:
            return None
        return User(
            id=row["id"],
            telegram_id=row["telegram_id"],
            level=row["level"],
            total_xp=row["total_xp"],
            current_streak=row["current_streak"],
            longest_streak=row["longest_streak"],
            last_activity_date=row["last_activity_date"],
            daily_goal=row["daily_goal"],
            reminder_enabled=row["reminder_enabled"],
            reminder_time=row["reminder_time"],
        )

    async def create(self, telegram_id: int, level: str) -> User:
        today = date.today().isoformat()
        await self._db.execute(
            "INSERT INTO users (telegram_id, level, last_activity_date) VALUES (?, ?, ?)",
            (telegram_id, level, today),
        )
        await self._db.commit()
        user = await self.get_by_telegram_id(telegram_id)
        if user is None:
            raise RuntimeError("Failed to create user")
        return user

    async def get_or_create(self, telegram_id: int, default_level: str) -> tuple[User, bool]:
        existing = await self.get_by_telegram_id(telegram_id)
        if existing is not None:
            return existing, False
        created = await self.create(telegram_id=telegram_id, level=default_level)
        return created, True

    async def update_daily_goal(self, telegram_id: int, goal: int) -> None:
        await self._db.execute(
            "UPDATE users SET daily_goal = ?, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
            (goal, telegram_id),
        )
        await self._db.commit()

    async def set_reminder_enabled(self, telegram_id: int, enabled: bool) -> None:
        await self._db.execute(
            "UPDATE users SET reminder_enabled = ?, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
            (1 if enabled else 0, telegram_id),
        )
        await self._db.commit()

    async def set_reminder_time(self, telegram_id: int, reminder_time: str) -> None:
        await self._db.execute(
            "UPDATE users SET reminder_time = ?, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
            (reminder_time, telegram_id),
        )
        await self._db.commit()

    async def add_xp(self, telegram_id: int, xp: int) -> None:
        if xp <= 0:
            return
        await self._db.execute(
            "UPDATE users SET total_xp = total_xp + ?, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
            (xp, telegram_id),
        )
        await self._db.commit()

    async def update_activity(self, telegram_id: int) -> None:
        """
        Update last_activity_date and streak counters.

        Rules:
        - first activity ever -> streak=1
        - activity same day -> no change
        - activity next day -> streak++
        - otherwise -> streak=1
        """
        user = await self.get_by_telegram_id(telegram_id)
        if user is None:
            return

        today = date.today()
        last = date.fromisoformat(user.last_activity_date) if user.last_activity_date else None

        if last == today:
            return

        if last is None:
            new_streak = 1
        else:
            diff = (today - last).days
            new_streak = user.current_streak + 1 if diff == 1 else 1

        longest = max(user.longest_streak, new_streak)
        await self._db.execute(
            """
            UPDATE users SET
              current_streak = ?,
              longest_streak = ?,
              last_activity_date = ?,
              updated_at = CURRENT_TIMESTAMP
            WHERE telegram_id = ?
            """,
            (new_streak, longest, today.isoformat(), telegram_id),
        )
        await self._db.commit()

