"""A helper function for parsing and executing api.ai skills."""

import logging
import json

import aiohttp


async def parse_apiai(opsdroid, message):
    """Parse a message against all apiai skills."""
    # pylint: disable=broad-except
    # We want to catch all exceptions coming from a skill module and not
    # halt the application. If a skill throws an exception it just doesn't
    # give a response to the user, so an error response should be given.
    config = opsdroid.config['parsers']['apiai']
    if 'access-token' in config:
        async with aiohttp.ClientSession() as session:
            payload = {
                "v": "20150910",
                "lang": "en",
                "sessionId": message.connector.name,
                "query": message.text
            }
            headers = {
                "Authorization": "Bearer " + config['access-token'],
                "Content-Type": "application/json"
            }
            async with session.post("https://api.api.ai/v1/query",
                                    data=json.dumps(payload),
                                    headers=headers) as resp:
                result = await resp.json()
                logging.debug("api.ai response - " + json.dumps(result))

                if result["status"]["code"] >= 300:
                    logging.error("api.ai error - " +
                                  str(result["status"]["code"]) + " " +
                                  result["status"]["errorType"])
                    return

                if "min-score" in config and \
                    result["score"] < config["min-score"]:
                    logging.debug("api.ai score lower than min-score")
                    return

                for skill in opsdroid.skills:

                    if "apiai" in skill:
                        if "action" in result["result"] and \
                                skill["apiai"] in result["result"]["action"]:
                            message.apiai = result
                            try:
                                await skill["skill"](opsdroid, message)
                            except Exception:
                                await message.respond(
                                    "Whoops there has been an error")
                                await message.respond(
                                    "Check the log for details")
                                logging.exception("Exception when parsing '" +
                                                  message.text +
                                                  "' against skill '" +
                                                  skill["apiai"] + "'")
