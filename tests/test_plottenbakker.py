from rollbot.plottenbakker.asyncing import bake_distribution
from rollbot.varenv import VarEnv
import asyncio


def test_bake_distribution():
    img = asyncio.run(bake_distribution("1d20", VarEnv("dummy", {})))
    # assert valid png
    data = img.getvalue()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert data.endswith(b"\x00\x00\x00\x00IEND\xaeB`\x82")
