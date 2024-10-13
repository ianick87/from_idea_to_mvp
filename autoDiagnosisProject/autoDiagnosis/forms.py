from django import forms
from .models import Data


class DataForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = "__all__"


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Select a CSV file")
