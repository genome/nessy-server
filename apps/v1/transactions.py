from . import models
from django.db import IntegrityError, transaction


@transaction.atomic
def insert_new_claim(claim):
    claim.save()
    claim.status_history.create(type=models.STATUS_WAITING)

    return claim

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
