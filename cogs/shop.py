import discord
from discord import app_commands
from discord.ext import commands
import db
from config import THEME_COLOR, EMOJI_COIN, EMOJI_SILVER_RING, EMOJI_GOLD_RING, EMOJI_DIAMOND_RING, EMOJI_LEGENDARY_RING
from ui import success_embed, error_embed, main_embed

RINGS = {
    "silver": {"name": f"{EMOJI_SILVER_RING} Silver Ring", "price": 5000},
    "gold": {"name": f"{EMOJI_GOLD_RING} Golden Ring", "price": 25000},
    "diamond": {"name": f"{EMOJI_DIAMOND_RING} Diamond Ring", "price": 50000},
    "legendary": {"name": f"{EMOJI_LEGENDARY_RING} Legendary Ring", "price": 100000}
}

class ShopSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=data["name"].split(" ")[1], value=key, description=f"Price: {data['price']:,} coins", emoji=data["name"].split(" ")[0]) for key, data in RINGS.items()]
        super().__init__(placeholder="Select a ring to view...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        key = self.values[0]
        data = RINGS[key]
        embed = main_embed(f"🛒 {data['name']}", f"Price: `{data['price']:,}` {EMOJI_COIN}\n\nClick below to purchase this ring.")
        view = BuyView(key)
        await interaction.response.edit_message(embed=embed, view=view)

class BuyView(discord.ui.View):
    def __init__(self, ring_key):
        super().__init__(timeout=60)
        self.ring_key = ring_key

    @discord.ui.button(label="Buy Ring", style=discord.ButtonStyle.success, emoji="💸")
    async def buy_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        key = self.ring_key
        price = RINGS[key]["price"]

        if await db.get_ring(interaction.guild.id, interaction.user.id):
            return await interaction.response.send_message(embed=error_embed("You already own a ring! Use it with `/marry`."), ephemeral=True)

        bal = await db.get_balance(interaction.guild.id, interaction.user.id)
        if bal < price:
            return await interaction.response.send_message(embed=error_embed(f"You need `{price - bal:,}` more coins."), ephemeral=True)

        await db.add_coins(interaction.guild.id, interaction.user.id, -price)
        await db.buy_ring(interaction.guild.id, interaction.user.id, key)
        await interaction.response.send_message(embed=success_embed(f"You bought a **{RINGS[key]['name']}**! Use `/marry` to propose."), ephemeral=True)

class Shop(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="shop", description="View the marriage ring shop")
    async def shop(self, interaction: discord.Interaction):
        embed = main_embed("🛒 Ring Shop", "Select a ring from the dropdown below to view its details and purchase it.")
        view = discord.ui.View()
        view.add_item(ShopSelect())
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot): await bot.add_cog(Shop(bot))
