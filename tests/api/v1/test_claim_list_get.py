from ..base import APITest
import itertools
import time


URL = '/v1/claims/'


class ClaimListGetSuccessGeneralTest(APITest):
    def setUp(self):
        super(ClaimListGetSuccessGeneralTest, self).setUp()
        self.response = self.get(URL)

    def test_should_return_200(self):
        self.assertEqual(200, self.response.status_code)

    def test_initial_get_should_be_empty_list(self):
        self.assertEqual([], self.response.DATA)


class ClaimListGetFilterSuccessTest(APITest):
    def setUp(self):
        super(ClaimListGetFilterSuccessTest, self).setUp()

        self.resources = ['foo', 'bar']
        self.user_data = ['a', 'b', 'c']

        for resource, user_data in itertools.product(self.resources,
                self.user_data):
            self.post(URL, {
                'resource': resource,
                'user_data': user_data,
                'ttl': 10,
            })

    def test_filter_by_resource(self):
        response = self.get(URL, resource='foo')
        self.assertEqual(3, len(response.DATA))
        actual_user_data = sorted(c['user_data'] for c in response.DATA)
        self.assertEqual(self.user_data, actual_user_data)

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


class ClaimListGetFilterTTLTest(APITest):
    def setUp(self):
        super(ClaimListGetFilterTTLTest, self).setUp()

        self.post(URL, {
            'resource': 'foo',
            'ttl': 600,
        })
        self.post(URL, {
            'resource': 'foo',
            'ttl': 600,
            'user_data': 'ignored_by_test',
        })

        self.post(URL, {
            'resource': 'bar',
            'ttl': 10,
        })

    def test_should_ignore_waiting_claims(self):
        response = self.get(URL, minimum_ttl=0)
        self.assertEqual(2, len(response.DATA))
        for claim in response.DATA:
            self.assertEqual('active', claim['status'])

    def test_minimum_should_exclude_ttls_that_are_too_small(self):
        response = self.get(URL, minimum_ttl=11)
        self.assertEqual(1, len(response.DATA))
        self.assertEqual('foo', response.DATA[0]['resource'])

    def test_maximum_should_exclude_ttls_that_are_too_large(self):
        response = self.get(URL, maximum_ttl=10)
        self.assertEqual(1, len(response.DATA))
        self.assertEqual('bar', response.DATA[0]['resource'])


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
            'ttl': 0.010,
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

        full_response = self.get(URL)

        offset_response = self.get(URL, offset=1)
        self.assertEqual(1, len(offset_response.DATA))
        self.assertEqual('waiting', offset_response.DATA[0]['status'])

        self.assertNotEqual(full_response.DATA[0]['url'],
                offset_response.DATA[0]['url'])
