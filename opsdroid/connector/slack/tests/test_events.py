"""Test events from Slack"""

import pytest
from opsdroid.connector.slack.events import InteractiveAction
from opsdroid.events import Message
from opsdroid.testing import running_opsdroid, MINIMAL_CONFIG


@pytest.mark.asyncio
class TestIntercativeAction:
    @pytest.mark.add_response("/", "POST", {"ok": True}, 200)
    async def test_respond_response_url_exists(self, mock_api_obj, mock_api):
        action = InteractiveAction({"response_url": mock_api_obj.base_url})
        response = await action.respond("this is a test response")
        assert response["ok"]

    async def test_respond_event_response_url_does_not_exist(
        self, mock_api_obj, mock_api
    ):
        action = InteractiveAction({})
        response = await action.respond("this is a test response")
        assert response == {"error": "Response URL not available in payload."}

    @pytest.mark.add_response("/", "POST", {"ok": True}, 200)
    async def test_respond_response_event_not_a_string(
        self, opsdroid, mock_api_obj, mock_api
    ):
        await opsdroid.load(config=MINIMAL_CONFIG)
        async with running_opsdroid(opsdroid):
            action = InteractiveAction({"response_url": mock_api_obj.base_url})
            message = Message("this is a test response")
            response = await action.respond(message)
            assert response
