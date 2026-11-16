import discord
from discord import app_commands
from discord.ext import commands
import db
from ui import success_embed, error_embed, main_embed
from config import EMOJI_HEART, THEME_COLOR, EMOJI_SILVER_RING, EMOJI_GOLD_RING, EMOJI_DIAMOND_RING, EMOJI_LEGENDARY_RING

RING_EMOJIS = {
    "silver": EMOJI_SILVER_RING,
    "gold": EMOJI_GOLD_RING,
    "diamond": EMOJI_DIAMOND_RING,
    "legendary": EMOJI_LEGENDARY_RING
}

class Marriage(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="marry", description="Propose to someone")
    async def marry(self, interaction: discord.Interaction, member: discord.Member):
        if member.bot or member == interaction.user:
            return await interaction.response.send_message(embed=error_embed("You can't marry a bot or yourself."), ephemeral=True)
        
        if await db.get_marriage(interaction.guild.id, interaction.user.id):
            return await interaction.response.send_message(embed=error_embed("You are already married!"), ephemeral=True)
            
        if await db.get_marriage(interaction.guild.id, member.id):
            return await interaction.response.send_message(embed=error_embed("They are already married!"), ephemeral=True)

        ring_name = await db.get_ring(interaction.guild.id, interaction.user.id)
        if not ring_name:
            return await interaction.response.send_message(embed=error_embed("You need to buy a ring first! Use `/shop`."), ephemeral=True)

        ring_emoji = RING_EMOJIS.get(ring_name.lower(), "💍")
        
        view = discord.ui.View()
        btn_yes = discord.ui.Button(label="Accept", style=discord.ButtonStyle.success)
        btn_no = discord.ui.Button(label="Decline", style=discord.ButtonStyle.danger)
        view.add_item(btn_yes)
        view.add_item(btn_no)

        embed = main_embed(f"{EMOJI_HEART} Marriage Proposal", f"{member.mention}, {interaction.user.mention} is proposing to you with a **{ring_name.capitalize()} Ring** {ring_emoji}!")
        await interaction.response.send_message(embed=embed, view=view)

        async def yes_cb(i):
            if i.user.id != member.id: return
            await db.add_marriage(interaction.guild.id, interaction.user.id, member.id)
            await db.remove_ring(interaction.guild.id, interaction.user.id)
            await i.response.edit_message(embed=success_embed(f"🎉 {interaction.user.mention} and {member.mention} are now married!"), view=None)

        async def no_cb(i):
            if i.user.id != member.id: return
            await i.response.edit_message(embed=error_embed("💔 Proposal declined. (Ring refunded)"), view=None)
            await db.buy_ring(interaction.guild.id, interaction.user.id, ring_name) # Refund

        btn_yes.callback = yes_cb
        btn_no.callback = no_cb

    @app_commands.command(name="divorce", description="Divorce your partner")
    async def divorce(self, interaction: discord.Interaction):
        if not await db.get_marriage(interaction.guild.id, interaction.user.id):
            return await interaction.response.send_message(embed=error_embed("You aren't married."), ephemeral=True)
        await db.remove_marriage(interaction.guild.id, interaction.user.id)
        await interaction.response.send_message(embed=success_embed("💔 You are now divorced."))

    @app_commands.command(name="couple", description="Check your marriage status")
    async def couple(self, interaction: discord.Interaction):
        partner = await db.get_marriage(interaction.guild.id, interaction.user.id)
        if partner: 
            await interaction.response.send_message(embed=main_embed(f"{EMOJI_HEART} Couple", f"You are married to <@{partner}>!"))
        else: 
            await interaction.response.send_message(embed=error_embed("You are single."), ephemeral=True)

async def setup(bot): await bot.add_cog(Marriage(bot))
