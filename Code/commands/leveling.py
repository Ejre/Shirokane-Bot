"""
Leveling System Cog
Handles XP tracking, leveling up, leaderboards, and auto-role rewards.
"""

import discord
from discord.ext import commands
import random
import time
from utils.database import get_user_data, update_user_xp, get_top_users, initialize_database

# Initialize DB on load
initialize_database()

# Role Rewards Configuration
# Format: {Level: Role_ID}
# REPLACE THESE IDs WITH YOUR ACTUAL SERVER ROLE IDs
# Format: {Level: Role_ID}
# REPLACE THESE IDs WITH YOUR ACTUAL SERVER ROLE IDs
ROLE_REWARDS = {
    1: 1473888417808121877,   # Beginner
    5: 1473887082941513830,   # Novice
    10: 1473887904366596167,  # Adventurer
    20: 1473887979079602321,  # Veteran
    40: 1473888043839782944,  # Hero
    50: 1473888079054897346   # Legend
}

class Leveling(commands.Cog):
    """Leveling system with XP and Rank commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.user) # 1 XP gain per 60s

    def get_xp_for_level(self, level):
        """Calculate total XP needed to reach a level."""
        # Formula: 100 * level^2
        # Lvl 1: 100
        # Lvl 2: 400
        # Lvl 5: 2500
        return 100 * (level ** 2)

    async def check_level_up(self, message, current_xp, current_level):
        """Check if user should level up and handle rewards."""
        user = message.author
        next_level = current_level + 1
        xp_needed = self.get_xp_for_level(next_level)
        
        if current_xp >= xp_needed:
            new_level = current_level + 1
            
            # Update DB
            update_user_xp(user.id, current_xp, new_level)
            
            # Send notification in CHANNEL
            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"Selamat {user.mention}, kamu naik ke **Level {new_level}**!",
                color=discord.Color.gold()
            )
            await message.channel.send(embed=embed)

            # Check Role Rewards
            await self.check_role_reward(message, user, new_level)
            
            return True
        return False

    async def check_role_reward(self, message, member, level):
        """Assign role if milestone reached."""
        role_id = ROLE_REWARDS.get(level)
        if role_id and role_id != 0:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role)
                    # Notify user about new role in CHANNEL
                    embed = discord.Embed(
                        title="🏅 Role Reward Unlocked!",
                        description=f"Kamu mendapatkan role baru: **{role.name}**!",
                        color=discord.Color.green()
                    )
                    await message.channel.send(embed=embed)
                except Exception as e:
                    print(f"[Leveling] Failed to add role {role_id} to {member}: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitor messages for XP gain."""
        if message.author.bot:
            return
        
        # Check Cooldown
        bucket = self._cd.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            return # User is on cooldown
        
        # Gain XP
        xp_gain = random.randint(15, 25)
        
        # Get current data
        user_data = get_user_data(message.author.id)
        current_xp = user_data["xp"] or 0
        current_level = user_data["level"] or 0
        
        new_xp = current_xp + xp_gain
        
        # Check Level Up (updates DB inside)
        leveled_up = await self.check_level_up(message.author, new_xp, current_level)
        
        if not leveled_up:
            # Just update XP
            update_user_xp(message.author.id, new_xp, current_level)

    @commands.command(aliases=["level"])
    async def rank(self, ctx, member: discord.Member = None):
        """Check your current level and XP."""
        member = member or ctx.author
        user_data = get_user_data(member.id)
        
        xp = user_data["xp"] or 0
        level = user_data["level"] or 0
        
        next_level_xp = self.get_xp_for_level(level + 1)
        prev_level_xp = self.get_xp_for_level(level)
        
        # Progress Calculation
        xp_needed_current_level = next_level_xp - prev_level_xp
        xp_progress = xp - prev_level_xp
        
        # Prevent division by zero for level 0
        if level == 0:
            percentage = (xp / next_level_xp) * 100
        else:
            percentage = (xp_progress / xp_needed_current_level) * 100
            
        percentage = min(max(percentage, 0), 100) # Clamp 0-100
        
        # Progress Bar
        bars = 10
        filled = int((percentage / 100) * bars)
        bar_str = "🟦" * filled + "⬜" * (bars - filled)
        
        embed = discord.Embed(
            title=f"📊 Rank: {member.display_name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Level", value=str(level), inline=True)
        embed.add_field(name="Total XP", value=f"{xp}", inline=True)
        embed.add_field(name="Progress", value=f"{bar_str} {int(percentage)}%", inline=False)
        embed.set_footer(text=f"Next Level at {next_level_xp} XP")
        
        await ctx.reply(embed=embed)

    @commands.command(aliases=["top", "lb"])
    async def leaderboard(self, ctx):
        """Show top 10 users by XP."""
        top_users = get_top_users(limit=10)
        
        if not top_users:
            await ctx.reply("Belum ada data leaderboard.")
            return

        embed = discord.Embed(
            title="🏆 Global Leaderboard",
            color=discord.Color.gold()
        )
        
        desc = ""
        for i, user in enumerate(top_users):
            user_id, xp, level = user
            
            # Fetch username
            try:
                member_obj = await self.bot.fetch_user(int(user_id))
                name = member_obj.display_name
            except:
                name = "Unknown User"
            
            medal = ""
            if i == 0: medal = "🥇"
            elif i == 1: medal = "🥈"
            elif i == 2: medal = "🥉"
            else: medal = f"#{i+1}"
            
            desc += f"**{medal} {name}** — Lvl {level} ({xp} XP)\n"
            
        embed.description = desc
        await ctx.reply(embed=embed)

    @commands.command()
    async def roles(self, ctx):
        """List all roles and their IDs (Helper for setup)."""
        roles = ctx.guild.roles
        desc = ""
        for role in reversed(roles): # Show highest role first
            if role.name != "@everyone":
                desc += f"{role.name}: `{role.id}`\n"
        
        embed = discord.Embed(
            title="📜 Server Roles",
            description=desc,
            color=discord.Color.blue()
        )
        await ctx.reply(embed=embed)

# Admin Restriction (User IDs who can use !setlevel and !addxp)
# REPLACE WITH YOUR USER ID(s)
ADMIN_IDS = [
    765561396225507349, # Contoh ID (Ganti dengan ID-mu!)
    1276872790376579073
]

class Leveling(commands.Cog):
    """Leveling system with XP and Rank commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.user) # 1 XP gain per 60s

    def is_admin(self, ctx):
        """Check if user is in ADMIN_IDS."""
        return ctx.author.id in ADMIN_IDS

    # ... (rest of methods)

    # ADMIN COMMANDS
    @commands.command()
    async def setlevel(self, ctx, member: discord.Member, level: int):
        """Set a user's level directly (Owner only)."""
        # Security Check
        if ctx.author.id not in ADMIN_IDS:
            await ctx.reply("⛔ **Akses Ditolak!** Command ini khusus Owner.")
            return

        xp_needed = self.get_xp_for_level(level)
        update_user_xp(member.id, xp_needed, level)
        
        # Check for role rewards for the new level
        await self.check_role_reward(ctx.message, member, level)
        
        embed = discord.Embed(
            title="🛠️ Admin Level Set",
            description=f"Set level **{member.display_name}** ke **Level {level}** (XP: {xp_needed}).",
            color=discord.Color.red()
        )
        await ctx.reply(embed=embed)

    @commands.command()
    async def addxp(self, ctx, member: discord.Member, amount: int):
        """Give XP to a user (Owner only)."""
        # Security Check
        if ctx.author.id not in ADMIN_IDS:
             await ctx.reply("⛔ **Akses Ditolak!** Command ini khusus Owner.")
             return

        user_data = get_user_data(member.id)
        current_xp = user_data["xp"] or 0
        current_level = user_data["level"] or 0
        
        new_xp = current_xp + amount
        
        # Check if this new XP causes a level up
        import math
        new_level = int(math.sqrt(new_xp / 100))
        
        # Determine if level changed
        if new_level > current_level:
            # Send Level Up message
             embed = discord.Embed(
                title="🎉 Admin Gift Level Up!",
                description=f"Selamat {member.mention}, kamu naik ke **Level {new_level}** berkat admin!",
                color=discord.Color.gold()
            )
             await ctx.send(embed=embed)
             # Check rewards
             await self.check_role_reward(ctx.message, member, new_level)
        
        update_user_xp(member.id, new_xp, new_level)
        
        embed = discord.Embed(
            title="🛠️ Admin XP Gift",
            description=f"Berikan **{amount} XP** ke {member.display_name}.\nTotal XP: {new_xp} (Lvl {new_level})",
            color=discord.Color.red()
        )
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
