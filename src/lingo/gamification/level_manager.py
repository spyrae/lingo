"""Automatic level progression based on XP thresholds."""

from __future__ import annotations

from lingo.memory.database import Database


# XP thresholds for level progression
LEVEL_THRESHOLDS: list[tuple[str, int]] = [
    ("zero", 0),
    ("beginner", 100),
    ("elementary", 500),
    ("intermediate", 1500),
    ("advanced", 4000),
]

LEVEL_NAMES: dict[str, str] = {
    "zero": "🌱 Pemula (Ноль)",
    "beginner": "📚 Pemula (Начинающий)",
    "elementary": "📖 Dasar (Элементарный)",
    "intermediate": "💪 Menengah (Средний)",
    "advanced": "🎓 Mahir (Продвинутый)",
}


def compute_level(total_xp: int) -> str:
    """Determine level based on total XP."""
    level = "zero"
    for name, threshold in LEVEL_THRESHOLDS:
        if total_xp >= threshold:
            level = name
    return level


async def check_level_up(db: Database, telegram_id: int) -> str | None:
    """Check if user should level up. Returns new level name if leveled up, None otherwise."""
    row = await db.fetchone(
        "SELECT level, total_xp FROM users WHERE telegram_id = ?",
        (telegram_id,),
    )
    if not row:
        return None

    current_level = row["level"]
    new_level = compute_level(row["total_xp"])

    if new_level == current_level:
        return None

    # Check if new level is actually higher
    current_idx = next(
        (i for i, (name, _) in enumerate(LEVEL_THRESHOLDS) if name == current_level), 0
    )
    new_idx = next(
        (i for i, (name, _) in enumerate(LEVEL_THRESHOLDS) if name == new_level), 0
    )
    if new_idx <= current_idx:
        return None

    await db.execute(
        "UPDATE users SET level = ?, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
        (new_level, telegram_id),
    )
    await db.commit()
    return new_level


def format_level_up(new_level: str) -> str:
    label = LEVEL_NAMES.get(new_level, new_level)
    return (
        "🎉 <b>Новый уровень!</b>\n\n"
        f"Ты достиг уровня: {label}\n\n"
        "Так держать! 💪"
    )
