import discord
from discord import app_commands
from discord.ext import commands
import db
import asyncio
from config import THEME_COLOR, EMOJI_TICKET, EMOJI_SUCCESS, EMOJI_ERROR
from ui import success_embed, error_embed, main_embed

class CloseButton(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=success_embed("Closing ticket in 5 seconds..."))
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketButton(discord.ui.Button):
    def __init__(self, panel_name, label):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=f"ticket_{panel_name}")
        self.panel_name = panel_name

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        config = await db.get_ticket_config(interaction.guild.id, self.panel_name)
        if not config:
            return await interaction.followup.send(embed=error_embed(f"Panel `{self.panel_name}` is not setup correctly."), ephemeral=True)

        existing = await db.get_user_ticket(interaction.guild.id, interaction.user.id)
        if existing:
            return await interaction.followup.send(embed=error_embed(f"You already have a ticket open: <#{existing}>"), ephemeral=True)

        cat_id, role_id, log_id = config
        category = interaction.guild.get_channel(int(cat_id))
        staff_role = interaction.guild.get_role(int(role_id))

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        channel = await interaction.guild.create_text_channel(
            name=f"{self.panel_name}-{interaction.user.name}", 
            category=category, 
            overwrites=overwrites
        )
        
        await db.add_ticket(channel.id, interaction.guild.id, interaction.user.id)
        
        embed = main_embed(f"{EMOJI_TICKET} {self.panel_name.capitalize()} Ticket", "Staff will be with you shortly.")
        await channel.send(f"{interaction.user.mention} {staff_role.mention}", embed=embed, view=CloseButton())
        await interaction.followup.send(embed=success_embed(f"Ticket created: {channel.mention}"), ephemeral=True)

class DynamicPanelView(discord.ui.View):
    def __init__(self, panel_name, label):
        super().__init__(timeout=None)
        self.add_item(TicketButton(panel_name, label))

class Tickets(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="ticket_setup", description="Setup a specific ticket panel")
    @app_commands.describe(
        panel_name="Unique ID for this panel (e.g., support, bug, apply)",
        category="The Discord category where tickets will be created",
        staff_role="The role that can see the tickets",
        log_channel="Where transcript logs go"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction, panel_name: str, category: discord.CategoryChannel, staff_role: discord.Role, log_channel: discord.TextChannel):
        await db.set_ticket_config(interaction.guild.id, panel_name, category.id, staff_role.id, log_channel.id)
        await interaction.response.send_message(embed=success_embed(f"Ticket panel `{panel_name}` configured."), ephemeral=True)

    @app_commands.command(name="ticket_panel", description="Send a ticket panel to the channel")
    @app_commands.describe(panel_name="Must match the name you used in /ticket_setup", button_label="What the button should say")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction, panel_name: str, button_label: str):
        config = await db.get_ticket_config(interaction.guild.id, panel_name)
        if not config:
            return await interaction.response.send_message(embed=error_embed(f"Setup `{panel_name}` first using `/ticket_setup`."), ephemeral=True)

        embed = main_embed(f"{EMOJI_TICKET} {button_label}", "Click the button below to open a ticket.")
        await interaction.channel.send(embed=embed, view=DynamicPanelView(panel_name, button_label))
        await interaction.response.send_message(embed=success_embed("Panel sent."), ephemeral=True)

async def setup(bot): await bot.add_cog(Tickets(bot))
