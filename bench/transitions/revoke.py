from .base import TransitionBase


class Revoke(TransitionBase):
    STATES = ['active', 'waiting']

    def __init__(self, base_rate, **kwargs):
        super(Revoke, self).__init__(**kwargs)
        self.base_rate = base_rate

    def modify_resource(self, resource, state):
        claim_url = state.get_claim_url(resource)
        response = self.patch(claim_url, {'status': 'revoked'})

        if response.status_code == 204:
            state.set_resource_state(resource, 'revoked', claim_url=None)

        elif response.status_code == 409:
            state.set_resource_state(resource, 'expired', claim_url=None)

        else:
            raise RuntimeError('Unexpected code from patch: %d'
                    % response.status_code)
