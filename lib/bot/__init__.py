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


    def is_command(self, msg):
        content = msg.content
        cmd_lst = [cmd.name for cmd in self.commands]
        return content.startswith(self.PREFIX) and content[len(self.PREFIX):].split(' ')[0] in cmd_lst


    def is_start_command(self, msg):
        return msg.content[len(self.PREFIX):].split(' ')[0] == 'start'


    def format_log(self, msg):
        user_name = msg.author.name
        content = msg.clean_content
        channel = msg.channel
        if isinstance(channel, TextChannel):
            channel_name = channel.name
            server_name = msg.guild.name
        elif isinstance(channel, DMChannel):
            channel_name = channel.recipient.name
            server_name = "DMChannel"
        return server_name + "| " + channel_name + "| " + user_name + ": " + content


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


    async def on_message(self, msg):
        #logging
        print(self.format_log(msg))
        #if user calls command but not in database
        userID = msg.author.id
        channel = msg.channel
        if self.is_command(msg) and not self.is_start_command(msg) and not db.user_exists(userID):
            await channel.send(f"You have not started a Kingdom yet! Use {self.PREFIX}start to get started!")
        else:
            print("processing command...")
            await self.process_commands(msg)


    async def on_command(self, ctx):
        if not db.user_exists(ctx.message.author.id):
            await ctx.send(f"You have not started a Kingdom yet! Use {self.PREFIX}start to get started!")


bot = Bot()