from . import exceptions
from . import models
from . import transactions
from django.db import IntegrityError
from rest_framework import serializers

import datetime


class TimeDeltaField(serializers.FloatField):
    default_error_messages = {
        'invalid': "'%s' could not be cast as a timedelta object",
    }

    def from_native(self, value):
        validated_value = serializers.FloatField.from_native(self, value)
        try:
            return datetime.timedelta(seconds=validated_value)
        except TypeError, ValueError:
            msg = self.error_messages['invalid'] % value
            raise serializers.ValidationError(msg)

    def to_native(self, value):
        return value.total_seconds()


class CurrentStatusField(serializers.WritableField):
    def field_from_native(self, data, files, field_name, into):
        claim = self.parent.object
        if claim is not None:
            desired_status = data['current_status']
            if desired_status == 'active':
                transactions.promote_lock(claim.resource)
                if claim.current_status() != 'active':
                    raise exceptions.LockContention()

            elif desired_status == 'released':
                try:
                    transactions.release_lock(claim)
                except models.Lock.DoesNotExist:
                    pass

    def field_to_native(self, obj, field_name):
        return obj.current_status()


class StatusHistorySerializer(serializers.ModelSerializer):
    type = serializers.Field(source='get_type_display')
    class Meta:
        model = models.ClaimStatus
        fields = ('type', 'timestamp')


class TTLField(serializers.WritableField):
    def field_from_native(self, data, files, field_name, into):
        obj = self.parent.object
        if obj:
            try:
                lock = models.Lock.objects.filter(claim=obj).get()
                lock.expiration_time = obj.timeout
                lock.save()
            except models.Lock.DoesNotExist:
                pass

    def field_to_native(self, obj, field_name):
        if obj:
            try:
                lock = models.Lock.objects.filter(claim=obj).get()
                return lock.ttl().total_seconds()
            except models.Lock.DoesNotExist:
                pass

        return None


class ClaimSerializer(serializers.HyperlinkedModelSerializer):
    current_status = CurrentStatusField(required=False)
    metadata = serializers.WritableField()
    resource = serializers.CharField()
    status_history = StatusHistorySerializer(many=True, read_only=True)
    timeout = TimeDeltaField()

    ttl = TTLField(required=False)

    class Meta:
        model = models.Claim
        fields = ('url',
                'current_status',
                'metadata',
                'resource',
                'status_history',
                'timeout',
                'ttl',
                )

    def validate_timeout(self, attrs, source):
        if attrs[source].total_seconds() < 0:
            raise serializers.ValidationError('timeout cannot be negative')
        return attrs
