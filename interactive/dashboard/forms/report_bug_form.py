from django import forms

class BugForm(forms.Form):
    your_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    report = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

