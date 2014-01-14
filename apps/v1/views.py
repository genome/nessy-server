from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status

from libs import lock

class LockViewSet(ViewSet):
    def create(self, request):
        return Response('hi', status=status.HTTP_201_CREATED)

    def list(self, request):
        return Response('hi')

    def retrieve(self, request, pk=None):
        return Response('hi')

    def update(self, request, pk=None):
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk=None):
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResourceViewSet(ViewSet):
    def list(self, request):
        return Response('hi')

    def retrieve(self, request, pk=None):
        return Response('hi')

    def destroy(self, request, pk=None):
        return Response(status=status.HTTP_204_NO_CONTENT)
