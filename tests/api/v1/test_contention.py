from ..base import APITest


URL = '/v1/claims/'


class ContentionTest(APITest):
# TODO
#    def test_claim_expiration_should_activate_next_claim(self):
#        pass

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

# TODO
#    def test_claim_release_should_not_activate_other_claims(self):
#        pass
