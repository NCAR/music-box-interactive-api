from django import forms
from .formsetup import option_setup


class OptionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(OptionsForm, self).__init__(*args, **kwargs)
        inits = option_setup()
        self.fields['grid'] = forms.ChoiceField(choices=[('box', 'Box')])
        self.fields['chemistry_time_step'] = forms.FloatField(initial=inits["chemistry_time_step"])
        self.fields['output_time_step'] = forms.FloatField(initial=inits["output_time_step"])
        self.fields['simulation_length'] = forms.FloatField(initial=inits["simulation_length"])

