import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiohttp
import db
from ui import success_embed, error_embed, main_embed
from config import EMOJI_INFO

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weather_loop.start()

    def cog_unload(self): 
        self.weather_loop.cancel()

    @tasks.loop(minutes=60)
    async def weather_loop(self):
        print("[WEATHER] Running hourly weather update loop...")
        configs = await db.get_weather_configs()
        
        if not configs:
            print("[WEATHER] No weather configs found in database.")
            return

        for gid, cid, city in configs:
            channel = self.bot.get_channel(int(cid))
            if not channel:
                print(f"[WEATHER] Channel {cid} not found. Skipping.")
                continue
            
            try:
                embed = await self.get_weather_embed(city)
                if embed: 
                    await channel.send(embed=embed)
                    print(f"[WEATHER] Successfully sent weather for {city} to {channel.name}")
            except Exception as e:
                print(f"[WEATHER ERROR] Failed to send to {channel.name}: {e}")

    @weather_loop.before_loop
    async def before(self): 
        await self.bot.wait_until_ready()

    async def get_weather_embed(self, city):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&format=json") as r:
                geo = await r.json()
                if not geo.get("results"): return None
                loc = geo["results"][0]
            async with session.get(f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}&current_weather=true") as r:
                data = await r.json()
                cw = data.get("current_weather")
                if not cw: return None
                embed = main_embed(f"{EMOJI_INFO} Weather in {loc['name']}", f"**Temp:** `{cw['temperature']}°C`\n**Wind:** `{cw['windspeed']} km/h`\n**Direction:** `{cw['winddirection']}°`")
                return embed

    @app_commands.command(name="setup_weather", description="Setup hourly weather updates")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_weather(self, interaction: discord.Interaction, channel: discord.TextChannel, city: str):
        embed = await self.get_weather_embed(city)
        if not embed: 
            return await interaction.response.send_message(embed=error_embed("City not found."), ephemeral=True)
            
        await db.set_weather_config(interaction.guild.id, channel.id, city)
        await interaction.response.send_message(embed=success_embed(f"Weather for **{city}** set in {channel.mention}."), ephemeral=True)
        await channel.send(embed=embed)

    @app_commands.command(name="stop_weather", description="Stop weather updates")
    @app_commands.checks.has_permissions(administrator=True)
    async def stop_weather(self, interaction: discord.Interaction, city: str = "all"):
        if city.lower() == "all":
            await db.remove_all_weather(interaction.guild.id)
            await interaction.response.send_message(embed=success_embed("Stopped all weather updates."), ephemeral=True)
        else:
            await db.remove_weather_config(interaction.guild.id, city)
            await interaction.response.send_message(embed=success_embed(f"Stopped updates for **{city}**."), ephemeral=True)

async def setup(bot): 
    await bot.add_cog(Weather(bot))
