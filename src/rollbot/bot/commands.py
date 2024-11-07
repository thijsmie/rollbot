import structlog
from discord import Interaction

from . import handlers, text
from .main import tree

logger = structlog.get_logger()


def log_action(action, context: Interaction, data: str = ""):
    logger.info(
        "Performing action",
        action=action,
        user=context.user.name,
        data=data,
    )


@tree.command(name="help", description="Show a help message")
async def implement_help(context: Interaction):
    log_action("help", context)
    await context.response.send_message(text.helptext)


@tree.command(name="roll", description="Roll some dice, like 'd8+3' or 'max(d20, d20) + 8'.")
async def implement_roll(context: Interaction, roll: str):
    await context.response.defer(thinking=True)
    log_action("roll", context, f"roll: {roll}")
    await handlers.roll(context, roll)


@tree.command(name="distribution", description="Plot the distribution of a diceroll.")
async def implement_distribution(context: Interaction, roll: str):
    await context.response.defer(thinking=True)
    log_action("distribution", context, f"roll: {roll}")
    await handlers.distribution(context, roll)


@tree.command(name="list", description="List your macros.")
async def implement_varlist(context: Interaction):
    await context.response.defer(thinking=True)
    log_action("list", context)
    await handlers.varlist(context)
