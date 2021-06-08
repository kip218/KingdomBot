from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Embed

from ..db import db
from .. import units
UNITS = units.MAP


class Store(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command(aliases=['shop'])
    async def store(self, ctx):
        '''
        The store.
        '''
        desc = f"Use `{self.bot.PREFIX}buy <item>` to buy.\n\n"
        for unit in UNITS.keys():
            emoji = UNITS[unit].get_emoji()
            cost = UNITS[unit].get_cost()
            desc += f'{emoji}`{unit}` {cost} coins\n'

        balance = db.get_balance(ctx.author.id)
        embed = Embed(title='Store', description=desc)\
                    .set_footer(text=f"Your balance: {balance} coins")
        await ctx.send(embed=embed)


    @command()
    async def buy(self, ctx, item):
        '''
        Buy an item from the store.
        '''
        item = item.capitalize()
        if item not in UNITS:
            await ctx.send(f'Could not find {item} in store.')

        userID = ctx.author.id
        unit_name = UNITS[item].get_name()
        unit_cost = UNITS[item].get_cost()
        if db.get_balance(userID) < unit_cost:
            await ctx.send("You don't have enough coins!")
        db.deduct_balance(userID, unit_cost)
        db.add_unit(userID, unit_name)
        await ctx.send(f'{unit_name} has been added to your army!')


    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, 'cog ready')


def setup(bot):
    bot.add_cog(Store(bot))