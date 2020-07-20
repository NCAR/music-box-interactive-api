from django import forms
from django.forms import Form, ModelForm

#import seperate dictionaries for each form

class optionsform(forms.Form):
    def __init__(self, *args, **kwargs):
        dynamic_fields = denest()
        super(CustomForm, self).__init__(*args, **kwargs)
        for key in dynamic_fields:
            self.fields[key] = forms.CharField(initial=dynamic_fields[key])


class speciesform(forms.Form):
    def __init__(self, *args, **kwargs):
        dynamic_fields = denest()
        super(CustomForm, self).__init__(*args, **kwargs)
        for key in dynamic_fields:
            self.fields[key] = forms.CharField(initial=dynamic_fields[key])


class initform(forms.Form):
    def __init__(self, *args, **kwargs):
        dynamic_fields = denest()
        super(CustomForm, self).__init__(*args, **kwargs)
        for key in dynamic_fields:
            self.fields[key] = forms.CharField(initial=dynamic_fields[key])


class evolvform(forms.Form):
    def __init__(self, *args, **kwargs):
        dynamic_fields = denest()
        super(CustomForm, self).__init__(*args, **kwargs)
        for key in dynamic_fields:
            self.fields[key] = forms.CharField(initial=dynamic_fields[key])


class photolysisform(forms.Form):
    def __init__(self, *args, **kwargs):
        dynamic_fields = denest()
        super(CustomForm, self).__init__(*args, **kwargs)
        for key in dynamic_fields:
            self.fields[key] = forms.CharField(initial=dynamic_fields[key])

