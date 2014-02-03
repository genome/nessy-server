import collections
import datetime



class State(object):
    UNSET = object()

    def __init__(self, resource_names):
        self._state_index = collections.defaultdict(set)
        self._state_index['released'].update(resource_names)

        self._resource_index = {r: 'released' for r in resource_names}
        self._claim_urls = {}
        self.transition_count = 0

        self._request_times = collections.defaultdict(list)

    def get_claim_url(self, resource):
        return self._claim_urls[resource]

    def resources_in_states(self, *states):
        blah = [self._state_index[s] for s in states]
        return set.union(*blah)

    def set_resource_state(self, resource, state, claim_url=UNSET):
        self.transition_count += 1
        old_state = self._resource_index.pop(resource)
        self._resource_index[resource] = state
        self._state_index[old_state].remove(resource)
        self._state_index[state].add(resource)

        if claim_url is not self.UNSET:
            if claim_url is None and resource in self._claim_urls:
                self._claim_urls.pop(resource)
            else:
                self._claim_urls[resource] = claim_url

    def noop(self):
        self.transition_count += 1

    def start_timer(self):
        self._begin_time = datetime.datetime.now()

    def stop_timer(self):
        self._end_time = datetime.datetime.now()

    @property
    def _total_runtime(self):
        return (self._end_time - self._begin_time).total_seconds()

    def report(self):
        tag_times = {
            tag: {
                'mean': sum(times) / len(times),
                'number': len(times),
                'rps': len(times) / sum(times),
            }
            for tag, times in self._request_times.iteritems()
        }

        return {
            'total_requests': self.transition_count,
            'total_runtime': self._total_runtime,
            'rps': self.transition_count / self._total_runtime,
            'times': tag_times,
        }

    def register_request(self, tag, seconds):
        self._request_times[tag].append(seconds)
