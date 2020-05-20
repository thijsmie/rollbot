import traceback
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

    # parse as straight diceroll
    else:
        return "[{}] ".format(calc(text, env))


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # we don't want the bot to reply to music bot
    if message.author.id == 706570555834499153:
        return

    # Obtain variable env for this user
    env = envs.get(str(message.author.id))

    # message of style "= d20+1"
    if message.content.startswith("="):
        try:
            resp = await handle_message_command(message.content[1:], env, message.channel)
        except Exception:
            print(traceback.format_exc())
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
            # Something caused an error, let the user know. Retain full error in logs
            print(traceback.format_exc())
            await message.channel.send(f"{message.author.display_name}: ERROR")


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    for g in client.guilds:
        print(g.name)
        
    print('------')

