from . import models
from django.db import IntegrityError, transaction


@transaction.atomic
def insert_new_claim(claim):
    claim.save()
    claim.status_history.create(type=models.STATUS_WAITING)

    return claim

def promote_lock(resource):
    now = models.get_canonical_time()
    return _promote_lock(resource, now)

@transaction.atomic
def _promote_lock(resource, now):
    _expire_lock(resource, now)
    claim = models.Claim.objects.filter(resource=resource
            ).earliest('creation_time')
    insert_lock(claim)

@transaction.atomic
def _expire_lock(resource, now):
    try:
        lock = models.Lock.objects.filter(resource=resource,
                expiration_time__lt=now).get()
        release_lock(lock.claim)

    except models.Lock.DoesNotExist:
        pass

@transaction.atomic
def insert_lock(claim):
    lock = models.Lock(resource=claim.resource, claim=claim,
            expiration_time=claim.timeout)
    lock.save()
    claim.status_history.create(type=models.STATUS_ACTIVE)

    return lock

@transaction.atomic
def release_lock(claim):
    lock = claim.lock.get()
    lock.delete()
    claim.status_history.create(type=models.STATUS_RELEASED)
