from ..exceptions import ConflictException
from sqlalchemy import Column, UniqueConstraint
from sqlalchemy import DateTime, ForeignKey, Enum, Integer, Interval, Text
from sqlalchemy import func, select
from sqlalchemy.orm import backref, column_property, relationship
import datetime
import sqlalchemy.ext.declarative


__all__ = ['Base', 'Claim', 'StatusHistory', 'Lock']


Base = sqlalchemy.ext.declarative.declarative_base()


_VALID_STATUSES = [
    'active',
    'expired',
    'released',
    'revoked',
    'waiting',
]

class Claim(Base):
    __tablename__ = 'claim'

    id = Column(Integer, primary_key=True)
    resource = Column(Text, index=True, nullable=False)
    initial_ttl = Column(Interval, index=True, nullable=False)
    status = Column(Enum(*_VALID_STATUSES, name='foo'), index=True, nullable=False)

    created = Column(DateTime(timezone=True), index=True, default=func.now(),
            nullable=False)
    activated = Column(DateTime(timezone=True), index=True)
    deactivated = Column(DateTime(timezone=True), index=True)

    # XXX Use a native JSON column for postgres
    user_data = Column(Text)

    lock = relationship('Lock', uselist=False, backref='claim')

    now = column_property(select([func.now()]))

    @property
    def ttl(self):
        if self.lock:
            return self.lock.ttl

    @property
    def active_duration(self):
        if self.activated is not None:
            if self.deactivated is not None:
                return self.deactivated - self.activated
            else:
                return self.now - self.activated

    @property
    def waiting_duration(self):
        if self.activated is not None:
            return self.activated - self.created
        elif self.deactivated is not None:
            return self.deactivated - self.created
        else:
            return self.now - self.created

    def get_session(self):
        inspector = sqlalchemy.inspection.inspect(self)
        return inspector.session

    def promote_resource(self, session):
        try:
            claim = session.query(Claim
                    ).filter_by(resource=self.resource, status='waiting',
                    ).order_by(Claim.created).first()
            if claim is not None:
                lock = Lock(claim=claim, resource=self.resource,
                        expiration_time=claim.now + claim.initial_ttl)
                claim.status = 'active'
                claim.activated = claim.now
                claim.status_history.append(
                        StatusHistory(status='active'))
                session.add(lock)
                session.commit()

        except sqlalchemy.exc.IntegrityError:
            session.rollback()

        lock = session.query(Lock
                ).filter_by(resource=self.resource).first()
        if lock:
            return lock.claim

    def activate(self):
        session = self.get_session()
        owner = self.promote_resource(session)

        if owner is not None:
            if owner.id == self.id:
                if owner.status == 'active':
                    return owner

                else:
                    raise ConflictException(claim_id=owner.id,
                            status=owner.status,
                            message='Invalid status for activation:  %s'
                            % owner.status)

            else:
                raise ConflictException(active_claim_id=owner.id,
                        message='Resource is locked by another claim')

        else:
            raise ConflictException(
                message='Found no eligible claims for activating resource:  %s'
                % self.resource)

    def expire(self):
        pass

    def release(self):
        session = self.get_session()

        if self.lock is None:
            raise ConflictException(status=self.status,
                    message='Cannot release inactive claim')

        try:
            session.delete(self.lock)
            self.status = 'released'
            self.status_history.append(StatusHistory(status='released'))
            session.commit()

        except sqlalchemy.exc.IntegrityError:
            # This code is currently not test covered, but it seems necessary.
            session.rollback()
            raise ConflictException(claim_id=self.id,
                    status=self.status,
                    message='Failed to release claim')

        return self

    def revoke(self):
        session = self.get_session()

        query = session.query(Claim
                ).filter_by(id=self.id
                ).with_for_update()
        locked_claim = query.one()

        if locked_claim.status in ['active', 'waiting']:
            locked_claim.status = 'revoked'
            locked_claim.status_history.append(
                    StatusHistory(status='revoked'))
            if locked_claim.lock is not None:
                session.delete(locked_claim.lock)
            session.commit()
        else:
            session.rollback()
            raise ConflictException(claim_id=self.id,
                    status=locked_claim.status,
                    message='Invalid status for revoke')


class StatusHistory(Base):
    __tablename__ = 'status_history'
    __table_args__ = (
            UniqueConstraint('claim_id', 'status'),
            )

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), default=func.now(),
            nullable=False)
    status = Column(Enum(*_VALID_STATUSES, name='foo'), index=True,
            nullable=False)
    claim_id = Column(Integer, ForeignKey('claim.id'), nullable=False)

    claim = relationship('Claim',
            backref=backref('status_history', order_by=timestamp))


class Lock(Base):
    __tablename__ = 'lock'

    id = Column(Integer, primary_key=True)

    resource = Column(Text, unique=True, nullable=False)
    claim_id = Column(Integer, ForeignKey('claim.id'), unique=True,
            nullable=False)

    expiration_time = Column(DateTime(timezone=True), index=True,
            default=func.now(), nullable=False)
    expiration_update_time = Column(DateTime(timezone=True), index=True,
            onupdate=func.now())

    now = column_property(select([func.now()]))

    @property
    def ttl(self):
        return self.expiration_time - self.now
