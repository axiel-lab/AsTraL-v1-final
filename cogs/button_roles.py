import discord
from discord import app_commands
from discord.ext import commands
import db
from ui import success_embed, error_embed, main_embed

class RoleButton(discord.ui.Button):
    def __init__(self, role_id, label, emoji):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=f"role_{role_id}")
        self.role_id = role_id
        if emoji: self.emoji = emoji
    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role: return await interaction.response.send_message(embed=error_embed("Role no longer exists."), ephemeral=True)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(embed=error_embed(f"Removed {role.mention}"), ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(embed=success_embed(f"Added {role.mention}"), ephemeral=True)

class DynamicRoleView(discord.ui.View):
    def __init__(self, buttons_data):
        super().__init__(timeout=None)
        for b in buttons_data: self.add_item(RoleButton(int(b[1]), b[3], b[2]))

class ButtonRoles(commands.Cog):
    def __init__(self, bot): self.bot = bot
    async def cog_load(self):
        rows = await db.get_all_button_roles()
        grouped = {}
        for row in rows:
            if row[0] not in grouped: grouped[row[0]] = []
            grouped[row[0]].append(row)
        for mid, buttons in grouped.items(): self.bot.add_view(DynamicRoleView(buttons), message_id=int(mid))

    br_group = app_commands.Group(name="buttonrole", description="Manage button roles")

    @br_group.command(name="create", description="Create a button role panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def br_create(self, interaction: discord.Interaction, title: str, description: str):
        embed = main_embed(title, description)
        msg = await interaction.channel.send(embed=embed)
        await interaction.response.send_message(embed=success_embed(f"Panel created. ID: `{msg.id}`"), ephemeral=True)

    @br_group.command(name="add", description="Add a button to a panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def br_add(self, interaction: discord.Interaction, message_id: str, role: discord.Role, label: str, emoji: str = None):
        try: msg = await interaction.channel.fetch_message(int(message_id))
        except: return await interaction.response.send_message(embed=error_embed("Message not found."), ephemeral=True)
        await db.add_button_role(msg.id, role.id, emoji, label)
        rows = await db.get_button_roles_for_message(msg.id)
        await msg.edit(view=DynamicRoleView(rows))
        self.bot.add_view(DynamicRoleView(rows), message_id=msg.id)
        await interaction.response.send_message(embed=success_embed(f"Button added to `{msg.id}`."), ephemeral=True)

async def setup(bot): await bot.add_cog(ButtonRoles(bot))
