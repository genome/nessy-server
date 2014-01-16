from django.db import connection, models

import datetime
import dateutil.parser
import json_field
import pytz
import timedelta

class AutoNowDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        return get_canonical_time()

class AutoNowPlusDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        now = get_canonical_time()
        return now + getattr(model_instance, self.attname, 0)

class Claim(models.Model):
    creation_time = AutoNowDateTimeField(db_index=True)

    resource =  models.TextField(db_index=True)
    timeout = timedelta.fields.TimedeltaField()

    metadata = json_field.JSONField()

    class Meta:
        ordering = ['creation_time']

    def current_status(self):
        try:
            # Manually find the latest, since 'latest' is hitting the cache
            sh_list = list(self.status_history.all())
            return sh_list[-1].get_type_display()
        except ClaimStatus.DoesNotExist:
            return None


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
class ClaimStatus(models.Model):
    type = models.IntegerField(choices=STATUS_CHOICES)
    timestamp = AutoNowDateTimeField(db_index=True)
    claim = models.ForeignKey(Claim, related_name='status_history')

    class Meta:
        ordering = ['timestamp']


class Lock(models.Model):
    resource =  models.TextField(unique=True)
    claim = models.ForeignKey(Claim, related_name='lock')

    activation_time = AutoNowDateTimeField(db_index=True)
    expiration_time = AutoNowPlusDateTimeField(db_index=True)
    expiration_update_time = AutoNowDateTimeField(db_index=True)

    class Meta:
        ordering = ['expiration_time']

    def ttl(self):
        return self.expiration_time - get_canonical_time()


def get_canonical_time():
    cursor = connection.cursor()
    result = cursor.execute('select current_timestamp')
    rows = result.fetchall()
    now = dateutil.parser.parse(rows[0][0])
    if now.tzinfo is None:
        now = now.replace(tzinfo=pytz.timezone('UTC'))
    return now
