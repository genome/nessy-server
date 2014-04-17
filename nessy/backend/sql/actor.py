from . import models
from . import filters
from .. import exceptions
from ..base_actor import ActorBase
from sqlalchemy import func
import datetime
import sqlalchemy.exc


__all__ = ['SqlActor']


class SqlActor(ActorBase):
    def __init__(self, session):
        self.session = session

    def cleanup(self):
        self.session.close()

    def list_claims(self, limit, offset, resource, status,
            minimum_ttl, maximum_ttl,
            minimum_active_duration, maximum_active_duration,
            minimum_waiting_duration, maximum_waiting_duration):

        query = self.session.query(models.Claim)

        query = filters.resource_equal(query, resource)
        query = filters.status_equal(query, status)

        query = filters.ttl_range(query, minimum_ttl, maximum_ttl)

        query = filters.active_duration_range(query,
                minimum_active_duration, maximum_active_duration)
        query = filters.waiting_duration_range(query,
                minimum_waiting_duration, maximum_waiting_duration)

        query = query.limit(limit).offset(offset)
        return query.all()

    def create_claim(self, resource, ttl, user_data):
        claim = models.Claim(resource=resource,
                initial_ttl=datetime.timedelta(seconds=ttl),
                user_data=user_data, status='waiting')
        claim.status_history.append(models.StatusHistory(status='waiting'))
        self.session.add(claim)
        self.session.commit()

        res = models.Resource(resource, session=self.session)
        res.promote()
        owner_id = res.owner_id
        if owner_id is not None and claim.id == owner_id:
            return claim, True
        else:
            return claim, False

    def get_claim(self, claim_id):
        return self.session.query(models.Claim).get(claim_id)

    def update_claim(self, claim_id, status, ttl):
        claim = self.session.query(models.Claim).get(claim_id)

        if claim is None:
            raise exceptions.ClaimNotFound(claim_id=claim_id)

        if ttl is not None:
            return self._update_ttl(claim, ttl)
        else:
            assert status is not None
            return self._update_status(claim, status)

    def _update_ttl(self, claim, new_ttl):
        resource = models.Resource(claim.resource, session=self.session)
        resource.expire_owning_claim()

        count = self.session.query(models.Lock
                ).filter_by(claim_id=claim.id).update({
                    'expiration_time':
                        func.now() + datetime.timedelta(seconds=new_ttl)},
                synchronize_session=False)

        if count == 1:
            self.session.commit()
            return claim

        else:
            self.session.rollback()
            raise exceptions.InvalidRequest(claim_id=claim.id,
                    status=claim.status, message='Failed to update ttl')

    def _update_status(self, claim, status):
        if status == 'active':
            return self._activate(claim)

        elif status == 'released':
            self._release(claim)

        elif status == 'withdrawn':
            self._withdraw(claim)

        elif status == 'aborted':
            self._abort(claim)

        elif status == 'revoked':
            self._revoke(claim)

        else:  # pragma: no cover
            # The view is currently forbidding this, but we should still raise
            # a reasonable exception here.
            assert False

    def _activate(self, claim):
        resource = models.Resource(claim.resource, session=self.session)
        resource.promote()
        owner_id = resource.owner_id

        if owner_id is not None:
            if owner_id == claim.id:
                return claim

            elif claim.status == 'waiting':
                raise exceptions.ConflictException(active_claim_id=owner_id,
                        message='Resource is locked by another claim')
            else:
                raise exceptions.InvalidRequest(
                        message='Claim has invalid status.',
                        status=claim.status)

        else:
            raise exceptions.InvalidRequest(
                message='Found no eligible claims for activating resource:  %s'
                % claim.resource)

    def _release(self, claim):
        count = self.session.query(models.Lock
                ).filter_by(claim_id=claim.id).delete()
        if count != 1:
            raise exceptions.InvalidRequest(claim_id=claim.id,
                    status=claim.status, message='Failed to remove lock.')

        claim.set_status('released')
        self.session.commit()

    def _withdraw(self, claim):
        self._cancel(claim, 'withdrawn')

    def _abort(self, claim):
        self._cancel(claim, 'aborted')

    def _revoke(self, claim):
        self._cancel(claim, 'revoked')

    def _cancel(self, claim, status):
        query = self.session.query(models.Claim
                ).filter_by(id=claim.id
                ).with_for_update()
        locked_claim = query.one()

        if locked_claim.status in ['active', 'waiting']:
            locked_claim.set_status(status)
            if locked_claim.lock is not None:
                self.session.delete(locked_claim.lock)
            self.session.commit()
        else:
            self.session.rollback()
            raise exceptions.InvalidRequest(claim_id=claim.id,
                    status=locked_claim.status,
                    message='Invalid status for cancellation')
