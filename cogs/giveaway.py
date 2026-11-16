import discord
from discord import app_commands
from discord.ext import commands, tasks
import db
import time
import random
import re
from ui import success_embed, error_embed, main_embed
from config import THEME_COLOR, EMOJI_GIFT, EMOJI_STAR

class GiveawayView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Enter", style=discord.ButtonStyle.success, custom_id="enter_giveaway", emoji=EMOJI_GIFT)
    async def enter(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not hasattr(self, 'entries'): self.entries = {}
        mid = interaction.message.id
        if mid not in self.entries: self.entries[mid] = set()
        if interaction.user.id in self.entries[mid]:
            self.entries[mid].remove(interaction.user.id)
            await interaction.response.send_message(embed=error_embed("Left the giveaway."), ephemeral=True)
        else:
            self.entries[mid].add(interaction.user.id)
            await interaction.response.send_message(embed=success_embed("Entered the giveaway!"), ephemeral=True)

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.view = GiveawayView()
        self.bot.add_view(self.view)
        self.check_giveaways.start()

    def cog_unload(self): self.check_giveaways.cancel()

    @app_commands.command(name="gstart", description="Start a giveaway")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def gstart(self, interaction: discord.Interaction, time_str: str, winners: int, prize: str):
        match = re.match(r"(\d+)([smhd])", time_str.lower())
        if not match: return await interaction.response.send_message(embed=error_embed("Invalid time. Use `10s`, `5m`, `1h`, `1d`."), ephemeral=True)
        amount, unit = int(match.group(1)), match.group(2)
        multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        end_time = int(time.time()) + (amount * multipliers[unit])
        embed = main_embed(f"{EMOJI_GIFT} GIVEAWAY", f"**Prize:** {prize}\n**Winners:** {winners}\n**Ends:** <t:{end_time}:R>\n\nClick the button below to enter!")
        await interaction.response.send_message(embed=success_embed("Giveaway started!"), ephemeral=True)
        msg = await interaction.channel.send(embed=embed, view=self.view)
        await db.add_giveaway(msg.id, msg.channel.id, prize, end_time, interaction.user.id, winners)

    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        now = int(time.time())
        for mid, cid, prize, end, host_id, winners in await db.get_giveaways():
            if now >= end:
                channel = self.bot.get_channel(int(cid))
                if not channel:
                    await db.remove_giveaway(mid)
                    continue
                try: msg = await channel.fetch_message(int(mid))
                except:
                    await db.remove_giveaway(mid)
                    continue
                entries = self.view.entries.get(int(mid), set()) if hasattr(self.view, 'entries') else set()
                if not entries:
                    await msg.edit(content="Giveaway ended. No valid entries.", embed=None, view=None)
                else:
                    winner_ids = random.sample(list(entries), min(winners, len(entries)))
                    winner_mentions = ", ".join(f"<@{wid}>" for wid in winner_ids)
                    embed = main_embed(f"{EMOJI_GIFT} Giveaway Ended", f"**Prize:** {prize}\n**Winners:** {winner_mentions}")
                    await msg.edit(content=f"🎉 **Giveaway Ended!** Winners: {winner_mentions}", embed=embed, view=None)
                    await channel.send(embed=main_embed("Congratulations!", f"Winners: {winner_mentions} won **{prize}**!"))
                await db.remove_giveaway(mid)

    @check_giveaways.before_loop
    async def before_check(self): await self.bot.wait_until_ready()

async def setup(bot): await bot.add_cog(Giveaways(bot))
