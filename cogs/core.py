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
            embed.add_field(name="Commands", value=f"`{len(self.bot.tree.get_commands())}` Commands", inline=True)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        elif self.values[0] == "Admin & Config":
            embed.title = f"{EMOJI_GEAR} Admin & Config"
            embed.description = (
                "`/set_prefix` - Change bot prefix\n"
                "`/setup_devlogs` - Send console logs to a channel\n"
                "`/ticket_setup` - Setup ticket panels\n"
                "`/buttonrole` - Create self-assign role panels\n"
                "`/setup_honeypot` - Trap compromised accounts\n"
                "`/setup_welcome` - Custom welcome messages\n"
                "`/setup_tempvoice` - Join-to-create VC hub\n"
                "`/voice_panel` - Global VC management panel\n"
                "`/automod` - Configure AutoMod\n"
                "`/logging` - Setup server logs\n"
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
                "`/lock` - Lock current channel\n"
                "`/unlock` - Unlock current channel\n"
                "`/temprole` - Give temporary roles\n"
                "`/note` - Staff notes on users"
            )
        elif self.values[0] == "Community":
            embed.title = f"{EMOJI_HEART} Community"
            embed.description = (
                "`/rank` - Check your level\n"
                "`/leaderboard` - Top active users\n"
                "`/marry` - Propose to someone\n"
                "`/divorce` - End your marriage\n"
                "`/couple` - Check marriage status\n"
                "`/shop` - Buy marriage rings\n"
                "`/daily` - Claim daily coins\n"
                "`/cash` - Check balance\n"
                "`/pay` - Transfer coins\n"
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
                "`/snipe` - See recently deleted messages\n"
                "`/ping` - Check bot latency\n"
                "`/botinfo` - View bot information"
            )
        elif self.values[0] == "Fun & Games":
            embed.title = f"{EMOJI_STAR} Fun & Games"
            embed.description = (
                "`/gstart` - Start a giveaway\n"
                "`/poll` - Create a button poll\n"
                "`/tictactoe` - Play Tic-Tac-Toe\n"
                "`/slots` - Play the slot machine\n"
                "`/cf` - Flip a coin\n"
                "`/8ball` - Ask the magic 8-ball\n"
                "`/roll` - Roll dice\n"
                "`/imagine` - Generate an AI image\n"
                "`/hug` `/slap` `/kiss` - Roleplay actions\n"
                "`/quote` - Random server quotes"
            )

        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.add_item(HelpSelect(bot))

class Core(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="help", description="View all bot commands")
    async def help(self, ctx: commands.Context):
        embed = discord.Embed(
            title=f"{EMOJI_GEAR} {BOT_NAME} | Help Menu",
            description="Welcome to the help menu. Use the dropdown below to explore my commands.",
            color=THEME_COLOR
        )
        embed.add_field(name="Ping", value=f"`{round(self.bot.latency * 1000)}ms`", inline=True)
        embed.add_field(name="Servers", value=f"`{len(self.bot.guilds)}`", inline=True)
        embed.add_field(name="Commands", value=f"`{len(self.bot.tree.get_commands())}` Commands", inline=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        if ctx.interaction:
            await ctx.send(embed=embed, view=HelpView(self.bot), ephemeral=True)
        else:
            await ctx.send(embed=embed, view=HelpView(self.bot))

async def setup(bot): await bot.add_cog(Core(bot))
