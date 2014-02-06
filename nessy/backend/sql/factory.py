from . import actor
from . import models
from ..base_factory import FactoryBase

import sqlalchemy


__all__ = ['SqlActorFactory']


class SqlActorFactory(FactoryBase):
    def __init__(self, connection_string):
        self._engine = sqlalchemy.create_engine(connection_string)
        self._Session = sqlalchemy.orm.sessionmaker(bind=self._engine)

    def initialize(self):
        models.Base.metadata.create_all(self._engine)

    def purge(self):
        s = self._Session()
        s.query(models.Lock).delete()
        s.query(models.StatusHistory).delete()
        s.query(models.Claim).delete()
        s.commit()

    def create_actor(self):
        return actor.SqlActor(self._Session())
