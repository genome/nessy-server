from sqlalchemy import Column
from sqlalchemy import DateTime, ForeignKey, Enum, Integer, Interval, Text
from sqlalchemy.orm import backref, relationship

import sqlalchemy.ext.declarative
import datetime


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
    timeout = Column(Interval, index=True, nullable=False)
    status = Column(Enum(*_VALID_STATUSES), index=True, nullable=False)

    created = Column(DateTime, index=True, default=datetime.datetime.utcnow,
            nullable=False)
    activated = Column(DateTime, index=True)
    deactivated = Column(DateTime, index=True)

    # XXX Use a native JSON column for postgres
    user_data = Column(Text)

    lock = relationship('Lock', uselist=False, backref='claim')

    @property
    def timeout_seconds(self):
        return self.timeout.total_seconds()

    @property
    def ttl(self):
        if self.lock:
            return self.lock.ttl

    @property
    def active_duration(self):
        if self.activated is not None:
            if self.deactivated is not None:
                return (self.deactivated - self.activated).total_seconds()
            else:
                now = datetime.datetime.utcnow()
                return (now - self.activated).total_seconds()

    @property
    def waiting_duration(self):
        if self.activated is not None:
            return (self.activated - self.created).total_seconds()
        elif self.deactivated is not None:
            return (self.deactivated - self.created).total_seconds()
        else:
            now = datetime.datetime.utcnow()
            return (now - self.created).total_seconds()


class StatusHistory(Base):
    __tablename__ = 'status_history'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, index=True, default=datetime.datetime.utcnow,
            nullable=False)
    status = Column(Enum(*_VALID_STATUSES), index=True, nullable=False)
    claim_id = Column(Integer, ForeignKey('claim.id'), nullable=False)

    claim = relationship('Claim',
            backref=backref('status_history', order_by=timestamp))


class Lock(Base):
    __tablename__ = 'lock'

    id = Column(Integer, primary_key=True)

    resource = Column(Text, unique=True, nullable=False)
    claim_id = Column(Integer, ForeignKey('claim.id'), unique=True,
            nullable=False)

    expiration_time = Column(DateTime, index=True,
            default=datetime.datetime.utcnow, nullable=False)
    expiration_update_time = Column(DateTime, index=True,
            default=datetime.datetime.utcnow, nullable=False)

    @property
    def ttl(self):
        now = datetime.datetime.utcnow()
        return (self.expiration_time - now).total_seconds()
