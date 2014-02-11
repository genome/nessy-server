from ..base import APITest
import time


URL = '/v1/claims/'


class ClaimPatchBase(APITest):
    def setUp(self):
        super(ClaimPatchBase, self).setUp()
        self.post_data = {
            'resource': 'update-test-resource',
            'ttl': 20,
        }

        self.post_response = self.post(URL, self.post_data)
        self.resource_url = self.post_response.headers['Location']


class ClaimPatchSuccess(ClaimPatchBase):
    def test_update_status_from_active_to_active_should_return_200(self):
        update_response = self.patch(self.resource_url, {'status': 'active'})
        self.assertEqual(200, update_response.status_code)

    def test_update_status_from_active_to_released_should_return_204(self):
        update_response = self.patch(self.resource_url, {'status': 'released'})
        self.assertEqual(204, update_response.status_code)

    def test_update_status_from_active_to_released_should_set_status(self):
        update_response = self.patch(self.resource_url, {'status': 'released'})
        get_response = self.get(self.resource_url)
        self.assertEqual('released', get_response.DATA['status'])

    def test_update_status_to_released_should_finalize_active_duration(self):
        update_response = self.patch(self.resource_url, {'status': 'released'})
        first_get_response = self.get(self.resource_url)
        time.sleep(0.010)
        second_get_response = self.get(self.resource_url)
        self.assertEqual(first_get_response.DATA['active_duration'],
                second_get_response.DATA['active_duration'])

    def test_update_status_from_active_to_revoked_should_return_204(self):
        update_response = self.patch(self.resource_url, {'status': 'revoked'})
        self.assertEqual(204, update_response.status_code)

    def test_update_status_from_active_to_revoked_should_set_status(self):
        update_response = self.patch(self.resource_url, {'status': 'revoked'})
        get_response = self.get(self.resource_url)
        self.assertEqual('revoked', get_response.DATA['status'])

    def test_update_status_from_active_to_revoked_should_finalize_active_duration(self):
        update_response = self.patch(self.resource_url, {'status': 'revoked'})
        first_get_response = self.get(self.resource_url)
        time.sleep(0.010)
        second_get_response = self.get(self.resource_url)
        self.assertEqual(first_get_response.DATA['active_duration'],
                second_get_response.DATA['active_duration'])

    def test_update_status_from_waiting_to_revoked_should_finalize_waiting_duration(self):
        second_post_response = self.post(URL, self.post_data)
        url = second_post_response.headers['Location']
        update_response = self.patch(url, {'status': 'revoked'})
        first_get_response = self.get(url)
        time.sleep(0.010)
        second_get_response = self.get(url)
        self.assertEqual(first_get_response.DATA['waiting_duration'],
                second_get_response.DATA['waiting_duration'])

    def test_update_status_from_waiting_to_active_should_return_200(self):
        second_post_response = self.post(URL, self.post_data)
        self.patch(self.resource_url, {'status': 'released'})
        update_response = self.patch(second_post_response.headers['Location'],
                {'status': 'active'})
        self.assertEqual(200, update_response.status_code)

    def test_update_status_from_waiting_to_active_should_set_status(self):
        second_post_response = self.post(URL, self.post_data)
        self.patch(self.resource_url, {'status': 'released'})
        update_response = self.patch(second_post_response.headers['Location'],
                {'status': 'active'})
        self.assertEqual('active', update_response.DATA['status'])

    def test_update_status_from_waiting_to_active_should_set_ttl(self):
        second_post_response = self.post(URL, self.post_data)
        self.patch(self.resource_url, {'status': 'released'})
        update_response = self.patch(second_post_response.headers['Location'],
                {'status': 'active'})
        self.assertIsInstance(update_response.DATA['ttl'], float)
        self.assertLessEqual(self.post_data['ttl']/2,
                update_response.DATA['ttl'])
        self.assertGreaterEqual(self.post_data['ttl'],
                update_response.DATA['ttl'])

    def test_update_status_from_waiting_to_active_should_set_active_duration(self):
        second_post_response = self.post(URL, self.post_data)
        self.patch(self.resource_url, {'status': 'released'})
        update_response = self.patch(second_post_response.headers['Location'],
                {'status': 'active'})
        self.assertIsInstance(update_response.DATA['active_duration'], float)
        self.assertLess(0, update_response.DATA['active_duration'])

    def test_update_status_from_waiting_to_revoked_should_return_204(self):
        second_post_response = self.post(URL, self.post_data)
        response = self.patch(second_post_response.headers['Location'],
                {'status': 'revoked'})
        self.assertEqual(204, response.status_code)

    def test_update_ttl_while_status_acitve_should_return_200(self):
        update_response = self.patch(self.resource_url, {'ttl': 600})
        self.assertEqual(200, update_response.status_code)

    def test_update_ttl_while_status_acitve_should_set_ttl(self):
        update_response = self.patch(self.resource_url, {'ttl': 600})
        self.assertLessEqual(550, update_response.DATA['ttl'])


class ClaimPatchError(ClaimPatchBase):
# TODO
#    def test_unknown_parameters_should_return_400(self):
#        pass

    def test_invalid_parameters_should_return_400(self):
        expired_status_response = self.patch(self.resource_url,
                {'status': 'expired'})
        self.assertEqual(400, expired_status_response.status_code)
        self.assertIn('status', expired_status_response.data)

        waiting_status_response = self.patch(self.resource_url,
                {'status': 'waiting'})
        self.assertEqual(400, waiting_status_response.status_code)
        self.assertIn('status', waiting_status_response.data)

        timeout_response = self.patch(self.resource_url,
                {'ttl': -1.7})
        self.assertEqual(400, timeout_response.status_code)
        self.assertIn('ttl', timeout_response.data)

    def test_update_with_no_parameters_should_return_400(self):
        invalid_response = self.patch(self.resource_url, {})
        self.assertEqual(400, invalid_response.status_code)

    def test_non_existent_claim_should_return_404(self):
        invalid_response = self.patch('/v1/claims/123456789/',
                 {'status': 'active'})
        self.assertEqual(404, invalid_response.status_code)

    def test_updating_claim_with_negative_ttl_should_return_400(self):
        invalid_response = self.patch(self.resource_url, {'ttl': -7})
        self.assertEqual(400, invalid_response.status_code)

    def test_updating_expired_claim_ttl_should_return_400(self):
        self.patch(self.resource_url, {'ttl': 0.005})
        time.sleep(0.005)
        expired_response = self.patch(self.resource_url, {'ttl': 600})
        self.assertEqual(400, expired_response.status_code)

    def test_updating_expired_claim_status_should_return_400(self):
        self.patch(self.resource_url, {'ttl': 0.005})
        time.sleep(0.005)
        r = self.post(URL, self.post_data)  # New claim should get the resource
        self.assertEqual(201, r.status_code)
        expired_response = self.patch(self.resource_url, {'status': 'revoked'})
        self.assertEqual(400, expired_response.status_code)

    def test_updating_released_claim_should_return_400(self):
        self.patch(self.resource_url, {'status': 'released'})
        statuses = ['active', 'released', 'revoked']
        for status in statuses:
            response = self.patch(self.resource_url, {'status': status})
            self.assertEqual(400, response.status_code)

    def test_updating_revoked_claim_should_return_400(self):
        self.patch(self.resource_url, {'status': 'revoked'})
        statuses = ['active', 'released', 'revoked']
        for status in statuses:
            response = self.patch(self.resource_url, {'status': status})
            self.assertEqual(400, response.status_code)

    def test_updating_status_from_waiting_to_released_should_return_400(self):
        second_post_response = self.post(URL, self.post_data)
        response = self.patch(second_post_response.headers['Location'],
                {'status': 'released'})
        self.assertEqual(400, response.status_code)

    def test_updating_ttl_when_status_not_active_should_return_400(self):
        second_post_response = self.post(URL, self.post_data)
        response = self.patch(second_post_response.headers['Location'],
                {'ttl': 600})
        self.assertEqual(400, response.status_code)

    def test_updating_status_to_active_with_contention_should_return_409(self):
        second_post_response = self.post(URL, self.post_data)
        response = self.patch(second_post_response.headers['Location'],
                {'status': 'active'})
        self.assertEqual(409, response.status_code)

    def test_updating_released_to_active_while_empty_should_return_400(self):
        self.patch(self.resource_url, {'status': 'released'})
        response = self.patch(self.resource_url, {'status': 'active'})
        self.assertEqual(400, response.status_code)

    def test_updating_released_to_active_while_full_should_return_400(self):
        second_post_response = self.post(URL, self.post_data)
        self.patch(self.resource_url, {'status': 'released'})
        response = self.patch(self.resource_url, {'status': 'active'})
        self.assertEqual(400, response.status_code)

    def test_updating_multiple_fields_should_return_400(self):
        response = self.patch(self.resource_url,
                {'status': 'active', 'ttl': 60})
        self.assertEqual(400, response.status_code)
