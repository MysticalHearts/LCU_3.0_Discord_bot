import discord
from discord.ext import commands
import datetime
from datetime import timezone
from cogs.events import db


class logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not member.guild:
            return
        elif member.guild.chunked:
            pass
        else: 
            await member.guild.chunk()

        logging_check = True
        welcoming_check = True
        records = await db.settings.find_one({'guild_id': member.guild.id}, {'welcome_toggle': 1, 'logging_toggle': 1, 'join_channel': 1, 'welcome_channel': 1, '_id': 0, 'welcome_text': 1})
        try:
            if records['logging_toggle'] == 0:
                logging_check = False
            
            if not records['join_channel']:
                logging_check = False
        except Exception:
            logging_check = False
        
        
        if logging_check:
            try:
                join_leave_channel = self.bot.get_channel(int(records['join_channel']))
                embed = discord.Embed(
                    description=f"**{member.mention}** has joined the server!",
                    color=discord.Color.green()
                )
                if not member.avatar.url:
                    embed.set_author(name=member.name, icon_url=member.default_avatar.url)
                else:
                    embed.set_author(name=member.name, icon_url=member.avatar.url)

                embed.add_field(name="Account Created", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline=True)
                embed.add_field(name="Member Count", value=member.guild.member_count, inline=True)
                embed.set_footer(text=f"User ID: {member.id} • LCU")
                await join_leave_channel.send(embed=embed)
            except Exception:
                logging_check = False
        
        try:
            if records['welcome_toggle'] == 0:
                welcoming_check = False
        except Exception:
            welcoming_check = False

        if welcoming_check:
            description = str(records['welcome_text'])
            try:
                new_des = description.replace("{member_mention}", member.mention)
                new_string1 = new_des.replace("{member_name}", str(member.name))
                new_string2 = new_string1.replace("{guild_name}", str(member.guild.name))
                new_string3 = new_string2.replace("{member_count}", str(member.guild.member_count))

                
                channel = self.bot.get_channel(int(records['welcome_channel']))
                await channel.send(new_string3)
            except KeyError:
                welcoming_check = False
        
        return

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if not member.guild:
            return
        elif member.guild.chunked:
            pass
        else: 
            await member.guild.chunk()
        records = await db.settings.find_one({'guild_id': member.guild.id}, {'logging_toggle': 1, 'leave_channel': 1, '_id': 0})
        try:
            if records['logging_toggle'] == 0:
                return
        except Exception:
            return
        
        if not records['leave_channel']:
            return
        
        
        join_leave_channel = self.bot.get_channel(records['leave_channel'])
        embed = discord.Embed(
            description=f"**{member.mention}** has left the server!",
            color=discord.Color.red()
        )
        if not member.avatar.url:
            embed.set_author(name=member.name, icon_url=member.default_avatar.url)
        else:
            embed.set_author(name=member.name, icon_url=member.avatar.url)
        embed.add_field(name="Member Count", value=member.guild.member_count)
        roles = ""
        for role in member.roles:
            roles += f"{role.mention}\n"
        embed.add_field(name="Previous Roles", value=roles, inline=False)
        embed.set_footer(text=f"User ID: {member.id} • LCU")
        try:
            await join_leave_channel.send(embed=embed)
        except discord.HTTPException:
            return


    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.message.Message):
        if not message.guild:
            return
        elif message.guild.chunked:
            pass
        else: 
            await message.guild.chunk()

        try:
            records = await db.settings.find_one({'guild_id': message.guild.id}, {'logging_channel': 1, 'logging_toggle': 1, '_id': 0})
        except Exception:
            return
        try:
            if records['logging_toggle'] == 0:
                return
        except Exception:
            return
        
        if not records['logging_channel']:
            return

        if message.author.bot:
            return

        if message.content == "":
            return

        try:
            async for entry in message.guild.audit_logs(limit=1,action=discord.AuditLogAction.message_delete):
                entry = entry
        except discord.Forbidden:
            return
        except discord.HTTPException:
            return
        except Exception:
            return
        desired_offset = timezone.utc
        if entry and entry.created_at.replace(microsecond=0, tzinfo=desired_offset) == datetime.datetime.utcnow().replace(microsecond=0, tzinfo=desired_offset):
            em = discord.Embed(description=f"Message from {message.author.mention} was deleted in <#{message.channel.id}> by **{entry.user.mention}**. \n", color=discord.Color.red())
        else:
            em = discord.Embed(description=f"Message from {message.author.mention} was deleted in <#{message.channel.id}>. \n", color=discord.Color.red())
        em.add_field(name="Message", value=message.content)

        if not message.author.avatar.url:
            em.set_author(name=message.author.name, icon_url=message.author.default_avatar.url)
        else:
            em.set_author(name=message.author.name, icon_url=message.author.avatar.url)
        em.set_footer(text=f"User ID: {message.author.id} | LCU")
        channel = self.bot.get_channel(int(records['logging_channel']))
        try:
            await channel.send(embed=em)
        except discord.HTTPException:
            return

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.guild:
            return
        elif before.guild.chunked:
            pass
        else: 
            await before.guild.chunk()
        records = await db.settings.find_one({'guild_id': before.guild.id}, {'logging_toggle': 1, 'logging_channel': 1, '_id': 0})
        if before.content == after.content:
            return
        if before.author.bot:
            return
        if not before.guild:
            return
        try:
            if records['logging_toggle'] == 0:
                return
        except Exception:
            return
        
        if not records['logging_channel']:
            return

        embed = discord.Embed(
        description = f"Message from <@!{before.author.id}> was edited in <#{before.channel.id}>.",
        colour = discord.Colour(0x00FF00)
        ) 
        if not before.author.avatar.url:
            embed.set_author(name=f'{before.author.name}', icon_url=before.author.default_avatar.url)
        else:
            embed.set_author(name=f'{before.author.name}', icon_url=before.author.avatar.url)
        embed.set_footer(text=f"Author ID:{before.author.id} • Message ID: {before.id} • LCU")
        embed.add_field(name='Before', value=before.content + "\u200b", inline=False)
        embed.add_field(name="After", value=after.content + "\u200b", inline=False)
        channel = self.bot.get_channel(int(records['logging_channel']))
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            return

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not before.guild:
            return
        elif before.guild.chunked:
            pass
        else: 
            await before.guild.chunk()
        records = await db.settings.find_one({'guild_id': before.guild.id}, {'logging_toggle': 1, 'logging_channel': 1, '_id': 0})
        try:
            if records['logging_toggle'] == 0:
                return
        except Exception:
            return
        
        try:
            if not records['logging_channel']:
                return
        except Exception:
            return
            
        if len(before.roles) < len(after.roles):
            changed_role_set = set(before.roles) ^ set(after.roles)
            if len(changed_role_set) > 0:
                changed_role = next(iter(changed_role_set))
            else:
                return
            embed = discord.Embed(
                description=f"**{after.mention}** was given the `{changed_role.name}` role.",
                color=discord.Color.green()
            )
            if not after.avatar.url:
                embed.set_author(name=after.name, icon_url=after.default_avatar.url)
            else:
                embed.set_author(name=after.name, icon_url=after.avatar.url)
            embed.set_footer(text=f"User ID: {after.id} • LCU")
            channel = self.bot.get_channel(int(records['logging_channel']))
            try:
                await channel.send(embed=embed)
            except discord.HTTPException:
                return
        if len(before.roles) > len(after.roles):
            changed_role_set = set(before.roles) ^ set(after.roles)
            if len(changed_role_set) > 0:
                changed_role = next(iter(changed_role_set))
            else:
                return
            embed = discord.Embed(
                description=f"**{after.mention}** was removed from the `{changed_role.name}` role.",
                color=discord.Color.red()
            )
            try:
                if not after.avatar.url:
                    embed.set_author(name=after.name, icon_url=after.default_avatar.url)
                else:
                    embed.set_author(name=after.name, icon_url=after.avatar.url)
            except AttributeError:
                embed.set_author(name=after.name, icon_url=after.default_avatar.url)

            embed.set_footer(text=f"User ID: {after.id} • LCU")
            channel = self.bot.get_channel(int(records['logging_channel']))
            try:
                await channel.send(embed=embed)
            except:
                return
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.TextChannel):
        if not channel.guild:
            return
        elif channel.guild.chunked:
            pass
        else: 
            await channel.guild.chunk()
        records = await db.settings.find_one({'guild_id': channel.guild.id}, {'logging_toggle': 1, 'logging_channel': 1, '_id': 0})
        try:
            if records['logging_toggle'] == 0:
                return
        except Exception:
            return
        
        if not records['logging_channel']:
            return

        try:
            async for entry in channel.guild.audit_logs(limit=1,action=discord.AuditLogAction.channel_create):
                entry = entry
        except discord.Forbidden:
            return
        except discord.HTTPException:
            return
        except Exception:
            return
        
        embed = discord.Embed(
            color=discord.Color.green()
        )
        embed.add_field(name="Channel", value=f"#{channel.name}")
        embed.add_field(name="Created By", value=entry.user.mention)
        embed.set_author(name="Channel Created", icon_url=channel.guild.icon.url)
        embed.set_footer(text=f"Channel ID: {channel.id} • LCU")
        channel = self.bot.get_channel(int(records['logging_channel']))
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            return
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.TextChannel):
        if not channel.guild:
            return
        elif channel.guild.chunked:
            pass
        else: 
            await channel.guild.chunk()
        records = await db.settings.find_one({'guild_id': channel.guild.id}, {'logging_toggle': 1, 'logging_channel': 1, '_id': 0})
        try:
            if records['logging_toggle'] == 0:
                return
        except Exception:
            return
        
        if not records['logging_channel']:
            return

        try:
            async for entry in channel.guild.audit_logs(limit=1,action=discord.AuditLogAction.channel_delete):
                entry = entry
        except discord.Forbidden:
            return
        except discord.HTTPException:
            return
        except Exception:
            return
        embed = discord.Embed(
            color=discord.Color.red()
        )
        embed.add_field(name="Channel", value=f"#{channel.name}")
        embed.add_field(name="Deleted By", value=entry.user.mention)
        embed.set_author(name="Channel Deleted", icon_url=channel.guild.icon.url)
        embed.set_footer(text=f"Channel ID: {channel.id} • LCU")
        channel = self.bot.get_channel(int(records['logging_channel']))
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            return
        
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if not before.guild:
            return
        elif before.guild.chunked:
            pass
        else: 
            await before.guild.chunk()

        records = await db.settings.find_one({'guild_id': before.guild.id}, {'logging_toggle': 1, 'logging_channel': 1, '_id': 0})
        try:
            if records['logging_toggle'] == 0:
                return
        except Exception:
            return
        
        if not records['logging_channel']:
            return

        try:
            if not before.topic:
                before.topic = None
            elif not after.topic:
                after.topic = None
        except KeyError:
            before.topic = None
            after.topic = None

        if before.name != after.name:
            try:
                async for entry in before.guild.audit_logs(limit=1,action=discord.AuditLogAction.channel_update):
                    entry = entry
            except discord.Forbidden:
                return
            except discord.HTTPException:
                return
            except Exception:
                return
            embed = discord.Embed(
                color=discord.Color.green()
            )
            embed.add_field(name="Before", value=f"#{before.name}")
            embed.add_field(name="After", value=f"#{after.name}")
            embed.add_field(name="Updated By", value=entry.user.mention)
            embed.set_author(name="Channel Renamed", icon_url=after.guild.icon.url)
            embed.set_footer(text=f"Channel ID: {after.id} • LCU")
            channel = self.bot.get_channel(int(records['logging_channel']))
            try:
                await channel.send(embed=embed)
            except discord.HTTPException:
                return
        if before.topic != after.topic:
            try:
                async for entry in before.guild.audit_logs(limit=1,action=discord.AuditLogAction.channel_update):
                    entry = entry
            except discord.Forbidden:
                return
            except discord.HTTPException:
                return
            except Exception:
                return
            embed = discord.Embed(
                description=f"The topic of the **#{after.name}** channel was changed by **@{entry.user.name}**.",
                color=discord.Color.green()
            )
            embed.add_field(name="Before", value=before.topic, inline=False)
            embed.add_field(name="After", value=after.topic, inline=False)
            embed.set_author(name="Channel Topic Updated", icon_url=after.guild.icon.url)
            embed.set_footer(text=f"Channel ID: {after.id} • LCU")
            channel = self.bot.get_channel(int(records['logging_channel'])) 
            try:
                await channel.send(embed=embed)
            except discord.HTTPException:
                return
        if before.category != after.category:
            try:
                async for entry in before.guild.audit_logs(limit=1,action=discord.AuditLogAction.channel_update):
                    entry = entry
            except discord.Forbidden:
                return
            except discord.HTTPException:
                return
            except Exception:
                return
            embed = discord.Embed(
                description=f"The category of the **#{after.name}** channel was changed by **@{entry.user.name}**.",
                color=discord.Color.green()
            )
            embed.add_field(name="Before", value=before.category, inline=False)
            embed.add_field(name="After", value=after.category, inline=False)
            embed.set_author(name="Channel Category Updated", icon_url=after.guild.icon.url)
            embed.set_footer(text=f"Channel ID: {after.id} • LCU")
            channel = self.bot.get_channel(int(records['logging_channel']))
            try:
                await channel.send(embed=embed)
            except discord.HTTPException:
                return
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        if not role.guild:
            return
        elif role.guild.chunked:
            pass
        else: 
            await role.guild.chunk()
        records = await db.settings.find_one({'guild_id': role.guild.id}, {'logging_toggle': 1, 'logging_channel': 1, '_id': 0})
        try:
            if records['logging_toggle'] == 0:
                return
        except Exception:
            return
        
        if not records['logging_channel']:
            return

        try:
            async for entry in role.guild.audit_logs(limit=1,action=discord.AuditLogAction.role_create):
                entry = entry
        except discord.Forbidden:
            return
        except discord.HTTPException:
            return
        except Exception:
            return
        embed = discord.Embed(
            color=discord.Color.green()
        )
        embed.add_field(name="Role", value=f"{role.mention}")
        embed.add_field(name="Created By", value=entry.user.mention)
        embed.set_author(name="Role Created", icon_url=role.guild.icon.url)
        embed.set_footer(text=f"Role ID: {role.id} • LCU")
        channel = self.bot.get_channel(int(records['logging_channel']))
        try:
            await channel.send(embed=embed)
        except:
            return
        
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        if not role.guild:
            return
        elif role.guild.chunked:
            pass
        else: 
            await role.guild.chunk()
        records = await db.settings.find_one({'guild_id': role.guild.id}, {'logging_toggle': 1, 'logging_channel': 1, '_id': 0})
        try:
            if records['logging_toggle'] == 0:
                return
        except Exception:
            return
        
        if not records['logging_channel']:
            return

        try:
            async for entry in role.guild.audit_logs(limit=1,action=discord.AuditLogAction.role_delete):
                entry = entry
        except discord.Forbidden:
            return
        except discord.HTTPException:
            return
        except Exception:
            return
        embed = discord.Embed(
            color=discord.Color.red()
        )
        embed.add_field(name="Role", value=f"{role.name}")
        embed.add_field(name="Deleted By", value=entry.user.mention)
        embed.set_author(name="Role Deleted", icon_url=role.guild.icon.url)
        embed.set_footer(text=f"Role ID: {role.id} • LCU")
        channel = self.bot.get_channel(int(records['logging_channel']))
        try:
            await channel.send(embed=embed)
        except:
            return
        
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if not guild:
            return
        elif guild.chunked:
            pass
        else: 
            await guild.chunk()
        records = await db.settings.find_one({'guild_id': guild.id}, {'logging_toggle': 1, 'logging_channel': 1, '_id': 0})
        try:
            if records['logging_toggle'] == 0:
                return
        except Exception:
            return
        
        if not records['logging_channel']:
            return

        try:
            async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.ban):
                entry = entry
        except discord.Forbidden:
            return
        except discord.HTTPException:
            return
        except Exception:
            return
        embed = discord.Embed(
            color=discord.Color.red()
        )
        embed.add_field(name="User", value=f"{user.mention}")
        embed.add_field(name="Banned By", value=entry.user.mention)

        if not user.avatar.url:
            embed.set_author(name="User Banned", icon_url=user.default_avatar.url)
        else:
            embed.set_author(name="User Banned", icon_url=user.avatar.url)
        embed.set_footer(text=f"User ID: {user.id} • LCU")
        channel = self.bot.get_channel(int(records['logging_channel']))
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            return
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if not guild:
            return
        elif guild.chunked:
            pass
        else: 
            await guild.chunk()
        records = await db.settings.find_one({'guild_id': guild.id}, {'logging_toggle': 1, 'logging_channel': 1, '_id': 0})
        try:
            if records['logging_toggle'] == 0:
                return
        except Exception:
            return
        
        if not records['logging_channel']:
            return

        try:
            async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.unban):
                entry = entry
        except discord.Forbidden:
            return
        except discord.HTTPException:
            return
        except Exception:
            return
        
        embed = discord.Embed(
            color=discord.Color.green()
        )
        embed.add_field(name="User", value=f"{user.mention}")
        embed.add_field(name="Unbanned By", value=entry.user.mention)
        if not user.avatar.url:
            embed.set_author(name="User Unbanned", icon_url=user.default_avatar.url)
        else:
            embed.set_author(name="User Unbanned", icon_url=user.avatar.url)
        embed.set_footer(text=f"User ID: {user.id} • LCU")
        channel = self.bot.get_channel(int(records['logging_channel']))
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            return
            
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after):
        if not before.guild:
            return
        elif before.guild.chunked:
            pass
        else: 
            await before.guild.chunk()
        records = await db.settings.find_one({'guild_id': before.guild.id}, {'logging_toggle': 1, 'logging_channel': 1, '_id': 0})
        try:
            if records['logging_toggle'] == 0:
                return
        except Exception:
            return
        
        if not records['logging_channel']:
            return

        if before.name != after.name:
            embed = discord.Embed(
                description=f"Role `{before.name}` was renamed to `{after.name}`.",
                color=discord.Color.green()
            )
            embed.set_author(name="Role Renamed", icon_url=after.guild.icon.url)
            embed.set_footer(text=f"Role ID: {after.id} • LCU")
            channel = self.bot.get_channel(int(records['logging_channel']))
            try:
                return await channel.send(embed=embed)
            except:
                pass
        if before.permissions != after.permissions:
            changed_role_perms = ""
            for perm in after.permissions:
                if perm not in before.permissions:
                    changed_role_perms += f"+ {perm[0]}\n"
            embed = discord.Embed(
                color=discord.Color.red()
            )
            embed.set_author(name="Role Permissions Updated", icon_url=after.guild.icon.url)
            embed.add_field(name="Added", value=changed_role_perms, inline=False)
            embed.set_footer(text=f"Role ID: {after.id} • LCU")
            channel = self.bot.get_channel(int(records['logging_channel']))
            try:
                return await channel.send(embed=embed)
            except discord.HTTPException:
                return

            

async def setup(bot):
  await bot.add_cog(logging(bot))


