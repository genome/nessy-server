from .base import TransitionBase


class Activate(TransitionBase):
    STATES = ['waiting']

    def modify_resource(self, resource, state):
        claim_url = state.get_claim_url(resource)
        response = self.patch(claim_url, {'status': 'active'}, state=state)

        if response.status_code == 200:
            state.set_resource_state(resource, 'active', claim_url=claim_url)

        elif response.status_code == 409:
            state.noop()

        else:
            raise RuntimeError('Unexpected code from patch: %d'
                    % response.status_code)
