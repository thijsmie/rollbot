import discord
import secrets
import logging
from lark.exceptions import UnexpectedInput

from discord.ext.commands import Context
from rollbot.varenv import VarEnv, var_env_provider
from rollbot.interpreter.calculator import evaluate, EvaluationError
from rollbot.plottenbakker.asyncing import bake_distribution, BakingError


def get_var_env(context: Context) -> VarEnv:
    return var_env_provider.get(str(context.author.id))


async def roll(context: Context, roll: str):
    env = get_var_env(context)

    try:
        result = evaluate(roll, env)
        var_env_provider.update(env)
    except EvaluationError as e:
        result = e.args[0]
    except UnexpectedInput as e:
        result = f"Unexpected input: ```\n{e.get_context(roll)}```"
    except Exception as e:
        logging.exception(e)
        result = "Server error"

    try:
        await context.respond(result)
    except Exception as e:
        logging.exception(e)
        await context.respond("Could not deliver result")


async def distribution(context: Context, roll: str):
    env = get_var_env(context)

    try:
        png = await bake_distribution(roll, env)
        await context.respond(
            file=discord.File(png, filename=f"{secrets.token_urlsafe(8)}.png")
        )
        return
    except BakingError as e:
        result = e.args[0]
    except Exception as e:
        logging.exception(e)
        result = "Server error"

    try:
        await context.respond(result)
    except Exception as e:
        logging.exception(e)
        await context.respond("Could not deliver result")


async def varlist(context: Context):
    env = get_var_env(context)
    await context.respond("\n".join(f"{k} = {v}" for k, v in env.items.items()))
