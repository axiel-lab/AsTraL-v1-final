import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import math
from ui import success_embed, error_embed, main_embed
from config import EMOJI_GEAR

class PowerTools(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="steal_emoji", description="Steal an emoji and add it to this server")
    @app_commands.checks.has_permissions(manage_emojis_and_stickers=True)
    async def steal_emoji(self, interaction: discord.Interaction, emoji: str, name: str):
        await interaction.response.defer(ephemeral=True)
        try:
            partial_emoji = discord.PartialEmoji.from_str(emoji)
            if not partial_emoji.id:
                return await interaction.followup.send(embed=error_embed("That is a default emoji, you can't steal it."), ephemeral=True)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(partial_emoji.url) as resp:
                    if resp.status != 200:
                        return await interaction.followup.send(embed=error_embed("Failed to download emoji."), ephemeral=True)
                    image_data = await resp.read()

            new_emoji = await interaction.guild.create_custom_emoji(name=name, image=image_data)
            await interaction.followup.send(embed=success_embed(f"Successfully added {new_emoji} as `:{name}:`"), ephemeral=True)
        except discord.HTTPException:
            await interaction.followup.send(embed=error_embed("Failed to add emoji. (File might be too big or server is full)."), ephemeral=True)

    @app_commands.command(name="steal_sticker", description="Steal a sticker and add it to this server")
    @app_commands.checks.has_permissions(manage_emojis_and_stickers=True)
    async def steal_sticker(self, interaction: discord.Interaction, sticker: discord.StickerItem, name: str):
        await interaction.response.defer(ephemeral=True)
        try:
            sticker_file = await sticker.read()
            await interaction.guild.create_sticker(name=name, description="Stolen sticker", emoji="🎨", file=discord.File(fp=sticker_file, filename="sticker.png"))
            await interaction.followup.send(embed=success_embed(f"Successfully added sticker `{name}`!"), ephemeral=True)
        except Exception as e:
            await interaction.followup.send(embed=error_embed(f"Failed to steal sticker. (File too big or no slots left)."), ephemeral=True)

    @commands.hybrid_command(name="banner", description="Get a user's profile banner")
    async def banner(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        user = await self.bot.fetch_user(member.id)
        if user.banner:
            embed = main_embed(f"{EMOJI_GEAR} {member.name}'s Banner", "")
            embed.set_image(url=user.banner.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=error_embed("This user does not have a profile banner."))

    @commands.hybrid_command(name="serverbanner", description="Get the server's banner")
    async def serverbanner(self, ctx: commands.Context):
        if ctx.guild.banner:
            embed = main_embed(f"{EMOJI_GEAR} {ctx.guild.name}'s Banner", "")
            embed.set_image(url=ctx.guild.banner.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=error_embed("This server does not have a banner."))

    @commands.hybrid_command(name="calc", description="Calculate a math expression")
    async def calc(self, ctx: commands.Context, *, expression: str):
        try:
            allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
            code = compile(expression, "<string>", "eval")
            for name in code.co_names:
                if name not in allowed_names:
                    raise NameError(f"The use of '{name}' is not allowed")
            result = eval(code, {"__builtins__": {}}, allowed_names)
            await ctx.send(embed=main_embed(f"{EMOJI_GEAR} Calculator", f"**Input:** `{expression}`\n**Result:** `{result}`"))
        except Exception:
            await ctx.send(embed=error_embed("Invalid math expression."), ephemeral=True)

async def setup(bot): await bot.add_cog(PowerTools(bot))
