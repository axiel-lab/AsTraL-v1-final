import discord
from discord import app_commands
from discord.ext import commands
import db
from ui import success_embed, error_embed, main_embed
from config import THEME_COLOR, EMOJI_HEART

class Welcome(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="setup_welcome", description="Setup the custom welcome message")
    @app_commands.describe(
        channel="The channel where welcomes will be sent",
        title="The title of the embed",
        description="The text below the title. Use {user} for a mention and {server} for the server name.",
        image_url="Paste a direct link to an Image or GIF"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_welcome(self, interaction: discord.Interaction, channel: discord.TextChannel, title: str, description: str, image_url: str):
        if not image_url.startswith("http"):
            return await interaction.response.send_message(embed=error_embed("The Image URL must start with `http`."), ephemeral=True)

        await db.set_welcome(interaction.guild.id, channel.id, title, description, image_url)
        
        preview_embed = main_embed(title.replace("{server}", interaction.guild.name), description.replace("{user}", interaction.user.mention).replace("{server}", interaction.guild.name))
        preview_embed.set_image(url=image_url)
        
        await interaction.response.send_message(
            content=f"✅ Configured for {channel.mention}. Preview:", 
            embed=preview_embed, 
            ephemeral=True
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = await db.get_welcome(member.guild.id)
        if not config: return

        chan_id, title, desc, image_url = config
        channel = member.guild.get_channel(int(chan_id))
        
        if not channel: return

        final_title = title.replace("{user}", member.name).replace("{server}", member.guild.name)
        final_desc = desc.replace("{user}", member.mention).replace("{server}", member.guild.name)

        embed = discord.Embed(
            title=final_title,
            description=final_desc,
            color=THEME_COLOR
        )
        
        if image_url:
            embed.set_image(url=image_url)

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(
            text=f"Member #{member.guild.member_count} • {member.guild.name}", 
            icon_url=member.guild.icon.url if member.guild.icon else None
        )

        await channel.send(content=f"{EMOJI_HEART} Welcome {member.mention}!", embed=embed)

async def setup(bot): 
    await bot.add_cog(Welcome(bot))
