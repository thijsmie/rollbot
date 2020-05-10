import itertools
import random
from functools import reduce
from math import factorial, ceil

from lark import Transformer


random = random.SystemRandom()


def comb(n, k):
    return factorial(n) / factorial(k) / factorial(n - k)


def one(*args):
    return 1


class Node:
    def get(self, env):
        pass

    def on_assign(self, env):
        return self

    def distribution(self, env):
        """ Return two lists, the first with the possible values, the second with their relative probability. """
        pass

    def calc(self):
        pass

    @property
    def calcable(self):
        return True


class ValNode(Node):
    def __init__(self, a):
        self.a = a

    def get(self, env):
        return self.a, str(self.a)

    def calc(self):
        return str(self.a)

    def distribution(self, env):
        return [self.a], [1]


class AddNode(Node):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get(self, env):
        va, da = self.a.get(env)
        vb, db = self.b.get(env)
        return int(va + vb), "({} + {})".format(da, db)

    def on_assign(self, env):
        return AddNode(self.a.on_assign(env), self.b.on_assign(env))

    def calc(self):
        return "({} + {})".format(self.a.calc(), self.b.calc())

    def distribution(self, env):
        a_pos, a_prob = self.a.distribution(env)
        b_pos, b_prob = self.b.distribution(env)

        out_pos = [0] * (len(a_pos) * len(b_pos))
        out_prob = [1] * (len(out_pos))

        for i in range(len(a_pos)):
            for j in range(len(b_pos)):
                out_pos[i * len(b_pos) + j] = a_pos[i] + b_pos[j]
                out_prob[i * len(b_pos) + j] = a_prob[i] * b_prob[j]

        return out_pos, out_prob


class SubNode(Node):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get(self, env):
        va, da = self.a.get(env)
        vb, db = self.b.get(env)
        return int(va - vb), "({} - {})".format(da, db)

    def on_assign(self, env):
        return SubNode(self.a.on_assign(env), self.b.on_assign(env))

    def calc(self):
        return "({} - {})".format(self.a.calc(), self.b.calc())

    def distribution(self, env):
        a_pos, a_prob = self.a.distribution(env)
        b_pos, b_prob = self.b.distribution(env)

        out_pos = [0] * (len(a_pos) * len(b_pos))
        out_prob = [1] * (len(out_pos))

        for i in range(len(a_pos)):
            for j in range(len(b_pos)):
                out_pos[i * len(b_pos) + j] = a_pos[i] - b_pos[j]
                out_prob[i * len(b_pos) + j] = a_prob[i] * b_prob[j]

        return out_pos, out_prob


class NegNode(Node):
    def __init__(self, a):
        self.a = a

    def get(self, env):
        va, da = self.a.get(env)
        return -va, "-{}".format(da)

    def on_assign(self, env):
        return NegNode(self.a.on_assign(env))

    def calc(self):
        return "-{}".format(self.a.calc())

    def distribution(self, env):
        pos, prob = self.a.distribution(env)
        pos = [-a for a in pos]
        return pos, prob


class MulNode(Node):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get(self, env):
        va, da = self.a.get(env)
        vb, db = self.b.get(env)
        return int(va * vb), "{} * {}".format(da, db)

    def on_assign(self, env):
        return MulNode(self.a.on_assign(env), self.b.on_assign(env))

    def calc(self):
        return "{} * {}".format(self.a.calc(), self.b.calc())

    def distribution(self, env):
        a_pos, a_prob = self.a.distribution(env)
        b_pos, b_prob = self.b.distribution(env)

        out_pos = [0] * (len(a_pos) * len(b_pos))
        out_prob = [1] * (len(out_pos))

        for i in range(len(a_pos)):
            for j in range(len(b_pos)):
                out_pos[i * len(b_pos) + j] = a_pos[i] * b_pos[j]
                out_prob[i * len(b_pos) + j] = a_prob[i] * b_prob[j]

        return out_pos, out_prob


class DivNode(Node):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get(self, env):
        va, da = self.a.get(env)
        vb, db = self.b.get(env)
        return va / vb, "{} / {}".format(da, db)

    def on_assign(self, env):
        return DivNode(self.a.on_assign(env), self.b.on_assign(env))

    def calc(self):
        return "{} / {}".format(self.a.calc(), self.b.calc())

    def distribution(self, env):
        a_pos, a_prob = self.a.distribution(env)
        b_pos, b_prob = self.b.distribution(env)

        out_pos = [0] * (len(a_pos) * len(b_pos))
        out_prob = [1] * (len(out_pos))

        for i in range(len(a_pos)):
            for j in range(len(b_pos)):
                out_pos[i * len(b_pos) + j] = a_pos[i] / b_pos[j]
                out_prob[i * len(b_pos) + j] = a_prob[i] * b_prob[j]

        return out_pos, out_prob


class CompareNode(Node):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get(self, env):
        va, da = self.a.get(env)
        vb, db = self.b.get(env)
        return int(va > vb), "({} > {})".format(da, db)

    def on_assign(self, env):
        return CompareNode(self.a.on_assign(env), self.b.on_assign(env))

    def calc(self):
        return "({} > {})".format(self.a.calc(), self.b.calc())

    def distribution(self, env):
        a_pos, a_prob = self.a.distribution(env)
        b_pos, b_prob = self.b.distribution(env)

        count_0 = 0
        count_1 = 0

        for i in range(len(a_pos)):
            for j in range(len(b_pos)):
                if a_pos[i] > b_pos[j]:
                    count_1 += a_prob[i] * b_prob[j]
                else:
                    count_0 += a_prob[i] * b_prob[j]

        return [0, 1], [count_0, count_1]


class VarNode(Node):
    def __init__(self, a, exec):
        self.a = a
        self.e = exec

    def get(self, env):
        va, da = env.get(self.a).get(env)
        return va, "{}{{{}}}".format(self.a, da)

    def on_assign(self, env):
        if self.e:
            return ValNode(self.get(env)[0])
        else:
            return VarNode(self.a, self.e)

    def calc(self):
        if self.e:
            return "{}".format(self.a)
        else:
            return "&{}".format(self.a)

    def distribution(self, env):
        return env.get(self.a).distribution(env)


class AvgNode(Node):
    def __init__(self, a):
        self.a = a

    def get(self, env):
        possibilities, probabilities = self.a.distribution(env)
        average = sum(x * y for x, y in zip(possibilities, probabilities)) / sum(probabilities)

        return average, "average({}){{{}}}".format(self.a.calc(), average)

    def on_assign(self, env):
        return NegNode(self.a.on_assign(env))

    def calc(self):
        return "average({})".format(self.a.calc())

    def distribution(self, env):
        val, _ = self.get(env)
        return [val], [1]


class AssignNode(Node):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get(self, env):
        vb = self.b.on_assign(env)
        env.set(self.a, vb)
        return 0, "{} = {}".format(self.a, vb.calc())

    def calc(self):
        return "{} = {}".format(self.a, self.b.calc())

    @property
    def calcable(self):
        return False


class RollNode(Node):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get(self, env):
        results = [random.randint(1, self.b) for _ in range(self.a)]
        return sum(results), "{}d{}{{{}}}".format(self.a, self.b, ", ".join(str(a) for a in results))

    def calc(self):
        if self.a != 1:
            return "{}d{}".format(self.a, self.b)
        else:
            return "d{}".format(self.b)

    def distribution(self, env):
        possible = list(range(self.a, self.a * self.b + 1))
        combinations = [0] * len(possible)

        for i in range(int(ceil(len(possible) / 2.0))):
            p = possible[i]
            s = self.b
            n = self.a
            combinations[i] = sum(((-1) ** k) * comb(n, k) * comb(p - s * k - 1, n - 1)
                                  for k in range(int(abs((p - n) / s)) + 1))
            combinations[-i - 1] = combinations[i]

        return possible, combinations


class FuncNode(Node):
    def __init__(self, funcname, func, args):
        self.funcname = funcname
        self.func = func
        self.args = args

    def get(self, env):
        values = []
        descriptions = []

        for a in self.args:
            v, d = a.get(env)
            values.append(v)
            descriptions.append(d)
        return self.func(*values), "{}({})".format(self.funcname, ", ".join(descriptions))

    def calc(self):
        return "{}({})".format(self.funcname, ", ".join(a.calc() for a in self.args))

    def distribution(self, env):
        possibilities = []
        probabilities = []

        for a in self.args:
            pos, prob = a.distribution(env)
            possibilities.append(pos)
            probabilities.append(prob)

        out_pos = [0] * reduce(lambda x, y: x*y, [len(p) for p in possibilities])
        out_prob = [1] * (len(out_pos))

        for i, v in enumerate(itertools.product(*possibilities)):
            out_pos[i] = self.func(*v)
        for i, v in enumerate(itertools.product(*probabilities)):
            out_prob[i] = reduce(lambda x, y: x*y, v)

        return out_pos, out_prob


class PickNode(Node):
    def __init__(self, options):
        self.options = options

    def get(self, env):
        option = random.choice(self.options)
        val, desc = option.get(env)
        return val, "{{{}}}".format(desc)

    def calc(self):
        return "{{{}}}".format(", ".join(a.calc() for a in self.options))

    def distribution(self, env):
        possibilities = []
        probabilities = []

        for a in self.options:
            pos, prob = a.distribution(env)
            possibilities += pos
            probabilities += [p * 1/float(len(self.options)) for p in prob]

        return possibilities, probabilities


functions = {
    'max': max,
    'min': min,
    'factorial': factorial,
    'comb': comb,
    'int': int
}


class BuildAST(Transformer):
    @staticmethod
    def assign_var(args):
        return AssignNode(*args)

    @staticmethod
    def var(args):
        return VarNode(args[0], False)

    @staticmethod
    def expl_exc_var(args):
        return VarNode(args[0], True)

    @staticmethod
    def roll(args):
        if len(args) > 1:
            return RollNode(int(args[0]), int(args[1]))
        return RollNode(1, int(args[0]))

    @staticmethod
    def number(num):
        return ValNode(int(num[0]))

    @staticmethod
    def add(nums):
        return AddNode(nums[0], nums[1])

    @staticmethod
    def sub(nums):
        return SubNode(nums[0], nums[1])

    @staticmethod
    def mul(nums):
        return MulNode(nums[0], nums[1])

    @staticmethod
    def div(nums):
        return DivNode(nums[0], nums[1])

    @staticmethod
    def func(nums):
        if nums[0] == "average":
            return AvgNode(nums[1])
        func = functions.get(nums[0], one)
        args = nums[1]
        if type(args) != list:
            args = [args]
        if len(nums) > 2:
            args = args + nums[2]
        return FuncNode(nums[0], func, args)

    @staticmethod
    def args(nums):
        if type(nums) is list:
            if len(nums) > 1 and type(nums[1]) is list:
                nums = [nums[0]] + nums[1]
        return nums

    @staticmethod
    def pick(nums):
        args = nums[0]
        if type(args) != list:
            args = [args]
        return PickNode(args)

    @staticmethod
    def neg(num):
        return NegNode(num[0])

    @staticmethod
    def average(num):
        return AvgNode(num[0])

    @staticmethod
    def greater(nums):
        return CompareNode(nums[0], nums[1])

    @staticmethod
    def smaller(nums):
        return CompareNode(nums[1], nums[0])
