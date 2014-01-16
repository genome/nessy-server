from . import models
from django.db import IntegrityError, transaction


@transaction.atomic
def insert_new_claim(claim):
    claim.current_status = models.STATUS_WAITING
    claim.save()
    claim.status_history.create(type=models.STATUS_WAITING)

    return claim

def promote_claim(claim):
    try:
        result_claim = promote_lock(claim.resource)
        return claim == result_claim
    except IntegrityError:
        return False

def promote_lock(resource):
#    now = models.get_canonical_time()
#    _expire_lock(resource, now)
    try:
        return _promote_lock(resource)
    except IntegrityError:
        pass

@transaction.atomic
def _promote_lock(resource):
    claim = models.Claim.objects.filter(resource=resource,
            current_status=models.STATUS_WAITING).earliest('creation_time')
    if claim.current_status == models.STATUS_WAITING:
        insert_lock(claim)
    return claim

@transaction.atomic
def _expire_lock(resource, now):
    try:
        lock = models.Lock.objects.filter(resource=resource,
                expiration_time__lt=now).get()
        claim = lock.claim
        lock.delete()
        claim.current_status = models.STATUS_EXPIRED
        claim.save()
        claim.status_history.create(type=models.STATUS_EXPIRED)

    except models.Lock.DoesNotExist:
        pass

@transaction.atomic
def insert_lock(claim):
    lock = models.Lock(resource=claim.resource, claim=claim,
            expiration_time=claim.timeout)
    lock.save()
    claim.current_status = models.STATUS_ACTIVE
    claim.save()
    claim.status_history.create(type=models.STATUS_ACTIVE)

    return lock

@transaction.atomic
def release_lock(claim):
    lock = claim.lock.get()
    lock.delete()
    claim.current_status = models.STATUS_RELEASED
    claim.save()
    claim.status_history.create(type=models.STATUS_RELEASED)
