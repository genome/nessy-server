from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, mixins, status, viewsets
from rest_framework.reverse import reverse
from django.db import IntegrityError, transaction

from . import exceptions
from . import models
from . import serializers
from . import transactions


class ClaimViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = models.Claim.objects.all()
    serializer_class = serializers.ClaimSerializer

    def create(self, request):
        claim = extract_claim(request)
        claim.update_status(models.STATUS_WAITING)
        claim.save()

        with transaction.atomic():
            active_claim = transactions.update_resource_status(claim.resource)

        if claim == active_claim:
            return _make_post_response(request, claim.refresh(),
                    status=status.HTTP_201_CREATED)

        else:
            return _make_post_response(request, claim,
                    status=status.HTTP_202_ACCEPTED)

    def update(self, request, pk=None, partial=False):
        try:
            claim = models.Claim.objects.get(id=pk)
        except models.Claim.DoesNotExist:
            return Response('No such claim (%s)' % pk,
                    status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                transactions.update_resource_status(claim.resource)

        except IntegrityError:
            raise exceptions.LockContention('Bad times')

        serializer = serializers.ClaimSerializer(claim.refresh(),
                data=request.DATA, partial=partial,
                context={'request': request})

        if serializer.is_valid():
            # XXX Is doing serializer.save outside the transaction a race?
            # maybe if we're trying to abandon a claim and it gets promoted?
            result_object = serializer.save()

            return Response(serializer.data)

        else:
            return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        return self.update(request, pk=pk, partial=True)



def extract_claim(request, pk=None):
    if pk is not None:
        claim = models.Claim.objects.get(id=pk)
        serializer = serializers.ClaimSerializer(claim, data=request.DATA,
                context={'request': request})
    else:
        serializer = serializers.ClaimSerializer(data=request.DATA,
                context={'request': request})

    if serializer.is_valid():
        claim = serializer.object
        return claim
    else:
        raise exceptions.InvalidRequest(serializer.errors)


def _make_update_response(request, claim, status):
    serializer = serializers.ClaimSerializer(claim,
            context={'request': request})
    return Response(serializer.data, status=status)

def _make_post_response(request, claim, status):
    response = _make_update_response(request, claim, status)
    response['Location'] = reverse('claim-detail', kwargs={'pk': claim.id},
            request=request)
    return response
