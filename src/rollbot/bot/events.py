import textwrap
import logging

import discord
from .main import bot, tree
from . import text


@bot.event
async def on_ready():
    await tree.sync()
    names = ";; ".join(str(g.name) for g in bot.guilds)
    txt = "\n".join(textwrap.wrap(names, width=120))

    logging.warning(
        f"""
--------------------------------------------------
Logged in as {bot.user.name} - {bot.user.id}

All guilds listed below
--------------------------------------------------
{txt}
--------------------------------------------------
That is {len(bot.guilds)} guilds active!
--------------------------------------------------
    """
    )


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
            logging.warning("Said hello to {}!".format(channel.guild.name))
            return True
        except Exception:
            return False
    return False


@bot.event
async def on_guild_join(guild: discord.Guild):
    # The bot has joined a new server, lets let them know what this bot can do
    logging.warning(f"Joined new server '{guild.name}'")

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
    logging.error("Could not say hello to {} sadly... :(".format(guild.name))
