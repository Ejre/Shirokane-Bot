"""
Music Commands Cog
All music playback related commands (play, skip, queue, etc.)
"""

import discord
import yt_dlp as youtube_dl
import unicodedata
import gc
from collections import deque
from discord.ext import commands
from logger import log_request

# Add Node.js to PATH if found (fixes "No supported JavaScript runtime" warning)
import os
node_path = r"C:\Program Files\nodejs"
if os.path.exists(node_path) and node_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + node_path

class QuietLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)



class QueuePaginationView(discord.ui.View):
    def __init__(self, ctx, queue_items, items_per_page=10):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.queue_items = queue_items
        self.items_per_page = items_per_page
        self.current_page = 0
        self.total_pages = (len(queue_items) - 1) // items_per_page + 1

    def _get_page_content(self):
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        current_items = self.queue_items[start:end]
        
        description = ""
        for i, song in enumerate(current_items):
            idx = start + i + 1
            description += f"**{idx}.** {song['title']}\n"
            
        embed = discord.Embed(
            title=f"📜 Queue List ({len(self.queue_items)} Songs)",
            description=description,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}")
        return embed

    def _update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == self.total_pages - 1

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.grey, disabled=True)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
             return await interaction.response.send_message("❌ This is not your menu!", ephemeral=True)
        
        self.current_page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self._get_page_content(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.grey)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
             return await interaction.response.send_message("❌ This is not your menu!", ephemeral=True)

        self.current_page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self._get_page_content(), view=self)

class Music(commands.Cog):
    """Music playback functionality"""
    
    def __init__(self, bot):
        self.bot = bot
        # Music queue per server
        self.queues = {}
    
    @commands.hybrid_command(aliases=["j"])
    async def join(self, ctx):
        """Make the bot join your voice channel."""
        if ctx.interaction:
            await ctx.interaction.response.defer()

        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send("✅ Bot has joined the voice channel!")
        else:
            await ctx.send("🚫 You need to be in a voice channel first!")
    
    @commands.hybrid_command(aliases=["p"])
    async def play(self, ctx, *, query: str):
        """
        Play a song from YouTube.
        """
        if ctx.interaction:
            await ctx.interaction.response.defer()

        guild_id = ctx.guild.id
        
        # Initialize queue for this server if not exists
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        
        # Get or create voice client
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        if not voice_client:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice_client = await channel.connect()
            else:
                await ctx.send("🚫 You need to be in a voice channel first!")
                return
        
        await ctx.send("🔍 Searching/Loading...")
        
        # Normalize text and handle queries
        query = unicodedata.normalize("NFKC", query)
        
        # If it's not a URL, search for it
        if not query.startswith("http"):
             query = f"ytsearch:{query} Official MV"
        
        # Configure yt-dlp with Lazy Loading settings
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": False,
            "quiet": True,
            "no_warnings": True,
            "extract_flat": "in_playlist", # CRITICAL: Don't resolve streams for playlists immediately
            "ignoreerrors": True, # CRITICAL: Skip over removed/unavailable videos
            "default_search": "ytsearch1",
            "source_address": "0.0.0.0",
            "logger": QuietLogger(),
        }

        import functools
        
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = await self.bot.loop.run_in_executor(
                    None, 
                    functools.partial(ydl.extract_info, query, download=False)
                )
            
            songs_to_add = []
            
            if "entries" in info:
                # Playlist or Search Result
                for entry in info["entries"]:
                    if entry:
                        # For playlists, we only get metadata (flat), so we mark for later resolution
                        songs_to_add.append({
                            "url": entry.get("url"), # Needs resolution
                            "title": entry.get("title", "Unknown Title"),
                            "needs_resolution": True
                        })
            else:
                # Single Video (Direct Link) - usually resolved fully unless flat forced
                # With 'in_playlist', single video direct links ARE resolved fully.
                songs_to_add.append({
                    "stream_url": info.get("url"), # Already ready
                    "title": info.get("title", "Unknown Title"),
                    "needs_resolution": False
                })
            
            if not songs_to_add:
                await ctx.send("⚠️ No results found.")
                return

            # Add to queue
            first_song_title = songs_to_add[0]["title"]
            count = 0
            for song in songs_to_add:
                self.queues[guild_id].append(song)
                count += 1

            # Log & Reply
            if count == 1:
                log_request(f"User {ctx.author} requested: {first_song_title}")
                # If resolving straight away
                if not voice_client.is_playing():
                     await self.play_next(ctx, voice_client, guild_id)
                     # Optional: Send "Now Playing" handled in play_next
                else:
                     await ctx.send(f"📌 **{first_song_title}** added to queue!")
            else:
                log_request(f"User {ctx.author} requested {count} songs from playlist")
                if not voice_client.is_playing():
                    await self.play_next(ctx, voice_client, guild_id)
                await ctx.send(f"✅ Added **{count}** songs to queue! Starting with **{first_song_title}**")

        except Exception as e:
            await ctx.send(f"❌ Error extracting info: {str(e)}")
            return
    
    async def play_next(self, ctx, voice_client, guild_id):
        """
        Play the next song in queue for the specified server.
        Handles lazy resolution of URLs.
        """
        if not voice_client or not voice_client.is_connected():
            return

        if guild_id in self.queues and self.queues[guild_id]:
            # Pop next song
            song_data = self.queues[guild_id].popleft()
            
            title = song_data.get("title", "Unknown")
            stream_url = song_data.get("stream_url")
            
            # Resolve URL if it was a flat playlist entry
            if song_data.get("needs_resolution"):
                webpage_url = song_data.get("url")
                
                # New options for single video resolution
                opts = {
                    "format": "bestaudio/best",
                    "quiet": True,
                    "noplaylist": True,
                    "format": "bestaudio/best",
                    "quiet": True,
                    "noplaylist": True,
                    "source_address": "0.0.0.0",
                    "logger": QuietLogger(),
                }
                
                import functools
                try:
                    with youtube_dl.YoutubeDL(opts) as ydl:
                        info = await self.bot.loop.run_in_executor(
                            None,
                            functools.partial(ydl.extract_info, webpage_url, download=False)
                        )
                        stream_url = info.get("url")
                        title = info.get("title", title)
                        
                except Exception as e:
                    # If resolution fails (e.g. video unavailable), log and skip to next
                    print(f"Error resolving {title}: {e}")
                    await ctx.send(f"⚠️ Skipping **{title}** (Video Unavailable/Error)")
                    await self.play_next(ctx, voice_client, guild_id)
                    return

            # Play the audio
            before_opts = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            
            def after_playing(e):
                self.bot.loop.create_task(self.play_next(ctx, voice_client, guild_id))
            
            voice_client.play(
                discord.FFmpegPCMAudio(
                    stream_url, 
                    before_options=before_opts,
                    options="-vn"
                ),
                after=after_playing
            )
            await ctx.send(f"🎵 **Now Playing:** {title}")
            
            gc.collect()
        else:
            await ctx.send("🎵 No more songs in queue.")
    
    @commands.hybrid_command(aliases=["s"])
    async def skip(self, ctx):
        """Skip the current song."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭ Skipped!")
        else:
            await ctx.send("❌ Tidak ada lagu yang sedang diputar.")

    @commands.hybrid_command(aliases=["q", "queue_list"])
    async def queue(self, ctx):
        """Show the current song queue."""
        if not self.music_queue:
            await ctx.send("📭 Queue kosong.")
            return

        embed = discord.Embed(title="🎶 Music Queue", color=discord.Color.blue())
        desc = ""
        for i, (title, url) in enumerate(self.music_queue):
            desc += f"{i+1}. [{title}]({url})\n"
            if len(desc) > 3800:
                desc += "... (dan lainnya)"
                break
        
        embed.description = desc
        await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["l", "disconnect"])
    async def leave(self, ctx):
        """Disconnect the bot from the voice channel."""
        if ctx.voice_client:
            # Clear queue
            self.music_queue = []
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Haaik, Rinko pamit dulu ya!")
        else:
            await ctx.send("❌ Bot tidak berada di voice channel.")


async def setup(bot):
    """Required function to load the cog"""
    await bot.add_cog(Music(bot))
