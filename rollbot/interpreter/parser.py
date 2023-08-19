from pathlib import Path
from lark import Lark
from lark.reconstruct import Reconstructor


with open(Path(__file__).resolve().parent / "roll.grammar") as f:
    grammar = f.read()


# Turn grammar into parser
parser = Lark(grammar, start=['toplevel', 'program', 'expression'], maybe_placeholders=False)
reconstructor = Reconstructor(parser)
