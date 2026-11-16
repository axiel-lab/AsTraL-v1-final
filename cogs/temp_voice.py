import discord
from discord import app_commands
from discord.ext import commands
import db
from ui import success_embed, error_embed, main_embed
from config import EMOJI_VOICE, EMOJI_LOCK, EMOJI_UNLOCK, EMOJI_TRASH, EMOJI_HEART, EMOJI_SUCCESS

class VoiceControl(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    def get_vc(self, interaction):
        if interaction.user.voice and interaction.user.voice.channel: return interaction.user.voice.channel
        if isinstance(interaction.channel, discord.VoiceChannel): return interaction.channel
        return None

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.secondary, emoji=EMOJI_LOCK, custom_id="vc_lock", row=0)
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc: return await interaction.response.send_message(embed=error_embed("Join the VC first."), ephemeral=True)
        if str(interaction.user.id) != await db.get_temp_channel(vc.id): return await interaction.response.send_message(embed=error_embed("Not your channel."), ephemeral=True)
        await vc.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message(embed=success_embed("Locked."), ephemeral=True)

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.secondary, emoji=EMOJI_UNLOCK, custom_id="vc_unlock", row=0)
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc: return await interaction.response.send_message(embed=error_embed("Join the VC first."), ephemeral=True)
        if str(interaction.user.id) != await db.get_temp_channel(vc.id): return await interaction.response.send_message(embed=error_embed("Not your channel."), ephemeral=True)
        await vc.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message(embed=success_embed("Unlocked."), ephemeral=True)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, emoji=EMOJI_TRASH, custom_id="vc_delete", row=1)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.get_vc(interaction)
        if not vc: return await interaction.response.send_message(embed=error_embed("Join the VC first."), ephemeral=True)
        if str(interaction.user.id) != await db.get_temp_channel(vc.id) and not interaction.user.guild_permissions.administrator: return await interaction.response.send_message(embed=error_embed("Not your channel."), ephemeral=True)
        await interaction.response.send_message(embed=success_embed("Deleting..."), ephemeral=True)
        await vc.delete()

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(VoiceControl())

    @app_commands.command(name="setup_tempvoice", description="Setup the join-to-create hub")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_tempvoice(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        await db.set_temp_hub(interaction.guild.id, channel.id)
        await interaction.response.send_message(embed=success_embed(f"Setup in {channel.mention}."), ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot: return
        if after.channel:
            hub_id = await db.get_temp_hub(member.guild.id)
            if hub_id and str(after.channel.id) == str(hub_id):
                guild = member.guild
                overwrites = {guild.default_role: discord.PermissionOverwrite(connect=True), member: discord.PermissionOverwrite(manage_channels=True, connect=True, move_members=True)}
                chan = await guild.create_voice_channel(name=f"{member.name}'s channel", category=after.channel.category, overwrites=overwrites)
                await db.add_temp_channel(chan.id, member.id)
                await member.move_to(chan)
                embed = main_embed(f"{EMOJI_VOICE} Voice Control Center", "Manage your channel using the buttons below.")
                await chan.send(embed=embed, view=VoiceControl())
        if before.channel:
            owner = await db.get_temp_channel(before.channel.id)
            if owner and len(before.channel.members) == 0:
                try: await before.channel.delete()
                except: pass
                finally: await db.clean_vc(before.channel.id)

async def setup(bot): await bot.add_cog(TempVoice(bot))
