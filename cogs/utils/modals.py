import discord
from discord import Interaction
from cogs.utils.checks import get_info
import re
from cogs.events import db

class MSessionBanner(discord.ui.Modal, title='Configuration'):

    answer = discord.ui.TextInput(label="Session Banner", placeholder="Say 'reset' to reset to none.")

    async def on_submit(self, ctx: Interaction):
       
      answer = str(self.answer)
      if answer.startswith("https://cdn.discordapp.com/attachments/") or answer.startswith("https://media.discordapp.net/attachments/"):
        await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'session_banner_link': answer}}
        )
        await ctx.response.send_message(f"It has now been configured!", ephemeral=True)
      elif answer == "reset":
        await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'session_banner_link': "skipped"}}
        )
        await ctx.response.send_message(f"It has now been configured!", ephemeral=True)
      else:
        await ctx.response.send_message(f"Invalid, it must be from `https://cdn.discordapp.com/attachments/` or `https://media.discordapp.net/attachments/`", ephemeral=True)

class MShutdownBanner(discord.ui.Modal, title='Configuration'):

    answer = discord.ui.TextInput(label="Shutdown Banner", placeholder="Say 'reset' to reset to none.")

    async def on_submit(self, ctx: Interaction):
       
      answer = str(self.answer)
      if answer.startswith("https://cdn.discordapp.com/attachments/") or answer.startswith("https://media.discordapp.net/attachments/"):
        await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'shutdown_banner_link': answer}}
        )
        await ctx.response.send_message(f"It has now been configured!", ephemeral=True)
      elif answer == "reset":
        await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'session_banner_link': "skipped"}}
        )
        await ctx.response.send_message(f"It has now been configured!", ephemeral=True)
      else:
        await ctx.response.send_message(f"Invalid, it must be from `https://cdn.discordapp.com/attachments/` or `https://media.discordapp.net/attachments/`", ephemeral=True)

class MEmoji(discord.ui.Modal, title='Configuration'):

    answer = discord.ui.TextInput(label="Emoji", placeholder="Must be a custom emoji.")

    async def on_submit(self, ctx: Interaction):
      answer = str(self.answer)
       
      if answer.startswith("<") and answer.endswith(">"):
        await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'emoji_id': answer}}
        )
        await ctx.response.send_message(f"It has now been configured!", ephemeral=True)
      else:
        await ctx.response.send_message(f"Please retry, it must start with < and end with >. Example: <emojiname:emojiid>", ephemeral=True)

class MShutdownDescription(discord.ui.Modal, title='Configuration'):

    answer = discord.ui.TextInput(label="Shutdown Description", placeholder="Say \"reset\" to reset to default.")

    async def on_submit(self, ctx: Interaction):
      answer = str(self.answer)
        
      if answer != "reset":
        await db.embeds.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'shutdown_description': answer}}
        )
        await ctx.response.send_message(f"Configured!", ephemeral=True)
      elif answer == "reset":
        await db.embeds.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'shutdown_description': str("{emoji} *Our ingame server has been shutdown. Do not join our server until we start up the server again.*\n\n**Issued on:** {timestamp}")}}
        )
        await ctx.response.send_message(f"Reset.", ephemeral=True)
#-----------------------------------------

class MServerName(discord.ui.Modal, title='Configuration'):

    answer = discord.ui.TextInput(label="Server Name")

    async def on_submit(self, ctx: Interaction):
      answer = str(self.answer)

      await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'server_name': answer}}
      )
      await ctx.response.send_message(f"It has now been configured!", ephemeral=True)

class MServerOwner(discord.ui.Modal, title='Configuration'):

    answer = discord.ui.TextInput(label="Server Owner")

    async def on_submit(self, ctx: Interaction):
      answer = str(self.answer)
      
      await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'server_owner': answer}}
      )
      await ctx.response.send_message(f"It has now been configured!", ephemeral=True)

class MCode(discord.ui.Modal, title='Configuration'):

    answer = discord.ui.TextInput(label="ROBLOX Code")

    async def on_submit(self, ctx: Interaction):
      answer = str(self.answer)

      if " " in answer:
        await ctx.response.send_message("Your server code cannot have spaces!", ephemeral=True)
        return
      
      await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'server_code': answer}}
      )
      await db.settings.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'session_link': f"https://policeroleplay.community/join/{answer}"}}
      )
      await ctx.response.send_message(f"It has now been configured!", ephemeral=True)

class MReminderText(discord.ui.Modal, title='Configuration'):

    answer = discord.ui.TextInput(label="M Command Text", style=discord.TextStyle.paragraph)

    async def on_submit(self, ctx: Interaction):
      answer = str(self.answer)
      
      await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'m_command_text': answer}}
      )
      await ctx.response.send_message(f"It has now been configured!", ephemeral=True)

class MVotes(discord.ui.Modal, title='Configuration'):

    answer = discord.ui.TextInput(label="Votes", placeholder = "Must be a number")

    async def on_submit(self, ctx: Interaction):
      
      answer = str(self.answer)

      if answer.isnumeric() != True:
        return await ctx.response.send_message(f"Please provide a number (e.g 1, 2, 3)", ephemeral=True)

      await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'vote_number': int(answer)}}
      )
      await ctx.response.send_message(f"It has now been configured!", ephemeral=True)
      

class MAdvert(discord.ui.Modal, title='Configuration'):

    answer = discord.ui.TextInput(label="Advertisement", style=discord.TextStyle.paragraph)

    async def on_submit(self, ctx: Interaction):
      answer = str(self.answer)
      
      await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'advertisement': answer}}
      )
      await ctx.response.send_message(f"It has now been configured!", ephemeral=True)

class MSessionLink(discord.ui.Modal, title='Configuration'):

    answer = discord.ui.TextInput(label="Session Link", placeholder="Say 'reset' to reset to default.")

    async def on_submit(self, ctx: Interaction):
      await ctx.response.defer()
       
      answer = str(self.answer)
      if answer.startswith("https://"):
        await db.settings.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'session_link': answer}}
        )
        await ctx.followup.send(f"It has now been configured!", ephemeral=True)
      elif answer == "reset":
        guild_info = await get_info(ctx)
        await db.settings.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'session_link': f"https://policeroleplay.community/join/{guild_info['server_code']}"}}
        )
        await ctx.followup.send(f"It has now been configured!", ephemeral=True)
      else:
        await ctx.followup.send(f"Invalid, it must be a link!", ephemeral=True)

class MSVoteBanner(discord.ui.Modal, title='Setup'):
   
    answer = discord.ui.TextInput(label="SVote Banner", placeholder="'reset' to reset the banner")

    async def on_submit(self, ctx: Interaction):
      await ctx.response.defer()
       
      answer = str(self.answer)
      if answer.startswith("https://cdn.discordapp.com/attachments/") or answer.startswith("https://media.discordapp.net/attachments/"):
        await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'svote_banner_link': answer}}
        )
        self.stop()
        await ctx.followup.send(f"It has now been configured!", ephemeral=True)
      elif answer == "reset":
        await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'svote_banner_link': "skipped"}}
        )
        await ctx.response.send_message(f"It has now been configured!", ephemeral=True)
      else:
        self.stop()
        await ctx.followup.send(f"Invalid, it must be from `https://cdn.discordapp.com/attachments/` or `https://media.discordapp.net/attachments/`", ephemeral=True)



class MLOALength(discord.ui.Modal, title='Settings'):
      
    answer = discord.ui.TextInput(label="LOA Min Time", placeholder="How much time for the minimum allowed LOA.")
    answer1 = discord.ui.TextInput(label="LOA Max Time", placeholder="")

    async def on_submit(self, ctx: Interaction):
      await ctx.response.defer()
       
      minAnwer = str(self.answer)
      maxAnswer = str(self.answer1)

      search = re.match(r"((\d+)[y])?((\d+)[m])?((\d+)[w])?((\d+)[d])?", minAnwer)
      search1 = re.match(r"((\d+)[y])?((\d+)[m])?((\d+)[w])?((\d+)[d])?", maxAnswer)

      if not search.group(2) and not search.group(4) and not search.group(6) and not search.group(8) or not search1.group(2) and not search1.group(4) and not search1.group(6) and not search1.group(8):
        await ctx.followup.send("Please use the format (Xy|Xm|Xw|Xd).")
      else:
        self.stop()
        await db.settings.update_one(
          {'guild_id': int(ctx.guild.id)},
          {'$set': {'loa_min': minAnwer}}
        )
        await db.settings.update_one(
          {'guild_id': int(ctx.guild.id)},
          {'$set': {'loa_max': maxAnswer}}
        )



        
      
      