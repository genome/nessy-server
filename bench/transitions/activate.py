from .base import TransitionBase


class Activate(TransitionBase):
    STATES = ['waiting']

    def __init__(self, get_url, **kwargs):
        super(Activate, self).__init__(**kwargs)
        self.get_url = get_url

    def modify_resource(self, resource, state):
        get_response = self.get(self.get_url, session_id=resource,
                params={'resource': resource, 'status': 'active'})

        if self._should_patch(get_response):
            self._patch_status(resource, state)
        else:
            state.noop()

    def _should_patch(self, get_response):
        data = get_response.json()
        if not data or len(data) != 1:
            return True

        claim = data[0]
        if claim['ttl'] < 0:
            return True

    def _patch_status(self, resource, state):
        claim_url = state.get_claim_url(resource)
        response = self.patch(claim_url, {'status': 'active'},
                session_id=resource)

        if response.status_code == 200:
            state.set_resource_state(resource, 'active', claim_url=claim_url)

        elif response.status_code == 409:
            state.noop()

        elif response.status_code == 400:
            state.set_resource_state(resource, 'expired', claim_url=claim_url)

        else:
            raise RuntimeError('Unexpected code from patch (%s): %d.  %s'
                    % (self.__class__.__name__, response.status_code,
                        response.text))
