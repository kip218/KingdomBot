from discord.ext.commands import Cog
from discord.ext.commands import command, max_concurrency, BucketType
from discord import Embed
from asyncio import TimeoutError

from ..db import db
from ..games.montyhall import MontyHall


class Game(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command()
    @max_concurrency(1, per=BucketType.user)
    async def montyhall(self, ctx):
        '''
        Play a game of Monty Hall.
        '''
        def check_guess(m):
            return m.author == ctx.author and m.content in ['1', '2', '3'] and m.channel == ctx.channel

        def check_switch(m):
            return m.author == ctx.author and m.content.lower() in ['y', 'n'] and m.channel == ctx.channel

        m = MontyHall()
        msg = await ctx.send(f"Choose a door to open (1, 2, 3)\n\n{m.display()}")

        #take guess
        try:
            answer = await self.bot.wait_for('message', check=check_guess, timeout=60)
            answer = int(answer.content)
            m.take_guess(answer)
        except TimeoutError:
            await msg.edit(content=msg.content + "\n\nThe game has timed out!")
            return
        else:
            open_pkg_num = m.reveal_pkg()
            await msg.edit(content=f"You've chosen {m.guess}.\n\nPackage {open_pkg_num} has been opened, revealing no coin.\n\nWould you like to switch? (y/n)\n\n{m.display()}")

        #take switch
        try:
            switch = await self.bot.wait_for('message', check=check_switch, timeout=60)
            switch = switch.content.lower()
            m.switch(switch)
        except TimeoutError:
            await msg.edit(content=msg.content + "\n\nThe game has timed out!")
            return
        else:
            m.reveal_all()
            if m.guess == m.coin:
                await msg.edit(content=f"You found the coin!\n\n{m.display()}")
            else:
                await msg.edit(content=f"You did not find the coin. Try again!\n\n{m.display()}")


    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, 'cog ready')


def setup(bot):
    bot.add_cog(Game(bot))