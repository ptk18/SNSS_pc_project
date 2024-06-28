from django import forms

class FileUploadForm(forms.Form):
    templateSelect = forms.CharField(max_length=50)
    file = forms.FileField()