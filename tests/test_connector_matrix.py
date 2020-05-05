"""Tests for the ConnectorMatrix class."""
import asyncio
from unittest import mock
from copy import deepcopy
import json

import aiohttp
import asynctest
import asynctest.mock as amock
from matrix_api_async import AsyncHTTPAPI
from matrix_client.errors import MatrixRequestError

import opsdroid.connector.matrix.events as matrix_events
from opsdroid.core import OpsDroid
from opsdroid import events
from opsdroid.connector.matrix import ConnectorMatrix
from opsdroid.connector.matrix.create_events import MatrixEventCreator
from opsdroid.cli.start import configure_lang  # noqa

api_string = "matrix_api_async.AsyncHTTPAPI.{}"


def setup_connector():
    """Initiate a basic connector setup for testing on"""
    connector = ConnectorMatrix(
        {
            "rooms": {"main": "#test:localhost"},
            "mxid": "@opsdroid:localhost",
            "password": "hello",
            "homeserver": "http://localhost:8008",
        }
    )
    return connector


class TestConnectorMatrixAsync(asynctest.TestCase):
    """Test the async methods of the opsdroid Matrix connector class."""

    @property
    def sync_return(self):
        """Define some mock json to return from the sync method"""
        return {
            "account_data": {"events": []},
            "device_lists": {"changed": [], "left": []},
            "device_one_time_keys_count": {"signed_curve25519": 50},
            "groups": {"invite": {}, "join": {}, "leave": {}},
            "next_batch": "s801873745",
            "presence": {"events": []},
            "rooms": {
                "invite": {},
                "join": {
                    "!aroomid:localhost": {
                        "account_data": {"events": []},
                        "ephemeral": {"events": []},
                        "state": {"events": []},
                        "summary": {},
                        "timeline": {
                            "events": [
                                {
                                    "content": {
                                        "body": "LOUD NOISES",
                                        "msgtype": "m.text",
                                    },
                                    "event_id": "$eventid:localhost",
                                    "origin_server_ts": 1547124373956,
                                    "sender": "@cadair:cadair.com",
                                    "type": "m.room.message",
                                    "unsigned": {"age": 3498},
                                }
                            ],
                            "limited": False,
                            "prev_batch": "s801873709",
                        },
                        "unread_notifications": {
                            "highlight_count": 0,
                            "notification_count": 0,
                        },
                    }
                },
                "leave": {},
            },
            "to_device": {"events": []},
        }

    @property
    def sync_invite(self):
        return {
            "account_data": {"events": []},
            "to_device": {"events": []},
            "device_one_time_keys_count": {},
            "rooms": {
                "invite": {
                    "!AWtmOvkBPTCSPbdaHn:localhost": {
                        "invite_state": {
                            "events": [
                                {
                                    "state_key": "@neo:matrix.org",
                                    "content": {
                                        "avatar_url": None,
                                        "membership": "join",
                                        "displayname": "stuart",
                                    },
                                    "sender": "@neo:matrix.org",
                                    "type": "m.room.member",
                                },
                                {
                                    "state_key": "",
                                    "content": {"join_rule": "invite"},
                                    "sender": "@neo:matrix.org",
                                    "type": "m.room.join_rules",
                                },
                                {
                                    "event_id": "$tibhPrUV0GJbb3-7Iad_LuYzTnB2vcdf4wBbHNXkQMc",
                                    "sender": "@neo:matrix.org",
                                    "content": {
                                        "avatar_url": None,
                                        "membership": "invite",
                                        "is_direct": True,
                                        "displayname": "Opsdroid",
                                    },
                                    "unsigned": {"age": 150},
                                    "type": "m.room.member",
                                    "state_key": "@opsdroid:opsdroid.dev",
                                    "origin_server_ts": 1575509408883,
                                },
                            ]
                        }
                    }
                },
                "join": {},
                "leave": {},
            },
            "groups": {"invite": {}, "join": {}, "leave": {}},
            "next_batch": "s110_1482_2_21_3_1_1_39_1",
            "device_lists": {"left": [], "changed": []},
            "presence": {"events": []},
        }

    def setUp(self):
        """Basic setting up for tests"""
        self.connector = setup_connector()
        self.api = AsyncHTTPAPI("https://notaurl.com", None)
        self.connector.connection = self.api

    async def test_make_filter(self):
        with amock.patch(api_string.format("create_filter")) as patched_filter:
            patched_filter.return_value = asyncio.Future()
            patched_filter.return_value.set_result({"filter_id": "arbitrary string"})
            filter_id = await self.connector.make_filter(self.api)
            assert filter_id == "arbitrary string"

            assert patched_filter.called
            assert patched_filter.call_args[1]["user_id"] == "@opsdroid:localhost"

    async def test_connect(self):
        with amock.patch(api_string.format("login")) as patched_login, amock.patch(
            api_string.format("join_room")
        ) as patched_join_room, amock.patch(
            api_string.format("create_filter")
        ) as patched_filter, amock.patch(
            api_string.format("sync")
        ) as patched_sync, amock.patch(
            api_string.format("get_display_name")
        ) as patched_get_nick, amock.patch(
            api_string.format("set_display_name")
        ) as patch_set_nick, amock.patch(
            "aiohttp.ClientSession"
        ) as patch_cs, OpsDroid() as _:

            # Skip actually creating a client session
            patch_cs.return_value = amock.MagicMock()

            patched_login.return_value = asyncio.Future()
            patched_login.return_value.set_result({"access_token": "arbitrary string1"})

            patched_join_room.return_value = asyncio.Future()
            patched_join_room.return_value.set_result({"room_id": "!aroomid:localhost"})

            patched_filter.return_value = asyncio.Future()
            patched_filter.return_value.set_result({"filter_id": "arbitrary string"})

            patched_sync.return_value = asyncio.Future()
            patched_sync.return_value.set_result({"next_batch": "arbitrary string2"})

            await self.connector.connect()

            assert "!aroomid:localhost" in self.connector.room_ids.values()

            assert self.connector.connection.token == "arbitrary string1"

            assert self.connector.filter_id == "arbitrary string"

            assert self.connector.connection.sync_token == "arbitrary string2"

            self.connector.nick = "Rabbit Hole"

            patched_get_nick.return_value = asyncio.Future()
            patched_get_nick.return_value.set_result("Rabbit Hole")

            await self.connector.connect()

            assert patched_get_nick.called
            assert not patch_set_nick.called

            patched_get_nick.return_value = asyncio.Future()
            patched_get_nick.return_value.set_result("Neo")

            self.connector.mxid = "@morpheus:matrix.org"

            await self.connector.connect()

            assert patched_get_nick.called
            patch_set_nick.assert_called_once_with(
                "@morpheus:matrix.org", "Rabbit Hole"
            )

    async def test_parse_sync_response(self):
        self.connector.room_ids = {"main": "!aroomid:localhost"}
        self.connector.filter_id = "arbitrary string"

        with amock.patch(api_string.format("get_display_name")) as patched_name:
            patched_name.return_value = asyncio.Future()
            patched_name.return_value.set_result("SomeUsersName")

            returned_message = await self.connector._parse_sync_response(
                self.sync_return
            )

            assert returned_message.text == "LOUD NOISES"
            assert returned_message.user == "SomeUsersName"
            assert returned_message.target == "!aroomid:localhost"
            assert returned_message.connector == self.connector
            raw_message = self.sync_return["rooms"]["join"]["!aroomid:localhost"][
                "timeline"
            ]["events"][0]
            assert returned_message.raw_event == raw_message

    async def test_sync_parse_invites(self):
        with amock.patch(api_string.format("get_display_name")) as patched_name:
            self.connector.opsdroid = amock.MagicMock()
            self.connector.opsdroid.parse.return_value = asyncio.Future()
            self.connector.opsdroid.parse.return_value.set_result("")
            patched_name.return_value = asyncio.Future()
            patched_name.return_value.set_result("SomeUsersName")

            await self.connector._parse_sync_response(self.sync_invite)

            (invite,), _ = self.connector.opsdroid.parse.call_args

            assert invite.target == "!AWtmOvkBPTCSPbdaHn:localhost"
            assert invite.user == "SomeUsersName"
            assert invite.user_id == "@neo:matrix.org"
            assert invite.connector is self.connector

    async def test_get_nick(self):
        self.connector.room_specific_nicks = True

        with amock.patch(
            api_string.format("get_room_displayname")
        ) as patched_roomname, amock.patch(
            api_string.format("get_display_name")
        ) as patched_globname:
            patched_roomname.return_value = asyncio.Future()
            patched_roomname.return_value.set_result("")

            mxid = "@notaperson:matrix.org"
            assert await self.connector.get_nick("#notaroom:localhost", mxid) == ""
            # Test if a room displayname couldn't be found
            patched_roomname.side_effect = Exception()

            # Test if that leads to a global displayname being returned
            patched_globname.return_value = asyncio.Future()
            patched_globname.return_value.set_result("@notaperson")
            assert (
                await self.connector.get_nick("#notaroom:localhost", mxid)
                == "@notaperson"
            )

            # Test that failed nickname lookup returns the mxid
            patched_globname.side_effect = MatrixRequestError()
            assert await self.connector.get_nick("#notaroom:localhost", mxid) == mxid

    async def test_get_formatted_message_body(self):
        original_html = "<p><h3><no>Hello World</no></h3></p>"
        original_body = "### Hello World"
        message = self.connector._get_formatted_message_body(original_html)
        assert message["formatted_body"] == "<h3>Hello World</h3>"
        assert message["body"] == "Hello World"

        message = self.connector._get_formatted_message_body(
            original_html, original_body
        )
        assert message["formatted_body"] == "<h3>Hello World</h3>"
        assert message["body"] == "### Hello World"

    async def _get_message(self):
        self.connector.room_ids = {"main": "!aroomid:localhost"}
        self.connector.filter_id = "arbitrary string"
        m = "opsdroid.connector.matrix.ConnectorMatrix.get_nick"

        with amock.patch(m) as patched_nick:
            patched_nick.return_value = asyncio.Future()
            patched_nick.return_value.set_result("Neo")

            return await self.connector._parse_sync_response(self.sync_return)

    async def test_send_edited_message(self):
        message = events.EditedMessage(
            text="New message",
            target="!test:localhost",
            linked_event=events.Message("hello", event_id="$hello"),
            connector=self.connector,
        )
        with amock.patch(
            api_string.format("send_message_event")
        ) as patched_send, OpsDroid() as _:
            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result({})

            new_content = self.connector._get_formatted_message_body(message.text)
            content = {
                "msgtype": "m.text",
                "m.new_content": new_content,
                "body": f"* {new_content['body']}",
                "m.relates_to": {
                    "rel_type": "m.replace",
                    "event_id": message.linked_event.event_id,
                },
            }

            await self.connector.send(message)

            patched_send.assert_called_once_with(
                message.target, "m.room.message", content
            )

            # Test linked event as event id
            message.linked_event = "$hello"

            await self.connector.send(message)

            patched_send.assert_called_with(message.target, "m.room.message", content)

            # Test responding to an edit
            await message.respond(events.EditedMessage("hello"))

            patched_send.assert_called_with(message.target, "m.room.message", content)

    async def test_respond_retry(self):
        message = await self._get_message()
        with amock.patch(api_string.format("send_message_event")) as patched_send:
            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result(None)
            await self.connector.send(message)

            message_obj = self.connector._get_formatted_message_body(message.text)
            patched_send.assert_called_once_with(
                message.target, "m.room.message", message_obj
            )

            patched_send.side_effect = [
                aiohttp.client_exceptions.ServerDisconnectedError(),
                patched_send.return_value,
            ]

            await self.connector.send(message)

            message_obj = self.connector._get_formatted_message_body(message.text)
            patched_send.assert_called_with(
                message.target, "m.room.message", message_obj
            )

    async def test_respond_room(self):
        message = await self._get_message()
        with amock.patch(
            api_string.format("send_message_event")
        ) as patched_send, amock.patch(
            api_string.format("get_room_id")
        ) as patched_room_id:

            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result(None)

            patched_room_id.return_value = asyncio.Future()
            patched_room_id.return_value.set_result(message.target)

            message.target = "main"
            await self.connector.send(message)

            message_obj = self.connector._get_formatted_message_body(message.text)
            patched_send.assert_called_once_with(
                "!aroomid:localhost", "m.room.message", message_obj
            )

    async def test_disconnect(self):
        self.connector.session = amock.MagicMock()
        self.connector.session.close = amock.CoroutineMock()
        await self.connector.disconnect()
        assert self.connector.session.close.called

    def test_get_roomname(self):
        self.connector.rooms = {
            "main": {"alias": "#notthisroom:localhost"},
            "test": {"alias": "#thisroom:localhost"},
        }
        self.connector.room_ids = dict(
            zip(
                self.connector.rooms.keys(),
                ["!aroomid:localhost", "!anotherroomid:localhost"],
            )
        )

        assert self.connector.get_roomname("#thisroom:localhost") == "test"
        assert self.connector.get_roomname("!aroomid:localhost") == "main"
        assert self.connector.get_roomname("someroom") == "someroom"

    def test_lookup_target(self):
        self.connector.room_ids = {"main": "!aroomid:localhost"}

        assert self.connector.lookup_target("main") == "!aroomid:localhost"
        assert self.connector.lookup_target("#test:localhost") == "!aroomid:localhost"
        assert (
            self.connector.lookup_target("!aroomid:localhost") == "!aroomid:localhost"
        )

    async def test_respond_image(self):
        gif_bytes = (
            b"GIF89a\x01\x00\x01\x00\x00\xff\x00,"
            b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;"
        )

        image = events.Image(file_bytes=gif_bytes, target="!test:localhost")
        with amock.patch(
            api_string.format("send_content")
        ) as patched_send, amock.patch(
            api_string.format("media_upload")
        ) as patched_upload:

            patched_upload.return_value = asyncio.Future()
            patched_upload.return_value.set_result({"content_uri": "mxc://aurl"})

            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result(None)
            await self.connector.send(image)

            patched_send.assert_called_once_with(
                "!test:localhost",
                "mxc://aurl",
                "opsdroid_upload",
                "m.image",
                {"w": 1, "h": 1, "mimetype": "image/gif", "size": 26},
            )

    async def test_respond_mxc(self):
        gif_bytes = (
            b"GIF89a\x01\x00\x01\x00\x00\xff\x00,"
            b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;"
        )

        image = events.Image(url="mxc://aurl", target="!test:localhost")
        with amock.patch(
            api_string.format("send_content")
        ) as patched_send, amock.patch(
            "opsdroid.events.Image.get_file_bytes"
        ) as patched_bytes:

            patched_bytes.return_value = asyncio.Future()
            patched_bytes.return_value.set_result(gif_bytes)

            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result(None)
            await self.connector.send(image)

            patched_send.assert_called_once_with(
                "!test:localhost", "mxc://aurl", "opsdroid_upload", "m.image", {}
            )

    async def test_respond_file(self):
        file_event = events.File(
            file_bytes=b"aslkdjlaksdjlkajdlk", target="!test:localhost"
        )
        with amock.patch(
            api_string.format("send_content")
        ) as patched_send, amock.patch(
            api_string.format("media_upload")
        ) as patched_upload:

            patched_upload.return_value = asyncio.Future()
            patched_upload.return_value.set_result({"content_uri": "mxc://aurl"})

            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result(None)
            await self.connector.send(file_event)

            patched_send.assert_called_once_with(
                "!test:localhost", "mxc://aurl", "opsdroid_upload", "m.file", {}
            )

    async def test_respond_new_room(self):
        event = events.NewRoom(name="test", target="!test:localhost")
        with amock.patch(api_string.format("create_room")) as patched_send, amock.patch(
            api_string.format("set_room_name")
        ) as patched_name:
            patched_name.return_value = asyncio.Future()
            patched_name.return_value.set_result(None)

            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result({"room_id": "!test:localhost"})

            resp = await self.connector.send(event)
            assert resp == "!test:localhost"

            assert patched_name.called_once_with("#test:localhost", "test")

            assert patched_send.called_once_with()

    async def test_respond_room_address(self):
        event = events.RoomAddress("#test:localhost", target="!test:localhost")
        with amock.patch(api_string.format("set_room_alias")) as patched_send:
            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result({})

            await self.connector.send(event)

            assert patched_send.called_once_with("!test:localhost", "#test:localhost")

    async def test_respond_join_room(self):
        event = events.JoinRoom(target="#test:localhost")
        with amock.patch(api_string.format("get_room_id")) as patched_get_room_id:
            patched_get_room_id.return_value = asyncio.Future()
            patched_get_room_id.return_value.set_result("!test:localhost")
            with amock.patch(api_string.format("join_room")) as patched_send:
                patched_send.return_value = asyncio.Future()
                patched_send.return_value.set_result({})
                await self.connector.send(event)
                assert patched_send.called_once_with("#test:localhost")

    async def test_respond_user_invite(self):
        event = events.UserInvite("@test:localhost", target="!test:localhost")
        with amock.patch(api_string.format("invite_user")) as patched_send:
            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result({})
            await self.connector.send(event)
            assert patched_send.called_once_with("#test:localhost", "@test:localhost")

    async def test_respond_room_description(self):
        event = events.RoomDescription("A test room", target="!test:localhost")
        with amock.patch(api_string.format("set_room_topic")) as patched_send:
            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result({})
            await self.connector.send(event)
            assert patched_send.called_once_with("#test:localhost", "A test room")

    async def test_respond_room_image(self):
        image = events.Image(url="mxc://aurl")
        event = events.RoomImage(image, target="!test:localhost")
        with OpsDroid() as opsdroid, amock.patch(
            api_string.format("send_state_event")
        ) as patched_send:
            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result({})
            opsdroid.connectors = [self.connector]
            await self.connector.send(event)
            assert patched_send.called_once_with(
                "#test:localhost",
                "m.room.avatar",
                {"url": "mxc://aurl"},
                state_key=None,
            )

    async def test_respond_user_role(self):
        existing_power_levels = {
            "ban": 50,
            "events": {"m.room.name": 100, "m.room.power_levels": 100},
            "events_default": 0,
            "invite": 50,
            "kick": 50,
            "notifications": {"room": 20},
            "redact": 50,
            "state_default": 50,
            "users": {"@example:localhost": 100},
            "users_default": 0,
        }
        role_events = [
            (
                events.UserRole(
                    75, target="!test:localhost", user_id="@test:localhost"
                ),
                75,
            ),
            (
                events.UserRole(
                    "mod", target="!test:localhost", user_id="@test:localhost"
                ),
                50,
            ),
            (
                events.UserRole(
                    "admin", target="!test:localhost", user_id="@test:localhost"
                ),
                100,
            ),
        ]
        for event, pl in role_events:
            with OpsDroid() as opsdroid, amock.patch(
                api_string.format("send_state_event")
            ) as patched_send:
                with amock.patch(
                    api_string.format("get_power_levels")
                ) as patched_power_levels:
                    opsdroid.connectors = [self.connector]

                    patched_power_levels.return_value = asyncio.Future()
                    patched_power_levels.return_value.set_result(existing_power_levels)
                    patched_send.return_value = asyncio.Future()
                    patched_send.return_value.set_result({})

                    await self.connector.send(event)

                    modified_power_levels = deepcopy(existing_power_levels)
                    modified_power_levels["users"]["@test:localhost"] = pl

                    assert patched_send.called_once_with(
                        "!test:localhost",
                        "m.room.power_levels",
                        existing_power_levels,
                        state_key=None,
                    )

    async def test_send_reaction(self):
        message = events.Message(
            "hello",
            event_id="$11111",
            connector=self.connector,
            target="!test:localhost",
        )
        reaction = events.Reaction("⭕")
        with OpsDroid() as _:
            with amock.patch(api_string.format("send_message_event")) as patched_send:
                patched_send.return_value = asyncio.Future()
                patched_send.return_value.set_result(None)

                await message.respond(reaction)

                content = {
                    "m.relates_to": {
                        "rel_type": "m.annotation",
                        "event_id": "$11111",
                        "key": reaction.emoji,
                    }
                }

                assert patched_send.called_once_with(
                    "!test:localhost", "m.reaction", content
                )

    async def test_send_reply(self):
        message = events.Message(
            "hello",
            event_id="$11111",
            connector=self.connector,
            target="!test:localhost",
        )
        reply = events.Reply("reply")
        with OpsDroid() as _:
            with amock.patch(api_string.format("send_message_event")) as patched_send:
                patched_send.return_value = asyncio.Future()
                patched_send.return_value.set_result(None)

                await message.respond(reply)

                content = self.connector._get_formatted_message_body(
                    reply.text, msgtype="m.text"
                )

                content["m.relates_to"] = {
                    "m.in_reply_to": {"event_id": message.event_id}
                }

                assert patched_send.called_once_with(
                    "!test:localhost", "m.room.message", content
                )

    async def test_send_reply_id(self):
        reply = events.Reply("reply", linked_event="$hello", target="!hello:localhost")
        with OpsDroid() as _:
            with amock.patch(api_string.format("send_message_event")) as patched_send:
                patched_send.return_value = asyncio.Future()
                patched_send.return_value.set_result(None)

                await self.connector.send(reply)

                content = self.connector._get_formatted_message_body(
                    reply.text, msgtype="m.text"
                )

                content["m.relates_to"] = {"m.in_reply_to": {"event_id": "$hello"}}

                assert patched_send.called_once_with(
                    "!test:localhost", "m.room.message", content
                )

    async def test_alias_already_exists(self):

        with amock.patch(api_string.format("set_room_alias")) as patched_alias:
            patched_alias.side_effect = MatrixRequestError(409)

            await self.connector._send_room_address(
                events.RoomAddress(target="!test:localhost", address="hello")
            )

    async def test_already_in_room(self):

        with amock.patch(api_string.format("invite_user")) as patched_invite:
            patched_invite.side_effect = MatrixRequestError(
                403, json.dumps({"error": "@neo.matrix.org is already in the room"})
            )

            await self.connector._send_user_invitation(
                events.UserInvite(target="!test:localhost", user_id="@neo:matrix.org")
            )

    async def test_invalid_role(self):
        with self.assertRaises(ValueError):
            await self.connector._set_user_role(
                events.UserRole(
                    "wibble", target="!test:localhost", user_id="@test:localhost"
                )
            )

    async def test_no_user_id(self):
        with self.assertRaises(ValueError):
            await self.connector._set_user_role(
                events.UserRole("wibble", target="!test:localhost")
            )

    def test_m_notice(self):
        self.connector.rooms["test"] = {
            "alias": "#test:localhost",
            "send_m_notice": True,
        }

        assert self.connector.message_type("main") == "m.text"
        assert self.connector.message_type("test") == "m.notice"
        self.connector.send_m_notice = True
        assert self.connector.message_type("main") == "m.notice"

        # Reset the state
        self.connector.send_m_notice = False
        del self.connector.rooms["test"]

    def test_construct(self):
        jr = matrix_events.MatrixJoinRules("hello")
        assert jr.content["join_rule"] == "hello"

        hv = matrix_events.MatrixHistoryVisibility("hello")
        assert hv.content["history_visibility"] == "hello"

    async def test_send_generic_event(self):
        event = matrix_events.GenericMatrixRoomEvent(
            "opsdroid.dev", {"hello": "world"}, target="!test:localhost",
        )
        with OpsDroid() as _:
            with amock.patch(api_string.format("send_message_event")) as patched_send:
                patched_send.return_value = asyncio.Future()
                patched_send.return_value.set_result(None)

                await self.connector.send(event)
                assert patched_send.called_once_with(
                    "!test:localhost", "opsdroid.dev", {"hello": "world"}
                )


class TestEventCreatorAsync(asynctest.TestCase):
    def setUp(self):
        """Basic setting up for tests"""
        self.connector = setup_connector()
        self.api = AsyncHTTPAPI("https://notaurl.com", None)
        self.connector.connection = self.api

    @property
    def message_json(self):
        return {
            "content": {"body": "I just did it manually.", "msgtype": "m.text"},
            "event_id": "$15573463541827394vczPd:matrix.org",
            "origin_server_ts": 1557346354253,
            "room_id": "!MeRdFpEonLoCwhoHeT:matrix.org",
            "sender": "@neo:matrix.org",
            "type": "m.room.message",
            "unsigned": {"age": 48926251},
            "age": 48926251,
        }

    @property
    def file_json(self):
        return {
            "origin_server_ts": 1534013434328,
            "sender": "@neo:matrix.org",
            "event_id": "$1534013434516721kIgMV:matrix.org",
            "content": {
                "body": "stereo_reproject.py",
                "info": {"mimetype": "text/x-python", "size": 1239},
                "msgtype": "m.file",
                "url": "mxc://matrix.org/vtgAIrGtuYJQCXNKRGhVfSMX",
            },
            "room_id": "!MeRdFpEonLoCwhoHeT:matrix.org",
            "type": "m.room.message",
            "unsigned": {"age": 23394532373},
            "age": 23394532373,
        }

    @property
    def image_json(self):
        return {
            "content": {
                "body": "index.png",
                "info": {
                    "h": 1149,
                    "mimetype": "image/png",
                    "size": 1949708,
                    "thumbnail_info": {
                        "h": 600,
                        "mimetype": "image/png",
                        "size": 568798,
                        "w": 612,
                    },
                    "thumbnail_url": "mxc://matrix.org/HjHqeJDDxcnOEGydCQlJZQwC",
                    "w": 1172,
                },
                "msgtype": "m.image",
                "url": "mxc://matrix.org/iDHKYJSQZZrrhOxAkMBMOaeo",
            },
            "event_id": "$15548652221495790FYlHC:matrix.org",
            "origin_server_ts": 1554865222742,
            "room_id": "!MeRdFpEonLoCwhoHeT:matrix.org",
            "sender": "@neo:matrix.org",
            "type": "m.room.message",
            "unsigned": {"age": 2542608318},
            "age": 2542608318,
        }

    @property
    def room_name_json(self):
        return {
            "content": {"name": "Testing"},
            "type": "m.room.name",
            "unsigned": {
                "prev_sender": "@neo:matrix.org",
                "replaces_state": "$wzwL9bnZ3hQOIcOGzY5g55jYkFHMM6PmaGZ2n9w1IuY",
                "age": 122,
                "prev_content": {"name": "test"},
            },
            "origin_server_ts": 1575305934310,
            "state_key": "",
            "sender": "@neo:matrix.org",
            "event_id": "$3r_PWCT9Vurlv-OFleAsf5gEnoZd-LEGHY6AGqZ5tJg",
        }

    @property
    def room_description_json(self):
        return {
            "content": {"topic": "Hello world"},
            "type": "m.room.topic",
            "unsigned": {"age": 137},
            "origin_server_ts": 1575306720044,
            "state_key": "",
            "sender": "@neo:matrix.org",
            "event_id": "$bEg2XISusHMKLBw9b4lMNpB2r9qYoesp512rKvbo5LA",
        }

    @property
    def message_edit_json(self):
        return {
            "content": {
                "msgtype": "m.text",
                "m.new_content": {"msgtype": "m.text", "body": "hello"},
                "m.relates_to": {
                    "rel_type": "m.replace",
                    "event_id": "$15573463541827394vczPd:matrix.org",
                },
                "body": " * hello",
            },
            "type": "m.room.message",
            "unsigned": {"age": 80},
            "origin_server_ts": 1575307305885,
            "sender": "@neo:matrix.org",
            "event_id": "$E8qj6GjtrxfRIH1apJGzDu-duUF-8D19zFQv0k4q1eM",
        }

    @property
    def reaction_json(self):
        return {
            "content": {
                "m.relates_to": {
                    "rel_type": "m.annotation",
                    "event_id": "$MYO9kzuKrOwRdIfwumh2n2KfSBAYLifpK156nd0f_hY",
                    "key": "👍",
                }
            },
            "type": "m.reaction",
            "unsigned": {"age": 90},
            "origin_server_ts": 1575315194228,
            "sender": "@neo:matrix.org",
            "event_id": "$4KOPKFjdJ5urFGJdK4lnS-Fd3qcNWbPdR_rzSCZK_g0",
        }

    @property
    def reply_json(self):
        return {
            "type": "m.room.message",
            "sender": "@neo:matrix.org",
            "content": {
                "msgtype": "m.text",
                "body": "> <@morpheus:matrix.org> I just did it manually.\n\nhello",
                "format": "org.matrix.custom.html",
                "formatted_body": '<mx-reply><blockquote><a href="https://matrix.to/#/!sdhlkHsdskdkHG:matrix.org/$15573463541827394vczPd:matrix.org">In reply to</a> <a href="https://matrix.to/#/@morpheus:matrix.org">@morpheus:matrix.org</a><br>I just did it manually.</blockquote></mx-reply>hello',
                "m.relates_to": {
                    "m.in_reply_to": {"event_id": "$15573463541827394vczPd:matrix.org"}
                },
            },
            "event_id": "$15755082701541RchcK:matrix.org",
            "origin_server_ts": 1575508270019,
            "unsigned": {"age": 501, "transaction_id": "m1575508269677.3"},
        }

    @property
    def join_room_json(self):
        return {
            "content": {
                "avatar_url": "mxc://example.org/SEsfnsuifSDFSSEF",
                "displayname": "Alice Margatroid",
                "membership": "join",
            },
            "event_id": "$143273582443PhrSn:example.org",
            "origin_server_ts": 1432735824653,
            "room_id": "!jEsUZKDJdhlrceRyVU:example.org",
            "sender": "@example:example.org",
            "state_key": "@alice:example.org",
            "type": "m.room.member",
            "unsigned": {"age": 1234},
        }

    @property
    def event_creator(self):
        patched_get_nick = amock.MagicMock()
        patched_get_nick.return_value = asyncio.Future()
        patched_get_nick.return_value.set_result("Rabbit Hole")
        self.connector.get_nick = patched_get_nick

        patched_get_download_url = mock.Mock()
        patched_get_download_url.return_value = "mxc://aurl"
        self.connector.connection.get_download_url = patched_get_download_url

        return MatrixEventCreator(self.connector)

    async def test_create_message(self):
        event = await self.event_creator.create_event(self.message_json, "hello")
        assert isinstance(event, events.Message)
        assert event.text == "I just did it manually."
        assert event.user == "Rabbit Hole"
        assert event.user_id == "@neo:matrix.org"
        assert event.target == "hello"
        assert event.event_id == "$15573463541827394vczPd:matrix.org"
        assert event.raw_event == self.message_json

    async def test_create_file(self):
        event = await self.event_creator.create_event(self.file_json, "hello")
        assert isinstance(event, events.File)
        assert event.url == "mxc://aurl"
        assert event.user == "Rabbit Hole"
        assert event.user_id == "@neo:matrix.org"
        assert event.target == "hello"
        assert event.event_id == "$1534013434516721kIgMV:matrix.org"
        assert event.raw_event == self.file_json

    async def test_create_image(self):
        event = await self.event_creator.create_event(self.image_json, "hello")
        assert isinstance(event, events.Image)
        assert event.url == "mxc://aurl"
        assert event.user == "Rabbit Hole"
        assert event.user_id == "@neo:matrix.org"
        assert event.target == "hello"
        assert event.event_id == "$15548652221495790FYlHC:matrix.org"
        assert event.raw_event == self.image_json

    async def test_unsupported_type(self):
        json = self.message_json
        json["type"] = "wibble"
        event = await self.event_creator.create_event(json, "hello")
        assert isinstance(event, matrix_events.GenericMatrixRoomEvent)
        assert event.event_type == "wibble"
        assert "wibble" in repr(event)
        assert event.target in repr(event)
        assert str(event.content) in repr(event)

    async def test_unsupported_message_type(self):
        json = self.message_json
        json["content"]["msgtype"] = "wibble"
        event = await self.event_creator.create_event(json, "hello")
        assert isinstance(event, matrix_events.GenericMatrixRoomEvent)
        assert event.content["msgtype"] == "wibble"

    async def test_room_name(self):
        event = await self.event_creator.create_event(self.room_name_json, "hello")
        assert isinstance(event, events.RoomName)
        assert event.user == "Rabbit Hole"
        assert event.user_id == "@neo:matrix.org"
        assert event.event_id == "$3r_PWCT9Vurlv-OFleAsf5gEnoZd-LEGHY6AGqZ5tJg"
        assert event.raw_event == self.room_name_json

    async def test_room_description(self):
        event = await self.event_creator.create_event(
            self.room_description_json, "hello"
        )
        assert isinstance(event, events.RoomDescription)
        assert event.user == "Rabbit Hole"
        assert event.user_id == "@neo:matrix.org"
        assert event.event_id == "$bEg2XISusHMKLBw9b4lMNpB2r9qYoesp512rKvbo5LA"
        assert event.raw_event == self.room_description_json

    async def test_edited_message(self):
        with amock.patch(api_string.format("get_event_in_room")) as patched_send:
            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result(self.message_json)
            event = await self.event_creator.create_event(
                self.message_edit_json, "hello"
            )

        assert isinstance(event, events.EditedMessage)
        assert event.text == "hello"
        assert event.user == "Rabbit Hole"
        assert event.user_id == "@neo:matrix.org"
        assert event.target == "hello"
        assert event.event_id == "$E8qj6GjtrxfRIH1apJGzDu-duUF-8D19zFQv0k4q1eM"
        assert event.raw_event == self.message_edit_json

        assert isinstance(event.linked_event, events.Message)

    async def test_reaction(self):
        with amock.patch(api_string.format("get_event_in_room")) as patched_send:
            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result(self.message_json)
            event = await self.event_creator.create_event(self.reaction_json, "hello")

        assert isinstance(event, events.Reaction)
        assert event.emoji == "👍"
        assert event.user == "Rabbit Hole"
        assert event.user_id == "@neo:matrix.org"
        assert event.target == "hello"
        assert event.event_id == "$4KOPKFjdJ5urFGJdK4lnS-Fd3qcNWbPdR_rzSCZK_g0"
        assert event.raw_event == self.reaction_json

        assert isinstance(event.linked_event, events.Message)

    async def test_reply(self):
        with amock.patch(api_string.format("get_event_in_room")) as patched_send:
            patched_send.return_value = asyncio.Future()
            patched_send.return_value.set_result(self.message_json)
            event = await self.event_creator.create_event(self.reply_json, "hello")

        assert isinstance(event, events.Reply)
        assert event.text == "hello"
        assert event.user == "Rabbit Hole"
        assert event.user_id == "@neo:matrix.org"
        assert event.target == "hello"
        assert event.event_id == "$15755082701541RchcK:matrix.org"
        assert event.raw_event == self.reply_json

        assert isinstance(event.linked_event, events.Message)

    async def test_create_joinroom(self):
        event = await self.event_creator.create_event(self.join_room_json, "hello")
        assert isinstance(event, events.JoinRoom)
        assert event.user == "Rabbit Hole"
        assert event.user_id == "@example:example.org"
        assert event.target == "hello"
        assert event.event_id == "$143273582443PhrSn:example.org"
        assert event.raw_event == self.join_room_json

    @property
    def custom_json(self):
        return {
            "content": {"hello": "world"},
            "event_id": "$15573463541827394vczPd:localhost",
            "origin_server_ts": 1557346354253,
            "room_id": "!test:localhost",
            "sender": "@neo:matrix.org",
            "type": "opsdroid.dev",
            "unsigned": {"age": 48926251},
            "age": 48926251,
        }

    async def test_create_generic(self):
        event = await self.event_creator.create_event(self.custom_json, "hello")
        assert isinstance(event, matrix_events.GenericMatrixRoomEvent)
        assert event.user == "Rabbit Hole"
        assert event.user_id == "@neo:matrix.org"
        assert event.target == "hello"
        assert event.event_id == "$15573463541827394vczPd:localhost"
        assert event.raw_event == self.custom_json
        assert event.content == {"hello": "world"}
        assert event.event_type == "opsdroid.dev"

    @property
    def custom_state_json(self):
        return {
            "content": {"hello": "world"},
            "type": "wibble.opsdroid.dev",
            "unsigned": {"age": 137},
            "origin_server_ts": 1575306720044,
            "state_key": "",
            "sender": "@neo:matrix.org",
            "event_id": "$bEg2XISusHMKLBw9b4lMNpB2r9qYoesp512rKvbo5LA",
        }

    async def test_create_generic_state(self):
        event = await self.event_creator.create_event(self.custom_state_json, "hello")
        assert isinstance(event, matrix_events.MatrixStateEvent)
        assert event.user == "Rabbit Hole"
        assert event.user_id == "@neo:matrix.org"
        assert event.target == "hello"
        assert event.event_id == "$bEg2XISusHMKLBw9b4lMNpB2r9qYoesp512rKvbo5LA"
        assert event.raw_event == self.custom_state_json
        assert event.content == {"hello": "world"}
        assert event.event_type == "wibble.opsdroid.dev"
        assert event.state_key == ""
