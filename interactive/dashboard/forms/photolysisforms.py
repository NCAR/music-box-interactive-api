from django import forms


class UploadPhotoFileForm(forms.Form):
    file = forms.FileField()
