from pathlib import Path

from lark import Lark
from lark.reconstruct import Reconstructor

with (Path(__file__).resolve().parent / "roll.grammar").open() as f:
    grammar = f.read()


# Turn grammar into parser
parser = Lark(grammar, start=["toplevel", "program", "expression"], maybe_placeholders=False)
reconstructor = Reconstructor(parser)
