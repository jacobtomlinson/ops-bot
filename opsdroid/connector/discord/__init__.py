"""A connector for Discord."""
import logging
from .client import DiscordNoThread

from voluptuous import Required

from opsdroid.connector import Connector, register_event
from opsdroid.events import Message

_LOGGER = logging.getLogger(__name__)
_DISCORD_SEND_URL = "https://discord.com/api"
CONFIG_SCHEMA = {
    Required("token"): str,
    "bot-name": str,
}

class ConnectorDiscord(Connector):

    def __init__(self, config, opsdroid=None):
        """Connector Setup."""
        super().__init__(config, opsdroid=opsdroid)
        _LOGGER.debug("Starting Discord Connector.")
        self.name = config.get("name", "discord")
        self.bot_name = config.get("bot-name", "opsdroid")
        self.token = config["token"]
        self.client = DiscordNoThread(self.token, self.handle_message)
        self.bot_id = None
    
    async def handle_message(self, text,user,user_id,target,msg):
        event = Message(text=text,user=user, user_id=user_id, target=target, connector=self,raw_event=msg)
        _LOGGER.info("-----------------------------------------------"+user+" said "+text)
        await self.opsdroid.parse(event)
    
    async def connect(self):
        await self.client.start()

    async def listen(self):
        """Listen handled by webhooks."""
        pass

    @register_event(Message)
    async def send_message(self, message):
        """Respond with a message."""
        _LOGGER.debug(_("Responding to Discord."))
        await message.target.send(message.text)
    
    async def disconnect(self):
        _LOGGER.debug(_("disconnecting"))
        pr("disconnecting")
        #_LOGGER.debug(_("disconnecting"))
        self.client.close()
        pr("disconnecting done")
        self.client.join()
        # for now, the thread is terminated

def pr(mes):
    with open("D:\Documents\Ecole\\02IMTAtlantique\IDL\debug.txt", "a") as f:
        f.write(mes + "\n")