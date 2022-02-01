from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.tasks import loop
from discord import Embed
from random import randint
from udpy import UrbanClient
from datetime import datetime, timedelta
import asyncio
import re

from ..db import db
from .. import bot
DELETED_MESSAGES = bot.DELETED_MESSAGES
EDITED_MESSAGES = bot.EDITED_MESSAGES
POLL_CHANNELS = bot.POLL_CHANNELS


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()


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
        await ctx.send(f"8{'='*n}D")


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
        <time> should be formatted as "dd:hh:mm:ss".
        Can keep track of up to 30 days.
        '''
        def getSec(s):
            l = list(map(int, s.split(':')))
            return sum(n * sec for n, sec in zip(l[::-1], (1, 60, 3600, 86400)))

        TIME_REGEX = re.compile(r"/(([0-2]?\d|30):([0-1]?\d|2[0-3]):([0-5]?\d):([0-5]?\d)$)|(([0-1]?\d|2[0-3]):([0-5]?\d):([0-5]?\d)$)|(([0-5]?\d):([0-5]?\d)$)|(([0-5]?\d)$)/gm")
        match = TIME_REGEX.match(time)

        if not match:
            await ctx.send("Please enter a valid time. Time should be formatted as 'dd:hh:mm:ss'.")
            return

        d, h, m, s = 0, 0, 0, 0
        l = time.split(':')
        if l: s = l.pop()
        if l: m = l.pop()
        if l: h = l.pop()
        if l: d = d.pop()

        seconds = getSec(match.group())
        now = datetime.utcnow()
        reminderTime = now + timedelta(seconds=seconds)
        reminderID = int(str(int(now.timestamp()))[-9:] + str(int(reminderTime.timestamp()))[-9:])

        db.add_reminder(reminderID, task, reminderTime, ctx.author.id)
        await ctx.send(f"{ctx.author.mention} I will remind you of `{task}` after {d}d {h}h {m}m {s}s.")


    @loop(seconds=60)
    async def check_reminders(self):
        reminders = db.get_reminders(datetime.utcnow())
        for reminder in reminders:
            reminderID, task, userID = reminder[0], reminder[1], reminder[2]
            user = await self.bot.fetch_user(userID)
            if user.dm_channel is None:
                await user.create_dm()
            await user.dm_channel.send(f"**Reminder:**\n`{task}`")
            db.remove_reminder(reminderID)


    @command()
    async def avatar(self, ctx, *, user: str=None):
        '''
        [user]'s profile picture. Sends your profile picture if [user] not specified.
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

    @command()
    async def poll(self, ctx, channel):
        '''
        Set the bot to automatically react to all messages in <channel> with specific set of reactions.
        Prompt will be shown after the initial command.
        '''
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("Only server admins can use this command!")
            return
        if not ctx.message.channel_mentions:
            await ctx.send("You must mention a channel to set up the poll.")
            return

        channel = ctx.message.channel_mentions[0]
        prompt = await ctx.send(f"Configuring {channel.mention} as poll channel. React to this message with a set of reactions needed for poll. Type 'done' when you're done reacting.")

        def check_author(msg):
            return msg.author == ctx.author and msg.content == 'done'
        
        try:
            done = await self.bot.wait_for('message', check=check_author, timeout=60)
        except TimeoutError:
            await ctx.message.edit(content=ctx.message.content + "\n\nThe prompt has timed out!")
            return

        emoji_lst = []
        prompt = await prompt.channel.fetch_message(prompt.id)
        for reaction in prompt.reactions:
            users = await reaction.users().flatten()
            if ctx.author in users:
                emoji_lst.append(reaction.emoji)

        POLL_CHANNELS[channel.id] = emoji_lst
        await ctx.send(f"{channel.mention} has been configured as a poll channel.")



    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, 'cog ready')


def setup(bot):
    bot.add_cog(Misc(bot))