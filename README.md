# 🎵 Shirokane Bot

Shirokane Bot is a feature-rich Discord bot designed to bring music, entertainment, and AI interaction to your server. Named after and inspired by **Shirokane Rinko** from *BanG Dream!*, this bot features a custom personality, high-quality music playback, and anime-style interactions.

## ✨ Features

### 🎧 Music Playback
Stream high-quality music directly from YouTube with stability and ease.
- **Play Music**: Play songs via URL or search query.
- **Queue System**: Manage a music queue with pagination support.
- **Background Play**: Efficient stream handling with `yt-dlp`.

### 🤖 AI Chat (Shirokane Rinko Mode)
Engage in conversations with an AI that mimics the personality of Shirokane Rinko (shy, polite, avid gamer).
- **Chat**: Ask questions or chat using `!ai`.
- **Auto-AI Mode**: Have continuous conversations without using the prefix.
- **Context Awareness**: Remembers the last 10 messages for deeper context.

### 🌸 Waifu & Anime
- **Waifu Collection**: Gacha-style waifu collection system.
- **AI Image Gen**: Generate anime-style images from text descriptions.

### 🎸 Bestdori Integration (New!)
The bot is now integrated with the **Bestdori API** to provide real-time BanG Dream! information.
- **Card Search**: Ask for cards by character (e.g. "Kartu Yukina") or type (e.g. "Kartu Dream Fest Rinko").
- **Event Info**: Get details about the current JP event (e.g. "Event JP sekarang apa?").
- **Smart Responses**: AI responses now include card images in a clean Embed format.

### 🎮 Other Features
- **Valorant Stats**: (Coming soon) Check player stats.
- **Fun Commands**: Keyword auto-responses and more.

---

## 🛠️ Prerequisites

Before you begin, ensure you have met the following requirements:
- **Python 3.9+** installed.
- **FFmpeg** installed and added to your system PATH (required for audio playback).
- A **Discord Bot Token** from the [Discord Developer Portal](https://discord.com/developers/applications).
- API Keys for AI features (e.g., Botcahx API).

---

## 📥 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ejre/shirokane-bot.git
   cd shirokane-bot
   ```

2. **Install dependencies:**
   It is recommended to use a virtual environment.
   ```bash
   pip install discord.py yt-dlp python-dotenv aiohttp requests openpyxl
   ```

3. **Install FFmpeg:**
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html), extract, and add the `bin` folder to your System Environment Requirements (PATH).
   - **Linux**: `sudo apt install ffmpeg`

---

## ⚙️ Configuration

1. Navigate to the `Code` directory.
2. Create a `.env` file based on the example below:

   ```ini
   # Discord Bot Token
   BOT_TOKEN=your_discord_bot_token_here

   # API Keys
   AI_API_KEY=your_ai_api_key
   VALORANT_API_KEY=your_valorant_api_key
   ```

---

## 🚀 Usage

1. Open a terminal and navigate to the `Code` directory:
   ```bash
   cd Code
   ```

2. Run the bot:
   ```bash
   python discord_bot.py
   ```

3. Invite the bot to your server and start using commands!

---

## 📝 Command List

### 🎵 Music Commands
| Command | Alias | Description |
| :--- | :--- | :--- |
| `!play <query/url>` | `!p` | Play a song or add to queue. |
| `!join` | `!j` | Summon bot to your voice channel. |
| `!skip` | `!s` | Skip the current song. |
| `!queue` | `!q` | View the current song queue. |
| `!leave` | `!l` | Disconnect bot from voice. |

### 🤖 AI Commands
| Command | Description |
| :--- | :--- |
| `!ai <message>` | Chat with Shirokane Rinko AI. <br> **Try asking:** <br> - "Kartu Dream Fest Rinko" <br> - "Event JP sekarang apa?" <br> - "Gacha terbaru" |
| `!autoai <on/off>` | Toggle continuous chat mode (no prefix needed). |

### 🌸 Waifu & Fun
| Command | Description |
| :--- | :--- |
| `!my` | Get a random waifu. |
| `!gen <prompt>` | Generate an anime image. |
| `!help` | Show the help menu. |

---

## 📂 Project Structure

```
shirokane-bot/
├── Code/
│   ├── commands/       # Cogs (Music, AI, Waifu, etc.)
│   ├── data/           # Data storage
│   ├── discord_bot.py  # Main entry point
│   ├── config.py       # Configuration loader
│   ├── logger.py       # Logging utility
│   └── .env            # Secrets (Ignored by Git)
└── README.md
```

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).
