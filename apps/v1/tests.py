from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import unittest


class NoContentionTest(APITestCase):
    def setUp(self):
        APITestCase.setUp(self)
        self.request_data = {
            'timeout': 0.010,
#            'requester_data': {
#                'baz': 'buz',
#                'foo': 3,
#            },
        }

    def lock_request_url(self, resource_name):
        return reverse('lock-requests', args=(resource_name,))


    def test_post_request_without_contention_should_return_201(self):
        response = self.client.post(self.lock_request_url('resource-foo'),
                self.request_data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_request_without_contention_should_immediately_activate(self):
        response = self.client.post(self.lock_request_url('resource-foo'),
                self.request_data)
        self.assertEqual('active', response.data['current_status'])



if __name__ == '__main__':
    unittest.main()
