import secrets

import discord
import structlog
from discord import Interaction
from lark.exceptions import UnexpectedInput

from rollbot.interpreter.calculator import EvaluationError, evaluate
from rollbot.plottenbakker.asyncing import BakingError, bake_distribution
from rollbot.varenv import VarEnv, var_env_provider

logger = structlog.get_logger()


def get_var_env(context: Interaction) -> VarEnv:
    return var_env_provider.get(str(context.user.id))


async def roll(context: Interaction, roll: str):
    env = get_var_env(context)

    try:
        result = evaluate(roll, env)
        var_env_provider.update(env)
    except EvaluationError as e:
        result = e.args[0]
    except UnexpectedInput as e:
        result = f"Unexpected input: ```\n{e.get_context(roll)}```"
    except Exception:
        logger.exception("Error during roll", roll=roll)
        result = "Server error"

    try:
        await context.followup.send(result)
    except Exception:
        logger.exception("Error during followup", roll=roll)
        await context.followup.send("Could not deliver result")


async def distribution(context: Interaction, roll: str):
    env = get_var_env(context)

    try:
        png = await bake_distribution(roll, env)
        await context.followup.send(file=discord.File(png, filename=f"{secrets.token_urlsafe(8)}.png"))
        return
    except BakingError as e:
        result = e.args[0]
    except Exception:
        logger.exception("Error during baking", roll=roll)
        result = "Server error"

    try:
        await context.followup.send(result)
    except Exception:
        logger.exception("Error during followup", roll=roll)
        await context.followup.send("Could not deliver result")


async def varlist(context: Interaction):
    env = get_var_env(context)
    items = env.items
    if not items:
        await context.followup.send("No macros defined")
    else:
        await context.followup.send("\n".join(f"{k} = {v}" for k, v in env.items.items()))
