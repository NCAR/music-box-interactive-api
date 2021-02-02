from django import forms
from .formsetup import initial_reaction_rates_setup, get_musica_named_reaction_options

class UploadPhotoFileForm(forms.Form):
    file = forms.FileField()


class InitialReactionRatesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(InitialReactionRatesForm, self).__init__(*args, **kwargs)
        initial_rates = initial_reaction_rates_setup()
        reaction_options = get_musica_named_reaction_options()
        for key, value in initial_rates.items():
            self.fields['reaction-MUSICA-name.' + key] = forms.ChoiceField(choices=reaction_options, initial=key, widget=forms.Select(attrs={'savebutton': 'photoSave', 'class': 'form-control musica-named-reaction-dropdown', 'reaction': key}))
            self.fields['initial-value.' + key] = forms.FloatField(initial=value, widget=forms.TextInput(attrs={'savebutton': 'photoSave', 'class': 'form-control'}))
            self.fields['units.' + key] = forms.ChoiceField(choices=[("s-1", "s-1"), ("mol m-3 s-1", "mol m-3 s-1")], widget=forms.Select(attrs={'savebutton': 'photoSave', 'class': 'form-control musica-named-reaction-units-dropdown', 'units': ''}))


class PhotoDatetimeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PhotoDatetimeForm, self).__init__(*args, **kwargs)
        self.fields['time zone'] = forms.CharField()
        self.fields['year'] = forms.IntegerField()
        self.fields['month'] = forms.CharField()
        self.fields['day'] = forms.IntegerField()
        self.fields['hour'] = forms.IntegerField()
