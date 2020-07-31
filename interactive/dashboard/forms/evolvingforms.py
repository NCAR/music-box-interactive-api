from django import forms


class UploadEvolvFileForm(forms.Form):
    file = forms.FileField()
