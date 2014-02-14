import abc
import collections
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
        self._sessions = None

    @property
    def sessions(self):
        if self._sessions is None:
            self._sessions = collections.defaultdict(self._new_session)
        return self._sessions


    def _new_session(self):
        s = requests.Session()

        s.headers.update(self._headers)

        return s

    def attach_stats_monitor(self, stats):
        self.stats = stats


    def _http_execute(self, method_name, url, data, params, session_id):
        session =  self.sessions[session_id]
        method = getattr(session, method_name)
        begin = datetime.datetime.now()

        done = False
        while not done:
            try:
                response = method(url, data=simplejson.dumps(data),
                        params=params, headers=self._headers)
                done = True
            except Exception as e:
                print "Error at", self.__class__.__name__, method_name
                print e

        end = datetime.datetime.now()
        self.stats.add_request(self.__class__.__name__, method_name,
                response.status_code,
                (end - begin).total_seconds())

        return response

    def get(self, url, params, session_id):
        return self._http_execute('get', url, None, params, session_id)

    def post(self, url, data, session_id):
        return self._http_execute('post', url, data, None, session_id)

    def patch(self, url, data, session_id):
        return self._http_execute('patch', url, data, None, session_id)

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
