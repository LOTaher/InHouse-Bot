import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal
from discord.ui import Button, View
import pymongo
from pymongo import MongoClient
import json
import re

with open("config.json", "r") as f:
    data = json.load(f)
    MODROLE = data['MODROLE']
    DEVROLE = data['DEVROLE']
    DATABASE = data["DATABASE"]
    LOGCHANNEL = data["LOGCHANNEL"]

cluster = MongoClient(DATABASE)
db = cluster['Wins']
collection = db['winCounter']

class Menu(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    async def addplayer(self, team, interaction): #Team 1 is 0, Team 2 is 1
        embed_dict = interaction.message.embeds[0].to_dict()
        for field in embed_dict['fields']:
            if str(interaction.user.id) in field['value']: 
                return await interaction.response.send_message("You are already on a team", ephemeral=True)

        player = embed_dict['fields'][team]
        player_index = player['value'].index('-')
        player_string = player['value'][:player_index] + interaction.user.mention + player['value'][player_index + 1:]
        new_embed = interaction.message.embeds[0]
        new_embed.set_field_at(index = team, name = player['name'], value = player_string, inline = player['inline'])
        await interaction.message.edit(content = interaction.message.content, embed = new_embed)
        await interaction.response.send_message(f"Successfully added to Team {team + 1}!", ephemeral=True) 

    @discord.ui.button(label="Team 1", style=discord.ButtonStyle.blurple, emoji="⚔️")
    async def teamone(self, interaction: discord.Interaction, button: discord.ui.Button):
        return await self.addplayer(0, interaction)

    @discord.ui.button(label="Team 2", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def teamtwo(self, interaction: discord.Interaction, button: discord.ui.Button):
        return await self.addplayer(1, interaction)
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=1054481046864941077)
        if role in interaction.user.roles:

            options = [
            discord.SelectOption(label="⚔️ Team 1", value="⚔️ Team 1"),
            discord.SelectOption(label="⚔️ Team 2", value="⚔️ Team 2")
            ]
            select = Select(options=options)
            view_select = discord.ui.View()
            view_select.add_item(select)

            await interaction.response.edit_message(view=view_select)
        else:
            await interaction.response.send_message(f"{interaction.user.mention} only Laith, John and Victor are allowed to confirm the setup.", ephemeral=True)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name=MODROLE)
        if role in interaction.user.roles:
            await interaction.response.defer()
            await interaction.followup.send(f"{interaction.user.mention} canceled the setup.")
            await interaction.delete_original_response()
        else:
            interaction.response.send_message(f"{interaction.user.mention} only Saints are allowed to cancel the setup.", ephemeral=True)

class Select(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Choose a winner", custom_id="id", options=options, max_values=1)

    async def call_loser(self, team, interaction):
        embed_dict = interaction.message.embeds[0].to_dict()
        loser_string = json.dumps(embed_dict['fields'][team]['value'])
        losers = await self.format_players(loser_string)
        return losers

    async def call_winner(self, team, interaction):
        embed_dict = interaction.message.embeds[0].to_dict()
        winner_string = json.dumps(embed_dict['fields'][team]['value'])
        winners = await self.format_players(winner_string)
        return winners

    async def format_players(self, players_str):
        players_str = players_str.replace('>','')
        players_str = players_str.replace('\\n','')
        players_str = players_str.replace('-', '')
        players_str = players_str.replace('"', '')       
        players = players_str.split('<@')
        players.pop(0) # Remove the nothing part
        return players

    async def log_game(self, team, winners, losers, author, guild):
        channel = discord.utils.get(guild.channels, id = LOGCHANNEL)
        await channel.send(f"**Game results**:\n`Team 1:`\n{winners}\n`Team 2:`\n{losers}\n**Winning Team**: {team}\n**Game ended by**: {author.display_name}")

    async def callback(self, interaction: discord.Interaction):
        winners = await self.call_winner(0 if "⚔️ Team 1" in self.values else 1, interaction)
        embed_dict = interaction.message.embeds[0].to_dict()
        await self.log_game(self.values[0], embed_dict['fields'][0]['value'], embed_dict['fields'][1]['value'], interaction.user, interaction.guild)
        win_string = ""
        for winner in winners:
            win_string += f"<@{winner}>\n"
            await self.add_win(winner)
        losers = await self.call_loser(1 if "⚔️ Team 1" in self.values else 0, interaction)
        for loser in losers:
            await self.add_loss(loser)

        embed = discord.Embed(title="Congratulations to the winners!", description= "Added +1 🏆 to each member of the winning team's profile")
        embed.add_field(name = self.values[0], value = win_string )

        await interaction.message.edit(embed=embed, view=None)
        
        await interaction.response.send_message(f"Game ended successfully! ", ephemeral=True)

    async def add_win(self, winner):
            myquery = { "_id": winner }
            if (collection.count_documents(myquery) == 0):
                post = { "_id": winner, "wins": 1, "losses": 0 }
                collection.insert_one(post)
            else:
                query = { "_id": winner }
                user = collection.find(query)
                for result in user:
                    wins = result["wins"]
                    losses = result["losses"]
                wins = wins + 1
                filter = {"_id": winner}
                update = {"$set": {"wins": wins}}
                losses = losses
                collection.update_one(filter, update)
    
    async def add_loss(self, loser):
            myquery = { "_id": loser }
            if (collection.count_documents(myquery) == 0):
                post = { "_id": loser, "wins": 0, "losses": 1 }
                collection.insert_one(post)
            else:
                query = { "_id": loser }
                user = collection.find(query)
                for result in user:
                    losses = result["losses"]
                    wins = result["wins"]
                losses = losses + 1
                filter = { "_id": loser}
                update = { "$set": { "losses": losses }}
                wins = wins
                collection.update_one(filter, update)        

class InHouse(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name = 'custom', description = 'Request to begin a custom in the Church Discord')
    async def custom(self, interaction: discord.Interaction):

        embed = discord.Embed(title=f"Summoner's Rift Custom Setup", description="Select which team you would like to join by pressing either button.")
        embed.add_field(name="Team 1 ⚔️", value="-\n-\n-\n-\n-", inline=True)
        embed.add_field(name="Team 2 ⚔️", value="-\n-\n-\n-\n-", inline=True)
        
        await interaction.response.send_message(embed=embed, view=Menu())

async def setup(client:commands.Bot):
    await client.add_cog(InHouse(client))