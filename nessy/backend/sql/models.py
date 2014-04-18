from ..exceptions import ConflictException, InvalidRequest
from sqlalchemy import Column, UniqueConstraint
from sqlalchemy import DateTime, ForeignKey, Enum, Integer, Interval, Text
from sqlalchemy import func, select
from sqlalchemy.orm import backref, column_property, relationship
import datetime
import sqlalchemy.ext.declarative
import sqlalchemy.orm.exc


__all__ = ['Base', 'Claim', 'Resource', 'StatusHistory', 'Lock']


_CONSISTENCY_EXCEPTIONS = (
    sqlalchemy.exc.IntegrityError,
    sqlalchemy.orm.exc.StaleDataError
)


Base = sqlalchemy.ext.declarative.declarative_base()


class Resource(object):
    def __init__(self, resource, session=None):
        self.resource = resource
        self.session = session

    def promote(self):
        self.expire_owning_claim()
        try:
            claim = self.session.query(Claim
                    ).filter_by(resource=self.resource, status='waiting',
                    ).order_by(Claim.created).first()
            if claim is not None:
                lock = Lock(claim=claim, resource=self.resource,
                        expiration_time=claim.now + claim.initial_ttl)
                claim.set_status('active')
                self.session.add(lock)
                self.session.commit()

        except _CONSISTENCY_EXCEPTIONS:
            self.session.rollback()

    def expire_owning_claim(self):
        try:
            lock = self.session.query(Lock
                    ).filter_by(resource=self.resource
                    ).filter(Lock.expiration_time < func.now()
                    ).first()

            if lock:
                claim = lock.claim
                claim.set_status('expired')
                self.session.delete(lock)
                self.session.commit()

        except _CONSISTENCY_EXCEPTIONS:
            self.session.rollback()

    @property
    def owner_id(self):
        lock = self.session.query(Lock
                ).filter_by(resource=self.resource).first()
        if lock:
            return lock.claim_id



class Claim(Base):
    __tablename__ = 'claim'

    STATUS_ENUM_NAME = 'claim_status_enum'

    CANCELLED_STATUSES = [
        'aborted',
        'revoked',
        'withdrawn',
    ]

    FINAL_STATUSES = [
        'expired',
        'released',
    ] + CANCELLED_STATUSES

    VALID_STATUSES = [
        'active',
        'waiting',
    ] + FINAL_STATUSES

    id = Column(Integer, primary_key=True)
    resource = Column(Text, index=True, nullable=False)
    initial_ttl = Column(Interval, index=True, nullable=False)
    status = Column(Enum(*VALID_STATUSES, name=STATUS_ENUM_NAME), index=True,
            nullable=False)

    created = Column(DateTime(timezone=True), index=True, default=func.now(),
            nullable=False)
    activated = Column(DateTime(timezone=True), index=True)
    deactivated = Column(DateTime(timezone=True), index=True)

    # XXX Use a native JSON column for postgres
    user_data = Column(Text)

    lock = relationship('Lock', uselist=False, backref='claim')

    now = column_property(select([func.now()]))

    def set_status(self, new_status):
        self.status = new_status
        self.status_history.append(StatusHistory(status=new_status))
        if new_status == 'active':
            self.activated = self.now
        elif new_status in self.FINAL_STATUSES:
            self.deactivated = self.now

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


class StatusHistory(Base):
    __tablename__ = 'status_history'
    __table_args__ = (
            UniqueConstraint('claim_id', 'status'),
            )

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), default=func.now(),
            nullable=False)
    status = Column(Enum(*Claim.VALID_STATUSES, name=Claim.STATUS_ENUM_NAME),
            index=True, nullable=False)
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
