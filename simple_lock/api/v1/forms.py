import wtforms


class ClaimCreateForm(wtforms.Form):
    resource = wtforms.TextField('Resource name', [
        wtforms.validators.Required(),
        wtforms.validators.Length(min=1, max=128),
    ])

    timeout = wtforms.FloatField('Lock timeout (seconds)', [
        wtforms.validators.Required(),
        wtforms.validators.NumberRange(min=0),
    ])


class ClaimUpdateForm(wtforms.Form):
    pass
