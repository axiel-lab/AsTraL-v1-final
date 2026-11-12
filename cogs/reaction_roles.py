import discord
from discord import app_commands
from discord.ext import commands

class ReactionRoles(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="reactionrole", description="Setup a reaction role")
    @app_commands.checks.has_permissions(administrator=True)
    async def reactionrole(self, interaction: discord.Interaction, role: discord.Role, emoji: str):
        embed = discord.Embed(title="Reaction Roles", description=f"React with {emoji} to get {role.mention}", color=discord.Color.blue())
        await interaction.response.send_message("Sending...", ephemeral=True)
        msg = await interaction.channel.send(embed=embed)
        await msg.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id: return
        # Simplistic approach: if reacting to a bot message with an embed titled "Reaction Roles"
        channel = self.bot.get_channel(payload.channel_id)
        try:
            msg = await channel.fetch_message(payload.message_id)
            if msg.author.id == self.bot.user.id and msg.embeds and msg.embeds[0].title == "Reaction Roles":
                # Extract role ID from description (simplistic parsing)
                desc = msg.embeds[0].description
                import re
                match = re.search(r'<@&(\d+)>', desc)
                if match:
                    role = payload.member.guild.get_role(int(match.group(1)))
                    if role: await payload.member.add_roles(role)
        except: pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # Similar logic for removing roles
        guild = self.bot.get_guild(payload.guild_id)
        if not guild: return
        member = guild.get_member(payload.user_id)
        channel = self.bot.get_channel(payload.channel_id)
        try:
            msg = await channel.fetch_message(payload.message_id)
            if msg.author.id == self.bot.user.id and msg.embeds and msg.embeds[0].title == "Reaction Roles":
                desc = msg.embeds[0].description
                import re
                match = re.search(r'<@&(\d+)>', desc)
                if match:
                    role = guild.get_role(int(match.group(1)))
                    if role: await member.remove_roles(role)
        except: pass

async def setup(bot): await bot.add_cog(ReactionRoles(bot))