from .base import TransitionBase


class Heartbeat(TransitionBase):
    STATES = ['active']

    def __init__(self, ttl, **kwargs):
        super(Heartbeat, self).__init__(**kwargs)
        self.ttl = ttl

    def modify_resource(self, resource, state):
        claim_url = state.get_claim_url(resource)
        response = self.patch(claim_url, {'ttl': self.ttl}, session_id=resource)

        if response.status_code == 200:
            state.noop()

        elif response.status_code == 400:
            state.set_resource_state(resource, 'expired', claim_url=None)

        else:
            raise RuntimeError('Unexpected code from patch: %d'
                    % response.status_code)
