from autodjbackend.views import CreatePlaylistViewSet

import unittest

from unittest.mock import patch

from autodjbackend import models

from rest_framework.request import HttpRequest, Request
from rest_framework.exceptions import ParseError, UnsupportedMediaType


class TestCreatePlayListViewSet(unittest.TestCase):

    def setUp(self):
        self.view_set = CreatePlaylistViewSet()

    def test_create_success(self):
        expected_tracks = [
            models.Track(
                title='title',
                original_artist='artist',
                duration=2,
            ),
            models.Track(
                title='another title',
                original_artist='artist',
                duration=2,
            )
        ]

        expected_output = {
            'tracks': [track.serialize for track in expected_tracks],
            'total_duration': 4,
        }

        request_data = {
            'track_criteria': {
                'original_artist': 'artist',
            },
            'total_duration': 4
        }

        request = Request(HttpRequest())
        request.data.update(request_data)

        with patch(
            'autodjbackend.utils.get_criteria_to_search',
            return_value=request_data['track_criteria']
        ) as mocked_get_criteria:
            with patch(
                'autodjbackend.utils.get_seed_nodes_from_criteria',
                return_value=expected_tracks
            ) as mocked_get_link_nodes:
                with patch(
                    'autodjbackend.playlist_generator.generate',
                    return_value=expected_output
                ) as mocked_generate:
                    with patch.object(
                        self.view_set, '_raise_if_not_json'
                    ) as mocked_content_type:
                        response = self.view_set.create(request)

                        mocked_get_criteria.assert_called_once()
                        mocked_get_link_nodes.assert_called_once()
                        mocked_generate.assert_called_once()
                        mocked_content_type.assert_called_once()

        actual_output = response.data

        self.assertDictEqual(expected_output, actual_output)

    def test_create_empty(self):
        request = Request(HttpRequest())

        with patch.object(
            self.view_set, '_raise_if_not_json'
        ) as mocked_content_type:
            with self.assertRaises(ParseError):
                self.view_set.create(request)

        mocked_content_type.assert_called_once()

    def test_create_invalid_data(self):
        request_data = {
            'invalid': 'data'
        }

        request = Request(HttpRequest())
        request.data.update(request_data)

        with patch.object(
            self.view_set, '_raise_if_not_json'
        ) as mocked_content_type:
            with self.assertRaises(ParseError):
                self.view_set.create(request)

        mocked_content_type.assert_called_once()

    def test_create_not_json_data(self):
        request_data = {
            'track_criteria': {
                'original_artist': 'artist',
            },
            'total_duration': 4
        }

        request = Request(HttpRequest())
        request.data.update(request_data)

        with self.assertRaises(UnsupportedMediaType):
            self.view_set.create(request)
