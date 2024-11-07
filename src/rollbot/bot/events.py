import itertools

import discord
import structlog

from . import text
from .main import bot, tree

logger = structlog.get_logger()


@bot.event
async def on_ready():
    await tree.sync()

    logger.info("Logged in", bot_name=bot.user.name, bot_id=bot.user.id)

    for batch in itertools.batched(bot.guilds, 50):
        logger.info("Connected to guilds", guilds=[g.name for g in batch])


async def hello_server(channel):
    if channel and channel.permissions_for(channel.guild.me).send_messages:
        try:
            await channel.send(
                embed=discord.Embed(
                    title="Thank you for using roll-bot!",
                    type="rich",
                    description=text.welcome_text.strip(),
                )
            )
            logger.info("Said hello", guild=channel.guild.name, channel=channel.name)
            return True
        except Exception:
            return False
    return False


@bot.event
async def on_guild_join(guild: discord.Guild):
    # The bot has joined a new server, lets let them know what this bot can do
    logger.info("Joined new server", guild=guild.name)

    try:
        if await hello_server(guild.system_channel):
            return
    except Exception:
        pass

    try:
        if await hello_server(guild.rules_channel):
            return
    except Exception:
        pass

    try:
        if await hello_server(guild.public_updates_channel):
            return
    except Exception:
        pass

    for channel in guild.text_channels:
        if await hello_server(channel):
            return

    logger.error("Could not send welcome message", guild=guild.name)
