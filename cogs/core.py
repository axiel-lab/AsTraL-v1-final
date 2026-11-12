import discord
from discord import app_commands
from discord.ext import commands
from config import THEME_COLOR, BOT_NAME

class HelpSelect(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Home", description="Main menu", emoji="🏠"),
            discord.SelectOption(label="Admin", description="Server management", emoji="🛠️"),
            discord.SelectOption(label="Moderation", description="Kick, Ban, Purge", emoji="🔨"),
            discord.SelectOption(label="Utility", description="Info and tools", emoji="⚙️"),
            discord.SelectOption(label="Fun & Games", description="Entertainment", emoji="🎮"),
        ]
        super().__init__(placeholder="Select a category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"{BOT_NAME} Help", color=THEME_COLOR)
        
        if self.values[0] == "Home":
            embed.description = "Welcome to the help menu! Use the dropdown below to explore commands."
            embed.add_field(name="Prefix", value="`!` (for custom commands)", inline=True)
            embed.add_field(name="Slash Commands", value="`/`", inline=True)
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
        elif self.values[0] == "Admin":
            embed.description = (
                "`/cc` - Custom Commands\n"
                "`/ticket` - Ticket system setup\n"
                "`/welcome` - Welcome messages\n"
                "`/logging` - Server logs\n"
                "`/automod` - Auto-moderation setup\n"
                "`/buttonrole` - Create role panels\n"
                "`/setup_vc_panel` - Voice control panel\n"
                "`/setup_suggestions` - Suggestion channel"
            )
            
        elif self.values[0] == "Moderation":
            embed.description = (
                "`/purge` - Delete messages\n"
                "`/kick` - Kick a member\n"
                "`/ban` - Ban a member\n"
                "`/warn` - Warn a member\n"
                "`/warnings` - View warnings\n"
                "`/lock` - Lock the channel\n"
                "`/unlock` - Unlock the channel\n"
                "`/temprole` - Give temp roles"
            )
            
        elif self.values[0] == "Utility":
            embed.description = (
                "`/ping` - Bot latency\n"
                "`/serverinfo` - Server details\n"
                "`/userinfo` - User details\n"
                "`/avatar` - Get user avatar\n"
                "`/remind` - Set a reminder\n"
                "`/afk` - Set AFK status\n"
                "`/translate` - Translate text\n"
                "`/weather` - Check the weather\n"
                "`/snipe` - See deleted messages\n"
                "`/highlight` - Keyword notifier\n"
                "`/note` - Staff notes on users"
            )
            
        elif self.values[0] == "Fun & Games":
            embed.description = (
                "`/8ball` - Ask the magic 8-ball\n"
                "`/coinflip` - Heads or tails\n"
                "`/roll` - Roll dice\n"
                "`!tictactoe` - Play Tic-Tac-Toe\n"
                "`/hug` `/slap` `/kiss` - Roleplay\n"
                "`/gstart` - Start a giveaway\n"
                "`/rank` - Check your level\n"
                "`/leaderboard` - Top users"
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
            title=f"{BOT_NAME} Help",
            description="Welcome to the help menu! Use the dropdown below to explore commands.",
            color=THEME_COLOR
        )
        embed.add_field(name="Prefix", value="`!` (for custom commands)", inline=True)
        embed.add_field(name="Slash Commands", value="`/`", inline=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed, view=HelpView(self.bot), ephemeral=True)

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            msg = f"⏳ Slow down! Try again in `{error.retry_after:.2f}s`."
        elif isinstance(error, app_commands.MissingPermissions):
            msg = "❌ You don't have permission to use this command."
        elif isinstance(error, app_commands.BotMissingPermissions):
            msg = "❌ I don't have the required permissions to do that."
        else:
            msg = "❌ An unexpected error occurred. Please try again later."
            print(f"Error: {error}")

        embed = discord.Embed(description=msg, color=discord.Color.red())
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            pass

async def setup(bot):
    await bot.add_cog(Core(bot))