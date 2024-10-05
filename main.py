mport discord
import os
import sys
import json
from discord.ext import commands
from discord import app_commands
import asyncio
import sqlite3
from cogs.utils.checks import *
import re
import time
import typing

intent = discord.Intents.default()
intent.message_content = True
intent.members = True
bot = commands.Bot(command_prefix="t-", intents=intent)
bot.remove_command('help')


def check_if_it_is_me(ctx):
    return ctx.message.author.id == 676895030094331915 or ctx.message.author.id == 687423771346599946 or ctx.message.author.id == 688919016722661452

async def load():
  for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
      await bot.load_extension(f'cogs.{filename[:-3]}')

async def main():
  await load()
  await bot.start("MTI4OTkyOTAzMjY0ODg4NDI4NA.GsXPDz.Kf76maU7j-tZu8NuozhIo3bNf_OSqGJZJ0RCBA")

@bot.command(pass_context=True)
@commands.check(check_if_it_is_me)
async def get(ctx, extension):
  await bot.load_extension(f"cogs.{extension}")
  await ctx.send("Command(s) was loaded!")

@bot.command(pass_context=True)
@commands.check(check_if_it_is_me)
async def delete(ctx, extension):
  await bot.unload_extension(f"cogs.{extension}")
  await ctx.send("Command(s) was deleted!")

@bot.command(pass_context=True)
@commands.check(check_if_it_is_me)
async def reload(ctx, extension):
  await bot.unload_extension(f"cogs.{extension}")
  await bot.load_extension(f"cogs.{extension}")
  await ctx.send("Command(s) was reloaded!")

#This command is not to be touched by anyone or face infractions
@bot.command()
@commands.is_owner()
async def sync(ctx, *, msg: typing.Optional[int] = None):
  if msg is None:
    await ctx.bot.tree.sync()
  else:
    await ctx.bot.tree.sync(guild=discord.Object(id = msg))
  await ctx.send(f"commands are synced")

@bot.command()
@commands.check(check_if_it_is_me)
async def testing(ctx: commands.Context, *, message: str):
  con = sqlite3.connect("cogs/data/main_db.db")
  cur = con.cursor()
  res = cur.execute(f"SELECT * FROM promos")
  result = res.fetchall()
  print(result)

@bot.command()
@commands.check(check_if_it_is_me)
async def devdm(ctx, member: discord.Member, *, message):
  em = discord.Embed(title="Development Notification", description=message)
  await member.send(embed=em)
  await ctx.send("sent")

asyncio.run(main())

@bot.command(pass_context=True)
@commands.check(check_if_it_is_me)
async def delete(ctx, extension):
  await bot.unload_extension(f"cogs.{extension}")
  await ctx.send("Command(s) was deleted!")

@bot.command(pass_context=True)
@commands.check(check_if_it_is_me)
async def reload(ctx, extension):
  await bot.unload_extension(f"cogs.{extension}")
  await bot.load_extension(f"cogs.{extension}")
  await ctx.send("Command(s) was reloaded!")

#This command is not to be touched by anyone or face infractions
@bot.command()
@commands.is_owner()
async def sync(ctx, *, msg: typing.Optional[int] = None):
  if msg is None:
    await ctx.bot.tree.sync()
  else:
    await ctx.bot.tree.sync(guild=discord.Object(id = msg))
  await ctx.send(f"commands are synced")

@bot.command()
@commands.check(check_if_it_is_me)
async def testing(ctx: commands.Context, *, message: str):
  con = sqlite3.connect("cogs/data/main_db.db")
  cur = con.cursor()
  res = cur.execute(f"SELECT * FROM promos")
  result = res.fetchall()
  print(result)

@bot.command()
@commands.check(check_if_it_is_me)
async def devdm(ctx, member: discord.Member, *, message):
  em = discord.Embed(title="Development Notification", description=message)
  await member.send(embed=em)
  await ctx.send("sent")

asyncio.run(main())
asyncio.set_event_loop(asyncio.new_event_loop())

            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")
        await bot.load_extension("cogs.utils.hot_reload")
        print("All cogs loaded successfully!")


intent = discord.Intents.default()
intent.message_content = True
intent.members = True
bot = Bot(
    command_prefix=load_env.prefix(),
    intents=intent,
    chunk_guilds_at_startup=False,
    help_command=None,
    allowed_mentions=discord.AllowedMentions(
        replied_user=True, everyone=True, roles=True
    ),
)

@bot.before_invoke
async def before_invoke(ctx):
    for user in ctx.bot.blacklists:
        if ctx.command.name != "unblacklist":
            if ctx.author.id == int(user):
                await ctx.send("You are blacklisted from LCU. Join our support server to appeal.")
                raise commands.CheckFailure("Blacklisted")
    
    if ctx.channel.type == discord.ChannelType.private:
        raise commands.NoPrivateMessage(
            "This command cannot be used in private messages."
        )


bot.run(load_env.token())
