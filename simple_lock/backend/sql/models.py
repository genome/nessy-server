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

    def activate(self):
        inspector = sqlalchemy.inspection.inspect(self)
        session = inspector.session

        query = session.query(Claim
                ).filter_by(id=self.id
                ).with_for_update()
        locked_claim = query.one()

        if locked_claim.status == 'active':
            session.rollback()
        elif locked_claim.status == 'waiting':
            locked_claim.status = 'active'
            locked_claim.status_history.append(
                    StatusHistory(status='active'))
            session.commit()
        else:
            session.rollback()
            raise ConflictException(claim_id=self.id,
                    status=locked_claim.status,
                    message='Invalid status for activation')

        return locked_claim

    def expire(self):
        pass

    def release(self):
        inspector = sqlalchemy.inspection.inspect(self)
        session = inspector.session

        query = session.query(Claim
                ).filter_by(id=self.id
                ).with_for_update()
        locked_claim = query.one()

        if locked_claim.status == 'active':
            locked_claim.status = 'released'
            locked_claim.status_history.append(
                    StatusHistory(status='released'))
            session.commit()
            # TODO add lock
        else:
            session.rollback()
            raise ConflictException(claim_id=self.id,
                    status=locked_claim.status,
                    message='Invalid status for release')

        return locked_claim

    def revoke(self):
        inspector = sqlalchemy.inspection.inspect(self)
        session = inspector.session

        query = session.query(Claim
                ).filter_by(id=self.id
                ).with_for_update()
        locked_claim = query.one()

        if locked_claim.status in ['active', 'waiting']:
            locked_claim.status = 'revoked'
            locked_claim.status_history.append(
                    StatusHistory(status='revoked'))
            session.commit()
            # TODO delete lock
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
