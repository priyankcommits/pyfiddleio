from django.forms import ModelForm
from django import forms

from .models import Script


class ScriptForm(ModelForm):
    """ Form for creating new Campaign """

    def __init__(self, *args, **kwargs):
        super(ScriptForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(ScriptForm, self).clean()

    class Meta:
        model = Script
        exclude = ['id', 'user', 'active']
        widgets = {
            'text': forms.Textarea(
                attrs={}
            ),
            'commands': forms.TextInput(attrs={"form": "fiddle_form"}),
            'packages': forms.TextInput(attrs={"form": "fiddle_form"}),
            'inputs': forms.TextInput(attrs={"form": "fiddle_form"}),
        }
