from . import models
from . import filters
from .. import exceptions
from ..base_actor import ActorBase
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
            return claim.update_ttl(ttl)
        else:
            assert status is not None
            return self._update_status(claim, status)

    def _update_status(self, claim, status):
        if status == 'active':
            return claim.activate()
        elif status == 'released':
            claim.release()
        else:
            assert status == 'revoked'
            claim.revoke()
