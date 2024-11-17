import functools
import operator
import re
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps
from random import SystemRandom
from typing import TypeVar

import structlog
from lark import Token, Tree
from lark.visitors import Interpreter, Transformer

from rollbot.stat_tracker import stat_tracker
from rollbot.varenv import VarEnv

from .functions import funcs
from .parser import parser, reconstructor

random = SystemRandom()
logger = structlog.get_logger()


def flatten(a):
    if isinstance(a, list):
        return functools.reduce(operator.iadd, (flatten(b) for b in a), [])
    return [a]


random = SystemRandom()


class EvaluationError(Exception):
    pass


_Return_T = TypeVar("_Return_T")
_R = TypeVar("_R")
_InterMethod = Callable[[type[Interpreter], _Return_T], _R]


def visit_children_decor(func: _InterMethod) -> _InterMethod:
    @wraps(func)
    def inner(cls, tree):
        values = cls.visit_children(tree)
        return func(cls, *values)

    return inner


class AnnotatedCalculateTree(Interpreter):
    roll_complexity_limit = 100_000_000
    single_roll_complexity = 10

    def __init__(self, env: VarEnv, depth=0):
        self._env: VarEnv = env
        self._depth = depth
        self._complexity_counter = 0
        super().__init__()

    def count_complexity(self, complexity):
        self._complexity_counter += complexity
        if self._complexity_counter > AnnotatedCalculateTree.roll_complexity_limit:
            raise EvaluationError("Roll calculation timed out: complexity too high!")

    @visit_children_decor
    def roll(self, one: str) -> tuple[int, str]:
        a, b = map(int, one.split("d"))

        if b == 0:
            raise EvaluationError("Can't roll a zero-sided die.")

        self.count_complexity(AnnotatedCalculateTree.single_roll_complexity * a * int(b // 20 + 1))
        r = tuple(random.randint(1, b) for _ in range(a))
        rt = tuple(str(v) for v in r)
        res = sum(r)
        desc = f"{one}{{{','.join(rt)}}}"
        logger.info("roll", roll=one, result=res)

        for v in r:
            stat_tracker.increment_stat(self._env.guild, self._env.user, b, v)

        return res, desc

    @visit_children_decor
    def sroll(self, one: str) -> tuple[int, str]:
        b = int(one[1:])

        if b == 0:
            raise EvaluationError("Can't roll a zero-sided die.")

        self.count_complexity(AnnotatedCalculateTree.single_roll_complexity * int(b // 20 + 1))
        res = random.randint(1, b)
        desc = f"{one}{{{res}}}"
        logger.info("roll", roll=one, result=res)

        stat_tracker.increment_stat(self._env.guild, self._env.user, b, res)

        return res, desc

    @visit_children_decor
    def kroll(self, one: str) -> tuple[int, str]:
        a, b, c = map(int, re.split("k|d", one))

        if b == 0:
            raise EvaluationError("Can't roll a zero-sided die.")

        if c > a:
            raise EvaluationError("Can't drop more than keeping.")

        self.count_complexity(
            # roll
            AnnotatedCalculateTree.single_roll_complexity * a * int(b // 20 + 1)
            # sort
            + a * a * 2
        )

        r = tuple(random.randint(1, b) for _ in range(a))
        r = tuple(sorted(r))
        border = int(a) - int(c)
        rl = r[:border]
        rh = r[border:]
        rlt = tuple(str(v) for v in rl)
        rht = tuple(str(v) for v in rh)
        res = sum(rh)
        desc = f"{one}{{{','.join(rlt)}|{','.join(rht)}}}"
        logger.info("roll", roll=one, result=res)

        for v in r:
            stat_tracker.increment_stat(self._env.guild, self._env.user, b, v)

        return res, desc

    @visit_children_decor
    def rroll(self, one: str) -> tuple[int, str]:
        a, b, c = map(int, re.split("d|rr", one))

        if b == 0:
            raise EvaluationError("Can't roll a zero-sided die.")

        self.count_complexity(AnnotatedCalculateTree.single_roll_complexity * a * int(b // 20 + 1) * c)

        roll1 = tuple(random.randint(1, b) for _ in range(a))
        roll2 = tuple(
            (True, prev_result, random.randint(1, b)) if prev_result <= c else (False, prev_result, prev_result)
            for prev_result in roll1
        )
        rt = tuple(f"{v}({pv})" if rerolled else str(v) for rerolled, pv, v in roll2)
        res = sum(v[2] for v in roll2)
        desc = f"{one}{{{','.join(rt)}}}"
        logger.info("rroll", roll=one, result=res)

        for rerolled, pv, v in roll2:
            if rerolled:
                stat_tracker.increment_stat(self._env.guild, self._env.user, b, pv)
            stat_tracker.increment_stat(self._env.guild, self._env.user, b, v)

        return res, desc

    @visit_children_decor
    def gt(self, one: tuple[int, str], two: tuple[int, str]) -> tuple[int, str]:
        self.count_complexity(1)
        descr = f"({one[1]} > {two[1]})"
        return (1 if one[0] > two[0] else 0), descr

    @visit_children_decor
    def lt(self, one: tuple[int, str], two: tuple[int, str]) -> tuple[int, str]:
        self.count_complexity(1)
        descr = f"({one[1]} < {two[1]})"
        return (1 if one[0] < two[0] else 0), descr

    @visit_children_decor
    def eq(self, one: tuple[int, str], two: tuple[int, str]) -> tuple[int, str]:
        self.count_complexity(1)
        descr = f"({one[1]} == {two[1]})"
        return (1 if one[0] == two[0] else 0), descr

    @visit_children_decor
    def add(self, one: tuple[int, str], two: tuple[int, str]) -> tuple[int, str]:
        self.count_complexity(1)
        return (one[0] + two[0]), f"{one[1]} + {two[1]}"

    @visit_children_decor
    def sub(self, one: tuple[int, str], two: tuple[int, str]) -> tuple[int, str]:
        self.count_complexity(1)
        return (one[0] - two[0]), f"{one[1]} - {two[1]}"

    @visit_children_decor
    def mul(self, one: tuple[int, str], two: tuple[int, str]) -> tuple[int, str]:
        self.count_complexity(1)
        return (one[0] * two[0]), f"{one[1]} \\* {two[1]}"

    @visit_children_decor
    def div(self, one: tuple[int, str], two: tuple[int, str]) -> tuple[int, str]:
        self.count_complexity(1)
        return int(one[0] // two[0]), f"{one[1]} / {two[1]}"

    @visit_children_decor
    def mod(self, one: tuple[int, str], two: tuple[int, str]) -> tuple[int, str]:
        self.count_complexity(1)
        return (one[0] % two[0]), f"{one[1]} % {two[1]}"

    @visit_children_decor
    def brace(self, expression: tuple[int, str]) -> tuple[int, str]:
        self.count_complexity(1)
        return expression[0], f"({expression[1]})"

    def number(self, tree) -> tuple[int, str]:
        self.count_complexity(1)
        return int(tree.children[0].value), tree.children[0].value

    @visit_children_decor
    def neg(self, one: tuple[int, str]) -> tuple[int, str]:
        self.count_complexity(1)
        return -one[0], f"-{one[1]}"

    @visit_children_decor
    def pick(self, args) -> tuple[int, str]:
        self.count_complexity(10)
        args = flatten(args)
        self.count_complexity(len(args))
        c = random.choice(args)
        return c[0], f"{{{c[1]}}}"

    @visit_children_decor
    def func(self, name: str, args: list[tuple[int, str]] | None = None) -> tuple[int, str]:
        if not args:
            raise EvaluationError(f"Function '{name}' requires arguments")

        self.count_complexity(10)
        args = flatten(args)
        self.count_complexity(len(args))
        if name not in funcs:
            raise EvaluationError(f"No such function '{name}'")

        values = [a[0] for a in args]
        descr = ", ".join(a[1] for a in args)
        return funcs[name](values), f"{name}({descr})"

    @visit_children_decor
    def var(self, name: str) -> tuple[int, str]:
        self.count_complexity(5)
        if self._depth > 20:
            raise EvaluationError("Depth limit reached (is this a recursive call?)")
        data = self._env.get(name)
        if data is None:
            raise EvaluationError(f"Undefined variable '{name}'.")
        try:
            return int(data), f"_{name}_{{{data}}}"
        except ValueError:
            self.count_complexity(100)
            tree = parser.parse(data, start="program")
            calculator = AnnotatedCalculateTree(self._env, self._depth + 1)
            val, desc = calculator.visit(tree)
            self.count_complexity(calculator._complexity_counter)
            return val, f"*{name}*{{{desc}}}"

    @visit_children_decor
    def p_value(self, expression: tuple[int, str]) -> tuple[int, str]:
        self.count_complexity(1)
        if len(expression[1]) > 500:
            return expression[0], f"[too long to render] › **{expression[0]}**"
        return expression[0], f"{expression[1]} › **{expression[0]}**"

    @visit_children_decor
    def s_value(self, expression: tuple[int, str]) -> str:
        self.count_complexity(1)
        if len(expression[1]) > 500:
            return f"[too long to render] › **{expression[0]}**"
        return f"{expression[1]} › **{expression[0]}**"

    @visit_children_decor
    def commentate(self, comment, statement) -> str:
        self.count_complexity(1)
        return f"{comment} {statement}"

    def statement_list(self, tree) -> str:
        self.count_complexity(1)
        a = self.visit(tree.children[0])
        b = self.visit(tree.children[1])
        return f"{a}; {b}"

    @visit_children_decor
    def value_assignment(self, name: Token, expression: tuple[int, str]) -> str:
        self.count_complexity(5)
        self._env.set(name.value, str(expression[0]))
        if len(expression[1]) > 500:
            return expression[0], f"{name.value} = [too long to render] › **{expression[0]}**"
        return f"{name.value} = {{{expression[1]}}} › **{expression[0]}**"

    @visit_children_decor
    def p_value_assignment(self, name: Token, program: tuple[int, str]) -> str:
        self.count_complexity(5)
        self._env.set(name.value, str(program[0]))
        if len(program[1]) > 500:
            return f"{name.value} &= (too long to render) › **{program[1]}**"
        return f"{name.value} &= ({{{program[1]}}}) › **{program[1]}**"

    def macro_assignment(self, tree) -> str:
        self.count_complexity(100)
        name = tree.children[0].value
        value = reconstructor.reconstruct(tree.children[1])
        self._env.set(name, value)
        return f"{name} = {value}"

    @visit_children_decor
    def p_func(self, statement: str, expression: tuple[int, str]) -> tuple[int, str]:
        self.count_complexity(1)
        if len(expression[1]) > 500:
            return expression[0], f"{statement}; [too long to render] › **{expression[0]}**"
        return expression[0], f"{statement}; {expression[1]} › **{expression[0]}**"

    @visit_children_decor
    def t_program(self, program: tuple[int, str]) -> str:
        self.count_complexity(1)
        return program[1]


def evaluate(text: str, env: VarEnv = None) -> tuple[int, str] | str:
    env = env or VarEnv("test", "test", "test")
    tree = parser.parse(text, start="toplevel")
    evaluation = AnnotatedCalculateTree(env).visit(tree)
    logger.info("evaluation", result=evaluation)
    return evaluation


class MinMaxTree(Interpreter):
    def __init__(self, env: VarEnv, depth=0):
        self._env: VarEnv = env
        self._depth = depth
        super().__init__()

    @visit_children_decor
    def roll(self, one: str):
        a, b = one.split("d")
        return int(a), int(a) * int(b)

    @visit_children_decor
    def sroll(self, one: str):
        return 1, int(one[1:])

    @visit_children_decor
    def kroll(self, one: str):
        a, cc = one.split("d")
        b, c = cc.split("k")
        return int(c), int(c) * int(b)

    @visit_children_decor
    def rroll(self, one: str):
        a, cc = one.split("d")
        b, c = cc.split("rr")
        return int(a), int(a) * int(b)

    @visit_children_decor
    def gt(self, one: tuple[int, int], two: tuple[int, int]):
        return 0, 1

    @visit_children_decor
    def lt(self, one: tuple[int, int], two: tuple[int, int]):
        return 0, 1

    @visit_children_decor
    def eq(self, one: tuple[int, int], two: tuple[int, int]):
        return 0, 1

    @visit_children_decor
    def add(self, one: tuple[int, int], two: tuple[int, int]):
        return one[0] + two[0], one[1] + two[1]

    @visit_children_decor
    def sub(self, one: tuple[int, int], two: tuple[int, int]):
        return one[0] - two[1], one[1] - two[0]

    @visit_children_decor
    def mul(self, one: tuple[int, int], two: tuple[int, int]):
        # With negatives involved, we have to consider all possible combinations
        extremas = (one[0] * two[0], one[0] * two[1], one[1] * two[0], one[1] * two[1])
        return min(extremas), max(extremas)

    @visit_children_decor
    def div(self, one: tuple[int, int], two: tuple[int, int]):
        # With negatives involved, we have to consider all possible combinations
        extremas = (one[0] // two[0], one[0] // two[1], one[1] // two[0], one[1] // two[1])
        return int(min(extremas)), int(max(extremas))

    @visit_children_decor
    def mod(self, one: tuple[int, int], two: tuple[int, int]):
        return 0, two[1] - 1

    def number(self, tree):
        v = int(tree.children[0].value)
        return v, v

    @visit_children_decor
    def neg(self, one: tuple[int, int]):
        return -one[1], -one[0]

    @visit_children_decor
    def pick(self, args):
        args = flatten(args)
        return min(*(a[0] for a in args)), max(*(a[1] for a in args))

    @visit_children_decor
    def func(self, name: str, args):
        args = flatten(args)
        if name not in funcs:
            raise EvaluationError(f"No such function '{name}'")

        # We have a nice selection of functions that are min/max preserving

        minvalues = [a[0] for a in args]
        maxvalues = [a[1] for a in args]
        return funcs[name](minvalues), funcs[name](maxvalues)

    @visit_children_decor
    def var(self, name: str):
        if self._depth > 20:
            raise EvaluationError("Depth limit reached (is this a recursive call?)")
        data = self._env.get(name)
        if not data:
            raise EvaluationError(f"Undefined variable '{name}'.")

        try:
            return int(data), int(data)
        except ValueError:
            tree = parser.parse(data, start="program")
            return MinMaxTree(self._env, self._depth + 1).transform(tree)


def minmax(text: str, env: VarEnv = None) -> tuple[int, int]:
    env = env or VarEnv("test", "test", "test")
    tree = parser.parse(text, start="expression")
    return MinMaxTree(env).visit(tree)


class FastPreProc(Transformer):
    def __init__(self, env: VarEnv, depth=0):
        self._env: VarEnv = env
        self._depth = depth
        super().__init__()

    def roll(self, one: str):
        a, b = one[0].split("d")
        return Tree("roll", (int(a), int(b)))

    def sroll(self, one: str):
        return Tree("sroll", (int(one[0][1:]),))

    def kroll(self, one: str):
        a, cc = one[0].split("d")
        b, c = cc.split("k")
        return Tree("kroll", (int(a), int(b), int(c)))

    def rroll(self, one: str):
        a, cc = one[0].split("d")
        b, c = cc.split("rr")
        return Tree("rroll", (int(a), int(b), int(c)))

    def var(self, tree):
        data = self._env.get(tree[0])
        if not data:
            raise EvaluationError(f"Undefined variable '{tree[0]}'.")

        try:
            return int(data)
        except ValueError:
            tree = parser.parse(data, start="program")
            return FastPreProc(self._env, self._depth + 1).transform(tree)


class FastCalculateTree(Interpreter):
    @visit_children_decor
    def roll(self, a: int, b: int):
        return sum(random.randint(1, b) for _ in range(a))

    @visit_children_decor
    def sroll(self, a: int):
        return random.randint(1, a)

    @visit_children_decor
    def kroll(self, a: int, b: int, c: int):
        r = tuple(random.randint(1, b) for _ in range(a))
        r = tuple(sorted(r))
        border = int(a) - int(c)
        rh = r[border:]
        return sum(rh)

    @visit_children_decor
    def rroll(self, a: int, b: int, c: int):
        roll1 = tuple(random.randint(1, b) for _ in range(a))
        roll2 = tuple(random.randint(1, b) if prev_result <= c else prev_result for prev_result in roll1)
        return sum(roll2)

    @visit_children_decor
    def gt(self, one: int, two: int):
        return 1 if one > two else 0

    @visit_children_decor
    def lt(self, one: int, two: int):
        return 1 if one < two else 0

    @visit_children_decor
    def eq(self, one: int, two: int):
        return 1 if one == two else 0

    @visit_children_decor
    def add(self, one: int, two: int):
        return one + two

    @visit_children_decor
    def sub(self, one: int, two: int):
        return one - two

    @visit_children_decor
    def mul(self, one: int, two: int):
        return one * two

    @visit_children_decor
    def div(self, one: int, two: int):
        return int(one / two)

    @visit_children_decor
    def mod(self, one: int, two: int):
        return one % two

    def number(self, tree):
        return int(tree.children[0].value)

    @visit_children_decor
    def neg(self, one: int):
        return -one

    @visit_children_decor
    def pick(self, args):
        return random.choice(flatten(args))

    @visit_children_decor
    def func(self, name: str, args):
        if name not in funcs:
            raise EvaluationError(f"No such function '{name}'")

        return funcs.get[name](*(a for a in flatten(args)))


def distribute(text: str, timeout: timedelta | None = None, env: VarEnv = None, num_bins: int = 1000):
    env = env or VarEnv("test", "test", "test")
    timeout = timeout or timedelta(seconds=1)
    tree = parser.parse(text, start="expression")
    minv, maxv = MinMaxTree(env).visit(tree)
    tree = FastPreProc(env).transform(tree)

    try:
        # By evaluating once we ensure the expression does not exceed our complexity limit
        evaluate(text, env)
    except EvaluationError:
        return None

    if minv == maxv:
        return [minv - 0.5, minv + 0.5], [1], 1

    num_bins = min(maxv - minv + 1, num_bins)

    binw = (maxv - minv) / (num_bins - 1)

    xbin = [minv + binw * i - 0.5 for i in range(num_bins + 1)]
    bins = [0] * num_bins

    end = datetime.now() + timeout
    fct = FastCalculateTree()
    t = 0
    while datetime.now() < end:
        t += 1
        v = fct.visit(tree)
        bins[int((v - minv) / binw)] += 1

    return xbin, bins, t
