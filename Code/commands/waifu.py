"""
Waifu Commands Cog  
Waifu viewing and generation commands
"""

import discord
import json
import random
import os
import io
import aiohttp
import asyncio
from datetime import datetime, timedelta
from discord.ext import commands
from logger import log_request
from config import AI_API_KEY, AI_API_URL, WAIFU_COOLDOWN_MINUTES, GEN_WAIFU_COOLDOWN_MINUTES, STABLE_HORDE_API_KEY

STABLE_HORDE_URL = "https://stablehorde.net/api/v2"



class Waifu(commands.Cog):
    """Waifu viewing and generation functionality"""
    
    def __init__(self, bot):
        self.bot = bot
        # Waifu feature state
        self.waifu_cooldowns = {}  # User cooldown tracking {user_id: datetime}
        self.gen_waifu_cooldowns = {}  # User cooldown for generation {user_id: datetime}
    
    @commands.hybrid_command(name="my")
    async def my_waifu(self, ctx):
        """
        Get a random waifu image with character and anime info.
        Cooldown: 5 minutes per user.
        """
        if ctx.interaction:
            await ctx.interaction.response.defer()

        user_id = ctx.author.id
        current_time = datetime.now()
        
        # Check cooldown
        if user_id in self.waifu_cooldowns:
            last_used = self.waifu_cooldowns[user_id]
            time_diff = current_time - last_used
            cooldown_delta = timedelta(minutes=WAIFU_COOLDOWN_MINUTES)
            
            if time_diff < cooldown_delta:
                # Still in cooldown
                remaining_time = cooldown_delta - time_diff
                total_seconds = remaining_time.seconds
                minutes, seconds = divmod(total_seconds, 60)
                
                embed = discord.Embed(
                    title="⏰ Cooldown Active",
                    description=f"Kamu harus menunggu **{minutes}m {seconds}s** lagi untuk menggunakan command ini!",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
        
        # Load waifu metadata
        metadata_path = os.path.join("waifu_data", "metadata.json")
        
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                waifu_list = json.load(f)
        except FileNotFoundError:
            await ctx.send("❌ Waifu database tidak ditemukan! Pastikan file `waifu_data/metadata.json` ada.")
            return
        except json.JSONDecodeError:
            await ctx.send("❌ Waifu database rusak! Periksa format `metadata.json`.")
            return
        
        if not waifu_list:
            await ctx.send("❌ Tidak ada waifu dalam database!")
            return
        
        # Select random waifu
        waifu = random.choice(waifu_list)
        character_name = waifu.get("character_name", "Unknown")
        anime_name = waifu.get("anime_name", "Unknown Anime")
        image_file = waifu.get("image_file", "")
        
        # Build image path
        image_path = os.path.join("waifu_data", "images", image_file)
        
        # Check if image exists
        if not os.path.exists(image_path):
            await ctx.send(f"❌ Gambar `{image_file}` tidak ditemukan di folder `waifu_data/images/`!")
            return
        
        # Create embed
        embed = discord.Embed(
            title=f"💖 {character_name}",
            description=f"**{anime_name}**",
            color=discord.Color.pink()
        )
        
        # Attach image file
        file = discord.File(image_path, filename=image_file)
        embed.set_image(url=f"attachment://{image_file}")
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        # Update cooldown
        self.waifu_cooldowns[user_id] = current_time
        
        # Send embed with image
        await ctx.send(file=file, embed=embed)
        
        # Log request
        log_request(f"User {ctx.author} got waifu: {character_name} from {anime_name}")
    
    def _make_api_request(self, url, method="GET", payload=None):
        """Helper function to make synchronous API requests."""
        try:
            if method == "POST":
                response = requests.post(url, data=payload, timeout=120)
            else:
                response = requests.get(url, timeout=120)
            return response
        except Exception as e:
            print(f"[API ERROR] Request failed: {e}")
            raise e

    @commands.hybrid_command()
    async def gen(self, ctx, *, description: str = None):
        """
        Generate a custom anime waifu image using AI.
        Usage: /gen <description>
        Example: /gen girl with long silver hair and blue eyes
        Cooldown: 10 minutes per user
        """
        if ctx.interaction:
            await ctx.interaction.response.defer()

        user_id = ctx.author.id
        current_time = datetime.now()

        # Check if description provided
        if not description:
            embed = discord.Embed(
                title="❌ Deskripsi Required",
                description="Gunakan: `/gen <deskripsi>`\n\n**Contoh:**\n`/gen girl with long pink hair and green eyes`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Check cooldown
        if user_id in self.gen_waifu_cooldowns:
            last_used = self.gen_waifu_cooldowns[user_id]
            time_diff = current_time - last_used
            cooldown_delta = timedelta(minutes=GEN_WAIFU_COOLDOWN_MINUTES)
            if time_diff < cooldown_delta:
                remaining_time = cooldown_delta - time_diff
                total_seconds = remaining_time.seconds
                minutes, seconds = divmod(total_seconds, 60)
                embed = discord.Embed(
                    title="⏰ Cooldown Active",
                    description=f"Kamu harus menunggu **{minutes}m {seconds}s** lagi!",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

        # Send loading message
        loading_embed = discord.Embed(
            title="🎨 Generating Waifu...",
            description=f"Sedang membuat waifu dengan deskripsi:\n`{description}`\n\n⏳ Harap tunggu, ini bisa memakan 30-120 detik...",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        # Build anime-optimized prompt
        positive_prompt = (
            f"masterpiece, best quality, ultra-detailed, anime style, "
            f"{description}, "
            f"beautiful detailed face, detailed eyes, vibrant colors, "
            f"soft lighting, professional anime artwork, clean lineart, "
            f"high resolution"
        )
        negative_prompt = (
            "lowres, bad anatomy, bad hands, text, error, missing fingers, "
            "extra digit, fewer digits, cropped, worst quality, low quality, "
            "normal quality, jpeg artifacts, signature, watermark, username, "
            "blurry, bad feet, nsfw, ugly, deformed"
        )

        headers = {
            "apikey": STABLE_HORDE_API_KEY,
            "Content-Type": "application/json",
            "Client-Agent": "ShirokaneBot:1.0"
        }

        payload = {
            "prompt": f"{positive_prompt} ### {negative_prompt}",
            "params": {
                "sampler_name": "k_euler_a",
                "steps": 30,
                "cfg_scale": 7.5,
                "width": 512,
                "height": 512,
                "n": 1,
                "karras": True
            },
            "models": ["Anything V5"],
            "nsfw": False,
            "shared": True,
            "r2": True
        }

        try:
            async with aiohttp.ClientSession() as session:
                # 1. Submit generation request
                async with session.post(
                    f"{STABLE_HORDE_URL}/generate/async",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 202:
                        error_text = await resp.text()
                        await loading_msg.delete()
                        await ctx.send(f"❌ Gagal submit ke Stable Horde (Status {resp.status}): `{error_text[:200]}`")
                        return
                    data = await resp.json()
                    job_id = data.get("id")

                if not job_id:
                    await loading_msg.delete()
                    await ctx.send("❌ Tidak mendapat job ID dari Stable Horde.")
                    return

                # 2. Poll for completion
                max_wait = 7200  # 2 hour timeout
                elapsed = 0
                image_url = None

                while elapsed < max_wait:
                    await asyncio.sleep(5)
                    elapsed += 5

                    async with session.get(
                        f"{STABLE_HORDE_URL}/generate/status/{job_id}",
                        headers={"apikey": STABLE_HORDE_API_KEY, "Client-Agent": "ShirokaneBot:1.0"},
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as status_resp:
                        if status_resp.status != 200:
                            continue
                        status_data = await status_resp.json()

                    if status_data.get("done"):
                        generations = status_data.get("generations", [])
                        if generations:
                            image_url = generations[0].get("img")
                        break

                    # Update loading embed with wait time every 15s
                    if elapsed % 15 == 0:
                        queue_pos = status_data.get("queue_position", "?")
                        wait_time = status_data.get("wait_time", "?")
                        loading_embed.description = (
                            f"Sedang membuat waifu dengan deskripsi:\n`{description}`\n\n"
                            f"⏳ Posisi antrian: **{queue_pos}** | Estimasi: **{wait_time}s**"
                        )
                        await loading_msg.edit(embed=loading_embed)

                if not image_url:
                    await loading_msg.delete()
                    await ctx.send("❌ Generation timeout atau tidak ada hasil. Coba lagi nanti!")
                    return

                # 3. Download the image
                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as img_resp:
                    if img_resp.status != 200:
                        await loading_msg.delete()
                        await ctx.send("❌ Gagal mendownload gambar hasil generate.")
                        return
                    image_bytes = await img_resp.read()

            # 4. Send result
            await loading_msg.delete()

            embed = discord.Embed(
                title="✨ Waifu Generated!",
                description=f"**Prompt:** {description}",
                color=discord.Color.green()
            )
            embed.set_image(url="attachment://generated_waifu.png")
            embed.set_footer(text=f"Generated for {ctx.author.display_name} • Powered by Stable Horde + Anything V5")

            file = discord.File(io.BytesIO(image_bytes), filename="generated_waifu.png")
            await ctx.send(file=file, embed=embed)

            # Update cooldown only on success
            self.gen_waifu_cooldowns[user_id] = current_time
            log_request(f"User {ctx.author} generated waifu (Stable Horde): {description}")

        except asyncio.TimeoutError:
            await loading_msg.delete()
            await ctx.send("❌ Request timeout. Stable Horde sedang sibuk, coba lagi nanti!")
        except Exception as e:
            try:
                await loading_msg.delete()
            except:
                pass
            import traceback
            traceback.print_exc()
            await ctx.send(f"❌ Error: {str(e)}")
            print(f"[GENWAIFU ERROR] {e}")


async def setup(bot):
    """Required function to load the cog"""
    await bot.add_cog(Waifu(bot))

