import discord
from discord.ext import commands
import datetime
from cogs.utils.checks import (
    checkLOASetup,
    is_management,
    is_staff,
    checkManage,
    checkStaff,
)
import re
from cogs.events import db
import datetime
from datetime import datetime, timedelta
import random


class endLOA(discord.ui.Modal, title="End Leave Of Absence"):
    deny_reason = discord.ui.TextInput(
        label="Explain why you want to end the LOA",
        placeholder="e.g. you've been on an loa for to long.",
        style=discord.TextStyle.paragraph,
        required=True,
    )

    def __init__(self, bot, member, time: str, reason: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.member = member
        self.time = time
        self.reason = reason
        self.buttons_disabled = False

    async def on_submit(self, interaction: discord.Interaction):
        deny_reason_value = self.deny_reason.value
        active_loa = await db.loa.find_one(
            {"author_id": self.member.id, "guild_id": interaction.guild.id}
        )
        member = self.bot.get_user(active_loa["author_id"])

        doneembed = discord.Embed(
            title="Successfully Ended!",
            description=f"I've successfully ended ``{member}``'s **Leave Of Absence** for ``{deny_reason_value}``!",
        )
        await interaction.response.send_message(embed=doneembed, ephemeral=True)
        dmembed2 = discord.Embed(
            title="Leave Of Absence Ended",
            description=f"Your LOA has been ended in {interaction.guild.name} for {deny_reason_value}",
        )
        await member.send(embed=dmembed2)
        channel_query = await db.settings.find_one(
            {"guild_id": interaction.guild.id}, {"loa_channel": 1}
        )
        channel = interaction.guild.get_channel(int(channel_query["loa_channel"]))
        channelembed = discord.Embed(
            title="Leave Of Absence Manually Ended",
            description=f"  **Staff Member:** {member.mention}\n  **Started:** {discord.utils.format_dt(active_loa['start_date'])}\n  **Ended:** {discord.utils.format_dt(active_loa['end_date'])}\n  **Reason:** ``{active_loa['reason']}``",
            color=0xC40505,
        )

        if not member.avatar.url:
            channelembed.set_author(
                icon_url=member.default_avatar.url, name=f"{member.name}"
            )
        else:
            channelembed.set_author(icon_url=member.avatar.url, name=f"{member.name}")
        await channel.send(embed=channelembed)
        await db.loa_list.insert_one(
            {
                "_id": active_loa["_id"],
                "start_date": active_loa["start_date"],
                "end_date": active_loa["end_date"],
                "guild_id": interaction.guild.id,
                "user_id": active_loa["author_id"],
            }
        )
        await db.loa.delete_one(active_loa)
        role = await db.settings.find_one({"guild_id": interaction.guild_id})
        if role is not None:
            loa_role = interaction.guild.get_role(role["loa_role"])
            await interaction.user.remove_roles(loa_role)
        else:
            pass


class deny(discord.ui.Modal, title="Deny"):
    deny_reason = discord.ui.TextInput(
        label="Explain the reason for the denial",
        placeholder="e.g. ewetwetwet",
        style=discord.TextStyle.paragraph,
        required=True,
    )

    def __init__(self, bot, orgAuthor, time: str, reason: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.orgAuthor = orgAuthor
        self.time = time
        self.reason = reason
        self.buttons_disabled = False

    async def on_submit(self, interaction: discord.Interaction):
        if self.buttons_disabled:
            return

        deny_reason_value = self.deny_reason.value

        doneembed = discord.Embed(
            title="Successfully Denied!",
            description=f"I've successfully denied ``{self.orgAuthor.name}`` for ``{deny_reason_value}``!",
        )
        await interaction.response.send_message(embed=doneembed, ephemeral=True)
        dmembed2 = discord.Embed(
            title="Leave Of Absence Denied",
            description=f"Your LOA has been denied in {interaction.guild.name} for {deny_reason_value}",
        )
        await self.orgAuthor.send(embed=dmembed2)
        channel_query = await db.settings.find_one(
            {"guild_id": interaction.guild.id}, {"loa_channel": 1}
        )
        channel = interaction.guild.get_channel(int(channel_query["loa_channel"]))
        channelembed = discord.Embed(
            title="Leave Of Absence Denied",
            description=f"**Leave Of Absence Reason:** {self.reason}\n **Denial Reason:** {deny_reason_value}",
        )
        await channel.send(embed=channelembed)


class AcceptDenyButton(discord.ui.View):
    def __init__(self, bot, member, time, id):
        super().__init__()

        self.bot = bot
        self.member = member
        self.time = time
        self.id = id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.defer()
        await db.loa.update_one({"_id": self.id}, {"$set": {"end_date": self.time}})
        extendedembed = discord.Embed(
            title="LOA Extension Approved",
            description=f"The request to extend the Leave Of Absence for {self.member.mention} has been approved.",
            colour=0x57F288,
        )
        await interaction.followup.send(embed=extendedembed)

        em = discord.Embed(
            title=f"Your LOA extention has been accepted in {interaction.guild.name}"
        )
        await self.member.send(embed=em)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        deniedembed = discord.Embed(
            title="LOA Extension Denied",
            description=f"The request to extend the Leave Of Absence for {self.member.mention} has been denied.",
            colour=0xFF5733,
        )
        await interaction.followup.send(embed=deniedembed)
        em = discord.Embed(
            title=f"Your LOA extention has been denied in {interaction.guild.name}"
        )
        await self.member.send(embed=em)


class addTime(discord.ui.Modal, title="LOA Extend"):
    time_input = discord.ui.TextInput(
        label="How much time do you want to add?",
        placeholder="e.g. 2w, 4h, or 5d",
        style=discord.TextStyle.short,
    )

    def __init__(self, bot, member, author, time: str, reason: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.time = time
        self.member = member
        self.author = author
        self.reason = reason

    async def on_submit(self, interaction: discord.Interaction):
        time_input_value = self.time_input.value
        match = re.match(
            r"(?:(\d+)y)?(?:(\d+)m)?(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?", time_input_value
        )
        if not match:
            await interaction.response.send_message(
                "Invalid time format. Use '1y2m3w4d5h' for a combination of years, months, weeks, days, and hours."
            )
            return

        years, months, weeks, days, hours = map(int, match.groups(default="0"))

        active_loa = await db.loa.find_one(
            {"author_id": self.member.id, "guild_id": interaction.guild.id}
        )

        if active_loa:
            if self.member == self.author:  # If managing your own LOA
                time_delta = timedelta(
                    days=years * 365 + months * 30 + weeks * 7 + days, hours=hours
                )
                new_end_date = active_loa["end_date"] + time_delta
                end_date = new_end_date

                extendedembed = discord.Embed(
                    title="LOA Extention",
                    description=f"Successfully sent an extention request. The LOA will end at {discord.utils.format_dt(new_end_date)}",
                )
                await interaction.response.send_message(
                    embed=extendedembed, ephemeral=True
                )

                channel_query = await db.settings.find_one(
                    {"guild_id": interaction.guild.id}, {"loa_channel": 1}
                )
                channel = interaction.guild.get_channel(
                    int(channel_query["loa_channel"])
                )

                requestembed = discord.Embed(
                    title=f"LOA Extension Request",
                    description=f"**Member:** {self.member.mention}\n**Requested by:** {interaction.user.mention}\n**New End Date:** {discord.utils.format_dt(new_end_date)}\n**Reason:** {self.reason}",
                    colour=0x57F288,
                )
                view = AcceptDenyButton(
                    self.bot, self.member, end_date, active_loa["_id"]
                )
                await channel.send(embed=requestembed, view=view)
            else:  # If managing someone else's LOA
                time_delta = timedelta(
                    days=years * 365 + months * 30 + weeks * 7 + days, hours=hours
                )
                new_end_date = active_loa["end_date"] + time_delta

                await db.loa.update_one(
                    {"_id": active_loa["_id"]}, {"$set": {"end_date": new_end_date}}
                )
                extendedembed = discord.Embed(
                    title="LOA Extended",
                    description=f"Successfully extended the Leave Of Absence to {years}y{months}m{weeks}w{days}d{hours}h. This will now end {discord.utils.format_dt(new_end_date)}",
                )
                await interaction.response.send_message(
                    embed=extendedembed, ephemeral=True
                )

                acceptdmembed = discord.Embed(title="You've received a leave extension")
                await self.member.send(embed=acceptdmembed)
        else:
            await interaction.response.send_message("You do not have an active LOA.")


class CreateLoa(discord.ui.Modal, title="LOA Create"):
    time_input = discord.ui.TextInput(
        label="How much time do you want to give?",
        placeholder="e.g. 2w, 4h, or 5d",
        style=discord.TextStyle.short,
    )
    loareason = discord.ui.TextInput(
        label="What is the reason?",
        placeholder="e.g. ewetwet",
        style=discord.TextStyle.long,
    )

    def __init__(self, bot, member, time: str, reason: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.time = time
        self.member = member
        self.reason = reason

    async def on_submit(self, interaction: discord.Interaction):
        find_loa = await db.loa.find_one(
            {"author_id": self.member.id, "guild_id": interaction.guild.id}
        )
        time_input_value = self.time_input.value
        match = re.match(r"(\d+)([hdw])", time_input_value)
        if not match:
            await interaction.response.send_message(
                "Invalid time format. Use '4h' for hours, '3d' for days, or '1w' for weeks."
            )
            return
        value, unit = match.groups()
        value = int(value)
        start_date = datetime.datetime.now()
        end_date = start_date
        if unit == "h":
            end_date += timedelta(hours=value)
        elif unit == "d":
            end_date += timedelta(days=value)
        elif unit == "w":
            end_date += timedelta(weeks=value)

        loa_id = "".join([str(random.randint(0, 9)) for _ in range(10)])
        post = {
            "author_id": self.member.id,  # Convert to string
            "guild_id": interaction.guild.id,  # Convert to string
            "start_date": start_date,
            "end_date": end_date,
            "loa_id": loa_id,
            "days": f"{value}{unit}",
            "reason": self.loareason.value,
        }
        await db.loa.insert_one(post)
        embed = discord.Embed(
            title="LOA Set",
            description=f"Successfully create a Leave Of Absence. The will end {discord.utils.format_dt(end_date)}",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        member = self.bot.get_user(self.member.id)
        acceptdmembed = discord.Embed(
            title="Your LOA has been set",
            description=f"Your LOA has been set in {interaction.guild.name} for {value}{unit}.\n\n**Reason:** {self.loareason.value}",
        )
        await member.send(embed=acceptdmembed)

        channel_query = await db.settings.find_one(
            {"guild_id": interaction.guild.id}, {"loa_channel": 1}
        )
        channel = interaction.guild.get_channel(int(channel_query["loa_channel"]))
        channelembed = discord.Embed(
            title=f"Leave Of Absence Set",
            description=f"  **Approved By:** {interaction.user.mention}\n  **Start:** {discord.utils.format_dt(start_date)}\n  **End:** {discord.utils.format_dt(end_date)}\n  **Leave Of Absence ID:** ``{loa_id}``\n  **Reason:** ``{self.reason}``",
            colour=0x57F288,
        )
        await channel.send(embed=channelembed)


class setLoa(discord.ui.View):
    def __init__(self, bot, member, time: str, reason: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.time = time
        self.member = member
        self.reason = reason
        self.incorrectPanel = discord.Embed(title="This is not your panel")

    @discord.ui.button(label="Set LOA", style=discord.ButtonStyle.green)
    @is_management()
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            CreateLoa(self.bot, self.member, self.time, self.reason)
        )


class extendEndButton(discord.ui.View):
    def __init__(self, bot, member, author, time: str, reason: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.time = time
        self.member = member
        self.author = author
        self.reason = reason
        self.incorrectPanel = discord.Embed(title="This is not your panel")

    @discord.ui.button(label="Extend", style=discord.ButtonStyle.green)
    @is_management()
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        loa_extend_modal = addTime(
            self.bot, self.member, self.author, self.time, self.reason
        )
        await interaction.response.send_modal(loa_extend_modal)

    @discord.ui.button(label="End", style=discord.ButtonStyle.red)
    @is_management()
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        find_loa = await db.loa.find_one(
            {"author_id": self.member.id, "guild_id": interaction.guild.id}
        )
        loa_end_modal = endLOA(self.bot, self.member, self.time, self.reason)
        await interaction.response.send_modal(loa_end_modal)


class acceptDenyButton(discord.ui.View):
    def __init__(self, bot, orgAuthor, time: str, reason: str):
        super().__init__(timeout=None)
        self.orgAuthor = orgAuthor
        self.bot = bot
        self.time = time
        self.reason = reason
        self.incorrectPanel = discord.Embed(title="This is not your panel")

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    @is_management()
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        record = await db.loa.find_one(
            {"author_id": self.orgAuthor.id, "guild_id": interaction.guild.id}
        )
        if record:
            return await interaction.response.send_message(
                "You have an ongoing LOA! End it to start a new one!"
            )

        start_date = datetime.now()
        end_date = start_date

        match = re.match(
            r"(?:(\d+)y)?(?:(\d+)m)?(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?", self.time
        )
        if match:
            years, months, weeks, days, hours = map(int, match.groups(default="0"))
            end_date += timedelta(
                days=years * 365 + months * 30 + weeks * 7 + days, hours=hours
            )

        loa_id = "".join([str(random.randint(0, 9)) for _ in range(10)])
        member = self.bot.get_user(self.orgAuthor.id)
        acceptembed = discord.Embed(
            title=f"Leave Of Absence Approved",
            description=f"**Approved By:** {interaction.user.mention}\n**Start:** {discord.utils.format_dt(start_date)}\n**End:** {discord.utils.format_dt(end_date)}\n**Leave Of Absence ID:** ``{loa_id}``\n  **Reason:** ``{self.reason}``",
            colour=discord.Color.green(),
        )
        if not member.avatar.url:
            acceptembed.set_author(
                icon_url=member.default_avatar.url, name=f"{member.name}"
            )
        else:
            acceptembed.set_author(icon_url=member.avatar.url, name=f"{member.name}")

        self.accept.disabled = True
        self.deny.disabled = True

        await interaction.response.edit_message(embed=acceptembed, view=self)

        post = {
            "author_id": self.orgAuthor.id,
            "guild_id": interaction.guild.id,
            "start_date": start_date,
            "end_date": end_date,
            "loa_id": loa_id,
            "days": self.time,
            "reason": self.reason,
        }
        await db.loa.insert_one(post)

        role_query = await db.settings.find_one(
            {"guild_id": interaction.guild.id}, {"loa_role": 1}
        )
        if role_query is not None:
            role = interaction.guild.get_role(int(role_query["loa_role"]))
            await self.orgAuthor.add_roles(role)
            acceptdmembed = discord.Embed(
                title=f"Your LOA has been accepted in {interaction.guild.name}"
            )
            await self.orgAuthor.send(embed=acceptdmembed)
        else:
            acceptdmembed = discord.Embed(
                title=f"Your LOA has been accepted in {interaction.guild.name}"
            )
            await self.orgAuthor.send(embed=acceptdmembed)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        loa_deny_modal = deny(self.bot, self.orgAuthor, self.time, self.reason)

        self.accept.disabled = True
        self.deny.disabled = True
        member = self.bot.get_user(self.orgAuthor.id)
        start_date = datetime.now()
        end_date = start_date

        match = re.match(
            r"(?:(\d+)y)?(?:(\d+)m)?(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?", self.time
        )
        if match:
            years, months, weeks, days, hours = map(int, match.groups(default="0"))
            end_date += timedelta(
                days=years * 365 + months * 30 + weeks * 7 + days, hours=hours
            )

        loa_id = "".join([str(random.randint(0, 9)) for _ in range(10)])
        denyembed = discord.Embed(
            title=f"Leave Of Absence Denied",
            description=f"**Denied By:** {interaction.user.mention}\n**Start:** {discord.utils.format_dt(start_date)}\n**End:** {discord.utils.format_dt(end_date)}\n**Leave Of Absence ID:** ``{loa_id}``\n  **Reason:** ``{self.reason}``",
            colour=discord.Color.red(),
        )
        if not member.avatar.url:
            denyembed.set_author(
                icon_url=member.default_avatar.url, name=f"{member.name}"
            )
        else:
            denyembed.set_author(icon_url=member.avatar.url, name=f"{member.name}")

        await interaction.response.send_modal(loa_deny_modal)
        await interaction.edit_original_response(embed=denyembed, view=self)


class loa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        name="loa", description="Create a loa", invoke_without_sub_command=False
    )
    async def loa(self, ctx):
        await ctx.send("Please provide what your managing")

    @loa.command(description="Request an LOA to get time off.")
    @is_staff()
    async def request(self, ctx: commands.Context, time: str, reason: str):
        if not re.match(
            r"^(?:(\d+)y)?(?:(\d+)m)?(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?$", time
        ):
            return await ctx.send(
                "Please use the correct time format: <number>y<number>m<number>w<number>d<number>h"
            )

        if await checkLOASetup(ctx) == 0:
            return await ctx.send(
                "The LOA Module is not enabled. Enable it in the settings menu."
            )

        record = await db.loa.find_one(
            {"author_id": ctx.author.id, "guild_id": ctx.guild.id}
        )
        if record:
            return await ctx.send("You have an ongoing LOA! End it to start a new one!")

        records = await db.settings.find_one(
            {"guild_id": ctx.guild.id}, {"loa_min": 1, "loa_max": 1}
        )

        def extract_time_values(time_string):
            search = re.match(
                r"^(?:(\d+)y)?(?:(\d+)m)?(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?$",
                time_string,
            )
            if search is None or search.group() == "":
                return 0, 0, 0, 0, 0
            return map(int, search.groups(default="0"))

        years, months, weeks, days, hours = extract_time_values(time)
        total_days = years * 365 + months * 30 + weeks * 7 + days

        loa_min = records.get("loa_min", "0d")
        loa_max = records.get("loa_max", "0d")

        min_years, min_months, min_weeks, min_days, min_hours = extract_time_values(
            loa_min
        )
        max_years, max_months, max_weeks, max_days, max_hours = extract_time_values(
            loa_max
        )

        min_total_days = min_years * 365 + min_months * 30 + min_weeks * 7 + min_days
        max_total_days = max_years * 365 + max_months * 30 + max_weeks * 7 + max_days

        min_total_hours = min_total_days * 24 + min_hours
        max_total_hours = max_total_days * 24 + max_hours

        if total_days < min_total_days:
            return await ctx.send("LOA time does not meet the minimum LOA time.")
        elif total_days > max_total_days:
            return await ctx.send("LOA time exceeds the maximum LOA time.")

        channel_query = await db.settings.find_one(
            {"guild_id": ctx.guild.id}, {"loa_channel": 1}
        )
        channel = ctx.guild.get_channel(int(channel_query["loa_channel"]))
        await ctx.send("I've sent a request for an LOA", delete_after=3)

        start_date = datetime.now()
        end_date = start_date + timedelta(days=total_days, hours=hours)

        channelembed = discord.Embed(
            title="Leave Of Absence Request",
            description="",
            colour=discord.Color.yellow(),
        )
        channelembed.add_field(
            name="Information",
            value=f"**Member:** {ctx.author.mention}\n**Start:** {discord.utils.format_dt(start_date)}\n**End:** {discord.utils.format_dt(end_date)}\n**Reason:** ``{reason}``\n**Time:** ``{time}``",
        )

        if not ctx.author.avatar.url:
            channelembed.set_author(
                icon_url=ctx.author.default_avatar.url, name=f"{ctx.author.name}"
            )
        else:
            channelembed.set_author(
                icon_url=ctx.author.avatar.url, name=f"{ctx.author.name}"
            )
        view = acceptDenyButton(self.bot, ctx.author, str(time), reason)
        await channel.send(embed=channelembed, view=view)

    @loa.command(description="Get a list of all the active LOA's in the server.")
    @is_staff()
    async def active(self, ctx: commands.Context):
        if await checkLOASetup(ctx) == 0:
            return await ctx.send(
                "The LOA Module is not enabled. Enable it in the settings menu."
            )

        async def on_timeout():
            farward_button.disabled = True
            back_button.disabled = True
            await msg.edit(view=view)

        async def farwardCallBack(interaction: discord.Interaction):
            if ctx.author.id != interaction.user.id:
                embed = discord.Embed(
                    description=f"You are not the user than ran this command!",
                    color=discord.Color.dark_embed(),
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
            nonlocal current_page
            current_page = (current_page + 1) % total_pages
            await interaction.response.edit_message(
                embed=await active_loa_embed(current_page), view=view
            )

        async def backwardCallBack(interaction: discord.Interaction):
            if ctx.author.id != interaction.user.id:
                embed = discord.Embed(
                    description=f"You are not the user than ran this command!",
                    color=discord.Color.dark_embed(),
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )

            nonlocal current_page
            current_page = (current_page - 1) % total_pages
            await interaction.response.edit_message(
                embed=await active_loa_embed(current_page), view=view
            )

        await ctx.defer(ephemeral=False)

        cursor = db.loa.find({"guild_id": ctx.guild.id})
        loa_results = await cursor.to_list(length=None)  # Retrieve documents as a list

        if not loa_results:
            await ctx.send("There are currently no active loas!")
            return

        loa_chunks = [loa_results[i : i + 6] for i in range(0, len(loa_results), 6)]
        total_pages = len(loa_chunks)
        current_page = 0

        async def active_loa_embed(page_number):
            embed = discord.Embed(
                title=f"Active Leave Of Absences",
                description="",
                colour=discord.Color.green(),
            )
            if not ctx.author.avatar.url:
                embed.set_author(
                    icon_url=ctx.author.default_avatar.url, name=f"{ctx.author.name}"
                )
            else:
                embed.set_author(
                    icon_url=ctx.author.avatar.url, name=f"{ctx.author.name}"
                )
            if not total_pages <= 1:
                embed.set_footer(text=f"Page {page_number + 1}/{total_pages}")
            loa_log_number = 0
            for loa in loa_chunks[page_number]:
                loa_log_number += 1
                member = self.bot.get_user(loa["author_id"])
                embed.add_field(
                    name=f"Leave {loa_log_number}",
                    value=f'{member.mention}\n> **Started:** {discord.utils.format_dt(loa["start_date"])}\n> **Ending:** {discord.utils.format_dt(loa["end_date"])}\n> **Reason** ``{loa["reason"]}``',
                    inline=False,
                )

            return embed

        if not total_pages <= 1:
            view = discord.ui.View()
            farward_button = discord.ui.Button(
                label="Next",
                style=discord.ButtonStyle.grey,
                emoji="<:LCUNext:1155282083745382440>",
            )
            back_button = discord.ui.Button(
                label="Previous",
                style=discord.ButtonStyle.grey,
                emoji="<:LCUBack:1155281607280828446>",
            )
            view.add_item(back_button)
            view.add_item(farward_button)

            view.timeout = 120
            view.on_timeout = on_timeout

            farward_button.callback = farwardCallBack
            back_button.callback = backwardCallBack

            msg = await ctx.send(embed=await active_loa_embed(current_page), view=view)
        elif total_pages <= 1:
            msg = await ctx.send(embed=await active_loa_embed(current_page))

    @loa.command(description="Manage a staff members LOA.")
    @is_staff()
    async def manage(self, ctx: commands.Context, member: discord.Member = None):
        if await checkLOASetup(ctx) == 0:
            return await ctx.send(
                "The LOA Module is not enabled. Enable it in the settings menu."
            )

        if member:
            if member.id == ctx.author.id:
                pass
            elif await checkStaff(ctx) and not await checkManage(ctx):
                return await ctx.send(
                    "You cannot manage another persons LOA if your not management!"
                )
        elif not member:
            member = ctx.author

        cursor = db.loa.find({"author_id": member.id, "guild_id": ctx.guild.id})
        loa_stats = await cursor.to_list(length=None)

        if loa_stats:
            embed = discord.Embed(title="Leave Of Absence Admin Panel", description="")

            if loa_stats:
                find_loa = loa_stats[-1]
                embed.add_field(
                    name="Current Leave Of Absence",
                    value=f'  **Started:** {discord.utils.format_dt(find_loa["start_date"])}\n  **Ending:** {discord.utils.format_dt(find_loa["end_date"])}\n  **Reason:** ``{find_loa["reason"]}``\n  **Leave Of Absence ID:** ``{find_loa["loa_id"]}``',
                )

            message = "\n".join(
                [
                    f"{discord.utils.format_dt(loa['start_date'])} - {discord.utils.format_dt(loa['end_date'])}"
                    for loa in loa_stats
                ]
            )
            embed.add_field(
                name="Previous Leave Of Absences", value=message, inline=False
            )

            if not member.avatar.url:
                embed.set_author(
                    icon_url=member.default_avatar.url, name=f"{member.name}"
                )
            else:
                embed.set_author(icon_url=member.avatar.url, name=f"{member.name}")
            await ctx.send(
                embed=embed,
                view=extendEndButton(self.bot, member, ctx.author, int, str),
            )
        else:
            await ctx.send("This user does not have any LOA records.")


async def setup(bot):
    await bot.add_cog(loa(bot))
