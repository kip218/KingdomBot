from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Embed
from random import randint

from ..db import db
from .. import bot
DELETED_MESSAGES = bot.DELETED_MESSAGES


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command()
    async def sheesh(self, ctx):
        '''
        SHEEEEESH!
        '''
        n = randint(2, 30)
        await ctx.send(f"SH{'E'*n}SH!")


    @command()
    async def snipe(self, ctx):
        '''
        See last deleted message.
        '''
        key = f"{ctx.guild.id}{ctx.channel.id}"
        if key not in DELETED_MESSAGES:
            await ctx.send("There's nothing to snipe!")
            return
        msg = DELETED_MESSAGES[key]
        embed = Embed(description=msg['content'],timestamp=msg['time'])\
                .set_author(name=msg['author'],icon_url=msg['avatar_url'])
        await ctx.send(embed=embed)


    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, 'cog ready')


def setup(bot):
    bot.add_cog(Misc(bot))