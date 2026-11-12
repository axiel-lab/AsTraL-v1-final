import discord
from discord import app_commands
from discord.ext import commands
import db
from config import RESERVED

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    cc_group = app_commands.Group(name="cc", description="Manage custom commands")

    def validate_name(self, name):
        name = name.lower().strip()
        if not name: return "Name can't be empty."
        if " " in name: return "No spaces allowed."
        if len(name) > 32: return "Name too long (max 32 chars)."
        if name in RESERVED: return "That name is reserved."
        return None

    @cc_group.command(name="add", description="Create a custom command")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def cc_add(self, interaction: discord.Interaction, name: str, response: str):
        err = self.validate_name(name)
        if err:
            return await interaction.response.send_message(f"❌ {err}", ephemeral=True)

        name = name.lower().strip()
        if len(response) > 500:
            return await interaction.response.send_message("❌ Max 500 chars.", ephemeral=True)

        if await db.get(interaction.guild.id, name) is not None:
            return await interaction.response.send_message(f"❌ `!{name}` already exists.", ephemeral=True)

        await db.save(interaction.guild.id, name, response, interaction.user.id)
        await interaction.response.send_message(f"✅ Added `!{name}`", ephemeral=True)

    @cc_group.command(name="edit", description="Edit a custom command")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def cc_edit(self, interaction: discord.Interaction, name: str, response: str):
        name = name.lower().strip()
        if await db.get(interaction.guild.id, name) is None:
            return await interaction.response.send_message(f"❌ `!{name}` doesn't exist.", ephemeral=True)

        await db.save(interaction.guild.id, name, response, interaction.user.id)
        await interaction.response.send_message(f"✏️ Updated `!{name}`", ephemeral=True)

    @cc_group.command(name="remove", description="Delete a custom command")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def cc_remove(self, interaction: discord.Interaction, name: str):
        name = name.lower().strip()
        if await db.get(interaction.guild.id, name) is None:
            return await interaction.response.send_message(f"❌ `!{name}` doesn't exist.", ephemeral=True)

        await db.delete(interaction.guild.id, name)
        await interaction.response.send_message(f"🗑️ Removed `!{name}`", ephemeral=True)

    @cc_group.command(name="list", description="List all custom commands")
    async def cc_list(self, interaction: discord.Interaction):
        rows = await db.list_all(interaction.guild.id)
        if not rows:
            return await interaction.response.send_message("No commands setup yet.", ephemeral=True)

        lines = [f"`!{n}` → {r[:60]}" for n, r in rows]
        
        chunks = []
        current = ""
        for line in lines:
            if len(current) + len(line) > 1900:
                chunks.append(current)
                current = ""
            current += line + "\n"
        if current: chunks.append(current)

        await interaction.response.send_message(f"**Commands:**\n{chunks[0]}", ephemeral=True)
        for c in chunks[1:]:
            await interaction.followup.send(c, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild or not msg.content.startswith("!"):
            return

        name = msg.content[1:].split()[0].lower()
        if name in RESERVED:
            return

        resp = await db.get(msg.guild.id, name)
        if resp:
            await msg.channel.send(resp.replace("{user}", msg.author.mention))
            return
            
        await self.bot.process_commands(msg)

async def setup(bot):
    await bot.add_cog(CustomCommands(bot))