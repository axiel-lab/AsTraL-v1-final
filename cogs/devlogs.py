import discord
from discord.ext import commands, tasks
import logging
import db
import io
from config import THEME_COLOR, EMOJI_GEAR
from ui import success_embed, error_embed, main_embed

# This class captures everything sent to the console
class DiscordLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_queue = []

    def emit(self, record):
        # Skip spammy heartbeat logs
        if "Shard ID None has successfully RESUMED" in record.getMessage():
            return
            
        msg = self.format(record)
        self.log_queue.append(msg)
        
        # Prevent memory leaks if the channel is down
        if len(self.log_queue) > 100:
            self.log_queue = self.log_queue[-100:]

log_handler = DiscordLogHandler()

class DevLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logging.getLogger().addHandler(log_handler)
        log_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
        self.send_logs.start()

    def cog_unload(self):
        logging.getLogger().removeHandler(log_handler)
        self.send_logs.cancel()

    @app_commands.command(name="setup_devlogs", description="Send console logs to this channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_devlogs(self, interaction: discord.Interaction):
        await db.set_devlog_channel(interaction.guild.id, interaction.channel_id)
        await interaction.response.send_message(embed=success_embed("Console logs will now be sent to this channel every 10 seconds."), ephemeral=True)

    @app_commands.command(name="stop_devlogs", description="Stop sending console logs")
    @app_commands.checks.has_permissions(administrator=True)
    async def stop_devlogs(self, interaction: discord.Interaction):
        await db.remove_devlog_channel(interaction.guild.id)
        await interaction.response.send_message(embed=success_embed("Console logs have been disabled."), ephemeral=True)

    @tasks.loop(seconds=10)
    async def send_logs(self):
        if not log_handler.log_queue:
            return

        channel_id = await db.get_devlog_channel()
        if not channel_id:
            log_handler.log_queue.clear()
            return

        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            return

        # Get the logs and clear the queue
        logs = log_handler.log_queue[:]
        log_handler.log_queue.clear()

        # Format logs into a clean code block
        text = "\n".join(logs)
        
        # Split into chunks if it exceeds Discord's 2000 character limit
        if len(text) > 1900:
            text = text[:1900] + "\n... (truncated)"

        embed = main_embed(f"{EMOJI_GEAR} Console Logs", f"```ansi\n{text}\n```")
        await channel.send(embed=embed)

    @send_logs.before_loop
    async def before_send_logs(self):
        await self.bot.wait_until_ready()

import discord
from discord import app_commands

async def setup(bot):
    await bot.add_cog(DevLogs(bot))
