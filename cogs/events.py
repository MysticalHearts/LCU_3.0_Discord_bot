import discord
from discord.ext import tasks, commands
import datetime
import time
import motor.motor_asyncio
import json
from dotenv import load_dotenv
load_dotenv()
import os

MONGO_URL = os.getenv('MONGO_URL')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client['lcu_beta_db']


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=1)
    async def check_loa_end_date(self):
        all_loas = db.loa.find()
        async for loa_findone in all_loas:
            if not loa_findone['start_date']:
                return
            else:
                current_time = datetime.datetime.now()
                if current_time > loa_findone['end_date']:
                    guild = self.bot.get_guild(loa_findone["guild_id"])
                    if guild:
                        member = guild.get_member(loa_findone["author_id"])
                        if member:
                            loadmembed = discord.Embed(title='Your LOA has expired')
                            await member.send(embed=loadmembed)

                            config = await db.settings.find_one({'guild_id': guild.id})
                            if config and 'loa_channel' in config:
                                channel = self.bot.get_channel(config['loa_channel'])
                                channelembed = discord.Embed(
                                    title='Leave Of Absence Ended',
                                    description=f"Started: {discord.utils.format_dt(loa_findone['start_date'])}\n Ended: {discord.utils.format_dt(loa_findone['end_date'])}\n Reason: {loa_findone['reason']}"
                                )
                                await channel.send(embed=channelembed)

                            await db.loa_list.insert_one({
                                '_id': loa_findone['_id'],
                                'start_date': loa_findone['start_date'],
                                'end_date': loa_findone['end_date'],
                                'guild_id': guild.id,
                                'user_id': member.id
                            })
                            await db.loa.delete_one({'_id': loa_findone['_id']})

                            role = await db.settings.find_one({'guild_id': guild.id})
                            if role and 'loa_role' in role:
                                loa_role = guild.get_role(role['loa_role'])
                                if loa_role:
                                    await member.remove_roles(loa_role)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author == self.bot.user:
                return

            mentioned = self.bot.user.mentioned_in(message)
            mentioned_alone = len(message.content.strip()) == len(self.bot.user.mention)

            if mentioned and mentioned_alone:
                response = (
                    "My prefix is `-`\n"
                    "Try `-help` for help with commands\n"
                    "Try `-setup` to setup the bot"
                )
                await message.channel.send(response)

        except discord.HTTPException as e:
            print(f"HTTP exception in on_message: {e}")
        except Exception as e:
            print(f"An error occurred in on_message: {e}")
            self.restart_message_event()

        

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await guild.chunk()
        channel = self.bot.get_channel(1073714276138766336)

        em = discord.Embed(title=f"Bot Joining Logs", description=f"Guild Name: **{guild}**\nGuild ID: **{guild.id}**\nMember Count: **{guild.member_count}**\nGuild Count: **{str(len(self.bot.guilds))}**")
        await channel.send(embed=em)

        
        # Send a message to the top channel
        em = discord.Embed(title="Thank You For Adding LCU!", description=f"LCU is a fully customizable Emergency Response : Liberty County. We allow you to do such things as sessions, shutdowns, and session votes\n\nSupport server: https://discord.gg/EvcYNK53MC\nSetup Command: `-setup`\nHelp Command: `-help`", color=discord.Color.blue())
        for channel in guild.text_channels:
            try:
                await channel.send(embed=em)
                break
            except Exception:
                pass


    @commands.Cog.listener()
    async def on_ready(self, ctx: commands.Context = None):
        await self.bot.wait_until_ready()
        self.check_loa_end_date.start()
        self.bot.uptime = int(time.time())
        records = db.blacklists.find()
        self.bot.blacklists = []
        async for record in records:
            self.bot.blacklists.append(int(record['user_id']))
        

        await self.bot.change_presence(activity=discord.Activity(name="-help | lcubot.xyz", type=discord.ActivityType.watching))
        
    
        print(self.bot.user.name + " is ready.")
    
    def restart_message_event(self):
        # Implement your restart logic here
        # For example, you might want to unregister and reregister the event
        self.bot.remove_listener(self.on_message)
        self.bot.add_listener(self.on_message)
        self.is_message_event_running = True

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        print(f"An error occurred in {event}")

        if event == 'on_message':
            print("Restarting on_message...")
            self.is_message_event_running = False
            self.restart_message_event()
        

    
async def setup(bot):
  await bot.add_cog(events(bot))


