import os
from dotenv import load_dotenv
import config

print("Checking configuration...")
if config.BOT_TOKEN:
    print(f"BOT_TOKEN loaded: {config.BOT_TOKEN[:5]}...")
else:
    print("BOT_TOKEN not loaded")

if config.AI_API_KEY:
    print(f"AI_API_KEY loaded: {config.AI_API_KEY[:3]}...")
else:
    print("AI_API_KEY not loaded")
