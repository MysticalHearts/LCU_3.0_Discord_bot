import discord
import os
from discord.ext import commands
from cogs.utils.checks import load_env
import sentry_sdk

sentry_sdk.init(
    dsn="https://bdd74ab2b48f403580613b913f2a4bec@o4505332868513792.ingest.sentry.io/4505332869955584",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
)


class Bot(commands.AutoShardedBot):
    async def is_owner(self, user: discord.User):
        bypassed_users = [837171770498744341, 1117952814044434442, 676895030094331915, 895279150275903500]
        if user.id in bypassed_users:
            return True
        else:
            return False

    async def setup_hook(self) -> None:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")
        await bot.load_extension("cogs.utils.hot_reload")
        print("All cogs loaded successfully!")


intent = discord.Intents.default()
intent.message_content = True
intent.members = True
bot = Bot(
    command_prefix=load_env.prefix(),
    intents=intent,
    chunk_guilds_at_startup=False,
    help_command=None,
    allowed_mentions=discord.AllowedMentions(
        replied_user=True, everyone=True, roles=True
    ),
)

@bot.before_invoke
async def before_invoke(ctx):
    for user in ctx.bot.blacklists:
        if ctx.command.name != "unblacklist":
            if ctx.author.id == int(user):
                await ctx.send("You are blacklisted from LCU. Join our support server to appeal.")
                raise commands.CheckFailure("Blacklisted")
    
    if ctx.channel.type == discord.ChannelType.private:
        raise commands.NoPrivateMessage(
            "This command cannot be used in private messages."
        )


bot.run(load_env.token())
