import secrets

import discord
import structlog
from discord import Interaction
from lark.exceptions import UnexpectedInput

from rollbot.interpreter.calculator import EvaluationError, evaluate
from rollbot.plottenbakker.asyncing import BakingError, bake_distribution, bake_statistics
from rollbot.stat_tracker import stat_tracker
from rollbot.varenv import VarEnv, var_env_provider

logger = structlog.get_logger()


def get_var_env(context: Interaction) -> VarEnv:
    return var_env_provider.get(str(context.user.id), str(context.user.id), str(context.guild_id))


async def roll(context: Interaction, roll: str) -> None:
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


async def distribution(context: Interaction, roll: str) -> None:
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


async def varlist(context: Interaction) -> None:
    env = get_var_env(context)
    items = env.items
    if not items:
        await context.followup.send("No macros defined")
    else:
        await context.followup.send("\n".join(f"{k} = {v}" for k, v in env.items.items()))


async def unset(context: Interaction, variable: str) -> None:
    env = get_var_env(context)
    if variable in env.items:
        env.unset(variable)
        var_env_provider.update(env)
        await context.followup.send(f"Deleted {variable}")
    else:
        await context.followup.send(f"No such macro {variable}")


async def statistics(context: Interaction, scope: str, die: int, timespan: str) -> None:
    if timespan == "day":
        days = 1
    elif timespan == "week":
        days = 7
    elif timespan == "month":
        days = 30
    else:
        await context.followup.send("Invalid timespan, can be day, week or month")
        return

    if scope == "global":
        scope_name = "Global"
        stats = stat_tracker.get_global_stats(die, days)
    elif scope == "guild":
        scope_name = context.guild.name
        stats = stat_tracker.get_guild_stats(str(context.guild_id), die, days)
    elif scope == "user":
        scope_name = context.user.name
        stats = stat_tracker.get_user_stats(str(context.user.id), die, days)
    else:
        await context.followup.send("Invalid scope, can be global, guild or user")
        return

    if not stats:
        await context.followup.send("No data available")
        return

    rolls = sum(stats.values())

    png = await bake_statistics(
        f"{scope_name} statistics of a d{die} this {timespan}, rolled {rolls} times.", stats, die
    )
    await context.followup.send(file=discord.File(png, filename=f"{secrets.token_urlsafe(8)}.png"))
