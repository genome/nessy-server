from django.db import models

import json_field
import timedelta


class Resource(models.Model):
    name = models.TextField(unique=True)


STATUS_CHOICES = (
    (0, 'waiting'),
    (2, 'active'),
    (4, 'released'),
    (6, 'abandoned'),
    (8, 'deleted'),
)
class RequestStatus(models.Model):
    type = models.IntegerField(choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ['timestamp']


class Request(models.Model):
    creation_time = models.DateTimeField(auto_now=True)

    resource = models.ForeignKey(Resource, related_name='requests')
    statuses = models.ForeignKey(RequestStatus)
    timeout = timedelta.fields.TimedeltaField()

    requester_data = json_field.JSONField()

    class Meta:
        ordering = ['creation_time']


class Lock(models.Model):
    resource = models.ForeignKey(Resource, related_name='lock')
    request = models.ForeignKey(Request, related_name='lock')
    expiration_time = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ('resource', 'request')
        ordering = ['expiration_time']
