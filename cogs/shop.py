import discord
from discord import app_commands
from discord.ext import commands
import db
from config import THEME_COLOR, EMOJI_COIN, EMOJI_SUCCESS, EMOJI_SILVER_RING, EMOJI_GOLD_RING, EMOJI_DIAMOND_RING, EMOJI_LEGENDARY_RING
from ui import success_embed, error_embed, main_embed

RINGS = {
    "silver": {"name": f"{EMOJI_SILVER_RING} Silver Ring", "price": 5000},
    "gold": {"name": f"{EMOJI_GOLD_RING} Golden Ring", "price": 25000},
    "diamond": {"name": f"{EMOJI_DIAMOND_RING} Diamond Ring", "price": 50000},
    "legendary": {"name": f"{EMOJI_LEGENDARY_RING} Legendary Ring", "price": 100000}
}

class Shop(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="shop", description="View the marriage ring shop")
    async def shop(self, interaction: discord.Interaction):
        embed = main_embed("🛒 Ring Shop", "Buy a ring to propose to your loved one!\nUse `/buy <item>` to purchase.")
        for key, data in RINGS.items():
            embed.add_field(name=data["name"], value=f"Price: `{data['price']:,}` {EMOJI_COIN}\nID: `{key}`", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Buy a ring")
    async def buy(self, interaction: discord.Interaction, item: str):
        item = item.lower()
        if item not in RINGS:
            return await interaction.response.send_message(embed=error_embed("Invalid ring. Options: `silver`, `gold`, `diamond`, `legendary`."), ephemeral=True)
        
        if await db.get_ring(interaction.guild.id, interaction.user.id):
            return await interaction.response.send_message(embed=error_embed("You already own a ring! Use it with `/marry`."), ephemeral=True)

        price = RINGS[item]["price"]
        bal = await db.get_balance(interaction.guild.id, interaction.user.id)
        
        if bal < price:
            return await interaction.response.send_message(embed=error_embed(f"You need `{price - bal:,}` more coins."), ephemeral=True)

        await db.add_coins(interaction.guild.id, interaction.user.id, -price)
        await db.buy_ring(interaction.guild.id, interaction.user.id, item)
        await interaction.response.send_message(embed=success_embed(f"You bought a **{RINGS[item]['name']}**! Use `/marry` to propose."), ephemeral=True)

async def setup(bot): await bot.add_cog(Shop(bot))
