
import asynctest
import asynctest.mock as amock

from opsdroid.__main__ import configure_lang
from opsdroid.core import OpsDroid
from opsdroid.matchers import match_regex
from opsdroid.events import Message
from opsdroid.parsers.regex import parse_regex


class TestParserRegex(asynctest.TestCase):
    """Test the opsdroid regex parser."""

    async def setup(self):
        configure_lang({})

    async def getMockSkill(self):
        async def mockedskill(opsdroid, config, message):
            pass
        mockedskill.config = {}
        return mockedskill

    async def getRaisingMockSkill(self):
        async def mockedskill(opsdroid, config, message):
            raise Exception()
        mockedskill.config = {}
        return mockedskill

    async def test_parse_regex(self):
        with OpsDroid() as opsdroid:
            mock_skill = await self.getMockSkill()
            opsdroid.skills.append(match_regex(r"(.*)")(mock_skill))

            mock_connector = amock.CoroutineMock()
            message = Message("Hello world", "user", "default", mock_connector)

            skills = await parse_regex(opsdroid, opsdroid.skills, message)
            self.assertEqual(mock_skill, skills[0]["skill"])

    async def test_parse_regex_priority_low(self):
        with OpsDroid() as opsdroid:
            regex = r"(.*)"

            mock_skill_low = await self.getMockSkill()
            opsdroid.skills.append(match_regex(regex, score_factor=0.6)(mock_skill_low))

            mock_connector = amock.CoroutineMock()
            message = Message("Hello world", "user", "default", mock_connector)

            skills = await opsdroid.get_ranked_skills(opsdroid.skills, message)
            self.assertEqual(mock_skill_low, skills[0]["skill"])

    async def test_parse_regex_priority_high(self):
        with OpsDroid() as opsdroid:
            regex = r"(.*)"

            mock_skill_high = await self.getMockSkill()
            opsdroid.skills.append(match_regex(regex, score_factor=1)(mock_skill_high))

            mock_connector = amock.CoroutineMock()
            message = Message("Hello world", "user", "default", mock_connector)

            skills = await opsdroid.get_ranked_skills(opsdroid.skills, message)
            self.assertEqual(mock_skill_high, skills[0]["skill"])

    async def test_parse_regex_raises(self):
        with OpsDroid() as opsdroid:
            mock_skill = await self.getRaisingMockSkill()
            opsdroid.skills.append(match_regex(r"(.*)")(mock_skill))

            self.assertEqual(len(opsdroid.skills), 1)

            mock_connector = amock.MagicMock()
            mock_connector.send = amock.CoroutineMock()
            message = Message("Hello world", "user", "default",
                              mock_connector)

            skills = await parse_regex(opsdroid, opsdroid.skills, message)
            self.assertEqual(mock_skill, skills[0]["skill"])

    async def test_parse_regex_matching_condition_search(self):
        with OpsDroid() as opsdroid:
            regex = r"(.*)"

            mock_skill_matching_search = await self.getMockSkill()
            opsdroid.skills.append(match_regex(regex, matching_condition="search")(mock_skill_matching_search))

            mock_connector = amock.CoroutineMock()
            message = Message("Hello world", "user", "default", mock_connector)

            skills = await opsdroid.get_ranked_skills(opsdroid.skills, message)
            self.assertEqual(mock_skill_matching_search, skills[0]["skill"])

    async def test_parse_regex_matching_condition_match(self):
        with OpsDroid() as opsdroid:
            regex = r"(.*)"

            mock_skill_matching_match = await self.getMockSkill()
            opsdroid.skills.append(match_regex(regex, matching_condition="match")(mock_skill_matching_match))

            mock_connector = amock.CoroutineMock()
            message = Message("Hello world", "user", "default", mock_connector)

            skills = await opsdroid.get_ranked_skills(opsdroid.skills, message)
            self.assertEqual(mock_skill_matching_match, skills[0]["skill"])

    async def test_parse_regex_matching_condition_fullmatch(self):
        with OpsDroid() as opsdroid:
            regex = r"(.*)"

            mock_skill_matching_fullmatch = await self.getMockSkill()
            opsdroid.skills.append(match_regex(regex, matching_condition="fullmatch")(mock_skill_matching_fullmatch))

            mock_connector = amock.CoroutineMock()
            message = Message("Hello world", "user", "default", mock_connector)

            skills = await opsdroid.get_ranked_skills(opsdroid.skills, message)
            self.assertEqual(mock_skill_matching_fullmatch, skills[0]["skill"])
