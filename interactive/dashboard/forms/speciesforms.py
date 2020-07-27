from django import forms
from .formsetup import *

with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json') as f:
    data = json.loads(f.read())


class UploadFileForm(forms.Form):
    file = forms.FileField()


default = data["default"]
new = data["new"]

formulas = default["Formula"]
initialValues = default["Initial Value"]
units = default["Units"]


newFormulas = new["Formula"]
newInitials = new["Initial Value"]
newUnits = new["Units"]



class SpeciesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SpeciesForm, self).__init__(*args, **kwargs)
        for formula, newFormula in zip(formulas, newFormulas):
            self.fields[formula] = forms.CharField(initial=newFormula)


class InitForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(InitForm, self).__init__(*args, **kwargs)
        for initialValue, newInitial in zip(initialValues, newInitials):
            self.fields[initialValue] = forms.FloatField(initial=newInitial)


class UnitForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UnitForm, self).__init__(*args, **kwargs)
        for unit, newUnit in zip(units, newUnits):
            self.fields[unit] = forms.ChoiceField(choices=[('mol m-3', 'mol-m-3')])
