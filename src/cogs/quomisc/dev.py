from __future__ import annotations

import typing as T

if T.TYPE_CHECKING:
    from core import Wolf

import asyncio
import datetime

import discord
from discord.ext import commands
from prettytable import PrettyTable

from core import Cog, Context
from models import BlockIdType, BlockList, Commands
from utils import get_ipm

from .helper import tabulate_query

__all__ = ("Dev",)


class Dev(Cog):
    def __init__(self, bot: Wolf):
        self.bot = bot

    def cog_check(self, ctx: Context):
        return ctx.author.id in ctx.config.DEVS

    @commands.group(hidden=True, invoke_without_command=True)
    async def bl(self, ctx: Context):
        """Blocklist commands."""
        await ctx.send_help(ctx.command)

    @bl.command(name="add")
    async def bl_add(self, ctx: Context, item: discord.User | int, *, reason: str = None):
        """Block a user or guild from using the bot."""
        block_id_type = BlockIdType.USER if isinstance(item, discord.User) else BlockIdType.GUILD
        block_id = item.id if isinstance(item, discord.User) else item

        record = await BlockList.get_or_none(block_id=block_id, block_id_type=block_id_type)
        if record:
            return await ctx.error(f"{item} is already blocked.")

        await BlockList.create(block_id=block_id, block_id_type=block_id_type, reason=reason)
        self.bot.cache.blocked_ids.add(block_id)
        await ctx.success(f"{item} has been blocked.")

    @bl.command(name="remove")
    async def bl_remove(self, ctx: Context, item: discord.User | int):
        """Unblock a user or guild from using the bot."""
        block_id = item.id if isinstance(item, discord.User) else item

        record = await BlockList.get_or_none(block_id=block_id)
        if not record:
            return await ctx.error(f"{item} is not blocked.")

        await record.delete()
        self.bot.cache.blocked_ids.remove(block_id)
        await ctx.success(f"{item} has been unblocked.")

    @commands.command(hidden=True)
    async def sync(
        self,
        ctx: commands.Context,
        guilds: commands.Greedy[discord.Object],
        spec: T.Optional[T.Literal["~", "*", "^"]] = None,
    ) -> None:
        if not guilds:
            if spec == "~":
                synced = await self.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                self.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await self.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                self.bot.tree.clear_commands(guild=ctx.guild)
                await self.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await self.bot.tree.sync()

            await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
            return

        ret = 0
        for guild in guilds:
            try:
                await self.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.group(hidden=True, invoke_without_command=True)
    async def botupdate(self, ctx: Context):
        await ctx.send_help(ctx.command)

    @botupdate.command(name="on")
    async def botmaintenance_on(self, ctx: Context, *, msg: str = None):
        self.bot.lockdown = True
        self.bot.lockdown_msg = msg
        await ctx.success("Now in maintenance mode")
        await asyncio.sleep(120)

        if not self.bot.lockdown:
            return await ctx.error("Lockdown mode has been cancelled")

        await ctx.success("Reloading...")
        self.bot.reboot()

    @botupdate.command(name="off")
    async def botmaintenance_off(self, ctx: Context):
        self.bot.lockdown, self.bot.lockdown_msg = False, None
        await ctx.success("Okay, stopped reload.")

    @commands.command(hidden=True)
    async def cmds(self, ctx: Context):
        total_uses = await Commands.all().count()

        records = await ctx.db.fetch(
            "SELECT cmd, COUNT(*) AS uses FROM commands GROUP BY cmd ORDER BY uses DESC LIMIT 15 "
        )

        table = PrettyTable()
        table.field_names = ["Command", "Invoke Count"]
        for record in records:
            table.add_row([record["cmd"], record["uses"]])

        table = table.get_string()
        embed = self.bot.embed(ctx, title=f"Command Usage ({total_uses})")
        embed.description = f"```{table}```"

        cmds = sum(1 for i in self.bot.walk_commands())

        embed.set_footer(text="Total Commands: {}  | Invoke rate per minute: {}".format(cmds, round(get_ipm(ctx.bot), 2)))

        await ctx.send(embed=embed)

    @commands.group(hidden=True, invoke_without_command=True, name="history")
    async def command_history(self, ctx):
        """Command history."""
        query = """SELECT
                        CASE failed
                            WHEN TRUE THEN cmd || ' [!]'
                            ELSE cmd
                        END AS "cmd",
                        to_char(used_at, 'Mon DD HH12:MI:SS AM') AS "invoked",
                        user_id,
                        guild_id
                   FROM commands
                   ORDER BY used_at DESC
                   LIMIT 15;
                """
        await tabulate_query(ctx, query)

    @command_history.command(name="for")
    async def command_history_for(self, ctx, days: T.Optional[int] = 7, *, command: str):
        """Command history for a command."""
        query = """SELECT *, t.success + t.failed AS "total"
                   FROM (
                       SELECT guild_id,
                              SUM(CASE WHEN failed THEN 0 ELSE 1 END) AS "success",
                              SUM(CASE WHEN failed THEN 1 ELSE 0 END) AS "failed"
                       FROM commands
                       WHERE cmd=$1
                       AND used_at > (CURRENT_TIMESTAMP - $2::interval)
                       GROUP BY guild_id
                   ) AS t
                   ORDER BY "total" DESC
                   LIMIT 30;
                """

        await tabulate_query(ctx, query, command, datetime.timedelta(days=days))

    @command_history.command(name="guild", aliases=["server"])
    async def command_history_guild(self, ctx, guild_id: int):
        """Command history for a guild."""
        query = """SELECT
                        CASE failed
                            WHEN TRUE THEN cmd || ' [!]'
                            ELSE cmd
                        END AS "cmd",
                        channel_id,
                        user_id,
                        used_at
                   FROM commands
                   WHERE guild_id=$1
                   ORDER BY used_at DESC
                   LIMIT 15;
                """
        await tabulate_query(ctx, query, guild_id)

    @command_history.command(name="user", aliases=["member"])
    async def command_history_user(self, ctx, user_id: int):
        """Command history for a user."""
        query = """SELECT
                        CASE failed
                            WHEN TRUE THEN cmd || ' [!]'
                            ELSE cmd
                        END AS "cmd",
                        guild_id,
                        used_at
                   FROM commands
                   WHERE user_id=$1
                   ORDER BY used_at DESC
                   LIMIT 20;
                """
        await tabulate_query(ctx, query, user_id)

    @commands.command(hidden=True)
    async def broadcast(self, ctx: Context, *, message: str):
        """Broadcast a message to all servers' private channels and server owners."""
        from models import Guild as GuildModel
        
        channel_count = 0
        owner_count = 0
        failed = 0
        
        async for guild_record in GuildModel.all():
            guild = self.bot.get_guild(guild_record.guild_id)
            if guild:
                # Send to private channel if exists
                if guild_record.private_channel:
                    channel = guild.get_channel(guild_record.private_channel)
                    if channel:
                        try:
                            await channel.send(message)
                            channel_count += 1
                        except:
                            failed += 1
                
                # Send to server owner
                if guild.owner:
                    try:
                        await guild.owner.send(message)
                        owner_count += 1
                    except:
                        failed += 1
        
        await ctx.success(f"Broadcast sent to {channel_count} channels and {owner_count} owners. Failed: {failed}")

    @commands.group(hidden=True, invoke_without_command=True, name="prm")
    async def premium_admin(self, ctx: Context):
        """Premium management."""
        await ctx.send_help(ctx.command)

    @premium_admin.group(name="user", invoke_without_command=True)
    async def premium_user(self, ctx: Context):
        """User premium management."""
        await ctx.send_help(ctx.command)
    
    @premium_user.command(name="add")
    async def premium_user_add(self, ctx: Context, user: discord.User, days: int = 30):
        """Add premium to a user. Usage: prm user add <user> [days]"""
        from models import User as UserModel
        from datetime import datetime, timedelta
        import constants as csts
        
        user_record = await UserModel.get_or_none(pk=user.id)
        if not user_record:
            user_record = await UserModel.create(user_id=user.id)
        
        end_time = datetime.now(tz=csts.IST) + timedelta(days=days)
        await UserModel.filter(pk=user.id).update(
            is_premium=True,
            premium_expire_time=end_time
        )
        
        await ctx.success(f"Added {days} days of premium to {user.mention}.")
    
    @premium_admin.group(name="guild", invoke_without_command=True)
    async def premium_guild(self, ctx: Context):
        """Guild premium management."""
        await ctx.send_help(ctx.command)
    
    @premium_guild.command(name="add")
    async def premium_guild_add(self, ctx: Context, guild_id: int, days: int = 30):
        """Add premium to a guild. Usage: prm guild add <guild_id> [days]"""
        from models import Guild as GuildModel
        from datetime import datetime, timedelta
        import constants as csts
        
        guild_record = await GuildModel.get_or_none(pk=guild_id)
        if not guild_record:
            guild_record = await GuildModel.create(guild_id=guild_id)
        
        end_time = datetime.now(tz=csts.IST) + timedelta(days=days)
        await GuildModel.filter(pk=guild_id).update(
            is_premium=True,
            premium_end_time=end_time,
            made_premium_by=ctx.author.id
        )
        
        guild = self.bot.get_guild(guild_id)
        guild_name = guild.name if guild else f"Guild {guild_id}"
        await ctx.success(f"Added {days} days of premium to {guild_name}.")
    
    @premium_admin.command(name="list")
    async def premium_list(self, ctx: Context):
        """List all premium users and guilds."""
        from models import User as UserModel, Guild as GuildModel
        from utils import discord_timestamp
        
        embed = discord.Embed(color=self.bot.color, title="Premium Users & Guilds")
        
        premium_users = await UserModel.filter(is_premium=True).all()
        if premium_users:
            user_list = []
            for user in premium_users[:10]:
                user_obj = self.bot.get_user(user.user_id)
                user_name = user_obj.name if user_obj else f"User {user.user_id}"
                expiry = discord_timestamp(user.premium_expire_time) if user.premium_expire_time else "Never"
                user_list.append(f"**{user_name}** (ID: {user.user_id}) - Expires: {expiry}")
            
            embed.add_field(
                name=f"Premium Users ({len(premium_users)})",
                value="\n".join(user_list) if user_list else "None",
                inline=False
            )
        
        premium_guilds = await GuildModel.filter(is_premium=True).all()
        if premium_guilds:
            guild_list = []
            for guild_record in premium_guilds[:10]:
                guild = self.bot.get_guild(guild_record.guild_id)
                guild_name = guild.name if guild else f"Guild {guild_record.guild_id}"
                expiry = discord_timestamp(guild_record.premium_end_time) if guild_record.premium_end_time else "Never"
                guild_list.append(f"**{guild_name}** (ID: {guild_record.guild_id}) - Expires: {expiry}")
            
            embed.add_field(
                name=f"Premium Guilds ({len(premium_guilds)})",
                value="\n".join(guild_list) if guild_list else "None",
                inline=False
            )
        
        if not premium_users and not premium_guilds:
            embed.description = "No premium users or guilds found."
        
        await ctx.send(embed=embed)

    @command_history.command(name="cog")
    async def command_history_cog(self, ctx, days: T.Optional[int] = 7, *, cog: str = None):
        """Command history for a cog or grouped by a cog."""
        interval = datetime.timedelta(days=days)
        if cog is not None:
            cog = self.bot.get_cog(cog)
            if cog is None:
                return await ctx.send(f"Unknown cog: {cog}")

            query = """SELECT *, t.success + t.failed AS "total"
                       FROM (
                           SELECT command,
                                  SUM(CASE WHEN failed THEN 0 ELSE 1 END) AS "success",
                                  SUM(CASE WHEN failed THEN 1 ELSE 0 END) AS "failed"
                           FROM commands
                           WHERE cmd = any($1::text[])
                           AND used_at > (CURRENT_TIMESTAMP - $2::interval)
                           GROUP BY cmd
                       ) AS t
                       ORDER BY "total" DESC
                       LIMIT 30;
                    """
            return await tabulate_query(ctx, query, [c.qualified_name for c in cog.walk_commands()], interval)
