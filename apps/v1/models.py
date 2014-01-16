from django.db import models

import json_field
import timedelta


class Claim(models.Model):
    creation_time = models.DateTimeField(auto_now=True)

    resource =  models.TextField(db_index=True)
    timeout = timedelta.fields.TimedeltaField()

    metadata = json_field.JSONField()

    class Meta:
        ordering = ['creation_time']


STATUS_WAITING   = 0
STATUS_ACTIVE    = 2
STATUS_RELEASED  = 4
STATUS_ABANDONED = 6
STATUS_LOOKUP = {
    STATUS_WAITING:   'waiting',
    STATUS_ACTIVE:    'active',
    STATUS_RELEASED:  'released',
    STATUS_ABANDONED: 'abandoned',
}

STATUS_CHOICES = (
    (STATUS_WAITING,   STATUS_LOOKUP[STATUS_WAITING]),
    (STATUS_ACTIVE,    STATUS_LOOKUP[STATUS_ACTIVE]),
    (STATUS_RELEASED,  STATUS_LOOKUP[STATUS_RELEASED]),
    (STATUS_ABANDONED, STATUS_LOOKUP[STATUS_ABANDONED]),
)
class ClaimStatus(models.Model):
    type = models.IntegerField(choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now=True, db_index=True)
    claim = models.ForeignKey(Claim, related_name='status_history')

    class Meta:
        ordering = ['timestamp']


class Lock(models.Model):
    resource =  models.TextField(db_index=True)
    claim = models.ForeignKey(Claim, related_name='lock')

    activation_time = models.DateTimeField(auto_now=True, db_index=True)
    expiration_time = models.DateTimeField(auto_now_add=True, db_index=True)
    expiration_update_time = models.DateTimeField(auto_now_add=True,
            db_index=True)

    class Meta:
        unique_together = ('resource', 'claim')
        ordering = ['expiration_time']
