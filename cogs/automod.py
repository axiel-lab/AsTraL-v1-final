import discord
from discord import app_commands
from discord.ext import commands
import db
import re
import time

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_regex = re.compile(r"(discord\.gg|discord(app)?\.com/invite)/[a-zA-Z0-9]+")
        self.link_regex = re.compile(r"https?://[^\s]+")
        self.spam_cache = {}

    @app_commands.command(name="automod", description="Configure AutoMod")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod(
        self, 
        interaction: discord.Interaction, 
        log_channel: discord.TextChannel, 
        anti_invite: bool, 
        anti_spam: bool,
        anti_caps: bool,
        anti_links: bool
    ):
        await db.set_automod(
            interaction.guild.id, 
            log_channel.id, 
            int(anti_invite), 
            int(anti_spam), 
            int(anti_caps), 
            int(anti_links)
        )
        await interaction.response.send_message("✅ AutoMod configured.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild or msg.author.guild_permissions.administrator:
            return

        config = await db.get_automod(msg.guild.id)
        if not config:
            return

        log_id, anti_invite, anti_spam, anti_caps, anti_links = config
        reason = None
        now = time.time()

        # Anti-Spam (5 messages in 5 seconds)
        if anti_spam:
            uid = str(msg.author.id)
            if uid not in self.spam_cache:
                self.spam_cache[uid] = []
            self.spam_cache[uid] = [t for t in self.spam_cache[uid] if now - t < 5]
            self.spam_cache[uid].append(now)
            if len(self.spam_cache[uid]) >= 5:
                reason = "Spamming messages."
                self.spam_cache[uid] = [] # reset

        # Anti-Invite
        if not reason and anti_invite and self.invite_regex.search(msg.content):
            reason = "Posting a Discord invite."

        # Anti-Links
        if not reason and anti_links and self.link_regex.search(msg.content):
            reason = "Posting unauthorized links."

        # Anti-Caps (70% caps and > 10 chars)
        if not reason and anti_caps and len(msg.content) > 10:
            caps = sum(1 for c in msg.content if c.isupper())
            if (caps / len(msg.content)) > 0.7:
                reason = "Excessive caps."

        # Mention Spam
        if not reason and len(msg.mentions) > 5:
            reason = "Mass mentioning users."

        if reason:
            try:
                await msg.delete()
            except discord.Forbidden:
                return

            embed = discord.Embed(
                title="AutoMod Action",
                description=f"**User:** {msg.author.mention}\n**Channel:** {msg.channel.mention}\n**Reason:** {reason}",
                color=discord.Color.red()
            )
            
            if log_id:
                log_channel = msg.guild.get_channel(int(log_id))
                if log_channel:
                    await log_channel.send(embed=embed)
            
            try:
                await msg.author.send(f"Your message in **{msg.guild.name}** was deleted: {reason}")
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(AutoMod(bot))