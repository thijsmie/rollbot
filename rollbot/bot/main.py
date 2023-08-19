import discord
from discord.ext.commands import Context


bot = discord.AutoShardedBot()
from . import commands
from . import events
