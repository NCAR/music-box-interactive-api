from django import forms
from .formsetup import formula_setup, value_setup, unit_setup


class UploadFileForm(forms.Form):
    file = forms.FileField()


class SpeciesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SpeciesForm, self).__init__(*args, **kwargs)

        formulas = formula_setup()
        units = unit_setup()
        values = value_setup()

        for key in formulas:
            self.fields[key + '.Formula'] = forms.CharField(initial=formulas[key])
            self.fields[key + '.Initial Value'] = forms.FloatField(initial=values[key])
            self.fields[key + '.Units'] = forms.ChoiceField(choices=[('mol m-3', 'mol-m-3',), ('mol/L', 'mol/L')])
        

        # def formgroup(self):
        #     return [self[name] for name in filter(lambda x: x.endswith('Formula'), self.fields.values()]


        # def valuegroup(self):
        #     return [self[name] for name in filter(lambda x: x.endswith('Initial Value'), self.fields.values()]


        # def unitgroup(self):
        #     return [self[name] for name in filter(lambda x: x.endswith('units'), self.fields.values()]




