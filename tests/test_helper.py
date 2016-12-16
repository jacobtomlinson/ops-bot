
import unittest
import logging

from opsdroid import helper


class TestHelper(unittest.TestCase):
    """Test the opsdroid helper classes."""

    def test_set_logging_level(self):
        helper.set_logging_level('debug')
        self.assertEqual(10, logging.getLogger().getEffectiveLevel())

        helper.set_logging_level('info')
        self.assertEqual(20, logging.getLogger().getEffectiveLevel())

        helper.set_logging_level('warning')
        self.assertEqual(30, logging.getLogger().getEffectiveLevel())

        helper.set_logging_level('error')
        self.assertEqual(40, logging.getLogger().getEffectiveLevel())

        helper.set_logging_level('critical')
        self.assertEqual(50, logging.getLogger().getEffectiveLevel())

        helper.set_logging_level('an unkown level')
        self.assertEqual(20, logging.getLogger().getEffectiveLevel())
