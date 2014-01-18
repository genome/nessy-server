from .base import APITest


class RootTest(APITest):
    def test_unknown_resource_should_return_404(self):
        foo = self.client.get('/unknown-resource/')
        self.assertEqual(404, foo.status_code)

# TODO
#    def test_root_should_redirect_to_configured_url(self):
#        foo = self.client.get('/')
#        self.assertEqual(304, foo.status_code)
