from django import forms
# from .formsetup import display_evolves

class UploadEvolvFileForm(forms.Form):
    file = forms.FileField(widget= forms.FileInput(attrs={'savebutton': 'evolvFileSave'}))

class UploadLossFileForm(forms.Form):
    file = forms.FileField(widget= forms.FileInput(attrs={'savebutton': 'lossFileSave'}))

# class LinearCombinationForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         super(LinearCombinationForm, self).__init__(*args, **kwargs)
#         options = display_evolves()[0]
#         for option in options:
#             if 'time' not in option:
#                 self.fields[option] = forms.BooleanField(required=False)
#         self.fields['Scale Factor'] = forms.FloatField(required=False)