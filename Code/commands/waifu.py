"""
Waifu Commands Cog  
Waifu viewing and generation commands
"""

import discord
import json
import random
import os
import requests
from datetime import datetime, timedelta
from discord.ext import commands
from logger import log_request
from config import AI_API_KEY, AI_API_URL, WAIFU_COOLDOWN_MINUTES, GEN_WAIFU_COOLDOWN_MINUTES


class Waifu(commands.Cog):
    """Waifu viewing and generation functionality"""
    
    def __init__(self, bot):
        self.bot = bot
        # Waifu feature state
        self.waifu_cooldowns = {}  # User cooldown tracking {user_id: datetime}
        self.gen_waifu_cooldowns = {}  # User cooldown for generation {user_id: datetime}
    
    @commands.command(name="my")
    async def my_waifu(self, ctx):
        """
        Get a random waifu image with character and anime info.
        Cooldown: 5 minutes per user.
        """
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
                await ctx.reply(embed=embed)
                return
        
        # Load waifu metadata
        metadata_path = os.path.join("waifu_data", "metadata.json")
        
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                waifu_list = json.load(f)
        except FileNotFoundError:
            await ctx.reply("❌ Waifu database tidak ditemukan! Pastikan file `waifu_data/metadata.json` ada.")
            return
        except json.JSONDecodeError:
            await ctx.reply("❌ Waifu database rusak! Periksa format `metadata.json`.")
            return
        
        if not waifu_list:
            await ctx.reply("❌ Tidak ada waifu dalam database!")
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
            await ctx.reply(f"❌ Gambar `{image_file}` tidak ditemukan di folder `waifu_data/images/`!")
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
        await ctx.reply(file=file, embed=embed)
        
        # Log request
        log_request(f"User {ctx.author} got waifu: {character_name} from {anime_name}")
    
    @commands.command()
    async def gen(self, ctx, *, description: str = None):
        """
        Generate a custom anime waifu image using AI.
        Usage: !gen <description>
        Example: !gen girl with long silver hair and blue eyes
        Cooldown: 10 minutes per user
        """
        user_id = ctx.author.id
        current_time = datetime.now()
        
        # Check if description provided
        if not description:
            embed = discord.Embed(
                title="❌ Deskripsi Required",
                description="Gunakan: `!gen <deskripsi>`\n\n**Contoh:**\n`!gen girl with long pink hair and green eyes`",
                color=discord.Color.red()
            )
            await ctx.reply(embed=embed)
            return
        
        # Check cooldown
        if user_id in self.gen_waifu_cooldowns:
            last_used = self.gen_waifu_cooldowns[user_id]
            time_diff = current_time - last_used
            cooldown_delta = timedelta(minutes=GEN_WAIFU_COOLDOWN_MINUTES)
            
            if time_diff < cooldown_delta:
                # Still in cooldown
                remaining_time = cooldown_delta - time_diff
                total_seconds = remaining_time.seconds
                minutes, seconds = divmod(total_seconds, 60)
                
                embed = discord.Embed(
                    title="⏰ Cooldown Active",
                    description=f"Kamu harus menunggu **{minutes}m {seconds}s** lagi untuk generate waifu lagi!",
                    color=discord.Color.red()
                )
                await ctx.reply(embed=embed)
                return
        
        # Send loading message
        loading_embed = discord.Embed(
            title="🎨 Generating Waifu...",
            description=f"Sedang membuat waifu dengan deskripsi:\n`{description}`\n\nHarap tunggu sebentar...",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.reply(embed=loading_embed)
        
        # Build optimized prompt for anime-style generation
        optimized_prompt = f"anime style, high quality anime illustration, {description}, beautiful detailed face, vibrant colors, professional anime artwork, detailed eyes, clean lineart"
        
        # Build API URL
        encoded_prompt = requests.utils.quote(optimized_prompt)
        api_url = f"{AI_API_URL.replace('/search/blackbox-chat', '/maker/text2img')}?text={encoded_prompt}&apikey={AI_API_KEY}"
        
        import functools
        
        try:
            # Make request to image generation API in a separate thread
            response = await self.bot.loop.run_in_executor(
                None,
                functools.partial(requests.get, api_url, timeout=60)
            )
            
            if response.status_code == 200:
                # Save image temporarily
                image_path = f"temp_generated_{user_id}.png"
                with open(image_path, "wb") as f:
                    f.write(response.content)
                
                # Create success embed
                embed = discord.Embed(
                    title="✨ Image Generated!",
                    description=f"**Prompt:** {description}",
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"Generated for {ctx.author.display_name}")
                
                # Send image
                file = discord.File(image_path, filename="generated_waifu.png")
                embed.set_image(url="attachment://generated_waifu.png")
                
                # Delete loading message
                await loading_msg.delete()
                
                # Send result
                await ctx.reply(file=file, embed=embed)
                
                # Clean up temp file
                try:
                    os.remove(image_path)
                except:
                    pass
                
                # Update cooldown
                self.gen_waifu_cooldowns[user_id] = current_time
                
                # Log request
                log_request(f"User {ctx.author} generated waifu: {description}")
                
            else:
                # API error
                await loading_msg.delete()
                error_embed = discord.Embed(
                    title="❌ Generation Failed",
                    description=f"API returned error code: {response.status_code}\nSilakan coba lagi nanti.",
                    color=discord.Color.red()
                )
                await ctx.reply(embed=error_embed)
                
        except requests.exceptions.Timeout:
            await loading_msg.delete()
            error_embed = discord.Embed(
                title="⏱️ Request Timeout",
                description="Generasi gambar memakan waktu terlalu lama. Silakan coba lagi.",
                color=discord.Color.red()
            )
            await ctx.reply(embed=error_embed)
            
        except Exception as e:
            await loading_msg.delete()
            error_embed = discord.Embed(
                title="❌ Error Occurred",
                description=f"Terjadi error: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.reply(embed=error_embed)
            print(f"[GENWAIFU ERROR] {e}")


async def setup(bot):
    """Required function to load the cog"""
    await bot.add_cog(Waifu(bot))
