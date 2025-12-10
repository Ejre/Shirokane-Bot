"""
Fun Commands Cog
Custom fun commands like sens, agent, rank, etc.
"""

import discord
from discord.ext import commands
from data.user_data import user_agents, user_ranks


class Fun(commands.Cog):
    """Fun and custom commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def sens(self, ctx):
        """Display Tedi's gaming sensitivity settings."""
        embed = discord.Embed(
            title="🖱️ Sens Tedi Aditiya Andrianto",
            description="0.55 , DPI 800",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.command()
    async def agent(self, ctx):
        """Display user's favorite Valorant agents."""
        user_id = ctx.author.id
        
        if user_id in user_agents:
            agents = user_agents[user_id]
            agent_list = "\\n".join([f"🔹 {agent}" for agent in agents])
            
            embed = discord.Embed(
                title=f"🔥 Agent Favorit {ctx.author.display_name}",
                description=agent_list,
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("🚫 Kamu belum memiliki daftar agent favorit! Minta admin untuk menambahkannya.")
    
    @commands.command()
    async def rank(self, ctx):
        """Display user's Valorant rank."""
        user_id = ctx.author.id
        
        # Get user's rank or default to Unranked
        if user_id in user_ranks:
            rank_name, rank_image = user_ranks[user_id]
        else:
            rank_name = "Unranked"
            rank_image = "https://static.wikia.nocookie.net/valorant/images/b/b4/ActRank_lvl5.png/revision/latest?cb=20200805002326"
        
        embed = discord.Embed(
            title=f"🏆 Rank {ctx.author.name}",
            description=f"Anda berada di **{rank_name} Rank**!",
            color=discord.Color.blue()
        )
        embed.set_image(url=rank_image)
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def sp(self, ctx):
        """Fun command about Sipa."""
        embed = discord.Embed(
            title="Sipa karbit",
            description="Bukankah ini my",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.command()
    async def rry(self, ctx):
        """Display RRY information."""
        embed = discord.Embed(
            title="RRY",
            description="MIRANDA YULI ZAKIYANTI",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.command()
    async def duo(self, ctx):
        """Display duo information."""
        embed = discord.Embed(
            title="DUO",
            description="@tedyyad_ & @syifatf__",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)


async def setup(bot):
    """Required function to load the cog"""
    await bot.add_cog(Fun(bot))
