import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiohttp
import db

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weather_loop.start()

    def cog_unload(self):
        self.weather_loop.cancel()

    @tasks.loop(hours=1)
    async def weather_loop(self):
        configs = await db.get_weather_configs()
        for gid, cid, city in configs:
            channel = self.bot.get_channel(int(cid))
            if not channel:
                continue
            
            embed = await self.get_weather_embed(city)
            if embed:
                await channel.send(embed=embed)

    @weather_loop.before_loop
    async def before_weather_loop(self):
        await self.bot.wait_until_ready()

    async def get_weather_embed(self, city):
        async with aiohttp.ClientSession() as session:
            # Get coordinates for the city
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
            async with session.get(geo_url) as r:
                data = await r.json()
                if not data.get("results"):
                    return None
                loc = data["results"][0]
                lat, lon = loc["latitude"], loc["longitude"]
                name = loc["name"]

            # Get weather data
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            async with session.get(weather_url) as r:
                data = await r.json()
                cw = data.get("current_weather")
                if not cw:
                    return None

                embed = discord.Embed(title=f"🌤️ Weather in {name}", color=discord.Color.blue())
                embed.add_field(name="Temperature", value=f"{cw['temperature']}°C")
                embed.add_field(name="Wind Speed", value=f"{cw['windspeed']} km/h")
                embed.add_field(name="Wind Direction", value=f"{cw['winddirection']}°")
                embed.set_footer(text="Updates automatically every hour.")
                return embed

    @app_commands.command(name="setup_weather", description="Setup hourly weather updates")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_weather(self, interaction: discord.Interaction, channel: discord.TextChannel, city: str):
        embed = await self.get_weather_embed(city)
        if not embed:
            return await interaction.response.send_message("❌ City not found.", ephemeral=True)
        
        await db.set_weather_config(interaction.guild.id, channel.id, city)
        await interaction.response.send_message(f"✅ Weather updates for **{city}** will be sent to {channel.mention} every hour.", ephemeral=True)
        await channel.send(embed=embed)

    @app_commands.command(name="stop_weather", description="Stop hourly weather updates")
    @app_commands.checks.has_permissions(administrator=True)
    async def stop_weather(self, interaction: discord.Interaction):
        await db.remove_weather_config(interaction.guild.id)
        await interaction.response.send_message("✅ Weather updates stopped.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Weather(bot))
