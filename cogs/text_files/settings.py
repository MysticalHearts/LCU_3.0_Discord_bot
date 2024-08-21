import discord
from discord.ext import commands
from discord.ui import View, Button, Select
from discord import Interaction
from cogs.utils.checks import sessionChange, shutdownChange, svoteChange, demoteChange, promoteChange, warnChange, strikeChange, getColor, get_info, is_staff, is_management
from cogs.utils.modals import MSessionLink, MLOALength
import re
from PIL import ImageColor
from cogs.events import db

        
class welcomeModal(discord.ui.Modal, title='Welcome Text'):

    answer = discord.ui.TextInput(label="Welcome Text", placeholder="Say 'reset' to reset to none.", style=discord.TextStyle.paragraph)

    async def on_submit(self, ctx: Interaction):
       
      answer = str(self.answer)
      
      if answer == "reset":
        await db.setup.update_one(
            {'guild_id': int(ctx.guild.id)},
            {'$set': {'welcome_text': "Welcome {member.mention} to {guild.name}!"}}
        )
        await ctx.response.send_message(f"It has now been configured!", ephemeral=True)
      else:
        
        await ctx.response.send_message(f"Saved!", ephemeral=True)

class otherSettings(discord.ui.View):
  def __init__(self, ctx, bot):
    super().__init__(timeout=None)
    self.ctx = ctx
    self.bot = bot

class SettingsPanel(discord.ui.View):
  def __init__(self, ctx, bot):
    super().__init__(timeout=None)
    self.ctx = ctx
    self.bot = bot
    self.mainMessage = None
    
    
  
  #---------------------Embeds Button
  @discord.ui.button(label="Embeds", style=discord.ButtonStyle.grey)
  async def embed_changer(self, ctx: Interaction, button: discord.ui.Button):
    guild_info = await get_info(ctx)
    try:
      if not ctx.user.id == self.ctx.author.id and ctx.channel.id == self.ctx.channel.id:
        return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
    except:
      if not ctx.user.id == self.ctx.user.id and ctx.channel.id == self.ctx.channel.id:
        return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
     
    em = discord.Embed(title=f"Embed Changer", description=f"Here you will be able to change the embeds descriptions and or reset the embed descriptions.", color=await getColor(ctx, "commands_color"))
    select_menu = Select(placeholder="Select An Embed to Change", options=[
    discord.SelectOption(label="Session", value="1", description="Edit the session emebed"),
    discord.SelectOption(label="Shutdown", value="2", description="Edit the shutdown embed"),
    discord.SelectOption(label="SVote", value="3", description="Edit the svote embed"),
    discord.SelectOption(label="Demote", value="4", description="Edit the demote embed"),
    discord.SelectOption(label="Promote", value="5", description="Edit the promote embed"),
    discord.SelectOption(label="Warn", value="6", description="Edit the warn embed"),
    discord.SelectOption(label="Strike", value="7", description="Edit the strike embed"),
    ])

    select_menu2 = Select(placeholder="Select An Embed to Reset", options=[
    discord.SelectOption(label="Session", value="1", description="Reset the session embed"),
    discord.SelectOption(label="Shutdown", value="2", description="Reset the shutdown embed"),
    discord.SelectOption(label="SVote", value="3", description="Reset the SVote embed"),
    discord.SelectOption(label="Demote", value="4", description="Reset the demote embed"),
    discord.SelectOption(label="Promote", value="5", description="Reset the promote embed"),
    discord.SelectOption(label="Warn", value="6", description="Reset the warn embed"),
    discord.SelectOption(label="Strike", value="7", description="Reset the strike embed"),
    ])

    button = Button(style=discord.ButtonStyle.red, label="Back")
    usr = ctx.user.id
    chn = ctx.channel.id

    async def callback(ctx: Interaction):
      if not ctx.user.id == usr and ctx.channel.id == chn:
        return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
      try:
        if select_menu.values[0] == "1":
          
          await sessionChange(ctx, self.bot, guild_info)
        elif select_menu.values[0] == "2":
          
          await shutdownChange(ctx, self.bot, guild_info)
        elif select_menu.values[0] == "3":
          
          await svoteChange(ctx, self.bot, guild_info)
        elif select_menu.values[0] == "4":
          
          await demoteChange(ctx, self.bot, guild_info)
        elif select_menu.values[0] == "5":
          
          await promoteChange(ctx, self.bot, guild_info)
        elif select_menu.values[0] == "6":
          
          await warnChange(ctx, self.bot, guild_info)
        elif select_menu.values[0] == "7":
          
          await strikeChange(ctx, self.bot, guild_info)
        else:
          print("Something Went Wrong")
      except Exception as e:
        raise e

    async def callback2(ctx: Interaction):
      if not ctx.user.id == usr and ctx.channel.id == chn:
        return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
       
      try:
        
        if select_menu2.values[0] == "1":

          var = "Our ingame server has been started up! If you voted, you must join the server, failure to do so will result in a infraction.\n\nServer Name: **{ro_name}**\nServer Owner: **{ro_owner}**\nServer Code: **{ro_code}** (Case Sensitive)\n\n**Issued on:** {timestamp}"
          await db.embeds.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'session_description': str(var), 'session_title': f'{ctx.guild.name} Session Startup', 'session_footer': '', 'session_author_link': '', 'session_author_name': ''}}
          )

          await ctx.response.send_message("Your embed is now reset", ephemeral=True)
        elif select_menu2.values[0] == "2":
          #await ctx.message.delete()
          var = "{emoji} *Our ingame server has been shutdown. Do not join our server until we start up the server again.*\n\n**Issued on:** {timestamp}"
          
          await db.embeds.update_one(
            {'guild_id': ctx.guild.id},
            {'$set': {'shutdown_description': var, 'shutdown_title': f'{ctx.guild.name} Session Shutdown', 'shutdown_footer': '', 'shutdown_author_link': '', 'shutdown_author_name': ''}}
          )
          await ctx.response.send_message("Your embed is now reset", ephemeral=True)
        elif select_menu2.values[0] == "3":
          #await ctx.message.delete()
          var = "{emoji} **Management Team** *have decided to start a session poll, vote below if you are willing to attend this session!*\n\n**Issued on:** {timestamp}"
          await db.embeds.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'svote_description': str(var), 'svote_title': f'{ctx.guild.name} Session Vote', 'svote_footer': '', 'svote_author_link': '', 'svote_author_name': ''}}
          )

          await ctx.response.send_message("Your embed is now reset", ephemeral=True)
        elif select_menu2.values[0] == "4":
          #await ctx.message.delete()
          var = "The HR Team has decided to take the following actions upon you. Please do not start any drama about this."
          await db.embeds.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'demote_description': str(var), 'demote_title': f'{ctx.guild.name} Demotion', 'demote_footer': '', 'demote_author_link': '', 'demote_author_name': ''}}
          )

          await ctx.response.send_message("Your embed is now reset", ephemeral=True)
        elif select_menu2.values[0] == "5":
          #await ctx.message.delete()
          var = "Congratulations on getting promoted!"
          
          await db.embeds.update_one(
            {'guild_id': ctx.guild.id},
            {'$set': {'promote_description': var, 'promote_title': f'{ctx.guild.name} Promotion', 'promote_footer': '', 'promote_author_link': '', 'promote_author_name': ''}}
          )
          await ctx.response.send_message("Your embed is now reset", ephemeral=True)
        elif select_menu2.values[0] == "6":
          #await ctx.message.delete()
          var = "The HR Team has decided to take the following actions upon you. Please do not start any drama about this."
          await db.embeds.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'warn_description': str(var), 'warn_title': f'Staff Warning', 'warn_footer': '', 'warn_author_link': '', 'warn_author_name': ''}}
          )
          await ctx.response.send_message("Your embed is now reset", ephemeral=True)
        elif select_menu2.values[0] == "7":
          #await ctx.message.delete()
          var = "The HR Team has decided to take the following actions upon you. Please do not start any drama about this."
          
          await db.embeds.update_one(
            {'guild_id': ctx.guild.id},
            {'$set': {'strike_description': var, 'strike_title': f'Staff Strike', 'strike_footer': '', 'strike_author_link': '', 'strike_author_name': ''}}
          )
          await ctx.response.send_message("Your embed is now reset", ephemeral=True)
        else:
          print("Something Went Wrong")
      except Exception as e:
        raise e
      
    async def callback3(ctx: Interaction):
        if not ctx.user.id == usr and ctx.channel.id == chn:
          return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
        em = discord.Embed(title=f"Settings Page", description=f"In this command you can edit any embed descriptions, colors, or toggles for LCU\n\n**Embeds** - Change any descriptions or reset any embeds\n**Colors** - Change any colors of the embeds\n**Other** - Toggle different features of LCU", color=await getColor(ctx, "commands_color"))
        view = SettingsPanel(ctx, self.bot)
        msg2 = await ctx.response.edit_message(embed=em, view=view)
        await self.bot.wait_for('interaction', timeout=None, check=lambda message: message.user == ctx.user and message.channel == ctx.channel)
    
    select_menu.callback = callback
    select_menu2.callback = callback2
    button.callback = callback3
    view = View()
    view.add_item(select_menu)
    view.add_item(select_menu2)
    view.add_item(button)
    msg = await ctx.response.edit_message(embed=em, view=view)

  #-------------------------Colors Button
  @discord.ui.button(label="Colors", style=discord.ButtonStyle.grey)
  async def color_changer(self, ctx: Interaction, button: discord.ui.Button):
    try:
      if not ctx.user.id == self.ctx.author.id and ctx.channel.id == self.ctx.channel.id:
        return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
    except:
      if not ctx.user.id == self.ctx.user.id and ctx.channel.id == self.ctx.channel.id:
        return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
     
    em = discord.Embed(title=f"Color Changer", description=f"In this section you will be able to change the colors for certain commands.", color=await getColor(ctx, "commands_color"))
    select_menu = Select(placeholder="Select An Embed to Change", options=[
    discord.SelectOption(label="Session", value="1", description="Change the session command color"),
    discord.SelectOption(label="Shutdown", value="2", description="Change the shutdown command color"),
    discord.SelectOption(label="SVote", value="3", description="Change the svote command color"),
    discord.SelectOption(label="Warn", value="4", description="Change the warn command color"),
    discord.SelectOption(label="Strike", value="5", description="Change the strike command color"),
    discord.SelectOption(label="Promote", value="6", description="Change the promote command color"),
    discord.SelectOption(label="Demote", value="7", description="Change the demote command color"),
    discord.SelectOption(label="Bot Color", value="8", description="Change the overall embed color"),
    ])

    button = Button(style=discord.ButtonStyle.red, label="Back")
    usr = ctx.user.id
    chn = ctx.channel.id

    async def callback(ctx: Interaction):
      if not ctx.user.id == usr and ctx.channel.id == chn:
        return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
       
      await ctx.message.delete()
      em = discord.Embed(title=f"Please provide a color in hex format(ex: `#54FF00`)", color=await getColor(ctx, "commands_color"))
      
      if select_menu.values[0] == "1":
        embed = await ctx.response.send_message(embed=em)
        msg2 = await self.bot.wait_for('message', timeout=None, check=lambda message: message.author == ctx.user and message.channel == ctx.channel)
        match = re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$', msg2.content)
        if not match:
          em2 = discord.Embed(title=f"That is not a hex value, please rerun the settings command!", color=await getColor(ctx, "commands_color"))
          return await ctx.followup.send(embed=em2)
        else:
          pass
        rgb = ImageColor.getrgb(msg2.content)
        await db.embeds.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'session_color': str(rgb)}}
        )
        await ctx.followup.send("Your embed color is now changed", ephemeral=True)
        await msg2.delete()
      elif select_menu.values[0] == "2":
        embedm = await ctx.response.send_message(embed=em)
        msg2 = await self.bot.wait_for('message', timeout=None, check=lambda message: message.author == ctx.user and message.channel == ctx.channel)
        match = re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$', msg2.content)
        if not match:
          em2 = discord.Embed(title=f"That is not a hex value, please rerun the settings command!", color=await getColor(ctx, "commands_color"))
          return await ctx.followup.send(embed=em2)
        else:
          pass
        rgb = ImageColor.getrgb(msg2.content)
        await db.embeds.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'shutdown_color': str(rgb)}}
        )
        await ctx.followup.send("Your embed color is now changed", ephemeral=True)
        
      elif select_menu.values[0] == "3":
        embedm = await ctx.response.send_message(embed=em)
        msg2 = await self.bot.wait_for('message', timeout=None, check=lambda message: message.author == ctx.user and message.channel == ctx.channel)
        match = re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$', msg2.content)
        if not match:
          em2 = discord.Embed(title=f"That is not a hex value, please rerun the settings command!", color=await getColor(ctx, "commands_color"))
          return await ctx.followup.send(embed=em2)
        else:
          pass
        rgb = ImageColor.getrgb(msg2.content)
        await db.embeds.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'svote_color': str(rgb)}}
        )
        await ctx.followup.send("Your embed color is now changed", ephemeral=True)
      
      elif select_menu.values[0] == "4":
        embedm = await ctx.response.send_message(embed=em)
        msg2 = await self.bot.wait_for('message', timeout=None, check=lambda message: message.author == ctx.user and message.channel == ctx.channel)
        match = re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$', msg2.content)
        if not match:
          em2 = discord.Embed(title=f"That is not a hex value, please rerun the settings command!", color=await getColor(ctx, "commands_color"))
          return await ctx.followup.send(embed=em2)
        else:
          pass
        rgb = ImageColor.getrgb(msg2.content)
        
        await db.embeds.update_one(
            {'guild_id': ctx.guild.id},
            {'$set': {'warn_color': str(rgb)}}
        )
        await ctx.followup.send("Your embed color is now changed", ephemeral=True)

      elif select_menu.values[0] == "5":
        embedm = await ctx.response.send_message(embed=em)
        msg2 = await self.bot.wait_for('message', timeout=None, check=lambda message: message.author == ctx.user and message.channel == ctx.channel)
        match = re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$', msg2.content)
        if not match:
          em2 = discord.Embed(title=f"That is not a hex value, please rerun the settings command!", color=await getColor(ctx, "commands_color"))
          return await ctx.followup.send(embed=em2)
        else:
          pass
        rgb = ImageColor.getrgb(msg2.content)
        await db.embeds.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'strike_color': str(rgb)}}
        )
        await ctx.followup.send("Your embed color is now changed", ephemeral=True)

      elif select_menu.values[0] == "6":
        embedm = await ctx.response.send_message(embed=em)
        msg2 = await self.bot.wait_for('message', timeout=None, check=lambda message: message.author == ctx.user and message.channel == ctx.channel)
        match = re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$', msg2.content)
        if not match:
          em2 = discord.Embed(title=f"That is not a hex value, please rerun the settings command!", color=await getColor(ctx, "commands_color"))
          return await ctx.followup.send(embed=em2)
        else:
          pass
        rgb = ImageColor.getrgb(msg2.content)
        
        await db.embeds.update_one(
            {'guild_id': ctx.guild.id},
            {'$set': {'promote_color': str(rgb)}}
        )
        await ctx.followup.send("Your embed color is now changed", ephemeral=True)

      elif select_menu.values[0] == "7":
        embedm = await ctx.response.send_message(embed=em)
        msg2 = await self.bot.wait_for('message', timeout=None, check=lambda message: message.author == ctx.user and message.channel == ctx.channel)
        match = re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$', msg2.content)
        if not match:
          em2 = discord.Embed(title=f"That is not a hex value, please rerun the settings command!", color=await getColor(ctx, "commands_color"))
          return await ctx.followup.send(embed=em2)
        else:
          pass
        rgb = ImageColor.getrgb(msg2.content)
        await db.embeds.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'demote_color': str(rgb)}}
        )
        await ctx.followup.send("Your embed color is now changed", ephemeral=True)

      elif select_menu.values[0] == "8":
        embedm = await ctx.response.send_message(embed=em)
        msg2 = await self.bot.wait_for('message', timeout=None, check=lambda message: message.author == ctx.user and message.channel == ctx.channel)
        match = re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$', msg2.content)
        if not match:
          em2 = discord.Embed(title=f"That is not a hex value, please rerun the settings command!", color=await getColor(ctx, "commands_color"))
          return await ctx.followup.send(embed=em2)
        else:
          pass
        rgb = ImageColor.getrgb(msg2.content)
        await db.embeds.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'commands_color': str(rgb)}}
        )
        await ctx.followup.send("Your embed color is now changed", ephemeral=True)
    
    async def callback2(ctx: Interaction):
        if not ctx.user.id == usr and ctx.channel.id == chn:
          return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
        em = discord.Embed(title=f"Settings Page", description=f"In this command you can edit any embed descriptions, colors, or toggles for LCU\n\n**Embeds** - Change any descriptions or reset any embeds\n**Colors** - Change any colors of the embeds\n**Other** - Toggle different features of LCU", color=await getColor(ctx, "commands_color"))
        view = SettingsPanel(ctx, self.bot)
        msg2 = await ctx.response.edit_message(embed=em, view=view)
        await self.bot.wait_for('interaction', timeout=None, check=lambda message: message.user == ctx.user and message.channel == ctx.channel)
      
    select_menu.callback = callback
    button.callback = callback2
    view = View()
    view.add_item(select_menu)
    view.add_item(button)
    msg = await ctx.response.edit_message(embed=em, view=view)

  #--------------------------Other Button
  @discord.ui.button(label="Other", style=discord.ButtonStyle.grey)
  async def other(self, ctx: Interaction, button: discord.ui.Button):
    try:
      if not ctx.user.id == self.ctx.author.id and ctx.channel.id == self.ctx.channel.id:
        return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
    except:
      if not ctx.user.id == self.ctx.user.id and ctx.channel.id == self.ctx.channel.id:
        return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)

    buttons = [
    discord.ui.button(label="Toggle: Reminders Command Ping", custom_id="1"),
    discord.ui.button(label="Session Link", custom_id="2"),
    discord.ui.button(label="Toggle: Session Here Ping", custom_id="3"),
    discord.ui.button(label="Toggle: LOA Module", custom_id="4"),
    discord.ui.button(label="Toggle: Logging Module", custom_id="5"),
    discord.ui.button(label="Toggle: Welcome Module", custom_id="6"),
    discord.ui.button(label="Toggle: Reminder Module", custom_id="7")
    ]
    view = discord.ui.View()
    for i in buttons:
      view.add_item(i)
    message = await ctx.send("Select an option:", view=view)
    records = await db.settings.find_one({'guild_id': int(ctx.guild.id)}, {'m_command_toggle': 1, "svote_here_toggle": 1, "loa_toggle": 1, "logging_toggle": 1, "welcome_toggle": 1, "reminders_toggle": 1})
    try:
        interaction = await self.bot.wait_for("button_click", timeout=600.0, check=lambda i: i.component and i.message.id == message.id and i.user.id == ctx.author.id)
    except asyncio.TimeoutError:
        await message.edit(content="Menu timed out.", components=[])

    else:
        selected_value = interaction.component.value
        if selected_value == "1":
          if records['m_command_toggle'] == 0:
            await db.settings.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'m_command_toggle': 1}}
            )
            return await ctx.response.send_message("M Command Ping: **ON**", ephemeral=True)
          elif records['m_command_toggle'] == 1:
            await db.settings.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'m_command_toggle': 0}}
            )
            return await ctx.response.send_message("M Command Ping: **OFF**", ephemeral=True)
        elif selected_value == "2":
          return await ctx.response.send_modal(MSessionLink())
        elif selected_value == "3":
          if records['svote_here_toggle'] == 0:
            await db.settings.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'svote_here_toggle': 1}}
            )
            return await ctx.response.send_message("Session Here Ping: **ON**", ephemeral=True)
          elif records['svote_here_toggle'] == 1:
            await db.settings.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'svote_here_toggle': 0}}
            )
            return await ctx.response.send_message("Session Here Ping: **OFF**", ephemeral=True)
        elif selected_value == "4":
          if records['loa_toggle'] == 0 or records['loa_toggle'] == None:
            modal = MLOALength()
            await ctx.response.send_modal(modal)
            await modal.wait()
            #-------------------------------------------------------------
            #--------------------LOA callbacks-----------------------
            async def role1callback(ctx: Interaction):
              await ctx.response.defer(ephemeral=False)
              try:
                shift_role = discord.utils.get(ctx.guild.roles, name=str(select_role3.values[0]))
                await db.settings.update_one(
                    {'guild_id': int(ctx.guild.id)},
                    {'$set': {'loa_role': str(shift_role.id)}}
                )
                
              except:
                await ctx.followup.send("Something Went wrong")
                return False
            async def channel1callback(ctx: Interaction):
              
                await ctx.response.defer(ephemeral=False)
                try:
                  shift_channel = discord.utils.get(ctx.guild.channels, name=str(select_channel1.values[0]))
                  await db.settings.update_one(
                      {'guild_id': int(ctx.guild.id)},
                      {'$set': {'loa_channel': str(shift_channel.id)}}
                  )
                
                except:
                    await ctx.followup.send("Something Went wrong")
                    return False

            #--------------------LOA roles and channels-----------------------

            em = discord.Embed(title=f"LOA Role", description=f"This role is used for active LOAs.", color=await getColor(ctx, "commands_color"))
            select_role3 = discord.ui.RoleSelect(placeholder="Select A Role", min_values=1, max_values=1)
            select_role3.callback = role1callback
            if select_role3.callback == False:
              return False
            view=View()
            view.add_item(select_role3)
            em2 = await ctx.followup.send(embed = em, view=view)
            await self.bot.wait_for('interaction', timeout=600.0, check=lambda message: message.user == ctx.user and message.channel == ctx.channel)
            try:
              await em2.delete()
            except:
              pass
            

            em = discord.Embed(title=f"LOA Channel", description=f"This channel will be used to send the LOA Requests.", color=await getColor(ctx, "commands_color"))
            select_channel1 = discord.ui.ChannelSelect(placeholder="Select A Channel", min_values=1, max_values=1)
            select_channel1.callback = channel1callback
            if select_channel1.callback == False:
              return False
            view=View()
            view.add_item(select_channel1)
            em2 = await ctx.followup.send(embed = em, view=view)
            await self.bot.wait_for('interaction', timeout=600.0, check=lambda message: message.user == ctx.user and message.channel == ctx.channel)
            try:
              await em2.delete()
            except:
              pass
            

            await db.settings.update_one(
              {'guild_id': ctx.guild.id},
              {'$set': {'loa_toggle': 1}}
            )
            return await ctx.followup.send("LOA function: **ON**", ephemeral=True)
          elif records['loa_toggle'] == 1:
            await db.settings.update_one(
              {'guild_id': ctx.guild.id},
              {'$set': {'loa_toggle': 0}}
            )
            return await ctx.response.send_message("LOA function: **OFF**", ephemeral=True)
        elif selected_value == "5":
          async def loggingcallback(ctx: Interaction):
                await ctx.response.defer(ephemeral=False)
                try:
                  shift_channel = discord.utils.get(ctx.guild.channels, name=str(select_channel1.values[0]))
                  await db.settings.update_one(
                      {'guild_id': int(ctx.guild.id)},
                      {'$set': {'logging_channel': str(shift_channel.id)}}
                  )
                
                except Exception as e:
                    print(e)
                    await ctx.followup.send("Something Went wrong")
                return False
          async def joincallback(ctx: Interaction):
              
                await ctx.response.defer(ephemeral=False)
                try:
                  shift_channel = discord.utils.get(ctx.guild.channels, name=str(select_channel2.values[0]))
                  await db.settings.update_one(
                      {'guild_id': int(ctx.guild.id)},
                      {'$set': {'join_channel': str(shift_channel.id)}}
                  )
                
                except:
                    await ctx.followup.send("Something Went wrong")
                return False
          async def leavecallback(ctx: Interaction):
              
                await ctx.response.defer(ephemeral=False)
                try:
                  shift_channel = discord.utils.get(ctx.guild.channels, name=str(select_channel3.values[0]))
                  await db.settings.update_one(
                      {'guild_id': int(ctx.guild.id)},
                      {'$set': {'leave_channel': str(shift_channel.id)}}
                  )
                
                except:
                    await ctx.followup.send("Something Went wrong")
                return False
              

          try:
            if records['logging_toggle'] == 0:
              record = 0
            elif records['logging_toggle'] == 1:
              record = 1
          except:
            record = 0

          if record == 1:
            await db.settings.update_one(
                {'guild_id': ctx.guild.id},
                {'$set': {'logging_toggle': 0}}
              )
            return await ctx.response.send_message("Logging: **OFF**", ephemeral=True)
          else:
            em = discord.Embed(title=f"Logging Channel", description=f"This is your main logging channel", color=await getColor(ctx, "commands_color"))
            select_channel1 = discord.ui.ChannelSelect(placeholder="Select A Channel", min_values=1, max_values=1)
            select_channel1.callback = loggingcallback
            if select_channel1.callback == False:
              return False
            view=View()
            view.add_item(select_channel1)
            em2 = await ctx.response.send_message(embed = em, view=view)
            await self.bot.wait_for('interaction', timeout=600.0, check=lambda message: message.user == ctx.user and message.channel == ctx.channel)
            try:
              await em2.delete()
            except:
              pass
            

            em = discord.Embed(title=f"Join Channel", description=f"This is the channel where your join logs will go to.", color=await getColor(ctx, "commands_color"))
            select_channel2 = discord.ui.ChannelSelect(placeholder="Select A Channel", min_values=1, max_values=1)
            select_channel2.callback = joincallback
            if select_channel2.callback == False:
              return False
            view=View()
            view.add_item(select_channel2)
            em2 = await ctx.followup.send(embed = em, view=view)
            await self.bot.wait_for('interaction', timeout=600.0, check=lambda message: message.user == ctx.user and message.channel == ctx.channel)
            try:
              await em2.delete()
            except:
              pass

            em = discord.Embed(title=f"Leave Channel", description=f"This is the channel where your leave logs will go to.", color=await getColor(ctx, "commands_color"))
            select_channel3 = discord.ui.ChannelSelect(placeholder="Select A Channel", min_values=1, max_values=1)
            select_channel3.callback = leavecallback
            if select_channel3.callback == False:
              return False
            view=View()
            view.add_item(select_channel3)
            em2 = await ctx.followup.send(embed = em, view=view)
            await self.bot.wait_for('interaction', timeout=600.0, check=lambda message: message.user == ctx.user and message.channel == ctx.channel)
            try:
              await em2.delete()
            except:
              pass

            await db.settings.update_one(
                {'guild_id': ctx.guild.id},
                {'$set': {'logging_toggle': 1}}
              )
            return await ctx.followup.send("Logging: **ON**", ephemeral=True)

        elif selected_value == "6":
          async def welcomecallback(ctx: Interaction):
            await ctx.response.defer(ephemeral=False)
            try:
              shift_channel = discord.utils.get(ctx.guild.channels, name=str(select_channel1.values[0]))
              await db.settings.update_one(
                  {'guild_id': int(ctx.guild.id)},
                  {'$set': {'welcome_channel': str(shift_channel.id)}}
              )
            
            except:
                await ctx.followup.send("Something Went wrong")
            return False
          
          try:
            if records['welcome_toggle'] == 0:
              record = 0
            elif records['welcome_toggle'] == 1:
              record = 1
          except:
            record = 0
          if record == 1:
            await db.settings.update_one(
                {'guild_id': ctx.guild.id},
                {'$set': {'welcome_toggle': 0}}
              )
            return await ctx.response.send_message("Welcome: **OFF**", ephemeral=True)
          else:
            em = discord.Embed(title=f"Welcome Channel", description=f"This is the channel that sends the welcome message", color=await getColor(ctx, "commands_color"))
            select_channel1 = discord.ui.ChannelSelect(placeholder="Select A Channel", min_values=1, max_values=1)
            select_channel1.callback = welcomecallback
            if select_channel1.callback == False:
              return False
            view=View()
            view.add_item(select_channel1)
            em2 = await ctx.response.send_message(embed = em, view=view)
            await self.bot.wait_for('interaction', timeout=600.0, check=lambda message: message.user == ctx.user and message.channel == ctx.channel)
            try:
              await em2.delete()
            except:
              pass

            await db.settings.update_one(
                {'guild_id': ctx.guild.id},
                {'$set': {'welcome_toggle': 1, 'welcome_text': 'Welcome {member.mention} to {guild.name}!'}}
              )
            return await ctx.followup.send("Welcome: **ON**", ephemeral=True)
        elif selected_value == "7":
          if records['reminders_toggle'] == 0:
            await db.settings.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'reminders_toggle': 1}}
            )
            return await ctx.response.send_message("Reminders Module: **ON**", ephemeral=True)
          elif records['reminders_toggle'] == 1:
            await db.settings.update_one(
              {'guild_id': int(ctx.guild.id)},
              {'$set': {'reminders_toggle': 0}}
            )
            return await ctx.response.send_message("Reminders Module: **OFF**", ephemeral=True)
        else:
          return

        if interaction.component.style == discord.ButtonStyle.red:
            interaction.component.style = discord.ButtonStyle.green
        else:
            interaction.component.style = discord.ButtonStyle.red

        await message.edit(components=[action_row])

    

    async def callback2(ctx: Interaction):
        if not ctx.user.id == usr and ctx.channel.id == chn:
          return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
        em = discord.Embed(title=f"Settings Page", description=f"In this command you can edit any embed descriptions, colors, or toggles for LCU\n\n**Embeds** - Change any descriptions or reset any embeds\n**Colors** - Change any colors of the embeds\n**Other** - Toggle different features of LCU", color=await getColor(ctx, "commands_color"))
        view = SettingsPanel(ctx, self.bot)
        msg2 = await ctx.response.edit_message(embed=em, view=view)
        await self.bot.wait_for('interaction', timeout=None, check=lambda message: message.user == ctx.user and message.channel == ctx.channel)
    
    select_menu.callback = callback
    button.callback = callback2
    view = View()
    view.add_item(select_menu)
    view.add_item(button)
    msg = await ctx.response.edit_message(embed=em, view=view)
  
  @discord.ui.button(label="Welcome", style=discord.ButtonStyle.grey)
  async def welcome(self, ctx: Interaction, button: discord.ui.Button):
    try:
      if not ctx.user.id == self.ctx.author.id and ctx.channel.id == self.ctx.channel.id:
        return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
    except:
      if not ctx.user.id == self.ctx.user.id and ctx.channel.id == self.ctx.channel.id:
        return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)

    record = await db.settings.find_one({'guild_id': ctx.guild.id}, {'welcome_text': 1, 'welcome_toggle': 1})
    try:
      if record['welcome_toggle'] == 0:
        return await ctx.response.send_message("Welcome is not enabled on this server!", ephemeral=True)
    except:
      return await ctx.response.send_message("Welcome is not enabled on this server!", ephemeral=True)
    
    button = Button(style=discord.ButtonStyle.red, label="Back")
    submit = Button(style=discord.ButtonStyle.green, label="Submit")
    set_message = Button(style=discord.ButtonStyle.grey, label="Set Message")
    usr = ctx.user.id
    chn = ctx.channel.id

    async def callback1(ctx: Interaction):
        if not ctx.user.id == usr and ctx.channel.id == chn:
          return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
        em = discord.Embed(title=f"Settings Page", description=f"In this command you can edit any embed descriptions, colors, or toggles for LCU\n\n**Embeds** - Change any descriptions or reset any embeds\n**Colors** - Change any colors of the embeds\n**Other** - Toggle different features of LCU", color=await getColor(ctx, "commands_color"))
        view = SettingsPanel(ctx, self.bot)
        msg2 = await ctx.response.edit_message(embed=em, view=view, content=None)
        await self.bot.wait_for('interaction', timeout=None, check=lambda message: message.user == ctx.user and message.channel == ctx.channel)
    
    async def callback2(ctx: Interaction):
      if not ctx.user.id == usr and ctx.channel.id == chn:
          return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
      
      await db.settings.update_one(
          {'guild_id': ctx.guild.id},
          {'$set': {'welcome_text': self.mainMessage}}
        )
      
      await ctx.response.send_message("Welcome Message Saved!", ephemeral=True)
    
    async def callback3(ctx: Interaction):
      if not ctx.user.id == usr and ctx.channel.id == chn:
          return await ctx.response.send_message("You are not the user who used the command!", ephemeral=True)
      
      modal = welcomeModal()
      await ctx.response.send_modal(modal)
      em = discord.Embed(title="Here are the placeholders you can use for welcome Text.", description="**{member_mention}**: This placeholder to mention the member upon joining.\n**{member_name}**: This is a placeholder to show the members name.\n**{guild_name}**: This is a placeholder to show what servers name.\n**{member_count}**: This is a placeholder that will show what number member they are.", color=await getColor(ctx, "commands_color"))
      msg = await ctx.followup.send(embed=em, ephemeral=True)
      await modal.wait()
      self.mainMessage = str(modal.answer)

      await ctx.message.edit(content=self.mainMessage)


    button.callback = callback1
    submit.callback = callback2
    set_message.callback = callback3
    view = View()
    view.add_item(button)
    view.add_item(submit)
    view.add_item(set_message)
    msg = await ctx.response.edit_message(content=record['welcome_text'], view=view, embed=None)
      
  
class settings(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  

  @commands.hybrid_command(description="This will allow you to change some settings of the bot.", with_app_command = True, extras={"category": "Other"})
  @is_management()
  async def settings(self, ctx: commands.Context):
    await ctx.defer(ephemeral = False)
     
    em = discord.Embed(title=f"Settings Page", description=f"In this command you can edit any embed descriptions, colors, or toggles for LCU\n\n**Embeds** - Change any descriptions or reset any embeds\n**Colors** - Change any colors of the embeds\n**Other** - Toggle different features of LCU", color=await getColor(ctx, "commands_color"))
    view = SettingsPanel(ctx, self.bot)
    msg = await ctx.send(embed=em, view=view)
    await self.bot.wait_for('interaction', timeout=None, check=lambda message: message.user == ctx.author)
    return
  
  @settings.error
  async def settings_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MessageNotFound):
      pass
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    
async def setup(bot):
  await bot.add_cog(settings(bot))