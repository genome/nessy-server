from ..base import APITest


class ClaimListPostGeneralSuccessTest(APITest):
    pass

# TODO
#    def test_should_set_location_header(self):
#        pass

# TODO
#    def test_should_set_user_provided_data(self):
#        pass

# TODO
#    def test_should_set_automatic_fields(self):
#        pass


class ClaimListPostSuccessWithoutContentionTest(APITest):
    def setUp(self):
        super(ClaimListPostSuccessWithoutContentionTest, self).setUp()
        self.post_data = {
            'resource': 'post-resource',
            'timeout': 0.010,
        }
        self.response = self.client.post('/v1/claims/', self.post_data)

    def test_should_return_201(self):
        self.assertEqual(201, self.response.status_code)

# TODO
#    def test_should_set_status_to_active(self):
#        pass

# TODO
#    def test_should_set_ttl_to_timeout(self):
#        pass


class ClaimListPostSuccessWithContentionTest(APITest):
    pass

# TODO
#    def test_should_return_202(self):
#        pass

# TODO
#    def test_should_set_status_to_waiting(self):
#        pass

class ClaimListPostErrorTest(APITest):
    pass

# TODO
#    def test_missing_mandatory_parameters_should_return_400(self):
#        pass

# TODO
#    def test_invalid_parameter_values_should_return_400(self):
#        pass

# TODO
#    def test_unknown_parameters_should_return_400(self):
#        pass
