from typing import Tuple, Callable, TypeVar, Type
from random import SystemRandom
from functools import wraps
from math import factorial
from datetime import datetime, timedelta

from lark import Tree, Token
from lark.visitors import Interpreter, Transformer

from .parser import parser, reconstructor
from rollbot.varenv import VarEnv


random = SystemRandom()


def comb(n, k, *args):
    return factorial(n) // factorial(k) // factorial(n - k)


def numerical_any(*args):
    return 1 if any(a > 0 for a in args) else 0


def one(*args):
    return 1


def flatten(a):
    if type(a) == list:
        return sum((flatten(b) for b in a), [])
    return [a]

random = SystemRandom()
funcs = {"max": max, "min": min, "fac": factorial, "comb": comb, "any": numerical_any}


class EvaluationError(Exception):
    pass


_Return_T = TypeVar("_Return_T")
_R = TypeVar("_R")
_InterMethod = Callable[[Type[Interpreter], _Return_T], _R]


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
    def roll(self, one: str):
        a,b = map(int, one.split('d'))
        self.count_complexity(AnnotatedCalculateTree.single_roll_complexity * a * (b // 20 + 1))
        r = tuple(random.randint(1, b) for _ in range(a))
        rt = tuple(str(v) for v in r)
        return sum(r), f"{one}{{{','.join(rt)}}}"

    @visit_children_decor
    def sroll(self, one: str):
        b = int(one[1:])
        self.count_complexity(AnnotatedCalculateTree.single_roll_complexity * (b // 20 + 1))
        r = random.randint(1, b)
        return r, f"{one}{{{r}}}"

    @visit_children_decor
    def kroll(self, one: str):
        a, cc = map(int, one.split('d'))
        b, c = map(int, cc.split('k'))
        if c >= a:
            raise EvaluationError("Can't drop more than keeping.")

        self.count_complexity(
            # roll
            AnnotatedCalculateTree.single_roll_complexity * a * (b // 20 + 1)
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
        return sum(rh), f"{one}{{{','.join(rlt)}|{','.join(rht)}}}"

    @visit_children_decor
    def gt(self, one: Tuple[int, str], two: Tuple[int, str]):
        self.count_complexity(1)
        descr = f"({one[1]} > {two[1]})"
        return (1 if one[0] > two[0] else 0), descr

    @visit_children_decor
    def lt(self, one: Tuple[int, str], two: Tuple[int, str]):
        self.count_complexity(1)
        descr = f"({one[1]} < {two[1]})"
        return (1 if one[0] < two[0] else 0), descr

    @visit_children_decor
    def eq(self, one: Tuple[int, str], two: Tuple[int, str]):
        self.count_complexity(1)
        descr = f"({one[1]} == {two[1]})"
        return (1 if one[0] == two[0] else 0), descr

    @visit_children_decor
    def add(self, one: Tuple[int, str], two: Tuple[int, str]):
        self.count_complexity(1)
        return (one[0] + two[0]), f"{one[1]} + {two[1]}"

    @visit_children_decor
    def sub(self, one: Tuple[int, str], two: Tuple[int, str]):
        self.count_complexity(1)
        return (one[0] - two[0]), f"{one[1]} - {two[1]}"

    @visit_children_decor
    def mul(self, one: Tuple[int, str], two: Tuple[int, str]):
        self.count_complexity(1)
        return (one[0] * two[0]), f"{one[1]} \\* {two[1]}"

    @visit_children_decor
    def div(self, one: Tuple[int, str], two: Tuple[int, str]):
        self.count_complexity(1)
        return (one[0] // two[0]), f"{one[1]} / {two[1]}"

    @visit_children_decor
    def mod(self, one: Tuple[int, str], two: Tuple[int, str]):
        self.count_complexity(1)
        return (one[0] % two[0]), f"{one[1]} % {two[1]}"

    @visit_children_decor
    def brace(self, expression: Tuple[int, str]):
        self.count_complexity(1)
        return one[0], f"({one[1]})"

    def number(self, tree):
        self.count_complexity(1)
        return int(tree.children[0].value), tree.children[0].value

    @visit_children_decor
    def neg(self, one: Tuple[int, str]):
        self.count_complexity(1)
        return -one[0], f"-{one[1]}"

    @visit_children_decor
    def pick(self, args):
        self.count_complexity(10)
        args = flatten(args)
        self.count_complexity(len(args))
        c = random.choice(args)
        return c[0], f"{{{c[1]}}}"

    @visit_children_decor
    def func(self, name: str, args):
        self.count_complexity(10)
        args = flatten(args)
        self.count_complexity(len(args))
        if name not in funcs:
            raise EvaluationError(f"No such function '{name}'")

        values = (a[0] for a in args)
        descr = ", ".join(a[1] for a in args)
        return funcs.get(name, one)(*values), f"{name}({descr})"

    @visit_children_decor
    def var(self, name: str):
        self.count_complexity(5)
        if self._depth > 20:
            raise EvaluationError("Depth limit reached (is this a recursive call?)")
        data = self._env.get(name)
        if data is None:
            raise EvaluationError(f"Undefined variable '{name}'.")
        try:
            return int(data), f"_{name}_{{{data}}}"
        except:
            self.count_complexity(100)
            tree = parser.parse(data, start='program')
            calculator = AnnotatedCalculateTree(self._env, self._depth + 1)
            val, desc = calculator.visit(tree)
            self.count_complexity(calculator.count_complexity)
            return val, f"*{name}*{{{desc}}}"

    @visit_children_decor
    def p_value(self, expression: Tuple[int, str]):
        self.count_complexity(1)
        return expression[0], f"{expression[1]} -> **{expression[0]}**"

    @visit_children_decor
    def s_value(self, expression: Tuple[int, str]):
        self.count_complexity(1)
        return f"{expression[1]} -> **{expression[0]}**"

    @visit_children_decor
    def commentate(self, comment, statement):
        self.count_complexity(1)
        return f"{comment} {statement}"

    def statement_list(self, tree):
        self.count_complexity(1)
        a = self.visit(tree.children[0])
        b = self.visit(tree.children[1])
        return f"{a}; {b}"

    @visit_children_decor
    def value_assignment(self, name: Token, expression: Tuple[int, str]):
        self.count_complexity(5)
        self._env.set(name.value, str(expression[0]))
        return f"{name.value} = {{{expression[1]}}} -> **{expression[0]}**"

    @visit_children_decor
    def p_value_assignment(self, name: Token, program: Tuple[int, str]):
        self.count_complexity(5)
        self._env.set(name.value, str(program[0]))
        return f"{name.value} &= ({{{program[1]}}}) -> **{program[1]}**"

    def macro_assignment(self, tree):
        self.count_complexity(100)
        name = tree.children[0].value
        value = reconstructor.reconstruct(tree.children[1])
        self._env.set(name, value)
        return f"{name} = {value}"

    @visit_children_decor
    def p_func(self, statement: str, expression: Tuple[int, str]):
        self.count_complexity(1)
        return expression[0], f"{statement}; {expression[1]} -> **{expression[0]}**"

    @visit_children_decor
    def t_program(self, program: Tuple[int, str]):
        self.count_complexity(1)
        return program[1]

def evaluate(text: str, env: VarEnv = None):
    env = env or VarEnv('test')
    tree = parser.parse(text, start='toplevel')
    return AnnotatedCalculateTree(env).visit(tree)



class MinMaxTree(Interpreter):
    def __init__(self, env: VarEnv, depth=0):
        self._env: VarEnv = env
        self._depth = depth
        super().__init__()

    @visit_children_decor
    def roll(self, one: str):
        a, b = one.split('d')
        return int(a), int(a) * int(b)

    @visit_children_decor
    def sroll(self, one: str):
        return 1, int(one[1:])

    @visit_children_decor
    def kroll(self, one: str):
        a, cc = one.split('d')
        b, c = cc.split('k')
        return int(c), int(c) * int(b)

    @visit_children_decor
    def gt(self, one: Tuple[int, int], two: Tuple[int, int]):
        return 0, 1

    @visit_children_decor
    def lt(self, one: Tuple[int, int], two: Tuple[int, int]):
        return 0, 1

    @visit_children_decor
    def eq(self, one: Tuple[int, int], two: Tuple[int, int]):
        return 0, 1

    @visit_children_decor
    def add(self, one: Tuple[int, int], two: Tuple[int, int]):
        return one[0] + two[0], one[1] + two[1]

    @visit_children_decor
    def sub(self, one: Tuple[int, int], two: Tuple[int, int]):
        return one[0] - two[0], one[1] - two[1]

    @visit_children_decor
    def mul(self, one: Tuple[int, int], two: Tuple[int, int]):
        return one[0] * two[0], one[1] * two[1]

    @visit_children_decor
    def div(self, one: Tuple[int, int], two: Tuple[int, int]):
        return one[0] // two[1], one[1] // two[0]

    @visit_children_decor
    def mod(self, one: Tuple[int, int], two: Tuple[int, int]):
        return 0, two[1] - 1

    def number(self, tree):
        v = int(tree.children[0].value)
        return v, v

    @visit_children_decor
    def neg(self, one: Tuple[int, int]):
        return -one[1], -one[0]

    @visit_children_decor
    def pick(self, args):
        args = flatten(args)
        return min(*(a[0] for a in args)), max(*(a[0] for a in args))

    @visit_children_decor
    def func(self, name: str, args):
        args = flatten(args)
        if name not in funcs:
            raise EvaluationError(f"No such function '{name}'")

        # We have a nice selection of functions that are min/max preserving

        minvalues = (a[0] for a in args)
        maxvalues = (a[1] for a in args)
        return funcs.get(name, one)(*minvalues), funcs.get(name, one)(*maxvalues)

    @visit_children_decor
    def var(self, name: str):
        if self._depth > 20:
            raise EvaluationError("Depth limit reached (is this a recursive call?)")
        data = self._env.get(name)
        if not data:
            raise EvaluationError(f"Undefined variable '{name}'.")

        try:
            return int(data), int(data)
        except:
            tree = parser.parse(data, start='program')
            return MinMaxTree(self._env, self._depth + 1).transform(tree)


class FastPreProc(Transformer):
    def __init__(self, env: VarEnv, depth=0):
        self._env: VarEnv = env
        self._depth = depth
        super().__init__()

    def roll(self, one: str):
        a,b = one[0].split('d')
        return Tree('roll', (int(a), int(b)))

    def sroll(self, one: str):
        return Tree('sroll', (int(one[0][1:]),))

    def kroll(self, one: str):
        a, cc = one[0].split('d')
        b, c = cc.split('k')
        return Tree('roll', (int(c), int(b)))

    def var(self, tree):
        data = self._env.get(tree[0])
        if not data:
            raise EvaluationError(f"Undefined variable '{tree[0]}'.")

        try:
            return int(data)
        except:
            tree = parser.parse(data, start='program')
            return FastPreProc(self._env, self._depth + 1).transform(tree)



class FastCalculateTree(Interpreter):
    @visit_children_decor
    def roll(self, a: int, b: int):
        return sum(random.randint(1, b) for _ in range(a))

    @visit_children_decor
    def sroll(self, a: int):
        return random.randint(1, a)

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
        return one / two

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

        return funcs.get(name, one)(*(a for a in flatten(args)))



def distribute(text: str, timeout: timedelta = None, env: VarEnv = None, num_bins: int = 1000):
    env = env or VarEnv('test')
    timeout = timeout or timedelta(seconds=1)
    tree = parser.parse(text, start='expression')
    minv, maxv = MinMaxTree(env).visit(tree)
    tree = FastPreProc(env).transform(tree)

    try:
        # By evaluating once we ensure the expression does not exceed our complexity limit
        evaluate(text, env)
    except EvaluationError:
        return None

    if minv == maxv:
        return None

    if maxv - minv + 1 < num_bins:
        num_bins = maxv - minv + 1

    binw = (maxv - minv) / (num_bins - 1)

    xbin = [minv + binw * i for i in range(num_bins+1)]
    bins = [0] * num_bins

    end = datetime.now() + timeout
    fct = FastCalculateTree()
    t = 0
    while datetime.now() < end:
        t += 1
        v = fct.visit(tree)
        bins[int((v - minv) / binw)] += 1

    return xbin, bins, t

