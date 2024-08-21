import discord
from discord.ext import commands
from discord.ui import View
from .utils.checks import is_management
from .events import db

class EmbedPanel(View):
  def __init__(self):
    super().__init__(timeout=None)
  
class ColorsPanel(View):
  def __init__(self):
    super().__init__(timeout=None)

class ModuleToggleSelect(discord.ui.View):
    def __init__(self, bot, records):
        super().__init__(timeout=None)
        self.bot = bot
        self.records = records
        self.result = sum(1 for record in records.values() if record == 1)
        
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

    async def interaction_check(self, interaction: discord.Interaction):
      selected_value = interaction.data["values"][0]
      match selected_value:
        case "r_mod":
          return
        case "loa_mod":
          return
        case "here_ping":
          return
        case "logging_mod":
          return
        case "welcome_mod":
          return
        case "r_ping":
          return

class settings(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  

  @commands.hybrid_command(description="This will allow you to change some settings of the bot.", with_app_command = True, extras={"category": "Other"})
  @is_management()
  async def settings(self, ctx: commands.Context):

    records = await db.settings.find_one({'guild_id': int(ctx.guild.id)}, {'m_command_toggle': 1, "svote_here_toggle": 1, "loa_toggle": 1, "logging_toggle": 1, "welcome_toggle": 1, "reminders_toggle": 1})
    view = ModuleToggleSelect(self.bot, records)

    await ctx.send("Select a module to toggle.", view=view)
    await view.wait()

    await ctx.send(view.value)
  
  @settings.error
  async def settings_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MessageNotFound):
      pass
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    
async def setup(bot):
  await bot.add_cog(settings(bot))