"""
Music Bot - Discord Bot with Music Playback and AI Chat Features
Modular Architecture using Discord.py Cogs


Main entry point that loads all command modules.
"""

import discord
import asyncio
import re
from discord.ext import commands
from logger import export_log_to_excel
from config import BOT_TOKEN, COMMAND_PREFIX, intents, keyword_responses


# ============================================================================
# CREATE BOT INSTANCE
# ============================================================================
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)


# ============================================================================
# BOT EVENTS
# ============================================================================
@bot.event
async def on_ready():
    """Called when bot successfully connects to Discord."""
    print(f"✅ Bot {bot.user} is now online!")
    print(f"📦 Loaded {len(bot.cogs)} cogs: {', '.join(bot.cogs.keys())}")
    print(f"🌳 Tree Commands: {len(bot.tree.get_commands())}")
    for cmd in bot.tree.get_commands():
        print(f" - /{cmd.name}")


@bot.event
async def on_message(message):
    """Handle incoming messages for auto-AI and keyword responses."""
    if message.author.bot:
        return  # Ignore messages from bots

    # Process commands first
    await bot.process_commands(message)

    # Handle bot mentions
    if bot.user in message.mentions:
        user_message = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if user_message:
            ai_cog = bot.get_cog("AI")
            if ai_cog:
                response = await ai_cog.get_ai_response(user_message)
            else:
                response = None
            if response:
                if isinstance(response, dict):
                    if response.get("text"):
                        await message.reply(response["text"])
                    if response.get("image"):
                        embed = discord.Embed(color=discord.Color.blue())
                        embed.set_image(url=response["image"])
                        await message.channel.send(embed=embed)
                else:
                    await message.reply(response)
        return

    # Handle replies to bot messages (e.g. replying to an embed the bot sent)
    ai_cog = bot.get_cog("AI")
    if (
        ai_cog
        and message.reference
        and message.reference.resolved  # The referenced message is cached/resolved
        and isinstance(message.reference.resolved, discord.Message)
        and message.reference.resolved.author == bot.user
        and message.author.id not in ai_cog.autoai_users  # Don't double-handle autoai users
    ):
        user_message = message.content.strip()
        if user_message and not user_message.startswith(COMMAND_PREFIX):
            response = await ai_cog.get_ai_response(user_message, message.author.id, use_memory=True)
            if response:
                if isinstance(response, dict):
                    if response.get("text"):
                        await message.reply(response["text"])
                    if response.get("image"):
                        embed = discord.Embed(color=discord.Color.blue())
                        embed.set_image(url=response["image"])
                        await message.channel.send(embed=embed)
                else:
                    await message.reply(response)
        return

    # Handle auto-AI mode (from AI Cog)
    if ai_cog and message.author.id in ai_cog.autoai_users:
        # Get user's message
        user_message = message.content.strip()
        
        # Skip if message is a command
        if user_message.startswith(COMMAND_PREFIX):
            return
            
        # Get AI response
        response = await ai_cog.get_ai_response(user_message, message.author.id, use_memory=True)
        if response:
            if isinstance(response, dict):
                text = response.get("text")
                image = response.get("image")
                
                # Send text first as regular message
                if text:
                    await message.reply(text)
                
                # Send image as embed if available
                if image:
                    embed = discord.Embed(color=discord.Color.blue())
                    embed.set_image(url=image)
                    await message.channel.send(embed=embed)
            else:
                await message.reply(response)
        return

    # Handle keyword responses (only if exact match)
    content = message.content.lower().strip()
    for keyword, image_url in keyword_responses.items():
        keyword = keyword.lower()
        pattern = r'^' + re.escape(keyword) + r'$'
        if re.fullmatch(pattern, content):
            await message.reply(image_url)
            break


# ============================================================================
# HELPER COMMANDS
# ============================================================================
# ============================================================================
# HELPER COMMANDS
# ============================================================================
bot.remove_command("help")  # Remove default help command

@bot.command()
async def sync(ctx):
    """Sync slash commands (Owner only)."""
    # Replace with your ID for safety, or use @commands.is_owner() if owner_id is set in Bot
    if ctx.author.id not in [765561396225507349, 1276872790376579073]: 
        return await ctx.send("Hanya owner yang bisa sync command.")

    await ctx.send("Syncing commands...")
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ Synced {len(synced)} commands globally!")
    except Exception as e:
        await ctx.send(f"❌ Sync failed: {e}")


@bot.command(aliases=["h"])
async def help(ctx):
    """Display help information about available commands."""
    embed = discord.Embed(
        title="📜 Music Bot Command List",
        description="Here are the commands you can use:",
        color=discord.Color.blue()
    )
    
    # Music commands
    embed.add_field(name="🎶 **Music**", value="`!play <query>`: Play song\n`!skip`: Skip song\n`!queue`: Show queue\n`!leave`: Disconnect", inline=False)
    
    # AI commands
    embed.add_field(name="🤖 **AI Chat**", value="`!ai <text>`: Chat with Rinko\n`!autoai <on/off>`: Toggle Auto-Reply", inline=False)
    
    # Waifu commands
    embed.add_field(name="💖 **Waifu**", value="`!my`: Random waifu info (CD: 5m)\n`!gen <desc>`: Generate anime art (CD: 10m)", inline=False)
    
    # Leveling System
    embed.add_field(name="� **Leveling**", value="`!rank`: Cek Level & XP\n`!leaderboard`: Top 10 users\n`!roles`: List role rewards", inline=False)

    # Anime & Fun
    embed.add_field(name="🎬 **Anime & Fun**", value="`!anime <judul>`: Cari info anime\n`!recommend`: Rekomendasi anime random\n`!valrank`: Cek rank Valorant (Fun)", inline=False)

    # Admin (Owner Only)
    embed.add_field(name="🛠️ **Admin/Owner**", value="`!setlevel @user <lvl>`: Set level manual\n`!addxp @user <amount>`: Tambah XP manual", inline=False)

    embed.set_footer(text="Shirokane Bot v2.0 - Leveling System Added!")
    
    await ctx.send(embed=embed)


# ============================================================================
# COG LOADING
# ============================================================================
async def load_extensions():
    """Load all command cogs (modules)"""
    extensions = [
        "commands.music",
        "commands.ai",
        "commands.waifu",
        "commands.fun",
        "commands.valorant",
        "commands.anime",
        "commands.leveling"
    ]
    
    for extension in extensions:
        try:
            await bot.load_extension(extension)
            print(f"✅ Loaded extension: {extension}")
        except Exception as e:
            print(f"❌ Failed to load extension {extension}: {e}")


# ============================================================================
# BOT LIFECYCLE
# ============================================================================
async def run_bot():
    """Start the bot with error handling."""
    async with bot:
        # Load all cogs before starting
        await load_extensions()
        
        try:
            await bot.start(BOT_TOKEN)
        except KeyboardInterrupt:
            print("⚠ CTRL+C detected, shutting down bot gracefully...")
            await shutdown()
        except asyncio.CancelledError:
            print("⚠ asyncio.CancelledError detected! Ensuring logs are saved...")
            await shutdown()
        finally:
            print("✅ Bot exited successfully.")


async def shutdown():
    """Gracefully shutdown the bot and export logs."""
    print("⚠ Bot is shutting down... Exporting logs...")
    
    try:
        export_log_to_excel()
        print("✅ Log telah diekspor, bot akan mati.")
    except Exception as e:
        print(f"⚠ Error exporting log: {str(e)}")
    
    await bot.close()


if __name__ == "__main__":
    asyncio.run(run_bot())
