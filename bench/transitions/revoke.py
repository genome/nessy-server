from .base import TransitionBase


class Revoke(TransitionBase):
    STATES = ['active', 'waiting']

    def modify_resource(self, resource, state):
        claim_url = state.get_claim_url(resource)
        response = self.patch(claim_url, {'status': 'revoked'},
                session_id=resource)

        if response.status_code == 204:
            state.set_resource_state(resource, 'revoked', claim_url=None)

        elif response.status_code == 400:
            state.set_resource_state(resource, 'expired', claim_url=None)

        else:
            raise RuntimeError('Unexpected code from patch (%s): %d.  %s'
                    % (self.__class__.__name__, response.status_code,
                        response.text))
