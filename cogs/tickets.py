import discord
from discord import app_commands
from discord.ext import commands
import db
import asyncio
from config import THEME_COLOR, EMOJI_TICKET, EMOJI_SUCCESS, EMOJI_ERROR
from ui import success_embed, error_embed

class VoiceControl(discord.ui.View): # Using your existing view logic
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=success_embed("Closing ticket in 5 seconds..."))
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketPanelView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.blurple, emoji=EMOJI_TICKET)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        config = await db.get_ticket_config(interaction.guild.id)
        if not config: return await interaction.followup.send(embed=error_embed("Ticket system not setup."), ephemeral=True)

        existing = await db.get_user_ticket(interaction.guild.id, interaction.user.id)
        if existing:
            return await interaction.followup.send(embed=error_embed(f"You already have a ticket: <#{existing}>"), ephemeral=True)

        cat_id, role_id, log_id = config
        category, staff_role = interaction.guild.get_channel(int(cat_id)), interaction.guild.get_role(int(role_id))

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        channel = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", category=category, overwrites=overwrites)
        await db.add_ticket(channel.id, interaction.guild.id, interaction.user.id)
        
        embed = discord.Embed(title=f"{EMOJI_TICKET} Support Ticket", description="Staff will be with you shortly.", color=THEME_COLOR)
        await channel.send(f"{interaction.user.mention} {staff_role.mention}", embed=embed, view=VoiceControl())
        await interaction.followup.send(embed=success_embed(f"Ticket created: {channel.mention}"), ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="ticket_panel", description="Send the ticket creation panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"{EMOJI_TICKET} Support Tickets", description="Click the button below to open a ticket.", color=THEME_COLOR)
        await interaction.channel.send(embed=embed, view=TicketPanelView())
        await interaction.response.send_message(embed=success_embed("Panel sent."), ephemeral=True)

    @app_commands.command(name="ticket_setup", description="Setup ticket category, role, and logs")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction, category: discord.CategoryChannel, staff_role: discord.Role, log_channel: discord.TextChannel):
        await db.set_ticket_config(interaction.guild.id, category.id, staff_role.id, log_channel.id)
        await interaction.response.send_message(embed=success_embed("Ticket system configured."), ephemeral=True)

async def setup(bot): await bot.add_cog(Tickets(bot))
