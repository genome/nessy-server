from django.db import models

import json_field
import timedelta


class Resource(models.Model):
    name = models.TextField(primary_key=True)


class Request(models.Model):
    creation_time = models.DateTimeField(auto_now=True)

    resource = models.ForeignKey(Resource, related_name='requests')
    timeout = timedelta.fields.TimedeltaField()

#    requester_data = json_field.JSONField()

    class Meta:
        ordering = ['creation_time']


STATUS_WAITING   = 0
STATUS_ACTIVE    = 2
STATUS_RELEASED  = 4
STATUS_ABANDONED = 6
STATUS_CHOICES = (
    (STATUS_WAITING,   'waiting'),
    (STATUS_ACTIVE,    'active'),
    (STATUS_RELEASED,  'released'),
    (STATUS_ABANDONED, 'abandoned'),
)
class RequestStatus(models.Model):
    type = models.IntegerField(choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now=True, db_index=True)
    request = models.ForeignKey(Request, related_name='statuses')

    class Meta:
        ordering = ['timestamp']


class Lock(models.Model):
    resource = models.ForeignKey(Resource, related_name='lock')
    request = models.ForeignKey(Request, related_name='lock')

    creation_time = models.DateTimeField(auto_now=True, db_index=True)
    expiration_time = models.DateTimeField(auto_now_add=True, db_index=True)
    expiration_update_time = models.DateTimeField(auto_now_add=True,
            db_index=True)

    class Meta:
        unique_together = ('resource', 'request')
        ordering = ['expiration_time']
