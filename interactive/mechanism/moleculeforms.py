from django import forms
from .mech_load import molecule_info

class MoleculeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SpeciesForm, self).__init__(*args, **kwargs)
        molec = molecule_info()

        self.fields['formula'] = forms.CharField(initial=)
        self.fields['solve'] = forms.CharField()
        self.fields['hl.henrys_law_type'] = forms.IntegerField()
        self.fields['hl.kh_298'] = forms.FloatField()
        self.fields['hl.dh_r'] = forms.FloatField()
        self.fields['hl.k1_298'] = forms.FloatField()
        self.fields['hl.dh1_r'] = forms.FloatField()
        self.fields['hl.k2_298'] = forms.FloatField()
        self.fields['hl.dh2_r'] = forms.FloatField()

