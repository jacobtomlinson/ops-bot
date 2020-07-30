"""Tests for the ConnectorSlack class."""
import asyncio
import unittest
import unittest.mock as mock
import asynctest
import asynctest.mock as amock
import slack
import json
import collections

import aiohttp

from opsdroid.core import OpsDroid
from opsdroid.connector.slack import ConnectorSlack
from opsdroid.connector.slack import events as slackevents
from opsdroid import events
from opsdroid.cli.start import configure_lang


class TestConnectorSlack(unittest.TestCase):
    """Test the opsdroid Slack connector class."""

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        configure_lang({})
        self.od = OpsDroid()
        self.od.__enter__()
        self.connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        self.event_creator = slackevents.SlackEventCreator(
            self.connector, self.connector.slack_rtm
        )

    def tearDown(self):
        slack.RTMClient._callbacks = collections.defaultdict(list)
        del self.connector
        del self.event_creator
        self.od.__exit__(None, None, None)
        del self.od

    def test_init(self):
        """Test that the connector is initialised properly."""
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        self.assertEqual("#general", connector.default_target)
        self.assertEqual("slack", connector.name)
        self.assertEqual(10, connector.timeout)

    def test_missing_api_key(self):
        """Test that creating without an API key raises an error."""
        with self.assertRaises(KeyError):
            ConnectorSlack({}, opsdroid=self.od)

    # def test_listen(self):
    #     connector = ConnectorSlack({})
    #     with self.assertRaises(NotImplementedError):
    #         self.loop.run_until_complete(connector.listen({}))

    # def test_respond(self):
    #     connector = ConnectorSlack({})
    #     with self.assertRaises(NotImplementedError):
    #         self.loop.run_until_complete(connector.send({}))

    # def test_react(self):
    #     connector = ConnectorSlack({})
    #     reacted = self.loop.run_until_complete(connector.react({}, 'emoji'))
    #     self.assertFalse(reacted)

    # def test_user_typing(self):
    #     opsdroid = 'opsdroid'
    #     connector = ConnectorSlack({})
    #     user_typing = self.loop.run_until_complete(
    #         connector.user_typing(opsdroid, trigger=True))
    #     assert user_typing is None


class TestConnectorSlackAsync(asynctest.TestCase):
    """Test the async methods of the opsdroid Slack connector class."""

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        configure_lang({})
        self.od = OpsDroid()
        self.od.__enter__()
        self.connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        self.event_creator = slackevents.SlackEventCreator(
            self.connector, self.connector.slack_rtm
        )

    def tearDown(self):
        slack.RTMClient._callbacks = collections.defaultdict(list)
        del self.connector
        del self.event_creator
        self.od.__exit__(None, None, None)
        del self.od

    async def test_connect(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        opsdroid = amock.CoroutineMock()
        opsdroid.eventloop = self.loop
        connector.slack_rtm._connect_and_read = amock.CoroutineMock()
        connector.slack.api_call = amock.CoroutineMock()
        connector.opsdroid.web_server = amock.CoroutineMock()
        connector.opsdroid.web_server.web_app = amock.CoroutineMock()
        connector.opsdroid.web_server.web_app.router = amock.CoroutineMock()
        connector.opsdroid.web_server.web_app.router.add_post = amock.CoroutineMock()
        await connector.connect()
        self.assertTrue(connector.slack_rtm._connect_and_read.called)
        self.assertTrue(connector.slack.api_call.called)
        self.assertTrue(connector.opsdroid.web_server.web_app.router.add_post.called)

    async def test_connect_auth_fail(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        opsdroid = amock.CoroutineMock()
        opsdroid.eventloop = self.loop
        connector.slack_rtm._connect_and_read = amock.Mock()
        connector.slack_rtm._connect_and_read.side_effect = slack.errors.SlackApiError(
            message="", response=""
        )

        await connector.connect()
        self.assertLogs("_LOGGER", "error")

    async def test_abort_on_connection_error(self):
        connector = ConnectorSlack({"token": "abc123"})
        connector.slack_rtm._connect_and_read = amock.CoroutineMock()
        connector.slack_rtm._connect_and_read.side_effect = Exception()
        connector.slack_rtm.stop = amock.CoroutineMock()

        with self.assertRaises(Exception):
            await connector.connect()
        self.assertTrue(connector.slack_rtm.stop.called)

    async def test_listen_loop(self):
        """Test that listening consumes from the socket."""
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.listening = False
        await connector.listen()

    async def test_lookup_username(self):
        """Test that looking up a username works and that it caches."""
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.users_info = amock.CoroutineMock()
        mock_user = mock.Mock()
        mock_user.data = {"user": {"name": "testuser"}}
        connector.slack.users_info.return_value = mock_user

        self.assertEqual(len(connector.known_users), 0)

        await connector.lookup_username("testuser")
        self.assertTrue(len(connector.known_users), 1)
        self.assertTrue(connector.slack.users_info.called)

        connector.slack.users_info.reset_mock()
        await connector.lookup_username("testuser")
        self.assertEqual(len(connector.known_users), 1)
        self.assertFalse(connector.slack.users_info.called)

        with self.assertRaises(ValueError):
            mock_user.data = {"user": None}
            connector.slack.users_info.return_value = mock_user
            await connector.lookup_username("invaliduser")

    async def test_respond(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock()
        await connector.send(
            events.Message(
                text="test", user="user", target="room", connector=connector,
            )
        )
        self.assertTrue(connector.slack.api_call.called)

    async def test_send_message_inside_thread(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock()
        linked_event = events.Message(
            text="linked text", raw_event={"thread_ts": "1582838099.000600"}
        )
        message = events.Message(
            text="test",
            user="user",
            target="room",
            connector=connector,
            linked_event=linked_event,
            event_id="1582838099.000601",
        )

        await connector.send(message)
        connector.slack.api_call.assert_called_once_with(
            "chat.postMessage",
            data={
                "channel": "room",
                "text": "test",
                "as_user": False,
                "username": "opsdroid",
                "icon_emoji": ":robot_face:",
                "thread_ts": "1582838099.000600",
            },
        )

    async def test_send_message_start_thread_is_true(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock()
        connector.start_thread = True
        event_id = "1582838099.000601"
        linked_event = events.Message(
            text="linked text", event_id=event_id, raw_event={}
        )
        message = events.Message(
            text="test",
            user="user",
            target="room",
            connector=connector,
            linked_event=linked_event,
        )
        await connector.send(message)
        connector.slack.api_call.assert_called_once_with(
            "chat.postMessage",
            data={
                "channel": "room",
                "text": "test",
                "as_user": False,
                "username": "opsdroid",
                "icon_emoji": ":robot_face:",
                "thread_ts": "1582838099.000601",
            },
        )

    async def test_send_blocks(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock()
        await connector.send(
            slackevents.Blocks(
                [{"type": "section", "text": {"type": "mrkdwn", "text": "*Test*"}}],
                "user",
                "room",
                connector,
            )
        )
        self.assertTrue(connector.slack.api_call.called)

    async def test_react(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock()
        prev_message = events.Message(
            text="test",
            user="user",
            target="room",
            connector=connector,
            raw_event={"ts": 0},
        )
        await prev_message.respond(events.Reaction("😀"))
        self.assertTrue(connector.slack.api_call)
        self.assertEqual(
            connector.slack.api_call.call_args[1]["data"]["name"], "grinning_face"
        )

    async def test_react_invalid_name(self):

        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock(
            side_effect=slack.errors.SlackApiError("invalid_name", "invalid_name")
        )
        prev_message = events.Message(
            text="test",
            user="user",
            target="room",
            connector=connector,
            raw_event={"ts": 0},
        )
        await prev_message.respond(events.Reaction("😀"))
        self.assertLogs("_LOGGER", "warning")

    async def test_react_unknown_error(self):

        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock(
            side_effect=slack.errors.SlackApiError("unknown", "unknown")
        )
        with self.assertRaises(slack.errors.SlackApiError):
            prev_message = events.Message(
                text="test",
                user="user",
                target="room",
                connector=connector,
                raw_event={"ts": 0},
            )
            await prev_message.respond(events.Reaction("😀"))

    async def test_replace_usernames(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.lookup_username = amock.CoroutineMock()
        connector.lookup_username.return_value = {"name": "user"}
        result = await connector.replace_usernames("Hello <@U023BECGF>!")
        self.assertEqual(result, "Hello user!")

    async def test_block_actions_interactivity(self):
        """Test the block_actions interactivity type in Slack interactions handler."""

        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.opsdroid = amock.CoroutineMock()
        connector.opsdroid.parse = amock.CoroutineMock()

        req_ob = {
            "type": "block_actions",
            "team": {"id": "T9TK3CUKW", "domain": "example"},
            "user": {
                "id": "UA8RXUSPL",
                "username": "jtorrance",
                "team_id": "T9TK3CUKW",
            },
            "channel": {"id": "CBR2V3XEX", "name": "review-updates"},
            "actions": [
                {
                    "action_id": "WaXA",
                    "block_id": "=qXel",
                    "text": {"type": "plain_text", "text": "View", "emoji": True},
                    "value": "click_me_123",
                    "type": "button",
                    "action_ts": "1548426417.840180",
                },
                {
                    "type": "overflow",
                    "block_id": "B5XNP",
                    "action_id": "BnhtF",
                    "selected_option": {
                        "text": {
                            "type": "plain_text",
                            "text": "Option 1",
                            "emoji": True,
                        },
                        "value": "value-0",
                    },
                    "action_ts": "1576336883.317406",
                },
                {
                    "type": "datepicker",
                    "block_id": "CAwR",
                    "action_id": "VS+",
                    "selected_date": "2019-12-31",
                    "initial_date": "1990-04-28",
                    "action_ts": "1576337318.133466",
                },
                {
                    "type": "multi_static_select",
                    "block_id": "rOL",
                    "action_id": "Cd9",
                    "selected_options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Choice 1",
                                "emoji": True,
                            },
                            "value": "value-0",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Choice 2",
                                "emoji": True,
                            },
                            "value": "value-1",
                        },
                    ],
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select items",
                        "emoji": True,
                    },
                    "action_ts": "1576337351.609054",
                },
                {
                    "type": "static_select",
                    "block_id": "OGN1",
                    "action_id": "4jd",
                    "selected_option": {
                        "text": {
                            "type": "plain_text",
                            "text": "Choice 2",
                            "emoji": True,
                        },
                        "value": "value-1",
                    },
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an item",
                        "emoji": True,
                    },
                    "action_ts": "1576337378.859991",
                },
            ],
        }

        mock_request = amock.CoroutineMock()
        mock_request.post = amock.CoroutineMock()
        mock_request.post.return_value = {"payload": json.dumps(req_ob)}

        response = await connector.slack_interactions_handler(mock_request)
        self.assertTrue(connector.opsdroid.parse.called)
        self.assertEqual(connector.opsdroid.parse.call_count, len(req_ob["actions"]))
        self.assertEqual(type(response), aiohttp.web.Response)
        self.assertEqual(response.status, 200)

    async def test_message_action_interactivity(self):
        """Test the message_action interactivity type in Slack interactions handler."""

        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.opsdroid = amock.CoroutineMock()
        connector.opsdroid.parse = amock.CoroutineMock()

        req_ob = {
            "token": "Nj2rfC2hU8mAfgaJLemZgO7H",
            "callback_id": "chirp_message",
            "type": "message_action",
            "trigger_id": "13345224609.8534564800.6f8ab1f53e13d0cd15f96106292d5536",
            "response_url": "https://hooks.slack.com/app-actions/T0MJR11A4/21974584944/yk1S9ndf35Q1flupVG5JbpM6",
            "team": {"id": "T0MJRM1A7", "domain": "pandamonium"},
            "channel": {"id": "D0LFFBKLZ", "name": "cats"},
            "user": {"id": "U0D15K92L", "name": "dr_maomao"},
            "message": {
                "type": "message",
                "user": "U0MJRG1AL",
                "ts": "1516229207.000133",
                "text": "World's smallest big cat! <https://youtube.com/watch?v=W86cTIoMv2U>",
            },
        }

        mock_request = amock.CoroutineMock()
        mock_request.post = amock.CoroutineMock()
        mock_request.post.return_value = {"payload": json.dumps(req_ob)}

        response = await connector.slack_interactions_handler(mock_request)
        self.assertTrue(connector.opsdroid.parse.called)
        self.assertEqual(type(response), aiohttp.web.Response)
        self.assertEqual(response.status, 200)

    async def test_view_submission_interactivity(self):
        """Test the view_submission interactivity type in Slack interactions handler."""

        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.opsdroid = amock.CoroutineMock()
        connector.opsdroid.parse = amock.CoroutineMock()

        req_ob = {
            "type": "view_submission",
            "team": {"id": "T0MJRM1A7", "domain": "pandamonium"},
            "user": {"id": "U0D15K92L", "name": "dr_maomao"},
            "view": {
                "id": "VNHU13V36",
                "type": "modal",
                "private_metadata": "shhh-its-secret",
                "callback_id": "modal-with-inputs",
                "state": {
                    "values": {
                        "multi-line": {
                            "ml-value": {
                                "type": "plain_text_input",
                                "value": "This is my example inputted value",
                            }
                        }
                    }
                },
                "hash": "156663117.cd33ad1f",
            },
        }

        mock_request = amock.CoroutineMock()
        mock_request.post = amock.CoroutineMock()
        mock_request.post.return_value = {"payload": json.dumps(req_ob)}

        response = await connector.slack_interactions_handler(mock_request)
        self.assertTrue(connector.opsdroid.parse.called)
        self.assertEqual(type(response), aiohttp.web.Response)
        self.assertEqual(response.status, 200)

    async def test_view_closed_interactivity(self):
        """Test the view_closed interactivity type in Slack interactions handler."""

        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.opsdroid = amock.CoroutineMock()
        connector.opsdroid.parse = amock.CoroutineMock()

        req_ob = {
            "type": "view_closed",
            "team": {"id": "TXXXXXX", "domain": "coverbands"},
            "user": {"id": "UXXXXXX", "name": "dreamweaver"},
            "view": {
                "id": "VNHU13V36",
                "type": "modal",
                "private_metadata": "shhh-its-secret",
                "callback_id": "modal-with-inputs",
                "state": {
                    "values": {
                        "multi-line": {
                            "ml-value": {
                                "type": "plain_text_input",
                                "value": "This is my example inputted value",
                            }
                        }
                    }
                },
                "hash": "156663117.cd33ad1f",
            },
            "api_app_id": "AXXXXXX",
            "is_cleared": False,
        }

        mock_request = amock.CoroutineMock()
        mock_request.post = amock.CoroutineMock()
        mock_request.post.return_value = {"payload": json.dumps(req_ob)}

        response = await connector.slack_interactions_handler(mock_request)
        self.assertTrue(connector.opsdroid.parse.called)
        self.assertEqual(type(response), aiohttp.web.Response)
        self.assertEqual(response.status, 200)

    async def test_respond_on_interactive_actions(self):
        """Test the respond method for interactive actions in Slack."""

        result = amock.Mock()
        result.json = amock.CoroutineMock()
        result.json.return_value = {"success": "payload sent."}

        payload = {
            "type": "message_action",
            "team": {"id": "TXXXXXX", "domain": "coverbands"},
            "user": {"id": "UXXXXXX", "name": "dreamweaver"},
            "response_url": "https://hooks.slack.com/app-actions/T0MJR11A4/21974584944/yk1S9ndf35Q1flupVG5JbpM6",
        }

        interactive_action = slackevents.InteractiveAction(payload)
        with amock.patch("aiohttp.ClientSession.post") as patched_request:
            patched_request.return_value = asyncio.Future()
            patched_request.return_value.set_result(result)
            await interactive_action.respond("Respond called with response_url")
            self.assertTrue(patched_request.called)

        payload = {
            "type": "view_closed",
            "team": {"id": "TXXXXXX", "domain": "coverbands"},
            "user": {"id": "UXXXXXX", "name": "dreamweaver"},
        }

        interactive_action = slackevents.InteractiveAction(payload)
        with amock.patch("aiohttp.ClientSession.post") as patched_request:
            patched_request.return_value = asyncio.Future()
            patched_request.return_value.set_result(result)
            await interactive_action.respond("Respond called without response_url")
            self.assertFalse(patched_request.called)

        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        raw_message = {
            "text": "Hello world",
            "user_id": "user_id",
            "user": "user",
            "room": "default",
        }
        message = events.Message(
            text="Hello world",
            user_id="user_id",
            user="user",
            target="default",
            connector=connector,
            raw_event=raw_message,
        )
        self.od.send = amock.CoroutineMock()

        with amock.patch("aiohttp.ClientSession.post") as patched_request:
            patched_request.return_value = asyncio.Future()
            patched_request.return_value.set_result(result)
            await interactive_action.respond(message)
            self.assertTrue(self.od.send.called)
            self.assertFalse(patched_request.called)

    async def test_send_room_creation(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock()
        await connector.send(events.NewRoom(name="mynewroom"))
        connector.slack.api_call.assert_called_once_with(
            "conversations.create", data={"name": "mynewroom"}
        )

    async def test_send_room_name_set(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock()
        await connector.send(
            events.RoomName(target="an-existing-room", name="my-new-room-name")
        )
        connector.slack.api_call.assert_called_once_with(
            "conversations.rename",
            data={"channel": "an-existing-room", "name": "my-new-room-name"},
        )

    async def test_send_user_invitation(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock()
        await connector.send(
            events.UserInvite(
                user="User McUserface", user_id="UMcU42", target="an-existing-room"
            )
        )
        connector.slack.api_call.assert_called_once_with(
            "conversations.invite",
            data={"channel": "an-existing-room", "users": "UMcU42"},
        )

    async def test_join_room(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock()
        await connector.send(events.JoinRoom(target="an-existing-room"))
        connector.slack.api_call.assert_called_once_with(
            "conversations.join", data={"channel": "an-existing-room"}
        )

    async def test_send_room_description(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock()
        await connector.send(
            events.RoomDescription(
                target="an-existing-room", description="A new description"
            )
        )
        connector.slack.api_call.assert_called_once_with(
            "conversations.setTopic",
            data={"channel": "an-existing-room", "topic": "A new description"},
        )

    async def test_send_pin_added(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock()
        await connector.send(
            events.PinMessage(
                target="an-existing-room",
                linked_event=events.Message(
                    "An important message",
                    user="User McUserface",
                    user_id="U9S8JGF45",
                    target="an-existing-room",
                    connector=connector,
                    event_id="1582838099.000600",
                ),
            )
        )
        connector.slack.api_call.assert_called_once_with(
            "pins.add",
            data={"channel": "an-existing-room", "timestamp": "1582838099.000600"},
        )

    async def test_send_pin_removed(self):
        connector = ConnectorSlack({"token": "abc123"}, opsdroid=self.od)
        connector.slack.api_call = amock.CoroutineMock()
        await connector.send(
            events.UnpinMessage(
                target="an-existing-room",
                linked_event=events.Message(
                    "An important message",
                    user="User McUserface",
                    user_id="U9S8JGF45",
                    target="an-existing-room",
                    connector=connector,
                    event_id="1582838099.000600",
                ),
            )
        )
        connector.slack.api_call.assert_called_once_with(
            "pins.remove",
            data={"channel": "an-existing-room", "timestamp": "1582838099.000600"},
        )
