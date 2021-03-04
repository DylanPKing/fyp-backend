import unittest
from unittest import mock

from autodjbackend import playlist_generator
from autodjbackend.models import Track


class TestPlaylistGenerator(unittest.TestCase):

    def test_h_value_exists_true(self):
        expected_value = True

        key = 'key'
        test_dict = {key: 1}

        actual_value = playlist_generator._h_value_exists(test_dict, key)
        assert expected_value == actual_value

    def test_h_value_exists_faise(self):
        expected_value = False

        key = 'key'
        test_dict = {key: 1}

        bad_key = 'bad key'

        actual_value = playlist_generator._h_value_exists(test_dict, bad_key)
        assert expected_value == actual_value

    def test_is_time_remaining_true(self):
        expected_value = True

        total_duration = 100000
        current_duration = 0

        actual_value = playlist_generator._is_time_remaining(
            total_duration, current_duration
        )

        assert expected_value == actual_value

    def test_is_time_remaining_false(self):
        expected_value = False

        total_duration = 100000
        current_duration = 90000

        actual_value = playlist_generator._is_time_remaining(
            total_duration, current_duration
        )

        assert expected_value == actual_value

    def test_bucket_tracks_by_h_value(self):
        test_heuristic_dict = {
            '123': 10,
            '456': 5,
            '789': 10,
            '012': 5,
        }

        expected_value = {
            10: ['123', '789'],
            5: ['456', '012'],
        }

        actual_value = playlist_generator._bucket_tracks_by_h_value(
            test_heuristic_dict
        )

        self.assertDictEqual(expected_value, actual_value)

    @mock.patch(
        'autodjbackend.playlist_generator._matches_user_criteria',
        return_value=10
    )
    @mock.patch(
        'autodjbackend.playlist_generator._original_performance',
        return_value=0
    )
    @mock.patch(
        'autodjbackend.playlist_generator._matches_current_track',
        return_value=5
    )
    @mock.patch(
        'autodjbackend.playlist_generator._contains_keywords', return_value=5
    )
    @mock.patch(
        'autodjbackend.playlist_generator._check_remaining_time',
        return_value=0
    )
    def test_calculate_heuristic_value_not_in_playlist(
        self, mocked_check_remaining_time, mocked_contains_keywords,
        mocked_matches_current_track, mocked_original_performance,
        mocked_matches_user_criteria
    ):
        expected_value = 20

        test_criteria = {
            'position': 3,
        }

        test_current_track = None

        test_track = None

        test_total_duration = 1

        test_current_total = 0

        actual_value = playlist_generator._calculate_heuristic_value(
            test_criteria, test_current_track, test_track,
            test_total_duration, test_current_total
        )

        assert expected_value == actual_value
        mocked_check_remaining_time.assert_called_once()
        mocked_contains_keywords.assert_called_once()
        mocked_matches_current_track.assert_called_once()
        mocked_matches_user_criteria.assert_called_once()
        mocked_original_performance.assert_called_once()

    @mock.patch(
        'autodjbackend.playlist_generator.minutes_to_milliseconds',
        return_value=0
    )
    def test_check_remaining_time_greater_than(
        self, mocked_minutes_to_milliseconds
    ):
        expected_value = 0

        test_total_duration = 0
        test_current_total = 0
        test_track = None

        actual_value = playlist_generator._check_remaining_time(
            test_track, test_total_duration, test_current_total
        )

        assert expected_value == actual_value
        mocked_minutes_to_milliseconds.assert_called_once()

    @mock.patch(
        'autodjbackend.playlist_generator.minutes_to_milliseconds',
        return_value=1
    )
    def test_check_remaining_time_greater_than_close_to_zero(
        self, mocked_minutes_to_milliseconds
    ):
        expected_value = 5

        test_total_duration = 0
        test_current_total = 0
        test_track = Track(duration=0)

        actual_value = playlist_generator._check_remaining_time(
            test_track, test_total_duration, test_current_total
        )

        assert expected_value == actual_value
        mocked_minutes_to_milliseconds.assert_called_once()

    @mock.patch(
        'autodjbackend.playlist_generator.minutes_to_milliseconds',
        return_value=1
    )
    def test_check_remaining_time_greater_than_not_close_to_zero(
        self, mocked_minutes_to_milliseconds
    ):
        expected_value = 0

        test_total_duration = 0
        test_current_total = 0
        test_track = Track(duration=2)

        actual_value = playlist_generator._check_remaining_time(
            test_track, test_total_duration, test_current_total
        )

        assert expected_value == actual_value
        mocked_minutes_to_milliseconds.assert_called_once()

    def test_contains_keywords_none(self):
        expected_value = 0

        test_current_track = Track(title='Hello')
        test_track = Track(title='World')

        actual_value = playlist_generator._contains_keywords(
            test_current_track, test_track
        )

        assert expected_value == actual_value

    def test_contains_keywords(self):
        expected_value = 5

        test_current_track = Track(title='a river')
        test_track = Track(title='b river')

        actual_value = playlist_generator._contains_keywords(
            test_current_track, test_track
        )

        assert expected_value == actual_value

    def test_matches_current_track_no_matches(self):
        expected_value = 0

        test_current_track = Track(position=1, year=0, original_artist='A')
        test_track = Track(position=2, year=1, original_artist='B')

        actual_value = playlist_generator._matches_current_track(
            test_current_track, test_track
        )

        assert expected_value == actual_value

    def test_matches_current_track_position(self):
        expected_value = 5

        test_current_track = Track(position=1, year=0, original_artist='A')
        test_track = Track(position=1, year=1, original_artist='B')

        actual_value = playlist_generator._matches_current_track(
            test_current_track, test_track
        )

        assert expected_value == actual_value

    def test_matches_current_track_year(self):
        expected_value = 5

        test_current_track = Track(position=1, year=0, original_artist='A')
        test_track = Track(position=2, year=0, original_artist='B')

        actual_value = playlist_generator._matches_current_track(
            test_current_track, test_track
        )

        assert expected_value == actual_value

    def test_matches_current_track_original_artist(self):
        expected_value = 5

        test_current_track = Track(position=1, year=0, original_artist='A')
        test_track = Track(position=2, year=1, original_artist='A')

        actual_value = playlist_generator._matches_current_track(
            test_current_track, test_track
        )

        assert expected_value == actual_value

    def test_original_performance_true(self):
        expected_value = -5

        test_artist = 'Artist'
        test_criteria = {
            'original_artist': test_artist
        }

        test_track = Track(artist=test_artist, original_artist=test_artist)

        actual_value = playlist_generator._original_performance(
            test_criteria, test_track
        )

        assert expected_value == actual_value

    def test_original_performance_false_cover(self):
        expected_value = 0

        test_artist = 'Artist'
        test_criteria = {
            'original_artist': test_artist
        }

        test_track = Track(artist='Brtist', original_artist=test_artist)

        actual_value = playlist_generator._original_performance(
            test_criteria, test_track
        )

        assert expected_value == actual_value

    def test_original_performance_false_not_in_criteria(self):
        expected_value = 0

        test_artist = 'Artist'
        test_criteria = {}

        test_track = Track(artist=test_artist, original_artist=test_artist)

        actual_value = playlist_generator._original_performance(
            test_criteria, test_track
        )

        assert expected_value == actual_value
