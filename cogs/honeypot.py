import discord
from discord import app_commands
from discord.ext import commands
import db

class Honeypot(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="setup_honeypot", description="Setup a trap channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_honeypot(self, interaction: discord.Interaction, channel: discord.TextChannel):
        embed = discord.Embed(
            title="⚠️ DO NOT SEND MESSAGES HERE! ⚠️",
            description="This channel is a trap for compromised accounts.\nSending any message here will result in a **jail**.\n\n🍯 **Accounts Caught: 0**",
            color=0xf1c40f
        )
        msg = await channel.send(embed=embed)
        await db.set_honeypot(interaction.guild.id, channel.id, msg.id)
        await interaction.response.send_message(f"✅ Honeypot setup in {channel.mention}.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild: return
        
        config = await db.get_honeypot(msg.guild.id)
        if config and str(msg.channel.id) == config["channel_id"]:
            try:
                await msg.author.ban(reason="Honeypot Triggered")
            except discord.Forbidden:
                pass
            
            try:
                await msg.delete()
            except:
                pass
            
            await db.update_honeypot_bans(msg.guild.id)
            new_config = await db.get_honeypot(msg.guild.id)
            
            try:
                honeypot_msg = await msg.channel.fetch_message(int(config["message_id"]))
                embed = honeypot_msg.embeds[0]
                embed.description = f"This channel is a trap for compromised accounts.\nSending any message here will result in a **jail**.\n\n🍯 **Accounts Caught: {new_config['bans']}**"
                await honeypot_msg.edit(embed=embed)
            except:
                pass

async def setup(bot): await bot.add_cog(Honeypot(bot))
