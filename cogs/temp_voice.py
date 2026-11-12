import discord
from discord import app_commands
from discord.ext import commands
import db

class TrustSelect(discord.ui.View):
    def __init__(self, vc_id):
        super().__init__(timeout=60)
        self.vc_id = vc_id

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Select a user to trust")
    async def select(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        user = select.values[0]
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc: return await interaction.response.edit_message(content="Channel gone.", view=None)
        await db.add_trusted(vc.id, user.id)
        await vc.set_permissions(user, connect=True)
        await interaction.response.edit_message(content=f"Trusted {user.mention}.", view=None)

class BlockSelect(discord.ui.View):
    def __init__(self, vc_id):
        super().__init__(timeout=60)
        self.vc_id = vc_id

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Select a user to block")
    async def select(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        user = select.values[0]
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc: return await interaction.response.edit_message(content="Channel gone.", view=None)
        await db.add_blocked(vc.id, user.id)
        await vc.set_permissions(user, connect=False)
        if user.voice and user.voice.channel == vc:
            await user.move_to(None)
        await interaction.response.edit_message(content=f"Blocked {user.mention}.", view=None)

class DisconnectSelect(discord.ui.View):
    def __init__(self, vc_id):
        super().__init__(timeout=60)
        self.vc_id = vc_id

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Select a user to disconnect")
    async def select(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        user = select.values[0]
        vc = interaction.guild.get_channel(self.vc_id)
        if user.voice and user.voice.channel == vc:
            await user.move_to(None)
            await interaction.response.edit_message(content=f"Disconnected {user.mention}.", view=None)
        else:
            await interaction.response.edit_message(content="User is not in this channel.", view=None)

class TransferSelect(discord.ui.View):
    def __init__(self, vc_id):
        super().__init__(timeout=60)
        self.vc_id = vc_id

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Select a user to transfer ownership to")
    async def select(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        user = select.values[0]
        vc = interaction.guild.get_channel(self.vc_id)
        await db.update_temp_owner(vc.id, user.id)
        await vc.set_permissions(user, manage_channels=True, connect=True, move_members=True)
        await interaction.response.edit_message(content=f"Transferred ownership to {user.mention}.", view=None)

class RenameModal(discord.ui.Modal, title="Rename Channel"):
    name = discord.ui.TextInput(label="New Name", max_length=100)

    def __init__(self, vc):
        super().__init__()
        self.vc = vc

    async def on_submit(self, interaction: discord.Interaction):
        await self.vc.edit(name=self.name.value)
        await interaction.response.send_message("Renamed.", ephemeral=True)

class VoiceControl(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    def get_vc(self, interaction):
        if interaction.user.voice and interaction.user.voice.channel:
            return interaction.user.voice.channel
        if isinstance(interaction.channel, discord.VoiceChannel):
            return interaction.channel
        return None

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.secondary, emoji="🔒", custom_id="vc_lock", row=0)
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc: return await interaction.response.send_message("Join the VC first.", ephemeral=True)
        owner = await db.get_temp_channel(vc.id)
        if str(interaction.user.id) != owner: return await interaction.response.send_message("Not your channel.", ephemeral=True)
        await vc.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message("Locked.", ephemeral=True)

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.secondary, emoji="🔓", custom_id="vc_unlock", row=0)
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc: return await interaction.response.send_message("Join the VC first.", ephemeral=True)
        owner = await db.get_temp_channel(vc.id)
        if str(interaction.user.id) != owner: return await interaction.response.send_message("Not your channel.", ephemeral=True)
        await vc.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message("Unlocked.", ephemeral=True)

    @discord.ui.button(label="Trust", style=discord.ButtonStyle.success, emoji="🤝", custom_id="vc_trust", row=0)
    async def trust(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc: return await interaction.response.send_message("Join the VC first.", ephemeral=True)
        owner = await db.get_temp_channel(vc.id)
        if str(interaction.user.id) != owner: return await interaction.response.send_message("Not your channel.", ephemeral=True)
        await interaction.response.send_message("Select user:", view=TrustSelect(vc.id), ephemeral=True)

    @discord.ui.button(label="Block", style=discord.ButtonStyle.danger, emoji="⛔", custom_id="vc_block", row=0)
    async def block(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc: return await interaction.response.send_message("Join the VC first.", ephemeral=True)
        owner = await db.get_temp_channel(vc.id)
        if str(interaction.user.id) != owner: return await interaction.response.send_message("Not your channel.", ephemeral=True)
        await interaction.response.send_message("Select user:", view=BlockSelect(vc.id), ephemeral=True)

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.primary, emoji="✏️", custom_id="vc_rename", row=1)
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc: return await interaction.response.send_message("Join the VC first.", ephemeral=True)
        owner = await db.get_temp_channel(vc.id)
        if str(interaction.user.id) != owner: return await interaction.response.send_message("Not your channel.", ephemeral=True)
        await interaction.response.send_modal(RenameModal(vc))

    @discord.ui.button(label="Disconnect", style=discord.ButtonStyle.secondary, emoji="👢", custom_id="vc_disconnect", row=1)
    async def disconnect(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc: return await interaction.response.send_message("Join the VC first.", ephemeral=True)
        owner = await db.get_temp_channel(vc.id)
        if str(interaction.user.id) != owner: return await interaction.response.send_message("Not your channel.", ephemeral=True)
        await interaction.response.send_message("Select user:", view=DisconnectSelect(vc.id), ephemeral=True)

    @discord.ui.button(label="Transfer", style=discord.ButtonStyle.primary, emoji="👑", custom_id="vc_transfer", row=1)
    async def transfer(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc: return await interaction.response.send_message("Join the VC first.", ephemeral=True)
        owner = await db.get_temp_channel(vc.id)
        if str(interaction.user.id) != owner: return await interaction.response.send_message("Not your channel.", ephemeral=True)
        await interaction.response.send_message("Select user:", view=TransferSelect(vc.id), ephemeral=True)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="vc_delete", row=1)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc: return await interaction.response.send_message("Join the VC first.", ephemeral=True)
        owner = await db.get_temp_channel(vc.id)
        if str(interaction.user.id) != owner and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Not your channel.", ephemeral=True)
        await interaction.response.send_message("Deleting...", ephemeral=True)
        await vc.delete()

# THIS WAS MISSING
class VCManageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Manage My VC", style=discord.ButtonStyle.primary, custom_id="manage_vc_btn")
    async def manage(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.response.send_message("You must be in a VC to use this.", ephemeral=True)
        
        vc = interaction.user.voice.channel
        owner = await db.get_temp_channel(vc.id)
        if not owner:
            return await interaction.response.send_message("You are not in a temporary VC.", ephemeral=True)
        if str(interaction.user.id) != owner:
            return await interaction.response.send_message("You do not own this channel.", ephemeral=True)

        await interaction.response.send_message("Your VC control panel:", view=VoiceControl(), ephemeral=True)

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(VoiceControl())
        self.bot.add_view(VCManageView())

    @app_commands.command(name="setup_tempvoice", description="Setup the join-to-create hub")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_tempvoice(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        await db.set_temp_hub(interaction.guild.id, channel.id)
        await interaction.response.send_message(f"Setup in {channel.mention}.", ephemeral=True)

    @app_commands.command(name="setup_vc_panel", description="Setup a text channel to manage your VC")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_vc_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎙️ Voice Control Hub",
            description="Join a temp voice channel, then click the button below to manage it.",
            color=discord.Color.blurple()
        )
        await interaction.channel.send(embed=embed, view=VCManageView())
        await interaction.response.send_message("Panel sent.", ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        if after.channel:
            hub_id = await db.get_temp_hub(member.guild.id)
            if hub_id and str(after.channel.id) == str(hub_id):
                guild = member.guild
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(connect=True),
                    member: discord.PermissionOverwrite(manage_channels=True, connect=True, move_members=True)
                }
                chan = await guild.create_voice_channel(name=f"{member.name}'s channel", category=after.channel.category, overwrites=overwrites)
                await db.add_temp_channel(chan.id, member.id)
                await member.move_to(chan)
                
                embed = discord.Embed(
                    title="🎙️ Voice Control Center",
                    description="Manage your private channel using the buttons below.",
                    color=discord.Color.blurple()
                )
                embed.add_field(name="Lock / Unlock", value="Control who joins.", inline=True)
                embed.add_field(name="Trust / Block", value="Allow or deny specific users.", inline=True)
                embed.add_field(name="Rename / Transfer", value="Change name or give ownership.", inline=True)
                embed.set_footer(text="Channel will be auto-deleted when empty.")
                
                await chan.send(embed=embed, view=VoiceControl())

        if before.channel:
            owner = await db.get_temp_channel(before.channel.id)
            if owner and len(before.channel.members) == 0:
                try:
                    await before.channel.delete()
                except discord.NotFound:
                    pass
                except discord.Forbidden:
                    pass
                finally:
                    await db.clean_vc(before.channel.id)

async def setup(bot):
    await bot.add_cog(TempVoice(bot))