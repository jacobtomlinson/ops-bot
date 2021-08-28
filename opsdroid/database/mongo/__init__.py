# -*- coding: utf-8 -*-
"""A module for opsdroid to allow persist in mongo database."""
import logging
from contextlib import contextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from voluptuous import Any

from opsdroid.database import Database

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = {
    "host": str,
    "port": Any(int, str),
    "database": str,
    "user": str,
    "password": str,
    "collection": str,
}


class DatabaseMongo(Database):
    """A module for opsdroid to allow memory to persist in a mongo database."""

    def __init__(self, config, opsdroid=None):
        """Create the connection.

        Set some basic properties from the database config such as the name
        of this database.

        Args:
            config (dict): The config for this database specified in the
                           `configuration.yaml` file.
             opsdroid (OpsDroid): An instance of opsdroid.core.

        """
        super().__init__(config, opsdroid=opsdroid)
        _LOGGER.debug("Loaded mongo database connector.")
        self.name = "mongo"
        self.config = config
        self.client = None
        self.database = None
        self.collection = config.get("collection", "opsdroid")

    async def connect(self):
        """Connect to the database."""
        host = self.config.get("host", "localhost")
        port = self.config.get("port", "27017")
        database = self.config.get("database", "opsdroid")
        user = self.config.get("user")
        pwd = self.config.get("password")
        if user and pwd:
            path = "mongodb://{user}:{pwd}@{host}:{port}".format(
                user=user, pwd=pwd, host=host, port=port
            )
        else:
            path = "mongodb://{host}:{port}".format(host=host, port=port)
        self.client = AsyncIOMotorClient(path)
        self.database = self.client[database]
        _LOGGER.info("Connected to MongoDB.")

    async def put(self, key, data):
        """Insert or replace an object into the database for a given key.

        Args:
            key (str): the key is the databasename
            data (object): the data to be inserted or replaced

        """
        _LOGGER.debug("Putting %s into MongoDB collection %s", key, self.collection)

        if isinstance(data, str):
            data = {"value": data}
        if "key" not in data:
            data["key"] = key

        response = await self.database[self.collection].update_one(
            {"key": data["key"]}, {"$set": data}
        )
        if bool(response) and response.raw_result["updatedExisting"]:
            return response

        return await self.database[self.collection].insert_one(data)

    async def get(self, key):
        """Get a document from the database (key).

        Args:
            key (str): the key is the database name.

        """
        _LOGGER.debug("Getting %s from MongoDB collection %s", key, self.collection)

        response = await self.database[self.collection].find_one(
            {"$query": {"key": key}, "$orderby": {"$natural": -1}}
        )
        if response.keys() == {"_id", "key", "value"}:
            response = response["value"]
        return response

    async def delete(self, key):
        """Delete a document from the database (key).

        Args:
            key (str): the key is the database name.

        """
        _LOGGER.debug("Deleting %s from MongoDB collection %s.", key, self.collection)

        return await self.database[self.collection].delete_one({"key": key})

    @contextmanager
    def memory_in_collection(self, collection):
        """Use collection state in the given collection rather than the default."""
        original_collection = self.collection
        self.collection = collection
        yield
        self.collection = original_collection
