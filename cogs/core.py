import discord
from discord import app_commands
from discord.ext import commands
from config import THEME_COLOR, BOT_NAME, EMOJI_GEAR, EMOJI_BAN, EMOJI_HEART, EMOJI_COIN, EMOJI_STAR

class HelpSelect(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Home", description="Main menu and bot stats", emoji="🏠"),
            discord.SelectOption(label="Admin & Config", description="Setup and server management", emoji=EMOJI_GEAR),
            discord.SelectOption(label="Moderation", description="Kick, Ban, Purge, and Warnings", emoji=EMOJI_BAN),
            discord.SelectOption(label="Community", description="Levels, Marriage, and Birthdays", emoji=EMOJI_HEART),
            discord.SelectOption(label="Utility", description="Info, Reminders, and Tools", emoji=EMOJI_COIN),
            discord.SelectOption(label="Fun & Games", description="Games, Roleplay, and Giveaways", emoji=EMOJI_STAR),
        ]
        super().__init__(placeholder="Select a category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=THEME_COLOR)
        
        if self.values[0] == "Home":
            embed.title = f"{EMOJI_GEAR} {BOT_NAME} | Help Menu"
            embed.description = "Welcome to the help menu. Use the dropdown below to explore my commands."
            embed.add_field(name="Ping", value=f"`{round(self.bot.latency * 1000)}ms`", inline=True)
            embed.add_field(name="Servers", value=f"`{len(self.bot.guilds)}`", inline=True)
            embed.add_field(name="Commands", value=f"`{len(self.bot.tree.get_commands())}` Slash Commands", inline=True)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
        elif self.values[0] == "Admin & Config":
            embed.title = f"{EMOJI_GEAR} Admin & Config"
            embed.description = (
                "`/cc` - Custom Commands setup\n"
                "`/ticket` - Support ticket system\n"
                "`/buttonrole` - Role self-assignment\n"
                "`/setup_honeypot` - Trap channel for compromised accounts\n"
                "`/welcome` - Welcome messages & autorole\n"
                "`/automod` - Anti-spam, links, and caps\n"
                "`/logging` - Message and member logs\n"
                "`/setup_weather` - Hourly weather updates"
            )
            
        elif self.values[0] == "Moderation":
            embed.title = f"{EMOJI_BAN} Moderation"
            embed.description = (
                "`/ban` - Ban a member\n"
                "`/kick` - Kick a member\n"
                "`/purge` - Bulk delete messages\n"
                "`/warn` - Warn a member\n"
                "`/warnings` - View user warnings\n"
                "`/lock` `/unlock` - Channel lockdown\n"
                "`/temprole` - Temporary roles\n"
                "`/note` - Staff notes on users"
            )
            
        elif self.values[0] == "Community":
            embed.title = f"{EMOJI_HEART} Community"
            embed.description = (
                "`/rank` - Check your level\n"
                "`/leaderboard` - Top active users\n"
                "`/marry` `/divorce` `/couple` - Marriage system\n"
                "`/shop` - Buy items\n"
                "`/set_birthday` - Setup birthday announcements\n"
                "`/suggest` - Submit a suggestion\n"
                "`/highlight` - Get pinged for keywords\n"
                "`/afk` - Set your AFK status"
            )
            
        elif self.values[0] == "Utility":
            embed.title = f"{EMOJI_COIN} Utility"
            embed.description = (
                "`/userinfo` - User details\n"
                "`/serverinfo` - Server details\n"
                "`/avatar` - Get user avatars\n"
                "`/remind` - Set a reminder\n"
                "`/translate` - Translate text\n"
                "`/weather` - Check current weather\n"
                "`/snipe` - See recently deleted messages\n"
                "`/ping` - Check bot latency"
            )
            
        elif self.values[0] == "Fun & Games":
            embed.title = f"{EMOJI_STAR} Fun & Games"
            embed.description = (
                "`/gstart` - Start a giveaway\n"
                "`/poll` - Create a button poll\n"
                "`!tictactoe` - Play a game of Tic-Tac-Toe\n"
                "`/slots` - Gamble your coins\n"
                "`/8ball` `/coinflip` `/roll` - Random fun\n"
                "`/hug` `/slap` `/kiss` - Roleplay actions\n"
                "`/quote` - Random server quotes\n"
                "`/counting` - Setup a counting channel"
            )

        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.add_item(HelpSelect(bot))

class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="View all bot commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{EMOJI_GEAR} {BOT_NAME} | Help Menu",
            description="Welcome to the help menu. Use the dropdown below to explore my commands.",
            color=THEME_COLOR
        )
        embed.add_field(name="Ping", value=f"`{round(self.bot.latency * 1000)}ms`", inline=True)
        embed.add_field(name="Servers", value=f"`{len(self.bot.guilds)}`", inline=True)
        embed.add_field(name="Commands", value=f"`{len(self.bot.tree.get_commands())}` Slash Commands", inline=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed, view=HelpView(self.bot), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Core(bot))
