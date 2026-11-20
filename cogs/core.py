import discord
from discord.ext import commands
import time
from config import THEME_COLOR, BOT_NAME, EMOJI_GEAR, EMOJI_BAN, EMOJI_HEART, EMOJI_COIN, EMOJI_STAR

class HelpSelect(discord.ui.Select):
    def __init__(self, bot, start_time):
        self.bot = bot
        self.start_time = start_time
        options = [
            discord.SelectOption(label="Home", description="Bot stats and info", emoji="🏠"),
            discord.SelectOption(label="Admin & Config", description="Server setup and logs", emoji=EMOJI_GEAR),
            discord.SelectOption(label="Moderation", description="Kick, Ban, and Warnings", emoji=EMOJI_BAN),
            discord.SelectOption(label="Economy & Levels", description="Cash, Ranks, and Marriage", emoji=EMOJI_HEART),
            discord.SelectOption(label="Utility", description="Info, Tools, and Reminders", emoji=EMOJI_COIN),
            discord.SelectOption(label="Fun & Games", description="Casino, AI, and Roleplay", emoji=EMOJI_STAR),
        ]
        super().__init__(placeholder="Select a category to manage...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=THEME_COLOR)
        
        if self.values[0] == "Home":
            uptime = int(time.time() - self.start_time)
            hours, remainder = divmod(uptime, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            embed.title = f"{EMOJI_GEAR} {BOT_NAME} | Help Menu"
            embed.description = "Welcome to the control center. Use the dropdown menu to explore commands."
            embed.add_field(name="Ping", value=f"`{round(self.bot.latency * 1000)}ms`", inline=True)
            embed.add_field(name="Servers", value=f"`{len(self.bot.guilds)}`", inline=True)
            embed.add_field(name="Uptime", value=f"`{hours}h {minutes}m {seconds}s`", inline=True)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
        elif self.values[0] == "Admin & Config":
            embed.title = f"{EMOJI_GEAR} Admin & Config"
            embed.description = "Manage server settings and bot configurations."
            embed.add_field(name="Setup", value="`/set_prefix` `/setup_devlogs` `/setup_weather`", inline=False)
            embed.add_field(name="Security", value="`/automod` `/setup_honeypot` `/logging`", inline=False)
            embed.add_field(name="Modules", value="`/ticket_setup` `/buttonrole` `/setup_welcome` `/setup_tempvoice` `/voice_panel`", inline=False)
            
        elif self.values[0] == "Moderation":
            embed.title = f"{EMOJI_BAN} Moderation"
            embed.description = "Keep your server safe and clean."
            embed.add_field(name="Actions", value="`/ban` `/kick` `/warn` `/purge`", inline=False)
            embed.add_field(name="Utilities", value="`/warnings` `/lock` `/unlock` `/temprole` `/note`", inline=False)
            
        elif self.values[0] == "Economy & Levels":
            embed.title = f"{EMOJI_HEART} Economy & Levels"
            embed.description = "The community systems."
            embed.add_field(name="Economy", value="`/cash` `/daily` `/pay` `/shop`", inline=False)
            embed.add_field(name="Gambling", value="`/cf` `/slots`", inline=False)
            embed.add_field(name="Community", value="`/rank` `/leaderboard` `/marry` `/divorce` `/couple`", inline=False)
            
        elif self.values[0] == "Utility":
            embed.title = f"{EMOJI_COIN} Utility"
            embed.description = "Useful tools and information."
            embed.add_field(name="Info", value="`/userinfo` `/serverinfo` `/avatar` `/botinfo` `/ping`", inline=False)
            embed.add_field(name="Tools", value="`/remind` `/translate` `/snipe` `/highlight` `/afk`", inline=False)
            
        elif self.values[0] == "Fun & Games":
            embed.title = f"{EMOJI_STAR} Fun & Games"
            embed.description = "Entertainment and interactions."
            embed.add_field(name="Games", value="`/tictactoe` `/poll` `/gstart`", inline=False)
            embed.add_field(name="Roleplay", value="`/hug` `/slap` `/kiss` `/8ball` `/roll`", inline=False)
            embed.add_field(name="AI", value="`/imagine`", inline=False)

        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self, bot, start_time):
        super().__init__(timeout=180)
        self.add_item(HelpSelect(bot, start_time))

class Core(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot
        self.start_time = time.time()

    @commands.hybrid_command(name="help", description="View all bot commands")
    async def help(self, ctx: commands.Context):
        uptime = int(time.time() - self.start_time)
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed(
            title=f"{EMOJI_GEAR} {BOT_NAME} | Help Menu",
            description="Welcome to the control center. Use the dropdown menu to explore commands.",
            color=THEME_COLOR
        )
        embed.add_field(name="Ping", value=f"`{round(self.bot.latency * 1000)}ms`", inline=True)
        embed.add_field(name="Servers", value=f"`{len(self.bot.guilds)}`", inline=True)
        embed.add_field(name="Uptime", value=f"`{hours}h {minutes}m {seconds}s`", inline=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        view = HelpView(self.bot, self.start_time)
        
        if ctx.interaction:
            await ctx.send(embed=embed, view=view, ephemeral=True)
        else:
            await ctx.send(embed=embed, view=view)

async def setup(bot): 
    await bot.add_cog(Core(bot))
