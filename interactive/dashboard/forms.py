from django import forms
from .formsetup import *

class SpeciesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SpeciesForm, self).__init__(*args, **kwargs)
        for formula in formulas:
            self.fields[formula] = forms.CharField(initial=formula)


class InitForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(InitForm, self).__init__(*args, **kwargs)
        for init in initialValues:
            self.fields[init] = forms.CharField(initial=init)


class UnitForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UnitForm, self).__init__(*args, **kwargs)

        for unit in units:
            self.fields[unit] = forms.CharField(initial=unit)
