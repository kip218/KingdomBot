from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Embed
from random import randint
from udpy import UrbanClient
import asyncio
import re

from ..db import db
from .. import bot
DELETED_MESSAGES = bot.DELETED_MESSAGES
EDITED_MESSAGES = bot.EDITED_MESSAGES


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command()
    async def sheesh(self, ctx):
        '''
        SHEEEEESH!
        '''
        n = randint(2, 40)
        await ctx.send(f"SH{'E'*n}SH!")


    @command()
    async def pp(self, ctx):
        '''
        pp?
        '''
        n = randint(2, 40)
        await ctx.send(f"3{'='*n}D")


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


    @command()
    async def editsnipe(self, ctx):
        '''
        See last edited message.
        '''
        key = f"{ctx.guild.id}{ctx.channel.id}"
        if key not in EDITED_MESSAGES:
            await ctx.send("There's nothing to snipe!")
            return
        msg = EDITED_MESSAGES[key]
        embed = Embed(description=msg['content'],timestamp=msg['time'])\
                .set_author(name=msg['author'],icon_url=msg['avatar_url'])
        await ctx.send(embed=embed)


    @command()
    async def define(self, ctx, *, phrase):
        '''
        Get definition from Urban Dictionary.
        '''
        client = UrbanClient()
        defs = client.get_definition(phrase)
        if defs is None:
            await ctx.send('Definition not found.')
            return
        best_def = defs[0]
        embed = Embed(title=best_def.word,description=f"*{best_def.definition}*")\
                    .set_footer(text=f"{best_def.example}")
        await ctx.send(embed=embed)


    @command()
    async def remind(self, ctx, time:str, *, task):
        '''
        Get reminded of <task> after <time>.
        <time> should be formatted as "hh:mm:ss".
        '''
        def getSec(s):
            l = list(map(int, s.split(':')))
            return sum(n * sec for n, sec in zip(l[::-1], (1, 60, 3600)))

        TIME_REGEX = re.compile(r"([0-1]\d|2[0-3]):([0-5]\d):([0-5]\d)$")
        MULTIPLER = {
          "d": 86400,
          "h": 3600,
          "m": 60,
          "s": 1,
        }
        match = TIME_REGEX.match(time)

        if not match:
          await ctx.send("Please enter a valid time. Time should be formatted as 'hh:mm:ss'.")
          return

        time = match.group()
        seconds = getSec(time)

        await ctx.send(f"{ctx.author.mention} I will remind you of `{task}` after {seconds} seconds.")
        await asyncio.sleep(seconds)

        if ctx.author.dm_channel is None:
            await ctx.author.create_dm()
        await ctx.author.dm_channel.send(f"**Reminder:**\n`{task}`")


    @command()
    async def avatar(self, ctx, *, user: str=None):
        '''
        [user]'s profile picture. Sends your profile picture if [user] not specified.
        w.avatar [user]
        '''
        # gets embed msg of member's avatar
        def get_pfp(member):
            pic_url = member.avatar_url
            title = 'Profile picture of ' + str(member)
            color = member.color
            embed = Embed(title=title, color=color)
            embed.set_image(url=pic_url)
            return embed

        if user is None:
            member = ctx.message.author
            embed = get_pfp(member)
            await ctx.send(embed=embed)
        elif len(ctx.message.mentions) > 0:
            member = ctx.message.mentions[0]
            embed = get_pfp(member)
            await ctx.send(embed=embed)
        else:
            lst_members = ctx.guild.members
            # loop to search name
            ind = 0
            found = False
            while found is False and ind < len(lst_members):
                curr_member = lst_members[ind]
                if user.lower() in (curr_member.name.lower() + "#" + curr_member.discriminator.lower()):
                    member = curr_member
                    found = True
                elif user.lower() in curr_member.display_name.lower():
                    member = curr_member
                    found = True
                else:
                    ind += 1
            if found is False:
                await ctx.send("Could not find user named \"" + user + "\" in the server.")
            else:
                embed = get_pfp(member)
                await ctx.send(embed=embed)


    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, 'cog ready')


def setup(bot):
    bot.add_cog(Misc(bot))