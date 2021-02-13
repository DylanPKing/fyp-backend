from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response


class CreatePlaylistViewSet(viewsets.ViewSet):

    def create(self, request: Request) -> Response:
        # TODO: Pull track attrs form request.data
        # MATCH DB for relevant tracks
        # Traverse graph using total_duration from request as limit.
        # Compile final traversal into a list to JSONify and return.
        # Add doc comment with correct HTTP syntax.
        return Response('Hello there')
