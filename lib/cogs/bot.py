from discord.ext.commands import Cog
from discord.ext.commands import command
from datetime import datetime
from discord import Embed

from ..db import db


class Bot(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command()
    async def ping(self, ctx):
        '''
        Checks bot latency from host server.
        '''
        latency = int(self.bot.latency*1000)
        msg_lst = ['Pong! ', str(latency), 'ms']
        msg = ''.join(msg_lst)
        await ctx.send(msg)


    @command()
    async def uptime(self, ctx):
        '''
        Shows bot uptime.
        '''
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"{days}d {hours}h {minutes}m {seconds}s")


    @command()
    async def servers(self, ctx):
        '''
        Shows the number of servers and users using the bot.
        '''
        num = len(self.bot.guilds)
        total_users = 0
        for guild in self.bot.guilds:
            total_users += guild.member_count
        await ctx.send(f"Currently present in {num} different servers with {total_users} users.")


    @command()
    async def server(self, ctx):
        '''
        Gives current server info.
        '''
        title = ctx.guild.name
        description = "Member count: " + str(ctx.guild.member_count)
        color = 0x48d1cc
        icon_url = ctx.guild.icon_url
        embed = Embed(title=title, description=description, color=color).set_thumbnail(url=icon_url)
        await ctx.send(embed=embed)


    @command()
    async def invite(self, ctx):
        '''
        Get invite link for KingdomBot.
        '''
        title = 'Invite Link'
        description = 'Click the link below to invite KingdomBot to your server.'
        url = self.bot.BOT_INVITE_URL
        avatar_url = self.bot.user.avatar_url
        embed = Embed(title=title, url=url)\
                .set_author(name=description, icon_url=avatar_url)
        await ctx.send(embed=embed)


    @command()
    async def prefix(self, ctx, new_prefix=''):
        '''
        Change the prefix for the bot.
        '''
        if not new_prefix:
            prefix = db.get_prefix(ctx.guild.id)
            await ctx.send(f"Current prefix for this server is `{prefix}`")
            return
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("Only server admins can change the prefix!")
            return
        if len(new_prefix) > 5:
            await ctx.send("Prefix can't be over 5 characters")
            return
        db.change_prefix(ctx.guild.id, new_prefix)
        await ctx.send(f'Prefix has been changed to `{new_prefix}`')


    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, 'cog ready')


def setup(bot):
    bot.add_cog(Bot(bot))