from flask.ext.wtf import TextField, PasswordField

from flask.ext.wtf import HTMLString, PasswordInput

class DisabledTextField(TextField):
    def __call__(self, *args, **kwargs):
        new_kwargs = kwargs.copy()
        new_kwargs['readonly'] = 'true'
        return super(DisabledTextField, self).__call__(*args, **new_kwargs)

class VisiblePasswordWidget(PasswordInput):
    def __call__(self, field, *args, **kwargs):
        print field.__dict__.values()

        resulting_input = super(VisiblePasswordWidget, self).__call__(field, *args, **kwargs)
        resulting_input += '<br/><label class="checkbox"><input type="checkbox" onclick="javascript:flipInputVisibility(this);">Show</input></label>'
        print resulting_input
        return resulting_input

class VisiblePasswordField(PasswordField):
    widget = VisiblePasswordWidget()

