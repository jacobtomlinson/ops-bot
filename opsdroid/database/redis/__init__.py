"""Module for storing data within Redis."""
import json
import logging

import aioredis
from aioredis import parser

from opsdroid.database import Database
from opsdroid.helper import JSONEncoder, JSONDecoder

_LOGGER = logging.getLogger(__name__)


class RedisDatabase(Database):
    """Database class for storing data within a Redis instance."""

    def __init__(self, config, opsdroid=None):
        """Initialise the sqlite database.

        Set basic properties of the database. Initialise properties like
        name, connection arguments, database file, table name and config.

        Args:
            config (dict): The configuration of the database which consists
                           of `file` and `table` name of the sqlite database
                           specified in `configuration.yaml` file.

        """
        super().__init__(config, opsdroid=opsdroid)
        self.config = config
        self.client = None
        self.host = self.config.get("host", "localhost")
        self.port = self.config.get("port", 6379)
        self.database = self.config.get("database", 0)
        self.password = self.config.get("password", None)
        _LOGGER.debug(_("Loaded redis database connector."))

    async def connect(self):
        """Connect to the database.

        This method will connect to a Redis database. By default it will
        connect to Redis on localhost on port 6379

        """
        try:
            self.client = await aioredis.create_pool(
                address=(self.host, int(self.port)),
                db=self.database,
                password=self.password,
                parser=parser.PyReader,
            )

            _LOGGER.info(
                _("Connected to redis database %s from %s on port %s"),
                self.database,
                self.host,
                self.port,
            )
        except OSError:
            _LOGGER.warning(
                _("Unable to connect to redis database on address: %s port: %s"),
                self.host,
                self.port,
            )

    async def put(self, key, data):
        """Store the data object in Redis against the key.

        Args:
            key (string): The key to store the data object under.
            data (object): The data object to store.

        """
        if self.client:
            _LOGGER.debug(_("Putting %s into redis"), key)
            await self.client.execute("SET", key, json.dumps(data, cls=JSONEncoder))

    async def get(self, key):
        """Get data from Redis for a given key.

        Args:
            key (string): The key to lookup in the database.

        Returns:
            object or None: The data object stored for that key, or None if no
                            object found for that key.

        """
        if self.client:
            _LOGGER.debug(_("Getting %s from redis"), key)
            data = await self.client.execute("GET", key)

            if data:
                return json.loads(data, encoding=JSONDecoder)

            return None

    async def disconnect(self):
        """Disconnect from the database."""
        if self.client:
            self.client.close()
