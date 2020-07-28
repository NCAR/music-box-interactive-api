from django import forms
from .formsetup import formula_setup, value_setup, unit_setup


class UploadFileForm(forms.Form):
    file = forms.FileField()




class FormulaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FormulaForm, self).__init__(*args, **kwargs)
        formulas = formula_setup()
        for key in formulas:
            self.fields[key] = forms.CharField(initial=formulas[key])


class InitForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(InitForm, self).__init__(*args, **kwargs)
        values = value_setup()
        for key in values:
            self.fields[key] = forms.FloatField(initial=values[key])


class UnitForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UnitForm, self).__init__(*args, **kwargs)
        units = unit_setup()
        for key in units:
            self.fields[key] = forms.ChoiceField(choices=[('mol m-3', 'mol-m-3',), ('mol/L', 'mol/L')])

