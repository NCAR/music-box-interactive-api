from django import forms
from .formsetup import photo_setup

class UploadPhotoFileForm(forms.Form):
    file = forms.FileField()


class PhotoForm(forms.Form):    
    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        inits = photo_setup()
        for key in inits['reactions']:
            self.fields[key + '.r_form'] = forms.CharField(initial=inits['reactions'][key], widget=forms.TextInput(attrs={'savebutton': 'photoSave'}))
            self.fields[key + '.init'] = forms.FloatField(initial=inits['initial value'][key], widget=forms.TextInput(attrs={'savebutton': 'photoSave'}))
        

class PhotoDatetimeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PhotoDatetimeForm, self).__init__(*args, **kwargs)
        self.fields['time zone'] = forms.CharField()
        self.fields['year'] = forms.IntegerField()
        self.fields['month'] = forms.CharField()
        self.fields['day'] = forms.IntegerField()
        self.fields['hour'] = forms.IntegerField()
