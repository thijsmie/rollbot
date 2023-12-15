import logging

from discord import Interaction

from .main import tree
from . import text
from . import handlers


def log_action(action, context: Interaction, data=""):
    logging.info(f"Doing {action} for user {context.user.name} {data}")


@tree.command(name="help", description="Show a help message")
async def implement_help(context: Interaction):
    await context.response.send_message(text.helptext)
    log_action("help", context)


@tree.command(
    name="roll", description="Roll some dice, like 'd8+3' or 'max(d20, d20) + 8'."
)
async def implement_roll(context: Interaction, roll: str):
    await context.response.defer(thinking=True)
    await handlers.roll(context, roll)
    log_action("roll", context, f"roll: {roll}")


@tree.command(name="distribution", description="Plot the distribution of a diceroll.")
async def implement_distribution(context: Interaction, roll: str):
    await context.response.defer(thinking=True)
    await handlers.distribution(context, roll)
    log_action("distribution", context, f"roll: {roll}")


@tree.command(name="list", description="List your macros.")
async def implement_varlist(context: Interaction):
    await context.response.defer(thinking=True)
    await handlers.varlist(context)
    log_action("list", context)
