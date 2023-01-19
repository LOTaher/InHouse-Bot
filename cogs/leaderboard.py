import discord
from discord.ext import commands
from discord import app_commands, utils
import pymongo
from pymongo import MongoClient
from discord.ui import Button, View
import json

with open("config.json", "r") as f:
    data = json.load(f)
    DATABASE = data['DATABASE']

cluster = MongoClient(DATABASE)
db = cluster['Wins']
collection = db['winCounter']

class Leaderboard(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name = 'leaderboard', description = 'Check out the Church Discord custom win leaderboard') # Change the command description. Include your own server instead.
    async def lb(self, interaction: discord.Interaction):
        rankings = collection.find().sort("wins", -1)
        i = 1
        embed = discord.Embed(title = f"Wins Leaderboard")
        win_str = ""
        emotes = ["🥇", "🥈", "🥉"]
        for x in rankings:
            user_wins = x["wins"]
            if i < 4: 
                win_str += f"{emotes[i-1]} <@{x['_id']}>     |     {user_wins} 🏆\n"
            else:
                win_str += f"{i}. <@{x['_id']}>     |     {user_wins} 🏆\n"               
            if i > 9:
                break
            i += 1
        embed.add_field(name=f"Top 10:", value=win_str, inline=False)
        embed.set_thumbnail(url=interaction.guild.icon.url)
        await interaction.response.send_message(embed=embed)

async def setup(client:commands.Bot):
    await client.add_cog(Leaderboard(client))