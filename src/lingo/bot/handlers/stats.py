from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from lingo.memory.database import Database
from lingo.memory.repositories.user_repository import UserRepository

router = Router(name="stats")


LEVEL_NAMES: dict[str, str] = {
    "zero": "🌱 Pemula (Ноль)",
    "beginner": "📚 Pemula (Начинающий)",
    "elementary": "📖 Dasar (Элементарный)",
    "intermediate": "💪 Menengah (Средний)",
}


async def _build_stats_text(db: Database, telegram_id: int) -> str | None:
    user = await UserRepository(db).get_by_telegram_id(telegram_id)
    if user is None:
        return None

    # Words stats
    row = await db.fetchone(
        """
        SELECT
          COUNT(*) as total,
          SUM(CASE WHEN status = 'mastered' THEN 1 ELSE 0 END) as mastered,
          SUM(CASE WHEN status = 'learning' THEN 1 ELSE 0 END) as learning,
          SUM(CASE WHEN status = 'review' THEN 1 ELSE 0 END) as review,
          SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new_words
        FROM user_words
        WHERE user_id = ?
        """,
        (user.id,),
    )
    total_words = int(row["total"]) if row else 0
    mastered = int(row["mastered"]) if row else 0
    learning = int(row["learning"]) if row else 0
    in_review = int(row["review"]) if row else 0
    new_words = int(row["new_words"]) if row else 0

    # Lessons stats
    row = await db.fetchone(
        "SELECT COUNT(*) as c FROM user_lessons WHERE user_id = ? AND status = 'completed'",
        (user.id,),
    )
    lessons_done = int(row["c"]) if row else 0

    # Achievements
    row = await db.fetchone(
        "SELECT COUNT(*) as c FROM achievements WHERE user_id = ?",
        (user.id,),
    )
    achievements = int(row["c"]) if row else 0

    level_label = LEVEL_NAMES.get(user.level, user.level)

    lines = [
        "📊 <b>Твой прогресс</b>\n",
        f"Уровень: {level_label}",
        f"XP: <b>{user.total_xp}</b>",
        f"Streak: <b>{user.current_streak}</b> дн. (макс: {user.longest_streak})",
        "",
        "📚 <b>Слова</b>",
        f"  Изучено: {total_words}",
    ]
    if total_words > 0:
        lines.append(f"  ✅ Выучены: {mastered}")
        lines.append(f"  📝 Учу: {learning}")
        lines.append(f"  🔄 На повторе: {in_review}")
        lines.append(f"  🆕 Новые: {new_words}")

    lines.append("")
    lines.append(f"📖 Уроков пройдено: <b>{lessons_done}</b>")
    lines.append(f"🏅 Достижений: <b>{achievements}</b>")
    lines.append(f"\n🎯 Цель: <b>{user.daily_goal}</b> новых слов/день")

    return "\n".join(lines)


@router.message(Command("stats"))
@router.message(F.text == "📊 Прогресс")
async def show_stats(message: Message, db: Database) -> None:
    if message.from_user is None:
        return

    text = await _build_stats_text(db, message.from_user.id)
    if text is None:
        await message.answer("Сначала нажми /start и пройди онбординг.")
        return

    await message.answer(text)
