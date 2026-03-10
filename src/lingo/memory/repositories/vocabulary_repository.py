from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lingo.memory.database import Database


@dataclass(frozen=True)
class VocabularyWord:
    id: int
    indonesian: str
    russian: str
    category: str
    difficulty: int
    part_of_speech: str | None
    examples_json: str | None
    notes: str | None


class VocabularyRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def get_word_by_id(self, word_id: int) -> VocabularyWord | None:
        row = await self._db.fetchone("SELECT * FROM vocabulary WHERE id = ?", (word_id,))
        if row is None:
            return None
        return VocabularyWord(
            id=row["id"],
            indonesian=row["indonesian"],
            russian=row["russian"],
            category=row["category"],
            difficulty=row["difficulty"],
            part_of_speech=row["part_of_speech"],
            examples_json=row["examples_json"],
            notes=row["notes"],
        )

    async def get_random_new_word_id(
        self, *, user_id: int, category: str | None = None
    ) -> int | None:
        if category:
            row = await self._db.fetchone(
                """
                SELECT v.id
                FROM vocabulary v
                LEFT JOIN user_words uw
                  ON uw.user_id = ? AND uw.word_id = v.id
                WHERE uw.id IS NULL
                  AND v.category = ?
                ORDER BY v.difficulty ASC, RANDOM()
                LIMIT 1
                """,
                (user_id, category),
            )
        else:
            row = await self._db.fetchone(
                """
                SELECT v.id
                FROM vocabulary v
                LEFT JOIN user_words uw
                  ON uw.user_id = ? AND uw.word_id = v.id
                WHERE uw.id IS NULL
                ORDER BY v.difficulty ASC, RANDOM()
                LIMIT 1
                """,
                (user_id,),
            )
        return int(row["id"]) if row else None

    async def insert_words(self, words: list[dict[str, Any]]) -> int:
        """
        Insert vocabulary entries.

        Expected keys: indonesian, russian, category. Optional: difficulty, part_of_speech, examples_json, notes.
        """
        inserted = 0
        for w in words:
            cursor = await self._db.execute(
                """
                INSERT OR IGNORE INTO vocabulary
                  (indonesian, russian, category, difficulty, part_of_speech, examples_json, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    w["indonesian"],
                    w["russian"],
                    w["category"],
                    int(w.get("difficulty", 1)),
                    w.get("part_of_speech"),
                    w.get("examples_json"),
                    w.get("notes"),
                ),
            )
            if getattr(cursor, "rowcount", 0) > 0:
                inserted += 1
        await self._db.commit()
        return inserted

