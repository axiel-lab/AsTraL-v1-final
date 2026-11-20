import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiohttp
import db
from ui import success_embed, error_embed, main_embed
from config import EMOJI_INFO, THEME_COLOR

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weather_loop.start()

    def cog_unload(self): self.weather_loop.cancel()

    @tasks.loop(hours=1)
    async def weather_loop(self):
        configs = await db.get_weather_configs()
        for gid, cid, city, mid in configs:
            channel = self.bot.get_channel(int(cid))
            if not channel: continue

            # Delete old message to prevent spam
            if mid:
                try:
                    old_msg = await channel.fetch_message(int(mid))
                    await old_msg.delete()
                except: pass

            embed = await self.get_weather_embed(city)
            if embed:
                new_msg = await channel.send(embed=embed)
                await db.set_weather_message(gid, cid, city, new_msg.id)

    @weather_loop.before_loop
    async def before(self): await self.bot.wait_until_ready()

    async def get_weather_embed(self, city):
        async with aiohttp.ClientSession() as session:
            # Get Coordinates
            async with session.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&format=json") as r:
                geo = await r.json()
                if not geo.get("results"): return None
                loc = geo["results"][0]
            
            # Get Advanced Weather Data
            url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['latitude']}&longitude={loc['longitude']}&current_weather=true&hourly=precipitation_probability&current=relative_humidity_2m,apparent_temperature&timezone=auto"
            async with session.get(url) as r:
                data = await r.json()
                cw = data.get("current_weather")
                if not cw: return None
                
                current = data.get("current", {})
                hourly = data.get("hourly", {})
                rain_prob = hourly.get("precipitation_probability", [])[:3] # Next 3 hours

                embed = main_embed(f"{EMOJI_INFO} Weather Analytics: {loc['name']}", "")
                
                embed.add_field(name="Temperature", value=f"`{cw['temperature']}°C`", inline=True)
                embed.add_field(name="Feels Like", value=f"`{current.get('apparent_temperature')}°C`", inline=True)
                embed.add_field(name="Humidity", value=f"`{current.get('relative_humidity_2m')}%`", inline=True)
                
                embed.add_field(name="Wind Speed", value=f"`{cw['windspeed']} km/h`", inline=True)
                embed.add_field(name="Wind Direction", value=f"`{cw['winddirection']}°`", inline=True)
                
                # Rain Prediction
                max_rain = max(rain_prob) if rain_prob else 0
                if max_rain > 60:
                    rain_status = f"🌧️ High chance of rain ({max_rain}%) in the next 3h."
                elif max_rain > 30:
                    rain_status = f"🌦️ Possible rain ({max_rain}%) in the next 3h."
                else:
                    rain_status = "☀️ Clear skies expected."
                    
                embed.add_field(name="Forecast", value=rain_status, inline=False)
                embed.set_footer(text=f"Live Analytics • {loc['country']}")

                return embed

    @app_commands.command(name="setup_weather", description="Setup hourly weather updates")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_weather(self, interaction: discord.Interaction, channel: discord.TextChannel, city: str):
        embed = await self.get_weather_embed(city)
        if not embed: return await interaction.response.send_message(embed=error_embed("City not found."), ephemeral=True)
        
        await db.set_weather_message(interaction.guild.id, channel.id, city, None)
        await interaction.response.send_message(embed=success_embed(f"Analytics for **{city}** will update here every hour."), ephemeral=True)
        msg = await channel.send(embed=embed)
        await db.set_weather_message(interaction.guild.id, channel.id, city, msg.id)

    @app_commands.command(name="stop_weather", description="Stop weather updates")
    @app_commands.checks.has_permissions(administrator=True)
    async def stop_weather(self, interaction: discord.Interaction, city: str = "all"):
        if city.lower() == "all":
            await db.remove_all_weather(interaction.guild.id)
            await interaction.response.send_message(embed=success_embed("Stopped all weather updates."), ephemeral=True)
        else:
            await db.remove_weather_config(interaction.guild.id, city)
            await interaction.response.send_message(embed=success_embed(f"Stopped updates for **{city}**."), ephemeral=True)

async def setup(bot): await bot.add_cog(Weather(bot))
