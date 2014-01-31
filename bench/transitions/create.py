from .base import TransitionBase


class Create(TransitionBase):
    STATES = ['released', 'expired', 'revoked']

    def __init__(self, url, ttl, **kwargs):
        super(Create, self).__init__(**kwargs)
        self.url = url
        self.ttl = ttl

    def modify_resource(self, resource, state):
        response = self.post(self.url, {'resource': resource, 'ttl': self.ttl},
                state=state)
        if response.status_code == 201:
            claim_url = response.headers['Location']
            state.set_resource_state(resource, 'active', claim_url=claim_url)

        elif response.status_code == 202:
            claim_url = response.headers['Location']
            state.set_resource_state(resource, 'waiting', claim_url=claim_url)

        else:
            raise RuntimeError('Unexpected code (%d) from post: %s'
                    % (response.status_code, response.text))
