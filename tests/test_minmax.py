import pytest

from rollbot.interpreter.calculator import minmax


@pytest.mark.parametrize(
    "roll, expected",
    [
        ("1", (1, 1)),
        ("d20", (1, 20)),
        ("d20+1", (2, 21)),
        ("d20-1", (0, 19)),
        ("d20+1d4", (2, 24)),
        ("d20-1d4", (-3, 19)),
        ("1*1", (1, 1)),
        ("2*3", (6, 6)),
        ("1+2*1d4", (3, 9)),
        ("1-2*1d4", (-7, -1)),
        ("1+d4/2", (1, 3)),
        ("1-d4/2", (-1, 1)),
        ("max(d20+1, d20)", (2, 21)),
        ("min(d20+1, d20)", (1, 20)),
    ],
)
def test_minmax(roll, expected):
    assert minmax(roll) == expected
