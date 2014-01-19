import wtforms

class _CommonFieldsMixin(object):
    timeout = wtforms.FloatField('Lock timeout (seconds)', [
        wtforms.validators.Required(),
        wtforms.validators.NumberRange(min=0),
    ])


class ClaimCreateForm(_CommonFieldsMixin, wtforms.Form):
    resource = wtforms.TextField('Resource name', [
        wtforms.validators.Required(),
        wtforms.validators.Length(min=1, max=128),
    ])


class ClaimUpdateForm(_CommonFieldsMixin, wtforms.Form):
    status = wtforms.TextField('Claim status', [
        wtforms.validators.AnyOf(['active', 'released', 'revoked']),
    ])
