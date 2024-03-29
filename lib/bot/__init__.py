from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot as BotBase
from discord import Intents
from discord.ext.commands import (
    CommandNotFound,
    BadArgument,
    MissingRequiredArgument,
    CommandOnCooldown,
    MaxConcurrencyReached,
)
from discord.ext.commands import when_mentioned_or
from discord.errors import Forbidden
from discord import TextChannel, DMChannel
from discord import Embed, Permissions, Game
from discord.utils import oauth_url
from glob import glob
from datetime import datetime
from ..db import db

# importing token
import sys

sys.path.append("../../")
from settings import TOKEN


OWNER_ID = 161774631303249921
PERMISSIONS = Permissions()
PERMISSIONS.update(
    add_reactions=True,
    view_audit_log=True,
    view_channel=True,
    send_messages=True,
    manage_messages=True,
    embed_links=True,
    read_message_history=True,
    use_external_emojis=True,
)
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)
COGS_PATH = [
    path.replace("/", ".").replace("\\", ".")[2:-3] for path in glob("./lib/cogs/*.py")
]
DELETED_MESSAGES = {}
EDITED_MESSAGES = {}
DEFAULT_PREFIX = "k!"
# POLL_CHANNELS = {}


def get_prefix(bot, msg):
    prefix = db.get_prefix(msg.guild.id)
    return when_mentioned_or(prefix)(bot, msg)


class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.scheduler = AsyncIOScheduler()

        intents = Intents.default()
        intents.members = True
        intents.presences = True
        intents.guilds = True

        db.autosave(self.scheduler)
        print("running bot...")
        super().__init__(command_prefix=get_prefix, owner_id=OWNER_ID, intents=intents)

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
        if msg.guild is None:
            prefix = DEFAULT_PREFIX
        else:
            prefix = db.get_prefix(msg.guild.id)
        return (
            content.startswith(prefix)
            and content[len(prefix) :].split(" ")[0] in cmd_lst
        )

    def is_start_command(self, msg):
        prefix = db.get_prefix(msg.guild.id)
        return msg.content[len(prefix) :].split(" ")[0] == "start"

    def format_log(self, msg):
        user_name = msg.author.name
        content = msg.clean_content
        channel = msg.channel
        if isinstance(channel, TextChannel):
            channel_name = channel.name
            server_name = msg.guild.name
            server_id = msg.guild.id
        elif isinstance(channel, DMChannel):
            channel_name = channel.recipient.name
            server_name = "DMChannel"
            server_id = ""
        return f"({server_id}) {server_name} | {channel_name} | {user_name} : {content}"

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
            await ctx.send(
                f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in {exc.retry_after:,.2f} secs."
            )
        elif isinstance(exc, MaxConcurrencyReached):
            await ctx.send(
                f"That command can only be used {exc.number} time per {str(exc.per).split('.')[-1]} concurrently."
            )
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
            self.BOT_INVITE_URL = oauth_url(self.user.id, permissions=PERMISSIONS)
            await self.change_presence(activity=Game("@Kingdom help"))
            print("bot ready")
        else:
            print("bot reconnected")

    async def on_message(self, msg):
        # logging
        print(self.format_log(msg))
        # if user calls command but not in database
        userID = msg.author.id
        channel = msg.channel
        if (
            self.is_command(msg)
            and not self.is_start_command(msg)
            and not db.user_exists(userID)
        ):
            await channel.send(
                f"You have not started a Kingdom yet! Use {db.get_prefix(msg.guild.id)}start to get started!"
            )
        elif self.is_command(msg):
            print("processing command...")
            await self.process_commands(msg)

        # poll channel function
        # if msg.channel.id in POLL_CHANNELS:
        #     reactions = POLL_CHANNELS[msg.channel.id]
        #     for reaction in reactions:
        #         await msg.add_reaction(reaction)

    async def on_message_delete(self, msg):
        key = f"{msg.guild.id}{msg.channel.id}"
        value = {
            "content": msg.content,
            "author": f"{msg.author.name}#{msg.author.discriminator}",
            "avatar_url": msg.author.avatar_url,
            "time": msg.created_at,
        }
        DELETED_MESSAGES[key] = value

    async def on_message_edit(self, msg, new_msg):
        key = f"{msg.guild.id}{msg.channel.id}"
        value = {
            "content": msg.content,
            "author": f"{msg.author.name}#{msg.author.discriminator}",
            "avatar_url": msg.author.avatar_url,
            "time": msg.created_at,
        }
        EDITED_MESSAGES[key] = value

    async def on_command(self, ctx):
        if not db.user_exists(ctx.message.author.id):
            await ctx.send(
                f"You have not started a Kingdom yet! Use {db.get_prefix(ctx.message.guild.id)}start to get started!"
            )
            return

    async def on_guild_join(self, guild):
        # notify me when bot joins server
        title = "KingdomBot joined a new server!"
        desc = f"Server name: {guild.name}\nServer ID: {guild.id}\nMember count: {guild.member_count}\nServer owner: {guild.owner}"
        color = 0x4CC417
        embed = Embed(title=title, description=desc, color=color).set_thumbnail(
            url=guild.icon_url
        )
        owner = self.get_user(self.owner_id)
        await owner.send(embed=embed)
        db.add_server(guild.id)
        print(title, desc)

    async def on_guild_remove(self, guild):
        # notify me when bot leaves server
        title = "KingdomBot left a server!"
        desc = f"Server name: {guild.name}\nServer ID: {guild.id}\nMember count: {guild.member_count}\nServer owner: {guild.owner}"
        color = 0xED1C24
        embed = Embed(title=title, description=desc, color=color).set_thumbnail(
            url=guild.icon_url
        )
        owner = self.get_user(self.owner_id)
        await owner.send(embed=embed)
        db.remove_server(guild_id)
        print(title, desc)


bot = Bot()
