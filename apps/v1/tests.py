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

    def patch(self, url, **kwargs):
        return self.client.patch(url, kwargs, format='json')

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

    def test_get_active_lock_should_return_ttl(self):
        post_response = self.post()
        get_response = self.client.get(post_response['Location'])
        self.assertGreater(post_response.data['ttl'], 0)

    def test_inital_ttl_should_be_close_to_timeout(self):
        post_response = self.post()
        get_response = self.client.get(post_response['Location'])
        self.assertGreater(post_response.data['ttl'],
                self.claim_data['timeout'] - 0.002)

    def test_patch_status_from_active_to_released_should_return_200(self):
        create_response = self.post()
        release_response = self.patch(create_response['Location'],
                current_status='released')
        self.assertEqual(status.HTTP_200_OK, release_response.status_code)

    def test_patch_status_from_active_to_released_should_release_lock(self):
        create_response_1 = self.post()
        release_response = self.patch(create_response_1['Location'],
                current_status='released')
        create_response_2 = self.post()
        self.assertEqual('active', create_response_2.data['current_status'])

    def test_claim_with_contention_should_wait(self):
        response_1 = self.post()
        response_2 = self.post()
        self.assertEqual('waiting', response_2.data['current_status'])

    def test_activate_waiting_lock_after_release_should_return_200(self):
        create_response_1 = self.post()
        create_response_2 = self.post()
        release_response_1 = self.patch(create_response_1['Location'],
                current_status='released')

        activate_response_2 = self.patch(create_response_1['Location'],
                current_status='active')
        self.assertEqual(status.HTTP_200_OK, activate_response_2.status_code)

    def test_activate_waiting_lock_after_release_should_become_active(self):
        create_response_1 = self.post()
        create_response_2 = self.post()
        release_response_1 = self.patch(create_response_1['Location'],
                current_status='released')

        activate_response_2 = self.patch(create_response_1['Location'],
                current_status='active')
        self.assertEqual('active', activate_response_2.data['current_status'])


if __name__ == '__main__':
    unittest.main()
