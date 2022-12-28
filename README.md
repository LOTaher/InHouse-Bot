# About InHouse-Bot
A bot to organize a 5v5 premade game within your Discord community!

Features include:

`/custom` - Setup the inhouse game with an interactive embed.

`/profile` - Displays win count, games played, and win rate.

`/leaderboard` - The top ten server members with the highest win count.


### Invite
This bot does not have a public invite link. If you really want to run an instance of this bot and host it yourself, the requirements are:
* Python 3.8 or higher
* Discord.py (https://github.com/Rapptz/discord.py)
* A bot application (https://discordapp.com/developers/applications/me)

You must also create a `config.json` file in the main directory. You can use this template:
```javascript
{
    "TOKEN": "", // Bot Token
    "DATABASE": "", // MongoDB URI 
    "MODROLE": "", // Moderator Role Name or ID
    "OWNERID": "", // Your Discord ID
    "DEVROLE": "" // Developer (Mod+ / Admin) Role Name or ID
    "LOGCHANNEL":  // Log Channel ID | This should not be a string
}
```
This bot was created and designed to be used in a single server. 

If you're new to hosting bots, I recommend you read up on [jagrosh's hosting article in the JMusicBot Wiki](https://jmusicbot.com/hosting/)

### Extra Note
Welcome to my first repository! If you have any questions join my [discord](https://discord.gg/UQqJGH8J3Z) community.


###### Special thanks to Anulot for carrying a lot of the weight on this one!




