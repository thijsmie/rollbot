import re
import pytest
from datetime import timedelta

from rollbot.interpreter.calculator import distribute, evaluate


def test_evaluate_basic():
    assert evaluate("1+1") == "1 + 1 › **2**"
    assert evaluate("1-1") == "1 - 1 › **0**"
    assert evaluate("1*1") == "1 \\* 1 › **1**"
    assert evaluate("1/1") == "1 / 1 › **1**"


def test_evaluate_d20():
    regex = r"d20{(\d+)} › \*\*(\d+)\*\*"
    for _ in range(1000):
        res = evaluate("d20")
        m = re.match(regex, res)
        assert m
        assert 1 <= int(m.group(1)) <= 20
        assert m.group(1) == m.group(2)


def test_evaluate_common_damage():
    regex = r"10 \+ 2d6{(\d+),(\d+)} \+ 2 › \*\*(\d+)\*\*"
    for _ in range(1000):
        res = evaluate("10+2d6+2")
        m = re.match(regex, res)
        assert m
        assert 14 <= int(m.group(3)) <= 24
        assert int(m.group(1)) + int(m.group(2)) + 12 == int(m.group(3))


def test_distribute_d20():
    xbin, bins, t = distribute("1d20", timedelta(seconds=1))

    assert [0.5 + i for i in range(21)] == xbin
    assert len(bins) == 20
    assert t > 100


def test_krolls():
    regex = r"4d4k3{(\d)\|(\d),(\d),(\d)} › \*\*(\d+)\*\*"
    for _ in range(1000):
        res = evaluate("4d4k3")
        m = re.match(regex, res)
        assert m
        assert 3 <= int(m.group(5)) <= 18
        assert int(m.group(2)) + int(m.group(3)) + int(m.group(4)) == int(m.group(5))


def test_rrolls():
    regex = r"4d4rr1{(\d)(\(\d\))?,(\d)(\(\d\))?,(\d)(\(\d\))?,(\d)(\(\d\))?} › \*\*(\d+)\*\*"
    for _ in range(1000):
        res = evaluate("4d4rr1")
        m = re.match(regex, res)
        assert m


@pytest.mark.parametrize("roll", [
    "4d4rr1",
    "4d20",
    "4d4k3",
    "10000d10000",
    "3",
    "d20/20"
])
def test_distribute_manyrolls(roll):
    distribute(roll, timedelta(seconds=0.3))
