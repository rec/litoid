from fractions import Fraction
from litoid.util import smooth
import pytest

# DT = Fraction(1, 10)
DT = 1

def make(*items):
    return [(i * DT, x) for i, x in enumerate(items)]


UNCHANGED = [
    make(),
    make(127),
    make(127, 128),
    make(127, 128, 128, 127, 126),
]



@pytest.mark.parametrize('sequence', UNCHANGED)
def test_unchanged(sequence):
    assert sequence == list(smooth(sequence))


def test_simple():
    actual = list(smooth(make(0, 1, 3)))
    expected = [(0, 0), (1, 1), (1.5, 2), (2, 3)]
    assert actual == expected


def test_smooth():
    actual = list(smooth(make(0, 1, 3, 7, 15, 16, 8, 4, 2, 0)))
    expected = [
        (0, 0), (1, 1), (1.5, 2), (2, 3), (2.25, 4), (2.5, 5), (2.75, 6),
        (3, 7), (3.125, 8), (3.25, 9), (3.375, 10), (3.5, 11),
        (3.625, 12), (3.75, 13), (3.875, 14),
        (4, 15), (5, 16), (5.125, 15), (5.25, 14), (5.375, 13), (5.5, 12),
        (5.625, 11), (5.75, 10), (5.875, 9),
        (6, 8), (6.25, 7), (6.5, 6), (6.75, 5), (7, 4), (7.5, 3),
        (8, 2), (8.5, 1), (9, 0)
    ]
    assert actual == expected
