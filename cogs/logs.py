import discord
from discord.ext import commands
import datetime
from datetime import timezone
from cogs.events import db   
from cogs.utils.checks import is_staff, get_info

class logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_group(with_app_command=True, extras={"Category": "Group"})
    async def log(self, ctx: commands.Context):
        pass
    

    @log.command(description="Create an STS log.", extras={"category": "Logs"})
    @is_staff()
    async def sts(self, ctx: commands.Context, host: discord.User,  minutes: int, *, reason: str):
        await ctx.defer()
        records = await db.settings.find_one({'guild_id': ctx.guild.id}, {"game_log_toggle": 1, "sts_channel": 1})
        try:
            if records["game_log_toggle"] == 0:
                return await ctx.send("It looks like you need to enable the game logging module!")
        except KeyError:
            return await ctx.send("It looks like you need to enable the game logging module!")

        if minutes > 60:
            return await ctx.send("Man. What a long STS. I can't log that.")
        guild_info = await get_info(ctx)
        embed = discord.Embed(title="STS Log", color=discord.Color.blue())
        embed.set_author(name=f"Logged by {ctx.author}", icon_url=f"{ctx.author.avatar.url}")
        embed.add_field(name="Host", value=f"{host.mention}")
        if minutes == 1:
            embed.add_field(name="Time", value=f"{minutes} minute")
        else:
            embed.add_field(name="Time", value=f"{minutes} minutes")
        embed.add_field(name="Reason", value=f"{reason}")
        embed.timestamp = datetime.datetime.now(timezone.utc)
        embed.set_footer(text=guild_info["server_name"])
        sts_schema = {
            "type": "sts",
            "author": ctx.author.id,
            "time": minutes,
            "reason": reason,
            "guild_id": ctx.guild.id,
            "date": datetime.datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0),
        }
        await db.logs.insert_one(sts_schema)
        channel = ctx.guild.get_channel(records["sts_channel"])
        await ctx.send("STS Logged!", delete_after=3)
        await channel.send(embed=embed)
        
    @log.command(description="Create a priority log.", extras={"category": "Logs"})
    @is_staff()
    async def prty(self, ctx: commands.Context, minutes: int, *, reason: str):
        await ctx.defer()

        records = await db.settings.find_one({'guild_id': ctx.guild.id}, {"game_log_toggle": 1, "prty_channel": 1})
        try:
            if records["game_log_toggle"] == 0:
                return await ctx.send("It looks like you need to enable the game logging module!")
        except KeyError:
            return await ctx.send("It looks like you need to enable the game logging module!")

        if minutes > 120:
            return await ctx.send("Man. What a long priority. I can't log that.")
        guild_info = await get_info(ctx)
        embed = discord.Embed(title="Priority Log", color=discord.Color.yellow())
        embed.set_author(name=f"Logged by {ctx.author}", icon_url=f"{ctx.author.avatar.url}")
        if minutes == 1:
            embed.add_field(name="Time", value=f"{minutes} minute")
        else:
            embed.add_field(name="Time", value=f"{minutes} minutes")
        embed.add_field(name="Reason", value=f"{reason}")
        embed.timestamp = datetime.datetime.now(timezone.utc)
        embed.set_footer(text=guild_info["server_name"])
        prty_schema = {
            "type": "prty",
            "author": ctx.author.id,
            "time": minutes,
            "reason": reason,
            "guild_id": ctx.guild.id,
        }
        await db.logs.insert_one(prty_schema)
        channel = ctx.guild.get_channel(records["prty_channel"])
        await ctx.send("PRTY Logged!", delete_after=3)
        await channel.send(embed=embed)
        
    @log.command(description="Create a ridealong log.", extras={"category": "Logs"})
    @is_staff()
    async def ridealong(self, ctx: commands.Context, host: discord.User, user: discord.User, result: str, *, feedback: str):
        await ctx.defer()

        records = await db.settings.find_one({'guild_id': ctx.guild.id}, {"game_log_toggle": 1, "ra_channel": 1})
        try:
            if records["game_log_toggle"] == 0:
                return await ctx.send("It looks like you need to enable the game logging module!")
        except KeyError:
            return await ctx.send("It looks like you need to enable the game logging module!")

        guild_info = await get_info(ctx)
        embed = discord.Embed(title="Ridealong Log", color=discord.Color.blue())
        embed.set_author(name=f"Logged by {ctx.author}", icon_url=f"{ctx.author.avatar.url}")
        embed.add_field(name="Host", value=f"{host.mention}", inline=True)
        embed.add_field(name="User", value=f"{user.mention}", inline=True)
        embed.add_field(name="Result", value=f"{result}", inline=True)
        embed.add_field(name="Feedback", value=f"{feedback}", inline=True)
        embed.timestamp = datetime.datetime.now(timezone.utc)
        embed.set_footer(text=guild_info["server_name"])
        ra_schema = {
            "type": "ra",
            "author": ctx.author.id,
            "host": host.name,
            "user": user.name,
            "result": result,
            "feedback": feedback,
            "guild_id": ctx.guild.id,
        }
        await db.logs.insert_one(ra_schema)
        channel = ctx.guild.get_channel(records["ra_channel"])
        await ctx.send("Ridealong Logged!", delete_after=3)
        await channel.send(embed=embed)
    
    @log.command(description="Create a ridealong log.", extras={"category": "Logs"})
    @is_staff()
    async def message(self, ctx: commands.Context, host: discord.User, *, message: str):
        await ctx.defer()

        records = await db.settings.find_one({'guild_id': ctx.guild.id}, {"game_log_toggle": 1, "message_channel": 1})
        try:
            if records["game_log_toggle"] == 0:
                return await ctx.send("It looks like you need to enable the game logging module!")
        except KeyError:
            return await ctx.send("It looks like you need to enable the game logging module!")

        guild_info = await get_info(ctx)
        embed = discord.Embed(title="Message Log", color=discord.Color.blue())
        embed.set_author(name=f"Logged by {ctx.author}", icon_url=f"{ctx.author.avatar.url}")
        embed.add_field(name="Host", value=f"{host.mention}", inline=True)
        embed.add_field(name="Message", value=f"{message}", inline=True)
        embed.timestamp = datetime.datetime.now(timezone.utc)
        embed.set_footer(text=guild_info["server_name"])
        ra_schema = {
            "type": "message",
            "author": ctx.author.id,
            "host": host.name,
            "message": message,
            "guild_id": ctx.guild.id,
        }
        await db.logs.insert_one(ra_schema)
        channel = ctx.guild.get_channel(records["message_channel"])
        await ctx.send("Message Logged!", delete_after=3)
        await channel.send(embed=embed)
        
        

async def setup(bot):
    await bot.add_cog(logs(bot))