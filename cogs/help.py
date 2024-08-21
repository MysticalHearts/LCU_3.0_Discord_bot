import discord
from discord.ext import commands
from discord import Interaction
import asyncio
from cogs.utils.checks import getColor

class searchModal(discord.ui.Modal, title='Setup'):

    answer = discord.ui.TextInput(label="Search Command", placeholder="Enter a command to search for.")

    async def on_submit(self, ctx: Interaction):
      await ctx.response.defer()
      answer = str(self.answer)

      self.stop()

class SettingsPanel(discord.ui.View):
    def __init__(self, ctx, bot, pages, cur_page, contents):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.bot = bot
        self.pages = pages
        self.cur_page = cur_page
        self.contents = contents

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.grey, emoji="<:LCUBack:1155281607280828446>")
    async def back(self, ctx: Interaction, button: discord.ui.Button):
      color = await getColor(ctx, "commands_color")
      super().__init__(timeout=None)
      if self.cur_page == 1:
        self.cur_page = self.pages
        e = discord.Embed(title=f"{list(self.contents.keys())[self.cur_page-1]}", description=f"\n{list(self.contents.values())[self.cur_page-1]}", color=color)
        e.set_footer(text=f"Page {self.cur_page}/{self.pages}")
        return await ctx.response.edit_message(embed=e)
      else:
        self.cur_page -= 1
        e = discord.Embed(title=f"{list(self.contents.keys())[self.cur_page-1]}", description=f"\n{list(self.contents.values())[self.cur_page-1]}", color=color)
        e.set_footer(text=f"Page {self.cur_page}/{self.pages}")
        return await ctx.response.edit_message(embed=e)
      
    @discord.ui.button(label="Next", style=discord.ButtonStyle.grey, emoji="<:LCUNext:1155282083745382440>")
    async def next(self, ctx: Interaction, button: discord.ui.Button):
      color = await getColor(ctx, "commands_color")

      if self.cur_page >= self.pages:
        self.cur_page = 1
        e = discord.Embed(title=f"{list(self.contents.keys())[self.cur_page-1]}", description=f"\n{list(self.contents.values())[self.cur_page-1]}", color=color)
        e.set_footer(text=f"Page {self.cur_page}/{self.pages}")
        return await ctx.response.edit_message(embed=e)
      else:
        self.cur_page += 1
        e = discord.Embed(title=f"{list(self.contents.keys())[self.cur_page-1]}", description=f"\n{list(self.contents.values())[self.cur_page-1]}", color=color)
        e.set_footer(text=f"Page {self.cur_page}/{self.pages}")
        return await ctx.response.edit_message(embed=e)
    
    @discord.ui.button(label="Search", style=discord.ButtonStyle.green, emoji="<:Search:1153875941496475710>")
    async def search(self, ctx: Interaction, button: discord.ui.Button):
      modal = searchModal()
      await ctx.response.send_modal(modal)
      await modal.wait()

      answer = str(modal.answer)
      if answer == None:
        return await ctx.followup.send("You didn't enter anything. Please try again.")
      else:
        command_ids = {}


        for command in await self.bot.tree.fetch_commands():
            for child in command.options:
                command_ids[f"{command.name} {child.name}"] = {}
                command_ids[f"{command.name} {child.name}"]['id'] = command.id
                command_ids[f"{command.name} {child.name}"]['description'] = str(child.description)
            
            command_ids[f"{command}"] = {}
            command_ids[f"{command}"]['id'] = command.id
            command_ids[f"{command}"]['description'] = command.description
        try:
          command_id = command_ids.get(f"{answer}")
          em = discord.Embed(title="Search Results", description=f"Here are the search results for the command **{answer}**.", color=await getColor(ctx, "commands_color"))
          em.add_field(name="Command", value=f"</{answer}:{command_id['id']}> - {command_ids[f'{answer}']['description']}")
          return await ctx.edit_original_response(embed = em, view = self)
        except:
          pass
        return await ctx.followup.send("Command not found.", ephemeral=True)



class helpc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Need help with commands? Run the help command.", with_app_command = True, extras={"category": "Other"})
    async def help(self, ctx: commands.Context):
      contents = {}
      command_ids = {}

      for command in await self.bot.tree.fetch_commands():
          for child in command.options:
              command_ids[f"{command.name} {child.name}"] = command.id
          command_ids[f"{command}"] = command.id

      for command in self.bot.walk_commands():
          category = command.extras.get('category')
          
          if category and category not in ('Group', 'Staff'):
              contents.setdefault(str(category), "")
              cat = str(category)
              value = contents.get(cat, "")
              
              try:
                  command_id = command_ids.get(f"{command}")
              except:
                  pass
              
              value += f"</{command}:{command_id}> - {command.description}\n\n"
              contents[cat] = value
      
      pages = int(len(contents))
      cur_page = 1
        
      color = await getColor(ctx, "commands_color")

      e = discord.Embed(title=f"{list(contents.keys())[0]}", description=f"\n{list(contents.values())[0]}", color=color)
      e.set_footer(text=f"Page {cur_page}/{pages}")
      view = SettingsPanel(ctx, self.bot, pages, cur_page, contents)
      msg = await ctx.send(embed=e, view = view)

      try:
        await self.bot.wait_for('interaction', timeout=800, check=lambda message: message.user == ctx.author and message.channel == ctx.channel)
      except asyncio.TimeoutError:
        view.next.disabled = True
        view.back.disabled = True
        return await msg.edit(view=view)

async def setup(bot):
  await bot.add_cog(helpc(bot))