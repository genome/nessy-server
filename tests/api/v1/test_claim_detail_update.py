from ..base import APITest
import abc


URL = '/v1/claims/'


class ClaimUpdateMixinBase(object):
    __metaclass__ = abc.ABCMeta

    def setUp(self):
        super(ClaimUpdateMixinBase, self).setUp()
        self.post_data = {
            'resource': 'update-test-resource',
            'ttl': 0.010,
        }

        self.post_response = self.post(URL, self.post_data)
        self.resource_url = self.post_response.headers['Location']

    @abc.abstractproperty
    def method(self):
        pass

    @abc.abstractmethod
    def method_data(self, data):
        pass

    def update(self, url, data):
        method = getattr(self, self.method)
        return method(url, data=self.method_data(data))


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
# TODO
#    def test_unknown_parameters_should_return_400(self):
#        pass

    def test_invalid_parameters_should_return_400(self):
        expired_status_response = self.update(self.resource_url,
                {'status': 'expired'})
        self.assertEqual(400, expired_status_response.status_code)
        self.assertIn('status', expired_status_response.data)

        waiting_status_response = self.update(self.resource_url,
                {'status': 'waiting'})
        self.assertEqual(400, waiting_status_response.status_code)
        self.assertIn('status', waiting_status_response.data)

        timeout_response = self.update(self.resource_url,
                {'ttl': -1.7})
        self.assertEqual(400, timeout_response.status_code)
        self.assertIn('ttl', timeout_response.data)

# TODO
#    def test_non_existant_claim_should_return_404(self):
#        pass

# TODO
#    def test_updating_claim_with_negative_ttl_should_return_409(self):
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

    def method_data(self, data):
        return data

class ClaimDetailPutMixin(object):
    method = 'put'

    def method_data(self, data):
        put_data = {
            'ttl': 0.010,
            'status': 'waiting',
        }
        put_data.update(data)
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
