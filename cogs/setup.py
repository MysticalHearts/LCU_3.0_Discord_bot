import discord
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui import View
from discord import Interaction
from cogs.utils.checks import startSetup, role_select, channel_select, get_info, complete, setup_command_check
from discord import app_commands
import asyncio


class MServerName(discord.ui.Modal, title="Setup"):
    answer = discord.ui.TextInput(label="Server Name")

    async def on_submit(self, ctx: Interaction):
        await ctx.response.defer()
        answer = str(self.answer)

        self.stop()


class MServerOwner(discord.ui.Modal, title="Setup"):
    answer = discord.ui.TextInput(label="Server Owner")

    async def on_submit(self, ctx: Interaction):
        await ctx.response.defer()
        answer = str(self.answer)

        self.stop()


class MCode(discord.ui.Modal, title="Setup"):
    answer = discord.ui.TextInput(label="ER:LC Server Code")

    async def on_submit(self, ctx: Interaction):
        await ctx.response.defer()
        answer = str(self.answer)

        self.stop()


class MReminderText(discord.ui.Modal, title="Setup"):
    answer = discord.ui.TextInput(
        label="M Command Text", style=discord.TextStyle.paragraph
    )

    async def on_submit(self, ctx: Interaction):
        await ctx.response.defer()
        answer = str(self.answer)

        self.stop()


class MVotes(discord.ui.Modal, title="Setup"):
    answer = discord.ui.TextInput(label="Votes", placeholder="Must be a number")

    async def on_submit(self, ctx: Interaction):
        await ctx.response.defer()
        answer = self.answer

        self.stop()


class MAdvert(discord.ui.Modal, title="Setup"):
    answer = discord.ui.TextInput(
        label="Advertisement", style=discord.TextStyle.paragraph
    )

    async def on_submit(self, ctx: Interaction):
        await ctx.response.defer()
        answer = str(self.answer)

        self.stop()


class MNickname(discord.ui.Modal, title="Setup"):
    answer = discord.ui.TextInput(label="LCU's nickname", style=discord.TextStyle.short)

    async def on_submit(self, ctx: Interaction):
        await ctx.response.defer()
        answer = str(self.answer)

        self.stop()


def canceled():
    return discord.Embed(
        title="Canceled",
        description="The Setup has been canceled",
        color=discord.Color.red(),
    )


class setup_dropdown(discord.ui.View):
    def __init__(self, bot, question):
        super().__init__(timeout=None)
        self.bot = bot
        self.question = question
        self.is_skipped = False
        self.is_canceled = False
        self.answer = None

    @discord.ui.select(
        placeholder="What would you like to do?",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Input",
                description="Enter a value for the current question",
                emoji="<:Input:1153867585859899402>",
            ),
            discord.SelectOption(
                label="Skip",
                description="Skip the current question",
                emoji="<:skip:1153867933517353092>",
            ),
            discord.SelectOption(
                label="Cancel",
                description="Cancel the setup of LCU",
                emoji="<:cancel:1153869169658429440>",
            ),
        ],
    )
    async def select(self, interaction: discord.Integration, select: discord.ui.Select):
        self.interaction = interaction
        if select.values[0] == "Input":
            match self.question:
                case "emoji":
                    await interaction.response.defer()
                    msg = await interaction.followup.send(
                        "Please react to this message with your custom emoji"
                    )

                    try:
                        reaction, user = await self.bot.wait_for(
                            "reaction_add",
                            timeout=600.0,
                            check=lambda reaction, user: user == interaction.user
                            and reaction.message.id == msg.id,
                        )
                        await msg.delete()
                        emoji = reaction.emoji
                        self.answer = emoji
                    except asyncio.TimeoutError:
                        await msg.delete()
                        await interaction.followup.send("You didn't react in time.")
                case "nickname":
                    modal = MNickname()
                    await interaction.response.send_modal(modal)
                    await modal.wait()
                    self.answer = str(modal.answer)
                    await interaction.guild.me.edit(nick=self.answer)
                case "server_name":
                    modal = MServerName()
                    await interaction.response.send_modal(modal)
                    await modal.wait()
                    self.answer = modal.answer
                case "server_owner":
                    modal = MServerOwner()
                    await interaction.response.send_modal(modal)
                    await modal.wait()
                    self.answer = modal.answer
                case "server_code":
                    modal = MCode()
                    await interaction.response.send_modal(modal)
                    await modal.wait()
                    self.answer = modal.answer
                case "votes":
                    modal = MVotes()
                    await interaction.response.send_modal(modal)
                    await modal.wait()
                    self.answer = modal.answer
                case "advertisement":
                    modal = MAdvert()
                    await interaction.response.send_modal(modal)
                    await modal.wait()
                    self.answer = modal.answer
            self.stop()
            self.clear_items()
        elif select.values[0] == "Skip":
            self.is_skipped = True
            match self.question:
                case "emoji":
                    self.answer = "skipped"
                case "nickname":
                    self.answer = None
                case "server_name":
                    self.answer = "server name"
                case "server_owner":
                    self.answer = "server owner"
                case "server_code":
                    self.answer = "code"
                case "votes":
                    self.answer = 5
                case "advertisement":
                    self.answer = (
                        f"**{interaction.guild.name}**\n\nPlease join our server!"
                    )
            self.stop()
            self.clear_items()
        elif select.values[0] == "Cancel":
            self.is_canceled = True

            self.stop()
            self.clear_items()


class setup_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="setup",
        description="This will setup LCU up with your own server information.",
        extras={"category": "Other"},
    )
    @setup_command_check()
    async def setup(
        self,
        interaction: discord.Interaction,
        session_banner: discord.Attachment = None,
        shutdown_banner: discord.Attachment = None,
        svote_banner: discord.Attachment = None,
    ):
        try:
            banners = {
                "session_banner": "skipped",
                "shutdown_banner": "skipped",
                "svote_banner": "skipped",
            }
            if session_banner:
                banners["session_banner"] = str(session_banner.proxy_url)
            if shutdown_banner:
                banners["shutdown_banner"] = str(shutdown_banner.proxy_url)
            if svote_banner:
                banners["svote_banner"] = str(svote_banner.proxy_url)

            embed = discord.Embed(
                title="Welcome to LCU's interactive setup!",
                description="**Please make sure you have the following before starting:**\n\n**- Staff Roles\n- Management Roles\n- Moderation Roles\n- Server Information (name/owner/code)**\n\nIf you have this information, please start the setup procedure by clicking the **Start** button below.",
                color=discord.Color(16763904),
            )

            embed.set_author(
                name="Setup",
                icon_url="https://cdn.discordapp.com/avatars/1057325266097156106/a26b452a356d746e46c23082f536cb8f.png?size=512",
            )

            view = View()
            button = discord.ui.Button(label="Start", style=discord.ButtonStyle.green)
            new_interaction = None

            async def buttonCallback(interaction: discord.Interaction):
                view.stop()
                nonlocal new_interaction
                new_interaction = interaction

            button.callback = buttonCallback
            view.add_item(button)
            await interaction.response.send_message(embed=embed, view=view)
            await view.wait()

            view = setup_dropdown(self.bot, "emoji")
            await new_interaction.response.edit_message(
                content=f"**{interaction.guild.name}'s Setup**: Please enter your server emoji.",
                embed=None,
                view=view,
            )
            await view.wait()
            emoji = view.answer
            await view.interaction.response.edit_message(view=None)
            if view.is_canceled:
                await new_interaction.edit_original_response(
                    embed=canceled(), content=None, view=None
                )
                return

            select = role_select(1, 25, interaction.user.id)
            view = View()
            view.add_item(select)
            await new_interaction.edit_original_response(
                content=f"**{interaction.guild.name}'s Setup**: Please input your moderation roles.",
                view=view
            )
            await select.view_obj.wait()
            await new_interaction.edit_original_response(view=None)
            moderation_roles = select.roles

            select1 = role_select(1, 25, interaction.user.id)
            view = View()
            view.add_item(select1)
            await select.interaction.response.edit_message(
                content=f"**{interaction.guild.name}'s Setup**: Please input your staff roles.",
                view=view,
            )
            await select1.view_obj.wait()
            await new_interaction.edit_original_response(view=None)
            staff_roles = select1.roles

            select = role_select(1, 25, interaction.user.id)
            view = View()
            view.add_item(select)
            await select1.interaction.response.edit_message(
                content=f"**{interaction.guild.name}'s Setup**: Please input your management roles.",
                view=view,
            )
            await select.view_obj.wait()
            await new_interaction.edit_original_response(view=None)
            management_roles = select.roles

            select1 = role_select(1, 1, interaction.user.id)
            view = View()
            view.add_item(select1)
            await select.interaction.response.edit_message(
                content=f"**{interaction.guild.name}'s Setup**: Please input your Session Ping role.",
                view=view,
            )
            await select1.view_obj.wait()
            await new_interaction.edit_original_response(view=None)
            ssu_ping = select1.roles

            select = channel_select(1, 1, interaction.user.id)
            view = View()
            view.add_item(select)
            await select1.interaction.response.edit_message(
                content=f"**{interaction.guild.name}'s Setup**: Please input your staff requests channel.",
                view=view,
            )
            await select.view_obj.wait()
            await new_interaction.edit_original_response(view=None)
            requests_channel = select.channels

            #nickname
            view = setup_dropdown(self.bot, "nickname")
            await select.interaction.response.edit_message(
                content=f"**{interaction.guild.name}'s Setup**: Please enter a bot nickname.",
                view=view,
            )
            await view.wait()
            try:
                await view.interaction.response.edit_message(view=None)
            except:
                pass
            if view.is_canceled:
                await new_interaction.edit_original_response(
                    embed=canceled(), content=None, view=None
                )
                return

            #server name
            view = setup_dropdown(self.bot, "server_name")
            await new_interaction.edit_original_response(
                content=f"**{interaction.guild.name}'s Setup**: Please enter your servers name.",
                view=view,
            )
            await view.wait()
            server_name = str(view.answer)
            await view.interaction.response.edit_message(view=None)
            if view.is_canceled:
                await new_interaction.edit_original_response(
                    embed=canceled(), content=None, view=None
                )
                return

            #server owner
            view = setup_dropdown(self.bot, "server_owner")
            await new_interaction.edit_original_response(
                content=f"**{interaction.guild.name}'s Setup**: Please enter your servers owner's username.",
                view=view,
            )
            await view.wait()
            server_owner = str(view.answer)
            await view.interaction.response.edit_message(view=None)
            if view.is_canceled:
                await new_interaction.edit_original_response(
                    embed=canceled(), content=None, view=None
                )
                return

            #server code
            view = setup_dropdown(self.bot, "server_code")
            await new_interaction.edit_original_response(
                content=f"**{interaction.guild.name}'s Setup**: Please enter your servers code.",
                view=view,
            )
            await view.wait()
            await view.interaction.response.edit_message(view=None)
            if view.is_canceled:
                await new_interaction.edit_original_response(
                    embed=canceled(), content=None, view=None
                )
                return
            server_code = str(view.answer)
            if " " in server_code:
                server_code = server_code.replace(" ", "")
            else:
                server_code = server_code

            #amount of votes
            while True:
                view = setup_dropdown(self.bot, "votes")
                await new_interaction.edit_original_response(
                    content=f"**{interaction.guild.name}'s Setup**: Please enter the amount of votes for you SVotes.",
                    view=view,
                )
                await view.wait()
                votes = str(view.answer)
                await view.interaction.response.edit_message(view=None)
                if view.is_canceled:
                    await new_interaction.edit_original_response(
                        embed=canceled(), content=None, view=None
                    )
                    return

                try:
                    votes = int(votes)
                    break
                except TypeError:
                    await new_interaction.channel.send(
                        "Please enter a number!", delete_after=2
                    )
                    continue
            
            #advertisement
            view = setup_dropdown(self.bot, "advertisement")
            await new_interaction.edit_original_response(
                content=f"**{interaction.guild.name}'s Setup**: Please enter your server's advertisement.",
                view=view,
            )
            await view.wait()
            advertisement = view.answer
            await view.interaction.response.edit_message(view=None)
            if view.is_canceled:
                await new_interaction.edit_original_response(
                    embed=canceled(), content=None, view=None
                )
                return

            await startSetup(
                interaction,
                banners=banners,
                emoji=emoji,
                moderation_roles=moderation_roles,
                staff_roles=staff_roles,
                management_roles=management_roles,
                ssu_ping=ssu_ping,
                requests_channel=requests_channel,
                server_name=server_name,
                server_owner=server_owner,
                server_code=server_code,
                votes=votes,
                advertisement=advertisement,
            )
        except asyncio.TimeoutError:
            return await interaction.response.send_message(
                "You didn't respond in time, please restart the setup procress!",
                ephemeral=True,
            )

    @setup.error
    async def setup_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MessageNotFound):
            pass
        elif ctx.guild.me.guild_permissions.administrator is False:
            return await ctx.send(
                "Please give me Administrator perms as I tend to work better!"
            )
        elif ctx.guild.me.guild_permissions.manage_roles is False:
            return await ctx.send("I need permission to manage roles!")
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send("I don't have the required permissions!")

    @commands.hybrid_command(
        description="This will auto setup LCU, you dont have to do anything!",
        extras={"category": "Other"},
    )
    @setup_command_check()
    async def autosetup(self, ctx: commands.Context):
        await ctx.defer()
        guild_info = await get_info(ctx)
        if guild_info:
            return await ctx.send("It looks like you already have a setup for this server!")

        await ctx.send("Starting setup...", empheral=True)
        
        emoji = await ctx.guild.create_custom_emoji(
            name="LCU",
            image="https://cdn.discordapp.com/avatars/1057325266097156106/a26b452a356d746e46c23082f536cb8f.png?size=512",
        )
        moderation_role = await ctx.guild.create_role(
            name="Moderation Team", color=discord.Color.blue()
        )
        staff_role = await ctx.guild.create_role(
            name="Staff Team", color=discord.Color.white()
        )
        management_role = await ctx.guild.create_role(
            name="Management Team", color=discord.Color.red()
        )
        ownership_role = await ctx.guild.create_role(
            name="Ownership Team", color=discord.Color.gold()
        )
        ssu_ping = await ctx.guild.create_role(
            name="SSU Ping", color=discord.Color.red()
        )
        requests_channel = await ctx.guild.create_text_channel(
            name="staff-requests", topic="Staff requests channel."
        )
        server_name = ctx.guild.name
        server_owner = ctx.guild.owner

        server_code = "https://policeroleplay.community/join/code"
        votes = 5
        advertisement = f"**{ctx.guild.name}**\n\nPlease join our server!"

        await startSetup(
            ctx,
            emoji=emoji,
            moderation_roles=[moderation_role],
            staff_roles=[staff_role],
            management_roles=[management_role, ownership_role],
            ssu_ping=[ssu_ping],
            requests_channel=requests_channel,
            server_name=server_name,
            server_owner=server_owner,
            server_code=server_code,
            votes=votes,
            advertisement=advertisement,
        )

        return await complete(ctx)


async def setup(bot):
    await bot.add_cog(setup_command(bot))
