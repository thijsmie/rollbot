import asyncio

import pytest

from rollbot.plottenbakker.asyncing import BakingError, bake_distribution, bake_statistics
from rollbot.varenv import VarEnv


def test_bake_distribution():
    img = asyncio.run(bake_distribution("1d20", VarEnv("dummy", "", "", {})))
    # assert valid png
    data = img.getvalue()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert data.endswith(b"\x00\x00\x00\x00IEND\xaeB`\x82")


def test_bake_distribution_error():
    # d0 causes an EvaluationError in the distributer → non-zero exit → BakingError
    with pytest.raises(BakingError):
        asyncio.run(bake_distribution("d0", VarEnv("dummy", "", "", {})))


def test_bake_statistics():
    stats = {1: 3, 2: 7, 3: 5, 4: 9, 5: 4, 6: 6}
    img = asyncio.run(bake_statistics("test user", stats, 6))
    data = img.getvalue()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
