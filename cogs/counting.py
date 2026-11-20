import discord
from discord.ext import commands
import db
from config import EMOJI_SUCCESS, EMOJI_ERROR
from ui import success_embed, error_embed

class Counting(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="setup_counting", description="Setup the counting game")
    @commands.has_permissions(administrator=True)
    async def setup_counting(self, ctx: commands.Context, channel: discord.TextChannel):
        await db.set_counting_channel(ctx.guild.id, channel.id)
        await ctx.send(embed=success_embed(f"Counting game setup in {channel.mention}. Start with **1**."))

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild: return

        config = await db.get_counting(msg.guild.id)
        if not config or str(msg.channel.id) != str(config[0]): return

        try: num = int(msg.content)
        except ValueError: return

        current, last_user = config[1], config[2]

        if str(msg.author.id) == str(last_user):
            await msg.add_reaction(EMOJI_ERROR)
            await msg.reply(embed=error_embed("You can't count twice in a row!"))
            await db.update_counting(msg.guild.id, 0, None)
            return

        if num == current + 1:
            await msg.add_reaction(EMOJI_SUCCESS)
            await db.update_counting(msg.guild.id, num, msg.author.id)
        else:
            await msg.add_reaction(EMOJI_ERROR)
            await msg.reply(embed=error_embed(f"Wrong number. It was **{current + 1}**. Resetting to 0."))
            await db.update_counting(msg.guild.id, 0, None)

async def setup(bot): await bot.add_cog(Counting(bot))
