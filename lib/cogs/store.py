from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Embed

from ..db import db
from .. import units

UNITS = units.MAP


class Store(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(aliases=["shop"])
    async def store(self, ctx):
        """
        The store.
        """
        prefix = db.get_prefix(ctx.guild.id)
        desc = f"Use `{prefix}buy <item>` to buy.\n\n"
        for unit in UNITS.keys():
            emoji = UNITS[unit].get_emoji()
            cost = UNITS[unit].get_cost()
            desc += f"{emoji}`{unit}` {cost} coins\n"

        balance = db.get_balance(ctx.author.id)
        embed = Embed(title="Store", description=desc).set_footer(
            text=f"Your balance: {balance} coins"
        )
        await ctx.send(embed=embed)

    @command(usage="<item> <n=1>")
    async def buy(self, ctx, item, n: int = 1):
        """
        Buy an item from the store.
        """
        item = item.capitalize()
        if item not in UNITS:
            await ctx.send(f"Could not find {item} in store.")
            return

        if n <= 0:
            await ctx.send("<n> must be a positive number.")
            return
        elif n > 10:
            await ctx.send("You can only buy 10 items at a time max.")
            return

        userID = ctx.author.id

        army_limit = 10
        army_size = db.get_armysize(userID)
        if army_size + n > army_limit:
            await ctx.send(
                f"Army capacity of {army_limit} exceeded. Current army size: {army_size}"
            )
            return

        unit_name = UNITS[item].get_name()
        unit_cost = UNITS[item].get_cost()
        purchase_cost = unit_cost * n
        if db.get_balance(userID) < purchase_cost:
            await ctx.send("You don't have enough coins!")
            return
        for i in range(n):
            db.deduct_balance(userID, unit_cost)
            db.add_unit(userID, unit_name)
        await ctx.send(f"{unit_name} x{n} has been added to your army!")

    @command(usage="<unit>")
    async def stats(self, ctx, unit):
        """
        Shows unit stats.
        """
        unit = unit.capitalize()
        if unit not in UNITS:
            await ctx.send(f"Could not find {unit}.")

        unit = UNITS[unit]
        name = unit.get_name()
        emoji = unit.get_emoji()
        cost = unit.get_cost()
        dmg = unit.get_dmg()
        max_hp = unit.get_max_hp()
        speed = unit.get_speed()
        gauge = unit.get_gauge()

        desc = f"**NAME** {name}\n\
                 **COST** {cost}\n\
                 **ATK** {dmg}\n\
                 **HP** {max_hp}\n\
                 **SPEED** {speed}\n\
                 **INITIAL GAUGE** {gauge}"
        embed = Embed(title=f"{emoji}`{name}`", description=desc)
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, "cog ready")


def setup(bot):
    bot.add_cog(Store(bot))
