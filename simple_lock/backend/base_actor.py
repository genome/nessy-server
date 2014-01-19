import abc


class ActorBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def cleanup(self):
        pass
