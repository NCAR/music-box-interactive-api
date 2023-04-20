from django import forms

class UploadEvolvFileForm(forms.Form):
    file = forms.FileField(widget= forms.FileInput(attrs={'savebutton': 'evolvFileSave', 'class': 'form-control'}))

class UploadLossFileForm(forms.Form):
    file = forms.FileField(widget= forms.FileInput(attrs={'savebutton': 'lossFileSave', 'class': 'form-control'}))

