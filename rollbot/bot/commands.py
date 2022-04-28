from .main import bot, Context
from . import text
from . import handlers



@bot.slash_command(name="help")
async def implement_help(context: Context):
    """Show the help message"""
    await context.respond(text.helptext)


@bot.slash_command(name="roll")
async def implement_roll(context: Context, roll: str):
    """Roll some dice, like 'd8+3' or 'max(d20, d20) + 8'."""
    await handlers.roll(context, roll)


@bot.slash_command(name="distribution")
async def implement_distribution(context: Context, roll: str):
    """Plot the distribution of a diceroll."""
    await handlers.distribution(context, roll)


@bot.slash_command(name="list")
async def implement_varlist(context: Context):
    """List your macros."""
    await handlers.varlist(context)
