import pytest

from rollbot.interpreter.calculator import EvaluationError, evaluate


def test_func_arity():
    evaluate("max(d20)")
    evaluate("max(d20, d20)")
    evaluate("min(d20)")
    evaluate("min(d20, d20)")
    evaluate("fac(5)")
    evaluate("fac(5, 5)")

    with pytest.raises(EvaluationError):
        evaluate("nosuchfun()")

    with pytest.raises(EvaluationError):
        evaluate("nosuchfun(1)")


def test_zero_sided_die():
    with pytest.raises(EvaluationError):
        evaluate("d0")

    with pytest.raises(EvaluationError):
        evaluate("1d0")

    with pytest.raises(EvaluationError):
        evaluate("2d0k1")
