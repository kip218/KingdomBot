from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Embed

from ..db import db


class Basic(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command()
    async def start(self, ctx):
        '''
        Start your kingdom!
        '''
        userID= ctx.message.author.id
        username = ctx.message.author.name
        already_started = db.record("SELECT UserID FROM users WHERE UserID = %s", userID)
        if already_started:
            await ctx.send("You have already started a Kingdom!")
        else:
            db.execute("INSERT INTO users (UserID, Username) VALUES (%s, %s) ON CONFLICT (UserID) DO NOTHING;",
                            userID, username)
            await ctx.send("Welcome to your Kingdom!")


    @command(aliases=['profile','balance'])
    async def kingdom(self, ctx):
        '''
        Shows your kingdom.
        '''
        balance, kingdom_name, kingdom_emblem = \
                db.record("SELECT Balance, KingdomName, KingdomEmblem\
                           FROM users WHERE UserID = %s", ctx.message.author.id)
        user = ctx.message.author
        title = f'{kingdom_emblem} {kingdom_name} {kingdom_emblem}'
        color = user.color
        icon_url = user.avatar_url
        embed = Embed(title=title, color=color)\
                        .set_thumbnail(url=icon_url)\
                        .add_field(name='Coins', value=balance)\
                        .set_footer(text=f"{user}'s kingdom")
        await ctx.send(embed=embed)


    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, 'cog ready')


def setup(bot):
    bot.add_cog(Basic(bot))