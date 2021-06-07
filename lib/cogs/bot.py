from discord.ext.commands import Cog
from discord.ext.commands import command
from datetime import datetime
from discord import Embed


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


    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, 'cog ready')


def setup(bot):
    bot.add_cog(Bot(bot))