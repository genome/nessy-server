import abc
import datetime
import simplejson
import requests


class TransitionBase(object):
    __metaclass__ = abc.ABCMeta

    _headers = {
        'Accepts': 'application/json',
        'Content-Type': 'application/json',
    }

    def __init__(self, base_rate):
        self.base_rate = base_rate

    def post(self, url, data, state):
        begin = datetime.datetime.now()
        response = requests.post(url, data=simplejson.dumps(data),
                headers=self._headers)
        end = datetime.datetime.now()

        state.register_request(self.__class__.__name__,
                (end - begin).total_seconds())

        return response

    def patch(self, url, data, state):
        begin = datetime.datetime.now()
        response = requests.patch(url, data=simplejson.dumps(data),
                headers=self._headers)
        end = datetime.datetime.now()

        state.register_request(self.__class__.__name__,
                (end - begin).total_seconds())

        return response

    def targets(self, state):
        return state.resources_in_states(*self.STATES)

    def rate(self, state):
        return self.base_rate * len(self.targets(state))

    def execute(self, state, r):
        targets = list(self.targets(state))

        i = int(r / self.base_rate)
        target_resource = targets[i]

        self.modify_resource(target_resource, state)

    @abc.abstractproperty
    def STATES(self):
        pass

    @abc.abstractmethod
    def modify_resource(self, resource, state):
        pass
