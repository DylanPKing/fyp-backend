import logging

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

from autodjbackend import playlist_generator, utils


logger = logging.getLogger(__name__)

MINUTES_TO_MILLISECONDS = 60000


class CreatePlaylistViewSet(ViewSet):

    def create(self, request):
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
                        msg : "Unable to generate playlist from criteria"
                    }

            Sample Call:
                curl -X POST -H "Content-Type: application/json" \
                    --data '{"criteria":{"original_artist":"Bob Dylan"},"total_duration":3600}' \  # noqa: E501, W605
                    /api/generate/
        """

        request_data = request.data

        try:
            total_duration = (
                request_data['total_duration'] * MINUTES_TO_MILLISECONDS
            )

            criteria_to_search = utils.get_criteria_to_search(
                request_data['track_criteria']
            )
        except KeyError as err:
            err_string = f'Request missing data: {err}'
            logger.info(err_string)
            raise ParseError(detail=err_string)

        link_nodes = utils.get_link_nodes_from_criteria(criteria_to_search)

        playlist = playlist_generator.generate(link_nodes, total_duration)

        resp_data = {
            'tracks': [],
            'total_duration': 0,
        }

        for track in playlist:
            resp_data['tracks'].append(track.serialize)
            resp_data['total_duration'] += track.duration

        return Response(resp_data)
