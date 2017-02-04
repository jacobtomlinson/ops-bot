"""Submodule to handle web requests in opsdroid."""

import json
import logging
from datetime import datetime

from aiohttp import web

from opsdroid.const import __version__


_LOGGER = logging.getLogger(__name__)


class Web:
    """Web server for opsdroid."""

    def __init__(self, opsdroid):
        """Setup web object."""
        self.opsdroid = opsdroid
        try:
            self.config = self.opsdroid.config["web"]
        except KeyError:
            self.config = {}
        self.web_app = web.Application(loop=self.opsdroid.eventloop)
        self.web_app.router.add_get('/', self.web_index_handler)
        self.web_app.router.add_get('', self.web_index_handler)
        self.web_app.router.add_get('/stats', self.web_stats_handler)
        self.web_app.router.add_get('/stats/', self.web_stats_handler)

    @property
    def get_port(self):
        """Return port from config or the default."""
        try:
            port = self.config["port"]
        except KeyError:
            port = 8080
        return port

    @property
    def get_host(self):
        """Return host from config or the default."""
        try:
            host = self.config["host"]
        except KeyError:
            host = '127.0.0.1'
        return host

    def start(self):
        """Start web servers."""
        _LOGGER.debug(
            "Starting web server with host %s and port %s",
            self.get_host, self.get_port)
        web.run_app(self.web_app, host=self.get_host,
                    port=self.get_port, print=_LOGGER.info)

    @staticmethod
    def build_response(status, result):
        """Build a json response object."""
        return web.Response(text=json.dumps({
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "result": result
        }))

    def web_index_handler(self, request):
        """Handle root web request."""
        return self.build_response(200, {
            "message": "Welcome to the opsdroid API"})

    def web_stats_handler(self, request):
        """Handle stats request."""
        return self.build_response(200, {
            "version": __version__,
            "messages": {
                "total_parsed": self.opsdroid.stats["messages_parsed"],
                "webhooks_called": self.opsdroid.stats["webhooks_called"]
            },
            "modules": {
                "skills": len(self.opsdroid.skills),
                "connectors": len(self.opsdroid.connectors),
                "databases": len(self.opsdroid.memory.databases)
            }
        })
