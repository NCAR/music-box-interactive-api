from django import forms
from .formsetup import ini_cond_setup

class UploadInitFileForm(forms.Form):
    file = forms.FileField()


class InitialConditionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(InitialConditionsForm, self).__init__(*args, **kwargs)
        inits = ini_cond_setup()
        self.fields['temperature'] = forms.FloatField(initial=inits["values"]["temperature"])
        self.fields['pressure'] = forms.FloatField(initial=inits["values"]["pressure"])


class ConditionsUnitsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ConditionsUnitsForm, self).__init__(*args, **kwargs)
        self.fields['temperature'] = forms.ChoiceField(
            choices=[('K', 'K'), ('C', 'C')])
        self.fields['pressure'] = forms.ChoiceField(
            choices=[('atm', 'atm'), ('kPa', 'kPa'), ('bar', 'Bar')])
