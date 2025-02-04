import asyncio
import logging.handlers
import os

import discord
from discord.ext import commands


from cogs.TicketingSystem import TicketLauncher, TicketInternals
from functions import checkDirectoryExists, getCurrentDateTime, ensureTicketingJSON_Exists

# Credits
__author__ = "Andrew Martin"
__version__ = "1.0"
__maintainer__ = "Andrew Martin"
__email__ = "apmartin@mtu.edu"
__status__ = "Production"


# HuskyBot constructor class
class CreateBot(commands.Bot):
    def __init__(self):
        # Specifies intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        intents.members = True
        super().__init__(command_prefix="/", intents=intents,
                         activity=discord.Activity(type=discord.ActivityType.watching, name='over the universe'),
                         status=discord.Status.do_not_disturb)

    async def setup_hook(self) -> None:
        print("HuskyBot spinning up...\n-----")

    async def on_ready(self):
        self.add_view(TicketLauncher())
        self.add_view(TicketInternals())
        print(f'We have successfully logged in as {self.user} on {getCurrentDateTime()}.\n-----')


HuskyBot = CreateBot()

# Defines the initial_extensions array
initial_extensions = []

# Logging setup / parameters
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logHandler = logging.FileHandler(filename='HuskyBot.log', encoding='utf-8', mode='w')
loggingDateFormat = '%Y-%m-%d %H:%M:%S'
loggingFormatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', loggingDateFormat, style='{')
logHandler.setFormatter(loggingFormatter)
logger.addHandler(logHandler)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        initial_extensions.append('cogs.' + filename[:-3])


async def main():
    # Ensures the all the needed working directories exist
    checkDirectoryExists('WorkingFiles/')
    checkDirectoryExists('WorkingFiles/FilesToCreate/')
    checkDirectoryExists('WorkingFiles/Databases/')
    ensureTicketingJSON_Exists()

    # Loads all cogs
    for extension in initial_extensions:
        await HuskyBot.load_extension(extension)

# returns the discord API key for logging into discord
def get_api_key():
    # get api key from docker secrets
    if os.path.exists("/run/secrets/apiKey"):
        api_key = open("/run/secrets/apiKey").encoding("uft-8").readline()
    elif os.getenv("apiKey") is not None:
        api_key = os.getenv("apiKey")
    return api_key


if __name__ == '__main__':
    asyncio.run(main())
try:
    HuskyBot.run(get_api_key(), log_handler=None)
except discord.LoginFailure:
    logging.fatal("API Key not supplied or incorrect, please make a docker secret for the api key")
    