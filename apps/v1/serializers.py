from rest_framework import serializers

from . import models


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Request


class LockSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lock
