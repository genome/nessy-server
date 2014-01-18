from ..base import APITest


class V1RootTest(APITest):
    def test_unknown_resource_should_return_404(self):
        foo = self.client.get('/v1/unknown-resource/')
        self.assertEqual(404, foo.status_code)
