from ..base import APITest
import time


URL = '/v1/claims/'


class ContentionTest(APITest):
    def test_claim_expiration_should_activate_next_claim(self):
        resource = 'everyone-wants-it'

        first_post_response = self.post(URL, {'resource': resource,
            'ttl': 0.010})
        second_post_response = self.post(URL, {'resource': resource, 'ttl': 60})

        time.sleep(0.010)
        activate_response = self.patch(second_post_response.headers['Location'],
                {'status': 'active'})

        self.assertEqual(200, activate_response.status_code)

# TODO
#    def test_claim_expiration_should_not_activate_other_claims(self):
#        pass

    def test_claim_release_should_activate_next_claim(self):
        post_data = {
            'resource': 'everyone-wants-it',
            'ttl': 600,
        }

        first_post_response = self.post(URL, post_data)
        second_post_response = self.post(URL, post_data)

        self.patch(first_post_response.headers['Location'],
                {'status': 'released'})
        activate_response = self.patch(second_post_response.headers['Location'],
                {'status': 'active'})

        self.assertEqual(200, activate_response.status_code)

    def test_claim_release_should_not_activate_other_claims(self):
        post_data = {
            'resource': 'everyone-wants-it',
            'ttl': 600,
        }

        first_post_response = self.post(URL, post_data)
        second_post_response = self.post(URL, post_data)
        third_post_response = self.post(URL, post_data)

        self.patch(first_post_response.headers['Location'],
                {'status': 'released'})
        activate_response = self.patch(third_post_response.headers['Location'],
                {'status': 'active'})

        self.assertEqual(409, activate_response.status_code)
