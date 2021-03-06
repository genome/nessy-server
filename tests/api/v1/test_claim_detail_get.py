from ..base import APITest
import datetime
import dateutil.parser
import time
import pytz


POST_URL = '/v1/claims/'


class ClaimDetailGetGeneralSuccessTest(APITest):
    def setUp(self):
        super(ClaimDetailGetGeneralSuccessTest, self).setUp()
        self.post_data = {
            'resource': 'post-resource',
            'ttl': 0.010,
        }
        self.post_response = self.post(POST_URL, self.post_data)
        self.url = self.post_response.headers['Location']
        self.response = self.get(self.url)

    def test_should_return_200(self):
        self.assertEqual(200, self.response.status_code)

    def test_should_return_creation_time(self):
        created = dateutil.parser.parse(self.response.DATA['created'])
        now = pytz.UTC.localize(datetime.datetime.utcnow())
        self.assertGreaterEqual(now, created)
        self.assertLessEqual(now - datetime.timedelta(seconds=2), created)

    def test_should_return_resource(self):
        self.assertEqual(self.post_data['resource'],
                self.response.DATA['resource'])

    def test_should_return_status(self):
        self.assertEqual('active', self.response.DATA['status'])

    def test_should_return_status_history(self):
        status_history = self.response.DATA['status_history']
        self.assertEqual(['waiting', 'active'],
                [sh['status'] for sh in status_history])

    def test_should_return_ttl(self):
        self.assertIsInstance(self.response.DATA['ttl'], float)
        self.assertGreaterEqual(self.post_data['ttl'],
                self.response.DATA['ttl'])

    def test_should_return_url(self):
        self.assertEqual(self.url, self.response.DATA['url'])


class ClaimDetailGetSuccessUserDataTest(APITest):
    def test_empty_user_provided_data_should_be_null(self):
        post_response = self.post(POST_URL, {
            'resource': 'post-resource',
            'ttl': 0.010,
        })
        get_response = self.get(post_response.headers['Location'])
        self.assertEqual(None, get_response.DATA['user_data'])

    def test_should_return_user_data(self):
        user_data = {
            'very': ['complex', 'stuff'],
        }
        post_response = self.post(POST_URL, {
            'resource': 'post-resource',
            'ttl': 0.010,
            'user_data': user_data,
        })
        get_response = self.get(post_response.headers['Location'])
        self.assertEqual(user_data, get_response.DATA['user_data'])


class ClaimDetailGetActiveSuccessTest(APITest):
    def setUp(self):
        super(ClaimDetailGetActiveSuccessTest, self).setUp()
        self.post_data = {
            'resource': 'post-resource',
            'ttl': 0.010,
        }
        self.post_response = self.post(POST_URL, self.post_data)
        self.url = self.post_response.headers['Location']
        self.response = self.get(self.url)

    def test_should_return_ttl(self):
        self.assertIsInstance(self.response.DATA['ttl'], float)
        self.assertGreaterEqual(self.post_data['ttl'],
                self.response.DATA['ttl'])

    def test_should_return_active_duration(self):
        self.assertIsInstance(self.response.DATA['active_duration'], float)
        time.sleep(0.010)
        updated_response = self.get(self.url)
        self.assertLess(0, updated_response.DATA['active_duration'])


class ClaimDetailGetWaitingSuccessTest(APITest):
    def setUp(self):
        super(ClaimDetailGetWaitingSuccessTest, self).setUp()
        self.post_data = {
            'resource': 'post-resource',
            'ttl': 0.010,
        }
        self.first_post_response = self.post(POST_URL, self.post_data)
        self.second_post_response = self.post(POST_URL, self.post_data)
        self.url = self.second_post_response.headers['Location']
        self.response = self.get(self.url)

    def test_should_return_waiting_duration(self):
        self.assertIsInstance(self.response.DATA['waiting_duration'], float)
        time.sleep(0.010)
        updated_response = self.get(self.url)
        self.assertLess(0, updated_response.DATA['waiting_duration'])


class ClaimDetailGetErrorTest(APITest):
    def test_non_existant_claim_should_return_404(self):
        response = self.get('/v1/claims/123456789/')
        self.assertEqual(404, response.status_code)
