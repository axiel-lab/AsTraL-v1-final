import discord
from discord import app_commands
from discord.ext import commands
import db
from config import THEME_COLOR, EMOJI_GEAR, EMOJI_TRASH, EMOJI_INFO
from ui import success_embed, error_embed, main_embed

class CustomCommands(commands.Cog):
    def __init__(self, bot): self.bot = bot

    cc_group = app_commands.Group(name="cc", description="Manage custom commands")

    @cc_group.command(name="add", description="Create a custom command")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def cc_add(self, interaction: discord.Interaction, name: str, response: str):
        name = name.lower().strip()
        if " " in name or len(name) > 32: return await interaction.response.send_message(embed=error_embed("Invalid name or too long."), ephemeral=True)
        if await db.get(interaction.guild.id, name) is not None:
            return await interaction.response.send_message(embed=error_embed(f"`!{name}` already exists."), ephemeral=True)
        await db.save(interaction.guild.id, name, response, interaction.user.id)
        await interaction.response.send_message(embed=success_embed(f"Added `!{name}`"), ephemeral=True)

    @cc_group.command(name="remove", description="Delete a custom command")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def cc_remove(self, interaction: discord.Interaction, name: str):
        name = name.lower().strip()
        if await db.get(interaction.guild.id, name) is None:
            return await interaction.response.send_message(embed=error_embed(f"`!{name}` doesn't exist."), ephemeral=True)
        await db.delete(interaction.guild.id, name)
        await interaction.response.send_message(embed=success_embed(f"{EMOJI_TRASH} Removed `!{name}`"), ephemeral=True)

    @cc_group.command(name="list", description="List all custom commands")
    async def cc_list(self, interaction: discord.Interaction):
        rows = await db.list_all(interaction.guild.id)
        if not rows: return await interaction.response.send_message(embed=info_embed("No commands setup yet."), ephemeral=True)
        desc = "".join(f"`!{n}` → {r[:50]}\n" for n, r in rows)
        await interaction.response.send_message(embed=main_embed(f"{EMOJI_INFO} Custom Commands", desc), ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild or not msg.content.startswith("!"): return
        name = msg.content[1:].split()[0].lower()
        resp = await db.get(msg.guild.id, name)
        if resp: await msg.channel.send(resp.replace("{user}", msg.author.mention))

async def setup(bot): await bot.add_cog(CustomCommands(bot))
