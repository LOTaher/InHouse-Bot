import discord
from discord.ext import commands
from typing import Literal
import json


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned, intents = discord.Intents.default())
        self.synced = False 
    
        self.cogslist = ['cogs.inhouse', 'cogs.profile', 'cogs.leaderboard']

    async def setup_hook(self):
        for ext in self.cogslist:
            await self.load_extension(ext)

    async def on_ready(self):
        print(f"Logged in as {self.user}.")
        await self.tree.sync()
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Church Customs'))

with open("config.json", "r") as f:
    data = json.load(f)
    TOKEN = data['TOKEN']

client = Client()

client.run(TOKEN)