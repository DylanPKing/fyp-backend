import logging

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, UnsupportedMediaType

from autodjbackend import playlist_generator, utils


logger = logging.getLogger(__name__)


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
                        position : [integer],
                        year : [integer],
                        original_artist : [string],
                        keyword_in_title : [string]
                    },
                    tracks_to_include : [[
                        title : [string],
                        artist : [string]
                    ]]
                    total_duration : [integer],
                    tolerance_window : [integer]
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
        self._raise_if_not_json(request.content_type)

        request_data = request.data

        try:
            total_duration = (
                playlist_generator.minutes_to_milliseconds(
                    request_data['total_duration']
                )
            )

            criteria_to_search = utils.get_criteria_to_search(
                request_data['track_criteria']
            )
        except KeyError as err:
            err_string = f'Request missing data: {err}'
            logger.debug(err_string)
            raise ParseError(detail=err_string)

        user_time_window = request_data.get('tolerance_window', 1)

        try:
            user_tracks_list = request_data['tracks_to_include']
        except KeyError:
            logger.info('No user-specified tracks.')
            seed_nodes = utils.get_seed_nodes_from_criteria(criteria_to_search)
            user_tracks = None
        else:
            user_tracks = [
                utils.get_seed_nodes_from_criteria(track)
                for track in user_tracks_list
            ]
            user_tracks = [
                track[0] for track in user_tracks if track != []
            ]
            seed_nodes = None

        resp_data = playlist_generator.generate(
            seed_nodes, criteria_to_search, total_duration,
            user_tracks, user_time_window
        )

        return Response(resp_data)

    def _raise_if_not_json(self, content_type):
        if content_type != 'application/json':
            raise UnsupportedMediaType(content_type)
