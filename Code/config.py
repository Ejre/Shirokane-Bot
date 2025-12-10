"""
Bot Configuration
Contains all configuration constants and API credentials
"""

# ============================================================================
# API CREDENTIALS
# ============================================================================
import os
from dotenv import load_dotenv

# Load .env file from the same directory as this config file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")
AI_API_URL = "https://api.botcahx.eu.org/api/search/blackbox-chat"
VALORANT_API_KEY = os.getenv("VALORANT_API_KEY")

# Alternative API key: IQeFNK4E
    
# ============================================================================
# BOT SETTINGS
# ============================================================================
import discord

# Bot Intents
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# Command Prefix
COMMAND_PREFIX = "!"

# ============================================================================
# FEATURE COOLDOWNS (in minutes)
# ============================================================================
WAIFU_COOLDOWN_MINUTES = 5
GEN_WAIFU_COOLDOWN_MINUTES = 10

# ============================================================================
# KEYWORD AUTO-RESPONSES
# ============================================================================
keyword_responses = {
    "mana": "https://tenor.com/huj5s14WkYC.gif"
}
