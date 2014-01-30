import collections



class State(object):
    UNSET = object()

    def __init__(self, resource_names):
        self._state_index = collections.defaultdict(set)
        self._state_index['released'].update(resource_names)

        self._resource_index = {r: 'released' for r in resource_names}
        self._claim_urls = {}
        self.transition_count = 0

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

        if claim_url is None and resource in self._claim_urls:
            self._claim_urls.pop(resource)
        else:
            self._claim_urls[resource] = claim_url

    def noop(self):
        self.transition_count += 1
