from __future__ import print_function, unicode_literals
from wtforms import TextField, PasswordField
from wtforms.widgets import PasswordInput

from flask.ext.admin.contrib.sqla.fields import QuerySelectField

import threading

local_data = threading.local()

class DisabledTextField(TextField):
    def __call__(self, *args, **kwargs):
        new_kwargs = kwargs.copy()
        new_kwargs['readonly'] = 'true'
        return super(DisabledTextField, self).__call__(*args, **new_kwargs)

class VisiblePasswordWidget(PasswordInput):
    def __call__(self, field, *args, **kwargs):

        visible = False

        for pos, registered_field in enumerate(local_data.fields):
            if field == registered_field and pos > 1:
                data = local_data.fields[pos - 1].data
                if data is not None:
                    visible = data.auth_type.name != 'DB'

        self.hide_value = not visible

        resulting_input = super(VisiblePasswordWidget, self).__call__(field, *args, **kwargs)
        if visible:
            resulting_input = resulting_input.replace('password', 'text')
        resulting_input += '<br/><label class="checkbox"><input type="checkbox" onclick="javascript:flipInputVisibility(this);" %s>Show</input></label>' % ('checked' if visible else '')
        return resulting_input

def register_self(self):
    if not hasattr(local_data, 'fields'):
        local_data.fields = [ self ]
    else:
        local_data.fields.append(self)

class VisiblePasswordField(PasswordField):

    widget = VisiblePasswordWidget()

    def __new__(self, *args, **kwargs):
        instance = super(VisiblePasswordField, self).__new__(self, *args, **kwargs)
        register_self(instance)
        return instance

class RecordingQuerySelectField(QuerySelectField):
    def __new__(self, *args, **kwargs):
        instance = super(RecordingQuerySelectField, self).__new__(self, *args, **kwargs)
        register_self(instance)
        return instance

