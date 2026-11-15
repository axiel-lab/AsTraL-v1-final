import discord
from discord import app_commands
from discord.ext import commands

class VerifyButton(discord.ui.View):
    def __init__(self, role_id): 
        super().__init__(timeout=None)
        self.role_id = role_id

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.success, custom_id="verify_btn")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message("❌ The verification role was deleted. Please contact an admin.", ephemeral=True)
        
        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Verified!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to give you this role. (My role is too low).", ephemeral=True)

class Verification(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="verify_panel", description="Send a verification panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def verify_panel(self, interaction: discord.Interaction, role: discord.Role):
        embed = discord.Embed(title="Verification", description="Click below to verify and gain access.", color=discord.Color.green())
        await interaction.channel.send(embed=embed, view=VerifyButton(role.id))
        await interaction.response.send_message("✅ Panel sent.", ephemeral=True)

async def setup(bot): await bot.add_cog(Verification(bot))
