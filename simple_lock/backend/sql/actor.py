from ..base_actor import ActorBase
from . import models
import datetime
import sqlalchemy.exc


__all__ = ['SqlActor']


class SqlActor(ActorBase):
    def __init__(self, session):
        self.session = session

    def cleanup(self):
        self.session.close()

    def list_claims(self, limit, offset, resource, status):
        query = self.session.query(models.Claim)

        if resource is not None:
            query = query.filter_by(resource=resource)
        if status is not None:
            query = query.filter_by(status=status)

        query = query.limit(limit).offset(offset)
        return query.all()

    def create_claim(self, resource, timeout, user_data):
        claim = models.Claim(resource=resource,
                timeout=datetime.timedelta(seconds=timeout),
                user_data=user_data, status='waiting')
        claim.status_history.append(models.StatusHistory(status='waiting'))
        self.session.add(claim)
        self.session.commit()

        try:
            with self.session.transaction:
                claim.lock = models.Lock(resource=resource,
                    expiration_time=datetime.datetime.utcnow() + claim.timeout)
                claim.status = 'active'
                claim.status_history.append(
                        models.StatusHistory(status='active'))
            return claim, True
        except sqlalchemy.exc.IntegrityError:
            return claim, False

    def get_claim(self, claim_id):
        return self.session.query(models.Claim).get(claim_id)
