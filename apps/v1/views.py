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


class LockDetailView(APIView):
    def get(self, request, resource_name):
        return Response('hi')


class OwnerDetailView(APIView):
    def get(self, request, resource_name):
        return Response('hi')


class RequestListView(APIView):
    def get(self, request, resource_name):
        return Response('hi')

    def post(self, request, resource_name):
        serializer = serializers.RequestSerializer(data=request.DATA)
        return Response(status=status.HTTP_201_CREATED)


class RequestDetailView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = models.Request.objects.all()
    serializer_class = serializers.RequestSerializer

    def patch(self, request, request_id):
        return Response('hi')

    def put(self, request, request_id):
        return Response('hi')

    def delete(self, request, request_id):
        return Response('hi')


class APIRootView(APIView):
    def get(self, request, format=None):
        return Response({
            'locks': reverse('lock-list', request=request, format=format),
        })
