import discord
from discord.ext import commands
import aiohttp
from config import VALORANT_API_KEY

class Valorant(commands.Cog):
    """Valorant stats and info commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.base_url = "https://api.henrikdev.xyz/valorant"
        self.headers = {
            "Authorization": VALORANT_API_KEY
        }
        
    @commands.command(aliases=["valorant", "v"])
    async def val(self, ctx, *, RiotID: str = None):
        """
        Get Valorant player stats (Account & MMR).
        Usage: !val <Name#Tag> (e.g. !val Ezra#123)
        """
        if not RiotID:
            await ctx.reply("❌ Harap masukkan Riot ID! Contoh: `!val Name#Tag`")
            return
            
        if "#" not in RiotID:
            await ctx.reply("❌ Format Riot ID salah! Harus mengandung '#'. Contoh: `Name#Tag`")
            return
            
        name, tag = RiotID.split("#", 1)
        
        # Initial status message
        msg = await ctx.reply(f"🔍 Mencari data untuk **{name}#{tag}**...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # 1. Get Account Data (for Level, Card, Region)
                account_url = f"{self.base_url}/v1/account/{name}/{tag}"
                async with session.get(account_url, headers=self.headers) as resp:
                    if resp.status != 200:
                        error_data = await resp.json()
                        await msg.edit(content=f"❌ Gagal mengambil data akun. Error: {resp.status}\n`{error_data.get('message', 'Unknown error')}`")
                        return
                    account_data = await resp.json()
                
                # Check for region, default to 'ap' (Asia Pacific) if not found or handled differently
                region = account_data.get("data", {}).get("region", "ap")
                
                # 2. Get MMR Data (for Rank)
                # Using v2 MMR endpoint which usually works well for current rank info
                mmr_url = f"{self.base_url}/v2/mmr/{region}/{name}/{tag}"
                async with session.get(mmr_url, headers=self.headers) as resp:
                    # MMR endpoint might return 404 if user is unranked or long inactive, handle gracefully?
                    # But if account exists, it usually returns something.
                    mmr_data = None
                    if resp.status == 200:
                        mmr_data = await resp.json()
                
                # Prepare Embed Data
                data = account_data["data"]
                card_small = data["card"]["small"]
                card_wide = data["card"]["wide"]
                account_level = data["account_level"]
                last_update = data["last_update"]  # This is usually a string
                
                # MMR info
                current_tier_patched = "Unranked"
                ranking_in_tier = 0
                elo = 0
                mmr_change_to_last = 0
                image_rank = None
                
                if mmr_data and mmr_data.get("status") == 200:
                    m_data = mmr_data.get("data", {}).get("current_data", {})
                    current_tier_patched = m_data.get("currenttierpatched", "Unranked")
                    ranking_in_tier = m_data.get("ranking_in_tier", 0)
                    elo = m_data.get("elo", 0)
                    mmr_change_to_last = m_data.get("mmr_change_to_last_game", 0)
                    image_rank = m_data.get("images", {}).get("small", None)
                
                # Create Embed
                embed = discord.Embed(
                    title=f"Valorant Stats: {data['name']}#{data['tag']}",
                    description=f"Region: {region.upper()}",
                    color=discord.Color.red()
                )
                
                embed.set_thumbnail(url=card_small)
                if image_rank:
                     embed.set_thumbnail(url=image_rank) # Prefer rank icon as thumbnail if available

                embed.set_image(url=card_wide)
                
                embed.add_field(name="🏆 Rank", value=f"**{current_tier_patched}**", inline=True)
                embed.add_field(name="📈 RR (Rank Rating)", value=f"{ranking_in_tier} / 100", inline=True)
                embed.add_field(name="📊 ELO", value=f"{elo}", inline=True)
                
                # Add MMR change info
                change_symbol = "+" if mmr_change_to_last >= 0 else ""
                embed.add_field(name="🔄 Last Match MMR", value=f"{change_symbol}{mmr_change_to_last}", inline=True)
                
                embed.add_field(name="⭐ Account Level", value=f"{account_level}", inline=True)

                embed.set_footer(text="Data provided by HenrikDev API")

                await msg.edit(content=None, embed=embed)
                
        except Exception as e:
            print(f"[VALORANT ERROR] {e}")
            await msg.edit(content=f"❌ Terjadi kesalahan internal saat mengambil data.")

async def setup(bot):
    await bot.add_cog(Valorant(bot))
