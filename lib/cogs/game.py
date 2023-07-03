from discord.ext.commands import Cog
from discord.ext.commands import command, max_concurrency, BucketType
from discord import Embed
from asyncio import TimeoutError

from ..db import db
from ..games.montyhall import MontyHall
from ..games.typeracer import TypeRacer


class Game(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    @max_concurrency(1, per=BucketType.user)
    async def montyhall(self, ctx):
        """
        Play a game of Monty Hall.
        """

        def check_guess(msg):
            return (
                msg.author == ctx.author
                and msg.content in ["1", "2", "3"]
                and msg.channel == ctx.channel
            )

        def check_switch(msg):
            return (
                msg.author == ctx.author
                and msg.content.lower() in ["y", "n"]
                and msg.channel == ctx.channel
            )

        m = MontyHall()
        msg = await ctx.send(f"Choose a package to open (1, 2, 3)\n\n{m.display()}")

        # take guess
        try:
            answer = await self.bot.wait_for("message", check=check_guess, timeout=60)
            answer = int(answer.content)
            m.take_guess(answer)
        except TimeoutError:
            await msg.edit(content=msg.content + "\n\nThe game has timed out!")
            return
        else:
            open_pkg_num = m.reveal_pkg()
            await msg.edit(
                content=f"You've chosen {m.guess}.\n\nPackage {open_pkg_num} has been opened, revealing no coin.\n\nWould you like to switch? (y/n)\n\n{m.display()}"
            )

        # take switch
        try:
            switch = await self.bot.wait_for("message", check=check_switch, timeout=60)
            switch = switch.content.lower()
            m.switch(switch)
        except TimeoutError:
            await msg.edit(content=msg.content + "\n\nThe game has timed out!")
            return
        else:
            m.reveal_all()
            if m.guess == m.coin:
                payment = m.get_payment()
                db.add_balance(ctx.author.id, payment)
                await msg.edit(
                    content=f"You found the coin! You won {payment} coins.\n\n{m.display()}"
                )
            else:
                await msg.edit(
                    content=f"You did not find the coin. Try again!\n\n{m.display()}"
                )

    @command(usage="[number of words]")
    @max_concurrency(1, per=BucketType.channel)
    async def typeracer(self, ctx, num_words: int = 5):
        """
        Play Typeracer.
        Number of words defaults to 5 if not specified.
        """
        if num_words > 25 or num_words < 1:
            await ctx.send("Number of words must be between 1 and 25!")
            return

        def check_answer(msg):
            return (
                msg.content == t.get_word() or msg.content == t.get_word_display()
            ) and msg.channel == ctx.channel

        def pay_players(scoreboard):
            for userID in scoreboard.keys():
                payment = scoreboard[userID]["payment"]
                db.add_balance(userID, payment)

        async def end_game(ctx, scoreboard):
            if scoreboard:
                pay_players(scoreboard)
                embed = t.get_scoreboard_embed()
                await ctx.send(embed=embed)

        await ctx.send(f"Generating a list of {num_words} words...")
        t = TypeRacer(num_words)
        await ctx.send("*The race has started!\nThe word to type is...*")

        while not t.game_over():
            embed = t.get_word_embed()
            msg = await ctx.send(embed=embed)
            # take answer
            try:
                answer = await self.bot.wait_for(
                    "message", check=check_answer, timeout=25
                )
            except TimeoutError:
                await msg.edit(content=msg.content + "\n\nThe game has timed out!")
                await end_game(ctx, t.get_scoreboard())
                return
            else:
                if t.is_correct(answer.content):
                    embed = t.process_answer(answer)
                    await msg.edit(embed=embed)
                elif t.is_copypaste(answer.content):
                    await ctx.send(
                        f"{answer.author.mention} Please don't copy and paste the word!"
                    )

        # paying players & displaying scoreboard
        await end_game(ctx, t.get_scoreboard())

    @Cog.listener()
    async def on_ready(self):
        print(self.__class__.__name__, "cog ready")


def setup(bot):
    bot.add_cog(Game(bot))
