from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Embed

from ..db import db
from .. import units
UNITS = units.MAP


class Pvp(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command(aliases=['lb'])
    async def leaderboard(self, ctx):
        '''
        Show Kingdom leaderboard for the server.
        '''
        guild_members = ctx.guild.members
        id_lst = [member.id for member in guild_members]
        lb_lst = []
        for userID in id_lst:
            user_stats = db.record("SELECT Username, Balance, KingdomName\
                                   FROM users WHERE UserID = %s", userID)
            if user_stats is not None:
                username = user_stats[0]
                balance = user_stats[1]
                kingdom_name = user_stats[2]
                lb_lst.append({'username':username, 'balance':balance, 'kingdom_name':kingdom_name})
                if len(lb_lst) == 10:
                    break
        #sorting leaderboard by balance
        lb_lst = sorted(lb_lst, key=lambda k: k['balance'], reverse=True)

        desc = ''
        place = 1
        for user in lb_lst:
            username = user['username']
            balance = user['balance']
            kingdom_name = user['kingdom_name']
            desc += f"**{place}. {username}'s {kingdom_name}** - {balance} coins\n"
            place += 1
        embed = Embed(title='Kingdom Leaderboard', description=desc)\
            .set_footer(text=f"Leaderboard for {ctx.guild.name}",
                        icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)


    @command()
    async def army(self, ctx):
        '''
        Shows your army.
        '''
        army = db.get_army(ctx.author.id)

        desc = ''
        for unit in army:
            unit_name = unit[0]
            unit_count = int(unit[1])
            unit_emoji = UNITS[unit_name].get_emoji()
            desc += f'{unit_emoji}`{unit_name}`       x {unit_count}\n'
        embed = Embed(title=f"{ctx.author.name}'s Army", description=desc)
        await ctx.send(embed=embed)


    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, 'cog ready')


def setup(bot):
    bot.add_cog(Pvp(bot))