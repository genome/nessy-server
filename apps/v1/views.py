from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, mixins, status
from rest_framework.reverse import reverse
from django.db import IntegrityError, transaction

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
        resource, _ = models.Resource.objects.get_or_create(name=resource_name)

        data = request.DATA
        data['resource'] = resource_name
        serializer = serializers.RequestSerializer(data=data)

        if serializer.is_valid():
            lock_request = _insert_new_lock_request(serializer.object)

            try:
                lock = _insert_new_lock(lock_request)
                response_serializer = serializers.RequestSerializer(
                        lock_request)
                return Response(response_serializer.data,
                        status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(response_serializer.data,
                        status=status.HTTP_202_ACCEPTED)
        else:
            return Response('More descriptive', status=status.HTTP_400)


@transaction.atomic
def _insert_new_lock_request(lock_request):
    lock_request.save()
    lock_request.statuses.create(type=models.STATUS_WAITING)

    return lock_request

@transaction.atomic
def _insert_new_lock(lock_request):
    lock = models.Lock(resource=lock_request.resource, request=lock_request,
            expiration_time=lock_request.timeout)
    lock_request.statuses.create(type=models.STATUS_ACTIVE)

    return lock


class RequestListView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = models.Request.objects.all()
    serializer_class = serializers.RequestSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


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
            'requests': reverse('request-list', request=request, format=format),
        })
