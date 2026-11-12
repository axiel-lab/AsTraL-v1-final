import discord
from discord import app_commands
from discord.ext import commands
import db

class Starboard(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="setup_starboard", description="Setup starboard")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_starboard(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await db.set_starboard(interaction.guild.id, channel.id)
        await interaction.response.send_message("✅ Starboard setup.", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) != "⭐" or payload.user_id == self.bot.user.id: return
        board_id = await db.get_starboard(payload.guild_id)
        if not board_id or payload.channel_id == int(board_id): return

        channel = self.bot.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        if len([r for r in msg.reactions if str(r.emoji) == "⭐"]) < 3: return

        board = self.bot.get_channel(int(board_id))
        star_id = await db.get_star(msg.id)
        
        if not star_id:
            embed = discord.Embed(description=msg.content, color=discord.Color.gold(), timestamp=msg.created_at)
            embed.set_author(name=msg.author.name, icon_url=msg.author.display_avatar.url)
            if msg.attachments: embed.set_image(url=msg.attachments[0].url)
            embed.add_field(name="Source", value=f"[Jump to message]({msg.jump_url})")
            
            star_msg = await board.send(content=f"⭐ **{msg.reactions[0].count}** | {msg.channel.mention}", embed=embed)
            await db.add_star(msg.id, star_msg.id)
        else:
            try:
                star_msg = await board.fetch_message(int(star_id))
                await star_msg.edit(content=f"⭐ **{len([r for r in msg.reactions if str(r.emoji) == '⭐'])}** | {msg.channel.mention}")
            except: pass

async def setup(bot): await bot.add_cog(Starboard(bot))