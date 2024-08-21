import discord
from discord.ext import commands
from discord.ui import View
from discord import Interaction
from cogs.utils.checks import *
import re
import os
from dotenv import load_dotenv
from cogs.events import db
import time

async def convertEmbed(ctx, description, title, footer, author, guild_info, timestamp, type):
    #description for session commands
    description = str(description)
    try:
      new_string = description.replace("{timestamp}", f"<t:{timestamp}:F>")
      new_string1 = new_string.replace("{ro_name}", guild_info['server_name'])
      new_string2 = new_string1.replace("{ro_owner}", guild_info['server_owner'])
      new_string3 = new_string2.replace("{ro_code}", guild_info['server_code'])
      new_string4 = new_string3.replace("{server_name}", f"{guild_info['server_name']}")
      try:
        new_string5 = new_string4.replace("{author_name}", f"{ctx.author.display_name}")
      except:
        new_string5 = new_string4.replace("{author_name}", f"{ctx.user.display_name}")
      emoji_id = guild_info['emoji_id']
      
      if emoji_id == "skipped":
        emoji_id = ""
        new_string6 = new_string5.replace("{emoji}", emoji_id)
      else:
        new_string6 = new_string5.replace("{emoji}", emoji_id)

      description = str(new_string6)
   
    except Exception as e:
       raise commands.CommandInvokeError(e)
    
    #title for session commands
    title = str(title)
    try:
      if title == 'None':
        if type == "session":
          title = "{emoji} {server_name} Session Startup"
        elif type == "shutdown":
          title = "{emoji} {server_name} Session Shutdown"
        elif type == "svote":
          title = "{emoji} {server_name} Session Vote"
        elif type == "warn":
          title = "{emoji} Staff Warning"
        elif type == "strike":
          title = "{emoji} Staff Strike"
        elif type == "demote":
          title = "{emoji} Staff Demotion"
        elif type == "promote":
          title = "{emoji} Staff Promotion"
      new_des = title.replace("{server_name}", f"{ctx.guild.name}")
      try:
        new_des2 = new_des.replace("{author_name}", f"{ctx.author.display_name}")
      except:
        new_des2 = new_des.replace("{author_name}", f"{ctx.user.display_name}")
      emoji_id = guild_info['emoji_id']

      if emoji_id == None or emoji_id == "skipped":
        emoji_id = ""
        new_string3 = new_des2.replace("{emoji}", emoji_id)
      else:
        new_string3 = new_des2.replace("{emoji}", emoji_id)

      title = str(new_string3)

    except Exception as e:
       raise commands.CommandInvokeError(e)
    
    #footer for session commands
    footer = str(footer)
    if footer:
      try:
        try:
          new_des = footer.replace("{author_name}", f"{ctx.author.display_name}")
        except:
          new_des = footer.replace("{author_name}", f"{ctx.user.display_name}")
        new_string1 = new_des.replace("{ro_name}", guild_info['server_name'])
        new_string2 = new_string1.replace("{ro_owner}", guild_info['server_owner'])
        new_string3 = new_string2.replace("{ro_code}", guild_info['server_code'])
        footer = new_string3
      except Exception as e:
        raise commands.CommandInvokeError(e)
    else:
      footer = None
    
    #author for session commands
    if author:
      try:
        try:
          author_name = author.replace("{author_name}", f"{ctx.author.display_name}")
        except:
          author_name = author.replace("{author_name}", f"{ctx.user.display_name}")
      except Exception as e:
        raise commands.CommandInvokeError(e)
    else:
      author_name = None
    

    
    return description, title, footer, author_name

class MDescription(discord.ui.Modal, title='Description Changer'):
    answer = discord.ui.TextInput(label="Description", placeholder="Your description", style=discord.TextStyle.paragraph)

    async def on_submit(self, ctx: Interaction):
      
      # await ctx.response.defer()
      self.stop()
      # await db.embeds.update_one({"guild_id": ctx.guild.id}, {'$set': {"session_description": str(self.answer)}})
      
      await ctx.response.send_message(f"Edited. Click on \"Submit\" to save.", ephemeral=True)

class MTitle(discord.ui.Modal, title='Title Changer'):
    answer = discord.ui.TextInput(label="Title", placeholder="{emoji} is a placeholder for your server emoji.")

    async def on_submit(self, ctx: Interaction):
      
      # await ctx.response.defer()
      self.stop()
      # await db.embeds.update_one({"guild_id": ctx.guild.id}, {'$set': {"session_description": str(self.answer)}})
      await ctx.response.send_message(f"Edited. Click on \"Submit\" to save.", ephemeral=True)


class MFooter(discord.ui.Modal, title='Footer Changer'):
    answer = discord.ui.TextInput(label="Footer", placeholder="Your footer")

    async def on_submit(self, ctx: Interaction):
      
      # await ctx.response.defer()
      self.stop()
      # await db.embeds.update_one({"guild_id": ctx.guild.id}, {'$set': {"session_description": str(self.answer)}})
      await ctx.response.send_message(f"Edited. Click on \"Submit\" to save.", ephemeral=True)

class MAuthor(discord.ui.Modal, title='Author Changer'):
    answer = discord.ui.TextInput(label="Author Name", placeholder="Your author name")
    answer1 = discord.ui.TextInput(label="Author Image", placeholder="Your author image. Must be an image link.")

    async def on_submit(self, ctx: Interaction):
      
      # await ctx.response.defer()
      self.stop()
      # await db.embeds.update_one({"guild_id": ctx.guild.id}, {'$set': {"session_description": str(self.answer)}})
      await ctx.response.send_message(f"Edited. Click on \"Submit\" to save.", ephemeral=True)

async def get_embed_info(ctx, type):
    keys_to_extract = ['description', 'color', 'title', 'footer', 'author_link', 'author_name']
    records = await db.embeds.find_one({'guild_id': int(ctx.guild.id)}, {f'{type}_{key}': 1 for key in keys_to_extract})

    result = {}
    for key in keys_to_extract:
        result[key] = records.get(f'{type}_{key}', None if key in ['footer', 'author_link', 'author_name'] else 'None')

    return tuple(result.values())



async def get_info(ctx):
    records = await db.setup.find_one({"$or": [{"guild_id": int(ctx.guild.id)}, {"guild_id": str(ctx.guild.id)}]})
    if records is None:
        return False
    return records

async def complete(ctx: Interaction):
    guild_info = await get_info(ctx)

    description = f"""**Session Banner:** `{guild_info['session_banner_link']}`\n
    **Shutdown Banner:** `{guild_info['shutdown_banner_link']}`\n
    **SVote Banner:** `{guild_info['svote_banner_link']}`\n
    **Server Emoji:** {guild_info['emoji_id']}\n
    **Moderation Roles:** {await convertInto(ctx, guild_info['mod_roles_id'])}\n
    **Staff Roles:** {await convertInto(ctx, guild_info['staff_roles_id'])}\n
    **Management Roles:** {await convertInto(ctx, guild_info['management_roles_id'])}\n
    **Session Role:** <@&{guild_info['session_role_id']}>\n
    **Staff Request Channel:** <#{guild_info['ping_channel']}>\n
    **ROBLOX Server Name:** `{guild_info['server_name']}`\n
    **ROBLOX Server Owner:** `{guild_info['server_owner']}`\n
    **ROBLOX Code:** `{guild_info['server_code']}`\n
    **Number of Votes:** `{guild_info['vote_number']}`\n
    """

    em = discord.Embed(title="Your Server is All Setup!", description=description)

    await ctx.channel.send(embed=em)

async def startSetup(ctx: Interaction, **guild_info):
  shutdown_description = "{emoji} *Our ingame server has been shutdown. Do not join our server until we start up the server again.*\n\n**Issued on:** {timestamp}"
  session_description = "Our ingame server has been started up! If you voted, you must join the server, failure to do so will result in a infraction.\n\nServer Name: **{ro_name}**\nServer Owner: **{ro_owner}**\nServer Code: **{ro_code}** (Case Sensitive)\n\n**Issued on:** {timestamp}"
  svote_description = "{emoji} **Management Team** *have decided to start a session poll, vote below if you are willing to attend this session!*\n\n**Issued on:** {timestamp}"
  infract_description = "The HR Team has decided to take the following actions upon you. Please do not start any drama about this."
  color = "(44, 47, 51)"
  session_color = "(43, 112, 182)"
  shutdown_color = "(247, 200, 137)"
  svote_color = "(176, 207, 251)"
  session_title = f"{ctx.guild.name} Session Startup"
  shutdown_title = f"{ctx.guild.name} Session Shutdown"
  svote_title = f"{ctx.guild.name} Session Vote"
  warn_title = f"{guild_info['emoji']} Staff Warn"
  strike_title = f"{guild_info['emoji']} Staff Strike"
  promote_title = f"{guild_info['emoji']} Staff Promotion"
  demote_title = f"{guild_info['emoji']} Staff Demotion"
  blank = ""
  banners = guild_info['banners']

  result = await db.setup.find_one({"guild_id": ctx.guild.id})

  if not result:
    setup_doc = {
        'guild_id': ctx.guild.id,
        'session_banner_link': str(banners['session_banner']),
        'shutdown_banner_link': str(banners['shutdown_banner']),
        'emoji_id': str(guild_info['emoji']),
        'staff_roles_id': str(guild_info['staff_roles']),
        'management_roles_id': str(guild_info['management_roles']),
        'session_role_id': str(guild_info['ssu_ping']),
        'm_command_channel': blank,
        'ping_channel': str(guild_info['requests_channel']),
        'server_name': str(guild_info['server_name']),
        'server_owner': str(guild_info['server_owner']),
        'server_code': str(guild_info['server_code']),
        'vote_number': int(guild_info['votes']),
        'm_command_text': blank,
        'advertisement': str(guild_info['advertisement']),
        'on_shift_role': 1,
        'mod_roles_id': str(guild_info['moderation_roles']),
        'svote_banner_link': str(banners['svote_banner'])
    }
    await db.setup.insert_one(setup_doc)

    embeds_doc = {
        'guild_id': int(ctx.guild.id),
        'shutdown_author_link': blank,
        'shutdown_author_name': blank,
        'shutdown_title': shutdown_title,
        'shutdown_description': shutdown_description,
        'shutdown_footer': blank,
        'session_author_link': blank,
        'session_author_name': blank,
        'session_title': session_title,
        'session_description': session_description,
        'session_footer': blank,
        'svote_author_link': blank,
        'svote_author_name': blank,
        'svote_title': svote_title,
        'svote_description': svote_description,
        'svote_footer': blank,
        'warn_author_link': blank,
        'warn_author_name': blank,
        'warn_title': warn_title,
        'warn_description': infract_description,
        'warn_footer': blank,
        'strike_author_link': blank,
        'strike_author_name': blank,
        'strike_title': strike_title,
        'strike_description': infract_description,
        'strike_footer': blank,
        'promote_author_link': blank,
        'promote_author_name': blank,
        'promote_title': promote_title,
        'promote_description': "Congratulations on getting promoted!",
        'promote_footer': blank,
        'demote_author_link': blank,
        'demote_author_name': blank,
        'demote_title': demote_title,
        'demote_description': infract_description,
        'demote_footer': blank,
        'session_color': session_color,
        'shutdown_color': shutdown_color,
        'svote_color': svote_color,
        'warn_color': color,
        'strike_color': color,
        'promote_color': color,
        'demote_color': color,
        'commands_color': color
    }
    await db.embeds.insert_one(embeds_doc)

    settings_doc = {
        'guild_id': int(ctx.guild.id),
        'm_command_toggle': 1,
        'session_link': f"https://policeroleplay.community/join/{guild_info['server_code']}",
        'loa_toggle': 0,
        'svote_here_toggle': 1,
        'loa_role': 1,
        'loa_channel': 1,
        'reminders_toggle': 0,
    }
    await db.settings.insert_one(settings_doc)

    return await complete(ctx)
  else:

    await db.embeds.delete_one({'guild_id': ctx.guild.id})

    await db.settings.delete_one({'guild_id': ctx.guild.id})

    await db.setup.delete_one({'guild_id': ctx.guild.id})

    setup_doc = {
        'guild_id': ctx.guild.id,
        'session_banner_link': str(banners['session_banner']),
        'shutdown_banner_link': str(banners['shutdown_banner']),
        'emoji_id': str(guild_info['emoji']),
        'staff_roles_id': str(guild_info['staff_roles']),
        'management_roles_id': str(guild_info['management_roles']),
        'session_role_id': str(guild_info['ssu_ping']),
        'm_command_channel': blank,
        'ping_channel': str(guild_info['requests_channel']),
        'server_name': str(guild_info['server_name']),
        'server_owner': str(guild_info['server_owner']),
        'server_code': str(guild_info['server_code']),
        'vote_number': int(guild_info['votes']),
        'm_command_text': blank,
        'advertisement': str(guild_info['advertisement']),
        'on_shift_role': 1,
        'mod_roles_id': str(guild_info['moderation_roles']),
        'svote_banner_link': str(banners['svote_banner'])
    }

    await db.setup.insert_one(setup_doc)

    embeds_doc = {
        'guild_id': int(ctx.guild.id),
        'shutdown_author_link': blank,
        'shutdown_author_name': blank,
        'shutdown_title': shutdown_title,
        'shutdown_description': shutdown_description,
        'shutdown_footer': blank,
        'session_author_link': blank,
        'session_author_name': blank,
        'session_title': session_title,
        'session_description': session_description,
        'session_footer': blank,
        'svote_author_link': blank,
        'svote_author_name': blank,
        'svote_title': svote_title,
        'svote_description': svote_description,
        'svote_footer': blank,
        'warn_author_link': blank,
        'warn_author_name': blank,
        'warn_title': warn_title,
        'warn_description': infract_description,
        'warn_footer': blank,
        'strike_author_link': blank,
        'strike_author_name': blank,
        'strike_title': strike_title,
        'strike_description': infract_description,
        'strike_footer': blank,
        'promote_author_link': blank,
        'promote_author_name': blank,
        'promote_title': promote_title,
        'promote_description': "Congratulations on getting promoted!",
        'promote_footer': blank,
        'demote_author_link': blank,
        'demote_author_name': blank,
        'demote_title': demote_title,
        'demote_description': infract_description,
        'demote_footer': blank,
        'session_color': session_color,
        'shutdown_color': shutdown_color,
        'svote_color': svote_color,
        'warn_color': color,
        'strike_color': color,
        'promote_color': color,
        'demote_color': color,
        'commands_color': color
    }

    await db.embeds.insert_one(embeds_doc)

    settings_doc = {
        'guild_id': int(ctx.guild.id),
        'm_command_toggle': 1,
        'session_link': f"https://policeroleplay.community/join/{guild_info['server_code']}",
        'loa_toggle': 0,
        'svote_here_toggle': 1,
        'loa_role': 1,
        'loa_channel': 1,
        'reminders_toggle': 0,
    }
    await db.settings.insert_one(settings_doc)

    return await complete(ctx)

async def getColor(ctx, sql_column):
    try:
        record = await db.embeds.find_one({"guild_id": ctx.guild.id}, {sql_column: 1})
        records = record.get(sql_column)

        if not records:
            await ctx.send("Color is not valid, please reset-up your colors")
            return discord.Color.default()

        match = re.match(r'\((\d+), (\d+), (\d+)\)', str(records))
        if not match:
            await ctx.send("Color is not valid, please reset-up your colors")
            return discord.Color.default()

        r, g, b = map(int, match.groups())
        color = discord.Color.from_rgb(r, g, b)

        return color
    except:
        return discord.Color.from_rgb(44, 47, 51)
    
async def checkStaff(ctx: commands.Context):
    if not ctx.guild or ctx.guild == None:
      return False
    elif ctx.guild.chunked:
      pass
    else:
      await ctx.guild.chunk()

    guild_info = await get_info(ctx)
    
    if not guild_info:
        return "invalid"
    
    member_list = guild_info['staff_roles_id']
    
    if isinstance(member_list, list):
        pass
    else:
        member_list = member_list.strip('[]').split(', ')
    
    for member in member_list:
        try:
            staff = discord.utils.get(ctx.guild.roles, id=int(member))
        except ValueError as e:
            raise commands.CommandInvokeError(e)

        if staff in ctx.author.roles:
            return True

    return False

async def checkManage(ctx: commands.Context):
    if not ctx.guild or ctx.guild == None:
      return False
    elif ctx.guild.chunked:
      pass
    else:
      await ctx.guild.chunk()

    guild_info = await get_info(ctx)
    
    if not guild_info:
        return "invalid"
    
    member_list = guild_info['management_roles_id']
    
    if isinstance(member_list, list):
        pass
    else:
        member_list = member_list.strip('[]').split(', ')
    
    if ctx.guild.owner.id == ctx.author.id or ctx.author.guild_permissions.administrator:
        return True
    
    for member in member_list:
        try:
            staff = discord.utils.get(ctx.guild.roles, id=int(member))
        except ValueError as e:
            raise commands.CommandInvokeError(e)

        if staff in ctx.author.roles:
            return True

    return False

async def checkSetUp(ctx: commands.Context):
    if not ctx.guild or ctx.guild == None:
      return False
    elif ctx.guild.chunked:
      pass
    else:
      await ctx.guild.chunk()
    guild_info = await get_info(ctx)
    
    if not guild_info:
        em = discord.Embed(title="Setup", description="Please set up the bot using `-setup`!", color=discord.Color.blue())
        await ctx.send(embed=em)
        return False
    else:
        return True
    
class change_buttons(discord.ui.View):
    def __init__(self, ctx, guild_info, embed, type):
        super().__init__()
        self.message = None
        self.isCanceled = False
        self.guild_info = guild_info
        self.embed = embed
        self.ctx = ctx
        self.title = None
        self.description = None
        self.footer = None
        self.author_link = None
        self.author_name = None
        self.type = type

    @discord.ui.button(label='Close', style=discord.ButtonStyle.red)
    async def close_button(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.message.delete()
        self.isCanceled = True
        self.stop()
    
    @discord.ui.button(label='Submit', style=discord.ButtonStyle.green)
    async def submit(self, ctx: discord.Interaction, button: discord.ui.Button):

        if self.title is not None:
          new_title = str(self.title).replace("{emoji}", f"{self.guild_info['emoji_id']}")
          await db.embeds.update_one({"guild_id": ctx.guild.id}, {'$set': {f"{self.type}_title": str(new_title)}})
        if self.description is not None:
          await db.embeds.update_one({"guild_id": ctx.guild.id}, {'$set': {f"{self.type}_description": str(self.description)}})
        if self.footer is not None:
          await db.embeds.update_one({"guild_id": ctx.guild.id}, {'$set': {f"{self.type}_footer": str(self.footer)}})
        if self.author_link is not None and self.author_name is not None:
          await db.embeds.update_one({"guild_id": ctx.guild.id}, {'$set': {f"{self.type}_author_name": str(self.author_name)}})
          await db.embeds.update_one({"guild_id": ctx.guild.id}, {'$set': {f"{self.type}_author_link": str(self.author_link)}})

        await ctx.response.send_message(f"Modifed.", ephemeral=True)
        return

    @discord.ui.button(label='Set Title', style=discord.ButtonStyle.gray)
    async def set_title(self, ctx: discord.Interaction, button: discord.ui.Button):
        modal = MTitle()
        await ctx.response.send_modal(modal)
        em = discord.Embed(title="Here are the placeholders you can use for titles.", description="**{emoji}** is a placeholder for your server emoji. \n **{server_name}** is a placeholder for your server name. \n\n **Example:** \n\n **{emoji}** **{server_name}** Session Startup")
        await ctx.followup.send(embed=em, ephemeral=True)
        await modal.wait()
        new_title = str(modal.answer).replace("{emoji}", f"{self.guild_info['emoji_id']}")

        self.title = str(new_title)
        embed = ctx.message.embeds[0]
        embed.title = str(new_title)
        await ctx.message.edit(embed=embed)
    
    @discord.ui.button(label='Set Description', style=discord.ButtonStyle.gray)
    async def set_description(self, ctx: discord.Interaction, button: discord.ui.Button):
        timestamp = int(time.time())
        modal = MDescription()
        await ctx.response.send_modal(modal)
        em = discord.Embed(title="Here are the placeholders you can use for descriptions.", description="**{author_name}**: This placeholder is the person who used the command. \n**{ro_name}**: This placeholder is your ROBLOX server name. \n **{ro_owner}**: This placeholder is your ROBLOX server owner. \n **{ro_code}**: This placeholder is your ROBLOX server code. \n **{emoji}**: This placeholder is your server emoji. \n **{timestamp}**: This placeholder is the time the embed was sent. \n\n **Example:** \n\n **{emoji}** *Our ingame server has been shutdown. Do not join our server until we start up the server again.*\n\n**Issued on:** **{timestamp}**")
        await ctx.followup.send(embed=em, ephemeral=True)
        await modal.wait()
        new_des = str(modal.answer).replace("{timestamp}", f"<t:{timestamp}:F>")
        new_string1 = new_des.replace("{ro_name}", self.guild_info['server_name'])
        new_string2 = new_string1.replace("{ro_owner}", self.guild_info['server_owner'])
        new_string3 = new_string2.replace("{ro_code}", self.guild_info['server_code'])
        new_string4 = new_string3.replace("{server_name}", f"{self.guild_info['server_name']}")
        try:
          new_string5 = new_string4.replace("{author_name}", f"{ctx.author.name}")
        except:
          new_string5 = new_string4.replace("{author_name}", f"{ctx.user.name}")
        emoji_id = self.guild_info['emoji_id']


        if emoji_id == None:
          emoji_id = ""
          new_string6 = new_string5.replace("{emoji}", emoji_id)
        else:
          new_string6 = new_string5.replace("{emoji}", emoji_id)

        description = str(new_string6)
        self.description = str(description)
        embed = ctx.message.embeds[0]
        embed.description = str(description)
        await ctx.message.edit(embed=embed) 

    
    @discord.ui.button(label='Set Footer', style=discord.ButtonStyle.gray)
    async def set_footer(self, ctx: discord.Interaction, button: discord.ui.Button):
        modal = MFooter()
        await ctx.response.send_modal(modal)
        em = discord.Embed(title="Here are the placeholders you can use for footers.", description="**{author_name}**: This placeholder is the person who used the command. \n **{ro_name}**: This placeholder is your ROBLOX server name. \n **{ro_owner}**: This placeholder is your ROBLOX server owner. \n **{ro_code}**: This placeholder is your ROBLOX server code. \n\n **Example:** \n\n **{user}** has started a session for **{ro_name}** with the code **{ro_code}**.")
        await ctx.followup.send(embed=em, ephemeral=True)
        await modal.wait()
        footer = str(modal.answer)
        try:
          try:
            new_des = footer.replace("{author_name}", f"{ctx.author.name}")
          except:
            new_des = footer.replace("{author_name}", f"{ctx.user.name}")
          new_string1 = new_des.replace("{ro_name}", self.guild_info['server_name'])
          new_string2 = new_string1.replace("{ro_owner}", self.guild_info['server_owner'])
          new_string3 = new_string2.replace("{ro_code}", self.guild_info['server_code'])
          footer = new_string3
        except Exception as e:
          raise commands.CommandInvokeError(e)
        self.footer = str(footer)
        embed = ctx.message.embeds[0]
        embed = embed.set_footer(text=str(footer))
        await ctx.message.edit(embed=embed)
    
    @discord.ui.button(label='Set Author', style=discord.ButtonStyle.gray)
    async def set_author(self, ctx: discord.Interaction, button: discord.ui.Button):
        modal = MAuthor()
        await ctx.response.send_modal(modal)
        em = discord.Embed(title="Here are the placeholders you can use for authors.", description="**{author_name}**: This placeholder is the person who used the command.")
        await ctx.followup.send(embed=em, ephemeral=True)
        await modal.wait()
        self.author_link = str(modal.answer1)
        self.author_name = str(modal.answer)
        try:
          try:
            new_des = str(modal.answer).replace("{author_name}", f"{ctx.author.name}")
          except:
            new_des = str(modal.answer).replace("{author_name}", f"{ctx.user.name}")
        except Exception as e:
          raise commands.CommandInvokeError(e)
        
        author_name = new_des
        embed = ctx.message.embeds[0]
        embed = embed.set_author(name=author_name, icon_url=str(modal.answer1))
        try:
          await ctx.message.edit(embed=embed)
        except:
          await ctx.followup.send("Please make sure you are inputting a valid image link.", ephemeral=True)

async def createUrlButton(urls, labels):
    buttons = [
        discord.ui.Button(style=discord.ButtonStyle.url, label=label, url=url)
        for label, url in zip(labels, urls)
    ]

    view = discord.ui.View()
    view.add_item(*buttons)
    
    return view

class load_env():
    load_dotenv()
    def token():
      TOKEN = os.getenv('TOKEN')
      token = str(TOKEN)
      return token
    def prefix():
      PREFIX = os.getenv('PREFIX')
      prefix = str(PREFIX)
      return prefix
    def SENTRY_ORGANIZATION_SLUG():
       SENTRY_ORGANIZATION_SLUG = os.getenv('SENTRY_ORGANIZATION_SLUG')
       SENTRY_ORGANIZATION_SLUG = str(SENTRY_ORGANIZATION_SLUG)
       return SENTRY_ORGANIZATION_SLUG
    def SENTRY_API_KEY():
       SENTRY_API_KEY = os.getenv('SENTRY_API_KEY')
       SENTRY_API_KEY = str(SENTRY_API_KEY)
       return SENTRY_API_KEY
    def PROJECT_SLUG():
       PROJECT_SLUG = os.getenv('PROJECT_SLUG')
       PROJECT_SLUG = str(PROJECT_SLUG)
       return PROJECT_SLUG
    def SENTRY_API_URL():
       SENTRY_API_URL = os.getenv('SENTRY_API_URL')
       SENTRY_API_URL = str(SENTRY_API_URL)
       return SENTRY_API_URL

async def handleEmbedChange(ctx: Interaction, bot, guild_info, embed_type):
    timestamp = int(time.time())
    await ctx.response.defer(ephemeral=False)
    embed_info = await get_embed_info(ctx, embed_type)

    newDescription = await convertEmbed(ctx, embed_info[0], embed_info[2], embed_info[3], embed_info[5], guild_info, timestamp, embed_type)
    em = discord.Embed(title=f"{newDescription[1]}", description=newDescription[0], color=discord.Color.red())
    if newDescription[2]:
        em.set_footer(text=newDescription[2])

    if newDescription[3]:
        em.set_author(name=newDescription[3], icon_url=embed_info[4])

    view = change_buttons(ctx, guild_info, em, embed_type)
    msg = await ctx.channel.send(embed=em, view=view)
        
def is_management():
    async def predicate(ctx: commands.Context):
        if ctx.channel.type == discord.ChannelType.private:
          raise commands.NoPrivateMessage(
              "This command cannot be used in private messages."
          )
        if await checkManage(ctx) == "invalid":
            if await checkSetUp(ctx):
                return True
            else:
                return False
        elif await checkManage(ctx) == True:
            if await checkSetUp(ctx):
                return True
            else:
                return False
        else:
            em = discord.Embed(title="Missing Permissions.", description="You don't have the correct roles to run this command.", color=discord.Color.red())
            await ctx.channel.send(embed=em)
            return False
    return commands.check(predicate)



def is_staff():
    async def predicate(ctx: commands.Context):
        if ctx.channel.type == discord.ChannelType.private:
          raise commands.NoPrivateMessage(
              "This command cannot be used in private messages."
          )
        if await checkStaff(ctx) == "invalid":
            if await checkSetUp(ctx):
                return True
            else:
                return False
        elif await checkStaff(ctx) == True or await checkManage(ctx) == True:
            if await checkSetUp(ctx):
                return True
            else:
                return False
        else:
            em = discord.Embed(title="Missing Permissions.", description="You don't have the correct roles to run this command.", color=discord.Color.red())
            await ctx.channel.send(embed=em)
            return False
    return commands.check(predicate)

def setup_command_check():
    async def predicate(ctx: commands.Context):
      if ctx.author.guild_permissions.administrator:
        return True
      else:
        em = discord.Embed(title="Incorrect Permissions", description="You need administrative permissions to run this command!", color=discord.Color.red())
        await ctx.channel.send(embed=em)
        return False
    return commands.check(predicate)
    
async def checkLOASetup(ctx):
    record = await db.settings.find_one({"guild_id": ctx.guild.id}, {"loa_toggle": 1})
    return record.get('loa_toggle', 0)



async def convertInto(ctx: Interaction, member_list):
    members = member_list.strip('[]').split(', ')
    mentions = [f"<@&{member}>" for member in members if member.isdigit()]

    return ' '.join(mentions)

class role_select(discord.ui.RoleSelect):
    def __init__(self, min_values, max_values, author):
        super().__init__(placeholder="Select A Role",max_values=min_values,min_values=max_values)
        view=View()
        view.add_item(self)
        self.roles = list()
        self.min_values = min_values
        self.max_values = max_values
        self.author = author
        self.view_obj = view
        self.interaction = None

    async def callback(self, interaction: Interaction):
      self.interaction = interaction
      if self.author != interaction.user.id:
        try:
          return await interaction.response.send_message("You aren't the user who initiated the command!", ephemeral=True)
        except:
          return await interaction.followup.send("You aren't the user who initiated the command!", ephemeral=True)
      for role in self.values:
        role = role.id
        self.roles.append(role)
      
      if self.max_values == 1:
        self.roles = int(self.roles[0])
      else:
        self.roles = str(self.roles)
      
      self.view_obj.stop()


class channel_select(discord.ui.ChannelSelect):
    def __init__(self, min_values, max_values, author):
        super().__init__(placeholder="Select A Channel",max_values=min_values,min_values=max_values)
        view = View()
        view.add_item(self)
        self.channels = []
        self.min_values = min_values
        self.max_values = max_values
        self.author = author
        self.view_obj = view
        self.interaction = None

    async def callback(self, interaction: Interaction):
      self.interaction = interaction
      if self.author != interaction.user.id:
        try:
          return await interaction.response.send_message("You aren't the user who initiated the command!", ephemeral=True)
        except:
          return await interaction.followup.send("You aren't the user who initiated the command!", ephemeral=True)
      for channel in self.values:
        channel = channel.id
        self.channels.append(channel)
      
      if self.max_values == 1:
        self.channels = int(self.channels[0])
      else:
        self.channels = str(self.channels)
      self.view_obj.stop()
    
async def get_discord_color(rgb):
    rgb_values = list(map(int, rgb[1:-1].split(', ')))
    return discord.Color.from_rgb(*rgb_values)
    
async def sessionChange(ctx: Interaction, bot, guild_info):
    timestamp = int(time.time())
    await ctx.response.defer(ephemeral=False)
    embed_info = await get_embed_info(ctx, 'session')

    newDescription = await convertEmbed(ctx, embed_info[0], embed_info[2], embed_info[3], embed_info[5], guild_info, timestamp, "session")
    em = discord.Embed(title=f"{newDescription[1]}", description=newDescription[0], color=discord.Color.red())
    if newDescription[2]:
      em.set_footer(text=newDescription[2])

    if newDescription[3]:
      em.set_author(name=newDescription[3], icon_url=embed_info[4])

    view = change_buttons(ctx, guild_info, em, "session")
    msg = await ctx.channel.send(embed=em, view=view)

async def shutdownChange(ctx: Interaction, bot, guild_info):
    timestamp = int(time.time())
    await ctx.response.defer(ephemeral=False)
    embed_info = await get_embed_info(ctx, 'shutdown')

    newDescription = await convertEmbed(ctx, embed_info[0], embed_info[2], embed_info[3], embed_info[5], guild_info, timestamp, "shutdown")
    em = discord.Embed(title=f"{newDescription[1]}", description=newDescription[0], color=discord.Color.red())
    if newDescription[2]:
      em.set_footer(text=newDescription[2])

    if newDescription[3]:
      em.set_author(name=newDescription[3], icon_url=embed_info[4])

    view = change_buttons(ctx, guild_info, em, "shutdown")
    msg = await ctx.channel.send(embed=em, view=view)

async def svoteChange(ctx: Interaction, bot, guild_info):
    timestamp = int(time.time())
    await ctx.response.defer(ephemeral=False)
    embed_info = await get_embed_info(ctx, 'svote')

    newDescription = await convertEmbed(ctx, embed_info[0], embed_info[2], embed_info[3], embed_info[5], guild_info, timestamp, "svote")
    em = discord.Embed(title=f"{newDescription[1]}", description=newDescription[0], color=discord.Color.red())
    if newDescription[2]:
      em.set_footer(text=newDescription[2])

    if newDescription[3]:
      em.set_author(name=newDescription[3], icon_url=embed_info[4])

    view = change_buttons(ctx, guild_info, em, "svote")
    msg = await ctx.channel.send(embed=em, view=view)




async def demoteChange(ctx: Interaction, bot, guild_info):
    timestamp = int(time.time())
    await ctx.response.defer(ephemeral=False)
    embed_info = await get_embed_info(ctx, 'demote')

    newDescription = await convertEmbed(ctx, embed_info[0], embed_info[2], embed_info[3], embed_info[5], guild_info, timestamp, "demote")
    em = discord.Embed(title=f"{newDescription[1]}", description=newDescription[0], color=discord.Color.red())
    if newDescription[2]:
      em.set_footer(text=newDescription[2])

    if newDescription[3]:
      em.set_author(name=newDescription[3], icon_url=embed_info[4])

    view = change_buttons(ctx, guild_info, em, "demote")
    msg = await ctx.channel.send(embed=em, view=view)


async def promoteChange(ctx: Interaction, bot, guild_info):
    timestamp = int(time.time())
    await ctx.response.defer(ephemeral=False)
    embed_info = await get_embed_info(ctx, 'promote')

    newDescription = await convertEmbed(ctx, embed_info[0], embed_info[2], embed_info[3], embed_info[5], guild_info, timestamp, "promote")
    em = discord.Embed(title=f"{newDescription[1]}", description=newDescription[0], color=discord.Color.red())
    if newDescription[2]:
      em.set_footer(text=newDescription[2])

    if newDescription[3]:
      em.set_author(name=newDescription[3], icon_url=embed_info[4])

    view = change_buttons(ctx, guild_info, em, "promote")
    msg = await ctx.channel.send(embed=em, view=view)


async def warnChange(ctx: Interaction, bot, guild_info):
    timestamp = int(time.time())
    await ctx.response.defer(ephemeral=False)
    embed_info = await get_embed_info(ctx, 'warn')

    newDescription = await convertEmbed(ctx, embed_info[0], embed_info[2], embed_info[3], embed_info[5], guild_info, timestamp, "warn")
    em = discord.Embed(title=f"{newDescription[1]}", description=newDescription[0], color=discord.Color.red())
    if newDescription[2]:
      em.set_footer(text=newDescription[2])

    if newDescription[3]:
      em.set_author(name=newDescription[3], icon_url=embed_info[4])

    view = change_buttons(ctx, guild_info, em, "warn")
    msg = await ctx.channel.send(embed=em, view=view)


async def strikeChange(ctx: Interaction, bot, guild_info):
    timestamp = int(time.time())
    await ctx.response.defer(ephemeral=False)
    embed_info = await get_embed_info(ctx, 'strike')

    newDescription = await convertEmbed(ctx, embed_info[0], embed_info[2], embed_info[3], embed_info[5], guild_info, timestamp, "strike")
    em = discord.Embed(title=f"{newDescription[1]}", description=newDescription[0], color=discord.Color.red())
    if newDescription[2]:
      em.set_footer(text=newDescription[2])

    if newDescription[3]:
      em.set_author(name=newDescription[3], icon_url=embed_info[4])

    view = change_buttons(ctx, guild_info, em, "strike")
    msg = await ctx.channel.send(embed=em, view=view)

async def make_custom_embed(ctx: commands.Context, type, timestamp, guild_info):
  embed_info = await get_embed_info(ctx, type)

  color = await get_discord_color(str(embed_info[1]))
  newDescription = await convertEmbed(ctx, embed_info[0], embed_info[2], embed_info[3], embed_info[5], guild_info, timestamp, type)

  embed = discord.Embed(title=f"{newDescription[1]}", description=newDescription[0], color=color)
  if type == "svote":
    banner = guild_info['svote_banner_link']
  elif type == "session":
    banner = guild_info['session_banner_link']
  elif type == "shutdown":
    banner = guild_info['shutdown_banner_link']

  if banner == "skipped":
    pass
  else:
    try:
      embed.set_image(url=f"{banner}")
    except discord.HTTPException:
      await ctx.channel.send(f"It looks like your banner link is invalid. Please change it in `-config` so I can display it!.")
  
  if embed_info[4]:
    embed.set_author(name=newDescription[3], icon_url=embed_info[4])

  if embed_info[3]:
    embed.set_footer(text=newDescription[2])
  
  return embed