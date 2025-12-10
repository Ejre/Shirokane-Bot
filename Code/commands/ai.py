"""
AI Commands Cog
AI chat functionality including auto-AI mode
"""

import aiohttp
import requests
from discord.ext import commands
import discord
from config import AI_API_KEY, AI_API_URL


class AI(commands.Cog):
    """AI chat and conversation functionality"""
    
    def __init__(self, bot):
        self.bot = bot
        # Auto-AI feature state
        self.autoai_users = set()  # Users who have auto-AI enabled
        self.user_conversations = {}  # Per-user conversation history {user_id: [messages]}
    
    async def get_ai_response(self, query: str, user_id: int = None, use_memory: bool = False):
        """
        Get AI response from the API.
        
        Args:
            query: User's question/message
            user_id: User ID for conversation memory
            use_memory: Whether to use conversation history
        
        Returns:
            AI response string or None if error
        """
        # Build conversation context if memory is enabled
        if use_memory and user_id:
            if user_id not in self.user_conversations:
                self.user_conversations[user_id] = []
            
            # Add current message to history
            self.user_conversations[user_id].append(f"User: {query}")
            
            # Limit conversation history to last 10 messages to avoid token limits
            if len(self.user_conversations[user_id]) > 10:
                self.user_conversations[user_id] = self.user_conversations[user_id][-10:]
            
            # Build context from history
            context = "\\n".join(self.user_conversations[user_id])
            full_query = f"{context}\\nRespond to the latest message."
        else:
            full_query = query
        
        # Add tsundere personality to prompt
        # Shirokane Rinko Personality
        prompt = (
            "Jawablah sebagai Shirokane Rinko dari BanG Dream! "
            "Sifatmu pemalu, sopan, lembut, dan sering ragu-ragu saat berbicara. "
            "Gunakan kata-kata pengisi seperti 'ano...', 'et-to...', atau 'uuh...' di awal kalimat untuk menunjukkan keraguan. "
            "Gunakan bahasa Indonesia yang sopan dan natural, jangan kaku atau baku seperti robot. "
            "Kamu suka bermain piano dan game online (Neo Fantasy Online). "
            "Jangan gunakan awalan 'AI:', 'Rinko:', atau 'Bot:' dalam responmu. "
            "Jika membahas game, kamu bisa sedikit lebih bersemangat tapi tetap sopan. "
            + full_query
        )

        # Alternative Personality (Tsundere) - Saved for reference
        # prompt = (
        #     "Jawablah seperti karakter anime perempuan dengan sifat tsundere, "
        #     "gunakan bahasa indonesia yang malu-malu, agak ragu, dan tambahkan emotikon "
        #     "seperti (>///< ) atau ///. "
        #     + full_query
        # )
        
        # Encode query for URL
        encoded_query = requests.utils.quote(prompt)
        api_url = f"{AI_API_URL}?text={encoded_query}&apikey={AI_API_KEY}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as resp:
                    data = await resp.json()
                    
                    if data.get("status"):
                        response = data["message"]
                        
                        # Clean up response prefixes
                        cleaned_response = response
                        prefixes_to_remove = ["AI:", "Rinko:", "Bot:", "Shirokane Rinko:"]
                        for prefix in prefixes_to_remove:
                            if cleaned_response.startswith(prefix):
                                cleaned_response = cleaned_response[len(prefix):].strip()
                            elif cleaned_response.startswith(prefix.lower()): # Case insensitive check
                                cleaned_response = cleaned_response[len(prefix):].strip()
                        
                        response = cleaned_response

                        # Store AI response in conversation history
                        if use_memory and user_id:
                            self.user_conversations[user_id].append(f"AI: {response}")
                        
                        return response
                    else:
                        return "⚠️ Gagal mendapatkan respons dari API."
        except Exception as e:
            print(f"[AI ERROR] {e}")
            return "❌ Terjadi error saat menghubungi API."
    
    @commands.command()
    async def ai(self, ctx, *, query: str):
        """Ask the AI a question with tsundere personality."""
        response = await self.get_ai_response(query)
        if response:
            await ctx.reply(response)
    
    @commands.command()
    async def autoai(self, ctx, mode: str = None):
        """
        Toggle auto-AI mode for the user.
        
        Usage:
            !autoai on  - Enable auto-AI mode
            !autoai off - Disable auto-AI mode and reset conversation memory
        """
        user_id = ctx.author.id
        
        if mode is None:
            # Show current status
            if user_id in self.autoai_users:
                await ctx.reply("✅ Auto-AI mode is currently **ON**. Use `!autoai off` to disable.", delete_after=5)
            else:
                await ctx.reply("❌ Auto-AI mode is currently **OFF**. Use `!autoai on` to enable.", delete_after=5)
            return
        
        mode = mode.lower()
        
        if mode == "on":
            if user_id in self.autoai_users:
                await ctx.reply("ℹ️ Auto-AI mode is already enabled for you!", delete_after=5)
            else:
                self.autoai_users.add(user_id)
                self.user_conversations[user_id] = []  # Initialize conversation history
                await ctx.reply(
                    "✅ **Auto-AI mode activated!**\n"
                    "Sekarang saya akan merespon semua pesan kamu tanpa perlu menggunakan `!ai`. "
                    "Gunakan `!autoai off` untuk mematikan fitur ini.",
                    delete_after=10
                )
        
        elif mode == "off":
            if user_id in self.autoai_users:
                self.autoai_users.remove(user_id)
                # Reset conversation memory
                if user_id in self.user_conversations:
                    del self.user_conversations[user_id]
                await ctx.reply(
                    "❌ **Auto-AI mode deactivated!**\n"
                    "Memori percakapan telah direset. Gunakan `!autoai on` untuk mengaktifkan kembali.",
                    delete_after=10
                )
            else:
                await ctx.reply("ℹ️ Auto-AI mode is already disabled for you!", delete_after=5)
        
        else:
            await ctx.reply(
                "⚠️ **Invalid option!**\n"
                "Gunakan `!autoai on` untuk mengaktifkan atau `!autoai off` untuk mematikan.",
                delete_after=5
            )


async def setup(bot):
    """Required function to load the cog"""
    await bot.add_cog(AI(bot))
