from typing import Tuple

import pytest

from main.models import Vote
from plan.templatetags.filters import humanize_score, humanize_score_index


@pytest.mark.parametrize(
    'score,choice',
    (
            (0, Vote.SCORE_CHOICES[0]),
            (25, Vote.SCORE_CHOICES[1]),
            (100, Vote.SCORE_CHOICES[4]),
            (101, Vote.SCORE_CHOICES[2]),  # Mid
            (200, Vote.SCORE_CHOICES[2]),  # Mid
            ('foo', Vote.SCORE_CHOICES[2]),  # Mid
    )
)
def test_humanize_score(score: int, choice: Tuple[int, str]):
    assert humanize_score(score) == choice[1]


@pytest.mark.parametrize(
    'index,choice',
    (
            (0, Vote.SCORE_CHOICES[0]),
            (1, Vote.SCORE_CHOICES[1]),
            (-1, Vote.SCORE_CHOICES[2]),
            (4, Vote.SCORE_CHOICES[4]),  # Mid
            (5, Vote.SCORE_CHOICES[2]),  # Mid
            ('foo', Vote.SCORE_CHOICES[2]),  # Mid
    )
)
def test_humanize_score_index(index: int, choice: Tuple[int, str]):
    assert humanize_score_index(index) == choice[1]
