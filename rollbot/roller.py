import os

from lark import Lark

from .nodes import BuildAST, ValNode


# Non-pretty way to find the current directory with the grammar file
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "roll.grammar")) as f:
    grammar = f.read()


# Turn grammar into parser
calc_parser = Lark(grammar, parser='earley')


# Calculate a result with nice explanatory text
def calc(txt, env):
    tree = calc_parser.parse(txt)
    ast = BuildAST().transform(tree)
    val, description = ast.get(env)
    if ast.calcable:
        env.set("_", ValNode(val))
        return "{} -> {}".format(description, int(val))
    return description


# Make a distribution
def distr(txt, env):
    tree = calc_parser.parse(txt)
    ast = BuildAST().transform(tree)
    return ast.distribution(env)
