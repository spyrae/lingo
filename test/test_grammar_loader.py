from pathlib import Path

from lingo.content.grammar_loader import GrammarLessonLoader


def test_list_metas_reads_lessons() -> None:
    lessons_dir = Path(__file__).resolve().parents[1] / "data" / "grammar"
    loader = GrammarLessonLoader(lessons_dir)
    metas = loader.list_metas()

    assert len(metas) >= 5
    assert metas[0].id == "grammar-01"
    assert metas[0].order == 1


def test_get_available_respects_prerequisites() -> None:
    lessons_dir = Path(__file__).resolve().parents[1] / "data" / "grammar"
    loader = GrammarLessonLoader(lessons_dir)

    available_0 = loader.get_available(completed_ids=[])
    assert any(m.id == "grammar-01" for m in available_0)
    assert all(m.id != "grammar-02" for m in available_0)  # prereq grammar-01

    available_1 = loader.get_available(completed_ids=["grammar-01"])
    assert any(m.id == "grammar-02" for m in available_1)

