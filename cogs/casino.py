import discord
from discord.ext import commands
import db
import random
import asyncio
from config import (
    THEME_COLOR, EMOJI_COIN, EMOJI_SUCCESS, EMOJI_ERROR, EMOJI_STAR,
    EMOJI_SPADE, EMOJI_CLUB, EMOJI_DIAMOND, EMOJI_HEART_SUIT, EMOJI_CARD_BACK,
    EMOJI_HIT, EMOJI_STAND, EMOJI_DOUBLE
)
from ui import success_embed, error_embed, main_embed

def get_suit_emoji(suit):
    return {"S": EMOJI_SPADE, "C": EMOJI_CLUB, "D": EMOJI_DIAMOND, "H": EMOJI_HEART_SUIT}.get(suit, "")

def format_card(card):
    rank = card[0].replace("T", "10")
    suit = card[1]
    return f"[{rank}{get_suit_emoji(suit)}]"

def calc_hand(hand):
    val = 0
    aces = 0
    for card in hand:
        rank = card[0]
        if rank in ["J", "Q", "K", "T"]: val += 10
        elif rank == "A": aces += 1; val += 11
        else: val += int(rank)
    while val > 21 and aces > 0:
        val -= 10
        aces -= 1
    return val

class BlackjackView(discord.ui.View):
    def __init__(self, user, bet, p_hand, d_hand, deck):
        super().__init__(timeout=60)
        self.user = user
        self.bet = bet
        self.p_hand = p_hand
        self.d_hand = d_hand
        self.deck = deck

    def get_embed(self, hide_dealer=True, result_text=None):
        p_val = calc_hand(self.p_hand)
        d_val = calc_hand(self.d_hand) if not hide_dealer else calc_hand([self.d_hand[0]])
        
        p_cards = " ".join(format_card(c) for c in self.p_hand)
        d_cards = " ".join(format_card(c) for c in self.d_hand) if not hide_dealer else f"{format_card(self.d_hand[0])} [{EMOJI_CARD_BACK}]"
        
        embed = main_embed("🃏 Mega Blackjack", f"**Your Hand (`{p_val}`):**\n{p_cards}\n\n**Dealer (`{d_val if not hide_dealer else '?'}`):**\n{d_cards}")
        embed.set_footer(text=f"Bet: {self.bet:,} coins")
        if result_text:
            embed.add_field(name="Result", value=result_text, inline=False)
        return embed

    async def end_game(self, interaction, result_text):
        for child in self.children: child.disabled = True
        await interaction.response.edit_message(embed=self.get_embed(hide_dealer=False, result_text=result_text), view=self)
        self.stop()

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.success, emoji=EMOJI_HIT)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user: return
        self.p_hand.append(self.deck.pop())
        if calc_hand(self.p_hand) > 21:
            await self.end_game(interaction, f"💥 **Bust!** You went over 21. You lost `{self.bet:,}` coins.")
        else:
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.danger, emoji=EMOJI_STAND)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user: return
        while calc_hand(self.d_hand) < 17:
            self.d_hand.append(self.deck.pop())
        
        p_val = calc_hand(self.p_hand)
        d_val = calc_hand(self.d_hand)
        
        if d_val > 21 or p_val > d_val:
            await db.add_coins(interaction.guild.id, self.user.id, self.bet * 2)
            res = f"🎉 **You Won!** You beat the dealer and won `{self.bet * 2:,}` coins!"
        elif p_val == d_val:
            await db.add_coins(interaction.guild.id, self.user.id, self.bet)
            res = "🤝 **Push!** It's a tie. You got your bet back."
        else:
            res = f"😔 **Dealer Wins.** You lost `{self.bet:,}` coins."
            
        await self.end_game(interaction, res)

    @discord.ui.button(label="Double", style=discord.ButtonStyle.primary, emoji=EMOJI_DOUBLE)
    async def double(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user: return
        bal = await db.get_balance(interaction.guild.id, self.user.id)
        if bal < self.bet:
            return await interaction.response.send_message(embed=error_embed("You don't have enough coins to double down."), ephemeral=True)
        
        await db.add_coins(interaction.guild.id, self.user.id, -self.bet)
        self.bet *= 2
        self.p_hand.append(self.deck.pop())
        
        if calc_hand(self.p_hand) > 21:
            await self.end_game(interaction, f"💥 **Bust!** You went over 21. You lost `{self.bet:,}` coins.")
            return

        while calc_hand(self.d_hand) < 17:
            self.d_hand.append(self.deck.pop())
            
        p_val = calc_hand(self.p_hand)
        d_val = calc_hand(self.d_hand)
        
        if d_val > 21 or p_val > d_val:
            await db.add_coins(interaction.guild.id, self.user.id, self.bet * 2)
            res = f"🎉 **You Won!** You doubled down and won `{self.bet * 2:,}` coins!"
        elif p_val == d_val:
            await db.add_coins(interaction.guild.id, self.user.id, self.bet)
            res = "🤝 **Push!** It's a tie. You got your bet back."
        else:
            res = f"😔 **Dealer Wins.** You lost `{self.bet:,}` coins."
            
        await self.end_game(interaction, res)

class Casino(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.hybrid_command(name="slots", aliases=["slot"], description="Play animated slots")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def slots(self, ctx: commands.Context, amount: int):
        if amount < 100: 
            return await ctx.send(embed=error_embed("Min bet is 100."), ephemeral=True)
        if await db.get_balance(ctx.guild.id, ctx.author.id) < amount:
            return await ctx.send(embed=error_embed("Not enough coins."), ephemeral=True)

        await db.add_coins(ctx.guild.id, ctx.author.id, -amount)
        emojis = [EMOJI_SPADE, EMOJI_CLUB, EMOJI_DIAMOND, EMOJI_HEART_SUIT]
        
        msg = await ctx.send(embed=main_embed("🎰 Spinning...", f"**[ ? | ? | ? ]**"))
        for _ in range(2):
            await asyncio.sleep(0.8)
            rand_emojis = [random.choice(emojis) for _ in range(3)]
            await msg.edit(embed=main_embed("🎰 Spinning...", f"**[ {rand_emojis[0]} | {rand_emojis[1]} | {rand_emojis[2]} ]**"))

        s1, s2, s3 = random.choice(emojis), random.choice(emojis), random.choice(emojis)
        
        if s1 == s2 == s3:
            win = amount * 5
            await db.add_coins(ctx.guild.id, ctx.author.id, win)
            embed = main_embed("🎰 JACKPOT!", f"**[ {s1} | {s2} | {s3} ]**\n\nYou won `{win:,}` coins!")
        elif s1 == s2 or s2 == s3 or s1 == s3:
            win = int(amount * 1.5)
            await db.add_coins(ctx.guild.id, ctx.author.id, win)
            embed = main_embed("🎰 You Matched Two!", f"**[ {s1} | {s2} | {s3} ]**\n\nYou won `{win:,}` coins!")
        else:
            embed = main_embed("🎰 You Lost", f"**[ {s1} | {s2} | {s3} ]**\n\nYou lost `{amount:,}` coins.")

        await msg.edit(embed=embed)

    @commands.hybrid_command(name="blackjack", aliases=["bj"], description="Play Mega Blackjack")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def blackjack(self, ctx: commands.Context, amount: int):
        if amount < 100: 
            return await ctx.send(embed=error_embed("Min bet is 100."), ephemeral=True)
        if await db.get_balance(ctx.guild.id, ctx.author.id) < amount:
            return await ctx.send(embed=error_embed("Not enough coins."), ephemeral=True)

        await db.add_coins(ctx.guild.id, ctx.author.id, -amount)
        
        deck = [f"{r}{s}" for r in "23456789TJQKA" for s in "SCDH"]
        random.shuffle(deck)
        
        p_hand = [deck.pop(), deck.pop()]
        d_hand = [deck.pop(), deck.pop()]
        
        view = BlackjackView(ctx.author, amount, p_hand, d_hand, deck)
        await ctx.send(embed=view.get_embed(), view=view)

async def setup(bot): 
    await bot.add_cog(Casino(bot))
