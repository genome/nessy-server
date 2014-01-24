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

    def list_claims(self, limit, offset, resource, status,
            minimum_active_duration, maximum_active_duration,
            minimum_waiting_duration, maximum_waiting_duration):

        query = self.session.query(models.Claim)

        if resource is not None:
            query = query.filter_by(resource=resource)
        if status is not None:
            query = query.filter_by(status=status)

        if minimum_active_duration is not None:
            minimum_active_duration = datetime.timedelta(
                    seconds=minimum_active_duration)
            finished_claims = query.filter(
                    models.Claim._done_active_duration != None,
                    models.Claim._done_active_duration
                        >= minimum_active_duration)
            active_claims = query.filter(
                    models.Claim._live_active_duration != None,
                    models.Claim._live_active_duration
                        >= minimum_active_duration)
            query = finished_claims.union(active_claims)

        if maximum_active_duration is not None:
            maximum_active_duration = datetime.timedelta(
                    seconds=maximum_active_duration)
            finished_claims = query.filter(
                    models.Claim._done_active_duration != None,
                    models.Claim._done_active_duration
                        <= maximum_active_duration)
            active_claims = query.filter(
                    models.Claim._live_active_duration != None,
                    models.Claim._live_active_duration
                        <= maximum_active_duration)
            query = finished_claims.union(active_claims)

        if minimum_waiting_duration is not None:
            minimum_waiting_duration = datetime.timedelta(
                    seconds=minimum_waiting_duration)
            activated_claims = query.filter(
                    models.Claim.activated != None,
                    models.Claim._done_waiting_duration
                        >= minimum_waiting_duration)

            deactivated_claims = query.filter(
                    models.Claim.activated == None,
                    models.Claim.deactivated != None,
                    models.Claim._skip_waiting_duration
                        >= minimum_waiting_duration)

            currently_waiting_claims = query.filter(
                    models.Claim.activated == None,
                    models.Claim.deactivated == None,
                    models.Claim._still_waiting_duration
                        >= minimum_waiting_duration)

            query = activated_claims.union(deactivated_claims,
                    currently_waiting_claims)

        if maximum_waiting_duration is not None:
            maximum_waiting_duration = datetime.timedelta(
                    seconds=maximum_waiting_duration)
            activated_claims = query.filter(
                    models.Claim.activated != None,
                    models.Claim._done_waiting_duration
                        <= maximum_waiting_duration)

            deactivated_claims = query.filter(
                    models.Claim.activated == None,
                    models.Claim.deactivated != None,
                    models.Claim._skip_waiting_duration
                        <= maximum_waiting_duration)

            currently_waiting_claims = query.filter(
                    models.Claim.activated == None,
                    models.Claim.deactivated == None,
                    models.Claim._still_waiting_duration
                        <= maximum_waiting_duration)

            query = activated_claims.union(deactivated_claims,
                    currently_waiting_claims)


        query = query.limit(limit).offset(offset)
        return query.all()

    def create_claim(self, resource, timeout, user_data):
        claim = models.Claim(resource=resource,
                timeout=datetime.timedelta(seconds=timeout),
                user_data=user_data, status='waiting')
        claim.status_history.append(models.StatusHistory(status='waiting'))
        self.session.add(claim)
        self.session.commit()

        owning_claim = self._promote_resource(resource)
        if owning_claim is not None and claim.id == owning_claim.id:
            return owning_claim, True
        else:
            return claim, False

    def _promote_resource(self, resource):
        try:
            claim = self.session.query(models.Claim
                    ).filter_by(resource=resource, status='waiting',
                    ).order_by(models.Claim.created).first()
            if claim is not None:
                lock = models.Lock(claim=claim, resource=resource,
                        expiration_time=claim.now + claim.timeout)
                claim.status = 'active'
                claim.activated = claim.now
                claim.status_history.append(
                        models.StatusHistory(status='active'))
                self.session.add(lock)
                self.session.commit()

        except sqlalchemy.exc.IntegrityError:
            self.session.rollback()

        lock = self.session.query(models.Lock
                ).filter_by(resource=resource).first()
        if lock:
            return lock.claim

    def get_claim(self, claim_id):
        return self.session.query(models.Claim).get(claim_id)
