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

    def list_claims(self, limit, offset):
        return self.session.query(models.Claim
                ).limit(limit).offset(offset).all()

    def create_claim(self, resource, timeout, user_data):
        claim = models.Claim(resource=resource,
                timeout=datetime.timedelta(seconds=timeout),
                user_data=user_data)
        claim.status_history.append(models.StatusHistory(status='waiting'))
        self.session.add(claim)
        self.session.commit()

        try:
            with self.session.transaction:
                claim.lock = models.Lock(resource=resource,
                    expiration_time=datetime.datetime.utcnow() + claim.timeout)
                claim.status_history.append(
                        models.StatusHistory(status='active'))
            return claim, True
        except sqlalchemy.exc.IntegrityError:
            return claim, False

    def get_claim(self, claim_id):
        return self.session.query(models.Claim).get(claim_id)
