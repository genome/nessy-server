from django.db import connection, models

import datetime
import dateutil.parser
import json_field
import pytz
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
    resource =  models.TextField(unique=True)
    claim = models.ForeignKey(Claim, related_name='lock')

    activation_time = models.DateTimeField(auto_now=True, db_index=True)
    expiration_time = models.DateTimeField(auto_now_add=True, db_index=True)
    expiration_update_time = models.DateTimeField(auto_now_add=True,
            db_index=True)

    class Meta:
        ordering = ['expiration_time']

    def ttl(self):
        cursor = connection.cursor()
        result = cursor.execute('select current_timestamp')
        rows = result.fetchall()
        now = dateutil.parser.parse(rows[0][0])
        if now.tzinfo is None:
            now = now.replace(tzinfo=pytz.timezone('UTC'))
        return self.expiration_time - now
