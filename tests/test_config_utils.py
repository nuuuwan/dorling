import unittest

from gig import EntType

from dorling import config_utils


class TestCase(unittest.TestCase):
    def test_district(self):
        config = config_utils.get_config_for_type(EntType.DISTRICT)
        self.assertEqual(len(config), 25)
