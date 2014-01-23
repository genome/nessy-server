from ..base import APITest


URL = '/v1/claims/'


class ClaimListGetSuccessGeneralTest(APITest):
    def setUp(self):
        super(ClaimListGetSuccessGeneralTest, self).setUp()
        self.post_data = {
            'resource': 'post-resource',
            'timeout': 0.010,
        }
        self.response = self.get(URL)

    def test_should_return_200(self):
        self.assertEqual(200, self.response.status_code)

    def test_initial_get_should_be_empty_list(self):
        self.assertEqual([], self.response.DATA)


class ClaimListGetFilterSuccessTest(APITest):
    pass

# TODO
#    def test_filter_by_resource(self):
#        pass

# TODO
#    def test_filter_by_ttl(self):
#        pass

# TODO
#    def test_filter_by_active_duration(self):
#        pass

# TODO
#    def test_filter_by_waiting_duration(self):
#        pass

# TODO
#    def test_filter_by_status(self):
#        pass


class ClaimListGetFilterErrorTest(APITest):
    pass

# TODO
#    def test_invalid_filter_parameter_should_return_400(self):
#        pass


class ClaimListGetPaginationTest(APITest):
    pass

# TODO
#    def test_should_respect_limit_parameter(self):
#        pass

# TODO
#    def test_should_respect_offset_parameter(self):
#        pass
