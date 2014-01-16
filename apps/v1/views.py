from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, mixins, status, viewsets
from rest_framework.reverse import reverse
from django.db import IntegrityError, transaction

from . import models
from . import serializers


class ClaimViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = models.Claim.objects.all()
    serializer_class = serializers.ClaimSerializer

    def create(self, request):
        request_serializer = serializers.ClaimSerializer(data=request.DATA)
        if request_serializer.is_valid():
            claim = request_serializer.object
            _insert_new_claim(claim)

            try:
                _insert_lock(claim)
                return _make_post_response(claim,
                        status=status.HTTP_201_CREATED)

            except IntegrityError:
                return _make_post_response(claim,
                        status=status.HTTP_202_ACCEPTED)

        else:
            return Response(request_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass

@transaction.atomic
def _insert_new_claim(claim):
    claim.save()
    claim.status_history.create(type=models.STATUS_WAITING)

    return claim

@transaction.atomic
def _insert_lock(claim):
    lock = models.Lock(resource=claim.resource, claim=claim,
            expiration_time=claim.timeout)
    claim.status_history.create(type=models.STATUS_ACTIVE)

    return lock

def _make_post_response(claim, status):
    serializer = serializers.ClaimSerializer(claim)
    response = Response(serializer.data, status=status)
    response['Location'] = reverse('claim-detail', kwargs={'pk': claim.id})
    return response
