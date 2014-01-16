from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import unittest


class ClaimTest(APITestCase):
    def setUp(self):
        APITestCase.setUp(self)
        self.claim_data = {
            'timeout': 0.010,
            'resource': 'resource-foo',
            'metadata': {
                'baz': 'buz',
                'foo': 3,
            },
        }


    def post(self):
        return self.client.post(reverse('claim-list'), self.claim_data,
                format='json')

    def test_post_claim_without_contention_should_return_201(self):
        response = self.post()
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_post_claim_without_contention_should_set_location_header(self):
        response = self.post()
        self.assertIsNotNone(response.get('Location'))

    def test_post_claim_should_set_metadata(self):
        response = self.post()
        self.assertEqual(self.claim_data['metadata'], response.data['metadata'])

    def test_claim_without_contention_should_immediately_activate(self):
        response = self.post()
        self.assertEqual('active', response.data['current_status'])

    def test_claim_with_contention_should_wait(self):
        response_1 = self.post()
        response_2 = self.post()
        self.assertEqual('waiting', response_2.data['current_status'])


if __name__ == '__main__':
    unittest.main()
