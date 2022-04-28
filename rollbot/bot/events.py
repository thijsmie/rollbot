from ast import expr_context
import textwrap
import logging

import discord
from .main import bot
from . import text
from rollbot.varenv import var_env_provider


@bot.event
async def on_ready():
    names = ", ".join(str(g.name) for g in bot.guilds)
    txt = textwrap.wrap(names, width=120)

    logging.warning(
        f"""
--------------------------------------------------
Logged in as {bot.user.name} - {bot.user.id}

All guilds listed below
--------------------------------------------------
{txt}
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
async def on_guild_join(guild):
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


async def update_server(channel):
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
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return

    # we don't want the bot to reply to other bots
    if message.author.bot:
        return

    # we don't care here about messages not associated to a guild
    if message.guild is None:
        return


    UPDATE_LVL = 1
    env = var_env_provider.get("__internal__")
    update_level = int(env.get(f"GuildULVL[{message.guild.id}]") or "0")

    if update_level >= UPDATE_LVL:
        return

    try:
        if message.content.startswith("="):
            await message.channel.send(
                embed=discord.Embed(
                    title="Rollbot has updated!",
                    type="rich",
                    description=text.update_text.strip(),
                )
            )
            env.set(f"GuildULVL[{message.guild.id}]", str(UPDATE_LVL))
            var_env_provider.update(env)
    except:
        # We don't care if message.content is gone now
        pass
