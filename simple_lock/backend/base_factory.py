import abc


class FactoryBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def initialize(self):
        pass

    @abc.abstractmethod
    def destroy(self):
        pass

    @abc.abstractmethod
    def create_actor(self):
        pass
