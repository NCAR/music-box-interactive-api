from django import forms
from .formsetup import photo_setup

class UploadPhotoFileForm(forms.Form):
    file = forms.FileField()


class PhotoForm(forms.Form):    
    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        inits = photo_setup()
        for key in inits['reactions']:
            self.fields[key + '.reaction'] = forms.CharField(initial=inits['reactions'][key])
            self.fields[key + '.inital_value'] = forms.FloatField(initial=inits['initial value'][key])
        

