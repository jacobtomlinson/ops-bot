# Always matcher

The `always` matcher is a special case which simply always matches a skill to every single message that passes through opsdroid.

When a message is parsed all skills are ranked by the parsers in order of how confident they are that the message is a match, and then the highest ranking skill is executed. The `always` matcher is useful if you are wanting to do something like keep track of the last time someone spoke, so you need the skill to execute on every message and you will never directly respond to a message.

## Example

```python
from opsdroid.matchers import match_always

@match_always
async def keep_track(opsdroid, config, message):
    # Put message.user into a database along with a timestamp
```

