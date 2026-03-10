from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lingo.memory.categories import WORD_CATEGORIES


@dataclass(frozen=True)
class VocabularyEntry:
    indonesian: str
    russian: str
    category: str
    difficulty: int
    part_of_speech: str | None
    english_gloss: str | None


class VocabularyValidationError(ValueError):
    pass


class VocabularyLoader:
    """
    Loads a TSV vocabulary seed file into normalized dicts suitable for VocabularyRepository.insert_words().

    TSV columns:
      indonesian, russian, category, difficulty, part_of_speech, english_gloss
    """

    def __init__(self, path: Path) -> None:
        self._path = path

    def load_entries(self) -> list[VocabularyEntry]:
        if not self._path.exists():
            raise FileNotFoundError(str(self._path))

        with self._path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            entries: list[VocabularyEntry] = []
            for i, row in enumerate(reader, start=2):
                entry = self._parse_row(row, line=i)
                entries.append(entry)
        return entries

    def to_insert_dicts(self) -> list[dict[str, Any]]:
        words: list[dict[str, Any]] = []
        for e in self.load_entries():
            notes = None
            if e.english_gloss:
                notes = f"en: {e.english_gloss}"
            words.append(
                {
                    "indonesian": e.indonesian,
                    "russian": e.russian,
                    "category": e.category,
                    "difficulty": int(e.difficulty),
                    "part_of_speech": e.part_of_speech,
                    "examples_json": None,
                    "notes": notes,
                }
            )
        return words

    def _parse_row(self, row: dict[str, str], *, line: int) -> VocabularyEntry:
        required = ["indonesian", "russian", "category"]
        for k in required:
            if not row.get(k):
                raise VocabularyValidationError(f"Missing {k} at line {line}")

        category = str(row["category"]).strip()
        if category not in WORD_CATEGORIES:
            raise VocabularyValidationError(f"Unknown category '{category}' at line {line}")

        difficulty_raw = (row.get("difficulty") or "1").strip()
        try:
            difficulty = int(difficulty_raw)
        except ValueError as e:
            raise VocabularyValidationError(f"Invalid difficulty '{difficulty_raw}' at line {line}") from e
        if difficulty < 1 or difficulty > 3:
            raise VocabularyValidationError(f"Difficulty out of range at line {line}: {difficulty}")

        part_of_speech = (row.get("part_of_speech") or "").strip() or None
        english_gloss = (row.get("english_gloss") or "").strip() or None

        return VocabularyEntry(
            indonesian=str(row["indonesian"]).strip(),
            russian=str(row["russian"]).strip(),
            category=category,
            difficulty=difficulty,
            part_of_speech=part_of_speech,
            english_gloss=english_gloss,
        )

