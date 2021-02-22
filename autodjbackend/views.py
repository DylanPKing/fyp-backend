from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from autodjbackend import models


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
        # TODO: Pull track attrs from request.data
        # MATCH DB for relevant link nodes
        # Traverse graph using total_duration from request as limit.
        # Compile final traversal into a list to JSONify and return.
        # Add doc comment with correct HTTP syntax.
        total_duration = request.data['total_duration']
        track_criteria = request.data['track_criteria']

        criteria_to_search = self._get_criteria_to_search(track_criteria)

        link_nodes = self._get_link_nodes_from_criteria(criteria_to_search)

        return Response('Hello there')

    def _get_criteria_to_search(self, track_criteria: dict) -> dict:
        criteria_to_search = {}
        for criteria in VALID_CRITERIA:
            if criteria in track_criteria.keys():
                criteria_to_search[criteria] = track_criteria[criteria]

        return criteria_to_search

    def _get_link_nodes_from_criteria(criteria_to_search: dict) -> list:
        link_nodes = []
        for key, value in criteria_to_search.items():
            link_node_class = CRITERA_TO_NODE_MODEL[key]
            params = {key: value}
            link_nodes.append(link_node_class(**params))

        return link_nodes