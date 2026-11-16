import discord
from discord import app_commands
from discord.ext import commands
import db
from config import THEME_COLOR, EMOJI_COIN, EMOJI_SUCCESS
from utils.ui import success_embed, error_embed, main_embed

class Shop(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="shop", description="View the server shop")
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🛒 Server Shop", description="Use `/buy` to purchase an item.", color=THEME_COLOR)
        embed.add_field(name="💍 Ring of Marriage", value=f"Cost: `1000` {EMOJI_COIN}\nRequired to propose to someone.\nBuy with: `/buy ring`", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Buy an item from the shop")
    async def buy(self, interaction: discord.Interaction, item: str):
        if item.lower() != "ring":
            return await interaction.response.send_message(embed=error_embed("Invalid item. Check `/shop`."), ephemeral=True)
        
        already_has = await db.has_ring(interaction.guild.id, interaction.user.id)
        if already_has:
            return await interaction.response.send_message(embed=error_embed("You already own a ring!"), ephemeral=True)

        price = 1000
        balance = await db.get_balance(interaction.guild.id, interaction.user.id)
        
        if balance < price:
            return await interaction.response.send_message(embed=error_embed(f"You need {price - balance} more coins."), ephemeral=True)

        await db.add_coins(interaction.guild.id, interaction.user.id, -price)
        await db.buy_ring(interaction.guild.id, interaction.user.id)
        
        await interaction.response.send_message(embed=success_embed("You bought a 💍 **Ring of Marriage**! You can now use `/marry`."), ephemeral=True)

async def setup(bot): await bot.add_cog(Shop(bot))
