import discord
from discord import app_commands
from discord.ext import commands
import db

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    shop_group = app_commands.Group(name="shop", description="Economy Shop")

    @shop_group.command(name="add", description="Add an item to the shop")
    @app_commands.checks.has_permissions(administrator=True)
    async def shop_add(self, interaction: discord.Interaction, name: str, price: int, role: discord.Role):
        await db.add_shop_item(interaction.guild.id, name, price, role.id)
        await interaction.response.send_message(f"✅ Added `{name}` to shop for {price} coins.", ephemeral=True)

    @shop_group.command(name="remove", description="Remove an item from the shop")
    @app_commands.checks.has_permissions(administrator=True)
    async def shop_remove(self, interaction: discord.Interaction, name: str):
        await db.remove_shop_item(interaction.guild.id, name)
        await interaction.response.send_message(f"✅ Removed `{name}` from shop.", ephemeral=True)

    @shop_group.command(name="list", description="View the shop")
    async def shop_list(self, interaction: discord.Interaction):
        items = await db.get_shop_items(interaction.guild.id)
        if not items:
            return await interaction.response.send_message("Shop is empty.", ephemeral=True)

        desc = ""
        for n, p, r in items:
            desc += f"**{n}** - {p} coins\n"
            
        embed = discord.Embed(title="🛒 Server Shop", description=desc, color=discord.Color.green())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Buy an item from the shop")
    async def buy(self, interaction: discord.Interaction, name: str):
        items = await db.get_shop_items(interaction.guild.id)
        item = next((x for x in items if x[0].lower() == name.lower()), None)

        if not item:
            return await interaction.response.send_message("Item not found in shop.", ephemeral=True)

        item_name, price, role_id = item
        balance = await db.get_balance(interaction.guild.id, interaction.user.id)

        if balance < price:
            return await interaction.response.send_message(f"You need {price - balance} more coins.", ephemeral=True)

        role = interaction.guild.get_role(int(role_id))
        if not role:
            return await interaction.response.send_message("Role no longer exists.", ephemeral=True)

        await db.update_balance(interaction.guild.id, interaction.user.id, -price)
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"✅ Bought **{item_name}** for {price} coins.")

async def setup(bot):
    await bot.add_cog(Shop(bot))