import discord
from discord import app_commands
from discord.ext import commands
import os
import aiohttp
import re
import db

SYSTEM_PROMPT = (
    "You are a mature, intelligent, and savage AI. "
    "You understand English and Banglish (Bengali in English letters) perfectly. "
    "Reply in the same language the user uses. "
    "Be sharp, brutally honest, and concise. Do not act like a polite assistant."
)

class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_ai", description="Setup the AI thread channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_ai(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await db.set_ai_channel(interaction.guild.id, channel.id)
        await interaction.response.send_message(f"✅ AI thread system enabled in {channel.mention}.", ephemeral=True)

    @app_commands.command(name="test_ai", description="Test if the AI APIs are working")
    async def test_ai(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        groq_key = os.getenv("GROQ_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        msg = f"**Groq Key:** {'Found ✅' if groq_key else 'Missing ❌'}\n"
        msg += f"**Gemini Key:** {'Found ✅' if gemini_key else 'Missing ❌'}\n\n"

        if groq_key:
            res = await self.query_groq("Say 'Groq works'", groq_key)
            msg += f"**Groq Response:** {res[:300]}\n\n"
            
        if gemini_key:
            res = await self.query_gemini("Say 'Gemini works'", gemini_key)
            msg += f"**Gemini Response:** {res[:300]}\n"
            
        await interaction.followup.send(msg)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or not msg.guild:
            return

        ai_chan_id = await db.get_ai_channel(msg.guild.id)
        
        if ai_chan_id and str(msg.channel.id) == str(ai_chan_id):
            await msg.delete()
            thread = await msg.channel.create_thread(name=f"Chat with {msg.author.display_name}"[:100], type=discord.ChannelType.public_thread)
            await thread.send(f"{msg.author.mention} said: *\"{msg.content}\"*\n\n**Thinking...**")
            response = await self.get_ai_response(msg.content)
            await thread.send(f"**AI:** {response}")
            return

        if isinstance(msg.channel, discord.Thread) and ai_chan_id and msg.channel.parent_id == int(ai_chan_id):
            async with msg.channel.typing():
                response = await self.get_ai_response(msg.content)
                await msg.reply(response, mention_author=False)
            return

        is_mentioned = self.bot.user in msg.mentions
        is_reply = False
        if msg.reference:
            try:
                resolved = msg.reference.resolved
                if isinstance(resolved, discord.Message) and resolved.author == self.bot.user:
                    is_reply = True
            except: pass

        if is_mentioned or is_reply:
            prompt = re.sub(r'<@!?\d+>', '', msg.content).strip()
            if not prompt:
                return await msg.reply("Kichu bolo, shudhu mention kore labh nai.", mention_author=False)

            async with msg.channel.typing():
                response = await self.get_ai_response(prompt)
                await msg.reply(response, mention_author=False)

    async def get_ai_response(self, text):
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            response = await self.query_groq(text, groq_key)
            if not response.startswith("ERROR"):
                return response
            print(f"[GROQ ERROR] {response}")

        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            response = await self.query_gemini(text, gemini_key)
            if not response.startswith("ERROR"):
                return response
            print(f"[GEMINI ERROR] {response}")

        return "Both AI APIs failed. Check Deplexo console logs for the exact reason."

    async def query_groq(self, text, api_key):
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile", # Updated model
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}],
            "max_tokens": 150,
            "temperature": 0.8
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload) as r:
                    if r.status == 200:
                        data = await r.json()
                        return data["choices"][0]["message"]["content"].strip()
                    return f"ERROR: Status {r.status} - {await r.text()}"
        except Exception as e:
            return f"ERROR: {e}"

    async def query_gemini(self, text, api_key):
        full_prompt = f"System: {SYSTEM_PROMPT}\n\nUser: {text}\n\nAI:"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
        # Updated API version and model
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={api_key}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as r:
                    if r.status == 200:
                        data = await r.json()
                        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    return f"ERROR: Status {r.status} - {await r.text()}"
        except Exception as e:
            return f"ERROR: {e}"

async def setup(bot):
    await bot.add_cog(AIChat(bot))
