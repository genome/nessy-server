from sqlalchemy import Column
from sqlalchemy import DateTime, ForeignKey, Enum, Integer, Interval, Text
from sqlalchemy.orm import backref, relationship

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
    resource = Column(Text, index=True)
    timeout = Column(Interval, index=True)

    # XXX Use a native JSON column for postgres
    user_data = Column(Text)

    # XXX Is this column premature optimization?
    status = Column(Enum(*_VALID_STATUSES), index=True)
    lock = relationship('Lock', uselist=False, backref='claim')


class StatusHistory(Base):
    __tablename__ = 'status_history'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, index=True)
    status = Column(Enum(*_VALID_STATUSES), index=True)

    claim = relationship('Claim',
            backref=backref('status_history', order_by=timestamp))


class Lock(Base):
    __tablename__ = 'lock'

    id = Column(Integer, primary_key=True)

    resource = Column(Text, unique=True)
    claim_id = Column(Integer, ForeignKey('claim.id'), unique=True)

    activation_time = Column(DateTime, index=True)
    expiration_time = Column(DateTime, index=True)
    expiration_update_time = Column(DateTime, index=True)
