from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import IntEnum


class Quality(IntEnum):
    BLACKOUT = 0
    INCORRECT = 1
    INCORRECT_EASY = 2
    CORRECT_HARD = 3
    CORRECT = 4
    PERFECT = 5


@dataclass(frozen=True)
class SRSCard:
    word_id: int
    ease_factor: float = 2.5
    interval_days: int = 0
    repetitions: int = 0
    next_review: date | None = None

    @property
    def is_new(self) -> bool:
        return self.repetitions == 0 and self.interval_days == 0


@dataclass(frozen=True)
class ReviewResult:
    new_ease_factor: float
    new_interval_days: int
    new_repetitions: int
    next_review: date
    xp_earned: int


class SRSEngine:
    XP_REWARDS: dict[Quality, int] = {
        Quality.BLACKOUT: 0,
        Quality.INCORRECT: 1,
        Quality.INCORRECT_EASY: 2,
        Quality.CORRECT_HARD: 5,
        Quality.CORRECT: 8,
        Quality.PERFECT: 10,
    }

    def calculate_review(self, card: SRSCard, quality: Quality) -> ReviewResult:
        q = int(quality)
        if q < 0 or q > 5:
            raise ValueError("quality must be in range 0..5")

        # SM-2 ease factor update
        new_ef = card.ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        new_ef = max(1.3, new_ef)

        if q < 3:
            new_reps = 0
            new_interval = 1
        else:
            new_reps = card.repetitions + 1
            if new_reps == 1:
                new_interval = 1
            elif new_reps == 2:
                new_interval = 6
            else:
                base = max(card.interval_days, 1)
                new_interval = max(1, round(base * new_ef))

        next_review = date.today() + timedelta(days=new_interval)
        return ReviewResult(
            new_ease_factor=round(new_ef, 2),
            new_interval_days=new_interval,
            new_repetitions=new_reps,
            next_review=next_review,
            xp_earned=int(self.XP_REWARDS.get(quality, 0)),
        )

    def get_card_status(self, ease_factor: float, repetitions: int) -> str:
        if repetitions == 0:
            return "new"
        if repetitions < 3:
            return "learning"
        if ease_factor >= 2.5 and repetitions >= 5:
            return "mastered"
        return "review"


srs_engine = SRSEngine()

