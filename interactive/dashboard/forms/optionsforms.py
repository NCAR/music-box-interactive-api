from django import forms
from .formsetup import option_setup


class UploadJsonConfigForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'savebutton': 'jsonConfigSave', 'class': 'form-control'}))


class OptionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(OptionsForm, self).__init__(*args, **kwargs)
        inits = option_setup()
        self.fields['grid'] = forms.ChoiceField(choices=[('box', 'Box')], widget=forms.Select(attrs={'savebutton': 'optionsSave', 'class': 'form-control'}))
        self.fields['chemistry_time_step'] = forms.FloatField(label="Chemistry time step [sec]", initial=inits["chemistry_time_step"], widget=forms.TextInput(attrs={'savebutton': 'optionsSave', 'class': 'form-control'}))
        self.fields['output_time_step'] = forms.FloatField(label="Output time step [sec]", initial=inits["output_time_step"], widget=forms.TextInput(attrs={'savebutton': 'optionsSave', 'class': 'form-control'}))
        self.fields['simulation_length'] = forms.FloatField(label="Simulation length [sec]", initial=inits["simulation_length"], widget=forms.TextInput(attrs={'savebutton': 'optionsSave', 'class': 'form-control'}))

