import abc


class FactoryBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def purge(self):
        pass  # pragma: no cover

    @abc.abstractmethod
    def create_actor(self):
        pass  # pragma: no cover
