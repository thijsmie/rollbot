import discord


intents = discord.Intents.default() 
bot = discord.AutoShardedClient(intents=intents)
tree = discord.app_commands.CommandTree(bot)
