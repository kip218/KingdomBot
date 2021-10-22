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
        db.add_user(userID, username)
        prefix = db.get_prefix(ctx.guild.id)
        await ctx.send(f"Welcome to your Kingdom! Try `{prefix}kingdom` to see your kingdom.")


    @command(usage='[user.mention]', aliases=['bal','balance','base','info'])
    async def kingdom(self, ctx, user=None):
        '''
        Shows user's kingdom. Shows your kingdom if no argument is provided.
        '''
        if user and ctx.message.mentions:
            user = ctx.message.mentions[0]
        else:
            user = ctx.message.author
        balance, kingdom_name, kingdom_emblem = \
                db.record("SELECT Balance, KingdomName, KingdomEmblem\
                           FROM users WHERE UserID = %s", user.id)
        title = kingdom_name
        color = user.color
        icon_url = kingdom_emblem
        avatar_url = ctx.author.avatar_url
        embed = Embed(title=title, color=color)\
                        .set_thumbnail(url=icon_url)\
                        .add_field(name=':coin:Balance', value=f'{balance} coins')\
                        .set_footer(text=f"{user}'s Kingdom")\
                        .set_author(name=user, icon_url=avatar_url)
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
            await ctx.send("This command only takes <custom emoji> as an argument! The custom emoji must be from this server.")
            return
        userID = ctx.author.id
        db.change_kingdom_emblem(userID, str(kingdom_emblem.url))
        await ctx.send(f"Your Kingdom emblem has been changed to {kingdom_emblem}.")


    @command(usage='<user.mention> <amount>', aliases=['give'])
    async def pay(self, ctx, user, amount:int=None):
        '''
        Pay another user <amount> of coins.
        '''
        if len(ctx.message.mentions) == 0:
            await ctx.send("You must mention a user to pay!")
            return

        if amount is None:
            await ctx.send("You must specify the amount of payment!")
            return

        if amount <= 0:
            await ctx.send("Payment amount must be positive!")
            return

        if db.get_balance(ctx.author.id) < amount:
            await ctx.send("You don't have enough coins!")
            return

        receiver = ctx.message.mentions[0]
        if receiver.bot:
            await ctx.send("You can't pay a bot!")
            return

        if receiver == ctx.author:
            await ctx.send("You can't pay yourself!")
            return

        if not db.user_exists(receiver.id):
            await ctx.send(f"{receiver.name} has not started their Kingdom yet!")
            return

        db.add_balance(receiver.id, amount)
        db.deduct_balance(ctx.author.id, amount)
        await ctx.send(f'{ctx.author.mention} has paid {receiver.mention} {amount} coins.')


    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, 'cog ready')


def setup(bot):
    bot.add_cog(Basic(bot))