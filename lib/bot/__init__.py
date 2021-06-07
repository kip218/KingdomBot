from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot as BotBase
from discord import Intents
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown, MaxConcurrencyReached)
from discord.errors import Forbidden
from discord import (TextChannel, DMChannel)
from glob import glob
from datetime import datetime
from ..db import db

#importing token
import sys
sys.path.append('../../')
from settings import TOKEN


PREFIX = "k!"
OWNER_IDS = [161774631303249921]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)
COGS_PATH = [path.replace('/','.')[2:-3] for path in glob("./lib/cogs/*.py")]


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.scheduler = AsyncIOScheduler()

        intents = Intents.default()
        intents.members = True
        intents.presences = True

        db.autosave(self.scheduler)
        print("running bot...")
        super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS, intents=intents)


    def setup(self):
        for cog_path in COGS_PATH:
            self.load_extension(cog_path)
            print(f"{cog_path.split('.')[-1]} cog loaded")
        print("setup complete")


    def run(self, version):
        self.VERSION = version
        self.TOKEN = TOKEN
        print("running setup...")
        self.setup()
        super().run(self.TOKEN)


    async def on_connect(self):
        print("bot connected")


    async def on_disconnect(self):
        print("bot disconnected")


    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")
        print("An error occured.")
        raise


    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("One or more required arguments are missing.")
        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in {exc.retry_after:,.2f} secs.")
        elif isinstance(exc, MaxConcurrencyReached):
            await ctx.send(f"That command can only be used {exc.number} time per {str(exc.per).split('.')[-1]} concurrently.")
        elif hasattr(exc, "original"):
            if isinstance(exc.original, Forbidden):
                await ctx.send("I do not have permission to do that.")
            else:
                raise exc.original
        else:
            raise exc


    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.launch_time = datetime.utcnow()
            self.scheduler.start()
            print("bot ready")
        else:
            print("bot reconnected")


    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)
        #logging
        user = message.author.name
        msg = message.clean_content
        if isinstance(message.channel, TextChannel):
            channel = message.channel.name
            server = message.guild.name
        elif isinstance(message.channel, DMChannel):
            channel = message.channel.recipient.name
            server = "DMChannel"
        print(server + "| " + channel + "| " + user + ": " + msg)


bot = Bot()