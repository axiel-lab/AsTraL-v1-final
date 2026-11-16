import discord
from discord import app_commands
from discord.ext import commands
from config import THEME_COLOR, BOT_NAME, EMOJI_GEAR, EMOJI_BAN, EMOJI_HEART, EMOJI_COIN, EMOJI_STAR
from ui import success_embed, error_embed

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
            embed.description = "`/set_prefix` • `/setup_devlogs` • `/ticket_setup` • `/buttonrole` • `/setup_honeypot` • `/welcome` • `/automod` • `/logging` • `/setup_weather`"
            
        elif self.values[0] == "Moderation":
            embed.title = f"{EMOJI_BAN} Moderation"
            embed.description = "`/ban` • `/kick` • `/purge` • `/warn` • `/warnings` • `/lock` • `/unlock` • `/temprole` • `/note`"
            
        elif self.values[0] == "Community":
            embed.title = f"{EMOJI_HEART} Community"
            embed.description = "`/rank` • `/leaderboard` • `/marry` • `/divorce` • `/couple` • `/shop` • `/daily` • `/balance` • `/set_birthday` • `/suggest` • `/highlight` • `/afk`"
            
        elif self.values[0] == "Utility":
            embed.title = f"{EMOJI_COIN} Utility"
            embed.description = "`/userinfo` • `/serverinfo` • `/avatar` • `/remind` • `/translate` • `/snipe` • `/ping`"
            
        elif self.values[0] == "Fun & Games":
            embed.title = f"{EMOJI_STAR} Fun & Games"
            embed.description = "`/gstart` • `/poll` • `/tictactoe` • `/slots` • `/cf` • `/8ball` • `/coinflip` • `/roll` • `/imagine` • `/hug` • `/slap` • `/kiss` • `/quote`"

        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.add_item(HelpSelect(bot))

class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="View all bot commands")
    async def help(self, ctx: commands.Context):
        embed = discord.Embed(
            title=f"{EMOJI_GEAR} {BOT_NAME} | Help Menu",
            description="Welcome to the help menu. Use the dropdown below to explore my commands.",
            color=THEME_COLOR
        )
        embed.add_field(name="Ping", value=f"`{round(self.bot.latency * 1000)}ms`", inline=True)
        embed.add_field(name="Servers", value=f"`{len(self.bot.guilds)}`", inline=True)
        embed.add_field(name="Commands", value=f"`{len(self.bot.tree.get_commands())}` Slash Commands", inline=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # ephemeral=True only works for slash commands
        if ctx.interaction:
            await ctx.send(embed=embed, view=HelpView(self.bot), ephemeral=True)
        else:
            await ctx.send(embed=embed, view=HelpView(self.bot))

async def setup(bot):
    await bot.add_cog(Core(bot))
