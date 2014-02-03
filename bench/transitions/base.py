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

    def __init__(self, base_rate, stats=None):
        self.base_rate = base_rate
        self.stats = stats

    def attach_stats_monitor(self, stats):
        self.stats = stats


    def _http_execute(self, method_name, url, data):
        method = getattr(requests, method_name)
        begin = datetime.datetime.now()
        response = method(url, data=simplejson.dumps(data),
                headers=self._headers)
        end = datetime.datetime.now()
        self.stats.add_request(self.__class__.__name__, method_name,
                response.status_code,
                (end - begin).total_seconds())

        return response


    def post(self, url, data):
        return self._http_execute('post', url, data)

    def patch(self, url, data):
        return self._http_execute('patch', url, data)

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
