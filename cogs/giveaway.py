import discord
from discord import app_commands
from discord.ext import commands, tasks
import db
import time
import random
import re

class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Enter", style=discord.ButtonStyle.success, custom_id="enter_giveaway", emoji="🎉")
    async def enter(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Simple in-memory tracking per message (or could be DB, but this is faster)
        if not hasattr(self, 'entries'):
            self.entries = {}
            
        mid = interaction.message.id
        if mid not in self.entries:
            self.entries[mid] = set()
            
        if interaction.user.id in self.entries[mid]:
            self.entries[mid].remove(interaction.user.id)
            await interaction.response.send_message("❌ Left the giveaway.", ephemeral=True)
        else:
            self.entries[mid].add(interaction.user.id)
            await interaction.response.send_message("✅ Entered the giveaway!", ephemeral=True)

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.view = GiveawayView()
        self.bot.add_view(self.view)
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @app_commands.command(name="gstart", description="Start a giveaway")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def gstart(self, interaction: discord.Interaction, time_str: str, winners: int, prize: str):
        # Parse time (e.g., 10m, 1h, 1d)
        match = re.match(r"(\d+)([smhd])", time_str.lower())
        if not match:
            return await interaction.response.send_message("❌ Invalid time. Use `10s`, `5m`, `1h`, `1d`.", ephemeral=True)
        
        amount, unit = int(match.group(1)), match.group(2)
        multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        seconds = amount * multipliers[unit]
        end_time = int(time.time()) + seconds

        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=f"**Prize:** {prize}\n**Winners:** {winners}\n**Ends:** <t:{end_time}:R>\n\nClick the button below to enter!",
            color=discord.Color.gold()
        )
        
        await interaction.response.send_message("Giveaway started!", ephemeral=True)
        msg = await interaction.channel.send(embed=embed, view=self.view)
        
        await db.add_giveaway(msg.id, msg.channel.id, prize, end_time, interaction.user.id, winners)

    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        now = int(time.time())
        active = await db.get_giveaways()
        
        for mid, cid, prize, end, host_id, winners in active:
            if now >= end:
                channel = self.bot.get_channel(int(cid))
                if not channel:
                    await db.remove_giveaway(mid)
                    continue
                
                try:
                    msg = await channel.fetch_message(int(mid))
                except discord.NotFound:
                    await db.remove_giveaway(mid)
                    continue

                # Fetch entries from the view
                entries = self.view.entries.get(int(mid), set()) if hasattr(self.view, 'entries') else set()
                
                if not entries:
                    await msg.edit(content="❌ Giveaway ended. No valid entries.", embed=None, view=None)
                else:
                    winner_ids = random.sample(list(entries), min(winners, len(entries)))
                    winner_mentions = ", ".join(f"<@{wid}>" for wid in winner_ids)
                    
                    embed = msg.embeds[0]
                    embed.description = f"**Prize:** {prize}\n**Winners:** {winner_mentions}\n\nEnded!"
                    embed.color = discord.Color.red()
                    
                    await msg.edit(content=f"🎉 **Giveaway Ended!** Winners: {winner_mentions}", embed=embed, view=None)
                    await channel.send(f"Congratulations {winner_mentions}! You won **{prize}**!")
                
                await db.remove_giveaway(mid)

    @check_giveaways.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Giveaways(bot))