from __future__ import annotations

from dataclasses import dataclass

from lingo.gamification.achievements_definitions import (
    ACHIEVEMENTS_BY_ID,
    AchievementDefinition,
)
from lingo.memory.database import Database
from lingo.memory.repositories.achievements_repository import AchievementsRepository
from lingo.memory.repositories.user_repository import UserRepository


@dataclass(frozen=True)
class UserAchievementStats:
    words_mastered: int
    lessons_completed: int
    longest_streak: int


class AchievementManager:
    def __init__(self, db: Database) -> None:
        self._db = db
        self._ach_repo = AchievementsRepository(db)
        self._user_repo = UserRepository(db)

    async def compute_stats(self, user_id: int) -> UserAchievementStats:
        row = await self._db.fetchone(
            "SELECT longest_streak FROM users WHERE id = ?",
            (user_id,),
        )
        longest = int(row["longest_streak"]) if row else 0

        row = await self._db.fetchone(
            "SELECT COUNT(*) as c FROM user_words WHERE user_id = ? AND status = 'mastered'",
            (user_id,),
        )
        mastered = int(row["c"]) if row else 0

        row = await self._db.fetchone(
            "SELECT COUNT(*) as c FROM user_lessons WHERE user_id = ? AND status = 'completed'",
            (user_id,),
        )
        lessons_completed = int(row["c"]) if row else 0

        return UserAchievementStats(
            words_mastered=mastered,
            lessons_completed=lessons_completed,
            longest_streak=longest,
        )

    async def check_and_unlock(
        self, *, user_id: int, telegram_id: int, event: str | None = None
    ) -> list[AchievementDefinition]:
        """
        Checks achievement conditions and unlocks newly earned ones.
        Returns list of newly unlocked definitions.
        """
        unlocked_ids = await self._ach_repo.list_unlocked_ids(user_id)
        stats = await self.compute_stats(user_id)

        newly_unlocked: list[AchievementDefinition] = []

        def try_unlock(achievement_id: str) -> None:
            if achievement_id in unlocked_ids:
                return
            definition = ACHIEVEMENTS_BY_ID.get(achievement_id)
            if definition is None:
                return
            newly_unlocked.append(definition)

        # Vocabulary thresholds
        if stats.words_mastered >= 10:
            try_unlock("vocab_10")
        if stats.words_mastered >= 50:
            try_unlock("vocab_50")
        if stats.words_mastered >= 100:
            try_unlock("vocab_100")
        if stats.words_mastered >= 250:
            try_unlock("vocab_250")
        if stats.words_mastered >= 500:
            try_unlock("vocab_500")

        # Streak thresholds
        if stats.longest_streak >= 7:
            try_unlock("streak_7")
        if stats.longest_streak >= 14:
            try_unlock("streak_14")
        if stats.longest_streak >= 30:
            try_unlock("streak_30")

        # Lessons thresholds
        if stats.lessons_completed >= 1:
            try_unlock("lesson_first")
        if stats.lessons_completed >= 5:
            try_unlock("lesson_5")
        if stats.lessons_completed >= 10:
            try_unlock("lesson_10")
        if stats.lessons_completed >= 20:
            try_unlock("lesson_20")

        # Event-driven
        if event == "practice_started":
            try_unlock("practice_first")
        if event == "quiz_completed":
            try_unlock("quiz_first")

        # Persist + XP rewards
        result: list[AchievementDefinition] = []
        for definition in newly_unlocked:
            inserted = await self._ach_repo.unlock(user_id, definition.id)
            if not inserted:
                continue
            await self._user_repo.add_xp(telegram_id, definition.xp_reward)
            result.append(definition)

        return result


def format_achievement_unlocked(a: AchievementDefinition) -> str:
    return (
        "🏅 <b>Достижение разблокировано!</b>\n\n"
        f"{a.icon} <b>{a.name}</b>\n"
        f"<i>{a.name_id}</i>\n\n"
        f"{a.description}\n\n"
        f"+{a.xp_reward} XP"
    )

