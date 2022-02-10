import unittest
from lib import jsonLib


class TestJson(unittest.TestCase):

    def setUp(self) -> None:
        self.jsonIn = jsonLib.jsonInput("test/test.json")

    def test_value_returned_1_level(self):
        self.assertEqual("Robocup-V0", self.jsonIn.get_value_from_Json("id"))

    def test_value_returned_3_level(self):
        self.assertEqual(self.jsonIn.get_value_from_Json("arguments", "team_left_dict", "green"), 2)


if __name__ == '__main__':
    unittest.main()
