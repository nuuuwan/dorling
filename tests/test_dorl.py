import os
import unittest

from gig import EntType

from dorling import Dorl, config_utils


class TestCase(unittest.TestCase):
    def test_districts(self):
        config = config_utils.get_config_for_type(EntType.DISTRICT)
        dorl = Dorl(config)
        svg_path = os.path.join('test_examples', 'districts.svg')
        dorl.write(svg_path)
