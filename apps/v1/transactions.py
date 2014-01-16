from . import models
from django.db import IntegrityError, transaction
import datetime


def update_resource_status(resource):
    try:
        _expire_lock_for_resource_if_timed_out(resource)
    except IntegrityError:
        pass

    _promote_lock_for_resource(resource)

def _expire_lock_for_resource_if_timed_out(resource):
    try:
        lock = models.Lock.objects.get(resource=resource)
        if lock.ttl().total_seconds() < 0:
            claim = lock.claim
            claim.update_status(models.STATUS_EXPIRED)
            lock.delete()
            lock.save()

    except models.Lock.DoesNotExist:
        pass

def _promote_lock_for_resource(resource):
    try:
        claim = models.Claim.objects.filter(resource=resource,
                current_status=models.STATUS_WAITING).earliest('creation_time')
    except models.Claim.DoesNotExist:
        return

    expiration_time = models.get_now_as_tz() + claim.timeout
    lock = models.Lock.objects.create(resource=claim.resource, claim=claim,
            expiration_time=expiration_time)
    claim.update_status(models.STATUS_ACTIVE)


def release_claim(claim):
    lock = claim.lock.get()
    lock.delete()
    claim.update_status(models.STATUS_RELEASED)
