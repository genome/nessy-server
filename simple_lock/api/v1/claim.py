from . import exceptions
from . import forms
from flask import g, request
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
        form = self._get_form(forms.ClaimCreateForm)

        r = flask.make_response('claim created', 201)
        r.headers['Location'] = '/v1/claims/42/'
        return r

    def put(self, claim_id):
        return self._update(claim_id)

    def patch(self, claim_id):
        return self._update(claim_id)

    def _update(self, claim_id):
        form = self._get_form(forms.ClaimUpdateForm)

        return 'claim updated', 204

    def _get_form(self, form_class):
        form = form_class(request.form, data=request.get_json())

        if not form.validate():
            raise exceptions.InvalidParameters(**form.errors)

        return form
