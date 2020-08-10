from django import forms
from .formsetup import ini_cond_setup

class UploadInitFileForm(forms.Form):
    file = forms.FileField()


class InitialConditionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(InitialConditionsForm, self).__init__(*args, **kwargs)
        inits = ini_cond_setup()
        self.fields['temperature.init'] = forms.FloatField(initial=inits["values"]["temperature"])
        self.fields['temperature.units'] = forms.ChoiceField(
            choices=[('K', 'K'), ('C', 'C')])
        self.fields['pressure.init'] = forms.FloatField(initial=inits["values"]["pressure"])
        self.fields['pressure.units'] = forms.ChoiceField(
            choices=[('atm', 'atm'), ('kPa', 'kPa'), ('bar', 'Bar')])
