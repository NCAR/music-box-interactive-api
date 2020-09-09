from django import forms
from .mech_load import *

class ReactionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ReactionForm, self).__init__(*args, **kwargs)
        inits = initialize_reactions()
        self.fields['rate'] = forms.CharField(initial=str(inits['rate']))
        i = 0
        for reactant in inits['reactants']:
            self.fields['reactant' + str(i)] = forms.CharField(initial=reactant)
            i = i+1

        self.fields['rate_call'] = forms.CharField(initial=inits['rate_call'])

        for key in inits['rate_constant']['parameters']:
            self.fields['rc.' + key] = forms.FloatField(initial=inits['rate_constant']['parameters'][key])
        
        self.fields['rc.reaction_class'] = forms.CharField(initial=inits['rate_constant']['reaction_class'])
        self.fields['troe'] = forms.CharField(initial=str(inits['troe']))
        i = 0
        for product in inits['products']:
            self.fields['p'+ str(i) + '.coefficient'] = forms.FloatField(initial=inits['products'][i]['coefficient'])
            self.fields['p'+ str(i) + '.molecule'] = forms.CharField(initial=inits['products'][i]['molecule'])
            i = i + 1
