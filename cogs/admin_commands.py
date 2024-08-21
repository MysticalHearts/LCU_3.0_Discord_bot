import discord
from discord.ext import commands
from cogs.events import db
# import tensorflow as tf
# from tensorflow import keras
# from sklearn.model_selection import train_test_split
# from sklearn.feature_extraction.text import CountVectorizer
# import numpy as np
import aiohttp
from cogs.utils.checks import load_env
from datetime import datetime, timezone

def check_support(ctx, bot):
    try:
        server = bot.get_guild(1000207936204836965)
        role1 = discord.utils.get(server.roles, id=1059547821101023242)
        role2 = discord.utils.get(server.roles, id=1059547830680813710)
        role3 = discord.utils.get(server.roles, id=1059547840839417907)
        if (
            role1 in ctx.author.roles
            or role2 in ctx.author.roles
            or role3 in ctx.author.roles
        ):
            return True
    except:
        server2 = bot.get_guild(1073712961253818459)
        role1 = discord.utils.get(server2.roles, id=1092525231832305748)
        role2 = discord.utils.get(server2.roles, id=1179295706192810054)
        role3 = discord.utils.get(server2.roles, id=1181758546602381422)
        role4 = discord.utils.get(server2.roles, id=1162801535932190891)
        role5 = discord.utils.get(server2.roles, id=1162168265330655243)

        if (
            role1 in ctx.author.roles
            or role2 in ctx.author.roles
            or role3 in ctx.author.roles
            or role4 in ctx.author.roles
            or role5 in ctx.author.roles
        ):
            return True

class admincmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.X_train = None

    @commands.command(description="testing command", extras={'category': "Staff"})
    @commands.is_owner()
    async def testing(self, ctx: commands.Context, arg: str = None):
        user = self.bot.get_user(ctx.author.id)
        await user.send("hi")

    @commands.command(
        description="This is a staff command", extras={"category": "Staff"}
    )
    async def check_setup(self, ctx: commands.Context, *, id: int):
        if check_support(ctx, self.bot):
            records = await db.setup.find_one({"guild_id": id}, {"_id": 0})

            records2 = await db.embeds.find_one({"guild_id": id}, {"_id": 0})

            records3 = await db.settings.find_one({"guild_id": id}, {"_id": 0})
            if not records and not records2 and not records3:
                return await ctx.send("This server has not been setup yet!")
            elif not records or not records2 or not records3:
                if records:
                    records = True
                if records2:
                    records2 = True
                if records3:
                    records3 = True
                await ctx.send("This server has an error with its setup (None/False = does not exsist : True = does exsist):\n\nSetup: {records}\nEmbeds: {records2}\nSettings: {records3}")
            em = discord.Embed(title=f"Setup for: {str(id)}", description="")
            em2 = discord.Embed(title=f"Embeds for: {str(id)}", description="")
            em3 = discord.Embed(title=f"Settings for: {str(id)}", description="")
            em4 = discord.Embed(title=f"Advertisement for: {str(id)}", description="")
            for record in records.items():
                if record[0] != "advertisement":
                    em.add_field(name=record[0], value=record[1])
                else:
                    em4.description = f"```{record[1]}```"

            for record in records2.items():
                em2.add_field(name=record[0], value=record[1])

            for record in records3.items():
                em3.add_field(name=record[0], value=record[1])

            await ctx.send(embed=em)
            await ctx.send(embed=em2)
            await ctx.send(embed=em3)
            try:
                await ctx.send(embed=em4)
            except:
                await ctx.send("Advertisement is too long to send in a message.")
        else:
            return

    @commands.command(
        description="This is a staff command", extras={"category": "Staff"}
    )
    @commands.is_owner()
    async def devdm(self, ctx, member: discord.Member, *, message):
        em = discord.Embed(title="Development Notification", description=message)
        try:
            await member.send(embed=em)
            await ctx.send("sent")
        except:
            await ctx.send("I cant send dms to this person!")

    @commands.command(
        description="This is a staff command", extras={"category": "Staff"}
    )
    @commands.is_owner()
    async def blacklist(self, ctx: commands.Context, member: int):
        record = await db.blacklists.find_one({"user_id": member})
        try:
            if isinstance(member, int):
                member = await self.bot.fetch_user(member)
                if not member:
                    return await ctx.send("Please provide a valid user id!")

                if not record and member:
                    await db.blacklists.insert_one({"user_id": member.id})
                    self.bot.blacklists.append(member.id)
                    return await ctx.send(f"Blacklisted <@{member.id}> (`{member.id}`).")
                else:
                    return await ctx.send(
                        f"<@{member.id}> (`{member.id}`) is already blacklisted."
                    )
            else:
                return await ctx.send("Please provide a valid user id.")
        except:
            return

    @commands.command(
        description="This is a staff command", extras={"category": "Staff"}
    )
    @commands.is_owner()
    async def unblacklist(self, ctx: commands.Context, member: int):
        member = await self.bot.fetch_user(member)
        record = await db.blacklists.find_one({"user_id": member.id})
        if record:
            await db.blacklists.delete_one({"user_id": member.id})
            self.bot.blacklists.remove(member.id)
            await ctx.send(f"un-blacklisted {member.mention} (`{member.id}`).")
        else:
            await ctx.send(f"{member.mention} is already un-blacklisted.")


async def setup(bot):
    await bot.add_cog(admincmd(bot))
