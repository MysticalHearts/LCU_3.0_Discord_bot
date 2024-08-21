import discord
from discord.ext import tasks, commands
from discord.ui import View
from discord import Interaction
from cogs.utils.checks import get_info, getColor, is_staff, is_management, checkStaff, checkSetUp, checkManage
import re
from discord.ext.commands import MessageNotFound, MissingPermissions, MissingRequiredArgument, BadArgument
import platform
from cogs.events import db

# async def is_staff_check(ctx):
#   for user in ctx.bot.blacklists:
#     if ctx.author.id == int(user):
#         await ctx.channel.send("is_staff check")
#         return False
#   if await checkStaff(ctx) == "invalid":
#       if await checkSetUp(ctx):
#           return True
#       else:
#           return False
#   elif await checkStaff(ctx) == True or await checkManage(ctx) == True:
#       if await checkSetUp(ctx):
#           return True
#       else:
#           return False
#   else:
#       em = discord.Embed(title="Missing Permissions.", description="You don't have the correct roles to run this command.", color=discord.Color.red())
#       await ctx.channel.send(embed=em)
#       return False


class blacklistModal(discord.ui.Modal, title='Server Blacklist'):
      name = discord.ui.TextInput(label="Server Name")
      reason = discord.ui.TextInput(label="Reason", style=discord.TextStyle.paragraph)
      proof = discord.ui.TextInput(label="Proof", style=discord.TextStyle.paragraph)

      async def on_submit(self, ctx: Interaction):
        await ctx.response.defer()
        name = str(self.name)
        reason = str(self.reason)
        proof = str(self.proof)
        
        self.stop()

class blacklist_dropdown(discord.ui.View):
  def __init__(self):
    super().__init__()

  @discord.ui.button(label="Input", style=discord.ButtonStyle.green, row=0)
  async def select(self, interaction: discord.Interaction, select: discord.ui.Select):
    modal = blacklistModal()
    await interaction.response.send_modal(modal)
    await modal.wait()
    name = modal.name
    reason = modal.reason
    proof = modal.proof

    try:
      await interaction.message.delete()
    except:
      pass

    em = discord.Embed(title=f"{name} Blacklist", color=discord.Color.red())
    em.add_field(name="Blacklisted Server", value=name, inline=False)
    em.add_field(name="Reason", value=reason, inline=False)
    em.add_field(name="Proof", value=proof, inline=False)
    em.set_author(name=interaction.guild.name, icon_url=f"https://cdn.discordapp.com/{interaction.guild.icon}")
    await interaction.channel.send(embed=em, view=None)
  
  @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=1)
  async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.edit_message(content="Cancelled", embed=None, view=None)

    
class commands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.index = 0

  @tasks.loop(seconds=480)
  async def mreminder(self, ctx: Interaction):
    guild_info = await get_info(ctx)
    res2 = await db.settings.find_one({'guild_id': ctx.guild.id}, {'m_command_toggle': 1})
    if res2['m_command_toggle'] == 1:
      if guild_info['on_shift_role'] == None:
        return await ctx.channel.send(ctx, "It looks like you forgot to input an on shift role, please select one in the config command!")
      else:
        members = guild_info['on_shift_role']
        msg = ""
        staff = discord.utils.get(ctx.guild.roles, id=int(members))
        msg += f"{staff.mention}"
    else:
      msg = ""
    channel = discord.utils.get(ctx.guild.channels, id=int(guild_info['m_command_channel']))
    em = discord.Embed(title="Staff Reminder", description=f"```{guild_info['m_command_text']}```", color=await getColor(ctx, "commands_color"))
    button = discord.ui.Button(style=discord.ButtonStyle.grey, label="Claim", custom_id="claimButton")#this is the unclaimed button 

    async def bcallback(ctx: Interaction):
      em = discord.Embed(title="Staff Reminder", description=f"```{guild_info['m_command_text']}```", color=discord.Color.yellow())
      em.set_footer(text=f"Claimed by: {ctx.user}")
      button = discord.ui.Button(style=discord.ButtonStyle.green, label="Completed", custom_id="compButton")#this is the complete button

      async def b2callback(ctx: Interaction):
        em = discord.Embed(title="Staff Reminder", description=f"```{guild_info['m_command_text']}```", color=discord.Color.green())
        em.set_footer(text=f"Completed by: {ctx.user}")
        button = discord.ui.Button(style=discord.ButtonStyle.green, label="Completed", custom_id="compedButton", disabled=True)#this is the completed button
        view = View()
        button.callback = b2callback
        view.add_item(button)
        await ctx.response.edit_message(embed=em, content=msg, view=view)

      view = View()
      button.callback = b2callback
      view.add_item(button)
      await ctx.response.edit_message(embed=em, content=msg, view=view)

    view = View()
    button.callback = bcallback
    view.add_item(button)
    await channel.send(embed=em, content=msg, view=view)

  @commands.hybrid_command(description="This command will provide all important information about LCU.", with_app_command = True, extras={"category": "Other"})
  async def info(self, ctx: commands.Context):
    await ctx.defer(ephemeral = False)
    
    try:
      await ctx.message.delete()
    except:
      pass
     
    uptime = self.bot.uptime
    guilds = len(self.bot.guilds)
    users = sum([i.member_count for i in self.bot.guilds])
    version = await db.command('buildInfo')
    version = version['version']
    em = discord.Embed(title=f"LCU", description=f"LCU is a customizable ERLC server management bot. All session and interaction-type commands can be customized to your liking. We pride ourselves on listening to our community while also providing quality updates and support.", color=await getColor(ctx, "commands_color"))
    em.add_field(name="LCU Information", value=f"**Servers:** {guilds}\n**Users:** {users}\n**Uptime:** <t:{uptime}:R>\n**Latency:** {round(self.bot.latency, 2)}", inline=True) 
    em.add_field(name="Other", value=f"**Discord API Wrapper:** discord.py {discord.__version__}\n**Database System:** MongoDB {version}\n**Host OS:** {platform.system()}", inline=True) 
    em.add_field(name="Links", value="[Support Server](https://discord.gg/u5hx6Bc2U5)\n[Bot Invite](https://discord.com/api/oauth2/authorize?client_id=1057325266097156106&permissions=2194661702774&scope=bot%20applications.commands)", inline=False)
    em.set_thumbnail(url="https://cdn.discordapp.com/attachments/1073714080797425674/1105686471366684672/LCU_41.png") 
    await ctx.send(embed=em)

  @commands.hybrid_command(description="This command will ping the mod roles you provided on setup.", with_app_command = True, extras={"category": "Tools"}) 
  @is_staff()
  async def mod(self, ctx: commands.Context):
    await ctx.defer(ephemeral = False)

    try:
      await ctx.message.delete()
    except:
      pass
     
    guild_info = await get_info(ctx)
    channel = discord.utils.get(ctx.guild.channels, id=int(guild_info['ping_channel']))
    em = discord.Embed(title="All Moderators", description=f"{ctx.author.mention} needs help ingame, go help them out!", color=await getColor(ctx, "commands_color"))
    member = guild_info['mod_roles_id']
    member1 = member[1:-1]
    member_list = re.split(r',\s?', member1)
    msg = ""
    for member in member_list:
      staff = discord.utils.get(ctx.guild.roles, id=int(member))
      if staff:
        msg += f"{staff.mention}"
    try:
      await channel.send(content=f"{msg}", embed=em, allowed_mentions=discord.AllowedMentions(roles=True, users = True, replied_user=True))
    except: 
      await ctx.send("Ensure your staff request channel in setup is correct. I can't find your channel.")


  @commands.hybrid_command(description="This will ping the staff roles you provided on setup.", with_app_command = True, extras={"category": "Tools"})
  @is_staff()
  async def staff(self, ctx: commands.Context):
    await ctx.defer(ephemeral = False)

    try:
      await ctx.message.delete()
    except:
      pass
     
    guild_info = await get_info(ctx)
    channel = discord.utils.get(ctx.guild.channels, id=int(guild_info['ping_channel']))
    em = discord.Embed(title="Staff", description=f"{ctx.author.mention} needs help ingame, go help them out!", color=await getColor(ctx, "commands_color"))
    member = guild_info['staff_roles_id']
    member = member[1:-1]
    member_list = re.split(r',\s?', member)
    msg = ""
    for member in member_list:
      staff = discord.utils.get(ctx.guild.roles, id=int(member))
      msg += f"{staff.mention}"
    try:
      await channel.send(content=f"{msg}", embed=em, allowed_mentions=discord.AllowedMentions(roles=True, users = True, replied_user=True))
    except:
      await ctx.send("Ensure your staff request channel in setup is correct. I can't find your channel.")

  @commands.hybrid_command(description="This will start the staff reminders.", with_app_command = True, extras={"category": "Tools"}) 
  @is_staff()
  async def on(self, ctx: commands.Context):
    await ctx.defer(ephemeral = False)

    try:
      await ctx.message.delete()
    except:
      pass

    records = await db.settings.find_one({'guild_id': ctx.guild.id}, {'reminders_toggle': 1})
    try:
      if records['reminders_toggle'] == 0:
        return await ctx.send("You have reminders disabled, please enable them in the config command.", delete_after=3)
      elif records['reminders_toggle'] == 1:
        pass
    except:
      return await ctx.send("You have reminders disabled, please enable them in the config command.", delete_after=3)
     
    if self.mreminder.is_running() == False:
      self.mreminder.start(ctx)
    else:
      return await ctx.send("Staff reminders are currently **on**!", delete_after=3)
    await ctx.send("Staff reminders have been **started**.", delete_after=3)


  @commands.hybrid_command(description="This will stop your staff reminders.", with_app_command = True, extras={"category": "Tools"})
  @is_staff()
  async def off(self, ctx: commands.Context):
    await ctx.defer(ephemeral = False)

    try:
      await ctx.message.delete()
    except:
      pass

    records = await db.settings.find_one({'guild_id': ctx.guild.id}, {'reminders_toggle': 1})
    try:
      if records['reminders_toggle'] == 0:
        return await ctx.send("You have reminders disabled, please enable them in the config command.", delete_after=3)
      elif records['reminders_toggle'] == 1:
        pass
    except:
      return await ctx.send("You have reminders disabled, please enable them in the config command.", delete_after=3)
     
    if self.mreminder.is_running():
      self.mreminder.cancel()
    else:
      return await ctx.send("Staff reminders are currently **off**!", delete_after=3)
    await ctx.send("Staff reminders have been **stopped**.", delete_after=3)

  @commands.hybrid_command(description="This will make an embed with your provided message.", with_app_command = True, extras={"category": "Tools"})
  @is_staff()
  async def embed(self, ctx: commands.Context, *, message: str):
    await ctx.defer(ephemeral = False)

    try:
      await ctx.message.delete()
    except:
      pass
     
    em = discord.Embed(title=f"{ctx.guild.name}", description=message, color=await getColor(ctx, "commands_color"))
    await ctx.send(embed=em)
  
  @embed.error
  async def embed_error(self, ctx: commands.Context, error):
    if isinstance(error, MessageNotFound):
      pass
    elif isinstance(error, MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    elif isinstance(error, MissingRequiredArgument):
      return await ctx.send("Please make sure you have a message to send. Example: `-embed Hello World`")
    elif isinstance(error, BadArgument):
      return await ctx.send("Please make sure you have a message to send. Example: `-embed Hello World`")

  @is_staff()
  @commands.hybrid_command(description="This will send a message to the channel with the given message.", with_app_command = True, extras={"category": "Tools"})
  async def say(self, ctx: commands.Context, *, message: str):
    await ctx.defer(ephemeral = False)
    
    try:
      await ctx.message.delete()
    except:
      pass

    guild_info = await get_info(ctx)
    await ctx.send(message)
  
  @say.error
  async def say_error(self, ctx, error):
    if isinstance(error, MessageNotFound):
      pass
    elif isinstance(error, MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    elif isinstance(error, MissingRequiredArgument):
      return await ctx.send("Please make sure you have a message to send. Example: `-say Hello World`")
    elif isinstance(error, BadArgument):
      return await ctx.send("Please make sure you have a message to send. Example: `-say Hello World`")

  @commands.hybrid_command(description="This will send your advertisement to the channel.", with_app_command = True, extras={"category": "Tools"})
  async def ad(self, ctx: commands.Context):
    await ctx.defer(ephemeral = False)
    guild_info = await get_info(ctx)
    try:
      await ctx.message.delete()
    except:
      pass
    
    if not guild_info:
      guild_info = await get_info(ctx)
      if not guild_info:
        return await ctx.send("it seems like I can't reach your setup, try again!")
    em = discord.Embed(title=f"{ctx.guild.name}'s Advertisement", description=f"```{guild_info['advertisement']}```", color = await getColor(ctx, "commands_color"))
    await ctx.send(embed=em)
    
  @commands.hybrid_command(description="This will send a blacklist message for the server given", with_app_command = True, extras={"category": "Other"})
  @is_management()
  async def server_blacklist(self, ctx: commands.Context):
    await ctx.defer(ephemeral = False)
     
    try:
      await ctx.message.delete()
    except:
      pass
    
    em = discord.Embed(title="Server Blacklist", description="You can use this command to send a server blacklist notification. Make sure you have the following information ready:\n\n**-** Server Name\n**-** Reason\n**-** Proof", color=discord.Color(16763904))
    em.set_author(name="Server Blacklist", icon_url=f"https://cdn.discordapp.com/{ctx.guild.icon}")
    await ctx.send(embed = em, view=blacklist_dropdown())
    

    
async def setup(bot):
    await bot.add_cog(commands(bot))