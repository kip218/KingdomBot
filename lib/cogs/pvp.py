from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Embed
from asyncio import sleep

from ..db import db
from ..war import *
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
        if army is None:
            await ctx.send('Your army is empty!')
            return

        desc = ''
        for unit in army:
            unit_name = unit[0]
            unit_count = int(unit[1])
            unit_emoji = UNITS[unit_name].get_emoji()
            desc += f'{unit_emoji}`{unit_name}`       x {unit_count}\n'
        embed = Embed(title=f"{ctx.author.name}'s Army", description=desc)
        await ctx.send(embed=embed)


    @command(aliases=['attack','invade'])
    async def raid(self, ctx, user):
        '''
        Raid another user's Kingdom.
        '''
        if len(ctx.message.mentions) == 0:
            await ctx.send("You must mention a user to raid!")
            return
        attacker = ctx.author
        defender = ctx.message.mentions[0]
        if attacker == defender:
            await ctx.send("You cannot raid yourself!")
            return
        if not db.user_exists(defender.id):
            await ctx.send(f"{defender.mention} has not started a Kingdom yet!")

        def get_embed(i):
            title = f'{attacker.name} VS {defender.name}'
            embed = Embed(title=title)
            embed.add_field(name=f"{attacker.name}'s Army", value=army1.army_state())
            embed.add_field(name=f"{defender.name}'s Army", value=army2.army_state())
            embed.set_footer(text=f"Round {i}")
            return embed

        army1 = Army(db.get_army(attacker.id))
        army2 = Army(db.get_army(defender.id))
        w = War(army1, army2)
        
        i = 1
        embed = get_embed(i)
        msg = await ctx.send(embed=embed)
        while not w.war_over():
            w.process_turn()
            embed = get_embed(i)
            i += 1
            await sleep(0.5)
            await msg.edit(embed=embed)
            w.fill_gauge()

        army1 = army1.get_full_army()
        army2 = army2.get_full_army()
        db.reset_army(attacker.id)
        db.reset_army(defender.id)
        db.add_units(attacker.id, [unit.get_name() for unit in army1])
        db.add_units(defender.id, [unit.get_name() for unit in army2])

        if army1:
            await ctx.send("Raid successful! You have annihilated the opposing army!")
        elif army2:
            await ctx.send("Raid failed! You were destroyed by the opposing army!")




    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, 'cog ready')


def setup(bot):
    bot.add_cog(Pvp(bot))