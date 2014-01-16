from django.db import connection, models, transaction
from django.utils import timezone

import datetime
import dateutil.parser
import json_field
import pytz
import timedelta


STATUS_WAITING   = 0
STATUS_ACTIVE    = 2
STATUS_RELEASED  = 4
STATUS_ABANDONED = 6
STATUS_EXPIRED   = 8
STATUS_CHOICES = (
    (STATUS_WAITING,   'waiting'),
    (STATUS_ACTIVE,    'active'),
    (STATUS_RELEASED,  'released'),
    (STATUS_ABANDONED, 'abandoned'),
    (STATUS_EXPIRED,   'expired'),
)


class Claim(models.Model):
    creation_time = models.DateTimeField(auto_now=True, db_index=True)

    resource =  models.TextField(db_index=True)
    timeout = timedelta.fields.TimedeltaField()
    current_status = models.IntegerField(choices=STATUS_CHOICES,
            default=STATUS_WAITING)

    metadata = json_field.JSONField()

    class Meta:
        ordering = ['creation_time']

    def refresh(self):
        return Claim.objects.all().get(id=self.id)

    @property
    def is_active(self):
        return self.current_status == STATUS_ACTIVE


    def update_status(self, new_status):
        self.current_status = new_status
        self.save()
        self.status_history.create(type=new_status)


class ClaimStatus(models.Model):
    type = models.IntegerField(choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now=True, db_index=True)
    claim = models.ForeignKey(Claim, related_name='status_history')

    class Meta:
        ordering = ['timestamp']


class Lock(models.Model):
    resource =  models.TextField(unique=True)
    claim = models.ForeignKey(Claim, related_name='lock')

    activation_time = models.DateTimeField(auto_now=True, db_index=True)
    expiration_time = models.DateTimeField(db_index=True)
    expiration_update_time = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ['expiration_time']

    def ttl(self):
        return self.expiration_time - get_now_as_tz()


def get_now_as_tz():
    now = datetime.datetime.now()
    return timezone.make_aware(now, timezone.get_default_timezone())
