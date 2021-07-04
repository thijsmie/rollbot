import textwrap
import logging
import re

import discord

from .varenv import VarEnvProvider
from .roller import calc
from .plottenbakker import bake_distribution


# Discord client
client = discord.Client()

# This regex finds pairs of square brackets to process
command = re.compile(r"\[([^\]]*)\]")

# Provide a environment of variables for each user
envs = VarEnvProvider()

# Handle a bit of message
async def handle_message_command(text, env, channel):
    cmd = text.lower().split(' ', 1)

    # message of style [distribution d20]
    if cmd[0] == 'distribution':
        with bake_distribution(cmd[1], env) as f:
            await channel.send(file=discord.File(f, "distribution_" + cmd[1] + ".png"))

    # message of style [list] shows user all variables he has defined
    elif cmd[0] == "list":
        resp = "\n"
        for k, v in env.items.items():
            resp += "\t{}: {}\n".format(k, v.calc())
        return resp

    elif cmd[0] == "help":
        await hello_server(channel)

    # parse as straight diceroll
    else:
        return "[{}] ".format(calc(text, env))


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # we don't want the bot to reply to other bots
    if message.author.bot:
        return

    # Obtain variable env for this user
    env = envs.get(str(message.author.id))

    # message of style "= d20+1"
    if message.content.startswith("="):
        try:
            resp = await handle_message_command(message.content[1:], env, message.channel)
        except Exception:
            logging.error("Faulty command: {}".format(message.content))
            await message.channel.send(f"{message.author.display_name}: ERROR")
            return
        await message.channel.send(f"{message.author.display_name}: {resp}")
        return

    # parse any [] pairs
    for match in re.finditer(command, message.content):
        try:
            data = match.group(1).strip()
            resp = await handle_message_command(data, env, message.channel)
            await message.channel.send(f"{message.author.display_name}: {resp}")
        except Exception:
            # Something caused an error. Determine if the bot was probably addressed
            # By checking if there was any dice in the command
            try:
                data = match.group(1).strip()
                if re.search("d\d", data):
                    logging.error("Faulty command: {}".format(match.group()))
                    await message.channel.send(f"{message.author.display_name}: ERROR")
            except Exception:
                pass


hello_message = """
To get started, try to roll some dice, just like this: [d20]! 

If you need any help, check out [the website](https://tmiedema.com/rollbot)! You can find a bunch of links there, also including a link to the source code if you are interested. Suggestions for improvements are also very welcome!
"""
async def hello_server(channel):
    if channel and channel.permissions_for(channel.guild.me).send_messages:
        try:
            await channel.send(embed=discord.Embed(title="Thank you for using roll-bot!", type="rich", description=hello_message.strip()))
            logging.warning("Said hello to {}!".format(channel.guild.name))
            return True
        except Exception:
            return False
    return False


@client.event
async def on_guild_join(guild):
    # The bot has joined a new server, lets let them know what this bot can do
    logging.warning(f"Joined new server '{guild.name}'")

    try:
        if (await hello_server(guild.system_channel)):
            return
    except Exception:
        pass

    try:
        if (await hello_server(guild.rules_channel)):
            return
    except Exception:
        pass

    try:
        if (await hello_server(guild.public_updates_channel)):
            return
    except Exception:
        pass

    for channel in guild.text_channels:
        if (await hello_server(channel)):
            return
    logging.error("Could not say hello to {} sadly... :(".format(guild.name))


@client.event
async def on_ready():
    names = ", ".join(str(g.name) for g in client.guilds)
    txt = textwrap.wrap(names, width=120)

    logging.warning(f"""
--------------------------------------------------
Logged in as {client.user.name} - {client.user.id}

All guilds listed below
--------------------------------------------------
{txt}
--------------------------------------------------
    """)
