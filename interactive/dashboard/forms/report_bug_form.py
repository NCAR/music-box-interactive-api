from django import forms

class BugForm(forms.Form):
    report = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

