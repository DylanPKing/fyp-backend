import unittest

from autodjbackend import models, utils


class TestUtils(unittest.TestCase):
    def test_get_criteria_to_search_valid_criteria(self):
        expected_output = {
            'track_number': 1,
            'year': 1990,
            'original_artist': 'Artist',
            'keyword_in_title': 'keyword',
        }

        actual_output = utils.get_criteria_to_search(expected_output)

        self.assertDictEqual(expected_output, actual_output)

    def test_get_criteria_to_search_invalid_criteria(self):
        expected_output = {}

        criteria = {'invalid': 'criteria'}

        actual_output = utils.get_criteria_to_search(criteria)

        self.assertDictEqual(expected_output, actual_output)

    def test_get_criteria_to_search_empty_criteria(self):
        expected_output = {}

        criteria = {}

        actual_output = utils.get_criteria_to_search(criteria)

        self.assertDictEqual(expected_output, actual_output)

    def test_get_link_nodes_from_criteria(self):
        expected_output = list(
            models.SameTrackNumber.nodes.filter(track_number=1)
        )

        criteria = {'track_number': 1}

        actual_output = utils.get_link_nodes_from_criteria(criteria)

        self.assertEqual(expected_output, actual_output)
