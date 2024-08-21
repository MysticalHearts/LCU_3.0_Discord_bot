import discord
from discord.ext import commands
from discord import Interaction
import re
from cogs.events import db


class SettingsPanel(discord.ui.View):
    def __init__(self, ctx, bot, pages, cur_page, contents, type):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.bot = bot
        self.pages = pages
        self.cur_page = cur_page
        self.contents = contents
        self.type = type

    @discord.ui.button(
        label="Previous",
        style=discord.ButtonStyle.grey,
        emoji="<:Left:1153876070832033813>",
    )
    async def back(self, ctx: Interaction, button: discord.ui.Button):
        if not ctx.user.id == self.ctx.author.id and ctx.channel.id == ctx.channel.id:
            return await ctx.response.send_message(
                "You are not the user who requested the LOA!", ephemeral=True
            )

        try:
            records = await db.embeds.find_one(
                {"guild_id": int(ctx.guild.id)}, {"commands_color": 1}
            )
            res = records["commands_color"]
            color2 = ",".join(res)
            color2 = color2.replace("(", "").replace(")", "")
            color_list = re.split(r",\s?", color2)
            color = discord.Color.from_rgb(
                int(color_list[0]), int(color_list[1]), int(color_list[2])
            )
        except:
            color = discord.Color.blue()
        super().__init__(timeout=None)
        if self.cur_page == 1:
            self.cur_page = 5
            e = discord.Embed(
                title=f"{list(self.contents.keys())[self.cur_page-1]}",
                color=discord.Color.blue(),
            )
            e.set_image(url=list(self.contents.values())[self.cur_page - 1])
            e.set_footer(text=f"Banner {self.cur_page}/{self.pages}")

        else:
            self.cur_page -= 1
            e = discord.Embed(
                title=f"{list(self.contents.keys())[self.cur_page-1]}",
                color=discord.Color.blue(),
            )
            e.set_image(url=list(self.contents.values())[self.cur_page - 1])
            e.set_footer(text=f"Banner {self.cur_page}/{self.pages}")

            return await ctx.response.edit_message(embed=e)

    @discord.ui.button(
        label="Next",
        style=discord.ButtonStyle.grey,
        emoji="<:right:1153876059490615388>",
    )
    async def next(self, ctx: Interaction, button: discord.ui.Button):
        if not ctx.user.id == self.ctx.author.id and ctx.channel.id == ctx.channel.id:
            return await ctx.response.send_message(
                "You are not the user who requested the LOA!", ephemeral=True
            )
        try:
            records = await db.embeds.find_one(
                {"guild_id": int(ctx.guild.id)}, {"commands_color": 1}
            )
            res = records["commands_color"]

            color2 = ",".join(res)
            color2 = color2.replace("(", "").replace(")", "")
            color_list = re.split(r",\s?", color2)
            color = discord.Color.from_rgb(
                int(color_list[0]), int(color_list[1]), int(color_list[2])
            )
        except:
            color = discord.Color.blue()
        if self.cur_page >= self.pages:
            self.cur_page = 1
            e = discord.Embed(
                title=f"{list(self.contents.keys())[self.cur_page-1]}",
                color=discord.Color.blue(),
            )
            e.set_image(url=list(self.contents.values())[self.cur_page - 1])
            e.set_footer(text=f"Banner {self.cur_page}/{self.pages}")
            return await ctx.response.edit_message(embed=e)
        else:
            self.cur_page += 1
            e = discord.Embed(
                title=f"{list(self.contents.keys())[self.cur_page-1]}",
                color=discord.Color.blue(),
            )
            e.set_image(url=list(self.contents.values())[self.cur_page - 1])
            e.set_footer(text=f"Banner {self.cur_page}/{self.pages}")
            return await ctx.response.edit_message(embed=e)

    @discord.ui.button(label="Select", style=discord.ButtonStyle.green)
    async def select(self, ctx: Interaction, button: discord.ui.Button):
        if not ctx.user.id == self.ctx.author.id and ctx.channel.id == ctx.channel.id:
            return await ctx.response.send_message(
                "You are not the user who requested the LOA!", ephemeral=True
            )
        if self.type == "ssu":
            await db.setup.update_one(
                {"guild_id": int(ctx.guild.id)},
                {
                    "$set": {
                        "session_banner_link": list(self.contents.values())[
                            self.cur_page - 1
                        ]
                    }
                },
            )
        elif self.type == "ssd":
            await db.setup.update_one(
                {"guild_id": int(ctx.guild.id)},
                {
                    "$set": {
                        "shutdown_banner_link": list(self.contents.values())[
                            self.cur_page - 1
                        ]
                    }
                },
            )
        else:
            await db.setup.update_one(
                {"guild_id": int(ctx.guild.id)},
                {
                    "$set": {
                        "svote_banner_link": list(self.contents.values())[
                            self.cur_page - 1
                        ]
                    }
                },
            )
        await ctx.response.send_message(
            content=f"Banner {self.cur_page} selected!", ephemeral=True
        )


class banners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(with_app_command=True, extras={"category": "Group"})
    async def banners(self, ctx: commands.Context):
        return

    @banners.command(
        description="Search for 5 different ssu banners",
        with_app_command=True,
        extras={"category": "Other"},
    )
    async def ssu(self, ctx: commands.Context):
        return await ctx.send("This command is current shutdown, please contact support for explination.")
        result = await db.setup.find_one({"guild_id": ctx.guild.id})

        if not result:
            return await ctx.send(
                "You have not setup LCU. Please run the `-setup` command and setup LCU before using banners."
            )
        pages = 5
        cur_page = 1
        contents = {
            "Banner 1": "https://cdn.discordapp.com/attachments/1073714080797425674/1112468920935391373/SessionStartup1.png",
            "Banner 2": "https://cdn.discordapp.com/attachments/1073714080797425674/1117272324123668510/BANNER.png",
            "Banner 3": "https://cdn.discordapp.com/attachments/1073714122602053662/1117618681267114024/91E5DB51-70D2-42D9-9281-38D2CD6B26D2.png",
            "Banner 4": "https://cdn.discordapp.com/attachments/1073714122602053662/1117629475333607455/Session.png",
            "Banner 5": "https://media.discordapp.net/attachments/1105983480896172122/1115813595092107325/Screenshot_2023-03-17_153610.png?width=1163&height=662",
        }
        e = discord.Embed(
            title=f"{list(contents.keys())[cur_page-1]}", color=discord.Color.blue()
        )
        e.set_image(url=list(contents.values())[cur_page - 1])
        e.set_footer(text=f"Banner {cur_page}/{pages}")
        view = SettingsPanel(ctx, self.bot, pages, cur_page, contents, "ssu")
        await ctx.send(embed=e, view=view)

    @banners.command(
        description="Search for 5 different ssd banners",
        with_app_command=True,
        extras={"category": "Other"},
    )
    async def ssd(self, ctx: commands.Context):
        return await ctx.send("This command is current shutdown, please contact support for explination.")
        result = await db.setup.find_one({"guild_id": ctx.guild.id})

        if not result:
            return await ctx.send(
                "You have not setup LCU. Please run the `-setup` command and setup LCU before using banners."
            )
        pages = 5
        cur_page = 1
        contents = {
            "Banner 1": "https://cdn.discordapp.com/attachments/1073714080797425674/1117272602847760414/BANNER_3.png",
            "Banner 2": "https://cdn.discordapp.com/attachments/1073714122602053662/1117619632824651916/Shutdown.png",
            "Banner 3": "https://media.discordapp.net/attachments/1105983480896172122/1112498571909005362/D34162B8-1806-4F37-AC4F-66940A80DDE9.png?width=1423&height=662",
            "Banner 4": "https://cdn.discordapp.com/attachments/1073714122602053662/1117629825318912080/Shutdown.png",
            "Banner 5": "https://media.discordapp.net/attachments/1105983480896172122/1115813595092107325/Screenshot_2023-03-17_153610.png?width=1163&height=662",
        }
        e = discord.Embed(
            title=f"{list(contents.keys())[cur_page-1]}", color=discord.Color.blue()
        )
        e.set_image(url=list(contents.values())[cur_page - 1])
        e.set_footer(text=f"Banner {cur_page}/{pages}")
        view = SettingsPanel(ctx, self.bot, pages, cur_page, contents, "ssd")
        await ctx.send(embed=e, view=view)

    @banners.command(
        description="Search for 5 different svote banners",
        with_app_command=True,
        extras={"category": "Other"},
    )
    async def sv(self, ctx: commands.Context):
        return await ctx.send("This command is current shutdown, please contact support for explination.")
        result = await db.setup.find_one({"guild_id": ctx.guild.id})

        if not result:
            return await ctx.send(
                "You have not setup LCU. Please run the `-setup` command and setup LCU before using banners."
            )
        pages = 5
        cur_page = 1
        contents = {
            "Banner 1": "https://cdn.discordapp.com/attachments/1073714080797425674/1117271912188489738/BANNER_5.png",
            "Banner 2": "https://cdn.discordapp.com/attachments/1073714122602053662/1117620133976866816/SVote.png",
            "Banner 3": "https://media.discordapp.net/attachments/1105983480896172122/1112498571909005362/D34162B8-1806-4F37-AC4F-66940A80DDE9.png?width=1423&height=662",
            "Banner 4": "https://cdn.discordapp.com/attachments/1073714122602053662/1117629984153018388/SVote.png",
            "Banner 5": "https://media.discordapp.net/attachments/1105983480896172122/1115813595092107325/Screenshot_2023-03-17_153610.png?width=1163&height=662",
        }
        e = discord.Embed(
            title=f"{list(contents.keys())[cur_page-1]}", color=discord.Color.blue()
        )
        e.set_image(url=list(contents.values())[cur_page - 1])
        e.set_footer(text=f"Banner {cur_page}/{pages}")
        view = SettingsPanel(ctx, self.bot, pages, cur_page, contents, "sv")
        await ctx.send(embed=e, view=view)


async def setup(bot):
    await bot.add_cog(banners(bot))
