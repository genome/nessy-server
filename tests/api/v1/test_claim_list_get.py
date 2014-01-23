from ..base import APITest
import itertools


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
    def setUp(self):
        super(ClaimListGetFilterSuccessTest, self).setUp()

        self.resources = ['foo', 'bar']
        self.timeouts = [1, 10, 100]

        for resource, timeout in itertools.product(self.resources,
                self.timeouts):
            self.post(URL, {
                'resource': resource,
                'timeout': timeout,
            })

    def test_filter_by_resource(self):
        response = self.get(URL, resource='foo')
        self.assertEqual(3, len(response.DATA))
        for expected_timeout, actual_timeout in itertools.izip(self.timeouts,
                sorted(c['timeout'] for c in response.DATA)):
            self.assertEqual(expected_timeout, actual_timeout)

    def test_filter_by_status(self):
        active_response = self.get(URL, status='active')
        self.assertEqual(2, len(active_response.DATA))

        waiting_response = self.get(URL, status='waiting')
        self.assertEqual(4, len(waiting_response.DATA))

# TODO
#    def test_filter_by_ttl(self):
#        pass

# TODO
#    def test_filter_by_active_duration(self):
#        pass

# TODO
#    def test_filter_by_waiting_duration(self):
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
