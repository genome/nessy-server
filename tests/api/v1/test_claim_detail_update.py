from ..base import APITest
import abc


class ClaimUpdateMixinBase(object):
    __metaclass__ = abc.ABCMeta

    def setUp(self):
        super(ClaimUpdateMixinBase, self).setUp()
        self.post_data = {
            'resource': 'update-test-resource',
            'timeout': 0.010,
        }
        self.changed_data = {}

        self.post_response = self.client.post('/v1/claims/', self.post_data)
        self.resource_url = self.post_response.headers['Location']

    @abc.abstractproperty
    def method(self):
        pass

    @abc.abstractmethod
    def method_data(self):
        pass

    def update(self):
        method = getattr(self.client, self.method)
        return method(self.resource_url, self.method_data())


class ClaimUpdateSuccessMixin(ClaimUpdateMixinBase):
    pass

# TODO
#    def test_update_status_from_active_to_active_should_return_200(self):
#        pass


# TODO
#    def test_update_status_from_active_to_released_should_return_204(self):
#        pass
# TODO
#    def test_update_status_from_active_to_released_should_set_status(self):
#        pass

# TODO
#    def test_update_status_from_active_to_revoked_should_return_204(self):
#        pass

# TODO
#    def test_update_status_from_active_to_revoked_should_set_status(self):
#        pass


# TODO
#    def test_update_status_from_waiting_to_active_should_return_200(self):
#        pass

# TODO
#    def test_update_status_from_waiting_to_active_should_set_status(self):
#        pass

# TODO
#    def test_update_status_from_waiting_to_active_should_set_ttl(self):
#        pass

# TODO
#    def test_update_status_from_waiting_to_active_should_set_active_duration(self):
#        pass


# TODO
#    def test_update_status_from_waiting_to_revoked_should_return_204(self):
#        pass


# TODO
#    def test_update_ttl_while_status_acitve_should_return_200(self):
#        pass

# TODO
#    def test_update_ttl_while_status_acitve_should_set_ttl(self):
#        pass


class ClaimUpdateErrorMixin(ClaimUpdateMixinBase):
    pass

# TODO
#    def test_unknown_parameters_should_return_400(self):
#        pass

# TODO
#    def test_invalid_parameters_should_return_400(self):
#        pass

# TODO
#    def test_non_existant_claim_should_return_404(self):
#        pass

# TODO
#    def test_updating_expired_claim_should_return_409(self):
#        pass

# TODO
#    def test_updating_released_claim_should_return_409(self):
#        pass

# TODO
#    def test_updating_revoked_claim_should_return_409(self):
#        pass

# TODO
#    def test_updating_status_from_waiting_to_released_should_return_409(self):
#        pass

# TODO
#    def test_updating_ttl_when_status_not_active_should_return_409(self):
#        pass



class ClaimDetailPatchMixin(object):
    method = 'patch'

    def method_data(self):
        return self.changed_data

class ClaimDetailPutMixin(object):
    method = 'put'

    def method_data(self):
        put_data = dict(self.post_data)
        put_data.update(self.changed_data)
        return put_data


class ClaimDetailPatchSuccessTest(ClaimDetailPatchMixin,
        ClaimUpdateSuccessMixin, APITest):
    pass

class ClaimDetailPatchErrorTest(ClaimDetailPatchMixin,
        ClaimUpdateErrorMixin, APITest):
    pass


class ClaimDetailPutSuccessTest(ClaimDetailPutMixin,
        ClaimUpdateSuccessMixin, APITest):
    pass

class ClaimDetailPutErrorTest(ClaimDetailPutMixin,
        ClaimUpdateErrorMixin, APITest):
    pass
