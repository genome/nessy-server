import flask.views


class ClaimView(flask.views.MethodView):
    def get(self, claim_id):
        if claim_id is None:
            return self._get_list()
        else:
            return self._get_detail(claim_id)

    def _get_list(self):
        pass

    def _get_detail(self, claim_id):
        pass

    def post(self):
        pass

    def put(self, claim_id):
        pass

    def patch(self, claim_id):
        pass
