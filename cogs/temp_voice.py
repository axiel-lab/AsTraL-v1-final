import discord
from discord.ext import commands
import db
from config import (
    EMOJI_LOCK, EMOJI_UNLOCK, EMOJI_TRASH, EMOJI_VOICE, 
    EMOJI_HEART, EMOJI_SUCCESS, EMOJI_ERROR, EMOJI_GEAR, EMOJI_WARNING
)
from ui import success_embed, error_embed, main_embed

# --- Modals ---
class RenameModal(discord.ui.Modal, title="Rename Channel"):
    name = discord.ui.TextInput(label="New Name", placeholder="Enter new channel name...", max_length=100)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.channel.edit(name=self.name.value)
        await db.set_temp_voice_name(interaction.channel.id, self.name.value)
        await interaction.response.send_message(embed=success_embed("Channel renamed and saved."), ephemeral=True)

class LimitModal(discord.ui.Modal, title="Set User Limit"):
    limit = discord.ui.TextInput(label="User Limit (0-99)", placeholder="0 for unlimited", max_length=2)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.limit.value)
            await interaction.channel.edit(user_limit=amount)
            await interaction.response.send_message(embed=success_embed(f"Limit set to {amount}."), ephemeral=True)
        except ValueError:
            await interaction.response.send_message(embed=error_embed("Invalid number."), ephemeral=True)

# --- Select Menus ---
class TrustSelect(discord.ui.View):
    def __init__(self, vc_id):
        super().__init__(timeout=60)
        self.vc_id = vc_id
    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Select a user to trust")
    async def select(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        user = select.values[0]
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc: return
        await db.add_trusted(vc.id, user.id)
        await vc.set_permissions(user, connect=True)
        await interaction.response.edit_message(embed=success_embed(f"Trusted {user.mention}."), view=None)

class BlockSelect(discord.ui.View):
    def __init__(self, vc_id):
        super().__init__(timeout=60)
        self.vc_id = vc_id
    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Select a user to block")
    async def select(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        user = select.values[0]
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc: return
        await db.add_blocked(vc.id, user.id)
        await vc.set_permissions(user, connect=False)
        if user.voice and user.voice.channel == vc: await user.move_to(None)
        await interaction.response.edit_message(embed=success_embed(f"Blocked {user.mention}."), view=None)

class KickSelect(discord.ui.View):
    def __init__(self, vc_id):
        super().__init__(timeout=60)
        self.vc_id = vc_id
    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Select a user to kick")
    async def select(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        user = select.values[0]
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc: return
        if user.voice and user.voice.channel == vc:
            await user.move_to(None)
            await interaction.response.edit_message(embed=success_embed(f"Kicked {user.mention}."), view=None)
        else:
            await interaction.response.edit_message(embed=error_embed("User not in this channel."), view=None)

class TransferSelect(discord.ui.View):
    def __init__(self, vc_id):
        super().__init__(timeout=60)
        self.vc_id = vc_id
    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Select a user to transfer ownership")
    async def select(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        user = select.values[0]
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc: return
        await db.update_temp_owner(vc.id, user.id)
        await vc.set_permissions(user, manage_channels=True, connect=True, move_members=True)
        await interaction.response.edit_message(embed=success_embed(f"Transferred ownership to {user.mention}."), view=None)

# --- Main VC Control Panel ---
class VoiceControl(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    def get_vc(self, interaction):
        if interaction.user.voice and interaction.user.voice.channel: return interaction.user.voice.channel
        return None

    async def check_owner(self, interaction, vc):
        owner = await db.get_temp_channel(vc.id)
        if str(interaction.user.id) != owner and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=error_embed("You are not the owner of this channel."), ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.secondary, emoji=EMOJI_LOCK, custom_id="vc_lock", row=0)
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc or not await self.check_owner(interaction, vc): return
        await vc.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message(embed=success_embed("Channel locked."), ephemeral=True)

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.secondary, emoji=EMOJI_UNLOCK, custom_id="vc_unlock", row=0)
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc or not await self.check_owner(interaction, vc): return
        await vc.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message(embed=success_embed("Channel unlocked."), ephemeral=True)

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.primary, emoji=EMOJI_GEAR, custom_id="vc_rename", row=0)
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc or not await self.check_owner(interaction, vc): return
        await interaction.response.send_modal(RenameModal())

    @discord.ui.button(label="Limit", style=discord.ButtonStyle.primary, emoji=EMOJI_VOICE, custom_id="vc_limit", row=0)
    async def limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc or not await self.check_owner(interaction, vc): return
        await interaction.response.send_modal(LimitModal())

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.success, emoji=EMOJI_HEART, custom_id="vc_claim", row=0)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc: return await interaction.response.send_message(embed=error_embed("Join a VC first."), ephemeral=True)
        owner_id = await db.get_temp_channel(vc.id)
        owner = interaction.guild.get_member(int(owner_id)) if owner_id else None
        
        if owner and owner.voice and owner.voice.channel == vc:
            return await interaction.response.send_message(embed=error_embed("The owner is still in the channel."), ephemeral=True)
            
        await db.update_temp_owner(vc.id, interaction.user.id)
        await vc.set_permissions(interaction.user, manage_channels=True, connect=True, move_members=True)
        await interaction.response.send_message(embed=success_embed(f"👑 {interaction.user.mention} has claimed the channel!"), ephemeral=True)

    @discord.ui.button(label="Trust", style=discord.ButtonStyle.secondary, emoji=EMOJI_SUCCESS, custom_id="vc_trust", row=1)
    async def trust(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc or not await self.check_owner(interaction, vc): return
        await interaction.response.send_message(embed=main_embed("Trust User", "Select a user to allow them to join."), view=TrustSelect(vc.id), ephemeral=True)

    @discord.ui.button(label="Block", style=discord.ButtonStyle.danger, emoji=EMOJI_ERROR, custom_id="vc_block", row=1)
    async def block(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc or not await self.check_owner(interaction, vc): return
        await interaction.response.send_message(embed=main_embed("Block User", "Select a user to deny access."), view=BlockSelect(vc.id), ephemeral=True)

    @discord.ui.button(label="Kick", style=discord.ButtonStyle.danger, emoji=EMOJI_ERROR, custom_id="vc_kick", row=1)
    async def kick(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc or not await self.check_owner(interaction, vc): return
        await interaction.response.send_message(embed=main_embed("Kick User", "Select a user to disconnect."), view=KickSelect(vc.id), ephemeral=True)

    @discord.ui.button(label="Transfer", style=discord.ButtonStyle.primary, emoji=EMOJI_HEART, custom_id="vc_transfer", row=1)
    async def transfer(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc or not await self.check_owner(interaction, vc): return
        await interaction.response.send_message(embed=main_embed("Transfer Ownership", "Select a user:"), view=TransferSelect(vc.id), ephemeral=True)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, emoji=EMOJI_TRASH, custom_id="vc_delete", row=1)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc or not await self.check_owner(interaction, vc): return
        await interaction.response.send_message(embed=success_embed("Deleting channel..."), ephemeral=True)
        await vc.delete()

# --- Text Channel Panel ---
class GlobalVoiceView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    
    @discord.ui.button(label="Manage My VC", style=discord.ButtonStyle.primary, emoji=EMOJI_VOICE, custom_id="global_vc_manage")
    async def manage(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.response.send_message(embed=error_embed("You must be in a voice channel to manage it."), ephemeral=True)
            
        vc = interaction.user.voice.channel
        owner_id = await db.get_temp_channel(vc.id)
        
        if not owner_id:
            return await interaction.response.send_message(embed=error_embed("You are not in a temporary voice channel."), ephemeral=True)
            
        await interaction.response.send_message(embed=main_embed(f"{EMOJI_GEAR} Control Center", "Manage your VC here."), view=VoiceControl(), ephemeral=True)

# --- Main Cog ---
class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(VoiceControl())
        self.bot.add_view(GlobalVoiceView())

    @commands.hybrid_command(name="setup_tempvoice", description="Setup the join-to-create hub")
    async def setup_tempvoice(self, ctx: commands.Context, channel: discord.VoiceChannel):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=error_embed("You need Administrator permission to use this."), ephemeral=True)

        await db.set_temp_hub(ctx.guild.id, channel.id)
        await ctx.send(embed=success_embed(f"Setup complete! {channel.mention} is now the hub."))

    @commands.hybrid_command(name="voice_panel", description="Setup the global voice management panel in this channel")
    async def voice_panel(self, ctx: commands.Context):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(embed=error_embed("You need Administrator permission to use this."), ephemeral=True)

        embed = main_embed(f"{EMOJI_VOICE} Voice Control Hub", "Join a temporary voice channel, then click the button below to manage it.")
        await ctx.send(embed=embed, view=GlobalVoiceView())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot: return

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
                
                embed = main_embed(f"{EMOJI_GEAR} Voice Control Center", "Manage your private channel using the buttons below.")
                await chan.send(embed=embed, view=VoiceControl())

        if before.channel:
            owner = await db.get_temp_channel(before.channel.id)
            if owner and len(before.channel.members) == 0:
                try: await before.channel.delete()
                except: pass
                finally: await db.clean_vc(before.channel.id)
            
            elif owner and str(member.id) == owner and len(before.channel.members) > 0:
                try:
                    await before.channel.send(embed=main_embed(f"{EMOJI_WARNING} Owner Left", "The owner has left the channel. Click **Claim** below to become the new owner."), view=VoiceControl())
                except: pass

async def setup(bot): await bot.add_cog(TempVoice(bot))
