import discord
from discord.ext import commands
import time
from cogs.utils.checks import (
    get_info,
    get_discord_color,
    createUrlButton,
    getColor,
    convertEmbed,
    get_embed_info,
    is_management,
    make_custom_embed
)
from cogs.events import db


class session(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(with_app_command=True, extras={"category": "Group"})
    async def session(self, ctx: commands.Context):
        return

    @session.command(
        description="This command sends the Server Start Up message.",
        with_app_command=True,
        extras={"category": "Session Commands"},
    )
    @is_management()
    async def startup(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False)

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        guild_info = await get_info(ctx)
        timestamp = int(time.time())

        em = await make_custom_embed(ctx, "session", timestamp, guild_info)

        result = await db.settings.find_one(
            {"guild_id": int(ctx.guild.id)}, {"session_link": 1}
        )

        view = await createUrlButton([result["session_link"]], ["Click to Join"])
        if view == "0x1":
            return

        member = guild_info["session_role_id"]
        try:
            if member[0] == "[" and member[0] == "]":
                member = member[1:-1]
            else:
                pass
        except Exception:
            pass

        role = discord.utils.get(ctx.guild.roles, id=int(member))
        if not role or not role.mention:
            return await ctx.send("It looks like I either can't mention your session role or you have deleted it.")
        
        await ctx.send("Message Sent Successfuly!", delete_after=1, ephemeral=True)
        await ctx.send(
            content=f"{role.mention}",
            embed=em,
            view=view,
            allowed_mentions=discord.AllowedMentions(
                roles=True, users=True, replied_user=True
            ),
        )

    @startup.error
    async def startup_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MessageNotFound):
            return await ctx.send("Please retry this command, message not found.")
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send("I don't have the required permissions!")

    @session.command(
        description="This command sends the Server Shutdown message.",
        with_app_command=True,
        extras={"category": "Session Commands"},
    )
    @is_management()
    async def shutdown(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False)

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        timestamp = int(time.time())
        guild_info = await get_info(ctx)

        em = await make_custom_embed(ctx, "shutdown", timestamp, guild_info)

        await ctx.send("Message Sent Successfuly!", delete_after=1, ephemeral=True)
        await ctx.channel.send(
            embed=em,
            allowed_mentions=discord.AllowedMentions(
                roles=True, users=True, replied_user=True
            ),
        )

    @shutdown.error
    async def shutdown_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MessageNotFound):
            return await ctx.send("Please retry this command, message not found.")
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send("I don't have the required permissions!")

    @session.command(
        description="This command sends the Session Cancel message.",
        with_app_command=True,
        extras={"category": "Session Commands"},
    )
    @is_management()
    async def vcancel(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False)
        deleted = False
        guild_info = await get_info(ctx)

        records = await db.embeds.find_one(
            {"guild_id": int(ctx.guild.id)},
            {"shutdown_description": 1, "shutdown_color": 1, "svote_title": 1},
        )

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        async for message in ctx.channel.history(limit=50):
            if message.author.id == self.bot.user.id:
                if len(message.embeds) > 0:
                    if message.embeds[0].title == records["svote_title"]:
                        deleted = True

                        color = await get_discord_color(records["shutdown_color"])

                        em = discord.Embed(
                            title=f"{ctx.guild.name} Session Canceled",
                            description=f"The session poll has been canceled by {ctx.author.mention}. Let's try again next time!\n\n**Timestamp:** <t:{int(time.time())}:F>",
                            color=color,
                        )
                        if (
                            guild_info["shutdown_banner_link"] == "skipped"
                            or guild_info["shutdown_banner_link"] == None
                        ):
                            pass
                        else:
                            try:
                                em.set_image(
                                    url=f"{guild_info['shutdown_banner_link']}"
                                )
                            except discord.HTTPException:
                                await ctx.send(
                                    f"It looks like your banner link is invalid. Please change it in `-config` so I can display it! It's currently `{guild_info['session_banner_link']}`."
                                )
                        await message.edit(embed=em, view=None)
                        break

        if not deleted:
            return await ctx.send("Please make sure to start a SVote before running this command!", delete_after=4, ephemeral=True)
        elif deleted:
            await ctx.send("Message Sent Successfuly!", delete_after=1, ephemeral=True)

    @session.command(
        description="This command sends the Server Restart message.",
        with_app_command=True,
        extras={"category": "Session Commands"},
    )
    @is_management()
    async def restart(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False)

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        guild_info = await get_info(ctx)
        timestamp = int(time.time())

        records = await db.settings.find_one(
            {"guild_id": int(ctx.guild.id)}, {"session_link": 1}
        )

        if guild_info['emoji_id'] == "skipped":
            emoji = ""
        else:
            emoji = guild_info['emoji_id']

        em = discord.Embed(
            title=f"{ctx.guild.name} Session Restart",
            description=f"{emoji} Our ingame server is restarting due to difficulties. Please rejoin using the link below!\n\nTimestamp: <t:{timestamp}:F>",
            color=await getColor(ctx, "commands_color"),
        )

        view = await createUrlButton([records["session_link"]], ["Click to Join"])
        if view == "0x1":
            return

        member = guild_info["session_role_id"]
        try:
            if member[0] == "[" and member[0] == "]":
                member = member[1:-1]
            else:
                pass
        except Exception:
            pass

        role = discord.utils.get(ctx.guild.roles, id=int(member))
        await ctx.send("Message Sent Successfuly!", delete_after=1, ephemeral=True)
        if not role or not role.mention:
            return await ctx.send("It looks like I either can't mention your session role or you have deleted it.")
        await ctx.send(
            content=f"{role.mention}",
            embed=em,
            view=view,
            allowed_mentions=discord.AllowedMentions(
                roles=True, users=True, replied_user=True
            ),
        )

    @session.command(
        description="This command sends the Server Full message.",
        with_app_command=True,
        extras={"category": "Session Commands"},
    )
    @is_management()
    async def full(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False)

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        guild_info = await get_info(ctx)
        color = await getColor(ctx, "commands_color")
        timestamp = int(time.time())

        if guild_info['emoji_id'] == "skipped":
            emoji = ""
        else:
            emoji = guild_info['emoji_id']

        em = discord.Embed(
            title=f"{ctx.guild.name} Server Full",
            description=f"{emoji} Our in-game server is full! Thank you all for some amazing roleplays, please remember spots will still open up. Click the button to join.\n\nTimestamp: <t:{timestamp}:F>",
            color=color,
        )

        records = await db.settings.find_one(
            {"guild_id": int(ctx.guild.id)}, {"session_link": 1}
        )

        view = await createUrlButton([records["session_link"]], ["Click to Join"])
        if view == "0x1":
            return

        await ctx.send("Message Sent Successfuly!", delete_after=1, ephemeral=True)
        await ctx.send(embed=em, view=view)
    
    @session.command(
        description="This command sends the Server Full message.",
        with_app_command=True,
        extras={"category": "Session Commands"},
    )
    @is_management()
    async def reminder(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False)

        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

        guild_info = await get_info(ctx)
        color = await getColor(ctx, "commands_color")
        timestamp = int(time.time())

        if guild_info['emoji_id'] == "skipped":
            emoji = ""
        else:
            emoji = guild_info['emoji_id']

        em = discord.Embed(
            title=f"{ctx.guild.name} Session Reminder",
            description=f"{emoji} Please remember that a session is still on going! Feel free to join.\n\nTimestamp: <t:{timestamp}:F>",
            color=color,
        )

        records = await db.settings.find_one(
            {"guild_id": int(ctx.guild.id)}, {"session_link": 1}
        )

        view = await createUrlButton([records["session_link"]], ["Click to Join"])
        if view == "0x1":
            return

        await ctx.send("Message Sent Successfuly!", delete_after=1, ephemeral=True)
        await ctx.send(embed=em, view=view)


async def setup(bot):
    await bot.add_cog(session(bot))
