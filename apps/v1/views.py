from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, mixins, status
from rest_framework.reverse import reverse

from . import models
from . import serializers


class LockListView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = models.Lock.objects.all()
    serializer_class = serializers.LockSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class OwnerDetailView(APIView):
    def get(self, request, resource_name):
        return Response('hi')


class RequestListView(APIView):
    def get(self, request, resource_name):
        return Response('hi')

    def post(self, request, resource_name):
        return Response(status=status.HTTP_201_CREATED)


class RequestDetailView(APIView):
    def get(self, request, resource_name, request_id):
        return Response('hi')

    def patch(self, request, resource_name, request_id):
        return Response('hi')

    def put(self, request, resource_name, request_id):
        return Response('hi')

    def delete(self, request, resource_name, request_id):
        return Response('hi')


class APIRootView(APIView):
    def get(self, request, format=None):
        return Response({
            'locks': reverse('lock-list', request=request, format=format),
        })
