import discord
from discord.ext import commands
import time
from cogs.utils.checks import get_info, getColor, convertEmbed, get_embed_info, is_management, is_staff
from cogs.events import db
from bson import ObjectId

class infractions(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.hybrid_group(with_app_command = True, extras={"category": "Group"})
  @is_staff()
  async def search(self, ctx: commands.Context):
    return

  @commands.hybrid_group(with_app_command = True, extras={"category": "Group"})
  @is_staff()
  async def delete(self, ctx: commands.Context):
    return
  
  @search.command(description="This command will search any STS logs.", with_app_command = True, extras={"category": "Logs"})
  @is_staff()
  async def sts(self, ctx: commands.Context, member: discord.Member):
    async def create_sts_embed(page_number):
        embed = discord.Embed(title="", color=await getColor(ctx, "commands_color"))
        embed.set_author(name=f"{member.name}'s STS History ({len(sts)})", icon_url=member.avatar.url)
        if not total_pages <= 1:
            embed.set_footer(text=f"Page {page_number + 1}/{total_pages}")
            
        sts_number = 0

        for warn in sts_chunks[page_number]:
            sts_number += 1
            if warn['time'] == 1:
                embed.add_field(name=f"ID: {sts_number}", value=f"**Reason:** {warn['reason']}\n**Time:** {warn['time']} minute\n**User:** <@{warn['user']}>\n**Date:** {warn['date']}", inline=False)
            else:
                embed.add_field(name=f"ID: {sts_number}", value=f"**Reason:** {warn['reason']}\n**Time:** {warn['time']} minutes\n**User:** <@{warn['user']}>\n**Date:** {warn['date']}", inline=False)

        return embed

    def check(interaction):
        return interaction.user == ctx.author

    records_yguilds = db.logs.find({'guild_id': {'$exists': True}, 'user': ctx.author.id, 'type': "sts"}).to_list(None)
    records_nguilds = db.logs.find({'guild_id': {'$exists': False}, 'user': ctx.author.id, 'type': "sts"}).to_list(None)

    sts = []

    for record in records_nguilds:
        sts.append(record)

    for item in records_yguilds:
        key = item["guild_id"]
        if int(key) == ctx.guild.id:
            sts.append(item)

    sts_chunks = [sts[i:i + 6] for i in range(0, len(sts), 6)]

    if not sts_chunks:
        return await ctx.send("No STS logs found for this user.")

    total_pages = len(sts_chunks)
    current_page = 0

    farward_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.grey, emoji="<:LCUNext:1155282083745382440>")
    back_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.grey, emoji="<:LCUBack:1155281607280828446>")

    view = discord.ui.View()
    view.add_item(back_button)
    view.add_item(farward_button)

    async def farwardCallBack(interaction: discord.Interaction):
        nonlocal current_page
        current_page = (current_page + 1) % total_pages
        await interaction.response.edit_message(embed=await create_sts_embed(current_page), view=view)

    async def backwardCallBack(interaction: discord.Interaction):
        nonlocal current_page
        current_page = (current_page - 1) % total_pages
        await interaction.response.edit_message(embed=await create_sts_embed(current_page), view=view)

    farward_button.callback = farwardCallBack
    back_button.callback = backwardCallBack

    message = await ctx.send(embed=await create_sts_embed(current_page), view=view)

    try:
        await ctx.message.delete()
    except:
        pass
    
  

  @commands.hybrid_command(description="This command will warn a staff member.", with_app_command = True, extras={"category": "Infractions"})
  @is_staff()
  async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = "None Was Specified"):
      await ctx.defer(ephemeral = False)

      try:
        await ctx.message.delete()
      except:
        pass
       
      guild_info = await get_info(ctx)
      timestamp = int(time.time())

      await db.warns.insert_one({
          'guild_id': ctx.guild.id,
          'user_id': member.id,
          'warn_reason': reason,
          'moderator': ctx.author.id
          
      })
      embed_info = await get_embed_info(ctx, 'warn')

      newDescription = await convertEmbed(ctx, embed_info[0], embed_info[2], embed_info[3], embed_info[5], guild_info, timestamp, "warn")
      
      em = discord.Embed(title=f"{newDescription[1]}", description=f"{newDescription[0]} \n\n> **Username:** {member.mention}\n> **Reason:** {reason}\n> **Server**: {ctx.guild.name}\n> **Submission Date:** <t:{timestamp}:F>", color=await getColor(ctx, "warn_color"))
      if embed_info[4]:
            em.set_author(name=newDescription[3], icon_url=embed_info[4])

      if embed_info[3]:
          em.set_footer(text=newDescription[2])

      await ctx.send(embed=em)

      try:
        await member.send(embed=em)
      except:
        pass

  
  @warn.error
  async def warn_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MessageNotFound):
      pass
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    elif isinstance(error, commands.MissingRequiredArgument):
      return await ctx.send("Please make sure you have a member than a reason. Example: `-warn @person Spamming`")
    elif isinstance(error, commands.BadArgument):
      return await ctx.send("Please make sure you have a member than a reason. Example: `-warn @person Spamming`")
    elif isinstance(error, commands.CommandInvokeError):
      pass
  
  @search.command(description="This command will search any warns for a staff member.", with_app_command=True, extras={"category": "Infractions"}, name="warns")
  @is_staff()
  async def search_warns(self, ctx: commands.Context, member: discord.Member):
    async def on_timeout():
        farward_button.disabled = True
        back_button.disabled = True
        await msg.edit(view=view)

    async def farwardCallBack(interaction: discord.Interaction):
        nonlocal current_page
        current_page = (current_page + 1) % total_pages
        await interaction.response.edit_message(embed=await create_warn_embed(current_page), view=view)
    
    async def backwardCallBack(interaction: discord.Interaction):
        nonlocal current_page
        current_page = (current_page - 1) % total_pages
        await interaction.response.edit_message(embed=await create_warn_embed(current_page), view=view)

    await ctx.defer(ephemeral=False)

    try:
        await ctx.message.delete()
    except:
        pass

    records_yguilds = await db.warns.find({'guild_id': {'$exists': True}, 'user_id': member.id}).to_list(None)
    records_nguilds = await db.warns.find({'guild_id': {'$exists': False}, 'user_id': member.id}).to_list(None)
    warns = []

    for record in records_nguilds:
        warns.append(record)

    for item in records_yguilds:
        key = item["guild_id"]
        if int(key) == ctx.guild.id:
            warns.append(item)

    warns_chunks = [warns[i:i + 6] for i in range(0, len(warns), 6)]

    if not warns_chunks:
        return await ctx.send("No warns found for this user.")

    total_pages = len(warns_chunks)
    current_page = 0

    async def create_warn_embed(page_number):
        embed = discord.Embed(title=f"", color=await getColor(ctx, "commands_color"))
        embed.set_author(name=f"{member.name}'s Warn History ({len(warns)})", icon_url=member.avatar.url)
        if not total_pages <= 1:
          embed.set_footer(text=f"Page {page_number + 1}/{total_pages}")

        for warn in warns_chunks[page_number]:
            embed.add_field(name=f"ID: {warn['_id']}", value=f"**Reason:** {warn['warn_reason']}\n**Moderator:** <@{warn['moderator']}>", inline=False)

        return embed

    if not total_pages <= 1:
      view = discord.ui.View()
      farward_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.grey, emoji="<:LCUNext:1155282083745382440>")
      back_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.grey, emoji="<:LCUBack:1155281607280828446>")
      view.add_item(back_button)
      view.add_item(farward_button)

      view.timeout = 120
      view.on_timeout = on_timeout

      farward_button.callback = farwardCallBack
      back_button.callback = backwardCallBack
    

      msg = await ctx.send(embed=await create_warn_embed(current_page), view=view)
    elif total_pages <= 1:
      msg = await ctx.send(embed=await create_warn_embed(current_page))

  
  @search_warns.error
  async def search_warns_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MessageNotFound):
      pass
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    elif isinstance(error, commands.MissingRequiredArgument):
      return await ctx.send("Please make sure you have a member. Example: `-search warns @person`")
    elif isinstance(error, commands.BadArgument):
      return await ctx.send("Please make sure you have a member. Example: `-search warns @person`")
    elif isinstance(error, commands.CommandInvokeError):
      pass

  @commands.hybrid_command(description="This command will strike a staff member.", with_app_command = True, extras={"category": "Infractions"}) 
  @is_staff()
  async def strike(self, ctx: commands.Context, member: discord.Member, *, reason: str = "None was specified."):
      await ctx.defer(ephemeral = False)
      
      try:
        await ctx.message.delete()
      except:
        pass
       
      guild_info = await get_info(ctx)
      timestamp = int(time.time())

      await db.strikes.insert_one({
        'guild_id': ctx.guild.id,
        'user_id': member.id,
        'strike_reason': reason,
        'moderator': ctx.author.id
      })
      embed_info = await get_embed_info(ctx, 'strike')

      newDescription = await convertEmbed(ctx, embed_info[0], embed_info[2], embed_info[3], embed_info[5], guild_info, timestamp, "strike")
      
      em = discord.Embed(title=f"{newDescription[1]}", description=f"{newDescription[0]} \n\n> **Username:** {member.mention}\n> **Reason:** {reason}\n> **Server**: {ctx.guild.name}\n> **Submission Date:** <t:{timestamp}:F>", color=await getColor(ctx, "strike_color"))
      if embed_info[4]:
          em.set_author(name=newDescription[3], icon_url=embed_info[4])

      if embed_info[3]:
          em.set_footer(text=newDescription[2])

      await ctx.send(embed=em)
      
      try:
        await member.send(embed=em)
      except:
        pass

  
  @strike.error
  async def strike_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MessageNotFound):
      pass
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    elif isinstance(error, commands.MissingRequiredArgument):
      return await ctx.send("Please make sure you have a member than a reason. Example: `-strike @person Spamming`")
    elif isinstance(error, commands.BadArgument):
      return await ctx.send("Please make sure you have a member than a reason. Example: `-strike @person Spamming`")
    elif isinstance(error, commands.CommandInvokeError):
      pass

  @search.command(description="This command will search any strikes for a staff member.", with_app_command = True, extras={"category": "Infractions"}, name="strikes")
  @is_staff()
  async def search_strikes(self, ctx: commands.Context, member: discord.Member):
    async def on_timeout():
      farward_button.disabled = True
      back_button.disabled = True
      await msg.edit(view=view)

    async def farwardCallBack(interaction: discord.Interaction):
        nonlocal current_page
        current_page = (current_page + 1) % total_pages
        await interaction.response.edit_message(embed=await create_strike_embed(current_page), view=view)
    
    async def backwardCallBack(interaction: discord.Interaction):
        nonlocal current_page
        current_page = (current_page - 1) % total_pages
        await interaction.response.edit_message(embed=await create_strike_embed(current_page), view=view)

    await ctx.defer(ephemeral=False)

    try:
        await ctx.message.delete()
    except:
        pass

    records_yguilds = await db.strikes.find({'guild_id': {'$exists': True}, 'user_id': member.id}).to_list(None)
    records_nguilds = await db.strikes.find({'guild_id': {'$exists': False}, 'user_id': member.id}).to_list(None)
    strikes = []

    for record in records_nguilds:
        strikes.append(record)

    for item in records_yguilds:
        key = item["guild_id"]
        if int(key) == ctx.guild.id:
            strikes.append(item)

    strike_chunks = [strikes[i:i + 6] for i in range(0, len(strikes), 6)]

    if not strike_chunks:
        return await ctx.send("No strikes are found for this user.")

    total_pages = len(strike_chunks)
    current_page = 0

    async def create_strike_embed(page_number):
        embed = discord.Embed(title=f"", color=await getColor(ctx, "commands_color"))
        embed.set_author(name=f"{member.name}'s Strike History ({len(strikes)})", icon_url=member.avatar.url)
        if not total_pages <= 1:
          embed.set_footer(text=f"Page {page_number + 1}/{total_pages}")

        for warn in strike_chunks[page_number]:
            embed.add_field(name=f"ID: {warn['_id']}", value=f"**Reason:** {warn['strike_reason']}\n**Moderator:** <@{warn['moderator']}>", inline=False)

        return embed

    if not total_pages <= 1:
      view = discord.ui.View()
      farward_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.grey, emoji="<:LCUNext:1155282083745382440>")
      back_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.grey, emoji="<:LCUBack:1155281607280828446>")
      view.add_item(back_button)
      view.add_item(farward_button)

      view.timeout = 120
      view.on_timeout = on_timeout

      farward_button.callback = farwardCallBack
      back_button.callback = backwardCallBack
    

      msg = await ctx.send(embed=await create_strike_embed(current_page), view=view)
    elif total_pages <= 1:
      msg = await ctx.send(embed=await create_strike_embed(current_page))
  
  @search_strikes.error
  async def search_strikes_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MessageNotFound):
      pass
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    elif isinstance(error, commands.MissingRequiredArgument):
      return await ctx.send("Please make sure you have a member. Example: `-search strikes @person`")
    elif isinstance(error, commands.BadArgument):
      return await ctx.send("Please make sure you have a member. Example: `-search strikes @person`")
    elif isinstance(error, commands.CommandInvokeError):
      pass

  @delete.command(description="This command will delete a warn for a staff member", with_app_command = True, extras={"category": "Infractions"}, name="warn")
  @is_staff()
  async def delete_warn(self, ctx: commands.Context, member: discord.Member, *, id: str):
      await ctx.defer(ephemeral = False)

      try:
        await ctx.message.delete()
      except:
        pass
       
      guild_info = await get_info(ctx)
      if len(id) < 24:
        em = discord.Embed(title=f"", description=f"Please input a valid ID.", color=discord.Color.from_rgb(255, 255, 254))
        return await ctx.send(embed=em)
      
      object_id = ObjectId(str(id))
      result = await db.warns.find_one({'_id': object_id})
      if not result:
        em = discord.Embed(title=f"", description=f"This warn is not in our database", color=discord.Color.from_rgb(255, 255, 254))
        return await ctx.send(embed=em)
      else:
        await db.warns.delete_one({'_id': object_id})

      await ctx.send(f"`{id}` has been deleted!")

  
  @delete_warn.error
  async def delete_warn_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MessageNotFound):
      pass
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    elif isinstance(error, commands.MissingRequiredArgument):
      return await ctx.send("Please make sure you have a member than an ID of the warn. Example: `-delete warn @person 1234`")
    elif isinstance(error, commands.BadArgument):
      return await ctx.send("Please make sure you have a member than an ID of the warn. Example: `-delete warn @person 1234`")
    elif isinstance(error, commands.CommandInvokeError):
      pass

  @delete.command(description="This command will delete a strike for a staff member.", with_app_command = True, extras={"category": "Infractions"}, name="strike")
  @is_staff()
  async def delete_strike(self, ctx: commands.Context, member: discord.Member, *, id: str):
      await ctx.defer(ephemeral = False)

      try:
        await ctx.message.delete()
      except:
        pass
       
      guild_info = await get_info(ctx)
      if len(id) < 24:
        em = discord.Embed(title=f"", description=f"Please input a valid ID.", color=discord.Color.from_rgb(255, 255, 254))
        return await ctx.send(embed=em)
      
      object_id = ObjectId(str(id))
      result = await db.strikes.find_one({'_id': object_id})
      if not result:
        em = discord.Embed(title=f"", description=f"This strike is not in our database", color=discord.Color.from_rgb(255, 255, 254))
        return await ctx.send(embed=em)
      else:
        await db.strikes.delete_one({'_id': object_id})

      await ctx.send(f"`{id}` has been deleted!")

  
  @delete_strike.error
  async def delete_strike_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MessageNotFound):
      pass
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    elif isinstance(error, commands.MissingRequiredArgument):
      return await ctx.send("Please make sure you have a member than an ID of the strike. Example: `-delete strike @person 1234`")
    elif isinstance(error, commands.BadArgument):
      return await ctx.send("Please make sure you have a member than an ID of the strike. Example: `-delete strike @person 1234`")
  
  @commands.hybrid_command(description="This command will terminate a staff member.", with_app_command = True, extras={"category": "Infractions"})
  @is_management()
  async def terminate(self, ctx: commands.Context, member: discord.Member, *, reason: str):
      await ctx.defer(ephemeral=False)

      try:
          await ctx.message.delete()
      except:
          pass
        
      guild_info = await get_info(ctx)
      

      if ctx.author == member:
          return await ctx.send("You cannot terminate yourself!", delete_after=2, emphemeral=True)
      else:
          timestamp = int(time.time())
          doc = {
              'user_id': member.id,
              'term_reason': reason, 
              'moderator': ctx.author.id,
              'guild_id': ctx.guild.id
          }
          await db.terminations.insert_one(doc)
          
          em = discord.Embed(title=f"{guild_info['emoji_id']} Staff Termination", description=f"You have been terminated by the HR Team in **{ctx.guild.name}**. \n\n> **Username:** {member.mention}\n> **Reason:** {reason}\n > **Submission Date:** <t:{timestamp}:F>", color=await getColor(ctx, "demote_color"))
          await ctx.send(embed=em)
          try:
            await member.send(embed=em)
          except Exception:
            pass
      
  @search.command(description="This command will search any terminations for a staff member.", with_app_command = True, extras={"category": "Infractions"}, name="terminations")
  @is_staff()
  async def search_term(self, ctx: commands.Context, member: discord.Member):
      async def on_timeout():
        farward_button.disabled = True
        back_button.disabled = True
        await msg.edit(view=view)

      async def farwardCallBack(interaction: discord.Interaction):
          nonlocal current_page
          current_page = (current_page + 1) % total_pages
          await interaction.response.edit_message(embed=await create_termination_embed(current_page), view=view)
      
      async def backwardCallBack(interaction: discord.Interaction):
          nonlocal current_page
          current_page = (current_page - 1) % total_pages
          await interaction.response.edit_message(embed=await create_termination_embed(current_page), view=view)

      await ctx.defer(ephemeral=False)

      try:
          await ctx.message.delete()
      except:
          pass

      records_yguilds = await db.terminations.find({'guild_id': {'$exists': True}, 'user_id': member.id}).to_list(None)
      records_nguilds = await db.terminations.find({'guild_id': {'$exists': False}, 'user_id': member.id}).to_list(None)
      terminations = []

      for record in records_nguilds:
          terminations.append(record)

      for item in records_yguilds:
          key = item["guild_id"]
          if int(key) == ctx.guild.id:
              terminations.append(item)

      strike_chunks = [terminations[i:i + 6] for i in range(0, len(terminations), 6)]

      if not strike_chunks:
          return await ctx.send("No terminations are found for this user.")

      total_pages = len(strike_chunks)
      current_page = 0

      async def create_termination_embed(page_number):
          embed = discord.Embed(title=f"", color=await getColor(ctx, "commands_color"))
          embed.set_author(name=f"{member.name}'s Termination History ({len(terminations)})", icon_url=member.avatar.url)
          if not total_pages <= 1:
            embed.set_footer(text=f"Page {page_number + 1}/{total_pages}")

          for warn in strike_chunks[page_number]:
              embed.add_field(name=f"ID: {warn['_id']}", value=f"**Reason:** {warn['term_reason']}\n**Moderator:** <@{warn['moderator']}>", inline=False)

          return embed

      if not total_pages <= 1:
        view = discord.ui.View()
        farward_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.grey, emoji="<:right:1153876059490615388>")
        back_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.grey, emoji="<:Left:1153876070832033813>")
        view.add_item(back_button)
        view.add_item(farward_button)

        view.timeout = 120
        view.on_timeout = on_timeout

        farward_button.callback = farwardCallBack
        back_button.callback = backwardCallBack
        

        msg = await ctx.send(embed=await create_termination_embed(current_page), view=view)
      elif total_pages <= 1:
        msg = await ctx.send(embed=await create_termination_embed(current_page))
  
  @search_term.error
  async def search_term_error(self, ctx: commands.Context, error):
      if isinstance(error, commands.MessageNotFound):
        pass
      elif isinstance(error, commands.MissingPermissions):
        return await ctx.send("I don't have the required permissions!")
      elif isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send("Please make sure you have a member. Example: `-search terminations @person`")
      elif isinstance(error, commands.BadArgument):
        return await ctx.send("Please make sure you have a member. Example: `-search terminations @person`")
      elif isinstance(error, commands.CommandInvokeError):
        pass

  @commands.hybrid_command(description="This command is used to promote any staff members who require a promotion.", with_app_command = True, extras={"category": "Infractions"})
  @is_management()
  async def promote(self, ctx: commands.Context, member: discord.Member, role: discord.Role, *, reason: str = "None Was Specified"):
    await ctx.defer(ephemeral = False)
     
    guild_info = await get_info(ctx)

    bot_member = ctx.guild.get_member(self.bot.user.id)
    top_role = discord.utils.get(ctx.guild.roles, id=bot_member.top_role.id)

    if top_role.position <= role.position:
        return await ctx.send("I can't promote someone to a role higher than me!")
    elif ctx.author == member:
        return await ctx.send("You can't promote yourself!")
    elif ctx.author.top_role.position <= role.position:
        return await ctx.send("Please make sure your top role is higher than the one your trying to promote to!")
    elif ctx.author.top_role.position <= member.top_role.position:
        return await ctx.send("Please make sure your top role is higher than the one your trying to promote!")
    elif role in member.roles:
        return await ctx.send("This user already has this role!")
    else:
        timestamp = int(time.time())
    
        await db.promos.insert_one({
          'user_id': member.id,
          'promo_reason': reason,
          'moderator': ctx.author.id,
          'promo_role_id': role.id,
          'guild_id': ctx.guild.id
        })
        embed_info = await get_embed_info(ctx, 'promote')

        newDescription = await convertEmbed(ctx, embed_info[0], embed_info[2], embed_info[3], embed_info[5], guild_info, timestamp, "promote")

        await member.add_roles(role)
        try:
          em = discord.Embed(title=f"{newDescription[1]}", description=f"{newDescription[0]} \n\n> **Username:** {member.mention}\n> **Reason:** {reason}\n> **Role:** {role.mention}\n> **Server**: {ctx.guild.name} \n > **Submission Date:** <t:{timestamp}:F>", color=await getColor(ctx, "promote_color"))
        except Exception as e:
          raise commands.CommandInvokeError(e)
        if embed_info[4]:
          em.set_author(name=newDescription[3], icon_url=embed_info[4])

        if embed_info[3]:
          em.set_footer(text=newDescription[2])
        await ctx.send(embed=em)

        try:
            await member.send(embed=em)
        except:
            pass
        
        try:
            await ctx.message.delete()
        except:
            pass
    
  @promote.error
  async def promote_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MessageNotFound):
      pass
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    elif isinstance(error, commands.MissingRequiredArgument):
      return await ctx.send("Please make sure you have a member, role, than a reason. Example: `-promote @person @mod Good Job`")
    elif isinstance(error, commands.BadArgument):
      return await ctx.send("Please make sure you have a member, role, than a reason. Example: `-promote @person @mod Good Job`")
    elif ctx.guild.me.guild_permissions.manage_roles is False:
       return await ctx.send("I need permission to manage roles.")

  @search.command(description="This command is used to search a user's promotions.", with_app_command = True, extras={"category": "Infractions"})
  @is_staff()
  async def promotions(self, ctx: commands.Context, member: discord.Member):
    await ctx.defer(ephemeral = False)

    records_yguilds = db.promos.find({'guild_id': {'$exists': True}, 'user_id': member.id})
    records_nguilds = db.promos.find({'guild_id': {'$exists': False}, 'user_id': member.id})
    result = []
    async for record in records_nguilds:
      result.append(record)

    async for item in records_yguilds:
      key = item["guild_id"]
      if int(key) == int(ctx.guild.id):
        result.append(item)
      else:
        pass
      
    
    if not records_yguilds and not records_nguilds:
      return await ctx.send("This user has no promotions!")

    em = discord.Embed(title=f"", description=f"Current promotions for {member.name}", color=await getColor(ctx, "commands_color"))
    em.set_author(name=f"{member.name}'s Promotions", icon_url=member.avatar.url)
    counter = 0
    for warn in result:
      counter += 1
      role = discord.utils.get(ctx.guild.roles, id=int(warn['promo_role_id']))
      em.add_field(name=f"ID: {counter}", value=f"**Role:** {role.mention}\n**Reason:** {warn['promo_reason']}\n**Moderator:** <@{int(warn['moderator'])}>")
    await ctx.send(embed=em)


    try:
      await ctx.message.delete()
    except:
      pass
    return

  @promotions.error
  async def promotions(self, ctx: commands.Context, error):
    if isinstance(error, commands.MessageNotFound):
      pass
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    elif isinstance(error, commands.MissingRequiredArgument):
      return await ctx.send("Please make sure you have a member. Example: `-search_promos @person`")
    elif isinstance(error, commands.BadArgument):
      return await ctx.send("Please make sure you have a member. Example: `-search_promos @person`")



  @commands.hybrid_command(description="This command is used to demote any staff members who require a demotion.", with_app_command = True, extras={"category": "Infractions"})
  @is_management()
  async def demote(self, ctx: commands.Context, member: discord.Member, role: discord.Role, *, reason: str = "None Was Specified"):
    await ctx.defer(ephemeral = False)
     
    guild_info = await get_info(ctx)
    guild = self.bot.get_guild(ctx.guild.id)
    bot_member = guild.get_member(self.bot.user.id)
    top_role = discord.utils.get(guild.roles, id=bot_member.top_role.id)
    if top_role.position <= role.position:
        return await ctx.send("I can't promote someone to a role higher than me!")
    elif ctx.author == member:
        return await ctx.send("You can't promote yourself!")
    elif ctx.author.top_role.position <= role.position:
        return await ctx.send("Please make sure your top role is higher than the one your trying to promote to!")
    elif ctx.author.top_role.position <= member.top_role.position:
        return await ctx.send("Please make sure your top role is higher than the one your trying to promote!")
    elif role in member.roles:
        return await ctx.send("This user already has this role!")
    else:
        if role not in member.roles:
          await member.add_roles(role)
        timestamp = int(time.time())
    
        await db.demos.insert_one({
          'user_id': member.id,
          'demo_reason': reason,
          'moderator': ctx.author.id,
          'demo_role_id': role.id,
          'guild_id': ctx.guild.id
        })
        embed_info = await get_embed_info(ctx, 'demote')

        newDescription = await convertEmbed(ctx, embed_info[0], embed_info[2], embed_info[3], embed_info[5], guild_info, timestamp, "demote")

        for r in reversed(member.roles):
          if r > role:
            try:
              await member.remove_roles(r)
            except Exception:
              pass

        em = discord.Embed(title=f"{newDescription[1]}", description=f"{newDescription[0]} \n\n> **Username:** {member.mention}\n> **Reason:** {reason}\n> **Role:** {role.mention}\n> **Server**: {ctx.guild.name} \n > **Submission Date:** <t:{timestamp}:F>", color=await getColor(ctx, "demote_color"))
        if embed_info[4]:
          em.set_author(name=newDescription[3], icon_url=embed_info[4])

        if embed_info[3]:
          em.set_footer(text=newDescription[2])
        await ctx.send(embed=em)
        try:
            await member.send(embed=em)
        except:
            pass
        
        try:
            await ctx.message.delete()
        except:
            pass
        return
    
  @demote.error
  async def demote_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MessageNotFound):
      pass
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    elif isinstance(error, commands.MissingRequiredArgument):
      return await ctx.send("Please make sure you have a member, role, than a reason. Example: `-demote @person @mod Good Job`")
    elif isinstance(error, commands.BadArgument):
      return await ctx.send("Please make sure you have a member, role, than a reason. Example: `-demote @person @mod Good Job`")
    elif ctx.guild.me.guild_permissions.manage_roles is False:
       return await ctx.send("I need permission to manage roles.")

  @search.command(description="This command is used to search a user's demotions.", with_app_command = True, extras={"category": "Infractions"})
  @is_staff()
  async def demotions(self, ctx: commands.Context, member: discord.Member):
    await ctx.defer(ephemeral = False)
     
    guild_info = await get_info(ctx)
    records_yguilds = db.demos.find({'guild_id': {'$exists': True}, 'user_id': member.id})
    records_nguilds = db.demos.find({'guild_id': {'$exists': False}, 'user_id': member.id})
    result = []
    async for record in records_nguilds:
      result.append(record)

    async for item in records_yguilds:
      key = item["guild_id"]
      if int(key) == int(ctx.guild.id):
        result.append(item)
      else:
        pass
      
    
    if not records_yguilds and not records_nguilds:
      return await ctx.send("This user has no demotions!")

    em = discord.Embed(title=f"{member}", description=f"These are the users demotions", color=await getColor(ctx, "commands_color"))
    em.set_author(name=f"{member.name}'s Demotions", icon_url=member.avatar.url)
    counter = 0
    for warn in result:
      counter += 1
      role = discord.utils.get(ctx.guild.roles, id=int(warn['demo_role_id']))
      em.add_field(name=f"ID: {counter}", value=f"**Role:** {role.mention}\n**Reason:** {warn['demo_reason']}\n**Moderator:** <@{int(warn['moderator'])}>")
    await ctx.send(embed=em)

    try:
      await ctx.message.delete()
    except:
      pass
    return
  
  @demotions.error
  async def demotions_error(self, ctx: commands.Context, error):
    if isinstance(error, commands.MessageNotFound):
      pass
    elif isinstance(error, commands.MissingPermissions):
      return await ctx.send("I don't have the required permissions!")
    elif isinstance(error, commands.MissingRequiredArgument):
      return await ctx.send("Please make sure you have a member. Example: `-search_demos @person`")
    elif isinstance(error, commands.BadArgument):
      return await ctx.send("Please make sure you have a member. Example: `-search_demos @person`")
    
    
async def setup(bot):
  await bot.add_cog(infractions(bot))