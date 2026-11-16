import discord
from discord import app_commands
from discord.ext import commands
import db
from config import THEME_COLOR, EMOJI_INFO, EMOJI_TRASH
from ui import success_embed, error_embed, main_embed

class StaffNotes(commands.Cog):
    def __init__(self, bot): self.bot = bot

    note_group = app_commands.Group(name="note", description="Staff notes on users")

    @note_group.command(name="add", description="Add a staff note to a user")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def note_add(self, interaction: discord.Interaction, user: discord.User, text: str):
        await db.add_note(interaction.guild.id, user.id, interaction.user.id, text)
        await interaction.response.send_message(embed=success_embed(f"Note added to {user.name}."), ephemeral=True)

    @note_group.command(name="view", description="View staff notes for a user")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def note_view(self, interaction: discord.Interaction, user: discord.User):
        notes = await db.get_notes(interaction.guild.id, user.id)
        if not notes: return await interaction.response.send_message(embed=error_embed(f"No notes found for {user.name}."), ephemeral=True)
        desc = "".join(f"**ID: {nid}** | By <@{author}>\n{text}\n\n" for nid, author, text in notes)
        await interaction.response.send_message(embed=main_embed(f"{EMOJI_INFO} Staff Notes: {user.name}", desc), ephemeral=True)

    @note_group.command(name="remove", description="Remove a staff note by ID")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def note_remove(self, interaction: discord.Interaction, note_id: int):
        await db.delete_note(note_id)
        await interaction.response.send_message(embed=success_embed(f"{EMOJI_TRASH} Note `{note_id}` deleted."), ephemeral=True)

async def setup(bot): await bot.add_cog(StaffNotes(bot))
