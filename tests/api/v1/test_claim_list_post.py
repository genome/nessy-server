from ..base import APITest

URL = '/v1/claims/'


class ClaimListPostGeneralSuccessTest(APITest):
    def setUp(self):
        super(ClaimListPostGeneralSuccessTest, self).setUp()
        self.post_data = {
            'resource': 'post-resource',
            'ttl': 0.010,
            'user_data': {
                'foo': 'bar',
                'baz': 42,
            },
        }
        self.response = self.post(URL, self.post_data)

    def test_should_set_valid_location_header(self):
        url = self.response.headers['Location']
        response = self.get(url)
        self.assertEqual(200, response.status_code)

    def test_should_set_automatic_fields(self):
        self.assertIsNotNone(self.response.DATA['created'])
        self.assertIsNotNone(self.response.DATA['status'])

    def test_should_set_user_provided_data(self):
        self.assertEqual(self.post_data['user_data'],
                self.response.DATA['user_data'])


class ClaimListPostSuccessWithoutContentionTest(APITest):
    def setUp(self):
        super(ClaimListPostSuccessWithoutContentionTest, self).setUp()
        self.post_data = {
            'resource': 'post-resource',
            'ttl': 1,
        }
        self.response = self.post(URL, self.post_data)

    def test_should_return_201(self):
        self.assertEqual(201, self.response.status_code)

    def test_should_set_status_to_active(self):
        self.assertEqual('active', self.response.DATA['status'])

    def test_should_set_ttl_to_timeout(self):
        self.assertIsNotNone(self.response.DATA['ttl'])
        self.assertLessEqual(self.response.DATA['ttl'],
                self.post_data['ttl'])
        self.assertGreaterEqual(self.response.DATA['ttl'], 0)


class ClaimListPostSuccessWithContentionTest(APITest):
    def setUp(self):
        super(ClaimListPostSuccessWithContentionTest, self).setUp()
        self.post_data = {
            'resource': 'post-resource',
            'ttl': 0.010,
        }
        self.first_response = self.post(URL, self.post_data)
        self.second_response = self.post(URL, self.post_data)

    def test_should_return_202(self):
        self.assertEqual(202, self.second_response.status_code)

    def test_should_set_status_to_waiting(self):
        self.assertEqual('waiting', self.second_response.DATA['status'])


class ClaimListPostErrorTest(APITest):
    def test_missing_mandatory_parameters_should_return_400(self):
        no_params_response = self.post(URL, data={})
        self.assertEqual(400, no_params_response.status_code)
        self.assertIn('resource', no_params_response.DATA)
        self.assertIn('ttl', no_params_response.DATA)

        no_resource_response = self.post(URL, {'ttl': 1.2})
        self.assertEqual(400, no_resource_response.status_code)
        self.assertIn('resource', no_resource_response.DATA)

        no_timeout_response = self.post(URL, {'resource': 'foo'})
        self.assertEqual(400, no_timeout_response.status_code)
        self.assertIn('ttl', no_timeout_response.DATA)

    def test_invalid_parameter_values_should_return_400(self):
        empty_resource_response = self.post(URL, {
            'resource': '',
            'ttl': 1.2,
        })
        self.assertEqual(400, empty_resource_response.status_code)
        self.assertIn('resource', empty_resource_response.DATA)

        negative_timeout_response = self.post(URL, {
            'resource': 'foo',
            'ttl': -1.2,
        })
        self.assertEqual(400, negative_timeout_response.status_code)
        self.assertIn('ttl', negative_timeout_response.DATA)

# TODO
#    def test_unknown_parameters_should_return_400(self):
#        unknown_param_response = self.post(URL, data={
#            'resource': 'foo',
#            'ttl': 1.2,
#            'unknown_param': 'enigma',
#        })
#        self.assertEqual(400, unknown_param_response.status_code)
#        self.assertIn('unknown_param', unknown_param_response.data)
