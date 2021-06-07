from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Embed, Emoji
from typing import Union

from ..db import db


class Basic(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command()
    async def start(self, ctx):
        '''
        Start your kingdom!
        '''
        if db.user_exists(ctx.message.author.id):
            await ctx.send("You have already started a Kingdom!")
            return

        userID= ctx.message.author.id
        username = ctx.message.author.name
        db.execute("INSERT INTO users (UserID, Username) VALUES (%s, %s) ON CONFLICT (UserID) DO NOTHING;",
                        userID, username)
        await ctx.send("Welcome to your Kingdom!")


    @command(aliases=['profile','balance','base','info'])
    async def kingdom(self, ctx):
        '''
        Shows your kingdom.
        '''
        balance, kingdom_name, kingdom_emblem = \
                db.record("SELECT Balance, KingdomName, KingdomEmblem\
                           FROM users WHERE UserID = %s", ctx.message.author.id)
        user = ctx.message.author
        title = kingdom_name
        color = user.color
        icon_url = kingdom_emblem
        embed = Embed(title=title, color=color)\
                        .set_thumbnail(url=icon_url)\
                        .add_field(name=':coin:Balance', value=f'{balance} coins')\
                        .set_footer(text=f"{user}'s kingdom")
        await ctx.send(embed=embed)


    @command(usage="<kingdom name>")
    async def kingdomname(self, ctx, *, kingdom_name:str):
        '''
        Change your Kingdom name.
        '''
        if len(kingdom_name) > 40:
            await ctx.send("Kingdom names must be shorter than 40 characters!")
            return
        userID = ctx.author.id
        db.change_kingdom_name(userID, kingdom_name)
        await ctx.send(f"Your Kingdom name has been changed to {kingdom_name}.")


    @command(usage="<custom emoji>")
    async def emblem(self, ctx, kingdom_emblem:Union[Emoji, str]):
        '''
        Change your Kingdom Emblem.
        '''
        if isinstance(kingdom_emblem, str):
            await ctx.send("This command only takes <custom emoji> as an argument!")
            return
        userID = ctx.author.id
        db.change_kingdom_emblem(userID, str(kingdom_emblem.url))
        await ctx.send(f"Your Kingdom emblem has been changed to {kingdom_emblem}.")


    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, 'cog ready')


def setup(bot):
    bot.add_cog(Basic(bot))