from django import forms
from .formsetup import formula_setup, value_setup, unit_setup, get_species_options


class UploadFileForm(forms.Form):
    file = forms.FileField()


class SpeciesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SpeciesForm, self).__init__(*args, **kwargs)

        formulas = formula_setup()
        species_options = get_species_options()
        units = unit_setup()
        values = value_setup()

        species_options.remove(('M', 'M'))

        for key in formulas:
            self.fields[key + '.Formula'] = forms.ChoiceField(choices=species_options, initial=formulas[key], widget=forms.Select(attrs={'id': key + '.Formula', 'savebutton': 'speciesSave', 'class': 'form-control species-dropdown', 'species': formulas[key]}))
            self.fields[key + '.Initial Value'] = forms.FloatField(initial=values[key], widget=forms.TextInput(attrs={'savebutton': 'speciesSave', 'class': 'form-control'}))
            self.fields[key + '.Units'] = forms.ChoiceField(initial=units[key], widget=forms.Select(attrs={'savebutton': 'speciesSave', 'class': 'form-control'}), choices=[('mol m-3', 'mol m-3',), ('molecule m-3', 'molecule m-3'), ('mol cm-3', 'mol cm-3'), ('molecule cm-3', 'molecule cm-3')])
