from django import forms
from .formsetup import ini_cond_setup

class UploadInitFileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'savebutton': 'initFileSave', 'class': 'form-control'}))


class InitialConditionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(InitialConditionsForm, self).__init__(*args, **kwargs)
        inits = ini_cond_setup()
        self.fields['temperature.label'] = forms.ChoiceField(choices=[('temperature', 'temperature')], widget=forms.Select(attrs={'savebutton': 'initialsSave', 'class': 'form-control'}))
        self.fields['temperature.init'] = forms.FloatField(initial=inits["values"]["temperature"], widget=forms.TextInput(attrs={'savebutton': 'initialsSave', 'class': 'form-control'}))
        self.fields['temperature.units'] = forms.ChoiceField(initial=inits["units"]["temperature"], choices=[('K', 'K'), ('C', 'C')], widget=forms.Select(attrs={'savebutton': 'initialsSave', 'class': 'form-control'}))
        self.fields['pressure.label'] = forms.ChoiceField(choices=[('pressure', 'pressure')], widget=forms.Select(attrs={'savebutton': 'initialsSave', 'class': 'form-control'}))
        self.fields['pressure.init'] = forms.FloatField(initial=inits["values"]["pressure"], widget=forms.TextInput(attrs={'savebutton': 'initialsSave', 'class': 'form-control'}))
        self.fields['pressure.units'] = forms.ChoiceField(initial=inits["units"]["pressure"], choices=[('atm', 'atm'), ('kPa', 'kPa'), ('bar', 'Bar')], widget=forms.Select(attrs={'savebutton': 'initialsSave', 'class': 'form-control'}))

