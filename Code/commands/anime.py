"""
Anime Commands Cog
Search for anime details and recommendations using Jikan API (MyAnimeList)
"""

import discord
import aiohttp
from discord.ext import commands
import random

JIKAN_API_URL = "https://api.jikan.moe/v4"

class Anime(commands.Cog):
    """Anime search and recommendation commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def fetch_anime_data(self, endpoint, params=None):
        """Helper to fetch data from Jikan API"""
        url = f"{JIKAN_API_URL}/{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        print(f"Jikan API Error: {resp.status}")
                        return None
        except Exception as e:
            print(f"Jikan API Exception: {e}")
            return None

    def create_anime_embed(self, data):
        """Create a Discord Embed from anime data"""
        entries = data.get("data")
        
        # Handle list response (search) vs single object (random)
        if isinstance(entries, list):
            if not entries:
                return None
            anime = entries[0]
        else:
            anime = entries

        # Extract Fields
        title = anime.get("title", "Unknown Title")
        title_en = anime.get("title_english")
        title_jp = anime.get("title_japanese")
        url = anime.get("url", "")
        images = anime.get("images", {}).get("jpg", {})
        image_url = images.get("large_image_url") or images.get("image_url")
        synopsis = anime.get("synopsis", "No synopsis available.")
        
        # Truncate synopsis if too long
        if synopsis and len(synopsis) > 300:
            synopsis = synopsis[:300] + "..."

        score = anime.get("score", "N/A")
        rank = anime.get("rank", "N/A")
        episodes = anime.get("episodes", "?")
        status = anime.get("status", "Unknown")
        rating = anime.get("rating", "Unknown")
        
        # Build Embed
        embed = discord.Embed(
            title=f"🎬 {title}",
            url=url,
            description=synopsis,
            color=discord.Color.purple()
        )
        
        if image_url:
            embed.set_image(url=image_url)
            
        embed.add_field(name="🇯🇵 Japanese", value=title_jp or "-", inline=True)
        embed.add_field(name="⭐ Score", value=f"**{score}** (#{rank})", inline=True)
        embed.add_field(name="📺 Episodes", value=f"{episodes} ({status})", inline=True)
        embed.add_field(name="🔞 Rating", value=rating, inline=True)
        
        embed.set_footer(text="Data provided by Jikan (MyAnimeList)", icon_url="https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png")
        
        return embed

    @commands.command(aliases=["ani", "a"])
    async def anime(self, ctx, *, query: str):
        """
        Search for an anime by title.
        Usage: !anime <title>
        """
        async with ctx.typing():
            data = await self.fetch_anime_data("anime", params={"q": query, "limit": 1})
            
            if data:
                embed = self.create_anime_embed(data)
                if embed:
                    await ctx.reply(embed=embed)
                else:
                    await ctx.reply(f"❌ Tidak ditemukan anime dengan judul '{query}'.")
            else:
                await ctx.reply("⚠️ Terjadi kesalahan saat menghubungi MyAnimeList.")

    @commands.command(aliases=["rec", "saran"])
    async def recommend(self, ctx):
        """
        Get a random anime recommendation.
        Usage: !recommend
        """
        async with ctx.typing():
            # Randomly choose between "Top Anime" (random page) or completely "Random Anime"
            # to ensure quality but also variety
            choice = random.choice(["top", "random"])
            
            data = None
            if choice == "top":
                # Get a random anime from top 100 (approx)
                # Jikan returns 25 per page
                page = random.randint(1, 4) 
                data = await self.fetch_anime_data("top/anime", params={"page": page})
                if data and "data" in data and data["data"]:
                    # Pick one random anime from the list
                    anime_data = random.choice(data["data"])
                    data = {"data": anime_data} # Wrap it to match create_anime_embed format
            else:
                # Completely random
                data = await self.fetch_anime_data("random/anime")
            
            if data:
                embed = self.create_anime_embed(data)
                if embed:
                    await ctx.reply(content="✨ **Rekomendasi Anime Untukmu:**", embed=embed)
                else:
                     await ctx.reply("❌ Gagal mengambil data rekomendasi.")
            else:
                await ctx.reply("⚠️ Terjadi kesalahan saat menghubungi MyAnimeList.")

async def setup(bot):
    await bot.add_cog(Anime(bot))
