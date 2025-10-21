from django import forms

class UploadZipForm(forms.Form):
    zip_file = forms.FileField(
        label='Select a .zip file',
        help_text='Upload a zip file containing data.json and images'
    )