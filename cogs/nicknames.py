import discord
from discord import app_commands
from discord.ext import commands
import db
import re
from config import THEME_COLOR, EMOJI_INFO, EMOJI_WARN, EMOJI_SUCCESS, EMOJI_ERROR, EMOJI_PIN

def clean_name(text):
    cleaned = re.sub(r'[!@#$%^&*()<>?{}]', '', text).strip()
    return cleaned[:32] or "User"

def get_rules_embed():
    embed = discord.Embed(
        title=f"{EMOJI_PIN} Nickname Setup",
        description=f"{EMOJI_INFO} **How to Use**\nJust type the name you want and send it here — we will change it!",
        color=THEME_COLOR
    )
    
    embed.add_field(
        name=f"{EMOJI_WARN} Nickname Rules",
        value=(
            "• Only standard text characters are allowed (no fancy fonts).\n"
            "• Offensive or inappropriate names are not allowed.\n"
            "• Names must not start with a symbol.\n"
            "• Bengali (Bangla) names are allowed.\n"
            "• Emojis can only be used at the end of the name."
        ),
        inline=False
    )
    
    embed.add_field(
        name=f"{EMOJI_SUCCESS} Reset",
        value="Use `.reset` to reset your name back to default.",
        inline=False
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
            
            if msg.content.lower() in [".reset", "reset"]:
                try:
                    await msg.author.edit(nick=None)
                    await msg.add_reaction(discord.PartialEmoji.from_str(EMOJI_SUCCESS))
                except discord.Forbidden:
                    await msg.add_reaction(discord.PartialEmoji.from_str(EMOJI_ERROR))
                    await msg.reply(f"{msg.author.mention}, I can't reset your name. My role might be lower than yours.", mention_author=True)
                    return
            else:
                new_nick = clean_name(msg.content)
                try:
                    await msg.author.edit(nick=new_nick)
                    await msg.add_reaction(discord.PartialEmoji.from_str(EMOJI_SUCCESS))
                except discord.Forbidden:
                    await msg.add_reaction(discord.PartialEmoji.from_str(EMOJI_ERROR))
                    await msg.reply(f"{msg.author.mention}, I can't change your name. My role might be lower than yours.", mention_author=True)
                    return
                except Exception as e:
                    await msg.add_reaction(discord.PartialEmoji.from_str(EMOJI_ERROR))
                    await msg.reply(f"{msg.author.mention}, an error occurred: {e}", mention_author=True)
                    return

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
