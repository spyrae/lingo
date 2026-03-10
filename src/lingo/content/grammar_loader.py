from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LessonMeta:
    id: str
    title: str
    title_id: str
    order: int
    difficulty: int
    estimated_time: int
    prerequisites: list[str]
    xp_reward: int


class LessonValidationError(ValueError):
    pass


class GrammarLessonLoader:
    def __init__(self, lessons_dir: Path) -> None:
        self._dir = lessons_dir
        self._cache: dict[str, dict[str, Any]] = {}

    def load_lesson(self, lesson_id: str) -> dict[str, Any] | None:
        if lesson_id in self._cache:
            return self._cache[lesson_id]

        path = self._dir / f"{lesson_id}.json"
        if not path.exists():
            return None

        lesson = json.loads(path.read_text(encoding="utf-8"))
        self._validate_lesson(lesson)
        self._cache[lesson_id] = lesson
        return lesson

    def list_metas(self) -> list[LessonMeta]:
        metas: list[LessonMeta] = []
        for path in sorted(self._dir.glob("grammar-*.json")):
            lesson = json.loads(path.read_text(encoding="utf-8"))
            self._validate_lesson(lesson)
            metas.append(
                LessonMeta(
                    id=str(lesson["id"]),
                    title=str(lesson["title"]),
                    title_id=str(lesson["title_id"]),
                    order=int(lesson["order"]),
                    difficulty=int(lesson["difficulty"]),
                    estimated_time=int(lesson["estimated_time"]),
                    prerequisites=list(lesson.get("prerequisites", [])),
                    xp_reward=int(lesson["xp_reward"]),
                )
            )
        metas.sort(key=lambda m: m.order)
        return metas

    def get_available(self, completed_ids: list[str]) -> list[LessonMeta]:
        completed = set(completed_ids)
        available: list[LessonMeta] = []
        for meta in self.list_metas():
            if meta.id in completed:
                continue
            if all(p in completed for p in meta.prerequisites):
                available.append(meta)
        return available

    def _validate_lesson(self, lesson: dict[str, Any]) -> None:
        required = [
            "id",
            "title",
            "title_id",
            "order",
            "difficulty",
            "estimated_time",
            "prerequisites",
            "theory",
            "examples",
            "exercises",
            "xp_reward",
        ]
        for key in required:
            if key not in lesson:
                raise LessonValidationError(f"Missing field: {key}")

        theory = lesson["theory"]
        if not isinstance(theory, dict) or "text" not in theory or "key_points" not in theory:
            raise LessonValidationError("Invalid theory block")

        if not isinstance(lesson["examples"], list) or len(lesson["examples"]) < 1:
            raise LessonValidationError("Lesson must have at least 1 example")
        if not isinstance(lesson["exercises"], list) or len(lesson["exercises"]) < 1:
            raise LessonValidationError("Lesson must have at least 1 exercise")

