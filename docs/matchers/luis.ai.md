# luis.ai Matcher

[luis.ai](https://www.luis.ai) is an NLP API for matching strings to [intents](https://docs.microsoft.com/en-us/azure/cognitive-services/LUIS/Home). Intents are created on the luis.ai website.

## Example 1

```python
from opsdroid.matchers import match_luisai_intent

@match_luisai_intent('Calendar.Add')
async def passthrough(opsdroid, config, message):
    if message.luisai["topScoringIntent"]["intent"]=="Calendar.Add":
        await message.respond(str(message.luisai))
```

The above skill would be called on any intent which has an action of `'Calendar.Add'`

## Creating a LUIS app

You can find a quick getting started with luis.ai guide [here](https://docs.microsoft.com/en-us/azure/cognitive-services/LUIS/luis-get-started-create-app).

## Configuring opsdroid

In order to enable luis.ai skills you must specify an `appid` and `appkey` for your bot. You can further configure the bot by enabling `verbose` or setting a `min-score` option to tell opsdroid to ignore any matches which score less than a given number between 0 and 1. The default for this is 0 which will match all messages.

```yaml

parsers:
   - name: luisai
     appid: "<application-id>"
     appkey: "<subscription-key>"
     verbose: True
     min-score: 0.6
```

## Message object additional parameters

### `message.luisai`

An http response object which has been returned by the luis.ai API. This allows you to access any information from the matched intent including the query, top scoring intent, intents etc.

```python
from opsdroid.matchers import match_luisai_intent

@match_luisai_intent('Calendar.Add')
async def passthrough(opsdroid, config, message):
    if message.luisai["topScoringIntent"]["intent"]=="Calendar.Add":
        await message.respond(str(message.luisai))
```

This example skill will print the following on the message "schedule meeting"

```json
{
   "query":"schedule meeting",
   "topScoringIntent":{
      "intent":"Calendar.Add",
      "score":0.900492251
   },
   "intents":[
      {
         "intent":"Calendar.Add",
         "score":0.900492251
      },
      {
         "intent":"None",
         "score":0.08836186
      },
      {
         "intent":"Calendar.Edit",
         "score":0.026984252
      },
      {
         "intent":"Calendar.CheckAvailability",
         "score":0.0102987411
      },
      {
         "intent":"Calendar.Delete",
         "score":0.00722231576
      },
      {
         "intent":"Calendar.Find",
         "score":0.005946379
      }
   ],
   "entities":[

   ]
}
```
