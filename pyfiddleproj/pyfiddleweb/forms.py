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
            'packages': forms.TextInput(
                attrs={
                    "form": "fiddle_form",
                    "placeholder": "Eg: numpy,requests==2.18.3"
                    }
                ),
            'commands': forms.TextInput(
                attrs={
                    "form": "fiddle_form",
                    "placeholder": "Eg: 1,2,3"
                    }
                ),
            'inputs': forms.TextInput(
                attrs={
                    "form": "fiddle_form",
                    "placeholder": "Eg: hello,world"
                    }
                ),
            'envs': forms.TextInput(
                attrs={
                    "form": "fiddle_form",
                    "placeholder": "Eg: env1,value1,env2,value2"
                    }
                ),
            'private': forms.CheckboxInput(attrs={"form": "fiddle_form"}),
            'version': forms.CheckboxInput(attrs={"form": "fiddle_form"}),
            'fiddle_name': forms.TextInput(
                attrs={"form": "fiddle_form", "placeholder": "myfiddle"})
        }
