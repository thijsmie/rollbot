from rollbot.interpreter.calculator import evaluate, distribute
from datetime import timedelta
import re


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


def test_distribute():
    xbin, bins, t = distribute("1d20", timedelta(seconds=1))

    assert list(range(1, 22)) == xbin
    assert len(bins) == 20
    assert t > 100
