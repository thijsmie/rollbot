import asyncio
import sys
from io import BytesIO

from rollbot.varenv import VarEnv

from . import BakingError
from .plotter import plot_distribution, plot_statistics


async def bake_distribution(expression: str, env: VarEnv) -> BytesIO:
    bakery = await asyncio.subprocess.create_subprocess_exec(
        sys.executable,
        "-m",
        "rollbot.plottenbakker.distributer",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await bakery.communicate(f"{env.name}\n{expression}\n".encode())
    if bakery.returncode != 0:
        raise BakingError(stdout.decode())

    try:
        pxbins, pdata, pnumrolls, _ = stdout.decode().split("\n")
        xbins = [float(x) for x in pxbins.split(" ")]
        data = [int(x) for x in pdata.split(" ")]
        num_rolls = int(pnumrolls)
    except Exception:
        raise BakingError("Server Error")

    buf = BytesIO()
    plot_distribution(buf, expression, xbins, data, num_rolls)
    buf.seek(0)
    return buf


async def bake_statistics(description: str, stats: dict[int, int], die: int) -> BytesIO:
    buf = BytesIO()
    plot_statistics(buf, description, stats, die)
    buf.seek(0)
    return buf
