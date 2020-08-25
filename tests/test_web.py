"""Test the opsdroid web."""
import ssl

import pytest

import asynctest
import asynctest.mock as amock

from opsdroid.cli.start import configure_lang
from opsdroid.core import OpsDroid
from opsdroid import web
import aiohttp.web

configure_lang({})


async def test_web():
    """Create a web object and check the config."""
    with OpsDroid() as opsdroid:
        app = web.Web(opsdroid)
        assert app.config == {}


async def test_web_get_port():
    """Check the port getter."""
    with OpsDroid() as opsdroid:
        opsdroid.config["web"] = {}
        app = web.Web(opsdroid)
        assert app.get_port == 8080

        opsdroid.config["web"] = {"port": 8000}
        app = web.Web(opsdroid)
        assert app.get_port == 8000


async def test_web_get_host():
    """Check the host getter."""
    with OpsDroid() as opsdroid:
        opsdroid.config["web"] = {}
        app = web.Web(opsdroid)
        assert app.get_host == "0.0.0.0"

        opsdroid.config["web"] = {"host": "127.0.0.1"}
        app = web.Web(opsdroid)
        assert app.get_host == "127.0.0.1"


async def test_web_get_ssl():
    """Check the host getter."""
    with OpsDroid() as opsdroid:
        opsdroid.config["web"] = {}
        app = web.Web(opsdroid)
        assert app.get_ssl_context == None

        opsdroid.config["web"] = {
            "ssl": {"cert": "tests/ssl/cert.pem", "key": "tests/ssl/key.pem"}
        }
        app = web.Web(opsdroid)
        assert type(app.get_ssl_context) == type(ssl.SSLContext(ssl.PROTOCOL_SSLv23))
        assert app.get_port == 8443

        opsdroid.config["web"] = {
            "ssl": {
                "cert": "/path/to/nonexistant/cert",
                "key": "/path/to/nonexistant/key",
            }
        }
        app = web.Web(opsdroid)
        assert app.get_ssl_context == None


async def test_web_build_response():
    """Check the response builder."""
    with OpsDroid() as opsdroid:
        opsdroid.config["web"] = {}
        app = web.Web(opsdroid)
        response = {"test": "test"}
        resp = app.build_response(200, response)
        assert type(resp) == aiohttp.web.Response


async def test_web_index_handler():
    """Check the index handler."""
    with OpsDroid() as opsdroid:
        opsdroid.config["web"] = {}
        app = web.Web(opsdroid)
        assert type(await app.web_index_handler(None)) == aiohttp.web.Response


async def test_web_stats_handler():
    """Check the stats handler."""
    with OpsDroid() as opsdroid:
        opsdroid.config["web"] = {}
        app = web.Web(opsdroid)
        assert type(await app.web_stats_handler(None)) == aiohttp.web.Response


async def test_web_start():
    """Check the stats handler."""
    with OpsDroid() as opsdroid:
        with amock.patch("aiohttp.web.AppRunner.setup") as mock_runner, amock.patch(
            "aiohttp.web.TCPSite.__init__"
        ) as mock_tcpsite, amock.patch(
            "aiohttp.web.TCPSite.start"
        ) as mock_tcpsite_start:
            mock_tcpsite.return_value = None
            app = web.Web(opsdroid)
            await app.start()
            assert mock_runner.called
            assert mock_tcpsite.called
            assert mock_tcpsite_start.called


async def test_web_stop():
    """Check the stats handler."""
    with OpsDroid() as opsdroid:
        app = web.Web(opsdroid)
        app.runner = amock.CoroutineMock()
        app.runner.cleanup = amock.CoroutineMock()
        await app.stop()
        assert app.runner.cleanup.called
