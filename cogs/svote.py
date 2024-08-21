import discord
from discord.ext import commands
from cogs.utils.checks import get_info, get_embed_info, get_discord_color, convertEmbed, createUrlButton, is_management, make_custom_embed
from cogs.events import db
import time
import re

class voteButtons(discord.ui.View):
  def __init__(self, guild_info, bot, timestamp):
    super().__init__(timeout=None)
    self.votes = 0
    self.votedUsers = []
    self.guild_info = guild_info
    self.timestamp = timestamp
    self.bot = bot
    self.voted_message = ""
    

  @discord.ui.button(label="Vote", style=discord.ButtonStyle.grey)
  async def vote(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id in self.votedUsers:
      return await interaction.response.send_message("You cannot unreact to this vote or vote again!", ephemeral=True)
    elif interaction.user.id not in self.votedUsers:
      self.votedUsers.append(interaction.user.id)
      self.votes += 1

      await interaction.response.send_message("Success! You will be notified when a session has started!", ephemeral=True)

    em = await make_custom_embed(interaction, "svote", self.timestamp, self.guild_info)

    button.label = f"Vote ({self.votes}/{self.guild_info['vote_number']})"

    await interaction.message.edit(embed=em, view=self)
    
    
    if self.votes == int(self.guild_info['vote_number']):
      em = await make_custom_embed(interaction, "session", self.timestamp, self.guild_info)

      result = await db.settings.find_one({ 'guild_id': int(interaction.guild.id) }, { 'session_link': 1 })
      code = str(result['session_link'])

      view = await createUrlButton([code], ["Click to Join"])
      if view == "0x1":
        return await interaction.response.send_message("Something went wrong while creating the buttons, please contact LCU Support!")
      
      
      await interaction.message.edit(embed=em, view=view)

      for x in self.votedUsers:
        user = interaction.guild.get_member(int(x))
        self.voted_message += f"{user.mention} "
      await interaction.followup.send(f"{self.guild_info['emoji_id']} *The following people are required to join the session, failure to join will result in a infraction:*\n{self.voted_message}")

      
  @discord.ui.button(label="View Votes", style=discord.ButtonStyle.blurple)
  async def view(self, interaction: discord.Interaction, button: discord.ui.Button):
    votedUsers = ""
    for votes in self.votedUsers:
      votedUsers += f"<@{votes}>"

    if self.votedUsers == []:
      votedUsers = "No One Has Voted Yet!"
    
    em = discord.Embed(title="Voted Users", description=votedUsers)
    await interaction.response.send_message(embed=em, ephemeral=True)

class svote(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.hybrid_command(description = "This will start a session vote.", with_app_command = True, extras={"category": "Session Commands"})
  @is_management()
  async def svote(self, ctx: commands.Context):
    await ctx.defer(ephemeral=False)
    try:
      await ctx.message.delete()
    except discord.HTTPException:
      pass

    timestamp = int(time.time())
    guild_info = await get_info(ctx)
     

    em = await make_custom_embed(ctx, "svote", timestamp, guild_info)

    view = voteButtons(guild_info, self.bot, timestamp)
    view.vote.label = f"Vote ({view.votes}/{guild_info['vote_number']})"
    member = guild_info['session_role_id']

    try: 
      if re.search(r"\[\d+\]", member):
        member = member[1:-1]
      elif not re.search(r"\[\d+\]", member):
        pass
    except Exception:
      pass

    role = discord.utils.get(ctx.guild.roles, id=int(member))
    
    records1 = await db.settings.find_one({ 'guild_id': int(ctx.guild.id) }, { 'svote_here_toggle': 1 })
    
    if records1['svote_here_toggle'] != 1 and records1['svote_here_toggle'] != 0:
      await db.settings.update_one({ 'guild_id': int(ctx.guild.id) }, { '$set': {'svote_here_toggle': 1} })
    
    await ctx.send("Message Sent Successfuly!", delete_after=1, ephemeral=True)
    if not role or not role.mention:
      return await ctx.send("It looks like I either can't mention your session role or you have deleted it.")
    if records1['svote_here_toggle'] == 1:
      return await ctx.send(content=f"@here {role.mention}", embed=em, view=view, allowed_mentions=discord.AllowedMentions(roles=True, users = True, replied_user=True))

    await ctx.send(content=f"{role.mention}", embed=em, view=view, allowed_mentions=discord.AllowedMentions(roles=True, users = True, replied_user=True))

  @svote.error
  async def svote_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MessageNotFound):
      pass
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("I don't have the required permissions!")

async def setup(bot):
  await bot.add_cog(svote(bot)) 