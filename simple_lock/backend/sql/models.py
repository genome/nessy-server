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
    resource = Column(Text, index=True)
    timeout = Column(Interval, index=True)
    created = Column(DateTime, index=True, default=datetime.datetime.utcnow)

    # XXX Use a native JSON column for postgres
    user_data = Column(Text)

    lock = relationship('Lock', uselist=False, backref='claim')

    @property
    def status(self):
        return self.status_history[-1].status

    @property
    def timeout_seconds(self):
        return self.timeout.total_seconds()

    @property
    def ttl(self):
        if self.lock:
            return self.lock.ttl

    @property
    def active_duration(self):
        if self.lock:
            return self.lock.active_duration


class StatusHistory(Base):
    __tablename__ = 'status_history'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    status = Column(Enum(*_VALID_STATUSES), index=True)
    claim_id = Column(Integer, ForeignKey('claim.id'))

    claim = relationship('Claim',
            backref=backref('status_history', order_by=timestamp))


class Lock(Base):
    __tablename__ = 'lock'

    id = Column(Integer, primary_key=True)

    resource = Column(Text, unique=True)
    claim_id = Column(Integer, ForeignKey('claim.id'), unique=True)

    activation_time = Column(DateTime, index=True,
            default=datetime.datetime.utcnow)
    expiration_time = Column(DateTime, index=True,
            default=datetime.datetime.utcnow)
    expiration_update_time = Column(DateTime, index=True,
            default=datetime.datetime.utcnow)

    @property
    def ttl(self):
        now = datetime.datetime.utcnow()
        return (self.expiration_time - now).total_seconds()

    @property
    def active_duration(self):
        now = datetime.datetime.utcnow()
        return (now - self.activation_time).total_seconds()
