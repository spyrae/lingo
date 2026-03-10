from datetime import date, timedelta

import pytest

from lingo.services.srs import Quality, SRSCard, srs_engine


def test_new_card_first_review_correct() -> None:
    card = SRSCard(word_id=1)
    result = srs_engine.calculate_review(card, Quality.CORRECT)

    assert result.new_repetitions == 1
    assert result.new_interval_days == 1
    assert result.next_review == date.today() + timedelta(days=1)


def test_second_review_correct() -> None:
    card = SRSCard(word_id=1, repetitions=1, interval_days=1, ease_factor=2.5)
    result = srs_engine.calculate_review(card, Quality.CORRECT)

    assert result.new_repetitions == 2
    assert result.new_interval_days == 6


def test_failed_review_resets() -> None:
    card = SRSCard(word_id=1, repetitions=3, interval_days=15, ease_factor=2.5)
    result = srs_engine.calculate_review(card, Quality.BLACKOUT)

    assert result.new_repetitions == 0
    assert result.new_interval_days == 1


def test_ease_factor_minimum() -> None:
    card = SRSCard(word_id=1, repetitions=0, interval_days=0, ease_factor=1.3)
    result = srs_engine.calculate_review(card, Quality.INCORRECT)
    assert result.new_ease_factor >= 1.3


def test_quality_out_of_range_raises() -> None:
    card = SRSCard(word_id=1)
    with pytest.raises(ValueError):
        # type: ignore[arg-type]
        srs_engine.calculate_review(card, 6)

