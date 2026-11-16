import discord
from discord import app_commands
from discord.ext import commands
import db
from config import THEME_COLOR, EMOJI_WARNING
from ui import success_embed

class Honeypot(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="setup_honeypot", description="Setup a trap channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_honeypot(self, interaction: discord.Interaction, channel: discord.TextChannel):
        embed = discord.Embed(
            title=f"{EMOJI_WARNING} Security Trap",
            description="This channel is a honeypot for compromised accounts.\nSending any message here will result in an immediate **kick**.\n\n",
            color=THEME_COLOR
        )
        embed.add_field(name="Accounts Caught", value="`0`", inline=False)
        embed.set_footer(text="Do not type here.")
        
        msg = await channel.send(embed=embed)
        await db.set_honeypot(interaction.guild.id, channel.id, msg.id)
        await interaction.response.send_message(embed=success_embed(f"Honeypot deployed in {channel.mention}."), ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild: return
        
        config = await db.get_honeypot(msg.guild.id)
        if config and str(msg.channel.id) == config["channel_id"]:
            try: await msg.author.kick(reason="Honeypot Triggered")
            except: pass
            
            try: await msg.delete()
            except: pass
            
            await db.update_honeypot_bans(msg.guild.id)
            new_config = await db.get_honeypot(msg.guild.id)
            
            try:
                honeypot_msg = await msg.channel.fetch_message(int(config["message_id"]))
                embed = honeypot_msg.embeds[0]
                embed.set_field_at(0, name="Accounts Caught", value=f"`{new_config['bans']}`", inline=False)
                await honeypot_msg.edit(embed=embed)
            except: pass

async def setup(bot): await bot.add_cog(Honeypot(bot))
