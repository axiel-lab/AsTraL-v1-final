import discord
from discord import app_commands
from discord.ext import commands
import db
import asyncio

async def close_ticket_logic(interaction: discord.Interaction):
    config = await db.get_ticket_config(interaction.guild.id)
    await db.remove_ticket(interaction.channel.id)
    
    if config:
        log_channel = interaction.guild.get_channel(int(config[2]))
        if log_channel:
            embed = discord.Embed(
                title="Ticket Closed", 
                description=f"Channel: `{interaction.channel.name}`\nClosed by: {interaction.user.mention}", 
                color=discord.Color.red()
            )
            await log_channel.send(embed=embed)
    
    await interaction.channel.delete()

class ConfirmCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        
    @discord.ui.button(label="Confirm Close", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing...", ephemeral=True)
        await close_ticket_logic(interaction)
        
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelled.", ephemeral=True)
        self.stop()

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Are you sure you want to close this ticket?", view=ConfirmCloseView(), ephemeral=True)

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.success, custom_id="claim_ticket_btn")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = await db.get_ticket_config(interaction.guild.id)
        if not config:
            return await interaction.response.send_message("Config missing.", ephemeral=True)
            
        staff_role = interaction.guild.get_role(int(config[1]))
        
        if staff_role not in interaction.user.roles and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only staff can claim.", ephemeral=True)

        await interaction.response.send_message(f"🎟️ Ticket claimed by {interaction.user.mention}.")
        await interaction.channel.edit(name=f"claimed-{interaction.channel.name.replace('ticket-', '')}")

class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.blurple, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        config = await db.get_ticket_config(interaction.guild.id)
        if not config:
            return await interaction.followup.send("❌ Ticket system not setup.", ephemeral=True)

        existing_id = await db.get_user_ticket(interaction.guild.id, interaction.user.id)
        if existing_id:
            existing_channel = interaction.guild.get_channel(int(existing_id))
            if existing_channel:
                return await interaction.followup.send(f"❌ You already have a ticket open: <#{existing_id}>", ephemeral=True)
            else:
                # Fix: User manually deleted the channel, clean up DB
                await db.remove_ticket(existing_id)

        cat_id, role_id, log_id = config
        category = interaction.guild.get_channel(int(cat_id))
        staff_role = interaction.guild.get_role(int(role_id))

        if not category or not staff_role:
            return await interaction.followup.send("❌ Invalid config. Contact an admin.", ephemeral=True)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        await db.add_ticket(channel.id, interaction.guild.id, interaction.user.id)
        
        embed = discord.Embed(title="Support Ticket", description="Staff will be with you shortly.", color=discord.Color.blurple())
        
        # Send the control view inside the ticket
        await channel.send(f"{interaction.user.mention} {staff_role.mention}", embed=embed, view=TicketControlView())
        await interaction.followup.send(f"✅ Ticket created: {channel.mention}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(TicketPanelView())
        self.bot.add_view(TicketControlView())

    ticket_group = app_commands.Group(name="ticket", description="Ticket system")

    @ticket_group.command(name="setup", description="Setup the ticket system")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction, category: discord.CategoryChannel, staff_role: discord.Role, log_channel: discord.TextChannel):
        await db.set_ticket_config(interaction.guild.id, category.id, staff_role.id, log_channel.id)
        await interaction.response.send_message("✅ Ticket system configured.", ephemeral=True)

    @ticket_group.command(name="panel", description="Send the ticket creation panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Support Tickets", 
            description="Click the button below to open a support ticket.", 
            color=discord.Color.blurple()
        )
        await interaction.channel.send(embed=embed, view=TicketPanelView())
        await interaction.response.send_message("✅ Panel sent.", ephemeral=True)

    @ticket_group.command(name="close", description="Close the current ticket")
    async def close(self, interaction: discord.Interaction):
        await interaction.response.send_message("Closing ticket...")
        await asyncio.sleep(1)
        await close_ticket_logic(interaction)

async def setup(bot):
    await bot.add_cog(Tickets(bot))