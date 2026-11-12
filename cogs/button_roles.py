import discord
from discord import app_commands
from discord.ext import commands
import db

class RoleButton(discord.ui.Button):
    def __init__(self, role_id, label, emoji):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=f"role_{role_id}")
        self.role_id = role_id
        if emoji:
            self.emoji = emoji

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message("Role no longer exists.", ephemeral=True)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Removed {role.mention}", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Added {role.mention}", ephemeral=True)

class DynamicRoleView(discord.ui.View):
    def __init__(self, buttons_data):
        super().__init__(timeout=None)
        for b in buttons_data:
            self.add_item(RoleButton(int(b[1]), b[3], b[2]))

class RolePanelModal(discord.ui.Modal, title="Panel Details"):
    p_title = discord.ui.TextInput(label="Panel Title", placeholder="Choose your roles...", max_length=100)
    p_desc = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph, placeholder="Select your roles below.", max_length=500)

    def __init__(self, roles):
        super().__init__()
        self.roles = roles

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title=self.p_title.value, 
            description=self.p_desc.value, 
            color=discord.Color.blurple()
        )
        msg = await interaction.channel.send(embed=embed)
        
        buttons_data = []
        for role in self.roles:
            emoji_val = role.unicode_emoji if hasattr(role, 'unicode_emoji') else None
            await db.add_button_role(msg.id, role.id, emoji_val, role.name)
            buttons_data.append((msg.id, str(role.id), emoji_val, role.name))
            
        view = DynamicRoleView(buttons_data)
        await msg.edit(view=view)
        interaction.client.add_view(view, message_id=msg.id)
        
        await interaction.followup.send("✅ Panel created!", ephemeral=True)

class RoleSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.selected_roles = []

    @discord.ui.select(cls=discord.ui.RoleSelect, placeholder="Select up to 25 roles...", min_values=1, max_values=25)
    async def role_select(self, interaction: discord.Interaction, select: discord.ui.RoleSelect):
        self.selected_roles = select.values
        await interaction.response.defer()

    @discord.ui.button(label="Next: Set Title & Description", style=discord.ButtonStyle.primary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected_roles:
            return await interaction.response.send_message("Please select at least one role first.", ephemeral=True)
        await interaction.response.send_modal(RolePanelModal(self.selected_roles))

class ButtonRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        rows = await db.get_all_button_roles()
        grouped = {}
        for row in rows:
            mid = row[0]
            if mid not in grouped:
                grouped[mid] = []
            grouped[mid].append(row)

        for mid, buttons in grouped.items():
            self.bot.add_view(DynamicRoleView(buttons), message_id=int(mid))

    br_group = app_commands.Group(name="buttonrole", description="Manage button roles")

    @br_group.command(name="create", description="Create a professional role panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def br_create(self, interaction: discord.Interaction):
        view = RoleSetupView()
        await interaction.response.send_message(
            "Select the roles you want to include in the panel, then click **Next**.", 
            view=view, 
            ephemeral=True
        )

    @br_group.command(name="add", description="Add a single button to an existing panel (with custom emoji)")
    @app_commands.checks.has_permissions(administrator=True)
    async def br_add(self, interaction: discord.Interaction, message_id: str, role: discord.Role, label: str, emoji: str = None):
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
        except:
            return await interaction.response.send_message("Message not found in this channel.", ephemeral=True)

        await db.add_button_role(msg.id, role.id, emoji, label)
        
        rows = await db.get_button_roles_for_message(msg.id)
        view = DynamicRoleView(rows)
        await msg.edit(view=view)
        
        self.bot.add_view(view, message_id=msg.id)
        await interaction.response.send_message(f"✅ Button added to message `{msg.id}`.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ButtonRoles(bot))