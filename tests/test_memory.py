
import unittest
import unittest.mock as mock

from opsdroid.memory import Memory


class TestMemory(unittest.TestCase):
    """Test the opsdroid memory class."""

    def setup(self):
        return Memory()

    def test_memory(self):
        memory = self.setup()
        data = "Hello world!"
        memory.put("test", data)
        self.assertEqual(data, memory.get("test"))
        self.assertIsNone(memory.get("nonexistant"))

    def test_sync(self):
        memory = self.setup()
        memory._get_from_database = mock.MagicMock()
        memory._put_to_database = mock.MagicMock()
        data = "Hello world!"

        memory.put("test", data)
        self.assertEqual(len(memory._put_to_database.mock_calls), 1)

        memory.get("test")
        self.assertEqual(len(memory._get_from_database.mock_calls), 1)
