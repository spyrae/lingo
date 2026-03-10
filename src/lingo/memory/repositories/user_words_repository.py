from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from lingo.memory.database import Database
from lingo.services.srs import Quality, SRSCard, ReviewResult, srs_engine


@dataclass(frozen=True)
class UserWordCard:
    user_id: int
    word_id: int
    indonesian: str
    russian: str
    category: str
    difficulty: int
    ease_factor: float
    interval_days: int
    repetitions: int
    next_review: str | None
    status: str


class UserWordsRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def ensure_user_word(self, user_id: int, word_id: int) -> None:
        today = date.today().isoformat()
        await self._db.execute(
            "INSERT OR IGNORE INTO user_words (user_id, word_id, next_review, status) VALUES (?, ?, ?, 'new')",
            (user_id, word_id, today),
        )
        await self._db.commit()

    async def get_due_cards(self, user_id: int, limit: int) -> list[UserWordCard]:
        today = date.today().isoformat()
        rows = await self._db.fetchall(
            """
            SELECT
              uw.user_id,
              uw.word_id,
              v.indonesian,
              v.russian,
              v.category,
              v.difficulty,
              uw.ease_factor,
              uw.interval_days,
              uw.repetitions,
              uw.next_review,
              uw.status
            FROM user_words uw
            JOIN vocabulary v ON v.id = uw.word_id
            WHERE uw.user_id = ?
              AND (uw.next_review IS NULL OR uw.next_review <= ?)
              AND uw.status != 'mastered'
            ORDER BY uw.next_review ASC NULLS FIRST, uw.status ASC, v.difficulty ASC
            LIMIT ?
            """,
            (user_id, today, limit),
        )
        return [
            UserWordCard(
                user_id=r["user_id"],
                word_id=r["word_id"],
                indonesian=r["indonesian"],
                russian=r["russian"],
                category=r["category"],
                difficulty=r["difficulty"],
                ease_factor=r["ease_factor"],
                interval_days=r["interval_days"],
                repetitions=r["repetitions"],
                next_review=r["next_review"],
                status=r["status"],
            )
            for r in rows
        ]

    async def record_review(self, user_id: int, word_id: int, quality: Quality) -> ReviewResult:
        row = await self._db.fetchone(
            """
            SELECT ease_factor, interval_days, repetitions, next_review
            FROM user_words
            WHERE user_id = ? AND word_id = ?
            """,
            (user_id, word_id),
        )

        if row is None:
            await self.ensure_user_word(user_id, word_id)
            row = await self._db.fetchone(
                """
                SELECT ease_factor, interval_days, repetitions, next_review
                FROM user_words
                WHERE user_id = ? AND word_id = ?
                """,
                (user_id, word_id),
            )
            if row is None:
                raise RuntimeError("Failed to initialize user_words row")

        next_review_date = None
        if row["next_review"]:
            next_review_date = date.fromisoformat(row["next_review"])

        card = SRSCard(
            word_id=word_id,
            ease_factor=row["ease_factor"],
            interval_days=row["interval_days"],
            repetitions=row["repetitions"],
            next_review=next_review_date,
        )

        result = srs_engine.calculate_review(card, quality)
        status = srs_engine.get_card_status(
            ease_factor=result.new_ease_factor,
            repetitions=result.new_repetitions,
        )

        is_correct = quality >= Quality.CORRECT_HARD
        last_result = "correct" if is_correct else "wrong"

        await self._db.execute(
            """
            UPDATE user_words SET
              ease_factor = ?,
              interval_days = ?,
              repetitions = ?,
              next_review = ?,
              status = ?,
              times_seen = times_seen + 1,
              times_correct = times_correct + ?,
              times_wrong = times_wrong + ?,
              last_seen = CURRENT_TIMESTAMP,
              last_result = ?,
              updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND word_id = ?
            """,
            (
                result.new_ease_factor,
                result.new_interval_days,
                result.new_repetitions,
                result.next_review.isoformat(),
                status,
                1 if is_correct else 0,
                0 if is_correct else 1,
                last_result,
                user_id,
                word_id,
            ),
        )
        await self._db.commit()
        return result

