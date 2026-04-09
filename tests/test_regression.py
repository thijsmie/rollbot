import pytest

from rollbot.interpreter.calculator import AnnotatedCalculateTree, EvaluationError, evaluate
from rollbot.varenv import VarEnv


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

    with pytest.raises(EvaluationError):
        evaluate("2d0kl1")

    with pytest.raises(EvaluationError):
        evaluate("1d0rr1")


def test_kroll_keep_exceeds_rolls():
    with pytest.raises(EvaluationError, match="Can't drop more than keeping"):
        evaluate("2d6k3")

    with pytest.raises(EvaluationError, match="Can't drop more than keeping"):
        evaluate("2d6kl3")


def test_exroll_must_have_two_sides():
    with pytest.raises(EvaluationError, match="at least two sides"):
        evaluate("1d1!")


def test_fn_comb():
    result = evaluate("comb(5, 2)")
    assert "10" in result


def test_fn_any():
    assert "0" in evaluate("any(0, 0)")
    assert "1" in evaluate("any(1, 0)")


def test_fn_fac_negative_arg():
    # fac with negative arg returns 1 (the else-branch of fn_fac)
    result = evaluate("fac(-1)")
    assert "1" in result


def test_var_macro_expansion():
    env = VarEnv("test", "test", "test")
    env.set("atk", "d20")
    result = evaluate("atk", env)
    # The var expands the stored expression and includes it in the description
    assert "d20" in result


def test_var_depth_limit():
    env = VarEnv("test", "test", "test")
    env.set("x", "x")
    with pytest.raises(EvaluationError, match="Depth limit"):
        evaluate("x", env)


def test_commentate():
    result = evaluate('"attack roll" d20')
    assert "attack roll" in result


def test_value_assignment():
    env = VarEnv("test", "test", "test")
    result = evaluate("x &= 5", env)
    assert "5" in result
    assert env.get("x") == "5"


def test_macro_assignment():
    env = VarEnv("test", "test", "test")
    evaluate("myroll = d20", env)
    assert env.get("myroll") == "d20"


def test_complexity_limit():
    original = AnnotatedCalculateTree.roll_complexity_limit
    AnnotatedCalculateTree.roll_complexity_limit = 0
    try:
        with pytest.raises(EvaluationError, match="complexity too high"):
            evaluate("d20")
    finally:
        AnnotatedCalculateTree.roll_complexity_limit = original
