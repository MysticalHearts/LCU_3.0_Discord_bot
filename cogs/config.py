import discord
from discord.ext import commands
from discord.ui import View
from cogs.utils.checks import is_management, role_select, channel_select
from cogs.utils.modals import MLOALength
from cogs.events import db

class selectMenu(discord.ui.Select):
    def __init__(self, options, parent_view):
        self.parent_view = parent_view
        self.interaction = None
        super().__init__(placeholder="What would you like to do?", min_values=1, max_values=1, row=0, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        self.parent_view.stop()
        self.interaction = interaction
    
class addRoleTypeNameModal(discord.ui.Modal, title="Add Role Type"):
    name = discord.ui.TextInput(label="Name", placeholder="Role Type Name", min_length=1, max_length=20)
    
    def __init__(self, parent_view):
        self.parent_view = parent_view
        self.interaction = None
        super().__init__(timeout=None)
    
    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.stop() 
        self.interaction = interaction
        
class roleTypePermissionsMenu(discord.ui.Select):
    def __init__(self, parent_view):
        self.parent_view = parent_view
        self.interaction = None
        super().__init__(placeholder="What permissions would you like for this Role Type?", min_values=1, max_values=6, row=0, options=[
            discord.SelectOption(label="Session Module", description="Allow this role type to use the Sessions Module"),
            discord.SelectOption(label="Shift System", description="Allow this role type to use the Shift System"),
            discord.SelectOption(label="Staff", description="Allow this role type to use stuff like the LOA Module, STS Logging, etc"),
            discord.SelectOption(label="Basic", description="Allow this role type to use basic commands like -say and -embed"),
            discord.SelectOption(label="Configuration", description="Allow this role type to modify the configuration of the bot"),
            discord.SelectOption(label="Staff Infraction Module", description="Allow this role type to use the Staff Infraction Module"),
        ])
        
    async def callback(self, interaction: discord.Interaction):
        self.parent_view.stop()
        self.interaction = interaction
        
class ModuleToggleSelect(discord.ui.View):
    def __init__(self, bot, records):
        super().__init__(timeout=None)
        self.bot = bot
        self.records = records
        self.result = sum(1 for record in self.records.values() if record == 1)
        
        select_options = [
            discord.SelectOption(label="Reminders Module", value="r_mod", description="Toggles the use of the -on and -off commands which will send the Reminder Text every 4 minutes."),
            discord.SelectOption(label="LOA Module", value="loa_mod", description="Toggles the use of -loa request, -loa manage, and -loa admin commands."),
            discord.SelectOption(label="SVote Here Ping", value="here_ping", description="Toggles the @here ping in the svote command."),
            discord.SelectOption(label="Logging Module", value="logging_mod", description="Toggles the logging module."),
            discord.SelectOption(label="Welcome Module", value="welcome_mod", description="Toggles the welcoming feature."),
            discord.SelectOption(label="Reminder Pings", value="r_ping", description="Toggles the pings for the -on and -off commands."),
        ]

        self.add_item(discord.ui.Select(
            placeholder=f"{self.result} Modules Enabled",
            min_values=1,
            max_values=1,
            options=select_options,
            custom_id="module_toggle"
        ))

        self.back_button = discord.ui.Button(style=discord.ButtonStyle.red, label="Back", custom_id="go_back")
        self.add_item(self.back_button)

    async def interaction_check(self, interaction: discord.Interaction):
      if list(interaction.data.values())[0] == 'go_back':
        embed = discord.Embed(title="LCU Configuration", description="Welcome to the LCU configuration menu. Here you can configure and enable specific features.\n\n **• Graphics** - In the graphics menu you can reconfigure banners, emojis, and more!\n\n **• Roles & Channels** - Here you can reconfigure your roles and channels (Staff Roles, Reminders channel, etc).\n\n **• Server Information** - Here you can reconfigure your server information (Server name, Server Code, etc).\n\n **• Embeds** - Configure your server embeds and embed colors (session embed, shutdown embed, etc)\n\n **• Modules** - Enable / disable your server modules (STS logging, Shift System, etc)n\n\n **• Other** - Miscellaneous. Enable/Disable pings for certain things, schedule certain things (like sessions, etc).", color=discord.Color.from_rgb(255,203,0))
        await interaction.response.edit_message(embed=embed, view=mainConfig(self.bot))
        return False
      
      selected_value = interaction.data["values"][0]
      match selected_value:
        case "r_mod":
          if self.records['reminders_toggle'] == 0 or self.records['reminders_toggle'] == None:

            select1 = channel_select(1, 1, interaction.user.id)
            view = View()
            view.add_item(select1)
            await interaction.response.send_message(
                content=f"This channel will be used to send the reminders to.",
                view=view,
            )
            await select1.view_obj.wait()
            await select1.interaction.response.edit_message(view=None)
            reminders_channel = select1.channels

            await select1.interaction.delete_original_response()
            
            await db.settings.update_one(
              {'guild_id': interaction.guild.id},
              {'$set': {'reminders_toggle': 1, 'reminders_channel': reminders_channel}}
            )
            return await interaction.followup.send("LOA function: **ON**", ephemeral=True)
          elif self.records['reminders_toggle'] == 1:
            await db.settings.update_one(
              {'guild_id': interaction.guild.id},
              {'$set': {'reminders_toggle': 0}}
            )
          return await interaction.response.send_message("LOA function: **OFF**", ephemeral=True)
        
        #--------------------loa module--------------------------------
        case "loa_mod":
          if self.records['loa_toggle'] == 0 or self.records['loa_toggle'] == None:
            modal = MLOALength()
            await interaction.response.send_modal(modal)
            await modal.wait()
            
            select = role_select(1, 1, interaction.user.id)
            view = View()
            view.add_item(select)
            await interaction.followup.send(
                content=f"This role is used for active LOAs.",
                view=view,
            )
            await select.view_obj.wait()
            loa_role = select.roles

            select1 = channel_select(1, 1, interaction.user.id)
            view = View()
            view.add_item(select1)
            await select.interaction.response.edit_message(
                content=f"This channel will be used to send the LOA Requests.",
                view=view,
            )
            await select1.view_obj.wait()
            loa_channel = select1.channels

            await select.interaction.delete_original_response()
            
            await db.settings.update_one(
              {'guild_id': interaction.guild.id},
              {'$set': {'loa_toggle': 1, 'loa_role': loa_role, 'loa_channel': loa_channel}}
            )
            return await interaction.followup.send("LOA function: **ON**", ephemeral=True)
          elif self.records['loa_toggle'] == 1:
            await db.settings.update_one(
              {'guild_id': interaction.guild.id},
              {'$set': {'loa_toggle': 0}}
            )
            return await interaction.response.send_message("LOA function: **OFF**", ephemeral=True)
        
        #-----------------Here Ping-------------------------------------
        case "here_ping":
          if self.records['svote_here_toggle'] == 0:
            await db.settings.update_one(
              {'guild_id': int(interaction.guild.id)},
              {'$set': {'svote_here_toggle': 1}}
            )
            return await interaction.response.send_message("Session Here Ping: **ON**", ephemeral=True)
          elif self.records['svote_here_toggle'] == 1:
            await db.settings.update_one(
              {'guild_id': int(interaction.guild.id)},
              {'$set': {'svote_here_toggle': 0}}
            )
            return await interaction.response.send_message("Session Here Ping: **OFF**", ephemeral=True)
        
        #------------------------------logging module--------------------
        case "logging_mod":
          try:
            if self.records['logging_toggle'] == 0:
              record = 0
            elif self.records['logging_toggle'] == 1:
              record = 1
          except:
            record = 0

          if record == 1:
            await db.settings.update_one(
                {'guild_id': interaction.guild.id},
                {'$set': {'logging_toggle': 0}}
              )
            return await interaction.response.send_message("Logging: **OFF**", ephemeral=True)
          else:
            select = channel_select(1, 1, interaction.user.id)
            view = View()
            view.add_item(select)
            await interaction.response.send_message(
                content=f"This is your main logging channel",
                view=view,
            )
            await select.view_obj.wait()
            await select.interaction.response.edit_message(view=None)
            main_channel = select.channels

            select1 = channel_select(1, 1, interaction.user.id)
            view = View()
            view.add_item(select1)
            await select.interaction.edit_original_response(
                content=f"This is the channel where your join logs will go to.",
                view=view,
            )
            await select1.view_obj.wait()
            await select1.interaction.response.edit_message(view=None)
            join_channel = select1.channels

            select = channel_select(1, 1, interaction.user.id)
            view = View()
            view.add_item(select)
            await select1.interaction.edit_original_response(
                content=f"This is the channel where your leave logs will go to.",
                view=view,
            )
            await select.view_obj.wait()
            await select.interaction.response.edit_message(view=None)
            leave_channel = select.channels

            await select.interaction.delete_original_response()

            await db.settings.update_one(
                {'guild_id': interaction.guild.id},
                {'$set': {'logging_toggle': 1, 'leave_channel': leave_channel, 'join_channel': join_channel, 'logging_channel': main_channel}}
              )
            return await interaction.followup.send("Logging: **ON**", ephemeral=True)
        
        #--------------------------------Welcome Module------------------------------
        case "welcome_mod":
          try:
            if self.records['welcome_toggle'] == 0:
              record = 0
            elif self.records['welcome_toggle'] == 1:
              record = 1
          except:
            record = 0

          if record == 1:
            await db.settings.update_one(
                {'guild_id': interaction.guild.id},
                {'$set': {'welcome_toggle': 0}}
              )
            return await interaction.response.send_message("Welcome: **OFF**", ephemeral=True)
          else:
            select = channel_select(1, 1, interaction.user.id)
            view = View()
            view.add_item(select)
            await interaction.response.send_message(
                content=f"This is the channel that sends the welcome message",
                view=view,
            )
            await select.view_obj.wait()
            await select.interaction.response.edit_message(view=None)
            main_channel = select.channels

            await select.interaction.delete_original_response()

            await db.settings.update_one(
                {'guild_id': interaction.guild.id},
                {'$set': {'welcome_toggle': 1, 'welcome_text': 'Welcome {member.mention} to {guild.name}!', 'welcome_channel': main_channel}}
              )
            return await interaction.followup.send("Welcome: **ON**", ephemeral=True)
        
        #---------------------------------------Reminder Ping----------------------------------
        case "r_ping":
          if self.records['m_command_toggle'] == 0:
            await db.settings.update_one(
              {'guild_id': int(interaction.guild.id)},
              {'$set': {'m_command_toggle': 1}}
            )
            return await interaction.response.send_message("M Command Ping: **ON**", ephemeral=True)
          elif self.records['m_command_toggle'] == 1:
            await db.settings.update_one(
              {'guild_id': int(interaction.guild.id)},
              {'$set': {'m_command_toggle': 0}}
            )
            return await interaction.response.send_message("M Command Ping: **OFF**", ephemeral=True)

class mainConfig(View):
    def __init__(self, bot):
      self.bot = bot
      super().__init__(timeout=None)
    
    @discord.ui.select(placeholder="Please select a category", min_values=1, max_values=1, row=0, options=[
          discord.SelectOption(label="Graphics", description="Configure your server graphics (banners, emojis, etc)", emoji="🖼️"), 
          discord.SelectOption(label="Roles and Channels", description="Configure your roles and channels (management and staff roles, LOA channel, etc)", emoji="📝"), 
          discord.SelectOption(label="Roles Types", description="Configure your roles and channels (management and staff roles, LOA channel, etc)", emoji="📝"), 
          discord.SelectOption(label="Server Information", description="Configure your server information (server name, code, etc)", emoji="🔧"),
          discord.SelectOption(label="Embeds", description="Configure your server embeds and embed colors (session embed, shutdown embed, etc)", emoji="📰"),
          discord.SelectOption(label="Modules", description="Enable / disable your server modules (STS logging, Shift System, etc)", emoji="🔌"),
          discord.SelectOption(label="Other", description="Miscellaneous. Enable/Disable pings for certain things, schedule certain things, etc)", emoji="❓")
        ])
    async def main_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "Graphics":
            em = discord.Embed(title="Graphics Config", description="This is a test", color=discord.Color.blue())
            await interaction.response.edit_message(embed=em)
        elif select.values[0] == "Modules":
            self.records = await db.settings.find_one({'guild_id': int(interaction.guild.id)}, {'m_command_toggle': 1, "svote_here_toggle": 1, "loa_toggle": 1, "logging_toggle": 1, "welcome_toggle": 1, "reminders_toggle": 1})
            view = ModuleToggleSelect(self.bot, self.records)

            embed=discord.Embed(title="LCU Configuration", description=f"All of these modules are toggles, select one to toggle on and or off.\n\n**• Reminders Module** - This will toggle the `-on` and `-off` commands\n\n**• LOA Module** - This will toggle the LOA module with Min, Max, LOA Role, and LOA Channels fields.\n\n**• Svote Here Ping** - This will enable the @here ping on the `-svote` command\n\n**• Logging Module** - With this toggle the logging system with Join, Leave, and General Log fields\n\n**• Welcome Module** - This will toggle the welcoming module with custom welcome messages\n\n**• Reminders Ping** - This will toggle the ping on the `-on` and `-off` commands", color=discord.Color.from_rgb(255,203,0))
            await interaction.response.edit_message(embed=embed, view=view)
            await view.wait()
        elif select.values[0] == "Roles and Channels":
            pass
        elif select.values[0] == "Roles Types":
            view = View()
            select = selectMenu(options=[
                discord.SelectOption(label="Add Role Type", description="Add a Role Type", emoji="➕"),
                discord.SelectOption(label="Delete Role Type", description="Delete a Role Type", emoji="➖"),
                discord.SelectOption(label="Modify Role Type", description="Modify a Role Type", emoji="🔧")
            ], parent_view=view)
            view.add_item(select)
            await interaction.response.edit_message("What would you like to do? **Add, Delete, or Modify**.", view=view)
            await view.wait()

            if select.values[0] == "Add Role Type":
                button = discord.ui.Button(style=discord.ButtonStyle.green, label="Input a name for your Role Type.")
                view = discord.ui.View()
                modal = addRoleTypeNameModal(parent_view=view)
                button.callback = lambda i: i.response.send_modal(modal)
                view.add_item(button)
                await select.interaction.response.send_message("What would you like to name the Role Type?", view=view)
                await view.wait()
                select = role_select(1, 20, interaction.user.id)
                view = View()
                view.add_item(select)
                await modal.interaction.response.send_message("What role(s) would you like to assign to this Role Type?", view=view)
                await select.view_obj.wait()
                roles = select.roles
                view = View()
                select = roleTypePermissionsMenu(parent_view=view)
                view.add_item(select)
                done = discord.ui.Button(style=discord.ButtonStyle.green, label="Done")
                done.callback = lambda i: view.stop()
                view.add_item(done)
                await select.interaction.response.send_message(f"What permissions would you like to give to this Role Type?", view=view)
                await view.wait()
                
            elif select.values[0] == "Delete Role Type":
                pass
            elif select.values[0] == "Modify Role Type":
                pass
       
class config(commands.Cog):
    def __init__ (self, bot):
      self.bot = bot
      self.staff_roles_returns = []

    @commands.hybrid_command(description="This will allow you to configure and enable specific features within LCU to your liking!", with_app_command = True, extras={"category": "Other"})
    @is_management()
    async def config(self, ctx: commands.Context):
      await ctx.defer()
      embed = discord.Embed(title="LCU Configuration", description="Welcome to the LCU configuration menu. Here you can configure and enable specific features.\n\n **• Graphics** - In the graphics menu you can reconfigure banners, emojis, and more!\n\n **• Roles & Channels** - Here you can reconfigure your roles and channels (Staff Roles, Reminders channel, etc).\n\n **• Server Information** - Here you can reconfigure your server information (Server name, Server Code, etc).\n\n **• Embeds** - Configure your server embeds and embed colors (session embed, shutdown embed, etc)\n\n **• Modules** - Enable / disable your server modules (STS logging, Shift System, etc)n\n\n **• Other** - Miscellaneous. Enable/Disable pings for certain things, schedule certain things (like sessions, etc).", color=discord.Color.from_rgb(255,203,0))
      await ctx.send(embed=embed, view=mainConfig(self.bot))
    
    @config.error
    async def config_error(self, ctx: commands.Context, error):
      if isinstance(error, commands.MessageNotFound):
        pass
      elif isinstance(error, commands.MissingPermissions):
        return await ctx.send("I don't have the required permissions!")



  

async def setup(bot):
  await bot.add_cog(config(bot))