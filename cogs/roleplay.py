import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import random

class Roleplay(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def fetch_img(self, action):
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://nekos.best/api/v2/{action}") as r:
                data = await r.json()
                return data['results'][0]['url']

    @app_commands.command(name="hug", description="Hug someone")
    async def hug(self, interaction: discord.Interaction, member: discord.Member):
        url = await self.fetch_img("hug")
        embed = discord.Embed(description=f"{interaction.user.mention} hugs {member.mention}!", color=discord.Color.pink())
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="slap", description="Slap someone")
    async def slap(self, interaction: discord.Interaction, member: discord.Member):
        url = await self.fetch_img("slap")
        embed = discord.Embed(description=f"{interaction.user.mention} slaps {member.mention}!", color=discord.Color.red())
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="kiss", description="Kiss someone")
    async def kiss(self, interaction: discord.Interaction, member: discord.Member):
        url = await self.fetch_img("kiss")
        embed = discord.Embed(description=f"{interaction.user.mention} kisses {member.mention}!", color=discord.Color.magenta())
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)

async def setup(bot): await bot.add_cog(Roleplay(bot))