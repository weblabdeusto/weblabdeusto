from flask.ext.wtf import TextField

class DisabledTextField(TextField):
    def __call__(self, *args, **kwargs):
        new_kwargs = kwargs.copy()
        new_kwargs['readonly'] = 'true'
        return super(DisabledTextField, self).__call__(*args, **new_kwargs)


