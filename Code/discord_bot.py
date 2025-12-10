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
            response = get_chat_response(user_message)
            await message.channel.send(response)
        return

    # Handle auto-AI mode (from AI Cog)
    ai_cog = bot.get_cog("AI")
    if ai_cog and message.author.id in ai_cog.autoai_users:
        # Get user's message
        user_message = message.content.strip()
        
        # Skip if message is a command
        if user_message.startswith(COMMAND_PREFIX):
            return
            
        # Get AI response
        response = await ai_cog.get_ai_response(user_message, message.author.id, use_memory=True)
        if response:
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
bot.remove_command("help")  # Remove default help command


@bot.command(aliases=["h"])
async def help(ctx):
    """Display help information about available commands."""
    embed = discord.Embed(
        title="📜 Music Bot Command List",
        description="Here are the commands you can use:",
        color=discord.Color.blue()
    )
    
    # Music commands
    embed.add_field(name="🎶 **!join / !j**", value="Make the bot join your voice channel.", inline=False)
    embed.add_field(name="🎵 **!play / !p**", value="Play a song from YouTube or a playlist.", inline=False)
    embed.add_field(name="⏭ **!skip / !s**", value="Skip the current song.", inline=False)
    embed.add_field(name="📜 **!queue_list / !queue / !q**", value="Show the current song queue.", inline=False)
    embed.add_field(name="👋 **!leave /!l**", value="Disconnect the bot from the voice channel.", inline=False)
    
    # AI commands
    embed.add_field(name="🤖 **!ai <pertanyaan>**", value="Ask the AI a question (tsundere mode).", inline=False)
    embed.add_field(name="🔄 **!autoai <on/off>**", value="Toggle auto-AI mode. When ON, bot responds to all your messages without needing !ai.", inline=False)
    
    # Waifu commands
    embed.add_field(name="💖 **!my**", value="Get a random waifu with character info. (Cooldown: 5 minutes)", inline=False)
    embed.add_field(name="🎨 **!gen <description>**", value="Generate custom anime image with AI. (Cooldown: 10 minutes)", inline=False)
    
    embed.set_footer(text="Use these commands to control the music bot!")
    
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
        "commands.valorant"
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
