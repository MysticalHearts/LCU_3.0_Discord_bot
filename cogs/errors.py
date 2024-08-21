import discord
from discord.ext import commands
from cogs.utils.checks import createUrlButton
import sentry_sdk as sdk
from discord.ext.commands import CommandNotFound
from zuid import ZUID

class errors(commands.Cog):
  def __init__ (self, bot):
      self.bot = bot

  @commands.Cog.listener()
  async def on_error(self, ctx: commands.Context, error):
    error_id = ZUID(prefix="error_", length=10)
    error_id = error_id()
    if isinstance(ctx.channel, discord.channel.DMChannel):
        return
    elif isinstance(error, CommandNotFound):
        return
    elif isinstance(error, commands.MessageNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        return
    elif isinstance(error, commands.CheckFailure):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        return
    elif isinstance(error, commands.BadArgument):
        return
    elif ctx.guild.me.guild_permissions.manage_roles is False:
        return
    elif isinstance(error, commands.CommandInvokeError):
        with sdk.push_scope() as scope:
                scope.set_tag("error_id", error_id)
                scope.level = "error"
                sdk.capture_exception(error, scope=scope)
    else:
        with sdk.push_scope() as scope:
                scope.set_tag("error_id", error_id)
                scope.level = "error"
                sdk.capture_exception(error, scope=scope)


  @commands.Cog.listener()
  async def on_command_error(self, ctx: commands.Context, error):
    error_id = ZUID(prefix="error_", length=10)
    error_id = error_id()
    if isinstance(ctx.channel, discord.channel.DMChannel):
        embed = discord.Embed(title="LCU does not support DMs.", description="You can join our [Support Server](https://discord.gg/fwafbXMZrT).")
        try:
            await ctx.send(embed=embed)
        except:
            await ctx.interaction.response.send_message(embed=embed)
    elif isinstance(error, CommandNotFound):
        return
    elif isinstance(error, commands.MessageNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        return
    elif isinstance(error, commands.CheckFailure):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        return
    elif isinstance(error, commands.BadArgument):
        return
    elif ctx.guild.me.guild_permissions.manage_roles is False:
        return
    elif isinstance(error, commands.CommandInvokeError):
        embed = discord.Embed(title="ERROR!", description=f"Command failed during running, please contact LCU Support!\n\n__**Error ID:**__ `{error_id}`", color=discord.Color.red())
        button = await createUrlButton(['https://discord.gg/u5hx6Bc2U5'], ['Join our Support Server!'])

        try:
            await ctx.channel.send(embed=embed, view=button)
        except:
            pass

        with sdk.push_scope() as scope:
                scope.set_tag("guild_id", ctx.guild.id)
                scope.set_tag("error_id", error_id)
                scope.level = "error"
                sdk.capture_exception(error, scope=scope)
    else:
        embed = discord.Embed(title="ERROR!", description=f"Something went wrong.", color=discord.Color.red())
        embed.add_field(name="Error:", value=f"||{error}||", inline=False)
        embed.add_field(name="Error ID:", value=f"`{error_id}`", inline=False)
        button = await createUrlButton(['https://discord.gg/u5hx6Bc2U5'], ['Join our Support Server!'])

        try:
            await ctx.channel.send(embed=embed, view=button)
        except:
            pass
        
        with sdk.push_scope() as scope:
                scope.set_tag("guild_id", ctx.guild.id)
                scope.set_tag("error_id", error_id)
                scope.level = "error"
                sdk.capture_exception(error, scope=scope)

           



async def setup(bot):
  await bot.add_cog(errors(bot))