import abc
import simplejson
import requests


class TransitionBase(object):
    __metaclass__ = abc.ABCMeta

    _headers = {
        'Accepts': 'application/json',
        'Content-Type': 'application/json',
    }

    def post(self, url, data):
        return requests.post(url, data=simplejson.dumps(data),
                headers=self._headers)

    def patch(self, url, data):
        return requests.patch(url, data=simplejson.dumps(data),
                headers=self._headers)

    @abc.abstractmethod
    def targets(self, state):
        pass

    def rate(self, state):
        return self.base_rate * len(self.targets(state))

    def execute(self, state, r):
        targets = list(self.targets(state))

        i = int(r / self.base_rate)
        target_resource = targets[i]

        self.modify_resource(target_resource, state)

    @abc.abstractmethod
    def modify_resource(self, resource, state):
        pass
