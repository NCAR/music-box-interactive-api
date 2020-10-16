from django import forms
from .mech_read_write import initialize_form

class MoleculeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MoleculeForm, self).__init__(*args, **kwargs)
        inits = initialize_form()
        self.fields['formula'] = forms.CharField(initial=inits['formula'],required=False)
        self.fields['mw.value'] = forms.FloatField(initial=inits['molecular weight']['value'])
        self.fields['hl.at 298K.value'] = forms.FloatField(initial=inits['henrys law constant']['at 298K']['value'])
        self.fields['hl.exponential factor.value'] = forms.FloatField(initial=inits['henrys law constant']['exponential factor']['value'])



class NewMoleculeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(NewMoleculeForm, self).__init__(*args, **kwargs)
        
        self.fields['moleculename'] = forms.CharField()
        self.fields['formula'] = forms.CharField()
        self.fields['mw.value'] = forms.FloatField()
        self.fields['hl.at 298K.value'] = forms.FloatField()
        self.fields['hl.exponential factor.value'] = forms.FloatField()



class MoleculeSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MoleculeSearchForm, self).__init__(*args, **kwargs)
        self.fields['query'] = forms.CharField(widget= forms.TextInput(attrs={'placeholder':'name'}))
