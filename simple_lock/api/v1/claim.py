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

        return 'claim created', 201

    def put(self, claim_id):
        pass

    def patch(self, claim_id):
        pass

    def _get_form(self, form_class):
        form = form_class(request.form)

        json_data = request.get_json()
        if json_data is not None:
            for k, v in json_data.iteritems():
                form[k].data = v

        if not form.validate():
            raise exceptions.InvalidParameters(**form.errors)

        return form
