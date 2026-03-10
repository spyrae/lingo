from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ScenarioMeta:
    id: str
    title: str
    title_id: str
    order: int
    difficulty: int
    estimated_time: int
    tags: list[str]


class ScenarioValidationError(ValueError):
    pass


class PracticeScenarioLoader:
    def __init__(self, scenarios_dir: Path) -> None:
        self._dir = scenarios_dir
        self._cache: dict[str, dict[str, Any]] = {}

    def load(self, scenario_id: str) -> dict[str, Any] | None:
        if scenario_id in self._cache:
            return self._cache[scenario_id]

        path = self._dir / f"{scenario_id}.json"
        if not path.exists():
            return None

        data = json.loads(path.read_text(encoding="utf-8"))
        self._validate(data)
        self._cache[scenario_id] = data
        return data

    def list_metas(self) -> list[ScenarioMeta]:
        metas: list[ScenarioMeta] = []
        for path in sorted(self._dir.glob("scenario-*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            self._validate(data)
            metas.append(
                ScenarioMeta(
                    id=str(data["id"]),
                    title=str(data["title"]),
                    title_id=str(data["title_id"]),
                    order=int(data["order"]),
                    difficulty=int(data["difficulty"]),
                    estimated_time=int(data["estimated_time"]),
                    tags=list(data.get("tags", [])),
                )
            )
        metas.sort(key=lambda m: m.order)
        return metas

    def _validate(self, data: dict[str, Any]) -> None:
        required = [
            "id",
            "title",
            "title_id",
            "order",
            "difficulty",
            "estimated_time",
            "tags",
            "setting",
            "roles",
            "goals",
            "must_use",
            "sample_dialog",
        ]
        for k in required:
            if k not in data:
                raise ScenarioValidationError(f"Missing field: {k}")

        difficulty = int(data["difficulty"])
        if difficulty < 1 or difficulty > 3:
            raise ScenarioValidationError("difficulty must be 1..3")

        sample = data["sample_dialog"]
        if not isinstance(sample, list) or len(sample) < 4:
            raise ScenarioValidationError("sample_dialog must have at least 4 turns")
        for turn in sample:
            if not isinstance(turn, dict):
                raise ScenarioValidationError("sample_dialog turns must be objects")
            if turn.get("role") not in {"student", "tutor"}:
                raise ScenarioValidationError("sample_dialog.role must be 'student' or 'tutor'")
            if not turn.get("text"):
                raise ScenarioValidationError("sample_dialog.text is required")

