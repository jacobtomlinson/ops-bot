# Regular Expression Matcher

## Configuring opsdroid

In order to enable regex skills you must set the `enabled` parameter to true in the parsers section of the opsdroid configuration file.

If a skill is configured with both the regex and some other NLU matcher then users who don't use NLU will get a simple regex match. However users with some other NLU configured will get matches on more flexible messages, but will not see duplicate responses where the regex also matched.

```yaml
parsers:
  - name: regex
    enabled: true
```

##

This is the simplest matcher available in opsdroid. It matches the message from the user against a regular expression. If the regex matches the function is called.

_note: The use of position anchors(`^` or `$`) are encouraged when using regex to match a function. This should prevent opsdroid to be triggered with every use of the matched regular expression_

## Example 1

```python
from opsdroid.matchers import match_regex

@match_regex('hi', case_sensitive=False)
async def hello(opsdroid, config, message):
    await message.respond('Hey')
```

The above skill would be called on any message which matches the regex `'hi'`, `'Hi'` or `'HI`. The `case_sensitive` kwarg is optional and defaults to `True`. 


## Example 2

```python
from opsdroid.matchers import match_regex

@match_regex('cold')
async def is_cold(opsdroid, config, message):
    await message.respond('it is')
```

The above skill would be called on any message that matches the regex `'cold'` . 

> user: is it cold?
>
> opsdroid: it is

Undesired effect: 

> user:  Wow, yesterday was so cold at practice!
>
> opsdroid: it is.

Since this matcher searches a message for the regular expression used on a skill, opsdroid will trigger any mention of the `'cold'`. To prevent this position anchors should be used.

#### Fixed example
```python
from opsdroid.matchers import match_regex

@match_regex('cold$')
async def is_cold(opsdroid, config, message):
    await message.respond('it is')
```

Now this skill will only be triggered if `'cold'` is located at the end of the message.

> user: is it cold
>
> opsdroid: it is
>
> user: Wow it was so cold outside yesterday!
>
> opsdroid: 

Since `'cold'` wasn't located at the end of the message, opsdroid didn't react to the second message posted by the user.

## Message object additional parameters

### `message.regex`

A _[re match object](https://docs.python.org/3/library/re.html#re.MatchObject)_ for the regular expression the message was matched against. This allows you to access any wildcard matches in the regex from within your skill.

```python
from opsdroid.matchers import match_regex

@match_regex(r'remember (.*)')
async def remember(opsdroid, config, message):
    remember = message.regex.group(1)
    await opsdroid.memory.put("remember", remember)
    await message.respond("OK I'll remember that")
```
