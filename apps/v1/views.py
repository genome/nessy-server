from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, mixins, status, viewsets
from rest_framework.reverse import reverse
from django.db import IntegrityError

from . import models
from . import serializers
from . import transactions


class ClaimViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet):
    queryset = models.Claim.objects.all()
    serializer_class = serializers.ClaimSerializer

    def create(self, request):
        request_serializer = serializers.ClaimSerializer(data=request.DATA)
        if request_serializer.is_valid():
            claim = request_serializer.object
            transactions.insert_new_claim(claim)

            try:
                transactions.insert_lock(claim)
                return _make_post_response(request, claim,
                        status=status.HTTP_201_CREATED)

            except IntegrityError:
                return _make_post_response(request, claim,
                        status=status.HTTP_202_ACCEPTED)

        else:
            return Response(request_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)


def _make_post_response(request, claim, status):
    serializer = serializers.ClaimSerializer(claim)
    response = Response(serializer.data, status=status)
    response['Location'] = reverse('claim-detail', kwargs={'pk': claim.id},
            request=request)
    return response
