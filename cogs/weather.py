import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

class Weather(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="weather", description="Check the weather")
    async def weather(self, interaction: discord.Interaction, city: str):
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://wttr.in/{city}?format=j1") as r:
                if r.status != 200:
                    return await interaction.followup.send("City not found.")
                data = await r.json()

        current = data['current_condition'][0]
        embed = discord.Embed(title=f"Weather in {city.title()}", color=discord.Color.blue())
        embed.add_field(name="Temp", value=f"{current['temp_C']}°C")
        embed.add_field(name="Feels Like", value=f"{current['FeelsLikeC']}°C")
        embed.add_field(name="Condition", value=current['weatherDesc'][0]['value'])
        embed.add_field(name="Humidity", value=f"{current['humidity']}%")
        embed.add_field(name="Wind", value=f"{current['windspeedKmph']} km/h")
        await interaction.followup.send(embed=embed)

async def setup(bot): await bot.add_cog(Weather(bot))