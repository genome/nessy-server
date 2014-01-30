from . import models
from . import translations
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

        query = translations.resource_equal(query, resource)
        query = translations.status_equal(query, status)

        query = translations.ttl_range(query, minimum_ttl, maximum_ttl)

        query = translations.active_duration_range(query,
                minimum_active_duration, maximum_active_duration)
        query = translations.waiting_duration_range(query,
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

        owning_claim = claim.promote_resource(self.session)
        if owning_claim is not None and claim.id == owning_claim.id:
            return owning_claim, True
        else:
            return claim, False

    def get_claim(self, claim_id):
        return self.session.query(models.Claim).get(claim_id)

    def update_claim(self, claim_id, status, ttl):
        claim = self.session.query(models.Claim).get(claim_id)

        if claim is None:
            raise exceptions.ClaimNotFound(claim_id=claim_id)

        if status == 'active':
            return claim.activate()
        elif status == 'released':
            claim.release()
            return
        else:
            assert status == 'revoked'
            claim.revoke()
            return
