from . import actor
from . import models
from ..base_factory import FactoryBase

import logging
import sqlalchemy
import time


__all__ = ['SqlActorFactory']


LOG = logging.getLogger(__file__)


class SqlActorFactory(FactoryBase):
    def __init__(self, connection_string, reconnect_sleep=30):
        self.connection_string = connection_string
        self.reconnect_sleep = reconnect_sleep
        self._engine = None
        self._Session = None

    def purge(self):
        s = self._get_session()
        s.query(models.Lock).delete()
        s.query(models.StatusHistory).delete()
        s.query(models.Claim).delete()
        s.commit()

    def create_actor(self):
        return actor.SqlActor(self._get_session())

    def _get_session(self):
        if self._Session is None:
            self._initialize_session()

        # NOTE:  autoflush must be off to avoid a deadlock inside
        # Resource.promote
        return self._Session(autoflush=False)

    def _initialize_session(self):
        while self._Session is None:
            try:
                self._engine = sqlalchemy.create_engine(self.connection_string)
                models.Base.metadata.create_all(self._engine)
                self._Session = sqlalchemy.orm.sessionmaker(bind=self._engine)
            except sqlalchemy.exc.OperationalError:
                LOG.critical(
                    'Failed to connect to SQL backend, retrying in %s seconds',
                    self.reconnect_sleep)
                time.sleep(self.reconnect_sleep)
