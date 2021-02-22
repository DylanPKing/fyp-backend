from neomodel.core import StructuredNode

from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from autodjbackend import models, playlist_generator


VALID_CRITERIA = [
    'track_number',
    'year',
    'original_artist',
    'keyword_in_title',
]

CRITERA_TO_NODE_MODEL = {
    'track_number': models.SameTrackNumber,
    'year': models.SameYear,
    'original_artist': models.SameOriginalArtist,
    'keyword_in_title': models.KeywordInTitle,
}

MINUTES_TO_MILLISECONDS = 60000


class CreatePlaylistViewSet(viewsets.ViewSet):

    def create(self, request: Request) -> Response:
        """
        Generates a new playlist based on request criteria.

        This endpoint receives parameters from a client with criterai for the
        playlist to adhere to, and then traverses a subset of the DB to
        generate this playlist to return.

        Args:
            request (rest_framework.request.Request:
                Request sent by the client.

        Returns:
            rest_framework.response.Response: A HTTP response with the
                generated playlist.

        Request format:
            URL: /api/generate/
            Method: POST
            Data:
                {
                    track_criteria : {
                        track_number : [integer],
                        year : [integer],
                        original_artist : [string],
                        keyword_in_title : [string]
                    },
                    total_duration : [integer]
                }
            Successful Repsonse:
                Code: 200
                Content:
                    {
                        tracks : [[autodjbackend.models.Track]],
                        total_duration : [integer]
                    }
            Error Response:
                Code: 422 Unprocessable Entry
                Content:
                    {
                        error : "Unable to generate playlist from criteria"
                    }

            Sample Call:
                curl -X POST -H "Content-Type: application/json" \
                    --data '{"criteria":{"original_artist":"Bob Dylan"},"total_duration":3600}' \
                    /api/generate/
        """
        total_duration = (
            request.data['total_duration'] * MINUTES_TO_MILLISECONDS
        )

        criteria_to_search: dict() = self._get_criteria_to_search(
            request.data['track_criteria']
        )

        link_nodes: list(StructuredNode) = self._get_link_nodes_from_criteria(
            criteria_to_search
        )

        playlist: list(models.Track) = playlist_generator.generate(
            link_nodes, total_duration
        )

        resp_data = {
            'tracks': [],
            'total_duration': 0,
        }
        for track in playlist:
            resp_data['tracks'].append(track.serialize)
            resp_data['total_duration'] += track.duration

        return Response(resp_data)

    def _get_criteria_to_search(self, track_criteria: dict) -> dict:
        criteria_to_search = {}
        for criteria in VALID_CRITERIA:
            try:
                criteria_to_search[criteria] = track_criteria[criteria]
            except KeyError:
                pass

        return criteria_to_search

    def _get_link_nodes_from_criteria(self, criteria_to_search: dict) -> list:
        link_nodes = []
        for key, value in criteria_to_search.items():
            link_node_class = CRITERA_TO_NODE_MODEL[key]
            params = {key: value}
            link_nodes.extend(link_node_class.nodes.filter(**params))

        return link_nodes
