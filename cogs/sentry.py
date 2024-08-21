import discord
from discord.ext import commands
import datetime
import time
import asyncio
import aiohttp
import logging
from cogs.utils.checks import load_env

def check_support(ctx, bot):
    try:
        server = bot.get_guild(1000207936204836965)
        role1 = discord.utils.get(server.roles, id=1059547821101023242)
        role2 = discord.utils.get(server.roles, id=1059547830680813710)
        role3 = discord.utils.get(server.roles, id=1059547840839417907)
        if (
            role1 in ctx.author.roles
            or role2 in ctx.author.roles
            or role3 in ctx.author.roles
        ):
            return True
    except discord.HTTPException:
        server2 = bot.get_guild(1073712961253818459)
        role1 = discord.utils.get(server2.roles, id=1092525231832305748)
        role2 = discord.utils.get(server2.roles, id=1179295706192810054)
        role3 = discord.utils.get(server2.roles, id=1181758546602381422)
        role4 = discord.utils.get(server2.roles, id=1162801535932190891)
        role5 = discord.utils.get(server2.roles, id=1162168265330655243)

        if (
            role1 in ctx.author.roles
            or role2 in ctx.author.roles
            or role3 in ctx.author.roles
            or role4 in ctx.author.roles
            or role5 in ctx.author.roles
        ):
            return True

class sentry(commands.Cog):
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.config = None
        self.headers = None
        self.SENTRY_API_KEY = str(load_env.SENTRY_API_KEY())
        self.SENTRY_ORGANIZATION_SLUG = str(load_env.SENTRY_ORGANIZATION_SLUG())
        self.PROJECT_SLUG = str(load_env.PROJECT_SLUG())
        self.SENTRY_API_URL = str(load_env.SENTRY_API_URL())
        
        self.headers = {
            "Authorization": f"Bearer {self.SENTRY_API_KEY}",
        }

    async def fetch_issues(self, error_id: str):
        url = (f"{self.SENTRY_API_URL}/projects/{self.SENTRY_ORGANIZATION_SLUG}/"
               f"{self.PROJECT_SLUG}/issues/")
        query_params = {"query": f"error_id:{error_id}"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=query_params) as response:
                    return await response.json() if response.status == 200 else None
        except Exception as e:
            logging.error(f"Error fetching issues: {e}")
            return None

    @staticmethod
    def process_response(issues):
        if not issues:
            return None

        issue_data = issues[0]
        title = issue_data.get('title', 'Title not available')
        value = issue_data.get('metadata', {}).get('value', 'Value not available')
        handled = issue_data.get('isUnhandled', 'Handled information not available')
        last_seen = issue_data.get('lastSeen', 'Last seen not available')
        permalink = issue_data.get('permalink', 'Last seen not available')
        

        last_seen_dt = datetime.datetime.fromisoformat(last_seen.replace('Z', '+00:00')).replace(tzinfo=datetime.timezone.utc)
        last_seen_formatted = discord.utils.format_dt(last_seen_dt, style='R')

        return title, value, handled, last_seen_formatted, permalink

    @staticmethod
    async def update_ui(loading, title, value, handled, last_seen, permalink, start_time):
        embed = discord.Embed(title=f"Sentry Issue: {title}", color=discord.Color.from_rgb(43, 45, 49))
        embed.add_field(name="Value", value=value, inline=False)
        embed.add_field(name="Unhandled", value=handled, inline=False)
        embed.add_field(name="Last Seen", value=last_seen, inline=False)
        embed.add_field(name="Link", value=permalink, inline=False)

        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000
        time_content = f"Fetched details at {'normal' if elapsed_time < 1900 else 'slow'} speed. ``{elapsed_time}ms``."
        await loading.edit(content=time_content, embed=embed)

    @commands.command(description="Get a Sentry issue by error ID", extras={"category": "Staff"})
    @commands.is_owner()
    async def sentry(self, ctx, error_id: str):
        if check_support(ctx, self.bot):
            loading = await ctx.send(content=f"Fetching...")
            start_time = time.time()

            for _ in range(1):
                issues = await self.fetch_issues(error_id)
                issue_data = self.process_response(issues)
                

                if issue_data is not None:
                    await self.update_ui(loading, *issue_data, start_time)
                    return

                next_attempt_time = int(time.time()) + 5
                await loading.edit(
                    content=f"No matching issues found for error ID: {error_id}... **Trying again "
                            f"<t:{next_attempt_time}:R>**.")
                await asyncio.sleep(5)

            await loading.edit(content=f"No matching issues found for error ID: {error_id} after all attempts.")

async def setup(bot):
    await bot.add_cog(sentry(bot))