import discord
from discord import app_commands
from discord.ext import commands
import db
import re

def clean_name(text):
    cleaned = re.sub(r'[!@#$%^&*()<>?{}]', '', text).strip()
    return cleaned[:32] or "User"

def get_rules_embed():
    embed = discord.Embed(
        title="📌 Nickname Setup",
        description="Type your name below to set your nickname.\n**Type `.reset` to remove your nickname.**\n\n**Restricted characters:**\n`!@#$%^&*()<>?{}`\n\nIf successful, I will react with ✅. If I cannot change your name, I will react with ❌ and tell you why.",
        color=discord.Color.blurple()
    )
    return embed

class Nicknames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_nick", description="Setup the nickname channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_nick(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.guild.me.guild_permissions.manage_nicknames:
            return await interaction.response.send_message("❌ Bot missing Manage Nicknames permission.", ephemeral=True)
        
        await db.set_nickname_channel(interaction.guild.id, channel.id, "rules_embed")
        
        msg = await channel.send(embed=get_rules_embed())
        await db.set_sticky(channel.id, msg.id, "rules_embed")
        
        await interaction.response.send_message(f"✅ Nickname system setup in {channel.mention}.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild:
            return

        config = await db.get_nickname_config(msg.guild.id)
        if config and str(msg.channel.id) == str(config[0]):
            
            # Check for reset command
            if msg.content.lower() in [".reset", "reset"]:
                try:
                    await msg.author.edit(nick=None)
                    await msg.add_reaction("✅")
                except discord.Forbidden:
                    await msg.add_reaction("❌")
                    await msg.reply(f"{msg.author.mention}, I can't reset your name. My role might be lower than yours.", mention_author=True)
                    return
            else:
                # Normal nickname change
                new_nick = clean_name(msg.content)
                try:
                    await msg.author.edit(nick=new_nick)
                    await msg.add_reaction("✅")
                except discord.Forbidden:
                    await msg.add_reaction("❌")
                    await msg.reply(f"{msg.author.mention}, I can't change your name. My role might be lower than yours.", mention_author=True)
                    return
                except Exception as e:
                    await msg.add_reaction("❌")
                    await msg.reply(f"{msg.author.mention}, an error occurred: {e}", mention_author=True)
                    return

            # Delete old sticky note and send new one
            sticky_data = await db.get_sticky(msg.channel.id)
            if sticky_data:
                old_msg_id = sticky_data[0]
                try:
                    old_msg = await msg.channel.fetch_message(int(old_msg_id))
                    await old_msg.delete()
                except:
                    pass
            
            new_msg = await msg.channel.send(embed=get_rules_embed())
            await db.set_sticky(msg.channel.id, new_msg.id, "rules_embed")

async def setup(bot):
    await bot.add_cog(Nicknames(bot))
