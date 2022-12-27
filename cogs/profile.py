import discord
from discord.ext import commands
from discord import app_commands, utils
import pymongo
from pymongo import MongoClient
from discord.ui import Button, View
import json

with open("config.json", "r") as f:
    data = json.load(f)
    DATABASE = data["DATABASE"]

cluster = MongoClient(DATABASE)
db = cluster['Wins']
collection = db['winCounter']

class Profile(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name = 'profile', description = 'View your own Church customs profile') # Change the command description. Include your own server instead.
    async def custom(self, interaction: discord.Interaction, user: discord.Member = None):

            user = user if user is not None else interaction.user
            myquery = { "_id": str(user.id) }
            if (collection.count_documents(myquery) == 0):
                embed = discord.Embed(title=f"{user.display_name}'s Profile", color=user.color)
                embed.add_field(name="Wins", value="0 🏆", inline=False) 
                embed.add_field(name="Games Played", value="0", inline=False)
                embed.add_field(name="Winrate", value="N/A", inline=False)
                embed.set_thumbnail(url=user.display_avatar.url) 

            else:
                query = { "_id": str(user.id) }
                dbresult = collection.find(query)
                for result in dbresult:
                    wins = result['wins']
                    losses = result['losses']
                embed = discord.Embed(title=f"{user.display_name}'s Profile", color=user.color)
                embed.add_field(name="Wins", value=f"{wins} 🏆", inline=False) 
                embed.add_field(name="Games Played", value=str(wins + losses), inline=False)
                embed.add_field(name="Winrate", value=str(int((wins / (wins + losses)) * 100)) + "%" , inline=False) 
                embed.set_thumbnail(url=user.display_avatar.url) 
                
            await interaction.response.send_message(embed=embed)

async def setup(client:commands.Bot):
    await client.add_cog(Profile(client))