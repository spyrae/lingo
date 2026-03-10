from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AchievementDefinition:
    id: str
    icon: str
    name: str
    name_id: str
    description: str
    xp_reward: int
    hidden: bool = False


ACHIEVEMENTS: list[AchievementDefinition] = [
    # Vocabulary (mastered words)
    AchievementDefinition(
        id="vocab_10",
        icon="📚",
        name="Первые шаги",
        name_id="Langkah Pertama",
        description="Выучи 10 слов",
        xp_reward=50,
    ),
    AchievementDefinition(
        id="vocab_50",
        icon="📖",
        name="Растущий словарь",
        name_id="Kamus Berkembang",
        description="Выучи 50 слов",
        xp_reward=100,
    ),
    AchievementDefinition(
        id="vocab_100",
        icon="💯",
        name="Сотня!",
        name_id="Seratus!",
        description="Выучи 100 слов",
        xp_reward=200,
    ),
    # Streak (longest streak)
    AchievementDefinition(
        id="streak_7",
        icon="🔥",
        name="Неделя!",
        name_id="Satu Minggu!",
        description="7 дней подряд",
        xp_reward=100,
    ),
    AchievementDefinition(
        id="streak_14",
        icon="🔥🔥",
        name="Две недели",
        name_id="Dua Minggu",
        description="14 дней подряд",
        xp_reward=200,
    ),
    AchievementDefinition(
        id="streak_30",
        icon="⭐",
        name="Месяц!",
        name_id="Satu Bulan!",
        description="30 дней подряд",
        xp_reward=500,
    ),
    # Lessons
    AchievementDefinition(
        id="lesson_first",
        icon="📝",
        name="Первый урок",
        name_id="Pelajaran Pertama",
        description="Пройди первый урок грамматики",
        xp_reward=30,
    ),
    AchievementDefinition(
        id="lesson_5",
        icon="✏️",
        name="Прилежный ученик",
        name_id="Siswa Rajin",
        description="Пройди 5 уроков",
        xp_reward=100,
    ),
    # Practice
    AchievementDefinition(
        id="practice_first",
        icon="💬",
        name="Первый диалог",
        name_id="Dialog Pertama",
        description="Начни первую практику с AI",
        xp_reward=30,
    ),
]


ACHIEVEMENTS_BY_ID: dict[str, AchievementDefinition] = {a.id: a for a in ACHIEVEMENTS}

