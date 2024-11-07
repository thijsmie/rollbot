from rollbot.interpreter.calculator import evaluate, EvaluationError
import pytest


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
