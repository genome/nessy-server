from .base import TransitionBase


class Create(TransitionBase):
    def __init__(self, url, base_rate, ttl, **kwargs):
        super(Create, self).__init__(**kwargs)
        self.url = url
        self.base_rate = base_rate
        self.ttl = ttl

    def targets(self, state):
        return state.resources_in_states('released', 'expired', 'revoked')

    def modify_resource(self, resource, state):
        response = self.post(self.url, {'resource': resource, 'ttl': self.ttl})
        if response.status_code == 201:
            claim_url = response.headers['Location']
            state.set_resource_state(resource, 'active', claim_url=claim_url)

        elif response.status_code == 202:
            claim_url = response.headers['Location']
            state.set_resource_state(resource, 'waiting', claim_url=claim_url)

        else:
            raise RuntimeError('Unexpected code (%d) from post: %s'
                    % (response.status_code, response.text))
