from ..base import APITest
import itertools
import time


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

    def test_filter_by_active_duration(self):
        min_response = self.get(URL, minimum_active_duration=0)
        self.assertEqual(2, len(min_response.DATA))
        max_response = self.get(URL, maximum_active_duration=-1)
        self.assertEqual(0, len(max_response.DATA))

        empty_response = self.get(URL, minimum_active_duration=0.002,
                maximum_active_duration=0.001)
        self.assertEqual(0, len(empty_response.DATA))

        min_response_no_matches = self.get(URL, minimum_active_duration=1000)
        self.assertEqual(0, len(min_response_no_matches.DATA))

    def test_filter_by_waiting_duration(self):
        everyone_min = self.get(URL, minimum_waiting_duration=0)
        self.assertEqual(6, len(everyone_min.DATA))
        everyone_max = self.get(URL, maximum_waiting_duration=1)
        self.assertEqual(6, len(everyone_max.DATA))

        time.sleep(0.010)
        min_response = self.get(URL, minimum_waiting_duration=0.010)
        self.assertEqual(4, len(min_response.DATA))
        max_response = self.get(URL, maximum_waiting_duration=0.010)
        self.assertEqual(2, len(max_response.DATA))


# TODO
#    def test_filter_by_ttl(self):
#        pass


class ClaimListGetFilterErrorTest(APITest):
    pass

# TODO
#    def test_invalid_filter_parameter_should_return_400(self):
#        pass


class ClaimListGetPaginationTest(APITest):
    def setUp(self):
        super(ClaimListGetPaginationTest, self).setUp()
        self.post_data = {
            'resource': 'post-resource',
            'timeout': 0.010,
        }

    def _post_claims(self, number):
        for i in xrange(number):
            self.post(URL, self.post_data)

    def test_should_respect_limit_parameter(self):
        self._post_claims(5)
        response = self.get(URL, limit=2)
        self.assertEqual(2, len(response.DATA))

    def test_should_respect_offset_parameter(self):
        self._post_claims(2)
        response = self.get(URL, offset=1)
        self.assertEqual(1, len(response.DATA))
        self.assertEqual('waiting', response.DATA[0]['status'])
